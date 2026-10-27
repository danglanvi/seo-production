#!/usr/bin/env bash
# rtreport_mau.sh (wp-host-optimize): lấy mẫu /tmp/lshttpd/.rtreport* của OpenLiteSpeed mỗi N giây, lưu trên máy agent. Chỉ đọc server.
# Mỗi pool PHP có dòng "EXTAPP [LSAPI] [<pool>] …: CMAXCONN, INUSE_CONN, WAITQUE_DEPTH"; dòng BLOCKED_IP liệt kê IP OLS đang cấm.
# Dùng: nohup bash rtreport_mau.sh --ssh 'ssh <host>' --out <file.log> [--giay 10] >/dev/null 2>&1 &
#   Dừng: kill $(cat <file.log>.pid). Đọc: python3 -I rtreport_phan_tich.py <file.log>.
# Phiên SSH rớt thì script nối lại sau 5 giây và ghi dòng "# mat-ket-noi <epoch>".
# Lỗi đã gặp 24/10/2026: bộ lấy mẫu một phiên SSH chết lúc 13:45, phép đo 48 giờ không còn số hàng chờ pool.
set -u
SSH= OUT= GIAY=10
while [ $# -gt 0 ]; do
  case "$1" in
    --ssh) SSH="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --giay) GIAY="$2"; shift 2 ;;
    *) echo "tham số lạ: $1" >&2; exit 2 ;;
  esac
done
[ -n "$SSH" ] && [ -n "$OUT" ] || { sed -n '4,5p' "$0" >&2; exit 2; }
echo $$ > "$OUT.pid"
REMOTE="while sleep $GIAY; do date +%s || exit; grep -h -E 'EXTAPP \[LSAPI\]|BLOCKED_IP' /tmp/lshttpd/.rtreport* 2>/dev/null; done"
while :; do
  $SSH -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 "$REMOTE" >> "$OUT" 2>> "$OUT.err"
  echo "# mat-ket-noi $(date +%s)" >> "$OUT"
  sleep 5
done
