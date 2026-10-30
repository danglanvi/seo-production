# Test cho trace_fn.mjs: trace long task theo hàm JS. Chrome chạy trên server giả 127.0.0.1, không gọi mạng ngoài.
# Ca thật: lớp 6 site agency mẫu 27/10/2026, trace theo hàm tìm ra long task JS duy nhất là khởi tạo slider; phần còn lại là layout.
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import SiteStub, run  # noqa: E402

CHROME = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HAS_CHROME = os.path.exists(CHROME)

HEAVY = ('<h1>Xin chào</h1>\n<script>\nfunction heavyFn(){var t=performance.now();while(performance.now()-t<160){}}\n'
         'addEventListener("load",function(){setTimeout(heavyFn,30)});\n</script>')


class TraceFnArgs(unittest.TestCase):
    def test_help_and_missing_url(self):
        self.assertEqual(run('trace_fn.mjs', '--help').returncode, 0)
        self.assertEqual(run('trace_fn.mjs').returncode, 2)

    def test_bad_dev_exit_2(self):
        self.assertEqual(run('trace_fn.mjs', '--url', 'http://127.0.0.1:9/', '--dev', 'tablet').returncode, 2)


@unittest.skipUnless(HAS_CHROME, 'cần Chrome (đặt CHROME_BIN)')
class TraceFnChrome(unittest.TestCase):
    def test_finds_named_js_long_task_and_keeps_clean_url(self):
        with SiteStub(body=HEAVY) as s, tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 't.json')
            r = run('trace_fn.mjs', '--url', s.url('/ok/'), '--runs', '1', '--settle', '1500', '--expect', 'trang thử', '--out', out, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(r.stdout.startswith('GUARD host=127.0.0.1:'), r.stdout)
            with open(out) as f:
                res = json.load(f)[0]
            js = [t for t in res['long_tasks'] if t['nguon'] == 'js']
            self.assertTrue(js, res)
            self.assertTrue(any('heavyFn@(inline)' in c and 'function heavyFn' in c for t in js for c in t['calls']), js)
            self.assertIn('TRACE_FN_DONE runs=1', r.stdout)
            self.assertEqual([p for p in s.paths if p.startswith('/ok')], ['/ok/'], s.paths)  # không thêm tham số vào URL

    def test_layout_only_page_has_no_js_task(self):
        with SiteStub() as s:
            r = run('trace_fn.mjs', '--url', s.url('/ok'), '--runs', '1', '--settle', '800', timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            res = json.loads([x for x in r.stdout.splitlines() if x.startswith('{')][0])
            self.assertEqual([t for t in res['long_tasks'] if t['nguon'] == 'js'], [])

    def test_expect_path_mismatch_exit_4(self):
        with SiteStub() as s:
            r = run('trace_fn.mjs', '--url', s.url('/ok'), '--runs', '1', '--settle', '300', '--expect-path', '/trang-khac/', timeout=120)
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
            self.assertIn('--expect-path', r.stderr)
            self.assertNotIn('TRACE_FN_DONE runs=1', r.stdout)

    def test_404_exit_4(self):
        with SiteStub(status_map={'/gone': 404}) as s:
            r = run('trace_fn.mjs', '--url', s.url('/gone'), '--runs', '1', '--settle', '300', timeout=120)
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main()
