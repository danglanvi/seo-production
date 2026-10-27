#!/usr/bin/env python3
"""team_accounts_check.py (wp-security-hardening): kiểm tài khoản team + 2FA trên một site sau khi cài mẫu templates/tai-khoan-team/.
Ba phần: quyền role (t.php chạy bằng wp eval-file), đăng nhập thật bằng mã dự phòng (--http), REST bằng app password (--rest).
Tạo user thử zz_* rồi xoá ở cuối. Production không publish bài thử: chỉ tạo nháp rồi xoá. Chỉ in PASS/FAIL, không in mật khẩu, mã, slug.

Dùng: python3 -I team_accounts_check.py --cfg <site.json> [--http] [--rest] [--out <file evidence>]
site.json:
  {"ten": "example-stg", "ssh": "example-vps", "path": "/www/wwwroot/stg.example.vn",
   "wp": "cd /tmp && sudo -u www HOME=/tmp/wpcli-home /usr/local/lsws/lsphp83/bin/php /usr/local/bin/wp --path={path}",
   "base": "https://stg.example.vn", "prod": false,
   "login_slug": {"env_file": "<file trong .agent-secrets>", "key": "WP_LOGIN_SLUG"}   hoặc {"option": "whl_page"},
   "basic_auth": {"env_file": "...", "user_key": "STG_BASIC_USER", "pass_key": "STG_BASIC_PASS"},   (tuỳ chọn)
   "host_header": "stg.example.vn"}   (tuỳ chọn, khi gọi staging qua tunnel 127.0.0.1)
"ssh" là alias trong ~/.ssh/config, hoặc mảng lệnh đầy đủ ["ssh", "-i", "<key>", "-p", "2210", "user@host"].
Mã thoát 0 khi mọi dòng PASS.
"""
import base64, http.cookiejar, json, os, re, secrets, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TPHP = os.path.join(HERE, '..', 'templates', 'tai-khoan-team', 't.php')
a = sys.argv[1:]
if '--cfg' not in a:
    sys.exit(__doc__)
C = json.load(open(a[a.index('--cfg') + 1], encoding='utf-8'))
OUT = a[a.index('--out') + 1] if '--out' in a else None
SSH = (['ssh', '-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR', C['ssh']] if isinstance(C['ssh'], str)
       else list(C['ssh'][:1]) + ['-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR'] + list(C['ssh'][1:]))
WP = C['wp'].format(path=C['path'])
BASE = C['base'].rstrip('/')
PROD = bool(C.get('prod'))
tag = secrets.token_hex(3)
remote = f'/tmp/zz-t-{tag}.php'
results = []


def secret_dir():
    d = os.path.abspath(os.getcwd())
    while not os.path.isdir(os.path.join(d, '.agent-secrets')):
        if os.path.dirname(d) == d:
            sys.exit('không thấy thư mục .agent-secrets từ thư mục hiện tại đi lên')
        d = os.path.dirname(d)
    return os.path.join(d, '.agent-secrets')


def env(fname):
    d = {}
    for line in open(os.path.join(secret_dir(), fname), encoding='utf-8'):
        m = re.match(r'^([A-Za-z0-9_]+)=(.*)$', line.strip())
        if m:
            d[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return d


def ok(label, cond):
    results.append(('PASS ' if cond else 'FAIL ') + label)
    print(results[-1], flush=True)


def ssh(cmd, stdin=''):
    return subprocess.run(SSH + [cmd], input=stdin, capture_output=True, text=True).stdout


def act(name, **kw):
    out = ssh(WP + f' eval-file {remote} 2>/dev/null', json.dumps(dict(act=name, tag=tag, prod=PROD, **kw)))
    for line in out.splitlines():
        if line.startswith(('PASS ', 'FAIL ')):
            results.append(line)
            print(line, flush=True)
    return out


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kw):
        return None


class R:
    def __init__(self, status, text, headers):
        self.status_code, self.text, self.headers = status, text, headers

    def json(self):
        return json.loads(self.text)


