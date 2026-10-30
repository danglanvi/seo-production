#!/usr/bin/env python3
"""Test offline cho scripts/log_urls_chet.py. Log giả của site mau.vn, IP thuộc dải tài liệu (192.0.2.0/24, 198.51.100.0/24).
Chạy: python3 -I tests/test_log_urls_chet.py
Ca thật làm nền (27/10/2026): URL cũ còn bị gọi lọt vào PHP; log origin 7 ngày cộng log CDN 2 ngày, lọc đường dẫn dò quét và link hỏng
trước khi chọn đích 301 hoặc 410.
"""
import gzip
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE.parent / "scripts"
GB, GB_FAKE, USER = "192.0.2.10", "198.51.100.9", "203.0.113.5"
UA_G = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
UA_U = "Mozilla/5.0 (Windows NT 10.0) Chrome/130.0 Safari/537.36"


def run(*args, ok=0):
    p = subprocess.run([sys.executable, "-I", str(S / "log_urls_chet.py"), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == ok, (args, p.returncode, p.stdout[-500:], p.stderr[-500:])
    return p


def dong(ip, path, code, ref="-", ua=UA_U, ts="25/Oct/2026:10:00:00 +0700", host=""):
    return f'{host}{ip} - - [{ts}] "GET {path} HTTP/1.1" {code} 512 "{ref}" "{ua}" 123\n'


def bunny(ip, path, code, ref="-", ua=UA_U, ms=1792900000000):
    return "|".join(["MISS", str(code), str(ms), "512", "999", ip, ref, f"https://mau.vn{path}", "x", ua, "VN", "0"]) + "\n"


def tsv(p):
    rows = [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()]
    h = rows[0]
    return h, {r[0]: dict(zip(h, r)) for r in rows[1:]}


def main():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        log = [
            dong(GB, "/bai-cu/", 404, ua=UA_G),                                   # Googlebot xác minh
            dong(GB_FAKE, "/gia-googlebot/", 404, ua=UA_G),                       # UA Google, IP không xác minh: không tính
            dong(USER, "/bai-cu/", 404, ref="https://www.google.com/", ua=UA_U),  # người dùng có referer
            dong(USER, "/bai-cu/", 404, ref="https://mau.vn/blog/", ua=UA_U),     # referer nội bộ
            dong(USER, "/bai-cu/", 404, ref="https://mau.vn/blog/", ua="curl/8.0"),  # curl: không tính
            dong(USER, "/chi-nguoi-dung/", 301, ref="https://blog.example/x", host="- "),  # host proxy phía trước IP
            dong(USER, "/da-song-lai/", 404, ref="https://blog.example/x"),
            dong(USER, "/da-song-lai/", 200, ref="https://blog.example/x"),
            dong(USER, "/wp-login.php", 404, ref="https://x.example/"),           # wp-*
            dong(USER, "/anh.jpg", 404, ref="https://x.example/"),                # file tĩnh
            dong(USER, "/phpmyadmin/", 404, ref="https://x.example/"),            # dò quét
            dong(USER, "/bai-cu/amp/", 404, ref="https://x.example/"),            # đuôi phụ
            dong(USER, "/rieng-site/", 404, ref="https://x.example/"),            # --drop-regex
            dong(USER, "/%22x/", 404, ref="https://x.example/"),                  # rác
            dong(USER, "/%20/a/", 404, ref="https://mau.vn/blog/"),               # path ghép %20: giữ, link hỏng nội bộ cần người đọc
            dong(USER, "/", 301, ref="https://x.example/"),                       # trang chủ
            dong(USER, "/khong-ref/", 404),                                       # không referer, không Googlebot
            dong(USER, "/qua-han/", 404, ref="https://x.example/", ts="01/Oct/2026:10:00:00 +0700"),  # ngoài --since
            "dòng hỏng không khớp định dạng\n",
        ]
        (d / "a.log").write_text("".join(log), encoding="utf-8")
        (d / "b.log.gz").write_bytes(gzip.compress(dong(GB, "/bai-cu/", 410, ua=UA_G).encode()))
        (d / "cdn.log").write_text(bunny(GB, "/chi-cdn/", 404, ua=UA_G) + bunny(USER, "/bai-cu/", 404, ref="https://blog.example/y") + "dòng ngắn\n", encoding="utf-8")
        (d / "ips.txt").write_text(GB + "\n")

        out = d / "ra.tsv"
        p = run("--site-host", "mau.vn", "--log", d / "a.log", "--log", d / "b.log.gz", "--cdn-log", d / "cdn.log", "--cdn-format", "bunny",
                "--verified-ips", d / "ips.txt", "--since", "2026-10-20", "--drop-regex", "^/rieng-site/", "--out", out)
        assert "CẢNH BÁO" not in p.stderr
        h, r = tsv(out)
        assert h[:5] == ["url", "clicks", "dich_goi_y", "tam_dong", "bo"], h
        assert set(r) == {"/bai-cu/", "/chi-nguoi-dung/", "/da-song-lai/", "/chi-cdn/", "/%20/a/"}, set(r)
        b = r["/bai-cu/"]
        # origin: 404 x4 (Googlebot, 2 referer, curl) + 410 qua .gz; CDN: 404 x1 có referer ngoài. curl đếm mã nhưng không đếm người dùng
        assert b["ma_log"] == "404:5,410:1", b["ma_log"]
        assert b["googlebot"] == "2" and b["nguoi_ref"] == "3" and b["noi_bo"] == "1" and b["nguon"] == "cdn+origin", b
        assert "mau.vn:1" in b["ref_top"] and GB not in json.dumps(b) and USER not in json.dumps(b)
        assert r["/chi-nguoi-dung/"]["googlebot"] == "0" and r["/chi-nguoi-dung/"]["nguoi_ref"] == "1"
        assert r["/da-song-lai/"]["ma_khac"] == "200:1"                       # đã sống lại: người xét thấy mã 200
        assert r["/chi-cdn/"]["nguon"] == "cdn" and r["/chi-cdn/"]["googlebot"] == "1"
        assert "/gia-googlebot/" not in r and "/khong-ref/" not in r and "/qua-han/" not in r
        assert "đường dẫn dò quét" in p.stderr and "wp-*" in p.stderr

        # không ghi đè
        run("--site-host", "mau.vn", "--log", d / "a.log", "--out", out, ok=2)

        # thiếu --verified-ips: cảnh báo, và IP trong dải 66.249 được tính
        (d / "c.log").write_text(dong("66.249.66.1", "/chi-prefix/", 404, ua=UA_G))
        p = run("--site-host", "mau.vn", "--log", d / "c.log", "--out", d / "c.tsv")
        assert "chưa xác minh" in p.stderr and "/chi-prefix/" in tsv(d / "c.tsv")[1]

        # file không đọc được dòng nào: thoát 2, không ghi "0 URL"
        (d / "rong.log").write_text("rác\nrác\n")
        p = run("--site-host", "mau.vn", "--log", d / "rong.log", "--out", d / "rong.tsv", ok=2)
        assert "Không đọc được dòng nào" in p.stderr and not (d / "rong.tsv").exists()
        run("--site-host", "mau.vn", "--log", d / "khong-co.log", "--out", d / "x.tsv", ok=2)
        run("--site-host", "mau.vn", "--cdn-log", d / "cdn.log", "--out", d / "y.tsv", ok=2)  # thiếu --cdn-format

        # tương thích pick_target.py: bảng ra làm --urls, không cột nào làm hỏng script
        dump = [dict(id=1, type="post", status="publish", name="bai-moi", parent=0, path="/bai-moi/", pm_uri=None, old_slugs=["bai-cu"])]
        (d / "dump.json").write_text(json.dumps(dump), encoding="utf-8")
        q = subprocess.run([sys.executable, "-I", str(S / "pick_target.py"), "--urls", str(out), "--dump", str(d / "dump.json"), "--out", str(d / "ra1.tsv")],
                           capture_output=True, text=True)
        assert q.returncode == 0, q.stderr
        _, ra = tsv(d / "ra1.tsv")
        assert ra["/bai-cu/"]["ma"] == "301" and ra["/bai-cu/"]["dich"] == "/bai-moi/" and ra["/bai-cu/"]["nguon"] == "old_slug", ra["/bai-cu/"]
    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
