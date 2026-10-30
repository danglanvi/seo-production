#!/usr/bin/env python3
"""Test offline cho scripts/wpx.sh. ssh, scp, flock, sudo, chown và php giả trong PATH. "Server" là thư mục tạm.

Không SSH, không gọi site thật. Chạy: python3 -B tests/test_wpx.py
ssh giả chạy lệnh từ xa bằng bash trên máy, nên test kiểm được cả cách quote biến.
"""
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wpx.sh"
HOST = "edge7.preview.example.test"

FAKES = {
    "ssh": r'''#!/bin/bash
echo "$*" >> "$FAKE_LOG/ssh_argv.log"
echo '** WARNING: connection is not using a post-quantum key exchange algorithm.' >&2
echo '** The server may need to be upgraded. See https://openssh.com/pq.html' >&2
cmd="${@: -1}"
bash -c "$cmd"
''',
    "scp": r'''#!/bin/bash
echo "$*" >> "$FAKE_LOG/scp_argv.log"
src="${@: -2:1}"; dst="${@: -1}"; dst="${dst#*:}"
mkdir -p "$(dirname "$dst")" && cp "$src" "$dst"
''',
    "flock": r'''#!/bin/bash
echo "$*" >> "$FAKE_LOG/flock_argv.log"
[ "$1" = -w ] && shift 2
shift
exec "$@"
''',
    "sudo": r'''#!/bin/bash
[ "$1" = -u ] && { echo "user=$2" >> "$FAKE_LOG/sudo.log"; shift 2; }
exec env "$@"
''',
    "chown": "#!/bin/bash\nexit 0\n",
    "php-fake": r'''#!/bin/bash
echo "PHPARGS $*"
echo "ENV DRY=${DRY-unset} MSG=${MSG-unset} HOME=$HOME"
for a in "$@"; do case "$a" in --path=*) echo "siteurl http://$FAKE_HOST/ path ${a#--path=}" ;; esac; done
exit "${FAKE_PHP_RC:-0}"
''',
}


class WpxTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        t = self.t = Path(self._td.name)
        self.bin = t / "bin"; self.bin.mkdir()
        self.log = t / "log"; self.log.mkdir()
        for name, body in FAKES.items():
            p = self.bin / name; p.write_text(body); p.chmod(p.stat().st_mode | stat.S_IXUSR)
        self.srv = t / "srv"; (self.srv / "prod").mkdir(parents=True)
        self.stg = self.srv / f"stg-{HOST}"; self.stg.mkdir()
        self.home_file = t / "stg_home"; self.home_file.write_text(f"https://{HOST}/\n")
        self.site = t / "site.json"
        self.cfg = {"ssh": "fake-alias", "docroot": str(self.srv / "prod"), "php_bin": str(self.bin / "php-fake"),
                    "wp_bin": "/usr/local/bin/wp", "wp_user": "www", "stg_docroot_glob": str(self.srv / "stg-*"),
                    "wpcli_home": str(t / "wpcli-home"), "wpcli_lock_dir": str(t / "locks")}
        self.write_site()
        self.php = t / "job.php"; self.php.write_text("<?php echo 1;\n")
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_LOG=str(self.log), FAKE_HOST=HOST,
                        STG_HOME_FILE=str(self.home_file))
        for k in ("STG_HOST", "STG_ALIAS", "WPX_SITE", "DRY", "MSG"):
            self.env.pop(k, None)

    def tearDown(self):
        self._td.cleanup()

    def write_site(self):
        self.site.write_text(json.dumps(self.cfg))

    def run_wpx(self, *args, env=None):
        e = dict(self.env, **(env or {}))
        return subprocess.run(["bash", str(SCRIPT), "--site", str(self.site), *args], capture_output=True, text=True, env=e, timeout=60)

    def logged(self, name):
        p = self.log / name
        return p.read_text() if p.exists() else ""

    def test_dry_in_lenh_khong_ssh(self):
        r = self.run_wpx("--dry", "--slot", "2", "--tag", "lane-a", "prod", str(self.php), "DRY=1", "MSG=hai từ")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("wpcli-slot-2.lock", r.stdout)
        self.assertIn("sudo -u www HOME=", r.stdout)
        self.assertIn(" DRY=1 ", r.stdout)
        self.assertIn("-d memory_limit=512M", r.stdout)
        self.assertIn(f"--path={self.srv / 'prod'} eval-file", r.stdout)
        self.assertIn("/lane-a/job.php", r.stdout)
        self.assertEqual(self.logged("ssh_argv.log") + self.logged("scp_argv.log"), "")

    def test_prod_chay_bien_sau_sudo_va_giu_ma_thoat(self):
        r = self.run_wpx("prod", str(self.php), "DRY=1", "MSG=câu có 'nháy' và $HOME", env={"FAKE_PHP_RC": "3"})
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("ENV DRY=1 MSG=câu có 'nháy' và $HOME", r.stdout)
        self.assertIn(f"HOME={self.cfg['wpcli_home']}", r.stdout)
        self.assertIn(f"--path={self.srv / 'prod'}", r.stdout)
        self.assertNotIn("post-quantum", r.stdout + r.stderr)
        self.assertIn("-n -o BatchMode=yes fake-alias", self.logged("ssh_argv.log"))
        self.assertIn("wpcli-slot-1.lock", self.logged("flock_argv.log"))
        self.assertTrue((Path(self.cfg["wpcli_home"]) / "wpx" / "job.php").exists())
        self.assertFalse(list(Path(self.cfg["wpcli_home"]).glob(".up-*")))

    def test_stg_che_host_va_thu_muc(self):
        r = self.run_wpx("stg", str(self.php), "DRY=1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = r.stdout + r.stderr
        self.assertNotIn(HOST, out)
        self.assertNotIn(str(self.stg), out)
        self.assertIn("--path=<stg-root>", out)
        self.assertIn("siteurl http://<stg-host>/", out)

    def test_stg_mau_khop_hai_thu_muc_thi_dung(self):
        (self.srv / "stg-khac").mkdir()
        r = self.run_wpx("stg", str(self.php))
        self.assertEqual(r.returncode, 4)
        self.assertNotIn("PHPARGS", r.stdout)
        self.assertEqual(self.logged("scp_argv.log"), "")

    def test_stg_khong_nap_duoc_host_thi_dung(self):
        self.home_file.unlink()
        r = self.run_wpx("stg", str(self.php))
        self.assertEqual(r.returncode, 4)
        self.assertNotIn("PHPARGS", r.stdout)

    def test_bien_sai_va_ho_so_thieu_khoa(self):
        for bad in ("1X=2", "A;rm=1", "KHONGBANG"):
            r = self.run_wpx("prod", str(self.php), bad)
            self.assertEqual(r.returncode, 2, bad)
        del self.cfg["php_bin"]; self.write_site()
        r = self.run_wpx("prod", str(self.php))
        self.assertEqual(r.returncode, 4)
        self.assertIn("php_bin", r.stderr)
        self.assertEqual(self.logged("ssh_argv.log"), "")


if __name__ == "__main__":
    unittest.main(verbosity=1)
