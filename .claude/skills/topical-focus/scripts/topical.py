#!/usr/bin/env python3
"""topical-focus: đo độ tập trung chủ đề của site và vị trí từng trang so với tâm site (EmbeddingGemma 2, local).

Chạy bằng venv embedding (numpy, scikit-learn; lệnh plan cần thêm sentence-transformers):
  map   --store DIR --out DIR [--pages pages.jsonl --lang vi --exclude REGEX] [--min-words 300]
        [--core core.txt] [--k auto|N] [--dims 768] [--outlier-pct 10] [--metrics metrics.jsonl]
        [--proof REGEX] [--names names.json]
        Đọc vector cấp page (prompt Document) trong store của site-vector-index.
        Ra pages.jsonl, clusters.json, summary.json, centroids.npz, proxy_rows.jsonl, report.md.
  selftest --map DIR --pages pages.jsonl [--target 0.95]
        Dùng tiêu đề + H2 của trang có sẵn làm bài dự kiến, đo độ khớp cụm, ghi cổng margin vào plan_gate.json.
  plan  --map DIR --in plan.jsonl --out out.jsonl
        Bài dự kiến {"id", "title", "outline": [h2...]} → cụm gần nhất, khoảng cách tới cụm thứ hai, 3 trang gần nhất.
        Bài có margin dưới cổng của selftest ghi review=true.
  gold-sheet --site-pages pages.jsonl --competitor titles.jsonl [...] --n 60 --seed 19 --out sheet.jsonl [--skip ids.txt]
        Lấy mẫu trang đối thủ để gán gold mù: mỗi dòng có title, H1 và 8 trang của site gần nhất theo trùng chữ
        (không dùng cosine). Người gán ghi "covered": 1 nếu site đã có trang cùng chủ đề chính, 0 nếu chưa.
  gap   --site-pages pages.jsonl --competitor titles.jsonl [...] --out DIR [--prompt Document]
        [--gap 0.xx] [--cover 0.xx] [--group-cos 0.83] [--lang vi --exclude REGEX]
        Khoảng trống chủ đề với đối thủ: embed title + H1 của site và đối thủ, tìm trang site gần nhất cho từng trang
        đối thủ, gom trang đối thủ chưa có trang tương ứng thành cụm. Ra gap_pages.jsonl, gap_groups.json, gap_report.md.
        Cosine dưới --gap: khoảng trống. Từ --cover trở lên: site đã có (chỉ đặt khi registry có ngưỡng này).
        Còn lại: Claude đọc. Không có --gap thì mọi trang ghi review (lượt đầu để hiệu chuẩn).
Cosine không so được giữa các site hay giữa các model. So mốc trên cùng site, cùng scope và cùng số chiều.
Chỉ số mô phỏng ý tưởng siteFocusScore, siteRadius trong tài liệu rò rỉ của Google, công thức thật chưa công bố.
"""
import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "site-vector-index" / "scripts"))
import svi  # noqa: E402  (cùng bộ skill; Store, encoder, mrl)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def unit(v):
    return v / max(float(np.linalg.norm(v)), 1e-12)


def norm_url(u):
    return (u or "").split("#")[0].split("?")[0].rstrip("/")


def folder(u):
    parts = [p for p in urlparse(u).path.split("/") if p]
    return "/" + parts[0] + "/" if len(parts) > 1 else "/"


def scope(a, st):
    """Trang trong scope: cấp page, đủ chữ, đúng ngôn ngữ, index được, canonical trỏ về chính nó."""
    info = {p["url"]: p for p in jl(a.pages)} if a.pages else {}
    rx = re.compile(a.exclude) if a.exclude else None
    keep, dropped = [], {}

    def drop(why):
        dropped[why] = dropped.get(why, 0) + 1

    for i, it in enumerate(st.items):
        if it["level"] != "page":
            continue
        u, p = it["url"], info.get(it["url"], {})
        words = it["meta"].get("words_main") or p.get("words_main") or 0
        if rx and rx.search(u):
            drop("exclude")
        elif words < a.min_words:
            drop(f"dưới {a.min_words} chữ")
        elif a.lang and p and not (p.get("lang") or "").lower().startswith(a.lang):
            drop("khác ngôn ngữ")
        elif p and "noindex" in (p.get("robots") or "").lower():
            drop("noindex")
        elif p and p.get("canonical") and norm_url(p["canonical"]) != norm_url(u):
            drop("canonical trỏ trang khác")
        else:
            keep.append(i)
    if a.pages and not info:
        sys.exit("--pages rỗng")
    return keep, dropped


