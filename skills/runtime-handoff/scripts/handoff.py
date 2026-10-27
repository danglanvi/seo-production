#!/usr/bin/env python3
"""Create and verify a source-pinned handoff, check HANDOFF.md, stamp its status line, build a new-session prompt,
prepare an account switch or a usage-limit checkpoint, run the overnight PLAN.md.
Python standard library only. Set HANDOFF_NOW="YYYY-MM-DD HH:MM" to fix the clock (tests only)."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys

BLOCKED = {"BRAIN", ".agent-secrets", ".env", "auth.json", ".credentials.json", ".stversions"}
TIME_RE = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?:/(\d{4}))?[ ,]+(?:lúc\s+)?(\d{1,2}):(\d{2})")
SLACK = dt.timedelta(minutes=2)


def now():
    """Giờ máy theo múi giờ local, làm tròn phút. HANDOFF_NOW chỉ dùng cho test."""
    fixed = os.environ.get("HANDOFF_NOW")
    if fixed:
        return dt.datetime.strptime(fixed, "%Y-%m-%d %H:%M")
    return dt.datetime.now().replace(second=0, microsecond=0)


def stamp_text(when=None):
    return (when or now()).strftime("%d/%m/%Y %H:%M")


def parse_times(text, default_year=None):
    """Trả danh sách (chuỗi gốc, datetime hoặc None, có_năm). Mốc sai lịch trả datetime None."""
    out = []
    for m in TIME_RE.finditer(text):
        d, mo, y, h, mi = m.groups()
        year = int(y) if y else (default_year or now().year)
        try:
            when = dt.datetime(year, int(mo), int(d), int(h), int(mi))
        except ValueError:
            when = None
        out.append((m.group(0).strip(), when, bool(y)))
    return out


def digest(path):
    path = path.resolve()
    if any(p in BLOCKED or p.startswith(".env.") or "sync-conflict" in p for p in path.parts):
        raise ValueError("Source is outside the portable handoff boundary")
    if not path.is_file():
        raise ValueError("Source file does not exist")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(spec_path, output):
    spec = json.loads(spec_path.read_text())
    for field in ["objective", "entity", "target_runtime"]:
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ValueError("Missing field: " + field)
    if spec["target_runtime"] not in {"claude", "codex", "antigravity", "hermes"}:
        raise ValueError("Unknown target runtime")
    result = {k: spec[k] for k in ["objective", "entity", "target_runtime"]}
    for field in ["completed", "decisions", "pending", "blockers"]:
        value = spec.get(field, [])
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("Expected a string list: " + field)
        result[field] = value
    result.update(schema_version=1, created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                  authorization="Historical decisions only; destination runtime must check current authority.", sources=[])
    for source in spec.get("sources", []):
        p = Path(source["path"]).expanduser()
        p = p if p.is_absolute() else spec_path.parent / p
        result["sources"].append({"path": str(p.resolve()), "purpose": source["purpose"], "sha256": digest(p)})
    if not result["sources"]:
        raise ValueError("At least one source is required")
    if output.suffix != ".md":
        raise ValueError("Output must end in .md")
    machine = output.with_suffix(".json")
    if output.exists() or machine.exists():
        raise ValueError("Output exists; choose the next version")
    lines = ["# Bàn giao công việc", "", result["objective"], "",
             f"Entity: {result['entity']} · Runtime nhận: {result['target_runtime']}", ""]
    for key, title in [("completed", "Đã hoàn thành"), ("decisions", "Quyết định đã ghi nhận"),
                       ("pending", "Bước tiếp theo"), ("blockers", "Blocker")]:
        lines += ["## " + title, ""] + (["- " + x for x in result[key]] or ["Chưa ghi nhận."]) + [""]
    lines += ["## Nguồn cần đọc", ""]
    for s in result["sources"]:
        lines += [f"- [{Path(s['path']).name}](<{s['path']}>) — {s['purpose']} · SHA256 `{s['sha256']}`"]
    lines += ["", "Quyết định ghi ở trên không tự cấp quyền gửi, publish hay truy cập dữ liệu mới. Runtime nhận đọc luật tại đích và verify nguồn trước khi tiếp tục.", ""]
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects against another task choosing the same version.
    with machine.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with output.open("x", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return {"markdown": str(output.resolve()), "json": str(machine.resolve()), "sources": len(result["sources"])}


def verify(path):
    doc = json.loads(path.read_text())
    findings = []
    if doc.get("schema_version") != 1 or not doc.get("sources"):
        raise ValueError("Invalid handoff contract")
    for source in doc["sources"]:
        try:
            status = "unchanged" if digest(Path(source["path"])) == source["sha256"] else "changed"
        except (ValueError, OSError):
            status = "missing_or_disallowed"
        findings.append({"path": source["path"], "status": status})
    return findings


SECTIONS = ["Trạng thái", "Đã xong", "Bước tiếp", "Chờ Lead quyết", "Bẫy đã gặp"]
NIGHT = ["Mục tiêu", "Được làm", "Không được làm", "Hàng việc", "Việc local-only", "Giờ kiểm kế tiếp", "Lịch đang sống",
         "Heartbeat", "Điều kiện dừng", "Chờ Lead", "Nhật ký đêm"]
# Tool phải có người duyệt: trong đêm không ai bấm, phiên treo (đêm 18 sang 19/10/2026 trống 500 phút).
RISKY = [("ArtifactData", re.compile(r"ArtifactData", re.I)),
         ("Artifact publish", re.compile(r"Artifact[ _-]*publish|publish[^\n]{0,20}artifact", re.I)),
         ("Monitor có $(", re.compile(r"Monitor[^\n]*\$\(", re.I)),
         ("launch Workflow", re.compile(r"(?:launch|khởi chạy|mở)\s+Workflow|Workflow\s+launch", re.I))]
TRIED_RE = re.compile(r"Đã thử lúc\s+\d{1,2}[:h]\d{2}[^\n]*khi Lead còn thức", re.I)
NEGATED_RE = re.compile(r"\b(?:không|cấm|tránh)\s+(?:gọi|dùng|chạy|launch)", re.I)


def sections(text):
    """Map tiêu đề ## / ### (bỏ phần sau dấu ':' hoặc '(') sang nội dung."""
    out, key = {}, None
    for line in text.splitlines():
        m = re.match(r"#{2,3}\s+(.+?)\s*$", line)
        if m:
            key = re.split(r"[:(—]", m.group(1))[0].strip()
            out[key] = []
        elif key:
            out[key].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def find_path(token, start):
    if token.startswith("~"):
        return Path(token).expanduser().exists()
    home = Path.home()
    for base in [start, *start.parents]:
        if (base / token).exists():
            return True
        if base == home:
            break
    return False


