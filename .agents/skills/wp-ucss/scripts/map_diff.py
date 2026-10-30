#!/usr/bin/env python3
"""map_diff.py (wp-ucss): so map trên site với map mới, chặn map làm mất path, ghi path cần purge.

Dùng: python3 -I map_diff.py <map_site.php> <map_moi.php> <thư mục ra> [--inv <inv.jsonl>]   (env MAX_LOST mặc định 3, MAX_LOST_PAIRS mặc định 0)
Ghi <thư mục ra>/purge_paths.txt và purge-groups.txt (12 path mỗi nhóm). Mã 1 khi map mới mất quá MAX_LOST path,
hoặc (khi có --inv) mất quá MAX_LOST_PAIRS cặp (path, biến thể) mà path vẫn còn trong map.
"""
import json
import os
import re
import sys


def parse(f):
    try:
        t = open(f, encoding='utf-8').read()
    except OSError:
        return {}
    out = {}
    for m in re.finditer(r"'([0-9a-f]{32})' => array\( 'f' => '([^']+)', 'p' => array\( (.*?) \) \),", t):
        out[m.group(1)] = (m.group(2), set(re.findall(r"'([^']+)' => 1", m.group(3))))
    return out


def parse_all(f):
    # Khoá 'all' của make_map.py: md5 file gộp phủ cả nhóm bài viết.
    try:
        m = re.search(r"'all' => array\( (.*?) \),", open(f, encoding='utf-8').read())
    except OSError:
        return set()
    return set(re.findall(r"'([0-9a-f]{32})' => 1", m.group(1))) if m else set()


def pairs(inv, old, new):
    # Cổng theo cặp (path, biến thể), theo file gộp trang đang phục vụ (inventory). MAX_LOST đếm path, nên không thấy path
    # còn trong map ở biến thể này mà mất CSS gọn ở biến thể khác (site agency mẫu 27/10/2026, kiểm độc lập bắt 3 path).
    # mat: cặp có CSS gọn ở map site, mất ở map mới, path vẫn còn trong map mới. ho: cặp chưa có CSS gọn ở cả hai map, path có trong map mới.
    con = set().union(*[v[1] for v in new.values()]) if new else set()
    mat, ho, tong = [], [], 0
    for line in open(inv, encoding='utf-8'):
        r = json.loads(line)
        hs = set(r.get('css') or [])
        if r.get('code') != 200 or len(hs) != 1:
            continue
        h, p, v = hs.pop(), r['path'], r['v']
        tong += 1
        a, b = p in old.get(h, ('', ()))[1], p in new.get(h, ('', ()))[1]
        if not b and p in con:
            (mat if a else ho).append(f'{p} {v} {h[:8]}')
    return tong, mat, ho


def diff(old, new, max_lost):
    # Cổng: map mới không được làm mất path đang có CSS gọn. Site mẫu 27/10/2026: lượt kiểm bỏ qua 124 cặp, map mất 30 path vẫn được giao.
    lost = set().union(*[v[1] for v in old.values()]) - set().union(*[v[1] for v in new.values()])
    if len(lost) > max_lost:
        return lost, None
    changed = set()
    for h in set(old) | set(new):
        o, n = old.get(h), new.get(h)
        if o == n:
            continue
        po = o[1] if o else set()
        pn = n[1] if n else set()
        if o and n and o[0] != n[0]:
            changed |= po | pn      # file gọn đổi: mọi path của file gộp đó
        else:
            changed |= po ^ pn      # path vào hoặc ra khỏi map
    return lost, sorted(changed)


def main(argv):
    inv = None
    if len(argv) == 6 and argv[4] == '--inv':
        inv, argv = argv[5], argv[:4]
    if len(argv) != 4:
        print(__doc__.strip().splitlines()[2]); return 2
    old, new = parse(argv[1]), parse(argv[2])
    lost, paths = diff(old, new, int(os.environ.get('MAX_LOST', '3')))
    if paths is None:
        print(f'DỪNG: map mới mất {len(lost)} path, ví dụ {sorted(lost)[:5]}. Xem verify.log; cố ý thì đặt MAX_LOST.')
        return 1
    if inv:
        tong, mat, ho = pairs(inv, old, new)
        print(f'cặp trong inventory: {tong} | mất CSS gọn ở biến thể: {len(mat)} | chưa có CSS gọn ở biến thể: {len(ho)}')
        for k in ho[:10]:
            print('  CẢNH BÁO chưa có CSS gọn', k)
        if len(mat) > int(os.environ.get('MAX_LOST_PAIRS', '0')):
            print(f'DỪNG: map mới mất CSS gọn ở {len(mat)} cặp, ví dụ {mat[:5]}. Xem verify.log; cố ý thì đặt MAX_LOST_PAIRS.')
            return 1
        for k in mat[:10]:
            print('  CẢNH BÁO mất CSS gọn', k)
    for h in sorted(parse_all(argv[1]) - parse_all(argv[2])):
        print('  CẢNH BÁO map mới bỏ khoá all của', h[:8], '(bài của nhóm về file gộp khi cache dựng lại)')
    R = argv[3]
    open(f'{R}/purge_paths.txt', 'w').write('\n'.join(paths) + ('\n' if paths else ''))
    groups = [paths[i:i + 12] for i in range(0, len(paths), 12)]
    open(f'{R}/purge-groups.txt', 'w').write(''.join(','.join(g) + '\n' for g in groups))
    print('path cần purge:', len(paths), 'nhóm:', len(groups), '| path mất:', len(lost))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
