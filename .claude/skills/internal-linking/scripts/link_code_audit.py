#!/usr/bin/env python3
"""link_code_audit.py - kiểm kê dạng mã của mọi phần tử bấm được trên trang HTML đã lưu (offline).

Làm bước 1 và một phần bước 2 của references/link-js.md §6, trước đây làm tay. Chỉ đọc file, không gọi site.

Lệnh:
  scan     quét file hoặc thư mục .html / .html.gz, in bảng vùng x dạng mã và các cờ vi phạm luật §3
  compare  so 2 file summary.json (trước và sau khi sửa template): đếm link thật mỗi trang theo vùng (luật 8)

Phần tử bấm được: <a> (có hoặc không href), <button>, <input submit|button>, thẻ có onclick, data-href, role=link|button.
Dạng hiện tại (cột code), chưa phải đề xuất. Đề xuất cần Jev link-purpose và Claude đọc (link-js.md §6 bước 3-5):
  D1 link thật <a href> (gồm tel, mailto) · D2 cuộn tới #neo (a href=#x, button scroll) · D3 button location.href
  D4 span/div onclick location · D5 mở tab ngoài (window.open) · lai (a href kèm onclick điều hướng, javascript:, a không href
  có chữ, href=# mở menu) · lỗi (href rỗng hoặc #) · UI (nút form, neo id, không điều hướng)

Vùng: header, footer, nav, sidebar, popup, breadcrumb, toc, body (kèm zone MC/SC theo H2 như the_link.py), hoặc vùng riêng
khai bằng --region "tên=REGEX" (khớp class hoặc id của thẻ tổ tiên, kiểm trước các vùng mặc định).

Cờ theo luật §3 của link-js.md:
  lai (luật 3) · thieu_ban_phim (luật 6: span/div điều hướng thiếu role và tabindex) · thieu_noopener (luật 6)
  link_that_toi_noindex (luật 5, cần --noindex hoặc trang quét có meta noindex)
  doch_chi_co_link_js (luật 2: đích nội bộ chỉ có link JS trong tập đã quét; tập nhỏ thì cờ này không đủ bằng chứng)
  doch_khong_trong_sitemap (luật 2, cần --sitemap)

Không ghi file nếu không có --out DIR (inventory.jsonl, templates.tsv, summary.json).
Mã thoát: 0 quét xong · 1 lỗi đầu vào · 2 sai tham số · 3 (scan --fail-on-flags) có cờ · 3 (compare) link thật ở body giảm.

Ví dụ:
  link_code_audit.py scan pages/ --host vidu.vn --noindex noindex.txt --out audit/
  link_code_audit.py compare audit_truoc/summary.json audit_sau/summary.json
"""
import argparse
import collections
import gzip
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col", "embed", "param", "track", "wbr"}
NAV_JS = re.compile(r"(?:window\.|document\.)?location(?:\.href)?\s*=\s*['\"]([^'\"]+)|location\.(?:assign|replace)\(\s*['\"]([^'\"]+)"
                    r"|window\.open\(\s*['\"]([^'\"]+)")
TRACK_JS = re.compile(r"gtag\(|dataLayer\.push|fbq\(|ga\(|_paq")
SC_DEFAULT = (r"faq|câu hỏi|hỏi đáp|kết luận|lời kết|tổng kết|tóm lại|giới thiệu (?:về )?(?:công ty|doanh nghiệp|chúng tôi)"
              r"|về chúng tôi|dịch vụ của (?:công ty|chúng tôi)|đọc thêm|bài viết liên quan|liên hệ")
FORM_CODE = {"a_href": "D1", "a_tel": "D1", "a_frag": "D2", "button_scroll": "D2", "span_scroll": "D2", "button_loc": "D3",
             "span_loc": "D4", "button_open": "D5", "span_open": "D5", "a_javascript": "lai", "a_href_onclick": "lai",
             "a_nohref_onclick": "lai", "ui_submit": "UI", "ui_button": "UI", "ui_other": "UI"}


