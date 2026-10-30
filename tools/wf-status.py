#!/usr/bin/env python3
"""wf-status: đọc dữ liệu workflow Claude Code và lint script workflow trước khi chạy.

Dùng cho skill web-lane-orchestration. Python 3 stdlib, không cần gói ngoài (lint syntax cần node nếu có).

  python3 tools/wf-status.py lint-script <script.js> [--args f.json] [--base DIR] [--json]
  python3 tools/wf-status.py tokens  <thư mục session | thư mục run | run id> [--by run|model|label] [--json]
  python3 tools/wf-status.py result  <label> <đích> [--max 6000]
  python3 tools/wf-status.py slots   <thư mục session> [--cap 10] [--active-min 30]
  python3 tools/wf-status.py stale   <đích> [--minutes 15]

Mã thoát: lint 1 khi có ERROR; result 3 khi chưa có result; slots 2 khi số slot >= cap.

Công thức tokens (hiệu chuẩn 24/10/2026 trên 3 run thật của một phiên):
  approx_total = tổng theo agent của ngữ cảnh lượt cuối = input + cache_creation + cache_read
  (lượt = một message.id, dòng cuối của id thắng; output không cộng vì đã nằm trong ngữ cảnh lượt sau).
  So với totalTokens trong wf_*.json:
    wf_b0de9016-138  1.901.432 vs 1.901.318  (-0,006%)
    wf_20e6ef10-539  2.418.720 vs 2.418.627  (-0,004%)
    wf_41656950-ff7  2.195.907 vs 2.195.829  (-0,004%)
  Công thức cũ "ngữ cảnh lượt cuối + output lượt cuối" lệch +1,7% / +0,9% / +6,4%.
  Các công thức cộng dồn mọi lượt (kể cả cache_read) lệch hàng chục lần, không dùng.
"""
import argparse
import bisect
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import OrderedDict
from pathlib import Path