RESUME_RE = re.compile(r"resumeFromRunId|resume\w*[^\n]{0,40}\bwf_[0-9a-f]", re.I)


def time_errors(body):
    """Mốc giờ trong Trạng thái phải có năm và không nằm sau giờ máy."""
    errors = []
    for raw, when, has_year in parse_times(body):
        if not has_year:
            errors.append(f"mốc giờ '{raw}' thiếu năm: chạy `handoff.py stamp` để lấy giờ máy")
        elif when is None:
            errors.append(f"mốc giờ '{raw}' không phải ngày giờ hợp lệ")
        elif when > now() + SLACK:
            errors.append(f"mốc giờ '{raw}' ở tương lai so với giờ máy {stamp_text()}: chạy `handoff.py stamp`")
    return errors


def check(path):
    path = path.resolve()
    text = path.read_text(encoding="utf-8")
    sec, errors, warnings = sections(text), [], []
    n = len(text.splitlines())
    if n > 60:
        errors.append(f"{n} dòng, quá 60")
    for s in SECTIONS:
        if s not in sec:
            errors.append(f"thiếu mục '{s}'")
    if "Trạng thái" in sec:
        body = sec["Trạng thái"]
        if not re.search(r"\d{1,2}/\d{1,2}/\d{4}", body):
            errors.append("mục Trạng thái thiếu ngày dd/mm/yyyy")
        errors += time_errors(body)
        flat = " ".join(body.split())
        if len([x for x in re.split(r"(?<=[.!?])\s+", flat) if x]) > 3:
            warnings.append("mục Trạng thái dài hơn 3 câu: sửa đè thành một đoạn ngắn")
    for name in ["Đã xong", "Bẫy đã gặp"]:
        for raw, when, _ in parse_times(sec.get(name, "")):
            if when and when > now() + SLACK:
                warnings.append(f"mục {name} có mốc giờ ở tương lai: {raw}")
    if RESUME_RE.search(text):
        warnings.append("HANDOFF ghi resume workflow (wf_ hoặc resumeFromRunId): resume chỉ chạy trong cùng phiên. Ghi script đã chép vào repo và bước chạy lại")
    for tok in re.findall(r"`([^`\n]+)`", text):
        if re.search(r"[<>{}*$|=]|\s--?\w|^[/@]|^https?:", tok) or not re.search(r"/.*\.(md|json|jsonl|tsv|csv|py|html|php|mjs|js|sh)$", tok):
            continue
        if " " in tok and "/" not in tok.split(" ")[0]:
            continue
        if not find_path(tok, path.parent):
            warnings.append(f"không thấy file: {tok}")
    return {"file": str(path), "lines": n, "errors": errors, "warnings": warnings[:20]}


