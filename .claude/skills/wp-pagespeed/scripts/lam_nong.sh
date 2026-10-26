#!/bin/bash
# lam_nong.sh: làm nóng page cache LiteSpeed của một site, mỗi URL chạy nhiều bản cache.
# Bản cache (-V): guest-d khách mới desktop · guest-m khách mới mobile · ret-d khách quay lại desktop · ret-m khách quay lại mobile.
#   Khách quay lại mang cookie _lscache_vary, script lấy cookie bằng POST tới guest.vary.php của LiteSpeed (chỉ khi -V có ret-*).
# Kiểu Accept (-W): webp (mặc định) giả Chrome thật, header Accept có image/webp. plain giả bot, Accept: */*. both chạy cả hai (gấp đôi lượt).
#   Khối WebP của .htaccess tách cache theo Accept, nên làm nóng bản plain không làm nóng bản khách thật vào. Lỗi đã gặp 21/10/2026:
#   bản cũ chỉ làm nóng plain, khách thật vẫn miss. Lượt đầu ở 40 URL nhiều khách nhất: bản mobile hit 5%, desktop 95% vì thiếu guest-m.
# Chạy 1 luồng. Không purge, không ghi dữ liệu site. Chỉ gửi GET tới --host, nên chạy đúng site đã được phép làm nóng.
#
# Cách dùng:
#   lam_nong.sh --host https://example.com                  mọi URL trong sitemap
#   lam_nong.sh --host https://example.com /a/ /b/          chỉ các path này (hoặc URL đầy đủ cùng host)
#   lam_nong.sh --host https://example.com -f danh-sach.txt mỗi dòng một path hoặc URL
# Tuỳ chọn:
#   --host URL        gốc site, gồm scheme (bắt buộc)
#   --sitemap URL|FILE  sitemap hoặc sitemap index. Mặc định thử /sitemap_index.xml, /wp-sitemap.xml, /sitemap.xml của --host
#   -f FILE           danh sách path hoặc URL, mỗi dòng một mục
#   -o FILE.tsv       ghi từng lượt: path, variant, code, lscache, ttfb, accept. Mặc định $TMPDIR/lam_nong_<ngày giờ>.tsv
#   -s GIÂY           nghỉ giữa các lượt, không dưới 0.5. Mặc định 0.5
#   -V LIST           chọn bản, ví dụ -V guest-d,guest-m. Mặc định cả 4
#   -W KIỂU           webp (mặc định), plain hoặc both
#   --retry-wait GIÂY chờ trước khi thử lại lượt lỗi 000 hoặc 5xx đúng 1 lần. Mặc định 60
#   --guest-vary-path đường dẫn guest.vary.php. Mặc định /wp-content/plugins/litespeed-cache/guest.vary.php
#   -n, --dry-run     in kế hoạch (URL, bản, Accept), không gửi request nào
#   -q                không in tiến độ
#   -h, --help        in trợ giúp này
# Mã thoát: 0 xong, 1 sai tham số hoặc không có URL hoặc không lấy được cookie, 2 còn lượt lỗi sau khi thử lại.
# Sau mỗi lần purge theo URL: chạy lại với đúng các path vừa purge. Purge xoá cả bản webp và plain của URL đó.

usage() { sed -n '2,/^# Sau mỗi lần purge/p' "$0" | sed 's/^# \{0,1\}//'; }

HOST=""; SITEMAP=""; LIST=""; OUT=""; SLEEP=0.5; VARS="guest-d,guest-m,ret-d,ret-m"; MODE="webp"; QUIET=0; DRY=0
RETRY_WAIT=60; GUEST_PATH="/wp-content/plugins/litespeed-cache/guest.vary.php"; PATHS=()
ACC_WEBP='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
ACC_PLAIN='*/*'
LANG_HDR='vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
UD='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
UM='Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36'

need() { [ $# -ge 2 ] || { echo "Thiếu giá trị cho $1." >&2; exit 1; }; }
while [ $# -gt 0 ]; do
  case "$1" in
    --host) need "$@"; HOST="${2%/}"; shift 2 ;;
    --sitemap) need "$@"; SITEMAP="$2"; shift 2 ;;
    -f) need "$@"; LIST="$2"; shift 2 ;;
    -o) need "$@"; OUT="$2"; shift 2 ;;
    -s) need "$@"; SLEEP="$2"; shift 2 ;;
    -V) need "$@"; VARS="$2"; shift 2 ;;
    -W) need "$@"; MODE="$2"; shift 2 ;;
    --retry-wait) need "$@"; RETRY_WAIT="$2"; shift 2 ;;
    --guest-vary-path) need "$@"; GUEST_PATH="$2"; shift 2 ;;
    -n|--dry-run) DRY=1; shift ;;
    -q) QUIET=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Tham số lạ: $1 (xem --help)." >&2; exit 1 ;;
    *) PATHS+=("$1"); shift ;;
  esac
