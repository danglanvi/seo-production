#!/bin/bash
# GET một đường dẫn trên staging qua tunnel. Host staging không đi vào tham số lệnh, và mọi output qua stg_mask.
#
# Dùng:  stg_get.sh [--port N] [--auth-file F | --auth-stdin] [--head] [--out FILE] [--force] [--max-time S] /duong-dan
#   --port       cổng tunnel local (mặc định: $STG_PORT hoặc 18094)
#   --auth-file  file Basic Auth: user:pass, user=/password= hoặc STG_BASIC_USER=/STG_BASIC_PASS= (mặc định: $STG_AUTH_FILE)
#   --auth-stdin đọc Basic Auth từ stdin, cùng định dạng
#   --head       chỉ lấy header
#   --out FILE   ghi bản đã che host vào FILE (không ghi đè nếu chưa có --force). Không có thì in ra stdout
# Gọi HTTP cổng 80 qua --connect-to, User-Agent trình duyệt. Chỉ đọc, không ghi staging.
# Cần tunnel đang sống (stg_tunnel.sh up) và STG_ALIAS hoặc STG_HOST (xem stg_env.sh).
# Mã thoát: 0 HTTP dưới 400 · 1 HTTP từ 400 · 2 lỗi dùng · 3 không kết nối (000) · 4 không che được host.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/stg_env.sh"

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

PORT="${STG_PORT:-18094}"; AUTH_FILE="${STG_AUTH_FILE:-}"; AUTH_STDIN=0; HEAD=0; OUT=""; FORCE=0; MAXT=30; URLPATH=""
while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="${2:-}"; shift 2 ;;
    --auth-file) AUTH_FILE="${2:-}"; shift 2 ;;
    --auth-stdin) AUTH_STDIN=1; shift ;;
    --head) HEAD=1; shift ;;
    --out) OUT="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --max-time) MAXT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "LỖI: tuỳ chọn lạ: $1" >&2; exit 2 ;;
    *) URLPATH="$1"; shift ;;
  esac
done
case "$URLPATH" in /*) ;; *) echo "LỖI: cần đường dẫn bắt đầu bằng /. Xem --help." >&2; exit 2 ;; esac
case "$PORT" in ''|*[!0-9]*) echo "LỖI: --port phải là số." >&2; exit 2 ;; esac
case "$MAXT" in ''|*[!0-9]*) echo "LỖI: --max-time phải là số." >&2; exit 2 ;; esac
if [ -n "$OUT" ] && [ -e "$OUT" ] && [ "$FORCE" -ne 1 ]; then echo "LỖI: $OUT đã có. Thêm --force để ghi đè." >&2; exit 2; fi

AUTH=""
if [ "$AUTH_STDIN" -eq 1 ]; then
  AUTH="$(stg_auth_parse)" || exit 2
elif [ -n "$AUTH_FILE" ]; then
  [ -f "$AUTH_FILE" ] || { echo "LỖI: không đọc được file Basic Auth." >&2; exit 2; }
  AUTH="$(stg_auth_parse < "$AUTH_FILE")" || exit 2
fi

stg_load || exit 1

cfg_esc() { local s="$1"; s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; printf '%s' "$s"; }
umask 077
TMPD="$(mktemp -d)"; trap 'rm -rf "$TMPD"' EXIT
{
  printf 'url = "http://%s%s"\n' "$STG_HOST" "$(cfg_esc "$URLPATH")"
  printf 'connect-to = "%s:80:127.0.0.1:%s"\n' "$STG_HOST" "$PORT"
  printf 'user-agent = "%s"\n' "$STG_UA"
  printf 'max-time = %s\n' "$MAXT"
  [ "$HEAD" -eq 1 ] && printf 'head\n'
  [ -n "$AUTH" ] && printf 'user = "%s"\n' "$(cfg_esc "$AUTH")"
} > "$TMPD/cfg"
unset AUTH

code="$(curl -sS -K "$TMPD/cfg" -o "$TMPD/body" -w '%{http_code}' 2> "$TMPD/err")"; crc=$?
rm -f "$TMPD/cfg"
[ -s "$TMPD/err" ] && { stg_mask < "$TMPD/err" >&2 || exit 4; }
code="${code:-000}"
bytes=0; [ -f "$TMPD/body" ] && bytes="$(wc -c < "$TMPD/body" | tr -d ' ')"
echo "[stg_get] http=$code bytes=$bytes" >&2
if [ "$crc" -ne 0 ] || [ "$code" = 000 ]; then
  echo "[stg_get] không kết nối được. Kiểm tunnel: stg_tunnel.sh status" >&2
  exit 3
fi
if [ -n "$OUT" ]; then
  stg_mask < "$TMPD/body" > "$TMPD/masked" || { echo "[stg_get] không che được host, không ghi file" >&2; exit 4; }
  mv "$TMPD/masked" "$OUT"
else
  stg_mask < "$TMPD/body" > "$TMPD/masked" || { echo "[stg_get] không che được host, không in body" >&2; exit 4; }
  cat "$TMPD/masked"
fi
[ "$code" -ge 400 ] && exit 1
exit 0
