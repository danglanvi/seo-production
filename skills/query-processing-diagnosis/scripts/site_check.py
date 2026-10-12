#!/usr/bin/env python3
"""Kiểm trang thật cho khối levers/qa (chỉ GET). Tải từng URL vào <thư mục>, in báo cáo gọn:
title, robots, canonical, H1/H2, JSON-LD (parse được không, loại, breadcrumb, ProductGroup), link theo vùng (menu/body/footer),
link tới các trang trong danh sách kèm anchor, phân trang, ảnh thiếu alt.

  python3 site_check.py <thư mục> key=https://... key2=https://...   [--cached]

Truyền từng cặp key=url thành đối số riêng (zsh không tách biến chứa nhiều đối số).
curl dùng --compressed: có site trả gzip kể cả khi không xin. Trang chờ (Cloudflare "One moment, please...",
"Just a moment") hiện ở dòng title: ghi thành lỗi retrieve, không đọc nội dung trang đó.
"""
import json, os, re, subprocess, sys, time
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

out_dir = sys.argv[1]
cached = "--cached" in sys.argv
pages = [a.split("=", 1) for a in sys.argv[2:] if "=" in a and not a.startswith("--")]
os.makedirs(out_dir, exist_ok=True)


class P(HTMLParser):
    def __init__(s, base):
        super().__init__(); s.base = base; s.z = []; s.a = None; s.at = ""; s.links = []; s.imgs = []; s.h = []; s.cur = None; s.buf = ""
        s.skip = 0; s.meta = {}; s.canon = None; s.ld = []; s.inld = False; s.ldbuf = ""

    def handle_starttag(s, tag, attrs):
        d = dict(attrs)
        if tag in ("header", "nav", "footer"):
            s.z.append(tag)
        if tag == "script" and (d.get("type") or "").lower() == "application/ld+json":
            s.inld = True; s.ldbuf = ""
        if tag in ("script", "style", "svg", "noscript"):
            s.skip += 1
        if tag == "meta" and (d.get("name") or "").lower() in ("robots", "description"):
            s.meta[d["name"].lower()] = d.get("content")
        if tag == "link" and (d.get("rel") or "").lower() == "canonical":
            s.canon = d.get("href")
        if tag in ("h1", "h2", "h3"):
            s.cur = tag; s.buf = ""
        if tag == "a" and d.get("href"):
            s.a = urljoin(s.base, d["href"]); s.at = ""
        if tag == "img":
            alt = d.get("alt")
            if s.a is not None:
                s.at += f" [img:{alt or ''}]"
            if not s.z:
                s.imgs.append(alt)

    def handle_endtag(s, tag):
        if tag in ("header", "nav", "footer") and tag in s.z:
            i = len(s.z) - 1 - s.z[::-1].index(tag); s.z = s.z[:i]
        if tag == "script" and s.inld:
            s.inld = False; s.ld.append(s.ldbuf)
        if tag in ("script", "style", "svg", "noscript"):
            s.skip = max(0, s.skip - 1)
        if tag == s.cur:
            t = re.sub(r"\s+", " ", s.buf).strip()
            if t:
                s.h.append((tag, t))
            s.cur = None
        if tag == "a" and s.a is not None:
            zone = "footer" if "footer" in s.z else "menu" if s.z else "body"
            s.links.append((s.a, re.sub(r"\s+", " ", s.at).strip()[:70], zone)); s.a = None

    def handle_data(s, d):
        if s.inld:
            s.ldbuf += d
        if s.skip:
            return
        if s.cur:
            s.buf += d
        if s.a is not None:
            s.at += d


def walk(o, out):
    if isinstance(o, dict):
        t = o.get("@type")
        if t:
            out.append((t if isinstance(t, str) else "/".join(t), o))
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


