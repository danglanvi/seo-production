#!/usr/bin/env python3
"""Lọc URL báo theo slug, cộng số Ahrefs, phân bổ về trang đích cho chiến dịch textlink. Chỉ dùng thư viện chuẩn.

  filter    --urls <file>... --terms <terms.json> --out <candidates.csv>
            Mỗi dòng file là một URL, hoặc CSV có cột url / url_to / url_from. Không crawl: chỉ đọc slug.
            terms.json: {"targets": [{"url", "quota", "A": [...], "B": [...]}], "C": [...], "neg": [...]}
            Script tự sinh dạng không dấu và dạng-gạch-nối. Điểm: A = 3/term, B = 2/term, C = 1/term; có term negative → loại.
  enrich    --candidates <csv> --ahrefs <file>... --out <csv>
            Join theo URL với kết quả Ahrefs (top-pages, pages-by-backlinks, batch-analysis): traffic, refdomains.
  allocate  --candidates <csv> --terms <terms.json> [--cap-domain 0.33] --out <plan.csv>
            Tier A → đúng trang đích có term A khớp; tier B → trang đích có term B khớp; tier C → trang có "home": true.
            Trong cùng tier: URL có refdomains, rồi traffic, rồi điểm. Mỗi URL báo gánh 1 trang đích.
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def plain(s):
    s = unicodedata.normalize("NFD", (s or "").lower()).replace("đ", "d").replace("Đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def slug_forms(term):
    p = plain(term).strip()
    return {re.sub(r"[^a-z0-9]+", "-", p).strip("-")}


def tokens(url):
    u = re.sub(r"^https?://", "", url.strip()).split("?")[0].split("#")[0]
    dom, _, path = u.partition("/")
    path = re.sub(r"\.(html?|php|aspx?)$", "", path.lower())
    path = re.sub(r"-?\d{3,}", "", path)  # bỏ id số
    return dom.lower().removeprefix("www."), "-" + re.sub(r"[^a-z0-9]+", "-", plain(path)).strip("-") + "-"


def read_urls(paths):
    out = []
    for p in paths:
        txt = Path(p).read_text(encoding="utf-8-sig")
        if txt.lstrip().startswith(("[", "{")):
            d = json.loads(txt)
            if isinstance(d, list) and d and "text" in d[0]:
                d, _ = json.JSONDecoder().raw_decode(d[0]["text"][d[0]["text"].index("{"):])
            rows = next(v for v in d.values() if isinstance(v, list)) if isinstance(d, dict) else d
            out += [r.get("url") or r.get("url_to") or r.get("url_from") for r in rows]
        elif "," in txt.splitlines()[0]:
            for r in csv.DictReader(txt.splitlines()):
                out.append(r.get("url") or r.get("url_to") or r.get("url_from"))
        else:
            out += [l.strip() for l in txt.splitlines() if l.strip()]
    return [u for u in out if u]


def term_index(T):
    idx = []
    for i, t in enumerate(T["targets"]):
        for tier, w in (("A", 3), ("B", 2)):
            for term in t.get(tier, []):
                idx += [(f, tier, w, i, term) for f in slug_forms(term)]
    idx += [(f, "C", 1, None, term) for term in T.get("C", []) for f in slug_forms(term)]
    neg = [f for term in T.get("neg", []) for f in slug_forms(term)]
    return idx, neg


def cmd_filter(a):
    T = json.loads(Path(a.terms).read_text(encoding="utf-8"))
    idx, neg = term_index(T)
    short = sorted({term for _, tier, _, _, term in idx if tier in "AB" and len(term.split()) <= 2})
    if short:  # bỏ dấu làm trùng nghĩa: "khóa học" và "khoa học" cùng slug khoa-hoc
        print("Cảnh báo: term A/B ngắn (≤ 2 tiếng) dễ trùng nghĩa sau khi bỏ dấu, đọc matched_terms: " + ", ".join(short), file=sys.stderr)
    seen, rows, dropped = set(), [], Counter()
    for url in read_urls(a.urls):
        key = re.sub(r"^https?://(www\.)?", "", url).split("?")[0].rstrip("/")
        if key in seen:
            dropped["trùng"] += 1
            continue
        seen.add(key)
        dom, s = tokens(url)
        if any(f"-{n}-" in s for n in neg):
            dropped["negative"] += 1
            continue
        hits = [(tier, w, i, term) for f, tier, w, i, term in idx if f"-{f}-" in s]
        if not hits:
            dropped["không khớp"] += 1
            continue
        best = min(h[0] for h in hits)
        per_t = Counter(h[2] for h in hits if h[2] is not None and h[0] == best)
        rows.append({"url": url, "domain": dom, "tier": best, "score": sum(h[1] for h in hits),
                     "targets": "|".join(str(i) for i, _ in per_t.most_common()),  # target khớp nhiều term nhất đứng đầu
                     "matched_terms": "; ".join(sorted({h[3] for h in hits}))})
    rows.sort(key=lambda r: (r["tier"], -r["score"]))
    write_csv(a.out, rows, ["url", "domain", "tier", "score", "targets", "matched_terms"])
    print(json.dumps({"giữ": len(rows), "tier": dict(Counter(r["tier"] for r in rows)), "bỏ": dict(dropped)}, ensure_ascii=False))


def write_csv(path, rows, cols):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def nkey(u):
    return re.sub(r"^https?://(www\.)?", "", (u or "").strip()).split("?")[0].rstrip("/")


def cmd_enrich(a):
    stats = {}
    for p in a.ahrefs:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if isinstance(d, list) and d and "text" in d[0]:
            d, _ = json.JSONDecoder().raw_decode(d[0]["text"][d[0]["text"].index("{"):])
        rows = next(v for v in d.values() if isinstance(v, list)) if isinstance(d, dict) else d
        for r in rows:
            u = r.get("url") or r.get("url_to")
            stats[nkey(u)] = {"traffic": r.get("sum_traffic", r.get("org_traffic", r.get("traffic", 0))) or 0,
                              "refdomains": r.get("refdomains_target", r.get("referring_domains", r.get("refdomains", 0))) or 0}
    rows = list(csv.DictReader(open(a.candidates, encoding="utf-8")))
    hit = 0
    for r in rows:
        s = stats.get(nkey(r["url"]))
        hit += bool(s)
        r.update(s or {"traffic": "", "refdomains": ""})
    write_csv(a.out, rows, list(rows[0].keys()) if rows else ["url"])
    print(json.dumps({"dòng": len(rows), "có số Ahrefs": hit}, ensure_ascii=False))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def cmd_allocate(a):
    T = json.loads(Path(a.terms).read_text(encoding="utf-8"))
    tg = T["targets"]
    rows = list(csv.DictReader(open(a.candidates, encoding="utf-8")))
    rows.sort(key=lambda r: (r["tier"], -(num(r.get("refdomains")) > 0), -num(r.get("traffic")), -num(r["score"])))
    total = sum(t["quota"] for t in tg)
    cap = max(1, int(a.cap_domain * total))
    left = {i: t["quota"] for i, t in enumerate(tg)}
    per_dom, plan = Counter(), []
    home = [i for i, t in enumerate(tg) if t.get("home")]
    for r in rows:
        if per_dom[r["domain"]] >= cap:
            continue
        cands = [int(i) for i in r["targets"].split("|") if i] if r["tier"] in "AB" else home
        cands = [i for i in cands if left[i] > 0]
        if not cands:
            continue
        i = cands[0]  # filter đã xếp target khớp nhiều term nhất lên đầu
        left[i] -= 1
        per_dom[r["domain"]] += 1
        plan.append({"URL đi link": r["url"], "domain": r["domain"], "tier": r["tier"], "URL đích": tg[i]["url"],
                     "matched_terms": r["matched_terms"], "traffic": r.get("traffic", ""), "refdomains": r.get("refdomains", "")})
    write_csv(a.out, plan, ["URL đi link", "domain", "tier", "URL đích", "matched_terms", "traffic", "refdomains"])
    short = {tg[i]["url"]: q for i, q in left.items() if q > 0}
    print(json.dumps({"đã phân": len(plan), "cap mỗi domain": cap, "thiếu quota": short,
                      "domain": dict(per_dom.most_common(5))}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("filter")
    f.add_argument("--urls", nargs="+", required=True)
    f.add_argument("--terms", required=True)
    f.add_argument("--out", required=True)
    e = sub.add_parser("enrich")
    e.add_argument("--candidates", required=True)
    e.add_argument("--ahrefs", nargs="+", required=True)
    e.add_argument("--out", required=True)
    al = sub.add_parser("allocate")
    al.add_argument("--candidates", required=True)
    al.add_argument("--terms", required=True)
    al.add_argument("--cap-domain", type=float, default=0.33)
    al.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"filter": cmd_filter, "enrich": cmd_enrich, "allocate": cmd_allocate}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
