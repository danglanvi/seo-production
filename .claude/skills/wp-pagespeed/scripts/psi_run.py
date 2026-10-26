# Đo PSI v5 cho danh sách URL: làm nóng cache bằng UA Lighthouse, rồi chạy N lượt cho mỗi URL x thiết bị.
# python3 -I "$WPS/scripts/psi_run.py" --urls urls.tsv --out <thư mục> [--runs 3] [--devices mobile,desktop] [--env <đường dẫn .env>]
#   [--categories performance,accessibility,best-practices,seo,agentic-browsing]  (mặc định chỉ performance)
#   [--jobs 2] [--dry-run] [--detach] [--fg-ok]
# urls.tsv: mỗi dòng "tên<TAB>url". File đã có (>10 KB) thì bỏ qua, nên chạy lại chỉ đo phần thiếu.
# Key: biến môi trường PAGESPEED_API_KEY, hoặc dòng PAGESPEED_API_KEY trong .agent-secrets/.env tìm từ thư mục hiện tại trở lên. Không ghi key ra file hay log.
# --jobs N: số lượt PSI chạy đồng thời (mặc định 2, theo luật tối đa 2 request đồng thời lên site). Lượt xếp xen kẽ theo vòng, URL, thiết bị.
#   N = 3 hoặc 4 chỉ khi cache_variants.py báo HIT đủ 5 biến thể và workstream cho phép; thêm --jobs-ok để xác nhận. Tối đa 4.
# --dry-run: in kế hoạch (số lượt cần đo, thời gian ước tính), không gọi API.
# Chạy tiền cảnh lâu hơn --max-fg-min phút (mặc định 8) thì script từ chối, mã thoát 5. Chọn một trong hai:
#   --detach: chạy nền, in đường dẫn log và file trạng thái <out>/PSI_STATE.txt, rồi thoát ngay. Đợi bằng lệnh ngắn: cat <out>/PSI_STATE.txt
#   --fg-ok: tự chịu trách nhiệm chạy tiền cảnh (chỉ khi lệnh đã nằm trong tiến trình nền).
# PSI_STATE.txt: dòng "RUNNING ..." lúc bắt đầu, dòng "DONE lỗi=<n> exit=<mã>" khi xong. Chỉ ghi file này trong <out>, không xoá file nào.
# Mã thoát: 0 xong, 1 còn lượt lỗi, 2 sai tham số, 5 bị từ chối chạy tiền cảnh.
import argparse, json, math, os, re, subprocess, sys, threading, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser(description='Đo PSI v5 cho danh sách URL x thiết bị x lượt, chạy song song có giới hạn (--jobs). Mô tả đầy đủ ở đầu file script.')
ap.add_argument('--urls', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--runs', type=int, default=3)
ap.add_argument('--devices', default='mobile,desktop')
ap.add_argument('--env')
ap.add_argument('--categories', default='performance')
ap.add_argument('--jobs', type=int, default=2)
ap.add_argument('--jobs-ok', action='store_true', help='xác nhận nâng --jobs lên 3 hoặc 4')
ap.add_argument('--dry-run', action='store_true')
ap.add_argument('--detach', action='store_true')
ap.add_argument('--fg-ok', action='store_true')
ap.add_argument('--max-fg-min', type=float, default=8.0)
ap.add_argument('--est-sec', type=float, default=30.0, help='ước thời gian một lượt PSI (giây)')
ap.add_argument('--sleep', type=float, default=3.0, help='nghỉ sau mỗi lượt của mỗi worker (giây)')
ap.add_argument('--retry-wait', type=float, default=20.0)
ap.add_argument('--no-warm', action='store_true')
ap.add_argument('--api-base', default='https://www.googleapis.com/pagespeedonline/v5/runPagespeed', help='chỉ đổi khi test với server giả')
a = ap.parse_args()
if a.jobs < 1 or a.jobs > 4:
    sys.exit('--jobs phải từ 1 đến 4')
if a.jobs > 2 and not a.jobs_ok:
    ap.error('--jobs %d vượt mức 2 request đồng thời lên một site. Chỉ nâng khi cache_variants.py báo HIT đủ 5 biến thể và workstream cho phép; thêm --jobs-ok để xác nhận' % a.jobs)


def find_key():
    if os.environ.get('PAGESPEED_API_KEY'):
        return os.environ['PAGESPEED_API_KEY']
    paths = [a.env] if a.env else []
    d = os.getcwd()
    while True:
        paths.append(os.path.join(d, '.agent-secrets', '.env'))
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    for p in paths:
        if p and os.path.exists(p):
            for l in open(p):
                m = re.match(r"\s*(export\s+)?PAGESPEED_API_KEY\s*=\s*(.*)$", l)
                if m:
                    return m.group(2).strip().strip('"').strip("'")
    sys.exit('Không thấy PAGESPEED_API_KEY')


urls = [l.rstrip('\n').split('\t')[:2] for l in open(a.urls) if l.strip() and not l.startswith('#')]
# LiteSpeed (cache-drop_qs) và nhiều plugin cache bỏ các tham số này khỏi khoá cache, còn theme hoặc plugin SEO hay gắn noindex,
# bỏ canonical cho URL có query. Lượt warm hoặc PSI đầu tiên khi cache trống sẽ ghi bản noindex vào cache của URL sạch.
DROP_QS = re.compile(r'(^|&)(utm_[^=&]*|fbclid|gclid|gbraid|wbraid|msclkid|ttclid|_ga|_gl)=', re.I)
bad = [u for _, u in urls if DROP_QS.search(urllib.parse.urlsplit(u).query)]
if bad:
    sys.exit('Không đo URL có utm_*, fbclid, gclid, _ga: dùng URL sạch hoặc tham số nằm trong cache-exc_qs. ' + ' '.join(bad[:5]))
devs = a.devices.split(',')
UA = {'mobile': 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36 Chrome-Lighthouse',
      'desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Chrome-Lighthouse'}
bad_dev = [d for d in devs if d not in UA]
if bad_dev:
    sys.exit('Thiết bị không hợp lệ: ' + ','.join(bad_dev))

# Danh sách lượt xếp xen kẽ: vòng ngoài cùng, rồi URL, rồi thiết bị. Số đo không lệch theo giờ giữa các URL.
tasks = []
for r in range(1, a.runs + 1):
    for n, u in urls:
        for st in devs:
            out = os.path.join(a.out, f"{n}_{st}_run{r}.json")
            if not (os.path.exists(out) and os.path.getsize(out) > 10000):
                tasks.append((r, n, u, st, out))
est_min = math.ceil(len(tasks) / a.jobs) * (a.est_sec + a.sleep) / 60.0
print(f"kế hoạch: {len(tasks)} lượt cần đo trong {len(urls) * len(devs) * a.runs}, --jobs {a.jobs}, ước tính {est_min:.1f} phút", flush=True)
if a.dry_run:
    for r, n, u, st, out in tasks[:20]:
        print(f"  run{r} {n} {st}")
    if len(tasks) > 20:
        print(f"  ... còn {len(tasks) - 20} lượt")
    print('DRY-RUN: chưa gọi API, chưa ghi file.')
    sys.exit(0)

state = os.path.join(a.out, 'PSI_STATE.txt')


def write_state(text):
    with open(state, 'w') as f:
        f.write(text + '\n')


if est_min > a.max_fg_min and not (a.detach or a.fg_ok):
    print(f"Từ chối chạy tiền cảnh: ước tính {est_min:.1f} phút, vượt {a.max_fg_min:g} phút. "
          "Thêm --detach để chạy nền rồi đợi bằng lệnh ngắn (cat <out>/PSI_STATE.txt), hoặc --fg-ok nếu lệnh đã nằm trong tiến trình nền.", file=sys.stderr)
    sys.exit(5)

key = find_key()
os.makedirs(a.out, exist_ok=True)

if a.detach:
    log = os.path.join(a.out, 'psi_run.log')
    argv = [x for x in sys.argv[1:] if x != '--detach'] + ['--fg-ok']
    write_state(f"RUNNING start={time.strftime('%Y-%m-%dT%H:%M:%S')} tasks={len(tasks)} est_min={est_min:.1f}")
    with open(log, 'a') as lf:
        proc = subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)] + argv, stdout=lf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    print(f"Đã chạy nền pid={proc.pid}. Log: {log}. Trạng thái: {state} (dòng DONE khi xong).", flush=True)
    sys.exit(0)

