#!/usr/bin/env python3
"""Test offline cho web-qa-gate v1.3: hạng mục 13 (tương tác), 14 (bố cục, landmark), 15 (Open Graph), cờ --tabs --resume --sample --cache,
phủ ảnh chụp, dọn Chrome mồ côi. Không gọi mạng ngoài: trang thử nằm ở tests/fixtures/web và chạy trên 127.0.0.1 (cổng ngẫu nhiên).
Các test cần Chrome và node tự bỏ qua khi máy thiếu (in "bỏ test ...").
Chạy: python3 -B -E tests/test_qa_gate_v13.py   hoặc   python3 -m pytest tests -q
Ca hỏng thật lấy từ bằng chứng của đợt rà 16–24/10/2026:
  menu_invisible: hamburger vô hình trên production và staging nhiều ngày (phiên 6cae27d5, 18/10)
  slider_covered, slider_dead: nút slide mobile bấm không được, vòng kiểm đầu bằng slick-current ra dương tính giả (phiên 106e7e1d, 22/10)
  lưới thiếu ô, hai CTA cùng href: lỗi lưới vẫn còn khi bàn giao (cro16)
  landmark_bad: menu Max Mega Menu nằm trong widget_text, không có nav
"""
import functools
import http.server
import json
import os
import shutil
import socketserver
import struct
import subprocess
import sys
import tempfile
import threading
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures"
WEB = FX / "web"
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import qa_extra as x  # noqa: E402
import qa_gate as q  # noqa: E402

NODE = shutil.which("node")


def have_chrome():
    if not NODE:
        return False
    p = subprocess.run([NODE, "-e", "import('" + (SCRIPTS / "_cdp.mjs").as_uri() + "').then(m=>{m.chromeBin()}).catch(()=>process.exit(3))"], capture_output=True)
    return p.returncode == 0


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class FixtureServer:
    """Server tĩnh trên 127.0.0.1, cổng do hệ điều hành chọn (không đụng cổng của phiên khác)."""

    def __enter__(self):
        self.srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(WEB)))
        self.srv.daemon_threads = True
        self.base = f"http://127.0.0.1:{self.srv.server_address[1]}"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def run_node(script, *argv, timeout=240):
    return subprocess.run([NODE, str(SCRIPTS / script), *argv], capture_output=True, text=True, timeout=timeout)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


# ---------- Thuần Python ----------

def test_color_contrast():
    assert x.parse_color("rgb(10, 61, 145)") == (10.0, 61.0, 145.0, 1.0)
    assert x.parse_color("rgba(0, 0, 0, 0)")[3] == 0 and x.is_transparent("transparent") and x.is_transparent("")
    assert x.parse_color("#abc") == (170, 187, 204, 1.0) and x.parse_color("#aabbcc80")[3] > 0.49
    assert round(x.contrast("#000", "#fff"), 1) == 21.0
    assert 1.9 < x.contrast("#bbbbbb", "#ffffff") < 1.95
    assert x.contrast("rgb(255, 255, 255)", "rgb(255, 255, 255)") == 1.0
    assert x.contrast("zzz", "#fff") is None
    assert x.same_color("rgb(11, 95, 255)", "#0b5fff") and not x.same_color("rgb(255, 0, 170)", "#0b5fff")
    assert x.large_text(24, 400) and x.large_text(19, 700) and not x.large_text(16, 700)


def menu_row(**m):
    base = {"found": True, "sel": "button.mega-menu-toggle", "w": 44, "h": 44, "bg": "rgb(255, 255, 255)",
            "ink": [{"kind": "bg", "on": "span.bar", "color": "rgb(34, 34, 34)"}], "links": 1, "linksAfter": 5}
    base.update(m)
    return {"kind": "page", "name": "home", "vw": 390, "menu": base}


def test_interact_menu():
    ok = x.check_interact([menu_row()])
    assert ok["status"] == "PASS", ok
    # Ca thật 18/10: vạch hamburger trong suốt, nút vẫn có kích thước.
    invisible = x.check_interact([menu_row(ink=[])])
    assert invisible["status"] == "FAIL" and "trong suốt" in invisible["findings"][0]["issue"]
    # Vạch cùng màu nền.
    white = x.check_interact([menu_row(ink=[{"kind": "bg", "on": "span.bar", "color": "rgb(255, 255, 255)"}])])
    assert white["status"] == "FAIL" and "cùng màu nền" in white["findings"][0]["issue"]
    # Bấm mà số link nhìn thấy không tăng.
    dead = x.check_interact([menu_row(linksAfter=1)])
    assert dead["status"] == "FAIL" and "không tăng" in dead["findings"][0]["issue"]
    # Không thấy nút: khai selector thì FAIL, không khai thì WARN.
    assert x.check_interact([menu_row(found=False, declared=True, existsHidden=True, hiddenSel="button.t")])["status"] == "FAIL"
    assert x.check_interact([menu_row(found=False, declared=False)])["status"] == "WARN"
    assert x.check_interact([])["status"] == "SKIP"
    assert x.check_interact([{"kind": "page", "name": "a", "vw": 390, "err": "timeout"}])["status"] == "SKIP"


def slider_row(**s):
    base = {"selector": "#slider", "found": True, "btn": True, "btnSel": "button.slick-next", "items": 4, "before": [0], "after": [1], "disabled": False, "covered": []}
    base.update(s)
    return {"kind": "page", "name": "home", "vw": 390, "sliders": [base]}


