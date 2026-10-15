"""
Paths and fixed settings shared by all analysis scripts.

* ``BENCHMARK``: folder ``problems/`` of the PEtab benchmark collection
  (https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab, commit
  fcbddf1b900efabdfbdc2b58452c89556e63f1ce). ``scripts/get_benchmark.sh`` downloads it to
  ``data/Benchmark-Models-PEtab``; another location can be given with the environment variable
  ``PETAB_BENCHMARK``.
* ``RESULTS``: folder ``results/`` of this package. By default the scripts write into it, so a
  re-run overwrites the stored results; set ``REPRO_RESULTS`` to write somewhere else and compare
  (see README, level C).
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = Path(os.environ.get("PETAB_BENCHMARK",
                                ROOT / "data" / "Benchmark-Models-PEtab" / "problems"))
RESULTS = Path(os.environ.get("REPRO_RESULTS", ROOT / "results"))
CACHE = RESULTS / "cache"          # resumable intermediate files of the largest problems

# Result folders (one JSON file per benchmark problem)
SELECTION = RESULTS / "selection"
SETTINGS = RESULTS / "settings"
VALIDATION = RESULTS / "external_validation"
ROBUSTNESS = RESULTS / "robustness"
ROBUSTNESS_SCENARIOS = RESULTS / "robustness_scenarios"
SINGLE = RESULTS / "single_parameter"
# Comparison with other selection criteria and further validations (Results, "Comparison with
# existing selection criteria"; Supplementary Notes on the comparison)
NESTED = RESULTS / "nested_validation"
SYNTHETIC_SEEDS = RESULTS / "synthetic_seeds"
RANDOM_SUBSETS = RESULTS / "random_subsets"
CALIBRATION_ONLY = RESULTS / "calibration_only"
QR_SELECTION = RESULTS / "qr_selection"
BRUN_MORRIS = RESULTS / "brun_morris"
PROFILE = RESULTS / "profile_likelihood"
IDENTIFIABILITY = RESULTS / "identifiability"     # profiles of the reduced problem, local check, Lean conditions
CRITERIA_TESTS = RESULTS / "criteria_tests"          # admissibility (+-5 %) and synthetic, 5 criteria
TIMING_COMPLETE = RESULTS / "timing_complete"        # run time of the complete method from scratch

# Method settings used in the paper (Methods, "Settings")
DELTA = 0.01                          # relative finite-difference step for J
ETA = 0.1                             # relative change for the finite effect s_j (stage 2)
TAU_R = 0.89                          # variance threshold of stage 1
TAU_KAPPA = TAU_VIF = 10.0            # collinearity thresholds
C = 0.9
TAU_E = float((1 - C ** 2) ** 0.5)    # admissibility threshold, 0.436
K_MIN = 2                             # minimum number of selected biological parameters
N_SCENARIOS, SEED, EPSILON = 15, 42, 0.05
LEVELS = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]   # perturbation sizes (robustness)

# Problems whose re-estimation error is computed to first order (Methods): repeated nonlinear
# re-estimation is impractical because of the cost of a simulation.
FIRST_ORDER = {"Alkan_SciSignal2018", "Bachmann_MSB2011", "Beer_MolBioSystems2014", "Chen_MSB2009",
               "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Lucarelli_CellSystems2018",
               "Raimundez_PCB2020"}

# The 34 PEtab problems with real measurements analysed in the paper (Table 1)
PROBLEMS = [
    "Alkan_SciSignal2018", "Armistead_CellDeathDis2024", "Bachmann_MSB2011", "Beer_MolBioSystems2014",
    "Bertozzi_PNAS2020", "Blasi_CellSystems2016", "Boehm_JProteomeRes2014", "Borghans_BiophysChem1997",
    "Brannmark_JBC2010", "Bruno_JExpBot2016", "Chen_MSB2009", "Crauste_CellSystems2017",
    "Elowitz_Nature2000", "Fiedler_BMCSystBiol2016", "Fujita_SciSignal2010", "Giordano_Nature2020",
    "Isensee_JCB2018", "Lang_PLOSComputBiol2024", "Laske_PLOSComputBiol2019", "Liu_IFACPapersOnLine2025",
    "Lucarelli_CellSystems2018", "Okuonghae_ChaosSolitonsFractals2020", "Oliveira_NatCommun2021",
    "Perelson_Science1996", "Rahman_MBS2016", "Raia_CancerResearch2011", "Raimundez_PCB2020",
    "SalazarCavazos_MBoC2020", "Schwen_PONE2014", "Smith_BMCSystBiol2013", "Sneyd_PNAS2002",
    "Weber_BMC2015", "Zhao_QuantBiol2020", "Zheng_PNAS2012",
]

# The 26 small and medium problems used for the sensitivity to the method settings (Fig. 5)
SETTINGS_PROBLEMS = [p for p in PROBLEMS if p not in FIRST_ORDER]

# Variants of Fig. 5: folder name -> environment variables that change one setting
SETTINGS_VARIANTS = {
    "delta_0.001": {"REPRO_DELTA": "0.001"},
    "delta_0.05": {"REPRO_DELTA": "0.05"},
    "tolerances_1e-9_1e-12": {"REPRO_RTOL": "1e-9", "REPRO_ATOL": "1e-12"},
    "tolerances_1e-6_1e-8": {"REPRO_RTOL": "1e-6", "REPRO_ATOL": "1e-8"},
    "perturbation_0.01": {"REPRO_EPSILON": "0.01"},
    "perturbation_0.10": {"REPRO_EPSILON": "0.10"},
    "tauR_0.80": {"REPRO_TAU_R": "0.80"},
    "tauR_0.85": {"REPRO_TAU_R": "0.85"},
    "tauR_0.95": {"REPRO_TAU_R": "0.95"},
    "tauK_5": {"REPRO_TAU_K": "5"},
    "tauK_30": {"REPRO_TAU_K": "30"},
    "tauE_0.10": {"REPRO_TAU_E": "0.10"},
    "tauE_0.20": {"REPRO_TAU_E": "0.20"},
    "tauE_0.30": {"REPRO_TAU_E": "0.30"},
    "tauE_0.50": {"REPRO_TAU_E": "0.50"},
}
