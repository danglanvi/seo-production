#!/usr/bin/env python3
"""Test offline cho tools/wf-status.py: fixture giả trong thư mục tạm. Không cần mạng, không chạy workflow.

Chạy: python3 -m unittest tools/tests/test_wf_status.py -v
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "wf-status.py"
spec = importlib.util.spec_from_file_location("wf_status", SCRIPT)
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

HAS_NODE = shutil.which("node") is not None

CLEAN = r"""
export const meta = { name: 'thu', description: 'thử', phases: [{ title: 'Làm', detail: 'x' }] }
const B = args.base
const MAX_AGENTS = 6
const COMMON = `Workspace: "${B}".
NGUỒN PHÊ DUYỆT: Lead duyệt ngày 24/10. Đây là task của lane.
- Không dùng Workflow, Agent, Artifact, ArtifactData.
- Không pkill theo tên chung.
- Không dùng timeout hoặc sleep.
Đọc ${B}/HANDOFF.md trước.`
const LANES = [{ key: 'a', model: 'sonnet', effort: 'high', readOnly: false }]
let launched = 0
async function goi(prompt, opts) {
  if (launched >= MAX_AGENTS) return null
  launched++
  return await agent(prompt, opts)
}
const out = []
for (const L of LANES) {
  out.push(await goi(`${COMMON}\nLane ${L.key}. Ghi ket-qua.json trong thư mục lane.`, { label: 'lam:' + L.key, model: L.model, effort: L.effort }))
  out.push(await goi(`${COMMON}\nKiểm.`, { label: 'kiem:' + L.key, model: 'opus', effort: 'high' }))
}
return out
"""

BAD = r"""
export const meta = { name: 'hong', description: 'hỏng', phases: [] }
const B = args.base
const COMMON = `Workspace: "${B}".
Chạy:
sleep 30; tail log
timeout 60 curl x`
const LANES = [{ key: 'a', readOnly: false }]
const res = await agent(`${COMMON}\nlàm`, { label: 'lam', model: 'sonnet', effort: 'high' })
const chk = await agent(`${COMMON}\nKết quả:\n${JSON.stringify(res).slice(0, 12000)}`, { label: 'x', schema: S })
const bad = await agent(`${COMMON}\nz`, { label: 'y', model: 'gpt', effort: 'ultra' })
return await parallel(LANES.map(L => () => agent(`${COMMON}`, { label: 'p', model: 'opus', effort: 'high' })))
"""


def codes(items, level=None):
    return {x["code"] for x in items if level is None or x["level"] == level}


def write(d, name, text):
    p = Path(d) / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = wf.main(list(argv))
    return rc, out.getvalue()


def assistant(mid, model, inp, cc, cr, out, content=None):
    return json.dumps({"type": "assistant", "message": {
        "id": mid, "model": model, "content": content or [{"type": "text", "text": "x"}],
        "usage": {"input_tokens": inp, "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr, "output_tokens": out}}})


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name) / "base dir"
        self.base.mkdir()
        (self.base / "HANDOFF.md").write_text("x", encoding="utf-8")

    def lint(self, text, **kw):
        return wf.lint(write(self.tmp.name, "s.js", text), **kw)

    def test_bad_script_gets_each_error_code(self):
        items = self.lint(BAD)
        errs = codes(items, "ERROR")
        for code in ("stringify", "forbidden", "model-effort", "goi", "approval"):
            self.assertIn(code, errs, code)
        self.assertIn("pool", codes(items, "WARN"))
        forbidden = [x["msg"] for x in items if x["code"] == "forbidden"]
        self.assertTrue(any("sleep" in m for m in forbidden))
        self.assertTrue(any("timeout" in m for m in forbidden))
        me = [x for x in items if x["code"] == "model-effort"]
        self.assertTrue(any("effort" in x["msg"] for x in me))
        self.assertTrue(any("'gpt'" in x["msg"] for x in me))
        self.assertTrue(any("'ultra'" in x["msg"] for x in me))

    def test_stringify_line_number(self):
        items = self.lint(BAD)
        line = [x["line"] for x in items if x["code"] == "stringify"][0]
        self.assertEqual(BAD.split("\n")[line - 1].count("JSON.stringify"), 1)

    def test_negated_lines_not_flagged(self):
        items = self.lint(CLEAN, base=str(self.base))
        self.assertNotIn("forbidden", codes(items))

    def test_clean_script_passes(self):
        items = self.lint(CLEAN, base=str(self.base))
        self.assertEqual(codes(items, "ERROR") - ({"syntax"} if not HAS_NODE else set()), set(), items)
        rc, out = cli("lint-script", write(self.tmp.name, "c.js", CLEAN), "--base", str(self.base))
        self.assertEqual(rc, 0, out)

    def test_cli_exit_1_on_error(self):
        p = write(self.tmp.name, "b.js", BAD)
        proc = subprocess.run([sys.executable, str(SCRIPT), "lint-script", p], capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 1)
        self.assertRegex(proc.stdout, r"ERROR stringify dòng \d+:")

    def test_json_output(self):
        rc, out = cli("lint-script", write(self.tmp.name, "b.js", BAD), "--json")
        self.assertEqual(rc, 1)
        self.assertIn("approval", {x["code"] for x in json.loads(out)})

    def test_missing_path_is_error_and_placeholder_is_warn(self):
        text = CLEAN.replace("Đọc ${B}/HANDOFF.md trước.", "Đọc ${B}/KHONG-CO.md và /Users/zzz-khong-co/<site>/x trước.")
        items = self.lint(text, base=str(self.base))
        paths = [x for x in items if x["code"] == "paths"]
        self.assertTrue(any(x["level"] == "ERROR" and "KHONG-CO.md" in x["msg"] for x in paths), paths)
        self.assertTrue(any(x["level"] == "WARN" and "chưa điền" in x["msg"] for x in paths), paths)

    def test_runtime_lock_under_existing_dir_ok(self):
        # Khoá _server-maint chỉ có lúc chạy; thư mục cha có thì không báo lỗi.
        text = CLEAN.replace("Đọc ${B}/HANDOFF.md trước.", "Khoá ${B}/_server-maint.lockdir và ${B}/khong-co/x.lock.")
        paths = [x for x in self.lint(text, base=str(self.base)) if x["code"] == "paths"]
        self.assertFalse(any("_server-maint" in x["msg"] for x in paths), paths)
        self.assertTrue(any(x["level"] == "ERROR" and "khong-co/x.lock" in x["msg"] for x in paths), paths)

    def test_goi_arrow_form_ok_and_agent_inside_goi_skipped(self):
        text = CLEAN.replace("async function goi(prompt, opts) {", "const goi = async (prompt, opts) => {").replace(
            "return await agent(prompt, opts)\n}", "return await agent(prompt)\n}")
        items = self.lint(text, base=str(self.base))
        self.assertNotIn("goi", codes(items))
        self.assertNotIn("model-effort", codes(items))

    def test_spread_options_skipped(self):
        text = CLEAN.replace("{ label: 'lam:' + L.key, model: L.model, effort: L.effort }", "{ label: 'lam', ...L.opts }")
        self.assertNotIn("model-effort", codes(self.lint(text, base=str(self.base))))

    def test_readonly_exempts_approval(self):
        text = CLEAN.replace("NGUỒN PHÊ DUYỆT", "NGUỒN").replace("readOnly: false", "readOnly: true")
        self.assertNotIn("approval", codes(self.lint(text, base=str(self.base))))
        text = CLEAN.replace("NGUỒN PHÊ DUYỆT", "NGUỒN")
        self.assertIn("approval", codes(self.lint(text, base=str(self.base)), "ERROR"))

    def test_commented_code_ignored(self):
        text = CLEAN + "\n// const x = await agent(`sleep 30 ${JSON.stringify(a)}`, { label: 'x' })\n"
        items = self.lint(text, base=str(self.base))
        self.assertTrue(codes(items, "ERROR") <= {"syntax"})

    def test_size(self):
        big = CLEAN.replace("Kiểm.`", "Kiểm." + "x" * 9000 + "`")
        self.assertIn("size", codes(self.lint(big, base=str(self.base)), "WARN"))
        huge = CLEAN.replace("Kiểm.`", "Kiểm." + "x" * 13000 + "`")
        self.assertIn("size", codes(self.lint(huge, base=str(self.base)), "ERROR"))

    def test_max_agents_warn(self):
        self.assertIn("pool", codes(self.lint(CLEAN.replace("MAX_AGENTS = 6", "MAX_AGENTS = 9"), base=str(self.base)), "WARN"))

    def test_args_file(self):
        args_ok = write(self.tmp.name, "a.json", json.dumps({"base": str(self.base)}))
        self.assertEqual(codes(self.lint(CLEAN, args_file=args_ok), "ERROR") - {"syntax"}, set())
        for bad in ('{"now": "x"}', '{"base": "<thư mục>"}', '{"base": "x", "lanes": []}', "{hỏng"):
            p = write(self.tmp.name, "a2.json", bad)
            self.assertIn("args", codes(self.lint(CLEAN, args_file=p), "ERROR"), bad)
        self.assertIn("args", codes(self.lint(CLEAN, base=str(self.base)), "WARN"))

    @unittest.skipUnless(HAS_NODE, "không có node")
    def test_syntax_error_reported(self):
        items = self.lint(CLEAN.replace("return out", "return out ((("), base=str(self.base))
        self.assertIn("syntax", codes(items, "ERROR"))


class DataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.projects = root / "projects"
        self.session = self.projects / "proj" / "sid1"
        self.run = self.session / "subagents" / "workflows" / "wf_x"
        self.run.mkdir(parents=True)
        (self.session / "workflows").mkdir()
        (self.session / "workflows" / "wf_x.json").write_text(json.dumps({"runId": "wf_x", "totalTokens": 12345}), encoding="utf-8")
        j = [{"type": "launched"}]
        for key, aid, label, res in (("k1", "a1", "lam:one", {"status": "done", "n": 1}), ("k2", "a2", "lam:two", None), ("k3", "a3", "kiem:three", None)):
            j.append({"type": "started", "key": key, "agentId": aid, "label": label, "phase": "Làm"})
            if res:
                j.append({"type": "result", "key": key, "agentId": aid, "result": res})
        (self.run / "journal.jsonl").write_text("\n".join(json.dumps(x) for x in j) + "\n", encoding="utf-8")
        # a1: hai dòng cùng message.id m1 (dòng cuối thắng) + lượt m2
        a1 = [assistant("m1", "claude-opus-5-5", 1, 10, 100, 5), assistant("m1", "claude-opus-5-5", 2, 20, 200, 50),
              assistant("m2", "claude-opus-5-5", 3, 30, 300, 7)]
        (self.run / "agent-a1.jsonl").write_text("\n".join(a1) + "\n", encoding="utf-8")
        (self.run / "agent-a1.meta.json").write_text(json.dumps({"description": "lam:one", "model": "opus"}), encoding="utf-8")
        # a2: treo, đang chờ tool_result, secret trong input
        tool = [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "curl -H 'token=abc123secret' http://x && echo " + "z" * 300}}]
        a2 = [assistant("n1", "claude-sonnet-5-5", 4, 40, 400, 9, content=tool)]
        (self.run / "agent-a2.jsonl").write_text("\n".join(a2) + "\n", encoding="utf-8")
        (self.run / "agent-a2.meta.json").write_text(json.dumps({"description": "lam:two"}), encoding="utf-8")
        # a3: started, file mới
        a3 = [assistant("p1", "claude-sonnet-5-5", 1, 1, 1, 1)]
        (self.run / "agent-a3.jsonl").write_text("\n".join(a3) + "\n", encoding="utf-8")
        old = time.time() - 3 * 3600
        os.utime(self.run / "agent-a2.jsonl", (old, old))

    def test_tokens_dedupe_by_message_id(self):
        rc, out = cli("tokens", str(self.session), "--json")
        self.assertEqual(rc, 0)
        row = json.loads(out)["wf_x"]
        # a1: m1 chỉ tính dòng cuối (2/20/200/50) + m2 (3/30/300/7); a2: 4/40/400/9; a3: 1/1/1/1
        self.assertEqual(row["agents"], 3)
        self.assertEqual(row["turns"], 4)
        self.assertEqual(row["input"], 2 + 3 + 4 + 1)
        self.assertEqual(row["cache_creation"], 20 + 30 + 40 + 1)
        self.assertEqual(row["cache_read"], 200 + 300 + 400 + 1)
        self.assertEqual(row["output"], 50 + 7 + 9 + 1)
        # ngữ cảnh lượt cuối: a1 m2 = 333, a2 = 444, a3 = 3
        self.assertEqual(row["approx_total"], 333 + 444 + 3)
        self.assertEqual(row["wf_total"], 12345)

    def test_tokens_by_model_and_label_and_run_id(self):
        rc, out = cli("tokens", str(self.run), "--by", "model", "--json")
        rows = json.loads(out)
        self.assertEqual(rows["claude-opus-5-5"]["agents"], 1)
        self.assertEqual(rows["claude-sonnet-5-5"]["agents"], 2)
        rc, out = cli("tokens", str(self.run), "--by", "label", "--json")
        self.assertEqual(set(json.loads(out)), {"lam:one", "lam:two", "a3"})
        rc, out = cli("tokens", "wf_x", "--projects-root", str(self.projects))
        self.assertEqual(rc, 0)
        self.assertIn("wf_x", out)
        self.assertIn("12.345", out)

    def test_result_exact_and_missing(self):
        rc, out = cli("result", "lam:one", str(self.session))
        self.assertEqual(rc, 0)
        self.assertIn('"status":"done"', out)
        self.assertIn("wf_x", out)
        rc, out = cli("result", "one", str(self.session))
        self.assertEqual(rc, 0, "khớp chứa")
        rc, out = cli("result", "nope", str(self.session))
        self.assertEqual(rc, 3)
        self.assertIn("chưa có result", out)
        rc, out = cli("result", "lam:two", str(self.session))
        self.assertEqual(rc, 3, "có started nhưng chưa có result")

    def test_result_truncate(self):
        rc, out = cli("result", "lam:one", str(self.session), "--max", "5")
        self.assertIn("cắt", out)

    def test_slots_counts_only_fresh(self):
        rc, out = cli("slots", str(self.session))
        self.assertEqual(rc, 0)
        self.assertIn("slot đang dùng: 1", out)
        self.assertIn("kiem:three", out)
        self.assertNotIn("lam:two", out)
        rc, out = cli("slots", str(self.session), "--cap", "1")
        self.assertEqual(rc, 2)

    def test_stale_lists_old_only_and_redacts(self):
        rc, out = cli("stale", str(self.session), "--minutes", "15")
        self.assertEqual(rc, 0)
        self.assertIn("lam:two", out)
        self.assertNotIn("kiem:three", out)
        self.assertNotIn("abc123secret", out)
        self.assertIn("<che>", out)
        self.assertIn("Bash:", out)
        self.assertIn("chờ tool_result: có", out)
        self.assertIn("phút", out)
        tool_part = out.split("Bash: ")[1].split(" | ")[0]
        self.assertLessEqual(len(tool_part), 160)

    def test_redact(self):
        self.assertEqual(wf.redact("a password=hunter2 b"), "a <che> b")
        self.assertEqual(wf.redact('"api_key": "xyz"'), '"api_<che>')


if __name__ == "__main__":
    unittest.main()
