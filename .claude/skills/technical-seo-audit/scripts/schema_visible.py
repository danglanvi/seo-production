#!/usr/bin/env python3
"""So schema JSON-LD với nội dung hiển thị của trang (technical-seo-audit, mục Semantic Markup).

Lệnh:
  extract  (--html-dir <thư mục> | --urls urls.txt [--save-dir <thư mục>]) --out blocks.jsonl
      Đọc HTML đã lưu (file .html, URL ở file .url cùng tên) hoặc GET URL công khai.
      Tách JSON-LD, giữ khối cần nội dung hiển thị, kiểm tất định từng mục.
  prepare  --blocks blocks.jsonl --out jev_in.jsonl [--all]
      Tạo input Jev cho khối chữ (FAQPage, QAPage, HowTo, Review) mà luật tất định chưa chốt.
  decide   --blocks blocks.jsonl [--jev jev_out.jsonl --gate 0.x] --out report.tsv
      Ghép kết quả tất định với nhãn Jev qua cổng confidence, ra trạng thái từng khối.

Python stdlib. Jev chỉ nhận chữ công khai của trang.
"""
import argparse
import hashlib
import html as htmllib
import json
import re
import sys
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

TEXT_TYPES = {"FAQPage", "QAPage", "HowTo", "Review"}
SELF_TYPES = {"Organization", "LocalBusiness", "ProfessionalService", "Corporation", "EducationalOrganization",
              "OnlineBusiness", "OnlineStore", "WebSite", "WebPage"}
# noscript không bỏ: plugin lazyload lồng noscript không đóng, bỏ qua sẽ mất chữ cả trang.
SKIP_TAGS = {"script", "style", "template", "svg", "head", "title"}
BLOCK_TAGS = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "dt", "dd", "section", "article",
              "summary", "details", "button", "blockquote", "figcaption", "label", "tr", "ul", "ol", "header",
              "footer", "main", "aside", "nav", "form"}
HEAD_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "summary", "dt"}
FAQ_HEAD = re.compile(r"faq|câu hỏi|hỏi đáp|thắc mắc|hỏi - đáp|q&a|questions", re.I)
FOUND, NEAR = 0.85, 0.5


def norm(s):
    s = unicodedata.normalize("NFC", str(s or "")).casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w]+", " ", s)).strip()


def toks(s):
    return set(norm(s).split())


