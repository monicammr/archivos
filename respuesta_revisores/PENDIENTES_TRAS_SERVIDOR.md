# Recálculo tras corregir los escenarios (15-10-2026) — HECHO

Corrección del recorte `max(θ₀(1+εu), 1e-12)` de los escenarios: cambian Armistead, Raimundez y Lang.

## Resultado
- Armistead: {k_d, k00} (antes {k_d, alpha_cer}); admisible, e_fit 33 %, patrón B.
- Raimundez: {kdeg_membran__MKN1, ka_MAPK__MKN1}; admisible, e_fit 18.7 % (antes 37.2 %, cos Δ −0.30 → 0.79).
  Con este subconjunto QR, Brun y Morris también son admisibles (Brun elige el mismo par).
- Lang: 13 parámetros, **no admisible** (e_fit de primer orden 0.564). Comprobado con el protocolo del
  artículo (RECL_AJUSTE_LINEAL=1, `reclasificacion_salidas_bio_poda_lin_srv`): mismo resultado.
- 31 de 34 problemas admisibles (antes 32).

## Hecho
- Resultados del servidor traídos a `certificados/resultados/` (espejo exacto, sin cachés) y sincronizados
  con el paquete (`certificados/sincroniza_paquete.py --aplica`; copias anteriores en
  `reproducibility/results/_before_negative_fix/`).
- Tablas y figuras regeneradas (certificados y `reproducibility/figures_tables`); cifras del texto
  comprobadas con `reproducibility/figures_tables/cifras_texto.py`.
- B5: robustez con direcciones independientes (`patrones_indep`, paquete `robustness_independent`).
- C3: señal y(θ*)−y(θ₀) en unidades de σ y amplitudes ±5 %/±50 % (`sintetico_senal_a*`,
  `sintetico_semillas_a005/a050`).
- Error en unidades de σ para los 31 problemas (`error_absoluto`).

## Errores de código encontrados y corregidos durante el recálculo
- Puntos de control que sólo comprobaban el tamaño del subconjunto (validación externa y anidada, QR,
  aleatorios, sólo calibración): al cambiar S hay que borrar resultados y puntos de control.
- `stage_reclass.py`: con p > 200 (Lang) las variantes RECL_TAG compartían cachés (corregido con CTAG).
- `VAL_PMAX` por defecto 60: Raimundez necesita 200 para ajustar el modelo completo.
- `control_admis_sint.py` debe correr después de QR/Brun/Morris (necesita sus selecciones).

## Pendiente de la usuaria
- Declaración de ética (comité del estudio SCT o justificación de la exención).
- Confirmar las referencias 16 y 17.
- Variantes de ajustes de Lang/Raimundez (información extra, no entran en el artículo): siguen en el
  servidor; traerlas sólo si se quieren.
