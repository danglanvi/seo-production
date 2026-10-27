#!/usr/bin/env python3
"""test_che_secret.py: che mật khẩu Redis, wp-config, response API, redis-cli -a; giữ nguyên dòng không có secret; chế độ chạy lệnh giữ mã thoát.

Ca thật: đêm 26–27/10/2026 một lane in mật khẩu Redis vào transcript 2 lần. Mọi giá trị trong fixture là giá trị giả.
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "che_secret.py")
sys.path.insert(0, os.path.dirname(HERE))
import che_secret  # noqa: E402

FAKE = "Zx9fakeRedisPass77"


class T(unittest.TestCase):
    def m(self, text, **k):
        return che_secret.mask(text, **k)[0]

    def test_redis_conf(self):
        out = self.m(f"bind 127.0.0.1\nrequirepass {FAKE}\nmaxmemory 256mb\n")
        self.assertNotIn(FAKE, out)
        self.assertIn("requirepass ***", out)
        self.assertIn("maxmemory 256mb", out)

    def test_redis_cli_a(self):
        out = self.m(f"redis-cli -a {FAKE} INFO keyspace")
        self.assertNotIn(FAKE, out)
        self.assertIn("INFO keyspace", out)

    def test_wp_config(self):
        out = self.m("define( 'DB_PASSWORD', 'p@ss-Fake-123' );\ndefine( 'AUTH_KEY', 'k$y-fake-very-long' );\ndefine( 'WP_CACHE', true );")
        self.assertNotIn("p@ss-Fake-123", out)
        self.assertNotIn("k$y-fake-very-long", out)
        self.assertIn("WP_CACHE", out)

    def test_api_json(self):
        out = self.m('{"Id": 42, "DeploymentKey": "dk-fake-0123456789", "AccessKey": "ak-fake-abcdef", "Name": "zone"}')
        self.assertNotIn("dk-fake", out)
        self.assertNotIn("ak-fake", out)
        self.assertIn('"Name": "zone"', out)

    def test_env_line_and_bearer(self):
        out = self.m("CLOUDFLARE_DNS_TOKEN=abcdEFGH12345678\nAuthorization: Bearer abcdefghijklmnop1234")
        self.assertNotIn("abcdEFGH12345678", out)
        self.assertNotIn("abcdefghijklmnop1234", out)

    def test_known_values_and_ip(self):
        out, n = che_secret.mask(f"log: {FAKE} from 203.0.113.9", known=[FAKE], ip=True)
        self.assertEqual(out, "log: *** from <ip>")
        self.assertEqual(n, 2)

    def test_plain_lines_untouched(self):
        s = "HTTP/2 200\ncache-control: max-age=31536000\nkeepalive_timeout 60\n"
        self.assertEqual(self.m(s), s)

    def test_wrap_keeps_exit_code(self):
        p = subprocess.run([sys.executable, SCRIPT, "--", sys.executable, "-c",
                            f"print('requirepass {FAKE}'); raise SystemExit(3)"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 3)
        self.assertNotIn(FAKE, p.stdout + p.stderr)
        self.assertIn("đã che 1 chỗ", p.stderr)

    def test_env_file_values(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, ".agent-secrets"))
        with open(os.path.join(d, ".agent-secrets", ".env"), "w") as f:
            f.write("BUNNY_API_KEY=bk-fake-value-001\nSHORT=abc\n")
        p = subprocess.run([sys.executable, SCRIPT], input="x bk-fake-value-001 y abc", capture_output=True, text=True, cwd=d)
        self.assertEqual(p.stdout, "x *** y abc")


if __name__ == "__main__":
    unittest.main()
