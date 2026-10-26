"""Test offline bộ script dọn HTML thừa: cruft_scan.py, cruft_clean.py, export_cruft.php, compare_autop.php, apply_cruft.php, rollback_cruft.php.
Chạy: python3 -B tests/test_cruft.py   (cần php CLI)
PHP chạy với WordPress giả (tests/php/run_cruft.php) có wpautop bản port.
Ca hỏng thật:
- 19/10 10:49-10:55 (6cae27d5-11): áp lên 130 bài, bài seo-global-la-gi đổi bố cục từ y≈4876 vì gỡ <span> chỉ chứa xuống dòng.
  compare_autop báo 55/130 bài khác cấu trúc, sửa luật còn 0/126, rollback 10:52.
- Cùng đợt: ghi theo md5 của bản export, bài đã đổi sau lúc xuất phải bị bỏ qua.
- Rollback không được chép đè bài mà phiên khác đã sửa sau lượt ghi (ghi-an-toan.md mục 5).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
RUNNER = HERE / "php" / "run_cruft.php"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def w(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False))


def py(script, *args):
    p = subprocess.run([sys.executable, "-I", str(SCRIPTS / script)] + [str(a) for a in args], capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr


# Bài classic dán từ Google Docs, có xuống dòng CRLF và span chỉ chứa xuống dòng (ca hỏng 19/10).
POST1 = ('<p><span style="font-weight: 400;">Dịch vụ SEO tổng thể</span> cho doanh nghiệp.</p>\r\n'
         '<p dir="ltr" aria-level="2"><span style="font-weight: 400;">Đoạn hai.</span></p>\r\n'
         '<p>&nbsp;</p>\r\n'
         'Dòng một\r\n<span style="font-weight: 400;">\r\n</span>Dòng hai\r\n\r\nĐoạn ba.')
EL = [{"id": "a1", "elType": "widget", "widgetType": "text-editor", "elements": [],
       "settings": {"editor": '<p><span style="font-weight: 400;">Chữ trong Elementor</span>&nbsp;</p>\n<p>Đoạn khác.</p>'}}]
POST2_EL = json.dumps(EL, ensure_ascii=False, separators=(",", ":"))
POST3 = '<!-- wp:paragraph -->\n<p><span style="font-weight: 400;">Khối Gutenberg</span></p>\n<!-- /wp:paragraph -->'
META = '<p><span style="font-weight: 400;">Mô tả ACF</span></p>\n<p>&nbsp;</p>'
WIDGET = {"2": {"title": "T", "text": '<span style="font-weight: 400;">Chữ widget</span>', "filter": True}, "_multiwidget": 1}


def make_store():
    return {
        "posts": {
            "1": {"ID": 1, "post_content": POST1, "post_type": "post", "post_name": "bai-mot", "post_status": "publish"},
            "2": {"ID": 2, "post_content": "Mô tả ngắn.", "post_type": "page", "post_name": "trang-elementor", "post_status": "publish"},
            "3": {"ID": 3, "post_content": POST3, "post_type": "post", "post_name": "bai-gutenberg", "post_status": "publish"},
            "4": {"ID": 4, "post_content": "<p>Đã sạch.</p>", "post_type": "post", "post_name": "da-sach", "post_status": "publish"},
        },
        "meta": {"2": {"_elementor_data": POST2_EL}},
        "postmeta_rows": {"77": {"post_id": 1, "meta_key": "mo_ta", "meta_value": META}},
        "options": {"widget_text": WIDGET},
        "export_posts_pages": [[
            {"ID": 1, "post_type": "post", "post_name": "bai-mot", "post_content": POST1, "el": None},
            {"ID": 2, "post_type": "page", "post_name": "trang-elementor", "post_content": "Mô tả ngắn.", "el": POST2_EL},
            {"ID": 3, "post_type": "post", "post_name": "bai-gutenberg", "post_content": POST3, "el": None},
        ], []],
        "export_meta_rows": [{"meta_id": 77, "post_id": 1, "meta_key": "mo_ta", "meta_value": META}],
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)

    def tearDown(self):
        self.t.cleanup()

    def php(self, script, store, **env):
        e = {k: v for k, v in os.environ.items() if k not in ("CHANGES", "CMP", "BK", "OUT", "LOG", "DRY", "LIMIT")}
        e.update({k: str(v) for k, v in env.items()})
        w(self.d / "store.json", store)
        so = self.d / "store_out.json"
        if so.exists():
            so.unlink()
        p = subprocess.run(["php", str(RUNNER), str(SCRIPTS / script), str(self.d / "store.json"), str(so)],
                           capture_output=True, text=True, env=e, timeout=120)
        return p.returncode, p.stdout, p.stderr, json.loads(so.read_text(encoding="utf-8")) if so.exists() else None


class Scan(Base):
    def test_dem_mau_rac_tu_file_local(self):
        w(self.d / "h" / "a.html", '<p><span style="font-weight: 400;">x</span>&nbsp;</p><p></p><p dir="ltr" aria-level="1">a &amp;amp; b</p><!-- c -->')
        w(self.d / "h" / "b.html", "<p>sạch</p>")
        rc, out, err = py("cruft_scan.py", self.d / "h", "--out", self.d / "scan.jsonl")
        self.assertEqual(rc, 0, err)
        rows = [json.loads(l) for l in (self.d / "scan.jsonl").read_text(encoding="utf-8").splitlines()]
        a = next(r for r in rows if r["u"].endswith("a.html"))
        self.assertEqual((a["dbl_amp"], a["gdocs_fw400"], a["aria_level"], a["dir_ltr"], a["p_empty"], a["comments"]), (1, 1, 1, 1, 1, 1))
        b = next(r for r in rows if r["u"].endswith("b.html"))
        self.assertEqual((b["dbl_amp"], b["p_empty"]), (0, 0))

    def test_khong_ghi_de_va_so_sanh(self):
        w(self.d / "h" / "a.html", "<p>&nbsp;</p>")
        args = (self.d / "h", "--out", self.d / "s.jsonl")
        self.assertEqual(py("cruft_scan.py", *args)[0], 0)
        self.assertEqual(py("cruft_scan.py", *args)[0], 2)
        w(self.d / "h" / "a.html", "<p>x</p>")
        self.assertEqual(py("cruft_scan.py", self.d / "h", "--out", self.d / "s2.jsonl")[0], 0)
        rc, out, err = py("cruft_scan.py", "--diff", self.d / "s.jsonl", self.d / "s2.jsonl")
        self.assertEqual(rc, 0)
        self.assertIn("p_empty", out)

    def test_nguon_loi_thoat_1(self):
        w(self.d / "u.txt", str(self.d / "khong-co.html") + "\n")
        rc, out, err = py("cruft_scan.py", self.d / "u.txt", "--out", self.d / "s.jsonl")
        self.assertEqual(rc, 1)

    def test_help(self):
        for s in ("cruft_scan.py", "cruft_clean.py"):
            rc, out, err = py(s, "--help")
            self.assertEqual(rc, 0)


class Clean(Base):
    def export(self, **kw):
        d = {"posts": [{"id": "1", "type": "post", "slug": "bai-mot", "content": POST1, "el": None, "md5c": md5(POST1), "md5e": md5("")},
                       {"id": "2", "type": "page", "slug": "trang-elementor", "content": "Mô tả ngắn.", "el": POST2_EL,
                        "md5c": md5("Mô tả ngắn."), "md5e": md5(POST2_EL)},
                       {"id": "3", "type": "post", "slug": "bai-gutenberg", "content": POST3, "el": None, "md5c": md5(POST3), "md5e": md5("")}],
             "meta": [{"meta_id": 77, "post_id": 1, "key": "mo_ta", "value": META, "md5": md5(META)}],
             "options": [{"key": "widget_text", "value": WIDGET, "md5": md5(json.dumps(WIDGET, ensure_ascii=False))}]}
        d.update(kw)
        w(self.d / "export.json", d)
        return self.d / "export.json"

    def test_don_rac_va_giu_md5_goc(self):
        rc, out, err = py("cruft_clean.py", self.export(), self.d / "run")
        self.assertEqual(rc, 0, out + err)
        ch = json.loads((self.d / "run" / "changes.json").read_text(encoding="utf-8"))
        kinds = sorted((c["kind"], str(c.get("id", c.get("meta_id", c.get("key"))))) for c in ch)
        self.assertEqual(kinds, [("meta", "77"), ("option", "widget_text"), ("post", "1"), ("post", "2"), ("post", "3")])
        p1 = next(c for c in ch if c["kind"] == "post" and c["id"] == "1")
        self.assertEqual((p1["md5c"], p1["md5e"]), (md5(POST1), md5("")))
        self.assertNotIn("font-weight", p1["content"])
        self.assertNotIn("aria-level", p1["content"])
        self.assertLess(p1["bytes_after"], p1["bytes_before"])
        p2 = next(c for c in ch if c["kind"] == "post" and c["id"] == "2")
        self.assertIsNone(p2["content"])
        self.assertNotIn("font-weight", p2["el"])
        self.assertEqual((self.d / "run" / "rejected.json").read_text(encoding="utf-8").strip(), "[]")

    def test_span_chi_chua_xuong_dong_duoc_giu_vi_wpautop(self):
        # ca hỏng 19/10: gỡ span này làm hai xuống dòng dính nhau, wpautop đổi thành ngắt đoạn và bố cục lệch.
        cc = load("cruft_clean")
        new = cc.clean_html(POST1, autop=True)
        self.assertEqual(cc.check_pair(POST1, new, True), [])
        naive = POST1.replace('<span style="font-weight: 400;">\r\n</span>', "")
        bad = cc.check_pair(POST1, naive, True)
        self.assertIn("cau_truc", bad)

    def test_bat_bien_bi_pha_thi_loai_va_thoat_1(self):
        cc = load("cruft_clean")
        naive = POST1.replace('<span style="font-weight: 400;">\r\n</span>', "")
        with mock.patch.object(cc, "clean_html", lambda h, *a, **k: naive if h == POST1 else h):
            rc = cc.main([str(self.export(posts=[{"id": "1", "type": "post", "slug": "bai-mot", "content": POST1, "el": None,
                                                  "md5c": md5(POST1), "md5e": md5("")}], meta=[], options=[])), str(self.d / "run")])
        self.assertEqual(rc, 1)
        rej = json.loads((self.d / "run" / "rejected.json").read_text(encoding="utf-8"))
        self.assertEqual((rej[0]["id"], rej[0]["vi_pham"]), ("1", ["cau_truc"]))
        self.assertEqual(json.loads((self.d / "run" / "changes.json").read_text(encoding="utf-8")), [])

    def test_chu_hien_thi_khong_doi(self):
        cc = load("cruft_clean")
        for h in (POST1, POST3, META, EL[0]["settings"]["editor"]):
            new = cc.clean_html(h, autop=True)
            self.assertEqual(cc.visible(new), cc.visible(h))

    def test_nbsp_giua_chu_so_vao_jev_va_ap_quyet_dinh(self):
        content = "<p>Giá từ 10&nbsp;triệu đồng</p>"
        ex = self.export(posts=[{"id": "9", "type": "post", "slug": "gia", "content": content, "el": None, "md5c": md5(content), "md5e": md5("")}],
                         meta=[], options=[])
        rc, out, err = py("cruft_clean.py", ex, self.d / "r1", "--emit-jev")
        self.assertEqual(rc, 0, err)
        rows = [json.loads(l) for l in (self.d / "r1" / "jev_nbsp_in.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertIn("NBSP", rows[0]["state"]["snippet"])
        self.assertEqual(json.loads((self.d / "r1" / "changes.json").read_text(encoding="utf-8")), [])
        w(self.d / "jev.jsonl", json.dumps({"id": rows[0]["id"], "intent": "plain_space"}) + "\n")
        rc, out, err = py("cruft_clean.py", ex, self.d / "r2", "--jev-nbsp", self.d / "jev.jsonl")
        self.assertEqual(rc, 0, err)
        ch = json.loads((self.d / "r2" / "changes.json").read_text(encoding="utf-8"))
        self.assertEqual(ch[0]["content"], "<p>Giá từ 10 triệu đồng</p>")

    def test_khong_ghi_de_ket_qua_cu(self):
        ex = self.export()
        self.assertEqual(py("cruft_clean.py", ex, self.d / "run")[0], 0)
        self.assertEqual(py("cruft_clean.py", ex, self.d / "run")[0], 2)
        self.assertEqual(py("cruft_clean.py", ex, self.d / "run", "--force")[0], 0)
        self.assertEqual(py("cruft_clean.py", self.d / "khong-co.json", self.d / "run2")[0], 2)


class Pipeline(Base):
    """export_cruft.php -> cruft_clean.py -> compare_autop.php -> apply_cruft.php -> rollback_cruft.php."""

    def setUp(self):
        super().setUp()
        self.store = make_store()
        rc, out, err, st = self.php("export_cruft.php", self.store, OUT=self.d / "export.json")
        self.assertEqual(rc, 0, out + err)
        rc, out, err = py("cruft_clean.py", self.d / "export.json", self.d / "run")
        self.assertEqual(rc, 0, out + err)
        self.changes = self.d / "run" / "changes.json"

    def compare(self, store=None, changes=None):
        return self.php("compare_autop.php", store or self.store, CHANGES=changes or self.changes, OUT=self.d / "cmp.json")

    def test_export_dung_md5_va_bo_bai_da_sach(self):
        ex = json.loads((self.d / "export.json").read_text(encoding="utf-8"))
        self.assertEqual([p["id"] for p in ex["posts"]], ["1", "2", "3"])
        self.assertEqual(ex["posts"][0]["md5c"], md5(POST1))
        self.assertIsNone(ex["posts"][0]["el"])
        self.assertEqual(ex["posts"][1]["md5e"], md5(POST2_EL))
        self.assertEqual(ex["meta"][0]["md5"], md5(META))
        self.assertEqual(ex["options"][0]["key"], "widget_text")

    def test_export_khong_ghi_de(self):
        rc, out, err, st = self.php("export_cruft.php", self.store, OUT=self.d / "export.json")
        self.assertEqual(rc, 2)
        rc, out, err, st = self.php("export_cruft.php", self.store)
        self.assertEqual(rc, 2)

    def test_compare_dat_khi_luat_dung(self):
        rc, out, err, st = self.compare()
        self.assertEqual(rc, 0, out + err)
        cmp = json.loads((self.d / "cmp.json").read_text(encoding="utf-8"))
        self.assertEqual(cmp["bad"], 0)
        self.assertEqual(cmp["changes_md5"], hashlib.md5(self.changes.read_bytes()).hexdigest())

    def test_compare_bat_ca_span_xuong_dong(self):
        # ca 19/10: 55/130 bài khác cấu trúc. Dựng changes theo kiểu gỡ span xuống dòng rồi kiểm.
        ch = json.loads(self.changes.read_text(encoding="utf-8"))
        p1 = next(c for c in ch if c["kind"] == "post" and c["id"] == "1")
        p1["content"] = POST1.replace('<span style="font-weight: 400;">\r\n</span>', "").replace('<span style="font-weight: 400;">', "").replace("</span>", "")
        w(self.d / "naive.json", ch)
        rc, out, err, st = self.compare(changes=self.d / "naive.json")
        self.assertEqual(rc, 1, out + err)
        cmp = json.loads((self.d / "cmp.json").read_text(encoding="utf-8"))
        self.assertEqual(cmp["bad"], 1)
        self.assertEqual(cmp["diffs"][0]["label"], "bai-mot")

    def test_apply_mac_dinh_chay_thu_khong_ghi(self):
        rc, out, err, st = self.php("apply_cruft.php", self.store, CHANGES=self.changes, OUT=self.d / "dry.json")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("chạy thử: khớp 5", out)
        self.assertEqual(st["posts"]["1"]["post_content"], POST1)
        self.assertFalse([c for c in st["calls"] if c.startswith(("wpdb_update", "update_post_meta", "update_option"))])
        self.assertEqual(json.loads((self.d / "dry.json").read_text(encoding="utf-8"))["would_apply"], 5)

    def test_ghi_that_can_cmp_dat_va_backup(self):
        # thiếu CMP
        rc, out, err, st = self.php("apply_cruft.php", self.store, CHANGES=self.changes, DRY=0, BK=self.d / "bk.json")
        self.assertEqual(rc, 2)
        self.assertEqual(st["posts"]["1"]["post_content"], POST1)
        # CMP có bad > 0
        w(self.d / "cmp.json", {"bad": 3, "changes_md5": hashlib.md5(self.changes.read_bytes()).hexdigest()})
        rc, out, err, st = self.php("apply_cruft.php", self.store, CHANGES=self.changes, CMP=self.d / "cmp.json", DRY=0, BK=self.d / "bk.json")
        self.assertEqual(rc, 2)
        # CMP của file changes khác
        w(self.d / "cmp.json", {"bad": 0, "changes_md5": "0" * 32})
        rc, out, err, st = self.php("apply_cruft.php", self.store, CHANGES=self.changes, CMP=self.d / "cmp.json", DRY=0, BK=self.d / "bk.json")
        self.assertEqual(rc, 2)
        self.assertFalse((self.d / "bk.json").exists())

    def good_apply(self, store=None):
        self.assertEqual(self.compare(store)[0], 0)
        return self.php("apply_cruft.php", store or self.store, CHANGES=self.changes, CMP=self.d / "cmp.json", DRY=0,
                        BK=self.d / "bk.json", OUT=self.d / "log.json")

    def test_ghi_that_dung_noi_dung_va_backup(self):
        rc, out, err, st = self.good_apply()
        self.assertEqual(rc, 0, out + err)
        ch = json.loads(self.changes.read_text(encoding="utf-8"))
        p1 = next(c for c in ch if c["kind"] == "post" and c["id"] == "1")
        self.assertEqual(st["posts"]["1"]["post_content"], p1["content"])
        self.assertNotIn("font-weight", st["posts"]["1"]["post_content"])
        self.assertIn("\r\n", st["posts"]["1"]["post_content"])
        self.assertNotIn("font-weight", st["meta"]["2"]["_elementor_data"])
        self.assertEqual(json.loads(st["meta"]["2"]["_elementor_data"])[0]["settings"]["editor"].count("Chữ trong Elementor"), 1)
        self.assertNotIn("font-weight", st["postmeta_rows"]["77"]["meta_value"])
        self.assertNotIn("font-weight", json.dumps(st["options"]["widget_text"], ensure_ascii=False))
        self.assertEqual(st["options"]["widget_text"]["_multiwidget"], 1)
        self.assertEqual(st["posts"]["4"]["post_content"], "<p>Đã sạch.</p>")
        bk = json.loads((self.d / "bk.json").read_text(encoding="utf-8"))
        self.assertEqual(next(b for b in bk if b["kind"] == "post" and b["id"] == "1")["content"], POST1)
        self.assertIn("wp_cache_flush", st["calls"])
        # backup đã có thì không ghi đè
        rc, out, err, st = self.php("apply_cruft.php", self.store, CHANGES=self.changes, CMP=self.d / "cmp.json", DRY=0, BK=self.d / "bk.json")
        self.assertEqual(rc, 2)

    def test_bai_da_doi_sau_luc_xuat_bi_bo_qua(self):
        # md5 khác lúc xuất: phiên khác đã sửa bài 1 giữa chừng. Phải skip, không ghi đè.
        changed = make_store()
        changed["posts"]["1"]["post_content"] = POST1 + "\r\nCâu phiên khác vừa thêm."
        # compare_autop cũng sẽ báo khác cấu trúc vì live đổi; ở đây giả lập cổng đã qua để kiểm riêng cổng md5 của apply.
        w(self.d / "cmp.json", {"bad": 0, "changes_md5": hashlib.md5(self.changes.read_bytes()).hexdigest()})
        self.assertEqual(self.compare(changed)[0], 1)
        w(self.d / "cmp.json", {"bad": 0, "changes_md5": hashlib.md5(self.changes.read_bytes()).hexdigest()})
        rc, out, err, st = self.php("apply_cruft.php", changed, CHANGES=self.changes, CMP=self.d / "cmp.json", DRY=0,
                                    BK=self.d / "bk.json", OUT=self.d / "log.json")
        self.assertEqual(rc, 1)
        self.assertIn("skip post 1", out)
        self.assertTrue(st["posts"]["1"]["post_content"].endswith("Câu phiên khác vừa thêm."))
        self.assertIn("font-weight", st["posts"]["1"]["post_content"])
        self.assertNotIn("font-weight", st["posts"]["3"]["post_content"])
        log = json.loads((self.d / "log.json").read_text(encoding="utf-8"))
        self.assertNotIn("1", [a["id"] for a in log["applied"] if a["kind"] == "post"])

    def test_rollback_tra_ve_dung_ban_goc(self):
        rc, out, err, applied = self.good_apply()
        self.assertEqual(rc, 0, out + err)
        rc, out, err, st = self.php("rollback_cruft.php", applied, BK=self.d / "bk.json", LOG=self.d / "log.json")  # mặc định chạy thử
        self.assertEqual(rc, 0, out + err)
        self.assertIn("chạy thử: 5 mục trả được", out)
        self.assertNotIn("font-weight", st["posts"]["1"]["post_content"])
        rc, out, err, st = self.php("rollback_cruft.php", applied, BK=self.d / "bk.json", LOG=self.d / "log.json", DRY=0)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(st["posts"]["1"]["post_content"], POST1)
        self.assertEqual(st["posts"]["3"]["post_content"], POST3)
        self.assertEqual(st["meta"]["2"]["_elementor_data"], POST2_EL)
        self.assertEqual(st["postmeta_rows"]["77"]["meta_value"], META)
        self.assertEqual(st["options"]["widget_text"], WIDGET)

    def test_rollback_khong_chep_de_bai_phien_khac_da_sua(self):
        rc, out, err, applied = self.good_apply()
        applied["posts"]["1"]["post_content"] += "\r\nCâu phiên khác thêm sau khi ghi."
        rc, out, err, st = self.php("rollback_cruft.php", applied, BK=self.d / "bk.json", LOG=self.d / "log.json", DRY=0)
        self.assertEqual(rc, 1)
        self.assertIn("đã đổi sau khi ghi, không chép đè: post:1", out)
        self.assertTrue(st["posts"]["1"]["post_content"].endswith("Câu phiên khác thêm sau khi ghi."))
        self.assertEqual(st["posts"]["3"]["post_content"], POST3)

    def test_thieu_dau_vao_thoat_2(self):
        for s in ("compare_autop.php", "apply_cruft.php", "rollback_cruft.php"):
            rc, out, err, st = self.php(s, self.store)
            self.assertEqual(rc, 2, s)


if __name__ == "__main__":
    unittest.main()