class Err(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


def sp(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def path_of(u, hosts):
    """Link nội bộ → path (giữ query, bỏ fragment). Ngoài site → None."""
    u = html.unescape((u or "").strip())
    if u.startswith("//"):
        u = "https:" + u
    m = re.match(r"^https?://([^/?#]+)([^#]*)", u, re.I)
    if m:
        host = m.group(1).lower()
        host = host[4:] if host.startswith("www.") else host
        if host not in hosts:
            return None
        u = m.group(2) or "/"
    if u.startswith("/") and not u.startswith("//"):
        u = u.split("#")[0]
        return (u.rstrip("/") or "/") if "?" not in u else u
    return None


def classify(tag, attrs, hosts):
    """Trả (form, js_target, tkind, target)."""
    href = attrs.get("href") if tag == "a" else None
    onclick = attrs.get("onclick") or ""
    m = NAV_JS.search(onclick)
    js = next((g for g in m.groups() if g), "") if m else ""
    if not js and attrs.get("data-href"):
        js = attrs["data-href"]
    if tag == "a":
        if href is None:
            form = "a_nohref_onclick" if onclick else "a_nohref"
        else:
            h = href.strip()
            if h.lower().startswith("javascript"):
                form = "a_javascript"
            elif onclick and (js or re.search(r"return false|preventDefault", onclick)):
                form = "a_href_onclick"
            elif h in ("", "#"):
                form = "a_hash"
            elif h.startswith("#"):
                form = "a_frag"
            elif re.match(r"^(tel|mailto|sms):", h, re.I):
                form = "a_tel"
            else:
                form = "a_href"
    elif tag in ("button", "input"):
        if js:
            form = "button_scroll" if js.startswith("#") else "button_loc" if path_of(js, hosts) is not None else "button_open"
        else:
            form = "ui_submit" if (attrs.get("type") or "").lower() == "submit" else "ui_button"
    elif js:
        form = "span_scroll" if js.startswith("#") else "span_loc" if path_of(js, hosts) is not None else "span_open"
    else:
        form = "ui_other"
    raw = href if href is not None else js
    raw = (raw or "").strip()
    if raw.startswith("#"):
        return form, js, "fragment", raw
    if re.match(r"^(tel|mailto|sms):", raw, re.I):
        return form, js, "tel", raw
    p = path_of(raw, hosts) if raw else None
    if p is not None:
        return form, js, "internal", p
    if re.match(r"^(https?:)?//", raw):
        return form, js, "external", raw
    return form, js, ("other" if raw and not raw.lower().startswith("javascript") else "none"), raw


class Page(HTMLParser):
    def __init__(self, regions, hosts):
        super().__init__(convert_charrefs=True)
        self.regions, self.hosts = regions, hosts
        self.stack, self.recs, self.open = [], [], []
        self.h2 = []  # (title, region)
        self.h2_open = None
        self.canonical = self.robots = None

    def _region(self):
        names = [(t, a) for t, a in self.stack]
        cls = lambda a: " ".join([a.get("class") or "", a.get("id") or ""])
        for name, rx in self.regions:
            if any(re.search(rx, cls(a), re.I) for _, a in names):
                return name
        if any(re.search(r"(^|[\s_-])(popup|modal|dialog)([\s_-]|$)", cls(a), re.I) or a.get("role") == "dialog" for _, a in names):
            return "popup"
        for t, a in names:
            if t == "header" or a.get("role") == "banner":
                return "header"
        for t, a in names:
            if t == "footer" or a.get("role") == "contentinfo":
                return "footer"
        if any(t == "aside" for t, _ in names):
            return "sidebar"
        if any(re.search(r"breadcrumb", cls(a), re.I) for _, a in names):
            return "breadcrumb"
        if any(re.search(r"(^|[\s_-])(toc|ez-toc|table-of-contents)", cls(a), re.I) for _, a in names):
            return "toc"
        if any(t == "nav" or a.get("role") == "navigation" for t, a in names):
            return "nav"
        return "body"

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: (v if v is not None else "") for k, v in attrs_list}
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower():
            self.canonical = attrs.get("href")
        if tag == "meta" and (attrs.get("name") or "").lower() in ("robots", "googlebot"):
            self.robots = ((self.robots or "") + "," + attrs.get("content", "")).strip(",")
        if tag == "h2":
            self.h2_open = {"region": self._region(), "text": []}
        clickable = (tag in ("a", "button") or "onclick" in attrs or "data-href" in attrs or attrs.get("role") in ("link", "button")
                     or (tag == "input" and (attrs.get("type") or "").lower() in ("submit", "button")))
        if clickable:
            form, js, tkind, target = classify(tag, attrs, self.hosts)
            rec = {"tag": tag, "form": form, "js_target": js[:300], "tkind": tkind, "target": target[:400],
                   "href": attrs.get("href") if tag == "a" else None, "onclick": (attrs.get("onclick") or "")[:200],
                   "aria": sp(attrs.get("aria-label")), "alt": "", "rel": attrs.get("rel", ""), "target_attr": attrs.get("target", ""),
                   "role": attrs.get("role", ""), "tabindex": attrs.get("tabindex", ""),
                   "aria_expanded": any(k in attrs for k in ("aria-expanded", "aria-haspopup", "aria-controls")),
                   "id": attrs.get("id", ""), "region": self._region(), "h2_idx": len(self.h2), "html": (self.get_starttag_text() or "")[:300],
                   "text": []}
            if tag == "input":
                rec["text"] = [attrs.get("value", "")]
                self.recs.append(rec)
            elif tag in VOID:
                self.recs.append(rec)
            else:
                self.open.append((len(self.stack), rec))
        if tag == "img":
            for _, rec in self.open:
                rec["alt"] = rec["alt"] or sp(attrs.get("alt"))
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                depth = i
                del self.stack[i:]
                keep = []
                for d, rec in self.open:
                    if d >= depth:
                        rec["text"] = sp(" ".join(rec["text"]))
                        self.recs.append(rec)
                    else:
                        keep.append((d, rec))
                self.open = keep
                if tag == "h2" and self.h2_open is not None:
                    self.h2.append((sp(" ".join(self.h2_open["text"])), self.h2_open["region"]))
                    self.h2_open = None
                return

    def handle_data(self, data):
        for _, rec in self.open:
            rec["text"].append(data)
        if self.h2_open is not None:
            self.h2_open["text"].append(data)

    def close(self):
        super().close()
        for _, rec in self.open:
            rec["text"] = sp(" ".join(rec["text"]))
            self.recs.append(rec)
        self.open = []


def current_code(r):
    f = r["form"]
    if f in FORM_CODE:
        return FORM_CODE[f]
    if f == "a_nohref":
        return "UI" if not (r["text"] or r["aria"] or r["alt"]) else "lai"
    if f == "a_hash":
        return "lai" if r["aria_expanded"] else "lỗi"
    return "UI"


def read_html(path):
    raw = open(path, "rb").read()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def canonical_host(doc):
    m = re.search(r"<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']https?://([^/\"']+)", doc, re.I) or \
        re.search(r"<link\b[^>]*href=[\"']https?://([^/\"']+)[^>]*rel=[\"']canonical[\"']", doc, re.I)
    if not m:
        return None
    h = m.group(1).lower()
    return h[4:] if h.startswith("www.") else h


def scan_file(path, rel, hosts, regions, sc_re, sc_last):
    doc = read_html(path)
    hosts2 = set(hosts)
    ch = canonical_host(doc)
    if ch:
        hosts2.add(ch)
    p = Page(regions, hosts2)
    p.feed(doc)
    p.close()
    page_path = path_of(p.canonical, hosts2) if p.canonical else None
    if page_path is None:
        page_path = "/" + re.sub(r"\.html?(\.gz)?$", "", rel).replace(os.sep, "/").strip("/")
    body_h2 = [t for t, reg in p.h2 if reg == "body"]
    n = len(body_h2)
    page_noindex = bool(p.robots and re.search(r"noindex", p.robots, re.I))
    for r in p.recs:
        r["page"] = page_path
        r["code"] = current_code(r)
        r["zone"] = ""
        r["h2"] = ""
        if r["region"] == "body":
            i = sum(1 for t, reg in p.h2[:r["h2_idx"]] if reg == "body")
            if i == 0:
                r["zone"] = "MC"
            else:
                title = body_h2[i - 1]
                r["h2"] = title[:160]
                r["zone"] = "SC" if (sc_re.search(title) or i > n - sc_last) else "MC"
        r.pop("h2_idx", None)
    return page_path, p.recs, page_noindex


def read_paths(path):
    txt = open(path, encoding="utf-8").read()
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)
    items = locs if locs else [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith("#")]
    return items


