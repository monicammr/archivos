import KineticNetwork
import StrictExistence

/-!
# Redes con positividad estricta: comprobación completa sin condiciones

Para modelos cuyo dominio exige especies **estrictamente** positivas (incidencias `β·S·I/N`,
potencias de Hill `Z^n` con `n` real, …). `Σ` (máscara `sx`) son las especies con dato inicial
`> 0` y `P = {y ≥ 0, yⱼ > 0 (j ∈ Σ)}` (`SPos`).

Comprobadores booleanos (Lean los ejecuta con `decide +kernel`), demostrados correctos una vez:

* `sNonneg`, `sPos`, `sOk`, `snp`: signo `≥ 0`, `> 0`, buena definición y signo `≤ 0` en `P`
  (aquí `yⱼ > 0` para `j ∈ Σ`, y `log q ≥ 0` para un racional `q ≥ 1`).
* `bnd`: la expresión está acotada (y es `≥ 0`) en `P ∩ [0, B]ⁿ` (o en todo `P`, sin la caja);
  reconoce términos saturantes `k·X/(… + X + …) ≤ k` (`satb`), `e^{≤ 0} ≤ 1`, y productos de
  fracciones `(a₁a₂)/(d₁d₂) = (a₁/d₁)(a₂/d₂)` (`bpair`).
* `cons i`: el término es `≤ K·yᵢ` en `P ∩ [0, B]ⁿ` (consumo proporcional a la especie).
* `checkNetS`: buena definición en `P`; consumo de una especie de `Σ` proporcional a ella;
  consumo de una especie fuera de `Σ` nulo cuando falta; producción `≥ 0`.
* `checkGrowthS`: crecimiento lineal con pesos `cᵢ ≥ 1`, en `P`.

`strict_final_init`: con ambas comprobaciones, la solución nominal **existe en `[0, T]`, queda
en `P` (las especies de `Σ` permanecen estrictamente positivas) y en el dominio**, y la
trayectoria es diferenciable respecto a θ. No queda ninguna condición sin demostrar.
-/

open Set Filter Topology KineticRegularity PositivityInvariance KineticCheck KineticCheck.KExpr'
  KineticNetwork StrictExistence

namespace StrictNetwork

variable {n p : ℕ}

/-! ## Igualdad sintáctica -/

/-- Igualdad sintáctica (conservadora: `false` con constantes reales y potencias reales). -/
def keq : KExpr n p → KExpr n p → Bool
  | .qconst q, .qconst q' => decide (q = q')
  | .var i, .var j => decide (i = j)
  | .par i, .par j => decide (i = j)
  | .add a b, .add a' b' => keq a a' && keq b b'
  | .sub a b, .sub a' b' => keq a a' && keq b b'
  | .mul a b, .mul a' b' => keq a a' && keq b b'
  | .div a b, .div a' b' => keq a a' && keq b b'
  | .npow a k, .npow a' k' => keq a a' && decide (k = k')
  | .exp a, .exp a' => keq a a'
  | .log a, .log a' => keq a a'
  | _, _ => false

theorem keq_sound : ∀ a b : KExpr n p, keq a b = true → a = b := by
  intro a
  induction a with
  | const c => intro b h; cases b <;> simp [keq] at h
  | qconst q => intro b h; cases b <;> simp [keq] at h; rw [h]
  | var i => intro b h; cases b <;> simp [keq] at h; rw [h]
  | par i => intro b h; cases b <;> simp [keq] at h; rw [h]
  | add a1 a2 ih1 ih2 =>
      intro b h; cases b <;> simp [keq] at h; rw [ih1 _ h.1, ih2 _ h.2]
  | sub a1 a2 ih1 ih2 =>
      intro b h; cases b <;> simp [keq] at h; rw [ih1 _ h.1, ih2 _ h.2]
  | mul a1 a2 ih1 ih2 =>
      intro b h; cases b <;> simp [keq] at h; rw [ih1 _ h.1, ih2 _ h.2]
  | div a1 a2 ih1 ih2 =>
      intro b h; cases b <;> simp [keq] at h; rw [ih1 _ h.1, ih2 _ h.2]
  | npow a k ih => intro b h; cases b <;> simp [keq] at h; rw [ih _ h.1, h.2]
  | rpow a r ih => intro b h; cases b <;> simp [keq] at h
  | exp a ih => intro b h; cases b <;> simp [keq] at h; rw [ih _ h]
  | log a ih => intro b h; cases b <;> simp [keq] at h; rw [ih _ h]

/-! ## Signos en la región estricta -/

/-- Racional `≥ 1`. -/
def qge1 : KExpr n p → Bool
  | .qconst q => decide (1 ≤ q)
  | _ => false

/-- Racional `> 1`. -/
def qgt1 : KExpr n p → Bool
  | .qconst q => decide (1 < q)
  | _ => false

lemma qge1_sound {e : KExpr n p} (h : qge1 e = true) (z) : 1 ≤ e.eval z := by
  cases e with
  | qconst q =>
      simp only [qge1, decide_eq_true_eq] at h
      show (1 : ℝ) ≤ (q : ℝ); exact_mod_cast h
  | _ => simp [qge1] at h

lemma qgt1_sound {e : KExpr n p} (h : qgt1 e = true) (z) : 1 < e.eval z := by
  cases e with
  | qconst q =>
      simp only [qgt1, decide_eq_true_eq] at h
      show (1 : ℝ) < (q : ℝ); exact_mod_cast h
  | _ => simp [qgt1] at h

/-- Cotas de parámetros (se comprueban en `θ₀`): `ub j = (inf, sup)`, con `r ≤ θⱼ` si
`inf = some r` y `θⱼ ≤ q` si `sup = some q`. -/
def UB (ub : Fin p → Option ℚ × Option ℚ) (θ : EuclideanSpace ℝ (Fin p)) : Prop :=
  (∀ j r, (ub j).1 = some r → (r : ℝ) ≤ θ j) ∧ (∀ j q, (ub j).2 = some q → θ j ≤ q)

