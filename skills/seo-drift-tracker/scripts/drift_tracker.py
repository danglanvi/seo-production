#!/usr/bin/env python3
"""Snapshot raw-HTML SEO elements, compare immutable snapshots, inspect history.

Python standard library only. See --help and ../references/cli.md.
"""

import argparse
import csv
import datetime as dt
import json
import re
import sqlite3
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

USER_AGENT = "GTV-SEO-Drift/1.0"
METHOD = "raw-html-v1; user-agent=" + USER_AGENT
ELEMENTS = ("http", "title", "description", "canonical", "robots", "h1",
            "hreflang", "schema_types", "internal_links")
ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


def normalize_url(value):
    value = urldefrag(value.strip())[0]
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL phải là HTTP(S), có hostname và không chứa credential")
    return value


def url_list(path):
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "url" not in reader.fieldnames:
                raise ValueError("CSV cần cột url")
            values = [row["url"] for row in reader]
    else:
        values = path.read_text(encoding="utf-8-sig").splitlines()
    urls = list(dict.fromkeys(normalize_url(v) for v in values if v.strip() and not v.lstrip().startswith("#")))
    if not urls:
        raise ValueError("Danh sách URL rỗng")
    return urls


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles, self.h1s, self.descriptions = [], [], []
        self.canonicals, self.alternates, self.links, self.robots = [], [], [], []
        self.base = None
        self.capture = None
        self.text_parts = []
        self.schema_types = set()
        self.warnings = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "base" and self.base is None and attrs.get("href"):
            self.base = attrs["href"]
        if tag in ("title", "h1") or (tag == "script" and attrs.get("type", "").lower().split(";")[0] == "application/ld+json"):
            self.capture, self.text_parts = tag, []
        if tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.descriptions.append(attrs.get("content", ""))
            if name == "robots":
                self.robots.append(attrs.get("content", "").strip().lower())
        if tag == "link" and attrs.get("href"):
            rel = attrs.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonicals.append(attrs["href"])
            if "alternate" in rel and attrs.get("hreflang"):
                self.alternates.append((attrs["hreflang"].lower(), attrs["href"]))
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_data(self, data):
        if self.capture:
            self.text_parts.append(data)

    def handle_endtag(self, tag):
        if tag != self.capture:
            return
        raw = "".join(self.text_parts)
        if tag == "script":
            try:
                self.collect_types(json.loads(raw))
            except (ValueError, RecursionError):
                self.warnings.append("JSON-LD không parse được; không so schema_types")
        else:
            text = " ".join(raw.split())
            (self.titles if tag == "title" else self.h1s).append(text)
        self.capture, self.text_parts = None, []

    def collect_types(self, value):
        if isinstance(value, dict):
            types = value.get("@type", [])
            for kind in ([types] if isinstance(types, str) else types if isinstance(types, list) else []):
                if isinstance(kind, str):
                    self.schema_types.add(kind)
            for child in value.values():
                self.collect_types(child)
        elif isinstance(value, list):
            for child in value:
                self.collect_types(child)


def extract(html, final_url, status, redirects=(), robots_headers=()):
    parser = SEOParser()
    parser.feed(html)
    parser.close()
    if parser.capture == "script":
        parser.warnings.append("JSON-LD chưa đóng; không so schema_types")
    base = urljoin(final_url, parser.base or "")
    internal = sum(1 for href in parser.links
                   if urlsplit(urljoin(base, href)).scheme in ("http", "https")
                   and urlsplit(urljoin(base, href)).hostname == urlsplit(final_url).hostname)
    return {
        "http": {"status": status, "final_url": final_url, "redirects": list(redirects)},
        "title": parser.titles,
        "description": [" ".join(v.split()) for v in parser.descriptions],
        "canonical": sorted(urljoin(base, v) for v in parser.canonicals),
        "robots": sorted(set(parser.robots + [v.strip().lower() for v in robots_headers])),
        "h1": {"count": len(parser.h1s), "texts": parser.h1s},
        "hreflang": sorted(set((lang, urljoin(base, href)) for lang, href in parser.alternates)),
        "schema_types": sorted(parser.schema_types),
        "internal_links": internal,
    }, parser.warnings


