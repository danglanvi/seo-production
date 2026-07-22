#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pv_movers.py — Lọc top page tăng/giảm theo ΔPV từ tab URL-level (chuẩn team SEO:
ưu tiên PV, ngưỡng |ΔPV| ≥ 100; clicks/imp là cột phụ) — feedback SEO Lead 22/07/2026.

Cơ chế: tải tab về CSV qua export URL (service account token — 1 request, không tốn
quota values API), parse local bằng csv thuần, tính movers. KHÔNG nạp data lớn vào LLM.

Cách chạy:
  python3 pv_movers.py --config <report-config.yaml> --workbook <key|spreadsheetId> \
      --tab "2. PV Job Listing data" [--gid 955293949] \
      [--min-dpv 100] [--top 10] [--out <weekdir>/movers_jl.json] [--save-csv <path>]

Cấu trúc tab kỳ vọng (dò header tự động): cột URL/Đường dẫn + 2 cột PV (gần nhất, trước)
→ ΔPV; nếu có cột Clicks/Imp/Pos 2 kỳ thì đính kèm làm cột phụ.
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
    s = str(v or "").strip().replace(",", "").replace("%", "")
    if s in ("", "-", "—"):
        return None
    try:
        n = float(s)
        return int(n) if n == int(n) else n
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--tab", default=None)
    ap.add_argument("--gid", default=None)
    ap.add_argument("--min-dpv", type=int, default=100)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--out", default=None, help="ghi JSON movers (mặc định in stdout)")
    ap.add_argument("--save-csv", default=None, help="lưu CSV thô đã tải (nên để trong 02-raw/seo-data/weekly/)")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    sid = args.workbook
    if cfg.get("spreadsheets", {}).get(args.workbook):
        sid = cfg["spreadsheets"][args.workbook]["id"]
    rt = cfg.get("report_tuan", {})
    if args.workbook == "report_tuan":
        known = {str(k): v for k, v in (rt.get("known_ids") or {}).items()}
        wk = sorted(known, key=lambda x: int(x))[-1] if known else None
        sid = known.get(wk)
        if not sid:
            sys.exit("LỖI: report_tuan chưa có known_ids — truyền spreadsheetId trực tiếp")

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
    # Dò header: dòng có cột chứa 'PV 7 ngày' (hoặc 'PV tuần') xuất hiện ≥2 lần + 1 cột URL/đường dẫn
    hdr_i, url_c, pv1_c, pv0_c = None, None, None, None
    for i, r in enumerate(rows[:12]):
        low = [str(c).lower() for c in r]
        pv_cols = [j for j, c in enumerate(low) if re.search(r"pv\s*(7\s*ngày|tuần)", c)]
        u_cols = [j for j, c in enumerate(low) if ("đường dẫn" in c or c.strip() in ("url", "page", "trang"))]
        if len(pv_cols) >= 2 and u_cols:
            hdr_i, url_c, pv1_c, pv0_c = i, u_cols[0], pv_cols[0], pv_cols[1]
            break
    if hdr_i is None:
        sys.exit("LỖI: không dò được header (cần cột URL + 2 cột PV)")

    low = [str(c).lower() for c in rows[hdr_i]]
    ck = [j for j, c in enumerate(low) if "click" in c]
    im = [j for j, c in enumerate(low) if re.search(r"imp", c)]
    ps = [j for j, c in enumerate(low) if re.search(r"\bpos", c)]
    # Cột phân loại (Intent/Nhóm ngành/Nhóm chủ đề/Location) — đưa vào item để
    # slide đọc pattern theo nhóm mà không phải tra lại CSV (feedback Vincent 22/07)
    DIM_KEYS = {"intent": "intent", "nhóm ngành": "nganh", "nhóm chủ đề": "chu_de",
                "location": "location", "khu vực": "location", "seo / non": "seo_flag"}
    dims = []
    for j, c in enumerate(low):
        for pat, key in DIM_KEYS.items():
            if pat in c:
                dims.append((j, key))
                break

    items = []
    for r in rows[hdr_i + 1:]:
        if url_c >= len(r):
            continue
        u = str(r[url_c]).strip()
        if not u or u.lower() in ("grand total", "total") or not ("/" in u or u.startswith("http")):
            continue
        pv1 = to_num(r[pv1_c] if pv1_c < len(r) else None)
        pv0 = to_num(r[pv0_c] if pv0_c < len(r) else None)
        if pv1 is None and pv0 is None:
            continue
        pv1, pv0 = pv1 or 0, pv0 or 0
        d = pv1 - pv0
        if abs(d) < args.min_dpv:
            continue
        it = {"url": u, "pv": pv1, "pv_prev": pv0, "d_pv": d,
              "pct": round(d / pv0 * 100, 1) if pv0 else None}
        if len(ck) >= 2:
            c1, c0 = to_num(r[ck[0]] if ck[0] < len(r) else None), to_num(r[ck[1]] if ck[1] < len(r) else None)
            if c1 is not None or c0 is not None:
                it["clicks"], it["clicks_prev"] = c1 or 0, c0 or 0
        if len(ps) >= 2:
            p1, p0 = to_num(r[ps[0]] if ps[0] < len(r) else None), to_num(r[ps[1]] if ps[1] < len(r) else None)
            if p1 is not None and p0 is not None:
                it["pos"], it["pos_prev"] = p1, p0
        for j, key in dims:
            v = str(r[j]).strip() if j < len(r) else ""
            if v:
                it[key] = v
        items.append(it)

    items.sort(key=lambda x: x["d_pv"])
    # losers/gainers tách theo DẤU — không để dòng ΔPV âm lọt vào gainers khi
    # số URL tăng đủ ngưỡng ít hơn --top (bug phát hiện 22/07 trên Data_Blog)
    losers = [it for it in items if it["d_pv"] < 0]
    gainers = [it for it in items if it["d_pv"] > 0]
    out = {
        "source": {"spreadsheet": sid, "gid": gid, "tab": args.tab},
        "rule": f"|ΔPV| ≥ {args.min_dpv} (chuẩn team: ưu tiên PV; clicks/pos là cột phụ)",
        "rows_qualified": len(items),
        "losers": losers[:args.top],
        "gainers": list(reversed(gainers[-args.top:])),
    }
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.out} (qualified: {len(items)})")
    else:
        print(text)


if __name__ == "__main__":
    main()
