"""Test offline cho log_health.py: fixture log tự dựng, không mạng. Chạy: python3 -B tests/test_log_health.py"""
import gzip
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "log_health.py"
spec = importlib.util.spec_from_file_location("log_health", SCRIPT)
lh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lh)

# Log site mẫu (OpenLiteSpeed): dòng bọc nháy đơn, trường đầu `'-`, mã ở $10.
OLS = [
    "'- 1.2.3.4 - - [24/Oct/2026:12:00:00 +0700] \"GET / HTTP/2\" 200 100 \"-\" \"Mozilla/5.0\"'",
    "'- 1.2.3.4 - - [24/Oct/2026:12:10:00 +0700] \"GET /a/ HTTP/2\" 503 0 \"-\" \"Mozilla/5.0\"'",
    "'- 1.2.3.4 - - [24/Oct/2026:12:10:30 +0700] \"GET /b/ HTTP/2\" 404 0 \"-\" \"Mozilla/5.0\"'",
]
# Log en và staging: không có trường đầu, mã ở $9.
STD = [
    '5.6.7.8 - - [24/Oct/2026:12:09:00 +0700] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
    '5.6.7.8 - - [24/Oct/2026:12:11:00 +0700] "POST /wp-admin/admin-ajax.php HTTP/1.1" 500 7 "-" "Mozilla/5.0"',
    'dòng hỏng',
]


class LogHealth(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "ols.access_log").write_text("\n".join(OLS) + "\n", encoding="utf-8")
        with gzip.open(self.t / "en.access_log.gz", "wt", encoding="utf-8") as f:
            f.write("\n".join(STD) + "\n")

    def test_ca_hong_that_awk_cot_cung(self):
        # Ca thật 23–24/10: awk $10 trên log chuẩn đọc số byte, nên báo 0 lỗi 5xx.
        self.assertEqual(STD[1].split()[9], "7")
        r = lh.scan(self.t / "en.access_log.gz")
        self.assertEqual((r["parsed"], r["unparsed"], r["5xx"]), (2, 1, 1))

    def test_ols_va_khung_gio(self):
        since = lh.parse_when("2026-10-24 12:08:20")
        r = lh.scan(self.t / "ols.access_log", since)
        self.assertEqual((r["in_window"], r["4xx"], r["5xx"]), (2, 1, 1))
        self.assertEqual(r["minutes_5xx"], {"2026-10-24 12:10": 1})
        self.assertEqual(lh.parse_when("24/Oct/2026:12:08:20"), since)

    def test_ma_thoat(self):
        self.assertEqual(lh.main(["--log", str(self.t / "ols.access_log"), "--since", "2026-10-24 12:10:10"]), 0)
        self.assertEqual(lh.main(["--log", str(self.t / "ols.access_log"), "--log", str(self.t / "en.access_log.gz")]), 1)
        (self.t / "rong.log").write_text("định dạng lạ\n", encoding="utf-8")
        self.assertEqual(lh.main(["--log", str(self.t / "rong.log")]), 2)


if __name__ == "__main__":
    unittest.main()
