#!/usr/bin/env python3
"""Tra lại transcript Claude Code sau compact: tin của Lead, trả lời của agent, lệnh tool, danh sách phiên.
Chỉ đọc, không ghi file. Che key, token, IP, host staging. Không in tool result lớn, bỏ mọi đoạn nhắc BRAIN/journal.
Python standard library only.

Ví dụ:
  transcript_recall.py sessions --limit 10
  transcript_recall.py user 84cabbc3 --grep "Jev|duyệt" --since "2026-10-19 18:00"
  transcript_recall.py assistant 84cabbc3 --last 5
  transcript_recall.py tools 84cabbc3 --name "Bash|Artifact" --results 150
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys

PRIVATE_MARK = "BRAIN/journal"
HIDDEN = "[bỏ: nhắc tới BRAIN/journal]"

MASKS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)", re.S), "[KHOÁ RIÊNG]"),
    (re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]*"), "[JWT]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "[KEY]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "[KEY]"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "[KEY]"),
    (re.compile(r"\bAIza[\w-]{20,}"), "[KEY]"),
    (re.compile(r"\bAKIA[0-9A-Z]{12,}"), "[KEY]"),
    (re.compile(r"(?i)\b(authorization|bearer)(\s*[:=]?\s*(?:bearer\s+)?)[A-Za-z0-9._+/=-]{12,}"), r"\1\2[ẨN]"),
    (re.compile(r"(?i)\b([A-Za-z_]*(?:key|token|secret|password|passwd|pwd|credential|auth|_pass)[A-Za-z_]*)(\s*[=:]\s*)([\"']?)(?!\[ẨN\])[^\s\"',;]{4,}"), r"\1\2\3[ẨN]"),
    (re.compile(r"(\s-u\s+)\S+"), r"\1[ẨN]"),
    (re.compile(r"(https?://)[^\s/:@]+:[^\s/@]+@"), r"\1[ẨN]@"),
    (re.compile(r"wp-login\.php\?\S+"), "wp-login.php?[ẨN]"),
    (re.compile(r"\b(?!127\.0\.0\.1\b)(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
    (re.compile(r"\b[A-Fa-f0-9]{32,}\b"), "[HEX]"),
    (re.compile(r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Z])(?=[A-Za-z0-9_-]*[a-z])[A-Za-z0-9_-]{36,}\b"), "[TOKEN]"),
]


def load_needles(files):
    """Mỗi dòng của file là một chuỗi cần che (host, slug, mã). Thêm STG_HOST nếu có trong môi trường."""
    needles = []
    for f in files:
        for line in Path(f).expanduser().read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#") and len(line.strip()) >= 6:
                needles.append(line.strip())
    host = os.environ.get("STG_HOST", "").strip()
    if len(host) >= 6:
        needles.append(host)
    return needles


def mask(text, needles=()):
    for n in needles:
        text = text.replace(n, "[ẨN]")
    for rx, rep in MASKS:
        text = rx.sub(rep, text)
    return text


def clip(text, width):
    text = " ".join(text.split())
    return text if len(text) <= width else text[:width].rstrip() + f" …(+{len(text) - width} ký tự)"


def parse_ts(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
    except ValueError:
        return None


def parse_arg_time(value):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError("Thời gian cần dạng 'YYYY-MM-DD HH:MM' hoặc 'YYYY-MM-DD': " + value)


def default_dir():
    cwd = str(Path.cwd().resolve())
    return Path("~/.claude/projects").expanduser() / re.sub(r"[^A-Za-z0-9-]", "-", cwd)


def resolve_session(arg, projects_dir):
    p = Path(arg).expanduser()
    if p.is_file():
        return p
    found = sorted(Path(projects_dir).expanduser().glob(arg + "*.jsonl"))
    if not found:
        raise ValueError(f"Không thấy phiên '{arg}' trong {projects_dir}")
    if len(found) > 1:
        raise ValueError(f"'{arg}' khớp {len(found)} phiên; gõ dài hơn: " + ", ".join(f.stem[:12] for f in found[:5]))
    return found[0]


def records(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def blocks(rec):
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


REMINDER = re.compile(r"<(system-reminder|local-command-[a-z]+|command-[a-z]+)>.*?</\1>", re.S)


def user_texts(rec):
    out = []
    for b in blocks(rec):
        if b.get("type") == "text":
            t = REMINDER.sub("", b.get("text", "")).strip()
            if t:
                out.append(t)
    return out


def assistant_texts(rec):
    return [b.get("text", "").strip() for b in blocks(rec) if b.get("type") == "text" and b.get("text", "").strip()]


def result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def summarize_input(inp):
    if not isinstance(inp, dict):
        return str(inp)
    for key in ["command", "file_path", "url", "pattern", "query", "description", "path", "skill"]:
        if inp.get(key):
            return f"{key}={inp[key]}"
    return json.dumps(inp, ensure_ascii=False)


def in_window(rec, since, until):
    ts = parse_ts(rec.get("timestamp"))
    if ts is None:
        return since is None and until is None
    return (since is None or ts >= since) and (until is None or ts <= until)


def emit(rec, label, text, a, needles):
    ts = parse_ts(rec.get("timestamp"))
    when = ts.strftime("%d/%m %H:%M") if ts else "--/-- --:--"
    body = HIDDEN if PRIVATE_MARK in text else mask(text, needles)
    return f"[{when}] {label}: {clip(body, a.width)}"


def cmd_text(a, role):
    needles = load_needles(a.needle_file)
    rx = re.compile(a.grep, re.I) if a.grep else None
    since, until = (parse_arg_time(a.since) if a.since else None), (parse_arg_time(a.until) if a.until else None)
    path = resolve_session(a.session, a.projects_dir)
    lines = []
    for rec in records(path):
        if rec.get("type") != role or rec.get("isSidechain") or not in_window(rec, since, until):
            continue
        for text in (user_texts(rec) if role == "user" else assistant_texts(rec)):
            if rx and (PRIVATE_MARK in text or not rx.search(text)):
                continue
            lines.append(emit(rec, "Lead" if role == "user" else "Claude", text, a, needles))
    for line in lines[-a.last:] if a.last else lines:
        print(line)
    if not lines:
        print("không có tin khớp", file=sys.stderr)
    return 0


def cmd_tools(a):
    needles = load_needles(a.needle_file)
    name_rx = re.compile(a.name, re.I) if a.name else None
    since, until = (parse_arg_time(a.since) if a.since else None), (parse_arg_time(a.until) if a.until else None)
    path = resolve_session(a.session, a.projects_dir)
    calls, order = {}, []
    for rec in records(path):
        if rec.get("isSidechain"):
            continue
        for b in blocks(rec):
            if rec.get("type") == "assistant" and b.get("type") == "tool_use" and in_window(rec, since, until):
                if name_rx and not name_rx.search(b.get("name", "")):
                    continue
                calls[b.get("id")] = {"rec": rec, "name": b.get("name", "?"), "input": summarize_input(b.get("input"))}
                order.append(b.get("id"))
            elif rec.get("type") == "user" and b.get("type") == "tool_result" and b.get("tool_use_id") in calls:
                calls[b["tool_use_id"]]["result"] = (result_text(b), bool(b.get("is_error")))
    shown = order[-a.last:] if a.last else order
    for cid in shown:
        c = calls[cid]
        text, err = c.get("result", (None, False))
        head = emit(c["rec"], c["name"], c["input"], a, needles)
        if text is None:
            tail = "chưa có kết quả"
        elif PRIVATE_MARK in text or PRIVATE_MARK in c["input"]:
            tail = HIDDEN
        else:
            size = len(text)
            tail = ("LỖI " if err else "") + f"{size} ký tự"
            if a.results and size <= a.max_result:
                tail += ": " + clip(mask(text, needles), a.results)
            elif a.results:
                tail += f" (lớn hơn {a.max_result}, không in)"
        print(f"{head}\n    -> {tail}")
    if not shown:
        print("không có lệnh tool khớp", file=sys.stderr)
    return 0


def session_info(path):
    title, first, last_ts = "", "", None
    for rec in records(path):
        t = rec.get("type")
        if t == "ai-title" and rec.get("aiTitle"):
            title = rec["aiTitle"]
        elif t in ("custom-title", "summary") and (rec.get("customTitle") or rec.get("summary")):
            title = rec.get("customTitle") or rec.get("summary")
        elif t == "user" and not first and not rec.get("isSidechain"):
            texts = user_texts(rec)
            first = texts[0] if texts else ""
        last_ts = rec.get("timestamp") or last_ts
    return title, first, parse_ts(last_ts)


def cmd_sessions(a):
    needles = load_needles(a.needle_file)
    files = sorted(Path(a.projects_dir).expanduser().glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        raise ValueError("Không có phiên nào trong " + str(a.projects_dir))
    since = parse_arg_time(a.since) if a.since else None
    shown = 0
    for f in files:
        mtime = dt.datetime.fromtimestamp(f.stat().st_mtime)
        if since and mtime < since:
            continue
        if shown >= a.limit:
            break
        title, first, last = session_info(f)
        first = HIDDEN if PRIVATE_MARK in first else mask(first, needles)
        print(f"{f.stem[:8]}  {(last or mtime).strftime('%d/%m %H:%M')}  {f.stat().st_size / 1e6:6.1f} MB  "
              f"{clip(mask(title, needles), 50) or '(chưa đặt tên)'} | {clip(first, 70)}")
        shown += 1
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--projects-dir", default=None, help="thư mục .jsonl của project (mặc định: theo thư mục hiện tại trong ~/.claude/projects)")
    common.add_argument("--needle-file", action="append", default=[], help="file mỗi dòng một chuỗi cần che (host, slug); lặp được")
    common.add_argument("--width", type=int, default=600, help="số ký tự tối đa mỗi tin")
    filt = argparse.ArgumentParser(add_help=False)
    filt.add_argument("--since"); filt.add_argument("--until"); filt.add_argument("--last", type=int, default=0, help="chỉ in N mục cuối")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sessions", parents=[common], help="liệt kê phiên mới nhất"); s.add_argument("--limit", type=int, default=15); s.add_argument("--since")
    for name, hlp in [("user", "tin của Lead"), ("assistant", "trả lời của Claude")]:
        u = sub.add_parser(name, parents=[common, filt], help=hlp)
        u.add_argument("session", help="id (tiền tố) hoặc đường dẫn .jsonl"); u.add_argument("--grep", help="regex, không phân biệt hoa thường")
    t = sub.add_parser("tools", parents=[common, filt], help="lệnh tool và kết quả (kết quả lớn chỉ in kích thước)")
    t.add_argument("session"); t.add_argument("--name", help="regex tên tool")
    t.add_argument("--results", type=int, default=200, help="in tối đa N ký tự kết quả; 0 là chỉ in kích thước")
    t.add_argument("--max-result", type=int, default=4000, help="kết quả dài hơn mức này không in nội dung")
    a = p.parse_args()
    if a.projects_dir is None:
        a.projects_dir = default_dir()
    if a.command == "sessions":
        return cmd_sessions(a)
    if a.command == "tools":
        return cmd_tools(a)
    return cmd_text(a, a.command)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
