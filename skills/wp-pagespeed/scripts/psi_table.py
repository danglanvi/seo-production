# Bảng so sánh PSI giữa các mốc đo. Ô điểm ghi mọi lượt của từng mốc; các cột khác ghi trung vị của mốc đầu → mốc cuối.
# python3 -I psi_table.py <thư mục mốc 1> [<mốc 2> ...] [--urls urls.tsv] [--detail] [--json out.json]
# --urls: giữ thứ tự template theo file. --detail: với mốc cuối, in phần tử LCP, 4 pha LCP, cơ hội tiết kiệm, bên thứ ba, byte theo loại, CrUX.
import argparse, glob, json, os, re, statistics as st

ap = argparse.ArgumentParser()
ap.add_argument('dirs', nargs='+')
ap.add_argument('--urls')
ap.add_argument('--detail', action='store_true')
ap.add_argument('--json')
a = ap.parse_args()

nv = lambda au, k: (au.get(k) or {}).get('numericValue')


def load(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, '*.json'))):
        m = re.match(r'(.+)_(mobile|desktop)(?:_run(\d+))?$', os.path.basename(f)[:-5])
        if not m:
            continue
        j = json.load(open(f)); lr = j['lighthouseResult']; au = lr['audits']
        sc = lr['categories']['performance']['score']
        if sc is None:
            continue
        obs = ((au.get('metrics') or {}).get('details') or {}).get('items') or [{}]
        out.setdefault((m.group(1), m.group(2)), []).append(dict(
            run=int(m.group(3) or 1), score=round(sc * 100), j=j,
            lcp=nv(au, 'largest-contentful-paint') / 1000, fcp=nv(au, 'first-contentful-paint') / 1000,
            tbt=nv(au, 'total-blocking-time'), cls=nv(au, 'cumulative-layout-shift'), kb=nv(au, 'total-byte-weight') / 1024,
            olcp=(obs[0].get('observedLargestContentfulPaint') or 0) / 1000, ofcp=(obs[0].get('observedFirstContentfulPaint') or 0) / 1000))
    return out


D = [load(d) for d in a.dirs]
names = [l.split('\t')[0] for l in open(a.urls) if l.strip() and not l.startswith('#')] if a.urls else sorted({k[0] for x in D for k in x})
f1 = lambda x: f'{x:.1f}'.replace('.', ',')
f3 = lambda x: f'{x:.3f}'.replace('.', ',')
fk = lambda x: f'{round(x):,}'.replace(',', '.')
med = lambda rows, k: st.median([r[k] for r in rows])
sc = lambda rows: '/'.join(str(r['score']) for r in sorted(rows, key=lambda r: r['run'])) if rows else '–'
pair = lambda b, c, k, f: f(med(c, k)) if b is c else f'{f(med(b, k))} → {f(med(c, k))}'
summary = {}
for dev in ('mobile', 'desktop'):
    print(f'\n{dev}\n| Template | Điểm ({" → ".join(os.path.basename(d.rstrip("/")) for d in a.dirs)}) | LCP (s) | FCP (s) | TBT (ms) | CLS | KB | LCP obs | FCP obs |\n|---|---|---|---|---|---|---|---|---|')
    for n in names:
        rows = [x.get((n, dev)) for x in D]
        b, c = rows[0], rows[-1]
        if not (b and c):
            print(f'| {n} | {" → ".join(sc(r) for r in rows)} | thiếu số |'); continue
        print(f"| {n} | {' → '.join(sc(r) for r in rows)} | {pair(b, c, 'lcp', f1)} | {pair(b, c, 'fcp', f1)} | {pair(b, c, 'tbt', lambda x: str(round(x)))} | {pair(b, c, 'cls', f3)} | {pair(b, c, 'kb', fk)} | {f1(med(c, 'olcp'))} | {f1(med(c, 'ofcp'))} |")
        summary.setdefault(dev, []).append([med(r, 'score') if r else None for r in rows])
