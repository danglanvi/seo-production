#!/usr/bin/env python3
"""Test offline cho lệnh gap và gold-sheet của topical.py, encoder giả (SVI_FAKE=1: cùng chữ thì cùng vector).
Chạy: python3 -I tests/test_gap.py  (cần venv có numpy + scikit-learn: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
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
    p = subprocess.run([PY, "-B", "-I", str(TOP), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


own = [{"url": f"https://mau.vn/chu-de-{i}/", "title": f"Chủ đề {i} là gì | Mẫu", "h1": f"Chủ đề {i} là gì",
        "lang": "vi-VN", "robots": "index, follow", "status": "200"} for i in range(25)]
own += [{"url": "https://mau.vn/en/topic/", "title": "Topic", "h1": "Topic", "lang": "en", "status": "200"},
        {"url": "https://mau.vn/an/", "title": "Trang ẩn", "h1": "Trang ẩn", "lang": "vi", "robots": "noindex", "status": "200"}]


def comp(site, url, title, h1="", status=200, lang="vi", final=None):
    return {"site": site, "url": url, "final_url": final or url, "status": status, "title": title, "h1": h1, "lang": lang,
            "robots": "", "sitemap_total": 40, "sampled": 10}


A = "doithu.vn"
rows_a = [
    comp(A, "https://doithu.vn/chu-de-3/", "Chủ đề 3 là gì October 2026 | DoiThu", "Chủ đề 3 là gì"),
    comp(A, "https://doithu.vn/x1/", "Khoảng trống X | DoiThu", "Khoảng trống X"),
    comp(A, "https://doithu.vn/x2/", "Khoảng trống X | DoiThu", "Khoảng trống X"),
    comp(A, "https://doithu.vn/y/", "Khoảng trống Y | DoiThu", "Khoảng trống Y"),
    comp(A, "https://doithu.vn/case-a/", "DoiThu x Khách A | DoiThu", "DoiThu x Khách A"),
    comp(A, "https://doithu.vn/tin/", "Tin nội bộ | DoiThu", "Tin nội bộ"),
    comp(A, "https://doithu.vn/loi/", "Lỗi", status=503),
    comp(A, "https://doithu.vn/chuyen/", "Chuyển hướng", final="https://khac-host.vn/"),
    comp(A, "https://doithu.vn/en/", "English page", lang="en"),
]
rows_b = [comp("khac.vn", "https://khac.vn/x/", "Khoảng trống X"),
          comp("khac.vn", "https://khac.vn/z/", "Chủ đề riêng Z")]

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    write(t / "own.jsonl", own)
    write(t / "a.jsonl", rows_a)
    write(t / "b.jsonl", rows_b)

    # lượt đầu chưa có ngưỡng: mọi trang ghi review, không gom cụm
    run("gap", "--site-pages", t / "own.jsonl", "--competitor", t / "a.jsonl", "--competitor", t / "b.jsonl", "--out", t / "g0")
    g0 = jl(t / "g0/gap_pages.jsonl")
    assert len(g0) == 8 and {r["state"] for r in g0} == {"review"}, g0  # bỏ 503, chuyển host khác, trang EN
    by = {r["id"]: r for r in g0}
    # bỏ đuôi brand lặp và năm: trang đối thủ khớp đúng chữ trang site, cosine 1
    assert by["https://doithu.vn/chu-de-3/"]["text"] == "Chủ đề 3 là gì", by["https://doithu.vn/chu-de-3/"]["text"]
    assert abs(by["https://doithu.vn/chu-de-3/"]["cos"] - 1) < 1e-3
    assert by["https://doithu.vn/chu-de-3/"]["nearest_own"] == "https://mau.vn/chu-de-3/"
    assert by["https://doithu.vn/case-a/"]["brand_page"] and not by["https://doithu.vn/y/"]["brand_page"]

    # có ngưỡng: khoảng trống được gom cụm, cụm nhiều đối thủ lên đầu, cụm trang thương hiệu xuống cuối
    run("gap", "--site-pages", t / "own.jsonl", "--competitor", t / "a.jsonl", "--competitor", t / "b.jsonl",
        "--gap", "0.86", "--cover", "0.95", "--out", t / "g1")
    g1 = {r["id"]: r for r in jl(t / "g1/gap_pages.jsonl")}
    assert g1["https://doithu.vn/chu-de-3/"]["state"] == "covered"
    assert all(r["state"] == "gap" for k, r in g1.items() if k != "https://doithu.vn/chu-de-3/")
    groups = json.loads((t / "g1/gap_groups.json").read_text(encoding="utf-8"))
    assert groups[0]["n"] == 3 and groups[0]["n_sites"] == 2, groups[0]
    assert groups[-1]["brand_share"] == 1.0
    rep = (t / "g1/gap_report.md").read_text(encoding="utf-8")
    assert "| doithu.vn | 6 | 1 | 0 | 5 | 10/40 URL sitemap |" in rep, rep
    assert "trang thương hiệu, case study của đối thủ" in rep

    # --cover thiếu --gap -> dừng
    run("gap", "--site-pages", t / "own.jsonl", "--competitor", t / "a.jsonl", "--cover", "0.9", "--out", t / "g2", ok=False)

    # gold-sheet: mẫu theo đối thủ, có 8 trang site gần nhất theo trùng chữ, chưa có nhãn
    run("gold-sheet", "--site-pages", t / "own.jsonl", "--competitor", t / "a.jsonl", "--competitor", t / "b.jsonl",
        "--n", "4", "--out", t / "sheet.jsonl")
    sh = jl(t / "sheet.jsonl")
    assert len(sh) == 4 and {r["site"] for r in sh} == {"doithu.vn", "khac.vn"}
    assert all(len(r["own_lexical_top8"]) == 8 and r["covered"] is None and "cos" not in r for r in sh)
    (t / "skip.txt").write_text("\n".join(r["id"] for r in sh), encoding="utf-8")
    run("gold-sheet", "--site-pages", t / "own.jsonl", "--competitor", t / "a.jsonl", "--competitor", t / "b.jsonl",
        "--n", "20", "--skip", t / "skip.txt", "--out", t / "sheet2.jsonl")
    assert not ({r["id"] for r in jl(t / "sheet2.jsonl")} & {r["id"] for r in sh})
print("test_gap: đạt")
