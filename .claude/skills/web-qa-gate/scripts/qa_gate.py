#!/usr/bin/env python3
"""web-qa-gate: kiểm site sau mỗi lần ghi, ra report.json + report.md có PASS/FAIL theo 14 hạng mục có script (hạng mục 12 chữ dễ đọc kiểm tay).

Một lệnh chạy đủ cổng (Python stdlib + curl + node; Pillow tuỳ chọn để đệm ảnh cho Jev):
  python3 -E qa_gate.py run --config qa.json --out <thư mục> [--jev] [--jev-budget 0.1] [--skip browser,http,jev]
  python3 -E qa_gate.py run --base https://stg.example.vn --urls urls.tsv --out <thư mục>      # không cần config
Dựng lại report từ dữ liệu đã thu (không gọi mạng):
  python3 -E qa_gate.py report --config qa.json --out <thư mục> [--mail-ok <token> | --mail-missing <token>]
Chạy lại phân tích một hạng mục trên file đã lưu (lượt thử, dữ liệu cũ):
  python3 -E qa_gate.py check overflow ux.jsonl [--widths 360,390,768,1366]
  python3 -E qa_gate.py check axe <file/thư mục ...>       python3 -E qa_gate.py check focus <file/thư mục ...>
  python3 -E qa_gate.py check http httpcheck.txt            python3 -E qa_gate.py check plugins <staging> <production>
  python3 -E qa_gate.py check html <thư mục html> [--urls urls.tsv] [--canonical-host h] [--expect-tracking GTM-X]
  python3 -E qa_gate.py check ui-visual jev-out.jsonl [--registry r.json] [--site domain]
Hạng mục 13 (tương tác), 14 (bố cục, landmark), 15 (Open Graph): khai khối "interact" trong qa.json để chạy 13 và 14; 15 chạy từ HTML server.
  python3 -E qa_gate.py check interact interact.jsonl [--config qa.json]   python3 -E qa_gate.py check layout interact.jsonl [--landmarks landmarks.jsonl]
  python3 -E qa_gate.py check og <thư mục html> [--canonical-host h]
Quét nhiều URL (run): --tabs N (Chrome song song), --resume (không đo lại dòng đã tốt), --sample N|P% [--seed S], --cache cached|nc|both, --page-timeout ms.
Gửi form thật (tạo lead thật, gửi mail thật): run --submit-live, cần WEB_QA_SUBMIT_LIVE=<host>; production cần thêm --approved.
"""
import argparse
import datetime as dt
import fnmatch
import glob
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import qa_extra  # noqa: E402  (cùng thư mục: hạng mục 13 đến 15, lấy mẫu, phủ ảnh chụp)

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 web-qa-gate"
DEFAULT_WIDTHS = [360, 768, 1366]
TRACKING_BLOCK = ["*googletagmanager.com*", "*google-analytics.com*", "*analytics.google.com*", "*googleadservices.com*",
                  "*doubleclick.net*", "*facebook.net*", "*facebook.com/tr*", "*clarity.ms*", "*hotjar.com*",
                  "*analytics.tiktok.com*", "*script.google.com*"]
CATS = [("overflow", "Tràn ngang"), ("axe", "Axe (a11y)"), ("focus", "Focus bàn phím"), ("form", "Form"),
        ("tracking", "Tracking"), ("plugins", "Plugin staging = production"), ("http", "Mã HTTP"),
        ("redirect", "Redirect"), ("canonical", "Canonical"), ("schema", "Schema"), ("ui_visual", "Jev ui-visual"),
        ("interact", "Tương tác và trạng thái"), ("layout", "Toàn vẹn bố cục"), ("og", "Open Graph")]
NOULS = ("cut_off", "fixed_covers", "overlap", "empty_control", "media_problem", "spacing")
RANK = {"FAIL": 3, "WARN": 2, "PASS": 1, "SKIP": 0}


def cat(status, summary, findings=None, notes=None):
    return {"status": status, "summary": summary, "findings": findings or [], "notes": notes or []}


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def files_in(paths, exts=(".json", ".jsonl")):
    out = []
    for p in map(Path, paths):
        out += sorted(x for x in p.iterdir() if x.suffix in exts) if p.is_dir() else [p]
    return out


def records(paths):
    """Đọc .json (một object hoặc list) và .jsonl. Gắn tên file vào _file."""
    out = []
    for f in files_in(paths):
        text = f.read_text(encoding="utf-8")
        rows = jl(f) if f.suffix == ".jsonl" else json.loads(text)
        for r in rows if isinstance(rows, list) else [rows]:
            out.append({**r, "_file": f.stem})
    return out


# ---------- 1. Tràn ngang ----------

def check_overflow(rows, widths=None, tol=0):
    """So bề rộng tài liệu với bề rộng đặt (vw). Dòng cũ của ux_probe.mjs không có vw: gán theo --widths, đúng thứ tự đo.
    Dòng có variant (cached, nc, default) được đo và báo riêng: lỗi chỉ ở bản có cache hay chỉ ở bản bỏ cache là hai lỗi khác nhau."""
    findings, errs, n, legacy = [], [], 0, False
    order = defaultdict(int)
    variants = set()
    for r in rows:
        name = r.get("name") or r.get("_file")
        var = r.get("variant")
        vw = r.get("vw")
        if vw is None and widths:
            i = order[name]
            order[name] += 1
            vw = widths[i] if i < len(widths) else None
        if vw is None:
            vw, legacy = r.get("W"), True
        if r.get("err") or r.get("docW") is None or vw is None:
            errs.append(f"{name} {vw}{' ' + var if var else ''}: {r.get('err') or 'thiếu số đo'}")
            continue
        n += 1
        if var:
            variants.add(var)
        actual = max(r.get("docW") or 0, r.get("innerW") or r.get("W") or 0)
        if actual - vw > tol:
            f = {"page": name, "width": vw, "over_px": actual - vw, "doc_width": actual, "level": "FAIL",
                 "offenders": [f"{o.get('s')} (mép phải {o.get('r')})" for o in (r.get("overflow") or [])[:4]]}
            if var:
                f["variant"] = var
                if r.get("cache"):
                    f["cache"] = r["cache"]
            findings.append(f)
    notes = [f"đo lỗi: {e}" for e in errs]
    if legacy:
        notes.append("Có dòng không rõ bề rộng đặt: đã so với innerWidth. Giả lập mobile nới innerWidth theo phần tràn, nên lỗi có thể bị che.")
    real = variants - {"default"}
    if "default" in variants or not variants:
        notes.append("Tải đúng URL đã cho, chưa rõ đo bản có cache hay bản bỏ cache. Thêm --cache both để đo cả hai: CSS, JS đã tối ưu của plugin cache có thể tràn mà bản bỏ cache không tràn, và ngược lại.")
    elif len(real) == 1:
        notes.append(f"Chỉ đo bản {next(iter(real))}. Thêm --cache both để đo cả bản có cache và bản bỏ cache.")
    if len(real) > 1:
        by = defaultdict(set)
        for f in findings:
            by[f.get("variant")].add((f["page"], f["width"]))
        for v in sorted(real):
            only = by[v] - set().union(*(by[o] for o in real if o != v))
            if only:
                notes.append(f"Tràn chỉ ở bản {v}: " + ", ".join(f"{p} {w}px" for p, w in sorted(only)[:8]))
    if not n and not errs:
        return cat("SKIP", "không có số đo", notes=notes)
    worst = max((f["over_px"] for f in findings), default=0)
    status = "FAIL" if findings else ("WARN" if errs else "PASS")
    return cat(status, f"{len(findings)}/{n} lượt đo tràn ngang" + (f", lớn nhất +{worst} px" if findings else ""),
               sorted(findings, key=lambda f: (-f["over_px"], f["page"])), notes)


# ---------- 2. Axe ----------

def axe_records(objs):
    """Nhận 3 dạng: dòng của browser_probe (axe), dòng axe_run.mjs (dev, v), file JSON axe đầy đủ (path, w, violations)."""
    out = []
    for o in objs:
        page = o.get("name") or o.get("path") or o.get("_file")
        width = o.get("vw") or o.get("w") or o.get("dev")
        if "axe" in o:
            if o["axe"] is None:
                continue
            viol, err = o["axe"].get("violations"), o["axe"].get("err")
        elif "v" in o:
            viol, err = o["v"], None if o["v"] is not None else "axe không chạy"
        elif "violations" in o:
            viol, err = o["violations"], None
        else:
            continue
        out.append({"page": page, "width": width, "violations": viol or [], "err": err})
    return out


