import LocalExistence
import ExactLinearCertificate

/-!
# Certificado local de cos Δ a partir sólo de la trayectoria nominal

Encadena `LocalExistence` (las soluciones existen cerca de `θ₀`), `ParamDiffODE` (la
trayectoria es diferenciable) y `ExactLinearCertificate` (el coseno no lineal tiende al lineal).
Las únicas hipótesis son: `f` de clase C¹ en un abierto `U` que contiene la trayectoria nominal,
la trayectoria nominal `x₀` (la que se integra numéricamente) y un dato inicial diferenciable.
-/

open Set Filter Topology Metric TrajectoryErrorBound CertifiedODEReduction CertifiedFiniteODE
  ExactLinearCertificate LocalExistence

namespace NominalCertificate

variable {n p N : ℕ}

/-- **Certificado local de cos Δ con hipótesis mínimas.** Existe la familia de soluciones `x`
(con `x θ₀ = x₀`) y la sensibilidad `S₀` (con `S₀ 0 = D0`) tales que, para cualquier conjunto
`Sset` y dirección `h`, si el coseno lineal calculado con la matriz de sensibilidad muestreada
supera `c`, entonces `cos Δ(s h) > c` para todo `s ∈ (0, s₀)`. -/
theorem local_cos_from_nominal
    (f : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p))} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      f z.1 z.2) U)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (f (x₀ t) θ₀) (Icc 0 T) t)
    (hγU : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ U)
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0)
    (tk : Fin N → ℝ) (htk : ∀ k, tk k ∈ Icc 0 T) :
    ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S₀ : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S₀ 0 = D0 ∧
        (∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S₀ t) θ₀) ∧
        ∀ (Sset : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) {c : ℝ},
          sampledCLM S₀ tk h ≠ 0 → sampledCLM S₀ tk (keepS Sset h) ≠ 0 →
          c < cosv (sampledCLM S₀ tk h) (sampledCLM S₀ tk (keepS Sset h)) →
          ∃ s₀ : ℝ, 0 < s₀ ∧ ∀ s ∈ Ioo 0 s₀,
            c < cosv (sampled x tk (θ₀ + s • h) - sampled x tk θ₀)
                  (sampled x tk (θ₀ + keepS Sset (s • h)) - sampled x tk θ₀) := by
  obtain ⟨x, hxθ₀, hev, S₀, hS0, -, hSder⟩ :=
    hasFDerivAt_of_nominal_solution f hU hf hT x₀ θ₀ hx₀ hγU x0 D0 hx0 hx00
  refine ⟨x, hxθ₀, hev, S₀, hS0, hSder, ?_⟩
  intro Sset h c h1 h2 hlin
  exact exists_cos_delta_gt (sampled x tk) (sampledCLM S₀ tk) θ₀
    (hasFDerivAt_sampled x tk θ₀ S₀ (fun k => hSder (tk k) (htk k))) Sset h h1 h2 hlin

end NominalCertificate

#print axioms NominalCertificate.local_cos_from_nominal
