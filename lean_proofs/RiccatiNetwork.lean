import KineticNetwork

/-!
# Existencia en un horizonte finito con crecimiento cuadrático (cota de Riccati)

Algunos modelos crecen de forma superlineal (p. ej. un patógeno que se replica como `ρ·P²`):
la solución puede explotar en tiempo finito y la existencia global no es cierta en general. Pero
sí se puede garantizar en un horizonte `[0, T]` suficientemente corto.

`exists_solution_riccati`: si `v` es C¹ en un abierto que contiene el ortante, cuasi-positivo, y
con pesos `cᵢ ≥ c_min > 0` se cumple `Σ cᵢ vᵢ(z) ≤ Q (Σ cᵢ zᵢ + 1)²` en el ortante, entonces
la solución existe en `[0, T]` (y es `≥ 0`) siempre que `(1 + δ)·Q·(φ₀ + 1)·T < 1`, con
`φ₀ = Σ cᵢ xᵢ(0)`. Prueba: truncamiento a una caja, y comparación de `ψ = φ + 1` con la
solución `R(t) = W/(1 − κt)` de `R' = (1+δ)Q R²`, `κ = (1+δ)QW`, `W = φ₀ + 1`.

Para una red concreta la constante `Q` se calcula **en racionales** (`checkRiccati`): cada término
con peso positivo se acota por `A + Bφ + Cφ²` (`quadC`, `quadV`), usando `yⱼ ≤ φ/cⱼ`.
`riccati_final`: teorema final para `T ≤ T_q`, sin condiciones pendientes.
-/

open Set Filter Topology Metric NNReal KineticRegularity PositivityInvariance KineticCheck
  KineticCheck.KExpr' KineticNetwork GlobalExistence ODEParamDiff

namespace RiccatiNetwork

variable {n p : ℕ}

