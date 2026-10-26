#!/usr/bin/env python3
"""Sổ giá trị đã duyệt: chặn op ghi đè trường đang mang giá trị đã duyệt mới hơn.

python3 -I so_duyet.py build --report <thư mục report> --reviews <thư mục reviews> --out so-duyet.json [--cu so-cu.json] [--force]
python3 -I so_duyet.py check --so so-duyet.json --plan plan.json [--out ket-qua.json]
python3 -I so_duyet.py the --so so-duyet.json --report <thư mục thẻ mới> [--json]

build: đọc mọi thẻ approved, edited, applied và ghi sổ. Khoá sổ là "<post>|<target>", giá trị là danh sách
       {item, field, value, status, time, applied}. Cách tính post, target, giá trị cuối giống plan.py.
       Trường không có target (khối chữ) vào sổ với khoá "<post>|~<key>". check không dùng các khoá này.
       Trường giữ nguyên (giá trị bằng before) không vào sổ. --cu gộp sổ cũ: mục của cùng item và field được thay bằng mục mới.
the:   chạy trước khi nạp thẻ mới. Trường của thẻ mới có before (hoặc raw) bằng một giá trị đã duyệt của cùng post
       mà lại đề xuất chữ khác là "đổi chữ đã duyệt": báo lỗi. Trường có "doi_chu_duyet": "<lý do>" (ví dụ vượt pixel)
       chỉ được liệt kê. Thẻ đã có trong sổ bị bỏ qua. Thoát mã 1 khi có lỗi.
check: so từng op của plan (plan.py sinh, hoặc ops.json có post, target, value, item) với sổ.
       Op ghi đè một giá trị khác của thẻ khác bị CHẶN khi thẻ kia được duyệt sau thẻ của op,
       hoặc khi thẻ của op không có trong sổ (op không đi qua trang duyệt).
       Op ngoài sổ có giá trị bằng thẻ duyệt mới nhất của trường thì qua, vì không đổi gì so với lần duyệt cuối.
       Op mới hơn sổ vẫn qua, nhưng được liệt kê ở "ghi_de_cu" để người ghi biết.
       Op engine dạng fix: dùng field làm target, new làm giá trị. Op text (thay một câu) không so được, bỏ qua.
Thoát mã 0 khi không op nào bị chặn, 1 khi có op bị chặn, 2 khi sai đầu vào hoặc file ra đã có.
plan.py --so gọi cùng hàm check_ops này.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

DEFAULT = {'seo_title': 'meta:rank_math_title', 'meta': 'meta:rank_math_description', 'h1': 'post_title', 'slug': 'post_name'}
APPROVED = ('approved', 'edited', 'applied')


def N(s):
    return unicodedata.normalize('NFC', str(s if s is not None else '')).replace(' ', ' ').strip()


def NS(s):
    return re.sub(r'\s+', ' ', N(s))


def base_key(k):
    return str(k or '').split('#')[0]


def parse_time(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except ValueError:
        return None


def _load_dir(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, '*.json'))):
        with open(f, encoding='utf-8') as fh:
            j = json.load(fh)
        out.append((os.path.splitext(os.path.basename(f))[0], j.get('data', j) if isinstance(j, dict) else j))
    return out


def fid_keys(fields):
    seen, out = {}, []
    for f in fields:
        k = f.get('key')
        seen[k] = seen.get(k, 0) + 1
        out.append(k if seen[k] == 1 else '%s#%d' % (k, seen[k]))
    return out


def build_ledger(report_dir, reviews_dir, old=None):
    reviews = {}
    for stem, d in _load_dir(reviews_dir):
        if isinstance(d, dict):
            reviews[d.get('item_id') or stem] = d
    entries = {}
    n_items = 0
    for _, doc in _load_dir(report_dir):
        for it in (doc.get('items') or []) if isinstance(doc, dict) else []:
            r = reviews.get(it.get('id'))
            if not r or r.get('status') not in APPROVED or not it.get('post_id'):
                continue
            n_items += 1
            vals = r.get('values') or {}
            opt = r.get('option') or it.get('default_option') or 'A'
            fields = it.get('fields') or []
            for fl, k in zip(fields, fid_keys(fields)):
                target = fl.get('target') or DEFAULT.get(base_key(k)) or '~' + k
                v = vals.get(k, fl.get('proposed', fl.get(opt, fl.get('A'))))
                raw = N(fl['raw']) if 'raw' in fl else N(fl.get('before'))
                if v is None or N(v) == N(fl.get('before')) or N(v) == raw:
                    continue
                entries.setdefault('%s|%s' % (it['post_id'], target), []).append({
                    'item': it['id'], 'field': k, 'value': N(v), 'status': r['status'],
                    'time': r.get('updatedAt') or '', 'applied': bool(r.get('appliedAt')) or r['status'] == 'applied'})
    if old:
        for key, lst in (old.get('entries') or {}).items():
            have = {(e['item'], e['field']) for e in entries.get(key, [])}
            for e in lst:
                if (e['item'], e['field']) not in have:
                    entries.setdefault(key, []).append(e)
    return {'version': 1, 'built': datetime.datetime.now().isoformat(timespec='seconds'), 'items': n_items, 'entries': entries}


def op_key(op):
    """(khoá sổ, giá trị) của op, hoặc None khi op không so được (text, redirect, content...)."""
    t = op.get('target')
    if t in ('text', 'el_rm', 'el_restore', 'redirect', 'content'):
        return None
    if t == 'fix':
        return '%s|%s' % (op.get('post', ''), op.get('field')), op.get('new')
    if 'value' not in op or op.get('post') in (None, ''):
        return None
    return '%s|%s' % (op['post'], t), op['value']


def check_ops(ledger, ops):
    """Trả (blocked, overrides). blocked: op bị chặn kèm lý do. overrides: op mới hơn, ghi đè giá trị đã duyệt cũ."""
    ents = ledger.get('entries') or {}
    blocked, overrides = [], []
    for op in ops:
        kv = op_key(op)
        if not kv:
            continue
        key, val = kv
        item = op.get('item')
        allv = ents.get(key, [])
        mine = [e for e in allv if e['item'] == item]
        times = [(parse_time(e['time']), e) for e in allv]
        if not mine and times and all(t for t, _ in times):
            # Op ngoài sổ có giá trị bằng thẻ duyệt mới nhất của trường: không đổi gì so với lần duyệt cuối.
            if NS(max(times, key=lambda x: x[0])[1]['value']) == NS(val):
                continue
        others = [e for e in ents.get(key, []) if e['item'] != item and NS(e['value']) != NS(val)]
        if not others:
            continue
        t_mine = parse_time(mine[0]['time']) if mine else None
        newer = []
        for e in others:
            te = parse_time(e['time'])
            # Thiếu giờ ở một bên thì coi là chưa chứng minh được op mới hơn: chặn.
            if t_mine is None or te is None or te >= t_mine:
                newer.append(e)
        rec = {'item': item, 'post': op.get('post'), 'target': op.get('target') if op.get('target') != 'fix' else op.get('field'),
               'value': N(val)[:160], 'against': [{'item': e['item'], 'value': e['value'][:160], 'time': e['time'], 'status': e['status'], 'applied': e['applied']} for e in (newer or others)]}
        if newer:
            rec['why'] = ('thẻ %s không có trong sổ duyệt' % item) if not mine else 'thẻ khác duyệt sau hoặc không rõ giờ'
            blocked.append(rec)
        else:
            overrides.append(rec)
    return blocked, overrides


def check_new_cards(ledger, docs):
    """Trả (loi, cho_phep): trường của thẻ mới đổi chữ đang là giá trị đã duyệt của cùng post."""
    ents = ledger.get('entries') or {}
    known = {e['item'] for lst in ents.values() for e in lst}
    by_post = {}
    for key, lst in ents.items():
        by_post.setdefault(key.split('|', 1)[0], []).extend(lst)
    loi, cho_phep = [], []
    for doc in docs:
        for it in (doc.get('items') or []) if isinstance(doc, dict) else []:
            if it.get('id') in known or not it.get('post_id'):
                continue
            fields = it.get('fields') or []
            for fl, k in zip(fields, fid_keys(fields)):
                before = NS(fl['raw'] if 'raw' in fl else fl.get('before'))
                if not before:
                    continue
                props = {NS(fl[x]) for x in ('proposed', 'A', 'B') if fl.get(x) is not None} - {before, NS(fl.get('before'))}
                hit = [e for e in by_post.get(str(it['post_id']), []) if NS(e['value']) == before]
                if not props or not hit:
                    continue
                rec = {'item': it['id'], 'field': k, 'post': it['post_id'], 'before': before[:160],
                       'duyet_boi': sorted({e['item'] for e in hit})}
                if fl.get('doi_chu_duyet'):
                    rec['ly_do'] = fl['doi_chu_duyet']
                    cho_phep.append(rec)
                else:
                    loi.append(rec)
    return loi, cho_phep


def cmd_the(a):
    if not os.path.exists(a.so) or not os.path.isdir(a.report):
        print('Thiếu sổ hoặc thư mục thẻ', file=sys.stderr)
        return 2
    with open(a.so, encoding='utf-8') as fh:
        led = json.load(fh)
    docs = [d for stem, d in _load_dir(a.report) if stem != 'summary']
    loi, cho_phep = check_new_cards(led, docs)
    if a.json:
        print(json.dumps({'loi': loi, 'cho_phep': cho_phep}, ensure_ascii=False, indent=1))
    else:
        print('Đổi chữ đã duyệt: %d lỗi | %d có lý do' % (len(loi), len(cho_phep)))
        for r in loi:
            print('LỖI %s %s (post %s): chữ hiện tại là chữ đã duyệt ở %s' % (r['item'], r['field'], r['post'], ', '.join(r['duyet_boi'])))
        for r in cho_phep:
            print('CÓ LÝ DO %s %s: %s' % (r['item'], r['field'], r['ly_do']))
    return 1 if loi else 0


def cmd_build(a):
    for d in (a.report, a.reviews):
        if not os.path.isdir(d):
            print('Không có thư mục ' + d, file=sys.stderr)
            return 2
    if os.path.exists(a.out) and not a.force:
        print('File ra đã có, thêm --force để ghi đè: ' + a.out, file=sys.stderr)
        return 2
    old = None
    if a.cu:
        if not os.path.exists(a.cu):
            print('Không có sổ cũ ' + a.cu, file=sys.stderr)
            return 2
        with open(a.cu, encoding='utf-8') as fh:
            old = json.load(fh)
    led = build_ledger(a.report, a.reviews, old)
    with open(a.out, 'w', encoding='utf-8') as fh:
        json.dump(led, fh, ensure_ascii=False, indent=1)
    print('Sổ: %d thẻ đã duyệt, %d trường (post|target)' % (led['items'], len(led['entries'])))
    return 0


def cmd_check(a):
    for f in (a.so, a.plan):
        if not os.path.exists(f):
            print('Không có file ' + f, file=sys.stderr)
            return 2
    if a.out and os.path.exists(a.out):
        print('File ra đã có: ' + a.out, file=sys.stderr)
        return 2
    with open(a.so, encoding='utf-8') as fh:
        led = json.load(fh)
    with open(a.plan, encoding='utf-8') as fh:
        plan = json.load(fh)
    ops = plan.get('ops', plan) if isinstance(plan, dict) else plan
    blocked, overrides = check_ops(led, ops)
    res = {'ops': len(ops), 'blocked': blocked, 'ghi_de_cu': overrides}
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
    print('Op: %d | chặn: %d | ghi đè giá trị duyệt cũ hơn: %d' % (len(ops), len(blocked), len(overrides)))
    for b in blocked:
        print('CHẶN %s post %s %s: %s (đang mang giá trị của %s)' % (b['item'], b['post'], b['target'], b['why'], ', '.join(x['item'] for x in b['against'])))
    return 1 if blocked else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Sổ giá trị đã duyệt. Xem docstring đầu file.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build', help='dựng sổ từ report và reviews')
    b.add_argument('--report', required=True)
    b.add_argument('--reviews', required=True)
    b.add_argument('--out', required=True)
    b.add_argument('--cu', help='sổ cũ để gộp')
    b.add_argument('--force', action='store_true')
    c = sub.add_parser('check', help='so plan với sổ')
    c.add_argument('--so', required=True)
    c.add_argument('--plan', required=True)
    c.add_argument('--out')
    t = sub.add_parser('the', help='kiểm thẻ mới không đổi chữ đã duyệt')
    t.add_argument('--so', required=True)
    t.add_argument('--report', required=True)
    t.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    return {'build': cmd_build, 'check': cmd_check, 'the': cmd_the}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
