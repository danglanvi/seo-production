#!/usr/bin/env python3
"""Cặp trang ăn thịt từ khoá ở nhánh GSC: so query bằng code local, Jev chỉ nhận chữ công khai của trang.

Lệnh:
  overlap --gsc <bảng page × query đã làm sạch> [--pairs pairs.tsv] [--min-shared 3] --out overlap.tsv
      Tính local cho từng cặp: số query chung, lượt hiển thị chung, phần lượt hiển thị của mỗi trang nằm ở query chung,
      số query mỗi trang thắng (vị trí tốt hơn). Không có --pairs: lấy mọi cặp có từ --min-shared query chung.
      File ra có query GSC: chỉ giữ local, không gửi Jev hay API ngoài.
  jev-in --pages pages.jsonl --pairs pairs.tsv --site <tên miền> --out jev_in.jsonl
      Dựng input cho rubric gsc-cannibal-pair ở chế độ chữ: mỗi trang chỉ có url, title, h1, đoạn mở đầu;
      shared_queries luôn rỗng. pages.jsonl: một dòng mỗi trang {url, title, h1, opening} lấy từ HTML công khai.
  check --in jev_in.jsonl
      Chặn trước khi gọi Jev: báo lỗi và thoát mã 1 nếu input còn trường GSC (query, clicks, impressions, position, ctr)
      hoặc shared_queries không rỗng.

Python stdlib. Chỉ đọc và ghi file local.
"""
import argparse
import collections
import csv
import itertools
import json
import sys
from pathlib import Path

GSC_KEYS = {"query", "queries", "top_queries", "shared_queries", "clicks", "impressions", "impr", "position", "pos", "ctr"}
PAGE_KEYS = ("url", "title", "h1", "opening")


def read_gsc(path, page_col="page", query_col="query"):
    delim = "\t" if str(path).endswith((".tsv", ".txt")) else ","
    by_page = collections.defaultdict(dict)
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh, delimiter=delim, quoting=csv.QUOTE_NONE if delim == "\t" else csv.QUOTE_MINIMAL)
        for r in rd:
            page = (r.get(page_col) or "").split("#")[0]
            q = (r.get(query_col) or "").strip()
            if not page or not q:
                continue
            cur = by_page[page].get(q)
            impr, clicks, pos = float(r.get("impressions") or 0), float(r.get("clicks") or 0), float(r.get("position") or 0)
            if cur:  # dòng trùng sau khi bỏ mảnh #: cộng lượt, giữ vị trí tốt hơn
                cur["impr"] += impr
                cur["clicks"] += clicks
                cur["pos"] = min(cur["pos"], pos) if pos else cur["pos"]
            else:
                by_page[page][q] = {"impr": impr, "clicks": clicks, "pos": pos}
    return by_page


def norm(u, site=""):
    u = u.strip()
    if site and u.startswith(("http://", "https://")):
        rest = u.split("://", 1)[1]
        host, _, path = rest.partition("/")
        if host.removeprefix("www.") == site:
            return "/" + path
    return u