def add_flags(recs, hosts, noindex, sitemap):
    real = collections.defaultdict(int)
    for r in recs:
        if r["code"] == "D1" and r["tkind"] == "internal":
            real[r["target"]] += 1
    for r in recs:
        fl = r["flags"] = []
        if r["code"] == "lai":
            fl.append("lai")
        if r["form"] in ("span_loc", "span_open", "span_scroll") \
                and not (r["role"] in ("link", "button") and r["tabindex"] != ""):
            fl.append("thieu_ban_phim")
        if r["form"] in ("button_open", "span_open") and "noopener" not in r["onclick"]:
            fl.append("thieu_noopener")
        if r["tag"] == "a" and r["target_attr"] == "_blank" and not re.search(r"noopener|noreferrer", r["rel"] or "", re.I):
            fl.append("thieu_noopener")
        if r["code"] == "D1" and r["tkind"] == "internal" and r["target"] in noindex:
            fl.append("link_that_toi_noindex")
        if r["code"] in ("D3", "D4") and r["tkind"] == "internal":
            if not real.get(r["target"]):
                fl.append("doch_chi_co_link_js")
            if sitemap is not None and r["target"] not in sitemap:
                fl.append("doch_khong_trong_sitemap")
    return recs


def page_counts(recs):
    out = {}
    for r in recs:
        c = out.setdefault(r["page"], {}).setdefault(r["region"], {"real": 0, "js": 0})
        if r["code"] == "D1" and r["tkind"] in ("internal", "external"):
            c["real"] += 1
        elif r["code"] in ("D3", "D4", "D5"):
            c["js"] += 1
    return out


