# Kiểm sau khi ghi plan.json: mã trả về, title, meta description, H1, slug mới + 301 từ URL cũ, redirect.
# python3 -I verify.py --plan plan.json --out verify.json [--year 2026]
# Staging có Basic Auth: đặt VERIFY_AUTH="user:pass" (chỉ gửi tới host của từng URL trong plan).
# Title chứa biến Rank Math khác %currentyear% (ví dụ %sep%) thì chỉ kiểm phần chữ cố định.
import argparse, base64, concurrent.futures as cf, datetime, html, json, os, re, unicodedata, urllib.error, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('--plan', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--year', default=str(datetime.date.today().year))
a = ap.parse_args()
plan = json.load(open(a.plan))
N = lambda s: re.sub(r'\s+', ' ', unicodedata.normalize('NFC', html.unescape(str(s or '')))).strip()
H = {'User-Agent': 'Mozilla/5.0 (Macintosh) wps-verify'}
if os.environ.get('VERIFY_AUTH'):
    H['Authorization'] = 'Basic ' + base64.b64encode(os.environ['VERIFY_AUTH'].encode()).decode()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *x, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def get(url):
    try:
        r = opener.open(urllib.request.Request(url, headers=H), timeout=40)
        return r.status, r.headers.get('Location'), r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Location'), e.read().decode('utf-8', 'replace')


def head_of(page):
    t = re.search(r'<title[^>]*>(.*?)</title>', page, re.S)
    d = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', page)
    h = [N(re.sub(r'<[^>]+>', '', x)) for x in re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S)]
    return N(t.group(1)) if t else None, N(d.group(1)) if d else None, h


def fixed_parts(v):
    return [p for p in (N(x) for x in re.split(r'%[a-z_]+%', v.replace('%currentyear%', a.year))) if len(p) > 3]


exp = {}
for o in plan['ops']:
    if not o.get('url'):
        continue
    e = exp.setdefault(o['url'], {'post': o['post']})
    if o['target'] == 'meta:rank_math_title':
        e['title'] = o['value']
    elif o['target'] == 'meta:rank_math_description':
        e['desc'] = o['value']
    elif o['target'] == 'post_title':
        e['h1'] = o['value']
    elif o['target'] == 'post_name':
        e['moved_to'] = o['redirect']['to']


def check(url):
    e = exp[url]
    bad = []
    if 'moved_to' in e:
        c, loc, _ = get(url)
        if c != 301 or (loc or '') != e['moved_to']:
            bad.append(f'URL cũ trả {c} → {loc}, cần 301 → {e["moved_to"]}')
        url = e['moved_to']
    c, loc, page = get(url)
    t, d, h1 = head_of(page)
    if c != 200:
        bad.append(f'mã {c} {loc or ""}')
    if 'title' in e and not all(p in (t or '') for p in fixed_parts(e['title'])):
        bad.append(f'title: {t!r}')
    if 'desc' in e and not all(p in (d or '') for p in fixed_parts(e['desc'])):
        bad.append(f'meta: {d!r}')
    if 'h1' in e and N(e['h1']) not in h1:
        bad.append(f'h1: {h1[:2]!r}')
    return url, bad


res = {}
with cf.ThreadPoolExecutor(6) as ex:
    for u, bad in ex.map(check, sorted(exp)):
        res[u] = bad
for o in plan['ops']:
    if o['target'] == 'redirect':
        site = re.match(r'https?://[^/]+', o.get('to') or o.get('url') or '')
        if site:
            c, loc, _ = get(f"{site.group(0)}/{o['src'].strip('/')}/")
            if c != o['code'] or (loc or '') != (o['to'] or ''):
                res[o['src']] = [f'redirect trả {c} → {loc}']
json.dump(res, open(a.out, 'w'), ensure_ascii=False, indent=1)
bad = {k: v for k, v in res.items() if v}
print(f'URL kiểm: {len(res)} | lệch: {len(bad)}')
for k, v in bad.items():
    print(' ', k, v)
raise SystemExit(1 if bad else 0)
