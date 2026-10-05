import NominalCertificate
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.SpecialFunctions.ExpDeriv

/-!
# Hipótesis 1: los modelos cinéticos son C¹ (lenguaje de leyes de velocidad)

Los teoremas suponen que `f` es C¹ en un abierto `U` que contiene la trayectoria nominal. Aquí se
**demuestra** esa hipótesis para toda una clase de modelos: los construidos con constantes,
concentraciones, parámetros, `+`, `−`, `×`, `/`, potencias enteras, potencias reales y `exp`
(acción de masas, Michaelis–Menten, Hill, inhibición, activación, …).

* `KExpr`: sintaxis de una ley de velocidad (constantes reales `const` o racionales `qconst`,
  estas últimas para que los comprobadores de `KineticCheck` sean calculables); `eval`: su valor; `ok`: condición de buena
  definición (denominadores `≠ 0`, bases de potencias reales `> 0`).
* `isOpen_ok`, `contDiffAt_eval`: el conjunto donde la expresión está bien definida es abierto y
  allí la expresión es C^∞ (en particular C¹).
* `field`, `domain`: el campo vectorial `ẋᵢ = Fᵢ(x, θ)` y su dominio natural;
  `contDiffOn_field`: el campo es C^∞ en su dominio, que es abierto.
* `ok_of_noDen`: sin divisiones ni potencias reales (acción de masas pura) el dominio es todo
  el espacio; `ok_mm`, `ok_hill`, `ok_hillR`: Michaelis–Menten y Hill están bien definidas para
  concentraciones `≥ 0` (o `> 0` con exponente real) y constantes `K > 0`.
* `kinetic_hasFDerivAt`, `kinetic_local_cos`: los teoremas de diferenciabilidad y del certificado
  local de cos Δ para modelos cinéticos, con **la única hipótesis** de que la trayectoria nominal
  permanece en el dominio (p. ej. ningún denominador se anula sobre ella).
-/

open Set Filter Topology

namespace KineticRegularity

variable {n p : ℕ}

/-- Sintaxis de una ley de velocidad en las concentraciones `x : ℝⁿ` y parámetros `θ : ℝᵖ`. -/
inductive KExpr (n p : ℕ) : Type
  | const : ℝ → KExpr n p
  | qconst : ℚ → KExpr n p
  | var : Fin n → KExpr n p
  | par : Fin p → KExpr n p
  | add : KExpr n p → KExpr n p → KExpr n p
  | sub : KExpr n p → KExpr n p → KExpr n p
  | mul : KExpr n p → KExpr n p → KExpr n p
  | div : KExpr n p → KExpr n p → KExpr n p
  | npow : KExpr n p → ℕ → KExpr n p
  | rpow : KExpr n p → ℝ → KExpr n p
  | exp : KExpr n p → KExpr n p
  | log : KExpr n p → KExpr n p

namespace KExpr

/-- Valor de la expresión en `z = (x, θ)`. -/
noncomputable def eval : KExpr n p →
    (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) → ℝ)
  | const c => fun _ => c
  | qconst q => fun _ => (q : ℝ)
  | var i => fun z => z.1 i
  | par j => fun z => z.2 j
  | add a b => fun z => a.eval z + b.eval z
  | sub a b => fun z => a.eval z - b.eval z
  | mul a b => fun z => a.eval z * b.eval z
  | div a b => fun z => a.eval z / b.eval z
  | npow a k => fun z => a.eval z ^ k
  | rpow a r => fun z => a.eval z ^ r
  | exp a => fun z => Real.exp (a.eval z)
  | log a => fun z => Real.log (a.eval z)

/-- La expresión está bien definida (y es diferenciable) en `z`: denominadores no nulos y bases
de potencias reales positivas. -/
def ok : KExpr n p → (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) → Prop)
  | const _ => fun _ => True
  | qconst _ => fun _ => True
  | var _ => fun _ => True
  | par _ => fun _ => True
  | add a b => fun z => a.ok z ∧ b.ok z
  | sub a b => fun z => a.ok z ∧ b.ok z
  | mul a b => fun z => a.ok z ∧ b.ok z
  | div a b => fun z => a.ok z ∧ b.ok z ∧ b.eval z ≠ 0
  | npow a _ => fun z => a.ok z
  | rpow a _ => fun z => a.ok z ∧ 0 < a.eval z
  | exp a => fun z => a.ok z
  | log a => fun z => a.ok z ∧ 0 < a.eval z

