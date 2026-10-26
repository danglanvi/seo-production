#!/usr/bin/env python3
"""Đo index của chuyên mục, phân trang và sitemap (technical-seo-audit, khu vực 2, 3, 4).

Lệnh:
  probe [URL ...] [--urls urls.tsv] [--html URL FILE ...] [--delay 1] [--out kq.tsv]
      Mỗi URL: mã HTTP (không theo redirect), Location, meta robots, X-Robots-Tag, canonical, canonical tự trỏ,
      số thẻ <loc> (sitemap). urls.tsv: "url<TAB>kỳ vọng", kỳ vọng là index | noindex | loc>=N | loc=N | -.
      --html đọc HTML đã lưu (ví dụ output stg_get.sh của staging), không có header.
      URL có query chỉ dùng để xác nhận noindex. Kỳ vọng index trên URL có query bị ghi "lệch".
      Exit 1 khi có dòng lệch kỳ vọng.
  paged P1 P2 [--html1 FILE --html2 FILE]
      So link nội bộ của trang 1 và trang 2, bỏ link phân trang. Không có link nào chỉ ở trang 2 thì là phân
      trang giả: trang 2 lặp danh sách trang 1. Exit 1 khi một trang không trích được link nào.

Python stdlib. Chỉ GET, 1 request mỗi --delay giây, User-Agent trình duyệt.
"""
import argparse
import collections
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/141.0.0.0 Safari/537.36")
PAGINATION = re.compile(r"/page/\d+/?$")
COLS = ("url", "code", "location", "meta_robots", "x_robots", "canonical", "self_canonical", "loc", "query",
        "ky_vong", "ket_qua")


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.robots, self.canonical, self.links = [], [], []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot"):
            self.robots.append(a.get("content", "").strip())
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical.append(a.get("href", "").strip())
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"].strip())


def parse(html):
    h = Head()
    h.feed(html)
    return h


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity",
                                               "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, {"x-loi": str(e)}, ""


def same_page(canonical, url):
    c, u = urlsplit(canonical), urlsplit(url)
    if (c.path or "/") != (u.path or "/") or c.query != u.query:
        return False
    return not c.netloc or not u.netloc or c.netloc.lower() == u.netloc.lower()


def is_noindex(row):
    return "noindex" in (row["meta_robots"] + ";" + row["x_robots"]).lower()


def judge(row, expect):
    if not expect or expect == "-":
        return "-"
    m = re.fullmatch(r"loc(>=|=)(\d+)", expect)
    if m:
        n = int(row["loc"])
        ok = n >= int(m.group(2)) if m.group(1) == ">=" else n == int(m.group(2))
        return "đạt" if ok else f"lệch: {n} thẻ <loc>"
    if row["code"] != "200":
        return f"lệch: mã {row['code']}"
    if expect == "noindex":
        return "đạt" if is_noindex(row) else "lệch: trang index"
    if expect == "index":
        if row["query"] == "1":
            return "lệch: URL có query, không kết luận index từ URL này"
        if is_noindex(row):
            return "lệch: noindex"
        return "đạt" if row["self_canonical"] == "1" else "lệch: canonical không tự trỏ"
    return f"lệch: kỳ vọng lạ '{expect}'"


def probe_row(url, code, headers, html, expect=""):
    h = parse(html) if html else Head()
    hd = {k.lower(): v for k, v in headers.items()}
    canon = ";".join(h.canonical)
    row = {"url": url, "code": str(code), "location": hd.get("location", ""), "meta_robots": ";".join(h.robots),
           "x_robots": hd.get("x-robots-tag", ""), "canonical": canon,
           "self_canonical": "1" if h.canonical and all(same_page(c, url) for c in h.canonical) else "0",
           "loc": str(len(re.findall(r"<loc>", html or ""))), "query": "1" if urlsplit(url).query else "0",
           "ky_vong": expect or "-"}
    row["ket_qua"] = judge(row, expect)
    return row


