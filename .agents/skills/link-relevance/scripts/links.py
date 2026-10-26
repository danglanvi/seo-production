#!/usr/bin/env python3
"""link-relevance: kiểm anchor và đoạn chứa link có khớp trang đích không (link nội bộ).

Chạy bằng venv embedding (numpy; lệnh prepare cần thêm sentence-transformers):
  prepare  --rows rows.jsonl --pages pages.jsonl --store DIR --out-dir W [--queries queries.jsonl]
           [--listing REGEX] [--min-share 0.6] [--brand "Tên brand,tên khác"]
           Đọc anchor vùng main từ rows.jsonl của site-vector-index. Kiểm bằng code: đích lỗi, trang chuyên mục,
           anchor rỗng, URL trần, lệch ngôn ngữ, một anchor trỏ nhiều đích, anchor trùng query GSC mà đích khác URL
           Google chọn. EmbeddingGemma: "anchor: đoạn" (prompt SearchQuery) so với mọi trang (Document), lấy margin
           giữa trang đích và trang gần nhất còn lại. Ra links.jsonl, jev_in.jsonl, summary.json.
  sample   --links W/links.jsonl --out-dir W/calibration [--low 25 --mid 20 --high 15 --random 30] [--seed 19]
           [--exclude ids.json ...]
           Phiếu gán gold mù: gold_todo.txt (không có điểm model) và gold_template.jsonl để điền yes/no.
  validate --links W/links.jsonl --gold gold.jsonl --jev-out jev_out.jsonl --out-dir W/calibration
           [--clusters pages.jsonl của topical-focus]
           Ra jev_gold.jsonl (cho calibrate.py jev), score_pairs.jsonl (điểm gộp, cho calibrate.py cosine --grid)
           và gsc_rows.jsonl (cho calibrate.py auc, nhóm theo cụm chủ đề của trang đích).
  decide   --links W/links.jsonl --jev-out jev_out.jsonl --registry model-calibration.json --site <domain>
           --out-dir W
           Điểm gộp = p(delivers) của Jev + 4 × margin Gemma. Cổng lấy từ registry: rubric anchor-score (cosine).
           Ra decisions.jsonl, report.md.
Cosine và margin không so được giữa các site hay giữa các model.
Mô phỏng ý tưởng anchor context, anchorMismatchDemotion trong tài liệu rò rỉ của Google; công thức thật chưa công bố.
"""
import argparse
import hashlib
import json
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

GENERIC = re.compile(r"^(xem chi tiết|xem thêm|chi tiết|tại đây|ở đây|tìm hiểu thêm|xem ngay|tư vấn ngay|đăng ký|"
                     r"đọc thêm|click here|here|read more|learn more|see more|register now|more|link)$")
HOME = {"trang chủ", "home", "homepage"}
RUBRIC = "anchor-score"
WEIGHT = 4  # trọng số margin trong điểm gộp, chọn trên gold dev, giữ cố định giữa các site


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def nu(u):
    return (u or "").split("#")[0].split("?")[0].rstrip("/")


def norm(s):
    s = unicodedata.normalize("NFC", s or "").replace("​", "").casefold()
    return re.sub(r"\s+", " ", s).strip(" .,:;!?\"'“”()[]-–>»→↗")


def path_of(u):
    return urlparse(u).path or "/"


def lang_of(u, page):
    lang = (page or {}).get("lang") or ("en" if path_of(u).startswith("/en/") else "vi")
    return lang.split("-")[0].lower()


