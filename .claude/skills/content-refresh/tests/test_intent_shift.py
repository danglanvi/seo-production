#!/usr/bin/env python3
"""Test offline cho intent_shift.py: encoder giả (SVI_FAKE=1), không cần model hay mạng.
Chạy: ~/.venvs/embeddinggemma/bin/python -B -I skills/content-refresh/tests/test_intent_shift.py"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
IS = HERE.parent / "scripts" / "intent_shift.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1", PYTHONDONTWRITEBYTECODE="1")


def run(*args, ok=True):
    p = subprocess.run([PY, "-B", "-I", str(IS), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("is_", IS)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# 1. shift(): trang trùng tâm thì drift âm hoặc 0; trang vuông góc với tâm thì drift ≈ spread
e = np.eye(4, dtype=np.float32)
tops = [e[0], e[0], (e[0] + e[1]) / np.sqrt(2)]
cos_c, spread, drift = m.shift(e[0], tops)
assert cos_c > 0.96 and drift < 0, (cos_c, spread, drift)
cos_c, spread, drift = m.shift(e[3], tops)
assert abs(cos_c) < 1e-4 and abs(drift - spread) < 1e-4 and spread > 0.9, (cos_c, spread, drift)
assert m.host("https://www.mau.vn/a/") == "mau.vn" and m.card("T", " a  b ", 3) == "T | a b"

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    res = [{"pos": i, "url": f"https://s{i}.vn/", "title": f"kết quả {i}", "snippet": "mô tả"} for i in range(1, 6)]
    res.insert(1, {"pos": 2, "url": "https://www.mau.vn/x/", "title": "trang mình", "snippet": "mô tả"})
    for i, r in enumerate(res):
        r["pos"] = i + 1
    write(t / "serp.jsonl", [{"query": "từ khóa là gì", "date": "2026-10-18", "results": res},
                             {"query": "ít kết quả", "results": res[:2]}])
    write(t / "pages.jsonl", [{"query": "từ khóa là gì", "url": "https://mau.vn/x/", "title": "Từ khóa SEO là gì",
                               "meta": "m", "position": 37.3, "impressions": 82},
                              {"query": "ít kết quả", "url": "https://mau.vn/y/", "title": "y", "meta": "m"},
                              {"query": "không có serp", "url": "https://mau.vn/z/", "title": "z", "meta": "m"}])
    # 2. --exclude-own bỏ kết quả cùng domain (kể cả www); truy vấn thiếu SERP hoặc thiếu kết quả bị bỏ qua.
    #    Ca thật 19/10: top 10 sau khi bỏ trang mình chỉ còn đủ ở 3/25 truy vấn, nên skill dùng top 3.
    p = run("--serp", t / "serp.jsonl", "--pages", t / "pages.jsonl", "--out", t / "o.jsonl", "--top", "3", "--exclude-own")
    o = jl(t / "o.jsonl")
    assert len(o) == 1 and "thiếu kết quả" in p.stderr and "không có SERP" in p.stderr, (o, p.stderr)
    r = o[0]
    assert r["top"] == ["https://s1.vn/", "https://s2.vn/", "https://s3.vn/"], r["top"]
    assert r["verdict"] == "chưa hiệu chuẩn, Claude đọc top 3" and r["position"] == 37.3 and r["serp_date"] == "2026-10-18"
    assert abs(r["drift"] - round(r["spread"] - r["cos_centroid"], 4)) <= 1e-4
    # 3. Có ngưỡng đã hiệu chuẩn thì ra verdict REWRITE hoặc refresh
    run("--serp", t / "serp.jsonl", "--pages", t / "pages.jsonl", "--out", t / "o2.jsonl", "--exclude-own", "--rewrite-at", "-5")
    assert jl(t / "o2.jsonl")[0]["verdict"].startswith("intent dịch chuyển")
    run("--serp", t / "serp.jsonl", "--pages", t / "pages.jsonl", "--out", t / "o3.jsonl", "--exclude-own", "--rewrite-at", "5")
    assert jl(t / "o3.jsonl")[0]["verdict"] == "intent giữ: refresh"
print("test_intent_shift: đạt")