/-- **Regularidad.** Donde la expresión está bien definida, es `C^k` para todo `k`. -/
theorem contDiffAt_eval (e : KExpr n p) {k : WithTop ℕ∞} :
    ∀ z, e.ok z → ContDiffAt ℝ k e.eval z := by
  induction e with
  | const c => intro z _; exact contDiffAt_const
  | qconst q => intro z _; exact contDiffAt_const
  | var i =>
      intro z _
      exact ((EuclideanSpace.proj i : EuclideanSpace ℝ (Fin n) →L[ℝ] ℝ).contDiff.comp
        contDiff_fst).contDiffAt
  | par j =>
      intro z _
      exact ((EuclideanSpace.proj j : EuclideanSpace ℝ (Fin p) →L[ℝ] ℝ).contDiff.comp
        contDiff_snd).contDiffAt
  | add a b ha hb => intro z h; exact (ha z h.1).add (hb z h.2)
  | sub a b ha hb => intro z h; exact (ha z h.1).sub (hb z h.2)
  | mul a b ha hb => intro z h; exact (ha z h.1).mul (hb z h.2)
  | div a b ha hb => intro z h; exact (ha z h.1).div (hb z h.2.1) h.2.2
  | npow a m ha => intro z h; exact (ha z h).pow m
  | rpow a r ha => intro z h; exact (ha z h.1).rpow_const_of_ne (ne_of_gt h.2)
  | exp a ha => intro z h; exact (ha z h).exp
  | log a ha => intro z h; exact (ha z h.1).log (ne_of_gt h.2)

/-- El conjunto donde la expresión está bien definida es **abierto**. -/
theorem isOpen_ok (e : KExpr n p) : IsOpen {z | e.ok z} := by
  induction e with
  | const c => exact isOpen_univ
  | qconst q => exact isOpen_univ
  | var i => exact isOpen_univ
  | par j => exact isOpen_univ
  | add a b ha hb => exact ha.inter hb
  | sub a b ha hb => exact ha.inter hb
  | mul a b ha hb => exact ha.inter hb
  | div a b ha hb =>
      have hc : ContinuousOn b.eval {z | b.ok z} := fun z hz =>
        (contDiffAt_eval b (k := 0) z hz).continuousAt.continuousWithinAt
      exact ha.inter (hc.isOpen_inter_preimage hb isOpen_compl_singleton)
  | npow a m ha => exact ha
  | rpow a r ha =>
      have hc : ContinuousOn a.eval {z | a.ok z} := fun z hz =>
        (contDiffAt_eval a (k := 0) z hz).continuousAt.continuousWithinAt
      exact hc.isOpen_inter_preimage ha isOpen_Ioi
  | exp a ha => exact ha
  | log a ha =>
      have hc : ContinuousOn a.eval {z | a.ok z} := fun z hz =>
        (contDiffAt_eval a (k := 0) z hz).continuousAt.continuousWithinAt
      exact hc.isOpen_inter_preimage ha isOpen_Ioi

/-- Expresiones sin denominadores ni potencias reales (acción de masas pura). -/
def noDen : KExpr n p → Prop
  | const _ => True
  | qconst _ => True
  | var _ => True
  | par _ => True
  | add a b => a.noDen ∧ b.noDen
  | sub a b => a.noDen ∧ b.noDen
  | mul a b => a.noDen ∧ b.noDen
  | div _ _ => False
  | npow a _ => a.noDen
  | rpow _ _ => False
  | exp a => a.noDen
  | log _ => False

/-- Acción de masas: la expresión está bien definida en todo el espacio. -/
theorem ok_of_noDen (e : KExpr n p) : e.noDen → ∀ z, e.ok z := by
  induction e with
  | const c => intro _ _; trivial
  | qconst q => intro _ _; trivial
  | var i => intro _ _; trivial
  | par j => intro _ _; trivial
  | add a b ha hb => intro h z; exact ⟨ha h.1 z, hb h.2 z⟩
  | sub a b ha hb => intro h z; exact ⟨ha h.1 z, hb h.2 z⟩
  | mul a b ha hb => intro h z; exact ⟨ha h.1 z, hb h.2 z⟩
  | div a b _ _ => intro h; exact h.elim
  | npow a m ha => intro h z; exact ha h z
  | rpow a r _ => intro h; exact h.elim
  | exp a ha => intro h z; exact ha h z
  | log a _ => intro h; exact h.elim

