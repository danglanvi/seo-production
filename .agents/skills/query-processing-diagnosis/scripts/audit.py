#!/usr/bin/env python3
"""Kiểm tràn bố cục của deck bằng Chrome headless qua DevTools Protocol (cdp.mjs đo vị trí thật từng phần tử).

  python3 audit.py <deck.html>            # in slide có phần tử tràn khỏi vùng nội dung 1920×1080
  python3 audit.py --json <du-an.json>    # dựng deck của dự án vào thư mục tạm rồi kiểm

Cần Node ≥22 và Chrome (đặt CHROME_PATH nếu Chrome không ở vị trí mặc định).
cdp.mjs dùng user-data-dir riêng, timeout 120 giây, xong thì kill đúng nhóm tiến trình Chrome đã mở.
Chụp ảnh từng slide: node cdp.mjs shots <deck.html> <thư mục> [n ...]
Thoát mã 1 nếu có tràn.
"""
import html, json, os, re, signal, subprocess, sys, tempfile
from pathlib import Path

def audit(path):
    try:
        r = subprocess.run(["node", str(Path(__file__).parent / "cdp.mjs"), "audit", str(path)], capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        print("audit: timeout"); return 2
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        print("audit: không đọc được kết quả", r.stderr[-300:]); return 2
    n_bad = 0
    for s in res:
        if s["bad"]:
            n_bad += 1
            print(f"slide {s['n']:>3} [{s['title']}]")
            for b in s["bad"]:
                print(f"    {b['over']:<28} {b['d'][:48]:<48} “{b['txt']}”")
        if s["clip"]:
            print(f"slide {s['n']:>3} [{s['title']}] nhãn bị cắt bằng dấu …: {s['clip']}")
    print(f"audit: {len(res)} slide, {n_bad} slide tràn")
    return 1 if n_bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == "--json":
        sys.path.insert(0, str(Path(__file__).parent))
        import qp_render
        out = Path(tempfile.mkdtemp(prefix="qpdeck_")) / (Path(a[1]).stem + ".html")
        out.write_text(qp_render.build_project(qp_render.load(a[1]), False), encoding="utf-8")
        sys.exit(audit(out))
    sys.exit(audit(a[0]))
