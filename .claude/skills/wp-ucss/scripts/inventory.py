# inventory.py (wp-ucss): mỗi URL × biến thể → file CSS gộp LiteSpeed đang trỏ tới.
# python3 -I inventory.py --site <site.json> <paths.txt> <out.jsonl> [biến thể, mặc định m,d,g]. Tuần tự, 1 lượt mỗi rate_ms, chạy trong plock.sh (khoá lock_file).
import gzip, json, os, re, sys, time, urllib.request
from html.parser import HTMLParser



# Marker của templates/ucss-swap.php là data-ucss; site có thể thêm tiền tố riêng (data-<site>-ucss, <site>-ucss-inline, data-<site>-h).
LINK_MARK = re.compile(r'data-(?:[a-z0-9_]+-)?ucss')
INLINE_ID = re.compile(r'(?:[a-z0-9_]+-)?ucss-inline')
INLINE_H = re.compile(r'data-(?:[a-z0-9_]+-)?(?:ucss-)?h')


def css_hashes(html, combined_path):
    pattern = re.compile(re.escape(combined_path) + r'([0-9a-f]{32})\.css')

    class CssParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.hashes = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'link':
                self.hashes.extend(pattern.findall(attrs.get('href') or ''))
                if any(LINK_MARK.fullmatch(k) and v == '1' for k, v in attrs.items()):
                    for _, url in re.findall(r"\bthis\.href\s*=\s*(['\"])(.*?)\1", attrs.get('onerror') or ''):
                        self.hashes.extend(pattern.findall(url))
            elif tag == 'style' and INLINE_ID.fullmatch(attrs.get('id') or ''):
                for k, v in attrs.items():
                    if INLINE_H.fullmatch(k) and re.fullmatch(r'[0-9a-f]{32}', v or ''):
                        self.hashes.append(v)

    parser = CssParser()
    parser.feed(html)
    parser.close()
    return list(dict.fromkeys(parser.hashes))


def main():
    a = sys.argv[1:]
    f = os.environ.get('UCSS_SITE')
    if '--site' in a:
        i = a.index('--site'); f = a[i + 1]; del a[i:i + 2]
    if not f:
        sys.exit('thiếu --site <site.json> hoặc biến UCSS_SITE')
    S = json.load(open(f))
    UA, ACC, BASE = S['ua'], S['accept'], 'https://' + S['host']
    GAP = S.get('rate_ms', 1000) / 1000
    paths = [l.strip() for l in open(a[0]) if l.strip().startswith('/')]
    devs = (a[2] if len(a) > 2 else 'm,d,g').split(',')
    out = open(a[1], 'a')
    for p in paths:
        for v in devs:
            t0 = time.time()
            rec = {'path': p, 'v': v}
            try:
                rq = urllib.request.Request(BASE + p, headers={'User-Agent': UA[v], 'Accept': ACC[v], 'Accept-Encoding': 'gzip', 'Accept-Language': S['accept_language']})
                with urllib.request.urlopen(rq, timeout=60) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                    h = body.decode('utf-8', 'replace')
                    rec.update(code=r.status, lsc=r.headers.get('X-LiteSpeed-Cache', ''), final=r.geturl().replace(BASE, ''))
            except urllib.error.HTTPError as e:
                rec.update(code=e.code); h = ''
            except Exception as e:
                rec.update(code=0, err=str(e)[:80]); h = ''
            rec['css'] = css_hashes(h, S['combined_css_path'])
            rec['guest'] = 'litespeed/javascript' in h
            rec['bytes'] = len(h.encode('utf-8'))
            out.write(json.dumps(rec) + '\n'); out.flush()
            time.sleep(max(0, GAP - (time.time() - t0)))


if __name__ == '__main__':
    main()
