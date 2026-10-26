"""Test offline cho log_clusters.py: fixture log tự dựng, không mạng, không model. Chạy: python3 -B tests/test_log_clusters.py"""
import gzip
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "log_clusters.py"
spec = importlib.util.spec_from_file_location("log_clusters", SCRIPT)
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

GB = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
LOG = [
    f'66.249.66.1 - - [15/Oct/2026:10:00:00 +0700] "GET /dich-vu-seo/ HTTP/1.1" 200 512 "-" "{GB}"',
    f'66.249.66.1 - - [15/Oct/2026:10:00:01 +0700] "GET /dich-vu-seo HTTP/1.1" 301 0 "-" "{GB}"',
    f'66.249.66.1 - - [16/Oct/2026:10:00:00 +0700] "GET /blog-a/?utm_source=x HTTP/1.1" 200 512 "-" "{GB}"',
    f'66.249.66.1 - - [16/Oct/2026:10:00:02 +0700] "GET /wp-content/a.css?ver=1 HTTP/1.1" 200 512 "-" "{GB}"',
    f'66.249.66.1 - - [16/Oct/2026:10:00:03 +0700] "GET /tag/cu/ HTTP/1.1" 404 0 "-" "{GB}"',
    # Bot giả UA: IP không có trong danh sách đã xác minh.
    f'1.2.3.4 - - [16/Oct/2026:11:00:00 +0700] "GET /blog-b/ HTTP/1.1" 200 512 "-" "{GB}"',
    '40.77.167.1 - - [16/Oct/2026:12:00:00 +0700] "GET /blog-b/ HTTP/1.1" 200 512 "-" "Mozilla/5.0 (compatible; bingbot/2.0)"',
    # Ca thật 06–19/10: công cụ audit nội bộ gọi trang có ?shotx=, không phải bot tìm kiếm.
    '10.0.0.1 - - [17/Oct/2026:09:00:00 +0700] "GET /dich-vu-seo/?shotx=1 HTTP/1.1" 200 512 "-" "agency-link-audit/1.0"',
    'dòng hỏng không đúng định dạng',
    f'66.249.66.1 - - [20/Oct/2026:10:00:00 +0700] "GET /blog-b/ HTTP/1.1" 200 512 "-" "{GB}"',
]


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


class LogClusters(unittest.TestCase):
    def setUp(self):
        t = self.t = Path(tempfile.mkdtemp())
        with gzip.open(t / "access.log.gz", "wt", encoding="utf-8") as f:
            f.write("\n".join(LOG) + "\n")
        (t / "map.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [
            {"url": "https://www.x.test/dich-vu-seo/", "cluster": 1, "title": "Dịch vụ SEO"},
            {"url": "https://x.test/blog-a/", "cluster": 3}, {"url": "https://x.test/blog-b/", "cluster": 3},
            {"url": "https://x.test/blog-c/", "cluster": 3}]), encoding="utf-8")
        (t / "clusters.json").write_text(json.dumps([{"cluster": 1, "name": "Dịch vụ", "cos_to_core": 0.95},
                                                     {"cluster": 3, "name": "SEO", "cos_to_core": 0.88}]), encoding="utf-8")
        (t / "core.txt").write_text("https://x.test/dich-vu-seo/\n", encoding="utf-8")
        (t / "ips.txt").write_text("66.249.66.1\n", encoding="utf-8")

    def run_it(self, *extra):
        t = self.t
        lc.main(["--log", str(t / "access.log.gz"), "--site", "https://x.test", "--map", str(t / "map.jsonl"),
                 "--clusters", str(t / "clusters.json"), "--core", str(t / "core.txt"), "--out-dir", str(t / "w"), *extra])
        return {r["cluster"]: r for r in jl(t / "w" / "clusters.jsonl")}

    def test_verified_and_date_filter(self):
        rows = self.run_it("--verified-ips", str(self.t / "ips.txt"), "--to", "2026-10-19")
        self.assertEqual(rows[1]["hits"], 2)          # / và bản không có dấu "/" gộp làm một URL
        self.assertTrue(rows[1]["important"])        # cụm chứa URL lõi
        self.assertEqual(rows[3]["hits"], 1)          # query bị bỏ; IP giả và ngày 20/10 không tính
        self.assertEqual(rows[3]["pages_crawled"], 1)
        outside = jl(self.t / "w" / "outside_map.jsonl")
        self.assertEqual(outside, [{"folder": "/tag/", "hits": 1}])
        core = jl(self.t / "w" / "core_urls.jsonl")[0]
        self.assertEqual(core["status"], {"200": 1, "301": 1})
        text = (self.t / "w" / "report.md").read_text(encoding="utf-8")
        self.assertNotIn("66.249.66.1", text)
        self.assertIn("'dòng không parse được': 1", text)

    def test_unverified_counts_self_declared(self):
        rows = self.run_it()
        self.assertEqual(rows[3]["hits"], 3)          # blog-a, blog-b từ IP giả, blog-b ngày 20/10
        self.assertIn("hit bot tự khai", (self.t / "w" / "report.md").read_text(encoding="utf-8"))

    def test_ols_line_and_more_bots(self):
        ols = ("'- 216.73.216.56 - - [19/Oct/2026:15:41:04 +0700] \"GET /seo/ HTTP/2\" 200 18770 \"-\" "
               "\"Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)\"'")
        m = lc.LINE.match(ols)
        self.assertIsNotNone(m)
        self.assertEqual((m["ip"], m["path"], m["status"]), ("216.73.216.56", "/seo/", "200"))
        self.assertEqual(lc.bot_of(m["ua"]), "claudebot")
        std = '66.249.66.1 - - [18/Oct/2026:10:00:00 +0700] "GET / HTTP/1.1" 200 5 "-" "Googlebot/2.1"'
        self.assertEqual(lc.LINE.match(std)["ip"], "66.249.66.1")
        self.assertEqual(lc.bot_of("Mozilla/5.0 (compatible; Bytespider)"), "bytespider")
        self.assertEqual(lc.bot_of("GoogleOther"), "googleother")

    def test_internal_tool_is_not_bot(self):
        self.assertIsNone(lc.bot_of("agency-link-audit/1.0"))
        self.assertEqual(lc.bot_of("Mozilla/5.0 (compatible; GPTBot/1.2)"), "gptbot")


if __name__ == "__main__":
    unittest.main()
