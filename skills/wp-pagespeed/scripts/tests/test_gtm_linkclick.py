# Test offline cho phần tái phát gtm.linkClick của templates/gtm-delay-loader.php. Chrome headless thật, server giả 127.0.0.1 phục vụ trang
# chứa loader (rút từ template, đổi URL gtm.js sang server giả) và một gtm.js giả trễ 600 ms, cài bộ nghe click lúc chạy như GTM.
# Ca hỏng thật 22/10/2026 (m22-gtm, trang đào tạo của site agency mẫu): loader hoãn nạp gtm.js ở thao tác đầu, khách bấm link Zalo trước khi gtm.js chạy,
# bộ nghe Link Click của GTM chưa cài nên mất click Zalo đầu tiên. Bản mẫu v1.11 (tests/data) tái hiện lỗi, bản mới phải replay đúng một event.
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
NEW = os.path.join(SKILL, 'templates', 'gtm-delay-loader.php')
OLD = os.path.join(HERE, 'data', 'gtm-delay-loader.v1.11.php')
CHROME = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HAS_CHROME = os.path.exists(CHROME)

FAKE_GTM = ("(function(){window.__gtmExec=Date.now();var dl=window.dataLayer=window.dataLayer||[];"
            "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');"
            "if(a)dl.push({event:'gtm.linkClick','gtm.elementUrl':a.href,native:1})},true)})();")


def loader_js(path):
    """Lấy thân script của loader hoãn (khối <script data-no-optimize>) và thay phần PHP, URL gtm.js trỏ về server giả."""
    with open(path, encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'<script data-no-optimize="1">(.*?)</script>', src, re.S)
    assert m, 'không thấy khối loader trong %s' % path
    js = m.group(1)
    js = js.replace("<?php echo TG_GTM_ID; ?>", 'GTM-TEST000').replace("<?php echo (int) TG_GTM_DELAY; ?>", '60000')
    js = js.replace('https://www.googletagmanager.com/', '/')
    assert '<?php' not in js and 'googletagmanager' not in js
    return js


PAGE = '''<!doctype html><html><head><meta charset="utf-8"><title>Trang loader</title><script data-no-optimize="1">%s</script></head>
<body><a id="z" class="zalo-btn" href="#zalo" style="display:block;width:200px;height:60px">Zalo</a>
<div id="d" style="width:200px;height:60px;margin-top:20px">Không phải link</div></body></html>'''


class Site:
    def __init__(self):
        self.pages = {'/new': PAGE % loader_js(NEW), '/old': PAGE % loader_js(OLD)}
        site = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                p = self.path.split('?')[0]
                if p == '/gtm.js':
                    time.sleep(0.6)
                    body, ct = FAKE_GTM.encode(), 'application/javascript'
                elif p in site.pages:
                    body, ct = site.pages[p].encode(), 'text/html; charset=utf-8'
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def url(self, p):
        return 'http://127.0.0.1:%d%s' % (self.port, p)

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def drive(url, mode):
    p = subprocess.run(['node', os.path.join(HERE, 'linkclick_driver.mjs'), '--url', url, '--mode', mode], capture_output=True, text=True, timeout=90)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


class Template(unittest.TestCase):
    def test_php_lint(self):
        php = shutil.which('php')
        if not php:
            self.skipTest('không có php')
        r = subprocess.run([php, '-l', NEW], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_template_keeps_rules_already_in_v111(self):
        with open(NEW, encoding='utf-8') as f:
            t = f.read()
        for needle in ("TG_GTM_NOW_URL", "gclid|gbraid|wbraid|fbclid|ttclid|utm_", "'pointerdown','touchstart','keydown','wheel','scroll','mousemove'",
                       "tg_gtm_now()", "Google Tag Manager (noscript)", 'data-no-optimize="1"'):
            self.assertIn(needle, t)

    def test_marker_matches_inline_script_and_guest_list_documented(self):
        js = loader_js(NEW)
        self.assertIn('gtm-delay-loader', js)           # mục loại trừ "gtm-delay-loader" khớp nội dung inline
        self.assertNotIn('gtm-delay-loader', loader_js(OLD))  # bản cũ chỉ có chuỗi này ở chú thích HTML ngoài thẻ script
        with open(NEW, encoding='utf-8') as f:
            self.assertIn('optm-gm_js_exc', f.read())

    def test_loader_js_is_valid_javascript(self):
        p = subprocess.run(['node', '--check', '-'], input=loader_js(NEW), capture_output=True, text=True)
        # node --check đọc stdin khi không có file; thân script là hàm tự gọi có "return" ở cấp hàm nên hợp lệ.
        self.assertEqual(p.returncode, 0, p.stderr)


@unittest.skipUnless(HAS_CHROME, 'cần Chrome (CHROME_BIN)')
class LinkClickReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site()

    @classmethod
    def tearDownClass(cls):
        cls.site.close()

    def test_ev_old_loader_loses_first_click(self):
        r = drive(self.site.url('/old'), 'early')
        self.assertTrue(r['gtmExec'])
        self.assertEqual(r['clicks'], [], 'bản v1.11 phải tái hiện lỗi mất click đầu tiên')

    def test_new_loader_replays_first_click_once(self):
        r = drive(self.site.url('/new'), 'early')
        self.assertTrue(r['gtmExec'])
        self.assertEqual(r['first'], 'gtm.js')  # gtm.start vẫn là phần tử đầu của dataLayer
        self.assertEqual(len(r['clicks']), 1, r)
        c = r['clicks'][0]
        self.assertFalse(c['native'])           # event do loader tái phát, không phải bộ nghe của gtm.js
        self.assertTrue(c['url'].endswith('#zalo'))
        self.assertEqual((c['id'], c['cls'], c['target'], c['isEl']), ('z', 'zalo-btn', '', True))

    def test_new_loader_no_duplicate_when_click_after_gtm_ready(self):
        r = drive(self.site.url('/new'), 'late')
        self.assertEqual(len(r['clicks']), 1, r)
        self.assertTrue(r['clicks'][0]['native'])  # chỉ bộ nghe của gtm.js, loader không tái phát thêm

    def test_ad_url_loads_at_once_and_never_double_counts(self):
        # URL quảng cáo nạp gtm.js ngay khi trang tải. Click đến sau hay trước khi gtm.js chạy đều phải ra đúng một event, không mất, không trùng.
        r = drive(self.site.url('/new?gclid=test123'), 'early')
        self.assertTrue(r['gtmExec'])
        self.assertEqual(len(r['clicks']), 1, r)

    def test_no_interaction_loads_nothing_and_replays_nothing(self):
        r = drive(self.site.url('/new'), 'none')
        self.assertFalse(r['gtmExec'])
        self.assertEqual(r['clicks'], [])

    def test_click_on_non_link_is_not_replayed(self):
        r = drive(self.site.url('/new'), 'div')
        self.assertTrue(r['gtmExec'])  # nhấn chuột vẫn kích hoạt nạp gtm.js
        self.assertEqual(r['clicks'], [])


if __name__ == '__main__':
    unittest.main()
