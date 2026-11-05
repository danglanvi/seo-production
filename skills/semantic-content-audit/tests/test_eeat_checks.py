"""Test offline cho eeat_checks.py: không mạng, không model. Chạy: python3 -B -E tests/test_eeat_checks.py"""
import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "eeat_checks.py"
spec = importlib.util.spec_from_file_location("eeat_checks", SCRIPT)
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)


def write_status(rows):
    p = Path(tempfile.mkdtemp()) / "status.csv"
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["check_id", "status", "evidence"])
        w.writerows(rows)
    return p


class EeatChecks(unittest.TestCase):
    def test_map_ids_ton_tai_va_tong_26_diem(self):
        checks = ec.load_checks()
        for _, name, _, ids in ec.MAP:
            for i in ids:
                self.assertIn(i, checks, name)
        self.assertEqual(sum(m[2] for m in ec.MAP), 26)

    def test_select_core_27_va_review_khong_trung(self):
        self.assertEqual(len(ec.select(["core"], False, [])), 27)
        ids = [c["check_id"] for c in ec.select(["core", "review"], False, ["TA08"])]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("RC01", ids)

    def test_draft_dung_pre_publish_thay_core(self):
        ids = {c["check_id"] for c in ec.select([], True, [])}
        self.assertEqual(len(ids), 24)

    def test_chua_kiem_khong_phai_rot(self):
        # Ca lỗi của thang cũ: thiếu bằng chứng bị chấm 0 như rớt. Nay ghi CANNOT-VERIFY, tách khỏi Does not meet.
        res = ec.points(ec.read_status(write_status([["TA08", "Not assessed", ""], ["CQ01", "Meets", "Mục 3 có số đo"]])))
        item = next(i for i in res["items"] if i["item"] == "First-hand usage evidence")
        self.assertEqual((item["points"], item["flag"]), (0, "CANNOT-VERIFY"))
        self.assertIn("First-hand usage evidence", res["cannot_verify"])

    def test_xau_nhat_va_partly_va_na(self):
        rows = ec.read_status(write_status([
            ["PS01", "Meets", "a"], ["PS02", "Partly meets", ""],
            ["TA07", "Does not meet", "sai số liệu mục 2"], ["TA13", "Meets", "b"],
            ["SP04", "Not applicable", "trang liên hệ, không cần ảnh bằng chứng"],
        ]))
        res = {i["item"]: i for i in ec.points(rows)["items"]}
        self.assertEqual(res["Created for audience"]["points"], 1)
        self.assertEqual(res["Technical accuracy"]["points"], 0)
        self.assertEqual(res["Original evidence media"]["points"], 3)

    def test_input_hong_thoat_2(self):
        for rows in ([["XX99", "Meets", "a"]], [["PS01", "Pass", "a"]], [["PS01", "Meets", ""]], [["SP04", "Not applicable", ""]]):
            r = subprocess.run([sys.executable, "-B", "-I", str(SCRIPT), "points", "--status", str(write_status(rows))],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2, rows)


if __name__ == "__main__":
    unittest.main()
