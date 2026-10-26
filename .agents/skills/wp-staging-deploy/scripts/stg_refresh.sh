#!/bin/bash
# Làm mới staging từ production: backup staging, dump production, import vào DB staging, search-replace URL, mount uploads/elementor ghi được.
# Chạy trên server bằng root:  ssh <host> 'PROD=... STG=... DB_PROD=... DB_STG=... PROD_URL=... THEME=... bash -s' < stg_refresh.sh
# Biến:
#   PROD, STG        thư mục gốc WordPress của production và staging
#   DB_PROD, DB_STG  tên DB
#   PROD_URL         ví dụ https://example.com (không có / cuối)
#   THEME            thư mục theme trong wp-content/themes
#   STG_HOME_FILE    file chứa URL staging (mặc định /root/.stg_home). Script không in host staging.
#   MYSQL_CNF        file [client] có quyền dump; nếu trống, script đọc mật khẩu root của aaPanel
#   PHP              mặc định /usr/local/lsws/lsphp83/bin/php
# Không in mật khẩu DB. Theme và mu-plugins của staging KHÔNG bị ghi đè: chép tay sau bước này nếu cần.
set -euo pipefail
: "${PROD:?}" "${STG:?}" "${DB_PROD:?}" "${DB_STG:?}" "${PROD_URL:?}" "${THEME:?}"
STG_HOME_FILE=${STG_HOME_FILE:-/root/.stg_home}
PHP=${PHP:-/usr/local/lsws/lsphp83/bin/php}
TS=$(date +%Y%m%d-%H%M)
BK=/root/backup-stg-refresh-$TS
WP="$PHP -d memory_limit=2048M /usr/local/bin/wp --allow-root --path=$STG --skip-plugins --skip-themes"
mkdir -p "$BK"
if [ -z "${MYSQL_CNF:-}" ]; then
  PW=$(sqlite3 /www/server/panel/data/default.db "select mysql_root from config where id=1")
  MYSQL_CNF=$(mktemp); chmod 600 "$MYSQL_CNF"; trap 'rm -f "$MYSQL_CNF"' EXIT
  printf "[client]\nuser=root\npassword=%s\n" "$PW" > "$MYSQL_CNF"; unset PW
fi
DUMP="mysqldump --defaults-extra-file=$MYSQL_CNF --single-transaction --quick --routines --triggers --hex-blob --default-character-set=utf8mb4"

echo "1 backup staging $(date +%T)"
tar czf "$BK/stg-theme-mu.tgz" -C "$STG/wp-content" "themes/$THEME" mu-plugins
nice -n 15 $DUMP "$DB_STG" | gzip -1 > "$BK/stg.sql.gz"
echo "2 dump production $(date +%T)"
nice -n 15 $DUMP "$DB_PROD" | gzip -1 > "$BK/prod.sql.gz"
echo "  base cho merge3.py: $BK/base"
mkdir -p "$BK/base/themes" && cp -a "$PROD/wp-content/themes/$THEME" "$BK/base/themes/" && cp -a "$PROD/wp-content/mu-plugins" "$BK/base/"
echo "3 import vào staging $(date +%T)"
zcat "$BK/prod.sql.gz" | nice -n 15 mysql --defaults-extra-file="$MYSQL_CNF" "$DB_STG"
mysql --defaults-extra-file="$MYSQL_CNF" "$DB_STG" -e "UPDATE wp_options SET option_value='0' WHERE option_name='blog_public';"

echo "4 search-replace $(date +%T)"
STG_URL=$(cat "$STG_HOME_FILE")
STG_HOST=$(sed -E 's#^https?://##; s#/.*##' "$STG_HOME_FILE")
PH=$(sed -E 's#^https?://##' <<<"$PROD_URL")
cd /tmp
i=0
for pair in "https://$PH|$STG_URL" "http://$PH|$STG_URL" "https:\\/\\/$PH|${STG_URL//\//\\/}"; do
  from="${pair%%|*}"; to="${pair#*|}"
  n=$(nice -n 15 $WP search-replace "$from" "$to" --all-tables-with-prefix --skip-columns=guid --precise --format=count 2>/dev/null || echo lỗi)
  echo "  cặp $((++i)): $n chỗ"
done
chk=$(mysql --defaults-extra-file="$MYSQL_CNF" -N "$DB_STG" -e "select option_value from wp_options where option_name='siteurl'")
[ "$chk" = "$STG_URL" ] && echo "  siteurl staging: OK" || echo "  siteurl staging: LỆCH"

echo "5 uploads/elementor ghi được $(date +%T)"
if mountpoint -q "$STG/wp-content/uploads"; then
  RW=/www/stg-rw/$(basename "$STG")/elementor
  mkdir -p "$RW"
  rsync -a --delete "$PROD/wp-content/uploads/elementor/" "$RW/"
  chown -R www:www "$(dirname "$RW")"
  # Mount con dưới bind mount shared lan sang production. Luôn make-private trước.
  mount --make-private "$STG/wp-content/uploads"
  if ! mountpoint -q "$STG/wp-content/uploads/elementor"; then mount --bind "$RW" "$STG/wp-content/uploads/elementor"; mount --make-private "$STG/wp-content/uploads/elementor"; fi
  if findmnt -l -o TARGET | grep -q "^$PROD/"; then echo "LỖI: có mount dưới production"; exit 1; fi
  sudo -u www touch "$STG/wp-content/uploads/elementor/.rwtest" && rm -f "$STG/wp-content/uploads/elementor/.rwtest" && echo "  ghi được: OK"
else
  echo "  uploads staging không phải bind mount: bỏ qua"
fi
echo "backup: $BK"
echo "xong $(date +%T)"
