import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "wf_watchdog.py"
RUN = "wf_test-001"


def iso(minutes_ago):
    t = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (t.microsecond // 1000)


def use(i, name, inp, ago):
    return {"type": "assistant", "timestamp": iso(ago),
            "message": {"content": [{"type": "tool_use", "id": i, "name": name, "input": inp}]}}


def res(i, ago):
    return {"type": "user", "timestamp": iso(ago),
            "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": "ok"}]}}


class WatchdogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.session = Path(self.tmp.name) / "sid"
        self.run_dir = self.session / "subagents" / "workflows" / RUN
        self.run_dir.mkdir(parents=True)
        self.journal = []

    def tearDown(self):
        self.tmp.cleanup()

    def agent(self, aid, label, lines, finished=False):
        self.journal.append({"type": "started", "key": "k" + aid, "agentId": aid, "label": label, "phase": "Làm"})
        if finished:
            self.journal.append({"type": "result", "key": "k" + aid, "agentId": aid, "result": {}})
        (self.run_dir / ("agent-%s.jsonl" % aid)).write_text("\n".join(json.dumps(l) for l in lines) + "\n")

    def run_cli(self, *extra, target=None):
        (self.run_dir / "journal.jsonl").write_text("\n".join(json.dumps(j) for j in self.journal) + "\n")
        p = subprocess.run([sys.executable, str(SCRIPT), str(target or self.run_dir), "--once", *extra],
                           capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_monitor_cho_155_phut(self):
        cmd = "until [ $(wc -l /tmp/x.log) -ge 5 ]; do sleep 5; done"
        self.agent("a1", "lam:toi-font", [use("t1", "Monitor", {"command": cmd}, 155)])
        code, out = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("TREO", out)
        self.assertIn("tool=Monitor", out)
        self.assertIn("[hop-duyet?]", out)
        self.assertIn("label=lam:toi-font", out)
        self.assertIn("run=" + RUN, out)
        self.assertIn("chờ=155p", out)

    def test_tool_co_result_khong_bao(self):
        self.agent("a1", "x", [use("t1", "Bash", {"command": "ls"}, 100), res("t1", 99), use("t2", "Bash", {"command": "ls"}, 1)])
        code, out = self.run_cli()
        self.assertEqual((code, out), (0, ""))

    def test_agent_da_co_result_bo_qua(self):
        self.agent("a1", "x", [use("t1", "Monitor", {"command": "$(wc -l f)"}, 200)], finished=True)
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertNotIn("TREO", out)

    def test_che_secret(self):
        self.agent("a1", "x", [use("t1", "Bash", {"command": "curl -H x password=abc123 http://h"}, 50)])
        code, out = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("<che>", out)
        self.assertNotIn("abc123", out)
        self.assertNotIn("[hop-duyet?]", out)

    def test_im(self):
        self.agent("a1", "x", [use("t1", "Bash", {"command": "ls"}, 60), res("t1", 59)])
        old = datetime.now().timestamp() - 3600
        os.utime(self.run_dir / "agent-a1.jsonl", (old, old))  # file không ghi 60 phút
        code, out = self.run_cli("--idle-minutes", "20")
        self.assertEqual(code, 1)
        self.assertIn(" IM ", out)

    def test_tool_moi_cho_chua_du_phut(self):
        self.agent("a1", "x", [use("t1", "Bash", {"command": "ls"}, 3)])
        code, _ = self.run_cli()
        self.assertEqual(code, 0)

    def test_run_xong_theo_wf_json(self):
        self.agent("a1", "x", [use("t1", "Monitor", {"command": "$(x)"}, 300)])
        wf = self.session / "workflows"
        wf.mkdir()
        (wf / (RUN + ".json")).write_text(json.dumps({"runId": RUN, "status": "completed"}))
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("XONG run=" + RUN, out)

    def test_session_dir_va_out(self):
        self.agent("a1", "x", [use("t1", "Bash", {"command": "echo `date`"}, 40)])
        outf = Path(self.tmp.name) / "bao.txt"
        code, out = self.run_cli("--out", str(outf), target=self.session)
        self.assertEqual(code, 1)
        self.assertIn("[hop-duyet?]", out)
        self.assertIn("TREO", outf.read_text())

    def test_lap_khong_bao_xong_gia_cho_run_cu(self):
        # Ca hỏng thật (kiểm độc lập 25/10): chạy ngay sau launch, session chỉ có run cũ đã xong
        # thì bản đầu in "XONG run=<run cũ>" và thoát 0.
        self.agent("a1", "x", [use("t1", "Bash", {"command": "ls"}, 30), res("t1", 29)], finished=True)
        (self.run_dir / "journal.jsonl").write_text("\n".join(json.dumps(j) for j in self.journal) + "\n")
        wf = self.session / "workflows"
        wf.mkdir()
        (wf / (RUN + ".json")).write_text(json.dumps({"runId": RUN, "status": "completed"}))
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.session), "--interval", "0.05", "--wait-new", "0.005"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("XONG", p.stdout)
        self.assertIn("KHONG-CO-RUN", p.stdout)

    def test_nhan_thu_muc_workflows(self):
        # Ca hỏng thật 29/10/2026 04:33: phiên chính truyền <session>/subagents/workflows, watchdog
        # chờ 30 phút rồi báo KHONG-CO-RUN trong khi agent w7 đang treo ở tabs_create_mcp.
        self.agent("a1", "lam:w7-compare-bar", [use("t1", "mcp__claude-in-chrome__tabs_create_mcp", {}, 26)])
        code, out = self.run_cli(target=self.session / "subagents" / "workflows")
        self.assertEqual(code, 1)
        self.assertIn("TREO", out)
        self.assertIn("tool=mcp__claude-in-chrome__tabs_create_mcp", out)
        (self.session / "workflows").mkdir()
        code, out = self.run_cli(target=self.session / "workflows")
        self.assertEqual(code, 1)
        self.assertIn("TREO", out)

    def test_thu_muc_la_bao_loi_ngay(self):
        # Chế độ lặp với thư mục không phải session: thoát 2 ngay, không chờ --wait-new 30 phút.
        la = Path(self.tmp.name) / "khong-phai-session"
        la.mkdir()
        p = subprocess.run([sys.executable, str(SCRIPT), str(la), "--wait-new", "30"],
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Không phải thư mục run hay session", p.stderr)

    def test_session_moi_chua_co_agent_van_cho(self):
        # Session mới: chưa có subagents/, nhưng có transcript <id>.jsonl cạnh thư mục. Không báo lỗi, chờ run mới.
        moi = Path(self.tmp.name) / "sid-moi"
        moi.mkdir()
        (Path(self.tmp.name) / "sid-moi.jsonl").write_text("{}\n")
        p = subprocess.run([sys.executable, str(SCRIPT), str(moi), "--interval", "0.05", "--wait-new", "0.005"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)
        self.assertIn("KHONG-CO-RUN", p.stdout)

    def test_dau_vao_sai(self):
        p = subprocess.run([sys.executable, str(SCRIPT), self.tmp.name, "--once"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
