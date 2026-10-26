#!/usr/bin/env python3
"""Lấy title và H1 của trang đối thủ từ sitemap công khai (topical-focus, lệnh gap).

Dùng:
  competitor_titles.py --sitemap https://<đối thủ>/sitemap_index.xml [--sitemap ...] --site <tên> --out titles.jsonl
                       [--include 'post|page|blog'] [--exclude-url REGEX] [--max 600] [--seed 19] [--workers 4]
  - Sitemap index: chỉ đọc sitemap con có tên khớp --include (bỏ taxonomy, tuyển dụng, tag).
  - --max: quá số này thì lấy mẫu ngẫu nhiên có seed, ghi lại số URL gốc để báo cáo phủ bao nhiêu.
  - Chạy lại lệnh thì bỏ qua URL đã lấy được (status 200). URL lỗi được thử lại; dòng sau cùng của một URL thắng.
  - Gặp 429 hoặc 503 (site chặn tốc độ): script nghỉ rồi thử lại 3 lần. Vẫn lỗi thì chạy lại với --workers 1.
Chỉ GET trang công khai, đọc tối đa 400 KB mỗi trang, nghỉ giữa các lượt. Python stdlib.
"""
import argparse
import html
import json
import random
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"


def get(url, limit=400_000, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.read(limit).decode("utf-8", "ignore")


def locs(xml):
    return [html.unescape(x.strip()) for x in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml)]


def sitemap_urls(index_url, include):
    _, _, xml = get(index_url, limit=5_000_000)
    if "<sitemapindex" in xml:
        rx = re.compile(include) if include else None
        out = []
        for sm in locs(xml):
            if rx and not rx.search(sm.rsplit("/", 1)[-1]):
                continue
            _, _, sub = get(sm, limit=20_000_000)
            out += locs(sub)
            time.sleep(0.5)
        return out
    return locs(xml)


class Head(HTMLParser):
    """Đọc title, H1 đầu tiên, lang, meta robots."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.h1, self.lang, self.robots = "", "", "", ""
        self._in = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang") or ""
        elif tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.robots = a.get("content") or ""
        elif tag in ("title", "h1") and self._in is None and not (tag == "title" and self.title) and not (tag == "h1" and self.h1):
            self._in, self._buf = tag, []

    def handle_endtag(self, tag):
        if tag == self._in:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            setattr(self, tag, text)
            self._in = None

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def parse(page):
    h = Head()
    try:
        h.feed(page)
    except Exception:  # HTML hỏng: giữ phần đã đọc
        pass
    return {"title": h.title, "h1": h.h1, "lang": h.lang, "robots": h.robots}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sitemap", action="append", required=True)
    ap.add_argument("--site", required=True, help="tên đối thủ, ghi vào từng dòng")
    ap.add_argument("--out", required=True)
    ap.add_argument("--include", default=r"(post|page|blog|solution|service|dich-vu)[-_]?sitemap")
    ap.add_argument("--exclude-url", default=r"/(tag|category|tuyen-dung|career|author)/")
    ap.add_argument("--max", type=int, default=600)
    ap.add_argument("--seed", type=int, default=19)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()

    urls = []
    for sm in a.sitemap:
        urls += sitemap_urls(sm, a.include)
    rx = re.compile(a.exclude_url) if a.exclude_url else None
    urls = sorted({u for u in urls if not (rx and rx.search(u))})
    total = len(urls)
    if total > a.max:
        urls = sorted(random.Random(a.seed).sample(urls, a.max))
    out = Path(a.out)
    done = set()
    if out.exists():
        done = {r["url"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines()) if r.get("status") == 200}
    todo = [u for u in urls if u not in done]
    print(f"{a.site}: {total} URL trong sitemap, lấy {len(urls)}, cần GET {len(todo)}", file=sys.stderr)

    def work(u):
        for attempt in range(4):
            time.sleep(0.5 if attempt == 0 else 10 * attempt)
            try:
                st, final, page = get(u)
                return {"site": a.site, "url": u, "final_url": final, "status": st, **parse(page),
                        "sitemap_total": total, "sampled": len(urls)}
            except Exception as x:
                err = getattr(x, "code", None) or type(x).__name__
                if err not in (429, 503):
                    break
        return {"site": a.site, "url": u, "status": err, "sitemap_total": total, "sampled": len(urls)}

    out.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as ex, out.open("a", encoding="utf-8") as fh:
        for i, rec in enumerate(ex.map(work, todo), 1):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}", file=sys.stderr)


if __name__ == "__main__":
    main()
