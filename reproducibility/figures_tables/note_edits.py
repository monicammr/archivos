"""
Editorial edits of the generated Supplementary Notes.

Several Supplementary Notes are generated from the stored results (make_extra_notes.py,
make_formulas.py, make_models.py, make_robustness_note.py) and were afterwards edited by hand: wording
requested by the reviews, sections added later (for example the comparison of the complete method
with profile likelihood in the note on computational cost, or the independent directions in the note
on robustness) and cross-references. Those edits are stored, one file per note, in note_edits/<note>.json
as a list of line-level patches on the generated text, so that

    generated text  +  note_edits/<note>.json  =  the note in the Supplementary Information.

Every number derived from the results is still produced by the generator; a patch only changes
narrative text, cross-references or layout. A patch whose context is not found is reported and skipped,
so a change of the generated text is never hidden.
"""
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent / "note_edits"


def finalize(name, text):
    """Apply the stored editorial patches of note `name` (e.g. "suppl_cost") to its generated text."""
    f = DIR / f"{name}.json"
    if not f.exists():
        return text
    lines = text.split("\n")
    for p in json.loads(f.read_text(encoding="utf-8")):
        old, new = p["old"], p["new"]
        if old:
            for i in range(len(lines) - len(old) + 1):
                if lines[i:i + len(old)] == old:
                    lines[i:i + len(old)] = new
                    break
            else:
                print(f"note_edits: {name}: context not found, patch skipped: {old[0][:60]!r}")
        else:   # insertion after an anchor line (None: at the start)
            if p["after"] is None:
                lines[0:0] = new
                continue
            try:
                i = lines.index(p["after"])
            except ValueError:
                print(f"note_edits: {name}: anchor not found, insertion skipped: {p['after'][:60]!r}")
                continue
            lines[i + 1:i + 1] = new
    return "\n".join(lines)
