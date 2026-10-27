#!/usr/bin/env python3
"""render_snap.py (wp-paid-plugin-exit): chụp HTML bỏ cache của danh sách path, để so trước và sau khi gỡ plugin.

Dùng:
  python3 render_snap.py --base https://<domain> --sitemap > urls.txt          # in mọi path trong sitemap_index.xml
  python3 render_snap.py --base https://<domain> urls.txt <outdir> [--workers 2] [--rps 1] [--via 127.0.0.1] [--bo-cache cookie|query]
Ra <outdir>/<idx>.html và index.json (status, bytes, ms, location, header cache). Chụp 2 lượt trước khi đổi, 1 lượt sau.
--via: chạy trên server, gọi qua IP đó với SNI của domain, để không đi qua CDN.
--bo-cache cookie (mặc định): cookie _lscache_vary ngẫu nhiên. query: thêm ?nc=<số>. Với LiteSpeed Cache có CSS gọn theo URL,
  tham số query có thể sinh file CSS mới cho mỗi URL, nên dùng cookie.
Mặc định 1 request/giây, 2 luồng: site mẫu 24/10/2026 chụp 352 URL trong khoảng 6 phút.
"""
import argparse, http.client, json, os, random, re, socket, ssl, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

UA = 'Mozilla/5.0 (compatible; render-snap)'


def make_conn(base, via):
    u = urlsplit(base)
    host, https = u.hostname, u.scheme == 'https'
    port = u.port or (443 if https else 80)
    if not via:
        return host, (lambda: (http.client.HTTPSConnection if https else http.client.HTTPConnection)(host, port, timeout=120))

    class Via(http.client.HTTPSConnection):
        def connect(self):
            s = socket.create_connection((via, port), timeout=self.timeout)
            self.sock = ssl._create_unverified_context().wrap_socket(s, server_hostname=host)
    if https:
        return host, (lambda: Via(host, port, timeout=120))
    return host, (lambda: http.client.HTTPConnection(via, port, timeout=120))


def fetch(conn, host, path, cookie=None):
    c = conn()
    h = {'Host': host, 'User-Agent': UA, 'Accept-Encoding': 'identity'}
    if cookie:
        h['Cookie'] = cookie
    c.request('GET', path, headers=h)
    r = c.getresponse()
    b = r.read()
    out = (r.status, b, r.getheader('location') or '', r.getheader('x-litespeed-cache') or r.getheader('cf-cache-status') or '')
    c.close()
    return out


def sitemap_paths(conn, host):
    loc = re.compile(r'<loc>\s*https?://' + re.escape(host) + r'(/[^<\s]*)\s*</loc>')
    out, seen = [], set()
    for sm in loc.findall(fetch(conn, host, '/sitemap_index.xml')[1].decode('utf-8', 'replace')):
        for p in loc.findall(fetch(conn, host, sm)[1].decode('utf-8', 'replace')):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--via')
    ap.add_argument('--sitemap', action='store_true')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--rps', type=float, default=1.0)
    ap.add_argument('--bo-cache', choices=['cookie', 'query'], default='cookie')
    ap.add_argument('urls', nargs='?')
    ap.add_argument('outdir', nargs='?')
    a = ap.parse_args()
    host, conn = make_conn(a.base, a.via)
    if a.sitemap:
        print('\n'.join(sitemap_paths(conn, host)))
        return 0
    if not (a.urls and a.outdir):
        sys.exit(__doc__)
    paths = [l.strip() for l in open(a.urls, encoding='utf-8') if l.strip()]
    os.makedirs(a.outdir, exist_ok=True)
    lock, last = threading.Lock(), [0.0]

    def pace():
        with lock:
            w = last[0] + 1.0 / a.rps - time.time()
            if w > 0:
                time.sleep(w)
            last[0] = time.time()

    def one(i, p):
        t0 = time.time()
        st, b, loc, xc = 'ERR', b'', '', ''
        for _ in range(3):
            try:
                pace()
                n = random.randint(1, 10 ** 9)
                q = p + ('&' if '?' in p else '?') + f'nc={n}' if a.bo_cache == 'query' else p
                st, b, loc, xc = fetch(conn, host, q, None if a.bo_cache == 'query' else f'_lscache_vary=rs{n}')
                break
            except Exception as e:  # mạng chập chờn: thử lại, ghi lỗi nếu hỏng cả 3 lượt
                b = str(e).encode()[:200]
                time.sleep(5)
        with open(os.path.join(a.outdir, '%04d.html' % i), 'wb') as f:
            f.write(b)
        return {'i': i, 'url': p, 'status': st, 'bytes': len(b), 'ms': int((time.time() - t0) * 1000),
                'loc': loc.replace(host, 'HOST'), 'xcache': xc}

    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda x: one(*x), enumerate(paths)))
    with open(os.path.join(a.outdir, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=0)
    print('xong', len(res), 'khác 200:', sum(1 for r in res if r['status'] != 200))
    return 0


if __name__ == '__main__':
    sys.exit(main())
