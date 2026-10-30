#!/bin/bash
# html_validate.sh <thư mục html> <out.jsonl>
# Chạy html-validate trên mọi *.html theo lô 40 file. Mỗi lô ghi JSON ra file tạm rồi mới đọc,
# vì Node cắt stdout khi đi qua pipe. Kết quả: 1 dòng JSON mỗi thông báo {id, rule, sev, sel, msg}.
set -u
DIR="$1"; OUT="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp)"
: > "$OUT"
find "$DIR" -maxdepth 1 -name '*.html' | sort | split -l 40 - "$TMP.lo."
for LO in "$TMP".lo.*; do
  tr '\n' '\0' < "$LO" | xargs -0 npx --yes html-validate@11 --config "$HERE/htmlvalidate-config.json" -f json > "$TMP" 2>/dev/null
  python3 -I "$HERE/hv_strip.py" < "$TMP" >> "$OUT"
  rm -f "$LO"
done
rm -f "$TMP"
wc -l < "$OUT"
