# Kiểm mã, nhãn cache, robots và canonical của URL sạch ở 5 biến thể cache mà trình duyệt thật và bot nhận:
# Chrome desktop và mobile có hoặc không có image/webp trong Accept, và Googlebot smartphone (Accept: */*).
# Chạy sau mỗi đợt PSI, purge theo URL hoặc làm nóng cache.
# python3 -I cache_variants.py <url> [<url> ...] | --urls urls.tsv  [--threads 2] [--out kq.jsonl]
# urls.tsv: "tên<TAB>url" hoặc mỗi dòng một URL. Script từ chối URL có query: theme và plugin SEO hay trả noindex cho URL có query.
# Lượt GET đầu ở biến thể còn trống ghi bản cache cho URL sạch, tức là làm nóng đúng biến thể đó.
# Exit 1 khi một URL có mã khác 200, robots hoặc canonical lệch giữa các biến thể, hoặc trang index mà thiếu canonical.
import argparse, concurrent.futures as cf, gzip, json, sys, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

ap = argparse.ArgumentParser()
ap.add_argument('url', nargs='*')
ap.add_argument('--urls')
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--out')
a = ap.parse_args()

CH = 'Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 {}Safari/537.36'
DUA = CH.format('Macintosh; Intel Mac OS X 10_15_7', '')
MUA = CH.format('Linux; Android 14; SM-A546E', 'Mobile ')
GBOT = ('Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/141.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
WEBP = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
VARIANTS = {'desktop-webp': (DUA, WEBP), 'desktop-plain': (DUA, '*/*'), 'mobile-webp': (MUA, WEBP),
            'mobile-plain': (MUA, '*/*'), 'googlebot-sp': (GBOT, '*/*')}

rows = []
for line in (open(a.urls, encoding='utf-8') if a.urls else []):
    if line.strip() and not line.startswith('#'):
        p = line.rstrip('\n').split('\t')
        rows.append((p[0], p[1]) if len(p) > 1 else (p[0], p[0]))
rows += [(u, u) for u in a.url]
if not rows:
    sys.exit('Thiếu URL.')
q = [u for _, u in rows if urllib.parse.urlsplit(u).query]
if q:
    sys.exit('Chỉ kiểm URL sạch, bỏ query: ' + ' '.join(q[:5]))


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots, self.canon = [], []

    def handle_starttag(self, tag, attrs):
        d = {k: (v or '') for k, v in attrs}
        if tag == 'meta' and d.get('name', '').lower() in ('robots', 'googlebot'):
            self.robots.append(d.get('content', '').lower())
        if tag == 'link' and 'canonical' in d.get('rel', '').lower().split():
            self.canon.append(d.get('href', ''))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *x, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def fetch(url, ua, acc):
    h = {'User-Agent': ua, 'Accept': acc, 'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8', 'Accept-Encoding': 'gzip'}
    try:
        r = opener.open(urllib.request.Request(url, headers=h), timeout=60)
    except urllib.error.HTTPError as e:
        r = e
    body = r.read()
    if (r.headers.get('Content-Encoding') or '').lower() == 'gzip':
        body = gzip.decompress(body)
    p = Head()
    p.feed(body.decode('utf-8', 'replace'))
    cache = next((f'{k}={r.headers[k]}' for k in ('x-litespeed-cache', 'x-qc-cache', 'cf-cache-status', 'x-cache') if r.headers.get(k)), '-')
    noindex = any('noindex' in x for x in p.robots + [(r.headers.get('X-Robots-Tag') or '').lower()])
    return {'code': r.status if hasattr(r, 'status') else r.code, 'cache': cache, 'noindex': noindex,
            'canonical': p.canon[0] if len(p.canon) == 1 else (p.canon or None), 'location': r.headers.get('Location')}


def check(row):
    name, url = row
    v = {k: fetch(url, ua, acc) for k, (ua, acc) in VARIANTS.items()}
    bad = []
    if any(x['code'] != 200 for x in v.values()):
        bad.append('mã ' + ', '.join(f"{k}={x['code']}" for k, x in v.items() if x['code'] != 200))
    ni = {k for k, x in v.items() if x['noindex']}
    if ni and len(ni) < len(v):
        bad.append('noindex chỉ ở ' + ', '.join(sorted(ni)))
    if len({json.dumps(x['canonical']) for x in v.values()}) > 1:
        bad.append('canonical lệch giữa các biến thể')
    if not ni and any(not x['canonical'] for x in v.values()):
        bad.append('trang index mà thiếu canonical')
    note = 'noindex ở cả 5 biến thể' if len(ni) == len(v) else ''
    return {'name': name, 'url': url, 'bad': bad, 'note': note, 'variants': v}


with cf.ThreadPoolExecutor(max(1, min(a.threads, 2))) as ex:
    res = list(ex.map(check, rows))
if a.out:
    with open(a.out, 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in res)
for r in res:
    print(('!! ' if r['bad'] else '   ') + f"{r['name']}  {'; '.join(r['bad'] + ([r['note']] if r['note'] else [])) or 'đạt'}")
    for k, x in r['variants'].items():
        print(f"     {k:13} {x['code']} {x['cache']:22} {'noindex' if x['noindex'] else 'index  '} {x['canonical']}")
nbad = sum(1 for r in res if r['bad'])
print(f'URL kiểm: {len(res)} | lệch: {nbad}')
sys.exit(1 if nbad else 0)
