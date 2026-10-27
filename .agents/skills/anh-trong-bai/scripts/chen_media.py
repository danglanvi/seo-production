#!/usr/bin/env python3
"""Chèn media đã dựng vào khung chờ <figure class="wide cho-media" data-img="IMG-NN"> của bài HTML.

  python3 chen_media.py <bai.html> media_plan.json [--out <bai mới.html>]

- so-do: SVG inline 2 bản (.sv-d desktop, .sv-m điện thoại), thêm CSS đổi bản theo bề rộng vào <head> một lần.
- anh-chup, anh-ai, anh-that: <img> có alt, width, height, loading="lazy", decoding="async" và <figcaption>.
- tuong-tac: chèn nguyên khối HTML trong file "html" (khối doc-kit), caption nếu có.
- video: YouTube chèn ảnh xem trước có nút phát (facade, không iframe); file MP4 dùng <video preload="metadata">.
Mục chưa có file thì giữ khung chờ và in cảnh báo. Mặc định ghi đè <bai.html>. Chỉ dùng Python stdlib.
"""
import argparse
import html
import json
import os
import re
import struct
import sys

E = html.escape
CSS = '.sv-m{display:none}@media (max-width:640px){.sv-d{display:none}.sv-m{display:block}}figure.svgfig svg{display:block;width:100%;height:auto}'


def img_size(p):
    b = open(p, 'rb').read(64)
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', b[16:24])
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        k = b[12:16]
        if k == b'VP8X':
            return 1 + int.from_bytes(b[24:27], 'little'), 1 + int.from_bytes(b[27:30], 'little')
        if k == b'VP8 ':
            w, h = struct.unpack('<HH', b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if k == b'VP8L':
            v = int.from_bytes(b[21:25], 'little')
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if b[:2] == b'\xff\xd8':
        f = open(p, 'rb')
        f.read(2)
        while True:
            m = f.read(2)
            if len(m) < 2 or m[0] != 0xFF:
                break
            ln = struct.unpack('>H', f.read(2))[0]
            if m[1] in (0xC0, 0xC1, 0xC2):
                f.read(1)
                h, w = struct.unpack('>HH', f.read(4))
                return w, h
            f.read(ln - 2)
    return None, None


def figure(it, base, html_dir):
    cap = it.get('caption', '')
    fc = f'<figcaption>{E(cap)}</figcaption>' if cap else ''
    i = it['id']
    if it.get('loai') == 'so-do' and it.get('svg'):
        d = open(os.path.join(base, it['svg']), encoding='utf-8').read()
        m = open(os.path.join(base, it['svg_m']), encoding='utf-8').read() if it.get('svg_m') else ''
        inner = f'<div class="sv-d">{d}</div><div class="sv-m">{m}</div>' if m else d
        return f'<figure class="wide svgfig" data-img="{i}">{inner}{fc}</figure>'
    if it.get('loai') == 'tuong-tac' and it.get('html'):
        block = open(os.path.join(base, it['html']), encoding='utf-8').read().strip()
        return f'<div class="tuong-tac" data-img="{i}">{block}</div>' + (f'<p class="fine">{E(cap)}</p>' if cap and it.get('caption_duoi') else '')
    if it.get('loai') == 'video' and it.get('youtube'):
        y = E(it['youtube'])
        return (f'<figure class="wide vid" data-img="{i}"><a class="yt" href="https://www.youtube.com/watch?v={y}" data-yt="{y}">'
                f'<img src="https://i.ytimg.com/vi/{y}/hqdefault.jpg" alt="{E(it.get("alt", ""))}" width="480" height="360" loading="lazy" decoding="async"></a>{fc}</figure>')
    if it.get('src'):
        p = os.path.normpath(os.path.join(base, it['src']))
        rel = os.path.relpath(p, html_dir)
        if p.lower().endswith('.mp4'):
            poster = f' poster="{E(os.path.relpath(os.path.join(base, it["poster"]), html_dir))}"' if it.get('poster') else ''
            return f'<figure class="wide vid" data-img="{i}"><video controls preload="metadata" playsinline{poster} src="{E(rel)}"></video>{fc}</figure>'
        w, h = img_size(p)
        wh = f' width="{w}" height="{h}"' if w else ''
        return f'<figure class="wide" data-img="{i}"><img src="{E(rel)}" alt="{E(it.get("alt", ""))}"{wh} loading="lazy" decoding="async">{fc}</figure>'
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('html')
    ap.add_argument('plan')
    ap.add_argument('--out')
    a = ap.parse_args()
    src = open(a.html, encoding='utf-8').read()
    plan = json.load(open(a.plan, encoding='utf-8'))
    base = os.path.dirname(os.path.abspath(a.plan))
    out = a.out or a.html
    html_dir = os.path.dirname(os.path.abspath(out))
    done, wait = [], []
    for it in plan['items']:
        i = re.escape(it['id'])
        # Khung chờ của md_to_html, hoặc khối đã chèn lần trước (bọc comment m:ID để chèn lại được).
        pat = re.compile(r'<figure class="wide cho-media" data-img="' + i + r'">[\s\S]*?</figure>|<!--m:' + i + r'-->[\s\S]*?<!--/m:' + i + r'-->')
        if not pat.search(src):
            continue
        f = figure(it, base, html_dir)
        if f is None:
            wait.append(it['id'])
            continue
        f = f'<!--m:{it["id"]}-->{f}<!--/m:{it["id"]}-->'
        src = pat.sub(lambda m: f, src, count=1)
        done.append(it['id'])
    if 'class="sv-d"' in src and '.sv-m{display:none}' not in src:
        src = src.replace('</head>', f'<style>{CSS}</style>\n</head>', 1)
    for it in plan['items']:  # CSS riêng của khối tương tác: vào <head> để wp_publish đưa vào meta _doc_kit_css
        if it.get('css') and it['id'] in done:
            css = open(os.path.join(base, it['css']), encoding='utf-8').read().strip()
            src = re.sub(r'<style data-m="' + re.escape(it['id']) + r'">[\s\S]*?</style>\n?', '', src)
            src = src.replace('</head>', f'<style data-m="{it["id"]}">{css}</style>\n</head>', 1)
    open(out, 'w', encoding='utf-8').write(src)
    print(f'chèn {len(done)}: {", ".join(done)}')
    if wait:
        print(f'CANH_BAO còn khung chờ {len(wait)}: {", ".join(wait)}')
    print(out)


if __name__ == '__main__':
    main()