def test_interact_slider():
    assert x.check_interact([slider_row()])["status"] == "PASS"
    # Ca thật 22/10: bấm mũi tên mà tập thẻ nhìn thấy không đổi (kiểm bằng class slick-current sẽ báo đạt).
    dead = x.check_interact([slider_row(after=[0])])
    assert dead["status"] == "FAIL" and "không đổi tập thẻ" in dead["findings"][0]["issue"]
    cover = x.check_interact([slider_row(covered=["center bị div.cover che"], after=[0])])
    assert cover["status"] == "FAIL" and "bị che" in cover["findings"][0]["issue"] and len(cover["findings"]) == 1
    # Nút disabled (đã tới thẻ cuối) thì tập thẻ không đổi là bình thường.
    assert x.check_interact([slider_row(after=[0], disabled=True)])["status"] == "PASS"
    assert x.check_interact([slider_row(items=0, before=[], after=[])])["status"] == "WARN"
    assert x.check_interact([slider_row(found=False)])["status"] == "WARN"


def test_interact_states_and_kit():
    node = lambda sel, **st: {"sel": sel, "text": "t", "base": {"color": "rgb(10, 61, 145)", "bg": "rgb(255, 255, 255)", "fs": 16, "fw": 400}, "states": st}
    same = {"changed": [], "color": "rgb(10, 61, 145)", "bg": "rgb(255, 255, 255)", "fs": 16, "fw": 400}
    good = {"changed": ["color"], "color": "rgb(176, 0, 32)", "bg": "rgb(255, 255, 255)", "fs": 16, "fw": 400}
    pale = {"changed": ["color"], "color": "rgb(187, 187, 187)", "bg": "rgb(255, 255, 255)", "fs": 16, "fw": 400}
    row = {"kind": "page", "name": "p", "vw": 1366, "states": [{"selector": "a", "matched": 3, "nodes": [
        node("a.good", hover=good, focus=good), node("a.lowc", hover=pale), node("a.dead", hover=same, focus=same)]}]}
    r = x.check_interact([row])
    issues = {(f["level"], f["issue"].split(": ")[-1]) for f in r["findings"]}
    assert r["status"] == "FAIL"
    assert ("FAIL", "tương phản ở :hover dưới ngưỡng") in issues
    assert ("WARN", "trạng thái :hover không đổi kiểu hiển thị") in issues
    assert ("FAIL", "trạng thái :focus không đổi kiểu hiển thị") in issues, issues  # focus không đổi là lỗi a11y
    low = [f for f in r["findings"] if "tương phản" in f["issue"]][0]
    assert low["examples"][0].startswith("a.lowc") and "1.92" in low["examples"][0]
    # Chữ lớn dùng ngưỡng 3:1.
    big = {**pale, "color": "rgb(140, 140, 140)", "fs": 28}
    assert x.check_interact([{**row, "states": [{"selector": "h", "matched": 1, "nodes": [node("h.x", hover=big)]}]}])["status"] == "PASS"
    assert x.check_interact([{**row, "states": [{"selector": "a", "matched": 0, "nodes": []}]}])["status"] == "WARN"
    # 13d màu kit.
    btn = lambda sel, bg: {"sel": sel, "text": "Nút", "bg": bg, "color": "rgb(255, 255, 255)", "border": "rgb(0, 0, 0)", "borderW": 0, "bgImage": False}
    brow = {"kind": "page", "name": "p", "vw": 1366, "buttons": [btn("a.k1", "rgb(11, 95, 255)"), btn("a.off", "rgb(255, 0, 170)")]}
    cfg = {"kit_button_colors": {"colors": ["#0b5fff", "#ff7a00"]}}
    r = x.check_interact([brow], cfg)
    assert r["status"] == "FAIL" and "1 nút không dùng màu kit" in r["findings"][0]["issue"] and "a.off" in r["findings"][0]["examples"][0]
    assert x.check_interact([{**brow, "buttons": brow["buttons"][:1]}], cfg)["status"] == "PASS"
    # Chiều ngược: accordion mang nền màu kit (site mẫu 18/10: nút kit hiện ở accordion, mũi tên slick, facade video, 3 lượt sửa).
    nc = [{"sel": "button.acc", "text": "FAQ", "bg": "rgb(255, 122, 0)", "bgImage": False}, {"sel": "button.plain", "text": "Đóng", "bg": "rgba(0, 0, 0, 0)", "bgImage": False}]
    r = x.check_interact([{**brow, "buttons": brow["buttons"][:1], "non_cta": nc}], cfg)
    assert r["status"] == "WARN" and "không phải CTA mang nền màu kit" in r["findings"][0]["issue"] and len(r["findings"][0]["examples"]) == 1, r
    nocfg = x.check_interact([brow], {})
    assert nocfg["status"] == "SKIP" and any("kit_button_colors" in n for n in nocfg["notes"])


