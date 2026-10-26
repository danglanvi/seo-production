#!/usr/bin/env python3
"""Test offline cho backlinks.py: store 3 trang, encoder giả (SVI_FAKE=1), dữ liệu Ahrefs mẫu dạng file MCP đã lưu.
Chạy: python3 -I tests/test_backlinks.py  (cần venv có numpy: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BL = HERE.parent / "scripts" / "backlinks.py"
SVI = HERE.parents[1] / "site-vector-index" / "scripts" / "svi.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1")
S = "https://mau.vn"

sys.dont_write_bytecode = True
sys.path.insert(0, str(BL.parent))
import backlinks as bl  # noqa: E402


def run(script, *args, ok=True):
    p = subprocess.run([PY, "-I", str(script), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def link(src, to, anchor, **kw):
    b = {"url_from": src, "url_to": S + to, "anchor": anchor, "title": "Bài nguồn về backlink", "snippet_left": "Đọc thêm",
         "snippet_right": "để hiểu rõ.", "domain_rating_source": 40, "url_rating_source": 20, "traffic": 100, "positions": 30,
         "links_external": 10, "tld_class_source": "com", "page_type_source": "/Article", "page_category_source": "/Internet",
         "is_spam": False, "is_content": True, "is_dofollow": True, "is_ugc": False, "is_sponsored": False, "is_image": False,
         "languages": ["vi"], "root_name_source": src.split("/")[2].removeprefix("www."), "first_seen_link": "2026-01-01T00:00:00Z"}
    b.update(kw)
    return b


AHREFS = [
    link("https://blog-a.vn/bai-1/", "/backlink-la-gi/", "backlink là gì"),
    link("https://spam.cn/x/", "/backlink-la-gi/", "Black Hat SEO backlinks", is_spam=True, traffic_domain=0),
    link("https://farm.xyz/p/", "/", "ultrabet güncel giriş", links_external=900, traffic_domain=0),
    link("https://mot-tin-hieu.vn/p/", "/", "Mẫu agency", is_spam=True),
    link("https://site.blogspot.com/a/", "/internal-link/", "internal link", root_name_source="blogspot.com", is_dofollow=False),
    link("https://jp.example/p/", "/", "mau.vn", languages=["ja"]),
    link("https://old.vn/p/", "/bai-da-xoa/", "bài cũ"),
    link("https://mau-khac.vn/p/", "/", "Mẫu", root_name_source="mau-khac.vn"),
    link("https://edu.example.edu/p/", "/internal-link/", "https://mau.vn/internal-link/", tld_class_source="edu",
         snippet_left="Xem https://mau.vn/internal-link/", snippet_right=""),
]


def make_store(d):
    rows = [{"id": S + p + "#page", "level": "page", "url": S + p, "text": t, "meta": {"title": t}}
            for p, t in [("/", "Mẫu Agency"), ("/backlink-la-gi/", "Backlink là gì"), ("/internal-link/", "Internal link là gì")]]
    write(d / "page_rows.jsonl", rows)
    run(SVI, "build", "--store", d / "store", "--in", d / "page_rows.jsonl")


def test_units():
    assert bl.theme_text({"title": "T", "anchor": "https://mau.vn/x/", "ctx": "Xem https://mau.vn/x/ và mau.vn nhé"}) == "T | link: Xem và nhé"
    assert bl.theme_text({"title": "T", "anchor": "backlink", "ctx": "về backlink"}) == "T | backlink: về backlink"
    g = bl.DEFAULT_THEME
    assert bl.pts_theme(g["lo"], g) == 0 and bl.pts_theme(g["hi"], g) == 35 and bl.pts_theme(0.99, g) == 35
    assert bl.pts_traffic({"traffic": 999}) == 35 and bl.pts_traffic({"traffic": 0, "positions": 0}) == 0
    assert bl.pts_traffic({"traffic": 0, "positions": 9999}) <= 17.5
    b = {"url_rating_source": 30, "domain_rating_source": 90, "links_external": 10}
    assert bl.pts_trust(b, False, True) == 30 and bl.pts_trust(b, False, True, reject=True) == 0
    assert bl.pts_trust(dict(b, links_external=500), False, True) < bl.pts_trust(b, False, True)
    assert bl.pts_trust(b, True, True) < bl.pts_trust(b, False, True)
    assert bl.pts_trust(dict(b, domain_rating_source=0, tld_class_source="edu"), False, True) == 30
    assert not bl.BAD_ANCHOR.search("better backlinks") and bl.BAD_ANCHOR.search("casino online")


def test_registry(d):
    reg = d / "registry.json"
    reg.write_text(json.dumps({"entries": [{"rubric": "backlink-theme", "site": "mau.vn", "lo": 0.5, "hi": 0.7}]}), encoding="utf-8")
    assert bl.theme_gate(reg, "mau.vn") == {"lo": 0.5, "hi": 0.7, "pass": 0.5, "source": "registry"}
    assert bl.theme_gate(reg, "khac.vn")["source"] == "defaults"


def main():
    test_units()
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        test_registry(d)
        make_store(d)
        (d / "mcp.json").write_text(json.dumps([{"type": "text", "text": json.dumps({"backlinks": AHREFS})}]), encoding="utf-8")
        w = d / "w"
        run(BL, "prepare", "--ahrefs", d / "mcp.json", d / "mcp.json", "--store", d / "store", "--own-domains", "mau-khac.vn",
            "--site", "mau.vn", "--out-dir", w)
        L = {x["src"]: x for x in jl(w / "bl_links.jsonl")}
        assert len(L) == len(AHREFS), "trùng file phải gộp"
        F = {s: set(x["flags"]) for s, x in L.items()}
        assert F["https://blog-a.vn/bai-1/"] == set()
        assert L["https://spam.cn/x/"]["machine"] == ["M1", "M2", "M3"] and L["https://spam.cn/x/"]["verdict"] == "REJECT"
        assert L["https://spam.cn/x/"]["trust_pts"] == 0
        assert {"obl_farm", "spam_topic", "zero_organic"} <= F["https://farm.xyz/p/"] and L["https://farm.xyz/p/"]["verdict"] == "REJECT"
        one = L["https://mot-tin-hieu.vn/p/"]  # chỉ is_spam: một tín hiệu là REVIEW, Trust giữ nguyên
        assert one["machine"] == ["M1"] and one["verdict"] == "REVIEW" and one["trust_pts"] > 0
        assert L["https://blog-a.vn/bai-1/"]["verdict"] == "KEEP"
        assert {"platform", "nofollow"} <= F["https://site.blogspot.com/a/"] and L["https://site.blogspot.com/a/"]["source_type"] == "nen_tang"
        assert "lang_other" in F["https://jp.example/p/"]
        assert "target_missing" in F["https://old.vn/p/"] and L["https://old.vn/p/"]["gemma"]["rank"] is None
        assert "own_network" in F["https://mau-khac.vn/p/"]
        assert L["https://blog-a.vn/bai-1/"]["source_type"] == "bai_viet"
        for x in L.values():
            assert x["ttt"] == round(x["theme_pts"] + x["traffic_pts"] + x["trust_pts"], 1) and 0 <= x["ttt"] <= 100
            assert isinstance(x["theme_ok"], bool)
        summ = json.loads((w / "summary.json").read_text(encoding="utf-8"))
        assert summ["n"] == len(AHREFS) and summ["theme_gate"]["source"] == "defaults"

        (d / "dev.txt").write_text("https://blog-a.vn/bai-1/\n", encoding="utf-8")
        run(BL, "sample", "--links", w / "bl_links.jsonl", "--n", 8, "--exclude", d / "dev.txt", "--out-dir", w / "cal")
        ids = [r["id"] for r in jl(w / "cal" / "gold_ids.jsonl")]
        todo = (w / "cal" / "gold_todo.txt").read_text(encoding="utf-8")
        assert "blog-a.vn" not in todo and "spam.cn" not in todo and "old.vn" not in todo, "sample phải bỏ dev, spam, đích mất"
        assert "cos" not in todo and "0." not in todo, "phiếu gold không được lộ điểm model"
        write(w / "cal" / "gold.jsonl", [{"id": i, "theme": "yes" if k % 2 == 0 else "no"} for k, i in enumerate(ids)])
        p = run(BL, "validate", "--links", w / "bl_links.jsonl", "--gold", w / "cal" / "gold.jsonl", "--out-dir", w / "cal")
        res = json.loads(p.stdout)
        assert res["n"] == len(ids) and res["auc_cos"] is None or 0 <= res["auc_cos"] <= 1

        run(BL, "report", "--links", w / "bl_links.jsonl", "--out", w / "report.md")
        rep = (w / "report.md").read_text(encoding="utf-8")
        assert "Theme đạt" in rep and "mau.vn/bai-da-xoa" in rep
        assert "spam.cn" not in rep.split("## 15 link")[1].split("## Đích")[0], "bảng top không có link REJECT"
    print("test_backlinks: OK")


if __name__ == "__main__":
    main()
