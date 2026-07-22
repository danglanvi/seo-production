#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog_groups.py — Tổng hợp bảng «3. Nhóm Blog» cho slide tuần (luật slide-map #15):
Clicks lấy NGUYÊN VĂN pivot «Đánh giá Blog»; Pos pivot KHÔNG có → dẫn xuất =
trung bình vị trí trọng số theo Impressions từ CSV URL-level Data_Blog.

Chạy OFFLINE trên weekdir đã fetch (0 API call — 80/20):
  python3 blog_groups.py --weekdir 02-raw/seo-data/weekly/2026-W11 \
      [--pivot-csv csv/data_phan_tich__danh_gia_blog.csv] \
      [--url-csv csv/data_phan_tich__blog_urllevel.csv] \
      [--out <weekdir>/blog_groups.json]

Output JSON: rows (theo pivot, mỗi nhóm × SEO-flag) + grand_total, mỗi dòng:
  {seo_flag, group, url_count, pv, pv_prev, d_pv, clicks, clicks_prev, d_clicks,
   d_imp, pos, pos_prev, d_pos}  — pos/d_pos = None nếu nhóm không có dòng URL-level.
Quy ước Δ Pos DƯƠNG = lên hạng (pos_prev - pos, theo quy ước sheet).
Số pivot giữ nguyên văn dạng chuỗi (FORMATTED_VALUE) — không tự tính lại.
"""
import argparse
import csv
import json
import os
import re
import sys


def num(v):
    s = str(v or "").strip().replace(",", "").replace("%", "")
    s = s.replace("▲", "").replace("▼", "-")
    if s in ("", "-", "—"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekdir", required=True)
    ap.add_argument("--pivot-csv", default="csv/data_phan_tich__danh_gia_blog.csv")
    ap.add_argument("--url-csv", default="csv/data_phan_tich__blog_urllevel.csv")
    ap.add_argument("--out", default=None, help="mặc định <weekdir>/blog_groups.json")
    args = ap.parse_args()

    wd = args.weekdir
    pivot_path = os.path.join(wd, args.pivot_csv)
    url_path = os.path.join(wd, args.url_csv)
    out_path = args.out or os.path.join(wd, "blog_groups.json")

    # ---- 1) Pos dẫn xuất từ URL-level (trọng số Imp, 2 kỳ) ----
    rows = list(csv.reader(open(url_path, encoding="utf-8")))
    hdr = [str(c).lower() for c in rows[0]]

    def find_one(pat):
        for i, c in enumerate(hdr):
            if re.search(pat, c):
                return i
        return None

    seo_c = find_one(r"seo\s*/\s*non")
    grp_c = find_one(r"nhóm chủ đề")
    pos_cols = [i for i, c in enumerate(hdr) if c.strip().startswith("pos")]
    imp_cols = [i for i, c in enumerate(hdr) if c.strip().startswith("imp")]
    if seo_c is None or grp_c is None or len(pos_cols) < 2 or len(imp_cols) < 2:
        sys.exit("LỖI: URL-level CSV thiếu cột (cần SEO/non, Nhóm chủ đề, 2×Pos, 2×Imp)")

    agg = {}   # (seo, group) -> [sum(pos1*imp1), sum(imp1), sum(pos0*imp0), sum(imp0)]
    tot = [0.0, 0.0, 0.0, 0.0]
    for r in rows[1:]:
        if len(r) <= max(pos_cols[1], imp_cols[1], grp_c):
            continue
        key = (str(r[seo_c]).strip(), str(r[grp_c]).strip())
        g = agg.setdefault(key, [0.0, 0.0, 0.0, 0.0])
        p1, p0 = num(r[pos_cols[0]]), num(r[pos_cols[1]])
        i1, i0 = num(r[imp_cols[0]]) or 0, num(r[imp_cols[1]]) or 0
        if p1 is not None and i1 > 0:
            g[0] += p1 * i1; g[1] += i1; tot[0] += p1 * i1; tot[1] += i1
        if p0 is not None and i0 > 0:
            g[2] += p0 * i0; g[3] += i0; tot[2] += p0 * i0; tot[3] += i0

    def pos_of(g):
        if not g or not g[1] or not g[3]:
            return (None, None, None)
        p, pp = round(g[0] / g[1], 1), round(g[2] / g[3], 1)
        return (p, pp, round(pp - p, 1))  # Δ dương = lên hạng

    # ---- 2) Pivot verbatim + ghép Pos ----
    prow = list(csv.reader(open(pivot_path, encoding="utf-8")))
    out_rows, grand = [], None
    cur_flag = ""
    seen_grand = False
    for r in prow[1:]:
        if len(r) < 12 or seen_grand:
            continue
        flag = str(r[0]).strip()
        grp = str(r[1]).strip()
        if flag:
            cur_flag = flag
        if flag == "Grand Total":
            p, pp, dp = pos_of(tot)
            grand = {"url_count": r[2], "pv": r[3], "pv_prev": r[4], "d_pv": r[5],
                     "clicks": r[6], "clicks_prev": r[7], "d_clicks": r[8],
                     "d_imp": r[11], "pos": p, "pos_prev": pp, "d_pos": dp}
            seen_grand = True  # pivot lặp bảng lần 2 phía dưới — chỉ lấy bảng đầu
            continue
        if not grp:
            continue
        p, pp, dp = pos_of(agg.get((cur_flag or "non-SEO", grp)))
        out_rows.append({"seo_flag": cur_flag or "non-SEO", "group": grp,
                         "url_count": r[2], "pv": r[3], "pv_prev": r[4], "d_pv": r[5],
                         "clicks": r[6], "clicks_prev": r[7], "d_clicks": r[8],
                         "d_imp": r[11], "pos": p, "pos_prev": pp, "d_pos": dp})

    out = {
        "note": "Clicks/PV nguyên văn pivot «Đánh giá Blog»; Pos dẫn xuất trọng số Imp"
                " từ Data_Blog URL-level (pivot không có cột Pos); Δ Pos dương = lên hạng.",
        "rows": out_rows,
        "grand_total": grand,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"wrote {out_path} ({len(out_rows)} rows + grand_total)")


if __name__ == "__main__":
    main()
