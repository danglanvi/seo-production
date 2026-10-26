#!/usr/bin/env python3
"""Test offline cho scripts/stg_env.sh, stg_tunnel.sh, stg_get.sh. Dùng ssh và curl giả trong PATH, host giả.

Không SSH, không gọi site thật. Chạy: python3 -B tests/test_stg_helpers.py
"""
import os
import re
import shutil
import socket
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
HOST = "edge7.preview.example.test"  # không khớp regex chung stg-[a-z0-9-]+
PASS = "pw-fake-Zq81"

FAKE_SSH = r'''#!/bin/bash
# ssh giả. -N: giữ tiến trình sống như tunnel. Lệnh khác: in nội dung $FAKE_STG_HOME.
echo "$*" >> "$FAKE_LOG_DIR/ssh_argv.log"
for a in "$@"; do
  if [ "$a" = "-N" ]; then
    [ -n "${FAKE_SSH_DIE_ON_TUNNEL:-}" ] && exit 255
    trap 'kill $! 2>/dev/null; exit 0' TERM
    sleep 300 & wait
    exit 0
  fi
done
echo '** WARNING: connection is not using a post-quantum key exchange algorithm.' >&2
echo '** This session may be vulnerable to "store now, decrypt later" attacks.' >&2
echo '** The server may need to be upgraded. See https://openssh.com/pq.html' >&2
[ -n "${FAKE_SSH_STDERR:-}" ] && echo "$FAKE_SSH_STDERR" >&2
cat "$FAKE_STG_HOME"
exit "${FAKE_SSH_RC:-0}"
'''

FAKE_CURL = r'''#!/bin/bash
# curl giả. Ghi argv và stdin/config, trả mã HTTP lấy lần lượt từ $FAKE_CURL_CODES (dòng cuối lặp lại).
echo "$*" >> "$FAKE_LOG_DIR/curl_argv.log"
out=""; cfg=""
while [ $# -gt 0 ]; do
  case "$1" in -o) out="$2"; shift 2 ;; -K) cfg="$2"; shift 2 ;; *) shift ;; esac
done
if [ "$cfg" = "-" ]; then cat >> "$FAKE_LOG_DIR/curl_cfg.log"; else cat "$cfg" >> "$FAKE_LOG_DIR/curl_cfg.log"; fi
code=$(head -1 "$FAKE_CURL_CODES")
[ "$(wc -l < "$FAKE_CURL_CODES")" -gt 1 ] && sed -i '' 1d "$FAKE_CURL_CODES"
[ -n "$out" ] && [ "$out" != /dev/null ] && cat "$FAKE_CURL_BODY" > "$out"
[ -n "${FAKE_CURL_ERR:-}" ] && echo "$FAKE_CURL_ERR" >&2
printf '%s' "$code"
[ "$code" = 000 ] && exit 7
exit 0
'''


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.t = Path(self._td.name)
        self.bin = self.t / "bin"; self.bin.mkdir()
        self.log = self.t / "log"; self.log.mkdir()
        for name, body in (("ssh", FAKE_SSH), ("curl", FAKE_CURL)):
            p = self.bin / name; p.write_text(body); p.chmod(p.stat().st_mode | stat.S_IXUSR)
        self.home = self.t / "stg_home"; self.home.write_text(f"http://{HOST}/\n")
        self.codes = self.t / "codes"; self.codes.write_text("200\n")
        self.body = self.t / "body"
        self.body.write_text(f'<a href="http://{HOST}/x">l</a>\n{{"u":"http:\\/\\/{HOST}\\/y"}}\n{HOST} lần 2\n')
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_LOG_DIR=str(self.log),
                        FAKE_STG_HOME=str(self.home), FAKE_CURL_CODES=str(self.codes), FAKE_CURL_BODY=str(self.body),
                        STG_ALIAS="fake-alias", STG_RUN_DIR=str(self.t / "run"), STG_WAIT_TRIES="6")
        self.env.pop("STG_HOST", None)

    def tearDown(self):
        for lane in ("default", "a", "b"):
            subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), "down", "--lane", lane, "--port", str(getattr(self, "port", 18094))],
                           env=self.env, capture_output=True, timeout=30)
        for pidf in (self.t / "run").glob("*.pid") if (self.t / "run").exists() else []:
            try: os.kill(int(pidf.read_text()), 9)
            except Exception: pass
        self._td.cleanup()

    def sh(self, script, shell="bash", env=None, **kw):
        return subprocess.run([shell, "-c", script], env=env or self.env, capture_output=True, text=True, timeout=60, **kw)

    def logtext(self, name):
        p = self.log / name
        return p.read_text() if p.exists() else ""


