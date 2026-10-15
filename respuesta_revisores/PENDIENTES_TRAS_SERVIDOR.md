# Pendientes del paper tras el recálculo del servidor (15-10-2026)

Corrección del recorte `max(θ₀(1+εu), 1e-12)` de los escenarios: cambian Armistead, Raimundez y Lang.

## Estado de las selecciones
- Armistead: {k_d, k00} (antes {k_d, alpha_cer}); admisible. Análisis rehechos y verificados en el servidor.
- Raimundez: {kdeg_membran__MKN1, ka_MAPK__MKN1}; admisible. Análisis en el servidor.
- Lang: 13 parámetros, **no admisible** (e_fit 0.564). Sus resultados posteriores se movieron a `_antes_negfix/`.

## Qué hay que actualizar cuando lleguen los resultados
1. Traer del servidor `certificados/resultados/` (sin las cachés de Lang mezcladas: usar las de la laptop).
2. Paquete de reproducibilidad: copiar selecciones y resultados nuevos a `reproducibility/results/`
   (selection, robustness, external_validation, nested_validation, synthetic_seeds, criteria_tests,
   identifiability, single_parameter, …) y regenerar figuras y tablas (`make_figures.py`,
   `make_robustness_note.py`, `comparison_suppl_figures.py`, `tablas_suplemento.py`,
   `identificabilidad_tabla.py`, `recuento_parametros.py`).
3. `error_absoluto.py` para Raimundez (y quitar `ABS_EXCLUIR`), luego `--tabla`.
4. Recuentos del texto que cambian con Lang no admisible: 32 → 31 admisibles, 29/29 y 28/28 de
   la admisibilidad comparada, 26/29 de la validación, identificabilidad 26 de 32 (67 de 76),
   patrones (27 A), 340/250/590 del sintético, 187/340 y 159/282, Tabla 1, Fig. 2–5, resúmenes
   por sistema de Armistead, Raimundez y Lang, Tabla S16 de QR (Armistead pasa a 1 en común).
5. Frase de Bachmann/Chen/Lang/Raimundez sin ajuste completo en el sintético (main, Methods):
   si Lang deja de ser admisible, quedan Chen y Raimundez.
6. B5 (`resultados/patrones_indep/`) y C3 (`sintetico_senal_a*/`, `sintetico_semillas_a005/`,
   `sintetico_semillas_a050/`): redactar resultados en la nota de robustez y en la del sintético.

## Ya hecho en esta sesión (sin depender del servidor)
- C7: frase "rather than simulation errors" matizada; discrepancias del simulador en unidades de σ.
- C4: diferencias de implementación entre criterios; perfiles no convergidos y puntos fallidos.
- C1: umbral como decisión de diseño; error en unidades de σ (Tabla `tab:abs`).
- C11: tratamiento de valores nulos/negativos y columnas nulas; tabla de recuentos incluida.
- E2: patrón B (definición = código), Chen 7–13/8–13, Isensee 7.6/9.8, Bachmann en el sintético,
  640/590, solapamientos de QR.
- Figuras: Fig. 5 más grande (generador con letra mayor); Fig. S9 con marcadores y líneas.
