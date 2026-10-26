#!/usr/bin/env python3
"""Tính bảng cho research file của backlink-research từ dữ liệu Ahrefs đã lưu. Chỉ dùng thư viện chuẩn.

  gap       --mine <rd mình.json> --comp <rd đối thủ.json>... [--min 2] --out <gap.md>
            Tên miền trỏ ≥ min đối thủ nhưng không trỏ mình. Verdict theo references/spam-filter-criteria.md:
            M1 = Ahrefs is_spam, M2 = tên miền không có organic (traffic_domain 0 và positions_source_domain 0).
            Cả hai → REJECT, một → REVIEW, không có → KEEP. Theme chưa đo: Claude xét ở Tầng 2.
  anchors   --file <anchors_<domain>.json>... --mine <domain> --keywords "kw1,kw2" [--brand "domain=tên1|tên2"] --out <anchors.md>
            Phân nhóm anchor theo refdomains: spam, naked, brand, brand_kw, exact, partial, generic, chu_de, rong.
            Consensus = trung bình các đối thủ, bỏ nhóm spam.
  velocity  --file <rd_history.json> --out <velocity.md>
            RD ròng theo tháng (Ahrefs refdomains-history monthly). Đây là số ròng, không phải số RD mới.

File vào: dạng {"target", "refdomains"|"anchors"|"history"}, hoặc file MCP đã lưu [{type, text}].
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

PLATFORMS = {"google.com", "youtube.com", "goo.gl", "gravatar.com", "vimeo.com", "linktr.ee", "behance.net", "weebly.com",
             "issuu.com", "webflow.io", "gitbook.io", "deviantart.com", "about.me", "blogspot.com", "wordpress.com",
             "medium.com", "tumblr.com", "wixsite.com", "notion.site", "github.io", "linkedin.com", "facebook.com",
             "pinterest.com", "x.com", "twitter.com", "reddit.com", "substack.com", "teletype.in", "justpaste.it",
             "sites.google.com", "padlet.com", "wakelet.com", "mystrikingly.com", "hashnode.com", "anyflip.com"}
GENERIC = {"tại đây", "xem tại đây", "đây", "xem thêm", "tham khảo thêm", "click", "click here", "here", "website", "trang chủ",
           "visit website", "visit site", "link", "xem chi tiết", "chi tiết", "read more", "homepage", "home", "source", "nguồn"}
SPAM_ANCHOR = re.compile(r"telegram|whatsapp|\bpbn\b|backlinks?\b.*(buy|cheap|dofollow)|black ?hat|seoexpress|masslinker|"
                         r"\bda\b.*\bpa\b|dr/da/tf|link building|guest posts?|casino|\bbet\b|gái gọi", re.I)
NAKED = re.compile(r"^(https?://|www\.)|^[\w.-]+\.(com|vn|net|org|io|media|asia|info|co)(/\S*)?$", re.I)


def load(path, key):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, list) and d and isinstance(d[0], dict) and "text" in d[0]:
        txt = d[0]["text"]
        d, _ = json.JSONDecoder().raw_decode(txt[txt.index("{"):])
    return d.get("target"), d[key]


def norm(s):
    s = unicodedata.normalize("NFC", (s or "").strip().lower())
    return re.sub(r"\s+", " ", s)


def write_out(out, lines, data):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(out).with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {out}")


def cmd_gap(a):
    _, mine = load(a.mine, "refdomains")
    have = {x["domain"] for x in mine}
    by = defaultdict(list)
    for f in a.comp:
        tgt, rds = load(f, "refdomains")
        for x in rds:
            by[x["domain"]].append(dict(x, _comp=tgt))
    rows = []
    for dom, xs in by.items():
        comps = sorted({x["_comp"] for x in xs})
        if len(comps) < a.min or dom in have:
            continue
        x0 = max(xs, key=lambda x: x.get("domain_rating") or 0)
        m = []
        if any(x.get("is_spam") for x in xs):
            m.append("M1")
        if (x0.get("traffic_domain") or 0) == 0 and (x0.get("positions_source_domain") or 0) == 0:
            m.append("M2")
        verdict = "REJECT" if len(m) >= 2 else "REVIEW" if m else "KEEP"
        rows.append({"domain": dom, "dr": x0.get("domain_rating"), "comps": comps, "traffic_domain": x0.get("traffic_domain"),
                     "positions": x0.get("positions_source_domain"), "dofollow": any((x.get("dofollow_links") or 0) > 0 for x in xs),
                     "platform": dom in PLATFORMS, "machine": m, "verdict": verdict})
    order = {"KEEP": 0, "REVIEW": 1, "REJECT": 2}
    rows.sort(key=lambda r: (order[r["verdict"]], -len(r["comps"]), -(r["dr"] or 0)))
    cnt = defaultdict(int)
    for r in rows:
        cnt[r["verdict"]] += 1
    lines = [f"# Link gap: {len(rows)} tên miền trỏ ≥ {a.min} đối thủ, chưa trỏ mình", "",
             f"KEEP {cnt['KEEP']} · REVIEW {cnt['REVIEW']} · REJECT {cnt['REJECT']}. REJECT = có cả M1 (Ahrefs spam) và M2 (không có organic).",
             "Theme chưa đo. Claude xét Theme ở Tầng 2 trước khi đưa sang backlink-plan.", "",
             "| Verdict | Tên miền | DR | Số đối thủ | Organic traffic | Từ khoá | Dofollow | Nền tảng | Tín hiệu |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['verdict']} | {r['domain']} | {r['dr']} | {len(r['comps'])} ({', '.join(r['comps'])}) | {r['traffic_domain']} | "
                     f"{r['positions']} | {'có' if r['dofollow'] else 'không'} | {'có' if r['platform'] else ''} | {' '.join(r['machine'])} |")
    write_out(a.out, lines, {"min": a.min, "counts": dict(cnt), "rows": rows})


def classify(anchor, labels, kws):
    s = norm(anchor)
    if not s.strip("​ "):
        return "rong"
    if len(s) > 90 or SPAM_ANCHOR.search(s):
        return "spam"
    if NAKED.search(s):
        return "naked"
    flat = s.replace(" ", "").replace("-", "")
    brand = any(l in flat for l in labels)
    kw_hit = [k for k in kws if k in s]
    if brand:
        return "brand_kw" if kw_hit else "brand"
    if s in kws:
        return "exact"
    if kw_hit:
        return "partial"
    if s in GENERIC:
        return "generic"
    return "chu_de"


GROUPS = ["brand", "brand_kw", "exact", "partial", "naked", "generic", "chu_de", "rong", "spam"]


def cmd_anchors(a):
    kws = [norm(k) for k in a.keywords.split(",") if k.strip()]
    extra = {}
    for part in (a.brand or "").split(";"):
        if "=" in part:
            dom, names = part.split("=", 1)
            extra[dom.strip()] = [norm(n).replace(" ", "") for n in names.split("|") if n.strip()]
    share = {}
    for f in a.file:
        tgt, rows = load(f, "anchors")
        labels = [tgt.split(".")[0].lower()] + extra.get(tgt, [])
        tot = defaultdict(int)
        for r in rows:
            tot[classify(r["anchor"], labels, kws)] += r.get("refdomains") or 0
        n_all = sum(tot.values()) or 1
        n_clean = (sum(v for k, v in tot.items() if k != "spam")) or 1
        share[tgt] = {"spam_share": round(tot["spam"] / n_all, 3), **{g: round(tot[g] / n_clean, 3) for g in GROUPS if g != "spam"}}
    comps = [t for t in share if t != a.mine]
    cons = {g: round(sum(share[t][g] for t in comps) / len(comps), 3) for g in GROUPS if g != "spam"} if comps else {}
    head = [t for t in share]
    lines = ["# Anchor consensus (tỷ lệ theo refdomains, đã bỏ anchor spam)", "",
             "| Nhóm | " + " | ".join(head) + " | Consensus đối thủ | Lệch của mình |", "|---|" + "---|" * (len(head) + 2)]
    for g in GROUPS:
        if g == "spam":
            continue
        dev = round(share[a.mine][g] - cons[g], 3) if a.mine in share and cons else ""
        lines.append(f"| {g} | " + " | ".join(f"{share[t][g]:.0%}" for t in head) + f" | {cons.get(g, 0):.0%} | {dev:+.0%} |" if dev != ""
                     else f"| {g} | " + " | ".join(f"{share[t][g]:.0%}" for t in head) + f" | {cons.get(g, 0):.0%} | |")
    lines.append("| spam (trên tổng) | " + " | ".join(f"{share[t]['spam_share']:.0%}" for t in head) + " | | |")
    lines += ["", "Nhóm `chu_de` là anchor chủ đề không chứa từ khoá đã khai. Claude đọc nhóm này trước khi kết luận lệch exact/partial.",
              "Ahrefs trả theo top anchor của từng site, nên tỷ lệ là của phần đầu hồ sơ, không phải toàn bộ."]
    write_out(a.out, lines, {"keywords": kws, "share": share, "consensus": cons})


def cmd_velocity(a):
    d = json.loads(Path(a.file).read_text(encoding="utf-8"))
    hist = d["history"]
    lines = ["# Nhịp RD ròng theo tháng (refdomains-history, monthly)", "",
             "| Domain | Đầu kỳ | Cuối kỳ | Ròng trung bình/tháng | Tháng tăng mạnh nhất | Tháng giảm mạnh nhất |", "|---|---|---|---|---|---|"]
    out = {}
    for dom, pts in hist.items():
        v = [p["refdomains"] for p in pts]
        diffs = [(pts[i]["date"][:7], v[i] - v[i - 1]) for i in range(1, len(v))]
        avg = round((v[-1] - v[0]) / max(1, len(v) - 1), 1)
        up = max(diffs, key=lambda z: z[1])
        dn = min(diffs, key=lambda z: z[1])
        out[dom] = {"start": v[0], "end": v[-1], "net_per_month": avg, "max_up": up, "max_down": dn}
        lines.append(f"| {dom} | {v[0]} | {v[-1]} | {avg:+} | {up[0]} ({up[1]:+}) | {dn[0]} ({dn[1]:+}) |")
    lines += ["", "Số ròng gồm cả RD spam mới và RD mất. Đọc cùng tỷ lệ spam ở bảng anchor trước khi lấy làm nhịp chuẩn."]
    write_out(a.out, lines, out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gap")
    g.add_argument("--mine", required=True)
    g.add_argument("--comp", nargs="+", required=True)
    g.add_argument("--min", type=int, default=2)
    g.add_argument("--out", required=True)
    n = sub.add_parser("anchors")
    n.add_argument("--file", nargs="+", required=True)
    n.add_argument("--mine", required=True)
    n.add_argument("--keywords", default="")
    n.add_argument("--brand", default="")
    n.add_argument("--out", required=True)
    v = sub.add_parser("velocity")
    v.add_argument("--file", required=True)
    v.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"gap": cmd_gap, "anchors": cmd_anchors, "velocity": cmd_velocity}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