class TestEnv(Base):
    def source(self, body, shell="bash"):
        return self.sh(f'source "{SCRIPTS}/stg_env.sh"; {body}', shell)

    def test_normalize_host_forms(self):
        for raw in (f"http://{HOST}/\n", f"https://{HOST}/wp/path\n", f"{HOST}\n", f"http://{HOST}/\r\n"):
            self.home.write_text(raw)
            for shell in ("bash", "zsh"):
                r = self.source('stg_load; [ "$STG_HOST" = "' + HOST + '" ] && echo OK', shell)
                self.assertIn("OK", r.stdout, (raw, shell, r.stderr))
                self.assertNotIn(HOST, r.stdout + r.stderr)  # stg_load không in host

    def test_invalid_home_content_rejected(self):
        self.home.write_text("<html>lỗi</html>\n")
        r = self.source("stg_load; echo rc=$?")
        self.assertIn("rc=3", r.stdout)

    def test_ssh_keeps_exit_code_through_pipe(self):
        # Ca hỏng thật: pipe qua grep làm mất mã thoát của ssh, lệnh lỗi vẫn báo thành công.
        for shell in ("bash", "zsh"):
            self.env["FAKE_SSH_RC"] = "7"
            r = self.source('SSH fake-alias "cat x" >/dev/null 2>&1; echo rc=$?', shell)
            self.assertIn("rc=7", r.stdout, shell)
            self.env["FAKE_SSH_RC"] = "0"
            r = self.source('SSH fake-alias "cat x" >/dev/null 2>&1; echo rc=$?', shell)
            self.assertIn("rc=0", r.stdout, shell)

    def test_ssh_filters_pq_warning_only(self):
        self.env["FAKE_SSH_STDERR"] = "LỖI thật của lệnh"
        for shell in ("bash", "zsh"):
            r = self.source('SSH fake-alias "cat x"', shell)
            self.assertNotIn("post-quantum", r.stderr)
            self.assertNotIn("store now", r.stderr)
            self.assertIn("LỖI thật của lệnh", r.stderr)
            self.assertIn(HOST, r.stdout)  # stdout nguyên vẹn

    def test_stg_mask_exact_host_and_old_regex_leaks(self):
        # Ca hỏng thật 18/10: regex chung stg-[a-z0-9-]+ để lọt host. stg_mask dùng đúng chuỗi host.
        text = f'<a href="http://{HOST}/x">{HOST}</a> {{"u":"http:\\/\\/{HOST}\\/y"}}\n'
        old = re.sub(r"stg-[a-z0-9-]+", "<stg-host>", text)
        self.assertIn(HOST, old)
        r = self.sh(f'source "{SCRIPTS}/stg_env.sh"; STG_HOST={HOST}; stg_mask', input=text) if False else subprocess.run(
            ["bash", "-c", f'source "{SCRIPTS}/stg_env.sh"; STG_HOST={HOST}; stg_mask'], env=self.env, input=text,
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertNotIn(HOST, r.stdout)
        self.assertEqual(r.stdout.count("<stg-host>"), 3)

    def test_stg_mask_fails_closed_without_host(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPTS}/stg_env.sh"; unset STG_HOST; stg_mask'], env=self.env,
                           input="bí mật\n", capture_output=True, text=True, timeout=30)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_documented_pipe_masks_stderr_and_keeps_rc(self):
        # Dạng ghi ở SKILL.md Bước 2 mục 5: stderr của lệnh từ xa cũng chứa host, phải qua stg_mask.
        self.env["FAKE_SSH_STDERR"] = f"lỗi ở {HOST}"
        self.env["FAKE_SSH_RC"] = "7"
        for shell in ("bash", "zsh"):
            r = self.sh(f'source "{SCRIPTS}/stg_env.sh"; export STG_HOST={HOST}; set -o pipefail; '
                        f'SSH fake-alias "cat x" 2>&1 | stg_mask; echo rc=$?', shell)
            self.assertNotIn(HOST, r.stdout + r.stderr, shell)
            self.assertIn("lỗi ở <stg-host>", r.stdout, shell)
            self.assertNotIn("post-quantum", r.stdout, shell)
            self.assertIn("rc=7", r.stdout, shell)

    def test_stg_load_needs_alias(self):
        self.env.pop("STG_ALIAS")
        r = self.source("stg_load; echo rc=$?")
        self.assertIn("rc=2", r.stdout)

    def test_documented_export_form_works(self):
        # Ca hỏng thật khi viết skill 25/10: dạng `STG_ALIAS=x source stg_env.sh && stg_load` mất biến ở cả bash và zsh.
        self.env.pop("STG_ALIAS")
        for shell in ("bash", "zsh"):
            bad = self.sh(f'STG_ALIAS=fake-alias source "{SCRIPTS}/stg_env.sh" && stg_load; echo rc=$?', shell)
            self.assertIn("rc=2", bad.stdout, shell)
            ok = self.sh(f'export STG_ALIAS=fake-alias; source "{SCRIPTS}/stg_env.sh" && stg_load; echo rc=$?', shell)
            self.assertIn("rc=0", ok.stdout, (shell, ok.stderr))