def test_layout_checks():
    lay = {"grids": [{"sel": "div#g1", "n": 4, "cols": 3, "rows": [3, 1], "empty": 0},
                     {"sel": "div#g2", "n": 3, "cols": 3, "rows": [3], "empty": 1},
                     {"sel": "div#g3", "n": 5, "cols": 3, "rows": [2, 3], "empty": 0}],
           "claims": [{"heading": "#claim", "text": "5 lý do", "claimed": 5, "cards": 4}, {"heading": "#ok", "text": "3 bước", "claimed": 3, "cards": 3},
                      {"heading": "#none", "missing": "heading"}],
           "ctas": [{"section": "section#cta", "href": "https://mau.vn/lien-he/", "labels": ["Nhận tư vấn", "Liên hệ ngay"]},
                    {"section": "section#dup", "href": "https://mau.vn/a/", "labels": ["Mua", "Mua"]}]}
    r = x.check_layout([{"kind": "page", "name": "home", "vw": 1366, "layout": lay}])
    by = {(f["item"], f["level"]) for f in r["findings"]}
    assert r["status"] == "FAIL"
    # Đặc tả ui-2 đã duyệt: nhóm lưới, CTA trùng link, cặp VI/EN là WARN vì dễ báo giả (cột đệm rỗng, lưới masonry). Claude xem ảnh từng dòng.
    assert ("14a", "WARN") in by and ("14a", "FAIL") not in by
    warns14a = [f["issue"] for f in r["findings"] if f["item"] == "14a"]
    assert any("ô trống" in i for i in warns14a) and any("thiếu ô giữa các hàng" in i for i in warns14a) and any("hàng cuối" in i for i in warns14a)
    claims = [f for f in r["findings"] if f["item"] == "14b"]
    assert [f["level"] for f in claims] == ["FAIL", "WARN"] and "heading nói 5, thấy 4 thẻ" in claims[0]["issue"]
    ctas = {f["level"] for f in r["findings"] if f["item"] == "14c"}
    assert ctas == {"WARN"}
    clean = {"grids": [{"sel": "g", "n": 6, "cols": 3, "rows": [3, 3], "empty": 0}], "claims": [], "ctas": []}
    assert x.check_layout([{"kind": "page", "name": "a", "vw": 390, "layout": clean}])["status"] == "PASS"
    assert x.check_layout([])["status"] == "SKIP"
    # 14d cặp VI/EN
    sig = {"h1": 1, "h2": 3, "h3": 0, "forms": 1, "sections": 6, "buttons": 4, "images": 8, "paragraphs": 20, "links": 40, "grids": [6]}
    pair = lambda en: {"kind": "pair", "name": "/ và /en/", "vw": 1366, "vi": {"status": 200, "sig": sig}, "en": {"status": 200, "sig": en}}
    assert x.check_layout([pair(dict(sig))])["status"] == "PASS"
    miss = x.check_layout([pair({**sig, "grids": [4]})])
    assert miss["status"] == "WARN" and "VI [6], EN [4]" in miss["findings"][0]["issue"]
    assert x.check_layout([pair({**sig, "h2": 2})])["findings"][0]["level"] == "WARN"
    assert x.check_layout([pair({**sig, "paragraphs": 12})])["status"] == "WARN"
    assert x.check_layout([{**pair(sig), "en": {"status": 404, "sig": None}}])["status"] == "FAIL"


def lm(**kw):
    base = {"main": 1, "mainSel": ["main#main"], "banner": 1, "contentinfo": 1, "skip": True,
            "h1": [{"in": "main", "text": "T"}], "navs": [{"sel": "nav#menu", "tag": "nav", "role": "", "label": "Chính", "links": 5, "in": "header"}],
            "menu": {"sel": "nav#menu", "tag": "nav", "role": "", "inNav": True, "links": 5, "in": "header", "widgetText": False}}
    base.update(kw)
    return {"name": "home", "vw": 1366, "status": 200, "landmarks": base}


def test_landmarks():
    assert x.check_layout([], [lm()])["status"] == "PASS"
    # Ca thật: menu của Max Mega Menu nằm trong widget_text (div), trang có 2 main và h1 ngoài main.
    bad = lm(main=2, mainSel=["main", "main"], h1=[{"in": "", "text": "T"}], navs=[],
             menu={"sel": "div#mega-menu-wrap-primary.mega-menu-wrap", "tag": "div", "role": "", "inNav": False, "links": 3, "in": "header", "widgetText": True}, skip=False)
    r = x.check_layout([], [bad])
    issues = " | ".join(f["issue"] for f in r["findings"])
    assert r["status"] == "FAIL"
    assert "2 phần tử main" in issues and "h1 nằm ngoài main" in issues and "widget_text" in issues and "skip link" in issues, issues
    assert x.check_layout([], [lm(h1=[])])["findings"][0]["issue"].startswith("1366px: có 0 thẻ h1")
    two_nav = lm(navs=[{"sel": "nav.a", "tag": "nav", "label": "", "links": 3}, {"sel": "nav.b", "tag": "nav", "label": "", "links": 3}])
    assert x.check_layout([], [two_nav])["status"] == "WARN"
    assert x.check_layout([], [{**lm(), "status": 500}])["status"] == "FAIL"


