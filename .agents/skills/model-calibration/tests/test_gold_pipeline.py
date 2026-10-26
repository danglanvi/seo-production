#!/usr/bin/env python3
"""Test offline cho gold-sheet, gold-merge, pipeline và cổng holdout của calibrate.py (v1.4).
Chạy: python3 -E tests/test_gold_pipeline.py

Ca hỏng thật lấy từ phiên 19/10/2026:
- pipeline Jev -> GLM so với gold: 15 khớp, 7 gold có mà chuỗi không bắt (recall 0,68); tin cuối chỉ báo Jev đúng.
- Ngưỡng chọn trên chính 53 trang gold, không có holdout, rồi vào báo cáo.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

CAL = Path(__file__).resolve().parent.parent / "scripts" / "calibrate.py"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-E", str(CAL), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (p.returncode, p.stdout, p.stderr)
    return p


def write(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jev_rows(rng, prefix, n, noisy_top=False):
    """Mục có xác suất p. Gold: p >= 0,75 luôn là 'match'. noisy_top: nửa số mục p cao lại là 'other'."""
    gold, pred = [], []
    for i in range(n):
        p = float(rng.uniform(0.3, 1.0))
        truth = "match" if (p >= 0.75 or rng.random() < 0.3) else "other"
        if noisy_top and p >= 0.75 and i % 2:
            truth = "other"
        gold.append({"id": f"{prefix}{i}", "label": truth})
        pred.append({"id": f"{prefix}{i}", "text": f"nội dung {prefix}{i}",
                     "answers": {"m": {"choice": "match" if p >= 0.5 else "other", "confidence": max(p, 1 - p),
                                       "probabilities": {"match": p, "other": 1 - p}}}})
    return gold, pred


def test_pipeline_recall(t):
    # 60 mục gold: 22 có thật. Chuỗi bắt 15, sót 7 (5 mất ở bước jev, 2 ở bước glm). Không báo nhầm mục nào.
    gold, rows = [], []
    for i in range(22):
        gold.append({"id": f"y{i}", "label": "yes"})
        if i < 15:
            rows.append({"id": f"y{i}", "jev": True, "glm": True})
        elif i < 20:
            rows.append({"id": f"y{i}", "jev": False})
        else:
            rows.append({"id": f"y{i}", "jev": True, "glm": False})
    for i in range(38):
        gold.append({"id": f"n{i}", "label": "no"})
        rows.append({"id": f"n{i}", "jev": i % 5 == 0, "glm": False})
    write(t / "pg.jsonl", gold)
    write(t / "pp.jsonl", rows)
    run("pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg.jsonl", "--positive", "yes", "--stages", "jev,glm",
        "--out", t / "pr.json")
    r = json.loads((t / "pr.json").read_text())
    assert r["table"] == {"tp": 15, "fn": 7, "fp": 0, "tn": 38}, r["table"]
    assert r["recall"] == 0.682 and r["precision"] == 1.0, r
    assert r["missed_by_stage"] == {"jev": 5, "glm": 2}, r["missed_by_stage"]
    assert r["stage_recall"]["jev"] == round(17 / 22, 3)
    # độ sót phải nằm cạnh độ đúng trong báo cáo và verdict
    assert "recall 0.682" in r["report_line"] and "precision 1.0" in r["report_line"], r["report_line"]
    assert r["verdict"].startswith("recall thấp"), r["verdict"]
    # hạ ngưỡng recall thì đạt
    run("pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg.jsonl", "--positive", "yes", "--stages", "jev,glm",
        "--min-recall", "0.6", "--out", t / "pr2.json")
    assert json.loads((t / "pr2.json").read_text())["verdict"].startswith("đạt")
    # mục gold vắng trong pred tính là chưa bắt và được đếm
    write(t / "pp_short.jsonl", rows[:15])
    run("pipeline", "--pred", t / "pp_short.jsonl", "--gold", t / "pg.jsonl", "--positive", "yes",
        "--stages", "jev,glm", "--out", t / "pr3.json")
    r3 = json.loads((t / "pr3.json").read_text())
    assert r3["table"]["fn"] == 7 and r3["absent_in_pred"] == 45, r3
    # lỗi đầu vào: gold quá ít, một bước, thiếu lớp
    write(t / "pg_small.jsonl", gold[:8])
    run("pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg_small.jsonl", "--positive", "yes", "--stages", "jev,glm", ok=False)
    run("pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg.jsonl", "--positive", "yes", "--stages", "jev", ok=False)
    run("pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg.jsonl", "--positive", "khong-co", "--stages", "jev,glm", ok=False)


def test_holdout_gate(t):
    rng = np.random.default_rng(3)
    tune_g, tune_p = jev_rows(rng, "t", 120)      # đủ mẫu để Wilson cho phép chọn ngưỡng
    hold_g, hold_p = jev_rows(rng, "h", 120)
    bad_g, bad_p = jev_rows(rng, "b", 120, noisy_top=True)
    small_g, small_p = hold_g[:20], hold_p[:20]
    write(t / "gold.jsonl", tune_g)
    write(t / "hold.jsonl", hold_g)
    write(t / "hold_bad.jsonl", bad_g)
    write(t / "hold_small.jsonl", small_g)
    write(t / "hold_dup.jsonl", tune_g[:50] + hold_g)  # 50 id trùng gold hiệu chuẩn
    write(t / "pred.jsonl", tune_p + hold_p + bad_p)
    base = ["jev", "--pred", t / "pred.jsonl", "--gold", t / "gold.jsonl", "--question", "m", "--positive", "match",
            "--rubric", "demo", "--version", "1", "--model", "m", "--site", "mau.vn", "--write"]

    def entry(name, *extra):
        reg = t / f"{name}.json"
        run(*base, "--registry", reg, "--out", t / f"{name}.res.json", *extra)
        return json.loads(reg.read_text())["entries"][0]

    # 1. không holdout: draft, threshold null (ca ngưỡng chọn trên chính gold)
    e = entry("no_hold")
    assert e["status"] == "draft" and e["threshold"] is None and e["conf_gate"] is None, e
    assert e["draft_values"]["threshold"] is not None and "holdout" in e["draft_reason"]
    # 2. holdout mới, đủ mẫu, ngưỡng giữ được: ready
    e = entry("ok_hold", "--holdout", t / "hold.jsonl")
    assert e["status"] == "ready" and e["threshold"] is not None and e["draft_values"] is None, e
    assert e["holdout"]["passed"] and e["holdout"]["n"] == 120
    # 3. holdout mà ngưỡng không giữ: draft kèm lý do
    e = entry("bad_hold", "--holdout", t / "hold_bad.jsonl")
    assert e["status"] == "draft" and e["threshold"] is None and "không giữ được" in e["draft_reason"], e
    # 4. holdout dưới 40 mẫu: draft
    e = entry("small_hold", "--holdout", t / "hold_small.jsonl")
    assert e["status"] == "draft" and "cần ≥ 40" in e["draft_reason"], e
    # 5. holdout trùng gold hiệu chuẩn: lỗi, không ghi registry
    run(*base, "--registry", t / "dup.json", "--holdout", t / "hold_dup.jsonl", ok=False)
    assert not (t / "dup.json").exists()
    # cosine: không holdout thì draft; có holdout thì ready
    pairs = [{"id": f"p{i}", "cos": float(rng.uniform(0.8, 0.95)), "label": 1} for i in range(40)]
    pairs += [{"id": f"n{i}", "cos": float(rng.uniform(0.4, 0.75)), "label": 0} for i in range(60)]
    hp = [{"id": f"hp{i}", "cos": float(rng.uniform(0.8, 0.95)), "label": 1} for i in range(25)]
    hp += [{"id": f"hn{i}", "cos": float(rng.uniform(0.4, 0.75)), "label": 0} for i in range(35)]
    write(t / "pairs.jsonl", pairs)
    write(t / "hpairs.jsonl", hp)
    cb = ["cosine", "--pairs", t / "pairs.jsonl", "--rubric", "c", "--version", "1", "--model", "g", "--site", "mau.vn", "--write"]
    run(*cb, "--registry", t / "c1.json", "--out", t / "c1.res.json")
    run(*cb, "--registry", t / "c2.json", "--holdout", t / "hpairs.jsonl", "--out", t / "c2.res.json")
    c1 = json.loads((t / "c1.json").read_text())["entries"][0]
    c2 = json.loads((t / "c2.json").read_text())["entries"][0]
    assert c1["status"] == "draft" and c1["threshold"] is None and c1["draft_values"]["threshold"] is not None
    assert c2["status"] == "ready" and c2["threshold"] is not None
    # pipeline có holdout: ready khi chuỗi giữ recall và precision trên holdout
    gold, rows = [], []
    for k in range(60):
        pos = k < 25
        gold.append({"id": f"a{k}", "label": "yes" if pos else "no"})
        rows.append({"id": f"a{k}", "jev": pos, "glm": pos})
    hgold = [{"id": f"z{k}", "label": "yes" if k < 25 else "no"} for k in range(60)]
    rows += [{"id": f"z{k}", "jev": k < 25, "glm": k < 25} for k in range(60)]
    write(t / "pg.jsonl", gold)
    write(t / "pz.jsonl", hgold)
    write(t / "pp.jsonl", rows)
    pb = ["pipeline", "--pred", t / "pp.jsonl", "--gold", t / "pg.jsonl", "--positive", "yes", "--stages", "jev,glm",
          "--rubric", "p", "--version", "1", "--model", "m", "--site", "mau.vn", "--write"]
    run(*pb, "--registry", t / "p1.json", "--holdout", t / "pz.jsonl", "--out", t / "p1.res.json")
    run(*pb, "--registry", t / "p2.json", "--out", t / "p2.res.json")
    assert json.loads((t / "p1.json").read_text())["entries"][0]["status"] == "ready"
    p2 = json.loads((t / "p2.json").read_text())["entries"][0]
    assert p2["status"] == "draft" and p2["recall"] == 1.0, p2
    run("show", "--registry", t / "p2.json")


def test_gold_sheet_and_merge(t):
    rng = np.random.default_rng(5)
    # 300 mục, confidence rải đều 0,5-1,0; 12 mục đánh dấu khó; có nhãn model để kiểm không lộ ra phiếu
    rows = []
    for i in range(300):
        p = float(rng.uniform(0.5, 1.0))
        rows.append({"id": f"i{i}", "text": f"Đoạn văn số {i} về chủ đề X",
                     "answers": {"q": {"choice": "NHAN_MODEL_BI_MAT", "confidence": p}}})
    rows[7]["answers"]["q"] = {"p_yes": 0.97}
    rows[250]["answers"]["other"] = {"choice": "x", "confidence": 0.9}
    del rows[250]["answers"]["q"]
    write(t / "out.jsonl", rows)
    (t / "hard.txt").write_text("\n".join(f"i{i}" for i in range(100, 112)) + "\n", encoding="utf-8")
    args = ["gold-sheet", "--pred", t / "out.jsonl", "--question", "q", "--n", "60", "--hard", t / "hard.txt",
            "--labels", "match,other", "--out", t / "sheet.txt"]
    # chạy thử: không ghi file
    r = json.loads(run(*args).stdout)
    assert r["dry_run"] and r["selected"] == 60 and not (t / "sheet.txt").exists(), r
    assert r["skipped_no_answer"] == 1
    assert r["by_stratum"]["hard"] == 12, r["by_stratum"]
    bands = {k: v for k, v in r["by_stratum"].items() if k != "hard"}
    assert len(bands) == 5 and max(bands.values()) - min(bands.values()) <= 1, bands  # dải 0,5-1,0 chia đều
    # ghi thật
    run(*args, "--write")
    sheet = (t / "sheet.txt").read_text(encoding="utf-8")
    assert sheet.count("### id:") == 60 and "# LABELS: match|other" in sheet
    assert "NHAN_MODEL_BI_MAT" not in sheet and "confidence" not in sheet and "0.9" not in sheet  # mù: không lộ nhãn model
    assert "Đoạn văn số" in sheet
    # cùng seed cho cùng phiếu
    run(*args[:-2], "--out", t / "sheet2.txt", "--write")
    assert (t / "sheet2.txt").read_text(encoding="utf-8") == sheet
    # thiếu --out khi --write, thiếu --question, thiếu nguồn: lỗi
    run("gold-sheet", "--pred", t / "out.jsonl", "--question", "q", "--write", ok=False)
    run("gold-sheet", "--pred", t / "out.jsonl", "--out", t / "x.txt", ok=False)
    run("gold-sheet", "--out", t / "x.txt", ok=False)
    # --items (chưa có nhãn model) và --exclude-gold
    write(t / "items.jsonl", [{"id": f"u{i}", "url": f"https://mau.vn/{i}"} for i in range(30)])
    write(t / "g0.jsonl", [{"id": "u0", "label": "a"}])
    r = json.loads(run("gold-sheet", "--items", t / "items.jsonl", "--n", "100", "--exclude-gold", t / "g0.jsonl").stdout)
    assert r["selected"] == 29 and r["by_stratum"] == {"all": 29}, r
    # contact sheet ảnh
    write(t / "imgs.jsonl", [{"id": f"m{i}", "image": f"img/{i}.png"} for i in range(10)])
    run("gold-sheet", "--items", t / "imgs.jsonl", "--n", "6", "--format", "html", "--out", t / "cs.html", "--write")
    h = (t / "cs.html").read_text(encoding="utf-8")
    assert h.count("<img") == 6 and (t / "cs.todo.txt").read_text(encoding="utf-8").count("### id:") == 6
    write(t / "noimg.jsonl", [{"id": "m1", "text": "x"}])
    run("gold-sheet", "--items", t / "noimg.jsonl", "--format", "html", "--out", t / "n.html", ok=False)

    # gold-merge: điền 45 nhãn match/other, để trống 10 ca mơ hồ, đánh '?' 5 ca
    lines, ids, k = sheet.splitlines(), [], 0
    out = []
    for ln in lines:
        if ln.startswith("### id: "):
            ids.append(ln[8:])
        if ln == "LABEL:":
            k += 1
            ln = "LABEL: " + ("" if k <= 10 else "?" if k <= 15 else "match" if k % 2 else "other")
        out.append(ln)
    (t / "filled.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    m = json.loads(run("gold-merge", "--todo", t / "filled.txt", "--gold", t / "gold.jsonl").stdout)
    assert m["dry_run"] and m["added"] == 45 and m["ambiguous"] == 15 and not (t / "gold.jsonl").exists(), m
    run("gold-merge", "--todo", t / "filled.txt", "--gold", t / "gold.jsonl", "--write")
    g = [json.loads(x) for x in (t / "gold.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(g) == 45 and all(x["label"] in ("match", "other") for x in g)
    assert not ({x["id"] for x in g} & set(m["ambiguous_ids"]))
    # chạy lại cùng phiếu: không đổi
    m2 = json.loads(run("gold-merge", "--todo", t / "filled.txt", "--gold", t / "gold.jsonl", "--write").stdout)
    assert m2["added"] == 0 and m2["unchanged"] == 45 and m2["total"] == 45
    # gold đã ghép đọc được bằng lệnh jev (id i* khớp pred)
    run("jev", "--pred", t / "out.jsonl", "--gold", t / "gold.jsonl", "--question", "q", "--positive", "match",
        "--out", t / "j.json")
    # nhãn ngoài danh sách: lỗi. Sửa gold đã có thiếu lý do: lỗi. Có lý do: ghi kèm note.
    (t / "bad.txt").write_text("\n".join(out).replace("LABEL: match", "LABEL: matc", 1) + "\n", encoding="utf-8")
    run("gold-merge", "--todo", t / "bad.txt", "--gold", t / "g_bad.jsonl", ok=False)
    first = next(x for x in g if x["label"] == "match")
    flip = "\n".join(out).replace(f"### id: {first['id']}\n", f"### id: {first['id']}\n", 1)
    blocks = flip.split("### id: ")
    for n, b in enumerate(blocks):
        if b.startswith(first["id"] + "\n"):
            blocks[n] = b.replace("LABEL: match", "LABEL: other")
    (t / "flip.txt").write_text("### id: ".join(blocks), encoding="utf-8")
    run("gold-merge", "--todo", t / "flip.txt", "--gold", t / "gold.jsonl", "--write", ok=False)
    run("gold-merge", "--todo", t / "flip.txt", "--gold", t / "gold.jsonl", "--overwrite", ok=False)
    run("gold-merge", "--todo", t / "flip.txt", "--gold", t / "gold.jsonl", "--overwrite", "--reason", "đọc lại: model đúng", "--write")
    g2 = {x["id"]: x for x in (json.loads(l) for l in (t / "gold.jsonl").read_text(encoding="utf-8").splitlines())}
    assert g2[first["id"]]["label"] == "other" and g2[first["id"]]["note"] == "đọc lại: model đúng"
    # phiếu rỗng: lỗi
    (t / "empty.txt").write_text("# trống\n", encoding="utf-8")
    run("gold-merge", "--todo", t / "empty.txt", "--gold", t / "gold.jsonl", ok=False)


def test_cosine_gold_join(t):
    # Dòng cosine: cặp có cos nhưng chưa có nhãn -> gold-sheet --items -> gán tay -> gold-merge -> cosine --gold.
    pool = []
    for k in range(35):
        pool.append({"id": f"tp{k}", "text": f"cặp {k}", "cos": round(0.86 + 0.13 * k / 34, 4), "truth": 1})
        pool.append({"id": f"tn{k}", "text": f"cặp âm {k}", "cos": round(0.55 + 0.25 * k / 34, 4), "truth": 0})
    for k in range(30):
        pool.append({"id": f"hp{k}", "text": f"cặp mới {k}", "cos": round(0.86 + 0.13 * k / 29, 4), "truth": 1})
        pool.append({"id": f"hn{k}", "text": f"cặp mới âm {k}", "cos": round(0.50 + 0.25 * k / 29, 4), "truth": 0})
    truth = {r["id"]: r.pop("truth") for r in pool}
    write(t / "pool.jsonl", pool)
    # phiếu mù: không lộ cos
    run("gold-sheet", "--items", t / "pool.jsonl", "--n", "200", "--labels", "1,0", "--out", t / "ph.txt", "--write")
    sheet = (t / "ph.txt").read_text(encoding="utf-8")
    assert "cos" not in sheet and "0.86" not in sheet and "# LABELS: 1|0" in sheet
    # gán tay: tuning = tp/tn, holdout = hp/hn
    def fill(prefixes, path):
        out, cur = [], None
        for line in sheet.splitlines():
            if line.startswith("### id: "):
                cur = line[8:]
            if line == "LABEL:" and cur and cur[:2] in prefixes:
                line = f"LABEL: {truth[cur]}"
            out.append(line)
        Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")
    fill(("tp", "tn"), t / "ph_tune.txt")
    fill(("hp", "hn"), t / "ph_hold.txt")
    run("gold-merge", "--todo", t / "ph_tune.txt", "--gold", t / "gold.jsonl", "--write")
    run("gold-merge", "--todo", t / "ph_hold.txt", "--gold", t / "hold.jsonl", "--write")
    base = ["cosine", "--pairs", t / "pool.jsonl", "--gold", t / "gold.jsonl"]
    res = json.loads(run(*base).stdout)
    assert res["n"] == 70 and res["n_positive"] == 35 and res["accept"], res
    reg = ["--registry", t / "reg.json", "--rubric", "c", "--version", "1", "--model", "g", "--site", "mau.vn", "--write"]
    run(*base, "--holdout", t / "hold.jsonl", *reg)
    e = json.loads((t / "reg.json").read_text(encoding="utf-8"))["entries"][-1]
    assert e["status"] == "ready" and e["holdout"]["n"] == 60 and e["threshold"] is not None, e
    # holdout trùng gold hiệu chuẩn: lỗi
    run(*base, "--holdout", t / "gold.jsonl", ok=False)
    # nhãn không phải 1|0: lỗi rõ
    write(t / "bad.jsonl", [{"id": "tp0", "label": "yes"}])
    p = run("cosine", "--pairs", t / "pool.jsonl", "--gold", t / "bad.jsonl", ok=False)
    assert "--labels 1,0" in p.stderr, p.stderr
    # id gold vắng trong --pairs: cảnh báo, vẫn chạy
    gold_rows = [json.loads(l) for l in (t / "gold.jsonl").read_text(encoding="utf-8").splitlines()]
    write(t / "gold_x.jsonl", gold_rows + [{"id": "khong-co", "label": "1"}])
    p = run("cosine", "--pairs", t / "pool.jsonl", "--gold", t / "gold_x.jsonl")
    assert "không có trong --pairs" in p.stderr and json.loads(p.stdout)["n"] == 70


def test_gold_sheet_content(t):
    # Ca thật 25/10: đầu ra jev.py chỉ có id, answers, model, task, cost. Phiếu dựng từ --pred để trống nội dung.
    # --content (đầu vào Jev) ghép state theo id; nhãn lấy từ criteria của câu hỏi khi thiếu --labels.
    crit = {"primary": {"seo-technical": "kỹ thuật", "seo-onpage": "onpage", "unknown": "không rõ"}}
    pred, inp = [], []
    for i in range(30):
        c = 0.45 + 0.018 * i
        pred.append({"id": str(1000 + i), "model": "jev", "task": "category-pick", "cost": 6e-05,
                     "answers": {"primary": {"choice": "seo-technical", "confidence": round(c, 3),
                                             "probabilities": {"seo-technical": round(c, 3)}}}})
        if i < 28:
            inp.append({"id": str(1000 + i), "state": {"site": "mau.vn", "title": f"Bài số {i}", "headings": ["H2 a", "H2 b"]},
                        "criteria": crit})
    write(t / "out.jsonl", pred)
    write(t / "in.jsonl", inp)
    run("gold-sheet", "--pred", t / "out.jsonl", "--question", "primary", "--n", "20", "--out", t / "trong.txt", "--write")
    assert "title:" not in (t / "trong.txt").read_text(encoding="utf-8")
    p = run("gold-sheet", "--pred", t / "out.jsonl", "--question", "primary", "--content", t / "in.jsonl",
            "--n", "30", "--out", t / "du.txt", "--write")
    sheet = (t / "du.txt").read_text(encoding="utf-8")
    assert "title: Bài số" in sheet and 'headings: ["H2 a", "H2 b"]' in sheet, sheet[:400]
    assert "# LABELS: seo-technical|seo-onpage|unknown" in sheet
    assert "confidence" not in sheet and "probabilities" not in sheet and "0.45" not in sheet
    assert "2 mục không có dòng trong --content" in p.stderr, p.stderr
    # --labels thắng criteria
    run("gold-sheet", "--pred", t / "out.jsonl", "--question", "primary", "--content", t / "in.jsonl",
        "--labels", "a,b", "--n", "10", "--out", t / "lb.txt", "--write")
    assert "# LABELS: a|b" in (t / "lb.txt").read_text(encoding="utf-8")


def main():
    for fn in (test_pipeline_recall, test_holdout_gate, test_gold_sheet_and_merge, test_cosine_gold_join,
               test_gold_sheet_content):
        with tempfile.TemporaryDirectory() as t:
            fn(Path(t))
        print(f"  {fn.__name__}: đạt")
    print("test_gold_pipeline: đạt")


if __name__ == "__main__":
    main()