class TestGet(Base):
    def get(self, *a, **kw):
        return subprocess.run(["bash", str(SCRIPTS / "stg_get.sh"), *a], env=self.env, capture_output=True, text=True,
                              timeout=60, **kw)

    def test_masks_output_and_keeps_host_out_of_argv(self):
        auth = self.t / "auth.txt"
        auth.write_text(f"user=u1\npassword={PASS}\nsite=x\ncreated=y\n")
        r = self.get("--auth-file", str(auth), "/trang-thu/")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(HOST, r.stdout + r.stderr)
        self.assertEqual(r.stdout.count("<stg-host>"), 3)
        self.assertNotIn(HOST, self.logtext("curl_argv.log"))
        self.assertNotIn(PASS, self.logtext("curl_argv.log"))
        cfg = self.logtext("curl_cfg.log")
        self.assertIn(f"connect-to = \"{HOST}:80:127.0.0.1:18094\"", cfg)
        self.assertIn(f"u1:{PASS}", cfg)
        self.assertIn("Mozilla/5.0", cfg)
        self.assertIn("http=200", r.stderr)

    def test_auth_stdin_user_pass_line(self):
        r = self.get("--auth-stdin", "/", input=f"u2:{PASS}\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"u2:{PASS}", self.logtext("curl_cfg.log"))
        self.assertNotIn(PASS, r.stdout + r.stderr)

    def test_auth_server_secrets_format(self):
        # Ca hỏng thật: file secret của staging có STG_URL ở dòng đầu. Bản cũ lấy dòng đó làm user:pass.
        auth = self.t / "stg-secrets.env"
        auth.write_text(f"STG_URL=http://{HOST}/\nSTG_DB_PASS='db-fake-77'\nSTG_BASIC_USER=u3\nSTG_BASIC_PASS=\"{PASS}\"\n")
        r = self.get("--auth-file", str(auth), "/")
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = self.logtext("curl_cfg.log")
        self.assertIn(f'user = "u3:{PASS}"', cfg)
        self.assertNotIn("STG_URL", cfg)

    def test_auth_keyvalue_without_user_pass_refused(self):
        auth = self.t / "x.env"
        auth.write_text(f"STG_URL=http://{HOST}/\nSTG_DB_PASS=db-fake-77\n")
        r = self.get("--auth-file", str(auth), "/")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.logtext("curl_argv.log"), "")
        self.assertNotIn(HOST, r.stdout + r.stderr)

    def test_auth_parse_in_zsh(self):
        r = subprocess.run(["zsh", "-c", f'source "{SCRIPTS}/stg_env.sh"; stg_auth_parse'], env=self.env,
                           input=f"user=u4\npassword={PASS}\nsite=x\n", capture_output=True, text=True, timeout=30)
        self.assertEqual(r.stdout.strip(), f"u4:{PASS}", r.stderr)

    def test_http_codes(self):
        self.codes.write_text("401\n")
        self.assertEqual(self.get("/").returncode, 1)
        self.codes.write_text("000\n")
        r = self.get("/")
        self.assertEqual(r.returncode, 3)
        self.assertIn("stg_tunnel.sh status", r.stderr)

    def test_curl_error_text_is_masked(self):
        self.env["FAKE_CURL_ERR"] = f"curl: (7) Failed to connect to {HOST} port 80"
        self.codes.write_text("000\n")
        r = self.get("/")
        self.assertNotIn(HOST, r.stderr)

    def test_out_file_masked_and_no_overwrite(self):
        out = self.t / "o.html"
        r = self.get("--out", str(out), "/")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn(HOST, out.read_text())
        self.assertEqual(self.get("--out", str(out), "/").returncode, 2)
        self.assertEqual(self.get("--out", str(out), "--force", "/").returncode, 0)

    def test_usage_errors(self):
        self.assertEqual(self.get("khong-co-slash").returncode, 2)
        self.assertEqual(self.get("--port", "abc", "/").returncode, 2)
        self.assertEqual(self.get("--bogus").returncode, 2)
        self.assertEqual(self.get("--help").returncode, 0)

    def test_ssh_failure_stops_before_curl(self):
        self.env["FAKE_SSH_RC"] = "5"
        r = self.get("/")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.logtext("curl_argv.log"), "")


