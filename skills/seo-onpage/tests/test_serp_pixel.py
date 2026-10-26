#!/usr/bin/env python3
"""Test offline cho serp_pixel.py: không cần mạng, không cần model. Chạy: python3 skills/seo-onpage/tests/test_serp_pixel.py"""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "serp_pixel.py"
spec = importlib.util.spec_from_file_location("serp_pixel", SCRIPT)
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)

# Title thật trong SERP 18/10/2026 (references/title-pixel.md mục 3); URL trong test đã đổi thành URL giả.
CUT_REAL = "Dịch vụ GEO website là gì? Tại sao SEO lại là nền tảng của GEO phát triển?"  # Google cắt dù chỉ 681,5 px
FULL_REAL = "GEO là gì? 9 kỹ thuật tối ưu GEO giúp tăng hiển thị trên AI [2026] - GTV SEO"  # Google hiện đủ dù 688,2 px


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(r.stderr)
    return r.stdout


class TestTable(unittest.TestCase):
    def setUp(self):
        self.m = sp.Meter(20, force_table=True)

    def test_mode_and_sum(self):
        self.assertEqual(self.m.mode, "table")
        t = json.loads(sp.TABLE.read_text(encoding="utf-8"))
        want = sum(t["widths"][c] for c in "abc") * 20 / t["upm"]
        self.assertAlmostEqual(self.m.width("abc"), want, places=6)

    def test_vietnamese_same_as_base(self):
        # Arial vẽ chữ có dấu tiếng Việt cùng độ rộng với chữ gốc.
        self.assertAlmostEqual(self.m.width("ế"), self.m.width("e"), places=6)
        self.assertAlmostEqual(self.m.width("ế"), self.m.width("ế"), places=6)  # NFD -> NFC

    def test_char_outside_table_uses_base(self):
        self.assertAlmostEqual(self.m.width("ṡ"), self.m.width("s"), places=6)

    def test_cut_word_boundary(self):
        text = "Dịch vụ SEO tổng thể cho doanh nghiệp vừa và lớn tại Việt Nam năm 2026 có báo cáo hàng tháng"
        shown = self.m.cut(text, 688)
        self.assertTrue(shown.endswith(" ..."))
        self.assertLessEqual(self.m.width(shown), 688)
        self.assertTrue(text.startswith(shown[:-4]))
        self.assertEqual(self.m.cut("Ngắn", 688), "Ngắn")


class TestFontAgreesWithTable(unittest.TestCase):
    def test_agree(self):
        mf = sp.Meter(20)
        if mf.mode != "font":
            self.skipTest("máy không có Pillow hoặc file Arial")
        mt = sp.Meter(20, force_table=True)
        for t in (CUT_REAL, FULL_REAL, "Báo giá SEO Website | Bảng giá Dịch vụ SEO Tổng Thể tại GTV - GTV SEO"):
            self.assertLess(abs(mf.width(t) - mt.width(t)), 1.5, t)


class TestCli(unittest.TestCase):
    def test_measure_tsv(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, "in.tsv")
            src.write_text("url\ttitle\tdescription\n/a\tNgắn\tMô tả ngắn\n/b\t" + CUT_REAL + " thêm chữ cho dài\t\n",
                           encoding="utf-8")
            out = Path(d, "out.tsv")
            run("measure", "--in", str(src), "--table", "--out", str(out))
            rows = list(csv.DictReader(out.open(encoding="utf-8"), delimiter="\t"))
            self.assertEqual([r["field"] for r in rows], ["title", "description", "title"])
            self.assertEqual(rows[0]["verdict"], "vừa")
            self.assertEqual(rows[2]["verdict"], "bị cắt")
            self.assertEqual(rows[2]["limit_px"], "688")

    def test_calibrate_reports_real_failure(self):
        m = sp.Meter(20, force_table=True)
        with tempfile.TemporaryDirectory() as d:
            short = ["Từ khóa là gì", "SEO là gì", "Dịch vụ SEO", "Báo giá SEO website", "GEO là gì",
                     "Công ty SEO uy tín", "Quy trình SEO", "Audit SEO", "Chi phí SEO", "Index là gì"]
            long_ = ["Dịch vụ SEO tổng thể cho doanh nghiệp vừa và lớn tại Việt Nam năm 2026 kèm báo cáo hàng tháng số " + str(i)
                     for i in range(12)]
            serp, full = ["url\ttitle"], ["url\tfull_title"]
            for i, t in enumerate(short * 2):
                serp.append(f"https://s{i}.vn/\t{t} {i}")
            for i, t in enumerate(long_):
                serp.append(f"https://l{i}.vn/\t{m.cut(t, 690)}")
                full.append(f"https://l{i}.vn/\t{t}")
            serp.append(f"https://a.vn/x/\t{m.cut(CUT_REAL, 600)}")  # ca hỏng thật: Google cắt sớm
            serp.append(f"https://b.vn/y/\t{FULL_REAL}")  # ca hỏng thật: Google hiện đủ
            full.append(f"https://a.vn/x/\t{CUT_REAL}")
            Path(d, "serp.tsv").write_text("\n".join(serp) + "\n", encoding="utf-8")
            Path(d, "full.tsv").write_text("\n".join(full) + "\n", encoding="utf-8")
            out = Path(d, "rep.json")
            run("calibrate", "--serp", str(Path(d, "serp.tsv")), "--full", str(Path(d, "full.tsv")), "--table",
                "--out", str(out))
            rep = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(rep["n_cut_labeled"], 13)
            loi = {e["url"] for e in rep["loi"]}
            self.assertTrue(loi and loi <= {"https://a.vn/x/", "https://b.vn/y/"}, loi)
            self.assertGreaterEqual(rep["holdout"]["accuracy"], 0.9)


if __name__ == "__main__":
    unittest.main(verbosity=1)
