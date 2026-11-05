"""Test tim_anh_goc.py và dung_lai_anh.py bằng ảnh tổng hợp. Bỏ qua khi máy không có opencv-python."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover
    cv2 = None


def _anh_nguon(path, w=1600, h=1000, seed=7):
    rng = np.random.default_rng(seed)
    im = np.full((h, w, 3), 235, np.uint8)
    for _ in range(260):
        x, y = int(rng.integers(0, w - 60)), int(rng.integers(0, h - 60))
        c = tuple(int(v) for v in rng.integers(0, 255, 3))
        if rng.random() < 0.5:
            cv2.rectangle(im, (x, y), (x + int(rng.integers(10, 60)), y + int(rng.integers(10, 60))), c, -1)
        else:
            cv2.circle(im, (x, y), int(rng.integers(5, 30)), c, -1)
    cv2.imwrite(path, im)
    return im


@unittest.skipIf(cv2 is None, 'cần opencv-python')
class TestDungLai(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.src = os.path.join(self.d, 'nguon.png')
        im = _anh_nguon(self.src)
        crop = im[200:840, 300:1324]
        small = cv2.resize(crop, (400, 250), interpolation=cv2.INTER_AREA).astype(np.float32)
        tint = np.linspace(0, 1, 400)[None, :, None] * np.array([60, 0, 40])[None, None, :]
        small = np.clip(small * 0.85 + tint, 0, 255).astype(np.uint8)
        a = np.full((250, 400), 255, np.uint8)
        cv2.circle(a, (0, 0), 30, 0, -1)
        self.small = os.path.join(self.d, 'nho.png')
        cv2.imwrite(self.small, np.dstack([small, a]))
        _anh_nguon(os.path.join(self.d, 'khac.png'), seed=99)

    def run_py(self, script, *args):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True)
        return r.returncode, [json.loads(x) for x in r.stdout.splitlines() if x.strip()]

    def test_tim_dung_ung_vien(self):
        code, rows = self.run_py('tim_anh_goc.py', '--dich', self.small, '--ung-vien', self.d)
        self.assertEqual(code, 0)
        self.assertTrue(rows[0]['ung_vien'].endswith('nguon.png'))
        self.assertAlmostEqual(rows[0]['ti_le'], 2.56, delta=0.05)

    def test_dung_lai_giu_mau_va_alpha(self):
        out = os.path.join(self.d, 'moi.png')
        code, rows = self.run_py('dung_lai_anh.py', '--nho', self.small, '--nguon', self.src, '--out', out, '--diff-png', os.path.join(self.d, 'diff.png'))
        self.assertEqual(code, 0)
        info = rows[0]
        self.assertGreater(info['size'][0], 900)
        self.assertLess(info['sai_khac_tb'], 4.0)
        o = cv2.imread(out, cv2.IMREAD_UNCHANGED)
        self.assertEqual(o.shape[2], 4)
        self.assertLess(int(o[2, 2, 3]), 30)

    def test_khong_khop_tra_3(self):
        code, rows = self.run_py('dung_lai_anh.py', '--nho', self.small, '--nguon', os.path.join(self.d, 'khac.png'), '--out', os.path.join(self.d, 'x.png'))
        self.assertEqual(code, 3)


if __name__ == '__main__':
    unittest.main()
