#!/usr/bin/env python3
"""Điền mẫu templates/theme-preview.php.tpl thành mu-plugin xem trước theme. Không in mã.

  theme_preview_fill.py --base <theme gốc> --preview <theme xem trước> --code-file <file 0600> --out <file .php>

Chưa có --code-file thì sinh mã 32 ký tự hex và ghi file đó ở quyền 0600. Có rồi thì đọc lại mã cũ.
Mã 0: đã ghi --out. Mã 2: tham số sai, tên theme sai dạng, file mã sai quyền hoặc sai độ dài, --out đã tồn tại.
"""
import argparse, os, re, secrets, stat, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "templates", "theme-preview.php.tpl")
SLUG = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--preview", required=True)
    ap.add_argument("--code-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    for name in (a.base, a.preview):
        if not SLUG.match(name):
            print("tên theme sai dạng: %r" % name, file=sys.stderr)
            return 2
    if a.base == a.preview:
        print("theme xem trước phải khác theme gốc", file=sys.stderr)
        return 2
    if os.path.exists(a.out):
        print("đã có %s, không ghi đè" % a.out, file=sys.stderr)
        return 2
    if os.path.exists(a.code_file):
        if stat.S_IMODE(os.stat(a.code_file).st_mode) & 0o077:
            print("file mã phải ở quyền 0600: %s" % a.code_file, file=sys.stderr)
            return 2
        code = open(a.code_file).read().strip()
        if not re.match(r"^[0-9a-f]{32}$", code):
            print("file mã không chứa đúng 32 ký tự hex", file=sys.stderr)
            return 2
    else:
        code = secrets.token_hex(16)
        fd = os.open(a.code_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, (code + "\n").encode())
        os.close(fd)
        print("đã sinh mã mới, ghi vào %s (0600)" % a.code_file)
    s = open(TPL, encoding="utf-8").read()
    for k, v in (("__PREVIEW_CODE__", code), ("__BASE_THEME__", a.base), ("__PREVIEW_THEME__", a.preview)):
        if k not in s:
            print("mẫu thiếu chỗ điền %s" % k, file=sys.stderr)
            return 2
        s = s.replace(k, v)
    fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(fd, s.encode("utf-8"))
    os.close(fd)
    print("đã ghi %s: theme %s -> %s" % (a.out, a.base, a.preview))
    return 0


if __name__ == "__main__":
    sys.exit(main())
