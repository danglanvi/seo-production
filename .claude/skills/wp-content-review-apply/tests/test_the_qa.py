"""Test offline scripts/the_qa.py (cổng QA máy cho thẻ có chữ mới).
Chạy: python3 -B tests/test_the_qa.py
Ca hỏng thật:
- 17/10 (0632744c-03, d61dfcca-04): Vincent nhắc 3 lần vì thẻ nạp lên trang duyệt khi chữ chưa qua humanizer.
- 18/10 (7ecaa7b8-02): thẻ r7s-m1-hero mất link nội bộ và còn câu 'hàng đầu' cũ.
- 60 meta viết lại 3 vòng vì quá 160 ký tự; số liệu 'hơn 200 khách' không có trong fact.
- Cam kết hoàn tiền không được tự thêm vào chữ web (AGENTS.md, CAM KẾT VÀ BẢO ĐẢM).
"""
import json
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "the_qa.py"
STUB = """import sys, json
t = sys.stdin.read()
bad = 'hoàn tiền' in t.lower()
print(json.dumps({'tong': {'chặn': 1 if bad else 0, 'xem': 0}, 'dong': []}))
sys.exit(1 if bad else 0)
"""
QA = {"humanizer": "1.4 | đã rà", "jev_text_qa": "ok"}


def field(key, before, **kw):
    f = {"key": key, "name": key, "before": before}
    f.update(kw)
    return f


def card(iid, fields, **kw):
    c = {"id": iid, "post_id": 1, "url": "https://example.vn/", "fields": fields}
    c.update(kw)
    return c


def w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


