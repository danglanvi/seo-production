#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_weekly_data.py — Kéo data tuần cho báo cáo tuần SEO (skill gtv-weekly-report).

Nguyên tắc: 1 lần values.batchGet cho MỖI workbook (tránh quota 60 reads/min),
lưu CSV thô + digest.json gọn để LLM phân tích mà không nạp data lớn vào context.

Cách chạy:
  python3 fetch_weekly_data.py --config <instance>/09-reporting/report-config.yaml [--week N]
                               [--report-id <spreadsheetId>] [--dry-run]

Output (dưới instance root suy từ vị trí config, hoặc --output-root):
  02-raw/seo-data/weekly/<YYYY>-W<NN>/csv/<workbook>__<key>.csv
  02-raw/seo-data/weekly/<YYYY>-W<NN>/digest.json
  02-raw/seo-data/weekly/<YYYY>-W<NN>/digest.md
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402
from google.oauth2 import service_account  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

API_CALLS = {"sheets": 0, "drive": 0}


def log(msg):
    print(msg, flush=True)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_config_dir"] = os.path.dirname(os.path.abspath(path))
    return cfg


def resolve_credentials(cfg):
    cand = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or cfg.get("credentials")
    cand = os.path.expanduser(cand)
    if not os.path.isfile(cand):
        sys.exit(f"LỖI: không thấy file credentials: {cand}")
    return service_account.Credentials.from_service_account_file(cand, scopes=SCOPES)


def week_number(cfg, today=None):
    anchor = dt.date.fromisoformat(str(cfg["week_anchor"]))
    today = today or dt.date.today()
    return (today - anchor).days // 7 + 1


def week_dates(cfg, n):
    anchor = dt.date.fromisoformat(str(cfg["week_anchor"]))
    start = anchor + dt.timedelta(days=(n - 1) * 7)
    end = start + dt.timedelta(days=6)
    return start, end


def fmt_d(d):
    return d.strftime("%d/%m/%Y")


def to_num(v):
    """'1,138,213' → 1138213 · '103%' → 103.0 · '' → None. Giữ nguyên nếu không phải số."""
    if v is None:
        return None
    s = str(v).strip()
    if s in ("", "—", "-"):
        return None
    s2 = s.replace(",", "").replace("%", "").replace(" ", "")
    neg = s2.startswith("(") and s2.endswith(")")
    if neg:
        s2 = s2[1:-1]
    try:
        n = float(s2)
        if neg:
            n = -n
        return int(n) if n == int(n) and "." not in s2 else n
    except ValueError:
        return s


def batch_get(svc, sid, ranges, label):
    """1 batchGet cho cả workbook; lỗi cả cụm → fallback từng range (bỏ range hỏng)."""
    out, errors = {}, {}
    keys = list(ranges.keys())
    for attempt in range(4):
        try:
            API_CALLS["sheets"] += 1
            resp = svc.spreadsheets().values().batchGet(
                spreadsheetId=sid,
                ranges=[ranges[k] for k in keys],
                valueRenderOption="FORMATTED_VALUE",
            ).execute()
            for k, vr in zip(keys, resp.get("valueRanges", [])):
                out[k] = vr.get("values", [])
            return out, errors
        except HttpError as e:
            if e.resp.status == 429:
                wait = 20 * (attempt + 1)
                log(f"  quota 429 ({label}) — chờ {wait}s rồi thử lại…")
                time.sleep(wait)
                continue
            log(f"  batchGet {label} lỗi ({e.resp.status}) — fallback từng range")
            break
    for k in keys:
        for attempt in range(3):
            try:
                API_CALLS["sheets"] += 1
                vr = svc.spreadsheets().values().get(
                    spreadsheetId=sid, range=ranges[k],
                    valueRenderOption="FORMATTED_VALUE",
                ).execute()
                out[k] = vr.get("values", [])
                break
            except HttpError as e:
                if e.resp.status == 429:
                    time.sleep(20 * (attempt + 1))
                    continue
                errors[k] = f"HTTP {e.resp.status}: {e.reason if hasattr(e, 'reason') else e}"
                break
    return out, errors


