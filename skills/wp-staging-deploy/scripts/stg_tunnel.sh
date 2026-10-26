#!/bin/bash
# Mở, kiểm và đóng tunnel SSH tới staging. Tunnel rớt thì `up` nối lại.
#
# Dùng:  stg_tunnel.sh up|down|status [--lane X] [--port N] [--alias A] [--retries N]
#   --lane     tên lane, chỉ chữ, số, gạch (mặc định: default). Mỗi lane một pid file riêng
#   --port     cổng local (mặc định: $STG_PORT hoặc 18094). Cổng riêng cho từng lane do phiên điều phối cấp
#   --alias    alias ssh (mặc định: $STG_ALIAS)
#   --retries  số lần nối lại khi up (mặc định 3)
# Biến: STG_RUN_DIR (thư mục pid file, mặc định ~/.cache/stg-tunnel), STG_WAIT_TRIES (số lần chờ 0,5 giây, mặc định 20)
# Kiểm sống: GET http://127.0.0.1:PORT/ với header Host của staging, chấp nhận 200, 301, 302, 401.
# Không ghi dữ liệu lên server. Không in host staging.
# Mã thoát: 0 tunnel sống · 1 tunnel chết hoặc không nối được · 2 lỗi dùng.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=stg_env.sh
. "$HERE/stg_env.sh"

usage() { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; }

CMD="${1:-}"; [ $# -gt 0 ] && shift
LANE=default; PORT="${STG_PORT:-18094}"; ALIAS="${STG_ALIAS:-}"; RETRIES=3
while [ $# -gt 0 ]; do
  case "$1" in
    --lane) LANE="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --alias) ALIAS="${2:-}"; shift 2 ;;
    --retries) RETRIES="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "LỖI: tuỳ chọn lạ: $1" >&2; exit 2 ;;
  esac
done
case "$CMD" in up|down|status) ;; -h|--help) usage; exit 0 ;; *) usage >&2; exit 2 ;; esac
case "$LANE" in ''|*[!A-Za-z0-9_-]*) echo "LỖI: --lane chỉ nhận chữ, số, gạch." >&2; exit 2 ;; esac
case "$PORT" in ''|*[!0-9]*) echo "LỖI: --port phải là số." >&2; exit 2 ;; esac
case "$RETRIES" in ''|*[!0-9]*) echo "LỖI: --retries phải là số." >&2; exit 2 ;; esac
STG_ALIAS="$ALIAS"

RUN_DIR="${STG_RUN_DIR:-$HOME/.cache/stg-tunnel}"
PIDF="$RUN_DIR/$LANE.pid"
WAIT_TRIES="${STG_WAIT_TRIES:-20}"

pid_of() { [ -f "$PIDF" ] && tr -dc '0-9' < "$PIDF" || true; }
is_our_tunnel() { # pid sống và đúng là ssh -L $PORT
  local pid="$1" cmd
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || return 1
  cmd="$(ps -p "$pid" -o command= 2>/dev/null)"
  case "$cmd" in *ssh*"-L $PORT:"*) return 0 ;; *) return 1 ;; esac
}
health() { # in mã HTTP (000 nếu lỗi)
  local code
  code="$(printf 'url = "http://127.0.0.1:%s/"\nheader = "Host: %s"\nuser-agent = "%s"\n' "$PORT" "$STG_HOST" "$STG_UA" \
    | curl -sS -K - -o /dev/null -w '%{http_code}' --max-time 10 2>/dev/null)" || true
  printf '%s' "${code:-000}"
}
healthy() { case "$(health)" in 200|301|302|401) return 0 ;; *) return 1 ;; esac; }
port_busy() { lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; }
stop_pid() {
  local pid="$1" i=0
  kill "$pid" 2>/dev/null || true
  while kill -0 "$pid" 2>/dev/null && [ "$i" -lt 20 ]; do sleep 0.25; i=$((i+1)); done
  kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
}

if [ "$CMD" != down ]; then stg_load || exit 1; fi
mkdir -p "$RUN_DIR" && chmod 700 "$RUN_DIR"

case "$CMD" in
  status)
    pid="$(pid_of)"; alive=no; is_our_tunnel "$pid" && alive=yes
    h=000; [ "$alive" = yes ] && h="$(health)"
    echo "lane=$LANE port=$PORT pid=${pid:-none} alive=$alive health=$h"
    [ "$alive" = yes ] && case "$h" in 200|301|302|401) exit 0 ;; esac
    exit 1 ;;
  down)
    pid="$(pid_of)"
    if is_our_tunnel "$pid"; then stop_pid "$pid"; echo "lane=$LANE: đã đóng tunnel pid $pid"
    elif [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then echo "lane=$LANE: pid $pid không phải tunnel ssh của lane này, không đụng" >&2; rm -f "$PIDF"; exit 1
    else echo "lane=$LANE: không có tunnel chạy"; fi
    rm -f "$PIDF"; exit 0 ;;
  up)
    n=0
    while [ "$n" -lt "$RETRIES" ]; do
      n=$((n+1))
      pid="$(pid_of)"
      if is_our_tunnel "$pid"; then
        if healthy; then echo "lane=$LANE port=$PORT: tunnel đang sống (pid $pid)"; exit 0; fi
        echo "lane=$LANE: tunnel pid $pid không trả lời, nối lại ($n/$RETRIES)" >&2
        stop_pid "$pid"
      fi
      rm -f "$PIDF"
      if port_busy; then echo "LỖI: cổng $PORT đang do tiến trình khác dùng. Đổi --port. Không tự kill." >&2; exit 1; fi
      [ -n "$ALIAS" ] || { echo "LỖI: thiếu --alias hoặc STG_ALIAS." >&2; exit 2; }
      nohup ssh -N -o BatchMode=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
        -o ConnectTimeout=15 -L "$PORT:127.0.0.1:80" "$ALIAS" >/dev/null 2>&1 &
      echo "$!" > "$PIDF"
      i=0
      while [ "$i" -lt "$WAIT_TRIES" ]; do
        sleep 0.5; i=$((i+1))
        is_our_tunnel "$(pid_of)" || break
        if healthy; then echo "lane=$LANE port=$PORT: tunnel lên (pid $(pid_of))"; exit 0; fi
      done
      echo "lane=$LANE: lần $n/$RETRIES chưa lên" >&2
      is_our_tunnel "$(pid_of)" && stop_pid "$(pid_of)"
    done
    rm -f "$PIDF"
    echo "LỖI: không nối được tunnel sau $RETRIES lần. Kiểm alias, quyền ssh và cổng 80 của staging." >&2
    exit 1 ;;
esac
