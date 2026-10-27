#!/usr/bin/env python3
"""Đổi câu trả lời của Lead thành danh sách việc.

Nguồn câu trả lời (chọn một):
  --text FILE   đoạn chữ dán từ nút "Chép câu trả lời" (FILE hoặc - cho stdin)
  --db FILE     JSON của doc db (kết quả ArtifactData get), có choices, notes, done

Luật: câu để trống = theo đề xuất, trừ hai trường hợp phải chọn tay:
thẻ có touches_live: true, hoặc phương án đề xuất là việc xoá hoặc gửi ra ngoài.
Hai trường hợp đó vào mục "Chờ chọn rõ", không vào danh sách làm.

Mặc định chỉ in kết quả. --into FILE.md cộng thêm một mục "Quyết định" vào file,
ở chế độ dry-run cho tới khi có --write. Python stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_decision as g  # noqa: E402


class InputError(Exception):
    pass


def read_text_source(arg):
    try:
        return sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    except OSError as e:
        raise InputError("không đọc được %s: %s" % (arg, e))


def find_doc(obj, depth=0):
    """Tìm dict có khoá choices trong kết quả ArtifactData get (chấp nhận vài lớp bọc)."""
    if isinstance(obj, dict):
        if "choices" in obj or "notes" in obj:
            return obj
        if depth < 4:
            for k in ("data", "doc", "document", "result"):
                if k in obj:
                    r = find_doc(obj[k], depth + 1)
                    if r is not None:
                        return r
    if isinstance(obj, list) and len(obj) == 1 and depth < 4:
        return find_doc(obj[0], depth + 1)
    return None


def from_db(path):
    try:
        raw = json.loads(read_text_source(path))
    except ValueError as e:
        raise InputError("JSON db hỏng: %s" % e)
    d = find_doc(raw)
    if d is None:
        raise InputError("không thấy choices hoặc notes trong JSON db")
    choices = d.get("choices") or {}
    notes = d.get("notes") or {}
    if not isinstance(choices, dict) or not isinstance(notes, dict):
        raise InputError("choices và notes phải là object")
    return {"choices": choices, "notes": notes, "done": d.get("done"), "updated": d.get("updated"), "source": "db"}


def from_text(path, spec):
    """Đọc chữ dán. Dòng của thẻ bắt đầu bằng '<label> — '. Dòng khác nối vào thẻ trước (ghi chú nhiều dòng)."""
    text = read_text_source(path).replace("\r\n", "\n")
    labels = {c["label"]: c for c in spec["cards"]}
    ordered = sorted(labels, key=len, reverse=True)
    blocks = {}
    cur = None
    unknown = []
    for line in text.split("\n"):
        hit = next((lb for lb in ordered if line.startswith(lb + " — ")), None)
        if hit:
            cur = hit
            blocks[cur] = [line[len(hit) + 3:]]
        elif cur is not None and line.strip():
            blocks[cur].append(line)
        elif cur is None and re.match(r"^.{1,40} — ", line):
            unknown.append(line[:60])
    choices, notes = {}, {}
    for lb, lines in blocks.items():
        c = labels[lb]
        body = "\n".join(lines)
        pos = 0
        marks = []
        for q in c["questions"]:
            tok = q["short"] + ": "
            i = body.find(tok, pos)
            if i < 0:
                raise InputError("thẻ %s: không thấy câu %r trong câu trả lời" % (lb, q["short"]))
            marks.append((q, i, i + len(tok)))
            pos = i + len(tok)
        ni = body.find("Ghi chú: ", pos if marks else 0)
        if ni >= 0 and (ni == 0 or body[max(0, ni - 2):ni] == "; "):
            notes[c["id"]] = body[ni + len("Ghi chú: "):].strip()
            tail_end = ni - 2 if ni > 0 else 0
        else:
            tail_end = len(body)
        for k, (q, s, e) in enumerate(marks):
            end = marks[k + 1][1] - 2 if k + 1 < len(marks) else tail_end
            val = body[e:end].strip()
            if val and not val.startswith("(để trống"):
                choices[q["name"]] = val
    if not blocks:
        raise InputError("không nhận ra dòng thẻ nào. Kiểm lại file dán và --spec")
    # Nút Chép luôn in mọi thẻ có câu hỏi. Thẻ vắng dòng nghĩa là chữ dán bị cắt, không phải để trống.
    missing = [c["label"] for c in spec["cards"] if c["questions"] and c["label"] not in blocks]
    return {"choices": choices, "notes": notes, "done": None, "updated": None, "source": "text", "unknown": unknown,
            "missing": missing}


def resolve(spec, ans):
    """Trả (mục, lỗi). Mỗi mục: card, label, question, value, option_label, source, note."""
    items, problems = [], []
    known_names = {q["name"] for c in spec["cards"] for q in c["questions"]}
    for name in ans["choices"]:
        if name not in known_names:
            problems.append("lựa chọn cho câu không có trong spec: %s" % name)
    known_ids = {c["id"] for c in spec["cards"]}
    for cid in ans["notes"]:
        if cid not in known_ids:
            problems.append("ghi chú cho thẻ không có trong spec: %s" % cid)
    missing = set(ans.get("missing") or [])
    for lb in [c["label"] for c in spec["cards"] if c["label"] in missing]:
        problems.append("thẻ %s: không có dòng trong chữ dán, chưa làm" % lb)
    for c in spec["cards"]:
        note = str(ans["notes"].get(c["id"], "")).strip()
        if c["label"] in missing:
            for q in c["questions"]:
                rec = next(o for o in q["options"] if o["recommended"])
                items.append({"card": c["id"], "label": c["label"], "question": q["short"], "note": "", "value": None,
                              "option_label": None, "source": "hold", "reason": "thiếu dòng trong chữ dán",
                              "recommended": rec["value"]})
            continue
        if not c["questions"]:
            if note:
                items.append({"card": c["id"], "label": c["label"], "question": None, "value": None,
                              "option_label": None, "source": "note", "note": note})
            continue
        for k, q in enumerate(c["questions"]):
            val = ans["choices"].get(q["name"])
            rec = next(o for o in q["options"] if o["recommended"])
            item = {"card": c["id"], "label": c["label"], "question": q["short"], "note": note if k == len(c["questions"]) - 1 else ""}
            if val is None or not str(val).strip():
                if g.is_hold_q(c, q):
                    item.update(value=None, option_label=None, source="hold",
                                reason="config sống" if c.get("touches_live") else "đề xuất là việc xoá hoặc gửi ra ngoài",
                                recommended=rec["value"])
                else:
                    item.update(value=rec["value"], option_label=rec["label"], source="default", destructive=rec["destructive"])
            else:
                opt = next((o for o in q["options"] if g.norm_ws(o["value"]) == g.norm_ws(val)), None)
                if opt is None:
                    item.update(value=str(val), option_label=None, source="unmatched")
                    problems.append("thẻ %s: giá trị %r không khớp phương án nào" % (c["label"], str(val)[:80]))
                else:
                    item.update(value=opt["value"], option_label=opt["label"], source="chosen", destructive=opt["destructive"])
            items.append(item)
    return items, problems


def render_md(spec, ans, items, problems, version):
    todo = [i for i in items if i["source"] in ("chosen", "default")]
    hold = [i for i in items if i["source"] == "hold"]
    bad = [i for i in items if i["source"] == "unmatched"]
    notes_only = [i for i in items if i["source"] == "note"]
    n_chosen = sum(1 for i in todo if i["source"] == "chosen")
    n_def = len(todo) - n_chosen
    lines = ["# Việc từ câu trả lời: %s%s" % (spec["title"], " (bản %s)" % version if version else "")]
    src = "db" if ans["source"] == "db" else "chữ dán"
    if ans.get("updated"):
        src += ", lưu lúc %s" % ans["updated"]
    lines.append("Nguồn: %s." % src)
    if ans["source"] == "db" and ans.get("done") is not True:
        lines.append("Cảnh báo: Lead chưa bấm \"Lưu, tôi trả lời xong\". Câu trả lời có thể chưa đủ.")
    lines.append("Tổng: %d câu. Anh chọn %d, theo đề xuất %d, chờ chọn rõ %d, không khớp %d." % (
        len(todo) + len(hold) + len(bad), n_chosen, n_def, len(hold), len(bad)))
    lines += ["", "## Làm"]
    if not todo:
        lines.append("- Không có việc.")
    for n, i in enumerate(todo, 1):
        tag = "anh chọn" if i["source"] == "chosen" else "theo đề xuất"
        lines.append("%d. [%s] %s: %s (%s)" % (n, i["label"], i["question"], i["value"], tag))
        if i.get("note"):
            lines.append("   Ghi chú: %s" % i["note"].replace("\n", " / "))
    if hold:
        lines += ["", "## Chờ chọn rõ (để trống thì chưa làm)"]
        for i in hold:
            lines.append("- [%s] %s. Lý do: %s. Đề xuất: %s." % (i["label"], i["question"], i["reason"], i["recommended"]))
            if i.get("note"):
                lines.append("  Ghi chú: %s" % i["note"].replace("\n", " / "))
    if bad:
        lines += ["", "## Không khớp phương án (kiểm lại)"]
        for i in bad:
            lines.append("- [%s] %s: %s" % (i["label"], i["question"], i["value"]))
    if notes_only:
        lines += ["", "## Ghi chú ở thẻ không hỏi"]
        for i in notes_only:
            lines.append("- [%s] %s" % (i["label"], i["note"].replace("\n", " / ")))
    if problems:
        lines += ["", "## Cảnh báo"]
        lines += ["- " + p for p in problems]
    return "\n".join(lines) + "\n"


def section_for_file(spec, md_body, version):
    marker = "<!-- decision-page:%s:v%s -->" % (spec["project"], version or "?")
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    body = md_body.split("\n", 1)[1] if md_body.startswith("# ") else md_body
    return marker, "## Quyết định: %s (bản %s, đọc lúc %s)\n%s\n%s\n" % (spec["title"], version or "?", stamp, marker, body.strip("\n"))


def put_section(existing, marker, section):
    if marker in existing:
        start = existing.rfind("\n## ", 0, existing.find(marker))
        start = 0 if start < 0 else start + 1
        end = existing.find("\n## ", existing.find(marker))
        tail = "" if end < 0 else existing[end + 1:]
        return existing[:start] + section + ("\n" + tail if tail else "")
    return existing.rstrip("\n") + "\n\n" + section if existing.strip() else section


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Đổi câu trả lời thành danh sách việc. Câu để trống = theo đề xuất, trừ xoá và config sống.",
        epilog="Mã thoát: 0 đạt; 2 input hỏng (file, JSON, spec); 3 có giá trị không khớp phương án hoặc tên lạ; 4 --require-done mà chưa bấm Lưu.")
    ap.add_argument("--spec", required=True, help="cau-hoi.json (hoặc file .cau-hoi.json cạnh trang đã dựng)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="file chữ dán từ nút Chép (- là stdin)")
    src.add_argument("--db", help="file JSON của doc db (ArtifactData get)")
    ap.add_argument("--version", help="số bản để ghi vào mục Quyết định (mặc định lấy từ spec)")
    ap.add_argument("--json", action="store_true", help="in JSON thay cho Markdown")
    ap.add_argument("--require-done", action="store_true", help="thoát 4 nếu db chưa có done=true")
    ap.add_argument("--into", help="file .md để cộng mục Quyết định vào (dry-run nếu thiếu --write)")
    ap.add_argument("--write", action="store_true", help="ghi thật vào --into")
    args = ap.parse_args(argv)
    if args.write and not args.into:
        print("LỖI: --write cần --into", file=sys.stderr)
        return 2
    try:
        spec = g.load_spec(args.spec, check_files=False)
    except g.SpecError as e:
        print("LỖI spec: " + "; ".join(e.problems), file=sys.stderr)
        return 2
    version = args.version or (json.loads(Path(args.spec).read_text(encoding="utf-8")).get("version"))
    try:
        ans = from_db(args.db) if args.db else from_text(args.text, spec)
    except InputError as e:
        print("LỖI input: %s" % e, file=sys.stderr)
        return 2
    items, problems = resolve(spec, ans)
    for u in ans.get("unknown") or []:
        problems.append("dòng không khớp thẻ nào: %s" % u)
    md = render_md(spec, ans, items, problems, version)
    if args.json:
        print(json.dumps({"title": spec["title"], "version": version, "source": ans["source"], "done": ans.get("done"),
                          "items": items, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(md)
    if args.into:
        marker, section = section_for_file(spec, md, version)
        p = Path(args.into)
        existing = p.read_text(encoding="utf-8") if p.exists() else ""
        new = put_section(existing, marker, section)
        if args.write:
            p.write_text(new, encoding="utf-8")
            print("Đã ghi mục Quyết định vào %s" % p, file=sys.stderr)
        else:
            print("DRY-RUN: sẽ %s mục Quyết định trong %s. Thêm --write để ghi." % ("thay" if marker in existing else "thêm", p), file=sys.stderr)
    if args.require_done and ans["source"] == "db" and ans.get("done") is not True:
        print("LỖI: db chưa có done=true", file=sys.stderr)
        return 4
    return 3 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