write_state(f"RUNNING start={time.strftime('%Y-%m-%dT%H:%M:%S')} tasks={len(tasks)} pid={os.getpid()}")
lock = threading.Lock()


def say(msg):
    with lock:
        print(msg.replace(key, '<KEY>'), flush=True)


if not a.no_warm:
    for n, u in urls:
        for st in devs:
            try:
                urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA[st], 'Accept': 'text/html,application/xhtml+xml,image/avif,image/webp,*/*'}), timeout=60).read()
            except Exception as e:
                say(f'warm lỗi {n} {st} {str(e)[:80]}')
    say('warm xong')


def work(t):
    r, n, u, st, out = t
    q = urllib.parse.urlencode([('url', u), ('strategy', st)] + [('category', c) for c in a.categories.split(',')] + [('locale', 'vi'), ('key', key)])
    ok = False
    for attempt in (1, 2, 3):
        t0 = time.time()
        try:
            with urllib.request.urlopen(a.api_base + '?' + q, timeout=180) as resp:
                data = resp.read()
            j = json.loads(data)
            if 'lighthouseResult' not in j:
                raise RuntimeError('không có lighthouseResult')
            s = data.decode('utf-8')
            assert key not in s
            open(out, 'w').write(s)
            sc = ' '.join(f"{k}={v.get('score')}" for k, v in j['lighthouseResult']['categories'].items())
            say(f"{time.strftime('%H:%M:%S')} {n} {st} run{r} {sc} {time.time()-t0:.0f}s")
            ok = True
            break
        except Exception as e:
            say(f"{time.strftime('%H:%M:%S')} {n} {st} run{r} lần {attempt} lỗi: {str(e)[:160]}")
            if attempt < 3:
                time.sleep(a.retry_wait)
    time.sleep(a.sleep)
    return ok


with ThreadPoolExecutor(max_workers=a.jobs) as ex:
    results = list(ex.map(work, tasks))
fail = sum(1 for ok in results if not ok)
code = 1 if fail else 0
say(f"PSI_DONE lỗi={fail}")
write_state(f"DONE lỗi={fail} exit={code} end={time.strftime('%Y-%m-%dT%H:%M:%S')}")
sys.exit(code)