def find_report_workbook(drive, cfg, n):
    known = {str(k): v for k, v in (cfg.get("report_tuan", {}).get("known_ids") or {}).items()}
    if str(n) in known:
        return known[str(n)], "known_ids"
    pattern = cfg.get("report_tuan", {}).get("name_pattern", "Report Tuần {week}")
    name = pattern.replace("{week}", str(n))
    API_CALLS["drive"] += 1
    resp = drive.files().list(
        q=f"name contains '{name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        fields="files(id,name,modifiedTime)", pageSize=10,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    if not files:
        return None, f"Drive search không thấy '{name}' — cần share workbook cho service account hoặc truyền --report-id"
    files.sort(key=lambda f: f.get("modifiedTime", ""), reverse=True)
    return files[0]["id"], f"drive_search:{files[0]['name']}"


def save_csv(outdir, wb, key, rows):
    path = os.path.join(outdir, "csv", f"{wb}__{key}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    return path


def find_header_row(rows, must_contain):
    for i, r in enumerate(rows):
        joined = " | ".join(str(c) for c in r).lower()
        if all(m.lower() in joined for m in must_contain):
            return i
    return None


def parse_runrate(rows, n):
    """Trích summary 2 KPI + các dòng W* quanh tuần N."""
    out = {"summary": [], "weeks": []}
    for r in rows[:8]:
        if r and str(r[0]).strip() in ("Organic Pageview", "Apply CV"):
            out["summary"].append([c for c in r if str(c).strip() != ""])
    for r in rows:
        if r and re.match(r"^W\d+$", str(r[0]).strip()):
            wn = int(str(r[0]).strip()[1:])
            if n - 5 <= wn <= n + 1:
                out["weeks"].append(r)
    return out


def parse_wow_table(rows):
    """Bảng 1 Overview WoW: tìm header 'Nhóm trang', trả các dòng tới hết bảng."""
    h = find_header_row(rows, ["nhóm trang"])
    if h is None:
        return {"raw_head": rows[:6], "rows": []}
    body = []
    for r in rows[h:]:
        if not any(str(c).strip() for c in r):
            if body:
                break
            continue
        body.append(r)
    return {"header_row_index": h, "rows": body}


def parse_gsc_movers(rows, min_clicks, top_n):
    """data GSC: Page | ... | Clicks this | Clicks prev | Imp this | Imp prev | CTR... → top movers theo ΔClicks."""
    h = find_header_row(rows, ["page", "clicks"])
    if h is None:
        return {"note": "không tìm thấy header Page/Clicks", "gainers": [], "losers": [], "rows_scanned": 0}
    header = rows[h]
    idx_clicks = [i for i, c in enumerate(header) if "clicks" in str(c).lower()]
    idx_pos = [i for i, c in enumerate(header) if re.search(r"\b(pos|position|av)", str(c).lower())]
    idx_imp = [i for i, c in enumerate(header) if "impression" in str(c).lower()]
    if len(idx_clicks) < 2:
        return {"note": "thiếu cột Clicks 2 kỳ", "gainers": [], "losers": [], "rows_scanned": 0}
    c1, c0 = idx_clicks[0], idx_clicks[1]
    movers = []
    for r in rows[h + 1:]:
        if not r or not str(r[0]).strip() or str(r[0]).strip().lower() in ("grand total", "total"):
            continue
        page = str(r[0]).strip()
        v1, v0 = to_num(r[c1] if c1 < len(r) else None), to_num(r[c0] if c0 < len(r) else None)
        if not isinstance(v1, (int, float)):
            v1 = 0
        if not isinstance(v0, (int, float)):
            v0 = 0
        if max(v1, v0) < min_clicks:
            continue
        row = {"page": page, "clicks": v1, "clicks_prev": v0, "d_clicks": v1 - v0,
               "pct": round((v1 - v0) / v0 * 100, 1) if v0 else None}
        if idx_imp[:2] and len(idx_imp) >= 2:
            i1 = to_num(r[idx_imp[0]] if idx_imp[0] < len(r) else None)
            i0 = to_num(r[idx_imp[1]] if idx_imp[1] < len(r) else None)
            if isinstance(i1, (int, float)) and isinstance(i0, (int, float)):
                row["imp"], row["imp_prev"], row["d_imp"] = i1, i0, i1 - i0
        if idx_pos[:2] and len(idx_pos) >= 2:
            p1 = to_num(r[idx_pos[0]] if idx_pos[0] < len(r) else None)
            p0 = to_num(r[idx_pos[1]] if idx_pos[1] < len(r) else None)
            if isinstance(p1, (int, float)) and isinstance(p0, (int, float)):
                row["pos"], row["pos_prev"] = p1, p0
        movers.append(row)
    movers.sort(key=lambda x: x["d_clicks"])
    return {
        "rows_scanned": len(movers),
        "min_clicks": min_clicks,
        "losers": movers[:top_n],
        "gainers": list(reversed(movers[-top_n:])),
    }


def parse_status_counts(rows):
    """Tab task ([Mới] Report tuần): gom task THEO TUẦN KẾ HOẠCH (marker 'Tuần X/... (dd/m - dd/m)'
    hoặc 'Tuần N'), đếm Status per tuần + toàn cục, gom dòng trễ. Slide SOW cần ĐỦ task của tuần."""
    h = find_header_row(rows, ["hạng mục", "status"])
    if h is None:
        return {"note": "không thấy header task", "counts": {}, "late": [], "weeks": {}}
    header = [str(c).strip().lower() for c in rows[h]]

    def col(name_parts):
        for i, c in enumerate(header):
            if all(p in c for p in name_parts):
                return i
        return None

    i_status, i_task = col(["status"]), col(["nội dung"])
    i_late = col(["trễ"])
    counts, late = {}, []
    weeks, order = {}, []
    cur = None
    for r in rows[h + 1:]:
        if not r or not any(str(c).strip() for c in r):
            continue
        c0 = str(r[0]).strip()
        task = str(r[i_task]).strip() if i_task is not None and i_task < len(r) else ""
        sv = str(r[i_status]).strip() if i_status is not None and i_status < len(r) else ""
        lv = str(r[i_late]).strip() if i_late is not None and i_late < len(r) else ""
        if c0.startswith("Plan tháng"):
            cur = None
            continue
        if re.match(r"^Tuần\b", c0) and c0.lower() != "tuần":
            cur = c0
            if cur not in weeks:
                weeks[cur] = {"tasks": [], "counts": {}}
                order.append(cur)
            continue
        if not task:
            continue
        if sv:
            counts[sv] = counts.get(sv, 0) + 1
        if cur:
            weeks[cur]["tasks"].append({"task": task[:200], "status": sv, "note": lv[:120]})
            if sv:
                weeks[cur]["counts"][sv] = weeks[cur]["counts"].get(sv, 0) + 1
        if lv:
            late.append({"tuần": cur or c0, "task": task[:160], "trễ": lv[:120], "status": sv})
    return {"counts": counts, "late": late[:25], "week_order": order, "weeks": weeks}


def small_table(rows, max_rows=40):
    return [r for r in rows[:max_rows] if any(str(c).strip() for c in r)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--week", type=int, default=None, help="Tuần dự án N (mặc định: tuần vừa KHÉP gần nhất)")
    ap.add_argument("--report-id", default=None, help="Spreadsheet ID của workbook Report Tuần N")
    ap.add_argument("--output-root", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Chỉ resolve tuần + nguồn, không gọi API")
    args = ap.parse_args()

    cfg = load_config(args.config)
    today = dt.date.today()
    n_today = week_number(cfg, today)
    # Tuần báo cáo mặc định = tuần đã KHÉP: nếu hôm nay là ngày cuối tuần dự án (thứ Tư) thì vẫn là tuần hiện tại chưa khép → lấy tuần trước
    n = args.week if args.week else (n_today - 1 if week_dates(cfg, n_today)[1] >= today else n_today)
    ws, we = week_dates(cfg, n)
    pws, pwe = week_dates(cfg, n - 1)
    year_tag = ws.isocalendar()[0]
    week_dir = f"{year_tag}-W{n:02d}"

    root = args.output_root or os.path.dirname(cfg["_config_dir"])
    outdir = os.path.join(root, "02-raw", "seo-data", "weekly", week_dir)

    log(f"Tuần dự án W{n}: {fmt_d(ws)} – {fmt_d(we)} (tuần trước: {fmt_d(pws)} – {fmt_d(pwe)})")
    log(f"Output: {outdir}")
    if args.dry_run:
        return

    creds = resolve_credentials(cfg)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    digest = {
        "meta": {
            "client": cfg.get("client_name") or cfg.get("client"),
            "domain": cfg.get("domain"),
            "week": n, "week_label": f"W{n}",
            "range": [ws.isoformat(), we.isoformat()],
            "range_display": f"{fmt_d(ws)} – {fmt_d(we)}",
            "prev_range_display": f"{fmt_d(pws)} – {fmt_d(pwe)}",
            "gsc_lag_days": cfg.get("gsc_lag_days", 2),
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "kpi_targets": cfg.get("kpi_targets", {}),
        },
        "sources": {}, "errors": {}, "sections": {},
    }

    tm_cfg = cfg.get("top_movers", {})
    min_clicks, top_n = int(tm_cfg.get("min_clicks", 30)), int(tm_cfg.get("top_n", 10))

    # ---- các workbook cố định ----
    for wb_key, wb in (cfg.get("spreadsheets") or {}).items():
        log(f"batchGet {wb_key} …")
        data, errs = batch_get(sheets, wb["id"], wb["ranges"], wb_key)
        digest["sources"][wb_key] = wb["id"]
        if errs:
            digest["errors"][wb_key] = errs
        for key, rows in data.items():
            save_csv(outdir, wb_key, key, rows)
            if key == "runrate_tuan":
                digest["sections"]["runrate_tuan"] = parse_runrate(rows, n)
            elif key == "report_tuan_tasks":
                digest["sections"]["sow_status"] = parse_status_counts(rows)
            elif key in ("viec_phoi_hop",):
                digest["sections"][key] = small_table(rows, 40)
            elif key in ("okrs_quy", "runrate_thang"):
                digest["sections"][key] = small_table(rows, 45)
            else:
                digest["sections"][key] = small_table(rows)

    # ---- workbook Report Tuần N ----
    rt_cfg = cfg.get("report_tuan") or {}
    rid, how = (args.report_id, "arg") if args.report_id else find_report_workbook(drive, cfg, n)
    if rid:
        log(f"Report Tuần W{n}: {rid} ({how})")
        data, errs = batch_get(sheets, rid, rt_cfg.get("ranges", {}), "report_tuan")
        digest["sources"]["report_tuan"] = rid
        if errs:
            digest["errors"]["report_tuan"] = errs
        for key, rows in data.items():
            save_csv(outdir, "report_tuan", key, rows)
            if key.startswith("overview_wow"):
                parsed = parse_wow_table(rows)
                if parsed.get("rows") or "bang1_overview_wow" not in digest["sections"]:
                    digest["sections"]["bang1_overview_wow"] = parsed
            elif key.startswith("gsc_"):
                digest["sections"][f"top_movers_{key}"] = parse_gsc_movers(rows, min_clicks, top_n)
                digest["sections"][f"top_movers_{key}"]["source_tab"] = rt_cfg["ranges"][key]
            elif key.startswith("plan_tuan"):
                digest["sections"][key] = parse_status_counts(rows)
            elif key.startswith("danh_gia"):
                digest["sections"][key] = small_table(rows, 65)
            else:
                digest["sections"][key] = small_table(rows)
    else:
        digest["errors"]["report_tuan"] = how
        log(f"⚠ {how}")

    # ---- ghi digest ----
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "digest.json"), "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=1)

    md = [f"# Digest W{n} — {digest['meta']['range_display']}",
          f"- Client: {digest['meta']['client']} ({digest['meta']['domain']})",
          f"- API calls: sheets={API_CALLS['sheets']} drive={API_CALLS['drive']}",
          f"- Sections: {', '.join(sorted(digest['sections'].keys()))}"]
    if digest["errors"]:
        md.append(f"- ⚠ Errors: {json.dumps(digest['errors'], ensure_ascii=False)}")
    rr = digest["sections"].get("runrate_tuan", {}).get("weeks", [])
    for r in rr:
        if str(r[0]).strip() == f"W{n}":
            md.append(f"- Run-rate W{n}: {' | '.join(str(c) for c in r[:13])}")
    with open(os.path.join(outdir, "digest.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    log(f"XONG — API calls: sheets={API_CALLS['sheets']}, drive={API_CALLS['drive']}")
    log(f"digest: {os.path.join(outdir, 'digest.json')}")


if __name__ == "__main__":
    main()
