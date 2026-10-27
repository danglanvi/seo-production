#!/usr/bin/env python3
"""Tổng hợp sổ lượt gọi Jev do jev.py ghi: số lượt chạy, số lượt gọi API, lỗi, chi phí theo ngày và theo task.

Dùng: python3 jev_ledger.py [--since YYYY-MM-DD] [--label <chuỗi>] [--ledger <file>] [--json]
Sổ mặc định: JEV_LEDGER hoặc ~/.cache/ai-assist/jev-ledger.jsonl. Mã thoát: 0 có số liệu, 2 sổ chưa có dòng nào khớp.
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

LEDGER = Path.home() / ".cache" / "ai-assist" / "jev-ledger.jsonl"


def rows(path, since=None, label=None):
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if since and r.get("t", "") < since:
            continue
        if label and label not in (r.get("label") or ""):
            continue
        out.append(r)
    return out


def summarize(rs):
    def agg(key):
        g = defaultdict(lambda: {"luot": 0, "goi": 0, "loi": 0, "usd": 0.0})
        for r in rs:
            s = g[key(r)]
            s["luot"] += 1
            s["goi"] += r.get("calls", 0)
            s["loi"] += r.get("errors", 0)
            s["usd"] = round(s["usd"] + (r.get("cost") or 0), 6)
        return dict(sorted(g.items()))
    return {"tong": agg(lambda r: "tong")["tong"] if rs else None,
            "theo_ngay": agg(lambda r: r.get("t", "")[:10]),
            "theo_task": agg(lambda r: f'{r.get("task")} {r.get("task_version") or ""}'.strip())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since")
    ap.add_argument("--label")
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    path = a.ledger or Path(os.environ.get("JEV_LEDGER") or LEDGER)
    rs = rows(path, a.since, a.label)
    if not rs:
        print(f"Sổ {path} chưa có dòng nào khớp.", file=sys.stderr)
        return 2
    s = summarize(rs)
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return 0
    t = s["tong"]
    print(f"Tổng: {t['luot']} lượt chạy, {t['goi']} lượt gọi API, {t['loi']} dòng lỗi, {t['usd']:.5f} USD")
    for name in ("theo_ngay", "theo_task"):
        print(name.replace("_", " ").capitalize() + ":")
        for k, v in s[name].items():
            print(f"  {k}: {v['luot']} lượt, {v['goi']} gọi, {v['usd']:.5f} USD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
