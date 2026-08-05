#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
url_yoy_forensics.py — Truy nguyên các URL từng có PV lớn ở kỳ so sánh nhưng sụt
sâu ở kỳ này. Chạy trên BẤT KỲ nhóm trang nào khai trong `periods.<kỳ>.sources`
qua tham số `--source` (job listing · category/PLP · product detail/PDP · blog…).

Vì sao cần: khi một nhóm URL mất phần lớn PV so cùng kỳ, mức mất thường bất thường tới độ
nghi đổi cấu trúc URL / index chuyển sang URL khác / mất hiển thị, chứ không phải "SEO kém
đi" (bài học CareerViet Q1/2026, note III.2 ngày 03/08). Site thương mại điện tử có vòng
đời sản phẩm ngắn còn dính nặng hơn: PDP hết hàng, đổi slug, ngừng kinh doanh. Đoán bừa
nguyên nhân trên slide gửi khách là điều tệ nhất có thể làm, nên script chỉ PHÂN LOẠI ỨNG
VIÊN kèm bằng chứng, còn kết luận cuối để team điền tay — cột «Nhận định team» cố tình để
trống.

Bốn nhóm nghi vấn, xếp theo thứ tự loại trừ:
  A. ĐỔI SLUG    — có URL khác cùng "vân tay" từ khoá tăng gần đúng phần đã mất
  B. BIẾN MẤT    — kỳ này không còn dòng nào, PV = 0 tuyệt đối
  C. CÒN SỐNG NHƯNG SỤT SÂU — vẫn có PV, mất > ngưỡng %
  D. ĐỔI THAM SỐ — cùng path gốc, khác query/facet

`--check-live` gọi HEAD từng URL (có nghỉ giữa các lần) để phân biệt 200 / 301 / 404 —
tuỳ chọn, vì đây là site của khách, không nện request vào đó khi chưa cần.

Cách chạy:
  python3 url_yoy_forensics.py --config <report-config.yaml> --period 2026-Q1
  python3 url_yoy_forensics.py --config ... --period 2026-Q1 --check-live --top 40
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402

UA = "Mozilla/5.0 (compatible; GTV-SEO-audit/1.0; +https://gtvseo.com/)"


def log(m):
    print(m, flush=True)


def slug_tokens(url):
    """Vân tay từ khoá của URL: bỏ đuôi -vi.html, bỏ mã facet (l8, k, cr92, t1000…),
    giữ phần chữ có nghĩa — đủ để nhận ra 2 URL cùng nói về một chủ đề."""
    path = urllib.parse.urlparse(url).path or url
    path = re.sub(r"\.(html?|php|aspx)$", "", path.lower())
    path = re.sub(r"-(vi|en)$", "", path)
    parts = re.split(r"[/\-_]+", path)
    out = set()
    for p in parts:
        if not p or p.isdigit():
            continue
        if re.fullmatch(r"[a-z]{1,3}\d+", p):        # mã facet: l8, k12, cr92, t1000
            continue
        if p in ("viec-lam", "viec", "lam", "vi", "en", "html", "tim"):
            continue
        if len(p) > 2:
            out.add(p)
    return out


def base_path(url):
    p = urllib.parse.urlparse(url).path or url
    return re.sub(r"[?#].*$", "", p)


def auto_generated(url):
    """Nhận diện URL SINH TỰ ĐỘNG — phải tách khỏi URL danh mục thật.

    Trên careerviet.vn có 2 họ URL tự sinh từng được index rất nhiều ở kỳ trước:
      · «/viec-lam/<từ khoá có dấu>-k-vi.html» — trang kết quả tìm kiếm theo từ khoá
      · «/viec-lam-tuong-tu/…»                — trang việc làm tương tự
    Mất PV ở 2 họ này KHÔNG cùng bản chất với mất PV ở trang danh mục lõi: nó thường là
    hệ quả của việc chủ động dọn URL rác. Gộp chung vào một bảng rồi kết luận "rớt hạng"
    là đọc sai hoàn toàn kết quả quý."""
    path = base_path(url)
    if "/viec-lam-tuong-tu/" in path:
        return "trang «việc làm tương tự» tự sinh"
    if re.search(r"-k-(vi|en)\.html?$", path):
        return "trang kết quả tìm kiếm theo từ khoá (đuôi -k-)"
    if re.search(r"[^\x00-\x7F]", path):
        return "URL chứa dấu tiếng Việt (dạng tự sinh, không phải slug chuẩn hoá)"
    return None


