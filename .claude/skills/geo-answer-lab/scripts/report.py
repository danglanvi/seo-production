#!/usr/bin/env python3
"""Chỉ số AI answer theo brand × engine và danh sách phản đối của brand chính.

Dùng: python3 -I report.py --dir <thư mục prepare> --brands brands.json --registry <model-calibration.json> [--site <domain>]
Đọc det.jsonl, citations.jsonl, jev_out.jsonl (rubric ai-answer-brand), glm_out.jsonl (tuỳ chọn, trích phản đối).
Cổng confidence: entry của site trong registry → calibration-defaults.json → không có thì dừng (Claude đọc mọi mục).
Nhãn dưới cổng ghi "review", không tính vào tỷ lệ. Ra report.json + report.md.
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUBRIC = "ai-answer-brand"


def find_defaults():
    """tools/ai-assist/calibration-defaults.json của repo SEO Production, tìm ngược từ thư mục chạy và thư mục script."""
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()] if Path(p).exists() else []


def gates(registry, site, version):
    out, src = {}, {}
    for path, want_site, name in ((registry, site, "site"), (find_defaults(), None, "defaults")):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == RUBRIC and e.get("version") == version and (want_site is None or e.get("site") == want_site):
                g = e.get("conf_gate") or e.get("threshold")
                if g and e["question"] not in out:
                    out[e["question"]], src[e["question"]] = g, name
    return out, src


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--brands", required=True, type=Path)
    ap.add_argument("--registry", default=None)
    ap.add_argument("--site", default=None)
    a = ap.parse_args()

    cfg = json.loads(a.brands.read_text(encoding="utf-8"))
    own = cfg["own"]
    det = {r["id"]: r for r in jl(a.dir / "det.jsonl")}
    jev = {r["id"]: r for r in jl(a.dir / "jev_out.jsonl") if "answers" in r}
    glm = {r["id"]: r for r in jl(a.dir / "glm_out.jsonl") if "quotes" in r}
    if not jev:
        sys.exit("thiếu jev_out.jsonl: chạy jev.py với tasks/ai-answer-brand.json trên jev_in.jsonl")
    version = next(iter(jev.values()))["task_version"]
    g, gsrc = gates(a.registry, a.site, version)
    missing = {"role", "proof", "objection"} - set(g)
    if missing:
        sys.exit(f"chưa có cổng cho {sorted(missing)} ở rubric {version}: hiệu chuẩn bằng skill model-calibration trước")

    def label(i, q):
        ans = (jev.get(i) or {}).get("answers", {}).get(q)
        if not ans:
            return "review"
        if "p_yes" in ans:
            p = ans["p_yes"]
            return "yes" if p >= g[q] else ("no" if p <= 1 - g[q] else "review")
        return ans["choice"] if ans["confidence"] >= g[q] else "review"

    agg = defaultdict(Counter)
    for i, d in det.items():
        if d["named_in_question"]:
            continue  # brand là chủ đề câu hỏi: không tính vào tỷ lệ được gợi ý
        for key in ((d["brand"], "all"), (d["brand"], d["engine"])):
            c = agg[key]
            c["pairs"] += 1
            if d["regex_mention"]:
                c["mention"] += 1
                c["first"] += d["mention_order"] == 1
                for q in ("role", "proof", "objection"):
                    c[f"{q}:{label(i, q)}"] += 1
    rows = {}
    for (b, e), c in sorted(agg.items()):
        m = c["mention"] or 1
        rows[f"{b}|{e}"] = {"brand": b, "engine": e, "pairs": c["pairs"],
                            "mention_rate": round(c["mention"] / c["pairs"], 3),
                            "recommended_rate": round(c["role:recommended"] / c["pairs"], 3),
                            "first_of_mentioned": round(c["first"] / m, 3),
                            "third_party_of_mentioned": round(c["proof:third_party"] / m, 3),
                            "objection_of_mentioned": round(c["objection:yes"] / m, 3),
                            "review_items": sum(v for k, v in c.items() if k.endswith(":review"))}
    cites = jl(a.dir / "citations.jsonl")
    own_cited = [c for c in cites if c.get("own_cited")]
    objections = defaultdict(list)
    for i, r in glm.items():
        if det.get(i, {}).get("brand") == own:
            for q in r["quotes"]:
                objections[q["tag"] or "other"].append({"id": i, "text": q["text"]})
    rep = {"rubric_version": version, "gates": g, "gate_source": gsrc, "brands": rows,
           "own": {"brand": own, "answers": len(cites), "answers_citing_own_domain": len(own_cited),
                   "objections_by_tag": {k: len(v) for k, v in objections.items()}, "objections": objections}}
    (a.dir / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    note = ("" if set(gsrc.values()) == {"site"} else
            " Một số cổng lấy từ defaults (đo trên site khác): số liệu là bản nháp tới khi hiệu chuẩn trên 40 mẫu của site này.")
    md = [f"# AI answer: {own}", "", f"Rubric {RUBRIC} {version}. Cổng confidence: " +
          ", ".join(f"{k} {v} ({gsrc[k]})" for k, v in sorted(g.items())) + ". Tỷ lệ chỉ tính prompt không nêu tên brand đó." + note, "",
          "| Brand | Engine | Cặp | Được nhắc | Được gợi ý | Nhắc đầu tiên | Bằng chứng bên thứ ba | Có phản đối | Chờ đọc |",
          "|---|---|---|---|---|---|---|---|---|"]
    pct = lambda x: f"{x * 100:.0f}%"
    for r in rows.values():
        md.append(f"| {r['brand']} | {r['engine']} | {r['pairs']} | {pct(r['mention_rate'])} | {pct(r['recommended_rate'])} | "
                  f"{pct(r['first_of_mentioned'])} | {pct(r['third_party_of_mentioned'])} | {pct(r['objection_of_mentioned'])} | "
                  f"{r['review_items']} |")
    md += ["", f"Câu trả lời trích dẫn domain của {own}: {len(own_cited)}/{len(cites)}.", "", "## Phản đối AI nêu về " + own, ""]
    for tag, items in sorted(objections.items(), key=lambda x: -len(x[1])):
        md.append(f"### {tag} ({len(items)})")
        md += [f"- {x['text'][:300]} `{x['id']}`" for x in items[:40]]
        md.append("")
    (a.dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"report: {len(rows)} dòng brand × engine, {sum(len(v) for v in objections.values())} câu phản đối -> {a.dir}")


if __name__ == "__main__":
    main()
