#!/usr/bin/env python3
"""Sửa file theme hoặc mu-plugin theo spec, có kiểm số lần khớp, backup, lint và đường lui. Mặc định chạy thử, không ghi gì.

Lệnh con:
  apply        <thư mục gốc> <spec.json> --backup DIR [--apply]   thay chuỗi theo spec
  quarantine   <thư mục gốc> <file tương đối>... --to DIR [--apply]   chuyển file ra DIR, không xoá
  unquarantine <thư mục gốc> --from DIR [file tương đối...] [--apply]  trả file từ DIR về chỗ cũ
  restore      <thư mục gốc> --backup DIR [--apply]   chép bản gốc trong backup về lại
  lint-css     <file>...                              kiểm scope CSS, không ghi gì

Spec: danh sách {id, file, old, new, count, regex?, css?, allow_global?}.
  count là số lần khớp mong đợi (mặc định 1). Một file có mục lệch thì không ghi file đó.
  Với file .css hoặc mục có "css": true, script kiểm phần "new": rule không có class, id hay thuộc tính (h1–h6, p, nav, button...)
  là rule toàn cục và bị chặn, trừ khi mục có "allow_global": true hoặc chạy --allow-global.
Sau khi ghi: .php chạy php -l, .css kiểm ngoặc cân. Lỗi thì trả file về bản gốc.
Mã thoát: 0 xong · 1 có mục lệch, lỗi lint, rule toàn cục hoặc file không xử lý được · 2 sai cú pháp hoặc spec sai.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

AT_RECURSE = ("media", "supports", "layer", "container", "document")


# ---------- đọc CSS tối thiểu, đủ để kiểm scope ----------
def strip_comments(s):
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)


def _match_brace(s, i):
    depth, q, n = 0, None, len(s)
    while i < n:
        c = s[i]
        if q:
            if c == "\\":
                i += 1
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


def iter_rules(css):
    """Trả (selector, body) cho từng rule thường, đi vào @media, @supports, @layer, @container. Bỏ @font-face, @keyframes."""
    s = strip_comments(css)
    out, i, n = [], 0, len(s)
    while i < n:
        j = s.find("{", i)
        if j < 0:
            break
        prelude = s[i:j]
        if ";" in prelude:
            prelude = prelude.rsplit(";", 1)[1]
        prelude = prelude.strip()
        k = _match_brace(s, j)
        body = s[j + 1:k]
        if prelude.startswith("@"):
            name = re.match(r"@([\w-]+)", prelude)
            if name and name.group(1).lower() in AT_RECURSE:
                out.extend(iter_rules(body))
        elif prelude:
            out.append((prelude, body))
        i = k + 1
    return out


def selector_list(prelude):
    out, depth, cur = [], 0, ""
    for c in prelude:
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        if c == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


ICON_RE = re.compile(r"icon|(^|[\s>+~,.])fa[sbrl]?($|[\s\-.:,\[])|(^|[\s>+~,])i($|[\s.:,\[>+~])|svg|dashicons|eicon", re.I)
ICON_PROPS = re.compile(r"(^|;|\s)(font-size|font-family|font-weight|line-height)\s*:", re.I)


def scope_lint(css):
    """Trả (global_rules, icon_warnings). Rule toàn cục: selector không có class, id hay thuộc tính."""
    globals_, icons = [], []
    for prelude, body in iter_rules(css):
        for sel in selector_list(prelude):
            if not re.search(r"[.#\[]", sel):
                globals_.append(sel)
            if ICON_RE.search(sel) and ICON_PROPS.search(body):
                icons.append(sel)
    return globals_, icons


def css_balanced(text):
    s = strip_comments(text)
    depth, q = 0, None
    i = 0
    while i < len(s):
        c = s[i]
        if q:
            if c == "\\":
                i += 1
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0 and q is None and "/*" not in s


# ---------- tiện ích ----------
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def safe_join(root, rel):
    if os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
        raise ValueError("đường dẫn phải tương đối và không chứa '..': %s" % rel)
    p = os.path.normpath(os.path.join(root, rel))
    if not (p == root or p.startswith(root.rstrip(os.sep) + os.sep)):
        raise ValueError("đường dẫn nằm ngoài thư mục gốc: %s" % rel)
    return p


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_atomic(path, text):
    tmp = path + ".tp-tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    shutil.copymode(path, tmp)
    os.replace(tmp, path)


def find_php(explicit):
    for c in (explicit, os.environ.get("PHP_BIN"), shutil.which("php"), "/usr/local/lsws/lsphp83/bin/php"):
        if c and os.path.exists(c):
            return c
    return None


def lint_file(path, php):
    """Trả None khi đạt, chuỗi lỗi khi hỏng, 'NO_PHP' khi thiếu php."""
    if path.endswith(".php"):
        if not php:
            return "NO_PHP"
        r = subprocess.run([php, "-l", path], capture_output=True, text=True)
        return None if r.returncode == 0 else (r.stdout + r.stderr).strip()[:300]
    if path.endswith(".css"):
        return None if css_balanced(read_text(path)) else "ngoặc nhọn CSS không cân hoặc comment không đóng"
    return None


def load_spec(path):
    try:
        spec = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError("không đọc được spec: %s" % e)
    if not isinstance(spec, list) or not spec:
        raise ValueError("spec phải là danh sách không rỗng")
    seen = set()
    for s in spec:
        for k in ("id", "file", "old", "new"):
            if k not in s:
                raise ValueError("mục thiếu khoá '%s': %s" % (k, s.get("id", s)))
        if not s["old"]:
            raise ValueError("mục %s có old rỗng" % s["id"])
        if s["id"] in seen:
            raise ValueError("id trùng: %s" % s["id"])
        seen.add(s["id"])
        s.setdefault("count", 1)
        if not isinstance(s["count"], int) or s["count"] < 1:
            raise ValueError("mục %s: count phải là số nguyên >= 1" % s["id"])
    return spec


# ---------- lệnh con ----------
def cmd_apply(a):
    root = os.path.abspath(a.root)
    spec = load_spec(a.spec)
    php = find_php(a.php)
    by_file = {}
    for s in spec:
        by_file.setdefault(s["file"], []).append(s)
    rep = {"apply": a.apply, "ok": [], "already": [], "skip": [], "global": [], "warn": [], "lint": [], "files": []}
    for rel, items in by_file.items():
        path = safe_join(root, rel)
        if not os.path.isfile(path):
            rep["skip"].append(["FILE", rel, "không có file", ""])
            continue
        src = read_text(path)
        cur, bad = src, []
        for s in items:
            if s.get("regex"):
                n = len(re.findall(s["old"], cur))
                if n == s["count"]:
                    cur = re.sub(s["old"], s["new"], cur)
                    rep["ok"].append([s["id"], rel, n, s["count"]])
                else:
                    bad.append([s["id"], rel, n, s["count"]])
            else:
                n = cur.count(s["old"])
                if n == s["count"]:
                    cur = cur.replace(s["old"], s["new"])
                    rep["ok"].append([s["id"], rel, n, s["count"]])
                elif n == 0 and s["new"] and cur.count(s["new"]) >= s["count"]:
                    rep["already"].append([s["id"], rel])
                else:
                    bad.append([s["id"], rel, n, s["count"]])
            if s.get("css") or rel.endswith(".css"):
                g, ic = scope_lint(s["new"])
                if g and not (s.get("allow_global") or a.allow_global):
                    rep["global"].append([s["id"], rel, g[:6]])
                for sel in ic:
                    rep["warn"].append([s["id"], rel, "rule font trên icon, nên loại trừ: " + sel])
        gl = [x for x in rep["global"] if x[1] == rel]
        if bad or gl:
            rep["skip"] += bad
            rep["skip"].append(["FILE", rel, "không ghi file này", "mục lệch" if bad else "rule toàn cục"])
            continue
        if cur == src:
            continue
        if not a.apply:
            rep["files"].append({"file": rel, "would_write": True, "before": sha(path)[:12]})
            continue
        bpath = safe_join(os.path.abspath(a.backup), rel)
        os.makedirs(os.path.dirname(bpath), exist_ok=True)
        if not os.path.exists(bpath):
            shutil.copy2(path, bpath)
        before = sha(path)
        write_atomic(path, cur)
        err = lint_file(path, php)
        note = None
        if err == "NO_PHP":
            if a.no_lint:
                err, note = None, "bỏ qua (không có php)"
            else:
                err = "không có php để lint file .php (đặt PHP_BIN hoặc --php, hoặc --no-lint)"
        if err:
            shutil.copy2(bpath, path)
            rep["lint"].append([rel, err])
            continue
        rep["files"].append({"file": rel, "before": before[:12], "after": sha(path)[:12], "backup": os.path.relpath(bpath), **({"lint": note} if note else {})})
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if (rep["skip"] or rep["lint"] or rep["global"]) else 0


def manifest_add(qdir, rows):
    mf = os.path.join(qdir, "MANIFEST.tsv")
    new = not os.path.exists(mf)
    with open(mf, "a", encoding="utf-8") as f:
        if new:
            f.write("time\trel\tsha256\tsize\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def cmd_quarantine(a):
    root, qdir = os.path.abspath(a.root), os.path.abspath(a.to)
    rep, rows, bad = {"apply": a.apply, "moved": [], "skip": []}, [], 0
    for rel in a.files:
        src, dst = safe_join(root, rel), safe_join(qdir, rel)
        if not os.path.isfile(src):
            rep["skip"].append([rel, "không có file (hoặc là thư mục)"]); bad += 1; continue
        if os.path.exists(dst):
            rep["skip"].append([rel, "đã có bản cùng tên trong quarantine, không ghi đè"]); bad += 1; continue
        rep["moved"].append([rel, sha(src)[:12]])
        if a.apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            digest, size = sha(src), os.path.getsize(src)
            shutil.move(src, dst)
            rows.append([time.strftime("%Y-%m-%dT%H:%M:%S"), rel, digest, size])
    if rows:
        manifest_add(qdir, rows)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if bad else 0


def cmd_unquarantine(a):
    root, qdir = os.path.abspath(a.root), os.path.abspath(a._from)
    files = a.files
    if not files:
        mf = os.path.join(qdir, "MANIFEST.tsv")
        if not os.path.exists(mf):
            print("Không có file nào và không có MANIFEST.tsv trong %s" % qdir, file=sys.stderr)
            return 2
        files = [l.split("\t")[1] for l in open(mf, encoding="utf-8").read().splitlines()[1:] if l.strip()]
    rep, bad = {"apply": a.apply, "restored": [], "skip": []}, 0
    for rel in dict.fromkeys(files):
        src, dst = safe_join(qdir, rel), safe_join(root, rel)
        if not os.path.isfile(src):
            rep["skip"].append([rel, "không có trong quarantine"]); bad += 1; continue
        if os.path.exists(dst):
            rep["skip"].append([rel, "đã có file ở chỗ cũ, không ghi đè"]); bad += 1; continue
        rep["restored"].append(rel)
        if a.apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if bad else 0


def cmd_restore(a):
    root, bdir = os.path.abspath(a.root), os.path.abspath(a.backup)
    if not os.path.isdir(bdir):
        print("Không thấy thư mục backup: %s" % bdir, file=sys.stderr)
        return 2
    rep = {"apply": a.apply, "restored": [], "same": []}
    for d, _, fs in os.walk(bdir):
        for f in fs:
            b = os.path.join(d, f)
            rel = os.path.relpath(b, bdir)
            dst = safe_join(root, rel)
            if os.path.exists(dst) and sha(dst) == sha(b):
                rep["same"].append(rel); continue
            rep["restored"].append(rel)
            if a.apply:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(b, dst)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


def cmd_lint_css(a):
    bad = 0
    for p in a.files:
        try:
            text = read_text(p)
        except OSError as e:
            print("%s: không đọc được (%s)" % (p, e)); bad += 1; continue
        g, ic = scope_lint(text)
        for sel in g:
            print("%s: rule toàn cục: %s" % (p, sel)); bad += 1
        for sel in ic:
            print("%s: cảnh báo, rule font trên icon: %s" % (p, sel))
        if not css_balanced(text):
            print("%s: ngoặc nhọn không cân" % p); bad += 1
    if not bad:
        print("lint-css: đạt")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("apply", help="thay chuỗi theo spec")
    p.add_argument("root"); p.add_argument("spec"); p.add_argument("--backup", required=True)
    p.add_argument("--apply", action="store_true", help="ghi thật (mặc định chạy thử)")
    p.add_argument("--php"); p.add_argument("--no-lint", action="store_true"); p.add_argument("--allow-global", action="store_true")
    p.set_defaults(fn=cmd_apply)
    p = sub.add_parser("quarantine", help="chuyển file ra thư mục quarantine")
    p.add_argument("root"); p.add_argument("files", nargs="+"); p.add_argument("--to", required=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_quarantine)
    p = sub.add_parser("unquarantine", help="trả file từ quarantine về chỗ cũ")
    p.add_argument("root"); p.add_argument("files", nargs="*"); p.add_argument("--from", dest="_from", required=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_unquarantine)
    p = sub.add_parser("restore", help="chép bản gốc trong backup về lại")
    p.add_argument("root"); p.add_argument("--backup", required=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_restore)
    p = sub.add_parser("lint-css", help="kiểm scope CSS")
    p.add_argument("files", nargs="+")
    p.set_defaults(fn=cmd_lint_css)
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        return a.fn(a)
    except ValueError as e:
        print("Lỗi: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
