#!/usr/bin/env bash
# Download the PEtab benchmark collection at the commit used in the paper (35 problems, about 80 MB)
# into data/Benchmark-Models-PEtab/. Only needed for levels C (re-running the analyses).
set -euo pipefail
cd "$(dirname "$0")/.."
COMMIT=fcbddf1b900efabdfbdc2b58452c89556e63f1ce
URL=https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab.git
DEST=data/Benchmark-Models-PEtab
PROBLEMS="Alkan_SciSignal2018 Armistead_CellDeathDis2024 Bachmann_MSB2011 Beer_MolBioSystems2014
Bertozzi_PNAS2020 Blasi_CellSystems2016 Boehm_JProteomeRes2014 Borghans_BiophysChem1997 Brannmark_JBC2010
Bruno_JExpBot2016 Chen_MSB2009 Crauste_CellSystems2017 Elowitz_Nature2000 Fiedler_BMCSystBiol2016
Froehlich_CellSystems2018 Fujita_SciSignal2010 Giordano_Nature2020 Isensee_JCB2018 Lang_PLOSComputBiol2024
Laske_PLOSComputBiol2019 Liu_IFACPapersOnLine2025 Lucarelli_CellSystems2018 Okuonghae_ChaosSolitonsFractals2020
Oliveira_NatCommun2021 Perelson_Science1996 Rahman_MBS2016 Raia_CancerResearch2011 Raimundez_PCB2020
SalazarCavazos_MBoC2020 Schwen_PONE2014 Smith_BMCSystBiol2013 Sneyd_PNAS2002 Weber_BMC2015
Zhao_QuantBiol2020 Zheng_PNAS2012"
if [ -d "$DEST/problems" ]; then
  echo "$DEST already exists"; exit 0
fi
mkdir -p data
git clone --filter=blob:none --no-checkout "$URL" "$DEST"
cd "$DEST"
git sparse-checkout init --no-cone
{ echo "/README.md"; for p in $PROBLEMS; do echo "/problems/$p/"; done; } | git sparse-checkout set --no-cone --stdin
git checkout -q "$COMMIT"
echo "PEtab benchmark at commit $(git rev-parse --short HEAD): $(ls problems | wc -l) problems in $DEST/problems"
