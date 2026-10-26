#!/usr/bin/env python3
"""geo-fanout-research: đo mức phủ của từng subquery theo section bằng EmbeddingGemma 2 (local).

Chạy bằng venv embedding: <venv>/bin/python -B -I fanout_cover.py <lệnh> ...
  cover --store DIR --subq subq.jsonl --pools pools.jsonl --out rows.jsonl [--detail detail.jsonl]
        [--grid 0.55:0.80:0.025] [--level passage]
        subq:  {"id", "query_id", "text", "lens"?}  (subquery fan-out của một prompt)
        pools: {"id", "text", "candidates": [url...], "labels": {url: số}?}  (cùng định dạng query của retrieval-lab)
        Mỗi (prompt, url): best cos của từng subquery trên passage của url (SearchQuery→Document),
        mean_best, min_best, share_ge_<t> (tỉ lệ subquery có best cos ≥ t), prompt_cos (prompt gốc), cited (0/1).
        detail: mỗi (prompt, url, subquery) một dòng: best_cos, heading của section thắng, best_item.
  gaps  --detail detail.jsonl --query-id Q --url U [--cover-at T] [--out gaps.md]
        Bảng subquery × section thắng của một trang, xếp cos thấp lên đầu.
        Có --cover-at (ngưỡng đã hiệu chuẩn trong registry): verdict COVERED / GAP.
        Không có: verdict "chưa hiệu chuẩn, Claude đọc".
  md-rows  --variant A=a.md --variant B=b.md --out rows.jsonl
        Tách bản nháp markdown thành dòng cho svi.py build: page (H1 + đoạn mở), passage theo đoạn dưới mỗi H2.
        URL của bản là "variant://<tên>". Dùng cho skill geo-variant-simulation.
  variants --ranks ranks.jsonl [--decide-at M] [--out variants.json]
        Đọc output "retrieval.py rank" (query = subquery, candidates = URL các bản). Mỗi bản: cos trung bình
        trên các subquery, số subquery thắng. margin = bản đầu − bản nhì. margin ≥ M: "mô phỏng phân định".
        Không có M trong registry: "chưa hiệu chuẩn, Claude đọc 6 trục".
Ngưỡng cosine không dùng chung giữa site: đọc registry của skill model-calibration.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # import svi từ skill khác: không sinh __pycache__ ở thư mục đó

HERE = Path(__file__).resolve()
SVI = HERE.parents[2] / "site-vector-index" / "scripts"


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def parse_grid(spec):
    lo, hi, step = (float(x) for x in spec.split(":"))
    n = int(round((hi - lo) / step)) + 1
    return [round(lo + i * step, 4) for i in range(n)]


def tkey(t):
    return f"share_ge_{t:.3f}".replace(".", "_")


def aggregate(best, grid):
    """best: list cos tốt nhất của từng subquery trên một trang. Trả các chỉ số mức phủ của trang."""
    out = {"n_subq": len(best), "mean_best": round(sum(best) / len(best), 4), "min_best": round(min(best), 4)}
    for t in grid:
        out[tkey(t)] = round(sum(b >= t for b in best) / len(best), 4)
    return out


def cmd_cover(a):
    sys.path.insert(0, str(SVI))
    import numpy as np
    import svi  # noqa: E402  (cùng bộ skill; Store, encoder)

    st = svi.Store(a.store)
    if not st.items:
        sys.exit("store rỗng")
    enc_name = svi.MODEL if os.environ.get("SVI_FAKE") != "1" else "fake"
    if st.manifest.get("model") != enc_name:
        sys.exit(f"store dùng {st.manifest.get('model')}, encoder là {enc_name}")
    grid = parse_grid(a.grid)
    pools = {p["id"]: p for p in jl(a.pools)}
    subq = jl(a.subq)
    by_q = {}
    for s in subq:
        if s["query_id"] not in pools:
            sys.exit(f"subquery {s['id']}: không có prompt {s['query_id']} trong pools")
        by_q.setdefault(s["query_id"], []).append(s)
    idx = {}
    for i, it in enumerate(st.items):
        if it["level"] == a.level:
            idx.setdefault(it["url"], []).append(i)
    enc = svi.encoder(a.max_tokens)
    qids = [q for q in pools if q in by_q]
    sv = enc.encode([s["text"] for q in qids for s in by_q[q]], "SearchQuery")
    pv = enc.encode([pools[q]["text"] for q in qids], "SearchQuery")
    rows, detail, k = [], [], 0
    for qi, q in enumerate(qids):
        p, ss = pools[q], by_q[q]
        V = sv[k:k + len(ss)]
        k += len(ss)
        labels = p.get("labels") or {}
        for u in p.get("candidates") or list(idx):
            ii = idx.get(u)
            if not ii:
                continue
            S = st.vec[ii].astype(np.float32) @ V.T  # passage × subquery
            j = S.argmax(axis=0)
            best = [float(S[j[c], c]) for c in range(len(ss))]
            prompt_cos = float((st.vec[ii].astype(np.float32) @ pv[qi]).max())
            rows.append({"query_id": q, "group": p.get("group"), "url": u, **aggregate(best, grid),
                         "prompt_cos": round(prompt_cos, 4), "label": labels.get(u, 0),
                         "cited": int(labels.get(u, 0) > 0), "n_passages": len(ii)})
            for c, s in enumerate(ss):
                it = st.items[ii[j[c]]]
                detail.append({"query_id": q, "url": u, "subq_id": s["id"], "lens": s.get("lens"), "subq": s["text"],
                               "best_cos": round(best[c], 4), "heading": it.get("meta", {}).get("heading", ""),
                               "section_index": it.get("meta", {}).get("section_index"), "best_item": it["id"],
                               "cited": int(labels.get(u, 0) > 0)})
    write(a.out, rows)
    if a.detail:
        write(a.detail, detail)
    print(f"cover: {len(qids)} prompt, {len(subq)} subquery, {len(rows)} cặp prompt × trang -> {a.out}", file=sys.stderr)


def cmd_gaps(a):
    allq = [r for r in jl(a.detail) if r["query_id"] == a.query_id]
    rows = [r for r in allq if r["url"] == a.url]
    if not rows:
        sys.exit(f"không có dòng cho {a.query_id} × {a.url}")
    pool_best = {}
    for r in allq:
        if r["url"] != a.url and r["best_cos"] > pool_best.get(r["subq_id"], ("", -1.0))[1]:
            pool_best[r["subq_id"]] = (r["url"], r["best_cos"])
    rows.sort(key=lambda r: r["best_cos"])
    note = (f"ngưỡng phủ {a.cover_at} (registry)" if a.cover_at is not None
            else "chưa hiệu chuẩn, Claude đọc từng dòng")
    out = [f"# Mức phủ subquery — {a.query_id} × {a.url}", "", f"> Verdict: {note}. Cos thấp xếp trước.", "",
           "| Subquery | Lens | Section thắng | Cos | Trang khác tốt nhất (cos) | Verdict |", "|---|---|---|---|---|---|"]
    for r in rows:
        v = ("COVERED" if r["best_cos"] >= a.cover_at else "GAP") if a.cover_at is not None else "Claude đọc"
        pb = pool_best.get(r["subq_id"])
        pbs = f"{pb[0]} ({pb[1]:.4f})" if pb else "-"
        out.append(f"| {r['subq']} | {r.get('lens') or ''} | {r['heading'] or '(không heading)'} | {r['best_cos']:.4f} | {pbs} | {v} |")
    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def md_rows(name, text, min_words=25):
    """Bản nháp markdown → dòng page + passage. Đoạn ngắn hơn min_words gộp với đoạn sau trong cùng H2."""
    url = f"variant://{name}"
    h1, intro, sec, rows, buf = "", "", -1, [], []
    heading = ""

    def flush():
        if buf:
            body = " ".join(buf)
            rows.append({"id": f"{url}#s{max(sec, 0)}p{len([r for r in rows if r['level'] == 'passage'])}",
                         "level": "passage", "url": url, "text": f"{heading}: {body}" if heading else body,
                         "meta": {"heading": heading, "section_index": max(sec, 0), "words": len(body.split())}})
            buf.clear()

    for block in [b.strip() for b in text.replace("\r", "").split("\n\n") if b.strip()]:
        first = block.splitlines()[0]
        if first.startswith("# "):
            h1 = first[2:].strip()
            block = "\n".join(block.splitlines()[1:]).strip()
            if not block:
                continue
        elif first.startswith("## "):
            flush()
            sec, heading = sec + 1, first[3:].strip()
            block = "\n".join(block.splitlines()[1:]).strip()
            if not block:
                continue
        body = " ".join(l.lstrip("-*0123456789.|> #").strip() for l in block.splitlines() if l.strip())
        if not intro and sec < 0:
            intro = body
        buf.append(body)
        if len(" ".join(buf).split()) >= min_words:
            flush()
    flush()
    page = {"id": f"{url}#page", "level": "page", "url": url, "text": " | ".join(x for x in (h1, intro) if x),
            "meta": {"h1": h1}}
    return [page] + rows


def cmd_md_rows(a):
    out = []
    for spec in a.variant:
        name, path = spec.split("=", 1)
        out += md_rows(name, Path(path).read_text(encoding="utf-8"))
    write(a.out, out)
    print(f"md-rows: {len(a.variant)} bản, {len(out)} dòng -> {a.out}", file=sys.stderr)


def cmd_variants(a):
    ranks = jl(a.ranks)
    score, wins = {}, {}
    for r in ranks:
        for u in r["urls"]:
            score.setdefault(u["url"], []).append(u["cos"])
        if r["urls"]:
            top = max(r["urls"], key=lambda u: u["cos"])["url"]
            wins[top] = wins.get(top, 0) + 1
    n = len(ranks)
    table = sorted(({"url": u, "mean_cos": round(sum(v) / len(v), 4), "n_subq": len(v), "wins": wins.get(u, 0)}
                    for u, v in score.items()), key=lambda x: -x["mean_cos"])
    if len(table) < 2:
        sys.exit("cần ít nhất 2 bản")
    if any(t["n_subq"] != n for t in table):
        sys.exit("có bản thiếu điểm ở một số subquery: kiểm candidates và store")
    margin = round(table[0]["mean_cos"] - table[1]["mean_cos"], 4)
    if a.decide_at is None:
        verdict = "chưa hiệu chuẩn, Claude đọc 6 trục"
    elif margin >= a.decide_at:
        verdict = f"mô phỏng phân định: {table[0]['url']} (margin {margin} ≥ {a.decide_at})"
    else:
        verdict = f"không phân định (margin {margin} < {a.decide_at}): Claude đọc 6 trục"
    rep = {"n_subq": n, "margin": margin, "decide_at": a.decide_at, "verdict": verdict, "variants": table}
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cover")
    c.add_argument("--store", required=True)
    c.add_argument("--subq", required=True)
    c.add_argument("--pools", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--detail", default=None)
    c.add_argument("--grid", default="0.55:0.80:0.025")
    c.add_argument("--level", default="passage")
    c.add_argument("--max-tokens", type=int, default=256)
    g = sub.add_parser("gaps")
    g.add_argument("--detail", required=True)
    g.add_argument("--query-id", required=True)
    g.add_argument("--url", required=True)
    g.add_argument("--cover-at", type=float, default=None)
    g.add_argument("--out", default=None)
    m = sub.add_parser("md-rows")
    m.add_argument("--variant", action="append", required=True, help="tên=đường dẫn .md, lặp cho mỗi bản")
    m.add_argument("--out", required=True)
    v = sub.add_parser("variants")
    v.add_argument("--ranks", required=True)
    v.add_argument("--decide-at", type=float, default=None)
    v.add_argument("--out", default=None)
    a = ap.parse_args()
    {"cover": cmd_cover, "gaps": cmd_gaps, "md-rows": cmd_md_rows, "variants": cmd_variants}[a.cmd](a)


if __name__ == "__main__":
    main()