def cmd_prepare(a):
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
    import svi  # noqa: E402  (cùng bộ skill)

    pages = {nu(p["url"]): p for p in jl(a.pages)}
    rows = jl(a.rows)
    anchors = [r for r in rows if r["level"] == "anchor" and (r.get("meta") or {}).get("zone", "main") == "main"]
    n_main = Counter(nu(r["url"]) for r in anchors)
    rx = re.compile(a.listing) if a.listing else None

    def listing(u):
        p = pages.get(u) or {}
        if rx and rx.search(path_of(u)):
            return True
        return (p.get("words_main") or 0) < 150 and n_main[u] >= 8

    def names_page(anc, u):
        """Anchor gọi đúng tên trang chuyên mục (menu chuyên mục): H1, phần đầu title hoặc đoạn cuối URL."""
        p, a = pages.get(u) or {}, norm(anc)
        h1 = p.get("h1") or ""
        names = {norm(h1[0] if isinstance(h1, list) and h1 else h1), norm(re.split(r"\s[|–-]\s", p.get("title") or "")[0]),
                 norm(path_of(u).rstrip("/").rsplit("/", 1)[-1].replace("-", " "))}
        return bool(a) and a in names

    st = svi.Store(a.store)
    pidx = [i for i, it in enumerate(st.items) if it["level"] == "page"]
    purl = [nu(st.items[i]["url"]) for i in pidx]
    pos = {u: k for k, u in enumerate(purl)}
    P = st.vec[pidx].astype(np.float32)

    queries = {}
    if a.queries:
        for q in jl(a.queries):
            if q.get("group") != "brand" and q.get("share", 1) >= a.min_share:
                queries[norm(q["text"])] = q

    brands = {norm(b) for b in (a.brand or "").split(",") if b.strip()}
    links, skipped = [], Counter()
    for r in anchors:
        src, tgt = nu(r["url"]), nu(r["meta"]["target"])
        if tgt == src:
            skipped["tự trỏ"] += 1
            continue
        anc = (r["meta"].get("anchor") or "").replace("​", "").strip()
        flags = []
        if tgt not in pages:
            flags.append("target_missing")
        elif listing(tgt):
            flags.append("listing_named" if names_page(anc, tgt) else "target_listing")
        elif names_page(anc, tgt) or (path_of(tgt) in ("", "/") and norm(anc) in HOME | brands):
            flags.append("anchor_names_target")
        if not anc:
            flags.append("empty_anchor")
        elif anc.startswith("http"):
            flags.append("naked_url")
        elif GENERIC.match(norm(anc)):
            flags.append("generic_anchor")
        if tgt in pages and lang_of(src, pages.get(src)) != lang_of(tgt, pages.get(tgt)):
            flags.append("lang_mismatch")
        x = {"id": r["id"], "src": src, "target": tgt, "anchor": anc, "ctx": r["text"][:1500], "flags": flags}
        q = queries.get(norm(anc))
        if q:
            x["gsc"] = {"query": q["text"], "chosen": nu(q["chosen"]), "share": q.get("share"), "impr": q.get("impr")}
            if nu(q["chosen"]) != tgt:
                flags.append("gsc_conflict")
        links.append(x)

    targets = defaultdict(set)
    for x in links:
        if x["anchor"] and not ({"generic_anchor", "naked_url"} & set(x["flags"])) and len(norm(x["anchor"])) >= 4:
            targets[norm(x["anchor"])].add(x["target"])
    for x in links:
        t = targets.get(norm(x["anchor"]), set())
        if len(t) > 1:
            x["flags"].append("anchor_multi_target")
            x["other_targets"] = sorted(t - {x["target"]})

    todo = [x for x in links if x["target"] in pos]
    texts = [f"{x['anchor'] or 'link'}: {x['ctx']}" for x in todo]
    enc = svi.encoder(a.max_tokens)
    Q = enc.encode(texts, "SearchQuery") if texts else np.zeros((0, P.shape[1]), dtype=np.float32)
    for j, x in enumerate(todo):
        c = P @ Q[j]
        if x["src"] in pos:
            c[pos[x["src"]]] = -9
        t = pos[x["target"]]
        ct = float(c[t])
        c[t] = -9
        bo = int(np.argmax(c))
        x["gemma"] = {"cos": round(ct, 4), "rank": int((c > ct).sum()) + 1, "margin": round(ct - float(c[bo]), 4),
                      "best_other": purl[bo]}

    jev_in, seen = [], set()
    for x in links:
        if "gemma" not in x or {"target_listing", "listing_named", "anchor_names_target"} & set(x["flags"]):
            continue
        key = hashlib.sha1(f"{x['anchor']}|{x['target']}|{x['ctx']}".encode()).hexdigest()[:16]
        x["jev_id"] = key
        if key in seen:
            continue
        seen.add(key)
        tu, tp, sp = path_of(x["target"]), pages[x["target"]], pages.get(x["src"]) or {}
        ctx, anc = x["ctx"], x["anchor"]
        para = ctx.replace(anc, f"[{anc}]({tu})", 1) if anc and anc in ctx else f"{ctx} [{anc or 'link'}]({tu})"
        jev_in.append({"id": key, "state": {
            "page": {"title": [sp.get("title", "")], "type": "web page"},
            "link_location": {"paragraph": para[:1500]},
            "target": {"url": tu, "title": tp.get("title", ""),
                       "summary": (tp.get("first_para") or tp.get("meta") or "")[:500],
                       "headings": (tp.get("h2") or [])[:12], "words": tp.get("words_main")}}})

    out = Path(a.out_dir)
    write(out / "links.jsonl", links)
    write(out / "jev_in.jsonl", jev_in)
    summ = {"model": svi.MODEL, "n_links": len(links), "skipped": dict(skipped), "n_jev": len(jev_in),
            "flags": dict(Counter(f for x in links for f in x["flags"])), "gsc_queries": len(queries)}
    (out / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False))


