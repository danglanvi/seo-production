# Test offline cho cdn_monitor.py: máy trạng thái báo lỗi, hoàn tác khi gửi lỗi, nội dung tin, trạng thái hỏng, plist.
# Không gọi mạng, không gửi tin. Ca lấy từ rà soát đối kháng 26/10/2026 (3 agent, 35 phát hiện).
import copy
import json
import os
import sys
import tempfile
import unittest
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cdn_monitor as m  # noqa: E402

CFG = dict(copy.deepcopy(m.DEFAULTS), domain="example.test", unswitch_hint="python3 t8.py unswitch --apply",
           label="vn.test.cdn-monitor", state_dir="/tmp/cdn-monitor-test", config_path="/tmp/a b & c/site.json", alert_cmd=["echo"])


def rounds(st, key, seq, t0=0, sched=()):
    out = []
    for i, ok in enumerate(seq):
        a, r = m.evaluate(st, {key: (ok, "x")}, t0 + i * 300, CFG, set(sched))
        out.append((len(a), len(r)))
    return out


class Evaluate(unittest.TestCase):
    def test_alert_after_two_rounds(self):
        st = {}
        self.assertEqual(rounds(st, "origin_http", [False, False]), [(0, 0), (1, 0)])
        self.assertEqual(st["checks"]["origin_http"]["since"], 0)

    def test_intermittent_alerts_by_window(self):
        # Lỗi xen kẽ: trước đây không bao giờ báo. Nay báo khi 3 lỗi trong 6 vòng.
        st = {}
        res = rounds(st, "origin_http", [False, True, False, True, False])
        self.assertEqual(sum(a for a, _ in res), 1)
        self.assertEqual(res[-1][0], 1)

    def test_no_repeat_before_repeat_min(self):
        st = {}
        res = rounds(st, "cdn_http", [False] * 6)
        self.assertEqual(sum(a for a, _ in res), 1)
        a, _ = m.evaluate(st, {"cdn_http": (False, "x")}, 300 + 120 * 60, CFG, set())
        self.assertEqual(len(a), 1)

    def test_recovery_needs_two_ok_rounds(self):
        st = {}
        rounds(st, "vn_lech", [False, False])
        res = rounds(st, "vn_lech", [True, True], t0=600)
        self.assertEqual(res, [(0, 0), (0, 1)])

    def test_scheduled_key_alerts_and_recovers_at_once(self):
        st = {}
        self.assertEqual(rounds(st, "cert_cdn", [False, True], sched=["cert_cdn"]), [(1, 0), (0, 1)])

    def test_money_repeats_daily_not_two_hours(self):
        st = {}
        rounds(st, "cdn_tien", [False], sched=["cdn_tien"])
        a, _ = m.evaluate(st, {"cdn_tien": (False, "x")}, 3 * 3600, CFG, {"cdn_tien"})
        self.assertEqual(a, [])
        a, _ = m.evaluate(st, {"cdn_tien": (False, "x")}, 24 * 3600 + 1, CFG, {"cdn_tien"})
        self.assertEqual(len(a), 1)

    def test_missing_fields_tolerated(self):
        st = {"checks": {"origin_http": {"alerted": 5}}}
        m.evaluate(st, {"origin_http": (False, "x")}, 600, CFG, set())
        self.assertEqual(st["checks"]["origin_http"]["fail"], 1)

    def test_absent_key_untouched(self):
        st = {"checks": {"xa_nhan_origin": {"fail": 1, "since": 5, "alerted": 5}}}
        m.evaluate(st, {"origin_http": (True, "ok")}, 600, CFG, set())
        self.assertEqual(st["checks"]["xa_nhan_origin"]["fail"], 1)


