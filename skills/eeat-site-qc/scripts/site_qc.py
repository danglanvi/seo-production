#!/usr/bin/env python3
"""QC E-E-A-T toàn site theo checklist Aleyda Solis: code chấm check tất định, Jev + EmbeddingGemma cho tín hiệu,
Claude đọc mọi Does not meet. Định tuyến 83 check: references/routing.json.

  code     --pages pages.jsonl --html-dir <store>/html --out code.jsonl [--robots robots.txt] [--lang vi] [--year 2026]
           Cần beautifulsoup4 (python3 -E). Thư mục HTML là cache của extract.py (<key>.html + <key>.url).
  prepare  --rows rows.jsonl --pages pages.jsonl --rubric <eeat-page-core|eeat-review|eeat-ai-spam|eeat-ymyl-flag>
           --out jev_in.jsonl [--core core_out.jsonl] [--urls urls.txt] [--max-chars 12000] [--site-name TÊN]
           eeat-review chỉ lấy trang Jev xếp review; eeat-ymyl-flag chỉ lấy trang ymyl_topic khác none (cần --core).
  report   --pages pages.jsonl --out-dir DIR [--code code.jsonl] [--jev a.jsonl,b.jsonl] [--effort pages.jsonl]
           [--dup pages.jsonl] [--topical pages.jsonl] [--claims claims.jsonl] [--presets core,ai_assisted]
           [--registry model-calibration.json --site <domain>] [--sample 0.1 --seed 7]
           Ra trang-thai.csv, doc-lai.tsv, bang-chung-can-lay.md, report.md.
  merge    --status trang-thai.csv --read doc-lai.tsv --out trang-thai-chot.csv
           Cột ket_luan_claude: "<trạng thái> | <bằng chứng>". Meets, Does not meet, Not applicable cần bằng chứng.
Mã thoát: 0 xong · 2 input hỏng.
"""
import argparse
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parents[1]
ROUTING = HERE / "references" / "routing.json"
TASKS = HERE / "tasks"
CHECKLIST = HERE.parent / "semantic-content-audit" / "references" / "eeat-checklist"
STATUSES = ["Does not meet", "Partly meets", "Not assessed", "Meets", "Not applicable"]
OPPOSITE = {"Does not meet": "Meets", "Meets": "Does not meet"}
ATTRIBUTION = ("Assessment based on Google's Content Quality, E-E-A-T, Helpfulness & Page Experience Checklist by "
               "Aleyda Solis · Orainti & SEOFOMO (https://docs.google.com/spreadsheets/d/"
               "12-F9Z4NzDADOFRQtOiN-CtjY2aaqj-R5CcrJNCuTha4/). Stay up to date with SEO and AI search with SEOFOMO: "
               "https://seofomo.co/")
# Câu lệnh gửi AI (không phải câu nhắc tên AI): tab, accordion ẩn có chữ "ChatGPT" là bình thường.
AI_TEXT = re.compile(r"ignore (all |any )?(previous|prior|above) (instructions|prompts)|bỏ qua (mọi |các |tất cả )?(hướng dẫn|chỉ dẫn)|"
                     r"(chatgpt|gemini|claude|perplexity|copilot|llm|ai|assistant|language model|trợ lý|mô hình)[^.!?\n]{0,40}"
                     r"(hãy|phải|luôn|please|must|should|always)[^.!?\n]{0,30}(giới thiệu|đề xuất|khuyên|xếp|recommend|rank|mention|cite|trích)|"
                     r"(khi|nếu) (được )?(người dùng|ai đó|user) hỏi[^.!?\n]{0,60}(trả lời|giới thiệu|đề xuất)|"
                     r"recommend \S+( \S+)? as the (best|top)", re.I)
HIDDEN = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(px|pt|em)?\s*(;|$)|"
                    r"opacity\s*:\s*0(\.0+)?\s*(;|$)", re.I)
PLACEHOLDER = re.compile(r"lorem ipsum|\bTODO\b|\[IMG-?\d|nội dung đang (được )?cập nhật|đang cập nhật nội dung", re.I)
TEMPLATE_VAR = re.compile(r"%%?[a-z_]+%%?|\{\{[^}]{1,40}\}\}", re.I)
VI_CHARS = set("ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ")
AFF_KEYS = {"aff", "aff_id", "affid", "affiliate", "aff_sub", "partner", "clickid", "click_id"}
AFF_HOSTS = re.compile(r"accesstrade|isclix|go\.isclix|shope\.ee|s\.shopee|amzn\.to|tiki\.vn/.*\?.*(src|spid)|"
                       r"lazada.*(aff|laz_trackid)|c\.lazada|ecomobi|masoffer|clickbank|impact\.com|awin1", re.I)
