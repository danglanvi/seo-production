#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
period_analyze.py — Phân tích URL-level cho kỳ THÁNG / QUÝ: top mover + rollup theo
dimension + độ phủ so với BẢNG 1.

Gộp 2 việc vào 1 lần tải: tab URL-level của CareerViet lên tới 100K dòng (~20MB), tách
thành 2 script rời sẽ tải trùng. Ở kỳ TUẦN, pv_movers.py vẫn giữ nguyên vai trò cũ —
script này KHÔNG thay thế nó, chỉ phục vụ kỳ tháng/quý nơi cấu trúc tab khác hẳn.

Khác biệt cốt lõi so với pv_movers.py: KHÔNG dò header tự động. Cột lấy đúng theo khai
báo trong `periods.<kỳ>.sources.*` của report-config.yaml, vì các tab kỳ tháng/quý bố
cục không thống nhất — riêng tab Job Listing kỳ QUÝ để cột năm trước TRƯỚC cột năm nay,
dò tự động sẽ đảo ngược toàn bộ danh sách tăng/giảm.

Ba thứ script này luôn xuất kèm, vì thiếu là slide sai:
  · coverage_pct — nguồn URL-level chỉ là mẫu con của tổng BẢNG 1; mọi slide dựng từ đây
    phải in chip scope, cấm suy ra số tổng (luật Vincent 03/08 + feedback SEO Lead 22/07)
  · rollup theo từng dimension khai trong config (Intent / ngành / khu vực / chủ đề)
  · cả 2 chiều tăng và giảm, không chỉ chiều xấu

Cách chạy:
  python3 period_analyze.py --config <report-config.yaml> --period 2026-07
  python3 period_analyze.py --config ... --period 2026-Q1 --source jl --save-csv
