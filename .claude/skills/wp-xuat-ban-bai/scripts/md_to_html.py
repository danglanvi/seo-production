#!/usr/bin/env python3
"""Chuyển bài Markdown đã humanize thành file HTML bài web theo format blog doc-kit.

  python3 md_to_html.py <bai.md> --profile <web-profile.json> [--out <thư mục>] [--slug <slug>]

Ra <out>/<slug>.html (mặc định cạnh file .md): <head> có <title> và meta description, <main> có header.hd (H1),
thân bài chia khối .prose và khối .wide, mục Nguồn tham khảo.
- Chỉ lấy thân bài: bỏ frontmatter, đoạn lặp meta description dưới H1, phần báo cáo sau thân bài (Change log,
  Data Fix Log, Internal links used, Image placeholders...).
- Link ra ngoài: profile "link_ngoai" = "chu-thich" thì đổi thành số chú thích [n] có tooltip; mục Nguồn tham khảo
  ghi URL dạng chữ. "giu" thì giữ link và thêm rel="noopener".
- Dòng [IMG-NN] thành khung chờ <figure class="wide cho-media" data-img="IMG-NN">. Skill anh-trong-bai thay khung này.
- Chữ ký thương hiệu (profile "chu_ky") thành <p class="chu-ky">.
Chỉ dùng Python stdlib.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse

REPORT = re.compile(r'^##\s+(Change log|Bằng chứng|Ticket|Data Fix|Voice Calibration|Final |Lớp [A-Z]|Post-publish|'
                    r'Internal links used|External links used|Image placeholders|Vòng sửa|Humanness|Checklist trước khi đăng)', re.I)
E = html.escape


def frontmatter(src):
    if not src.startswith('---\n'):
        return {}, src
    end = src.find('\n---\n', 4)
    if end < 0:
        return {}, src
    meta, key = {}, None
    for line in src[4:end].splitlines():
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m:
            key, v = m.group(1), m.group(2).strip()
            meta[key] = [] if v == '' else v.strip('"').strip("'")
        elif key and re.match(r'^\s+-\s+', line) and isinstance(meta.get(key), list):
            meta[key].append(re.sub(r'^\s+-\s+', '', line).strip().strip('"').strip("'"))
    return meta, src[end + 5:]


def body_lines(text, meta):
    """Dòng thân bài và H1. Dừng ở mục báo cáo đầu tiên."""
    lines = text.splitlines()
    h1, out, started = '', [], False
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not h1 and ln.startswith('# '):
            h1 = ln[2:].strip()
            i += 1
            # đoạn lặp meta description ngay dưới H1, rồi dòng ---
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            desc = (meta.get('meta_description') or '').strip()
            if j < len(lines) and desc and lines[j].strip() == desc:
                j += 1
            k = j
            while k < len(lines) and not lines[k].strip():
                k += 1
            if k < len(lines) and lines[k].strip() == '---':
                j = k + 1
            i = j
            started = True
            continue
        if REPORT.match(ln):
            break
        if ln.strip() == '---':
            nxt = next((x for x in lines[i + 1:] if x.strip()), '')
            if REPORT.match(nxt) or not nxt:
                break
            i += 1
            continue
        if started or not h1:
            out.append(ln)
        i += 1
    while out and not out[-1].strip():
        out.pop()
    return h1, out


class Inline:
    def __init__(self, profile):
        self.base = urllib.parse.urlparse(profile.get('url', '')).netloc.replace('www.', '')
        self.mode = profile.get('link_ngoai', 'chu-thich')
        self.sources = []  # [(url, tên)]

    def is_internal(self, u):
        if u.startswith(('#', '/')) and not u.startswith('//'):
            return True
        host = urllib.parse.urlparse(u).netloc.replace('www.', '')
        return bool(self.base) and host == self.base

    def note(self, url, name):
        for n, (u, _) in enumerate(self.sources, 1):
            if u == url:
                return n
        self.sources.append((url, name))
        return len(self.sources)

    def __call__(self, s):
        codes = []

        def keep(m):
            codes.append('<code>' + E(m.group(1)) + '</code>')
            return f'\x00{len(codes) - 1}\x00'

        s = re.sub(r'`([^`]+)`', keep, s)
        links = []

        def restore(x):
            return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], x)

        def link(m):
            text, url = m.group(1), m.group(2).strip()
            t = restore(self.fmt(text))
            if self.is_internal(url):
                links.append(f'<a href="{E(url)}">{t}</a>')
            elif self.mode == 'giu':
                links.append(f'<a href="{E(url)}" rel="noopener" target="_blank">{t}</a>')
            else:
                name = re.sub(r'<[^>]+>', '', t)
                n = self.note(url, html.unescape(name))
                host = urllib.parse.urlparse(url).netloc.replace('www.', '')
                links.append(f'{t}<sup class="fn"><a href="#nguon-{n}" title="{E(html.unescape(name))} ({E(host)})">[{n}]</a></sup>')
            return f'\x01{len(links) - 1}\x01'

        s = re.sub(r'\[([^\]]+)\]\((\S+?)\)', link, s)
        s = self.fmt(s)
        s = re.sub(r'\x01(\d+)\x01', lambda m: links[int(m.group(1))], s)
        return restore(s)

    @staticmethod
    def fmt(s):
        s = E(s, quote=False)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
        return s


def table(rows, inl):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    head, body = cells[0], [r for r in cells[2:]] if len(cells) > 1 and re.match(r'^[\s|:-]+$', rows[1]) else cells[1:]
    th = ''.join(f'<th>{inl(c)}</th>' for c in head)
    tb = ''.join('<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in r) + '</tr>' for r in body)
    return f'<div class="tbl wide"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'


def convert(lines, inl, chu_ky):
    """Trả danh sách khối (loại, html). loại 'p' nằm trong .prose; 'w' là khối rộng."""
    blocks, para, i = [], [], 0
    sig = [re.sub(r'\W+', '', x).lower() for x in chu_ky]

    def flush():
        if not para:
            return
        txt = ' '.join(x.strip() for x in para)
        plain = re.sub(r'\W+', '', re.sub(r'[*_]', '', txt)).lower()
        if sig and sig[0] and plain.startswith(sig[0]):
            parts = [inl(x.strip()) for x in para]
            blocks.append(('p', '<p class="chu-ky">' + '<br>'.join(parts) + '</p>'))
        else:
            blocks.append(('p', f'<p>{inl(txt)}</p>'))
        para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r'^(#{2,4})\s+(.*)$', s)
        if m:
            flush()
            lv = len(m.group(1))
            blocks.append(('p', f'<h{lv}>{inl(m.group(2).strip())}</h{lv}>'))
            i += 1
            continue
        m = re.match(r'^\[(IMG-\d+[a-z]?)\]$', s)
        if m:
            flush()
            blocks.append(('w', f'<figure class="wide cho-media" data-img="{m.group(1)}"><figcaption>[Chờ media {m.group(1)}]</figcaption></figure>'))
            i += 1
            continue
        if s.startswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            blocks.append(('w', table(rows, inl)))
            continue
        if s.startswith('>'):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                q.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            paras = [p for p in re.split(r'\n\s*\n', '\n'.join(q)) if p.strip()]
            blocks.append(('p', '<blockquote>' + ''.join(f'<p>{inl(" ".join(p.split()))}</p>' for p in paras) + '</blockquote>'))
            continue
        m = re.match(r'^([-*]|\d+[.)])\s+', s)
        if m:
            flush()
            ordered = m.group(1)[0].isdigit()
            items = []
            while i < len(lines):
                cur = lines[i]
                mm = re.match(r'^\s*([-*]|\d+[.)])\s+(.*)$', cur)
                if mm and (mm.group(1)[0].isdigit()) == ordered and not cur.startswith('    '):
                    items.append(mm.group(2))
                elif cur.strip() and cur.startswith((' ', '\t')) and items:
                    items[-1] += ' ' + cur.strip()
                else:
                    break
                i += 1
            tag = 'ol' if ordered else 'ul'
            blocks.append(('p', f'<{tag}>' + ''.join(f'<li>{inl(x)}</li>' for x in items) + f'</{tag}>'))
            continue
        if s.startswith('```'):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i])
                i += 1
            i += 1
            if len(code) == 1:
                blocks.append(('p', f'<div class="bcmd" data-noedit><code>{E(code[0])}</code><button type="button">Chép</button></div>'))
            else:
                blocks.append(('p', '<pre><code>' + E('\n'.join(code)) + '</code></pre>'))
            continue
        if s == '---' or (s.startswith('<!--') and s.endswith('-->')):
            flush()
            i += 1
            continue
        if s.startswith('<') and not s.startswith(('<strong', '<em', '<a ', '<code', '<b>', '<i>')):
            flush()
            raw = [ln]
            i += 1
            while i < len(lines) and lines[i].strip():
                raw.append(lines[i])
                i += 1
            blocks.append(('w', '\n'.join(raw)))
            continue
        para.append(ln)
        i += 1
    flush()
    return blocks


def assemble(blocks):
    out, buf = [], []
    for kind, h in blocks:
        if kind == 'p':
            buf.append(h)
        else:
            if buf:
                out.append('<div class="prose">\n' + '\n'.join(buf) + '\n</div>')
                buf = []
            out.append(h)
    if buf:
        out.append('<div class="prose">\n' + '\n'.join(buf) + '\n</div>')
    return '\n\n'.join(out)


def notes(sources, profile):
    if not sources:
        return ''
    title = profile.get('tieu_de_nguon', 'Nguồn tham khảo')
    li = ''.join(f'<li id="nguon-{n}">{E(name)}. {E(urllib.parse.urlparse(u).netloc.replace("www.", ""))}. <span class="url">{E(u)}</span></li>'
                 for n, (u, name) in enumerate(sources, 1))
    return f'<section class="notes prose" id="nguon">\n<h4>{E(title)}</h4>\n<ol>{li}</ol>\n</section>'


def build(md_path, profile, slug=None):
    src = open(md_path, encoding='utf-8').read()
    meta, text = frontmatter(src)
    h1, lines = body_lines(text, meta)
    if not h1:
        sys.exit('Không thấy H1 (dòng "# ...") trong bài.')
    inl = Inline(profile)
    blocks = convert(lines, inl, profile.get('chu_ky') or [])
    first = next((k for k, (t, h) in enumerate(blocks) if t == 'p' and h.startswith('<p>')), None)
    if first is not None:
        blocks[first] = ('p', '<p class="lead">' + blocks[first][1][3:])
    body = assemble(blocks)
    desc = meta.get('meta_description', '')
    title = meta.get('meta_title') or h1
    if not slug:
        u = meta.get('url_slug', '')
        slug = urllib.parse.urlparse(u).path.strip('/').split('/')[-1] if u else ''
        slug = slug or os.path.splitext(os.path.basename(md_path))[0]
    page = (f'<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{E(title)}</title>\n'
            f'<meta name="description" content="{E(desc)}">\n'
            f'<meta name="keyword" content="{E(meta.get("primary_keyword", ""))}">\n'
            f'<meta name="slug" content="{E(slug)}">\n</head>\n<body>\n<main>\n'
            f'<header class="hd">\n<h1>{inl.fmt(h1)}</h1>\n</header>\n\n{body}\n\n{notes(inl.sources, profile)}\n</main>\n</body>\n</html>\n')
    return slug, page, {'h1': h1, 'meta_title': title, 'meta_description': desc, 'keyword': meta.get('primary_keyword', ''),
                        'nguon_ngoai': len(inl.sources), 'cho_media': re.findall(r'data-img="(IMG-[\w]+)"', body)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('md')
    ap.add_argument('--profile', required=True)
    ap.add_argument('--out')
    ap.add_argument('--slug')
    a = ap.parse_args()
    profile = json.load(open(a.profile, encoding='utf-8'))
    slug, page, info = build(a.md, profile, a.slug)
    out = a.out or os.path.dirname(os.path.abspath(a.md))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, slug + '.html')
    open(path, 'w', encoding='utf-8').write(page)
    print(path)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    main()
