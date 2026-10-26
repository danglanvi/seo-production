"""Test offline cho rules_jev.py: không mạng, không model. Chạy: python3 -B -E tests/test_rules_jev.py
Phần tách đoạn cần beautifulsoup4; máy thiếu bs4 thì test đó bỏ qua."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "rules_jev.py"
spec = importlib.util.spec_from_file_location("rules_jev", SCRIPT)
rj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rj)
try:
    import bs4  # noqa: F401
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

HTML = """<html><body><div class="entry-content">
<p>Đoạn mở bài giới thiệu chủ đề chính của bài viết này cho người đọc mới.</p>
<h2>2. Cấp bậc của SubHeading</h2>
<p>Trong HTML, SubHeading được chia thành nhiều cấp độ, thường được đánh dấu từ H2 đến H6:</p>
<ul><li>H1: tiêu đề chính</li><li>H2: đề mục lớn</li></ul>
<p>Đoạn thứ hai của mục này nói thêm về cách dùng các cấp heading trong bài.</p>
<h3>39. Remove/ Disavow những backlink xấu</h3>
<p>“Trộm cắp” các backlink đối thủ là một cụm từ được sử dụng khá nhiều trong nghề.</p>
<p>Ngắn quá.</p>
</div></body></html>"""


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


class RulesJev(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.version = json.loads(rj.TASK.read_text(encoding="utf-8"))["version"]

    @unittest.skipUnless(HAS_BS4, "thiếu beautifulsoup4")
    def test_paragraphs(self):
        (self.t / "h").mkdir()
        (self.t / "h" / "a.html").write_text(HTML, encoding="utf-8")
        (self.t / "h" / "a.url").write_text("https://x.test/a/", encoding="utf-8")
        rj.main(["paragraphs", "--html-dir", str(self.t / "h"), "--out", str(self.t / "p.jsonl")])
        rows = jl(self.t / "p.jsonl")
        self.assertEqual(len(rows), 4)                          # đoạn dưới 8 chữ bị bỏ
        self.assertFalse(rows[0]["first_after_heading"])        # đoạn mở bài không có heading
        self.assertTrue(rows[1]["first_after_heading"] and rows[1]["has_list"])
        self.assertIn("H2: đề mục lớn", rows[1]["text"])         # ca thật: đoạn kết thúc bằng ":" gộp danh sách
        self.assertFalse(rows[2]["first_after_heading"])
        self.assertEqual(rows[3]["heading"], "39. Remove/ Disavow những backlink xấu")

    def test_code_flags(self):
        flags = rj.code_flags({"heading": "39. Remove/ Disavow những backlink xấu", "words": 130, "has_list": False,
                               "text": "“Trộm cắp” các backlink đối thủ là một cụm từ."})
        self.assertEqual([f.split()[0] for f in flags], ["R24", "R26", "R32"])
        self.assertEqual(rj.code_flags({"heading": "Tỷ lệ 1/2", "words": 20, "has_list": False,
                                        "text": "Theo Google, nội dung hữu ích được ưu tiên."}), ["R21 dẫn nguồn trước claim"])

    def test_decide_modes(self):
        self.assertEqual(rj.decide(0.9, {}), "chưa hiệu chuẩn")
        self.assertEqual(rj.decide(0.5, {"triage": 0.42}), "Claude đọc")
        self.assertEqual(rj.decide(0.1, {"triage": 0.42}), "Jev xếp thấp")
        self.assertEqual(rj.decide(0.1, {"no": 0.6}), "đạt")
        self.assertEqual(rj.decide(0.97, {"yes": 0.95}), "vi phạm")

    def test_prepare_and_report(self):
        paras = [{"id": "u#p0", "url": "u", "heading": "X là gì?", "first_after_heading": True, "text": "X là ...",
                  "words": 3, "has_list": False},
                 {"id": "u#p1", "url": "u", "heading": "X là gì?", "first_after_heading": False, "text": "Thêm ý.",
                  "words": 2, "has_list": False}]
        (self.t / "p.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in paras), encoding="utf-8")
        rj.main(["prepare", "--paras", str(self.t / "p.jsonl"), "--out", str(self.t / "in.jsonl")])
        self.assertEqual(set(jl(self.t / "in.jsonl")[0]["state"]), {"heading", "text"})
        out = [{"id": p["id"], "answers": {q: {"p_yes": 0.6} for q in rj.QUESTIONS}} for p in paras]
        (self.t / "o.jsonl").write_text("".join(json.dumps(o) + "\n" for o in out), encoding="utf-8")
        reg = self.t / "reg.json"
        reg.write_text(json.dumps({"entries": [{"rubric": "writing-rules", "version": self.version, "mode": "jev",
                                                "question": "answer_first", "site": "x.test", "threshold": None,
                                                "reject_below": 0.42}]}), encoding="utf-8")
        rj.main(["report", "--paras", str(self.t / "p.jsonl"), "--jev-out", str(self.t / "o.jsonl"),
                 "--registry", str(reg), "--site", "x.test", "--out-dir", str(self.t / "w")])
        rows = {r["id"]: r for r in jl(self.t / "w" / "paragraphs.jsonl")}
        self.assertEqual(rows["u#p0"]["answer_first"], "Claude đọc")
        self.assertNotIn("answer_first", rows["u#p1"])          # chỉ chấm đoạn đầu sau heading
        self.assertEqual(rows["u#p1"]["fluff"], "chưa hiệu chuẩn")


if __name__ == "__main__":
    unittest.main()
