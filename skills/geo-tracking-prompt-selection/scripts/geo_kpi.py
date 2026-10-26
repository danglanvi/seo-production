#!/usr/bin/env python3
"""Đo KPI GEO từ câu trả lời AI đã thu, và so một lần đo lại với mốc (geo-tracking-prompt-selection).

Lệnh:
  kpi --raw raw.jsonl --det det.jsonl --citations citations.jsonl --prompts prompts.tsv --brands brands.json --out-dir <thư mục>
      raw.jsonl do collect.py của geo-answer-lab thu; det.jsonl, citations.jsonl do prepare.py của geo-answer-lab ra.
      Ra kpi.json (theo engine + từng ô prompt × engine) và by_prompt.tsv.
  compare --base <kpi.json mốc> --new <kpi.json lần đo lại> [--change-date YYYY-MM-DD] --out compare.md
      Chỉ so prompt có ở cả 2 lần đo. Báo đổi model, thiếu lượt chạy, prompt đổi chữ, và chênh nằm trong nhiễu.
  ahrefs --snapshots snapshots.json --own <domain> --out ahrefs.md
      snapshots.json: [{"domain", "date", "country"?, "ai_responses_count": <kết quả site-explorer-ai-responses-count>}].
      Tách citation từ prompt khỏi AIO theo từ khoá, xếp brand chính với đối thủ, in diễn biến theo ngày của brand chính.

Định nghĩa (khớp references/readiness-baseline.md của bản root và mốc pilot 18/10/2026):
- Câu trả lời hợp lệ: ok=true và có chữ. Lượt chạy lại sau cùng thắng.
- Mention rate = câu trả lời nhắc brand chính / câu trả lời hợp lệ của prompt không mang tên brand (branded = no).
- Cited rate = câu trả lời trích domain của brand chính / cùng mẫu số.
- SoV = lượt brand chính / tổng lượt của tập brand cố định. Mỗi câu trả lời đếm mỗi brand tối đa 1 lần.
- Chênh giữa các lượt (run_spread) = chênh lớn nhất của mention rate giữa run 1, 2, 3… trong một lần đo. Chỉ để mô tả.
- compare đọc chênh bằng bootstrap theo prompt, ghép cặp 2 lần đo (2.000 lượt, seed cố định). Khoảng 95% chứa 0 thì
  ghi "trong nhiễu". Thử A/A trên mốc pilot 18/10 (cùng ngày, không có thay đổi thật): run_spread báo sai "tăng/giảm"
  ở 6/9 ô; bootstrap ghi "trong nhiễu" ở 35/36 ô, ô còn lại sát biên (cận trên −0,4 điểm). Vì vậy chỉ kết luận
  tăng hoặc giảm khi 2 mốc liên tiếp cùng chiều.

Python stdlib. Chỉ đọc file local, không gọi mạng.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import random
import sys
from pathlib import Path


def read_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def rate(k, n):
    return round(k / n, 3) if n else None


def cmd_kpi(a):
    prompts = {p["id"]: p for p in csv.DictReader(open(a.prompts, encoding="utf-8"), delimiter="\t")}
    cfg = json.loads(Path(a.brands).read_text(encoding="utf-8"))
    own = cfg["own"]
    raw_all = read_jsonl(a.raw)
    valid = {}
    for r in raw_all:
        if r.get("ok") and r.get("answer"):
            valid[(r["prompt_id"], r["engine"], r["run"])] = r
    tried = {(r["prompt_id"], r["engine"], r["run"]) for r in raw_all}
    failed = collections.Counter(k[1] for k in tried - set(valid))
    det = collections.defaultdict(set)  # (pid, engine, run) -> brand nhắc
    for d in read_jsonl(a.det):
        if d.get("regex_mention"):
            det[(d["prompt_id"], d["engine"], d["run"])].add(d["brand"])
    cites = {(c["prompt_id"], c["engine"], c["run"]): c for c in read_jsonl(a.citations)}

    engines = sorted({k[1] for k in valid}, key=lambda e: ["chatgpt", "gemini", "perplexity"].index(e)
                     if e in ("chatgpt", "gemini", "perplexity") else 9)
    cells = {}
    out = {"own": own, "own_domains": cfg.get("own_domains", []), "brands": sorted(cfg["brands"]), "engines": {},
           "cells": cells, "prompt_hash": {}}
    for pid, p in prompts.items():
        out["prompt_hash"][pid] = hashlib.sha256(p.get("prompt", "").strip().encode()).hexdigest()[:12]
    dates = sorted(r.get("date", "") for r in valid.values() if r.get("date"))
    out["measured"] = {"from": dates[0] if dates else None, "to": dates[-1] if dates else None}

    for e in engines:
        keys = [k for k in valid if k[1] == e]
        nb = [k for k in keys if prompts.get(k[0], {}).get("branded") == "no"]
        bofu = [k for k in nb if prompts[k[0]].get("funnel") == "BOFU"]
        app = collections.Counter(b for k in nb for b in det[k])
        tot = sum(app.values())
        own_cited = lambda k: bool((cites.get(k) or {}).get("own_cited"))
        by_run = {}
        for run in sorted({k[2] for k in nb}):
            ks = [k for k in nb if k[2] == run]
            by_run[str(run)] = rate(sum(own in det[k] for k in ks), len(ks))
        rv = [v for v in by_run.values() if v is not None]
        urls = collections.Counter()
        for k in keys:  # mỗi câu trả lời đếm mỗi URL tối đa 1 lần
            urls.update({(d.get("url") or "").split("?")[0].split("#")[0]
                         for d in (cites.get(k) or {}).get("domains", [])
                         if any(d["domain"] == od or d["domain"].endswith("." + od) for od in cfg.get("own_domains", []))
                         and "vertexaisearch" not in (d.get("url") or "")})
        doms = collections.Counter(d["domain"] for k in nb for d in {x["domain"]: x for x in (cites.get(k) or {}).get("domains", [])}.values())
        out["engines"][e] = {
            "responses": len(keys), "failed": failed.get(e, 0),
            "models_served": dict(collections.Counter(valid[k].get("model_served") or valid[k].get("model") for k in keys)),
            "runs": len(by_run),
            "mention_nonbranded": rate(sum(own in det[k] for k in nb), len(nb)),
            "mention_bofu_nonbranded": rate(sum(own in det[k] for k in bofu), len(bofu)),
            "cited_nonbranded": rate(sum(own_cited(k) for k in nb), len(nb)),
            "sov_nonbranded": rate(app[own], tot),
            "mention_by_run": by_run,
            "run_spread": round(max(rv) - min(rv), 3) if len(rv) > 1 else None,
            "top_brands": app.most_common(6),
            "own_urls": urls.most_common(8),
            "own_urls_note": "Gemini trả link vertexaisearch: chỉ biết domain từ title, không biết URL" if e == "gemini" else "",
            "top_domains": doms.most_common(10),
            "cost": round(sum(valid[k].get("cost") or 0 for k in keys), 3),
        }
        for k in keys:
            c = cells.setdefault(k[0], {}).setdefault(e, {"n": 0, "own_mention": 0, "own_cited": 0, "app": {}})
            c["n"] += 1
            c["own_mention"] += own in det[k]
            c["own_cited"] += own_cited(k)
            for b in det[k]:
                c["app"][b] = c["app"].get(b, 0) + 1
    for pid in cells:
        for c in cells[pid].values():
            c["branded"] = prompts.get(pid, {}).get("branded", "")
            c["funnel"] = prompts.get(pid, {}).get("funnel", "")
    out["cost"] = round(sum(v["cost"] for v in out["engines"].values()), 3)

    od = Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    (od / "kpi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(od / "by_prompt.tsv", "w", encoding="utf-8") as fh:
        cols = ["id", "funnel", "branded", "prompt"] + [f"{e}_{m}" for e in engines for m in ("mention", "cited")]
        fh.write("\t".join(cols) + "\n")
        for pid, p in prompts.items():
            row = [pid, p.get("funnel", ""), p.get("branded", ""), p.get("prompt", "")]
            for e in engines:
                c = cells.get(pid, {}).get(e, {"n": 0, "own_mention": 0, "own_cited": 0})
                row += [f"{c['own_mention']}/{c['n']}", f"{c['own_cited']}/{c['n']}"]
            fh.write("\t".join(row) + "\n")
    pct = lambda x: "—" if x is None else f"{round(x * 100)}%"
    for e, v in out["engines"].items():
        print(f"{e}: nhắc {pct(v['mention_nonbranded'])} (BOFU {pct(v['mention_bofu_nonbranded'])}), "
              f"trích {pct(v['cited_nonbranded'])}, SoV {pct(v['sov_nonbranded'])}, chênh giữa các lượt {pct(v['run_spread'])}, "
              f"{v['responses']} câu trả lời, lỗi {v['failed']}, {v['cost']} USD")


def subset(kpi, pids, e, own):
    """Tính lại mention, cited, SoV của một engine trên tập prompt chung (prompt không mang tên brand)."""
    n = m = c = o = t = 0
    for pid in pids:
        cell = kpi["cells"].get(pid, {}).get(e)
        if not cell or cell.get("branded") != "no":
            continue
        n += cell["n"]
        m += cell["own_mention"]
        c += cell["own_cited"]
        o += cell["app"].get(own, 0)
        t += sum(cell["app"].values())
    return {"n": n, "mention": rate(m, n), "cited": rate(c, n), "sov": rate(o, t)}


def boot_ci(base, new, pids, e, own, key, iters=2000, seed=19):
    """Khoảng 95% của chênh (đo lại − mốc), bootstrap theo prompt, ghép cặp: mỗi lượt rút lại cùng prompt cho cả 2 lần đo."""
    pool = [p for p in pids if (base["cells"].get(p, {}).get(e) or {}).get("branded") == "no"
            and (new["cells"].get(p, {}).get(e) or {}).get("branded") == "no"]
    if len(pool) < 5:
        return None
    rnd, ds = random.Random(seed), []
    for _ in range(iters):
        smp = [rnd.choice(pool) for _ in pool]
        x, y = subset_multi(base, smp, e, own)[key], subset_multi(new, smp, e, own)[key]
        if x is not None and y is not None:
            ds.append(y - x)
    ds.sort()
    return (round(ds[int(0.025 * len(ds))], 3), round(ds[int(0.975 * len(ds)) - 1], 3)) if ds else None


def subset_multi(kpi, pids, e, own):
    """Như subset() nhưng cho phép prompt lặp (mẫu bootstrap)."""
    n = m = c = o = t = 0
    for pid in pids:
        cell = kpi["cells"][pid][e]
        n += cell["n"]
        m += cell["own_mention"]
        c += cell["own_cited"]
        o += cell["app"].get(own, 0)
        t += sum(cell["app"].values())
    return {"mention": rate(m, n), "cited": rate(c, n), "sov": rate(o, t)}


def day_of(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def cmd_compare(a):
    base = json.loads(Path(a.base).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    own = base["own"]
    shared = sorted(set(base["cells"]) & set(new["cells"]))
    changed_text = [p for p in shared if base["prompt_hash"].get(p) != new["prompt_hash"].get(p)]
    shared = [p for p in shared if p not in changed_text]
    only_new = sorted(set(new["cells"]) - set(base["cells"]))
    lines = [f"# So lần đo GEO: {base['measured']['to'] or '?'} → {new['measured']['to'] or '?'}", ""]
    nd, cd = day_of(new["measured"]["to"]), day_of(a.change_date)
    if nd and cd:
        d = (nd - cd).days
        near = min((14, 30, 60), key=lambda x: abs(x - d))
        lines.append(f"Lần đo lại ở ngày +{d} sau đợt sửa {a.change_date} (mốc gần nhất: ngày {near}"
                     + ("" if abs(near - d) <= 3 else ", lệch hơn 3 ngày so với lịch") + ").")
    lines.append(f"So {len(shared)} prompt chung. Prompt mới (cohort riêng, không so): {len(only_new)}. "
                 f"Prompt đổi chữ (bỏ khỏi so): {', '.join(changed_text) or 'không'}.")
    lines += ["", "| Engine | Chỉ số | Mốc | Đo lại | Chênh | Khoảng 95% của chênh | Đọc |", "|---|---|---|---|---|---|---|"]
    flags = []
    for e in [x for x in base["engines"] if x in new["engines"]]:
        b, n = subset(base, shared, e, own), subset(new, shared, e, own)
        mb, mn = base["engines"][e]["models_served"], new["engines"][e]["models_served"]
        if set(mb) != set(mn):
            flags.append(f"{e}: model đổi {sorted(mb)} → {sorted(mn)}. Không đọc chênh là tác dụng của việc sửa.")
        for side, k in (("mốc", base), ("đo lại", new)):
            if k["engines"][e]["runs"] < 3:
                flags.append(f"{e}: {side} chỉ có {k['engines'][e]['runs']} lượt chạy (cần ≥ 3).")
        for name, key in (("Nhắc brand", "mention"), ("Trích domain", "cited"), ("SoV", "sov")):
            x, y = b[key], n[key]
            if x is None or y is None:
                lines.append(f"| {e} | {name} | {x} | {y} | — | — | thiếu dữ liệu |")
                continue
            dlt = round(y - x, 3)
            ci = boot_ci(base, new, shared, e, own, key)
            if ci is None:
                read, cis = "ít hơn 5 prompt, không đọc", "—"
            else:
                read = "trong nhiễu" if ci[0] <= 0 <= ci[1] else ("tăng" if dlt > 0 else "giảm")
                cis = f"{ci[0]:+.0%} đến {ci[1]:+.0%}"
            lines.append(f"| {e} | {name} | {x:.0%} | {y:.0%} | {dlt:+.0%} | {cis} | {read} |")
    moved = []
    for pid in shared:
        for e in new["cells"][pid]:
            cb, cn = base["cells"][pid].get(e), new["cells"][pid].get(e)
            if not cb or not cn or not cb["n"] or not cn["n"]:
                continue
            if abs(cn["own_mention"] / cn["n"] - cb["own_mention"] / cb["n"]) >= 2 / 3 - 1e-9:
                moved.append(f"- {pid} · {e}: {cb['own_mention']}/{cb['n']} → {cn['own_mention']}/{cn['n']}")
    lines += ["", "Cảnh báo:", ""] + ([f"- {f}" for f in flags] or ["- không có"])
    lines += ["", "Prompt đổi từ 2/3 lượt trở lên:", ""] + (moved or ["- không có"])
    lines += ["", "Số là ảnh chụp theo ngày đo, dùng để so xu hướng (directional). Chênh trong nhiễu không phải thay đổi."]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# Nền tảng chạy prompt. google_ai_overviews_keywords là AIO theo từ khoá SERP, đếm riêng.
PROMPT_PLATFORMS = ("chatgpt", "google_ai_overviews", "google_ai_mode", "gemini", "perplexity", "copilot", "grok", "claude")
GOOGLE_AI = ("google_ai_overviews", "google_ai_mode", "gemini")


def cmd_ahrefs(a):
    snaps = json.loads(Path(a.snapshots).read_text(encoding="utf-8"))
    flags, rows = [], {}
    for s in snaps:
        c = s["ai_responses_count"]
        cit = {k: v["citations"] for k, v in c.items()}
        prompt = sum(cit.get(k, 0) for k in PROMPT_PLATFORMS)
        if "google_ai_overviews_keywords" in cit:
            kw = cit["google_ai_overviews_keywords"]
        elif "all_platforms" in cit and all(k in cit for k in PROMPT_PLATFORMS[:6]):
            kw = f"≈{cit['all_platforms'] - prompt}"  # suy ra; gồm cả grok, claude nếu không lấy riêng
        else:
            kw = None
            flags.append(f"{s['domain']} {s['date']}: thiếu nền tảng, không tách được AIO theo từ khoá.")
        rows.setdefault(s["domain"], []).append({"date": s["date"], "country": s.get("country") or "tất cả",
                                                 "prompt": prompt, "kw": kw, "cit": cit})
    countries = {r["country"] for v in rows.values() for r in v}
    if len(countries) > 1:
        flags.append(f"Trộn phạm vi quốc gia {sorted(countries)}: chỉ so dòng cùng phạm vi.")
    latest = {d: max(v, key=lambda r: r["date"]) for d, v in rows.items()}
    total = sum(r["prompt"] for r in latest.values()) or 1
    lines = [f"# Số trích dẫn AI theo Ahrefs (`site-explorer-ai-responses-count`), thương hiệu chính {a.own}", "",
             "Cột \"Từ prompt\" cộng các nền tảng chạy prompt. Cột \"AIO theo từ khoá\" là AI Overviews trên từ khoá SERP, đếm riêng. "
             "`all_platforms` của Ahrefs cộng cả hai, không dùng làm KPI.", "",
             "| Domain | Ngày | Từ prompt | Phần của tập | ChatGPT | Google AI (AIO + AI Mode + Gemini) | Perplexity | Copilot | AIO theo từ khoá |",
             "|---|---|---|---|---|---|---|---|---|"]
    for d, r in sorted(latest.items(), key=lambda x: -x[1]["prompt"]):
        g = sum(r["cit"].get(k, 0) for k in GOOGLE_AI)
        name = f"**{d}**" if d == a.own else d
        lines.append(f"| {name} | {r['date']} | {r['prompt']} | {r['prompt'] / total:.0%} | {r['cit'].get('chatgpt', '—')} | {g} | "
                     f"{r['cit'].get('perplexity', '—')} | {r['cit'].get('copilot', '—')} | {r['kw'] if r['kw'] is not None else '—'} |")
    hist = sorted(rows.get(a.own, []), key=lambda r: r["date"])
    if len(hist) > 1:
        lines += ["", f"## {a.own} theo thời gian", "", "| Nền tảng | " + " | ".join(r["date"] for r in hist) + " |",
                  "|---|" + "---|" * len(hist)]
        keys = [k for k in PROMPT_PLATFORMS if any(k in r["cit"] for r in hist)]
        for k in keys:
            vals = [r["cit"].get(k) for r in hist]
            lines.append(f"| {k} | " + " | ".join("—" if v is None else str(v) for v in vals) + " |")
            if vals[0] == 0 and (vals[-1] or 0) > 0:
                flags.append(f"{k}: từ 0 lên {vals[-1]}. Có thể Ahrefs mới mở rộng kho prompt, chưa chắc là site tăng.")
        lines.append("| Từ prompt | " + " | ".join(str(r["prompt"]) for r in hist) + " |")
        lines.append("| AIO theo từ khoá | " + " | ".join("—" if r["kw"] is None else str(r["kw"]) for r in hist) + " |")
    lines += ["", "Cảnh báo:", ""] + ([f"- {f}" for f in flags] or ["- không có"])
    lines += ["", "Số Ahrefs là ước tính theo kho prompt của Ahrefs, không phải bộ prompt của dự án. Dùng để so xu hướng (directional). "
              "Cần bộ prompt riêng thì đo bằng lệnh `kpi`."]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("kpi")
    for f in ("raw", "det", "citations", "prompts", "brands", "out-dir"):
        k.add_argument("--" + f, required=True)
    c = sub.add_parser("compare")
    c.add_argument("--base", required=True)
    c.add_argument("--new", required=True)
    c.add_argument("--change-date")
    c.add_argument("--out", required=True)
    h = sub.add_parser("ahrefs")
    h.add_argument("--snapshots", required=True)
    h.add_argument("--own", required=True)
    h.add_argument("--out", required=True)
    a = ap.parse_args()
    {"kpi": cmd_kpi, "compare": cmd_compare, "ahrefs": cmd_ahrefs}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