class TestTunnel(Base):
    def tun(self, *a):
        return subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), *a, "--port", str(self.port)], env=self.env,
                              capture_output=True, text=True, timeout=120)

    def setUp(self):
        super().setUp()
        self.port = free_port()

    def test_up_status_down(self):
        r = self.tun("up")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(HOST, r.stdout + r.stderr)
        s = self.tun("status")
        self.assertEqual(s.returncode, 0)
        self.assertIn("alive=yes health=200", s.stdout)
        self.assertNotIn(HOST, s.stdout)
        again = self.tun("up")
        self.assertIn("đang sống", again.stdout)
        self.assertEqual(self.logtext("ssh_argv.log").count("-N"), 1)
        opts = self.logtext("ssh_argv.log")
        self.assertIn("ServerAliveInterval=15", opts)
        self.assertIn("ExitOnForwardFailure=yes", opts)
        d = self.tun("down")
        self.assertEqual(d.returncode, 0)
        self.assertEqual(self.tun("status").returncode, 1)

    def test_health_request_sends_host_via_stdin_not_argv(self):
        self.tun("up")
        self.assertNotIn(HOST, self.logtext("curl_argv.log"))
        self.assertIn(f"Host: {HOST}", self.logtext("curl_cfg.log"))

    def test_stale_pid_file_reconnects(self):
        # Ca hỏng thật: tunnel rớt thầm, pid file còn. up phải nối lại, status phải báo chết.
        self.assertEqual(self.tun("up").returncode, 0)
        pidf = self.t / "run" / "default.pid"
        old = int(pidf.read_text())
        os.kill(old, 9)
        st = self.tun("status")
        self.assertEqual(st.returncode, 1)
        self.assertIn("alive=no", st.stdout)
        self.assertEqual(self.tun("up").returncode, 0)
        self.assertNotEqual(int(pidf.read_text()), old)

    def test_hung_tunnel_is_restarted(self):
        # Tiến trình sống nhưng không trả lời (000): up kill và mở lại.
        self.assertEqual(self.tun("up").returncode, 0)
        pidf = self.t / "run" / "default.pid"
        old = int(pidf.read_text())
        self.codes.write_text("000\n200\n")
        r = self.tun("up")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nối lại", r.stderr)
        self.assertNotEqual(int(pidf.read_text()), old)

    def test_up_fails_with_nonzero_when_never_healthy(self):
        self.codes.write_text("000\n")
        r = self.tun("up", "--retries", "1")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.tun("status").returncode, 1)

    def test_ssh_dies_immediately(self):
        self.env["FAKE_SSH_DIE_ON_TUNNEL"] = "1"
        r = self.tun("up", "--retries", "2")
        self.assertEqual(r.returncode, 1)

    def test_foreign_port_user_not_killed(self):
        s = socket.socket(); s.bind(("127.0.0.1", self.port)); s.listen(1)
        try:
            r = self.tun("up")
            self.assertEqual(r.returncode, 1)
            self.assertIn("tiến trình khác", r.stderr)
        finally:
            s.close()

    def test_down_refuses_unrelated_pid(self):
        p = subprocess.Popen(["sleep", "60"])
        try:
            (self.t / "run").mkdir(exist_ok=True)
            (self.t / "run" / "default.pid").write_text(str(p.pid))
            r = self.tun("down")
            self.assertEqual(r.returncode, 1)
            self.assertIsNone(p.poll())
        finally:
            p.kill(); p.wait()

    def test_lanes_are_independent(self):
        p2 = free_port()
        a = subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), "up", "--lane", "a", "--port", str(self.port)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        b = subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), "up", "--lane", "b", "--port", str(p2)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stderr + b.stderr)
        subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), "down", "--lane", "b", "--port", str(p2)], env=self.env,
                       capture_output=True, timeout=30)
        self.assertEqual(self.tun("status", "--lane", "a").returncode, 0)
        subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), "down", "--lane", "a", "--port", str(self.port)],
                       env=self.env, capture_output=True, timeout=30)

    def test_usage_errors(self):
        run = lambda *a: subprocess.run(["bash", str(SCRIPTS / "stg_tunnel.sh"), *a], env=self.env, capture_output=True,
                                        text=True, timeout=30)
        self.assertEqual(run().returncode, 2)
        self.assertEqual(run("up", "--lane", "../x").returncode, 2)
        self.assertEqual(run("up", "--port", "x").returncode, 2)
        self.assertEqual(run("bogus").returncode, 2)
        self.assertEqual(run("--help").returncode, 0)