/-- Signos de los parámetros: positividad (`pos`) y cotas superiores (`ub`). -/
def PP (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (θ : EuclideanSpace ℝ (Fin p)) : Prop :=
  PosParams pos θ ∧ UB ub θ

/-- `q − θⱼ ≥ 0` por una cota `θⱼ ≤ r ≤ q` (con `θⱼ > 0`). -/
def subub (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) : KExpr n p → KExpr n p → Bool
  | .qconst q, .par j => pos j && (match (ub j).2 with | some r => decide (r ≤ q) | none => false)
  | _, _ => false

/-- `q + θⱼ ≥ 0` por una cota inferior `θⱼ ≥ r ≥ −q`. -/
def addlb (ub : Fin p → Option ℚ × Option ℚ) : KExpr n p → KExpr n p → Bool
  | .qconst q, .par j => match (ub j).1 with | some r => decide (0 ≤ q + r) | none => false
  | _, _ => false

lemma addlb_sound {ub : Fin p → Option ℚ × Option ℚ} {θ : EuclideanSpace ℝ (Fin p)}
    (hub : UB ub θ) {a b : KExpr n p} (h : addlb ub a b = true) (z : EuclideanSpace ℝ (Fin n)) :
    0 ≤ a.eval (z, θ) + b.eval (z, θ) := by
  cases a with
  | qconst q =>
    cases b with
    | par j =>
      simp only [addlb] at h
      cases e : (ub j).1 with
      | none => rw [e] at h; simp at h
      | some r =>
        rw [e] at h
        simp only [decide_eq_true_eq] at h
        have h1 := hub.1 j r e
        have h2 : (0 : ℝ) ≤ q + r := by exact_mod_cast h
        show (0 : ℝ) ≤ q + θ j
        linarith
    | _ => simp [addlb] at h
  | _ => simp [addlb] at h

lemma subub_sound {pos : Fin p → Bool} {ub : Fin p → Option ℚ × Option ℚ} {θ : EuclideanSpace ℝ (Fin p)}
    (hθ : PP pos ub θ) {a b : KExpr n p} (h : subub pos ub a b = true) (z : EuclideanSpace ℝ (Fin n)) :
    0 ≤ a.eval (z, θ) - b.eval (z, θ) ∧ a.eval (z, θ) - b.eval (z, θ) ≤ a.eval (z, θ) := by
  cases a with
  | qconst q =>
    cases b with
    | par j =>
      simp only [subub, Bool.and_eq_true] at h
      obtain ⟨hp, hu⟩ := h
      cases e : (ub j).2 with
      | none => rw [e] at hu; simp at hu
      | some r =>
        rw [e] at hu
        simp only [decide_eq_true_eq] at hu
        have h1 := hθ.2.2 j r e
        have h2 : (r : ℝ) ≤ q := by exact_mod_cast hu
        have h3 := hθ.1 j hp
        show 0 ≤ (q : ℝ) - θ j ∧ (q : ℝ) - θ j ≤ q
        constructor <;> linarith
    | _ => simp [subub] at h
  | _ => simp [subub] at h

/-- Las cotas `ub` se cumplen en `θq`. -/
def checkUB (ub : Fin p → Option ℚ × Option ℚ) (θq : Fin p → ℚ) : Bool :=
  (List.finRange p).all fun j =>
    (match (ub j).1 with | some r => decide (r ≤ θq j) | none => true) &&
    (match (ub j).2 with | some r => decide (θq j ≤ r) | none => true)

lemma ub_qvec {ub : Fin p → Option ℚ × Option ℚ} {θq : Fin p → ℚ} (h : checkUB ub θq = true) :
    UB ub (qvec θq) := by
  simp only [checkUB, List.all_eq_true, List.mem_finRange, true_implies, Bool.and_eq_true] at h
  refine ⟨fun j r hj => ?_, fun j r hj => ?_⟩
  · have := (h j).1
    rw [hj] at this
    simp only [decide_eq_true_eq] at this
    rw [qvec_apply]; exact_mod_cast this
  · have := (h j).2
    rw [hj] at this
    simp only [decide_eq_true_eq] at this
    rw [qvec_apply]; exact_mod_cast this

variable (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (sx : Fin n → Bool)

mutual
/-- `≥ 0` en `P`. -/
def sNonneg (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 ≤ q)
  | .var _ => true
  | .par j => pos j
  | .add a b => (sNonneg pos ub a && sNonneg pos ub b) || addlb ub a b
  | .sub a b => (qge1 a && expLe1 pos ub b) || subub pos ub a b
  | .mul a b => sNonneg pos ub a && sNonneg pos ub b
  | .div a b => sNonneg pos ub a && sNonneg pos ub b
  | .npow a _ => sNonneg pos ub a
  | .rpow a _ => sNonneg pos ub a
  | .exp _ => true
  | .log a => qge1 a

/-- `≤ 0` en `P`. -/
def snp (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) : KExpr n p → Bool
  | .qconst q => decide (q ≤ 0)
  | .add a b => snp pos ub a && snp pos ub b
  | .sub a b => snp pos ub a && sNonneg pos ub b
  | .mul a b => (snp pos ub a && sNonneg pos ub b) || (sNonneg pos ub a && snp pos ub b)
  | .div a b => snp pos ub a && sNonneg pos ub b
  | _ => false

/-- `e^x` con `x ≤ 0`, luego `0 ≤ e^x ≤ 1`. -/
def expLe1 (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) : KExpr n p → Bool
  | .exp x => snp pos ub x
  | _ => false
end

/-- `> 0` en `P`. -/
def sPos : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 < q)
  | .var j => sx j
  | .par j => pos j
  | .add a b => (sPos a && sNonneg pos ub b) || (sNonneg pos ub a && sPos b)
  | .sub _ _ => false
  | .mul a b => sPos a && sPos b
  | .div a b => sPos a && sPos b
  | .npow a _ => sPos a
  | .rpow a _ => sPos a
  | .exp _ => true
  | .log a => qgt1 a

/-- Bien definida en `P`. -/
def sOk : KExpr n p → Bool
  | .const _ => true
  | .qconst _ => true
  | .var _ => true
  | .par _ => true
  | .add a b => sOk a && sOk b
  | .sub a b => sOk a && sOk b
  | .mul a b => sOk a && sOk b
  | .div a b => sOk a && sOk b && sPos pos ub sx b
  | .npow a _ => sOk a
  | .rpow a _ => sOk a && sPos pos ub sx a
  | .exp a => sOk a
  | .log a => sOk a && sPos pos ub sx a

variable {pos ub sx} {y : EuclideanSpace ℝ (Fin n)} {θ : EuclideanSpace ℝ (Fin p)}

/-- Corrección conjunta de `sNonneg`, `snp` y `expLe1`. -/
theorem sign_sound (hy : Nonneg y) (hθ : PP pos ub θ) : ∀ e : KExpr n p,
    (sNonneg pos ub e = true → 0 ≤ e.eval (y, θ)) ∧ (snp pos ub e = true → e.eval (y, θ) ≤ 0) ∧
    (expLe1 pos ub e = true → 0 ≤ e.eval (y, θ) ∧ e.eval (y, θ) ≤ 1) := by
  intro e
  induction e with
  | const c => exact ⟨fun h => by simp [sNonneg] at h, fun h => by simp [snp] at h,
      fun h => by simp [expLe1] at h⟩
  | qconst q =>
      refine ⟨fun h => ?_, fun h => ?_, fun h => by simp [expLe1] at h⟩
      · simp only [sNonneg, decide_eq_true_eq] at h
        show (0 : ℝ) ≤ (q : ℝ); exact_mod_cast h
      · simp only [snp, decide_eq_true_eq] at h
        show ((q : ℝ)) ≤ 0; exact_mod_cast h
  | var i => exact ⟨fun _ => hy i, fun h => by simp [snp] at h, fun h => by simp [expLe1] at h⟩
  | par j => exact ⟨fun h => (hθ.1 j h).le, fun h => by simp [snp] at h,
      fun h => by simp [expLe1] at h⟩
  | add a b ha hb =>
      refine ⟨fun h => ?_, fun h => ?_, fun h => by simp [expLe1] at h⟩
      · simp only [sNonneg, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · exact add_nonneg (ha.1 h.1) (hb.1 h.2)
        · exact addlb_sound hθ.2 h y
      · simp only [snp, Bool.and_eq_true] at h
        exact add_nonpos (ha.2.1 h.1) (hb.2.1 h.2)
  | sub a b ha hb =>
      refine ⟨fun h => ?_, fun h => ?_, fun h => by simp [expLe1] at h⟩
      · simp only [sNonneg, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · have h1 := qge1_sound h.1 (y, θ)
          have h2 := (hb.2.2 h.2).2
          show 0 ≤ a.eval _ - b.eval _; linarith
        · exact (subub_sound hθ h y).1
      · simp only [snp, Bool.and_eq_true] at h
        have h1 := ha.2.1 h.1
        have h2 := hb.1 h.2
        show a.eval _ - b.eval _ ≤ 0; linarith
  | mul a b ha hb =>
      refine ⟨fun h => ?_, fun h => ?_, fun h => by simp [expLe1] at h⟩
      · simp only [sNonneg, Bool.and_eq_true] at h
        exact mul_nonneg (ha.1 h.1) (hb.1 h.2)
      · simp only [snp, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
        · exact mul_nonpos_of_nonpos_of_nonneg (ha.2.1 h1) (hb.1 h2)
        · exact mul_nonpos_of_nonneg_of_nonpos (ha.1 h1) (hb.2.1 h2)
  | div a b ha hb =>
      refine ⟨fun h => ?_, fun h => ?_, fun h => by simp [expLe1] at h⟩
      · simp only [sNonneg, Bool.and_eq_true] at h
        exact div_nonneg (ha.1 h.1) (hb.1 h.2)
      · simp only [snp, Bool.and_eq_true] at h
        show a.eval _ / b.eval _ ≤ 0
        rw [div_eq_mul_inv]
        exact mul_nonpos_of_nonpos_of_nonneg (ha.2.1 h.1) (inv_nonneg.2 (hb.1 h.2))
  | npow a k ha =>
      exact ⟨fun h => pow_nonneg (ha.1 h) k, fun h => by simp [snp] at h,
        fun h => by simp [expLe1] at h⟩
  | rpow a r ha =>
      exact ⟨fun h => Real.rpow_nonneg (ha.1 h) r, fun h => by simp [snp] at h,
        fun h => by simp [expLe1] at h⟩
  | exp a ha =>
      refine ⟨fun _ => (Real.exp_pos _).le, fun h => by simp [snp] at h, fun h => ?_⟩
      simp only [expLe1] at h
      exact ⟨(Real.exp_pos _).le, Real.exp_le_one_iff.2 (ha.2.1 h)⟩
  | log a _ =>
      refine ⟨fun h => ?_, fun h => by simp [snp] at h, fun h => by simp [expLe1] at h⟩
      simp only [sNonneg] at h
      exact Real.log_nonneg (qge1_sound h _)

theorem sNonneg_sound (hy : Nonneg y) (hθ : PP pos ub θ) :
    ∀ e : KExpr n p, sNonneg pos ub e = true → 0 ≤ e.eval (y, θ) :=
  fun e => (sign_sound hy hθ e).1

theorem expLe1_sound (hy : Nonneg y) (hθ : PP pos ub θ) :
    ∀ e : KExpr n p, expLe1 pos ub e = true → 0 ≤ e.eval (y, θ) ∧ e.eval (y, θ) ≤ 1 :=
  fun e => (sign_sound hy hθ e).2.2

theorem sPos_sound (hy : SPos sx y) (hθ : PP pos ub θ) :
    ∀ e : KExpr n p, sPos pos ub sx e = true → 0 < e.eval (y, θ) := by
  intro e
  induction e with
  | const c => intro h; exact absurd h (by simp [sPos])
  | qconst q =>
      intro h; simp only [sPos, decide_eq_true_eq] at h
      show (0 : ℝ) < (q : ℝ); exact_mod_cast h
  | var i => intro h; exact hy.2 i h
  | par j => intro h; exact hθ.1 j h
  | add a b ha hb =>
      intro h; simp only [sPos, Bool.or_eq_true, Bool.and_eq_true] at h
      rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
      · exact add_pos_of_pos_of_nonneg (ha h1) (sNonneg_sound hy.1 hθ b h2)
      · exact add_pos_of_nonneg_of_pos (sNonneg_sound hy.1 hθ a h1) (hb h2)
  | sub a b _ _ => intro h; exact absurd h (by simp [sPos])
  | mul a b ha hb =>
      intro h; simp only [sPos, Bool.and_eq_true] at h
      exact mul_pos (ha h.1) (hb h.2)
  | div a b ha hb =>
      intro h; simp only [sPos, Bool.and_eq_true] at h
      exact div_pos (ha h.1) (hb h.2)
  | npow a k ha => intro h; exact pow_pos (ha h) k
  | rpow a r ha => intro h; exact Real.rpow_pos_of_pos (ha h) r
  | exp a _ => intro _; exact Real.exp_pos _
  | log a _ =>
      intro h; simp only [sPos] at h
      exact Real.log_pos (qgt1_sound h _)

theorem sOk_sound (hy : SPos sx y) (hθ : PP pos ub θ) :
    ∀ e : KExpr n p, sOk pos ub sx e = true → e.ok (y, θ) := by
  intro e
  induction e with
  | const c => intro _; trivial
  | qconst q => intro _; trivial
  | var i => intro _; trivial
  | par j => intro _; trivial
  | add a b ha hb =>
      intro h; simp only [sOk, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | sub a b ha hb =>
      intro h; simp only [sOk, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | mul a b ha hb =>
      intro h; simp only [sOk, Bool.and_eq_true] at h; exact ⟨ha h.1, hb h.2⟩
  | div a b ha hb =>
      intro h; simp only [sOk, Bool.and_eq_true] at h
      exact ⟨ha h.1.1, hb h.1.2, ne_of_gt (sPos_sound hy hθ b h.2)⟩
  | npow a k ha => intro h; exact ha h
  | rpow a r ha =>
      intro h; simp only [sOk, Bool.and_eq_true] at h
      exact ⟨ha h.1, sPos_sound hy hθ a h.2⟩
  | exp a ha => intro h; exact ha h
  | log a ha =>
      intro h; simp only [sOk, Bool.and_eq_true] at h
      exact ⟨ha h.1, sPos_sound hy hθ a h.2⟩

theorem snp_sound (hy : Nonneg y) (hθ : PP pos ub θ) :
    ∀ e : KExpr n p, snp pos ub e = true → e.eval (y, θ) ≤ 0 :=
  fun e => (sign_sound hy hθ e).2.1

/-- `X` es un sumando de `d` (los demás sumandos son `≥ 0`), luego `0 ≤ X ≤ d`. -/
def summand (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (X : KExpr n p) : KExpr n p → Bool
  | .add a b => (keq (.add a b) X && sNonneg pos ub X) ||
      (summand pos ub X a && sNonneg pos ub b) || (sNonneg pos ub a && summand pos ub X b)
  | d => keq d X && sNonneg pos ub X

theorem summand_sound (hy : Nonneg y) (hθ : PP pos ub θ) (X : KExpr n p) :
    ∀ d : KExpr n p, summand pos ub X d = true → 0 ≤ X.eval (y, θ) ∧ X.eval (y, θ) ≤ d.eval (y, θ) := by
  have base : ∀ d : KExpr n p, (keq d X && sNonneg pos ub X) = true →
      0 ≤ X.eval (y, θ) ∧ X.eval (y, θ) ≤ d.eval (y, θ) := by
    intro d h
    simp only [Bool.and_eq_true] at h
    rw [keq_sound d X h.1]
    exact ⟨sNonneg_sound hy hθ X h.2, le_rfl⟩
  intro d
  induction d with
  | add a b ha hb =>
      intro h
      simp only [summand, Bool.or_eq_true, Bool.and_eq_true] at h
      rcases h with (h | ⟨h1, h2⟩) | ⟨h1, h2⟩
      · exact base _ (by simp [h.1, h.2])
      · obtain ⟨p1, p2⟩ := ha h1
        exact ⟨p1, by show _ ≤ a.eval _ + b.eval _; linarith [sNonneg_sound hy hθ b h2]⟩
      · obtain ⟨p1, p2⟩ := hb h2
        exact ⟨p1, by show _ ≤ a.eval _ + b.eval _; linarith [sNonneg_sound hy hθ a h1]⟩
  | const c => intro h; exact base _ (by simpa only [summand] using h)
  | qconst q => intro h; exact base _ (by simpa only [summand] using h)
  | var i => intro h; exact base _ (by simpa only [summand] using h)
  | par j => intro h; exact base _ (by simpa only [summand] using h)
  | sub a b _ _ => intro h; exact base _ (by simpa only [summand] using h)
  | mul a b _ _ => intro h; exact base _ (by simpa only [summand] using h)
  | div a b _ _ => intro h; exact base _ (by simpa only [summand] using h)
  | npow a k _ => intro h; exact base _ (by simpa only [summand] using h)
  | rpow a r _ => intro h; exact base _ (by simpa only [summand] using h)
  | exp a _ => intro h; exact base _ (by simpa only [summand] using h)
  | log a _ => intro h; exact base _ (by simpa only [summand] using h)

/-! ## Acotación y consumo proporcional -/

mutual
/-- Acotada y `≥ 0` en `P ∩ [0, B]ⁿ` (`bx = true`) o en todo `P` (`bx = false`). -/
def bnd (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (bx : Bool) : KExpr n p → Bool
  | .const _ => false
  | .qconst q => decide (0 ≤ q)
  | .var _ => bx
  | .par j => pos j
  | .add a b => (bnd pos ub bx a && bnd pos ub bx b) ||
      (varfree (.add a b) && sNonneg pos ub (.add a b))
  | .sub a b => (qge1 a && expLe1 pos ub b) || subub pos ub a b
  | .mul a b => bnd pos ub bx a && bnd pos ub bx b
  | .div a d => (varfree (.div a d) && sNonneg pos ub (.div a d)) ||
      (bnd pos ub bx a && lowerpos pos d) || satb pos ub bx d a || bpair pos ub bx a d
  | .npow a _ => bnd pos ub bx a
  | .rpow a r => varfree (.rpow a r) && sNonneg pos ub (.rpow a r)
  | .exp a => varfree a || snp pos ub a
  | .log a => qge1 a

/-- `a/d` acotada: `a` contiene como factor un sumando de `d` (término saturante). -/
def satb (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (bx : Bool) (d : KExpr n p) : KExpr n p → Bool
  | .mul u v => summand pos ub (.mul u v) d || (satb pos ub bx d u && bnd pos ub bx v) ||
      (bnd pos ub bx u && satb pos ub bx d v)
  | .const c => summand pos ub (.const c) d
  | .qconst q => summand pos ub (.qconst q) d
  | .var j => summand pos ub (.var j) d
  | .par j => summand pos ub (.par j) d
  | .add a b => summand pos ub (.add a b) d
  | .sub a b => summand pos ub (.sub a b) d
  | .div a b => summand pos ub (.div a b) d
  | .npow a k => summand pos ub (.npow a k) d
  | .rpow a r => summand pos ub (.rpow a r) d
  | .exp a => summand pos ub (.exp a) d
  | .log a => summand pos ub (.log a) d

/-- `(a₁a₂)/(d₁d₂) = (a₁/d₁)(a₂/d₂)` (o emparejado al revés), cada factor acotado. -/
def bpair (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (bx : Bool) : KExpr n p → KExpr n p → Bool
  | .mul a1 a2, .mul d1 d2 =>
      (((bnd pos ub bx a1 && lowerpos pos d1) || satb pos ub bx d1 a1 || bpair pos ub bx a1 d1) &&
        ((bnd pos ub bx a2 && lowerpos pos d2) || satb pos ub bx d2 a2 || bpair pos ub bx a2 d2)) ||
      (((bnd pos ub bx a1 && lowerpos pos d2) || satb pos ub bx d2 a1 || bpair pos ub bx a1 d2) &&
        ((bnd pos ub bx a2 && lowerpos pos d1) || satb pos ub bx d1 a2 || bpair pos ub bx a2 d1))
  | _, _ => false
end

mutual
/-- Consumo proporcional: `0 ≤ e ≤ K·yᵢ` en `P ∩ [0, B]ⁿ`. -/
def cons (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (i : Fin n) : KExpr n p → Bool
  | .var j => decide (j = i)
  | .mul a b => (cons pos ub i a && bnd pos ub true b) || (bnd pos ub true a && cons pos ub i b)
  | .npow a k => decide (1 ≤ k) && cons pos ub i a && bnd pos ub true a
  | .div a d => (cons pos ub i a && lowerpos pos d) || cpair pos ub i a d
  | _ => false

/-- `(a₁a₂)/(d₁d₂)` con un factor proporcional a `yᵢ` y el otro acotado. -/
def cpair (pos : Fin p → Bool) (ub : Fin p → Option ℚ × Option ℚ) (i : Fin n) : KExpr n p → KExpr n p → Bool
  | .mul a1 a2, .mul d1 d2 =>
      ((((cons pos ub i a1 && lowerpos pos d1) || cpair pos ub i a1 d1) &&
          ((bnd pos ub true a2 && lowerpos pos d2) || satb pos ub true d2 a2 || bpair pos ub true a2 d2)) ||
        (((bnd pos ub true a1 && lowerpos pos d1) || satb pos ub true d1 a1 || bpair pos ub true a1 d1) &&
          ((cons pos ub i a2 && lowerpos pos d2) || cpair pos ub i a2 d2))) ||
      ((((cons pos ub i a1 && lowerpos pos d2) || cpair pos ub i a1 d2) &&
          ((bnd pos ub true a2 && lowerpos pos d1) || satb pos ub true d1 a2 || bpair pos ub true a2 d1)) ||
        (((bnd pos ub true a1 && lowerpos pos d2) || satb pos ub true d2 a1 || bpair pos ub true a1 d2) &&
          ((cons pos ub i a2 && lowerpos pos d1) || cpair pos ub i a2 d1)))
  | _, _ => false
end

variable (sx) in
/-- `0 ≤ e ≤ M` en `P` (y en la caja `[0, B]ⁿ` si `bx`). -/
def BndB (θ : EuclideanSpace ℝ (Fin p)) (bx : Bool) (e : KExpr n p) : Prop :=
  ∀ B : ℝ, ∃ M : ℝ, ∀ y, SPos sx y → (bx = true → ∀ j, y j ≤ B) →
    0 ≤ e.eval (y, θ) ∧ e.eval (y, θ) ≤ M

variable (sx) in
/-- `0 ≤ e ≤ K·yᵢ` en `P ∩ [0, B]ⁿ`. -/
def ConsB (θ : EuclideanSpace ℝ (Fin p)) (i : Fin n) (e : KExpr n p) : Prop :=
  ∀ B : ℝ, ∃ K : ℝ, 0 ≤ K ∧ ∀ y, SPos sx y → (∀ j, y j ≤ B) →
    0 ≤ e.eval (y, θ) ∧ e.eval (y, θ) ≤ K * y i

lemma bndB_const {bx : Bool} {e : KExpr n p} (hθ : PP pos ub θ)
    (h : (varfree e && sNonneg pos ub e) = true) : BndB sx θ bx e := by
  simp only [Bool.and_eq_true] at h
  intro B
  refine ⟨e.eval (0, θ), fun y hy _ => ⟨sNonneg_sound hy.1 hθ e h.2, ?_⟩⟩
  rw [eval_varfree e h.1 y 0 θ]

lemma bndB_div_lowerpos {bx : Bool} {a d : KExpr n p} (hθ : PP pos ub θ)
    (ha : BndB sx θ bx a) (hd : lowerpos pos d = true) : BndB sx θ bx (.div a d) := by
  intro B
  obtain ⟨M, hM⟩ := ha B
  refine ⟨M / lowval pos θ d, fun y hy hB => ?_⟩
  obtain ⟨a0, aM⟩ := hM y hy hB
  obtain ⟨l1, l2⟩ := lowerpos_sound hy.1 hθ.1 d hd
  show 0 ≤ a.eval (y, θ) / d.eval (y, θ) ∧ a.eval (y, θ) / d.eval (y, θ) ≤ _
  refine ⟨div_nonneg a0 (l1.le.trans l2), ?_⟩
  calc a.eval (y, θ) / d.eval (y, θ) ≤ a.eval (y, θ) / lowval pos θ d :=
        div_le_div_of_nonneg_left a0 l1 l2
    _ ≤ M / lowval pos θ d := div_le_div_of_nonneg_right aM l1.le

lemma bndB_summand {bx : Bool} {a d : KExpr n p} (hθ : PP pos ub θ)
    (h : summand pos ub a d = true) : BndB sx θ bx (.div a d) := by
  intro B
  refine ⟨1, fun y hy _ => ?_⟩
  obtain ⟨a0, ad⟩ := summand_sound hy.1 hθ a d h
  show 0 ≤ a.eval (y, θ) / d.eval (y, θ) ∧ a.eval (y, θ) / d.eval (y, θ) ≤ 1
  exact ⟨div_nonneg a0 (a0.trans ad), div_le_one_of_le₀ ad (a0.trans ad)⟩

lemma bndB_mul {bx : Bool} {a b : KExpr n p} (ha : BndB sx θ bx a) (hb : BndB sx θ bx b) :
    BndB sx θ bx (.mul a b) := by
  intro B
  obtain ⟨Ma, hMa⟩ := ha B
  obtain ⟨Mb, hMb⟩ := hb B
  refine ⟨Ma * Mb, fun y hy hB => ?_⟩
  obtain ⟨a0, aM⟩ := hMa y hy hB
  obtain ⟨b0, bM⟩ := hMb y hy hB
  exact ⟨mul_nonneg a0 b0, mul_le_mul aM bM b0 (a0.trans aM)⟩

lemma bndB_add {bx : Bool} {a b : KExpr n p} (ha : BndB sx θ bx a) (hb : BndB sx θ bx b) :
    BndB sx θ bx (.add a b) := by
  intro B
  obtain ⟨Ma, hMa⟩ := ha B
  obtain ⟨Mb, hMb⟩ := hb B
  refine ⟨Ma + Mb, fun y hy hB => ?_⟩
  obtain ⟨a0, aM⟩ := hMa y hy hB
  obtain ⟨b0, bM⟩ := hMb y hy hB
  exact ⟨add_nonneg a0 b0, add_le_add aM bM⟩

/-- `(u·v)/d = (u/d)·v`. -/
lemma bndB_frac_mul_l {bx : Bool} {u v d : KExpr n p} (hu : BndB sx θ bx (.div u d))
    (hv : BndB sx θ bx v) : BndB sx θ bx (.div (.mul u v) d) := by
  have := bndB_mul hu hv
  intro B
  obtain ⟨M, hM⟩ := this B
  refine ⟨M, fun y hy hB => ?_⟩
  have e : (KExpr.div (.mul u v) d).eval (y, θ) = (KExpr.mul (.div u d) v).eval (y, θ) := by
    show u.eval (y, θ) * v.eval (y, θ) / d.eval (y, θ) = u.eval (y, θ) / d.eval (y, θ) * v.eval (y, θ)
    ring
  rw [e]; exact hM y hy hB

/-- `(u·v)/d = u·(v/d)`. -/
lemma bndB_frac_mul_r {bx : Bool} {u v d : KExpr n p} (hu : BndB sx θ bx u)
    (hv : BndB sx θ bx (.div v d)) : BndB sx θ bx (.div (.mul u v) d) := by
  have := bndB_mul hu hv
  intro B
  obtain ⟨M, hM⟩ := this B
  refine ⟨M, fun y hy hB => ?_⟩
  have e : (KExpr.div (.mul u v) d).eval (y, θ) = (KExpr.mul u (.div v d)).eval (y, θ) := by
    show u.eval (y, θ) * v.eval (y, θ) / d.eval (y, θ) = u.eval (y, θ) * (v.eval (y, θ) / d.eval (y, θ))
    ring
  rw [e]; exact hM y hy hB

lemma bndB_pair {bx : Bool} {a1 a2 d1 d2 : KExpr n p} (h1 : BndB sx θ bx (.div a1 d1))
    (h2 : BndB sx θ bx (.div a2 d2)) : BndB sx θ bx (.div (.mul a1 a2) (.mul d1 d2)) := by
  have := bndB_mul h1 h2
  intro B
  obtain ⟨M, hM⟩ := this B
  refine ⟨M, fun y hy hB => ?_⟩
  have e : (KExpr.div (.mul a1 a2) (.mul d1 d2)).eval (y, θ)
      = (KExpr.mul (.div a1 d1) (.div a2 d2)).eval (y, θ) := mul_div_mul_comm _ _ _ _
  rw [e]; exact hM y hy hB

lemma bndB_pair' {bx : Bool} {a1 a2 d1 d2 : KExpr n p} (h1 : BndB sx θ bx (.div a1 d2))
    (h2 : BndB sx θ bx (.div a2 d1)) : BndB sx θ bx (.div (.mul a1 a2) (.mul d1 d2)) := by
  have := bndB_mul h1 h2
  intro B
  obtain ⟨M, hM⟩ := this B
  refine ⟨M, fun y hy hB => ?_⟩
  have e : (KExpr.div (.mul a1 a2) (.mul d1 d2)).eval (y, θ)
      = (KExpr.mul (.div a1 d2) (.div a2 d1)).eval (y, θ) := by
    show a1.eval (y, θ) * a2.eval (y, θ) / (d1.eval (y, θ) * d2.eval (y, θ)) = _
    rw [mul_comm (d1.eval (y, θ)), mul_div_mul_comm]; rfl
  rw [e]; exact hM y hy hB

lemma consB_mul_l {i : Fin n} {a b : KExpr n p} (ha : ConsB sx θ i a) (hb : BndB sx θ true b) :
    ConsB sx θ i (.mul a b) := by
  intro B
  obtain ⟨K, hK, hKa⟩ := ha B
  obtain ⟨M, hM⟩ := hb B
  refine ⟨K * max M 0, mul_nonneg hK (le_max_right _ _), fun y hy hB => ?_⟩
  obtain ⟨a0, aK⟩ := hKa y hy hB
  obtain ⟨b0, bM⟩ := hM y hy (fun _ => hB)
  refine ⟨mul_nonneg a0 b0, ?_⟩
  show a.eval (y, θ) * b.eval (y, θ) ≤ _
  calc a.eval (y, θ) * b.eval (y, θ) ≤ (K * y i) * max M 0 :=
        mul_le_mul aK (bM.trans (le_max_left _ _)) b0 (mul_nonneg hK (hy.1 i))
    _ = K * max M 0 * y i := by ring

lemma consB_mul_r {i : Fin n} {a b : KExpr n p} (ha : BndB sx θ true a) (hb : ConsB sx θ i b) :
    ConsB sx θ i (.mul a b) := by
  have := consB_mul_l hb ha
  intro B
  obtain ⟨K, hK, h⟩ := this B
  refine ⟨K, hK, fun y hy hB => ?_⟩
  have e : (KExpr.mul a b).eval (y, θ) = (KExpr.mul b a).eval (y, θ) := mul_comm _ _
  rw [e]; exact h y hy hB

lemma consB_div_lowerpos {i : Fin n} {a d : KExpr n p} (hθ : PP pos ub θ)
    (ha : ConsB sx θ i a) (hd : lowerpos pos d = true) : ConsB sx θ i (.div a d) := by
  intro B
  obtain ⟨K, hK, hKa⟩ := ha B
  have hl : 0 < lowval pos θ d := (lowerpos_sound KineticCheck.nonneg_zero hθ.1 d hd).1
  refine ⟨K / lowval pos θ d, div_nonneg hK hl.le, fun y hy hB => ?_⟩
  obtain ⟨a0, aK⟩ := hKa y hy hB
  have l2 := (lowerpos_sound hy.1 hθ.1 d hd).2
  show 0 ≤ a.eval (y, θ) / d.eval (y, θ) ∧ a.eval (y, θ) / d.eval (y, θ) ≤ _
  refine ⟨div_nonneg a0 (hl.le.trans l2), ?_⟩
  calc a.eval (y, θ) / d.eval (y, θ) ≤ a.eval (y, θ) / lowval pos θ d :=
        div_le_div_of_nonneg_left a0 hl l2
    _ ≤ (K * y i) / lowval pos θ d := div_le_div_of_nonneg_right aK hl.le
    _ = K / lowval pos θ d * y i := by ring

lemma bndB_congr {bx : Bool} {e e' : KExpr n p} (he : ∀ y, e.eval (y, θ) = e'.eval (y, θ))
    (h : BndB sx θ bx e') : BndB sx θ bx e := by
  intro B
  obtain ⟨M, hM⟩ := h B
  exact ⟨M, fun y hy hB => by rw [he]; exact hM y hy hB⟩

lemma consB_congr {i : Fin n} {e e' : KExpr n p} (he : ∀ y, e.eval (y, θ) = e'.eval (y, θ))
    (h : ConsB sx θ i e') : ConsB sx θ i e := by
  intro B
  obtain ⟨K, hK, hM⟩ := h B
  exact ⟨K, hK, fun y hy hB => by rw [he]; exact hM y hy hB⟩

lemma eval_pair (a1 a2 d1 d2 : KExpr n p) (z) :
    (KExpr.div (.mul a1 a2) (.mul d1 d2)).eval z = (KExpr.mul (.div a1 d1) (.div a2 d2)).eval z :=
  mul_div_mul_comm _ _ _ _

lemma eval_pair' (a1 a2 d1 d2 : KExpr n p) (z) :
    (KExpr.div (.mul a1 a2) (.mul d1 d2)).eval z = (KExpr.mul (.div a1 d2) (.div a2 d1)).eval z := by
  show a1.eval z * a2.eval z / (d1.eval z * d2.eval z) = _
  rw [mul_comm (d1.eval z), mul_div_mul_comm]; rfl

lemma consB_var (i : Fin n) : ConsB sx θ i (.var i) := by
  intro B
  refine ⟨1, zero_le_one, fun y hy _ => ⟨hy.1 i, ?_⟩⟩
  show y i ≤ 1 * y i; rw [one_mul]

lemma consB_npow {i : Fin n} {a : KExpr n p} {k : ℕ} (hk : 1 ≤ k) (ha : ConsB sx θ i a)
    (hb : BndB sx θ true a) : ConsB sx θ i (.npow a k) := by
  obtain ⟨m, rfl⟩ : ∃ m, k = m + 1 := ⟨k - 1, by omega⟩
  intro B
  obtain ⟨K, hK, hKa⟩ := ha B
  obtain ⟨M, hM⟩ := hb B
  refine ⟨max M 0 ^ m * K, mul_nonneg (pow_nonneg (le_max_right _ _) _) hK,
    fun y hy hB => ?_⟩
  obtain ⟨a0, aK⟩ := hKa y hy hB
  obtain ⟨_, aM⟩ := hM y hy (fun _ => hB)
  refine ⟨pow_nonneg a0 _, ?_⟩
  show a.eval (y, θ) ^ (m + 1) ≤ _
  rw [pow_succ]
  calc a.eval (y, θ) ^ m * a.eval (y, θ) ≤ max M 0 ^ m * (K * y i) :=
        mul_le_mul (pow_le_pow_left₀ a0 (aM.trans (le_max_left _ _)) m) aK a0
          (pow_nonneg (le_max_right _ _) _)
    _ = _ := by ring

lemma bndB_npow {bx : Bool} {a : KExpr n p} (k : ℕ) (ha : BndB sx θ bx a) :
    BndB sx θ bx (.npow a k) := by
  intro B
  obtain ⟨M, hM⟩ := ha B
  refine ⟨max M 0 ^ k, fun y hy hB => ?_⟩
  obtain ⟨a0, aM⟩ := hM y hy hB
  exact ⟨pow_nonneg a0 k, pow_le_pow_left₀ a0 (aM.trans (le_max_left _ _)) k⟩

lemma bndB_exp_np {bx : Bool} {a : KExpr n p} (hθ : PP pos ub θ) (h : snp pos ub a = true) :
    BndB sx θ bx (.exp a) := by
  intro B
  refine ⟨1, fun y hy _ => ⟨(Real.exp_pos _).le, ?_⟩⟩
  exact Real.exp_le_one_iff.2 (snp_sound hy.1 hθ a h)

lemma bndB_var {j : Fin n} : BndB sx θ true (.var j) := by
  intro B
  exact ⟨B, fun y hy hB => ⟨hy.1 j, hB rfl j⟩⟩

/-- Factor acotado `a/d`. -/
lemma bq_of {bx : Bool} {a d : KExpr n p} (hθ : PP pos ub θ)
    (hb : bnd pos ub bx a = true → BndB sx θ bx a)
    (hs : satb pos ub bx d a = true → BndB sx θ bx (.div a d))
    (hp : bpair pos ub bx a d = true → BndB sx θ bx (.div a d))
    (h : ((bnd pos ub bx a = true ∧ lowerpos pos d = true) ∨ satb pos ub bx d a = true) ∨
      bpair pos ub bx a d = true) : BndB sx θ bx (.div a d) := by
  rcases h with (⟨h1, h2⟩ | h) | h
  · exact bndB_div_lowerpos hθ (hb h1) h2
  · exact hs h
  · exact hp h

/-- Factor proporcional `a/d ≤ K·yᵢ`. -/
lemma cq_of {i : Fin n} {a d : KExpr n p} (hθ : PP pos ub θ)
    (hc : cons pos ub i a = true → ConsB sx θ i a)
    (hp : cpair pos ub i a d = true → ConsB sx θ i (.div a d))
    (h : (cons pos ub i a = true ∧ lowerpos pos d = true) ∨ cpair pos ub i a d = true) :
    ConsB sx θ i (.div a d) := by
  rcases h with ⟨h1, h2⟩ | h
  · exact consB_div_lowerpos hθ (hc h1) h2
  · exact hp h

/-- **Corrección de los comprobadores de acotación y de consumo proporcional.** -/
theorem bnd_sound (hθ : PP pos ub θ) : ∀ e : KExpr n p,
    (∀ bx, bnd pos ub bx e = true → BndB sx θ bx e) ∧
    (∀ bx d, satb pos ub bx d e = true → BndB sx θ bx (.div e d)) ∧
    (∀ bx d, bpair pos ub bx e d = true → BndB sx θ bx (.div e d)) ∧
    (∀ i, cons pos ub i e = true → ConsB sx θ i e) ∧
    (∀ i d, cpair pos ub i e d = true → ConsB sx θ i (.div e d)) := by
  have sat0 : ∀ (e : KExpr n p) bx d, summand pos ub e d = true → BndB sx θ bx (.div e d) :=
    fun e bx d h => bndB_summand hθ h
  intro e
  induction e with
  | mul u v ihu ihv =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd, Bool.and_eq_true] at h
        exact bndB_mul (ihu.1 bx h.1) (ihv.1 bx h.2)
      · simp only [satb, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with (h | ⟨h1, h2⟩) | ⟨h1, h2⟩
        · exact sat0 _ bx d h
        · exact bndB_frac_mul_l (ihu.2.1 bx d h1) (ihv.1 bx h2)
        · exact bndB_frac_mul_r (ihu.1 bx h1) (ihv.2.1 bx d h2)
      · cases d with
        | mul d1 d2 =>
            simp only [bpair, Bool.or_eq_true, Bool.and_eq_true] at h
            rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
            · exact bndB_congr (fun y => eval_pair u v d1 d2 (y, θ)) (bndB_mul
                (bq_of hθ (ihu.1 bx) (ihu.2.1 bx d1) (ihu.2.2.1 bx d1) h1)
                (bq_of hθ (ihv.1 bx) (ihv.2.1 bx d2) (ihv.2.2.1 bx d2) h2))
            · exact bndB_congr (fun y => eval_pair' u v d1 d2 (y, θ)) (bndB_mul
                (bq_of hθ (ihu.1 bx) (ihu.2.1 bx d2) (ihu.2.2.1 bx d2) h1)
                (bq_of hθ (ihv.1 bx) (ihv.2.1 bx d1) (ihv.2.2.1 bx d1) h2))
        | _ => simp [bpair] at h
      · simp only [cons, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
        · exact consB_mul_l (ihu.2.2.2.1 i h1) (ihv.1 true h2)
        · exact consB_mul_r (ihu.1 true h1) (ihv.2.2.2.1 i h2)
      · cases d with
        | mul d1 d2 =>
            simp only [cpair, Bool.or_eq_true, Bool.and_eq_true] at h
            rcases h with ((⟨h1, h2⟩ | ⟨h1, h2⟩) | (⟨h1, h2⟩ | ⟨h1, h2⟩))
            · exact consB_congr (fun y => eval_pair u v d1 d2 (y, θ)) (consB_mul_l
                (cq_of hθ (ihu.2.2.2.1 i) (ihu.2.2.2.2 i d1) h1)
                (bq_of hθ (ihv.1 true) (ihv.2.1 true d2) (ihv.2.2.1 true d2) h2))
            · exact consB_congr (fun y => eval_pair u v d1 d2 (y, θ)) (consB_mul_r
                (bq_of hθ (ihu.1 true) (ihu.2.1 true d1) (ihu.2.2.1 true d1) h1)
                (cq_of hθ (ihv.2.2.2.1 i) (ihv.2.2.2.2 i d2) h2))
            · exact consB_congr (fun y => eval_pair' u v d1 d2 (y, θ)) (consB_mul_l
                (cq_of hθ (ihu.2.2.2.1 i) (ihu.2.2.2.2 i d2) h1)
                (bq_of hθ (ihv.1 true) (ihv.2.1 true d1) (ihv.2.2.1 true d1) h2))
            · exact consB_congr (fun y => eval_pair' u v d1 d2 (y, θ)) (consB_mul_r
                (bq_of hθ (ihu.1 true) (ihu.2.1 true d2) (ihu.2.2.1 true d2) h1)
                (cq_of hθ (ihv.2.2.2.1 i) (ihv.2.2.2.2 i d1) h2))
        | _ => simp [cpair] at h
  | div a d iha ihd =>
      refine ⟨fun bx h => ?_, fun bx d' h => ?_, fun bx d' h => ?_, fun i h => ?_,
        fun i d' h => ?_⟩
      · simp only [bnd, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with ((h | ⟨h1, h2⟩) | h) | h
        · exact bndB_const hθ (by simp [h.1, h.2])
        · exact bndB_div_lowerpos hθ (iha.1 bx h1) h2
        · exact iha.2.1 bx d h
        · exact iha.2.2.1 bx d h
      · simp only [satb] at h; exact sat0 _ bx d' h
      · simp [bpair] at h
      · simp only [cons, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with ⟨h1, h2⟩ | h
        · exact consB_div_lowerpos hθ (iha.2.2.2.1 i h1) h2
        · exact iha.2.2.2.2 i d h
      · simp [cpair] at h
  | npow a k iha =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h; exact bndB_npow k (iha.1 bx h)
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp only [cons, Bool.and_eq_true, decide_eq_true_eq] at h
        exact consB_npow h.1.1 (iha.2.2.2.1 i h.1.2) (iha.1 true h.2)
      · simp [cpair] at h
  | add a b iha ihb =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · exact bndB_add (iha.1 bx h.1) (ihb.1 bx h.2)
        · exact bndB_const hθ (by simp only [Bool.and_eq_true]; exact h)
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | var j =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h; subst h; exact bndB_var
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp only [cons, decide_eq_true_eq] at h; subst h; exact consB_var j
      · simp [cpair] at h
  | qconst q =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h; exact bndB_const hθ (by simp [varfree, sNonneg, h])
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | par j =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h; exact bndB_const hθ (by simp [varfree, sNonneg, h])
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | const c =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp [bnd] at h
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | sub a b _ _ =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · have hs : sNonneg pos ub (.sub a b) = true := by simpa only [bnd, sNonneg] using h
        simp only [bnd, Bool.or_eq_true, Bool.and_eq_true] at h
        rcases h with h | h
        · cases a with
          | qconst q =>
              intro B
              refine ⟨(q : ℝ), fun y hy _ => ⟨sNonneg_sound hy.1 hθ _ hs, ?_⟩⟩
              have := (expLe1_sound hy.1 hθ b h.2).1
              show (q : ℝ) - b.eval _ ≤ q; linarith
          | _ => simp [qge1] at h
        · intro B
          refine ⟨a.eval (0, θ), fun y hy _ => ⟨sNonneg_sound hy.1 hθ _ hs, ?_⟩⟩
          have := (subub_sound hθ h y).2
          cases a with
          | qconst q => exact this
          | _ => simp [subub] at h
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | rpow a r _ =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h; exact bndB_const hθ h
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | exp a _ =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd, Bool.or_eq_true] at h
        rcases h with h | h
        · exact bndB_const hθ (by simp [varfree, sNonneg, h])
        · exact bndB_exp_np hθ h
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h
  | log a _ =>
      refine ⟨fun bx h => ?_, fun bx d h => ?_, fun bx d h => ?_, fun i h => ?_, fun i d h => ?_⟩
      · simp only [bnd] at h
        cases a with
        | qconst q => exact bndB_const hθ (by simp [varfree, sNonneg, h])
        | _ => simp [qge1] at h
      · simp only [satb] at h; exact sat0 _ bx d h
      · simp [bpair] at h
      · simp [cons] at h
      · simp [cpair] at h

/-! ## Red estricta: comprobación por términos -/

variable (pos ub sx) in
/-- Comprobación de un término en la región estricta. -/
def termOKS (t : KExpr n p × List (Fin n × ℚ)) : Bool :=
  sOk pos ub sx t.1 && t.2.all fun e =>
    if decide (e.2 < 0) then (if sx e.1 then cons pos ub e.1 t.1 else vanishes e.1 t.1)
    else (sNonneg pos ub t.1 || (!sx e.1 && vanishes e.1 t.1))

variable (pos ub sx) in
def checkNetS (Rx : List (KExpr n p × List (Fin n × ℚ))) : Bool := Rx.all (termOKS pos ub sx)

/-- Cuasi-positividad en `P` de la contribución de un término. -/
lemma term_qp {t : KExpr n p × List (Fin n × ℚ)} (ht : termOKS pos ub sx t = true)
    (hy : SPos sx y) (hθ : PP pos ub θ) (i : Fin n) (hyi : y i = 0) :
    0 ≤ ((coef t.2 i : ℚ) : ℝ) * t.1.eval (y, θ) := by
  have hsi : sx i = false := by
    cases h : sx i
    · rfl
    · have := hy.2 i h; rw [hyi] at this; exact absurd this (lt_irrefl 0)
  simp only [termOKS, Bool.and_eq_true, List.all_eq_true] at ht
  obtain ⟨-, hcol⟩ := ht
  unfold coef
  generalize t.2 = col0 at hcol ⊢
  induction col0 with
  | nil => simp
  | cons e col ih =>
      have he := hcol e List.mem_cons_self
      rw [List.map_cons, List.sum_cons, Rat.cast_add, add_mul]
      refine add_nonneg ?_ (ih fun e' h' => hcol e' (List.mem_cons_of_mem _ h'))
      by_cases hei : e.1 = i
      · rw [if_pos hei]
        rw [hei, hsi] at he
        by_cases hs : e.2 < 0
        · simp only [hs, decide_true, if_true, Bool.false_eq_true, if_false] at he
          rw [vanishes_sound i hyi t.1 he, mul_zero]
        · simp only [hs, decide_false, Bool.false_eq_true, if_false, Bool.not_false,
            Bool.true_and, Bool.or_eq_true] at he
          rcases he with he | he
          · exact mul_nonneg (by exact_mod_cast not_lt.1 hs) (sNonneg_sound hy.1 hθ t.1 he)
          · rw [vanishes_sound i hyi t.1 he, mul_zero]
      · rw [if_neg hei]; simp

/-- Consumo proporcional de una especie de `Σ` en la contribución de un término. -/
lemma term_decay (hθ : PP pos ub θ) {t : KExpr n p × List (Fin n × ℚ)}
    (ht : termOKS pos ub sx t = true) {i : Fin n} (hi : sx i = true) :
    ∀ B : ℝ, ∃ K : ℝ, 0 ≤ K ∧ ∀ y, SPos sx y → (∀ j, y j ≤ B) →
      -K * y i ≤ ((coef t.2 i : ℚ) : ℝ) * t.1.eval (y, θ) := by
  simp only [termOKS, Bool.and_eq_true, List.all_eq_true] at ht
  obtain ⟨-, hcol⟩ := ht
  unfold coef
  generalize t.2 = col0 at hcol ⊢
  induction col0 with
  | nil => intro B; exact ⟨0, le_rfl, fun y _ _ => by simp⟩
  | cons e col ih =>
      intro B
      obtain ⟨K1, hK1, h1⟩ := ih (fun e' h' => hcol e' (List.mem_cons_of_mem _ h')) B
      have he := hcol e List.mem_cons_self
      have hc : ∃ K2 : ℝ, 0 ≤ K2 ∧ ∀ y, SPos sx y → (∀ j, y j ≤ B) →
          -K2 * y i ≤ (((if e.1 = i then e.2 else 0 : ℚ)) : ℝ) * t.1.eval (y, θ) := by
        by_cases hei : e.1 = i
        · simp only [hei, if_true]
          rw [hei, hi] at he
          by_cases hs : e.2 < 0
          · simp only [hs, decide_true, if_true] at he
            obtain ⟨K, hK, hKc⟩ := (bnd_sound (sx := sx) hθ t.1).2.2.2.1 i he B
            have hs' : (e.2 : ℝ) < 0 := by exact_mod_cast hs
            refine ⟨-(e.2 : ℝ) * K, mul_nonneg (by linarith) hK, fun y hy hB => ?_⟩
            obtain ⟨v0, vK⟩ := hKc y hy hB
            nlinarith
          · simp only [hs, decide_false, Bool.false_eq_true, if_false, Bool.not_true,
              Bool.false_and, Bool.or_false] at he
            refine ⟨0, le_rfl, fun y hy _ => ?_⟩
            rw [neg_zero, zero_mul]
            exact mul_nonneg (by exact_mod_cast not_lt.1 hs) (sNonneg_sound hy.1 hθ t.1 he)
        · refine ⟨0, le_rfl, fun y _ _ => ?_⟩
          simp [hei]
      obtain ⟨K2, hK2, h2⟩ := hc
      refine ⟨K1 + K2, add_nonneg hK1 hK2, fun y hy hB => ?_⟩
      rw [List.map_cons, List.sum_cons, Rat.cast_add, add_mul]
      have e1 := h1 y hy hB
      have e2 := h2 y hy hB
      have : -(K1 + K2) * y i = -K1 * y i + -K2 * y i := by ring
      rw [this]; linarith

theorem checkNetS_sound {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkNetS pos ub sx Rx = true) (hθ : PP pos ub θ) :
    (∀ y, SPos sx y → (y, θ) ∈ domain (netF Rx)) ∧
    (∀ y, SPos sx y → ∀ i, y i = 0 → 0 ≤ field (netF Rx) y θ i) ∧
    (∀ B : ℝ, ∃ C : ℝ, 0 ≤ C ∧ ∀ y, SPos sx y → (∀ j, y j ≤ B) →
      ∀ i, sx i = true → -C * y i ≤ field (netF Rx) y θ i) := by
  simp only [checkNetS, List.all_eq_true] at h
  refine ⟨fun y hy i => ok_netExpr Rx i _ fun t ht => ?_, fun y hy i hyi => ?_, fun B => ?_⟩
  · have := h t ht
    simp only [termOKS, Bool.and_eq_true] at this
    exact sOk_sound hy hθ t.1 this.1
  · show 0 ≤ (netExpr Rx i).eval (y, θ)
    rw [eval_netExpr]
    apply List.sum_nonneg
    intro x hx
    obtain ⟨t, ht, rfl⟩ := List.mem_map.1 hx
    exact term_qp (h t ht) hy hθ i hyi
  · -- por especie
    have hsp : ∀ i, ∃ K : ℝ, 0 ≤ K ∧ (sx i = true → ∀ y, SPos sx y → (∀ j, y j ≤ B) →
        -K * y i ≤ (netExpr Rx i).eval (y, θ)) := by
      intro i
      by_cases hi : sx i = true
      · suffices H : ∀ R : List (KExpr n p × List (Fin n × ℚ)), (∀ t ∈ R, termOKS pos ub sx t = true) →
            ∃ K : ℝ, 0 ≤ K ∧ ∀ y, SPos sx y → (∀ j, y j ≤ B) →
              -K * y i ≤ (R.map fun t => ((coef t.2 i : ℚ) : ℝ) * t.1.eval (y, θ)).sum by
          obtain ⟨K, hK, hKs⟩ := H Rx h
          exact ⟨K, hK, fun _ y hy hB => by rw [eval_netExpr]; exact hKs y hy hB⟩
        intro R hR
        induction R with
        | nil => exact ⟨0, le_rfl, fun y _ _ => by simp⟩
        | cons t R ih =>
            obtain ⟨K1, hK1, h1⟩ := ih fun t' h' => hR t' (List.mem_cons_of_mem _ h')
            obtain ⟨K2, hK2, h2⟩ := term_decay hθ (hR t List.mem_cons_self) hi B
            refine ⟨K2 + K1, add_nonneg hK2 hK1, fun y hy hB => ?_⟩
            rw [List.map_cons, List.sum_cons]
            have e1 := h1 y hy hB
            have e2 := h2 y hy hB
            have : -(K2 + K1) * y i = -K2 * y i + -K1 * y i := by ring
            rw [this]; linarith
      · exact ⟨0, le_rfl, fun h' => absurd h' hi⟩
    choose K hK0 hK using hsp
    refine ⟨∑ i, K i, Finset.sum_nonneg fun i _ => hK0 i, fun y hy hB i hi => ?_⟩
    have hle : K i ≤ ∑ j, K j :=
      Finset.single_le_sum (f := K) (fun j _ => hK0 j) (Finset.mem_univ i)
    have := hK i hi y hy hB
    have h2 : -(∑ j, K j) * y i ≤ -K i * y i := by nlinarith [hy.1 i]
    exact h2.trans this

/-! ## Crecimiento lineal en la región estricta -/

variable (pos ub) in
def growthOKS (c : Fin n → ℚ) (t : KExpr n p × List (Fin n × ℚ)) : Bool :=
  decide (wgt c t.2 = 0) || (decide (wgt c t.2 < 0) && sNonneg pos ub t.1) ||
    (decide (0 < wgt c t.2) && (linOK pos t.1 || bnd pos ub false t.1))

variable (pos ub) in
def checkGrowthS (c : Fin n → ℚ) (Rx : List (KExpr n p × List (Fin n × ℚ))) : Bool :=
  (List.finRange n).all (fun i => decide (1 ≤ c i)) && Rx.all (growthOKS pos ub c)

lemma term_growth (hθ : PP pos ub θ) {c : Fin n → ℚ} {t : KExpr n p × List (Fin n × ℚ)}
    (ht : growthOKS pos ub c t = true) :
    ∃ A Bt : ℝ, 0 ≤ A ∧ 0 ≤ Bt ∧ ∀ y, SPos sx y →
      ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ) ≤ A + Bt * ssum y := by
  simp only [growthOKS, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at ht
  rcases ht with (h0 | ⟨h0, h1⟩) | ⟨h0, h1 | h1⟩
  · exact ⟨0, 0, le_rfl, le_rfl, fun y _ => by rw [h0]; simp⟩
  · refine ⟨0, 0, le_rfl, le_rfl, fun y hy => ?_⟩
    have : ((wgt c t.2 : ℚ) : ℝ) < 0 := by exact_mod_cast h0
    rw [zero_add, zero_mul]
    exact mul_nonpos_of_nonpos_of_nonneg this.le (sNonneg_sound hy.1 hθ t.1 h1)
  · have hw : (0 : ℝ) < (wgt c t.2 : ℝ) := by exact_mod_cast h0
    obtain ⟨l1, l2, -⟩ := linBound_sound KineticCheck.nonneg_zero hθ.1 t.1 h1
    refine ⟨(wgt c t.2 : ℝ) * (linBound pos θ t.1).1, (wgt c t.2 : ℝ) * (linBound pos θ t.1).2,
      mul_nonneg hw.le l1, mul_nonneg hw.le l2, fun y hy => ?_⟩
    obtain ⟨-, -, l3⟩ := linBound_sound hy.1 hθ.1 t.1 h1
    nlinarith [mul_le_mul_of_nonneg_left l3 hw.le]
  · have hw : (0 : ℝ) < (wgt c t.2 : ℝ) := by exact_mod_cast h0
    obtain ⟨M, hM⟩ := (bnd_sound (sx := sx) hθ t.1).1 false h1 0
    refine ⟨(wgt c t.2 : ℝ) * max M 0, 0, mul_nonneg hw.le (le_max_right _ _), le_rfl,
      fun y hy => ?_⟩
    obtain ⟨-, vM⟩ := hM y hy (fun h => absurd h Bool.false_ne_true)
    rw [zero_mul, add_zero]
    exact mul_le_mul_of_nonneg_left (vM.trans (le_max_left _ _)) hw.le

theorem checkGrowthS_sound {c : Fin n → ℚ} {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkGrowthS pos ub c Rx = true) (hθ : PP pos ub θ) :
    ∃ a b : ℝ, 0 ≤ a ∧ 0 ≤ b ∧ ∀ y, SPos sx y →
      ∑ i, (c i : ℝ) * field (netF Rx) y θ i ≤ a + b * ∑ i, (c i : ℝ) * y i := by
  simp only [checkGrowthS, Bool.and_eq_true, List.all_eq_true, List.mem_finRange,
    true_implies, decide_eq_true_eq] at h
  obtain ⟨hc1, hR⟩ := h
  have H : ∀ R : List (KExpr n p × List (Fin n × ℚ)), (∀ t ∈ R, growthOKS pos ub c t = true) →
      ∃ a b : ℝ, 0 ≤ a ∧ 0 ≤ b ∧ ∀ y, SPos sx y →
        (R.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ)).sum ≤ a + b * ssum y := by
    intro R hR'
    induction R with
    | nil => exact ⟨0, 0, le_rfl, le_rfl, fun y _ => by simp⟩
    | cons t R ih =>
        obtain ⟨a1, b1, ha1, hb1, h1⟩ := ih fun t' h' => hR' t' (List.mem_cons_of_mem _ h')
        obtain ⟨a2, b2, ha2, hb2, h2⟩ := term_growth (sx := sx) hθ (hR' t List.mem_cons_self)
        refine ⟨a2 + a1, b2 + b1, add_nonneg ha2 ha1, add_nonneg hb2 hb1, fun y hy => ?_⟩
        rw [List.map_cons, List.sum_cons]
        have e1 := h1 y hy
        have e2 := h2 y hy
        have : a2 + a1 + (b2 + b1) * ssum y = (a2 + b2 * ssum y) + (a1 + b1 * ssum y) := by ring
        rw [this]; linarith
  obtain ⟨a, b, ha, hb, hab⟩ := H Rx hR
  refine ⟨a, b, ha, hb, fun y hy => ?_⟩
  have hsum : ∑ i, (c i : ℝ) * field (netF Rx) y θ i
      = (Rx.map fun t => ((wgt c t.2 : ℚ) : ℝ) * t.1.eval (y, θ)).sum :=
    sum_c_netExpr c Rx (y, θ)
  have hS : ssum y ≤ ∑ i, (c i : ℝ) * y i := by
    apply Finset.sum_le_sum
    intro i _
    have : (1 : ℝ) ≤ (c i : ℝ) := by exact_mod_cast hc1 i
    nlinarith [hy.1 i]
  rw [hsum]
  nlinarith [hab y hy, mul_le_mul_of_nonneg_left hS hb]

lemma c_ge_oneS {c : Fin n → ℚ} {Rx : List (KExpr n p × List (Fin n × ℚ))}
    (h : checkGrowthS pos ub c Rx = true) (i : Fin n) : (1 : ℝ) ≤ (c i : ℝ) := by
  simp only [checkGrowthS, Bool.and_eq_true, List.all_eq_true, List.mem_finRange,
    true_implies, decide_eq_true_eq] at h
  exact_mod_cast h.1 i

/-! ## Teoremas finales -/

/-- Existencia global con positividad estricta para una red comprobada. -/
theorem strict_exists (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNetS pos ub sx Rx = true) (c : Fin n → ℚ) (hG : checkGrowthS pos ub c Rx = true)
    {θ₀ : EuclideanSpace ℝ (Fin p)} (hθ₀ : PP pos ub θ₀)
    (x0 : EuclideanSpace ℝ (Fin n)) (hx0 : SPos sx x0) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = x0 ∧
      ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) θ₀) (Icc 0 T) t ∧
        SPos sx (x₀ t) := by
  obtain ⟨hdom, hqp, hdec⟩ := checkNetS_sound hN hθ₀
  obtain ⟨a, b, ha, hb, hgr⟩ := checkGrowthS_sound (sx := sx) hG hθ₀
  set U : Set (EuclideanSpace ℝ (Fin n)) := (fun y => (y, θ₀)) ⁻¹' domain (netF Rx)
  have hcont : Continuous fun y : EuclideanSpace ℝ (Fin n) => (y, θ₀) :=
    continuous_id.prodMk continuous_const
  have hU : IsOpen U := (isOpen_domain _).preimage hcont
  have hv : ContDiffOn ℝ 1 (fun y => field (netF Rx) y θ₀) U :=
    (contDiffOn_field (netF Rx)).comp (contDiff_id.prodMk contDiff_const).contDiffOn
      (fun y hy => hy)
  exact exists_global_solution_strict sx (fun y => field (netF Rx) y θ₀) hU hv
    (fun z hz => hdom z hz) (fun z hz i hi => hqp z hz i hi) hdec (fun i => (c i : ℝ))
    one_pos (c_ge_oneS hG) ha hb (fun z hz => hgr z hz) x0 hx0 hT

variable (pos ub sx) in
/-- Condición inicial `G(θ)`: bien definida, `≥ 0`, y `> 0` en `Σ`. -/
def checkInitS (G : Fin n → KExpr n p) : Bool :=
  checkInit pos G && (List.finRange n).all fun i => !sx i || isPos pos (G i)

lemma init_sPos {G : Fin n → KExpr n p} (h : checkInitS pos sx G = true)
    {θ₀ : EuclideanSpace ℝ (Fin p)} (hθ₀ : PP pos ub θ₀) : SPos sx (field G 0 θ₀) := by
  simp only [checkInitS, Bool.and_eq_true, List.all_eq_true, List.mem_finRange, true_implies,
    Bool.or_eq_true, Bool.not_eq_eq_eq_not, Bool.not_true] at h
  refine ⟨init_nonneg h.1 hθ₀.1, fun j hj => ?_⟩
  rcases h.2 j with h' | h'
  · rw [hj] at h'; exact absurd h' (by decide)
  · exact isPos_sound KineticCheck.nonneg_zero hθ₀.1 (G j) h'

/-- **Teorema final con positividad estricta (condición inicial `G(θ)`).** Sin condiciones
pendientes: la solución nominal existe en `[0, T]`, las especies de `Σ` permanecen `> 0`, las
demás `≥ 0`, la trayectoria queda en el dominio, las soluciones existen cerca de `θ₀` y la
trayectoria es diferenciable respecto a `θ`, con `S(0) = ∂G/∂θ`. -/
theorem strict_final_init (Rx : List (KExpr n p × List (Fin n × ℚ)))
    (hN : checkNetS pos ub sx Rx = true) (c : Fin n → ℚ) (hG : checkGrowthS pos ub c Rx = true)
    (G : Fin n → KExpr n p) (hI : checkInitS pos sx G = true)
    (θq : Fin p → ℚ) (hθ : checkPosParams pos θq = true)
    (hU : checkUB ub θq = true) {T : ℝ} (hT : 0 ≤ T) :
    ∃ x₀ : ℝ → EuclideanSpace ℝ (Fin n), x₀ 0 = field G 0 (qvec θq) ∧
      (∀ t ∈ Icc 0 T,
        HasDerivWithinAt x₀ (field (netF Rx) (x₀ t) (qvec θq)) (Icc 0 T) t ∧
        SPos sx (x₀ t) ∧ (x₀ t, qvec θq) ∈ domain (netF Rx)) ∧
      ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x (qvec θq) = x₀ ∧
        (∀ᶠ θ in 𝓝 (qvec θq), x θ 0 = field G 0 θ ∧
          ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field (netF Rx) (x θ t) θ) (Icc 0 T) t) ∧
        ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)),
          S 0 = fderiv ℝ (fun θ => field G 0 θ) (qvec θq) ∧
          ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) (qvec θq) := by
  have hθ₀ : PP pos ub (qvec θq) := ⟨posParams_qvec hθ, ub_qvec hU⟩
  obtain ⟨hdom, -, -⟩ := checkNetS_sound hN hθ₀
  obtain ⟨x₀, h0, hsol⟩ := strict_exists Rx hN c hG hθ₀ _ (init_sPos hI hθ₀) hT
  refine ⟨x₀, h0, fun t ht => ⟨(hsol t ht).1, (hsol t ht).2, hdom _ (hsol t ht).2⟩, ?_⟩
  simp only [checkInitS, Bool.and_eq_true] at hI
  obtain ⟨x, hx, hev, S, hS0, -, hS⟩ := kinetic_hasFDerivAt (netF Rx) hT x₀ (qvec θq)
    (fun t ht => (hsol t ht).1) (fun t ht => hdom _ (hsol t ht).2) (fun θ => field G 0 θ) _
    (init_differentiable hI.1 hθ₀.1).hasFDerivAt h0.symm
  exact ⟨x, hx, hev, S, hS0, hS⟩

end StrictNetwork

#print axioms StrictNetwork.bnd_sound
#print axioms StrictNetwork.checkNetS_sound
#print axioms StrictNetwork.checkGrowthS_sound
#print axioms StrictNetwork.strict_final_init
