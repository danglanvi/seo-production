#!/bin/bash
# deploy_ucss.sh (wp-ucss, chạy trên server): DRY=1|0 STAGE=<REMOTE_DIR>/stage-<bản> DOCROOT=... REMOTE_DIR=... PHP_BIN=... WP_USER=... bash <REMOTE_DIR>/deploy_ucss.sh
# regen.sh truyền các biến từ site.json. UCSS_DIR mặc định wp-content/ucss, MU_NAME mặc định ucss-swap.php.
# Chép file CSS gọn mới và map.php từ STAGE vào $DOCROOT/$UCSS_DIR/. Không xoá file gọn cũ (trang đã cache có thể còn trỏ tới).
# map.php thay bằng mv nguyên tử, bản cũ giữ ở $REMOTE_DIR/backup-map-<giờ>.php. Lần đầu (MU=1) cài mu-plugin $REMOTE_DIR/$MU_NAME.
# Dừng nếu: map.php lỗi cú pháp, map trỏ tới file không có trong STAGE, file CSS rỗng, mu-plugin đã có mà MU=1, hoặc mu-plugin (bản cài mới hay bản đã cài) trỏ thư mục khác UCSS_DIR.
set -u
DRY=${DRY:-1}; MU=${MU:-0}; S=${STAGE:?thiếu STAGE}; T=$(date +%H%M%S)
RD=${REMOTE_DIR:?thiếu REMOTE_DIR}; PHP=${PHP_BIN:?thiếu PHP_BIN}; WU=${WP_USER:?thiếu WP_USER}; MUN=${MU_NAME:-ucss-swap.php}; UD=${UCSS_DIR:-wp-content/ucss}
W=${DOCROOT:?thiếu DOCROOT}/wp-content; D=$DOCROOT/$UD
[[ "$UD" =~ ^wp-content/[A-Za-z0-9_-]+$ ]] || { echo "DỪNG: UCSS_DIR phải dạng wp-content/<tên>"; exit 3; }
[ -f "$S/map.php" ] || { echo "DỪNG: thiếu $S/map.php"; exit 3; }
$PHP -l "$S/map.php" >/dev/null || { echo "DỪNG: map.php lỗi cú pháp"; exit 3; }
need=$($PHP -r '$m = include $argv[1]; foreach ($m["files"] as $e) echo $e["f"], "\n";' "$S/map.php")
n=0; for f in $need; do [ -s "$S/$f" ] || { echo "DỪNG: map trỏ tới $f nhưng STAGE không có hoặc rỗng"; exit 3; }; n=$((n+1)); done
paths=$($PHP -r '$m = include $argv[1]; $c = 0; foreach ($m["files"] as $e) $c += count($e["p"]); echo $c;' "$S/map.php")
moi=0; for f in $need; do [ -f "$D/$f" ] || moi=$((moi+1)); done
echo "map: $n file gọn, $paths path; file mới cần chép: $moi; map hiện tại md5=$( [ -f $D/map.php ] && md5sum < $D/map.php | cut -c1-8 || echo 'chưa có') mới=$(md5sum < $S/map.php | cut -c1-8)"
if [ "$MU" = 1 ]; then
  [ -f $W/mu-plugins/$MUN ] && { echo "DỪNG: mu-plugin $MUN đã có"; exit 3; }
  $PHP -l $RD/$MUN >/dev/null || { echo "DỪNG: $MUN lỗi cú pháp"; exit 3; }
  grep -qF "\$sub = '${UD#wp-content/}';" $RD/$MUN || { echo "DỪNG: \$sub trong $MUN khác thư mục $UD"; exit 3; }
  echo "sẽ cài mu-plugin $MUN md5=$(md5sum < $RD/$MUN | cut -c1-8)"
elif [ -f $W/mu-plugins/$MUN ]; then
  # Đổi ucss_dir sau khi đã cài mu-plugin thì map ghi vào thư mục mu-plugin không đọc: dừng thay vì lệch im lặng.
  grep -qF "\$sub = '${UD#wp-content/}';" $W/mu-plugins/$MUN || { echo "DỪNG: \$sub trong mu-plugin đã cài khác thư mục $UD"; exit 3; }
fi
[ "$DRY" = 1 ] && { echo "DRY: chưa ghi"; exit 0; }
install -d -o $WU -g $WU -m 755 $D
for f in $need; do [ -f "$D/$f" ] || install -o $WU -g $WU -m 644 "$S/$f" "$D/$f"; done
[ -f $D/map.php ] && cp -p $D/map.php $RD/backup-map-$T.php && echo "backup map cũ: $RD/backup-map-$T.php"
install -o $WU -g $WU -m 644 "$S/map.php" "$D/.map.php.new" && mv -f "$D/.map.php.new" "$D/map.php" && echo "ghi map.php $(md5sum < $D/map.php | cut -c1-8) $(date +%H:%M:%S)"
if [ "$MU" = 1 ]; then
  install -o $WU -g $WU -m 644 $RD/$MUN $W/mu-plugins/$MUN && echo "cài mu-plugin $(date +%H:%M:%S)"
fi
