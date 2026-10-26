#!/usr/bin/env python3
"""Test offline cho visual.py: HTML mẫu 1 trang, ảnh PNG tạo bằng Pillow, nhãn Jev giả.
Không test embed (cần model) và shoot (cần Chrome). Chạy: python3 -E tests/test_visual.py (cần beautifulsoup4 + Pillow).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent / "scripts" / "visual.py"
sys.path.insert(0, str(HERE.parent / "scripts"))
import visual  # noqa: E402


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-E", str(VIS), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


HTML = """<html><body><header><img src="/logo.png" alt="logo"></header><article>
<h1>Bài mẫu</h1><p>Mở đầu bài viết về công cụ SEO với đủ chữ để thành một mục riêng của trang mẫu này nhé bạn đọc.</p>
<h2>Google Search Console</h2><p>Search Console cho biết truy vấn, hiển thị và lượt nhấp của từng trang trên Google, rất hữu ích cho người làm SEO mỗi ngày.</p>
<img src="/a.png" alt="Báo cáo hiệu suất trong Google Search Console"><img src="/b.png" alt="ui ux 10">
<h2>Ahrefs</h2><p>Ahrefs đo backlink, từ khoá và đối thủ của website, là bộ công cụ trả phí phổ biến nhất ngành SEO hiện nay.</p>
<img data-src="/c.png" src="data:image/gif;base64,x" alt=""><img src="/d.png" alt="logo"><img src="/e.svg" alt="icon">
</article></body></html>"""


def main():
    assert visual.fileish("ui ux 10") and visual.fileish("pic3") and visual.fileish("Group35")
    assert not visual.fileish("Báo cáo hiệu suất trong Search Console") and not visual.fileish("SEO năm 2026")
    from PIL import Image
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "html").mkdir()
        (d / "html" / "p1.html").write_text(HTML, encoding="utf-8")
        (d / "html" / "p1.url").write_text("https://mau.vn/bai/", encoding="utf-8")
        run("images", "--html-dir", d / "html", "--out", d / "images.jsonl")
        im = {x["src"].rsplit("/", 1)[-1]: x for x in jl(d / "images.jsonl")}
        assert set(im) == {"a.png", "b.png", "c.png", "d.png"}, set(im)  # bỏ ảnh header, svg, data URI
        assert im["a.png"]["h2"] == "Google Search Console" and im["c.png"]["h2"] == "Ahrefs"
        assert "fileish_alt" in im["b.png"]["flags"] and "missing_alt" in im["c.png"]["flags"]
        assert im["a.png"]["flags"] == [] and len(jl(d / "sections.jsonl")) == 3

        # media.jsonl giả (thay lệnh embed): ảnh nhỏ được đệm khi dựng input Jev
        for n, size in (("a", (800, 500)), ("d", (200, 120))):
            Image.new("RGB", size, "gray").save(d / f"{n}.png")
        med = [{**im["a.png"], "img": str(d / "a.png"), "alt_cos": 0.75, "sec_cos": 0.7},
               {**im["d.png"], "img": str(d / "d.png"), "alt_cos": 0.55, "sec_cos": 0.5}]
        write(d / "media.jsonl", med)
        write(d / "bad.jsonl", [{**med[0], "img": "img/khong-co.png"}])
        assert "không tìm thấy" in run("embed", "--sample", d / "bad.jsonl", "--sections", d / "sections.jsonl",
                                       "--out", d / "x.jsonl", ok=False).stderr
        run("jev-in", "--media", d / "media.jsonl", "--out", d / "jev_in.jsonl")
        jin = {r["id"]: r for r in jl(d / "jev_in.jsonl")}
        small = jin[im["d.png"]["id"]]["state"]["image"]["image_path"]
        assert small.endswith("_pad.png") and min(Image.open(small).size) >= 320
        write(d / "jev_out.jsonl", [
            {"id": im["a.png"]["id"], "answers": {"alt_matches": {"p_yes": 0.9}, "fits_section": {"p_yes": 0.95}}},
            {"id": im["d.png"]["id"], "answers": {"alt_matches": {"p_yes": 0.05}, "fits_section": {"p_yes": 0.2}}}])
        write(d / "gold_alt.jsonl", [{"id": im["a.png"]["id"], "label": "yes"}, {"id": im["d.png"]["id"], "label": "no"}])
        run("pairs", "--media", d / "media.jsonl", "--jev-out", d / "jev_out.jsonl", "--gold", d / "gold_alt.jsonl",
            "--out", d / "pairs.jsonl")
        assert [(r["cos"], r["label"]) for r in jl(d / "pairs.jsonl")] == [(2.4, 1), (1.15, 0)]
        v = visual.task_version("image-fit")
        run("media", "--images", d / "images.jsonl", "--media", d / "media.jsonl", "--jev-out", d / "jev_out.jsonl",
            "--registry", d / "none.json", "--site", "mau.vn", "--out-dir", d / "w", ok=False) if not visual.find_defaults() else None
        reg = {"entries": [{"rubric": "alt-score", "version": f"{v}+w2", "mode": "cosine", "site": "mau.vn", "reject_below": 1.64},
                           {"rubric": "image-fit", "version": v, "mode": "jev", "site": "mau.vn", "question": "fits_section",
                            "positive": "yes", "threshold": 0.7, "conf_gate": 0.7}]}
        (d / "reg.json").write_text(json.dumps(reg), encoding="utf-8")
        run("media", "--images", d / "images.jsonl", "--media", d / "media.jsonl", "--jev-out", d / "jev_out.jsonl",
            "--registry", d / "reg.json", "--site", "mau.vn", "--out-dir", d / "w")
        D = {x["src"].rsplit("/", 1)[-1]: x for x in jl(d / "w" / "media_decisions.jsonl")}
        assert D["a.png"]["alt_status"] == "chưa kết luận" and D["a.png"]["fit_status"] == "khớp mục"
        assert D["d.png"]["alt_status"] == "alt lệch ảnh" and D["d.png"]["fit_status"] == "review"
        assert D["b.png"]["alt_status"] == "alt dạng tên file" and D["c.png"]["alt_status"] == "thiếu alt"
        assert "## Alt lệch ảnh" in (d / "w" / "media_report.md").read_text(encoding="utf-8")

        # layout: 1 pool, trang được trích có câu trả lời ở màn đầu
        Image.new("RGB", (1366, 900), "white").save(d / "s1.png")
        write(d / "shots.jsonl", [{"url": "https://x.vn/a", "shot": str(d / "s1.png")}, {"url": "https://mau.vn/bai/", "shot": str(d / "s1.png")}])
        write(d / "pools.jsonl", [{"id": "P1", "text": "công cụ seo", "urls": [{"url": "https://x.vn/a", "label": 1},
                                                                             {"url": "https://mau.vn/bai/", "label": 0}]}])
        run("jev-in", "--shots", d / "shots.jsonl", "--pools", d / "pools.jsonl", "--out", d / "jl_in.jsonl")
        assert [r["id"] for r in jl(d / "jl_in.jsonl")] == ["P1|https://x.vn/a", "P1|https://mau.vn/bai/"]
        box = {"box": {"top": 0.1, "bottom": 0.4, "left": 0.1, "right": 0.6}}
        ans = lambda p: {**{q: {"p_yes": p} for q in visual.FEATURES}, "centerpiece": box, "primary_cta": box}
        write(d / "jl_out.jsonl", [{"id": "P1|https://x.vn/a", "answers": ans(0.95)}, {"id": "P1|https://mau.vn/bai/", "answers": ans(0.05)}])
        lv = visual.task_version("first-screen")
        reg["entries"].append({"rubric": "first-screen", "version": lv, "mode": "jev", "site": "mau.vn",
                               "question": "answer_visible", "conf_gate": 0.8})
        (d / "reg.json").write_text(json.dumps(reg), encoding="utf-8")
        run("layout", "--jev-out", d / "jl_out.jsonl", "--pools", d / "pools.jsonl", "--registry", d / "reg.json",
            "--site", "mau.vn", "--own-domain", "mau.vn", "--out-dir", d / "w")
        rows = jl(d / "w" / "auc_rows.jsonl")
        assert len(rows) == 2 and rows[0]["cited"] == 1 and rows[0]["centerpiece_top"] == 0.1
        rep = (d / "w" / "layout_report.md").read_text(encoding="utf-8")
        assert "| answer_visible | 0.8 (site) | 1/1 | 0/1 | 0/1 |" in rep, rep
    print("test_visual: OK")


if __name__ == "__main__":
    main()
