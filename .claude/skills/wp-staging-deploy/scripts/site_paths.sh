#!/bin/bash
# site_paths.sh — dựng danh sách path toàn site để purge và làm nóng sau khi đổi phần dùng chung (nút nổi, header, footer, CSS inline).
#
# Dùng:  site_paths.sh --host https://example.com [--out paths.txt] [--max-page 40] [--sleep 1] [--archive /blog/ ...] [--extra file]
#   --host      gốc site, gồm scheme (bắt buộc)
#   --out       file kết quả, mỗi dòng một path (mặc định paths.txt)
#   --max-page  số trang phân trang tối đa thử cho mỗi trang lưu trữ (mặc định 40)
#   --sleep     nghỉ giữa các request dò phân trang, không dưới 1 giây (mặc định 1)
#   --archive   trang lưu trữ cần dò thêm /page/N/ ngoài sitemap chuyên mục (*category*), lặp được. Ví dụ trang blog, trang lưu trữ CPT
#   --extra     file path ngoài sitemap (trang noindex như trang cảm ơn, trang lưu trữ CPT), mỗi dòng một path
# Cách làm: đọc sitemap index (Rank Math, Yoast: /sitemap_index.xml; WordPress lõi: /wp-sitemap.xml), lấy mọi <loc> không phải ảnh,
#   rồi dò /page/2/, /page/3/… của từng trang lưu trữ tới khi gặp mã khác 200. Trang phân trang không nằm trong sitemap
#   nhưng vẫn có cache riêng (site agency mẫu 28/10/2026: 21 trang phân trang ngoài 346 URL sitemap).
# Chỉ gửi GET. Không purge, không ghi dữ liệu site. Chia lô ≤12 path: split -l 12 <out> lo_ rồi nối mỗi file bằng dấu phẩy.
set -u
HOST=""; OUT="paths.txt"; MAXP=40; SLP=1; ARCH=(); EXTRA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST="${2%/}"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --max-page) MAXP="$2"; shift 2 ;;
    --sleep) SLP="$2"; shift 2 ;;
    --archive) ARCH+=("$2"); shift 2 ;;
    --extra) EXTRA="$2"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "site_paths.sh: tham số lạ $1" >&2; exit 2 ;;
  esac
done
[ -n "$HOST" ] || { echo "site_paths.sh: thiếu --host" >&2; exit 2; }
case "$SLP" in 0|0.*) SLP=1 ;; esac
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
locs() { curl -s --max-time 60 "$1" | grep -o '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g'; }
IDX=""
for s in /sitemap_index.xml /wp-sitemap.xml /sitemap.xml; do
  if locs "$HOST$s" > "$TMP/idx" && [ -s "$TMP/idx" ]; then IDX="$s"; break; fi
done
[ -n "$IDX" ] || { echo "site_paths.sh: không đọc được sitemap của $HOST" >&2; exit 1; }
: > "$TMP/urls"; : > "$TMP/cat"
while read -r sm; do
  case "$sm" in
    *.xml|*.xml\?*) locs "$sm" > "$TMP/one"; cat "$TMP/one" >> "$TMP/urls"; case "$sm" in *category*) cat "$TMP/one" >> "$TMP/cat" ;; esac ;;
    *) echo "$sm" >> "$TMP/urls" ;;
  esac
done < "$TMP/idx"
grep -v -i -E '\.(jpe?g|png|webp|gif|svg|avif)$' "$TMP/urls" | sed "s#^$HOST##" | grep '^/' | sort -u > "$TMP/paths"
{ sed "s#^$HOST##" "$TMP/cat" | grep '^/'; [ ${#ARCH[@]} -gt 0 ] && printf '%s\n' "${ARCH[@]}"; } | sort -u > "$TMP/arch"
: > "$TMP/paged"
while read -r a; do
  [ -n "$a" ] || continue
  n=2
  while [ "$n" -le "$MAXP" ]; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$HOST${a%/}/page/$n/")
    sleep "$SLP"
    [ "$code" = 200 ] || break
    echo "${a%/}/page/$n/" >> "$TMP/paged"; n=$((n + 1))
  done
done < "$TMP/arch"
[ -n "$EXTRA" ] && grep '^/' "$EXTRA" > "$TMP/extra" || : > "$TMP/extra"
sort -u "$TMP/paths" "$TMP/paged" "$TMP/extra" > "$OUT"
echo "sitemap $IDX: $(wc -l < "$TMP/paths" | tr -d ' ') path · phân trang: $(wc -l < "$TMP/paged" | tr -d ' ') · thêm: $(wc -l < "$TMP/extra" | tr -d ' ') · tổng $(wc -l < "$OUT" | tr -d ' ') → $OUT"
