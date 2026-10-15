# Data dictionary of `results/`

All result files are JSON (one file per benchmark problem unless stated otherwise). The field names
and a few categorical labels were kept exactly as written by the analysis programs, which use
Spanish names; this table gives their meaning. Fractions are given as numbers between 0 and 1
(e.g. `eajuste_med = 0.094` means 9.4 %) unless the name ends in `%`.

Common labels: `sistema` = problem; `segundos` = running time of that problem in seconds (on the
machine that produced the file); `admisible` = admissible; `Stage 1` / `Stage 2` = stage of the
selection; `Técnico` = technical failure (the nominal simulation fails); `salidas` = measured outputs;
`estados` = state trajectories.

## `selection/` and `settings/<variant>/` (analysis/selection.py)

| Field | Meaning |
|---|---|
| `p` | number of estimated parameters of the PEtab problem |
| `S1` | subset returned by stage 1 (greedy selection by sensitivity energy) |
| `Rvar_S1_%` | R_var of the stage-1 subset (%) |
| `S1_cumple` | true if stage 1 reached R_var >= tau_R with at least 2 parameters |
| `cos_S1`, `erel_S1` | median cos(Delta) and e_rel of the stage-1 subset |
| `motivo_stage2` | why stage 2 was used ("stage 1 reaches R_var but is not admissible") |
| `etapa` | stage that produced the subset (`Stage 1`, `Stage 2`) |
| `S_antes_poda` | subset before backward elimination |
| `podados` | parameters removed by backward elimination |
| `S` | **final selected biological parameters** |
| `calibracion` | calibration parameters (scalings, offsets), always re-estimated with S |
| `Rvar_%` | R_var(S) (%) |
| `kappa`, `VIF` | condition number and largest VIF of the standardised columns of J for S |
| `cos_med`, `erel_med` | median over the scenarios of cos(Delta) and e_rel (no re-estimation) |
| `eajuste_med` | **median e_fit** (re-estimation of S and the calibration parameters) |
| `eajuste_cota` | upper bound e_rel used when e_fit was not computed (not used in the paper) |
| `eajuste_metodo` | present for the 8 problems where e_fit is computed to first order |
| `n_escenarios` | number of valid scenarios (of 15) |
| `admisible` | **admissible**: |S| >= 2 and median e_fit <= tau_e |
| `motivo` | reason when the problem could not be analysed |
| `T`, `etapa_paper`, `S_paper` | legacy fields of an earlier version of the analysis (state trajectories), not used |

## `external_validation/` (analysis/external_validation.py)

| Field | Meaning |
|---|---|
| `division` | split: `condiciones nuevas` (held-out experimental conditions) or `extrapolación temporal (t ≥ c)` (later time points) |
| `n_condiciones`, `n_train`, `n_test` | number of conditions; training and test measurements |
| `S`, `|S|`, `n_calibracion` | subset validated, its size, number of calibration parameters |
| `p_y` | parameters that affect the outputs |
| `locales_prueba`, `S_locales_prueba` | parameters that only act in test conditions (excluded from the fits) |
| `no_evaluable` | why no training/test split was possible |
| `A_chi2_test_red`, `A_chi2_test_full`, `A_chi2_test_theta0` | real data: test chi2/n of the reduced model, of the full model (both re-fitted to the training data) and of the published theta0 |
| `A_chi2_train_red`, `A_chi2_train_full` | real data: training chi2/n |
| `B_chi2_test_theta0`, `B_chi2_test_red`, `B_chi2_test_full` | synthetic data: test chi2/n (theta0 = signal-to-noise indicator) |
| `B_epred_red`, `B_epred_full`, `B_epred_theta0` | synthetic data: prediction error e_pred with respect to the known truth (1 for theta0) |
| `B_error` | failure of the synthetic experiment (simulation of the truth) |
| `etapas_reanudadas` | fits that were resumed from a checkpoint |

## `robustness/` (analysis/robustness.py)

| Field | Meaning |
|---|---|
| `S`, `n_calibracion` | subset (fixed) and number of calibration parameters |
| `semilla`, `u` | seed and the 15 random directions u(k) (15 x p), the same at every size |
| `niveles` | results per perturbation size (`"1"`, `"5"`, ..., `"50"` = +-1 %, ..., +-50 %) |
| `niveles.*.n` | valid scenarios |
| `niveles.*.escenarios` | indices k of the valid scenarios |
| `niveles.*.eaj`, `erel`, `cos` | e_fit, e_rel and cos(Delta) of every valid scenario |
| `niveles.*.eaj_med`, `eaj_q25`, `eaj_q75`, `erel_med`, `cos_med` | median and quartiles |
| `patron` | robustness pattern A-D (Results) |
| `eajuste_metodo` | `linealizado` (first order) or `no lineal` |

## `single_parameter/` (analysis/single_parameter.py)

| Field | Meaning |
|---|---|
| `candidatos` | number of candidates tested (up to 10 by energy and 10 by finite effect) |
| `un_parametro` | for each candidate: `parametro`, `e_rel`, `e_fit`, `admisible` |
| `algun_parametro_solo_basta` | true if some single parameter is admissible |
| `mejor` | best admissible single parameter j* (smallest e_fit) |
| `mejor_efit_10`, `S_efit_10` | median e_fit at +-10 % of {j*} and of the selected subset S |
| `mejor_validacion` | external validation of {j*} (same fields as external_validation) |
| `mejor_validacion_calibracion` | number of calibration parameters re-estimated with j* in that validation |

## Other files

| File | Content |
|---|---|
| `simulator_check/simulator_check.jsonl` | one line per problem: `mediciones`, `condiciones`, `p`, `p_y`, `err_rel_mediana` and `err_rel_max_vs_simulations` (relative difference with the reference simulations of the benchmark), `nota` (why no comparison was possible) |
| `cost/simulation_times.json` | `p`, `t_sim` (seconds per simulation), `modo` (`salidas` or `estados`); Smith: `t_sim_medido` and `nota` (scaled from a second machine) |
| `crauste_blowup.json` | `nominal` and `un_parametro_1%` (24 one-at-a-time changes): `existe_en_[0,28]` (the solution exists on the measured horizon), `t_final` (time reached), `efectores_max`, `t_max`; `tolerancias`: number of failures (`fallos_*`) for each integrator tolerance |
| `sbml_to_lean/<problem>.json` | report of the translation to Lean: sizes (`n_estados`, `n_theta`, `reacciones`), checks done in Python before writing the Lean file, `lean` (file written), `teorema_final`, `traducido` |
| `sbml_to_lean/translation_fidelity.json` | for each model: `err_rel_max` (largest relative difference between the vector field of the Lean file and libRoadRunner), `err_theta`, `err_x0`, `err_por_punto` |
| `sct/sct_analysis.json` | SCT example: `theta0`, `R2_theta0`, `DE_100` (100 differential-evolution runs: seeds, R^2, parameter ranges, `cambia_signo` = changes sign), `sigma`, selection fields as above, `descartes` (rejected candidates and the parameter they are most collinear with), `niveles`/`patron` (robustness), `validacion` (chi2/n and R^2 on days 25-31; `red` = reduced, `full` = full, `_DE` = full model re-fitted by differential evolution; `estable_*` = stable) |
