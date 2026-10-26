#!/usr/bin/env python3
"""Test offline cho retrieval.py: encoder giả (SVI_FAKE=1), không cần model hay mạng.
Chạy: python3 -I tests/test_retrieval.py  (svi.py và retrieval.py chạy bằng venv embedding: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RET = HERE.parent / "scripts" / "retrieval.py"
SVI = HERE.parents[1] / "site-vector-index" / "scripts" / "svi.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1")


def run(script, *args, ok=True):
    p = subprocess.run([PY, "-I", str(script), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (script.name, p.stderr)
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    urls = [f"https://mau.vn/{s}/" for s in ("a", "b", "c")]
    rows = []
    for u in urls:
        rows.append({"id": u + "#page", "level": "page", "url": u, "text": "trang " + u})
        rows += [{"id": f"{u}#p{i}", "level": "passage", "url": u, "text": f"đoạn {i} của {u}"} for i in range(2)]
    write(t / "rows.jsonl", rows)
    run(SVI, "build", "--store", t / "st", "--in", t / "rows.jsonl")

    # rank: chỉ xếp trong candidates, URL thiếu trong store ghi vào missing, nhãn đi kèm
    write(t / "q.jsonl", [{"id": "q1", "text": "dịch vụ seo", "group": "BOFU",
                           "candidates": [urls[0], urls[1], "https://khac.vn/"], "labels": {urls[0]: 1}}])
    run(RET, "rank", "--store", t / "st", "--in", t / "q.jsonl", "--out", t / "r.jsonl")
    r = jl(t / "r.jsonl")[0]
    assert r["n_candidates"] == 2 and r["missing"] == ["https://khac.vn/"], r
    assert [u["rank"] for u in r["urls"]] == [1, 2] and r["urls"][0]["gap_to_top"] == 0
    assert {u["url"]: u["label"] for u in r["urls"]} == {urls[0]: 1, urls[1]: 0}
    assert all(u["best_item"].split("#")[1].startswith("p") for u in r["urls"])  # level passage mặc định

    # route: URL Google chọn có hạng trong toàn site, top1 khớp là bool
    write(t / "rq.jsonl", [{"id": "g1", "text": "bảng giá", "chosen": urls[2], "impr": 50, "pos": 4.2}])
    run(RET, "route", "--store", t / "st", "--in", t / "rq.jsonl", "--out", t / "ro.jsonl")
    o = jl(t / "ro.jsonl")[0]
    assert 1 <= o["chosen_rank"] <= 3 and isinstance(o["agree_top1"], bool) and len(o["gemma_top3"]) == 3
    assert o["impr"] == 50 and o["margin"] >= 0

    # validate: 5 query dương thắng âm, 1 query ngược -> AUC trung bình 5/6
    ranks = []
    for i in range(6):
        hi, lo = (0.8, 0.5) if i < 5 else (0.5, 0.8)
        ranks.append({"id": f"v{i}", "group": "x", "urls": [{"url": "p", "cos": hi, "rank": 1 if hi > lo else 2, "label": 1},
                                                          {"url": "n", "cos": lo, "rank": 2 if hi > lo else 1, "label": 0}]})
    write(t / "ranks.jsonl", ranks)
    run(RET, "validate", "--ranks", t / "ranks.jsonl", "--out", t / "rep.json")
    rep = json.loads((t / "rep.json").read_text(encoding="utf-8"))
    assert rep["n_queries"] == 6 and abs(rep["mean_auc"] - 5 / 6) < 1e-3, rep["mean_auc"]
    run(RET, "validate", "--ranks", t / "ranks.jsonl", "--out", t / "rep2.json", "--metric", "rank")
    assert abs(json.loads((t / "rep2.json").read_text())["mean_auc"] - 5 / 6) < 1e-3
    # quá ít query có đủ 2 lớp: dừng
    write(t / "few.jsonl", ranks[:3])
    run(RET, "validate", "--ranks", t / "few.jsonl", "--out", t / "rep3.json", ok=False)
print("test_retrieval: đạt")
