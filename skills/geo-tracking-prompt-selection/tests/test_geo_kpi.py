"""Test offline cho scripts/geo_kpi.py. Chạy từ root repo: python3 -B -m unittest discover -s skills/geo-tracking-prompt-selection/tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "geo_kpi.py"
PROMPTS = "id\tfunnel\tbranded\ttopic\tprompt\n" + "".join(
    f"P{i:02d}\t{'BOFU' if i <= 4 else 'MOFU'}\tno\tt\tcâu hỏi {i}\n" for i in range(1, 9)) + "P09\tBOFU\tyes\tt\tBrandA có tốt không\n"
BRANDS = {"own": "BrandA", "own_domains": ["a.vn"], "brands": {"BrandA": {"regex": "branda"}, "BrandB": {"regex": "brandb"}}}


def build(d, mention, model="m1", runs=3, prompts=PROMPTS, date="2026-10-18 10:00"):
    """mention(pid, engine, run) -> (nhắc A?, trích a.vn?)."""
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    (d / "prompts.tsv").write_text(prompts, encoding="utf-8")
    (d / "brands.json").write_text(json.dumps(BRANDS), encoding="utf-8")
    raw, det, cit = [], [], []
    ids = [l.split("\t")[0] for l in prompts.splitlines()[1:]]
    for pid in ids:
        for e in ("chatgpt", "gemini"):
            for k in range(1, runs + 1):
                m, c = mention(pid, e, k)
                url = "https://vertexaisearch.cloud.google.com/x" if e == "gemini" else "https://a.vn/dich-vu/?utm=1"
                raw.append({"prompt_id": pid, "engine": e, "run": k, "ok": True, "answer": "x", "model": model,
                            "model_served": model, "date": date, "cost": 0.01})
                det += [{"prompt_id": pid, "engine": e, "run": k, "brand": "BrandA", "regex_mention": m},
                        {"prompt_id": pid, "engine": e, "run": k, "brand": "BrandB", "regex_mention": True}]
                doms = [{"domain": "a.vn", "url": url}, {"domain": "a.vn", "url": url}] if c else [{"domain": "b.vn", "url": "https://b.vn/"}]
                cit.append({"prompt_id": pid, "engine": e, "run": k, "domains": doms, "own_cited": c})
    raw.append({"prompt_id": "P01", "engine": "chatgpt", "run": 9, "ok": False, "error": "http_429"})
    for name, rows in (("raw.jsonl", raw), ("det.jsonl", det), ("citations.jsonl", cit)):
        (d / name).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    subprocess.run([sys.executable, "-B", str(SCRIPT), "kpi", "--raw", str(d / "raw.jsonl"), "--det", str(d / "det.jsonl"),
                    "--citations", str(d / "citations.jsonl"), "--prompts", str(d / "prompts.tsv"),
                    "--brands", str(d / "brands.json"), "--out-dir", str(d / "kpi")], check=True, capture_output=True)
    return json.loads((d / "kpi" / "kpi.json").read_text(encoding="utf-8")), d / "kpi" / "kpi.json"


def compare(base, new, *extra):
    r = subprocess.run([sys.executable, "-B", str(SCRIPT), "compare", "--base", str(base), "--new", str(new),
                        "--out", str(Path(new).parent / "c.md"), *extra], check=True, capture_output=True, text=True)
    return r.stdout


class Kpi(unittest.TestCase):
    def test_rates(self):
        with tempfile.TemporaryDirectory() as t:
            # P01–P04 (BOFU) nhắc + trích, P05–P08 không; P09 mang tên brand không vào mẫu số
            k, _ = build(t, lambda p, e, r: (p in ("P01", "P02", "P03", "P04", "P09"), p in ("P01", "P02", "P09")))
            c = k["engines"]["chatgpt"]
            self.assertEqual(c["mention_nonbranded"], 0.5)
            self.assertEqual(c["mention_bofu_nonbranded"], 1.0)
            self.assertEqual(c["cited_nonbranded"], 0.25)
            self.assertEqual(c["sov_nonbranded"], round(12 / 36, 3))  # A 12 lượt, B 24 lượt
            self.assertEqual(c["failed"], 1)
            self.assertEqual(c["runs"], 3)
            self.assertEqual(c["run_spread"], 0)

    def test_url_once_per_answer_and_gemini_domain_only(self):
        with tempfile.TemporaryDirectory() as t:
            k, _ = build(t, lambda p, e, r: (True, True))
            self.assertEqual(k["engines"]["chatgpt"]["own_urls"], [["https://a.vn/dich-vu/", 27]])
            self.assertEqual(k["engines"]["gemini"]["own_urls"], [])
            self.assertIn("vertexaisearch", k["engines"]["gemini"]["own_urls_note"])


class Compare(unittest.TestCase):
    def test_same_data_in_noise(self):
        with tempfile.TemporaryDirectory() as t:
            f = lambda p, e, r: (p in ("P01", "P02") or (p == "P03" and r == 1), p == "P01")
            _, a = build(Path(t) / "a", f)
            _, b = build(Path(t) / "b", f)
            out = compare(a, b)
            self.assertNotIn("| tăng |", out)
            self.assertNotIn("| giảm |", out)
            self.assertIn("trong nhiễu", out)

    def test_real_change_detected(self):
        with tempfile.TemporaryDirectory() as t:
            _, a = build(Path(t) / "a", lambda p, e, r: (p == "P01", False))
            _, b = build(Path(t) / "b", lambda p, e, r: (p != "P08", False))
            out = compare(a, b)
            self.assertRegex(out, r"\| chatgpt \| Nhắc brand \| 12% \| 88% \| \+75% \| .* \| tăng \|")

    def test_flags_model_runs_prompt_text_and_day(self):
        with tempfile.TemporaryDirectory() as t:
            f = lambda p, e, r: (True, False)
            _, a = build(Path(t) / "a", f)
            changed = PROMPTS.replace("câu hỏi 2\n", "câu hỏi 2 đã sửa\n") + "P10\tBOFU\tno\tt\tcâu mới\n"
            _, b = build(Path(t) / "b", f, model="m2", runs=2, prompts=changed, date="2026-11-03 09:00")
            out = compare(a, b, "--change-date", "2026-10-20")
            self.assertIn("model đổi", out)
            self.assertIn("chỉ có 2 lượt chạy", out)
            self.assertIn("Prompt đổi chữ (bỏ khỏi so): P02", out)
            self.assertIn("Prompt mới (cohort riêng, không so): 1", out)
            self.assertIn("ngày +14", out)
            self.assertIn("mốc gần nhất: ngày 14)", out)


class TestAhrefs(unittest.TestCase):
    def test_split_prompt_vs_aio_keywords(self):
        P = ("all_platforms", "chatgpt", "google_ai_overviews", "google_ai_mode", "gemini", "perplexity", "copilot")
        cnt = lambda vals, **x: {**{k: {"citations": v, "pages": 1} for k, v in zip(P, vals)}, **{k: {"citations": v, "pages": 1} for k, v in x.items()}}
        snaps = [{"domain": "a.vn", "date": "2026-10-19", "ai_responses_count": cnt((100, 2, 10, 5, 3, 10, 0), google_ai_overviews_keywords=70)},
                 {"domain": "a.vn", "date": "2026-07-19", "ai_responses_count": cnt((90, 2, 5, 5, 0, 8, 0))},
                 {"domain": "b.vn", "date": "2026-10-19", "ai_responses_count": cnt((500, 10, 40, 20, 10, 20, 0))},
                 {"domain": "c.vn", "date": "2026-10-19", "country": "vn", "ai_responses_count": {"all_platforms": {"citations": 9, "pages": 1}}}]
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "s.json").write_text(json.dumps(snaps), encoding="utf-8")
            r = subprocess.run([sys.executable, "-B", str(SCRIPT), "ahrefs", "--snapshots", str(Path(d) / "s.json"), "--own", "a.vn",
                                "--out", str(Path(d) / "o.md")], capture_output=True, text=True, check=True).stdout
        self.assertIn("| **a.vn** | 2026-10-19 | 30 | 23% | 2 | 18 | 10 | 0 | 70 |", r)  # 30 từ prompt, không lấy 100
        self.assertIn("| b.vn | 2026-10-19 | 100 | ", r)
        self.assertIn("| ≈400 |", r)  # suy ra từ all_platforms − tổng prompt
        self.assertIn("| Từ prompt | 20 | 30 |", r)
        self.assertIn("gemini: từ 0 lên 3", r)
        self.assertIn("c.vn 2026-10-19: thiếu nền tảng", r)
        self.assertIn("Trộn phạm vi quốc gia", r)


if __name__ == "__main__":
    unittest.main()
