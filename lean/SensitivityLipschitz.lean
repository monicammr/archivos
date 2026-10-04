import Mathlib.Analysis.ODE.Gronwall
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Normed.Operator.Prod

/-!
# Cota formal de la constante de Lipschitz de la sensibilidad (`Lc`)

Hipótesis (todas calculables para el modelo): en un conjunto convexo `K ⊆ E × P` que contiene
las trayectorias `(x(θ,t), θ)` para los `θ` considerados, el campo `g(x,θ) = f(x,θ)` es
diferenciable con
* `‖Dg‖ ≤ M₁` (primeras derivadas),
* `‖Dg z − Dg z'‖ ≤ M₂ ‖z − z'‖` (derivada Lipschitz, es decir segundas derivadas acotadas).

Resultados, con `e := exp(M₁ T)`:
1. `traj_lipschitz`: `‖x(θ,t) − x(θ',t)‖ ≤ (e − 1) ‖θ − θ'‖`.
2. `sens_bound`: la sensibilidad cumple `‖S_θ(t)‖ ≤ e − 1`.
3. `sens_lipschitz`: `‖S_θ(t) − S_θ'(t)‖ ≤ M₂ e² (e − 1)/M₁ · ‖θ − θ'‖`.
-/

open Set Filter Topology

namespace SensitivityLipschitz

section Gronwall

variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Grönwall con dato inicial nulo: si `u 0 = 0` y `‖u'‖ ≤ K ‖u‖ + ε` en `[0, T]`, entonces
`‖u t‖ ≤ ε (e^{KT} − 1)/K`. -/
theorem gronwall_zero_init {T K ε : ℝ} (hK : 0 < K) (hε : 0 ≤ ε) (u u' : ℝ → F)
    (hu : ∀ t ∈ Icc 0 T, HasDerivWithinAt u (u' t) (Icc 0 T) t) (h0 : u 0 = 0)
    (hb : ∀ t ∈ Icc 0 T, ‖u' t‖ ≤ K * ‖u t‖ + ε) :
    ∀ t ∈ Icc 0 T, ‖u t‖ ≤ ε * ((Real.exp (K * T) - 1) / K) := by
  intro t ht
  have hc : ContinuousOn u (Icc 0 T) := fun s hs => (hu s hs).continuousWithinAt
  have hIci : ∀ s ∈ Ico 0 T, HasDerivWithinAt u (u' s) (Ici s) s := fun s hs =>
    (hu s (Ico_subset_Icc_self hs)).mono_of_mem_nhdsWithin
      (mem_of_superset (Icc_mem_nhdsGE hs.2) (Icc_subset_Icc hs.1 le_rfl))
  have key := norm_le_gronwallBound_of_norm_deriv_right_le hc hIci (by rw [h0, norm_zero])
    (fun s hs => hb s (Ico_subset_Icc_self hs)) t ht
  rw [gronwallBound_of_K_ne_0 hK.ne'] at key
  simp only [zero_mul, zero_add, sub_zero] at key
  have hexp : Real.exp (K * t) ≤ Real.exp (K * T) :=
    Real.exp_le_exp.2 (mul_le_mul_of_nonneg_left ht.2 hK.le)
  calc ‖u t‖ ≤ ε / K * (Real.exp (K * t) - 1) := key
    _ ≤ ε / K * (Real.exp (K * T) - 1) :=
        mul_le_mul_of_nonneg_left (by linarith) (div_nonneg hε hK.le)
    _ = ε * ((Real.exp (K * T) - 1) / K) := by ring

end Gronwall

section Main

variable {E P : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup P] [NormedSpace ℝ P]

lemma norm_comp_inl_le (L : E × P →L[ℝ] E) :
    ‖L.comp (ContinuousLinearMap.inl ℝ E P)‖ ≤ ‖L‖ := by
  refine ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg _) fun u => ?_
  simp only [ContinuousLinearMap.comp_apply, ContinuousLinearMap.inl_apply]
  calc ‖L (u, 0)‖ ≤ ‖L‖ * ‖(u, (0 : P))‖ := L.le_opNorm _
    _ = ‖L‖ * ‖u‖ := by simp

lemma norm_comp_inr_le (L : E × P →L[ℝ] E) :
    ‖L.comp (ContinuousLinearMap.inr ℝ E P)‖ ≤ ‖L‖ := by
  refine ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg _) fun u => ?_
  simp only [ContinuousLinearMap.comp_apply, ContinuousLinearMap.inr_apply]
  calc ‖L (0, u)‖ ≤ ‖L‖ * ‖((0 : E), u)‖ := L.le_opNorm _
    _ = ‖L‖ * ‖u‖ := by simp

variable (g : E × P → E) (Dg : E × P → (E × P →L[ℝ] E)) (K : Set (E × P))
  {M₁ M₂ T : ℝ}

/-- `g` es `M₁`-Lipschitz en el convexo `K`. -/
lemma g_lipschitz (hK : Convex ℝ K) (hdiff : ∀ z ∈ K, HasFDerivAt g (Dg z) z)
    (hM1 : ∀ z ∈ K, ‖Dg z‖ ≤ M₁) {z z' : E × P} (hz : z ∈ K) (hz' : z' ∈ K) :
    ‖g z - g z'‖ ≤ M₁ * ‖z - z'‖ :=
  hK.norm_image_sub_le_of_norm_hasFDerivWithin_le
    (fun w hw => (hdiff w hw).hasFDerivWithinAt) hM1 hz' hz

lemma norm_pair_sub_le (a a' : E) (b b' : P) :
    ‖((a, b) : E × P) - (a', b')‖ ≤ ‖a - a'‖ + ‖b - b'‖ := by
  rw [Prod.mk_sub_mk, Prod.norm_mk]
  exact max_le (le_add_of_nonneg_right (norm_nonneg _)) (le_add_of_nonneg_left (norm_nonneg _))

/-- **1. Las trayectorias son Lipschitz en θ**: `‖x(θ,t) − x(θ',t)‖ ≤ (e^{M₁T} − 1) ‖θ − θ'‖`. -/
theorem traj_lipschitz (hK : Convex ℝ K) (hdiff : ∀ z ∈ K, HasFDerivAt g (Dg z) z)
    (hM₁ : 0 < M₁) (hM1 : ∀ z ∈ K, ‖Dg z‖ ≤ M₁)
    (x : P → ℝ → E) (θ θ' : P)
    (hsol : ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (g (x θ t, θ)) (Icc 0 T) t)
    (hsol' : ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ') (g (x θ' t, θ')) (Icc 0 T) t)
    (hinit : x θ 0 = x θ' 0)
    (hKθ : ∀ t ∈ Icc 0 T, (x θ t, θ) ∈ K) (hKθ' : ∀ t ∈ Icc 0 T, (x θ' t, θ') ∈ K) :
    ∀ t ∈ Icc 0 T, ‖x θ t - x θ' t‖ ≤ ‖θ - θ'‖ * (Real.exp (M₁ * T) - 1) := by
  intro t ht
  have key := gronwall_zero_init (u := fun s => x θ s - x θ' s)
    (u' := fun s => g (x θ s, θ) - g (x θ' s, θ')) (ε := M₁ * ‖θ - θ'‖) hM₁
    (by positivity) (fun s hs => (hsol s hs).sub (hsol' s hs)) (by simp [hinit])
    (fun s hs => by
      have := g_lipschitz g Dg K hK hdiff hM1 (hKθ s hs) (hKθ' s hs)
      have h2 := norm_pair_sub_le (x θ s) (x θ' s) θ θ'
      calc ‖g (x θ s, θ) - g (x θ' s, θ')‖ ≤ M₁ * ‖((x θ s, θ) : E × P) - (x θ' s, θ')‖ := this
        _ ≤ M₁ * (‖x θ s - x θ' s‖ + ‖θ - θ'‖) := mul_le_mul_of_nonneg_left h2 hM₁.le
        _ = M₁ * ‖x θ s - x θ' s‖ + M₁ * ‖θ - θ'‖ := by ring) t ht
  calc _ ≤ M₁ * ‖θ - θ'‖ * ((Real.exp (M₁ * T) - 1) / M₁) := key
    _ = ‖θ - θ'‖ * (Real.exp (M₁ * T) - 1) := by field_simp

/-- **2. La sensibilidad está acotada**: `‖S_θ(t)‖ ≤ e^{M₁T} − 1`. -/
theorem sens_bound (hM₁ : 0 < M₁) (hM1 : ∀ z ∈ K, ‖Dg z‖ ≤ M₁)
    (xθ : ℝ → E) (θ : P) (S : ℝ → (P →L[ℝ] E))
    (hS : ∀ t ∈ Icc 0 T, HasDerivWithinAt S
      ((Dg (xθ t, θ)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S t
        + (Dg (xθ t, θ)).comp (ContinuousLinearMap.inr ℝ E P)) (Icc 0 T) t)
    (hS0 : S 0 = 0) (hKθ : ∀ t ∈ Icc 0 T, (xθ t, θ) ∈ K) :
    ∀ t ∈ Icc 0 T, ‖S t‖ ≤ Real.exp (M₁ * T) - 1 := by
  intro t ht
  have key := gronwall_zero_init (ε := M₁) hM₁ hM₁.le S _ hS hS0 (fun s hs => by
    have hA := (norm_comp_inl_le (Dg (xθ s, θ))).trans (hM1 _ (hKθ s hs))
    have hB := (norm_comp_inr_le (Dg (xθ s, θ))).trans (hM1 _ (hKθ s hs))
    calc _ ≤ ‖(Dg (xθ s, θ)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S s‖
          + ‖(Dg (xθ s, θ)).comp (ContinuousLinearMap.inr ℝ E P)‖ := norm_add_le _ _
      _ ≤ ‖(Dg (xθ s, θ)).comp (ContinuousLinearMap.inl ℝ E P)‖ * ‖S s‖ + M₁ :=
          add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) hB
      _ ≤ M₁ * ‖S s‖ + M₁ := by
          gcongr) t ht
  calc _ ≤ M₁ * ((Real.exp (M₁ * T) - 1) / M₁) := key
    _ = Real.exp (M₁ * T) - 1 := by field_simp

/-- **3. La sensibilidad es Lipschitz en θ**:
`‖S_θ(t) − S_θ'(t)‖ ≤ M₂ e^{2M₁T} (e^{M₁T} − 1)/M₁ · ‖θ − θ'‖`. -/
theorem sens_lipschitz (hK : Convex ℝ K) (hdiff : ∀ z ∈ K, HasFDerivAt g (Dg z) z)
    (hM₁ : 0 < M₁) (hM₂ : 0 ≤ M₂) (hM1 : ∀ z ∈ K, ‖Dg z‖ ≤ M₁)
    (hM2 : ∀ z ∈ K, ∀ z' ∈ K, ‖Dg z - Dg z'‖ ≤ M₂ * ‖z - z'‖)
    (x : P → ℝ → E) (θ θ' : P)
    (hsol : ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (g (x θ t, θ)) (Icc 0 T) t)
    (hsol' : ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ') (g (x θ' t, θ')) (Icc 0 T) t)
    (hinit : x θ 0 = x θ' 0)
    (hKθ : ∀ t ∈ Icc 0 T, (x θ t, θ) ∈ K) (hKθ' : ∀ t ∈ Icc 0 T, (x θ' t, θ') ∈ K)
    (S S' : ℝ → (P →L[ℝ] E))
    (hS : ∀ t ∈ Icc 0 T, HasDerivWithinAt S
      ((Dg (x θ t, θ)).comp (ContinuousLinearMap.inl ℝ E P) ∘L S t
        + (Dg (x θ t, θ)).comp (ContinuousLinearMap.inr ℝ E P)) (Icc 0 T) t)
    (hS' : ∀ t ∈ Icc 0 T, HasDerivWithinAt S'
      ((Dg (x θ' t, θ')).comp (ContinuousLinearMap.inl ℝ E P) ∘L S' t
        + (Dg (x θ' t, θ')).comp (ContinuousLinearMap.inr ℝ E P)) (Icc 0 T) t)
    (hS0 : S 0 = 0) (hS0' : S' 0 = 0) :
    ∀ t ∈ Icc 0 T, ‖S t - S' t‖ ≤ ‖θ - θ'‖ *
      (M₂ * Real.exp (M₁ * T) * Real.exp (M₁ * T) * ((Real.exp (M₁ * T) - 1) / M₁)) := by
  have hT0 : ∀ t ∈ Icc 0 T, 0 ≤ T := fun t ht => ht.1.trans ht.2
  set e := Real.exp (M₁ * T) with he
  have hx := traj_lipschitz g Dg K hK hdiff hM₁ hM1 x θ θ' hsol hsol' hinit hKθ hKθ'
  have hSb := sens_bound Dg K hM₁ hM1 (x θ') θ' S' hS' hS0' hKθ'
  intro t ht
  have he1 : 1 ≤ e := Real.one_le_exp (mul_nonneg hM₁.le (hT0 t ht))
  have key := gronwall_zero_init (ε := M₂ * ‖θ - θ'‖ * e * e) hM₁ (by positivity)
    (fun s => S s - S' s) _ (fun s hs => (hS s hs).sub (hS' s hs)) (by simp [hS0, hS0'])
    (fun s hs => by
      set z := ((x θ s, θ) : E × P)
      set z' := ((x θ' s, θ') : E × P)
      have hz : ‖z - z'‖ ≤ ‖θ - θ'‖ * e := by
        have := norm_pair_sub_le (x θ s) (x θ' s) θ θ'
        have h1 := hx s hs
        calc ‖z - z'‖ ≤ ‖x θ s - x θ' s‖ + ‖θ - θ'‖ := this
          _ ≤ ‖θ - θ'‖ * (e - 1) + ‖θ - θ'‖ := by linarith
          _ = ‖θ - θ'‖ * e := by ring
      have hD : ‖Dg z - Dg z'‖ ≤ M₂ * (‖θ - θ'‖ * e) :=
        (hM2 z (hKθ s hs) z' (hKθ' s hs)).trans (mul_le_mul_of_nonneg_left hz hM₂)
      have hA := (norm_comp_inl_le (Dg z)).trans (hM1 _ (hKθ s hs))
      have e1 : ((Dg z).comp (ContinuousLinearMap.inl ℝ E P) ∘L S s
            + (Dg z).comp (ContinuousLinearMap.inr ℝ E P))
          - ((Dg z').comp (ContinuousLinearMap.inl ℝ E P) ∘L S' s
            + (Dg z').comp (ContinuousLinearMap.inr ℝ E P))
          = (Dg z).comp (ContinuousLinearMap.inl ℝ E P) ∘L (S s - S' s)
            + (Dg z - Dg z').comp (ContinuousLinearMap.inl ℝ E P) ∘L S' s
            + (Dg z - Dg z').comp (ContinuousLinearMap.inr ℝ E P) := by
        simp only [ContinuousLinearMap.comp_sub, ContinuousLinearMap.sub_comp]; abel
      rw [e1]
      have hS's : ‖S' s‖ ≤ e - 1 := hSb s hs
      have t1 : ‖(Dg z).comp (ContinuousLinearMap.inl ℝ E P) ∘L (S s - S' s)‖
          ≤ M₁ * ‖S s - S' s‖ :=
        (ContinuousLinearMap.opNorm_comp_le _ _).trans
          (mul_le_mul_of_nonneg_right hA (norm_nonneg _))
      have t2 : ‖(Dg z - Dg z').comp (ContinuousLinearMap.inl ℝ E P) ∘L S' s‖
          ≤ M₂ * (‖θ - θ'‖ * e) * (e - 1) :=
        (ContinuousLinearMap.opNorm_comp_le _ _).trans
          (mul_le_mul ((norm_comp_inl_le _).trans hD) hS's (norm_nonneg _) (by positivity))
      have t3 : ‖(Dg z - Dg z').comp (ContinuousLinearMap.inr ℝ E P)‖
          ≤ M₂ * (‖θ - θ'‖ * e) := (norm_comp_inr_le _).trans hD
      calc _ ≤ ‖(Dg z).comp (ContinuousLinearMap.inl ℝ E P) ∘L (S s - S' s)‖
            + ‖(Dg z - Dg z').comp (ContinuousLinearMap.inl ℝ E P) ∘L S' s‖
            + ‖(Dg z - Dg z').comp (ContinuousLinearMap.inr ℝ E P)‖ :=
            (norm_add_le _ _).trans (add_le_add_right (norm_add_le _ _) _)
        _ ≤ M₁ * ‖S s - S' s‖ + M₂ * (‖θ - θ'‖ * e) * (e - 1) + M₂ * (‖θ - θ'‖ * e) := by
            linarith
        _ = M₁ * ‖S s - S' s‖ + M₂ * ‖θ - θ'‖ * e * e := by ring) t ht
  calc _ ≤ M₂ * ‖θ - θ'‖ * e * e * ((e - 1) / M₁) := key
    _ = _ := by ring

end Main

end SensitivityLipschitz

