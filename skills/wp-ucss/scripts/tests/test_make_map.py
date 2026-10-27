# test_make_map.py (wp-ucss): cổng của make_map.py. Fixture 2 file gộp: H1 có /a/ đạt mọi biến thể và /b/ lệch ở d; H2 có /c/ thiếu trạng thái.
# Cần: chỉ /a/ vào map, H2 không vào map, tên file gọn = <md5 gộp>.<md5 gọn 8>.css, map.php qua php -l (nếu máy có php).
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
shutil.rmtree(tmp)
sys.exit(1 if bad else 0)