def png(w, h):
    raw = b"".join(b"\x00" + b"\x80\x80\x80" * w for _ in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def jpeg(w, h):
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", h, w) + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"


def webp_x(w, h):
    return b"RIFF" + struct.pack("<I", 22) + b"WEBPVP8X" + struct.pack("<I", 10) + b"\x00\x00\x00\x00" + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")


def test_image_dims():
    assert x.image_dims(png(1200, 630)) == (1200, 630)
    assert x.image_dims(jpeg(1200, 675)) == (1200, 675)
    assert x.image_dims(webp_x(1200, 675)) == (1200, 675)
    assert x.image_dims(b"GIF89a" + struct.pack("<HH", 10, 20)) == (10, 20)
    assert x.image_dims(b"khong phai anh") is None and x.image_dims(b"") is None
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "a.png"
        f.write_bytes(png(40, 20))
        p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_extra.py"), "dims", str(f)], capture_output=True, text=True)
        assert p.returncode == 0 and p.stdout.strip() == "40x20"
        f.write_bytes(b"x")
        assert subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_extra.py"), "dims", str(f)], capture_output=True).returncode == 1


def og_page(name, head, status=200, url=None):
    html = f'<!doctype html><html><head><title>t</title>{head}</head><body></body></html>'
    return {"name": name, "url": url or f"https://mau.vn/{name}/", "status": status, "html": html, "parsed": q.parse_page(html)}


GOOD_OG = ('<link rel="canonical" href="https://mau.vn/ok/"><meta property="og:title" content="T"><meta property="og:description" content="D">'
           '<meta property="og:url" content="https://mau.vn/ok/"><meta property="og:type" content="article">'
           '<meta property="og:image" content="https://mau.vn/u/anh.jpg"><meta name="twitter:card" content="summary_large_image">'
           '<meta name="twitter:image" content="https://mau.vn/u/anh.jpg">')


def test_og():
    img = {"ok": {"url": "https://mau.vn/u/anh.jpg", "code": "200", "content_type": "image/jpeg", "bytes": 90000, "w": 1200, "h": 675}}
    r = x.check_og([og_page("ok", GOOD_OG)], img, "mau.vn")
    assert r["status"] == "PASS", r
    # Thiếu og:image và twitter:image (chưa có trong gate bản 1.2).
    miss = x.check_og([og_page("none", '<meta property="og:title" content="T">')], None, "mau.vn")
    issues = [f["issue"] for f in miss["findings"]]
    assert miss["status"] == "FAIL" and "thiếu og:image" in issues and "thiếu cả og:image lẫn twitter:image" in issues
    # Đường dẫn tương đối, SVG, WebP.
    rel = x.check_og([og_page("rel", GOOD_OG.replace("https://mau.vn/u/anh.jpg", "/u/anh.jpg"))], None, "mau.vn")
    assert rel["status"] == "FAIL" and "tương đối" in rel["findings"][0]["issue"]
    svg = x.check_og([og_page("svg", GOOD_OG.replace("anh.jpg", "anh.svg"))], None, "mau.vn")
    assert svg["status"] == "FAIL" and "SVG" in svg["findings"][0]["issue"]
    webp = x.check_og([og_page("webp", GOOD_OG.replace("anh.jpg", "anh.webp"))], None, "mau.vn")
    assert webp["status"] == "WARN" and "JPEG hoặc PNG" in webp["findings"][0]["issue"]
    # Ảnh: 404, không phải ảnh, nhỏ, sai tỉ lệ, nặng.
    base = {"url": "https://mau.vn/u/anh.jpg", "code": "200", "content_type": "image/jpeg", "bytes": 1000, "w": 1200, "h": 675}
    pg = lambda: [og_page("ok", GOOD_OG)]
    assert x.check_og(pg(), {"ok": {**base, "code": "404"}}, "mau.vn")["status"] == "FAIL"
    assert x.check_og(pg(), {"ok": {**base, "content_type": "text/html"}}, "mau.vn")["status"] == "FAIL"
    small = x.check_og(pg(), {"ok": {**base, "w": 600, "h": 338}}, "mau.vn")
    assert small["status"] == "WARN" and "dưới 1200px" in small["findings"][0]["issue"]
    square = x.check_og(pg(), {"ok": {**base, "w": 1200, "h": 1200}}, "mau.vn")
    assert square["status"] == "WARN" and "tỉ lệ 1.00" in square["findings"][0]["issue"]
    assert "5 MB" in x.check_og(pg(), {"ok": {**base, "bytes": 6 * 1024 * 1024}}, "mau.vn")["findings"][0]["issue"]
    # og:url khác canonical, thiếu twitter:card, host ảnh khác.
    off = x.check_og([og_page("ok", GOOD_OG.replace('og:url" content="https://mau.vn/ok/"', 'og:url" content="https://mau.vn/khac/"').replace('<meta name="twitter:card" content="summary_large_image">', ""))], None, "mau.vn")
    assert any("og:url khác canonical" in f["issue"] for f in off["findings"]) and any("twitter:card" in f["issue"] for f in off["findings"])
    assert any("host khác" in f["issue"] for f in x.check_og([og_page("ok", GOOD_OG)], None, "stg.mau.vn")["findings"])
    assert x.check_og([og_page("x", "", status=404)], None)["status"] == "SKIP"
    # ghi chú ảnh dùng chung
    many = [og_page(f"p{i}", GOOD_OG.replace("/ok/", f"/p{i}/")) for i in range(3)]
    assert any("dùng chung một og:image" in n for n in x.check_og(many, None, "mau.vn")["notes"])


def test_tile_coverage():
    row = lambda n, ph, **kw: {"name": "home", "vw": 360, "vh": 800, "shots": [{"file": f"h_{i}.jpg", "i": i, "y": 0, "page_h": ph} for i in range(n)], **kw}
    assert x.check_tile_coverage([row(5, 4000)]) == []
    # Ca thật: tiles treo, chụp được 2 màn trên trang cao 4000 px (cần 5).
    r = x.check_tile_coverage([row(2, 4000)])
    assert r[0]["level"] == "FAIL" and "chụp 2/5 màn" in r[0]["issue"]
    assert x.check_tile_coverage([row(2, 4000)], "sample")[0]["level"] == "WARN"
    cap = x.check_tile_coverage([row(12, 20000, tiles_needed=25, tiles_cap=12)])
    assert cap[0]["level"] == "WARN" and "tiles_max" in cap[0]["issue"]
    assert x.check_tile_coverage([{"name": "a", "vw": 360, "vh": 800, "shots": []}])[0]["level"] == "FAIL"
    assert x.check_tile_coverage([{"name": "a", "vw": 360, "vh": 800}]) == []  # variant không chụp ảnh
    # Nối vào check_ui_visual: thiếu màn thì hạng mục FAIL dù Jev không gắn cờ ảnh nào.
    jev = [{"id": "home|360|0", "answers": {k: {"p_yes": 0.1} for k in q.NOULS}}]
    gates = {k: {"thr": 0.9} for k in q.NOULS}
    r = q.check_ui_visual(jev, gates, browser_rows=[row(2, 4000)])
    assert r["status"] == "FAIL" and "chụp thiếu màn" in r["summary"]
    assert q.check_ui_visual(jev, gates, browser_rows=[row(5, 4000)])["status"] == "PASS"
    assert q.check_ui_visual(jev, gates, browser_rows=[row(2, 4000)], tiles_mode="sample")["status"] == "WARN"


def test_apply_sample():
    urls = [{"name": f"u{i}"} for i in range(20)] + [{"name": "home", "always": True}]
    a = x.apply_sample(urls, "5", seed=1)
    assert len(a) == 5 and "home" in [u["name"] for u in a]
    assert a == x.apply_sample(urls, "5", seed=1) and a != x.apply_sample(urls, "5", seed=2)
    assert [u["name"] for u in a] == [u["name"] for u in urls if u in a]  # giữ thứ tự gốc
    assert len(x.apply_sample(urls, "10%", seed=1)) == 3  # ceil(21 * 0,1)
    assert len(x.apply_sample(urls, "100", seed=1)) == 21 and x.apply_sample(urls, None) == urls
    assert len(x.apply_sample(urls, "1", seed=1)) == 1  # mẫu nhỏ hơn số URL always: vẫn giữ URL always
    try:
        x.apply_sample(urls, "abc")
        raise AssertionError("phải báo lỗi")
    except ValueError:
        pass


def test_overflow_variants():
    row = lambda var, doc, cache="": {"name": "home", "vw": 390, "docW": doc, "innerW": max(doc, 390), "variant": var, "cache": cache,
                                      "overflow": [{"s": "div.x", "r": doc, "n": 1}] if doc > 390 else []}
    both = q.check_overflow([row("cached", 410, "hit"), row("nc", 390, "miss")])
    assert both["status"] == "FAIL" and both["findings"][0]["variant"] == "cached" and both["findings"][0]["cache"] == "hit"
    assert any("Tràn chỉ ở bản cached" in n for n in both["notes"])
    assert not any("--cache both" in n for n in both["notes"])
    one = q.check_overflow([row("nc", 390)])
    assert one["status"] == "PASS" and any("Chỉ đo bản nc" in n for n in one["notes"])
    default = q.check_overflow([row("default", 390)])
    assert any("chưa rõ đo bản có cache" in n for n in default["notes"])


def test_form_lead_path_note():
    ok = {"name": "p", "url": "https://mau.vn/p/", "status": 200, "html": (FX / "page_ok.html").read_text(encoding="utf-8")}
    notes = q.check_form([ok])["notes"]
    assert any("form → mail → Sheet → CMS → hộp thư thật" in n for n in notes)
    assert q.check_form([])["status"] == "SKIP"


def test_run_plan_and_flags():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cfg = {"site": "mau.vn", "base": "https://mau.vn", "widths": [360, 1366],
               "urls": [{"name": f"u{i}", "path": f"/{i}/"} for i in range(10)] + [{"name": "home", "path": "/", "always": True}]}
        (t / "qa.json").write_text(json.dumps(cfg), encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "run", "--config", str(t / "qa.json"), "--out", str(t / "out"), *a],
                                        capture_output=True, text=True)
        p = run("--plan", "--sample", "3", "--seed", "4", "--cache", "both", "--tabs", "3")
        assert p.returncode == 0, p.stderr
        plan = json.loads(p.stdout)
        assert len(plan["urls"]) == 3 and "home" in plan["urls"] and plan["variants"] == ["cached", "nc"]
        assert plan["browser_runs"] == 3 * 2 * 2 and plan["total_urls"] == 11 and plan["tabs"] == 3 and plan["interact"] is False
        assert not (t / "out").exists(), "--plan không được ghi file"
        assert json.loads(run("--plan", "--sample", "3", "--seed", "4").stdout)["urls"] == plan["urls"]
        assert run("--plan", "--tabs", "9").returncode == 2
        assert run("--plan", "--sample", "abc").returncode == 2
        assert run("--plan", "--cache", "zzz").returncode == 2
        assert json.loads(run("--plan").stdout)["variants"] == ["default"]


