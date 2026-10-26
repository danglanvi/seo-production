#!/usr/bin/env python3
"""gsc_route: chuẩn bị query GSC cho `retrieval-lab route` và đọc kết quả định tuyến query → URL. Chỉ chạy local.

Lệnh:
  prep     --gsc <query×page: JSON GSC API {rows:[{keys:[query,page],...}]} | TSV có cột query, page, clicks, impressions, position>
           [--keywords kw.txt] [--groups hang.tsv --group-col template [--chosen-col url]] [--base https://domain]
           [--candidates urls.txt] [--min-impr 20]
           [--keep-missing] --out queries.jsonl
           Bỏ dòng jump link "#", gộp query theo NFC + casefold, URL Google chọn = trang có nhiều hiển thị nhất.
           Mỗi dòng: {id, text, chosen, impr, clicks, pos, share, n_urls, group?, candidates?}.
  summary  --routing routing.jsonl --out <tiền tố> [--share-split 0.6]
           Ghi <tiền tố>.tsv (mỗi query một verdict) và <tiền tố>_group.json (tổng theo group).

Dữ liệu GSC không rời máy: không gửi file nào ở đây vào Jev hay API ngoài.
Cổng share 0,6 lấy từ skill retrieval-lab (Quy trình bước 2). Không đặt ngưỡng cosine mới ở đây.
"""
import argparse
import collections
import csv
import json
import sys
import unicodedata
from pathlib import Path


def qkey(s):
    return unicodedata.normalize("NFC", (s or "").strip()).casefold()


def read_gsc(path):
    p = Path(path)
    if p.suffix == ".json":
        d = json.loads(p.read_text(encoding="utf-8"))
        for r in d.get("rows", []):
            yield r["keys"][0], r["keys"][1], float(r.get("clicks", 0)), float(r["impressions"]), float(r["position"])
        return
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        yield r["query"], r["page"], float(r.get("clicks") or 0), float(r["impressions"]), float(r["position"])