class RevertUnsent(unittest.TestCase):
    def test_failed_send_is_retried_next_round(self):
        st = {}
        rounds(st, "origin_http", [False])
        prev = copy.deepcopy(st["checks"])
        a, r = m.evaluate(st, {"origin_http": (False, "x")}, 300, CFG, set())
        self.assertEqual(len(a), 1)
        m.revert_unsent(st, prev, a, r)
        self.assertNotIn("alerted", st["checks"]["origin_http"])
        a, _ = m.evaluate(st, {"origin_http": (False, "x")}, 600, CFG, set())
        self.assertEqual(len(a), 1)

    def test_failed_recovery_is_retried(self):
        st = {}
        rounds(st, "cdn_http", [False, False, True])
        prev = copy.deepcopy(st["checks"])
        a, r = m.evaluate(st, {"cdn_http": (True, "ok")}, 900, CFG, set())
        self.assertEqual(len(r), 1)
        m.revert_unsent(st, prev, a, r)
        self.assertIn("alerted", st["checks"]["cdn_http"])
        _, r = m.evaluate(st, {"cdn_http": (True, "ok")}, 1200, CFG, set())
        self.assertEqual(len(r), 1)


class Compose(unittest.TestCase):
    def test_cdn_failure_has_unswitch_and_no_ip(self):
        msg = m.compose(CFG, [("cdn_http", "lỗi tới 203.0.113.9", 0)], [], 600)
        self.assertIn("LỖI NGHIÊM TRỌNG", msg)
        self.assertIn("unswitch --apply", msg)
        self.assertNotIn("203.0.113.9", msg)

    def test_origin_failure_has_no_unswitch(self):
        msg = m.compose(CFG, [("origin_http", "mã 502", 0)], [], 600)
        self.assertIn("LỖI NGHIÊM TRỌNG", msg)
        self.assertNotIn("unswitch", msg)
        self.assertIn("Chưa nên trả DNS", msg)

    def test_warning_has_no_unswitch(self):
        msg = m.compose(CFG, [("vn_lech", "google CDN", 0)], [], 600)
        self.assertIn("Cảnh báo", msg)
        self.assertNotIn("unswitch", msg)

    def test_partial_ns_line_suppressed_when_all_down(self):
        msg = m.compose(CFG, [("ns_cdn", "a KHÔNG", 0), ("ns_cdn_mot", "a KHÔNG", 0)], [], 600)
        self.assertNotIn(m.TEN["ns_cdn_mot"], msg)

    def test_api_error_is_not_critical(self):
        msg = m.compose(CFG, [("cdn_api", "HTTP 503", 0)], [], 600)
        self.assertIn("Cảnh báo", msg)
        self.assertNotIn("unswitch", msg)

    def test_notes_only(self):
        self.assertIn("gián đoạn", m.compose(CFG, [], [], 0, ["[CDN x] Giám sát bị gián đoạn 30 phút"]))

    def test_empty(self):
        self.assertEqual(m.compose(CFG, [], [], 0), "")

    def test_resolver_labels_are_not_ips(self):
        for v in CFG["resolver_labels"].values():
            self.assertEqual(m.mask(v), v)

    def test_every_key_has_name(self):
        for k in m.CRIT | m.UNSWITCH | set(m.REPEAT_MIN) | set(m.SUPPRESS) | {"vn_lech", "xa_nhan_origin", "vn_lech_gp"}:
            self.assertIn(k, m.TEN)


class State(unittest.TestCase):
    def test_broken_state_is_quarantined(self):
        d = tempfile.mkdtemp()
        sp = os.path.join(d, "state.json")
        open(sp, "w").write("{cắt dở")
        errors = []
        self.assertEqual(m.load_state(sp, errors), {})
        self.assertEqual(len(errors), 1)
        self.assertFalse(os.path.exists(sp))
        self.assertTrue(any(f.startswith("state.json.hong-") for f in os.listdir(d)))

    def test_save_roundtrip(self):
        d = tempfile.mkdtemp()
        sp = os.path.join(d, "state.json")
        m.save_state(sp, {"a": 1})
        self.assertEqual(json.load(open(sp)), {"a": 1})


class Send(unittest.TestCase):
    def test_missing_binary_returns_false(self):
        cfg = dict(CFG, alert_cmd=["/khong/co/hermes"])
        self.assertFalse(m.send(cfg, "x", False))


