import PositivityInvariance
import EventSystems

/-!
# Comprobación automática de modelos cinéticos (SBML → `KExpr` → Lean)

Comprobadores **booleanos** sobre la sintaxis `KExpr`, demostrados correctos una sola vez. Para
cada modelo concreto, Lean los *ejecuta* (`decide`) y el teorema `checked_model_hasFDerivAt`
da la diferenciabilidad de la trayectoria sin ninguna hipótesis adicional sobre el modelo.

Supuestos globales: parámetros estimados `θ > 0` (todos los nominales de PEtab lo son en estos
modelos) y concentraciones `≥ 0`.

* `isNonneg e`: `e ≥ 0` en el ortante (`y ≥ 0`, `θ > 0`) — `isNonneg_sound`.
* `isPos e`: `e > 0` en el ortante — `isPos_sound`.
* `okOrth e`: denominadores `> 0` y bases de potencias reales `> 0` en el ortante, luego `e` está
  bien definida — `okOrth_sound`.
* `vanishes i e`: `e = 0` si `yᵢ = 0` (el término contiene el factor `yᵢ`) — `vanishes_sound`.
* `qp i e`: `e ≥ 0` si `y ≥ 0`, `yᵢ = 0` (los términos de consumo de la especie `i` se anulan
  sin especie `i`) — `qp_sound`.
* `checkModel F`: `okOrth (F i) ∧ qp i (F i)` para todo `i`.
-/

open Set Filter Topology KineticRegularity KExpr PositivityInvariance

namespace KineticCheck

variable {n p : ℕ}

/-- Parámetros positivos. -/
def PosParams (θ : EuclideanSpace ℝ (Fin p)) : Prop := ∀ j, 0 < θ j

namespace KExpr'

/-- Signo `≥ 0` garantizado sintácticamente en el ortante. -/
def isNonneg : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 ≤ q)
  | .var _ => true
  | .par _ => true
  | .add a b => isNonneg a && isNonneg b
  | .sub _ _ => false
  | .mul a b => isNonneg a && isNonneg b
  | .div a b => isNonneg a && isNonneg b
  | .npow a _ => isNonneg a
  | .rpow a _ => isNonneg a
  | .exp _ => true
  | .log _ => false

/-- Signo `> 0` garantizado sintácticamente en el ortante. -/
def isPos : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 < q)
  | .var _ => false
  | .par _ => true
  | .add a b => (isPos a && isNonneg b) || (isNonneg a && isPos b)
  | .sub _ _ => false
  | .mul a b => isPos a && isPos b
  | .div a b => isPos a && isPos b
  | .npow a _ => isPos a
  | .rpow a _ => isPos a
  | .exp _ => true
  | .log _ => false

/-- Bien definida en el ortante. -/
def okOrth : KExpr n p → Bool
  | .const _ => true
  | .qconst _ => true
  | .var _ => true
  | .par _ => true
  | .add a b => okOrth a && okOrth b
  | .sub a b => okOrth a && okOrth b
  | .mul a b => okOrth a && okOrth b
  | .div a b => okOrth a && okOrth b && isPos b
  | .npow a _ => okOrth a
  | .rpow a _ => okOrth a && isPos a
  | .exp a => okOrth a
  | .log a => okOrth a && isPos a

/-- Se anula cuando `yᵢ = 0`. -/
def vanishes (i : Fin n) : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (q = 0)
  | .var j => decide (j = i)
  | .par _ => false
  | .add a b => vanishes i a && vanishes i b
  | .sub a b => vanishes i a && vanishes i b
  | .mul a b => vanishes i a || vanishes i b
  | .div a _ => vanishes i a
  | .npow a k => vanishes i a && decide (0 < k)
  | .rpow _ _ => false
  | .exp _ => false
  | .log _ => false

