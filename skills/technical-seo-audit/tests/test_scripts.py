"""Test offline cho script của technical-seo-audit. Không cần mạng, không cần model.

Chạy: python3 -B -m unittest discover -s skills/technical-seo-audit/tests (từ root repo).
"""
import csv
import http.server
import io
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import gsc_clean  # noqa: E402
import gsc_pairs  # noqa: E402
import index_probe  # noqa: E402
import link_sources  # noqa: E402
import pagerank  # noqa: E402
import schema_visible as sv  # noqa: E402


def page(body, ld):
    return ("<html><head><title>T</title><script type=\"application/ld+json\">" + json.dumps(ld, ensure_ascii=False)
            + "</script></head><body>" + body + "</body></html>")


FAQ = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": "SEO mất bao lâu để có kết quả?",
     "acceptedAnswer": {"@type": "Answer", "text": "Thường từ 3 đến 6 tháng với từ khoá cạnh tranh vừa."}},
    {"@type": "Question", "name": "Chi phí SEO tổng thể là bao nhiêu?",
     "acceptedAnswer": {"@type": "Answer", "text": "Từ 15 triệu mỗi tháng tuỳ quy mô website."}}]}


class SchemaVisible(unittest.TestCase):
    def test_faq_all_visible(self):
        html = page("<h2>Câu hỏi thường gặp</h2><h3>SEO mất bao lâu để có kết quả?</h3>"
                    "<p>Thường từ 3 đến 6 tháng với từ khoá cạnh tranh vừa.</p>"
                    "<h3>Chi phí SEO tổng thể là bao nhiêu?</h3><p>Từ 15 triệu mỗi tháng tuỳ quy mô website.</p>", FAQ)
        b = sv.extract_page(html, "https://a.vn/x/")
        self.assertEqual(len(b), 1)
        self.assertEqual(b[0]["det"], "all")
        self.assertFalse(b[0]["jev_needed"])

    def test_faq_schema_only(self):
        html = page("<h1>Bài khác</h1><p>Nội dung không liên quan tới câu hỏi trong schema.</p>", FAQ)
        b = sv.extract_page(html, "https://a.vn/y/")[0]
        self.assertEqual(b["det"], "none")
        self.assertEqual(sv.decide(b, {})[0], "FAIL")

    def test_question_shown_answer_missing_is_not_all(self):
        html = page("<ul><li>SEO mất bao lâu để có kết quả?</li><li>Chi phí SEO tổng thể là bao nhiêu?</li></ul>", FAQ)
        b = sv.extract_page(html, "https://a.vn/z/")[0]
        self.assertEqual(b["det"], "partial")
        self.assertFalse(b["jev_needed"])
        self.assertEqual(sv.decide(b, {})[0], "FAIL")

    def test_yoast_id_reference(self):
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": ["WebPage", "FAQPage"], "@id": "https://a.vn/p/", "mainEntity": [{"@id": "#q1"}]},
            {"@type": "Question", "@id": "#q1", "name": "GEO là gì?",
             "acceptedAnswer": {"@type": "Answer", "text": "GEO là tối ưu nội dung cho câu trả lời AI."}}]}
        html = page("<h2>GEO là gì?</h2><p>GEO là tối ưu nội dung cho câu trả lời AI.</p>", ld)
        b = sv.extract_page(html, "https://a.vn/p/")[0]
        self.assertEqual(b["items"][0]["value"], "GEO là gì?")
        self.assertEqual(b["det"], "all")

    def test_empty_schema(self):
        ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "", "acceptedAnswer": {"text": ""}}]}
        b = sv.extract_page(page("<p>x</p>", ld), "https://a.vn/e/")[0]
        self.assertEqual(b["det"], "empty")
        self.assertEqual(sv.decide(b, {})[0], "FAIL")

    def test_broken_escaped_tags_and_entities(self):
        self.assertEqual(sv.text_of("u003cstrongu003e1. Dịch vụ GEO?u003c/strongu003e"), "1. Dịch vụ GEO?")
        self.assertEqual(sv.text_of("Muss ich f&uuml;r Hosting <b>zahlen</b>?"), "Muss ich für Hosting zahlen ?")

    def test_nested_unclosed_noscript_keeps_text(self):
        # Ca thật 19/10: lazyload lồng <noscript> không đóng làm mất chữ cả trang.
        body = ("<noscript><iframe src=x></iframe><noscript><iframe src=y></iframe></noscript>"
                "<h2>SEO mất bao lâu để có kết quả?</h2><p>Thường từ 3 đến 6 tháng với từ khoá cạnh tranh vừa.</p>"
                "<h2>Chi phí SEO tổng thể là bao nhiêu?</h2><p>Từ 15 triệu mỗi tháng tuỳ quy mô website.</p>")
        b = sv.extract_page(page(body, FAQ), "https://a.vn/n/")[0]
        self.assertGreater(b["visible_chars"], 50)
        self.assertEqual(b["det"], "all")

    def test_price_units(self):
        nums = sv.numbers("Gói từ 15 triệu, gói nhỏ 1,5tr, add-on 999k, giá cũ 3.000.000đ")
        for v in ("15000000", "1500000", "999000", "3000000"):
            self.assertIn(v, nums)
        ld = {"@type": "Service", "offers": {"@type": "Offer", "price": "15000000", "priceCurrency": "VND"}}
        b = sv.extract_page(page("<p>Gói SEO từ 15 triệu mỗi tháng.</p>", ld), "https://a.vn/g/")[0]
        self.assertEqual(b["det"], "all")

    def test_video_only_in_jsonld(self):
        ld = {"@type": "VideoObject", "name": "v", "embedUrl": "https://www.youtube-nocookie.com/embed/JDj-8I0EJyc"}
        b = sv.extract_page(page("<p>Không có video trên trang.</p>", ld), "https://a.vn/v/")[0]
        self.assertEqual(b["det"], "none")
        b2 = sv.extract_page(page('<div class="yt" data-id="JDj-8I0EJyc"></div>', ld), "https://a.vn/v2/")[0]
        self.assertEqual(b2["det"], "all")

    def test_self_serving_rating_flag(self):
        ld = {"@type": "Organization", "name": "A", "aggregateRating": {"@type": "AggregateRating",
                                                                       "ratingValue": "4.9", "reviewCount": "132"}}
        b = sv.extract_page(page("<p>Đánh giá 4,9/5 từ 132 khách</p>", ld), "https://a.vn/r/")[0]
        self.assertEqual(b["det"], "all")
        self.assertTrue(b["self_serving"])

    def test_decide_gates(self):
        b = {"id": "x#1", "type": "FAQPage", "det": "unclear", "items": []}
        jev = {"x#1": {"answers": {"shown": {"choice": "partial", "confidence": 0.5,
                                            "probabilities": {"all": 0.2, "partial": 0.5, "none": 0.25}}}}}
        self.assertEqual(sv.decide(b, jev, fail_gate=0.7)[0], "FAIL")
        self.assertEqual(sv.decide(b, jev, fail_gate=0.8)[0], "CẦN XEM")
        self.assertEqual(sv.decide(b, {}, fail_gate=0.7)[0], "CẦN XEM")
        jev2 = {"x#1": {"answers": {"shown": {"choice": "all", "probabilities": {"all": 0.7, "partial": 0.2}}}}}
        self.assertEqual(sv.decide(b, jev2, fail_gate=0.7)[0], "CẦN XEM")  # cổng pass chưa hiệu chuẩn
        self.assertEqual(sv.decide(b, jev2, fail_gate=0.7, pass_gate=0.55)[0], "ĐẠT")
        howto = dict(b, type="HowTo")
        self.assertEqual(sv.decide(howto, jev2, fail_gate=0.7, pass_gate=0.55)[0], "CẦN XEM")

    def test_jev_state_has_no_scores(self):
        b = sv.extract_page(page("<ul><li>SEO mất bao lâu để có kết quả?</li></ul>", FAQ), "https://a.vn/s/")[0]
        st = sv.jev_state(b)
        self.assertIn("Q: SEO mất bao lâu", st["marked_up"][0])
        self.assertNotIn("score", json.dumps(st))


