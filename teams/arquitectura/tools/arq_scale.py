"""arq scale: calibrate pixel measurements to real-world metres.

Usage:
  arq scale from-scale --scale 100 --dpi 200          # drawing at 1:100 rendered at 200 dpi
  arq scale from-ref --px 812 --meters 4.50           # a dimension you can read on the plan
  arq scale check --scale 100 --dpi 200 --px 812 --meters 4.50   # does the stated scale match a printed dimension?
  arq scale measure --px-per-m 36.2 --p1 100,200 --p2 900,200    # distance between two pixel points
  arq scale area --px-per-m 36.2 --poly "0,0;400,0;400,300;0,300"  # polygon area in m2
Always cross-check a stated scale against at least one printed dimension: PDFs are often rescaled when printed.
"""
from __future__ import annotations

import argparse
import math
import sys

INCH_M = 0.0254
TOLERANCE = 0.03  # 3 % between stated scale and a printed dimension


def px_per_m_from_scale(scale: float, dpi: float) -> float:
    return dpi / INCH_M / scale


def parse_pt(text: str) -> tuple[float, float]:
    try:
        x, y = text.split(",")
        return float(x), float(y)
    except ValueError as exc:
        raise SystemExit(f"arq scale: bad point '{text}', expected x,y") from exc


def polygon_area(points: list[tuple[float, float]]) -> float:
    s = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        s += x0 * y1 - x1 * y0
    return abs(s) / 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq scale", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["from-scale", "from-ref", "check", "measure", "area"])
    ap.add_argument("--scale", type=float, help="denominator, e.g. 100 for 1:100")
    ap.add_argument("--dpi", type=float, default=200)
    ap.add_argument("--px", type=float)
    ap.add_argument("--meters", type=float)
    ap.add_argument("--px-per-m", type=float)
    ap.add_argument("--p1")
    ap.add_argument("--p2")
    ap.add_argument("--poly")
    a = ap.parse_args(argv)

    if a.mode == "from-scale":
        if not a.scale:
            raise SystemExit("arq scale: --scale required")
        ppm = px_per_m_from_scale(a.scale, a.dpi)
        print(f"px_per_m = {ppm:.3f}  (1 px = {1000 / ppm:.2f} mm real)")
    elif a.mode == "from-ref":
        if not (a.px and a.meters):
            raise SystemExit("arq scale: --px and --meters required")
        ppm = a.px / a.meters
        print(f"px_per_m = {ppm:.3f}")
        print(f"implied scale at {a.dpi:.0f} dpi = 1:{a.dpi / INCH_M / ppm:.1f}")
    elif a.mode == "check":
        if not (a.scale and a.px and a.meters):
            raise SystemExit("arq scale: --scale, --px and --meters required")
        expected = px_per_m_from_scale(a.scale, a.dpi)
        measured = a.px / a.meters
        diff = (measured - expected) / expected
        verdict = "OK" if abs(diff) <= TOLERANCE else "MISMATCH"
        print(f"stated 1:{a.scale:g} -> {expected:.3f} px/m; printed dimension -> {measured:.3f} px/m; "
              f"difference {diff * 100:+.1f}% [{verdict}]")
        if verdict == "MISMATCH":
            print(f"implied real scale 1:{a.dpi / INCH_M / measured:.1f}. Trust the printed dimension, flag the scale as unreliable.")
            return 1
    elif a.mode == "measure":
        if not (a.px_per_m and a.p1 and a.p2):
            raise SystemExit("arq scale: --px-per-m, --p1, --p2 required")
        (x0, y0), (x1, y1) = parse_pt(a.p1), parse_pt(a.p2)
        d = math.hypot(x1 - x0, y1 - y0)
        print(f"{d:.1f} px = {d / a.px_per_m:.3f} m")
    else:
        if not (a.px_per_m and a.poly):
            raise SystemExit("arq scale: --px-per-m and --poly required")
        pts = [parse_pt(p) for p in a.poly.split(";")]
        if len(pts) < 3:
            raise SystemExit("arq scale: polygon needs at least 3 points")
        print(f"area = {polygon_area(pts) / a.px_per_m ** 2:.3f} m2")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
