#!/usr/bin/env python3
"""Nhánh backlink của link-relevance: chấm T.T.T (Theme 35, Traffic 35, Trust 30) cho backlink lấy từ Ahrefs.

  prepare  --ahrefs <file.json> [...] --store <store site đích> --own-domains a.com,b.com --out-dir <W> [--registry <json> --site <domain>]
           Đọc kết quả Ahrefs site-explorer-all-backlinks (dạng {"backlinks": [...]}, list, hoặc file MCP đã lưu).
           Code gắn cờ, xếp loại nguồn; EmbeddingGemma đo Theme: "title | anchor: đoạn quanh link", đã bỏ URL và tên miền (SearchQuery)
           so với trang đích trong store (Document). Ghi bl_links.jsonl, summary.json.
  sample   --links <W>/bl_links.jsonl --n 60 --out-dir <W>/calibration   phiếu gold không có điểm model.
  validate --links ... --gold gold.jsonl --out-dir <W>/calibration          AUC của cos, ngưỡng, score_pairs.jsonl.
  report   --links ... --out <W>/report.md                                  bảng loại nguồn, T.T.T, đích lỗi.

Traffic và Trust là thang quy đổi theo GTV từ số Ahrefs, chưa hiệu chuẩn với thứ hạng thật. Chỉ Theme có gold.
"""
import argparse
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PLATFORMS = {"google.com", "blogspot.com", "wordpress.com", "medium.com", "webflow.io", "tumblr.com", "wixsite.com",
             "weebly.com", "notion.site", "github.io", "gitbook.io", "behance.net", "linkedin.com", "facebook.com",
             "youtube.com", "pinterest.com", "x.com", "twitter.com", "substack.com", "tistory.com", "naver.com",
             "goo.gl", "bit.ly", "about.me", "issuu.com", "scribd.com", "slideshare.net", "dribbble.com", "reddit.com"}
TYPE = {"Article": "bai_viet", "Listing": "danh_sach", "Listing_Collection": "danh_sach", "User_Generated_Content": "ugc_forum",
        "Core_Page": "trang_chinh", "Landing_Page": "landing", "Video": "video", "Profile": "ho_so"}
# gtvseo.com 19/10/2026, 120 link gold qua 3 tập: lo, hi là dải chấm điểm; pass 0.64 = Theme đạt (precision 0.87, recall 0.99).
# Registry rubric backlink-theme thay theo site.
DEFAULT_THEME = {"lo": 0.62, "hi": 0.78, "pass": 0.64}
# Tín hiệu máy theo skills/backlink-research/references/spam-filter-criteria.md: REJECT khi có từ 2 tín hiệu, 1 tín hiệu là REVIEW.
# M1 Ahrefs is_spam · M2 tên miền nguồn không có organic traffic · M3 trên 100 link ra, hoặc danh mục/anchor cờ bạc, người lớn, black hat.
FARM_OUTLINKS = 100
BAD_CAT = re.compile(r"Gambling|Adult|Pornograph", re.I)
BAD_ANCHOR = re.compile(r"\b(casino|bet|ultrabet|giriş|slot|porn|sex|viagra|black hat|pbn|buy backlinks)\b", re.I)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def nu(u):
    u = re.sub(r"^https?://(www\.)?", "", (u or "").strip()).split("#")[0].split("?")[0]  # bỏ ?fbclid, ?utm
    return u.rstrip("/")


def load_ahrefs(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, list) and d and isinstance(d[0], dict) and "type" in d[0] and "text" in d[0]:
        d = json.loads(d[0]["text"])  # file MCP đã lưu: [{type, text}, ...]
    return d["backlinks"] if isinstance(d, dict) else d


URLISH = re.compile(r"https?://\S+|\b[\w.-]+\.(?:com|vn|io|net|org|info|co|asia|xyz)\b\S*", re.I)


def theme_text(x):
    """Chữ đem đo Theme: title + anchor + đoạn quanh link, bỏ URL và tên miền.
    URL đích trong anchor trần chứa slug của trang đích, không phải bằng chứng Theme của trang nguồn."""
    anc = URLISH.sub(" ", x["anchor"]).strip() or "link"
    ctx = re.sub(r"\s+", " ", URLISH.sub(" ", x["ctx"])).strip()
    return f"{x['title']} | {anc}: {ctx}"


