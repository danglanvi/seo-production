# A/B trên PSI bằng bản HTML tĩnh (do-dac.md mục 3): dựng biến thể, đưa lên uploads/psi-ab-<tag>/, tạo danh sách URL xen kẽ,
# lập bảng kết quả, chuyển file thử vào quarantine. Không xoá file nào trên server.
#   python3 -I "$WPS/scripts/psi_ab.py" build  --spec ab.json --dir <thư mục> --site https://example.com --tag <tag> [--a v0 --b v4 --min-gain 3 --lcp-ms 200 --cls 0.02 --min-runs 4 --max-runs 5 --bench-gap 0.2] [--from-src]
#   python3 -I "$WPS/scripts/psi_ab.py" verify --dir <thư mục>                       (kiểm noindex và canonical của mọi bản tĩnh)
#   python3 -I "$WPS/scripts/psi_ab.py" upload --dir <thư mục> --ssh <alias> --root <web root> --tag <tag> [--owner www:www] [--apply]
#   python3 -I "$WPS/scripts/psi_ab.py" urls   --dir <thư mục> --site https://example.com --tag <tag> [--runs 4] > urls-ab.tsv
#   python3 -I "$WPS/scripts/psi_run.py" --urls urls-ab.tsv --out <psi> --runs 1 --devices mobile
#   python3 -I "$WPS/scripts/psi_ab.py" table  --psi <psi> --dir <thư mục> [--split-bench] [--bench-cut 800]
#   python3 -I "$WPS/scripts/psi_ab.py" quarantine --ssh <alias> --root <web root> --tag <tag> [--qdir /www/backup/quarantine] [--site https://example.com --dir <thư mục>] [--apply]
# upload và quarantine ghi lên server: mặc định chỉ in lệnh sẽ chạy (dry-run). Thêm --apply để chạy thật.
# build tự chèn <meta name="robots" content="noindex,nofollow"> và canonical trỏ chính bản tĩnh vào MỌI file out/*.html, kể cả v0.
# Nguyên nhân: 22/10/2026 sáu bản tĩnh A/B nằm công khai khoảng 30 phút với robots index và canonical trỏ URL gốc. upload chạy verify trước, lỗi thì từ chối (mã 3).
# Có --site và --tag thì canonical là URL tuyệt đối của bản tĩnh. Thiếu thì canonical là tên file (tương đối, vẫn trỏ chính nó).
# Ngưỡng đặt trước: build ghi "decision" vào spec.json (a, b, min_gain, lcp_ms, cls, min_runs, max_runs, bench_gap, thời điểm). Chạy build lại với ngưỡng khác bị từ chối (mã 2).
# table in nhãn tốt hơn, không đổi, xấu hơn hoặc chưa đủ lượt theo ngưỡng đã ghi (cùng luật với psi_decide.py --spec), chỉ cho trang của spec.
# table đọc cả min_runs, max_runs, bench_gap ở gốc spec.json (cách ghi tay trong ab.json trước bản 1.17). Ca lỗi 29/10/2026: table dùng min_runs 3 trong khi spec ghi 4.
# table --split-bench: thêm bảng tách theo benchmarkIndex (< 800 máy chậm, >= 800 máy nhanh), trung vị từng nhóm.
# quarantine --site --dir: sau khi chuyển, gọi từng URL bản tĩnh và yêu cầu 404 hoặc 410. Còn 200 thì mã thoát 1.
# build --from-src: đọc <dir>/src/<trang>.html có sẵn thay vì tải từ site (dùng khi test offline).
# ab.json: {"pages": {"home": "https://example.com/"},
#           "variants": {"v0": [], "v4": [{"re": "<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->", "sub": "<script>…</script>"}],
#                        "nocv": [{"html_class": "tg-cv-off"}]}}
# Mỗi "re" phải khớp đúng "count" lần (mặc định 1), nếu không script dừng: biến thể sai thì kết quả A/B vô nghĩa.
# Mã thoát: 0 đạt, 1 lỗi chạy, 2 sai tham số hoặc đổi ngưỡng đặt trước, 3 bản tĩnh không an toàn (noindex, canonical).
import argparse, datetime, glob, json, os, re, statistics as st, subprocess, sys, time, urllib.error, urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_lib as L  # noqa: E402

UA = 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36 Chrome-Lighthouse'
ap = argparse.ArgumentParser(description='A/B trên PSI bằng bản HTML tĩnh: build, verify, upload, urls, table, quarantine. Mô tả đầy đủ ở đầu file script.')
ap.add_argument('cmd', choices=['build', 'verify', 'upload', 'urls', 'table', 'quarantine'])
for k in ('spec', 'dir', 'ssh', 'root', 'tag', 'site', 'psi', 'a', 'b'):
    ap.add_argument('--' + k)