/-- Cuasi-positividad de la componente `i`: `≥ 0` si `y ≥ 0` y `yᵢ = 0`. -/
def qp (i : Fin n) : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 ≤ q)
  | .var _ => true
  | .par _ => true
  | .add a b => qp i a && qp i b
  | .sub a b => (qp i a && vanishes i b) || (vanishes i a && vanishes i b)
  | .mul a b => (isNonneg a && qp i b) || (qp i a && isNonneg b) || vanishes i a || vanishes i b
  | .div a b => (qp i a && isNonneg b) || vanishes i a
  | .npow a k => isNonneg a || (vanishes i a && decide (0 < k))
  | .rpow a _ => isNonneg a
  | .exp _ => true
  | .log _ => false

variable {y : EuclideanSpace ℝ (Fin n)} {θ : EuclideanSpace ℝ (Fin p)}

theorem isNonneg_sound (hy : Nonneg y) (hθ : PosParams θ) :
    ∀ e : KExpr n p, isNonneg e = true → 0 ≤ e.eval (y, θ) := by
  intro e
  induction e with
  | const c => intro h; exact absurd h (by simp [isNonneg])
  | qconst q =>
      intro h; simp only [isNonneg, decide_eq_true_eq] at h
      show (0 : ℝ) ≤ (q : ℝ); exact_mod_cast h
  | var i => intro _; exact hy i
  | par j => intro _; exact (hθ j).le
  | add a b ha hb =>
      intro h; simp only [isNonneg, Bool.and_eq_true] at h
      exact add_nonneg (ha h.1) (hb h.2)
  | sub a b _ _ => intro h; exact absurd h (by simp [isNonneg])
  | mul a b ha hb =>
      intro h; simp only [isNonneg, Bool.and_eq_true] at h
      exact mul_nonneg (ha h.1) (hb h.2)
  | div a b ha hb =>
      intro h; simp only [isNonneg, Bool.and_eq_true] at h
      exact div_nonneg (ha h.1) (hb h.2)
  | npow a k ha => intro h; exact pow_nonneg (ha h) k
  | rpow a r ha => intro h; exact Real.rpow_nonneg (ha h) r
  | exp a _ => intro _; exact (Real.exp_pos _).le
  | log a _ => intro h; exact absurd h (by simp [isNonneg])

theorem isPos_sound (hy : Nonneg y) (hθ : PosParams θ) :
    ∀ e : KExpr n p, isPos e = true → 0 < e.eval (y, θ) := by
  intro e
  induction e with
  | const c => intro h; exact absurd h (by simp [isPos])
  | qconst q =>
      intro h; simp only [isPos, decide_eq_true_eq] at h
      show (0 : ℝ) < (q : ℝ); exact_mod_cast h
  | var i => intro h; exact absurd h (by simp [isPos])
  | par j => intro _; exact hθ j
  | add a b ha hb =>
      intro h; simp only [isPos, Bool.or_eq_true, Bool.and_eq_true] at h
      rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
      · exact add_pos_of_pos_of_nonneg (ha h1) (isNonneg_sound hy hθ b h2)
      · exact add_pos_of_nonneg_of_pos (isNonneg_sound hy hθ a h1) (hb h2)
  | sub a b _ _ => intro h; exact absurd h (by simp [isPos])
  | mul a b ha hb =>
      intro h; simp only [isPos, Bool.and_eq_true] at h
      exact mul_pos (ha h.1) (hb h.2)
  | div a b ha hb =>
      intro h; simp only [isPos, Bool.and_eq_true] at h
      exact div_pos (ha h.1) (hb h.2)
  | npow a k ha => intro h; exact pow_pos (ha h) k
  | rpow a r ha => intro h; exact Real.rpow_pos_of_pos (ha h) r
  | exp a _ => intro _; exact Real.exp_pos _
  | log a _ => intro h; exact absurd h (by simp [isPos])

