# Test offline cho templates/guest-tap.php. Chrome headless thật, server giả 127.0.0.1 phục vụ trang có script của mẫu, một thẻ
# script type="litespeed/javascript" (dấu hiệu JS còn hoãn) và window.__load() giả lượt LiteSpeed nạp JS hoãn: gỡ thẻ đó, gắn handler mở menu,
# phát DOMContentLiteSpeedLoaded. Ca hỏng thật 26/10/2026 (site agency mẫu, CS-26): khách ở lại trang Guest Mode, lần chạm đầu vào nút menu
# mobile không mở vì JS menu chưa nạp. Mẫu phải mở menu đúng một lần, không mở khi bấm chỗ khác, không mở hai lần khi JS đã nạp.
import json
import os
import re
import shutil
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
TPL = os.path.join(SKILL, 'templates', 'guest-tap.php')
CHROME = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HAS_CHROME = os.path.exists(CHROME) and shutil.which('node')


def tap_js():
    with open(TPL, encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'<script id="wps-guest-tap"[^>]*>(.*?)</script>', src, re.S)
    assert m, 'không thấy khối script trong mẫu'
    js = m.group(1).replace('<?php echo wp_json_encode( WPS_GUEST_TAP_SEL ); ?>', json.dumps('#z'))
    assert '<?php' not in js
    return js


PAGE = '''<!doctype html><html><head><meta charset="utf-8"><title>Guest</title></head><body>
<button id="z" style="display:block;width:200px;height:60px">Menu</button>
<div id="d" style="width:200px;height:60px;margin-top:20px">Chữ</div>
<script type="litespeed/javascript">window.__never=1</script>
<script>window.__load=function(){document.querySelector('script[type="litespeed/javascript"]').remove();
document.getElementById('z').addEventListener('click',function(){window.__opened=(window.__opened||0)+1});
document.dispatchEvent(new Event('DOMContentLiteSpeedLoaded'))}</script>
<script>%s</script></body></html>'''


class GuestTap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        body = (PAGE % tap_js()).encode()

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(body)

        cls.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = 'http://127.0.0.1:%d/p' % cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def run_mode(self, mode):
        out = subprocess.run(['node', os.path.join(HERE, 'guesttap_driver.mjs'), '--url', self.url, '--mode', mode],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout.strip().splitlines()[-1])['opened']

    def test_php_lint(self):
        if not shutil.which('php'):
            self.skipTest('không có php')
        out = subprocess.run(['php', '-l', TPL], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    @unittest.skipUnless(HAS_CHROME, 'không có Chrome hoặc node')
    def test_tap_before_load_opens_once(self):
        self.assertEqual(self.run_mode('early'), 1)

    @unittest.skipUnless(HAS_CHROME, 'không có Chrome hoặc node')
    def test_no_tap_no_open(self):
        self.assertEqual(self.run_mode('none'), 0)

    @unittest.skipUnless(HAS_CHROME, 'không có Chrome hoặc node')
    def test_tap_after_load_not_doubled(self):
        self.assertEqual(self.run_mode('late'), 1)

    @unittest.skipUnless(HAS_CHROME, 'không có Chrome hoặc node')
    def test_other_element_ignored(self):
        self.assertEqual(self.run_mode('other'), 0)


if __name__ == '__main__':
    unittest.main()
