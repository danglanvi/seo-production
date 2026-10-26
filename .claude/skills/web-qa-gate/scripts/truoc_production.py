#!/usr/bin/env python3
"""Kiểm phụ cho cổng trước production và chế độ audit đầu workstream của web-qa-gate.
Script chỉ đọc file đã lưu (thư mục out của qa_gate.py run), không gọi mạng, không ghi lên site.

  python3 -E truoc_production.py skeleton <out> [--ignore lang-switch,wpml-ls] [--out f.json]
      Header và footer giữa các template cùng <html lang>: so cấu trúc thẻ (FAIL khi lệch) và nội dung đã chuẩn hoá (WARN khi lệch).
      --ignore bỏ cây con có class hoặc id chứa chuỗi đã khai (vùng được phép khác giữa trang, ví dụ nút đổi ngôn ngữ).
      Đếm CSS, JS chặn render trong <head> của từng trang (WARN khi lệch từ 3 file giữa các template).
  python3 -E truoc_production.py diff <out A> <out B> [<out C>] [--labels prod,stg-moi,stg-cu] [--out f.json]
      So mã HTTP theo đường dẫn (bỏ tham số nc=), mã thẻ tracking trong HTML và số thẻ trong lưới (raw/interact.jsonl).
      Dùng cho: smoke trước và sau deploy, so 3 môi trường, so thẻ tracking production với staging, đếm thẻ trước và sau khi ghi.
  python3 -E truoc_production.py controls <out | thư mục html> [--out f.json]
      HTML server: link menu href="#" hoặc rỗng, phần tử không tương tác có onclick, link và nút không có tên.
  python3 -E truoc_production.py headers <out | thư mục html> [--out f.json]
      Header bảo mật trong file .hdr đã lưu: HSTS (trang https), X-Content-Type-Options nosniff, Referrer-Policy,
      Permissions-Policy, X-Frame-Options hoặc CSP frame-ancestors. Thiếu là WARN.
  python3 -E truoc_production.py urls <file URL mỗi dòng> --base <base> [--nc] > urls.tsv
      Đổi danh sách URL (ví dụ output wp post list --field=url) thành urls.tsv cho qa_gate.py run --urls.
Mã thoát: 0 PASS hoặc WARN, 1 FAIL, 2 sai tham số hoặc thiếu dữ liệu.
"""
import argparse
import hashlib
import json
import random
import re
import string
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_gate import tracking_ids  # noqa: E402

RANK = {"FAIL": 3, "WARN": 2, "PASS": 1, "SKIP": 0}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HEADER_HINT = re.compile(r"(^|[\s_-])(site-header|masthead|elementor-location-header|header-main)($|[\s_-])", re.I)
FOOTER_HINT = re.compile(r"(^|[\s_-])(site-footer|colophon|elementor-location-footer|footer-main)($|[\s_-])", re.I)
VOLATILE_CLASS = re.compile(r"^(.*current[-_].*|.*[-_]active|active|is-active|(mega-)?page[-_]item(-\d+)?|focus|hover)$", re.I)
LAZY_ATTR = {"src", "srcset", "sizes", "loading", "fetchpriority", "decoding", "data-lazyloaded", "data-no-lazy", "data-src", "data-srcset", "data-sizes"}
NONINTERACTIVE = {"div", "span", "li", "img", "section", "p", "td", "article", "figure", "i", "svg"}


def result(status, summary, findings=(), notes=()):
    return {"status": status, "summary": summary, "findings": list(findings), "notes": list(notes)}


def worst(findings):
    return max((f["level"] for f in findings), key=RANK.get, default="PASS")


def html_dir(d):
    d = Path(d)
    return d / "raw" / "html" if (d / "raw" / "html").is_dir() else d


