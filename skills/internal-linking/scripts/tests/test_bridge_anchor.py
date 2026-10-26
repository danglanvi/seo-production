"""Test offline cho bridge_candidates.py và anchor_gsc.py. Không gọi mạng, không nạp model, chỉ dùng stdlib.
Chạy: python3 -B scripts/tests/test_bridge_anchor.py   (từ thư mục skill)

Ca hỏng thật (nguồn lỗi, đề xuất nd-10):
- 17/10 và 18/10/2026 agent dựng pipeline cầu nối bằng script ad hoc 2 lần (15.522 rồi 16.464 đoạn), Gemma nạp lại model mỗi khối.
  bridge_candidates.py không nạp model: svi.py query chạy một tiến trình, script chỉ lọc và xuất jev_in.jsonl.
  Các test test_build_* kiểm từng luật lọc: đoạn trên chính trang đích, mở bài, khối template lặp, trang đã link tới đích, chỉ SC.
- Phần EV của nd-10 bị cắt ở 500 ký tự nên chưa đối chiếu ca hỏng cụ thể của bước chọn anchor từ GSC. anchor_gsc.py chỉ áp
  luật có sẵn trong references/anchor-rules.md (luật 1, 2, 6, ≤3 lần, anchor = seed query của trang đích).
"""
import contextlib
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
import bridge_candidates as BC  # noqa: E402
import anchor_gsc as AG  # noqa: E402

S = "https://example.vn"


def wj(path, items):
    Path(path).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), encoding="utf-8")


