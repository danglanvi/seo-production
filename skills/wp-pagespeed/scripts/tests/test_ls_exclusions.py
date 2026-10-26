# Test offline cho ls_exclusions_check.py.
# Ca lỗi dựng từ luật perf-5 (đợt tốc độ 19/10/2026, site agency mẫu bật LiteSpeed Guest Mode): loader GTM hoãn chỉ nằm trong optm-js_defer_exc
# (danh sách Delay JS thường). Guest Mode đọc danh sách riêng optm-gm_js_exc, nên loader vẫn bị trễ ở lượt xem đầu mà PSI đo.
# Fixture dựng lại cấu hình sai đó từ luật, không phải bản xuất cấu hình thật của site.
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import run  # noqa: E402


class LsExclusions(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name

    def tearDown(self):
        self.t.cleanup()

    def conf(self, data, name='conf.json', raw=None):
        p = os.path.join(self.d, name)
        with open(p, 'w') as f:
            f.write(raw if raw is not None else json.dumps(data))
        return p

    def check(self, p, *scripts):
        argv = ['--conf', p]
        for s in scripts:
            argv += ['--script', s]
        return run('ls_exclusions_check.py', *argv)

    def test_real_failure_guest_mode_wrong_list(self):
        p = self.conf({'guest': 1, 'optm-js_defer': 2, 'optm-js_defer_exc': ['gtm-delay-loader'], 'optm-gm_js_exc': []})
        r = self.check(p, 'gtm-delay-loader')
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('optm-gm_js_exc', r.stdout)
        self.assertIn('không áp cho Guest Mode', r.stdout)
        self.assertTrue(r.stdout.strip().endswith('LS_EXCL fail'))

    def test_guest_mode_right_list(self):
        p = self.conf({'guest': 1, 'optm-js_defer': 2, 'optm-js_defer_exc': ['gtm-delay-loader'], 'optm-gm_js_exc': ['gtm-delay-loader']})
        r = self.check(p, 'gtm-delay-loader')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(r.stdout.strip().endswith('LS_EXCL ok'))

    def test_guest_off_delay_on_uses_defer_list(self):
        p = self.conf({'guest': 0, 'optm-js_defer': 2, 'optm-js_defer_exc': ['gtm-delay-loader'], 'optm-gm_js_exc': []})
        self.assertEqual(self.check(p, 'gtm-delay-loader').returncode, 0)
        p2 = self.conf({'guest': 0, 'optm-js_defer': 2, 'optm-js_defer_exc': [], 'optm-gm_js_exc': ['gtm-delay-loader']}, 'c2.json')
        r = self.check(p2, 'gtm-delay-loader')
        self.assertEqual(r.returncode, 1)
        self.assertIn('optm-js_defer_exc', r.stdout)

    def test_both_off_nothing_to_do(self):
        p = self.conf({'guest': 0, 'optm-js_defer': 0})
        r = self.check(p, 'gtm-delay-loader')
        self.assertEqual(r.returncode, 0)
        self.assertIn('không cần loại trừ', r.stdout)

    def test_substring_semantics(self):
        # Mục loại trừ là chuỗi con của chuỗi nhận dạng script. "gtm" khớp "googletagmanager.com/gtm.js", nhưng chuỗi dài hơn thì không.
        p = self.conf({'guest': 1, 'optm-js_defer': 0, 'optm-gm_js_exc': ['googletagmanager.com']})
        self.assertEqual(self.check(p, 'https://www.googletagmanager.com/gtm.js?id=GTM-TEST').returncode, 0)
        p2 = self.conf({'guest': 1, 'optm-js_defer': 0, 'optm-gm_js_exc': ['gtm-delay-loader-v2']}, 'c2.json')
        self.assertEqual(self.check(p2, 'gtm-delay-loader').returncode, 1)

    def test_multiple_scripts_one_missing(self):
        p = self.conf({'guest': 1, 'optm-js_defer': 0, 'optm-gm_js_exc': 'gtm-delay-loader\nfbevents'})
        self.assertEqual(self.check(p, 'gtm-delay-loader', 'fbevents').returncode, 0)
        r = self.check(p, 'gtm-delay-loader', 'tawk.to')
        self.assertEqual(r.returncode, 1)
        self.assertIn('LỖI  tawk.to', r.stdout)

    def test_tsv_format_with_prefix(self):
        raw = 'litespeed.conf.guest\t1\nlitespeed.conf.optm-js_defer\t2\nlitespeed.conf.optm-js_defer_exc\t["gtm-delay-loader"]\nlitespeed.conf.optm-gm_js_exc\t["gtm-delay-loader"]\n'
        p = self.conf(None, 'conf.tsv', raw=raw)
        self.assertEqual(self.check(p, 'gtm-delay-loader').returncode, 0)

    def test_missing_keys_is_input_error(self):
        p = self.conf({'optm-gm_js_exc': ['x']})
        r = self.check(p, 'x')
        self.assertEqual(r.returncode, 2)
        self.assertIn('thiếu key', r.stderr)

    def test_broken_json_and_missing_file(self):
        self.assertEqual(self.check(self.conf(None, 'bad.json', raw='{"guest": 1,'), 'x').returncode, 2)
        self.assertEqual(self.check(os.path.join(self.d, 'khong-co.json'), 'x').returncode, 2)

    def test_help(self):
        r = run('ls_exclusions_check.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--conf', r.stdout)


if __name__ == '__main__':
    unittest.main()
