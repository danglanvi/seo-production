#!/bin/bash
# Quét thư mục làm việc của đợt: có lộ host staging, mật khẩu Basic Auth, mật khẩu DB hay mẫu secret không.
# Không bao giờ in giá trị cần tìm. Chạy trước khi báo xong đợt và trước khi mở file HTML evidence.
#
# Dùng:  stg_leak_check.sh <thư-mục> [--auth-file F] [--env-file F]... [--needle-file F]... [--no-host]
#   --auth-file    file Basic Auth (định dạng như stg_get.sh). Mật khẩu thành needle. Mặc định: $STG_AUTH_FILE
#   --env-file     file KHOÁ=giá trị, ví dụ bản sao file secret của staging. Lấy giá trị của khoá có
#                  PASS, SECRET, TOKEN, KEY, SALT, SLUG, HOST, URL trong tên. Giá trị URL và HOST thêm dạng host
#   --needle-file  mỗi dòng một chuỗi cần tìm (bỏ dòng trống và dòng bắt đầu bằng #)
#   --no-host      không nạp host staging. Chỉ dùng khi đợt không chạm staging
# Host staging lấy từ STG_HOST, hoặc stg_load khi có STG_ALIAS (xem stg_env.sh). Thiếu cả hai thì dừng.
# Tìm ở dạng gốc và dạng JSON-escape (/ thành \/), trong nội dung (cả file nhị phân) và trong tên file.
# Thêm mẫu: wp-login.php có dấu ? theo sau, AIza..., khoá riêng PEM. Bỏ needle ngắn hơn 6 ký tự.
# Mã thoát: 0 sạch · 1 có lộ · 2 lỗi dùng hoặc không có needle nào.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/stg_env.sh"

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; }

DIR=""; AUTH_FILE="${STG_AUTH_FILE:-}"; NO_HOST=0; ENV_FILES=(); NEEDLE_FILES=()
while [ $# -gt 0 ]; do
  case "$1" in
    --auth-file) AUTH_FILE="${2:-}"; shift 2 ;;
    --env-file) ENV_FILES+=("${2:-}"); shift 2 ;;
    --needle-file) NEEDLE_FILES+=("${2:-}"); shift 2 ;;
    --no-host) NO_HOST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "LỖI: tuỳ chọn lạ: $1" >&2; exit 2 ;;
    *) [ -z "$DIR" ] || { echo "LỖI: chỉ nhận một thư mục." >&2; exit 2; }; DIR="$1"; shift ;;
  esac
done
[ -n "$DIR" ] && [ -d "$DIR" ] || { echo "LỖI: cần một thư mục để quét. Xem --help." >&2; exit 2; }

NEEDLES=(); LABELS=(); SHORT=0
add() { # giá trị, nhãn
  local v="$1"
  if [ "${#v}" -lt 6 ]; then SHORT=$((SHORT+1)); return 0; fi
  NEEDLES+=("$v"); LABELS+=("$2")
  case "$v" in */*) NEEDLES+=("${v//\//\\/}"); LABELS+=("$2 (json)") ;; esac
}
need_file() { [ -f "$1" ] || { echo "LỖI: không đọc được file: $(basename "$1")" >&2; exit 2; }; }

if [ "$NO_HOST" -eq 0 ]; then
  stg_load || { echo "LỖI: không nạp được host staging. Đặt STG_ALIAS, hoặc thêm --no-host nếu đợt không chạm staging." >&2; exit 2; }
  add "$STG_HOST" "host staging"
fi
if [ -n "$AUTH_FILE" ]; then
  need_file "$AUTH_FILE"
  a="$(stg_auth_parse < "$AUTH_FILE")" || exit 2
  add "${a#*:}" "mật khẩu Basic Auth"; unset a
fi
for f in ${ENV_FILES[@]+"${ENV_FILES[@]}"}; do
  need_file "$f"
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"; line="${line#export }"
    case "$line" in *=*) ;; *) continue ;; esac
    k="${line%%=*}"; v="${line#*=}"
    case "$k" in ''|[0-9]*|*[!A-Za-z0-9_]*) continue ;; esac
    ku="$(printf '%s' "$k" | tr '[:lower:]' '[:upper:]')"
    case "$ku" in *PASS*|*SECRET*|*TOKEN*|*KEY*|*SALT*|*SLUG*|*HOST*|*URL*) ;; *) continue ;; esac
    case "$v" in \"*\") v="${v#\"}"; v="${v%\"}" ;; \'*\') v="${v#\'}"; v="${v%\'}" ;; esac
    add "$v" "$k@$(basename "$f")"
    case "$ku" in *HOST*|*URL*) h="$(stg_norm_host "$v")"; [ "$h" = "$v" ] || add "$h" "$k@$(basename "$f") (host)" ;; esac
  done < "$f"
done
for f in ${NEEDLE_FILES[@]+"${NEEDLE_FILES[@]}"}; do
  need_file "$f"; n=0
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1)); line="${line%$'\r'}"
    case "$line" in ''|'#'*) continue ;; esac
    add "$line" "$(basename "$f"):dòng $n"
  done < "$f"
done
[ "$SHORT" -gt 0 ] && echo "Bỏ $SHORT needle ngắn hơn 6 ký tự." >&2
if [ "${#NEEDLES[@]}" -eq 0 ]; then echo "LỖI: không có needle nào để tìm." >&2; exit 2; fi

umask 077
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
LEAKS=0
safe() { local p="$1" n; for n in "${NEEDLES[@]}"; do p="${p//"$n"/***}"; done; printf '%s' "$p"; }

i=0
while [ "$i" -lt "${#NEEDLES[@]}" ]; do
  n="${NEEDLES[$i]}"; l="${LABELS[$i]}"; i=$((i+1))
  printf '%s\n' "$n" > "$TMP"
  while IFS= read -r p; do
    [ -n "$p" ] && { echo "LỘ nội dung [$l]: $(safe "$p")"; LEAKS=$((LEAKS+1)); }
  done < <(grep -rlaF -f "$TMP" -- "$DIR" 2>/dev/null)
  while IFS= read -r p; do
    case "$p" in *"$n"*) echo "LỘ tên file [$l]: $(safe "$p")"; LEAKS=$((LEAKS+1)) ;; esac
  done < <(find "$DIR" 2>/dev/null)
done
for pat in 'wp-login\.php\?' 'AIza[0-9A-Za-z_-]{20,}' 'BEGIN [A-Z ]*PRIVATE KEY'; do
  while IFS= read -r p; do
    [ -n "$p" ] && { echo "LỘ mẫu [$pat]: $(safe "$p")"; LEAKS=$((LEAKS+1)); }
  done < <(grep -rlaE -e "$pat" -- "$DIR" 2>/dev/null)
done

if [ "$LEAKS" -gt 0 ]; then
  echo "KẾT QUẢ: $LEAKS chỗ lộ. Xoá hoặc che bằng stg_mask rồi chạy lại."
  exit 1
fi
echo "KẾT QUẢ: sạch (${#NEEDLES[@]} needle, 3 mẫu)."
exit 0
