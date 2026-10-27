import contextlib
import importlib.util
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/drift_tracker.py"
spec = importlib.util.spec_from_file_location("drift", SCRIPT)
drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift)

HTML = '''<html><head><title>SEO &amp; GEO</title>
<link rel="canonical" href="/article"><meta name="description" content="Mô tả">
<link rel="alternate" hreflang="vi" href="/vi">
<script type="application/ld+json">{"@graph":[{"@type":"Article"},{"@type":["Organization","Thing"]}]}</script>
</head><body><h1>Hướng <em>dẫn</em></h1><a href="/next">Next</a>
<a href="https://external.invalid">External</a></body></html>'''


def page(html=HTML):
    values, warnings = drift.extract(html, "https://example.test/article", 200)
    return {"url": "https://example.test/article", "values": values, "error": None,
            "unavailable": ["schema_types"] if warnings else [], "warnings": warnings}


class ExtractionTests(unittest.TestCase):
    def test_raw_html_extracts_nine_elements_and_nested_schema(self):
        result = page()["values"]
        self.assertEqual(set(drift.ELEMENTS), set(result))
        self.assertEqual(["SEO & GEO"], result["title"])
        self.assertEqual(["https://example.test/article"], result["canonical"])
        self.assertEqual({"count": 1, "texts": ["Hướng dẫn"]}, result["h1"])
        self.assertEqual(["Article", "Organization", "Thing"], result["schema_types"])
        self.assertEqual(1, result["internal_links"])

    def test_noindex_and_canonical_change_are_critical(self):
        old = page()
        new = page(HTML.replace('href="/article"', 'href="/other"') + '<meta name="robots" content="noindex">')
        findings, missing = drift.compare({old["url"]: old}, {new["url"]: new})
        self.assertEqual({"canonical", "robots"}, {f["element"] for f in findings})
        self.assertTrue(all(f["severity"] == "CRITICAL" and f["falsifiability"] for f in findings))
        self.assertEqual([], missing)

    def test_fetch_error_does_not_look_like_deleted_elements(self):
        old = page()
        new = {**old, "values": {}, "error": "FETCH_ERROR: TimeoutError"}
        findings, missing = drift.compare({old["url"]: old}, {new["url"]: new})
        self.assertEqual([], findings)
        self.assertEqual(1, len(missing))

    def test_invalid_jsonld_is_not_schema_removal(self):
        old = page()
        new = page(HTML.replace('"@graph":', 'broken:'))
        findings, missing = drift.compare({old["url"]: old}, {new["url"]: new})
        self.assertEqual([], findings)
        self.assertIn("schema_types", missing[0]["reason"])

    def test_link_threshold_and_schema_removal(self):
        self.assertEqual("INFO", drift.severity("internal_links", 10, 8))
        self.assertEqual("MEDIUM", drift.severity("internal_links", 10, 7))
        self.assertEqual("MEDIUM", drift.severity("internal_links", 0, 1))
        self.assertEqual("HIGH", drift.severity("schema_types", ["Article"], []))
        self.assertEqual("MEDIUM", drift.severity("schema_types", [], ["Article"]))


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            html = HTML
            calls = 0

            def do_GET(self):
                type(self).calls += 1
                if self.path == "/redirect":
                    self.send_response(301)
                    self.send_header("Location", "/article")
                    self.end_headers()
                    return
                self.send_response(503 if self.path == "/fail" else 200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("X-Robots-Tag", "noindex" if self.path == "/noindex" else "all")
                self.end_headers()
                self.wfile.write(self.html.encode())

            def log_message(self, *args):
                pass

        cls.handler = Handler
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_redirect_and_http_header_are_recorded(self):
        result = drift.fetch(self.base + "/redirect", interval=0.01)
        self.assertIsNone(result["error"])
        self.assertEqual(301, result["values"]["http"]["redirects"][0]["status"])
        self.assertEqual(self.base + "/article", result["values"]["http"]["final_url"])
        self.assertIn("noindex", drift.fetch(self.base + "/noindex")["values"]["robots"])

    def test_persistent_503_retries_once_and_preserves_known_http_status(self):
        before = self.handler.calls
        result = drift.fetch(self.base + "/fail", interval=0.01)
        self.assertEqual(2, self.handler.calls - before)
        self.assertEqual(503, result["values"]["http"]["status"])
        self.assertEqual(set(drift.ELEMENTS[1:]), set(result["unavailable"]))

    def test_cli_baseline_compare_history_and_immutability(self):
        with tempfile.TemporaryDirectory() as tmp:
            db, urls = Path(tmp) / "drift.sqlite", Path(tmp) / "urls.txt"
            urls.write_text(self.base + "/article\n")
            def run(*args):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = drift.main(["--db", str(db), "--json", *args])
                return code, json.loads(output.getvalue())
            self.handler.html = HTML
            code, baseline = run("baseline", "--urls", str(urls), "--label", "before")
            self.assertEqual(0, code)
            self.handler.html = HTML.replace("SEO &amp; GEO", "New title")
            try:
                code, result = run("compare", "--label", "after")
                self.assertEqual(1, code)
                self.assertEqual("title", result["findings"][0]["element"])
                code, history = run("history", "--element", "title")
                self.assertEqual([["SEO & GEO"], ["New title"]], [r["value"] for r in history["history"]])
                conn = drift.connect(db)
                try:
                    saved, _pages = drift.read_snapshot(conn)
                    self.assertEqual(baseline["snapshot"], saved)
                finally:
                    conn.close()
            finally:
                self.handler.html = HTML

    def test_missing_baseline_never_fetches(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(drift, "fetch") as fetch:
            with contextlib.redirect_stderr(io.StringIO()):
                code = drift.main(["--db", str(Path(tmp) / "absent.sqlite"), "compare", "--label", "after"])
            self.assertEqual(2, code)
            fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