def bullets(block, limit=8):
    items = [l.strip()[2:].strip() for l in block.splitlines() if re.match(r"\s*(?:[-*]|\d+\.)\s", l)]
    items = items or [l.strip() for l in block.splitlines() if l.strip()]
    return [re.sub(r"^\d+\.\s*", "", x) for x in items[:limit]]


def stamp(path, note, write=False, drop_lanes=False):
    """Ghi đè mục Trạng thái bằng 'dd/mm/yyyy HH:MM: <note>' theo giờ máy, giữ các dòng `Lane:` trừ khi drop_lanes. Mặc định chỉ in kết quả."""
    path = path.resolve()
    note = " ".join(note.split())
    if not note:
        raise ValueError("Cần --note không rỗng")
    lines = path.read_text(encoding="utf-8").splitlines()
    heads = [(i, re.split(r"[:(—]", m.group(1))[0].strip()) for i, l in enumerate(lines) if (m := re.match(r"#{2,3}\s+(.+?)\s*$", l))]
    pos = [k for k, (_, name) in enumerate(heads) if name == "Trạng thái"]
    if not pos:
        raise ValueError("HANDOFF thiếu mục 'Trạng thái'")
    start = heads[pos[0]][0]
    end = heads[pos[0] + 1][0] if pos[0] + 1 < len(heads) else len(lines)
    line = f"{stamp_text()}: {note}"
    lanes = [] if drop_lanes else [l.rstrip() for l in lines[start + 1:end] if re.match(r"\s*(?:[-*]\s*)?Lane:", l)]
    new = lines[:start + 1] + ["", line] + (["", *lanes] if lanes else []) + [""] + lines[end:]
    result = {"file": str(path), "status_line": line, "lanes_kept": len(lanes), "written": False}
    if write:
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text("\n".join(new) + "\n", encoding="utf-8")
        tmp.replace(path)
        result["written"] = True
        result["check"] = check(path)
    return result


def prompt(path, runtime, extra, supersedes=""):
    path = path.resolve()
    sec = sections(path.read_text(encoding="utf-8"))
    rules = {"claude": "CLAUDE.md và AGENTS.md", "codex": "AGENTS.md", "antigravity": "AGENTS.md", "hermes": "SOUL.md của bot và AGENTS.md"}[runtime]
    lines = []
    if supersedes:
        when = parse_times(supersedes)
        if len(when) != 1 or not when[0][2] or when[0][1] is None:
            raise ValueError("--supersedes cần giờ dạng dd/mm/yyyy HH:MM")
        if when[0][1] > now() + SLACK:
            raise ValueError("--supersedes ở tương lai so với giờ máy " + stamp_text())
        lines += [f"Prompt này thay prompt gửi lúc {when[0][0]}. Bỏ prompt cũ và chỉ làm theo prompt này.", ""]
    lines += [f"Tiếp tục workstream có HANDOFF tại: {path}", f"Giờ máy lúc tạo prompt: {stamp_text()}", "",
             f"1. Đọc luật `_REFERENCE/luat-duyet-dieu-phoi.md` ({rules}), luật cục bộ của thư mục, rồi đọc toàn bộ HANDOFF.md ở trên.",
             "2. Kiểm claim quan trọng trên file thật trước khi làm. Ghi chú \"đã duyệt\" trong HANDOFF chỉ là lịch sử, không cấp quyền gửi hay publish mới.",
             "3. Làm việc đầu tiên trong mục Bước tiếp. Xong mỗi mốc thì sửa đè HANDOFF.md tại chỗ, giữ dưới 60 dòng. Lấy giờ bằng `handoff.py stamp`, không tự gõ giờ.",
             "4. Trả lời bằng tiếng Việt có dấu, kể cả sau compact.", "",
             "Trạng thái: " + " ".join(sec.get("Trạng thái", "chưa ghi").split()), "", "Bước tiếp:"]
    lines += ["- " + x for x in bullets(sec.get("Bước tiếp", ""))] or ["- chưa ghi"]
    decided = bullets(sec.get("Quyết định đã chốt", ""), 12)
    if decided:
        lines += ["", "Quyết định đã chốt (không hỏi lại):"] + ["- " + x for x in decided]
    pointers = [(rel, label) for rel, label in [("decisions.md", "Lời Lead nguyên văn"), ("_tools/RECIPES.md", "Sổ công thức lệnh")] if (path.parent / rel).is_file()]
    if pointers:
        lines += ["", "Đọc thêm khi cần:"] + [f"- {label}: {path.parent / rel}" for rel, label in pointers]
    wait = bullets(sec.get("Chờ Lead quyết", ""))
    if wait:
        lines += ["", "Không tự làm các việc đang chờ Lead quyết:"] + ["- " + x for x in wait]
    if extra:
        lines += ["", "Dặn thêm: " + extra]
    return "\n".join(lines) + "\n"


