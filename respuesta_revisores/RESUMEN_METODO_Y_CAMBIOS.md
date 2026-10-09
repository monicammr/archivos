# Resumen: método final y qué cambiar en el paper

## 1. El método final, paso a paso

| Paso | Qué se hace | Valor usado |
|---|---|---|
| **0. Datos** | Se usan las **mediciones reales** de PEtab: cada observable, en su condición experimental y en sus tiempos, en la escala de los datos (lin/log/log10) y dividida por su ruido σ | — |
| **1. Separar parámetros** | **Biológicos** (del modelo SBML) y **de calibración** (escalas, offsets). Sólo se eligen biológicos; los de calibración se reajustan siempre | — |
| **2. Sensibilidades** | Matriz **J** relativa (∂y/∂log θ) por diferencias centradas | δ = 1 % |
| **3. Etapa 1** | Ordenar por energía E_j y elegir con el **algoritmo voraz** (aceptar si κ y VIF ≤ umbral; descartar para siempre si no) hasta R_var ≥ τ_R | τ_R = 0,89; κ, VIF ≤ 10 |
| **4. ¿Admisible?** | Reajustar el subconjunto (+ calibración) y medir **e_ajuste** en 15 escenarios a ±5 %. Admisible si \|S\| ≥ 2 y e_ajuste ≤ τ_e | τ_e = 0,436 (⇔ cos Δ ≥ 0,9) |
| **5. Etapa 2** | Si la Etapa 1 no es admisible: ordenar por efecto real s_j y repetir el voraz hasta que sea admisible | — |
| **6. Poda** | Quitar los parámetros que sobran mientras siga siendo admisible → **mínimo por inclusión** | — |
| **7. Validación** | Predecir experimentos **no usados**; datos reales y simulados con ruido | — |

En sistemas grandes (Chen, Lang, Bachmann…), e_ajuste se calcula linealizado (primer orden).

## 2. Lo que conseguimos

| | Resultado |
|---|---|
| Admisibles | **32 de 34** sistemas PEtab (fallan Crauste y Beer) |
| Tamaño típico | **2 parámetros biológicos** (+ los de calibración de cada sistema) |
| Validación externa con datos reales | el reducido predice **igual o mejor** que el completo en **22 de 25** |
| Validación con ruido simulado | señal > ruido: 8 de 13 dentro del umbral; señal < ruido: 13 de 15 al nivel del ruido |
| Robustez (δ, tolerancias, ±1/±5/±10 %, umbrales) | casi ningún cambio en los parámetros elegidos |
| ¿Basta 1 solo parámetro? | con ±5 % a veces sí, pero es **frágil** (peor con ±10 % y al predecir) → justifica \|S\| ≥ 2 |
| Costo | lineal en p (2p simulaciones para J); Froehlich con 4 231 parámetros: 2,6 h en 4 núcleos |
| Lean 4 | todos los pasos del método respaldados (ver tabla en lean/README.md) |

Excluidos: Froehlich (9 169 condiciones), SCT Bandura (no es PEtab).

## 3. Qué cambiar en cada parte del paper

| Parte del paper | Qué cambiar | Revisor |
|---|---|---|
| **Título** | Quitar "minimal" y "certified" sin matices. Ej.: "…to a compact, non-redundant subset of biological parameters…" | R4 (1, 9) |
| **Resumen** | Nuevo método (mediciones, e_ajuste, poda), nuevos números (32/34, 2 parámetros, 22/25) | R4, R3 |
| **Introducción** | Casi igual; añadir que se trabaja con datos medidos y ruidosos | R3 |
| **Sec. 2 (método)** | Reescribir con el método de la sección 1; **tabla de notación**; símbolos genéricos (τ_R, τ_κ, τ_e, δ) y valores en "Experimental setup"; quitar ρ y el teorema inexistente | R2 (1, 2, 3), R4 (2, 3, 4) |
| **Supuestos** | Lista explícita (EDO suave, θ₀ buen ajuste, análisis local, ruido gaussiano con σ, calibración siempre estimada) | R3 |
| **Sec. Lean** | Teoremas como "Teorema 1, 2…" en matemáticas; nombres de Lean en una tabla del apéndice; decir qué NO se demuestra (validez lejos de θ₀) | R2 (2), R4, R3 |
| **Resultados** | Nueva Tabla 1 (= Tabla A), nueva Figura 2 (cos Δ, e_rel, e_ajuste); validación externa; robustez y umbrales (Tablas C); costo (Tabla B) | R4 (5, 6), R2 (4, 5) |
| **Discusión / limitaciones** | Validez local; Crauste y Beer; exclusiones; linealización en los grandes; muchos parámetros de calibración en Bachmann/Raimundez; σ del benchmark | R3, R4 (10) |
| **Conclusiones** | Mensaje nuevo: "reduce a pocos parámetros biológicos, predice condiciones nuevas igual o mejor que el completo, con garantías formales locales" | R4 |
| **Reproducibilidad** | Ejemplo trabajado + depósito en Zenodo | R4 (7) |
| **Carta de respuesta** | Comentario por comentario: qué se hizo y dónde está | todos |

## 4. Archivos con todo listo

* Tablas en inglés: `respuesta_revisores/tables_en.md`
* Notación en inglés: `respuesta_revisores/notacion.md`
* Pruebas de Lean: `lean/README.md`