"""
import argparse
import csv
import io
import json
import os
import _cred  # resolver credential dùng chung
import re
import sys
import urllib.parse
import urllib.request
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402
from google.auth.transport.requests import Request  # noqa: E402
from google.oauth2 import service_account  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]

csv.field_size_limit(10 ** 7)


def log(m):
    print(m, flush=True)


def col_idx(letter):
    """'A'→0, 'AA'→26."""
    n = 0
    for ch in str(letter).strip().upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def to_num(v):
    s = str(v or "").strip().replace(",", "").replace("%", "").replace(" ", "")
    if s in ("", "-", "—", "#REF!", "#DIV/0!", "#N/A"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    try:
        n = float(s)
        return -n if neg else n
    except ValueError:
        return None


def get_creds(cfg):
    p = _cred.path(cfg)
    if not os.path.isfile(p):
        sys.exit(f"LỖI: không thấy credentials {p}")
    creds = service_account.Credentials.from_service_account_file(p, scopes=SCOPES)
    creds.refresh(Request())
    return creds


def tab_gids(creds, sid):
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    meta = svc.spreadsheets().get(spreadsheetId=sid, fields="sheets(properties(sheetId,title))").execute()
    return {sh["properties"]["title"].strip(): str(sh["properties"]["sheetId"]) for sh in meta.get("sheets", [])}


def download_tab(creds, sid, gid, save_to=None):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?" + urllib.parse.urlencode(
        {"format": "csv", "gid": gid})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {creds.token}"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    if save_to:
        os.makedirs(os.path.dirname(os.path.abspath(save_to)), exist_ok=True)
        with open(save_to, "w", encoding="utf-8") as f:
            f.write(raw)
    return list(csv.reader(io.StringIO(raw)))


def cell(row, idx):
    return row[idx] if idx is not None and 0 <= idx < len(row) else None


def read_records(rows, spec, header_row, cur_col, prev_col):
    """Đọc thành list record theo cột KHAI TƯỜNG MINH. header_row đếm từ 1."""
    iu = col_idx(spec["url_col"])
    ic = col_idx(cur_col) if cur_col else None
    ip = col_idx(prev_col) if prev_col else None
    dims = {k: col_idx(v) for k, v in (spec.get("dims") or {}).items()}
    extra = {k: col_idx(v) for k, v in (spec.get("extra") or {}).items()}

    recs = []
    for r in rows[header_row:]:
        u = str(cell(r, iu) or "").strip()
        if not u or u.lower() in ("grand total", "total", "tổng"):
            continue
        if not ("/" in u or u.startswith("http")):
            continue
        cur = to_num(cell(r, ic)) if ic is not None else None
        prev = to_num(cell(r, ip)) if ip is not None else None
        if cur is None and prev is None:
            continue
        rec = {"url": u, "cur": cur or 0.0, "prev": prev or 0.0}
        for k, j in dims.items():
            v = str(cell(r, j) or "").strip()
            if v:
                rec[k] = v
        for k, j in extra.items():
            v = to_num(cell(r, j))
            if v is not None:
                rec[k] = v
        recs.append(rec)
    return recs


def load_source(creds, sid, gids, spec, save_dir=None, key=""):
    """Trả (records, source_meta). Chế độ join: ghép 2 tab theo URL (Job Detail kỳ quý
    nằm ở 2 tab rời, không có sẵn cột Δ)."""
    if spec.get("join") == "url":
        recs = {}
        for which, tab_key, hdr_key, val_field in (
            ("cur", "tab_cur", "header_row_cur", "cur"),
            ("prev", "tab_prev", "header_row_prev", "prev"),
        ):
            tab = spec[tab_key]
            gid = gids.get(tab.strip())
            if gid is None:
                sys.exit(f"LỖI: không thấy tab {tab!r}. Tab có: {sorted(gids)}")
            save = os.path.join(save_dir, "csv", f"{key}__{which}.csv") if save_dir else None
            rows = download_tab(creds, sid, gid, save)
            sub = read_records(rows, spec, spec[hdr_key], spec["cur_col"], None)
            for r in sub:
                tgt = recs.setdefault(r["url"], {"url": r["url"], "cur": 0.0, "prev": 0.0})
                tgt[val_field] = r["cur"]
                for k, v in r.items():
                    if k not in ("url", "cur", "prev") and k not in tgt:
                        tgt[k] = v
        return list(recs.values()), {"join": "url", "tabs": [spec["tab_cur"], spec["tab_prev"]]}

    tab = spec["tab"]
    gid = gids.get(tab.strip())
    if gid is None:
        sys.exit(f"LỖI: không thấy tab {tab!r}. Tab có: {sorted(gids)}")
    save = os.path.join(save_dir, "csv", f"{key}.csv") if save_dir else None
    rows = download_tab(creds, sid, gid, save)
    recs = read_records(rows, spec, spec["header_row"], spec["cur_col"], spec["prev_col"])
    return recs, {"tab": tab, "gid": gid}


UNCLASSIFIED = "(không phân loại)"
_BAD_DIM = {"#n/a", "#ref!", "#div/0!", "#value!", "", "-", "—", "n/a", "na", "null", "chưa phân loại"}


def clean_dim(v):
    """Ô dimension rỗng hoặc lỗi công thức đều là 'chưa gán nhãn' — gộp về một rọ thay vì
    để '#N/A' hiện lên slide như thể là một nhóm ngành có thật."""
    s = str(v or "").strip()
    return UNCLASSIFIED if s.lower() in _BAD_DIM else s


def dim_key(name):
    """Khoá gộp nhãn. Team gõ tay nên cùng một nhóm xuất hiện nhiều biến thể: «Job × Title»
    (dấu nhân U+00D7) và «Job x Title» (chữ x thường) là MỘT, nhưng nếu để nguyên sẽ thành
    2 nhóm — đủ để lật ngược kết luận (đã gặp T7: một bên −209K, một bên +1K)."""
    s = str(name).lower().replace("×", "x").replace("*", "x")
    s = re.sub(r"\s+", " ", s).strip(" .-")
    return s


def rollup(recs, dim):
    buckets = {}
    for r in recs:
        raw = clean_dim(r.get(dim))
        k = dim_key(raw)
        b = buckets.setdefault(k, {"name": raw, "_variants": {}, "urls": 0, "cur": 0.0, "prev": 0.0})
        b["_variants"][raw] = b["_variants"].get(raw, 0) + 1
        b["urls"] += 1
        b["cur"] += r["cur"]
        b["prev"] += r["prev"]
    out = []
    for b in buckets.values():
        variants = b.pop("_variants")
        b["name"] = max(variants, key=variants.get)          # hiển thị theo biến thể phổ biến nhất
        if len(variants) > 1:
            b["merged_variants"] = sorted(variants, key=variants.get, reverse=True)
        b["delta"] = b["cur"] - b["prev"]
        b["pct"] = round(b["delta"] / b["prev"] * 100, 2) if b["prev"] else None
        out.append(b)
    out.sort(key=lambda x: x["delta"])
    return out


def bang1_scope_total(bang1, scope_ref, metric):
    """Tổng BẢNG 1 cho phạm vi tương ứng, trả (kỳ này, kỳ so sánh) — mẫu số tính độ phủ.
    Phải lấy CẢ 2 kỳ: độ phủ lệch nhau giữa 2 kỳ là dấu hiệu mẫu không cùng cohort."""
    if not bang1 or not scope_ref:
        return None, None
    ref = str(scope_ref).strip().lower()
    if ref.startswith("tổng toàn site"):
        row = next((r for r in bang1["rows"] if r["kind"] == "toan_site"), None)
        m = (row or {}).get("metrics", {}).get(metric) or {}
        return m.get("cur"), m.get("prev")
    cur = prev = None
    for r in bang1["rows"]:
        if r["kind"] != "group" or ref not in r["name"].lower():
            continue
        m = r.get("metrics", {}).get(metric)
        if not m:
            continue
        if m.get("cur") is not None:
            cur = (cur or 0) + m["cur"]
        if m.get("prev") is not None:
            prev = (prev or 0) + m["prev"]
    return cur, prev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", required=True)
    ap.add_argument("--source", default=None, help="Chỉ chạy 1 nguồn (mặc định: tất cả)")
    ap.add_argument("--save-csv", action="store_true", help="Giữ lại CSV thô đã tải")
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg_dir = os.path.dirname(os.path.abspath(args.config))
    root = os.path.dirname(cfg_dir)

    periods = cfg.get("periods") or {}
    if args.period not in periods:
        sys.exit(f"LỖI: kỳ {args.period!r} không có trong config (có: {', '.join(periods)})")
    p = periods[args.period]
    sid = cfg["spreadsheets"][p["workbook"]]["id"]

    bucket = "monthly" if p.get("mode") == "month" else "quarterly"
    outdir = args.outdir or os.path.join(root, "02-raw", "seo-data", bucket, args.period)
    os.makedirs(outdir, exist_ok=True)

    bang1 = None
    b1_path = os.path.join(outdir, f"bang1_{args.period}.json")
    if os.path.isfile(b1_path):
        with open(b1_path, encoding="utf-8") as f:
            bang1 = json.load(f)
    else:
        log(f"⚠ chưa có {b1_path} — chạy bang1_parser.py trước để có mẫu số tính độ phủ")

    creds = get_creds(cfg)
    gids = tab_gids(creds, sid)

    sources = p.get("sources") or {}
    keys = [args.source] if args.source else list(sources)
    summary = []

    for key in keys:
        if key not in sources:
            sys.exit(f"LỖI: nguồn {key!r} không có trong kỳ {args.period} (có: {', '.join(sources)})")
        spec = sources[key]
        metric = spec.get("metric", "pv")
        log(f"\n── {args.period} · {key} ({spec.get('tab') or spec.get('tab_cur')}) …")

        recs, src_meta = load_source(creds, sid, gids, spec,
                                     save_dir=outdir if args.save_csv else None, key=key)
        for r in recs:
            r["delta"] = r["cur"] - r["prev"]
            r["pct"] = round(r["delta"] / r["prev"] * 100, 1) if r["prev"] else None

        total_cur = sum(r["cur"] for r in recs)
        total_prev = sum(r["prev"] for r in recs)
        scope_cur, scope_prev = bang1_scope_total(bang1, spec.get("scope_ref"), metric)
        cov_cur = round(total_cur / scope_cur * 100, 1) if scope_cur else None
        cov_prev = round(total_prev / scope_prev * 100, 1) if scope_prev else None

        min_d = float(spec.get("min_dpv", 100))
        qualified = [r for r in recs if abs(r["delta"]) >= min_d]
        losers = sorted([r for r in qualified if r["delta"] < 0], key=lambda x: x["delta"])
        gainers = sorted([r for r in qualified if r["delta"] > 0], key=lambda x: -x["delta"])
        top = int(spec.get("top", 20))

        # Tổng của nguồn URL-level CHỈ so được với BẢNG 1 khi độ phủ 2 kỳ xấp xỉ nhau.
        # Các tab này là lát cắt "top URL PV cao" — tập URL đổi giữa 2 kỳ, nên Δ của mẫu
        # có thể ngược dấu với Δ của tổng mà cả hai đều đúng. Tự phát hiện và khoá lại,
        # không để con số ngược dấu lọt lên slide (note II.2 + III.1 của Vincent 03/08).
        warns = []
        usable_total = True
        if cov_cur is not None and cov_prev is not None:
            if abs(cov_cur - cov_prev) > 3.0:
                usable_total = False
                warns.append(
                    f"độ phủ 2 kỳ lệch nhau ({cov_cur}% kỳ này vs {cov_prev}% kỳ so sánh) — "
                    f"mẫu KHÔNG cùng tập URL giữa 2 kỳ, tổng và %Δ của nguồn này KHÔNG so được "
                    f"với BẢNG 1, có thể ngược dấu mà vẫn đúng")
            if max(cov_cur, cov_prev) > 101.0:
                usable_total = False
                warns.append(
                    f"độ phủ vượt 100% ({max(cov_cur, cov_prev)}%) — nguồn này KHÔNG phải tập con "
                    f"của nhóm «{spec.get('scope_ref')}» trong BẢNG 1 (khác bộ lọc kênh hoặc lẫn URL "
                    f"ngoài nhóm); chỉ dùng ở mức từng URL, không dùng mức tổng")
        elif cov_cur is None:
            warns.append("chưa đối chiếu được với BẢNG 1 (thiếu bang1_<kỳ>.json hoặc scope_ref)")

        src_name = src_meta.get("tab") or " + ".join(src_meta.get("tabs", []))
        scope_note = f"Nguồn URL-level «{src_name}» — {len(recs):,} URL"
        if cov_cur is not None:
            scope_note += (f", phủ {cov_cur}% tổng «{spec.get('scope_ref')}» của BẢNG 1 "
                           f"({total_cur:,.0f} / {scope_cur:,.0f})")
        scope_note += (". Dùng để chỉ ra TRANG NÀO ảnh hưởng và vì sao; "
                       "số tổng và tỉ trọng toàn cục luôn lấy từ BẢNG 1.")
        if warns:
            scope_note += " ⚠ " + " · ".join(warns)

        out = {
            "period": args.period,
            "period_label": p.get("label"),
            "compare_label": p.get("compare_label"),
            "source_key": key,
            "source": src_meta,
            "metric": metric,
            "rule": f"|Δ| ≥ {min_d:,.0f}",
            "urls_total": len(recs),
            "total_cur": total_cur,
            "total_prev": total_prev,
            "total_delta": total_cur - total_prev,
            "total_pct": round((total_cur - total_prev) / total_prev * 100, 2) if total_prev else None,
            "total_comparable_to_bang1": usable_total,   # False → CẤM đưa %Δ tổng của nguồn này lên slide
            "warnings": warns,
            "scope_ref": spec.get("scope_ref"),
            "scope_total_bang1_cur": scope_cur,
            "scope_total_bang1_prev": scope_prev,
            "coverage_cur_pct": cov_cur,
            "coverage_prev_pct": cov_prev,
            "scope_note": scope_note,
            "rows_qualified": len(qualified),
            "losers": losers[:top],
            "gainers": gainers[:top],
            "rollups": {dim: rollup(recs, dim) for dim in (spec.get("dims") or {})},
        }
        path = os.path.join(outdir, f"analysis_{key}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)

        verdict = "tổng SO ĐƯỢC với BẢNG 1" if usable_total else "⛔ tổng KHÔNG so được với BẢNG 1"
        log(f"   {len(recs):,} URL · tổng {total_cur:,.0f} vs {total_prev:,.0f} "
            f"({out['total_pct']:+.2f}%) · phủ {cov_cur}% / {cov_prev}% (kỳ này/kỳ so sánh) → {verdict}")
        for w in warns:
            log(f"   ⚠ {w}")
        log(f"   qualified {len(qualified):,} (|Δ|≥{min_d:,.0f}) · giảm {len(losers):,} · tăng {len(gainers):,}")
        for dim, rows_ in out["rollups"].items():
            worst = rows_[0] if rows_ else None
            best = rows_[-1] if rows_ else None
            if worst and best:
                log(f"   rollup {dim:<10} {len(rows_):>3} nhóm · giảm nhất: {worst['name'][:26]} "
                    f"({worst['delta']:+,.0f}) · tăng nhất: {best['name'][:26]} ({best['delta']:+,.0f})")
        log(f"   → {path}")
        summary.append((key, len(recs), cov_cur, usable_total))

    log(f"\nXONG {args.period}: " + " · ".join(f"{k} {n:,} URL (phủ {c}%){'' if u else ' ⛔'}" for k, n, c, u in summary))


if __name__ == "__main__":
    main()