def read_list(path):
    return [l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def cmd_prep(a):
    agg = {}
    for q, page, clicks, impr, pos in read_gsc(a.gsc):
        if "#" in page:  # jump link (#ftoc-…) lặp hiển thị của URL gốc
            continue
        if a.base and page.startswith("/"):
            page = a.base.rstrip("/") + page
        k = qkey(q)
        x = agg.setdefault(k, {"impr": 0.0, "clicks": 0.0, "pw": 0.0, "pages": collections.Counter()})
        x["impr"] += impr
        x["clicks"] += clicks
        x["pw"] += pos * impr
        x["pages"][page] += impr
    groups, fixed = {}, {}
    if a.groups:
        for r in csv.DictReader(open(a.groups, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
            groups[qkey(r["keyword"])] = r[a.group_col]
            if a.chosen_col and r.get(a.chosen_col):
                fixed[qkey(r["keyword"])] = r[a.chosen_col]
    want = [qkey(k) for k in read_list(a.keywords)] if a.keywords else None
    keys = list(dict.fromkeys(want)) if want is not None else sorted(agg, key=lambda k: -agg[k]["impr"])
    cands = read_list(a.candidates) if a.candidates else None
    out, missing = [], []
    for k in keys:
        x = agg.get(k)
        if k in fixed:  # URL Google chọn lấy từ file hạng (SpySERP); GSC chỉ cấp share khi có
            ok = x is not None and x["impr"] >= a.min_impr
            row = {"text": k, "chosen": fixed[k], "impr": int(x["impr"]) if x else 0,
                   "share": round(x["pages"].get(fixed[k], 0) / x["impr"], 3) if ok else None,
                   "nguon_chosen": a.chosen_col}
        elif x is None or x["impr"] < a.min_impr:
            missing.append(k)
            if a.keep_missing:
                row = {"text": k, "chosen": None, "impr": int(x["impr"]) if x else 0, "khong_du_gsc": True}
            else:
                continue
        else:
            chosen, ci = x["pages"].most_common(1)[0]
            row = {"text": k, "chosen": chosen, "impr": int(x["impr"]), "clicks": int(x["clicks"]),
                   "pos": round(x["pw"] / x["impr"], 2), "share": round(ci / x["impr"], 3), "n_urls": len(x["pages"])}
        if k in groups:
            row["group"] = groups[k]
        if cands:
            row["candidates"] = cands
        out.append(row)
    for i, r in enumerate(out):
        r["id"] = f"q{i}"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps({"id": r.pop("id"), **r}, ensure_ascii=False) + "\n" for r in out),
                           encoding="utf-8")
    print(json.dumps({"query": len(out), "co_gsc": sum(1 for r in out if r.get("chosen")),
                      "thieu_hoac_duoi_min_impr": len(missing)}, ensure_ascii=False))


def verdict(r, split):
    if not r.get("chosen"):
        return "chưa có dữ liệu GSC: đọc gemma_top trước khi gán URL"
    if r.get("chosen_rank") is None:
        return "URL Google chọn không có trong store"
    if r["agree_top1"]:
        return "khớp"
    if r.get("share") is None:
        return "Gemma chọn URL khác, chưa có share GSC: đọc 2 trang"
    if r["share"] < split:
        return "Google chia query: ứng viên cannibalization"
    return "Google chọn URL khác: kiểm link nội bộ và anchor"


def cmd_summary(a):
    rows = [json.loads(l) for l in Path(a.routing).read_text(encoding="utf-8").splitlines() if l.strip()]
    tsv = Path(str(a.out) + ".tsv")
    cols = ["id", "text", "group", "impr", "share", "chosen", "gemma_top", "chosen_rank", "margin", "verdict"]
    by = collections.defaultdict(lambda: {"n": 0, "impr": 0, "impr_khop": 0, "verdict": collections.Counter()})
    with open(tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(cols)
        for r in rows:
            v = verdict(r, a.share_split)
            w.writerow([r.get("id"), r.get("text"), r.get("group") or "", r.get("impr") or 0, r.get("share"),
                        r.get("chosen") or "", r.get("gemma_top"), r.get("chosen_rank"), r.get("margin"), v])
            g = by[r.get("group") or "-"]
            g["n"] += 1
            g["impr"] += r.get("impr") or 0
            g["impr_khop"] += (r.get("impr") or 0) if r.get("agree_top1") else 0
            g["verdict"][v.split(":")[0]] += 1
    summ = {g: {"n": x["n"], "impr": x["impr"], "ty_le_impr_khop": round(x["impr_khop"] / x["impr"], 3) if x["impr"] else None,
                "verdict": dict(x["verdict"])} for g, x in sorted(by.items())}
    have = [r for r in rows if r.get("chosen_rank")]
    total = {"query": len(rows), "co_url_google": len(have),
             "top1_khop": sum(r["agree_top1"] for r in have), "top3_khop": sum(r["chosen_rank"] <= 3 for r in have)}
    Path(str(a.out) + "_group.json").write_text(json.dumps({"tong": total, "group": summ}, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    print(json.dumps(total, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep")
    p.add_argument("--gsc", required=True)
    p.add_argument("--keywords")
    p.add_argument("--groups", help="TSV có cột keyword và cột nhóm, ví dụ hang.tsv của qp_ranks.py")
    p.add_argument("--group-col", default="group", help="tên cột nhóm, ví dụ template")
    p.add_argument("--chosen-col", help="lấy URL Google chọn từ cột này của --groups, ví dụ url của hang.tsv")
    p.add_argument("--base", help="thêm domain cho page dạng /path")
    p.add_argument("--candidates", help="file URL, mỗi dòng một URL: giới hạn tập trang khi route")
    p.add_argument("--min-impr", type=float, default=20)
    p.add_argument("--keep-missing", action="store_true", help="giữ keyword thiếu GSC, chosen = null")
    p.add_argument("--out", required=True)
    s = sub.add_parser("summary")
    s.add_argument("--routing", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--share-split", type=float, default=0.6)
    a = ap.parse_args()
    {"prep": cmd_prep, "summary": cmd_summary}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
