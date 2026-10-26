# Lập bảng "Phần còn trừ điểm" cho báo cáo nghiệm thu (SKILL.md Bước 5 và 6). Chỉ đọc JSON PSI, không gọi mạng, không ghi file.
#   python3 -I "$WPS/scripts/psi_con_tru.py" <thư mục psi> [<thư mục khác> ...] [--urls urls.tsv] [--thr 0.9] [--diag] [--mt] [--json]
# Nhận file của psi_run.py (<tên>_<thiết bị>_run<N>.json), của psi_ab (<tên>-<biến thể>-r<k>_<thiết bị>_run1.json)
# và file không có hậu tố thiết bị (đọc configSettings.formFactor). Đuôi -r<k> (vòng xen kẽ) được gộp về một template.
# Nhiều thư mục (ví dụ 3 lượt performance và 1 lượt đủ 5 hạng mục) được gộp theo template x thiết bị.
# In 2 bảng markdown:
#   1. Điểm trung vị của 5 hạng mục (performance, accessibility, best-practices, seo, agentic-browsing) mỗi template x thiết bị. "-" là chưa đo.
#   2. Phần còn trừ điểm: audit có trọng số trong hạng mục và điểm trung vị dưới --thr (mặc định 0,9). Cột "Lý do chưa sửa" để trống cho người làm điền.
#      Hạng mục performance chỉ có 5 chỉ số mang trọng số (FCP, LCP, TBT, CLS, Speed Index). --diag thêm audit chẩn đoán (trọng số 0) dưới ngưỡng.
# --mt: thêm bảng chi phí theo nguyên nhân (trung vị): styleLayout ms, scriptEvaluation ms, font KB (số file), tài nguyên chặn hiển thị, TBT ms.
# Dòng cuối luôn là "CON_TRU dong=<n> thieu_hang_muc=<m>": n là số dòng bảng 2, m là số cặp template x thiết bị chưa đo đủ 5 hạng mục.
# Mã thoát: 0 xong, 1 không có file PSI hợp lệ, 2 sai tham số.
import argparse
import glob
import json
import os
import re
import statistics as st
import sys

CATS = ['performance', 'accessibility', 'best-practices', 'seo', 'agentic-browsing']
NAME = re.compile(r'^(?P<name>.+?)(?:_(?P<dev>mobile|desktop))?(?:_run(?P<run>\d+))?\.json$')
ROUND = re.compile(r'-r\d+$')
DIAG_MODES = ('metricSavings', 'binary', 'numeric')

ap = argparse.ArgumentParser(description='Bảng "Phần còn trừ điểm" từ JSON PSI. Mô tả đầy đủ ở đầu file script.')
ap.add_argument('dirs', nargs='+', help='thư mục JSON của psi_run.py hoặc psi_ab')
ap.add_argument('--urls', help='urls.tsv để giữ thứ tự template')
ap.add_argument('--thr', type=float, default=0.9, help='ngưỡng điểm audit (0-1), mặc định 0.9')
ap.add_argument('--diag', action='store_true', help='thêm audit chẩn đoán của performance (trọng số 0)')
ap.add_argument('--mt', action='store_true', help='thêm bảng chi phí theo nguyên nhân')
ap.add_argument('--json', action='store_true', help='in JSON một dòng thay cho bảng markdown')
a = ap.parse_args()
if not 0 < a.thr <= 1:
    ap.error('--thr phải lớn hơn 0 và không quá 1')
for d in a.dirs:
    if not os.path.isdir(d):
        ap.error('không có thư mục %s' % d)
if a.urls and not os.path.isfile(a.urls):
    ap.error('không có file %s' % a.urls)

runs, skipped = {}, 0
for d in a.dirs:
    for f in sorted(glob.glob(os.path.join(d, '*.json'))):
        m = NAME.match(os.path.basename(f))
        if not m:
            continue
        try:
            with open(f, encoding='utf-8') as fh:
                j = json.load(fh)
        except (OSError, ValueError):
            skipped += 1
            continue
        lr = j.get('lighthouseResult') if isinstance(j, dict) else None
        if not isinstance(lr, dict) or not isinstance(lr.get('categories'), dict) or not lr['categories']:
            skipped += 1
            continue
        dev = m.group('dev') or (lr.get('configSettings') or {}).get('formFactor') or '?'
        runs.setdefault((ROUND.sub('', m.group('name')), dev), []).append(lr)

if not runs:
    print('Lỗi: không có file PSI hợp lệ trong %s (bỏ qua %d file hỏng hoặc không phải PSI)' % (', '.join(a.dirs), skipped), file=sys.stderr)
    print('CON_TRU dong=0 thieu_hang_muc=0')
    sys.exit(1)

order = []
if a.urls:
    with open(a.urls, encoding='utf-8') as fh:
        order = [l.split('\t')[0].strip() for l in fh if l.strip() and not l.startswith('#')]
rank = {n: i for i, n in enumerate(order)}
keys = sorted(runs, key=lambda k: (rank.get(k[0], len(rank)), k[0], 0 if k[1] == 'mobile' else 1))

pct = lambda x: '-' if x is None else str(int(round(x * 100)))
dec = lambda x, n=2: ('{:.%df}' % n).format(x).replace('.', ',')
cell = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')


