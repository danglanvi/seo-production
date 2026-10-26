#!/usr/bin/env python3
"""Test offline cho fanout_cover.py: encoder giả (SVI_FAKE=1), không cần model hay mạng.
Chạy: ~/.venvs/embeddinggemma/bin/python -B -I skills/geo-fanout-research/tests/test_fanout_cover.py
(svi.py cần numpy: script con chạy bằng SVI_PYTHON hoặc venv embedding, thiếu thì dùng python hiện tại)."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FC = HERE.parent / "scripts" / "fanout_cover.py"
SVI = HERE.parents[1] / "site-vector-index" / "scripts" / "svi.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1", PYTHONDONTWRITEBYTECODE="1")


def run(script, *args, ok=True):
    p = subprocess.run([PY, "-B", "-I", str(script), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (script.name, p.stderr)
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


# 1. Hàm gộp: ca thật 19/10/2026 (1 prompt đo lường GEO × 1 trang của site mình), 6 subquery đều ≥ 0,72.
#    Ngưỡng phủ 0,70 cho share 1,0 ở mọi trang: lý do share_ge dưới 0,75 có AUC 0,5 ở dev.
spec = importlib.util.spec_from_file_location("fc", FC)
fc = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(fc)
best = [0.7212, 0.7402, 0.7936, 0.7960, 0.8434, 0.8718]
agg = fc.aggregate(best, fc.parse_grid("0.70:0.80:0.05"))
assert agg["n_subq"] == 6 and agg["min_best"] == 0.7212, agg
assert abs(agg["mean_best"] - 0.7944) < 1e-4, agg["mean_best"]
assert agg["share_ge_0_700"] == 1.0 and agg["share_ge_0_750"] == round(4 / 6, 4) and agg["share_ge_0_800"] == round(2 / 6, 4), agg
assert fc.parse_grid("0.70:0.90:0.025")[-1] == 0.9 and len(fc.parse_grid("0.70:0.90:0.025")) == 9

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    urls = [f"https://mau.vn/{s}/" for s in ("a", "b")]
    rows = []
    for u in urls:
        rows.append({"id": u + "#page", "level": "page", "url": u, "text": "trang " + u})
        for s in range(2):
            rows += [{"id": f"{u}#s{s}p{i}", "level": "passage", "url": u, "text": f"đoạn {s}-{i} của {u}",
                      "meta": {"heading": f"Mục {s}", "section_index": s}} for i in range(2)]
    write(t / "rows.jsonl", rows)
    # encoder giả băm cả prompt: dựng store bằng prompt SearchQuery để chữ trùng cho cos 1
    run(SVI, "build", "--store", t / "st", "--in", t / "rows.jsonl", "--prompt", "SearchQuery")
    write(t / "pools.jsonl", [{"id": "P1", "text": "geo là gì", "group": "TOFU",
                               "candidates": urls + ["https://thieu.vn/"], "labels": {urls[0]: 2}}])
    # 2. Subquery trùng nguyên văn một passage: cos 1 với đúng passage đó
    write(t / "subq.jsonl", [{"id": "P1-s1", "query_id": "P1", "lens": "dinh-nghia", "text": "đoạn 1-0 của " + urls[1]},
                             {"id": "P1-s2", "query_id": "P1", "lens": "cach-lam", "text": "cách làm geo"}])
    run(FC, "cover", "--store", t / "st", "--subq", t / "subq.jsonl", "--pools", t / "pools.jsonl",
        "--out", t / "c.jsonl", "--detail", t / "d.jsonl", "--grid", "0.5:0.9:0.1")
    c = {r["url"]: r for r in jl(t / "c.jsonl")}
    assert set(c) == set(urls), c.keys()  # URL thiếu trong store bị bỏ qua
    assert c[urls[0]]["cited"] == 1 and c[urls[1]]["cited"] == 0 and c[urls[0]]["label"] == 2
    assert c[urls[1]]["n_subq"] == 2 and c[urls[1]]["n_passages"] == 4 and "share_ge_0_900" in c[urls[1]]
    d = [r for r in jl(t / "d.jsonl") if r["url"] == urls[1] and r["subq_id"] == "P1-s1"][0]
    assert d["best_cos"] > 0.999 and d["heading"] == "Mục 1" and d["best_item"] == f"{urls[1]}#s1p0", d
    # 3. gaps: không có ngưỡng thì Claude đọc; có ngưỡng thì COVERED/GAP; có cột trang khác tốt nhất
    out = run(FC, "gaps", "--detail", t / "d.jsonl", "--query-id", "P1", "--url", urls[1]).stdout
    assert "chưa hiệu chuẩn, Claude đọc" in out and "COVERED" not in out and urls[0] in out
    lines = [l for l in out.splitlines() if l.startswith("| ") and "Subquery" not in l]
    assert "cách làm geo" in lines[0], lines  # cos thấp xếp trước
    out2 = run(FC, "gaps", "--detail", t / "d.jsonl", "--query-id", "P1", "--url", urls[1], "--cover-at", "0.99").stdout
    assert out2.count("| COVERED |") == 1 and out2.count("| GAP |") == 1, out2
    # 4. Subquery trỏ prompt không có trong pools: dừng
    write(t / "bad.jsonl", [{"id": "X-s1", "query_id": "X", "text": "abc"}])
    run(FC, "cover", "--store", t / "st", "--subq", t / "bad.jsonl", "--pools", t / "pools.jsonl", "--out", t / "x.jsonl", ok=False)
    run(FC, "gaps", "--detail", t / "d.jsonl", "--query-id", "P9", "--url", urls[0], ok=False)
# 5. md-rows: H1 + đoạn mở thành page; đoạn dưới H2 mang heading; đoạn ngắn gộp với đoạn sau
md = "# GEO là gì\n\nGEO là tối ưu để AI trích.\n\n## Cách đo GEO\n\nĐo tỷ lệ trích.\n\n" + " ".join(["từ"] * 30) + "\n\n## Chi phí\n\n- Gói A\n- Gói B\n"
rws = fc.md_rows("A", md)
assert rws[0]["level"] == "page" and rws[0]["text"] == "GEO là gì | GEO là tối ưu để AI trích.", rws[0]
ps = [r for r in rws if r["level"] == "passage"]
assert [p["meta"]["heading"] for p in ps] == ["", "Cách đo GEO", "Chi phí"], [p["meta"] for p in ps]
assert ps[1]["text"].startswith("Cách đo GEO: Đo tỷ lệ trích. từ") and ps[1]["meta"]["section_index"] == 0
assert ps[2]["text"] == "Chi phí: Gói A Gói B" and ps[2]["meta"]["section_index"] == 1
assert len({p["id"] for p in ps}) == len(ps) and all(p["url"] == "variant://A" for p in ps)

# 6. variants: margin dưới ngưỡng thì Claude đọc; không có ngưỡng thì "chưa hiệu chuẩn"; thiếu điểm thì dừng.
#    Số thật 19/10 (1 prompt GEO, top 10): trang được trích 0,7997, trang site mình 0,7940, margin 0,0057 < 0,015.
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    rk = [{"id": f"s{i}", "urls": [{"url": "B", "cos": b}, {"url": "A", "cos": a}]}
          for i, (a, b) in enumerate([(0.80, 0.81), (0.79, 0.80), (0.81, 0.80)])]
    write(t / "rk.jsonl", rk)
    r1 = json.loads(run(FC, "variants", "--ranks", t / "rk.jsonl", "--decide-at", "0.015").stdout)
    assert r1["variants"][0]["url"] == "B" and r1["variants"][0]["wins"] == 2 and r1["margin"] == 0.0033, r1
    assert r1["verdict"].startswith("không phân định"), r1["verdict"]
    r2 = json.loads(run(FC, "variants", "--ranks", t / "rk.jsonl").stdout)
    assert r2["verdict"] == "chưa hiệu chuẩn, Claude đọc 6 trục"
    r3 = json.loads(run(FC, "variants", "--ranks", t / "rk.jsonl", "--decide-at", "0.003").stdout)
    assert r3["verdict"].startswith("mô phỏng phân định: B"), r3["verdict"]
    write(t / "thieu.jsonl", rk + [{"id": "s9", "urls": [{"url": "A", "cos": 0.9}]}])
    run(FC, "variants", "--ranks", t / "thieu.jsonl", ok=False)
print("test_fanout_cover: đạt")