theorem okOrth_sound (hy : Nonneg y) (hθ : PosParams θ) :
    ∀ e : KExpr n p, okOrth e = true → e.ok (y, θ) := by
  intro e
  induction e with
  | const c => intro _; trivial
  | qconst q => intro _; trivial
  | var i => intro _; trivial
  | par j => intro _; trivial
  | add a b ha hb =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | sub a b ha hb =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | mul a b ha hb =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | div a b ha hb =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h
      exact ⟨ha h.1.1, hb h.1.2, ne_of_gt (isPos_sound hy hθ b h.2)⟩
  | npow a k ha => intro h; exact ha h
  | rpow a r ha =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h
      exact ⟨ha h.1, isPos_sound hy hθ a h.2⟩
  | exp a ha => intro h; exact ha h
  | log a ha =>
      intro h; simp only [okOrth, Bool.and_eq_true] at h
      exact ⟨ha h.1, isPos_sound hy hθ a h.2⟩

theorem vanishes_sound (i : Fin n) (hyi : y i = 0) :
    ∀ e : KExpr n p, vanishes i e = true → e.eval (y, θ) = 0 := by
  intro e
  induction e with
  | const c => intro h; exact absurd h (by simp [vanishes])
  | qconst q =>
      intro h; simp only [vanishes, decide_eq_true_eq] at h
      show ((q : ℝ)) = 0
      rw [h]; simp
  | var j =>
      intro h; simp only [vanishes, decide_eq_true_eq] at h
      show y j = 0
      rw [h]; exact hyi
  | par j => intro h; exact absurd h (by simp [vanishes])
  | add a b ha hb =>
      intro h; simp only [vanishes, Bool.and_eq_true] at h
      show a.eval (y, θ) + b.eval (y, θ) = 0
      rw [ha h.1, hb h.2, add_zero]
  | sub a b ha hb =>
      intro h; simp only [vanishes, Bool.and_eq_true] at h
      show a.eval (y, θ) - b.eval (y, θ) = 0
      rw [ha h.1, hb h.2, sub_zero]
  | mul a b ha hb =>
      intro h; simp only [vanishes, Bool.or_eq_true] at h
      show a.eval (y, θ) * b.eval (y, θ) = 0
      rcases h with h | h
      · rw [ha h, zero_mul]
      · rw [hb h, mul_zero]
  | div a b ha _ =>
      intro h
      show a.eval (y, θ) / b.eval (y, θ) = 0
      rw [ha h, zero_div]
  | npow a k ha =>
      intro h; simp only [vanishes, Bool.and_eq_true, decide_eq_true_eq] at h
      show a.eval (y, θ) ^ k = 0
      rw [ha h.1]; exact zero_pow (Nat.pos_iff_ne_zero.1 h.2)
  | rpow a r _ => intro h; exact absurd h (by simp [vanishes])
  | exp a _ => intro h; exact absurd h (by simp [vanishes])
  | log a _ => intro h; exact absurd h (by simp [vanishes])

