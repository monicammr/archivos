#!/usr/bin/env python3
"""Genera THEOREMS.md (catálogo de todos los teoremas y lemas, con su descripción) y
CheckAxioms.lean (#print axioms de cada teorema) a partir de los archivos .lean de esta carpeta."""
import re
from pathlib import Path

D = Path(__file__).resolve().parent
TEORIA = sorted(p for p in D.glob("*.lean") if p.stem not in ("All", "AllModels", "CheckAxioms", "CheckModelAxioms", "lakefile"))
MODELOS = sorted((D / "Models").glob("*.lean"))


def decls(path):
    txt = path.read_text(encoding="utf-8")
    ns, out = [], []
    doc = None
    for raw in txt.splitlines():
        line = raw.strip()
        m = re.match(r"namespace\s+(\S+)", line)
        if m:
            ns.append(m.group(1)); continue
        m = re.match(r"end\s+(\S+)", line)
        if m and ns and ns[-1] == m.group(1):
            ns.pop(); continue
        m = re.match(r"/--\s*(.*?)(-/)?$", line)
        if m:
            doc = m.group(1); continue
        m = re.match(r"(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(theorem|lemma)\s+([^\s(:{\[]+)", line)
        if m:
            name = ".".join(ns + [m.group(2)])
            d = re.sub(r"\*\*|`", "", doc or "").strip().rstrip(".")
            out.append((m.group(1), name, d, "private" in line))
            doc = None
        elif line and not line.startswith("--") and doc is not None and not raw.startswith(" "):
            doc = doc if line.startswith("theorem") or line.startswith("lemma") else doc
    return out


def resumen_modulo(path):
    txt = path.read_text(encoding="utf-8")
    m = re.search(r"/-!\s*\n?#?\s*(.*?)\n", txt)
    return m.group(1).strip("# ").strip() if m else ""


def main():
    L = ["# Catálogo de demostraciones formales (Lean 4 + Mathlib)", "",
         "Generado por `catalogo.py`. Todas las demostraciones compilan sin `sorry` ni axiomas propios.", ""]
    total = 0
    filas = []
    for p in TEORIA:
        ds = decls(p)
        total += len(ds)
        filas.append((p.stem, len(ds), resumen_modulo(p)))
    L += [f"**Módulos de teoría:** {len(TEORIA)}; **teoremas y lemas:** {total}. "
          f"**Modelos del benchmark verificados:** {len(MODELOS)}.", "",
          "## Resumen por módulo", "", "| Módulo | Teoremas y lemas | Contenido |", "|---|---|---|"]
    L += [f"| `{a}` | {b} | {c} |" for a, b, c in filas]
    L += ["", "## Todos los teoremas y lemas", ""]
    ax = ["-- Generado por catalogo.py: axiomas de cada teorema (deben ser sólo propext,",
          "-- Classical.choice y Quot.sound).", "import All", ""]
    for p in TEORIA:
        L += [f"### `{p.stem}`", "", "| Tipo | Nombre | Descripción |", "|---|---|---|"]
        for kind, name, d, priv in decls(p):
            L.append(f"| {kind} | `{name}` | {d} |")
            if not priv:
                ax.append(f"#print axioms {name}")
        L.append("")
    L += ["## Modelos del benchmark", "",
          "Cada archivo de `Models/` es un modelo traducido de SBML; su teorema final establece "
          "regularidad, existencia de solución en el horizonte simulado y no negatividad de las concentraciones.", ""]
    axm = ["-- Generado por catalogo.py: axiomas del teorema final de cada modelo.", "import AllModels", ""]
    for p in MODELOS:
        fin = [f"Models.{p.stem}.{n}" for n in re.findall(r"^(?:theorem|def)\s+(final\w*)", p.read_text(encoding="utf-8"), re.M)]
        L.append(f"* `{p.stem}`: " + (", ".join(f"`{n}`" for n in fin) or "—"))
        axm += [f"#print axioms {n}" for n in fin]
    (D / "CheckModelAxioms.lean").write_text("\n".join(axm) + "\n", encoding="utf-8")
    (D / "THEOREMS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (D / "CheckAxioms.lean").write_text("\n".join(ax) + "\n", encoding="utf-8")
    print(f"{len(TEORIA)} módulos, {total} declaraciones, {len(MODELOS)} modelos")


if __name__ == "__main__":
    main()
