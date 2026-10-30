"""Test offline set_post_modified.php bằng WordPress giả (tests/php/run_engine.php).
Chạy: python3 -B tests/test_post_modified.py   (cần php CLI)
Ca gốc: đổi lastmod sitemap của 4 trang site agency mẫu 27/10/2026 bằng SQL có điều kiện giá trị cũ, 4/4 rows=1.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "set_post_modified.php"
RUNNER = HERE / "php" / "run_engine.php"
HEAD = "id\turl\tpost_modified_cu\tpost_modified_gmt_cu\tpost_modified_moi\tpost_modified_gmt_moi\tcan_cu\n"
OLD = ("2025-11-04 05:27:42", "2025-11-03 22:27:42")
NEW = ("2026-10-26 14:42:31", "2026-10-26 07:42:31")


def store(*rows):
    return {"posts": {str(i): {"post_modified": m, "post_modified_gmt": g} for i, m, g in rows}}


def run(st, mode, tsv_rows):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "store.json").write_text(json.dumps(st), encoding="utf-8")
        (d / "lastmod.tsv").write_text(HEAD + "".join("\t".join(r) + "\n" for r in tsv_rows), encoding="utf-8")
        e = {k: v for k, v in os.environ.items() if k not in ("MODE", "TSV")}
        if mode is not None:
            e["MODE"] = mode
        e["TSV"] = str(d / "lastmod.tsv")
        p = subprocess.run(["php", str(RUNNER), str(SCRIPT), str(d / "store.json"), str(d / "out.json")],
                           capture_output=True, text=True, env=e, timeout=60)
        after = json.loads((d / "out.json").read_text(encoding="utf-8"))
        lines = [json.loads(x) for x in p.stdout.splitlines() if x.startswith("{")]
        return p.returncode, p.stdout, lines, after


ROW = ("10", "/a/", *OLD, *NEW, "ghi chữ 14:42")


class PostModifiedTest(unittest.TestCase):
    def test_dry_khong_ghi(self):
        rc, _, lines, after = run(store((10, *OLD)), "dry", [ROW])
        self.assertEqual(rc, 0)
        self.assertEqual(lines[0]["status"], "would_update")
        self.assertEqual(after["posts"]["10"]["post_modified"], OLD[0])
        self.assertNotIn("wpdb_query:10", after["calls"])

    def test_write_chi_ghi_dong_khop_va_khong_flush(self):
        lech = ("11", "/b/", *OLD, *NEW, "x")
        rc, _, lines, after = run(store((10, *OLD), (11, "2026-01-01 00:00:00", OLD[1])), "write", [ROW, lech])
        self.assertEqual(rc, 0)
        self.assertEqual([x["status"] for x in lines], ["updated", "skip: giá trị live khác giá trị mong đợi"])
        self.assertEqual((after["posts"]["10"]["post_modified"], after["posts"]["10"]["post_modified_gmt"]), NEW)
        self.assertEqual(after["posts"]["11"]["post_modified"], "2026-01-01 00:00:00")
        self.assertIn("clean_post_cache:10", after["calls"])
        self.assertNotIn("wp_cache_flush", after["calls"])

    def test_chay_lai_va_rollback(self):
        _, _, lines, _ = run(store((10, *NEW)), "write", [ROW])
        self.assertEqual(lines[0]["status"], "skip: giá trị live khác giá trị mong đợi")
        _, _, lines, after = run(store((10, *NEW)), "rollback", [ROW])
        self.assertEqual(lines[0]["status"], "updated")
        self.assertEqual(after["posts"]["10"]["post_modified"], OLD[0])

    def test_thieu_mode_khong_chay(self):
        for mode in (None, "", "ghi"):
            rc, out, lines, after = run(store((10, *OLD)), mode, [ROW])
            self.assertEqual(rc, 2, mode)
            self.assertEqual(lines, [])
            self.assertEqual(after["posts"]["10"]["post_modified"], OLD[0])

    def test_sai_dinh_dang_va_thieu_cot(self):
        sai = ("10", "/a/", *OLD, "2026-10-26T14:42:31", NEW[1], "x")
        _, _, lines, after = run(store((10, *OLD)), "write", [sai, ("12", "/c/")])
        self.assertEqual([x["status"] for x in lines], ["skip: sai định dạng", "skip: thiếu cột"])
        self.assertEqual(after["posts"]["10"]["post_modified"], OLD[0])


if __name__ == "__main__":
    unittest.main(verbosity=1)
