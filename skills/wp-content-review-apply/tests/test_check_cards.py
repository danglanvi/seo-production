"""Test offline scripts/check_cards.py (lint builder thẻ).
Chạy: python3 -B tests/test_check_cards.py
Ca hỏng thật:
- 18/10 (6cae27d5-06): 36 thẻ scn-a1/a2/a3 có hai trường cùng key, mọi ô hiện cùng một chữ.
- 17/10: thẻ A/B không có options, trang chỉ hiện A.
- Thẻ thiếu id/item_id làm trang không lưu được.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_cards.py"


def w(d, rel, obj):
    p = Path(d, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj, encoding="utf-8")


def run(*args):
    p = subprocess.run([sys.executable, "-I", str(SCRIPT)] + list(args), capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout, p.stderr


GOOD = {"id": "ok-1", "post_id": 1, "url": "https://example.vn/", "fields": [
    {"key": "seo_title", "name": "t", "before": "a", "A": "b", "B": "a"}]}
OPTS = [{"key": "A", "label": "A"}, {"key": "B", "label": "B"}]


class Lint(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)

    def tearDown(self):
        self.t.cleanup()

    def msgs(self, *extra):
        rc, out, err = run(str(self.d / "report"), "--json", *extra)
        return rc, json.loads(out) if out.strip().startswith("{") else out

    def test_sach_thi_exit_0(self):
        w(self.d, "report/meta.json", {"options": OPTS, "items": [GOOD]})
        w(self.d, "report/summary.json", {"sections": [{"key": "meta", "title": "Meta", "count": 1}]})
        rc, r = self.msgs()
        self.assertEqual(rc, 0, r)
        self.assertEqual(r["errors"], [])
        self.assertEqual(r["items"], 1)

    def test_khoa_truong_trung(self):
        bad = {"id": "scn-a1-x", "post_id": 1, "fields": [
            {"key": "text", "name": "1", "before": "a", "proposed": "b"}, {"key": "text", "name": "2", "before": "c", "proposed": "d"}]}
        ok = {"id": "scn-a1-y", "post_id": 1, "fields": [
            {"key": "text", "name": "1", "before": "a", "proposed": "b"}, {"key": "text#2", "name": "2", "before": "c", "proposed": "d"}]}
        w(self.d, "report/scn-a1.json", {"items": [bad, ok]})
        rc, r = self.msgs()
        self.assertEqual(rc, 1)
        self.assertEqual([e["where"] for e in r["errors"]], ["scn-a1/scn-a1-x"])
        self.assertIn("cùng key", r["errors"][0]["msg"])

    def test_thieu_id_trung_id_thieu_before_key(self):
        w(self.d, "report/a.json", {"items": [{"fields": []}, dict(GOOD, options=OPTS),
                                              {"id": "ok-1", "fields": [{"key": "h1", "name": "x", "proposed": "y"}, {"name": "z", "before": "q"}]}]})
        w(self.d, "report/b.json", {"items": [dict(GOOD, options=OPTS)]})
        rc, r = self.msgs()
        text = " | ".join(e["msg"] for e in r["errors"])
        self.assertEqual(rc, 1)
        for frag in ("thiếu id", "id trùng", "thiếu before", "thiếu key"):
            self.assertIn(frag, text)

    def test_ab_khong_co_options(self):
        w(self.d, "report/meta.json", {"items": [GOOD]})
        rc, r = self.msgs()
        self.assertEqual(rc, 1)
        self.assertIn("trang chỉ hiện A", r["errors"][0]["msg"])
        w(self.d, "report/meta.json", {"items": [dict(GOOD, options=[{"key": "A"}])]})  # có options nhưng thiếu B
        rc, r = self.msgs()
        self.assertEqual(rc, 1)
        self.assertIn("phương án B", r["errors"][0]["msg"])
        w(self.d, "report/meta.json", {"options": OPTS, "items": [GOOD]})  # options ở mức phần: đạt
        self.assertEqual(self.msgs()[0], 0)

    def test_canh_bao_summary_va_post_id(self):
        it = {"id": "x", "fields": [{"key": "meta", "name": "m", "before": "a", "proposed": "b"}]}
        w(self.d, "report/meta.json", {"items": [it]})
        w(self.d, "report/r3.json", {"items": [dict(it, id="y")]})
        w(self.d, "report/summary.json", {"sections": [{"key": "meta", "count": 5}, {"key": "tech"}]})
        rc, r = self.msgs()
        self.assertEqual(rc, 0)
        text = " | ".join(x["msg"] for x in r["warnings"])
        for frag in ("count=5", 'phần "tech" không có tài liệu', 'tài liệu "r3"', "thiếu post_id"):
            self.assertIn(frag, text)

    def test_doc_qua_lon(self):
        big = dict(GOOD, id="big", note="x" * (260 * 1024))
        w(self.d, "report/meta.json", {"options": OPTS, "items": [big]})
        rc, r = self.msgs()
        self.assertEqual(rc, 1)
        self.assertIn("256 KiB", r["errors"][0]["msg"])

    def test_reviews(self):
        w(self.d, "report/meta.json", {"options": OPTS, "items": [GOOD]})
        w(self.d, "reviews/ok-1.json", {"item_id": "ok-1", "status": "approved", "values": {"seo_title": "x", "khong_co": "y"}})
        w(self.d, "reviews/thieu.json", {"status": "approved"})
        w(self.d, "reviews/la.json", {"item_id": "la", "status": "done"})
        w(self.d, "reviews/mo-coi.json", {"item_id": "mo-coi", "status": "approved"})
        rc, r = self.msgs("--reviews", str(self.d / "reviews"))
        self.assertEqual(rc, 1)
        errs = " | ".join(e["msg"] for e in r["errors"])
        warns = " | ".join(e["msg"] for e in r["warnings"])
        self.assertIn("thiếu item_id", errs)
        self.assertIn('status lạ "done"', errs)
        self.assertIn("không có trong report", warns)
        self.assertIn("khong_co", warns)

    def test_dau_vao_sai(self):
        self.assertEqual(run("/khong/co")[0], 2)
        self.assertEqual(run("--help")[0], 0)
        w(self.d, "report/hong.json", "{khong phai json")
        rc, out, _ = run(str(self.d / "report"))
        self.assertEqual(rc, 1)
        self.assertIn("không phải JSON", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
