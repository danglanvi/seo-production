"""Test measure_ref.mjs offline. Chạy: python3 -B tests/test_measure_ref.py

Cần node 22 trở lên. Ca đo trang và ca chụp cần Chrome; thiếu Chrome thì bỏ qua 2 ca đó và báo.
Trang mẫu tests/fixtures/ref_blog.html: cột chữ 680px, chữ 18px/1.7, mục lục nav.toc dính top 24px,
trang chặn scrollTo như thư viện cuộn mượt, dưới 800px có nút "Mục lục" và thanh CTA dính đáy.
Test chặn mọi request http và https, nên không gọi mạng.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "measure_ref.mjs"
FIXTURE = ROOT / "tests" / "fixtures" / "ref_blog.html"
CHROME = os.environ.get("CHROME_BIN") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HAS_CHROME = Path(CHROME).exists() or bool(shutil.which("google-chrome") or shutil.which("chromium"))

CSS = """/* latin */
@font-face { font-family: 'Roboto'; src: url(a.woff2); unicode-range: U+0000-00FF; }
/* vietnamese */
@font-face { font-family: 'Roboto'; src: url(b.woff2); unicode-range: U+0102-0103; }
/* latin */
@font-face { font-family: 'Fake Sans'; src: url(c.woff2); unicode-range: U+0000-00FF; }
"""


def node(*argv, timeout=120):
    p = subprocess.run(["node", str(SCRIPT), *argv], capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def ref_json(d):
    f = Path(d, "ref.json")
    f.write_text(json.dumps({"url": "https://vi-du.test/bai/", "widths": [
        {"width": 1440, "col": {"width": 680, "font": {"size": 18, "lh_ratio": 1.7}}, "h2": {"size": 28}},
        {"width": 390, "col": None}]}), encoding="utf-8")
    return f


def test_vi_subset_offline():
    with tempfile.TemporaryDirectory() as d:
        css = Path(d, "fonts.css")
        css.write_text(CSS, encoding="utf-8")
        rc, out = node("vi-subset", "Roboto,Fake Sans,Khong Co", "--css", str(css))
        assert rc == 1, out
        assert "Roboto\tcó vietnamese" in out
        assert "Fake Sans\tTHIẾU vietnamese" in out
        assert "Khong Co\tKHÔNG THẤY font" in out
        assert node("vi-subset", "Roboto", "--css", str(css))[0] == 0
        assert node("vi-subset", "--css", str(css))[0] == 2


def test_fonts_sheet():
    with tempfile.TemporaryDirectory() as d:
        ref, out = ref_json(d), Path(d, "so.html")
        rc, msg = node("fonts", "--ref", str(ref), "--fonts", "Georgia,Arial,Verdana", "--out", str(out), "--no-google")
        assert rc == 0, msg
        html = out.read_text(encoding="utf-8")
        assert html.count('<section class="b"') == 3
        assert "width:680px" in html and "font-size:18px" in html and "line-height:1.7" in html
        assert "googleapis" not in html
        node("fonts", "--ref", str(ref), "--fonts", "Be Vietnam Pro", "--out", str(out))
        assert "family=Be+Vietnam+Pro:wght@400;700" in out.read_text(encoding="utf-8")
        assert node("fonts", "--ref", str(ref), "--fonts", "A,B,C,D,E,F,G", "--out", str(out))[0] == 2  # quá 6 font
        assert node("fonts", "--ref", str(ref), "--fonts", "A", "--out", str(out), "--width", "390")[0] == 2  # không có cột chữ


def test_measure_fixture():
    if not HAS_CHROME:
        print("BỎ QUA test_measure_fixture: không có Chrome")
        return
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "ref.json")
        rc, msg = node("measure", FIXTURE.as_uri(), "--widths", "1440,390", "--scroll", "4", "--wait", "300",
                       "--block", "http://*,https://*", "--out", str(out))
        assert rc == 0, msg
        desk, mob = json.loads(out.read_text(encoding="utf-8"))["widths"]
        assert desk["col"]["width"] == 680 and desk["col"]["font"]["size"] == 18 and desk["col"]["font"]["lh_ratio"] == 1.7
        assert desk["col"]["font"]["family"].startswith("Georgia")
        assert desk["h1"]["size"] == 40 and desk["h2"]["size"] == 28
        t = desk["toc"]
        assert t["box"] == "nav#toc.toc" and t["markup"] == "nav.toc > ol > li > a" and t["links"] == 4 and t["depth"] == 1
        assert t["position"] == "sticky"
        # trang chặn scrollTo: chỉ wheel mới cuộn được
        assert desk["sau_cuon"]["scrollY"] > 1000 and desk["sau_cuon"]["toc_top"] == 24
        assert mob["toc"]["visible"] is False and '"Mục lục"' in mob["toc"]["toggle"]
        assert mob["sau_cuon"]["toc_top"] is None
        cta = [x for x in mob["sau_cuon"]["dinh"] if x["sel"] == "a.cta-bar"]
        assert cta and cta[0]["bottom"] == 0 and cta[0]["text"] == "Đăng ký tư vấn"
        assert not [x for x in desk["sau_cuon"]["dinh"] if x["sel"] == "a.cta-bar"]
        assert node("measure")[0] == 2


def test_fonts_shot():
    if not HAS_CHROME:
        print("BỎ QUA test_fonts_shot: không có Chrome")
        return
    with tempfile.TemporaryDirectory() as d:
        ref, out, png = ref_json(d), Path(d, "so.html"), Path(d, "so.png")
        rc, msg = node("fonts", "--ref", str(ref), "--fonts", "Georgia,Arial", "--out", str(out), "--no-google", "--shot", str(png))
        assert rc == 0, msg
        assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


if __name__ == "__main__":
    test_vi_subset_offline()
    test_fonts_sheet()
    test_measure_fixture()
    test_fonts_shot()
    print("OK 4 test")
