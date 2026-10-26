#!/usr/bin/env python3
"""So khớp và gom nhóm bằng EmbeddingGemma 2 chạy local (dữ liệu không rời máy).

Chạy bằng venv có sentence-transformers, torch, scikit-learn: <venv>/bin/python -I emb.py <lệnh> ...
Thiết bị: Apple GPU (mps) nếu có, nếu không thì CPU (chậm hơn nhiều).
  nn       --query q.jsonl --docs d.jsonl --k 5 --out out.jsonl   (mỗi dòng {"id", "text"})
  cluster  --in x.jsonl --threshold 0.85 --out out.jsonl
Prompt mặc định: nn dùng SearchQuery/Document; so mã với mã thì đặt cả hai là SentenceSimilarity.
Cosine của model này chưa có ngưỡng chung: hiệu chuẩn bằng mẫu âm/dương thật trước khi đặt ngưỡng.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Model đã có sẵn trong cache máy. Không gọi Hugging Face, vì lần gọi mạng có thể treo không báo lỗi (17/10/2026).
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def load_model(max_tokens):
    import torch
    from sentence_transformers import SentenceTransformer
    mps = torch.backends.mps.is_available()
    m = SentenceTransformer("google/embeddinggemma-2", device="mps" if mps else "cpu",
                            model_kwargs={"torch_dtype": torch.bfloat16 if mps else torch.float32},
                            config_kwargs={"vision_config": None, "audio_config": None})
    m.max_seq_length = max_tokens
    return m


def read(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def encode(model, rows, prompt):
    v = model.encode([r["text"] for r in rows], prompt_name=prompt, batch_size=16,
                     normalize_embeddings=True, convert_to_numpy=True)
    return np.asarray(v, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    nn = sub.add_parser("nn")
    nn.add_argument("--query", required=True)
    nn.add_argument("--docs", required=True)
    nn.add_argument("--k", type=int, default=5)
    nn.add_argument("--qprompt", default="SearchQuery")
    nn.add_argument("--dprompt", default="Document")
    cl = sub.add_parser("cluster")
    cl.add_argument("--in", dest="inp", required=True)
    cl.add_argument("--threshold", type=float, required=True, help="cosine tối thiểu để chung nhóm")
    cl.add_argument("--prompt", default="Clustering")
    for p in (nn, cl):
        p.add_argument("--out", required=True, type=Path)
        p.add_argument("--max-tokens", type=int, default=1024)
    args = ap.parse_args()

    t = time.time()
    model = load_model(args.max_tokens)
    out = []
    if args.cmd == "nn":
        q, d = read(args.query), read(args.docs)
        sims = encode(model, q, args.qprompt) @ encode(model, d, args.dprompt).T
        for i, row in enumerate(q):
            top = np.argsort(-sims[i])[:args.k]
            out.append({"id": row["id"], "max_cos": round(float(sims[i, top[0]]), 4),
                        "top": [{"id": d[j]["id"], "cos": round(float(sims[i, j]), 4)} for j in top]})
    else:
        from sklearn.cluster import AgglomerativeClustering
        rows = read(args.inp)
        v = encode(model, rows, args.prompt)
        labels = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                         distance_threshold=1 - args.threshold).fit_predict(v)
        sizes = np.bincount(labels)
        out = [{"id": r["id"], "cluster": int(c), "cluster_size": int(sizes[c])} for r, c in zip(rows, labels)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(f"{args.cmd}: {len(out)} dòng trong {time.time() - t:.1f}s -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