class Page(HTMLParser):
    """Chữ hiển thị theo khối, heading, và HTML ngoài thẻ script để kiểm video."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.open = 0, {}
        self.blocks, self.heads, self.cur = [], [], []
        self.in_head = 0
        self.head_buf = []
        self.ld, self.ld_buf, self.in_ld = [], [], False
        self.media = []

    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if t:
            self.blocks.append(t)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":  # </head> thiếu thì vẫn đọc được thân trang
            self.open, self.skip = {}, 0
        if tag == "script" and "ld+json" in (a.get("type") or "").lower():
            self.in_ld, self.ld_buf = True, []
        if tag in SKIP_TAGS:
            self.open[tag] = self.open.get(tag, 0) + 1
            self.skip = sum(self.open.values())
            return
        if tag in ("iframe", "video", "source", "a", "img", "div", "lite-youtube"):
            for k in ("src", "data-src", "href", "data-id", "videoid", "data-video-id", "data-lazy-src", "data-settings"):
                if a.get(k):
                    self.media.append(a[k])
        if tag in BLOCK_TAGS:
            self.flush()
        if tag in HEAD_TAGS:
            self.in_head += 1
            self.head_buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self.in_ld:
            self.ld.append("".join(self.ld_buf))
            self.in_ld = False
        if tag in SKIP_TAGS:
            self.open[tag] = max(0, self.open.get(tag, 0) - 1)
            self.skip = sum(self.open.values())
            return
        if tag in HEAD_TAGS and self.in_head:
            self.in_head -= 1
            h = re.sub(r"\s+", " ", "".join(self.head_buf)).strip()
            if h:
                self.heads.append(h)
        if tag in BLOCK_TAGS:
            self.flush()

    def handle_data(self, data):
        if self.in_ld:
            self.ld_buf.append(data)
        if self.skip:
            return
        self.cur.append(data)
        if self.in_head:
            self.head_buf.append(data)

    def close(self):
        super().close()
        self.flush()


def nodes(obj, parent=None):
    """Duyệt mọi object có @type trong JSON-LD, kèm type của object cha."""
    if isinstance(obj, list):
        for x in obj:
            yield from nodes(x, parent)
    elif isinstance(obj, dict):
        t = obj.get("@type")
        types = t if isinstance(t, list) else [t] if t else []
        if types:
            yield obj, [str(x) for x in types], parent
        me = types[0] if types else parent
        for k, v in obj.items():
            if k != "@context":
                yield from nodes(v, me)


def load_ld(raw):
    out = []
    for txt in raw:
        txt = txt.strip().rstrip(";")
        try:
            out.append(json.loads(txt))
        except json.JSONDecodeError:
            try:
                out.append(json.loads(re.sub(r"[\x00-\x1f]", " ", txt)))
            except json.JSONDecodeError:
                continue
    return out


def text_of(v):
    if isinstance(v, dict):
        return text_of(v.get("text") or v.get("name") or "")
    if isinstance(v, list):
        return " ".join(text_of(x) for x in v)
    s = re.sub(r"\\?u003c/?\w*\\?u003e", " ", str(v or ""))  # thẻ HTML mất dấu \ khi plugin lưu schema
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def id_map(docs):
    """@id → object đầy đủ, để giải tham chiếu kiểu Yoast (mainEntity chỉ chứa {"@id": ...})."""
    out = {}

    def walk(o):
        if isinstance(o, list):
            for x in o:
                walk(x)
        elif isinstance(o, dict):
            if o.get("@id") and len(o) > 1:
                out.setdefault(o["@id"], o)
            for v in o.values():
                walk(v)
    walk(docs)
    return out


def resolve(o, ids):
    if isinstance(o, dict) and set(o) == {"@id"}:
        return ids.get(o["@id"], o)
    return o


def match_text(value, blocks, full, answer=False):
    """Điểm 0–1: mục có trong chữ hiển thị không. Câu hỏi so với khối ngắn; câu trả lời lấy 25 tiếng đầu."""
    q = norm(value)
    if not q:
        return 0.0, ""
    if answer:
        q = " ".join(q.split()[:25])
    if q in full:
        i = full.find(q)
        return 1.0, full[max(0, i - 40): i + len(q) + 80]
    tq = set(q.split())
    best, ev = 0.0, ""
    cap = max(3 * len(tq), len(tq) + 15)
    for b in blocks:
        tb = b["t"]
        if not answer and len(tb) > cap:
            continue
        c = len(tq & tb) / len(tq)
        if c > best:
            best, ev = c, b["raw"]
    return round(best, 3), ev[:300]


UNITS = {"tỷ": 10**9, "tỉ": 10**9, "triệu": 10**6, "tr": 10**6, "nghìn": 10**3, "ngàn": 10**3, "k": 10**3}


def numbers(text):
    """Số trong chữ hiển thị, bỏ dấu phân cách nghìn; giữ dạng thập phân và giá viết chữ (15 triệu, 1,5tr, 999k)."""
    out = set()
    for m in re.findall(r"\d[\d.,]*\d|\d", text):
        out.add(m)
        out.add(m.replace(",", "."))
        out.add(re.sub(r"[.,]", "", m))
    for num, unit in re.findall(r"(\d+(?:[.,]\d+)?)\s*(tỷ|tỉ|triệu|tr|nghìn|ngàn|k)(?![\wà-ỹ])", text, re.I):
        try:
            out.add(str(round(float(num.replace(",", ".")) * UNITS[unit.lower()])))
        except (ValueError, KeyError):
            continue
    return out


def fmt_num(v):
    try:
        f = float(str(v).replace(",", "."))
    except ValueError:
        return None
    return str(int(f)) if f == int(f) else str(f)


def yt_id(s):
    m = re.search(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/|vi/)|youtu\.be/|i\.ytimg\.com/vi/)([\w-]{11})", s or "")
    return m.group(1) if m else None


def items_for(node, types, page):
    t = types[0]
    full, blocks, nums = page["full"], page["blocks"], page["nums"]
    items = []
    if "FAQPage" in types or "QAPage" in types:
        ents = node.get("mainEntity") or []
        ents = ents if isinstance(ents, list) else [ents]
        for e in ents:
            e = resolve(e, page["ids"])
            if not isinstance(e, dict):
                continue
            qtext = text_of(e.get("name") or e.get("text"))
            qs, ev = match_text(qtext, blocks, full)
            ans = resolve(e.get("acceptedAnswer") or e.get("suggestedAnswer"), page["ids"])
            atext = text_of(ans) if ans else ""
            as_, aev = match_text(atext, blocks, full, answer=True) if atext.strip() else (1.0, "")
            # Cặp hỏi–đáp đạt khi câu hỏi hiện ra và phần đầu câu trả lời cũng hiện ra.
            items.append({"kind": "qa", "value": qtext[:200], "answer": atext[:200], "score": min(qs, as_),
                          "q_score": qs, "a_score": as_, "evidence": ev, "a_evidence": aev[:200]})
    elif "HowTo" in types:
        steps = node.get("step") or []
        steps = steps if isinstance(steps, list) else [steps]
        for st in steps:
            st = resolve(st, page["ids"])
            v = text_of(st.get("name") or st.get("text")) if isinstance(st, dict) else text_of(st)
            s, ev = match_text(v, blocks, full)
            items.append({"kind": "step", "value": v[:200], "score": s, "evidence": ev})
    elif "Review" in types:
        body = text_of(node.get("reviewBody") or node.get("description"))
        if body.strip():
            s, ev = match_text(body, blocks, full, answer=True)
            items.append({"kind": "review", "value": body[:200], "score": s, "evidence": ev})
    elif "AggregateRating" in types:
        r = fmt_num(node.get("ratingValue"))
        if r:
            dec = "." in r
            pat = re.escape(r).replace(r"\.", "[.,]")
            near = re.search(rf"(?<![\d.,]){pat}(?![\d])\s*(/\s*5|/\s*10|★|⭐|sao|stars?|điểm)", page["text"], re.I)
            ok = (dec and r in nums) or bool(near)
            items.append({"kind": "rating", "value": r, "score": 1.0 if ok else 0.0, "evidence": ""})
        c = node.get("reviewCount") or node.get("ratingCount")
        c = fmt_num(c) if c is not None else None
        if c and len(c) >= 2:
            items.append({"kind": "count", "value": c, "score": 1.0 if c in nums else 0.0, "evidence": ""})
    elif t in ("Offer", "AggregateOffer") or "Offer" in types:
        p = fmt_num(node.get("price") or node.get("lowPrice"))
        if p and p != "0":
            items.append({"kind": "price", "value": p, "score": 1.0 if p.split(".")[0] in nums else 0.0, "evidence": ""})
    elif "VideoObject" in types:
        refs = [str(node.get(k) or "") for k in ("embedUrl", "contentUrl", "url", "thumbnailUrl")]
        vid = next((yt_id(x) for x in refs if yt_id(x)), None)
        media = page["media"]
        ok = bool(vid and vid in media) or any(x and x in media for x in refs[:2])
        items.append({"kind": "video", "value": vid or refs[0][:120], "score": 1.0 if ok else 0.0, "evidence": ""})
    return items


def verdict(items):
    main = [i for i in items if i["kind"] != "answer"] or items
    if not items or not any(i["value"].strip() for i in main):
        return "empty"
    found = sum(i["score"] >= FOUND for i in main)
    miss = sum(i["score"] < NEAR for i in main)
    if found == len(main):
        return "all"
    if miss == len(main):
        # Câu hỏi hiện nhưng câu trả lời không khớp: vẫn FAIL, nhưng hướng sửa khác với trang không có FAQ.
        return "partial" if any(i.get("q_score", 0) >= FOUND for i in main) else "none"
    if found + miss == len(main) and found:
        return "some"
    return "unclear"


def parse_page(html, url):
    p = Page()
    try:
        p.feed(html)
        p.close()
    except Exception:  # HTML hỏng vẫn lấy phần đã đọc
        p.flush()
    text = " ".join(p.blocks)
    blocks = [{"raw": b, "t": toks(b)} for b in p.blocks if len(b) > 2]
    media = " ".join(p.media) + " " + re.sub(r"<script[^>]*ld\+json[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    faq = ""
    for i, b in enumerate(p.blocks):
        if len(b) < 120 and FAQ_HEAD.search(b):
            faq = " | ".join(p.blocks[i: i + 40])[:2500]
            break
    ld = load_ld(p.ld)
    return {"url": url, "text": text, "full": norm(text), "blocks": blocks, "nums": numbers(text),
            "heads": p.heads, "media": media, "ld": ld, "ids": id_map(ld), "faq": faq}


def extract_page(html, url):
    page = parse_page(html, url)
    pid = hashlib.sha1(url.encode()).hexdigest()[:12]
    out, n = [], 0
    keep = TEXT_TYPES | {"AggregateRating", "Offer", "AggregateOffer", "VideoObject"}
    for doc in page["ld"]:
        for node, types, parent in nodes(doc):
            if not keep & set(types):
                continue
            items = items_for(node, types, page)
            if not items:
                continue
            n += 1
            typ = next(t for t in types if t in keep)
            v = verdict(items)
            out.append({"id": f"{pid}#{n}", "url": url, "type": typ, "parent_type": parent, "items": items,
                        "det": v, "jev_needed": typ in TEXT_TYPES and v in ("some", "unclear"),
                        "self_serving": typ == "AggregateRating" and parent in SELF_TYPES,
                        "headings": page["heads"][:60] if typ in TEXT_TYPES else [],
                        "faq_section": page["faq"] if typ in TEXT_TYPES else "",
                        "visible_chars": len(page["text"])})
    return out


def read_pages(a):
    if a.html_dir:
        for f in sorted(Path(a.html_dir).glob("*.html")):
            u = f.with_suffix(".url")
            url = u.read_text(encoding="utf-8").strip() if u.exists() else f.stem
            yield url, f.read_text(encoding="utf-8", errors="ignore")
    else:
        save = Path(a.save_dir) if a.save_dir else None
        if save:
            save.mkdir(parents=True, exist_ok=True)
        for url in [l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()]:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (technical-seo-audit schema check)"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    html = r.read(5_000_000).decode("utf-8", errors="ignore")
            except Exception as e:  # mạng lỗi: ghi lại, không dừng cả lượt
                print(f"lỗi tải {url}: {e}", file=sys.stderr)
                continue
            if save:
                h = hashlib.sha1(url.encode()).hexdigest()[:16]
                (save / f"{h}.html").write_text(html, encoding="utf-8")
                (save / f"{h}.url").write_text(url, encoding="utf-8")
            yield url, html


def cmd_extract(a):
    rows = []
    for url, html in read_pages(a):
        rows.extend(extract_page(html, url))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} khối -> {a.out}", file=sys.stderr)


def jev_state(b):
    main = [i for i in b["items"] if i["kind"] != "answer"][:12]
    marked = [f"Q: {i['value'][:160]} | A: {i.get('answer', '')[:160]}" if i["kind"] == "qa" else i["value"][:240]
              for i in main]
    return {"url": b["url"], "schema_type": b["type"],
            "marked_up": marked,
            "page_headings": [h[:120] for h in b["headings"][:60]],
            "faq_section": b["faq_section"][:2500],
            "closest_passages": [i["evidence"][:200] + (" … " + i["a_evidence"][:150] if i.get("a_evidence") else "")
                                 for i in main]}


def cmd_prepare(a):
    n = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for b in map(json.loads, Path(a.blocks).read_text(encoding="utf-8").splitlines()):
            if b["type"] in TEXT_TYPES and b["det"] != "empty" and (a.all or b["jev_needed"]):
                f.write(json.dumps({"id": b["id"], "state": jev_state(b)}, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n} khối gửi Jev -> {a.out}", file=sys.stderr)


def decide(b, jev, fail_gate=None, pass_gate=None):
    """Trạng thái cuối của một khối.

    Luật tất định chốt trước: mọi mục khớp nguyên văn → ĐẠT; không mục nào hiện hoặc schema rỗng → FAIL.
    Khối chữ còn lại: Jev p(partial) + p(none) từ fail_gate → FAIL; FAQ có p(all) từ pass_gate → ĐẠT;
    dưới cổng thì Claude đọc. Khối số (rating, giá, video) không gửi Jev: Jev kém so số.
    """
    v, src = b["det"], "luật"
    if b["type"] in TEXT_TYPES and v not in ("all", "none", "partial", "empty"):
        pr = (((jev.get(b["id"]) or {}).get("answers") or {}).get("shown") or {}).get("probabilities") or {}
        p_fail = pr.get("partial", 0) + pr.get("none", 0)
        if pr and fail_gate is not None and p_fail >= fail_gate:
            v, src = ("none" if pr.get("none", 0) > pr.get("partial", 0) else "partial"), f"jev p_fail {p_fail:.2f}"
        elif pr and pass_gate is not None and b["type"] != "HowTo" and pr.get("all", 0) >= pass_gate:
            v, src = "all", f"jev p_all {pr['all']:.2f}"
        else:
            v, src = "review", "Claude đọc"
    status = {"all": "ĐẠT", "some": "FAIL", "partial": "FAIL", "none": "FAIL", "empty": "FAIL"}.get(v, "CẦN XEM")
    if b["type"] not in TEXT_TYPES and v == "unclear":
        status = "CẦN XEM"
    note = "Google bỏ qua review tự đánh giá cho Organization/LocalBusiness" if b.get("self_serving") else ""
    if v == "empty":
        note = "schema khai báo mục rỗng"
    return status, v, src, note


def cmd_decide(a):
    jev = {}
    if a.jev:
        for l in Path(a.jev).read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                jev[r["id"]] = r
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("id\turl\ttype\tparent\tstatus\tshown\tsource\tmissing\tnote\n")
        for b in map(json.loads, Path(a.blocks).read_text(encoding="utf-8").splitlines()):
            status, v, src, note = decide(b, jev, a.fail_gate, a.pass_gate)
            miss = "; ".join(f"{i['kind']}: {i['value'][:60]}" for i in b["items"]
                             if i["kind"] != "answer" and i["score"] < NEAR)[:400]
            f.write("\t".join([b["id"], b["url"], b["type"], str(b.get("parent_type") or ""), status, v, src,
                               miss, note]) + "\n")
    print(f"-> {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    g = e.add_mutually_exclusive_group(required=True)
    g.add_argument("--html-dir")
    g.add_argument("--urls")
    e.add_argument("--save-dir")
    e.add_argument("--out", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--blocks", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--all", action="store_true", help="gửi mọi khối chữ, dùng khi hiệu chuẩn")
    d = sub.add_parser("decide")
    d.add_argument("--blocks", required=True)
    d.add_argument("--jev")
    d.add_argument("--fail-gate", type=float, default=None, help="cổng p(partial)+p(none) của rubric schema-visible trong registry")
    d.add_argument("--pass-gate", type=float, default=None, help="cổng p(all) cho FAQ; để trống khi registry chưa có")
    d.add_argument("--out", required=True)
    a = ap.parse_args()
    {"extract": cmd_extract, "prepare": cmd_prepare, "decide": cmd_decide}[a.cmd](a)


if __name__ == "__main__":
    main()
