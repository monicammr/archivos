#!/usr/bin/env python3
"""
Regenerate every figure, table and Supplementary Note of the paper from the stored results
(README, level A). Takes a few minutes; no simulation is run except the small refits of the SCT note.

Output folder: ./output (or the folder given by PAPER_DIR):
  tables/table1.tex, tables/tableS1.tex, tables/tableS3.tex
  figures/fig1_pipeline ... fig6_architecture (.pdf, .eps, .tif), figures/figS*.pdf
  figure3/ (consolidated table and counts of Fig. 3)
  suppl_*.tex (Supplementary Notes that contain numbers)

Usage: python build_all.py
"""
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
    ("Note: SCT model (Supplementary Table S16, Fig. S3; needs the participant data)", "make_sct_note.py"),
    ("Comparison with other criteria: Fig. 3 (revised) and Fig. 4", "comparison_figures.py"),
    ("Comparison with other criteria: supplementary figures", "comparison_suppl_figures.py"),
    ("Pivoted QR against our method on real data (Supplementary Fig., fig_brun.pdf)", "figure_qr_scatter.py"),
    ("Comparison with other criteria and further validations: supplementary tables", "comparison_tables.py"),
    ("Comparison with other criteria: bootstrap and McNemar statistics", "comparison_statistics.py"),
    ("Comparison with other criteria: summary of the counts quoted in the text", "comparison_summary.py"),
]

if __name__ == "__main__":
    failed = []
    for label, script in STEPS:
        t = time.time()
        print(f"== {label} ({script})", flush=True)
        r = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE)
        if r.returncode != 0:
            failed.append(script)
        print(f"   {'done' if r.returncode == 0 else 'NOT DONE'} in {time.time() - t:.0f} s", flush=True)
    print(f"\nOutput written to {OUT}")
    if failed:
        print("Not completed:", ", ".join(failed),
              "(make_sct_note.py needs the SCT participant data, available on request)")
