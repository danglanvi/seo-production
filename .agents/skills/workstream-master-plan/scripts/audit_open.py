#!/usr/bin/env python3
"""Liệt kê yêu cầu của Lead chưa vào sổ plan.json, và thẻ đã duyệt chưa áp.

Chỉ đọc, không ghi file nào.

Nguồn tin nhắn (dùng một hoặc nhiều --source):
  *.jsonl   transcript Claude Code. Lấy tin Lead gõ (type user, không isMeta, turnOrigin
            human), tin gửi giữa lượt (attachment queued_command) và tin phiên khác chuyển
            ("Another Claude session ..."). Bỏ tin task-notification, scheduled, system và khối
            <ide_opened_file>, <ide_selection> do IDE chèn.
  *.txt/.md file text của runtime khác. Mỗi tin cách nhau một dòng '---'. Nếu file không có
            dòng '---' thì mỗi đoạn cách nhau dòng trống là một tin. Dòng đầu của tin có thể là
            '[DD/MM/YYYY HH:MM]' hoặc '[DD/MM HH:MM]' để lọc theo --since.

Một tin coi là đã vào sổ khi một ask trong plan.json trùng tin đó: ask nằm trong tin, tin nằm
trong ask, một đoạn ask (cách bởi '...' hoặc '…') nằm trong tin, hoặc từ chung >= 60% từ của ask.
Tin ngắn hơn --min-chars (mặc định 12) bị bỏ qua, ví dụ "ok", "duyệt".

Thẻ duyệt (tuỳ chọn): --cards FILE.json là export các thẻ, dạng list hoặc object id -> thẻ hoặc
{"cards": [...]}. Thẻ có status approved hoặc edited mà chưa applied (không có applied true,
applied_at, và status khác applied) là việc chưa áp. --applied FILE.json (ví dụ mark_applied.json,
list id hoặc list object có id) loại thêm các thẻ đã áp. Giả định schema này chưa kiểm với thẻ thật.

Mã thoát: 0 không còn việc mở, 1 còn tin chưa vào sổ hoặc thẻ chưa áp, 2 đầu vào sai.
Đầu ra che chuỗi giống token, mật khẩu, khoá API.
Python 3.9+, chỉ dùng thư viện chuẩn.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan as P  # noqa: E402

PEER_PREFIXES = ("another claude session",)
SKIP_PREFIXES = ("<task-notification", "<system-reminder", "<command-", "<local-command", "[request interrupted",
                 "caveat:", "this session is being continued", "base directory for this skill",
                 "<browser_instruction", "<artifact-content-auth")
SKIP_TURN_ORIGINS = {"scheduled", "task_notification", "system"}
CC_TYPES = {"user", "assistant", "attachment", "system", "summary"}
SECRET_RES = [
    re.compile(r"\b(sk|pk|ghp|gho|xox[abp]|AKIA|AIza)[-_A-Za-z0-9]{16,}"),
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)\b(password|passwd|pwd|mật khẩu|token|secret|api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?<![A-Za-z0-9/_.-])(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{32,}(?![A-Za-z0-9/_.-])"),
]
QUERY_SECRET_RE = re.compile(r"(?i)([?&](?:sk|key|token|access_token|auth|sig|signature)=)[^&\s#]+")
IDE_BLOCK_RE = re.compile(r"<(ide_[a-z_]+)>.*?</\1>", re.S)


class InputError(Exception):
    pass


def mask(text):
    text = QUERY_SECRET_RE.sub(r"\1[đã che]", text)
    for rx in SECRET_RES:
        text = rx.sub("[đã che]", text)
    return text


def norm(text):
    t = unicodedata.normalize("NFC", text).lower()
    t = re.sub(r"[^\w]+", " ", t, flags=re.UNICODE)
    return " ".join(t.split())


def parse_iso_local(ts):
    if not isinstance(ts, str):
        return None
    t = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], ts.strip())
    t = t.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(t).astimezone().replace(tzinfo=None)
    except ValueError:
        return None


def strip_images(text):
    text = IDE_BLOCK_RE.sub("", text)
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("[Image:")).strip()


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return ""
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def classify(text):
    low = text.strip().lower()
    if any(low.startswith(p) for p in SKIP_PREFIXES):
        return None
    if any(low.startswith(p) for p in PEER_PREFIXES):
        return "peer"
    return "lead"


def read_transcript(path):
    msgs = []
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError as e:
        raise InputError("không đọc được %s: %s" % (path, e))
    cc_rows = 0
    with fh:
        for line in fh:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(o, dict):
                continue
            if o.get("type") in CC_TYPES:
                cc_rows += 1
            kind, text = None, ""
            if o.get("type") == "user" and not o.get("isMeta"):
                if o.get("turnOrigin") in SKIP_TURN_ORIGINS or o.get("promptSource") == "system":
                    continue
                origin = o.get("origin")
                if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
                    continue
                text = text_of((o.get("message") or {}).get("content"))
                kind = "typed"
            elif o.get("type") == "attachment":
                a = o.get("attachment") or {}
                if a.get("type") != "queued_command" or a.get("commandMode") not in (None, "prompt"):
                    continue
                text = text_of(a.get("prompt"))
                kind = "queued"
            else:
                continue
            text = strip_images(text)
            if not text:
                continue
            cls = classify(text)
            if cls is None:
                continue
            msgs.append({"time": parse_iso_local(o.get("timestamp")), "text": text,
                         "kind": "peer" if cls == "peer" else kind, "src": Path(path).name})
    if cc_rows == 0:
        raise InputError("%s không phải transcript Claude Code (không có dòng user/assistant). "
                         "Runtime khác: xuất tin ra file .txt, mỗi tin cách nhau dòng ---" % path)
    return msgs


def read_text_file(path, ref):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise InputError("không đọc được %s: %s" % (path, e))
    if re.search(r"^-{3,}\s*$", raw, re.M):
        blocks = re.split(r"^-{3,}\s*$", raw, flags=re.M)
    else:
        blocks = re.split(r"\n\s*\n", raw)
    msgs = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        t = None
        m = re.match(r"^\[([^\]]+)\]\s*", b)
        if m:
            t = P.parse_stamp(m.group(1), ref)
            if t is not None:
                b = b[m.end():].strip()
        if b:
            msgs.append({"time": t, "text": b, "kind": "text", "src": Path(path).name})
    return msgs


def covered(msg_text, asks):
    mt = norm(msg_text)
    mset = set(mt.split())
    for ask in asks:
        pieces = [x for x in re.split(r"\.\.\.|…", ask) if norm(x)]
        full = norm(ask)
        if len(full) >= 12 and (full in mt or (len(mt) >= 12 and mt in full)):
            return True
        for pc in pieces:
            n = norm(pc)
            if len(n) >= 15 and n in mt:
                return True
        toks = [t for t in full.split() if len(t) >= 2]
        if len(toks) >= 4 and sum(1 for t in toks if t in mset) / len(toks) >= 0.6:
            return True
    return False


def audit_messages(plan, msgs, min_chars, since):
    asks = [r["ask"] for r in plan.get("requests", []) if isinstance(r, dict) and isinstance(r.get("ask"), str)]
    seen, open_, short, old, ok = set(), [], 0, 0, 0
    for m in msgs:
        key = (norm(m["text"]), m["time"].strftime("%Y%m%d%H%M") if m["time"] else "")
        if key in seen:
            continue
        seen.add(key)
        if since and m["time"] and m["time"] < since:
            old += 1
            continue
        if len(m["text"].strip()) < min_chars:
            short += 1
            continue
        if covered(m["text"], asks):
            ok += 1
        else:
            open_.append(m)
    return open_, {"covered": ok, "short": short, "before_since": old, "total": len(seen)}


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise InputError("không đọc được %s: %s" % (path, e))
    except json.JSONDecodeError as e:
        raise InputError("%s không phải JSON: %s" % (path, e))


def card_list(data):
    if isinstance(data, dict):
        for k in ("cards", "docs", "items"):
            if isinstance(data.get(k), list):
                return card_list(data[k])
        out = []
        for k, v in data.items():
            if isinstance(v, dict):
                out.append(dict(v, id=v.get("id", k)))
        return out
    if isinstance(data, list):
        return [c for c in data if isinstance(c, dict)]
    raise InputError("--cards cần list hoặc object")


def applied_ids(data):
    ids = set()
    if isinstance(data, dict):
        data = data["applied"] if isinstance(data.get("applied"), list) else list(data.keys())
    if not isinstance(data, list):
        raise InputError("--applied cần list id hoặc list object có id")
    for x in data:
        if isinstance(x, str):
            ids.add(x)
        elif isinstance(x, dict) and isinstance(x.get("id"), str):
            ids.add(x["id"])
    return ids


def pending_cards(cards, applied):
    out = []
    for c in cards:
        cid = c.get("id")
        status = str(c.get("status", "")).lower()
        if status not in ("approved", "edited"):
            continue
        if c.get("applied") is True or c.get("applied_at") or cid in applied:
            continue
        out.append(c)
    return out


def build_parser():
    ap = argparse.ArgumentParser(prog="audit_open.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--plan", default="plan.json", help="đường dẫn plan.json (mặc định ./plan.json)")
    ap.add_argument("--source", action="append", default=[], help="transcript .jsonl hoặc file text tin nhắn, dùng nhiều lần")
    ap.add_argument("--since", help="chỉ xét tin từ mốc 'DD/MM/YYYY HH:MM'. Tin không có giờ vẫn xét.")
    ap.add_argument("--min-chars", type=int, default=12, help="bỏ tin ngắn hơn số ký tự này (mặc định 12)")
    ap.add_argument("--no-peer", action="store_true", help="bỏ tin do phiên khác chuyển")
    ap.add_argument("--cards", help="export thẻ duyệt (JSON)")
    ap.add_argument("--applied", help="mark_applied.json: id thẻ đã áp")
    ap.add_argument("--excerpt", type=int, default=240, help="số ký tự trích mỗi tin (mặc định 240)")
    ap.add_argument("--json", action="store_true", help="in JSON thay cho văn bản")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    ref = P.now()
    try:
        plan, _ = P.load_plan(args.plan)
    except P.PlanError as e:
        print("LỖI: " + e.msg, file=sys.stderr)
        return 2
    if not isinstance(plan.get("requests"), list):
        print("LỖI: plan.json thiếu 'requests'", file=sys.stderr)
        return 2
    if not args.source and not args.cards:
        print("LỖI: cần ít nhất một --source hoặc --cards", file=sys.stderr)
        return 2
    since = None
    if args.since:
        since = P.parse_stamp(args.since, ref)
        if since is None:
            print("LỖI: --since sai dạng, dùng 'DD/MM/YYYY HH:MM'", file=sys.stderr)
            return 2
    try:
        msgs = []
        for s in args.source:
            msgs += read_transcript(s) if s.lower().endswith(".jsonl") else read_text_file(s, ref)
        if args.no_peer:
            msgs = [m for m in msgs if m["kind"] != "peer"]
        pend = []
        if args.cards:
            applied = applied_ids(load_json(args.applied)) if args.applied else set()
            pend = pending_cards(card_list(load_json(args.cards)), applied)
    except InputError as e:
        print("LỖI: %s" % e, file=sys.stderr)
        return 2

    open_, stats = audit_messages(plan, msgs, args.min_chars, since)
    if args.json:
        print(json.dumps({
            "open_messages": [{"time": m["time"].strftime(P.STAMP_FMT) if m["time"] else None, "kind": m["kind"],
                               "src": m["src"], "text": mask(m["text"])[:args.excerpt]} for m in open_],
            "pending_cards": [{"id": c.get("id"), "status": c.get("status")} for c in pend],
            "stats": stats}, ensure_ascii=False, indent=1))
    else:
        print("Tin xét %d: đã vào sổ %d, bỏ vì ngắn %d, trước --since %d, chưa vào sổ %d." % (
            stats["total"], stats["covered"], stats["short"], stats["before_since"], len(open_)))
        for n, m in enumerate(open_, 1):
            t = m["time"].strftime(P.STAMP_FMT) if m["time"] else "không rõ giờ"
            ex = " ".join(mask(m["text"]).split())
            print("%d. [%s] (%s, %s) %s%s" % (n, t, m["kind"], m["src"], ex[:args.excerpt], "..." if len(ex) > args.excerpt else ""))
        if args.cards:
            print("Thẻ approved/edited chưa áp: %d" % len(pend))
            for c in pend:
                print("- %s (%s)" % (c.get("id"), c.get("status")))
        if open_ or pend:
            print("Việc cần làm: chạy plan.py add-request và add-item cho từng tin, rồi chạy lại lệnh này.")
    return 1 if (open_ or pend) else 0


if __name__ == "__main__":
    sys.exit(main())
