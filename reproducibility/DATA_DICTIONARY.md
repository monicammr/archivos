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

## `nested_validation/` (analysis/nested_validation.py)

| Field | Meaning |
|---|---|
| `S`, `|S|`, `division`, `n_train`, `n_test` | selected subset, its size, kind of split, number of training and test measurements |
| `chi2_test_red_original` | test chi2/n of the reduced model with the non-selected parameters at theta0 |
| `chi2_test_full_train` | test chi2/n of the full model re-estimated on the training data (theta_train) |
| `chi2_test_red_nested` | test chi2/n of the reduced model with the non-selected parameters at theta_train |
| `chi2_test_theta0` | test chi2/n of the published estimate theta0 |
| `ratio_nested_vs_original` | `chi2_test_red_nested / chi2_test_red_original` (above 1: worse without the theta0 anchor) |

## `synthetic_seeds/<problem>/s<seed>.json` (analysis/synthetic_seeds.py)

One file per problem and seed (42-61). Fields as in `external_validation/` (keys `B_*`) for that
seed: `semilla` = seed; `p_y` = free parameters; `B_chi2_test_theta0`, `B_chi2_test_red`,
`B_chi2_test_full`; `B_epred_red`, `B_epred_full` (relative prediction error with respect to the
truth; 1 = theta0); `nfev_red`, `nfev_full` = function evaluations of the fits; `seg_red` = seconds of
the reduced fit; `B_error` = the simulation of the truth failed. `B_*_full` is absent for the four
problems with more than 100 free parameters. `RESUMEN.json` and `RESUMEN.md` summarise all seeds
(`por_semilla`: counts per seed; `por_sistema`: per problem, `con_senal` = seeds with signal,
`red_ok_senal` = reduced e_pred <= tau_e among them, `red_le_full_senal` = reduced e_pred <= full).

## `random_subsets/` and `calibration_only/` (analysis/baselines.py)

| Field | Meaning |
|---|---|
| `k` | number of biological parameters of our subset (also used for the random subsets) |
| `chi2_ours` | test chi2/n of our subset (theta0 anchor), from `nested_validation/` |
| `chi2_rand_median`, `chi2_rand_q1`, `chi2_rand_q3` | median and quartiles of the test chi2/n over the random draws |
| `chi2_por_semilla`, `n_seeds`, `n_validas` | test chi2/n of each draw (seeds 0-19), number of draws, valid draws |
| `chi2_vacio` | test chi2/n with only the calibration parameters re-estimated (`n_cal` of them) |
| `ratio_rand_vs_ours`, `ratio_vacio_vs_ours` | baseline over ours (below 1: the baseline predicts better) |
| `nota` | `sin calibracion, th0 directo` = no calibration parameters: theta0 is evaluated directly |

## `qr_selection/` (analysis/qr_selection.py) and `brun_morris/` (analysis/brun_morris.py)

| Field | Meaning |
|---|---|
| `S_ours`, `S_qr`, `S_brun`, `S_morris` | biological parameters selected by each criterion (same `k`) |
| `chi2_ours`, `chi2_qr`, `chi2_brun`, `chi2_morris`, `chi2_perfil` | test chi2/n of each subset (with the calibration parameters, theta0 anchor) |
| `overlap`, `overlap_brun_ours`, `overlap_morris_ours` | parameters shared with our subset |
| `ratio_qr_vs_ours` | `chi2_qr / chi2_ours` |
| `detalle_brun` | `gamma` = collinearity index of the selected subset, `cumple_gamma` = gamma <= 10, `dmsqr_top` = importance of the 15 candidates |
| `detalle_morris` | `mu_star_top` = mu* of the 10 most influential parameters, `fallos_simulacion` = failed elementary effects |
| `segundos_brun`, `segundos_morris`, `tipo` | seconds of each criterion (selection and fit); kind of split |

## `profile_likelihood/` (analysis/profile_likelihood.py)

`<problem>.json`:

