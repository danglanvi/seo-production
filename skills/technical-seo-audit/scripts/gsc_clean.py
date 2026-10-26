#!/usr/bin/env python3
"""Làm sạch bảng GSC theo trang trước khi đếm (technical-seo-audit, nhánh GSC 90 ngày).

Dùng: gsc_clean.py --in gsc_page_query.tsv --out gsc_clean.tsv [--page-col page] [--impr-col impressions]

- Bỏ dòng URL có mảnh # (jump link mục lục, ví dụ #ftoc-heading-3). GSC ghi các dòng này với lượt hiển thị
  gần bằng URL gốc. Cộng gộp sẽ thổi số của trang lên nhiều lần.
- Báo cờ "cắt": API Search Analytics trả tối đa 25.000 dòng mỗi lần. Bảng đúng 25.000 dòng (hoặc bội số khi
  ghép nhiều trang) là bảng thiếu dòng. Khi đó kéo lại theo từng trang hoặc chia cửa sổ ngày.

Python stdlib. Dữ liệu GSC chỉ xử lý local.
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

API_ROW_LIMIT = 25_000


def read_rows(path):
    delim = "\t" if str(path).endswith((".tsv", ".txt")) else ","
    with open(path, encoding="utf-8-sig", newline="") as fh:
        # TSV: query có dấu nháy kép, đọc bằng QUOTE_NONE để không gộp dòng.
        return list(csv.DictReader(fh, delimiter=delim, quoting=csv.QUOTE_NONE if delim == "\t" else csv.QUOTE_MINIMAL))


def clean(rows, page_col="page", impr_col="impressions"):
    keep, frag = [], []
    for r in rows:
        (frag if "#" in (r.get(page_col) or "") else keep).append(r)

    def impr(rs):
        return sum(float(r.get(impr_col) or 0) for r in rs)

    by_page = collections.Counter((r.get(page_col) or "").split("#")[0] for r in frag)
    n = len(rows)
    report = {
        "rows": n,
        "fragment_rows": len(frag),
        "fragment_row_share": round(len(frag) / n, 3) if n else 0,
        "impressions_clean": round(impr(keep)),
        "impressions_with_fragments": round(impr(rows)),
        "capped": bool(n) and n % API_ROW_LIMIT == 0,
        "top_fragment_pages": by_page.most_common(5),
    }
    return keep, report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--page-col", default="page")
    ap.add_argument("--impr-col", default="impressions")
    a = ap.parse_args()
    rows = read_rows(a.inp)
    if rows and a.page_col not in rows[0]:
        sys.exit(f"không thấy cột {a.page_col}")
    keep, report = clean(rows, a.page_col, a.impr_col)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        if rows:
            if out.suffix in (".tsv", ".txt"):
                cols = list(rows[0])
                fh.write("\t".join(cols) + "\n")
                fh.writelines("\t".join(r.get(c) or "" for c in cols) + "\n" for r in keep)
            else:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(keep)
    print(json.dumps(report, ensure_ascii=False))
    if report["capped"]:
        print(f"CẢNH BÁO: bảng có {report['rows']} dòng, chạm giới hạn {API_ROW_LIMIT} dòng mỗi lần kéo. "
              "Kéo lại theo từng trang hoặc chia cửa sổ ngày.", file=sys.stderr)


if __name__ == "__main__":
    main()
