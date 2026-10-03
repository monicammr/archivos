# Certificado Lean 4: error de trayectoria al fijar parámetros

Verificado con Lean 4.23.0 y Mathlib `v4.23.0` (mismas versiones que el proyecto original).
Ningún teorema usa `sorry` ni axiomas propios: `#print axioms` devuelve solo
`[propext, Classical.choice, Quot.sound]`.

| Archivo | Teorema | Enunciado |
|---|---|---|
| `FirstOrderErrorBound.lean` | `first_order_error_sq_bound` | ‖JΔθ − J_SΔθ_S‖² ≤ R(S)·‖Δθ_{Sᶜ}‖², con R(S) = Σ_{j∉S}(JᵀJ)_jj |
| | `first_order_error_from_Rvar` | R_var(S) ≥ r ⇒ ‖JΔθ − J_SΔθ_S‖² ≤ (1−r)·tr(JᵀJ)·‖Δθ‖² |
| `TrajectoryErrorBound.lean` | `trajectory_error_bound` | Si θ ↦ F(θ) (trayectoria muestreada) es diferenciable en θ₀ con Jacobiano J: ∀η>0, para Δθ pequeño, ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ √R(S)·‖Δθ_{Sᶜ}‖ + η‖Δθ‖ |
| | `trajectory_error_from_Rvar` | R_var(S) ≥ r ⇒ ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ (√((1−r)·tr(JᵀJ)) + η)·‖Δθ‖ |

Alcance: el resultado es local (Δθ → 0). La diferenciabilidad de la trayectoria respecto a
los parámetros es una hipótesis (`HasFDerivAt`), que para EDOs con campo C¹ es el teorema
clásico de dependencia diferenciable. `J` es el Jacobiano exacto; el calculado por
diferencias finitas es una aproximación de él.

## Compilar
En un proyecto con Mathlib v4.23.0, agrega `` `FirstOrderErrorBound `` y
`` `TrajectoryErrorBound `` a `roots` del `lakefile.lean` y ejecuta `lake build`.
