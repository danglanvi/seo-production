"""Test offline cho pair_check.py: không mạng, không model; vector giả. Chạy bằng Python có numpy:
~/.venvs/embeddinggemma/bin/python -B tests/test_pair_check.py"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pair_check.py"
spec = importlib.util.spec_from_file_location("pair_check", SCRIPT)
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


def unit(v):
    v = np.asarray(v, dtype="float32")
    return v / np.linalg.norm(v)


def make_store(d, rows):
    d.mkdir(parents=True, exist_ok=True)
    (d / "items.jsonl").write_text("".join(json.dumps({"id": f"{u}#{lvl}{i}", "level": lvl, "url": u}) + "\n"
                                           for i, (u, lvl, _) in enumerate(rows)), encoding="utf-8")
    np.save(d / "vec.npy", np.stack([unit(v) for _, lvl, v in rows]).astype("float16"))


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


class PairCheck(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        V, E = "https://x.test/", "https://x.test/en/"
        rows = [
            (V + "lien-he/", "page", [1, 0.1, 0, 0]), (V + "lien-he/", "section", [1, 0, 0, 0]),
            (V + "dich-vu/", "page", [0, 1, 0.1, 0]), (V + "dich-vu/", "section", [0, 1, 0, 0]),
            (V + "dich-vu/", "section", [0, 0.9, 0.4, 0]),
            (V + "blog/", "page", [0, 0, 0, 1]), (V + "blog/", "section", [0, 0, 0, 1]),
            (E + "contact/", "page", [1, 0.12, 0, 0.05]), (E + "contact/", "section", [1, 0.02, 0, 0]),
            (E + "service/", "page", [0.05, 1, 0.1, 0]), (E + "service/", "section", [0, 1, 0.05, 0]),
            (E + "service/", "section", [0, 0.85, 0.45, 0])]
        make_store(self.t / "store", rows)
        (self.t / "html").mkdir()
        # Ca thật 19/10: trang khai hreflang vi/en/x-default trong <head>, thứ tự thuộc tính khác nhau.
        (self.t / "html" / "a.html").write_text(
            '<link rel="alternate" hreflang="en" href="https://x.test/en/contact/" />'
            '<link hreflang="vi" rel="alternate" href="https://x.test/lien-he/">'
            '<link rel="alternate" hreflang="x-default" href="https://x.test/lien-he/" />', encoding="utf-8")
        (self.t / "html" / "b.html").write_text('<link rel="alternate" hreflang="en" href="https://x.test/en/service/" />',
                                                encoding="utf-8")

    def test_declared(self):
        pc.main(["declared", "--html-dir", str(self.t / "html"), "--out", str(self.t / "d.jsonl")])
        self.assertEqual(jl(self.t / "d.jsonl"), [{"a_url": "https://x.test/lien-he/", "b_url": "https://x.test/en/contact/",
                                                    "source": "a.html"}])

    def test_pairs_and_report(self):
        pc.main(["declared", "--html-dir", str(self.t / "html"), "--out", str(self.t / "d.jsonl")])
        pc.main(["pairs", "--store", str(self.t / "store"), "--b-prefix", "/en/", "--declared", str(self.t / "d.jsonl"),
                 "--k", "2", "--out", str(self.t / "p.jsonl")])
        pairs = {(r["b_url"][14:], r["a_url"][14:]): r for r in jl(self.t / "p.jsonl")}
        self.assertEqual(len(pairs), 4)
        top = pairs[("/en/service/", "/dich-vu/")]
        self.assertEqual(top["rank"], 1)
        self.assertGreater(top["sec_cov"], 0.95)
        self.assertTrue(pairs[("/en/contact/", "/lien-he/")]["declared"])
        reg = self.t / "reg.json"
        reg.write_text(json.dumps({"entries": [{"rubric": "hreflang-pair", "version": "sec_cov", "mode": "cosine",
                                                "site": "x.test", "threshold": None, "reject_below": 0.82}]}), encoding="utf-8")
        pc.main(["report", "--pairs", str(self.t / "p.jsonl"), "--registry", str(reg), "--site", "x.test",
                 "--out-dir", str(self.t / "w")])
        pages = {p["b_url"][14:]: p for p in jl(self.t / "w" / "pages.jsonl")}
        self.assertEqual(pages["/en/contact/"]["flag"], "cặp đã khai: Claude đọc")
        self.assertEqual(pages["/en/service/"]["flag"], "chưa khai hreflang: Claude đọc ứng viên")
        self.assertEqual(pages["/en/service/"]["best"], "https://x.test/dich-vu/")
        decided = {(r["b_url"][14:], r["a_url"][14:]): r["decision"] for r in jl(self.t / "w" / "pairs_decided.jsonl")}
        self.assertEqual(decided[("/en/service/", "/lien-he/")], "Claude đọc cuối")   # dưới ngưỡng nháp: không loại
        self.assertEqual(pages["/en/service/"]["shortlist"][-1], "https://x.test/lien-he/")
        self.assertIn("https://x.test/lien-he/", pages["/en/service/"]["low"])

    def test_no_gate_means_claude_reads(self):
        self.assertEqual(pc.decide(0.99, {})[0], "Claude đọc")
        self.assertEqual(pc.decide(None, {"reject": 0.8})[0], "Claude đọc")
        dec, why = pc.decide(0.7, {"reject": 0.8})
        self.assertEqual(dec, "Claude đọc cuối")
        self.assertIn("nháp, chưa holdout", why)


if __name__ == "__main__":
    unittest.main()
