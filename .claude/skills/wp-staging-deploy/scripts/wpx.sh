#!/bin/bash
# wpx.sh — chạy một file PHP bằng `wp eval-file` trên production hoặc staging của site.
#
# Dùng:  wpx.sh --site <site.json> [--slot 1|2] [--tag <tên>] [--dry] <prod|stg> <file.php> [KHOÁ=GIÁ_TRỊ ...]
#   --site   hồ sơ site dạng JSON (mặc định: $WPX_SITE). Cùng khoá với site.json của wp-ucss:
#              ssh, docroot, php_bin, wp_bin, wp_user          bắt buộc
#              stg_docroot_glob                                bắt buộc khi chạy stg. Mẫu glob trên server phải khớp đúng 1 thư mục
#              wpcli_home (mặc định /tmp/wpcli-home), wpcli_lock_dir (mặc định /tmp), memory_limit (mặc định 512M)
#   --slot   khe WP-CLI: giữ <wpcli_lock_dir>/wpcli-slot-<n>.lock bằng flock, chờ tối đa 300 giây (mặc định 1)
#   --tag    thư mục con trong wpcli_home cho file của phiên, chữ thường, số, - và _ (mặc định wpx)
#   --dry    chỉ in lệnh sẽ chạy trên server. Không ssh, không scp
#   KHOÁ=GIÁ_TRỊ  biến môi trường cho script PHP. Script đặt biến sau `sudo -u <wp_user>`, vì sudo xoá biến đặt trước nó
# Chạy bằng user web, cd /tmp, PHP -d memory_limit, display_errors=0. ssh luôn có -n để không đọc mất stdin của vòng lặp.
# Giá trị biến được quote bằng printf %q, nên shell đăng nhập trên server phải là bash.
# stg: script đọc host staging bằng stg_load (stg_env.sh), rồi che đúng chuỗi host và đúng đường dẫn thư mục staging
#      trong mọi output. Không nạp được host thì dừng, không chạy.
# Mã thoát: mã của lệnh trên server · 2 lỗi dùng · 4 hồ sơ thiếu khoá, staging không khớp 1 thư mục hoặc không che được host.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/stg_env.sh"

usage() { sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; }

SITE="${WPX_SITE:-}"; SLOT=1; TAG=wpx; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --site) SITE="${2:-}"; shift 2 ;;
    --slot) SLOT="${2:-}"; shift 2 ;;
    --tag) TAG="${2:-}"; shift 2 ;;
    --dry) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "LỖI: tuỳ chọn lạ: $1" >&2; exit 2 ;;
    *) break ;;
  esac
done
[ $# -ge 2 ] || { echo "LỖI: thiếu <prod|stg> <file.php>. Xem --help." >&2; exit 2; }
SIDE="$1"; F="$2"; shift 2
case "$SIDE" in prod|stg) ;; *) echo "LỖI: phía phải là prod hoặc stg." >&2; exit 2 ;; esac
[ -f "$F" ] || { echo "LỖI: không thấy file $F." >&2; exit 2; }
case "$SLOT" in 1|2) ;; *) echo "LỖI: --slot chỉ nhận 1 hoặc 2." >&2; exit 2 ;; esac
case "$TAG" in ''|*[!a-z0-9_-]*) echo "LỖI: --tag chỉ gồm chữ thường, số, - và _." >&2; exit 2 ;; esac
[ -n "$SITE" ] && [ -f "$SITE" ] || { echo "LỖI: cần --site <site.json> hoặc WPX_SITE." >&2; exit 2; }

