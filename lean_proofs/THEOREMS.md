# Catálogo de demostraciones formales (Lean 4 + Mathlib)

Generado por `catalogo.py`. Todas las demostraciones compilan sin `sorry` ni axiomas propios.

**Módulos de teoría:** 31; **teoremas y lemas:** 289. **Modelos del benchmark verificados:** 22.

## Resumen por módulo

| Módulo | Teoremas y lemas | Contenido |
|---|---|---|
| `CertifiedFiniteODE` | 5 | Certificado de cos Δ para la EDO, con `Lc` acotado formalmente |
| `CertifiedODEReduction` | 1 | Certificado completo: de la EDO al error de trayectoria del modelo reducido |
| `CosineCertificate` | 5 | cos Δ y perturbaciones finitas: certificados no asintóticos |
| `EventSystems` | 1 | Hipótesis 2: sistemas con eventos en tiempos fijos |
| `ExactLinearCertificate` | 13 | Certificados de cos Δ con el error lineal exacto y versión local (sin `Lc`) |
| `FirstOrderErrorBound` | 12 | Cota de error de primer orden al fijar parámetros descartados |
| `GlobalExistence` | 11 | Existencia global de la solución nominal (condición C4) |
| `GlobalLipschitzODE` | 3 | Existencia global en `[a, b]` para EDOs con campo globalmente Lipschitz |
| `GreedySelection` | 7 | El algoritmo greedy de selección (sección 2.3) y sus garantías |
| `IdentifiabilityConditioning` | 10 | κ y VIF ⇒ estimación por mínimos cuadrados única y estable |
| `IntervalInit` | 5 | Condiciones iniciales θ-dependientes evaluadas por intervalos racionales |
| `KineticCheck` | 19 | Comprobación automática de modelos cinéticos (SBML → `KExpr` → Lean) |
| `KineticNetwork` | 18 | Redes de reacciones: comprobación completa, incluida la existencia global (C4) |
| `KineticRegularity` | 11 | Hipótesis 1: los modelos cinéticos son C¹ (lenguaje de leyes de velocidad) |
| `LinearizedFit` | 3 | e_ajuste linealizado (sistemas grandes) y su relación con el e_ajuste real |
| `LocalExistence` | 9 | Existencia de soluciones para parámetros cercanos (se elimina la hipótesis `hsol`) |
| `NominalCertificate` | 1 | Certificado local de cos Δ a partir sólo de la trayectoria nominal |
| `NumericalRobustness` | 6 | Robustez numérica: del cálculo aproximado a las hipótesis exactas |
| `OutputComposition` | 4 | De los estados a las salidas medidas: y_i = h(g_i(x(t_i), θ)) / σ_i |
| `ParamDiffODE` | 8 | Dependencia diferenciable de las soluciones de una EDO respecto a los parámetros |
| `PatternMechanisms` | 4 | Mecanismos detrás de los patrones de robustez (sección 3.2) |
| `Poda` | 2 | Poda (eliminación hacia atrás): el subconjunto final es mínimo por inclusión |
| `PositivityInvariance` | 15 | Positividad: las concentraciones que empiezan `≥ 0` siguen `≥ 0` |
| `RefitMonotone` | 5 | Reajustar más parámetros nunca empeora el error (e_ajuste monótono) |
| `RiccatiNetwork` | 9 | Existencia en un horizonte finito con crecimiento cuadrático (cota de Riccati) |
| `ScaledError` | 5 | cos Δ = error mínimo tras reajustar el tamaño de la respuesta |
| `SensitivityLipschitz` | 8 | Cota formal de la constante de Lipschitz de la sensibilidad (`Lc`) |
| `SpectralConditioning` | 22 | κ y VIF tal como se calculan numéricamente (teorema espectral y matriz inversa) |
| `StrictExistence` | 12 | Existencia global con positividad estricta |
| `StrictNetwork` | 46 | Redes con positividad estricta: comprobación completa sin condiciones |
| `TrajectoryErrorBound` | 9 | Del Jacobiano a la trayectoria: cota de error al fijar parámetros |

## Todos los teoremas y lemas

### `CertifiedFiniteODE`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `CertifiedFiniteODE.sampledCLM_apply` | Derivada de la trayectoria muestreada construida a partir de la sensibilidad S |
| lemma | `CertifiedFiniteODE.hasFDerivAt_sampled` |  |
| lemma | `CertifiedFiniteODE.jacobianOf_sampledCLM` |  |
| theorem | `CertifiedFiniteODE.sampledCLM_sub_le` | Paso 4. Si ‖S(t_k) − S'(t_k)‖ ≤ B para todo k, entonces |
| theorem | `CertifiedFiniteODE.certified_cos_ode` | Certificado de cos Δ para la EDO (Lc formal) |

### `CertifiedODEReduction`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `CertifiedODEReduction.certified_parameter_reduction` | Teorema principal (certificado de reducción para EDOs) |