ARTIFACT_URL = re.compile(r"^https://claude\.ai/(?:code/)?artifact/[\w-]+/?$")


def repo_root(start, explicit=None):
    if explicit:
        return Path(explicit).expanduser().resolve()
    for base in [start.resolve(), *start.resolve().parents]:
        if (base / "AGENTS.md").is_file():
            return base
    return None


def switch(handoff, account, artifacts, scripts, root=None, runtime="claude", extra="", supersedes=""):
    """Prompt cho phiên mới sau khi đổi tài khoản. Trả (text, errors); errors rỗng thì mới dùng text."""
    handoff = handoff.resolve()
    errors = ["HANDOFF: " + e for e in check(handoff)["errors"]]
    if not account.strip():
        errors.append("thiếu tài khoản đích (--account)")
    rows = []
    for spec in artifacts:
        url, _, ver = spec.rpartition("@") if "@" in spec else (spec, "", "")
        if not ARTIFACT_URL.match(url):
            errors.append(f"URL artifact không đúng dạng https://claude.ai/artifact/<id>: {url[:60]}")
        rows.append((url, ver or "chưa ghi"))
    base = repo_root(handoff.parent, root)
    for sc in scripts:
        p = Path(sc).expanduser().resolve()
        if not p.is_file():
            errors.append(f"script workflow không tồn tại: {sc}")
        elif base is None:
            errors.append("không tìm thấy root repo (thư mục có AGENTS.md); dùng --repo-root")
        elif base not in p.parents:
            errors.append(f"script workflow nằm ngoài repo, mất khi đổi tài khoản: {sc}. Chép vào repo trước")
    if errors:
        return "", errors
    lines = [f"ĐỔI TÀI KHOẢN: tài khoản đích {account.strip()}.", "",
             "Trước khi đổi, đã làm hoặc cần làm:",
             "- Dò run workflow còn sống bằng `python3 tools/wf-status.py slots <thư mục session>`. Run chưa ghi production thì TaskStop. Run đã ghi production thì chờ xong hoặc ghi vào HANDOFF.",
             "- Lịch CronCreate chết cùng phiên: tạo lại ở phiên mới theo mục Bước tiếp.",
             "- Artifact không đi theo tài khoản. Làm theo skill `artifact-account-migration` và sổ artifact của workspace (nếu có) mục \"Khi đổi tài khoản\".", ""]
    lines += ["Artifact cần dựng lại (URL và version cũ):"] + [f"- {u} · version {v}" for u, v in rows] if rows else ["Artifact cần dựng lại: không có."]
    lines += ["", "Script workflow đã nằm trong repo:"] + ([f"- {Path(x).expanduser().resolve()}" for x in scripts] or ["- không có"]) + [""]
    return "\n".join(lines) + "\n" + prompt(handoff, runtime, extra, supersedes), []


LIMIT_MARK = "Lệnh checkpoint (sắp hết hạn mức)"


