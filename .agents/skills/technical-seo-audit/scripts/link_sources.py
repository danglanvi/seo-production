#!/usr/bin/env python3
"""Tìm nguồn của link hỏng hoặc link qua redirect (technical-seo-audit, khu vực 1 và 3).

Lệnh:
  summarize --inlinks "<redirection_(3xx)_inlinks.csv>" [--inlinks "<client_error_(4xx)_inlinks.csv>"]
            --site <tên miền> --out-dir <thư mục>
      Đọc bulk export inlinks của Screaming Frog. Đếm inlink theo đích, tách nội bộ, link ngoài,
      nút chia sẻ hoặc widget chat. Ghi targets.tsv và patterns.txt (chuỗi để tìm trong DB).
  sources --json <output find_sources.php> --out sources.tsv
      Đọc output của find_sources.php (bỏ dòng cảnh báo PHP lẫn ở đầu), bỏ revision, autosave và bản nháp,
      ghi nguồn còn sống: bài, trang, menu, footer Elementor, term, option.

Python stdlib. Chỉ đọc file.
"""
import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SHARE_HOSTS = ("zalo.me", "messenger.com", "m.me", "facebook.com/sharer", "twitter.com/intent", "x.com/intent",
               "linkedin.com/share", "pinterest.com/pin", "t.me/share", "wa.me", "api.whatsapp.com")
LIVE_STATUS = {"publish", "private", "future"}
NOISE_OPTIONS = {"rank_math_backups", "rewrite_rules", "_transient", "_site_transient"}
ELEMENTOR_KEYS = {"_elementor_data", "_elementor_page_settings"}
CACHE_KEYS = {"_elementor_element_cache", "_elementor_css"}


def host_of(url):
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def classify(dest, site):
    h = host_of(dest)
    if h == site or h.endswith("." + site):
        return "nội bộ"
    low = dest.lower()
    if any(s in low for s in SHARE_HOSTS):
        return "chia sẻ/widget"
    return "ngoài"


def pattern_for(dest, site):
    """Chuỗi tìm trong DB. Link nội bộ: đường dẫn giữ dấu / hai đầu, để không khớp tên file ảnh
    (bài 18/10: "silo-la-gi" khớp cả "cau-truc-silo-la-gi.png"). Link ngoài: host + đường dẫn, bỏ scheme."""
    p = urlsplit(dest)
    path = p.path or "/"
    if classify(dest, site) == "nội bộ":
        return path if path not in ("", "/") else None
    return ((p.hostname or "") + path.rstrip("/")).removeprefix("www.")


