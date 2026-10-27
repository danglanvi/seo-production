# Test offline cho script cdn-speed-setup. Không gọi mạng.
# Ca hỏng thật (site VN, 26/10/2026): mã trạm Bunny Los Angeles "LA" trùng mã Lào, Googlebot bờ Tây bị đưa về origin khoảng 2 phút.
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import geo_rule  # noqa: E402
import rt_model  # noqa: E402
from _cdn import classify, mask  # noqa: E402
from cdn_dns_switch import plan  # noqa: E402
from warm import images  # noqa: E402
from bunny_geo_script import render  # noqa: E402


class GeoRule(unittest.TestCase):
    def test_vn_origin(self):
        self.assertEqual(geo_rule.route("VN", "SG"), "ORIGIN")

    def test_us_resolver_vn_station(self):
        # Resolver Mỹ (GeoIP US) nhưng trạm Bunny DNS ở Singapore nhận câu hỏi: coi là khách châu Á.
        self.assertEqual(geo_rule.route("US", "SG"), "ORIGIN")

    def test_la_station_is_us(self):
        self.assertEqual(geo_rule.route("US", "LA"), "CDN")

    def test_laos_country(self):
        self.assertEqual(geo_rule.route("LA", "SG"), "ORIGIN")

    def test_no_us_station_in_asia_sz(self):
        self.assertEqual(sorted(set(geo_rule.US_SZ) & set(geo_rule.ASIA_SZ)), [])

    def test_every_us_station_routes_cdn(self):
        for sz in geo_rule.US_SZ:
            self.assertEqual(geo_rule.route("US", sz), "CDN", sz)

    def test_empty_country_origin(self):
        self.assertEqual(geo_rule.route("", "IL"), "ORIGIN")

    def test_aaaa_asia_empty(self):
        self.assertEqual(geo_rule.route("VN", "SG", "AAAA"), "EMPTY")


class TemplateParity(unittest.TestCase):
    def setUp(self):
        self.js = open(os.path.join(SKILL, "templates", "geo-dns-script.js"), encoding="utf-8").read()

    def lst(self, name):
        m = re.search(r"const %s = \[([^\]]*)\]" % name, self.js)
        return re.findall(r'"([^"]+)"', m.group(1))

    def test_asia_same(self):
        self.assertEqual(self.lst("ASIA"), geo_rule.ASIA)

    def test_asia_sz_same(self):
        self.assertEqual(self.lst("ASIA_SZ"), geo_rule.ASIA_SZ)

    def test_render_no_placeholder_and_no_ip_in_template(self):
        self.assertIsNone(re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", self.js))
        out = render(self.js, "203.0.113.9", "zone-x")
        self.assertIn('"203.0.113.9"', out)
        self.assertNotIn("{{", out)


class Switch(unittest.TestCase):
    A = {"id": "a1", "type": "A", "content": "203.0.113.9", "proxied": False}
    C = {"id": "c1", "type": "CNAME", "content": "geo.cdn.test", "proxied": False}

    def test_switch_batch(self):
        body, _ = plan("switch", [self.A], "example.test", "geo.cdn.test")
        self.assertEqual(body["deletes"], [{"id": "a1"}])
        self.assertEqual(body["posts"][0]["type"], "CNAME")
        self.assertFalse(body["posts"][0]["proxied"])

    def test_switch_idempotent(self):
        body, why = plan("switch", [self.C], "example.test", "geo.cdn.test")
        self.assertIsNone(body)

    def test_unswitch(self):
        body, _ = plan("unswitch", [self.C], "example.test", ip="203.0.113.9")
        self.assertEqual(body["posts"][0], {"type": "A", "name": "example.test", "content": "203.0.113.9", "proxied": False, "ttl": 1})

    def test_refuse_proxied(self):
        body, why = plan("switch", [dict(self.A, proxied=True)], "example.test", "geo.cdn.test")
        self.assertIsNone(body)
        self.assertIn("proxied", why)

    def test_refuse_two_records(self):
        body, _ = plan("switch", [self.A, dict(self.A, id="a2")], "example.test", "geo.cdn.test")
        self.assertIsNone(body)


class Helpers(unittest.TestCase):
    def test_mask(self):
        self.assertEqual(mask("ip 203.0.113.9 v6 2001:db8::1"), "ip <ip> v6 <ip>")

    def test_classify(self):
        self.assertEqual(classify(["203.0.113.9"], "203.0.113.9"), "ORIGIN")
        self.assertEqual(classify(["198.51.100.1"], "203.0.113.9"), "CDN")
        self.assertEqual(classify([], "203.0.113.9"), "EMPTY")

    def test_rt_threshold(self):
        self.assertAlmostEqual(rt_model.h_for(250), 0.269, places=3)
        self.assertAlmostEqual(rt_model.rt(rt_model.h_for(250)), 250, places=6)

    def test_rt_host_hit(self):
        mix = {"html": {"share": 0.4, "hit": 0.5}, "img": {"share": 0.6, "hit": 0.0}}
        self.assertAlmostEqual(rt_model.host_hit(mix), 0.2)

    def test_images_same_host_and_srcset(self):
        html = ('<img src="/wp-content/uploads/a.jpg"><img data-src="https://cdn.other.test/b.png">'
                '<img srcset="https://example.test/c-300.webp 300w, /d.png 600w">')
        self.assertEqual(images(html, "https://example.test/bai/", "example.test"),
                         ["https://example.test/c-300.webp", "https://example.test/d.png",
                          "https://example.test/wp-content/uploads/a.jpg"])

    def test_warm_html_accept_webp(self):
        # Ca thật site VN 27/10/2026: Bunny giữ bản HTML của lượt đầu sau purge; làm nóng bằng Accept */* làm khách nhận bản không WebP.
        import warm
        calls = []

        class R:
            stdout = "HTTP/2 200\ncdn-cache: MISS\n\nCODE=200 T=0.1"

        orig = warm.subprocess.run
        warm.subprocess.run = lambda args, **k: (calls.append(args), R())[1]
        try:
            warm.fetch("https://example.test/", "example.test", "192.0.2.1", "UA", accept=warm.WEBP_ACCEPT)
            warm.fetch("https://example.test/a.png", "example.test", "192.0.2.1", "UA")
        finally:
            warm.subprocess.run = orig
        self.assertIn("Accept: " + warm.WEBP_ACCEPT, calls[0])
        self.assertIn("image/webp", warm.WEBP_ACCEPT)
        self.assertEqual(calls[0][:2], ["curl", "-s"])
        self.assertEqual(calls[0][-1], "https://example.test/")
        self.assertFalse(any(str(x).startswith("Accept:") for x in calls[1]))

    def test_rt_cli(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"html": {"share": 0.5, "hit": 0.8}, "img": {"share": 0.5, "hit": 0.2}}, f)
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "rt_model.py"), "--mix", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("h = 0.500", p.stdout)


if __name__ == "__main__":
    unittest.main()