def theme_gate(registry, site):
    if registry and Path(registry).exists():
        reg = json.loads(Path(registry).read_text(encoding="utf-8"))
        for e in reg.get("entries", []):
            if e.get("rubric") == "backlink-theme" and e.get("site") in (site, "*") and e.get("lo") is not None:
                return {"lo": e["lo"], "hi": e["hi"], "pass": e.get("pass", e["lo"]), "source": "registry"}
    return dict(DEFAULT_THEME, source="defaults")


def pts_theme(cos, g):
    return round(35 * min(1.0, max(0.0, (cos - g["lo"]) / (g["hi"] - g["lo"]))), 1)


def pts_traffic(b):
    t = math.log10(1 + max(0, b.get("traffic") or 0)) / 3  # đủ 35 khi trang nguồn có 1.000 lượt tìm/tháng
    p = 0.5 * min(1.0, math.log10(1 + max(0, b.get("positions") or 0)) / 2)  # có từ khoá, chưa có traffic: tối đa nửa thang (từ 100 từ khoá)
    return round(35 * min(1.0, max(t, p)), 1)


def pts_trust(b, platform, follow, reject=False):
    if reject:  # chỉ REJECT (từ 2 tín hiệu máy) về 0; một tín hiệu như is_spam là REVIEW
        return 0.0
    ext = b.get("links_external") or 0
    outlink = 1.0 if ext <= 50 else max(0.3, 50 / ext)
    strength = 15 * min(1.0, (b.get("url_rating_source") or 0) / 30) * outlink * (1.0 if follow else 0.5)
    if b.get("tld_class_source") in ("gov", "edu"):
        rank = 15.0
    else:
        rank = 15 * min(1.0, (b.get("domain_rating_source") or 0) / 90) * (0.4 if platform else 1.0)
    return round(strength + rank, 1)


