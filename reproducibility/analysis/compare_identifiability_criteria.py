#!/usr/bin/env python3
"""
Compares the practical identifiability of the parameters selected by our method and by the other
criteria (Brun, Morris, standard pivoted QR, profile likelihood), after running
scripts/run_identifiability_other_criteria.sh.

Profiles: results/identifiability/profiles/<p>.json (our subsets) and
          results/identifiability/profiles_subsets_<criterion>/<p>.json (other criteria; only the
          problems whose subset differs from ours were profiled, the others reuse our profiles).
Each profile file lists, per selected parameter, its class: "identificable" (Delta chi2 > 3.84 on
both sides), "no identificable practico" (one side) or "plano" (neither).

Comparison on the problems that every criterion has (same problems for all):
  * identifiable parameters / selected parameters, per criterion;
  * problems in which every selected parameter is identifiable;
  * paired comparison with ours over problems: exact McNemar test on "all identifiable", and the
    number of problems in which the criterion has more / fewer identifiable parameters.

Usage: python compare_identifiability_criteria.py   -> table on screen and
       results/identifiability/criteria_comparison.json
"""
import json

from scipy.stats import binomtest

import config as CFG

ID = CFG.IDENTIFIABILITY
CRIT = ["brun", "morris", "qr_gks", "perfil"]


def load(folder):
    out = {}
    for f in (ID / folder).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "perfiles" in d:
            out[f.stem] = {p["parametro"]: p["clase"] for p in d["perfiles"]}
    return out


if __name__ == "__main__":
    ours = load("profiles")
    sel = {f.stem: json.loads(f.read_text()) for f in CFG.SELECTION.glob("*.json")}
    res = {"ours": ours}
    for c in CRIT:
        subs = {f.stem: json.loads(f.read_text()) for f in (CFG.RESULTS / f"subsets_{c}").glob("*.json")}
        prof = load(f"profiles_subsets_{c}")
        r = {}
        for p, d in subs.items():
            if set(d["S"]) == set(sel[p]["S"]) and p in ours:
                r[p] = ours[p]                       # same subset as ours: same profiles
            elif p in prof:
                r[p] = prof[p]
        res[c] = r
    common = sorted(set.intersection(*[set(v) for v in res.values()]))
    print(f"Problems with profiles for every criterion: {len(common)}")
    print(f"{'criterion':10s} {'identifiable params':>20s} {'problems all identifiable':>27s}  vs ours: McNemar P, more/fewer")
    summary = {"problems": common}
    allid = {m: {p: all(v == "identificable" for v in res[m][p].values()) for p in common} for m in res}
    nid = {m: {p: sum(v == "identificable" for v in res[m][p].values()) for p in common} for m in res}
    for m in ["ours"] + CRIT:
        tot = sum(len(res[m][p]) for p in common)
        ni = sum(nid[m].values())
        na = sum(allid[m].values())
        line = f"{m:10s} {ni:>9d} of {tot:<9d} {na:>13d} of {len(common):<12d}"
        row = {"identifiable": ni, "selected": tot, "all_identifiable": na}
        if m != "ours":
            b = sum(allid["ours"][p] and not allid[m][p] for p in common)
            c = sum(allid[m][p] and not allid["ours"][p] for p in common)
            pv = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
            more = sum(nid[m][p] > nid["ours"][p] for p in common)
            fewer = sum(nid[m][p] < nid["ours"][p] for p in common)
            line += f"  P={pv:.3g}, {more} more / {fewer} fewer"
            row.update(mcnemar_only_ours=b, mcnemar_only_other=c, p=pv, more=more, fewer=fewer)
        print(line)
        summary[m] = row
    (ID / "criteria_comparison.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("written", ID / "criteria_comparison.json")
