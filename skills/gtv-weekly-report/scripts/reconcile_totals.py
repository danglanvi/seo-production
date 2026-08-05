#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reconcile_totals.py — Đối chiếu các nguồn cùng nói về "tổng PV/Apply của kỳ" và giải
thích vì sao chúng lệch nhau.

Bối cảnh: dự án có ÍT NHẤT 2 thang đo song song, cùng đúng nhưng khác phạm vi:
  · BẢNG 1 (tab Overview)  → nguồn cho tăng/giảm & tỉ trọng theo nhóm trang
  · Run-rate tháng          → nguồn cho % hoàn thành so với KPI cam kết
  · Khối header của tab kỳ  → con số team gõ tay, có lúc lấy từ Looker thay vì GA4
Ba nguồn này KHÔNG bằng nhau và KHÔNG được ép cho bằng (Vincent chốt 03/08). Việc của
script là in ra bảng lệch kèm diễn giải để deck có 1 slide nói thẳng chuyện đó — thay vì
để SEO Manager phía khách tự phát hiện giữa buổi họp.

Chạy offline hoàn toàn: đọc digest.json + bang1_<kỳ>.json + analysis_*.json đã fetch.

Cách chạy:
  python3 reconcile_totals.py --config <report-config.yaml> --period 2026-Q1
  python3 reconcile_totals.py --config ... --all --out <dir>/reconcile.json
