#!/usr/bin/env python3
"""Test offline cho tools/capabilities.py: bảng giả, lệnh giả, thư mục tạm. Không cần mạng, không cần model.

Chạy: python3 -m unittest discover -s tools/tests -p test_capabilities.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "capabilities.py"
SECRET = "supersecretvalue987"

spec = importlib.util.spec_from_file_location("capabilities", SCRIPT)
cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap)

FAKE_TABLE = """# Bảng giả

| Lệnh | Việc |
|---|---|
| `khong-phai-bang-tool` | bảng khác, script phải bỏ qua |

| id | tool | dùng cho việc gì | lệnh kiểm | trạng thái | fallback khi thiếu | skill dùng |
|---|---|---|---|---|---|---|
| `ok1` | Tool có | thử | `echo ready` | ok | không cần | a |
| `bad1` | Tool thiếu | thử | `echo thieu-roi; exit 3` | missing | dùng cách tay | b |
| `slow` | Tool chậm | thử | `sleep 5` | missing | chờ | c |
| `piped` | Lệnh có dấu ống | thử | `echo a \\| tr a b` | ok | không cần | d |
| `leak` | Lệnh in secret | thử | `cat .agent-secrets/.env; echo sk-abcdefghijklmnopqrstu` | ok | không cần | e |
| `haskey` | Key trong .env | thử | `python3 tools/capabilities.py key FAKE_CAP_KEY` | ok | không cần | f |
| `longleak` | Secret ở chỗ cắt chữ | thử | `echo "$(printf 'a %.0s' $(seq 1 42))$(sed -n 's/^FAKE_CAP_KEY=//p' .agent-secrets/.env)"` | ok | không cần | g |
"""


def make_repo(table=FAKE_TABLE):
    root = Path(tempfile.mkdtemp(prefix="cap-test-"))
    (root / "tools").mkdir()
    shutil.copy(SCRIPT, root / "tools" / "capabilities.py")
    if table is not None:
        (root / "tools" / "capabilities.md").write_text(table, encoding="utf-8")
    (root / ".agent-secrets").mkdir()
    (root / ".agent-secrets" / ".env").write_text("FAKE_CAP_KEY=%s\nexport OTHER_TOKEN='%s-2'\n" % (SECRET, SECRET),
                                                encoding="utf-8")
    return root


def run(root, *args, env_extra=None, path=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("FAKE_")}
    env.update(env_extra or {})
    if path is not None:
        env["PATH"] = path
    proc = subprocess.run([sys.executable, str(root / "tools" / "capabilities.py"), *args],
                          cwd=str(root), env=env, capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


class ParseTest(unittest.TestCase):
    def setUp(self):
        self.root = make_repo()
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_reads_only_tool_table(self):
        rows = cap.load_table(self.root / "tools" / "capabilities.md")
        self.assertEqual(list(rows), ["ok1", "bad1", "slow", "piped", "leak", "haskey", "longleak"])
        self.assertEqual(rows["ok1"]["cmd"], "echo ready")
        self.assertEqual(rows["bad1"]["fallback"], "dùng cách tay")
        self.assertEqual(rows["piped"]["cmd"], "echo a | tr a b")

    def test_bad_tables(self):
        cases = {
            "id trùng": FAKE_TABLE + "| `ok1` | lặp | thử | `echo x` | ok | - | - |\n",
            "thiếu lệnh kiểm": FAKE_TABLE.replace("`echo ready`", "chạy tay"),
            "id không hợp lệ": FAKE_TABLE.replace("`ok1`", "`Ok_1`"),
            "không có bảng": "# Trống\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        }
        for name, text in cases.items():
            with self.subTest(name):
                path = self.root / "tools" / "capabilities.md"
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(cap.TableError):
                    cap.load_table(path)

    def test_need_syntax(self):
        self.assertEqual(cap.parse_need("a,b?,c"), [("a", False), ("b", True), ("c", False)])
        self.assertEqual(cap.parse_need(" a , b? ,"), [("a", False), ("b", True)])
        self.assertEqual(cap.parse_need("a?,a"), [("a", False)])
        self.assertEqual(cap.parse_need("a,a?"), [("a", False)])
        for bad in ("", " , ", "?", "a,?"):
            with self.subTest(bad), self.assertRaises(ValueError):
                cap.parse_need(bad)


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.root = make_repo()
        self.addCleanup(shutil.rmtree, self.root, True)

    def check_json(self, need, *extra):
        code, out, err = run(self.root, "check", "--need", need, "--json", *extra)
        return code, json.loads(out) if out.strip() else None, err

    def test_all_required_ok_exit_0(self):
        code, data, _ = self.check_json("ok1,piped")
        self.assertEqual(code, 0)
        self.assertTrue(data["ok"])
        self.assertEqual([r["status"] for r in data["results"]], ["ok", "ok"])
        self.assertEqual(data["results"][1]["detail"], "b")

    def test_required_missing_exit_1(self):
        code, data, _ = self.check_json("ok1,bad1")
        self.assertEqual(code, 1)
        self.assertEqual(data["missing_required"], ["bad1"])
        self.assertEqual(data["results"][1]["detail"], "thieu-roi")

    def test_optional_missing_exit_0(self):
        code, out, _ = run(self.root, "check", "--need", "ok1,bad1?")
        self.assertEqual(code, 0)
        self.assertIn("missing", out)
        self.assertIn("tuỳ chọn", out)
        self.assertIn("fallback bad1: dùng cách tay", out)

    def test_unknown_id_exit_2(self):
        code, out, err = run(self.root, "check", "--need", "ok1,khong-co?")
        self.assertEqual(code, 2)
        self.assertIn("khong-co", err)
        self.assertEqual(out, "")

    def test_bad_need_exit_2(self):
        code, _, err = run(self.root, "check", "--need", "ok1,?")
        self.assertEqual(code, 2)
        self.assertIn("?", err)

    def test_timeout_counts_missing(self):
        start = time.time()
        code, data, _ = self.check_json("slow", "--timeout", "1")
        self.assertLess(time.time() - start, 4.5)
        self.assertEqual(code, 1)
        self.assertEqual(data["results"][0]["detail"], "quá 1 s")

    def test_no_secret_in_output(self):
        for args in (("check", "--need", "leak,haskey,longleak"), ("check", "--need", "leak,haskey,longleak", "--json")):
            with self.subTest(args):
                code, out, err = run(self.root, *args)
                self.assertEqual(code, 0)
                self.assertNotIn(SECRET[:8], out + err)
                self.assertNotIn("abcdefghijklmnopqrstu", out + err)
                self.assertIn(cap.HIDDEN, out)
                self.assertIn("FAKE_CAP_KEY: có", out)

    def test_missing_table_exit_2(self):
        (self.root / "tools" / "capabilities.md").unlink()
        code, _, err = run(self.root, "check", "--need", "ok1")
        self.assertEqual(code, 2)
        self.assertIn("capabilities.md", err)

    def test_list(self):
        code, out, _ = run(self.root, "list", "--json")
        self.assertEqual(code, 0)
        self.assertEqual([r["id"] for r in json.loads(out)][:2], ["ok1", "bad1"])


class HelperTest(unittest.TestCase):
    def setUp(self):
        self.root = make_repo()
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_key_from_env_file_and_environment(self):
        code, out, _ = run(self.root, "key", "FAKE_CAP_KEY", "FAKE_ENV_ONLY", env_extra={"FAKE_ENV_ONLY": "abc-123-xyz"})
        self.assertEqual(code, 0)
        self.assertEqual(out.split("\n")[:2], ["FAKE_CAP_KEY: có", "FAKE_ENV_ONLY: có"])
        self.assertNotIn(SECRET, out)
        self.assertNotIn("abc-123-xyz", out)

    def test_key_missing_and_bad_name(self):
        self.assertEqual(run(self.root, "key", "FAKE_NOT_SET")[0], 1)
        self.assertEqual(run(self.root, "key", "bad-name")[0], 2)

    def test_gws_auth(self):
        fakebin = self.root / "bin"
        fakebin.mkdir()
        status = {"has_refresh_token": True, "token_valid": True, "refresh_token": "1//" + SECRET,
                  "scopes": ["https://www.googleapis.com/auth/webmasters.readonly", "openid"]}
        gws = fakebin / "gws"
        gws.write_text("#!/bin/sh\necho 'Using keyring backend: keyring' >&2\ncat <<'EOF'\n%s\nEOF\n" % json.dumps(status),
                       encoding="utf-8")
        gws.chmod(0o755)
        path = "%s:/usr/bin:/bin" % fakebin
        code, out, _ = run(self.root, "gws-auth", "webmasters.readonly", path=path)
        self.assertEqual(code, 0)
        self.assertIn("có scope webmasters.readonly", out)
        self.assertNotIn(SECRET, out)
        code, out, _ = run(self.root, "gws-auth", "drive", path=path)
        self.assertEqual(code, 1)
        self.assertIn("thiếu scope drive", out)
        code, out, _ = run(self.root, "gws-auth", path="/usr/bin:/bin")
        self.assertEqual(code, 1)
        self.assertIn("chưa cài", out)


if __name__ == "__main__":
    unittest.main()