def page_status(f):
    hdr = f.with_suffix(".hdr")
    codes = re.findall(r"(?m)^HTTP/[\d.]+\s+(\d{3})", hdr.read_text(encoding="utf-8", errors="replace")) if hdr.exists() else []
    return int(codes[-1]) if codes else None  # khối cuối khi file có cả bước redirect


def load_pages(d):
    pages = []
    for f in sorted(html_dir(d).glob("*.html")):
        st = page_status(f)
        if st in (200, None):
            pages.append((f.stem, f.read_text(encoding="utf-8", errors="replace")))
    return pages


class Regions(HTMLParser):
    """Lấy header và footer cấp trang (không nằm trong main, article), đếm CSS và JS chặn render trong head."""

    def __init__(self, ignore=()):
        super().__init__(convert_charrefs=True)
        self.ignore, self.skip = tuple(ignore), None
        self.stack, self.cur, self.done = [], None, {}
        self.buf = {"header": [], "footer": []}
        self.struct = {"header": [], "footer": []}
        self.block_css = self.block_js = 0
        self.lang = ""

    def _kind(self, t, a):
        if t in VOID or t in ("html", "head", "body", "script", "style", "template") or any(x in ("head", "main", "article") for x, _ in self.stack):
            return None
        cls = a.get("class", "") + " " + a.get("id", "")
        if t == "header" or HEADER_HINT.search(cls):
            return "header" if "header" not in self.done else None
        if t == "footer" or FOOTER_HINT.search(cls):
            return "footer"  # lấy footer cuối cùng của trang
        return None

    def handle_starttag(self, t, attrs):
        a = {k: (v or "") for k, v in attrs}
        if t == "html":
            self.lang = a.get("lang", "").split("-")[0].lower()
        in_head = any(x == "head" for x, _ in self.stack)
        if in_head and t == "link" and "stylesheet" in a.get("rel", "").lower().split() and a.get("media", "all") not in ("print",) and "onload" not in a and "disabled" not in a:
            self.block_css += 1
        if in_head and t == "script" and a.get("src") and not ({"async", "defer"} & set(a)) and a.get("type", "text/javascript") in ("", "text/javascript", "application/javascript"):
            self.block_js += 1
        if self.cur is None:
            k = self._kind(t, a)
            if k:
                self.cur = (k, len(self.stack))
                self.buf[k], self.struct[k] = [], []
        ign = self.cur and self.skip is None and any(x in a.get("class", "") + " " + a.get("id", "") for x in self.ignore)
        if ign and t not in VOID:
            self.skip = len(self.stack)  # bỏ cả cây con: vùng site khai được phép khác giữa trang (--ignore)
        if self.cur and self.skip is None and not ign:
            k = self.cur[0]
            ident = re.sub(r"\d+", "#", a.get("id", ""))
            self.struct[k].append(t + ("#" + ident if ident else ""))
            keep, a = [], dict(a)
            if t in ("img", "source", "iframe", "video"):
                # Plugin lazy-load đổi src, srcset, loading theo vị trí ảnh trên từng trang: chỉ giữ URL thật.
                real = a.get("data-src") or a.get("src", "")
                a = {n: v for n, v in a.items() if n not in LAZY_ATTR}
                a["src"] = "" if real.startswith("data:") else re.sub(r"\.(png|jpe?g|gif)\.webp$", r".\1", real)  # cache gắn .webp theo trình duyệt
            if t == "a" and "hreflang" in a:
                a.pop("href", None)  # nút đổi ngôn ngữ trỏ về chính trang đang xem
            for n, v in sorted(a.items()):
                if n in ("aria-current", "nonce", "data-nonce") or (n == "value" and a.get("type") == "hidden"):
                    continue
                if n == "class":
                    v = " ".join(c for c in v.split() if not VOLATILE_CLASS.match(c))
                v = re.sub(r"_wpnonce=[^&\"']+", "_wpnonce=", v)
                keep.append(f"{n}={v}")
            self.buf[k].append(f"<{t} {' '.join(keep)}>")
        if t not in VOID:
            self.stack.append((t, a))

    def handle_endtag(self, t):
        if t in VOID:
            return
        while self.stack:
            x, _ = self.stack.pop()
            if self.skip is not None and len(self.stack) == self.skip:
                self.skip = None
            if self.cur and len(self.stack) == self.cur[1]:
                self.done[self.cur[0]] = True
                self.cur = None
            if x == t:
                break

    def handle_data(self, d):
        if self.cur and self.skip is None and d.strip():
            self.buf[self.cur[0]].append(" ".join(d.split()))


