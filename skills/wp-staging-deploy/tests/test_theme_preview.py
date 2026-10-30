"""Test offline cho theme_preview_fill.py và mẫu theme-preview.php.tpl."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "theme_preview_fill.py"


def run(*args):
    return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True)


class ThemePreview(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="thp-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_dien_mau_khong_in_ma(self):
        code, out = self.d / "code", self.d / "p.php"
        r = run("--base", "theme-goc", "--preview", "theme-goc-v2", "--code-file", str(code), "--out", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        ma = code.read_text().strip()
        self.assertEqual(len(ma), 32)
        self.assertEqual(stat.S_IMODE(os.stat(code).st_mode), 0o600)
        s = out.read_text(encoding="utf-8")
        self.assertIn("'%s'" % ma, s)
        self.assertNotIn("__", s.split("defined('ABSPATH')")[1])
        self.assertNotIn(ma, r.stdout + r.stderr)
        if shutil.which("php"):
            self.assertEqual(subprocess.run(["php", "-l", str(out)], capture_output=True).returncode, 0)

    def test_doc_lai_ma_cu_va_tu_choi_loi(self):
        code = self.d / "code"
        self.assertEqual(run("--base", "a", "--preview", "b", "--code-file", str(code), "--out", str(self.d / "1.php")).returncode, 0)
        self.assertEqual(run("--base", "a", "--preview", "b", "--code-file", str(code), "--out", str(self.d / "2.php")).returncode, 0)
        self.assertEqual((self.d / "1.php").read_text(), (self.d / "2.php").read_text())
        self.assertEqual(run("--base", "a", "--preview", "b", "--code-file", str(code), "--out", str(self.d / "1.php")).returncode, 2)
        self.assertEqual(run("--base", "a", "--preview", "a", "--code-file", str(code), "--out", str(self.d / "3.php")).returncode, 2)
        self.assertEqual(run("--base", "A B", "--preview", "b", "--code-file", str(code), "--out", str(self.d / "4.php")).returncode, 2)
        os.chmod(code, 0o644)
        self.assertEqual(run("--base", "a", "--preview", "b", "--code-file", str(code), "--out", str(self.d / "5.php")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
