#!/usr/bin/env python3
"""Hiệu chuẩn ngưỡng cho Jev và EmbeddingGemma, kiểm chứng proxy với kết quả thật, ghi registry theo site.

Chạy bằng Python có numpy:
  jev    --pred jev_out.jsonl --gold gold.jsonl --question <tên> --positive <nhãn> [--target 0.95]
  cosine --pairs pairs.jsonl [--gold gold.jsonl] [--target 0.95] [--grid LO:HI:STEP]  (mỗi dòng {"id", "cos", "label": 0|1};
         có --gold thì nhãn lấy từ gold.jsonl của gold-merge, cặp không có gold bị bỏ)
  proxy  --data rows.jsonl --metric <trường> --outcome <trường> [--group <trường>] [--control <trường>] [--min-n 20]
  auc    --data rows.jsonl --metric <trường> --label <trường 0/1> --group <trường>   (AUC trong từng nhóm, bootstrap)
  show   --registry <file.json>
  gold-sheet --pred jev_out.jsonl --question <tên> [--content jev_in.jsonl] | --items items.jsonl  [--n 60] [--hard ids.txt]
             [--format todo|html] --out <file> [--write]
         Dựng phiếu gán tay mù: lấy mẫu phân tầng theo dải confidence cộng ca khó, KHÔNG in nhãn hay confidence của model.
  gold-merge --todo <phiếu đã điền> --gold gold.jsonl [--labels a,b] [--write]
         Ghép nhãn tay vào gold.jsonl. Ô trống hoặc "?" là ca mơ hồ, không vào gold.
  pipeline --pred rows.jsonl --gold gold.jsonl --positive <nhãn> --stages jev,glm [--min-recall 0.8]
         Recall và precision đầu-cuối của chuỗi nhiều bước, bảng 2×2 so với gold, kèm bước làm mất mục.
Thêm vào jev/cosine/proxy/auc/pipeline để ghi registry:
  --registry <file.json> --rubric <tên> --version <v> --model <model> --site <domain|*> --industry <ngành> --lang vi --write
Entry có ngưỡng (jev, cosine, pipeline) chỉ có status "ready" khi --holdout <file> đạt: ≥ 40 mẫu mới, không trùng gold hiệu chuẩn,
và ngưỡng giữ được trên đó. Thiếu holdout thì status "draft", threshold null, giá trị đề xuất nằm ở draft_values.
Lệnh ghi dữ liệu (gold-sheet, gold-merge, --write) mặc định chạy thử và chỉ in kế hoạch; thêm --write để ghi.
Gold do người hoặc Claude gán tay, tối thiểu 40 mẫu, có cả ca dương lẫn âm. Không lấy nhãn của chính model làm gold.
"""
import argparse
import html
import json
import os
import random
import re
import sys
import time
from pathlib import Path

