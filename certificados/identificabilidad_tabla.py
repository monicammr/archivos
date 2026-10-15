#!/usr/bin/env python3
"""
Tabla y resumen de la nota suplementaria «Identifiability of the selected parameters».

Fuentes (resultados/identificabilidad/):
  perfil/<p>.json      — perfiles del modelo reducido (identificabilidad_perfil.py / _srv.py)
  local/<p>.json       — κ y VIF de J_{S∪Θ_C} en θ₀ (identificabilidad_local.py)
  certificado*.csv     — hipótesis del teorema de Lean (identificabilidad_certificado.py)
Salida: paper/scirep/tables/tableS_identif.tex y resultados/identificabilidad/resumen.md
"""
import json, math, glob
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
R = HERE / "resultados" / "identificabilidad"
PAPER = HERE.parent / "paper" / "scirep" / "tables"


def esc(s):
    return str(s).replace("_", "\\_\\allowbreak{}")


def corto(s):
    return s.split("_")[0].replace("SalazarCavazos", "Salazar-Cavazos")


cert = pd.concat([pd.read_csv(f) for f in sorted(R.glob("certificado*.csv"))], ignore_index=True)
cert = cert[cert["error"].isna()] if "error" in cert else cert
cert = cert.drop_duplicates(["sistema", "parametro"], keep="last").set_index(["sistema", "parametro"])


# máquina en que se calculó cada problema (S: servidor de 256 núcleos; el resto, estación de 8 núcleos)
SERVIDOR = {"Bachmann_MSB2011", "Chen_MSB2009", "Isensee_JCB2018", "Lang_PLOSComputBiol2024",
            "Raimundez_PCB2020", "Smith_BMCSystBiol2013"}


def tiempo_cpu(carpeta):
    """Tiempo de cómputo para determinar la identificabilidad: ajuste del problema reducido más
    todos los puntos de los perfiles (suma de los segundos de cada ajuste, última ronda)."""
    import numpy as _np
    m = _np.load(carpeta / "minimo.npz")
    t = float(m["segundos"]) if "segundos" in m.files else 0.0
    for f in carpeta.glob("p_*.json"):
        t += float(json.loads(f.read_text(encoding="utf-8")).get("segundos", 0.0))
    return t


def fmt_t(s):
    if s < 1:
        return "$<$1 s"
    if s < 60:
        return f"{s:.0f} s"
    if s < 3600:
        return f"{s / 60:.1f} min"
    return f"{s / 3600:.1f} h"