class Plist(unittest.TestCase):
    def test_valid_xml_escaped_path_stdout_devnull(self):
        body = m.plist(CFG)
        doc = xml.dom.minidom.parseString(body)
        strings = [n.firstChild.nodeValue for n in doc.getElementsByTagName("string") if n.firstChild]
        self.assertIn("/tmp/a b & c/site.json", strings)
        self.assertIn("/dev/null", strings)
        self.assertIn("<integer>300</integer>", body)


class Round2(unittest.TestCase):
    # Ca từ vòng kiểm lại 26/10/2026 23:1x.
    def test_dead_origin_has_no_unswitch_even_with_cdn_origin(self):
        msg = m.compose(CFG, [("origin_http", "mã 502", 0), ("cdn_origin", "mã 502", 0)], [], 600)
        self.assertNotIn("unswitch", msg)
        self.assertIn("Chưa nên trả DNS", msg)

    def test_cdn_origin_alone_has_unswitch(self):
        self.assertIn("unswitch", m.compose(CFG, [("cdn_origin", "mã 502", 0)], [], 600))

    def test_single_failure_after_recovery_not_alerted(self):
        st = {}
        res = rounds(st, "origin_http", [False, False, True, True, False])
        self.assertEqual(sum(a for a, _ in res), 1)

    def test_mask_ipv6_tail(self):
        self.assertEqual(m.mask("x 2606:4700::6810:84e5 y"), "x <ip> y")


class RunFlow(unittest.TestCase):
    # Chạy run() với mạng, gửi tin và đồng hồ giả. Không gọi mạng.
    def setUp(self):
        self.d = tempfile.mkdtemp()
        open(os.path.join(self.d, "origin"), "w").write("203.0.113.9")
        self.cfg = dict(CFG, state_dir=os.path.join(self.d, "st"), config_path=os.path.join(self.d, "site.json"),
                        origin_file=os.path.join(self.d, "origin"), heartbeat_hour=None, bunny_billing=False,
                        globalping_every_min=10 ** 9, geo_ns=[], cf_ns=[])
        self.sent, self.net, self.t = [], [True], [1_000_000.0]
        self.orig = {k: getattr(m, k) for k in ("net_ok", "check_round", "send", "check_account")}
        self.orig_time = m.time.time
        m.net_ok = lambda: self.net[0]
        m.check_round = lambda cfg, origin, errors: ({"origin_http": (True, "mã 200")}, None)
        m.send = lambda cfg, msg, dry: (self.sent.append(msg) or True)
        m.time.time = lambda: self.t[0]

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(m, k, v)
        m.time.time = self.orig_time

    def tick(self, sec=300, net=True):
        self.t[0] += sec
        self.net[0] = net
        return m.run(self.cfg, False)

    def test_gap_note_survives_offline_wakeup(self):
        self.tick()
        self.tick(3 * 3600, net=False)  # máy dậy sau 3 giờ, chưa có mạng
        self.assertEqual(self.sent, [])
        self.tick()
        self.assertTrue(any("gián đoạn" in x for x in self.sent))
        n = len(self.sent)
        self.tick()
        self.assertEqual(len(self.sent), n)  # không gửi lặp

    def test_gap_note_retried_after_failed_send(self):
        self.tick()
        m.send = lambda cfg, msg, dry: False
        self.tick(3 * 3600)
        m.send = lambda cfg, msg, dry: (self.sent.append(msg) or True)
        self.tick()
        self.assertTrue(any("gián đoạn" in x for x in self.sent))

    def test_account_network_error_alerts(self):
        self.cfg["bunny_billing"] = True

        def boom(cfg, now_local):
            raise OSError("timeout")
        m.check_account = boom
        self.tick()
        self.tick(900)
        self.assertTrue(any(m.TEN["cdn_api"] in x for x in self.sent))

    def test_dry_writes_no_state(self):
        self.t[0] += 300
        m.run(self.cfg, True)
        self.assertFalse(os.path.exists(os.path.join(self.cfg["state_dir"], "state.json")))


if __name__ == "__main__":
    unittest.main()
