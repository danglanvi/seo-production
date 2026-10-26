#!/usr/bin/env python3
"""Kiểm bản dựng lại có "giống hệt" bản gốc không: ảnh chụp, chữ hiển thị và mã HTTP.

  python3 parity.py shots --dir <thư mục ảnh> --a fc --b tg [--fold d1440=900,m390=844] [--tol 32] [--max-pct 3] [--max-first 1]
      ảnh đặt tên <trang>-<a>-<viewport>.png và <trang>-<b>-<viewport>.png
  python3 parity.py status --a status_a.tsv --b status_b.tsv [--ignore-query-in-redirect]
      mỗi dòng: <path>\\t<mã> [đích redirect]
  python3 parity.py text --a <thư mục .txt bản a> --b <thư mục .txt bản b>
      chữ hiển thị đã trích (mỗi trang một file cùng tên)

Ảnh: % điểm ảnh lệch trên phần cao chung của 2 ảnh, và trên màn đầu. Đạt khi 2 ảnh cao bằng nhau, cả trang ≤3%, màn đầu ≤1%. Chữ và mã HTTP: phải khớp 100%.
Exit 1 khi có mục vượt ngưỡng.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path


def pct_diff(a, b, top, bottom, tol):
    from PIL import ImageChops
    w = min(a.width, b.width)
    ca, cb = a.crop((0, top, w, bottom)), b.crop((0, top, w, bottom))
    d = ImageChops.difference(ca.convert("RGB"), cb.convert("RGB"))
    if tol:
        d = d.point(lambda v: 255 if v > tol else 0)
    m = d.convert("L").point(lambda v: 255 if v else 0)
    n = sum(m.histogram()[255:])
    return 100.0 * n / (w * (bottom - top)) if bottom > top else 0.0


def cmd_shots(a):
    from PIL import Image
    fold = dict(x.split("=") for x in a.fold.split(",")) if a.fold else {}
    rx = re.compile(rf"^(.+)-{re.escape(a.a)}-([^-]+)\.png$")
    rows, bad = [], 0
    for fa in sorted(Path(a.dir).glob(f"*-{a.a}-*.png")):
        m = rx.match(fa.name)
        if not m:
            continue
        page, vp = m.groups()
        fb = fa.with_name(f"{page}-{a.b}-{vp}.png")
        if not fb.exists():
            rows.append(f"{page}-{vp}.png\tthiếu ảnh {a.b}")
            bad += 1
            continue
        ia, ib = Image.open(fa), Image.open(fb)
        h = min(ia.height, ib.height)
        f = min(int(fold.get(vp, h)), h)
        whole, first = pct_diff(ia, ib, 0, h, a.tol), pct_diff(ia, ib, 0, f, a.tol)
        ok = ia.height == ib.height and whole <= a.max_pct and first <= a.max_first
        bad += not ok
        rows.append(f"{page}-{vp}.png\tcao {a.a}={ia.height} {a.b}={ib.height}\tlệch cả trang={whole:.2f}%\tmàn đầu={first:.2f}%\t{'đạt' if ok else 'LỆCH'}")
    print("\n".join(rows))
    return 1 if bad else 0


def read_status(p, strip_q):
    out = {}
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        dest = parts[1].split(" ", 1)[1] if " " in parts[1] else ""
        if strip_q:
            dest = dest.split("?", 1)[0]
        out[parts[0]] = (parts[1].split(" ")[0], dest.strip())
    return out


def cmd_status(a):
    sa, sb = read_status(a.a, a.ignore_query_in_redirect), read_status(a.b, a.ignore_query_in_redirect)
    diff = [k for k in sorted(set(sa) | set(sb)) if sa.get(k) != sb.get(k)]
    for k in diff:
        print(f"{k}\ta={sa.get(k)}\tb={sb.get(k)}")
    print(f"{len(set(sa) | set(sb))} URL, {len(diff)} lệch")
    return 1 if diff else 0


def norm_text(s):
    return re.sub(r"\s+", " ", s).strip()


def cmd_text(a):
    bad = 0
    for fa in sorted(Path(a.a).glob("*.txt")):
        fb = Path(a.b) / fa.name
        if not fb.exists():
            print(f"{fa.name}\tthiếu ở bản b")
            bad += 1
            continue
        ta, tb = norm_text(fa.read_text(encoding="utf-8")), norm_text(fb.read_text(encoding="utf-8"))
        if ta != tb:
            bad += 1
            wa, wb = ta.split(" "), tb.split(" ")
            ops = [o for o in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes() if o[0] != "equal"][:3]
            print(f"{fa.name}\tLỆCH\t" + " | ".join(f"{' '.join(wa[i1:i2])!r}→{' '.join(wb[j1:j2])!r}" for _, i1, i2, j1, j2 in ops))
        else:
            print(f"{fa.name}\tkhớp")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shots")
    s.add_argument("--dir", required=True)
    s.add_argument("--a", required=True)
    s.add_argument("--b", required=True)
    s.add_argument("--fold", default="")
    s.add_argument("--tol", type=int, default=32, help="lệch mỗi kênh màu lớn hơn mức này mới tính (32 tái tạo bảng 17/10)")
    s.add_argument("--max-pct", type=float, default=3.0)
    s.add_argument("--max-first", type=float, default=1.0)
    t = sub.add_parser("status")
    t.add_argument("--a", required=True)
    t.add_argument("--b", required=True)
    t.add_argument("--ignore-query-in-redirect", action="store_true")
    x = sub.add_parser("text")
    x.add_argument("--a", required=True)
    x.add_argument("--b", required=True)
    a = ap.parse_args(argv)
    return {"shots": cmd_shots, "status": cmd_status, "text": cmd_text}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
