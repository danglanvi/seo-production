#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_period_data.py — Kéo data kỳ THÁNG / QUÝ cho báo cáo tháng + báo cáo quý.

Song sinh với fetch_weekly_data.py (kỳ TUẦN) — dùng lại nguyên bộ máy auth/batchGet/
backoff của file đó, chỉ khác ở chỗ nguồn số là workbook kỳ (khai trong `periods:`
của report-config.yaml) thay vì workbook «Report Tuần N».

Mỗi kỳ kéo 3 nhóm nguồn:
  1. Workbook kỳ (data_thang_7 / data_quy_1): BẢNG 1 + các bảng đánh giá
  2. ke_hoach_tong: run-rate tháng (%HT vs KPI) + run-rate tuần + OKRs Q1/Q2
  3. bao_cao_ket_qua: tab «4.1 REPORT TUẦN» (SOW thực tế) + việc cần phối hợp
Các tab URL-level hàng chục nghìn dòng KHÔNG đi qua đây — chúng được kéo bằng CSV
export trong pv_movers.py / dimension_rollup.py (1 request, không tốn quota values API).

Cách chạy:
  python3 fetch_period_data.py --config <instance>/09-reporting/report-config.yaml --period 2026-07
  python3 fetch_period_data.py --config ... --all
  python3 fetch_period_data.py --config ... --period 2026-Q1 --dry-run

Output:
  02-raw/seo-data/monthly/<period>/{digest.json,digest.md,csv/*}     (mode: month)
  02-raw/seo-data/quarterly/<period>/{digest.json,digest.md,csv/*}   (mode: quarter)
"""
import argparse
import datetime as dt
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from googleapiclient.discovery import build  # noqa: E402

from fetch_weekly_data import (  # noqa: E402  — dùng lại, không chép code
    API_CALLS,
    batch_get,
    load_config,
    log,
    parse_status_counts,
    resolve_credentials,
    save_csv,
    small_table,
)

# Nguồn dùng chung cho mọi kỳ: run-rate là thang đo %HT vs KPI cam kết, OKRs + SOW là
# đầu vào cho khối «việc đã triển khai» và «OKRs quý sau» của báo cáo.
SHARED = {
    "ke_hoach_tong": ["runrate_thang", "runrate_tuan", "okrs_quy_1", "okrs_quy_2"],
    "bao_cao_ket_qua": ["report_tuan_41", "viec_phoi_hop"],
}

BIG_TABLE_KEYS = ("danh_gia", "okrs", "report_tuan_41", "runrate")


def out_dir_for(cfg, period_key, period, output_root=None):
    root = output_root or os.path.dirname(cfg["_config_dir"])
    bucket = "monthly" if period.get("mode") == "month" else "quarterly"
    return os.path.join(root, "02-raw", "seo-data", bucket, period_key)


def fetch_period(cfg, sheets, period_key, period, outdir):
    digest = {
        "meta": {
            "client": cfg.get("client_name") or cfg.get("client"),
            "domain": cfg.get("domain"),
            "period": period_key,
            "mode": period.get("mode"),
            "label": period.get("label"),
            "range": period.get("range"),
            "compare_label": period.get("compare_label"),
            "compare_range": period.get("compare_range"),
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "kpi_targets": cfg.get("kpi_targets", {}),
        },
        "sources": {}, "errors": {}, "sections": {},
    }

    wanted = {period["workbook"]: None}          # None = lấy hết range của workbook kỳ
    wanted.update(SHARED)

    for wb_key, keys in wanted.items():
        wb = (cfg.get("spreadsheets") or {}).get(wb_key)
        if not wb:
            digest["errors"][wb_key] = "workbook không khai trong spreadsheets:"
            log(f"  ⚠ bỏ qua {wb_key} — chưa khai trong config")
            continue
        ranges = wb["ranges"] if keys is None else {k: wb["ranges"][k] for k in keys if k in wb["ranges"]}
        if not ranges:
            continue
        log(f"  batchGet {wb_key} ({len(ranges)} range) …")
        data, errs = batch_get(sheets, wb["id"], ranges, wb_key)
        digest["sources"][wb_key] = wb["id"]
        if errs:
            digest["errors"][wb_key] = errs
        for key, rows in data.items():
            save_csv(outdir, wb_key, key, rows)
            if key == "report_tuan_41":
                digest["sections"]["sow_tasks"] = parse_status_counts(rows)
            elif key.startswith(BIG_TABLE_KEYS):
                # bảng OKRs/đánh giá/run-rate dài hơn bảng tuần — giữ rộng tay hơn
                digest["sections"][key] = small_table(rows, 120)
            else:
                digest["sections"][key] = small_table(rows, 60)

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "digest.json"), "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=1)

    rng = period.get("range") or ["?", "?"]
    cmp_rng = period.get("compare_range") or ["?", "?"]
    md = [
        f"# Digest {period_key} — {period.get('label')}",
        f"- Client: {digest['meta']['client']} ({digest['meta']['domain']})",
        f"- Kỳ: {rng[0]} → {rng[1]}  ·  so với {period.get('compare_label')}: {cmp_rng[0]} → {cmp_rng[1]}",
        f"- API calls: sheets={API_CALLS['sheets']} drive={API_CALLS['drive']}",
        f"- Sections: {', '.join(sorted(digest['sections'].keys()))}",
    ]
    if digest["errors"]:
        md.append(f"- ⚠ Errors: {json.dumps(digest['errors'], ensure_ascii=False)}")
    md.append("")
    md.append("> Số tổng/tăng giảm theo nhóm trang: đọc từ `overview_bang1` (BẢNG 1) — đã qua "
              "`bang1_parser.py`. %HT vs KPI: đọc từ `runrate_thang`. Hai thang đo này KHÁC "
              "phạm vi cụm, không ép khớp nhau (xem `reconcile_totals.py`).")
    with open(os.path.join(outdir, "digest.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    return digest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", default=None, help="Khoá kỳ trong config, vd 2026-07 hoặc 2026-Q1")
    ap.add_argument("--all", action="store_true", help="Kéo mọi kỳ khai trong config")
    ap.add_argument("--output-root", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in kỳ + đích ghi, không gọi API")
    args = ap.parse_args()

    cfg = load_config(args.config)
    periods = cfg.get("periods") or {}
    if args.all:
        keys = list(periods.keys())
    elif args.period:
        keys = [args.period]
    else:
        sys.exit("LỖI: cần --period <khoá> hoặc --all")
    for k in keys:
        if k not in periods:
            sys.exit(f"LỖI: kỳ {k!r} không có trong config (có: {', '.join(periods)})")

    plan = [(k, periods[k], out_dir_for(cfg, k, periods[k], args.output_root)) for k in keys]
    for k, p, outdir in plan:
        rng = p.get("range") or ["?", "?"]
        log(f"{k} · {p.get('label')} · {rng[0]} → {rng[1]} · workbook={p['workbook']}")
        log(f"   → {outdir}")
    if args.dry_run:
        return

    creds = resolve_credentials(cfg)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)

    for k, p, outdir in plan:
        log(f"\n{'='*90}\nKÉO SỐ KỲ {k} — {p.get('label')}")
        d = fetch_period(cfg, sheets, k, p, outdir)
        log(f"  sections: {len(d['sections'])} · errors: {len(d['errors'])}")
        log(f"  digest: {os.path.join(outdir, 'digest.json')}")

    log(f"\nXONG — API calls: sheets={API_CALLS['sheets']}, drive={API_CALLS['drive']}")


if __name__ == "__main__":
    main()