import numpy as np


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def wilson_low(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return (c - r) / d


def pick_threshold(scores, ys, target, min_n, grid=None):
    """Ngưỡng thấp nhất mà nhóm từ ngưỡng trở lên đạt precision >= target và cận dưới Wilson >= target - 0,1."""
    rows = []
    for thr in (grid if grid is not None else np.round(np.arange(0.30, 0.991, 0.05), 2)):
        sel = scores >= thr
        n, k = int(sel.sum()), int(ys[sel].sum())
        prec = k / n if n else 0.0
        rows.append({"thr": float(thr), "n": n, "precision": round(prec, 3), "recall": round(k / max(int(ys.sum()), 1), 3),
                     "coverage": round(n / len(ys), 3), "wilson_low": round(wilson_low(k, n), 3)})
    ok = [r for r in rows if r["n"] >= min_n and r["precision"] >= target and r["wilson_low"] >= target - 0.1]
    return rows, (min(ok, key=lambda r: r["thr"]) if ok else None)


def conf_gate(conf, correct, target, min_n):
    """Cổng confidence cho câu hỏi nhiều lớp: mức thấp nhất mà nhãn từ mức đó trở lên đúng >= target
    và cận dưới Wilson >= target - 0,1. Dưới cổng thì Claude đọc."""
    rows = []
    for c in np.round(np.arange(0.50, 0.951, 0.05), 2):
        sel = conf >= c
        n, k = int(sel.sum()), int(correct[sel].sum())
        rows.append({"conf": float(c), "n": n, "accuracy": round(k / n, 3) if n else 0.0,
                     "coverage": round(n / len(conf), 3), "wilson_low": round(wilson_low(k, n), 3)})
    ok = [r for r in rows if r["n"] >= min_n and r["accuracy"] >= target and r["wilson_low"] >= target - 0.1]
    return min(ok, key=lambda r: r["conf"]) if ok else None


def buckets(conf, correct):
    edges = [(0.9, 1.01), (0.8, 0.9), (0.7, 0.8), (0.6, 0.7), (0.5, 0.6), (0.0, 0.5)]
    out = []
    for lo, hi in edges:
        m = (conf >= lo) & (conf < hi)
        n = int(m.sum())
        out.append({"conf": f"{lo:.1f}–{min(hi, 1):.1f}", "n": n,
                    "accuracy": round(float(correct[m].mean()), 3) if n else None})
    return out


def jev_arrays(preds, gold, question, positive):
    """Ghép gold với nhãn Jev: trả ids, confidence, đúng/sai, điểm lớp dương, gold dương."""
    ids = [i for i in gold if i in preds and "answers" in preds[i] and question in preds[i]["answers"]]
    conf, correct, pos_score, ys = [], [], [], []
    for i in ids:
        ans = preds[i]["answers"][question]
        g = gold[i]
        if "p_yes" in ans:
            label = "yes" if ans["p_yes"] >= 0.5 else "no"
            c = max(ans["p_yes"], 1 - ans["p_yes"])
            ps = ans["p_yes"] if positive == "yes" else 1 - ans["p_yes"]
        elif "choice" in ans:
            label, c = ans["choice"], ans.get("confidence") or 0
            ps = (ans.get("probabilities") or {}).get(positive, c if label == positive else 0)
        else:
            sys.exit("câu hỏi score: dùng chế độ proxy với gold dạng số")
        conf.append(c)
        correct.append(label == g)
        pos_score.append(ps)
        ys.append(g == positive)
    return ids, *map(np.asarray, (conf, correct, pos_score, ys))


HOLDOUT_MIN = 40


def holdout_info(tuning_ids, hold_ids, n_pos):
    """Kiểm holdout: mẫu mới, đủ 40, đủ hai lớp. Trùng gold hiệu chuẩn là lỗi của người chạy."""
    overlap = sorted(set(tuning_ids) & set(hold_ids))
    if overlap:
        sys.exit(f"holdout trùng {len(overlap)} id với gold hiệu chuẩn (ví dụ {overlap[:3]}): holdout phải là mẫu mới")
    n = len(hold_ids)
    info = {"n": n, "n_positive": int(n_pos), "passed": False, "reason": None}
    if n < HOLDOUT_MIN:
        info["reason"] = f"holdout chỉ {n} mẫu: cần ≥ {HOLDOUT_MIN}"
    elif n_pos < 5 or n - n_pos < 5:
        info["reason"] = "holdout thiếu lớp dương hoặc âm: cần ≥ 5 mẫu mỗi lớp"
    return info


def holdout_eval(info, sel, hits, a, what):
    """Ngưỡng hoặc cổng phải giữ precision trên holdout theo đúng tiêu chí lúc chọn."""
    n, k = int(sel.sum()), int(hits[sel].sum())
    prec = k / n if n else 0.0
    info.update(n_selected=n, precision=round(prec, 3), wilson_low=round(wilson_low(k, n), 3))
    if n >= a.min_n and prec >= a.target and info["wilson_low"] >= a.target - 0.1:
        info["passed"] = True
    else:
        info["reason"] = (f"{what} không giữ được trên holdout: {n} mục qua, precision {info['precision']}, "
                          f"Wilson {info['wilson_low']}")
    return info


def cmd_jev(a):
    gold = {g["id"]: str(g["label"]) for g in jl(a.gold)}
    preds = {p["id"]: p for p in jl(a.pred)}
    ids, conf, correct, pos_score, ys = jev_arrays(preds, gold, a.question, a.positive)
    missing = len(gold) - len(ids)
    if len(ids) < 20:
        sys.exit(f"chỉ {len(ids)} mẫu có cả gold lẫn nhãn Jev: cần ít nhất 20, nên 40+")
    rows, best = pick_threshold(pos_score, ys.astype(int), a.target, a.min_n)
    res = {"mode": "jev", "question": a.question, "positive": a.positive, "n": int(len(ids)),
           "missing_pred": missing, "n_positive": int(ys.sum()), "accuracy": round(float(correct.mean()), 3),
           "by_confidence": buckets(conf, correct), "thresholds": rows,
           "recommended": best, "target_precision": a.target,
           "conf_gate": conf_gate(conf, correct, a.target, a.min_n),
           "verdict": "dùng ngưỡng" if best else "không ngưỡng nào đạt: Claude đọc mọi mục"}
    if not best and res["conf_gate"]:
        res["verdict"] = f"không có ngưỡng theo lớp; dùng cổng confidence ≥ {res['conf_gate']['conf']}, dưới cổng Claude đọc"
    if a.holdout:
        hg = {g["id"]: str(g["label"]) for g in jl(a.holdout)}
        h_ids, h_conf, h_correct, h_ps, h_ys = jev_arrays(preds, hg, a.question, a.positive)
        info = holdout_info(list(gold), h_ids, h_ys.sum())
        if info["reason"] is None:
            if best:
                holdout_eval(info, h_ps >= best["thr"], h_ys, a, f"ngưỡng {best['thr']}")
            elif res["conf_gate"]:
                holdout_eval(info, h_conf >= res["conf_gate"]["conf"], h_correct, a,
                             f"cổng confidence {res['conf_gate']['conf']}")
            else:
                info["reason"] = "không có ngưỡng hay cổng để kiểm trên holdout"
        res["holdout"] = info
    return res


def cos_with_gold(pairs, gold_path):
    """Gắn nhãn gold (id, label 1|0 từ gold-merge) vào cặp có cos. Dòng gold có sẵn cos thì giữ nguyên."""
    by_id = {str(r["id"]): r for r in pairs}
    out, missing = [], []
    for g in jl(gold_path):
        i = str(g["id"])
        try:
            lbl = int(g["label"])
        except ValueError:
            sys.exit(f"cosine cần nhãn gold 1|0, gặp {g['label']!r} ở id {i}: dựng phiếu với --labels 1,0")
        if "cos" in g:
            out.append(dict(g, label=lbl))
        elif i in by_id:
            out.append(dict(by_id[i], label=lbl))
        else:
            missing.append(i)
    if missing:
        print(f"cảnh báo: {len(missing)} id gold không có trong --pairs (ví dụ {missing[:3]})", file=sys.stderr)
    return out


def cmd_cosine(a):
    pool = jl(a.pairs)
    rows = cos_with_gold(pool, a.gold) if a.gold else pool
    s = np.asarray([r["cos"] for r in rows], dtype=float)
    y = np.asarray([int(r["label"]) for r in rows])
    if y.sum() < 5 or (1 - y).sum() < 5:
        sys.exit("cần ít nhất 5 cặp dương và 5 cặp âm")
    # Cosine dồn trong dải hẹp (cặp cùng site thường 0,85–1): lưới 0,01 thay cho 0,05.
    # --grid LO:HI:STEP cho điểm khác dải, ví dụ margin cosine (-0.10:0.10:0.01).
    if a.grid:
        lo, hi, step = (float(x) for x in a.grid.split(":"))
        grid = np.round(np.arange(lo, hi + step / 2, step), 4)
    else:
        grid = np.round(np.arange(0.50, 0.9951, 0.01), 2)
    thr_rows, accept = pick_threshold(s, y, a.target, a.min_n, grid)
    # Ngưỡng loại: dưới ngưỡng này gần như chắc là âm.
    reject = None
    for thr in (grid[::-1] if a.grid else np.round(np.arange(0.95, 0.09, -0.01), 2)):
        sel = s < thr
        n = int(sel.sum())
        if n >= a.min_n and (1 - y[sel]).mean() >= a.target:
            reject = {"thr": float(thr), "n": n, "npv": round(float((1 - y[sel]).mean()), 3)}
            break
    holdout = None
    if a.holdout:
        hrows = cos_with_gold(pool, a.holdout) if a.gold else jl(a.holdout)
        hs = np.asarray([r["cos"] for r in hrows], dtype=float)
        hy = np.asarray([int(r["label"]) for r in hrows])
        holdout = holdout_info([r["id"] for r in rows], [r["id"] for r in hrows], hy.sum())
        if holdout["reason"] is None:
            if accept:
                holdout_eval(holdout, hs >= accept["thr"], hy, a, f"ngưỡng nhận {accept['thr']}")
            else:
                holdout["reason"] = "không có ngưỡng nhận để kiểm trên holdout"
    return {"mode": "cosine", "holdout": holdout, "n": len(rows), "n_positive": int(y.sum()),
            "max_negative": round(float(s[y == 0].max()), 4), "min_positive": round(float(s[y == 1].min()), 4),
            "median_positive": round(float(np.median(s[y == 1])), 4), "median_negative": round(float(np.median(s[y == 0])), 4),
            "accept": accept, "reject_below": reject, "thresholds": thr_rows, "target_precision": a.target,
            "verdict": ("vùng xám từ {} tới {}: Claude đọc".format(reject["thr"] if reject else "?", accept["thr"] if accept else "?"))}


def rank(x):
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), dtype=float)
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return None
    rx, ry = rank(np.asarray(x, float)), rank(np.asarray(y, float))
    return float(np.corrcoef(rx, ry)[0, 1])


