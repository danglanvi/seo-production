# Test offline cho psi_cls_dump.py. Ca hỏng thật: CLS 0,334 chỉ PSI thấy (19/10/2026), H1 cao 141 px, PSI gán nguyên nhân "Phông chữ web",
# lab trên Mac đo 0,009. Nguyên nhân phải hiện cùng boundingRect và ảnh để người đọc không tin nhãn font.
import glob
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import run, write_psi  # noqa: E402

SHIFTS = [
    {'score': 0.31, 'node': {'selector': 'header > div.hero > h1.entry-title', 'nodeLabel': 'SEO là gì', 'snippet': '<h1 class="entry-title">',
                             'boundingRect': {'top': 120, 'left': 16, 'width': 358, 'height': 141, 'bottom': 261, 'right': 374}},
     'subItems': {'items': [{'cause': 'Phông chữ web', 'extra': {'type': 'url', 'value': 'https://site-a.example/fonts/inter.woff2'}}]}},
    {'score': 0.024, 'node': {'selector': 'div.logo > img', 'boundingRect': {'top': 8, 'left': 16, 'width': 0, 'height': 0}},
     'subItems': {'items': [{'cause': 'Thành phần hình ảnh chưa xác định kích thước', 'extra': {'selector': 'div.logo > img', 'type': 'node'}}]}},
]


class ClsDump(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.f = write_psi(self.t.name, 'a_mobile_run1.json', score=62, cls=0.334, bench=650, shifts=SHIFTS)

    def tearDown(self):
        self.t.cleanup()

    def test_prints_culprit_rect_bench_and_font_warning(self):
        r = run('psi_cls_dump.py', self.f)
        self.assertEqual(r.returncode, 0, r.stderr)
        o = r.stdout
        self.assertIn('CLS lab: 0.334', o)
        self.assertIn('benchmarkIndex: 650', o)
        self.assertIn('máy chậm', o)
        self.assertIn('h1.entry-title', o)
        self.assertIn('h=141', o)
        self.assertIn('Phông chữ web', o)
        self.assertIn('phỏng đoán', o)
        self.assertIn('CLS field (CrUX p75', o)
        self.assertIn('filmstrip 3 khung', o)

    def test_no_out_writes_nothing(self):
        before = set(os.listdir(self.t.name))
        r = run('psi_cls_dump.py', self.f)
        self.assertIn('Chưa ghi PNG', r.stdout)
        self.assertEqual(set(os.listdir(self.t.name)), before)

    def test_out_writes_images(self):
        out = os.path.join(self.t.name, 'img')
        r = run('psi_cls_dump.py', self.f, '--out', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        names = sorted(os.listdir(out))
        self.assertTrue(any(n.startswith('final-screenshot') for n in names), names)
        self.assertEqual(len([n for n in names if n.startswith('filmstrip-') and n != 'filmstrip-all.png']), 3, names)
        try:
            import PIL  # noqa: F401
            self.assertIn('filmstrip-all.png', names)
            self.assertTrue(all(n.endswith('.png') for n in names))
            with open(os.path.join(out, 'final-screenshot.png'), 'rb') as f:
                self.assertEqual(f.read(8), b'\x89PNG\r\n\x1a\n')
        except ImportError:
            pass

    def test_corrupt_or_empty_json_exit_1(self):
        bad = os.path.join(self.t.name, 'bad.json')
        with open(bad, 'w') as f:
            f.write('{"lighthouseResult": ')
        self.assertEqual(run('psi_cls_dump.py', bad).returncode, 1)
        with open(bad, 'w') as f:
            json.dump({'error': {'code': 500}}, f)
        r = run('psi_cls_dump.py', bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn('lighthouseResult', r.stderr)
        self.assertEqual(run('psi_cls_dump.py', '/khong/co.json').returncode, 1)

    def test_no_shifts(self):
        f = write_psi(self.t.name, 'b_mobile_run1.json', cls=0.0)
        r = run('psi_cls_dump.py', f)
        self.assertEqual(r.returncode, 0)
        self.assertIn('không ghi dịch chuyển', r.stdout)

    def test_help(self):
        self.assertEqual(run('psi_cls_dump.py', '--help').returncode, 0)


if __name__ == '__main__':
    unittest.main()
