#!/usr/bin/env python3
"""KPI "tỉ lệ HTML trong lượt Googlebot web" từ access log, kèm chia theo loại file, mã HTML, loại bot và theo giờ.

Định nghĩa (site agency mẫu, người duyệt chốt 26/10/2026):
- Googlebot web = UA Googlebot smartphone hoặc desktop (không tính Image, Video, AdsBot, StoreBot, InspectionTool, GoogleOther)
  và IP nằm trong dải Googlebot (file JSON Google công bố). Log sau CDN: thêm --trust-xff để xét IP đầu của X-Forwarded-For.
- HTML = GET vào URL trang, mọi mã (200, 301, 404, 410...). Infra = robots.txt, sitemap, ads.txt, llm(s).txt, assetlinks.
- % KPI = HTML / (mọi lượt trừ infra). % gốc = HTML / mọi lượt.

Ví dụ:
  python3 -I kpi_html.py --log access.log --log access.log.1.gz --ranges googlebot.json --since "2026-10-26 21:22" --by-hour --json kpi.json
Giờ so theo giờ ghi trong log (bỏ múi giờ). Mã thoát: 0 = có số, 2 = không đọc được dòng nào hoặc mẫu số bằng 0.
Script không in IP.
"""
import argparse
import gzip
import ipaddress
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

# Định dạng combined, có thể có trường X-Forwarded-For đứng trước IP (logFormat OLS mẫu) và dấu ' đầu dòng.
LINE = re.compile(r"^'?(?:(?P<xff>\S+) )?(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] \"(?P<meth>\S+) (?P<path>\S+)[^\"]*\" "
                  r"(?P<st>\d{3}) \S+ \"[^\"]*\" \"(?P<ua>[^\"]*)\"(?: (?P<us>\d+))?")
INFRA = {'/robots.txt', '/ads.txt', '/llm.txt', '/llms.txt', '/.well-known/assetlinks.json'}
OTHER_GOOGLE = ('googlebot-image', 'googlebot-video', 'adsbot', 'storebot', 'google-inspectiontool', 'googleother', 'mediapartners')
SMALL = 30


def load_ranges(path):
    nets = [ipaddress.ip_network(p.get('ipv4Prefix') or p.get('ipv6Prefix')) for p in json.load(open(path))['prefixes']]
    return [n for n in nets if n.version == 4], [n for n in nets if n.version == 6]


def in_ranges(ip, ranges):
    try:
        a = ipaddress.ip_address(ip.strip())
    except ValueError:
        return False
    return any(a in n for n in ranges[0 if a.version == 4 else 1])


def bot(ua):
    u = ua.lower()
    if 'googlebot' not in u or any(k in u for k in OTHER_GOOGLE):
        return None
    return 'smartphone' if ('mobile' in u or 'android' in u) else 'desktop'


def ftype(path, css_prefix):
    q = path.split('?')[0].lower()
    m = re.search(r'\.([a-z0-9]{2,5})$', q)
    e = m.group(1) if m else ''
    if q in INFRA or e == 'xsl' or (e == 'xml' and 'sitemap' in q):
        return 'infra'
    if css_prefix and q.startswith(css_prefix) and e == 'css':
        return 'css-gop'
    if e in ('woff2', 'woff', 'ttf', 'otf', 'eot'):
        return 'font'
    if e in ('jpg', 'jpeg', 'png', 'webp', 'avif', 'gif', 'svg', 'ico'):
        return 'image'
    if e in ('css', 'js'):
        return e
    if e in ('xml', 'rss', 'atom', 'json') or '/feed' in q or q.startswith('/wp-json'):
        return 'feed-json'
    if e or q.startswith(('/wp-content/', '/wp-includes/', '/wp-admin/')):
        return 'khac'
    return 'html'


def parse_when(s):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%b/%Y:%H:%M:%S'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise SystemExit(f'Không hiểu giờ: {s}')