def test_help_and_exit_codes():
    if not NODE:
        print("bỏ test --help của .mjs: thiếu node")
    else:
        for f in ("browser_probe.mjs", "interact_probe.mjs", "landmarks.mjs", "chrome_cleanup.mjs"):
            p = run_node(f, "--help")
            assert p.returncode == 0 and f in p.stdout, (f, p.stderr)
        for f in ("browser_probe.mjs", "interact_probe.mjs", "landmarks.mjs"):
            assert run_node(f).returncode == 2, f  # thiếu --job hoặc --out
        assert run_node("chrome_cleanup.mjs", "--lạ").returncode == 2
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / "bad.json"
            bad.write_text("{khong phai json", encoding="utf-8")
            assert run_node("browser_probe.mjs", "--job", str(bad), "--out", str(Path(t) / "o.jsonl")).returncode == 2
            assert run_node("browser_probe.mjs", "--job", str(bad), "--out", str(Path(t) / "o.jsonl"), "--tabs", "0").returncode == 2
            ok = Path(t) / "ok.json"
            ok.write_text(json.dumps({"pages": [{"name": "a", "url": "http://x"}]}), encoding="utf-8")
            assert run_node("browser_probe.mjs", "--job", str(ok), "--out", str(Path(t) / "o.jsonl"), "--cache", "zzz").returncode == 2
    p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_extra.py"), "--help"], capture_output=True, text=True)
    assert p.returncode == 0 and "Hạng mục 13 đến 15" in p.stdout
    assert subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_extra.py")], capture_output=True).returncode == 2
    assert subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "check", "og", "--help"], capture_output=True).returncode == 0


