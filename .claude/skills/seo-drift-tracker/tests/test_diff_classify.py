"""Test offline cho diff_classify.py: không mạng, không model. Chạy: python3 -B tests/test_diff_classify.py"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "diff_classify.py"
spec = importlib.util.spec_from_file_location("diff_classify", SCRIPT)
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def put(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


class CodeRule(unittest.TestCase):
    def test_nbsp_is_harmless(self):
        # Ca thật 19/10: title chỉ khác NBSP trước dấu "|".
        self.assertEqual(dc.code_rule("ACME & Agency\xa0 | Agency", "ACME & Agency | Agency")[0], "vô hại")

    def test_case_and_punct_is_harmless(self):
        self.assertEqual(dc.code_rule("Cách đăng ký, Xác minh", "cách đăng ký xác minh")[0], "vô hại")

    def test_number_change_is_significant(self):
        # Ca thật: meta đổi 500+ thành 550+.
        self.assertEqual(dc.code_rule("500+ dự án thành công", "550+ dự án thành công"), ("đáng kể", "số đổi"))
        self.assertEqual(dc.code_rule("Dữ liệu 1.200.000 lượt", "Dữ liệu 1200000 lượt")[0], "vô hại")

    def test_empty_is_significant(self):
        self.assertEqual(dc.code_rule("", "Marketing")[0], "đáng kể")

    def test_rename_goes_to_jev(self):
        # Ca thật: đổi tên entity không đổi số, code không chốt.
        self.assertEqual(dc.code_rule("Google Data Studio là gì?", "Looker Studio (Google Data Studio) là gì?"), (None, None))


class Commands(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_pipeline(self):
        put(self.tmp / "a.jsonl", [
            {"url": "https://x.test/a", "title": "A | X", "meta": "500+ dự án", "h1": ["Hướng dẫn A"]},
            {"url": "https://x.test/b", "title": "B", "meta": "m", "h1": "B"}])
        put(self.tmp / "b.jsonl", [
            {"url": "https://x.test/a", "title": "A  |  X", "meta": "550+ dự án", "h1": "Hướng dẫn chi tiết A"},
            {"url": "https://x.test/b", "title": "B", "meta": "m", "h1": "B"}])
        dc.main(["diffs", "--old", str(self.tmp / "a.jsonl"), "--new", str(self.tmp / "b.jsonl"),
                 "--out", str(self.tmp / "d.jsonl")])
        diffs = jl(self.tmp / "d.jsonl")
        self.assertEqual(sorted(d["element"] for d in diffs), ["h1", "meta", "title"])
        dc.main(["prepare", "--diffs", str(self.tmp / "d.jsonl"), "--out-dir", str(self.tmp / "w")])
        jev_in = jl(self.tmp / "w" / "jev_in.jsonl")
        self.assertEqual(len(jev_in), 1)
        self.assertEqual(set(jev_in[0]["state"]), {"url", "element", "old", "new"})
        h1 = jev_in[0]["id"]
        put(self.tmp / "out.jsonl", [{"id": h1, "answers": {"significant": {"p_yes": 0.9}}}])
        version = json.loads(dc.TASK.read_text(encoding="utf-8"))["version"]
        reg = self.tmp / "reg.json"
        reg.write_text(json.dumps({"entries": [
            {"rubric": "diff-impact", "version": version, "mode": "jev", "question": "significant",
             "positive": "yes", "site": "x.test", "threshold": 0.65, "conf_gate": 0.7}]}), encoding="utf-8")
        dc.main(["report", "--diffs", str(self.tmp / "d.jsonl"), "--jev-out", str(self.tmp / "out.jsonl"),
                 "--registry", str(reg), "--site", "x.test", "--out-dir", str(self.tmp / "w")])
        rows = {r["element"]: r for r in jl(self.tmp / "w" / "diff_impact.jsonl")}
        self.assertEqual(rows["title"]["decision"], "vô hại")
        self.assertEqual(rows["meta"]["decision"], "đáng kể")
        self.assertEqual(rows["h1"]["decision"], "đáng kể")
        # Cổng confidence gộp không được chốt "vô hại": p thấp vẫn để Claude đọc.
        put(self.tmp / "out.jsonl", [{"id": h1, "answers": {"significant": {"p_yes": 0.1}}}])
        dc.main(["report", "--diffs", str(self.tmp / "d.jsonl"), "--jev-out", str(self.tmp / "out.jsonl"),
                 "--registry", str(reg), "--site", "x.test", "--out-dir", str(self.tmp / "w")])
        rows = {r["element"]: r for r in jl(self.tmp / "w" / "diff_impact.jsonl")}
        self.assertEqual(rows["h1"]["decision"], "Claude đọc")

    def test_no_gate_means_claude_reads(self):
        self.assertEqual(dc.decide(0.99, {})[0], "Claude đọc")
        self.assertEqual(dc.decide(None, {"yes": 0.6})[0], "Claude đọc")

    def test_from_drift(self):
        (self.tmp / "c.json").write_text(json.dumps({"findings": [
            {"url": "https://x.test/a", "element": "description", "before": ["Cũ"], "after": ["Mới"], "severity": "MEDIUM"},
            {"url": "https://x.test/a", "element": "h1", "before": {"text": ["A"], "count": 1},
             "after": {"text": ["B"], "count": 1}, "severity": "HIGH"},
            {"url": "https://x.test/a", "element": "canonical", "before": ["/a"], "after": ["/b"], "severity": "CRITICAL"}]}),
            encoding="utf-8")
        dc.main(["from-drift", "--json", str(self.tmp / "c.json"), "--out", str(self.tmp / "d.jsonl")])
        rows = jl(self.tmp / "d.jsonl")
        self.assertEqual([(r["element"], r["old"], r["new"]) for r in rows], [("meta", "Cũ", "Mới"), ("h1", "A", "B")])


if __name__ == "__main__":
    unittest.main()
