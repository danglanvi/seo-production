#!/usr/bin/env python3
"""Test offline cho cluster.py: không cần mạng, không cần model.
Chạy: ~/.venvs/embeddinggemma/bin/python -I skills/serp-clustering/tests/test_cluster.py
(lệnh cos cần numpy; thiếu numpy thì ca đó tự bỏ qua)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cluster.py"


def run(*args, env=None):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True,
                       env={**os.environ, **(env or {})})
    if r.returncode:
        raise AssertionError(r.stderr)
    return r.stdout


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def wjl(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


class TestOverlap(unittest.TestCase):
    def test_normalize_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            a = ["seed\tpos\turl"]
            a += [f"dịch vụ seo\t{i}\thttps://www.s{i}.vn/x/" for i in range(1, 11)]
            a += [f"công ty seo\t{i}\thttp://s{i}.vn/x" for i in range(1, 5)]
            a += [f"công ty seo\t{i}\thttps://c{i}.vn/" for i in range(5, 11)]
            a += [f"từ khóa là gì\t{i}\thttps://k{i}.vn/" for i in range(1, 11)]
            b = ["seed\tpos\turl"] + [f"dịch vụ seo\t{i}\thttps://z{i}.vn/" for i in range(1, 11)]
            Path(d, "a.tsv").write_text("\n".join(a) + "\n", encoding="utf-8")
            Path(d, "b.tsv").write_text("\n".join(b) + "\n", encoding="utf-8")
            out = json.loads(run("overlap", "--serp", str(Path(d, "a.tsv")), str(Path(d, "b.tsv")), "--out", d))
            self.assertEqual(out["keywords"], 3)
            self.assertEqual(out["conflicts"], 1)  # nguồn sau bị bỏ, nguồn đầu giữ
            ov = {(r["a"], r["b"]): r["overlap"] for r in jl(Path(d, "serp_pairs.jsonl"))}
            self.assertEqual(ov[("dịch vụ seo", "công ty seo")], 4)  # www, http/https, dấu / cuối là cùng URL
            self.assertEqual(ov[("dịch vụ seo", "từ khóa là gì")], 0)


class TestTriageEvaluate(unittest.TestCase):
    def test_real_failure_and_saving(self):
        with tempfile.TemporaryDirectory() as d:
            # Ca hỏng thật (dev 19/10): cặp giá gộp được (7/10) nhưng cosine 0,8961 dưới ngưỡng 0,90.
            cos = [{"a": "báo giá seo website", "b": "bảng giá dịch vụ seo tổng thể", "cos": 0.8961},
                   {"a": "báo giá seo website", "b": "từ khóa là gì", "cos": 0.62},
                   {"a": "bảng giá dịch vụ seo tổng thể", "b": "từ khóa là gì", "cos": 0.60},
                   {"a": "dịch vụ seo", "b": "báo giá seo website", "cos": 0.93},
                   {"a": "dịch vụ seo", "b": "bảng giá dịch vụ seo tổng thể", "cos": 0.95},
                   {"a": "dịch vụ seo", "b": "từ khóa là gì", "cos": 0.70}]
            serp = [{"a": "báo giá seo website", "b": "bảng giá dịch vụ seo tổng thể", "overlap": 7},
                    {"a": "báo giá seo website", "b": "từ khóa là gì", "overlap": 0},
                    {"a": "bảng giá dịch vụ seo tổng thể", "b": "từ khóa là gì", "overlap": 1},
                    {"a": "dịch vụ seo", "b": "báo giá seo website", "overlap": 3},
                    {"a": "dịch vụ seo", "b": "bảng giá dịch vụ seo tổng thể", "overlap": 5},
                    {"a": "dịch vụ seo", "b": "từ khóa là gì", "overlap": 0}]
            wjl(Path(d, "cos.jsonl"), cos)
            wjl(Path(d, "serp.jsonl"), serp)
            summ = json.loads(run("triage", "--cos", str(Path(d, "cos.jsonl")), "--diff-below", "0.90", "--out", d))
            self.assertEqual(summ["can_serp"], 2)
            self.assertEqual(summ["keyword_khong_can_serp"], 1)  # "từ khóa là gì" không cần kéo SERP
            run("evaluate", "--triage", str(Path(d, "triage.jsonl")), "--serp-pairs", str(Path(d, "serp.jsonl")),
                "--out", str(Path(d, "rep.json")))
            rep = json.loads(Path(d, "rep.json").read_text(encoding="utf-8"))
            self.assertEqual(rep["serp_pull_saved"], 1)
            self.assertEqual(rep["sai"]["chac_khac_nhung_overlap_ge_4"], 1)
            self.assertEqual(rep["cap_sai"][0]["overlap"], 7)

    def test_labels(self):
        with tempfile.TemporaryDirectory() as d:
            wjl(Path(d, "cos.jsonl"), [{"a": "x", "b": "y", "cos": 0.9}, {"a": "x", "b": "z", "cos": 0.5}])
            wjl(Path(d, "serp.jsonl"), [{"a": "y", "b": "x", "overlap": 6}, {"a": "x", "b": "z", "overlap": 1}])
            run("labels", "--cos", str(Path(d, "cos.jsonl")), "--serp-pairs", str(Path(d, "serp.jsonl")),
                "--pos-min", "6", "--out", str(Path(d, "rows.jsonl")))
            self.assertEqual([r["label"] for r in jl(Path(d, "rows.jsonl"))], [1, 0])


class TestCosFake(unittest.TestCase):
    def test_cos_fake_encoder(self):
        if subprocess.run([sys.executable, "-I", "-c", "import numpy"], capture_output=True).returncode:
            self.skipTest("thiếu numpy: chạy bằng venv embedding")
        with tempfile.TemporaryDirectory() as d:
            Path(d, "kw.txt").write_text("dịch vụ seo\ncông ty seo\ngiá seo\n", encoding="utf-8")
            run("cos", "--keywords", str(Path(d, "kw.txt")), "--out", str(Path(d, "c.jsonl")), env={"SVI_FAKE": "1"})
            rows = jl(Path(d, "c.jsonl"))
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(-1.0 <= r["cos"] <= 1.0 and r["model"] == "fake" for r in rows))


if __name__ == "__main__":
    unittest.main(verbosity=1)
