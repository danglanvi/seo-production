"""Test offline cho the_link.py và link_code_audit.py. Không gọi mạng, không cần thư viện ngoài.
Chạy: python3 -B scripts/tests/test_internal_linking.py   (từ thư mục skill) hoặc python3 -B test_internal_linking.py

Ca hỏng thật (nguồn lỗi):
- Helper ad hoc review/dieu_chinh_vi_tri_link.py (mạng nội dung vidu.vn, 18/10/2026) sửa link trong thẻ bằng assert count == 1
  và regex trên thẻ <a> thô. Nó gãy với: anchor có &amp; (SEO &amp; GEO), anchor chia qua <span> lồng trong <a>, href tuyệt đối có www,
  href nháy đơn, nhiều link cùng đích (assert dừng chương trình, không báo link nào). Các test test_ca_that_* tái hiện từng lỗi.
  Phần EV của đề xuất nd-10 bị cắt ở 500 ký tự nên chưa đối chiếu thêm ca cụ thể.
- Kiểm kê dạng mã link làm tay ngày 19/10/2026 (review/link_js/ của cùng mạng nội dung) gặp dạng lai <a href onclick>, href="#" mở menu,
  span onclick thiếu role và tabindex. Các test test_audit_* kiểm từng dạng.
"""
import contextlib
import gzip
import io
import json
import os
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import the_link as TL  # noqa: E402
import link_code_audit as LA  # noqa: E402

HOST = ["vidu.vn"]


def jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def lines_of(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def run(mod, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = mod.main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


DOC = """# Bài mẫu

Mở bài không link.

## Mục chính

Xem <a href="https://www.vidu.vn/dich-vu-seo/"><span class="x">dịch vụ SEO</span>&nbsp;&amp; GEO</a> để biết phạm vi việc.

## Đo lường

Đọc [GEO [2026]](/geo/) để nắm cách đo.

## Kết luận

Xem bảng giá dịch vụ SEO để biết chi phí.

## FAQ

Hỏi đáp thêm.
"""


class TheLinkTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = Path(self.tmp.name) / "the.md"
        self.f.write_text(DOC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return run(TL, list(args) + ["--host", "vidu.vn"])

    # ----- ca hỏng thật -----
    def test_ca_that_amp_nbsp_span_long(self):
        new, info = TL.reanchor_text(DOC, "/dich-vu-seo/", "dịch vụ SEO & GEO", "dịch vụ SEO và GEO", hosts=HOST)
        self.assertIn('<span class="x">dịch vụ SEO và GEO</span></a>', new)
        self.assertEqual(new.count("<span"), new.count("</span>"))
        self.assertEqual(len(info), 1)

    def test_ca_that_href_tuyet_doi_va_nhay_don(self):
        doc = "## A\n\nXem <a class='k' href='http://vidu.vn/dich-vu-seo'>dịch vụ</a> ngay.\n\n## FAQ\n\nx\n"
        new, _ = TL.unlink_text(doc, "/dich-vu-seo/", hosts=HOST)
        self.assertIn("Xem dịch vụ ngay.", new)
        self.assertNotIn("<a", new)

    def test_ca_that_nhieu_link_cung_dich_khong_assert(self):
        doc = "## A\n\n[a](/x/) và [b](/x/)\n\n## FAQ\n\nz\n"
        with self.assertRaises(TL.Err) as cm:
            TL.unlink_text(doc, "/x/", hosts=HOST)
        self.assertIn("--nth", str(cm.exception))
        new, info = TL.unlink_text(doc, "/x/", hosts=HOST, nth=2)
        self.assertEqual(new.split("\n\n")[1], "[a](/x/) và b")
        new, info = TL.unlink_text(doc, "/x/", hosts=HOST, all_=True)
        self.assertEqual(len(info), 2)

    def test_ca_that_anchor_markdown_co_ngoac_long(self):
        new, _ = TL.unlink_text(DOC, "/geo/", hosts=HOST)
        self.assertIn("Đọc GEO [2026] để nắm", new)

    def test_nbsp_ky_tu_va_nfd(self):
        doc = "## A\n\nĐọc [dịch vụ SEO](/x/) nhé.\n"
        nfd = unicodedata.normalize("NFD", "dịch vụ SEO")
        new, _ = TL.reanchor_text(doc, "/x/", nfd, "dịch vụ SEO & GEO", hosts=HOST)
        self.assertIn("[dịch vụ SEO & GEO](/x/)", new)

    def test_khong_dung_link_trong_code_va_comment(self):
        doc = "## A\n\n```\n[a](/x/)\n```\n\n<!-- <a href=\"/x/\">c</a> -->\n\nThật: [b](/x/)\n"
        links = TL.find_links(doc, set())
        self.assertEqual([l.anchor for l in links], ["b"])

    def test_reanchor_khong_khop_bao_loi_khong_ghi(self):
        rc, out, err = self.cli("reanchor", str(self.f), "--target", "/geo/", "--old", "không có", "--new", "x", "--write")
        self.assertEqual(rc, 1)
        self.assertEqual(self.f.read_text(encoding="utf-8"), DOC)

    # ----- dry-run và ghi -----
    def test_dry_run_mac_dinh_khong_ghi(self):
        rc, out, _ = self.cli("unlink", str(self.f), "--target", "/geo/")
        self.assertEqual(rc, 0)
        self.assertIn("Dry-run", out)
        self.assertEqual(self.f.read_text(encoding="utf-8"), DOC)
        self.assertEqual(len(list(self.f.parent.iterdir())), 1)

    def test_write_tao_ban_luu(self):
        rc, out, _ = self.cli("unlink", str(self.f), "--target", "/geo/", "--write")
        self.assertEqual(rc, 0)
        self.assertNotIn("](/geo/)", self.f.read_text(encoding="utf-8"))
        baks = [p for p in self.f.parent.iterdir() if ".bak-" in p.name]
        self.assertEqual(len(baks), 1)
        self.assertEqual(baks[0].read_text(encoding="utf-8"), DOC)

    def test_out_khong_ghi_de(self):
        o = self.f.parent / "moi.md"
        self.assertEqual(self.cli("unlink", str(self.f), "--target", "/geo/", "--out", str(o))[0], 0)
        self.assertTrue(o.exists())
        self.assertEqual(self.cli("unlink", str(self.f), "--target", "/geo/", "--out", str(o))[0], 1)

    def test_write_va_out_cung_luc_la_loi_tham_so(self):
        self.assertEqual(self.cli("unlink", str(self.f), "--target", "/geo/", "--write", "--out", "x")[0], 2)

    def test_missing_ok_chay_lai_an_toan(self):
        self.assertEqual(self.cli("unlink", str(self.f), "--target", "/khong-co/")[0], 1)
        self.assertEqual(self.cli("unlink", str(self.f), "--target", "/khong-co/", "--missing-ok")[0], 0)

    # ----- đếm luật -----
    def test_to_sc_chuyen_xuong_muc_sc(self):
        new, info = TL.to_sc_text(DOC, "/dich-vu-seo/", "bảng giá dịch vụ SEO", hosts=HOST)
        sec = new.split("## Kết luận")[1].split("## FAQ")[0]
        self.assertIn('<a href="https://www.vidu.vn/dich-vu-seo/">bảng giá dịch vụ SEO</a>', sec)
        self.assertNotIn("<a ", new.split("## Kết luận")[0])
        self.assertEqual(len(info), 2)

    def test_to_sc_khong_thay_chu_thi_dung(self):
        rc, _, err = self.cli("to-sc", str(self.f), "--target", "/dich-vu-seo/", "--anchor", "chữ không tồn tại", "--write")
        self.assertEqual(rc, 1)
        self.assertEqual(self.f.read_text(encoding="utf-8"), DOC)

    def test_to_sc_bo_qua_chu_da_nam_trong_link(self):
        doc = DOC.replace("Xem bảng giá dịch vụ SEO", "Xem [bảng giá dịch vụ SEO](/gia/)")
        with self.assertRaises(TL.Err):
            TL.to_sc_text(doc, "/dich-vu-seo/", "bảng giá dịch vụ SEO", hosts=HOST, to_h2="kết luận")

    def test_to_sc_chan_ghi_khi_sinh_vi_pham_moi(self):
        sa = Path(self.tmp.name) / "sa.json"
        sa.write_text(json.dumps({"bảng giá dịch vụ seo": 3}), encoding="utf-8")
        args = ["to-sc", str(self.f), "--target", "/dich-vu-seo/", "--anchor", "bảng giá dịch vụ SEO", "--to-h2", "kết luận",
                "--site-anchors", str(sa), "--write"]
        rc, out, _ = self.cli(*args)
        self.assertEqual(rc, 3)
        self.assertIn("R3", out)
        self.assertEqual(self.f.read_text(encoding="utf-8"), DOC)
        self.assertEqual(self.cli(*args, "--allow-violations")[0], 0)
        self.assertIn("/dich-vu-seo/\">bảng giá dịch vụ SEO</a>", self.f.read_text(encoding="utf-8"))

    def test_vi_pham_co_san_khong_chan_lan_sua_khac(self):
        doc = DOC.replace("Hỏi đáp thêm.", "Xem thêm [dịch vụ](https://vidu.vn/dich-vu-seo/).")
        self.f.write_text(doc, encoding="utf-8")
        rc, out, _ = self.cli("unlink", str(self.f), "--target", "/geo/", "--write")
        self.assertEqual(rc, 0)
        self.assertIn("VI PHẠM R1", out)

    def test_r2_hai_link_moi_trong_mot_h2_mc(self):
        doc = "## Mục\n\n[a](/a/) và [b](/b/)\n\n## FAQ\n\nx\n\n## Kết luận\n\ny\n"
        rep = TL.analyze({"d": doc}, HOST)
        self.assertEqual([v["luat"] for v in rep["vi_pham"]], ["R2"])
        base = "## Mục\n\n[a](/a/) và b\n\n## FAQ\n\nx\n\n## Kết luận\n\ny\n"
        rep = TL.analyze({"d": doc}, HOST, base_texts={"d": base})
        self.assertEqual(rep["vi_pham"], [])

    def test_r2_khong_ap_cho_sc(self):
        doc = "## Mục\n\ntext\n\n## FAQ\n\n[a](/a/) và [b](/b/)\n\n## Kết luận\n\n[c](/c/) [d](/d/)\n"
        self.assertEqual(TL.analyze({"d": doc}, HOST)["vi_pham"], [])

    def test_r1_link_manh_cung_dich(self):
        doc = "## Mục\n\n[a](/a/) rồi [b](/a/#phan-2)\n\n## FAQ\n\nx\n\n## KL\n\ny\n"
        rep = TL.analyze({"d": doc}, HOST)
        self.assertIn("R1", [v["luat"] for v in rep["vi_pham"]])

    def test_r3_anchor_qua_3_lan_qua_nhieu_file(self):
        t = {"f%d" % i: "## A\n\n[SEO&nbsp;tổng thể](/x%d/)\n\n## FAQ\n\nz\n\n## KL\n\nz\n" % i for i in range(4)}
        rep = TL.analyze(t, HOST)
        r3 = [v for v in rep["vi_pham"] if v["luat"] == "R3"]
        self.assertEqual(len(r3), 1)
        self.assertEqual(r3[0]["so_lan"], 4)
        rep = TL.analyze({"f0": t["f0"]}, HOST, site_anchors={"seo tổng thể": 3})
        self.assertEqual([v["luat"] for v in rep["vi_pham"]], ["R3"])

    def test_check_thoat_3_khi_vi_pham(self):
        self.f.write_text("## M\n\n[a](/a/) [b](/b/)\n\n## FAQ\n\nx\n\n## KL\n\ny\n", encoding="utf-8")
        self.assertEqual(run(TL, ["check", str(self.f)])[0], 3)
        self.assertEqual(run(TL, ["check", str(self.f), "--json"])[0], 3)

    def test_canh_bao_mo_bai(self):
        doc = "Mở bài có [a](/a/).\n\n## M\n\ntext\n\n## FAQ\n\nx\n\n## KL\n\ny\n"
        rep = TL.analyze({"d": doc}, HOST)
        self.assertEqual([w["luat"] for w in rep["canh_bao"]], ["mo_bai"])
        self.assertEqual(rep["vi_pham"], [])

    def test_help_cac_lenh(self):
        for argv in ([], ["unlink"], ["reanchor", "x"]):
            self.assertEqual(run(TL, argv)[0], 2)
        rc, out, _ = run(TL, ["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("dry-run", out)


A_HTML = """<!doctype html><html><head><link rel="canonical" href="https://www.vidu.vn/a/">
<title>A</title></head><body>
<header><nav><a href="/gioi-thieu/">Giới thiệu</a>
<a href="#" aria-expanded="false">Dịch vụ</a>
<a href="#">Rỗng</a></header>
<main><h1>A</h1>
<p>Mở bài <a href="https://vidu.vn/b/"><span>trang</span> <img alt="bê"></a>
<p>Hybrid <a href="/c/" onclick="location.href='/d/'">c</a> và <a href="javascript:void(0)">js</a>
<button type="button" onclick="location.href='/lien-he/'">Liên hệ</button>
<span onclick="location.href='/doi-ngu/'">Đội ngũ</span>
<span role="link" tabindex="0" onclick="location.href='/tuyen-dung/'">Tuyển</span>
<div onclick="window.open('https://maps.example/x','_blank')">Bản đồ</div>
<a href="https://ext.example/p" target="_blank">ngoài</a>
<a href="/b/">tới b</a>
<h2>Nội dung</h2><p>Chữ <a href="/e/">e</a></p>
<h2>Câu hỏi thường gặp</h2><p><a href="/f/">f</a></p>
<h2>Cuối</h2><p><a href="/g/">g</a></p>
</main>
<footer><a href="/chinh-sach/">Chính sách</a></footer></body></html>
"""
B_HTML = """<html><head><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://vidu.vn/b/"></head><body>
<main><h1>B</h1><p>x <a href="/a/">a</a></p><p><a href="/d/">d thật</a></p></main>
<footer><a href="/chinh-sach/">Chính sách</a></footer></body></html>
"""
C_HTML = """<html><head><link rel="canonical" href="https://vidu.vn/c/"></head><body>
<main><h1>C</h1><h2>Mục</h2><p>x</p></main>
<footer><a href="/chinh-sach/">Chính sách</a></footer></body></html>
"""


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name) / "pages"
        self.d.mkdir()
        (self.d / "a.html").write_text(A_HTML, encoding="utf-8")
        with gzip.open(self.d / "b.html.gz", "wt", encoding="utf-8") as f:
            f.write(B_HTML)
        (self.d / "c.html").write_text(C_HTML, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def inv(self):
        out = Path(self.tmp.name) / "out"
        rc, _, _ = run(LA, ["scan", str(self.d), "--host", "vidu.vn", "--out", str(out)])
        self.assertEqual(rc, 0)
        rows = jsonl(out / "inventory.jsonl")
        return out, rows

    def find(self, rows, page, text):
        return next(r for r in rows if r["page"] == page and r["text"].startswith(text))

    def test_audit_dang_lai(self):
        _, rows = self.inv()
        self.assertIn("lai", self.find(rows, "/a", "c")["flags"])
        self.assertEqual(self.find(rows, "/a", "js")["code"], "lai")
        self.assertEqual(self.find(rows, "/a", "Dịch vụ")["code"], "lai")
        self.assertEqual(self.find(rows, "/a", "Rỗng")["code"], "lỗi")

    def test_audit_ban_phim_va_noopener(self):
        _, rows = self.inv()
        self.assertIn("thieu_ban_phim", self.find(rows, "/a", "Đội ngũ")["flags"])
        self.assertNotIn("thieu_ban_phim", self.find(rows, "/a", "Tuyển")["flags"])
        self.assertEqual(self.find(rows, "/a", "Đội ngũ")["code"], "D4")
        self.assertEqual(self.find(rows, "/a", "Liên hệ")["code"], "D3")
        mo = self.find(rows, "/a", "Bản đồ")
        self.assertEqual(mo["code"], "D5")
        self.assertIn("thieu_noopener", mo["flags"])
        self.assertIn("thieu_noopener", self.find(rows, "/a", "ngoài")["flags"])

    def test_audit_noindex_tu_meta_va_gz(self):
        _, rows = self.inv()
        r = self.find(rows, "/a", "tới b")
        self.assertEqual(r["tkind"], "internal")
        self.assertIn("link_that_toi_noindex", r["flags"])

    def test_audit_dich_chi_co_link_js(self):
        _, rows = self.inv()
        self.assertIn("doch_chi_co_link_js", self.find(rows, "/a", "Liên hệ")["flags"])
        self.assertIn("doch_chi_co_link_js", self.find(rows, "/a", "Đội ngũ")["flags"])
        self.assertEqual(sum("doch_chi_co_link_js" in r["flags"] for r in rows if r["target"] == "/d/"), 0)

    def test_audit_vung_va_zone(self):
        _, rows = self.inv()
        self.assertEqual(self.find(rows, "/a", "Giới thiệu")["region"], "header")
        self.assertEqual(self.find(rows, "/a", "Chính sách")["region"], "footer")
        self.assertEqual(self.find(rows, "/a", "trang")["zone"], "MC")
        self.assertEqual(self.find(rows, "/a", "e")["zone"], "MC")
        self.assertEqual(self.find(rows, "/a", "f")["zone"], "SC")
        self.assertEqual(self.find(rows, "/a", "g")["zone"], "SC")

    def test_audit_anchor_long_span_img_va_p_khong_dong(self):
        _, rows = self.inv()
        r = self.find(rows, "/a", "trang")
        self.assertEqual(r["alt"], "bê")
        self.assertEqual(r["tkind"], "internal")
        self.assertEqual(r["target"], "/b")

    def test_audit_template_gop_mot_dong(self):
        out, _ = self.inv()
        lines = lines_of(out / "templates.tsv")
        row = [l for l in lines if "/chinh-sach" in l]
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].split("\t")[4], "3")

    def test_audit_khong_ghi_neu_khong_out(self):
        before = sorted(os.listdir(self.tmp.name))
        rc, out, _ = run(LA, ["scan", str(self.d), "--host", "vidu.vn"])
        self.assertEqual(rc, 0)
        self.assertIn("Chưa ghi file", out)
        self.assertEqual(sorted(os.listdir(self.tmp.name)), before)

    def test_audit_fail_on_flags_va_loi_dau_vao(self):
        self.assertEqual(run(LA, ["scan", str(self.d), "--fail-on-flags"])[0], 3)
        self.assertEqual(run(LA, ["scan", str(Path(self.tmp.name) / "khong-co")])[0], 1)
        empty = Path(self.tmp.name) / "trong"
        empty.mkdir()
        self.assertEqual(run(LA, ["scan", str(empty)])[0], 1)
        self.assertEqual(run(LA, ["scan", str(self.d), "--region", "sai"])[0], 2)

    def test_audit_region_rieng(self):
        (self.d / "d.html").write_text('<html><body><ul class="mega-sub-menu"><li><a href="/x/">X</a></li></ul></body></html>',
                                       encoding="utf-8")
        out = Path(self.tmp.name) / "o2"
        run(LA, ["scan", str(self.d), "--region", "mega menu=mega-sub-menu", "--out", str(out)])
        rows = jsonl(out / "inventory.jsonl")
        self.assertEqual(self.find(rows, "/d", "X")["region"], "mega menu")

    def test_compare_body_giam(self):
        out, _ = self.inv()
        (self.d / "a.html").write_text(A_HTML.replace('<a href="/b/">tới b</a>', '<span onclick="location.href=\'/b/\'">tới b</span>'),
                                       encoding="utf-8")
        out2 = Path(self.tmp.name) / "out2"
        run(LA, ["scan", str(self.d), "--host", "vidu.vn", "--out", str(out2)])
        rc, text, _ = run(LA, ["compare", str(out / "summary.json"), str(out2 / "summary.json")])
        self.assertEqual(rc, 3)
        self.assertIn("BODY GIẢM /a", text)
        self.assertEqual(run(LA, ["compare", str(out / "summary.json"), str(out2 / "summary.json"), "--allow-body-drop"])[0], 0)
        self.assertEqual(run(LA, ["compare", str(out / "summary.json"), str(out / "summary.json")])[0], 0)
        self.assertEqual(run(LA, ["compare", str(out / "x.json"), str(out / "summary.json")])[0], 1)

    def test_help(self):
        rc, out, _ = run(LA, ["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("scan", out)
        self.assertEqual(run(LA, [])[0], 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
