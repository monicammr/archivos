#!/usr/bin/env python3
"""
Control of the translation check (Supplementary Note "Verified benchmark models"): a 1 % change of
one number of a Lean model file must be detected by verify_translation.py.

For the chosen model (default Boehm_JProteomeRes2014) three modified copies of its Lean file are
written to a temporary folder, each with one number multiplied by 1.01:
  * the first parameter value of theta_q (`def θq`),
  * the first initial value of x_q (`def xq`),
  * the first stoichiometric coefficient of the reaction list (`def Rx`);
verify_translation.py is then run on each copy. The expected result is a relative difference of
about 1e-2 (instead of rounding error, ~1e-12, for the original file).

Usage: python mutation_control.py [Problem]
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = HERE.parent / "lean_proofs" / "Models"
NUM = re.compile(r"\((-?\d+)(?: / (\d+))? : ℚ\)")


def scale_first(text, start, factor=Fraction(101, 100)):
    """Multiply by `factor` the first rational literal after position `start`."""
    m = NUM.search(text, start)
    q = Fraction(int(m.group(1)), int(m.group(2) or 1))
    if q == 0:                      # skip zeros (a 1 % change of 0 is 0)
        return scale_first(text, m.end(), factor)
    r = q * factor
    return text[:m.start()] + f"({r.numerator} / {r.denominator} : ℚ)" + text[m.end():]


def run(models_dir, name):
    out = subprocess.run([sys.executable, str(HERE / "verify_translation.py"), name,
                          "--models-dir", str(models_dir)], capture_output=True, text=True)
    line = [ln for ln in out.stdout.splitlines() if ln.startswith("{")][-1]
    r = json.loads(line)
    return {k: r.get(k) for k in ("err_rel_max", "err_theta", "err_x0", "error")}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Boehm_JProteomeRes2014"
    original = (MODELS / f"{name}.lean").read_text()
    results = {"original": run(MODELS, name)}
    for label, anchor in (("parameter (θq) x 1.01", "def θq"), ("initial value (xq) x 1.01", "def xq"),
                          ("stoichiometric coefficient x 1.01", "def Rx")):
        i = original.index(anchor)
        if label.startswith("stoichiometric"):
            i = original.index("[(", original.index("), [(", i))     # first column of the first reaction
        mutated = scale_first(original, i)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "Models"
            shutil.copytree(MODELS, d)
            (d / f"{name}.lean").write_text(mutated)
            results[label] = run(d, name)
    print(json.dumps({"sistema": name, **results}, indent=1))


if __name__ == "__main__":
    main()
