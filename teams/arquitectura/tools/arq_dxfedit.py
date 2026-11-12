"""arq dxfedit: add review marks / proposals to a COPY of a DXF. Never modifies the original.

Usage:
  arq dxfedit <in.dxf> <ops.json> [--out out.dxf] [--force]
Output defaults to <in>_eeas.dxf next to the input. Refuses to write to the input file (or any hard link / link to it),
and refuses to overwrite any other existing file unless --force. The file is written to a temp name and moved into place.
ops.json: list of operations, coordinates and sizes in METRES (converted to the drawing's units via $INSUNITS):
  {"op": "line", "a": [x,y], "b": [x,y]}
  {"op": "polyline", "points": [[x,y],...], "closed": true}
  {"op": "rect", "min": [x,y], "max": [x,y]}
  {"op": "circle", "center": [x,y], "radius": r}
  {"op": "text", "at": [x,y], "text": "...", "height": 0.15}
  {"op": "note", "at": [x,y], "text": "H1: pasillo 0,80 m (ejemplo ilustrativo)"}      (text with a leader circle)
Each op may set "kind": "correccion" (red, layer EEAS_CORRECCION) or "propuesta" (green, layer EEAS_PROPUESTA);
default is "correccion". Everything lands on those two layers so it can be hidden or deleted in one step.
Unit-less drawings: pass --assume-units m|cm|mm after confirming the unit; otherwise the tool refuses.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import ezdxf
from ezdxf import units as dxf_units

LAYERS = {"correccion": ("EEAS_CORRECCION", 1), "propuesta": ("EEAS_PROPUESTA", 3)}
DEFAULT_TEXT_HEIGHT_M = 0.15
DEFAULT_RADIUS_M = 0.5
ASSUMED = {"m": 1.0, "cm": 0.01, "mm": 0.001}


def drawing_unit_in_metres(doc, assume: str | None) -> float:
    code = doc.header.get("$INSUNITS", 0)
    if code:
        try:
            return dxf_units.conversion_factor(code, dxf_units.M)
        except (KeyError, TypeError, IndexError, ZeroDivisionError):
            pass
    if assume:
        return ASSUMED[assume]
    raise SystemExit("arq dxfedit: the drawing declares no usable $INSUNITS. Confirm the unit against a known dimension and "
                     "re-run with --assume-units m|cm|mm (marks would be 1000x too small or too large otherwise).")


def pt(value, name: str, k: float) -> tuple[float, float]:
    try:
        x, y = value
        return float(x) / k, float(y) / k
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"arq dxfedit: '{name}' must be [x, y], got {value!r}") from exc


def apply_op(msp, op: dict, index: int, k: float) -> None:
    """k = metres per drawing unit; op values are in metres."""
    if not isinstance(op, dict):
        raise SystemExit(f"arq dxfedit: op #{index} must be an object")
    kind = op.get("kind", "correccion")
    if kind not in LAYERS:
        raise SystemExit(f"arq dxfedit: op #{index}: kind must be one of {sorted(LAYERS)}")
    layer, color = LAYERS[kind]
    attr = {"layer": layer, "color": color}
    name = op.get("op")
    if name == "line":
        msp.add_line(pt(op.get("a"), "a", k), pt(op.get("b"), "b", k), dxfattribs=attr)
    elif name == "polyline":
        pts = [pt(p, "points", k) for p in op.get("points", [])]
        if len(pts) < 2:
            raise SystemExit(f"arq dxfedit: op #{index}: polyline needs 2+ points")
        msp.add_lwpolyline(pts, close=bool(op.get("closed")), dxfattribs=attr)
    elif name == "rect":
        (x0, y0), (x1, y1) = pt(op.get("min"), "min", k), pt(op.get("max"), "max", k)
        msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs=attr)
    elif name == "circle":
        msp.add_circle(pt(op.get("center"), "center", k), float(op.get("radius", DEFAULT_RADIUS_M)) / k, dxfattribs=attr)
    elif name in ("text", "note"):
        h = float(op.get("height", DEFAULT_TEXT_HEIGHT_M)) / k
        at = pt(op.get("at"), "at", k)
        if name == "note":
            msp.add_circle(at, h, dxfattribs=attr)
            at = (at[0] + 2 * h, at[1])
        msp.add_text(str(op.get("text", "")), height=h, dxfattribs=attr).set_placement(at)
    else:
        raise SystemExit(f"arq dxfedit: op #{index}: unknown op {name!r}")


def check_destination(src: Path, out: Path, force: bool) -> None:
    if out.exists():
        if os.path.samefile(out, src):
            raise SystemExit("arq dxfedit: refusing to overwrite the original drawing (same file or a link to it)")
        if not force:
            raise SystemExit(f"arq dxfedit: {out} already exists; choose another --out or pass --force")
    if out.resolve() == src.resolve():
        raise SystemExit("arq dxfedit: refusing to overwrite the original drawing")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq dxfedit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dxf")
    ap.add_argument("ops")
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true", help="overwrite an existing output file (never the input)")
    ap.add_argument("--assume-units", choices=sorted(ASSUMED))
    a = ap.parse_args(argv)

    src = Path(a.dxf)
    out = Path(a.out) if a.out else src.with_name(src.stem + "_eeas.dxf")
    check_destination(src, out, a.force)
    try:
        try:
            doc = ezdxf.readfile(str(src))
        except (ezdxf.DXFStructureError, UnicodeDecodeError):
            from ezdxf import recover

            doc, auditor = recover.readfile(str(src))
            print(f"warning: input DXF was damaged; recovered ({len(auditor.errors)} errors fixed)", file=sys.stderr)
        with open(a.ops, encoding="utf-8") as fh:
            ops = json.load(fh)
    except (OSError, json.JSONDecodeError, ezdxf.DXFError, UnicodeDecodeError) as exc:
        raise SystemExit(f"arq dxfedit: {exc}") from exc
    if not isinstance(ops, list):
        raise SystemExit("arq dxfedit: ops.json must be a list")
    k = drawing_unit_in_metres(doc, a.assume_units)
    for name, color in LAYERS.values():
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    msp = doc.modelspace()
    for i, op in enumerate(ops):
        apply_op(msp, op, i, k)
    tmp = out.with_name(out.name + ".tmp")
    try:
        doc.saveas(str(tmp))
        check_destination(src, out, a.force)  # re-check right before the move
        os.replace(tmp, out)
    finally:
        if tmp.exists():
            tmp.unlink()
    print(f"{len(ops)} operations written to {out} (original untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