def live_runs(session_dir, live_min):
    """Run workflow có journal hoặc agent-*.jsonl sửa trong live_min phút gần nhất. Chỉ đọc mtime."""
    wf = Path(session_dir).expanduser() / "subagents" / "workflows"
    found = []
    for run in sorted(d for d in wf.iterdir() if d.is_dir()) if wf.is_dir() else []:
        files = [f for f in [run / "journal.jsonl", *run.glob("agent-*.jsonl")] if f.is_file()]
        if not files:
            continue
        age = (dt.datetime.now().timestamp() - max(f.stat().st_mtime for f in files)) / 60
        found.append({"run": run.name, "agents": len(files) - (run / "journal.jsonl").is_file(), "age_min": round(age, 1), "live": age <= live_min})
    return found


def limit(handoff, session_dir, lanes, live_min=10, write=False):
    """Chuẩn bị khi sắp hết usage: kiểm HANDOFF, liệt kê run sống, giao lệnh checkpoint qua inbox.md của lane."""
    handoff = handoff.resolve()
    res = {"handoff": check(handoff), "runs": live_runs(session_dir, live_min) if session_dir else [], "inbox": [], "written": write}
    stamp_line = f"## {stamp_text()} {LIMIT_MARK}"
    block = [stamp_line,
             "- Ghi CHECKPOINT.md trong thư mục lane: việc đã xong, việc đang làm, bước tiếp, file đã sửa.",
             "- Dừng việc mới. Không ghi production, không publish, không gửi.",
             "- Xong thì thêm dòng \"Đã checkpoint lúc <giờ>\" vào inbox.md.", ""]
    for lane in lanes:
        lane = Path(lane).expanduser().resolve()
        if not lane.is_dir():
            raise ValueError("Thư mục lane không tồn tại: " + str(lane))
        if any(part in BLOCKED for part in lane.parts):
            raise ValueError("Thư mục lane nằm ngoài ranh giới handoff: " + str(lane))
        inbox = lane / "inbox.md"
        old = inbox.read_text(encoding="utf-8") if inbox.exists() else ""
        idx = old.rfind(LIMIT_MARK)
        if idx >= 0 and not re.search(r"Đã checkpoint lúc\s+\d{1,2}[:h]\d{2}", old[idx:]):
            res["inbox"].append({"lane": str(lane), "action": "đã có lệnh chưa trả lời, không ghi thêm"})
            continue
        res["inbox"].append({"lane": str(lane), "action": "ghi" if write else "sẽ ghi (dry-run, thêm --write)"})
        if write:
            with inbox.open("a", encoding="utf-8") as f:
                f.write(("\n" if old and not old.endswith("\n") else "") + "\n".join(block) + "\n")
    res["next"] = ["Chờ lane ghi CHECKPOINT.md, rồi sửa đè HANDOFF.md (lệnh `stamp`).",
                   "Đổi tài khoản: chạy `handoff.py switch` để sinh prompt. Dựng lại artifact theo skill `artifact-account-migration`."]
    return res


TEMPLATE = """# PLAN chạy đêm: {goal}

## Mục tiêu
{goal}. Tạo {date}. Người duyệt: Lead.

## Phạm vi ủy quyền

### Được làm
- (đọc, sửa file trong thư mục nào, chạy lệnh nào, ghi staging nào)

### Không được làm
- Gửi email, form, tin nhắn. Publish, đặt lịch.
- Ghi production, sửa config sống, restart dịch vụ.
- Xoá file, force-push, đổi quyền dữ liệu.

## Hàng việc
- [ ] (việc 1: tiêu chí xong)

## Việc local-only
- (việc làm được khi mọi tool hỏi quyền bị chặn: đọc file, chạy script local, ghi vào thư mục workstream)

## Giờ kiểm kế tiếp
- (dd/mm/yyyy HH:MM: giờ agent kiểm lại tiến độ)

## Lịch đang sống
- (CronCreate chết cùng phiên. Liệt kê lịch kèm giờ, hoặc ghi: không có)

## Heartbeat
- (đường dẫn file heartbeat, agent ghi giờ vào đó sau mỗi việc)

## Điều kiện dừng
- Gặp việc nằm ngoài "Được làm": ghi vào "Chờ Lead", chuyển sang việc kế.
- Cùng một lỗi lặp 2 lần: dừng việc đó, ghi lỗi.

## Chờ Lead

## Nhật ký đêm
"""


