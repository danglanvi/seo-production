# test_make_map.py (wp-ucss): cổng của make_map.py. Fixture 2 file gộp: H1 có /a/ đạt mọi biến thể và /b/ lệch ở d; H2 có /c/ thiếu trạng thái.
# Cần: chỉ /a/ vào map, H2 không vào map, không có khoá all khi thiếu holdout, tên file gọn = <md5 gộp>.<md5 gọn 8>.css, map.php qua php -l (nếu máy có php).
# python3 -I test_make_map.py → in OK/SAI, mã 1 nếu có ca sai.
import hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
H1, H2 = '1' * 32, '2' * 32
tmp = tempfile.mkdtemp(prefix='wp-ucss-map-')
out, dep = f'{tmp}/out', f'{tmp}/dep'
for d in ('pages', 'verify', 'reduced'):
    os.makedirs(f'{out}/{d}')
st_ok = {'n': 0, 'lostFonts': [], 'animDiff': None, 'hDiff': None}
st_bad = dict(st_ok, n=3)
rows = [  # path, dev, hash, các trạng thái verify (None: không có file verify)
    ('/a/', 'm', H1, [['js', st_ok], ['menu', st_ok]]),
    ('/a/', 'd', H1, [['js', st_ok], ['hover1', st_ok]]),
    ('/b/', 'm', H1, [['js', st_ok]]),
    ('/b/', 'd', H1, [['js', st_ok], ['hover1', st_bad]]),
    ('/c/', 'm', H2, [['js', None]]),
    ('/c/', 'd', H2, None),
]
for p, dev, h, states in rows:
    name = f"{dev}_{p.strip('/')}.json"
    json.dump({'path': p, 'dev': dev, 'hash': h}, open(f'{out}/pages/{name}', 'w'))
    if states is not None:
        json.dump({'path': p, 'dev': dev, 'hash': h, 'states': states}, open(f'{out}/verify/{name}', 'w'))
for h in (H1, H2):
    open(f'{out}/reduced/{h}.css', 'w').write(f'/* {h[0]} */.a{{x:1}}')
r = subprocess.run([sys.executable, '-I', os.path.join(HERE, '..', 'make_map.py'), out, dep], capture_output=True, text=True, env=dict(os.environ, UCSS_VER='test'))

bad = 0
def ok(name, cond, more=''):
    global bad
    bad += not cond
    print('OK ' if cond else 'SAI', name, '' if cond else more)

ok('make_map.py chạy', r.returncode == 0, r.stderr[-400:])
t = open(f'{dep}/map.php').read() if os.path.exists(f'{dep}/map.php') else ''
m = re.findall(r"'([0-9a-f]{32})' => array\( 'f' => '([^']+)', 'p' => array\( (.*?) \) \),", t)
name1 = f"{H1}.{hashlib.md5(open(f'{out}/reduced/{H1}.css', 'rb').read()).hexdigest()[:8]}.css"
ok('chỉ H1 vào map', [x[0] for x in m] == [H1], t)
ok('chỉ path /a/ của H1 vào map', bool(m) and re.findall(r"'([^']+)' => 1", m[0][2]) == ['/a/'], t)
ok('tên file gọn theo md5 nội dung, đã chép', bool(m) and m[0][1] == name1 and os.path.exists(f'{dep}/{name1}'))
ok('H2 không có file gọn trong deploy', not any(f.startswith(H2) for f in os.listdir(dep)))
s = json.load(open(f'{dep}/map.json'))
ok('map.json đếm lượt kiểm không đạt', s['verify_bad'] == {'lệch': 1, 'thiếu trạng thái': 1}, s['verify_bad'])
if shutil.which('php'):
    p = subprocess.run(['php', '-l', f'{dep}/map.php'], capture_output=True, text=True)
    ok('php -l map.php', p.returncode == 0, p.stdout + p.stderr)
else:
    print('BỎ php -l map.php: máy không có php')
ok('không có holdout: map không có khoá all', "'all'" not in t)


# Khoá 'all' (site agency mẫu 27/10/2026: holdout 12 bài × 4 biến thể đạt rồi mới phủ cả nhóm bài). Fixture: H1 có /a/ đạt m, d;
# holdout 3 bài ngoài tập dựng, HOLDOUT_MIN=3. Mỗi ca đổi đúng một điều kiện.
def run_all(name, n_ho=3, lech=False, file_khac=False, trong_tap=False, hmin='3'):
    d = tempfile.mkdtemp(prefix='wp-ucss-all-')
    o, ho, dp = f'{d}/out', f'{d}/out-ho', f'{d}/dep'
    for x in ('pages', 'verify', 'reduced'):
        os.makedirs(f'{o}/{x}'); os.makedirs(f'{ho}/{x}')
    for dev in ('m', 'd'):
        json.dump({'path': '/a/', 'dev': dev, 'hash': H1}, open(f'{o}/pages/{dev}_a.json', 'w'))
        json.dump({'path': '/a/', 'dev': dev, 'hash': H1, 'states': [['js', st_ok]]}, open(f'{o}/verify/{dev}_a.json', 'w'))
    open(f'{o}/reduced/{H1}.css', 'w').write('.a{x:1}')
    open(f'{ho}/reduced/{H1}.css', 'w').write('.a{x:2}' if file_khac else '.a{x:1}')
    for i in range(n_ho):
        p = '/a/' if trong_tap and i == 0 else f'/ho-{i}/?nc=1'
        for dev in ('m', 'd'):
            stt = st_bad if lech and i == 0 and dev == 'd' else st_ok
            json.dump({'path': p, 'dev': dev, 'hash': H1, 'states': [['js', stt]]}, open(f'{ho}/verify/{dev}_ho{i}.json', 'w'))
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, '..', 'make_map.py'), o, dp], capture_output=True, text=True,
                       env=dict(os.environ, UCSS_VER='test', HOLDOUT_MIN=hmin))
    m = open(f'{dp}/map.php').read() if r.returncode == 0 else ''
    shutil.rmtree(d)
    return r, m


r, m = run_all('đủ')
ok('holdout đủ, đạt, file trùng byte: ghi all', r.returncode == 0 and f"'all' => array( '{H1}' => 1 )" in m, r.stdout + r.stderr)
if shutil.which('php'):
    open(f'{tmp}/all.php', 'w').write(m)
    p = subprocess.run(['php', '-r', '$m = include $argv[1]; exit(isset($m["all"]["' + H1 + '"]) && isset($m["files"]["' + H1 + '"]) ? 0 : 1);', f'{tmp}/all.php'], capture_output=True, text=True)
    ok('php đọc được map có khoá all', p.returncode == 0, p.stdout + p.stderr)
sys.path.insert(0, os.path.join(HERE, '..'))
import map_diff  # noqa: E402
open(f'{tmp}/all.php', 'w').write(m)
ok('map_diff.parse vẫn đọc phần files của map có all', list(map_diff.parse(f'{tmp}/all.php')) == [H1])
ok('file gọn holdout khác byte: không all', "'all'" not in run_all('khác', file_khac=True)[1])
ok('một lượt holdout lệch: không all', "'all'" not in run_all('lệch', lech=True)[1])
ok('holdout ít hơn HOLDOUT_MIN: không all', "'all'" not in run_all('ít', hmin='4')[1])
ok('holdout trùng path tập dựng: không all', "'all'" not in run_all('trùng', trong_tap=True)[1])
shutil.rmtree(tmp)
sys.exit(1 if bad else 0)
