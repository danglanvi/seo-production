#!/usr/bin/env python3
"""Test offline cho qa_gate.py: không cần mạng, không cần trình duyệt, không cần model.
Chạy: python3 -B -E tests/test_qa_gate.py   (Pillow tuỳ chọn cho test đệm ảnh; node tuỳ chọn cho test cú pháp .mjs)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures"
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import qa_gate as q  # noqa: E402


def page(name, url, status=200, **kw):
    html = (FX / f"{name}.html").read_text(encoding="utf-8")
    return {"name": name, "url": url, "status": status, "html": html, "parsed": q.parse_page(html), **kw}


def browser_row(name, vw, docW, innerW=None, forms=None, axe=None, focus=None, tracking=None, shots=None):
    return {"name": name, "url": f"https://mau.vn/{name}/", "vw": vw, "vh": 800 if vw < 800 else 900, "mobile": vw < 800,
            "docW": docW, "innerW": innerW or max(docW, vw), "overflow": [{"s": "div.mega-menu-wrap", "r": docW, "n": 1}] if docW > vw else [],
            "forms": forms or [], "axe": axe, "focus": focus, "tracking": tracking or {"seen": 0, "blocked": 0, "leaked": []}, "shots": shots or []}


def test_overflow():
    # Giả lập mobile nới innerWidth theo phần tràn: phải so với bề rộng đặt (vw).
    rows = [browser_row("home", 360, 360), browser_row("home", 768, 778), browser_row("home", 1366, 1366)]
    r = q.check_overflow(rows)
    assert r["status"] == "FAIL" and len(r["findings"]) == 1, r
    f = r["findings"][0]
    assert f["width"] == 768 and f["over_px"] == 10 and "mega-menu-wrap" in f["offenders"][0]
    assert q.check_overflow([browser_row("a", 360, 360)])["status"] == "PASS"
    assert q.check_overflow([{"name": "a", "vw": 360, "err": "timeout"}])["status"] == "WARN"
    assert q.check_overflow([])["status"] == "SKIP"
    # Dòng cũ của ux_probe.mjs (W = innerWidth): gán bề rộng đặt theo thứ tự đo thì thấy lỗi 768 bị che.
    legacy = q.records([FX / "ux_legacy.jsonl"])
    blind = q.check_overflow(legacy)
    assert [f["width"] for f in blind["findings"]] == [1366] and any("che" in n for n in blind["notes"])
    fixed = q.check_overflow(legacy, [360, 768, 1366])
    assert sorted((f["width"], f["over_px"]) for f in fixed["findings"]) == [(768, 10), (1366, 60)], fixed


def test_http_and_redirect():
    rows = q.parse_httpcheck_output((FX / "httpcheck.txt").read_text(encoding="utf-8"))
    assert len(rows) == 4 and rows[1]["location"] == "/moi/"
    r = q.check_http(rows)
    assert r["status"] == "FAIL" and [f["path"] for f in r["findings"]] == ["/wp-admin/"]
    lst = q.parse_http_list("# chú thích\n200 /\n301 /cu/ /moi/\n403 /xmlrpc.php\n")
    assert lst[1] == {"expect": 301, "path": "/cu/", "location": "/moi/"} and len(lst) == 3
    rows = [{"path": "/cu/", "expect": 301, "code": "301", "location": "https://mau.vn/khac/", "expect_location": "/moi/"},
            {"path": "/", "expect": 200, "code": "000", "location": ""}]
    r = q.check_http(rows, "https://mau.vn")
    assert len(r["findings"]) == 2 and "000" in r["findings"][1]["note"]
    base = "https://mau.vn"
    ok = q.eval_redirect({"from": "/cu/", "to": "/moi/"}, [{"url": "https://mau.vn/cu/", "code": "301", "location": "https://mau.vn/moi/"},
                                                          {"url": "https://mau.vn/moi/", "code": "200", "location": ""}], base)
    assert ok["level"] == "PASS"
    tmp = q.eval_redirect({"from": "/cu/", "to": "/moi/"}, [{"url": "https://mau.vn/cu/", "code": "302", "location": "/moi/"},
                                                           {"url": "https://mau.vn/moi/", "code": "200", "location": ""}], base)
    assert tmp["level"] == "FAIL" and "302" in tmp["issue"]
    hops3 = [{"url": "https://mau.vn/cu/", "code": "301", "location": "/a/"}, {"url": "https://mau.vn/a/", "code": "301", "location": "/moi/"},
             {"url": "https://mau.vn/moi/", "code": "200", "location": ""}]
    assert q.eval_redirect({"from": "/cu/", "to": "/moi/"}, hops3, base)["level"] == "WARN"
    dead = [{"url": "https://mau.vn/cu/", "code": "301", "location": "/moi/"}, {"url": "https://mau.vn/moi/", "code": "404", "location": ""}]
    assert q.eval_redirect({"from": "/cu/", "to": "/moi/"}, dead, base)["level"] == "FAIL"
    assert q.check_redirect([])["status"] == "SKIP"


def test_canonical():
    ok = page("page_ok", "https://mau.vn/dich-vu/")
    r = q.check_canonical([ok], "mau.vn")
    assert r["status"] == "PASS", r
    bad = page("page_bad", "https://mau.vn/gioi-thieu/")
    r = q.check_canonical([bad], "mau.vn")
    issues = " | ".join(f["issue"] for f in r["findings"])
    assert r["status"] == "FAIL" and "2 thẻ" in issues and "host khác" in issues and "không tự trỏ" in issues, issues
    ni = page("page_noindex", "https://mau.vn/?s=a")
    r = q.check_canonical([ni], "mau.vn")
    assert r["status"] == "PASS" and "noindex" in r["notes"][0]
    # trang index được mà thiếu canonical
    miss = {"name": "x", "url": "https://mau.vn/x/", "status": 200, "html": "<html><head><title>x</title></head></html>"}
    assert q.check_canonical([miss], "mau.vn")["status"] == "FAIL"
    # X-Robots-Tag noindex trong header
    hdr = {**miss, "headers": "HTTP/2 200\nx-robots-tag: noindex\n"}
    assert q.check_canonical([hdr], "mau.vn")["status"] == "PASS"
    # trang 404 không kiểm canonical
    assert q.check_canonical([{**miss, "status": 404}], "mau.vn")["status"] == "SKIP"


def test_schema():
    ok = page("page_ok", "https://mau.vn/dich-vu/", expect_schema=["Organization", "Service"])
    r = q.check_schema([ok], "mau.vn")
    assert r["status"] == "PASS", r  # ImageObject gravatar không tính là host khác
    assert "Service" in ok["schema_types"]
    bad = page("page_bad", "https://mau.vn/gioi-thieu/", expect_schema=["Article"])
    r = q.check_schema([bad], "mau.vn")
    issues = [f["issue"] for f in r["findings"]]
    assert r["status"] == "FAIL"
    assert any("không parse được" in i for i in issues)
    assert any("Person thiếu name" in i for i in issues)
    assert any("tên mặc định 'admin'" in i for i in issues)
    assert any("host khác: prod.mau.vn" in i for i in issues)
    assert any("thiếu loại schema mong đợi: Article" in i for i in issues)
    assert "1/2 khối" in r["summary"]
    # Organization của công ty liên quan mang host khác là hợp lệ; WebPage mang host khác thì cảnh báo
    sister = {"name": "s", "url": "https://mau.vn/", "status": 200, "html": '<script type="application/ld+json">{"@graph":[{"@type":"Organization","@id":"https://cty-me.vn/#org","name":"Công ty mẹ"},{"@type":"WebPage","@id":"https://mau.vn/#webpage"}]}</script>'}
    assert q.check_schema([sister], "mau.vn")["status"] == "PASS"


def test_form():
    ok = page("page_ok", "https://mau.vn/dich-vu/")
    forms = ok["parsed"]["forms"]
    lead = [f for f in forms if not f["search"]]
    assert len(forms) == 2 and len(lead) == 1
    f = lead[0]
    assert f["honeypot"] and f["nonce"] and f["contact"] and [x["name"] for x in f["fields"]] == ["your-name", "your-phone"]
    assert f["fields"][1]["required"]
    r = q.check_form([ok])
    assert r["status"] == "PASS" and "Chưa gửi form thật" in r["notes"][0]
    bad = page("page_bad", "https://mau.vn/gioi-thieu/")
    issues = [x["issue"] for x in q.check_form([bad])["findings"]]
    assert any("honeypot" in i for i in issues) and any("email hay điện thoại" in i for i in issues)
    # form gửi bằng JS (không method, không action) không tính là GET; form GET có action và trường liên hệ thì cảnh báo
    js = '<form id="leadForm"><input name="phone" type="tel"><input name="hp_check" type="text"><button>Gửi</button></form>'
    get = '<form action="/gui/" method="get"><input name="email" type="email"><button>Gửi</button></form>'
    i_js = [x["issue"] for x in q.check_form([{"name": "a", "status": 200, "html": js}])["findings"]]
    i_get = [x["issue"] for x in q.check_form([{"name": "b", "status": 200, "html": get}])["findings"]]
    assert not any("GET" in i for i in i_js) and not any("honeypot" in i for i in i_js), i_js
    assert any("GET" in i for i in i_get)
    # WPForms bản modern: không có honeypot trong HTML, JS thêm token chống spam vào DOM
    wp = '<form id="wpforms-form-1" class="wpforms-form" method="post"><input type="hidden" name="wpforms[id]" value="1"><input type="email" name="wpforms[fields][2]"></form>'
    pg = {"name": "lien-he", "status": 200, "html": wp}
    assert any("honeypot" in x["issue"] for x in q.check_form([pg])["findings"])
    dom = [{"name": "lien-he", "vw": 360, "forms": [{"visible": True, "visibleFields": 1, "hidden": ["wpforms[id]", "wpforms[token]"]}]}]
    r = q.check_form([pg], dom)
    assert r["status"] == "PASS", r
    # DOM: form hiện ở desktop nhưng không khởi tạo ở 360 px
    rows = [browser_row("lien-he", 360, 360, forms=[{"visible": False, "visibleFields": 0}]),
            browser_row("lien-he", 1366, 1366, forms=[{"visible": True, "visibleFields": 3}])]
    r = q.check_form([], rows)
    assert r["status"] == "FAIL" and "360 px" in r["findings"][0]["issue"]
    # lượt gửi thật: chờ kiểm hộp mail, rồi mail-ok thành PASS
    live = {"url": "https://stg.mau.vn/lien-he/", "token": "QA-1", "success_seen": True, "posts": [{"url": "x", "status": 200}]}
    assert q.check_form([ok], (), live)["status"] == "WARN"
    assert q.check_form([ok], (), live, "ok")["status"] == "PASS"
    assert q.check_form([ok], (), live, "missing")["status"] == "FAIL"
    assert q.check_form([ok], (), {**live, "success_seen": False})["status"] == "FAIL"


def test_tracking():
    assert q.is_tracking_url("https://www.googletagmanager.com/gtm.js?id=GTM-AB12CD3")
    assert q.is_tracking_url("https://region1.google-analytics.com/g/collect?v=2")
    assert q.is_tracking_url("https://www.facebook.com/tr?id=123&ev=PageView")
    assert q.is_tracking_url("https://connect.facebook.net/en_US/fbevents.js")
    assert q.is_tracking_url("https://script.google.com/macros/s/abc/exec")
    assert not q.is_tracking_url("https://fonts.googleapis.com/css2?family=Inter")
    assert not q.is_tracking_url("https://www.facebook.com/vidu")
    ok = page("page_ok", "https://mau.vn/dich-vu/")
    assert q.tracking_ids(ok["html"]) == ["GTM-AB12CD3"]
    assert q.tag_present(ok["html"], "re:GTM-[A-Z0-9]+") and not q.tag_present(ok["html"], "G-ZZZZZZZZ")
    r = q.check_tracking([ok], ["GTM-AB12CD3"], [browser_row("dich-vu", 360, 360, tracking={"seen": 3, "blocked": 3, "leaked": []})])
    assert r["status"] == "PASS" and "chặn 3" in r["notes"][1]
    r = q.check_tracking([ok, page("page_bad", "https://mau.vn/gioi-thieu/")], ["GTM-AB12CD3"],
                         [browser_row("x", 360, 360, tracking={"seen": 2, "blocked": 1, "leaked": ["https://sgtm.mau.vn/g/collect"]})])
    assert r["status"] == "FAIL" and len(r["findings"]) == 2
    assert q.check_tracking([ok], [], [])["status"] == "SKIP"


def test_plugins():
    prod = q.parse_plugin_list((FX / "plugins_prod.json").read_text(encoding="utf-8"))
    stg = q.parse_plugin_list((FX / "plugins_stg.tsv").read_text(encoding="utf-8"))
    assert set(prod) == {"contact-form-7", "litespeed-cache", "seo-by-rank-math", "wp-mail-smtp"}
    assert stg["zz-staging-safety"]["status"] == "must-use" and stg["litespeed-cache"]["status"] == "inactive"
    kinds = {f["plugin"]: f["kind"] for f in q.diff_plugins(stg, prod)}
    assert kinds == {"litespeed-cache": "khác trạng thái", "seo-by-rank-math": "khác version",
                     "wp-mail-smtp": "chỉ có ở production", "zz-staging-safety": "chỉ có ở staging"}, kinds
    r = q.check_plugins((FX / "plugins_stg.tsv").read_text(encoding="utf-8"), (FX / "plugins_prod.json").read_text(encoding="utf-8"),
                        ("zz-staging-safety",))
    assert r["status"] == "FAIL" and len(r["findings"]) == 3
    table = "+------+--------+\n| name | status | version |\n+------+\n| akismet | active | 5.3 |\n"
    assert q.parse_plugin_list(table) == {"akismet": {"status": "active", "version": "5.3"}}
    assert q.check_plugins(None, "[]")["status"] == "SKIP"


def test_axe_formats():
    a = [{"name": "home", "dev": "mobile", "v": [{"id": "color-contrast", "impact": "serious", "n": 5, "ex": [{"t": "a.btn"}]},
                                                {"id": "region", "impact": "moderate", "n": 1, "ex": []}]},
         {"path": "/lien-he/", "w": 1440, "version": "4.10.2", "violations": [{"id": "region", "impact": "moderate", "n": 2, "nodes": [{"t": ".fab"}]}]},
         {"name": "x", "vw": 360, "axe": {"violations": [{"id": "button-name", "impact": "critical", "n": 1, "ex": [{"t": "button.menu"}]}]}},
         {"name": "y", "vw": 768, "axe": None}]
    recs = q.axe_records(a)
    assert len(recs) == 3
    r = q.check_axe(recs)
    by = {f["rule"]: f for f in r["findings"]}
    assert r["status"] == "FAIL" and by["color-contrast"]["level"] == "FAIL" and by["region"]["level"] == "WARN"
    assert by["region"]["pages"] == 2 and by["region"]["nodes"] == 3
    r2 = q.check_axe(recs, ignore=("color-contrast", "button-name"))
    assert r2["status"] == "WARN"
    assert q.check_axe([])["status"] == "SKIP"


def test_focus():
    good = {"sig": "a.skip-link", "txt": "Bỏ qua đến nội dung chính", "outline": "2px solid rgb(0,0,0)", "shadow": "", "inview": True, "hidden": False}
    plain = {"sig": "nav > a", "txt": "Dịch vụ", "outline": "", "shadow": "", "inview": True, "hidden": False}
    ghost = {"sig": "div.slick-slide > a", "txt": "", "outline": "1px auto", "shadow": "", "inview": False, "hidden": True}
    recs = q.focus_records([{"name": "home", "vw": 360, "focus": {"n": 3, "items": [good, plain, ghost]}},
                            {"url": "https://mau.vn/", "w": 1440, "n": 1, "items": [good], "_file": "home-d1440"}])
    assert len(recs) == 2
    r = q.check_focus(recs)
    issues = [f["issue"] for f in r["findings"]]
    assert r["status"] == "FAIL" and any("không đổi hiển thị" in i for i in issues) and any("ẩn vẫn nhận focus" in i for i in issues)
    r = q.check_focus(q.focus_records([{"items": [plain], "_file": "a", "w": 360}]))
    assert any("skip link" in f["issue"] for f in r["findings"])
    assert q.check_focus(q.focus_records([{"items": [good], "_file": "a", "w": 360}]))["status"] == "PASS"
    # bản đo mới có changed: ô nhập đổi màu viền khi focus là có chỉ báo; outline có sẵn mà không đổi là không có chỉ báo
    border = {**plain, "sig": "form > input", "changed": True}
    static = {**good, "sig": "a.box", "txt": "Hộp", "changed": False}
    r = q.check_focus(q.focus_records([{"name": "p", "vw": 360, "focus": {"items": [good, border, static]}}]))
    assert r["status"] == "FAIL" and r["findings"][0]["examples"] == ["a.box"], r
    # phần tử ngoài màn hình lúc đo chỉ là ghi chú
    off = {**good, "inview": False}
    r = q.check_focus(q.focus_records([{"name": "p", "vw": 360, "focus": {"items": [good, off]}}]))
    assert r["status"] == "PASS" and any("ngoài màn hình" in n for n in r["notes"])


def test_ui_visual():
    with tempfile.TemporaryDirectory() as t:
        reg = Path(t) / "reg.json"
        reg.write_text(json.dumps({"entries": [
            {"rubric": "ui-visual", "version": "2026-10-17.2", "site": "mau.vn", "question": "empty_control", "threshold": 0.9},
            {"rubric": "ui-visual", "version": "2026-10-17.1", "site": "mau.vn", "question": "cut_off", "threshold": 0.5},
            {"rubric": "first-screen", "version": "2026-10-17.2", "site": "mau.vn", "question": "media", "threshold": 0.5}]}), encoding="utf-8")
        gates = q.load_gates([str(reg), None], "mau.vn", "2026-10-17.2")
        assert list(gates) == ["empty_control"] and gates["empty_control"]["thr"] == 0.9
        rows = [{"id": "a|360|0", "answers": {"empty_control": {"p_yes": 0.8}, "cut_off": {"p_yes": 0.75}}},
                {"id": "a|1366|0", "answers": {"empty_control": {"p_yes": 0.95}}},
                {"id": "b|360|0", "error": "http_400", "route": "review"}]
        r = q.check_ui_visual(rows, gates)
        assert r["status"] == "WARN" and all(f["level"] == "WARN" for f in r["findings"])
        flagged = {f["shot"]: f["flags"] for f in r["findings"]}
        assert flagged == {"a|360|0": ["cut_off 0.75"], "a|1366|0": ["empty_control 0.95"]}, flagged
        assert any("chưa hiệu chuẩn" in n.lower() for n in r["notes"])
        none = q.check_ui_visual(rows[:1], {})
        assert "chưa hiệu chuẩn, chỉ báo cho người đọc" in none["summary"]
        assert q.check_ui_visual([], gates)["status"] == "SKIP"
        all_gates = {k: {"thr": 0.9} for k in q.NOULS}
        assert q.check_ui_visual([{"id": "c", "answers": {k: {"p_yes": 0.1} for k in q.NOULS}}], all_gates)["status"] == "PASS"
        try:
            from PIL import Image
        except ImportError:
            print("bỏ test đệm ảnh: thiếu Pillow")
            return
        small = Path(t) / "nho.png"
        Image.new("RGB", (300, 200), "gray").save(small)
        out = q.pad_image(small)
        assert Image.open(out).size == (320, 320) and out.name == "nho_pad.png"
        big = Path(t) / "lon.jpg"
        Image.new("RGB", (800, 1600), "gray").save(big)
        w, h = Image.open(q.pad_image(big)).size
        assert max(w, h) <= 1568 and w * h <= 800_000 and abs(w / h - 0.5) < 0.01, (w, h)
        # Ca thật 23/10: màn desktop 1366x768 (1,05 MP) bị Jev trả http_400; ô dẹt cao < 0,3 lần rộng cũng vậy.
        desk = Path(t) / "desk.png"
        Image.new("RGB", (1366, 768), "gray").save(desk)
        w, h = Image.open(q.pad_image(desk)).size
        assert w * h <= 800_000 and w > 1100, (w, h)
        flat = Path(t) / "det.png"
        Image.new("RGB", (1200, 200), "gray").save(flat)
        assert Image.open(q.pad_image(flat)).size == (1200, 360)
        ok = Path(t) / "vua.jpg"
        Image.new("RGB", (540, 1170), "gray").save(ok)
        assert q.pad_image(ok) == ok
        shots = Path(t) / "shots"
        shots.mkdir()
        Image.new("RGB", (540, 1170), "gray").save(shots / "home_360_0.jpg")
        items = q.jev_items([{**browser_row("home", 360, 360, shots=[{"file": "home_360_0.jpg", "i": 0, "y": 0, "page_h": 4000}])}], shots, "Sticky header is intentional.")
        assert items[0]["id"] == "home|360|0" and items[0]["state"][1] == {"image_path": "shots/home_360_0.jpg"}
        assert "phone 360x800" in items[0]["state"][0] and items[0]["state"][0].endswith("Sticky header is intentional.")


def test_submit_guard():
    env = {"WEB_QA_SUBMIT_LIVE": "stg.mau.vn"}
    assert q.submit_allowed(False, "staging", "stg.mau.vn", env)[0] is False
    assert q.submit_allowed(True, "staging", "stg.mau.vn", {})[0] is False
    assert q.submit_allowed(True, "staging", "mau.vn", env)[0] is False
    assert q.submit_allowed(True, "staging", "stg.mau.vn", env) == (True, "ok")
    prod = {"WEB_QA_SUBMIT_LIVE": "mau.vn"}
    ok, why = q.submit_allowed(True, "production", "mau.vn", prod)
    assert not ok and "--approved" in why
    assert q.submit_allowed(True, "production", "mau.vn", prod, "  ")[0] is False
    assert q.submit_allowed(True, "production", "mau.vn", prod, "Người duyệt A, 19/10 14:00")[0] is True


def test_report_end_to_end():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        out, raw = t / "qa", t / "qa" / "raw"
        (raw / "html").mkdir(parents=True)
        shutil.copy(FX / "page_ok.html", raw / "html" / "dich-vu.html")
        shutil.copy(FX / "page_bad.html", raw / "html" / "gioi-thieu.html")
        shutil.copy(FX / "plugins_stg.tsv", t / "stg.tsv")
        shutil.copy(FX / "plugins_prod.json", t / "prod.json")
        http = [{"kind": "page", "name": "dich-vu", "path": "/dich-vu/", "expect": 200, "code": "200", "location": "", "final_code": "200", "final_url": "https://mau.vn/dich-vu/"},
                {"kind": "page", "name": "gioi-thieu", "path": "/gioi-thieu/", "expect": 200, "code": "200", "location": "", "final_code": "200", "final_url": "https://mau.vn/gioi-thieu/"},
                {"kind": "http", "path": "/xmlrpc.php", "expect": 403, "code": "403", "location": ""},
                {"kind": "redirect", "spec": {"from": "/cu/", "to": "/dich-vu/"}, "hops": [
                    {"url": "https://mau.vn/cu/", "code": "301", "location": "https://mau.vn/dich-vu/"}, {"url": "https://mau.vn/dich-vu/", "code": "200", "location": ""}]}]
        (raw / "http.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in http), encoding="utf-8")
        rows = [browser_row("dich-vu", 360, 360, forms=[{"visible": True, "visibleFields": 2}], tracking={"seen": 2, "blocked": 2, "leaked": []},
                            axe={"violations": [{"id": "region", "impact": "moderate", "n": 1, "ex": []}]},
                            focus={"n": 1, "items": [{"sig": "a.skip", "txt": "Bỏ qua đến nội dung", "outline": "2px solid", "shadow": "", "inview": True, "hidden": False}]}),
                browser_row("dich-vu", 768, 778, forms=[{"visible": True, "visibleFields": 2}]),
                browser_row("dich-vu", 1366, 1366, forms=[{"visible": True, "visibleFields": 2}])]
        (raw / "browser.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        cfg = {"site": "mau.vn", "env": "staging", "base": "https://mau.vn", "widths": [360, 768, 1366],
               "urls": [{"name": "dich-vu", "path": "/dich-vu/", "schema": ["Service"], "form": True}, {"name": "gioi-thieu", "path": "/gioi-thieu/"}],
               "tracking": {"expect": ["GTM-AB12CD3"]}, "plugins": {"staging": "stg.tsv", "production": "prod.json", "ignore": ["zz-staging-safety"]},
               "redirects": [{"from": "/cu/", "to": "/dich-vu/"}]}
        (t / "qa.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "report", "--config", str(t / "qa.json"), "--out", str(out)],
                           capture_output=True, text=True, cwd=t)
        assert p.returncode == 1, p.stderr  # FAIL trả mã 1
        rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
        st = {k: v["status"] for k, v in rep["categories"].items()}
        assert rep["verdict"] == "FAIL"
        assert st == {"overflow": "FAIL", "axe": "WARN", "focus": "PASS", "form": "WARN", "tracking": "FAIL", "plugins": "FAIL",
                      "http": "PASS", "redirect": "PASS", "canonical": "FAIL", "schema": "FAIL", "ui_visual": "SKIP",
                      "interact": "SKIP", "layout": "SKIP", "og": "FAIL"}, st
        md = (out / "report.md").read_text(encoding="utf-8")
        assert "Kết luận: **FAIL**" in md and "| Tràn ngang | FAIL |" in md and "Bỏ qua: Jev ui-visual" in md
        # check html trên thư mục đã lưu
        p = subprocess.run([sys.executable, "-B", "-E", str(SCRIPTS / "qa_gate.py"), "check", "html", str(raw / "html"), "--canonical-host", "mau.vn"],
                           capture_output=True, text=True)
        res = json.loads(p.stdout)
        assert res["schema"]["status"] == "FAIL" and res["tracking"]["status"] == "SKIP"


def test_mjs_syntax():
    node = shutil.which("node")
    if not node:
        print("bỏ test cú pháp .mjs: thiếu node")
        return
    for f in ("_cdp.mjs", "browser_probe.mjs", "form_submit.mjs", "interact_probe.mjs", "landmarks.mjs", "chrome_cleanup.mjs"):
        p = subprocess.run([node, "--check", str(SCRIPTS / f)], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
    src = (SCRIPTS / "form_submit.mjs").read_text(encoding="utf-8")
    assert "process.env.WEB_QA_SUBMIT_LIVE !== host" in src and "process.exit(2)" in src


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} test đạt")