class TestLeakCheck(Base):
    def setUp(self):
        super().setUp()
        self.d = self.t / "dot"; self.d.mkdir()
        (self.d / "sach.md").write_text("Staging <stg-host> trả 200.\n")
        self.auth = self.t / "auth.txt"; self.auth.write_text(f"user=u1\npassword={PASS}\n")

    def scan(self, *a):
        return subprocess.run(["bash", str(SCRIPTS / "stg_leak_check.sh"), str(self.d), *a], env=self.env,
                              capture_output=True, text=True, timeout=60)

    def assert_quiet(self, r):
        self.assertNotIn(HOST, r.stdout + r.stderr)
        self.assertNotIn(PASS, r.stdout + r.stderr)

    def test_clean_dir(self):
        r = self.scan("--auth-file", str(self.auth))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sạch", r.stdout)
        self.assertIn("-n", self.logtext("ssh_argv.log"))  # stg_load qua SSH()

    def test_host_in_html_and_json_escaped(self):
        # Ca hỏng thật 18/10: host staging lộ trong file evidence vì lệnh không pipe qua bộ che.
        (self.d / "a.html").write_text(f'<a href="http://{HOST}/x">x</a>')
        (self.d / "b.json").write_text('{"u":"http:\\/\\/' + HOST + '\\/y"}')
        r = self.scan()
        self.assertEqual(r.returncode, 1)
        self.assertIn("a.html", r.stdout)
        self.assertIn("b.json", r.stdout)
        self.assert_quiet(r)

    def test_password_in_binary_and_filename(self):
        (self.d / "shot.png").write_bytes(b"\x89PNG\x00\x01" + PASS.encode() + b"\x00\xff")
        (self.d / f"log-{HOST}.txt").write_text("rỗng\n")
        r = self.scan("--auth-file", str(self.auth))
        self.assertEqual(r.returncode, 1)
        self.assertIn("shot.png", r.stdout)
        self.assertIn("LỘ tên file [host staging]", r.stdout)
        self.assertIn("log-***.txt", r.stdout)
        self.assert_quiet(r)

    def test_env_file_db_pass_and_url_host(self):
        env = self.t / "stg-secrets.env"
        env.write_text("STG_URL=https://edge9.other.example.test/\nSTG_DB_PASS='db-fake-7781'\nSTG_DB_NAME=dbx\n")
        (self.d / "c.txt").write_text("mysql -p db-fake-7781 và edge9.other.example.test\n")
        r = self.scan("--no-host", "--env-file", str(env))
        self.assertEqual(r.returncode, 1)
        self.assertIn("STG_DB_PASS@stg-secrets.env", r.stdout)
        self.assertIn("STG_URL@stg-secrets.env (host)", r.stdout)
        self.assertNotIn("db-fake-7781", r.stdout + r.stderr)
        self.assertNotIn("edge9.other", r.stdout + r.stderr)

    def test_patterns(self):
        # Ghép chuỗi lúc chạy để file test không tự khớp mẫu khi quét thư mục skill.
        (self.d / "d.txt").write_text("vào /wp-login.php" + "?abc123 và AIza" + "SyFAKEfakeFAKEfake12345\n")
        nf = self.t / "needles.txt"; nf.write_text("# ghi chú\n\nkhong-co-trong-thu-muc-91\n")
        r = self.scan("--no-host", "--needle-file", str(nf))
        self.assertEqual(r.returncode, 1)
        self.assertIn("wp-login", r.stdout)
        self.assertIn("AIza", r.stdout)

    def test_no_host_source_stops(self):
        self.env.pop("STG_ALIAS")
        r = self.scan("--auth-file", str(self.auth))
        self.assertEqual(r.returncode, 2)
        self.assertIn("--no-host", r.stderr)

    def test_no_needle_and_usage(self):
        self.assertEqual(self.scan("--no-host").returncode, 2)
        self.assertEqual(self.scan("--bogus").returncode, 2)
        self.assertEqual(subprocess.run(["bash", str(SCRIPTS / "stg_leak_check.sh"), "--help"], env=self.env,
                                        capture_output=True, timeout=30).returncode, 0)


if __name__ == "__main__":
    unittest.main()
