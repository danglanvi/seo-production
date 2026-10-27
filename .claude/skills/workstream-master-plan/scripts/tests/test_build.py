import re
import unittest

from _common import Base, FIXED_NOW, P, make_plan
import build as B


class BuildTest(Base):
    def build(self, f, *extra):
        return self.run_main(B.main, ["--plan", str(f), *extra])

    def outputs(self):
        return sorted(p.name for p in self.dir.iterdir() if p.name != "plan.json")

    def test_dry_run_khong_ghi_con_apply_thi_ghi(self):
        f = self.write_plan()
        code, out, _ = self.build(f)
        self.assertEqual(code, 0)
        self.assertIn("DRY-RUN", out)
        self.assertEqual(self.outputs(), [])
        code, out, _ = self.build(f, "--apply")
        self.assertEqual(code, 0)
        self.assertEqual(self.outputs(), ["master-plan-site-mau_master-plan.html", "master-plan-site-mau_master-plan.md"])
        self.assertIn("Tiến độ chương trình: 1/3 (33%)", out)
        self.assertIn("'done': 1", out)

    def test_moi_ngay_deu_hien(self):
        def m(p):
            p["requests"] += [
                {"date": "20/10 17:0x", "ask": "Giờ viết tay", "items": "M1"},
                {"date": "Ghi chú thẻ", "ask": "Không có ngày", "items": "M3"},
                {"date": "25/10/2026 08:00", "ask": "Ngày cuối", "items": "M3"},
            ]
        f = self.write_plan(m)
        self.assertEqual(self.build(f, "--apply")[0], 0)
        html = (self.dir / "master-plan-site-mau_master-plan.html").read_text(encoding="utf-8")
        md = (self.dir / "master-plan-site-mau_master-plan.md").read_text(encoding="utf-8")
        days = re.findall(r'data-day="([^"]+)"', html)
        self.assertEqual(days, ["2026-10-20", "2026-10-23", "2026-10-24", "2026-10-25", "unknown"])
        for label in ("20/10/2026", "23/10/2026", "24/10/2026", "25/10/2026", "Không rõ ngày"):
            self.assertIn("### Ngày %s" % label, md)
        self.assertEqual(len(re.findall(r'<tr class="reqrow">', html)), 6)

    # --- ca hỏng thật: báo cáo v1 chỉ mở ngày cuối (22:35 19/10)
    def test_assert_bat_loi_chi_hien_ngay_cuoi(self):
        plan = make_plan()
        html, md = B.render_html(plan, FIXED_NOW), B.render_md(plan, FIXED_NOW)
        B.check_render(plan, html, md, FIXED_NOW)
        parts = html.split('<section class="day"')
        broken = parts[0] + '<section class="day"' + parts[-1]
        with self.assertRaises(B.AssertFail) as cm:
            B.check_render(plan, broken, md, FIXED_NOW)
        self.assertIn("thiếu ngày", str(cm.exception))
        broken_md = re.sub(r"### Ngày 23/10/2026.*?(?=### Ngày 24)", "", md, flags=re.S)
        with self.assertRaises(B.AssertFail):
            B.check_render(plan, html, broken_md, FIXED_NOW)

    def test_assert_bat_loi_mat_viec(self):
        plan = make_plan()
        html, md = B.render_html(plan, FIXED_NOW), B.render_md(plan, FIXED_NOW)
        no_item = re.sub(r'<details class="item s-todo".*?</details>', "", html, flags=re.S)
        with self.assertRaises(B.AssertFail) as cm:
            B.check_render(plan, no_item, md, FIXED_NOW)
        self.assertIn("HTML có 2 việc, data có 3", str(cm.exception))
        no_md = md.replace("- [ ] **M3**", "- [ ] M3")
        with self.assertRaises(B.AssertFail):
            B.check_render(plan, html, no_md, FIXED_NOW)

    # --- việc trỏ phase không có sẽ rơi khỏi báo cáo âm thầm; build phải dừng
    def test_phase_la_lam_build_dung_va_khong_ghi(self):
        def m(p):
            p["items"][2]["phase"] = "P9"
        f = self.write_plan(m)
        code, _, err = self.build(f, "--apply")
        self.assertEqual(code, 2)
        self.assertIn("phase", err)
        self.assertEqual(self.outputs(), [])

    # --- ca hỏng thật: requests[].items là list (list.replace 20/10 15:30)
    def test_items_list_lam_build_dung_khong_vang_loi_python(self):
        def m(p):
            p["requests"][0]["items"] = ["M1"]
        f = self.write_plan(m)
        code, _, err = self.build(f, "--apply")
        self.assertEqual(code, 2)
        self.assertIn("CHUỖI", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(self.outputs(), [])

    def test_html_escape_title_va_ask(self):
        def m(p):
            p["title"] = "Plan <script>alert(1)</script>"
            p["requests"][0]["ask"] = "<img src=x onerror=1>"
        f = self.write_plan(m)
        self.build(f, "--apply")
        html = next(self.dir.glob("*.html")).read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)", html)
        self.assertNotIn("<img src=x", html)

    def test_bao_cao_phien(self):
        def m(p):
            p["items"][1].update(status="done", evidence="log/footer.log", status_at="25/10/2026 08:10")
            p["items"][0]["status_at"] = "23/10/2026 12:00"
            p["requests"].append({"date": "25/10/2026 08:00", "ask": "Yêu cầu trong phiên", "items": "M3"})
            p["items"][2].update(status="need", need_checked="thẻ chưa duyệt")
        f = self.write_plan(m)
        code, out, _ = self.build(f, "--session-report", "--since", "25/10/2026 00:00", "--apply")
        self.assertEqual(code, 0, out)
        rep = (self.dir / "master-plan-site-mau_bao-cao-phien_v1.md").read_text(encoding="utf-8")
        self.assertIn("**Tiến độ chương trình: 2/3 (66%)**", rep)
        self.assertIn("## Yêu cầu mới trong phiên (1)", rep)
        self.assertIn("## Xong trong phiên (1)", rep)
        self.assertIn("**M2** Sửa footer. Bằng chứng: log/footer.log", rep)
        self.assertIn("Đã kiểm chưa duyệt: thẻ chưa duyệt", rep)
        self.assertNotIn("**M1** Sửa menu. Bằng chứng", rep)
        self.build(f, "--session-report", "--since", "25/10/2026 00:00", "--apply")
        self.assertTrue((self.dir / "master-plan-site-mau_bao-cao-phien_v2.md").exists())

    def test_assert_bao_cao_phien_bat_dem_sai(self):
        plan = make_plan()
        text, meta = B.render_session_report(plan, FIXED_NOW, FIXED_NOW.replace(hour=0, minute=0))
        B.check_session_report(plan, text, meta)
        with self.assertRaises(B.AssertFail):
            B.check_session_report(plan, text.replace("- **M2**", "- M2"), meta)

    def test_since_sai_dang_ma_thoat_2(self):
        f = self.write_plan()
        code, _, _ = self.build(f, "--session-report", "--since", "hôm qua")
        self.assertEqual(code, 2)

    def test_khong_tai_tai_nguyen_ngoai(self):
        html = B.render_html(make_plan(), FIXED_NOW)
        self.assertNotRegex(html, r"https?://")

    def test_help(self):
        code, out, _ = self.run_main(B.main, ["--help"])
        self.assertEqual(code, 0)
        self.assertIn("--apply", out)


if __name__ == "__main__":
    unittest.main()
