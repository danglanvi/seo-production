# Test offline cho img_display_width.mjs (Chrome headless, server giả 127.0.0.1) và img_width_report.py (JSON dựng tay).
# Ca hỏng thật: (1) 18/10/2026 trang của site mẫu 2 tải ảnh thừa 27-414 KB mỗi trang vì ảnh gốc rộng hơn nhiều so với bề rộng hiển thị;
# (2) luật M28: bật cờ mobile của CDP làm viewport bố cục và scrollWidth lệch, nên script phải đo bằng mobile:false và ghi innerWidth thật;
# (3) đo nhầm đích (trang 404, sai title) cho số vô nghĩa: guard thoát mã 4.
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixtures import SCRIPTS, run  # noqa: E402

CHROME = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HAS_CHROME = os.path.exists(CHROME)


def jpeg(w, h):
    from PIL import Image
    b = io.BytesIO()
    Image.new('RGB', (w, h), (40, 120, 200)).save(b, 'JPEG', quality=80)
    return b.getvalue()


PAGE = '''<!doctype html><html><head><meta charset="utf-8"><title>Trang đo ảnh</title><style>
body{margin:0}.col{max-width:300px}.hidden{display:none}
</style></head><body>
<div class="col"><img id="big" src="/big.jpg" style="width:100%" alt=""></div>
<img id="ok" src="/ok.jpg" style="width:200px" alt="">
<img id="hero" src="/hero-720.jpg" srcset="/hero-400.jpg 400w, /hero-720.jpg 720w, /hero-1600.jpg 1600w" sizes="100vw" style="width:100%" alt="">
<img class="hidden" src="/hid.jpg" alt="">
<img id="vec" src="/logo.svg" style="width:50px" alt="">
<img id="lazy" loading="lazy" src="/lazy.jpg" style="margin-top:3000px;width:150px" alt="">
</body></html>'''
IMAGES = {'/big.jpg': (1200, 800), '/ok.jpg': (200, 120), '/hero-400.jpg': (400, 200), '/hero-720.jpg': (720, 360), '/hero-1600.jpg': (1600, 800),
          '/hid.jpg': (900, 900), '/lazy.jpg': (150, 90)}


class Site:
    def __init__(self):
        site = self
        self.hits = []

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                p = self.path.split('?')[0]
                site.hits.append(p)
                if p in IMAGES:
                    body, ct, code = jpeg(*IMAGES[p]), 'image/jpeg', 200
                elif p == '/logo.svg':
                    body, ct, code = b'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"/>', 'image/svg+xml', 200
                elif p == '/404':
                    body, ct, code = '<title>Không tìm thấy</title>'.encode(), 'text/html; charset=utf-8', 404
                elif p == '/':
                    body, ct, code = PAGE.encode(), 'text/html; charset=utf-8', 200
                else:
                    body, ct, code = b'', 'text/plain', 404
                self.send_response(code)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()

    def url(self, p='/'):
        return 'http://127.0.0.1:%d%s' % (self.port, p)


def measure(*argv, timeout=150):
    return run('img_display_width.mjs', *argv, timeout=timeout)


def by_src(vp):
    return {i['src']: i for i in vp['images']}


