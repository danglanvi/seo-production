#!/usr/bin/env python3
"""Gộp 3 phía (base, staging, production) cho theme và mu-plugins rồi chép lên production.

  python3 -I merge3.py --base <dir> --stg <wp-content staging> --prod <wp-content production> \
      --roots themes/<theme>,mu-plugins [--skip mu-plugins/zz-staging-only.php,...] [--apply --backup-dir <dir>]

base = bản theme và mu-plugins của production lúc làm mới staging. Luật:
- File chỉ staging đổi: lấy bản staging. File chỉ production đổi: giữ production.
- File cả hai đổi: diff3 -m. Khi xung đột, chỉ nhận bản staging nếu staging đã chứa mọi thay đổi của production.
- File trong --skip (chỉ dùng cho staging) không chép.
Mặc định chỉ in plan (dry). --apply cần --backup-dir: script nén bản production sắp bị đè, ghi danh sách file mới, rồi mới chép.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import time


def walk(root, roots):
    r = {}
    for top in roots:
        for d, _, fs in os.walk(os.path.join(root, top)):
            for f in fs:
                p = os.path.join(d, f)
                with open(p, "rb") as fh:
                    r[os.path.relpath(p, root)] = hashlib.md5(fh.read()).hexdigest()
    return r


def plan(base, stg, prod, roots, skip):
    B, S, P = walk(base, roots), walk(stg, roots), walk(prod, roots)
    out, errs = [], []
    for k in sorted(set(B) | set(S) | set(P)):
        if skip and k.startswith(tuple(skip)):
            continue
        b, s, p = B.get(k), S.get(k), P.get(k)
        if s == p:
            continue
        if s is None:
            errs.append(f"staging thiếu {k} (production có)")
            continue
        if p is None or p == b:
            out.append(("stg", k, None))
            continue
        if s == b:
            continue  # chỉ production đổi: giữ
        r = subprocess.run(["diff3", "-m", os.path.join(stg, k), os.path.join(base, k), os.path.join(prod, k)], capture_output=True)
        if r.returncode == 0:
            out.append(("merged", k, r.stdout))
            continue
        d = subprocess.run(["diff", os.path.join(base, k), os.path.join(prod, k)], capture_output=True, text=True).stdout.splitlines()
        added = [x[2:] for x in d if x.startswith("> ")]
        removed = [x[2:] for x in d if x.startswith("< ")]
        with open(os.path.join(stg, k), encoding="utf-8", errors="replace") as fh:
            st = fh.read()
        if all(a in st for a in added) and all(x not in st or x in added for x in removed):
            out.append(("stg", k, None))
        else:
            errs.append(f"xung đột chưa giải: {k}")
    return out, errs


def apply(items, stg, prod, backup_dir, owner):
    os.makedirs(backup_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    tgz = os.path.join(backup_dir, f"prod-before-{ts}.tgz")
    new = [k for _, k, _ in items if not os.path.exists(os.path.join(prod, k))]
    with tarfile.open(tgz, "w:gz") as t:
        for _, k, _ in items:
            if os.path.exists(os.path.join(prod, k)):
                t.add(os.path.join(prod, k), arcname=k)
    with open(os.path.join(backup_dir, f"prod-new-files-{ts}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(new) + ("\n" if new else ""))
    u, g = (owner.split(":") + [None])[:2] if owner else (None, None)
    for kind, k, merged in items:
        dst = os.path.join(prod, k)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if kind == "stg":
            shutil.copy2(os.path.join(stg, k), dst)
        else:
            with open(dst, "wb") as fh:
                fh.write(merged)
        if u:
            shutil.chown(dst, u, g or u)
    print(f"đã chép {len(items)} file. Backup: {tgz}")
    print(f"Rollback: tar xzf {tgz} -C {prod} && xargs -I{{}} rm -f {prod}/{{}} < {os.path.join(backup_dir, f'prod-new-files-{ts}.txt')}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--stg", required=True)
    ap.add_argument("--prod", required=True)
    ap.add_argument("--roots", required=True, help="danh sách thư mục trong wp-content, cách nhau bằng dấu phẩy")
    ap.add_argument("--skip", default="", help="tiền tố đường dẫn chỉ dùng cho staging")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup-dir")
    ap.add_argument("--owner", default="www:www")
    a = ap.parse_args(argv)
    roots = [x for x in a.roots.split(",") if x]
    skip = [x for x in a.skip.split(",") if x]
    items, errs = plan(a.base, a.stg, a.prod, roots, skip)
    for kind, k, _ in items:
        print(kind, k)
    print(len(items), "file")
    if errs:
        print("DỪNG:")
        for e in errs:
            print(" ", e)
        return 1
    if a.apply:
        if not a.backup_dir:
            print("DỪNG: --apply cần --backup-dir", file=sys.stderr)
            return 2
        apply(items, a.stg, a.prod, a.backup_dir, a.owner)
    return 0


if __name__ == "__main__":
    sys.exit(main())
