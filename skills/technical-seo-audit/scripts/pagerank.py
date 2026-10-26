#!/usr/bin/env python3
"""PageRank nội bộ từ export Screaming Frog (technical-seo-audit, Path B).

SF chạy headless không chạy Crawl Analysis, nên cột Link Score trống. Script này tính lại từ 2 file export:
  internal_all.csv   (--export-tabs "Internal:All")
  all_inlinks.csv    (--bulk-export "Links:All Inlinks")

Dùng:
  pagerank.py --internal internal_all.csv --inlinks all_inlinks.csv --out pagerank_internal.tsv
              [--damping 0.85] [--iters 40]

Nút: trang HTML, mã 200, Indexability = Indexable. Cạnh: link Hyperlink, follow, nguồn và đích đều là nút,
bỏ mảnh #, bỏ link tự trỏ. Trang không có link ra chia đều điểm cho mọi nút.
Output TSV: hang, url, pr_x1000, so_trang_nguon, content, navigation, header, footer, khac.
Script in số nút và số cạnh. Báo cáo ghi bộ lọc nút và số nút cạnh hạng PageRank.
Exit 1 khi không có nút (sai file hoặc sai cột). Python stdlib. Chỉ đọc file export.
"""
import argparse
import collections
import csv
import sys

POSITIONS = ("Content", "Navigation", "Header", "Footer")


def read_rows(path, need):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        miss = [c for c in need if c not in (rd.fieldnames or [])]
        if miss:
            sys.exit(f"LỖI: {path} thiếu cột {', '.join(miss)}. Kiểm tên export của SF.")
        yield from rd


def load_pages(path):
    pages = set()
    for r in read_rows(path, ("Address", "Content Type", "Status Code", "Indexability")):
        if (r["Content Type"].lower().startswith("text/html") and r["Status Code"].strip() == "200"
                and r["Indexability"].strip() == "Indexable"):
            pages.add(r["Address"].split("#")[0])
    return pages


def load_graph(path, pages):
    out = collections.defaultdict(set)
    sources = collections.defaultdict(set)
    pos = collections.defaultdict(collections.Counter)
    for r in read_rows(path, ("Type", "Source", "Destination", "Follow")):
        s, t = r["Source"].split("#")[0], r["Destination"].split("#")[0]
        if r["Type"] != "Hyperlink" or r["Follow"].strip().lower() != "true":
            continue
        if s not in pages or t not in pages or s == t:
            continue
        out[s].add(t)
        sources[t].add(s)
        p = r.get("Link Position", "")
        pos[t][p if p in POSITIONS else "khac"] += 1
    return out, sources, pos


def pagerank(pages, out, damping=0.85, iters=40):
    n = len(pages)
    pr = {p: 1 / n for p in pages}
    for _ in range(iters):
        dangling = sum(pr[p] for p in pages if not out[p])
        nxt = {p: (1 - damping) / n + damping * dangling / n for p in pages}
        for s in pages:
            if out[s]:
                share = damping * pr[s] / len(out[s])
                for t in out[s]:
                    nxt[t] += share
        pr = nxt
    return pr


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--internal", required=True)
    ap.add_argument("--inlinks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--damping", type=float, default=0.85)
    ap.add_argument("--iters", type=int, default=40)
    a = ap.parse_args(argv)

    pages = load_pages(a.internal)
    if not pages:
        sys.exit("LỖI: 0 trang HTML 200 Indexable. Kiểm file Internal:All.")
    out, sources, pos = load_graph(a.inlinks, pages)
    pr = pagerank(pages, out, a.damping, a.iters)
    rows = sorted(pages, key=lambda p: (-pr[p], p))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("hang\turl\tpr_x1000\tso_trang_nguon\tcontent\tnavigation\theader\tfooter\tkhac\n")
        for i, p in enumerate(rows, 1):
            c = pos[p]
            f.write(f"{i}\t{p}\t{pr[p] * 1000:.3f}\t{len(sources[p])}\t{c['Content']}\t{c['Navigation']}"
                    f"\t{c['Header']}\t{c['Footer']}\t{c['khac']}\n")
    edges = sum(len(v) for v in out.values())
    print(f"{len(pages)} trang (HTML 200 Indexable), {edges} cạnh follow giữa các trang đó -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