def read_text(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def read_urls(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and not line.lstrip().startswith("#"):
                p = line.rstrip("\n").split("\t")
                out.append((p[0].strip(), p[1].strip() if len(p) > 1 else ""))
    return out


def cmd_probe(a):
    items = [(u, "") for u in a.url] + (read_urls(a.urls) if a.urls else [])
    rows = []
    for i, (u, exp) in enumerate(items):
        if i:
            time.sleep(a.delay)
        code, headers, html = fetch(u)
        rows.append(probe_row(u, code, headers, html, exp))
    for u, f in a.html or []:
        rows.append(probe_row(u, 200, {}, read_text(f)))
    lines = ["\t".join(COLS)] + ["\t".join(r[c] for c in COLS) for r in rows]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    bad = [r for r in rows if r["ket_qua"].startswith("lệch")]
    if bad:
        print(f"{len(bad)}/{len(rows)} dòng lệch kỳ vọng", file=sys.stderr)
    return 1 if bad else 0


def site_links(html, base, site_host=None):
    hrefs = [urljoin(base, x).split("#")[0] for x in parse(html).links]
    hosts = collections.Counter(urlsplit(x).netloc.lower() for x in hrefs if urlsplit(x).netloc)
    host = site_host or (urlsplit(base).netloc.lower() if urlsplit(base).netloc.lower() in hosts else
                         (hosts.most_common(1)[0][0] if hosts else ""))
    out = set()
    for x in hrefs:
        s = urlsplit(x)
        if s.scheme not in ("http", "https") or s.netloc.lower() != host:
            continue
        if PAGINATION.search(s.path) or "paged=" in s.query:
            continue
        out.add((s.path or "/") + ("?" + s.query if s.query else ""))
    return out, host


def compare_pages(html1, html2, p1, p2):
    l1, host = site_links(html1, p1)
    l2, _ = site_links(html2, p2, host)
    skip = {urlsplit(p1).path or "/", urlsplit(p2).path or "/"}
    l1, l2 = l1 - skip, l2 - skip
    return {"p1": len(l1), "p2": len(l2), "only_p2": len(l2 - l1), "only_p1": len(l1 - l2),
            "mau_only_p2": sorted(l2 - l1)[:5]}


def cmd_paged(a):
    if a.html1 and a.html2:
        h1, h2 = read_text(a.html1), read_text(a.html2)
    else:
        c1, _, h1 = fetch(a.p1)
        time.sleep(a.delay)
        c2, _, h2 = fetch(a.p2)
        if c1 != 200 or c2 != 200:
            print(f"LỖI: mã trang 1 = {c1}, trang 2 = {c2}. Cần cả hai trả 200.", file=sys.stderr)
            return 1
    r = compare_pages(h1, h2, a.p1, a.p2)
    print(f"p1={r['p1']} p2={r['p2']} only_p2={r['only_p2']} only_p1={r['only_p1']}")
    if not r["p1"] or not r["p2"]:
        print("LỖI: một trang không trích được link nội bộ nào. Không kết luận.", file=sys.stderr)
        return 1
    if r["only_p2"]:
        print(f"phân trang thật: {r['only_p2']} link chỉ có ở trang 2, ví dụ {', '.join(r['mau_only_p2'])}")
    else:
        print("phân trang giả: trang 2 không có link nào khác trang 1")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("url", nargs="*")
    p.add_argument("--urls")
    p.add_argument("--html", nargs=2, action="append", metavar=("URL", "FILE"))
    p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--out")
    p.set_defaults(func=cmd_probe)
    g = sub.add_parser("paged")
    g.add_argument("p1")
    g.add_argument("p2")
    g.add_argument("--html1")
    g.add_argument("--html2")
    g.add_argument("--delay", type=float, default=1.0)
    g.set_defaults(func=cmd_paged)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
