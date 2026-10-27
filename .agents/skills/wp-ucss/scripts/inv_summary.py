# inv_summary.py (wp-ucss): tóm tắt inventory và sinh jobs.txt cho gen/verify.
# python3 -I inv_summary.py <inv.jsonl> <jobs.txt>. Chỉ lấy lượt mã 200, đúng 1 file CSS gộp, path cuối không đổi (không redirect).
import collections, json, sys

R = [json.loads(l) for l in open(sys.argv[1])]
last = {}
for r in R:
    last[(r['path'], r['v'])] = r
by_hash = collections.defaultdict(lambda: collections.Counter())
jobs, skip = [], collections.Counter()
for (p, v), r in sorted(last.items()):
    if r.get('code') != 200: skip['mã ' + str(r.get('code'))] += 1; continue
    if r.get('final', p) != p: skip['redirect'] += 1; continue
    css = sorted(set(r['css']))
    if len(css) != 1: skip['số file gộp=%d' % len(css)] += 1; continue
    by_hash[css[0]][v] += 1
    jobs.append(f'{p} {v}')
with open(sys.argv[2], 'w') as f:
    f.write('\n'.join(jobs) + '\n')
print('lượt', len(R), 'cặp path×biến thể', len(last), 'job', len(jobs), 'bỏ', dict(skip))
print('file gộp khác nhau', len(by_hash), '| theo biến thể m/d/g:', {v: len([h for h in by_hash if by_hash[h][v]]) for v in 'mdg'})
for h, c in sorted(by_hash.items(), key=lambda x: -sum(x[1].values()))[:12]:
    print(' ', h[:8], dict(c))