CLASE = {"identificable": "I", "no identificable practico": "N", "plano": "F"}
filas, res = [], []
for f in sorted((R / "perfil").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    s = d["sistema"]
    loc = json.loads((R / "local" / f"{s}.json").read_text()) if (R / "local" / f"{s}.json").exists() else {}
    vif = max(loc.get("VIF_SC_n_S", {}).values() or [float("nan")])
    cls, clsr, wald, lc = [], [], [], []
    for p in d["perfiles"]:
        c = CLASE[p["clase"]]
        # puntos del perfil que no se pudieron simular a ningún lado: no evaluable
        fall = p.get("puntos_fallidos", 0)
        if c == "F" and p["dchi2_max_izq"] == 0 and p["dchi2_max_der"] == 0 and fall > 0:
            c = "--"
        cls.append(c)
        clsr.append(CLASE[p["clase_robusto"]] if c != "--" else "--")
        key = (s, p["parametro"])
        if key in cert.index:
            r = cert.loc[key]
            wald.append(bool(r["certificado_lineal"]))
            lc.append(bool(r.get("certificado_local", False)))
    n = len(cls)
    ni = cls.count("I")
    res.append({"sistema": s, "n": n, "ident": ni, "todos": ni == n, "evaluables": n - cls.count("--"),
                "ident_robusto": clsr.count("I"), "chi2_gl": d["chi2_por_gl"],
                "wald_coincide": sum((w == (c == "I")) for w, c in zip(wald, cls) if c != "--"),
                "cert_local": sum(lc), "vif_local": vif,
                "segundos": tiempo_cpu(R / "perfil" / s), "servidor": s in SERVIDOR})
    filas.append([corto(s), str(n), str(d.get("n_calibracion", "")),
                  f"{d['chi2_por_gl']:.2f}" if d["chi2_por_gl"] < 100 else f"{d['chi2_por_gl']:,.0f}",
                  "--" if not math.isfinite(vif) else (f"{vif:.1f}" if vif < 1000 else f"{vif:.1e}"),
                  " ".join(cls), " ".join(clsr),
                  f"{sum(wald)}/{len(wald)}" if wald else "--", f"{sum(lc)}/{len(lc)}" if lc else "--",
                  fmt_t(res[-1]["segundos"]) + ("$^{\\mathrm{S}}$" if s in SERVIDOR else "")])

df = pd.DataFrame(res)
L = [r"\begin{longtable}{@{}lrrrrllrrr@{}}",
     r"\caption{Identifiability of the selected parameters in the reduced problem ($S\cup\Theta_C$ free, other parameters at $\theta_0$, all measurements). $|S|$, $|\Theta_C|$: selected biological and calibration parameters; $\chi^2/n$: at the optimum of the reduced problem; VIF: largest variance inflation factor of a selected parameter among the columns of $J_{S\cup\Theta_C}$ (unit-norm, uncentred) at $\theta_0$. Profile: class of each selected parameter by profile likelihood with $\Delta\chi^2=3.84$ within $[|\theta_0|/10,10|\theta_0|]$ (I, identifiable, the profile exceeds the threshold on both sides; N, practically non-identifiable, on one side; F, flat; --, the profile could not be simulated); robust: the same with the threshold scaled by $\max(1,\chi^2_{\min}/\mathrm{d.f.})$. Wald: parameters whose linear (Wald) interval $\sqrt{3.84\,[(J^{\top}J)^{-1}]_{jj}}$ fits within the bounds on both sides; Lean: parameters for which the hypotheses of \texttt{practically\_identifiable\_grad} hold at the computed profile points up to the first crossing. Time: computing time needed to determine the identifiability of the selected parameters, that is, the fit of the reduced problem plus the re-estimations at all profile points, summed over the fits (CPU time; the points were computed in parallel, so the wall-clock time is shorter); $^{\mathrm{S}}$, computed on a shared server (128 or 256 cores), otherwise on an 8-core workstation. For Isensee and Smith the profile was repeated after a better optimum was found, and only the last round is counted; for Chen, two profile points (one of them outside the bounds) did not finish and are not counted.}\label{tab:identif}\\",
     r"\toprule",
     r"Problem & $|S|$ & $|\Theta_C|$ & $\chi^2/n$ & VIF & Profile & Robust & Wald & Lean & Time \\",
     r"\midrule", r"\endfirsthead",
     r"\toprule",
     r"Problem & $|S|$ & $|\Theta_C|$ & $\chi^2/n$ & VIF & Profile & Robust & Wald & Lean & Time \\",
     r"\midrule", r"\endhead"]
L += [" & ".join(f) + r" \\" for f in filas]
L += [r"\bottomrule", r"\end{longtable}"]
PAPER.mkdir(parents=True, exist_ok=True)
(PAPER / "tableS_identif.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

tot = df["n"].sum()
md = [f"Problemas: {len(df)}; con todos los parámetros identificables: {int(df['todos'].sum())}",
      f"Parámetros identificables: {int(df['ident'].sum())} de {tot} (evaluables {int(df['evaluables'].sum())})",
      f"Robusto: {int(df['ident_robusto'].sum())} de {tot}; problemas todos identificables (robusto): "
      f"{int((df['ident_robusto'] == df['n']).sum())}",
      f"Wald coincide con el perfil en {int(df['wald_coincide'].sum())} de {int(df['evaluables'].sum())} evaluables",
      f"Certificado local (Lean, hipótesis en los puntos): {int(df['cert_local'].sum())} parámetros",
      "", df.to_string()]
(R / "resumen.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md[:5]))
