#!/usr/bin/env python3
"""semantic_audit.py (semantic-html-optimization): audit semantic HTML chỉ đọc theo mẫu URL đại diện mỗi template.

Dùng: python3 -I semantic_audit.py --base https://<domain> <chon.tsv> <thư mục html> <out.csv>
chon.tsv có cột path và nhom (template). Tải mỗi path 1 lần (URL sạch, 1 request/giây, UA riêng), lưu HTML vào thư mục,
lần sau đọc lại file đã lưu. Đo theo trang: H1, heading trong và ngoài <main>, nhảy cấp, heading rỗng, heading giả
(<p> chỉ chứa <strong>/<b> dài 3–80 ký tự), số thẻ landmark và thẻ ngữ nghĩa, <nav> thiếu nhãn, ảnh thiếu kích thước hoặc alt.
Chạy thật 27/10/2026 trên 95 URL của site agency mẫu: tìm ra 3 trang thiếu <main>, 0/95 trang có <time>, card không bọc <article>.
"""
import csv
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "semantic-audit-readonly/1.0"
TAGS = ["main", "header", "footer", "nav", "article", "section", "aside", "figure", "figcaption", "time", "table", "th", "caption", "ol", "ul", "blockquote", "b", "i", "strong", "em", "details"]


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.c = {t: 0 for t in TAGS}
        self.heads = []          # (level, text)
        self.cur = None
        self.skip = 0            # trong script/style
        self.img = 0
        self.img_nodim = 0
        self.img_noalt = 0
        self.main_depth = 0
        self.in_main = False
        self.h_in_main = []
        self.nav_nolabel = 0
        self.after_h1 = None     # chữ sau H1
        self.fake_h = 0          # <p><strong> đứng một mình, ngắn (heading giả)
        self._p_text = None
        self._p_strong = ""
        self._p_in_strong = 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("script", "style", "noscript", "template"):
            self.skip += 1
            return
        if tag in self.c:
            self.c[tag] += 1
        if tag == "nav" and not a.get("aria-label") and not a.get("aria-labelledby"):
            self.nav_nolabel += 1
        if tag == "main":
            self.in_main = True
        if tag == "img":
            self.img += 1
            if not a.get("width") or not a.get("height"):
                self.img_nodim += 1
            if a.get("alt") is None:
                self.img_noalt += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.cur = [int(tag[1]), ""]
        if tag == "p":
            self._p_text, self._p_strong, self._p_in_strong = "", "", 0
        if tag in ("strong", "b") and self._p_text is not None:
            self._p_in_strong += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template"):
            self.skip = max(0, self.skip - 1)
            return
        if tag == "main":
            self.in_main = False
        if self.cur and tag == "h%d" % self.cur[0]:
            lv, tx = self.cur[0], re.sub(r"\s+", " ", self.cur[1]).strip()
            self.heads.append((lv, tx))
            if self.in_main:
                self.h_in_main.append((lv, tx))
            if lv == 1 and self.after_h1 is None:
                self.after_h1 = ""
            self.cur = None
        if tag in ("strong", "b") and self._p_text is not None:
            self._p_in_strong = max(0, self._p_in_strong - 1)
        if tag == "p" and self._p_text is not None:
            pt, st = self._p_text.strip(), self._p_strong.strip()
            if st and pt == st and 3 <= len(pt) <= 80:
                self.fake_h += 1
            self._p_text = None

    def handle_data(self, d):
        if self.skip:
            return
        if self.cur:
            self.cur[1] += d
        if self._p_text is not None:
            self._p_text += d
            if self._p_in_strong:
                self._p_strong += d
        if self.after_h1 is not None and len(self.after_h1) < 400 and not self.cur:
            self.after_h1 += re.sub(r"\s+", " ", d)


def skips(heads):
    n, prev = 0, 0
    for lv, _ in heads:
        if prev and lv > prev + 1:
            n += 1
        prev = lv
    return n


def main():
    a = sys.argv[1:]
    if '--base' not in a or len(a) < 5:
        sys.exit(__doc__)
    i = a.index('--base'); base = a[i + 1].rstrip('/'); del a[i:i + 2]
    tsv, outdir, out = a[0], Path(a[1]), a[2]
    outdir.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t"))
    res = []
    for r in rows:
        path = r["path"]
        f = outdir / (re.sub(r"[^a-z0-9]+", "_", path.strip("/")) or "home")
        f = f.with_suffix(".html")
        if not f.exists():
            req = urllib.request.Request(base + path, headers={"User-Agent": UA, "Accept": "text/html"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    f.write_bytes(resp.read())
            except Exception as e:
                res.append({"path": path, "nhom": r.get("nhom", ""), "loi": str(e)[:80]})
                time.sleep(1)
                continue
            time.sleep(1)
        html = f.read_text(encoding="utf-8", errors="replace")
        p = P()
        p.feed(html)
        h = p.heads
        hm = p.h_in_main
        res.append({
            "path": path, "nhom": r.get("nhom", ""), "kb": round(len(html.encode()) / 1024),
            "h1": sum(1 for lv, _ in h if lv == 1), "h1_main": sum(1 for lv, _ in hm if lv == 1),
            "h_main": len(hm), "h_ngoai_main": len(h) - len(hm), "nhay_cap_main": skips(hm),
            "h_rong": sum(1 for _, t in h if not t), "heading_gia": p.fake_h,
            **{t: p.c[t] for t in TAGS},
            "nav_khong_nhan": p.nav_nolabel, "img": p.img, "img_thieu_kt": p.img_nodim, "img_thieu_alt": p.img_noalt,
            "h1_text": (next((t for lv, t in h if lv == 1), ""))[:70],
            "sau_h1": (p.after_h1 or "")[:160],
        })
    keys = []
    for x in res:
        for k in x:
            if k not in keys:
                keys.append(k)
    with open(out, "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=keys)
        w.writeheader()
        w.writerows(res)
    print("xong", len(res), "trang ->", out)


if __name__ == "__main__":
    main()