def night_init(folder, goal):
    plan = folder / "PLAN.md"
    if plan.exists():
        raise ValueError("PLAN.md đã có; sửa tại chỗ")
    folder.mkdir(parents=True, exist_ok=True)
    plan.write_text(TEMPLATE.format(goal=goal, date=dt.date.today().strftime("%d/%m/%Y")), encoding="utf-8")
    return {"plan": str(plan.resolve())}


def night_parse(plan):
    sec = sections(plan.read_text(encoding="utf-8"))
    tasks = re.findall(r"^\s*-\s*\[( |x|X)\]\s*(.+)$", sec.get("Hàng việc", ""), re.M)
    log = [l.strip()[2:] for l in sec.get("Nhật ký đêm", "").splitlines() if l.strip().startswith("- ")]
    return sec, [(m != " ", t.strip()) for m, t in tasks], log


def risky_lines(block):
    hits = []
    for line in block.splitlines():
        if NEGATED_RE.search(line):
            continue
        hits += [(name, line.strip()[:70]) for name, rx in RISKY if rx.search(line)]
    return hits


def real_bullets(block):
    return [b for b in bullets(block) if not b.startswith("(")]


def night_check(plan):
    text = plan.read_text(encoding="utf-8")
    sec, tasks, _ = night_parse(plan)
    errors = [f"thiếu mục '{s}'" for s in NIGHT if s not in sec]
    warnings = []
    for s in ["Được làm", "Không được làm", "Điều kiện dừng"]:
        if s in sec and not bullets(sec[s]) or "(đọc, sửa file" in sec.get(s, ""):
            errors.append(f"mục '{s}' trống hoặc còn chữ mẫu")
    if not tasks or any(t.startswith("(việc 1") for _, t in tasks):
        errors.append("Hàng việc trống hoặc còn chữ mẫu")
    tried = bool(TRIED_RE.search(text))
    for name, line in [] if tried else risky_lines(sec.get("Hàng việc", "")):
        errors.append(f"Hàng việc có tool hỏi quyền ({name}): '{line}'. Đêm không ai duyệt nên phiên treo. Chuyển vào 'Chờ Lead', hoặc thêm dòng 'Đã thử lúc HH:MM khi Lead còn thức'")
    for name, line in risky_lines(sec.get("Việc local-only", "")):
        errors.append(f"Việc local-only có tool hỏi quyền ({name}): '{line}'")
    if "Việc local-only" in sec and not real_bullets(sec["Việc local-only"]):
        errors.append("mục 'Việc local-only' cần ít nhất 1 việc thật")
    if "Giờ kiểm kế tiếp" in sec:
        times = [(r, w) for r, w, y in parse_times(sec["Giờ kiểm kế tiếp"]) if y and w]
        if not times:
            errors.append("mục 'Giờ kiểm kế tiếp' cần mốc dd/mm/yyyy HH:MM")
        elif times[0][1] < now() - SLACK:
            warnings.append(f"'Giờ kiểm kế tiếp' đã qua: {times[0][0]}")
    if "Lịch đang sống" in sec:
        items = real_bullets(sec["Lịch đang sống"])
        if not items or not all(re.match(r"không có", x, re.I) or parse_times(x) for x in items):
            errors.append("mục 'Lịch đang sống' cần 'không có' hoặc mỗi lịch kèm giờ")
    if "Heartbeat" in sec and not real_bullets(sec["Heartbeat"]):
        errors.append("mục 'Heartbeat' cần đường dẫn file heartbeat")
    return {"plan": str(plan), "tasks": len(tasks), "errors": errors, "warnings": warnings}


