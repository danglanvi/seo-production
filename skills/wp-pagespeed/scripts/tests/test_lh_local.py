# Test offline cho lh_local.mjs. Không mở Chrome: chỉ kiểm tham số, cấu hình và mã thoát.
# Ca hỏng thật: PSI không reload của LiteSpeed Guest Mode (guest.vary.php) nên lab local phải chặn URL đó mới giống PSI (19/10/2026).
# Chạy thật Lighthouse trên server giả chỉ khi đặt WPS_RUN_LH=1 (cần cache npx có lighthouse và Chrome).
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import SiteStub, run  # noqa: E402


class LhLocal(unittest.TestCase):
    def test_help_and_usage(self):
        self.assertEqual(run('lh_local.mjs', '--help').returncode, 0)
        r = run('lh_local.mjs')
        self.assertEqual(r.returncode, 2)

    def test_bad_dev_exit_2(self):
        self.assertEqual(run('lh_local.mjs', '--url', 'https://a.test/', '--dev', 'tablet', '--dry-run').returncode, 2)

    def test_block_vary_in_flags(self):
        r = run('lh_local.mjs', '--url', 'https://a.test/x/', '--block-vary', '--block', '*chat.js*', '--dry-run')
        self.assertEqual(r.returncode, 0, r.stderr)
        j = json.loads(r.stdout[:r.stdout.rindex('}') + 1])
        self.assertEqual(j['flags']['blockedUrlPatterns'], ['*guest.vary.php*', '*chat.js*'])
        self.assertEqual(j['flags']['throttling']['cpuSlowdownMultiplier'], 4)
        self.assertEqual(j['host'], 'a.test')
        self.assertIn('DRY-RUN', r.stdout)

    def test_without_block_vary_nothing_blocked(self):
        r = run('lh_local.mjs', '--url', 'https://a.test/', '--dry-run')
        j = json.loads(r.stdout[:r.stdout.rindex('}') + 1])
        self.assertEqual(j['flags']['blockedUrlPatterns'], [])

    def test_missing_modules_exit_3(self):
        with tempfile.TemporaryDirectory() as home:
            r = run('lh_local.mjs', '--url', 'https://a.test/', '--lh-modules', os.path.join(home, 'none'), env={'HOME': home, 'LH_MODULES': ''})
            self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
            self.assertIn('lighthouse', r.stderr)

    @unittest.skipUnless(os.environ.get('WPS_RUN_LH') == '1', 'đặt WPS_RUN_LH=1 để chạy Lighthouse thật trên server giả')
    def test_live_on_local_stub(self):
        with SiteStub() as s, tempfile.TemporaryDirectory() as d:
            r = run('lh_local.mjs', '--url', s.url('/ok'), '--block-vary', '--expect', 'trang thử', '--out', d, timeout=240)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, 'lh_mobile_run1.json')))
            r2 = run('psi_cls_dump.py', os.path.join(d, 'lh_mobile_run1.json'))
            self.assertEqual(r2.returncode, 0, r2.stderr)
            bad = run('lh_local.mjs', '--url', s.url('/ok'), '--expect', 'khác hẳn', timeout=240)
            self.assertEqual(bad.returncode, 4)


if __name__ == '__main__':
    unittest.main()