def partial_spearman(x, y, z):
    """Spearman giữa x và y sau khi khử phần tuyến tính theo hạng của z, ví dụ độ dài bài."""
    if len(x) < 4:
        return None
    rx, ry, rz = (rank(np.asarray(v, float)) for v in (x, y, z))
    A = np.vstack([rz, np.ones_like(rz)]).T
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
    ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    if ex.std() < 1e-9 or ey.std() < 1e-9:
        return None
    return float(np.corrcoef(ex, ey)[0, 1])


def cmd_proxy(a):
    need = [a.metric, a.outcome] + ([a.control] if a.control else [])
    rows = [r for r in jl(a.data) if all(r.get(k) is not None for k in need)]
    if len(rows) < a.min_n:
        sys.exit(f"chỉ {len(rows)} dòng có đủ {', '.join(need)}: cần {a.min_n}")
    rng = np.random.default_rng(7)

    def corr(sub):
        x, y = np.asarray([r[a.metric] for r in sub], float), np.asarray([r[a.outcome] for r in sub], float)
        if a.control:
            return partial_spearman(x, y, np.asarray([r[a.control] for r in sub], float))
        return spearman(x, y)

    if a.group:
        groups = {}
        for r in rows:
            groups.setdefault(r[a.group], []).append(r)
        gs = [g for g in groups.values() if len(g) >= 3]

        def stat(sample):
            vals = [corr(g) for g in sample]
            vals = [v for v in vals if v is not None]
            return float(np.mean(vals)) if vals else None

        point = stat(gs)
        boots = [stat([gs[i] for i in rng.integers(0, len(gs), len(gs))]) for _ in range(1000)]
        unit = f"{len(gs)} nhóm ({a.group})"
    else:
        point = corr(rows)
        boots = [corr([rows[i] for i in rng.integers(0, len(rows), len(rows))]) for _ in range(1000)]
        unit = f"{len(rows)} dòng"
    if a.control:
        unit += f", khử {a.control}"
    boots = [b for b in boots if b is not None]
    if point is None or not boots:
        sys.exit("không tính được tương quan: metric hoặc outcome không đổi")
    lo, hi = np.percentile(boots, [2.5, 97.5])
    verdict = ("dùng được (tương quan dương, CI không chứa 0)" if lo > 0 else
               "ngược chiều: kiểm lại định nghĩa" if hi < 0 else "chưa chứng minh: không đưa vào báo cáo khách")
    return {"mode": "proxy", "metric": a.metric, "outcome": a.outcome, "control": a.control, "unit": unit,
            "n_rows": len(rows),
            "spearman": round(point, 3), "ci95": [round(float(lo), 3), round(float(hi), 3)], "verdict": verdict}


