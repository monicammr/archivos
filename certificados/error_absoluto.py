#!/usr/bin/env python3
"""
Error de reproducción en unidades del ruido (auditoría, punto C1).

e_fit es un error RELATIVO al cambio de la respuesta del modelo, ‖Δy_full‖. Para juzgar si ese
error es pequeño frente a la precisión de las mediciones, se expresa también en unidades de σ:
las salidas de petab_outputs.py ya están divididas por σ_i, de modo que para cada escenario k
    error absoluto RMS = e_fit,k · ‖Δy_full,k‖ / √n          (σ por medición)
    cambio RMS        =          ‖Δy_full,k‖ / √n
con n el número de mediciones. Los e_fit,k por escenario se leen de resultados/patrones/<P>.json
(nivel ±5 %, semilla 42: los mismos escenarios de la selección) y ‖Δy_full,k‖ se recalcula con las
mismas direcciones u(k).

Uso: python error_absoluto.py [Problema ...]   → resultados/error_absoluto/<P>.json, RESUMEN.md
"""
import sys, os, json
from pathlib import Path
from multiprocessing import Pool
import numpy as np

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import petab_outputs as PO

HERE = Path(__file__).resolve().parent
SEL = HERE / "resultados" / "reclasificacion_salidas_bio_poda"
PAT = HERE / "resultados" / "patrones"
REPRO = HERE.parent / "reproducibility" / "results" / "robustness"
OUTD = HERE / "resultados" / "error_absoluto"
NIVEL, CLAVE = 0.05, "5"


def uno(name):
    # resultados por escenario de la Fig. 5 (paquete de reproducibilidad); si el subconjunto ha
    # cambiado desde entonces, los de resultados/patrones (rehechos con el subconjunto actual)
    S_act = json.loads((SEL / f"{name}.json").read_text())["S"]
    pat = None
    for d in (REPRO, PAT):
        if (d / f"{name}.json").exists():
            c = json.loads((d / f"{name}.json").read_text())
            if c.get("S") == S_act and "eaj" in c["niveles"][CLAVE]:
                pat = c; break
    if pat is None:
        raise RuntimeError("sin resultados de robustez por escenario para el subconjunto actual")
    niv = pat["niveles"][CLAVE]
    Sy = PO.PSys(name)
    th0 = Sy.theta0
    # direcciones u(k): guardadas en los resultados recientes; en los anteriores se regeneran con la
    # misma semilla (patrones.py comprueba que coinciden con las de la selección)
    U = np.array(pat["u"]) if "u" in pat else \
        np.random.default_rng(pat.get("semilla", 42)).uniform(-1, 1, size=(15, len(th0)))
    y0 = Sy.sim(th0).ravel()
    n = y0.size
    umbral = max(1e-10 * np.linalg.norm(y0), 1e-6)
    idx = [Sy.names.index(q) for q in pat["S"] + json.loads((SEL / f"{name}.json").read_text()).get(
        "calibracion", []) if q in Sy.names]
    # escenarios válidos con la misma regla que patrones.py (los resultados antiguos no los guardan)
    validos, normas = [], {}
    for k in range(len(U)):
        th = th0 * (1 + NIVEL * U[k])
        yf = Sy.sim(th)
        if yf is None:
            continue
        nf = float(np.linalg.norm(yf.ravel() - y0))
        if nf < umbral:
            continue
        ts = th0.copy(); ts[idx] = th[idx]
        if "escenarios" not in niv and Sy.sim(ts) is None:
            continue
        validos.append(k); normas[k] = nf
    ks = niv.get("escenarios", validos)
    if len(ks) != len(niv["eaj"]):
        raise RuntimeError(f"{len(ks)} escenarios válidos frente a {len(niv['eaj'])} e_fit guardados")
    filas = []
    for k, ef in zip(ks, niv["eaj"]):
        if k not in normas:
            continue
        cambio = normas[k] / np.sqrt(n)
        filas.append({"k": int(k), "e_fit": float(ef), "cambio_rms_sigma": cambio,
                      "error_rms_sigma": float(ef) * cambio})
    med = lambda c: float(np.median([f[c] for f in filas])) if filas else float("nan")
    mx = lambda c: float(np.max([f[c] for f in filas])) if filas else float("nan")
    return {"sistema": name, "S": pat["S"], "n": n, "n_escenarios": len(filas),
            "e_fit_med": med("e_fit"), "cambio_rms_sigma_med": med("cambio_rms_sigma"),
            "error_rms_sigma_med": med("error_rms_sigma"), "error_rms_sigma_max": mx("error_rms_sigma"),
            "escenarios": filas}


