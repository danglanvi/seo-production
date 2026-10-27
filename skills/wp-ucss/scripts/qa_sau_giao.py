# qa_sau_giao.py (wp-ucss): kiểm sau mỗi lần giao map. Mỗi path trong map × biến thể: trang 200, link file gộp có trong map đã đổi sang
# CSS gọn, ghi robots và canonical để so với lượt trước. Thay cho lượt QA bằng agent (site mẫu 27/10/2026: 2 agent, 274 lượt tải).
# python3 -I qa_sau_giao.py --site <site.json> <map.php> <out.json> [biến thể, mặc định m,d,p,q,g] [--baseline <out lượt trước.json>] [--paths <file>]
# --paths: chỉ kiểm path có trong file (ví dụ purge_paths.txt của lượt regen vừa giao).
# Tuần tự, 1 lượt mỗi rate_ms, chạy trong plock.sh (khoá lock_file). Mã 1 khi có cặp SAI hoặc robots/canonical đổi so với baseline.
import gzip, json, os, re, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from map_diff import parse  # noqa: E402

LINK = re.compile(r'<link\b[^>]*>', re.I)
ROBOTS = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']*)', re.I)
CANON = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']*)', re.I)


class Qa:
    def __init__(self, S, map_php):
        self.S, self.swap = S, S.get('swap_attr', 'data-ucss')
        self.md5 = re.compile(re.escape(S['combined_css_path']) + r'([0-9a-f]{32})\.css')
        self.path_md5 = {p: h for h, (_, ps) in parse(map_php).items() for p in ps}

    def links(self, html):
        """Trả (md5 đã đổi, md5 chưa đổi) theo thẻ link stylesheet có đường dẫn file gộp."""
        done, raw = [], []
        for t in LINK.findall(html):
            m = self.md5.search(t)
            if m and 'stylesheet' in t.lower():
                (done if self.swap in t else raw).append(m.group(1))
        return done, raw

    def judge(self, p, code, final, html):
        if code != 200 or final != p:
            return 'SAI', f'mã {code}, cuối {final}'
        done, raw = self.links(html)
        if self.path_md5.get(p) in raw:
            return 'SAI', 'link file gộp có trong map chưa đổi sang CSS gọn'
        if raw and not done:
            return 'CẢNH BÁO', 'file gộp ngoài map (site đã dựng file gộp mới): chạy regen.sh'
        return ('ĐẠT', '') if done else ('CẢNH BÁO', 'không thấy link file gộp')

    def fetch(self, p, v):
        S, base = self.S, 'https://' + self.S['host']
        rq = urllib.request.Request(base + p, headers={'User-Agent': S['ua'][v], 'Accept': S['accept'][v], 'Accept-Encoding': 'gzip', 'Accept-Language': S['accept_language']})
        try:
            with urllib.request.urlopen(rq, timeout=60) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                return r.status, r.geturl().replace(base, ''), r.headers.get('X-Robots-Tag', ''), body.decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            return e.code, p, '', ''


def compare(rows, old_rows):
    old = {(r['path'], r['v']): r for r in old_rows}
    out = []
    for r in rows:
        o = old.get((r['path'], r['v']))
        if o and (o['robots'], o['canonical']) != (r['robots'], r['canonical']):
            out.append({'path': r['path'], 'v': r['v'], 'truoc': [o['robots'], o['canonical']], 'sau': [r['robots'], r['canonical']]})
    return out


def main(a):
    f, base_f, only = os.environ.get('UCSS_SITE'), None, None
    if '--site' in a:
        i = a.index('--site'); f = a[i + 1]; del a[i:i + 2]
    if '--baseline' in a:
        i = a.index('--baseline'); base_f = a[i + 1]; del a[i:i + 2]
    if '--paths' in a:
        i = a.index('--paths'); only = {l.strip() for l in open(a[i + 1]) if l.strip()}; del a[i:i + 2]
    if not f or len(a) < 2:
        print('dùng: qa_sau_giao.py --site <site.json> <map.php> <out.json> [m,d,p,q,g] [--baseline <file>]'); return 2
    S = json.load(open(f)); q = Qa(S, a[0]); gap = S.get('rate_ms', 1000) / 1000
    devs = (a[2] if len(a) > 2 else 'm,d,p,q,g').split(',')
    rows = []
    for p in sorted(x for x in q.path_md5 if only is None or x in only):
        for v in devs:
            t0 = time.time()
            code, final, xrt, html = q.fetch(p, v)
            st, why = q.judge(p, code, final, html)
            rm, cm = ROBOTS.search(html), CANON.search(html)
            rows.append({'path': p, 'v': v, 'kq': st, 'ly_do': why, 'robots': (rm.group(1) if rm else '') + ('|' + xrt if xrt else ''),
                         'canonical': cm.group(1) if cm else ''})
            time.sleep(max(0, gap - (time.time() - t0)))
    doi = compare(rows, json.load(open(base_f))['rows']) if base_f else []
    dem = {k: sum(r['kq'] == k for r in rows) for k in ('ĐẠT', 'CẢNH BÁO', 'SAI')}
    json.dump({'site': S['host'], 'luot': len(rows), 'dem': dem, 'robots_canonical_doi': doi, 'rows': rows}, open(a[1], 'w'), ensure_ascii=False, indent=1)
    print(f"{len(rows)} lượt: ĐẠT {dem['ĐẠT']}, CẢNH BÁO {dem['CẢNH BÁO']}, SAI {dem['SAI']}; robots/canonical đổi: {len(doi) if base_f else 'chưa có baseline'}")
    for r in rows:
        if r['kq'] != 'ĐẠT':
            print(r['kq'], r['v'], r['path'], r['ly_do'])
    return 1 if dem['SAI'] or doi else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
