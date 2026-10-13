# Building the manuscript and the Supplementary Information

The figures, Table 1, the Supplementary Tables S1/S3 and the Supplementary Notes that contain numbers
are generated from the results of the reproducibility package (`../../reproducibility/`), with the
output written into this folder:

```bash
cd ../../reproducibility/figures_tables
PAPER_DIR=../../paper/scirep SCT_DATA=../../certificados/datos_sct/datos_sct_31dias.csv python build_all.py
cd ../../paper/scirep
pdflatex main && bibtex main && pdflatex main && pdflatex main
pdflatex supplementary && pdflatex supplementary && pdflatex supplementary
```

(`SCT_DATA` points to the participant data of the SCT example, which are not public; without it the
SCT note and Supplementary Fig. S3 are left as they are.)

Files written by the build: `tables/table1.tex`, `tables/tableS1.tex`, `tables/tableS3.tex`,
`figures/fig*.{pdf,eps,tif}`, `figures/figS*.pdf`, `figure3/`, `suppl_simulator.tex`,
`suppl_synthetic.tex`, `suppl_single.tex`, `suppl_settings.tex`, `suppl_cost.tex`,
`suppl_robustness.tex`, `suppl_systems.tex`, `suppl_formulas.tex`, `suppl_models.tex`, `suppl_sct.tex`.
The other `.tex` files (`main.tex`, `supplementary.tex`, `note_sequence.tex`, `suppl_validation.tex`,
`suppl_reproduction.tex`, `suppl_conclusion.tex`, `references.tex`) are written by hand.

The DOI of the reproducibility package on Zenodo is set once, in the macro `\zenododoi` at the top of
`main.tex` and of `supplementary.tex`.
