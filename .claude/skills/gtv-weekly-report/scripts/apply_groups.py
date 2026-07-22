#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_groups.py — Tổng hợp Apply theo Page Group từ tab «Data Apply thanks»
(feedback SEO Lead 22/07/2026: slide Apply OVERVIEW theo page group đứng TRƯỚC
slide Apply theo Intent). Range trong config chỉ lấy ~80 dòng đầu nên KHÔNG đủ
để cộng nhóm — script này tải NGUYÊN tab về CSV (1 request export, không tốn
quota values API) rồi aggregate local. Không nạp data lớn vào LLM.

Cách chạy:
  python3 apply_groups.py --config <report-config.yaml> --workbook data_phan_tich \
      --tab "Data Apply thanks" [--group-col "Page Group"] \
      [--out <weekdir>/apply_groups.json] [--save-csv <path>]

Cấu trúc tab kỳ vọng: pivot referrer-level có cột group (mặc định «Page Group»)
+ 2 cột giá trị «Apply tuần này…» / «Apply tuần trước…» (bỏ qua các cột «SUM of …»
của pivot phụ nằm cùng hàng).
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402
from google.oauth2 import service_account  # noqa: E402
from google.auth.transport.requests import Request  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]


def to_num(v):
    s = str(v or "").strip().replace(",", "")
    if s in ("", "-", "—"):
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--tab", default=None)
    ap.add_argument("--gid", default=None)
    ap.add_argument("--group-col", default="Page Group")
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-csv", default=None)
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    sid = args.workbook
    if cfg.get("spreadsheets", {}).get(args.workbook):
        sid = cfg["spreadsheets"][args.workbook]["id"]

    cred_path = os.path.expanduser(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or cfg["credentials"])
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    creds.refresh(Request())

    gid = args.gid
    if gid is None:
        if not args.tab:
            sys.exit("LỖI: cần --tab hoặc --gid")
        svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
        meta = svc.spreadsheets().get(spreadsheetId=sid, fields="sheets(properties(sheetId,title))").execute()
        for sh in meta.get("sheets", []):
            if sh["properties"]["title"].strip() == args.tab.strip():
                gid = str(sh["properties"]["sheetId"])
                break
        if gid is None:
            sys.exit(f"LỖI: không thấy tab '{args.tab}' — tab có: "
                     f"{[s['properties']['title'] for s in meta.get('sheets', [])]}")

    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?" + urllib.parse.urlencode(
        {"format": "csv", "gid": gid})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {creds.token}"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    if args.save_csv:
        os.makedirs(os.path.dirname(os.path.abspath(args.save_csv)), exist_ok=True)
        with open(args.save_csv, "w", encoding="utf-8") as f:
            f.write(raw)

    rows = list(csv.reader(io.StringIO(raw)))
    hdr_i = grp_c = cur_c = prev_c = None
    for i, r in enumerate(rows[:12]):
        low = [str(c).lower() for c in r]
        g = [j for j, c in enumerate(r) if str(c).strip().lower() == args.group_col.strip().lower()]
        cur = [j for j, c in enumerate(low)
               if re.search(r"apply\s*tuần\s*này", c) and not c.strip().startswith("sum of")]
        prv = [j for j, c in enumerate(low)
               if re.search(r"apply\s*tuần\s*trước", c) and not c.strip().startswith("sum of")]
        if g and cur and prv:
            hdr_i, grp_c, cur_c, prev_c = i, g[0], cur[0], prv[0]
            break
    if hdr_i is None:
        sys.exit("LỖI: không dò được header (cần cột group + 2 cột Apply tuần này/trước)")

    agg, order = {}, []
    for r in rows[hdr_i + 1:]:
        if grp_c >= len(r):
            continue
        g = str(r[grp_c]).strip()
        if not g or g.lower() in ("grand total", "total"):
            continue
        a = to_num(r[cur_c] if cur_c < len(r) else None)
        b = to_num(r[prev_c] if prev_c < len(r) else None)
        if a is None and b is None:
            continue
        if g not in agg:
            agg[g] = [0, 0]
            order.append(g)
        agg[g][0] += a or 0
        agg[g][1] += b or 0

    groups = []
    for g in sorted(order, key=lambda x: -agg[x][0]):
        a, b = agg[g]
        d = a - b
        groups.append({"group": g, "apply": a, "apply_prev": b, "d": d,
                       "pct": round(d / b * 100, 2) if b else None})
    ta = sum(v[0] for v in agg.values())
    tb = sum(v[1] for v in agg.values())
    out = {
        "source": {"spreadsheet": sid, "gid": gid, "tab": args.tab, "group_col": args.group_col},
        "groups": groups,
        "grand_total": {"apply": ta, "apply_prev": tb, "d": ta - tb,
                        "pct": round((ta - tb) / tb * 100, 2) if tb else None},
    }
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.out} (groups: {len(groups)}, GT {ta:,} / {tb:,})")
    else:
        print(text)


if __name__ == "__main__":
    main()
