#!/usr/bin/env python3
"""test_map_diff.py (wp-ucss): cổng mất path và danh sách purge của map_diff.py.

Ca hỏng thật: site mẫu 27/10/2026 05:49, lượt kiểm bỏ qua 124 cặp, map mới mất 30 path mà vẫn được giao.
Fixture map-su-co/ là hai map thật của lượt đó, path đã đổi thành /p-NNN/.
"""
import os, subprocess, sys, tempfile
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
sys.exit(1 if bad else 0)
