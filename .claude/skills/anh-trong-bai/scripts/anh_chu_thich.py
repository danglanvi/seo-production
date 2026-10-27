#!/usr/bin/env python3
"""Xử lý ảnh chụp, ảnh thật hoặc ảnh AI trước khi chèn bài: ghép, cắt, che, khoanh, ghim số, logo, WebP có metadata.

  python3 anh_chu_thich.py <ảnh 1> [<ảnh 2> ...] --out <file.webp> --profile <web-profile.json>
          [--spec chu_thich.json] [--alt "…"] [--title "…"] [--nguon chup-man-hinh|anh-that|ai] [--logo] [--kb 140]

- Nhiều ảnh: ghép dọc, cách nhau dải xám 16 px. --le N thêm lề trắng N px quanh từng ảnh (ảnh chụp trang: 24).
- spec (toạ độ px của ảnh đã ghép): {"cat": [x, y, w, h], "che": [[x, y, w, h]], "khung": [[x, y, w, h]], "ghim": [[x, y, số]]}.
  "che" phủ khối màu đặc (tên khách, domain, email, số điện thoại). Không làm mờ: chữ mờ vẫn đọc lại được.
- Thu về bề rộng media.rong_anh của profile (mặc định 1200), WebP dưới trần KB (ảnh chụp: kb_anh_chup, ảnh AI: kb_anh_chup).
- --logo: ghép logo media.logo của profile góc dưới phải, rộng 9%, mờ 0,55 (luật cho ảnh AI).
- Metadata XMP: tiêu đề, alt, tác giả, IPTC DigitalSourceType theo --nguon.
Cần Pillow.
"""
import argparse
import html
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

DST = 'http://cv.iptc.org/newscodes/digitalsourcetype/'
NGUON = {'chup-man-hinh': 'screenCapture', 'anh-that': 'digitalCapture', 'ai': 'compositeWithTrainedAlgorithmicMedia'}
FONTS = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']


def font(sz):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def ghep(paths, le=0):
    ims = [Image.open(p).convert('RGB') for p in paths]
    if le:
        ims = [ImageOps.expand(i, border=le, fill='white') for i in ims]
    if len(ims) == 1:
        return ims[0]
    W = max(i.width for i in ims)
    H = sum(i.height for i in ims) + 16 * (len(ims) - 1)
    out = Image.new('RGB', (W, H), '#E2E8F0')
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height + 16
    return out


def ve(im, spec, mau):
    d = ImageDraw.Draw(im)
    for x, y, w, h in spec.get('che', []):
        d.rectangle([x, y, x + w, y + h], fill='#1E293B')
    for x, y, w, h in spec.get('khung', []):
        for k in range(4):
            d.rounded_rectangle([x - k, y - k, x + w + k, y + h + k], radius=10, outline=mau)
    r = max(16, im.width // 60)
    f = font(int(r * 1.2))
    for x, y, n in spec.get('ghim', []):
        d.ellipse([x - r, y - r, x + r, y + r], fill=mau, outline='white', width=3)
        d.text((x, y), str(n), fill='white', font=f, anchor='mm')
    if spec.get('cat'):
        x, y, w, h = spec['cat']
        im = im.crop((x, y, x + w, y + h))
    return im


def logo(im, path):
    lg = Image.open(path).convert('RGBA')
    w = max(60, int(im.width * 0.09))
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    a = lg.split()[3].point(lambda v: int(v * 0.55))
    lg.putalpha(a)
    base = im.convert('RGBA')
    m = int(im.width * 0.025)
    base.alpha_composite(lg, (im.width - w - m, im.height - lg.height - m))
    return base.convert('RGB')


def xmp(title, alt, who, nguon):
    e = html.escape
    return (f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
            f'<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/">'
            f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{e(title)}</rdf:li></rdf:Alt></dc:title>'
            f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{e(alt)}</rdf:li></rdf:Alt></dc:description>'
            f'<dc:creator><rdf:Seq><rdf:li>{e(who)}</rdf:li></rdf:Seq></dc:creator>'
            f'<Iptc4xmpExt:DigitalSourceType>{DST}{NGUON[nguon]}</Iptc4xmpExt:DigitalSourceType>'
            f'</rdf:Description></rdf:RDF></x:xmpmeta>').encode()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('anh', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--spec')
    ap.add_argument('--alt', default='')
    ap.add_argument('--title', default='')
    ap.add_argument('--nguon', choices=list(NGUON), default='chup-man-hinh')
    ap.add_argument('--logo', action='store_true')
    ap.add_argument('--kb', type=int)
    ap.add_argument('--le', type=int, default=0, help='lề trắng px quanh từng ảnh trước khi ghép (ảnh chụp trang: 24)')
    a = ap.parse_args()
    prof = json.load(open(a.profile, encoding='utf-8'))
    m = prof.get('media') or {}
    mau = (m.get('mau') or {}).get('chinh', '#2563EB')
    im = ghep(a.anh, a.le)
    if a.spec:
        im = ve(im, json.load(open(a.spec, encoding='utf-8')), mau)
    W = int(m.get('rong_anh', 1200))
    if im.width > W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    if a.logo or a.nguon == 'ai':
        lp = m.get('logo')
        if not lp:
            sys.exit('Ảnh AI cần logo watermark: khai media.logo trong profile.')
        im = logo(im, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(a.profile)), lp)))
    cap = a.kb or int(m.get('kb_anh_chup', 140))
    md = xmp(a.title or a.alt, a.alt, prof.get('brand', ''), a.nguon)
    for q in range(86, 40, -4):
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=q, method=6, xmp=md)
        if buf.tell() <= cap * 1024:
            break
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'wb').write(buf.getvalue())
    kb = buf.tell() / 1024
    flag = '' if kb <= cap else f' VUOT_TRAN {cap} KB'
    print(f'{a.out}\t{im.width}x{im.height}\t{kb:.0f} KB\tq{q}{flag}')
    sys.exit(1 if flag else 0)


if __name__ == '__main__':
    main()
