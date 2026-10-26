# So các file JSONL của perf_probe.mjs (dòng "median"). Mỗi file là một mốc, ví dụ production và staging, hoặc trước và sau một đợt sửa.
# python3 -I probe_table.py <mốc 1>.jsonl <mốc 2>.jsonl [...] [--urls urls.tsv] [--detail]
# Nhãn trong file đặt theo dạng "<mốc>-<template>" (perf_probe --label prod-home); script nhóm theo phần sau dấu "-" đầu tiên.
# --detail: in phần tử LCP và nguồn layout shift (từ dòng từng lượt) cho template có CLS từ 0,1 hoặc LCP chậm hơn mốc đầu từ 0,3 s.
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument('files', nargs='+')
ap.add_argument('--urls')
ap.add_argument('--detail', action='store_true')
a = ap.parse_args()


def load(f):
    med, runs = {}, {}
    for l in open(f):
        try:
            j = json.loads(l)
        except ValueError:
            continue
        k = (j['label'].split('-', 1)[-1], j['dev'])
        if j.get('run') == 'median':
            med[k] = j
        else:
            runs.setdefault(k, []).append(j)
    return med, runs


D = [load(f) for f in a.files]
names = [l.split('\t')[0] for l in open(a.urls) if l.strip() and not l.startswith('#')] if a.urls else sorted({k[0] for m, _ in D for k in m})
s = lambda x: f'{x / 1000:.2f}'.replace('.', ',')
col = lambda rows, k, f: ' → '.join(f(r[k]) if r else '–' for r in rows)
hdr = ' → '.join(os.path.basename(f).rsplit('.', 1)[0] for f in a.files)
for dev in ('mobile', 'desktop'):
    print(f'\n{dev} ({hdr})\n| Template | FCP (s) | LCP (s) | TBT (ms) | CLS | KB | TTFB (ms) | theme |\n|---|---|---|---|---|---|---|---|')
    for n in names:
        rows = [m.get((n, dev)) for m, _ in D]
        if not any(rows):
            continue
        print(f"| {n} | {col(rows, 'fcp', s)} | {col(rows, 'lcp', s)} | {col(rows, 'tbt', lambda x: str(round(x)))} | {col(rows, 'cls', str)} | {col(rows, 'kb', lambda x: str(round(x)))} | {col(rows, 'ttfb', lambda x: str(round(x)))} | {' / '.join(r['theme'] for r in rows if r)} |")
if a.detail:
    print()
    for dev in ('mobile', 'desktop'):
        for n in names:
            base = D[0][0].get((n, dev))
            for f, (m, runs) in zip(a.files, D):
                r = m.get((n, dev))
                if not r or not (r['cls'] >= 0.1 or (base and r['lcp'] - base['lcp'] >= 300)):
                    continue
                one = (runs.get((n, dev)) or [{}])[0]
                print(f"{os.path.basename(f)} {n} {dev}: LCP {s(r['lcp'])} s ({one.get('el', '')}), CLS {r['cls']}, shifts {one.get('shifts')}")
