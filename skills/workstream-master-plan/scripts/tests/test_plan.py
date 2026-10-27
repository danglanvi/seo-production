import hashlib
import json
import subprocess
import sys
import unittest
from datetime import datetime
from pathlib import Path

from _common import Base, FIXED_NOW, P, SCRIPTS, make_plan

INSTANCE = SCRIPTS.parent.parent.parent / "Deliverables/GTV-Brand/GTV-Website/master-plan/plan.json"


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


class PlanTest(Base):
    def plan_cli(self, *argv):
        return self.run_main(P.main, list(argv))

    # --- ca hỏng thật: requests[].items là list (lỗi list.replace 20/10 15:30)
    def test_items_list_bi_chan_boi_lint(self):
        def m(p):
            p["requests"][0]["items"] = ["M1", "M2"]
        f = self.write_plan(m)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 1)
        self.assertIn("CHUỖI", out)

    def test_ghi_lai_khong_the_tao_items_list(self):
        f = self.write_plan()
        code, _, _ = self.plan_cli("add-request", "--plan", str(f), "--ask", "Việc mới", "--items", "M3", "--apply")
        self.assertEqual(code, 0)
        self.assertIsInstance(self.read_plan(f)["requests"][-1]["items"], str)

    # --- giờ do code đóng dấu
    def test_gio_lay_tu_dong_ho_may(self):
        f = self.write_plan()
        self.plan_cli("add-request", "--plan", str(f), "--ask", "Đổi footer lần hai", "--items", "M2", "--apply")
        r = self.read_plan(f)["requests"][-1]
        self.assertEqual(r["date"], "25/10/2026 09:30")
        self.assertEqual(self.read_plan(f)["updated"], "25/10/2026 09:30")

    def test_khong_co_tham_so_nhap_gio_tay(self):
        f = self.write_plan()
        for flag in ("--date", "--when", "--time"):
            code, _, err = self.plan_cli("add-request", "--plan", str(f), "--ask", "x", "--items", "M1", flag, "01/01/2020 00:00")
            self.assertEqual(code, 2, flag)

    def test_canh_bao_moc_sau_gio_hien_tai(self):
        def m(p):
            p["requests"][2]["date"] = "26/10/2026 09:00"
        f = self.write_plan(m)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 0)
        self.assertIn("sau giờ hiện tại", out)
        code, _, _ = self.plan_cli("lint", "--plan", str(f), "--strict")
        self.assertEqual(code, 1)

    def test_moc_khong_nam_van_hop_le_va_qua_nam_moi(self):
        ref = datetime(2027, 1, 3, 9, 0)
        self.assertEqual(P.parse_stamp("30/12 22:00", ref), datetime(2026, 12, 30, 22, 0))
        self.assertEqual(P.parse_stamp("02/01 08:00", ref), datetime(2027, 1, 2, 8, 0))
        self.assertIsNone(P.parse_stamp("20/10 17:0x", ref))
        self.assertIsNone(P.parse_stamp("Ghi chú thẻ", ref))

    # --- dry-run mặc định
    def test_dry_run_khong_ghi(self):
        f = self.write_plan()
        before = sha(f)
        for argv in (["add-request", "--ask", "a b c", "--items", "M1"],
                     ["add-item", "--title", "Việc", "--phase", "P1", "--source", "tin"],
                     ["set-status", "M2", "done", "--evidence", "log"]):
            code, out, _ = self.plan_cli(argv[0], "--plan", str(f), *argv[1:])
            self.assertEqual(code, 0, argv)
            self.assertIn("DRY-RUN", out)
        self.assertEqual(sha(f), before)

    def test_init_dry_run_apply_va_khong_ghi_de(self):
        d = self.dir / "ws"
        code, out, _ = self.plan_cli("init", str(d))
        self.assertEqual(code, 0)
        self.assertFalse((d / "plan.json").exists())
        code, _, _ = self.plan_cli("init", str(d), "--title", "Plan thử", "--apply")
        self.assertEqual(code, 0)
        data = self.read_plan(d / "plan.json")
        self.assertEqual(data["title"], "Plan thử")
        self.assertEqual(data["updated"], "25/10/2026 09:30")
        code, _, _ = self.plan_cli("lint", "--plan", str(d / "plan.json"))
        self.assertEqual(code, 0)
        code, _, err = self.plan_cli("init", str(d), "--apply")
        self.assertEqual(code, 2)

    # --- ask quá dài, trùng
    def test_ask_qua_200_ky_tu(self):
        f = self.write_plan()
        code, _, err = self.plan_cli("add-request", "--plan", str(f), "--ask", "x" * 201, "--items", "M1", "--apply")
        self.assertEqual(code, 2)
        self.assertIn("200", err)

    def test_ask_trung_bi_tu_choi(self):
        f = self.write_plan()
        code, _, _ = self.plan_cli("add-request", "--plan", str(f), "--ask", "Sửa menu trang chủ", "--items", "M1", "--apply")
        self.assertEqual(code, 2)

    # --- việc bị sót: request không trỏ item
    def test_request_khong_tro_item_bi_lint_bat(self):
        f = self.write_plan()
        code, _, _ = self.plan_cli("add-request", "--plan", str(f), "--ask", "Thêm trang EN", "--items", "M9", "--apply")
        self.assertEqual(code, 0)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 1)
        self.assertIn("không trỏ tới việc nào", out)
        code, _, _ = self.plan_cli("add-item", "--plan", str(f), "--id", "M9", "--title", "Trang EN", "--phase", "P2",
                                   "--source", "Tin 25/10 09:00", "--apply")
        self.assertEqual(code, 0)
        code, _, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 0)

    def test_request_khong_viec_phai_co_ly_do(self):
        f = self.write_plan()
        code, _, _ = self.plan_cli("add-request", "--plan", str(f), "--ask", "Luật mới", "--apply")
        self.assertEqual(code, 2)
        code, _, _ = self.plan_cli("add-request", "--plan", str(f), "--ask", "Tối đa 10 agent",
                                   "--no-items-reason", "luật chung", "--apply")
        self.assertEqual(code, 0)
        code, _, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 0)

    # --- add-item
    def test_add_item_tu_cap_id_blocks_va_program(self):
        f = self.write_plan()
        code, _, _ = self.plan_cli("add-item", "--plan", str(f), "--title", "Việc mới", "--phase", "P2", "--deps", "M2,M3",
                                   "--source", "Tin 25/10 09:00", "--program", "Site B", "--detail", "d1", "--apply")
        self.assertEqual(code, 0)
        d = self.read_plan(f)
        new = d["items"][-1]
        self.assertEqual(new["id"], "M4")
        self.assertEqual(new["program"], "Site B")
        self.assertEqual(new["added"], "25/10/2026 09:30")
        by = {i["id"]: i for i in d["items"]}
        self.assertIn("M4", by["M2"]["blocks"])
        self.assertIn("M4", by["M3"]["blocks"])

    def test_add_item_phase_la_hoac_thieu_source_bi_tu_choi(self):
        f = self.write_plan()
        before = sha(f)
        code, _, err = self.plan_cli("add-item", "--plan", str(f), "--title", "x", "--phase", "P9", "--source", "tin", "--apply")
        self.assertEqual(code, 2)
        self.assertIn("phase", err)
        code, _, _ = self.plan_cli("add-item", "--plan", str(f), "--title", "x", "--phase", "P1", "--source", " ", "--apply")
        self.assertEqual(code, 2)
        code, _, _ = self.plan_cli("add-item", "--plan", str(f), "--title", "x", "--phase", "P1", "--source", "t", "--deps", "M99", "--apply")
        self.assertEqual(code, 2)
        self.assertEqual(sha(f), before)

    # --- set-status
    def test_done_can_evidence_va_need_can_checked(self):
        f = self.write_plan()
        code, _, err = self.plan_cli("set-status", "--plan", str(f), "M2", "done", "--apply")
        self.assertEqual(code, 2)
        code, _, err = self.plan_cli("set-status", "--plan", str(f), "M3", "need", "--apply")
        self.assertEqual(code, 2)
        self.assertEqual(self.read_plan(f)["items"][1]["status"], "doing")
        code, _, _ = self.plan_cli("set-status", "--plan", str(f), "M3", "need", "--checked", "thẻ M3 chưa duyệt, chat chưa nhắc", "--apply")
        self.assertEqual(code, 0)
        code, _, _ = self.plan_cli("set-status", "--plan", str(f), "M2", "done", "--evidence", "log/footer.log", "--apply")
        self.assertEqual(code, 0)
        d = self.read_plan(f)
        self.assertEqual(d["items"][1]["status"], "done")
        self.assertEqual(d["items"][1]["status_at"], "25/10/2026 09:30")

    # --- lint
    def test_deps_vong_bi_bat(self):
        def m(p):
            p["items"][0]["deps"] = ["M2"]
        f = self.write_plan(m)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 1)
        self.assertIn("vòng", out)

    def test_lint_item_thieu_source_va_done_thieu_evidence(self):
        def m(p):
            p["items"][0]["evidence"] = ""
            p["items"][1]["source"] = ""
        f = self.write_plan(m)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 1)
        self.assertIn("M1: done nhưng thiếu evidence", out)
        self.assertIn("M2: thiếu source", out)

    def test_lint_status_va_id_trung(self):
        def m(p):
            p["items"][2]["status"] = "xong"
            p["items"][1]["id"] = "M1"
        f = self.write_plan(m)
        code, out, _ = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 1)
        self.assertIn("status 'xong'", out)
        self.assertIn("id trùng", out)

    def test_json_hong_ma_thoat_3(self):
        f = self.dir / "plan.json"
        f.write_text("{không phải json", encoding="utf-8")
        code, _, err = self.plan_cli("lint", "--plan", str(f))
        self.assertEqual(code, 3)
        code, _, _ = self.plan_cli("lint", "--plan", str(self.dir / "khong-co.json"))
        self.assertEqual(code, 3)

    # --- progress
    def test_progress_dem_tu_file(self):
        f = self.write_plan()
        code, out, _ = self.plan_cli("progress", "--plan", str(f))
        self.assertEqual(code, 0)
        self.assertIn("Tiến độ chương trình: 1/3 (33%)", out)
        self.assertIn("- Site A: 1/2", out)
        self.assertIn("- Site B: 0/1", out)
        code, out, _ = self.plan_cli("progress", "--plan", str(f), "--program", "Site A")
        self.assertIn("Tiến độ chương trình Site A: 1/2 (50%)", out)
        code, _, _ = self.plan_cli("progress", "--plan", str(f), "--program", "Không có")
        self.assertEqual(code, 2)

    # --- phiên khác ghi cùng lúc
    def test_file_doi_giua_chung_ma_thoat_4(self):
        f = self.write_plan()
        plan, raw = P.load_plan(str(f))
        f.write_text(json.dumps(make_plan(lambda p: p.update(title="Bản do phiên khác ghi")), ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(P.PlanError) as cm:
            P.save_plan(str(f), plan, raw)
        self.assertEqual(cm.exception.code, 4)
        self.assertEqual(self.read_plan(f)["title"], "Bản do phiên khác ghi")

    def test_ghi_khong_de_lai_file_tam(self):
        f = self.write_plan()
        self.plan_cli("add-request", "--plan", str(f), "--ask", "Yêu cầu thêm", "--items", "M1", "--apply")
        self.assertEqual([p.name for p in self.dir.iterdir()], ["plan.json"])

    # --- --help và chạy như script
    def test_help_tung_lenh(self):
        for sub in ([], ["init"], ["add-request"], ["add-item"], ["set-status"], ["progress"], ["lint"]):
            r = subprocess.run([sys.executable, str(SCRIPTS / "plan.py"), *sub, "--help"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, sub)
            self.assertIn("usage", r.stdout)

    def test_exit_code_khac_0_khi_thieu_doi_so(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "plan.py"), "add-request"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    # --- tương thích instance thật (chỉ đọc, bỏ qua khi không có)
    @unittest.skipUnless(INSTANCE.exists(), "không có instance mẫu")
    def test_doc_duoc_instance_mau_khong_loi_schema(self):
        plan, _ = P.load_plan(str(INSTANCE))
        errs, _ = P.validate(plan)
        schema_errs = [e for e in errs if "phải là" in e or "thiếu hoặc sai kiểu" in e or "không hợp lệ" in e
                       or "không có trong phases" in e or "trùng" in e or "vòng" in e]
        self.assertEqual(schema_errs, [])
        self.assertTrue(P.progress_line(plan).startswith("Tiến độ chương trình"))


if __name__ == "__main__":
    unittest.main()