done

[ -n "$HOST" ] || { echo "Thiếu --host (ví dụ --host https://example.com)." >&2; exit 1; }
case "$HOST" in http://*|https://*) ;; *) echo "--host phải có scheme http:// hoặc https://." >&2; exit 1 ;; esac
case "$MODE" in webp) MODES=(webp) ;; plain) MODES=(plain) ;; both) MODES=(webp plain) ;; *) echo "-W chỉ nhận webp, plain hoặc both." >&2; exit 1 ;; esac
awk -v s="$SLEEP" 'BEGIN { exit !(s ~ /^[0-9]+([.][0-9]+)?$/ && s >= 0.5) }' || { echo "-s phải là số từ 0.5 trở lên (nghỉ ít hơn làm tải site)." >&2; exit 1; }
awk -v s="$RETRY_WAIT" 'BEGIN { exit !(s ~ /^[0-9]+([.][0-9]+)?$/) }' || { echo "--retry-wait phải là số giây." >&2; exit 1; }
IFS=',' read -r -a VV <<< "$VARS"
NEED_COOKIE=0
for v in "${VV[@]}"; do
  case "$v" in guest-d|guest-m) ;; ret-d|ret-m) NEED_COOKIE=1 ;; *) echo "-V có bản lạ: $v (chỉ guest-d, guest-m, ret-d, ret-m)." >&2; exit 1 ;; esac
done
[ -z "$OUT" ] && OUT="${TMPDIR:-/tmp}/lam_nong_$(date +%Y%m%d-%H%M%S).tsv"

TMP=$(mktemp -d "${TMPDIR:-/tmp}/lam_nong.XXXXXX"); CJ="$TMP/guest.jar"; URLS="$TMP/urls.txt"
trap 'rm -rf "$TMP"' EXIT

# Chuẩn hoá về path: bỏ scheme và host nếu trùng --host (bỏ qua www.), bỏ khoảng trắng, loại trùng. Mục khác host bị bỏ và báo.
norm() {
  python3 -I -c '
import sys
from urllib.parse import urlsplit
base = urlsplit(sys.argv[1]).netloc.lower()
strip = lambda h: h[4:] if h.startswith("www.") else h
seen, out = set(), []
for ln in sys.stdin:
    s = "".join(ln.split())
    if not s:
        continue
    if s.startswith(("http://", "https://")):
        u = urlsplit(s)
        if strip(u.netloc.lower()) != strip(base):
            sys.stderr.write("Bỏ qua URL khác host: %s\n" % s)
            continue
        s = u.path + ("?" + u.query if u.query else "")
    if s.startswith("/") and s not in seen:
        seen.add(s)
        out.append(s)
print("\n".join(out))
' "$HOST"
}

from_sitemap() {
  python3 -I -c '
import re, sys, urllib.request
host, sm = sys.argv[1], sys.argv[2]
def get(u):
    if not u.startswith(("http://", "https://")):
        return open(u, encoding="utf-8").read()
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 Chrome/141.0.0.0"})
    return urllib.request.urlopen(r, timeout=60).read().decode("utf-8", "replace")
def walk(u, depth=0):
    xml = get(u)
    urls = []
    for blk in re.findall(r"<(?:url|sitemap)>(.*?)</(?:url|sitemap)>", xml, re.S):
        m = re.search(r"<loc>\s*([^<]+?)\s*</loc>", blk)
        if not m:
            continue
        loc = m.group(1).replace("&amp;", "&")
        if loc.endswith(".xml") and depth < 3:
            urls += walk(loc, depth + 1)
        elif not loc.endswith(".xml"):
            urls.append(loc)
    return urls
cands = [sm] if sm else [host + "/sitemap_index.xml", host + "/wp-sitemap.xml", host + "/sitemap.xml"]
last = None
for c in cands:
    try:
        urls = walk(c)
    except Exception as e:
        last = e
        continue
    if urls:
        print("\n".join(urls))
        sys.exit(0)
sys.stderr.write("Không đọc được sitemap (%s)\n" % last)
sys.exit(1)
' "$HOST" "$SITEMAP"
}

if [ -n "$LIST" ]; then
  [ -r "$LIST" ] || { echo "Không đọc được danh sách: $LIST" >&2; exit 1; }
  norm < "$LIST" > "$URLS"
