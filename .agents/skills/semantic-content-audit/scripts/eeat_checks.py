#!/usr/bin/env python3
"""Chọn check E-E-A-T theo preset và suy 26 điểm Phase 4 từ trạng thái (references/eeat-aleyda.md).

  select  --presets core[,review,...] [--draft] [--extra PS07,TA12] [--out checks.tsv]
          Bài đã đăng: core + preset nội dung. Bản nháp (--draft): pre_publish thay core.
          In TSV: check_id, scope, applies_when, question, how_to_check. Không ghi --out thì in ra màn hình.
  points  --status status.csv [--out diem.json]
          status.csv có cột check_id, status, evidence. Status: Meets | Partly meets | Does not meet |
          Not assessed | Not applicable. Meets, Does not meet, Not applicable cần evidence.
          Mỗi mục điểm lấy trạng thái xấu nhất của các check ánh xạ. Mục thiếu bằng chứng ghi CANNOT-VERIFY, 0 điểm.
Mã thoát: 0 xong · 2 input hỏng (check ID lạ, status lạ, thiếu evidence).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "references" / "eeat-checklist"
STATUSES = ["Meets", "Partly meets", "Does not meet", "Not assessed", "Not applicable"]
NEED_EVIDENCE = {"Meets", "Does not meet", "Not applicable"}
WORST = ["Does not meet", "Not assessed", "Partly meets", "Meets"]

# Mục điểm Phase 4 (E-E-A-T 16 + Helpful 10) -> check ID của checklist Aleyda.
MAP = [
    ("E-E-A-T", "First-hand usage evidence", 3, ["TA08", "CQ01"]),
    ("E-E-A-T", "Original evidence media", 3, ["SP04"]),
    ("E-E-A-T", "Specific observations", 2, ["CQ01", "CQ11"]),
    ("E-E-A-T", "Technical accuracy", 2, ["TA07", "TA13"]),
    ("E-E-A-T", "Domain language", 1, ["CQ11", "TA06"]),
    ("E-E-A-T", "Author credentials", 2, ["TA01", "TA02", "TA06"]),
    ("E-E-A-T", "Source quality", 1, ["TA04", "TA12"]),
    ("E-E-A-T", "No contradictions", 1, ["TA07", "SP07"]),
    ("E-E-A-T", "Transparent limitations", 1, ["PS07", "TA12"]),
    ("Helpful", "Created for audience", 2, ["PS01", "PS02"]),
    ("Helpful", "Reader doesn't need to re-search", 2, ["PS03", "PS04", "CQ12"]),
    ("Helpful", "Original value added", 2, ["CQ01", "CQ02", "PS06"]),
    ("Helpful", "No warning signs present", 2, ["PS05", "CQ03", "CQ09", "CP01"]),
    ("Helpful", "Who-How-Why addressed", 2, ["TA01", "TA11", "AI02"]),
]


def load_checks():
    return {c["check_id"]: c for c in json.loads((DATA / "checklist.json").read_text(encoding="utf-8"))["checks"]}


def load_presets():
    return {k: v for k, v in json.loads((DATA / "presets.json").read_text(encoding="utf-8")).items() if k != "_note"}


def die(msg):
    print(f"LỖI: {msg}", file=sys.stderr)
    sys.exit(2)


def select(presets, draft, extra):
    checks, pre = load_checks(), load_presets()
    names = [p for p in presets if p]
    for n in names:
        if n not in pre:
            die(f"preset lạ: {n} (có: {', '.join(pre)})")
    base = ["pre_publish"] if draft else ["core"]
    ids = []
    for n in base + [n for n in names if n not in ("core", "pre_publish")]:
        ids += pre[n]["check_ids"]
    for x in extra:
        if x not in checks:
            die(f"check ID lạ: {x}")
        ids.append(x)
    return [checks[i] for i in dict.fromkeys(ids)]


def read_status(path):
    checks = load_checks()
    rows = {}
    with open(path, encoding="utf-8", newline="") as f:
        for n, r in enumerate(csv.DictReader(f), start=2):
            cid, st, ev = (r.get("check_id") or "").strip(), (r.get("status") or "").strip(), (r.get("evidence") or "").strip()
            if cid not in checks:
                die(f"dòng {n}: check ID lạ '{cid}'")
            if st not in STATUSES:
                die(f"dòng {n}: status lạ '{st}'")
            if st in NEED_EVIDENCE and not ev:
                die(f"dòng {n}: {cid} {st} thiếu evidence")
            rows[cid] = st
    return rows


def points(rows):
    items, total, cv = [], 0, []
    for group, name, pts, ids in MAP:
        sts = [rows[i] for i in ids if i in rows and rows[i] != "Not applicable"]
        if not sts and any(rows.get(i) == "Not applicable" for i in ids):
            st, got = "Not applicable", pts
        elif not sts:
            st, got = "Not assessed", 0
        else:
            st = min(sts, key=WORST.index)
            got = {"Meets": pts, "Partly meets": pts // 2}.get(st, 0)
        flag = "CANNOT-VERIFY" if st == "Not assessed" else ""
        if flag:
            cv.append(name)
        total += got
        items.append({"group": group, "item": name, "max": pts, "points": got, "status": st, "flag": flag, "checks": ids})
    return {"points": total, "max": sum(m[2] for m in MAP), "cannot_verify": cv, "items": items}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--presets", default="core")
    s.add_argument("--draft", action="store_true")
    s.add_argument("--extra", default="")
    s.add_argument("--out")
    p = sub.add_parser("points")
    p.add_argument("--status", required=True)
    p.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "select":
        rows = select(a.presets.split(","), a.draft, [x for x in a.extra.split(",") if x])
        lines = ["check_id\tscope\tapplies_when\tquestion\thow_to_check"]
        lines += ["\t".join(c[k].replace("\t", " ").replace("\n", " ") for k in
                            ("check_id", "review_scope", "applies_when", "question", "how_to_check")) for c in rows]
        text = "\n".join(lines) + "\n"
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
            print(f"{len(rows)} check -> {a.out}")
        else:
            sys.stdout.write(text)
    else:
        res = points(read_status(a.status))
        text = json.dumps(res, ensure_ascii=False, indent=1)
        if a.out:
            Path(a.out).write_text(text + "\n", encoding="utf-8")
        print(f"Phase 4: {res['points']}/{res['max']} · CANNOT-VERIFY {len(res['cannot_verify'])} mục")


if __name__ == "__main__":
    main()
