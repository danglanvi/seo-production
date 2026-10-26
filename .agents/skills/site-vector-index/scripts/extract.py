#!/usr/bin/env python3
"""Tách HTML thành dòng cho site vector index: page, section (theo H2), passage, anchor (kèm ngữ cảnh 2 bên).

Chạy bằng Python có beautifulsoup4 (Python hệ thống trên máy GTV có sẵn):
  python3 -E extract.py --urls urls.txt --cache html/ --out rows.jsonl --pages pages.jsonl [--site https://example.com]
  python3 -E extract.py --html-dir html/ --out rows.jsonl --pages pages.jsonl
Chỉ tải URL công khai. Tôn trọng tốc độ: mặc định nghỉ 0,5 s giữa 2 lượt tải.
Main content: chọn vùng bài viết theo selector quen thuộc, bỏ nav, header, footer, aside, form, TOC, khối liên quan, chia sẻ.
Passage mang đường dẫn heading ("H2 > H3: đoạn") để embedding hiểu ngữ cảnh, giống cách công cụ truy xuất cắt chunk.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("cần beautifulsoup4: python3 -m pip install beautifulsoup4")

MAIN_SELECTORS = [".entry-content", ".post-content", ".article-content", "article .content", "main article",
                  "article", "main", "[role=main]", "#content", ".site-content"]
DROP = ("script,style,noscript,svg,iframe,nav,header,footer,aside,form,.toc,#toc,.ez-toc-container,.rank-math-toc,"
        ".related-posts,.related,.social-share,.share,.sharedaddy,.breadcrumb,.breadcrumbs,.comments,#comments,"
        ".widget,.sidebar,.cookie,.popup,.modal")
# Không có "widget": Elementor bọc mọi nội dung trong elementor-widget-*. Sidebar WP (.widget) đã nằm trong DROP.
NOISE_CLASS = re.compile(r"(^|[-_ ])(menu|nav|navbar|footer|header|sidebar|breadcrumb|toc|related|share|"
                         r"social|comment|cookie|popup|modal|newsletter|subscribe)([-_ ]|$)", re.I)
UA = "Mozilla/5.0 (compatible; GTV-SVI/1.0; +site-vector-index)"


def nfc(s):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s or "")).strip()


def words(s):
    return len(s.split())


def fetch(url, cache, delay):
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    path = cache / f"{key}.html" if cache else None
    if path and path.exists():
        return path.read_text(encoding="utf-8", errors="ignore"), 200
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            html, code = r.read(5_000_000).decode(r.headers.get_content_charset() or "utf-8", "ignore"), r.status
    except urllib.error.HTTPError as e:
        return "", e.code
    except Exception:
        return "", 0
    if path:
        cache.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        (cache / f"{key}.url").write_text(url, encoding="utf-8")
    time.sleep(delay)
    return html, code


def pick_main(soup):
    """Selector đầu tiên theo thứ tự ưu tiên mà vùng lớn nhất của nó có ít nhất 50% số từ của vùng lớn nhất mọi selector.
    Trang Elementor có nhiều <article> nhỏ (thẻ testimonial, thẻ bài): lấy vùng lớn nhất, không lấy thẻ đầu tiên."""
    best = []
    for sel in MAIN_SELECTORS:
        els = soup.select(sel)
        if els:
            el = max(els, key=lambda e: words(e.get_text(" ")))
            best.append((sel, el, words(el.get_text(" "))))
    top = max((w for _, _, w in best), default=0)
    for sel, el, w in best:
        if w >= 80 and w >= 0.5 * top:
            return el, sel
    return soup.body or soup, "body"


def strip_noise(main):
    for el in main.select(DROP):
        el.decompose()
    total = words(main.get_text(" ")) or 1
    for el in main.find_all(True):
        if el.attrs is None:
            continue
        cls = " ".join(el.get("class") or []) + " " + (el.get("id") or "")
        if NOISE_CLASS.search(cls) and el.name not in ("p", "li", "td", "h2", "h3", "h4"):
            if words(el.get_text(" ")) > 0.3 * total:
                continue  # khối nhiễu không chứa phần lớn bài: class trùng tên thì giữ lại
            el.decompose()


def parse(html, url, site, max_passage_words, min_passage_words, anchors=True):
    soup = BeautifulSoup(html, "html.parser")
    head = {
        "url": url,
        "title": nfc(soup.title.get_text()) if soup.title else "",
        "meta": nfc((soup.find("meta", attrs={"name": "description"}) or {}).get("content", "")),
        "canonical": (soup.find("link", rel="canonical") or {}).get("href", ""),
        "robots": (soup.find("meta", attrs={"name": "robots"}) or {}).get("content", ""),
        "lang": (soup.html or {}).get("lang", "") if soup.html else "",
    }
    h1 = soup.find("h1")
    head["h1"] = nfc(h1.get_text(" ")) if h1 else ""
    main, sel = pick_main(soup)
    # Link nav/footer dùng để so vị trí: ghi trước khi bỏ khối nhiễu.
    main_links = {id(a) for a in main.find_all("a", href=True)}
    strip_noise(main)
    kept_links = {id(a) for a in main.find_all("a", href=True)}
    head["main_selector"] = sel
    sections, cur = [], {"h2": "", "h3": "", "blocks": []}
    for el in main.find_all(["h2", "h3", "h4", "p", "li", "td", "blockquote", "figcaption", "dd"]):
        if el.find_parent(["li", "td", "blockquote"]) and el.name in ("p",):
            continue  # đoạn nằm trong li/td đã lấy ở cha
        t = nfc(el.get_text(" "))
        if not t:
            continue
        if el.name == "h2":
            if cur["blocks"] or cur["h2"]:
                sections.append(cur)
            cur = {"h2": t, "h3": "", "blocks": []}
        elif el.name in ("h3", "h4"):
            cur["h3"] = t
            cur["blocks"].append({"kind": "heading", "text": t, "h3": t})
        else:
            cur["blocks"].append({"kind": el.name, "text": t, "h3": cur["h3"]})
    if cur["blocks"] or cur["h2"]:
        sections.append(cur)
    head["h2"] = [s["h2"] for s in sections if s["h2"]]
    first = next((b["text"] for s in sections for b in s["blocks"] if b["kind"] == "p" and words(b["text"]) >= 15), "")
    head["first_para"] = first
    head["words_main"] = sum(words(b["text"]) for s in sections for b in s["blocks"] if b["kind"] != "heading")

    rows = []
    page_text = " | ".join(x for x in [head["title"], head["h1"], head["meta"], "; ".join(head["h2"][:12]), first] if x)
    if page_text:  # PDF hoặc trang render bằng JS: không có chữ để embed, chỉ ghi trong pages.jsonl
        rows.append({"id": f"{url}#page", "level": "page", "url": url, "text": page_text[:4000],
                     "meta": {"title": head["title"], "h1": head["h1"], "words_main": head["words_main"]}})
    for si, s in enumerate(sections):
        body = " ".join(b["text"] for b in s["blocks"] if b["kind"] != "heading")
        if words(body) < 20:
            continue
        rows.append({"id": f"{url}#s{si}", "level": "section", "url": url,
                     "text": (s["h2"] + ": " if s["h2"] else "") + body[:12000],
                     "meta": {"heading": s["h2"], "section_index": si, "words": words(body)}})
        # Passage: gộp khối liền nhau tới khoảng max_passage_words, không vượt ranh giới H3.
        buf, h3, pi = [], None, 0

        def flush():
            nonlocal buf, pi
            txt = " ".join(buf)
            if words(txt) >= min_passage_words:
                path = " > ".join(x for x in (s["h2"], h3) if x)
                rows.append({"id": f"{url}#s{si}p{pi}", "level": "passage", "url": url,
                             "text": (path + ": " if path else "") + txt,
                             "meta": {"heading": s["h2"], "h3": h3 or "", "section_index": si, "words": words(txt)}})
                pi += 1
            buf = []

        for b in s["blocks"]:
            if b["kind"] == "heading":
                flush()
                h3 = b["text"]
                continue
            if words(" ".join(buf + [b["text"]])) > max_passage_words and buf:
                flush()
            buf.append(b["text"])
        flush()
    # Anchor: chữ quanh link trong main content, giống trường context của anchor trong tài liệu leak (F09.3).
    for ai, a in enumerate(soup.find_all("a", href=True) if anchors else []):
        href = urljoin(url, a["href"]).split("#")[0]
        if not href.startswith("http") or (site and urlparse(href).netloc != urlparse(site).netloc):
            continue
        zone = "main" if id(a) in kept_links else ("main_noise" if id(a) in main_links else "template")
        if zone != "main":
            continue
        img = a.find("img")
        anchor = nfc(a.get_text(" ")) or (nfc(img.get("alt", "")) if img else "")
        block = a.find_parent(["p", "li", "td", "blockquote"]) or a.parent
        ctx = nfc(block.get_text(" ")) if block else anchor
        if not (ctx or anchor):
            continue  # link ảnh không alt: không có chữ để embed
        rows.append({"id": f"{url}#a{ai}", "level": "anchor", "url": url, "text": ctx[:1500] or anchor,
                     "meta": {"anchor": anchor, "target": href, "zone": zone}})
    return head, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--urls", type=Path, help="file mỗi dòng 1 URL")
    src.add_argument("--html-dir", type=Path, help="thư mục .html; URL lấy từ file .url cùng tên hoặc canonical")
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--site", default="", help="chỉ giữ anchor nội bộ của domain này")
    ap.add_argument("--no-anchors", action="store_true", help="bỏ level anchor (trang đối thủ, SERP)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pages", required=True, type=Path)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--max-passage-words", type=int, default=160)
    ap.add_argument("--min-passage-words", type=int, default=25)
    a = ap.parse_args()

    jobs = []
    if a.urls:
        jobs = [u.strip() for u in a.urls.read_text(encoding="utf-8").splitlines() if u.strip().startswith("http")]
    else:
        jobs = sorted(a.html_dir.glob("*.html"))
    pages, rows, failed = [], [], []
    for j in jobs:
        if isinstance(j, Path):
            html = j.read_text(encoding="utf-8", errors="ignore")
            side = j.with_suffix(".url")
            url = side.read_text(encoding="utf-8").strip() if side.exists() else ""
            if not url:
                m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html)
                url = m.group(1) if m else j.stem
            code = 200
        else:
            url = j
            html, code = fetch(url, a.cache, a.delay)
        if code != 200 or not html:
            failed.append({"url": url, "status": code})
            continue
        head, r = parse(html, url, a.site, a.max_passage_words, a.min_passage_words, not a.no_anchors)
        head["status"] = code
        pages.append(head)
        rows.extend(r)
    for p, items in ((a.out, rows), (a.pages, pages)):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), encoding="utf-8")
    if failed:
        Path(str(a.pages) + ".failed.json").write_text(json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8")
    lv = {}
    for r in rows:
        lv[r["level"]] = lv.get(r["level"], 0) + 1
    print(f"extract: {len(pages)} trang, lỗi {len(failed)}, dòng {lv} -> {a.out}", file=sys.stderr)
    return 1 if jobs and not pages else 0


if __name__ == "__main__":
    raise SystemExit(main())