@unittest.skipUnless(HAS_CHROME, 'cần Chrome (CHROME_BIN)')
class DisplayWidth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site()
        cls.site.__enter__()
        r = measure('--url', cls.site.url(), '--widths', '360,768')
        assert r.returncode == 0, r.stderr
        cls.res = json.loads(r.stdout)
        cls.stderr = r.stderr

    @classmethod
    def tearDownClass(cls):
        cls.site.__exit__()

    def test_viewport_is_real_and_not_mobile_flag(self):
        # Ca hỏng thật M28: viewport thật phải đúng bề rộng yêu cầu, kể cả 360 (dưới mức 500 của cửa sổ headless).
        self.assertEqual([v['innerWidth'] for v in self.res['viewports']], [360, 768])
        for v in self.res['viewports']:
            self.assertLessEqual(v['scrollWidth'], v['innerWidth'])
        with open(os.path.join(SCRIPTS, 'img_display_width.mjs'), encoding='utf-8') as f:
            src = f.read()
        self.assertIn('mobile: false', src)
        self.assertNotIn('mobile: true', src)

    def test_display_and_natural_widths(self):
        v360, v768 = self.res['viewports']
        big = by_src(v360)['/big.jpg']
        self.assertEqual(big['naturalWidth'], 1200)
        self.assertEqual(big['fileWidth'], 1200)
        self.assertAlmostEqual(big['displayWidth'], 300, delta=1)   # cột 300 px, ảnh width:100%
        self.assertTrue(big['visible'])
        self.assertAlmostEqual(by_src(v360)['/ok.jpg']['displayWidth'], 200, delta=0.5)
        self.assertGreater(big['bytes'], 0)

    def test_srcset_candidate_changes_with_viewport(self):
        v360, v768 = self.res['viewports']
        self.assertEqual(by_src(v360)['/hero-720.jpg']['fileWidth'], 400)
        self.assertEqual(by_src(v768)['/hero-720.jpg']['fileWidth'], 1600)
        # naturalWidth của trình duyệt đã chia theo sizes (srcset w): 360 chứ không phải 400 px của file. Đo bằng naturalWidth sẽ ra số sai.
        self.assertEqual(by_src(v360)['/hero-720.jpg']['naturalWidth'], 360)
        self.assertEqual(by_src(v360)['/hero-720.jpg']['srcsetWidths'], [400, 720, 1600])

    def test_lazy_image_is_loaded_without_scrolling(self):
        lazy = by_src(self.res['viewports'][0])['/lazy.jpg']
        self.assertEqual(lazy['naturalWidth'], 150)
        self.assertEqual(lazy['fileWidth'], 150)
        self.assertEqual(lazy['loading'], 'lazy')
        self.assertTrue(lazy['complete'])

    def test_hidden_image_is_not_visible(self):
        self.assertFalse(by_src(self.res['viewports'][0])['/hid.jpg']['visible'])

    def test_guard_line_and_json_fields(self):
        self.assertIn('GUARD host=127.0.0.1:%d status=200' % self.site.port, self.stderr)
        self.assertEqual(self.res['status'], 200)
        self.assertEqual(self.res['dpr'], 1)
        self.assertIn('IMG_WIDTH', self.stderr)

    def test_report_flags_oversized_ev(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'm.json')
            with open(p, 'w') as f:
                json.dump(self.res, f)
            r = run('img_width_report.py', p, '--json')
            self.assertEqual(r.returncode, 0, r.stderr)
            rows = {x['src']: x for x in json.loads(r.stdout)}
            self.assertEqual(rows['/big.jpg']['verdict'], 'thừa')          # 1200 px cho khung 300 px ở mọi viewport
            self.assertGreater(rows['/big.jpg']['kb_thừa_ước_tính'], 0)
            self.assertEqual(rows['/big.jpg']['cần_px_tối_đa'], 300)
            self.assertEqual(rows['/ok.jpg']['verdict'], 'đạt')
            self.assertEqual(rows['/lazy.jpg']['verdict'], 'đạt')
            self.assertEqual(rows['/hero-720.jpg']['verdict'], 'thừa một phần')  # 360 px đạt, 768 px chọn nhầm 1600w
            self.assertEqual(rows['/hero-720.jpg']['viewport_thừa'], [768])
            self.assertNotIn('/hid.jpg', rows)    # ảnh ẩn bỏ qua
            self.assertNotIn('/logo.svg', rows)   # SVG bỏ qua
            self.assertEqual(run('img_width_report.py', p, '--strict').returncode, 1)
            table = run('img_width_report.py', p)
            self.assertIn('IMG_WIDTH_REPORT', table.stdout)
            self.assertLess(table.stdout.index('/big.jpg'), table.stdout.index('/ok.jpg'))  # ảnh thừa xếp trước

    def test_dpr_two_makes_small_image_blurry(self):
        r = measure('--url', self.site.url(), '--widths', '768', '--dpr', '2')
        self.assertEqual(r.returncode, 0, r.stderr)
        res = json.loads(r.stdout)
        self.assertEqual(res['dpr'], 2)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'm.json')
            with open(p, 'w') as f:
                f.write(r.stdout)
            rows = {x['src']: x for x in json.loads(run('img_width_report.py', p, '--json').stdout)}
        self.assertEqual(rows['/ok.jpg']['verdict'], 'mờ')   # 200 px cho khung 200 px CSS ở màn hình dpr 2 cần 400 px

    def test_out_requires_apply_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 'ra.json')
            r = measure('--url', self.site.url(), '--widths', '360', '--out', out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(os.path.exists(out))
            self.assertIn('Dry-run', r.stderr)
            self.assertTrue(json.loads(r.stdout)['viewports'])
            r2 = measure('--url', self.site.url(), '--widths', '360', '--out', out, '--apply')
            self.assertEqual(r2.returncode, 0, r2.stderr)
            with open(out) as f:
                self.assertEqual(json.load(f)['widths'], [360])
            self.assertEqual(r2.stdout, '')
            r3 = measure('--url', self.site.url(), '--widths', '360', '--out', out, '--apply')
            self.assertEqual(r3.returncode, 1)
            self.assertIn('không ghi đè', r3.stderr)

    def test_ev_guard_wrong_target(self):
        r = measure('--url', self.site.url('/404'), '--widths', '360')
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn('HTTP 404', r.stderr)
        r2 = measure('--url', self.site.url(), '--widths', '360', '--expect', 'Đăng nhập')
        self.assertEqual(r2.returncode, 4, r2.stderr)
        self.assertIn('title', r2.stderr)
        r3 = measure('--url', self.site.url('/404'), '--widths', '360', '--no-guard')
        self.assertEqual(r3.returncode, 0, r3.stderr)
        r4 = measure('--url', self.site.url(), '--widths', '360', '--expect', 'trang đo ảnh')
        self.assertEqual(r4.returncode, 0, r4.stderr)


class NoChrome(unittest.TestCase):
    def test_bad_args(self):
        for argv in ([], ['--url', 'http://127.0.0.1:1/', '--widths', 'abc'], ['--url', 'http://127.0.0.1:1/', '--widths', '100'], ['--url', 'http://127.0.0.1:1/', '--dpr', '9'],
                     ['--url', 'khong-phai-url'], ['--url', 'http://127.0.0.1:1/', '--apply']):
            self.assertEqual(measure(*argv).returncode, 2, argv)
        self.assertEqual(measure('--help').returncode, 0)

    def test_tunnel_closed_exits_4_without_chrome(self):
        r = measure('--url', 'http://tunnel-tat.test:1/', '--resolve', 'tunnel-tat.test=127.0.0.1', '--widths', '360')
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn('tunnel', r.stderr)


class Report(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.t.cleanup()

    def write(self, name, data):
        p = os.path.join(self.t.name, name)
        with open(p, 'w') as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        return p

    @staticmethod
    def img(src, disp, nat, bytes_=50000, visible=True, cur=None):
        return {'src': src, 'currentSrc': cur or 'http://x' + src, 'naturalWidth': nat, 'naturalHeight': nat, 'displayWidth': disp, 'displayHeight': disp, 'visible': visible,
                'bytes': bytes_, 'srcsetWidths': [], 'loading': '', 'complete': True}

    def doc(self, dpr, rows):
        return {'url': 'http://x/', 'dpr': dpr, 'widths': [360], 'viewports': [{'vw': 360, 'innerWidth': 360, 'scrollWidth': 360, 'images': rows}]}

    def test_thresholds_and_waste(self):
        p = self.write('a.json', self.doc(1, [self.img('/a.jpg', 300, 300), self.img('/b.jpg', 300, 330), self.img('/c.jpg', 300, 450, bytes_=100000),
                                              self.img('/d.jpg', 300, 200), self.img('/tiny.gif', 1, 1), self.img('/i.svg', 40, 400)]))
        rows = {x['src']: x for x in json.loads(run('img_width_report.py', p, '--json').stdout)}
        self.assertEqual(rows['/a.jpg']['verdict'], 'đạt')
        self.assertEqual(rows['/b.jpg']['verdict'], 'đạt')         # 1,1 dưới ngưỡng 1,25
        self.assertEqual(rows['/c.jpg']['verdict'], 'thừa')        # 1,5
        self.assertEqual(rows['/d.jpg']['verdict'], 'mờ')          # 0,67
        self.assertNotIn('/tiny.gif', rows)
        self.assertNotIn('/i.svg', rows)
        self.assertAlmostEqual(rows['/c.jpg']['kb_thừa_ước_tính'], 100000 * (1 - (300 / 450) ** 2) / 1024.0, delta=0.1)
        self.assertEqual(run('img_width_report.py', p, '--strict').returncode, 1)
        self.assertEqual(run('img_width_report.py', p, '--tolerance', '2', '--blur', '0.5', '--strict').returncode, 0)

    def test_merge_two_dpr_files(self):
        a = self.write('d1.json', self.doc(1, [self.img('/a.jpg', 200, 200)]))
        b = self.write('d2.json', self.doc(2, [self.img('/a.jpg', 200, 200)]))
        r = run('img_width_report.py', a, b, '--json')
        rows = json.loads(r.stdout)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['verdict'], 'mờ')  # đạt ở dpr 1 nhưng thiếu nét ở dpr 2
        self.assertEqual(rows[0]['cần_px_tối_đa'], 400)

    def test_bad_inputs(self):
        self.assertEqual(run('img_width_report.py', os.path.join(self.t.name, 'khong-co.json')).returncode, 2)
        self.assertEqual(run('img_width_report.py', self.write('hong.json', '{"viewports": [')).returncode, 2)
        self.assertEqual(run('img_width_report.py', self.write('thieu.json', {'foo': 1})).returncode, 2)
        self.assertEqual(run('img_width_report.py', self.write('ok.json', self.doc(1, [])), '--tolerance', '1').returncode, 2)

    def test_help(self):
        self.assertEqual(run('img_width_report.py', '--help').returncode, 0)


if __name__ == '__main__':
    unittest.main()
