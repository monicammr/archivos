# Paper 2: version submitted to Scientific Reports (15 November 2026)

This folder records exactly what was submitted on 15 November 2026. It is separate from `paper/scirep/`,
whose `main.tex` (tag `scirep-submission`, commit 1f96461) is a later, shortened draft that was not the
one submitted.

## Origin

The sources are those of commit `3bb72dbe` (17 October 2026, 11:36), the version reviewed by the
supervisor, with these changes:

1. **Reproducibility package DOI**: `10.5281/zenodo.23338175` (record of version 1.0.0) replaced by
   `10.5281/zenodo.23338174` (all versions; resolves to version 1.6.0, the package described in the text).
2. **Abstract** rewritten for a general reader, following the supervisor's review: no technical terms, the
   problem, the method and its impact, few numbers (187 words).
3. **Introduction**: technical terms explained at first use (profile likelihood, redundant parameters,
   pivoted QR, Brun's collinearity index, social cognitive theory, PEtab and SBML, conditioning tests,
   Lean 4 and Mathlib).
4. **Third person** throughout the paper and the Supplementary Information (no "we", "our", "us"):
   "our method/subsets" became "the proposed method/subsets"; table headers "Ours" became "Proposed".
5. **Figures with "Our method" in their labels** were regenerated from the stored results of the
   reproducibility package with the labels changed and nothing else: `figures/fig4_comparison.*`,
   `figures/fig_brun.pdf`, `figures/figS_admissibility_map.pdf`, `figures/figS_synth_seeds.pdf`. The
   patched scripts are in `figure_scripts/`; the package itself (Zenodo version 1.6.0) is unchanged and its
   scripts still write "Our method".
6. **Cover letter**: dated 15 November 2026; title of the paper; the admissibility test described; the
   imposed minimum of two clarified; null baselines explained; no suggested or excluded reviewers; related
   submission (IFAC SysID 2027 conference paper, being submitted the same day).

No number, result, table or reference of the paper or the Supplementary Information changed.

## Files

- `main.tex`, `supplementary.tex`, `suppl_*.tex`, `tables/`, `figures/`, `references.tex`,
  `cover_letter.tex`: LaTeX sources (build: `pdflatex supplementary` three times, then
  `pdflatex main && bibtex main && pdflatex main && pdflatex main`; `cover_letter.tex` with pdflatex).
- `pdf_enviados/`: the PDFs submitted (paper, Supplementary Information, cover letter) and a Spanish
  translation of the cover letter for internal review (not submitted).
- `figure_scripts/`: the figure scripts of the reproducibility package with the labels in third person.
