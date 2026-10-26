#!/usr/bin/env python3
"""Test offline cho wp-ui-fix: match.mjs, css_sources.sh, theme_patch.py, type_probe.mjs, type_check.py, shot_el.mjs, so_sanh.py.
Không SSH, không gọi site hay server thật, không gọi API trả phí. Chrome chỉ mở trang fixture trên 127.0.0.1.
Chạy: python3 -B scripts/tests/test_wp_ui_fix.py   (cần node và Chrome cho nhóm test trình duyệt, thiếu thì nhóm đó SKIP)

Ca hỏng thật đã gặp (nguồn gốc nằm trong workspace của Vincent, Deliverables/GTV-Brand/GTV-Website, 18–20/10/2026; số liệu đã chép vào fixture):
 1. Accordion 12px do theme ép bằng selector 4 lớp: luật 1 lớp ép 16px thua (ux-type-audit/pilot-bao-cao.md §3).
 2. Critical CSS của 5 template còn height:350px cho .feat-img, cùng bản sao ở template PHP và file gộp (ui-20261020/bao-cao.md, M14).
 3. measure.mjs cũ ẩn cả phần tử sticky: ảnh hero mobile mất, Jev báo lỗi giả 0,87 (pilot-bao-cao.md §2).
 4. Trang chủ 14 px, 99,5% chữ dưới ngưỡng, H1 56 px so với 32 px ở trang dịch vụ (pilot-bao-cao.md §1).
 5. Bản vá vòng 1–2 gây 7 lỗi hồi quy (rule toàn cục trên heading) và file có mục lệch vẫn bị ghi (review đối kháng 18/10).
 6. CSS form thua specificity, phải đẩy staging 3 lượt (18/10 21:00): match.mjs --css báo rule thử thua trước khi deploy.
 7. Nút liên hệ fixed phủ phần tử khi chụp, ảnh trước/sau không so được: shot_el.mjs ẩn fixed, giữ sticky; so_sanh.py khoanh vùng đổi.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
FX = HERE / "fixtures"
PY = sys.executable


def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def rjson(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wtext(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def rtext(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def run(cmd, env=None, cwd=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd, timeout=180)


def have_chrome():
    if not shutil.which("node"):
        return False
    code = "import {chromeBin} from %s; try{chromeBin();console.log('ok')}catch(e){console.log('no')}" % json.dumps(
        "file://" + str(SCRIPTS.parent.parent / "web-qa-gate/scripts/_cdp.mjs"))
    r = run(["node", "--input-type=module", "-e", code])
    return r.stdout.strip() == "ok"


HAVE_NODE = bool(shutil.which("node"))
HAVE_CHROME = have_chrome()
SERVER = None


class FixtureServer:
    ROUTES = {"/": ("match.html", "text/html; charset=utf-8"), "/type": ("type.html", "text/html; charset=utf-8"),
              "/shot": ("shot.html", "text/html; charset=utf-8"),
              "/theme.css": ("theme.css", "text/css"), "/litespeed/css/abc123.css": ("abc123.css", "text/css")}

    def __init__(self):
        routes = self.ROUTES

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                hit = routes.get(self.path.split("?")[0])
                if not hit:
                    self.send_response(404); self.end_headers(); return
                body = (FX / hit[0]).read_bytes()
                self.send_response(200); self.send_header("Content-Type", hit[1]); self.end_headers(); self.wfile.write(body)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()


def setUpModule():
    global SERVER
    SERVER = FixtureServer()


def tearDownModule():
    SERVER.httpd.shutdown()
    SERVER.httpd.server_close()


class TestCli(unittest.TestCase):
    def test_moi_script_co_help_thoat_0(self):
        cmds = [["bash", str(SCRIPTS / "css_sources.sh"), "--help"], [PY, "-I", str(SCRIPTS / "theme_patch.py"), "--help"], [PY, "-I", str(SCRIPTS / "type_check.py"), "--help"],
                [PY, str(SCRIPTS / "so_sanh.py"), "--help"]]
        if HAVE_NODE:
            cmds += [["node", str(SCRIPTS / "match.mjs"), "--help"], ["node", str(SCRIPTS / "type_probe.mjs"), "--help"], ["node", str(SCRIPTS / "shot_el.mjs"), "--help"]]
        for c in cmds:
            r = run(c)
            self.assertEqual(r.returncode, 0, c)
            self.assertIn("Mã thoát", r.stdout, c)

    @unittest.skipUnless(HAVE_NODE, "thiếu node")
    def test_cu_phap_mjs(self):
        for f in ("_cascade.mjs", "match.mjs", "type_probe.mjs", "shot_el.mjs", "tests/cascade_unit.mjs"):
            self.assertEqual(run(["node", "--check", str(SCRIPTS / f)]).returncode, 0, f)


# ---------- cascade (node, không cần Chrome) ----------
@unittest.skipUnless(HAVE_NODE, "thiếu node")
class TestCascade(unittest.TestCase):
    def test_unit(self):
        r = run(["node", str(SCRIPTS / "tests/cascade_unit.mjs")])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("cascade_unit: OK", r.stdout)


# ---------- match.mjs ----------
@unittest.skipUnless(HAVE_CHROME, "thiếu node hoặc Chrome")
class TestMatch(unittest.TestCase):
    def match(self, selector, *extra):
        r = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/", selector, "--json", *extra])
        return r, (json.loads(r.stdout)["results"] if r.stdout.strip().startswith("{") else None)

    def test_ca1_theme_4_lop_thang_luat_1_lop(self):
        r, res = self.match("#acc", "--width", "1366", "--props", "font-size")
        self.assertEqual(r.returncode, 0, r.stderr)
        p = res[0]["properties"][0]
        self.assertEqual(p["winner"]["value"], "12px")
        self.assertEqual(p["winner"]["spec"], [0, 4, 1])
        self.assertTrue(p["winner"]["source"].endswith("/theme.css"))
        self.assertEqual(p["computed"], "12px")
        losers = {d["selector"]: d for d in p["overridden"]}
        self.assertIn(".accordion-body p", losers)
        self.assertIn("specificity thấp hơn", losers[".accordion-body p"]["why"])
        self.assertIn("inline <style>", losers[".accordion-body p"]["source"])
        self.assertIn("> (0,4,1)", p["need"])

    def test_important_inline_va_shorthand(self):
        _, res = self.match("#note", "--width", "390", "--props", "font-size,color,margin-top")
        by = {p["prop"]: p for p in res[0]["properties"]}
        self.assertTrue(by["font-size"]["winner"]["important"])
        self.assertEqual(by["font-size"]["computed"], "14px")
        self.assertTrue(by["color"]["winner"]["inline"])
        self.assertEqual(by["color"]["winner"]["value"], "rgb(200, 0, 0)")
        self.assertIsNone(by["color"]["winner"]["line"])
        self.assertTrue(by["margin-top"]["winner"]["implicit"])
        self.assertEqual(by["margin-top"]["winner"]["value"], "0px")
        self.assertEqual([d["value"] for d in by["margin-top"]["overridden"]], ["20px"])

    def test_file_gop_cache_co_goi_y_va_media_theo_do_rong(self):
        _, res = self.match("#h2", "--widths", "390,1366", "--props", "font-size")
        w = {r["width"]: r["properties"][0] for r in res}
        for width in (390, 1366):
            self.assertEqual(w[width]["winner"]["value"], "30px")
            self.assertIn("css_sources.sh", w[width]["hint"])
        medias = [d.get("media") for d in w[390]["overridden"]]
        self.assertIn("(max-width: 500px)", medias)
        self.assertEqual(len(w[390]["overridden"]), 2)

    def test_all_hien_longhand(self):
        r = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/", "#note", "--all"])
        self.assertIn("(từ shorthand)", r.stdout)
        r2 = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/", "#note"])
        self.assertIn("dùng --all", r2.stdout)

    def test_state_va_loi(self):
        r, _ = self.match(".khong-co")
        self.assertEqual(r.returncode, 1)
        r = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/"])
        self.assertEqual(r.returncode, 2)
        r = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/", "p", "--state", "lạ"])
        self.assertEqual(r.returncode, 2)
        r = run(["node", str(SCRIPTS / "match.mjs"), "--help"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("Mã thoát", r.stdout)

    def test_ca6_css_thu_thua_va_thang(self):
        # Ca 18/10: rule sửa 1 lớp thua theme 4 lớp, lane chỉ biết sau khi đẩy staging. --css báo trước khi deploy.
        d = tempfile.mkdtemp(prefix="mt-")
        try:
            weak, strong = os.path.join(d, "yeu.css"), os.path.join(d, "manh.css")
            wtext(weak, ".accordion-item p { font-size: 17px; }\n")
            wtext(strong, "/* thử */\n.accordion-list .accordion-item .accordion-body .expanded-content-1 p#acc { font-size: 17px; }\n")
            r, res = self.match("#acc", "--width", "390", "--props", "font-size", "--css", weak)
            self.assertEqual(r.returncode, 3, r.stderr)
            p = res[0]["properties"][0]
            self.assertEqual(p["computed"], "12px")
            self.assertEqual(res[0]["trial"]["loses"], ["font-size"])
            lost = [x for x in p["overridden"] if x["source"].startswith("CSS thử")]
            self.assertEqual(len(lost), 1)
            self.assertIn("specificity thấp hơn", lost[0]["why"])
            r, res = self.match("#acc", "--width", "390", "--props", "font-size", "--css", strong)
            self.assertEqual(r.returncode, 0, r.stderr)
            p = res[0]["properties"][0]
            self.assertEqual(p["computed"], "17px")
            self.assertTrue(p["winner"]["source"].startswith("CSS thử (--css manh.css)"))
            self.assertEqual(p["winner"]["line"], 2)
            self.assertEqual(res[0]["trial"], {"file": strong, "wins": ["font-size"], "loses": []})
            r = run(["node", str(SCRIPTS / "match.mjs"), SERVER.url + "/", "#acc", "--css", os.path.join(d, "khong.css")])
            self.assertEqual(r.returncode, 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)


# ---------- shot_el.mjs ----------
def px_colors(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    return im.size, set(im.getdata()), im


@unittest.skipUnless(HAVE_CHROME, "thiếu node hoặc Chrome")
class TestShotEl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp(prefix="se-")
        cls.r = run(["node", str(SCRIPTS / "shot_el.mjs"), "hop=" + SERVER.url + "/shot", "--sel", "#hop", "--pad", "10",
                     "--widths", "390,1366", "--out", cls.out, "--label", "truoc", "--wait", "300"])
        cls.data = rjson(os.path.join(cls.out, "shots_truoc.json")) if os.path.exists(os.path.join(cls.out, "shots_truoc.json")) else {"shots": []}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_ca7_chup_phan_tu_an_fixed_giu_sticky(self):
        self.assertEqual(self.r.returncode, 0, self.r.stdout + self.r.stderr)
        for s in self.data["shots"]:
            self.assertEqual(s["hid_fixed"], 1)
            self.assertEqual(s["kept_sticky"], 1)
            self.assertEqual(s["path"], "/shot")
            self.assertNotIn("url", s)
            size, cols, im = px_colors(os.path.join(self.out, s["file"]))
            self.assertEqual(size, (320, 140))
            self.assertEqual(im.getpixel((160, 70)), (0, 160, 0))
            self.assertNotIn((255, 0, 0), cols)

    def test_css_thu_va_man_dau_giu_fixed(self):
        css = os.path.join(self.out, "thu.css")
        wtext(css, "#hop{background:rgb(0,0,255)!important}\n")
        r = run(["node", str(SCRIPTS / "shot_el.mjs"), "hop=" + SERVER.url + "/shot", "--sel", "#hop", "--pad", "10", "--widths", "390",
                 "--out", self.out, "--label", "sau", "--wait", "300", "--css", css])
        self.assertEqual(r.returncode, 0, r.stderr)
        s = rjson(os.path.join(self.out, "shots_sau.json"))["shots"][0]
        self.assertEqual(s["css"], "thu.css")
        self.assertEqual(px_colors(os.path.join(self.out, s["file"]))[2].getpixel((160, 70)), (0, 0, 255))
        r = run(["node", str(SCRIPTS / "shot_el.mjs"), "hop=" + SERVER.url + "/shot", "--widths", "390", "--out", self.out, "--label", "hero", "--wait", "300"])
        self.assertEqual(r.returncode, 0, r.stderr)
        size, cols, _ = px_colors(os.path.join(self.out, "hop_390_hero.png"))
        self.assertEqual(size, (390, 800))
        self.assertIn((255, 0, 0), cols)
        self.assertIn((0, 0, 200), cols)

    def test_loi_selector_404_va_cu_phap(self):
        r = run(["node", str(SCRIPTS / "shot_el.mjs"), SERVER.url + "/shot", "--sel", ".khong-co", "--widths", "390", "--out", self.out, "--label", "x1", "--wait", "100"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("selector khớp 0", rjson(os.path.join(self.out, "shots_x1.json"))["shots"][0]["error"])
        r = run(["node", str(SCRIPTS / "shot_el.mjs"), SERVER.url + "/khong", "--widths", "390", "--out", self.out, "--label", "x2", "--wait", "100"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("HTTP 404", rjson(os.path.join(self.out, "shots_x2.json"))["shots"][0]["error"])
        self.assertEqual(run(["node", str(SCRIPTS / "shot_el.mjs"), SERVER.url + "/shot", "--out", self.out]).returncode, 2)
        self.assertEqual(run(["node", str(SCRIPTS / "shot_el.mjs"), SERVER.url + "/shot", "--out", self.out, "--label", "có dấu"]).returncode, 2)


# ---------- so_sanh.py ----------
class TestSoSanh(unittest.TestCase):
    def setUp(self):
        from PIL import Image, ImageDraw
        self.d = tempfile.mkdtemp(prefix="ss-")
        a = Image.new("RGB", (400, 600), "white")
        b = a.copy()
        dr = ImageDraw.Draw(b)
        dr.rectangle((50, 100, 149, 159), fill="black")
        dr.rectangle((200, 450, 299, 499), fill="black")
        a.save(os.path.join(self.d, "home_1366_truoc.png"))
        b.save(os.path.join(self.d, "home_1366_sau.png"))
        a.save(os.path.join(self.d, "dv_390_truoc.png"))
        a.save(os.path.join(self.d, "dv_390_sau.png"))
        shot = lambda n, w, lb: {"name": n, "width": w, "label": lb, "sel": "main", "file": "%s_%d_%s.png" % (n, w, lb)}
        wjson(os.path.join(self.d, "shots_truoc.json"), {"shots": [shot("home", 1366, "truoc"), shot("dv", 390, "truoc")]})
        wjson(os.path.join(self.d, "shots_sau.json"), {"shots": [shot("home", 1366, "sau"), shot("dv", 390, "sau")]})

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def ss(self, *extra):
        return run([PY, str(SCRIPTS / "so_sanh.py"), "--dir", self.d, "--json", *extra])

    def test_khung_do_dung_vung_doi_va_trang_html(self):
        r = self.ss()
        self.assertEqual(r.returncode, 0, r.stderr)
        res = json.loads(r.stdout)
        by = {p["name"]: p for p in res["pairs"]}
        self.assertEqual(by["home"]["boxes"], [[50, 100, 149, 159], [200, 450, 299, 499]])
        self.assertEqual(by["home"]["status"], "đổi")
        self.assertEqual(by["dv"]["status"], "không đổi")
        self.assertTrue(res["out"].endswith("so-sanh_v1.html"))
        h = rtext(res["out"])
        self.assertIn("left:12.500%;top:16.667%;width:25.000%;height:10.000%", h)
        self.assertIn("Chép câu trả lời", h)
        self.assertIn('class="opt dx"', h)
        self.assertIn('src="home_1366_sau.png"', h)
        self.assertNotIn("data:image", h)
        r2 = run([PY, str(SCRIPTS / "so_sanh.py"), "--dir", self.d])
        self.assertIn("CẢNH BÁO dv 390px: không đổi", r2.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.d, "so-sanh_v2.html")))

    def test_cau_hoi_so_lieu_embed(self):
        q = os.path.join(self.d, "q.json")
        wjson(q, {"cau_hoi": [{"id": "thang", "hoi": "Áp thang chữ ra toàn site?", "boi_canh": "Pilot 2 trang đạt.",
                                "lua_chon": [{"id": "a", "nhan": "Áp toàn site", "de_xuat": True}, {"id": "b", "nhan": "Sửa thêm"}]}]})
        m = os.path.join(self.d, "m.json")
        wjson(m, [{"muc": "PSI mobile trang chủ", "truoc": 90, "sau": 93}])
        out = os.path.join(self.d, "trang.html")
        r = self.ss("--cau-hoi", q, "--so-lieu", m, "--embed", "--out", out, "--title", "Pilot <thang chữ>")
        self.assertEqual(r.returncode, 0, r.stderr)
        h = rtext(out)
        self.assertIn("data:image/png;base64,", h)
        self.assertIn("PSI mobile trang chủ", h)
        self.assertIn("Áp thang chữ ra toàn site?", h)
        self.assertIn("Pilot &lt;thang chữ&gt;", h)

    def test_thieu_cap_va_dau_vao_sai(self):
        data = rjson(os.path.join(self.d, "shots_sau.json"))
        data["shots"] = data["shots"][:1]
        wjson(os.path.join(self.d, "shots_sau.json"), data)
        r = self.ss()
        self.assertEqual(r.returncode, 1)
        self.assertIn("chỉ có ở lượt truoc", json.loads(r.stdout)["missing"][0])
        q = os.path.join(self.d, "q.json")
        wjson(q, {"cau_hoi": [{"id": "x", "hoi": "?", "lua_chon": [{"id": "a", "nhan": "A", "de_xuat": True}, {"id": "b", "nhan": "B", "de_xuat": True}]}]})
        self.assertEqual(self.ss("--cau-hoi", q).returncode, 2)
        self.assertEqual(self.ss("--sau", "khong-co").returncode, 2)
        self.assertEqual(self.ss("--thr", "300").returncode, 2)


# ---------- type_probe.mjs ----------
@unittest.skipUnless(HAVE_CHROME, "thiếu node hoặc Chrome")
class TestTypeProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp(prefix="tp-")
        cls.r = run(["node", str(SCRIPTS / "type_probe.mjs"), "home=" + SERVER.url + "/type", "--out", cls.out, "--widths", "390,1366", "--max-screens", "2"])
        cls.data = rjson(os.path.join(cls.out, "type_probe.json")) if os.path.exists(os.path.join(cls.out, "type_probe.json")) else {"pages": []}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def page(self, vp):
        return next(p for p in self.data["pages"] if p["vp"] == vp)

    def test_chay_xong_va_do_khoi_chu(self):
        self.assertEqual(self.r.returncode, 0, self.r.stdout + self.r.stderr)
        d = self.page("d1366")
        by = {b["sel"].split(" > ")[-1]: b for b in d["blocks"]}
        self.assertEqual(by["p.intro"]["fs"], 14)
        self.assertEqual(by["p.intro"]["lines"], 1)
        self.assertEqual(by["p#long"]["lines"], 2)
        self.assertGreater(by["p#long"]["cpl"], 80)
        self.assertEqual(by["footer"]["region"] if "footer" in by else d["blocks"][-1]["region"], "footer")
        self.assertEqual({h["tag"]: h["fs"] for h in d["heads"]}, {"h1": 56, "h2": 28})
        m = self.page("m390")
        self.assertGreater(next(b for b in m["blocks"] if b["tag"] == "h1")["lines"], 1)

    def test_ca3_an_fixed_giu_sticky(self):
        # Bản cũ ẩn cả sticky nên ảnh hero mobile mất. Bản này chỉ ẩn fixed và còn đếm sticky đã giữ.
        for vp in ("d1366", "m390"):
            p = self.page(vp)
            self.assertEqual(p["hid_fixed"], 1, vp)
            self.assertEqual(p["kept_sticky"], 1, vp)

    def test_khoang_cach_header_h1_va_anh(self):
        d = self.page("d1366")
        self.assertEqual(d["header"]["bottom"], 60)
        self.assertEqual(d["h1_gap"], 38)
        self.assertEqual(d["status"], 200)
        self.assertEqual(sorted(d["shots"]), ["home_1366_hero.jpg", "home_1366_s00.jpg", "home_1366_s01.jpg"])
        for f in d["shots"]:
            self.assertGreater(os.path.getsize(os.path.join(self.out, f)), 1000)

    def test_loi_cu_phap_va_url_hong(self):
        self.assertEqual(run(["node", str(SCRIPTS / "type_probe.mjs")]).returncode, 2)
        self.assertEqual(run(["node", str(SCRIPTS / "type_probe.mjs"), "ftp://x"]).returncode, 2)
        self.assertEqual(run(["node", str(SCRIPTS / "type_probe.mjs"), "--help"]).returncode, 0)
        out = tempfile.mkdtemp(prefix="tp-")
        try:
            r = run(["node", str(SCRIPTS / "type_probe.mjs"), "http://127.0.0.1:9/khong", "--out", out, "--widths", "1366", "--no-shots", "--wait", "100"])
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            d = rjson(os.path.join(out, "type_probe.json"))
            self.assertTrue(d["pages"][0].get("error") or d["pages"][0].get("blocks") == [])
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_probe_noi_type_check(self):
        r = run([PY, "-I", str(SCRIPTS / "type_check.py"), os.path.join(self.out, "type_probe.json"), "--json"])
        self.assertEqual(r.returncode, 1, r.stdout)
        codes = {(f["code"], f["page"].split()[-1]) for f in json.loads(r.stdout)["findings"]}
        self.assertIn(("body_small", "d1366"), codes)
        self.assertIn(("long_line", "d1366"), codes)


# ---------- css_sources.sh ----------
class TestCssSources(unittest.TestCase):
    def setUp(self):
        self.wp = tempfile.mkdtemp(prefix="wp-")
        w = Path(self.wp) / "wp-content"
        files = {
            "mu-plugins/gtv-ccss/cat-d.css": ".feat-img{height:350px;object-fit:cover}\n",
            "mu-plugins/gtv-ccss/tat/blog-d.css": ".feat-img { height: 350px; }\n",
            "mu-plugins/gtv-typo.php": "<?php\n// font only\n",
            "themes/gtv/templates/t.php": "<style>.blog-item .wrapper .image{height:165px}</style>\n<div class=\"feat-img\"></div>\n",
            "themes/gtv/style.css": ".feat-img{height:350px}\n",
            "litespeed/css/h.css": ".feat-img{height:350px}\n",
            "litespeed/ccss/x.css": ".feat-img{height:350px}\n",
            "uploads/elementor/css/post-12.css": ".elementor-12 .feat-img{height:350px}\n",
            "plugins/foo/assets/a.css": ".feat-img{height:350px}\n",
            "plugins/foo/node_modules/b.css": ".feat-img{height:350px}\n",
        }
        for rel, text in files.items():
            p = w / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        self.cc = Path(self.wp) / "cc.txt"
        self.cc.write_text(".a{x:1}\n.feat-img{height:350px}\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.wp, ignore_errors=True)

    def cs(self, *a, **k):
        return run(["bash", str(SCRIPTS / "css_sources.sh"), *a], **k)

    def tsv(self, *a):
        r = self.cs("--wp", self.wp, "--tsv", *a)
        return r, [l.split("\t") for l in r.stdout.splitlines() if l]

    def test_ca2_feat_img_350px_o_moi_nguon(self):
        r, rows = self.tsv("--custom-css-file", str(self.cc), "--regex", r"height:\s*350px")
        self.assertEqual(r.returncode, 0)
        by = {}
        for src, f, ln, txt in rows:
            by.setdefault(src, []).append(f)
        self.assertEqual(sorted(by), ["1", "2", "3", "5", "6", "7"])
        self.assertEqual(sorted(by["2"]), ["wp-content/litespeed/ccss/x.css", "wp-content/mu-plugins/gtv-ccss/cat-d.css", "wp-content/mu-plugins/gtv-ccss/tat/blog-d.css"])
        self.assertEqual(by["1"], ["wp-content/themes/gtv/style.css"])
        self.assertEqual(by["3"], ["custom_css (Customizer, DB)"])
        self.assertEqual(by["5"], ["wp-content/uploads/elementor/css/post-12.css"])
        self.assertEqual(by["6"], ["wp-content/plugins/foo/assets/a.css"])
        self.assertEqual(by["7"], ["wp-content/litespeed/css/h.css"])
        self.assertNotIn("4", by)
        self.assertFalse(any("node_modules" in f for fs in by.values() for f in fs))

    def test_ban_sao_trong_php_template(self):
        r, rows = self.tsv("height:165px")
        self.assertEqual([(x[0], x[1], x[2]) for x in rows], [("1", "wp-content/themes/gtv/templates/t.php", "1")])

    def test_bao_cao_va_nguon_chua_kiem(self):
        r = self.cs("--wp", self.wp, "feat-img")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[3] Customizer custom_css (DB): CHƯA KIỂM", r.stdout)
        self.assertIn("Sửa MỌI bản sao", r.stdout)
        r = self.cs("--wp", self.wp, "--theme", "khong-co", "height:165px")
        self.assertEqual(r.returncode, 1)

    def test_wp_cmd_xuat_custom_css(self):
        stub = Path(self.wp) / "fakewp"
        stub.write_text('#!/bin/sh\necho "$@" > "%s/args.txt"\necho ".feat-img{height:350px}"\n' % self.wp)
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        r = self.cs("--wp", self.wp, "--wp-cmd", "%s --path=/x" % stub, "feat-img")
        self.assertIn("[3] Customizer custom_css (DB): 1 khớp", r.stdout)
        self.assertIn("post list --post_type=custom_css", (Path(self.wp) / "args.txt").read_text())

    def test_regex_files_va_loi(self):
        r = self.cs("--wp", self.wp, "--regex", "--files", r"height:\s*350px")
        self.assertIn("wp-content/litespeed/css/h.css", r.stdout.splitlines())
        self.assertEqual(self.cs("--wp", "/khong/co/dau", "x").returncode, 2)
        self.assertEqual(self.cs("--wp", self.wp).returncode, 2)
        self.assertEqual(self.cs("--wp", self.wp, "--max", "x", "a").returncode, 2)
        self.assertEqual(self.cs("--lạ", "a").returncode, 2)
        r = self.cs("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Mã thoát", r.stdout)


# ---------- theme_patch.py ----------
class TestThemePatch(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="tpatch-")
        self.root = os.path.join(self.d, "theme")
        self.bk = os.path.join(self.d, "backup")
        os.makedirs(os.path.join(self.root, "templates"))
        os.makedirs(os.path.join(self.root, "mu"))
        self.w("templates/t.php", "<?php\n$a = 1;\n?><style>.image{height:165px}</style>\n<style>.image2{height:165px}</style>\n")
        self.w("style.css", ".feat-img{height:350px}\n.x{color:red}\n")
        self.w("mu/gtv.php", "<?php\n// mu\n")
        stub = os.path.join(self.d, "fakephp")
        wtext(stub, '#!/bin/sh\nif grep -q SYNTAXERR "$2"; then echo "PHP Parse error: syntax error" ; exit 255; fi\necho "No syntax errors detected"\n')
        os.chmod(stub, 0o755)
        self.php = stub

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def w(self, rel, text):
        wtext(os.path.join(self.root, rel), text)

    def r(self, rel):
        return rtext(os.path.join(self.root, rel))

    def spec(self, items):
        p = os.path.join(self.d, "spec.json")
        wjson(p, items)
        return p

    def tp(self, *a, env=None):
        r = run([PY, "-I", str(SCRIPTS / "theme_patch.py"), *a], env=env)
        rep = None
        try:
            rep = json.loads(r.stdout)
        except ValueError:
            pass
        return r, rep

    def apply(self, items, *extra):
        return self.tp("apply", self.root, self.spec(items), "--backup", self.bk, "--php", self.php, *extra)

    def test_mac_dinh_chay_thu_khong_ghi(self):
        before = self.r("style.css")
        r, rep = self.apply([{"id": "a", "file": "style.css", "old": "height:350px", "new": "aspect-ratio:16/9", "count": 1}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(rep["apply"])
        self.assertEqual(rep["files"][0]["would_write"], True)
        self.assertEqual(self.r("style.css"), before)
        self.assertFalse(os.path.exists(self.bk))

    def test_apply_ghi_backup_va_dung_sha(self):
        r, rep = self.apply([{"id": "a", "file": "style.css", "old": ".feat-img{height:350px}", "new": ".page-id-9 .feat-img{aspect-ratio:16/9}", "count": 1}], "--apply")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("aspect-ratio:16/9", self.r("style.css"))
        self.assertEqual(rtext(os.path.join(self.bk, "style.css")), ".feat-img{height:350px}\n.x{color:red}\n")
        f = rep["files"][0]
        self.assertNotEqual(f["before"], f["after"])

    def test_ca5_file_co_muc_lech_khong_bi_ghi(self):
        # M14: spec mong 2 chỗ height:165px, file chỉ có 2 style nhưng mục thứ hai mong 3 chỗ. Cả file phải giữ nguyên.
        before = self.r("templates/t.php")
        items = [{"id": "ok", "file": "templates/t.php", "old": ".image{height:165px}", "new": ".image{aspect-ratio:16/9}", "count": 1},
                 {"id": "lech", "file": "templates/t.php", "old": "height:165px", "new": "height:auto", "count": 3},
                 {"id": "khac", "file": "style.css", "old": "color:red", "new": "color:blue", "count": 1}]
        r, rep = self.apply(items, "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.r("templates/t.php"), before)
        self.assertEqual([s[0] for s in rep["skip"] if s[0] != "FILE"], ["lech"])
        self.assertIn("color:blue", self.r("style.css"))  # file khác vẫn ghi

    def test_lint_php_hong_tra_ve_ban_goc(self):
        before = self.r("mu/gtv.php")
        r, rep = self.apply([{"id": "p", "file": "mu/gtv.php", "old": "// mu", "new": "SYNTAXERR(", "count": 1}], "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.r("mu/gtv.php"), before)
        self.assertEqual(rep["lint"][0][0], "mu/gtv.php")
        self.assertEqual(rep["files"], [])

    @unittest.skipUnless(shutil.which("php"), "thiếu php")
    def test_lint_php_that(self):
        before = self.r("mu/gtv.php")
        r, _ = self.tp("apply", self.root, self.spec([{"id": "p", "file": "mu/gtv.php", "old": "// mu", "new": "function (", "count": 1}]), "--backup", self.bk, "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.r("mu/gtv.php"), before)

    def test_thieu_php_thi_khong_ghi_file_php(self):
        before = self.r("mu/gtv.php")
        r, rep = self.tp("apply", self.root, self.spec([{"id": "p", "file": "mu/gtv.php", "old": "// mu", "new": "// mu2", "count": 1}]), "--backup", self.bk, "--apply",
                         env={"PHP_BIN": "", "PATH": "/nonexistent"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.r("mu/gtv.php"), before)
        self.assertIn("không có php", rep["lint"][0][1])

    def test_css_hong_ngoac_tra_ve_ban_goc(self):
        before = self.r("style.css")
        r, rep = self.apply([{"id": "c", "file": "style.css", "old": ".x{color:red}", "new": ".x{color:red", "count": 1}], "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.r("style.css"), before)

    def test_ca5_rule_toan_cuc_tren_heading_bi_chan(self):
        before = self.r("style.css")
        bad = [{"id": "g", "file": "style.css", "old": ".x{color:red}", "new": "h2{font-size:32px}\n@media (max-width:600px){ p{font-size:16px} nav a{color:#000} }", "count": 1}]
        r, rep = self.apply(bad, "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.r("style.css"), before)
        self.assertEqual(sorted(rep["global"][0][2]), ["h2", "nav a", "p"])
        ok = [{"id": "g", "file": "style.css", "old": ".x{color:red}", "new": ".page-id-125291 h2{font-size:32px}\n@media (max-width:600px){ .page-id-125291 p{font-size:16px} }", "count": 1}]
        r, rep = self.apply(ok, "--apply")
        self.assertEqual(r.returncode, 0, r.stdout)
        # allow_global cho ngoại lệ có chủ ý
        self.w("style.css", ".x{color:red}\n")
        r, _ = self.apply([dict(bad[0], allow_global=True)], "--apply")
        self.assertEqual(r.returncode, 0)

    def test_css_true_trong_mu_plugin_php_va_canh_bao_icon(self):
        r, rep = self.apply([{"id": "m", "file": "mu/gtv.php", "old": "// mu", "new": "echo '<style>.fa-icon, .elementor-icon i{font-size:20px} body p{margin:0}</style>';", "count": 1, "css": True}], "--apply")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(rep["global"][0][2], ["body p"])
        self.assertTrue(any("icon" in w[2] for w in rep["warn"]))

    def test_chay_lai_khong_loi(self):
        item = [{"id": "a", "file": "style.css", "old": ".x{color:red}", "new": ".y .x{color:blue}", "count": 1}]
        self.apply(item, "--apply")
        r, rep = self.apply(item, "--apply")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(rep["already"], [["a", "style.css"]])

    def test_spec_sai_va_duong_dan_ra_ngoai(self):
        r, _ = self.apply([{"id": "a", "file": "../ngoai.css", "old": "a", "new": "b"}])
        self.assertEqual(r.returncode, 2)
        r, _ = self.apply([{"id": "a", "file": "style.css", "old": "", "new": "b"}])
        self.assertEqual(r.returncode, 2)
        r, _ = self.apply([{"id": "a", "file": "style.css", "old": "x", "new": "y"}, {"id": "a", "file": "style.css", "old": "x", "new": "y"}])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "theme_patch.py")]).returncode, 2)
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "theme_patch.py"), "--help"]).returncode, 0)

    def test_quarantine_khong_xoa_va_tra_ve(self):
        q = os.path.join(self.d, "quar")
        r, rep = self.tp("quarantine", self.root, "mu/gtv.php", "--to", q)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.root, "mu/gtv.php")))  # chạy thử không chuyển
        r, rep = self.tp("quarantine", self.root, "mu/gtv.php", "--to", q, "--apply")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.root, "mu/gtv.php")))
        self.assertTrue(os.path.exists(os.path.join(q, "mu/gtv.php")))
        self.assertIn("mu/gtv.php", rtext(os.path.join(q, "MANIFEST.tsv")))
        r, _ = self.tp("quarantine", self.root, "mu/gtv.php", "--to", q, "--apply")
        self.assertEqual(r.returncode, 1)  # file đã không còn
        self.w("mu/gtv.php", "<?php // bản mới\n")
        r, _ = self.tp("unquarantine", self.root, "--from", q, "--apply")
        self.assertEqual(r.returncode, 1)  # không ghi đè bản đang chạy
        os.remove(os.path.join(self.root, "mu/gtv.php"))
        r, rep = self.tp("unquarantine", self.root, "--from", q, "--apply")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.r("mu/gtv.php"), "<?php\n// mu\n")

    def test_restore_tu_backup(self):
        orig = self.r("style.css")
        self.apply([{"id": "a", "file": "style.css", "old": ".x{color:red}", "new": ".y .x{color:blue}", "count": 1}], "--apply")
        self.assertNotEqual(self.r("style.css"), orig)
        r, rep = self.tp("restore", self.root, "--backup", self.bk)
        self.assertEqual(rep["restored"], ["style.css"])
        self.assertNotEqual(self.r("style.css"), orig)  # chạy thử
        self.tp("restore", self.root, "--backup", self.bk, "--apply")
        self.assertEqual(self.r("style.css"), orig)

    def test_giu_crlf(self):
        self.w("style.css", ".a{x:1}\r\n.b{y:2}\r\n")
        self.apply([{"id": "a", "file": "style.css", "old": ".a{x:1}", "new": ".p .a{x:3}", "count": 1}], "--apply")
        self.assertEqual(self.r("style.css"), ".p .a{x:3}\r\n.b{y:2}\r\n")

    def test_lint_css_lenh_con(self):
        p = os.path.join(self.d, "a.css")
        wtext(p, "h1{a:b}\n.ok h2{a:b}\n")
        r = run([PY, "-I", str(SCRIPTS / "theme_patch.py"), "lint-css", p])
        self.assertEqual(r.returncode, 1)
        self.assertIn("rule toàn cục: h1", r.stdout)
        wtext(p, ".ok h2{a:b}\n")
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "theme_patch.py"), "lint-css", p]).returncode, 0)


# ---------- type_check.py ----------
def blk(tag, fs, n, sel, region="main", lines=1, cpl=None, y=0, cls="", fixed=False):
    return {"tag": tag, "sel": sel, "cls": cls, "fs": fs, "n": n, "w": 600, "lines": lines, "cpl": cpl if cpl is not None else n, "y": y, "region": region, "fixed": fixed, "sticky": False, "t": "x"}


def head(tag, fs, region="main"):
    return {"tag": tag, "fs": fs, "region": region, "fixed": False, "y": 0, "sel": tag, "t": "h"}


def page(name, width, blocks, heads, gap=64):
    return {"name": name, "path": "/" + name, "width": width, "vp": ("m" if width < 800 else "d") + str(width), "blocks": blocks, "heads": heads, "h1_gap": gap}


class TestTypeCheck(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="tc-")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def run_check(self, pages, *extra):
        p = os.path.join(self.d, "probe.json")
        wjson(p, {"version": 1, "pages": pages})
        r = run([PY, "-I", str(SCRIPTS / "type_check.py"), p, "--json", *extra])
        try:
            return r, json.loads(r.stdout)
        except ValueError:
            return r, None

    def codes(self, res):
        return sorted((f["code"], f["severity"]) for f in res["findings"])

    def truoc(self):
        # Số đo production trước pilot (pilot-bao-cao.md §1): home 1366 chữ thân 14 px, H1 56 / H2 28 / H3 22. dvseo H1 32.
        home = page("home", 1366, [blk("p", 14, 1990, "main > p.sub")] + [blk("p", 17, 10, "main > p.x")] + [blk("p", 14, 100, "main > div.accordion-body > p", lines=2, cpl=111, y=900)],
                    [head("h1", 56), head("h2", 28), head("h3", 22)], gap=0)
        dv = page("dvseo", 1366, [blk("p", 14, 1500, "main > p"), blk("p", 17, 300, "main > p.ok")], [head("h1", 32), head("h2", 28), head("h3", 16), head("h3", 22)], gap=64)
        mob = page("home", 390, [blk("p", 14, 1990, "main > p.sub"), blk("p", 12, 300, ".accordion-list .accordion-item .accordion-body p")], [head("h1", 30), head("h2", 28), head("h3", 22)], gap=56)
        return [home, dv, mob]

    def test_ca4_trang_chu_14px_h1_lech(self):
        r, res = self.run_check(self.truoc())
        self.assertEqual(r.returncode, 1)
        got = self.codes(res)
        self.assertIn(("body_small", "fail"), got)
        self.assertIn(("h1_spread", "fail"), got)
        self.assertIn(("hero_tight", "fail"), got)
        self.assertIn(("long_line", "warn"), got)
        home = next(p for p in res["pages"] if p["page"] == "home d1366")
        self.assertGreater(home["small_pct"], 90)
        self.assertEqual(home["body_px"], 14)
        spread = next(f for f in res["findings"] if f["code"] == "h1_spread")
        self.assertIn("(mọi trang, desktop)", spread["page"])
        self.assertEqual(sorted(d["h1_px"] for d in spread["detail"]), [32, 56])
        mob = next(f for f in res["findings"] if f["code"] == "body_small" and "m390" in f["page"])
        self.assertIn("accordion-body", json.dumps(mob["detail"], ensure_ascii=False))
        # hero ở mobile (gap 56) và dvseo (gap 64) không bị báo
        self.assertEqual([f["page"] for f in res["findings"] if f["code"] == "hero_tight"], ["home d1366"])

    def sau(self):
        # Staging sau pilot: chữ thân 17/16 px, H1 40 / 36. Còn nhãn chỉ số 14 px, chức danh 15 px, chú thích ảnh AI 15 px.
        labels = [blk("div", 14, 60, "main > div.case-metric", cls="case-metric"), blk("p", 15, 30, "main > p.speaker-title", cls="speaker-title"), blk("p", 15, 30, "main > p.ai-caption", cls="ai-caption")]
        labels = [dict(b, tag="p") for b in labels]
        home = page("home", 1366, [blk("p", 17, 800, "main > p")] + labels, [head("h1", 40), head("h2", 32), head("h3", 22)], gap=64)
        dv = page("dvseo", 1366, [blk("p", 17, 800, "main > p")], [head("h1", 36), head("h2", 32), head("h3", 20), head("h3", 22)], gap=64)
        return [home, dv]

    def test_sau_pilot_dat_khi_co_luat_component(self):
        r, res = self.run_check(self.sau())
        self.assertEqual(r.returncode, 1, "mặc định nhãn 14–15 px bị tính là dưới ngưỡng 16 px")
        self.assertEqual([c for c, s in self.codes(res) if s == "fail"], ["body_small"])
        rules = str(FX / "ui-rules.sample.md")
        r, res = self.run_check(self.sau(), "--rules", rules)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual([f for f in res["findings"] if f["severity"] == "fail"], [])
        self.assertTrue(all(p["small_pct"] == 0 for p in res["pages"]))

    def test_luat_md_h_scale_va_loi_luat(self):
        pages = self.sau()
        pages[1]["heads"][1]["fs"] = 28
        r, res = self.run_check(pages, "--rules", str(FX / "ui-rules.sample.md"))
        self.assertIn(("h_scale", "warn"), self.codes(res))
        self.assertEqual(r.returncode, 0)  # h_scale mặc định chỉ cảnh báo
        bad = os.path.join(self.d, "r.md")
        wtext(bad, "không có khối json\n")
        self.assertEqual(self.run_check(self.sau(), "--rules", bad)[0].returncode, 2)
        bj = os.path.join(self.d, "r.json")
        wjson(bj, {"type_rules": {"khoa_la": 1}})
        self.assertEqual(self.run_check(self.sau(), "--rules", bj)[0].returncode, 2)
        wjson(bj, {"severity": {"long_line": "fail"}})
        pages = self.sau()
        pages[0]["blocks"].append(blk("p", 17, 200, "main > p.rong", lines=2, cpl=100))
        r, _ = self.run_check(pages, "--rules", bj)
        self.assertEqual(r.returncode, 1)

    def test_loai_fixed_nav_footer_va_icon(self):
        pages = [page("a", 1366, [blk("p", 17, 800, "main > p"), blk("p", 12, 200, "main > p.nho", fixed=True), blk("li", 12, 200, "nav > li", region="nav"),
                                  blk("p", 12, 200, "footer > p", region="footer"), blk("p", 12, 200, "main > span.fa-icon-text"), blk("p", 12, 20, "main > p.ngan")],
                       [head("h1", 40), head("h2", 32)])]
        r, res = self.run_check(pages)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(res["pages"][0]["excluded"], 4)
        self.assertEqual(res["pages"][0]["blocks"], 1)

    def test_h_order_va_loi_do(self):
        pages = [page("a", 1366, [blk("p", 17, 800, "main > p")], [head("h1", 40), head("h2", 17), head("h3", 18)])]
        r, res = self.run_check(pages)
        self.assertEqual(r.returncode, 1)
        self.assertIn(("h_order", "fail"), self.codes(res))
        pages = [dict(page("a", 1366, [], []), error="timeout")]
        r, res = self.run_check(pages)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(res["findings"][0]["code"], "probe_error")

    def test_dau_vao_sai_va_defaults(self):
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "type_check.py")]).returncode, 2)
        p = os.path.join(self.d, "x.json")
        wtext(p, "{}")
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "type_check.py"), p]).returncode, 2)
        self.assertEqual(run([PY, "-I", str(SCRIPTS / "type_check.py"), os.path.join(self.d, "khong.json")]).returncode, 2)
        r = run([PY, "-I", str(SCRIPTS / "type_check.py"), "--print-defaults"])
        d = json.loads(r.stdout)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(d["defaults"]["max_cpl"], 80)
        self.assertIn("WCAG", d["sources"]["max_cpl"])
        for k in d["sources"]:
            self.assertIn(k, d["defaults"])

    def test_text_va_list(self):
        p = os.path.join(self.d, "probe.json")
        wjson(p, {"pages": self.truoc()})
        r = run([PY, "-I", str(SCRIPTS / "type_check.py"), p, "--list"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("Kết quả: FAIL", r.stdout)
        self.assertIn("sel=", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