ENVS=""
for kv in "$@"; do
  k="${kv%%=*}"
  case "$kv" in *=*) ;; *) echo "LỖI: đối số '$kv' không có dạng KHOÁ=GIÁ_TRỊ." >&2; exit 2 ;; esac
  case "$k" in ''|[0-9]*|*[!A-Za-z0-9_]*) echo "LỖI: tên biến '$k' không hợp lệ." >&2; exit 2 ;; esac
  ENVS="$ENVS $k=$(printf '%q' "${kv#*=}")"
done

cfg() { python3 -I -c 'import json,sys
d = json.load(open(sys.argv[1])); v = d.get(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
sys.exit("wpx.sh: hồ sơ site thiếu khoá " + sys.argv[2]) if v in (None, "") else print(v)' "$SITE" "$@"; }
H=$(cfg ssh) && DR=$(cfg docroot) && PHP=$(cfg php_bin) && WPB=$(cfg wp_bin) && WU=$(cfg wp_user) \
  && WH=$(cfg wpcli_home /tmp/wpcli-home) && LD=$(cfg wpcli_lock_dir /tmp) && MEM=$(cfg memory_limit 512M) || exit 4
GLOB=""
if [ "$SIDE" = stg ]; then GLOB=$(cfg stg_docroot_glob) || exit 4; fi

b="$(basename "$F")"
q() { printf '%q' "$1"; }
UP="$WH/.up-$TAG-$b"; DST="$WH/$TAG/$b"
build_cmd() { # $1 = docroot đã giải
  printf 'mkdir -p %s && cp %s %s && rm -f %s && chown -R %s %s && cd /tmp && flock -w 300 %s sudo -u %s HOME=%s%s %s -d memory_limit=%s -d display_errors=0 -d error_reporting=0 %s --path=%s eval-file %s 2>&1' \
    "$(q "$WH/$TAG")" "$(q "$UP")" "$(q "$DST")" "$(q "$UP")" "$(q "$WU:$WU")" "$(q "$WH/$TAG")" \
    "$(q "$LD/wpcli-slot-$SLOT.lock")" "$(q "$WU")" "$(q "$WH")" "$ENVS" "$(q "$PHP")" "$(q "$MEM")" "$(q "$WPB")" "$(q "$1")" "$(q "$DST")"
}

if [ "$DRY" = 1 ]; then
  if [ "$SIDE" = prod ]; then R="$DR"; else R="<thư mục khớp $GLOB>"; fi
  echo "[wpx dry] scp $F -> $H:$UP"
  echo "[wpx dry] ssh -n $H $(build_cmd "$R")"
  exit 0
fi

mask_root() { WPX_R="$1" perl -pe 'BEGIN { $r = $ENV{WPX_R}; } s/\Q$r\E/<stg-root>/g if $r ne ""'; }
R="$DR"
if [ "$SIDE" = stg ]; then
  [ -n "${STG_ALIAS:-}" ] || { STG_ALIAS="$H"; export STG_ALIAS; }
  stg_load || { echo "wpx.sh: không nạp được host staging, dừng." >&2; exit 4; }
  R=$(SSH "$H" "set -- $GLOB; if [ \$# -eq 1 ] && [ -d \"\$1\" ]; then printf '%s' \"\$1\"; else echo \"mẫu staging khớp \$# mục\"; exit 4; fi")
  rc=$?
  if [ "$rc" -ne 0 ] || [ -z "$R" ] || [ "${R#/}" = "$R" ]; then
    printf '%s\n' "$R" | stg_mask >&2
    echo "wpx.sh: stg_docroot_glob không khớp đúng 1 thư mục, dừng." >&2; exit 4
  fi
fi

scp -q "$F" "$H:$UP" 2>&1 | grep -v -E "$STG_SSH_NOISE|^\*\* WARNING" >&2
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "wpx.sh: scp lỗi, dừng." >&2; exit 4; }

set -o pipefail
if [ "$SIDE" = prod ]; then
  ssh -n -o BatchMode=yes "$H" "$(build_cmd "$R")" 2>&1 | { grep -v -E "$STG_SSH_NOISE|^\*\* WARNING" || true; }
  exit "${PIPESTATUS[0]}"
fi
ssh -n -o BatchMode=yes "$H" "$(build_cmd "$R")" 2>&1 | { grep -v -E "$STG_SSH_NOISE|^\*\* WARNING" || true; } | mask_root "$R" | stg_mask
st=("${PIPESTATUS[@]}")
[ "${st[3]}" -eq 0 ] || exit 4
exit "${st[0]}"
