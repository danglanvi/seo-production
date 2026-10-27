"""Test offline cho tim_file_lo.sh. Chạy: python3 -B scripts/tests/test_tim_file_lo.py
SSH thay bằng 'bash -c' chạy cục bộ. HTTP chạy trên server giả 127.0.0.1 phục vụ thư mục web root giả.
Ca hỏng thật: 27/10/2026 site WooCommerce trên shared hosting có 5 dump SQL trong wp-content/backups/ và wp-content/deploy-staging/
trả 200; exposure_check.sh không thấy vì chỉ thử path cố định.
"""
import os
import subprocess
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), 'tim_file_lo.sh')


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.log'):  # site đã có rule chặn log
            self.send_response(403)
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *a):
        pass


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(data)


class TimFileLo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, 'web root')
        write(self.root, 'wp-content/backups/pre-deploy-20260525.sql', 'INSERT INTO wp_users VALUES (1);')
        write(self.root, 'wp-content/deploy-staging/db export.sql', 'x' * 10)
        write(self.root, 'wp-content/debug.log', 'PHP Notice')
        write(self.root, 'wp-content/cache/page.gz', 'cache')
        write(self.root, 'wp-content/backups/empty.sql', '')
        write(self.root, 'index.php', '<?php')
        write(self.root, 'wp-content/plugins/wordfence/lib/noc1.key', 'PUBLIC KEY')  # file đi kèm plugin, vô hại
        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=self.root))
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.base = f'http://127.0.0.1:{self.srv.server_address[1]}'

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def run_script(self, *extra):
        out = os.path.join(self.tmp.name, 'ket-qua.tsv')
        p = subprocess.run(['bash', SCRIPT, '--ssh', 'bash -c', '--root', self.root, '--base', self.base,
                            '--sleep', '0', '--out', out, *extra], capture_output=True, text=True, timeout=60)
        if not os.path.exists(out):
            return p, ''
        with open(out) as f:
            return p, f.read()

    def test_bat_dump_tai_duoc(self):
        p, tsv = self.run_script()
        self.assertEqual(p.returncode, 1, p.stderr)
        rows = {r.split('\t')[4]: r.split('\t')[0] for r in tsv.strip().splitlines()[1:]}
        muc = {r.split('\t')[4]: r.split('\t')[1] for r in tsv.strip().splitlines()[1:]}
        self.assertEqual(rows['wp-content/backups/pre-deploy-20260525.sql'], '200')
        self.assertEqual(rows['wp-content/deploy-staging/db export.sql'], '200')  # tên có dấu cách vẫn mã hoá đúng
        self.assertEqual(rows['wp-content/debug.log'], '403')
        self.assertNotIn('wp-content/cache/page.gz', rows)  # thư mục cache bị bỏ
        self.assertNotIn('wp-content/backups/empty.sql', rows)  # file 0 byte bị bỏ
        self.assertNotIn('index.php', rows)
        self.assertEqual(muc['wp-content/backups/pre-deploy-20260525.sql'], 'cao')
        self.assertEqual(rows['wp-content/plugins/wordfence/lib/noc1.key'], '200')
        self.assertEqual(muc['wp-content/plugins/wordfence/lib/noc1.key'], 'goi')  # không tính là lộ
        self.assertIn('2 file mức cao hoặc trung tải được', p.stderr)

    def test_sach_thi_ma_0(self):
        for rel in ('wp-content/backups/pre-deploy-20260525.sql', 'wp-content/deploy-staging/db export.sql'):
            os.remove(os.path.join(self.root, rel))
        p, tsv = self.run_script()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('0 file mức cao hoặc trung tải được', p.stderr)  # còn file đi kèm plugin trả 200 vẫn mã 0

    def test_khong_noi_dung_file_trong_ket_qua(self):
        p, tsv = self.run_script()
        self.assertNotIn('INSERT INTO', p.stdout + tsv)

    def test_root_sai_thi_ma_2(self):
        p = subprocess.run(['bash', SCRIPT, '--ssh', 'bash -c', '--root', os.path.join(self.tmp.name, 'khong-co'),
                            '--base', self.base, '--sleep', '0'], capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 2)


class DumpTrongPlugin(TimFileLo):
    test_bat_dump_tai_duoc = test_sach_thi_ma_0 = test_khong_noi_dung_file_trong_ket_qua = test_root_sai_thi_ma_2 = None

    def test_dump_trong_thu_muc_plugin_van_la_cao(self):
        write(self.root, 'wp-content/plugins/x/db.sql', 'dump')
        p, tsv = self.run_script()
        muc = {r.split('\t')[4]: r.split('\t')[1] for r in tsv.strip().splitlines()[1:]}
        self.assertEqual(muc['wp-content/plugins/x/db.sql'], 'cao')


if __name__ == '__main__':
    unittest.main()
