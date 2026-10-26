#!/usr/bin/env python3
"""Quét HTML thừa của trang: entity mã hoá 2 lần, rác dán từ Google Docs, thẻ rỗng, style inline, comment, khoảng trắng.
Chỉ đọc. Nguồn là URL (GET một lần mỗi URL) hoặc file HTML local. Dùng để đo trước và sau khi dọn.

python3 -I cruft_scan.py <urls.txt | thư mục html> --out scan.jsonl [--workers 6] [--force]
python3 -I cruft_scan.py --diff scan_truoc.jsonl scan_sau.jsonl

Nguồn: file văn bản mỗi dòng một URL hoặc một đường dẫn file .html, hoặc thư mục chứa *.html.
Với URL, chỉ gọi site khi người chạy cho phép đo trang thật (đo bằng URL sạch, không utm_*). Test offline chỉ dùng file.
Mỗi dòng ra là một JSON: u, bytes, gz, đếm theo mẫu rác, comment, ws_bytes, style_attr, visible_entities, jsonld_entities.
Luôn in tổng theo mẫu khi quét xong. --diff so hai file kết quả và in mức giảm theo mẫu và tổng byte.
Mã thoát: 0 chạy xong, 1 có nguồn lỗi (URL không tải được, file không đọc được), 2 sai đầu vào hoặc file ra đã có (thêm --force).
"""
import argparse
import concurrent.futures as cf
import glob
import gzip
import html
import json
import os
import re
import sys
import urllib.request

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
P = {
    'dbl_amp': r'&amp;(?:amp|quot|lt|gt|nbsp|#\d+|#x[0-9a-f]+|[a-z]+);',
    'amp_038': r'&#0?38;',
    'nbsp': r'&nbsp;|\xa0',
    'p_empty': r'<p[^>]*>(?:\s|&nbsp;|\xa0|<br\s*/?>)*</p>',
    'span_empty': r'<(span|strong|b|em|i)\b[^>]*>\s*</\1>',
    'gdocs_guid': r'docs-internal-guid',
    'gdocs_fw400': r'style="font-weight:\s*400;?"',
    'gdocs_span_style': r'<span style="[^"]*(?:font-weight|font-family|vertical-align|white-space|background-color: transparent|font-variant)[^"]*">',
    'dir_ltr': r'\sdir="ltr"',
    'aria_level': r'\saria-level="\d"',
    'role_presentation': r'role="presentation"',
    'data_sheets': r'data-sheets-[a-z]+=',
    'mce_bookmark': r'data-mce-type="bookmark"|mce_SELRES',
    'bom': '﻿',
    'type_js': r'<script[^>]*\stype=["\']text/javascript["\']',
    'type_css': r'<(?:style|link)[^>]*\stype=["\']text/css["\']',
    'br_chain': r'(?:<br\s*/?>\s*){2,}',
    'mso': r'class="Mso|mso-[a-z-]+:',
}
COUNT_KEYS = list(P) + ['comments', 'style_attr', 'visible_entities', 'jsonld_entities']


def scan_html(h, u='', raw_len=None):
    raw_len = raw_len if raw_len is not None else len(h.encode('utf-8'))
    r = {'u': u, 'bytes': raw_len, 'gz': len(gzip.compress(h.encode('utf-8'), 6))}
    for k, p in P.items():
        r[k] = len(re.findall(p, h, re.I))
    com = re.findall(r'<!--(?!\[if).*?-->', h, re.S)
    r['comments'], r['comment_bytes'] = len(com), sum(map(len, com))
    r['ws_bytes'] = sum(len(x) - 1 for x in re.findall(r'[ \t\r\n]{2,}', re.sub(r'<(script|style|pre|textarea)\b.*?</\1>', '', h, flags=re.S | re.I)))
    st = re.findall(r'\sstyle="([^"]*)"', h)
    r['style_attr'], r['style_bytes'] = len(st), sum(len(s) + 9 for s in st)
    body = re.sub(r'<(script|style|noscript)\b.*?</\1>', ' ', h, flags=re.S | re.I)
    txt = html.unescape(re.sub(r'<[^>]+>', ' ', body))
    vis = re.findall(r'.{0,40}&(?:amp|quot|nbsp|lt|gt|#\d+|#x[0-9a-f]+);.{0,40}', txt, re.I)
    r['visible_entities'] = len(vis)
    r['vis_ex'] = [re.sub(r'\s+', ' ', v)[:90] for v in vis[:3]]
    lds = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S)
    ldent = [m for s in lds for m in re.findall(r'.{0,30}&(?:amp|quot|#\d+|nbsp);.{0,30}', s)]
    r['jsonld_entities'] = len(ldent)
    r['tags'] = len(re.findall(r'<[a-zA-Z][^>]*>', h))
    return r


def scan_source(src):
    try:
        if src.startswith(('http://', 'https://')):
            raw = urllib.request.urlopen(urllib.request.Request(src, headers={'User-Agent': UA}), timeout=40).read()
        else:
            raw = open(src, 'rb').read()
    except Exception as e:
        return {'u': src, 'err': str(e)[:120]}
    return scan_html(raw.decode('utf-8', 'replace'), src, len(raw))


def sources(path):
    if os.path.isdir(path):
        return sorted(glob.glob(os.path.join(path, '*.html')))
    return [l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('#')]


def total(rows):
    t = {k: 0 for k in COUNT_KEYS + ['bytes', 'gz', 'ws_bytes', 'style_bytes', 'comment_bytes']}
    for r in rows:
        if 'err' in r:
            continue
        for k in t:
            t[k] += r.get(k, 0)
    return t


def cmd_diff(a, b):
    ra = {r['u']: r for r in map(json.loads, open(a, encoding='utf-8')) if 'err' not in r}
    rb = {r['u']: r for r in map(json.loads, open(b, encoding='utf-8')) if 'err' not in r}
    common = sorted(set(ra) & set(rb))
    ta, tb = total([ra[u] for u in common]), total([rb[u] for u in common])
    print('%d trang có ở cả hai file' % len(common))
    for k in ta:
        if ta[k] or tb[k]:
            print('%-18s %10d -> %10d  (%+d)' % (k, ta[k], tb[k], tb[k] - ta[k]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Quét HTML thừa. Xem docstring đầu file.')
    ap.add_argument('src', nargs='?')
    ap.add_argument('--out')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--diff', nargs=2, metavar=('TRUOC', 'SAU'))
    a = ap.parse_args(argv)
    if a.diff:
        if not all(os.path.isfile(x) for x in a.diff):
            print('Thiếu file --diff', file=sys.stderr)
            return 2
        return cmd_diff(*a.diff)
    if not a.src or not a.out or not os.path.exists(a.src):
        print('Cần nguồn (urls.txt hoặc thư mục html) và --out', file=sys.stderr)
        return 2
    if os.path.exists(a.out) and not a.force:
        print('File ra đã có: %s (thêm --force để ghi đè)' % a.out, file=sys.stderr)
        return 2
    srcs = sources(a.src)
    if not srcs:
        print('Không có nguồn nào để quét', file=sys.stderr)
        return 2
    with cf.ThreadPoolExecutor(max(1, a.workers)) as ex:
        rows = list(ex.map(scan_source, srcs))
    with open(a.out, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    bad = [r for r in rows if 'err' in r]
    t = total(rows)
    print('%d nguồn, %d lỗi. Tổng: %s' % (len(rows), len(bad), json.dumps({k: v for k, v in t.items() if v}, ensure_ascii=False)))
    for r in bad:
        print('LỖI %s: %s' % (r['u'], r['err']), file=sys.stderr)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
