"""arq areas: verify a room/surface table (arithmetic only, no regulations).

Usage:
  arq areas <table.csv> [--tol 0.02] [--built-total 123.4] [--useful-total 98.7]
CSV columns (header required, ';' or ',' separated):
  name, declared_m2, width_m, depth_m          (width/depth optional; used to recompute rectangles)
Reports: declared vs recomputed area per room, sum of rooms vs the declared totals, useful/built ratio,
and rows that do not add up. Spanish decimals (1,5) are accepted.
"""
from __future__ import annotations

import argparse
import csv
import sys

DEFAULT_TOL = 0.02
MIN_RATIO, MAX_RATIO = 0.60, 0.95  # useful/built outside this range usually means a transcription error


def num(text: str | None) -> float | None:
    if text is None or not text.strip():
        return None
    try:
        return float(text.strip().replace(",", "."))
    except ValueError as exc:
        raise SystemExit(f"arq areas: not a number: '{text}'") from exc


def read_rows(path: str) -> list[dict]:
    for encoding in ("utf-8-sig", "cp1252"):  # Spanish Excel exports CSV as cp1252
        try:
            with open(path, newline="", encoding=encoding) as fh:
                sample = fh.read(2048)
                fh.seek(0)
                delim = ";" if sample.count(";") > sample.count(",") else ","
                reader = csv.DictReader(fh, delimiter=delim)
                fields = {f.strip() for f in (reader.fieldnames or [])}
                if not {"name", "declared_m2"} <= fields:
                    print(f"arq areas: header must contain at least name and declared_m2, found {sorted(fields)}", file=sys.stderr)
                    raise SystemExit(2)
                return [{(k or "").strip(): v for k, v in row.items()} for row in reader]
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise SystemExit(f"arq areas: cannot read {path}: {exc}") from exc
    raise SystemExit(f"arq areas: {path} is neither UTF-8 nor cp1252 text")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq areas", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL)
    ap.add_argument("--built-total", type=float)
    ap.add_argument("--useful-total", type=float)
    a = ap.parse_args(argv)

    rows = read_rows(a.file)
    problems = 0
    total = 0.0
    for r in rows:
        name = (r.get("name") or "?").strip()
        declared, w, d = num(r.get("declared_m2")), num(r.get("width_m")), num(r.get("depth_m"))
        total += declared or 0
        note = ""
        if declared is not None and w and d:
            calc = w * d
            if abs(calc - declared) / max(calc, 1e-9) > a.tol:
                note = f"  [MISMATCH: {w}x{d} = {calc:.2f}]"
                problems += 1
        print(f"{name:<28} declared {declared if declared is not None else 'n/a':>8}{note}")
    print(f"sum of rooms: {total:.2f} m2")
    if a.useful_total is not None:
        diff = total - a.useful_total
        status = "OK" if abs(diff) / max(a.useful_total, 1e-9) <= a.tol else "MISMATCH"
        problems += status != "OK"
        print(f"declared useful total {a.useful_total:.2f}: difference {diff:+.2f} m2 [{status}]")
    if a.built_total:
        # Without --useful-total the rooms listed are taken as the useful area (they must be a subset of the built one).
        useful = a.useful_total if a.useful_total is not None else total
        if useful > a.built_total * (1 + a.tol):
            print(f"useful {useful:.2f} m2 EXCEEDS built {a.built_total:.2f} m2 [MISMATCH: impossible; "
                  f"check which rooms the built total includes]")
            problems += 1
        else:
            ratio = useful / a.built_total
            status = "OK" if MIN_RATIO <= ratio <= MAX_RATIO else "SUSPICIOUS"
            problems += status != "OK"
            print(f"useful/built = {ratio:.2f} [{status}: expected {MIN_RATIO}-{MAX_RATIO}]")
    print(f"{problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