def _seguro(name):
    try:
        r = uno(name)
    except Exception as e:
        r = {"sistema": name, "error": repr(e)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"{name}.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r.get(k) for k in ("sistema", "e_fit_med", "cambio_rms_sigma_med",
                                            "error_rms_sigma_med", "error")}), flush=True)


def resumen():
    rs = [json.loads(p.read_text()) for p in sorted(OUTD.glob("*.json"))]
    L = ["# Error de reproducción en unidades del ruido (±5 %, 15 escenarios)", "",
         "| Sistema | n | mediana e_fit | mediana cambio RMS (σ) | mediana error RMS (σ) | máx. error RMS (σ) |",
         "|---|---|---|---|---|---|"]
    for r in rs:
        if "error" in r:
            L.append(f"| {r['sistema']} | error: {r['error'][:60]} |"); continue
        L.append(f"| {r['sistema']} | {r['n']} | {r['e_fit_med']:.3f} | {r['cambio_rms_sigma_med']:.3g} | "
                 f"{r['error_rms_sigma_med']:.3g} | {r['error_rms_sigma_max']:.3g} |")
    (OUTD / "RESUMEN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def tabla_latex():
    """paper/scirep/tables/tableS_abs.tex (sólo los problemas cuyo subconjunto es el actual)."""
    filas = []
    for p in sorted(OUTD.glob("*.json")):
        r = json.loads(p.read_text())
        sel = SEL / f"{r['sistema']}.json"
        if "error" in r or not sel.exists() or json.loads(sel.read_text()).get("S") != r["S"] \
                or r["sistema"] in os.environ.get("ABS_EXCLUIR", "").split(","):
            continue
        def f(x):
            if x == 0:
                return "0"
            if 0.01 <= abs(x) < 100:
                return f"{x:.2f}"
            m, e = f"{x:.1e}".split("e")
            return f"${m}\\times10^{{{int(e)}}}$"
        nombre = r["sistema"].split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")
        filas.append(f"{nombre} & {r['n']} & {r['n_escenarios']} & {100 * r['e_fit_med']:.1f} & "
                     f"{f(r['cambio_rms_sigma_med'])} & {f(r['error_rms_sigma_med'])} & {f(r['error_rms_sigma_max'])} \\\\")
    cab = "Problem & $n$ & Valid & Median $e_{\\mathrm{fit}}$ (\\%) & Change (RMS, $\\sigma$) & Error (RMS, $\\sigma$) & Max error \\\\"
    t = ["\\begin{longtable}{@{}lrrrrrr@{}}",
         "\\caption{Reproduction error of the selected subsets in units of the recorded noise, over the scenarios at $\\pm5\\%$. "
         "$n$: number of measurements; Valid: valid scenarios. Change: root mean square of $\\Delta y_{\\mathrm{full}}$ per measurement, "
         "in units of $\\sigma$ (median over the scenarios); Error: root mean square of the remaining error after re-estimation, "
         "$e_{\\mathrm{fit}}\\|\\Delta y_{\\mathrm{full}}\\|/\\sqrt n$ (median and maximum over the scenarios). A value below one means that "
         "the reduced model reproduces the perturbed full model to within the noise of the measurements.}\\label{tab:abs}\\\\",
         "\\toprule", cab, "\\midrule", "\\endfirsthead", "\\toprule", cab, "\\midrule", "\\endhead"] + filas + \
        ["\\bottomrule", "\\end{longtable}"]
    out = HERE.parent / "paper" / "scirep" / "tables" / "tableS_abs.tex"
    out.write_text("\n".join(t) + "\n", encoding="utf-8")
    print("escrita", out, len(filas), "filas")


if __name__ == "__main__":
    if "--resumen" in sys.argv:
        resumen(); sys.exit()
    if "--tabla" in sys.argv:
        tabla_latex(); sys.exit()
    nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not nombres:
        nombres = [f.stem for f in sorted(SEL.glob("*.json"))
                   if json.loads(f.read_text()).get("admisible")]
    with Pool(int(os.environ.get("NPROC", 4))) as pool:
        list(pool.imap_unordered(_seguro, nombres))
    resumen()
