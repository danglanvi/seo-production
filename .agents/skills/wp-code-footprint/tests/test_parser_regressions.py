"""Các ca từng làm bộ đếm regex báo sạch hoặc báo comment giả."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

S = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(S))
from scan_html import scan_file


class ParserRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def scan(self, html):
        path = self.root / "page.html"
        path.write_text(html, encoding="utf-8")
        return scan_file(path)

    def test_regex_strings_template_and_line_offset(self):
        r = self.scan('''<script>
const re = /[//]phiên/;
const s = `dòng đầu
// chuỗi phiên, không phải comment`;
const t = `${/* phiên thật */ 1}`;
// đợt thật
</script>''')
        self.assertTrue(r["scan_complete"], r["scan_errors"])
        self.assertEqual([(c["text"], c["line"]) for c in r["comments_in_code"]],
                         [("/* phiên thật */", 5), ("// đợt thật", 6)])

    def test_script_data_and_deferred_external(self):
        r = self.scan('''<script type="application/ld+json">{"url":"https://x/phiên"}</script>
<script type="importmap">{"imports":{}}</script>
<script data-src="external.js">/* placeholder phiên */</script>
<script type="application/x-javascript">/* phiên JS MIME cũ */</script>
<script type="module">export const a=1; // phiên thật
</script>''')
        self.assertTrue(r["scan_complete"], r["scan_errors"])
        self.assertEqual(r["inline_scripts"], 2)
        self.assertEqual(r["inline_data_scripts"], 2)
        self.assertGreater(r["inline_data_bytes"], 0)
        self.assertEqual(len(r["comments_in_code"]), 2)

    def test_css_strings_urls_and_comments(self):
        r = self.scan('''<style>.a{content:"/* phiên giả */";background:url(https://x/phiên/*fake*/x)}
/* đợt thật */ .b{color:red}</style>''')
        self.assertEqual([c["text"] for c in r["comments_in_code"]], ["/* đợt thật */"])

    def test_invalid_js_and_css_are_incomplete(self):
        r = self.scan('<script>const x = ;</script><style>/* chưa đóng</style>')
        self.assertFalse(r["scan_complete"])
        self.assertEqual(len(r["scan_errors"]), 2)

    def test_missing_parser_is_not_zero_clean(self):
        path = self.root / "page.html"
        path.write_text('<script>const x=1;</script>')
        env = dict(os.environ, ACORN_PATH=str(self.root / "missing-module"))
        run = subprocess.run([sys.executable, "-I", str(S / "footprint_count.py"), str(path)],
                             env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("scan_complete=0", run.stdout)

    def test_same_length_scripts_not_deduplicated_and_utf8_bytes(self):
        for name, code in (("a", "const a='ế';"), ("b", "const b='ế';"), ("c", "const a='ế';")):
            (self.root / f"{name}.html").write_text(f'<script id="same">{code}</script>')
        out = self.root / "out"
        run = subprocess.run([sys.executable, "-I", str(S / "scan_html.py"), str(self.root), str(out)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        rows = [json.loads(s) for s in (out / "jev_scripts.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["state"]["bytes"], len("const a='ế';".encode("utf-8")))

    def test_heading_nested_text(self):
        r = self.scan('<main><section><h2><span>Tiêu </span><strong>đề</strong></h2></section></main>')
        self.assertEqual(r["sections_no_heading"], 0)
        self.assertEqual(r["headings"][0]["text"], "Tiêu đề")

    def test_unclosed_script_is_incomplete(self):
        r = self.scan('<script>/* phiên chưa đóng thẻ */')
        self.assertFalse(r["scan_complete"])

    def test_comparison_rejects_missing_page(self):
        before, after = self.root / "before", self.root / "after"
        before.mkdir()
        after.mkdir()
        (before / "a.html").write_text('<p>A</p>')
        (before / "b.html").write_text('<p>B</p>')
        (after / "a.html").write_text('<p>A</p>')
        run = subprocess.run([sys.executable, "-I", str(S / "compare.py"), str(before), str(after)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("INCOMPLETE", run.stderr)

    def test_long_html_comment_is_counted_in_full(self):
        path = self.root / "page.html"
        path.write_text('<!--' + ('x' * 350) + ' phiên -->')
        run = subprocess.run([sys.executable, "-I", str(S / "footprint_count.py"), str(path)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("htmlcomment_quytrinh=1", run.stdout)


if __name__ == "__main__":
    unittest.main()
