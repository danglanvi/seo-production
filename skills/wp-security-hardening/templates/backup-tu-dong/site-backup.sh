#!/bin/bash
# Backup tự động một site WordPress. Cài vào /root/bin/site-backup.sh, chạy bằng /etc/cron.d/site-backup (mẫu: backup.cron).
# Đặt SITE, NAME, VHOST theo hồ sơ server (00-client-context/wp-server.md).
#   site-backup.sh db    DB production, mỗi ngày. 14 slot theo thứ trong tuần và tuần chẵn/lẻ.
#   site-backup.sh files wp-content, wp-config.php, .htaccess, vhost. Chủ nhật. 2 slot theo tuần chẵn/lẻ.
# Slot mới ghi đè slot cũ cùng tên, nên script không xoá file nào.
# Bản ngoài server: máy làm việc kéo về bằng backup_pull.sh (cùng thư mục mẫu).
# Biến môi trường: SITE, NAME, VHOST, BACKUP_DIR (mặc định /www/backup/auto), PHP_BIN (mặc định lsphp83 của OpenLiteSpeed), CNF_PHP (mặc định /root/bin/backup-cnf.php).
# Nén bằng zstd. Server không có zstd thì dùng gzip (đuôi .gz) và ghi dòng THAY THẾ vào log.
# Mã thoát: 0 xong · 1 lỗi (không để lại file 0 byte hay file .part) · 2 sai tham số.
set -euo pipefail
umask 077
case "${1:-}" in -h|--help) sed -n '2,/^# Mã thoát/p' "$0" | sed 's/^# \{0,1\}//'; exit 0;; esac
D=${BACKUP_DIR:-/www/backup/auto}
PHP_BIN=${PHP_BIN:-/usr/local/lsws/lsphp83/bin/php}
CNF_PHP=${CNF_PHP:-/root/bin/backup-cnf.php}
SITE=${SITE:-/www/wwwroot/example.com}
NAME=${NAME:-$(basename "$SITE")}
VHOST=${VHOST:-www/server/panel/vhost/openlitespeed/detail/$NAME.conf}
W=$(( 10#$(date +%V) % 2 ))
log() { echo "$(date '+%F %T') $*"; }
mkdir -p "$D/db" "$D/files"
if command -v zstd >/dev/null 2>&1; then
	ZEXT=zst; zc() { zstd -q -T2 "-$1"; }; zd() { zstdcat "$1"; }; zt() { zstd -tq "$1"; }
elif command -v gzip >/dev/null 2>&1; then
	ZEXT=gz; zc() { gzip -c "-$(( $1 > 9 ? 9 : $1 ))"; }; zd() { gzip -dc "$1"; }; zt() { gzip -t "$1"; }
	log "THAY THẾ: không có zstd, dùng gzip"
else
	log "LỖI: không có zstd lẫn gzip"; exit 1
fi

case "${1:-}" in
db)
	CNF=$(mktemp)
	trap 'rm -f "$CNF" "${OUT:-/nonexistent}.part"' EXIT
	DB=$("$PHP_BIN" "$CNF_PHP" "$SITE/wp-config.php" "$CNF")
	OUT="$D/db/${NAME}-db-$(date +%a)-$W.sql.$ZEXT"
	# --no-tablespaces: user WordPress thường không có quyền PROCESS, thiếu cờ này mysqldump báo lỗi.
	mysqldump --defaults-extra-file="$CNF" --single-transaction --quick --no-tablespaces --routines --triggers \
		--default-character-set=utf8mb4 "$DB" | zc 10 > "$OUT.part"
	[ -s "$OUT.part" ] || { log "LỖI: file dump rỗng"; exit 1; }
	zd "$OUT.part" | tail -c 200 | grep -q "Dump completed" || { log "LỖI: dump thiếu dòng 'Dump completed'"; exit 1; }
	mv -f "$OUT.part" "$OUT"
	date '+%F %T' > "$D/LAST_OK_db"
	log "db ok $(basename "$OUT") $(du -h "$OUT" | cut -f1)"
	;;
files)
	OUT="$D/files/${NAME}-files-$W.tar.$ZEXT"
	trap 'rm -f "$OUT.part"' EXIT
	# tar trả mã 1 khi file đổi lúc đang đọc (Wordfence, cache ghi liên tục). Mã 1 vẫn là bản dùng được.
	{ tar -C / -cf - --warning=no-file-changed \
		--exclude="${SITE#/}/wp-content/cache" --exclude="${SITE#/}/wp-content/litespeed" \
		--exclude="${SITE#/}/wp-content/wflogs" --exclude="${SITE#/}/wp-content/upgrade*" \
		"${SITE#/}/wp-content" "${SITE#/}/wp-config.php" "${SITE#/}/.htaccess" \
		"$VHOST" || [ $? -eq 1 ]; } | zc 3 > "$OUT.part"
	[ -s "$OUT.part" ] || { log "LỖI: file backup rỗng"; exit 1; }
	zt "$OUT.part"
	mv -f "$OUT.part" "$OUT"
	date '+%F %T' > "$D/LAST_OK_files"
	log "files ok $(basename "$OUT") $(du -h "$OUT" | cut -f1)"
	;;
*)
	echo "Dùng: $0 db|files" >&2
	exit 2
	;;
esac
