"""Test offline cho verify_googlebot.py: fixture log và dải IP tự dựng (dải tài liệu RFC 5737), resolver giả, không mạng.
Chạy: python3 -B tests/test_verify_googlebot.py"""
import contextlib
import gzip
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_googlebot.py"
spec = importlib.util.spec_from_file_location("verify_googlebot", SCRIPT)
vg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vg)

GBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
IN_RANGE = [f"198.51.100.{i}" for i in range(1, 18)]          # 17 IP trong dải
STALE = [f"203.0.113.{i}" for i in range(1, 4)]               # 3 IP ngoài dải nhưng rDNS đúng (file dải cũ)
FAKE = [f"203.0.113.{i}" for i in range(11, 16)]              # 5 IP giả UA


def ols(ip, ua=GBOT, status=200):
    return f"'- {ip} - - [19/Oct/2026:18:24:00 +0700] \"GET /a/ HTTP/2\" {status} 100 \"-\" \"{ua}\"'"


def std(ip, ua=GBOT):
    return f'{ip} - - [19/Oct/2026:18:24:00 +0700] "GET /b/ HTTP/1.1" 200 512 "-" "{ua}"'


class FakeDns:
    """Giả rDNS. Đếm số lần gọi để chứng minh IP trong dải không bị rDNS."""

    def __init__(self):
        self.calls = []
        self.rev = {ip: f"crawl-{ip.replace('.', '-')}.googlebot.com" for ip in STALE}
        self.rev[FAKE[0]] = f"crawl-{FAKE[0].replace('.', '-')}.googlebot.com.evil.net"   # đuôi giả
        self.rev[FAKE[1]] = "fakegooglebot.com"                                             # thiếu dấu chấm ranh giới
        self.rev[FAKE[2]] = "host.googlebot.com"                                            # forward lệch IP
        # FAKE[3], FAKE[4]: không có PTR

    def reverse(self, ip):
        self.calls.append(ip)
        return self.rev.get(ip)

    def forward(self, host):
        for ip in STALE:
            if host == self.rev[ip]:
                return {ip}
        return {"192.0.2.99"}


