import TrajectoryErrorBound
import ParamDiffODE

/-!
# Certificado completo: de la EDO al error de trayectoria del modelo reducido

Une los dos resultados:
* `ODEParamDiff.hasFDerivAt_solution_param`: la trayectoria es diferenciable respecto a θ
  y su derivada es la solución `S` de la ecuación variacional (sin suponerlo);
* `TrajectoryErrorBound.trajectory_error_from_Rvar`: si `R_var(S) ≥ r`, fijar los
  parámetros descartados produce un error de trayectoria `≤ (√((1−r)·tr(JᵀJ)) + η)‖Δθ‖`.

La matriz `J` es la matriz de sensibilidad muestreada: filas = (instante `t_k`, estado `i`),
columnas = parámetros, `J_{(k,i),j} = (S(t_k) e_j)_i`.
-/

open Set Filter Topology Asymptotics FirstOrderErrorBound TrajectoryErrorBound ODEParamDiff

namespace CertifiedODEReduction

variable {n p N : ℕ}

/-- Trayectoria muestreada en los instantes `tk`, aplanada a un vector de `ℝ^{N·n}`. -/
noncomputable def sampled (x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n))
    (tk : Fin N → ℝ) (θ : EuclideanSpace ℝ (Fin p)) : EuclideanSpace ℝ (Fin (N * n)) :=
  (EuclideanSpace.equiv (Fin (N * n)) ℝ).symm
    (fun i => x θ (tk (finProdFinEquiv.symm i).1) (finProdFinEquiv.symm i).2)

/-- Matriz de sensibilidad muestreada `J_{(k,i),j} = (S(t_k) e_j)_i`. -/
noncomputable def sensMatrix
    (S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)))
    (tk : Fin N → ℝ) : Fin (N * n) → Fin p → ℝ :=
  fun i j => S (tk (finProdFinEquiv.symm i).1) (EuclideanSpace.single j 1)
    (finProdFinEquiv.symm i).2

/-- **Teorema principal (certificado de reducción para EDOs).**

Hipótesis: `f` es C¹ en un abierto `U` que contiene la trayectoria nominal (basta para
cinéticas de acción de masas, Michaelis–Menten o Hill); para `θ` cerca de `θ₀` las soluciones
`x θ` existen en `[0, T]` con dato inicial `x θ 0 = x0 θ`, donde `x0` es diferenciable en `θ₀`
con derivada `D0` (`D0 = 0` si el dato inicial no depende de los parámetros); los instantes de
muestreo `t_k` están en `[0, T]`.

Conclusión: existe la sensibilidad `S` (solución de la ecuación variacional, `S 0 = D0`) tal
que, para todo subconjunto `Sset` de parámetros conservados con `R_var(Sset) ≥ r` medido sobre
la matriz de sensibilidad muestreada `J`, y para todo `η > 0`, si `Δθ` es suficientemente
pequeño:

  ‖F(θ₀+Δθ) − F(θ₀+Δθ_S)‖ ≤ (√((1−r)·tr(JᵀJ)) + η) · ‖Δθ‖,

donde `F` es la trayectoria muestreada y `F(θ₀+Δθ_S)` la del modelo reducido (parámetros
descartados fijados en su valor nominal). -/
theorem certified_parameter_reduction
    (f : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p))} (hU : IsOpen U)
    (hf : ContDiffOn ℝ 1 (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      f z.1 z.2) U)
    {T : ℝ} (hT : 0 ≤ T) (x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n))
    (θ₀ : EuclideanSpace ℝ (Fin p))
    (hγU : ∀ t ∈ Icc 0 T, (x θ₀ t, θ₀) ∈ U)
    (hsol : ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 T,
      HasDerivWithinAt (x θ) (f (x θ t) θ) (Icc 0 T) t)
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀)
    (hinit : ∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ)
    (tk : Fin N → ℝ) (htk : ∀ k, tk k ∈ Icc 0 T) :
    ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
      S 0 = D0 ∧
      (∀ t ∈ Icc 0 T, HasDerivWithinAt S
        ((fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) => f z.1 z.2)
            (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ _ _) ∘L S t
          + (fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) => f z.1 z.2)
            (x θ₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ _ _)) (Icc 0 T) t) ∧
      ∀ (Sset : Finset (Fin p)) (r : ℝ),
        r * totalColumnEnergy (sensMatrix S tk) ≤ keptColumnEnergy (sensMatrix S tk) Sset →
        ∀ η > 0, ∀ᶠ Δθ in 𝓝 (0 : EuclideanSpace ℝ (Fin p)),
          ‖sampled x tk (θ₀ + Δθ) - sampled x tk (θ₀ + keepS Sset Δθ)‖
            ≤ (Real.sqrt ((1 - r) * totalColumnEnergy (sensMatrix S tk)) + η) * ‖Δθ‖ := by
  obtain ⟨S, hS0, hSvar, hSder⟩ :=
    hasFDerivAt_solution_param_init f hU hf hT x θ₀ hγU hsol x0 D0 hx0 hinit
  refine ⟨S, hS0, hSvar, ?_⟩
  -- derivada de cada coordenada muestreada
  set e := (finProdFinEquiv : Fin N × Fin n ≃ Fin (N * n)).symm with he
  set coord : Fin n → (EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ) := fun i =>
    (ContinuousLinearMap.proj i).comp
      ((EuclideanSpace.equiv (Fin n) ℝ : EuclideanSpace ℝ (Fin n) ≃L[ℝ] (Fin n → ℝ)) :
        EuclideanSpace ℝ (Fin n) →L[ℝ] (Fin n → ℝ)) with hcoord
  have hG : HasFDerivAt (fun θ => fun i : Fin (N * n) => x θ (tk (e i).1) (e i).2)
      (ContinuousLinearMap.pi fun i => (coord (e i).2).comp (S (tk (e i).1))) θ₀ := by
    rw [hasFDerivAt_pi]
    intro i
    exact (coord (e i).2).hasFDerivAt.comp θ₀ (hSder _ (htk _))
  set L := ((EuclideanSpace.equiv (Fin (N * n)) ℝ).symm :
      (Fin (N * n) → ℝ) →L[ℝ] EuclideanSpace ℝ (Fin (N * n))).comp
    (ContinuousLinearMap.pi fun i => (coord (e i).2).comp (S (tk (e i).1))) with hL
  have hF : HasFDerivAt (sampled x tk) L θ₀ :=
    (EuclideanSpace.equiv (Fin (N * n)) ℝ).symm.hasFDerivAt.comp θ₀ hG
  have hJ : jacobianOf L = sensMatrix S tk := by
    funext i j; rfl
  intro Sset r hr η hη
  have := trajectory_error_from_Rvar (sampled x tk) L θ₀ hF Sset r (by rwa [hJ]) hη
  simpa [hJ] using this

end CertifiedODEReduction

#print axioms CertifiedODEReduction.certified_parameter_reduction
