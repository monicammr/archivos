# Certificado Lean 4: reducción de parámetros en sistemas de EDOs

Verificado con Lean 4.23.0 y Mathlib `v4.23.0`. Ningún archivo usa `sorry` ni axiomas propios:
`#print axioms` devuelve solo `[propext, Classical.choice, Quot.sound]`.

```
lake exe cache get   # descarga Mathlib precompilado
lake build            # teoría
lake build Models     # los modelos (Chen ~10 min; Froehlich necesita > 14 GB de RAM)
```

## Teorema principal

`CertifiedODEReduction.certified_parameter_reduction` (`CertifiedODEReduction.lean`)

Sea `ẋ = f(x, θ)` con `f` de clase C¹ en un abierto `U ⊆ ℝⁿ × ℝᵖ` que contiene la trayectoria
nominal, y supongamos que para `θ` cerca de `θ₀` las soluciones `x(θ, ·)` existen en `[0, T]`
con dato inicial `x(θ, 0) = x₀(θ)`, con `x₀` diferenciable en `θ₀` (derivada `D₀`).
Sean `t_1, …, t_N ∈ [0, T]` los instantes de muestreo. Entonces existe la sensibilidad `S(t)`
(solución de la ecuación variacional `S' = ∂ₓf·S + ∂_θf`, `S(0) = D₀`) tal que, con `J` la matriz de sensibilidad
muestreada (`J_{(k,i),j} = (S(t_k) e_j)_i`), para todo conjunto `S` de parámetros conservados con
`R_var(S) ≥ r` y todo `η > 0`, si `Δθ` es suficientemente pequeño:

    ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ (√((1−r)·tr(JᵀJ)) + η) · ‖Δθ‖

donde `F` es la trayectoria muestreada y `F(θ₀+Δθ_S)` la del modelo reducido (parámetros
descartados fijados en su valor nominal).

## Archivos

