"""
Paths shared by the scripts that generate the figures, tables and Supplementary Notes of the paper
from the stored results.

* RESULTS: the results of the analyses (default ../results; REPRO_RESULTS to use another folder,
  e.g. the output of a re-run).
* LEAN: the Lean development (../lean_proofs).
* OUT: where the LaTeX fragments, tables/ and figures/ are written (default ./output; the paper is
  built with PAPER_DIR pointing to the folder of main.tex).
"""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = Path(os.environ.get("REPRO_RESULTS", ROOT / "results"))
LEAN = ROOT / "lean_proofs"
OUT = Path(os.environ.get("PAPER_DIR", HERE / "output"))
FIG = OUT / "figures"
TAB = OUT / "tables"
for _d in (OUT, FIG, TAB):
    _d.mkdir(parents=True, exist_ok=True)


def load(sub):
    """{problem: result} for the JSON files of RESULTS/sub (empty if the folder does not exist)."""
    d = RESULTS / sub
    return {f.stem: json.loads(f.read_text()) for f in sorted(d.glob("*.json"))} if d.exists() else {}


def measurements():
    """{problem: (number of measurements, number of experimental conditions)} from the simulator check."""
    out = {}
    for line in (RESULTS / "simulator_check" / "simulator_check.jsonl").read_text().splitlines():
        if line.startswith("{"):
            d = json.loads(line)
            out[d["sistema"]] = (d["mediciones"], d["condiciones"])
    return out
