#!/usr/bin/env python3
"""serp-clustering: gom trước bằng EmbeddingGemma, SERP chỉ quyết cặp giáp ranh.

Lệnh:
  overlap   --serp <TSV seed,pos,url | thư mục JSON Firecrawl search>... --out DIR [--top 10]
            Đếm URL top 10 chung cho mọi cặp keyword. Keyword trùng ở nhiều nguồn: giữ nguồn đầu, ghi conflicts.
            Ra serp_pairs.jsonl {a, b, overlap} và keywords.txt.
  cos       --keywords kw.txt --out cos_pairs.jsonl [--prompt Clustering]
            Cosine EmbeddingGemma cho mọi cặp keyword. Chạy bằng venv embedding với -I.
  triage    --cos cos_pairs.jsonl --diff-below T_LO [--same-from T_HI] --out DIR
            Cặp cos < T_LO: chắc khác cụm. Cặp cos ≥ T_HI: chắc cùng cụm. Còn lại: cần SERP.
            Ra triage.jsonl, need_serp.txt (keyword cần kéo SERP), summary.json.
  evaluate  --triage triage.jsonl --serp-pairs serp_pairs.jsonl --out report.json [--keywords subset.txt]
            So triage với SERP overlap: cặp sai, lượt kéo SERP tiết kiệm được.
  labels    --cos cos_pairs.jsonl --serp-pairs serp_pairs.jsonl --pos-min N --out rows.jsonl [--keywords subset.txt]
            Dòng {id, cos, label} cho model-calibration (label = overlap ≥ N).

Luật verdict SERP (Bước 3 của SKILL.md): ≥ 4/10 GỘP, 2–3/10 BORDERLINE, ≤ 1/10 TÁCH. Gộp trang chỉ khi SERP ≥ 6/10.
Ngưỡng cosine không dùng chung giữa site: đọc references/gemma-truoc.md.
"""
import argparse
import csv
import itertools
import json
import os
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve()
SVI = HERE.parents[2] / "site-vector-index" / "scripts"


def nfc(s):
    return unicodedata.normalize("NFC", (s or "").strip())


def norm_url(u):
    p = urlparse(u)
    return (p.netloc.replace("www.", "") + p.path).rstrip("/")


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write_jl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def key(a, b):
    return " | ".join(sorted((a, b)))


