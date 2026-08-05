#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bang1_parser.py — Đọc BẢNG 1 «OVERVIEW KPI PAGEVIEW & APPLY THANKS» và TỰ KIỂM SỐ.

Vì sao cần: BẢNG 1 là nguồn DUY NHẤT được phép dùng cho mọi con số tăng/giảm và tỉ
trọng theo nhóm trang trong deck tháng/quý (luật Vincent 03/08/2026). Nhưng bảng này
do người dựng công thức tay nên đã nhiều lần lỗi: kéo nhầm công thức từ dòng khác,
trừ ngược ra PV âm, chia % nhầm cột mẫu số. Số sai lọt vào deck gửi COO là mất uy tín
thật, nên bảng phải qua cổng kiểm tự động trước khi được render.

Script làm 2 việc:
  1. Parse ra JSON chuẩn hoá (nuôi build_deck.py)
  2. Tính lại Δ và % TỪ CHÍNH 2 cột giá trị gốc rồi đối chiếu với ô sheet đang ghi,
     kiểm tổng cụm/tổng site, bắt ô âm, ô #REF!, kỳ báo cáo sai ngày/năm.
     Còn lệch → exit code 1 (dùng làm gate: không cho build deck).

Cách chạy:
  python3 bang1_parser.py --config <instance>/09-reporting/report-config.yaml --period 2026-07
  python3 bang1_parser.py --config ... --period 2026-Q1 --out <dir>/bang1.json --fixlist <file>.md
  python3 bang1_parser.py --config ... --all          # kiểm mọi kỳ khai trong config

Đọc SONG SONG cả FORMATTED_VALUE lẫn UNFORMATTED_VALUE: giá trị thô để tính toán
(chuỗi đã format mất độ chính xác), chuỗi format để biết ô nào là kiểu phần trăm —
Sheets lưu ô % dưới dạng tỉ lệ 0-1 nên phải nhân 100 mới so được.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402
from google.oauth2 import service_account  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Sai số cho phép khi đối chiếu. Δ là số nguyên pageview nên gần như phải khớp tuyệt đối;
# % cho 0,05 điểm để bỏ qua sai lệch làm tròn hiển thị.
TOL_DELTA = 1.0
TOL_PCT = 0.05

# Metric thực sự lên deck. Ô lỗi ngoài các metric này chỉ cảnh báo, không chặn build.
RENDERED_METRICS = {"pv", "apply", "applythanks"}


def log(m):
    print(m, flush=True)


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_config_dir"] = os.path.dirname(os.path.abspath(path))
    return cfg


