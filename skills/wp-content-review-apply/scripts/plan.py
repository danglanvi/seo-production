# Sinh plan ghi WordPress từ kết quả trang duyệt (chế độ trường sống).
# python3 -I plan.py --reviews <thư mục reviews> --report <thư mục report> --out plan.json [--hold hold.json] [--site https://example.com]
# --report: các file tài liệu phần ({"items": [...]}), tên bất kỳ *.json. --reviews: file do ArtifactData list ghi, mỗi file một tài liệu.
# --hold: [{"item": "<id>", "field": "<key>", "why": "..."}] giữ lại không ghi. Mục có ghi chú cũng bị giữ, trừ khi có trong --allow-note.
# Dừng (exit 1) khi một trường có 2 giá trị đã duyệt khác nhau.
# --so: sổ giá trị đã duyệt (so_duyet.py build). Op ghi đè giá trị đã duyệt mới hơn của thẻ khác bị đưa vào holds, không vào ops.
import argparse, glob, json, os, re, sys, unicodedata
from urllib.parse import urlparse

ap = argparse.ArgumentParser()
ap.add_argument('--reviews', required=True)
ap.add_argument('--report', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--hold')
ap.add_argument('--allow-note', default='', help='mã mục có ghi chú nhưng vẫn ghi, cách nhau bằng dấu phẩy')
ap.add_argument('--site', default='')
ap.add_argument('--so', help='sổ giá trị đã duyệt do so_duyet.py build sinh')
a = ap.parse_args()

N = lambda s: unicodedata.normalize('NFC', str(s if s is not None else '')).strip()
DEFAULT = {'seo_title': 'meta:rank_math_title', 'meta': 'meta:rank_math_description', 'h1': 'post_title', 'slug': 'post_name'}
raw_of = lambda f: N(f['raw']) if 'raw' in f else ('' if re.fullmatch(r'\(.*\)', N(f.get('before'))) else N(f.get('before')))

R = {}
for f in glob.glob(os.path.join(a.reviews, '*.json')):
    d = json.load(open(f))
    d = d.get('data', d)
    if d.get('item_id'):
        R[d['item_id']] = d
items = []
for f in sorted(glob.glob(os.path.join(a.report, '*.json'))):
    d = json.load(open(f))
    items += d.get('items', []) if isinstance(d, dict) else []
holds = json.load(open(a.hold)) if a.hold else []
allow = set(x for x in a.allow_note.split(',') if x)

cand, manual, skipped = {}, [], []
for it in items:
    r = R.get(it['id'])
    if not r or r.get('status') not in ('approved', 'edited'):
        continue
    if N(r.get('note')) and it['id'] not in allow:
        holds.append({'item': it['id'], 'field': '*', 'why': 'có ghi chú: ' + N(r['note'])[:160]})
        continue
    vals = r.get('values') or {}
    for fld in it.get('fields', []):
        k = fld['key']
        target = fld.get('target') or DEFAULT.get(k.split('#')[0])  # key#n: trường trùng key trong một thẻ
        opt = r.get('option') or it.get('default_option') or 'A'
        v = vals.get(k, fld.get('proposed', fld.get(opt, fld.get('A'))))
        if v is None or N(v) == N(fld.get('before')) or N(v) == raw_of(fld):
            continue
        if not N(v) and not fld.get('allow_empty'):
            holds.append({'item': it['id'], 'field': k, 'why': 'giá trị duyệt để trống, hỏi lại trước khi xoá giá trị cũ'})
            continue
        if not target:
            manual.append({'item': it['id'], 'field': k, 'value': N(v), 'url': it.get('url', '')})
            continue
        if any(h['item'] == it['id'] and h['field'] in (k, '*') for h in holds):
            continue
        cand.setdefault((it.get('post_id'), target), []).append({'value': N(v), 'item': it['id'], 'field': k, 'before': raw_of(fld), 'url': it.get('url', ''), 'edited': r['status'] == 'edited'})

ops, conflicts = [], []
for (post, target), lst in sorted(cand.items(), key=lambda x: (str(x[0][0]), x[0][1])):
    if len({x['value'] for x in lst}) > 1:
        ed = [x for x in lst if x['edited']]
        if len({x['value'] for x in ed}) == 1:
            lst = ed
        else:
            conflicts.append({'post': post, 'target': target, 'values': lst}); continue
    x = lst[0]
    if not post:
        skipped.append({'item': x['item'], 'why': 'mục không có post_id'}); continue
    op = {'post': post, 'target': target, 'before': x['before'], 'value': x['value'], 'item': x['item'], 'url': x['url']}
    if target == 'post_name':
        old_path = urlparse(x['url']).path if x['url'] else x['before']
        new_slug = x['value'].strip('/').split('/')[-1]
        op['value'] = new_slug
        op['before'] = old_path.strip('/').split('/')[-1]
        new_path = old_path.rstrip('/').rsplit('/', 1)[0] + '/' + new_slug + '/'
        op['redirect'] = {'src': old_path.strip('/'), 'to': (a.site or (f"{urlparse(x['url']).scheme}://{urlparse(x['url']).netloc}" if x['url'] else '')) + new_path, 'code': 301}
    ops.append(op)

so_blocked = []
if a.so:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I không tự thêm thư mục của script
    import so_duyet
    so_blocked, _over = so_duyet.check_ops(json.load(open(a.so, encoding='utf-8')), ops)
    gone = {(b['item'], str(b['post']), b['target']) for b in so_blocked}
    for b in so_blocked:
        holds.append({'item': b['item'], 'field': b['target'], 'why': 'ghi đè giá trị đã duyệt mới hơn của ' + ', '.join(x['item'] for x in b['against'])})
    ops = [o for o in ops if (o['item'], str(o['post']), o['target']) not in gone]
if conflicts:
    print('XUNG ĐỘT, dừng:', json.dumps(conflicts, ensure_ascii=False, indent=1)); sys.exit(1)
plan = {'ops': ops, 'manual': manual, 'holds': holds, 'skipped': skipped}
json.dump(plan, open(a.out, 'w'), ensure_ascii=False, indent=1)
by = {}
for o in ops:
    k = o['target'] if o['target'].startswith('meta:') else o['target'].split(':')[0]
    by[k] = by.get(k, 0) + 1
print('thao tác:', len(ops), json.dumps(by, ensure_ascii=False), '| ghi tay:', len(manual), '| giữ lại:', len(holds), '| bỏ:', len(skipped), '| chặn theo sổ:', len(so_blocked))