def test_check_cli_new_categories():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "html").mkdir()
        (t / "html" / "ok.html").write_text(f"<html><head>{GOOD_OG}</head></html>", encoding="utf-8")
        (t / "html" / "none.html").write_text("<html><head><title>x</title></head></html>", encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "check", *a], capture_output=True, text=True)
        p = run("og", str(t / "html"), "--canonical-host", "mau.vn")
        assert p.returncode == 0 and json.loads(p.stdout)["status"] == "FAIL"
        (t / "i.jsonl").write_text(json.dumps(menu_row(ink=[])) + "\n", encoding="utf-8")
        assert json.loads(run("interact", str(t / "i.jsonl")).stdout)["status"] == "FAIL"
        (t / "l.jsonl").write_text(json.dumps(lm(main=0)) + "\n", encoding="utf-8")
        assert json.loads(run("layout", str(t / "i.jsonl"), "--landmarks", str(t / "l.jsonl")).stdout)["status"] == "FAIL"


# ---------- Cần Chrome ----------

def test_orphan_sweep():
    if not NODE:
        print("bỏ test dọn Chrome mồ côi: thiếu node")
        return
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        done = subprocess.Popen([sys.executable, "-c", "pass"])
        done.wait()
        orphan, live = t / "wqg-orphan", t / "wqg-live"
        for d, owner in ((orphan, done.pid), (live, os.getpid())):
            d.mkdir()
            (d / "owner.pid").write_text(str(owner))
        # Tiến trình giả có --user-data-dir trỏ vào hai thư mục. Chỉ cái của chủ đã chết bị giết.
        sleeper = lambda d: subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)", f"--user-data-dir={d}"])
        a, b = sleeper(orphan), sleeper(live)
        try:
            dry = run_node("chrome_cleanup.mjs", "--tmp", str(t))
            assert dry.returncode == 0 and "wqg-orphan" in dry.stdout and "wqg-live" not in dry.stdout and "Thêm --apply" in dry.stdout, dry.stdout
            assert a.poll() is None and orphan.exists(), "dry-run không được giết hay xoá"
            applied = run_node("chrome_cleanup.mjs", "--tmp", str(t), "--apply")
            assert applied.returncode == 0 and "đã dọn" in applied.stdout
            a.wait(timeout=10)
            assert not orphan.exists() and live.exists() and b.poll() is None, "chỉ dọn thư mục mồ côi, giữ Chrome của lượt đang chạy"
        finally:
            for p in (a, b):
                if p.poll() is None:
                    p.kill()


