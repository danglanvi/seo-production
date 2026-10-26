"""Test offline scripts/doi_chieu.py: nhãn da-len, chua-len, mot-phan, doc-tay, bỏ qua; tải trang từ máy local.
Chạy: python3 -B tests/test_doi_chieu.py
Ca hỏng thật (19/10, 6cae27d5-16): thẻ Vincent sửa chữ (values) mà agent đối chiếu theo đề xuất, báo "chưa lên" nhầm.
"""
import http.server
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "doi_chieu.py"

OLD_META = "Dịch vụ SEO trọn gói cho doanh nghiệp vừa và nhỏ với báo cáo hằng tháng rõ ràng"
NEW_META = "Dịch vụ SEO và GEO vận hành bằng AI cho doanh nghiệp với báo cáo hằng tuần minh bạch"
EDITED_META = "Chúng tôi làm SEO và GEO cho doanh nghiệp, báo cáo mỗi tuần, số liệu lấy thẳng từ Search Console"


def page(title, meta, h1, body=""):
    return ("<html><head><title>%s</title><meta name=\"description\" content=\"%s\"></head><body><h1>%s</h1><p>%s</p></body></html>"
            % (title, meta, h1, body))


def write(d, rel, obj):
    p = Path(d, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def card(i, url, fields, post_id=1):
    return {"id": i, "post_id": post_id, "url": url, "label": i, "fields": fields}


def meta_field(key="meta", before=OLD_META, a=NEW_META):
    return {"key": key, "name": key, "before": before, "A": a, "B": before}


def export(d, cards, reviews):
    write(d, "report/meta.json", {"items": cards, "options": [{"key": "A", "label": "A"}, {"key": "B", "label": "B"}]})
    for i, r in reviews.items():
        write(d, "reviews/%s.json" % i, dict({"item_id": i}, **r))


def run(args):
    return subprocess.run([sys.executable, "-I", str(SCRIPT)] + args, capture_output=True, text=True, timeout=60)


class Labels(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)

    def tearDown(self):
        self.t.cleanup()

    def go(self, cards, reviews, pages, extra=None):
        export(self.d / "db", cards, reviews)
        write(self.d, "pages.json", pages)
        p = run([str(self.d / "db"), "--out", str(self.d / "out"), "--cache", str(self.d / "pages.json"), "--year", "2026"] + (extra or []))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        res = json.loads((self.d / "out" / "ket-qua.json").read_text(encoding="utf-8"))
        return {c["id"]: c for c in res}, (self.d / "out" / "ket-qua.md").read_text(encoding="utf-8")

    def pg(self, **kw):
        from importlib import util
        spec = util.spec_from_file_location("dc", SCRIPT)
        m = util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.parse_page(page(kw.get("title", "T"), kw.get("meta", ""), kw.get("h1", ""), kw.get("body", "")), 200, 2026)

    def test_nhan_co_ban_va_chu_nguoi_duyet_sua(self):
        u = lambda n: "https://example.vn/%s/" % n
        cards = [
            card("c-len", u("a"), [meta_field()]),
            card("c-chua", u("b"), [meta_field()]),
            card("c-sua", u("c"), [meta_field()]),
            card("c-bo", u("d"), [meta_field()]),
            card("c-tay", u("e"), [{"key": "action", "name": "Việc", "before": "x", "proposed": "Mỗi trang cần thêm schema FAQ"}]),
        ]
        reviews = {
            "c-len": {"status": "approved", "option": "A", "values": {}},
            "c-chua": {"status": "approved", "option": "A", "values": {}},
            "c-sua": {"status": "edited", "option": "A", "values": {"meta": EDITED_META}},
            "c-bo": {"status": "rejected", "option": "A", "values": {}},
            "c-tay": {"status": "approved", "values": {}},
        }
        pages = {u("a"): self.pg(meta=NEW_META), u("b"): self.pg(meta=OLD_META), u("c"): self.pg(meta=EDITED_META),
                 u("d"): self.pg(meta=OLD_META), u("e"): self.pg()}
        c, md = self.go(cards, reviews, pages)
        self.assertEqual(c["c-len"]["ket_qua"], "da-len")
        self.assertEqual(c["c-chua"]["ket_qua"], "chua-len")
        # Lỗi 19/10: đối chiếu theo đề xuất A sẽ báo chưa lên. Phải lấy chữ người duyệt sửa.
        self.assertEqual(c["c-sua"]["ket_qua"], "da-len")
        self.assertEqual(c["c-bo"]["ket_qua"], "bo-qua")
        self.assertEqual(c["c-tay"]["ket_qua"], "doc-tay")
        self.assertIn("c-chua", md.split("Hàng ghi ngay")[1])
        self.assertNotIn("c-len", md.split("Hàng ghi ngay")[1])

    def test_mot_phan_va_option_b_va_nam(self):
        u = "https://example.vn/x/"
        cards = [card("m1", u, [{"key": "seo_title", "name": "t", "before": "Cũ", "A": "SEO %currentyear% giá tốt cho doanh nghiệp vừa", "B": "Cũ"}]),
                 card("m2", u, [meta_field()])]
        reviews = {"m1": {"status": "approved", "option": "A", "values": {}}, "m2": {"status": "approved", "option": "B", "values": {}}}
        pages = {u: self.pg(title="SEO 2026 giá tốt cho doanh nghiệp vừa", meta="Một đoạn không liên quan gì cả")}
        c, _ = self.go(cards, reviews, pages)
        self.assertEqual(c["m1"]["ket_qua"], "da-len")  # %currentyear% thay bằng --year
        self.assertEqual(c["m2"]["fields"][0]["final"], OLD_META)  # option B giữ chữ cũ
        self.assertIn(c["m2"]["ket_qua"], ("mot-phan", "chua-len"))

    def test_khoa_lane_va_khoa_trung_key(self):
        u = "https://example.vn/y/"
        cards = [card("lane-1", u, [meta_field()]), card("lane-2", u, [meta_field()]),
                 card("dup", u, [meta_field("text", "Câu một cũ của trang này khá dài", "Câu một mới của trang này khá dài"),
                                 meta_field("text", "Câu hai cũ của trang này khá dài", "Câu hai mới của trang này khá dài")])]
        reviews = {"lane-1": {"status": "approved", "option": "A"}, "lane-2": {"status": "approved", "option": "A"},
                   "dup": {"status": "edited", "option": "A", "values": {"text": "Câu một mới của trang này khá dài", "text#2": "Câu hai mới của trang này khá dài"}}}
        (self.d / "khoa.txt").write_text("# lane đang chạy\nlane-1\nlane-2x*\n", encoding="utf-8")
        pages = {u: self.pg(body="Câu một mới của trang này khá dài. Câu hai mới của trang này khá dài.")}
        c, _ = self.go(cards, reviews, pages, ["--khoa", str(self.d / "khoa.txt")])
        self.assertEqual(c["lane-1"]["ket_qua"], "bo-qua")
        self.assertEqual(c["lane-1"]["bo_qua_vi"], "khoa-lane")
        self.assertNotEqual(c["lane-2"]["ket_qua"], "bo-qua")
        self.assertEqual([f["final"] for f in c["dup"]["fields"]], ["Câu một mới của trang này khá dài", "Câu hai mới của trang này khá dài"])
        self.assertEqual(c["dup"]["ket_qua"], "da-len")

    def test_dau_vao_sai_va_khong_ghi_de(self):
        export(self.d / "db", [card("a", "https://example.vn/", [meta_field()])], {})
        p = run([str(self.d / "db"), "--out", str(self.d / "out")])
        self.assertEqual(p.returncode, 2)  # không có --site và --cache
        write(self.d, "pages.json", {})
        args = [str(self.d / "db"), "--out", str(self.d / "out"), "--cache", str(self.d / "pages.json")]
        self.assertEqual(run(args).returncode, 0)
        p = run(args)
        self.assertEqual(p.returncode, 2)
        self.assertIn("--force", p.stderr)
        self.assertEqual(run(args + ["--force"]).returncode, 0)
        self.assertEqual(run([str(self.d / "khong-co"), "--out", str(self.d / "o2"), "--cache", str(self.d / "pages.json")]).returncode, 2)
        self.assertEqual(run(["--help"]).returncode, 0)


class Fetch(unittest.TestCase):
    def test_tai_trang_url_sach_dung_host_va_nhip(self):
        seen = []

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                seen.append((self.path, time.monotonic()))
                body = page("T", NEW_META, "H").encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as d:
                d = Path(d)
                base = "http://127.0.0.1:%d" % port
                cards = [card("a", base + "/a/?utm_source=x#frag", [meta_field()]), card("b", base + "/b/", [meta_field()]),
                         card("c", base + "/c/", [meta_field()]), card("d", base + "/d/", [meta_field()]),
                         card("ngoai", "http://example.invalid/z/", [meta_field()]), card("bo", base + "/bo/", [meta_field()])]
                export(d / "db", cards, {"bo": {"status": "rejected"}})
                p = run([str(d / "db"), "--out", str(d / "out"), "--site", base, "--cache", str(d / "p.json"), "--rps", "10"])
                self.assertEqual(p.returncode, 0, p.stderr)
                paths = sorted(x[0] for x in seen)
                self.assertEqual(paths, ["/a/", "/b/", "/c/", "/d/"])  # query và fragment bị bỏ, host khác và thẻ bỏ không tải
                ts = sorted(x[1] for x in seen)
                self.assertGreaterEqual(ts[-1] - ts[0], 0.28)  # 4 request ở 10 request/giây cho cả 2 luồng
                self.assertTrue((d / "p.json").exists())
                res = {c["id"]: c for c in json.loads((d / "out" / "ket-qua.json").read_text(encoding="utf-8"))}
                self.assertEqual(res["a"]["ket_qua"], "da-len")
                self.assertEqual(res["ngoai"]["ket_qua"], "khong-co-url")
                # Chạy lại với cache có sẵn: không tải thêm.
                n = len(seen)
                p = run([str(d / "db"), "--out", str(d / "out2"), "--site", base, "--cache", str(d / "p.json")])
                self.assertEqual(p.returncode, 0)
                self.assertEqual(len(seen), n)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=1)
