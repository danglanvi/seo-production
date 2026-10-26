#!/usr/bin/env python3
"""Tự host một URL CSS của Google Fonts, giữ đúng subset, unicode-range và thứ tự rule như CSS của Google.

Dùng:
  python3 -I gfonts_selfhost.py "https://fonts.googleapis.com/css2?family=Roboto:wght@700;800;900&display=swap" \
      --out <thư mục font của theme> --prefix roboto --url-base /wp-content/themes/<theme>/assets/fonts

Ghi: file <prefix>-<subset>.woff2 (font biến thiên: một file cho mọi độ đậm) hoặc <prefix>-<độ đậm>-<subset>.woff2 (font tĩnh),
và <prefix>.css (một @font-face cho mỗi file). Font biến thiên khai báo font-weight bằng khoảng nhỏ nhất đến lớn nhất mà URL xin.
Trang chỉ xin một độ đậm thì khai đúng một giá trị, để chữ không đổi độ đậm so với bản Google.
Không preload file nào. Ghi giấy phép (thường là OFL) vào README của theme.
"""
import argparse
import collections
import os
import re
import sys
import urllib.request

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
TEN_SUBSET = {'vietnamese': 'vi'}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
    return b if binary else b.decode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('css_url')
    ap.add_argument('--out', required=True)
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--url-base', default='.')
    ap.add_argument('--subsets', help='chỉ giữ các subset này, ví dụ vietnamese,latin,latin-ext. Mặc định giữ mọi subset Google trả')
    a = ap.parse_args()
    if not a.css_url.startswith('https://fonts.googleapis.com/'):
        sys.exit('Chỉ nhận URL fonts.googleapis.com')
    css = get(a.css_url)
    rules = []
    for sub, body in re.findall(r'/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{([^}]*)\}', css):
        f = dict(re.findall(r'([\w-]+):\s*([^;]+);', body))
        src = re.search(r'url\((https://[^)]+)\)', f.get('src', ''))
        if not src:
            sys.exit('Rule thiếu url: ' + body[:80])
        rules.append({'sub': sub, 'family': f['font-family'].strip("'\""), 'style': f.get('font-style', 'normal'),
                      'weight': int(f.get('font-weight', '400').split()[0]), 'url': src.group(1), 'range': f.get('unicode-range', '').strip()})
    if a.subsets:
        rules = [r for r in rules if r['sub'] in a.subsets.split(',')]
    if not rules:
        sys.exit('CSS không có @font-face kèm chú thích subset, hoặc --subsets loại hết. Kiểm UA, URL, tên subset.')
    # Gom các rule dùng chung một file (font biến thiên), giữ thứ tự xuất hiện đầu tiên
    files = collections.OrderedDict()
    for r in rules:
        files.setdefault((r['url'], r['style']), []).append(r)
    tinh = any(len({r['url'] for r in rules if r['sub'] == s}) > 1 for s in {r['sub'] for r in rules})
    os.makedirs(a.out, exist_ok=True)
    out_css, rows = [], []
    for (url, style), rs in files.items():
        r0 = rs[0]
        w = sorted({r['weight'] for r in rs})
        sub = TEN_SUBSET.get(r0['sub'], r0['sub'])
        name = a.prefix + (f'-{w[0]}' if tinh else '') + ('-italic' if style == 'italic' else '') + f'-{sub}.woff2'
        data = get(url, binary=True)
        if data[:4] != b'wOF2':
            sys.exit(f'File tải về không phải WOFF2: {url}')
        with open(os.path.join(a.out, name), 'wb') as fh:
            fh.write(data)
        fw = str(w[0]) if len(w) == 1 else f'{w[0]} {w[-1]}'
        out_css.append(f"@font-face{{font-family:'{r0['family']}';font-style:{style};font-weight:{fw};font-display:swap;"
                       f"src:url({a.url_base.rstrip('/')}/{name}) format('woff2');unicode-range:{r0['range']}}}")
        rows.append((name, r0['sub'], fw, len(data) // 1024))
    with open(os.path.join(a.out, a.prefix + '.css'), 'w') as fh:
        fh.write('\n'.join(out_css) + '\n')
    print(f"{'file':<34} {'subset':<12} {'độ đậm':<9} KB")
    for n, s, fw, kb in rows:
        print(f'{n:<34} {s:<12} {fw:<9} {kb}')
    print(f'{"font tĩnh" if tinh else "font biến thiên"}: {len(rows)} file, CSS ở {os.path.join(a.out, a.prefix + ".css")}')


if __name__ == '__main__':
    main()