NOISE = {"ContactPoint", "Country", "PostalAddress", "ImageObject", "ListItem", "EntryPoint", "SearchAction", "QuantitativeValue", "MonetaryAmount", "DefinedRegion", "ShippingDeliveryTime", "OpeningHoursSpecification", "AdministrativeArea", "Thing", "Person", "Brand", "PropertyValue", "GeoCoordinates", "Audience", "BuyAction", "DefinedTerm", "CreativeWorkSeries", "Answer", "Question", "Credential", "Rating"}


def norm(u):
    p = urlparse(u)
    return (p.netloc.replace("www.", ""), p.path.rstrip("/") or "/")


keys = {norm(u): k for k, u in pages}
for k, url in pages:
    f = os.path.join(out_dir, k + ".html")
    code = "cache"
    if not cached or not os.path.exists(f):
        code = subprocess.run(["curl", "-s", "-L", "--compressed", "-A", "Mozilla/5.0", "-o", f, "-w", "%{http_code}", "--max-time", "40", url], capture_output=True, text=True).stdout
        time.sleep(1.5)
    raw = open(f, encoding="utf-8", errors="ignore").read() if os.path.exists(f) else ""
    p = P(url); p.feed(raw)
    host = urlparse(url).netloc.replace("www.", "")
    title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    print(f"\n=== {k} {url} [{code}] {len(raw)//1024}KB")
    tt = re.sub(r"\s+", " ", title.group(1)).strip()[:120] if title else None
    print(f"  title: {tt}")
    print(f"  robots: {p.meta.get('robots')} | canonical: {p.canon}")
    h1 = [t for g, t in p.h if g == "h1"]; h2 = [t for g, t in p.h if g == "h2"]
    print(f"  H1: {h1[:2]} | H2 ({len(h2)}): {[x[:45] for x in h2[:12]]}")
    types, errs = [], []
    for b in p.ld:
        try:
            walk(json.loads(b), types)
        except Exception as ex:
            snip = re.sub(r"\s+", " ", b)[:90]
            errs.append(f"{str(ex)[:60]} :: {snip}")
    tset = sorted({t for t, _ in types})
    print(f"  JSON-LD: {len(p.ld)} khối, lỗi {len(errs)} | loại: {[x for x in tset if x not in NOISE]}")
    for e_ in errs:
        print("   ! LỖI:", e_)
    for t, o in types:
        if t == "BreadcrumbList":
            print("   breadcrumb:", " › ".join(str(i.get("name") or (i.get("item") or {}).get("name", "") if isinstance(i.get("item"), dict) else i.get("name")) for i in o.get("itemListElement", []) if isinstance(i, dict)))
        if t == "ProductGroup":
            hv = o.get("hasVariant") or []
            print(f"   ProductGroup: variesBy={o.get('variesBy')} variant={len(hv)} size_field={sum(1 for v in hv if isinstance(v, dict) and v.get('size'))}")
        if t == "FAQPage":
            print("   FAQPage: có")
    internal = [(a, t, z) for a, t, z in p.links if urlparse(a).netloc.replace("www.", "") == host]
    by = {z: len({norm(a) for a, _, zz in internal if zz == z}) for z in ("menu", "body", "footer")}
    print(f"  link nội bộ duy nhất: menu {by['menu']}, body {by['body']}, footer {by['footer']}")
    pag = sorted({int(x) for x in re.findall(r"(?:[?&]page=|/page/)(\d+)", raw)})
    if pag:
        print(f"  phân trang: {pag[:3]}…{pag[-1]}")
    imgs = p.imgs
    print(f"  ảnh (ngoài menu/footer): {len(imgs)}, thiếu alt {sum(1 for a in imgs if not (a or '').strip())}")
    hits = {}
    for a, t, z in internal:
        kk = keys.get(norm(a))
        if kk and kk != k:
            hits.setdefault(kk, set()).add(f"{z}:{t[:50]}" if z == "body" else z)
    for kk, v in hits.items():
        print(f"   → {kk}: {sorted(v)[:5]}")
