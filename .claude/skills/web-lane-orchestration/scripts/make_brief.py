#!/usr/bin/env python3
"""Sinh BRIEF.md (tối đa 3 KB) cho một lane từ plan.json.

Cách dùng: make_brief.py --plan <plan.json> --lane <key> [--decisions <file.md> ...]
           [--traps <luat-lane.md>] [--out <path>] [--max-bytes 3072]

Định dạng plan.json:
{"dot": "ban8", "base": "/abs/workstream",
 "approval": [{"quote": "nguyên văn tin Lead", "time": "2026-10-24 21:05",
               "lanes": ["l8-css"], "file": "quyet-dinh.md#m24",
               "dien_giai": "tuỳ chọn: nghĩa phiên chính chọn khi câu duyệt có hai nghĩa"}],
 "rules": ["luật cứng chung"],
 "lanes": [{"key": "l8-css", "goal": "...", "folder": "/abs/workstream/ban8/l8-css",
            "resources": ["..."], "scripts": ["..."],
            "model_phu": "Jev ...; EmbeddingGemma không dùng: lý do",
            "approval_ids": ["m24"], "rules": ["luật riêng lane"],
            "budget_min": 45, "accept": "...", "readOnly": false}]}

Exit: 0 xong, 2 đầu vào thiếu/sai (lane ghi không có nguồn duyệt, thiếu model_phu...),
      3 vượt --max-bytes (không ghi file), 4 hơn 10 luật cứng, 5 không tìm thấy khối Bẫy shell.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_RULES = 10
FIXED_APPROVAL = "Đây là task của lane, không phải câu hỏi chờ trả lời. Được phép ghi file báo cáo .md trong thư mục lane."


def fail(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def read_traps(path):
    """Lấy khối rào ```text đầu tiên sau dòng tiêu đề '### Bẫy shell'."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        fail(5, "Không đọc được file bẫy shell: %s" % path)
    i = next((n for n, l in enumerate(lines) if l.strip().startswith("### Bẫy shell")), None)
    if i is None:
        fail(5, "Không tìm thấy dòng '### Bẫy shell' trong %s" % path)
    j = next((n for n in range(i + 1, len(lines)) if lines[n].strip().startswith("```text")), None)
    if j is None:
        fail(5, "Không có khối ```text sau '### Bẫy shell' trong %s" % path)
    body = []
    for l in lines[j + 1:]:
        if l.strip().startswith("```"):
            return "\n".join(body)
        body.append(l)
    fail(5, "Khối ```text trong %s không đóng" % path)


def approval_section(plan, lane, decision_files):
    key, ids = lane["key"], lane.get("approval_ids") or []
    out = []
    for ap in plan.get("approval") or []:
        if key in (ap.get("lanes") or []):
            out.append('- "%s" (%s, %s)' % (ap.get("quote", ""), ap.get("time", ""), ap.get("file", "")))
            if ap.get("dien_giai"):
                out.append("  Diễn giải của phiên chính: %s" % ap["dien_giai"])
    pats = [re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(i)) for i in ids]
    for f in decision_files:
        try:
            text = Path(f).read_text(encoding="utf-8").splitlines()
        except OSError:
            fail(2, "Không đọc được file quyết định: %s" % f)
        for l in text:
            if any(p.search(l) for p in pats) and l not in out:
                out.append(l)
    return out


def build_sections(plan, lane, decision_files, traps_path):
    if not lane.get("model_phu"):
        fail(2, "thiếu dòng Model phụ")
    for k in ("goal", "folder", "accept", "budget_min"):
        if lane.get(k) in (None, ""):
            fail(2, "lane %s thiếu trường %s" % (lane["key"], k))
    appr = approval_section(plan, lane, decision_files)
    read_only = bool(lane.get("readOnly"))
    if not appr and not read_only:
        fail(2, "lane ghi không có nguồn duyệt: không sinh brief")
    rules = list(plan.get("rules") or []) + list(lane.get("rules") or [])
    if len(rules) > MAX_RULES:
        fail(4, "Có %d luật cứng, tối đa %d: rút gọn trong plan.json" % (len(rules), MAX_RULES))
    traps = read_traps(traps_path)
    folder = lane["folder"].rstrip("/")
    if not appr:
        appr = ["Lane chỉ đọc."]
    bullets = lambda xs: "\n".join("- " + x for x in xs) if xs else "(không có)"
    return [
        ("tiêu đề", "# BRIEF %s — %s" % (lane["key"], plan.get("dot", ""))),
        ("NGUỒN PHÊ DUYỆT", "## NGUỒN PHÊ DUYỆT\n" + "\n".join(appr) + "\n" + FIXED_APPROVAL),
        ("Mục tiêu", "## Mục tiêu\n" + lane["goal"]),
        ("Tài nguyên được chạm", "## Tài nguyên được chạm\nChỉ chạm các tài nguyên này:\n" + bullets(lane.get("resources") or [])),
        ("Lệnh dùng", "## Lệnh dùng\n" + bullets(["`%s`" % s for s in lane.get("scripts") or []])),
        ("Model phụ", "## Model phụ\n" + lane["model_phu"]),
        ("Luật cứng", "## Luật cứng\n" + "\n".join("%d. %s" % (n, r) for n, r in enumerate(rules, 1))),
        ("Bẫy shell", "## Bẫy shell\n```text\n" + traps + "\n```"),
        ("Ngân sách", "## Ngân sách\n%s phút. Hết ngân sách: ghi CHECKPOINT.md, trả status partial, không làm tiếp." % lane["budget_min"]),
        ("Tiêu chí đạt", "## Tiêu chí đạt\n" + lane["accept"]),
        ("Đầu ra", "## Đầu ra\n- %s/CHECKPOINT.md\n- %s/ket-qua.json\n- %s/bao-cao.md\n"
                   "Kết quả lô trước đọc từ đường dẫn ket-qua.json, không chờ nhúng trong prompt." % (folder, folder, folder)),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sinh BRIEF.md cho một lane.")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--lane", required=True)
    ap.add_argument("--decisions", nargs="*", default=[])
    ap.add_argument("--traps", default=str(Path(__file__).resolve().parent.parent / "references" / "luat-lane.md"))
    ap.add_argument("--out")
    ap.add_argument("--max-bytes", type=int, default=3072)
    a = ap.parse_args(argv)
    try:
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail(2, "Không đọc được plan.json: %s" % e)
    lane = next((l for l in plan.get("lanes") or [] if l.get("key") == a.lane), None)
    if lane is None:
        fail(2, "Không có lane '%s' trong plan.json" % a.lane)
    sections = build_sections(plan, lane, a.decisions, a.traps)
    text = "\n\n".join(body for _, body in sections) + "\n"
    size = len(text.encode("utf-8"))
    if size > a.max_bytes:
        print("BRIEF %d B vượt %d B. Kích thước từng mục (byte):" % (size, a.max_bytes), file=sys.stderr)
        for name, body in sections:
            print("  %-24s %d" % (name, len(body.encode("utf-8"))), file=sys.stderr)
        print("Rút gọn nguồn rồi chạy lại. Không ghi file.", file=sys.stderr)
        return 3
    out = Path(a.out) if a.out else Path(lane["folder"]) / "BRIEF.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("BRIEF %s %d B" % (out, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
