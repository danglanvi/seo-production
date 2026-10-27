# Test offline cho psi_run.py bằng server PSI giả trên 127.0.0.1 (không gọi Google, không dùng key thật).
# Ca hỏng thật: tháng 10/2026 chờ PSI tuần tự 388-630 phút mỗi phiên, lệnh tiền cảnh quá lâu làm treo phiên (perf-1, hs-7).
import glob
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import PsiStub, run  # noqa: E402

KEY = 'KEY-GIA-0123456789'
ENV = {'PAGESPEED_API_KEY': KEY}
FAST = ['--sleep', '0', '--retry-wait', '0', '--no-warm', '--min-gap', '0']


class PsiRun(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name
        self.urls = os.path.join(self.d, 'urls.tsv')
        self.out = os.path.join(self.d, 'psi')

    def tearDown(self):
        self.t.cleanup()

    def write_urls(self, n):
        with open(self.urls, 'w') as f:
            for i in range(n):
                f.write('p%d\thttps://site-a.example/p%d/\n' % (i, i))

    def go(self, api, *extra):
        return run('psi_run.py', '--urls', self.urls, '--out', self.out, '--api-base', api, *extra, env=ENV)

    def test_jobs2_parallel_interleaved_and_resumable(self):
        self.write_urls(2)
        with PsiStub(delay=0.3) as s:
            r = self.go(s.api, '--runs', '2', '--jobs', '2', *FAST)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(len(glob.glob(os.path.join(self.out, '*.json'))), 8)
            self.assertEqual(s.max_inflight, 2, 'phải chạy đúng 2 lượt đồng thời')
            first_round = {(u, st) for u, st, _ in s.calls[:4]}
            self.assertEqual(len(first_round), 4, 'vòng 1 phải xong cả 4 tổ hợp url x thiết bị trước vòng 2')
            n = len(s.calls)
            r2 = self.go(s.api, '--runs', '2', '--jobs', '2', *FAST)
            self.assertEqual(r2.returncode, 0)
            self.assertEqual(len(s.calls), n, 'chạy lại không được gọi API vì file đã có')
        with open(os.path.join(self.out, 'PSI_STATE.txt')) as f:
            self.assertIn('DONE lỗi=0 exit=0', f.read())
        self.assertNotIn(KEY, r.stdout + r.stderr)

    def test_cached_result_is_retried_not_saved(self):
        # Ca hỏng thật 27/10/2026: PSI trả kết quả đã lưu cho lượt 2 và 3 (cùng fetchTime, mỗi lượt khoảng 1 giây),
        # nên "trung vị 3 lượt" thật ra là 1 lượt. Lượt trùng fetchTime phải bị bỏ và đo lại.
        self.write_urls(1)
        with PsiStub(cache_hits=1) as s:
            r = self.go(s.api, '--runs', '2', '--devices', 'mobile', '--jobs', '1', *FAST)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn('fetchTime', r.stdout)
            self.assertEqual(len(s.calls), 3, 'lượt 2 phải gọi lại sau khi gặp kết quả đã lưu')
        fts = set()
        for f in glob.glob(os.path.join(self.out, '*.json')):
            with open(f) as fh:
                fts.add(json.load(fh)['lighthouseResult']['fetchTime'])
        self.assertEqual(len(fts), 2, '2 file phải có 2 fetchTime khác nhau')

    def test_min_gap_spaces_same_url(self):
        self.write_urls(1)
        with PsiStub() as s:
            t0 = time.time()
            r = self.go(s.api, '--runs', '2', '--devices', 'mobile', '--jobs', '2', '--sleep', '0', '--retry-wait', '0', '--no-warm', '--min-gap', '1.5')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertGreaterEqual(time.time() - t0, 1.5, 'hai lượt cùng URL + thiết bị phải cách nhau --min-gap')
            self.assertEqual(s.max_inflight, 1, 'cùng URL + thiết bị không chạy đồng thời')

    def test_jobs1_is_sequential(self):
        self.write_urls(2)
        with PsiStub(delay=0.1) as s:
            r = self.go(s.api, '--runs', '1', '--jobs', '1', *FAST)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(s.max_inflight, 1)

    def test_jobs_above_2_needs_ack_and_max_4(self):
        self.write_urls(1)
        r = run('psi_run.py', '--urls', self.urls, '--out', self.out, '--jobs', '3', '--dry-run', env=ENV)
        self.assertEqual(r.returncode, 2)
        self.assertIn('--jobs-ok', r.stderr)
        r = run('psi_run.py', '--urls', self.urls, '--out', self.out, '--jobs', '3', '--jobs-ok', '--dry-run', env=ENV)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run('psi_run.py', '--urls', self.urls, '--out', self.out, '--jobs', '5', '--jobs-ok', '--dry-run', env=ENV)
        self.assertNotEqual(r.returncode, 0)

    def test_refuses_long_foreground(self):
        # 40 URL x 2 thiết bị x 3 lượt = 240 lượt, khoảng 60 phút ở --jobs 2: phải từ chối, không gọi API.
        self.write_urls(40)
        with PsiStub() as s:
            r = self.go(s.api, '--runs', '3', *FAST)
            self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
            self.assertIn('--detach', r.stderr)
            self.assertEqual(s.calls, [])
        self.assertFalse(os.path.exists(os.path.join(self.out, 'PSI_STATE.txt')))

    def test_dry_run_writes_nothing(self):
        self.write_urls(3)
        r = run('psi_run.py', '--urls', self.urls, '--out', self.out, '--dry-run', env={})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('DRY-RUN', r.stdout)
        self.assertFalse(os.path.exists(self.out))

    def test_detach_runs_in_background_and_writes_done_marker(self):
        self.write_urls(2)
        with PsiStub(delay=0.2) as s:
            t0 = time.time()
            r = self.go(s.api, '--runs', '1', '--detach', '--max-fg-min', '0', *FAST)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn('pid=', r.stdout)
            self.assertLess(time.time() - t0, 5, 'detach phải thoát ngay')
            state = os.path.join(self.out, 'PSI_STATE.txt')
            txt = ''
            for _ in range(100):
                txt = open(state).read() if os.path.exists(state) else ''
                if txt.startswith('DONE'):
                    break
                time.sleep(0.2)
            self.assertIn('DONE lỗi=0 exit=0', txt)
            self.assertEqual(len(s.calls), 4)
            self.assertTrue(os.path.exists(os.path.join(self.out, 'psi_run.log')))

    def test_failures_exit_1_and_state_records_them(self):
        self.write_urls(1)
        with PsiStub(mode='fail') as s:
            r = self.go(s.api, '--runs', '1', '--devices', 'mobile', *FAST)
            self.assertEqual(r.returncode, 1)
            self.assertIn('PSI_DONE lỗi=1', r.stdout)
            self.assertEqual(len(s.calls), 3, '3 lần thử')
        self.assertIn('DONE lỗi=1 exit=1', open(os.path.join(self.out, 'PSI_STATE.txt')).read())
        self.assertNotIn(KEY, r.stdout + r.stderr)

    def test_rejects_tracking_params(self):
        with open(self.urls, 'w') as f:
            f.write('p\thttps://site-a.example/p/?utm_source=x\n')
        with PsiStub() as s:
            r = self.go(s.api, *FAST)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('utm_', r.stderr + r.stdout)
            self.assertEqual(s.calls, [])

    def test_missing_key_exit_nonzero(self):
        # Chạy trong thư mục tạm và trỏ server giả: không thể chạm key thật của workspace.
        self.write_urls(1)
        with PsiStub() as s:
            r = run('psi_run.py', '--urls', self.urls, '--out', self.out, '--no-warm', '--api-base', s.api,
                    '--env', os.path.join(self.d, 'khong-co.env'), env={'PAGESPEED_API_KEY': '', 'HOME': self.d}, cwd=self.d)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('PAGESPEED_API_KEY', r.stderr + r.stdout)
            self.assertEqual(s.calls, [])

    def test_help(self):
        r = run('psi_run.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--jobs', r.stdout)
        self.assertIn('--detach', r.stdout)


if __name__ == '__main__':
    unittest.main()
