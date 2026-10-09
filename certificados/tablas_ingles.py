#!/usr/bin/env python3
"""English tables for the manuscript / response letter → ../respuesta_revisores/tables_en.md

Table A: per-system results of the final method (measured outputs, biological parameters,
         calibration parameters always re-estimated, backward elimination), plus external
         validation.
Table B: computational cost (reviewer 2, comment 5).
Table C: sensitivity to the method thresholds (reviewer 2, comment 4).
"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
R = HERE / "resultados"
OUT = HERE.parent / "respuesta_revisores" / "tables_en.md"


def carga(d):
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))} if d.exists() else {}


def pct(x):
    return "—" if x is None or not np.isfinite(x) else f"{100 * x:.1f}%"


def num(x, d=2):
    return "—" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


def tabla_sistemas():
    sel = carga(R / "reclasificacion_salidas_bio_poda")
    val = carga(R / "validacion_externa_bio")
    chk = {}
    f = R / "salidas_check_log.txt"
    if f.exists():
        for l in f.read_text().splitlines():
            if l.startswith("{"):
                d = json.loads(l); chk[d["sistema"]] = d
    L = ["## Table A. Per-system results (final method)", "",
         "Measured outputs (PEtab observables, conditions, noise); selection among biological "
         "parameters only, calibration parameters (scalings/offsets) always re-estimated; "
         "backward elimination. e_fit: median relative error after re-estimation over 15 "
         "scenarios at ±5% (threshold 0.436 ⇔ cos Δ ≥ 0.9). External validation: χ²/n on "
         "held-out conditions (real data; reduced vs full model re-fitted on the training "
         "conditions; full model only for p ≤ 60) and relative prediction error e_pred on "
         "synthetic noisy data. * e_fit computed to first order (linearized) for computational "
         "cost.", "",
         "| System | p | Meas. | Cond. | Stage | k (biological) | Selected biological parameters | "
         "Calibration re-estimated | e_fit | Admissible | χ²/n test (reduced / full) | "
         "e_pred (synthetic) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    n_adm = 0
    for n, d in sel.items():
        c = chk.get(n, {})
        v = val.get(n, {})
        if d.get("admisible"):
            n_adm += 1
        ef = d.get("eajuste_med")
        star = "*" if d.get("eajuste_metodo") else ""
        if "no_evaluable" in v:
            ext, ep = "not evaluable", "—"
        elif v:
            ext = f"{num(v.get('A_chi2_test_red'))} / {num(v.get('A_chi2_test_full'))}"
            ep = num(v.get("B_epred_red"))
        else:
            ext, ep = "not run", "—"
        etapa = {"Stage 1": "1", "Stage 2": "2"}.get(d.get("etapa"), d.get("etapa", "—"))
        L.append(f"| {n.split('_')[0]} | {d.get('p', '—')} | {c.get('mediciones', '—')} | "
                 f"{c.get('condiciones', '—')} | {etapa} | {len(d.get('S', []))} | "
                 f"{', '.join(d.get('S', []))} | {len(d.get('calibracion', []))} | "
                 f"{pct(ef)}{star} | {'yes' if d.get('admisible') else 'no'} | {ext} | {ep} |")
    L += ["", f"Admissible: {n_adm} of {len(sel)} PEtab systems. Not included: "
          "Froehlich_CellSystems2018 (9,169 experimental conditions; see Table B) and the SCT "
          "Bandura model (not a PEtab problem; analysed on states only)."]
    return L


def tabla_costo():
    d = json.loads((R / "costo" / "tiempos_simulacion.json").read_text())

    def hms(s):
        return f"{s:.0f} s" if s < 120 else (f"{s/60:.0f} min" if s < 7200 else f"{s/3600:.1f} h")
    L = ["## Table B. Computational cost", "",
         "The dominant step is the sensitivity matrix J by central differences (2p simulations) "
         "plus the stage-2 scan (p simulations); all simulations are independent "
         "(embarrassingly parallel). Greedy selection, κ/VIF, backward elimination and the "
         "linearized e_fit use only J (linear algebra). Times measured on a 4-core server.", "",
         "| System | p | Data | Time per simulation | Simulations (3p) | Serial time | "
         "4 cores |", "|---|---|---|---|---|---|---|"]
    for n, v in sorted(d.items(), key=lambda kv: kv[1]["p"]):
        t = 3 * v["p"] * v["t_sim"]
        modo = "measured outputs" if v["modo"] == "salidas" else "states"
        L.append(f"| {n.split('_')[0]} | {v['p']} | {modo} | {v['t_sim']:.3g} s | {3 * v['p']} | "
                 f"{hms(t)} | {hms(t / 4)} |")
    L += ["", "Cost grows linearly in p. Froehlich (4,231 parameters, 1,228 species) was "
          "processed completely on states; on its measured outputs (9,169 conditions) each "
          "evaluation requires ~9,000 simulations and it was excluded. For such models, "
          "forward or adjoint sensitivity equations (e.g. AMICI) compute J at the cost of a few "
          "simulations."]
    return L


def tabla_umbrales():
    base = carga(R / "reclasificacion_salidas_bio_poda")
    vars_ = [("rvar080", "τ_R = 0.80"), ("rvar085", "τ_R = 0.85"), (None, "baseline"),
             ("rvar095", "τ_R = 0.95"), ("kv5", "τ_κ = τ_VIF = 5"), ("kv30", "τ_κ = τ_VIF = 30"),
             ("emax010", "τ_e = 0.10"), ("emax020", "τ_e = 0.20"), ("emax030", "τ_e = 0.30"),
             ("emax050", "τ_e = 0.50")]
    peq = None
    L = ["## Table C. Sensitivity to the method thresholds", "",
         "Final method re-run on the small and medium systems changing one threshold at a time "
         "(baseline: τ_R = 0.89, τ_κ = τ_VIF = 10, τ_e = 0.436). Same S: identical selected "
         "subset as the baseline.", "",
         "| Setting | Systems | Admissible | Mean k (admissible) | Stage 1 | Same S | Same stage |",
         "|---|---|---|---|---|---|---|"]
    for tag, desc in vars_:
        if tag is None:
            V = base
        else:
            V = carga(R / f"reclasificacion_salidas_bio_poda_{tag}")
            if peq is None and len(V) >= 20:
                peq = set(V)
        if tag is None and peq:
            V = {k: v for k, v in base.items() if k in peq}
        V = {k: v for k, v in V.items() if k in base}
        if not V:
            continue
        adm = [v for v in V.values() if v.get("admisible")]
        same = sum(set(V[k].get("S", [])) == set(base[k].get("S", [])) for k in V)
        st = sum(V[k].get("etapa") == base[k].get("etapa") for k in V)
        e1 = sum(v.get("etapa") == "Stage 1" for v in V.values())
        mk = np.mean([len(v["S"]) for v in adm]) if adm else float("nan")
        L.append(f"| {desc} | {len(V)} | {len(adm)} | {mk:.2f} | {e1} | {same}/{len(V)} | "
                 f"{st}/{len(V)} |")
    L += ["", "Robustness to δ (0.1%, 1%, 5%), integrator tolerances, perturbation size (±1%, "
          "±5%, ±10%) and time grid (N_t = 30, 60, 120; horizon 2T) is reported separately "
          "(sensitivity analysis, reviewer 4 comment 6)."]
    return L


def main():
    L = ["# Tables (English version)", ""] + tabla_sistemas() + [""] + tabla_costo() + [""] + \
        tabla_umbrales()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