def cmd_summarize(a):
    site = a.site.lower().removeprefix("www.")
    by = {}
    for f in a.inlinks:
        with open(f, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                d = r.get("Destination", "")
                if not d:
                    continue
                t = by.setdefault(d, {"status": r.get("Status Code", ""), "n": 0, "sources": set(),
                                      "pos": collections.Counter(), "types": collections.Counter()})
                t["n"] += 1
                t["sources"].add(r.get("Source", ""))
                t["pos"][r.get("Link Position") or "?"] += 1
                t["types"][r.get("Type") or "?"] += 1
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tot = collections.Counter()
    pats = set()
    rows = sorted(by.items(), key=lambda kv: -kv[1]["n"])
    with open(out / "targets.tsv", "w", encoding="utf-8") as fh:
        fh.write("destination\tstatus\tclass\tinlinks\tsource_pages\tpositions\ttypes\tpattern\tsample_source\n")
        for d, t in rows:
            c = classify(d, site)
            tot[c] += t["n"]
            pat = pattern_for(d, site) if c != "chia sẻ/widget" else ""
            if pat:
                pats.add(pat)
            fh.write("\t".join([d, t["status"], c, str(t["n"]), str(len(t["sources"])),
                                ", ".join(f"{k} {v}" for k, v in t["pos"].most_common()),
                                ", ".join(f"{k} {v}" for k, v in t["types"].most_common()),
                                pat or "", sorted(t["sources"])[0] if t["sources"] else ""]) + "\n")
    (out / "patterns.txt").write_text("|".join(sorted(pats)) + "\n", encoding="utf-8")
    hosts = collections.Counter()
    for d, t in rows:
        hosts[host_of(d)] += t["n"]
    summary = {"inlinks": sum(tot.values()), "by_class": dict(tot), "targets": len(rows), "by_host": dict(hosts.most_common())}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


def load_find_sources(path):
    """Output WP-CLI lẫn dòng PHP Warning/Notice ở đầu: cắt tới dấu { đầu tiên rồi mới parse."""
    t = Path(path).read_text(encoding="utf-8", errors="ignore")
    i = t.find("{")
    if i < 0:
        sys.exit("không thấy JSON trong output find_sources.php")
    warn = [l for l in t[:i].splitlines() if l.strip()]
    data, _ = json.JSONDecoder().raw_decode(t[i:])
    return data, warn


def live_rows(data):
    """Dòng nguồn còn sống. Bỏ revision, autosave, nháp, option sao lưu; ghi riêng cache Elementor."""
    out = []
    for pat, hits in data.items():
        if not isinstance(hits, dict):  # PHP mã hoá mảng rỗng thành []
            continue
        for row in hits.get("post", []):
            pid, ptype, status, slug, n = (row + [None] * 5)[:5]
            if ptype == "revision" or status not in LIVE_STATUS:
                continue
            kind = "Elementor template" if ptype == "elementor_library" else "post_content"
            out.append({"pattern": pat, "where": kind, "id": str(pid), "type": ptype, "status": status,
                        "slug": slug or "", "key": "post_content", "count": n})
        for row in hits.get("meta", []):
            pid, key, ptype, status, slug, n, n_esc = (row + [None] * 7)[:7]
            if ptype == "revision" or status not in LIVE_STATUS:
                continue
            if key in CACHE_KEYS:
                where = "cache Elementor (sinh lại, không sửa)"
            elif key in ELEMENTOR_KEYS:
                where = "Elementor _elementor_data"
            elif key == "_menu_item_url":
                where = "menu"
            elif key.startswith("_wp_attach") or key == "_wp_old_slug":
                where = "tên file hoặc slug cũ (không phải link)"
            elif "schema" in key.lower():
                where = f"JSON-LD {key} (không phải thẻ a)"
            else:
                where = f"postmeta {key}"
            out.append({"pattern": pat, "where": where, "id": str(pid), "type": ptype or "", "status": status or "",
                        "slug": slug or "", "key": key, "count": (n or 0) + (n_esc or 0)})
        for row in hits.get("opt", []):
            name, n = (row + [None] * 2)[:2]
            if any(name.startswith(x) for x in NOISE_OPTIONS):
                continue
            out.append({"pattern": pat, "where": "option", "id": name, "type": "", "status": "", "slug": "",
                        "key": name, "count": n})
        for row in hits.get("term", []):
            out.append({"pattern": pat, "where": "mô tả term", "id": str(row[0]), "type": row[1], "status": "",
                        "slug": "", "key": "description", "count": 1})
        for row in hits.get("usermeta", []):
            out.append({"pattern": pat, "where": "usermeta (hồ sơ tác giả)", "id": str(row[0]), "type": "", "status": "",
                        "slug": "", "key": row[1], "count": 1})
        for row in hits.get("termmeta", []):
            out.append({"pattern": pat, "where": "termmeta", "id": str(row[0]), "type": "", "status": "", "slug": "",
                        "key": row[1], "count": 1})
    return out


def cmd_sources(a):
    data, warn = load_find_sources(a.json)
    rows = live_rows(data)
    with open(a.out, "w", encoding="utf-8") as fh:
        cols = ["pattern", "where", "id", "type", "status", "slug", "key", "count"]
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    pats = collections.Counter(r["pattern"] for r in rows)
    empty = [p for p, h in data.items() if not isinstance(h, dict) or not any(h.values())]
    print(f"{len(rows)} nguồn còn sống, {len(pats)} chuỗi có nguồn, {len(empty)} chuỗi không thấy trong DB, "
          f"{len(warn)} dòng cảnh báo PHP đã bỏ -> {a.out}", file=sys.stderr)
    if empty:
        print("không thấy trong DB (tìm tiếp trong file theme, mu-plugin bằng rg): " + ", ".join(empty), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summarize")
    s.add_argument("--inlinks", action="append", required=True)
    s.add_argument("--site", required=True)
    s.add_argument("--out-dir", required=True)
    o = sub.add_parser("sources")
    o.add_argument("--json", required=True)
    o.add_argument("--out", required=True)
    a = ap.parse_args()
    {"summarize": cmd_summarize, "sources": cmd_sources}[a.cmd](a)


if __name__ == "__main__":
    main()