SF_COLS = ["Type", "Source", "Destination", "Status Code", "Link Position"]


class LinkSources(unittest.TestCase):
    def test_summarize_classes_and_patterns(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "redirection_(3xx)_inlinks.csv"
            rows = [["Hyperlink", "https://a.vn/x/", "https://a.vn/seo/seo-offpage/", "301", "Content"],
                    ["Hyperlink", "https://a.vn/y/", "https://a.vn/seo/seo-offpage/", "301", "Content"],
                    ["Hyperlink", "https://a.vn/x/", "https://zalo.me/0900", "302", "Footer"],
                    ["Hyperlink", "https://a.vn/x/", "http://online.gov.vn/Home/WebDetails/1", "301", "Footer"]]
            with open(f, "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(SF_COLS)
                w.writerows(rows)
            out = Path(d) / "o"

            class A:
                inlinks = [str(f)]
                site = "www.a.vn"
                out_dir = str(out)
            link_sources.cmd_summarize(A)
            s = json.loads((out / "summary.json").read_text())
            self.assertEqual(s["by_class"], {"nội bộ": 2, "chia sẻ/widget": 1, "ngoài": 1})
            pats = (out / "patterns.txt").read_text().strip().split("|")
            self.assertIn("/seo/seo-offpage/", pats)  # giữ / hai đầu: không khớp tên file ảnh
            self.assertIn("online.gov.vn/Home/WebDetails/1", pats)
            self.assertFalse(any("zalo" in p for p in pats))

    def test_find_sources_output_with_php_warnings(self):
        raw = ("PHP Warning:  Undefined array key \"licence\" in /x.php on line 168\n"
               "Warning: Trying to access array offset on null in /x.php\n" + json.dumps({
                   "/seo/seo-offpage/": {
                       "post": [["83842", "elementor_library", "publish", "kham-pha-chu-de", 1],
                                ["111134", "revision", "inherit", "83842-revision-v1", 1],
                                ["108981", "page", "draft", "", 1]],
                       "meta": [[83842, "_elementor_data", "elementor_library", "publish", "kham-pha-chu-de", 0, 1],
                                [125614, "_menu_item_url", "nav_menu_item", "publish", "m", 1, 0],
                                [90479, "header_schema", "post", "publish", "kpi-seo", 2, 0],
                                [86631, "_wp_attached_file", "attachment", "inherit", "anh", 1, 0]],
                       "opt": [["rank_math_backups", 1], ["widget_text", 1]],
                       "usermeta": [[12, "twitter"]]},
                   "/khong-co/": []}))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            p.write_text(raw)
            data, warn = link_sources.load_find_sources(p)
            self.assertEqual(len(warn), 2)
            rows = link_sources.live_rows(data)
            ids = {(r["where"], r["id"]) for r in rows}
            self.assertIn(("Elementor template", "83842"), ids)
            self.assertIn(("Elementor _elementor_data", "83842"), ids)
            self.assertIn(("menu", "125614"), ids)
            self.assertIn(("option", "widget_text"), ids)
            self.assertIn(("usermeta (hồ sơ tác giả)", "12"), ids)
            self.assertNotIn("111134", {r["id"] for r in rows})  # revision
            self.assertNotIn("108981", {r["id"] for r in rows})  # nháp
            self.assertNotIn("rank_math_backups", {r["id"] for r in rows})
            schema = [r for r in rows if r["id"] == "90479"][0]
            self.assertIn("không phải thẻ a", schema["where"])

    def test_php_script_adds_escaped_variant(self):
        php = (Path(__file__).resolve().parents[1] / "scripts" / "find_sources.php").read_text()
        self.assertIn("str_replace( '/', '\\\\/', $p )", php)
        self.assertIn("usermeta", php)


class GscClean(unittest.TestCase):
    def test_fragments_and_cap(self):
        rows = [{"page": "/geo-la-gi/", "query": "geo là gì", "impressions": "3923"},
                {"page": "/geo-la-gi/#ftoc-heading-1", "query": "geo là gì", "impressions": "3854"},
                {"page": "/geo-la-gi/#ftoc-heading-8", "query": "geo là gì", "impressions": "3854"}]
        keep, rep = gsc_clean.clean(rows)
        self.assertEqual(len(keep), 1)
        self.assertEqual(rep["impressions_clean"], 3923)
        self.assertEqual(rep["impressions_with_fragments"], 11631)
        self.assertFalse(rep["capped"])
        _, rep2 = gsc_clean.clean([{"page": "/a/", "impressions": "1"}] * 25000)
        self.assertTrue(rep2["capped"])

    def test_tsv_with_quote_in_query(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "g.tsv"
            p.write_text('page\tquery\tclicks\timpressions\n/a/\t"seo" là gì\t1\t10\n/a/#x\tb\t0\t9\n/b/\tc\t0\t5\n')
            rows = gsc_clean.read_rows(p)
            self.assertEqual(len(rows), 3)
            keep, rep = gsc_clean.clean(rows)
            self.assertEqual(rep["fragment_rows"], 1)
            self.assertEqual(rep["impressions_clean"], 15)



class GscPairs(unittest.TestCase):
    TSV = ("page\tquery\tclicks\timpressions\tctr\tposition\n"
           "/a/\tseo là gì\t5\t100\t0.05\t2.0\n/b/\tseo là gì\t1\t50\t0.02\t6.0\n"
           "/a/\tseo onpage\t3\t40\t0.07\t3.0\n/b/\tseo onpage\t2\t60\t0.03\t2.5\n"
           "/a/#ftoc-heading-1\tseo là gì\t0\t90\t0\t2.0\n/b/\tseo 2026\t0\t30\t0\t8.0\n"
           "/c/\tseo là gì\t0\t5\t0\t20.0\n")

    def test_overlap_local(self):
        with tempfile.TemporaryDirectory() as t:
            g, pairs, out = Path(t) / "g.tsv", Path(t) / "p.tsv", Path(t) / "o.tsv"
            g.write_text(self.TSV, encoding="utf-8")
            pairs.write_text("https://site.vn/a/ | https://site.vn/b/\n", encoding="utf-8")
            gsc_pairs.cmd_overlap(type("A", (), {"gsc": str(g), "pairs": str(pairs), "site": "site.vn", "min_shared": 3, "out": str(out)})())
            row = dict(zip(*[l.split("\t") for l in out.read_text(encoding="utf-8").splitlines()]))
            self.assertEqual(row["shared_queries"], "2")
            self.assertEqual(row["share_a"], "1.0")  # dòng #ftoc gộp vào /a/
            self.assertEqual(row["share_b"], round(110 / 140, 3).__str__())
            self.assertEqual((row["wins_a"], row["wins_b"]), ("1", "1"))

    def test_candidates_without_pairs(self):
        with tempfile.TemporaryDirectory() as t:
            g, out = Path(t) / "g.tsv", Path(t) / "o.tsv"
            g.write_text(self.TSV, encoding="utf-8")
            gsc_pairs.cmd_overlap(type("A", (), {"gsc": str(g), "pairs": None, "site": "", "min_shared": 2, "out": str(out)})())
            lines = out.read_text(encoding="utf-8").splitlines()[1:]
            self.assertEqual([l.split("\t")[:3] for l in lines], [["/a/", "/b/", "2"]])

    def test_jev_input_text_only_and_check(self):
        with tempfile.TemporaryDirectory() as t:
            pages, pairs, out = Path(t) / "pages.jsonl", Path(t) / "p.tsv", Path(t) / "in.jsonl"
            pages.write_text("\n".join(json.dumps({"url": u, "title": "T " + u, "h1": "H", "excerpt": "đoạn mở",
                                                   "top_queries": ["seo là gì"]}) for u in ("/a/", "/b/")), encoding="utf-8")
            pairs.write_text("/a/ | /b/\n", encoding="utf-8")
            gsc_pairs.cmd_jev_in(type("A", (), {"pages": str(pages), "pairs": str(pairs), "site": "site.vn", "out": str(out)})())
            row = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(row["state"]["shared_queries"], [])
            self.assertEqual(set(row["state"]["page_a"]), {"url", "title", "h1", "opening"})
            self.assertEqual(gsc_pairs.problems([row]), [])
            bad = {"id": "x", "state": {"page": {"url": "/a/", "top_queries": ["q"]}, "shared_queries": ["q"]}}
            self.assertEqual(len(gsc_pairs.problems([bad])), 2)
            bad_file = Path(t) / "bad.jsonl"
            bad_file.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gsc_pairs.cmd_check(type("A", (), {"inp": str(bad_file)})())


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(header)
        w.writerows(rows)


class PageRank(unittest.TestCase):
    """Link Score trống khi SF chạy headless (18/10/2026). Lượt tính đầu lấy 389 trang HTML, bản lưu lấy 357 trang index được."""

    INTERNAL = ("Address", "Content Type", "Status Code", "Indexability")
    INLINKS = ("Type", "Source", "Destination", "Follow", "Link Position")

    def run_pr(self, internal_rows, inlink_rows):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t)
        i, l, o = Path(t) / "internal_all.csv", Path(t) / "all_inlinks.csv", Path(t) / "pr.tsv"
        write_csv(i, self.INTERNAL, internal_rows)
        write_csv(l, self.INLINKS, inlink_rows)
        buf = io.StringIO()
        with redirect_stdout(buf):
            pagerank.main(["--internal", str(i), "--inlinks", str(l), "--out", str(o)])
        rows = [r.split("\t") for r in o.read_text(encoding="utf-8").splitlines()[1:]]
        return rows, buf.getvalue()

    def test_filters_nodes_and_edges(self):
        H = "text/html; charset=UTF-8"
        internal = [("https://a.vn/", H, "200", "Indexable"), ("https://a.vn/x/", H, "200", "Indexable"),
                    ("https://a.vn/y/", H, "200", "Indexable"), ("https://a.vn/noindex/", H, "200", "Non-Indexable"),
                    ("https://a.vn/anh.webp", "image/webp", "200", "Indexable"), ("https://a.vn/cu/", H, "301", "Non-Indexable")]
        inl = [("Hyperlink", "https://a.vn/", "https://a.vn/x/", "true", "Navigation"),
               ("Hyperlink", "https://a.vn/", "https://a.vn/y/", "true", "Content"),
               ("Hyperlink", "https://a.vn/x/", "https://a.vn/y/#muc-2", "true", "Content"),
               ("Hyperlink", "https://a.vn/y/", "https://a.vn/", "true", "Header"),
               ("Hyperlink", "https://a.vn/noindex/", "https://a.vn/x/", "true", "Content"),
               ("Hyperlink", "https://a.vn/y/", "https://a.vn/x/", "false", "Content"),
               ("Image", "https://a.vn/x/", "https://a.vn/anh.webp", "true", "Content"),
               ("Hyperlink", "https://a.vn/x/", "https://a.vn/x/", "true", "Content"),
               ("Hyperlink", "https://a.vn/x/", "https://a.vn/cu/", "true", "Content")]
        rows, out = self.run_pr(internal, inl)
        self.assertEqual(len(rows), 3)
        self.assertIn("3 trang", out)
        self.assertIn("4 cạnh", out)
        by_url = {r[1]: r for r in rows}
        self.assertNotIn("https://a.vn/noindex/", by_url)
        self.assertEqual(rows[0][1], "https://a.vn/y/")
        self.assertEqual(by_url["https://a.vn/y/"][3], "2")
        self.assertEqual(by_url["https://a.vn/y/"][4], "2")
        self.assertEqual(by_url["https://a.vn/x/"][3], "1")
        total = sum(float(r[2]) for r in rows)
        self.assertAlmostEqual(total, 1000, delta=0.01)

    def test_no_nodes_exits(self):
        with self.assertRaises(SystemExit):
            self.run_pr([("https://a.vn/", "text/html", "200", "Non-Indexable")], [])

    def test_missing_column_exits(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t)
        i = Path(t) / "i.csv"
        write_csv(i, ("Address", "Status Code"), [("https://a.vn/", "200")])
        with self.assertRaises(SystemExit):
            pagerank.load_pages(str(i))


def html_page(robots="index, follow", canonical=None, links=()):
    head = f'<meta name="robots" content="{robots}"/>' if robots else ""
    if canonical:
        head += f'<link rel="canonical" href="{canonical}" />'
    body = "".join(f'<a href="{x}">x</a>' for x in links)
    return f"<html><head>{head}</head><body>{body}</body></html>"


NAV = ["/", "/dich-vu/", "/lien-he/", "https://zalo.me/123", "/seo/#top"]


class IndexProbe(unittest.TestCase):
    def test_query_url_cannot_prove_index(self):
        """Site agency mẫu 18/10/2026: URL gắn ?nc= làm theme trả noindex, đề xuất báo nhầm 35 trang noindex."""
        r = index_probe.probe_row("https://a.vn/case/x/?nc=123", 200, {}, html_page("follow, noindex"), "index")
        self.assertEqual(r["query"], "1")
        self.assertTrue(r["ket_qua"].startswith("lệch: URL có query"))
        r = index_probe.probe_row("https://a.vn/?s=seo", 200, {}, html_page("follow, noindex"), "noindex")
        self.assertEqual(r["ket_qua"], "đạt")

    def test_clean_url_index_and_canonical(self):
        r = index_probe.probe_row("https://a.vn/seo/page/2/", 200, {}, html_page(canonical="https://a.vn/seo/page/2/"), "index")
        self.assertEqual((r["self_canonical"], r["ket_qua"]), ("1", "đạt"))
        r = index_probe.probe_row("https://a.vn/seo/page/2/", 200, {}, html_page(canonical="https://a.vn/seo/"), "index")
        self.assertEqual(r["ket_qua"], "lệch: canonical không tự trỏ")
        r = index_probe.probe_row("https://a.vn/seo/", 200, {"X-Robots-Tag": "noindex"}, html_page(canonical="https://a.vn/seo/"), "index")
        self.assertEqual(r["ket_qua"], "lệch: noindex")
        r = index_probe.probe_row("/seo/", 200, {}, html_page(canonical="http://HOST/seo/"), "index")
        self.assertEqual(r["ket_qua"], "đạt")

    def test_sitemap_loc_count(self):
        xml = "<urlset>" + "".join(f"<url><loc>https://a.vn/c{i}/</loc></url>" for i in range(14)) + "</urlset>"
        self.assertEqual(index_probe.probe_row("https://a.vn/category-sitemap.xml", 200, {}, xml, "loc=14")["ket_qua"], "đạt")
        self.assertTrue(index_probe.probe_row("https://a.vn/category-sitemap.xml", 200, {}, xml, "loc>=15")["ket_qua"].startswith("lệch"))

    def test_real_pagination(self):
        p1 = html_page(links=NAV + ["/seo/bai-1/", "/seo/bai-2/", "/seo/page/2/"])
        p2 = html_page(links=NAV + ["/seo/bai-3/", "/seo/bai-4/", "/seo/", "/seo/page/3/"])
        r = index_probe.compare_pages(p1, p2, "https://a.vn/seo/", "https://a.vn/seo/page/2/")
        self.assertEqual(r["only_p2"], 2)

    def test_fake_pagination_ignores_pager_links(self):
        """Site agency mẫu 17/10/2026: /blog/page/2/ lặp đúng danh sách /blog/. Chỉ link phân trang khác nhau."""
        lst = NAV + ["/seo/bai-1/", "/seo/bai-2/"]
        p1 = html_page(links=lst + ["/blog/page/2/"])
        p2 = html_page(links=lst + ["/blog/", "/blog/page/3/", "/blog/?paged=3"])
        r = index_probe.compare_pages(p1, p2, "https://a.vn/blog/", "https://a.vn/blog/page/2/")
        self.assertEqual(r["only_p2"], 0)

    def test_empty_extraction_is_error(self):
        """Lượt đo 17/10/2026 ra md5 d41d8cd9 (chuỗi rỗng) cho danh sách bài: bộ trích hỏng, không phải trang trùng."""
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t)
        f1, f2 = Path(t) / "1.html", Path(t) / "2.html"
        f1.write_text(html_page(links=NAV + ["/seo/bai-1/"]), encoding="utf-8")
        f2.write_text("<html><body><div data-list='js'></div></body></html>", encoding="utf-8")
        a = type("A", (), {"p1": "https://a.vn/seo/", "p2": "https://a.vn/seo/page/2/", "html1": str(f1),
                           "html2": str(f2), "delay": 0})()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(index_probe.cmd_paged(a), 1)

    def test_fetch_does_not_follow_redirect(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/cu/":
                    self.send_response(301)
                    self.send_header("Location", "/moi/")
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("X-Robots-Tag", "noindex, nofollow")
                self.end_headers()
                self.wfile.write(html_page(canonical="/moi/").encode())

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        base = f"http://127.0.0.1:{srv.server_port}"
        code, headers, _ = index_probe.fetch(base + "/cu/")
        self.assertEqual(code, 301)
        self.assertEqual({k.lower(): v for k, v in headers.items()}["location"], "/moi/")
        r = index_probe.probe_row(base + "/moi/", *index_probe.fetch(base + "/moi/"), "index")
        self.assertEqual(r["ket_qua"], "lệch: noindex")


@unittest.skipUnless(shutil.which("php"), "không có php")
class RobotsPublicTest(unittest.TestCase):
    STUB = ("<?php $GLOBALS['f'] = array(); function add_filter($h, $cb, $p = 10) { $GLOBALS['f'][] = array($h, $cb(), $p); }\n"
            "%s include '%s'; echo json_encode($GLOBALS['f']);")

    def run_php(self, define):
        code = self.STUB % (define, SCRIPTS / "robots-public-test.php")
        return json.loads(subprocess.run(["php", "-r", code[5:]], capture_output=True, text=True, check=True).stdout)

    def test_only_on_staging(self):
        self.assertEqual(self.run_php("define('WP_ENVIRONMENT_TYPE', 'staging');"), [["pre_option_blog_public", "1", 99]])
        self.assertEqual(self.run_php("define('WP_ENVIRONMENT_TYPE', 'production');"), [])
        self.assertEqual(self.run_php(""), [])


if __name__ == "__main__":
    unittest.main()
