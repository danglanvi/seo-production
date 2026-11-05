#!/bin/bash
# health.sh <HH:MM[:SS]> [HH:MM[:SS]]; exit 0 đạt, 1 có lỗi site, 2 chưa kiểm đủ.
# ACCESS_LOG, ERROR_LOG, SITE_DOMAIN; HEALTH_DATE=YYYY-MM-DD khi kiểm cửa sổ cũ.
# Chỉ xuất số tổng hợp. Error log dùng chung vhost; không coi file thiếu/parser lỗi là 0.
set -euo pipefail
python3 - "$@" <<'PY'
import datetime as dt
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

try:
    if len(sys.argv) not in (2, 3):
        raise ValueError('cần giờ bắt đầu và giờ kết thúc tuỳ chọn')
    now = dt.datetime.now().astimezone()
    day = dt.date.fromisoformat(os.environ.get('HEALTH_DATE', str(now.date())))
    start = dt.datetime.combine(day, dt.time.fromisoformat(sys.argv[1]), now.tzinfo)
    end = dt.datetime.combine(day, dt.time.fromisoformat(sys.argv[2]), now.tzinfo) if len(sys.argv) == 3 else now
    if end < start:
        raise ValueError('giờ kết thúc trước giờ bắt đầu')
    raw_domain = os.environ.get('SITE_DOMAIN') or os.environ.get('HOST') or Path(os.environ.get('DOCROOT', '')).name
    domain = urlsplit(raw_domain if '://' in raw_domain else '//' + raw_domain).hostname or ''
    if not re.fullmatch(r'[A-Za-z0-9.-]+', domain):
        raise ValueError('cần SITE_DOMAIN hợp lệ')
    access = Path(os.environ['ACCESS_LOG'])
    error = Path(os.environ.get('ERROR_LOG', '/usr/local/lsws/logs/error.log'))
    requests = bad_http = fatal = bad_parse = unknown_fatal = 0
    domain_tag = re.compile(r'#' + re.escape(domain) + r'(?=[:\]\s,]|$)', re.I)
    with access.open(errors='replace') as source:
        for line in source:
            if not line.strip():
                continue
            stamp = re.search(r'\[([^]]+)\]', line)
            status = re.search(r'"[^\"]*"\s+(\d{3})(?:\s|$)', line)
            try:
                when = dt.datetime.strptime(stamp[1], '%d/%b/%Y:%H:%M:%S %z')
            except (TypeError, ValueError):
                bad_parse += 1
                continue
            if not start <= when <= end:
                continue
            if not status:
                bad_parse += 1
                continue
            requests += 1
            bad_http += status[1].startswith('5')
    with error.open(errors='replace') as source:
        for line in source:
            if not re.search(r'PHP (?:Fatal|Parse)', line):
                continue
            stamp = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if not stamp:
                bad_parse += 1
                continue
            when = dt.datetime.strptime(stamp[1], '%Y-%m-%d %H:%M:%S').replace(tzinfo=now.tzinfo)
            if start <= when <= end:
                if domain_tag.search(line):
                    fatal += 1
                elif not re.search(r'#[A-Za-z0-9.-]+(?=[:\]\s,]|$)', line):
                    unknown_fatal += 1
    incomplete = bad_parse or unknown_fatal or not requests
    result = 'INCOMPLETE' if incomplete else 'FAIL' if bad_http or fatal else 'PASS'
    print(f'5xx_tu_{sys.argv[1]}={bad_http} php_fatal_{domain}_tu_{sys.argv[1]}={fatal} '
          f'access_requests={requests} parse_errors={bad_parse} fatal_unattributed={unknown_fatal} '
          f'window_start={start.isoformat()} window_end={end.isoformat()} status={result}')
    sys.exit(2 if incomplete else 1 if bad_http or fatal else 0)
except (OSError, ValueError, KeyError) as exc:
    print('HEALTH_INCOMPLETE: ' + type(exc).__name__, file=sys.stderr)
    sys.exit(2)
PY