def check_axe(recs, fail_impacts=("critical", "serious"), ignore=()):
    if not recs:
        return cat("SKIP", "không có kết quả axe")
    rules = {}
    errs = [f"{r['page']} {r['width']}: {r['err']}" for r in recs if r["err"]]
    for r in recs:
        for v in r["violations"]:
            if v["id"] in ignore:
                continue
            x = rules.setdefault(v["id"], {"rule": v["id"], "impact": v.get("impact"), "pages": set(), "nodes": 0, "examples": []})
            x["pages"].add(f"{r['page']}@{r['width']}")
            x["nodes"] += v.get("n") or len(v.get("nodes") or [])
            for e in (v.get("ex") or v.get("nodes") or [])[:2]:
                t = e.get("t") if isinstance(e, dict) else str(e)
                if t and len(x["examples"]) < 3 and t not in x["examples"]:
                    x["examples"].append(t if isinstance(t, str) else " ".join(t))
    findings = []
    for x in rules.values():
        lvl = "FAIL" if x["impact"] in fail_impacts else "WARN"
        findings.append({**x, "pages": len(x["pages"]), "level": lvl})
    findings.sort(key=lambda f: (-RANK[f["level"]], -f["nodes"]))
    nf = sum(f["level"] == "FAIL" for f in findings)
    status = "FAIL" if nf else ("WARN" if findings or errs else "PASS")
    by_imp = defaultdict(int)
    for f in findings:
        by_imp[f["impact"]] += 1
    summ = f"{len(recs)} lượt, {len(findings)} luật vi phạm" + (" (" + ", ".join(f"{k} {v}" for k, v in sorted(by_imp.items())) + ")" if findings else "")
    return cat(status, summ, findings, [f"axe lỗi: {e}" for e in errs] + [f"bỏ qua luật: {', '.join(ignore)}"] * bool(ignore))


# ---------- 3. Focus ----------

SKIP_RE = re.compile(r"skip|bỏ qua|nội dung chính|main content", re.I)


def focus_records(objs):
    out = []
    for o in objs:
        if "focus" in o:
            if o["focus"]:
                out.append({"page": o.get("name"), "width": o.get("vw"), "items": o["focus"].get("items") or []})
        elif "items" in o:
            out.append({"page": o.get("_file") or o.get("url"), "width": o.get("w"), "items": o["items"]})
    return out


def check_focus(recs):
    if not recs:
        return cat("SKIP", "không có lượt bấm Tab")
    findings, offview = [], 0
    for r in recs:
        it = r["items"]
        if not it:
            findings.append({"page": r["page"], "width": r["width"], "level": "FAIL", "issue": "không phần tử nào nhận focus"})
            continue
        # changed (bản đo mới): style có đổi khi mất focus. Bản đo cũ không có changed: dựa vào outline, box-shadow.
        no_ind = [i["sig"] for i in it if not i.get("hidden") and
                  (i.get("changed") is False or (i.get("changed") is None and not i.get("outline") and not i.get("shadow")))]
        hidden = [i["sig"] for i in it if i.get("hidden")]
        offview += sum(1 for i in it if i.get("inview") is False and not i.get("hidden"))
        first = it[0]
        skip_ok = bool(SKIP_RE.search(f"{first.get('txt', '')} {first.get('sig', '')}"))
        if no_ind:
            findings.append({"page": r["page"], "width": r["width"], "level": "FAIL", "issue": f"{len(no_ind)} phần tử nhận focus không đổi hiển thị (outline, viền, nền, bóng)", "examples": no_ind[:4]})
        if hidden:
            findings.append({"page": r["page"], "width": r["width"], "level": "FAIL", "issue": f"{len(hidden)} phần tử ẩn vẫn nhận focus", "examples": hidden[:4]})
        if not skip_ok:
            findings.append({"page": r["page"], "width": r["width"], "level": "WARN", "issue": "phần tử nhận focus đầu tiên không phải skip link", "examples": [first.get("sig")]})
    status = max((f["level"] for f in findings), key=RANK.get, default="PASS")
    total = sum(len(r["items"]) for r in recs)
    notes = ["Script so style lúc có và không có focus."]
    if any(i.get("changed") is None for r in recs for i in r["items"]):
        notes[0] += " Dữ liệu cũ không có số so: dòng thiếu outline cần xem ảnh trước khi kết luận."
    if offview:
        notes.append(f"{offview} điểm dừng nằm ngoài màn hình lúc đo. Trang cuộn mượt (scroll-behavior: smooth) làm số này tăng, nên không tính là lỗi.")
    return cat(status, f"{len(recs)} lượt, {total} điểm dừng Tab, {sum(f['level'] == 'FAIL' for f in findings)} lỗi",
               sorted(findings, key=lambda f: -RANK[f["level"]]), notes)


# ---------- HTML: canonical, schema, form, tracking ----------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HP_CLASS = re.compile(r"honeypot|(^|[\s_-])hp($|[\s_-])|wpforms-field-hp|ak_hp|nf-field-hp|gform_validation_container|frm_verify", re.I)
HP_NAME = re.compile(r"honeypot|^hp[_-]|[_-]hp$|ak_hp_textarea|fax_only|leave.?blank|^_?gotcha$", re.I)
CAPTCHA = re.compile(r"g-recaptcha|cf-turnstile|h-captcha|frc-captcha|recaptcha/api|challenges\.cloudflare\.com/turnstile|hcaptcha\.com|wpcf7-recaptcha", re.I)
NONCE = re.compile(r"nonce|token|csrf", re.I)
CONTACT = re.compile(r"mail|phone|tel|sdt|dien.?thoai|mobile|zalo", re.I)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canon, self.robots, self.ld, self.forms = [], [], [], []
        self.meta = defaultdict(list)
        self.stack, self.form, self.ld_buf, self.captcha = [], None, None, False

    def handle_starttag(self, t, a):
        a = {k: (v or "") for k, v in a}
        hidden = bool(self.stack and self.stack[-1][1])
        style = a.get("style", "").replace(" ", "").lower()
        if "display:none" in style or "visibility:hidden" in style or a.get("aria-hidden") == "true" or HP_CLASS.search(a.get("class", "")):
            hidden = True
        if CAPTCHA.search(a.get("class", "") + " " + a.get("src", "") + " " + a.get("name", "")):
            self.captcha = True
        if t == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canon.append(a.get("href", ""))
        if t == "meta" and a.get("name", "").lower() in ("robots", "googlebot"):
            self.robots.append(a.get("content", "").lower())
        if t == "meta":
            k = (a.get("property") or a.get("name") or "").strip().lower()
            if k.startswith(("og:", "twitter:", "article:", "fb:")):
                self.meta[k].append(a.get("content", ""))
        if t == "script" and "ld+json" in a.get("type", "").lower():
            self.ld_buf = []
        if t == "form":
            self.form = {"id": a.get("id", ""), "class": a.get("class", "")[:60], "action": a.get("action"), "method": (a.get("method") or "").lower(),
                         "role": a.get("role", ""), "fields": [], "hidden": [], "honeypot": False}
            self.forms.append(self.form)
        if self.form is not None and t in ("input", "textarea", "select"):
            typ = (a.get("type") or ("text" if t == "input" else t)).lower()
            name = a.get("name", "")
            if typ == "hidden":
                self.form["hidden"].append(name)
            elif typ not in ("submit", "button", "image", "reset"):
                if hidden or HP_NAME.search(name) or (a.get("tabindex") == "-1" and a.get("autocomplete") == "off"):
                    self.form["honeypot"] = True
                else:
                    self.form["fields"].append({"name": name, "type": typ, "required": "required" in a or a.get("aria-required") == "true"})
        if t not in VOID:
            self.stack.append((t, hidden))

    def handle_endtag(self, t):
        if t == "script" and self.ld_buf is not None:
            self.ld.append("".join(self.ld_buf))
            self.ld_buf = None
        if t == "form":
            self.form = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == t:
                del self.stack[i:]
                break

    def handle_data(self, d):
        if self.ld_buf is not None:
            self.ld_buf.append(d)


def parse_page(html):
    p = PageParser()
    p.feed(html)
    for f in p.forms:
        names = [x["name"] for x in f["fields"]]
        f["search"] = f["role"] == "search" or "s" in names or any(x["type"] == "search" for x in f["fields"])
        f["contact"] = any(x["type"] in ("email", "tel") or CONTACT.search(x["name"]) for x in f["fields"])
        f["nonce"] = any(NONCE.search(h) for h in f["hidden"])
    return {"canonical": p.canon, "robots": p.robots, "ld": p.ld, "forms": p.forms, "captcha": p.captcha, "meta": dict(p.meta)}


def norm_url(u):
    s = urlsplit(u)
    host = (s.hostname or "").lower()
    if s.port and not ((s.scheme == "https" and s.port == 443) or (s.scheme == "http" and s.port == 80)):
        host += f":{s.port}"
    return urlunsplit((s.scheme.lower(), host, s.path or "/", s.query, ""))


