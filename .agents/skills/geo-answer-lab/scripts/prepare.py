#!/usr/bin/env python3
"""Lớp tất định cho câu trả lời AI: regex brand, vị trí nhắc, brand có trong câu hỏi, domain được trích dẫn.

Dùng: python3 -I prepare.py --raw raw.jsonl --prompts prompts.tsv --brands brands.json --out-dir <thư mục>
brands.json: {"own": "<brand chính>", "own_domains": ["example.com"],
              "brands": {"<tên>": {"regex": "<regex chữ thường>", "aliases": ["..."]}}}
Ra: det.jsonl (một dòng mỗi câu trả lời × brand), jev_in.jsonl (chỉ cặp regex thấy brand: Jev không cần chấm cặp vắng mặt),
citations.jsonl (domain trích dẫn mỗi câu trả lời; link vertexaisearch của Gemini lấy domain từ title).
"""
import argparse
import csv
import json
import re
from pathlib import Path


def domains(citations):
    out = []
    for c in citations or []:
        u, t = (c.get("url") or ""), (c.get("title") or "")
        m = re.search(r"https?://(?:www\.)?([^/?#]+)", u)
        host = m.group(1).lower() if m else ""
        if "vertexaisearch" in host:
            host = t.lower().replace("www.", "").strip()
        if host:
            out.append({"domain": host, "url": u.split("?utm_")[0]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--prompts", required=True, type=Path)
    ap.add_argument("--brands", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--jev-out", type=Path, default=None,
                    help="sau bước Jev: chỉ ghi glm_in.jsonl gồm cặp có objection p_yes > 0,3")
    a = ap.parse_args()

    if a.jev_out:
        p = {r["id"]: r["answers"]["objection"]["p_yes"] for r in map(json.loads, a.jev_out.read_text(encoding="utf-8").splitlines())
             if r.get("answers", {}).get("objection")}
        src = (a.out_dir / "jev_in.jsonl").read_text(encoding="utf-8").splitlines()
        sel = [l for l in src if p.get(json.loads(l)["id"], 1) > 0.3]  # thiếu nhãn Jev thì vẫn gửi GLM để Claude đọc
        (a.out_dir / "glm_in.jsonl").write_text("".join(l + "\n" for l in sel), encoding="utf-8")
        print(f"prepare: {len(sel)}/{len(src)} cặp cần trích phản đối -> {a.out_dir / 'glm_in.jsonl'}")
        return

    cfg = json.loads(a.brands.read_text(encoding="utf-8"))
    pats = {b: re.compile(v["regex"], re.I) for b, v in cfg["brands"].items()}
    prompts = {p["id"]: p for p in csv.DictReader(a.prompts.open(encoding="utf-8"), delimiter="\t")}
    recs = {}
    for l in a.raw.read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        if r.get("ok") and r.get("answer"):
            recs[(r["prompt_id"], r["engine"], r["run"])] = r  # lượt chạy lại sau cùng thắng
    det, jin, cites = [], [], []
    for (pid, eng, run), r in sorted(recs.items()):
        p = prompts.get(pid, {})
        first = {b: m.start() for b, pat in pats.items() if (m := pat.search(r["answer"]))}
        order = {b: i + 1 for i, b in enumerate(sorted(first, key=first.get))}
        doms = domains(r.get("citations"))
        cites.append({"answer_id": f"{pid}|{eng}|{run}", "prompt_id": pid, "engine": eng, "run": run,
                      "domains": doms, "own_cited": any(d["domain"].endswith(tuple(cfg.get("own_domains", []))) for d in doms)
                      if cfg.get("own_domains") else None})
        for b in pats:
            i = f"{pid}|{eng}|{run}|{b}"
            row = {"id": i, "prompt_id": pid, "engine": eng, "run": run, "brand": b,
                   "branded": p.get("branded", ""), "funnel": p.get("funnel", ""), "topic": p.get("topic", ""),
                   "named_in_question": bool(pats[b].search(p.get("prompt", ""))),
                   "regex_mention": b in first, "mention_order": order.get(b), "n_brands": len(first)}
            det.append(row)
            if b in first:
                jin.append({"id": i, "state": {"question": p.get("prompt", ""), "answer": r["answer"], "brand": b,
                                               "aliases": cfg["brands"][b].get("aliases", [])}})
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("det.jsonl", det), ("jev_in.jsonl", jin), ("citations.jsonl", cites)):
        (a.out_dir / name).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    print(f"prepare: {len(recs)} câu trả lời, {len(det)} cặp, {len(jin)} cặp có brand -> {a.out_dir}")


if __name__ == "__main__":
    main()
