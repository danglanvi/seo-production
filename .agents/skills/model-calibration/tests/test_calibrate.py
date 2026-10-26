#!/usr/bin/env python3
"""Test offline cho calibrate.py bằng dữ liệu tổng hợp biết trước đáp án. Chạy: python3 -E tests/test_calibrate.py"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

CAL = Path(__file__).resolve().parent.parent / "scripts" / "calibrate.py"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-E", str(CAL), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(path, rows):
    Path(path).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def main():
    rng = np.random.default_rng(1)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        # Jev: nhãn dương có xác suất cao thì đúng; dưới 0,6 thì nhiễu
        gold, pred = [], []
        for i in range(120):
            p = float(rng.uniform(0.3, 1.0))
            truth = "match" if (p >= 0.75 or rng.random() < 0.3) else "other"
            choice = "match" if p >= 0.5 else "other"
            gold.append({"id": str(i), "label": truth})
            pred.append({"id": str(i), "answers": {"m": {"choice": choice, "confidence": max(p, 1 - p),
                                                          "probabilities": {"match": p, "other": 1 - p}}}})
        write(t / "g.jsonl", gold)
        write(t / "p.jsonl", pred)
        run("jev", "--pred", t / "p.jsonl", "--gold", t / "g.jsonl", "--question", "m", "--positive", "match",
            "--out", t / "r.json", "--registry", t / "reg.json", "--rubric", "demo", "--version", "1",
            "--model", "typesafe/jev-1.14", "--site", "mau.vn", "--write")
        r = json.loads((t / "r.json").read_text())
        assert r["recommended"] and r["recommended"]["thr"] >= 0.75, r["recommended"]
        reg = json.loads((t / "reg.json").read_text())
        # v1.4: không có --holdout thì entry là draft, threshold null, giá trị đề xuất nằm ở draft_values
        e0 = reg["entries"][0]
        assert len(reg["entries"]) == 1 and e0["status"] == "draft" and e0["threshold"] is None, e0
        assert e0["draft_values"]["threshold"] == r["recommended"]["thr"]
        # ghi lại cùng khoá: thay, không nhân đôi
        run("jev", "--pred", t / "p.jsonl", "--gold", t / "g.jsonl", "--question", "m", "--positive", "match",
            "--out", t / "r.json", "--registry", t / "reg.json", "--rubric", "demo", "--version", "1",
            "--model", "typesafe/jev-1.14", "--site", "mau.vn", "--write")
        assert len(json.loads((t / "reg.json").read_text())["entries"]) == 1
        # câu hỏi 3 lớp: confidence >= 0,7 luôn đúng, dưới 0,7 sai một nửa -> cổng confidence ở 0,7
        g3, p3 = [], []
        for i in range(80):
            c = 0.9 if i < 50 else 0.55
            truth = ["a", "b", "c"][i % 3]
            choice = truth if (c > 0.7 or i % 2) else ["a", "b", "c"][(i + 1) % 3]
            g3.append({"id": f"k{i}", "label": truth})
            p3.append({"id": f"k{i}", "answers": {"k": {"choice": choice, "confidence": c}}})
        write(t / "g3.jsonl", g3)
        write(t / "p3.jsonl", p3)
        run("jev", "--pred", t / "p3.jsonl", "--gold", t / "g3.jsonl", "--question", "k", "--positive", "a",
            "--target", "0.9", "--out", t / "r3.json")
        r3 = json.loads((t / "r3.json").read_text())
        assert r3["conf_gate"] and 0.55 < r3["conf_gate"]["conf"] <= 0.9, r3["conf_gate"]
        # thiếu mẫu: dừng
        write(t / "g2.jsonl", gold[:5])
        run("jev", "--pred", t / "p.jsonl", "--gold", t / "g2.jsonl", "--question", "m", "--positive", "match", ok=False)

        # cosine: dương 0,8–0,95, âm 0,4–0,75 -> ngưỡng nhận nằm trong khoảng dương
        pairs = [{"id": f"p{i}", "cos": float(rng.uniform(0.8, 0.95)), "label": 1} for i in range(40)]
        pairs += [{"id": f"n{i}", "cos": float(rng.uniform(0.4, 0.75)), "label": 0} for i in range(60)]
        write(t / "pairs.jsonl", pairs)
        run("cosine", "--pairs", t / "pairs.jsonl", "--out", t / "c.json")
        c = json.loads((t / "c.json").read_text())
        assert c["accept"] and c["accept"]["thr"] <= c["min_positive"] and c["accept"]["precision"] >= 0.95, c["accept"]
        assert c["max_negative"] < c["min_positive"]
        # cosine --grid: điểm âm (margin) -> ngưỡng nằm trong dải âm, không bị cắt ở 0,50
        write(t / "mpairs.jsonl", [{**p, "cos": p["cos"] - 0.9} for p in pairs])
        run("cosine", "--pairs", t / "mpairs.jsonl", "--grid=-0.6:0.1:0.01", "--out", t / "m.json")
        m = json.loads((t / "m.json").read_text())
        assert m["accept"] and m["accept"]["thr"] < 0 and m["accept"]["thr"] <= m["min_positive"], m["accept"]
        assert m["accept"]["precision"] >= 0.95

        # proxy: metric tương quan dương theo nhóm -> dùng được; metric ngẫu nhiên -> chưa chứng minh
        rows = []
        for g in range(30):
            for k in range(6):
                m = float(rng.random())
                rows.append({"g": g, "m": m, "noise": float(rng.random()), "y": m * 5 + float(rng.normal(0, 0.8))})
        write(t / "d.jsonl", rows)
        run("proxy", "--data", t / "d.jsonl", "--metric", "m", "--outcome", "y", "--group", "g", "--out", t / "x.json")
        assert json.loads((t / "x.json").read_text())["verdict"].startswith("dùng được")
        run("proxy", "--data", t / "d.jsonl", "--metric", "noise", "--outcome", "y", "--group", "g", "--out", t / "y.json")
        assert json.loads((t / "y.json").read_text())["verdict"].startswith("chưa chứng minh")

        # control: metric chỉ tương quan qua độ dài -> khử độ dài thì mất tín hiệu
        rows = []
        for k in range(200):
            ln = float(rng.random())
            rows.append({"len": ln, "m": ln + float(rng.normal(0, 0.1)), "y": ln * 5 + float(rng.normal(0, 0.5))})
        write(t / "l.jsonl", rows)
        run("proxy", "--data", t / "l.jsonl", "--metric", "m", "--outcome", "y", "--out", t / "l0.json")
        assert json.loads((t / "l0.json").read_text())["verdict"].startswith("dùng được")
        run("proxy", "--data", t / "l.jsonl", "--metric", "m", "--outcome", "y", "--control", "len", "--out", t / "l1.json")
        l1 = json.loads((t / "l1.json").read_text())
        assert not l1["verdict"].startswith("dùng được") and "khử len" in l1["unit"], l1

        # auc: mục được trích có điểm cao hơn trong từng pool -> dùng được; điểm ngẫu nhiên -> chưa chứng minh
        rows = []
        for g in range(25):
            for k in range(8):
                y = int(k < 3)
                rows.append({"pool": g, "cited": y, "m": y * 0.6 + float(rng.random()), "noise": float(rng.random())})
        write(t / "a.jsonl", rows)
        run("auc", "--data", t / "a.jsonl", "--metric", "m", "--label", "cited", "--group", "pool", "--out", t / "a1.json",
            "--registry", t / "reg.json", "--rubric", "r", "--version", "1", "--model", "m", "--site", "mau.vn", "--write")
        a1 = json.loads((t / "a1.json").read_text())
        assert a1["verdict"].startswith("dùng được") and a1["auc"] > 0.6, a1
        run("auc", "--data", t / "a.jsonl", "--metric", "noise", "--label", "cited", "--group", "pool", "--out", t / "a2.json")
        assert json.loads((t / "a2.json").read_text())["verdict"].startswith("chưa chứng minh")
        reg = json.loads((t / "reg.json").read_text())
        assert any(e["mode"] == "auc" and e["auc"] == a1["auc"] for e in reg["entries"])
        run("show", "--registry", t / "reg.json")
    print("test_calibrate: đạt")


if __name__ == "__main__":
    main()
