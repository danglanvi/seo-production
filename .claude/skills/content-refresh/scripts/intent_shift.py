#!/usr/bin/env python3
"""content-refresh: đo intent dịch chuyển bằng EmbeddingGemma 2 (local).
So tâm vector của top N SERP hiện tại với vector trang mình cho cùng truy vấn.

Chạy bằng venv embedding: <venv>/bin/python -B -I intent_shift.py --serp serp.jsonl --pages pages.jsonl --out shift.jsonl
  serp:  {"query", "date"?, "results": [{"pos", "url", "title", "snippet"}]}   (top 10 hữu cơ)
  pages: {"query", "url", "title", "meta"}   (trang mình đang nhận truy vấn đó, ví dụ URL có lượt hiển thị lớn nhất trong GSC)
  [--top 3] [--exclude-own] [--chars 300] [--rewrite-at D]
Mỗi truy vấn: cos(trang, tâm top N), spread = cos trung bình của từng kết quả top N với tâm,
drift = spread − cos(trang, tâm). drift lớn: trang đứng xa intent mà top N đang thống nhất.
Văn bản so là "title | snippet" (kết quả SERP) và "title | meta" (trang mình), cùng prompt Document.
--rewrite-at chỉ truyền khi registry có ngưỡng đã hiệu chuẩn. Không có thì verdict "chưa hiệu chuẩn, Claude đọc top N".
"""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.dont_write_bytecode = True  # import svi từ skill khác: không sinh __pycache__ ở thư mục đó

HERE = Path(__file__).resolve()
SVI = HERE.parents[2] / "site-vector-index" / "scripts"


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def host(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def card(title, body, chars):
    return " | ".join(x for x in ((title or "").strip(), " ".join((body or "").split())[:chars]) if x)


def shift(own, tops):
    """own: vector trang (chuẩn hoá). tops: list vector top N (chuẩn hoá). Trả (cos_centroid, spread, drift)."""
    import numpy as np
    T = np.asarray(tops, dtype=np.float32)
    c = T.mean(axis=0)
    c = c / np.linalg.norm(c)
    cos = float(np.asarray(own, dtype=np.float32) @ c)
    spread = float((T @ c).mean())
    return round(cos, 4), round(spread, 4), round(spread - cos, 4)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serp", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--exclude-own", action="store_true", help="bỏ kết quả cùng domain với trang mình khỏi top N")
    ap.add_argument("--chars", type=int, default=300)
    ap.add_argument("--rewrite-at", type=float, default=None)
    ap.add_argument("--max-tokens", type=int, default=256)
    a = ap.parse_args()
    sys.path.insert(0, str(SVI))
    import svi  # noqa: E402

    serp = {r["query"]: r for r in jl(a.serp)}
    pages = jl(a.pages)
    jobs = []
    for p in pages:
        s = serp.get(p["query"])
        if not s:
            print(f"bỏ qua {p['query']}: không có SERP", file=sys.stderr)
            continue
        res = sorted(s["results"], key=lambda r: r.get("pos", 99))
        if a.exclude_own:
            res = [r for r in res if host(r["url"]) != host(p["url"])]
        res = res[:a.top]
        if len(res) < a.top:
            print(f"bỏ qua {p['query']}: SERP thiếu kết quả", file=sys.stderr)
            continue
        jobs.append((p, s, res))
    texts = []
    for p, _, res in jobs:
        texts.append(card(p.get("title"), p.get("meta"), a.chars))
        texts += [card(r.get("title"), r.get("snippet"), a.chars) for r in res]
    vec = svi.encoder(a.max_tokens).encode(texts, "Document")
    out, k = [], 0
    for p, s, res in jobs:
        own, tops = vec[k], vec[k + 1:k + 1 + len(res)]
        k += 1 + len(res)
        cos, spread, drift = shift(own, tops)
        if a.rewrite_at is None:
            verdict = f"chưa hiệu chuẩn, Claude đọc top {a.top}"
        else:
            verdict = "intent dịch chuyển: cân nhắc REWRITE" if drift >= a.rewrite_at else "intent giữ: refresh"
        out.append({"query": p["query"], "url": p["url"], "serp_date": s.get("date"), "cos_centroid": cos,
                    "spread": spread, "drift": drift, "top": [r["url"] for r in res], "verdict": verdict,
                    **{k2: p[k2] for k2 in ("impressions", "position") if k2 in p}})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    enc = "fake" if os.environ.get("SVI_FAKE") == "1" else svi.MODEL
    print(f"intent_shift: {len(out)} truy vấn, top {a.top}, encoder {enc} -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