def check_canonical(pages, canonical_host=None):
    """pages: [{name, url, status, html|parsed, headers, expect_canonical}]"""
    findings, n, skipped = [], 0, []
    for p in pages:
        if p.get("status") not in (200, None):
            skipped.append(f"{p['name']} ({p.get('status')})")
            continue
        info = p.get("parsed") or parse_page(p.get("html") or "")
        xr = [l for l in (p.get("headers") or "").lower().splitlines() if l.startswith("x-robots-tag:")]
        noindex = any("noindex" in r for r in info["robots"] + xr)
        cans = info["canonical"]
        n += 1
        host = canonical_host or (urlsplit(p["url"]).netloc if p.get("url") else None)

        def add(level, issue):
            findings.append({"page": p["name"], "level": level, "issue": issue, "canonical": cans})
        if not cans:
            if noindex:
                skipped.append(f"{p['name']} (noindex, không có canonical)")
            else:
                add("FAIL", "trang index được nhưng thiếu canonical")
            continue
        if len(cans) > 1:
            add("FAIL", f"{len(cans)} thẻ canonical")
        c = cans[0]
        if not urlsplit(c).scheme:
            add("WARN", "canonical dạng đường dẫn tương đối")
            c = urljoin(p.get("url") or "", c)
        if host and urlsplit(c).netloc.lower() != host.lower():
            add("FAIL", f"canonical trỏ host khác: {urlsplit(c).netloc}")
        target = p.get("expect_canonical") or p.get("url")
        if target and not noindex and norm_url(c) != norm_url(target):
            add("FAIL", f"canonical không tự trỏ: {c} khác {target}")
    if not n:
        return cat("SKIP", "không có HTML trang 200", notes=[f"bỏ qua: {', '.join(skipped)}"] if skipped else [])
    status = max((f["level"] for f in findings), key=RANK.get, default="PASS")
    return cat(status, f"{n} trang 200, {len({f['page'] for f in findings if f['level'] == 'FAIL'})} trang lỗi canonical", findings,
               [f"không kiểm canonical: {', '.join(skipped)}"] if skipped else [])


def ld_nodes(obj):
    if isinstance(obj, list):
        for x in obj:
            yield from ld_nodes(x)
    elif isinstance(obj, dict):
        if "@type" in obj:
            yield obj
        for k, v in obj.items():
            if k != "@type":
                yield from ld_nodes(v)


def types_of(node):
    t = node.get("@type")
    return t if isinstance(t, list) else [t]


PAGE_TYPES = {"WebPage", "WebSite", "Article", "BlogPosting", "NewsArticle", "CollectionPage", "ProfilePage", "AboutPage", "ContactPage",
              "FAQPage", "SearchResultsPage", "BreadcrumbList", "ItemPage", "QAPage", "MedicalWebPage"}


def check_schema(pages, canonical_host=None, bad_names=("admin", "administrator")):
    findings, n, nblocks, nvalid = [], 0, 0, 0
    named = {"Person", "Organization", "LocalBusiness", "Corporation", "EducationalOrganization", "ProfessionalService"}
    for p in pages:
        if p.get("status") not in (200, None):
            continue
        info = p.get("parsed") or parse_page(p.get("html") or "")
        n += 1
        host = (canonical_host or (urlsplit(p["url"]).netloc if p.get("url") else "")).lower()

        def add(level, issue):
            findings.append({"page": p["name"], "level": level, "issue": issue})
        if not info["ld"]:
            add("WARN", "không có JSON-LD")
        types, data = set(), []
        for raw in info["ld"]:
            nblocks += 1
            try:
                data.append(json.loads(raw))
                nvalid += 1
            except json.JSONDecodeError as e:
                add("FAIL", f"JSON-LD không parse được: {str(e)[:80]}")
        other_hosts = set()
        for node in ld_nodes(data):
            ts = set(map(str, types_of(node)))
            types |= ts
            if ts & named and not str(node.get("name") or "").strip():
                add("FAIL", f"{'/'.join(sorted(ts & named))} thiếu name (@id {node.get('@id', '')})")
            if ts & named and str(node.get("name") or "").strip().lower() in bad_names:
                add("WARN", f"{'/'.join(sorted(ts & named))} mang tên mặc định '{node.get('name')}'")
            # Chỉ node cấp trang (WebPage, WebSite, Article...) phải mang host của site. Node tổ chức khác (công ty mẹ, đối tác) được trỏ host khác.
            nid = str(node.get("@id") or "")
            if host and ts & PAGE_TYPES and nid.startswith("http") and urlsplit(nid).netloc.lower() != host:
                other_hosts.add(urlsplit(nid).netloc)
        if other_hosts:
            add("WARN", f"node cấp trang có @id mang host khác: {', '.join(sorted(other_hosts))}")
        missing = [t for t in p.get("expect_schema") or [] if t not in types]
        if missing:
            add("FAIL", f"thiếu loại schema mong đợi: {', '.join(missing)}")
        p["schema_types"] = sorted(types)
    if not n:
        return cat("SKIP", "không có HTML trang 200")
    status = max((f["level"] for f in findings), key=RANK.get, default="PASS")
    return cat(status, f"{n} trang, {nvalid}/{nblocks} khối JSON-LD hợp lệ, {len({f['page'] for f in findings if f['level'] == 'FAIL'})} trang lỗi",
               sorted(findings, key=lambda f: -RANK[f["level"]]))


def check_form(pages, browser_rows=(), live=None, mail=None):
    """Cấu trúc form từ HTML server + form có hiện, có khởi tạo ở từng bề rộng (DOM). Mặc định không gửi."""
    findings, nforms, expected = [], 0, set()
    dom_hidden = defaultdict(set)  # trường ẩn trong DOM sau JS, ví dụ token chống spam của WPForms
    for r in browser_rows:
        for f in r.get("forms") or []:
            dom_hidden[r["name"]] |= set(f.get("hidden") or [])
    for p in pages:
        if p.get("status") not in (200, None):
            continue
        info = p.get("parsed") or parse_page(p.get("html") or "")
        leads = [f for f in info["forms"] if not f["search"]]
        server_hidden = {h for f in info["forms"] for h in f["hidden"]}
        js_token = sorted(h for h in dom_hidden[p["name"]] - server_hidden if NONCE.search(h))
        if p.get("expect_form") or leads:
            expected.add(p["name"])
        if p.get("expect_form") and not leads:
            findings.append({"page": p["name"], "level": "WARN", "issue": "HTML server không có form; form có thể do JS dựng, xem số đo DOM"})
        for f in leads:
            nforms += 1
            tag = f"form{'#' + f['id'] if f['id'] else ''}"
            if not f["fields"]:
                findings.append({"page": p["name"], "level": "FAIL", "issue": f"{tag} không có trường nhập"})
                continue
            if not f["contact"]:
                findings.append({"page": p["name"], "level": "WARN", "issue": f"{tag} không có trường email hay điện thoại"})
            if not (f["honeypot"] or info["captcha"] or js_token):
                findings.append({"page": p["name"], "level": "WARN", "issue": f"{tag} không thấy honeypot, captcha hay token chống spam do JS thêm"})
            f["js_token"] = js_token
            # Form không có method lẫn action thường do JS gửi (fetch): không tính là GET.
            if f["method"] == "get" and f["action"] and f["contact"]:
                findings.append({"page": p["name"], "level": "WARN", "issue": f"{tag} gửi bằng GET: dữ liệu khách lộ trên URL"})
            f["page"] = p["name"]
    dom = defaultdict(dict)
    for r in browser_rows:
        if "forms" in r and not r.get("err"):
            dom[r["name"]][r["vw"]] = sum(1 for f in r["forms"] if f["visible"] and f["visibleFields"] > 0)
            if r.get("form"):
                expected.add(r["name"])
    for name, by_w in sorted(dom.items()):
        # Trang khai báo có form, hoặc form hiện ở bề rộng này mà mất ở bề rộng khác (form không khởi tạo trên mobile).
        if name in expected or max(by_w.values()) > 0:
            for w, k in sorted(by_w.items()):
                if k == 0:
                    findings.append({"page": name, "level": "FAIL", "issue": f"form không hiện hoặc không khởi tạo ở {w} px"})
    notes = []
    if live:
        ok = live.get("success_seen") and any(200 <= x["status"] < 400 for x in live.get("posts") or [])
        if not ok:
            findings.append({"page": live.get("url"), "level": "FAIL", "issue": "gửi form thật không thấy phản hồi thành công", "token": live.get("token")})
        elif mail == "ok":
            notes.append(f"Đã gửi thật, hộp mail đã nhận token {live.get('token')}.")
        elif mail == "missing":
            findings.append({"page": live.get("url"), "level": "FAIL", "issue": "hộp mail không nhận được mail của lượt gửi thật", "token": live.get("token")})
        else:
            findings.append({"page": live.get("url"), "level": "WARN", "issue": f"chờ kiểm hộp mail: tìm token {live.get('token')}", "token": live.get("token")})
    else:
        notes.append("Chưa gửi form thật (mặc định). Gửi thật theo references/form-gui-that.md.")
    if not nforms and not dom and not live:
        return cat("SKIP", "không có form", findings, notes)
    notes.append("Đường đi của lead chưa kiểm bằng script: form → mail → Sheet → CMS → hộp thư thật. Kiểm tay từng chặng theo checklist của hạng mục Form, ghi tên site và mốc giờ vào báo cáo.")
    status = max((f["level"] for f in findings), key=RANK.get, default="PASS")
    return cat(status, f"{nforms} form trong HTML, {len(expected)} trang có form", findings, notes)


