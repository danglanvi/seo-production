#!/usr/bin/env python3
"""Test offline: footprint_count đếm comment đúng (bỏ regex literal, bỏ 'trình duyệt'); scan_html đếm heading có chữ trong span."""
import json, subprocess, sys, tempfile, shutil
from pathlib import Path
H = Path(__file__).resolve().parent; S = H.parent / "scripts"; FX = H / "fixtures" / "mau.html"
out = subprocess.run([sys.executable, "-I", str(S / "footprint_count.py"), str(FX)], capture_output=True, text=True).stdout
line = out.splitlines()[0]
kv = dict(x.split("=") for x in line.split(": ", 1)[1].split())
assert kv["inline_script"] == "1" and kv["inline_style"] == "1", line
assert kv["comment_code"] == "3", line            # 1 CSS + 1 block JS + 1 line JS; regex literal \// không tính; URL // không tính
assert kv["comment_vi"] == "3", line
assert kv["comment_quytrinh"] == "2", line         # CSS 'v8-ky-thuat … duyệt' và JS 'phiên'; 'trình duyệt' không tính
assert kv["data_no_optimize"] == "1", line
tmp = Path(tempfile.mkdtemp()); shutil.copy(FX, tmp / "d_mau.html"); o = tmp / "out"
subprocess.run([sys.executable, "-I", str(S / "scan_html.py"), str(tmp), str(o)], check=True, capture_output=True)
r = json.load(open(o / "scan_html.json"))[0]
assert r["tags"]["main"] == 1 and r["tags"]["section"] == 2, r["tags"]
assert r["sections_no_heading"] == 1, r["sections_no_heading"]   # heading trong <span> vẫn tính
assert r["headings"][0]["text"] == "Tiêu đề", r["headings"]
print("PASS test_footprint: 7 kiểm")
