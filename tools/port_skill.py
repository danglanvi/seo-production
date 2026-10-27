#!/usr/bin/env python3
"""port_skill.py: chép skill đã sửa ở master sang repo instance hoặc fork, có sao lưu và chặn skill có lineage riêng.

Dùng (từ root SEO Production):
  python3 tools/port_skill.py --skills wp-dang-bai,wp-xuat-ban-bai --to ../PROJECTS/<slug> --to "../Content Production - <brand>"
  Thêm --extra _TEMPLATES/wp-server.md để chép file ngoài skill, cùng đường dẫn tương đối. File --extra chỉ chép sang đích là instance
  của master (MIGRATION.md có dòng `master_version:`). Repo fork khác loại có thể có file cùng tên mà nội dung khác, ví dụ MIGRATION.md
  của repo Content (lỗi bắt được ở lượt chạy thử 27/10/2026).
  Mặc định chỉ in kế hoạch. --write mới chép. --new cho phép thêm skill hoặc file mà đích chưa có.
  --ep <skill> chép cả skill bị chặn vì lineage, sau khi người duyệt đã so diff.

Luật chặn (một skill ở một đích):
  - đích có file mà master không có: đích có lineage riêng;
  - SKILL.md của đích không có version, hoặc version của đích từ bằng master trở lên mà nội dung khác.
Script không xoá file. Bản cũ của mọi file bị ghi đè nằm ở --backup (mặc định ~/Backups/port-skill/<giờ>/<tên đích>/).
Sau khi chép, chạy sync mirror của đích: `bash tools/sync-skills.sh` nếu đích có, hoặc sync của workspace.
Mã thoát: 0 khi không có mục bị chặn, 1 khi có, 2 khi lỗi tham số.
Lỗi đã gặp 27/10/2026: vòng lặp shell port tay chạy trong zsh không tách danh sách thành từ, tạo 14 thư mục rỗng tên ghép. Script này không qua shell.
"""
import argparse, datetime, filecmp, os, re, shutil, sys
from pathlib import Path

SKIP = {'__pycache__', '.pytest_cache', '.DS_Store'}
MASTER = Path(__file__).resolve().parent.parent


def files(root):
    out = set()
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if f not in SKIP:
                out.add(Path(dp, f).relative_to(root).as_posix())
    return out


def version(skill_dir):
    p = Path(skill_dir, 'SKILL.md')
    if not p.is_file():
        return None
    head = p.read_text(encoding='utf-8', errors='replace').split('\n---', 1)[0]
    m = re.search(r'^\s*version:\s*["\']?v?([0-9][0-9.]*)', head, re.M)
    return tuple(int(x) for x in m.group(1).strip('.').split('.')) if m else None


def plan_skill(src, dst, allow_new, ep):
    """Trả (trạng thái, danh sách (rel, loại)). Trạng thái: chep, giong, chan:<lý do>, thieu."""
    if not dst.is_dir():
        return ('chep' if allow_new else 'thieu'), [(r, 'mới') for r in sorted(files(src))]
    fs, fd = files(src), files(dst)
    changes = [(r, 'mới') for r in sorted(fs - fd)]
    changes += [(r, 'sửa') for r in sorted(fs & fd) if not filecmp.cmp(src / r, dst / r, shallow=False)]
    if not changes:
        return 'giong', []
    if not ep:
        only = sorted(fd - fs)
        if only:
            return 'chan:đích có file master không có (' + ', '.join(only[:3]) + ')', changes
        vs, vd = version(src), version(dst)
        if vd is None:
            return 'chan:SKILL.md của đích không có version', changes
        if vs is not None and vd >= vs:
            return 'chan:version đích %s ≥ master %s mà nội dung khác' % ('.'.join(map(str, vd)), '.'.join(map(str, vs))), changes
    return 'chep', changes


def copy(src_file, dst_file, backup_file):
    if dst_file.exists():
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst_file, backup_file)
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skills', default='', help='tên skill, cách nhau bằng dấu phẩy')
    ap.add_argument('--to', action='append', required=True, help='root repo đích, lặp lại cho nhiều đích')
    ap.add_argument('--extra', action='append', default=[], help='file ngoài skill, đường dẫn tương đối từ root master')
    ap.add_argument('--master', default=str(MASTER))
    ap.add_argument('--backup', default=None)
    ap.add_argument('--new', action='store_true')
    ap.add_argument('--ep', action='append', default=[])
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(argv)
    master = Path(a.master).resolve()
    skills = [s.strip() for s in a.skills.split(',') if s.strip()]
    for s in skills:
        if not (master / 'skills' / s / 'SKILL.md').is_file():
            print(f'lỗi: master không có skills/{s}/SKILL.md', file=sys.stderr)
            return 2
    for e in a.extra:
        if not (master / e).is_file():
            print(f'lỗi: master không có {e}', file=sys.stderr)
            return 2
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_root = Path(a.backup) if a.backup else Path.home() / 'Backups' / 'port-skill' / stamp
    blocked = 0
    print(('GHI' if a.write else 'CHẠY THỬ') + f' · master {master}')
    for t in a.to:
        tgt = Path(t).resolve()
        if not tgt.is_dir():
            print(f'lỗi: không có thư mục đích {t}', file=sys.stderr)
            return 2
        bdir = backup_root / tgt.name.replace(' ', '_')
        print(f'\n== {tgt.name}')
        for s in skills:
            st, ch = plan_skill(master / 'skills' / s, tgt / 'skills' / s, a.new, s in a.ep)
            n_new = sum(1 for _, k in ch if k == 'mới')
            print(f'  {s}: {st} ({len(ch) - n_new} sửa, {n_new} mới)')
            if st.startswith('chan') or st == 'thieu':
                blocked += st.startswith('chan')
                continue
            for rel, kind in ch:
                print(f'    {kind} skills/{s}/{rel}')
                if a.write:
                    copy(master / 'skills' / s / rel, tgt / 'skills' / s / rel, bdir / 'skills' / s / rel)
        mig = tgt / 'MIGRATION.md'
        is_instance = mig.is_file() and re.search(r'^master_version:', mig.read_text(encoding='utf-8', errors='replace')[:400], re.M)
        for e in a.extra:
            src, dst = master / e, tgt / e
            if not is_instance:
                print(f'  {e}: bỏ qua (đích không phải instance của master)')
                continue
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                print(f'  {e}: giong')
            elif not dst.exists() and not a.new:
                print(f'  {e}: thieu (thêm --new để chép)')
            else:
                print(f'  {e}: chep')
                if a.write:
                    copy(src, dst, bdir / e)
        if a.write:
            sync = 'bash tools/sync-skills.sh' if (tgt / 'tools' / 'sync-skills.sh').is_file() else 'sync mirror của workspace'
            print(f'  Bước kế: chạy `{sync}` trong {tgt.name}. Bản cũ ở {bdir}')
    if blocked:
        print(f'\n{blocked} mục bị chặn. So diff rồi chép bằng --ep <skill> nếu người duyệt đồng ý.')
    return 1 if blocked else 0


if __name__ == '__main__':
    sys.exit(main())