elif [ ${#PATHS[@]} -gt 0 ]; then
  printf '%s\n' "${PATHS[@]}" | norm > "$URLS"
else
  from_sitemap | norm > "$URLS" || { echo "Không lấy được danh sách URL từ sitemap. Truyền path hoặc -f." >&2; exit 1; }
fi
N=$(grep -c . "$URLS" 2>/dev/null); N=${N:-0}
[ "$N" -gt 0 ] || { echo "Không có URL nào để làm nóng." >&2; exit 1; }

if [ "$DRY" -eq 1 ]; then
  echo "DRY-RUN: $N URL x ${#VV[@]} bản x ${#MODES[@]} kiểu Accept = $((N * ${#VV[@]} * ${#MODES[@]})) lượt. Không gửi request nào."
  echo "Bản: ${VARS}. Accept: ${MODES[*]}. Nghỉ ${SLEEP} s giữa các lượt. Cookie khách quay lại: $([ $NEED_COOKIE -eq 1 ] && echo "có (POST $GUEST_PATH)" || echo "không cần")."
  head -5 "$URLS" | sed 's/^/  /'
  [ "$N" -gt 5 ] && echo "  ... và $((N - 5)) URL nữa"
  exit 0
fi

if [ "$NEED_COOKIE" -eq 1 ]; then
  W=$RETRY_WAIT; awk -v w="$W" 'BEGIN { exit !(w > 5) }' && W=5
  for i in 1 2 3; do
    curl -s -o /dev/null -c "$CJ" -A "$UD" -X POST --max-time 30 "$HOST$GUEST_PATH" && grep -q _lscache_vary "$CJ" 2>/dev/null && break
    sleep "$W"
  done
  grep -q _lscache_vary "$CJ" 2>/dev/null || { echo "Không lấy được cookie _lscache_vary từ $GUEST_PATH. Bỏ ret-d,ret-m khỏi -V hoặc kiểm đường dẫn --guest-vary-path." >&2; exit 1; }
fi

printf 'path\tvariant\tcode\tlscache\tttfb\taccept\n' > "$OUT" || { echo "Không ghi được $OUT" >&2; exit 1; }
ERR=0; I=0

one() { # path variant kiểu -> in "code<TAB>lscache<TAB>ttfb"
  local p="$1" v="$2" a="$3" ua="$UD" acc="$ACC_WEBP" h="$TMP/h.$$" r c
  local ck=()
  case "$v" in *-m) ua="$UM" ;; esac
  case "$v" in ret-*) ck=(-b "$CJ") ;; esac
  [ "$a" = plain ] && acc="$ACC_PLAIN"
  : > "$h"
  r=$(curl -s -o /dev/null -D "$h" "${ck[@]}" -A "$ua" -H "Accept: $acc" -H "Accept-Language: $LANG_HDR" --compressed --max-time 90 -w '%{http_code}\t%{time_starttransfer}' "$HOST$p")
  c=$(grep -i '^x-litespeed-cache:' "$h" 2>/dev/null | awk '{print $2}' | tr -d '\r')
  printf '%s\t%s\t%s\n' "${r%%$'\t'*}" "${c:--}" "${r#*$'\t'}"
}

while IFS= read -r p; do
  I=$((I + 1))
  for m in "${MODES[@]}"; do
    for v in "${VV[@]}"; do
      row=$(one "$p" "$v" "$m"); code=${row%%$'\t'*}
      if [ "$code" = "000" ] || [ "${code:0:1}" = "5" ]; then
        sleep "$RETRY_WAIT"; row=$(one "$p" "$v" "$m"); code=${row%%$'\t'*}
      fi
      case "$code" in 2*|3*) ;; *) ERR=$((ERR + 1)) ;; esac
      printf '%s\t%s\t%s\t%s\n' "$p" "$v" "$row" "$m" >> "$OUT"
      sleep "$SLEEP"
    done
  done
  [ "$QUIET" -eq 0 ] && [ $((I % 50)) -eq 0 ] && echo "  $I/$N URL, $(date +%H:%M:%S)" >&2
done < "$URLS"

echo "Xong $N URL x ${#VV[@]} bản x ${#MODES[@]} kiểu Accept (${MODES[*]}). File: $OUT"
python3 -I - "$OUT" <<'PY'
import csv, sys, collections
c = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(sys.argv[1]), delimiter='\t'):
    c[r['variant'] + ' ' + r['accept']][r['lscache'] if r['code'].startswith(('2', '3')) else 'loi'] += 1
for v, k in c.items():
    n = sum(k.values())
    print('  %-14s %4d lượt: đã hit sẵn %4d (%.0f%%), vừa làm nóng (miss) %4d, không cache %d, lỗi %d' % (v, n, k['hit'], 100.0 * k['hit'] / n, k['miss'], k['-'], k['loi']))
PY
[ "$ERR" -gt 0 ] && { echo "Có $ERR lượt lỗi sau khi thử lại." >&2; exit 2; }
exit 0