def auc(pos, neg):
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def cmd_auc(a):
    """AUC trong từng nhóm (ví dụ cùng một pool kết quả tìm kiếm): mục có nhãn dương có điểm cao hơn mục âm không."""
    need = [a.metric, a.label, a.group]
    rows = [r for r in jl(a.data) if all(r.get(k) is not None for k in need)]
    groups = {}
    for r in rows:
        groups.setdefault(r[a.group], []).append(r)
    vals = []
    for g in groups.values():
        v = auc([float(r[a.metric]) for r in g if r[a.label]], [float(r[a.metric]) for r in g if not r[a.label]])
        if v is not None:
            vals.append(v)
    if len(vals) < 5:
        sys.exit(f"chỉ {len(vals)} nhóm có cả mục dương và âm: cần ít nhất 5")
    vals = np.asarray(vals)
    rng = np.random.default_rng(7)
    boots = [float(vals[rng.integers(0, len(vals), len(vals))].mean()) for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    verdict = ("dùng được (CI trên 0,5)" if lo > 0.5 else "ngược chiều (CI dưới 0,5): kiểm cách chọn mẫu" if hi < 0.5
               else "chưa chứng minh (CI chứa 0,5): không đưa vào báo cáo khách")
    return {"mode": "auc", "metric": a.metric, "outcome": a.label, "unit": f"{len(vals)} nhóm ({a.group})",
            "n_rows": len(rows), "auc": round(float(vals.mean()), 3), "ci95": [round(float(lo), 3), round(float(hi), 3)],
            "share_auc_gt_05": round(float((vals > 0.5).mean()), 3), "verdict": verdict}


BANDS = [(0.9, 1.01, "0.9-1.0"), (0.8, 0.9, "0.8-0.9"), (0.7, 0.8, "0.7-0.8"), (0.6, 0.7, "0.6-0.7"),
         (0.5, 0.6, "0.5-0.6"), (0.0, 0.5, "<0.5")]
CONTENT_FIELDS = ("text", "url", "title", "path", "image")


def answer_conf(ans):
    """Confidence của một câu trả lời Jev; None nếu là câu hỏi score."""
    if "p_yes" in ans:
        return max(ans["p_yes"], 1 - ans["p_yes"])
    if "choice" in ans:
        return ans.get("confidence") or 0
    return None


def band_of(c):
    for lo, hi, name in BANDS:
        if lo <= c < hi:
            return name
    return BANDS[-1][2]


def read_ids(path):
    """Danh sách id: mỗi dòng một id, hoặc jsonl có trường id."""
    out = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.add(str(json.loads(line)["id"]) if line.startswith("{") else line)
    return out


def stratified_pick(items, n, hard_share, rng):
    """Ca khó lấy trước (tối đa hard_share của n), phần còn lại chia đều các dải confidence theo vòng."""
    items = sorted(items, key=lambda x: x["id"])
    hard = [x for x in items if x["hard"]]
    rng.shuffle(hard)
    chosen = [(x, "hard") for x in hard[:int(n * hard_share)]]
    taken = {x["id"] for x, _ in chosen}
    pools = {}
    for x in items:
        if x["id"] not in taken:
            pools.setdefault(x["band"], []).append(x)
    for v in pools.values():
        rng.shuffle(v)
    order = [b for _, _, b in BANDS if b in pools] + [b for b in pools if b not in {c for _, _, c in BANDS}]
    while len(chosen) < n and any(pools.values()):
        for b in order:
            if pools[b] and len(chosen) < n:
                chosen.append((pools[b].pop(), b))
    rng.shuffle(chosen)  # thứ tự trộn để dải confidence không lộ qua vị trí
    return chosen


def row_body(row, field):
    """Nội dung hiện trong phiếu: --field, rồi trường nội dung thường gặp, rồi state của đầu vào Jev."""
    if field:
        v = row.get(field)
    else:
        v = next((row[f] for f in CONTENT_FIELDS if row.get(f)), None)
        if v is None and isinstance(row.get("state"), dict):
            return "\n".join(f"{k}: {s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)}"
                             for k, s in row["state"].items())
        if v is None:
            v = row.get("state")
    return "" if v is None else str(v)


def todo_text(chosen, field, labels):
    lines = ["# Phiếu gán gold. Điền nhãn sau \"LABEL:\". Để trống nếu ca mơ hồ.",
             "# Gán xong trước khi xem nhãn model."]
    if labels:
        lines.append("# LABELS: " + "|".join(labels))
    for x, _ in chosen:
        lines += ["", f"### id: {x['id']}"]
        body = row_body(x["row"], field)
        lines += ["  " + ln for ln in (body.splitlines() or [""])]
        lines.append("LABEL:")
    return "\n".join(lines) + "\n"


def contact_html(chosen, image_field, labels):
    cards = []
    for k, (x, _) in enumerate(chosen, 1):
        img = x["row"].get(image_field)
        cards.append(f'<figure><img src="{html.escape(str(img))}" loading="lazy" alt="">'
                     f'<figcaption>#{k} · {html.escape(x["id"])}</figcaption></figure>')
    note = ("Nhãn: " + " / ".join(labels) + ". ") if labels else ""
    return ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Phiếu gán gold</title>'
            '<style>body{font:14px system-ui;margin:16px}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}'
            'figure{margin:0}img{width:100%;border:1px solid #ccc}</style></head><body>'
            f'<h1>Phiếu gán gold</h1><p>{note}Điền nhãn vào file todo cùng tên, theo id. Không xem nhãn model.</p>'
            f'<div class="g">{"".join(cards)}</div></body></html>')


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def cmd_gold_sheet(a):
    if bool(a.pred) == bool(a.items):
        sys.exit("chọn đúng một trong --pred (kèm --question) hoặc --items")
    if a.pred and not a.question:
        sys.exit("--pred cần --question để chia dải confidence")
    if a.format == "html" and not a.out:
        sys.exit("--format html cần --out")
    hard_ids = read_ids(a.hard) if a.hard else set()
    skip_ids = {str(g["id"]) for g in jl(a.exclude_gold)} if a.exclude_gold else set()
    # Đầu ra jev.py không mang nội dung: --content (đầu vào Jev, có state) ghép nội dung theo id.
    content = {str(r["id"]): r for r in jl(a.content)} if a.content else {}
    items, no_answer, no_content = [], 0, 0
    for r in jl(a.pred or a.items):
        rid = str(r["id"])
        if rid in skip_ids:
            continue
        if content:
            no_content += rid not in content
            r = {**content.get(rid, {}), **r}
        band = "all"
        if a.pred:
            ans = (r.get("answers") or {}).get(a.question)
            c = answer_conf(ans) if ans else None
            if c is None:
                no_answer += 1
                continue
            band = band_of(c)
        items.append({"id": rid, "row": r, "band": band, "hard": bool(r.get("hard")) or rid in hard_ids})
    if len({x["id"] for x in items}) != len(items):
        sys.exit("id trùng trong nguồn mẫu")
    if not items:
        sys.exit("không còn mẫu nào để lấy")
    chosen = stratified_pick(items, a.n, a.hard_share, random.Random(a.seed))
    labels = [x for x in (a.labels or "").split(",") if x]
    if not labels and a.question:
        crit = next((r["criteria"].get(a.question) for r in content.values() if isinstance(r.get("criteria"), dict)), None)
        labels = list(crit) if isinstance(crit, dict) else []
    if no_content:
        print(f"cảnh báo: {no_content} mục không có dòng trong --content, phiếu để trống nội dung", file=sys.stderr)
    if a.format == "html":
        missing = [x["id"] for x, _ in chosen if not x["row"].get(a.image_field)]
        if missing:
            sys.exit(f"{len(missing)} mẫu thiếu trường {a.image_field} (ví dụ {missing[:3]})")
    strata = {}
    for _, b in chosen:
        strata[b] = strata.get(b, 0) + 1
    out_todo = Path(a.out) if a.format == "todo" and a.out else (Path(a.out).with_suffix(".todo.txt") if a.out else None)
    res = {"mode": "gold-sheet", "dry_run": not a.write, "requested": a.n, "selected": len(chosen),
           "by_stratum": dict(sorted(strata.items())), "skipped_no_answer": no_answer,
           "out": str(a.out) if a.out else None, "todo": str(out_todo) if out_todo else None,
           "verdict": "đã ghi phiếu" if a.write else "chạy thử: thêm --write và --out để ghi phiếu"}
    if len(chosen) < a.n:
        print(f"cảnh báo: chỉ có {len(chosen)} mẫu, ít hơn {a.n} yêu cầu", file=sys.stderr)
    if a.write:
        if not a.out:
            sys.exit("--write cần --out")
        atomic_write(out_todo, todo_text(chosen, a.field, labels))
        if a.format == "html":
            atomic_write(a.out, contact_html(chosen, a.image_field, labels))
    return res