/-! ### Leyes de velocidad habituales -/

/-- Michaelis–Menten: `V x / (K + x)`. -/
def mm (V K x : KExpr n p) : KExpr n p := div (mul V x) (add K x)

/-- Hill con coeficiente entero: `V xᵐ / (Kᵐ + xᵐ)`. -/
def hill (V K x : KExpr n p) (m : ℕ) : KExpr n p :=
  div (mul V (npow x m)) (add (npow K m) (npow x m))

/-- Hill con coeficiente real: `V x^h / (K^h + x^h)`. -/
def hillR (V K x : KExpr n p) (h : ℝ) : KExpr n p :=
  div (mul V (rpow x h)) (add (rpow K h) (rpow x h))

theorem ok_mm {V K x : KExpr n p} {z} (hV : V.ok z) (hK : K.ok z) (hx : x.ok z)
    (hK0 : 0 < K.eval z) (hx0 : 0 ≤ x.eval z) : (mm V K x).ok z :=
  ⟨⟨hV, hx⟩, ⟨hK, hx⟩, by
    show K.eval z + x.eval z ≠ 0
    linarith⟩

theorem ok_hill {V K x : KExpr n p} {z} (m : ℕ) (hV : V.ok z) (hK : K.ok z) (hx : x.ok z)
    (hK0 : 0 < K.eval z) (hx0 : 0 ≤ x.eval z) : (hill V K x m).ok z :=
  ⟨⟨hV, hx⟩, ⟨hK, hx⟩, by
    show K.eval z ^ m + x.eval z ^ m ≠ 0
    have := pow_pos hK0 m
    have := pow_nonneg hx0 m
    linarith⟩

theorem ok_hillR {V K x : KExpr n p} {z} (h : ℝ) (hV : V.ok z) (hK : K.ok z) (hx : x.ok z)
    (hK0 : 0 < K.eval z) (hx0 : 0 < x.eval z) : (hillR V K x h).ok z :=
  ⟨⟨hV, ⟨hx, hx0⟩⟩, ⟨⟨hK, hK0⟩, ⟨hx, hx0⟩⟩, by
    show K.eval z ^ h + x.eval z ^ h ≠ 0
    have := Real.rpow_pos_of_pos hK0 h
    have := Real.rpow_pos_of_pos hx0 h
    linarith⟩

end KExpr

open KExpr

/-! ## El campo vectorial de un modelo cinético -/

/-- Campo `ẋᵢ = Fᵢ(x, θ)` definido por las leyes de velocidad `F`. -/
noncomputable def field (F : Fin n → KExpr n p) (x : EuclideanSpace ℝ (Fin n))
    (θ : EuclideanSpace ℝ (Fin p)) : EuclideanSpace ℝ (Fin n) :=
  (EuclideanSpace.equiv (Fin n) ℝ).symm (fun i => (F i).eval (x, θ))

/-- Dominio natural: todas las componentes están bien definidas. -/
def domain (F : Fin n → KExpr n p) : Set (EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p)) :=
  {z | ∀ i, (F i).ok z}

theorem isOpen_domain (F : Fin n → KExpr n p) : IsOpen (domain F) := by
  have : domain F = ⋂ i, {z | (F i).ok z} := by ext z; simp [domain]
  rw [this]
  exact isOpen_iInter_of_finite fun i => isOpen_ok (F i)

/-- **El campo de un modelo cinético es C^k (en particular C¹) en su dominio abierto.** -/
theorem contDiffOn_field (F : Fin n → KExpr n p) {k : WithTop ℕ∞} :
    ContDiffOn ℝ k (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
      field F z.1 z.2) (domain F) := by
  intro z hz
  apply ContDiffAt.contDiffWithinAt
  have hpi : ContDiffAt ℝ k (fun z => fun i => (F i).eval z) z :=
    contDiffAt_pi.2 fun i => contDiffAt_eval (F i) z (hz i)
  exact (EuclideanSpace.equiv (Fin n) ℝ).symm.contDiff.contDiffAt.comp z hpi

/-- Acción de masas pura: el dominio es todo el espacio. -/
theorem domain_eq_univ (F : Fin n → KExpr n p) (h : ∀ i, (F i).noDen) : domain F = univ :=
  eq_univ_of_forall fun z i => ok_of_noDen (F i) (h i) z