### `CosineCertificate`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `CosineCertificate.cos_lower_of_rel_error` | Cota inferior del coseno a partir del error relativo |
| theorem | `CosineCertificate.cos_ge_of_rel_error` | Si además ε < 1 y a ≠ 0, entonces b ≠ 0 y cos Δ ≥ c |
| theorem | `CosineCertificate.taylor_bound` | Taylor con derivada Lipschitz: ‖F(θ₀+h) − F(θ₀) − DF(θ₀) h‖ ≤ Lc ‖h‖² |
| theorem | `CosineCertificate.finite_trajectory_error` | Cota explícita para perturbaciones finitas. Para todo ‖h‖ ≤ ρ₀: |
| theorem | `CosineCertificate.finite_cos_certificate` | Certificado de cos Δ para una perturbación finita h. Sean |

### `EventSystems`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `EventSystems.event_hasFDerivAt` | Diferenciabilidad respecto a θ para sistemas con eventos en tiempos fijos |

### `ExactLinearCertificate`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `ExactLinearCertificate.cos_certificate_of_bounds` | Lema genérico de certificado. Si 0 < A ≤ ‖a‖, ‖a − b‖ ≤ e y e² ≤ (1 − c²) A² con |
| lemma | `ExactLinearCertificate.cosv_smul` | cosv es invariante por un mismo reescalado positivo de ambos vectores |
| lemma | `ExactLinearCertificate.continuousAt_cosv` | cosv es continua en todo par de vectores no nulos |
| lemma | `ExactLinearCertificate.keepS_smul` | keepS es lineal: (s h)_S = s h_S |
| theorem | `ExactLinearCertificate.norm_linear_part_eq` | El término lineal exacto es la norma del vector ∑_{j ∉ S} J_{·j} h_j, calculable |
| theorem | `ExactLinearCertificate.finite_trajectory_error_exact` | (A1) Cota explícita con el error lineal exacto. Para todo ‖h‖ ≤ ρ₀: |
| theorem | `ExactLinearCertificate.exact_le_Rvar_bound` | La cota exacta nunca es peor que la de R(S) |
| theorem | `ExactLinearCertificate.finite_cos_certificate_exact` | (A1) Certificado de cos Δ con el error lineal exacto. Con |
| theorem | `ExactLinearCertificate.certified_cos_ode_exact` | (A1) Certificado de cos Δ para la EDO con el error lineal exacto y Lc formal |
| theorem | `ExactLinearCertificate.tendsto_cos_delta` | (A2) Límite de cos Δ. Si F es diferenciable en θ₀ con derivada J, y J h ≠ 0, |
| theorem | `ExactLinearCertificate.eventually_cos_delta_gt` | (A2) Certificado local sin Lc. Si el coseno lineal cos(J h, J h_S) (calculado con la |
| theorem | `ExactLinearCertificate.exists_cos_delta_gt` | Forma explícita: existe s₀ > 0 tal que cos Δ(s h) > c para todo s ∈ (0, s₀) |
| theorem | `ExactLinearCertificate.local_cos_ode` | (A2) Versión para la EDO. Si la solución es C¹ en un abierto alrededor de la trayectoria |

### `FirstOrderErrorBound`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `FirstOrderErrorBound.sqNorm_nonneg` | ‖Δθ_{Sᶜ}‖²: magnitud de la perturbación en los parámetros descartados |
| theorem | `FirstOrderErrorBound.columnEnergy_nonneg` |  |
| theorem | `FirstOrderErrorBound.removedColumnEnergy_nonneg` |  |
| theorem | `FirstOrderErrorBound.removedParamSq_nonneg` |  |
| theorem | `FirstOrderErrorBound.sum_split` | Separar una suma sobre todos los parámetros en conservados + descartados |
| theorem | `FirstOrderErrorBound.total_eq_kept_add_removed` | tr(JᵀJ) = energía conservada + energía descartada |
| theorem | `FirstOrderErrorBound.response_sub_reduced` | El error de truncamiento es exactamente la contribución de las columnas descartadas |
| theorem | `FirstOrderErrorBound.first_order_error_sq_bound` | Cota de error de primer orden (forma cuadrática) |
| theorem | `FirstOrderErrorBound.first_order_error_bound` | Cota de error de primer orden (forma con normas) |
| theorem | `FirstOrderErrorBound.removedParamSq_le` | ‖Δθ_{Sᶜ}‖² ≤ ‖Δθ‖² |
| theorem | `FirstOrderErrorBound.first_order_error_from_removed_fraction` | Conexión con el criterio del Stage 1 (energía descartada ≤ ε·tr(JᵀJ)) |
| theorem | `FirstOrderErrorBound.first_order_error_from_Rvar` | Forma con R_var. Si la fracción conservada cumple |

### `GlobalExistence`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `GlobalExistence.clampB_apply` | Truncamiento a la caja [0, B]ⁿ |
| lemma | `GlobalExistence.clampB_nonneg` |  |
| lemma | `GlobalExistence.clampB_le` |  |
| lemma | `GlobalExistence.clampB_pos` |  |
| lemma | `GlobalExistence.clampB_eq` |  |
| lemma | `GlobalExistence.dist_clampB_le` |  |
| lemma | `GlobalExistence.clampB_mem` | La caja [0, B]ⁿ |
| lemma | `GlobalExistence.convex_box` |  |
| lemma | `GlobalExistence.isCompact_box` |  |
| lemma | `GlobalExistence.lipschitzOn_box` | Un campo C¹ en un abierto que contiene la caja es Lipschitz en la caja |
| theorem | `GlobalExistence.exists_global_solution` | Existencia global de la solución (condición C4) |

### `GlobalLipschitzODE`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `ODEParamDiff.isSolOn_self` | α resuelve α' = v t α en [a, c] (derivadas dentro de [a, c]) |
| lemma | `ODEParamDiff.extend_solution` | Paso de extensión: una solución en [a, c] se extiende a [a, d] si K (d - c) ≤ 1/2 |
| theorem | `ODEParamDiff.exists_solution_Icc` | Existencia global en [a, b] para un campo globalmente K-Lipschitz y continuo en t |

### `GreedySelection`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `GreedySelection.greedy_ok` | El resultado siempre pasa el filtro ok |
| theorem | `GreedySelection.greedy_subset` | El resultado contiene al conjunto inicial y solo añade candidatos de la lista |
| theorem | `GreedySelection.greedy_discard_permanent` | Descarte permanente. Si ok es antimonótono, todo candidato j de la lista que no |
| lemma | `GreedySelection.supportedOn_mono` | Filtro VIF: para cada j ∈ S, toda combinación soportada en S con u_j = 1 cumple |
| theorem | `GreedySelection.okKappa_anti` | El filtro κ es antimonótono: quitar parámetros no aumenta κ |
| theorem | `GreedySelection.okVIF_anti` | El filtro VIF es antimonótono: quitar parámetros no aumenta ningún VIF |
| theorem | `GreedySelection.greedy_kappa_vif_guarantee` | Garantía del algoritmo de la sección 2.3. Con el filtro conjunto κ ≤ κ₀ y VIF ≤ V |

### `IdentifiabilityConditioning`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `Identifiability.IsLSMin.inner_residual_eq_zero` | Ecuaciones normales: en un minimizador el residuo es ortogonal a la imagen de Z |
| theorem | `Identifiability.ls_response_stability` | Estabilidad de la respuesta ajustada: ‖Z v − Z v'‖ ≤ ‖y − y'‖ |
| theorem | `Identifiability.ls_param_stability` | Unicidad y estabilidad con cota inferior σmin ‖u‖ ≤ ‖Z u‖ |
| theorem | `Identifiability.ls_unique` | Unicidad del estimador: con los mismos datos, el minimizador es único |
| theorem | `Identifiability.one_le_kappa_mul_sigmaMin` | Con columnas de norma 1 (‖Z e_j‖ = 1), σmax ≥ 1; por tanto κ σmin ≥ 1 |
| theorem | `Identifiability.ls_kappa_stability` | κ ⇒ estimación estable. Columnas L2-normalizadas, σmin ‖u‖ ≤ ‖Z u‖ ≤ σmax ‖u‖ y |
| theorem | `Identifiability.ls_param_kappa_stability` | Versión en los parámetros originales. Si J_S = Z ∘ D con D invertible |
| theorem | `Identifiability.ls_vif_coordinate_stability` | VIF ⇒ estabilidad por parámetro. Si toda combinación u con u_j = 1 cumple |
| theorem | `Identifiability.vif_geometric_of_inverse` | Del VIF calculado a la hipótesis geométrica. Sea w la columna j de (ZᵀZ)⁻¹, |
| theorem | `Identifiability.ls_vif_inverse_stability` | VIF (fórmula de la matriz inversa) ⇒ estabilidad por parámetro. Combinación de |

### `IntervalInit`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `IntervalInit.mul_mem_corners` | Exponentes de las potencias reales |
| lemma | `IntervalInit.imul_sound` |  |
| theorem | `IntervalInit.ival_sound` | Corrección de la evaluación por intervalos |
| theorem | `IntervalInit.initI_sound` | Dato inicial comprobado por intervalos: Gᵢ(θ₀) ≥ 0, y > 0 en Σ |
| theorem | `IntervalInit.strict_final_initI` | Teorema final con positividad estricta y dato inicial certificado por intervalos. Sin |

### `KineticCheck`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `KineticCheck.KExpr'.isNonneg_sound` | Cuasi-positividad de la componente i: ≥ 0 si y ≥ 0 y yᵢ = 0 |
| theorem | `KineticCheck.KExpr'.isPos_sound` |  |
| theorem | `KineticCheck.KExpr'.okOrth_sound` |  |
| theorem | `KineticCheck.KExpr'.vanishes_sound` |  |
| theorem | `KineticCheck.KExpr'.qp_sound` |  |
| theorem | `KineticCheck.checkModel_spec` | Comprobador de un modelo completo (calculable: Lean lo ejecuta con decide) |
| theorem | `KineticCheck.checkModel_sound` | Un modelo que pasa la comprobación tiene su dominio conteniendo el ortante y es |
| theorem | `KineticCheck.checked_model_hasFDerivAt` | Teorema final para un modelo comprobado. Si checkModel F = true (lo verifica Lean |
| theorem | `KineticCheck.checked_segments_hasFDerivAt` | Modelos con entradas por tramos (escalones en tiempos fijos). El tramo k dura L k y |
| lemma | `KineticCheck.qvec_apply` | Vector real con entradas racionales |
| theorem | `KineticCheck.posParams_qvec` | Comprobador: los parámetros marcados como positivos lo son |
| theorem | `KineticCheck.nonneg_qvec` | Comprobador: condiciones iniciales ≥ 0 |
| theorem | `KineticCheck.checked_model_final` | Teorema final por modelo (dato inicial constante). Con el modelo comprobado, θ₀ y |
| theorem | `KineticCheck.checked_segments_final` | Teorema final por modelo con entradas por tramos (dato inicial constante) |
| theorem | `KineticCheck.checkInit_spec` | Comprobador de la condición inicial x₀(θ) = G(θ): bien definida y ≥ 0 para θ > 0 |
| lemma | `KineticCheck.nonneg_zero` |  |
| theorem | `KineticCheck.init_differentiable` | La condición inicial θ ↦ G(θ) es diferenciable en todo θ₀ con parámetros positivos |
| theorem | `KineticCheck.init_nonneg` |  |
| theorem | `KineticCheck.checked_model_final_init` | Teorema final por modelo, con condición inicial x₀(θ) = G(θ) dependiente de θ |

### `KineticNetwork`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `KineticNetwork.eval_netExpr` | Campo de la red |
| lemma | `KineticNetwork.ok_netExpr` |  |
| lemma | `KineticNetwork.coef_mul_nonneg` | Comprobación de un término |
| theorem | `KineticNetwork.checkNet_sound` | La red comprobada tiene dominio ⊇ ortante y es cuasi-positiva |
| lemma | `KineticNetwork.eval_varfree` | Sin concentraciones |
| lemma | `KineticNetwork.ssum_nonneg` | Suma de las concentraciones |
| theorem | `KineticNetwork.lowerpos_sound` |  |
| theorem | `KineticNetwork.linBound_sound` |  |
| lemma | `KineticNetwork.sum_c_coef` | Peso de un término: Σ cᵢ · coefᵢ |
| lemma | `KineticNetwork.sum_c_netExpr` |  |
| theorem | `KineticNetwork.checkGrowth_sound` | Cota de crecimiento de una red comprobada |
| theorem | `KineticNetwork.checkNet_append` |  |
| theorem | `KineticNetwork.checkGrowth_append` |  |
| lemma | `KineticNetwork.c_ge_one` |  |
| theorem | `KineticNetwork.network_exists` | Existencia global de la solución nominal para una red comprobada |
| theorem | `KineticNetwork.network_final` | Teorema final de una red comprobada (dato inicial constante). Sin condiciones |
| theorem | `KineticNetwork.network_final_init` | Teorema final de una red comprobada, con condición inicial x₀(θ) = G(θ) |
| theorem | `KineticNetwork.network_segments_final` | Teorema final por tramos (entradas por escalones en tiempos fijos), sin condiciones |

### `KineticRegularity`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `KineticRegularity.KExpr.contDiffAt_eval` | Regularidad. Donde la expresión está bien definida, es C^k para todo k |
| theorem | `KineticRegularity.KExpr.isOpen_ok` | El conjunto donde la expresión está bien definida es abierto |
| theorem | `KineticRegularity.KExpr.ok_of_noDen` | Acción de masas: la expresión está bien definida en todo el espacio |
| theorem | `KineticRegularity.KExpr.ok_mm` | Hill con coeficiente real: V x^h / (K^h + x^h) |
| theorem | `KineticRegularity.KExpr.ok_hill` |  |
| theorem | `KineticRegularity.KExpr.ok_hillR` |  |
| theorem | `KineticRegularity.isOpen_domain` | Dominio natural: todas las componentes están bien definidas |
| theorem | `KineticRegularity.contDiffOn_field` | El campo de un modelo cinético es C^k (en particular C¹) en su dominio abierto |
| theorem | `KineticRegularity.domain_eq_univ` | Acción de masas pura: el dominio es todo el espacio |
| theorem | `KineticRegularity.kinetic_hasFDerivAt` | Diferenciabilidad de la trayectoria para modelos cinéticos. Única hipótesis sobre el |
| theorem | `KineticRegularity.kinetic_local_cos` | Certificado local de cos Δ para modelos cinéticos, con la misma única hipótesis |

### `LinearizedFit`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `LinearizedFit.lin_le_scaled` | El ajuste lineal no supera el error tras reescalar (en un subespacio que contiene b) |
| theorem | `LinearizedFit.fit_upper_of_lin` | Cota superior: el error real en el óptimo lineal no excede e_lin + M‖c‖² |
| theorem | `LinearizedFit.fit_lower_of_lin` | Cota inferior: en la bola ‖c‖ ≤ ρ, el error real es al menos e_lin‖d‖ − Mρ², |

### `LocalExistence`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `LocalExistence.clampE_apply` | Truncamiento coordenada a coordenada a la caja [-c, c]ⁿ |
| lemma | `LocalExistence.abs_clamp_sub_le` |  |
| lemma | `LocalExistence.dist_clampE_le` |  |
| lemma | `LocalExistence.lipschitz_clampE` |  |
| lemma | `LocalExistence.clampE_eq` | El truncamiento es la identidad en la bola de radio c |
| lemma | `LocalExistence.clampE_zero` |  |
| lemma | `LocalExistence.norm_clampE_le` | La imagen del truncamiento está en la bola de radio (n + 1) c |
| theorem | `LocalExistence.exists_solutions_near` | Existencia de soluciones para θ cerca de θ₀. Si f es C¹ en el abierto U, x₀ |
| theorem | `LocalExistence.hasFDerivAt_of_nominal_solution` | Diferenciabilidad respecto a θ a partir sólo de la solución nominal. Con las hipótesis |

### `NominalCertificate`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `NominalCertificate.local_cos_from_nominal` | Certificado local de cos Δ con hipótesis mínimas. Existe la familia de soluciones x |

### `NumericalRobustness`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `NumericalRobustness.fd_column_error` | Error de diferencias finitas con paso δ en la dirección v (‖v‖ = 1): |
| lemma | `NumericalRobustness.columnEnergy_eq_norm_sq` | Columna j de J como vector euclídeo |
| theorem | `NumericalRobustness.rvar_certified_from_approx` | R_var certificado. Sean J̃ las columnas calculadas con ‖J_j − J̃_j‖ ≤ τ_j |
| theorem | `NumericalRobustness.opNorm_le_frobenius` | Norma de operador acotada por la norma de Frobenius (por columnas) |
| theorem | `NumericalRobustness.kappa_certified_from_approx` | κ certificado. Si ‖(Z − Z̃) u‖ ≤ τ ‖u‖ para todo u, Z̃ cumple |
| theorem | `NumericalRobustness.vif_certified_from_approx` | VIF certificado. Con las mismas hipótesis sobre Z̃ (cota inferior σ̃min) y |

### `OutputComposition`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `OutputComposition.output_sq_bound` | Cota de salidas a partir de los estados (suma de cuadrados) |
| theorem | `OutputComposition.output_uniform_bound` | Cota uniforme: con ‖x(t_i) − x'(t_i)‖ ≤ ε para todas las mediciones |
| theorem | `OutputComposition.log_lipschitz` | log es Lipschitz con constante 1/c en [c, ∞), c > 0 |
| theorem | `OutputComposition.log10_lipschitz` | log10 (log x / log 10) es Lipschitz con constante 1/(c · log 10) en [c, ∞) |

### `ParamDiffODE`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `ODEParamDiff.uniform_linearization` | Linealización uniforme de una función C¹ en un abierto U, cerca de un compacto K₀ |
| theorem | `ODEParamDiff.tube_gronwall` | Grönwall en un tubo. Si yh es una solución aproximada (defecto ≤ εg) que |
| lemma | `ODEParamDiff.norm_comp_inl_le` |  |
| lemma | `ODEParamDiff.clm_prod_apply_split` |  |
| lemma | `ODEParamDiff.lipschitzOn_slice` | Lipschitz de y ↦ f y θ en una bola, a partir de una cota de la derivada conjunta |
| theorem | `ODEParamDiff.hasFDerivAt_solution_param_init` | Dependencia diferenciable respecto a parámetros |
| theorem | `ODEParamDiff.hasFDerivAt_solution_param_on` | Versión con dato inicial fijo y f de clase C¹ en un abierto U |
| theorem | `ODEParamDiff.hasFDerivAt_solution_param` | Versión global: f de clase C¹ en todo E × P |

### `PatternMechanisms`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `PatternMechanisms.not_okKappa_of_kernel` | Patrón D, filtro κ. Si existe u ≠ 0 soportado en S con Z u = 0, ningún κ₀ |
| theorem | `PatternMechanisms.ls_not_unique_of_kernel` | Patrón D, identificabilidad. Si Z u = 0, todo minimizador v tiene otro |
| theorem | `PatternMechanisms.opposing_pair_kernel` | Caso concreto de efectos opuestos: si la columna a es λ veces la columna b |
| theorem | `PatternMechanisms.exact_reduction_of_zero_energy` | Patrón A, reducción exacta. Si la energía descartada es nula, la respuesta |

### `Poda`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `Poda.prune_spec` | Corrección de la poda: admisible, contenido en S y mínimo por inclusión |
| theorem | `Poda.exists_minimal_admissible` | Forma de uso: existe un subconjunto admisible de S, mínimo por inclusión, que se obtiene |

### `PositivityInvariance`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `PositivityInvariance.pos_apply` | Parte positiva componente a componente |
| lemma | `PositivityInvariance.pos_nonneg` |  |
| lemma | `PositivityInvariance.pos_eq_self` |  |
| lemma | `PositivityInvariance.dist_pos_le` |  |
| lemma | `PositivityInvariance.sub_pos_apply` |  |
| lemma | `PositivityInvariance.pos_apply_eq_zero` |  |
| lemma | `PositivityInvariance.isClosed_nonneg` |  |
| lemma | `PositivityInvariance.hasDerivAt_negSq` | a ↦ min(a, 0)² es derivable con derivada 2 min(a, 0) |
| theorem | `PositivityInvariance.nonneg_core` | Núcleo (Grönwall). En [a, b], si x' = v(x), x(a) ≥ 0, |
| theorem | `PositivityInvariance.nonneg_of_quasiPositive` | Invariancia del ortante ≥ 0. Si v es C¹ en un abierto U, cuasi-positiva en los |
| theorem | `PositivityInvariance.kinetic_nonneg` | Modelos cinéticos: positividad y permanencia en el dominio. Si el dominio del modelo |
| theorem | `PositivityInvariance.kinetic_hasFDerivAt_of_nonneg` | Diferenciabilidad para modelos cinéticos con dato inicial ≥ 0. Igual que |
| theorem | `PositivityInvariance.exampleModel_orth` | El modelo de ejemplo |
| theorem | `PositivityInvariance.exampleModel_qp` |  |
| theorem | `PositivityInvariance.exampleModel_nonneg` | En el ejemplo, toda solución con x(0) ≥ 0 es ≥ 0 y permanece en el dominio |

### `RefitMonotone`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `RefitMonotone.feas_mono` | Error tras reestimar S (ínfimo sobre los factibles) |
| theorem | `RefitMonotone.fitErr_anti` | Monotonía: más parámetros libres ⇒ error de reajuste menor o igual |
| theorem | `RefitMonotone.fitErr_union_le` | Calibración: reajustar además los parámetros C no empeora el error |
| theorem | `RefitMonotone.fitErr_le_erel` | e_ajuste ≤ e_rel: el punto sin reajuste es factible |
| theorem | `RefitMonotone.admissible_mono` | Admisibilidad monótona: si S cumple el umbral, cualquier T ⊇ S también |

### `RiccatiNetwork`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `RiccatiNetwork.exists_solution_riccati` | Existencia en [0, T] con crecimiento cuadrático |
| theorem | `RiccatiNetwork.qval_sound` | Su valor racional en θ = θq |
| lemma | `RiccatiNetwork.qnn_sound` | Constante racional ≥ 0 |
| lemma | `RiccatiNetwork.var_le_phi` | Cota lineal 0 ≤ e ≤ A + B·φ |
| theorem | `RiccatiNetwork.linV_sound` |  |
| lemma | `RiccatiNetwork.prodV_sound` | Producto de dos cotas lineales |
| theorem | `RiccatiNetwork.quadV_sound` |  |
| theorem | `RiccatiNetwork.tot_sound` | Comprobación completa: pesos ≥ 1, signos, Q > 0 y 1.1·Q·(φ₀ + 1)·T_q < 1 |
| theorem | `RiccatiNetwork.riccati_final` | Teorema final con crecimiento cuadrático: para 0 ≤ T ≤ T_q, la solución nominal |

### `ScaledError`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `ScaledError.norm_sub_smul_sq` |  |
| theorem | `ScaledError.scaled_error_ge` | Cota inferior del error con reescalado |
| theorem | `ScaledError.scaled_error_eq` | El mínimo se alcanza en α* = ⟪a, b⟫ / ‖b‖² |
| theorem | `ScaledError.scaled_error_cos` | Forma con cos Δ: el error mínimo es ‖a‖²(1 − cos²Δ) |
| theorem | `ScaledError.min_rel_error_eq` | Error relativo mínimo tras reescalar = √(1 − cos²Δ) |

### `SensitivityLipschitz`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `SensitivityLipschitz.gronwall_zero_init` | Grönwall con dato inicial nulo: si u 0 = 0 y ‖u'‖ ≤ K ‖u‖ + ε en [0, T], entonces |
| lemma | `SensitivityLipschitz.norm_comp_inl_le` |  |
| lemma | `SensitivityLipschitz.norm_comp_inr_le` |  |
| lemma | `SensitivityLipschitz.g_lipschitz` | g es M₁-Lipschitz en el convexo K |
| lemma | `SensitivityLipschitz.norm_pair_sub_le` |  |
| theorem | `SensitivityLipschitz.traj_lipschitz` | 1. Las trayectorias son Lipschitz en θ: ‖x(θ,t) − x(θ',t)‖ ≤ (e^{M₁T} − 1) ‖θ − θ'‖ |
| theorem | `SensitivityLipschitz.sens_bound` | 2. La sensibilidad está acotada: ‖S_θ(t)‖ ≤ e^{M₁T} − 1 |
| theorem | `SensitivityLipschitz.sens_lipschitz` | 3. La sensibilidad es Lipschitz en θ: |

### `SpectralConditioning`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `SpectralConditioning.inner_gram` | Operador de Gram G = Z† Z (en coordenadas, Zᵀ Z) |
| lemma | `SpectralConditioning.gram_isSymmetric` |  |
| lemma | `SpectralConditioning.finrank_eq` |  |
| lemma | `SpectralConditioning.lam_antitone` | Base ortonormal de autovectores de ZᵀZ (vectores singulares derechos de Z) |
| lemma | `SpectralConditioning.gram_evec` |  |
| lemma | `SpectralConditioning.sq_norm_apply_evec` | ‖Z vᵢ‖² = λᵢ: los autovalores son los cuadrados de los valores singulares |
| lemma | `SpectralConditioning.lam_nonneg` |  |
| theorem | `SpectralConditioning.sq_norm_apply_eq_sum` | Teorema espectral aplicado a Z: ‖Z u‖² = ∑ᵢ λᵢ cᵢ² y ‖u‖² = ∑ᵢ cᵢ², con c las |
| theorem | `SpectralConditioning.sq_norm_eq_sum` |  |
| theorem | `SpectralConditioning.sq_norm_bounds` | Si todos los autovalores están en [lo, hi], entonces lo ‖u‖² ≤ ‖Z u‖² ≤ hi ‖u‖² |
| lemma | `SpectralConditioning.lam_le_max` | Índice del menor autovalor |
| lemma | `SpectralConditioning.min_le_lam` |  |
| theorem | `SpectralConditioning.norm_bounds` | √λ_min ‖u‖ ≤ ‖Z u‖ ≤ √λ_max ‖u‖ |
| theorem | `SpectralConditioning.opNorm_eq_sqrt_lamMax` | σ_max = √λ_max = ‖Z‖ (norma de operador) |
| theorem | `SpectralConditioning.sqrt_lamMin_mul_le` | √λ_min es una cota inferior válida: √λ_min ‖u‖ ≤ ‖Z u‖ |
| theorem | `SpectralConditioning.le_sqrt_lamMin` | … y es la mejor posible: toda σ con σ ‖u‖ ≤ ‖Z u‖ cumple σ ≤ √λ_min = σ_min |
| theorem | `SpectralConditioning.ls_kappa_stability_spectral` | κ espectral ⇒ estimación estable. Con columnas L2-normalizadas y λ_min > 0, dos |
| lemma | `SpectralConditioning.matCLM_apply` | Aplicación lineal continua asociada a una matriz M (la matriz de sensibilidad escalada) |
| lemma | `SpectralConditioning.inner_matCLM` |  |
| theorem | `SpectralConditioning.gram_toEuclideanLin` | gram (matCLM M) es la matriz Mᵀ M (lo que calcula Z.T @ Z) |
| theorem | `SpectralConditioning.vif_matrix_inverse` | VIF mediante la matriz inversa. Si MᵀM es invertible y w = (MᵀM)⁻¹ e_j, entonces |
| theorem | `SpectralConditioning.ls_vif_matrix_stability` | VIF calculado con inv(Z.T @ Z) ⇒ estabilidad por parámetro. Si |

### `StrictExistence`

| Tipo | Nombre | Descripción |
|---|---|---|
| lemma | `StrictExistence.lo_nonneg` | Cota inferior de la caja: ε en Σ, 0 fuera |
| lemma | `StrictExistence.lo_le` |  |
| lemma | `StrictExistence.clampQ_apply` | Truncamiento a la caja Q |
| lemma | `StrictExistence.clampQ_mem` | La caja Q |
| lemma | `StrictExistence.boxQ_sPos` |  |
| lemma | `StrictExistence.clampQ_pos` |  |
| lemma | `StrictExistence.clampQ_eq` |  |
| lemma | `StrictExistence.dist_clampQ_le` |  |
| lemma | `StrictExistence.convex_boxQ` |  |
| lemma | `StrictExistence.isCompact_boxQ` |  |
| lemma | `StrictExistence.lipschitzOn_boxQ` |  |
| theorem | `StrictExistence.exists_global_solution_strict` | Existencia global con positividad estricta |

### `StrictNetwork`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `StrictNetwork.keq_sound` | Igualdad sintáctica (conservadora: false con constantes reales y potencias reales) |
| lemma | `StrictNetwork.qge1_sound` | Racional > 1 |
| lemma | `StrictNetwork.qgt1_sound` |  |
| lemma | `StrictNetwork.addlb_sound` | q + θⱼ ≥ 0 por una cota inferior θⱼ ≥ r ≥ −q |
| lemma | `StrictNetwork.subub_sound` |  |
| lemma | `StrictNetwork.ub_qvec` | Las cotas ub se cumplen en θq |
| theorem | `StrictNetwork.sign_sound` | Corrección conjunta de sNonneg, snp y expLe1 |
| theorem | `StrictNetwork.sNonneg_sound` |  |
| theorem | `StrictNetwork.expLe1_sound` |  |
| theorem | `StrictNetwork.sPos_sound` |  |
| theorem | `StrictNetwork.sOk_sound` |  |
| theorem | `StrictNetwork.snp_sound` |  |
| theorem | `StrictNetwork.summand_sound` | X es un sumando de d (los demás sumandos son ≥ 0), luego 0 ≤ X ≤ d |
| lemma | `StrictNetwork.bndB_const` | 0 ≤ e ≤ K·yᵢ en P ∩ [0, B]ⁿ |
| lemma | `StrictNetwork.bndB_div_lowerpos` |  |
| lemma | `StrictNetwork.bndB_summand` |  |
| lemma | `StrictNetwork.bndB_mul` |  |
| lemma | `StrictNetwork.bndB_add` |  |
| lemma | `StrictNetwork.bndB_frac_mul_l` | (u·v)/d = (u/d)·v |
| lemma | `StrictNetwork.bndB_frac_mul_r` | (u·v)/d = u·(v/d) |
| lemma | `StrictNetwork.bndB_pair` |  |
| lemma | `StrictNetwork.bndB_pair'` |  |
| lemma | `StrictNetwork.consB_mul_l` |  |
| lemma | `StrictNetwork.consB_mul_r` |  |
| lemma | `StrictNetwork.consB_div_lowerpos` |  |
| lemma | `StrictNetwork.bndB_congr` |  |
| lemma | `StrictNetwork.consB_congr` |  |
| lemma | `StrictNetwork.eval_pair` |  |
| lemma | `StrictNetwork.eval_pair'` |  |
| lemma | `StrictNetwork.consB_var` |  |
| lemma | `StrictNetwork.consB_npow` |  |
| lemma | `StrictNetwork.bndB_npow` |  |
| lemma | `StrictNetwork.bndB_exp_np` |  |
| lemma | `StrictNetwork.bndB_var` |  |
| lemma | `StrictNetwork.bq_of` | Factor acotado a/d |
| lemma | `StrictNetwork.cq_of` | Factor proporcional a/d ≤ K·yᵢ |
| theorem | `StrictNetwork.bnd_sound` | Corrección de los comprobadores de acotación y de consumo proporcional |
| lemma | `StrictNetwork.term_qp` | Cuasi-positividad en P de la contribución de un término |
| lemma | `StrictNetwork.term_decay` | Consumo proporcional de una especie de Σ en la contribución de un término |
| theorem | `StrictNetwork.checkNetS_sound` |  |
| lemma | `StrictNetwork.term_growth` |  |
| theorem | `StrictNetwork.checkGrowthS_sound` |  |
| lemma | `StrictNetwork.c_ge_oneS` |  |
| theorem | `StrictNetwork.strict_exists` | Existencia global con positividad estricta para una red comprobada |
| lemma | `StrictNetwork.init_sPos` | Condición inicial G(θ): bien definida, ≥ 0, y > 0 en Σ |
| theorem | `StrictNetwork.strict_final_init` | Teorema final con positividad estricta (condición inicial G(θ)). Sin condiciones |

### `TrajectoryErrorBound`

| Tipo | Nombre | Descripción |
|---|---|---|
| theorem | `TrajectoryErrorBound.keepS_apply` | Perturbación del modelo reducido: conserva Δθ_j si j ∈ S, y pone 0 |
| theorem | `TrajectoryErrorBound.norm_keepS_le` | ‖Δθ_S‖ ≤ ‖Δθ‖ |
| theorem | `TrajectoryErrorBound.clm_apply_eq_linResponse` | Expansión de una aplicación lineal en la base canónica: |
| theorem | `TrajectoryErrorBound.clm_keepS_eq_reducedResponse` | (L Δθ_S)_i = ∑_{j∈S} J i j · Δθ_j |
| theorem | `TrajectoryErrorBound.linear_part_bound` | Parte lineal del error: ‖L Δθ − L Δθ_S‖ ≤ √R(S) · ‖Δθ_{Sᶜ}‖ |
| theorem | `TrajectoryErrorBound.sqrt_removedParamSq_le` | ‖Δθ_{Sᶜ}‖² ≤ ‖Δθ‖² en forma de raíces |
| theorem | `TrajectoryErrorBound.remainder_isLittleO` | El resto no lineal F(θ₀+Δθ) − F(θ₀+Δθ_S) − L(Δθ − Δθ_S) es o(‖Δθ‖) |
| theorem | `TrajectoryErrorBound.trajectory_error_bound` | Cota de error de trayectoria (no lineal, local) |
| theorem | `TrajectoryErrorBound.trajectory_error_from_Rvar` | Forma con el criterio del Stage 1. Si R_var(S) ≥ r |

## Modelos del benchmark

Cada archivo de `Models/` es un modelo traducido de SBML; su teorema final establece regularidad, existencia de solución en el horizonte simulado y no negatividad de las concentraciones.

* `Armistead_CellDeathDis2024`: `Models.Armistead_CellDeathDis2024.final`
* `Bachmann_MSB2011`: `Models.Bachmann_MSB2011.final`
* `Blasi_CellSystems2016`: `Models.Blasi_CellSystems2016.final`
* `Boehm_JProteomeRes2014`: `Models.Boehm_JProteomeRes2014.final`
* `Borghans_BiophysChem1997`: `Models.Borghans_BiophysChem1997.final`
* `Brannmark_JBC2010`: `Models.Brannmark_JBC2010.final`
* `Chen_MSB2009`: `Models.Chen_MSB2009.final`
* `Crauste_CellSystems2017`: `Models.Crauste_CellSystems2017.final`
* `Elowitz_Nature2000`: `Models.Elowitz_Nature2000.final`
* `Fiedler_BMCSystBiol2016`: `Models.Fiedler_BMCSystBiol2016.final`
* `Froehlich_CellSystems2018`: `Models.Froehlich_CellSystems2018.final`
* `Giordano_Nature2020`: `Models.Giordano_Nature2020.final`
* `Lang_PLOSComputBiol2024`: `Models.Lang_PLOSComputBiol2024.final`
* `Okuonghae_ChaosSolitonsFractals2020`: `Models.Okuonghae_ChaosSolitonsFractals2020.final`
* `Rahman_MBS2016`: `Models.Rahman_MBS2016.final`
* `Raia_CancerResearch2011`: `Models.Raia_CancerResearch2011.final`
* `Raimundez_PCB2020`: `Models.Raimundez_PCB2020.final`
* `SalazarCavazos_MBoC2020`: `Models.SalazarCavazos_MBoC2020.final`
* `Sneyd_PNAS2002`: `Models.Sneyd_PNAS2002.final`
* `Weber_BMC2015`: `Models.Weber_BMC2015.final`
* `Zhao_QuantBiol2020`: `Models.Zhao_QuantBiol2020.final`
* `Zheng_PNAS2012`: `Models.Zheng_PNAS2012.final`
