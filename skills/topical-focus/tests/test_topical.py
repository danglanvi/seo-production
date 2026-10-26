#!/usr/bin/env python3
"""Test offline cho topical.py: store dựng tay với 3 cụm rõ + 3 trang lạc đề, encoder giả (SVI_FAKE=1) cho plan.
Chạy: python3 -I tests/test_topical.py  (cần venv có numpy + scikit-learn: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent / "scripts" / "topical.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1")


def run(*args, ok=True):
    p = subprocess.run([PY, "-I", str(TOP), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def make_store(d, prompt="Document"):
    import numpy as np
    rng = np.random.default_rng(1)
    site = rng.standard_normal(768)
    dirs = [site + 0.8 * rng.standard_normal(768) for _ in range(3)]
    items, vecs, pages = [], [], []
    for k, dv in enumerate(dirs):
        for i in range(20):
            u = f"https://mau.vn/cum{k}/bai-{i}/"
            vecs.append(dv + 0.25 * rng.standard_normal(768))
            items.append((u, f"Cụm {k} bài {i}", 800))
    for i in range(3):
        u = f"https://mau.vn/lac-de-{i}/"
        vecs.append(0.2 * site + rng.standard_normal(768))
        items.append((u, f"Lạc đề {i}", 800))
    u = "https://mau.vn/case-study/khach-a/"
    vecs.append(0.2 * site + rng.standard_normal(768))
    items.append((u, "Case study khách A", 800))
    extra = [("https://mau.vn/en/page/", "EN", 800, "en"), ("https://mau.vn/ngan/", "Ngắn", 100, "vi"),
             ("https://mau.vn/noindex/", "Noindex", 800, "vi"), ("https://mau.vn/trung/", "Trùng", 800, "vi")]
    for u, t, w, _ in extra:
        vecs.append(site + 0.25 * rng.standard_normal(768))
        items.append((u, t, w))
    V = np.asarray(vecs, dtype=np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    rows = []
    for (u, t, w) in items:
        rows.append({"id": u + "#page", "level": "page", "url": u, "prompt": prompt, "meta": {"title": t, "words_main": w}})
        lang = next((x[3] for x in extra if x[0] == u), "vi")
        pages.append({"url": u, "title": t, "lang": lang, "words_main": w, "h2": [t + " phần 1", t + " phần 2"],
                      "robots": "noindex" if "noindex" in u else "index, follow",
                      "canonical": "https://mau.vn/cum0/bai-0/" if "trung" in u else u})
    d.mkdir(parents=True)
    write(d / "items.jsonl", rows)
    np.save(d / "vec.npy", V.astype(np.float16))
    (d / "manifest.json").write_text(json.dumps({"model": "fake", "count": len(rows)}), encoding="utf-8")
    return pages


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    pages = make_store(t / "store")
    write(t / "pages.jsonl", pages)
    write(t / "metrics.jsonl", [{"url": p["url"], "impressions": 100 if "lac-de-0" in p["url"] else 5000, "clicks": 1}
                                for p in pages])
    (t / "core.txt").write_text("https://mau.vn/cum0/bai-0/\nhttps://mau.vn/cum0/bai-1\n", encoding="utf-8")
    (t / "names.json").write_text(json.dumps({"0": "Cụm A"}), encoding="utf-8")

    # scope: bỏ trang EN, trang ngắn, noindex, canonical trỏ trang khác
    run("map", "--store", t / "store", "--pages", t / "pages.jsonl", "--lang", "vi", "--core", t / "core.txt",
        "--metrics", t / "metrics.jsonl", "--proof", "/case-study/", "--names", t / "names.json", "--out", t / "m")
    s = json.loads((t / "m/summary.json").read_text())
    assert s["n_pages"] == 64 and s["dropped"] == {"khác ngôn ngữ": 1, "dưới 300 chữ": 1, "noindex": 1,
                                                   "canonical trỏ trang khác": 1}, s
    # 3 cụm rõ: k tự chọn đúng 3 (3 trang lạc đề không đủ thành cụm riêng)
    assert s["k"] == 3, s["k_scan"]
    rows = jl(t / "m/pages.jsonl")
    low = sorted(rows, key=lambda r: r["cos_site"])[:4]
    assert {r["url"] for r in low} == {f"https://mau.vn/lac-de-{i}/" for i in range(3)} | {"https://mau.vn/case-study/khach-a/"}
    assert all(r["outlier"] for r in low)
    rep = (t / "m/report.md").read_text()
    # trang bằng chứng không vào bảng trang nội dung xa tâm; tên cụm lấy từ names.json
    table = rep.split("## Trang nội dung xa tâm")[1].split("## Đọc kết quả")[0]
    assert "lac-de-0" in table and "ít hiển thị" in table and "case-study" not in table
    assert "Trang bằng chứng" in rep and "| Cụm A |" in rep
    assert s["cos_site_core"] is not None and all("cos_core" in r for r in rows)
    proxy = jl(t / "m/proxy_rows.jsonl")
    assert len(proxy) == 64 and all(p["log_impr"] is not None for p in proxy)

    # core quá ít URL trong scope -> dừng
    (t / "core1.txt").write_text("https://mau.vn/cum0/bai-0/\n", encoding="utf-8")
    run("map", "--store", t / "store", "--core", t / "core1.txt", "--out", t / "m1", ok=False)
    # vector dựng bằng prompt khác Document -> dừng
    make_store(t / "store_cl", prompt="Clustering")
    run("map", "--store", t / "store_cl", "--out", t / "m2", ok=False)

    # plan khi chưa có selftest: mọi bài ghi review
    write(t / "plan.jsonl", [{"id": "p1", "title": "Bài mới", "outline": ["Phần 1"]}])
    run("plan", "--map", t / "m", "--in", t / "plan.jsonl", "--out", t / "plan_out.jsonl")
    po = jl(t / "plan_out.jsonl")
    assert po[0]["review"] is True and len(po[0]["nearest_pages"]) == 3 and "margin_2nd" in po[0]
    # selftest chạy được và ghi plan_gate.json
    run("selftest", "--map", t / "m", "--pages", t / "pages.jsonl")
    g = json.loads((t / "m/plan_gate.json").read_text())
    assert g["n"] == 64 and len(g["bands"]) == 7
print("test_topical: đạt")
