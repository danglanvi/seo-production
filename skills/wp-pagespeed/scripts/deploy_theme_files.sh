#!/bin/bash
# Chép vài file của theme lên server, không đụng file khác: backup bản trên server, lint PHP, chép, sửa owner và quyền, purge.
# Dùng: ALIAS=<ssh alias> ROOT=<web root> THEME_DIR=<thư mục theme trên máy> [THEME=<tên theme trên server>] \
#       [PHP=<php trên server>] [OWNER=www:www] [PURGE='<lệnh purge chạy trên server>'] deploy_theme_files.sh <file trong theme>...
# Ví dụ PURGE (LiteSpeed Cache): 'cd /tmp && sudo -u www <php> /usr/local/bin/wp --path=<root> litespeed-purge all'
# Rollback: chạy lại script với THEME_DIR=<thư mục backup script in ra> và cùng danh sách file.
# Trả về trạng thái gốc thì dùng thư mục backup của lần deploy ĐẦU. Lần deploy sau chỉ backup bản trung gian (v1).
# File chưa có trên server không nằm trong backup: trả lại bằng cách chuyển file đó vào quarantine.
set -euo pipefail
ALIAS="${ALIAS:?Thiếu ALIAS}"
ROOT="${ROOT:?Thiếu ROOT}"
THEME_DIR="${THEME_DIR:?Thiếu THEME_DIR}"
THEME="${THEME:-$(basename "$THEME_DIR")}"
PHP="${PHP:-php}"
OWNER="${OWNER:-www:www}"
[ $# -gt 0 ] || { echo "Thiếu danh sách file"; exit 1; }
for f in "$@"; do [ -f "$THEME_DIR/$f" ] || { echo "Không có $THEME_DIR/$f"; exit 1; }; done
BK="${BK_ROOT:-$HOME/Backups/$ALIAS}/$(date +%F)/theme-files-$(basename "$ROOT")-$(date +%H%M%S)"
mkdir -p "$BK"
R="$ROOT/wp-content/themes/$THEME"
ssh "$ALIAS" "cd '$R' && tar -cf - --ignore-failed-read $* 2>/dev/null" | tar -xf - -C "$BK" 2>/dev/null || true
echo "backup: $BK ($(find "$BK" -type f | wc -l | tr -d ' ') file)"
COPYFILE_DISABLE=1 tar --no-xattrs -C "$THEME_DIR" -cf - "$@" | ssh "$ALIAS" "set -e
N=\$(mktemp -d)
tar -xf - --no-same-owner -C \$N
ERR=\$(find \$N -name '*.php' -print0 | xargs -0 -r -n1 $PHP -l 2>&1 | grep -v '^No syntax errors' || true)
if [ -n \"\$ERR\" ]; then echo 'LINT FAIL'; echo \"\$ERR\"; rm -r \$N; exit 1; fi
cp -a \$N/. '$R'/
cd \$N
find . -mindepth 1 -exec chown $OWNER '$R'/{} \;
find . -type f -exec chmod 644 '$R'/{} \;
cd /
rm -r \$N
echo 'đã chép $# file'"
if [ -n "${PURGE:-}" ]; then ssh "$ALIAS" "$PURGE" 2>&1 | tail -1; fi