/-- **Diferenciabilidad de la trayectoria para modelos cinéticos.** Única hipótesis sobre el
modelo: la trayectoria nominal permanece en el dominio (ningún denominador se anula y las bases
de potencias reales son positivas a lo largo de ella). -/
theorem kinetic_hasFDerivAt (F : Fin n → KExpr n p)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field F (x₀ t) θ₀) (Icc 0 T) t)
    (hdom : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ domain F)
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0) :
    ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field F (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S 0 = D0 ∧
        (∀ t ∈ Icc 0 T, HasDerivWithinAt S
          ((fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
              field F z.1 z.2) (x₀ t, θ₀)).comp (ContinuousLinearMap.inl ℝ _ _) ∘L S t
            + (fderiv ℝ (fun z : EuclideanSpace ℝ (Fin n) × EuclideanSpace ℝ (Fin p) =>
              field F z.1 z.2) (x₀ t, θ₀)).comp (ContinuousLinearMap.inr ℝ _ _))
          (Icc 0 T) t) ∧
        ∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S t) θ₀ :=
  LocalExistence.hasFDerivAt_of_nominal_solution (field F) (isOpen_domain F)
    (contDiffOn_field F) hT x₀ θ₀ hx₀ hdom x0 D0 hx0 hx00

/-- **Certificado local de cos Δ para modelos cinéticos**, con la misma única hipótesis. -/
theorem kinetic_local_cos {N : ℕ} (F : Fin n → KExpr n p)
    {T : ℝ} (hT : 0 ≤ T) (x₀ : ℝ → EuclideanSpace ℝ (Fin n)) (θ₀ : EuclideanSpace ℝ (Fin p))
    (hx₀ : ∀ t ∈ Icc 0 T, HasDerivWithinAt x₀ (field F (x₀ t) θ₀) (Icc 0 T) t)
    (hdom : ∀ t ∈ Icc 0 T, (x₀ t, θ₀) ∈ domain F)
    (x0 : EuclideanSpace ℝ (Fin p) → EuclideanSpace ℝ (Fin n))
    (D0 : EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n))
    (hx0 : HasFDerivAt x0 D0 θ₀) (hx00 : x0 θ₀ = x₀ 0)
    (tk : Fin N → ℝ) (htk : ∀ k, tk k ∈ Icc 0 T) :
    ∃ x : EuclideanSpace ℝ (Fin p) → ℝ → EuclideanSpace ℝ (Fin n), x θ₀ = x₀ ∧
      (∀ᶠ θ in 𝓝 θ₀, x θ 0 = x0 θ ∧
        ∀ t ∈ Icc 0 T, HasDerivWithinAt (x θ) (field F (x θ t) θ) (Icc 0 T) t) ∧
      ∃ S₀ : ℝ → (EuclideanSpace ℝ (Fin p) →L[ℝ] EuclideanSpace ℝ (Fin n)), S₀ 0 = D0 ∧
        (∀ t ∈ Icc 0 T, HasFDerivAt (fun θ => x θ t) (S₀ t) θ₀) ∧
        ∀ (Sset : Finset (Fin p)) (h : EuclideanSpace ℝ (Fin p)) {c : ℝ},
          CertifiedFiniteODE.sampledCLM S₀ tk h ≠ 0 →
          CertifiedFiniteODE.sampledCLM S₀ tk (TrajectoryErrorBound.keepS Sset h) ≠ 0 →
          c < ExactLinearCertificate.cosv (CertifiedFiniteODE.sampledCLM S₀ tk h)
                (CertifiedFiniteODE.sampledCLM S₀ tk (TrajectoryErrorBound.keepS Sset h)) →
          ∃ s₀ : ℝ, 0 < s₀ ∧ ∀ s ∈ Ioo 0 s₀,
            c < ExactLinearCertificate.cosv
                  (CertifiedODEReduction.sampled x tk (θ₀ + s • h)
                    - CertifiedODEReduction.sampled x tk θ₀)
                  (CertifiedODEReduction.sampled x tk
                      (θ₀ + TrajectoryErrorBound.keepS Sset (s • h))
                    - CertifiedODEReduction.sampled x tk θ₀) :=
  NominalCertificate.local_cos_from_nominal (field F) (isOpen_domain F) (contDiffOn_field F)
    hT x₀ θ₀ hx₀ hdom x0 D0 hx0 hx00 tk htk

end KineticRegularity

#print axioms KineticRegularity.contDiffOn_field
#print axioms KineticRegularity.kinetic_hasFDerivAt
#print axioms KineticRegularity.kinetic_local_cos