class Redirects(HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        normalize_url(newurl)
        self.chain.append({"status": code, "url": req.full_url, "location": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=15, interval=1):
    for attempt in range(2):
        redirects = Redirects()
        try:
            opener = build_opener(redirects)
            request = Request(url, headers={"User-Agent": USER_AGENT})
            try:
                response = opener.open(request, timeout=timeout)
            except HTTPError as exc:
                if 300 <= exc.code < 400:
                    raise URLError("Redirect không hoàn tất") from exc
                response = exc
            with response:
                status = response.code
                if status >= 500 and attempt == 0:
                    time.sleep(interval)
                    continue
                data = response.read(5 * 1024 * 1024 + 1)
                if len(data) > 5 * 1024 * 1024:
                    raise ValueError("Response vượt 5 MiB; không parse HTML bị cắt")
                final_url = response.geturl()
                normalize_url(final_url)
                encoding = response.headers.get_content_charset() or "utf-8"
                html = data.decode(encoding, errors="replace")
                values, warnings = extract(html, final_url, status, redirects.chain,
                                           response.headers.get_all("X-Robots-Tag", []))
                # Error documents are not the original page: compare HTTP only.
                unavailable = list(ELEMENTS[1:]) if status >= 400 else []
                if response.headers.get_content_type() not in ("text/html", "application/xhtml+xml"):
                    unavailable = list(ELEMENTS[1:])
                    warnings.append("Response không phải HTML; chỉ so HTTP")
                if warnings and "schema_types" not in unavailable:
                    unavailable.append("schema_types")
                return {"url": url, "values": values, "error": None,
                        "unavailable": unavailable, "warnings": warnings}
        except (OSError, ValueError, LookupError, RecursionError) as exc:
            if attempt == 0:
                time.sleep(interval)
                continue
            return {"url": url, "values": {}, "error": "FETCH_ERROR: " + type(exc).__name__,
                    "unavailable": list(ELEMENTS), "warnings": []}


def connect(path, create=False):
    if not path.exists() and not create:
        raise ValueError("Chưa có store; chạy baseline trước")
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=20)
    db.row_factory = sqlite3.Row
    if create:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY, ts TEXT NOT NULL, label TEXT NOT NULL,
                kind TEXT NOT NULL, method TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pages (
                snapshot_id INTEGER NOT NULL, url TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY (snapshot_id, url));
        """)
    return db


def save_snapshot(db, label, kind, pages):
    with db:
        cursor = db.execute("INSERT INTO snapshots(ts,label,kind,method) VALUES (?,?,?,?)",
                            (dt.datetime.now(dt.timezone.utc).isoformat(), label, kind, METHOD))
        snapshot_id = cursor.lastrowid
        db.executemany("INSERT INTO pages VALUES (?,?,?)",
                       [(snapshot_id, p["url"], json.dumps(p, ensure_ascii=False)) for p in pages])
    return snapshot_id


def read_snapshot(db, snapshot_id=None):
    row = db.execute("SELECT * FROM snapshots WHERE id=?", (snapshot_id,)).fetchone() if snapshot_id else db.execute(
        "SELECT * FROM snapshots WHERE kind='baseline' ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        raise ValueError("Không tìm thấy baseline/snapshot được yêu cầu")
    pages = {p["url"]: json.loads(p["payload"]) for p in db.execute(
        "SELECT url,payload FROM pages WHERE snapshot_id=? ORDER BY url", (row["id"],))}
    return dict(row), pages


def severity(element, before, after):
    if element in ("http", "canonical"):
        return "CRITICAL"
    if element == "robots":
        def restrictions(value):
            tokens = set(re.findall(r"[a-z]+", " ".join(value)))
            if "none" in tokens:
                tokens.update(("noindex", "nofollow"))
            return tokens & {"noindex", "nofollow"}
        return "CRITICAL" if restrictions(after) - restrictions(before) else "INFO"
    if element in ("title", "h1", "hreflang"):
        return "HIGH"
    if element == "schema_types":
        return "HIGH" if set(before) - set(after) else "MEDIUM"
    if element == "internal_links":
        delta = abs(after - before) / before if before else (float("inf") if after else 0)
        return "MEDIUM" if delta > 0.2 else "INFO"
    return "MEDIUM"


def compare(before, after):
    findings, unavailable = [], []
    for url in sorted(set(before) | set(after)):
        if url not in before or url not in after:
            findings.append({"url": url, "element": "url_list", "before": url in before,
                             "after": url in after, "severity": "INFO"})
            continue
        old, new = before[url], after[url]
        if old.get("error") or new.get("error"):
            unavailable.append({"url": url, "reason": {"baseline": old.get("error"), "current": new.get("error")}})
            continue
        skipped = set(old.get("unavailable", [])) | set(new.get("unavailable", []))
        if skipped:
            unavailable.append({"url": url, "reason": "Không so: " + ", ".join(sorted(skipped))})
        for element in ELEMENTS:
            if element in skipped:
                continue
            a, b = old["values"][element], new["values"][element]
            # JSON round trip makes tuple/list representation irrelevant.
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                findings.append({"url": url, "element": element, "before": a, "after": b,
                                 "severity": severity(element, a, b)})
    findings.sort(key=lambda f: (ORDER[f["severity"]], f["url"], f["element"]))
    for finding in findings:
        finding["intentional"] = "Account/khách xác nhận"
        if finding["severity"] in ("CRITICAL", "HIGH"):
            finding["falsifiability"] = "Đối chiếu kế hoạch deploy và xác nhận chủ đích; đổi có kế hoạch chưa phải regression."
            finding["leading_indicator"] = "Kiểm URL Inspection và theo dõi impressions URL trong 2–4 tuần."
    return findings, unavailable


def emit(result, as_json):
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print("# SEO Drift — " + result["mode"])
    print("\nDATA TIER: A — SQLite · raw HTML · " + METHOD)
    for key in ("baseline", "snapshot"):
        if key in result:
            item = result[key]
            print(f"\n{key}: #{item['id']} · {item['label']} · {item['ts']}")
    if "findings" in result:
        print("\n" + " · ".join(f"{level}: {sum(f['severity'] == level for f in result['findings'])}" for level in ORDER))
        print("\n| Mức | URL | Element | Trước | Sau | Chủ đích? |\n|---|---|---|---|---|---|")
        def cell(v):
            return json.dumps(v, ensure_ascii=False).replace("|", "&#124;").replace("<", "&lt;").replace(">", "&gt;")
        for finding in result["findings"]:
            print("| " + " | ".join(cell(finding[k]) for k in ("severity", "url", "element", "before", "after", "intentional")) + " |")
        if any(f["severity"] in ("CRITICAL", "HIGH") for f in result["findings"]):
            print("\nVới CRITICAL/HIGH: đối chiếu kế hoạch deploy để loại cảnh báo sai; kiểm URL Inspection và impressions 2–4 tuần. CRITICAL cần chuyển Account/dev xác minh trong ngày.")
    for key in ("unavailable", "errors", "history"):
        if result.get(key):
            print("\n" + key + ":\n\n```json\n" + json.dumps(result[key], ensure_ascii=False, indent=2) + "\n```")
    if "urls" in result:
        print(f"\nURLs: {result['urls']} · FETCH_ERROR: {len(result.get('errors', []))}")


def positive(value):
    number = float(value)
    if not 0 < number < float("inf"):
        raise argparse.ArgumentTypeError("cần số dương hữu hạn")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in ("baseline", "compare"):
        sub = commands.add_parser(mode)
        sub.add_argument("--urls", type=Path, required=mode == "baseline")
        sub.add_argument("--label", required=True)
        sub.add_argument("--timeout", type=positive, default=15)
        sub.add_argument("--interval", type=positive, default=1)
        sub.add_argument("--allow-large", action="store_true", help="Xác nhận phạm vi >200 URL đã được duyệt")
        if mode == "compare":
            sub.add_argument("--baseline-id", type=int)
    history = commands.add_parser("history")
    history.add_argument("--url")
    history.add_argument("--element", choices=ELEMENTS)
    args = parser.parse_args(argv)
    db = None
    try:
        if args.mode != "history" and (not args.label.strip() or args.interval < 0.5):
            raise ValueError("Label phải có nội dung; interval tối thiểu 0.5 giây")
        db = connect(args.db, create=args.mode == "baseline")
        if args.mode == "history":
            if args.url:
                args.url = normalize_url(args.url)
            rows = db.execute("SELECT s.id,s.ts,s.label,p.url,p.payload FROM snapshots s JOIN pages p ON p.snapshot_id=s.id ORDER BY s.id,p.url")
            values = []
            for row in rows:
                if args.url and row["url"] != args.url:
                    continue
                payload = json.loads(row["payload"])
                values.append({"id": row["id"], "ts": row["ts"], "label": row["label"], "url": row["url"],
                               "value": payload["values"].get(args.element) if args.element else payload["values"],
                               "error": payload["error"], "unavailable": payload["unavailable"]})
            emit({"mode": "history", "history": values}, args.json)
            return 0
        baseline, old_pages = read_snapshot(db, args.baseline_id) if args.mode == "compare" else (None, {})
        if baseline and baseline["method"] != METHOD:
            raise ValueError("Phương pháp fetch khác baseline; không so hai phương pháp")
        urls = url_list(args.urls) if args.urls else list(old_pages)
        if len(urls) > 200 and not args.allow_large:
            raise ValueError("Hơn 200 URL: cần duyệt phạm vi/rate limit trước, rồi dùng --allow-large")
        pages = []
        for index, url in enumerate(urls):
            if index:
                time.sleep(args.interval)
            pages.append(fetch(url, args.timeout, args.interval))
        snapshot_id = save_snapshot(db, args.label.strip(), args.mode, pages)
        snapshot, current = read_snapshot(db, snapshot_id)
        result = {"mode": args.mode, "snapshot": snapshot, "urls": len(urls),
                  "errors": [{"url": p["url"], "error": p["error"]} for p in pages if p["error"]],
                  "unavailable": [{"url": p["url"], "reason": "Không so: " + ", ".join(p["unavailable"])}
                                  for p in pages if p["unavailable"] and not p["error"]]}
        if baseline:
            result["baseline"] = baseline
            result["findings"], result["unavailable"] = compare(old_pages, current)
        emit(result, args.json)
        if result["errors"] or result.get("unavailable"):
            return 2
        return 1 if any(f["severity"] in ("CRITICAL", "HIGH") for f in result.get("findings", [])) else 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