def cmd_sample(a):
    links = [x for x in jl(a.links) if "gemma" in x and "target_listing" not in x["flags"] and "gsc" not in x]
    excl = set()
    for f in a.exclude or []:
        excl |= set(json.loads(Path(f).read_text(encoding="utf-8")))
    uniq, seen = [], set()
    for x in links:
        k = (norm(x["anchor"]), x["target"])
        if k in seen or x["id"] in excl:
            continue
        seen.add(k)
        uniq.append(x)
    r = random.Random(a.seed)
    m = lambda x: x["gemma"]["margin"]
    bands = [[x for x in uniq if m(x) < -0.03], [x for x in uniq if -0.03 <= m(x) <= 0.03], [x for x in uniq if m(x) > 0.03]]
    pick = []
    for band, n in zip(bands, (a.low, a.mid, a.high)):
        pick += r.sample(band, min(n, len(band)))
    ids = {x["id"] for x in pick}
    rest = [x for x in uniq if x["id"] not in ids]
    pick += r.sample(rest, min(a.random, len(rest)))
    r.shuffle(pick)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "gold_ids.json").write_text(json.dumps([x["id"] for x in pick]), encoding="utf-8")
    write(out / "gold_template.jsonl", [{"id": x["id"], "label": None, "note": ""} for x in pick])
    with open(out / "gold_todo.txt", "w", encoding="utf-8") as f:
        for i, x in enumerate(pick):
            f.write(f"[{i}] SRC {path_of(x['src'])}\n  ANCHOR: {x['anchor'][:150]}\n  CTX: {x['ctx'][:300]}\n"
                    f"  TARGET {path_of(x['target'])}\n\n")
    print(f"{len(pick)} link -> {out}/gold_todo.txt; điền nhãn yes/no vào gold_template.jsonl rồi lưu gold.jsonl")


def jev_p(path):
    out = {}
    for d in jl(path):
        ans = (d.get("answers") or {}).get("delivers")
        if ans and "p_yes" in ans:
            out[d["id"]] = ans["p_yes"]
    return out


def score(p, margin):
    return round(p + WEIGHT * margin, 4)


def cmd_validate(a):
    links = {x["id"]: x for x in jl(a.links)}
    gold = {g["id"]: g["label"] for g in jl(a.gold) if g.get("label") in ("yes", "no")}
    jp = jev_p(a.jev_out)
    out = Path(a.out_dir)
    jg, pairs = [], []
    for i, lab in gold.items():
        x = links.get(i)
        if not x or "jev_id" not in x or x["jev_id"] not in jp:
            continue
        jg.append({"id": x["jev_id"], "label": lab})
        pairs.append({"id": i, "cos": score(jp[x["jev_id"]], x["gemma"]["margin"]), "label": int(lab == "yes")})
    write(out / "jev_gold.jsonl", jg)
    write(out / "score_pairs.jsonl", pairs)
    cl = {nu(p["url"]): p.get("cluster") for p in jl(a.clusters)} if a.clusters else {}
    grp = defaultdict(list)
    for x in links.values():
        if "gsc" in x and "gemma" in x:
            grp[(norm(x["anchor"]), x["target"])].append(x)
    gsc = [{"id": f"{k[0]}|{k[1]}", "margin": round(sum(v["gemma"]["margin"] for v in xs) / len(xs), 4),
            "agree": int(xs[0]["gsc"]["chosen"] == k[1]), "group": str(cl.get(k[1], "all"))} for k, xs in grp.items()]
    write(out / "gsc_rows.jsonl", gsc)
    print(f"jev_gold {len(jg)} · score_pairs {len(pairs)} · gsc_rows {len(gsc)} -> {out}")


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def score_version():
    task = Path(__file__).resolve().parents[1] / "tasks" / "anchor-target.json"
    return json.loads(task.read_text(encoding="utf-8"))["version"] + f"+w{WEIGHT}"


