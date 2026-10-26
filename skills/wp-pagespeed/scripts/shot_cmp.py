# So 2 lượt chụp của shot.mjs: chức năng, lỗi JS mới, ảnh hỏng, tràn ngang, phần trăm điểm ảnh lệch.
# python3 shot_cmp.py <thư mục A> <label A> <thư mục B> <label B> [--thr 40]
# Dòng "!!" là chức năng đổi hoặc có lỗi JS mới. Exit code 1 khi có dòng "!!".
import json, os, sys
from PIL import Image, ImageChops

dA, lA, dB, lB = sys.argv[1:5]
thr = int(sys.argv[sys.argv.index('--thr') + 1]) if '--thr' in sys.argv else 40
A = {(r['name'], r['dev']): r for r in json.load(open(os.path.join(dA, f'results_{lA}.json')))}
B = {(r['name'], r['dev']): r for r in json.load(open(os.path.join(dB, f'results_{lB}.json')))}
FIXED = ['status', 'formsVisible', 'slick', 'owl', 'swiper', 'flickity', 'iconMissing', 'jq']


def pdiff(fa, fb):
    if not (os.path.exists(fa) and os.path.exists(fb)):
        return 'n/a'
    a = Image.open(fa).convert('L'); b = Image.open(fb).convert('L')
    h = min(a.height, b.height); w = min(a.width, b.width)
    d = ImageChops.difference(a.crop((0, 0, w, h)), b.crop((0, 0, w, h))).point(lambda v: 255 if v > thr else 0)
    pct = 100.0 * sum(1 for v in d.getdata() if v) / (w * h)
    bbox = d.getbbox()
    return f'{pct:.1f}%' + ('' if a.height == b.height else ' hΔ') + (f' bbox={bbox}' if bbox and pct > 0.5 else '')


bad = 0
for k, a in A.items():
    b = B.get(k)
    if not b:
        print('!!', k, 'thiếu trong', lB); bad += 1; continue
    if 'status' not in a:
        print('  ', f'{k[0]:22} {k[1]:7} atf={pdiff(os.path.join(dA, f"{k[0]}_{k[1]}_atf.jpg"), os.path.join(dB, f"{k[0]}_{k[1]}_atf.jpg"))}'); continue
    keys = FIXED + sorted(x for x in set(a) | set(b) if x.startswith('vis_'))
    ch = [f'{x}:{a.get(x)}→{b.get(x)}' for x in keys if a.get(x) != b.get(x)]
    if len(b.get('brokenImgs', [])) > len(a.get('brokenImgs', [])):
        ch.append(f'broken {len(a.get("brokenImgs", []))}→{len(b.get("brokenImgs", []))}')
    if (b.get('scrollWidth') or 0) > (b.get('vw') or b.get('innerWidth') or 0) and a.get('scrollWidth') != b.get('scrollWidth'):
        ch.append(f'tràn ngang {a.get("scrollWidth")}→{b.get("scrollWidth")}')
    newerr = sorted(set(b.get('errors', [])) - set(a.get('errors', [])))
    info = f'kb {a.get("kb")}→{b.get("kb")} webp {a.get("webp")}→{b.get("webp")}'
    if abs((a.get('height') or 0) - (b.get('height') or 0)) > 30:
        info += f' h {a.get("height")}→{b.get("height")}'
    fa, fb = set(a.get('fonts', [])), set(b.get('fonts', []))
    if fa != fb:
        info += f' font +{sorted(fb - fa)} -{sorted(fa - fb)}'
    full = pdiff(os.path.join(dA, f'{k[0]}_{k[1]}.jpg'), os.path.join(dB, f'{k[0]}_{k[1]}.jpg'))
    atf = pdiff(os.path.join(dA, f'{k[0]}_{k[1]}_atf.jpg'), os.path.join(dB, f'{k[0]}_{k[1]}_atf.jpg'))
    flag = '!!' if (ch or newerr) else '  '
    bad += bool(ch or newerr)
    print(f'{flag} {k[0]:22} {k[1]:7} full={full:24} atf={atf:24} {info} {" ".join(ch)}' + (f' NEWERR {[e[:90] for e in newerr]}' if newerr else ''))
print('ISSUES', bad)
sys.exit(1 if bad else 0)
