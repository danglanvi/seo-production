# Test offline cho guard của perf_probe.mjs, shot.mjs, lh_local.mjs (_guard.mjs). Chrome chạy trên server giả 127.0.0.1.
# Ca hỏng thật: 16-17/10/2026 agent đo nhầm đích hai lần (trang 404, tunnel staging đã tắt), số đo vô nghĩa và mất khoảng 4 phút mỗi lần.
import json
import os
import socket
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import SCRIPTS, SiteStub, run  # noqa: E402

CHROME = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HAS_CHROME = os.path.exists(CHROME)


def verdict(**kw):
    code = "import {verdict} from './_guard.mjs'; console.log(JSON.stringify(verdict(%s)))" % json.dumps(kw)
    import subprocess
    p = subprocess.run(['node', '--input-type=module', '-e', code], cwd=SCRIPTS, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


class GuardUnit(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(verdict(requestedHost='a.test', finalHost='a.test', status=200, title='Trang chủ | A', expect='trang chủ', lcp=900), [])

    def test_404_page(self):
        e = verdict(requestedHost='a.test', finalHost='a.test', status=404, title='Không tìm thấy', lcp=900)
        self.assertTrue(any('404' in x for x in e))

    def test_no_status_is_error(self):
        self.assertTrue(verdict(requestedHost='a.test', finalHost='a.test', status=None, title='', lcp=900))

    def test_title_mismatch(self):
        e = verdict(requestedHost='a.test', finalHost='a.test', status=200, title='Đăng nhập', expect='Trang chủ', lcp=900)
        self.assertTrue(any('title' in x for x in e))

    def test_lcp_below_100(self):
        e = verdict(requestedHost='a.test', finalHost='a.test', status=200, title='x', lcp=40)
        self.assertTrue(any('LCP' in x for x in e))
        self.assertEqual(verdict(requestedHost='a.test', finalHost='a.test', status=200, title='x', lcp=40, minLcp=0), [])

    def test_redirect_to_other_host(self):
        e = verdict(requestedHost='stg.a.test', finalHost='a.test', status=200, title='x', lcp=900)
        self.assertTrue(any('host thật' in x for x in e))
        self.assertEqual(verdict(requestedHost='stg.a.test', finalHost='a.test', status=200, title='x', lcp=900, allowRedirectHost=True), [])


class TunnelGuard(unittest.TestCase):
    def test_probe_exits_4_when_tunnel_closed(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        r = run('perf_probe.mjs', '--url', 'https://stg.a.test:%d/' % port, '--resolve', 'stg.a.test=127.0.0.1', '--runs', '1')
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertIn('tunnel', r.stderr)

    def test_shot_and_lh_exit_4_when_tunnel_closed(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        with tempfile.TemporaryDirectory() as d:
            u = os.path.join(d, 'u.tsv')
            with open(u, 'w') as f:
                f.write('x\thttps://stg.a.test:%d/\n' % port)
            r = run('shot.mjs', '--urls', u, '--out', os.path.join(d, 'o'), '--label', 't', '--resolve', 'stg.a.test=127.0.0.1')
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        r = run('lh_local.mjs', '--url', 'https://stg.a.test:%d/' % port, '--resolve', 'stg.a.test=127.0.0.1')
        self.assertIn(r.returncode, (3, 4))  # 3 nếu máy không có module Lighthouse, 4 khi guard chạy trước

    def test_open_port_passes_tunnel_check(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        code = "import {checkTunnel} from './_guard.mjs'; await checkTunnel('h.test=127.0.0.1','https://h.test:%d/'); console.log('open')" % s.getsockname()[1]
        import subprocess
        p = subprocess.run(['node', '--input-type=module', '-e', code], cwd=SCRIPTS, capture_output=True, text=True)
        s.close()
        self.assertEqual(p.stdout.strip(), 'open', p.stderr)


@unittest.skipUnless(HAS_CHROME, 'cần Chrome (đặt CHROME_BIN)')
class ProbeGuardWithChrome(unittest.TestCase):
    def probe(self, url, *extra):
        return run('perf_probe.mjs', '--url', url, '--runs', '1', '--dev', 'mobile', *extra, timeout=90)

    def test_404_page_exit_4(self):
        with SiteStub(status_map={'/gone': 404}) as s:
            r = self.probe(s.url('/gone'))
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
            self.assertIn('status=404', r.stdout)
            self.assertNotIn('"run":"median"', r.stdout)

    def test_title_mismatch_exit_4(self):
        with SiteStub() as s:
            r = self.probe(s.url('/ok'), '--expect', 'Trang khác')
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
            self.assertIn('title', r.stderr)

    def test_good_page_prints_guard_line_first_and_exit_0(self):
        with SiteStub() as s:
            with tempfile.TemporaryDirectory() as d:
                done = os.path.join(d, 'done.txt')
                r = self.probe(s.url('/ok'), '--expect', 'trang thử', '--done', done)
                marker = open(done).read().strip() if os.path.exists(done) else ''
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(r.stdout.startswith('GUARD host=127.0.0.1:'), r.stdout)
            self.assertIn('status=200', r.stdout.splitlines()[0])
            self.assertIn('"run":"median"', r.stdout)
            self.assertEqual(marker, 'PROBE_DONE exit=0')

    def test_no_guard_lets_404_through(self):
        with SiteStub(status_map={'/gone': 404}) as s:
            r = self.probe(s.url('/gone'), '--no-guard')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_shot_first_url_404_stops_before_writing(self):
        with SiteStub(status_map={'/gone': 404}) as s, tempfile.TemporaryDirectory() as d:
            u = os.path.join(d, 'u.tsv')
            with open(u, 'w') as f:
                f.write('gone\t%s\n' % s.url('/gone'))
            r = run('shot.mjs', '--urls', u, '--out', os.path.join(d, 'o'), '--label', 't', timeout=120)
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
            self.assertFalse(os.path.exists(os.path.join(d, 'o', 'results_t.json')))


if __name__ == '__main__':
    unittest.main()