def cmd_prepare(a):
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
    sys.dont_write_bytecode = True
    import svi  # noqa: E402  (cùng bộ skill)

    own = {d.strip().lower() for d in a.own_domains.split(",") if d.strip()}
    st = svi.Store(a.store)
    pidx = [i for i, it in enumerate(st.items) if it["level"] == "page"]
    purl = [nu(st.items[i]["url"]) for i in pidx]
    pos = {u: k for k, u in enumerate(purl)}
    P = st.vec[pidx].astype(np.float32)
    titles = {}
    for i in pidx:
        m = st.items[i].get("meta") or {}
        if isinstance(m, str):
            m = {}
        titles[nu(st.items[i]["url"])] = m.get("title", "")

    rows, seen = [], set()
    for f in a.ahrefs:
        for b in load_ahrefs(f):
            key = (b.get("url_from"), b.get("url_to"), b.get("anchor"))
            if key not in seen:
                seen.add(key)
                rows.append(b)

    g = theme_gate(a.registry, a.site)
    links = []
    for k, b in enumerate(rows):
        root = (b.get("root_name_source") or "").lower()
        follow = bool(b.get("is_dofollow")) and not b.get("is_ugc") and not b.get("is_sponsored")
        platform = root in PLATFORMS
        tgt = nu(b.get("url_to"))
        flags = []
        if b.get("is_spam"):
            flags.append("spam")
        if b.get("traffic_domain") == 0:
            flags.append("zero_organic")
        if (b.get("links_external") or 0) > FARM_OUTLINKS:
            flags.append("obl_farm")
        if BAD_CAT.search(b.get("page_category_source") or "") or BAD_ANCHOR.search(b.get("anchor") or ""):
            flags.append("spam_topic")
        machine = sorted({"M1" for f in flags if f == "spam"} | {"M2" for f in flags if f == "zero_organic"}
                         | {"M3" for f in flags if f in ("obl_farm", "spam_topic")})
        verdict = "REJECT" if len(machine) >= 2 else "REVIEW" if machine else "KEEP"
        if root in own:
            flags.append("own_network")
        if platform:
            flags.append("platform")
        if not follow:
            flags.append("nofollow")
        if not b.get("is_content"):
            flags.append("not_content")
        if b.get("is_image"):
            flags.append("image")
        if tgt not in pos:
            flags.append("target_missing")
        langs = [x.split("-")[0] for x in (b.get("languages") or [])]
        if langs and not ({"vi", "en"} & set(langs)):
            flags.append("lang_other")
        anc = (b.get("anchor") or "").strip()
        ctx = " ".join(x for x in [(b.get("snippet_left") or "").strip(), anc, (b.get("snippet_right") or "").strip()] if x)
        if not anc and not ctx:
            flags.append("empty_context")
        ptype = (b.get("page_type_source") or "").split(",")[0].strip("/").split("/")[0]
        stype = "nen_tang" if platform else TYPE.get(ptype, "khac")
        links.append({"id": f"b{k:04d}", "src": b.get("url_from"), "root": root, "target": tgt, "anchor": anc,
                      "title": b.get("title") or "", "ctx": ctx[:600], "source_type": stype,
                      "page_type": b.get("page_type_source") or "", "category": (b.get("page_category_source") or "")[:300],
                      "dr": b.get("domain_rating_source"), "ur": b.get("url_rating_source"), "traffic": b.get("traffic"),
                      "positions": b.get("positions"), "links_external": b.get("links_external"), "follow": follow,
                      "first_seen": (b.get("first_seen_link") or "")[:10], "flags": flags, "machine": machine, "verdict": verdict,
                      "traffic_pts": pts_traffic(b),
                      "trust_pts": pts_trust(b, platform, follow, verdict == "REJECT")})

    texts = [theme_text(x) for x in links]
    Q = svi.encoder(a.max_tokens).encode(texts, "SearchQuery") if texts else np.zeros((0, P.shape[1]), dtype=np.float32)
    for j, x in enumerate(links):
        c = P @ Q[j]
        best = int(np.argmax(c))
        if x["target"] in pos:
            ct = float(c[pos[x["target"]]])
            x["gemma"] = {"cos": round(ct, 4), "rank": int((c > ct).sum()) + 1, "best": purl[best], "best_cos": round(float(c[best]), 4)}
        else:
            ct = float(c[best])  # đích không còn trong store: đo với trang gần nhất của site
            x["gemma"] = {"cos": round(ct, 4), "rank": None, "best": purl[best], "best_cos": round(ct, 4)}
        x["theme_pts"] = pts_theme(ct, g)
        x["theme_ok"] = ct >= g["pass"]
        x["ttt"] = round(x["theme_pts"] + x["traffic_pts"] + x["trust_pts"], 1)
        x["target_title"] = titles.get(x["target"], "")

    out = Path(a.out_dir)
    write(out / "bl_links.jsonl", links)
    summ = {"model": svi.MODEL, "n": len(links), "theme_gate": g, "flags": dict(Counter(f for x in links for f in x["flags"])),
            "source_type": dict(Counter(x["source_type"] for x in links)),
            "ttt_median": sorted(x["ttt"] for x in links)[len(links) // 2] if links else None}
    (out / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False))


def cmd_sample(a):
    skip = {x.strip() for x in Path(a.exclude).read_text(encoding="utf-8").split()} if a.exclude else set()
    links = [x for x in jl(a.links) if "spam" not in x["flags"] and "target_missing" not in x["flags"] and (x["ctx"] or x["title"])
             and x["src"] not in skip]
    links.sort(key=lambda x: x["gemma"]["cos"])
    rnd = random.Random(a.seed)
    bands = [links[i * len(links) // 4:(i + 1) * len(links) // 4] for i in range(4)]
    pick = []
    for b in bands:
        pick += rnd.sample(b, min(len(b), a.n // 4))
    rnd.shuffle(pick)
    out = Path(a.out_dir)
    lines = []
    for x in pick:
        lines += [f"## {x['id']}", f"Nguồn: {x['src']}", f"Title nguồn: {x['title']}", f"Anchor: {x['anchor']}",
                  f"Đoạn: {x['ctx']}", f"Đích: {x['target']} | {x['target_title']}", "Theme (yes/no):", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "gold_todo.txt").write_text("\n".join(lines), encoding="utf-8")
    write(out / "gold_ids.jsonl", [{"id": x["id"]} for x in pick])
    print(f"{len(pick)} link -> {out / 'gold_todo.txt'}")


def auc(pos, neg):
    if not pos or not neg:
        return None
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg))


def cmd_validate(a):
    links = {x["id"]: x for x in jl(a.links)}
    gold = [g for g in jl(a.gold) if g["id"] in links]
    pairs = [{"id": g["id"], "score": links[g["id"]]["gemma"]["cos"], "label": 1 if g["theme"] == "yes" else 0} for g in gold]
    pos = [p["score"] for p in pairs if p["label"]]
    neg = [p["score"] for p in pairs if not p["label"]]
    best = max(((t, sum((p["score"] >= t) == bool(p["label"]) for p in pairs)) for t in sorted({p["score"] for p in pairs})),
               key=lambda z: z[1], default=(None, 0))
    res = {"n": len(pairs), "yes": len(pos), "no": len(neg), "auc_cos": round(auc(pos, neg), 3) if auc(pos, neg) is not None else None,
           "best_threshold": best[0], "accuracy_at_best": round(best[1] / len(pairs), 3) if pairs else None}
    out = Path(a.out_dir)
    write(out / "score_pairs.jsonl", pairs)
    (out / "validate.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))


def cmd_report(a):
    links = jl(a.links)
    n = len(links)
    by = defaultdict(list)
    for x in links:
        by[x["source_type"]].append(x)
    clean = [x for x in links if x["verdict"] != "REJECT" and "lang_other" not in x["flags"]]
    lines = [f"# Backlink T.T.T: {n} link", "", "Thang Theme 35 · Traffic 35 · Trust 30. Traffic và Trust quy đổi theo GTV từ số Ahrefs.", "",
             "| Loại nguồn | Số link | T.T.T trung vị | Theme trung vị | Dofollow |", "|---|---|---|---|---|"]
    for t, xs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        med = sorted(x["ttt"] for x in xs)[len(xs) // 2]
        th = sorted(x["theme_pts"] for x in xs)[len(xs) // 2]
        lines.append(f"| {t} | {len(xs)} | {med} | {th} | {sum(x['follow'] for x in xs)} |")
    ok = sum(x.get("theme_ok", False) for x in clean)
    vc = Counter(x["verdict"] for x in links)
    lines += ["", f"Verdict tín hiệu máy: KEEP {vc['KEEP']} · REVIEW {vc['REVIEW']} · REJECT {vc['REJECT']} (REJECT = từ 2 tín hiệu M1–M3).",
              "", f"Theme đạt (cos từ ngưỡng pass): {ok}/{len(clean)} link (bỏ REJECT và link khác tiếng Việt, tiếng Anh)."]
    fl = Counter(f for x in links for f in x["flags"])
    lines += ["", "## Cờ", ""] + [f"- {k}: {v}" for k, v in fl.most_common()]
    lines += ["", "## 15 link T.T.T cao nhất (không REJECT)", "", "| T.T.T | Theme | Traffic | Trust | Nguồn | Anchor | Đích |", "|---|---|---|---|---|---|---|"]
    for x in sorted(clean, key=lambda x: -x["ttt"])[:15]:
        lines.append(f"| {x['ttt']} | {x['theme_pts']} | {x['traffic_pts']} | {x['trust_pts']} | {x['src'][:70]} | {x['anchor'][:40]} | /{x['target'].split('/', 1)[-1] if '/' in x['target'] else ''} |")
    miss = Counter(x["target"] for x in links if "target_missing" in x["flags"] and x["verdict"] != "REJECT")
    lines += ["", "## Đích không còn trong store (kiểm 301 hoặc 410)", ""] + ([f"- {u}: {c} link" for u, c in miss.most_common()] or ["- không có"])
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{n} link -> {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--ahrefs", nargs="+", required=True)
    p.add_argument("--store", required=True)
    p.add_argument("--own-domains", default="")
    p.add_argument("--registry")
    p.add_argument("--site", default="")
    p.add_argument("--max-tokens", type=int, default=256)
    p.add_argument("--out-dir", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--links", required=True)
    s.add_argument("--n", type=int, default=60)
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--exclude", help="file danh sách URL nguồn đã dùng ở tập dev")
    s.add_argument("--out-dir", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--links", required=True)
    v.add_argument("--gold", required=True)
    v.add_argument("--out-dir", required=True)
    r = sub.add_parser("report")
    r.add_argument("--links", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"prepare": cmd_prepare, "sample": cmd_sample, "validate": cmd_validate, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
