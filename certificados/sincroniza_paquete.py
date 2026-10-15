#!/usr/bin/env python3
"""
Copia al paquete de reproducibilidad (reproducibility/results/) los resultados de certificados/resultados/
de los problemas que cambiaron con la corrección de los escenarios (recorte max(θ₀(1+εu), 1e-12)):
Armistead y Raimundez (subconjunto nuevo) y Lang (deja de ser admisible). Los resultados anteriores
del paquete se guardan en results/_before_negative_fix/<carpeta>/ (sin sobrescribir copias previas).
Además añade las carpetas de los análisis nuevos de la auditoría (B5, C3, error en unidades de σ).

Uso: python sincroniza_paquete.py            (muestra lo que haría)
     python sincroniza_paquete.py --aplica
"""
import os, sys, shutil, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = HERE / "resultados"
R = HERE.parent / "reproducibility" / "results"
B = R / "_before_negative_fix"
PROB = ["Armistead_CellDeathDis2024", "Raimundez_PCB2020", "Lang_PLOSComputBiol2024"]
APLICA = "--aplica" in sys.argv

# carpeta del paquete  <-  carpeta de certificados (mismo formato y nombres de archivo)
MAPA = {"selection": "reclasificacion_salidas_bio_poda", "criteria_tests": "control_admis_sint",
        "criteria_tests_20pc": "control_admis_sint_nivel020", "qr_selection": "comparacion_brun",
        "brun_morris": "control_morris_brun", "random_subsets": "control_aleatorio",
        "calibration_only": "control_vacio", "profile_likelihood": "control_perfil",
        "synthetic_seeds": "sintetico_semillas", "external_validation": "validacion_externa_bio",
        "nested_validation": "validacion_anidada", "robustness": "patrones",
        "single_parameter": "un_parametro_final"}
AJUSTES = {"delta0001": "delta_0.001", "delta005": "delta_0.05", "nivel001": "perturbation_0.01",
           "nivel010": "perturbation_0.10", "emax010": "tauE_0.10", "emax020": "tauE_0.20",
           "emax030": "tauE_0.30", "emax050": "tauE_0.50", "kv30": "tauK_30", "kv5": "tauK_5",
           "rvar080": "tauR_0.80", "rvar085": "tauR_0.85", "rvar095": "tauR_0.95",
           "tolgruesa": "tolerances_1e-6_1e-8", "tolfina": "tolerances_1e-9_1e-12"}
NUEVAS = {"robustness_independent": "patrones_indep", "synthetic_signal_a020": "sintetico_senal_a020",
          "synthetic_signal_a005": "sintetico_senal_a005", "synthetic_signal_a050": "sintetico_senal_a050",
          "synthetic_seeds_a005": "sintetico_semillas_a005", "synthetic_seeds_a050": "sintetico_semillas_a050",
          "absolute_error": "error_absoluto"}
acciones = []


def quita(p):
    """Mueve p (archivo o carpeta del paquete) a _before_negative_fix/, sin sobrescribir copias previas."""
    rel = p.relative_to(R)
    destino = B / rel
    if destino.exists():
        acciones.append(("borra", p))
    else:
        acciones.append(("respalda", p, destino))


def copia(src, dst):
    acciones.append(("copia", src, dst))


for rd, cd in MAPA.items():
    for n in PROB:
        for p in sorted((R / rd).glob(f"{n}*")):
            quita(p)
        for s in sorted((C / cd).glob(f"{n}*")):
            if cd == "patrones" and s.is_dir():
                continue
            if rd == "criteria_tests_20pc" and not s.name.endswith("__adm.json"):
                continue   # el paquete sólo guarda la admisibilidad a ±20 % (como en los demás problemas)
            copia(s, R / rd / s.name)
# ajustes del método: el análisis del artículo cubre 26 problemas; sólo se actualizan los presentes
for tag, rd in AJUSTES.items():
    for n in PROB:
        p = R / "settings" / rd / f"{n}.json"
        if p.exists():
            quita(p)
            copia(C / f"reclasificacion_salidas_bio_poda_{tag}" / f"{n}.json", p)
# análisis nuevos, completos
for rd, cd in NUEVAS.items():
    if (C / cd).exists():
        if (R / rd).exists():
            acciones.append(("borra", R / rd))
        copia(C / cd, R / rd)

for a in acciones:
    print(a[0], *[str(x).replace(str(HERE.parent), "") for x in a[1:]])
print(len(acciones), "acciones")
if APLICA:
    for a in acciones:
        if a[0] == "respalda":
            a[2].parent.mkdir(parents=True, exist_ok=True); shutil.move(str(a[1]), str(a[2]))
        elif a[0] == "borra":
            shutil.rmtree(a[1]) if a[1].is_dir() else a[1].unlink()
    for a in acciones:
        if a[0] == "copia":
            a[2].parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree(a[1], a[2], dirs_exist_ok=True) if a[1].is_dir() else shutil.copy2(a[1], a[2]))
    # identificabilidad: CSV completos y, por problema, perfiles (perfil -> profiles) y análisis local
    CI, RI, BI = C / "identificabilidad", R / "identifiability", B / "identifiability"
    for f in CI.glob("*.csv"):
        shutil.copy2(f, RI / f.name)
    for sc, sr in (("perfil", "profiles"), ("local", "local")):
        for n in PROB:
            for p in list((RI / sr).glob(f"{n}*")):
                dst = BI / sr / p.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    shutil.move(str(p), str(dst))
                else:
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
            for p in (CI / sc).glob(f"{n}*"):
                (shutil.copytree(p, RI / sr / p.name, dirs_exist_ok=True) if p.is_dir() else shutil.copy2(p, RI / sr / p.name))
    print("aplicado")
