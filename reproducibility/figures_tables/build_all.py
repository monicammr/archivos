#!/usr/bin/env python3
"""
Regenerate every figure, table and Supplementary Note of the paper from the stored results
(README, level A). Takes a few minutes; no simulation is run.

Output folder: ./output (or the folder given by PAPER_DIR):
  tables/table1.tex, tables/tableS1.tex, tables/tableS3.tex
  figures/fig1_pipeline ... fig6_architecture (.pdf, .eps, .tif), figures/figS*.pdf
  figure3/ (consolidated table and counts of Fig. 3)
  suppl_*.tex (Supplementary Notes that contain numbers)

Usage: python build_all.py
"""
import os
import subprocess
import sys
import time

from common import HERE, OUT

STEPS = [
    ("Table 1 and Supplementary Table S1", "make_tables.py"),
    ("Figures 1-6 and Supplementary Fig. S1 (EPS and TIFF copies)", "make_figures.py"),
    ("Notes: simulator, synthetic experiment, single parameter, settings, cost", "make_extra_notes.py"),
    ("Note: robustness (and Supplementary Fig. S2)", "make_robustness_note.py"),
    ("Note: system-by-system summary", "make_systems_note.py"),
    ("Note: statements of the formal theorems (and lean_proofs/FORMULAS.md)", "make_formulas.py"),
    ("Supplementary Table S3 (Lean modules)", "make_tableS3.py"),
    ("Note: verified benchmark models (Supplementary Tables S7, S8)", "make_models.py"),
    ("Identifiability of the subsets of every criterion (Supplementary Tables and the column of Table 2)", "identif_criteria_tables.py"),
    ("Second audit: statistics of the comparison (fixed scenarios, null controls, standard QR, training-output selection, three families of truths) and Table 2", "audit2_stats.py"),
    ("Comparison with other criteria: Fig. 3 (revised) and Fig. 4", "comparison_figures.py"),
    ("Second audit: supplementary tables (nonlinear check, admissibility per problem, synthetic families, identifiability by region)", "audit2_tables.py"),
    ("Comparison with other criteria: supplementary figures", "comparison_suppl_figures.py"),
    ("Pivoted QR against our method on real data (Supplementary Fig., fig_brun.pdf)", "figure_qr_scatter.py"),
    ("Identifiability of the selected parameters (Supplementary Table, tableS_identif)", "identifiability_table.py"),
    ("Identifiability: profiles of every problem and per-parameter table (figS_identif_profiles, tableS_identif_param)", "identifiability_details.py"),
    ("Comparison with other criteria and further validations: supplementary tables", "comparison_tables.py"),
    ("Comparison with other criteria: bootstrap and McNemar statistics", "comparison_statistics.py"),
    ("Comparison with other criteria: summary of the counts quoted in the text", "comparison_summary.py"),
    ("Additional analyses of the review: robustness with independent directions, signal and amplitudes, error in noise units, settings of Lang and Raimundez", "make_review_notes.py"),
    ("Test of the minimum subset size k_min = 2 (Supplementary Table)", "kmin_tables.py"),
    ("Admissibility with the calibration parameters fixed (Supplementary Tables)", "calibration_fixed_tables.py"),
    ("Conditioning of the final subsets with unit-length columns (Supplementary Table)", "conditioning_table.py"),
    ("Computing time of every analysis (Supplementary Tables of computing time)", "make_timing_notes.py"),
]

if __name__ == "__main__":
    failed = []
    for label, script in STEPS:
        t = time.time()
        print(f"== {label} ({script})", flush=True)
        # UTF-8 output also on consoles with another default encoding (Windows)
        r = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if r.returncode != 0:
            failed.append(script)
        print(f"   {'done' if r.returncode == 0 else 'NOT DONE'} in {time.time() - t:.0f} s", flush=True)
    print(f"\nOutput written to {OUT}")
    if failed:
        print("Not completed:", ", ".join(failed),
              )
