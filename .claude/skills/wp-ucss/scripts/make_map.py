# make_map.py (wp-ucss): chọn path đã qua bộ kiểm, đặt tên file gọn theo nội dung, sinh map.php cho mu-plugin.
# python3 -I make_map.py <outDir> <deployDir>. Ghi <deployDir>/<md5 gộp>.<md5 gọn 8>.css, map.php, map.json (tóm tắt).
# Path vào map của file gộp H khi mọi lượt (path, biến thể) trỏ tới H đều có kết quả kiểm: không lỗi, không bỏ qua, đủ trạng thái,
# 0 lệch style, không mất font, không lệch animation, không lệch chiều cao trang. Thiếu một biến thể thì path đó giữ file gốc.
import collections, glob, hashlib, json, os, shutil, sys

out, dep = sys.argv[1], sys.argv[2]
os.makedirs(dep, exist_ok=True)
gen = {}
for f in glob.glob(f'{out}/pages/*.json'):
    r = json.load(open(f))
    if r.get('hash') and not r.get('err'):
        gen[(r['path'], r['dev'])] = r['hash']
ok_v, bad = {}, collections.Counter()
for f in glob.glob(f'{out}/verify/*.json'):
    r = json.load(open(f))
    k = (r['path'], r['dev'])
    why = None
    if r.get('err') or r.get('skip'):
        why = 'lỗi/bỏ qua'
    elif not r.get('states') or any(s is None for _, s in r['states']):
        why = 'thiếu trạng thái'
    elif any(s['n'] or s['lostFonts'] or s['animDiff'] or s['hDiff'] for _, s in r['states']):
        why = 'lệch'
    ok_v[k] = why is None
    if why:
        bad[why] += 1
paths = collections.defaultdict(lambda: collections.defaultdict(list))  # hash -> path -> [ok...]
for (p, d), h in gen.items():
    paths[h][p].append(ok_v.get((p, d), False))
files, summary = {}, []
for h, pp in sorted(paths.items()):
    src = f'{out}/reduced/{h}.css'
    good = sorted(p for p, oks in pp.items() if oks and all(oks))
    if not good or not os.path.exists(src):
        summary.append({'hash': h, 'paths': len(pp), 'ok': 0}); continue
    b = open(src, 'rb').read()
    name = f'{h}.{hashlib.md5(b).hexdigest()[:8]}.css'
    shutil.copyfile(src, f'{dep}/{name}')
    files[h] = {'f': name, 'p': good}
    summary.append({'hash': h, 'file': name, 'bytes': len(b), 'paths': len(pp), 'ok': len(good), 'thieu': sorted(set(pp) - set(good))[:20]})


def php_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


lines = ['<?php', '// wp-ucss map (sinh bởi make_map.py, không sửa tay). md5 file gộp => file gọn và các path đã qua bộ kiểm.', 'return array(',
         "\t'v' => " + php_str(os.environ.get('UCSS_VER', 'local')) + ',', "\t'files' => array("]
for h, e in sorted(files.items()):
    lines.append(f"\t\t{php_str(h)} => array( 'f' => {php_str(e['f'])}, 'p' => array( " + ', '.join(php_str(p) + ' => 1' for p in e['p']) + ' ) ),')
lines += ['\t),', ');', '']
open(f'{dep}/map.php', 'w').write('\n'.join(lines))
json.dump({'files': summary, 'verify_bad': bad}, open(f'{dep}/map.json', 'w'), ensure_ascii=False, indent=1)
tot_p = sum(len(e['p']) for e in files.values())
print(f'file gộp có bản gọn: {len(files)}/{len(paths)} | path trong map: {tot_p} | lượt kiểm không đạt: {dict(bad)}')
for s in summary:
    if s.get('ok', 0) < s['paths']:
        print('  thiếu', s['hash'][:8], f"{s.get('ok', 0)}/{s['paths']}", s.get('thieu', [])[:5])