class Session:
    """Phiên HTTP bằng thư viện chuẩn: giữ cookie, không tự theo redirect, Basic Auth và Host tuỳ chọn."""

    def __init__(self, basic=None, test_cookie=False):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)
        self.h = {'User-Agent': 'Mozilla/5.0 (Macintosh) team-accounts-check'}
        if C.get('host_header'):
            self.h['Host'] = C['host_header']
        if basic:
            self.h['Authorization'] = 'Basic ' + base64.b64encode(f'{basic[0]}:{basic[1]}'.encode()).decode()
        if test_cookie:
            host = urllib.parse.urlparse(BASE).hostname
            self.jar.set_cookie(http.cookiejar.Cookie(0, 'wordpress_test_cookie', 'WP Cookie check', None, False, host, False, False,
                                                      '/', True, False, None, False, None, None, {}))

    def _do(self, method, url, data=None, js=None, auth=None, allow_redirects=False, timeout=60):
        h = dict(self.h)
        body = None
        if js is not None:
            body = json.dumps(js).encode(); h['Content-Type'] = 'application/json'
        elif data is not None:
            body = urllib.parse.urlencode(data).encode(); h['Content-Type'] = 'application/x-www-form-urlencoded'
        if auth:
            h['Authorization'] = 'Basic ' + base64.b64encode(f'{auth[0]}:{auth[1]}'.encode()).decode()
        try:
            with self.op.open(urllib.request.Request(url, data=body, headers=h, method=method), timeout=timeout) as r:
                return R(r.status, r.read().decode('utf-8', 'replace'), r.headers)
        except urllib.error.HTTPError as e:
            return R(e.code, e.read().decode('utf-8', 'replace'), e.headers)

    def get(self, url, **kw):
        return self._do('GET', url, **kw)

    def post(self, url, data=None, json=None, **kw):
        return self._do('POST', url, data=data, js=json, **kw)


def session():
    basic = None
    if C.get('basic_auth'):
        b = C['basic_auth']; e = env(b['env_file'])
        basic = (e[b['user_key']], e[b['pass_key']])
    return Session(basic, test_cookie=True)


def login_slug():
    ls = C.get('login_slug') or {}
    if ls.get('env_file'):
        return env(ls['env_file'])[ls['key']]
    if ls.get('option'):
        return ssh(WP + f" option get {ls['option']} 2>/dev/null").strip()
    return 'wp-login.php'


def hidden(html):
    d = {}
    for m in re.finditer(r'<input[^>]+type="hidden"[^>]*>', html):
        n, v = re.search(r'name="([^"]+)"', m.group(0)), re.search(r'value="([^"]*)"', m.group(0))
        if n:
            d[n.group(1)] = v.group(1) if v else ''
    return d


def form_action(html):
    m = re.search(r'<form[^>]+id="loginform"[^>]*>', html)
    x = re.search(r'action="([^"]+)"', m.group(0)) if m else None
    return re.sub(r'^https?://[^/]+', BASE, x.group(1).replace('&amp;', '&')) if x else None


def admin_ok(s):
    r = s.get(BASE + '/wp-admin/', allow_redirects=False, timeout=90)
    return r.status_code == 200 and 'wpadminbar' in r.text


