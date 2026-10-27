#!/bin/bash
# Quét một thư mục xem có lộ secret, host staging hoặc slug đăng nhập không. Không bao giờ in giá trị needle.
# Chạy trước khi báo xong một đợt và trước khi mở HTML evidence.
#
# Dùng:  leak_scan.sh <thư-mục> [--secrets-dir D] [--needle-file F]... [--min-len N] [--patterns-only] [-h]
#
# Needle lấy từ:
#   1. Giá trị của khoá có tên KEY/TOKEN/SECRET/PASS/PASSWORD/PWD/LICEN?E/SLUG/STG_HOST/LOGIN_URL/CREDENTIAL/ADMIN
#      trong .env, *.env, *.env.bak*, *.txt của .agent-secrets (đọc bằng regex, không dùng `source`).
#      Bỏ khoá kết thúc bằng _PATH hoặc APPLICATION_CREDENTIALS.
#   2. Mỗi dòng của --needle-file (bỏ dòng trống và dòng bắt đầu bằng #). Dùng cho mã 2FA, host, slug ghi tay.
#   3. Biến môi trường STG_HOST nếu có (stg_env.sh đặt biến này).
# Mỗi needle được tìm ở dạng gốc và dạng JSON-escape (/ thành \/), trong nội dung file (cả nhị phân) và trong tên file.
# Thêm mẫu: AIza..., WP_API...=, ROOT_SSH_P...=, *_PASSWORD=, wp-login.php có dấu ? theo sau, khoá riêng PEM.
# Giới hạn: không bắt dạng URL-encode hay base64 của needle.
#
# Mã thoát: 0 sạch · 1 có lộ · 2 lỗi dùng hoặc thiếu nguồn needle.
set -u

usage() { sed -n "2,17p" "$0" | sed 's/^# \{0,1\}//'; }

SCAN_DIR=""; SECRETS_DIR="${AGENT_SECRETS_DIR:-}"; MIN_LEN=6; PATTERNS_ONLY=0
NEEDLE_FILES=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --secrets-dir) SECRETS_DIR="${2:-}"; shift 2 ;;
    --needle-file) NEEDLE_FILES+=("${2:-}"); shift 2 ;;
    --min-len) MIN_LEN="${2:-}"; shift 2 ;;
    --patterns-only) PATTERNS_ONLY=1; shift ;;
    -*) echo "LỖI: tuỳ chọn lạ: $1" >&2; exit 2 ;;
    *) if [ -z "$SCAN_DIR" ]; then SCAN_DIR="$1"; shift; else echo "LỖI: chỉ nhận một thư mục." >&2; exit 2; fi ;;
  esac
done
[ -n "$SCAN_DIR" ] && [ -d "$SCAN_DIR" ] || { echo "LỖI: cần một thư mục để quét. Xem --help." >&2; exit 2; }
case "$MIN_LEN" in ''|*[!0-9]*) echo "LỖI: --min-len phải là số." >&2; exit 2 ;; esac
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -n "$SECRETS_DIR" ] || SECRETS_DIR="$HERE/../.agent-secrets"
SCAN_ABS="$(cd "$SCAN_DIR" && pwd -P)"