def parse_todo(text):
    labels, blocks, cur = None, [], None
    for line in text.splitlines():
        m = re.match(r"# LABELS:\s*(.+)$", line)
        if m:
            labels = [x.strip() for x in m.group(1).split("|") if x.strip()]
        m = re.match(r"### id:\s*(.+?)\s*$", line)
        if m:
            cur = {"id": m.group(1), "label": ""}
            blocks.append(cur)
        elif line.startswith("LABEL:") and cur is not None:
            cur["label"] = line[len("LABEL:"):].strip()
    return labels, blocks


def cmd_gold_merge(a):
    labels, blocks = parse_todo(Path(a.todo).read_text(encoding="utf-8"))
    if not blocks:
        sys.exit("phiếu không có khối '### id:'")
    ids = [b["id"] for b in blocks]
    if len(set(ids)) != len(ids):
        sys.exit("id trùng trong phiếu")
    allowed = [x for x in a.labels.split(",") if x] if a.labels else labels
    if allowed:
        bad = [b for b in blocks if b["label"] and b["label"] != "?" and b["label"] not in allowed]
        if bad:
            sys.exit(f"{len(bad)} nhãn ngoài danh sách {allowed} (ví dụ id {bad[0]['id']}: {bad[0]['label']!r})")
    path = Path(a.gold)
    gold = {str(g["id"]): g for g in jl(path)} if path.exists() else {}
    added, same, ambiguous, conflicts = [], [], [], []
    for b in blocks:
        if b["label"] in ("", "?"):
            ambiguous.append(b["id"])
        elif b["id"] not in gold:
            added.append(b)
        elif str(gold[b["id"]]["label"]) == b["label"]:
            same.append(b["id"])
        else:
            conflicts.append(b["id"])
    if conflicts and not (a.overwrite and a.reason):
        sys.exit(f"{len(conflicts)} id đã có gold với nhãn khác (ví dụ {conflicts[:3]}): "
                 "sửa gold cần --overwrite và --reason, ghi lý do sau khi đọc ca lệch")
    for b in blocks:
        if b["id"] in conflicts:
            gold[b["id"]] = {"id": b["id"], "label": b["label"], "note": a.reason}
    for b in added:
        gold[b["id"]] = {"id": b["id"], "label": b["label"]}
    counts = {}
    for g in gold.values():
        counts[str(g["label"])] = counts.get(str(g["label"]), 0) + 1
    warn = []
    if len(gold) < HOLDOUT_MIN:
        warn.append(f"gold mới có {len(gold)} mẫu: cần ≥ {HOLDOUT_MIN}")
    if len(counts) < 2 or min(counts.values()) < 5:
        warn.append("gold chưa đủ hai lớp, mỗi lớp ≥ 5 mẫu")
    res = {"mode": "gold-merge", "dry_run": not a.write, "added": len(added), "unchanged": len(same),
           "overwritten": len(conflicts), "ambiguous": len(ambiguous), "ambiguous_ids": ambiguous,
           "total": len(gold), "by_label": dict(sorted(counts.items())), "warnings": warn,
           "gold": str(path), "verdict": f"ghi {len(added) + len(conflicts)} dòng vào gold" if a.write
           else "chạy thử: thêm --write để ghi gold"}
    if a.write:
        atomic_write(path, "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in gold.values()))
    return res


def pipeline_stats(rows, gold, stages, positive, target, min_recall):
    """Bảng 2×2 đầu-cuối. Mục được bắt khi mọi bước đều giữ lại. Mục gold không có trong rows tính là chưa bắt."""
    preds = {str(r["id"]): r for r in rows}
    tp = fn = fp = tn = absent = 0
    lost, stage_hit = {s: 0 for s in stages}, {s: 0 for s in stages}
    for i, g in gold.items():
        r = preds.get(i)
        if r is None:
            absent += 1
        vals = [bool(r and r.get(s)) for s in stages]
        caught = all(vals)
        if g == positive:
            for s, v in zip(stages, vals):
                stage_hit[s] += v
            if caught:
                tp += 1
            else:
                fn += 1
                lost[stages[vals.index(False)]] += 1
        elif caught:
            fp += 1
        else:
            tn += 1
    n_pos = tp + fn
    recall = tp / n_pos if n_pos else None
    prec = tp / (tp + fp) if tp + fp else None
    st = {"n": len(gold), "n_positive": n_pos, "table": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
          "recall": round(recall, 3) if recall is not None else None,
          "recall_wilson_low": round(wilson_low(tp, n_pos), 3),
          "precision": round(prec, 3) if prec is not None else None,
          "precision_wilson_low": round(wilson_low(tp, tp + fp), 3),
          "missed_by_stage": lost,
          "stage_recall": {s: round(stage_hit[s] / n_pos, 3) if n_pos else None for s in stages},
          "absent_in_pred": absent}
    st["report_line"] = (f"recall {st['recall']} ({tp}/{n_pos} mục có thật được bắt, sót {fn}) · "
                         f"precision {st['precision']} ({tp}/{tp + fp} mục báo là đúng)")
    if recall is None or recall < min_recall:
        st["verdict"] = (f"recall thấp ({st['recall']}): chuỗi sót {fn}/{n_pos} mục có thật; "
                         "báo độ sót cạnh độ đúng, không giao như đã lọc xong")
    elif prec is not None and prec < target:
        st["verdict"] = f"precision thấp ({st['precision']} < {target}): Claude đọc mục chuỗi báo"
    else:
        st["verdict"] = f"đạt: recall ≥ {min_recall}, precision ≥ {target}"
    return st


def cmd_pipeline(a):
    stages = [x.strip() for x in a.stages.split(",") if x.strip()]
    if len(stages) < 2 or len(set(stages)) != len(stages):
        sys.exit("--stages cần ít nhất 2 tên bước khác nhau, ví dụ jev,glm")
    gold = {str(g["id"]): str(g["label"]) for g in jl(a.gold)}
    rows = jl(a.pred)
    n_pos = sum(v == a.positive for v in gold.values())
    if len(gold) < 20 or n_pos < 5 or len(gold) - n_pos < 5:
        sys.exit(f"gold có {len(gold)} mẫu, {n_pos} dương: cần ≥ 20 mẫu và ≥ 5 mẫu mỗi lớp")
    res = {"mode": "pipeline", "question": ">".join(stages), "positive": a.positive, "stages": stages}
    res.update(pipeline_stats(rows, gold, stages, a.positive, a.target, a.min_recall))
    res["unit"] = f"chuỗi {'>'.join(stages)}"
    if a.holdout:
        hg = {str(g["id"]): str(g["label"]) for g in jl(a.holdout)}
        info = holdout_info(list(gold), list(hg), sum(v == a.positive for v in hg.values()))
        if info["reason"] is None:
            h = pipeline_stats(rows, hg, stages, a.positive, a.target, a.min_recall)
            info.update(recall=h["recall"], precision=h["precision"], table=h["table"])
            if h["verdict"].startswith("đạt"):
                info["passed"] = True
            else:
                info["reason"] = "chuỗi không giữ được trên holdout: " + h["verdict"]
        res["holdout"] = info
    return res


def write_registry(a, res):
    path = Path(a.registry)
    reg = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"entries": []}
    best = res.get("recommended") or res.get("accept") or {}
    gate = {"threshold": best.get("thr"), "conf_gate": (res.get("conf_gate") or {}).get("conf"),
            "reject_below": (res.get("reject_below") or {}).get("thr")}
    holdout = res.get("holdout")
    # Entry có ngưỡng hoặc cổng lọc chỉ "ready" khi holdout mù, mới và đạt. Proxy/auc đã có CI theo nhóm.
    gated = res["mode"] in ("jev", "cosine", "pipeline")
    ready = (not gated) or bool(holdout and holdout["passed"])
    draft_reason = None
    if not ready:
        draft_reason = (holdout or {}).get("reason") or "thiếu --holdout: cần ≥ 40 mẫu mù mới, không trùng gold hiệu chuẩn"
    entry = {"rubric": a.rubric, "version": a.version, "model": a.model, "site": a.site, "industry": a.industry,
             "lang": a.lang, "question": getattr(a, "question", None) or res.get("question"),
             "positive": getattr(a, "positive", None),
             "mode": res["mode"], "status": "ready" if ready else "draft",
             **(gate if ready else {k: None for k in gate}),
             "draft_values": None if ready else {k: v for k, v in gate.items() if v is not None},
             "draft_reason": draft_reason, "holdout": holdout,
             "metric": res.get("metric"), "outcome": res.get("outcome"), "group": getattr(a, "group", None),
             "control": res.get("control"), "unit": res.get("unit"),
             "date": time.strftime("%Y-%m-%d"), "n": res.get("n") or res.get("n_rows"),
             "precision": best.get("precision", res.get("precision")), "coverage": best.get("coverage"),
             "recall": res.get("recall"),
             "spearman": res.get("spearman"), "auc": res.get("auc"), "ci95": res.get("ci95"),
             "verdict": res["verdict"], "evidence": a.evidence or ""}
    key = ("rubric", "version", "model", "site", "question", "positive", "mode", "metric", "outcome", "group",
           "control")
    reg["entries"] = [e for e in reg["entries"] if tuple(e.get(k) for k in key) != tuple(entry.get(k) for k in key)]
    reg["entries"].append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"registry: ghi {a.rubric} {a.version} cho {a.site} -> {path} (status {entry['status']})", file=sys.stderr)
    if draft_reason:
        print(f"registry: draft, threshold null: {draft_reason}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jev")
    j.add_argument("--pred", required=True)
    j.add_argument("--gold", required=True)
    j.add_argument("--question", required=True)
    j.add_argument("--positive", required=True)
    j.add_argument("--holdout", default=None, help="gold mù ≥ 40 mẫu mới, cùng file --pred, không trùng --gold")
    c = sub.add_parser("cosine")
    c.add_argument("--pairs", required=True)
    c.add_argument("--grid", default=None, help="LO:HI:STEP cho điểm ngoài dải 0,50–0,995, ví dụ margin")
    c.add_argument("--gold", default=None, help="gold.jsonl từ gold-merge (id, label 1|0); nhãn lấy từ đây, cặp không có gold bị bỏ")
    c.add_argument("--holdout", default=None, help="file cặp mới (id, cos, label) ≥ 40 mẫu, không trùng --pairs; "
                   "có --gold thì holdout là gold (id, label), cos lấy từ --pairs")
    p = sub.add_parser("proxy")
    p.add_argument("--data", required=True)
    p.add_argument("--metric", required=True)
    p.add_argument("--outcome", required=True)
    p.add_argument("--group", default=None)
    p.add_argument("--control", default=None, help="trường cần khử, ví dụ log số chữ của bài")
    u = sub.add_parser("auc")
    u.add_argument("--data", required=True)
    u.add_argument("--metric", required=True)
    u.add_argument("--label", required=True, help="trường nhãn 0/1, ví dụ cited")
    u.add_argument("--group", required=True, help="trường nhóm, ví dụ id của pool truy vấn")
    pl = sub.add_parser("pipeline", help="recall và precision đầu-cuối của chuỗi nhiều bước")
    pl.add_argument("--pred", required=True, help="jsonl: {id, <bước>: true|false}; bước vắng hoặc false là không giữ mục")
    pl.add_argument("--gold", required=True)
    pl.add_argument("--positive", required=True, help="nhãn gold của mục chuỗi phải bắt")
    pl.add_argument("--stages", required=True, help="tên các bước theo thứ tự, ví dụ jev,glm")
    pl.add_argument("--min-recall", type=float, default=0.8)
    pl.add_argument("--holdout", default=None, help="gold mù ≥ 40 mẫu mới, cùng file --pred, không trùng --gold")
    gs = sub.add_parser("gold-sheet", help="dựng phiếu gán gold mù: mẫu phân tầng, không in nhãn model")
    gs.add_argument("--pred", default=None, help="đầu ra Jev (jsonl); kèm --question")
    gs.add_argument("--items", default=None, help="danh sách mục (jsonl có id), khi chưa có đầu ra model")
    gs.add_argument("--question", default=None)
    gs.add_argument("--content", default=None, help="đầu vào Jev (jsonl có id, state): ghép nội dung theo id; "
                    "không có --labels thì lấy nhãn từ criteria của câu hỏi")
    gs.add_argument("--n", type=int, default=60)
    gs.add_argument("--seed", type=int, default=7)
    gs.add_argument("--hard", default=None, help="file id ca khó (mỗi dòng một id); mục có \"hard\": true cũng tính")
    gs.add_argument("--hard-share", type=float, default=0.25, help="tối đa phần mẫu dành cho ca khó")
    gs.add_argument("--exclude-gold", default=None, help="gold.jsonl hiện có: bỏ các id đã gán")
    gs.add_argument("--format", choices=("todo", "html"), default="todo", help="todo: văn bản; html: contact sheet ảnh + todo cạnh")
    gs.add_argument("--field", default=None, help="trường nội dung hiện trong phiếu (mặc định text/url/title/path/image)")
    gs.add_argument("--image-field", default="image")
    gs.add_argument("--labels", default=None, help="các nhãn hợp lệ, ngăn bằng dấu phẩy; ghi vào đầu phiếu")
    gs.add_argument("--out", default=None)
    gs.add_argument("--write", action="store_true", help="ghi phiếu; mặc định chỉ chạy thử")
    gm = sub.add_parser("gold-merge", help="ghép nhãn tay từ phiếu vào gold.jsonl")
    gm.add_argument("--todo", required=True)
    gm.add_argument("--gold", required=True)
    gm.add_argument("--labels", default=None, help="nhãn hợp lệ; mặc định lấy từ dòng # LABELS: của phiếu")
    gm.add_argument("--overwrite", action="store_true", help="cho sửa nhãn gold đã có; bắt buộc kèm --reason")
    gm.add_argument("--reason", default=None, help="lý do sửa gold sau khi đọc ca lệch")
    gm.add_argument("--write", action="store_true", help="ghi gold; mặc định chỉ chạy thử")
    s = sub.add_parser("show")
    s.add_argument("--registry", required=True)
    for x in (j, c, p, u, pl):
        x.add_argument("--target", type=float, default=0.95)
        x.add_argument("--min-n", type=int, default=10)
        x.add_argument("--out", type=Path, default=None)
        x.add_argument("--registry", default=None)
        x.add_argument("--write", action="store_true")
        for k in ("rubric", "version", "model", "site", "industry", "lang", "evidence"):
            x.add_argument(f"--{k}", default=None)
    a = ap.parse_args()
    if a.cmd == "show":
        reg = json.loads(Path(a.registry).read_text(encoding="utf-8"))
        for e in reg["entries"]:
            what = e.get("question") or (f"{e['metric']}→{e.get('outcome')}" if e.get("metric") else "")
            what += f" |{e['control']}" if e.get("control") else ""
            print(f"{e['site']:<16} {e['rubric']:<24} {what:<22} {e.get('status', 'ready'):<6} thr={e.get('threshold')} "
                  f"gate={e.get('conf_gate')} rho={e.get('spearman')} auc={e.get('auc')} recall={e.get('recall')} "
                  f"n={e.get('n')} {e['date']} | {e['verdict']}")
        return 0
    if a.cmd in ("gold-sheet", "gold-merge"):
        res = {"gold-sheet": cmd_gold_sheet, "gold-merge": cmd_gold_merge}[a.cmd](a)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if a.cmd == "proxy" and a.min_n == 10:
        a.min_n = 20
    res = {"jev": cmd_jev, "cosine": cmd_cosine, "proxy": cmd_proxy, "auc": cmd_auc,
           "pipeline": cmd_pipeline}[a.cmd](a)
    text = json.dumps(res, ensure_ascii=False, indent=1)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
    print(text if not a.out else f"{a.cmd}: {res['verdict']} -> {a.out}")
    if a.write:
        missing = [k for k in ("registry", "rubric", "version", "model", "site") if not getattr(a, k)]
        if missing:
            sys.exit(f"thiếu {missing} để ghi registry")
        write_registry(a, res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
