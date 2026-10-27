"""Test offline cho semantic_audit.py. Chạy: python3 -B scripts/tests/test_semantic_audit.py
HTML đã lưu sẵn trong thư mục html nên script không gọi mạng. Mẫu lấy từ lỗi thật của site agency mẫu 27/10/2026:
trang thiếu <main>, card không bọc <article>, ngày đăng không có <time>, chữ đậm làm heading, nhảy cấp H1 → H3.
"""
import csv
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), 'semantic_audit.py')

LOI = """<html><body><header><nav><a href="/">Trang chủ</a></nav></header>
<div class="content"><h1>Đội ngũ</h1><h3>Nhảy cấp</h3>
<p><strong>Bước 1: Nghiên cứu</strong></p><p>Nội dung bước một.</p>
<p><strong>Ví dụ dài hơn nhưng vẫn là đoạn thường</strong> có chữ thường đi kèm.</p>
<img src="a.jpg"></div><footer>f</footer>
<script>var x = "<p><strong>Trong script</strong></p>";</script></body></html>"""

DAT = """<html><body><header><nav aria-label="Menu chính"><a href="/">Trang chủ</a></nav></header>
<main><article><h1>Bài viết</h1><time datetime="2026-10-27">27/10/2026</time>
<h2>Mục</h2><h3>Mục con</h3><figure><img src="a.jpg" width="10" height="10" alt="a"><figcaption>c</figcaption></figure>
</article><aside>bên</aside></main><footer>f</footer></body></html>"""


class SemanticAudit(unittest.TestCase):
    def run_audit(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        html = os.path.join(tmp.name, 'html')
        os.makedirs(html)
        with open(os.path.join(html, 'doi_ngu.html'), 'w') as f:
            f.write(LOI)
        with open(os.path.join(html, 'bai.html'), 'w') as f:
            f.write(DAT)
        tsv = os.path.join(tmp.name, 'chon.tsv')
        with open(tsv, 'w') as f:
            f.write('path\tnhom\n/doi-ngu/\ttrang\n/bai/\tbai-viet\n')
        out = os.path.join(tmp.name, 'out.csv')
        p = subprocess.run(['python3', '-I', SCRIPT, '--base', 'http://127.0.0.1:9', tsv, html, out], capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(out) as f:
            return {r['path']: r for r in csv.DictReader(f)}

    def test_trang_loi(self):
        r = self.run_audit()['/doi-ngu/']
        self.assertEqual(r['main'], '0')
        self.assertEqual(r['heading_gia'], '1')  # chỉ đoạn chỉ chứa chữ đậm, bỏ đoạn trong script
        self.assertEqual(r['nav_khong_nhan'], '1')
        self.assertEqual(r['time'], '0')
        self.assertEqual(r['img_thieu_kt'], '1')
        self.assertEqual(r['img_thieu_alt'], '1')

    def test_trang_dat(self):
        r = self.run_audit()['/bai/']
        self.assertEqual((r['main'], r['article'], r['aside'], r['time']), ('1', '1', '1', '1'))
        self.assertEqual((r['h1_main'], r['nhay_cap_main'], r['heading_gia'], r['nav_khong_nhan']), ('1', '0', '0', '0'))

    def test_thieu_base_thi_dung(self):
        p = subprocess.run(['python3', '-I', SCRIPT, 'a', 'b', 'c'], capture_output=True, text=True, timeout=30)
        self.assertNotEqual(p.returncode, 0)


if __name__ == '__main__':
    unittest.main()
