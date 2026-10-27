#!/usr/bin/env python3
"""jev_ucss.py (wp-ucss): gom ảnh lệch của verify.mjs thành input Jev (rubric ucss-diff), rồi đọc kết quả.
Dùng:
  python3 -I jev_ucss.py prep <outDir> [--tag nhãn]   -> <outDir>/jev/<nhãn>/items.jsonl + ảnh ghép (trái gốc | phải gọn)
  python3 -I jev_ucss.py read <outDir> [--tag nhãn] [--th 0.7]   -> bảng cặp cần Claude xem
Lớp tất định trước: cặp ảnh giống hệt pixel (lệch style không hiện ra) không gửi Jev, ghi nhãn "pixel=0".
Chạy Jev (từ root repo): /usr/bin/python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/ucss-diff.json --in <items.jsonl> --out <kq.jsonl> --budget 0.3
"""
import json, os, sys, glob
from PIL import Image, ImageChops

a = sys.argv[1:]
cmd, out = a[0], a[1]
tag = a[a.index('--tag') + 1] if '--tag' in a else 'v1'
th = float(a[a.index('--th') + 1]) if '--th' in a else 0.7
J = f'{out}/jev/{tag}'

if cmd == 'prep':
    os.makedirs(J, exist_ok=True)
    items, same, n = [], [], 0
    for fa in sorted(glob.glob(f'{out}/shots/*_a.png')):
        base = os.path.basename(fa)[:-6]
        A, B = Image.open(fa).convert('RGB'), Image.open(fa[:-6] + '_b.png').convert('RGB')
        n += 1
        bb = ImageChops.difference(A, B).getbbox() if A.size == B.size else (0, 0) + A.size
        if not bb:
            same.append(base); continue
        bar = 12
        im = Image.new('RGB', (A.width + B.width + bar, max(A.height, B.height)), (255, 0, 255))
        im.paste(A, (0, 0)); im.paste(B, (A.width + bar, 0))
        im.save(f'{J}/{base}.png')
        dev, rest = base.split('_', 1)
        items.append({'id': base, 'state': {'description': f'{"phone" if dev == "m" else "desktop"} screenshot region of a page on a WordPress website ({rest})',
                                             'image_path': f'{base}.png'}})
    with open(f'{J}/items.jsonl', 'w') as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + '\n')
    json.dump(same, open(f'{J}/pixel0.json', 'w'))
    print(f'cặp ảnh: {n}; giống hệt pixel: {len(same)}; gửi Jev: {len(items)} -> {J}/items.jsonl')

elif cmd == 'read':
    rows = [json.loads(l) for l in open(f'{J}/kq.jsonl')]
    flag = []
    for r in rows:
        ans = r.get('answers') or {}
        p = (ans.get('visible_change') or {}).get('p_yes')
        ck = (ans.get('change_kind') or {}).get('choice', '').split(':')[0]
        if r.get('route') == 'review' or p is None or p >= th:
            flag.append((r['id'], p, ck, r.get('route')))
    print(f'Jev: {len(rows)} cặp; cần Claude xem (visible_change >= {th} hoặc review): {len(flag)}')
    for x in sorted(flag, key=lambda x: -(x[1] or 1)): print(*x, sep='\t')
