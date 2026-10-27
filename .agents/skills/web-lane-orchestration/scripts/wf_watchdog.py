#!/usr/bin/env python3
"""Dò agent workflow bị treo, chạy ngoài model (không gọi model, không gửi ra ngoài, không kill tiến trình).

Cách dùng: wf_watchdog.py <run-dir hoặc session-dir> [--minutes 12] [--idle-minutes 20]
           [--once] [--interval 120] [--max-hours 10] [--out <file>]

Chạy bằng Bash run_in_background: tiến trình chỉ thoát khi có việc cần người xem.
Exit 0: không có báo (--once) hoặc run đã xong (in dòng XONG).
Exit 1: có báo TREO hoặc IM.  Exit 3: quá --max-hours.  Exit 2: đầu vào sai.

Cấu trúc dữ liệu của Claude Code (đã kiểm trên dữ liệu thật):
  <session>/subagents/workflows/<runId>/journal.jsonl     dòng started/result theo agent
  <session>/subagents/workflows/<runId>/agent-<id>.jsonl  transcript, mỗi dòng có timestamp ISO
  <session>/workflows/<runId>.json                        chỉ có khi run đã kết thúc; status completed|killed|failed
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TAIL_BYTES = 256 * 1024
TERMINAL = {"completed", "killed", "failed"}
APPROVAL_TOOLS = {"Monitor", "ArtifactData", "Artifact"}
SECRET_RE = re.compile(r"(?i)(pass(word)?|token|secret|key)\s*[=:]\s*\S+")
QUIET_MIN_FINISH = 10  # phút không file nào ghi thì coi run đã xong
STALE_HOURS = 12  # chế độ session-dir: bỏ qua run bị bỏ rơi lâu hơn mức này


def parse_ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def tail_lines(path):
    """Đọc phần cuối file, bỏ dòng đầu nếu bị cắt giữa chừng."""
    with open(path, "rb") as fh:
        size = os.fstat(fh.fileno()).st_size
        start = max(0, size - TAIL_BYTES)
        fh.seek(start)
        data = fh.read()
    lines = data.split(b"\n")
    if start > 0:
        lines = lines[1:]
    return lines


def pending_tools(path):
    """Trả về {tool_use_id: (datetime, tên, input)} cho tool_use chưa có tool_result trong phần cuối file."""
    pend = {}
    for raw in tail_lines(path):
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        content = (d.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        ts = parse_ts(d.get("timestamp"))
        for x in content:
            if not isinstance(x, dict):
                continue
            if x.get("type") == "tool_use" and ts:
                pend[x.get("id")] = (ts, x.get("name", "?"), x.get("input") or {})
            elif x.get("type") == "tool_result":
                pend.pop(x.get("tool_use_id"), None)
    return pend


def describe_input(name, inp):
    if isinstance(inp, dict) and isinstance(inp.get("command"), str):
        s = inp["command"]
    else:
        s = json.dumps(inp, ensure_ascii=False)
    s = SECRET_RE.sub("<che>", s)  # che trước khi cắt để không lộ nửa chuỗi
    return s.replace("\n", " ")[:120]


def needs_approval_hint(name, inp):
    if name in APPROVAL_TOOLS:
        return True
    if name == "Bash" and isinstance(inp, dict):
        cmd = str(inp.get("command", ""))
        return "$(" in cmd or "`" in cmd
    return False


def read_journal(path):
    """Trả về (started{key: (agentId, label)}, done{key})."""
    started, done = {}, set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "started":
                    started[d.get("key")] = (d.get("agentId"), d.get("label") or d.get("agentId"))
                elif d.get("type") == "result":
                    done.add(d.get("key"))
    except OSError:
        pass
    return started, done


def newest_mtime(run_dir):
    latest = 0.0
    for p in run_dir.iterdir():
        try:
            latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
    return latest


def wf_status(run_dir):
    f = run_dir.parent.parent.parent / "workflows" / (run_dir.name + ".json")
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh).get("status")
    except (OSError, ValueError):
        return None


def find_runs(target):
    """Run dir có journal.jsonl; session dir thì lấy mọi run trong subagents/workflows."""
    if (target / "journal.jsonl").exists():
        return [target], False
    base = target / "subagents" / "workflows"
    if base.is_dir():
        return sorted(p for p in base.iterdir() if (p / "journal.jsonl").exists()), True
    return [], False


def scan_run(run_dir, now, minutes, idle_minutes):
    """Trả về (alerts[], finished: bool)."""
    status = wf_status(run_dir)
    if status in TERMINAL:
        return [], True
    started, done = read_journal(run_dir / "journal.jsonl")
    open_agents = [(k, v) for k, v in started.items() if k not in done]
    if not open_agents and now.timestamp() - newest_mtime(run_dir) > QUIET_MIN_FINISH * 60:
        return [], True
    alerts = []
    hhmm = datetime.fromtimestamp(now.timestamp()).strftime("%H:%M")
    for _, (aid, label) in open_agents:
        f = run_dir / ("agent-%s.jsonl" % aid)
        if not f.exists():
            continue
        pend = pending_tools(f)
        stuck = None
        for ts, name, inp in sorted(pend.values(), key=lambda t: t[0]):
            wait = (now - ts).total_seconds() / 60
            if wait >= minutes:
                stuck = (name, inp, wait)
                break
        if stuck:
            name, inp, wait = stuck
            kind = "TREO"
        elif not pend and (now.timestamp() - f.stat().st_mtime) / 60 >= idle_minutes:
            name, inp, wait = "-", {}, (now.timestamp() - f.stat().st_mtime) / 60
            kind = "IM"
        else:
            continue
        line = "%s %s run=%s label=%s tool=%s chờ=%dp input=%s" % (
            hhmm, kind, run_dir.name, label, name, int(wait), describe_input(name, inp))
        if needs_approval_hint(name, inp):
            line += " [hop-duyet?]"
        alerts.append(line)
    return alerts, False


def scan_all(target, now, minutes, idle_minutes):
    runs, multi = find_runs(target)
    alerts, finished, active = [], [], 0
    for r in runs:
        if multi and wf_status(r) not in TERMINAL and now.timestamp() - newest_mtime(r) > STALE_HOURS * 3600:
            continue  # run bị bỏ rơi, không theo dõi
        a, fin = scan_run(r, now, minutes, idle_minutes)
        alerts += a
        if fin:
            finished.append(r.name)
        else:
            active += 1
    return alerts, finished, active, bool(runs)


def emit(lines, out):
    for ln in lines:
        print(ln, flush=True)
    if out and lines:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dò agent workflow treo.")
    ap.add_argument("target")
    ap.add_argument("--minutes", type=float, default=12)
    ap.add_argument("--idle-minutes", type=float, default=20)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=float, default=120)
    ap.add_argument("--max-hours", type=float, default=10)
    ap.add_argument("--out")
    ap.add_argument("--wait-new", type=float, default=15,
                    help="chế độ lặp: số phút chờ run mới xuất hiện trước khi thoát 2")
    a = ap.parse_args(argv)
    target = Path(a.target).expanduser()
    runs, multi = find_runs(target)
    if not target.is_dir() or (a.once and not runs):
        print("Không tìm thấy run nào (cần journal.jsonl) trong: %s" % target, file=sys.stderr)
        return 2
    # Chạy ngay sau khi launch: run mới có thể chưa có journal. Run đã xong từ trước
    # trong session bị bỏ qua, để không báo XONG giả cho run cũ.
    old = {r.name for r in runs if wf_status(r) in TERMINAL} if multi and not a.once else set()
    seen_active = False
    t0 = time.time()
    while True:
        now = datetime.now(timezone.utc)
        alerts, finished, active, _ = scan_all(target, now, a.minutes, a.idle_minutes)
        finished = [r for r in finished if r not in old]
        if alerts:
            emit(alerts, a.out)
            return 1
        if a.once:
            for r in finished:
                print("XONG run=%s" % r)
            return 0
        seen_active = seen_active or active > 0
        if active == 0 and (finished or seen_active):
            for r in finished:
                print("XONG run=%s" % r, flush=True)
            return 0
        if not seen_active and not finished and time.time() - t0 > a.wait_new * 60:
            emit(["%s KHONG-CO-RUN không thấy run mới sau %g phút" % (datetime.now().strftime("%H:%M"), a.wait_new)], a.out)
            return 2
        if time.time() - t0 > a.max_hours * 3600:
            msg = "%s QUA-GIO quá %g giờ, dừng theo dõi" % (datetime.now().strftime("%H:%M"), a.max_hours)
            emit([msg], a.out)
            return 3
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