ap.add_argument('--owner', default='www:www')
ap.add_argument('--runs', type=int, default=4)
ap.add_argument('--qdir', default='/www/backup/quarantine')
ap.add_argument('--min-gain', type=float)
ap.add_argument('--lcp-ms', type=float)
ap.add_argument('--cls', type=float)
ap.add_argument('--min-runs', type=int)
ap.add_argument('--max-runs', type=int)
ap.add_argument('--bench-gap', type=float)
ap.add_argument('--from-src', action='store_true', help='build: đọc <dir>/src/<trang>.html có sẵn, không tải từ site')
ap.add_argument('--split-bench', action='store_true', help='table: tách kết quả theo benchmarkIndex')
ap.add_argument('--bench-cut', type=float, default=L.DEFAULT_THR['bench_cut'])
ap.add_argument('--apply', action='store_true', help='upload, quarantine: chạy thật lên server (mặc định chỉ in lệnh)')
a = ap.parse_args()


def need(*ks):
    miss = [k for k in ks if not getattr(a, k.replace('-', '_'))]
    if miss:
        sys.exit('Thiếu --' + ', --'.join(miss))


def files():
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(a.dir, 'out', '*.html')))


def static_url(fname):
    return '%s/wp-content/uploads/psi-ab-%s/%s' % (a.site.rstrip('/'), a.tag, fname)


def canon_for(fname, site=None, tag=None):
    site, tag = site or a.site, tag or a.tag
    if site and tag:
        return '%s/wp-content/uploads/psi-ab-%s/%s' % (site.rstrip('/'), tag, fname)
    return fname


def spec_meta():
    sp = os.path.join(a.dir, 'spec.json')
    return json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}


def verify_dir():
    """Kiểm noindex và canonical tự trỏ ở mọi out/*.html. Trả danh sách lỗi."""
    fl = files()
    if not fl:
        return ['không có file trong %s/out' % a.dir]
    meta = spec_meta().get('meta', {})
    errs = []
    for f in fl:
        html = open(os.path.join(a.dir, 'out', f), encoding='utf-8').read()
        for e in L.check_noindex(html, canon_for(f, meta.get('site'), meta.get('tag'))):
            errs.append('%s: %s' % (f, e))
    return errs


def check_gone(urls, opener=urllib.request.urlopen):
    """Trả danh sách URL còn mở (không phải 404 hoặc 410)."""
    still = []
    for u in urls:
        try:
            opener(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=30).read()
            still.append(u)
        except urllib.error.HTTPError as e:
            if e.code not in (404, 410):
                still.append('%s (HTTP %d)' % (u, e.code))
    return still


