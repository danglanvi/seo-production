#!/usr/bin/env python3
"""Quét file mã trong một web root WordPress và in JSONL: dấu hiệu, vị trí lạ, đoạn trích để model đọc.

Chỉ đọc, không sửa. Chạy được trên server (Python 3.8+) qua stdin:
  ssh <host> "python3 - <web-root> --skip <thư mục,...> --neg <thư mục,...>" < scan_files.py > ket-qua.jsonl
--skip: thư mục đã qua checksum (core, plugin wordpress.org) nên bỏ qua.
--neg: thư mục sạch đã qua checksum, lấy mẫu làm mẫu âm để hiệu chuẩn ngưỡng (nhãn "neg_sample").
"""
import argparse
import hashlib
import json
import os
import random
import re
import sys

CODE_EXT = {".php", ".phtml", ".php3", ".php4", ".php5", ".php7", ".php8", ".phar", ".inc", ".suspected"}
SKIP_DIRS = {"cache", "litespeed", "node_modules", ".git", "backups-dup-pro", "ai1wm-backups", "updraft", "webp-express"}
SIGNALS = [
    ("eval", r"\beval\s*\("),
    ("assert_call", r"\bassert\s*\(\s*\$"),
    ("b64_decode", r"base64_decode\s*\("),
    ("inflate", r"\b(?:gzinflate|gzuncompress|gzdecode|str_rot13)\s*\("),
    ("create_function", r"create_function\s*\("),
    ("preg_e", r"preg_replace\s*\(\s*['\"](.).*?\1[a-z]*e[a-z]*['\"]"),
    ("shell", r"\b(?:shell_exec|passthru|system|exec|popen|proc_open|pcntl_exec)\s*\("),
    ("hex2bin", r"\bhex2bin\s*\("),
    ("req_input_exec", r"(?:eval|assert|system|exec|passthru|shell_exec|include|require)(?:_once)?\s*\(?\s*[^;]{0,40}\$_(?:GET|POST|REQUEST|COOKIE|SERVER|FILES)"),
    ("file_write_input", r"(?:file_put_contents|fwrite|move_uploaded_file)\s*\([^;]{0,120}\$_(?:GET|POST|REQUEST|COOKIE|FILES)"),
    ("dyn_func", r"\$\w+\s*\(\s*\$\w+"),
    ("chr_chain", r"(?:chr\(\d+\)\s*\.\s*){4,}"),
    ("hex_string", r"(?:\\x[0-9a-fA-F]{2}){20,}"),
    ("long_blob", r"[A-Za-z0-9+/=]{300,}"),
    ("globals_obf", r"\$GLOBALS\s*\[\s*['\"][^'\"]{1,6}['\"]\s*\]\s*\("),
    ("shell_names", r"(?i)\b(?:filesman|wso shell|b374k|c99shell|r57shell|indoxploit|alfa ?shell|uname -a)\b"),
    ("silence", r"error_reporting\s*\(\s*0\s*\)|@ini_set\s*\(\s*['\"]display_errors"),
    ("js_atob", r"\batob\s*\("),
    ("js_fromcharcode", r"String\.fromCharCode\s*\("),
    ("js_new_function", r"new\s+Function\s*\("),
    ("js_obfuscator", r"_0x[0-9a-f]{4,}"),
    ("js_doc_write_unescape", r"document\.write\s*\(\s*unescape"),
    ("xor_decode", r"chr\s*\(\s*ord\s*\("),
]
COMPILED = [(n, re.compile(p)) for n, p in SIGNALS]
ODD = re.compile(r"wp-content/(?:uploads|cache|upgrade)/.*\.(?:php\d?|phtml|phar|inc|ico)$|/\.[^/]+\.php$|/wp-include/|/wp-admins?/|/wp-contents/")
EPOCH_NAME = re.compile(r"[_-]1[78]\d{8}(?:[_.-]|$)")


def excerpt(text, hits):
    flat = re.sub(r"\s+", " ", text)
    parts = [flat[:1500]]
    for start in hits[:3]:
        if start > 1500:
            s = max(0, start - 200)
            parts.append("..." + flat[s:s + 500])
    return " ".join(parts)[:3200]


def scan(path, rel, label=None):
    try:
        st = os.stat(path)
        if st.st_size > 3_000_000:
            return None
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return None
    text = raw.decode("utf-8", "replace")
    signals, hits = [], []
    flat = re.sub(r"\s+", " ", text)
    for name, rx in COMPILED:
        m = rx.search(flat)
        if m:
            signals.append(name)
            hits.append(m.start())
    if len(re.findall(r"\\x[0-9a-fA-F]{2}", flat)) >= 15:
        signals.append("hex_escapes")
    if EPOCH_NAME.search(rel):
        signals.append("epoch_name")
    # File cấu hình chứa mật khẩu DB: giữ dấu hiệu, không trích nội dung.
    config = os.path.basename(rel).startswith("wp-config") or os.path.basename(rel) == ".env"
    row = {"id": rel, "location": rel, "size": st.st_size, "mtime": int(st.st_mtime),
           "sha256": hashlib.sha256(raw).hexdigest(), "signals": signals,
           "odd_location": bool(ODD.search("/" + rel)),
           "excerpt": "[config file, content withheld]" if config else excerpt(text, sorted(hits))}
    if label:
        row["label"] = label
    return row


def wanted(name, full):
    ext = os.path.splitext(name)[1].lower()
    if ext in CODE_EXT or name == ".htaccess":
        return True
    if ext == ".ico" or (ext == ".js" and "/uploads/" in full):
        return True
    if ext in {".js", ".html", ".htm"}:
        return None  # chỉ giữ nếu có dấu hiệu
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--skip", default="")
    ap.add_argument("--neg", default="")
    ap.add_argument("--neg-count", type=int, default=300)
    ap.add_argument("--all-js", action="store_true", help="giữ mọi file JS/HTML, kể cả không có dấu hiệu")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    skip = {os.path.normpath(os.path.join(root, s)) for s in a.skip.split(",") if s}
    out = sys.stdout
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and os.path.join(dirpath, d) not in skip]
        for name in files:
            full = os.path.join(dirpath, name)
            keep = wanted(name, full)
            if keep is False:
                continue
            row = scan(full, os.path.relpath(full, root))
            if not row:
                continue
            if name.endswith(".ico") and "<?php" not in row["excerpt"]:
                continue
            if keep is None and not row["signals"] and not a.all_js:
                continue
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    pool = []
    for d in [s for s in a.neg.split(",") if s]:
        for dirpath, _, files in os.walk(os.path.join(root, d)):
            pool += [os.path.join(dirpath, f) for f in files if f.endswith(".php")]
    random.seed(17)
    for full in random.sample(pool, min(a.neg_count, len(pool))):
        row = scan(full, os.path.relpath(full, root), label="neg_sample")
        if row:
            row["id"] = "neg:" + row["id"]
            out.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
