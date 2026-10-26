# Test offline cho lam_nong.sh. Server giả trên 127.0.0.1 bắt chước page cache LiteSpeed: khoá cache gồm path, mobile hay desktop,
# khách quay lại (cookie _lscache_vary) và Accept có image/webp. Lượt đầu vào một khoá trả miss, các lượt sau trả hit.
# Ca hỏng thật 21/10/2026 (đợt tốc độ site agency mẫu): (1) bản cũ chỉ làm nóng biến thể plain nên khách thật (Accept có webp) vẫn miss;
# (2) lượt đầu ở 40 URL nhiều khách nhất bản mobile chỉ hit 5% còn desktop 95%, vì danh sách bản thiếu guest-m.
import csv
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import SCRIPTS  # noqa: E402

SCRIPT = os.path.join(SCRIPTS, 'lam_nong.sh')
PAGES = ['/a/', '/b/']


class LsStub:
    def __init__(self):
        self.cache, self.log, self.fail_once, self.counts = set(), [], set(), {}
        self.lock = threading.Lock()
        stub = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body=b'', ctype='text/html', extra=None):
                self.send_response(code)
                self.send_header('Content-Type', ctype)
                for k, v in (extra or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                if self.path.endswith('/guest.vary.php'):
                    return self._send(200, b'', extra={'Set-Cookie': '_lscache_vary=abc123; Path=/'})
                self._send(404)

            def do_GET(self):
                host = 'http://127.0.0.1:%d' % stub.port
                if self.path == '/sitemap_index.xml':
                    return self._send(200, ('<sitemapindex><sitemap><loc>%s/sm-posts.xml</loc></sitemap></sitemapindex>' % host).encode(), 'application/xml')
                if self.path == '/sm-posts.xml':
                    locs = ''.join('<url><loc>%s%s</loc></url>' % (host, p) for p in PAGES)
                    return self._send(200, ('<urlset>%s</urlset>' % locs).encode(), 'application/xml')
                ua, acc, ck = self.headers.get('User-Agent', ''), self.headers.get('Accept', ''), self.headers.get('Cookie', '')
                mobile, ret, webp = 'Mobile' in ua, '_lscache_vary' in ck, 'image/webp' in acc
                with stub.lock:
                    stub.log.append({'path': self.path, 'mobile': mobile, 'ret': ret, 'webp': webp, 'accept': acc})
                    n = stub.counts[self.path] = stub.counts.get(self.path, 0) + 1
                if self.path == '/dead/':
                    return self._send(500, b'loi')
                if self.path in stub.fail_once and n == 1:
                    return self._send(503, b'bao tri')
                key = (self.path, mobile, ret, webp)
                with stub.lock:
                    state = 'hit' if key in stub.cache else 'miss'
                    stub.cache.add(key)
                self._send(200, b'<html></html>', extra={'X-LiteSpeed-Cache': state})

        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()

    @property
    def host(self):
        return 'http://127.0.0.1:%d' % self.port


def warm(host, out, *argv, timeout=180):
    return subprocess.run(['bash', SCRIPT, '--host', host, '-o', out, '-q'] + list(argv), capture_output=True, text=True, timeout=timeout)


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter='\t'))


