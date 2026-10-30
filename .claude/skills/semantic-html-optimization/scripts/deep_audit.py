#!/usr/bin/env python3
"""deep_audit.py: đo semantic HTML sâu trên HTML đã tải (không có lệnh mạng).
Dùng: python3 -I deep_audit.py <thư mục html> <urls.tsv> <out.csv> <out_chi_tiet.jsonl>
Đọc <nhom>_d.html. Đo lại các chỉ số của v1 (landmark, H1, nhảy cấp, danh sách sai, bảng không th, b/i, figure lồng)
và các mảng v1 chưa đo: link và nút (href rỗng, không tên, div onclick, lồng tương tác), form không nhãn,
breadcrumb, id trùng, iframe không title, chữ heading (trùng, chung chung, dài), liệt kê viết bằng <p>,
ngày không bọc <time>, <address>, tabindex dương, role heading, chữ nằm ngoài landmark, 400 ký tự sau H1.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup, Comment

try:
    import html5lib  # noqa: F401
    PARSER = "html5lib"
except ImportError:
    PARSER = "lxml"

HTAG = ["h1", "h2", "h3", "h4", "h5", "h6"]
LANDMARK = {"header", "nav", "main", "footer", "aside"}
INTERACTIVE = {"a", "button", "input", "select", "textarea"}
ENUM = re.compile(r"^\s*(\d{1,2}[\.\)]\s|Bước\s*\d|Cách\s*\d|Mẹo\s*\d|Lưu ý\s*\d)", re.I)
DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
GENERIC = {"mô tả sản phẩm", "đánh giá", "hỏi đáp", "sản phẩm tương tự", "câu hỏi thường gặp", "bài viết liên quan",
           "thông số kỹ thuật", "đặc điểm nổi bật", "tin tức", "liên hệ", "có thể bạn thích", "danh mục", "bộ lọc",
           "sản phẩm", "kết luận", "tổng quan", "giới thiệu"}


def txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""


def acc_name(el):
    if el.get("aria-label", "").strip() or el.get("aria-labelledby") or el.get("title", "").strip():
        return True
    if txt(el):
        return True
    for img in el.find_all(["img", "svg"]):
        if (img.get("alt") or "").strip() or img.find("title"):
            return True
    return False


def visible_chain_hidden(el):
    for p in [el] + list(el.parents):
        if getattr(p, "attrs", None) is None:
            continue
        if p.has_attr("hidden") or p.get("aria-hidden") == "true":
            return True
        st = (p.get("style") or "").replace(" ", "").lower()
        if "display:none" in st:
            return True
    return False


def audit(html):
    soup = BeautifulSoup(html, PARSER)
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup(["script", "style", "noscript", "template"]):
        t.decompose()
    body = soup.body or soup
    r, d = {}, {}
    mains = soup.find_all("main")
    main = mains[0] if mains else None
    r["main"] = len(mains)
    hs = soup.find_all(HTAG)
    h1 = soup.find_all("h1")
    r["h1"] = len(h1)
    r["h1_rong"] = sum(1 for h in h1 if not txt(h))
    r["h1_trong_main"] = sum(1 for h in h1 if main and main in h.parents)
    d["h1_text"] = [txt(h)[:120] for h in h1]
    # nhảy cấp toàn trang
    seq, skips = [], []
    last = 0
    for h in hs:
        lv = int(h.name[1])
        if last and lv > last + 1:
            skips.append(f"h{last}->h{lv}:{txt(h)[:50]}")
        last = lv
        seq.append(f"{h.name}:{txt(h)[:70]}")
    r["heading"] = len(hs)
    r["nhay_cap"] = len(skips)
    d["nhay_cap"] = skips
    d["cay"] = seq
    # chữ heading
    texts = [txt(h).lower() for h in hs if txt(h)]
    dup = [t for t, n in Counter(texts).items() if n > 1]
    r["heading_trung_chu"] = len(dup)
    d["heading_trung_chu"] = dup[:20]
    gen = [txt(h) for h in hs if txt(h).lower().strip(" :") in GENERIC and h.name in ("h2", "h3")]
    r["heading_chung_chung"] = len(gen)
    d["heading_chung_chung"] = gen
    r["heading_dai_120"] = sum(1 for h in hs if len(txt(h)) > 120)
    r["heading_rong"] = sum(1 for h in hs if not txt(h))
    r["heading_an"] = sum(1 for h in hs if visible_chain_hidden(h))
    r["role_heading"] = len(soup.select('[role="heading"]'))
    r["heading_chua_khoi"] = sum(1 for h in hs if h.find(["div", "p", "ul", "section"]))
    # landmark
    for t in ("header", "nav", "footer", "aside", "article", "section"):
        r[t] = len(soup.find_all(t))
    navs = soup.find_all("nav")
    r["nav_khong_nhan"] = sum(1 for n in navs if not (n.get("aria-label") or n.get("aria-labelledby")))
    d["nav"] = [(n.get("aria-label") or n.get("id") or " ".join(n.get("class", [])))[:40] for n in navs]
    r["section_khong_heading"] = sum(1 for s in soup.find_all("section")
                                     if not s.find(HTAG) and not s.get("aria-label") and not s.get("aria-labelledby"))
    # chữ ngoài landmark
    out_chars = 0
    for s in body.find_all(string=True):
        if not s.strip():
            continue
        if not any(getattr(p, "name", None) in LANDMARK for p in s.parents):
            out_chars += len(s.strip())
    r["chu_ngoai_landmark"] = out_chars
    # link và nút
    links = soup.find_all("a")
    r["a"] = len(links)
    r["a_khong_href"] = sum(1 for a in links if not a.has_attr("href"))
    bad = [a for a in links if a.has_attr("href") and (a["href"].strip() in ("", "#") or a["href"].lower().startswith("javascript"))]
    r["a_href_rong_hash_js"] = len(bad)
    d["a_href_rong_hash_js"] = [txt(a)[:40] or str(a.attrs)[:80] for a in bad][:15]
    noname = [a for a in links if a.has_attr("href") and not acc_name(a)]
    r["a_khong_ten"] = len(noname)
    d["a_khong_ten"] = [a.get("href", "")[:80] for a in noname][:15]
    btns = soup.find_all("button")
    r["button"] = len(btns)
    r["button_khong_ten"] = sum(1 for b in btns if not acc_name(b))
    d["button_khong_ten"] = [" ".join(b.get("class", []))[:50] for b in btns if not acc_name(b)][:15]
    onclick = [e for e in soup.find_all(onclick=True) if e.name not in ("a", "button", "input")]
    r["onclick_khong_phai_link"] = len(onclick)
    d["onclick"] = [f"{e.name}.{'.'.join(e.get('class', []))[:40]}" for e in onclick][:10]
    nested = 0
    for e in soup.find_all(["a", "button"]):
        if e.find(["a", "button", "input", "select", "textarea"]):
            nested += 1
    r["tuong_tac_long_nhau"] = nested
    r["blank_thieu_rel"] = sum(1 for a in links if a.get("target") == "_blank" and "noopener" not in " ".join(a.get("rel", [])))
    r["tabindex_duong"] = sum(1 for e in soup.find_all(tabindex=True) if str(e["tabindex"]).lstrip("-").isdigit() and int(e["tabindex"]) > 0)
    # form
    ids_label = {l.get("for") for l in soup.find_all("label") if l.get("for")}
    nolabel = []
    for f in soup.find_all(["input", "select", "textarea"]):
        if f.name == "input" and f.get("type", "text").lower() in ("hidden", "submit", "button", "image", "reset"):
            continue
        ok = (f.get("id") in ids_label or f.find_parent("label") or f.get("aria-label") or f.get("aria-labelledby") or f.get("title"))
        if not ok:
            nolabel.append(f"{f.name}[{f.get('type', '')}] name={f.get('name', '')}")
    r["form_khong_nhan"] = len(nolabel)
    d["form_khong_nhan"] = nolabel[:15]
    # breadcrumb
    bc = soup.select('nav[aria-label*="readcrumb" i], [class*="breadcrumb"], [id*="breadcrumb"]')
    r["breadcrumb"] = 1 if bc else 0
    bc_nav = [b for b in bc if b.name == "nav" or b.find_parent("nav")]
    r["breadcrumb_trong_nav"] = 1 if bc_nav else 0
    r["breadcrumb_dung_ol"] = 1 if any(b.find("ol") or b.name == "ol" for b in bc) else 0
    r["breadcrumb_aria_current"] = 1 if any(b.select('[aria-current]') for b in bc) else 0
    d["breadcrumb_text"] = txt(bc[0])[:150] if bc else ""
    # id trùng
    ids = Counter(e["id"] for e in soup.find_all(id=True))
    dup_id = [k for k, n in ids.items() if n > 1]
    r["id_trung"] = len(dup_id)
    d["id_trung"] = dup_id[:15]
    # iframe, ảnh
    ifr = soup.find_all("iframe")
    r["iframe"] = len(ifr)
    r["iframe_khong_title"] = sum(1 for i in ifr if not (i.get("title") or "").strip())
    imgs = soup.find_all("img")
    r["img"] = len(imgs)
    r["img_khong_alt"] = sum(1 for i in imgs if not i.has_attr("alt"))
    r["img_alt_rong"] = sum(1 for i in imgs if i.has_attr("alt") and not i["alt"].strip())
    r["img_thieu_kt"] = sum(1 for i in imgs if not (i.get("width") and i.get("height")))
    # danh sách
    bad_list = 0
    for l in soup.find_all(["ul", "ol"]):
        if any(getattr(c, "name", None) not in (None, "li", "script", "template") for c in l.children):
            bad_list += 1
    r["ds_sai"] = bad_list
    # liệt kê viết bằng <p> (≥2 đoạn liền nhau mở bằng số/Bước)
    enum_runs, run = [], []
    for p in (main or body).find_all("p"):
        t = txt(p)
        if ENUM.match(t):
            run.append(t[:60])
        else:
            if len(run) >= 2:
                enum_runs.append(run)
            run = []
    if len(run) >= 2:
        enum_runs.append(run)
    r["liet_ke_bang_p"] = len(enum_runs)
    d["liet_ke_bang_p"] = [x[:3] for x in enum_runs][:8]
    r["ol"] = len(soup.find_all("ol"))
    r["dl"] = len(soup.find_all("dl"))
    # bảng
    tbl = soup.find_all("table")
    r["table"] = len(tbl)
    r["table_khong_th"] = sum(1 for t in tbl if not t.find("th"))
    r["table_caption"] = sum(1 for t in tbl if t.find("caption"))
    # chữ
    r["b_co_chu"] = sum(1 for b in soup.find_all("b") if txt(b))
    r["i_co_chu"] = sum(1 for i in soup.find_all("i") if txt(i))
    r["strong"] = len(soup.find_all("strong"))
    r["blockquote"] = len(soup.find_all("blockquote"))
    r["cite"] = len(soup.find_all("cite"))
    r["figure"] = len(soup.find_all("figure"))
    r["figure_long_figure"] = sum(1 for f in soup.find_all("figure") if f.find("figure"))
    # ngày
    times = soup.find_all("time")
    r["time"] = len(times)
    r["time_thieu_datetime"] = sum(1 for t in times if not t.get("datetime"))
    date_txt = 0
    for s in (main or body).find_all(string=DATE):
        if not any(getattr(p, "name", None) == "time" for p in s.parents):
            date_txt += len(DATE.findall(s))
    r["ngay_khong_time"] = date_txt
    # địa chỉ, liên hệ
    r["address"] = len(soup.find_all("address"))
    r["tel_link"] = sum(1 for a in links if a.get("href", "").startswith("tel:"))
    r["mailto_link"] = sum(1 for a in links if a.get("href", "").startswith("mailto:"))
    # html lang, skip link
    r["lang"] = (soup.html.get("lang") if soup.html else "") or ""
    r["skip_link"] = 1 if soup.select('a[href="#main"], a[href="#content"], a[href="#primary"], a.skip-link') else 0
    # thẻ sản phẩm
    cards = soup.select(".product-card-wrapper")
    r["the_sp"] = len(cards)
    r["the_sp_article"] = sum(1 for c in cards if c.name == "article" or c.find("article"))
    r["the_sp_trong_li"] = sum(1 for c in cards if c.parent and c.parent.name == "li" or c.name == "li")
    # 400 ký tự sau H1
    flow = ""
    if h1:
        buf = []
        for s in h1[0].find_all_next(string=True):
            t = s.strip()
            if t:
                buf.append(t)
            if sum(len(x) for x in buf) > 420:
                break
        flow = re.sub(r"\s+", " ", " ".join(buf))[:400]
    d["flow_400"] = flow
    # DOM
    r["dom_node"] = len(body.find_all(True)) + (len(soup.head.find_all(True)) if soup.head else 0)
    return r, d


def main():
    hdir, urls, out, outj = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    rows = list(csv.DictReader(open(urls, encoding="utf-8"), delimiter="\t"))
    res = []
    with open(outj, "w", encoding="utf-8") as fj:
        for row in rows:
            f = hdir / f"{row['nhom']}_d.html"
            if not f.exists():
                continue
            r, d = audit(f.read_text(encoding="utf-8", errors="replace"))
            res.append({"nhom": row["nhom"], "path": row["path"], **r})
            fj.write(json.dumps({"nhom": row["nhom"], "path": row["path"], **d}, ensure_ascii=False) + "\n")
    with open(out, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print(f"parser={PARSER} url={len(res)}")


if __name__ == "__main__":
    main()
