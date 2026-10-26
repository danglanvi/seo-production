#!/usr/bin/env python3
"""Test offline cho gsc_route.py: không cần mạng, không cần model. Chạy: python3 skills/query-processing-diagnosis/tests/test_gsc_route.py"""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gsc_route.py"


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(r.stderr)
    return r.stdout


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


GSC = {"rows": [
    {"keys": ["dịch vụ seo", "https://x.vn/dich-vu-seo/"], "clicks": 10, "impressions": 700, "position": 10},
    {"keys": ["Dịch vụ SEO", "https://x.vn/dich-vu-seo/"], "clicks": 1, "impressions": 100, "position": 12},
    {"keys": ["dịch vụ seo", "https://x.vn/bang-gia/"], "clicks": 0, "impressions": 200, "position": 30},
    # Dòng jump link lặp hiển thị của URL gốc: phải bỏ (GSC 18/10 có 6.702/25.000 dòng loại này).
    {"keys": ["dịch vụ seo", "https://x.vn/dich-vu-seo/#ftoc-1"], "clicks": 0, "impressions": 900, "position": 9},
    {"keys": ["giá seo", "https://x.vn/bang-gia/"], "clicks": 0, "impressions": 15, "position": 20},
]}


class TestPrep(unittest.TestCase):
    def test_merge_jump_link_share(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "gsc.json").write_text(json.dumps(GSC, ensure_ascii=False), encoding="utf-8")
            Path(d, "kw.txt").write_text("Dịch vụ SEO\ngiá seo\nseo là gì\n", encoding="utf-8")
            Path(d, "c.txt").write_text("https://x.vn/dich-vu-seo/\nhttps://x.vn/bang-gia/\n", encoding="utf-8")
            run("prep", "--gsc", str(Path(d, "gsc.json")), "--keywords", str(Path(d, "kw.txt")), "--candidates",
                str(Path(d, "c.txt")), "--keep-missing", "--out", str(Path(d, "q.jsonl")))
            rows = jl(Path(d, "q.jsonl"))
            self.assertEqual([r["text"] for r in rows], ["dịch vụ seo", "giá seo", "seo là gì"])
            q = rows[0]
            self.assertEqual(q["impr"], 1000)  # 700 + 100 (gộp casefold) + 200; bỏ 900 của jump link
            self.assertEqual(q["chosen"], "https://x.vn/dich-vu-seo/")
            self.assertEqual(q["share"], 0.8)
            self.assertEqual(len(q["candidates"]), 2)
            self.assertIsNone(rows[1]["chosen"])  # 15 hiển thị < 20
            self.assertTrue(rows[2]["khong_du_gsc"])

    def test_chosen_from_spyserp_hang_tsv(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "gsc.json").write_text(json.dumps(GSC, ensure_ascii=False), encoding="utf-8")
            Path(d, "hang.tsv").write_text("keyword\ttemplate\turl\tnow\n"
                                           "dịch vụ seo\tT1\thttps://x.vn/bang-gia/\t12\n"
                                           "\"seo agency\"\tT2\thttps://x.vn/agency/\t30\n", encoding="utf-8")
            Path(d, "kw.txt").write_text("dịch vụ seo\n\"seo agency\"\n", encoding="utf-8")
            run("prep", "--gsc", str(Path(d, "gsc.json")), "--keywords", str(Path(d, "kw.txt")), "--groups",
                str(Path(d, "hang.tsv")), "--group-col", "template", "--chosen-col", "url", "--out", str(Path(d, "q.jsonl")))
            rows = jl(Path(d, "q.jsonl"))
            self.assertEqual([(r["chosen"], r["group"]) for r in rows],
                             [("https://x.vn/bang-gia/", "T1"), ("https://x.vn/agency/", "T2")])
            self.assertEqual(rows[0]["share"], 0.2)  # 200/1000 hiển thị GSC của URL SpySERP
            self.assertIsNone(rows[1]["share"])  # keyword có dấu nháy kép vẫn khớp nhóm; không có GSC

    def test_tsv_relative_page(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "gsc.tsv").write_text("page\tquery\tclicks\timpressions\tposition\n/a/\tseo\t1\t50\t3\n",
                                          encoding="utf-8")
            run("prep", "--gsc", str(Path(d, "gsc.tsv")), "--base", "https://x.vn", "--out", str(Path(d, "q.jsonl")))
            self.assertEqual(jl(Path(d, "q.jsonl"))[0]["chosen"], "https://x.vn/a/")


class TestSummary(unittest.TestCase):
    def test_verdicts(self):
        routing = [
            {"id": "q0", "text": "a", "group": "T1", "chosen": "u1", "gemma_top": "u1", "chosen_rank": 1, "agree_top1": True, "impr": 100, "share": 0.9},
            {"id": "q1", "text": "b", "group": "T1", "chosen": "u1", "gemma_top": "u2", "chosen_rank": 2, "agree_top1": False, "impr": 50, "share": 0.4},
            {"id": "q2", "text": "c", "group": "T2", "chosen": "u3", "gemma_top": "u2", "chosen_rank": 5, "agree_top1": False, "impr": 30, "share": 0.95},
            {"id": "q3", "text": "d", "group": "T2", "chosen": None, "gemma_top": "u2", "chosen_rank": None, "agree_top1": False},
            {"id": "q4", "text": "e", "group": "T2", "chosen": "u1", "gemma_top": "u2", "chosen_rank": 2, "agree_top1": False, "share": None},
        ]
        with tempfile.TemporaryDirectory() as d:
            Path(d, "r.jsonl").write_text("".join(json.dumps(r) + "\n" for r in routing), encoding="utf-8")
            out = json.loads(run("summary", "--routing", str(Path(d, "r.jsonl")), "--out", str(Path(d, "s"))))
            self.assertEqual(out, {"query": 5, "co_url_google": 4, "top1_khop": 1, "top3_khop": 3})
            v = [r["verdict"] for r in csv.DictReader(Path(d, "s.tsv").open(encoding="utf-8"), delimiter="\t")]
            self.assertTrue(v[0] == "khớp" and v[1].startswith("Google chia query") and v[2].startswith("Google chọn URL khác")
                            and v[3].startswith("chưa có dữ liệu GSC") and v[4].startswith("Gemma chọn URL khác, chưa có share"))
            g = json.loads(Path(d, "s_group.json").read_text(encoding="utf-8"))["group"]
            self.assertEqual(g["T1"]["ty_le_impr_khop"], round(100 / 150, 3))


if __name__ == "__main__":
    unittest.main(verbosity=1)