TAG_RE = [re.compile(r"\bGTM-[A-Z0-9]{5,9}\b"), re.compile(r"\bG-[A-Z0-9]{8,12}\b"), re.compile(r"\bUA-\d{4,10}-\d{1,3}\b"),
          re.compile(r"\bAW-\d{6,12}\b"), re.compile(r"fbq\(\s*['\"]init['\"]\s*,\s*['\"](\d{8,20})"), re.compile(r"clarity\.ms/tag/([a-z0-9]{6,14})")]


def tracking_ids(html):
    found = set()
    for r in TAG_RE:
        for m in r.finditer(html or ""):
            found.add(m.group(1) if m.groups() else m.group(0))
    return sorted(found)


def tag_present(html, pattern):
    if pattern.startswith("re:"):
        return bool(re.search(pattern[3:], html or ""))
    return pattern in (html or "")


def is_tracking_url(url, patterns=TRACKING_BLOCK):
    return any(fnmatch.fnmatchcase(url.lower(), p.lower()) for p in patterns)


def check_tracking(pages, expect=(), browser_rows=()):
    findings, ids = [], set()
    n = 0
    for p in pages:
        if p.get("status") not in (200, None) or p.get("expect_tracking") is False:
            continue
        n += 1
        ids |= set(tracking_ids(p.get("html")))
        miss = [e for e in expect if not tag_present(p.get("html"), e)]
        if miss:
            findings.append({"page": p["name"], "level": "FAIL", "issue": f"thiếu thẻ: {', '.join(miss)}"})
    seen = blocked = 0
    ran = False
    for r in browser_rows:
        t = r.get("tracking")
        if not t:
            continue
        ran = True
        seen, blocked = seen + t["seen"], blocked + t["blocked"]
        if t["leaked"]:
            findings.append({"page": f"{r['name']}@{r['vw']}", "level": "FAIL", "issue": "request tracking lọt qua chặn", "examples": t["leaked"][:3]})
    notes = [f"Thẻ thấy trong HTML: {', '.join(sorted(ids)) or 'không có'}."]
    if ran:
        notes.append(f"Trình duyệt: {seen} request tracking, chặn {blocked}. QA không gửi hit thật.")
    if not expect:
        notes.append("Chưa khai báo thẻ mong đợi (tracking.expect): chỉ kiểm phần chặn.")
    if not ran and not expect:
        return cat("SKIP", "không có số đo trình duyệt và chưa khai báo thẻ", findings, notes)
    status = "FAIL" if findings else "PASS"
    return cat(status, f"{n} trang kiểm thẻ, {sum(f['issue'].startswith('thiếu') for f in findings)} trang thiếu thẻ, "
               f"{sum('lọt' in f['issue'] for f in findings)} lượt lọt request", findings, notes)


# ---------- Plugin ----------

NOISE = re.compile(r"^\s*(Notice|Warning|Deprecated|PHP |Success:|Error:|Fatal)", re.I)


def parse_plugin_list(text):
    """Đọc output `wp plugin list` dạng JSON, CSV, TSV hoặc bảng. Bỏ dòng Notice/Success của WP-CLI."""
    i = text.find("[{")
    if i >= 0:
        rows, _ = json.JSONDecoder().raw_decode(text[i:])
        return {r["name"]: {"status": r.get("status", ""), "version": r.get("version", "") or ""} for r in rows}
    lines = [l for l in text.splitlines() if l.strip() and not NOISE.match(l) and not l.lstrip().startswith("+")]
    out, cols = {}, None
    for l in lines:
        sep = "\t" if "\t" in l else ("|" if "|" in l else ("," if "," in l else None))
        cells = [c.strip() for c in (l.strip().strip("|").split(sep) if sep else l.split())]
        if cols is None:
            if "name" in cells and "status" in cells:
                cols = cells
            continue
        if len(cells) < 2:
            continue
        r = dict(zip(cols, cells + [""] * (len(cols) - len(cells))))
        out[r["name"]] = {"status": r.get("status", ""), "version": r.get("version", "")}
    return out


def diff_plugins(stg, prod, ignore=()):
    findings = []
    for name in sorted(set(stg) | set(prod)):
        if name in ignore:
            continue
        s, p = stg.get(name), prod.get(name)
        if not s:
            findings.append({"plugin": name, "kind": "chỉ có ở production", "production": f"{p['status']} {p['version']}".strip(), "level": "FAIL"})
        elif not p:
            findings.append({"plugin": name, "kind": "chỉ có ở staging", "staging": f"{s['status']} {s['version']}".strip(), "level": "FAIL"})
        elif s["status"] != p["status"]:
            findings.append({"plugin": name, "kind": "khác trạng thái", "staging": s["status"], "production": p["status"], "level": "FAIL"})
        elif s["version"] != p["version"]:
            findings.append({"plugin": name, "kind": "khác version", "staging": s["version"], "production": p["version"], "level": "FAIL"})
    return findings


def check_plugins(stg_text, prod_text, ignore=()):
    if stg_text is None or prod_text is None:
        return cat("SKIP", "thiếu file plugin list của staging hoặc production",
                   notes=["Lấy bằng `wp plugin list --format=json` theo hồ sơ server. Không có hồ sơ server thì không SSH."])
    stg, prod = parse_plugin_list(stg_text), parse_plugin_list(prod_text)
    if not stg or not prod:
        return cat("WARN", "không đọc được danh sách plugin", notes=[f"staging {len(stg)}, production {len(prod)} plugin"])
    f = diff_plugins(stg, prod, ignore)
    return cat("FAIL" if f else "PASS", f"staging {len(stg)}, production {len(prod)} plugin, {len(f)} chỗ lệch", f,
               [f"bỏ qua: {', '.join(ignore)}"] if ignore else [])


# ---------- HTTP, redirect ----------

def parse_http_list(text):
    """Dòng 'mã đường-dẫn [location]' như danh sách LIST của httpcheck.sh."""
    out = []
    for l in text.splitlines():
        p = l.split()
        if len(p) >= 2 and p[0].isdigit() and not l.lstrip().startswith("#"):
            out.append({"expect": int(p[0]), "path": p[1], **({"location": p[2]} if len(p) > 2 else {})})
    return out


def parse_httpcheck_output(text):
    """Output của httpcheck.sh: 'OK|FAIL mong-đợi thực-tế đường-dẫn [location]'."""
    rows = []
    for l in text.splitlines():
        p = l.split()
        if len(p) >= 4 and p[0] in ("OK", "FAIL"):
            rows.append({"path": p[3], "expect": int(p[1]), "code": p[2], "location": p[4] if len(p) > 4 else ""})
    return rows


def check_http(rows, base=""):
    if not rows:
        return cat("SKIP", "không có kiểm HTTP")
    findings = []
    for r in rows:
        code = str(r.get("code"))
        bad = code != str(r["expect"])
        exp_loc = r.get("expect_location") or ""
        if not bad and exp_loc and norm_url(urljoin(base or "http://x/", r.get("location") or "")) != norm_url(urljoin(base or "http://x/", exp_loc)):
            bad = True
        if bad:
            findings.append({"path": r["path"], "expect": r["expect"], "code": code, "location": r.get("location", ""), "level": "FAIL",
                             **({"note": "000 = không kết nối được (tunnel rớt, DNS, timeout): chạy lại"} if code == "000" else {})})
    return cat("FAIL" if findings else "PASS", f"{len(rows)} kiểm, {len(findings)} sai mã", findings)


def eval_redirect(spec, hops, base):
    """hops: [{url, code, location}] theo thứ tự. spec: {from, to, code=301}."""
    want = int(spec.get("code", 301))
    to = norm_url(urljoin(base, spec["to"]))
    res = {"from": spec["from"], "to": spec["to"], "chain": [f"{h['code']} {h['url']}" for h in hops]}
    if not hops:
        return {**res, "level": "FAIL", "issue": "không có phản hồi"}
    first, last = hops[0], hops[-1]
    if str(first["code"]) != str(want):
        return {**res, "level": "FAIL", "issue": f"mã {first['code']}, mong đợi {want}"}
    if norm_url(last["url"]) != to:
        return {**res, "level": "FAIL", "issue": f"đích cuối {last['url']} khác {to}"}
    if str(last["code"]) != "200":
        return {**res, "level": "FAIL", "issue": f"đích trả {last['code']}"}
    if len(hops) > 2:
        return {**res, "level": "WARN", "issue": f"chuỗi {len(hops) - 1} bước"}
    return {**res, "level": "PASS"}