if a.cmd == 'build':
    need('spec', 'dir')
    spec = json.load(open(a.spec, encoding='utf-8'))
    os.makedirs(os.path.join(a.dir, 'src'), exist_ok=True)
    os.makedirs(os.path.join(a.dir, 'out'), exist_ok=True)
    # Trang cần regex khớp số lần khác nhau: build nhiều spec vào cùng --dir. spec.json gộp pages để urls, table thấy đủ trang.
    sp = os.path.join(a.dir, 'spec.json')
    old = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    pages = {**old.get('pages', {}), **spec['pages']}
    # Ngưỡng đặt trước: ghi một lần ở build đầu. Build sau không được đổi.
    want = {k: v for k, v in (('a', a.a), ('b', a.b), ('min_gain', a.min_gain), ('lcp_ms', a.lcp_ms), ('cls', a.cls),
                              ('min_runs', a.min_runs), ('max_runs', a.max_runs), ('bench_gap', a.bench_gap)) if v is not None}
    dec = old.get('decision')
    if want:
        if dec:
            diff = {k: (dec.get(k), v) for k, v in want.items() if dec.get(k) != v}
            if diff:
                sys.exit('Ngưỡng đã đặt trước, không đổi sau khi build: %s. Muốn đổi thì dùng --dir mới.' % diff)
        else:
            dec = dict(L.DEFAULT_THR)
            dec = {'min_gain': dec['min_gain'], 'lcp_ms': dec['lcp_ms'], 'cls': dec['cls'], **want,
                   'decided_at': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
    meta = old.get('meta') or {}
    if a.site and a.tag:
        meta = {'site': a.site, 'tag': a.tag}
    out_spec = {**spec, 'pages': pages}
    if dec:
        out_spec['decision'] = dec
    if meta:
        out_spec['meta'] = meta
    json.dump(out_spec, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for p, url in spec['pages'].items():
        srcf = os.path.join(a.dir, 'src', p + '.html')
        if a.from_src:
            h = open(srcf, encoding='utf-8').read()
        else:
            h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read().decode('utf-8')
            open(srcf, 'w', encoding='utf-8').write(h)
        for v, ops in spec['variants'].items():
            out = h
            for op in ops:
                if 'html_class' in op:
                    m = re.search(r'<html\b[^>]*>', out)
                    tag = m.group(0)
                    new = re.sub(r'class="([^"]*)"', r'class="\1 %s"' % op['html_class'], tag, 1) if 'class="' in tag \
                        else tag.replace('<html', '<html class="%s"' % op['html_class'], 1)
                    out = out.replace(tag, new, 1)
                else:
                    n = len(re.findall(op['re'], out, re.S))
                    if n != op.get('count', 1):
                        sys.exit(f"{p}-{v}: regex khớp {n} lần, cần {op.get('count', 1)}: {op['re'][:80]}")
                    out = re.sub(op['re'], lambda _: op['sub'], out, flags=re.S)
            fname = f'{p}-{v}.html'
            try:
                out = L.inject_noindex(out, canon_for(fname))
            except ValueError as e:
                sys.exit(f'{fname}: {e}')
            open(os.path.join(a.dir, 'out', fname), 'w', encoding='utf-8').write(out)
    errs = verify_dir()
    if errs:
        sys.exit('Bản tĩnh sau build chưa an toàn:\n' + '\n'.join(errs))
    print('\n'.join(files()))

elif a.cmd == 'verify':
    need('dir')
    errs = verify_dir()
    if errs:
        print('KHÔNG AN TOÀN: bản tĩnh có thể bị index.\n' + '\n'.join(errs), file=sys.stderr)
        sys.exit(3)
    print('OK: %d bản tĩnh đều noindex,nofollow và canonical tự trỏ' % len(files()))

elif a.cmd == 'upload':
    need('dir', 'ssh', 'root', 'tag')
    errs = verify_dir()
    if errs:
        print('Từ chối upload: bản tĩnh chưa noindex hoặc canonical chưa tự trỏ. Chạy lại build.\n' + '\n'.join(errs), file=sys.stderr)
        sys.exit(3)
    d = f"{a.root}/wp-content/uploads/psi-ab-{a.tag}"
    remote = f"mkdir -p {d} && tar -xf - --no-same-owner -C {d} && chown -R {a.owner} {d} && chmod 644 {d}/*.html && ls {d} | wc -l"
    if not a.apply:
        print('DRY-RUN: sẽ gửi %d file %s lên %s bằng: ssh %s "%s". Thêm --apply để chạy thật.' % (len(files()), ' '.join(files()), d, a.ssh, remote))
        sys.exit(0)
    tar = subprocess.Popen(['tar', '--no-xattrs', '-C', os.path.join(a.dir, 'out'), '-cf', '-'] + files(),
                           stdout=subprocess.PIPE, env={**os.environ, 'COPYFILE_DISABLE': '1'})
    r = subprocess.run(['ssh', a.ssh, remote], stdin=tar.stdout)
    tar.wait()
    sys.exit(1 if r.returncode or tar.returncode else 0)

elif a.cmd == 'urls':
    need('dir', 'site', 'tag')
    spec = json.load(open(os.path.join(a.dir, 'spec.json'), encoding='utf-8'))
    for r in range(1, a.runs + 1):
        for v in spec['variants']:
            for p in spec['pages']:
                print(f"{p}-{v}-r{r}\t{a.site.rstrip('/')}/wp-content/uploads/psi-ab-{a.tag}/{p}-{v}.html?r={a.tag}{r}")

elif a.cmd == 'table':
    need('psi')
    sp_all = spec_meta() if a.dir else {}
    R = defaultdict(list)
    RS = defaultdict(list)  # (dev, trang, biến thể) -> run dict cho psi_lib.decide
    for f in glob.glob(os.path.join(a.psi, '*_mobile_run*.json')) + glob.glob(os.path.join(a.psi, '*_desktop_run*.json')):
        # Tên trang có thể có dấu gạch dưới (product_cat): tách bằng regex của psi_lib, không split('_').
        try:
            nm = L.parse_ab_name(os.path.basename(f), sp_all.get('variants'), sp_all.get('pages'))
        except ValueError as exc:
            sys.exit(str(exc))
        if not nm:
            print('Bỏ file không theo tên psi_ab: ' + os.path.basename(f), file=sys.stderr)
            continue
        dev, p, v, rk = nm['dev'], nm['page'], nm['var'], nm['k']
        lr = json.load(open(f))['lighthouseResult']
        m = lr['audits']['metrics']['details']['items'][0]
        lt = lr['audits'].get('long-tasks', {}).get('details', {}).get('items', [])
        R[(dev, p, v)].append((round(lr['categories']['performance']['score'] * 100), round(m['totalBlockingTime']), m['largestContentfulPaint'],
                               m.get('observedFirstContentfulPaint', 0), m.get('observedTraceEnd', 0) - m.get('observedLoad', 0),
                               sum(1 for t in lt if re.search(r'googletagmanager|google-analytics|facebook|doubleclick', t['url'])) > 0))
        r = L.load_run(f)
        r['k'] = int(re.sub(r'\D', '', rk) or 0)
        RS[(dev, p, v)].append(r)
    print('thiết bị | trang | biến thể | điểm (các lượt) | trung vị | TBT (các lượt) | LCP trung vị s | traceEnd − load lớn nhất ms | lượt có long task tracking')
    for (dev, p, v), x in sorted(R.items()):
        print(f"{dev} | {p} | {v} | {sorted(i[0] for i in x)} | {st.median(i[0] for i in x)} | {sorted(i[1] for i in x)} | "
              f"{st.median(i[2] for i in x) / 1000:.1f} | {max(i[4] for i in x)} | {sum(i[5] for i in x)}/{len(x)}")
    if a.split_bench:
        cut = a.bench_cut
        print(f'\nTách theo benchmarkIndex (< {cut:.0f} máy chậm, >= {cut:.0f} máy nhanh)')
        print('thiết bị | trang | biến thể | nhóm máy | số lượt | điểm trung vị | LCP trung vị s | benchmarkIndex trung vị')
        for (dev, p, v), runs in sorted(RS.items()):
            for name, pick in (('chậm', lambda r: r['bench'] is not None and r['bench'] < cut), ('nhanh', lambda r: r['bench'] is not None and r['bench'] >= cut), ('không rõ', lambda r: r['bench'] is None)):
                g = [r for r in runs if pick(r) and r['score'] is not None]
                if g:
                    print(f"{dev} | {p} | {v} | {name} | {len(g)} | {st.median(r['score'] for r in g):.1f} | "
                          f"{st.median(r['lcp'] for r in g) / 1000:.1f} | {st.median(r['bench'] for r in g if r['bench'] is not None) if name != 'không rõ' else '–'}")
    sd = sp_all.get('decision') or {}
    if sd.get('a') and sd.get('b'):
        thr = {k: L.DEFAULT_THR[k] for k in L.THR_KEYS}
        thr.update(L.spec_thr(sp_all))
        print(f"\nNgưỡng đặt trước ({sd.get('decided_at', '?')}): A={sd['a']} B={sd['b']} điểm {thr['min_gain']}, LCP {thr['lcp_ms']} ms, CLS {thr['cls']}, "
              f"{thr['min_runs']}-{thr['max_runs']} lượt mỗi nhánh, lệch máy {thr['bench_gap']}")
        for (dev, p, v), runs in sorted(RS.items()):
            if v != sd['a'] or (sp_all.get('pages') and p not in sp_all['pages']):
                continue
            b = RS.get((dev, p, sd['b']), [])
            r = L.decide(runs, b, thr)
            print(f"{dev} | {p} | {sd['a']}→{sd['b']} | {L.LABELS[r['label']]} | {r['reason']}{('; ' + r['note']) if r['note'] else ''}")
    else:
        print('\nChưa có ngưỡng đặt trước. Chạy build với --a, --b (và --min-gain, --lcp-ms, --cls) TRƯỚC khi đo, rồi thêm --dir vào lệnh table.', file=sys.stderr)

elif a.cmd == 'quarantine':
    need('ssh', 'root', 'tag')
    q = f"{a.qdir}/psi-ab-{a.tag}-{time.strftime('%Y%m%d')}"
    src = f"{a.root}/wp-content/uploads/psi-ab-{a.tag}"
    remote = f"mkdir -p {q} && chmod 700 {q} && mv {src} {q}/ && echo 'Tra lai: mv {q}/psi-ab-{a.tag} {a.root}/wp-content/uploads/' > {q}/MANIFEST.txt && echo {q}"
    if not a.apply:
        print(f'DRY-RUN: sẽ chuyển {src} vào {q} bằng: ssh {a.ssh} "{remote}". Thêm --apply để chạy thật.')
        sys.exit(0)
    r = subprocess.run(['ssh', a.ssh, remote])
    if r.returncode:
        sys.exit(1)
    if a.site and a.dir:
        still = check_gone([static_url(f) for f in files()])
        if still:
            print('Sau quarantine vẫn còn mở (cần 404 hoặc 410):\n' + '\n'.join(still), file=sys.stderr)
            sys.exit(1)
        print('Đã kiểm: mọi bản tĩnh trả 404 hoặc 410.')
    else:
        print('Chưa kiểm 404: thêm --site và --dir để script gọi lại từng URL.', file=sys.stderr)
