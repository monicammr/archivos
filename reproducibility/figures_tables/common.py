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


def load_validation():
    """External validation on real data, {problem: dict with the keys A_* of external_validation}.

    The test chi2/n of the reduced model, of the full model refitted to the training data and of
    theta0 are taken from results/nested_validation (the run used by every table, figure and
    statistical test), and from results/external_validation for the problems that run does not
    cover (no full refit, no split). The full-model refit of over-parameterised problems can end
    in different local optima in different runs, so a single run is used throughout. The
    training chi2/n of the full model is kept only where the two runs agree on the full model.
    """
    ext, nes = load("external_validation"), load("nested_validation")
    out = {}
    for p, v in ext.items():
        v = dict(v)
        n = nes.get(p)
        if n is not None:
            f_old = v.get("A_chi2_test_full")
            v["A_chi2_test_red"] = n["chi2_test_red_original"]
            v["A_chi2_test_full"] = n["chi2_test_full_train"]
            v["A_chi2_test_theta0"] = n["chi2_test_theta0"]
            f_new = n["chi2_test_full_train"]
            if not (isinstance(f_old, (int, float)) and isinstance(f_new, (int, float))
                    and abs(f_old - f_new) <= 0.01 * max(abs(f_new), 1e-300)):
                v.pop("A_chi2_train_full", None)
        out[p] = v
    return out


def efit_final(name, d):
    """Median e_fit of the final subset reported in Table 1, Supplementary Table S1 and Fig. 2.

    For the problems whose selection used the first-order e_fit, the final subset was re-estimated
    nonlinearly afterwards (results/efit_nonlinear); that value is reported. Returns (value, True)
    in that case and (value of the selection, False) otherwise.
    """
    f = RESULTS / "efit_nonlinear" / f"{name}.json"
    if f.exists():
        return json.loads(f.read_text())["eajuste_med_nolineal"], True
    return d.get("eajuste_med", float("nan")), False


def fmt_efit(x, tau=0.4358898943540674):
    """e_fit in percent with one decimal, or three when the value is within 0.1 points of tau_e."""
    return f"{100 * x:.3f}" if abs(x - tau) < 1e-3 else f"{100 * x:.1f}"


# Problems left out of the admissibility comparison between criteria. Bertozzi: our method selected
# its parameters on all measured outputs, which include the test conditions (New York), whereas the
# other criteria selected on the training outputs (California), so the criteria did not use the same
# information. It stays in the selection results (Table 1).
EXCLUDE_ADMISSIBILITY = {"Bertozzi_PNAS2020"}
