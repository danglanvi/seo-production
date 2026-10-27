#!/usr/bin/env python3
"""tong_hop_php_tai.py (wp-host-optimize): đọc output thô của php_tai.sh, in bảng Markdown quy về /ngày.

Dùng: python3 -I tong_hop_php_tai.py php_tai.txt [--tran 10] [--top 12]
  --tran: trần tiến trình PHP của pool (maxConns). Script đếm số phút có số request PHP bên ngoài đồng thời ≥ trần.
Bảng: tổng theo vhost, theo actor (bên ngoài), theo endpoint (bên ngoài), phút chạm trần, IP và path tốn PHP-giây nhất.
Quy ngày theo cửa sổ ở dòng #RUN. Vhost có per=noD thiếu %D: số PHP là trần trên, PHP-giây không đo được.
"""
import collections, datetime, sys

a = sys.argv[1:]
if not a or a[0].startswith('--'):
    sys.exit(__doc__)
TRAN = int(a[a.index('--tran') + 1]) if '--tran' in a else 10
TOP = int(a[a.index('--top') + 1]) if '--top' in a else 12

NOIBO = {'noi-bo', 'psi-lighthouse', 'preload'}
G = collections.defaultdict(lambda: [0, 0, 0.0])
GA = collections.defaultdict(lambda: [0, 0, 0.0])
GE = collections.defaultdict(lambda: [0, 0, 0.0])
NOD = collections.Counter()
CX = collections.defaultdict(list)
IP = collections.defaultdict(lambda: [0, 0, 0.0, 0])
PT = collections.defaultdict(lambda: [0, 0.0])
gio = None
for line in open(a[0], encoding='utf-8', errors='replace'):
    p = line.rstrip('\n').split('|')
    if p[0] == '#RUN':
        t0, t1 = (datetime.datetime.strptime(x, '%Y-%m-%d %H:%M') for x in p[2:4])
        gio = (t1 - t0).total_seconds() / 3600
    elif p[0] == 'G':
        v, per, _day, act, ep = p[1:6]
        T, PP, PS = int(p[6]), int(p[7]), float(p[8])
        for tgt, k in ((G, v), (GA, (v, act)), (GE, (v, ep, act in NOIBO))):
            tgt[k][0] += T; tgt[k][1] += PP; tgt[k][2] += PS
        if per == 'noD':
            NOD[v] += T
    elif p[0] == 'C':
        CX[p[1]].append(float(p[4]))
    elif p[0] == 'I':
        k = (p[1], p[2], p[3])
        for i, x in enumerate((int(p[4]), int(p[5]), float(p[6]), int(p[7]))):
            IP[k][i] += x
    elif p[0] == 'P':
        k = (p[1], p[4], p[5])
        PT[k][0] += int(p[6]); PT[k][1] += float(p[7])
if not gio:
    sys.exit('không thấy dòng #RUN có cửa sổ đo')
F = 24 / gio


def n(x):
    return f'{x:,.0f}'.replace(',', '.')


print(f'Cửa sổ {gio:.1f} giờ, quy /ngày ×{F:.3f}. Bên ngoài = bỏ nội bộ, PSI/Lighthouse, preload.\n')
print('## Tổng theo vhost\n\n| Vhost | Request/ngày | PHP/ngày | PHP-giây/ngày | Ghi chú |\n|---|---|---|---|---|')
for v, x in sorted(G.items()):
    note = f'{NOD[v] / x[0]:.0%} dòng thiếu %D: số PHP là trần trên' if NOD[v] else ''
    print(f'| {v} | {n(x[0] * F)} | {n(x[1] * F)} | {n(x[2] * F)} | {note} |')
for v in sorted(G):
    rows = [(act, x) for (vv, act), x in GA.items() if vv == v and act not in NOIBO]
    tp, ts = sum(x[1] for _, x in rows), sum(x[2] for _, x in rows)
    print(f'\n## {v}: bên ngoài theo actor (PHP {n(tp * F)}/ngày, PHP-giây {n(ts * F)}/ngày)\n')
    print('| Actor | Request/ngày | PHP/ngày | PHP-giây/ngày | % PHP-giây |\n|---|---|---|---|---|')
    for act, x in sorted(rows, key=lambda t: (-t[1][2], -t[1][1])):
        print(f'| {act} | {n(x[0] * F)} | {n(x[1] * F)} | {n(x[2] * F)} | {x[2] / ts:.0%} |' if ts else f'| {act} | {n(x[0] * F)} | {n(x[1] * F)} | 0 | – |')
    print(f'\n## {v}: bên ngoài theo endpoint\n\n| Endpoint | PHP/ngày | PHP-giây/ngày |\n|---|---|---|')
    eps = [(ep, x) for (vv, ep, nb), x in GE.items() if vv == v and not nb and x[1]]
    for ep, x in sorted(eps, key=lambda t: (-t[1][2], -t[1][1])):
        print(f'| {ep} | {n(x[1] * F)} | {n(x[2] * F)} |')
    c = CX.get(v, [])
    print(f'\nPhút có ≥ {TRAN} request PHP bên ngoài đồng thời: {sum(1 for x in c if x >= TRAN)} / {len(c)} phút có dữ liệu.')
    ips = sorted(((k, x) for k, x in IP.items() if k[0] == v), key=lambda t: -t[1][2])[:TOP]
    if ips:
        print(f'\n## {v}: IP tốn PHP-giây nhất (cả cửa sổ)\n\n| IP | Actor | Request | PHP | PHP-giây | 404 |\n|---|---|---|---|---|---|')
        for (_, ip, act), x in ips:
            print(f'| {ip} | {act} | {x[0]} | {x[1]} | {x[2]:.0f} | {x[3]} |')
    pts = sorted(((k, x) for k, x in PT.items() if k[0] == v), key=lambda t: -t[1][1])[:TOP]
    if pts:
        print(f'\n## {v}: path tốn PHP-giây nhất (bên ngoài, cả cửa sổ)\n\n| Endpoint | Path | PHP | PHP-giây |\n|---|---|---|---|')
        for (_, ep, path), x in pts:
            print(f'| {ep} | `{path}` | {x[0]} | {x[1]:.0f} |')
