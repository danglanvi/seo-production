#!/usr/bin/env python3
"""Đăng bài HTML (format tài liệu pages.dev hoặc HTML thường) lên WordPress gtvseo.com / theaigrowth.io qua REST + app password.

Lệnh:
  python3 wp_publish.py doctor --site gtv|tag
  python3 wp_publish.py push <bai.html> --site gtv|tag [--status draft|publish] [--slug s] [--category slug1,slug2]
                         [--tags t1,t2] [--title "…"] [--seo-title "…"] [--seo-desc "…"] [--keyword "…"]
                         [--featured <ảnh>|first] [--id <post id>] [--allow-claims] [--dry-run]
  python3 wp_publish.py media <file> --site gtv|tag [--alt "…"]
  python3 wp_publish.py trash <bai.html> --site gtv|tag      (bỏ bài đã đăng từ file này vào thùng rác)

Key (biến môi trường, hoặc file .env tìm từ thư mục hiện tại đi lên, ưu tiên .agent-secrets/.env):
  WP_GTV_URL, WP_GTV_USER, WP_GTV_APP_PASSWORD · WP_TAG_URL, WP_TAG_USER, WP_TAG_APP_PASSWORD
Đăng lại cùng file thì cập nhật đúng bài cũ (lưu ID trong <bai.html>.wp.json). Ảnh đã tải không tải lại.
Chỉ dùng Python stdlib."""
import argparse
import base64
import hashlib
import html
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from css_scope import scope  # noqa: E402

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) wp-dang-bai/1.0'
DEFAULT_URL = {'gtv': 'https://gtvseo.com', 'tag': 'https://theaigrowth.io'}
CLAIMS = re.compile(r'hoàn\s*(100\s*%|tiền|lại\s*tiền)|money[- ]back|cam\s*kết\s*hoàn', re.I)
OTHER_BRAND = {'gtv': re.compile(r'The AI Growth|theaigrowth\.io', re.I), 'tag': re.compile(r'GTV SEO|gtvseo\.com', re.I)}


def load_env():
    env, d = {}, os.path.abspath(os.getcwd())
    files = []
    while True:
        files += [os.path.join(d, '.agent-secrets', '.env'), os.path.join(d, '.env')]
        p = os.path.dirname(d)
        if p == d:
            break
        d = p
    for f in reversed(files):
        if os.path.isfile(f):
            for line in open(f, encoding='utf-8'):
                m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
                if m:
                    env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k.startswith('WP_')})
    return env


class WP:
    def __init__(self, site):
        e = load_env()
        p = 'WP_' + site.upper() + '_'
        self.base = (e.get(p + 'URL') or DEFAULT_URL[site]).rstrip('/')
        user, pw = e.get(p + 'USER'), (e.get(p + 'APP_PASSWORD') or '').replace(' ', '')
        if not user or not pw:
            sys.exit(f'Thiếu {p}USER hoặc {p}APP_PASSWORD trong .env. Xem hướng dẫn trong SKILL.md mục Cài đặt.')
        self.auth = 'Basic ' + base64.b64encode(f'{user}:{pw}'.encode()).decode()
        self.host = e.get(p + 'HOST')  # chỉ dùng cho staging gọi qua tunnel

    def req(self, method, path, data=None, headers=None, raw=None):
        url = path if path.startswith('http') else self.base + '/wp-json' + path
        h = {'Authorization': self.auth, 'User-Agent': UA, 'Accept': 'application/json'}
        if self.host:
            h['Host'] = self.host
        body = raw
        if data is not None:
            body = json.dumps(data).encode()
            h['Content-Type'] = 'application/json'
        h.update(headers or {})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h, method=method), timeout=180) as r:
                return r.status, json.loads(r.read().decode() or 'null')
        except urllib.error.HTTPError as err:
            try:
                j = json.loads(err.read().decode())
            except Exception:
                j = {}
            return err.code, j