def rj(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def run(mod, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = mod.main(argv)
    return code, out.getvalue(), err.getvalue()


def passage(url, si, pi, h2, text, h3=""):
    path = " > ".join(x for x in (h2, h3) if x)
    return {"id": "%s#s%dp%d" % (url, si, pi), "level": "passage", "url": url, "text": (path + ": " if path else "") + text,
            "meta": {"heading": h2, "h3": h3, "section_index": si, "words": len(text.split())}}


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.d = Path(self.tmp.name)
        A, B, C, D, E, F = (S + p for p in ("/dich-vu-seo/", "/seo-la-gi/", "/seo-onpage/", "/tin-1/", "/audit/", "/tin-2/"))
        self.A, self.B, self.C, self.D, self.E = A, B, C, D, E
        tpl = "Đăng ký nhận bản tin SEO hàng tuần từ đội ngũ chuyên gia của chúng tôi để cập nhật xu hướng."
        rows = [
            {"id": A + "#page", "level": "page", "url": A, "text": "x", "meta": {"title": "Dịch vụ SEO | Site"}},
            passage(A, 1, 0, "Phạm vi dịch vụ", "Dịch vụ SEO gồm audit, nội dung và liên kết nội bộ cho website doanh nghiệp."),
            passage(B, 0, 0, "", "SEO là quá trình tối ưu website để xuất hiện trên Google, mở bài trả lời câu hỏi chính."),
            passage(B, 1, 0, "SEO hoạt động thế nào", "Công cụ tìm kiếm thu thập, lập chỉ mục rồi xếp hạng trang theo truy vấn."),
            passage(B, 2, 0, "Câu hỏi thường gặp", "Doanh nghiệp nhỏ có nên thuê dịch vụ SEO hay tự làm SEO trong năm đầu?"),
            passage(C, 1, 0, "Kết luận", "Tối ưu onpage là một phần của dịch vụ SEO tổng thể cho website."),
            {"id": C + "#a0", "level": "anchor", "url": C, "text": "ctx", "meta": {"anchor": "dịch vụ SEO", "target": A,
                                                                                  "zone": "main"}},
            passage(D, 3, 1, "Đăng ký", tpl), passage(E, 4, 0, "Liên hệ", tpl), passage(F, 2, 0, "Bản tin", tpl),
            passage(E, 1, 0, "Quy trình audit SEO", "Quy trình audit SEO kỹ thuật kiểm crawl, index và tốc độ trang."),
        ]
        pages = [
            {"url": A, "title": "Dịch vụ SEO | Site", "h1": "Dịch vụ SEO", "meta": "Dịch vụ SEO trọn gói",
             "h2": ["Phạm vi dịch vụ", "Bảng giá", "Câu hỏi thường gặp"], "robots": "index, follow"},
            {"url": B, "title": "SEO là gì", "h1": "SEO là gì", "h2": ["SEO hoạt động thế nào", "Lợi ích", "Câu hỏi thường gặp",
                                                                      "Kết luận"], "robots": ""},
            {"url": C, "title": "SEO onpage", "h1": "SEO onpage", "h2": ["Onpage là gì", "Kết luận"], "robots": "noindex"},
        ]
        hits = [{"id": A, "text": "q", "top": [
            {"id": A + "#s1p0", "url": A, "level": "passage", "cos": 0.91},
            {"id": B + "#s0p0", "url": B, "level": "passage", "cos": 0.80},
            {"id": B + "#s2p0", "url": B, "level": "passage", "cos": 0.74},
            {"id": B + "#s1p0", "url": B, "level": "passage", "cos": 0.52},
            {"id": C + "#s1p0", "url": C, "level": "passage", "cos": 0.77},
            {"id": D + "#s3p1", "url": D, "level": "passage", "cos": 0.60},
            {"id": S + "/mat/#s1p0", "url": S + "/mat/", "level": "passage", "cos": 0.5},
        ]}]
        wj(d / "rows.jsonl", rows)
        wj(d / "pages.jsonl", pages)
        wj(d / "hits.jsonl", hits)
        wj(d / "targets.jsonl", [{"url": "/dich-vu-seo/", "keywords": ["audit SEO"]}])
        (d / "targets.txt").write_text(A + "\n# ghi chú\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, *extra, out="out"):
        d = self.d
        return run(BC, ["build", "--targets", str(d / "targets.jsonl"), "--hits", str(d / "hits.jsonl"), "--rows",
                        str(d / "rows.jsonl"), "--pages", str(d / "pages.jsonl"), "--out", str(d / out)] + list(extra))

    def test_queries_from_pages(self):
        code, out, _ = run(BC, ["queries", "--targets", str(self.d / "targets.txt"), "--pages", str(self.d / "pages.jsonl")])
        self.assertEqual(code, 0)
        q = json.loads(out.strip())
        self.assertEqual(q["id"], self.A)
        self.assertIn("Dịch vụ SEO", q["text"])
        self.assertIn("Bảng giá", q["text"])
        self.assertEqual(q["filter"], {"level": "passage"})

    def test_queries_no_text_fails(self):
        code, _, err = run(BC, ["queries", "--targets", str(self.d / "targets.txt")])
        self.assertEqual(code, 1)
        self.assertIn("không có title", err)

    def test_build_filters(self):
        code, _, err = self.build()
        self.assertEqual(code, 0, err)
        s = json.loads((self.d / "out" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(s["dropped"], {"cung_trang": 1, "mo_bai": 1, "trang_da_link": 1, "lap_template": 1})
        self.assertEqual(s["missing_rows"], 1)
        kept = rj(self.d / "out" / "candidates.jsonl")
        ids = [k["passage_id"] for k in kept]
        self.assertEqual(ids, [self.B + "#s2p0", self.B + "#s1p0", self.E + "#s1p0"])
        self.assertEqual([k["vung"] for k in kept], ["SC", "MC", "?"])  # trang E không có trong pages.jsonl
        self.assertEqual(kept[2]["nguon"], "kw")
        self.assertEqual(kept[2]["kw"], ["audit SEO"])
        jev = rj(self.d / "out" / "jev_in.jsonl")
        st = jev[0]["state"]
        self.assertEqual(st["source"]["heading"], "Câu hỏi thường gặp")
        # Khoá state khớp jev_in đã hiệu chuẩn link-bridge 17/10 (source: title, heading, paragraph).
        self.assertEqual(sorted(st["source"]), ["heading", "paragraph", "title"])
        self.assertEqual(sorted(st["target"]), ["headings", "summary", "title", "url"])
        self.assertTrue(st["source"]["paragraph"].startswith("Doanh nghiệp nhỏ"))
        self.assertEqual(st["target"]["title"], "Dịch vụ SEO")
        self.assertEqual(st["target"]["headings"][0], "Phạm vi dịch vụ")
        self.assertTrue((self.d / "out" / "candidates.tsv").read_text(encoding="utf-8").startswith("id\ttarget"))

    def test_build_no_overwrite(self):
        self.assertEqual(self.build()[0], 0)
        code, _, err = self.build()
        self.assertEqual(code, 1)
        self.assertIn("không ghi đè", err)
        self.assertEqual(self.build("--force")[0], 0)

    def test_build_sc_only_and_keep_linked(self):
        code, _, err = self.build("--sc-only", "--keep-linked", out="sc")
        self.assertEqual(code, 0, err)
        kept = rj(self.d / "sc" / "candidates.jsonl")
        by = {k["passage_id"]: k for k in kept}
        self.assertEqual(set(by), {self.B + "#s2p0", self.C + "#s1p0"})
        self.assertEqual(by[self.C + "#s1p0"]["flags"], ["trang_da_link", "nguon_noindex"])
        s = json.loads((self.d / "sc" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(s["dropped"]["mc"], 2)

    def test_build_min_cos_keeps_keyword_rows(self):
        self.assertEqual(self.build("--min-cos", "0.6", out="mc")[0], 0)
        ids = [k["passage_id"] for k in rj(self.d / "mc" / "candidates.jsonl")]
        self.assertEqual(ids, [self.B + "#s2p0", self.E + "#s1p0"])

    def test_merge(self):
        self.assertEqual(self.build()[0], 0)
        kept = rj(self.d / "out" / "candidates.jsonl")
        wj(self.d / "jev.jsonl", [
            {"id": kept[0]["id"], "answers": {"fit": {"choice": "natural_bridge", "confidence": 0.9,
                                                      "probabilities": {"natural_bridge": 0.9, "weak_fit": 0.1}}}},
            {"id": kept[1]["id"], "answers": {"fit": {"choice": "weak_fit", "confidence": 0.6,
                                                      "probabilities": {"natural_bridge": 0.3}}}},
            {"id": kept[2]["id"], "error": "http_500", "route": "review"},
        ])
        code, out, err = run(BC, ["merge", "--candidates", str(self.d / "out" / "candidates.jsonl"), "--jev",
                                  str(self.d / "jev.jsonl")])
        self.assertEqual(code, 0, err)
        lines = out.strip().split("\n")
        self.assertTrue(lines[0].startswith("target\tdat\tnb"))
        self.assertIn("True\t0.9\tnatural_bridge\tSC", lines[1])
        self.assertIn("loi_jev:http_500", out)
        self.assertIn("đạt natural_bridge >= 0.85: 1", err)


class AnchorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.d = Path(self.tmp.name)
        rows = [
            {"keys": [S + "/dich-vu-seo/", "dịch vụ seo"], "clicks": 40, "impressions": 900, "ctr": 0.04, "position": 6.2},
            {"keys": [S + "/dich-vu-seo/", "seo là gì"], "clicks": 2, "impressions": 300, "position": 18.0},
            {"keys": [S + "/dich-vu-seo/", "bảng giá seo"], "clicks": 1, "impressions": 80, "position": 12.0},
            {"keys": [S + "/bang-gia-seo/", "bảng giá seo"], "clicks": 20, "impressions": 400, "position": 3.1},
            {"keys": [S + "/dich-vu-seo/", "thuê seo"], "clicks": 3, "impressions": 120, "position": 9.0},
            {"keys": [S + "/dich-vu-seo/", "dịch vụ seo tổng thể"], "clicks": 5, "impressions": 150, "position": 7.0},
            {"keys": [S + "/dich-vu-seo/", "gtv seo"], "clicks": 50, "impressions": 500, "position": 1.0},
        ]
        (d / "gsc.json").write_text(json.dumps({"rows": rows}, ensure_ascii=False), encoding="utf-8")
        (d / "dich.md").write_text(
            "---\ntitle: x\n---\n# Dịch vụ SEO\n\nSEO là gì? Đây là đoạn mở bài của trang đích.\n\n"
            "## Phạm vi\n\nDịch vụ SEO tổng thể gồm audit và nội dung. Bảng giá SEO ở trang riêng.\n\n"
            "Chúng tôi cung cấp dịch&nbsp;vụ SEO cho doanh nghiệp.\n", encoding="utf-8")
        (d / "nguon.md").write_text(
            "# Bài nguồn\n\nMở bài.\n\n## Lợi ích\n\nNội dung.\n\n## Câu hỏi thường gặp\n\n"
            "Dịch vụ SEO tổng thể có cần không? Nhiều doanh nghiệp hỏi câu này.\n\n"
            "Khi nào nên dùng dịch vụ SEO thay vì tự làm? Trước hết cần hiểu SEO là gì.\n\n## Kết luận\n\nHết.\n",
            encoding="utf-8")
        (d / "anchors.json").write_text(json.dumps({"Dịch vụ SEO": 3}, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def rep(self, **kw):
        rows = AG.read_gsc(str(self.d / "gsc.json"), "page,query")
        return AG.analyze(rows, "/dich-vu-seo/", **kw)

    def test_rules(self):
        d = self.d
        rep = self.rep(target_text=(d / "dich.md").read_text(encoding="utf-8"),
                       source_text=AG.section_text((d / "nguon.md").read_text(encoding="utf-8"), "câu hỏi", 2),
                       site_anchors=json.loads((d / "anchors.json").read_text(encoding="utf-8")), exclude="gtv")
        by = {r["query"]: r for r in rep["rows"]}
        self.assertNotIn("gtv seo", by)
        self.assertEqual(by["dịch vụ seo"]["flags"], ["du_3_lan"])
        self.assertEqual(by["dịch vụ seo"]["da_dung"], 3)
        self.assertEqual(by["bảng giá seo"]["flags"][0], "trang_khac")
        self.assertEqual(by["bảng giá seo"]["trang_khac"], "/bang-gia-seo")
        self.assertEqual(by["seo là gì"]["flags"], ["mo_bai_dich"])
        self.assertTrue(by["seo là gì"]["dat"])  # mo_bai_dich chỉ cảnh báo
        self.assertIn("khong_co_trong_dich", by["thuê seo"]["flags"])
        self.assertEqual(by["dịch vụ seo tổng thể"]["flags"], ["chi_o_dau_doan"])
        self.assertEqual(rep["chua_kiem"], [])
        self.assertEqual([r["query"] for r in rep["rows"] if r["dat"]], ["seo là gì"])

    def test_dat_and_order(self):
        rep = self.rep(target_text=(self.d / "dich.md").read_text(encoding="utf-8"))
        q = [r["query"] for r in rep["rows"]]
        self.assertEqual(q[:2], ["dịch vụ seo", "dịch vụ seo tổng thể"])  # dòng đạt lên trước, rồi theo click
        self.assertTrue(rep["rows"][0]["dat"])
        gtv = rep["rows"][q.index("gtv seo")]  # 50 click nhưng không có trong trang đích
        self.assertEqual(gtv["flags"], ["khong_co_trong_dich"])
        self.assertIn("du_3_lan", rep["chua_kiem"])

    def test_nfd_query_and_html_target(self):
        rows = [{"page": None, "query": unicodedata.normalize("NFD", "dịch vụ seo"), "clicks": 1, "impressions": 5,
                 "position": 4.0}]
        html = ("<html><body><header><a href='/'>Dịch vụ SEO menu</a></header><article><h1>Tiêu đề</h1>"
                "<p>Đoạn mở bài.</p><p>Chúng tôi làm dịch&nbsp;vụ SEO &amp; GEO.</p></article></body></html>")
        rep = AG.analyze(rows, S + "/dich-vu-seo/", target_text=html)
        r = rep["rows"][0]
        self.assertTrue(r["checks"]["co_trong_dich"])
        self.assertFalse(r["checks"]["mo_bai_dich"])
        self.assertTrue(rep["mot_trang"])
        self.assertIn("trang_khac", rep["chua_kiem"])

    def test_csv_vietnamese_single_page(self):
        p = self.d / "q.csv"
        p.write_text("﻿Truy vấn hàng đầu,Số lượt nhấp,Số lần hiển thị,CTR,Vị trí\n"
                     "dịch vụ seo,\"1.234\",\"20.000\",6%,\"3,4\"\nthuê seo,5,90,5%,8\n", encoding="utf-8")
        rows = AG.read_gsc(str(p), "page,query")
        self.assertEqual(rows[0]["clicks"], 1234)
        self.assertEqual(rows[0]["impressions"], 20000)
        self.assertEqual(rows[0]["position"], 3.4)
        self.assertIsNone(rows[0]["page"])
        code, out, err = run(AG, [str(p), "--page", "/dich-vu-seo/"])
        self.assertEqual(code, 0, err)
        self.assertIn("không kiểm được trang_khac", out)
        self.assertIn("| dịch vụ seo | có | 1234 | 20000 | 3,4 |", out)

    def test_csv_with_page_column_tsv(self):
        p = self.d / "q.tsv"
        p.write_text("Page\tQuery\tClicks\tImpressions\tPosition\n%s/a/\tseo\t3\t10\t2.5\n%s/b/\tseo\t9\t50\t1.5\n" % (S, S),
                     encoding="utf-8")
        rep = AG.analyze(AG.read_gsc(str(p), "page,query"), "/a/")
        self.assertEqual(rep["rows"][0]["flags"], ["trang_khac"])

    def test_cli_errors(self):
        d = self.d
        code, _, err = run(AG, [str(d / "gsc.json"), "--page", "/khong-co/"])
        self.assertEqual(code, 1)
        self.assertIn("không có query", err)
        code, _, err = run(AG, [str(d / "gsc.json"), "--page", "/dich-vu-seo/", "--source-file", str(d / "nguon.md"),
                                "--section", "không tồn tại"])
        self.assertEqual(code, 1)
        self.assertIn("không thấy mục H2", err)
        out = d / "a.tsv"
        self.assertEqual(run(AG, [str(d / "gsc.json"), "--page", "/dich-vu-seo/", "--out", str(out)])[0], 0)
        self.assertTrue(out.read_text(encoding="utf-8").startswith("query\tdat"))
        code, _, err = run(AG, [str(d / "gsc.json"), "--page", "/dich-vu-seo/", "--out", str(out)])
        self.assertEqual(code, 1)
        self.assertIn("không ghi đè", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