def head_status(url, domain, timeout=12):
    if not url.startswith("http"):
        url = f"https://{domain}{url if url.startswith('/') else '/' + url}"
    # Nhiều URL Job Listing có dấu tiếng Việt trong path (/viec-lam/Nhân-viên-SEO-k-vi.html).
    # Không percent-encode thì urllib ném lỗi encode và mọi URL loại này về None — đúng
    # nhóm URL đang cần soi nhất lại là nhóm không kiểm được.
    sp = urllib.parse.urlsplit(url)
    url = urllib.parse.urlunsplit((
        sp.scheme, sp.netloc,
        urllib.parse.quote(sp.path, safe="/%"),
        urllib.parse.quote(sp.query, safe="=&%"), ""))
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.url if r.url != url else None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")
    except Exception as e:
        return None, f"lỗi: {type(e).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", default="2026-Q1")
    ap.add_argument("--source", default="jl")
    ap.add_argument("--min-prev", type=float, default=3000, help="PV kỳ so sánh tối thiểu để xét")
    ap.add_argument("--drop-pct", type=float, default=50.0, help="Ngưỡng % mất PV để coi là bất thường")
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--check-live", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.7)
    ap.add_argument("--csv", default=None, help="Xuất CSV cho team điền cột «Nhận định team»")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg_dir = os.path.dirname(os.path.abspath(args.config))
    p = (cfg.get("periods") or {}).get(args.period) or sys.exit(f"LỖI: kỳ {args.period!r} không có")
    bucket = "monthly" if p.get("mode") == "month" else "quarterly"
    d = os.path.join(os.path.dirname(cfg_dir), "02-raw", "seo-data", bucket, args.period)
    a_path = os.path.join(d, f"analysis_{args.source}.json")
    if not os.path.isfile(a_path):
        sys.exit(f"LỖI: thiếu {a_path} — chạy period_analyze.py trước")

    # analysis_*.json chỉ giữ top mover; cần TOÀN BỘ bản ghi để dò URL thay thế →
    # đọc lại từ CSV thô nếu có, không thì cảnh báo là chỉ dò trong phạm vi top.
    recs, full = [], False
    csv_path = os.path.join(d, "csv", f"{args.source}.csv")
    a = json.load(open(a_path, encoding="utf-8"))
    if os.path.isfile(csv_path):
        spec = p["sources"][args.source]
        ci = lambda L: sum((ord(c) - 64) * 26 ** i for i, c in enumerate(reversed(L.upper()))) - 1  # noqa: E731
        iu, ic, ip = ci(spec["url_col"]), ci(spec["cur_col"]), ci(spec["prev_col"])
        dims = {k: ci(v) for k, v in (spec.get("dims") or {}).items()}
        csv.field_size_limit(10 ** 7)
        with open(csv_path, encoding="utf-8") as f:
            for row in list(csv.reader(f))[spec["header_row"]:]:
                if len(row) <= max(iu, ic, ip):
                    continue
                u = str(row[iu]).strip()
                if not u or not ("/" in u or u.startswith("http")):
                    continue
                num = lambda s: float(str(s).replace(",", "") or 0) if re.fullmatch(  # noqa: E731
                    r"-?[\d,]+(\.\d+)?", str(s).strip() or "x") else 0.0
                r = {"url": u, "cur": num(row[ic]), "prev": num(row[ip])}
                for k, j in dims.items():
                    r[k] = str(row[j]).strip() if j < len(row) else ""
                recs.append(r)
        full = True
    else:
        recs = a["losers"] + a["gainers"]
        log(f"⚠ không thấy {csv_path} — chỉ dò trong phạm vi top mover, "
            f"chạy period_analyze.py --save-csv để dò đầy đủ")

    log(f"Nguồn: {a['source'].get('tab')} · {len(recs):,} bản ghi "
        f"({'toàn bộ' if full else 'chỉ top mover'})")

    gainers = [r for r in recs if r["cur"] - r["prev"] > 0]
    gain_idx = defaultdict(list)
    for g in gainers:
        for t in slug_tokens(g["url"]):
            gain_idx[t].append(g)
    by_base = defaultdict(list)
    for r in recs:
        by_base[base_path(r["url"])].append(r)

    suspects = [r for r in recs
                if r["prev"] >= args.min_prev
                and r["prev"] > 0
                and (r["prev"] - r["cur"]) / r["prev"] * 100 >= args.drop_pct]
    suspects.sort(key=lambda r: r["cur"] - r["prev"])
    log(f"Ứng viên: {len(suspects):,} URL có PV kỳ so sánh ≥ {args.min_prev:,.0f} "
        f"và mất ≥ {args.drop_pct}%")

    out = []
    for r in suspects[: args.top]:
        lost = r["prev"] - r["cur"]
        toks = slug_tokens(r["url"])
        cand, best = None, 0.0
        seen = set()
        for t in toks:
            for g in gain_idx.get(t, []):
                if g["url"] == r["url"] or g["url"] in seen:
                    continue
                seen.add(g["url"])
                gt = slug_tokens(g["url"])
                sim = len(toks & gt) / len(toks | gt) if (toks | gt) else 0
                gained = g["cur"] - g["prev"]
                # ứng viên thay thế phải vừa giống tên vừa nhận được lượng PV đáng kể
                score = sim * min(1.0, gained / lost) if lost else 0
                if score > best:
                    cand, best = g, score

        siblings = [x for x in by_base.get(base_path(r["url"]), []) if x["url"] != r["url"]]
        auto_gen = auto_generated(r["url"])
        if auto_gen:
            nhom, ly_do = "E. URL sinh tự động", (
                f"{auto_gen} — nhóm URL tự sinh, năm ngoái được index rất nhiều. Mất PV ở đây "
                f"nhiều khả năng là KẾT QUẢ CỦA VIỆC DỌN FILTER/URL RÁC (công đoạn technical "
                f"đã làm trong quý), không phải mất traffic có giá trị. Team xác nhận trước "
                f"khi kết luận.")
        elif cand and best >= 0.20:
            nhom, ly_do = "A. Đổi slug (nghi)", (
                f"«{cand['url'][:70]}» giống tên {best:.0%} và tăng "
                f"{cand['cur'] - cand['prev']:+,.0f} PV — cần soi có phải URL thay thế không")
        elif r["cur"] == 0:
            nhom, ly_do = "B. Biến mất", "kỳ này PV = 0 tuyệt đối — kiểm URL còn sống / còn index không"
        elif siblings:
            nhom, ly_do = "D. Đổi tham số/facet", (
                f"cùng path gốc còn {len(siblings)} biến thể khác — nghi tách/gộp facet")
        else:
            nhom, ly_do = "C. Còn sống, sụt sâu", (
                f"vẫn còn {r['cur']:,.0f} PV nhưng mất {lost / r['prev'] * 100:.0f}% — "
                f"nghi mất hiển thị / rớt hạng")

        item = {
            "url": r["url"], "pv_ky_so_sanh": r["prev"], "pv_ky_nay": r["cur"],
            "mat_pv": -lost, "mat_pct": round(-lost / r["prev"] * 100, 1),
            "nhom_nghi_van": nhom, "bang_chung": ly_do,
            "url_thay_the_nghi": cand["url"] if cand and best >= 0.20 else None,
            "nhan_dinh_team": "",          # ← để TRỐNG, team điền sau khi soi tay
        }
        for k in ("intent", "nganh", "location"):
            if r.get(k):
                item[k] = r[k]
        out.append(item)

    if args.check_live:
        log(f"Kiểm trạng thái HTTP {len(out)} URL (nghỉ {args.sleep}s giữa các lần)…")
        for i, it in enumerate(out, 1):
            st, loc = head_status(it["url"], cfg.get("domain", ""))
            it["http_status"] = st
            it["redirect_to"] = loc
            if st in (301, 302, 308) and loc:
                it["nhom_nghi_van"] = "A. Đổi slug (đã xác nhận redirect)"
                it["bang_chung"] = f"HTTP {st} → {str(loc)[:80]}"
            elif st in (404, 410):
                it["nhom_nghi_van"] = "B. Biến mất (đã xác nhận)"
                it["bang_chung"] = f"HTTP {st} — URL không còn tồn tại"
            if i % 10 == 0:
                log(f"   {i}/{len(out)}")
            time.sleep(args.sleep)

    groups = defaultdict(list)
    for it in out:
        groups[it["nhom_nghi_van"]].append(it)
    log("\nPhân loại:")
    for g, items in sorted(groups.items()):
        log(f"  {g:<38} {len(items):>3} URL · mất {sum(i['mat_pv'] for i in items):>12,.0f} PV")

    res = {"period": args.period, "source": a["source"], "period_label": a.get("period_label"),
           "compare_label": a.get("compare_label"),
           "rule": f"PV kỳ so sánh ≥ {args.min_prev:,.0f} và mất ≥ {args.drop_pct}%",
           "quet_toan_bo": full, "ung_vien": len(suspects), "items": out,
           "luu_y": ("Cột «nhan_dinh_team» để TRỐNG có chủ đích — máy chỉ khoanh vùng nghi vấn "
                     "kèm bằng chứng, kết luận nguyên nhân phải do người soi tay xác nhận trước "
                     "khi lên slide gửi khách.")}
    out_p = os.path.join(d, f"forensics_{args.source}_{args.period}.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    log(f"\n→ {out_p}")

    csv_out = args.csv or os.path.join(d, f"forensics_{args.source}_{args.period}.csv")
    cols = ["url", "pv_ky_so_sanh", "pv_ky_nay", "mat_pv", "mat_pct", "intent", "nganh",
            "location", "nhom_nghi_van", "bang_chung", "url_thay_the_nghi",
            "http_status", "redirect_to", "nhan_dinh_team"]
    with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    log(f"→ {csv_out}   (gửi team điền cột «nhan_dinh_team»)")


if __name__ == "__main__":
    main()
