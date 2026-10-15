# Notation (proposed Table 0 for Section 2)

Proposed for Reviewer 2, comments 1 and 3. The method is described with symbols only. Their
numerical values go in a separate "Experimental setup" subsection (last column).

| Symbol | Meaning | Value used (Experimental setup) |
|---|---|---|
| $x(t;\theta) \in \mathbb{R}^n$ | state trajectory of the ODE model $\dot x = f(x,\theta)$ | — |
| $\theta \in \mathbb{R}^p$, $\theta_0$ | parameter vector; nominal (published) value | PEtab `nominalValue` |
| $\Theta_B$, $\Theta_C$ | biological parameters (SBML model) and calibration parameters (scalings, offsets); $\theta = (\theta_B, \theta_C)$ | from `observables.tsv` / `parameters.tsv` |
| $y_i(\theta) = h\big(g_i(x(t_i;\theta),\theta)\big)/\sigma_i$ | $i$-th measured output: observable $g_i$, transformation $h$ (lin/log/log10), noise s.d. $\sigma_i$, at the experimental condition and time of measurement $i$ | PEtab `measurements.tsv` |
| $y(\theta) \in \mathbb{R}^m$ | vector of all measured outputs | $m$ = number of measurements |
| $J = \partial y / \partial \log\theta \in \mathbb{R}^{m \times p}$ | relative (logarithmic) sensitivity matrix, by central differences with step $\delta$ | $\delta = 0.01$ |
| $J_S$ | columns of $J$ indexed by $S \subseteq \{1,\dots,p\}$ | — |
| $E_j = \lVert J_{:,j} \rVert^2$ | energy (squared sensitivity) of parameter $j$ | — |
| $R_{\mathrm{var}}(S) = \sum_{j\in S} E_j / \sum_{j} E_j$ | fraction of total sensitivity energy captured by $S$ | stage-1 threshold $\tau_R = 0.89$ |
| $s_j = \lVert y(\theta_0 + \eta\,\theta_{0,j} e_j) - y(\theta_0) \rVert$ | finite-perturbation effect of parameter $j$ (stage-2 ordering) | $\eta = 0.1$ |
| $\kappa(S)$, $\mathrm{VIF}(S)$ | condition number and maximum variance inflation factor of the standardized columns $J_S$ | $\tau_\kappa = \tau_{\mathrm{VIF}} = 10$ |
| $\Delta y_{\mathrm{full}}$, $\Delta y_S$ | output change when all parameters / only those in $S$ are perturbed | scenarios: $N_{\mathrm{esc}} = 15$, $\pm\varepsilon$, $\varepsilon = 0.05$ |
| $\cos\Delta = \langle \Delta y_{\mathrm{full}}, \Delta y_S\rangle / (\lVert\Delta y_{\mathrm{full}}\rVert \lVert\Delta y_S\rVert)$ | directional agreement (no re-estimation) | — |
| $e_{\mathrm{rel}} = \lVert \Delta y_{\mathrm{full}} - \Delta y_S \rVert / \lVert \Delta y_{\mathrm{full}} \rVert$ | relative error without re-estimation | — |
| $e_{\mathrm{fit}} = \min_{\theta_S,\theta_C} \lVert y(\theta_S,\theta_C,\theta_{0,\bar S}) - y_{\mathrm{full}} \rVert / \lVert \Delta y_{\mathrm{full}} \rVert$ | relative error after re-estimating $\theta_S$ (and $\theta_C$), with the rest fixed at $\theta_0$ | — |
| $\tau_e = \sqrt{1-c^2}$ | admissibility threshold on $e_{\mathrm{fit}}$, equivalent to $\cos\Delta \ge c$ after optimal rescaling (Theorem: minimal rescaled error $=\sqrt{1-\cos^2\Delta}$) | $c = 0.9 \Rightarrow \tau_e = 0.436$ |
| $\mathcal{A}(S)$ | admissibility: $\lvert S\rvert \ge k_{\min}$ and median $e_{\mathrm{fit}}(S) \le \tau_e$ | $k_{\min} = 2$ |
| $N_t$ | number of time points (states-based variant only; with measured outputs the times are those of the experiment) | 60 |

## Changes to remove from the current manuscript

* $\rho$ (Section 2.4) and the bound $(1-\varepsilon)(1-\rho^2)$: removed. The cited formal result
  (`fit_from_measurable_removed`) does not exist in the Lean development. The bound was not proven.
* Lean identifiers in the main text: replaced by numbered theorems stated mathematically. The
  correspondence goes in an appendix table, e.g. Theorem 1 ↔ `ScaledError.min_rel_error_eq`,
  Theorem 2 ↔ `Poda.prune_spec`.