def sheets_service(cfg):
    cand = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or cfg.get("credentials")
    cand = os.path.expanduser(cand)
    if not os.path.isfile(cand):
        sys.exit(f"LỖI: không thấy file credentials: {cand}")
    creds = service_account.Credentials.from_service_account_file(cand, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def read_grid(svc, sid, rng):
    """Trả (raw, fmt) — cùng vùng, 2 cách render, đã pad đều chiều dài dòng."""
    resp = svc.spreadsheets().values().batchGet(
        spreadsheetId=sid, ranges=[rng, rng],
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()
    raw = resp["valueRanges"][0].get("values", [])
    resp2 = svc.spreadsheets().values().get(
        spreadsheetId=sid, range=rng, valueRenderOption="FORMATTED_VALUE",
    ).execute()
    fmt = resp2.get("values", [])
    width = max([len(r) for r in raw + fmt] + [12])
    pad = lambda g: [(r + [""] * width)[:width] for r in g]  # noqa: E731
    return pad(raw), pad(fmt)


# Đọc thô, ô lỗi về dạng '#REF! (Reference does not exist)' — KHÔNG kết thúc bằng '!'
ERR_RE = re.compile(r"^#(REF|DIV/0|N/A|VALUE|NAME\?|NUM|NULL|ERROR)", re.I)


def err_token(v):
    s = str(v).strip()
    m = ERR_RE.match(s)
    return s.split()[0] if m else None


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def pct_value(raw_cell, fmt_cell):
    """Ô % trong Sheets lưu tỉ lệ 0-1 → quy về điểm phần trăm. Nhận biết bằng chuỗi format."""
    n = num(raw_cell)
    if n is None:
        return None
    return n * 100 if "%" in str(fmt_cell) else n


def find_header(raw):
    """Trả về dòng CHỨA CÁC CỘT Δ — đây mới là dòng định vị được metric.

    Bảng có lúc dùng header 1 tầng (tên nhóm và cột Δ cùng dòng), có lúc 2 tầng: dòng
    trên gộp ô «1. KPI PAGEVIEW» / «2. KPI APPLY THANKS», dòng dưới mới là tên cột thật.
    Neo vào chữ «Nhóm trang» rồi dò xuống tối đa 3 dòng để bắt được cả hai kiểu."""
    anchor = None
    for i, r in enumerate(raw):
        joined = " | ".join(str(c) for c in r).lower()
        if "nhóm trang" in joined:
            anchor = i
            break
    if anchor is None:
        return None
    for i in range(anchor, min(anchor + 3, len(raw))):
        if find_metric_cols(raw[i]):
            return i
    return anchor


def find_metric_cols(header):
    """Định vị cột theo chữ trong header thay vì đóng cứng vị trí — bảng tháng và bảng
    quý cùng bố cục nhưng tiêu đề khác nhau, và team có thể chèn cột bất cứ lúc nào.
    Mỗi khối metric = [cur, prev, Δ, %] với Δ nhận ra bằng ký tự 'Δ'."""
    blocks = []
    for i, c in enumerate(header):
        t = " ".join(str(c).split()).lower()
        if t.startswith("δ") or t.startswith("Δ".lower()):
            name = t.lstrip("δ ").strip() or "metric"
            cur, prev = i - 2, i - 1
            pct = i + 1
            if cur < 2:
                continue
            blocks.append({"metric": name, "cur": cur, "prev": prev, "delta": i, "pct": pct})
    return blocks


def parse_bang1(raw, fmt, period_label):
    h = find_header(raw)
    if h is None:
        return None, [{"kind": "cau-truc", "cell": "-", "what": "không tìm thấy dòng header chứa «Nhóm trang»"}]

    header = raw[h]
    blocks = find_metric_cols(header)
    if not blocks:
        return None, [{"kind": "cau-truc", "cell": f"dòng {h+1}",
                       "what": "không định vị được cột Δ nào trong header"}]

    rows, issues = [], []

    def cell(r_idx, c_idx):
        return f"{col_letter(c_idx)}{r_idx + 1}"

    # ── quét thân bảng: từ sau header tới hết dòng TỔNG TOÀN SITE ──
    end = len(raw)
    for i in range(h + 1, len(raw)):
        first = " ".join(str(raw[i][0]).split())
        if first.upper().startswith("TỔNG TOÀN SITE"):
            end = i + 1
            break

    # quét ô lỗi trên TOÀN bảng (kể cả cột nằm ngoài các khối metric — bảng quý còn sót
    # mấy cột Session của template tuần, đang #REF!, dễ làm người đọc sheet hoang mang)
    # Ô lỗi nằm trong cột metric ĐƯỢC RENDER (pv/apply) thì chặn build; nằm ở cột không
    # dùng (vd cột Session sót lại của template tuần) thì chỉ cảnh báo — gate chặn vì
    # chuyện không ảnh hưởng số trên deck sẽ nhanh chóng bị bỏ qua.
    rendered_cols = {c for b in blocks if b["metric"] in RENDERED_METRICS
                     for c in (b["cur"], b["prev"], b["delta"], b["pct"])}
    seen_err = {}
    for i in range(h, end):
        for c_idx, v in enumerate(raw[i]):
            tok = err_token(v)
            if not tok:
                continue
            head_txt = " ".join(str(raw[h][c_idx]).split())[:34] or f"cột {col_letter(c_idx)}"
            seen_err.setdefault((head_txt, tok, c_idx in rendered_cols), []).append(f"{col_letter(c_idx)}{i+1}")
    for (head_txt, tok, is_rendered), cells in seen_err.items():
        issues.append({
            "kind": "o-loi",
            "severity": "block" if is_rendered else "warn",
            "cell": cells[0] + (f" (+{len(cells)-1} ô)" if len(cells) > 1 else ""),
            "row_name": head_txt,
            "what": (f"ô lỗi công thức {tok} trong cột đang được render lên deck — phải sửa"
                     if is_rendered else
                     f"ô lỗi công thức {tok} ở cột KHÔNG dùng trong báo cáo tháng/quý "
                     f"(sót lại từ template tuần) — nên xoá cột cho sạch sheet, không chặn build"),
        })

    for i in range(h + 1, end):
        r_raw, r_fmt = raw[i], fmt[i]
        name = " ".join(str(r_raw[0]).split()).lstrip("•").strip()
        if not name:
            continue
        upper = name.upper()
        kind = ("cum_kpi" if upper.startswith("TỔNG CỤM KPI")
                else "toan_site" if upper.startswith("TỔNG TOÀN SITE")
                else "group")
        kpi_flag = " ".join(str(r_raw[1]).split()).strip()
        entry = {"name": name, "row": i + 1, "kind": kind,
                 "in_kpi_cluster": kpi_flag.lower().startswith("có"), "metrics": {}}

        for b in blocks:
            cur = num(r_raw[b["cur"]])
            prev = num(r_raw[b["prev"]])
            d_sheet = num(r_raw[b["delta"]])
            p_sheet = pct_value(r_raw[b["pct"]], r_fmt[b["pct"]])

            if cur is None and prev is None:
                continue

            m = {"cur": cur, "prev": prev, "delta_sheet": d_sheet, "pct_sheet": p_sheet}
            if cur is not None and prev is not None:
                m["delta"] = cur - prev
                m["pct"] = (cur - prev) / prev * 100 if prev else None

                if d_sheet is None:
                    issues.append({"kind": "thieu-o", "cell": cell(i, b["delta"]), "row_name": name,
                                   "what": f"[{b['metric']}] thiếu ô Δ", "expect": f"{m['delta']:,.0f}"})
                elif abs(d_sheet - m["delta"]) > TOL_DELTA:
                    issues.append({"kind": "delta-sai", "cell": cell(i, b["delta"]), "row_name": name,
                                   "what": f"[{b['metric']}] Δ sheet ghi {d_sheet:,.0f}",
                                   "expect": f"{m['delta']:,.0f}"})

                if m["pct"] is not None:
                    if p_sheet is None:
                        issues.append({"kind": "thieu-o", "cell": cell(i, b["pct"]), "row_name": name,
                                       "what": f"[{b['metric']}] thiếu ô %", "expect": f"{m['pct']:.2f}%"})
                    elif abs(p_sheet - m["pct"]) > TOL_PCT:
                        extra = ""
                        # chẩn đoán mẫu số: chia cho kỳ hiện tại thay vì kỳ so sánh
                        if cur and abs(p_sheet - (cur - prev) / cur * 100) <= TOL_PCT:
                            extra = " — đang chia cho cột KỲ NÀY, phải chia cho cột KỲ SO SÁNH"
                        issues.append({"kind": "pct-sai", "cell": cell(i, b["pct"]), "row_name": name,
                                       "what": f"[{b['metric']}] % sheet ghi {p_sheet:.2f}%{extra}",
                                       "expect": f"{m['pct']:.2f}%"})

            for label, c_idx in (("kỳ này", b["cur"]), ("kỳ so sánh", b["prev"])):
                v = num(r_raw[c_idx])
                if v is not None and v < 0:
                    issues.append({"kind": "gia-tri-am", "cell": cell(i, c_idx), "row_name": name,
                                   "what": f"[{b['metric']}] {label} ra số ÂM ({v:,.0f}) — pageview/apply không thể âm"})

            entry["metrics"][b["metric"]] = m
        rows.append(entry)

    # ── kiểm tổng: cụm KPI = Σ dòng đánh «Có», toàn site = Σ mọi nhóm trang ──
    groups = [r for r in rows if r["kind"] == "group"]
    for target_kind, subset, label in (
        ("cum_kpi", [r for r in groups if r["in_kpi_cluster"]], "TỔNG CỤM KPI = Σ các dòng đánh «Có»"),
        ("toan_site", groups, "TỔNG TOÀN SITE = Σ mọi nhóm trang"),
    ):
        tot = next((r for r in rows if r["kind"] == target_kind), None)
        if not tot:
            continue
        for b in blocks:
            mk = b["metric"]
            tm = tot["metrics"].get(mk)
            if not tm or tm.get("cur") is None:
                continue
            parts = [r["metrics"][mk]["cur"] for r in subset
                     if mk in r["metrics"] and r["metrics"][mk].get("cur") is not None]
            if not parts:
                continue
            s = sum(parts)
            if abs(s - tm["cur"]) > max(2.0, abs(tm["cur"]) * 0.0005):
                issues.append({
                    "kind": "tong-lech",
                    "cell": f"{col_letter(b['cur'])}{tot['row']}",
                    "row_name": tot["name"],
                    "what": f"[{mk}] {label}: sheet ghi {tm['cur']:,.0f}, cộng {len(parts)} dòng ra {s:,.0f} "
                            f"(lệch {s - tm['cur']:,.0f})",
                    "expect": f"{s:,.0f}",
                })

    # ── kiểm khối kỳ báo cáo phía trên bảng (bắt lỗi gõ nhầm năm/ngày) ──
    this_year = dt.date.today().year
    for i in range(0, min(h, len(fmt))):
        text = " ".join(str(c) for c in fmt[i] if str(c).strip())
        if not text or not re.search(r"kỳ|quý|tháng", text, re.I):
            continue
        for m in re.finditer(r"\b(\d{4})\b", text):
            y = int(m.group(1))
            if y > this_year or y < this_year - 2:
                issues.append({"kind": "ky-bao-cao", "cell": f"dòng {i+1}", "row_name": text[:70],
                               "what": f"năm {y} nằm ngoài khoảng hợp lệ ({this_year-2}–{this_year})"})
        dates = re.findall(r"(\d{1,2})[/.](\d{1,2})", text)
        if len(dates) >= 4:
            (d1, m1), (d2, m2), (d3, m3), (d4, m4) = dates[:4]
            if m1 == m3 and m2 == m4 and m1 != m2:
                issues.append({"kind": "ky-bao-cao", "cell": f"dòng {i+1}", "row_name": text[:70],
                               "what": f"2 vế kỳ so sánh cùng tháng bắt đầu ({m1}) — vế sau nhiều khả năng "
                                       f"phải là {d3}/{m2}"})

    return {"period_label": period_label, "header_row": h + 1,
            "metrics": [b["metric"] for b in blocks], "rows": rows}, issues


def fmt_issue_table(all_issues):
    out = ["| Kỳ | Ô | Dòng | Vấn đề | Giá trị đúng |", "|---|---|---|---|---|"]
    for period, iss in all_issues:
        for it in iss:
            out.append(f"| {period} | `{it['cell']}` | {it.get('row_name','—')[:44]} | "
                       f"{it['what']} | {it.get('expect','—')} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", default=None, help="Khoá kỳ trong config, vd 2026-07 hoặc 2026-Q1")
    ap.add_argument("--all", action="store_true", help="Kiểm mọi kỳ khai trong config")
    ap.add_argument("--out", default=None, help="Ghi JSON chuẩn hoá (1 kỳ) hoặc thư mục (nhiều kỳ)")
    ap.add_argument("--fixlist", default=None, help="Ghi danh sách ô cần sửa dạng markdown")
    ap.add_argument("--quiet", action="store_true")
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

    svc = sheets_service(cfg)
    all_issues, results = [], {}

    for k in keys:
        p = periods[k]
        wb = (cfg.get("spreadsheets") or {}).get(p["workbook"])
        if not wb:
            sys.exit(f"LỖI: workbook {p['workbook']!r} của kỳ {k} không có trong spreadsheets:")
        rng = f"'{p['bang1_tab']}'!A1:P40"
        log(f"\n{'='*96}\nKỲ {k} — {p['label']} · tab {p['bang1_tab']!r}")
        raw, fmt = read_grid(svc, wb["id"], rng)
        parsed, issues = parse_bang1(raw, fmt, p["label"])
        if parsed is None:
            for it in issues:
                log(f"  ✗ {it['what']}")
            all_issues.append((k, issues))
            continue

        results[k] = parsed
        if not args.quiet:
            log(f"  header dòng {parsed['header_row']} · metric: {', '.join(parsed['metrics'])} · "
                f"{len(parsed['rows'])} dòng")
            for r in parsed["rows"]:
                mk = parsed["metrics"][0]
                m = r["metrics"].get(mk, {})
                if m.get("cur") is None:
                    continue
                mark = "◆" if r["kind"] != "group" else ("✓" if r["in_kpi_cluster"] else " ")
                log(f"   {mark} {r['name'][:44]:<44} {m['cur']:>13,.0f} vs {m['prev']:>13,.0f} "
                    f"→ {m.get('delta',0):>12,.0f} ({(m.get('pct') or 0):+.2f}%)")

        blocking = [i for i in issues if i.get("severity", "block") == "block"]
        warnings_ = [i for i in issues if i.get("severity", "block") == "warn"]
        if blocking:
            log(f"  ✗ {len(blocking)} ô CHẶN BUILD:")
            for it in blocking:
                log(f"     {it['cell']:<12} {it.get('row_name','')[:40]:<40} {it['what']}"
                    + (f"  → đúng: {it['expect']}" if it.get("expect") else ""))
        if warnings_:
            log(f"  ⚠ {len(warnings_)} ô cảnh báo (không chặn build):")
            for it in warnings_:
                log(f"     {it['cell']:<12} {it.get('row_name','')[:40]:<40} {it['what']}")
        if not blocking and not warnings_:
            log("  ✓ PASS — mọi Δ, %, tổng đều khớp")
        elif not blocking:
            log("  ✓ PASS — số render đều khớp (chỉ còn cảnh báo dọn sheet)")
        if issues:
            all_issues.append((k, issues))

    if args.out:
        if len(keys) == 1 and not args.out.endswith(os.sep) and not os.path.isdir(args.out):
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results[keys[0]], f, ensure_ascii=False, indent=1)
            log(f"\nJSON: {args.out}")
        else:
            os.makedirs(args.out, exist_ok=True)
            for k, v in results.items():
                path = os.path.join(args.out, f"bang1_{k}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(v, f, ensure_ascii=False, indent=1)
                log(f"JSON: {path}")

    n_block = sum(1 for _, iss in all_issues for i in iss if i.get("severity", "block") == "block")
    n_warn = sum(1 for _, iss in all_issues for i in iss if i.get("severity", "block") == "warn")
    if all_issues:
        if n_block:
            log(f"\n{'='*96}\nGATE: FAIL — {n_block} ô chặn build"
                + (f" (+{n_warn} cảnh báo)" if n_warn else "")
                + ". KHÔNG render số §1-§3 cho tới khi sửa xong.")
        else:
            log(f"\n{'='*96}\nGATE: PASS — số render đều khớp; còn {n_warn} ô cảnh báo nên dọn cho sạch sheet.")
        if args.fixlist:
            os.makedirs(os.path.dirname(os.path.abspath(args.fixlist)), exist_ok=True)
            block_rows = [(p, [i for i in iss if i.get("severity", "block") == "block"]) for p, iss in all_issues]
            warn_rows = [(p, [i for i in iss if i.get("severity", "block") == "warn"]) for p, iss in all_issues]
            body = [
                "# Danh sách ô cần sửa — BẢNG 1 (Overview KPI Pageview & Applythanks)",
                "",
                f"> Máy dò tự động ngày {dt.date.today():%d/%m/%Y} · script `bang1_parser.py`.",
                "> Mỗi dòng dưới đây là ô mà **Δ hoặc % không khớp với chính 2 cột giá trị gốc "
                "nằm ngay bên trái nó**, hoặc ô ra giá trị không thể có (pageview âm, `#REF!`).",
                "> Cột «Giá trị đúng» là kết quả tính lại từ 2 cột gốc — sửa công thức cho ra đúng số này.",
                "",
                "## A. Phải sửa — đang chặn việc dựng báo cáo",
                "",
                "Đây là các ô mà con số sẽ lên thẳng slide gửi khách.",
                "",
                fmt_issue_table(block_rows) if any(r for _, r in block_rows) else "_Không còn ô nào._",
                "",
                "## B. Nên dọn — không chặn báo cáo",
                "",
                fmt_issue_table(warn_rows) if any(r for _, r in warn_rows) else "_Không còn ô nào._",
                "",
                "## Sau khi sửa",
                "",
                "```bash",
                "python3 skills/gtv-weekly-report/scripts/bang1_parser.py \\",
                "  --config 09-reporting/report-config.yaml --all",
                "```",
                "",
                "Thấy `GATE: PASS` là xong.",
            ]
            with open(args.fixlist, "w", encoding="utf-8") as f:
                f.write("\n".join(body) + "\n")
            log(f"Danh sách gửi team: {args.fixlist}")
        sys.exit(1 if n_block else 0)

    log(f"\n{'='*96}\nGATE: PASS — {len(keys)} kỳ, không ô nào lệch.")


if __name__ == "__main__":
    main()