"""
import argparse
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402


def log(m):
    print(m, flush=True)


def to_num(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v or "").strip().replace(",", "").replace("%", "").replace(" ", "")
    if s in ("", "-", "—") or s.startswith("#"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def period_dir(cfg_dir, period_key, period):
    root = os.path.dirname(cfg_dir)
    bucket = "monthly" if period.get("mode") == "month" else "quarterly"
    return os.path.join(root, "02-raw", "seo-data", bucket, period_key)


def months_in_range(rng):
    """['2026-05-01','2026-07-31'] → ['T5/2026','T6/2026','T7/2026']"""
    y0, m0 = int(rng[0][:4]), int(rng[0][5:7])
    y1, m1 = int(rng[1][:4]), int(rng[1][5:7])
    out = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        out.append(f"T{m}/{y}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def parse_runrate_thang(rows, want_months):
    """Tab «Run-rate tháng»: cột = tháng dự án, dòng = KPI/Thực tế/%HT/YoY per metric."""
    hdr_i = next((i for i, r in enumerate(rows)
                  if any(re.fullmatch(r"T\d{1,2}/\d{4}", str(c).strip()) for c in r)), None)
    if hdr_i is None:
        return None
    header = [str(c).strip() for c in rows[hdr_i]]
    cols = {h: j for j, h in enumerate(header) if re.fullmatch(r"T\d{1,2}/\d{4}", h)}
    idx = [cols[m] for m in want_months if m in cols]
    if not idx:
        return None

    def row_label(r):
        """Nhãn dòng KHÔNG cố định ở cột A: sheet có lúc thụt data vào 1 cột (dòng tiêu đề
        khối nằm cột A, dòng số nằm cột B). Lấy ô có chữ đầu tiên trong 3 cột đầu."""
        for c in (r or [])[:3]:
            s = str(c).strip()
            if s:
                return s
        return ""

    def grab(label_pat, block_from=0, block_to=None):
        for i, r in enumerate(rows[block_from:block_to], start=block_from):
            if re.search(label_pat, row_label(r), re.I):
                vals = [to_num(r[j]) if j < len(r) else None for j in idx]
                if any(v is not None for v in vals):
                    return vals, i
        return None, None

    # Biên khối A (Pageview) / B (Apply) / C (CR). Marker phải NEO ĐẦU DÒNG dạng «B · …»:
    # dòng ghi chú đầu tab có chứa chữ «Apply CV» nên bắt bằng từ khoá tự do sẽ cắt nhầm
    # biên ngay dòng 2, khiến toàn bộ số Pageview bị gán sang khối Apply.
    def block_start(letter):
        return next((i for i, r in enumerate(rows)
                     if re.match(rf"^\s*{letter}\s*[·•.]", row_label(r))), None)

    b_start = block_start("B") or len(rows)
    c_start = block_start("C") or len(rows)

    out = {"months": [m for m in want_months if m in cols]}
    for key, pat, lo, hi in (
        ("pv_kpi", r"KPI\s*\(", 0, b_start),
        ("pv_actual", r"Thực tế", 0, b_start),
        ("pv_yoy", r"YOY|Cùng k", 0, b_start),
        ("apply_kpi", r"KPI\s*\(", b_start, c_start),
        ("apply_actual", r"Thực tế", b_start, c_start),
        ("apply_yoy", r"YOY|Cùng k", b_start, c_start),
    ):
        vals, _ = grab(pat, lo, hi)
        out[key] = vals
        out[key + "_sum"] = sum(v for v in vals if v is not None) if vals else None
    return out


def parse_header_block(rows, hdr_limit=13):
    """Khối «KỲ BÁO CÁO & TARGET» phía trên BẢNG 1 — số team gõ tay."""
    found = {}
    for r in rows[:hdr_limit]:
        label = " ".join(str(r[0] if r else "").split())
        if not label:
            continue
        val = next((to_num(c) for c in r[1:4] if to_num(c) is not None), None)
        if val is None:
            continue
        low = label.lower()
        if "pv" in low and ("cụm kpi" in low or "lũy kế" in low):
            found["pv_cum_kpi" if "cùng k" not in low else "pv_cum_kpi_prev"] = (label, val)
        elif "ứng tuyển" in low:
            found["apply" if "cùng k" not in low else "apply_prev"] = (label, val)
    return found


def bang1_totals(bang1):
    out = {}
    for kind in ("cum_kpi", "toan_site"):
        row = next((r for r in bang1["rows"] if r["kind"] == kind), None)
        if not row:
            continue
        for mk, m in row.get("metrics", {}).items():
            if m.get("cur") is not None:
                out[f"{kind}_{mk}"] = (row["name"], m.get("cur"), m.get("prev"))
    return out


def reconcile(cfg, cfg_dir, period_key, period):
    d = period_dir(cfg_dir, period_key, period)
    digest_p = os.path.join(d, "digest.json")
    bang1_p = os.path.join(d, f"bang1_{period_key}.json")
    if not os.path.isfile(digest_p):
        sys.exit(f"LỖI: thiếu {digest_p} — chạy fetch_period_data.py trước")
    if not os.path.isfile(bang1_p):
        sys.exit(f"LỖI: thiếu {bang1_p} — chạy bang1_parser.py --out {bang1_p} trước")
    digest = json.load(open(digest_p, encoding="utf-8"))
    bang1 = json.load(open(bang1_p, encoding="utf-8"))

    months = months_in_range(period["range"])
    rr = parse_runrate_thang(digest["sections"].get("runrate_thang") or [], months)
    hdr = parse_header_block(digest["sections"].get("overview_bang1") or [])
    b1 = bang1_totals(bang1)

    rows = []
    b1_cum = b1.get("cum_kpi_pv")
    if b1_cum:
        rows.append({"nguon": "BẢNG 1 — TỔNG CỤM KPI", "metric": "pv",
                     "cur": b1_cum[1], "prev": b1_cum[2],
                     "pham_vi": "Việc làm + Job Detail + Tool + Blog CV/Lương (4 dòng đánh «Có»)",
                     "dung_cho": "Mọi con số tăng/giảm và tỉ trọng theo nhóm trang", "scope_class": "total"})
    if rr and rr.get("pv_actual_sum"):
        rows.append({"nguon": f"Run-rate tháng — Thực tế ({'+'.join(rr['months'])})", "metric": "pv",
                     "cur": rr["pv_actual_sum"],
                     "prev": rr.get("pv_yoy_sum"),
                     "pham_vi": "Cụm «Việc làm + Tool» theo cách đo GA4 khai trong sheet run-rate",
                     "dung_cho": "% hoàn thành so với KPI kế hoạch năm", "scope_class": "total"})
        if rr.get("pv_kpi_sum"):
            rows.append({"nguon": f"Run-rate tháng — KPI kế hoạch ({'+'.join(rr['months'])})", "metric": "pv",
                         "cur": rr["pv_kpi_sum"], "prev": None,
                         "pham_vi": "Mục tiêu đặt ra, không phải số đo",
                         "dung_cho": "Mẫu số của % hoàn thành", "scope_class": "target"})
    if hdr.get("pv_cum_kpi"):
        rows.append({"nguon": f"Header tab kỳ — «{hdr['pv_cum_kpi'][0]}»", "metric": "pv",
                     "cur": hdr["pv_cum_kpi"][1], "prev": (hdr.get("pv_cum_kpi_prev") or [None, None])[1],
                     "pham_vi": "Số team gõ tay ở đầu tab",
                     "dung_cho": "Đối chiếu nhanh — không dùng render", "scope_class": "total"})

    b1_apply = b1.get("toan_site_apply")
    if b1_apply:
        rows.append({"nguon": "BẢNG 1 — TỔNG TOÀN SITE (Applythanks)", "metric": "apply",
                     "cur": b1_apply[1], "prev": b1_apply[2],
                     "pham_vi": "Applythanks quy về landing page, mọi nhóm trang",
                     "dung_cho": "Tăng/giảm Applythanks theo nhóm trang", "scope_class": "total"})
    if rr and rr.get("apply_actual_sum"):
        rows.append({"nguon": f"Run-rate tháng — Applythanks thực tế ({'+'.join(rr['months'])})", "metric": "apply",
                     "cur": rr["apply_actual_sum"], "prev": rr.get("apply_yoy_sum"),
                     "pham_vi": "Sự kiện ApplyThanks_PMAX từ 4 nguồn (organic, google_jobs_apply, direct, search.google.com)",
                     "dung_cho": "% hoàn thành Applythanks so với KPI", "scope_class": "total"})
    if hdr.get("apply"):
        rows.append({"nguon": f"Header tab kỳ — «{hdr['apply'][0]}»", "metric": "apply",
                     "cur": hdr["apply"][1], "prev": (hdr.get("apply_prev") or [None, None])[1],
                     "pham_vi": "Số team gõ tay ở đầu tab",
                     "dung_cho": "Đối chiếu nhanh — không dùng render", "scope_class": "total"})

    # nguồn URL-level nào tổng khớp BẢNG 1 thì ghi nhận — đó là nguồn hiếm hoi dùng được ở mức tổng
    for f in sorted(os.listdir(d)):
        if not f.startswith("analysis_") or not f.endswith(".json"):
            continue
        a = json.load(open(os.path.join(d, f), encoding="utf-8"))
        if a.get("total_comparable_to_bang1") and a.get("coverage_cur_pct"):
            rows.append({"nguon": f"URL-level «{a['source'].get('tab') or a['source_key']}»",
                         "metric": a.get("metric", "pv"), "cur": a["total_cur"], "prev": a["total_prev"],
                         "pham_vi": f"{a['urls_total']:,} URL · phủ {a['coverage_cur_pct']}% nhóm «{a['scope_ref']}»",
                         "dung_cho": "Đủ điều kiện dùng ở mức tổng (độ phủ 2 kỳ đều ~100%)", "scope_class": "group"})

    # Chỉ so lệch giữa các nguồn CÙNG đo một phạm vi tổng. Một nhóm trang lẻ (Job Detail)
    # hay một con số mục tiêu không phải "cách đo khác của cùng đại lượng" — đem so với
    # tổng cụm sẽ ra con số vô nghĩa kiểu −43%.
    for metric in ("pv", "apply"):
        subset = [r for r in rows if r["metric"] == metric and r["cur"]
                  and r.get("scope_class") == "total"]
        base = subset[0]["cur"] if subset else None
        for r in subset:
            r["lech_vs_bang1"] = r["cur"] - base if base else None
            r["lech_pct"] = round((r["cur"] - base) / base * 100, 2) if base else None

    return {"period": period_key, "label": period.get("label"),
            "months": months, "rows": rows,
            "ket_luan": (
                "Các nguồn trên KHÔNG bằng nhau vì đo phạm vi khác nhau, và không được ép cho bằng. "
                "Luật dùng trong báo cáo: BẢNG 1 là nguồn DUY NHẤT cho mọi con số tăng/giảm và tỉ trọng "
                "theo nhóm trang; Run-rate tháng là nguồn DUY NHẤT cho % hoàn thành so với KPI. "
                "Mỗi slide ghi rõ đang dùng nguồn nào.")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg_dir = os.path.dirname(os.path.abspath(args.config))
    periods = cfg.get("periods") or {}
    keys = list(periods) if args.all else ([args.period] if args.period else [])
    if not keys:
        sys.exit("LỖI: cần --period <khoá> hoặc --all")

    for k in keys:
        if k not in periods:
            sys.exit(f"LỖI: kỳ {k!r} không có trong config")
        res = reconcile(cfg, cfg_dir, k, periods[k])
        log(f"\n{'='*104}\nĐỐI CHIẾU TỔNG — {k} · {res['label']}  (tháng: {', '.join(res['months'])})")
        for metric, title in (("pv", "PAGEVIEW"), ("apply", "APPLYTHANKS")):
            sub = [r for r in res["rows"] if r["metric"] == metric]
            if not sub:
                continue
            log(f"\n  ── {title} ──")
            for r in sub:
                prev = f"{r['prev']:>13,.0f}" if r.get("prev") else " " * 13
                lech = (f"{r['lech_pct']:+7.2f}%" if r.get("lech_pct") is not None
                        else ("  (mốc)" if r.get("scope_class") == "total" else "      —"))
                log(f"    {r['nguon'][:52]:<52} {r['cur']:>13,.0f} {prev}  lệch {lech}")
                log(f"        phạm vi : {r['pham_vi']}")
                log(f"        dùng cho: {r['dung_cho']}")
        out_p = os.path.join(period_dir(cfg_dir, k, periods[k]), f"reconcile_{k}.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        log(f"\n  → {out_p}")
        log(f"  {res['ket_luan']}")


if __name__ == "__main__":
    main()
