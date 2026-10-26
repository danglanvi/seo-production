#!/usr/bin/env python3
"""Test offline cho svi.py và extract.py: encoder giả (SVI_FAKE=1), không cần model hay mạng.
Chạy bằng Python có beautifulsoup4: python3 -E tests/test_svi.py  (exit 0 = đạt)
svi.py chạy bằng venv embedding (SVI_PYTHON, mặc định ~/.venvs/embeddinggemma/bin/python nếu có).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVI = HERE.parent / "scripts" / "svi.py"
EXT = HERE.parent / "scripts" / "extract.py"
ENV = dict(os.environ, SVI_FAKE="1")
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"
SVI_PY = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else sys.executable)

HTML = """<html lang="vi"><head><title>Dịch vụ SEO | Mẫu</title>
<meta name="description" content="Mô tả trang mẫu."><link rel="canonical" href="https://mau.vn/dich-vu-seo/"></head>
<body><header><nav><a href="https://mau.vn/">Trang chủ</a></nav></header>
<main><article><h1>Dịch vụ SEO tổng thể</h1>
<h2>Dịch vụ SEO là gì</h2><p>Dịch vụ SEO là việc một đơn vị bên ngoài nghiên cứu, tối ưu và đo lường website để tăng lượt truy cập tự nhiên từ Google trong nhiều tháng liên tục.</p>
<p>Gói dịch vụ thường gồm audit kỹ thuật, nội dung, liên kết nội bộ và báo cáo hằng tháng, xem thêm <a href="https://mau.vn/bang-gia/">bảng giá dịch vụ SEO</a> để biết chi phí.</p>
<h3>Ai nên thuê</h3><p>Doanh nghiệp có website bán hàng hoặc dịch vụ nhưng chưa có đội SEO nội bộ đủ người làm nội dung và kỹ thuật thường nên thuê ngoài.</p>
<h2>Quy trình</h2><ul><li>Bước một là audit toàn bộ website và đối thủ cạnh tranh trong ngành để tìm khoảng trống nội dung lớn nhất.</li>
<li>Bước hai là lập kế hoạch nội dung theo cụm chủ đề, ưu tiên trang dịch vụ đang mang doanh thu cho doanh nghiệp.</li></ul>
</article></main><footer><a href="https://mau.vn/lien-he/">Liên hệ</a></footer></body></html>"""


def run(*args, ok=True):
    cmd = [sys.executable, "-E"] if str(args[0]).endswith("extract.py") else [SVI_PY, "-I"]
    p = subprocess.run([*cmd, *map(str, args)], env=ENV, capture_output=True, text=True)
    if ok and p.returncode != 0:
        raise AssertionError(f"{args[0]} lỗi: {p.stderr}")
    if not ok and p.returncode == 0:
        raise AssertionError(f"{args[0]} lẽ ra phải lỗi")
    return p


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        # extract: main content, bỏ nav/footer, passage có heading, anchor nội bộ trong bài
        (t / "html").mkdir()
        (t / "html" / "a.html").write_text(HTML, encoding="utf-8")
        run(EXT, "--html-dir", t / "html", "--site", "https://mau.vn", "--out", t / "rows.jsonl", "--pages", t / "pages.jsonl")
        rows, pages = jl(t / "rows.jsonl"), jl(t / "pages.jsonl")
        assert pages[0]["url"] == "https://mau.vn/dich-vu-seo/" and pages[0]["h1"] == "Dịch vụ SEO tổng thể"
        levels = [r["level"] for r in rows]
        assert levels.count("page") == 1 and levels.count("section") == 2, levels
        anchors = [r for r in rows if r["level"] == "anchor"]
        assert [a["meta"]["target"] for a in anchors] == ["https://mau.vn/bang-gia/"], anchors
        assert any(r["level"] == "passage" and r["text"].startswith("Dịch vụ SEO là gì > Ai nên thuê:") for r in rows)
        assert not any("Trang chủ" in r["text"] or "Liên hệ" in r["text"] for r in rows if r["level"] != "page")

        # Elementor: <article> nhỏ đứng trước bài, nội dung bọc trong elementor-widget-container, link ảnh không chữ
        long = " ".join(["Nội dung dịch vụ SEO tổng thể cho doanh nghiệp có website bán hàng."] * 20)
        (t / "el").mkdir()
        (t / "el" / "b.html").write_text(
            '<html><head><title>Bảng giá</title><link rel="canonical" href="https://mau.vn/bang-gia/"></head><body><main>'
            f'<article class="card"><p>{" ".join(["thẻ"] * 90)}</p></article>'
            f'<div class="elementor-widget elementor-widget-text-editor"><div class="elementor-widget-container">'
            f'<h2>Gói Starter</h2><p>{long}</p><p><a href="https://mau.vn/lien-he/"><img src="x.png"></a></p></div></div>'
            '</main></body></html>', encoding="utf-8")
        run(EXT, "--html-dir", t / "el", "--site", "https://mau.vn", "--out", t / "el.jsonl", "--pages", t / "elp.jsonl")
        ep = jl(t / "elp.jsonl")[0]
        assert ep["main_selector"] == "main" and ep["words_main"] > 200 and ep["h2"] == ["Gói Starter"], ep
        assert all((r["text"] or "").strip() for r in jl(t / "el.jsonl")), "dòng rỗng lọt vào rows"

        store = t / "store"
        run(SVI, "build", "--store", store, "--in", t / "rows.jsonl")
        n1 = json.loads((store / "manifest.json").read_text())["count"]
        assert n1 == len(rows)
        # build lại cùng input: không embed mới
        p = run(SVI, "build", "--store", store, "--in", t / "rows.jsonl")
        assert "embed mới 0" in p.stderr, p.stderr
        # replace: URL có trong input mới thay toàn bộ item cũ của URL đó
        write(t / "one.jsonl", [{"id": "https://mau.vn/dich-vu-seo/#page", "level": "page",
                                 "url": "https://mau.vn/dich-vu-seo/", "text": "trang mới"}])
        run(SVI, "build", "--store", store, "--in", t / "one.jsonl", "--mode", "replace")
        assert json.loads((store / "manifest.json").read_text())["count"] == 1
        run(SVI, "build", "--store", store, "--in", t / "rows.jsonl", "--mode", "replace")

        # query: chữ trùng hệt passage thì cos cao nhất là chính passage đó (encoder giả theo hash, cùng prompt)
        target = next(r for r in rows if r["level"] == "passage")
        write(t / "q.jsonl", [{"id": "q1", "text": target["text"]}])
        run(SVI, "query", "--store", store, "--in", t / "q.jsonl", "--level", "passage", "--qprompt", "Document",
            "--k", "3", "--out", t / "q_out.jsonl")
        top = jl(t / "q_out.jsonl")[0]["top"]
        assert top[0]["id"] == target["id"] and top[0]["cos"] > 0.99, top
        run(SVI, "query", "--store", store, "--in", t / "q.jsonl", "--per-url", "--out", t / "q2.jsonl")
        assert len({h["url"] for h in jl(t / "q2.jsonl")[0]["top"]}) == len(jl(t / "q2.jsonl")[0]["top"])

        # pairs: 2 trang có section giống hệt thì ra 1 cặp cos ~1
        dup = [{"id": f"https://mau.vn/{k}/#s0", "level": "section", "url": f"https://mau.vn/{k}/",
                "text": "Đoạn giống hệt nhau ở hai trang địa phương.", "meta": {"tpl": "local"}} for k in ("hn", "hcm")]
        write(t / "dup.jsonl", dup)
        run(SVI, "build", "--store", store, "--in", t / "dup.jsonl")
        run(SVI, "pairs", "--store", store, "--level", "section", "--min", "0.99", "--cross-url", "--out", t / "pairs.jsonl")
        pr = jl(t / "pairs.jsonl")
        assert len(pr) == 1 and pr[0]["cos"] > 0.99, pr

        # centroid: có summary, mọi item có cos_site
        run(SVI, "centroid", "--store", store, "--level", "section", "--group", "folder", "--out", t / "c.jsonl")
        assert all("cos_site" in r and "group" in r for r in jl(t / "c.jsonl"))
        assert "focus_mean_cos" in json.loads(Path(str(t / "c.jsonl") + ".summary.json").read_text())

        # cross: store B chứa đúng 1 section trùng chữ store A
        write(t / "b.jsonl", [dict(dup[0], id="b1", url="https://doi-thu.vn/x/", level="passage")])
        run(SVI, "build", "--store", t / "storeB", "--in", t / "b.jsonl")
        run(SVI, "cross", "--store", store, "--against", t / "storeB", "--level", "section", "--against-level", "passage",
            "--out", t / "x.jsonl")
        x = {r["id"]: r for r in jl(t / "x.jsonl")}
        assert x[dup[0]["id"]]["max_cos"] > 0.99

        # lỗi: id trùng, level sai
        write(t / "bad.jsonl", [{"id": "a", "level": "page", "url": "u", "text": "x"}] * 2)
        run(SVI, "build", "--store", t / "s2", "--in", t / "bad.jsonl", ok=False)
        write(t / "bad2.jsonl", [{"id": "a", "level": "zzz", "url": "u", "text": "x"}])
        run(SVI, "build", "--store", t / "s2", "--in", t / "bad2.jsonl", ok=False)
    print("test_svi: đạt")


if __name__ == "__main__":
    main()
