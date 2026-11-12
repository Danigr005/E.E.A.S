"""arq dxf: read-only inspection of a DXF drawing (convert DWG to DXF first).

Usage:
  arq dxf summary <file.dxf>                       units, extents, layers, entity counts, blocks
  arq dxf areas <file.dxf> [--layer L]             closed polylines: area (m2) and perimeter (m), per layer
  arq dxf dims <file.dxf>                          DIMENSION entities: measured vs overridden text, mismatches flagged
  arq dxf text <file.dxf> [--layer L]              TEXT/MTEXT contents with positions (metres)
  arq dxf blocks <file.dxf>                        block insert counts (doors, windows, fixtures) with names
  arq dxf render <file.dxf> <out.png> [--dpi 150]  rasterise the modelspace for visual review
Options (before the subcommand's file): --assume-units m|cm|mm   use when the drawing declares no $INSUNITS.
Lengths are converted to metres from $INSUNITS. If the drawing is unit-less, areas/dims/text REFUSE to guess:
pass --assume-units after confirming the unit against a known dimension (door width, room size).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict

import ezdxf
from ezdxf import units as dxf_units

DIM_MISMATCH_TOLERANCE = 0.01
NUMBER = re.compile(r"[-+]?\d+(?:[.,]\d+)?")
ASSUMED = {"m": 1.0, "cm": 0.01, "mm": 0.001}
ANGULAR_DIMTYPES = (2, 5)  # angular (2-line) and angular (3-point)
ORDINATE_DIMTYPE = 6


def load(path: str):
    try:
        return ezdxf.readfile(path)
    except (ezdxf.DXFStructureError, UnicodeDecodeError) as exc:
        try:
            from ezdxf import recover

            doc, auditor = recover.readfile(path)
            print(f"warning: {path} is damaged ({exc}); recovered with {len(auditor.errors)} error(s) fixed, "
                  f"{len(auditor.fixes)} fix(es). Verify the drawing visually.", file=sys.stderr)
            return doc
        except Exception as exc2:
            raise SystemExit(f"arq dxf: {path} is not a readable DXF: {exc2}") from exc2
    except OSError as exc:
        raise SystemExit(f"arq dxf: cannot open {path}: {exc}") from exc


def metre_factor(doc, assume: str | None = None) -> tuple[float | None, str]:
    """Return (factor to metres or None when unknown, label)."""
    code = doc.header.get("$INSUNITS", 0)
    if code == 0:
        if assume:
            return ASSUMED[assume], f"unitless, ASSUMED {assume} by --assume-units"
        return None, "unitless ($INSUNITS=0)"
    try:
        return dxf_units.conversion_factor(code, dxf_units.M), dxf_units.decode(code)
    except (KeyError, TypeError, IndexError, ZeroDivisionError):
        if assume:
            return ASSUMED[assume], f"unsupported $INSUNITS={code}, ASSUMED {assume}"
        return None, f"unsupported $INSUNITS={code}"


def require_factor(doc, assume: str | None) -> tuple[float, str]:
    factor, label = metre_factor(doc, assume)
    if factor is None:
        raise SystemExit(f"arq dxf: drawing units unknown ({label}). Confirm the unit against a known dimension and "
                         "re-run with --assume-units m|cm|mm. Refusing to print numbers that could be off by 1000x.")
    print(f"[units: {label}; factor to m = {factor}]")
    return factor, label


def closed_polylines(msp, layer: str | None):
    for e in msp:
        if layer and e.dxf.layer != layer:
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = list(e.get_points("xyb"))
            if e.closed or (len(pts) > 3 and pts[0][:2] == pts[-1][:2]):
                yield e, [(p[0], p[1]) for p in pts], any(abs(p[2]) > 1e-9 for p in pts)
        elif e.dxftype() == "POLYLINE" and e.is_closed and not e.is_3d_polyline:
            yield e, [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices], any(abs(v.dxf.get("bulge", 0)) > 1e-9 for v in e.vertices)


def cmd_summary(doc, a) -> None:
    f, unit = metre_factor(doc, a.assume_units)
    msp = doc.modelspace()
    counts = Counter(e.dxftype() for e in msp)
    if f is None:
        print(f"WARNING: drawing is {unit}: numbers below are in raw drawing units, NOT metres. Use --assume-units after checking.")
        f = 1.0
    print(f"DXF version: {doc.dxfversion}   units: {unit}   factor to m: {f}")
    try:
        from ezdxf import bbox

        ext = bbox.extents(msp)
        if ext.has_data:
            size = ext.size
            print(f"extents (units x factor): {size.x * f:.2f} x {size.y * f:.2f}   min=({ext.extmin.x * f:.2f},{ext.extmin.y * f:.2f})")
    except Exception as exc:  # extents are informative only
        print(f"extents: unavailable ({exc})")
    print(f"layers ({len(doc.layers)}):")
    per_layer = Counter(e.dxf.layer for e in msp)
    for layer in doc.layers:
        state = "OFF" if not layer.is_on() else ("frozen" if layer.is_frozen() else "on")
        print(f"  {layer.dxf.name:<30} {per_layer.get(layer.dxf.name, 0):>5} entities  [{state}]")
    print("entity types: " + ", ".join(f"{k}={v}" for k, v in counts.most_common()))
    blocks = [b.name for b in doc.blocks if not b.name.startswith("*")]
    print(f"blocks: {len(blocks)}  {blocks[:25]}")
    print("note: only modelspace is read; paper-space layouts and entities inside block inserts are not summarised.")


def cmd_areas(doc, a) -> None:
    from shapely.geometry import Polygon

    f, _ = require_factor(doc, a.assume_units)
    rows = defaultdict(list)
    for e, pts, has_arcs in closed_polylines(doc.modelspace(), a.layer):
        if len(pts) < 3:
            continue
        poly = Polygon(pts)
        rows[e.dxf.layer].append((poly.area * f * f, poly.length * f, poly.is_valid, e.dxf.handle, has_arcs))
    if not rows:
        print("no closed polylines found (rooms may be drawn with loose LINEs: use `arq dxf render` and read visually)")
        return
    for layer, items in rows.items():
        total = sum(i[0] for i in items)
        print(f"layer {layer}: {len(items)} closed polylines, total {total:.2f} m2")
        for area, per, valid, handle, arcs in sorted(items, key=lambda i: -i[0]):
            flags = ("" if valid else "  [SELF-INTERSECTING]") + ("  [HAS ARC SEGMENTS: straight-chord area, approximate]" if arcs else "")
            print(f"  handle {handle:<6} area {area:9.2f} m2  perimeter {per:8.2f} m{flags}")
    print("note: modelspace only; polylines inside block inserts or paper space are not counted.")


def dim_override(e) -> str | None:
    txt = e.dxf.get("text", "")
    return None if txt in ("", "<>") else txt


def cmd_dims(doc, a) -> None:
    f, _ = require_factor(doc, a.assume_units)
    n = bad = skipped = 0
    for e in doc.modelspace().query("DIMENSION"):
        n += 1
        base = e.dimtype & 7
        if base == ORDINATE_DIMTYPE:
            skipped += 1
            print(f"  handle {e.dxf.handle:<6} ordinate dimension: skipped (not a length)")
            continue
        try:
            measured = e.get_measurement()
        except Exception:
            print(f"  handle {e.dxf.handle}: measurement not computable (type {e.dimtype})")
            skipped += 1
            continue
        if not isinstance(measured, (int, float)):
            skipped += 1
            continue
        over = dim_override(e)
        if base in ANGULAR_DIMTYPES:
            print(f"  handle {e.dxf.handle:<6} layer {e.dxf.layer:<16} angular {measured:8.2f} deg"
                  + (f"  [override '{over}']" if over else ""))
            continue
        measured_m = measured * f
        flag = ""
        if over:
            m = NUMBER.search(over)
            if m:
                shown = float(m.group().replace(",", "."))
                candidates = (measured_m, measured_m * 100, measured_m * 1000, measured)
                if min(abs(shown - c) / max(c, 1e-9) for c in candidates) > DIM_MISMATCH_TOLERANCE:
                    flag = f"  [OVERRIDE '{over}' != measured]"
                    bad += 1
        print(f"  handle {e.dxf.handle:<6} layer {e.dxf.layer:<16} measured {measured_m:8.3f} m{flag}")
    print(f"{n} dimensions, {bad} with suspicious overridden text, {skipped} skipped")


def cmd_text(doc, a) -> None:
    f, _ = require_factor(doc, a.assume_units)
    for e in doc.modelspace().query("TEXT MTEXT"):
        if a.layer and e.dxf.layer != a.layer:
            continue
        txt = e.dxf.text if e.dxftype() == "TEXT" else e.plain_text()
        p = e.dxf.insert
        print(f"({p.x * f:.2f},{p.y * f:.2f}) m [{e.dxf.layer}] {txt.strip()!r}")


def cmd_blocks(doc, _a) -> None:
    c = Counter(e.dxf.name for e in doc.modelspace().query("INSERT"))
    for name, n in c.most_common():
        print(f"{n:>4}  {name}")
    if not c:
        print("no block inserts in modelspace")


def cmd_render(doc, a) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace(), finalize=True)
    fig.savefig(a.out, dpi=a.dpi)
    print(f"rendered {a.out}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq dxf", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assume-units", choices=sorted(ASSUMED), help="only for drawings without $INSUNITS")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("summary", "areas", "dims", "text", "blocks", "render"):
        sp = sub.add_parser(name)
        sp.add_argument("--assume-units", choices=sorted(ASSUMED), default=argparse.SUPPRESS)
        sp.add_argument("file")
        if name in ("areas", "text"):
            sp.add_argument("--layer")
        if name == "render":
            sp.add_argument("out")
            sp.add_argument("--dpi", type=int, default=150)
    a = ap.parse_args(argv)
    doc = load(a.file)
    {"summary": cmd_summary, "areas": cmd_areas, "dims": cmd_dims, "text": cmd_text,
     "blocks": cmd_blocks, "render": cmd_render}[a.cmd](doc, a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