def read_kw(path):
    return [nfc(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def load_serp(paths, top):
    urls, conflicts = {}, []

    def add(q, lst, src):
        q = nfc(q)
        if q in urls:
            if urls[q] != lst:
                conflicts.append({"keyword": q, "nguon_bo": src, "chung_voi_nguon_dau": len(set(urls[q]) & set(lst))})
            return
        urls[q] = lst

    for p in paths:
        pth = Path(p)
        files = sorted(pth.glob("*.json")) if pth.is_dir() else [pth]
        for f in files:
            if f.suffix == ".json":
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                web = (d.get("data") or {}).get("web") if isinstance(d, dict) and isinstance(d.get("data"), dict) else None
                if web:
                    add(f.stem.replace("_", " "), [norm_url(x["url"]) for x in web[:top]], str(f))
                continue
            rows = list(csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"))
            order = []
            for r in rows:
                if r["seed"] not in order:
                    order.append(r["seed"])
            for q in order:
                lst = [norm_url(r["url"]) for r in sorted((r for r in rows if r["seed"] == q), key=lambda r: int(r["pos"]))]
                add(q, lst[:top], str(f))
    return urls, conflicts


def cmd_overlap(a):
    urls, conflicts = load_serp(a.serp, a.top)
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    rows = [{"a": x, "b": y, "overlap": len(set(urls[x]) & set(urls[y])),
             "short": min(len(urls[x]), len(urls[y])) < a.top} for x, y in itertools.combinations(urls, 2)]
    write_jl(od / "serp_pairs.jsonl", rows)
    (od / "keywords.txt").write_text("".join(k + "\n" for k in urls), encoding="utf-8")
    (od / "conflicts.json").write_text(json.dumps(conflicts, ensure_ascii=False, indent=1), encoding="utf-8")
    dist = {}
    for r in rows:
        dist[r["overlap"]] = dist.get(r["overlap"], 0) + 1
    print(json.dumps({"keywords": len(urls), "pairs": len(rows), "conflicts": len(conflicts),
                      "phan_bo_overlap": dict(sorted(dist.items()))}, ensure_ascii=False))


def cmd_cos(a):
    sys.path.insert(0, str(SVI))
    import numpy as np
    import svi
    kws = read_kw(a.keywords)
    v = svi.encoder(a.max_tokens).encode(kws, a.prompt)
    sim = np.asarray(v, dtype=np.float32) @ np.asarray(v, dtype=np.float32).T
    model = svi.MODEL if os.environ.get("SVI_FAKE") != "1" else "fake"
    rows = [{"a": kws[i], "b": kws[j], "cos": round(float(sim[i, j]), 4), "prompt": a.prompt, "model": model}
            for i, j in itertools.combinations(range(len(kws)), 2)]
    write_jl(a.out, rows)
    print(f"cos: {len(kws)} keyword, {len(rows)} cặp, prompt {a.prompt} -> {a.out}", file=sys.stderr)


def subset(rows, path):
    if not path:
        return rows
    keep = set(read_kw(path))
    return [r for r in rows if r["a"] in keep and r["b"] in keep]


def cmd_triage(a):
    rows = subset(jl(a.cos), a.keywords)
    out, need = [], set()
    for r in rows:
        if a.same_from is not None and r["cos"] >= a.same_from:
            d = "chắc cùng cụm"
        elif r["cos"] < a.diff_below:
            d = "chắc khác cụm"
        else:
            d = "cần SERP"
            need.update((r["a"], r["b"]))
        out.append({**r, "triage": d})
    kws = {k for r in rows for k in (r["a"], r["b"])}
    od = Path(a.out)
    write_jl(od / "triage.jsonl", out)
    (od / "need_serp.txt").write_text("".join(k + "\n" for k in sorted(need)), encoding="utf-8")
    summ = {"pairs": len(out), "diff_below": a.diff_below, "same_from": a.same_from,
            "chac_khac": sum(r["triage"] == "chắc khác cụm" for r in out),
            "chac_cung": sum(r["triage"] == "chắc cùng cụm" for r in out),
            "can_serp": sum(r["triage"] == "cần SERP" for r in out),
            "keywords": len(kws), "keyword_can_serp": len(need), "keyword_khong_can_serp": len(kws - need)}
    (od / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False))


def cmd_evaluate(a):
    tri = subset(jl(a.triage), a.keywords)
    ov = {key(r["a"], r["b"]): r["overlap"] for r in jl(a.serp_pairs)}
    miss = [r for r in tri if key(r["a"], r["b"]) not in ov]
    if miss:
        sys.exit(f"{len(miss)} cặp thiếu SERP, ví dụ {miss[0]['a']} | {miss[0]['b']}")
    rows = [{**r, "overlap": ov[key(r["a"], r["b"])]} for r in tri]
    khac = [r for r in rows if r["triage"] == "chắc khác cụm"]
    cung = [r for r in rows if r["triage"] == "chắc cùng cụm"]
    kws = {k for r in rows for k in (r["a"], r["b"])}
    need = {k for r in rows if r["triage"] == "cần SERP" for k in (r["a"], r["b"])}
    err = [r for r in rows if (r["triage"] == "chắc khác cụm" and r["overlap"] >= a.borderline)
           or (r["triage"] == "chắc cùng cụm" and r["overlap"] < a.merge)]
    rep = {"pairs": len(rows), "keywords": len(kws),
           "serp_pull_baseline": len(kws), "serp_pull_gemma": len(need), "serp_pull_saved": len(kws) - len(need),
           "pairs_decided_without_serp": len(khac) + len(cung),
           "sai": {f"chac_khac_nhung_overlap_ge_{a.borderline}": sum(r["overlap"] >= a.borderline for r in khac),
                   f"chac_khac_nhung_overlap_ge_{a.gop}": sum(r["overlap"] >= a.gop for r in khac),
                   f"chac_cung_nhung_overlap_lt_{a.merge}": sum(r["overlap"] < a.merge for r in cung)},
           "so_cap_sai": len(err),
           "cap_sai": sorted(({"a": r["a"], "b": r["b"], "cos": r["cos"], "overlap": r["overlap"], "triage": r["triage"]}
                              for r in err), key=lambda r: -r["overlap"])}
    Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("pairs", "keywords", "serp_pull_gemma", "serp_pull_saved", "sai", "so_cap_sai")},
                     ensure_ascii=False))


def cmd_labels(a):
    cos = subset(jl(a.cos), a.keywords)
    ov = {key(r["a"], r["b"]): r["overlap"] for r in jl(a.serp_pairs)}
    rows = [{"id": key(r["a"], r["b"]), "cos": r["cos"], "label": int(ov[key(r["a"], r["b"])] >= a.pos_min),
             "overlap": ov[key(r["a"], r["b"])]} for r in cos if key(r["a"], r["b"]) in ov]
    write_jl(a.out, rows)
    print(f"labels: {len(rows)} cặp, dương (overlap ≥ {a.pos_min}) {sum(r['label'] for r in rows)} -> {a.out}",
          file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("overlap")
    o.add_argument("--serp", nargs="+", required=True)
    o.add_argument("--out", required=True)
    o.add_argument("--top", type=int, default=10)
    c = sub.add_parser("cos")
    c.add_argument("--keywords", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--prompt", default="Clustering")
    c.add_argument("--max-tokens", type=int, default=64)
    t = sub.add_parser("triage")
    t.add_argument("--cos", required=True)
    t.add_argument("--diff-below", type=float, required=True)
    t.add_argument("--same-from", type=float, default=None)
    t.add_argument("--keywords")
    t.add_argument("--out", required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("--triage", required=True)
    e.add_argument("--serp-pairs", required=True)
    e.add_argument("--keywords")
    e.add_argument("--borderline", type=int, default=2)
    e.add_argument("--gop", type=int, default=4)
    e.add_argument("--merge", type=int, default=6)
    e.add_argument("--out", required=True)
    lb = sub.add_parser("labels")
    lb.add_argument("--cos", required=True)
    lb.add_argument("--serp-pairs", required=True)
    lb.add_argument("--pos-min", type=int, required=True)
    lb.add_argument("--keywords")
    lb.add_argument("--out", required=True)
    a = ap.parse_args()
    {"overlap": cmd_overlap, "cos": cmd_cos, "triage": cmd_triage, "evaluate": cmd_evaluate, "labels": cmd_labels}[a.cmd](a)


if __name__ == "__main__":
    main()
