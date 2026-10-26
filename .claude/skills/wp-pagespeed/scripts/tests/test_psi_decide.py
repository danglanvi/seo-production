# Test offline cho psi_decide.py và psi_lib.decide. Ca hỏng thật: site agency mẫu 24/10/2026, bản A trung vị 94,5 và bản C 88,5
# chỉ vì ba lượt A rơi vào máy PSI nhanh (benchmarkIndex 890-1088). So cùng nhóm máy thì hai bản như nhau.
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import run, write_psi  # noqa: E402
import psi_lib as L  # noqa: E402


def fill(d, var, rows, page='home', dev='mobile'):
    """rows: danh sách dict kwargs cho psi_json, vòng xen kẽ k = 1, 2, ..."""
    for k, kw in enumerate(rows, 1):
        write_psi(d, '%s-%s-r%d_%s_run1.json' % (page, var, k, dev), dev=dev, **kw)


def S(scores, bench=1000.0, lcp=1500, cls=0.0):
    return [dict(score=s, bench=bench, lcp=lcp, cls=cls) for s in scores]


class DecideCli(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name

    def tearDown(self):
        self.t.cleanup()

    def dec(self, *extra):
        return run('psi_decide.py', self.d, '--a', 'v0', '--b', 'v4', *extra)

    def test_better(self):
        fill(self.d, 'v0', S([80, 81, 79, 80, 82]))
        fill(self.d, 'v4', S([86, 87, 85, 86, 88]))
        r = self.dec()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('PSI_DECIDE label=better', r.stdout)

    def test_same_after_max_runs(self):
        fill(self.d, 'v0', S([88, 89, 87, 88, 90]))
        fill(self.d, 'v4', S([89, 88, 88, 89, 89]))
        r = self.dec()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('PSI_DECIDE label=same', r.stdout)

    def test_same_diff_but_few_runs_needs_more(self):
        fill(self.d, 'v0', S([88, 89, 87]))
        fill(self.d, 'v4', S([89, 88, 88]))
        r = self.dec()
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn('label=more', r.stdout)

    def test_too_few_runs(self):
        fill(self.d, 'v0', S([80, 81]))
        fill(self.d, 'v4', S([90, 91]))
        r = self.dec()
        self.assertEqual(r.returncode, 3)
        self.assertIn('cần ít nhất 3 lượt', r.stdout)

    def test_machine_noise_is_not_called_worse(self):
        # Ca hỏng thật 24/10: A có 3 lượt máy nhanh (95, 94, 94) và 2 lượt máy chậm (87, 88). B có 5 lượt máy chậm quanh 88.
        # Trung vị gộp A=94, B=88 sẽ báo "xấu hơn" sai.
        a = S([95, 94, 94], bench=1000) + S([87, 88], bench=600)
        fill(self.d, 'v0', a)
        fill(self.d, 'v4', S([87, 88, 88, 87, 88], bench=600))
        naive = L.decide([dict(score=x, bench=1000, lcp=1500, cls=0, k=i) for i, x in enumerate([95, 94, 94, 87, 88])],
                         [dict(score=x, bench=1000, lcp=1500, cls=0, k=i) for i, x in enumerate([87, 88, 88, 87, 88])])
        self.assertEqual(naive['label'], 'worse', 'điều kiện của ca: so gộp mà không xét máy PSI sẽ báo xấu hơn')
        r = self.dec()
        self.assertNotIn('label=worse', r.stdout)
        self.assertIn('lệch máy PSI', r.stdout)

    def test_machine_gap_without_common_group_is_more(self):
        fill(self.d, 'v0', S([95, 94, 94], bench=1000))
        fill(self.d, 'v4', S([87, 88, 88], bench=600))
        r = self.dec()
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn('lệch máy PSI', r.stdout)

    def test_lcp_regression_is_worse_even_if_cls_improves(self):
        # Site mẫu 2: preload font đổi CLS 0,08 thành 0 nhưng LCP mô phỏng 1,5 thành 2,3 s.
        fill(self.d, 'v0', S([85, 86, 85, 85, 86], lcp=1500, cls=0.08))
        fill(self.d, 'v4', S([86, 87, 86, 86, 87], lcp=2300, cls=0.0))
        r = self.dec()
        self.assertIn('label=worse', r.stdout)
        self.assertIn('LCP', r.stdout)

    def test_cls_regression_is_worse_even_if_score_up(self):
        fill(self.d, 'v0', S([80, 81, 80], cls=0.0))
        fill(self.d, 'v4', S([86, 87, 86], cls=0.1))
        self.assertIn('label=worse', self.dec().stdout)

    def test_median_up_but_pairs_disagree_is_not_better(self):
        fill(self.d, 'v0', S([84, 70, 71]))
        fill(self.d, 'v4', S([80, 81, 60]))
        r = self.dec()
        self.assertNotIn('label=better', r.stdout)
        self.assertIn('cặp lượt', r.stdout)

    def test_corrupt_json_exit_1(self):
        fill(self.d, 'v0', S([80, 81, 82]))
        fill(self.d, 'v4', S([80, 81, 82]))
        open(os.path.join(self.d, 'home-v4-r9_mobile_run1.json'), 'w').write('{"kind": "x"')
        r = self.dec()
        self.assertEqual(r.returncode, 1)
        self.assertIn('Lỗi', r.stderr)

    def test_missing_args_and_dir(self):
        self.assertEqual(run('psi_decide.py', self.d).returncode, 2)
        self.assertEqual(run('psi_decide.py', '/khong/co', '--a', 'v0', '--b', 'v4').returncode, 1)

    def test_max_runs_caps_branch(self):
        fill(self.d, 'v0', S([80] * 5 + [60] * 5))
        fill(self.d, 'v4', S([80] * 5 + [95] * 5))
        r = self.dec('--max-runs', '5', '--json')
        j = json.loads(r.stdout)
        self.assertEqual(j['pages']['home']['nA'], 5)
        self.assertEqual(j['overall'], 'same')

    def test_dirs_mode(self):
        a, b = os.path.join(self.d, 'A'), os.path.join(self.d, 'B')
        for i in (1, 2, 3):
            write_psi(a, 'home_mobile_run%d.json' % i, score=70 + i)
            write_psi(b, 'home_mobile_run%d.json' % i, score=80 + i)
        r = run('psi_decide.py', '--a-dir', a, '--b-dir', b)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('label=better', r.stdout)

    def test_help(self):
        r = run('psi_decide.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--max-runs', r.stdout)


class LibNoindex(unittest.TestCase):
    BAD = ('<!doctype html><html><head><meta charset="utf-8"><title>t</title>'
           '<meta name="robots" content="index, follow"><META NAME=\'robots\' content=\'max-image-preview:large\'>'
           '<link rel="canonical" href="https://site-a.example/trang/"></head><body></body></html>')

    def test_check_flags_bad(self):
        errs = L.check_noindex(self.BAD, 'home-v0.html')
        self.assertTrue(any('meta robots' in e for e in errs))
        self.assertTrue(any('canonical trỏ' in e for e in errs))

    def test_inject_makes_safe(self):
        out = L.inject_noindex(self.BAD, 'https://site-a.example/wp-content/uploads/psi-ab-t/home-v0.html')
        self.assertEqual(L.check_noindex(out, 'https://site-a.example/wp-content/uploads/psi-ab-t/home-v0.html'), [])
        self.assertNotIn('index, follow', out)
        self.assertNotIn('https://site-a.example/trang/', out)
        self.assertEqual(out.count('canonical'), 1)

    def test_no_head_raises(self):
        with self.assertRaises(ValueError):
            L.inject_noindex('<html><body></body></html>', 'x.html')


if __name__ == '__main__':
    unittest.main()
