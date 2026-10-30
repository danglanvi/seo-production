"""Test offline cho deep_audit.py: HTML mẫu có lỗi đã gặp ở site bán lẻ mẫu 29–30/10/2026."""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "deep_audit.py"
spec = importlib.util.spec_from_file_location("deep_audit", SCRIPT)
da = importlib.util.module_from_spec(spec)
spec.loader.exec_module(da)

LOI = """<!doctype html><html lang="vi"><body>
<header><nav><a href="#">Trang chủ</a></nav></header>
<main><h1>Vợt mẫu</h1>
<h3>Thông số</h3>
<section class="trust"><p>Cam kết chính hãng</p></section>
<form><input type="text" name="q"></form>
<button class="next"></button>
<p>Cập nhật 12/10/2026</p>
<table><tr><td>Nặng</td><td>230 g</td></tr></table>
</main></body></html>"""

DUNG = """<!doctype html><html lang="vi"><body>
<a class="skip-link" href="#main">Bỏ qua tới nội dung</a>
<header><nav aria-label="Menu chính"><a href="/">Trang chủ</a></nav></header>
<main id="main"><article><h1>Vợt mẫu</h1>
<section aria-labelledby="ts"><h2 id="ts">Thông số</h2>
<table><caption>Thông số</caption><tr><th scope="row">Nặng</th><td>230 g</td></tr></table></section>
<form><label for="q">Tìm</label><input id="q" type="text" name="q"></form>
<button type="button" aria-label="Ảnh sau"></button>
<p>Cập nhật <time datetime="2026-10-12">12/10/2026</time></p>
</article></main></body></html>"""


class DeepAudit(unittest.TestCase):
    def test_bat_loi_da_gap(self):
        r, _ = da.audit(LOI)
        self.assertGreaterEqual(r["nhay_cap"], 1)
        self.assertGreaterEqual(r["section_khong_heading"], 1)
        self.assertGreaterEqual(r["form_khong_nhan"], 1)
        self.assertGreaterEqual(r["button_khong_ten"], 1)
        self.assertGreaterEqual(r["ngay_khong_time"], 1)
        self.assertGreaterEqual(r["table_khong_th"], 1)

    def test_ban_dung_khong_bao_loi(self):
        r, _ = da.audit(DUNG)
        for k in ("nhay_cap", "section_khong_heading", "form_khong_nhan", "button_khong_ten",
                  "ngay_khong_time", "table_khong_th"):
            self.assertEqual(r[k], 0, k)

    def test_chay_dong_lenh(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "loi_d.html").write_text(LOI, encoding="utf-8")
            (t / "dung_d.html").write_text(DUNG, encoding="utf-8")
            (t / "urls.tsv").write_text("nhom\tpath\nloi\t/a/\ndung\t/b/\nthieu\t/c/\n", encoding="utf-8")
            # Không dùng -I: bs4 nằm ở user site-packages (eval E21). Thư mục script là skill, HTML chỉ vào qua tham số.
            subprocess.run([sys.executable, "-B", str(SCRIPT), str(t), str(t / "urls.tsv"),
                            str(t / "out.csv"), str(t / "ct.jsonl")], check=True, capture_output=True)
            rows = list(csv.DictReader(open(t / "out.csv", encoding="utf-8")))
            self.assertEqual([r["nhom"] for r in rows], ["loi", "dung"])
            self.assertEqual(len((t / "ct.jsonl").read_text(encoding="utf-8").splitlines()), 2)
            json.loads((t / "ct.jsonl").read_text(encoding="utf-8").splitlines()[0])


if __name__ == "__main__":
    unittest.main()