DEFAULT_ROOT = os.path.expanduser("~/.claude/projects")
MODELS = {"sonnet", "opus", "haiku"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
NEGATION = ("không", "cấm", "do not", "never")
SECRET_RE = re.compile(r"(?i)(pass(?:word)?|token|secret|key)[\"']?\s*[=:]\s*\S+")


def redact(text):
    return SECRET_RE.sub("<che>", text)


def nfc(s):
    return unicodedata.normalize("NFC", s)


# ---------------------------------------------------------------- tìm run, đọc journal

def run_dirs(target, root=None):
    """Trả danh sách thư mục run từ thư mục session, thư mục run hoặc run id."""
    root = os.path.expanduser(root or DEFAULT_ROOT)
    p = Path(os.path.expanduser(target))
    if p.is_dir():
        wfdir = p / "subagents" / "workflows"
        if wfdir.is_dir():
            return sorted(d for d in wfdir.iterdir() if d.is_dir())
        if p.name == "workflows" and p.parent.name == "subagents":
            return sorted(d for d in p.iterdir() if d.is_dir())
        if (p / "journal.jsonl").exists() or glob.glob(str(p / "agent-*.jsonl")):
            return [p]
        return []
    found = glob.glob(os.path.join(root, "*", "*", "subagents", "workflows", target))
    return sorted(Path(f) for f in found if os.path.isdir(f))


def read_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def journal(run):
    """(started: list[dict], results: dict key -> result)."""
    started, results = [], {}
    for o in read_jsonl(run / "journal.jsonl"):
        if o.get("type") == "started":
            started.append(o)
        elif o.get("type") == "result":
            results[o.get("key")] = o.get("result")
    return started, results


def run_mtime(run):
    j = run / "journal.jsonl"
    return j.stat().st_mtime if j.exists() else run.stat().st_mtime


def agent_file(run, agent_id):
    return run / ("agent-%s.jsonl" % agent_id)


def agent_meta(path):
    try:
        return json.loads(Path(str(path)[:-6] + ".meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def wf_summary(run):
    f = run.parent.parent.parent / "workflows" / (run.name + ".json")
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def open_agents(run):
    """Agent đã started chưa có result: list[(label, agentId, path)]."""
    started, results = journal(run)
    return [(s.get("label") or s.get("agentId"), s.get("agentId"), agent_file(run, s.get("agentId")))
            for s in started if s.get("key") not in results]


# ---------------------------------------------------------------- tokens

def agent_turns(path):
    """Các lượt assistant đã dedupe theo message.id (dòng cuối của id thắng), giữ thứ tự xuất hiện."""
    turns = OrderedDict()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                m = o.get("message") or {}
                if o.get("type") != "assistant" or not isinstance(m.get("usage"), dict):
                    continue
                turns[m.get("id") or o.get("uuid") or str(len(turns))] = (m.get("model") or "?", m["usage"])
    except OSError:
        pass
    return list(turns.values())


def ctx(u):
    return sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def new_row():
    return dict(agents=0, turns=0, input=0, cache_creation=0, cache_read=0, output=0, approx_total=0)


def add_turns(row, turns, by_model=None):
    for model, u in turns:
        if by_model is not None and model != by_model:
            continue
        row["turns"] += 1
        row["input"] += u.get("input_tokens") or 0
        row["cache_creation"] += u.get("cache_creation_input_tokens") or 0
        row["cache_read"] += u.get("cache_read_input_tokens") or 0
        row["output"] += u.get("output_tokens") or 0


def token_rows(runs, by):
    rows = OrderedDict()
    for run in runs:
        wf = wf_summary(run)
        _, _ = journal(run)
        for f in sorted(run.glob("agent-*.jsonl")):
            turns = agent_turns(f)
            if not turns:
                continue
            last_model, last_u = turns[-1]
            if by == "run":
                keys = [run.name]
            elif by == "label":
                keys = [agent_meta(f).get("description") or f.stem[6:]]
            else:
                keys = sorted({m for m, _ in turns})
            for k in keys:
                row = rows.setdefault(k, new_row())
                add_turns(row, turns, by_model=k if by == "model" else None)
                if by != "model" or k == last_model:
                    row["agents"] += 1
                    row["approx_total"] += ctx(last_u)
            if by == "run":
                rows[run.name]["wf_total"] = wf.get("totalTokens")
        if by == "run" and run.name in rows:
            rows[run.name]["wf_total"] = wf.get("totalTokens")
    return rows


def cmd_tokens(a):
    runs = run_dirs(a.target, a.projects_root)
    if not runs:
        print("Không tìm thấy run cho: %s" % a.target, file=sys.stderr)
        return 4
    rows = token_rows(runs, a.by)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    cols = ["agents", "turns", "input", "cache_creation", "cache_read", "output", "approx_total"]
    if a.by == "run":
        cols.append("wf_total")
    head = [a.by] + cols
    table = [head]
    tot = new_row()
    for k, r in rows.items():
        table.append([k] + [fmt(r.get(c)) for c in cols])
        for c in tot:
            tot[c] += r.get(c) or 0
    if len(rows) > 1:
        table.append(["TỔNG"] + [fmt(tot.get(c)) if c != "wf_total" else "" for c in cols])
    widths = [max(len(str(r[i])) for r in table) for i in range(len(head))]
    for i, r in enumerate(table):
        print("  ".join(str(c).rjust(widths[j]) if j else str(c).ljust(widths[j]) for j, c in enumerate(r)))
    print("approx_total = tổng theo agent của ngữ cảnh lượt cuối (input+cache_creation+cache_read), ước từ agent jsonl.")
    if a.by == "run":
        print("wf_total = totalTokens trong workflows/wf_*.json (số của hệ thống); trống nếu không có file đó.")
    return 0


def fmt(v):
    return "" if v is None else "{:,}".format(v).replace(",", ".")


# ---------------------------------------------------------------- result, slots, stale

def cmd_result(a):
    runs = sorted(run_dirs(a.target, a.projects_root), key=run_mtime, reverse=True)
    if not runs:
        print("Không tìm thấy run cho: %s" % a.target, file=sys.stderr)
        return 4
    want = a.label
    data = [(r, *journal(r)) for r in runs]
    hits = [(r, s, res) for r, st, res in data for s in st if s.get("label") == want]
    if not hits:
        hits = [(r, s, res) for r, st, res in data for s in st if want in (s.get("label") or "")]
    shown = 0
    for run, s, results in hits:
        if s.get("key") not in results:
            continue
        text = json.dumps(results[s["key"]], ensure_ascii=False, separators=(",", ":"))
        if len(text) > a.max:
            text = text[:a.max] + "…(cắt, còn %d ký tự)" % (len(text) - a.max)
        print("# run %s label %s" % (run.name, s.get("label")))
        print(text)
        shown += 1
    if not shown:
        print("chưa có result")
        return 3
    return 0


def cmd_slots(a):
    cutoff = time.time() - a.active_min * 60
    active = []
    for run in run_dirs(a.target, a.projects_root):
        for label, _, f in open_agents(run):
            if f.exists() and f.stat().st_mtime >= cutoff:
                active.append("%s (%s)" % (label, run.name))
    print("slot đang dùng: %d (cap %d)" % (len(active), a.cap))
    for x in active:
        print("- " + x)
    return 2 if len(active) >= a.cap else 0


def last_tool(path):
    """(tên tool, input đã che secret, đang chờ tool_result) của tool_use cuối; None nếu chưa có."""
    size = path.stat().st_size
    for tail in (512 * 1024, None):
        with open(path, "rb") as fh:
            if tail and size > tail:
                fh.seek(size - tail)
                fh.readline()
            lines = fh.read().decode("utf-8", "replace").splitlines()
        uses, done = [], set()
        for line in lines:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            c = (o.get("message") or {}).get("content")
            if not isinstance(c, list):
                continue
            for x in c:
                if not isinstance(x, dict):
                    continue
                if x.get("type") == "tool_use":
                    uses.append(x)
                elif x.get("type") == "tool_result":
                    done.add(x.get("tool_use_id"))
        if uses or not tail or size <= tail:
            break
    if not uses:
        return None
    u = uses[-1]
    inp = u.get("input") or {}
    text = inp.get("command") if isinstance(inp.get("command"), str) else json.dumps(inp, ensure_ascii=False)
    text = redact(text).replace("\n", " ")[:160]
    return u.get("name"), text, u.get("id") not in done


def cmd_stale(a):
    now = time.time()
    n = 0
    for run in run_dirs(a.target, a.projects_root):
        for label, _, f in open_agents(run):
            age = (now - f.stat().st_mtime) / 60 if f.exists() else None
            if age is not None and age <= a.minutes:
                continue
            n += 1
            tool = last_tool(f) if f.exists() else None
            when = "không có file" if age is None else "%d phút" % age
            if tool:
                print("%s | %s | %s: %s | chờ tool_result: %s" % (label, when, tool[0], tool[1], "có" if tool[2] else "không"))
            else:
                print("%s | %s | chưa có tool_use" % (label, when))
    if not n:
        print("không có agent treo quá %d phút" % a.minutes)
    return 0


# ---------------------------------------------------------------- lint: quét JS

class Scan:
    """Quét nguồn JS: che comment và nội dung template; gom template literal (dòng, biểu thức)."""

    def __init__(self, src):
        self.src = src
        self.n = len(src)
        self.masked = list(src)
        self.nl = [i for i, c in enumerate(src) if c == "\n"]
        self.templates = []
        self.comments = []
        self.code(0, False)
        self.code_text = "".join(self.masked)

    def lineno(self, i):
        return bisect.bisect_left(self.nl, i) + 1

    def blank(self, a, b):
        for k in range(a, min(b, self.n)):
            if self.masked[k] != "\n":
                self.masked[k] = " "

    def skip_str(self, i):
        q = self.src[i]
        i += 1
        while i < self.n and self.src[i] != q and self.src[i] != "\n":
            i += 2 if self.src[i] == "\\" else 1
        return i + 1

    def skip_regex(self, i):
        i += 1
        in_class = False
        while i < self.n and self.src[i] != "\n":
            c = self.src[i]
            if c == "\\":
                i += 2
                continue
            if c == "[":
                in_class = True
            elif c == "]":
                in_class = False
            elif c == "/" and not in_class:
                return i + 1
            i += 1
        return i

    def code(self, i, stop_at_brace):
        depth, prev = 0, ""
        src, n = self.src, self.n
        while i < n:
            c = src[i]
            nx = src[i + 1:i + 2]
            if c == "/" and nx == "/":
                j = src.find("\n", i)
                j = n if j < 0 else j
                self.blank(i, j)
                self.comments.append((i, j))
                i = j
                continue
            if c == "/" and nx == "*":
                j = src.find("*/", i + 2)
                j = n if j < 0 else j + 2
                self.blank(i, j)
                self.comments.append((i, j))
                i = j
                continue
            if c in "'\"":
                i = self.skip_str(i)
                prev = '"'
                continue
            if c == "`":
                i = self.template(i)
                prev = "`"
                continue
            if c == "/" and (prev in ("", "(", ",", "=", ":", "[", "!", "&", "|", "?", "{", "}", ";")
                             or src[:i].rstrip().endswith("return")):
                i = self.skip_regex(i)
                prev = "/"
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                if depth == 0 and stop_at_brace:
                    return i
                depth -= 1
            if not c.isspace():
                prev = c
            i += 1
        return i

    def template(self, i):
        start = i
        src = self.src
        line0 = self.lineno(i)
        cur = line0
        lines, raw, exprs = [[[], line0]], [], []
        i += 1
        while i < self.n:
            c = src[i]
            if c == "\\":
                e = src[i + 1:i + 2]
                i += 2
                if e == "n":
                    lines.append([[], cur])
                    raw.append("\n")
                elif e == "\n":
                    cur += 1
                else:
                    lines[-1][0].append(e)
                    raw.append(e)
                continue
            if c == "`":
                break
            if c == "$" and src[i + 1:i + 2] == "{":
                j = self.code(i + 2, True)
                exprs.append((src[i + 2:j], self.lineno(i + 2)))
                raw.append("${" + src[i + 2:j] + "}")
                cur = self.lineno(j)
                i = j + 1
                continue
            if c == "\n":
                cur += 1
                lines.append([[], cur])
                raw.append("\n")
            else:
                lines[-1][0].append(c)
                raw.append(c)
            i += 1
        self.blank(start + 1, i)
        before = "".join(self.masked[:start]).rstrip()
        self.templates.append(dict(
            line=line0, exprs=exprs, raw="".join(raw),
            lines=[("".join(t), ln) for t, ln in lines],
            is_common=bool(re.search(r"\bCOMMON\s*=$", before)),
        ))
        return i + 1


def match_close(code, i):
    """Chỉ số ngoặc đóng khớp với ngoặc mở tại i, bỏ qua chuỗi '...' và "...". -1 nếu thiếu."""
    pairs = {"(": ")", "{": "}", "[": "]"}
    stack = []
    k = i
    while k < len(code):
        c = code[k]
        if c in "'\"":
            k += 1
            while k < len(code) and code[k] != c and code[k] != "\n":
                k += 2 if code[k] == "\\" else 1
        elif c in pairs:
            stack.append(pairs[c])
        elif c in ")}]":
            if not stack or stack.pop() != c:
                return -1
            if not stack:
                return k
        k += 1
    return -1


def split_top(text):
    """Cắt chuỗi theo dấu phẩy ở độ sâu 0."""
    parts, depth, cur, k = [], 0, [], 0
    while k < len(text):
        c = text[k]
        if c in "'\"":
            j = k + 1
            while j < len(text) and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            cur.append(text[k:j + 1])
            k = j + 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        k += 1
    if "".join(cur).strip():
        parts.append("".join(cur))
    return parts


def function_span(code, name):
    """Khoảng (đầu, cuối) thân hàm `name` nếu tìm thấy."""
    m = re.search(r"function\s+%s\s*\(" % name, code) or re.search(r"(?:const|let|var)\s+%s\s*=" % name, code)
    if not m:
        return None
    k = m.end() - 1 if m.group(0).endswith("(") else m.end()
    if m.group(0).endswith("("):
        k = match_close(code, k)
        if k < 0:
            return None
    brace = code.find("{", k)
    if brace < 0:
        return None
    end = match_close(code, brace)
    return (m.start(), end if end > 0 else len(code))


class Findings:
    def __init__(self):
        self.items = []

    def add(self, level, code, line, msg):
        self.items.append(dict(level=level, code=code, line=line, msg=msg))


def lint(path, args_file=None, base=None):
    f = Findings()
    src = Path(path).read_text(encoding="utf-8")
    sc = Scan(src)
    code = sc.code_text
    args_data = None
    if args_file:
        try:
            args_data = json.loads(Path(args_file).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            f.add("ERROR", "args", 1, "File args không đọc được hoặc JSON hỏng (%s): sửa file rồi chạy lại" % e)
        else:
            if not isinstance(args_data, dict):
                f.add("ERROR", "args", 1, "File args phải là một object JSON")
                args_data = None
    if base is None and isinstance(args_data, dict) and isinstance(args_data.get("base"), str):
        base = args_data["base"]

    lint_args(f, sc, code, args_data, args_file)
    lint_templates(f, sc, base)
    lint_calls(f, sc, code)
    lint_structure(f, sc, code, src)
    lint_syntax(f, src, code)
    f.items.sort(key=lambda x: (x["line"], x["code"]))
    return f.items


def used_args(sc, code):
    keys = {}
    texts = [(code, None)] + [(e, ln) for t in sc.templates for e, ln in t["exprs"]]
    for text, ln in texts:
        for m in re.finditer(r"\bargs\??\.(\w+)", text):
            keys.setdefault(m.group(1), ln or sc.lineno(m.start()))
        for m in re.finditer(r"\bargs\[\s*['\"](\w+)['\"]\s*\]", text):
            keys.setdefault(m.group(1), ln or sc.lineno(m.start()))
        for m in re.finditer(r"\{([^{}]*)\}\s*=\s*args\b", text):
            for part in m.group(1).split(","):
                k = part.split(":")[0].split("=")[0].strip()
                if k.isidentifier():
                    keys.setdefault(k, ln or sc.lineno(m.start()))
    return keys


def walk_values(v, trail=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from walk_values(x, trail + "." + k if trail else k)
    elif isinstance(v, list):
        yield trail, v
        for i, x in enumerate(v):
            yield from walk_values(x, "%s[%d]" % (trail, i))
    else:
        yield trail, v


def lint_args(f, sc, code, data, args_file):
    keys = used_args(sc, code)
    if not keys:
        return
    if not args_file:
        f.add("WARN", "args", min(keys.values()), "Script dùng args.%s nhưng chưa có --args: không kiểm được. Thêm --args <file.json>" % sorted(keys)[0])
        return
    if data is None:
        return
    for k, ln in sorted(keys.items(), key=lambda x: x[1]):
        if k not in data:
            f.add("ERROR", "args", ln, "Script dùng args.%s nhưng file args không có khoá '%s': thêm khoá này" % (k, k))
    for trail, v in walk_values(data):
        if isinstance(v, list) and not v:
            f.add("ERROR", "args", 1, "args.%s là mảng rỗng: điền ít nhất một phần tử" % trail)
        elif isinstance(v, str) and re.search(r"<[^<>]*>", v):
            f.add("ERROR", "args", 1, "args.%s còn chỗ chưa điền %s: thay bằng giá trị thật" % (trail, re.search(r"<[^<>]*>", v).group(0)))


def lint_templates(f, sc, base):
    common_size = 0
    for t in sc.templates:
        if t["is_common"]:
            common_size = len("\n".join(x for x, _ in t["lines"]).encode("utf-8"))
    for t in sc.templates:
        # forbidden + stringify
        for text, ln in t["lines"]:
            check_forbidden(f, nfc(text), ln)
        for expr, ln in t["exprs"]:
            if "JSON.stringify(" in expr:
                f.add("ERROR", "stringify", ln, "Không nhúng JSON vào prompt: truyền đường dẫn ket-qua.json thay vì nhúng JSON")
        # size
        size = len("\n".join(x for x, _ in t["lines"]).encode("utf-8"))
        if any(e.strip() == "COMMON" for e, _ in t["exprs"]):
            size += common_size
        if size > 12 * 1024:
            f.add("ERROR", "size", t["line"], "Prompt ước %d KB, vượt 12 KB: cắt bớt hoặc chuyển nội dung dài sang file rồi chỉ đường dẫn" % (size // 1024))
        elif size > 8 * 1024:
            f.add("WARN", "size", t["line"], "Prompt ước %.1f KB, vượt 8 KB: nên rút gọn" % (size / 1024))
        if t["is_common"]:
            lint_paths(f, t, base)


def check_forbidden(f, line, ln):
    low = line.lower()
    if any(w in low for w in NEGATION):
        return
    s = re.sub(r"^[\s>*•`\-$]+|^\d+[.)]\s*", "", line)
    rules = [
        (r"ArtifactData", "ArtifactData", "Prompt có ArtifactData: agent con không được dùng, xoá hoặc thêm câu cấm"),
        (r"\bMonitor\b", "Monitor", "Prompt có Monitor: agent con không dùng Monitor, xoá hoặc thêm câu cấm"),
        (r"\brm\s+-\w*r\w*f|\brm\s+-\w*f\w*r", "rm -rf", "Prompt có rm -rf: dùng lệnh xoá có đích cụ thể, hoặc bỏ"),
        (r"\bpkill\s+(?:-\w+\s+)*-f\b", "pkill -f", "Prompt có pkill -f: dùng kill theo PID cụ thể"),
        (r"^(?:.*?[;&|(]\s*)?sleep\b", "sleep", "Dòng lệnh sleep: không chờ bằng sleep, dùng run_in_background hoặc kiểm đúng một lần"),
        (r"^(?:.*?[;&|(]\s*)?until\s", "until", "Dòng lệnh until: không viết vòng chờ, kiểm đúng một lần"),
        (r"^(?:.*?[;&|(]\s*)?while\b.*\bsleep\b", "while-sleep", "Vòng while ... sleep: không viết vòng chờ"),
        (r"(?<![\w.-])g?timeout\s", "timeout", "timeout/gtimeout không có trên macOS: dùng perl -e 'alarm N; exec @ARGV'"),
    ]
    for pat, name, msg in rules:
        if re.search(pat, s if name in ("sleep", "until", "while-sleep") else line):
            f.add("ERROR", "forbidden", ln, msg)


def lint_paths(f, t, base):
    raw = t["raw"]
    token = "\0BASE\0"
    text = raw.replace("${B}", token).replace("${args.base}", token)
    pending_base_warn = token in text and not base
    seen = set()
    for m in re.finditer(r"(?:\0BASE\0|~/|/Users/)[^\s\"'`]*", text):
        cand = re.sub(r"[.,;:)\]]+$", "", m.group(0))
        ln = t["line"] + text.count("\n", 0, m.start())
        if cand in seen:
            continue
        seen.add(cand)
        if "<" in cand or "${" in cand or (token in cand and not base):
            if token not in cand:
                f.add("WARN", "paths", ln, "Đường dẫn chưa điền: %s" % cand.replace(token, "${B}"))
            continue
        full = cand.replace(token, base or "")
        rest = text[m.end():]
        if token in cand:
            ok = path_exists(full)
        else:
            ok = path_exists(full) or any(path_exists(full + ext) for ext in word_extensions(rest))
        # Khoá, log, pid tạo lúc chạy: thư mục cha có là đủ.
        clean = re.sub(r"[/.,;:)\]]+$", "", full)
        if not ok and re.search(r"\.(lock|lockdir|log|pid|queue|queue-done)$", clean):
            ok = path_exists(os.path.dirname(os.path.expanduser(clean)))
        if not ok:
            f.add("ERROR", "paths", ln, "Đường dẫn không tồn tại: %s. Sửa đường dẫn hoặc tạo file" % full)
    if pending_base_warn:
        f.add("WARN", "paths", t["line"], "COMMON dùng ${B} nhưng chưa có --base: chưa kiểm đường dẫn dưới thư mục gốc")


def path_exists(p):
    p = re.sub(r"[.,;:)\]]+$", "", p)
    return os.path.exists(os.path.expanduser(p))


def word_extensions(rest, limit=8):
    """Phần nối thêm cho đường dẫn có dấu cách không đặt trong ngoặc."""
    exts, cur = [], ""
    for w in re.findall(r"\s+[^\s\"'`]+", rest)[:limit]:
        cur += w
        exts.append(cur)
    return exts


def lint_calls(f, sc, code):
    goi_span = function_span(code, "goi")
    for m in re.finditer(r"(?<![\w.$])(agent|goi)\s*\(", code):
        name = m.group(1)
        if re.search(r"function\s+$", code[:m.start()]):
            continue
        if name == "agent" and goi_span and goi_span[0] <= m.start() <= goi_span[1]:
            continue
        end = match_close(code, m.end() - 1)
        if end < 0:
            continue
        ln = sc.lineno(m.start())
        args = split_top(code[m.end():end])
        if any("..." in a for a in args):
            continue
        if len(args) < 2:
            f.add("ERROR", "model-effort", ln, "%s( thiếu object option: thêm { label, model, effort }" % name)
            continue
        opt = args[-1].strip()
        if not opt.startswith("{"):
            continue
        entries = {}
        for e in split_top(opt[1:opt.rfind("}")]):
            e = e.strip()
            km = re.match(r"(\w+|'[^']*'|\"[^\"]*\")\s*(?::(.*))?$", e, re.S)
            if km:
                entries[km.group(1).strip("'\"")] = (km.group(2) if km.group(2) is not None else km.group(1)).strip()
        for key, allowed in (("model", MODELS), ("effort", EFFORTS)):
            if key not in entries:
                f.add("ERROR", "model-effort", ln, "%s( thiếu %s: thêm %s: <%s>" % (name, key, key, "|".join(sorted(allowed))))
                continue
            lm = re.match(r"^(['\"])(.*)\1$", entries[key], re.S)
            if lm and lm.group(2) not in allowed:
                f.add("ERROR", "model-effort", ln, "%s: '%s' không hợp lệ, chọn một trong %s" % (key, lm.group(2), "|".join(sorted(allowed))))


def lint_structure(f, sc, code, src):
    if not re.search(r"function\s+goi\s*\(|(?:const|let|var)\s+goi\s*=", code):
        f.add("ERROR", "goi", 1, "Thiếu hàm goi() có cờ dừng hạn mức: thêm function goi(...) bọc agent()")
    flags = re.findall(r"\breadOnly\s*:\s*(\w+)", code)
    exempt = bool(flags) and all(x == "true" for x in flags)
    nocomment = nocomment_text(sc)
    if "NGUỒN PHÊ DUYỆT" not in nfc(nocomment) and not exempt:
        f.add("ERROR", "approval", 1, "Thiếu mục 'NGUỒN PHÊ DUYỆT' trong prompt: thêm ngày, nơi duyệt và phạm vi (lane chỉ đọc thì đặt readOnly: true)")
    for m in re.finditer(r"parallel\(\s*LANES\.map", code):
        f.add("WARN", "pool", sc.lineno(m.start()), "Dùng pool(LANES, N) thay cho parallel(LANES.map(...)) để giới hạn số agent chạy cùng lúc")
    for m in re.finditer(r"\bMAX_AGENTS\s*[=:]\s*(\d+)", code):
        if int(m.group(1)) > 6:
            f.add("WARN", "pool", sc.lineno(m.start()), "MAX_AGENTS = %s vượt 6 agent mỗi workflow: hạ xuống 6" % m.group(1))


def nocomment_text(sc):
    """Nguồn đã bỏ comment, giữ nguyên chuỗi và template."""
    out = list(sc.src)
    for a, b in sc.comments:
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "
    return "".join(out)


def lint_syntax(f, src, code):
    params = ["agent", "parallel", "pipeline", "phase", "log", "args", "budget", "workflow", "goi"]
    params = [p for p in params if not re.search(r"(?:const|let|var|function)\s+%s\b" % p, code)]
    body = re.sub(r"\bexport\s+const\s+meta\b", "const meta", src)
    js = "async function __wf(%s) { %s\n}\n" % (", ".join(params), body)
    with tempfile.TemporaryDirectory(prefix="wf-lint-") as d:
        p = os.path.join(d, "script.cjs")
        Path(p).write_text(js, encoding="utf-8")
        try:
            r = subprocess.run(["node", "--check", p], capture_output=True, text=True, timeout=60)
        except FileNotFoundError:
            f.add("WARN", "syntax", 1, "Máy không có node: bỏ qua kiểm cú pháp")
            return
        except subprocess.TimeoutExpired:
            f.add("WARN", "syntax", 1, "node --check quá 60 giây: bỏ qua kiểm cú pháp")
            return
    if r.returncode != 0:
        err = r.stderr
        lm = re.search(r"script\.cjs:(\d+)", err)
        msg = next((x for x in err.splitlines() if "Error" in x), "lỗi cú pháp")
        f.add("ERROR", "syntax", int(lm.group(1)) if lm else 1, "Cú pháp JS sai (%s): sửa theo dòng này" % msg.strip())


def cmd_lint(a):
    if not os.path.isfile(a.script):
        print("Không thấy file: %s" % a.script, file=sys.stderr)
        return 4
    items = lint(a.script, a.args, a.base)
    if a.json:
        print(json.dumps(items, ensure_ascii=False, indent=1))
    else:
        for x in items:
            print("%s %s dòng %d: %s" % (x["level"], x["code"], x["line"], x["msg"]))
        if not items:
            print("OK: không có lỗi hoặc cảnh báo")
    return 1 if any(x["level"] == "ERROR" for x in items) else 0


# ---------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(prog="wf-status", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    root = argparse.ArgumentParser(add_help=False)
    root.add_argument("--projects-root", default=None, help="mặc định ~/.claude/projects (dùng khi tìm theo run id)")

    s = sub.add_parser("lint-script", help="lint tĩnh script workflow")
    s.add_argument("script")
    s.add_argument("--args", help="file JSON args sẽ truyền khi chạy")
    s.add_argument("--base", help="thư mục thay cho ${B} và ${args.base}")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("tokens", parents=[root], help="bảng token theo run, model hoặc label")
    s.add_argument("target")
    s.add_argument("--by", choices=["run", "model", "label"], default="run")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_tokens)

    s = sub.add_parser("result", parents=[root], help="in result của agent theo label")
    s.add_argument("label")
    s.add_argument("target")
    s.add_argument("--max", type=int, default=6000)
    s.set_defaults(fn=cmd_result)

    s = sub.add_parser("slots", parents=[root], help="đếm agent đang chạy")
    s.add_argument("target")
    s.add_argument("--cap", type=int, default=10)
    s.add_argument("--active-min", type=int, default=30)
    s.set_defaults(fn=cmd_slots)

    s = sub.add_parser("stale", parents=[root], help="agent started chưa có result và file không ghi")
    s.add_argument("target")
    s.add_argument("--minutes", type=int, default=15)
    s.set_defaults(fn=cmd_stale)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