def median_or_none(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


cat_rows, rows, missing = [], [], []
for k in keys:
    lrs = runs[k]
    scores = {c: median_or_none([(lr['categories'].get(c) or {}).get('score') for lr in lrs]) for c in CATS}
    have = [c for c in CATS if any(c in lr['categories'] for lr in lrs)]
    if len(have) < len(CATS):
        missing.append({'template': k[0], 'dev': k[1], 'thieu': [c for c in CATS if c not in have]})
    cat_rows.append({'template': k[0], 'dev': k[1], 'luot': len(lrs), 'diem': {c: scores[c] for c in CATS}})
    for c in CATS + sorted({c for lr in lrs for c in lr['categories']} - set(CATS)):
        per = {}
        for lr in lrs:
            cat = lr['categories'].get(c)
            if not cat:
                continue
            au = lr.get('audits') or {}
            for ref in cat.get('auditRefs') or []:
                aid, w = ref.get('id'), ref.get('weight') or 0
                x = au.get(aid) or {}
                if x.get('score') is None or ref.get('group') == 'hidden':
                    continue
                if w <= 0 and not (a.diag and c == 'performance' and x.get('scoreDisplayMode') in DIAG_MODES):
                    continue
                p = per.setdefault(aid, {'w': w, 'title': x.get('title') or aid, 'vals': []})
                p['vals'].append((x['score'], x.get('displayValue') or ''))
        for aid, p in per.items():
            ss = sorted(p['vals'], key=lambda v: v[0])
            med = st.median([v[0] for v in ss])
            if med >= a.thr:
                continue
            rows.append({'template': k[0], 'dev': k[1], 'hang_muc': c, 'diem_hang_muc': scores.get(c, median_or_none(
                [(lr['categories'].get(c) or {}).get('score') for lr in lrs])), 'audit': aid, 'tieu_de': p['title'],
                'trong_so': p['w'], 'diem': med, 'duoi_nguong': sum(1 for v in ss if v[0] < a.thr), 'luot': len(ss),
                'gia_tri': ss[len(ss) // 2][1]})
rows.sort(key=lambda r: (keys.index((r['template'], r['dev'])), CATS.index(r['hang_muc']) if r['hang_muc'] in CATS else 99, -r['trong_so'], r['diem']))

mt_rows = []
if a.mt:
    for k in keys:
        vals = []
        for lr in runs[k]:
            au = lr.get('audits') or {}
            if 'performance' not in lr['categories'] or 'mainthread-work-breakdown' not in au:
                continue
            br = {i.get('group'): i.get('duration', 0) for i in ((au['mainthread-work-breakdown'].get('details') or {}).get('items') or [])}
            reqs = (au.get('network-requests', {}).get('details') or {}).get('items') or []
            fonts = [i for i in reqs if i.get('resourceType') == 'Font']
            rb = au.get('render-blocking-insight') or au.get('render-blocking-resources') or {}
            vals.append((br.get('styleLayout', 0), br.get('scriptEvaluation', 0), sum(i.get('transferSize', 0) for i in fonts) / 1024, len(fonts),
                         len((rb.get('details') or {}).get('items') or []), (au.get('total-blocking-time') or {}).get('numericValue') or 0))
        if vals:
            med = [st.median(c) for c in zip(*vals)]
            mt_rows.append({'template': k[0], 'dev': k[1], 'luot': len(vals), 'style_layout_ms': round(med[0]), 'script_ms': round(med[1]),
                            'font_kb': round(med[2]), 'font_file': med[3], 'chan_hien_thi': med[4], 'tbt_ms': round(med[5])})

summary = 'CON_TRU dong=%d thieu_hang_muc=%d' % (len(rows), len(missing))
if a.json:
    print(json.dumps({'nguong': a.thr, 'hang_muc': cat_rows, 'con_tru': rows, 'thieu': missing, 'mt': mt_rows, 'bo_qua': skipped}, ensure_ascii=False))
    print(summary)
    sys.exit(0)

print('## Điểm trung vị theo hạng mục\n')
print('| Template | Thiết bị | Lượt | ' + ' | '.join(CATS) + ' |')
print('|---|---|---|' + '---|' * len(CATS))
for r in cat_rows:
    print('| %s | %s | %d | %s |' % (cell(r['template']), r['dev'], r['luot'], ' | '.join(pct(r['diem'][c]) for c in CATS)))
print('\n## Phần còn trừ điểm (audit dưới %s)\n' % dec(a.thr))
if rows:
    print('| Template | Thiết bị | Hạng mục (điểm) | Audit | Trọng số | Điểm audit | Lượt dưới ngưỡng | Giá trị | Lý do chưa sửa |')
    print('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        print('| %s | %s | %s (%s) | `%s` %s | %s | %s | %d/%d | %s |  |' % (
            cell(r['template']), r['dev'], r['hang_muc'], pct(r['diem_hang_muc']), r['audit'], cell(r['tieu_de']),
            ('%g' % r['trong_so']).replace('.', ','), dec(r['diem']), r['duoi_nguong'], r['luot'], cell(r['gia_tri'])))
else:
    print('Không có audit nào dưới ngưỡng.')
if missing:
    print('\nCHƯA ĐO ĐỦ 5 HẠNG MỤC:')
    for x in missing:
        print('- %s %s: thiếu %s' % (x['template'], x['dev'], ', '.join(x['thieu'])))
if a.mt:
    print('\n## Chi phí theo nguyên nhân (trung vị)\n')
    print('| Template | Thiết bị | Lượt | styleLayout ms | script ms | Font KB (file) | Chặn hiển thị | TBT ms |')
    print('|---|---|---|---|---|---|---|---|')
    for r in mt_rows:
        print('| %s | %s | %d | %d | %d | %d (%g) | %g | %d |' % (cell(r['template']), r['dev'], r['luot'], r['style_layout_ms'], r['script_ms'],
                                                           r['font_kb'], r['font_file'], r['chan_hien_thi'], r['tbt_ms']))
if skipped:
    print('\nBỏ qua %d file hỏng hoặc không phải PSI.' % skipped)
print(summary)