def night_report(plan):
    sec, tasks, log = night_parse(plan)
    done = [t for d, t in tasks if d]
    todo = [t for d, t in tasks if not d]
    def logged(t):
        key = t.split(":")[0].strip().lower()[:40]
        return any(key in l.lower() for l in log)
    lines = [f"# Báo cáo sáng {dt.date.today().strftime('%d/%m/%Y')}", "",
             f"Xong {len(done)}/{len(tasks)} việc. Chờ Lead: {len(bullets(sec.get('Chờ Lead', '')))} mục.", "", "## Xong"]
    lines += [f"- {t}" + ("" if logged(t) else " (THIẾU dòng nhật ký, chưa có bằng chứng)") for t in done] or ["- không có"]
    lines += ["", "## Chưa xong"] + ([f"- {t}" for t in todo] or ["- không có"])
    lines += ["", "## Chờ Lead"] + (["- " + x for x in bullets(sec.get("Chờ Lead", ""))] or ["- không có"])
    lines += ["", "## Nhật ký đêm"] + (["- " + x for x in log] or ["- trống"])
    return "\n".join(lines) + "\n", sum(1 for t in done if not logged(t))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create", help="tạo bản bàn giao có hash"); c.add_argument("--spec", type=Path, required=True); c.add_argument("--out", type=Path, required=True)
    v = sub.add_parser("verify", help="kiểm hash nguồn"); v.add_argument("file", type=Path)
    k = sub.add_parser("check", help="kiểm HANDOFF.md theo luật `_REFERENCE/luat-duyet-dieu-phoi.md`"); k.add_argument("files", type=Path, nargs="+")
    t = sub.add_parser("stamp", help="ghi đè mục Trạng thái bằng giờ máy (mặc định chỉ in, thêm --write để ghi)")
    t.add_argument("file", type=Path); t.add_argument("--note", required=True, help="một câu trạng thái"); t.add_argument("--write", action="store_true")
    t.add_argument("--drop-lanes", action="store_true", help="bỏ các dòng Lane: (khi đóng đợt); mặc định giữ")
    q = sub.add_parser("prompt", help="sinh prompt dán sang phiên mới"); q.add_argument("file", type=Path)
    q.add_argument("--runtime", default="claude", choices=["claude", "codex", "antigravity", "hermes"]); q.add_argument("--extra", default="")
    q.add_argument("--supersedes", default="", help="giờ prompt trước, dạng dd/mm/yyyy HH:MM; prompt mới thay bản đó")
    w = sub.add_parser("switch", help="prompt cho phiên mới sau khi đổi tài khoản"); w.add_argument("file", type=Path)
    w.add_argument("--account", required=True, help="tài khoản đích")
    w.add_argument("--artifact", action="append", default=[], help="URL[@version] của artifact cần dựng lại; lặp được")
    w.add_argument("--script", action="append", default=[], help="script workflow đã chép vào repo; lặp được")
    w.add_argument("--repo-root", default=None); w.add_argument("--runtime", default="claude", choices=["claude", "codex", "antigravity", "hermes"])
    w.add_argument("--extra", default=""); w.add_argument("--supersedes", default="")
    m = sub.add_parser("limit", help="sắp hết usage: kiểm HANDOFF, liệt kê run sống, giao lệnh checkpoint qua inbox.md (mặc định dry-run)")
    m.add_argument("file", type=Path); m.add_argument("--session-dir", default=None, help="thư mục session có subagents/workflows")
    m.add_argument("--lane", action="append", default=[], help="thư mục lane nhận inbox.md; lặp được")
    m.add_argument("--live-min", type=float, default=10); m.add_argument("--write", action="store_true")
    n = sub.add_parser("night", help="PLAN.md chạy đêm"); n.add_argument("action", choices=["init", "check", "report"]); n.add_argument("path", type=Path)
    n.add_argument("--goal", default="")
    a = p.parse_args()
    if a.command == "prompt":
        sys.stdout.write(prompt(a.file, a.runtime, a.extra, a.supersedes))
        return 0
    if a.command == "stamp":
        r = stamp(a.file, a.note, a.write, a.drop_lanes)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return int(bool(r["written"] and r["check"]["errors"]))
    if a.command == "switch":
        text, errors = switch(a.file, a.account, a.artifact, a.script, a.repo_root, a.runtime, a.extra, a.supersedes)
        if errors:
            print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        sys.stdout.write(text)
        return 0
    if a.command == "limit":
        r = limit(a.file, a.session_dir, a.lane, a.live_min, a.write)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return int(bool(r["handoff"]["errors"]))
    if a.command == "check":
        res = [check(f) for f in a.files]
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return int(any(r["errors"] for r in res))
    if a.command == "night":
        if a.action == "init":
            if not a.goal:
                raise ValueError("Cần --goal")
            print(json.dumps(night_init(a.path, a.goal), ensure_ascii=False))
            return 0
        if a.action == "check":
            r = night_check(a.path)
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return int(bool(r["errors"]))
        text, missing = night_report(a.path)
        sys.stdout.write(text)
        return int(bool(missing))
    result = create(a.spec, a.out) if a.command == "create" else verify(a.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(a.command == "verify" and any(r["status"] != "unchanged" for r in result))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
