#!/usr/bin/env python3
"""Lấy danh sách bản lưu Wayback (CDX) cho URL chết, ghi wb.json cho pick_target.py --wayback.
Script chỉ gọi web.archive.org để đọc. Không gọi site, không ghi site.

Chạy: python3 wayback_cdx.py --in ra.tsv --host <domain> --out wb.json [--cache <thư mục>] [--offline] [--ma 410_de_xuat,hoi] [--nghi 1.5]

Vào:
  --in       TSV có cột url. Có cột ma (output của pick_target.py) thì chỉ lấy dòng có ma nằm trong --ma.
  --host     domain của site, ví dụ mau.vn. Script ghép host với đường dẫn để hỏi CDX.
  --cache    thư mục giữ từng phản hồi CDX. Lượt sau đọc cache, không hỏi lại.
  --offline  chỉ đọc cache, không gọi mạng. URL chưa có cache bị bỏ qua và báo ở stderr.
  --ma       mã cần tra, mặc định 410_de_xuat,hoi.
  --nghi     số giây nghỉ giữa 2 lần gọi CDX, mặc định 1,5.
Ra: JSON {đường dẫn: [["timestamp","statuscode"], ...]}, đúng dạng pick_target.py --wayback.
Mã thoát: 0 xong · 1 có URL lỗi mạng (vẫn ghi phần đã lấy) · 2 input sai.
"""
import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from urlpath import norm  # noqa: E402

CDX = "https://web.archive.org/cdx/search/cdx?url={}&output=json&fl=timestamp,statuscode&collapse=digest&limit=50"


def cache_file(cache, path):
    return Path(cache) / (urllib.parse.quote(norm(path), safe="") + ".json")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--host", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--ma", default="410_de_xuat,hoi")
    ap.add_argument("--nghi", type=float, default=1.5)
    a = ap.parse_args()
    if not Path(a.inp).is_file():
        print(f"lỗi: không có file --in {a.inp}", file=sys.stderr)
        return 2
    if a.offline and not a.cache:
        print("lỗi: --offline cần --cache", file=sys.stderr)
        return 2
    with open(a.inp, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if rows and "url" not in rows[0]:
        print("lỗi: TSV thiếu cột url", file=sys.stderr)
        return 2
    want = set(a.ma.split(","))
    paths = []
    for r in rows:
        u = (r.get("url") or "").strip()
        if u and ("ma" not in r or r["ma"] in want):
            p = urllib.parse.urlsplit(u).path or "/"
            if p not in paths:
                paths.append(p)
    if a.cache:
        Path(a.cache).mkdir(parents=True, exist_ok=True)
    out, loi, called = {}, 0, False
    for p in paths:
        cf = cache_file(a.cache, p) if a.cache else None
        if cf and cf.is_file():
            out[p] = json.loads(cf.read_text(encoding="utf-8") or "[]")
            continue
        if a.offline:
            print(f"bỏ qua (chưa có cache): {p}", file=sys.stderr)
            continue
        if called:
            time.sleep(a.nghi)
        called = True
        url = CDX.format(urllib.parse.quote(a.host.strip("/") + p, safe=""))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "content-inventory-audit/1.1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8").strip()
            data = json.loads(body) if body else []
        except (OSError, ValueError) as e:
            print(f"lỗi mạng {p}: {e}", file=sys.stderr)
            loi += 1
            continue
        out[p] = data
        if cf:
            cf.write_text(json.dumps(data), encoding="utf-8")
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    co_200 = sum(any(len(x) > 1 and str(x[1]) == "200" for x in v[1:]) for v in out.values())
    print(json.dumps({"url": len(paths), "co_du_lieu": len(out), "co_ban_200": co_200, "loi_mang": loi}, ensure_ascii=False))
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
