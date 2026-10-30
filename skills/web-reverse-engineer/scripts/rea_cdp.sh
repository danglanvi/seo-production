#!/bin/sh
# Mở và đóng một Chrome headless có cổng CDP cho lệnh rea.
# open <url>: in EP=... và TID=... để dùng với eval. close: tắt Chrome đó.
set -eu
PORT="${REA_CDP_PORT:-9333}"
CHROME="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PROFILE="${TMPDIR:-/tmp}/rea-cdp-$PORT"
EP="http://127.0.0.1:$PORT"

case "${1:-}" in
  open)
    [ $# -ge 2 ] || { echo "dùng: rea_cdp.sh open <url>" >&2; exit 2; }
    "$CHROME" --headless=new --remote-debugging-port="$PORT" --user-data-dir="$PROFILE" \
      --no-first-run --window-size=1366,900 "$2" >/dev/null 2>&1 &
    python3 - "$EP" "$2" <<'PY'
import json, sys, time, urllib.request
ep, url = sys.argv[1], sys.argv[2]
host = url.split("/")[2] if "//" in url else url
for _ in range(150):
    try:
        pages = json.load(urllib.request.urlopen(ep + "/json/list", timeout=2))
        page = next((p for p in pages if p.get("type") == "page" and host in p.get("url", "")), None)
        if page:
            time.sleep(2)
            print(f"EP={ep}; TID={page['id']}")
            sys.exit(0)
    except OSError:
        pass
    time.sleep(0.2)
sys.exit("Chrome không mở được trang qua cổng CDP")
PY
    ;;
  close)
    pkill -f "remote-debugging-port=$PORT" || true
    ;;
  *)
    echo "dùng: rea_cdp.sh open <url> | close" >&2
    exit 2
    ;;
esac
