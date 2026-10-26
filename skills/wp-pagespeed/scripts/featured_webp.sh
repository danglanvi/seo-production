#!/bin/bash
# Đổi ảnh đại diện PNG/JPG nặng của một bài sang attachment WebP mới; ảnh OG (Rank Math) giữ attachment cũ để thẻ chia sẻ
# Facebook, Zalo không đổi. Ảnh gốc, các cỡ con cũ và URL cũ giữ nguyên.
# Dùng: ALIAS=<ssh alias> WP='<lệnh wp đầy đủ, có --path>' [PURGE='<lệnh purge trên server>'] [BK_ROOT=<thư mục backup>] \
#       featured_webp.sh <post id> <file .webp trên máy> "<alt>"
# Ví dụ WP: 'cd /tmp && sudo -u www HOME=/tmp/wpcli-home /usr/local/lsws/lsphp83/bin/php /usr/local/bin/wp --path=/www/wwwroot/example.com'
# Trước khi chạy: bài phải trả 200 (bài đã 301 thì bỏ qua). Tạo WebP bằng: cwebp -q 86 -m 6 -sharp_yuv <ảnh> -o <tên-có-ngữ-cảnh>.webp
# 1. Ghi _thumbnail_id, rank_math_facebook_image(_id) cũ vào thư mục backup. 2. wp media import (WordPress tự sinh cỡ con WebP).
# 3. rank_math_facebook_image(_id) trỏ về attachment cũ nếu đang trống. 4. Đặt attachment mới làm ảnh đại diện, purge.
# Rollback: lệnh in ở cuối và lưu trong rollback.txt. Attachment mới để lại trong thư viện.
set -euo pipefail
ALIAS="${ALIAS:?Thiếu ALIAS}"; WP="${WP:?Thiếu WP}"
ID="${1:?Thiếu post id}"; F="${2:?Thiếu file webp}"; ALT="${3:?Thiếu alt}"
[ -f "$F" ] && [ "${F##*.}" = webp ] || { echo "Không có file .webp: $F"; exit 1; }
[[ "$ALT" != *"'"* && "$ALT" != *'"'* ]] || { echo "Alt không được chứa dấu nháy"; exit 1; }
BK="${BK_ROOT:-$HOME/Backups/$ALIAS}/$(date +%F)/featured-webp-$ID-$(date +%H%M%S)"
mkdir -p "$BK"
ssh "$ALIAS" "$WP eval 'foreach([\"_thumbnail_id\",\"rank_math_facebook_image\",\"rank_math_facebook_image_id\"] as \$k) echo \$k, \"=\", get_post_meta($ID, \$k, true), \"\n\";' 2>/dev/null" > "$BK/meta.txt"
OLD=$(sed -n 's/^_thumbnail_id=//p' "$BK/meta.txt"); OGID=$(sed -n 's/^rank_math_facebook_image_id=//p' "$BK/meta.txt")
[ -n "$OLD" ] || { echo "Bài $ID chưa có ảnh đại diện"; exit 1; }
echo "backup: $BK (ảnh cũ $OLD, OG id '$OGID')"
T="/tmp/featured-webp-$ID-$$"
ssh "$ALIAS" "mkdir -p $T && chmod 755 $T"
scp -q "$F" "$ALIAS:$T/$(basename "$F")"
NEW=$(ssh "$ALIAS" "chmod 644 $T/* && $WP media import $T/$(basename "$F") --post_id=$ID --alt='$ALT' --title='$ALT' --porcelain 2>/dev/null")
[[ "$NEW" =~ ^[0-9]+$ ]] || { echo "Import lỗi: $NEW (file tạm còn ở $ALIAS:$T)"; exit 1; }
if [ -z "$OGID" ]; then
	ssh "$ALIAS" "$WP eval '\$u = wp_get_attachment_url($OLD); update_post_meta($ID, \"rank_math_facebook_image\", \$u); update_post_meta($ID, \"rank_math_facebook_image_id\", $OLD); echo \"og giữ: \", \$u, \"\n\";' 2>/dev/null"
fi
ssh "$ALIAS" "$WP post meta update $ID _thumbnail_id $NEW >/dev/null 2>&1 && echo 'ảnh đại diện mới: $NEW'"
[ -n "${PURGE:-}" ] && ssh "$ALIAS" "$PURGE" >/dev/null 2>&1 && echo "purge xong"
echo "File tạm trên server: $T (chuyển vào quarantine khi xong, không xoá)"
RB="$WP post meta update $ID _thumbnail_id $OLD"
[ -z "$OGID" ] && RB="$RB && $WP post meta delete $ID rank_math_facebook_image && $WP post meta delete $ID rank_math_facebook_image_id"
echo "Rollback: ssh $ALIAS \"$RB\"" | tee "$BK/rollback.txt"