def die(code, j, what):
    sys.exit(f'Lỗi {what}: HTTP {code} {j.get("code", "")} {j.get("message", "")}'.strip())


def doctor(a):
    wp = WP(a.site)
    c, me = wp.req('GET', '/wp/v2/users/me?context=edit')
    if c != 200:
        die(c, me, 'đăng nhập bằng app password')
    print(f'OK {wp.base}: {me.get("name")} · role {", ".join(me.get("roles", []))}')
    c, sch = wp.req('OPTIONS', '/wp/v2/posts')
    props = (sch or {}).get('schema', {}).get('properties', {})
    meta = props.get('meta', {}).get('properties', {})
    print('doc-kit trên site:', 'có' if '_doc_kit' in meta and 'doc_seo' in props else 'CHƯA CÓ (báo admin cài mu-plugin doc-kit)')


def extract(src):
    """Trả (title, desc, body_html, doc_css) từ file HTML."""
    title = desc = ''
    m = re.search(r'<header class="hd">([\s\S]*?)</header>', src)
    if m:
        t = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', m.group(1))
        title = re.sub(r'<[^>]+>', '', t.group(1)).strip() if t else ''
    if not title:
        t = re.search(r'<title>([\s\S]*?)</title>', src) or re.search(r'<h1[^>]*>([\s\S]*?)</h1>', src)
        title = re.sub(r'<[^>]+>', '', t.group(1)).strip() if t else ''
    d = re.search(r'<meta name="description" content="([^"]*)"', src)
    desc = html.unescape(d.group(1)) if d else ''
    css = []
    head = src.split('<body', 1)[0] if '<body' in src else ''
    for s in re.findall(r'<style[^>]*>([\s\S]*?)</style>', head):
        if 'Format bài blog của site tài liệu GTV' in s or ':root{--bg:#FAF9F5' in s:
            continue
        css.append(scope(s))
    m = re.search(r'<main[^>]*>([\s\S]*)</main>', src)
    if m:
        body = m.group(1)
    elif '<body' in src:
        body = re.search(r'<body[^>]*>([\s\S]*)</body>', src).group(1)
    else:
        body = src
    body = re.sub(r'<header class="hd">[\s\S]*?</header>', '', body, count=1)
    body = re.sub(r'<script[\s\S]*?</script>', '', body)
    body = re.sub(r'<style[\s\S]*?</style>', '', body)
    body = re.sub(r'<nav class="nav">[\s\S]*?</nav>|<footer class="ft">[\s\S]*?</footer>', '', body)
    return html.unescape(title), desc, body.strip(), '\n'.join(c for c in css if c.strip())


def upload(wp, state, data, name, alt=''):
    sha = hashlib.sha256(data).hexdigest()
    if sha in state['media']:
        return state['media'][sha]
    ctype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    c, j = wp.req('POST', '/wp/v2/media', raw=data, headers={'Content-Type': ctype, 'Content-Disposition': f'attachment; filename="{name}"'})
    if c not in (200, 201):
        die(c, j, f'tải {name}')
    if alt:
        wp.req('POST', f'/wp/v2/media/{j["id"]}', data={'alt_text': alt})
    state['media'][sha] = {'id': j['id'], 'url': j['source_url']}
    print(f'  ảnh/video: {name} → media {j["id"]}')
    return state['media'][sha]


def slugify(s):
    s = s.lower().replace('đ', 'd')
    s = ''.join(ch for ch in __import__('unicodedata').normalize('NFD', s) if not __import__('unicodedata').combining(ch))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:70] or 'bai'