def check_redirect(results):
    if not results:
        return cat("SKIP", "không khai báo redirect cần kiểm")
    bad = [r for r in results if r["level"] != "PASS"]
    status = max((r["level"] for r in results), key=RANK.get)
    return cat(status, f"{len(results)} redirect, {sum(r['level'] == 'FAIL' for r in bad)} lỗi, {sum(r['level'] == 'WARN' for r in bad)} chuỗi nhiều bước", bad)


# ---------- Jev ui-visual ----------

def load_gates(paths, site, version, rubric="ui-visual"):
    gates = {}
    for path in paths:
        if not path or not Path(path).is_file():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == rubric and e.get("version") == version and e.get("site") in (site, "*") and e.get("question") not in gates:
                thr = e.get("threshold") if e.get("threshold") is not None else e.get("conf_gate")
                if thr is not None:
                    gates[e["question"]] = {"thr": thr, "site": e.get("site"), "source": str(path)}
    return gates


def pad_image(path, minimum=320, maximum=1568, max_px=800_000, min_ratio=0.3):
    """Jev trả http_400 với ảnh cạnh dưới ~280 px, ảnh trên ~1 MP và ảnh dẹt cao dưới 0,3 lần rộng (đo 23/10/2026).
    Thu ảnh về ≤ 0,8 MP và ≤ 1.568 px mỗi cạnh, rồi đệm nền trắng lên 320 px và lên tỉ lệ cao/rộng 0,3."""
    try:
        from PIL import Image
    except ImportError:
        return path
    im = Image.open(path)
    w, h = im.size
    if min(w, h) >= minimum and max(w, h) <= maximum and w * h <= max_px and h >= min_ratio * w:
        return path
    im = im.convert("RGB")
    if max(im.size) > maximum:
        im.thumbnail((maximum, maximum))
    if im.width * im.height > max_px:
        k = (max_px / (im.width * im.height)) ** 0.5
        im = im.resize((int(im.width * k), int(im.height * k)))
    w = max(im.width, minimum)
    h = max(im.height, minimum, int(min_ratio * w + 0.999))
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    out = Path(path).with_name(Path(path).stem + "_pad.png")
    canvas.save(out)
    return out


def jev_items(browser_rows, shots_dir, site_note=""):
    items = []
    for r in browser_rows:
        for s in r.get("shots") or []:
            f = pad_image(Path(shots_dir) / s["file"])
            dev = f"a phone {r['vw']}x{r['vh']}" if r.get("mobile") else f"a screen {r['vw']}x{r['vh']}"
            ctx = (f"Screenshot of one screen of the page {urlsplit(r['url']).path or '/'} on {dev}. The page is scrolled {s['y']}px "
                   f"from the top (page height {s['page_h']}px). The page continues above and below this screen, so content cut by "
                   f"the top or bottom edge of the screenshot is normal. {site_note}").strip()
            items.append({"id": f"{r['name']}|{r['vw']}|{s['i']}", "state": [ctx, {"image_path": os.path.relpath(f, Path(shots_dir).parent)}]})
    return items


def check_ui_visual(jev_rows, gates, uncal=0.7, browser_rows=(), tiles_mode="all"):
    if not jev_rows:
        return cat("SKIP", "chưa chạy Jev (thêm --jev)")
    findings, errs = [], [r["id"] for r in jev_rows if "error" in r]
    # Màn chụp ít hơn page_h/vh nghĩa là Jev và người xem chỉ thấy một phần trang: FAIL khi tiles là "all".
    findings += qa_extra.check_tile_coverage(browser_rows, tiles_mode)
    for r in jev_rows:
        a = r.get("answers") or {}
        flags = []
        for q in NOULS:
            p = (a.get(q) or {}).get("p_yes")
            thr = gates[q]["thr"] if q in gates else uncal
            if p is not None and p >= thr:
                flags.append(f"{q} {p:.2f}")
        if flags:
            findings.append({"shot": r["id"], "level": "WARN", "flags": flags, "box": (a.get("defect_box") or {}).get("box")})
    uncal_q = [q for q in NOULS if q not in gates]
    notes = [f"Jev lỗi {len(errs)} ảnh: {', '.join(errs[:5])}"] if errs else []
    if uncal_q:
        notes.append(f"Câu chưa hiệu chuẩn cho site này: {', '.join(uncal_q)}. Chưa hiệu chuẩn, chỉ báo cho người đọc (ngưỡng tạm {uncal}).")
    notes.append("Model không tự đánh FAIL. Claude xem ảnh của mọi dòng trước khi kết luận. fixed_covers và cut_off hay báo nhầm khi trang có thanh dính, nút nổi.")
    status = "FAIL" if any(f["level"] == "FAIL" for f in findings) else ("WARN" if findings or errs or uncal_q else "PASS")
    cov = [f for f in findings if "flags" not in f]
    summ = f"{len(jev_rows)} ảnh, {len(findings) - len(cov)} ảnh cần xem" + (f", {len(cov)} URL chụp thiếu màn" if cov else "") + (" (chưa hiệu chuẩn, chỉ báo cho người đọc)" if len(uncal_q) == len(NOULS) else "")
    return cat(status, summ, findings, notes)


# ---------- Gửi form thật ----------

def submit_allowed(flag, env_kind, host, environ, approved=None):
    """Hai lớp chặn: cờ --submit-live và WEB_QA_SUBMIT_LIVE bằng đúng host. Production cần thêm ghi chú duyệt của người có quyền."""
    if not flag:
        return False, "không có --submit-live"
    if environ.get("WEB_QA_SUBMIT_LIVE") != host:
        return False, f"WEB_QA_SUBMIT_LIVE phải bằng {host}"
    if env_kind != "staging" and not (approved or "").strip():
        return False, "production: cần --approved '<người duyệt, ngày giờ>' cho đúng lượt này"
    return True, "ok"


# ---------- Cấu hình, thu thập ----------

def load_config(a):
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")) if a.config else {}
    root = Path(a.config).resolve().parent if a.config else Path.cwd()
    if getattr(a, "base", None):
        cfg["base"] = a.base
    if getattr(a, "urls", None):
        cfg["urls"] = [{"name": l.split("\t")[0], "path": l.split("\t")[1].strip()} for l in Path(a.urls).read_text(encoding="utf-8").splitlines()
                       if l.strip() and not l.startswith("#")]
    if getattr(a, "widths", None):
        cfg["widths"] = [int(x) for x in a.widths.split(",")]
    if not cfg.get("base"):
        sys.exit("thiếu base: đặt trong config hoặc --base")
    cfg.setdefault("widths", DEFAULT_WIDTHS)
    cfg.setdefault("env", "staging")
    cfg.setdefault("site", urlsplit(cfg["base"]).hostname)
    cfg.setdefault("canonical_host", urlsplit(cfg["base"]).netloc)
    if isinstance(cfg.get("http"), str):
        cfg["http"] = parse_http_list((root / cfg["http"]).read_text(encoding="utf-8"))
    cfg["_root"] = str(root)
    return cfg


def page_url(cfg, u):
    return urljoin(cfg["base"].rstrip("/") + "/", u["path"].lstrip("/")) if not u["path"].startswith("http") else u["path"]


def curl(url, cfg, body=None, hdr=None, fmt="%{http_code} %{redirect_url}", extra=()):
    host = urlsplit(url).hostname
    cmd = ["curl", "-s", "-m", "30", "-A", UA, "-o", str(body or os.devnull), "-w", fmt, *extra]
    if hdr:
        cmd += ["-D", str(hdr)]
    if cfg.get("resolve") and cfg["resolve"].split("=")[0] == host:
        ip = cfg["resolve"].split("=")[1]
        cmd += ["--resolve", f"{host}:443:{ip}", "--resolve", f"{host}:80:{ip}"]
    cred = os.environ.get("WEB_QA_AUTH") or os.environ.get("CDP_AUTH")
    if cred and host == urlsplit(cfg["base"]).hostname:
        cmd += ["-u", cred]
    if cfg.get("cookie"):
        cmd += ["-b", cfg["cookie"]]
    p = subprocess.run(cmd + [url], capture_output=True, text=True)
    code, _, loc = p.stdout.strip().partition(" ")
    return code or "000", loc.strip()


def chain(url, cfg, raw, name=None, maxhops=6):
    hops = []
    for i in range(maxhops):
        body = raw / "html" / f"{name}.html" if name else None
        hdr = raw / "html" / f"{name}.hdr" if name else None
        code, loc = curl(url, cfg, body, hdr)
        hops.append({"url": url, "code": code, "location": loc})
        if not code.startswith("3") or not loc:
            break
        url = urljoin(url, loc)
        time.sleep(0.2)
    return hops


