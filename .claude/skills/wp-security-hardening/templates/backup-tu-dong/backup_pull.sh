#!/bin/bash
# Kéo backup tự động (/www/backup/auto trên server) về máy làm việc. Đây là bản ngoài server.
# Dùng: ALIAS=<ssh alias> [DEST=<thư mục>] backup_pull.sh. Chạy tay, hoặc đặt lịch (launchd trên Mac, cron trên Linux).
# Server ghi đè slot cũ, nên thư mục đích chỉ giữ 14 bản DB và 2 bản file như server.
# Biến môi trường: ALIAS (bắt buộc), DEST, SRC (mặc định /www/backup/auto), SSH_CMD (mặc định ssh),
#   VERIFY (đường dẫn verify_backup.sh, mặc định scripts/verify_backup.sh của skill nếu thấy).
# Có rsync trên server thì dùng rsync. Không có thì kéo bằng tar qua SSH và báo rõ.
# Sau khi kéo, script kiểm bản DB mới nhất bằng verify_backup.sh (nếu có). File rỗng hoặc cụt thì thoát 1.
# Mã thoát: 0 kéo xong và bản DB mới nhất đạt · 1 kéo lỗi, bản DB cũ hơn 48 giờ hoặc kiểm không đạt · 2 thiếu ALIAS.
set -euo pipefail
case "${1:-}" in -h|--help) sed -n '2,/^# Mã thoát/p' "$0" | sed 's/^# \{0,1\}//'; exit 0;; esac
ALIAS="${ALIAS:-}"; [ -n "$ALIAS" ] || { echo "Thiếu ALIAS. Xem --help." >&2; exit 2; }
DEST="${DEST:-$HOME/Backups/$ALIAS/auto}"
SRC="${SRC:-/www/backup/auto}"
SSH_CMD="${SSH_CMD:-ssh}"
VERIFY="${VERIFY:-$(dirname "$0")/../../scripts/verify_backup.sh}"
mkdir -p "$DEST"
chmod 700 "$DEST"
to_epoch() { date -d "$1" +%s 2>/dev/null || date -j -f '%Y-%m-%d %H:%M:%S' "$1" +%s 2>/dev/null || echo 0; }
echo "$(date '+%F %T') bắt đầu kéo về $DEST"
if $SSH_CMD "$ALIAS" 'command -v rsync >/dev/null 2>&1'; then
	rc=0
	rsync -a --partial --timeout=120 -e "$SSH_CMD" "$ALIAS:$SRC/" "$DEST/" || rc=$?
	if [ "$rc" -ne 0 ]; then echo "LỖI: rsync thoát mã $rc. Backup chưa được kéo." >&2; exit 1; fi
else
	echo "THAY THẾ: server không có rsync. Kéo bằng tar qua SSH."
	set +o pipefail
	$SSH_CMD "$ALIAS" "tar -C '$SRC' -cf - ." | tar -C "$DEST" -xf -
	prc=("${PIPESTATUS[@]}")
	set -o pipefail
	if [ "${prc[0]}" -ne 0 ] || [ "${prc[1]}" -ne 0 ]; then echo "LỖI: kéo bằng tar thất bại (mã ${prc[0]}, ${prc[1]})." >&2; exit 1; fi
fi
LAST=$(cat "$DEST/LAST_OK_db" 2>/dev/null || echo "")
NOW=$(date +%s); THEN=0
[ -n "$LAST" ] && THEN=$(to_epoch "$LAST")
AGE=$(( ( NOW - THEN ) / 3600 ))
if [ -z "$LAST" ] || [ "$AGE" -gt 48 ]; then
	echo "CẢNH BÁO: bản DB mới nhất trên server cũ hơn 48 giờ (LAST_OK_db: ${LAST:-không có}). Xem /var/log/tag-backup.log trên server." >&2
	exit 1
fi
if [ -f "$VERIFY" ]; then
	NEWEST=$(ls -t "$DEST"/db/* 2>/dev/null | head -1 || true)
	if [ -z "$NEWEST" ]; then echo "CẢNH BÁO: không có file DB nào trong $DEST/db." >&2; exit 1; fi
	bash "$VERIFY" "$NEWEST" || { echo "LỖI: bản DB mới nhất không đạt kiểm tra." >&2; exit 1; }
fi
echo "$(date '+%F %T') xong. DB mới nhất: $LAST"