def push(a):
    src_path = os.path.abspath(a.file)
    src = open(src_path, encoding='utf-8').read()
    title, desc, body, css = extract(src)
    title = a.title or title
    slug = a.slug or slugify(title)
    text = re.sub(r'<[^>]+>', ' ', body)
    if CLAIMS.search(text) and not a.allow_claims:
        sys.exit('Dừng: bài có câu cam kết hoàn tiền ("' + CLAIMS.search(text).group(0) + '"). Luật GTV/TAG cấm tự thêm. Xoá câu đó, hoặc thêm --allow-claims nếu Vincent đã duyệt.')
    if OTHER_BRAND[a.site].search(text):
        print(f'Cảnh báo: bài đăng lên {a.site.upper()} có nhắc brand bên kia ("{OTHER_BRAND[a.site].search(text).group(0)}"). Kiểm luật GTV ≠ TAG.')
    if a.dry_run:
        print(f'[dry-run] tiêu đề: {title}\n[dry-run] slug: {slug} · thân bài {len(body):,} ký tự · CSS riêng {len(css):,} ký tự')
        n_data = len(re.findall(r'(?:src|poster)="data:', body))
        n_file = len([u for u in re.findall(r'(?:src|poster)="([^"]+)"', body) if not u.startswith(('http', 'data:', '//', '#'))])
        print(f'[dry-run] ảnh data: {n_data} · file cục bộ: {n_file}')
        return
    wp = WP(a.site)
    state_path = src_path + '.wp.json'
    allst = json.load(open(state_path)) if os.path.exists(state_path) else {}
    state = allst.setdefault(a.site, {'post_id': None, 'media': {}})
    n = [0]

    def repl_data(m):
        attr, mime, b64 = m.group(1), m.group(2), m.group(3)
        n[0] += 1
        ext = mimetypes.guess_extension(mime) or '.bin'
        ext = '.jpg' if ext in ('.jpe', '.jpeg') else ext
        alt = ''
        return f'{attr}="{upload(wp, state, base64.b64decode(b64), f"{slug}-{n[0]}{ext}", alt)["url"]}"'

    body = re.sub(r'(src|poster)="data:([\w/+.-]+);base64,([A-Za-z0-9+/=\s]+)"', repl_data, body)

    def repl_file(m):
        attr, u = m.group(1), m.group(2)
        if u.startswith(('http', 'data:', '//', '#', 'mailto:')):
            return m.group(0)
        p = os.path.normpath(os.path.join(os.path.dirname(src_path), urllib.parse.unquote(u)))
        if not os.path.isfile(p):
            print(f'Cảnh báo: không thấy file {u}, giữ nguyên đường dẫn.')
            return m.group(0)
        name = os.path.basename(p)
        return f'{attr}="{upload(wp, state, open(p, "rb").read(), name)["url"]}"'

    body = re.sub(r'(src|poster)="([^"]+)"', repl_file, body)
    for im in re.finditer(r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]+)"', body):
        for v in state['media'].values():
            if v['url'] == im.group(1) and not v.get('alt'):
                wp.req('POST', f'/wp/v2/media/{v["id"]}', data={'alt_text': html.unescape(im.group(2))})
                v['alt'] = 1

    post = {'title': title, 'content': body, 'slug': slug, 'status': a.status,
            'meta': {'_doc_kit': True, '_doc_kit_css': css},
            'doc_seo': {'title': a.seo_title or '', 'description': a.seo_desc or desc, 'focus_keyword': a.keyword or ''}}
    if a.category:
        ids = []
        for s in a.category.split(','):
            c, j = wp.req('GET', '/wp/v2/categories?slug=' + urllib.parse.quote(s.strip()))
            if c == 200 and j:
                ids.append(j[0]['id'])
            else:
                print(f'Cảnh báo: không có chuyên mục "{s}".')
        if ids:
            post['categories'] = ids
    if a.tags:
        ids = []
        for s in a.tags.split(','):
            c, j = wp.req('GET', '/wp/v2/tags?search=' + urllib.parse.quote(s.strip()))
            hit = [t for t in (j or []) if t['name'].lower() == s.strip().lower()] if c == 200 else []
            if hit:
                ids.append(hit[0]['id'])
            else:
                print(f'Cảnh báo: thẻ "{s}" chưa có trên site. Người đăng bài không tạo được thẻ mới, nhờ SEO Leader tạo.')
        if ids:
            post['tags'] = ids
    if a.featured:
        if a.featured == 'first':
            first = re.search(r'<img[^>]+src="([^"]+)"', body)
            hit = [v for v in state['media'].values() if first and v['url'] == first.group(1)]
            if hit:
                post['featured_media'] = hit[0]['id']
        else:
            post['featured_media'] = upload(wp, state, open(a.featured, 'rb').read(), os.path.basename(a.featured), title)['id']

    pid = a.id or state.get('post_id')
    c, j = wp.req('POST', f'/wp/v2/posts/{pid}' if pid else '/wp/v2/posts', data=post)
    if c not in (200, 201):
        json.dump(allst, open(state_path, 'w'), ensure_ascii=False, indent=1)
        die(c, j, 'đăng bài')
    state['post_id'] = j['id']
    json.dump(allst, open(state_path, 'w'), ensure_ascii=False, indent=1)
    raw = j.get('content', {}).get('raw', '')
    lost = [t for t in ('<svg', '<button', '<input', '<video', '<details') if body.count(t) > raw.count(t)]
    if lost:
        print('Cảnh báo: WordPress lọc bớt thẻ ' + ', '.join(lost) + '. Báo admin kiểm mu-plugin doc-kit.')
    print(f'{"Cập nhật" if pid else "Tạo"} bài {j["id"]} · trạng thái {j["status"]} · {j["link"]}')
    if j['status'] != 'publish':
        print(f'Xem trước (cần đăng nhập): {wp.base}/?p={j["id"]}&preview=true')


