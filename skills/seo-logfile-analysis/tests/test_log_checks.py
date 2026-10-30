"""Test offline cho log_checks.py: fixture log tự dựng (IP tài liệu RFC 5737), fetch giả cho --probe, không mạng.
Chạy: python3 -B tests/test_log_checks.py"""
import contextlib
import gzip
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "log_checks.py"
spec = importlib.util.spec_from_file_location("log_checks", SCRIPT)
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

GBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
HUMAN = "Mozilla/5.0 Chrome/120"
V1, V2, U1 = "198.51.100.1", "198.51.100.2", "203.0.113.9"
SITE = "https://example.com"


def ols(ip, path, status, size, ref="-", ua=GBOT, day="19"):
    # Định dạng OpenLiteSpeed sau 21/10/2026: bọc nháy đơn, X-Forwarded-For đầu dòng, %D và trạng thái cache cuối dòng.
    return f"'- {ip} - - [{day}/Oct/2026:10:00:00 +0700] \"GET {path} HTTP/2\" {status} {size} \"{ref}\" \"{ua}\" 15234 \"miss\"'"


def std(ip, path, status, size, ref="-", ua=GBOT, day="18"):
    return f'{ip} - - [{day}/Oct/2026:10:00:00 +0700] "GET {path} HTTP/1.1" {status} {size} "{ref}" "{ua}"'


