#!/usr/bin/env python3
"""
Compare re-computed results with the stored ones (README, level C).

    python scripts/compare_results.py results_rerun/selection results/selection [--rtol 1e-6]

For every JSON file present in both folders, all fields are compared recursively; numbers are equal
if their relative difference is at most rtol (NaN equals NaN). Fields that record running times,
checkpoints or legacy bookkeeping are ignored (IGNORED). The list of differences is printed and the
exit code is 1 if there is any.
"""
import json
import math
import sys
from pathlib import Path

IGNORED = {"segundos", "T", "etapa_paper", "S_paper", "etapas_reanudadas"}


def compare(a, b, rtol, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in IGNORED:
                continue
            if k not in a or k not in b:
                out.append(f"{path}.{k}: only in {'new' if k not in b else 'stored'}")
                continue
            compare(a[k], b[k], rtol, f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, rtol, f"{path}[{i}]", out)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
            return
        if abs(a - b) > rtol * max(abs(a), abs(b), 1e-300):
            out.append(f"{path}: {a!r} vs {b!r}")
    elif a != b:
        out.append(f"{path}: {str(a)[:80]!r} vs {str(b)[:80]!r}")


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    rtol = float(sys.argv[sys.argv.index("--rtol") + 1]) if "--rtol" in sys.argv else 1e-6
    if "--rtol" in sys.argv:
        args.remove(sys.argv[sys.argv.index("--rtol") + 1])
    new, old = Path(args[0]), Path(args[1])
    files = sorted(set(f.name for f in new.glob("*.json")) & set(f.name for f in old.glob("*.json")))
    total = []
    for f in files:
        out = []
        compare(json.loads((new / f).read_text()), json.loads((old / f).read_text()), rtol, f[:-5], out)
        print(f"{'OK  ' if not out else 'DIFF'} {f[:-5]}" + (f"  ({len(out)} differences)" if out else ""))
        for line in out[:10]:
            print("      " + line)
        total += out
    print(f"\n{len(files)} files compared, {sum(1 for f in files if any(l.startswith(f[:-5]) for l in total))} with differences")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
