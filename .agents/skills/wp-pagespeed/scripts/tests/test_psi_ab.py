# Test offline cho psi_ab.py: noindex tự gắn, verify, ngưỡng đặt trước, --split-bench, dry-run mặc định, kiểm 404 sau quarantine.
# Ca hỏng thật: 22/10/2026 sáu bản HTML tĩnh A/B nằm công khai khoảng 30 phút với robots index và canonical trỏ URL gốc.
import json
import os
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import SiteStub, run, write_psi  # noqa: E402

PAGE = ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Trang chủ</title>'
        '<meta name="robots" content="index, follow, max-image-preview:large">'
        '<link rel="canonical" href="https://site-a.example/">'
        '<!-- Google Tag Manager --><script>gtm()</script><!-- End Google Tag Manager -->'
        '</head><body><h1>Chào</h1></body></html>')
SPEC = {'pages': {'home': 'https://site-a.example/'},
        'variants': {'v0': [], 'v4': [{'re': '<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->', 'sub': '<script>delayed()</script>'}]}}


class PsiAb(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name
        self.dir = os.path.join(self.d, 'ab')
        os.makedirs(os.path.join(self.dir, 'src'))
        with open(os.path.join(self.dir, 'src', 'home.html'), 'w', encoding='utf-8') as f:
            f.write(PAGE)
        self.spec = os.path.join(self.d, 'ab.json')
        with open(self.spec, 'w') as f:
            json.dump(SPEC, f)

    def tearDown(self):
        self.t.cleanup()

    def build(self, *extra):
        return run('psi_ab.py', 'build', '--spec', self.spec, '--dir', self.dir, '--from-src', *extra)

    def out(self, name):
        return open(os.path.join(self.dir, 'out', name), encoding='utf-8').read()

    def test_build_injects_noindex_and_self_canonical_on_every_variant(self):
        r = self.build('--site', 'https://site-a.example', '--tag', 't1')
        self.assertEqual(r.returncode, 0, r.stderr)
        for f in ('home-v0.html', 'home-v4.html'):
            h = self.out(f)
            self.assertEqual(h.count('name="robots"'), 1, f)
            self.assertIn('content="noindex,nofollow"', h)
            self.assertIn('href="https://site-a.example/wp-content/uploads/psi-ab-t1/%s"' % f, h)
            self.assertNotIn('index, follow', h)
            self.assertNotIn('href="https://site-a.example/"', h)
        self.assertIn('delayed()', self.out('home-v4.html'))
        self.assertEqual(run('psi_ab.py', 'verify', '--dir', self.dir).returncode, 0)

    def test_build_without_site_uses_relative_self_canonical(self):
        self.assertEqual(self.build().returncode, 0)
        self.assertIn('href="home-v0.html"', self.out('home-v0.html'))

    def test_verify_and_upload_refuse_indexable_static_page(self):
        self.build('--site', 'https://site-a.example', '--tag', 't1')
        bad = os.path.join(self.dir, 'out', 'home-v0.html')
        with open(bad, 'w', encoding='utf-8') as f:
            f.write(PAGE)  # đúng ca 22/10: robots index và canonical trỏ URL gốc
        r = run('psi_ab.py', 'verify', '--dir', self.dir)
        self.assertEqual(r.returncode, 3)
        self.assertIn('home-v0.html', r.stderr)
        r = run('psi_ab.py', 'upload', '--dir', self.dir, '--ssh', 'khong-co-host', '--root', '/www', '--tag', 't1', '--apply')
        self.assertEqual(r.returncode, 3, 'phải từ chối trước khi chạm ssh')
        self.assertIn('Từ chối upload', r.stderr)

    def test_upload_and_quarantine_default_to_dry_run(self):
        self.build('--site', 'https://site-a.example', '--tag', 't1')
        r = run('psi_ab.py', 'upload', '--dir', self.dir, '--ssh', 'khong-co-host', '--root', '/www', '--tag', 't1')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('DRY-RUN', r.stdout)
        r = run('psi_ab.py', 'quarantine', '--ssh', 'khong-co-host', '--root', '/www', '--tag', 't1')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('DRY-RUN', r.stdout)

    def test_decision_threshold_is_locked_after_first_build(self):
        r = self.build('--a', 'v0', '--b', 'v4', '--min-gain', '3', '--lcp-ms', '200', '--cls', '0.02')
        self.assertEqual(r.returncode, 0, r.stderr)
        spec = json.load(open(os.path.join(self.dir, 'spec.json')))
        self.assertEqual(spec['decision']['min_gain'], 3.0)
        self.assertIn('decided_at', spec['decision'])
        r = self.build('--a', 'v0', '--b', 'v4', '--min-gain', '1')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('đặt trước', r.stderr)
        self.assertEqual(self.build('--a', 'v0', '--b', 'v4', '--min-gain', '3').returncode, 0)

    def test_regex_count_mismatch_stops_build(self):
        spec = json.loads(json.dumps(SPEC))
        spec['variants']['v4'][0]['count'] = 2
        json.dump(spec, open(self.spec, 'w'))
        r = self.build()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('khớp 1 lần', r.stderr)

    def fill_psi(self, name, bench, score, lcp=1500, k=1):
        write_psi(os.path.join(self.d, 'psi'), 'home-%s-r%d_mobile_run1.json' % (name, k), bench=bench, score=score, lcp=lcp)

    def test_table_split_bench_and_preset_verdict(self):
        self.build('--a', 'v0', '--b', 'v4')
        # Ca 24/10: v0 có 3 lượt máy nhanh, v4 toàn máy chậm.
        for k, (b, s) in enumerate([(1000, 95), (950, 94), (900, 94), (600, 87), (650, 88)], 1):
            self.fill_psi('v0', b, s, k=k)
        for k, (b, s) in enumerate([(600, 87), (620, 88), (640, 88), (610, 87), (630, 88)], 1):
            self.fill_psi('v4', b, s, k=k)
        r = run('psi_ab.py', 'table', '--psi', os.path.join(self.d, 'psi'), '--dir', self.dir, '--split-bench')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Tách theo benchmarkIndex', r.stdout)
        lines = [l for l in r.stdout.splitlines() if l.startswith('mobile | home | v0 | ')]
        self.assertEqual(len(lines), 3, lines)  # 1 dòng bảng chính + nhóm chậm + nhóm nhanh
        self.assertTrue(any('| chậm | 2 |' in l for l in lines))
        self.assertTrue(any('| nhanh | 3 |' in l for l in lines))
        self.assertIn('Ngưỡng đặt trước', r.stdout)
        self.assertIn('lệch máy PSI', r.stdout)

    def test_table_without_decision_warns_not_fails(self):
        for k in (1, 2, 3):
            self.fill_psi('v0', 900, 90, k=k)
            self.fill_psi('v4', 900, 91, k=k)
        r = run('psi_ab.py', 'table', '--psi', os.path.join(self.d, 'psi'))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Chưa có ngưỡng đặt trước', r.stderr)

    def fake_ssh_env(self):
        b = os.path.join(self.d, 'bin')
        os.makedirs(b)
        p = os.path.join(b, 'ssh')
        with open(p, 'w') as f:
            f.write('#!/bin/sh\nexit 0\n')
        os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
        return {'PATH': b + os.pathsep + os.environ['PATH']}

    def test_quarantine_checks_404_after_move(self):
        self.build('--site', 'http://127.0.0.1:1', '--tag', 't1')
        env = self.fake_ssh_env()
        with SiteStub(status_map={}) as s:  # mọi đường dẫn trả 200: file vẫn còn mở
            r = run('psi_ab.py', 'quarantine', '--ssh', 'x', '--root', '/www', '--tag', 't1', '--apply', '--site', 'http://127.0.0.1:%d' % s.port, '--dir', self.dir, env=env)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn('vẫn còn mở', r.stderr)
        paths = ['/wp-content/uploads/psi-ab-t1/home-v0.html', '/wp-content/uploads/psi-ab-t1/home-v4.html']
        with SiteStub(status_map={p: 404 for p in paths}) as s:
            r = run('psi_ab.py', 'quarantine', '--ssh', 'x', '--root', '/www', '--tag', 't1', '--apply', '--site', 'http://127.0.0.1:%d' % s.port, '--dir', self.dir, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn('404 hoặc 410', r.stdout)

    def test_help(self):
        r = run('psi_ab.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--split-bench', r.stdout)


if __name__ == '__main__':
    unittest.main()
