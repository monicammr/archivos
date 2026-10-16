# Audit of the Lean definitions against the paper and the Python code

Second audit, 16 October 2026. A Lean theorem is only as useful as the correspondence between its
definitions and what the paper and the code compute. For each definition used by a central
theorem, this file states the Lean definition, what the paper says, what `analysis/` computes, and
whether they agree. `NonVacuity.lean` shows, for the same theorems, that their hypotheses can be
satisfied (and, for defined properties, that they can fail).

| Lean definition (file) | Lean meaning | Paper / code | Agreement |
|---|---|---|---|
| `ScaledError.min_rel_error_eq` | `min_λ ‖d − λb‖/‖d‖ = √(1 − cos²(d,b))` for `d, b ≠ 0` | Theorem 1; `τ_e = √(1 − 0.9²)` in `config.py` | Exact. |
| `Poda.prune`, predicate `Q` | backward elimination with an arbitrary predicate `Q` and an arbitrary removal rule `pick` | `selection.py`: removes parameters in increasing `E_j` while `admissible()` holds | Exact: the code's rule is one admissible `pick`; `Q` is the implemented admissibility (`|S| ≥ 2` and median rule). First part of Theorem 2 needs nothing more. |
| `Poda.prune_inclusion_minimal`, `hmono` | monotone `Q` | not proved for the implemented `Q` (local optimiser) | Checked empirically: 0 violations among the nested pairs evaluated (`monotonia` in `results/selection_*fixedscen`). |
| `RefitMonotone.fitErr` | infimum of a nonnegative error over the box with the other parameters fixed | `e_fit`: trust-region fit from two starting points, box `[|θ₀|/10, 10|θ₀|]` in log, value without re-estimation included | Lean is the exact optimum; the code is a local optimum. `e_fit ≤ e_rel` holds by construction in the code (the value without re-estimation is included). |
| `GreedySelection.okKappa`, `okVIF` | `κ(Z_S) ≤ κ₀` and `VIF_j(Z_S) ≤ V` for a linear map `Z`, via bounds over vectors supported on `S` | `selection.py` uses columns **centred and scaled** (`_standardize`, correlation matrix) | The greedy theorems hold for any `Z`, in particular for the centred columns scaled to unit norm, so the selection guarantee applies as implemented (κ is scale-invariant; VIF of the correlation matrix equals that of the unit-norm centred columns). |
| `Identifiability.ls_kappa_stability`, `ls_vif_coordinate_stability` | stability of the least-squares solution for a map `Z` with **unit columns** (`hunit`) | paper, Table 3 row "Selection with κ and VIF" | Applies to the uncentred unit-length columns of `J_S`, not to the centred ones used by the selection. Computed for the final subsets (`analysis/conditioning_check.py`): satisfied in 30 of 31, not in Rahman (κ = 12.4, VIF = 39). |
| `FirstOrderErrorBound.first_order_error_from_Rvar` | `‖JΔθ − J_SΔθ_S‖² ≤ (1 − r)·tr(JᵀJ)·‖Δθ‖²` when `R_var(S) ≥ r` | Level 3 in Table 1; `R_var` in `selection.py` (`E_j = ‖J_j‖²` of the relative `J`) | Same `E_j` and `R_var`. The bound is on the **absolute** linearised error **without** re-estimation, not on the relative `e_fit`; the paper uses it only as the level-3 label. |
| `LinearizedFit.fit_upper_of_lin`, `fit_lower_of_lin` | `|e_fit − e_lin|` bounded by `Mρ²/‖d‖` given a second-order remainder bound `M` | first-order `e_fit` of six problems | `M` never computed, so the bound is not instantiated; the six problems were re-estimated nonlinearly instead (`analysis/efit_nonlinear.py`). |
| `ProfileIdentifiability.PracticallyIdentifiable` | ∃ `0 < t₋ < d₋`, `0 < t₊ < d₊` such that every admissible `δ` with `φ δ ≤ −t₋` or `φ δ ≥ t₊` has `Δχ² ≥ c` | Raue et al.: the 95 % profile-likelihood interval is bounded on both sides within the bounds; `c = 3.84` | Exact: the profile at `t` is the minimum of `Δχ²` over admissible `δ` with `φ δ = t`. `φ` is the displacement of `log|θ_j|`; `F` is the box of all free parameters. |
| `practically_identifiable_grad`, hypothesis `hrem` | `‖R δ − R 0 − A δ‖ ≤ ε` for **all** `δ ∈ F` | `identifiability_conditions.py` estimated `ε` only at the computed profile points | Mismatch (point N2 of the audit): addressed by `practically_identifiable_grad_tail` / `_rel_tail` (bound needed only on the tail) and by `identifiability_box.py`, which estimates the tail bounds over `F` by sampling and adversarial search, for regions of radius 10, 5, 3, 2 and 1.5. Still an estimate of a supremum, not a proof. |
| Model files `Models/*.lean` | rate laws, stoichiometry, parameter values and initial values as exact rationals | SBML + PEtab tables | Checked numerically against libRoadRunner at the nominal state and five random states (largest relative difference `1e-12`); a 1 % change of one number is detected. |

## What this audit found

1. κ/VIF normalisation differs between the code (centred) and the least-squares statements of Lean
   (uncentred unit columns). The greedy guarantees still apply; the least-squares stability does
   not apply to Rahman.
2. The identifiability hypothesis was checked on the wrong set (the profile path instead of `F`).
3. Monotonicity of the implemented admissibility was assumed, not checked (now checked: 0 violations).
4. `verify.sh` reported success although the axiom check of the 28 models failed (`AllModels` was
   not a build target), and its `sorry` search failed when re-run (it scanned the downloaded Mathlib).
   Both fixed.

No theorem was found to be false; every problem was in the link between a theorem and the numbers.