def files_of(inputs):
    out = []
    for i in inputs:
        if os.path.isdir(i):
            for root, _, fs in os.walk(i):
                for f in sorted(fs):
                    if re.search(r"\.html?(\.gz)?$", f, re.I):
                        full = os.path.join(root, f)
                        out.append((full, os.path.relpath(full, i)))
        elif os.path.isfile(i):
            out.append((i, os.path.basename(i)))
        else:
            raise Err("không thấy đường dẫn %s" % i)
    if not out:
        raise Err("không có file .html hoặc .html.gz")
    return sorted(out)


def cmd_scan(a):
    hosts = set((h.lower()[4:] if h.lower().startswith("www.") else h.lower()) for h in a.host)
    regions = []
    for r in a.region:
        if "=" not in r:
            raise Err("--region cần dạng tên=REGEX", 2)
        regions.append(tuple(r.split("=", 1)))
    sc_re = re.compile(a.sc_h2, re.I)
    noindex = set(path_of(x, hosts) or x for x in read_paths(a.noindex)) if a.noindex else set()
    sitemap = set(path_of(x, hosts) or x for x in read_paths(a.sitemap)) if a.sitemap else None
    recs, pages = [], []
    for full, rel in files_of(a.inputs):
        try:
            pp, rs, ni = scan_file(full, rel, hosts, regions, sc_re, a.sc_last)
        except (OSError, EOFError, ValueError) as e:
            raise Err("không đọc được %s: %s" % (full, e))
        pages.append(pp)
        recs += rs
        if ni:
            noindex.add(pp)
    add_flags(recs, hosts, noindex, sitemap)
    table = collections.defaultdict(lambda: collections.Counter())
    for r in recs:
        table[r["region"] + (" " + r["zone"] if r["zone"] else "")][r["code"]] += 1
    flags = collections.Counter(f for r in recs for f in r["flags"])
    groups = collections.OrderedDict()
    for r in recs:
        if r["region"] != "body":
            key = (r["region"], r["code"], r["target"], r["text"] or r["aria"] or r["alt"])
            g = groups.setdefault(key, {"region": r["region"], "code": r["code"], "target": r["target"],
                                        "anchor": key[3], "pages": set(), "flags": set()})
            g["pages"].add(r["page"])
            g["flags"].update(r["flags"])
    summary = {"so_trang": len(pages), "so_phan_tu": len(recs), "bang": {k: dict(v) for k, v in sorted(table.items())},
               "co": dict(flags), "trang": page_counts(recs), "gioi_han": [
                   "Dạng hiện tại, chưa phải đề xuất D1-D6: cần Jev link-purpose và Claude đọc (link-js.md §6).",
                   "Cờ doch_chi_co_link_js chỉ đáng tin khi tập quét phủ đủ trang mẹ của đích." if len(pages) < 20 else
                   "Cờ doch_chi_co_link_js tính trên %d trang quét." % len(pages)]}
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "inventory.jsonl"), "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(os.path.join(a.out, "templates.tsv"), "w", encoding="utf-8") as f:
            f.write("region\tcode\ttarget\tanchor\tso_trang\tco\n")
            for g in groups.values():
                f.write("\t".join([g["region"], g["code"], g["target"], g["anchor"].replace("\t", " "), str(len(g["pages"])),
                                   ",".join(sorted(g["flags"]))]) + "\n")
        with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    if a.json:
        print(json.dumps(summary, ensure_ascii=False, indent=1))
    else:
        print("Quét %d trang, %d phần tử bấm được." % (len(pages), len(recs)))
        codes = ["D1", "D2", "D3", "D4", "D5", "lai", "lỗi", "UI"]
        print("%-16s" % "vùng" + "".join("%6s" % c for c in codes))
        for k, v in sorted(table.items()):
            print("%-16s" % k + "".join("%6d" % v.get(c, 0) for c in codes))
        print("Cờ: " + (", ".join("%s=%d" % kv for kv in sorted(flags.items())) if flags else "không có"))
        print("Template lặp ngoài body: %d nhóm (gộp theo vùng, dạng, đích, anchor)." % len(groups))
        for g in summary["gioi_han"]:
            print("Giới hạn: " + g)
        if a.out:
            print("Đã ghi %s/{inventory.jsonl,templates.tsv,summary.json}" % a.out)
        else:
            print("Chưa ghi file (thêm --out DIR để lưu).")
    return 3 if (a.fail_on_flags and flags) else 0