/-- **Existencia en `[0, T]` con crecimiento cuadrático.** -/
theorem exists_solution_riccati (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    {U : Set (EuclideanSpace ℝ (Fin n))} (hU : IsOpen U) (hv : ContDiffOn ℝ 1 v U)
    (horth : ∀ z, Nonneg z → z ∈ U)
    (hqp : ∀ z, Nonneg z → ∀ i, z i = 0 → 0 ≤ v z i)
    (c : Fin n → ℝ) {cmin Q δ : ℝ} (hcmin : 0 < cmin) (hc : ∀ i, cmin ≤ c i)
    (hQ : 0 < Q) (hδ : 0 < δ)
    (hgrowth : ∀ z, Nonneg z → ∑ i, c i * v z i ≤ Q * (∑ i, c i * z i + 1) ^ 2)
    (x0 : EuclideanSpace ℝ (Fin n)) (hx0 : Nonneg x0) {T : ℝ} (hT : 0 ≤ T)
    (hblow : (1 + δ) * Q * (∑ i, c i * x0 i + 1) * T < 1) :
    ∃ x : ℝ → EuclideanSpace ℝ (Fin n), x 0 = x0 ∧
      ∀ t ∈ Icc 0 T, HasDerivWithinAt x (v (x t)) (Icc 0 T) t ∧ Nonneg (x t) := by
  have hcpos : ∀ i, 0 < c i := fun i => hcmin.trans_le (hc i)
  set φ0 : ℝ := ∑ i, c i * x0 i with hφ0
  have hφ0 : 0 ≤ φ0 := Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hx0 i)
  set W : ℝ := φ0 + 1 with hW
  have hWpos : 0 < W := by rw [hW]; linarith
  set κ : ℝ := (1 + δ) * Q * W with hκ
  have hκpos : 0 < κ := mul_pos (mul_pos (by linarith) hQ) hWpos
  have hκT : κ * T < 1 := by rw [hκ]; exact hblow
  have hden : ∀ t ∈ Icc 0 T, 0 < 1 - κ * t := fun t ht => by
    have : κ * t ≤ κ * T := mul_le_mul_of_nonneg_left ht.2 hκpos.le
    linarith
  set R : ℝ → ℝ := fun t => W / (1 - κ * t) with hR
  set M : ℝ := W / (1 - κ * T) - 1 with hM
  have hRle : ∀ t ∈ Icc 0 T, R t ≤ W / (1 - κ * T) := fun t ht =>
    div_le_div_of_nonneg_left hWpos.le (hden T ⟨hT, le_rfl⟩)
      (by have := mul_le_mul_of_nonneg_left ht.2 hκpos.le; linarith)
  have hWle : W ≤ W / (1 - κ * T) := by
    rw [le_div_iff₀ (hden T ⟨hT, le_rfl⟩)]
    nlinarith [mul_nonneg hκpos.le hT]
  have hM0 : 0 ≤ M := by rw [hM]; linarith
  set B : ℝ := M / cmin + 1 with hB
  have hB0 : 0 ≤ B := by rw [hB]; have := div_nonneg hM0 hcmin.le; linarith
  have hbox : box B ⊆ U := fun z hz => horth z hz.1
  obtain ⟨L, hL⟩ := lipschitzOn_box v hU hv B hbox
  set w : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n) := fun z => v (clampB B z)
    with hw
  have hwLip : LipschitzWith L w := LipschitzWith.of_dist_le_mul fun y y' => by
    have := hL.dist_le_mul _ (clampB_mem hB0 y) _ (clampB_mem hB0 y')
    exact this.trans (mul_le_mul_of_nonneg_left (dist_clampB_le B y y') L.2)
  obtain ⟨α, hα0, hαsol⟩ := exists_solution_Icc (fun _ => w) L hT (fun _ _ => hwLip)
    (fun _ => continuousOn_const) x0
  have hα : ∀ t ∈ Icc 0 T, HasDerivWithinAt α (w (α t)) (Icc 0 T) t := hαsol
  have hnn : ∀ t ∈ Icc 0 T, Nonneg (α t) := by
    refine nonneg_core w α (K := 0) le_rfl hα (by rw [hα0]; exact hx0) ?_ ?_
    · intro t _
      have : w (pos (α t)) = w (α t) := by simp only [hw, clampB_pos]
      rw [this, sub_self, norm_zero]; positivity
    · intro t _ i hi
      have hy : clampB B (pos (α t)) i = 0 := by
        rw [clampB_apply, hi, min_eq_right hB0, max_self]
      exact hqp _ (clampB_nonneg _ _) i hy
  set φ : ℝ → ℝ := fun t => ∑ i, c i * α t i with hφdef
  set φ' : ℝ → ℝ := fun t => ∑ i, c i * w (α t) i with hφ'def
  have hφd : ∀ t ∈ Icc 0 T, HasDerivWithinAt φ (φ' t) (Icc 0 T) t := by
    intro t ht
    apply HasDerivWithinAt.fun_sum
    intro i _
    have hxi : HasDerivWithinAt (fun t => α t i) (w (α t) i) (Icc 0 T) t := by
      have := (EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).hasFDerivAt
        |>.comp_hasDerivWithinAt t (hα t ht)
      simpa using this
    exact hxi.const_mul (c i)
  have hφ0' : ∀ t ∈ Icc 0 T, 0 ≤ φ t := fun t ht =>
    Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (hnn t ht i)
  have hbound : ∀ t ∈ Icc 0 T, φ' t ≤ Q * (φ t + 1) ^ 2 := by
    intro t ht
    have h1 := hgrowth (clampB B (α t)) (clampB_nonneg _ _)
    have h2 : ∑ i, c i * clampB B (α t) i ≤ φ t := by
      apply Finset.sum_le_sum
      intro i _
      apply mul_le_mul_of_nonneg_left _ (hcpos i).le
      rw [clampB_apply]
      exact max_le (hnn t ht i) (min_le_right _ _)
    have h0 : 0 ≤ ∑ i, c i * clampB B (α t) i :=
      Finset.sum_nonneg fun i _ => mul_nonneg (hcpos i).le (clampB_nonneg _ _ i)
    have h3 : (∑ i, c i * clampB B (α t) i + 1) ^ 2 ≤ (φ t + 1) ^ 2 :=
      pow_le_pow_left₀ (by linarith) (by linarith) 2
    show ∑ i, c i * v (clampB B (α t)) i ≤ Q * (φ t + 1) ^ 2
    exact h1.trans (mul_le_mul_of_nonneg_left h3 hQ.le)
  have hIci : ∀ t ∈ Ico 0 T, Icc 0 T ∈ 𝓝[Ici t] t := fun t ht =>
    mem_of_superset (Icc_mem_nhdsGE ht.2) (Icc_subset_Icc ht.1 le_rfl)
  -- derivada de la frontera R
  have hRd : ∀ t ∈ Icc 0 T, HasDerivAt R (W * κ / (1 - κ * t) ^ 2) t := by
    intro t ht
    have hg : HasDerivAt (fun t : ℝ => 1 - κ * t) (-κ) t := by
      simpa using ((hasDerivAt_id t).const_mul κ).const_sub 1
    have := (hasDerivAt_const t W).div hg (hden t ht).ne'
    convert this using 1
    ring
  have hcomp := image_le_of_deriv_right_lt_deriv_boundary' (a := 0) (b := T)
    (f := fun t => φ t + 1) (f' := φ') (B := R) (B' := fun t => W * κ / (1 - κ * t) ^ 2)
    (fun t ht => ((hφd t ht).add_const 1).continuousWithinAt)
    (fun t ht => ((hφd t (Ico_subset_Icc_self ht)).add_const 1).mono_of_mem_nhdsWithin
      (hIci t ht))
    (by
      show φ 0 + 1 ≤ W / (1 - κ * 0)
      rw [mul_zero, sub_zero, div_one]
      show ∑ i, c i * α 0 i + 1 ≤ W
      rw [hα0])
    (fun t ht => (hRd t ht).continuousAt.continuousWithinAt)
    (fun t ht => (hRd t (Ico_subset_Icc_self ht)).hasDerivWithinAt)
    (by
      intro t ht heq
      have ht' := Ico_subset_Icc_self ht
      have hd := hden t ht'
      have hRpos : 0 < R t := div_pos hWpos hd
      have e1 : W * κ / (1 - κ * t) ^ 2 = (1 + δ) * Q * R t ^ 2 := by
        simp only [hR, hκ]; field_simp
      have e2 : φ t + 1 = R t := heq
      have := hbound t ht'
      rw [e2] at this
      show φ' t < W * κ / (1 - κ * t) ^ 2
      rw [e1]
      have : Q * R t ^ 2 < (1 + δ) * Q * R t ^ 2 := by
        have : 0 < δ * Q * R t ^ 2 := by positivity
        nlinarith
      linarith)
  have hφM : ∀ t ∈ Icc 0 T, φ t ≤ M := by
    intro t ht
    have := hcomp ht
    have := hRle t ht
    simp only at *
    rw [hM]; linarith
  have hbelow : ∀ t ∈ Icc 0 T, ∀ i, α t i ≤ B := by
    intro t ht i
    have h1 : c i * α t i ≤ φ t :=
      Finset.single_le_sum (f := fun j => c j * α t j)
        (fun j _ => mul_nonneg (hcpos j).le (hnn t ht j)) (Finset.mem_univ i)
    have h2 : cmin * α t i ≤ c i * α t i := mul_le_mul_of_nonneg_right (hc i) (hnn t ht i)
    have h3 : α t i ≤ M / cmin := by
      rw [le_div_iff₀ hcmin]; linarith [hφM t ht]
    rw [hB]; linarith
  refine ⟨α, hα0, fun t ht => ⟨?_, hnn t ht⟩⟩
  have : w (α t) = v (α t) := by
    simp only [hw]; rw [clampB_eq (hnn t ht) (hbelow t ht)]
  rw [← this]; exact hα t ht

/-! ## Cotas racionales calculables -/

/-- Expresión sin concentraciones en el fragmento racional (`+ − × / ^n`, constantes, θ). -/
def qc : KExpr n p → Bool
  | .qconst _ => true
  | .par _ => true
  | .add a b => qc a && qc b
  | .sub a b => qc a && qc b
  | .mul a b => qc a && qc b
  | .div a b => qc a && qc b
  | .npow a _ => qc a
  | _ => false

/-- Su valor racional en `θ = θq`. -/
def qval (θq : Fin p → ℚ) : KExpr n p → ℚ
  | .qconst q => q
  | .par j => θq j
  | .add a b => qval θq a + qval θq b
  | .sub a b => qval θq a - qval θq b
  | .mul a b => qval θq a * qval θq b
  | .div a b => qval θq a / qval θq b
  | .npow a k => qval θq a ^ k
  | _ => 0

theorem qval_sound (θq : Fin p → ℚ) (y : EuclideanSpace ℝ (Fin n)) :
    ∀ e : KExpr n p, qc e = true → e.eval (y, qvec θq) = (qval θq e : ℝ) := by
  intro e
  induction e with
  | qconst q => intro _; rfl
  | par j => intro _; rfl
  | add a b ha hb =>
      intro h; simp only [qc, Bool.and_eq_true] at h
      show a.eval _ + b.eval _ = _; rw [ha h.1, hb h.2]; simp [qval]
  | sub a b ha hb =>
      intro h; simp only [qc, Bool.and_eq_true] at h
      show a.eval _ - b.eval _ = _; rw [ha h.1, hb h.2]; simp [qval]
  | mul a b ha hb =>
      intro h; simp only [qc, Bool.and_eq_true] at h
      show a.eval _ * b.eval _ = _; rw [ha h.1, hb h.2]; simp [qval]
  | div a b ha hb =>
      intro h; simp only [qc, Bool.and_eq_true] at h
      show a.eval _ / b.eval _ = _; rw [ha h.1, hb h.2]; simp [qval]
  | npow a k ha =>
      intro h; simp only [qc] at h
      show a.eval _ ^ k = _; rw [ha h]; simp [qval]
  | const _ => intro h; simp [qc] at h
  | var _ => intro h; simp [qc] at h
  | rpow _ _ _ => intro h; simp [qc] at h
  | exp _ _ => intro h; simp [qc] at h
  | log _ _ => intro h; simp [qc] at h

/-- Constante racional `≥ 0`. -/
def qnn (θq : Fin p → ℚ) (e : KExpr n p) : Bool := qc e && decide (0 ≤ qval θq e)

lemma qnn_sound {θq : Fin p → ℚ} {e : KExpr n p} (h : qnn θq e = true)
    (y : EuclideanSpace ℝ (Fin n)) :
    e.eval (y, qvec θq) = (qval θq e : ℝ) ∧ (0 : ℝ) ≤ qval θq e := by
  simp only [qnn, Bool.and_eq_true, decide_eq_true_eq] at h
  exact ⟨qval_sound θq y e h.1, by exact_mod_cast h.2⟩

/-- Combinación ponderada `φ = Σ cᵢ yᵢ`. -/
noncomputable def phi (c : Fin n → ℚ) (y : EuclideanSpace ℝ (Fin n)) : ℝ :=
  ∑ i, (c i : ℝ) * y i

/-- Cota lineal `0 ≤ e ≤ A + B·φ`. -/
def linC (θq : Fin p → ℚ) : KExpr n p → Bool
  | .var _ => true
  | .add a b => linC θq a && linC θq b
  | .mul a b => (qnn θq a && linC θq b) || (linC θq a && qnn θq b)
  | e => qnn θq e

def linV (c : Fin n → ℚ) (θq : Fin p → ℚ) : KExpr n p → ℚ × ℚ
  | .var j => (0, 1 / c j)
  | .add a b => ((linV c θq a).1 + (linV c θq b).1, (linV c θq a).2 + (linV c θq b).2)
  | .mul a b =>
      if qnn θq a && linC θq b then (qval θq a * (linV c θq b).1, qval θq a * (linV c θq b).2)
      else ((linV c θq a).1 * qval θq b, (linV c θq a).2 * qval θq b)
  | e => (qval θq e, 0)

variable {c : Fin n → ℚ} {θq : Fin p → ℚ} {y : EuclideanSpace ℝ (Fin n)}

lemma var_le_phi (hc : ∀ i, 0 < c i) (hy : Nonneg y) (j : Fin n) :
    y j ≤ ((1 / c j : ℚ) : ℝ) * phi c y := by
  have hcj : (0 : ℝ) < c j := by exact_mod_cast hc j
  have h1 : (c j : ℝ) * y j ≤ phi c y :=
    Finset.single_le_sum (f := fun i => (c i : ℝ) * y i)
      (fun i _ => mul_nonneg (by exact_mod_cast (hc i).le) (hy i)) (Finset.mem_univ j)
  push_cast
  rw [one_div, inv_mul_eq_div, le_div_iff₀ hcj]
  linarith

theorem linV_sound (hc : ∀ i, 0 < c i) (hy : Nonneg y) :
    ∀ e : KExpr n p, linC θq e = true →
      (0 : ℝ) ≤ (linV c θq e).1 ∧ (0 : ℝ) ≤ (linV c θq e).2 ∧
      0 ≤ e.eval (y, qvec θq) ∧
      e.eval (y, qvec θq) ≤ (linV c θq e).1 + ((linV c θq e).2 : ℝ) * phi c y := by
  have hphi : 0 ≤ phi c y :=
    Finset.sum_nonneg fun i _ => mul_nonneg (by exact_mod_cast (hc i).le) (hy i)
  have cst : ∀ e : KExpr n p, qnn θq e = true →
      (0 : ℝ) ≤ (qval θq e : ℝ) ∧ (0 : ℝ) ≤ ((0 : ℚ) : ℝ) ∧ 0 ≤ e.eval (y, qvec θq) ∧
      e.eval (y, qvec θq) ≤ (qval θq e : ℝ) + ((0 : ℚ) : ℝ) * phi c y := by
    intro e h
    obtain ⟨h1, h2⟩ := qnn_sound h y
    refine ⟨h2, by simp, by rw [h1]; exact h2, by rw [h1]; simp⟩
  intro e
  induction e with
  | var j =>
      intro _
      refine ⟨by simp [linV], ?_, hy j, ?_⟩
      · show (0 : ℝ) ≤ ((1 / c j : ℚ) : ℝ)
        have := hc j; positivity
      · show y j ≤ ((0 : ℚ) : ℝ) + ((1 / c j : ℚ) : ℝ) * phi c y
        rw [Rat.cast_zero, zero_add]; exact var_le_phi hc hy j
  | add a b ha hb =>
      intro h; simp only [linC, Bool.and_eq_true] at h
      obtain ⟨a1, a2, a3, a4⟩ := ha h.1
      obtain ⟨b1, b2, b3, b4⟩ := hb h.2
      simp only [linV, Rat.cast_add]
      refine ⟨by linarith, by linarith, add_nonneg a3 b3, ?_⟩
      show a.eval _ + b.eval _ ≤ _
      nlinarith
  | mul a b ha hb =>
      intro h
      simp only [linV]
      by_cases h1 : (qnn θq a && linC θq b) = true
      · rw [if_pos h1]
        simp only [Bool.and_eq_true] at h1
        obtain ⟨e1, e2⟩ := qnn_sound h1.1 y
        obtain ⟨b1, b2, b3, b4⟩ := hb h1.2
        simp only [Rat.cast_mul]
        refine ⟨mul_nonneg e2 b1, mul_nonneg e2 b2, ?_, ?_⟩
        · show 0 ≤ a.eval _ * b.eval _; rw [e1]; exact mul_nonneg e2 b3
        · show a.eval _ * b.eval _ ≤ _; rw [e1]
          nlinarith [mul_le_mul_of_nonneg_left b4 e2]
      · rw [if_neg h1]
        simp only [linC, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · exact absurd (by simp [h.1, h.2]) h1
        obtain ⟨e1, e2⟩ := qnn_sound h.2 y
        obtain ⟨a1, a2, a3, a4⟩ := ha h.1
        simp only [Rat.cast_mul]
        refine ⟨mul_nonneg a1 e2, mul_nonneg a2 e2, ?_, ?_⟩
        · show 0 ≤ a.eval _ * b.eval _; rw [e1]; exact mul_nonneg a3 e2
        · show a.eval _ * b.eval _ ≤ _; rw [e1]
          nlinarith [mul_le_mul_of_nonneg_right a4 e2]
  | qconst q => intro h; exact cst _ (by simpa only [linC] using h)
  | par j => intro h; exact cst _ (by simpa only [linC] using h)
  | const r => intro h; exact cst _ (by simpa only [linC] using h)
  | sub a b _ _ => intro h; exact cst _ (by simpa only [linC] using h)
  | div a b _ _ => intro h; exact cst _ (by simpa only [linC] using h)
  | npow a k _ => intro h; exact cst _ (by simpa only [linC] using h)
  | rpow a r _ => intro h; exact cst _ (by simpa only [linC] using h)
  | exp a _ => intro h; exact cst _ (by simpa only [linC] using h)
  | log a _ => intro h; exact cst _ (by simpa only [linC] using h)

variable (θq) in
/-- Cota cuadrática `0 ≤ e ≤ A + B·φ + C·φ²`. -/
def quadC : KExpr n p → Bool
  | .mul a b => (linC θq a && linC θq b) || (quadC a && qnn θq b) || (qnn θq a && quadC b)
  | .npow a k => decide (k = 2) && linC θq a
  | e => linC θq e

/-- Producto de dos cotas lineales. -/
def prodV (u v : ℚ × ℚ) : ℚ × ℚ × ℚ := (u.1 * v.1, u.1 * v.2 + v.1 * u.2, u.2 * v.2)

variable (c θq) in
def quadV : KExpr n p → ℚ × ℚ × ℚ
  | .mul a b =>
      if linC θq a && linC θq b then prodV (linV c θq a) (linV c θq b)
      else if quadC θq a && qnn θq b then
        ((quadV a).1 * qval θq b, (quadV a).2.1 * qval θq b, (quadV a).2.2 * qval θq b)
      else (qval θq a * (quadV b).1, qval θq a * (quadV b).2.1, qval θq a * (quadV b).2.2)
  | .npow a _ => prodV (linV c θq a) (linV c θq a)
  | e => ((linV c θq e).1, (linV c θq e).2, 0)

lemma prodV_sound {a b : ℝ} {u v : ℚ × ℚ} {φ : ℝ} (hφ : 0 ≤ φ)
    (hu : (0 : ℝ) ≤ u.1 ∧ (0 : ℝ) ≤ u.2 ∧ 0 ≤ a ∧ a ≤ u.1 + (u.2 : ℝ) * φ)
    (hv : (0 : ℝ) ≤ v.1 ∧ (0 : ℝ) ≤ v.2 ∧ 0 ≤ b ∧ b ≤ v.1 + (v.2 : ℝ) * φ) :
    (0 : ℝ) ≤ (prodV u v).1 ∧ (0 : ℝ) ≤ (prodV u v).2.1 ∧ (0 : ℝ) ≤ (prodV u v).2.2 ∧
      0 ≤ a * b ∧
      a * b ≤ (prodV u v).1 + ((prodV u v).2.1 : ℝ) * φ + ((prodV u v).2.2 : ℝ) * φ ^ 2 := by
  obtain ⟨u1, u2, a0, au⟩ := hu
  obtain ⟨v1, v2, b0, bv⟩ := hv
  simp only [prodV, Rat.cast_mul, Rat.cast_add]
  refine ⟨mul_nonneg u1 v1, add_nonneg (mul_nonneg u1 v2) (mul_nonneg v1 u2), mul_nonneg u2 v2,
    mul_nonneg a0 b0, ?_⟩
  have := mul_le_mul au bv b0 (by positivity)
  nlinarith

theorem quadV_sound (hc : ∀ i, 0 < c i) (hy : Nonneg y) :
    ∀ e : KExpr n p, quadC θq e = true →
      (0 : ℝ) ≤ (quadV c θq e).1 ∧ (0 : ℝ) ≤ (quadV c θq e).2.1 ∧
      (0 : ℝ) ≤ (quadV c θq e).2.2 ∧ 0 ≤ e.eval (y, qvec θq) ∧
      e.eval (y, qvec θq) ≤ (quadV c θq e).1 + ((quadV c θq e).2.1 : ℝ) * phi c y +
        ((quadV c θq e).2.2 : ℝ) * phi c y ^ 2 := by
  have hphi : 0 ≤ phi c y :=
    Finset.sum_nonneg fun i _ => mul_nonneg (by exact_mod_cast (hc i).le) (hy i)
  have lin : ∀ e : KExpr n p, linC θq e = true →
      (0 : ℝ) ≤ ((linV c θq e).1 : ℝ) ∧ (0 : ℝ) ≤ ((linV c θq e).2 : ℝ) ∧
      (0 : ℝ) ≤ ((0 : ℚ) : ℝ) ∧ 0 ≤ e.eval (y, qvec θq) ∧
      e.eval (y, qvec θq) ≤ ((linV c θq e).1 : ℝ) + ((linV c θq e).2 : ℝ) * phi c y +
        ((0 : ℚ) : ℝ) * phi c y ^ 2 := by
    intro e h
    obtain ⟨l1, l2, l3, l4⟩ := linV_sound (θq := θq) hc hy e h
    exact ⟨l1, l2, by simp, l3, by simpa using l4⟩
  intro e
  induction e with
  | mul a b ha hb =>
      intro h
      simp only [quadV]
      by_cases h1 : (linC θq a && linC θq b) = true
      · rw [if_pos h1]
        simp only [Bool.and_eq_true] at h1
        exact prodV_sound hphi (linV_sound hc hy a h1.1) (linV_sound hc hy b h1.2)
      · rw [if_neg h1]
        simp only [quadC, Bool.or_eq_true, Bool.and_eq_true] at h
        by_cases h2 : (quadC θq a && qnn θq b) = true
        · rw [if_pos h2]
          simp only [Bool.and_eq_true] at h2
          obtain ⟨q1, q2, q3, q4, q5⟩ := ha h2.1
          obtain ⟨e1, e2⟩ := qnn_sound h2.2 y
          simp only [Rat.cast_mul]
          refine ⟨mul_nonneg q1 e2, mul_nonneg q2 e2, mul_nonneg q3 e2, ?_, ?_⟩
          · show 0 ≤ a.eval _ * b.eval _; rw [e1]; exact mul_nonneg q4 e2
          · show a.eval _ * b.eval _ ≤ _; rw [e1]
            nlinarith [mul_le_mul_of_nonneg_right q5 e2]
        · rw [if_neg h2]
          rcases h with (h | h) | h
          · exact absurd (by simp [h.1, h.2]) h1
          · exact absurd (by simp [h.1, h.2]) h2
          obtain ⟨q1, q2, q3, q4, q5⟩ := hb h.2
          obtain ⟨e1, e2⟩ := qnn_sound h.1 y
          simp only [Rat.cast_mul]
          refine ⟨mul_nonneg e2 q1, mul_nonneg e2 q2, mul_nonneg e2 q3, ?_, ?_⟩
          · show 0 ≤ a.eval _ * b.eval _; rw [e1]; exact mul_nonneg e2 q4
          · show a.eval _ * b.eval _ ≤ _; rw [e1]
            nlinarith [mul_le_mul_of_nonneg_left q5 e2]
  | npow a k _ =>
      intro h
      simp only [quadC, Bool.and_eq_true, decide_eq_true_eq] at h
      obtain ⟨rfl, h⟩ := h
      simp only [quadV]
      have := prodV_sound hphi (linV_sound (θq := θq) hc hy a h) (linV_sound hc hy a h)
      show _ ∧ _ ∧ _ ∧ 0 ≤ a.eval _ ^ 2 ∧ a.eval _ ^ 2 ≤ _
      rw [sq]; exact this
  | var j => intro h; exact lin _ (by simpa only [quadC] using h)
  | add a b _ _ => intro h; exact lin _ (by simpa only [quadC] using h)
  | qconst q => intro h; exact lin _ (by simpa only [quadC] using h)
  | par j => intro h; exact lin _ (by simpa only [quadC] using h)
  | const r => intro h; exact lin _ (by simpa only [quadC] using h)
  | sub a b _ _ => intro h; exact lin _ (by simpa only [quadC] using h)
  | div a b _ _ => intro h; exact lin _ (by simpa only [quadC] using h)
  | rpow a r _ => intro h; exact lin _ (by simpa only [quadC] using h)
  | exp a _ => intro h; exact lin _ (by simpa only [quadC] using h)
  | log a _ => intro h; exact lin _ (by simpa only [quadC] using h)

/-! ## Red con crecimiento cuadrático -/

variable (c θq) in
/-- Suma, sobre los términos de peso positivo, de `w·(A, B, C)`. -/
def tot : List (KExpr n p × List (Fin n × ℚ)) → ℚ × ℚ × ℚ
  | [] => (0, 0, 0)
  | t :: R =>
      if 0 < wgt c t.2 then
        ((tot R).1 + wgt c t.2 * (quadV c θq t.1).1,
          (tot R).2.1 + wgt c t.2 * (quadV c θq t.1).2.1,
          (tot R).2.2 + wgt c t.2 * (quadV c θq t.1).2.2)
      else tot R

def termR (pos : Fin p → Bool) (c : Fin n → ℚ) (θq : Fin p → ℚ)
    (t : KExpr n p × List (Fin n × ℚ)) : Bool :=
  decide (wgt c t.2 = 0) || (decide (wgt c t.2 < 0) && isNonneg pos t.1) ||
    (decide (0 < wgt c t.2) && quadC θq t.1)

/-- Constante de Riccati `Q = max(A, B/2, C)`. -/
def Qof (T3 : ℚ × ℚ × ℚ) : ℚ := max T3.1 (max (T3.2.1 / 2) T3.2.2)

/-- Comprobación completa: pesos `≥ 1`, signos, `Q > 0` y `1.1·Q·(φ₀ + 1)·T_q < 1`. -/
def checkRiccati (pos : Fin p → Bool) (c : Fin n → ℚ) (θq : Fin p → ℚ) (xq : Fin n → ℚ) (Tq : ℚ) (Rx : List (KExpr n p × List (Fin n × ℚ))) : Bool :=
  (List.finRange n).all (fun i => decide (1 ≤ c i)) && Rx.all (termR pos c θq) &&
    decide (0 < Qof (tot c θq Rx)) &&
    decide (11 / 10 * Qof (tot c θq Rx) * (((List.finRange n).map fun i => c i * xq i).sum + 1)
      * Tq < 1)

theorem tot_sound {pos : Fin p → Bool} (hc : ∀ i, 0 < c i) (hy : Nonneg y) (hθ : PosParams pos (qvec θq)) :
    ∀ R : List (KExpr n p × List (Fin n × ℚ)), (∀ t ∈ R, termR pos c θq t = true) →
      (R.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, qvec θq)).sum ≤
        (tot c θq R).1 + ((tot c θq R).2.1 : ℝ) * phi c y +
          ((tot c θq R).2.2 : ℝ) * phi c y ^ 2 := by
  intro R hR
  induction R with
  | nil => simp [tot]
  | cons t R ih =>
      have ih' := ih fun t' h' => hR t' (List.mem_cons_of_mem _ h')
      have ht := hR t List.mem_cons_self
      simp only [termR, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at ht
      rw [List.map_cons, List.sum_cons]
      by_cases hw : 0 < wgt c t.2
      · simp only [tot, if_pos hw, Rat.cast_add, Rat.cast_mul]
        have hq : quadC θq t.1 = true := by
          rcases ht with (h0 | ⟨h0, -⟩) | ⟨-, h0⟩
          · exact absurd h0 hw.ne'
          · exact absurd h0 (not_lt.2 hw.le)
          · exact h0
        obtain ⟨-, -, -, -, q5⟩ := quadV_sound (θq := θq) hc hy t.1 hq
        have hw' : (0 : ℝ) < (wgt c t.2 : ℝ) := by exact_mod_cast hw
        nlinarith [mul_le_mul_of_nonneg_left q5 hw'.le]
      · simp only [tot, if_neg hw]
        have : ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, qvec θq) ≤ 0 := by
          rcases ht with (h0 | ⟨h0, h1⟩) | ⟨h0, -⟩
          · rw [h0]; simp
          · have : ((wgt c t.2 : ℚ) : ℝ) < 0 := by exact_mod_cast h0
            exact mul_nonpos_of_nonpos_of_nonneg this.le (isNonneg_sound hy hθ t.1 h1)
          · exact absurd h0 hw
        linarith

/-- **Teorema final con crecimiento cuadrático**: para `0 ≤ T ≤ T_q`, la solución nominal
existe en `[0, T]`, es `≥ 0` y queda en el dominio; las soluciones existen cerca de `θ₀` y la
trayectoria es diferenciable respecto a `θ`. -/
theorem riccati_final (pos : Fin p → Bool) (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNet pos Rx = true) (c : Fin n → ℚ) (θq : Fin p → ℚ)
    (hθ : checkPosParams pos θq = true) (xq : Fin n → ℚ) (hx : checkNonneg xq = true)
    (Tq : ℚ) (hR : checkRiccati pos c θq xq Tq Rx = true) {T : ℝ} (hT : 0 ≤ T)
    (hTT : T ≤ Tq) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = qvec xq ∧
      (∀ t ∈ Icc 0 T,
        HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) (qvec θq)) (Icc 0 T) t ∧
        Nonneg (x₀ t) ∧ (x₀ t, qvec θq) ∈ domain (netF Rx)) ∧
      ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x (qvec θq) = x₀ ∧
        (∀ᶠ θ in 𝓝 (qvec θq), x θ 0 = qvec xq ∧
          ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field (netF Rx) (x θ t) θ) (Icc 0 T) t) ∧
        ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = 0 ∧
          ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) (qvec θq) := by
  have hθ₀ := posParams_qvec hθ
  obtain ⟨horth, hqp⟩ := checkNet_sound hN hθ₀
  simp only [checkRiccati, Bool.and_eq_true, List.all_eq_true, List.mem_finRange,
    true_implies, decide_eq_true_eq] at hR
  obtain ⟨⟨⟨hc1, hterm⟩, hQ⟩, hblow⟩ := hR
  have hcpos : ∀ i, 0 < c i := fun i => lt_of_lt_of_le one_pos (hc1 i)
  set Qq := Qof (tot c θq Rx) with hQq
  have hQr : (0 : ℝ) < Qq := by exact_mod_cast hQ
  -- cota de crecimiento
  have hgrowth : ∀ z, Nonneg z → ∑ i, (c i : ℝ) * field (netF Rx) z (qvec θq) i ≤
      (Qq : ℝ) * (∑ i, (c i : ℝ) * z i + 1) ^ 2 := by
    intro z hz
    have hs : ∑ i, (c i : ℝ) * field (netF Rx) z (qvec θq) i
        = (Rx.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (z, qvec θq)).sum :=
      sum_c_netExpr c Rx (z, qvec θq)
    have h1 := tot_sound (pos := pos) hcpos hz hθ₀ Rx hterm
    rw [hs]
    have hφ : 0 ≤ phi c z :=
      Finset.sum_nonneg fun i _ => mul_nonneg (by exact_mod_cast (hcpos i).le) (hz i)
    have hA : ((tot c θq Rx).1 : ℝ) ≤ Qq := by
      have : (tot c θq Rx).1 ≤ Qq := le_max_left _ _
      exact_mod_cast this
    have hB : ((tot c θq Rx).2.1 : ℝ) ≤ 2 * Qq := by
      have : (tot c θq Rx).2.1 / 2 ≤ Qq := (le_max_left _ _).trans (le_max_right _ _)
      have : (tot c θq Rx).2.1 ≤ 2 * Qq := by linarith
      exact_mod_cast this
    have hC : ((tot c θq Rx).2.2 : ℝ) ≤ Qq := by
      have : (tot c θq Rx).2.2 ≤ Qq := (le_max_right _ _).trans (le_max_right _ _)
      exact_mod_cast this
    show _ ≤ (Qq : ℝ) * (phi c z + 1) ^ 2
    nlinarith [mul_le_mul_of_nonneg_right hB hφ, mul_le_mul_of_nonneg_right hC (sq_nonneg (phi c z))]
  -- condición de horizonte
  rw [← Fin.sum_univ_def] at hblow
  have hblowR : (1 + 1 / 10) * (Qq : ℝ) * (∑ i, (c i : ℝ) * qvec xq i + 1) * T < 1 := by
    have hb : ((11 / 10 * Qq * (∑ i, c i * xq i + 1) * Tq : ℚ) : ℝ) < 1 := by
      exact_mod_cast hblow
    push_cast at hb
    simp only [qvec_apply]
    have hS : 0 ≤ ∑ i, (c i : ℝ) * qvec xq i := Finset.sum_nonneg fun i _ =>
      mul_nonneg (by exact_mod_cast (hcpos i).le) (nonneg_qvec hx i)
    have hK : 0 ≤ 11 / 10 * (Qq : ℝ) * (∑ i, (c i : ℝ) * qvec xq i + 1) := by positivity
    have := mul_le_mul_of_nonneg_left hTT hK
    simp only [qvec_apply] at this
    norm_num at this hb ⊢
    linarith
  -- existencia
  set U : Set (EuclideanSpace ℝ (Fin n)) := (fun y => (y, qvec θq)) ⁻¹' domain (netF Rx)
  have hcont : Continuous fun y : EuclideanSpace ℝ (Fin n) => (y, qvec θq) :=
    continuous_id.prodMk continuous_const
  have hU : IsOpen U := (isOpen_domain _).preimage hcont
  have hv : ContDiffOn ℝ 1 (fun y => field (netF Rx) y (qvec θq)) U :=
    (contDiffOn_field (netF Rx)).comp (contDiff_id.prodMk contDiff_const).contDiffOn
      (fun y hy => hy)
  obtain ⟨x₀, h0, hsol⟩ := exists_solution_riccati (fun y => field (netF Rx) y (qvec θq)) hU hv
    (fun z hz => horth z hz) (fun z hz i hi => hqp z hz i hi) (fun i => (c i : ℝ))
    one_pos (fun i => by show (1 : ℝ) ≤ (c i : ℝ); exact_mod_cast hc1 i) hQr (by norm_num : (0 : ℝ) < 1 / 10)
    hgrowth (qvec xq) (nonneg_qvec hx) hT hblowR
  refine ⟨x₀, h0, fun t ht => ⟨(hsol t ht).1, (hsol t ht).2, horth _ (hsol t ht).2⟩, ?_⟩
  exact kinetic_hasFDerivAt_of_nonneg (netF Rx) hT x₀ (qvec θq) horth hqp
    (fun t ht => (hsol t ht).1) (by rw [h0]; exact nonneg_qvec hx) (fun _ => qvec xq) 0
    (hasFDerivAt_const _ _) h0.symm

end RiccatiNetwork

#print axioms RiccatiNetwork.riccati_final

#print axioms RiccatiNetwork.exists_solution_riccati