class Base(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.ver = self.t / "verified_ips.txt"
        self.ver.write_text(f"{V1}\n{V2}\n", encoding="utf-8")

    def log(self, name, lines):
        p = self.t / name
        if name.endswith(".gz"):
            with gzip.open(p, "wt", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        else:
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(p)

    def run_main(self, args, fetch=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lc.main(args, fetch=fetch)
        return code, out.getvalue(), err.getvalue()


class Uploads(Base):
    def lines_ca_that(self):
        miss = "/wp-content/uploads/2021/09/Mobile.png"
        L = [ols("203.0.113.5", miss, 410, 95839, ref="https://site-ngoai.example/a", ua=HUMAN) for _ in range(6)]
        L += [std("203.0.113.6", "/wp-content/uploads/2021/09/Message.png", 410, 95839, ua=HUMAN) for _ in range(2)]
        L += [ols("203.0.113.7", "/wp-content/uploads/2022/04/child-bg.png", 410, 95839, ref=SITE + "/seo/", ua=HUMAN)]
        L += [ols("203.0.113.7", "/wp-content/uploads/2024/01/ok.png", 200, 50000, ua=HUMAN)]
        L += [ols("203.0.113.8", "/bai-viet/", 200, 52700, ua=HUMAN) for _ in range(3)]
        L += ["dòng hỏng"]
        return L

    def test_ca_hong_that_410_nang_cho_file_thieu(self):
        # Ca thật site agency mẫu 06–19/10/2026: file upload thiếu trả 410 kèm trang 404 WordPress, khoảng 95 KB mỗi lần.
        log = self.log("a.access_log", self.lines_ca_that())
        code, out, _ = self.run_main(["uploads", "--log", log, "--site", SITE, "--json"])
        s = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual((s["missing_hits"], s["missing_files"], s["median_bytes"]), (9, 3, 95839))
        self.assertEqual(s["missing_bytes_pct"], round(100 * 9 * 95839 / (9 * 95839 + 50000 + 3 * 52700), 1))
        self.assertEqual(s["top_referer_hosts"], [["site-ngoai.example", 6]])   # referer cùng site bị bỏ
        self.assertEqual(s["top_files"][0], {"path": "/wp-content/uploads/2021/09/Mobile.png", "hits": 6,
                                             "avg_bytes": 95839})

    def test_bang_khong_chua_ip(self):
        log = self.log("a.access_log", self.lines_ca_that())
        _, out, _ = self.run_main(["uploads", "--log", log, "--site", SITE])
        self.assertNotIn("203.0.113.", out)
        self.assertIn("Cờ: trung vị trên 2048 byte", out)

    def test_sau_khi_sua_404_tinh_khong_co_co(self):
        # Đo sau rule 404 tĩnh 21/10: 1.249 byte mỗi response.
        lines = [ols("203.0.113.5", "/wp-content/uploads/2021/09/Mobile.png", 404, 1249, ua=HUMAN) for _ in range(4)]
        code, out, _ = self.run_main(["uploads", "--log", self.log("b.access_log.gz", lines), "--json"])
        self.assertEqual((code, json.loads(out)["median_bytes"]), (0, 1249))

    def test_loc_ngay(self):
        log = self.log("a.access_log", self.lines_ca_that())
        code, out, _ = self.run_main(["uploads", "--log", log, "--from", "2026-10-19", "--json"])
        self.assertEqual(json.loads(out)["missing_hits"], 7)   # 2 dòng ngày 18/10 bị loại

    def test_file_khong_doc_duoc_dong_nao_ma_2(self):
        bad = self.log("bad.access_log", ["không phải log", "cũng không phải"])
        good = self.log("a.access_log", self.lines_ca_that())
        code, _, err = self.run_main(["uploads", "--log", good, "--log", bad])
        self.assertEqual(code, 2)
        self.assertIn("0 lỗi", err)


ROUTES = {
    "/a": (301, "/a/"), "/a/": (200, None),
    "/faq/": (302, SITE + "/"), "/": (200, None),
    "/old/": (301, "/mid/"), "/mid/": (301, "/new/"), "/new/": (200, None),
    "/dead/": (301, "/gone/"), "/gone/": (410, None),
    "/cat-old/": (301, "/seo/"), "/seo/": (200, None),
    "/loop/": (301, "/loop2/"), "/loop2/": (301, "/loop/"),
    "/fixed/": (200, None),
}


def fake_fetch(url):
    return ROUTES[urlsplit(url).path]


class Redirects(Base):
    def lines_log(self):
        L = [ols(V1, "/a", 301, 0) for _ in range(3)] + [ols(V1, "/faq/", 302, 0) for _ in range(2)]
        L += [ols(V2, "/bo-1/", 410, 95000), ols(V2, "/go-sai/", 410, 95000), ols(V2, "/go-sai/", 410, 95000)]
        L += [ols(V2, "/x/", 404, 1000)]
        L += [ols(U1, "/b/", 301, 0)]                     # Googlebot tự khai, IP chưa xác minh
        L += [ols(V1, "/c/?p=1", 301, 0)]                  # URL có query
        L += [ols(V1, "/wp-content/x.png", 301, 0), ols(V1, "/feed/", 301, 0)]   # không phải HTML
        L += [ols(V1, "/d/", 200, 5000), ols(V1, "/e/", 301, 0, ua=HUMAN)]
        return L

    def test_khong_probe_dem_va_co_410_ngoai_danh_sach(self):
        log = self.log("a.access_log", self.lines_log())
        bo = self.t / "bo.txt"
        bo.write_text("https://www.example.com/bo-1\n", encoding="utf-8")   # www và thiếu "/" vẫn khớp
        code, out, _ = self.run_main(["redirects", "--log", log, "--site", SITE, "--verified-ips", str(self.ver),
                                      "--remove-list", str(bo), "--json"])
        s = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual((s["redirect_urls"], s["redirect_hits"]), (2, 5))
        self.assertEqual(s["skipped"], {"tu_khai": 1, "co_query": 1, "khong_html": 2})
        self.assertEqual((s["hits_410"], s["urls_410"], s["hits_404"]), (3, 2, 1))
        self.assertEqual((s["urls_410_ngoai_danh_sach"], s["hits_410_ngoai_danh_sach"]), (1, 2))
        self.assertEqual(s["groups"], {"tam_thoi": {"urls": 1, "hits": 2}})

    def test_bang_khong_chua_ip_va_nhac_url_ngau_nhien(self):
        log = self.log("a.access_log", self.lines_log())
        _, out, _ = self.run_main(["redirects", "--log", log, "--site", SITE, "--verified-ips", str(self.ver)])
        for ip in (V1, V2, U1):
            self.assertNotIn(ip, out)
        self.assertIn("Thiếu --remove-list", out)
        self.assertIn("URL ngẫu nhiên phải trả 404", out)

    def test_probe_chia_nhom(self):
        L = [ols(V1, p, 302 if p == "/faq/" else 301, 0) for p in
             ("/a", "/faq/", "/old/", "/dead/", "/cat-old/", "/loop/", "/fixed/")]
        hub = self.t / "hub.txt"
        hub.write_text(SITE + "/seo/\n", encoding="utf-8")
        d = self.t / "out"
        code, out, _ = self.run_main(["redirects", "--log", self.log("p.access_log", L), "--site", SITE,
                                      "--verified-ips", str(self.ver), "--hub-urls", str(hub), "--probe",
                                      "--out-dir", str(d), "--json"], fetch=fake_fetch)
        got = {urlsplit(r["url"]).path: r["nhom"] for r in json.loads(out)["rows"]}
        self.assertEqual(got, {"/a": ["thieu_gach_cuoi"], "/faq/": ["ve_trang_chu", "tam_thoi"], "/old/": ["chuoi"],
                               "/dead/": ["dich_khong_200"], "/cat-old/": ["ve_hub"],
                               "/loop/": ["chuoi", "dich_khong_200"], "/fixed/": ["da_doi"]})
        self.assertEqual(code, 1)
        tsv = (d / "redirects.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(tsv[0].split("\t"), ["hit_googlebot", "url", "ma_trong_log", "status_hien_tai", "so_buoc",
                                              "dich_cuoi", "status_dich", "nhom"])
        old = [r for r in tsv if "/old/\t" in r][0].split("\t")
        self.assertEqual(old[3:7], ["301", "2", SITE + "/new/", "200"])
        code, _, err = self.run_main(["redirects", "--log", self.log("p.access_log", L), "--site", SITE,
                                      "--verified-ips", str(self.ver), "--out-dir", str(d)])
        self.assertEqual(code, 2)   # không ghi đè khi thiếu --force
        self.assertIn("--force", err)

    def test_thieu_gach_cuoi_mot_buoc_khong_co_co(self):
        L = [ols(V1, "/a", 301, 0)]
        code, out, _ = self.run_main(["redirects", "--log", self.log("ok.access_log", L), "--site", SITE,
                                      "--verified-ips", str(self.ver), "--probe", "--json"], fetch=fake_fetch)
        self.assertEqual(code, 0)

    def test_probe_loi_mang_la_chua_do_ma_3(self):
        def flaky(url):
            if urlsplit(url).path == "/old/":
                raise OSError("timeout")
            return fake_fetch(url)
        L = [ols(V1, "/a", 301, 0), ols(V1, "/old/", 301, 0)]
        code, out, err = self.run_main(["redirects", "--log", self.log("f.access_log", L), "--site", SITE,
                                        "--verified-ips", str(self.ver), "--probe", "--json"], fetch=flaky)
        got = {urlsplit(r["url"]).path: r["nhom"] for r in json.loads(out)["rows"]}
        self.assertEqual(got["/old/"], ["chua_do"])
        self.assertEqual(code, 3)
        self.assertIn("chưa probe xong", err)

    def test_loi_dau_vao_ma_2(self):
        log = self.log("a.access_log", self.lines_log())
        empty = self.t / "empty.txt"
        empty.write_text("\n", encoding="utf-8")
        base = ["redirects", "--log", log, "--site", SITE, "--verified-ips"]
        self.assertEqual(self.run_main(base + [str(self.t / "none.txt")])[0], 2)
        self.assertEqual(self.run_main(base + [str(empty)])[0], 2)
        human = self.log("h.access_log", [ols(V1, "/a/", 200, 10, ua=HUMAN)])
        code, out, err = self.run_main(["redirects", "--log", human, "--site", SITE, "--verified-ips", str(self.ver)])
        self.assertEqual(code, 2)
        self.assertIn("0 redirect", err)

    def test_help(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as cm:
            lc.main(["--help"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("uploads", out.getvalue())


if __name__ == "__main__":
    unittest.main()
