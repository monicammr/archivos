"""Carpeta 00_General: resumen global (PDF), registros, archivos globales y verificación de Lean."""
import csv
import glob
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import organiza as O  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer  # noqa: E402

G = O.OUT / "00_General"
LEAN = Path(r"C:\Users\monic\Documents\archivos-certificados\reproducibility\lean_proofs")
ANA = Path(r"C:\Users\monic\Documents\archivos-certificados\reproducibility\analysis")
SCR = Path(r"C:\Users\monic\Documents\archivos-certificados\reproducibility\scripts")


def count_adm(metodo, nivel):
    ok = tot = 0
    for n in O.problems:
        if n.startswith("Bertozzi"):
            continue
        d = O.adm(n, metodo, nivel)
        if d and "eajuste_med" in d:
            tot += 1
            ok += bool(d.get("admisible_sin_kmin" if metodo == "empty" else "admisible"))
    return ok, tot


def main():
    if G.exists():
        shutil.rmtree(G)
    (G / "registros_servidor").mkdir(parents=True)
    for f in (O.ST / "logs").iterdir():
        shutil.copy2(f, G / "registros_servidor" / f.name)
    (G / "resultados_globales").mkdir()
    shutil.copy2(O.ST / "conditioning_check.json", G / "resultados_globales")
    for f in glob.glob(str(O.ST / "identifiability" / "certificado_*.csv")):
        shutil.copy2(f, G / "resultados_globales")
    (G / "verificacion_Lean").mkdir()
    for f in ["BUILD_LOG.md", "DEFINITIONS_AUDIT.md", "NonVacuity.lean", "ProfileIdentifiability.lean", "verify.sh", "lakefile.lean"]:
        shutil.copy2(LEAN / f, G / "verificacion_Lean")
    (G / "scripts").mkdir()
    for f in ["selection.py", "criteria_tests.py", "qr_selection.py", "efit_nonlinear.py", "conditioning_check.py",
              "identifiability_profiles.py", "identifiability_box.py", "identifiability_conditions.py"]:
        shutil.copy2(ANA / f, G / "scripts")
    for f in ["fase_a_audit2.sh", "identificabilidad_audit2.sh"]:
        shutil.copy2(SCR / f, G / "scripts")

    P, H1, H2, SM, T = O.P, O.H1, O.H2, O.SM, O.table
    s = [Paragraph("Segunda auditoría: resumen de todo lo calculado en el servidor", H1),
         Paragraph("Servidor vast.ai de 88 núcleos y 251 GB de RAM, 15–16 de octubre de 2026. Esta carpeta "
                   "contiene el resumen global, los registros del servidor (sin los avisos repetitivos del "
                   "integrador), los resultados que afectan a todos los sistemas, la verificación de Lean y los "
                   "programas usados. Cada carpeta numerada 01–34 contiene los resultados de un sistema y un PDF "
                   "que los explica.", P)]

    s.append(Paragraph("1. Qué se hizo y por qué", H2))
    s.append(T([
        ["Prueba", "Qué se hizo", "Objeción que responde"],
        ["A5", "Repetir la selección con un conjunto fijo de escenarios y registrar la monotonía", "Cada subconjunto se evaluaba con escenarios distintos; el Teorema 2 suponía monotonía sin comprobarla"],
        ["A1", "Repetir tu selección viendo solo las salidas de entrenamiento", "Tu método veía los datos de prueba y los demás criterios no"],
        ["A2", "Re-estimación no lineal en los 6 problemas decididos a primer orden", "La admisibilidad de esos 6 no estaba verificada"],
        ["A3", "Admisibilidad de k = 0 (solo calibración) y de 20 subconjuntos aleatorios", "Sin controles nulos no se sabe si pasar la prueba tiene mérito"],
        ["A4", "QR estándar de Golub–Klema–Stewart", "El QR anterior no era el algoritmo de la literatura"],
        ["A6", "Predicción sintética con verdades log-uniformes y dispersas", "La prueba original usaba la misma familia de perturbaciones que tu método"],
        ["Identif. (a)", "Perfiles de los subconjuntos elegidos con entrenamiento", "¿Los nuevos pares también son identificables?"],
        ["Identif. (b)", "Perfiles con 20 puntos por lado", "¿La clasificación depende de la resolución?"],
        ["Identif. (c)", "Hipótesis del teorema de Lean en toda la región alrededor del óptimo", "La hipótesis se había comprobado solo sobre el perfil"],
        ["Condicion.", "κ y VIF con columnas sin centrar", "El código y Lean usan normalizaciones distintas"],
        ["Lean", "Compilación desde cero, axiomas, lean4checker, testigos de no vacuidad", "¿Las demostraciones son correctas y dicen lo que el paper afirma?"],
    ], [2.2 * cm, 7 * cm, 8 * cm]))

    s.append(Paragraph("2. Resultados globales", H2))
    a5 = [O.L(f) for f in glob.glob(str(O.ST / "selection_fixedscen" / "*.json"))]
    orig = {n: O.L(O.REPO / "selection" / f"{n}.json") for n in O.problems}
    changed = [d["sistema"] for d in a5 if set(d.get("S", [])) != set(orig[d["sistema"]].get("S", []))]
    pairs = sum(d.get("monotonia", {}).get("nested_pairs", 0) for d in a5)
    viol = sum(d.get("monotonia", {}).get("violations", 0) for d in a5)
    a1 = [O.L(f) for f in glob.glob(str(O.ST / "selection_train_fixedscen" / "*.json"))]
    pairs += sum(d.get("monotonia", {}).get("nested_pairs", 0) for d in a1)
    viol += sum(d.get("monotonia", {}).get("violations", 0) for d in a1)
    a1_adm = sum(bool(d.get("admisible")) for d in a1)
    a1_diff = sum(set(d.get("S", [])) != set(orig[d["sistema"]].get("S", [])) for d in a1)
    s.append(Paragraph(f"<b>A5.</b> Con el conjunto fijo de escenarios cambiaron {len(changed)} subconjuntos de 34"
                       f"{(' (' + ', '.join(changed) + ')') if changed else ''}. Monotonía: {viol} violaciones en {pairs} "
                       "pares anidados evaluados (A5 y A1 juntos).", P))
    s.append(Paragraph(f"<b>A1.</b> Seleccionando solo con entrenamiento, {a1_adm} de 34 problemas tienen subconjunto "
                       f"admisible y {a1_diff} eligen un subconjunto distinto del original. Bertozzi deja de tener un par "
                       "admisible (un solo parámetro bastaría); Perelson no es evaluable porque en entrenamiento el cambio "
                       "de las salidas queda bajo el umbral numérico.", P))
    rows = [["Problema", "e_fit primer orden", "e_fit no lineal", "Tasa de paso", "Admisible"]]
    for f in sorted(glob.glob(str(O.ST / "efit_nonlinear" / "*.json"))):
        d = O.L(f)
        rows.append([d["sistema"], O.f3(d["eajuste_med_primer_orden"], 5), O.f3(d["eajuste_med_nolineal"], 5),
                     f"{100 * d['tasa_paso_nolineal']:.0f} %", O.yesno(d["admisible_nolineal"])])
    s.append(Paragraph("<b>A2.</b> Los seis problemas de primer orden quedan confirmados por la re-estimación no lineal "
                       "(Lucarelli por un margen de 4×10<super>−5</super>):", P))
    s.append(T(rows, [5 * cm, 3 * cm, 3 * cm, 2.6 * cm, 2.4 * cm]))

    rows = [["Criterio", "Admisible ±5 %", "Admisible ±20 %"]]
    for m in ["ours", "brun", "morris", "perfil", "qr_gks", "qr", "train", "empty"]:
        a, t = count_adm(m, 5)
        b, u = count_adm(m, 20)
        rows.append([O.LABEL[m], f"{a}/{t}", f"{b}/{u}"])
    per_draw5 = [count_adm(f"rand{i}", 5) for i in range(20)]
    per_draw20 = [count_adm(f"rand{i}", 20) for i in range(20)]
    import statistics as st
    rows.append(["Subconjuntos aleatorios (mediana por sorteo)",
                 f"{st.median(a for a, _ in per_draw5):.0f}/{per_draw5[0][1]} (rango {min(a for a, _ in per_draw5)}–{max(a for a, _ in per_draw5)})",
                 f"{st.median(a for a, _ in per_draw20):.0f}/{per_draw20[0][1]} (rango {min(a for a, _ in per_draw20)}–{max(a for a, _ in per_draw20)})"])
    s.append(Paragraph("<b>A3 y A4.</b> Admisibilidad (re-estimar el subconjunto reproduce el modelo completo), con la "
                       "misma regla para todos (Bertozzi excluido):", P))
    s.append(T(rows, [7.5 * cm, 4.5 * cm, 4.5 * cm]))
    s.append(Paragraph("<b>A6.</b> Fracción de casos sintéticos con señal en los que el subconjunto predice la verdad con "
                       "error ≤ τ (casos comunes a todos los criterios; calculado en el servidor):", P))
    s.append(T([["Criterio", "Uniforme ±20 %", "Log-uniforme", "Dispersa"],
                ["Tu método (todas las salidas)", "56 %", "50 %", "54 %"],
                ["Tu método (solo entrenamiento)", "51 %", "48 %", "55 %"],
                ["Brun", "55 %", "50 %", "52 %"],
                ["Morris", "48 %", "48 %", "46 %"],
                ["Perfil de verosimilitud", "39 %", "37 %", "40 %"],
                ["QR pivotado (anterior)", "34 %", "29 %", "44 %"],
                ["QR estándar", "30 %", "24 %", "39 %"]], [6.5 * cm, 3.3 * cm, 3.3 * cm, 3.3 * cm]))
    s.append(Paragraph("<b>Lectura.</b> Con los mismos datos de entrenamiento, tu método rinde como Brun y claramente "
                       "mejor que QR y el perfil de verosimilitud, con las tres familias de verdades. El 28/28 en "
                       "admisibilidad se debe a que tu método verifica sobre las mismas salidas en que se le evalúa; el "
                       "mensaje del paper debe ser que la contribución es esa verificación, no la ordenación por "
                       "sensibilidad (que comparte con Brun y con los métodos de ortogonalización).", P))

    s.append(Paragraph("<b>Identificabilidad.</b> Perfiles originales: 65 de 74 parámetros identificables. Perfiles "
                       "densos: 65 de 74 (un solo cambio de categoría, Fujita reaction_6_k1, que sigue sin ser "
                       "identificable). Subconjuntos elegidos con entrenamiento: 35 de 43. Hipótesis del teorema de "
                       "Lean en toda la región alrededor del óptimo:", P))
    rows = [["Región (factor alrededor del óptimo)", "Parámetros que cumplen las hipótesis"]]
    for r, fn in [("10 (todo el rango)", ""), ("5", "_r5"), ("3", "_r3"), ("2", "_r2"), ("1,5", "_r1.5")]:
        d = list(csv.DictReader(open(O.ST / "identifiability" / f"certificado_box{fn}_parametros.csv", encoding="utf-8")))
        rows.append([r, f"{sum(x['pf'] == 'True' for x in d)} de {len(d)}"])
    s.append(T(rows, [8 * cm, 8 * cm]))
    s.append(Paragraph("Con el teorema de Lean, la identificabilidad solo se respalda cerca del óptimo; en todo el rango "
                       "del estudio la evidencia son los perfiles numéricos. Es una comprobación numérica de las "
                       "hipótesis (muestreo y búsqueda del peor caso), no un certificado.", P))
    s.append(Paragraph("<b>Condicionamiento.</b> Con columnas de longitud 1 sin centrar, 30 de los 31 subconjuntos cumplen "
                       "κ ≤ 10 y VIF ≤ 10; Rahman no (κ = 12,4; VIF = 39), así que el teorema de estabilidad de mínimos "
                       "cuadrados no se aplica a ese subconjunto.", P))

    s.append(Paragraph("3. Verificación de las demostraciones en Lean 4", H2))
    s.append(T([
        ["Comprobación", "Resultado"],
        ["Compilación desde cero en una copia limpia (32 módulos de teoría, testigos y 28 modelos)", "2.658 tareas sin errores, 18 min"],
        ["Búsqueda de sorry y axiom en las fuentes", "ninguno"],
        ["Axiomas de los teoremas (CheckAxioms)", "309 de 309, solo propext, Classical.choice y Quot.sound"],
        ["Axiomas del teorema final de cada modelo", "28 de 28, solo los estándar"],
        ["lean4checker (segundo verificador independiente)", "todos los módulos aceptados: 32 de teoría, NonVacuity y 46 de modelos"],
        ["Control negativo: teorema falso con sorry", "detectado (sorryAx)"],
        ["Testigos de no vacuidad (NonVacuity.lean)", "las hipótesis de los teoremas centrales se pueden cumplir; ejemplo no lineal para identificabilidad"],
        ["Auditoría de definiciones (DEFINITIONS_AUDIT.md)", "ningún teorema falso; diferencias de definición documentadas"],
    ], [9 * cm, 7.5 * cm]))
    s.append(Paragraph("Además se corrigieron dos errores del script verify.sh: la comprobación de axiomas de los modelos "
                       "fallaba en silencio (AllModels no se compilaba) y la búsqueda de sorry fallaba al ejecutarlo dos "
                       "veces (revisaba Mathlib). Ahora el script se detiene con error si algo no queda verificado.", P))

    s.append(Paragraph("4. Índice de sistemas", H2))
    rows = [["Carpeta", "Admisible (paper)", "A5 igual", "A1 admisible", "Parámetros identificables"]]
    for i, n in enumerate(O.problems, 1):
        o = orig[n] or {}
        d5 = O.L(O.ST / "selection_fixedscen" / f"{n}.json") or {}
        d1 = O.L(O.ST / "selection_train_fixedscen" / f"{n}.json") or {}
        po = O.L(O.REPO / "identifiability" / "profiles" / f"{n}.json")
        idt = f"{po['n_identificables']}/{len(po['perfiles'])}" if po else "—"
        rows.append([f"{i:02d}_{n}", O.yesno(o.get("admisible")), O.yesno(set(d5.get("S", [])) == set(o.get("S", []))),
                     O.yesno(d1.get("admisible")), idt])
    s.append(T(rows, [7 * cm, 2.6 * cm, 2 * cm, 2.4 * cm, 3 * cm]))
    s.append(Paragraph("Subcarpetas de 00_General: registros_servidor (registros de cada cálculo, sin avisos del "
                       "integrador), resultados_globales, verificacion_Lean y scripts.", SM))
    SimpleDocTemplate(str(G / "00_Resumen_general.pdf"), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                      topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                      title="Segunda auditoría: resumen del servidor").build(s)


if __name__ == "__main__":
    main()
    print("ok")
