#!/usr/bin/env python3
"""Chọn đích 301 hoặc 410 cho URL chết. Tra DB trước (mọi post_type, mọi post_status, slug cũ), rồi Wayback, rồi mới đề xuất 410.
Script chỉ đọc file đã xuất. Không gọi site, không gọi Wayback, không ghi site. Mọi kết quả chờ người duyệt.

Chạy: python3 pick_target.py --urls urls.tsv --dump urls.json [--wayback wayback.json] [--terms terms.json] [--out ra.tsv] [--rules-out moi.json] [--strict]

Vào:
  --urls     TSV cột url (bắt buộc), clicks, dich_goi_y, tam_dong, bo. clicks = click GSC trong kỳ. tam_dong=1 khi người duyệt chốt đóng tạm (302).
             bo=1 khi URL nằm trong danh sách bỏ đã duyệt: chỉ khi đó 410_de_xuat thành 410. URL khác không tồn tại giữ 404.
  --rules-out  ghi rule cho dòng 301, 302, 410 dạng chain_check.py --new: {id, from, comparison, to, code}. Rule 410 có to rỗng.
  --dump     kết quả export_urls.php: id, type, status, name, path, pm_uri, old_slugs.
  --wayback  JSON {đường dẫn: dòng CDX}: dòng CDX dạng [["timestamp","statuscode"], ["20210423174117","200"], ...].
  --terms    JSON danh sách đường dẫn chuyên mục, thẻ, archive. Đích gợi ý nằm trong đây bị cờ.
Ra: TSV cột url, ma, dich, nguon, canh_bao, ly_do. Không có --out thì in ra stdout.
ma: giu (URL đang sống) · khoi_phuc (bài còn trong DB, hỏi khôi phục trước khi 301) · 301 · 302 · doc_wayback (Claude đọc bản lưu rồi chọn đích)
    · 410_de_xuat (chưa có bo=1) · 410 (có bo=1) · hoi (thiếu căn cứ) · loi (đích gợi ý sai).
Luật:
  1. Bài còn trong DB ở trạng thái nháp, chờ duyệt, riêng tư, hẹn giờ hoặc thùng rác: khôi phục trước khi 301.
  2. Slug cũ (_wp_old_slug) trỏ về bài publish: 301 về bài đó.
  3. Attachment trùng slug không là đích và không là bằng chứng bài còn tồn tại.
  4. Không có trong DB: có bản lưu Wayback mã 200 thì Claude đọc bản lưu. Không có thì 410 khi không có click, hoặc hỏi khi có click.
  5. Đích gợi ý phải là bài publish. Trang chủ, bài nháp, thùng rác, attachment hoặc đường dẫn không có trong DB là lỗi. Trang chuyên mục là cảnh báo.
Mã thoát: 0 xong · 1 có dòng "loi" khi dùng --strict · 2 input sai.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from urlpath import NHAP, load_dump, load_json, norm  # noqa: E402


def decide(row, dump, wayback, terms):
    path = norm(row["url"])
    slug = path.strip("/").rsplit("/", 1)[-1]
    by_path = [p for p in dump if path in p["keys"]]
    by_slug = [p for p in dump if p["slug_n"].rsplit("/", 1)[-1] == slug]
    by_old = [p for p in dump if slug in {o.rsplit("/", 1)[-1] for o in p["old_n"]}]
    real = lambda ps: [p for p in ps if p.get("type") != "attachment"]  # noqa: E731
    live = [p for p in real(by_path) if p.get("status") == "publish"]
    warn = []
    if by_slug and not real(by_slug):
        warn.append("attachment_trung_slug")
    res = dict(url=row["url"], ma="", dich="", nguon="", canh_bao="", ly_do="")
    sug = (row.get("dich_goi_y") or "").strip()
    if live:
        res.update(ma="giu", nguon="db", ly_do=f"{path} đang trả bài {live[0]['id']} (publish): không redirect")
    elif [p for p in real(by_path + by_slug) if p.get("status") in NHAP or p.get("status") == "trash"]:
        p = [p for p in real(by_path + by_slug) if p.get("status") in NHAP or p.get("status") == "trash"][0]
        res.update(ma="khoi_phuc", nguon="db", ly_do=f"bài {p['id']} ({p.get('type')}) còn trong DB, trạng thái {p['status']}: hỏi người duyệt khôi phục trước khi 301")
    elif [p for p in real(by_old) if p.get("status") == "publish"]:
        p = [p for p in real(by_old) if p.get("status") == "publish"][0]
        res.update(ma="301" if p.get("path") else "hoi", dich=p.get("path") or "", nguon="old_slug", ly_do=f"slug cũ của bài {p['id']}" + ("" if p.get("path") else ", dump thiếu path: người duyệt chọn đích"))
    elif sug:
        res.update(ma="301", dich=sug, nguon="goi_y")
    else:
        cdx = wayback.get(path) or []
        if [r for r in cdx[1:] if len(r) > 1 and str(r[1]) == "200"]:
            res.update(ma="doc_wayback", nguon="wayback", ly_do=f"{len(cdx) - 1} bản lưu, Claude đọc bản lưu rồi chọn đích")
        elif int(row.get("clicks") or 0) > 0:
            res.update(ma="hoi", ly_do=f"không có trong DB và Wayback nhưng có {row['clicks']} click: người duyệt chọn đích")
        elif (row.get("bo") or "").strip() == "1":
            res.update(ma="410", nguon="khong_co", ly_do="không có trong DB, không có bản lưu Wayback mã 200, không có click; nằm trong danh sách bỏ đã duyệt")
        else:
            res.update(ma="410_de_xuat", nguon="khong_co", ly_do="không có trong DB, không có bản lưu Wayback mã 200, không có click")
    if res["ma"] in ("301", "doc_wayback", "hoi") and sug and res["nguon"] != "old_slug":
        res["dich"] = sug
    if res["ma"] == "301":
        d = norm(res["dich"])
        hit = [p for p in dump if d in p["keys"]]
        if d == "/":
            res.update(ma="loi", ly_do="đích là trang chủ")
        elif hit and all(p.get("type") == "attachment" for p in hit):
            res.update(ma="loi", ly_do=f"đích {d} là attachment")
        elif hit and not [p for p in hit if p.get("status") == "publish"]:
            res.update(ma="loi", ly_do=f"đích {d} là bài trạng thái {hit[0]['status']}")
        elif not hit and d in terms:
            res.update(ma="loi", ly_do=f"đích {d} là chuyên mục, thẻ hoặc archive: chỉ 301 về bài cùng chủ đề, không có bài phù hợp thì 410")
        elif not hit and d not in terms:
            res.update(ma="loi", ly_do=f"đích {d} không có trong dump bài và không có trong danh sách chuyên mục")
        if res["ma"] == "301" and norm(row["url"]) == d:
            res.update(ma="loi", ly_do="đích trùng nguồn")
        if res["ma"] == "301" and (row.get("tam_dong") or "").strip() == "1":
            res["ma"] = "302"
            res["ly_do"] = (res["ly_do"] + "; " if res["ly_do"] else "") + "người duyệt chốt đóng tạm: ghi ngày xem lại"
    res["canh_bao"] = ",".join(warn)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--urls", required=True)
    ap.add_argument("--dump", required=True)
    ap.add_argument("--wayback")
    ap.add_argument("--terms")
    ap.add_argument("--out")
    ap.add_argument("--rules-out")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    for k in ("urls", "dump", "wayback", "terms"):
        p = getattr(a, k)
        if p and not Path(p).is_file():
            print(f"lỗi: không có file --{k} {p}", file=sys.stderr)
            return 2
    try:
        dump = load_dump(a.dump)
        wb = {norm(k): v for k, v in load_json(a.wayback).items()} if a.wayback else {}
        terms = {norm(t) for t in load_json(a.terms)} if a.terms else set()
        with open(a.urls, encoding="utf-8-sig") as f:
            rows = [r for r in csv.DictReader(f, delimiter="\t") if (r.get("url") or "").strip()]
        if not rows and Path(a.urls).stat().st_size and "url" not in Path(a.urls).read_text(encoding="utf-8-sig").splitlines()[0]:
            raise ValueError("TSV thiếu cột url")
        res = [decide(r, dump, wb, terms) for r in rows]
    except (ValueError, KeyError, TypeError) as e:
        print(f"lỗi input: {e!r}", file=sys.stderr)
        return 2
    head = ["url", "ma", "dich", "nguon", "canh_bao", "ly_do"]
    text = "\t".join(head) + "\n" + "".join("\t".join(r[h] for h in head) + "\n" for r in res)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"đã ghi {len(res)} dòng vào {a.out}")
    else:
        sys.stdout.write(text)
    if a.rules_out:
        rules = [{"id": f"moi-{i}", "from": urlsplit(r["url"].strip()).path or "/", "comparison": "exact", "to": r["dich"] if r["ma"] != "410" else "", "code": int(r["ma"])}
                 for i, r in enumerate(res, 1) if r["ma"] in ("301", "302", "410")]
        Path(a.rules_out).write_text(json.dumps(rules, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"đã ghi {len(rules)} rule vào {a.rules_out}", file=sys.stderr)
    return 1 if a.strict and any(r["ma"] == "loi" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
