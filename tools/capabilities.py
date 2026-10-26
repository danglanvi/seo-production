#!/usr/bin/env python3
"""capabilities.py — kiểm tool trên máy theo bảng trong capabilities.md cùng thư mục.

Chạy từ root repo:
    python3 tools/capabilities.py check --need python3,jev,gemma?   # "?" = tuỳ chọn
    python3 tools/capabilities.py check --need jev --json
    python3 tools/capabilities.py list
Lệnh phụ cho cột "lệnh kiểm" của bảng (chỉ in có/thiếu, không in giá trị):
    python3 tools/capabilities.py key OPENROUTER_JEV_API_KEY
    python3 tools/capabilities.py gws-auth webmasters.readonly

Exit: 0 = đủ tool bắt buộc · 1 = thiếu tool bắt buộc · 2 = id lạ, bảng lỗi hoặc sai cú pháp.
Chỉ dùng thư viện chuẩn. Lệnh kiểm chạy từ root repo, mỗi lệnh có timeout, output đã che secret.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE = HERE / "capabilities.md"
ROOT = HERE.parent
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
CODE_RE = re.compile(r"`([^`]+)`")
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASS|LICEN|CREDENTIAL", re.I)
GENERIC_SECRETS = [
    re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"(?=[A-Za-z0-9_+=-]*\d)[A-Za-z0-9_+=-]{40,}"),
]
HIDDEN = "<ẩn>"


class TableError(Exception):
    pass


def nfc(text):
    return unicodedata.normalize("NFC", text)


# ---------------------------------------------------------------- bảng

def split_row(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s.replace("\\|", "\x00").strip("|")
    return [c.strip().replace("\x00", "|") for c in s.split("|")]


def column(rec, key):
    return next((v for k, v in rec.items() if key in k), "")


def load_table(path=TABLE):
    """Đọc mọi bảng markdown có cột đầu `id` và một cột `lệnh kiểm`."""
    if not path.is_file():
        raise TableError("không thấy %s cạnh script" % path.name)
    rows, header = {}, None
    for no, line in enumerate(nfc(path.read_text(encoding="utf-8")).splitlines(), 1):
        cells = split_row(line)
        if cells is None:
            header = None
            continue
        if header is None:
            low = [c.lower().strip("`* ") for c in cells]
            if low and low[0] == "id" and any("lệnh kiểm" in c for c in low):
                header = low
            continue
        if all(set(c) <= set(":- ") for c in cells):
            continue
        rec = dict(zip(header, cells))
        tid = cells[0].strip("`* ")
        if not ID_RE.match(tid):
            raise TableError("dòng %d: id không hợp lệ: %r" % (no, tid))
        if tid in rows:
            raise TableError("dòng %d: id trùng: %s" % (no, tid))
        m = CODE_RE.search(column(rec, "lệnh kiểm"))
        if not m:
            raise TableError("dòng %d: %s thiếu lệnh kiểm đặt trong dấu `...`" % (no, tid))
        rows[tid] = {"id": tid, "cmd": m.group(1), "tool": column(rec, "tool"),
                     "use": column(rec, "dùng cho"), "fallback": column(rec, "fallback"),
                     "skills": column(rec, "skill"), "line": no}
    if not rows:
        raise TableError("%s không có bảng nào có cột id và lệnh kiểm" % path.name)
    return rows


def parse_need(spec):
    """'a,b?,c' -> [(id, tuỳ_chọn)]. Một id ghi hai lần: bắt buộc thắng tuỳ chọn."""
    merged = {}
    for part in spec.split(","):
        p = part.strip()
        if not p:
            continue
        optional = p.endswith("?")
        p = p[:-1].strip() if optional else p
        if not p:
            raise ValueError("có dấu ? đứng riêng trong --need")
        merged[p] = merged.get(p, True) and optional
    if not merged:
        raise ValueError("--need rỗng")
    return list(merged.items())


# ---------------------------------------------------------------- secret

def env_files():
    """.agent-secrets/.env tìm ngược từ thư mục chạy và từ root repo (giống jev.py)."""
    found = []
    for start in (Path.cwd().resolve(), ROOT):
        for d in (start, *start.parents):
            f = d / ".agent-secrets" / ".env"
            if f.is_file() and f not in found:
                found.append(f)
    return found


def read_env(path):
    out = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*['\"]?([^'\"\s]+)", line)
        if m:
            out.setdefault(m.group(1), m.group(2))
    return out


def env_value(name, files):
    if os.environ.get(name):
        return os.environ[name]
    for f in files:
        value = read_env(f).get(name)
        if value:
            return value
    return None


def secret_values():
    values = set()
    for f in env_files():
        values.update(v for v in read_env(f).values() if len(v) >= 6)
    values.update(v for k, v in os.environ.items() if SECRET_NAME.search(k) and len(v) >= 6)
    return sorted(values, key=len, reverse=True)


def redact(text, secrets):
    for value in secrets:
        text = text.replace(value, HIDDEN)
    for pattern in GENERIC_SECRETS:
        text = pattern.sub(HIDDEN, text)
    return text


# ---------------------------------------------------------------- chạy lệnh kiểm

def run_check(cmd, timeout):
    try:
        proc = subprocess.Popen(cmd, shell=True, cwd=str(ROOT), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                encoding="utf-8", errors="replace", start_new_session=True)
    except OSError as err:
        return False, "không chạy được lệnh kiểm: %s" % err
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        proc.communicate()
        return False, "quá %g s" % timeout
    lines = [l.strip() for l in (out or "").splitlines() if l.strip()]
    lines = lines or [l.strip() for l in (err or "").splitlines() if l.strip()]
    return proc.returncode == 0, " · ".join(lines[:3])


def shorten(text, limit=100):
    return text if len(text) <= limit else text[:limit - 3] + "..."


def cmd_check(args):
    table = load_table()
    try:
        need = parse_need(args.need)
    except ValueError as err:
        print("LỖI: %s" % err, file=sys.stderr)
        return 2
    unknown = [tid for tid, _ in need if tid not in table]
    if unknown:
        print("LỖI: id lạ: %s. Xem danh sách: python3 tools/capabilities.py list"
              % ", ".join(unknown), file=sys.stderr)
        return 2
    with ThreadPoolExecutor(max_workers=min(8, len(need))) as pool:
        checks = list(pool.map(lambda item: run_check(table[item[0]]["cmd"], args.timeout), need))
    secrets = secret_values()
    rows = []
    for (tid, optional), (ok, detail) in zip(need, checks):
        rows.append({"id": tid, "required": not optional, "status": "ok" if ok else "missing",
                     "detail": shorten(redact(detail, secrets)), "fallback": table[tid]["fallback"]})
    missing = [r["id"] for r in rows if r["required"] and r["status"] == "missing"]
    if args.json:
        print(json.dumps({"ok": not missing, "missing_required": missing, "results": rows},
                         ensure_ascii=False, indent=2))
        return 1 if missing else 0
    width = max(len(r["id"]) for r in rows) + 2
    print("%-*s%-11s%-11s%s" % (width, "id", "cần", "trạng thái", "chi tiết"))
    for r in rows:
        print("%-*s%-11s%-11s%s" % (width, r["id"], "bắt buộc" if r["required"] else "tuỳ chọn",
                                    r["status"], r["detail"]))
    opt_missing = [r for r in rows if not r["required"] and r["status"] == "missing"]
    if missing:
        print("\nKẾT LUẬN: thiếu tool bắt buộc: %s. Dừng và báo tên tool." % ", ".join(missing))
    else:
        print("\nKẾT LUẬN: đủ tool bắt buộc.")
    for r in [r for r in rows if r["status"] == "missing"]:
        print("  fallback %s: %s" % (r["id"], r["fallback"] or "(bảng chưa ghi)"))
    if opt_missing and not missing:
        print("Tool tuỳ chọn thiếu: dùng fallback ở trên và ghi giới hạn vào báo cáo.")
    return 1 if missing else 0


def cmd_list(args):
    table = load_table()
    if args.json:
        print(json.dumps(list(table.values()), ensure_ascii=False, indent=2))
        return 0
    width = max(len(t) for t in table) + 2
    for tid, row in table.items():
        print("%-*s%s" % (width, tid, row["tool"]))
    return 0


def cmd_key(args):
    bad = [n for n in args.names if not NAME_RE.match(n)]
    if bad:
        print("LỖI: tên key không hợp lệ: %s" % ", ".join(bad), file=sys.stderr)
        return 2
    files = env_files()
    ok = True
    for name in args.names:
        has = bool(env_value(name, files))
        ok = ok and has
        print("%s: %s" % (name, "có" if has else "thiếu"))
    return 0 if ok else 1


def cmd_gws_auth(args):
    try:
        proc = subprocess.run(["gws", "auth", "status"], capture_output=True, text=True,
                              timeout=args.timeout)
    except FileNotFoundError:
        print("gws: chưa cài")
        return 1
    except subprocess.TimeoutExpired:
        print("gws: quá %g s" % args.timeout)
        return 1
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        print("gws: không đọc được trạng thái đăng nhập")
        return 1
    if data.get("has_refresh_token") is not True:
        print("gws: chưa đăng nhập (chạy: gws auth login)")
        return 1
    scopes = [str(s) for s in data.get("scopes") or []]
    lacking = [s for s in args.scopes if not any(x == s or x.endswith("/" + s) for x in scopes)]
    if lacking:
        print("gws: đã đăng nhập, thiếu scope %s" % ", ".join(lacking))
        return 1
    print("gws: đã đăng nhập OAuth" + (", có scope %s" % ", ".join(args.scopes) if args.scopes else ""))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Kiểm tool trên máy theo bảng capabilities.md")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="kiểm bộ tool một skill cần")
    p.add_argument("--need", required=True, help="danh sách id, ví dụ python3,jev,gemma?")
    p.add_argument("--timeout", type=float, default=20.0, help="giây cho mỗi lệnh kiểm")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("list", help="liệt kê id trong bảng")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)
    p = sub.add_parser("key", help="key có trong biến môi trường hoặc .agent-secrets/.env không")
    p.add_argument("names", nargs="+")
    p.set_defaults(func=cmd_key)
    p = sub.add_parser("gws-auth", help="gws đã đăng nhập OAuth và có scope")
    p.add_argument("scopes", nargs="*")
    p.add_argument("--timeout", type=float, default=10.0)
    p.set_defaults(func=cmd_gws_auth)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except TableError as err:
        print("LỖI bảng: %s" % err, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
