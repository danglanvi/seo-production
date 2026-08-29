#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_source_links.py — Sinh registry link nguồn dữ liệu cho deck báo cáo.

Vì sao cần: mỗi slide data có khối `.data-meta` ghi nguồn bằng chữ («tab Run-rate
tháng»). Người đọc phía client muốn bấm thẳng vào ĐÚNG tab đó. Script này đọc
`source_links:` trong report-config.yaml, gọi Sheets API lấy `sheetId` (gid) thật
của từng tab rồi ghi ra `data-sources.yaml` — build_deck.py nạp file này và đổi
token `[[key]]` trong content.yaml thành thẻ <a> trỏ đúng tab.

Vì sao KHÔNG hard-code gid trong content.yaml: gid đổi khi team nhân bản workbook
theo kỳ; sinh lại registry rẻ hơn sửa 48 slide.

Cách chạy:
  python3 build_source_links.py --config 09-reporting/report-config.yaml \
      --out 09-reporting/data-sources.yaml [--check]

  --check : chỉ đối chiếu, không ghi file (exit≠0 nếu có tab không tồn tại).

Chỉ ĐỌC metadata sheet (spreadsheets.get, fields=sheets.properties) — 1 call/workbook.
"""
import argparse
import io
import os
import _cred  # resolver credential dùng chung
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("FAIL: thiếu PyYAML (pip install pyyaml)\n")
    sys.exit(2)

SHEET_URL = "https://docs.google.com/spreadsheets/d/%s/edit#gid=%s"


def die(msg):
    sys.stderr.write("FAIL: %s\n" % msg)
    sys.exit(1)


def load_tabs(cfg, wb_keys):
    """{workbook_key: {'id':…, 'title':…, 'tabs':{tên: gid}}} — 1 API call/workbook."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    cred = _cred.path(cfg)
    creds = service_account.Credentials.from_service_account_file(
        cred, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    out = {}
    for key in wb_keys:
        wb = (cfg.get("spreadsheets") or {}).get(key)
        if not wb:
            sys.stderr.write("  ⚠ workbook «%s» không có trong config.spreadsheets\n" % key)
            continue
        meta = svc.spreadsheets().get(
            spreadsheetId=wb["id"],
            fields="properties.title,sheets.properties(sheetId,title)").execute()
        out[key] = {
            "id": wb["id"],
            "title": meta["properties"]["title"],
            "tabs": {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]},
        }
    return out


def main():
    ap = argparse.ArgumentParser(description="Sinh registry link nguồn dữ liệu từ report-config.yaml")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true", help="chỉ đối chiếu, không ghi")
    args = ap.parse_args()

    with io.open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    spec = cfg.get("source_links") or {}
    if not spec:
        die("report-config.yaml chưa có khối `source_links:` — xem references/report-config-schema.md")

    wb_keys = sorted({v["workbook"] for v in spec.values() if v.get("workbook")})
    tabs = load_tabs(cfg, wb_keys) if wb_keys else {}

    sources, missing, errs = {}, [], []
    for key in sorted(spec):
        v = spec[key] or {}
        label = v.get("label") or v.get("tab") or key
        # Nguồn ngoài Google Sheets (Looker, GA4, GSC, file rời) khai url thẳng
        if v.get("url"):
            sources[key] = {"label": label, "url": v["url"],
                            "workbook": v.get("workbook_name") or v.get("note") or ""}
            continue
        wbk, tab = v.get("workbook"), v.get("tab")
        if not wbk or not tab:
            missing.append({"key": key, "label": label,
                            "can": v.get("can") or "chưa có workbook/tab hoặc url"})
            continue
        wb = tabs.get(wbk)
        if not wb:
            errs.append("%s: workbook «%s» không đọc được" % (key, wbk))
            continue
        if tab not in wb["tabs"]:
            near = [t for t in wb["tabs"] if t.strip() == tab.strip()]
            if near:  # tên tab có space thừa đầu/cuối — chuyện thường trên sheet team
                tab = near[0]
            else:
                errs.append("%s: tab «%s» không tồn tại trong «%s»" % (key, tab, wb["title"]))
                continue
        sources[key] = {"label": label, "workbook": wb["title"], "tab": tab,
                        "url": SHEET_URL % (wb["id"], wb["tabs"][tab])}

    for e in errs:
        sys.stderr.write("  ✗ %s\n" % e)
    print("  resolve: %d nguồn có link · %d nguồn còn thiếu · %d lỗi"
          % (len(sources), len(missing), len(errs)))
    if errs:
        sys.exit(1)
    if args.check:
        print("  --check: OK, không ghi file")
        return

    doc = {
        "_note": ("Registry nguồn dữ liệu cho deck báo cáo — SINH TỰ ĐỘNG, đừng sửa tay. "
                  "Sửa khối `source_links:` trong report-config.yaml rồi chạy lại "
                  "scripts/build_source_links.py. Token dùng trong content.yaml: [[key]] "
                  "hoặc [[key|nhãn hiển thị]]."),
        "sources": sources,
    }
    if missing:
        doc["missing"] = missing
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    print("  ghi: %s" % args.out)
    if missing:
        print("  ⚠ nguồn CHƯA có link (hỏi người vận hành):")
        for m in missing:
            print("     · %-26s %s — cần: %s" % (m["key"], m["label"], m["can"]))


if __name__ == "__main__":
    main()