| Field | Meaning |
|---|---|
| `p_libres`, `n_bio` | free parameters of the training fit; biological parameters profiled |
| `n_identificables`, `n_no_identificables_practicos`, `n_planos` | parameters identifiable (profile above Delta chi2 = 3.84 on both sides), bounded on one side, flat |
| `S_perfil` | the `k` parameters with the narrowest profile confidence interval |
| `chi2_perfil`, `chi2_ours`, `chi2_qr`, `ratio_perfil_vs_ours` | test chi2/n of the profile subset, of ours and of pivoted QR |
| `overlap_perfil_ours`, `overlap_perfil_qr` | parameters shared with our subset and with the QR subset |
| `coste_min_train` | chi2 (sum of squares) of the full training fit used as the minimum |
| `rondas_reajuste` | times the full model was re-estimated because a profile point improved the minimum |
| `dchi2_minimo_perfiles` | smallest Delta chi2 among the profile points after the last re-estimation (below -1: residual improvement) |
| `puntos_fallidos` | profile points whose fit failed (Delta chi2 > 1e4), excluded |
| `perfiles` | per parameter: `clase` (`identificable`, `no identificable practico`, `plano`), `ancho_ic_log` (width of the 95 % interval in log units; infinite if open), `dchi2_max_izq`, `dchi2_max_der` (largest Delta chi2 on each side) |
| `no_evaluable` | not profiled: more than 60 free parameters (`PL_PMAX`), or no training/test split |

`<problem>/perfil_<parameter>_<side>_<i>.json`: one profile point (`lado` = side, `despl` =
displacement of log|theta_j|, `dchi2`, `nfev`, `theta` = re-estimated parameter vector);
`<problem>/full_train.npz`: minimum (`theta`, `coste`, `rondas`). `logs/`: summary lines of the runs
(`terminado` = problem finished with `seg_total` seconds; `reajuste` = re-estimation of the minimum).

## `criteria_tests/` and `criteria_tests_20pc/` (analysis/criteria_tests.py)

File names `<problem>__<criterion>__adm.json` (admissibility) and `<problem>__<criterion>__sint_<seed>.json`
(synthetic), with `<criterion>` = `ours`, `qr`, `brun`, `morris`, `perfil`. `criteria_tests/` uses
perturbations of +-5 % (the level of the method); `criteria_tests_20pc/`, +-20 % (admissibility only).

| Field | Meaning |
|---|---|
| `S` | biological parameters of the subset tested |
| `eajuste_med`, `erel_med` | median e_fit and median e_rel over the scenarios |
| `admisible` | min(`eajuste_med`, `erel_med`) <= 0.436 and at least 2 parameters (rule of the method) |
| `n_escenarios`, `lineal` | valid scenarios; true if e_fit was computed to first order (problems of `config.FIRST_ORDER`) |
| `B_chi2_test_theta0`, `B_chi2_test_red`, `B_epred_red`, `semilla` | synthetic experiment for that seed (as in `external_validation/`) |
| `no_evaluable` | `sin subconjunto` = the criterion has no subset for the problem; `falla la simulación de la verdad` = the truth could not be simulated |

## `identifiability/` (analysis/identifiability_*.py)

Profile likelihood of the selected parameters in the reduced problem (S and the calibration
parameters free, the other parameters at theta0, all measurements).

`profiles/<problem>/minimo.npz`: optimum of the reduced problem (`theta`, `coste` = chi2, `rondas` =
re-fits after a profile point improved the optimum). `profiles/<problem>/p_<parameter>_<+|->_<i>.json`:
one profile point (`despl` = displacement in log|theta_j|, `log_theta`, `dchi2`, `theta` = all
parameters after the re-fit). `profiles/<problem>.json`:

| Field | Meaning |
|---|---|
| `chi2_por_gl`, `umbral_robusto` | chi2 per degree of freedom at the optimum; threshold of the robust variant, 3.84 max(1, chi2/d.f.) |
| `perfiles[].clase`, `clase_robusto` | `identificable` (profile above 3.84 on both sides within [theta0/10, 10 theta0]), `no identificable practico` (one side), `plano` (neither) |
| `perfiles[].ic_izq_log`, `ic_der_log` | distance (log) at which the profile crosses the threshold on each side (inf = no crossing) |
| `perfiles[].minimo_en_limite`, `puntos_fallidos` | sides without valid points (optimum at a bound); points whose simulation failed |

`local/<problem>.json`: `kappa_SC_n`, `VIF_SC_n_S` (condition number and VIF of the unit-norm,
uncentred columns of S and the calibration parameters at theta0), `par_mas_parecido_con_S` (most
similar pair of columns and their cosine). `certificado*.csv`: one row per selected parameter with
the quantities of the Lean theorem `ProfileIdentifiability.practically_identifiable_grad`: `I_j`
(profiled information), `gamma` (norm of the projection of the residual onto the range of the
sensitivity matrix), `eps_j` (largest nonlinear remainder at the profile points), `tstar`,
`tstar_lineal` (Wald half-width), `d_menos`, `d_mas` (distances to the bounds), `certificado_lineal`,
`certificado_local` (hypotheses satisfied with epsilon = 0, or with epsilon evaluated at the points up
to the first crossing). `summary.md`: the counts quoted in the paper.