NEEDLES=(); LABELS=()
add_needle() { # giá trị, nhãn
  local v="$1" l="$2"
  [ "${#v}" -ge "$MIN_LEN" ] || return 0
  NEEDLES+=("$v"); LABELS+=("$l")
  case "$v" in */*) NEEDLES+=("${v//\//\\/}"); LABELS+=("$l (json)") ;; esac
}

KEY_RE='(KEY|TOKEN|SECRET|PASS|PASSWORD|PWD|LICEN[CS]E|SLUG|STG_HOST|LOGIN_URL|CREDENTIAL|ADMIN)'
LINE_RE='^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$'

if [ "$PATTERNS_ONLY" -eq 0 ]; then
  if [ -d "$SECRETS_DIR" ]; then
    SD_ABS="$(cd "$SECRETS_DIR" && pwd -P)"
    case "$SCAN_ABS/" in "$SD_ABS"/*) echo "LỖI: thư mục quét nằm trong kho secret. Chọn thư mục deliverable." >&2; exit 2 ;; esac
    shopt -s nullglob dotglob 2>/dev/null
    for f in "$SD_ABS"/.env "$SD_ABS"/.env.bak* "$SD_ABS"/*.env "$SD_ABS"/*.env.bak* "$SD_ABS"/*.txt; do
      [ -f "$f" ] || continue
      case "$f" in *.example) continue ;; esac
      base="$(basename "$f")"
      while IFS= read -r line || [ -n "$line" ]; do
        line="${line%$'\r'}"
        [[ "$line" =~ $LINE_RE ]] || continue
        k="${BASH_REMATCH[2]}"; v="${BASH_REMATCH[3]}"
        ku="$(printf '%s' "$k" | tr '[:lower:]' '[:upper:]')"
        if [[ "$ku" =~ $KEY_RE ]] && ! [[ "$ku" =~ (_PATH|APPLICATION_CREDENTIALS)$ ]]; then ok=1; else ok=0; fi
        [ "$ok" -eq 1 ] || continue
        v="${v%"${v##*[![:space:]]}"}"
        case "$v" in \"*\") v="${v#\"}"; v="${v%\"}" ;; \'*\') v="${v#\'}"; v="${v%\'}" ;; esac
        add_needle "$v" "$k@$base"
        case "$k" in
          *STG_HOST*) h="${v#*://}"; h="${h%%/*}"; [ "$h" = "$v" ] || add_needle "$h" "$k@$base (host)" ;;
        esac
      done < "$f"
    done
  fi
  for nf in ${NEEDLE_FILES[@]+"${NEEDLE_FILES[@]}"}; do
    [ -f "$nf" ] || { echo "LỖI: không đọc được --needle-file: $(basename "$nf")" >&2; exit 2; }
    n=0
    while IFS= read -r line || [ -n "$line" ]; do
      n=$((n+1)); line="${line%$'\r'}"
      case "$line" in ''|'#'*) continue ;; esac
      add_needle "$line" "needle-file:$(basename "$nf"):dòng $n"
    done < "$nf"
  done
  if [ -n "${STG_HOST:-}" ]; then add_needle "$STG_HOST" "env:STG_HOST"; fi
  if [ "${#NEEDLES[@]}" -eq 0 ]; then
    echo "LỖI: không nạp được needle nào (thiếu kho secret ở $(basename "$SECRETS_DIR"), --needle-file hoặc STG_HOST)." >&2
    echo "Dùng --patterns-only nếu chỉ muốn quét mẫu." >&2
    exit 2
  fi
fi

umask 077
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
LEAKS=0

safe_path() { # thay mọi needle trong đường dẫn bằng ***
  local p="$1" n
  for n in ${NEEDLES[@]+"${NEEDLES[@]}"}; do p="${p//"$n"/***}"; done
  printf '%s' "$p"
}

i=0
while [ "$i" -lt "${#NEEDLES[@]}" ]; do
  n="${NEEDLES[$i]}"; l="${LABELS[$i]}"; i=$((i+1))
  printf '%s\n' "$n" > "$TMP"
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    echo "LỘ nội dung [$l] trong: $(safe_path "$p")"; LEAKS=$((LEAKS+1))
  done < <(grep -rlaF --exclude-dir=.agent-secrets -f "$TMP" -- "$SCAN_DIR" 2>/dev/null)
  while IFS= read -r p; do
    case "$p" in *"$n"*) echo "LỘ tên file [$l] trong: $(safe_path "$p")"; LEAKS=$((LEAKS+1)) ;; esac
  done < <(find "$SCAN_DIR" -name .agent-secrets -prune -o -print 2>/dev/null)
done

PATTERNS=(
  'AIza[0-9A-Za-z_-]{20,}'
  'WP_API[A-Z_]*='
  'ROOT_SSH_P[A-Z_]*='
  '(MYSQL_ROOT|AAPANEL|FTP|DB)_PASSWORD[A-Za-z_]*='
  'wp-login\.php\?'
  'BEGIN [A-Z ]*PRIVATE KEY'
)
for pat in "${PATTERNS[@]}"; do
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    echo "LỘ mẫu [$pat] trong: $(safe_path "$p")"; LEAKS=$((LEAKS+1))
  done < <(grep -rlaE --exclude-dir=.agent-secrets -e "$pat" -- "$SCAN_DIR" 2>/dev/null)
done

if [ "$LEAKS" -gt 0 ]; then
  echo "KẾT QUẢ: $LEAKS chỗ lộ. Xoá hoặc che trước khi báo xong. Coi secret đã lộ là cần đổi."
  exit 1
fi
echo "KẾT QUẢ: sạch (${#NEEDLES[@]} needle, ${#PATTERNS[@]} mẫu)."
exit 0
