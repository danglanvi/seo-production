#!/usr/bin/env python3
"""render_diff.py (wp-paid-plugin-exit): so HTML sau khi đổi plugin với các bản chụp trước, tách khác thật khỏi nhiễu.

Dùng: python3 render_diff.py <trước1,trước2> <sau> [--host <domain>] [--show 3] > ket-qua.json
Mỗi thư mục là output của render_snap.py. Chụp 2 lượt trước để biết phần đổi ngẫu nhiên giữa các lượt.
Một URL "khác thật" khi không bản trước nào trùng, và ở mức nội dung có dòng mà không bản trước nào có (thêm),
hoặc mọi bản trước đều có mà bản sau không có (mất). Dòng chỉ đổi giữa các bản trước là nhiễu.
So 2 mức sau khi chuẩn hoá (nonce, giờ, chuỗi ngẫu nhiên, ô honeypot của WPForms):
  full     toàn bộ HTML
  content  chữ nhìn thấy, href, src, srcset, alt, title, meta robots và canonical, JSON-LD
Lỗi đã gặp 24/10/2026: không bỏ ô honeypot WPForms (nhãn 3 chữ ngẫu nhiên, container position:absolute) thì 11/352 URL báo khác.
Mã thoát 1 khi có URL khác thật hoặc khác mã HTTP.
"""
import json, os, re, sys, difflib, html as H
from collections import Counter

RX = [
    (r'wpa_field_info = JSON\.parse\(atob\("[^"]*"\)\)', 'wpa_field_info=RND'),
    (r'(?<=[-_])[0-9a-f]{13}(?![0-9a-z])', 'UNIQ'),
    (r'(?i)(nonce|_wpnonce|security|_ajax_nonce|ajaxnonce|wpnonce|token)(["\']?\s*[:=]\s*\\?["\']?)[0-9a-f]{8,12}', r'\1\2NONCE'),
    (r'(?i)(data-nonce|data-wpnonce|data-token)="[^"]*"', r'\1="NONCE"'),
    (r'(?i)name="(_wpnonce|wpforms\[nonce\]|[a-z_]*nonce)" value="[^"]*"', r'name="\1" value="NONCE"'),
    (r'<!-- Page (?:generated|optimized|cached) by LiteSpeed[^>]*-->', '<!--LS-->'),
    (r'<!--\s*Performance optimized by[^>]*-->', ''),
    (r'(?i)<!--[^>]*(?:generated in|queries in|served from|seconds|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^>]*-->', '<!--TIME-->'),
    (r'\b1[6-9]\d{8}(?:\.\d+)?\b', 'EPOCH'),
    (r'\b1[6-9]\d{11}\b', 'EPOCHMS'),
    (r'(?i)(wpforms-[a-z0-9-]*?-?)[0-9a-f]{13,}', r'\1RND'),
    (r'(?i)\buc_[a-z0-9_]*?([0-9a-f]{5,})\b', 'UC_RND'),
    (r'(?i)\b(id|for|aria-controls|aria-labelledby|data-id)="([a-z_-]*?)[0-9a-f]{6,}"', r'\1="\2RND"'),
]
CRX = [(re.compile(a), b) for a, b in RX]
HPC = re.compile(r'#(wpforms-\d+-field_\d+)-container\s*\{[^}]*position:\s*absolute')


def norm(t, host=None):
    for fid in set(HPC.findall(t)):  # ô honeypot: container mà CSS của trang đặt position:absolute
        t = re.sub(r'(?s)\s*<div id="' + re.escape(fid) + r'-container"[^>]*>.*?</div>', '<!--WPF-HONEYPOT-->', t)
    t = re.sub(r'(#wpforms-\d+-field_)\d+(-container\s*\{[^}]*position:\s*absolute)', r'\1N\2', t)
    if host:
        t = t.replace(host, 'HOST')
    for r, s in CRX:
        t = r.sub(s, t)
    return t


