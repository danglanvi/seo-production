#!/usr/bin/env python3
"""Gom URL bot đã crawl theo cụm chủ đề của topical-focus, so với cụm quan trọng của site. Chỉ stdlib, chạy trên máy.

  python3 -B log_clusters.py --log access.log [--log access.log.1.gz ...] --site https://example.com \\
      --map pages.jsonl --clusters clusters.json [--core core.txt] [--important 1,3] \\
      [--verified-ips ips.txt] [--bot googlebot] [--from 2026-10-01 --to 2026-10-19] --out-dir DIR

Log: combined hoặc common (Apache, Nginx, LiteSpeed). File .gz đọc thẳng.
--map: pages.jsonl của topical-focus, mỗi dòng {"url", "cluster", "title"?}. --clusters: clusters.json {"cluster", "name", "cos_to_core"?}.
--core: URL lõi, mỗi dòng một URL. Cụm quan trọng = cụm chứa URL lõi, hoặc danh sách --important.
--verified-ips: IP đã qua reverse DNS + forward-confirm ở Bước 2. Có file thì chỉ hit từ IP đó tính là bot thật.
Output không chứa IP. Không gửi log cho Jev hay dịch vụ ngoài.
"""
import argparse
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse

# OpenLiteSpeed có thể bọc dòng trong nháy đơn và thêm trường proxy ("-" hoặc IP) trước IP client.
LINE = re.compile(r"^'?(?:\S+ )?(?P<ip>\S+) \S+ \S+ \[" r'(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+)(?: [^"]*)?" '
                  r'(?P<status>\d{3}) (?P<bytes>\S+)(?: "(?P<ref>[^"]*)" "(?P<ua>[^"]*)")?')
BOTS = [("googlebot", re.compile(r"googlebot|google-inspectiontool|storebot-google", re.I)),
        ("bingbot", re.compile(r"bingbot", re.I)),
        ("gptbot", re.compile(r"gptbot|oai-searchbot|chatgpt-user", re.I)),
        ("claudebot", re.compile(r"claudebot|claude-user|claude-searchbot", re.I)),
        ("perplexitybot", re.compile(r"perplexitybot|perplexity-user", re.I)),
        ("googleother", re.compile(r"googleother|google-extended", re.I)),
        ("applebot", re.compile(r"applebot", re.I)),
        ("metabot", re.compile(r"meta-externalagent|facebookexternalhit", re.I)),
        ("bytespider", re.compile(r"bytespider", re.I)),
        ("amazonbot", re.compile(r"amazonbot", re.I)),
        ("ccbot", re.compile(r"ccbot", re.I))]
ASSET = re.compile(r"\.(css|js|png|jpe?g|gif|webp|avif|svg|ico|woff2?|ttf|map|xml|txt|json|mp4|pdf)$", re.I)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def norm(url):
    """Bỏ query, fragment, www, hoa thường ở host; path luôn có '/' cuối nếu không phải file."""
    p = urlparse(url)
    path = p.path or "/"
    if not path.endswith("/") and not ASSET.search(path) and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    return urlunparse(("https", p.netloc.lower().removeprefix("www."), path, "", "", ""))


def bot_of(ua):
    for name, rx in BOTS:
        if rx.search(ua or ""):
            return name
    return None


def read_lines(paths):
    for p in paths:
        op = gzip.open if str(p).endswith(".gz") else open
        with op(p, "rt", encoding="utf-8", errors="replace") as f:
            yield from f