CONTACT = re.compile(r"lien-he|contact|gioi-thieu|about|ve-chung-toi", re.I)
AUTHOR_HREF = re.compile(r"/(author|tac-gia|tacgia|chuyen-gia|team|doi-ngu)/", re.I)
YEAR = re.compile(r"\b(20\d\d)\b")
DATE_TXT = re.compile(r"(cập nhật|updated|ngày đăng|published)[^0-9]{0,20}(\d{1,2}[/.-]\d{1,2}[/.-](20\d\d))", re.I)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write_jl(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def die(msg):
    print(f"LỖI: {msg}", file=sys.stderr)
    sys.exit(2)


def load_checks():
    return {c["check_id"]: c for c in json.loads((CHECKLIST / "checklist.json").read_text(encoding="utf-8"))["checks"]}


def load_presets():
    return {k: v for k, v in json.loads((CHECKLIST / "presets.json").read_text(encoding="utf-8")).items() if k != "_note"}


def load_routing():
    return json.loads(ROUTING.read_text(encoding="utf-8"))["checks"]


# ---------- code ----------

def robots_rules(path):
    """Luật Disallow/Allow cho Googlebot (nhóm 'googlebot' nếu có, không thì '*')."""
    if not path:
        return None
    groups, cur, agents = defaultdict(list), [], []
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if cur:
                agents, cur = [], []
            agents.append(v.lower())
        elif k in ("allow", "disallow"):
            cur.append((k, v))
            for a in agents:
                groups[a] = cur
    return groups.get("googlebot") or groups.get("*") or []


def robots_allowed(rules, path):
    """Luật khớp dài nhất thắng; bằng nhau thì Allow thắng (cách Google đọc robots.txt)."""
    if rules is None:
        return None
    best, allowed = -1, True
    for k, v in rules:
        if not v:
            continue
        pat = "^" + re.escape(v).replace(r"\*", ".*").replace(r"\$", "$")
        if re.match(pat, path) and (len(v) > best or (len(v) == best and k == "allow")):
            best, allowed = len(v), k == "allow"
    return allowed


def ld_items(soup):
    out = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(s.string or "")
        except (json.JSONDecodeError, TypeError):
            out.append({"_invalid": True})
            continue
        stack = d if isinstance(d, list) else [d]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if "@graph" in x:
                    stack += x["@graph"]
                out.append(x)
            elif isinstance(x, list):
                stack += x
    return out


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def code_page(url, html, page, rules, lang, year):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    text = norm(soup.get_text(" "))
    R = {}

    def put(cid, status, evidence):
        R[cid] = {"status": status, "evidence": evidence}

    robots = norm(page.get("robots"))
    canon = page.get("canonical") or ""
    allowed = robots_allowed(rules, urlparse(url).path or "/")
    if "noindex" in robots:
        put("SP01", "Does not meet", f"meta robots: {robots}. Kiểm trang có cần index không")
    elif allowed is False:
        put("SP01", "Does not meet", "robots.txt chặn Googlebot")
    elif canon and canon.rstrip("/") != url.rstrip("/"):
        put("SP01", "Partly meets", f"canonical trỏ {canon}")
    elif allowed is None:
        put("SP01", "Not assessed", "không noindex, canonical tự trỏ; chưa kiểm robots.txt (thiếu --robots)")
    else:
        put("SP01", "Meets", "200, không noindex, canonical tự trỏ, robots.txt cho Googlebot vào")
    snip = [x for x in ("nosnippet", "max-snippet:0", "max-snippet: 0") if x in robots]
    dns = len(soup.select("[data-nosnippet]"))
    put("SP02", "Partly meets" if snip or dns else "Meets",
        f"robots {snip or 'không hạn chế snippet'}; data-nosnippet {dns} phần tử")

    items = [x for x in ld_items(soup)]
    if not items:
        put("SP03", "Not applicable", "Trang không có JSON-LD")
    elif any(x.get("_invalid") for x in items):
        put("SP03", "Does not meet", "JSON-LD lỗi cú pháp")
    else:
        bad = []
        for x in items:
            t = x.get("@type")
            t = t if isinstance(t, list) else [t]
            head = x.get("headline") or (x.get("name") if any(k in ("Article", "BlogPosting", "NewsArticle") for k in t) else None)
            if head and any(k in ("Article", "BlogPosting", "NewsArticle") for k in t):
                hw = set(norm(head).split())
                tw = set(norm(page.get("title", "") + " " + page.get("h1", "")).split())
                if hw and len(hw & tw) / len(hw) < 0.5:
                    bad.append(f"headline '{head[:60]}' lệch title/H1")
            au = x.get("author")
            for a in (au if isinstance(au, list) else [au] if au else []):
                n = a.get("name") if isinstance(a, dict) else a
                if isinstance(n, str) and n.strip() and norm(n) not in text:
                    bad.append(f"author '{n}' không hiện trên trang")
            if "FAQPage" in t:
                for q in x.get("mainEntity") or []:
                    qn = q.get("name") if isinstance(q, dict) else None
                    if qn and norm(qn)[:40] not in text:
                        bad.append(f"câu FAQ '{qn[:50]}' không hiện trên trang")
        put("SP03", "Does not meet" if bad else "Meets", "; ".join(bad[:3]) or f"{len(items)} mục JSON-LD khớp chữ hiển thị")

    put("PE04", "Meets" if url.startswith("https://") else "Does not meet",
        "HTTPS" if url.startswith("https://") else "URL không dùng HTTPS")
    mixed = [t.get("src") for t in soup.find_all(["img", "script", "iframe"], src=True) if t["src"].startswith("http://")]
    if mixed and url.startswith("https://"):
        put("PE04", "Partly meets", f"{len(mixed)} tài nguyên http:// (mixed content), ví dụ {mixed[0][:80]}")

    plang = (page.get("lang") or "").lower()
    # Đo trên title, H1, H2, đoạn đầu: header và footer của site song ngữ làm lệch số đo nếu lấy cả trang.
    main_txt = norm(" ".join([page.get("title") or "", page.get("h1") or "", " ".join(page.get("h2") or []),
                              page.get("first_para") or ""]))
    letters = [ch for ch in main_txt if ch.isalpha()]
    vi_share = sum(ch in VI_CHARS for ch in letters) / max(len(letters), 1)
    seen = "vi" if vi_share >= 0.03 else ("en" if vi_share < 0.005 else "trộn")
    if not letters:
        put("PS08", "Not assessed", "không có chữ chính để đo ngôn ngữ")
    elif seen == "trộn":
        put("PS08", "Partly meets", f"html lang='{plang or 'trống'}', title/H2/đoạn đầu trộn ngôn ngữ (ký tự Việt {vi_share:.1%})")
    else:
        put("PS08", "Meets" if plang.startswith(seen) else "Does not meet",
            f"html lang='{plang or 'trống'}', chữ chính đo là {seen} (ký tự Việt {vi_share:.1%})")

    head_txt = " ".join(page.get(k) or "" for k in ("title", "h1", "meta"))
    m = PLACEHOLDER.search(text) or TEMPLATE_VAR.search(head_txt)
    put("CQ07", "Does not meet" if m else "Meets",
        f"chữ giữ chỗ '{m.group(0)}'" if m else "không thấy chữ giữ chỗ ở thân trang, title, H1, meta")

    title = page.get("title", "") + " " + page.get("h1", "")
    t_years = {int(y) for y in YEAR.findall(title)}
    mod = [x.get("dateModified") for x in items if isinstance(x.get("dateModified"), str)]
    mod_year = max((int(d[:4]) for d in mod if d[:4].isdigit()), default=None)
    vis = DATE_TXT.findall(text)
    late = max((d[:10] for d in mod), default="") >= f"{year - 1}-11-01"
    if "currentyear" in title.lower():
        put("MT01", "Does not meet", "biến năm chưa thay trong title hoặc H1")
    elif year in t_years and (mod_year is None or (mod_year < year and not late)):
        put("MT01", "Does not meet", f"title/H1 có năm {year} nhưng dateModified {max(mod)[:10] if mod else 'không có'}")
    elif year in t_years and mod_year < year:
        put("MT01", "Not assessed", f"title/H1 năm {year}, dateModified {max(mod)[:10]} (cuối năm trước): so bản cũ để xác nhận")
    elif year in t_years:
        put("MT01", "Not assessed", f"title năm {year}, dateModified {mod[0][:10]}: so bản cũ để xác nhận thay đổi thật")
    elif vis or mod:
        put("MT01", "Not assessed", f"ngày hiển thị {vis[0][1] if vis else '—'}, dateModified {mod[0][:10] if mod else '—'}")
    else:
        put("MT01", "Not applicable", "trang không hiển thị ngày cập nhật, title không có năm")

    byl = [x.get("author") for x in items if x.get("author")]
    meta_a = soup.find("meta", attrs={"name": "author"})
    a_links = [a for a in soup.find_all("a", href=True) if AUTHOR_HREF.search(a["href"]) or "author" in (a.get("rel") or [])]
    cls = soup.select("[class*=author], [class*=tac-gia], .byline, [rel=author]")
    sig = [s for s, ok in (("schema author", byl), ("meta author", meta_a), ("link tác giả", a_links), ("khối tác giả", cls)) if ok]
    put("TA01", "Meets" if sig else "Not assessed", ", ".join(sig) if sig else "không thấy byline: kiểm trang có cần tác giả không")
    host0 = urlparse(url).netloc
    in_block = [a for el in cls for a in el.find_all("a", href=True)
                if urlparse(a["href"]).netloc in ("", host0) and urlparse(a["href"]).path.strip("/")]
    a_links = a_links or in_block
    put("TA02", "Meets" if a_links else ("Partly meets" if sig else "Not assessed"),
        f"link trang tác giả {a_links[0]['href'][:80]}" if a_links else "byline không link tới trang tác giả")

    links = soup.find_all("a", href=True)
    host = urlparse(url).netloc
    aff = []
    for a in links:
        h = a["href"]
        if not h.startswith("http") or urlparse(h).netloc == host:
            continue
        qs = {k.lower(): v for k, v in parse_qs(urlparse(h).query).items()}
        if AFF_HOSTS.search(h) or set(qs) & AFF_KEYS or "affiliate" in [x.lower() for x in qs.get("utm_medium", [])]:
            aff.append(a)
    if not aff:
        put("CP06", "Not applicable", "không thấy link affiliate")
        put("TA11", "Not applicable", "không thấy link affiliate")
    else:
        bare = [a for a in aff if not {"sponsored", "nofollow"} & set(a.get("rel") or [])]
        put("CP06", "Does not meet" if bare else "Meets",
            f"{len(bare)}/{len(aff)} link affiliate thiếu rel sponsored/nofollow" if bare else f"{len(aff)} link affiliate có rel")
        put("TA11", "Not assessed", f"{len(aff)} link affiliate: kiểm câu công khai quan hệ thương mại")

    hid = []
    for el in soup.find_all(style=HIDDEN):
        t = el.get_text(" ", strip=True)
        if AI_TEXT.search(t):
            hid.append(t[:120])
    for el in soup.select("[hidden], [aria-hidden=true]"):
        t = el.get_text(" ", strip=True)
        if AI_TEXT.search(t):
            hid.append(t[:120])
    put("CP07", "Does not meet" if hid else "Meets",
        f"chữ ẩn nhắm vào AI: '{hid[0]}'" if hid else "không thấy chữ ẩn nhắm vào AI")

    com = soup.select("#comments, .comments, .comment-list, .wpdiscuz-comment")
    if not com:
        put("CP10", "Not applicable", "không có khu bình luận")
    else:
        ext = [a for c in com for a in c.find_all("a", href=True)
               if a["href"].startswith("http") and urlparse(a["href"]).netloc != host]
        bare = [a for a in ext if not {"ugc", "nofollow"} & set(a.get("rel") or [])]
        put("CP10", "Does not meet" if bare else "Meets",
            f"{len(bare)} link ngoài trong bình luận thiếu rel ugc/nofollow" if bare else "link bình luận có rel ugc/nofollow")

    site = {"contact": any(CONTACT.search(a["href"]) for a in links),
            "tel": any(a["href"].startswith(("tel:", "mailto:")) for a in links)}
    return R, site


def cmd_code(a):
    try:
        import bs4  # noqa: F401
    except ImportError:
        die("cần beautifulsoup4 (chạy bằng python3 -E)")
    pages = {p["url"]: p for p in jl(a.pages)}
    html = {}
    for f in Path(a.html_dir).glob("*.url"):
        h = f.with_suffix(".html")
        if h.exists():
            html[f.read_text(encoding="utf-8").strip()] = h
    rules = robots_rules(a.robots)
    year = a.year or date.today().year
    out, site, missing = [], Counter(), 0
    titles, metas = Counter(), Counter()
    for p in pages.values():
        titles[norm(p.get("title"))] += 1
        metas[norm(p.get("meta"))] += 1
    for u, p in sorted(pages.items()):
        if u not in html:
            missing += 1
            continue
        res, s = code_page(u, html[u].read_text(encoding="utf-8", errors="ignore"), p, rules, a.lang, year)
        t, m = norm(p.get("title")), norm(p.get("meta"))
        if not m:
            res["AI04"] = {"status": "Does not meet", "evidence": "meta description trống"}
        elif titles[t] > 1 or metas[m] > 1:
            res["AI04"] = {"status": "Partly meets", "evidence": f"title trùng {titles[t]} trang, meta trùng {metas[m]} trang"}
        else:
            res["AI04"] = {"status": "Meets", "evidence": "title và meta riêng"}
        site.update(k for k, v in s.items() if v)
        out.append({"url": u, "checks": res})
    n = len(out)
    out.append({"url": "__site__", "checks": {"TA10": {
        "status": "Meets" if site["contact"] and site["tel"] else ("Partly meets" if site["contact"] or site["tel"] else "Does not meet"),
        "evidence": f"link liên hệ/giới thiệu trên {site['contact']}/{n} trang; tel/mailto trên {site['tel']}/{n} trang"}}})
    write_jl(a.out, out)
    print(f"code: {n} trang, thiếu HTML {missing} -> {a.out}", file=sys.stderr)


# ---------- prepare ----------

def choice_of(r, q):
    x = ((r.get("answers") or {}).get(q) or {})
    return x.get("choice"), x.get("probabilities") or {}


def cmd_prepare(a):
    task = TASKS / f"{a.rubric}.json"
    if not task.exists():
        die(f"rubric lạ: {a.rubric}")
    pages = {p["url"]: p for p in jl(a.pages)}
    want = {l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()} if a.urls else None
    keep = None
    if a.rubric in ("eeat-review", "eeat-ymyl-flag"):
        if not a.core:
            die(f"{a.rubric} cần --core (output Jev của eeat-page-core)")
        keep = set()
        for r in jl(a.core):
            if a.rubric == "eeat-review":
                c, pr = choice_of(r, "page_type")
                if c == "review" or pr.get("review", 0) >= 0.3:
                    keep.add(r["id"])
            else:
                c, pr = choice_of(r, "ymyl_topic")
                if c not in (None, "none") or pr.get("none", 1) <= 0.7:
                    keep.add(r["id"])
    secs = defaultdict(list)
    for r in jl(a.rows):
        if r["level"] != "section":
            continue
        m = re.search(r"#s(\d+)$", r["id"])
        secs[r["url"]].append((int(m.group(1)) if m else 0, r["text"]))
    out, short = [], 0
    for u, parts in sorted(secs.items()):
        if (want and u not in want) or (keep is not None and u not in keep):
            continue
        p = pages.get(u, {})
        body = "\n\n".join(t for _, t in sorted(parts))
        if len(body.split()) < 80:
            short += 1
            continue
        lang = "en" if (p.get("lang") or "").lower().startswith("en") else "vi"
        head = "\n".join(x for x in (p.get("title"), p.get("h1")) if x)
        out.append({"id": u, "state": {"lang": lang, "site": a.site_name or urlparse(u).netloc,
                                        "text": (head + "\n\n" + body)[:a.max_chars]}})
    write_jl(a.out, out)
    print(f"prepare {a.rubric}: {len(out)} trang, bỏ {short} trang dưới 80 chữ -> {a.out}", file=sys.stderr)


# ---------- report ----------

def find_defaults():
    for start in (Path.cwd(), HERE):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def gates(registry, site):
    """{(rubric, version, question): gate} từ registry site, rồi defaults."""
    g = {}
    for path, want in ((registry, site), (find_defaults(), None)):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("mode") == "jev" and (want is None or e.get("site") == want):
                k = (e.get("rubric"), e.get("version"), e.get("question"))
                if k not in g and (e.get("conf_gate") or e.get("threshold")):
                    g[k] = e.get("conf_gate") or e.get("threshold")
    return g


def worst(statuses):
    return min(statuses, key=STATUSES.index)


def jev_signal(sig, r, G, page_ctx):
    only = sig.get("only") or {}
    if "page_type" in only and page_ctx.get("page_type") not in only["page_type"]:
        return {"status": "Not applicable", "route": "mẫu", "source": "jev page_type",
                "evidence": f"Jev xếp loại trang {page_ctx.get('page_type') or 'chưa có'}"}
    if only.get("ymyl") and not page_ctx.get("ymyl"):
        return {"status": "Not applicable", "route": "mẫu", "source": "jev ymyl_topic", "evidence": "Jev xếp không YMYL"}
    if r is None:
        return None
    p = ((r.get("answers") or {}).get(sig["question"]) or {}).get("p_yes")
    if p is None:
        return {"status": "Not assessed", "route": "Claude đọc", "source": f"jev {sig['question']}",
                "evidence": r.get("error") or "Jev không trả lời"}
    gate = G.get((sig["rubric"], r.get("task_version"), sig["question"]))
    ev = f"{sig['question']} p={p:.2f}"
    if gate is None:
        st = sig["yes"] if p >= 0.5 else OPPOSITE[sig["yes"]]
        return {"status": st, "route": "Claude đọc", "source": "jev chưa hiệu chuẩn", "evidence": ev, "p": p}
    if p >= gate:
        st = sig["yes"]
    elif p <= 1 - gate:
        st = OPPOSITE[sig["yes"]]
    else:
        return {"status": "Not assessed", "route": "Claude đọc", "source": f"jev dải xám (cổng {gate})", "evidence": ev, "p": p}
    return {"status": st, "route": "Claude đọc" if st != "Meets" else "mẫu", "source": f"jev cổng {gate}",
            "evidence": ev, "p": p}


def reuse_signal(sig, u, R):
    f, field = sig["from"], sig["field"]
    x = (R.get(f) or {}).get(u)
    if x is None:
        return None
    if f == "effort" and field in ("original_data", "first_hand"):
        lab = x.get(field)
        st = {"yes": "Meets", "no": "Partly meets"}.get(lab, "Not assessed")
        return {"status": st, "route": "mẫu" if st == "Meets" else "Claude đọc", "source": f"content-effort {field}",
                "evidence": f"{field}={lab}"}
    if f == "effort":
        s = x.get("effort")
        if s is None:
            return None
        st = "Does not meet" if s == 0 else ("Partly meets" if s == 1 else "Meets")
        return {"status": st, "route": "mẫu" if st == "Meets" else "Claude đọc", "source": "content-effort effort",
                "evidence": f"effort={s}/3"}
    if f == "dup":
        d = x.get("dup_share", 0)
        st = "Does not meet" if d >= 0.5 else ("Partly meets" if d >= 0.2 else "Meets")
        return {"status": st, "route": "mẫu" if st == "Meets" else "Claude đọc", "source": "Gemma passage-dup (mốc nháp)",
                "evidence": f"dup_share={d:.0%}"}
    if f == "topical":
        out = bool(x.get("outlier"))
        return {"status": "Not assessed" if out else "Meets", "route": "Claude đọc" if out else "mẫu",
                "source": "Gemma topical-focus", "evidence": f"cos_site={x.get('cos_site')}, outlier={out}"}
    if f == "claims":
        n = x
        return {"status": "Partly meets" if n else "Meets", "route": "Claude đọc" if n else "mẫu",
                "source": "content-quality-lab claims", "evidence": f"{n} câu số liệu cần thêm nguồn"}
    return None


def cmd_report(a):
    checks, presets, routing = load_checks(), load_presets(), load_routing()
    pages = [p for p in jl(a.pages)]
    urls = [p["url"] for p in pages]
    code = {r["url"]: r["checks"] for r in jl(a.code)} if a.code else {}
    jev = defaultdict(dict)
    for f in (a.jev or "").split(","):
        if f:
            for r in jl(f):
                if r.get("task"):
                    jev[r["task"]][r["id"]] = r
    R = {}
    if a.effort:
        R["effort"] = {r["url"]: r for r in jl(a.effort)}
    if a.dup:
        R["dup"] = {r["url"]: r for r in jl(a.dup)}
    if a.topical:
        R["topical"] = {r["url"]: r for r in jl(a.topical)}
    if a.claims:
        c = Counter(r["url"] for r in jl(a.claims) if "thêm nguồn" in (r.get("de_xuat") or ""))
        R["claims"] = {u: c.get(u, 0) for u in {r["url"] for r in jl(a.claims)}}
    G = gates(a.registry, a.site)
    ctx = {}
    for u in urls:
        core = jev.get("eeat-page-core", {}).get(u)
        pt, _ = choice_of(core, "page_type") if core else (None, {})
        ym, _ = choice_of(core, "ymyl_topic") if core else (None, {})
        ctx[u] = {"page_type": pt, "ymyl": ym not in (None, "none")}
    names = [x for x in (a.presets or "core").split(",") if x]
    for n in names:
        if n not in presets:
            die(f"preset lạ: {n}")
    sel = list(presets["core"]["check_ids"])
    for n in names:
        sel += presets[n]["check_ids"]
    if any(c["page_type"] == "review" for c in ctx.values()):
        sel += presets["review"]["check_ids"]
    if any(c["ymyl"] for c in ctx.values()):
        sel += presets["ymyl"]["check_ids"]
    sel = list(dict.fromkeys(sel))
    tmpl = {u: ctx[u]["page_type"] or (urlparse(u).path.strip("/").split("/")[0] or "home") for u in urls}

    rows = []
    for cid in sel:
        scope = checks[cid]["review_scope"]
        sigs = routing[cid]
        lanes = {s["lane"] for s in sigs}
        if lanes <= {"claude", "evidence"} or scope in ("Site", "Workflow") and lanes & {"evidence"}:
            s0 = sigs[0]
            if scope in ("Site", "Workflow") or s0["lane"] == "evidence":
                rows.append({"target": "__site__" if scope != "Template" else "*", "template": "", "scope": scope,
                             "check_id": cid, "status": "Not assessed",
                             "route": "lấy bằng chứng" if s0["lane"] == "evidence" else "Claude đọc mẫu",
                             "source": s0["lane"] + (f" → {s0['skill']}" if s0.get("skill") else ""),
                             "evidence": s0.get("need") or s0.get("note"), "p": ""})
                continue
            for t in sorted(set(tmpl.values())):
                rows.append({"target": "*", "template": t, "scope": scope, "check_id": cid, "status": "Not assessed",
                             "route": "Claude đọc mẫu", "source": "claude", "evidence": s0.get("note"), "p": ""})
            continue
        if cid == "TA10":
            x = code.get("__site__", {}).get("TA10")
            rows.append({"target": "__site__", "template": "", "scope": scope, "check_id": cid,
                         "status": x["status"] if x else "Not assessed", "route": "Claude đọc" if x and x["status"] != "Meets" else "mẫu",
                         "source": "code", "evidence": x["evidence"] if x else "chưa chạy code", "p": ""})
            continue
        for u in urls:
            got = []
            for s in sigs:
                if s["lane"] == "code":
                    x = code.get(u, {}).get(cid)
                    if x:
                        rt = {"Meets": "tự chốt", "Not applicable": "tự chốt", "Not assessed": "Claude đọc mẫu"}.get(
                            x["status"], "Claude đọc")
                        got.append({**x, "route": rt, "source": "code"})
                elif s["lane"] == "jev":
                    g = jev_signal(s, jev.get(s["rubric"], {}).get(u), G, ctx[u])
                    if g:
                        got.append(g)
                elif s["lane"] == "reuse":
                    g = reuse_signal(s, u, R)
                    if g:
                        got.append(g)
            if not got:
                rows.append({"target": u, "template": tmpl[u], "scope": scope, "check_id": cid, "status": "Not assessed",
                             "route": "chưa chạy lane", "source": ",".join(sorted(lanes - {"claude", "evidence"})),
                             "evidence": "chưa có output của lane máy", "p": ""})
                continue
            applicable = [g for g in got if g["status"] != "Not applicable"]
            pick = min(applicable, key=lambda g: STATUSES.index(g["status"])) if applicable else got[0]
            route = "Claude đọc" if pick["status"] in ("Does not meet", "Partly meets") else pick["route"]
            if cid == "TA02" and pick["status"] != "Meets" and ctx[u]["page_type"] not in ("article", "review", "news"):
                route = "Claude đọc mẫu"  # trang dịch vụ, case, giới thiệu: không bắt link trang tác giả
            if cid == "TA01" and pick["status"] == "Not assessed":
                # Không byline: trang bài, review, tin cần tác giả; trang dịch vụ, sản phẩm thì Claude đọc mẫu.
                if ctx[u]["page_type"] in ("article", "review", "news"):
                    pick = {**pick, "status": "Does not meet"}
                    route = "Claude đọc"
                else:
                    route = "Claude đọc mẫu"
            rows.append({"target": u, "template": tmpl[u], "scope": scope, "check_id": cid, "status": pick["status"],
                         "route": route, "source": " + ".join(g["source"] for g in got),
                         "evidence": " | ".join(g["evidence"] for g in got), "p": pick.get("p", "")})

    rnd = random.Random(a.seed)
    for r in rows:
        if r["route"] == "mẫu":
            r["route"] = "Claude đọc (mẫu)" if rnd.random() < a.sample else "giữ đề xuất"
    # Dòng URL "Claude đọc mẫu": giữ 2 trang mỗi check × template, còn lại chờ kết luận của mẫu.
    grp = defaultdict(list)
    for r in rows:
        if r["route"] == "Claude đọc mẫu" and r["target"] not in ("__site__", "*"):
            grp[(r["check_id"], r["template"])].append(r)
    for g in grp.values():
        rnd.shuffle(g)
        for r in g[2:]:
            r["route"] = "theo mẫu"
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cols = ["target", "template", "scope", "check_id", "status", "route", "source", "p", "evidence"]
    with open(out / "trang-thai.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    order = {"Does not meet": 0, "Partly meets": 1, "Not assessed": 2, "Meets": 3, "Not applicable": 4}
    read = sorted((r for r in rows if r["route"].startswith("Claude")),
                  key=lambda r: (order[r["status"]], r["check_id"], -(r["p"] or 0) if r["p"] != "" else 0))
    with open(out / "doc-lai.tsv", "w", encoding="utf-8") as f:
        f.write("\t".join(cols + ["ket_luan_claude"]) + "\n")
        for r in read:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\t\n")
    ev = [r for r in rows if r["route"] == "lấy bằng chứng"]
    E = ["# Bằng chứng cần lấy", "", "Các check dưới đây không chấm được bằng chữ trên trang. Ghi Not assessed tới khi có bằng chứng.", ""]
    E += [f"- **{r['check_id']}** ({r['scope']}): {checks[r['check_id']]['question']} — {r['evidence']}"
          f"{' · skill: ' + r['source'].split('→ ')[1] if '→' in r['source'] else ''}" for r in ev]
    (out / "bang-chung-can-lay.md").write_text("\n".join(E) + "\n", encoding="utf-8")

    by = defaultdict(Counter)
    for r in rows:
        by[r["check_id"]][r["status"]] += 1
    L = ["# QC E-E-A-T toàn site (bản máy, chờ Claude chốt)", "",
         "Đây là đánh giá chuyên môn trên bằng chứng đã xem, không phải điểm của Google, không phải chứng nhận, "
         "không dự đoán thứ hạng hay lượt AI trích dẫn.", "",
         f"- Trang: {len(urls)} · check chọn: {len(sel)} (preset {', '.join(['core'] + [n for n in names if n != 'core'])})",
         f"- Dòng trạng thái: {len(rows)} · Claude cần đọc: {len(read)} · lấy bằng chứng: {len(ev)}",
         f"- Rubric Jev đã có cổng: {len({k[0] for k in G if k[0] and k[0].startswith('eeat-')}) or 'chưa'}; "
         "Jev chưa hiệu chuẩn thì mọi nhãn đi vào danh sách Claude đọc.", "",
         "| Check | Câu hỏi | Meets | Partly | Does not meet | Not assessed | N/A |", "|---|---|---|---|---|---|---|"]
    for cid in sel:
        c = by[cid]
        L.append(f"| {cid} | {checks[cid]['question']} | {c['Meets']} | {c['Partly meets']} | {c['Does not meet']} | "
                 f"{c['Not assessed']} | {c['Not applicable']} |")
    L += ["", "## Theo template", "", "| Template | Trang | Does not meet | Partly |", "|---|---|---|---|"]
    tc = Counter(tmpl.values())
    for t, n in tc.most_common():
        d = sum(1 for r in rows if r["template"] == t and r["status"] == "Does not meet" and r["target"] != "*")
        pm = sum(1 for r in rows if r["template"] == t and r["status"] == "Partly meets" and r["target"] != "*")
        L.append(f"| {t} | {n} | {d} | {pm} |")
    L += ["", "> " + ATTRIBUTION]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"report: {len(rows)} dòng, Claude đọc {len(read)}, lấy bằng chứng {len(ev)} -> {out}", file=sys.stderr)


def cmd_merge(a):
    rows = list(csv.DictReader(Path(a.status).read_text(encoding="utf-8").splitlines()))
    idx = {(r["target"], r["template"], r["check_id"]): r for r in rows}
    done, open_err = 0, 0
    lines = Path(a.read).read_text(encoding="utf-8").splitlines()
    head = lines[0].split("\t")
    for n, line in enumerate(lines[1:], start=2):
        d = dict(zip(head, line.split("\t")))
        k = (d.get("target"), d.get("template"), d.get("check_id"))
        kl = (d.get("ket_luan_claude") or "").strip()
        if not kl:
            if d.get("status") in ("Does not meet", "Partly meets"):
                open_err += 1
            continue
        st, _, ev = (x.strip() for x in kl.partition("|"))
        if st not in STATUSES:
            die(f"doc-lai dòng {n}: trạng thái lạ '{st}'")
        if st in ("Meets", "Does not meet", "Not applicable") and not ev:
            die(f"doc-lai dòng {n}: {k[2]} {st} thiếu bằng chứng")
        if k not in idx:
            die(f"doc-lai dòng {n}: không có dòng {k} trong trang-thai.csv")
        r = idx[k]
        r.update(status=st, route="Claude chốt", evidence=f"{ev} (máy: {r['status']}; {r['evidence']})")
        done += 1
    cols = list(rows[0].keys()) if rows else []
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"merge: Claude chốt {done} dòng; lỗi máy chưa đọc {open_err} -> {a.out}", file=sys.stderr)
    if open_err:
        print("CẢNH BÁO: còn dòng Does not meet/Partly meets chưa có kết luận của Claude (Gate).", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("code")
    c.add_argument("--pages", required=True)
    c.add_argument("--html-dir", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--robots")
    c.add_argument("--lang", default="vi")
    c.add_argument("--year", type=int)
    p = sub.add_parser("prepare")
    p.add_argument("--rows", required=True)
    p.add_argument("--pages", required=True)
    p.add_argument("--rubric", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--core")
    p.add_argument("--urls")
    p.add_argument("--max-chars", type=int, default=12000)
    p.add_argument("--site-name")
    r = sub.add_parser("report")
    r.add_argument("--pages", required=True)
    r.add_argument("--out-dir", required=True)
    for k in ("code", "jev", "effort", "dup", "topical", "claims", "registry", "site"):
        r.add_argument(f"--{k}")
    r.add_argument("--presets", default="core")
    r.add_argument("--sample", type=float, default=0.1)
    r.add_argument("--seed", type=int, default=7)
    m = sub.add_parser("merge")
    m.add_argument("--status", required=True)
    m.add_argument("--read", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args()
    {"code": cmd_code, "prepare": cmd_prepare, "report": cmd_report, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    main()
