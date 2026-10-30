#!/usr/bin/env python3
"""Kiểm alt của một ảnh ở mọi biến thể HTML mà trang trả về: khách desktop, khách mobile, Googlebot smartphone.

Alt của một ảnh có thể đến từ hai nguồn: alt của attachment và chuỗi cứng trong template (ví dụ nhánh ảnh mobile khi
trường ACF ảnh mobile để trống). Sửa attachment mà bỏ sót template thì một biến thể vẫn in alt cũ. Script GET từng URL
bằng từng UA, tìm mọi thẻ <img> có --match trong src, data-src, srcset hoặc data-srcset, rồi so alt từng ký tự.
Ca thật 27/10/2026: 3 trang x 3 biến thể, đạt 9/9, 0 alt cũ. Một biến thể mobile đã in chuỗi cứng trong template.

Dùng (chỉ stdlib):
  python3 alt_variants.py --url https://site/trang/ [--url ...] --match ten-file-anh --alt "Alt đúng" [--old-alt "Alt cũ" ...]
                          [--ua desktop|mobile|googlebot ...] [--timeout 15] [--json]
  --match    chuỗi nằm trong URL ảnh (tên file là đủ).
  --alt      alt đúng, so từng ký tự sau khi giải mã entity HTML.
  --old-alt  chuỗi alt cũ. Xuất hiện ở bất kỳ chỗ nào của HTML (gồm JSON-LD) là lỗi. Lặp lại được.
  --ua       mặc định cả ba. Mỗi URL một GET mỗi UA, nghỉ --delay giây giữa hai lượt (mặc định 1).
Googlebot ở đây chỉ là chuỗi UA, không phải IP Google. Site chặn UA giả cho kết quả khác: ghi vào báo cáo.
Mã thoát: 0 mọi biến thể đạt · 1 có biến thể sai alt, thiếu ảnh hoặc còn alt cũ · 2 input sai hoặc lỗi mạng.
"""
import argparse
import json
import sys
import time
import urllib.request
from html.parser import HTMLParser

UAS = {
    "desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "mobile": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "googlebot": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/130.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}
THUOC_TINH = ("src", "data-src", "srcset", "data-srcset", "data-lazy-src")


class Anh(HTMLParser):
    def __init__(self, match):
        super().__init__(convert_charrefs=True)
        self.match = match
        self.thay = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        d = {k: (v or "") for k, v in attrs}
        if any(self.match in d.get(k, "") for k in THUOC_TINH):
            self.thay.append(d.get("alt"))


def tai(url, ua, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def kiem(html, match, alt, old_alts):
    p = Anh(match)
    p.feed(html)
    loi = []
    if not p.thay:
        loi.append("khong_thay_anh")
    for x in p.thay:
        if x != alt:
            loi.append(f"alt_sai: {x!r}")
    for o in old_alts:
        if o and o in html:
            loi.append(f"con_alt_cu: {o!r}")
    return p.thay, loi


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", action="append", required=True)
    ap.add_argument("--match", required=True)
    ap.add_argument("--alt", required=True)
    ap.add_argument("--old-alt", action="append", default=[])
    ap.add_argument("--ua", action="append", choices=sorted(UAS))
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    kq, sai = [], 0
    for u in a.url:
        for ten in a.ua or sorted(UAS):
            try:
                html = tai(u, UAS[ten], a.timeout)
            except Exception as e:  # noqa: BLE001
                print(f"Lỗi mạng {u} ({ten}): {type(e).__name__}", file=sys.stderr)
                return 2
            thay, loi = kiem(html, a.match, a.alt, a.old_alt)
            sai += bool(loi)
            kq.append({"url": u, "ua": ten, "so_anh": len(thay), "dat": not loi, "loi": loi})
            time.sleep(a.delay)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False))
    else:
        for r in kq:
            print(f"{'DAT' if r['dat'] else 'SAI'}\t{r['ua']}\t{r['so_anh']} ảnh\t{r['url']}\t{'; '.join(r['loi'])}")
        print(f"ALT_VARIANTS dat={len(kq) - sai}/{len(kq)}")
    return 1 if sai else 0


if __name__ == "__main__":
    sys.exit(main())
