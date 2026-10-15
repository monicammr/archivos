# Reproducibility package

**Few biological parameters suffice to reproduce measured dynamics in systems biology models:
local sensitivity-based reduction with formally verified mathematical guarantees**

Mónica Miranda R., Carlos Salazar, César Martín, Adriana Aguirre
(Escuela Superior Politécnica del Litoral, ESPOL). Submitted to *Scientific Reports*.

This package contains everything needed to check the results of the paper:

* the **Python programs** of the method and of every numerical analysis (`analysis/`);
* the **results** of those analyses, one file per benchmark problem (`results/`, 3 MB);
* the **programs that produce every figure, table and Supplementary Note** of the paper from those
  results (`figures_tables/`);
* the **formal proofs** in Lean 4 with Mathlib: 31 modules with 289 theorems and lemmas, and the
  hypotheses of 28 benchmark models (`lean_proofs/`);
* the **translator** of the SBML models into Lean and an independent check of the translation
  (`lean_translation/`).

The benchmark problems themselves are downloaded from the PEtab benchmark collection
(`scripts/get_benchmark.sh`). The step-count data of the participant of the social cognitive theory
(SCT) example are not included; they are available from the authors on reasonable request.

---

## Three levels of checking

| Level | What it does | Time | Needs |
|---|---|---|---|
| **A** | Regenerates every figure, table and Supplementary Note from the stored results | under a minute | Python, LaTeX |
| **B** | Compiles all formal proofs and checks that they use no unproved assumption | 1–2 h | Lean (elan) |
| **C** | Re-runs the analyses from the PEtab problems and compares with the stored results | minutes per problem; about 1–2 days in total on 4 cores | Python, the benchmark (download) |

Each level is independent. A reader who only wants to see where a number comes from needs level A;
a reader who wants to check the mathematics needs level B; level C repeats the computations.

---

## Contents

```
README.md               this manual
DATA_DICTIONARY.md      meaning of every field of the result files
requirements.txt        Python packages (exact versions); environment.yml for conda
LICENSE                 MIT (code); LICENSE-results.md: CC BY 4.0 (results)
CITATION.cff            how to cite
scripts/
  get_benchmark.sh      downloads the 35 PEtab problems used (commit fcbddf1, about 80 MB)
  compare_results.py    compares re-computed results with the stored ones
analysis/               the method and the numerical analyses (Python)
  config.py             paths and settings of the paper (delta, tau_R, tau_kappa, tau_e, seeds, ...)
  petab_problem.py      simulation of the measured outputs of a PEtab problem
  selection.py          parameter selection (stages 1 and 2, admissibility, backward elimination)
  external_validation.py  prediction of held-out experiments (real and synthetic data)
  robustness.py         errors at perturbation sizes 1-50 % (paired scenarios), patterns A-D
  single_parameter.py   single-parameter subsets (minimum size 2)
  simulator_check.py    comparison with the reference simulations of the benchmark
  timing.py             time of one simulation (computational cost)
  crauste_blowup.py     why no local reduction exists for Crauste
  sct_model.py, sct_analysis.py   SCT example (needs the participant data)
results/                stored results (see DATA_DICTIONARY.md)
  selection/            selected subset of each of the 34 problems
  settings/<variant>/   the same with one setting changed (15 variants, 26 problems)
  external_validation/  held-out prediction, real and synthetic data
  robustness/           errors of the 15 scenarios at 7 perturbation sizes
  single_parameter/     single-parameter subsets
  simulator_check/, cost/, sbml_to_lean/, sct/, crauste_blowup.json
figures_tables/         produce the figures, tables and Supplementary Notes from results/
  build_all.py          runs all of them (level A)
lean_proofs/            Lean 4 + Mathlib project (see lean_proofs/README.md)
lean_translation/
  sbml_to_lean.py       translator SBML -> Lean (writes lean_proofs/Models/)
  verify_translation.py independent check of the translated models against libRoadRunner
  mutation_control.py   control: a 1 % change of one number of a Lean file is detected
```

---

## Installation

**Python** (3.11; tested on Linux with the versions in `requirements.txt`):

