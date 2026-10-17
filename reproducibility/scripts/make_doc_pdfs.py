#!/usr/bin/env python3
"""
Builds the PDF versions of the package manuals (README.pdf, DATA_DICTIONARY.pdf) and, if present,
of the Spanish guide, from their Markdown sources: Markdown -> standalone HTML with a print style
sheet (pandoc) -> PDF (headless Chrome or Edge). Tables wrap their text and long commands and paths
break inside their cell instead of running into the next column.

Requirements: pandoc and Google Chrome or Microsoft Edge (or set BROWSER to the executable).
Usage (from reproducibility/):  python scripts/make_doc_pdfs.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DOCS = [(HERE / "README.md", HERE / "README.pdf", "Reproducibility package: manual"),
        (HERE / "DATA_DICTIONARY.md", HERE / "DATA_DICTIONARY.pdf", "Reproducibility package: data dictionary"),
        (HERE.parent / "docs" / "REPRODUCIBILITY_PACKAGE_GUIDE_ES.md",
         HERE.parent / "docs" / "Reproducibility_package_guide_ES.pdf", "Guide to the reproducibility package (Spanish)")]

CSS = r"""
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
html { font-size: 10pt; }
body { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: #1f2328; line-height: 1.45;
       max-width: none; margin: 0; }
h1 { font-size: 19pt; margin: 0 0 4pt 0; color: #0b3d63; border-bottom: 2px solid #0b3d63; padding-bottom: 4pt; }
h2 { font-size: 14pt; margin: 18pt 0 6pt 0; color: #0b3d63; border-bottom: 1px solid #c9d6e2; padding-bottom: 2pt;
     page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt 0; color: #24292f; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
ul, ol { padding-left: 18pt; }
li { margin: 2pt 0; }
a { color: #0969da; text-decoration: none; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 8.8pt; background: #f2f4f7;
       padding: 0 2px; border-radius: 3px; overflow-wrap: anywhere; word-break: break-word; }
pre { background: #f6f8fa; border: 1px solid #d8dee4; border-radius: 4px; padding: 7pt 9pt;
      white-space: pre-wrap; overflow-wrap: anywhere; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.4pt; line-height: 1.35; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt 0; font-size: 8.6pt; table-layout: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #e8eef5; color: #0b3d63; text-align: left; font-weight: 600; }
th, td:first-child { overflow-wrap: normal; word-break: normal; hyphens: manual; }
td:first-child { min-width: 2.6em; }
ul { list-style: none; padding-left: 16pt; }
ul > li { position: relative; }
ul > li::before { content: "2"; position: absolute; left: -11pt; color: #0b3d63; font-family: Arial, sans-serif; }
th, td { border: 1px solid #c9d1d9; padding: 3pt 5pt; vertical-align: top; overflow-wrap: anywhere; }
td code, th code { font-size: 8pt; }
tr:nth-child(even) td { background: #fafbfc; }
hr { border: none; border-top: 1px solid #d8dee4; margin: 14pt 0; }
blockquote { margin: 6pt 0; padding: 2pt 10pt; border-left: 3px solid #c9d6e2; color: #57606a; }
"""


def browser():
    for c in [os.environ.get("BROWSER"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]:
        if c and Path(c).exists():
            return c
    sys.exit("Chrome or Edge not found; set BROWSER to its executable")


def build(md, pdf, title, exe, tmp):
    css = tmp / "style.css"
    css.write_text(CSS, encoding="utf-8")
    html = tmp / (md.stem + ".html")
    subprocess.run(["pandoc", str(md), "-f", "gfm", "-t", "html5", "-s", "--embed-resources",
                    "--css", str(css), "--metadata", f"pagetitle={title}", "-o", str(html)], check=True)
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"written {pdf}")


if __name__ == "__main__":
    exe = browser()
    with tempfile.TemporaryDirectory() as t:
        for md, pdf, title in DOCS:
            if md.exists():
                build(md, pdf, title, exe, Path(t))