def test_browser_probe_flags():
    if not have_chrome():
        print("bỏ test browser_probe: thiếu Chrome hoặc node")
        return
    with FixtureServer() as srv, tempfile.TemporaryDirectory() as t:
        t = Path(t)
        pages = [{"name": "menu_ok", "url": f"{srv.base}/menu_ok.html"}, {"name": "layout", "url": f"{srv.base}/layout.html"}]
        job = {"pages": pages, "widths": [360, 1366], "block": ["*googletagmanager.com*"], "tracking": ["*googletagmanager.com*"],
               "shots_dir": str(t / "shots"), "wait": 200, "focus_widths": [], "axe_widths": [], "hide_fixed": True}
        (t / "job.json").write_text(json.dumps(job), encoding="utf-8")
        out = t / "b.jsonl"
        p = run_node("browser_probe.mjs", "--job", str(t / "job.json"), "--out", str(out), "--tabs", "2", "--cache", "both")
        assert p.returncode == 0, p.stderr
        rows = jl(out)
        assert len(rows) == 8 and {r["variant"] for r in rows} == {"cached", "nc"}
        assert all(r["docW"] == r["vw"] for r in rows) and all(r["tracking"]["leaked"] == [] for r in rows)
        shots = [r for r in rows if r.get("shots")]
        assert shots and all(r["variant"] == "cached" for r in shots), "ảnh chụp chỉ ở variant đầu"
        assert all(len(r["shots"]) >= r["tiles_needed"] for r in shots), "tiles mặc định là đủ page_h/vh"
        # --list và --resume: giữ dòng tốt, bỏ dòng lỗi, đo lại đúng dòng thiếu.
        plan = lambda *a: json.loads(run_node("browser_probe.mjs", "--job", str(t / "job.json"), "--out", str(out), "--cache", "both", "--list", *a).stdout)
        assert plan("--resume")["todo"] == [] and plan("--resume")["skipped"] == 8
        keep = [r for r in rows if not (r["name"] == "layout" and r["vw"] == 1366)]
        broken = {"name": "layout", "url": pages[1]["url"], "vw": 1366, "variant": "cached", "err": "timeout"}
        out.write_text("".join(json.dumps(r) + "\n" for r in keep + [broken]), encoding="utf-8")
        todo = plan("--resume")
        assert sorted(todo["todo"]) == ["layout|1366|cached", "layout|1366|nc"] and todo["skipped"] == 6, todo
        p = run_node("browser_probe.mjs", "--job", str(t / "job.json"), "--out", str(out), "--cache", "both", "--resume")
        assert p.returncode == 0, p.stderr
        rows2 = jl(out)
        assert len(rows2) == 8 and not any(r.get("err") for r in rows2), "dòng lỗi phải bị thay bằng dòng đo lại"
        # --sample cố định theo seed.
        s1, s2 = plan("--sample", "1", "--seed", "3"), plan("--sample", "1", "--seed", "3")
        assert s1 == s2 and len(s1["pages"]) == 1
        # Hết giờ mỗi URL: ghi err, Chrome mở lại, lượt quét không dừng.
        out2 = t / "slow.jsonl"
        p = run_node("browser_probe.mjs", "--job", str(t / "job.json"), "--out", str(out2), "--page-timeout", "50")
        r = jl(out2)
        assert p.returncode == 1 and r and all("timeout" in x_.get("err", "") for x_ in r), (p.returncode, r[:1])


def interact_job(base, pages, interact, **kw):
    return {"pages": [{"name": n, "url": f"{base}/{n}.html"} for n in pages], "block": ["*googletagmanager.com*"], "wait": 200, "interact": interact, **kw}


def test_interact_probe_real_failures():
    if not have_chrome():
        print("bỏ test interact_probe: thiếu Chrome hoặc node")
        return
    with FixtureServer() as srv, tempfile.TemporaryDirectory() as t:
        t = Path(t)
        pages = ["menu_ok", "menu_invisible", "menu_dead", "slider_ok", "slider_covered", "slider_dead", "states", "buttons", "layout"]
        sl = lambda p: {"selector": "#slider", "items": ".slide", "page": p, "widths": [390]}
        interact = {"menu_toggle": {}, "sliders": [sl("slider_ok"), sl("slider_covered"), sl("slider_dead")],
                    "changed_selectors": [{"selector": "a", "page": "states"}], "kit_button_colors": {"colors": ["#0b5fff", "#ff7a00"], "widths": [1366]},
                    "count_claims": [{"page": "layout", "heading": "#claim", "cards": "#g1 .rs"}], "layout_widths": [1366]}
        (t / "job.json").write_text(json.dumps(interact_job(srv.base, pages, interact, shots_dir=str(t / "shots"))), encoding="utf-8")
        p = run_node("interact_probe.mjs", "--job", str(t / "job.json"), "--out", str(t / "i.jsonl"))
        assert p.returncode == 0, p.stderr
        rows = jl(t / "i.jsonl")
        res = x.check_interact(rows, interact)
        got = {(f["item"], f["page"], f["level"]) for f in res["findings"]}
        # Ca hỏng thật phải bị bắt.
        assert ("13a", "menu_invisible", "FAIL") in got, res["findings"]       # hamburger vô hình (18/10)
        assert ("13a", "menu_dead", "FAIL") in got                            # bấm không có gì xảy ra
        assert ("13b", "slider_covered", "FAIL") in got                       # mũi tên bị che (22/10)
        assert ("13b", "slider_dead", "FAIL") in got                          # bấm không đổi thẻ (22/10)
        assert ("13c", "states", "FAIL") in got                               # tương phản :hover thấp
        assert ("13d", "buttons", "FAIL") in got                              # nút lệch màu kit
        assert ("13d", "buttons", "WARN") in got                              # accordion mang màu kit (18/10)
        # Trang đúng không bị báo.
        okf = [f for f in res["findings"] if f["page"] in ("menu_ok", "slider_ok") and not (f["item"] == "13a" and f["level"] == "WARN")]
        assert not okf, okf  # trang đúng không bị báo lỗi (trang không có menu chỉ bị nhắc WARN)
        issues = " | ".join(f["issue"] + " " + " ".join(f.get("examples", [])) for f in res["findings"] if f["page"] == "states")
        assert "tương phản ở :hover" in issues and "a.lowc" in issues
        assert "không đổi kiểu hiển thị" in issues  # a.dead
        visited = [r for r in rows if r["name"] == "states" and r.get("states")][0]["states"][0]["nodes"][0]["states"]["visited"]
        assert visited["color"] == "rgb(75, 42, 138)" and visited["changed"], "đọc được màu :visited thật qua CSS.getComputedStyleForNode"
        shots = {r["menu"]["shots"][1] for r in rows if r.get("menu", {}).get("found")}
        assert all((t / "shots" / s).exists() for s in shots), "chụp lúc mở menu"
        lay = x.check_layout(rows, (), interact)
        l_issues = " | ".join(f["issue"] for f in lay["findings"])
        assert lay["status"] == "FAIL" and "ô trống" in l_issues and "heading nói 5, thấy 4 thẻ" in l_issues and "cùng trỏ" in l_issues, l_issues
        assert "hàng cuối chỉ có 1/3 ô" in l_issues


