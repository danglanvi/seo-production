#!/bin/bash
# prod_get.sh <path> [m|d] [nc|cache] [webp]  -> HTML production. nc = bỏ cache (?nc=<random>). webp = thêm Accept image/webp (bản người dùng).
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
[ "${2:-d}" = m ] && UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
U="${HOST:?HOST}$1"; [ "${3:-cache}" = nc ] && U="$U?nc=$RANDOM$RANDOM"
ACC="text/html"; [ "${4:-}" = webp ] && ACC="text/html,application/xhtml+xml,image/webp,*/*;q=0.8"
curl -s -L -A "$UA" -H "Accept: $ACC" -H "Accept-Language: vi" -w '\n<!--HTTP %{http_code} %{size_download}B-->\n' "$U"