def collect_http(cfg, raw):
    (raw / "html").mkdir(parents=True, exist_ok=True)
    rows = []
    for u in cfg.get("urls", []):
        url = page_url(cfg, u)
        hops = chain(url, cfg, raw, u["name"])
        (raw / "html" / f"{u['name']}.url").write_text(hops[-1]["url"], encoding="utf-8")
        rows.append({"kind": "page", "name": u["name"], "path": u["path"], "url": url, "expect": u.get("expect", 200),
                     "code": hops[0]["code"], "location": hops[0]["location"], "final_code": hops[-1]["code"], "final_url": hops[-1]["url"]})
    for h in cfg.get("http", []):
        code, loc = curl(page_url(cfg, h), cfg)
        rows.append({"kind": "http", "path": h["path"], "expect": h["expect"], "code": code, "location": loc, "expect_location": h.get("location", "")})
        time.sleep(0.2)
    for r in cfg.get("redirects", []):
        rows.append({"kind": "redirect", "spec": r, "hops": chain(page_url(cfg, {"path": r["from"]}), cfg, raw)})
    with (raw / "http.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def find_axe(cfg):
    cands = [cfg.get("axe_js"), os.environ.get("AXE_JS"), str(Path.home() / ".cache/web-qa-gate/axe.min.js")]
    for d in [Path.cwd(), *Path.cwd().parents]:
        cands.append(str(d / "node_modules/axe-core/axe.min.js"))
    cands += sorted(glob.glob(str(Path.home() / ".npm/_npx/*/node_modules/axe-core/axe.min.js")))
    return next((c for c in cands if c and Path(c).is_file()), None)


def find_up(rel):
    for start in (HERE, Path.cwd()):
        for d in [start, *start.parents]:
            if (d / rel).is_file():
                return d / rel
    return None


def tiles_setting(cfg):
    t = cfg.get("ui_visual", {}).get("tiles", "all")
    return t if t in ("all", None) else int(t)


def probe_job(cfg, raw, **extra):
    """Phần chung của job.json cho mọi script đo: trang, chặn tracking, host. Basic Auth lấy từ biến môi trường, không ghi vào file."""
    job = {"pages": [{"name": u["name"], "url": page_url(cfg, u), "form": bool(u.get("form")), **({"always": True} if u.get("always") else {})} for u in cfg.get("urls", [])],
           "block": TRACKING_BLOCK + cfg.get("tracking", {}).get("block_extra", []),
           "host": urlsplit(cfg["base"]).hostname, "resolve": cfg.get("resolve"), "cookie": cfg.get("cookie"), "wait": cfg.get("wait", 2500)}
    job.update(extra)
    return job


def collect_browser(cfg, raw, axe_js, opts=None):
    opts = opts or {}
    uv = cfg.get("ui_visual", {})
    job = probe_job(cfg, raw, widths=cfg["widths"], axe_js=axe_js, axe_widths=[cfg["widths"][0], cfg["widths"][-1]],
                    focus_widths=[cfg["widths"][0], cfg["widths"][-1]], focus_max=cfg.get("focus", {}).get("max", 80),
                    tracking=TRACKING_BLOCK + cfg.get("tracking", {}).get("block_extra", []),
                    shots_dir=str(raw / "shots"), tiles=tiles_setting(cfg), tiles_max=uv.get("tiles_max", 12),
                    hide_selectors=uv.get("hide_selectors", []), hide_fixed=bool(uv.get("hide_fixed")))
    (raw / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    out = raw / "browser.jsonl"
    if out.exists() and not opts.get("resume"):
        out.unlink()
    cmd = ["node", str(HERE / "browser_probe.mjs"), "--job", str(raw / "job.json"), "--out", str(out)]
    if opts.get("tabs"):
        cmd += ["--tabs", str(opts["tabs"])]
    if opts.get("resume"):
        cmd += ["--resume"]
    if opts.get("cache"):
        cmd += ["--cache", opts["cache"]]
    if opts.get("page_timeout"):
        cmd += ["--page-timeout", str(opts["page_timeout"])]
    subprocess.run(cmd, check=False)


def collect_interact(cfg, raw, opts=None):
    """Hạng mục 13 và 14: interact_probe.mjs (menu, slider, trạng thái, nút, lưới, cặp VI/EN) và landmarks.mjs. Cần khối interact trong qa.json."""
    opts = opts or {}
    ic = cfg.get("interact")
    if ic is None:
        return "chưa khai khối interact trong qa.json"
    ic = dict(ic)
    ic["pairs"] = [{**p, "vi": page_url(cfg, {"path": p["vi"]}), "en": page_url(cfg, {"path": p["en"]})} for p in ic.get("pairs", [])]
    job = probe_job(cfg, raw, interact=ic, shots_dir=str(raw / "shots"), page_timeout=opts.get("page_timeout"))
    (raw / "interact_job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    out = raw / "interact.jsonl"
    if out.exists():
        out.unlink()
    pt = ["--page-timeout", str(opts["page_timeout"])] if opts.get("page_timeout") else []
    subprocess.run(["node", str(HERE / "interact_probe.mjs"), "--job", str(raw / "interact_job.json"), "--out", str(out), *pt], check=False)
    lm = ic.get("landmarks", {})
    if lm is not False:
        ljob = probe_job(cfg, raw, landmarks=lm or {}, landmark_widths=(lm or {}).get("widths") or [390, 1366])
        (raw / "landmarks_job.json").write_text(json.dumps(ljob, ensure_ascii=False, indent=1), encoding="utf-8")
        lout = raw / "landmarks.jsonl"
        if lout.exists():
            lout.unlink()
        subprocess.run(["node", str(HERE / "landmarks.mjs"), "--job", str(raw / "landmarks_job.json"), "--out", str(lout), *pt], check=False)
    return None


def collect_og_images(cfg, raw):
    """Tải mỗi og:image một lần (tối đa 12 MB) để kiểm mã HTTP, loại nội dung, cỡ và dung lượng. Chỉ đọc."""
    done, rows = {}, []
    (raw / "og").mkdir(parents=True, exist_ok=True)
    for pg in html_pages(cfg, raw):
        if pg.get("status") not in (200, None):
            continue
        img = (parse_page(pg["html"]).get("meta", {}).get("og:image") or [""])[0].strip()
        if not urlsplit(img).scheme or not urlsplit(img).netloc:
            continue
        if img not in done:
            dest = raw / "og" / f"{len(done)}.img"
            code, ctype = curl(img, cfg, dest, fmt="%{http_code} %{content_type}", extra=("-L", "--max-redirs", "3", "--max-filesize", "12582912"))
            data = dest.read_bytes() if dest.exists() else b""
            dims = qa_extra.image_dims(data) if code == "200" else None
            done[img] = {"url": img, "code": code, "content_type": ctype, "bytes": len(data), "w": dims[0] if dims else None, "h": dims[1] if dims else None}
            if dest.exists():
                dest.unlink()
            time.sleep(0.2)
        rows.append({"page": pg["name"], **done[img]})
    with (raw / "og_images.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def collect_jev(cfg, raw, budget):
    jev, task = find_up("tools/ai-assist/jev.py"), find_up("tools/ai-assist/tasks/ui-visual.json")
    if not jev or not task:
        return "không tìm thấy tools/ai-assist/jev.py"
    rows = jl(raw / "browser.jsonl") if (raw / "browser.jsonl").exists() else []
    items = jev_items(rows, raw / "shots", cfg.get("ui_visual", {}).get("site_note", ""))
    if not items:
        return "không có ảnh chụp"
    with (raw / "jev-in.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(i, ensure_ascii=False) + "\n" for i in items)
    p = subprocess.run([sys.executable, "-I", str(jev), "--task", str(task), "--in", str(raw / "jev-in.jsonl"),
                        "--out", str(raw / "jev-out.jsonl"), "--budget", str(budget)], capture_output=True, text=True)
    return None if p.returncode == 0 else (p.stderr.strip().splitlines() or ["jev lỗi"])[-1][:200]


def submit_live(cfg, raw, a):
    live = cfg.get("form_live") or {}
    page = next((u for u in cfg.get("urls", []) if u["name"] == live.get("page")), None)
    if not page or not live.get("data"):
        sys.exit("form_live trong config cần 'page' (tên trong urls) và 'data' (file JSON trường → giá trị)")
    url = page_url(cfg, page)
    ok, why = submit_allowed(a.submit_live, cfg["env"], urlsplit(url).netloc, os.environ, a.approved)
    if not ok:
        sys.exit(f"từ chối gửi form thật: {why}")
    token = f"QA-{dt.datetime.now():%Y%m%d%H%M}-{random.randint(1000, 9999)}"
    cmd = ["node", str(HERE / "form_submit.mjs"), "--submit-live", "--url", url, "--data", str(Path(cfg["_root"]) / live["data"]),
           "--token", token, "--out", str(raw / "form_live.json")]
    cmd += ["--form", live["form"]] * bool(live.get("form")) + ["--success", live["success"]] * bool(live.get("success"))
    subprocess.run(cmd, check=False)
    if (raw / "form_live.json").exists():
        d = json.loads((raw / "form_live.json").read_text(encoding="utf-8"))
        d.update({"env": cfg["env"], "approved": a.approved or ""})
        (raw / "form_live.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------- Report ----------

def html_pages(cfg, raw):
    http = {r["name"]: r for r in jl(raw / "http.jsonl") if r.get("kind") == "page"} if (raw / "http.jsonl").exists() else {}
    pages = []
    for u in cfg.get("urls", []):
        f = raw / "html" / f"{u['name']}.html"
        if not f.exists():
            continue
        h = http.get(u["name"], {})
        code = h.get("final_code")
        pages.append({"name": u["name"], "url": h.get("final_url") or page_url(cfg, u), "status": int(code) if str(code).isdigit() else None,
                      "html": f.read_text(encoding="utf-8", errors="replace"),
                      "headers": (raw / "html" / f"{u['name']}.hdr").read_text(encoding="utf-8", errors="replace") if (raw / "html" / f"{u['name']}.hdr").exists() else "",
                      "expect_schema": u.get("schema"), "expect_form": u.get("form"), "expect_tracking": u.get("tracking"),
                      "expect_canonical": urljoin(cfg["base"], u["canonical"]) if u.get("canonical") else None})
    return pages


def build_report(cfg, out, mail=None, notes=()):
    raw = Path(out) / "raw"
    if (raw / "sample.json").exists():
        keep = set(json.loads((raw / "sample.json").read_text(encoding="utf-8"))["names"])
        cfg = {**cfg, "urls": [u for u in cfg.get("urls", []) if u["name"] in keep]}
    browser = jl(raw / "browser.jsonl") if (raw / "browser.jsonl").exists() else []
    http = jl(raw / "http.jsonl") if (raw / "http.jsonl").exists() else []
    pages = html_pages(cfg, raw)
    for p in pages:
        p["parsed"] = parse_page(p["html"])
    root = Path(cfg["_root"])
    pl = cfg.get("plugins", {})
    rd = lambda k: (root / pl[k]).read_text(encoding="utf-8", errors="replace") if pl.get(k) and (root / pl[k]).exists() else None
    live = json.loads((raw / "form_live.json").read_text(encoding="utf-8")) if (raw / "form_live.json").exists() else None
    jev_rows = jl(raw / "jev-out.jsonl") if (raw / "jev-out.jsonl").exists() else []
    irows = jl(raw / "interact.jsonl") if (raw / "interact.jsonl").exists() else []
    lrows = jl(raw / "landmarks.jsonl") if (raw / "landmarks.jsonl").exists() else []
    og_images = {r["page"]: r for r in jl(raw / "og_images.jsonl")} if (raw / "og_images.jsonl").exists() else {}
    task = find_up("tools/ai-assist/tasks/ui-visual.json")
    version = json.loads(task.read_text(encoding="utf-8"))["version"] if task else None
    reg = [cfg.get("registry") and str(root / cfg["registry"]), "00-client-context/model-calibration.json",
           str(find_up("tools/ai-assist/calibration-defaults.json") or "")]
    ax = cfg.get("axe", {})
    cats = {
        "overflow": check_overflow(browser),
        "axe": check_axe(axe_records(browser), tuple(ax.get("fail_impacts", ("critical", "serious"))), tuple(ax.get("ignore", ()))),
        "focus": check_focus(focus_records(browser)),
        "form": check_form(pages, browser, live, mail),
        "tracking": check_tracking(pages, cfg.get("tracking", {}).get("expect", []), browser),
        "plugins": check_plugins(rd("staging"), rd("production"), tuple(pl.get("ignore", ()))),
        "http": check_http([r for r in http if r["kind"] in ("page", "http")], cfg["base"]),
        "redirect": check_redirect([eval_redirect(r["spec"], r["hops"], cfg["base"]) for r in http if r["kind"] == "redirect"]),
        "canonical": check_canonical(pages, cfg.get("canonical_host")),
        "schema": check_schema(pages, cfg.get("canonical_host")),
        "ui_visual": check_ui_visual(jev_rows, load_gates(reg, cfg["site"], version), browser_rows=browser,
                                     tiles_mode="all" if tiles_setting(cfg) == "all" else "sample"),
        "interact": qa_extra.check_interact(irows, cfg.get("interact")),
        "layout": qa_extra.check_layout(irows, lrows, cfg.get("interact")),
        "og": qa_extra.check_og(pages, og_images, cfg.get("canonical_host"), (cfg.get("og") or {}).get("min_width", 1200)),
    }
    sample = raw / "sample.json"
    if sample.exists():
        sm = json.loads(sample.read_text(encoding="utf-8"))
        cats["overflow"]["notes"].append(f"Chạy trên mẫu {len(sm['names'])}/{sm['total']} URL (--sample {sm['spec']}, seed {sm['seed']}). Kết luận chỉ áp cho mẫu.")
    if browser and not any(r.get("axe") for r in browser):
        cats["axe"]["notes"].append("Không có axe-core: tải https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js vào ~/.cache/web-qa-gate/axe.min.js.")
    for k, n in notes:
        cats[k]["notes"].append(n)
    st = [c["status"] for c in cats.values()]
    verdict = "FAIL" if "FAIL" in st else ("REVIEW" if "WARN" in st else "PASS")
    rep = {"site": cfg["site"], "env": cfg["env"], "base": cfg["base"], "widths": cfg["widths"], "urls": len(cfg.get("urls", [])),
           "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "verdict": verdict, "categories": cats}
    Path(out, "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(out, "report.md").write_text(render_md(rep), encoding="utf-8")
    return rep


def fmt_finding(f):
    head = f.get("page") or f.get("plugin") or f.get("path") or f.get("rule") or f.get("shot") or f.get("from") or ""
    parts = []
    for k in ("width", "issue", "kind", "impact", "over_px", "code", "expect", "staging", "production", "nodes", "pages", "flags", "chain", "note", "offenders", "examples"):
        if k in f and f[k] not in (None, "", []):
            v = f[k]
            v = ", ".join(map(str, v)) if isinstance(v, list) else v
            parts.append(f"{k}={v}" if k not in ("issue", "kind") else str(v))
    return f"- {f.get('level', '')} {head}: " + "; ".join(parts)


def render_md(rep):
    c = rep["categories"]
    names = dict(CATS)
    bad = [names[k] for k, v in c.items() if v["status"] == "FAIL"]
    warn = [names[k] for k, v in c.items() if v["status"] == "WARN"]
    skip = [names[k] for k, v in c.items() if v["status"] == "SKIP"]
    L = [f"# Web QA gate: {rep['site']} ({rep['env']})", "",
         f"- Thời điểm: {rep['generated']}. Base: {rep['base']}. Bề rộng: {', '.join(map(str, rep['widths']))} px. Số URL: {rep['urls']}.",
         f"- Kết luận: **{rep['verdict']}**.",
         f"- Hạng mục FAIL: {', '.join(bad) or 'không có'}.",
         f"- Cần người xem (WARN): {', '.join(warn) or 'không có'}.",
         f"- Bỏ qua: {', '.join(skip) or 'không có'}.", "",
         "| Hạng mục | Kết quả | Tóm tắt |", "|---|---|---|"]
    L += [f"| {names[k]} | {v['status']} | {v['summary']} |" for k, v in c.items()]
    L += ["", "## Chi tiết", ""]
    for k, v in c.items():
        L.append(f"### {names[k]}: {v['status']}")
        L.append("")
        L += [fmt_finding(f) for f in v["findings"][:30]]
        if len(v["findings"]) > 30:
            L.append(f"- … còn {len(v['findings']) - 30} dòng trong report.json")
        L += [f"- Ghi chú: {n}" for n in v["notes"]]
        if not v["findings"] and not v["notes"]:
            L.append("- Không có phát hiện.")
        L.append("")
    return "\n".join(L)


# ---------- CLI ----------

def resolve_variants(cache):
    return {None: ["default"], "both": ["cached", "nc"]}.get(cache, [cache])


def cmd_run(a):
    cfg = load_config(a)
    out = Path(a.out)
    raw = out / "raw"
    skip = set((a.skip or "").split(","))
    all_urls = cfg.get("urls", [])
    sample_file = raw / "sample.json"
    reuse = bool(a.resume and sample_file.exists())
    if reuse:
        keep = set(json.loads(sample_file.read_text(encoding="utf-8"))["names"])  # giữ đúng mẫu của lượt trước
        cfg["urls"] = [u for u in all_urls if u["name"] in keep]
    elif a.sample:
        cfg["urls"] = qa_extra.apply_sample(all_urls, a.sample, a.seed)
    sampled = reuse or (a.sample and len(cfg["urls"]) < len(all_urls))
    variants = resolve_variants(a.cache)
    if a.plan:
        todo = [f"{u['name']}|{w}|{v}" for u in cfg["urls"] for w in cfg["widths"] for v in variants]
        print(json.dumps({"urls": [u["name"] for u in cfg["urls"]], "total_urls": len(all_urls), "widths": cfg["widths"], "variants": variants,
                          "tabs": a.tabs, "browser_runs": len(todo), "interact": cfg.get("interact") is not None}, ensure_ascii=False))
        return 0
    raw.mkdir(parents=True, exist_ok=True)
    if sampled and not reuse:
        sample_file.write_text(json.dumps({"spec": a.sample, "seed": a.seed, "total": len(all_urls), "names": [u["name"] for u in cfg["urls"]]}, ensure_ascii=False), encoding="utf-8")
    elif not sampled and sample_file.exists():
        sample_file.unlink()
    notes = []
    opts = {"tabs": a.tabs, "resume": a.resume, "cache": a.cache, "page_timeout": a.page_timeout}
    if "http" not in skip:
        collect_http(cfg, raw)
    if "browser" not in skip:
        collect_browser(cfg, raw, find_axe(cfg), opts)
    if "interact" not in skip and cfg.get("interact") is not None:
        err = collect_interact(cfg, raw, opts)
        if err:
            notes.append(("interact", f"không chạy: {err}"))
    if "og" not in skip and (raw / "html").exists():
        collect_og_images(cfg, raw)
    if a.jev and "jev" not in skip:
        err = collect_jev(cfg, raw, a.jev_budget)
        if err:
            notes.append(("ui_visual", f"Jev không chạy: {err}"))
    if a.submit_live:
        submit_live(cfg, raw, a)
    rep = build_report(cfg, out, notes=notes)
    print(f"{rep['verdict']} -> {out / 'report.md'}")
    return 1 if rep["verdict"] == "FAIL" else 0


def cmd_report(a):
    cfg = load_config(a)
    mail = "ok" if a.mail_ok else ("missing" if a.mail_missing else None)
    live = Path(a.out) / "raw" / "form_live.json"
    if mail and live.exists() and json.loads(live.read_text(encoding="utf-8")).get("token") not in (a.mail_ok, a.mail_missing):
        sys.exit("token không khớp lượt gửi trong raw/form_live.json")
    rep = build_report(cfg, a.out, mail)
    print(f"{rep['verdict']} -> {Path(a.out) / 'report.md'}")
    return 1 if rep["verdict"] == "FAIL" else 0


def load_dir_pages(d, urls=None, pattern="*.html"):
    """Thư mục HTML đã lưu: <tên>.html, tuỳ chọn <tên>.hdr (dòng đầu 'HTTP/x 200') và <tên>.url."""
    m = {}
    if urls:
        m = {l.split("\t")[0]: l.split("\t")[1].strip() for l in Path(urls).read_text(encoding="utf-8").splitlines() if "\t" in l}
    pages = []
    for f in sorted(Path(d).glob(pattern)):
        hdr = f.with_suffix(".hdr")
        headers = hdr.read_text(encoding="utf-8", errors="replace") if hdr.exists() else ""
        st = re.match(r"HTTP/[\d.]+\s+(\d{3})", headers)
        uf = f.with_suffix(".url")
        url = m.get(f.stem) or (uf.read_text(encoding="utf-8").strip() if uf.exists() else None)
        pages.append({"name": f.stem, "url": url, "status": int(st.group(1)) if st else None, "headers": headers,
                      "html": f.read_text(encoding="utf-8", errors="replace")})
    return pages


def cmd_check(a):
    k, files = a.category, a.files
    if k == "overflow":
        res = check_overflow(records(files), [int(x) for x in a.widths.split(",")] if a.widths else None)
    elif k == "axe":
        res = check_axe(axe_records(records(files)), tuple(a.fail_impacts.split(",")), tuple(filter(None, (a.ignore or "").split(","))))
    elif k == "focus":
        res = check_focus(focus_records(records(files)))
    elif k == "http":
        res = check_http(parse_httpcheck_output(Path(files[0]).read_text(encoding="utf-8")))
    elif k == "plugins":
        res = check_plugins(*(Path(f).read_text(encoding="utf-8", errors="replace") for f in files[:2]), tuple(filter(None, (a.ignore or "").split(","))))
    elif k == "html":
        pages = load_dir_pages(files[0], a.urls, a.glob)
        for p in pages:
            p["parsed"] = parse_page(p["html"])
        exp = [x for x in (a.expect_tracking or "").split(",") if x]
        res = {"canonical": check_canonical(pages, a.canonical_host), "schema": check_schema(pages, a.canonical_host),
               "form": check_form(pages), "tracking": check_tracking(pages, exp)}
    elif k == "ui-visual":
        res = check_ui_visual(jl(files[0]), load_gates([a.registry], a.site, a.version))
    elif k in ("interact", "layout"):
        icfg = json.loads(Path(a.config).read_text(encoding="utf-8")).get("interact") if a.config else None
        rows = records(files)
        if k == "interact":
            res = qa_extra.check_interact(rows, icfg)
        else:
            res = qa_extra.check_layout(rows, records([a.landmarks]) if a.landmarks else (), icfg)
    elif k == "og":
        pages = load_dir_pages(files[0], a.urls, a.glob)
        for p in pages:
            p["parsed"] = parse_page(p["html"])
        images = {r["page"]: r for r in jl(a.images)} if a.images else {}
        res = qa_extra.check_og(pages, images, a.canonical_host)
    else:
        sys.exit(f"hạng mục không hỗ trợ: {k}")
    text = json.dumps(res, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "report"):
        s = sub.add_parser(name)
        s.add_argument("--config")
        s.add_argument("--base")
        s.add_argument("--urls", help="tên<TAB>đường dẫn mỗi dòng")
        s.add_argument("--widths", help="ví dụ 360,768,1366")
        s.add_argument("--out", required=True)
    r = sub.choices["run"]
    r.add_argument("--skip", help="bỏ phần thu thập: http,browser,interact,og,jev")
    r.add_argument("--jev", action="store_true", help="chấm ảnh chụp bằng Jev ui-visual")
    r.add_argument("--jev-budget", type=float, default=0.1)
    r.add_argument("--tabs", type=int, default=1, help="số Chrome chạy song song cho lượt đo trình duyệt (1 đến 6)")
    r.add_argument("--resume", action="store_true", help="không đo lại dòng đã đo tốt trong raw/browser.jsonl; giữ đúng mẫu của lượt trước")
    r.add_argument("--sample", help="chỉ chạy N URL hoặc P%% số URL trong config, ví dụ 12 hoặc 15%%")
    r.add_argument("--seed", type=int, default=1, help="hạt giống của --sample: cùng seed cho cùng mẫu")
    r.add_argument("--cache", choices=["cached", "nc", "both"], help="đo bản có cache, bản bỏ cache (?nc=) hoặc cả hai. Mặc định tải đúng URL đã cho")
    r.add_argument("--page-timeout", type=int, help="trần thời gian cho mỗi URL x bề rộng, mili giây (mặc định 120000)")
    r.add_argument("--plan", action="store_true", help="chỉ in kế hoạch (URL, bề rộng, variant), không đo, không ghi file")
    r.add_argument("--submit-live", action="store_true", help="GỬI FORM THẬT. Production cần --approved")
    r.add_argument("--approved", help="ghi chú duyệt cho lượt gửi thật trên production")
    rp = sub.choices["report"]
    rp.add_argument("--mail-ok", help="token lượt gửi thật đã thấy trong hộp mail")
    rp.add_argument("--mail-missing", help="token lượt gửi thật không thấy trong hộp mail")
    c = sub.add_parser("check")
    c.add_argument("category", choices=["overflow", "axe", "focus", "http", "plugins", "html", "ui-visual", "interact", "layout", "og"])
    c.add_argument("--config", help="check interact, layout: qa.json có khối interact (màu kit và ngưỡng)")
    c.add_argument("--landmarks", help="check layout: file landmarks.jsonl")
    c.add_argument("--images", help="check og: file og_images.jsonl")
    c.add_argument("files", nargs="+")
    c.add_argument("--widths")
    c.add_argument("--fail-impacts", default="critical,serious")
    c.add_argument("--ignore")
    c.add_argument("--urls")
    c.add_argument("--glob", default="*.html", help="check html: lọc file, ví dụ 'prod_*.html'")
    c.add_argument("--canonical-host")
    c.add_argument("--expect-tracking")
    c.add_argument("--registry")
    c.add_argument("--site", default="*")
    c.add_argument("--version", default="2026-10-17.2")
    c.add_argument("--out")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        if not 1 <= a.tabs <= 6:
            ap.error("--tabs phải từ 1 đến 6")
        if a.sample:
            try:
                qa_extra.apply_sample([], a.sample)
            except ValueError as e:
                ap.error(str(e))
    return {"run": cmd_run, "report": cmd_report, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
