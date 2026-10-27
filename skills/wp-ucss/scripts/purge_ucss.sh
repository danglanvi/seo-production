#!/bin/bash
# purge_ucss.sh (wp-ucss): purge LiteSpeed theo URL qua WP-CLI trên server, mỗi dòng của F là 1 nhóm ≤12 path. Tự chép purge_urls.php lên /tmp/wpcli-home/wp-ucss/ trước khi chạy.
# Biến: UCSS_SITE=<site.json> (lấy ssh, docroot, php_bin, wp_bin, wp_user), DRY=1 mặc định (chỉ liệt kê), FROM/TO = dòng đầu/cuối (mặc định cả file), F = file nhóm.
# ssh -n và đọc file qua fd 3: ssh không đọc mất stdin của vòng lặp.
# Quy ước server gán cứng: /tmp/wpcli-home là HOME của WP-CLI, /tmp/wpcli-slot-1.lock là khoá chung để mọi job WP-CLI trên server chạy lần lượt.
# Server khác quy ước thì sửa 2 đường dẫn này ở dòng ssh bên dưới.
# Cuối lệnh in "đã chạy X/Y nhóm"; mã thoát 0 chỉ khi X = Y. LiteSpeed gửi hàng đợi purge ở request PHP kế tiếp: chạy bước làm nóng ngay sau.
set -u
SITE=${UCSS_SITE:?thiếu UCSS_SITE=<site.json>}
cfg() { python3 -I -c 'import json,sys
v = json.load(open(sys.argv[1])).get(sys.argv[2])
sys.exit("site.json thiếu khoá " + sys.argv[2]) if v is None else print(v)' "$SITE" "$1"; }
H=$(cfg ssh) && DR=$(cfg docroot) && PHP=$(cfg php_bin) && WP=$(cfg wp_bin) && WU=$(cfg wp_user) || { echo "DỪNG: site.json thiếu khoá"; exit 4; }
DRY=${DRY:-1}; F=${F:-purge-groups.txt}
N=$(grep -c . "$F"); FROM=${FROM:-1}; TO=${TO:-$N}
want=$((TO - FROM + 1)); ok=0; i=0
[ "$DRY" = 1 ] && st=would_purge || st=queued
ssh -n "$H" "install -d -o $WU -g $WU /tmp/wpcli-home/wp-ucss" && scp -q "$(dirname "$0")/purge_urls.php" "$H:/tmp/wpcli-home/wp-ucss/purge_urls.php" && ssh -n "$H" "chown $WU:$WU /tmp/wpcli-home/wp-ucss/purge_urls.php" || { echo "DỪNG: không chép được purge_urls.php"; exit 4; }
while read -r g <&3; do
  i=$((i + 1)); [ $i -lt $FROM ] && continue; [ $i -gt $TO ] && break
  [[ "$g" =~ ^[/a-z0-9,._-]+$ ]] || { echo "DỪNG: dòng $i có ký tự lạ"; break; }
  out=$(ssh -n "$H" "cd /tmp; flock /tmp/wpcli-slot-1.lock sudo -u $WU HOME=/tmp/wpcli-home URLS='$g' MAX=12 DRY=$DRY $PHP -d memory_limit=512M $WP --path=$DR eval-file /tmp/wpcli-home/wp-ucss/purge_urls.php 2>/dev/null </dev/null" | grep '^{')
  n=$(printf '%s' "$out" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read() or "{}"); print(d.get("status","none"), len(d.get("urls",[])))')
  echo "nhóm $i: $n"
  [ "${n%% *}" = "$st" ] && ok=$((ok + 1))
done 3< "$F"
echo "đã chạy ${ok}/${want} nhóm (dòng ${FROM}-${TO}, DRY=${DRY}, $(date '+%F %T %z'))"
[ $ok -eq $want ]