def read_pairs(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith(("url_a", "#")):
            continue
        parts = line.split("\t")[0].split(" | ") if " | " in line.split("\t")[0] else line.split("\t")[:2]
        out.append((parts[0].strip(), parts[1].strip()))
    return out


def pair_stats(a, b, by_page):
    qa, qb = by_page.get(a, {}), by_page.get(b, {})
    shared = set(qa) & set(qb)
    tot_a, tot_b = sum(v["impr"] for v in qa.values()), sum(v["impr"] for v in qb.values())
    sh_a, sh_b = sum(qa[q]["impr"] for q in shared), sum(qb[q]["impr"] for q in shared)
    win_a = sum(1 for q in shared if qa[q]["pos"] and (not qb[q]["pos"] or qa[q]["pos"] < qb[q]["pos"]))
    win_b = sum(1 for q in shared if qb[q]["pos"] and (not qa[q]["pos"] or qb[q]["pos"] < qa[q]["pos"]))
    top = sorted(shared, key=lambda q: -(qa[q]["impr"] + qb[q]["impr"]))[:5]
    return {"url_a": a, "url_b": b, "shared_queries": len(shared), "shared_impr": round(sh_a + sh_b),
            "share_a": round(sh_a / tot_a, 3) if tot_a else 0, "share_b": round(sh_b / tot_b, 3) if tot_b else 0,
            "wins_a": win_a, "wins_b": win_b, "top_shared_local_only": " ; ".join(top)}


def cmd_overlap(a):
    by_page = read_gsc(a.gsc)
    site = a.site.removeprefix("www.") if a.site else ""
    if a.pairs:
        pairs = [(norm(x, site), norm(y, site)) for x, y in read_pairs(a.pairs)]
    else:
        idx = collections.defaultdict(set)
        for p, qs in by_page.items():
            for q in qs:
                idx[q].add(p)
        cnt = collections.Counter()
        for ps in idx.values():
            if len(ps) <= 30:  # query chung cho rất nhiều trang (tên brand) không tạo cặp
                cnt.update(itertools.combinations(sorted(ps), 2))
        pairs = [pq for pq, n in cnt.items() if n >= a.min_shared]
    rows = sorted((pair_stats(x, y, by_page) for x, y in pairs), key=lambda r: -r["shared_impr"])
    cols = ["url_a", "url_b", "shared_queries", "shared_impr", "share_a", "share_b", "wins_a", "wins_b", "top_shared_local_only"]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        fh.writelines("\t".join(str(r[c]) for c in cols) + "\n" for r in rows)
    print(f"{len(rows)} cặp -> {a.out} (file có query GSC: chỉ giữ local)", file=sys.stderr)


def cmd_jev_in(a):
    pages = {}
    for line in Path(a.pages).read_text(encoding="utf-8").splitlines():
        if line.strip():
            p = json.loads(line)
            pages[p["url"]] = {"url": p["url"], "title": p.get("title") or "", "h1": p.get("h1") or "",
                               "opening": p.get("opening") or p.get("excerpt") or ""}
    out, miss = [], []
    for x, y in read_pairs(a.pairs):
        pa, pb = pages.get(x), pages.get(y)
        if not pa or not pb:
            miss.append(f"{x} | {y}")
            continue
        out.append({"id": f"{x} | {y}", "state": {"site": a.site, "page_a": pa, "page_b": pb, "shared_queries": []}})
    bad = problems(out)
    if bad:
        sys.exit("input còn dữ liệu GSC: " + "; ".join(bad[:5]))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(f"{len(out)} cặp -> {a.out}; thiếu chữ trang: {len(miss)}", file=sys.stderr)


def problems(rows):
    """Trường GSC trong input Jev. shared_queries chỉ được có và phải rỗng."""
    bad = []

    def walk(o, path, rid):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "shared_queries":
                    if v:
                        bad.append(f"{rid}: {path}{k} không rỗng")
                elif k.lower() in GSC_KEYS:
                    bad.append(f"{rid}: có trường {path}{k}")
                else:
                    walk(v, f"{path}{k}.", rid)
        elif isinstance(o, list):
            for v in o:
                walk(v, path, rid)

    for r in rows:
        walk(r.get("state", {}), "", r.get("id", "?"))
    return bad


def cmd_check(a):
    rows = [json.loads(l) for l in Path(a.inp).read_text(encoding="utf-8").splitlines() if l.strip()]
    bad = problems(rows)
    if bad:
        print("\n".join(bad[:20]), file=sys.stderr)
        sys.exit(f"{len(bad)} chỗ còn dữ liệu GSC. Không gọi Jev.")
    print(f"{len(rows)} dòng: chỉ có chữ công khai, gọi Jev được", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("overlap")
    o.add_argument("--gsc", required=True)
    o.add_argument("--pairs")
    o.add_argument("--site", default="")
    o.add_argument("--min-shared", type=int, default=3)
    o.add_argument("--out", required=True)
    j = sub.add_parser("jev-in")
    j.add_argument("--pages", required=True)
    j.add_argument("--pairs", required=True)
    j.add_argument("--site", required=True)
    j.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("--in", dest="inp", required=True)
    a = ap.parse_args()
    {"overlap": cmd_overlap, "jev-in": cmd_jev_in, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