def rows(paths, ranges, trust_xff, since, until, css_prefix, stats):
    for path in paths:
        op = gzip.open if path.endswith('.gz') else open
        with op(path, 'rt', encoding='utf-8', errors='replace') as f:
            for line in f:
                if not line.strip():
                    continue
                m = LINE.match(line)
                if not m:
                    stats['khong_doc_duoc'] += 1
                    continue
                stats['doc_duoc'] += 1
                b = bot(m['ua'])
                if not b:
                    continue
                if not in_ranges(m['ip'], ranges):
                    first = (m['xff'] or '').split(',')[0]
                    if not (trust_xff and first and in_ranges(first, ranges)):
                        stats['ua_googlebot_ip_ngoai_dai'] += 1
                        continue
                    stats['ip_qua_xff'] += 1
                t = datetime.strptime(m['time'].split()[0], '%d/%b/%Y:%H:%M:%S')
                if (since and t < since) or (until and t > until):
                    continue
                yield dict(t=t, b=b, st=int(m['st']), ft=ftype(m['path'], css_prefix),
                           ms=int(m['us']) / 1000 if m['us'] else None)


def summ(rs):
    c = Counter(r['ft'] for r in rs)
    n, h, inf = len(rs), c['html'], c['infra']
    ms = sorted(r['ms'] for r in rs if r['ft'] == 'html' and r['ms'] is not None)
    return dict(tong=n, html=h, infra=inf, mau_so=n - inf, theo_loai=dict(c),
                pct_goc=round(100 * h / n, 1) if n else None,
                pct_kpi=round(100 * h / (n - inf), 1) if n - inf else None,
                ma_html=dict(Counter(r['st'] for r in rs if r['ft'] == 'html')),
                html_ms_trung_vi=round(ms[len(ms) // 2], 1) if ms else None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--log', action='append', required=True)
    ap.add_argument('--ranges', required=True, help='googlebot.json Google công bố')
    ap.add_argument('--trust-xff', action='store_true', help='log sau CDN: xét IP đầu của X-Forwarded-For')
    ap.add_argument('--since')
    ap.add_argument('--until')
    ap.add_argument('--by-hour', action='store_true')
    ap.add_argument('--css-prefix', default='/wp-content/litespeed/css/', help='đường dẫn file CSS gộp; rỗng để tắt')
    ap.add_argument('--json')
    a = ap.parse_args(argv)
    stats = Counter()
    rs = list(rows(a.log, load_ranges(a.ranges), a.trust_xff, a.since and parse_when(a.since),
                   a.until and parse_when(a.until), a.css_prefix, stats))
    out = dict(tong_hop=summ(rs), smartphone=summ([r for r in rs if r['b'] == 'smartphone']),
               desktop=summ([r for r in rs if r['b'] == 'desktop']), dong=dict(stats))
    if a.by_hour:
        by = defaultdict(list)
        for r in rs:
            by[r['t'].strftime('%Y-%m-%d %H')].append(r)
        out['theo_gio'] = {k: summ(v) for k, v in sorted(by.items())}
    s = out['tong_hop']
    print(f"Googlebot web: {s['tong']} lượt, HTML {s['html']}, infra {s['infra']}, mẫu số KPI {s['mau_so']}; "
          f"% gốc {s['pct_goc']}, % KPI {s['pct_kpi']}")
    print('Theo loại:', s['theo_loai'], '| mã HTML:', s['ma_html'], '| HTML ms trung vị:', s['html_ms_trung_vi'])
    for k in ('smartphone', 'desktop'):
        print(f"{k}: {out[k]['tong']} lượt, % KPI {out[k]['pct_kpi']}")
    for k, v in out.get('theo_gio', {}).items():
        print(f'{k}h: % KPI {v["pct_kpi"]} ({v["mau_so"]})')
    print('Dòng:', dict(stats))
    if s['mau_so'] and s['mau_so'] < SMALL:
        print(f'CẢNH BÁO: mẫu số {s["mau_so"]} < {SMALL}, không kết luận theo giờ hay theo ngày từ số này.')
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    return 0 if stats['doc_duoc'] and s['mau_so'] else 2


if __name__ == '__main__':
    sys.exit(main())