def day_of(stamp):
    try:
        return datetime.strptime(stamp.split()[0], "%d/%b/%Y:%H:%M:%S").date().isoformat()
    except ValueError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", action="append", required=True)
    ap.add_argument("--site", required=True, help="gốc site, ví dụ https://example.com")
    ap.add_argument("--map", required=True)
    ap.add_argument("--clusters", required=True)
    ap.add_argument("--core")
    ap.add_argument("--important", default="", help="id cụm quan trọng, cách nhau dấu phẩy")
    ap.add_argument("--verified-ips")
    ap.add_argument("--bot", default="googlebot")
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)

    host = urlparse(a.site).netloc.lower().removeprefix("www.")
    page_cluster = {norm(p["url"]): p["cluster"] for p in jl(a.map)}
    titles = {norm(p["url"]): p.get("title", "") for p in jl(a.map)}
    raw = json.loads(Path(a.clusters).read_text(encoding="utf-8"))
    cl = {c["cluster"]: c for c in (raw if isinstance(raw, list) else raw.get("clusters", []))}
    core = [norm(u) for u in Path(a.core).read_text(encoding="utf-8").split() if u.strip()] if a.core else []
    important = {int(x) for x in a.important.split(",") if x.strip()} | {page_cluster[u] for u in core if u in page_cluster}
    verified = set(Path(a.verified_ips).read_text(encoding="utf-8").split()) if a.verified_ips else None

    stats = Counter()
    hits, bot_hits, days = Counter(), Counter(), set()
    url_hits, status = Counter(), defaultdict(Counter)
    for line in read_lines(a.log):
        m = LINE.match(line)
        if not m:
            stats["dòng không parse được"] += 1
            continue
        stats["dòng parse được"] += 1
        day = day_of(m["time"])
        if (a.date_from and day and day < a.date_from) or (a.date_to and day and day > a.date_to):
            continue
        bot = bot_of(m["ua"])
        if not bot:
            continue
        bot_hits[bot] += 1
        if bot != a.bot:
            continue
        if verified is not None and m["ip"] not in verified:
            stats["hit bot tự khai, IP chưa xác minh"] += 1
            continue
        if m["method"] not in ("GET", "HEAD"):
            continue
        path = m["path"]
        if path.startswith("http"):
            if urlparse(path).netloc.lower().removeprefix("www.") != host:
                continue
            path = urlparse(path).path
        if ASSET.search(urlparse(path).path):
            stats["hit file tĩnh"] += 1
            continue
        u = norm(f"https://{host}{path}")
        days.add(day)
        url_hits[u] += 1
        status[u][m["status"]] += 1
        if "?" in path:
            stats["hit có query"] += 1

    total = sum(url_hits.values())
    rows = []
    for cid in sorted(cl, key=lambda c: -cl[c].get("cos_to_core", 0)):
        urls = [u for u, c in page_cluster.items() if c == cid]
        crawled = [u for u in urls if url_hits[u]]
        h = sum(url_hits[u] for u in urls)
        share_pages = len(urls) / max(len(page_cluster), 1)
        share_hits = h / total if total else 0.0
        rows.append({"cluster": cid, "name": cl[cid].get("name", ""), "important": cid in important,
                     "cos_to_core": cl[cid].get("cos_to_core"), "pages": len(urls), "pages_crawled": len(crawled),
                     "hits": h, "share_pages": round(share_pages, 3), "share_hits": round(share_hits, 3),
                     "ratio": round(share_hits / share_pages, 2) if share_pages and total else None})
    outside = Counter()
    for u, n in url_hits.items():
        if u not in page_cluster:
            seg = urlparse(u).path.strip("/").split("/")[0]
            outside["/" + (seg + "/" if seg else "")] += n
    core_rows = [{"url": u, "title": titles.get(u, ""), "hits": url_hits[u],
                  "per_day": round(url_hits[u] / max(len(days), 1), 2), "status": dict(status[u])} for u in core]
    out = Path(a.out_dir)
    write(out / "clusters.jsonl", rows)
    write(out / "outside_map.jsonl", [{"folder": k, "hits": v} for k, v in outside.most_common()])
    write(out / "core_urls.jsonl", core_rows)
    write(out / "url_hits.jsonl", [{"url": u, "hits": n, "cluster": page_cluster.get(u), "status": dict(status[u])}
                                   for u, n in url_hits.most_common()])
    in_map = sum(r["hits"] for r in rows)
    L = [f"# Crawl theo cụm chủ đề — bot `{a.bot}`", "",
         f"- Số ngày có hit: {len(days)}. Hit HTML của bot: {total}. Trong map: {in_map}. Ngoài map: {total - in_map}.",
         f"- {dict(stats)}",
         f"- Hit theo bot (mọi URL): {dict(bot_hits)}",
         "- IP đã xác minh: " + ("có, chỉ tính IP trong danh sách" if verified is not None else
                                 "chưa; số liệu là hit bot tự khai, chưa phải Googlebot thật"), "",
         "| Cụm | Tên | Quan trọng | Cos tới lõi | Trang | Trang được crawl | Hit | % trang | % hit | Hit/trang so với TB |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| C{r['cluster']} | {r['name']} | {'có' if r['important'] else ''} | {r['cos_to_core']} | {r['pages']} | "
                 f"{r['pages_crawled']} | {r['hits']} | {r['share_pages']:.1%} | {r['share_hits']:.1%} | {r['ratio']} |")
    L += ["", "Hit/trang so với TB < 1 ở cụm quan trọng: bot ghé cụm đó ít hơn mức trung bình của site.", "",
          "## URL lõi", "", "| URL | Hit | Hit/ngày | Status |", "|---|---|---|---|"]
    L += [f"| {r['url']} | {r['hits']} | {r['per_day']} | {r['status']} |" for r in core_rows]
    L += ["", "## Ngoài map (theo thư mục cấp 1)", "", "| Thư mục | Hit |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in outside.most_common(15)]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{total} hit HTML của {a.bot}, {len(rows)} cụm -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
