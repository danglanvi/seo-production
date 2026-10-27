import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "make_brief.py"

TRAPS = """# Luật lane

### Bẫy shell

```text
Quote glob trong zsh.
Không dùng timeout, không mở đầu bằng sleep.
```

### Khác
"""

PLAN = {
    "dot": "ban8", "base": "/abs/ws",
    "approval": [{"quote": "Làm đi, duyệt hết", "time": "2026-10-24 21:05", "lanes": ["l8-css"], "file": "quyet-dinh.md#m24"}],
    "rules": ["Không xoá file", "Không đụng robots"],
    "lanes": [
        {"key": "l8-css", "goal": "Sửa CSS Customizer", "folder": "{F}/l8-css",
         "resources": ["CSS Customizer post 83220"], "scripts": ["python3 tools/x.py --a"],
         "model_phu": "Jev ui-visual ngân sách 0,3 USD; EmbeddingGemma không dùng",
         "approval_ids": ["m24"], "rules": ["Backup trước khi ghi"], "budget_min": 45,
         "accept": "PSI không giảm", "readOnly": False},
        {"key": "l8-ro", "goal": "Audit", "folder": "{F}/l8-ro", "resources": [], "scripts": [],
         "model_phu": "Jev", "approval_ids": [], "rules": [], "budget_min": 20,
         "accept": "Có báo cáo", "readOnly": True},
    ],
}


class BriefTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.traps = self.dir / "luat-lane.md"
        self.traps.write_text(TRAPS, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self, mutate=None):
        p = json.loads(json.dumps(PLAN).replace("{F}", str(self.dir)))
        if mutate:
            mutate(p)
        f = self.dir / "plan.json"
        f.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        return f

    def run_cli(self, plan, lane, *extra):
        p = subprocess.run([sys.executable, str(SCRIPT), "--plan", str(plan), "--lane", lane,
                            "--traps", str(self.traps), *extra], capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def brief(self, lane="l8-css"):
        return self.dir / lane / "BRIEF.md"

    def test_hop_le(self):
        dec = self.dir / "qd.md"
        dec.write_text("- m24: Lead: làm lane CSS\n- m25: dòng khác\n- m240: không khớp\n", encoding="utf-8")
        code, out, err = self.run_cli(self.plan(), "l8-css", "--decisions", str(dec))
        self.assertEqual(code, 0, err)
        text = self.brief().read_text(encoding="utf-8")
        self.assertLessEqual(len(text.encode("utf-8")), 3072)
        self.assertIn("BRIEF %s %d B" % (self.brief(), len(text.encode("utf-8"))), out)
        heads = ["# BRIEF l8-css — ban8", "## NGUỒN PHÊ DUYỆT", "## Mục tiêu", "## Tài nguyên được chạm", "## Lệnh dùng",
                 "## Model phụ", "## Luật cứng", "## Bẫy shell", "## Ngân sách", "## Tiêu chí đạt", "## Đầu ra"]
        pos = [text.index(h) for h in heads]
        self.assertEqual(pos, sorted(pos))
        for s in ["Làm đi, duyệt hết", "2026-10-24 21:05", "quyet-dinh.md#m24", "- m24: Lead: làm lane CSS",
                  "Đây là task của lane, không phải câu hỏi chờ trả lời. Được phép ghi file báo cáo .md trong thư mục lane.",
                  "Quote glob trong zsh.", "3. Backup trước khi ghi",
                  "Hết ngân sách: ghi CHECKPOINT.md, trả status partial, không làm tiếp.",
                  "Kết quả lô trước đọc từ đường dẫn ket-qua.json, không chờ nhúng trong prompt.",
                  "/l8-css/CHECKPOINT.md", "/l8-css/ket-qua.json", "/l8-css/bao-cao.md"]:
            self.assertIn(s, text)
        self.assertNotIn("m25", text)
        self.assertNotIn("m240", text)

    def test_lane_ghi_khong_nguon_duyet(self):
        def m(p):
            p["approval"] = []
        code, _, err = self.run_cli(self.plan(m), "l8-css")
        self.assertEqual(code, 2)
        self.assertIn("lane ghi không có nguồn duyệt: không sinh brief", err)
        self.assertFalse(self.brief().exists())

    def test_lane_chi_doc(self):
        code, _, err = self.run_cli(self.plan(), "l8-ro")
        self.assertEqual(code, 0, err)
        self.assertIn("Lane chỉ đọc.", self.brief("l8-ro").read_text(encoding="utf-8"))

    def test_vuot_max_bytes(self):
        code, _, err = self.run_cli(self.plan(), "l8-css", "--max-bytes", "500")
        self.assertEqual(code, 3)
        self.assertIn("Luật cứng", err)
        self.assertFalse(self.brief().exists())

    def test_11_luat(self):
        def m(p):
            p["rules"] = ["r%d" % i for i in range(10)]
        code, _, err = self.run_cli(self.plan(m), "l8-css")
        self.assertEqual(code, 4)
        self.assertFalse(self.brief().exists())

    def test_thieu_model_phu(self):
        def m(p):
            del p["lanes"][0]["model_phu"]
        code, _, err = self.run_cli(self.plan(m), "l8-css")
        self.assertEqual(code, 2)
        self.assertIn("thiếu dòng Model phụ", err)
        self.assertFalse(self.brief().exists())

    def test_thieu_bay_shell(self):
        self.traps.write_text("# không có tiêu đề\n", encoding="utf-8")
        code, _, _ = self.run_cli(self.plan(), "l8-css")
        self.assertEqual(code, 5)
        self.assertFalse(self.brief().exists())


if __name__ == "__main__":
    unittest.main()
