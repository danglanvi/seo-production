#!/usr/bin/env python3
"""map_diff.py (wp-ucss): so map trên site với map mới, chặn map làm mất path, ghi path cần purge.

Dùng: python3 -I map_diff.py <map_site.php> <map_moi.php> <thư mục ra>   (env MAX_LOST, mặc định 3)
Ghi <thư mục ra>/purge_paths.txt và purge-groups.txt (12 path mỗi nhóm). Mã 1 khi map mới mất quá MAX_LOST path.
"""
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
    if len(argv) != 4:
        print(__doc__.strip().splitlines()[2]); return 2
    lost, paths = diff(parse(argv[1]), parse(argv[2]), int(os.environ.get('MAX_LOST', '3')))
    if paths is None:
        print(f'DỪNG: map mới mất {len(lost)} path, ví dụ {sorted(lost)[:5]}. Xem verify.log; cố ý thì đặt MAX_LOST.')
        return 1
    R = argv[3]
    open(f'{R}/purge_paths.txt', 'w').write('\n'.join(paths) + ('\n' if paths else ''))
    groups = [paths[i:i + 12] for i in range(0, len(paths), 12)]
    open(f'{R}/purge-groups.txt', 'w').write(''.join(','.join(g) + '\n' for g in groups))
    print('path cần purge:', len(paths), 'nhóm:', len(groups), '| path mất:', len(lost))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
