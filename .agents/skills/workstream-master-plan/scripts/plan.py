#!/usr/bin/env python3
"""Sổ yêu cầu và master plan của một workstream: đọc, kiểm, thêm vào plan.json.

Lệnh (mọi lệnh ghi mặc định dry-run, thêm --apply để ghi):
  init <thư mục>                      tạo plan.json từ templates/plan.skeleton.json
  add-request --ask "..." --items M41,M42
                                      thêm yêu cầu của Lead (ask tối đa 200 ký tự)
  add-item --title "..." --phase P1 --source "..." [--program X] [--deps M1,M2]
                                      thêm việc vào plan
  set-status ID STATUS                đổi trạng thái (done cần --evidence, need cần --checked)
  progress [--program X]              in dòng "Tiến độ chương trình x/y" đếm từ file
  lint                                kiểm schema và logic, không ghi gì

Giờ do code lấy từ đồng hồ máy (datetime.now). Không có tham số nhập giờ tay.
Schema giữ tương thích với instance master-plan có sẵn: requests[].items là CHUỖI
(ví dụ "M41, M42"), không phải list. Lỗi list.replace ngày 20/10 đến từ chỗ này.

Mã thoát: 0 xong, 1 lint có lỗi, 2 đầu vào sai, 3 không đọc được hoặc không ghi được
plan.json, 4 plan.json đổi trong lúc xử lý (phiên khác vừa ghi), chạy lại lệnh.
Python 3.9+, chỉ dùng thư viện chuẩn.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKELETON = SKILL_DIR / "templates" / "plan.skeleton.json"
STATUSES = ["doing", "todo", "need", "wait", "other", "done"]
STATUS_LABEL = {
    "doing": "Đang làm", "todo": "Chưa làm", "need": "Cần Lead quyết",
    "wait": "Chờ mốc", "other": "Phiên khác", "done": "Xong",
}
ASK_MAX = 200
NO_WORK_MARKERS = ("xong", "luật", "luat", "không có việc", "khong co viec")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TOKEN_ID_RE = re.compile(r"\b[A-Za-z]{1,4}\d+[A-Za-z0-9]*\b")
STAMP_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\s+(\d{1,2}):(\d{2})\s*$")
STAMP_FMT = "%d/%m/%Y %H:%M"


class PlanError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


def now():
    """Giờ máy. Điểm duy nhất lấy giờ, test thay hàm này."""
    return datetime.now()


def fmt_stamp(dt):
    return dt.strftime(STAMP_FMT)


def parse_stamp(s, ref=None):
    """Đọc 'DD/MM/YYYY HH:MM' hoặc 'DD/MM HH:MM'. Không đọc được thì trả None.

    Mốc không có năm lấy năm của ref. Nếu kết quả lệch quá 180 ngày về tương lai
    thì lùi một năm, để workstream chạy qua tháng 12 sang tháng 1 không báo sai.
    """
    if not isinstance(s, str):
        return None
    m = STAMP_RE.match(s)
    if not m:
        return None
    ref = ref or now()
    d, mo, y, h, mi = m.groups()
    year = int(y) if y else ref.year
    try:
        dt = datetime(year, int(mo), int(d), int(h), int(mi))
    except ValueError:
        return None
    if not y and dt - ref > timedelta(days=180):
        try:
            dt = dt.replace(year=year - 1)
        except ValueError:
            return None
    return dt


def id_tokens(text):
    return TOKEN_ID_RE.findall(text or "")


def is_no_work(items_text):
    t = (items_text or "").strip().lower()
    return any(t.startswith(k) for k in NO_WORK_MARKERS)


# ---------------------------------------------------------------- đọc, ghi

def read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as e:
        raise PlanError(3, "không đọc được %s: %s" % (path, e))


def parse_plan(raw, path="plan.json"):
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise PlanError(3, "%s không phải JSON hợp lệ: %s" % (path, e))
    if not isinstance(data, dict):
        raise PlanError(3, "%s phải là object ở gốc" % path)
    return data


def load_plan(path):
    raw = read_bytes(path)
    return parse_plan(raw, path), raw


def dump_plan(plan):
    return (json.dumps(plan, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def save_plan(path, plan, orig_raw):
    """Ghi nguyên tử. Dừng nếu file đã đổi từ lúc đọc (phiên khác vừa ghi)."""
    p = Path(path)
    try:
        current = p.read_bytes()
    except OSError as e:
        raise PlanError(3, "không đọc lại được %s: %s" % (path, e))
    if hashlib.sha256(current).digest() != hashlib.sha256(orig_raw).digest():
        raise PlanError(4, "%s đã đổi trong lúc xử lý. Chạy lại lệnh để đọc bản mới." % path)
    tmp = p.with_name(p.name + ".tmp-%d" % os.getpid())
    try:
        tmp.write_bytes(dump_plan(plan))
        os.replace(str(tmp), str(p))
    except OSError as e:
        raise PlanError(3, "không ghi được %s: %s" % (path, e))
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------- kiểm

def _is_str_list(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def find_cycle(items):
    """Trả về danh sách id tạo thành vòng deps, hoặc None."""
    graph = {i["id"]: [d for d in i.get("deps", []) if isinstance(d, str)] for i in items
             if isinstance(i, dict) and isinstance(i.get("id"), str)}
    color = {}
    stack = []

    def visit(n):
        color[n] = 1
        stack.append(n)
        for d in graph.get(n, []):
            if d not in graph:
                continue
            if color.get(d) == 1:
                return stack[stack.index(d):] + [d]
            if color.get(d) is None:
                r = visit(d)
                if r:
                    return r
        stack.pop()
        color[n] = 2
        return None

    for n in graph:
        if color.get(n) is None:
            r = visit(n)
            if r:
                return r
    return None


def validate(plan, ref=None):
    """Trả (errors, warnings), mỗi phần tử là một chuỗi."""
    ref = ref or now()
    errs, warns = [], []
    for k, typ in (("items", list), ("phases", list), ("requests", list), ("done", list), ("rules", list)):
        if not isinstance(plan.get(k), typ):
            errs.append("thiếu hoặc sai kiểu khoá '%s' (cần list)" % k)
    if not isinstance(plan.get("title"), str) or not plan.get("title", "").strip():
        errs.append("thiếu 'title'")
    if errs:
        return errs, warns

    phase_ids = set()
    for n, ph in enumerate(plan["phases"]):
        if not isinstance(ph, dict) or not all(isinstance(ph.get(k), str) for k in ("id", "name", "when", "why")):
            errs.append("phases[%d] cần id, name, when, why kiểu chuỗi" % n)
            continue
        if ph["id"] in phase_ids:
            errs.append("phase trùng id %s" % ph["id"])
        phase_ids.add(ph["id"])

    ids, items = set(), []
    for n, it in enumerate(plan["items"]):
        if not isinstance(it, dict):
            errs.append("items[%d] phải là object" % n)
            continue
        iid = it.get("id")
        if not isinstance(iid, str) or not ID_RE.match(iid):
            errs.append("items[%d] id sai hoặc thiếu: %r" % (n, iid))
            continue
        if iid in ids:
            errs.append("%s: id trùng" % iid)
        ids.add(iid)
        items.append(it)
        if not isinstance(it.get("title"), str) or not it["title"].strip():
            errs.append("%s: thiếu title" % iid)
        if it.get("phase") not in phase_ids:
            errs.append("%s: phase %r không có trong phases" % (iid, it.get("phase")))
        if it.get("status") not in STATUSES:
            errs.append("%s: status %r không hợp lệ (dùng %s)" % (iid, it.get("status"), "/".join(STATUSES)))
        for key in ("detail", "deps", "blocks"):
            if key in it and not _is_str_list(it[key]):
                errs.append("%s: '%s' phải là list chuỗi" % (iid, key))
        if not isinstance(it.get("source"), str) or not it.get("source", "").strip():
            errs.append("%s: thiếu source (nguồn của việc, ví dụ tin Lead kèm giờ)" % iid)
        if it.get("status") == "done" and (not isinstance(it.get("evidence"), str) or not it.get("evidence", "").strip()):
            errs.append("%s: done nhưng thiếu evidence" % iid)
        if "program" in it and (not isinstance(it["program"], str) or not it["program"].strip()):
            errs.append("%s: 'program' phải là chuỗi không rỗng" % iid)
        if it.get("status") == "need" and not str(it.get("need_checked", "")).strip():
            warns.append("%s: status need chưa ghi need_checked (đã kiểm Lead chưa duyệt ở đâu)" % iid)
        for key in ("added", "status_at"):
            if key in it:
                dt = parse_stamp(it[key], ref)
                if dt is None:
                    warns.append("%s: '%s' không đọc được giờ: %r" % (iid, key, it[key]))
                elif dt > ref + timedelta(minutes=1):
                    warns.append("%s: '%s' = %s nằm sau giờ hiện tại %s" % (iid, key, it[key], fmt_stamp(ref)))

    for it in items:
        iid = it["id"]
        for d in it.get("deps", []) if _is_str_list(it.get("deps", [])) else []:
            if d not in ids:
                errs.append("%s: deps trỏ tới %s không có trong plan" % (iid, d))
            if d == iid:
                errs.append("%s: deps tự trỏ vào chính nó" % iid)
        for b in it.get("blocks", []) if _is_str_list(it.get("blocks", [])) else []:
            if b not in ids:
                warns.append("%s: blocks trỏ tới %s không có trong plan" % (iid, b))
    cyc = find_cycle(items)
    if cyc:
        errs.append("deps tạo vòng: %s" % " -> ".join(cyc))

    prefixes = {re.match(r"[A-Za-z]+", i).group(0) for i in ids if re.match(r"[A-Za-z]+", i)}
    for n, r in enumerate(plan["requests"]):
        tag = "requests[%d]" % n
        if not isinstance(r, dict):
            errs.append("%s phải là object" % tag)
            continue
        if not isinstance(r.get("items"), str):
            errs.append("%s: 'items' phải là CHUỖI, không phải %s (lỗi list.replace 20/10)" % (tag, type(r.get("items")).__name__))
            continue
        if not isinstance(r.get("ask"), str) or not r["ask"].strip():
            errs.append("%s: thiếu ask" % tag)
        if not isinstance(r.get("date"), str) or not r["date"].strip():
            errs.append("%s: thiếu date" % tag)
        else:
            dt = parse_stamp(r["date"], ref)
            if dt is not None and dt > ref + timedelta(minutes=1):
                warns.append("%s: date %s nằm sau giờ hiện tại %s" % (tag, r["date"], fmt_stamp(ref)))
        known = [i for i in ids if re.search(r"(?<![A-Za-z0-9._-])%s(?![A-Za-z0-9._-])" % re.escape(i), r["items"])]
        if not known and not is_no_work(r["items"]):
            errs.append("%s (%s): yêu cầu không trỏ tới việc nào trong plan: %r" % (tag, r.get("date", "?"), r["ask"][:60]))
        for t in id_tokens(r["items"]):
            m = re.match(r"[A-Za-z]+", t)
            if known and t not in ids and m and m.group(0) in prefixes:
                warns.append("%s: nhắc %s nhưng plan không có việc này" % (tag, t))

    for n, d in enumerate(plan["done"]):
        if not isinstance(d, dict) or not all(isinstance(d.get(k), str) for k in ("when", "what", "evidence")):
            errs.append("done[%d] cần when, what, evidence kiểu chuỗi" % n)

    up = plan.get("updated")
    if isinstance(up, str) and up.strip():
        dt = parse_stamp(up, ref)
        if dt is not None and dt > ref + timedelta(minutes=1):
            warns.append("updated %s nằm sau giờ hiện tại %s" % (up, fmt_stamp(ref)))
    return errs, list(dict.fromkeys(warns))


def progress(plan, program=None):
    """Đếm tiến độ từ file: (done, total, theo từng chương trình, theo trạng thái)."""
    items = [i for i in plan["items"] if program is None or i.get("program") == program]
    by_prog = {}
    for i in plan["items"]:
        key = i.get("program") or ""
        d = by_prog.setdefault(key, [0, 0])
        d[1] += 1
        if i.get("status") == "done":
            d[0] += 1
    counts = {s: sum(1 for i in items if i.get("status") == s) for s in STATUSES}
    return counts["done"], len(items), by_prog, counts


def progress_line(plan, program=None):
    done, total, _, _ = progress(plan, program)
    name = " " + program if program else ""
    pct = (100 * done // total) if total else 0
    return "Tiến độ chương trình%s: %d/%d (%d%%)" % (name, done, total, pct)


# ---------------------------------------------------------------- lệnh

def say(msg=""):
    print(msg)


def commit(args, plan, orig_raw, ref, what, tolerate=""):
    """Kiểm plan mới không thêm lỗi rồi ghi (--apply) hoặc chỉ in (dry-run)."""
    old = parse_plan(orig_raw)
    old_errs, _ = validate(old, ref)
    plan["updated"] = fmt_stamp(ref)
    new_errs, _ = validate(plan, ref)
    added = [e for e in new_errs if e not in old_errs and not (tolerate and tolerate in e)]
    if added:
        raise PlanError(2, "thay đổi này tạo lỗi mới, không ghi:\n  - " + "\n  - ".join(added))
    if args.apply:
        save_plan(args.plan, plan, orig_raw)
        say("Đã ghi %s: %s" % (args.plan, what))
    else:
        say("DRY-RUN (chưa ghi): %s. Thêm --apply để ghi vào %s." % (what, args.plan))


def csv_ids(text):
    out = []
    for p in (text or "").split(","):
        p = p.strip()
        if not p:
            continue
        if not ID_RE.match(p):
            raise PlanError(2, "id không hợp lệ: %r" % p)
        if p not in out:
            out.append(p)
    return out


def cmd_init(args):
    target = Path(args.dir)
    out = target / "plan.json"
    if out.exists():
        raise PlanError(2, "%s đã có, không ghi đè" % out)
    skel = parse_plan(read_bytes(SKELETON), str(SKELETON))
    if args.title:
        skel["title"] = args.title
    skel["updated"] = fmt_stamp(now())
    if args.apply:
        try:
            target.mkdir(parents=True, exist_ok=True)
            out.write_bytes(dump_plan(skel))
        except OSError as e:
            raise PlanError(3, "không ghi được %s: %s" % (out, e))
        say("Đã tạo %s" % out)
    else:
        say("DRY-RUN (chưa ghi): sẽ tạo %s với title %r. Thêm --apply để ghi." % (out, skel["title"]))


def cmd_add_request(args):
    ref = now()
    plan, raw = load_plan(args.plan)
    ask = " ".join((args.ask or "").split())
    if not ask:
        raise PlanError(2, "--ask rỗng")
    if len(ask) > ASK_MAX:
        raise PlanError(2, "--ask dài %d ký tự, tối đa %d. Trích ý chính, không dán cả tin." % (len(ask), ASK_MAX))
    if bool(args.items) == bool(args.no_items_reason):
        raise PlanError(2, "cần đúng một trong hai: --items M41,M42 hoặc --no-items-reason \"lý do\"")
    if any(isinstance(r, dict) and r.get("ask") == ask for r in plan.get("requests", [])):
        raise PlanError(2, "yêu cầu giống hệt đã có trong sổ")
    if args.items:
        ids = csv_ids(args.items)
        if not ids:
            raise PlanError(2, "--items rỗng")
        existing = {i.get("id") for i in plan.get("items", []) if isinstance(i, dict)}
        for i in ids:
            if i not in existing:
                say("CẢNH BÁO: %s chưa có trong plan. Chạy add-item cho %s, lint sẽ báo nếu quên." % (i, i))
        items_text = ", ".join(ids)
    else:
        items_text = "không có việc: " + args.no_items_reason.strip()
    entry = {"date": fmt_stamp(ref), "ask": ask, "items": items_text}
    plan.setdefault("requests", []).append(entry)
    say(json.dumps(entry, ensure_ascii=False))
    commit(args, plan, raw, ref, "thêm yêu cầu lúc %s" % entry["date"],
           tolerate="không trỏ tới việc nào")


def next_id(plan, prefix):
    pat = re.compile(r"^%s(\d+)$" % re.escape(prefix))
    nums = [int(m.group(1)) for i in plan.get("items", []) if isinstance(i, dict)
            for m in [pat.match(str(i.get("id", "")))] if m]
    return "%s%d" % (prefix, (max(nums) + 1) if nums else 1)


def cmd_add_item(args):
    ref = now()
    plan, raw = load_plan(args.plan)
    status = args.status
    if status == "done" and not (args.evidence or "").strip():
        raise PlanError(2, "status done cần --evidence")
    if status == "need" and not (args.checked or "").strip():
        raise PlanError(2, "status need cần --checked \"đã kiểm Lead chưa duyệt ở đâu\"")
    iid = args.id or next_id(plan, args.prefix)
    if not ID_RE.match(iid):
        raise PlanError(2, "id không hợp lệ: %r" % iid)
    if any(isinstance(i, dict) and i.get("id") == iid for i in plan.get("items", [])):
        raise PlanError(2, "id %s đã có" % iid)
    if not (args.source or "").strip():
        raise PlanError(2, "--source rỗng. Ghi tin Lead kèm giờ hoặc tên tài liệu nguồn.")
    deps = csv_ids(args.deps)
    entry = {
        "id": iid, "phase": args.phase, "status": status, "title": args.title.strip(),
        "detail": [d for d in (args.detail or []) if d.strip()],
        "deps": deps, "blocks": [], "source": args.source.strip(),
        "evidence": (args.evidence or "").strip(), "added": fmt_stamp(ref), "status_at": fmt_stamp(ref),
    }
    if args.program:
        entry["program"] = args.program.strip()
    if status == "need":
        entry["need_checked"] = args.checked.strip()
    plan["items"].append(entry)
    for d in deps:
        for it in plan["items"]:
            if it.get("id") == d and iid not in it.setdefault("blocks", []):
                it["blocks"].append(iid)
    say(json.dumps(entry, ensure_ascii=False))
    commit(args, plan, raw, ref, "thêm việc %s" % iid)


def cmd_set_status(args):
    ref = now()
    plan, raw = load_plan(args.plan)
    it = next((i for i in plan.get("items", []) if isinstance(i, dict) and i.get("id") == args.id), None)
    if it is None:
        raise PlanError(2, "không có việc %s" % args.id)
    if args.evidence:
        it["evidence"] = args.evidence.strip()
    if args.status == "done" and not str(it.get("evidence", "")).strip():
        raise PlanError(2, "status done cần --evidence (đường dẫn file, log, số đo)")
    if args.status == "need":
        if not (args.checked or "").strip():
            raise PlanError(2, "status need cần --checked \"đã kiểm Lead chưa duyệt ở đâu\"")
        it["need_checked"] = args.checked.strip()
    old = it.get("status")
    it["status"] = args.status
    it["status_at"] = fmt_stamp(ref)
    commit(args, plan, raw, ref, "%s: %s -> %s lúc %s" % (args.id, old, args.status, it["status_at"]))


def cmd_progress(args):
    plan, _ = load_plan(args.plan)
    if not isinstance(plan.get("items"), list) or not all(isinstance(i, dict) for i in plan["items"]):
        raise PlanError(2, "plan.json thiếu 'items' hoặc sai kiểu, chạy lint")
    errs, _ = validate(plan)
    if errs:
        print("CẢNH BÁO: plan.json có %d lỗi lint, số đếm bên dưới có thể lệch. Chạy lint." % len(errs), file=sys.stderr)
    if args.program:
        done, total, _, _ = progress(plan, args.program)
        if total == 0:
            raise PlanError(2, "không có việc nào thuộc chương trình %r" % args.program)
    say(progress_line(plan, args.program))
    if not args.program:
        _, _, by_prog, counts = progress(plan)
        for name in sorted(k for k in by_prog if k):
            d, t = by_prog[name]
            say("- %s: %d/%d" % (name, d, t))
        if "" in by_prog and len(by_prog) > 1:
            d, t = by_prog[""]
            say("- (chưa gắn chương trình): %d/%d" % (d, t))
        say("Trạng thái: " + " · ".join("%s %d" % (STATUS_LABEL[s], counts[s]) for s in STATUSES if counts[s]))


def cmd_lint(args):
    plan, _ = load_plan(args.plan)
    errs, warns = validate(plan)
    for e in errs:
        say("LỖI: " + e)
    for w in warns:
        say("CẢNH BÁO: " + w)
    say("lint: %d lỗi, %d cảnh báo, %d việc, %d yêu cầu" % (
        len(errs), len(warns), len(plan.get("items", [])), len(plan.get("requests", []))))
    if errs or (args.strict and warns):
        raise PlanError(1, "")


def build_parser():
    ap = argparse.ArgumentParser(prog="plan.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, write=True):
        p.add_argument("--plan", default="plan.json", help="đường dẫn plan.json (mặc định ./plan.json)")
        if write:
            p.add_argument("--apply", action="store_true", help="ghi thật; không có cờ này chỉ dry-run")

    p = sub.add_parser("init", help="tạo plan.json từ skeleton")
    p.add_argument("dir")
    p.add_argument("--title")
    p.add_argument("--apply", action="store_true", help="ghi thật; không có cờ này chỉ dry-run")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("add-request", help="thêm yêu cầu của Lead vào sổ")
    common(p)
    p.add_argument("--ask", required=True, help="trích tối đa 200 ký tự")
    p.add_argument("--items", help="id việc, cách nhau dấu phẩy, ví dụ M41,M42")
    p.add_argument("--no-items-reason", help="dùng thay --items khi yêu cầu là luật chung, không có việc")
    p.set_defaults(fn=cmd_add_request)

    p = sub.add_parser("add-item", help="thêm việc vào plan")
    common(p)
    p.add_argument("--id")
    p.add_argument("--prefix", default="M", help="tiền tố khi tự cấp id (mặc định M)")
    p.add_argument("--title", required=True)
    p.add_argument("--phase", required=True)
    p.add_argument("--status", default="todo", choices=STATUSES)
    p.add_argument("--detail", action="append", help="một dòng chi tiết, dùng nhiều lần")
    p.add_argument("--deps", default="", help="id việc phải xong trước, cách nhau dấu phẩy")
    p.add_argument("--source", required=True, help="tin Lead kèm giờ hoặc tài liệu nguồn")
    p.add_argument("--program", help="tên chương trình để đếm tiến độ")
    p.add_argument("--evidence")
    p.add_argument("--checked", help="bắt buộc khi --status need: đã kiểm Lead chưa duyệt ở đâu")
    p.set_defaults(fn=cmd_add_item)

    p = sub.add_parser("set-status", help="đổi trạng thái một việc")
    common(p)
    p.add_argument("id")
    p.add_argument("status", choices=STATUSES)
    p.add_argument("--evidence")
    p.add_argument("--checked")
    p.set_defaults(fn=cmd_set_status)

    p = sub.add_parser("progress", help="in tiến độ đếm từ file")
    common(p, write=False)
    p.add_argument("--program")
    p.set_defaults(fn=cmd_progress)

    p = sub.add_parser("lint", help="kiểm schema và logic")
    common(p, write=False)
    p.add_argument("--strict", action="store_true", help="cảnh báo cũng làm mã thoát 1")
    p.set_defaults(fn=cmd_lint)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except PlanError as e:
        if e.msg:
            print("LỖI: " + e.msg, file=sys.stderr)
        return e.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
