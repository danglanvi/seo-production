#!/bin/bash
# Bấm đúp trên máy Mac chạy liên tục để cài lịch kéo backup về máy mỗi ngày. Đặt file này cạnh backup_pull.sh.
# Sửa 3 dòng ALIAS, LABEL, HOUR dưới đây trước khi giao cho người vận hành.
# Gỡ: launchctl bootout gui/$(id -u)/<LABEL>, rồi chuyển file plist khỏi ~/Library/LaunchAgents/.
set -euo pipefail
ALIAS="${ALIAS:-site-vps}"
LABEL="${LABEL:-vn.gtv.backup-pull.$ALIAS}"
HOUR="${HOUR:-8}"
DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DEST="$HOME/Backups/$ALIAS/auto"
LOG="$HOME/Backups/$ALIAS/backup-pull.log"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Backups/$ALIAS"

if ! ssh -o BatchMode=yes -o ConnectTimeout=10 "$ALIAS" true 2>/dev/null; then
	echo "Máy này chưa SSH được vào $ALIAS (thiếu alias hoặc key trong ~/.ssh). Dừng, chưa cài gì."
	read -r -p "Bấm Enter để đóng."
	exit 1
fi

# Plist là XML: dấu & trong đường dẫn phải viết thành &amp;, nếu không launchctl từ chối nạp.
x() { local s="${1//&/&amp;}"; s="${s//</&lt;}"; printf '%s' "${s//>/&gt;}"; }
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key><string>$LABEL</string>
	<key>ProgramArguments</key>
	<array><string>/bin/bash</string><string>$(x "$DIR/backup_pull.sh")</string></array>
	<key>EnvironmentVariables</key>
	<dict><key>ALIAS</key><string>$ALIAS</string><key>DEST</key><string>$(x "$DEST")</string></dict>
	<key>StartCalendarInterval</key>
	<dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>30</integer></dict>
	<key>StandardOutPath</key><string>$(x "$LOG")</string>
	<key>StandardErrorPath</key><string>$(x "$LOG")</string>
</dict>
</plist>
EOF
plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Đã cài lịch $HOUR:30 mỗi ngày. Chạy thử lần đầu..."
ALIAS="$ALIAS" DEST="$DEST" /bin/bash "$DIR/backup_pull.sh" | tee -a "$LOG"
read -r -p "Xong. Sáng mai xem $LOG để chắc lịch chạy được. Bấm Enter để đóng."