class TheQA(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)
        (self.d / "stub.py").write_text(STUB, encoding="utf-8")
        w(self.d / "facts.json", {"khach": "hơn 100 khách hàng", "nam": 10})

    def tearDown(self):
        self.t.cleanup()

    def run_qa(self, items, extra=(), facts=True, report_name="meta"):
        w(self.d / "report" / (report_name + ".json"), {"items": items})
        args = [sys.executable, "-I", str(SCRIPT), str(self.d / "report"), "--entity", "gtv", "--khong-px",
                "--copy-guard", str(self.d / "stub.py"), "--nam", "2026", "--json"]
        if facts:
            args += ["--facts", str(self.d / "facts.json")]
        p = subprocess.run(args + list(extra), capture_output=True, text=True, timeout=60)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
        return p.returncode, out, p.stderr

    def msgs(self, out):
        return " | ".join(e["msg"] for e in out["errors"])

    def test_sach_thi_exit_0(self):
        c = card("ok-1", [field("meta", "Meta cũ 10 năm.", proposed="Meta mới sau 10 năm làm SEO.", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["chu_da_kiem"], 1)
        self.assertFalse(out["da_ghi"])

    def test_thieu_humanizer_bi_chan(self):
        c = card("h-1", [field("meta", "Cũ", proposed="Mới viết tay chưa rà.")])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("qa.humanizer", self.msgs(out))

    def test_humanizer_rong_bi_chan(self):
        c = card("h-2", [field("meta", "Cũ", proposed="Mới.", qa={"humanizer": "  "})])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)

    def test_qa_cap_the_dung_chung(self):
        c = card("h-3", [field("meta", "Cũ", proposed="Mới.")], qa=QA)
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)

    def test_mat_link_bi_chan(self):
        before = 'Xem <a href="/dich-vu-seo/">dịch vụ SEO</a> và <a href="https://example.vn/lien-he/">liên hệ</a>.'
        proposed = 'Xem <a href="/dich-vu-seo/">dịch vụ SEO</a> và liên hệ.'
        c = card("r7s-m1-hero", [field("hero", before, raw=before, proposed=proposed, qa=QA)])
        rc, out, err = self.run_qa([c], extra=["--site", "https://example.vn"])
        self.assertEqual(rc, 1)
        self.assertIn("mất link: /lien-he", self.msgs(out))

    def test_link_cung_host_khac_dang_viet_khong_phai_mat(self):
        before = 'Xem <a href="https://example.vn/lien-he/">liên hệ</a>.'
        proposed = 'Hãy <a href="/lien-he">liên hệ</a> ngay.'
        c = card("l-1", [field("hero", before, raw=before, proposed=proposed, qa=QA)])
        rc, out, err = self.run_qa([c], extra=["--site", "https://example.vn"])
        self.assertEqual(rc, 0, out)

    def test_them_link_chi_ghi_nhan(self):
        c = card("l-2", [field("hero", "Cũ", proposed='Mới <a href="/moi/">chỗ mới</a>.', qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)

    def test_meta_qua_160_ky_tu(self):
        c = card("m-1", [field("meta", "Cũ", proposed="a" * 161, qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("161 ký tự, tối đa 160", self.msgs(out))

    def test_title_dem_sau_khi_thay_bien_nam(self):
        # 62 ký tự + biến năm: %currentyear% (13 ký tự) đổi thành 2026 (4 ký tự), vừa 65
        t = "b" * 55 + " %currentyear%"
        c = card("t-1", [field("seo_title", "Cũ", proposed=t, qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)
        c = card("t-2", [field("seo_title", "Cũ", proposed="b" * 62 + " %currentyear%", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)

    def test_so_khong_co_trong_fact_bi_chan(self):
        c = card("n-1", [field("meta", "Cũ", proposed="Hơn 200 khách hàng tin dùng.", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("200", self.msgs(out))

    def test_so_co_trong_fact_hoac_before_thi_qua(self):
        c = card("n-2", [field("meta", "Cũ có 7 bước.", proposed="Hơn 100 khách, 10 năm, 7 bước.", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)

    def test_so_hang_nghin_khac_dau_phan_cach(self):
        c = card("n-3", [field("meta", "Giá từ 5.000.000 đồng.", proposed="Giá từ 5,000,000 đồng.", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)

    def test_copy_guard_chan_hoan_tien(self):
        c = card("c-1", [field("hero", "Cũ", proposed="Cam kết hoàn tiền nếu không hài lòng.", qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("copy_guard chặn", self.msgs(out))

    def test_thieu_copy_guard_thoat_2(self):
        w(self.d / "report" / "meta.json", {"items": [card("c-2", [field("meta", "Cũ", proposed="Mới", qa=QA)])]})
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.d / "report"), "--entity", "gtv", "--khong-px",
                            "--facts", str(self.d / "facts.json"), "--copy-guard", str(self.d / "khong-co.py")],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)
        self.assertIn("copy_guard", p.stderr)

    def test_khong_copy_guard_chi_canh_bao(self):
        c = card("c-3", [field("meta", "Cũ", proposed="Mới", qa=QA)])
        rc, out, err = self.run_qa([c], extra=["--khong-copy-guard"])
        self.assertEqual(rc, 0, out)
        self.assertTrue(any("copy_guard" in x["msg"] for x in out["warnings"]))

    def test_chu_nfd_bi_chan(self):
        nfd = unicodedata.normalize("NFD", "Dịch vụ SEO tổng thể")
        c = card("u-1", [field("meta", "Cũ", proposed=nfd, qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("NFC", self.msgs(out))

    def test_truong_giu_nguyen_va_slug_khong_kiem(self):
        c = card("g-1", [field("meta", "Giữ nguyên", A="Giữ nguyên", B="Giữ nguyên"),
                         field("slug", "/cu/", proposed="/moi-2026/")])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["chu_da_kiem"], 0)

    def test_hai_phuong_an_loi_o_phuong_an_b(self):
        c = card("ab-1", [field("meta", "Cũ", A="Ổn.", B="x" * 170, qa=QA)])
        rc, out, err = self.run_qa([c])
        self.assertEqual(rc, 1)
        self.assertIn("phương án B", self.msgs(out))

    def test_ghi_chi_khi_khong_loi_va_khong_de(self):
        c = card("w-1", [field("meta", "Cũ", proposed="Mới có 10 năm.", qa=QA)])
        outdir = self.d / "ra"
        rc, out, err = self.run_qa([c], extra=["--ghi", str(outdir)])
        self.assertEqual(rc, 0, out)
        d = json.loads((outdir / "meta.json").read_text(encoding="utf-8"))
        qa = d["items"][0]["fields"][0]["qa"]
        self.assertEqual(qa["humanizer"], "1.4 | đã rà")
        self.assertEqual(qa["copy_guard"], "ok")
        self.assertEqual(qa["do_dai"]["ky_tu"], 14)
        self.assertTrue(qa["nfc"])
        self.assertEqual(qa["links"], {"mat": [], "them": []})
        # lần hai không có --force: thoát 2, không ghi đè
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.d / "report"), "--entity", "gtv", "--khong-px",
                            "--copy-guard", str(self.d / "stub.py"), "--facts", str(self.d / "facts.json"), "--ghi", str(outdir)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)

    def test_co_loi_thi_khong_ghi(self):
        c = card("w-2", [field("meta", "Cũ", proposed="Mới.")])
        outdir = self.d / "ra2"
        rc, out, err = self.run_qa([c], extra=["--ghi", str(outdir)])
        self.assertEqual(rc, 1)
        self.assertFalse(outdir.exists())

    def test_thieu_facts_thoat_2(self):
        c = card("f-1", [field("meta", "Cũ", proposed="Mới", qa=QA)])
        w(self.d / "report" / "meta.json", {"items": [c]})
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.d / "report"), "--entity", "gtv",
                            "--facts", str(self.d / "khong-co.json")], capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)

    def test_do_px_khi_co_serp_pixel(self):
        w(self.d / "report" / "meta.json", {"items": [card("px-1", [field("seo_title", "Cũ", proposed="Tiêu đề ngắn", qa=QA)])]})
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.d / "report"), "--entity", "gtv", "--facts", str(self.d / "facts.json"),
                            "--copy-guard", str(self.d / "stub.py"), "--json"], capture_output=True, text=True, timeout=60)
        out = json.loads(p.stdout)
        self.assertEqual(p.returncode, 0, out)


if __name__ == "__main__":
    unittest.main()