| Archivo | Contenido |
|---|---|
| `FirstOrderErrorBound.lean` | Cota algebraica: ‖JΔθ − J_SΔθ_S‖² ≤ R(S)·‖Δθ_{Sᶜ}‖²; forma con `R_var` |
| `TrajectoryErrorBound.lean` | Si `F` es diferenciable con Jacobiano `J`: ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ √R(S)‖Δθ_{Sᶜ}‖ + o(‖Δθ‖) |
| `GlobalLipschitzODE.lean` | Existencia global en `[a,b]` para EDOs con campo globalmente Lipschitz (pegando Picard–Lindelöf) |
| `ParamDiffODE.lean` | **Dependencia diferenciable respecto a parámetros** (`hasFDerivAt_solution_param_init`; corolarios `_on` y global): θ ↦ x(θ,t) es diferenciable y su derivada resuelve la ecuación variacional. Usa Grönwall (Mathlib), linealización uniforme en compactos e inducción continua |
| `CertifiedODEReduction.lean` | Une todo en el teorema principal |
| `IdentifiabilityConditioning.lean` | **κ y VIF ⇒ identificabilidad (sección 2.2).** Ecuaciones normales; con columnas L2-normalizadas y κ(Z) ≤ κ, dos ajustes por mínimos cuadrados cumplen ‖D(θ̂ − θ̂')‖ ≤ κ‖y − y'‖ (unicidad y estabilidad); si VIF_j = ((ZᵀZ)⁻¹)_jj ≤ V, el parámetro j cumple \|Δv_j\| ≤ √V‖Δy‖ |
| `CosineCertificate.lean` | cos Δ ≥ c a partir del error relativo; cota explícita (no asintótica) para perturbaciones finitas con derivada Lipschitz; certificado de cos Δ por escenario |
| `NumericalRobustness.lean` | Error de diferencias finitas; R_var, κ y VIF certificados a partir de cantidades calculadas con margen de error |
| `SensitivityLipschitz.lean` | Cota formal de `Lc`: trayectorias y sensibilidades Lipschitz en θ (Grönwall), con constantes explícitas en `M₁`, `M₂`, `T` |
| `CertifiedFiniteODE.lean` | Certificado de cos Δ para la EDO con `Lc = √N·M₂e²(e−1)/M₁`, `e = exp(M₁T)` |
| `PatternMechanisms.lean` | Mecanismos de los patrones D (efectos opuestos ⇒ no identificabilidad) y A (energía nula ⇒ reducción exacta) |
| `ExactLinearCertificate.lean` | **(A1)** Certificado de cos Δ con el error lineal exacto ‖J(h − h_S)‖ en lugar de √R‖h_{Sᶜ}‖ (finito y para la EDO). **(A2)** Límite: cos Δ(s·h) → cos(Jh, J h_S) cuando s → 0⁺; si el coseno lineal supera c, cos Δ > c para perturbaciones pequeñas, **sin Lc** |
| `SpectralConditioning.lean` | **(A3)** Teorema espectral para ZᵀZ: ‖Zu‖² = Σλᵢcᵢ², ‖Z‖ = √λ_max, √λ_min es la mejor σ_min; κ = √(λ_max/λ_min) (= `numpy.linalg.cond`). VIF_j = ((MᵀM)⁻¹)_jj con `Matrix.inv` |
| `LocalExistence.lean` | **(A4)** Si la solución nominal existe en [0,T], las soluciones existen para θ cerca de θ₀ (truncamiento + Grönwall); se elimina la hipótesis de existencia del teorema de diferenciabilidad |
| `NominalCertificate.lean` | Encadena A4 + diferenciabilidad + A2: certificado local de cos Δ con hipótesis mínimas (solo f C¹ y la trayectoria nominal) |
| `KineticRegularity.lean` | **Hipótesis 1 demostrada para modelos cinéticos.** Lenguaje `KExpr` de leyes de velocidad (constantes, concentraciones, parámetros, +, −, ×, /, potencias enteras y reales, exp): todo modelo así es C^∞ en el abierto donde los denominadores no se anulan. Michaelis–Menten y Hill están bien definidas con K > 0 y concentraciones ≥ 0; acción de masas pura: dominio = todo el espacio. Versiones cinéticas de la diferenciabilidad y del certificado local de cos Δ |
| `EventSystems.lean` | **Hipótesis 2: eventos en tiempos fijos** (Smith_BMCSystBiol2013). Tramos con campos C¹ y mapas de reinicio diferenciables: las soluciones existen cerca de θ₀ y la trayectoria es diferenciable en θ₀ en todos los tramos |
| `PositivityInvariance.lean` | **Positividad.** Si el modelo es cuasi-positivo (una especie con concentración 0 no puede consumirse) y C¹, las concentraciones que empiezan ≥ 0 siguen ≥ 0 (Grönwall sobre Σ min(xᵢ,0)² + inducción continua). Para modelos cinéticos cuyo dominio contiene el ortante ≥ 0 (MM y Hill con K > 0), la trayectoria queda en el dominio automáticamente. Ejemplo verificado: producción + degradación de Michaelis–Menten |
| `KineticCheck.lean` | **Comprobación automática de modelos.** Comprobadores booleanos sobre `KExpr` (signo ≥ 0 / > 0, dominio ⊇ ortante, cuasi-positividad), con prueba de corrección. Si `checkModel pos F = true` (Lean lo calcula), `checked_model_hasFDerivAt` da positividad, permanencia en el dominio, existencia y diferenciabilidad; `checked_segments_hasFDerivAt` para entradas por escalones en tiempos fijos |
| `Models/*.lean` | **Los modelos del artículo**, generados de SBML por `certificados/sbml_to_lean.py`. 15 verificados (`check`, `diff`); en 6 Lean demuestra que la comprobación falla (`check_falla`). Ver `certificados/resultados/sbml_lean/tabla.md` |
| `GreedySelection.lean` | **Algoritmo greedy (sección 2.3).** El subconjunto devuelto siempre cumple κ ≤ κ₀ y VIF ≤ V; está formado por candidatos; y todo parámetro descartado seguiría violando el filtro con el conjunto final (justifica el descarte permanente, porque κ y VIF son antimonótonos) |

## Qué afirmación del artículo respalda cada teorema

| Afirmación del artículo | Teorema Lean |
|---|---|
| E_j = (JᵀJ)_jj; R_var = energía conservada / tr(JᵀJ) | `FirstOrderErrorBound.total_eq_kept_add_removed` |
| J es la derivada de la trayectoria y resuelve la ecuación variacional | `ODEParamDiff.hasFDerivAt_solution_param_init` |
| R_var(S) ≥ r ⇒ fijar los parámetros descartados preserva la trayectoria (local) | `CertifiedODEReduction.certified_parameter_reduction` |
| κ ≤ 10 ⇒ ecuaciones normales bien condicionadas, estimación única y estable | `Identifiability.ls_param_kappa_stability`, `Identifiability.ls_unique` |
| VIF ≤ 10 ⇒ cada parámetro conservado es identificable individualmente | `Identifiability.ls_vif_inverse_stability` |
| El algoritmo greedy devuelve un subconjunto que cumple κ/VIF; el descarte permanente es correcto | `GreedySelection.greedy_kappa_vif_guarantee` |
| Perturbaciones finitas: cota explícita del error de trayectoria | `CosineCertificate.finite_trajectory_error` |
| cos Δ ≥ c para un escenario concreto (certificado verificable por escenario) | `CosineCertificate.finite_cos_certificate` |
| **Lc acotado formalmente**: la sensibilidad es Lipschitz en θ con constante explícita M₂e²(e−1)/M₁ | `SensitivityLipschitz.sens_lipschitz` (y `traj_lipschitz`, `sens_bound`) |
| **cos Δ ≥ c para la EDO, con Lc = √N·M₂e²(e−1)/M₁** (sin suponer Lc) | `CertifiedFiniteODE.certified_cos_ode` |
| Diferencias finitas aproximan J con error ≤ Lc·δ | `NumericalRobustness.fd_column_error` |
| La comprobación de R_var sobre J̃ (con margen) implica R_var(J) ≥ r | `NumericalRobustness.rvar_certified_from_approx` |
| Las comprobaciones de κ y VIF sobre Z̃ (con margen) implican κ ≤ κ₀ y VIF ≤ V₀ para Z | `NumericalRobustness.kappa_certified_from_approx`, `vif_certified_from_approx` |
| Patrón D: efectos opuestos ⇒ κ rechaza y no hay identificabilidad | `PatternMechanisms.not_okKappa_of_kernel`, `ls_not_unique_of_kernel`, `opposing_pair_kernel` |
| Patrón A: energía descartada nula ⇒ reducción exacta a primer orden | `PatternMechanisms.exact_reduction_of_zero_energy` |
| Cota finita con el término lineal exacto ‖J h_{Sᶜ}‖ (nunca peor que la de R_var) | `ExactLinearCertificate.finite_trajectory_error_exact`, `finite_cos_certificate_exact`, `certified_cos_ode_exact` |
| **cos Δ ≈ coseno lineal para perturbaciones pequeñas** (justifica comparar cos Δ con la predicción de J) | `ExactLinearCertificate.tendsto_cos_delta`, `eventually_cos_delta_gt`, `local_cos_ode` |
| κ calculado con la SVD (σ_max/σ_min) da la estabilidad de mínimos cuadrados | `SpectralConditioning.ls_kappa_stability_spectral`, `opNorm_eq_sqrt_lamMax`, `le_sqrt_lamMin` |
| VIF calculado como diag((ZᵀZ)⁻¹) da la estabilidad por parámetro | `SpectralConditioning.ls_vif_matrix_stability`, `vif_matrix_inverse` |
| Basta integrar la trayectoria nominal: las soluciones perturbadas existen y son diferenciables en θ | `LocalExistence.exists_solutions_near`, `hasFDerivAt_of_nominal_solution` |
| Certificado local de cos Δ con hipótesis mínimas | `NominalCertificate.local_cos_from_nominal` |
| Los modelos (acción de masas, Michaelis–Menten, Hill) cumplen la regularidad C¹ | `KineticRegularity.contDiffOn_field`, `ok_mm`, `ok_hill`, `ok_hillR`, `domain_eq_univ` |
| La metodología vale con la única condición de que ningún denominador se anule sobre la trayectoria nominal | `KineticRegularity.kinetic_hasFDerivAt`, `kinetic_local_cos` |
| Sistemas con eventos en tiempos fijos (Smith) | `EventSystems.event_hasFDerivAt` |
| Las concentraciones permanecen ≥ 0 (modelos cuasi-positivos) | `PositivityInvariance.nonneg_of_quasiPositive`, `kinetic_nonneg` |
| Diferenciabilidad para modelos cinéticos con solo: dominio ⊇ ortante ≥ 0, cuasi-positividad y dato inicial ≥ 0 | `PositivityInvariance.kinetic_hasFDerivAt_of_nonneg` |
| **Cada modelo concreto** (15 de 22) cumple las hipótesis: C¹, dominio ⊇ ortante, cuasi-positivo | `Models.<Sistema>.check`, `Models.<Sistema>.diff` |

Lo que **no** está formalizado (y sigue siendo evidencia numérica en el artículo):
* los valores concretos de cada modelo (cos Δ por escenario, tasa de admisibilidad 89 %), que
  requerirían integración de EDOs verificada (aritmética de intervalos);
* las cotas `M₁`, `M₂` de las derivadas de `f` en la región `K` y que las trayectorias permanecen
  en `K` (hipótesis del certificado, calculables para cada modelo), y la cota `τ` del error numérico;
* la clasificación empírica de los 36 sistemas en patrones A–D (sí están demostrados los mecanismos).

No se formalizó (por decisión): la variante de Grönwall con norma logarítmica `μ` (mejoraría
`Lc` de `exp(M₁T)` a `exp(μT)`, pero los cálculos muestran que tampoco bastaría: ver
`../certificados/README.md`).

## Hipótesis que permanecen (explícitas en el enunciado)

1. `f` es C¹ en un abierto que contiene la trayectoria nominal — **demostrado** para todo modelo
   escrito con `KExpr` (`KineticRegularity`); que la trayectoria no anule ningún denominador es
   **automático** si el dominio contiene el ortante ≥ 0 (MM/Hill con K > 0), el modelo es
   cuasi-positivo y el dato inicial es ≥ 0 (`PositivityInvariance`).
   La traducción SBML → `KExpr` es automática (`certificados/sbml_to_lean.py`) y Lean verifica
   las condiciones en 15 de los 22 modelos (`Models/`). La fidelidad del traductor (que el
   `KExpr` generado es el mismo modelo que integra roadrunner) no está demostrada en Lean.
1b. Eventos: **demostrado** para eventos en tiempos fijos (`EventSystems`); no cubre eventos
   disparados por el estado (umbrales).
2. ~~Las soluciones existen en `[0, T]` para `θ` en un entorno de `θ₀`~~ — **ya demostrado**
   (`LocalExistence`): basta la trayectoria nominal. Sigue siendo hipótesis en
   `certified_cos_ode` (versión finita), que necesita las soluciones en toda la bola `B(θ₀, ρ₀)`.
3. El dato inicial `x₀(θ)` es diferenciable en `θ₀` (si no depende de `θ`, `D₀ = 0`).
4. El teorema principal es local (`Δθ → 0`). La versión finita (`certified_cos_ode(_exact)`)
   da cotas numéricas, pero con `Lc` enorme en modelos rígidos; la versión local
   (`local_cos_from_nominal`) no necesita `Lc` pero no dice hasta qué tamaño de perturbación vale.
5. `J` es la sensibilidad exacta; la calculada por diferencias finitas es una aproximación.
