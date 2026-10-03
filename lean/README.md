# Certificado Lean 4: reducción de parámetros en sistemas de EDOs

Verificado con Lean 4.23.0 y Mathlib `v4.23.0`. Ningún archivo usa `sorry` ni axiomas propios:
`#print axioms` devuelve solo `[propext, Classical.choice, Quot.sound]`.

```
lake exe cache get   # descarga Mathlib precompilado
lake build
```

## Teorema principal

`CertifiedODEReduction.certified_parameter_reduction` (`CertifiedODEReduction.lean`)

Sea `ẋ = f(x, θ)` con `f : ℝⁿ × ℝᵖ → ℝⁿ` de clase C¹, y supongamos que para `θ` cerca de `θ₀`
las soluciones `x(θ, ·)` existen en `[0, T]` con el mismo dato inicial. Sean `t_1, …, t_N ∈ [0, T]`
los instantes de muestreo. Entonces existe la sensibilidad `S(t)` (solución de la ecuación
variacional `S' = ∂ₓf·S + ∂_θf`, `S(0) = 0`) tal que, con `J` la matriz de sensibilidad
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
| `ParamDiffODE.lean` | **Dependencia diferenciable respecto a parámetros** (`hasFDerivAt_solution_param`): θ ↦ x(θ,t) es diferenciable y su derivada resuelve la ecuación variacional. Usa Grönwall (Mathlib), linealización uniforme en compactos e inducción continua |
| `CertifiedODEReduction.lean` | Une todo en el teorema principal |

## Hipótesis que permanecen (explícitas en el enunciado)

1. `f` es C¹ en todo `ℝⁿ × ℝᵖ` (cierto para cinética de acción de masas, que es polinomial).
2. Las soluciones existen en `[0, T]` para `θ` en un entorno de `θ₀` (el modelo está bien planteado).
3. El dato inicial no depende de `θ`.
4. El resultado es local (`Δθ → 0`); no da una cota numérica para perturbaciones finitas.
5. `J` es la sensibilidad exacta; la calculada por diferencias finitas es una aproximación.
