#!/usr/bin/env python3
"""chon_url.py (wp-ucss): chọn URL đại diện để sinh, kiểm và đo UCSS, thay cho quét toàn site (bài học site WordPress OLS + LiteSpeed Cache, 26/10/2026).
Dùng: python3 -I chon_url.py <ds.json> <gsc.json> <inv.jsonl> <out.tsv> [--cfg chon.json]
- ds.json: WP-CLI eval-file ds.php (path, post_type, danh mục, template). gsc.json: tools/gsc/gsc.sh query <site> 90 page.
- inv.jsonl: inventory.py (md5 file CSS gộp theo path, biến thể m).
Luật chọn (cfg, mẫu templates/chon.example.json):
1. Template: mỗi file CSS gộp lấy 1 URL nhiều click nhất, nếu nhóm đó có click >= min_clicks hoặc hiển thị >= min_impr, hoặc URL nằm trong must.
2. Bài chuyên mục ưu tiên (priority_cats): lấy hết.
3. Bài core (core_cats) top_core theo click; bài outer (còn lại) top_outer theo click.
4. Bài có vị trí trung bình <= max_pos: thêm top_impr theo hiển thị.
5. extra_per_hash: nhóm file gộp nhiều trang (vd. customer stories) lấy thêm N URL.
Ra TSV: path, nhóm, lý do, hash, click, hiển thị, vị trí.
"""
import json, sys, collections

a = sys.argv[1:]
cfg = {}
if '--cfg' in a:
    i = a.index('--cfg'); cfg = json.load(open(a[i + 1])); del a[i:i + 2]
ds, gsc, invf, out = a
C = dict(min_clicks=5, min_impr=500, must=[], priority_cats=[], core_cats=[], top_core=14, top_outer=7,
         top_impr=5, max_pos=15, extra_per_hash={}, skip=[])
C.update(cfg)

d = json.load(open(ds))
meta = {r[0]: r for r in d['rows']}
g = {}
for r in json.load(open(gsc)).get('rows', []):
    u = r['keys'][0]
    p = '/' + u.split('://', 1)[-1].split('/', 1)[-1] if '://' in u else u
    g[p] = r
H = {}
for l in open(invf):
    r = json.loads(l)
    if r['v'] == 'm' and r.get('code') == 200 and len(set(r['css'])) == 1 and r.get('final', r['path']) == r['path']:
        H[r['path']] = r['css'][0]
clk = lambda p: g.get(p, {}).get('clicks', 0)
imp = lambda p: g.get(p, {}).get('impressions', 0)
pos = lambda p: g.get(p, {}).get('position', 99)
cats = lambda p: (meta[p][2].split('|') if p in meta and meta[p][2] else [p.strip('/').split('/')[0]] if p.count('/') > 2 else [])
is_post = lambda p: (p in meta and meta[p][1] == 'post') or (p not in meta and p.count('/') > 2)

chon = collections.OrderedDict()
def add(p, nhom, ly_do):
    if p in H and p not in chon and p not in C['skip']:
        chon[p] = (nhom, ly_do)

for p in C['must']:
    add(p, 'template', 'must')
groups = collections.defaultdict(list)
for p, h in H.items():
    groups[h].append(p)
for h, ps in sorted(groups.items(), key=lambda x: -sum(clk(p) for p in x[1])):
    tot_c, tot_i = sum(clk(p) for p in ps), sum(imp(p) for p in ps)
    top = sorted(ps, key=lambda p: (-clk(p), -imp(p), p))
    if tot_c >= C['min_clicks'] or tot_i >= C['min_impr']:
        add(top[0], 'template', f'top của file gộp ({len(ps)} trang)')
    for p in top[1:1 + int(C['extra_per_hash'].get(h[:8], 0))]:
        add(p, 'template', 'thêm của file gộp nhiều trang')
posts = [p for p in H if is_post(p)]
for p in sorted(posts, key=lambda p: -clk(p)):
    if set(cats(p)) & set(C['priority_cats']):
        add(p, 'uu-tien', 'chuyên mục ưu tiên ' + ','.join(sorted(set(cats(p)) & set(C['priority_cats']))))
core = [p for p in posts if set(cats(p)) & set(C['core_cats'])]
outer = [p for p in posts if p not in core and not set(cats(p)) & set(C['priority_cats'])]
for p in sorted(core, key=lambda p: -clk(p))[:C['top_core']]:
    add(p, 'core', 'top click core')
for p in sorted(outer, key=lambda p: -clk(p))[:C['top_outer']]:
    add(p, 'outer', 'top click outer')
for p in sorted([p for p in posts if pos(p) <= C['max_pos']], key=lambda p: -imp(p))[:C['top_impr']]:
    add(p, 'core' if p in core else 'outer', f'top hiển thị, vị trí <= {C["max_pos"]}')

with open(out, 'w') as f:
    f.write('path\tnhom\tly_do\thash\tclick90\thien_thi90\tvi_tri\n')
    for p, (n, l) in chon.items():
        f.write(f'{p}\t{n}\t{l}\t{H[p][:8]}\t{clk(p)}\t{imp(p)}\t{pos(p):.1f}\n')
c = collections.Counter(n for n, _ in chon.values())
print(f'chọn {len(chon)} URL: ' + ', '.join(f'{k}={v}' for k, v in c.items()) + f'; file gộp phủ: {len({H[p] for p in chon})}/{len(groups)}')
