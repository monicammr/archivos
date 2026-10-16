#!/usr/bin/env python3
"""
Hypotheses of the Lean identifiability theorems evaluated over the admissible set (second audit,
point N2).

practically_identifiable_grad requires ||r(delta) - r0 - A delta|| <= eps for EVERY delta in the
admissible set F (the box of the free parameters, selected and calibration, within
[|theta0|/10, 10|theta0|] in log|theta|), but identifiability_conditions.py estimated eps only at the
computed profile points. The proof only uses the bound in the TAIL of the profile,
{delta in F : delta_j <= -t_lo or delta_j >= t_hi}, which gives two theorems (lean_proofs/
ProfileIdentifiability.lean):
  practically_identifiable_grad_tail: ||rho|| <= eps on the tail and tstarGrad(eps) <= t;
  practically_identifiable_rel_tail:  ||rho|| <= eta ||A delta|| (eta < 1) on the tail and
                                      tstarRel(eta) <= t.
For each selected parameter and side, this script looks for the smallest t (< distance to the
bound) at which one of these conditions holds, with eps(t) and eta(t) estimated over the tail of F:
  1. space-filling sample of F (scrambled Sobol sequence, ID_BOX_N points, default 1024) and the
     computed profile points;
  2. for every (parameter, side, condition) that passes on the sample, an adversarial search
     maximises the remainder (or the ratio) on the tail with L-BFGS-B from the ID_BOX_STARTS
     (default 3) worst tail points, and the condition is checked again.
eps and eta are estimates from below of suprema (no interval arithmetic): the result checks the
hypotheses of the theorems over the right set, densely and adversarially, but is not a proof.

Usage:  NPROC=40 python identifiability_box.py [Problem ...]
Output: results/identifiability/box/<problem>.json and results/identifiability/audit2/certificado_box*.csv (outside the folder read by the paper tables)
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import qmc

import identifiability_profiles as P
from identifiability_conditions import tstar_grad, tstar_rel

D = 0.01
C = P.UMBRAL
N_BOX = int(os.environ.get("ID_BOX_N", 1024))
N_STARTS = int(os.environ.get("ID_BOX_STARTS", 3))
MIN_TAIL = 20          # minimum number of sampled points in a tail to accept a condition
# ID_BOX_RADIUS=r restricts F to the parameters within a factor r of theta_hat (and within the
# bounds of the study): the conclusion is then practical identifiability within that region.
RADIUS = float(os.environ.get("ID_BOX_RADIUS", 10))
OUT = P.OUTD.parent / "box"
TAG = "" if RADIUS == 10 else f"_r{RADIUS:g}"


def r_of(name, th):
    d = P.prep(name)
    z = d["S"].z(th)
    if z is None:
        return None
    fil = d["filas"]
    v = z[fil] - d["zd"][fil]
    return np.where(np.isfinite(v), v, 1e3)


def base(name):
    """theta_hat, r0, A (free parameters with a nonzero column), bounds of delta."""
    f = OUT / name / "base.npz"
    if f.exists():
        b = np.load(f, allow_pickle=True)
        return {k: b[k] for k in b.files}
    d = P.prep(name)
    S = d["S"]
    th = np.load(P.f_min(name))["theta"]
    lib = d["libres"]
    r0 = r_of(name, th)
    A = np.zeros((r0.size, len(lib)))
    for k, j in enumerate(lib):
        tp, tm = th.copy(), th.copy()
        tp[j] *= math.exp(D); tm[j] *= math.exp(-D)
        rp, rm = r_of(name, tp), r_of(name, tm)
        if rp is not None and rm is not None:
            A[:, k] = (rp - rm) / (2 * D)
    nz = np.linalg.norm(A, axis=0) > 1e-10 * max(np.linalg.norm(A, axis=0).max(), 1e-300)
    lib_nz = np.array([j for j, z in zip(lib, nz) if z], dtype=int)
    A = A[:, nz]
    u_hat = np.log(np.abs(th[lib_nz]))
    t0 = np.log(np.maximum(np.abs(S.theta0[lib_nz]), 1e-300))
    lo, hi = t0 - math.log(10) - u_hat, t0 + math.log(10) - u_hat
    b = dict(theta=th, r0=r0, A=A, lib=lib_nz, u_hat=u_hat, lo=lo, hi=hi)
    (OUT / name).mkdir(parents=True, exist_ok=True)
    np.savez(f, **b)
    return b


_B = {}


def _b(name):
    if name not in _B:
        b = dict(base(name))
        b["lo"] = np.maximum(b["lo"], -math.log(RADIUS))
        b["hi"] = np.minimum(b["hi"], math.log(RADIUS))
        _B[name] = b
    return _B[name]


def remainder(name, delta):
    """(||r(delta) - r0 - A delta||, ||A delta||)."""
    b = _b(name)
    delta = np.asarray(delta, dtype=float)
    th = b["theta"].copy()
    sg = np.sign(th[b["lib"]]); sg[sg == 0] = 1
    th[b["lib"]] = sg * np.exp(b["u_hat"] + delta)
    r = r_of(name, th)
    nAd = float(np.linalg.norm(b["A"] @ delta))
    if r is None:
        return float("nan"), nAd
    return float(np.linalg.norm(r - b["r0"] - b["A"] @ delta)), nAd


def sobol(name):
    b = _b(name)
    pts = qmc.Sobol(d=len(b["lib"]), scramble=True, seed=0).random(N_BOX)
    return b["lo"] + pts * (b["hi"] - b["lo"])


def t_base(name):
    t0 = time.time()
    base(name)
    return name, round(time.time() - t0, 1)


def t_sample(arg):
    name, delta = arg
    rem, nAd = remainder(name, delta)
    return name, delta, rem, nAd


def t_adversarial(arg):
    """Maximise the remainder (mode 'abs') or remainder/||A delta|| (mode 'rel') on one tail."""
    name, k, side, t, mode, start = arg
    b = _b(name)
    lo, hi = b["lo"].copy(), b["hi"].copy()
    if side > 0:
        lo[k] = t
    else:
        hi[k] = -t
    best = {"v": -1.0, "x": None, "rem": None, "nAd": None}

    def f(x):
        rem, nAd = remainder(name, x)
        if not np.isfinite(rem):
            return 0.0
        v = rem if mode == "abs" else (rem / nAd if nAd > 0 else math.inf)
        if v > best["v"]:
            best.update(v=v, x=np.array(x).tolist(), rem=rem, nAd=nAd)
        return -v if np.isfinite(v) else -1e30
    x0 = np.clip(np.asarray(start, dtype=float), lo, hi)
    try:
        minimize(f, x0, method="L-BFGS-B", bounds=list(zip(lo, hi)),
                 options={"maxiter": 20, "eps": 1e-3})
    except Exception:
        pass
    return arg[:5], best


def scan(I, gam, nr0, k, side, dside, pts, mode):
    """Smallest t on a grid at which the condition holds on the sampled tail, or None."""
    x = np.array([s * p[0][k] for p in pts for s in (side,)])
    rem = np.array([p[1] for p in pts]); nAd = np.array([p[2] for p in pts])
    for t in np.linspace(0.01, dside, 200)[:-1]:
        tail = x >= t
        if tail.sum() < MIN_TAIL:
            return None
        if mode == "abs":
            eps = float(rem[tail].max())
            if tstar_grad(I, eps, gam, C, nr0) <= t:
                return float(t), eps
        else:
            eta = float(np.max(rem[tail] / np.maximum(nAd[tail], 1e-300)))
            if eta < 1 and tstar_rel(I, eta, gam, C, nr0) <= t:
                return float(t), eta
    return None


def param_info(b, k):
    A, r0 = b["A"], b["r0"]
    coef, *_ = np.linalg.lstsq(A, r0, rcond=None)
    gam = float(np.linalg.norm(A @ coef))
    otras = np.delete(A, k, axis=1)
    if otras.shape[1]:
        cf, *_ = np.linalg.lstsq(otras, A[:, k], rcond=None)
        I = float(np.sum((A[:, k] - otras @ cf) ** 2))
    else:
        I = float(A[:, k] @ A[:, k])
    return I, gam, float(np.linalg.norm(r0))


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = which or sorted(p.stem for p in P.OUTD.glob("*.json"))
    names = [n for n in names if P.f_min(n).exists()]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(int(os.environ.get("NPROC", 8))) as pool:
        for n, s in pool.imap_unordered(t_base, names):
            print(json.dumps({"base": n, "seg": s}), flush=True)
        # 1. sample of F and profile points
        tasks = [(n, x.tolist()) for n in names for x in sobol(n)]
        for n in names:
            d, b = P.prep(n), _b(n)
            for f in (P.OUTD / n).glob("p_*.json"):
                p = json.loads(f.read_text(encoding="utf-8"))
                if P.dentro(d, p) and p["dchi2"] <= P.FALLO:
                    tp = np.array(p["theta"])
                    dl = np.log(np.abs(tp[b["lib"]])) - b["u_hat"]
                    if np.all(dl >= b["lo"] - 1e-9) and np.all(dl <= b["hi"] + 1e-9):   # only points of F
                        tasks.append((n, dl.tolist()))
        pts = {n: [] for n in names}
        for k_, (n, x, rem, nAd) in enumerate(pool.imap_unordered(t_sample, tasks, chunksize=4)):
            if np.isfinite(rem):
                pts[n].append((np.array(x), rem, nAd))
            if (k_ + 1) % 2000 == 0:
                print(f"  {k_ + 1}/{len(tasks)} points ({time.time() - t0:.0f} s)", flush=True)
        # 2. scan on the sample; adversarial search at the t found; the worst points found are added
        #    to the sample of the problem (they are points of F) and the scan is repeated, until the
        #    t of the scan is the t at which the adversarial search was run (pass) or no t is left
        info, state = {}, {}
        for n in names:
            d, b = P.prep(n), _b(n)
            lib = list(b["lib"])
            for j in d["sel"]:
                if j not in lib:
                    continue
                k = lib.index(j)
                I, gam, nr0 = param_info(b, k)
                for side, dside in ((-1, -float(b["lo"][k])), (1, float(b["hi"][k]))):
                    for mode in ("abs", "rel"):
                        key = (n, d["S"].names[j], side, mode)
                        info[key] = dict(k=k, I=I, gam=gam, nr0=nr0, dside=dside, t_adv=None,
                                         muestra=None, rondas=0)
                        state[key] = "open" if I > 0 else "fail"
        for ronda in range(5):
            adv_tasks = []
            for key, st in state.items():
                if st != "open":
                    continue
                n, _, side, mode = key
                r = info[key]
                s = scan(r["I"], r["gam"], r["nr0"], r["k"], side, r["dside"], pts[n], mode)
                if ronda == 0:
                    r["muestra"] = s
                if s is None:
                    state[key] = "fail"; continue
                if r["t_adv"] is not None and s[0] <= r["t_adv"] + 1e-12:
                    state[key] = "pass"; r["t"], r["valor"] = s; continue
                r["t_adv"], r["rondas"] = s[0], ronda + 1
                tail = [p for p in pts[n] if side * p[0][r["k"]] >= s[0]]
                kf = (lambda p: p[1]) if mode == "abs" else (lambda p: p[1] / max(p[2], 1e-300))
                for p in sorted(tail, key=kf, reverse=True)[:N_STARTS]:
                    adv_tasks.append((n, r["k"], side, s[0], mode, p[0].tolist()))
            if not adv_tasks:
                break
            print(f"round {ronda}: {len(adv_tasks)} adversarial searches", flush=True)
            for a, best in pool.imap_unordered(t_adversarial, adv_tasks):
                if best["x"] is not None and np.isfinite(best["rem"]):
                    pts[a[0]].append((np.array(best["x"]), best["rem"], best["nAd"]))
        for key, st in state.items():
            if st == "open":
                state[key] = "fail"
    rows = []
    for key, r in info.items():
        n, nom, side, mode = key
        rows.append({"sistema": n, "parametro": nom, "lado": side, "condicion": mode, "I_j": r["I"],
                     "gamma": r["gam"], "norma_r0": r["nr0"], "d_lado": r["dside"],
                     "pasa_muestra": r["muestra"] is not None,
                     "t_muestra": r["muestra"][0] if r["muestra"] else None,
                     "t": r.get("t"), "valor_final": r.get("valor"), "rondas_adversario": r["rondas"],
                     "pasa_final": state[key] == "pass"})
    df = pd.DataFrame(rows)
    (P.OUTD.parent / "audit2").mkdir(exist_ok=True)
    df.to_csv(P.OUTD.parent / "audit2" / f"certificado_box{TAG}.csv", index=False)
    # one line per parameter: certified if, on BOTH sides, one of the two conditions passes
    if len(df):
        df["pf"] = df.get("pasa_final", False).fillna(False).astype(bool)
        lado = df.groupby(["sistema", "parametro", "lado"])["pf"].any().reset_index()
        par = lado.groupby(["sistema", "parametro"])["pf"].all().reset_index()
        par.to_csv(P.OUTD.parent / "audit2" / f"certificado_box{TAG}_parametros.csv", index=False)
        print(par.to_string())
        print("certified parameters:", int(par["pf"].sum()), "of", len(par))
    print(f"Done ({time.time() - t0:.0f} s)", flush=True)