def pick_k(M, k_arg):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    n = len(M)
    if k_arg != "auto":
        k = int(k_arg)
        km = KMeans(k, n_init=10, random_state=0).fit(M)
        return km, None, []
    # Sàn kích thước cụm: vài trang lạc đề tự thành cụm riêng sẽ đẩy silhouette lên mà không thành chủ đề.
    floor = max(5, int(n * 0.02))
    scan = []
    for k in range(3, min(12, n // 8) + 1):
        km = KMeans(k, n_init=10, random_state=0).fit(M)
        s = silhouette_score(M, km.labels_, metric="cosine", sample_size=min(n, 3000), random_state=0)
        scan.append((k, round(float(s), 3), int(np.bincount(km.labels_).min()), km))
    ok = [x for x in scan if x[2] >= floor]
    if not ok:
        sys.exit(f"chỉ {n} trang hoặc mọi k đều có cụm dưới {floor} trang: đặt --k")
    best = max(ok, key=lambda x: (x[1], -x[0]))
    return best[3], best[1], [{"k": k, "silhouette": s, "min_size": m} for k, s, m, _ in scan]


def cmd_map(a):
    st = svi.Store(a.store)
    if not st.items:
        sys.exit("store rỗng")
    idx, dropped = scope(a, st)
    if len(idx) < 24:
        sys.exit(f"chỉ {len(idx)} trang trong scope (bỏ: {dropped})")
    if any(st.items[i].get("prompt", "Document") != "Document" for i in idx):
        sys.exit("vector cấp page phải dựng bằng prompt Document: pilot đo Clustering, SentenceSimilarity không có tín hiệu")
    M = svi.mrl(st.vec[idx].astype(np.float32), a.dims)
    items = [st.items[i] for i in idx]
    urls = [it["url"] for it in items]
    c = unit(M.mean(0))
    cs = M @ c
    core = None
    if a.core:
        want = {norm_url(l.strip()) for l in Path(a.core).read_text(encoding="utf-8").splitlines() if l.strip()}
        ci = [k for k, u in enumerate(urls) if norm_url(u) in want]
        if len(ci) < 2:
            sys.exit(f"--core: chỉ {len(ci)} URL có trong scope, cần ít nhất 2")
        core = unit(M[ci].mean(0))
    km, sil, scan = pick_k(M, a.k)
    C = np.stack([unit(x) for x in km.cluster_centers_])
    lab = km.labels_
    metrics = {norm_url(m["url"]): m for m in jl(a.metrics)} if a.metrics else {}
    names = json.loads(Path(a.names).read_text(encoding="utf-8")) if a.names else {}
    proof = re.compile(a.proof) if a.proof else None
    pct = (np.argsort(np.argsort(cs)) + 1) / len(cs) * 100
    rows = []
    for k, it in enumerate(items):
        m = metrics.get(norm_url(it["url"]), {})
        role = "proof" if proof and proof.search(it["url"]) else "content"
        r = {"url": it["url"], "title": it["meta"].get("title"), "words": it["meta"].get("words_main"),
             "folder": folder(it["url"]), "role": role, "cos_site": round(float(cs[k]), 4),
             "pct_site": round(float(pct[k]), 1), "cluster": int(lab[k]),
             "cos_cluster": round(float(M[k] @ C[lab[k]]), 4), "outlier": bool(pct[k] <= a.outlier_pct)}
        if core is not None:
            r["cos_core"] = round(float(M[k] @ core), 4)
        if metrics:
            r["impressions"] = m.get("impressions", 0)
            r["clicks"] = m.get("clicks", 0)
        rows.append(r)
    clusters = []
    for j in range(len(C)):
        ix = np.flatnonzero(lab == j)
        near = ix[np.argsort(-(M[ix] @ C[j]))[:5]]
        folders = {}
        for k in ix:
            folders[rows[k]["folder"]] = folders.get(rows[k]["folder"], 0) + 1
        cl = {"cluster": j, "name": names.get(str(j), ""), "n": int(len(ix)), "share": round(len(ix) / len(rows), 3),
              "cos_to_site": round(float(C[j] @ c), 4), "mean_cos_site": round(float(cs[ix].mean()), 4),
              "near_titles": [rows[k]["title"] for k in near],
              "top_folders": sorted(folders.items(), key=lambda x: -x[1])[:3]}
        if core is not None:
            cl["cos_to_core"] = round(float(C[j] @ core), 4)
        if metrics:
            cl["impressions"] = int(sum(rows[k]["impressions"] for k in ix))
            cl["clicks"] = int(sum(rows[k]["clicks"] for k in ix))
        clusters.append(cl)
    clusters.sort(key=lambda x: x["cos_to_site"])
    summary = {"model": st.manifest.get("model"), "dims": a.dims, "n_pages": len(rows), "dropped": dropped,
               "focus_mean_cos": round(float(cs.mean()), 4),
               "radius_p50": round(float(np.percentile(1 - cs, 50)), 4),
               "radius_p90": round(float(np.percentile(1 - cs, 90)), 4),
               "k": int(len(C)), "silhouette": sil, "k_scan": scan,
               "cos_site_core": round(float(c @ core), 4) if core is not None else None,
               "outlier_pct": a.outlier_pct, "scope": {"lang": a.lang, "exclude": a.exclude, "min_words": a.min_words}}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write(out / "pages.jsonl", rows)
    (out / "clusters.json").write_text(json.dumps(clusters, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    np.savez(out / "centroids.npz", site=c, core=core if core is not None else np.zeros(0), clusters=C,
             pages=M.astype(np.float16), urls=np.asarray(urls), dims=np.asarray(a.dims))
    proxy = [{"id": r["url"], "cos_site": r["cos_site"], "cos_core": r.get("cos_core"),
              "log_impr": math.log1p(r["impressions"]) if metrics else None,
              "log_words": math.log(max(r["words"] or 1, 1)), "cluster": r["cluster"], "folder": r["folder"]}
             for r in rows]
    write(out / "proxy_rows.jsonl", proxy)
    (out / "report.md").write_text(report(summary, clusters, rows, bool(metrics), core is not None), encoding="utf-8")
    print(f"map: {len(rows)} trang, {len(C)} cụm, focus {summary['focus_mean_cos']}, "
          f"radius_p90 {summary['radius_p90']} -> {out}", file=sys.stderr)


def report(s, clusters, rows, has_m, has_core):
    L = ["# Độ tập trung chủ đề", "",
         f"Scope: {s['n_pages']} trang (bỏ {sum(s['dropped'].values())}: {s['dropped']}). "
         f"Model {s['model']}, {s['dims']} chiều.", "",
         f"- Focus (cosine trung bình tới tâm site): {s['focus_mean_cos']}",
         f"- Bán kính: p50 {s['radius_p50']}, p90 {s['radius_p90']} (1 − cosine)",
         f"- Số cụm: {s['k']}" + (f", silhouette {s['silhouette']}" if s["silhouette"] is not None else "")]
    if has_core:
        L.append(f"- Cosine giữa tâm site và tâm trang lõi: {s['cos_site_core']}")
    L += ["", "Chỉ số mô phỏng, trọng số thật của Google chưa công bố. So mốc trên cùng site, cùng scope.", "",
          "## Cụm chủ đề (xa tâm trước)", "",
          "| Cụm | Tên | Trang | Tỷ trọng | Cos tới tâm site |" + (" Cos tới lõi |" if has_core else "")
          + (" Hiển thị |" if has_m else "") + " Tiêu đề gần tâm cụm |",
          "|---|---|---|---|---|" + ("---|" if has_core else "") + ("---|" if has_m else "") + "---|"]
    for c in clusters:
        L.append(f"| C{c['cluster']} | {c['name'] or '(Claude đặt tên)'} | {c['n']} | {c['share']:.0%} | {c['cos_to_site']} |"
                 + (f" {c['cos_to_core']} |" if has_core else "") + (f" {c['impressions']:,} |" if has_m else "")
                 + " " + " · ".join((t or "")[:60] for t in c["near_titles"][:3]) + " |")
    content = [r for r in rows if r["role"] == "content"]
    med = float(np.median([r["impressions"] for r in content])) if has_m and content else None
    out = sorted([r for r in content if r["outlier"]], key=lambda r: r["cos_site"])
    L += ["", f"## Trang nội dung xa tâm (dưới phân vị {s['outlier_pct']})", ""]
    if has_m:
        L.append(f"Mốc \"ít hiển thị\": dưới trung vị của trang nội dung trong scope ({med:,.0f}).")
        L.append("")
    L += ["| URL | Tiêu đề | Cos tới tâm | Cụm |" + (" Hiển thị | Nhóm đọc |" if has_m else ""),
          "|---|---|---|---|" + ("---|---|" if has_m else "")]
    for r in out:
        L.append(f"| {r['url']} | {(r['title'] or '')[:70]} | {r['cos_site']} | C{r['cluster']} |"
                 + (f" {r['impressions']:,} | {'ít hiển thị' if r['impressions'] < med else 'nhiều hiển thị'} |"
                    if has_m else ""))
    proof_out = [r for r in rows if r["role"] == "proof" and r["outlier"]]
    if proof_out:
        L += ["", f"Trang bằng chứng (case study, tác giả, giới thiệu) xa tâm: {len(proof_out)} trang. "
              "Không xét gộp hay bỏ theo độ lệch tâm: các trang này phục vụ EEAT và consensus."]
    L += ["", "## Đọc kết quả", "",
          "- Trang xa tâm, ít hiển thị: chuyển sang `content-refresh` để xét CONSOLIDATE hoặc PRUNE.",
          "- Trang xa tâm, nhiều hiển thị: giữ trang. Không mở rộng nhánh đó khi chưa có quyết định chiến lược.",
          "- Cụm xa tâm nhưng là mảng kinh doanh: đối chiếu topical map. Bổ sung bài nối cụm đó với cụm lõi.",
          "- Người vận hành quyết việc gộp, bỏ hay giữ. Script không tự đề xuất xoá trang."]
    return "\n".join(L) + "\n"


def assign(map_dir, plan, max_tokens):
    z = np.load(Path(map_dir) / "centroids.npz")
    dims = int(z["dims"])
    site, C, P, urls = z["site"], z["clusters"], z["pages"].astype(np.float32), [str(u) for u in z["urls"]]
    clusters = {c["cluster"]: c for c in json.loads((Path(map_dir) / "clusters.json").read_text(encoding="utf-8"))}
    texts = [(p.get("title") or "") + "\n" + "\n".join(p.get("outline") or []) for p in plan]
    V = svi.mrl(svi.encoder(max_tokens).encode(texts, "Document"), dims)
    out = []
    for p, v in zip(plan, V):
        s = C @ v
        o = np.argsort(-s)
        near = np.argsort(-(P @ v))[:3]
        cl = clusters[int(o[0])]
        out.append({"id": p["id"], "title": p.get("title"), "cluster": int(o[0]), "cluster_name": cl.get("name"),
                    "cos_cluster": round(float(s[o[0]]), 4), "margin_2nd": round(float(s[o[0]] - s[o[1]]), 4),
                    "cluster_cos_to_site": cl["cos_to_site"], "cos_site_ref": round(float(v @ site), 4),
                    "nearest_pages": [{"url": urls[k], "cos": round(float(P[k] @ v), 4)} for k in near]})
    return out


def cmd_plan(a):
    gate_file = Path(a.map) / "plan_gate.json"
    gate = json.loads(gate_file.read_text(encoding="utf-8")).get("margin_gate") if gate_file.exists() else None
    out = assign(a.map, jl(a.inp), a.max_tokens)
    for r in out:
        r["review"] = gate is None or r["margin_2nd"] < gate
    write(a.out, out)
    note = f"cổng margin {gate}" if gate is not None else "chưa chạy selftest: mọi bài ghi review"
    print(f"plan: {len(out)} bài, {sum(r['review'] for r in out)} cần Claude đọc ({note}) -> {a.out}", file=sys.stderr)


def wilson_low(k, n, z=1.96):
    if not n:
        return 0.0
    p = k / n
    return (p + z * z / (2 * n) - z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5) / (1 + z * z / n)


def cmd_selftest(a):
    """Lấy tiêu đề + H2 của trang có sẵn làm "bài dự kiến", so cụm gán được với cụm của chính trang đó."""
    info = {p["url"]: p for p in jl(a.pages)}
    rows = jl(Path(a.map) / "pages.jsonl")
    plan = [{"id": r["url"], "title": info[r["url"]].get("title"), "outline": (info[r["url"]].get("h2") or [])[:12]}
            for r in rows if r["url"] in info and info[r["url"]].get("h2")]
    if len(plan) < 40:
        sys.exit(f"chỉ {len(plan)} trang có H2: cần ít nhất 40")
    truth = {r["url"]: r["cluster"] for r in rows}
    out = assign(a.map, plan, a.max_tokens)
    ok = np.asarray([r["cluster"] == truth[r["id"]] for r in out])
    mg = np.asarray([r["margin_2nd"] for r in out])
    bands, gate = [], None
    for t in (0.0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05):
        sel = mg >= t
        n, k = int(sel.sum()), int(ok[sel].sum())
        b = {"margin": t, "n": n, "agree": round(k / n, 3) if n else None, "coverage": round(n / len(ok), 3),
             "wilson_low": round(wilson_low(k, n), 3)}
        bands.append(b)
        if gate is None and n >= 30 and b["agree"] >= a.target and b["wilson_low"] >= a.target - 0.1:
            gate = t
    res = {"n": len(out), "agree_all": round(float(ok.mean()), 3), "target": a.target, "margin_gate": gate,
           "bands": bands, "note": "outline của trang có sẵn; trang đó có góp vào tâm cụm nên số hơi lạc quan"}
    (Path(a.map) / "plan_gate.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"selftest: khớp {res['agree_all']:.1%}, cổng margin {gate} -> {Path(a.map) / 'plan_gate.json'}",
          file=sys.stderr)


SEP = re.compile(r"\s+[|\-–—:]\s+")
DATES = re.compile(r"\b(?:(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+)?"
                   r"(?:19|20)\d{2}\b|\btháng\s+\d{1,2}(?:\s*/\s*\d{4})?", re.I)


def brand_tails(titles, min_share=0.15):
    """Đoạn cuối title lặp ở nhiều trang của một site (tên brand, slogan): bỏ trước khi embed."""
    tails = {}
    for t in titles:
        parts = SEP.split(t or "")
        if len(parts) > 1:
            k = parts[-1].strip().lower()
            tails[k] = tails.get(k, 0) + 1
    return {k for k, n in tails.items() if n >= max(5, min_share * len(titles))}


def clean_title(t, tails):
    # Giữ đúng cách làm sạch đã hiệu chuẩn 19/10. Đổi cách làm sạch thì cosine đổi: hiệu chuẩn lại với holdout mới.
    t = (t or "").strip()
    parts = SEP.split(t)
    if len(parts) > 1 and parts[-1].strip().lower() in tails:
        t = t[: t.rfind(parts[-1])].rstrip(" |-–—:")
    return re.sub(r"\s+", " ", DATES.sub(" ", t)).strip(" |-–—:")


def stem_of(url):
    host = (urlparse(url).hostname or "").removeprefix("www.")
    return host.split(".")[0]


def topic_text(title, h1, tails):
    t, h = clean_title(title, tails), clean_title(h1, tails)
    if not h or h.lower() == t.lower():
        return t
    return t + "\n" + h if t else h


def load_side(a):
    """Trang site (pages.jsonl của extract.py) và trang đối thủ (competitor_titles.py), đã lọc và có topic_text."""
    rx = re.compile(a.exclude) if a.exclude else None

    def ok(r):
        lang = (r.get("lang") or "").lower()
        return (not (a.lang and lang and not lang.startswith(a.lang)) and "noindex" not in (r.get("robots") or "").lower()
                and not (rx and rx.search(r["url"])) and (r.get("title") or r.get("h1")))

    own = [r for r in jl(a.site_pages) if ok(r) and str(r.get("status", 200)) == "200"]
    comp = {}
    for f in a.competitor:
        for r in jl(f):
            comp[r["url"]] = r  # dòng sau cùng thắng (lượt chạy lại)
    comp = [r for r in comp.values() if r.get("status") == 200 and ok(r)
            and urlparse(r.get("final_url") or r["url"]).hostname == urlparse(r["url"]).hostname]
    for side in (own, *[[r for r in comp if r["site"] == s] for s in sorted({r["site"] for r in comp})]):
        tails = brand_tails([r.get("title") for r in side])
        for r in side:
            h1 = r.get("h1")
            stem = stem_of(r["url"])
            r["text"] = topic_text(r.get("title"), h1[0] if isinstance(h1, list) and h1 else h1, tails)
            r["brand_page"] = bool(stem) and stem in r["text"].lower().replace(" ", "")
    return [r for r in own if r["text"]], [r for r in comp if r["text"]]


TOK = re.compile(r"\w+", re.U)
STOP = set("và của cho là có các những một được trong với để khi như từ này đó thì không bạn cách gì nào bao nhiêu "
           "hướng dẫn top tốt nhất hiện nay mới chi tiết".split())


def toks(t):
    return {w for w in TOK.findall((t or "").lower()) if w not in STOP and not w.isdigit()}


def cmd_gold_sheet(a):
    import random
    own, comp = load_side(a)
    skip = set(Path(a.skip).read_text(encoding="utf-8").split()) if a.skip else set()
    pool = sorted((r for r in comp if r["url"] not in skip), key=lambda r: r["url"])
    by_site = {}
    for r in pool:
        by_site.setdefault(r["site"], []).append(r)
    rnd, pick = random.Random(a.seed), []
    per = max(1, a.n // max(1, len(by_site)))
    for s in sorted(by_site):
        pick += rnd.sample(by_site[s], min(per, len(by_site[s])))
    ot = [(r, toks(r["text"])) for r in own]
    out = []
    for r in pick:
        q = toks(r["text"])
        near = sorted(ot, key=lambda x: -len(q & x[1]) / max(1, len(q)))[:8]
        out.append({"id": r["url"], "site": r["site"], "text": r["text"],
                    "own_lexical_top8": [f"{o['url']} :: {o['text'][:110]}" for o, _ in near], "covered": None})
    write(a.out, out)
    print(f"gold-sheet: {len(out)} trang đối thủ -> {a.out}. Gán covered 0/1 trước khi chạy gap.", file=sys.stderr)


def cmd_gap(a):
    from sklearn.cluster import AgglomerativeClustering
    own, comp = load_side(a)
    if len(own) < 20 or not comp:
        sys.exit(f"thiếu dữ liệu: {len(own)} trang site, {len(comp)} trang đối thủ")
    enc = svi.encoder(a.max_tokens)
    O = svi.mrl(enc.encode([r["text"] for r in own], a.prompt), a.dims)
    V = svi.mrl(enc.encode([r["text"] for r in comp], a.prompt), a.dims)
    S = V @ O.T
    best = S.argmax(1)
    rows = []
    for i, r in enumerate(comp):
        c = float(S[i, best[i]])
        state = ("review" if a.gap is None else "gap" if c < a.gap else
                 "covered" if a.cover is not None and c >= a.cover else "review")
        rows.append({"id": r["url"], "site": r["site"], "text": r["text"], "cos": round(c, 4), "state": state,
                     "brand_page": r.get("brand_page", False),
                     "nearest_own": own[best[i]]["url"], "nearest_own_text": own[best[i]]["text"]})
    gi = [i for i, r in enumerate(rows) if r["state"] == "gap"]
    groups = []
    if len(gi) >= 2:
        # Gom để Claude đọc theo chủ đề: cosine trung bình giữa các trang trong cụm từ --group-cos trở lên.
        ag = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                     distance_threshold=1 - a.group_cos).fit(V[gi])
        for g in sorted(set(ag.labels_)):
            ix = [gi[k] for k in np.flatnonzero(ag.labels_ == g)]
            cen = unit(V[ix].mean(0))
            order = sorted(ix, key=lambda k: -float(V[k] @ cen))
            sites = {}
            for k in ix:
                sites[rows[k]["site"]] = sites.get(rows[k]["site"], 0) + 1
            no = int((O @ cen).argmax())
            groups.append({"group": len(groups), "n": len(ix), "n_sites": len(sites), "sites": sites,
                           "brand_share": round(sum(rows[k]["brand_page"] for k in ix) / len(ix), 2),
                           "titles": [rows[k]["text"].split("\n")[0] for k in order[:6]],
                           "urls": [rows[k]["id"] for k in order[:6]],
                           "nearest_own": own[no]["url"], "nearest_own_cos": round(float(O[no] @ cen), 4)})
            for k in ix:
                rows[k]["group"] = groups[-1]["group"]
    elif len(gi) == 1:
        rows[gi[0]]["group"] = 0
        groups.append({"group": 0, "n": 1, "n_sites": 1, "sites": {rows[gi[0]]["site"]: 1},
                       "brand_share": float(rows[gi[0]]["brand_page"]),
                       "titles": [rows[gi[0]]["text"].split("\n")[0]], "urls": [rows[gi[0]]["id"]],
                       "nearest_own": rows[gi[0]]["nearest_own"], "nearest_own_cos": rows[gi[0]]["cos"]})
    # Cụm toàn trang thương hiệu, case study, tin của chính đối thủ xếp cuối: không phải khoảng trống chủ đề.
    groups.sort(key=lambda g: (g["brand_share"] > 0.5, -g["n_sites"], -g["n"]))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write(out / "gap_pages.jsonl", rows)
    (out / "gap_groups.json").write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding="utf-8")
    cnt = {}
    for r in rows:
        cnt.setdefault(r["site"], {"covered": 0, "review": 0, "gap": 0})[r["state"]] += 1
    L = ["# Khoảng trống chủ đề với đối thủ", "",
         f"Site: {len(own)} trang. Đối thủ: {len(comp)} trang. Embed title + H1 bằng EmbeddingGemma prompt `{a.prompt}`, "
         f"{a.dims} chiều. Ngưỡng: khoảng trống < {a.gap}" + (f", đã có ≥ {a.cover}" if a.cover is not None else
                                                             ", phần còn lại Claude đọc") + ".", "",
         "| Đối thủ | Trang | Site đã có | Claude đọc | Khoảng trống | Lấy mẫu |", "|---|---|---|---|---|---|"]
    tot = {}
    for r in comp:
        tot[r["site"]] = (r.get("sampled"), r.get("sitemap_total"))
    for s, c in sorted(cnt.items()):
        n = sum(c.values())
        smp = tot.get(s, (None, None))
        L.append(f"| {s} | {n} | {c['covered']} | {c['review']} | {c['gap']} | "
                 + (f"{smp[0]}/{smp[1]} URL sitemap" if smp[1] else "—") + " |")
    L += ["", "## Cụm khoảng trống (nhiều đối thủ trước)", "",
          "| Cụm | Trang | Đối thủ | Tiêu đề đại diện | Trang site gần nhất (cos) | Ghi chú |", "|---|---|---|---|---|---|"]
    for g in groups:
        L.append(f"| G{g['group']} | {g['n']} | {', '.join(f'{k} {v}' for k, v in g['sites'].items())} | "
                 + " · ".join(t[:60] for t in g["titles"][:3]) + f" | {g['nearest_own']} ({g['nearest_own_cos']}) | "
                 + ("trang thương hiệu, case study của đối thủ" if g["brand_share"] > 0.5 else "") + " |")
    L += ["", "## Đọc kết quả", "",
          "- Claude đọc từng cụm và mọi trang `review` trước khi đề xuất bài mới. Cụm có 2 đối thủ trở lên là ứng viên mạnh hơn.",
          "- Bỏ cụm ngoài định vị và ngoài mảng kinh doanh của site (tin tuyển dụng, sự kiện, chủ đề của entity khác).",
          "- Bài mới đề xuất từ cụm: gán vào bản đồ chủ đề bằng lệnh `plan`, kiểm SERP trước khi viết.",
          "- Chỉ số mô phỏng. Một trang đối thủ không có trang tương ứng chưa chứng minh chủ đề đó có traffic."]
    (out / "gap_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"gap: {len(comp)} trang đối thủ, {len(gi)} khoảng trống, {len(groups)} cụm -> {out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map")
    m.add_argument("--store", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--pages", default=None, help="pages.jsonl của extract.py: lang, robots, canonical")
    m.add_argument("--lang", default=None, help="tiền tố mã ngôn ngữ, ví dụ vi")
    m.add_argument("--exclude", default=None, help="regex URL loại khỏi scope, ví dụ /en/")
    m.add_argument("--min-words", type=int, default=300)
    m.add_argument("--core", default=None, help="file URL trang lõi (dịch vụ, trang chủ), mỗi dòng một URL")
    m.add_argument("--k", default="auto")
    m.add_argument("--dims", type=int, default=768, choices=(768, 512, 256, 128))
    m.add_argument("--outlier-pct", type=float, default=10)
    m.add_argument("--metrics", default=None, help='jsonl {"url", "impressions", "clicks"} từ GSC chiều page')
    m.add_argument("--proof", default=None, help="regex URL trang bằng chứng: case study, tác giả, giới thiệu")
    m.add_argument("--names", default=None, help='json {"<số cụm>": "tên"} do Claude đặt sau lượt chạy đầu')
    p = sub.add_parser("plan")
    p.add_argument("--map", required=True)
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-tokens", type=int, default=512)
    t = sub.add_parser("selftest")
    t.add_argument("--map", required=True)
    t.add_argument("--pages", required=True, help="pages.jsonl của extract.py: title, h2")
    t.add_argument("--target", type=float, default=0.95)
    t.add_argument("--max-tokens", type=int, default=512)
    for name in ("gap", "gold-sheet"):
        g = sub.add_parser(name)
        g.add_argument("--site-pages", required=True, help="pages.jsonl của extract.py (url, title, h1, lang, robots)")
        g.add_argument("--competitor", action="append", required=True, help="jsonl của competitor_titles.py")
        g.add_argument("--lang", default="vi")
        g.add_argument("--exclude", default=r"/en/")
        if name == "gap":
            g.add_argument("--out", required=True)
            g.add_argument("--prompt", default="Document")
            g.add_argument("--dims", type=int, default=768, choices=(768, 512, 256, 128))
            g.add_argument("--gap", type=float, default=None, help="cosine dưới ngưỡng này: khoảng trống (registry)")
            g.add_argument("--cover", type=float, default=None, help="cosine từ ngưỡng này: site đã có (registry)")
            g.add_argument("--group-cos", type=float, default=0.83, help="độ giống tối thiểu khi gom trang khoảng trống")
            g.add_argument("--max-tokens", type=int, default=128)
        else:
            g.add_argument("--n", type=int, default=60)
            g.add_argument("--seed", type=int, default=19)
            g.add_argument("--skip", default=None, help="file id đã gán (dev) để lấy holdout mới")
            g.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "map" and a.lang:
        a.lang = a.lang.lower()
    if a.cmd == "gap" and a.cover is not None and (a.gap is None or a.gap > a.cover):
        sys.exit("--cover cần --gap nhỏ hơn hoặc bằng nó")
    {"map": cmd_map, "plan": cmd_plan, "selftest": cmd_selftest, "gap": cmd_gap, "gold-sheet": cmd_gold_sheet}[a.cmd](a)


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
