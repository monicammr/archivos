# Evaluación del certificado formal de cos Δ en los 24 sistemas admisibles

Scripts: `certify_systems.py` (22 sistemas PEtab) y `certify_sct.py` (SCT Bandura).
Resultados: `resultados/tabla_certificados.csv` / `.md` y un JSON por sistema.
Froehlich_CellSystems2018 no se calculó (4231 parámetros, 1229 estados: ~8 h solo para J).

## Qué se calcula

Para cada sistema, con los subconjuntos de `04_robustez/robustez_sweep_*.py` (y SCT con
{beta43, beta54, beta34, beta14, gamma33}, que reproduce cos Δ = 0,987):

* `J` = ∂F/∂θ en θ₀ (diferencias centradas), `R(S)` y `R_var` (absoluto y relativo);
* los escenarios del artículo (semilla 42, 15 por nivel, θ = θ₀(1 + nivel·d));
* cotas **inferiores** de `M₁ = sup‖Df‖`, `M₂ = Lip(Df)` y de la norma logarítmica `μ`,
  evaluadas en las trayectorias nominal y perturbadas;
* `Lc` en tres variantes:
  * **actual** (teorema `certified_cos_ode` de Lean): `Lc = √N·M₂·e²(e−1)/M₁`, `e = exp(M₁T)`;
  * relativa (θ = θ₀(1+u)), mismo teorema;
  * relativa con norma logarítmica (requeriría extender el teorema en Lean);
* la condición del certificado con c = 0,9 en cada escenario.

Como las cotas usadas son **inferiores** y `Lc` es creciente en ellas, si la condición falla con
estos valores, falla también con los verdaderos.

## Resultado

**El certificado no se cumple en ningún escenario de ningún sistema**, ni al ±1 % ni al ±5 %,
en ninguna de las tres variantes. `log10 Lc` va de ~12 (SCT, variante μ) a ~10⁹ (Elowitz);
la única excepción numérica es SalazarCavazos (`Lc ≈ 10⁻²·⁵`), pero con T = 0,01 la respuesta
es diminuta y el certificado solo alcanzaría perturbaciones de ~0,0007 %.

Causa: la cota de Grönwall crece como `exp(M₁T)` (o `exp(μT)`); los modelos son rígidos y
`M₁T`, `μT` son grandes. Además, la cota de primer orden `√R‖h_{Sᶜ}‖` (Cauchy–Schwarz) es
mucho más pesimista que el error real: incluso en el límite de perturbaciones infinitesimales
no garantiza cos Δ ≥ 0,9 en la mayoría de los escenarios.

## Otros hallazgos (afectan a la Tabla 1 del artículo)

* Con el propio código del pipeline (`sensitivity_jacobian` de `petab_V9_todos35.py`), varios
  subconjuntos **no reproducen el R_var de la Tabla 1** (p. ej. Sneyd {k1,k2}: ~0 % frente a
  99,5 %; Elowitz: 0,03–1 % frente a 99,4 %; Crauste: 1,9–23,5 % frente a 96,6 %). Los modelos
  no cambiaron en el benchmark desde mayo de 2026 (salvo Bachmann).
* `02_sct_bandura/sct_fim_greedy.py` no se ejecuta tal cual (usa `VIF_MAX2` antes de definirlo).
  Corregido, selecciona 4 parámetros con cos Δ = 0,63; con gamma33 (5 parámetros) se obtiene
  cos Δ = 0,987, como en el artículo.
* Los cos Δ simulados al ±5 % coinciden en general con la Tabla 1.

## Certificado con el término lineal exacto y certificado local (sección A)

`resultados/tabla_local.md` (generada a partir de los JSON) añade, con los mismos escenarios:

* **1er orden exacto**: la condición lineal con `‖J h_{Sᶜ}‖` (Lean:
  `finite_cos_certificate_exact`) en lugar de `√R ‖h_{Sᶜ}‖`. Es mucho menos pesimista
  (p. ej. Armistead 15/15 frente a 0/15 al ±5 %), pero el **certificado finito sigue fallando en
  todos los escenarios**, porque el término `2 Lc ‖h‖²` domina.
* **Coseno lineal** `cos(J h, J h_S)` (Lean: `tendsto_cos_delta`). Su mediana al ±5 % coincide
  con el cos Δ simulado en 20 de los 21 sistemas que lo tienen (diferencia ≤ 0,015;
  SalazarCavazos no tiene cos Δ simulado), lo que confirma numéricamente
  que la linealización describe bien el cos Δ del artículo. Si el coseno lineal supera 0,9, el
  teorema `eventually_cos_delta_gt` garantiza cos Δ > 0,9 **para perturbaciones suficientemente
  pequeñas en esa dirección**, pero no dice que ±5 % sea "suficientemente pequeño".
* Excepción: **Lang_PLOSComputBiol2024** (coseno lineal 0,006 frente a cos Δ simulado 0,982;
  R_var ≈ 0). La respuesta de Lang al ±5 % no es lineal, o la J por diferencias finitas
  no es fiable en este modelo (124 estados, 294 parámetros). Conviene revisarlo antes de citar
  su fila de la Tabla 1.
