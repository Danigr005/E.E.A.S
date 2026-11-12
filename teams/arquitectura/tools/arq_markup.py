"""arq markup: draw review findings on a plan image (overview or tile PNG).

Usage:
  arq markup <image.png> <findings.json> <out.png>
findings.json: [{"id": "H1", "severity": "critico|alto|medio|bajo|info", "label": "short text",
                 "bbox": [x0, y0, x1, y1]}]   (pixels of the given image)
Colours: critico=red, alto=orange, medio=yellow, bajo=blue, info=grey. A legend is added at the top-left.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

COLORS = {"critico": (214, 39, 40), "alto": (255, 127, 14), "medio": (230, 190, 20),
          "bajo": (31, 119, 180), "info": (127, 127, 127)}
LINE_WIDTH = 4
REQUIRED = ("id", "severity", "bbox")


def validate(items) -> None:
    if not isinstance(items, list):
        raise SystemExit("arq markup: findings.json must be a list of objects")
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise SystemExit(f"arq markup: finding #{i} must be an object")
        missing = [k for k in REQUIRED if k not in it]
        if missing:
            raise SystemExit(f"arq markup: finding #{i} lacks {missing}")
        if it["severity"] not in COLORS:
            raise SystemExit(f"arq markup: finding {it['id']}: severity must be one of {sorted(COLORS)}")
        box = it["bbox"]
        if not isinstance(box, list) or len(box) != 4 or not all(isinstance(v, (int, float)) for v in box):
            raise SystemExit(f"arq markup: finding {it['id']}: bbox needs 4 numbers [x0,y0,x1,y1]")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    src, findings_path, out = argv
    if os.path.exists(out) and os.path.samefile(src, out):
        raise SystemExit("arq markup: output must differ from the input image (never overwrite the plan)")
    try:
        with open(findings_path, encoding="utf-8") as fh:
            items = json.load(fh)
        img = Image.open(src).convert("RGB")
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"arq markup: {exc}") from exc
    validate(items)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=max(14, img.width // 90))
    for it in items:
        bx0, by0, bx1, by1 = it["bbox"]
        x0, x1 = sorted((bx0, bx1))
        y0, y1 = sorted((by0, by1))
        color = COLORS[it["severity"]]
        draw.rectangle([x0, y0, x1, y1], outline=color, width=LINE_WIDTH)
        tag = f"{it['id']} {it.get('label', '')}".strip()
        tw = draw.textlength(tag, font=font)
        ty = max(0, y0 - font.size - 6)
        draw.rectangle([x0, ty, x0 + tw + 8, ty + font.size + 6], fill=color)
        draw.text((x0 + 4, ty + 2), tag, fill=(255, 255, 255), font=font)
    y = 8
    for sev, color in COLORS.items():
        draw.rectangle([8, y, 8 + 18, y + 18], fill=color)
        draw.text((32, y), sev, fill=(0, 0, 0), font=font)
        y += font.size + 8
    img.save(out)
    print(f"{len(items)} findings drawn on {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
