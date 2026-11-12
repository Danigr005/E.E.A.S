"""arq ingest: turn a PDF or image plan into inspectable pieces.

Usage:
  arq ingest <file.pdf|png|jpg|tif> --out DIR [--dpi 200] [--tile 1800] [--overlap 150]
             [--pages 1,3] [--ocr] [--lang spa+eng]

For each page NN it writes into DIR:
  pNN_overview.png        whole sheet, long side <= 2000 px (orientation, layout, title block)
  pNN_tiles/rRR_cCC.png   overlapping full-resolution tiles (read dimensions, labels, symbols)
  pNN_words.json          text words with pixel bboxes (vector text for PDFs, OCR with --ocr)
  pNN_vectors.json        PDF only: line/rect/curve counts and the longest line segments (px)
  pNN_meta.json           page size (mm), dpi, pixel size, tile grid with origins (px)
Pixel coordinates in every JSON refer to the full-resolution page at the stated dpi.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 500_000_000
OVERVIEW_LONG_SIDE = 2000
TOP_LINES = 60
MIN_TILE = 256
MAX_PIXELS = 250_000_000  # refuse to render a page larger than this
MM_PER_INCH = 25.4


def parse_pages(spec: str | None, total: int) -> list[int]:
    if not spec:
        return list(range(total))
    pages = sorted({int(p) - 1 for p in spec.split(",") if p.strip()})
    bad = [p + 1 for p in pages if p < 0 or p >= total]
    if bad:
        raise SystemExit(f"arq ingest: page(s) {bad} out of range (document has {total})")
    return pages


def make_tiles(img: Image.Image, out: Path, tile: int, overlap: int) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    step = max(tile - overlap, 1)
    tiles = []
    rows = max(1, -(-(img.height - overlap) // step))
    cols = max(1, -(-(img.width - overlap) // step))
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * step, r * step
            x1, y1 = min(x0 + tile, img.width), min(y0 + tile, img.height)
            name = f"r{r:02d}_c{c:02d}.png"
            img.crop((x0, y0, x1, y1)).save(out / name)
            tiles.append({"file": f"{out.name}/{name}", "x0": x0, "y0": y0, "x1": x1, "y1": y1})
    return tiles


def ocr_words(img: Image.Image, lang: str) -> list[dict]:
    import pytesseract

    try:
        data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError:
        print("warning: tesseract not installed; no OCR text. Read dimensions visually from the tiles.", file=sys.stderr)
        return []
    except pytesseract.TesseractError as exc:
        raise SystemExit(f"arq ingest: OCR failed ({exc}). Try --lang eng") from exc
    words = []
    for i, text in enumerate(data["text"]):
        if text.strip() and float(data["conf"][i]) >= 30:
            words.append({"text": text, "x0": data["left"][i], "y0": data["top"][i],
                          "x1": data["left"][i] + data["width"][i], "y1": data["top"][i] + data["height"][i],
                          "conf": float(data["conf"][i])})
    return words


def pdf_words_and_vectors(pdf_path: Path, index: int, scale: float) -> tuple[list[dict], dict]:
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[index]
        words = [{"text": w["text"], "x0": round(w["x0"] * scale, 1), "y0": round(w["top"] * scale, 1),
                  "x1": round(w["x1"] * scale, 1), "y1": round(w["bottom"] * scale, 1)}
                 for w in page.extract_words(keep_blank_chars=False, use_text_flow=False)]
        segs = []
        for ln in page.lines:
            length = ((ln["x1"] - ln["x0"]) ** 2 + (ln["bottom"] - ln["top"]) ** 2) ** 0.5
            segs.append({"x0": round(ln["x0"] * scale, 1), "y0": round(ln["top"] * scale, 1),
                         "x1": round(ln["x1"] * scale, 1), "y1": round(ln["bottom"] * scale, 1),
                         "len_px": round(length * scale, 1), "width_pt": round(ln.get("linewidth") or 0, 2)})
        segs.sort(key=lambda s: -s["len_px"])
        vectors = {"lines": len(page.lines), "rects": len(page.rects), "curves": len(page.curves),
                   "images": len(page.images), "longest_lines": segs[:TOP_LINES]}
    return words, vectors


def load_image(src: Path, args) -> Image.Image:
    """Open an image flattened on white (transparent plans would turn black), upright, with its own dpi if declared."""
    try:
        raw = ImageOps.exif_transpose(Image.open(src))
    except OSError as exc:
        raise SystemExit(f"arq ingest: cannot open image {src}: {exc}") from exc
    declared = raw.info.get("dpi")
    if declared and declared[0] and not args.dpi_explicit:
        args.dpi = int(round(float(declared[0])))
        print(f"note: using the image's own resolution, {args.dpi} dpi")
    elif not args.dpi_explicit:
        print(f"warning: image declares no dpi; assuming {args.dpi}. Sheet size in mm is NOT reliable: calibrate with a printed dimension.",
              file=sys.stderr)
    if raw.mode in ("RGBA", "LA") or (raw.mode == "P" and "transparency" in raw.info):
        rgba = raw.convert("RGBA")
        flat = Image.new("RGB", rgba.size, "white")
        flat.paste(rgba, mask=rgba.split()[3])
        return flat
    return raw.convert("RGB")


def process_page(args, index: int, img: Image.Image, width_pt: float, height_pt: float,
                 pdf_path: Path | None, out: Path) -> dict:
    tag = f"p{index + 1:02d}"
    scale = args.dpi / 72.0
    long_side = max(img.size)
    ov = img.copy()
    if long_side > OVERVIEW_LONG_SIDE:
        ratio = OVERVIEW_LONG_SIDE / long_side
        ov = ov.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)
    ov.save(out / f"{tag}_overview.png")
    tiles = make_tiles(img, out / f"{tag}_tiles", args.tile, args.overlap)

    words: list[dict] = []
    vectors: dict | None = None
    source = "none"
    if pdf_path is not None:
        words, vectors = pdf_words_and_vectors(pdf_path, index, scale)
        source = "pdf-vector-text"
        (out / f"{tag}_vectors.json").write_text(json.dumps(vectors, indent=1))
    if args.ocr or not words:
        # Images, scans and PDFs whose text was converted to outlines carry no text layer: OCR the raster.
        words = ocr_words(img, args.lang)
        source = "ocr"
    (out / f"{tag}_words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))

    meta = {"page": index + 1, "dpi": args.dpi, "px_size": [img.width, img.height],
            "mm_size": [round(width_pt / 72 * MM_PER_INCH, 1), round(height_pt / 72 * MM_PER_INCH, 1)],
            "words": len(words), "words_source": source,
            "vector_lines": vectors["lines"] if vectors else None, "tile": args.tile, "overlap": args.overlap,
            "tiles": tiles}
    (out / f"{tag}_meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="arq ingest", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=None, help="render/assumed resolution (default 200)")
    ap.add_argument("--tile", type=int, default=1800)
    ap.add_argument("--overlap", type=int, default=150)
    ap.add_argument("--pages")
    ap.add_argument("--ocr", action="store_true", help="OCR the page (default for images)")
    ap.add_argument("--lang", default="eng", help="tesseract languages, e.g. spa+eng if installed")
    args = ap.parse_args(argv)
    args.dpi_explicit = args.dpi is not None
    args.dpi = args.dpi or 200
    if args.tile < MIN_TILE or not 0 <= args.overlap < args.tile:
        raise SystemExit(f"arq ingest: need --tile >= {MIN_TILE} and 0 <= --overlap < --tile")
    if not 30 <= args.dpi <= 1200:
        raise SystemExit("arq ingest: --dpi must be between 30 and 1200")

    src = Path(args.file)
    if not src.is_file():
        raise SystemExit(f"arq ingest: file not found: {src}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = []

    if src.suffix.lower() == ".pdf":
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(src))
        for index in parse_pages(args.pages, len(doc)):
            page = doc[index]
            w_pt, h_pt = page.get_size()
            px = (w_pt * args.dpi / 72) * (h_pt * args.dpi / 72)
            if px > MAX_PIXELS:
                raise SystemExit(f"arq ingest: page {index + 1} would be {px / 1e6:.0f} Mpx at {args.dpi} dpi "
                                 f"(limit {MAX_PIXELS // 1_000_000}); lower --dpi (A0 sheets: 100-150)")
            img = page.render(scale=args.dpi / 72.0).to_pil().convert("RGB")
            summary.append(process_page(args, index, img, w_pt, h_pt, src, out))
    else:
        img = load_image(src, args)
        w_pt, h_pt = img.width / args.dpi * 72, img.height / args.dpi * 72
        summary.append(process_page(args, 0, img, w_pt, h_pt, None, out))

    for m in summary:
        print(f"page {m['page']}: {m['px_size'][0]}x{m['px_size'][1]} px @ {m['dpi']} dpi "
              f"({m['mm_size'][0]}x{m['mm_size'][1]} mm), {len(m['tiles'])} tiles, "
              f"{m['words']} words [{m['words_source']}], vector lines: {m['vector_lines']}")
    print(f"output: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
