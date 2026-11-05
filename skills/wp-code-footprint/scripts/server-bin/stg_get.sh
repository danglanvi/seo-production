#!/bin/bash
# stg_get.sh <path> [m]  -> HTML staging (host đã che thành STG). Chạy trên server. Gọi https qua 127.0.0.1; STG_AUTH="user:pass" nếu staging có Basic Auth.
H=${STG_HOST:?STG_HOST}
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
[ "${2:-}" = m ] && UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
AUTH=(); [ -n "${STG_AUTH:-}" ] && AUTH=(-u "$STG_AUTH")
curl -sk "${AUTH[@]}" --resolve "$H:443:127.0.0.1" -A "$UA" -H "Accept-Language: vi" -w '\n<!--HTTP %{http_code}-->\n' "https://$H$1" | sed "s#$H#STG#g"
