#!/usr/bin/env python3
"""Test offline cho links.py: site mẫu 8 trang, encoder giả (SVI_FAKE=1), nhãn Jev giả.
Chạy: python3 -I tests/test_links.py  (cần venv có numpy: SVI_PYTHON hoặc ~/.venvs/embeddinggemma)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINKS = HERE.parent / "scripts" / "links.py"
SVI = HERE.parents[1] / "site-vector-index" / "scripts" / "svi.py"
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)
ENV = dict(os.environ, SVI_FAKE="1")
S = "https://mau.vn"


def run(script, *args, ok=True):
    p = subprocess.run([PY, "-I", str(script), *map(str, args)], env=ENV, capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


PAGES = [
    ("/", "Mẫu Agency | Mẫu", "Mẫu Agency", 1500, "vi-VN", ["Dịch vụ"]),
    ("/backlink-la-gi/", "Backlink là gì? Cách xây backlink", "Backlink là gì?", 3000, "vi-VN", ["Backlink là gì?"]),
    ("/internal-link/", "Internal link là gì", "Internal link", 2500, "vi-VN", ["Internal link là gì?"]),
    ("/external-link/", "External link là gì", "External link", 2000, "vi", ["External link là gì?"]),
    ("/marketing/", "Kiến thức Marketing | Mẫu", "Marketing", 40, "vi-VN", ["Bài viết trong chuyên mục"]),
    ("/bang-gia/", "Bảng giá dịch vụ", "Bảng giá", 1200, "vi-VN", ["Gói A"]),
    ("/en/service/", "SEO service", "SEO service", 900, "en-US", ["Service"]),
    ("/bai-nguon/", "Bài nguồn", "Bài nguồn", 2000, "vi-VN", ["Mục 1"]),
]

ANCHORS = [  # (src, anchor, target, ctx)
    ("/bai-nguon/", "backlink", "/backlink-la-gi/", "Xây backlink chất lượng giúp tăng uy tín."),
    ("/bai-nguon/", "external link", "/internal-link/", "Đặt external link tới nguồn uy tín."),
    ("/bai-nguon/", "external link", "/external-link/", "External link là liên kết ra ngoài."),
    ("/bai-nguon/", "CTA", "/marketing/", "CTA là lời kêu gọi hành động."),
    ("/bai-nguon/", "Marketing", "/marketing/", "Xem chuyên mục Marketing."),
    ("/bai-nguon/", "Trang chủ", "/", "Trang chủ"),
    ("/bai-nguon/", "Xem chi tiết >>", "/bang-gia/", "Bảng giá các gói. Xem chi tiết >>"),
    ("/bai-nguon/", "https://mau.vn/bang-gia/", "/bang-gia/", "Giá tại https://mau.vn/bang-gia/"),
    ("/bai-nguon/", "form", "/convert-form/", "Điền form để nhận tư vấn."),
    ("/bai-nguon/", "tự trỏ", "/bai-nguon/", "Mục lục"),
    ("/en/service/", "Price list", "/bang-gia/", "See the price list"),
    ("/bai-nguon/", "​", "/external-link/", "Liên kết ra ngoài"),
]


def make_site(d):
    pages, rows = [], []
    for path, title, h1, words, lang, h2 in PAGES:
        u = S + path
        pages.append({"url": u, "title": title, "h1": h1, "words_main": words, "lang": lang, "h2": h2,
                      "first_para": f"Mở đầu của {title}", "status": 200})
        rows.append({"id": u + "#page", "level": "page", "url": u, "text": f"{title} | {' '.join(h2)}"})
    for i, (src, anc, tgt, ctx) in enumerate(ANCHORS):
        rows.append({"id": f"{S}{src}#a{i}", "level": "anchor", "url": S + src, "text": ctx,
                     "meta": {"anchor": anc, "target": S + tgt, "zone": "main"}})
    for i in range(10):  # trang chuyên mục có nhiều link vùng main
        rows.append({"id": f"{S}/marketing/#a{100 + i}", "level": "anchor", "url": S + "/marketing/",
                     "text": f"Bài {i}. Xem chi tiết >>", "meta": {"anchor": "Xem chi tiết >>",
                                                                   "target": S + "/backlink-la-gi/", "zone": "main"}})
    write(d / "pages.jsonl", pages)
    write(d / "rows.jsonl", rows)
    write(d / "page_rows.jsonl", [r for r in rows if r["level"] == "page"])
    run(SVI, "build", "--store", d / "store", "--in", d / "page_rows.jsonl")
    write(d / "queries.jsonl", [{"text": "external link", "chosen": S + "/external-link/", "share": 0.9,
                                 "impr": 150, "group": "nonbrand"}])


def main():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        make_site(d)
        w = d / "w"
        run(LINKS, "prepare", "--rows", d / "rows.jsonl", "--pages", d / "pages.jsonl", "--store", d / "store",
            "--queries", d / "queries.jsonl", "--brand", "Mẫu", "--out-dir", w)
        L = {x["anchor"] + "→" + x["target"].replace(S, ""): x for x in jl(w / "links.jsonl")}
        summ = json.loads((w / "summary.json").read_text(encoding="utf-8"))
        assert summ["skipped"].get("tự trỏ") == 1, summ
        assert "target_missing" in L["form→/convert-form"]["flags"]
        assert "target_listing" in L["CTA→/marketing"]["flags"]
        assert "listing_named" in L["Marketing→/marketing"]["flags"]
        assert "anchor_names_target" in L["Trang chủ→"]["flags"]
        assert "generic_anchor" in L["Xem chi tiết >>→/bang-gia"]["flags"]
        assert "naked_url" in L["https://mau.vn/bang-gia/→/bang-gia"]["flags"]
        assert "lang_mismatch" in L["Price list→/bang-gia"]["flags"]
        assert "empty_anchor" in L["→/external-link"]["flags"]
        assert "lang_mismatch" not in L["→/external-link"]["flags"], "vi và vi-VN là cùng ngôn ngữ"
        bad = L["external link→/internal-link"]
        assert "gsc_conflict" in bad["flags"] and "anchor_multi_target" in bad["flags"]
        assert "gsc_conflict" not in L["external link→/external-link"]["flags"]
        assert {"cos", "rank", "margin", "best_other"} <= set(bad["gemma"])
        jin = jl(w / "jev_in.jsonl")
        jids = {j["id"] for j in jin}
        assert L["CTA→/marketing"].get("jev_id") is None and L["Trang chủ→"].get("jev_id") is None
        assert bad["jev_id"] in jids and "[external link](/internal-link)" in \
            next(j for j in jin if j["id"] == bad["jev_id"])["state"]["link_location"]["paragraph"]

        # sample: phiếu gán mù không có điểm model
        run(LINKS, "sample", "--links", w / "links.jsonl", "--out-dir", w / "cal", "--low", "2", "--mid", "2",
            "--high", "2", "--random", "2")
        todo = (w / "cal" / "gold_todo.txt").read_text(encoding="utf-8")
        assert "margin" not in todo and "cos" not in todo and "ANCHOR:" in todo

        # Jev giả: link đúng p cao, link sai p thấp
        jo = [{"id": j["id"], "answers": {"delivers": {"p_yes": 0.1 if j["state"]["target"]["url"] ==
                                                        "/internal-link" else 0.95}}} for j in jin]
        write(w / "jev_out.jsonl", jo)
        gold = [{"id": x["id"], "label": "no" if x is bad else "yes"} for x in L.values() if x.get("jev_id")]
        write(w / "gold.jsonl", gold)
        run(LINKS, "validate", "--links", w / "links.jsonl", "--gold", w / "gold.jsonl", "--jev-out",
            w / "jev_out.jsonl", "--out-dir", w / "cal")
        sp = jl(w / "cal" / "score_pairs.jsonl")
        assert len(sp) == len(gold) and all(isinstance(r["cos"], float) for r in sp)
        assert sorted(r["agree"] for r in jl(w / "cal" / "gsc_rows.jsonl")) == [0, 1]

        # decide: thiếu cổng thì dừng; có cổng thì ra trạng thái
        run(LINKS, "decide", "--links", w / "links.jsonl", "--jev-out", w / "jev_out.jsonl", "--registry",
            d / "none.json", "--site", "mau.vn", "--out-dir", w, "--version", "t1", ok=False)
        reg = {"entries": [{"rubric": "anchor-score", "mode": "cosine", "site": "mau.vn", "version": "t1",
                            "threshold": 0.5}]}
        (d / "reg.json").write_text(json.dumps(reg), encoding="utf-8")
        run(LINKS, "decide", "--links", w / "links.jsonl", "--jev-out", w / "jev_out.jsonl", "--registry",
            d / "reg.json", "--site", "mau.vn", "--out-dir", w, "--version", "t1")
        D = {x["anchor"] + "→" + x["target"].replace(S, ""): x["status"] for x in jl(w / "decisions.jsonl")}
        assert D["form→/convert-form"] == "đích lỗi"
        assert D["CTA→/marketing"] == "lệch: trang chuyên mục"
        assert D["Marketing→/marketing"] == "khớp" and D["Trang chủ→"] == "khớp"
        assert D["external link→/internal-link"] == "review"
        rep = (w / "report.md").read_text(encoding="utf-8")
        assert "## Link trỏ về trang chuyên mục" in rep and "## Anchor trùng query GSC" in rep
        assert "| external link | 150 | /internal-link | /external-link |" in rep
    print("test_links: OK")


if __name__ == "__main__":
    main()
