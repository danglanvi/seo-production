#!/usr/bin/env python3
"""Test offline cho tong_hop_php_tai.py và rtreport_phan_tich.py. Chạy: python3 -B scripts/tests/test_host_scripts.py"""
import os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)


def run(script, text, *args):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
    try:
        return subprocess.run([sys.executable, '-I', os.path.join(S, script), f.name, *args], capture_output=True, text=True)
    finally:
        os.unlink(f.name)


PHP = """#RUN|2026-10-27 20:44:21 +0700|2026-10-27 18:00|2026-10-27 20:00
G|site.vn|D|2026-10-27|scanner-ip|trang-404|100|40|60.0|0|40|100|0|0|0
G|site.vn|D|2026-10-27|nguoi-dung|trang|50|10|20.0|40|10|0|0|0|0
G|site.vn|D|2026-10-27|noi-bo|trang|500|300|200.0|0|300|0|0|0|0
G|khach.vn|noD|2026-10-27|nguoi-dung|trang|80|30|0.0|0|0|0|0|0|0
C|site.vn|2026-10-27 18:01|12.00|11.00|1.000|0.900
C|site.vn|2026-10-27 18:02|3.00|2.00|1.000|0.900
I|site.vn|10.0.0.9|scanner-ip|100|40|60.0|100
P|site.vn|D|scanner-ip|trang-404|/graphql|40|60.0
"""

RT = """1792806600
/tmp/lshttpd/.rtreport:BLOCKED_IP:
EXTAPP [LSAPI] [site.vn] [site.vn.10000]: CMAXCONN: 10, EMAXCONN: 10, POOL_SIZE: 3, INUSE_CONN: 10, IDLE_CONN: 0, WAITQUE_DEPTH: 4, REQ_PER_SEC: 9, TOT_REQS: 10
EXTAPP [LSAPI] [site.vn] [site.vn.10000]: CMAXCONN: 10, EMAXCONN: 10, POOL_SIZE: 3, INUSE_CONN: 2, IDLE_CONN: 1, WAITQUE_DEPTH: 1, REQ_PER_SEC: 1, TOT_REQS: 10
1792806610
EXTAPP [LSAPI] [site.vn] [site.vn.10000]: CMAXCONN: 10, EMAXCONN: 10, POOL_SIZE: 3, INUSE_CONN: 1, IDLE_CONN: 2, WAITQUE_DEPTH: 0, REQ_PER_SEC: 1, TOT_REQS: 11
# mat-ket-noi 1792806615
1792806700
BLOCKED_IP: 203.0.113.5
EXTAPP [LSAPI] [khach.vn] [khach.vn.10000]: CMAXCONN: 20, EMAXCONN: 20, POOL_SIZE: 1, INUSE_CONN: 0, IDLE_CONN: 1, WAITQUE_DEPTH: 0, REQ_PER_SEC: 0, TOT_REQS: 5
"""


class TongHop(unittest.TestCase):
    def test_quy_ngay_va_bo_noi_bo(self):
        r = run('tong_hop_php_tai.py', PHP)
        self.assertEqual(r.returncode, 0, r.stderr)
        # Cửa sổ 2 giờ → ×12. Bên ngoài site.vn: PHP 50 → 600/ngày, PHP-giây 80 → 960/ngày.
        self.assertIn('bên ngoài theo actor (PHP 600/ngày, PHP-giây 960/ngày)', r.stdout)
        self.assertIn('| scanner-ip | 1.200 | 480 | 720 | 75% |', r.stdout)
        self.assertNotIn('| noi-bo |', r.stdout)

    def test_canh_bao_thieu_D(self):
        r = run('tong_hop_php_tai.py', PHP)
        self.assertIn('| khach.vn | 960 | 360 | 0 | 100% dòng thiếu %D: số PHP là trần trên |', r.stdout)

    def test_phut_cham_tran(self):
        r = run('tong_hop_php_tai.py', PHP, '--tran', '10')
        self.assertIn('Phút có ≥ 10 request PHP bên ngoài đồng thời: 1 / 2 phút', r.stdout)

    def test_thieu_run(self):
        r = run('tong_hop_php_tai.py', PHP.split('\n', 1)[1])
        self.assertNotEqual(r.returncode, 0)


class Rtreport(unittest.TestCase):
    def test_hang_cho_dem_theo_mau(self):
        r = run('rtreport_phan_tich.py', RT)
        self.assertEqual(r.returncode, 0, r.stderr)
        # 2 worker cùng báo hàng chờ ở 1 mẫu → 10 giây, không phải 20.
        self.assertIn('| site.vn | 2 | 10 | 10 | 10 | 4 |', r.stdout)

    def test_mat_mau_va_mat_ket_noi(self):
        # Lỗi thật 24/10/2026: bộ lấy mẫu chết, số hàng chờ 48 giờ thiếu mà không ai biết.
        r = run('rtreport_phan_tich.py', RT)
        self.assertIn('1 lần mất kết nối', r.stdout)
        self.assertIn('mất mẫu', r.stdout)
        self.assertIn('203.0.113.5', r.stdout)
        self.assertIn('CẢNH BÁO: mẫu cuối cách đây', r.stdout)


if __name__ == '__main__':
    unittest.main()
