#!/usr/bin/env python3
"""bunny_purge.py (wp-ucss): purge cache Bunny theo từng URL sau khi đổi HTML trên origin, tuỳ chọn làm nóng lại ngay. Nhánh "bunny" của bước purge CDN trong regen.sh.
Dùng: python3 -I bunny_purge.py <paths.txt> [--site <site.json>] [--host https://example.com] [--apply] [--warm]
- paths.txt: mỗi dòng 1 path bắt đầu bằng "/". Mặc định chỉ in việc sẽ làm; --apply mới gọi API.
- Host mặc định: https://<host> của site.json (--site hoặc biến UCSS_SITE). Không cần id pull zone: API purge theo URL.
- Gọi POST https://api.bunny.net/purge?url=<host><path>&async=false, 1 lượt/giây. Không thêm exactPath: tham số đó chỉ xoá bản desktop
  (site mẫu 27/10/2026). Purge 1 URL xoá mọi biến thể (WebP, mobile).
- --warm: purge xong path nào thì làm nóng ngay path đó ở trạm CDN khách chính dùng, bằng ua/accept của biến thể d và m trong site.json
  (accept có image/webp). Bunny không tách HTML theo Accept và giữ bản của lượt đầu sau purge, nên lượt đầu phải là bản WebP.
  Cần trong site.json: cdn_host (hostname pull zone, ví dụ <zone>.b-cdn.net), cdn_warm_ecs (danh sách dải ECS cho dig +subnet,
  chọn theo vùng của trạm cần làm nóng). Kiểm cdn-cachedat (giờ UTC, dạng 10/26/2026 17:15:55) ở 5 path đầu: phải sau giờ purge.
- Mã thoát 0 khi mọi purge, mọi lượt làm nóng (200) và mọi lượt kiểm đạt.
- Không purge toàn zone. Không in IP trạm. Key: biến BUNNY_API_KEY hoặc dòng cùng tên trong .agent-secrets/.env tìm ngược lên
  từ thư mục hiện tại, không thấy thì từ thư mục của script (đọc qua _cdn.secret của skill cdn-speed-setup), không in.
"""
import json, os, subprocess, sys, time, urllib.parse
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cdn-speed-setup', 'scripts'))
from _cdn import bn  # noqa: E402

a = sys.argv[1:]
f = os.environ.get('UCSS_SITE')
if '--site' in a:
    i = a.index('--site'); f = a[i + 1]; del a[i:i + 2]
apply, warm = '--apply' in a, '--warm' in a
S = json.load(open(f)) if f else {}
if '--host' in a:
    host = a[a.index('--host') + 1]
elif S:
    host = 'https://' + S['host']
else:
    sys.exit('thiếu --host hoặc --site <site.json> (UCSS_SITE)')
if warm and not (S.get('cdn_host') and S.get('cdn_warm_ecs') and S.get('ua') and S.get('accept')):
    sys.exit('--warm cần site.json có cdn_host, cdn_warm_ecs, ua, accept')
paths = [l.strip() for l in open(a[0]) if l.strip().startswith('/')]


# _cdn.secret tìm .agent-secrets/.env ngược lên từ thư mục hiện tại. Dưới launchd thư mục site có thể nằm ngoài repo:
# khi đó chuyển tới thư mục cha gần nhất của script có .agent-secrets, sau khi đã đọc paths.txt và site.json.
def up(d):
    while not os.path.isdir(os.path.join(d, '.agent-secrets')) and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    return d if os.path.isdir(os.path.join(d, '.agent-secrets')) else None


if apply and not os.environ.get('BUNNY_API_KEY') and not up(os.getcwd()):
    r = up(os.path.dirname(os.path.abspath(__file__)))
    if r:
        os.chdir(r)


def edge_ip():
    for e in S['cdn_warm_ecs']:
        r = subprocess.run(['dig', '+short', '@8.8.8.8', S['cdn_host'], 'A', f'+subnet={e}'], capture_output=True, text=True, timeout=20)
        ips = [x for x in r.stdout.split() if x.count('.') == 3 and x.replace('.', '').isdigit()]
        if ips:
            return ips[-1]
    return None


def get(path, ip, dev):
    hn = urllib.parse.urlparse(host).hostname
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-D', '-', '--max-time', '40', '--resolve', f'{hn}:443:{ip}',
                        '-A', S['ua'][dev] + ' wp-ucss-warm', '-H', f"Accept: {S['accept'][dev]}",
                        '-H', f"Accept-Language: {S.get('accept_language', 'en')}", '-H', 'Accept-Encoding: br, gzip',
                        host.rstrip('/') + path], capture_output=True, text=True)
    h = {}
    for l in r.stdout.splitlines():
        if l.startswith('HTTP/'):
            h['status'] = l.split()[1] if len(l.split()) > 1 else ''
        elif ':' in l:
            k, v = l.split(':', 1); h[k.strip().lower()] = v.strip()
    return h


ip = edge_ip() if warm and apply else None
if warm and apply and not ip:
    print('LỖI: không tra được IP trạm CDN, chỉ purge'); warm = False
ok = wok = chk = chk_ok = 0
for i, p in enumerate(paths):
    url = host.rstrip('/') + p
    if not apply:
        print('sẽ purge' + (' + làm nóng d, m' if warm else ''), url); ok += 1; continue
    t0 = time.time()
    c, j = bn('POST', '/purge?' + urllib.parse.urlencode({'url': url, 'async': 'false'}))
    ok += c in (200, 204)
    line = f'{c} {url}'
    if warm and c in (200, 204):
        for dev in ('d', 'm'):
            time.sleep(1)
            h = get(p, ip, dev)
            wok += h.get('status') == '200'
            line += f" {dev}={h.get('status', '-')}/{h.get('cdn-cache', '-')}"
        if i < 5:
            for dev in ('d', 'm'):
                time.sleep(1)
                h = get(p, ip, dev)
                chk += 1
                try:
                    at = datetime.strptime(h.get('cdn-cachedat', ''), '%m/%d/%Y %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()
                except ValueError:
                    at = 0
                good = h.get('cdn-cache') == 'HIT' and at >= t0 - 2
                chk_ok += good
                line += f" kiểm-{dev}={h.get('cdn-cache', '-')}{'' if good else '!'}"
    print(line)
    time.sleep(1)
msg = f"{'đã purge' if apply else 'DRY'} {ok}/{len(paths)} URL"
if warm and apply:
    msg += f", làm nóng {wok}/{2 * ok} lượt 200, kiểm cdn-cachedat {chk_ok}/{chk}"
print(msg + f" ({time.strftime('%F %T')})")
sys.exit(0 if ok == len(paths) and (not warm or not apply or (wok == 2 * ok and chk_ok == chk)) else 1)