def md5(parts):
    return hashlib.md5("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def cmd_skeleton(a):
    pages = load_pages(a.dir)
    if len(pages) < 2:
        return result("SKIP", f"cần ít nhất 2 trang 200, có {len(pages)}")
    rows, findings, notes = [], [], []
    ignore = [x.strip() for x in (getattr(a, "ignore", None) or "").split(",") if x.strip()]
    if ignore:
        notes.append(f"Bỏ khỏi phép so các vùng có class hoặc id chứa: {', '.join(ignore)}. Ghi lý do vào report.")
    for name, html in pages:
        p = Regions(ignore)
        p.feed(html)
        r = {"page": name, "lang": p.lang, "css_chan": p.block_css, "js_chan": p.block_js}
        for k in ("header", "footer"):
            r[k] = (md5(p.struct[k]), md5(p.buf[k])) if p.struct[k] else None
            if not p.struct[k]:
                findings.append({"level": "WARN", "page": name, "issue": f"không thấy {k} cấp trang (thẻ {k} hoặc class site-{k})"})
        rows.append(r)
    # Chỉ so trong cùng ngôn ngữ (<html lang>): bản EN có menu khác bản VI là chủ ý.
    for lang in sorted({r["lang"] for r in rows}):
        grp = [r for r in rows if r["lang"] == lang]
        tag = f" [lang {lang}]" if lang else ""
        if len(grp) < 2:
            notes.append(f"Ngôn ngữ {lang or 'không khai'} chỉ có 1 trang ({grp[0]['page']}): không có trang cùng ngôn ngữ để so.")
            continue
        for k in ("header", "footer"):
            by_struct, by_full = defaultdict(list), defaultdict(list)
            for r in grp:
                if r[k]:
                    by_struct[r[k][0]].append(r["page"])
                    by_full[r[k][1]].append(r["page"])
            if len(by_struct) > 1:
                groups = sorted(by_struct.values(), key=len, reverse=True)
                findings.append({"level": "FAIL", "page": ", ".join(groups[1][:6]), "issue": f"{k} khác cấu trúc thẻ với nhóm chính ({', '.join(groups[0][:6])}){tag}: template dùng {k} khác", "groups": groups})
            elif len(by_full) > 1:
                groups = sorted(by_full.values(), key=len, reverse=True)
                findings.append({"level": "WARN", "page": ", ".join(groups[1][:6]), "issue": f"{k} cùng cấu trúc nhưng khác chữ hoặc thuộc tính{tag}: xem diff 2 file HTML", "groups": groups})
    for key, label in (("css_chan", "CSS"), ("js_chan", "JS")):
        vals = [r[key] for r in rows]
        if max(vals) - min(vals) >= 3:
            hi = [r["page"] for r in rows if r[key] == max(vals)]
            findings.append({"level": "WARN", "page": ", ".join(hi[:6]), "issue": f"{label} chặn render trong head lệch giữa template: {min(vals)} đến {max(vals)} file"})
    notes.append("Số file chặn render mỗi trang: " + "; ".join(f"{r['page']} CSS {r['css_chan']}, JS {r['js_chan']}" for r in rows))
    notes.append("H1 kiểm ở hạng mục 14e (DOM đã render). Canonical kiểm ở hạng mục 9.")
    st = worst(findings)
    return result(st, f"{len(rows)} trang, {sum(f['level'] == 'FAIL' for f in findings)} lỗi cấu trúc header/footer", findings, notes)


def norm_path(p):
    s = urlsplit(p)
    q = [(k, v) for k, v in parse_qsl(s.query, keep_blank_values=True) if k != "nc"]
    return urlunsplit(("", "", s.path or "/", urlencode(q), ""))


def load_run(d):
    raw = Path(d) / "raw"
    if not (raw / "http.jsonl").exists():
        sys.exit(f"thiếu {raw / 'http.jsonl'}: chạy qa_gate.py run trước")
    rows = [json.loads(l) for l in (raw / "http.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    codes, names = {}, {}
    for r in rows:
        if r.get("kind") == "page":
            codes[norm_path(r["path"])] = str(r.get("final_code") or r.get("code"))
            names[r["name"]] = norm_path(r["path"])
        elif r.get("kind") == "http":
            codes[norm_path(r["path"])] = str(r.get("code"))
    tags = {}
    for name, path in names.items():
        f = raw / "html" / f"{name}.html"
        if f.exists():
            tags[path] = set(tracking_ids(f.read_text(encoding="utf-8", errors="replace")))
    grids = {}
    if (raw / "interact.jsonl").exists():
        for l in (raw / "interact.jsonl").read_text(encoding="utf-8").splitlines():
            r = json.loads(l) if l.strip() else {}
            for g in (r.get("layout") or {}).get("grids") or []:
                grids[(r.get("name"), r.get("vw"), g.get("sel"))] = g.get("n")
    return codes, tags, grids


def bad_change(a, b):
    return b.startswith("5") or b == "000" or (a.startswith("2") and not b.startswith("2"))


def cmd_diff(a):
    if not 2 <= len(a.dirs) <= 3:
        sys.exit("diff nhận 2 hoặc 3 thư mục out")
    labels = a.labels.split(",") if a.labels else [Path(d).name for d in a.dirs]
    if len(labels) != len(a.dirs):
        sys.exit("--labels phải có đúng số nhãn bằng số thư mục")
    runs = [load_run(d) for d in a.dirs]
    findings = []
    paths = sorted(set().union(*(r[0] for r in runs)))
    for p in paths:
        cs = [r[0].get(p) for r in runs]
        if None in cs:
            findings.append({"level": "WARN", "path": p, "issue": "thiếu ở " + ", ".join(l for l, c in zip(labels, cs) if c is None)})
            continue
        if len(set(cs)) == 1:
            continue
        f = {"path": p, "codes": dict(zip(labels, cs)), "level": "FAIL" if any(bad_change(cs[0], c) for c in cs[1:]) else "WARN"}
        if len(cs) == 3:
            x, y, z = cs
            f["issue"] = (f"lệch chỉ ở {labels[1]}: nghi do theme hoặc bản mới" if y != x and z == x else
                          f"{labels[1]} và {labels[2]} cùng lệch với {labels[0]}: nghi do dữ liệu" if y == z != x else "lệch nhiều phía")
        else:
            f["issue"] = f"mã đổi {cs[0]} → {cs[1]}"
        findings.append(f)
    for p in sorted(set(runs[0][1]) & set().union(*(r[1] for r in runs[1:]))):
        base = runs[0][1][p]
        for lab, r in zip(labels[1:], runs[1:]):
            if p not in r[1]:
                continue
            miss, extra = base - r[1][p], r[1][p] - base
            if miss:
                findings.append({"level": "FAIL", "path": p, "issue": f"thẻ tracking có ở {labels[0]} mà không có ở {lab}: {', '.join(sorted(miss))}"})
            if extra:
                findings.append({"level": "WARN", "path": p, "issue": f"thẻ tracking chỉ có ở {lab}: {', '.join(sorted(extra))}"})
    for key in sorted(set(runs[0][2]) & set().union(*(r[2] for r in runs[1:])), key=str):
        ns = [r[2].get(key) for r in runs]
        if len(set(n for n in ns if n is not None)) > 1:
            findings.append({"level": "WARN", "path": f"{key[0]} {key[1]}px {key[2]}", "issue": "số thẻ trong lưới đổi: " + ", ".join(f"{l} {n}" for l, n in zip(labels, ns))})
    notes = ["Lượt smoke có tham số nc= thì bỏ qua kết luận canonical trong report.md của lượt đó: chỉ đọc kết quả diff."]
    st = worst(findings)
    return result(st, f"{len(paths)} đường dẫn, {sum(f['level'] == 'FAIL' for f in findings)} FAIL, {sum(f['level'] == 'WARN' for f in findings)} WARN", findings, notes)


class Controls(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.open = [], []
        self.dead_menu, self.onclick, self.noname = [], [], []

    @staticmethod
    def sel(t, a):
        s = t + (f"#{a['id']}" if a.get("id") else "")
        return s + "".join("." + c for c in a.get("class", "").split()[:2])

    def handle_starttag(self, t, attrs):
        a = {k: (v or "") for k, v in attrs}
        in_nav = any(x in ("nav", "header") or r == "navigation" for x, r in self.stack)
        if t == "a" and in_nav and "href" in a and (a["href"].strip() in ("", "#") or a["href"].strip().lower().startswith("javascript:")):
            self.dead_menu.append(self.sel(t, a))
        if t in NONINTERACTIVE and "onclick" in a:
            self.onclick.append(self.sel(t, a))
        for o in self.open:
            if t == "img" and a.get("alt", "").strip():
                o["named"] = True
            if t == "svg" and (a.get("aria-label") or "").strip():
                o["named"] = True
        if (t == "a" and "href" in a) or t == "button":
            named = any((a.get(k) or "").strip() for k in ("aria-label", "aria-labelledby", "title"))
            if a.get("aria-hidden") != "true":
                self.open.append({"sel": self.sel(t, a), "tag": t, "named": named})
        if t not in VOID:
            self.stack.append((t, a.get("role", "")))

    def handle_data(self, d):
        if d.strip():
            for o in self.open:
                o["named"] = True

    def handle_endtag(self, t):
        if t in ("a", "button"):
            for i in range(len(self.open) - 1, -1, -1):
                if self.open[i]["tag"] == t:
                    o = self.open.pop(i)
                    if not o["named"]:
                        self.noname.append(o["sel"])
                    break
        if t in VOID:
            return
        while self.stack:
            if self.stack.pop()[0] == t:
                break


def cmd_controls(a):
    pages = load_pages(a.dir)
    if not pages:
        return result("SKIP", "không có HTML trang 200")
    findings = []
    for name, html in pages:
        p = Controls()
        p.feed(html)
        for lst, issue in ((p.dead_menu, 'link trong nav/header có href="#", rỗng hoặc javascript:'),
                           (p.onclick, "phần tử không tương tác có onclick (bàn phím không tới được)"),
                           (p.noname, "link hoặc nút không có tên trong HTML server")):
            if lst:
                findings.append({"level": "WARN", "page": name, "issue": f"{len(lst)} {issue}", "examples": sorted(set(lst))[:5]})
    notes = ["Các dòng này là WARN: axe (hạng mục 2) và focus (hạng mục 3) trên DOM đã render là phép đo chặn."]
    return result(worst(findings), f"{len(pages)} trang, {len({f['page'] for f in findings})} trang có điều khiển cần xem", findings, notes)


SEC_HEADERS = (("strict-transport-security", "HSTS", None), ("x-content-type-options", "X-Content-Type-Options", "nosniff"),
               ("referrer-policy", "Referrer-Policy", None), ("permissions-policy", "Permissions-Policy", None))


def last_headers(text):
    """File .hdr có thể chứa nhiều khối khi có redirect: lấy khối cuối."""
    blocks = re.split(r"(?m)^(?=HTTP/[\d.]+\s+\d{3})", text)
    h = {}
    for line in (blocks[-1] if blocks else "").splitlines()[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            h.setdefault(k.strip().lower(), v.strip())
    return h


def cmd_headers(a):
    d = html_dir(a.dir)
    files = [f for f in sorted(d.glob("*.hdr")) if page_status(f) == 200]
    if not files:
        return result("SKIP", "không có file .hdr của trang 200")
    findings, seen = [], defaultdict(list)
    for f in files:
        h = last_headers(f.read_text(encoding="utf-8", errors="replace"))
        uf = f.with_suffix(".url")
        https = (uf.read_text(encoding="utf-8").strip() if uf.exists() else "https://").startswith("https://")
        miss = []
        for key, label, need in SEC_HEADERS:
            if key == "strict-transport-security" and not https:
                continue
            v = h.get(key)
            if v is None or (need and need not in v.lower()):
                miss.append(label)
        if not (h.get("x-frame-options") or "frame-ancestors" in h.get("content-security-policy", "")):
            miss.append("X-Frame-Options hoặc CSP frame-ancestors")
        for m in miss:
            seen[m].append(f.stem)
    for m, pages in seen.items():
        findings.append({"level": "WARN", "page": ", ".join(pages[:6]), "issue": f"thiếu {m} trên {len(pages)}/{len(files)} trang"})
    notes = ["Header bảo mật là quyết định của site: đối chiếu skill wp-security-hardening trước khi kết luận. Header có thể do CDN thêm, nên kiểm cả bản production."]
    return result(worst(findings), f"{len(files)} trang, {len(seen)} loại header thiếu", findings, notes)


def slug(path):
    s = re.sub(r"[^a-z0-9]+", "-", urlsplit(path).path.lower()).strip("-")
    return s[:60] or "home"


def cmd_urls(a):
    base = urlsplit(a.base)
    seen, out = defaultdict(int), []
    for line in Path(a.file).read_text(encoding="utf-8").splitlines():
        u = line.strip()
        if not u or u.startswith("#"):
            continue
        s = urlsplit(u)
        path = urlunsplit(("", "", s.path or "/", s.query, "")) if s.netloc in ("", base.netloc) else u
        if a.nc:
            path += ("&" if "?" in path else "?") + "nc=" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        n = slug(u)
        seen[n] += 1
        out.append(f"{n if seen[n] == 1 else f'{n}-{seen[n]}'}\t{path}")
    print("\n".join(out))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("skeleton", "controls", "headers"):
        s = sub.add_parser(name)
        s.add_argument("dir")
        s.add_argument("--out")
        if name == "skeleton":
            s.add_argument("--ignore", help="chuỗi con của class hoặc id, ngăn bằng dấu phẩy: vùng được phép khác giữa trang (ví dụ nút đổi ngôn ngữ)")
    d = sub.add_parser("diff")
    d.add_argument("dirs", nargs="+")
    d.add_argument("--labels")
    d.add_argument("--out")
    u = sub.add_parser("urls")
    u.add_argument("file")
    u.add_argument("--base", required=True)
    u.add_argument("--nc", action="store_true", help="thêm tham số nc=<ngẫu nhiên> để bỏ cache")
    a = ap.parse_args(argv)
    if a.cmd == "urls":
        return cmd_urls(a)
    src = a.dir if a.cmd != "diff" else a.dirs[0]
    if not Path(src).is_dir():
        print(f"không thấy thư mục: {src}", file=sys.stderr)
        return 2
    res = {"skeleton": cmd_skeleton, "controls": cmd_controls, "headers": cmd_headers, "diff": cmd_diff}[a.cmd](a)
    text = json.dumps(res, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 1 if res["status"] == "FAIL" else (2 if res["status"] == "SKIP" else 0)


if __name__ == "__main__":
    sys.exit(main())
