#!/bin/bash
# apply_vhost_ucss.sh (wp-ucss, chạy trên server): DRY=1|0 VHOST_CONF=<file vhost OpenLiteSpeed> REMOTE_DIR=<thư mục script> [UCSS_DIR=wp-content/ucss] bash <REMOTE_DIR>/apply_vhost_ucss.sh
# Chèn $REMOTE_DIR/vhost-ucss-block.txt (thay @UCSS_DIR@ bằng UCSS_DIR) vào vhost, ngay trước dòng "rewrite  {".
# Không restart. Dừng nếu khối đã có, mốc "rewrite  {" không đúng 1 dòng, hoặc context /wp-content/litespeed/ không đúng 1.
set -u
F=${VHOST_CONF:?thiếu VHOST_CONF}; S=${REMOTE_DIR:?thiếu REMOTE_DIR}; UD=${UCSS_DIR:-wp-content/ucss}; T=$(date +%H%M%S)
grep -q "^context /$UD/ {" $F && { echo "DỪNG: context đã có"; exit 3; }
[ "$(grep -c '^rewrite  {$' $F)" = 1 ] || { echo "DỪNG: mốc rewrite = $(grep -c '^rewrite  {$' $F)"; exit 3; }
[ "$(grep -c '^context /wp-content/litespeed/ {$' $F)" = 1 ] || { echo "DỪNG: context litespeed = $(grep -c '^context /wp-content/litespeed/ {$' $F)"; exit 3; }
BLK=$(mktemp); sed "s#@UCSS_DIR@#$UD#g" "$S/vhost-ucss-block.txt" > $BLK
NEW=$(mktemp); awk -v blk="$BLK" '/^rewrite  \{$/{while((getline l < blk)>0) print l} {print}' $F > $NEW
echo "vhost md5=$(md5sum < $F | cut -c1-8) mới=$(md5sum < $NEW | cut -c1-8)"; diff $F $NEW
[ "${DRY:-1}" = 1 ] && { echo "DRY: chưa ghi"; rm -f $NEW $BLK; exit 0; }
cp -p $F $S/backup-vhost-$T.conf && echo "backup $S/backup-vhost-$T.conf"
cat $NEW > $F && rm -f $NEW $BLK && echo "ghi vhost $(md5sum < $F | cut -c1-8) $(date +%H:%M:%S)"