class LamNong(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.t.name, 'ra.tsv')

    def tearDown(self):
        self.t.cleanup()

    def test_default_sitemap_all_variants_warm_then_hit(self):
        with LsStub() as s:
            r1 = warm(s.host, self.out)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            a = rows(self.out)
            self.assertEqual(len(a), 8)  # 2 URL x 4 bản x 1 kiểu Accept
            self.assertEqual({x['path'] for x in a}, set(PAGES))
            self.assertEqual({x['variant'] for x in a}, {'guest-d', 'guest-m', 'ret-d', 'ret-m'})
            self.assertTrue(all(x['lscache'] == 'miss' and x['code'] == '200' and float(x['ttfb']) >= 0 for x in a))
            out2 = os.path.join(self.t.name, 'ra2.tsv')
            r2 = warm(s.host, out2)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertTrue(all(x['lscache'] == 'hit' for x in rows(out2)), rows(out2))
            self.assertIn('100%', r2.stdout)

    def test_ev_missing_mobile_variant_stays_miss(self):
        # Danh sách bản chỉ có desktop: bản mobile của khách thật vẫn miss (hit 5% ở mobile, 95% ở desktop).
        with LsStub() as s:
            self.assertEqual(warm(s.host, self.out, '-V', 'guest-d,ret-d', '/a/').returncode, 0)
            probe = os.path.join(self.t.name, 'mobile.tsv')
            self.assertEqual(warm(s.host, probe, '-V', 'guest-m', '/a/').returncode, 0)
            self.assertEqual([x['lscache'] for x in rows(probe)], ['miss'])
            # Chạy lại với đủ bản mobile thì lần sau hit.
            probe2 = os.path.join(self.t.name, 'mobile2.tsv')
            self.assertEqual(warm(s.host, probe2, '-V', 'guest-m', '/a/').returncode, 0)
            self.assertEqual([x['lscache'] for x in rows(probe2)], ['hit'])

    def test_ev_default_warms_webp_not_only_plain(self):
        with LsStub() as s:
            self.assertEqual(warm(s.host, self.out, '-V', 'guest-d', '/a/').returncode, 0)
            self.assertTrue(all(x['webp'] for x in s.log), s.log)  # mặc định gửi Accept có image/webp như Chrome
            self.assertTrue(all('image/webp' in x['accept'] for x in s.log))
            # Làm nóng riêng bản plain (lỗi của bản cũ) không làm nóng bản webp của khách thật.
            s.cache.clear()
            s.log.clear()
            p = os.path.join(self.t.name, 'plain.tsv')
            self.assertEqual(warm(s.host, p, '-V', 'guest-d', '-W', 'plain', '/a/').returncode, 0)
            self.assertEqual(s.log[0]['accept'], '*/*')
            q = os.path.join(self.t.name, 'real.tsv')
            self.assertEqual(warm(s.host, q, '-V', 'guest-d', '/a/').returncode, 0)
            self.assertEqual(rows(q)[0]['lscache'], 'miss')

    def test_both_mode_doubles_rows(self):
        with LsStub() as s:
            self.assertEqual(warm(s.host, self.out, '-V', 'guest-d,guest-m', '-W', 'both', '/a/').returncode, 0)
            a = rows(self.out)
            self.assertEqual(len(a), 4)
            self.assertEqual({x['accept'] for x in a}, {'webp', 'plain'})

    def test_retry_once_then_ok(self):
        with LsStub() as s:
            s.fail_once.add('/a/')
            r = warm(s.host, self.out, '-V', 'guest-d', '--retry-wait', '0', '/a/')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(rows(self.out)[0]['code'], '200')
            self.assertEqual(s.counts['/a/'], 2)

    def test_still_failing_exit_2_after_one_retry(self):
        with LsStub() as s:
            r = warm(s.host, self.out, '-V', 'guest-d', '--retry-wait', '0', '/dead/', '/a/')
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertEqual(s.counts['/dead/'], 2)  # đúng 1 lần thử lại
            a = {x['path']: x for x in rows(self.out)}
            self.assertEqual(a['/dead/']['code'], '500')
            self.assertEqual(a['/a/']['code'], '200')  # lượt lỗi không chặn URL sau
            self.assertIn('lượt lỗi', r.stderr)

    def test_connection_refused_exit_2(self):
        r = warm('http://127.0.0.1:1', self.out, '-V', 'guest-d', '--retry-wait', '0', '/a/')
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(rows(self.out)[0]['code'], '000')

    def test_cookie_failure_exit_1(self):
        r = warm('http://127.0.0.1:1', self.out, '-V', 'ret-d', '--retry-wait', '0', '/a/')
        self.assertEqual(r.returncode, 1)
        self.assertIn('_lscache_vary', r.stderr)

    def test_sleep_below_floor_rejected(self):
        with LsStub() as s:
            r = warm(s.host, self.out, '-s', '0.1', '/a/')
            self.assertEqual(r.returncode, 1)
            self.assertIn('0.5', r.stderr)
            self.assertEqual(s.log, [])

    def test_dry_run_sends_nothing(self):
        with LsStub() as s:
            r = subprocess.run(['bash', SCRIPT, '--host', s.host, '--dry-run'], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('DRY-RUN: 2 URL x 4 bản x 1 kiểu Accept = 8 lượt', r.stdout)
            self.assertEqual([x for x in s.log], [])
            self.assertFalse(os.path.exists(self.out))

    def test_file_list_other_host_skipped_and_dedup(self):
        with LsStub() as s:
            lst = os.path.join(self.t.name, 'ds.txt')
            with open(lst, 'w') as f:
                f.write('%s/a/\n/a/\nhttps://khac.example/x/\n  /b/  \n' % s.host)
            r = warm(s.host, self.out, '-V', 'guest-d', '-f', lst)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual([x['path'] for x in rows(self.out)], ['/a/', '/b/'])
            self.assertIn('khác host', r.stderr)

    def test_bad_args(self):
        for argv in (['--host'], ['--host', 'example.com'], ['--host', 'http://127.0.0.1:1', '-W', 'xyz'],
                     ['--host', 'http://127.0.0.1:1', '-V', 'guest-x'], ['--host', 'http://127.0.0.1:1', '--lạ']):
            r = subprocess.run(['bash', SCRIPT] + argv + ['/a/'], capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 1, argv)

    def test_missing_host(self):
        r = subprocess.run(['bash', SCRIPT, '/a/'], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn('--host', r.stderr)

    def test_help(self):
        r = subprocess.run(['bash', SCRIPT, '--help'], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertIn('--retry-wait', r.stdout)


if __name__ == '__main__':
    unittest.main()
