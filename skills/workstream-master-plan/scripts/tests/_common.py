"""Fixture dùng chung cho test của workstream-master-plan. Dữ liệu giả, không có số của site thật."""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import plan as P  # noqa: E402

FIXED_NOW = datetime(2026, 10, 25, 9, 30)

BASE = {
    "title": "Master plan site mẫu",
    "updated": "24/10/2026 18:00",
    "rules": ["Mọi yêu cầu vào plan trước khi làm."],
    "phases": [
        {"id": "P1", "name": "Đợt 1", "when": "24/10", "why": "Việc đã duyệt."},
        {"id": "P2", "name": "Đợt 2", "when": "25/10", "why": "Việc sau đợt 1."},
    ],
    "items": [
        {"id": "M1", "phase": "P1", "status": "done", "title": "Sửa menu", "detail": ["chi tiết `a`"],
         "deps": [], "blocks": ["M2"], "source": "Tin 23/10 10:00", "evidence": "log/apply.log", "program": "Site A"},
        {"id": "M2", "phase": "P1", "status": "doing", "title": "Sửa footer", "detail": [],
         "deps": ["M1"], "blocks": [], "source": "Tin 23/10 10:05", "evidence": "", "program": "Site A"},
        {"id": "M3", "phase": "P2", "status": "todo", "title": "Đổi ảnh", "detail": [],
         "deps": [], "blocks": [], "source": "Tin 24/10 09:00", "evidence": "", "program": "Site B"},
    ],
    "done": [{"when": "23/10", "what": "Dọn cache.", "evidence": "`cache.log`"}],
    "requests": [
        {"date": "23/10/2026 10:00", "ask": "Sửa menu trang chủ", "items": "M1"},
        {"date": "23/10/2026 10:05", "ask": "Sửa footer luôn", "items": "M2"},
        {"date": "24/10 09:00", "ask": "Đổi ảnh đại diện", "items": "M3"},
    ],
}


def make_plan(mutate=None):
    p = copy.deepcopy(BASE)
    if mutate:
        mutate(p)
    return p


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.orig_now = P.now
        P.now = lambda: FIXED_NOW

    def tearDown(self):
        P.now = self.orig_now
        self.tmp.cleanup()

    def write_plan(self, mutate=None, name="plan.json"):
        f = self.dir / name
        f.write_text(json.dumps(make_plan(mutate), ensure_ascii=False, indent=1), encoding="utf-8")
        return f

    def read_plan(self, f):
        return json.loads(Path(f).read_text(encoding="utf-8"))

    def run_main(self, fn, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = fn(argv)
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()
