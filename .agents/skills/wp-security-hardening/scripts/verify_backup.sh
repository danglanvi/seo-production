#!/bin/bash
# Kiểm file backup sau khi tạo hoặc sau khi kéo về: kích thước, nén đọc được, dump đủ, không có lệnh phá bảng. Chỉ đọc, trừ khi có --write-sums.
# verify_backup.sh [tuỳ chọn] <file> [file...]
#
# File nhận: *.sql, *.sql.gz, *.sql.zst (dump DB) và *.tar, *.tar.gz, *.tgz, *.tar.zst (mã nguồn).
#
# Tuỳ chọn:
#   --min-bytes N     Kích thước tối thiểu. Mặc định 1024. File 0 byte luôn lỗi.
#   --min-tables N    Dump đầy đủ: số "CREATE TABLE" tối thiểu. Mặc định 1.
#   --min-entries N   Tar: số entry tối thiểu. Mặc định 1.
#   --partial         Dump một phần (mysqldump --where --no-create-info --replace). Lỗi nếu có "DROP TABLE" hoặc "CREATE TABLE",
#                     vì nạp lại sẽ xoá hoặc dựng lại cả bảng. Cảnh báo nếu dùng INSERT INTO thay vì REPLACE INTO.
#   --write-sums      Ghi SHA256SUMS trong thư mục của file, tên file không kèm đường dẫn. Chỉ ghi khi mọi kiểm tra đạt.
#   -h, --help        In trợ giúp này.
#
# Dump đầy đủ phải có dòng "Dump completed" ở cuối. Thiếu dòng này nghĩa là dump bị cắt giữa chừng.
# Mã thoát: 0 mọi file đạt · 1 có file lỗi · 2 sai tham số hoặc thiếu công cụ giải nén.
MIN_BYTES=1024; MIN_TABLES=1; MIN_ENTRIES=1; PARTIAL=0; SUMS=0
FILES=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,/^# Mã thoát/p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    --min-bytes) MIN_BYTES="${2-}"; shift 2;;
    --min-tables) MIN_TABLES="${2-}"; shift 2;;
    --min-entries) MIN_ENTRIES="${2-}"; shift 2;;
    --partial) PARTIAL=1; shift;;
    --write-sums) SUMS=1; shift;;
    -*) echo "Tham số lạ: $1 (xem --help)" >&2; exit 2;;
    *) FILES="$FILES
$1"; shift;;
  esac
done
for v in "$MIN_BYTES" "$MIN_TABLES" "$MIN_ENTRIES"; do case "$v" in ''|*[!0-9]*) echo "Giá trị số không hợp lệ: '$v'" >&2; exit 2;; esac; done
[ -n "$FILES" ] || { echo "Thiếu file cần kiểm. Xem --help." >&2; exit 2; }

sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
cat_sql() { # in nội dung SQL đã giải nén ra stdout
  case "$1" in
    *.zst) command -v zstd >/dev/null 2>&1 || { echo "THIẾU công cụ: zstd" >&2; exit 2; }; zstd -dc -- "$1";;
    *.gz) gzip -dc -- "$1";;
    *) cat -- "$1";;
  esac
}
bad=0
okfiles=""
IFS='
'
for f in $FILES; do
  [ -n "$f" ] || continue
  errs=""
  if [ ! -f "$f" ]; then echo "FAIL $f: không có file"; bad=1; continue; fi
  size=$(wc -c < "$f" | tr -d ' ')
  [ "$size" -eq 0 ] && errs="$errs; file 0 byte"
  [ "$size" -gt 0 ] && [ "$size" -lt "$MIN_BYTES" ] && errs="$errs; chỉ $size byte, dưới ngưỡng $MIN_BYTES"
  info="$size byte"
  if [ -z "$errs" ]; then
    case "$f" in
      *.sql|*.sql.gz|*.sql.zst)
        case "$f" in *.zst) command -v zstd >/dev/null 2>&1 || { echo "THIẾU công cụ: zstd" >&2; exit 2; }; zstd -tq -- "$f" 2>/dev/null || errs="$errs; nén zstd hỏng";; *.gz) gzip -t -- "$f" 2>/dev/null || errs="$errs; nén gzip hỏng";; esac
        if [ -z "$errs" ]; then
          tmp=$(mktemp "${TMPDIR:-/tmp}/verifybk.XXXXXX"); cat_sql "$f" > "$tmp" 2>/dev/null
          drop=$(grep -c '^DROP TABLE' "$tmp"); create=$(grep -c '^CREATE TABLE' "$tmp")
          if [ $PARTIAL = 1 ]; then
            [ "$drop" -gt 0 ] && errs="$errs; có $drop dòng DROP TABLE (dump một phần phải dùng --no-create-info --replace)"
            [ "$create" -gt 0 ] && errs="$errs; có $create dòng CREATE TABLE (thiếu --no-create-info)"
            ins=$(grep -c '^INSERT INTO' "$tmp"); [ "$ins" -gt 0 ] && info="$info, cảnh báo: $ins dòng INSERT INTO (nên dùng --replace)"
            rep=$(grep -c '^REPLACE INTO' "$tmp"); info="$info, REPLACE INTO=$rep"
          else
            [ "$create" -lt "$MIN_TABLES" ] && errs="$errs; chỉ $create bảng (CREATE TABLE), cần ít nhất $MIN_TABLES"
            tail -c 400 "$tmp" | grep -q 'Dump completed' || errs="$errs; thiếu dòng 'Dump completed' ở cuối (dump bị cắt)"
            info="$info, $create bảng"
          fi
          rm -f "$tmp"
        fi;;
      *.tar|*.tar.gz|*.tgz|*.tar.zst)
        case "$f" in
          *.zst) command -v zstd >/dev/null 2>&1 || { echo "THIẾU công cụ: zstd" >&2; exit 2; }; n=$(zstd -dc -- "$f" 2>/dev/null | tar -tf - 2>/dev/null | wc -l | tr -d ' ');;
          *.gz|*.tgz) n=$(tar -tzf "$f" 2>/dev/null | wc -l | tr -d ' ');;
          *) n=$(tar -tf "$f" 2>/dev/null | wc -l | tr -d ' ');;
        esac
        [ "$n" -lt "$MIN_ENTRIES" ] && errs="$errs; chỉ $n entry (hoặc archive không đọc được), cần ít nhất $MIN_ENTRIES"
        info="$info, $n entry";;
      *) errs="$errs; đuôi file không nhận (xem --help)";;
    esac
  fi
  if [ -n "$errs" ]; then echo "FAIL $f:${errs#;}"; bad=1; else echo "OK   $f ($info)"; okfiles="$okfiles
$f"; fi
done
if [ $SUMS = 1 ]; then
  if [ $bad = 0 ]; then
    for f in $okfiles; do
      [ -n "$f" ] || continue
      d=$(dirname "$f"); b=$(basename "$f"); s="$d/SHA256SUMS"
      touch "$s"; grep -vF "  $b" "$s" > "$s.tmp" 2>/dev/null; echo "$(sha256 "$f")  $b" >> "$s.tmp"; mv "$s.tmp" "$s"
      echo "SUMS $s <- $b"
    done
  else echo "Không ghi SHA256SUMS vì có file lỗi."; fi
fi
exit $bad
