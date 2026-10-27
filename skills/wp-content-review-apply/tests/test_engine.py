"""Test offline apply.php và locate.php bằng WordPress giả (tests/php/run_engine.php).
Chạy: python3 -B tests/test_engine.py   (cần php CLI có intl)
Mỗi ca chạy một tiến trình PHP riêng, trong phạm vi hàm như `wp eval-file`.
Ca hỏng thật:
- 17/10: bản chạy thử báo 227 'không thấy' vì hàm dùng biến cấp file như biến toàn cục (ca scope_eval_file).
- 18/10: đường dẫn Elementor sai tạo khoá null rác trong dữ liệu ghi (ca elementor_path_sai).
- Chữ DB có NBSP, NFD và \\r\\n, chữ cũ lấy từ file không khớp (ca nbsp_nfd_crlf).
"""
import json
import os
import subprocess
import tempfile
import unicodedata
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
RUNNER = HERE / "php" / "run_engine.php"


def run_php(script, store, plan=None, env=None, as_file=None):
    """Trả (mã thoát, stdout, stderr, store sau khi chạy, nội dung OUT hoặc None)."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "store.json").write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
        e = dict(os.environ)
        for k in ("PLAN", "DRY", "OUT", "SRC", "PURGE", "FAIL_ON_SKIP", "NEEDLES", "FLUSH"):
            e.pop(k, None)
        if plan is not None:
            (d / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            e["PLAN"] = str(d / "plan.json")
        e["OUT"] = str(d / "out.json")
        e.update(env or {})
        if as_file:
            for name, content in as_file.items():
                (d / name).write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
                e[name.split(".")[0].upper()] = str(d / name)
        p = subprocess.run(["php", str(RUNNER), str(SCRIPTS / script), str(d / "store.json"), str(d / "store_out.json")],
                           capture_output=True, text=True, env=e, timeout=60)
        so = d / "store_out.json"
        store_after = json.loads(so.read_text(encoding="utf-8")) if so.exists() else None
        out = Path(e["OUT"]) if e.get("OUT") else None
        log = json.loads(out.read_text(encoding="utf-8")) if out and out.exists() else None
        return p.returncode, p.stdout, p.stderr, store_after, log


def apply(store, ops, dry=False, **kw):
    env = {"DRY": "1" if dry else "0", "PURGE": "0"}
    env.update(kw.pop("env", {}))
    return run_php("apply.php", store, {"ops": ops}, env=env, **kw)


def widget(wid, settings, children=None):
    w = {"id": wid, "elType": "widget", "widgetType": "text-editor", "settings": settings, "elements": []}
    if children is not None:
        w = {"id": wid, "elType": "container", "settings": settings or {"layout": "boxed"}, "elements": children}
    return w


def el_store(data, post=10):
    return {"posts": {str(post): {"post_content": "", "post_title": "T", "post_name": "t"}},
            "meta": {str(post): {"_elementor_data": json.dumps(data, ensure_ascii=False)}}}


def el_after(store, post=10):
    return json.loads(store["meta"][str(post)]["_elementor_data"])


class ElementorPath(unittest.TestCase):
    DATA = [widget("c1", {}, [
        widget("w1", {"editor": "Dịch vụ SEO tốt", "title": "Tiêu đề", "list": [{"t": "a"}, {"t": "b"}]}),
        widget("w2", {"editor": "Không đụng tới"}),
    ])]

    def test_elementor_path_sai_khong_tao_khoa_null(self):
        """Lỗi 18/10: path sai làm $slot = &$slot[$k] tạo khoá null. Op đúng và op sai cùng một bài."""
        ops = [
            {"item": "x1", "post": 10, "target": "elementor:w1:khong_co.sau.hon", "before": "", "value": "RAC"},
            {"item": "x2", "post": 10, "target": "elementor:w1:editor", "before": "Dịch vụ SEO tốt", "value": "Dịch vụ SEO & GEO"},
        ]
        rc, _, err, st, log = apply(el_store(self.DATA), ops)
        self.assertEqual(rc, 0, err)
        self.assertEqual([s[1] for s in log["skip"]], ["không thấy đường dẫn"])
        after = el_after(st)
        self.assertEqual(after[0]["elements"][0]["settings"]["editor"], "Dịch vụ SEO & GEO")
        expected = json.loads(json.dumps(self.DATA))
        expected[0]["elements"][0]["settings"]["editor"] = "Dịch vụ SEO & GEO"
        self.assertEqual(after, expected)  # phần không chạm giữ nguyên
        self.assertNotIn("khong_co", json.dumps(after))
        self.assertNotIn("null", json.dumps(after))
        md5_w2 = lambda d: json.dumps(d[0]["elements"][1], sort_keys=True)
        self.assertEqual(md5_w2(after), md5_w2(self.DATA))

    def test_chi_op_sai_thi_khong_ghi_elementor(self):
        ops = [{"item": "x1", "post": 10, "target": "elementor:w1:khong_co.sau.hon", "before": "", "value": "RAC"}]
        rc, _, _, st, log = apply(el_store(self.DATA), ops)
        self.assertEqual(rc, 0)
        self.assertEqual(el_after(st), self.DATA)
        self.assertNotIn("update_post_meta:10:_elementor_data", st["calls"])

    def test_op_cu_khoa_la_cuoi_thieu_duoc_khi_before_trong(self):
        ops = [{"item": "x1", "post": 10, "target": "elementor:w2:subtitle", "before": "", "value": "Mới"}]
        rc, _, _, st, log = apply(el_store(self.DATA), ops)
        self.assertEqual(el_after(st)[0]["elements"][1]["settings"]["subtitle"], "Mới")


class ObjectCache(unittest.TestCase):
    """27/10/2026: bản bỏ wp_cache_flush() làm cache mảnh của mu-plugin bám save_post giữ chữ cũ, vì apply.php ghi bằng $wpdb."""
    OPS = [{"item": "x1", "post": 10, "target": "elementor:w1:editor", "before": "A", "value": "B"}]

    def store(self):
        return el_store([widget("w1", {"editor": "A"})])

    def test_mac_dinh_xoa_object_cache(self):
        rc, _, err, st, _ = apply(self.store(), self.OPS)
        self.assertEqual(rc, 0, err)
        self.assertIn("wp_cache_flush", st["calls"])

    def test_flush_0_khong_xoa(self):
        rc, _, err, st, _ = apply(self.store(), self.OPS, env={"FLUSH": "0"})
        self.assertEqual(rc, 0, err)
        self.assertNotIn("wp_cache_flush", st["calls"])
        self.assertEqual(el_after(st)[0]["settings"]["editor"], "B")


class TextTarget(unittest.TestCase):
    def post_store(self, content):
        return {"posts": {"5": {"post_content": content, "post_title": "T", "post_name": "t"}}, "meta": {}}

    def text_op(self, **kw):
        op = {"item": "t1", "post": 5, "target": "text", "field": "post_content"}
        op.update(kw)
        return op

    def test_nbsp_nfd_crlf(self):
        """DB có NBSP, NFD, CRLF. Chữ cũ gõ bằng dấu cách thường, NFC, LF vẫn khớp đúng 1 vị trí."""
        db = unicodedata.normalize("NFD", "Chúng tôi là agency SEO\r\nhàng đầu Việt Nam.")
        rc, _, err, st, log = apply(self.post_store(db), [self.text_op(old="agency SEO hàng đầu", new="agency SEO & GEO")])
        self.assertEqual(rc, 0, err)
        self.assertEqual(log["skip"], [], log)
        got = st["posts"]["5"]["post_content"]
        self.assertEqual(got, "Chúng tôi là agency SEO & GEO Việt Nam.")
        self.assertTrue(unicodedata.is_normalized("NFC", got))
        self.assertIn("5", {str(k) for k in log["before"]["values"]})
        self.assertEqual(log["before"]["values"]["5"]["post_content"], db)  # before giữ nguyên bản gốc để rollback

    def test_khop_nhieu_vi_tri_phai_dung(self):
        db = "Xem thêm A. Xem thêm B. Xem thêm C."
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Xem thêm", new="Đọc thêm")])
        self.assertEqual(st["posts"]["5"]["post_content"], db)
        self.assertIn("khớp 3 vị trí", log["skip"][0][1])

    def test_ctx_nth_multi(self):
        db = "Xem thêm A. Xem thêm B. Xem thêm C."
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Xem thêm", new="Đọc thêm", ctx_phai="B.")])
        self.assertEqual(st["posts"]["5"]["post_content"], "Xem thêm A. Đọc thêm B. Xem thêm C.")
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Xem thêm", new="Đọc thêm", nth=3)])
        self.assertEqual(st["posts"]["5"]["post_content"], "Xem thêm A. Xem thêm B. Đọc thêm C.")
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Xem thêm", new="Đọc thêm", multi=True, count=3)])
        self.assertEqual(st["posts"]["5"]["post_content"], "Đọc thêm A. Đọc thêm B. Đọc thêm C.")
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Xem thêm", new="Đọc thêm", multi=True, count=2)])
        self.assertEqual(st["posts"]["5"]["post_content"], db)
        self.assertIn("cần 2", log["skip"][0][1])

    def test_ap_hai_lan_khong_nhan_doi(self):
        """new chứa old: chạy lại không được áp lần hai."""
        db = "Dịch vụ SEO rất tốt."
        op = self.text_op(old="SEO", new="SEO & GEO")
        rc, _, _, st, log = apply(self.post_store(db), [op])
        once = st["posts"]["5"]["post_content"]
        self.assertEqual(once, "Dịch vụ SEO & GEO rất tốt.")
        rc, _, _, st2, log2 = apply(self.post_store(once), [op])
        self.assertEqual(st2["posts"]["5"]["post_content"], once)
        self.assertEqual(log2["skip"], [])
        self.assertIn("(đã đúng)", log2["ok"][0])

    def test_khong_thay_chu_cu(self):
        rc, _, _, st, log = apply(self.post_store("Nội dung khác hẳn."), [self.text_op(old="không có đâu", new="x")])
        self.assertIn("không thấy chữ cũ", log["skip"][0][1])

    def test_hai_op_cung_truong_noi_tiep(self):
        db = "Alpha beta gamma."
        ops = [self.text_op(old="Alpha", new="Một"), self.text_op(old="gamma", new="ba")]
        rc, _, _, st, log = apply(self.post_store(db), ops)
        self.assertEqual(st["posts"]["5"]["post_content"], "Một beta ba.")
        self.assertEqual(st["calls"].count("wpdb_update:5"), 1)  # ghi một lần

    def test_dry_khong_ghi(self):
        db = "Alpha beta."
        rc, _, _, st, log = apply(self.post_store(db), [self.text_op(old="Alpha", new="Một")], dry=True)
        self.assertEqual(st["posts"]["5"]["post_content"], db)
        self.assertTrue(log["dry"])
        self.assertEqual(len(log["ok"]), 1)
        self.assertIn("md5_after", log)

    def test_meta_wp_slash_giu_dau_gach_cheo(self):
        store = {"posts": {"5": {"post_content": "", "post_title": "", "post_name": ""}},
                 "meta": {"5": {"rank_math_title": "A \\ B cũ %sep%"}}}
        op = self.text_op(field="meta:rank_math_title", old="cũ", new="mới")
        rc, _, _, st, log = apply(store, [op])
        self.assertEqual(st["meta"]["5"]["rank_math_title"], "A \\ B mới %sep%")

    def test_usermeta_va_option(self):
        store = {"posts": {}, "usermeta": {"3": {"description": "Tiểu sử cũ của tác giả"}},
                 "options": {"blogdescription": "Mô tả cũ", "cau_hinh": {"a": {"b": "chữ cũ"}}}}
        ops = [
            {"item": "u", "target": "text", "field": "usermeta:3:description", "old": "cũ", "new": "mới"},
            {"item": "o", "target": "fix", "field": "option:blogdescription", "old": "Mô tả cũ", "new": "Mô tả mới"},
            {"item": "p", "target": "text", "field": "option:cau_hinh:a.b", "old": "cũ", "new": "mới"},
            {"item": "q", "target": "text", "field": "option:cau_hinh:a.khong_co", "old": "x", "new": "y"},
        ]
        rc, _, err, st, log = apply(store, ops)
        self.assertEqual(rc, 0, err)
        self.assertEqual(st["usermeta"]["3"]["description"], "Tiểu sử mới của tác giả")
        self.assertEqual(st["options"]["blogdescription"], "Mô tả mới")
        self.assertEqual(st["options"]["cau_hinh"], {"a": {"b": "chữ mới"}})
        self.assertEqual([s[1] for s in log["skip"]], ["không thấy đường dẫn"])

    def test_elementor_text_theo_widget(self):
        data = ElementorPath.DATA
        ops = [{"item": "e", "post": 10, "target": "text", "field": "elementor:w1:editor", "old": "SEO tốt", "new": "SEO & GEO tốt"}]
        rc, _, _, st, log = apply(el_store(data), ops)
        self.assertEqual(el_after(st)[0]["elements"][0]["settings"]["editor"], "Dịch vụ SEO & GEO tốt")
        ops = [{"item": "e", "post": 10, "target": "text", "field": "elementor:w1:editor.sai.sau", "old": "SEO", "new": "x"}]
        rc, _, _, st, log = apply(el_store(data), ops)
        self.assertEqual(el_after(st), data)
        self.assertEqual(log["skip"][0][1], "không thấy đường dẫn")


class FixTarget(unittest.TestCase):
    def test_fix_dung_guard_old(self):
        store = {"posts": {"5": {"post_content": "", "post_title": "Tiêu đề cũ", "post_name": "t"}}, "meta": {}}
        ok = {"item": "f", "post": 5, "target": "fix", "field": "post_title", "old": "Tiêu đề cũ", "new": "Tiêu đề mới"}
        rc, _, _, st, log = apply(store, [ok])
        self.assertEqual(st["posts"]["5"]["post_title"], "Tiêu đề mới")
        bad = dict(ok, old="Một tiêu đề khác")
        rc, _, _, st, log = apply(store, [bad])
        self.assertEqual(st["posts"]["5"]["post_title"], "Tiêu đề cũ")
        self.assertIn("khác bản lúc soạn", log["skip"][0][1])

    def test_fix_khoa_chua_co(self):
        data = ElementorPath.DATA
        op = {"item": "f", "post": 10, "target": "fix", "field": "elementor:w2:subtitle", "old": None, "new": "Phụ đề"}
        rc, _, _, st, log = apply(el_store(data), [op])
        self.assertEqual(el_after(st)[0]["elements"][1]["settings"]["subtitle"], "Phụ đề")
        # Khoá cha thiếu thì không tạo.
        op = dict(op, field="elementor:w2:a.b")
        rc, _, _, st, log = apply(el_store(data), [op])
        self.assertEqual(el_after(st), data)

    def test_field_sai_dang_va_post_thieu(self):
        rc, _, _, st, log = apply({"posts": {}, "meta": {}}, [
            {"item": "a", "post": 1, "target": "fix", "field": "gi_do", "old": "x", "new": "y"},
            {"item": "b", "post": 99, "target": "fix", "field": "post_title", "old": "x", "new": "y"}])
        self.assertEqual([s[1] for s in log["skip"]], ["field sai dạng", "không có post"])


class ElementorTree(unittest.TestCase):
    def test_el_rm_dung_1_phan_tu(self):
        data = [widget("c1", {}, [widget("w1", {"editor": "Lorem"}), widget("w2", {"editor": "Giữ"})])]
        ops = [{"item": "r", "post": 10, "target": "el_rm", "id": "w1", "widget_type": "text-editor"}]
        rc, _, _, st, log = apply(el_store(data), ops)
        self.assertEqual([e["id"] for e in el_after(st)[0]["elements"]], ["w2"])
        self.assertIsInstance(el_after(st)[0]["elements"], list)
        ops = [{"item": "r", "post": 10, "target": "el_rm", "id": "khong-co"}]
        rc, _, _, st, log = apply(el_store(data), ops)
        self.assertEqual(el_after(st), data)
        self.assertIn("gỡ 0 phần tử", log["skip"][0][1])
        ops = [{"item": "r", "post": 10, "target": "el_rm", "id": "w1", "widget_type": "heading"}]
        rc, _, _, st, log = apply(el_store(data), ops)
        self.assertEqual(el_after(st), data)

    def test_el_rm_id_trung_khong_gỡ(self):
        data = [widget("c1", {}, [widget("dup", {}), widget("dup", {})])]
        rc, _, _, st, log = apply(el_store(data), [{"item": "r", "post": 10, "target": "el_rm", "id": "dup"}])
        self.assertEqual(el_after(st), data)
        self.assertIn("gỡ 2 phần tử", log["skip"][0][1])

    def test_el_restore(self):
        data = [widget("c1", {}, [widget("w2", {"editor": "Giữ"})])]
        w1 = widget("w1", {"editor": "Gốc"})
        op = {"item": "r", "post": 10, "target": "el_restore", "id": "w1", "parent": "c1", "index": 0, "src_key": "w1"}
        rc, _, err, st, log = apply(el_store(data), [op], as_file={"src.json": {"w1": {"widget": w1}}})
        self.assertEqual(rc, 0, err)
        self.assertEqual([e["id"] for e in el_after(st)[0]["elements"]], ["w1", "w2"])
        # Chạy lại: đã có thì báo đã đúng, không chèn lần hai.
        rc, _, _, st2, log2 = apply(st, [op], as_file={"src.json": {"w1": {"widget": w1}}})
        self.assertEqual([e["id"] for e in el_after(st2)[0]["elements"]], ["w1", "w2"])
        self.assertIn("(đã đúng)", log2["ok"][0])
        # Thiếu container.
        rc, _, _, st3, log3 = apply(el_store(data), [dict(op, parent="khong-co")], as_file={"src.json": {"w1": {"widget": w1}}})
        self.assertEqual(el_after(st3), data)


class Output(unittest.TestCase):
    def test_scope_eval_file_va_out(self):
        """Lỗi 17/10: hàm dùng biến cấp file như biến toàn cục báo 'không thấy' hàng loạt.
        Runner chạy script trong hàm. Op đúng phải ok, và log ra file OUT."""
        store = {"posts": {"5": {"post_content": "a b c", "post_title": "", "post_name": ""}}, "meta": {}}
        ops = [{"item": "t", "post": 5, "target": "text", "field": "post_content", "old": "b", "new": "B"}]
        rc, out, err, st, log = apply(store, ops)
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(log["ok"]), 1)
        self.assertEqual(log["skip"], [])
        self.assertTrue(out.startswith("OUT "))  # stdout chỉ có một dòng tóm tắt

    def test_khong_ghi_de_out_va_loi_dau_vao(self):
        store = {"posts": {}, "meta": {}}
        with tempfile.TemporaryDirectory() as d:
            existing = Path(d) / "log.json"
            existing.write_text("{}")
            rc, _, err, _, _ = apply(store, [], env={"OUT": str(existing)})
            self.assertEqual(rc, 1)
            self.assertIn("không ghi đè", err)
            self.assertEqual(existing.read_text(), "{}")
        rc, _, err, _, _ = run_php("apply.php", store, None, env={"PLAN": "/khong/co.json"})
        self.assertEqual(rc, 1)
        rc, _, err, _, _ = run_php("apply.php", store, {"khong_co_ops": 1})
        self.assertEqual(rc, 1)

    def test_stdout_khi_khong_co_out(self):
        store = {"posts": {"5": {"post_content": "a b", "post_title": "", "post_name": ""}}, "meta": {}}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "plan.json").write_text(json.dumps({"ops": []}))
            e = dict(os.environ, PLAN=str(Path(d) / "plan.json"), DRY="1")
            e.pop("OUT", None)
            (Path(d) / "s.json").write_text(json.dumps(store))
            p = subprocess.run(["php", str(RUNNER), str(SCRIPTS / "apply.php"), str(Path(d) / "s.json"), str(Path(d) / "o.json")],
                               capture_output=True, text=True, env=e)
            self.assertEqual(p.returncode, 0)
            self.assertTrue(json.loads(p.stdout)["dry"])

    def test_fail_on_skip(self):
        store = {"posts": {}, "meta": {}}
        ops = [{"item": "a", "post": 1, "target": "fix", "field": "post_title", "old": "x", "new": "y"}]
        rc, _, _, _, log = apply(store, ops, env={"FAIL_ON_SKIP": "1"})
        self.assertEqual(rc, 2)
        self.assertEqual(len(log["skip"]), 1)  # log vẫn được ghi trước khi thoát

    def test_help(self):
        p = subprocess.run(["php", str(SCRIPTS / "apply.php"), "--help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("apply.php", p.stdout)


class OldTargets(unittest.TestCase):
    """Dạng cũ (before, value) vẫn chạy như bản 1.4."""

    def test_meta_va_post_title(self):
        store = {"posts": {"5": {"post_content": "", "post_title": "Cũ", "post_name": "x"}},
                 "meta": {"5": {"rank_math_title": "Title cũ"}}}
        ops = [
            {"item": "a", "post": 5, "target": "meta:rank_math_title", "before": "Title cũ", "value": "Title mới"},
            {"item": "b", "post": 5, "target": "post_title", "before": "Cũ", "value": "Mới"},
            {"item": "c", "post": 5, "target": "post_title", "before": "Sai", "value": "Mới 2"},
        ]
        rc, _, _, st, log = apply(store, ops)
        self.assertEqual(st["meta"]["5"]["rank_math_title"], "Title mới")
        self.assertEqual(st["posts"]["5"]["post_title"], "Mới")
        self.assertIn("khác bản lúc soạn", log["skip"][0][1])

    def test_content_md5(self):
        import hashlib
        store = {"posts": {"5": {"post_content": "gốc", "post_title": "", "post_name": ""}}, "meta": {}}
        h = hashlib.md5("gốc".encode()).hexdigest()
        rc, _, _, st, log = apply(store, [{"item": "a", "post": 5, "target": "content", "md5_before": h, "value": "mới"}])
        self.assertEqual(st["posts"]["5"]["post_content"], "mới")
        rc, _, _, st, log = apply(store, [{"item": "a", "post": 5, "target": "content", "md5_before": "sai", "value": "mới"}])
        self.assertEqual(st["posts"]["5"]["post_content"], "gốc")


class Locate(unittest.TestCase):
    def test_locate_tim_chu_unicode_trong_elementor(self):
        needle = "Dịch vụ SEO"
        escaped = json.dumps([{"settings": {"editor": needle + " tốt"}}])  # \u escape như Elementor lưu
        tables = {
            "posts": [{"ID": "5", "post_status": "publish", "post_type": "post", "post_content": "Giới thiệu " + needle + ". " + needle, "post_title": "T"},
                      {"ID": "6", "post_status": "publish", "post_type": "post", "post_content": "Dich vu SEO khong dau", "post_title": "T"}],
            "postmeta": [{"post_id": "10", "meta_key": "_elementor_data", "meta_value": escaped, "post_status": "publish", "post_type": "page"},
                         {"post_id": "11", "meta_key": "rank_math_title", "meta_value": "Khác hẳn", "post_status": "publish", "post_type": "page"}],
            "options": [],
        }
        rc, out, err, st, log = run_php("locate.php", {"tables": tables, "posts": {}}, None,
                                        as_file={"needles.json": [{"id": "n1", "needle": needle}]}, env={"OUT": ""})
        self.assertEqual(rc, 0, err)
        res = json.loads(out)
        hits = res[0]["hits"]
        by = {(h["post"], h["where"]): h["count"] for h in hits if "post" in h}
        self.assertEqual(by[(5, "post_content")], 2)
        self.assertEqual(by[(10, "meta:_elementor_data")], 1)  # tìm được chữ nằm trong JSON Elementor đã escape \u
        self.assertNotIn((6, "post_content"), by)  # LIKE không phân biệt dấu: lọc lại bằng đếm đúng chữ
        self.assertNotIn((11, "meta:rank_math_title"), by)


if __name__ == "__main__":
    unittest.main(verbosity=1)