for dev, rows in summary.items():
    cols = list(zip(*rows))
    print(f"\n{dev}: điểm trung vị {len(rows)} template theo mốc: " + ' → '.join(str(st.median([v for v in col if v is not None])) for col in cols))

if a.detail:
    last = D[-1]
    for n in names:
        for dev in ('mobile', 'desktop'):
            rows = last.get((n, dev))
            if not rows:
                continue
            r = sorted(rows, key=lambda r: r['score'])[len(rows) // 2]
            j = r['j']; au = j['lighthouseResult']['audits']
            print(f"\n## {n} {dev} (lượt {r['run']}, điểm {r['score']})")
            lb = (au.get('lcp-breakdown-insight') or {}).get('details') or {}
            for it in lb.get('items', []):
                if it.get('type') == 'node':
                    print('  LCP:', (it.get('snippet') or it.get('selector') or '')[:150])
                if it.get('type') == 'table':
                    print('  Pha LCP:', ', '.join(f"{p.get('label') or p.get('subpart')} {round(p.get('duration') or 0)} ms" for p in it.get('items', [])))
            opp = []
            for k, v in au.items():
                s = v.get('metricSavings') or {}
                dt = v.get('details') or {}
                b = (dt.get('overallSavingsBytes') or sum((it.get('wastedBytes') or 0) for it in dt.get('items') or [] if isinstance(it, dict))) / 1024
                if v.get('score') is not None and v['score'] < 0.9 and (s.get('LCP') or s.get('FCP') or s.get('TBT') or b):
                    opp.append((round((s.get('LCP') or 0) + (s.get('FCP') or 0) + (s.get('TBT') or 0)), round(b), k))
            print('  Cơ hội (ms LCP+FCP+TBT, KB):', '; '.join(f'{k} {ms}ms {kb}KB' for ms, kb, k in sorted(opp, reverse=True)[:8]))
            rb = [((it.get('url') or '')[-70:], round(it.get('wastedMs') or 0)) for it in ((au.get('render-blocking-insight') or {}).get('details') or {}).get('items') or []]
            if rb:
                print('  Chặn hiển thị:', '; '.join(f'{u} {w}ms' for u, w in rb[:6]))
            tp = []
            for it in ((au.get('third-parties-insight') or {}).get('details') or {}).get('items') or []:
                e = it.get('entity'); e = e.get('text') if isinstance(e, dict) else e
                tp.append((round(it.get('mainThreadTime') or 0), round((it.get('transferSize') or 0) / 1024), e))
            if tp:
                print('  Bên thứ ba (ms main thread, KB):', '; '.join(f'{e} {t}ms {kb}KB' for t, kb, e in sorted(tp, reverse=True)[:6]))
            bt = {}
            for q in ((au.get('network-requests') or {}).get('details') or {}).get('items') or []:
                bt[q.get('resourceType')] = bt.get(q.get('resourceType'), 0) + (q.get('transferSize') or 0)
            print('  KB theo loại:', ', '.join(f'{k} {round(v / 1024)}' for k, v in sorted(bt.items(), key=lambda x: -x[1])))
            for lab, le in (('CrUX URL', j.get('loadingExperience')), ('CrUX origin', j.get('originLoadingExperience'))):
                mm = (le or {}).get('metrics') or {}
                if mm:
                    g = lambda k: (mm.get(k) or {}).get('percentile')
                    print(f"  {lab}: LCP {g('LARGEST_CONTENTFUL_PAINT_MS')} ms, INP {g('INTERACTION_TO_NEXT_PAINT')} ms, CLS {g('CUMULATIVE_LAYOUT_SHIFT_SCORE')}/100, TTFB {g('EXPERIMENTAL_TIME_TO_FIRST_BYTE')} ms")

if a.json:
    json.dump({os.path.basename(d.rstrip('/')): {f'{k[0]}|{k[1]}': [{x: v for x, v in r.items() if x != 'j'} for r in rows] for k, rows in x.items()} for d, x in zip(a.dirs, D)}, open(a.json, 'w'), ensure_ascii=False, indent=1)
