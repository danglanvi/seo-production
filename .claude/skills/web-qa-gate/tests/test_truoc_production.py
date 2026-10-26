#!/usr/bin/env python3
"""Test offline cho scripts/truoc_production.py (cổng trước production, audit đầu workstream). Không gọi mạng.
Chạy: python3 -B -E tests/test_truoc_production.py   hoặc   python3 -m pytest tests -q
Ca hỏng thật lấy từ đợt rà 16–24/10/2026:
  skeleton: người duyệt hỏi "đã kiểm skeleton chung theme chưa" khi 2 trang mới đã lên staging mà chưa ai so header, footer giữa template (17/10).
  diff: phép so tracking, mã HTTP 3 môi trường và smoke trước/sau deploy của cổng trước production (đặc tả qa-2, mục A4–A6).
  controls: menu cha href="#", div onclick, nút carousel và link icon không có tên (18–19/10).
  diff lưới: lưới 3+2 thiếu ô sau khi ghi nội dung, lane tự báo đạt (20/10).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "truoc_production.py"
sys.path.insert(0, str(SCRIPT.parent))
import truoc_production as t  # noqa: E402

HEAD = '<head><link rel="stylesheet" href="/a.css"><link rel="stylesheet" href="/p.css" media="print"><script src="/j.js"></script><script src="/d.js" defer></script>{extra}</head>'
HEADER = '<header class="site-header"><nav><ul><li class="menu-item {cur}"><a href="/">Trang chủ</a></li><li><a href="/dich-vu/">Dịch vụ</a></li></ul></nav></header>'
HEADER_OLD = '<header class="site-header"><div class="old"><a href="/">Trang chủ</a></div></header>'
FOOTER = '<footer class="site-footer"><p>Công ty mẫu</p>{logo}</footer>'
LOGO_LAZY = '<img alt="Logo" data-lazyloaded="1" data-src="/logo.webp" src="data:image/svg+xml;base64,AAA">'
LOGO_EAGER = '<img alt="Logo" data-no-lazy="1" fetchpriority="high" src="/logo.webp">'
LOGO_PNG, LOGO_PNG_WEBP = '<img alt="Logo" src="/logo.png">', '<img alt="Logo" src="/logo.png.webp">'


def page(header=HEADER, cur="", extra="", body="<main><h1>Tiêu đề</h1></main>", gtm="GTM-ABCDE12", lang="vi-VN", logo=LOGO_LAZY):
    return f"<!doctype html><html lang=\"{lang}\">{HEAD.format(extra=extra)}<body>{header.format(cur=cur)}{body}{FOOTER.format(logo=logo)}<script>gtm('{gtm}')</script></body></html>"


def write_run(d, pages, codes, interact=None):
    raw = Path(d) / "raw"
    (raw / "html").mkdir(parents=True)
    rows = []
    for name, (path, html) in pages.items():
        (raw / "html" / f"{name}.html").write_text(html, encoding="utf-8")
        (raw / "html" / f"{name}.hdr").write_text(f"HTTP/2 {codes.get(name, 200)}\n", encoding="utf-8")
        rows.append({"kind": "page", "name": name, "path": path, "code": str(codes.get(name, 200)), "final_code": str(codes.get(name, 200))})
    (raw / "http.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    if interact:
        (raw / "interact.jsonl").write_text("".join(json.dumps(r) + "\n" for r in interact), encoding="utf-8")


def run(*args):
    return subprocess.run([sys.executable, "-B", "-E", str(SCRIPT), *map(str, args)], capture_output=True, text=True)


def test_skeleton_pass_and_fail():
    with tempfile.TemporaryDirectory() as d:
        # Cùng header, chỉ khác class current-menu-item, nonce và cách lazy-load logo footer: không phải lỗi (cờ giả ở site mẫu 23/10).
        write_run(d, {"home": ("/", page(cur="current-menu-item")), "bai": ("/bai/", page(extra='<meta name="x" nonce="abc">', logo=LOGO_EAGER))}, {})
        res = t.cmd_skeleton(type("A", (), {"dir": d})())
        assert res["status"] == "PASS", res
    with tempfile.TemporaryDirectory() as d:
        # Class menu của plugin (mega-current-menu-item, page-item-N) và đuôi .webp do cache gắn: không phải lỗi.
        write_run(d, {"home": ("/", page(logo=LOGO_PNG)), "bai": ("/bai/", page(cur="mega-current-menu-item page_item page-item-106", logo=LOGO_PNG_WEBP))}, {})
        assert t.cmd_skeleton(type("A", (), {"dir": d})())["status"] == "PASS"
    with tempfile.TemporaryDirectory() as d:
        # Template bài viết dùng header cũ: FAIL.
        write_run(d, {"home": ("/", page()), "dv": ("/dv/", page()), "bai": ("/bai/", page(header=HEADER_OLD))}, {})
        p = run("skeleton", d)
        assert p.returncode == 1, p.stdout
        res = json.loads(p.stdout)
        fail = [f for f in res["findings"] if f["level"] == "FAIL"]
        assert fail and fail[0]["page"] == "bai" and "header khác cấu trúc" in fail[0]["issue"]
    with tempfile.TemporaryDirectory() as d:
        # Mục đổi ngôn ngữ chỉ hiện ở trang có bản dịch (site mẫu 19/10 và 23/10): FAIL khi chưa khai, PASS khi khai --ignore.
        ls = HEADER.replace("</ul>", '<li class="lang-switch-item"><a href="/en/" hreflang="en"><span>EN</span></a></li></ul>')
        write_run(d, {"home": ("/", page()), "dv": ("/dv/", page()), "gt": ("/gt/", page(header=ls))}, {})
        assert run("skeleton", d).returncode == 1
        p = run("skeleton", d, "--ignore", "lang-switch")
        assert p.returncode == 0 and json.loads(p.stdout)["status"] == "PASS", p.stdout
    with tempfile.TemporaryDirectory() as d:
        # Bản EN có menu khác bản VI là chủ ý: chỉ so trong cùng <html lang>. Lượt thử trên site mẫu 23/10 báo nhầm trang EN trước khi sửa.
        write_run(d, {"home": ("/", page()), "dv": ("/dv/", page()), "en": ("/en/", page(header=HEADER_OLD, lang="en-US"))}, {})
        res = t.cmd_skeleton(type("A", (), {"dir": d})())
        assert res["status"] == "PASS" and any("chỉ có 1 trang (en)" in n for n in res["notes"]), res


def test_skeleton_blocking_and_link_hint():
    with tempfile.TemporaryDirectory() as d:
        many = "".join(f'<link rel="stylesheet" href="/x{i}.css">' for i in range(4))
        # link trong head có id chứa site-header không được coi là header.
        hint = '<link rel="stylesheet" id="site-header-css" href="/h.css">'
        write_run(d, {"home": ("/", page(extra=hint)), "bai": ("/bai/", page(extra=hint + many))}, {})
        res = t.cmd_skeleton(type("A", (), {"dir": d})())
        issues = " | ".join(f["issue"] for f in res["findings"])
        assert "CSS chặn render" in issues and res["status"] == "WARN", res
        assert "CSS 2, JS 1" in res["notes"][0]  # a.css + h.css; print và defer không tính


def test_diff_two_and_three_runs():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as c:
        pg = {"home": ("/?nc=aa11", page()), "dv": ("/dv/", page()), "lh": ("/lien-he/", page())}
        write_run(a, pg, {})
        write_run(b, {"home": ("/?nc=bb22", page(gtm="GTM-ZZZZZ99")), "dv": ("/dv/", page()), "lh": ("/lien-he/", page())}, {"dv": 500})
        write_run(c, pg, {})
        p = run("diff", a, b, "--labels", "truoc,sau")
        assert p.returncode == 1, p.stdout
        res = json.loads(p.stdout)
        text = " | ".join(f"{f.get('path')} {f['issue']}" for f in res["findings"])
        assert "/dv/ mã đổi 200 → 500" in text
        assert "GTM-ABCDE12" in text and "không có ở sau" in text, text  # tham số nc= bị bỏ khi so đường dẫn
        p3 = run("diff", a, b, c, "--labels", "prod,stg-moi,stg-cu")
        res3 = json.loads(p3.stdout)
        dv = [f for f in res3["findings"] if f.get("path") == "/dv/"][0]
        assert "lệch chỉ ở stg-moi" in dv["issue"] and dv["level"] == "FAIL"


def test_diff_grid_counts():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        g = lambda n: [{"name": "home", "vw": 1366, "layout": {"grids": [{"sel": "#ly-do", "n": n}]}}]
        write_run(a, {"home": ("/", page())}, {}, interact=g(6))
        write_run(b, {"home": ("/", page())}, {}, interact=g(5))
        res = t.cmd_diff(type("A", (), {"dirs": [a, b], "labels": "truoc,sau"})())
        assert res["status"] == "WARN" and "truoc 6, sau 5" in res["findings"][0]["issue"], res


def test_controls():
    body = ('<main><h1>T</h1><nav><a href="#">Dịch vụ</a><a href="/a/">A</a></nav>'
            '<div class="card" onclick="go()">Thẻ</div>'
            '<button class="slick-next"></button><button aria-label="Sau">›</button>'
            '<a href="/fb/"><i class="fa fa-facebook"></i></a><a href="/x/"><img src="x.png" alt="X"></a></main>')
    with tempfile.TemporaryDirectory() as d:
        write_run(d, {"home": ("/", page(body=body))}, {})
        res = t.cmd_controls(type("A", (), {"dir": d})())
        text = " | ".join(f["issue"] + " " + " ".join(f["examples"]) for f in res["findings"])
        assert res["status"] == "WARN"
        assert 'href="#"' in text and "div.card" in text and "button.slick-next" in text and "a" in text
        noname = [f for f in res["findings"] if "không có tên" in f["issue"]][0]
        assert noname["issue"].startswith("2 ") and "img" not in " ".join(noname["examples"]), noname  # nút slick-next + link icon


def test_headers():
    with tempfile.TemporaryDirectory() as d:
        write_run(d, {"home": ("/", page()), "bai": ("/bai/", page())}, {})
        h = Path(d) / "raw" / "html"
        full = "x-content-type-options: nosniff\nreferrer-policy: strict-origin-when-cross-origin\npermissions-policy: camera=()\nx-frame-options: SAMEORIGIN\nstrict-transport-security: max-age=31536000\n"
        # Trang chủ qua 1 redirect: chỉ đọc khối header cuối.
        (h / "home.hdr").write_text("HTTP/2 301\nlocation: /\n\nHTTP/2 200\n" + full, encoding="utf-8")
        # Bài viết thiếu HSTS như site mẫu 19/10 (header đã lưu có nosniff, Referrer-Policy, Permissions-Policy, không có HSTS).
        (h / "bai.hdr").write_text("HTTP/2 200\n" + full.replace("strict-transport-security: max-age=31536000\n", ""), encoding="utf-8")
        for n in ("home", "bai"):
            (h / f"{n}.url").write_text(f"https://stg.example.vn/{n}/", encoding="utf-8")
        res = t.cmd_headers(type("A", (), {"dir": d})())
        assert res["status"] == "WARN" and len(res["findings"]) == 1 and "thiếu HSTS trên 1/2 trang" in res["findings"][0]["issue"], res


def test_urls_and_exit_codes():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "u.txt"
        f.write_text("https://stg.example.vn/\nhttps://stg.example.vn/dich-vu/\nhttps://stg.example.vn/dich-vu/\n# chú thích\n", encoding="utf-8")
        p = run("urls", f, "--base", "https://stg.example.vn", "--nc")
        lines = p.stdout.strip().splitlines()
        assert p.returncode == 0 and len(lines) == 3
        assert lines[0].startswith("home\t/?nc=") and lines[2].startswith("dich-vu-2\t/dich-vu/?nc=")
        assert run("skeleton", Path(d) / "khong-co").returncode == 2
        write_run(Path(d) / "one", {"home": ("/", page())}, {})
        assert run("skeleton", Path(d) / "one").returncode == 2  # cần ít nhất 2 trang


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} test đạt")
