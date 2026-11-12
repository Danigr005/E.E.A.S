"""arq cte: local, citable copy of the official CTE Documentos Básicos (codigotecnico.org).

Usage:
  arq cte fetch [--only SI,SUA]     download the PDFs and extract text per page (idempotent)
  arq cte list                      what is stored, with source URL, download date and size
  arq cte search <regex> [--doc SI] [--context 1] [--max 20]    regex search; prints doc, page and lines
  arq cte page <doc> <n>            print one page of extracted text
Store: $EEAS_ARQ_HOME/cte (default ~/.local/share/eeas/arquitectura/cte). Text keeps one form feed per page,
so page numbers in `search` match the PDF page index (1-based), not the printed folio.
The files are the state's official texts: cite them as "<DB> <section>, PDF p.<n>, consulted <date>", and check
codigotecnico.org for later modifications before relying on a figure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import http.client
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://www.codigotecnico.org/pdf/Documentos"
DOCS = {  # id: (relative url, description)
    "PARTE1": ("Parte1/Parte_I_jun2022.pdf", "CTE Parte I (condiciones generales, exigencias basicas)"),
    "SE": ("SE/DBSE.pdf", "DB-SE Seguridad estructural"),
    "SE-AE": ("SE/DBSE-AE.pdf", "DB-SE-AE Acciones en la edificacion"),
    "SE-C": ("SE/DBSE-C.pdf", "DB-SE-C Cimientos"),
    "SE-A": ("SE/DBSE-A.pdf", "DB-SE-A Acero"),
    "SE-F": ("SE/DBSE-F.pdf", "DB-SE-F Fabrica"),
    "SE-M": ("SE/DBSE-M.pdf", "DB-SE-M Madera"),
    "SI": ("SI/DBSI.pdf", "DB-SI Seguridad en caso de incendio"),
    "SUA": ("SUA/DBSUA.pdf", "DB-SUA Seguridad de utilizacion y accesibilidad"),
    "HS": ("HS/DBHS.pdf", "DB-HS Salubridad"),
    "HR": ("HR/DBHR.pdf", "DB-HR Proteccion frente al ruido"),
    "HE": ("HE/DBHE.pdf", "DB-HE Ahorro de energia"),
}
USER_AGENT = "eeas-arquitectura/1.0 (document fetch)"
MAX_BYTES = 80 * 1024 * 1024
TIMEOUT = 60


class DownloadError(Exception):
    """One document could not be fetched; the others are still tried."""


def store() -> Path:
    root = Path(os.environ.get("EEAS_ARQ_HOME", Path.home() / ".local/share/eeas/arquitectura")) / "cte"
    root.mkdir(parents=True, exist_ok=True)
    return root


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read(MAX_BYTES + 1)
    except (OSError, http.client.HTTPException) as exc:
        raise DownloadError(f"download failed for {url}: {exc}") from exc
    if len(data) > MAX_BYTES:
        raise DownloadError(f"{url} exceeds {MAX_BYTES // 2**20} MB, refusing")
    if not data.startswith(b"%PDF"):
        raise DownloadError(f"{url} did not return a PDF (site layout changed?)")
    return data


def extract_text(pdf: Path, txt: Path) -> None:
    try:
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True, capture_output=True, timeout=300)
    except FileNotFoundError as exc:
        raise SystemExit("arq cte: pdftotext (poppler) is required") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"arq cte: pdftotext failed on {pdf.name}: {exc.stderr.decode(errors='replace')[:200]}") from exc


def cmd_fetch(a) -> None:
    root = store()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    wanted = [d.strip().upper() for d in a.only.split(",")] if a.only else list(DOCS)
    unknown = [d for d in wanted if d not in DOCS]
    if unknown:
        raise SystemExit(f"arq cte: unknown doc(s) {unknown}; known: {sorted(DOCS)}")
    failures: list[str] = []
    for doc in wanted:
        rel, desc = DOCS[doc]
        pdf, txt = root / f"{doc}.pdf", root / f"{doc}.txt"
        if pdf.exists() and txt.exists() and doc in manifest:
            print(f"= {doc}: already stored")
            continue
        url = f"{BASE}/{rel}"
        try:
            data = download(url)
        except DownloadError as exc:
            failures.append(f"{doc}: {exc}")
            print(f"! {doc}: {exc}", file=sys.stderr)
            continue
        pdf.write_bytes(data)
        extract_text(pdf, txt)
        manifest[doc] = {"url": url, "description": desc, "downloaded": date.today().isoformat(),
                         "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
        print(f"+ {doc}: {len(data) / 1e6:.1f} MB, {txt.read_text(errors='replace').count(chr(12))} pages")
    if failures:
        raise SystemExit(f"arq cte: {len(failures)} document(s) not fetched: " + "; ".join(failures))


def cmd_list(_a) -> None:
    mp = store() / "manifest.json"
    if not mp.exists():
        print("nothing stored yet: run `arq cte fetch`")
        return
    for doc, m in json.loads(mp.read_text()).items():
        print(f"{doc:<7} {m['downloaded']}  {m['bytes'] / 1e6:5.1f} MB  {m['description']}\n        {m['url']}")


def known_doc(doc: str) -> str:
    name = doc.strip().upper()
    if name not in DOCS:
        raise SystemExit(f"arq cte: unknown document '{doc}'; known: {sorted(DOCS)}")
    return name


def pages_of(doc: str) -> list[str]:
    doc = known_doc(doc)
    txt = store() / f"{doc.upper()}.txt"
    if not txt.exists():
        raise SystemExit(f"arq cte: {doc} not stored (run `arq cte fetch --only {doc}`)")
    return txt.read_text(errors="replace").split("\f")


def cmd_search(a) -> None:
    try:
        rx = re.compile(a.regex, re.IGNORECASE)
    except re.error as exc:
        raise SystemExit(f"arq cte: invalid regex: {exc}") from exc
    stored = [p.stem for p in sorted(store().glob("*.txt")) if p.stem in DOCS]
    if not stored:
        raise SystemExit("arq cte: no CTE text stored; run `arq cte fetch` first (an empty store must not read as 'no matches')")
    if len(stored) < len(DOCS) and not a.doc:
        print(f"warning: only {len(stored)} of {len(DOCS)} documents stored (missing: {sorted(set(DOCS) - set(stored))}); "
              "'no matches' may be a gap in the store. Run `arq cte fetch`.", file=sys.stderr)
    docs = [known_doc(d) for d in a.doc.split(",")] if a.doc else stored
    shown = 0
    for doc in docs:
        for pno, page in enumerate(pages_of(doc), start=1):
            lines = page.splitlines()
            for i, line in enumerate(lines):
                if rx.search(line):
                    lo, hi = max(0, i - a.context), min(len(lines), i + a.context + 1)
                    print(f"--- {doc} p.{pno}")
                    print("\n".join(l.rstrip() for l in lines[lo:hi]))
                    shown += 1
                    if shown >= a.max:
                        print(f"[stopped at --max {a.max}]")
                        return
    if not shown:
        print("no matches")


def cmd_page(a) -> None:
    pages = pages_of(a.doc)
    if not 1 <= a.n <= len(pages):
        raise SystemExit(f"arq cte: {a.doc} has pages 1-{len(pages)}")
    print(pages[a.n - 1])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq cte", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--only")
    sub.add_parser("list")
    s = sub.add_parser("search")
    s.add_argument("regex")
    s.add_argument("--doc")
    s.add_argument("--context", type=int, default=1)
    s.add_argument("--max", type=int, default=20)
    p = sub.add_parser("page")
    p.add_argument("doc")
    p.add_argument("n", type=int)
    a = ap.parse_args(argv)
    {"fetch": cmd_fetch, "list": cmd_list, "search": cmd_search, "page": cmd_page}[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