try:
    ssh(f'cat > {remote} && chmod 644 {remote}', open(TPHP, encoding='utf-8').read())
    pw = secrets.token_urlsafe(20)
    act('setup', pw=pw)
    act('unit')

    if '--http' in a:
        codes = json.loads(re.search(r'\{"codes".*\}', act('codes')).group(0))['codes']
        slug = login_slug().strip('/')
        login_url = f'{BASE}/{slug}' if slug.endswith('.php') else f'{BASE}/{slug}/'
        if not PROD:
            s = session()
            s.get(login_url, timeout=60)
            s.post(login_url, data={'log': f'zz_tw_{tag}', 'pwd': 'sai-' + pw, 'wp-submit': 'Log In', 'testcookie': '1'}, allow_redirects=False, timeout=60)
            ok('sai mật khẩu không vào được wp-admin', not admin_ok(s))
        s = session()
        s.get(login_url, timeout=60)
        r = s.post(login_url, data={'log': f'zz_tw_{tag}', 'pwd': pw, 'wp-submit': 'Log In', 'redirect_to': BASE + '/wp-admin/', 'testcookie': '1'}, allow_redirects=False, timeout=60)
        on2fa = r.status_code == 200 and 'two-factor-backup-code' in r.text and 'wp-auth-nonce' in r.text
        ok('đúng mật khẩu thì hiện màn nhập mã 2FA' + ('' if on2fa else f' [HTTP {r.status_code}]'), on2fa)
        ok('chưa nhập mã thì chưa vào được wp-admin', not admin_ok(s))
        if on2fa:
            html = r.text
            r2 = s.post(form_action(html), data={**hidden(html), 'two-factor-backup-code': '00000000'}, allow_redirects=False, timeout=60)
            ok('mã sai bị từ chối', not admin_ok(s))
            html = r2.text if 'wp-auth-nonce' in r2.text else html
            time.sleep(5)  # Two Factor bắt chờ tăng dần sau mỗi lần nhập sai
            s.post(form_action(html), data={**hidden(html), 'two-factor-backup-code': codes[0]}, allow_redirects=False, timeout=60)
            ok('mã đúng thì vào wp-admin (200, có thanh admin)', admin_ok(s))

    if '--rest' in a:
        cred = json.loads(re.search(r'\{"login".*\}', act('apppw')).group(0))
        api = BASE + '/wp-json/wp/v2'
        s = Session()
        me = s.get(api + '/users/me?context=edit', auth=(cred['login'], cred['pw']), timeout=60)
        ok('REST app password của user có 2FA: users/me 200, role Người đăng bài', me.status_code == 200 and 'team_writer' in me.json().get('roles', []))
        bad = s.get(api + '/users/me', auth=(cred['login'], pw), timeout=60)
        ok('REST bằng mật khẩu đăng nhập bị chặn (401)', bad.status_code == 401)
        r = s.post(api + '/posts', auth=(cred['login'], cred['pw']), json={'title': f'zz test {tag}', 'content': '<p>test</p>', 'status': 'draft'}, timeout=60)
        byline = int(ssh(WP + ' eval "echo TEAM_BYLINE_ID;" 2>/dev/null').strip() or 0)
        ok('REST tạo bài nháp: 201, tác giả là tài khoản team', r.status_code == 201 and r.json().get('author') == byline)
        if r.status_code == 201:
            pid = r.json()['id']
            u = s.post(f'{api}/posts/{pid}', auth=(cred['login'], cred['pw']), json={'title': f'zz test {tag} sửa'}, timeout=60)
            ok('REST sửa bài đứng tên team: 200', u.status_code == 200)
            pg = s.post(api + '/pages', auth=(cred['login'], cred['pw']), json={'title': f'zz test {tag}', 'status': 'draft'}, timeout=60)
            ok('REST tạo page bị chặn (403)', pg.status_code == 403)
except Exception as e:  # lỗi harness vẫn phải dọn user thử
    ok(f'harness chạy hết (lỗi {type(e).__name__})', False)
finally:
    act('cleanup')
    ssh(f'rm -f {remote}')
    fails = [x for x in results if x.startswith('FAIL')]
    line = f"== {C.get('ten', BASE)}: {len(results) - len(fails)} PASS, {len(fails)} FAIL"
    print(line)
    if OUT:
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(f"## {time.strftime('%d/%m/%Y %H:%M')} {' '.join(x for x in a if x.startswith('--') and x not in ('--cfg', '--out'))}\n" + '\n'.join(results) + f'\n{line}\n')
    sys.exit(1 if fails else 0)
