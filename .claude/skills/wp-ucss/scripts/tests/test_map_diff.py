#!/usr/bin/env python3
"""test_map_diff.py (wp-ucss): cổng mất path và danh sách purge của map_diff.py.

Ca hỏng thật: site mẫu 27/10/2026 05:49, lượt kiểm bỏ qua 124 cặp, map mới mất 30 path mà vẫn được giao.
Fixture map-su-co/ là hai map thật của lượt đó, path đã đổi thành /p-NNN/.
"""
import json, os, subprocess, sys, tempfile
T = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(T); F = os.path.join(T, 'fixtures', 'map-su-co')
sys.path.insert(0, S)
import map_diff as md  # noqa: E402

bad = 0
def ok(name, cond):
    global bad
    bad += 0 if cond else 1
    print('OK ' if cond else 'SAI', name)

old, new = md.parse(os.path.join(F, 'site.php')), md.parse(os.path.join(F, 'moi.php'))
lost, paths = md.diff(old, new, 3)
ok('ca 27/10: mất 30 path thì dừng', len(lost) == 30 and paths is None)
lost, paths = md.diff(old, new, 40)
ok('MAX_LOST=40: đi tiếp, path mất nằm trong danh sách purge', paths is not None and lost <= set(paths))
ok('map giống nhau: 0 path purge', md.diff(old, old, 3)[1] == [])
h = next(iter(old)); chg = dict(old); chg[h] = ('khac.css', old[h][1])
ok('file gọn đổi: purge mọi path của file gộp đó', set(md.diff(old, chg, 3)[1]) == old[h][1])
with tempfile.TemporaryDirectory() as d:
    env = dict(os.environ, MAX_LOST='3')
    r = subprocess.run([sys.executable, '-I', os.path.join(S, 'map_diff.py'), os.path.join(F, 'site.php'), os.path.join(F, 'moi.php'), d], env=env, capture_output=True, text=True)
    ok('CLI: mã 1 và không ghi file purge khi dừng', r.returncode == 1 and 'DỪNG' in r.stdout and not os.listdir(d))
    r = subprocess.run([sys.executable, '-I', os.path.join(S, 'map_diff.py'), os.path.join(F, 'site.php'), os.path.join(F, 'site.php'), d], env=env, capture_output=True, text=True)
    ok('CLI: map không đổi ghi file purge rỗng', r.returncode == 0 and open(os.path.join(d, 'purge_paths.txt')).read() == '')
# Cổng theo cặp (path, biến thể): dữ liệu giả lập. Bản gốc của cổng (pair_check.py) chạy làm cổng giao 2 lần trên site agency mẫu 27/10/2026,
# cả 2 lần 0 cặp mất. Chưa có ca dừng thật, nên test dựng map site và map mới bằng tay.
H1, H2, H3 = '1' * 32, '2' * 32, '3' * 32
site_m = {H1: ('h1.css', {'/a/', '/b/'}), H2: ('h2.css', {'/a/', '/b/'})}
moi_m = {H1: ('h1.css', {'/a/', '/b/'}), H2: ('h2.css', {'/b/'})}  # /a/ mất bản H2 (biến thể q) nhưng vẫn còn trong map qua H1
inv_rows = [('/a/', 'm', H1), ('/a/', 'q', H2), ('/b/', 'm', H1), ('/b/', 'q', H2), ('/b/', 'p', H3), ('/c/', 'm', H1)]
lost, paths = md.diff(site_m, moi_m, 3)
ok('giả lập: cổng path không thấy (0 path mất)', not lost and paths is not None)

def php(m, all_=()):
    s = "<?php\nreturn array(\n\t'v' => 't',\n\t'files' => array(\n"
    for h, (f, ps) in m.items():
        s += f"\t\t'{h}' => array( 'f' => '{f}', 'p' => array( " + ', '.join(f"'{p}' => 1" for p in sorted(ps)) + ' ) ),\n'
    s += '\t),\n' + ("\t'all' => array( " + ', '.join(f"'{h}' => 1" for h in all_) + ' ),\n' if all_ else '') + ');\n'
    return s

with tempfile.TemporaryDirectory() as d:
    inv = os.path.join(d, 'inv.jsonl')
    open(inv, 'w').write(''.join(json.dumps({'path': p, 'v': v, 'code': 200, 'css': [h]}) + '\n' for p, v, h in inv_rows))
    fs, fm = os.path.join(d, 'site.php'), os.path.join(d, 'moi.php')
    open(fs, 'w').write(php(site_m, [H1])); open(fm, 'w').write(php(moi_m))
    ok('giả lập: parse đọc map tự dựng', md.parse(fs) == site_m and md.parse_all(fs) == {H1} and md.parse_all(fm) == set())
    tong, mat, ho = md.pairs(inv, md.parse(fs), md.parse(fm))
    ok('giả lập: 1 cặp mất (/a/ q), 1 cặp chưa có (/b/ p), /c/ ngoài map không tính', tong == 6 and mat == [f'/a/ q {H2[:8]}'] and ho == [f'/b/ p {H3[:8]}'])
    out = os.path.join(d, 'r'); os.mkdir(out)
    r = subprocess.run([sys.executable, '-I', os.path.join(S, 'map_diff.py'), fs, fm, out, '--inv', inv], capture_output=True, text=True, env=dict(os.environ, MAX_LOST='3'))
    ok('CLI --inv: mất cặp thì mã 1, không ghi file purge', r.returncode == 1 and 'DỪNG: map mới mất CSS gọn ở 1 cặp' in r.stdout and not os.listdir(out))
    r = subprocess.run([sys.executable, '-I', os.path.join(S, 'map_diff.py'), fs, fm, out, '--inv', inv], capture_output=True, text=True, env=dict(os.environ, MAX_LOST='3', MAX_LOST_PAIRS='1'))
    ok('CLI --inv MAX_LOST_PAIRS=1: đi tiếp, báo cặp mất và bỏ khoá all', r.returncode == 0 and 'CẢNH BÁO map mới bỏ khoá all' in r.stdout and 'CẢNH BÁO chưa có CSS gọn /b/ p' in r.stdout and 'CẢNH BÁO mất CSS gọn /a/ q' in r.stdout)
    r = subprocess.run([sys.executable, '-I', os.path.join(S, 'map_diff.py'), fs, fm, out], capture_output=True, text=True, env=dict(os.environ, MAX_LOST='3'))
    ok('CLI không có --inv: chạy như bản cũ', r.returncode == 0 and 'cặp trong inventory' not in r.stdout)
sys.exit(1 if bad else 0)