class VerifyGooglebot(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.ranges = self.t / "googlebot.json"
        self.ranges.write_text(json.dumps({"prefixes": [{"ipv4Prefix": "198.51.100.0/24"}, {"ipv6Prefix": "2001:db8:1::/48"}]}),
                               encoding="utf-8")
        lines = [ols(ip) for ip in IN_RANGE] + [std(ip) for ip in STALE + FAKE]
        lines += [ols("198.51.100.200", ua="Mozilla/5.0 Chrome/120")]   # UA người dùng: bỏ qua
        lines += ["dòng hỏng"]
        (self.t / "a.access_log").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.dns = FakeDns()

    def run_main(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = vg.main(args, reverse=self.dns.reverse, forward=self.dns.forward)
        return code, out.getvalue(), err.getvalue()

    def test_ca_hong_that_rdns_tuan_tu_429_ip(self):
        # Ca thật 19/10: rDNS mọi IP vượt 600 s và rDNS lệch dải IP ở 8/25 IP.
        # Nay 17/25 IP nằm trong dải phải được loại trước rDNS; chỉ 8 IP ngoài dải bị rDNS.
        code, out, _ = self.run_main(["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges), "--json"])
        s = json.loads(out)
        self.assertEqual(sorted(self.dns.calls), sorted(STALE + FAKE))
        self.assertEqual(len(self.dns.calls), 8)
        self.assertEqual(s["ips"], 25)
        self.assertEqual(s["ips_by_status"], {"range": 17, "rdns": 3, "fake": 5, "unchecked": 0})
        self.assertEqual(s["real_ip_pct"], 80.0)
        self.assertEqual(s["invalid_ip_lines"], 0)
        self.assertEqual(s["unparsed_lines"], 1)
        self.assertEqual(code, 1)

    def test_tran_dau_ra_khong_chua_ip(self):
        _, out, _ = self.run_main(["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges)])
        for ip in IN_RANGE + STALE + FAKE:
            self.assertNotIn(ip, out)
        self.assertIn("Thật: 80.0% IP", out)
        self.assertIn("file dải IP", out)   # nhắc tải lại dải khi có IP chỉ qua rDNS

    def test_host_ok_ranh_gioi_ten_mien(self):
        sfx = (".googlebot.com", ".google.com")
        self.assertTrue(vg.host_ok("crawl-1-2-3-4.googlebot.com.", sfx))
        self.assertFalse(vg.host_ok("fakegooglebot.com", sfx))
        self.assertFalse(vg.host_ok("a.googlebot.com.evil.net", sfx))
        self.assertFalse(vg.host_ok(None, sfx))

    def test_ipv6_va_file_text(self):
        txt = self.t / "r.txt"
        txt.write_text("# ghi chú\n198.51.100.0/24\n2001:db8:1::/48\n", encoding="utf-8")
        rg = vg.load_ranges([txt])
        self.assertTrue(vg.in_ranges("2001:db8:1::abcd", rg))
        self.assertFalse(vg.in_ranges("2001:db8:2::1", rg))
        self.assertTrue(vg.in_ranges("198.51.100.255", rg))
        self.assertFalse(vg.in_ranges("198.51.101.0", rg))

    def test_no_rdns_ip_ngoai_dai_la_unchecked_ma_thoat_3(self):
        code, out, err = self.run_main(["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges), "--no-rdns"])
        self.assertEqual(self.dns.calls, [])
        self.assertEqual(code, 3)
        self.assertIn("chưa kiểm", err)

    def test_max_rdns_uu_tien_ip_nhieu_hit(self):
        # IP giả cuối danh sách có nhiều hit nhất: phải được kiểm trước khi hết hạn mức.
        busy = FAKE[4]
        extra = "\n".join(std(busy) for _ in range(5)) + "\n"
        with open(self.t / "a.access_log", "a", encoding="utf-8") as f:
            f.write(extra)
        code, out, _ = self.run_main(["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges),
                                      "--max-rdns", "1", "--workers", "1", "--json"])
        self.assertEqual(self.dns.calls, [busy])
        s = json.loads(out)
        self.assertEqual(s["ips_by_status"]["unchecked"], 7)
        self.assertEqual(code, 3)

    def test_dry_run_khong_ghi_va_write_ghi(self):
        d = self.t / "out"
        args = ["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges), "--out-dir", str(d)]
        _, out, _ = self.run_main(args)
        self.assertFalse(d.exists())
        self.assertIn("[dry-run]", out)
        self.run_main(args + ["--write"])
        ver = (d / "verified_ips.txt").read_text(encoding="utf-8").split()
        self.assertEqual(sorted(ver), sorted(IN_RANGE + STALE))
        self.assertEqual(sorted((d / "fake_ips.txt").read_text(encoding="utf-8").split()), sorted(FAKE))
        code, _, err = self.run_main(args + ["--write"])   # lần hai: không ghi đè
        self.assertEqual(code, 2)
        self.assertIn("--force", err)
        code, _, _ = self.run_main(args + ["--write", "--force"])
        self.assertEqual(code, 1)

    def test_loi_thieu_dau_vao_ma_thoat_2(self):
        log = str(self.t / "a.access_log")
        self.assertEqual(self.run_main(["--log", log])[0], 2)                                   # thiếu --ranges
        self.assertEqual(self.run_main(["--ranges", str(self.ranges)])[0], 2)                   # thiếu log
        self.assertEqual(self.run_main(["--log", log, "--ranges", str(self.t / "none.json")])[0], 2)
        self.assertEqual(self.run_main(["--log", str(self.t / "none.log"), "--ranges", str(self.ranges)])[0], 2)
        self.assertEqual(self.run_main(["--log", log, "--ranges", str(self.ranges), "--write"])[0], 2)

    def test_dai_ip_rong_hoac_hong_la_loi(self):
        empty = self.t / "empty.json"
        empty.write_text('{"prefixes": []}', encoding="utf-8")
        bad = self.t / "bad.json"
        bad.write_text("{không phải json", encoding="utf-8")
        badcidr = self.t / "bad.txt"
        badcidr.write_text("999.1.1.1/8\n", encoding="utf-8")
        log = str(self.t / "a.access_log")
        for f in (empty, bad, badcidr):
            self.assertEqual(self.run_main(["--log", log, "--ranges", str(f)])[0], 2, f.name)

    def test_log_khong_co_bot_khong_duoc_ghi_100_phan_tram(self):
        p = self.t / "human.log"
        p.write_text(ols("198.51.100.5", ua="Mozilla/5.0 Chrome/120") + "\n", encoding="utf-8")
        code, out, err = self.run_main(["--log", str(p), "--ranges", str(self.ranges)])
        self.assertEqual(code, 2)
        self.assertNotIn("100", out)
        self.assertIn("Không có IP googlebot", err)

    def test_gz_ols_va_file_ips(self):
        with gzip.open(self.t / "en.access_log.gz", "wt", encoding="utf-8") as f:
            f.write(ols("198.51.100.7") + "\n" + std("198.51.100.8") + "\n")
        code, out, _ = self.run_main(["--log", str(self.t / "en.access_log.gz"), "--ranges", str(self.ranges), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["ips_by_status"]["range"], 2)
        ips = self.t / "ips.txt"
        ips.write_text("198.51.100.9\n198.51.100.9\nkhông-phải-ip\n", encoding="utf-8")
        code, out, _ = self.run_main(["--ips", str(ips), "--ranges", str(self.ranges), "--json"])
        s = json.loads(out)
        self.assertEqual((code, s["ips"], s["hits"], s["invalid_ip_lines"]), (0, 1, 2, 1))

    def test_crosscheck_do_do_lech(self):
        code, out, _ = self.run_main(["--log", str(self.t / "a.access_log"), "--ranges", str(self.ranges),
                                      "--crosscheck", "4", "--json"])
        c = json.loads(out)["crosscheck"]
        self.assertEqual(c["sampled"], 4)
        self.assertEqual(c["mismatch"], 4)   # resolver giả không có PTR cho IP trong dải
        self.assertEqual(json.loads(out)["ips_by_status"]["range"], 17)   # không đổi trạng thái

    def test_bingbot_dung_duoi_rieng(self):
        p = self.t / "bing.log"
        p.write_text(std("203.0.113.1", ua="Mozilla/5.0 (compatible; bingbot/2.0)") + "\n", encoding="utf-8")
        self.dns.rev["203.0.113.1"] = "msnbot-203-0-113-1.search.msn.com"
        self.dns.forward = lambda host: {"203.0.113.1"}
        code, out, _ = self.run_main(["--log", str(p), "--ranges", str(self.ranges), "--bot", "bingbot", "--json"])
        self.assertEqual((code, json.loads(out)["ips_by_status"]["rdns"]), (0, 1))

    def test_ptr_googleusercontent_la_fake(self):
        # Ca thật 19/10/2026 (log site agency mẫu): 126 IP PTR googleusercontent.com (máy thuê Google Cloud) đều giả UA.
        # Forward-confirm vẫn khớp, nên đuôi này không được tính là Googlebot.
        ip = "203.0.113.50"
        p = self.t / "gcp.log"
        p.write_text(std(ip) + "\n", encoding="utf-8")
        self.dns.rev[ip] = "50.113.0.203.bc.googleusercontent.com"
        self.dns.forward = lambda host: {ip}
        code, out, _ = self.run_main(["--log", str(p), "--ranges", str(self.ranges), "--json"])
        self.assertEqual((code, json.loads(out)["ips_by_status"]["fake"]), (1, 1))

    def test_help(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as cm:
            vg.main(["--help"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("googlebot.json", out.getvalue())


if __name__ == "__main__":
    unittest.main()
