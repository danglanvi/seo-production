#!/usr/bin/env python3
"""Site vector index: embed trang, section, passage, anchor của một site bằng EmbeddingGemma 2 (local), dùng lại cho mọi skill.

Chạy bằng venv có sentence-transformers + torch: <venv>/bin/python -I svi.py <lệnh> ...
  build    --store DIR --in rows.jsonl [--mode upsert|replace] [--prompt Document]
  query    --store DIR --in q.jsonl --k 10 [--level passage] [--per-url] [--coarse 128 --pool 300] --out out.jsonl
  cross    --store A --against B [--level section] [--against-level passage] --k 3 --out out.jsonl
  centroid --store DIR --level page [--group folder|meta.<field>] [--weight meta.<field>] --out out.jsonl
  pairs    --store DIR --level section --min 0.92 [--cross-url] [--same meta.<field>] --out out.jsonl
  stats    --store DIR

Dòng input của build: {"id", "level", "url", "text", "meta": {...}}. id phải duy nhất trong store.
Dòng input của query: {"id", "text", "filter": {"level", "url_prefix", "urls": [...]}} (filter tuỳ chọn).
Mỗi vector chuẩn hoá L2, lưu float16. MRL: 128 chiều đầu, chuẩn hoá lại, dùng để lọc thô store lớn.
Cosine phụ thuộc cặp prompt (SearchQuery-Document khác Document-Document): hiệu chuẩn ngưỡng theo skill model-calibration.
SVI_FAKE=1: encoder giả, tất định, chỉ dùng cho test offline.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

MODEL = "google/embeddinggemma-2"
DIM = 768
LEVELS = ("page", "section", "passage", "anchor", "image", "query", "other")


# ---------- encoder ----------

class FakeEncoder:
    """Vector giả theo hash của chữ: cùng chữ thì cùng vector. Chỉ để test logic store."""
    name = "fake"

    def encode(self, texts, prompt):
        out = np.zeros((len(texts), DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            seed = int(hashlib.sha1((prompt + "\n" + t).encode()).hexdigest()[:8], 16)
            out[i] = np.random.default_rng(seed).standard_normal(DIM)
        return out / np.linalg.norm(out, axis=1, keepdims=True)


class GemmaEncoder:
    name = MODEL

    def __init__(self, max_tokens):
        import torch
        from sentence_transformers import SentenceTransformer
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        # bfloat16: float16 cho NaN với model này (đo 15/10/2026). Text-only: tắt nhánh ảnh, audio.
        self.m = SentenceTransformer(MODEL, device=device, model_kwargs={"torch_dtype": torch.bfloat16},
                                     config_kwargs={"vision_config": None, "audio_config": None})
        self.m.max_seq_length = max_tokens

    def encode(self, texts, prompt):
        v = self.m.encode(texts, prompt_name=prompt, batch_size=16, normalize_embeddings=True,
                          convert_to_numpy=True, show_progress_bar=False)
        return np.asarray(v, dtype=np.float32)


def encoder(max_tokens):
    return FakeEncoder() if os.environ.get("SVI_FAKE") == "1" else GemmaEncoder(max_tokens)


# ---------- store ----------

def read_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def text_hash(prompt, text):
    return hashlib.sha1((prompt + "\n" + text).encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.manifest = {}
        self.items = []
        self.vec = np.zeros((0, DIM), dtype=np.float16)
        if (self.path / "manifest.json").exists():
            self.manifest = json.loads((self.path / "manifest.json").read_text(encoding="utf-8"))
            self.items = read_jsonl(self.path / "items.jsonl")
            self.vec = np.load(self.path / "vec.npy")
            if len(self.items) != len(self.vec):
                sys.exit(f"store hỏng: {len(self.items)} item nhưng {len(self.vec)} vector")

    def save(self, enc_name):
        self.path.mkdir(parents=True, exist_ok=True)
        counts = {}
        for it in self.items:
            counts[it["level"]] = counts.get(it["level"], 0) + 1
        self.manifest.update({"model": enc_name, "dim": DIM, "dtype": "float16", "normalized": True,
                              "updated": time.strftime("%Y-%m-%d %H:%M"), "count": len(self.items),
                              "levels": counts})
        write_jsonl(self.path / "items.jsonl", self.items)
        np.save(self.path / "vec.npy", self.vec.astype(np.float16))
        (self.path / "manifest.json").write_text(json.dumps(self.manifest, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")

    def mask(self, level=None, url_prefix=None, urls=None):
        m = np.ones(len(self.items), dtype=bool)
        for i, it in enumerate(self.items):
            if level and it["level"] != level:
                m[i] = False
            elif url_prefix and not it["url"].startswith(url_prefix):
                m[i] = False
            elif urls and it["url"] not in urls:
                m[i] = False
        return m


def check_model(store, enc_name):
    old = store.manifest.get("model")
    if old and old != enc_name:
        sys.exit(f"store dùng model {old}, lượt này dùng {enc_name}: không trộn vector của 2 model")


def cmd_build(a):
    rows = read_jsonl(a.inp)
    if a.levels:
        rows = [r for r in rows if r.get("level") in a.levels.split(",")]
    bad = [r.get("id") for r in rows if not r.get("id") or r.get("level") not in LEVELS or not (r.get("text") or "").strip()]
    if bad:
        sys.exit(f"{len(bad)} dòng thiếu id, level hợp lệ hoặc text: {bad[:5]}")
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        sys.exit("id trùng trong input")
    st = Store(a.store)
    enc_name = MODEL if os.environ.get("SVI_FAKE") != "1" else "fake"
    check_model(st, enc_name)
    old = {it["id"]: (i, it) for i, it in enumerate(st.items)}
    if a.mode == "replace":
        # Trang trong input thay toàn bộ item cũ của URL đó (passage bị xoá trên site thì xoá khỏi store).
        urls = {r["url"] for r in rows}
        keep = [i for i, it in enumerate(st.items) if it["url"] not in urls]
    else:
        keep = [i for i, it in enumerate(st.items) if it["id"] not in set(ids)]
    new_items, new_vec, todo = [], [], []
    for r in rows:
        h = text_hash(a.prompt, r["text"])
        prev = old.get(r["id"])
        item = {"id": r["id"], "level": r["level"], "url": r["url"], "hash": h, "prompt": a.prompt,
                "chars": len(r["text"]), "meta": r.get("meta") or {}}
        if a.keep_text:
            item["text"] = r["text"]
        if prev and prev[1]["hash"] == h:
            new_vec.append(st.vec[prev[0]].astype(np.float32))
        else:
            new_vec.append(None)
            todo.append((len(new_items), r["text"]))
        new_items.append(item)
    t = time.time()
    if todo:
        enc = encoder(a.max_tokens)
        todo.sort(key=lambda x: len(x[1]))  # lô gần cùng độ dài: ít padding, log tiến độ đều
        for s in range(0, len(todo), 512):
            part = todo[s:s + 512]
            for (pos, _), v in zip(part, enc.encode([x[1] for x in part], a.prompt)):
                new_vec[pos] = v
            print(f"build: {min(s + 512, len(todo))}/{len(todo)} ({time.time() - t:.0f}s)", file=sys.stderr, flush=True)
    st.items = [st.items[i] for i in keep] + new_items
    kept_vec = [st.vec[i].astype(np.float32) for i in keep]
    st.vec = np.asarray(kept_vec + new_vec, dtype=np.float32).reshape(-1, DIM)
    if not np.isfinite(st.vec).all():
        sys.exit("vector có NaN hoặc inf: kiểm dtype (phải bfloat16) trước khi lưu")
    st.save(enc_name)
    print(f"build: {len(rows)} dòng, embed mới {len(todo)}, dùng lại {len(rows) - len(todo)}, "
          f"store {len(st.items)} item, {time.time() - t:.1f}s", file=sys.stderr)


def mrl(v, dims):
    if dims >= DIM:
        return v
    x = v[:, :dims].astype(np.float32)
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def topk(sims, k):
    k = min(k, sims.shape[-1])
    idx = np.argpartition(-sims, k - 1)[:k]
    return idx[np.argsort(-sims[idx])]


def search(st, qv, mask, k, per_url, coarse, pool):
    cand = np.flatnonzero(mask)
    if not len(cand):
        return []
    docs = st.vec[cand].astype(np.float32)
    if coarse and coarse < DIM and len(cand) > pool:
        s0 = mrl(docs, coarse) @ mrl(qv[None, :], coarse)[0]
        keep = topk(s0, pool)
        cand, docs = cand[keep], docs[keep]
    sims = docs @ qv
    order = np.argsort(-sims)
    out, seen = [], set()
    for j in order:
        it = st.items[cand[j]]
        if per_url:
            if it["url"] in seen:
                continue
            seen.add(it["url"])
        out.append({"id": it["id"], "url": it["url"], "level": it["level"], "cos": round(float(sims[j]), 4),
                    "meta": {k2: it["meta"][k2] for k2 in ("title", "heading", "h2") if k2 in it["meta"]}})
        if len(out) >= k:
            break
    return out


def cmd_query(a):
    st = Store(a.store)
    if not st.items:
        sys.exit("store rỗng")
    enc_name = MODEL if os.environ.get("SVI_FAKE") != "1" else "fake"
    check_model(st, enc_name)
    qs = read_jsonl(a.inp)
    qv = encoder(a.max_tokens).encode([q["text"] for q in qs], a.qprompt)
    out = []
    for q, v in zip(qs, qv):
        f = q.get("filter") or {}
        m = st.mask(f.get("level", a.level), f.get("url_prefix"), set(f["urls"]) if f.get("urls") else None)
        hits = search(st, v, m, a.k, a.per_url, a.coarse, a.pool)
        out.append({"id": q["id"], "text": q["text"], "top": hits})
    write_jsonl(a.out, out)
    print(f"query: {len(out)} truy vấn -> {a.out}", file=sys.stderr)


def cmd_cross(a):
    sa, sb = Store(a.store), Store(a.against)
    if sa.manifest.get("model") != sb.manifest.get("model"):
        sys.exit("2 store khác model")
    ma, mb = sa.mask(a.level), sb.mask(a.against_level)
    ia, ib = np.flatnonzero(ma), np.flatnonzero(mb)
    if not len(ia) or not len(ib):
        sys.exit("một trong 2 store không có item ở level đã chọn")
    vb = sb.vec[ib].astype(np.float32)
    out = []
    for start in range(0, len(ia), 1024):
        chunk = ia[start:start + 1024]
        sims = sa.vec[chunk].astype(np.float32) @ vb.T
        for row, i in zip(sims, chunk):
            top = topk(row, a.k)
            it = sa.items[i]
            out.append({"id": it["id"], "url": it["url"], "max_cos": round(float(row[top[0]]), 4),
                        "top": [{"id": sb.items[ib[j]]["id"], "url": sb.items[ib[j]]["url"],
                                 "cos": round(float(row[j]), 4)} for j in top]})
    write_jsonl(a.out, out)
    print(f"cross: {len(out)} item -> {a.out}", file=sys.stderr)


def field(it, spec):
    if spec == "folder":
        parts = [p for p in urlparse(it["url"]).path.split("/") if p]
        return "/" + parts[0] + "/" if len(parts) > 1 else "/"
    if spec.startswith("meta."):
        return it["meta"].get(spec[5:])
    return it.get(spec)


def cmd_centroid(a):
    st = Store(a.store)
    idx = np.flatnonzero(st.mask(a.level))
    if not len(idx):
        sys.exit("không có item ở level này")
    v = st.vec[idx].astype(np.float32)
    w = np.ones(len(idx), dtype=np.float32)
    if a.weight:
        w = np.asarray([float(field(st.items[i], a.weight) or 0) for i in idx], dtype=np.float32)
        w = np.log1p(np.maximum(w, 0)) + 1  # log để vài trang nhiều click không kéo lệch hết tâm
    c = (v * w[:, None]).sum(0)
    c /= np.linalg.norm(c)
    cos_site = v @ c
    groups = {}
    if a.group:
        for pos, i in enumerate(idx):
            groups.setdefault(field(st.items[i], a.group) or "(trống)", []).append(pos)
    gc = {}
    for g, ps in groups.items():
        x = (v[ps] * w[ps, None]).sum(0)
        gc[g] = x / np.linalg.norm(x)
    out = []
    for pos, i in enumerate(idx):
        it = st.items[i]
        r = {"id": it["id"], "url": it["url"], "cos_site": round(float(cos_site[pos]), 4)}
        if a.group:
            g = field(it, a.group) or "(trống)"
            r.update({"group": g, "cos_group": round(float(v[pos] @ gc[g]), 4)})
        out.append(r)
    summary = {"level": a.level, "n": int(len(idx)), "focus_mean_cos": round(float(cos_site.mean()), 4),
               "radius_p90": round(float(np.percentile(1 - cos_site, 90)), 4),
               "groups": {g: {"n": len(ps), "mean_cos_site": round(float(cos_site[ps].mean()), 4),
                              "mean_cos_group": round(float((v[ps] @ gc[g]).mean()), 4),
                              "cos_group_to_site": round(float(gc[g] @ c), 4)} for g, ps in groups.items()}}
    write_jsonl(a.out, out)
    Path(str(a.out) + ".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"centroid: {len(out)} item, focus {summary['focus_mean_cos']} -> {a.out}", file=sys.stderr)


def cmd_pairs(a):
    st = Store(a.store)
    idx = np.flatnonzero(st.mask(a.level))
    v = st.vec[idx].astype(np.float32)
    out = []
    for start in range(0, len(idx), 2048):
        sims = v[start:start + 2048] @ v.T
        for r in range(sims.shape[0]):
            p = start + r
            js = np.flatnonzero(sims[r, p + 1:] >= a.min) + p + 1
            for j in js:
                ia, ib = st.items[idx[p]], st.items[idx[j]]
                if a.cross_url and ia["url"] == ib["url"]:
                    continue
                if a.same and field(ia, a.same) != field(ib, a.same):
                    continue
                out.append({"a": ia["id"], "b": ib["id"], "url_a": ia["url"], "url_b": ib["url"],
                            "cos": round(float(sims[r, j]), 4)})
    out.sort(key=lambda x: -x["cos"])
    write_jsonl(a.out, out)
    print(f"pairs: {len(out)} cặp từ {a.min} -> {a.out}", file=sys.stderr)


def cmd_stats(a):
    st = Store(a.store)
    print(json.dumps(st.manifest, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--in", dest="inp", required=True)
    b.add_argument("--mode", choices=("upsert", "replace"), default="upsert")
    b.add_argument("--prompt", default="Document")
    b.add_argument("--keep-text", action="store_true", help="lưu cả chữ trong items.jsonl (để đọc lại khi review)")
    b.add_argument("--levels", default=None, help="chỉ embed các level này, ví dụ page,passage")
    q = sub.add_parser("query")
    q.add_argument("--in", dest="inp", required=True)
    q.add_argument("--k", type=int, default=10)
    q.add_argument("--level", default=None)
    q.add_argument("--qprompt", default="SearchQuery")
    q.add_argument("--per-url", action="store_true", help="mỗi URL chỉ lấy item tốt nhất (max-sim theo trang)")
    q.add_argument("--coarse", type=int, default=128, help="số chiều MRL để lọc thô; 768 = tắt")
    q.add_argument("--pool", type=int, default=300)
    c = sub.add_parser("cross")
    c.add_argument("--against", required=True)
    c.add_argument("--level", default="section")
    c.add_argument("--against-level", default="passage")
    c.add_argument("--k", type=int, default=3)
    ce = sub.add_parser("centroid")
    ce.add_argument("--level", default="page")
    ce.add_argument("--group", default=None)
    ce.add_argument("--weight", default=None)
    p = sub.add_parser("pairs")
    p.add_argument("--level", default="section")
    p.add_argument("--min", type=float, required=True)
    p.add_argument("--cross-url", action="store_true")
    p.add_argument("--same", default=None)
    s = sub.add_parser("stats")
    for x in (b, q, c, ce, p, s):
        x.add_argument("--store", required=True)
        x.add_argument("--max-tokens", type=int, default=1024)
    for x in (q, c, ce, p):
        x.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    {"build": cmd_build, "query": cmd_query, "cross": cmd_cross, "centroid": cmd_centroid,
     "pairs": cmd_pairs, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
