"""Test offline templates/trang-duyet.html và scripts/kiem_trang_duyet.mjs bằng DOM giả (cần node).
Chạy: python3 -B tests/test_template.py
Ca hỏng thật:
- 17/10: phần r3 thêm sau không nằm trong ORDER viết cứng, nút E không chạy (find() duyệt ORDER).
- 18/10: reviews.limit(1000) khi đã có hơn 1000 kết quả: bộ đếm thiếu thẻ.
- Status 'applied' không có trong bộ đếm, thẻ đã áp biến mất khỏi số đếm.
- 18/10: hai trường cùng key trong một thẻ lưu đè values.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATE = SKILL / "templates" / "trang-duyet.html"
CHECK = SKILL / "scripts" / "kiem_trang_duyet.mjs"
DRIVER = HERE / "template_driver.mjs"


def card(i, fields=None):
    return {"id": i, "post_id": 1, "url": "https://example.vn/" + i + "/", "label": i,
            "fields": fields or [{"key": "seo_title", "name": "SEO title", "max": 65, "before": "Cũ " + i, "A": "Mới " + i, "B": "Cũ " + i}]}


def write_export(d, sections, statuses, summary=True):
    """sections: {tên: [mã thẻ]}. statuses: {mã thẻ: status}."""
    (d / "report").mkdir()
    (d / "reviews").mkdir()
    for name, ids in sections.items():
        (d / "report" / (name + ".json")).write_text(json.dumps({"intro": "x", "items": [card(i) for i in ids]}), encoding="utf-8")
    if summary:
        (d / "report" / "summary.json").write_text(json.dumps({"sections": [{"key": k, "title": k, "state": "ready"} for k in list(sections)[:1]]}), encoding="utf-8")
    for i, s in statuses.items():
        (d / "reviews" / (i + ".json")).write_text(json.dumps({"item_id": i, "status": s, "values": {}, "updatedAt": "2026-10-17T00:00:00Z"}), encoding="utf-8")


def run_check(d):
    p = subprocess.run(["node", str(CHECK), str(TEMPLATE), str(d), "--json"], capture_output=True, text=True, timeout=60)
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("{") else p.stdout), p.stderr


class TemplateCounts(unittest.TestCase):
    def test_hon_1000_ket_qua_va_applied_va_phan_ngoai_order(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            meta = ["m%04d" % i for i in range(1000)]
            extra = ["s%04d" % i for i in range(303)]  # phần scn-a1 không có trong ORDER và không có trong summary
            st = {}
            cyc = ["approved", "edited", "applied", "rejected"]
            for n, i in enumerate(meta + extra):
                st[i] = cyc[n % 4]
            for i in meta[:50]:
                del st[i]  # 50 thẻ còn chờ duyệt
            write_export(d, {"meta": meta, "scn-a1": extra}, st)
            rc, r, err = run_check(d)
            self.assertEqual(rc, 0, (r, err))
            self.assertEqual(r["page"]["total"], 1303)
            self.assertGreater(r["page"]["applied"], 0)
            self.assertEqual(r["diffs"], [])
            self.assertEqual(r["reviews_in_copy"], 1253)
            self.assertTrue(any(q["lim"] == 1000 and q["filters"] >= 1 for q in r["queries"]), r["queries"])  # chia khoảng, không còn một truy vấn limit(1000)
            self.assertEqual(len([q for q in r["queries"] if q["name"] == "reviews"]), 3)

    def test_lech_thi_exit_1(self):
        """Kiểm chứng bộ kiểm có bắt lệch: bản sao có status lạ mà trang đếm khác."""
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            write_export(d, {"meta": ["a1", "a2"]}, {"a1": "approved"})
            p = subprocess.run(["node", str(CHECK), str(TEMPLATE), str(d)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout)
        p = subprocess.run(["node", str(CHECK), str(TEMPLATE), "/khong/co"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        p = subprocess.run(["node", str(CHECK), "--help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)

    def test_nut_duyet_chay_o_phan_ngoai_order_va_khoa_truong_trung(self):
        r = subprocess.run(["node", str(DRIVER), str(TEMPLATE)], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
