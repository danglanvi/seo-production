#!/usr/bin/env bash
# gsc.sh — Google Search Console API qua OAuth của gws CLI (tài khoản Google đang login trên máy)
# Property nào đã share cho tài khoản đó là API thấy ngay — không cần cài thêm per property.
#
# Cách dùng:
#   tools/gsc/gsc.sh sites                                        # liệt kê property truy cập được
#   tools/gsc/gsc.sh query    <property> [days] [dimensions]      # Search Analytics (mặc định 90 ngày, dim=page)
#   tools/gsc/gsc.sh inspect  <property> <url>                    # URL Inspection — index status thật 1 URL
#   tools/gsc/gsc.sh sitemaps <property>                          # sitemap đã submit + status
#   tools/gsc/gsc.sh coverage <property> <file-urls.txt> [out]    # inspect hàng loạt → CSV (quota 2.000/ngày/property)
#
# <property>: URL-prefix ("https://example.vn/") hoặc domain property ("sc-domain:example.vn")
# Yêu cầu: gws đã login scope webmasters.readonly; Search Console API enabled trên project quota.
# Quota URL Inspection: 2.000 calls/ngày/property, 600/phút — coverage tự giãn nhịp ~2 call/giây.

set -euo pipefail

CACHE_DIR="${HOME}/.cache/gsc-cli"
mkdir -p "$CACHE_DIR"
TOKEN_FILE="$CACHE_DIR/access_token.json"

die() { echo "LỖI: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null || die "thiếu lệnh: $1"; }
need gws; need python3; need curl

# --- Token: lấy refresh_token từ gws, tự mint access_token (cache ~50 phút) ---
get_token() {
  if [[ -f "$TOKEN_FILE" ]]; then
    local now exp
    now=$(date +%s)
    exp=$(python3 -c "import json;print(json.load(open('$TOKEN_FILE')).get('exp',0))" 2>/dev/null || echo 0)
    if (( now < exp )); then
      python3 -c "import json;print(json.load(open('$TOKEN_FILE'))['access_token'])"
      return
    fi
  fi
  # heredoc chiếm stdin của python nên KHÔNG pipe được: ghi export ra file tạm 0600 rồi đọc lại (sửa 02/09/2026)
  local export_file="$CACHE_DIR/.export.json"
  ( umask 077; gws auth export --unmasked 2>/dev/null > "$export_file" )
  python3 - "$TOKEN_FILE" "$export_file" <<'PY'
import json, sys, urllib.request, urllib.parse, time, os
_raw = open(sys.argv[2]).read(); os.unlink(sys.argv[2])
creds = json.loads(_raw[_raw.find("{"):])  # bỏ dòng "Using keyring backend" nếu gws in trước JSON
data = urllib.parse.urlencode({
    "client_id": creds["client_id"],
    "client_secret": creds["client_secret"],
    "refresh_token": creds["refresh_token"],
    "grant_type": "refresh_token",
}).encode()
req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
try:
    resp = json.load(urllib.request.urlopen(req))
except urllib.error.HTTPError as e:
    sys.stderr.write("Refresh token lỗi: %s\n" % e.read().decode())
    sys.exit(2)
tok = {"access_token": resp["access_token"], "exp": int(time.time()) + resp.get("expires_in", 3600) - 300}
out = sys.argv[1]
with open(out, "w") as f:
    json.dump(tok, f)
import os; os.chmod(out, 0o600)
print(resp["access_token"])
PY
}

api() { # api <method> <url> [json-body]
  local method="$1" url="$2" body="${3:-}" token
  token=$(get_token) || die "không lấy được access token (đã 'gws auth login' với scope webmasters.readonly chưa?)"
  if [[ -n "$body" ]]; then
    curl -sS -X "$method" "$url" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d "$body"
  else
    curl -sS -X "$method" "$url" -H "Authorization: Bearer $token"
  fi
}

enc() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }

cmd="${1:-}"; shift || true
case "$cmd" in
  sites)
    api GET "https://www.googleapis.com/webmasters/v3/sites" | python3 -m json.tool
    ;;
  query)
    prop="${1:?property}"; days="${2:-90}"; dims="${3:-page}"
    start=$(date -v-"${days}"d +%Y-%m-%d 2>/dev/null || date -d "-${days} days" +%Y-%m-%d)
    end=$(date +%Y-%m-%d)
    dims_json=$(python3 -c "import json,sys;print(json.dumps(sys.argv[1].split(',')))" "$dims")
    api POST "https://www.googleapis.com/webmasters/v3/sites/$(enc "$prop")/searchAnalytics/query" \
      "{\"startDate\":\"$start\",\"endDate\":\"$end\",\"dimensions\":$dims_json,\"rowLimit\":25000}" | python3 -m json.tool
    ;;
  inspect)
    prop="${1:?property}"; url="${2:?url}"
    api POST "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect" \
      "{\"siteUrl\":\"$prop\",\"inspectionUrl\":\"$url\"}" | python3 -m json.tool
    ;;
  sitemaps)
    prop="${1:?property}"
    api GET "https://www.googleapis.com/webmasters/v3/sites/$(enc "$prop")/sitemaps" | python3 -m json.tool
    ;;
  coverage)
    prop="${1:?property}"; file="${2:?file-urls.txt}"; out="${3:-coverage-$(date +%Y%m%d-%H%M).csv}"
    [[ -f "$file" ]] || die "không thấy file: $file"
    total=$(grep -c . "$file" || true)
    (( total <= 2000 )) || echo "⚠️  $total URL > quota 2.000/ngày — sẽ dừng khi hết quota" >&2
    echo "url,verdict,coverage_state,robots_state,indexing_state,last_crawl,google_canonical" > "$out"
    n=0
    while IFS= read -r u; do
      [[ -z "$u" ]] && continue
      n=$((n+1)); printf '\r%d/%d %s' "$n" "$total" "$u" >&2
      api POST "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect" \
        "{\"siteUrl\":\"$prop\",\"inspectionUrl\":\"$u\"}" | python3 - "$u" >> "$out" <<'PY'
import json, sys, csv
u = sys.argv[1]
try:
    d = json.load(sys.stdin).get("inspectionResult", {}).get("indexStatusResult", {})
except Exception:
    d = {}
w = csv.writer(sys.stdout)
w.writerow([u, d.get("verdict",""), d.get("coverageState",""), d.get("robotsTxtState",""),
            d.get("indexingState",""), d.get("lastCrawlTime",""), d.get("googleCanonical","")])
PY
      sleep 0.5   # ~2 call/giây — an toàn dưới 600/phút
    done < "$file"
    echo >&2
    echo "Xong → $out"
    ;;
  *)
    grep '^#' "$0" | sed 's/^# \{0,1\}//' | head -14
    exit 1
    ;;
esac