## `timing_complete/` (analysis/selection.py run from scratch)

`parallel/`, `single_core/`: the complete result of `selection.py` (fields as in `selection/`) run
without cached results, with the sensitivity computations on 16-64 cores or on one core; the run
time is `segundos`. `parallel_corrected_code/`: the eight problems of `config.FIRST_ORDER` with the
corrected program (version 1.1); their subsets and `eajuste_med` are identical to `selection/`.
The runs shared a 128-core server, so the times are upper bounds.

## `robustness_independent/` (analysis/robustness.py with ROBUST_INDEP=1)

Same fields as `robustness/`, plus `direcciones` ("independent at every size") and, in every size of
`niveles`, `semilla` (seed of the directions of that size: 42 at +-5 %, 42 + 1000 i at the i-th other size).
The top-level `u` are the directions of seed 42; the scenarios of the other sizes are not the rows of `u`.

## `synthetic_signal_a<amplitude>/` and `synthetic_seeds_a<amplitude>/` (analysis/synthetic_seeds.py)

One file per problem and seed (`<problem>/s<seed>.json`), as in `synthetic_seeds/`, with the amplitude
`a` of the truth theta* = theta0 (1 + a u) in the folder name (005 = 0.05, 020 = 0.20, 050 = 0.50) and in
`amplitud`. New fields (also in `synthetic_seeds_a005/`, `_a050/`):

| Field | Meaning |
|---|---|
| `senal_rms_test`, `senal_rms_train` | root mean square of y(theta*) - y(theta0) per test / training measurement, in units of sigma |
| `senal_norma_test`, `ruido_norma_test` | norm of y(theta*) - y(theta0) on the test measurements, and sqrt(n_test) (norm of unit noise) |

The `synthetic_signal_*` folders contain only these fields (no fits). `synthetic_seeds_a*` contain the
same fields as `synthetic_seeds/` (`B_chi2_test_*`, `B_epred_red`, `B_epred_full`, ...).

## `absolute_error/` (analysis/absolute_error.py)

| Field | Meaning |
|---|---|
| `n`, `n_escenarios` | number of measurements; valid scenarios at +-5 % |
| `e_fit_med` | median e_fit over the scenarios (from `robustness/`, +-5 %) |
| `cambio_rms_sigma_med` | median of `\|Delta y_full\| / sqrt(n)`, the change of the full model per measurement in units of sigma |
| `error_rms_sigma_med`, `error_rms_sigma_max` | median and maximum of `e_fit * \|Delta y_full\| / sqrt(n)`, the error that remains after re-estimation, in units of sigma |
| `escenarios` | the same quantities for every scenario `k` |

## `settings_extra/` (analysis/selection.py --variant)

Same fields as `selection/`, for Lang and Raimundez, in folders named as in `settings/`; `README.md`
lists the variants that did not finish.

## Other files

| File | Content |
|---|---|
| `simulator_check/simulator_check.jsonl` | one line per problem: `mediciones`, `condiciones`, `p`, `p_y`, `err_rel_mediana` and `err_rel_max_vs_simulations` (relative difference with the reference simulations of the benchmark), `nota` (why no comparison was possible) |
| `cost/simulation_times.json` | `p`, `t_sim` (seconds per simulation), `modo` (`salidas` or `estados`); Smith: `t_sim_medido` and `nota` (scaled from a second machine) |
| `crauste_blowup.json` | `nominal` and `un_parametro_1%` (24 one-at-a-time changes): `existe_en_[0,28]` (the solution exists on the measured horizon), `t_final` (time reached), `efectores_max`, `t_max`; `tolerancias`: number of failures (`fallos_*`) for each integrator tolerance |
| `sbml_to_lean/<problem>.json` | report of the translation to Lean: sizes (`n_estados`, `n_theta`, `reacciones`), checks done in Python before writing the Lean file, `lean` (file written), `teorema_final`, `traducido` |
| `sbml_to_lean/translation_fidelity.json` | for each model: `err_rel_max` (largest relative difference between the vector field of the Lean file and libRoadRunner), `err_theta`, `err_x0`, `err_por_punto` |
| `sct/sct_analysis.json` | SCT example: `theta0`, `R2_theta0`, `DE_100` (100 differential-evolution runs: seeds, R^2, parameter ranges, `cambia_signo` = changes sign), `sigma`, selection fields as above, `descartes` (rejected candidates and the parameter they are most collinear with), `niveles`/`patron` (robustness), `validacion` (chi2/n and R^2 on days 25-31; `red` = reduced, `full` = full, `_DE` = full model re-fitted by differential evolution; `estable_*` = stable) |