def content(t):
    out = []
    t2 = re.sub(r'(?is)<(script|style|noscript)\b(?![^>]*application/ld\+json)[^>]*>.*?</\1>', ' ', t)
    for m in re.finditer(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', t):
        out.append('LD ' + re.sub(r'\s+', ' ', m.group(1)).strip())
    for m in re.finditer(r'(?is)<(meta|link)\b[^>]*>', t2):
        tag = m.group(0)
        if re.search(r'(?i)(name|property|rel)="(robots|canonical|description|og:[a-z:]+|twitter:[a-z]+|alternate|hreflang)"', tag):
            out.append('HEAD ' + re.sub(r'\s+', ' ', tag))
    for m in re.finditer(r'(?is)\b(href|src|srcset|data-src|data-srcset|alt|title|data-bg|placeholder|value|action)="([^"]*)"', t2):
        out.append('A %s=%s' % (m.group(1).lower(), m.group(2)))
    for m in re.finditer(r'(?i)url\(([^)]+)\)', t2):
        out.append('U ' + m.group(1))
    for l in re.sub(r'(?s)<[^>]+>', '\n', t2).split('\n'):
        l = re.sub(r'\s+', ' ', H.unescape(l)).strip()
        if l:
            out.append('T ' + l)
    return out


def compare(befores, after, host=None, show=3):
    idx = [{x['i']: x for x in json.load(open(os.path.join(d, 'index.json'), encoding='utf-8'))} for d in befores]
    ia = {x['i']: x for x in json.load(open(os.path.join(after, 'index.json'), encoding='utf-8'))}
    rd = lambda d, i: norm(open(os.path.join(d, '%04d.html' % i), 'rb').read().decode('utf-8', 'replace'), host)
    res = {'n': 0, 'n200': 0, 'status_diff': [], 'full_same': 0, 'content_same': 0, 'noise_only': [], 'real_diff': [], 'detail': {}}
    for i in sorted(ia):
        res['n'] += 1
        u = ia[i]['url']
        res['n200'] += ia[i]['status'] == 200
        key = lambda x: (x['status'], x['loc'])
        if all(key(ix[i]) != key(ia[i]) for ix in idx):
            res['status_diff'].append([u, [ix[i]['status'] for ix in idx], ia[i]['status']])
        tb, tas = rd(after, i), [rd(d, i) for d in befores]
        if tb in tas:
            res['full_same'] += 1
            continue
        cb, cas = content(tb), [content(t) for t in tas]
        if cb in cas:
            res['content_same'] += 1
            continue
        Cb, Cas = Counter(cb), [Counter(c) for c in cas]
        added = [l for l in Cb if all(Cb[l] > Ca.get(l, 0) for Ca in Cas)]
        removed = [l for l in set().union(*Cas) if all(Ca.get(l, 0) > Cb.get(l, 0) for Ca in Cas)]
        if not added and not removed:
            res['noise_only'].append(u)
            continue
        res['real_diff'].append(u)
        la, lb = re.split(r'(?<=>)', tas[0]), re.split(r'(?<=>)', tb)
        d = [x[:300] for x in difflib.unified_diff(la, lb, n=0, lineterm='') if x[:1] in '+-' and not x.startswith(('+++', '---'))]
        res['detail'][u] = {'added': [x[:300] for x in added[:show * 3]], 'removed': [x[:300] for x in removed[:show * 3]], 'full': d[:show * 2]}
    return res


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    host = a[a.index('--host') + 1] if '--host' in a else None
    show = int(a[a.index('--show') + 1]) if '--show' in a else 3
    res = compare(a[0].split(','), a[1], host, show)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"{res['n']} URL: {res['full_same']} trùng, {res['content_same']} trùng nội dung, {len(res['noise_only'])} chỉ nhiễu, "
          f"{len(res['real_diff'])} khác thật, {len(res['status_diff'])} khác mã HTTP", file=sys.stderr)
    return 1 if res['real_diff'] or res['status_diff'] else 0


if __name__ == '__main__':
    sys.exit(main())
