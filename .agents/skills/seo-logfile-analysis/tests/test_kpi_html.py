#!/usr/bin/env python3
"""test_kpi_html.py: mẫu số KPI bỏ infra, loại UA giả và bot Google khác, IP qua X-Forwarded-For chỉ tính khi --trust-xff.

Ca thật: site agency mẫu 26–27/10/2026, KPI tính tay 3 lần trong đêm; chạy kpi_html.py trên log origin của đêm đó cho đúng số tay
(41 lượt, HTML 23, infra 8, % KPI 69,7). IP trong fixture là địa chỉ tài liệu (RFC 5737) và một dải mẫu, không phải IP thật.
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
import kpi_html  # noqa: E402

RANGES = {'prefixes': [{'ipv4Prefix': '203.0.113.0/24'}, {'ipv6Prefix': '2001:db8::/32'}]}
SP = 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
DT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
IMG = 'Googlebot-Image/1.0'


def L(xff, ip, hhmm, path, st, ua, us=None):
    tail = f' {us} "hit"' if us is not None else ''
    return f'\'{xff} {ip} - - [26/Oct/2026:{hhmm}:00 +0700] "GET {path} HTTP/1.1" {st} 100 "-" "{ua}"{tail}\'\n'


LOG = ''.join([
    L('-', '203.0.113.5', '21:30', '/bai-a/', 200, SP, 40000),
    L('-', '203.0.113.5', '21:31', '/bai-cu', 301, SP, 20000),
    L('-', '203.0.113.6', '21:32', '/robots.txt', 200, DT),
    L('-', '203.0.113.6', '21:33', '/sitemap_index.xml', 200, DT),
    L('-', '203.0.113.5', '21:34', '/wp-content/litespeed/css/' + 'a' * 32 + '.css', 200, SP),
    L('-', '203.0.113.5', '22:01', '/bai-xoa/', 410, SP),
    L('-', '198.51.100.9', '22:02', '/bai-b/', 200, SP),                     # UA giả, IP ngoài dải
    L('203.0.113.7', '192.0.2.10', '22:03', '/bai-c/', 200, SP),            # qua CDN
    L('-', '203.0.113.5', '22:04', '/anh.webp', 200, IMG),                   # Googlebot-Image
    L('-', '203.0.113.5', '20:59', '/bai-truoc/', 200, SP),                  # trước --since
    'dòng hỏng\n',
])


def run(*extra):
    d = tempfile.mkdtemp()
    log, rg, js = os.path.join(d, 'a.log'), os.path.join(d, 'r.json'), os.path.join(d, 'o.json')
    open(log, 'w').write(LOG)
    json.dump(RANGES, open(rg, 'w'))
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = kpi_html.main(['--log', log, '--ranges', rg, '--since', '2026-10-26 21:00', '--json', js, *extra])
    return code, json.load(open(js)), buf.getvalue()


class T(unittest.TestCase):
    def test_kpi_mau_so_bo_infra(self):
        code, o, _ = run()
        s = o['tong_hop']
        self.assertEqual(code, 0)
        self.assertEqual((s['tong'], s['html'], s['infra'], s['mau_so']), (6, 3, 2, 4))
        self.assertEqual(s['pct_kpi'], 75.0)
        self.assertEqual(s['ma_html'], {'200': 1, '301': 1, '410': 1})
        self.assertEqual(s['theo_loai']['css-gop'], 1)

    def test_loai_ua_gia_va_bot_khac(self):
        _, o, _ = run()
        self.assertEqual(o['dong']['ua_googlebot_ip_ngoai_dai'], 2)  # UA giả + lượt CDN khi chưa bật --trust-xff
        self.assertEqual(o['dong']['khong_doc_duoc'], 1)

    def test_trust_xff(self):
        _, o, _ = run('--trust-xff')
        self.assertEqual(o['tong_hop']['html'], 4)
        self.assertEqual(o['dong']['ip_qua_xff'], 1)

    def test_theo_gio_va_canh_bao_mau_nho(self):
        _, o, out = run('--by-hour')
        self.assertEqual(sorted(o['theo_gio']), ['2026-10-26 21', '2026-10-26 22'])
        self.assertIn('CẢNH BÁO: mẫu số', out)
        self.assertNotIn('203.0.113', out)

    def test_html_ms(self):
        _, o, _ = run()
        self.assertEqual(o['tong_hop']['html_ms_trung_vi'], 40.0)

    def test_khong_co_dong_ma_2(self):
        d = tempfile.mkdtemp()
        log, rg = os.path.join(d, 'a.log'), os.path.join(d, 'r.json')
        open(log, 'w').write('rác\n')
        json.dump(RANGES, open(rg, 'w'))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(kpi_html.main(['--log', log, '--ranges', rg]), 2)


if __name__ == '__main__':
    unittest.main()
