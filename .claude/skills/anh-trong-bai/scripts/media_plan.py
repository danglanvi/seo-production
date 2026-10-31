#!/usr/bin/env python3
"""Lập và kiểm media_plan.json cho media trong thân bài.

  python3 media_plan.py tu-md <bai.md> --out media_plan.json [--brief <07-media-brief/...md>]
  python3 media_plan.py kiem media_plan.json [--html <bai.html>] [--profile <web-profile.json>]
  python3 media_plan.py chu-so-do media_plan.json --out specs-chu.json

tu-md: đọc bảng "## Image placeholders" (cột Ref, Vị trí, Loại, Mô tả, Alt, Filename) của bài humanize. Có --brief thì
lấy thêm Caption, Composition, Source hint từ hộp "Media Brief — IMG-NN". Không ghi đè file đã có.
kiem: mỗi mục có loai hợp lệ, alt, caption khác alt, ten_file kebab; file đã dựng có thật và trong trần KB; ảnh AI không
tả người, văn phòng, khách hàng; một ảnh không lặp hai chỗ. Có --html: mọi khung chờ trong bài có mục trong plan và ngược lại.
chu-so-do: gom chữ của mọi sơ đồ (khối so_do) thành specs cho semantic-media/scripts/diagram_body_check.py.
Mã thoát: 0 đạt, 1 có LOI, 2 sai input. Chỉ dùng Python stdlib.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

LOAI = {'so-do', 'anh-chup', 'anh-ai', 'anh-that', 'tuong-tac', 'video'}
MAP = [(r'interactive|tương tác|calculator|tool', 'tuong-tac'), (r'screenshot|ảnh chụp màn hình|chụp màn hình', 'anh-chup'),
       (r'video', 'video'), (r'photo|ảnh thật|ảnh chụp', 'anh-that'), (r'\bai\b|minh hoạ ai|ảnh ai|illustration', 'anh-ai'),
       (r'diagram|sơ đồ|infographic|chart|biểu đồ|flow|timeline|bảng hình', 'so-do')]
NGUOI = re.compile(r'\b(người|chân dung|đội ngũ|nhân viên|văn phòng|khách hàng|ceo|founder|học viên|portrait|person|people|team|office|customer)\b', re.I)
ALT_BAD = re.compile(r'^\s*(ảnh|hình ảnh|hình|image|picture|photo)\b', re.I)
ALT_KIEU = {'video': re.compile(r'\b(clip|video|ảnh động|gif)\b', re.I), 'anh-chup': re.compile(r'\b(ảnh chụp|chụp màn hình|screenshot)\b', re.I)}


def kebab(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd'))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def classify(t):
    t = t.lower()
    for pat, k in MAP:
        if re.search(pat, t):
            return k
    return 'so-do'


def tu_md(a):
    if os.path.exists(a.out):
        sys.exit(f'{a.out} đã có. Không ghi đè; xoá hoặc đổi tên file rồi chạy lại.')
    src = open(a.md, encoding='utf-8').read()
    m = re.search(r'^## Image placeholders\s*\n([\s\S]*?)(?=\n## |\Z)', src, re.M)
    if not m:
        sys.exit('Bài không có bảng "## Image placeholders". Lập media_plan.json tay theo references/chon-media.md.')
    rows = [r for r in m.group(1).splitlines() if r.strip().startswith('|')][2:]
    items = []
    for r in rows:
        c = [x.strip() for x in r.strip().strip('|').split('|')]
        if len(c) < 6:
            continue
        rid = re.search(r'IMG-\d+[a-z]?', c[0])
        if not rid:
            continue
        fname = re.sub(r'[`"]', '', c[5]).split('(')[0].strip()
        base = os.path.splitext(os.path.basename(fname))[0] if fname else rid.group(0).lower()
        items.append({'id': rid.group(0), 'vi_tri': c[1], 'loai': classify(c[2]), 'loai_goc': c[2], 'mo_ta': c[3],
                      'alt': c[4].strip('"').strip('“”'), 'caption': '', 'ten_file': kebab(base)[:60], 'trang_thai': 'can-dung'})
    if a.brief and os.path.exists(a.brief):
        b = open(a.brief, encoding='utf-8').read()
        for it in items:
            box = re.search(r'Media Brief\s*[—-]\s*' + re.escape(it['id']) + r'\b[^\n]*\n((?:>.*\n?)+)', b)
            if not box:
                continue
            # Bảng của bài humanize mới hơn brief: alt của bảng giữ nguyên, alt của brief chỉ ghi để đối chiếu.
            for key, field in (('Caption', 'caption'), ('Composition', 'bo_cuc'), ('Source hint', 'nguon_goi_y'), ('Alt text', 'alt_brief')):
                f = re.search(r'\*\*' + key + r':\*\*\s*(.+)', box.group(1))
                if f:
                    it[field] = f.group(1).strip().strip('"“”')
    plan = {'bai': os.path.relpath(a.md, os.path.dirname(os.path.abspath(a.out))), 'items': items}
    json.dump(plan, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for it in items:
        print(f'{it["id"]}\t{it["loai"]}\t{it["ten_file"]}\t{it["alt"][:70]}')
    print(f'{len(items)} mục → {a.out}. Viết caption và spec dựng cho từng mục theo references/chon-media.md.')


def kiem(a):
    plan = json.load(open(a.plan, encoding='utf-8'))
    base = os.path.dirname(os.path.abspath(a.plan))
    prof = json.load(open(a.profile, encoding='utf-8')) if a.profile else {}
    caps = {'do-hoa': (prof.get('media') or {}).get('kb_do_hoa', 80), 'anh': (prof.get('media') or {}).get('kb_anh_chup', 140)}
    loi, canh, seen = [], [], {}
    for it in plan.get('items', []):
        i = it.get('id', '?')
        if it.get('loai') not in LOAI:
            loi.append(f'{i}: loai "{it.get("loai")}" không hợp lệ ({", ".join(sorted(LOAI))})')
        alt, cap = (it.get('alt') or '').strip(), (it.get('caption') or '').strip()
        if it.get('loai') != 'tuong-tac':
            if not alt:
                loi.append(f'{i}: thiếu alt')
            elif len(alt) > 140:
                canh.append(f'{i}: alt dài {len(alt)} ký tự (nên dưới 125)')
            if ALT_BAD.match(alt):
                loi.append(f'{i}: alt mở bằng "ảnh/hình". Tả nội dung, không tả loại file')
            for k, pat in ALT_KIEU.items():
                if k != it.get('loai') and pat.search(alt) and not (k == 'anh-chup' and it.get('loai') == 'anh-that'):
                    loi.append(f'{i}: alt nói "{pat.search(alt).group(0)}" nhưng media là {it.get("loai")}. Alt tả media đã dựng, không tả brief cũ')
            if not cap:
                loi.append(f'{i}: thiếu caption (câu người đọc rút ra)')
            elif cap.lower() == alt.lower():
                loi.append(f'{i}: caption trùng alt')
        tf = it.get('ten_file', '')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', tf or ''):
            loi.append(f'{i}: ten_file "{tf}" phải là chữ thường không dấu nối bằng gạch ngang')
        if it.get('loai') == 'anh-ai' and NGUOI.search(' '.join(str(it.get(k, '')) for k in ('mo_ta', 'bo_cuc', 'prompt_tom_tat'))):
            loi.append(f'{i}: ảnh AI tả người, đội ngũ, văn phòng hoặc khách hàng. Dùng ảnh thật hoặc đổi sang hình không người')
        for k in ('svg', 'svg_m', 'src', 'html'):
            if it.get(k):
                p = os.path.normpath(os.path.join(base, it[k]))
                if not os.path.isfile(p):
                    loi.append(f'{i}: không thấy file {it[k]}')
                    continue
                if k == 'src':
                    kb = os.path.getsize(p) / 1024
                    cap_kb = caps['anh'] if it['loai'] in ('anh-chup', 'anh-that', 'anh-ai') else caps['do-hoa']
                    if kb > cap_kb:
                        loi.append(f'{i}: {it[k]} nặng {kb:.0f} KB, trần {cap_kb} KB')
                    if seen.get(p):
                        loi.append(f'{i}: dùng lại ảnh của {seen[p]}. Mỗi chỗ một ảnh, trừ khi ghi allow_reuse kèm lý do')
                    elif not it.get('allow_reuse'):
                        seen[p] = i
        ready = any(it.get(k) for k in ('svg', 'src', 'html', 'youtube'))
        if it.get('trang_thai') == 'xong' and not ready:
            loi.append(f'{i}: trạng thái xong nhưng chưa có file')
        if not ready:
            canh.append(f'{i}: chưa có media ({it.get("trang_thai", "can-dung")})')
    if a.html:
        h = open(a.html, encoding='utf-8').read()
        ids = {it['id'] for it in plan.get('items', [])}
        holes = set(re.findall(r'class="wide cho-media" data-img="(IMG-[\w]+)"', h))
        placed = set(re.findall(r'data-img="(IMG-[\w]+)"', h))
        for x in sorted(holes):
            loi.append(f'{x}: bài còn khung chờ media')
        for x in sorted(placed - ids):
            loi.append(f'{x}: có trong bài nhưng không có trong plan')
        for x in sorted(ids - placed):
            canh.append(f'{x}: có trong plan nhưng bài không có vị trí')
    for x in canh:
        print('CANH_BAO', x)
    for x in loi:
        print('LOI', x)
    print(f'{len(plan.get("items", []))} mục · {len(loi)} lỗi · {len(canh)} cảnh báo')
    sys.exit(1 if loi else 0)


def chu_so_do(a):
    plan = json.load(open(a.plan, encoding='utf-8'))
    skip = {'kieu', 'net', 'to', 'tu', 'den', 'loai'}

    def gom(v, out, key=''):
        if isinstance(v, str) and key not in skip and v.strip():
            out.append(v.strip())
        elif isinstance(v, dict):
            if 'nhan' in v and 'gia_tri' in v:  # thanh của biểu đồ cột: so cả số
                out.append(f'{v["nhan"]} {v["gia_tri"]}')
                return
            for k, x in v.items():
                gom(x, out, k)
        elif isinstance(v, list):
            for x in v:
                gom(x, out, key)
    items = []
    for it in plan.get('items', []):
        if it.get('loai') == 'so-do' and it.get('so_do'):
            chu = []
            gom(it['so_do'], chu)
            items.append({'id': it['id'], 'json_prompt': {'elements': [{'items': chu}]}})
    json.dump({'items': items}, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(items)} sơ đồ → {a.out}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    t = sp.add_parser('tu-md')
    t.add_argument('md')
    t.add_argument('--out', required=True)
    t.add_argument('--brief')
    k = sp.add_parser('kiem')
    k.add_argument('plan')
    k.add_argument('--html')
    k.add_argument('--profile')
    c = sp.add_parser('chu-so-do')
    c.add_argument('plan')
    c.add_argument('--out', required=True)
    a = ap.parse_args()
    {'tu-md': tu_md, 'kiem': kiem, 'chu-so-do': chu_so_do}[a.cmd](a)


if __name__ == '__main__':
    main()
