#!/bin/bash
# Kiểm từ ngoài các điểm lộ phổ biến của WordPress: so mã HTTP thực tế với mã mong đợi. Chỉ gửi GET.
# exposure_check.sh <https://domain> [file danh sách "mã path", mặc định exposure_default.txt cạnh script] [--show-location]
# Không in Location khi thiếu --show-location, vì Location của wp-activate.php hoặc wp-admin có thể lộ slug đăng nhập ẩn.
# Mã mong đợi có thể ghi nhiều giá trị: "403|404". Exit 1 khi có dòng FAIL.
# Path chứa {RAND} được thay bằng chuỗi ngẫu nhiên mới mỗi lần chạy (đặt WPS_RAND để cố định khi test).
#   Dòng có {RAND} là phép thử "URL không tồn tại": 200 rỗng không được coi là OK.
# Biến môi trường: EXPOSURE_CURL_CONFIG = file cấu hình curl (-K), dùng cho staging có Basic Auth.
# Mã thoát: 0 mọi dòng OK · 1 có dòng FAIL · 2 sai tham số hoặc thiếu file danh sách.
case "${1:-}" in -h|--help|"") sed -n '2,/^# Mã thoát/p' "$0" | sed 's/^# \{0,1\}//'; [ -z "${1:-}" ] && exit 2; exit 0;; esac
B="$1"; F="${2:-$(dirname "$0")/exposure_default.txt}"; SHOW=0
[ "$3" = "--show-location" ] || [ "$2" = "--show-location" ] && SHOW=1
[ "$2" = "--show-location" ] && F="$(dirname "$0")/exposure_default.txt"
[ -f "$F" ] || { echo "Không thấy file danh sách: $F" >&2; exit 2; }
RND="${WPS_RAND:-$(printf '%04x%04x' $RANDOM $RANDOM)}"
KOPT=""; [ -n "${EXPOSURE_CURL_CONFIG:-}" ] && KOPT="-K"
fail=0
while read -r exp path note; do
  [ -z "$path" ] && continue
  case "$exp" in \#*) continue;; esac
  isrand=0; case "$path" in *'{RAND}'*) isrand=1; path="${path//\{RAND\}/$RND}";; esac
  if [ -n "$KOPT" ]; then out=$(curl -s -K "$EXPOSURE_CURL_CONFIG" -o /dev/null -m 20 -w '%{http_code} %{size_download} %{redirect_url}' "$B$path")
  else out=$(curl -s -o /dev/null -m 20 -w '%{http_code} %{size_download} %{redirect_url}' "$B$path"); fi
  code=${out%% *}; rest=${out#* }; size=${rest%% *}; loc=${rest#* }; [ "$loc" = "$rest" ] && loc=""
  extra=""
  if echo "|$exp|" | grep -q "|$code|"; then st=OK
  elif [ "$code" = 200 ] && [ "$size" = 0 ] && [ $isrand = 0 ]; then st=OK; extra="(200 rỗng)"
  else st=FAIL; fail=1; fi
  [ -n "$loc" ] && { [ $SHOW = 1 ] && extra="→ $loc" || extra="→ (có redirect)"; }
  printf '%-4s %-8s %-3s %-55s %s %s\n' "$st" "$exp" "$code" "$path" "$extra" "$note"
done < "$F"
exit $fail
