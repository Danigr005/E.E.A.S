"""arq ifc: read-only inspection and IDS validation of an IFC model.

Usage:
  arq ifc summary <file.ifc>              schema, project, storeys, element counts
  arq ifc spaces <file.ifc>               spaces with level, name and area (Qto if present, else geometry)
  arq ifc openings <file.ifc>             doors and windows with width/height and host level
  arq ifc check <file.ifc> <rules.ids>    validate against an IDS file (buildingSMART) with ifctester
Lengths are converted to metres using the model's declared length unit (printed on the first line).
Never edits the model. For changes, write a copy with ifcopenshell.api in a separate script and re-check.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter

import ifcopenshell
import ifcopenshell.util.element as uel
import ifcopenshell.util.unit as uunit


def load(path: str):
    try:
        return ifcopenshell.open(path)
    except Exception as exc:
        raise SystemExit(f"arq ifc: cannot open {path}: {exc}") from exc


def length_scale(m) -> float:
    """Metres per model length unit."""
    try:
        scale = float(uunit.calculate_unit_scale(m))
    except Exception as exc:
        raise SystemExit(f"arq ifc: cannot determine the model's length unit ({exc}); refusing to print unscaled numbers") from exc
    print(f"[length unit: {scale} m per model unit; area unit: {area_scale(m)} m2 per model area unit]")
    return scale


def area_scale(m) -> float:
    """m2 per model area unit (IFC declares AREAUNIT separately from LENGTHUNIT)."""
    try:
        return float(uunit.calculate_unit_scale(m, "AREAUNIT"))
    except Exception as exc:
        raise SystemExit(f"arq ifc: cannot determine the model's area unit ({exc}); refusing to print unscaled areas") from exc


def storey_of(el) -> str:
    cont = uel.get_container(el) or uel.get_aggregate(el)
    while cont is not None and not cont.is_a("IfcBuildingStorey"):
        cont = uel.get_container(cont) or uel.get_aggregate(cont)
    return (cont.Name or "?") if cont else "?"


def space_area(sp, a_scale: float) -> float | None:
    """Area in m2: Qto values use the model's AREAUNIT; geometry from ifcopenshell is already metric."""
    for pset in uel.get_psets(sp, qtos_only=True).values():
        for key in ("NetFloorArea", "GrossFloorArea"):
            if isinstance(pset.get(key), (int, float)):
                return float(pset[key]) * a_scale
    try:
        import ifcopenshell.geom
        import ifcopenshell.util.shape as ushape

        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), sp)
        return float(ushape.get_footprint_area(shape.geometry))
    except Exception:
        return None


def cmd_summary(m, _a) -> None:
    s = length_scale(m)
    proj = m.by_type("IfcProject")
    print(f"schema: {m.schema}   project: {proj[0].Name if proj else '?'}")
    storeys = sorted(m.by_type("IfcBuildingStorey"), key=lambda st: st.Elevation or 0)
    print("storeys: " + ", ".join(f"{st.Name} ({(st.Elevation or 0) * s:.2f} m)" for st in storeys))
    counts = Counter(e.is_a() for e in m.by_type("IfcElement"))
    for name, n in counts.most_common(20):
        print(f"  {n:>5}  {name}")


def cmd_spaces(m, _a) -> None:
    length_scale(m)
    a_s = area_scale(m)
    total = 0.0
    spaces = m.by_type("IfcSpace")
    for sp in spaces:
        area = space_area(sp, a_s)
        total += area or 0
        shown = f"{area:8.2f} m2" if area is not None else "    n/a    "
        print(f"{storey_of(sp):<12} {(sp.LongName or sp.Name or '?'):<28} {shown}")
    print(f"{len(spaces)} spaces, total {total:.2f} m2")


def cmd_openings(m, _a) -> None:
    s = length_scale(m)
    for kind in ("IfcDoor", "IfcWindow"):
        for el in m.by_type(kind):
            w, h = getattr(el, "OverallWidth", None), getattr(el, "OverallHeight", None)
            wm = f"{w * s:.2f}" if isinstance(w, (int, float)) else "n/a"
            hm = f"{h * s:.2f}" if isinstance(h, (int, float)) else "n/a"
            print(f"{kind[3:]:<7} {storey_of(el):<12} {(el.Name or '?'):<24} width {wm} m  height {hm} m")


def cmd_check(m, a) -> None:
    from ifctester import ids, reporter

    try:
        spec = ids.open(a.ids)
    except Exception as exc:
        raise SystemExit(f"arq ifc: cannot read IDS {a.ids}: {exc}") from exc
    spec.validate(m)
    reporter.Console(spec).report()
    if any(not s.status for s in spec.specifications):
        raise SystemExit(1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq ifc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("summary", "spaces", "openings", "check"):
        sp = sub.add_parser(name)
        sp.add_argument("file")
        if name == "check":
            sp.add_argument("ids")
    a = ap.parse_args(argv)
    model = load(a.file)
    {"summary": cmd_summary, "spaces": cmd_spaces, "openings": cmd_openings, "check": cmd_check}[a.cmd](model, a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