def test_landmarks_and_pairs_probe():
    if not have_chrome():
        print("bỏ test landmarks và cặp VI/EN: thiếu Chrome hoặc node")
        return
    with FixtureServer() as srv, tempfile.TemporaryDirectory() as t:
        t = Path(t)
        job = {"pages": [{"name": n, "url": f"{srv.base}/{n}.html"} for n in ("landmarks_ok", "landmarks_bad")], "landmark_widths": [1366], "wait": 200}
        (t / "job.json").write_text(json.dumps(job), encoding="utf-8")
        p = run_node("landmarks.mjs", "--job", str(t / "job.json"), "--out", str(t / "l.jsonl"))
        assert p.returncode == 0, p.stderr
        rows = jl(t / "l.jsonl")
        ok = x.check_layout([], [r for r in rows if r["name"] == "landmarks_ok"])
        assert ok["status"] == "PASS", ok["findings"]
        bad = x.check_layout([], [r for r in rows if r["name"] == "landmarks_bad"])
        text = " | ".join(f["issue"] for f in bad["findings"])
        assert bad["status"] == "FAIL" and "2 phần tử main" in text and "widget_text" in text and "h1 nằm ngoài main" in text, text
        # Chế độ --url, menu khai selector.
        p = run_node("landmarks.mjs", "--url", f"{srv.base}/landmarks_ok.html", "--widths", "390", "--menu", "#menu-chinh", "--out", str(t / "u.jsonl"))
        assert p.returncode == 0 and jl(t / "u.jsonl")[0]["landmarks"]["menu"]["declared"] is True
        # Cặp VI/EN lệch số thẻ trong lưới.
        pj = interact_job(srv.base, [], {"pairs": [{"name": "vi-en", "vi": f"{srv.base}/pair_vi.html", "en": f"{srv.base}/pair_en.html"}]})
        (t / "pj.json").write_text(json.dumps(pj), encoding="utf-8")
        p = run_node("interact_probe.mjs", "--job", str(t / "pj.json"), "--out", str(t / "p.jsonl"))
        assert p.returncode == 0, p.stderr
        res = x.check_layout(jl(t / "p.jsonl"))
        assert res["status"] == "WARN" and "VI [6], EN [4]" in res["findings"][0]["issue"], res["findings"]


def test_run_end_to_end_with_new_categories():
    if not have_chrome():
        print("bỏ test run đầy đủ: thiếu Chrome hoặc node")
        return
    with FixtureServer() as srv, tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cfg = {"site": "mau.local", "env": "staging", "base": srv.base, "widths": [390, 1366], "wait": 200,
               "urls": [{"name": "menu_invisible", "path": "/menu_invisible.html", "always": True}, {"name": "layout", "path": "/layout.html"}],
               "ui_visual": {"tiles": "all"},
               "interact": {"menu_toggle": {}, "count_claims": [{"page": "layout", "heading": "#claim", "cards": "#g1 .rs"}], "layout_widths": [1366]}}
        (t / "qa.json").write_text(json.dumps(cfg), encoding="utf-8")
        p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "run", "--config", str(t / "qa.json"), "--out", str(t / "out"),
                            "--cache", "both", "--tabs", "2"], capture_output=True, text=True, timeout=600)
        assert p.returncode == 1, (p.returncode, p.stdout, p.stderr[-400:])
        rep = json.loads((t / "out" / "report.json").read_text(encoding="utf-8"))
        st = {k: v["status"] for k, v in rep["categories"].items()}
        assert list(st) == [k for k, _ in q.CATS] and len(st) == 14
        assert st["interact"] == "FAIL" and st["layout"] == "FAIL" and st["og"] == "FAIL" and st["overflow"] == "PASS", st
        assert any("13a" == f["item"] for f in rep["categories"]["interact"]["findings"])
        md = (t / "out" / "report.md").read_text(encoding="utf-8")
        assert "| Tương tác và trạng thái | FAIL |" in md and "| Toàn vẹn bố cục | FAIL |" in md and "| Open Graph | FAIL |" in md
        assert (t / "out" / "raw" / "interact.jsonl").exists() and (t / "out" / "raw" / "landmarks.jsonl").exists() and (t / "out" / "raw" / "og_images.jsonl").exists() is True
        # --resume chạy lại không đo lại dòng đã tốt.
        before = (t / "out" / "raw" / "browser.jsonl").read_text(encoding="utf-8")
        p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "run", "--config", str(t / "qa.json"), "--out", str(t / "out"),
                            "--cache", "both", "--resume", "--skip", "http,interact,og"], capture_output=True, text=True, timeout=600)
        assert p.returncode == 1 and (t / "out" / "raw" / "browser.jsonl").read_text(encoding="utf-8") == before


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} test đạt")
