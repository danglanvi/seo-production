#!/usr/bin/env python3
"""Phân loại diff chữ của snapshot SEO: đáng kể hay vô hại. Code chốt ca rõ, Jev chấm phần còn lại, Claude đọc vùng xám.

Lệnh (Python 3.9+, chỉ stdlib):
  diffs   --old A.jsonl --new B.jsonl [--fields title,meta,h1] --out diffs.jsonl
          Mỗi dòng snapshot {"url", "title", "meta", "h1"}; h1 dạng chuỗi hoặc danh sách.
  from-drift --json compare.json --out diffs.jsonl
          Đọc output `drift_tracker.py --json compare` (nếu có), lấy title, description, h1.
  prepare --diffs diffs.jsonl --out-dir DIR
          Ra code.jsonl (ca code chốt) và jev_in.jsonl (ca gửi Jev, chỉ chữ công khai của trang).
  report  --diffs diffs.jsonl --out-dir DIR [--jev-out jev_out.jsonl] [--registry model-calibration.json --site <domain>]
          Ra diff_impact.tsv, diff_impact.jsonl, report.md.
Luật code: chữ giống nhau sau chuẩn hoá (NFC, khoảng trắng, hoa thường, dấu câu) là vô hại; số đổi, rỗng ↔ có chữ là đáng kể.
Cổng Jev đọc từ registry rubric "diff-impact", rồi tools/ai-assist/calibration-defaults.json; không có cổng thì Claude đọc mọi ca Jev.
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

RUBRIC = "diff-impact"
TASK = Path(__file__).resolve().parents[1] / "tasks" / "diff-impact.json"
ELEMENT_MAP = {"description": "meta"}
MAX_CHARS = 3000


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def as_text(v):
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("text", v.get("value", ""))
    if isinstance(v, list):
        return " | ".join(as_text(x) or "" for x in v)
    return str(v)


def clean(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", (s or "").replace("\xa0", " "))).strip()


def loose(s):
    """Bỏ hoa thường, dấu câu và dấu phân cách hàng nghìn; giữ chữ có dấu tiếng Việt và số."""
    s = re.sub(r"(?<=\d)[.,](?=\d)", "", clean(s).casefold())
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def numbers(s):
    return sorted(re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*", clean(s)))


def diff_id(url, element, old, new):
    h = hashlib.sha1(f"{url}\n{element}\n{old}\n{new}".encode("utf-8")).hexdigest()[:10]
    return f"{element}|{url}|{h}"


def code_rule(old, new):
    """Trả (nhãn, lý do) khi code chốt được, ngược lại (None, None)."""
    o, n = clean(old), clean(new)
    if o == n:
        return "vô hại", "chỉ khác khoảng trắng hoặc Unicode"
    if not o or not n:
        return "đáng kể", "rỗng ↔ có chữ"
    if loose(o) == loose(n):
        return "vô hại", "chỉ khác hoa thường hoặc dấu câu"
    if numbers(o) != numbers(n):
        return "đáng kể", "số đổi"
    return None, None


def cmd_diffs(a):
    fields = [f.strip() for f in a.fields.split(",") if f.strip()]
    old = {r["url"]: r for r in jl(a.old)}
    rows = []
    for r in jl(a.new):
        u = r.get("url")
        if u not in old:
            continue
        for f in fields:
            va, vb = as_text(old[u].get(f)), as_text(r.get(f))
            if va is None or vb is None or va == vb:
                continue
            rows.append({"id": diff_id(u, f, va, vb), "url": u, "element": f, "old": va, "new": vb})
    write(a.out, rows)
    print(f"{len(rows)} diff -> {a.out}", file=sys.stderr)
    return 0


def cmd_from_drift(a):
    res = json.loads(Path(a.json).read_text(encoding="utf-8"))
    rows = []
    for f in res.get("findings", []):
        el = ELEMENT_MAP.get(f.get("element"), f.get("element"))
        if el not in ("title", "meta", "h1"):
            continue
        va, vb = as_text(f.get("before")), as_text(f.get("after"))
        rows.append({"id": diff_id(f["url"], el, va, vb), "url": f["url"], "element": el, "old": va, "new": vb})
    write(a.out, rows)
    print(f"{len(rows)} diff chữ -> {a.out}", file=sys.stderr)
    return 0


def cmd_prepare(a):
    out = Path(a.out_dir)
    code, jev = [], []
    for d in jl(a.diffs):
        lab, why = code_rule(d["old"], d["new"])
        if lab:
            code.append({"id": d["id"], "label": lab, "why": why})
        else:
            jev.append({"id": d["id"], "state": {"url": d["url"], "element": d["element"],
                                                 "old": clean(d["old"])[:MAX_CHARS], "new": clean(d["new"])[:MAX_CHARS]}})
    write(out / "code.jsonl", code)
    write(out / "jev_in.jsonl", jev)
    print(f"code chốt {len(code)}, gửi Jev {len(jev)} -> {out}", file=sys.stderr)
    return 0


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def load_gates(registry, site, version):
    """Ngưỡng của câu hỏi `significant`: p_yes cho yes, 1 − p_yes cho no. Không dùng cổng confidence gộp 2 lớp:
    hiệu chuẩn 19/10 có 7/8 ca "vô hại" đúng ở p ≤ 0,3, chưa đủ để tự chốt."""
    for path, want_site, src in ((registry, site, "site"), (find_defaults(), None, "defaults")):
        if not path or not Path(path).exists():
            continue
        g = {}
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") != RUBRIC or e.get("version") != version or e.get("mode") != "jev" \
                    or e.get("question") != "significant" or (want_site and e.get("site") != want_site):
                continue
            if e.get("threshold") is not None:
                g[e.get("positive")] = e["threshold"]
        if g:
            return g, src
    return {}, None


def decide(p_yes, gates):
    if p_yes is None:
        return "Claude đọc", "Jev lỗi hoặc chưa chạy"
    if "yes" in gates and p_yes >= gates["yes"]:
        return "đáng kể", f"Jev p={p_yes:.2f} ≥ {gates['yes']}"
    if "no" in gates and 1 - p_yes >= gates["no"]:
        return "vô hại", f"Jev p={p_yes:.2f}, 1 − p ≥ {gates['no']}"
    return "Claude đọc", f"Jev p={p_yes:.2f} dưới cổng"


def cmd_report(a):
    out = Path(a.out_dir)
    version = json.loads(TASK.read_text(encoding="utf-8"))["version"]
    jev = {r["id"]: r for r in jl(a.jev_out)} if a.jev_out else {}
    gates, gsrc = load_gates(a.registry, a.site, version)
    rows = []
    for d in jl(a.diffs):
        lab, why = code_rule(d["old"], d["new"])
        src, p = "code", None
        if not lab:
            r = jev.get(d["id"]) or {}
            p = ((r.get("answers") or {}).get("significant") or {}).get("p_yes")
            lab, why = decide(p, gates)
            src = "jev"
        rows.append({"id": d["id"], "url": d["url"], "element": d["element"], "decision": lab, "source": src,
                     "p_significant": p, "why": why, "old": clean(d["old"]), "new": clean(d["new"])})
    order = {"đáng kể": 0, "Claude đọc": 1, "vô hại": 2}
    rows.sort(key=lambda r: (order[r["decision"]], r["url"], r["element"]))
    write(out / "diff_impact.jsonl", rows)
    cols = ["decision", "source", "p_significant", "url", "element", "why", "old", "new"]
    tsv = ["\t".join(cols)] + ["\t".join("" if r[c] is None else str(r[c]).replace("\t", " ") for c in cols) for r in rows]
    (out / "diff_impact.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
    n = {k: sum(r["decision"] == k for r in rows) for k in order}
    L = [f"# Phân loại diff — rubric {RUBRIC} {version}", "",
         f"- Diff: {len(rows)}. Đáng kể: {n['đáng kể']}. Claude đọc: {n['Claude đọc']}. Vô hại: {n['vô hại']}.",
         f"- Code chốt: {sum(r['source'] == 'code' for r in rows)}. Jev: {sum(r['source'] == 'jev' for r in rows)}.",
         f"- Cổng Jev: {gates or 'chưa có'} ({gsrc or 'Claude đọc mọi ca Jev'}).",
         "- Nhãn chỉ nói mức đổi nghĩa. Cột \"Chủ đích?\" của drift report vẫn do Account hoặc khách xác nhận.", ""]
    if gsrc == "defaults":
        L.append("- Cổng lấy từ defaults: bản nháp tới khi hiệu chuẩn trên 40 diff của site này.")
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(rows)} diff: {n} -> {out}", file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("diffs")
    d.add_argument("--old", required=True)
    d.add_argument("--new", required=True)
    d.add_argument("--fields", default="title,meta,h1")
    d.add_argument("--out", required=True)
    f = sub.add_parser("from-drift")
    f.add_argument("--json", required=True)
    f.add_argument("--out", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--diffs", required=True)
    p.add_argument("--out-dir", required=True)
    r = sub.add_parser("report")
    r.add_argument("--diffs", required=True)
    r.add_argument("--out-dir", required=True)
    r.add_argument("--jev-out")
    r.add_argument("--registry")
    r.add_argument("--site")
    a = ap.parse_args(argv)
    return {"diffs": cmd_diffs, "from-drift": cmd_from_drift, "prepare": cmd_prepare, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
