#!/usr/bin/env python3
"""Kiểm bài HTML trước khi đăng theo luật bài web và web-profile của site.

  python3 kiem_bai.py <bai.html> --profile <web-profile.json> [--online] [--json out.json]

LOI (chặn đăng): không đúng 1 H1 · còn chuỗi giữ chỗ ([LINK-CHỜ, [Chờ media, TODO, {{, [[) · có <script> trong thân ·
câu cam kết hoàn tiền · nhắc brand bên kia · link ra ngoài khi profile link_ngoai = "chu-thich" · thiếu chữ ký thương hiệu ·
ảnh thiếu alt · khối bấm sai cấu trúc (quiz thiếu data-ok, checklist thiếu data-key, tab lệch số nút và số pane,
công thức .calc ngoài phép tính an toàn, nút data-embed thiếu khung đích hoặc link ngoài Google Docs/Drive/Looker Studio) ·
--online: link nội bộ trả 4xx/5xx.
CANH_BAO: H2 không có hình, bảng hay khối bấm · bài không có khối bấm · ảnh thiếu width/height · title hoặc meta
description dài · link nội bộ chuyển hướng · không có link nội bộ.
Cuối báo cáo in luat_rieng của profile để người đăng đọc lại. Mã thoát: 0 đạt, 1 có LOI. Chỉ dùng Python stdlib.
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

CLAIMS = re.compile(r'hoàn\s*(100\s*%|tiền|lại\s*tiền)|money[- ]back|cam\s*kết\s*hoàn', re.I)
HOLD = re.compile(r'\[LINK-CH[ỜO]|\[Ch[ờo] media|\bTODO\b|\{\{|\[\[|\[IMG-\d+\]|cho-media|LINK-CHO', re.I)
VISUAL = re.compile(r'<(figure|table|svg|video)\b|class="[^"]*\b(btabs|bquiz|bchk|calc|tabs|say2|cards|tuong-tac|bcmd|tpl)\b')
EMBED = re.compile(r'^https://(docs|drive|lookerstudio)\.google\.com/')  # cùng danh sách với doc-kit.js
SAFE = re.compile(r'^[\s\d.+\-*/(),]*$')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) wp-xuat-ban-bai/1.0'


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def blocks(body, cls):
    """Nội dung của mọi <div class="cls ..."> tính theo cặp thẻ div cân bằng."""
    out = []
    for m in re.finditer(r'<div class="' + cls + r'\b[^"]*"[^>]*>', body):
        depth, pos = 1, m.end()
        for t in re.finditer(r'<(/?)div\b', body[pos:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                out.append(body[pos:pos + t.start()])
                break
    return out


def status(url):
    req = urllib.request.Request(url, method='GET', headers={'User-Agent': UA})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=20) as r:
            return r.status, ''
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Location', '')
    except Exception as e:  # mạng lỗi: báo, không chặn
        return 0, str(e)[:80]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('html')
    ap.add_argument('--profile', required=True)
    ap.add_argument('--online', action='store_true')
    ap.add_argument('--json')
    a = ap.parse_args()
    src = open(a.html, encoding='utf-8').read()
    prof = json.load(open(a.profile, encoding='utf-8'))
    main_ = (re.search(r'<main[^>]*>([\s\S]*)</main>', src) or re.search(r'<body[^>]*>([\s\S]*)</body>', src) or [None, src])[1]
    body = re.sub(r'<header class="hd">[\s\S]*?</header>', '', main_, count=1)
    plain = text(body)
    loi, canh = [], []

    n_h1 = len(re.findall(r'<h1[\s>]', main_))
    if n_h1 != 1:
        loi.append(f'có {n_h1} thẻ H1, cần đúng 1')
    for m in HOLD.finditer(re.sub(r'<!--/?m:IMG-[\w]+-->', '', body)):
        ctx = text(body[max(0, m.start() - 60):m.end() + 60])
        loi.append(f'còn chuỗi giữ chỗ "{m.group(0)}": …{ctx[:110]}…')
    if re.search(r'<script\b', body):
        loi.append('thân bài có <script>: WordPress bỏ thẻ này. Dùng khối doc-kit (references/khoi-doc-kit.md)')
    c = CLAIMS.search(plain)
    if c:
        loi.append(f'câu cam kết hoàn tiền "{c.group(0)}": luật workspace cấm tự thêm')
    if prof.get('brand_khac'):
        b = re.search(prof['brand_khac'], plain, re.I)
        if b:
            loi.append(f'bài nhắc brand bên kia "{b.group(0)}" (luật tách brand)')
    host = urllib.parse.urlparse(prof.get('url', '')).netloc.replace('www.', '')
    links = re.findall(r'<a\b[^>]*href="([^"]+)"', body)
    internal, external = [], []
    for u in links:
        if u.startswith(('#', 'mailto:', 'tel:')):
            continue
        h = urllib.parse.urlparse(u).netloc.replace('www.', '')
        (internal if (not h or h == host) else external).append(u)
    if external and prof.get('link_ngoai', 'chu-thich') == 'chu-thich':
        for u in sorted(set(external)):
            loi.append(f'link ra ngoài {u}: site này dùng số chú thích, không hyperlink ra ngoài')
    if not internal:
        canh.append('bài không có link nội bộ')
    ck = prof.get('chu_ky') or []
    if ck:
        n = plain.count(ck[0])
        if n == 0:
            loi.append(f'thiếu chữ ký thương hiệu "{ck[0]}" sau kết luận/CTA')
        elif n > 1:
            canh.append(f'chữ ký thương hiệu xuất hiện {n} lần (chuẩn: 1 lần)')
    else:
        canh.append('profile chưa có chu_ky: hỏi người duyệt mẫu chữ ký của brand')
    for im in re.findall(r'<img\b[^>]*>', body):
        if not re.search(r'\balt="[^"]+"', im):
            loi.append(f'ảnh thiếu alt: {im[:90]}')
        if not (re.search(r'\bwidth="\d+"', im) and re.search(r'\bheight="\d+"', im)):
            canh.append(f'ảnh thiếu width/height (gây CLS): {im[:90]}')
    for q in re.findall(r'<div class="qz">([\s\S]*?)</div>\s*(?=<div class="qz">|</div>)', body):
        if 'data-ok' not in q:
            loi.append('câu hỏi .bquiz không có nút đúng data-ok')
    for ch in re.findall(r'<div class="bchk"[^>]*>', body):
        if 'data-key=' not in ch:
            loi.append('checklist .bchk thiếu data-key (trang không nhớ được ô đã đánh dấu)')
    for t in blocks(body, 'btabs'):
        bar = re.search(r'<div class="btab-bar"[^>]*>([\s\S]*?)</div>', t)
        nb = len(re.findall(r'<button', bar.group(1))) if bar else 0
        npn = len(re.findall(r'class="btab-pane"', t))
        if bar and nb != npn:
            loi.append(f'khối tab có {nb} nút nhưng {npn} pane')
    for b in re.findall(r'<[^>]*\bdata-embed="[^"]*"[^>]*>', body):
        tid = re.search(r'data-embed="([^"]*)"', b).group(1)
        src = html.unescape((re.search(r'data-src="([^"]*)"', b) or [None, ''])[1])
        if f'id="{tid}"' not in body:
            loi.append(f'khung xem trước data-embed="{tid}" không có phần tử id="{tid}"')
        if not EMBED.match(src):
            loi.append(f'khung xem trước data-src "{src[:60]}" không phải link Google Docs/Drive/Looker Studio: doc-kit.js không nạp')
    for calc in blocks(body, 'calc'):
        names = re.findall(r'data-i="(\w+)"', calc)
        for f in re.findall(r'data-f="([^"]+)"', calc):
            rest = re.sub(r'round|[A-Za-z_]\w*', lambda m: '' if m.group(0) in names or m.group(0) == 'round' else '#', html.unescape(f))
            if not SAFE.match(rest):
                loi.append(f'công thức .calc "{f}" có tên chưa khai data-i hoặc phép tính ngoài + - * / ( ) round')
    parts = re.split(r'(<h2[\s>])', body)
    secs = [parts[i] + parts[i + 1] for i in range(1, len(parts) - 1, 2)]
    for s in secs:
        title = text((re.search(r'<h2[^>]*>([\s\S]*?)</h2>', s) or [None, ''])[1])
        if not VISUAL.search(s) and not re.search(r'câu hỏi thường gặp|faq|nguồn', title, re.I):
            canh.append(f'H2 "{title[:60]}" chưa có hình, bảng hay khối bấm')
    if not re.search(r'class="[^"]*\b(btabs|bquiz|bchk|calc|tabs)\b', body):
        canh.append('bài chưa có khối bấm thử (tab, quiz, checklist, công cụ tính)')
    t = (re.search(r'<title>([\s\S]*?)</title>', src) or [None, ''])[1]
    d = (re.search(r'<meta name="description" content="([^"]*)"', src) or [None, ''])[1]
    if len(html.unescape(t)) > 62:
        canh.append(f'title {len(html.unescape(t))} ký tự: đo pixel bằng serp_pixel.py của seo-onpage nếu repo có, không thì giữ dưới 60 ký tự')
    if not d:
        canh.append('thiếu meta description')
    elif len(html.unescape(d)) > 160:
        canh.append(f'meta description {len(html.unescape(d))} ký tự (dễ bị cắt)')
    if a.online:
        base = prof.get('url', '').rstrip('/')
        for u in sorted(set(internal)):
            full = u if u.startswith('http') else base + (u if u.startswith('/') else '/' + u)
            code, loc = status(full)
            if code >= 400:
                loi.append(f'link nội bộ {full} trả HTTP {code}')
            elif 300 <= code < 400:
                canh.append(f'link nội bộ {full} chuyển hướng ({code}) tới {loc}: trỏ thẳng URL đích')
            elif code == 0:
                canh.append(f'không kiểm được {full}: {loc}')
    for x in canh:
        print('CANH_BAO', x)
    for x in loi:
        print('LOI', x)
    if prof.get('luat_rieng'):
        print('Luật riêng của site (đọc lại trước khi đăng):')
        for r in prof['luat_rieng']:
            print('  -', r)
    print(f'{len(loi)} lỗi · {len(canh)} cảnh báo · {len(internal)} link nội bộ · {len(re.findall(r"<sup class=.fn.>", body))} chú thích nguồn')
    if a.json:
        json.dump({'loi': loi, 'canh_bao': canh}, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()