```bash
python3.11 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

or, with conda, `conda env create -f environment.yml && conda activate fewparams`.

**Other tools** (level A only): `pdflatex` (any TeX distribution, for Fig. 6) and `pdftops`,
`pdftoppm` (poppler-utils, for the EPS and TIFF copies of the figures).

**Lean** (level B only): install [elan](https://github.com/leanprover/elan); it installs the Lean version
given in `lean_proofs/lean-toolchain` (4.23.0) automatically.

All commands below are run from the folder of this README.

---

## Level A — figures, tables and Supplementary Notes from the stored results

```bash
cd figures_tables
python build_all.py
```

The output is written to `figures_tables/output/`:

* `tables/table1.tex` (Table 1), `tables/tableS1.tex`, `tables/tableS3.tex`;
* `figures/fig1_pipeline.pdf` … `fig6_architecture.pdf` (with `.eps` and `.tif` copies) and the
  supplementary figures `figS1_validation_scatter.pdf`, `figS_robustness_scenarios.pdf`;
* `figure3/`: the consolidated table behind Fig. 3 and a summary of the counts quoted in the text;
* `suppl_*.tex`: the Supplementary Notes that contain numbers (simulator, synthetic experiment,
  single parameter, settings, cost, robustness, system-by-system summary, verified models,
  statements of the formal theorems).

Each script prints the counts that the paper quotes (for example the numbers of admissible problems
for each setting), so that they can be compared with the text. The note on the SCT example and
Supplementary Fig. S3 need the participant data (place the file as described in
`analysis/sct_model.py`); without it, that step is skipped with a message.

To see where a particular number of the paper comes from, use the table
[Where each result comes from](#where-each-result-comes-from) and open the JSON file of the problem
(fields explained in `DATA_DICTIONARY.md`).

---

## Level B — the formal proofs

```bash
cd lean_proofs
./verify.sh
```

The script (i) checks that no file contains `sorry` or `axiom`, (ii) downloads the precompiled
Mathlib, (iii) compiles the 31 theory modules and the 28 model files and (iv) prints the axioms used by
every theorem. Only Lean's standard axioms (`propext`, `Classical.choice`, `Quot.sound`) must appear.
The first compilation takes about 1–2 hours (mostly the largest models, Chen and Froehlich); the log of
our build is `lean_proofs/BUILD_LOG.md`. `lean_proofs/README.md` relates each step of the method to
its theorems, and `lean_proofs/FORMULAS.md` gives the statement of every theorem in mathematical
notation.

The model files can be regenerated from the SBML models and checked independently (needs the
benchmark, see level C):

```bash
cd lean_translation
python sbml_to_lean.py               # writes lean_proofs/Models/ (identical files) and results/sbml_to_lean/
python verify_translation.py         # largest relative difference with libRoadRunner: about 1e-12
python mutation_control.py           # a 1 % change of one number is detected (difference about 1e-2)
```

---

## Level C — re-running the analyses

1. Download the benchmark problems (35 problems at commit `fcbddf1`, about 80 MB, needs `git`):

   ```bash
   bash scripts/get_benchmark.sh
   ```

   (Another copy can be used by setting `PETAB_BENCHMARK=/path/to/Benchmark-Models-PEtab/problems`.)

2. Choose where to write the new results, so that the stored ones are kept for comparison:

   ```bash
   export REPRO_RESULTS=$PWD/results_rerun      # Windows PowerShell: $env:REPRO_RESULTS="$PWD\results_rerun"
   export NPROC=4                               # processes for the problems that run in parallel
   cd analysis
   ```

3. Run the steps in this order (each step uses the selection of step b). Any step can be limited to
   some problems by giving their names, e.g. `python selection.py Boehm_JProteomeRes2014`.

   | Step | Command | Paper | Time on 4 cores |
   |---|---|---|---|
   | a | `python simulator_check.py` | Supplementary Table S9 | minutes |
   | b | `python selection.py` | Fig. 2, Table 1, Suppl. Table S1 | minutes, except Chen (~2 h), Lang, Raimundez |
   | c | `for v in delta_0.001 delta_0.05 tolerances_1e-9_1e-12 tolerances_1e-6_1e-8 perturbation_0.01 perturbation_0.10 tauR_0.80 tauR_0.85 tauR_0.95 tauK_5 tauK_30 tauE_0.10 tauE_0.20 tauE_0.30 tauE_0.50; do python selection.py --variant $v; done` | Fig. 5, Suppl. Table S14 | 0.5–1 h per variant |
   | d | `python external_validation.py` | Fig. 3, Suppl. Fig. S1, Suppl. Table S12 | ~6 h (Chen and Raimundez take most) |
   | e | `python robustness.py` | Fig. 4, Suppl. Tables S10–S11, Fig. S2 | a few hours |
   | f | `python single_parameter.py` | Suppl. Table S13 | ~1 h |
   | g | `python crauste_blowup.py` | Results (Crauste) | minutes |
   | h | `python timing.py --write Boehm_JProteomeRes2014 Chen_MSB2009 ...` | Suppl. Table S15 | minutes (times depend on the machine) |
   | i | `python sct_analysis.py` | Suppl. Note SCT, Table S16 | ~30 min (needs the data) |

4. Compare each folder with the stored results:

   ```bash
   cd ..
   python scripts/compare_results.py results_rerun/selection results/selection
   python scripts/compare_results.py results_rerun/external_validation results/external_validation
   ...
   ```

   Running times and checkpoint bookkeeping are ignored; numbers are compared with a relative
   tolerance of 1e-6 (`--rtol` to change it).

5. Optionally, regenerate the figures and tables from the new results:
   `REPRO_RESULTS=$PWD/results_rerun python figures_tables/build_all.py`.

**What to expect.** The method is deterministic (fixed seeds), and for the small and medium problems
the re-computed results agree with the stored ones to the last digits. Small differences can appear
(i) in the problems whose simulations occasionally fail to integrate, so that a scenario is valid in
one run and not in another (Chen: 8 to 13 of 15 scenarios per size); (ii) in the fits of the external
validation, which use the result of the previous optimisation when a long fit is resumed from a
checkpoint; and (iii) with other versions of libRoadRunner/SUNDIALS or of NumPy/SciPy. Running times
(`segundos`, `t_sim`) depend on the machine.

**Large problems.** For the eight problems in `config.FIRST_ORDER` (Alkan, Bachmann, Beer, Chen,
Isensee, Lang, Lucarelli, Raimundez) the re-estimation error is computed to first order, as stated in
the Methods; their sensitivity matrices are computed in parallel (`NPROC` processes), kept on disk in
single precision in `results_rerun/cache/` and the computation resumes from there if interrupted.
Froehlich (4,231 parameters, 9,169 experimental conditions) is not analysed on its measured outputs
(each evaluation needs about 9,000 simulations); only the time of one simulation of its state
trajectories is used (cost note), and its model is verified in Lean.

---

## Where each result comes from

| Paper | Program (`analysis/`) | Results (`results/`) | Figure/table program (`figures_tables/`) |
|---|---|---|---|
| Fig. 1 (method) | — | — | `make_figures.py` (`fig1`) |
| Fig. 2, Table 1, Suppl. Table S1; Results, numbers of selected parameters, levels of guarantee | `selection.py` | `selection/` | `make_figures.py` (`fig2`), `make_tables.py` |
| Fig. 3, Suppl. Fig. S1; Results, held-out prediction | `external_validation.py` | `external_validation/` | `make_figure3.py` |
| Synthetic experiment (Results; Suppl. Table S12) | `external_validation.py` (keys `B_*`) | `external_validation/` | `make_extra_notes.py` |
| Fig. 4, Suppl. Tables S10–S11, Suppl. Fig. S2; patterns A–D, pass rates | `robustness.py` | `robustness/` | `make_figures.py` (`fig4`), `make_robustness_note.py` |
| Fig. 5, Suppl. Table S14 (method settings) | `selection.py --variant` | `settings/` | `make_fig5_settings.py`, `make_extra_notes.py` |
| Single-parameter subsets (Results; Suppl. Table S13) | `single_parameter.py` | `single_parameter/` | `make_extra_notes.py` |
| Crauste (Results, non-admissible problems) | `crauste_blowup.py` | `crauste_blowup.json` | — |
| Computational cost (Results; Suppl. Table S15) | `timing.py` | `cost/` | `make_extra_notes.py` |
| Simulator check (Methods; Suppl. Table S9) | `simulator_check.py` | `simulator_check/` | `make_extra_notes.py` |
| Fig. 6, Table 2; Suppl. Tables S3–S6 (formal statements) | `lean_proofs/` | — | `fig6_architecture.tex`, `make_tableS3.py`, `make_formulas.py` |
| Verified models, translation fidelity (Methods; Suppl. Tables S7–S8) | `lean_translation/` | `sbml_to_lean/` | `make_models.py` |
| System-by-system summary (Supplementary Note) | all of the above | all of the above | `make_systems_note.py` |
| SCT example (Introduction, Results; Suppl. Table S16, Fig. S3) | `sct_analysis.py` | `sct/` | `make_sct_note.py` |

Supplementary Tables S2 (notation) and S4 (scope of each guarantee) are text of the Supplementary
Information and are not generated.

---

## Notes

* **Settings of the method.** All thresholds and seeds are in `analysis/config.py` and are those of
  the Methods: delta = 1 %, eta = 10 %, tau_R = 0.89, tau_kappa = tau_VIF = 10, tau_e = 0.436
  (c = 0.9), k_min = 2, 15 scenarios at +-5 % with seed 42.
* **Language of the result files.** Field names in `results/` are those written by the original
  programs (Spanish); `DATA_DICTIONARY.md` translates them. The programs of this package write the
  same fields, so new and stored results can be compared directly.
* **Simulator.** libRoadRunner (CVODE, relative and absolute tolerances 1e-7 and 1e-10). Measurements at
  steady state and pre-equilibration use t = 1e5. If the integrator fails, the simulation is repeated
  piecewise with the discontinuities of the condition as breakpoints (Isensee).
* **Smith.** Its simulation time in `cost/` was measured on a second machine and scaled by 1.55 (field
  `nota`); all other times were measured on the same four-core server.
* **SCT data.** `analysis/sct_model.py` describes the expected file (columns `xi3`–`xi8`, `eta4`, one row
  per day).

## License and citation

Code: MIT (`LICENSE`). Results: CC BY 4.0 (`LICENSE-results.md`). Please cite the paper and this
package (`CITATION.cff`). Contact: Mónica Miranda R., mmmirand@espol.edu.ec.
