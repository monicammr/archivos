"""Organiza los resultados del servidor (segunda auditoría) en una carpeta por sistema, con un PDF
que explica qué se hizo, por qué y qué salió para ese sistema."""
import csv
import glob
import json
import math
import os
import shutil
import statistics as st
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ST = Path(r"C:\Users\monic\AppData\Local\Temp\claude\servidor_staging")
REPO = Path(r"C:\Users\monic\Documents\archivos-certificados\reproducibility\results")
OUT = Path(r"C:\Users\monic\Downloads\Servidor_auditoria2_2026-10-16")
TAU = math.sqrt(1 - 0.81)

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Arial-Bold", fontSize=16, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Arial-Bold", fontSize=12.5, spaceBefore=10, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontName="Arial", fontSize=9.5, leading=13, spaceAfter=5)
SM = ParagraphStyle("SM", parent=P, fontSize=8, leading=10.5)
CELL = ParagraphStyle("CELL", parent=P, fontSize=8, leading=10, spaceAfter=0)


def L(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None


def f3(x, n=3):
    if x is None:
        return "—"
    try:
        x = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(x):
        return "∞" if x > 0 else "—"
    return f"{x:.{n}f}"


def table(rows, widths=None, header=True):
    data = [[Paragraph(str(c), CELL) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")))
    t.setStyle(TableStyle(style))
    return t


def yesno(b):
    return "sí" if b else "no" if b is not None else "—"


NAMES = ["ours", "train", "brun", "morris", "perfil", "qr", "qr_gks", "empty"]
LABEL = {"ours": "Tu método (todas las salidas)", "train": "Tu método (solo entrenamiento)",
         "brun": "Brun (colinealidad)", "morris": "Morris", "perfil": "Perfil de verosimilitud",
         "qr": "QR pivotado (versión anterior)", "qr_gks": "QR estándar (Golub–Klema–Stewart)",
         "empty": "Solo calibración (k = 0)"}

# ------------------------------------------------------------------------------------------ data
problems = sorted(Path(f).stem for f in glob.glob(str(REPO / "selection" / "*.json")))
box = {}
for r in ["10", "5", "3", "2", "1.5"]:
    fn = ST / "identifiability" / (f"certificado_box_parametros.csv" if r == "10" else f"certificado_box_r{r}_parametros.csv")
    for row in csv.DictReader(open(fn, encoding="utf-8")):
        box.setdefault(row["sistema"], {}).setdefault(row["parametro"], {})[r] = row["pf"] == "True"
cond = {r["sistema"]: r for r in (L(ST / "conditioning_check.json") or [])}
cert_train = {}
for row in csv.DictReader(open(ST / "identifiability" / "certificado_train.csv", encoding="utf-8")):
    cert_train.setdefault(row["sistema"], []).append(row)


def adm(name, metodo, nivel):
    d = L(ST / ("criteria_tests_fixedscen" if nivel == 5 else "criteria_tests_20pc_fixedscen") / f"{name}__{metodo}__adm.json")
    return d


def sint(folder, name, metodo):
    """(casos con señal, éxitos) de la familia de verdades `folder` para un método."""
    n = k = 0
    if metodo == "ours" and folder == "uniforme":
        files = glob.glob(str(REPO / "synthetic_seeds" / name / "s*.json"))
        recs = [L(f) for f in files]
    else:
        base = {"uniforme": ["criteria_tests", "criteria_tests_fixedscen"],
                "loguniforme": ["criteria_tests_sint_loguniforme"],
                "dispersa": ["criteria_tests_sint_dispersa"]}[folder]
        recs = []
        seen = set()
        for b in base:
            d = (ST / b) if (ST / b).exists() else (REPO / b)
            for f in glob.glob(str(d / f"{name}__{metodo}__sint_*.json")):
                if Path(f).name in seen:
                    continue
                seen.add(Path(f).name)
                recs.append(L(f))
    for r in recs:
        if not r or r.get("B_epred_red") is None or r.get("B_chi2_test_theta0") is None:
            continue
        if r["B_chi2_test_theta0"] < 2:
            continue
        e = r["B_epred_red"]
        if e is None or not math.isfinite(float(e)):
            continue
        n += 1
        k += float(e) <= TAU
    return n, k


# ------------------------------------------------------------------------------------- texts
INTRO = ("Este documento resume los análisis que se hicieron en el servidor (88 núcleos, 15–16 de "
         "octubre de 2026) para responder a la segunda auditoría del manuscrito para <i>Scientific "
         "Reports</i>. Cada sección dice qué se hizo, por qué se hizo (qué objeción de un revisor "
         "responde) y qué salió para este sistema. Los archivos de resultados de este sistema están en "
         "las subcarpetas de esta carpeta; el resumen global y la verificación de Lean están en "
         "<b>00_General</b>.")
WHY = {
    "A5": ("<b>Por qué.</b> En la versión anterior, si la simulación con el subconjunto fallaba en un "
           "escenario, ese escenario se descartaba, de modo que cada subconjunto podía evaluarse con "
           "escenarios distintos. Además, el Teorema 2 (ningún subconjunto más pequeño sirve) necesita "
           "que la admisibilidad sea monótona, y eso no se había comprobado."),
    "A1": ("<b>Por qué.</b> Tu método elegía los parámetros mirando todas las salidas medidas, incluidas "
           "las condiciones que después se usan como prueba, mientras que los otros criterios elegían "
           "solo con las de entrenamiento. Para que la comparación sea justa, se repitió tu selección "
           "viendo solo las salidas de entrenamiento."),
    "A2": ("<b>Por qué.</b> En los seis problemas con simulaciones más caras la admisibilidad se había "
           "decidido con una aproximación lineal (primer orden) del error de re-estimación. Se comprobó "
           "con el cálculo no lineal real, con los mismos ajustes que en los demás problemas."),
    "A3": ("<b>Por qué.</b> Para saber si pasar la prueba de admisibilidad tiene mérito, hay que ver qué "
           "pasa con subconjuntos sin selección: re-estimar solo la calibración (k = 0) y 20 subconjuntos "
           "aleatorios del mismo tamaño. También se evaluaron con la misma regla los otros criterios y el "
           "QR estándar (el QR anterior no era el algoritmo de la literatura)."),
    "A6": ("<b>Por qué.</b> En la prueba sintética original las «verdades» se generaban con el mismo tipo "
           "de perturbación que usa tu método para decidir, lo que podía favorecerlo. Se repitió con otras "
           "dos familias: log-uniforme (cada parámetro multiplicado por un factor entre 0,5 y 2) y "
           "dispersa (el 15 % de los parámetros cambia ±50 %)."),
    "ID": ("<b>Por qué.</b> La identificabilidad se apoyaba en perfiles de verosimilitud (evidencia "
           "numérica) y en un teorema de Lean cuya hipótesis sobre el resto no lineal se había comprobado "
           "solo a lo largo del perfil, no en todo el conjunto que exige el teorema. Se hicieron tres "
           "refuerzos: (a) perfiles de los subconjuntos elegidos con entrenamiento; (b) perfiles densos "
           "(20 puntos por lado en vez de 10); (c) comprobación de la hipótesis en toda la región "
           "alrededor del óptimo (muestreo de 512 puntos y búsqueda del peor caso), para regiones de "
           "factor 10, 5, 3, 2 y 1,5, con los nuevos teoremas de Lean que solo piden la cota en la "
           "cola del perfil."),
    "COND": ("<b>Por qué.</b> El código calcula κ y VIF con columnas centradas (matriz de correlación), "
             "mientras que el teorema de Lean sobre mínimos cuadrados usa columnas de longitud 1 sin "
             "centrar. Se calcularon las dos versiones para ver si el teorema se aplica."),
}


def system_pdf(name, dest):
    orig = L(REPO / "selection" / f"{name}.json") or {}
    a5 = L(ST / "selection_fixedscen" / f"{name}.json") or {}
    a1 = L(ST / "selection_train_fixedscen" / f"{name}.json") or {}
    story = [Paragraph(f"{name}", H1), Paragraph(INTRO, P)]

    # ---- 0. original selection
    story.append(Paragraph("Punto de partida: la selección del paper", H2))
    story.append(table([
        ["Subconjunto seleccionado", "e_fit (mediana)", "Admisible", "Parámetros de calibración"],
        [", ".join(orig.get("S", [])) or "—", f3(orig.get("eajuste_med")), yesno(orig.get("admisible")),
         str(len(orig.get("calibracion", [])))]], [7 * cm, 2.6 * cm, 2 * cm, 3.4 * cm]))
    story.append(Paragraph(f"Umbral de admisibilidad: e_fit ≤ τ = {TAU:.5f}.", SM))

    # ---- A5
    story.append(Paragraph("A5 · Conjunto fijo de escenarios y monotonía", H2))
    story.append(Paragraph(WHY["A5"], P))
    if a5:
        same = set(a5.get("S", [])) == set(orig.get("S", []))
        m = a5.get("monotonia", {})
        story.append(table([
            ["Subconjunto con escenarios fijos", "¿Igual al original?", "e_fit", "Admisible",
             "Pares anidados revisados", "Violaciones de monotonía"],
            [", ".join(a5.get("S", [])) or "—", yesno(same), f3(a5.get("eajuste_med")),
             yesno(a5.get("admisible")), str(m.get("nested_pairs", "—")), str(m.get("violations", "—"))]],
            [5 * cm, 2 * cm, 1.6 * cm, 1.6 * cm, 2.6 * cm, 2.6 * cm]))
        story.append(Paragraph("<b>Qué significa.</b> " + (
            "El subconjunto no cambia: la forma de tratar los escenarios que fallan no afectaba al resultado. "
            if same else "El subconjunto cambia al fijar los escenarios; ver el archivo de esta carpeta. ") +
            ("No se encontró ninguna violación de monotonía entre los subconjuntos evaluados."
             if m.get("violations", 0) == 0 else "Hay violaciones de monotonía; revisar."), P))
    else:
        story.append(Paragraph("No disponible para este sistema.", P))

    # ---- A1
    story.append(Paragraph("A1 · Selección usando solo las salidas de entrenamiento", H2))
    story.append(Paragraph(WHY["A1"], P))
    if a1:
        rows = [["Subconjunto (solo entrenamiento)", "Filas usadas", "e_fit", "Admisible", "¿Igual al original?"],
                [", ".join(a1.get("S", [])) or "—", str(a1.get("n_rows", "—")), f3(a1.get("eajuste_med")),
                 yesno(a1.get("admisible")), yesno(set(a1.get("S", [])) == set(orig.get("S", [])))]]
        story.append(table(rows, [6 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm]))
        ad5, ad20 = adm(name, "train", 5), adm(name, "train", 20)
        real = L(ST / "criteria_tests_fixedscen" / f"{name}__train__real.json")
        txt = []
        if ad5 and "admisible" in ad5:
            txt.append(f"Ese subconjunto, evaluado sobre todas las salidas, es admisible a ±5 %: {yesno(ad5['admisible'])} "
                       f"(e_fit {f3(ad5.get('eajuste_med'))}); a ±20 %: {yesno((ad20 or {}).get('admisible'))}.")
        if real and real.get("ratio_vs_ours") is not None:
            txt.append(f"En datos reales, su χ²/n de prueba es {f3(real['ratio_vs_ours'], 2)} veces el del subconjunto original.")
        if a1.get("outputs") == "all":
            txt.append("Este problema no tiene división entrenamiento/prueba (una sola condición y un solo tiempo), "
                       "así que la selección usa todas las salidas.")
        story.append(Paragraph(" ".join(txt) or "Sin pruebas comparativas para este sistema.", P))
    else:
        story.append(Paragraph("No disponible.", P))

    # ---- A2
    en = L(ST / "efit_nonlinear" / f"{name}.json")
    if en:
        story.append(Paragraph("A2 · Verificación no lineal (problema de primer orden)", H2))
        story.append(Paragraph(WHY["A2"], P))
        story.append(table([
            ["e_fit primer orden", "e_fit no lineal", "Escenarios válidos", "Tasa de paso", "Admisible (no lineal)", "Tiempo de cálculo"],
            [f3(en["eajuste_med_primer_orden"], 5), f3(en["eajuste_med_nolineal"], 5), str(en["n_escenarios_validos"]),
             f"{100 * en['tasa_paso_nolineal']:.0f} %", yesno(en["admisible_nolineal"]),
             f"{en['segundos_total'] / 3600:.1f} h CPU"]], [2.6 * cm] * 6))
        story.append(Paragraph("<b>Qué significa.</b> La aproximación de primer orden "
                               + ("queda confirmada por el cálculo no lineal." if en["admisible_nolineal"] else
                                  "NO queda confirmada por el cálculo no lineal.")
                               + (" El margen frente al umbral es muy pequeño, así que la admisibilidad es límite."
                                  if abs(en["eajuste_med_nolineal"] - TAU) < 0.01 else ""), P))

    # ---- A3 / A4 admissibility table
    story.append(Paragraph("A3 y A4 · Admisibilidad de todos los criterios y controles nulos", H2))
    story.append(Paragraph(WHY["A3"], P))
    rows = [["Criterio", "Subconjunto", "±5 %: e_fit", "±5 % admisible", "±20 % admisible"]]
    any_ = False
    for mth in ["ours", "brun", "morris", "perfil", "qr", "qr_gks", "train", "empty"]:
        d5, d20 = adm(name, mth, 5), adm(name, mth, 20)
        if not d5 or "eajuste_med" not in d5:
            continue
        any_ = True
        key = "admisible_sin_kmin" if mth == "empty" else "admisible"
        rows.append([LABEL[mth], ", ".join(d5.get("S", [])) or "(ninguno)", f3(d5.get("eajuste_med")),
                     yesno(d5.get(key)), yesno((d20 or {}).get(key))])
    r5 = [adm(name, f"rand{i}", 5) for i in range(20)]
    r20 = [adm(name, f"rand{i}", 20) for i in range(20)]
    r5 = [d for d in r5 if d and "admisible" in d]
    r20 = [d for d in r20 if d and "admisible" in d]
    if r5:
        any_ = True
        rows.append(["20 subconjuntos aleatorios", f"{len(r5)} sorteos",
                     f3(st.median([d['eajuste_med'] for d in r5])),
                     f"{sum(d['admisible'] for d in r5)} de {len(r5)}",
                     f"{sum(d['admisible'] for d in r20)} de {len(r20)}" if r20 else "—"])
    if any_:
        story.append(table(rows, [4.6 * cm, 5.4 * cm, 1.8 * cm, 2 * cm, 2 * cm]))
        story.append(Paragraph("<b>Cómo leerlo.</b> Si los controles (solo calibración, aleatorios) también "
                               "son admisibles, pasar la prueba tiene poco mérito en este sistema; si fallan y tu "
                               "subconjunto pasa, la selección aporta algo real.", P))
    else:
        story.append(Paragraph("Este sistema no entra en la comparación de criterios (sin subconjunto admisible, "
                               "o excluido por coste de simulación o por no tener división entrenamiento/prueba).", P))
    gks = L(ST / "qr_selection_gks" / f"{name}.json")
    if gks and gks.get("S_qr"):
        story.append(Paragraph(f"QR estándar eligió {', '.join(gks['S_qr'])} (en común con tu subconjunto: "
                               f"{gks.get('overlap', '—')}); χ²/n de prueba en datos reales: {f3(gks.get('chi2_qr'), 2)} "
                               f"frente a {f3(gks.get('chi2_ours'), 2)} del tuyo.", P))

    # ---- A6 synthetic
    story.append(Paragraph("A6 · Predicción sobre datos sintéticos con tres familias de verdades", H2))
    story.append(Paragraph(WHY["A6"], P))
    rows = [["Criterio", "Uniforme ±20 % (20 semillas)", "Log-uniforme (10 semillas)", "Dispersa (10 semillas)"]]
    any_ = False
    for mth in ["ours", "train", "brun", "morris", "perfil", "qr", "qr_gks"]:
        cells = []
        for fam in ["uniforme", "loguniforme", "dispersa"]:
            n, k = sint(fam, name, mth)
            cells.append(f"{k}/{n} ({100 * k / n:.0f} %)" if n else "—")
        if any(c != "—" for c in cells):
            any_ = True
            rows.append([LABEL[mth]] + cells)
    if any_:
        story.append(table(rows, [5 * cm, 3.6 * cm, 3.6 * cm, 3.6 * cm]))
        story.append(Paragraph("Cada celda: casos (semillas) con señal mayor que el ruido en los que el subconjunto "
                               "predice la verdad con error relativo ≤ τ. «—»: sin casos con señal o no evaluado.", SM))
    else:
        story.append(Paragraph("Sin casos sintéticos con señal para este sistema (o no participa en la comparación).", P))

    # ---- identifiability
    story.append(Paragraph("Identificabilidad de los parámetros seleccionados", H2))
    story.append(Paragraph(WHY["ID"], P))
    po = L(REPO / "identifiability" / "profiles" / f"{name}.json")
    pdn = L(ST / "identifiability" / "profiles_dense" / f"{name}.json")
    if po:
        dense = {p["parametro"]: p["clase"] for p in (pdn or {}).get("perfiles", [])}
        rows = [["Parámetro", "Perfil original (10 puntos/lado)", "Perfil denso (20 puntos/lado)",
                 "Hipótesis de Lean en la región: factor 10 / 5 / 3 / 2 / 1,5"]]
        for p in po["perfiles"]:
            b = box.get(name, {}).get(p["parametro"], {})
            br = " / ".join("sí" if b.get(r) else "no" for r in ["10", "5", "3", "2", "1.5"]) if b else "—"
            rows.append([p["parametro"], p["clase"], dense.get(p["parametro"], "—"), br])
        story.append(table(rows, [4.2 * cm, 3.6 * cm, 3.6 * cm, 5 * cm]))
        story.append(Paragraph("«identificable»: el intervalo de confianza del 95 % del perfil queda acotado a ambos lados "
                               "dentro del rango del estudio. «sí» en la última columna: las hipótesis del teorema de Lean (resto no lineal "
                               "acotado en la cola del perfil, absoluto o relativo) se cumplen en toda la región de "
                               "ese factor alrededor del óptimo, según el muestreo y la búsqueda del peor caso; es una "
                               "comprobación numérica, no un certificado.", SM))
    else:
        story.append(Paragraph("No hay perfiles para este sistema (no tiene subconjunto admisible).", P))
    pt = L(ST / "identifiability" / "profiles_selection_train_fixedscen" / f"{name}.json")
    if pt:
        story.append(Paragraph("(a) Subconjunto elegido con entrenamiento: " + "; ".join(
            f"{p['parametro']}: {p['clase']}" for p in pt["perfiles"]) + ".", P))

    c = cond.get(name)
    if c:
        story.append(Paragraph("Condicionamiento: columnas centradas frente a longitud 1", H2))
        story.append(Paragraph(WHY["COND"], P))
        story.append(table([
            ["κ centrado", "VIF centrado", "κ longitud 1", "VIF longitud 1", "κ con calibración", "¿Aplica el teorema (≤ 10)?"],
            [f3(c["kappa_centred"], 2), f3(c["VIF_centred"], 2), f3(c["kappa_unit"], 2), f3(c["VIF_unit"], 2),
             f3(c["kappa_unit_with_calibration"], 2) if c["kappa_unit_with_calibration"] < 1e6 else f"{c['kappa_unit_with_calibration']:.1e}",
             yesno(c["kappa_unit"] <= 10 and c["VIF_unit"] <= 10)]], [2.7 * cm] * 6))

    # ---- files
    story.append(Paragraph("Archivos de esta carpeta", H2))
    files = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file() and p.suffix != ".pdf")
    story.append(Paragraph(f"{len(files)} archivos. Subcarpetas: " + ", ".join(sorted({f.split(os.sep)[0] for f in files if os.sep in f})) + ".", P))
    SimpleDocTemplate(str(dest / f"{name}_explicacion.pdf"), pagesize=A4, leftMargin=1.6 * cm,
                      rightMargin=1.6 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                      title=f"{name}: análisis de la segunda auditoría").build(story)


def copy_system(name, dest):
    def cp(src, sub):
        src = Path(src)
        if src.exists():
            (dest / sub).mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dest / sub / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest / sub / src.name)
    cp(ST / "selection_fixedscen" / f"{name}.json", "A5_escenarios_fijos")
    cp(ST / "selection_train_fixedscen" / f"{name}.json", "A1_seleccion_entrenamiento")
    cp(ST / "efit_nonlinear" / f"{name}.json", "A2_efit_no_lineal")
    cp(ST / "efit_nonlinear" / name, "A2_efit_no_lineal")
    cp(ST / "qr_selection_gks" / f"{name}.json", "A4_QR_estandar")
    for f in glob.glob(str(ST / "criteria_tests_fixedscen" / f"{name}__*")):
        cp(f, "A3_A4_criterios_5pc")
    for f in glob.glob(str(ST / "criteria_tests_20pc_fixedscen" / f"{name}__*")):
        cp(f, "A3_A4_criterios_20pc")
    for fam in ["loguniforme", "dispersa"]:
        for f in glob.glob(str(ST / f"criteria_tests_sint_{fam}" / f"{name}__*")):
            cp(f, f"A6_sintetico_{fam}")
    cp(ST / "identifiability" / "profiles_dense" / f"{name}.json", "Identificabilidad_perfiles_densos")
    cp(ST / "identifiability" / "profiles_dense" / name, "Identificabilidad_perfiles_densos")
    cp(ST / "identifiability" / "profiles_selection_train_fixedscen" / f"{name}.json", "Identificabilidad_subconjunto_entrenamiento")
    cp(ST / "identifiability" / "profiles_selection_train_fixedscen" / name, "Identificabilidad_subconjunto_entrenamiento")
    cp(ST / "identifiability" / "box" / name, "Identificabilidad_region_admisible")
    rows = []
    for r in ["", "_r5", "_r3", "_r2", "_r1.5"]:
        fn = ST / "identifiability" / f"certificado_box{r}.csv"
        for row in csv.DictReader(open(fn, encoding="utf-8")):
            if row["sistema"] == name:
                row["radio"] = r.replace("_r", "") or "10"
                rows.append(row)
    if rows:
        (dest / "Identificabilidad_region_admisible").mkdir(parents=True, exist_ok=True)
        with open(dest / "Identificabilidad_region_admisible" / f"{name}_hipotesis_por_radio.csv", "w",
                  newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    if name in cond:
        (dest / "Condicionamiento").mkdir(parents=True, exist_ok=True)
        (dest / "Condicionamiento" / f"{name}_kappa_vif.json").write_text(json.dumps(cond[name], indent=1), encoding="utf-8")


if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for i, n in enumerate(problems, 1):
        dest = OUT / f"{i:02d}_{n}"
        dest.mkdir()
        copy_system(n, dest)
        system_pdf(n, dest)
        print("ok", n)