def trash(a):
    state_path = os.path.abspath(a.file) + '.wp.json'
    allst = json.load(open(state_path)) if os.path.exists(state_path) else {}
    pid = (allst.get(a.site) or {}).get('post_id')
    if not pid:
        sys.exit(f'Không thấy ID bài của file này trên {a.site} (thiếu {os.path.basename(state_path)}).')
    wp = WP(a.site)
    c, j = wp.req('DELETE', f'/wp/v2/posts/{pid}')
    if c != 200:
        die(c, j, 'bỏ bài vào thùng rác')
    allst[a.site]['post_id'] = None
    json.dump(allst, open(state_path, 'w'), ensure_ascii=False, indent=1)
    print(f'Đã chuyển bài {pid} vào thùng rác (khôi phục được trong wp-admin 30 ngày). Ảnh đã tải vẫn nằm trong Media.')


def media(a):
    wp = WP(a.site)
    st = {'media': {}}
    print(upload(wp, st, open(a.file, 'rb').read(), os.path.basename(a.file), a.alt or '')['url'])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest='cmd', required=True)
    d = sp.add_parser('doctor')
    d.add_argument('--site', choices=['gtv', 'tag'], required=True)
    u = sp.add_parser('push')
    u.add_argument('file')
    u.add_argument('--site', choices=['gtv', 'tag'], required=True)
    u.add_argument('--status', choices=['draft', 'publish', 'pending', 'private'], default='draft')
    for o in ('--slug', '--category', '--tags', '--title', '--seo-title', '--seo-desc', '--keyword', '--featured'):
        u.add_argument(o)
    u.add_argument('--id', type=int)
    u.add_argument('--allow-claims', action='store_true')
    u.add_argument('--dry-run', action='store_true')
    m = sp.add_parser('media')
    m.add_argument('file')
    m.add_argument('--site', choices=['gtv', 'tag'], required=True)
    m.add_argument('--alt')
    t = sp.add_parser('trash')
    t.add_argument('file')
    t.add_argument('--site', choices=['gtv', 'tag'], required=True)
    a = p.parse_args()
    {'doctor': doctor, 'push': push, 'media': media, 'trash': trash}[a.cmd](a)


if __name__ == '__main__':
    main()