def cmd_compare(a):
    try:
        old = json.load(open(a.before, encoding="utf-8"))["trang"]
        new = json.load(open(a.after, encoding="utf-8"))["trang"]
    except (OSError, ValueError, KeyError) as e:
        raise Err("không đọc được summary.json: %s" % e)
    tot = collections.defaultdict(lambda: [0, 0])
    drops, rows = [], []
    for pg in sorted(set(old) | set(new)):
        for reg in sorted(set(old.get(pg, {})) | set(new.get(pg, {}))):
            b = old.get(pg, {}).get(reg, {}).get("real", 0)
            n = new.get(pg, {}).get(reg, {}).get("real", 0)
            tot[reg][0] += b
            tot[reg][1] += n
            if b != n:
                rows.append((pg, reg, b, n))
                if reg == "body" and n < b and pg in old and pg in new:
                    drops.append((pg, b, n))
    if a.json:
        print(json.dumps({"tong": {k: v for k, v in tot.items()}, "doi": rows, "body_giam": drops}, ensure_ascii=False, indent=1))
    else:
        print("Link thật (D1) theo vùng: trước → sau")
        for reg, (b, n) in sorted(tot.items()):
            print("  %-12s %5d → %5d (%+d)" % (reg, b, n, n - b))
        print("Trang có đổi: %d" % len(rows))
        for pg, b, n in drops:
            print("BODY GIẢM %s: %d → %d (luật 1: không đổi link D1 trong thân bài sang link JS)" % (pg, b, n))
        if not drops:
            print("Link thật ở body không giảm.")
    return 3 if (drops and not a.allow_body_drop) else 0


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="kiểm kê phần tử bấm được", description="Quét HTML đã lưu. Chỉ đọc; --out DIR mới ghi file.")
    s.add_argument("inputs", nargs="+", help="file hoặc thư mục .html / .html.gz")
    s.add_argument("--host", action="append", default=[], help="host của site (lặp được), vd vidu.vn. Host trong canonical tự thêm")
    s.add_argument("--region", action="append", default=[], help='vùng riêng "tên=REGEX" khớp class hoặc id tổ tiên (lặp được)')
    s.add_argument("--noindex", help="file danh sách path noindex, mỗi dòng một path (trang có meta noindex tự thêm)")
    s.add_argument("--sitemap", help="file sitemap XML hoặc danh sách path, để kiểm đích link JS có trong sitemap")
    s.add_argument("--sc-last", type=int, default=2, help="số H2 cuối của body tính là SC (mặc định 2)")
    s.add_argument("--sc-h2", default=SC_DEFAULT, help="regex tên H2 thuộc SC")
    s.add_argument("--out", help="thư mục ghi inventory.jsonl, templates.tsv, summary.json")
    s.add_argument("--json", action="store_true")
    s.add_argument("--fail-on-flags", action="store_true", help="thoát 3 nếu có cờ")
    c = sub.add_parser("compare", help="so link thật trước và sau", description="So 2 summary.json. Thoát 3 nếu link thật ở body giảm.")
    c.add_argument("before")
    c.add_argument("after")
    c.add_argument("--allow-body-drop", action="store_true", help="chấp nhận body giảm (đã duyệt)")
    c.add_argument("--json", action="store_true")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return cmd_scan(a) if a.cmd == "scan" else cmd_compare(a)
    except Err as e:
        print("LỖI: %s" % e, file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