theorem qp_sound (hy : Nonneg y) (hθ : PosParams θ) (i : Fin n) (hyi : y i = 0) :
    ∀ e : KExpr n p, qp i e = true → 0 ≤ e.eval (y, θ) := by
  intro e
  induction e with
  | const c => intro h; exact absurd h (by simp [qp])
  | qconst q =>
      intro h; simp only [qp, decide_eq_true_eq] at h
      show (0 : ℝ) ≤ (q : ℝ); exact_mod_cast h
  | var j => intro _; exact hy j
  | par j => intro _; exact (hθ j).le
  | add a b ha hb =>
      intro h; simp only [qp, Bool.and_eq_true] at h
      exact add_nonneg (ha h.1) (hb h.2)
  | sub a b ha _ =>
      intro h; simp only [qp, Bool.or_eq_true, Bool.and_eq_true] at h
      show 0 ≤ a.eval (y, θ) - b.eval (y, θ)
      rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
      · rw [vanishes_sound i hyi b h2, sub_zero]; exact ha h1
      · rw [vanishes_sound i hyi a h1, vanishes_sound i hyi b h2, sub_zero]
  | mul a b ha hb =>
      intro h; simp only [qp, Bool.or_eq_true, Bool.and_eq_true] at h
      show 0 ≤ a.eval (y, θ) * b.eval (y, θ)
      rcases h with ((⟨h1, h2⟩ | ⟨h1, h2⟩) | h) | h
      · exact mul_nonneg (isNonneg_sound hy hθ a h1) (hb h2)
      · exact mul_nonneg (ha h1) (isNonneg_sound hy hθ b h2)
      · rw [vanishes_sound i hyi a h, zero_mul]
      · rw [vanishes_sound i hyi b h, mul_zero]
  | div a b ha _ =>
      intro h; simp only [qp, Bool.or_eq_true, Bool.and_eq_true] at h
      show 0 ≤ a.eval (y, θ) / b.eval (y, θ)
      rcases h with ⟨h1, h2⟩ | h
      · exact div_nonneg (ha h1) (isNonneg_sound hy hθ b h2)
      · rw [vanishes_sound i hyi a h, zero_div]
  | npow a k _ =>
      intro h; simp only [qp, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at h
      show 0 ≤ a.eval (y, θ) ^ k
      rcases h with h | ⟨h1, h2⟩
      · exact pow_nonneg (isNonneg_sound hy hθ a h) k
      · rw [vanishes_sound i hyi a h1, zero_pow (Nat.pos_iff_ne_zero.1 h2)]
  | rpow a r _ =>
      intro h
      exact Real.rpow_nonneg (isNonneg_sound hy hθ a h) r
  | exp a _ => intro _; exact (Real.exp_pos _).le
  | log a _ => intro h; exact absurd h (by simp [qp])

end KExpr'

open KExpr'

/-- **Comprobador de un modelo completo** (calculable: Lean lo ejecuta con `decide`). -/
def checkModel (F : Fin n → KExpr n p) : Bool :=
  (List.finRange n).all fun i => okOrth (F i) && qp i (F i)

theorem checkModel_spec {F : Fin n → KExpr n p} (h : checkModel F = true) (i : Fin n) :
    okOrth (F i) = true ∧ qp i (F i) = true := by
  simp only [checkModel, List.all_eq_true, List.mem_finRange, true_implies,
    Bool.and_eq_true] at h
  exact h i

/-- Un modelo que pasa la comprobación tiene su dominio conteniendo el ortante y es
cuasi-positivo (para todo `θ > 0`). -/
theorem checkModel_sound {F : Fin n → KExpr n p} (h : checkModel F = true)
    {θ : EuclideanSpace ℝ (Fin p)} (hθ : PosParams θ) :
    (∀ y, Nonneg y → (y, θ) ∈ domain F) ∧
    (∀ y, Nonneg y → ∀ i, y i = 0 → 0 ≤ field F y θ i) :=
  ⟨fun y hy i => okOrth_sound hy hθ (F i) (checkModel_spec h i).1,
   fun y hy i hyi => qp_sound hy hθ i hyi (F i) (checkModel_spec h i).2⟩

/-- **Teorema final para un modelo comprobado.** Si `checkModel F = true` (lo verifica Lean
ejecutando el comprobador), `θ₀ > 0` y el dato inicial nominal es `≥ 0`, entonces las
soluciones existen cerca de `θ₀`, la trayectoria es `≥ 0`, permanece en el dominio y es
diferenciable respecto a `θ`, con sensibilidad `S` (la matriz `J` del artículo). -/
theorem checked_model_hasFDerivAt (F : Fin n → KExpr n p) (hF : checkModel F = true)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (hθ₀ : PosParams θ₀)
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field F (x₀ t) θ₀) (Icc 0 T) t)
    (hpos0 : Nonneg (x₀ 0))
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0) :
    (∀ t ∈ Icc 0 T, Nonneg (x₀ t) ∧ (x₀ t, θ₀) ∈ domain F) ∧
    ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field F (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = D0 ∧
        ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ₀ := by
  obtain ⟨horth, hqp⟩ := checkModel_sound hF hθ₀
  exact ⟨kinetic_nonneg F θ₀ horth hqp x₀ hx₀ hpos0,
    kinetic_hasFDerivAt_of_nonneg F hT x₀ θ₀ horth hqp hx₀ hpos0 x0 D0 hx0 hx00⟩

/-- **Modelos con entradas por tramos (escalones en tiempos fijos).** El tramo `k` dura `L k` y
tiene campo `F k`; el estado es continuo entre tramos. Si cada tramo pasa la comprobación,
`θ₀ > 0` y el dato inicial nominal es `≥ 0`, entonces las soluciones de todos los tramos existen
cerca de `θ₀` y la trayectoria es diferenciable en `θ₀` en todo instante. -/
theorem checked_segments_hasFDerivAt (F : ℕ → Fin n → KExpr n p)
    (hF : ∀ k, checkModel (F k) = true) (L : ℕ → ℝ) (hL : ∀ k, 0 ≤ L k)
    (y₀ : ℕ → ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (hθ₀ : PosParams θ₀)
    (hy₀ : ∀ k, ∀ t ∈ Icc 0 (L k),
      HasDerivWithinAt (y₀ k) (field (F k) (y₀ k t) θ₀) (Icc 0 (L k)) t)
    (hlink : ∀ k, y₀ (k + 1) 0 = y₀ k (L k)) (hpos0 : Nonneg (y₀ 0 0))
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (hx0 : DifferentiableAt ℝ x0 θ₀) (hx00 : x0 θ₀ = y₀ 0 0) :
    ∃ Y : ℕ → EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n),
      (∀ k, Y k θ₀ = y₀ k) ∧
      (∀ k, ∀ᶠ θ in 𝓝 θ₀, ∀ t ∈ Icc 0 (L k),
        HasDerivWithinAt (Y k θ) (field (F k) (Y k θ t) θ) (Icc 0 (L k)) t) ∧
      (∀ᶠ θ in 𝓝 θ₀, Y 0 θ 0 = x0 θ) ∧
      (∀ k, ∀ᶠ θ in 𝓝 θ₀, Y (k + 1) θ 0 = Y k θ (L k)) ∧
      (∀ k, ∀ s ∈ Icc 0 (L k), DifferentiableAt ℝ (fun θ => Y k θ s) θ₀) := by
  -- positividad y permanencia en el dominio, tramo a tramo
  have hseg : ∀ k, Nonneg (y₀ k 0) ∧
      ∀ t ∈ Icc 0 (L k), Nonneg (y₀ k t) ∧ (y₀ k t, θ₀) ∈ domain (F k) := by
    intro k
    induction k with
    | zero =>
        obtain ⟨horth, hqp⟩ := checkModel_sound (hF 0) hθ₀
        exact ⟨hpos0, kinetic_nonneg (F 0) θ₀ horth hqp (y₀ 0) (hy₀ 0) hpos0⟩
    | succ k ih =>
        have h0 : Nonneg (y₀ (k + 1) 0) := by
          rw [hlink]; exact (ih.2 (L k) ⟨hL k, le_rfl⟩).1
        obtain ⟨horth, hqp⟩ := checkModel_sound (hF (k + 1)) hθ₀
        exact ⟨h0, kinetic_nonneg (F (k + 1)) θ₀ horth hqp (y₀ (k + 1)) (hy₀ (k + 1)) h0⟩
  exact EventSystems.event_hasFDerivAt (fun k => field (F k)) (fun k => domain (F k))
    (fun k => isOpen_domain (F k)) (fun k => contDiffOn_field (F k)) L hL
    (fun _ x _ => x) y₀ θ₀ hy₀ (fun k t ht => ((hseg k).2 t ht).2)
    (fun _ => differentiableAt_fst) hlink x0 hx0 hx00

/-! Prueba de humo: Michaelis–Menten con producción constante pasa la comprobación. -/
example : checkModel (n := 1) (p := 3)
    ![KExpr.sub (KExpr.par 0) (KExpr.mm (KExpr.par 1) (KExpr.par 2) (KExpr.var 0))] = true := by
  decide

end KineticCheck

#print axioms KineticCheck.checked_model_hasFDerivAt
#print axioms KineticCheck.checked_segments_hasFDerivAt
