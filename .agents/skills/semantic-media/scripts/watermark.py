#!/usr/bin/env python3
"""Ghép logo vào ảnh AI: góc dưới phải, rộng 9% ảnh, cách mép 2,5% chiều rộng, mờ 0,55. Thu về bề rộng đích (không phóng to), xuất WebP dưới max KB.
python3 watermark.py --in <ảnh gốc.png> --logo <logo.png có nền trong> --out <ảnh.webp> --width 1600 --max-kb 120"""
import argparse
from pathlib import Path

from PIL import Image


def stamp(im, logo, width_pct=0.09, margin_pct=0.025, opacity=0.55):
    w, h = im.size
    lw = round(w * width_pct)
    lg = logo.convert("RGBA").resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: round(v * opacity)))
    m = round(w * margin_pct)
    c = im.convert("RGBA")
    c.alpha_composite(lg, (w - lw - m, h - lg.height - m))
    return c.convert("RGB")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--logo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--max-kb", type=float, default=150)
    a = ap.parse_args(argv)
    im = Image.open(a.src).convert("RGB")
    if a.width and im.width > a.width:
        im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
    out = stamp(im, Image.open(a.logo))
    q = 90
    while True:
        out.save(a.out, "WEBP", quality=q, method=6)
        kb = Path(a.out).stat().st_size / 1024
        if kb <= a.max_kb or q <= 60:
            break
        q -= 5
    print(f"{a.out}: {out.width}x{out.height} {kb:.0f} KB q{q}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
