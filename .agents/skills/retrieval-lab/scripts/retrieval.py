#!/usr/bin/env python3
"""retrieval-lab: mô phỏng truy xuất dense trên site vector index (EmbeddingGemma 2, local).

Chạy bằng venv embedding: <venv>/bin/python -I retrieval.py <lệnh> ...
  rank      --store DIR --in queries.jsonl --out ranks.jsonl [--level passage] [--k 20]
            queries: {"id", "text", "candidates": [url...]?, "labels": {url: số}?, "group"?}
            Mỗi query: điểm từng URL = max cosine (SearchQuery→Document) trên passage của URL đó, kèm passage thắng,
            hạng, khoảng cách tới URL đứng đầu. Có candidates thì chỉ xếp trong tập đó.
  validate  --ranks ranks.jsonl --out report.json [--metric cos|rank]
            Cần labels. AUC từng query (URL có nhãn > 0 so với URL nhãn 0), trung bình theo query, bootstrap CI 95%.
  route     --store DIR --in queries.jsonl --out routing.jsonl [--level page|passage]
            Định tuyến query → URL: URL Gemma chọn so với "chosen" (URL Google đang chọn, ghi trong query).
            "candidates" trong query giới hạn tập trang, ví dụ chỉ trang cùng ngôn ngữ với query.
Ngưỡng cosine không dùng chung giữa site: đọc registry của skill model-calibration.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
SVI = HERE.parents[2] / "site-vector-index" / "scripts"
sys.path.insert(0, str(SVI))
import svi  # noqa: E402  (cùng bộ skill; Store, encoder)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def url_scores(st, idx_by_url, qv, urls):
    """Điểm mỗi URL = max cosine trên các item của URL. Trả list (url, cos, item_id) giảm dần."""
    out = []
    for u in urls:
        idx = idx_by_url.get(u)
        if idx is None or not len(idx):
            continue
        s = st.vec[idx].astype(np.float32) @ qv
        j = int(np.argmax(s))
        out.append((u, float(s[j]), st.items[idx[j]]["id"]))
    out.sort(key=lambda x: -x[1])
    return out


def index_by_url(st, level):
    d = {}
    for i, it in enumerate(st.items):
        if it["level"] == level:
            d.setdefault(it["url"], []).append(i)
    return {u: np.asarray(v) for u, v in d.items()}


def load(a):
    st = svi.Store(a.store)
    if not st.items:
        sys.exit("store rỗng")
    qs = jl(a.inp)
    enc_name = svi.MODEL if os.environ.get("SVI_FAKE") != "1" else "fake"
    if st.manifest.get("model") != enc_name:
        sys.exit(f"store dùng {st.manifest.get('model')}, encoder là {enc_name}")
    qv = svi.encoder(a.max_tokens).encode([q["text"] for q in qs], "SearchQuery")
    return st, qs, qv


def cmd_rank(a):
    st, qs, qv = load(a)
    by_url = index_by_url(st, a.level)
    out = []
    for q, v in zip(qs, qv):
        urls = q.get("candidates") or list(by_url)
        sc = url_scores(st, by_url, v, urls)
        missing = [u for u in (q.get("candidates") or []) if u not in by_url]
        top = sc[0][1] if sc else None
        rows = [{"url": u, "cos": round(c, 4), "rank": r + 1, "gap_to_top": round(top - c, 4), "best_item": i,
                 "label": (q.get("labels") or {}).get(u, 0)} for r, (u, c, i) in enumerate(sc[:a.k] if not q.get("candidates") else sc)]
        out.append({"id": q["id"], "group": q.get("group"), "text": q["text"], "n_candidates": len(sc),
                    "missing": missing, "urls": rows})
    write(a.out, out)
    print(f"rank: {len(out)} query -> {a.out}", file=sys.stderr)


def auc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def cmd_validate(a):
    rows = jl(a.ranks)
    per = []
    for r in rows:
        key = "cos" if a.metric == "cos" else "rank"
        sign = 1 if key == "cos" else -1
        pos = [sign * u[key] for u in r["urls"] if u["label"] > 0]
        neg = [sign * u[key] for u in r["urls"] if u["label"] == 0]
        v = auc(pos, neg)
        if v is not None:
            per.append({"id": r["id"], "group": r.get("group"), "auc": round(v, 3), "n_pos": len(pos), "n_neg": len(neg)})
    if len(per) < 5:
        sys.exit(f"chỉ {len(per)} query có cả URL dương và âm")
    vals = np.asarray([p["auc"] for p in per])
    rng = np.random.default_rng(7)
    boots = [float(vals[rng.integers(0, len(vals), len(vals))].mean()) for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    groups = {}
    for p in per:
        groups.setdefault(p["group"] or "-", []).append(p["auc"])
    rep = {"metric": a.metric, "n_queries": len(per), "mean_auc": round(float(vals.mean()), 3),
           "ci95": [round(float(lo), 3), round(float(hi), 3)],
           "share_auc_gt_05": round(float((vals > 0.5).mean()), 3),
           "by_group": {g: {"n": len(v), "mean_auc": round(float(np.mean(v)), 3)} for g, v in groups.items()},
           "verdict": ("proxy có tín hiệu (CI trên 0,5)" if lo > 0.5 else
                       "ngược chiều (CI dưới 0,5): kiểm cách chọn mẫu, ví dụ nhãn dương đến từ query khác" if hi < 0.5 else
                       "chưa chứng minh (CI chứa 0,5)"),
           "per_query": per}
    Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"validate: AUC {rep['mean_auc']} CI {rep['ci95']} -> {rep['verdict']}", file=sys.stderr)


def cmd_route(a):
    st, qs, qv = load(a)
    by_url = index_by_url(st, a.level)
    out = []
    for q, v in zip(qs, qv):
        # candidates: giới hạn trang cùng ngôn ngữ hoặc cùng cụm; không có thì xếp toàn site
        sc = url_scores(st, by_url, v, q.get("candidates") or list(by_url))
        rank_of = {u: r + 1 for r, (u, _, _) in enumerate(sc)}
        cos_of = {u: c for u, c, _ in sc}
        ch = q.get("chosen")
        out.append({"id": q["id"], "text": q["text"], "group": q.get("group"), "chosen": ch,
                    "gemma_top": sc[0][0], "gemma_top_cos": round(sc[0][1], 4),
                    "gemma_top3": [u for u, _, _ in sc[:3]],
                    "chosen_rank": rank_of.get(ch), "chosen_cos": round(cos_of[ch], 4) if ch in cos_of else None,
                    "margin": round(sc[0][1] - cos_of[ch], 4) if ch in cos_of else None,
                    "agree_top1": sc[0][0] == ch, **{k: q[k] for k in ("impr", "clicks", "pos", "share", "n_urls") if k in q}})
    write(a.out, out)
    have = [r for r in out if r["chosen_rank"]]
    print(f"route: {len(out)} query; top1 khớp {sum(r['agree_top1'] for r in have)}/{len(have)}; "
          f"top3 khớp {sum(1 for r in have if r['chosen_rank'] <= 3)}/{len(have)} -> {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rank")
    ro = sub.add_parser("route")
    for x in (r, ro):
        x.add_argument("--store", required=True)
        x.add_argument("--in", dest="inp", required=True)
        x.add_argument("--out", required=True)
        x.add_argument("--max-tokens", type=int, default=256)
    r.add_argument("--level", default="passage")
    r.add_argument("--k", type=int, default=20)
    ro.add_argument("--level", default="page")
    v = sub.add_parser("validate")
    v.add_argument("--ranks", required=True)
    v.add_argument("--out", required=True)
    v.add_argument("--metric", choices=("cos", "rank"), default="cos")
    a = ap.parse_args()
    {"rank": cmd_rank, "validate": cmd_validate, "route": cmd_route}[a.cmd](a)


if __name__ == "__main__":
    main()
