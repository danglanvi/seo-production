#!/usr/bin/env bash
# tim_file_lo.sh (wp-security-hardening): tìm file backup, dump, log, file môi trường nằm trong web root, rồi thử tải từng file từ ngoài.
# exposure_check.sh chỉ thử path cố định. Script này tìm file thật trên server, nên bắt được dump đặt tên tuỳ ý.
# Ca thật 27/10/2026 (site WooCommerce trên shared hosting): 5 dump SQL 57 MB trong wp-content/backups/ và wp-content/deploy-staging/ trả 200.
#
# Dùng: tim_file_lo.sh --ssh '<lệnh mở shell trên server>' --root <web root> --base https://<domain> [--out <file.tsv>] [--sleep 1] [--max 300]
#   --ssh: ví dụ 'ssh site-vps' hoặc 'ssh -i <key> -p 2210 user@host'. Không để dấu cách trong đường dẫn key. Test dùng 'bash -c'.
#   Staging có Basic Auth: đặt EXPOSURE_CURL_CONFIG=<file cấu hình curl> như exposure_check.sh.
# Bước 1 (server, chỉ đọc): find các đuôi nguy hiểm, bỏ thư mục cache. Bước 2 (từ ngoài): GET byte đầu (Range 0-0), 1 lượt/giây.
# Ra bảng TSV: mã HTTP, mức, byte, ngày sửa, path. Không tải nội dung file. 200 hoặc 206 nghĩa là ai cũng tải được.
# Mức: cao (dump, backup, log, env, wp-config, khoá SSH), trung (zip, tar, csv, xlsx, pem, key ngoài thư mục gói),
#   goi (file đi kèm plugin, theme, core, không phải dump/log/env; ví dụ khoá công khai và CA bundle của Wordfence, đo 27/10/2026).
# Mã thoát: 0 khi không file mức cao hoặc trung nào tải được, 1 khi có, 2 khi lỗi chạy.
set -u
SSH= ROOT= BASE= OUT= SLEEP=1 MAX=300
while [ $# -gt 0 ]; do
  case "$1" in
    --ssh) SSH="$2"; shift 2 ;;
    --root) ROOT="$2"; shift 2 ;;
    --base) BASE="${2%/}"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    --max) MAX="$2"; shift 2 ;;
    *) echo "tham số lạ: $1" >&2; exit 2 ;;
  esac
done
[ -n "$SSH" ] && [ -n "$ROOT" ] && [ -n "$BASE" ] || { sed -n '6,9p' "$0" >&2; exit 2; }

REMOTE='set -u
root="$1"; cd "$root" || exit 3
find . \( -path ./wp-content/cache -o -path ./wp-content/litespeed -o -path "*/node_modules" -o -path ./.git \) -prune -o -type f -size +0c \( \
  -iname "*.sql" -o -iname "*.sql.*" -o -iname "*.dump" -o -iname "*.zip" -o -iname "*.tar" -o -iname "*.tar.*" -o -iname "*.tgz" \
  -o -iname "*.gz" -o -iname "*.zst" -o -iname "*.bz2" -o -iname "*.7z" -o -iname "*.rar" -o -iname "*.wpress" -o -iname "*.jpa" \
  -o -iname "*.bak" -o -iname "*.old" -o -iname "*.orig" -o -iname "*.save" -o -iname "*.swp" -o -iname "*~" \
  -o -iname "*.log" -o -iname "error_log" -o -iname ".env" -o -iname ".env.*" -o -iname "*.env" -o -iname "*.pem" -o -iname "*.key" \
  -o -iname "id_rsa*" -o -iname "*.csv" -o -iname "*.xls" -o -iname "*.xlsx" -o -iname "wp-config*.php?*" \) -print 2>/dev/null |
while IFS= read -r f; do
  s=$(wc -c < "$f" | tr -d " ")
  d=$(stat -c %y "$f" 2>/dev/null) || d=$(stat -f %Sm -t %F "$f" 2>/dev/null) || d=?
  printf "%s\t%s\t%s\n" "$s" "${d:0:10}" "${f#./}"
done'

LIST=$(printf '%s\n' "$REMOTE" | $SSH "bash -s -- $(printf %q "$ROOT")") || { echo "không đọc được web root qua SSH" >&2; exit 2; }
CURL=(curl -s -o /dev/null -w '%{http_code}' -r 0-0 --max-time 20 -A 'Mozilla/5.0 (compatible; tim_file_lo)')
[ -n "${EXPOSURE_CURL_CONFIG:-}" ] && CURL+=(-K "$EXPOSURE_CURL_CONFIG")

n=0; open=0
TAB=$'\t'
hdr="ma${TAB}muc${TAB}byte${TAB}ngay${TAB}path"
HIGH='(\.(sql|dump|wpress|jpa|bak|old|orig|save|swp|log|env)$|\.sql\.|(^|/)\.env|(^|/)error_log$|wp-config|id_rsa|~$)'
PKG='^(wp-content/plugins/|wp-content/themes/|wp-includes/|wp-admin/)'
[ -n "$OUT" ] && echo "$hdr" > "$OUT"
echo "$hdr"
while IFS="$TAB" read -r size day path; do
  [ -z "${path:-}" ] && continue
  n=$((n + 1))
  if [ "$n" -gt "$MAX" ]; then echo "dừng ở $MAX file (--max); chạy lại với --max lớn hơn" >&2; break; fi
  enc=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$path")
  code=$("${CURL[@]}" "$BASE/$enc")
  low=$(printf '%s' "$path" | tr '[:upper:]' '[:lower:]')
  if printf '%s' "$low" | grep -Eq "$HIGH"; then muc=cao
  elif printf '%s' "$low" | grep -Eq "$PKG"; then muc=goi
  else muc=trung; fi
  case "$code:$muc" in 200:cao|206:cao|200:trung|206:trung) open=$((open + 1)) ;; esac
  line="$code$TAB$muc$TAB$size$TAB$day$TAB$path"
  echo "$line"
  [ -n "$OUT" ] && echo "$line" >> "$OUT"
  sleep "$SLEEP"
done <<< "$LIST"
echo "tim_file_lo: $n file khớp đuôi, $open file mức cao hoặc trung tải được từ ngoài" >&2
[ "$open" -gt 0 ] && exit 1
exit 0
