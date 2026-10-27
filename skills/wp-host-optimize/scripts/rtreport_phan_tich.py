#!/usr/bin/env python3
"""rtreport_phan_tich.py (wp-host-optimize): đọc file của rtreport_mau.sh, in bảng theo pool PHP.

Dùng: python3 -I rtreport_phan_tich.py <file.log> [--ngay YYYY-MM-DD] [--tz 7] [--giay 10]
Mỗi pool: số mẫu có dòng, trần (CMAXCONN), INUSE lớn nhất, số giây có hàng chờ, hàng chờ lớn nhất.
Giây có hàng chờ = số mẫu có ít nhất một worker báo WAITQUE_DEPTH > 0, nhân khoảng lấy mẫu.
Script in các khoảng mất mẫu dài hơn 3 lần khoảng lấy mẫu. Chỉ dùng số giây hàng chờ khi độ phủ đủ cho cửa sổ cần so.
"""
import collections, datetime, re, sys

a = sys.argv[1:]
if not a or a[0].startswith('--'):
    sys.exit(__doc__)
arg = lambda k, d: a[a.index(k) + 1] if k in a else d
DAY, GIAY = arg('--ngay', None), int(arg('--giay', 10))
TZ = datetime.timezone(datetime.timedelta(hours=float(arg('--tz', 7))))
RX = re.compile(r'EXTAPP \[LSAPI\] \[([^\]]+)\].*?CMAXCONN: (\d+).*?INUSE_CONN: (\d+).*?WAITQUE_DEPTH: (\d+)')
fmt = lambda t: datetime.datetime.fromtimestamp(t, TZ).strftime('%d/%m %H:%M:%S')

pool = collections.defaultdict(lambda: {'mau': set(), 'tran': 0, 'inuse': 0, 'cho': set(), 'cho_max': 0})
blocked = collections.Counter()
ts, keep, mau, gaps, last, drops = None, False, [], [], None, 0
for line in open(a[0], encoding='utf-8', errors='replace'):
    line = line.strip()
    if line.startswith('# mat-ket-noi'):
        drops += 1
        continue
    if re.fullmatch(r'\d{10}', line):
        ts = int(line)
        keep = DAY is None or datetime.datetime.fromtimestamp(ts, TZ).strftime('%Y-%m-%d') == DAY
        if keep:
            if last is not None and ts - last > 3 * GIAY:
                gaps.append((last, ts))
            last = ts
            mau.append(ts)
        continue
    if not keep or ts is None:
        continue
    m = RX.search(line)
    if m:
        p = pool[m.group(1)]
        p['mau'].add(ts)
        p['tran'] = max(p['tran'], int(m.group(2)))
        p['inuse'] = max(p['inuse'], int(m.group(3)))
        w = int(m.group(4))
        if w:
            p['cho'].add(ts)
            p['cho_max'] = max(p['cho_max'], w)
    elif 'BLOCKED_IP:' in line:
        v = line.split('BLOCKED_IP:', 1)[1].strip()
        if v:
            blocked[v[:120]] += 1
if not mau:
    sys.exit('không có mẫu trong cửa sổ')
phu = len(mau) * GIAY / max(mau[-1] - mau[0] + GIAY, 1)
print(f'{len(mau)} mẫu, {fmt(mau[0])} → {fmt(mau[-1])}, độ phủ {phu:.0%}, {drops} lần mất kết nối.')
tuoi = datetime.datetime.now(TZ).timestamp() - mau[-1]
if DAY is None and tuoi > 300:
    print(f'CẢNH BÁO: mẫu cuối cách đây {tuoi / 3600:.1f} giờ. Nếu bộ lấy mẫu còn phải chạy, nó đã dừng: kiểm tiến trình trong file .pid.')
for g0, g1 in gaps[:20]:
    print(f'  mất mẫu {fmt(g0)} → {fmt(g1)} ({(g1 - g0) / 60:.1f} phút)')
print('\n| Pool | Mẫu có dòng | Trần | INUSE lớn nhất | Giây có hàng chờ | Hàng chờ lớn nhất |\n|---|---|---|---|---|---|')
for k, p in sorted(pool.items()):
    print(f"| {k} | {len(p['mau'])} | {p['tran']} | {p['inuse']} | {len(p['cho']) * GIAY} | {p['cho_max']} |")
print('\nBLOCKED_IP khác rỗng:', dict(blocked) if blocked else 'không có')
