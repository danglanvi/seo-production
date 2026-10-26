#!/usr/bin/env python3
"""Đếm sức khoẻ access log trong một khung giờ: tổng request, 4xx, 5xx, phút có 5xx, dòng không đọc được.

Dùng khi lane sửa site cần đo "5xx mới" trước và sau thay đổi. Mã trạng thái đọc bằng regex giống
log_clusters.py, nên log OpenLiteSpeed có trường đầu `'-` và log chuẩn không có trường đó đều đọc đúng.
Không gán cột awk cứng: ngày 23–24/10/2026 bốn lane đếm sai 5xx vì log en và staging đặt mã ở $9, không ở $10.

Ví dụ:
  python3 -B log_health.py --log a.access_log --log b.access_log.gz --since "2026-10-24 12:08:20" [--until ...] [--json]
Giờ so theo giờ ghi trong log (bỏ múi giờ). --since/--until nhận "YYYY-MM-DD HH:MM[:SS]" hoặc "24/Oct/2026:12:08:20".
Mã thoát: 0 = không có 5xx, 1 = có 5xx trong khung, 2 = có file không đọc được dòng nào (không được ghi "0 lỗi").
"""
import argparse
import gzip
import json
import re
import sys
from collections import Counter
from datetime import datetime

LINE = re.compile(r"^'?(?:\S+ )?(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] \"[^\"]*\" (?P<status>\d{3}) ")


def parse_when(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%b/%Y:%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise SystemExit(f"Không hiểu giờ: {s}")


def scan(path, since=None, until=None):
    op = gzip.open if str(path).endswith(".gz") else open
    r = {"file": str(path), "lines": 0, "parsed": 0, "unparsed": 0, "in_window": 0, "4xx": 0, "5xx": 0}
    minutes = Counter()
    with op(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            r["lines"] += 1
            m = LINE.match(line)
            if not m:
                r["unparsed"] += 1
                continue
            r["parsed"] += 1
            t = datetime.strptime(m["time"].split()[0], "%d/%b/%Y:%H:%M:%S")
            if (since and t < since) or (until and t > until):
                continue
            r["in_window"] += 1
            code = m["status"][0]
            if code == "4":
                r["4xx"] += 1
            elif code == "5":
                r["5xx"] += 1
                minutes[t.strftime("%Y-%m-%d %H:%M")] += 1
    r["minutes_5xx"] = dict(minutes.most_common(10))
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", action="append", required=True, help="file access log, .gz đọc thẳng; lặp cho nhiều file")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    since = parse_when(a.since) if a.since else None
    until = parse_when(a.until) if a.until else None
    rows = [scan(p, since, until) for p in a.log]
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print("| file | dòng | đọc được | không đọc được | trong khung | 4xx | 5xx | phút có 5xx |")
        print("|---|---|---|---|---|---|---|---|")
        for r in rows:
            mins = ", ".join(f"{k} ({v})" for k, v in r["minutes_5xx"].items()) or "-"
            print(f"| {r['file']} | {r['lines']} | {r['parsed']} | {r['unparsed']} | {r['in_window']} | {r['4xx']} | {r['5xx']} | {mins} |")
    bad = [r["file"] for r in rows if r["parsed"] == 0]
    for b in bad:
        print(f"KHÔNG đọc được dòng nào: {b}. Không được ghi '0 lỗi' cho file này.", file=sys.stderr)
    if bad:
        return 2
    return 1 if any(r["5xx"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
