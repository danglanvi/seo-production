#!/usr/bin/env python3
"""Test offline cho ssim_luma.py, webp_recompress.py và alt_variants.py. Ảnh tổng hợp, máy chủ HTTP chạy ở 127.0.0.1.
Không gọi site thật. Chạy: python3 -B scripts/tests/test_image_tools.py  (cần Pillow, numpy; webp_recompress cần cwebp)
Ca thật làm nền (27/10/2026): SSIM theo loại ảnh trên 32/35 banner; hero có alpha đo 0,9737 trên nền thật và 0,9616 trên nền đen/trắng;
alt hero có hai nguồn (attachment và chuỗi cứng trong template).
"""
import json
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

S = Path(__file__).resolve().parent.parent


def run(script, *args, ok=0):
    p = subprocess.run([sys.executable, str(S / script), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == ok, (script, args, p.returncode, p.stdout[-600:], p.stderr[-600:])
    return p


def anh_chu(path, nhieu=0):
    im = Image.new("RGB", (320, 180), (240, 240, 250))
    d = ImageDraw.Draw(im)
    for i in range(6):
        d.rectangle([20 + i * 45, 30, 50 + i * 45, 150], outline=(20, 20, 90), width=2)
        d.text((24 + i * 45, 80), "LOGO", fill=(10, 10, 10))
    arr = np.asarray(im).astype(int)
    if nhieu:
        rng = np.random.default_rng(1)
        arr = np.clip(arr + rng.integers(-nhieu, nhieu + 1, arr.shape), 0, 255)
    Image.fromarray(arr.astype("uint8")).save(path)


def anh_alpha(path, luong_tu=0):
    """Chủ thể màu xanh-tím, viền mờ. luong_tu > 0 làm tròn alpha về bội số, như bản nén."""
    w = h = 200
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(xx - 100, yy - 100)
    alpha = np.clip((90 - r) * 6, 0, 255)
    if luong_tu:
        alpha = np.round(alpha / luong_tu) * luong_tu
    rgb = np.zeros((h, w, 3))
    rgb[...] = (70, 60, 200)
    Image.fromarray(np.dstack([rgb, alpha]).astype("uint8")).save(path)


def test_ssim(td):
    a, b = td / "a.png", td / "b.png"
    anh_chu(a)
    anh_chu(b, nhieu=0)
    p = run("ssim_luma.py", a, b, "--kind", "chu", "--json")
    assert json.loads(p.stdout)["do"][0]["ssim_luma"] == 1.0
    anh_chu(b, nhieu=40)
    p = run("ssim_luma.py", a, b, "--kind", "chu", ok=1)
    assert "KHONG_DAT" in p.stdout
    # --min thắng --kind; thiếu cả hai thì argparse thoát 2
    run("ssim_luma.py", a, b, "--min", "0.1")
    run("ssim_luma.py", a, b, ok=2)
    # khác kích thước thoát 2
    Image.new("RGB", (10, 10)).save(td / "nho.png")
    run("ssim_luma.py", a, td / "nho.png", "--kind", "that", ok=2)
    print("ok ssim: đạt, không đạt, --min, khác kích thước")


def test_alpha_nen_that(td):
    a, b = td / "ga.png", td / "gb.png"
    anh_alpha(a)
    anh_alpha(b, luong_tu=64)
    run("ssim_luma.py", a, b, "--kind", "that", ok=2)  # thiếu --bg: từ chối
    p = run("ssim_luma.py", a, b, "--min", "0.0", "--bg", "#4637c8", "--bg", "#000000", "--bg", "#ffffff", "--json")
    d = {r["bg"]: r["ssim_luma"] for r in json.loads(p.stdout)["do"]}
    # nền trùng màu chủ thể che hết lỗi alpha; nền tương phản lộ lỗi: số đo phụ thuộc nền
    assert d["#4637c8"] > d["#000000"] and d["#4637c8"] > d["#ffffff"], d
    print("ok alpha: số đo theo nền", d)


def test_recompress(td):
    if not shutil.which("cwebp"):
        print("BỎ QUA recompress: máy không có cwebp")
        return
    src = td / "goc.png"
    anh_chu(src, nhieu=6)
    out = td / "moi.webp"
    p = run("webp_recompress.py", "--src", src, "--kind", "chu", "--out", out, "--target-kb", "1")
    r = json.loads(p.stdout)
    assert r["action"] in ("new-file", "keep-ssim", "keep-saving"), r
    if r["action"] == "new-file":
        assert out.exists() and r["ssim_luma"] >= 0.98 and r["bytes"] < r["ref_bytes"] * 0.92, r
    else:
        assert not out.exists()
    # ảnh mượt + --ref chất lượng cao: bản mới phải đạt SSIM và nhỏ hơn ref ít nhất 8%, rồi được ghi
    yy, xx = np.mgrid[0:240, 0:320]
    muot = td / "muot.png"
    Image.fromarray(np.dstack([xx * 0.8, yy * 1.0, (xx + yy) * 0.4]).astype("uint8")).save(muot)
    ref_cao = td / "ref_cao.webp"
    Image.open(muot).save(ref_cao, "WEBP", quality=99, method=6)
    out_m = td / "muot_moi.webp"
    r4 = json.loads(run("webp_recompress.py", "--src", muot, "--ref", ref_cao, "--kind", "that", "--out", out_m, "--target-kb", "0.5").stdout)
    assert r4["action"] == "recompress" and out_m.exists() and r4["ssim_luma"] >= 0.97 and r4["bytes"] <= r4["ref_bytes"] * 0.92, r4
    # --ref nhỏ hơn target: bỏ qua, không ghi
    ref = td / "ref.webp"
    Image.open(src).save(ref, "WEBP", quality=60)
    out2 = td / "moi2.webp"
    r2 = json.loads(run("webp_recompress.py", "--src", src, "--ref", ref, "--kind", "that", "--out", out2, "--target-kb", "500").stdout)
    assert r2["action"] == "skip-nho" and not out2.exists(), r2
    # không ghi đè
    out.write_bytes(b"x")
    run("webp_recompress.py", "--src", src, "--kind", "chu", "--out", out, ok=2)
    # ngưỡng chu (0,98) chặn q thấp: nén nặng quá không được ghi
    nang = td / "nang.png"
    anh_chu(nang, nhieu=60)
    r3 = json.loads(run("webp_recompress.py", "--src", nang, "--kind", "chu", "--out", td / "n3.webp", "--q-start", "20", "--q-min", "10").stdout)
    assert r3["action"] in ("keep-ssim", "keep-saving"), r3
    print("ok recompress:", r["action"], r2["action"], r3["action"], r4["action"], r4["bytes"], "/", r4["ref_bytes"])


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        ua = self.headers.get("User-Agent", "")
        alt = "Alt cũ" if "Mobile" in ua and "Googlebot" not in ua else "Alt đúng"
        if self.path == "/khong-anh":
            html = "<html><body><p>Không có ảnh</p></body></html>"
        elif self.path == "/jsonld-cu":
            html = f'<html><img src="/u/hero-446.webp" alt="Alt đúng"><script type="application/ld+json">{{"name":"Alt cũ"}}</script></html>'
        else:
            html = f'<html><img src="/u/hero-446.webp" srcset="/u/hero-446.webp 446w" alt="{alt}"><img src="/u/khac.webp" alt="x"></html>'
        b = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


def test_alt():
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"
    try:
        # UA mobile in alt cũ (chuỗi cứng trong template): phải bắt được
        p = run("alt_variants.py", "--url", base + "/trang", "--match", "hero-446", "--alt", "Alt đúng", "--old-alt", "Alt cũ", "--delay", "0", ok=1)
        assert "SAI\tmobile" in p.stdout and "DAT\tdesktop" in p.stdout and "DAT\tgooglebot" in p.stdout and "dat=2/3" in p.stdout, p.stdout
        # chỉ desktop và googlebot: đạt
        run("alt_variants.py", "--url", base + "/trang", "--match", "hero-446", "--alt", "Alt đúng", "--ua", "desktop", "--ua", "googlebot", "--delay", "0")
        # không thấy ảnh: sai
        p = run("alt_variants.py", "--url", base + "/khong-anh", "--match", "hero-446", "--alt", "Alt đúng", "--delay", "0", ok=1)
        assert "khong_thay_anh" in p.stdout
        # alt cũ nằm trong JSON-LD: sai dù thẻ img đúng
        p = run("alt_variants.py", "--url", base + "/jsonld-cu", "--match", "hero-446", "--alt", "Alt đúng", "--old-alt", "Alt cũ", "--ua", "desktop", "--delay", "0", ok=1)
        assert "con_alt_cu" in p.stdout
    finally:
        srv.shutdown()
    # lỗi mạng thoát 2
    run("alt_variants.py", "--url", "http://127.0.0.1:9/x", "--match", "a", "--alt", "b", "--ua", "desktop", "--timeout", "2", ok=2)
    print("ok alt_variants: mobile in alt cũ bị bắt, không ảnh, JSON-LD, lỗi mạng")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        test_ssim(td)
        test_alpha_nen_that(td)
        test_recompress(td)
    test_alt()
    print("TẤT CẢ ĐẠT")
