#!/bin/bash
# Kiểm site còn sống sau mỗi mốc thay đổi: mã HTTP, dung lượng, title, lỗi fatal. Chỉ đọc.
# sitecheck.sh <https://domain> <nhãn mốc> <file đường dẫn, mỗi dòng một path> [thư mục lưu HTML]
# In một dòng mỗi URL. Exit 1 khi có mã khác 2xx/3xx hoặc có chuỗi lỗi fatal.
B="$1"; L="$2"; P="$3"; OUT="${4:-${TMPDIR:-/tmp}/sitecheck}"
mkdir -p "$OUT"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
bad=0
while read -r u; do
  [ -z "$u" ] && continue
  case "$u" in \#*) continue;; esac
  f="$OUT/${L}_$(echo "$u" | tr '/?&=' '____').html"
  r=$(curl -s -A "$UA" -o "$f" -w '%{http_code} %{size_download}' --max-time 60 "$B$u")
  t=$(grep -oE '<title>[^<]{0,70}' "$f" | head -1 | sed 's/<title>//')
  fatal=$(grep -ciE 'Fatal error|critical error|Parse error|There has been a critical' "$f")
  code=${r%% *}
  { [ "$code" -ge 400 ] || [ "$fatal" != 0 ]; } && bad=1
  printf '%-8s %-30s %s fatal=%s title=%s\n' "$L" "$u" "$r" "$fatal" "$t"
done < "$P"
exit $bad
