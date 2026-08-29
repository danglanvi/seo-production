#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capture_sheet_range.py — CHỤP literal một vùng Google Sheet thành PNG
(bậc 2 của thang capture — khi cần hình y nguyên thay vì render HTML).

Cơ chế: mint access token từ service account → tải PDF qua URL export của Sheets
(https://docs.google.com/spreadsheets/d/<id>/export?format=pdf&gid=<gid>&range=<A1>)
→ render PNG bằng Swift/PDFKit (scripts/pdf2png.swift — không cần poppler).

Cách chạy:
  python3 capture_sheet_range.py --config <report-config.yaml> \
      --workbook ke_hoach_tong --tab "Run-rate tuần" --range A1:N30 \
      --out "<instance>/02-raw/screenshots/tools/20260723_runrate-tuan_w12.png"

  (--workbook nhận key trong config HOẶC spreadsheetId trực tiếp; --gid thay được --tab)
"""
import argparse
import os
import _cred  # resolver credential dùng chung
import subprocess
import sys
import tempfile
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workbook", required=True, help="key trong config.spreadsheets HOẶC spreadsheetId")
    ap.add_argument("--tab", default=None, help="tên tab (resolve gid qua API — 1 call)")
    ap.add_argument("--gid", default=None, help="gid tab (bỏ qua --tab nếu có)")
    ap.add_argument("--range", default=None, help="A1 range, vd A1:N30 (bỏ trống = cả tab)")
    ap.add_argument("--out", required=True, help="đường dẫn PNG output (naming theo protocol screenshots)")
    ap.add_argument("--scale", default="2.0")
    ap.add_argument("--portrait", action="store_true")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    sid = args.workbook
    if cfg.get("spreadsheets", {}).get(args.workbook):
        sid = cfg["spreadsheets"][args.workbook]["id"]

    cred_path = _cred.path(cfg)
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    creds.refresh(Request())

    gid = args.gid
    if gid is None:
        if not args.tab:
            sys.exit("LỖI: cần --tab hoặc --gid")
        svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
        meta = svc.spreadsheets().get(spreadsheetId=sid, fields="sheets(properties(sheetId,title))").execute()
        for sh in meta.get("sheets", []):
            p = sh["properties"]
            if p["title"].strip() == args.tab.strip():
                gid = str(p["sheetId"])
                break
        if gid is None:
            titles = [sh["properties"]["title"] for sh in meta.get("sheets", [])]
            sys.exit(f"LỖI: không thấy tab '{args.tab}'. Tab có: {titles}")

    params = {
        "format": "pdf", "gid": gid, "size": "A4",
        "portrait": "true" if args.portrait else "false",
        "scale": "2",  # fit to width
        "top_margin": "0.2", "bottom_margin": "0.2", "left_margin": "0.2", "right_margin": "0.2",
        "sheetnames": "false", "printtitle": "false", "pagenumbers": "false",
        "gridlines": "false", "fzr": "true",
    }
    if args.range:
        params["range"] = args.range
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {creds.token}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        pdf_bytes = resp.read()
    if not pdf_bytes.startswith(b"%PDF"):
        sys.exit("LỖI: response không phải PDF — kiểm tra quyền service account với workbook này")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        pdf_path = os.path.join(td, "capture.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        swift_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf2png.swift")
        prefix = os.path.splitext(os.path.basename(args.out))[0]
        subprocess.run(["swift", swift_src, pdf_path, td, args.scale, prefix], check=True, capture_output=True)
        produced = [p for p in sorted(os.listdir(td)) if p.endswith(".png")]
        if not produced:
            sys.exit("LỖI: PDFKit không render được PNG")
        # 1 trang → đúng tên out; nhiều trang → trang 1 vào out, các trang sau thêm hậu tố
        first = os.path.join(td, produced[0])
        os.replace(first, args.out)
        for extra in produced[1:]:
            dst = os.path.splitext(args.out)[0] + "_" + extra.split("-")[-1]
            os.replace(os.path.join(td, extra), dst)
    print(f"wrote {args.out}")
    print("NHẮC: append log op `capture` + ghi 'Dùng cho: <deliverable/công đoạn>' (protocol §8).")


if __name__ == "__main__":
    main()
