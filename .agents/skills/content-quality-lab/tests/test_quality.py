#!/usr/bin/env python3
"""Test offline cho quality.py: không gọi Jev, không cần model. Lệnh template dùng store dựng tay.
Chạy: python3 -I tests/test_quality.py  (lệnh template cần numpy: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = HERE.parent / "scripts" / "quality.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)


def run(*args, ok=True, cwd=None):
    p = subprocess.run([PY, "-I", str(Q), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def jev_row(u, od, fh):
    return {"id": u, "task_version": "t1", "answers": {"effort": {"score": 0.5}, "original_data": {"p_yes": od},
                                                       "first_hand": {"p_yes": fh}, "named_sources": {"p_yes": 0.5}}}


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    # prepare: ghép section theo số thứ tự, bỏ trang ngắn, lọc theo danh sách URL
    long = " ".join(["chữ"] * 200)
    write(t / "rows.jsonl", [
        {"id": "https://a.vn/x/#s1", "level": "section", "url": "https://a.vn/x/", "text": "PHẦN HAI " + long},
        {"id": "https://a.vn/x/#s0", "level": "section", "url": "https://a.vn/x/", "text": "PHẦN MỘT " + long},
        {"id": "https://a.vn/y/#s0", "level": "section", "url": "https://a.vn/y/", "text": "ngắn"},
        {"id": "https://b.vn/z/#s0", "level": "section", "url": "https://b.vn/z/", "text": long},
        {"id": "https://a.vn/x/#p0", "level": "passage", "url": "https://a.vn/x/", "text": "bỏ qua"}])
    write(t / "pages.jsonl", [{"url": "https://a.vn/x/", "title": "Tiêu đề X", "lang": "vi-VN"},
                              {"url": "https://b.vn/z/", "title": "Z", "lang": "en"}])
    (t / "urls.txt").write_text("https://a.vn/x/\nhttps://a.vn/y/\n", encoding="utf-8")
    run("prepare", "--rows", t / "rows.jsonl", "--pages", t / "pages.jsonl", "--urls", t / "urls.txt", "--out", t / "in.jsonl")
    rows = jl(t / "in.jsonl")
    assert [r["id"] for r in rows] == ["https://a.vn/x/"], rows
    txt = rows[0]["state"]["text"]
    assert txt.startswith("Tiêu đề X") and txt.index("PHẦN MỘT") < txt.index("PHẦN HAI") and rows[0]["state"]["lang"] == "vi"

    # validate: nhận cả 2 dạng pool
    write(t / "jev.jsonl", [jev_row("https://own.vn/a/", 0.1, 0.1), jev_row("https://c1.vn/", 0.95, 0.95),
                            jev_row("https://c2.vn/", 0.5, 0.2), jev_row("https://n1.vn/", 0.05, 0.05)])
    write(t / "pools.jsonl", [
        {"id": "P1", "text": "câu hỏi 1", "urls": [{"url": "https://own.vn/a/", "label": 0}, {"url": "https://c1.vn/", "label": 2},
                                                  {"url": "https://n1.vn/", "label": 0}]},
        {"id": "P2", "text": "câu hỏi 2", "candidates": ["https://c2.vn/", "https://n1.vn/", "https://khong-co.vn/"],
         "labels": {"https://c2.vn/": 1}}])
    run("validate", "--jev-out", t / "jev.jsonl", "--pools", t / "pools.jsonl", "--out", t / "auc.jsonl")
    auc = jl(t / "auc.jsonl")
    assert len(auc) == 5 and {(r["pool"], r["url"], r["cited"]) for r in auc} >= {("P2", "https://c2.vn/", 1), ("P1", "https://c1.vn/", 1)}

    # report: thiếu cổng thì dừng
    write(t / "empty_reg.json", [])
    (t / "reg0.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
    run("report", "--jev-out", t / "jev.jsonl", "--registry", t / "reg0.json", "--site", "own.vn", "--out-dir", t / "r0",
        ok=False, cwd=t)
    reg = {"entries": [{"rubric": "content-effort", "version": "t1", "mode": "jev", "site": "own.vn", "question": "original_data",
                        "conf_gate": 0.8}, {"rubric": "content-effort", "version": "t1", "mode": "jev", "site": "own.vn",
                                            "question": "first_hand", "conf_gate": 0.8},
                       {"rubric": "passage-dup", "version": "1.0", "mode": "cosine", "site": "own.vn", "threshold": 0.96}]}
    (t / "reg.json").write_text(json.dumps(reg), encoding="utf-8")
    run("report", "--jev-out", t / "jev.jsonl", "--registry", t / "reg.json", "--site", "own.vn", "--pools", t / "pools.jsonl",
        "--out-dir", t / "r", cwd=t)
    pages = {p["url"]: p for p in jl(t / "r/pages.jsonl")}
    assert pages["https://c1.vn/"]["original_data"] == "yes" and pages["https://own.vn/a/"]["original_data"] == "no"
    assert pages["https://c2.vn/"]["original_data"] == "review" and pages["https://c2.vn/"]["named_sources"] == "chưa hiệu chuẩn"
    rep = (t / "r/report.md").read_text()
    assert "thêm số đo từ dự án thật" in rep and "trang mình ngoài pool" in rep

    # template: 2 trang có 1 passage gần trùng, 1 trang khác hẳn
    import numpy as np
    rng = np.random.default_rng(3)
    base = rng.standard_normal(768)
    vecs = [base, base + 0.05 * rng.standard_normal(768), rng.standard_normal(768), rng.standard_normal(768),
            rng.standard_normal(768)]
    urls = ["https://own.vn/a/", "https://own.vn/b/", "https://own.vn/a/", "https://own.vn/b/", "https://own.vn/c/"]
    V = np.asarray(vecs, dtype=np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    (t / "store").mkdir()
    write(t / "store/items.jsonl", [{"id": f"{u}#p{i}", "level": "passage", "url": u, "meta": {}, "text": f"đoạn {i}"}
                                    for i, u in enumerate(urls)])
    np.save(t / "store/vec.npy", V.astype(np.float16))
    (t / "store/manifest.json").write_text(json.dumps({"model": "fake"}), encoding="utf-8")
    run("template", "--store", t / "store", "--registry", t / "reg0.json", "--site", "own.vn", "--out-dir", t / "t0",
        ok=False, cwd=t)
    run("template", "--store", t / "store", "--registry", t / "reg.json", "--site", "own.vn", "--out-dir", t / "t", cwd=t)
    pairs = jl(t / "t/dup_pairs.jsonl")
    assert len(pairs) == 1 and {pairs[0]["url_a"], pairs[0]["url_b"]} == {"https://own.vn/a/", "https://own.vn/b/"}
    assert pairs[0]["status"] == "dup"
    tp = {p["url"]: p for p in jl(t / "t/pages.jsonl")}
    assert tp["https://own.vn/a/"]["dup_share"] == 0.5 and tp["https://own.vn/c/"]["dup"] == 0
print("test_quality: đạt")