def gate(registry, site, rubric, mode, version):
    for path, want in ((registry, site), (find_defaults(), None)):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == rubric and e.get("mode") == mode and e.get("version") == version \
                    and (want is None or e.get("site") == want) and e.get("threshold") is not None:
                return e["threshold"], ("site" if want else "defaults")
    return None, None


def cmd_decide(a):
    links = jl(a.links)
    jp = jev_p(a.jev_out)
    ver = a.version or score_version()
    thr, src = gate(a.registry, a.site, RUBRIC, "cosine", ver)
    if thr is None:
        sys.exit(f"thiếu cổng anchor-score {ver}: hiệu chuẩn bằng model-calibration (sample → gold → validate → cosine)")
    dec = []
    for x in links:
        f, g = set(x["flags"]), x.get("gemma") or {}
        p = jp.get(x.get("jev_id"))
        sc = score(p, g["margin"]) if p is not None and g else None
        if "target_missing" in f:
            st = "đích lỗi"
        elif "target_listing" in f:
            st = "review" if "generic_anchor" in f else "lệch: trang chuyên mục"
        elif {"listing_named", "anchor_names_target"} & f:
            st = "khớp"
        elif sc is not None and sc >= thr:
            st = "khớp"
        else:
            st = "review"
        dec.append({**x, "jev_p": p, "score": sc, "status": st})
    out = Path(a.out_dir)
    write(out / "decisions.jsonl", dec)
    c = Counter(d["status"] for d in dec)
    P = path_of
    L = ["# Độ khớp anchor và trang đích", "",
         f"{len(dec)} link nội bộ vùng main. Điểm gộp = p Jev + {WEIGHT} × margin Gemma; khớp khi ≥ {thr} ({src}).", ""]
    if src == "defaults":
        L += ["Có cổng lấy từ defaults (đo trên site khác): kết quả là bản nháp tới khi hiệu chuẩn trên 40+ link của site này.", ""]
    L += ["| Trạng thái | Link |", "|---|---|"] + [f"| {k} | {v} |" for k, v in c.most_common()] + [""]
    L += ["Chỉ số mô phỏng, trọng số thật của Google chưa công bố. Claude đọc mọi link review trước khi đề xuất sửa.", ""]

    lst = defaultdict(list)
    for d in dec:
        if d["status"] == "lệch: trang chuyên mục":
            lst[d["target"]].append(d)
    if lst:
        L += ["## Link trỏ về trang chuyên mục", "", "Anchor nêu một chủ đề cụ thể nhưng đích chỉ liệt kê bài.", "",
              "| Trang chuyên mục | Link | Ví dụ anchor |", "|---|---|---|"]
        for t, ds in sorted(lst.items(), key=lambda kv: -len(kv[1])):
            L.append(f"| {P(t)} | {len(ds)} | {' · '.join(sorted({d['anchor'][:40] for d in ds})[:5])} |")
        L.append("")

    gc = defaultdict(list)
    for d in dec:
        if "gsc_conflict" in d["flags"]:
            gc[(d["gsc"]["query"], d["target"])].append(d)
    if gc:
        L += ["## Anchor trùng query GSC nhưng trỏ khác URL Google chọn", "",
              "| Query | Hiển thị | Link trỏ tới | Google chọn | Link | Margin |", "|---|---|---|---|---|---|"]
        for (q, t), ds in sorted(gc.items(), key=lambda kv: -(kv[1][0]["gsc"].get("impr") or 0))[:40]:
            g, ms = ds[0]["gsc"], [d["gemma"]["margin"] for d in ds if "gemma" in d]
            L.append(f"| {q} | {g.get('impr')} | {P(t)} | {P(g['chosen'])} | {len(ds)} | "
                     f"{round(sum(ms) / len(ms), 3) if ms else 'đích lỗi'} |")
        L.append("")

    mt = defaultdict(set)
    for d in dec:
        if "anchor_multi_target" in d["flags"]:
            mt[norm(d["anchor"])].add(P(d["target"]))
    if mt:
        L += ["## Một anchor trỏ nhiều đích", "", "| Anchor | Đích |", "|---|---|"]
        for k, ts in sorted(mt.items(), key=lambda kv: -len(kv[1]))[:30]:
            L.append(f"| {k} | {' · '.join(sorted(ts))} |")
        L.append("")

    rv = sorted([d for d in dec if d["status"] == "review"], key=lambda d: -9 if d["score"] is None else d["score"])
    if rv:
        L += [f"## Link cần Claude đọc ({len(rv)}, điểm thấp trước)", "",
              "| Trang | Anchor | Đích | Jev | Margin | Trang gần hơn |", "|---|---|---|---|---|---|"]
        for d in rv[:a.top]:
            g = d.get("gemma") or {}
            jpv = "" if d["jev_p"] is None else round(d["jev_p"], 2)
            L.append(f"| {P(d['src'])} | {d['anchor'][:50]} | {P(d['target'])} | {jpv} | {g.get('margin')} | "
                     f"{P(g['best_other']) if g.get('margin', 0) < 0 else ''} |")
        L.append("")
    other = Counter(f for d in dec for f in d["flags"] if f in ("empty_anchor", "naked_url", "lang_mismatch"))
    if other or c.get("đích lỗi"):
        L += ["## Lỗi code khác", "", "| Lỗi | Link |", "|---|---|"]
        L += [f"| đích lỗi (redirect, 404, noindex hoặc ngoài crawl) | {c.get('đích lỗi', 0)} |"]
        L += [f"| {k} | {v} |" for k, v in other.most_common()] + [""]
    (out / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(json.dumps(dict(c), ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--rows", required=True)
    p.add_argument("--pages", required=True)
    p.add_argument("--store", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--queries", default=None, help="queries.jsonl của retrieval-lab route: text, chosen, share, impr")
    p.add_argument("--listing", default=None, help="regex đường dẫn trang chuyên mục, thêm vào luật tự nhận")
    p.add_argument("--min-share", type=float, default=0.6)
    p.add_argument("--brand", default="", help="tên brand, cách nhau bởi dấu phẩy: anchor là tên brand trỏ trang chủ thì khớp")
    p.add_argument("--max-tokens", type=int, default=512)
    s = sub.add_parser("sample")
    s.add_argument("--links", required=True)
    s.add_argument("--out-dir", required=True)
    for k, v in (("low", 25), ("mid", 20), ("high", 15), ("random", 30), ("seed", 19)):
        s.add_argument(f"--{k}", type=int, default=v)
    s.add_argument("--exclude", nargs="*", default=None, help="gold_ids.json của vòng trước")
    v = sub.add_parser("validate")
    v.add_argument("--links", required=True)
    v.add_argument("--gold", required=True)
    v.add_argument("--jev-out", required=True)
    v.add_argument("--out-dir", required=True)
    v.add_argument("--clusters", default=None, help="pages.jsonl của topical-focus (url → cluster)")
    d = sub.add_parser("decide")
    d.add_argument("--links", required=True)
    d.add_argument("--jev-out", required=True)
    d.add_argument("--registry", default=None)
    d.add_argument("--site", required=True)
    d.add_argument("--out-dir", required=True)
    d.add_argument("--top", type=int, default=60)
    d.add_argument("--version", default=None, help="version cổng; mặc định = version rubric anchor-target + trọng số")
    a = ap.parse_args()
    {"prepare": cmd_prepare, "sample": cmd_sample, "validate": cmd_validate, "decide": cmd_decide}[a.cmd](a)


if __name__ == "__main__":
    main()
