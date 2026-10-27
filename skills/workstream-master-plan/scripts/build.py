#!/usr/bin/env python3
"""Dựng master plan (HTML + MD) và báo cáo phiên (MD) từ plan.json, có assert.

Cách dùng:
  build.py --plan plan.json                       dry-run: dựng trong bộ nhớ, chạy assert, in số đếm
  build.py --plan plan.json --apply               ghi <slug>_master-plan.html và .md (ghi đè bản dựng cũ)
  build.py --plan plan.json --session-report --since "25/10/2026 08:00" [--apply]
                                                  thêm báo cáo phiên <slug>_bao-cao-phien_vN.md (N tăng dần)

Assert chạy cả khi dry-run. Build dừng, không ghi gì, nếu:
  - plan.json còn lỗi lint (ví dụ requests[].items là list, việc trỏ phase không có);
  - số việc trong HTML hoặc MD khác số việc trong plan.json;
  - một ngày có yêu cầu không hiện trong HTML hoặc MD (lỗi báo cáo v1 chỉ mở ngày cuối);
  - số dòng yêu cầu hoặc số nhóm việc đã xong render khác số trong data;
  - tổng số đếm trạng thái khác số việc.

Giờ dựng lấy từ đồng hồ máy. Báo cáo phiên có dòng "Tiến độ chương trình x/y".
Mã thoát: 0 xong, 2 đầu vào sai hoặc lint lỗi, 3 lỗi đọc/ghi file, 5 assert thất bại.
Python 3.9+, chỉ dùng thư viện chuẩn, không tải font hay script ngoài.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan as P  # noqa: E402

ORDER = ["doing", "todo", "need", "wait", "other", "done"]
DAY_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})(?:/(\d{4}))?(?!\d)")
UNKNOWN_DAY = "unknown"


class AssertFail(Exception):
    pass


def slugify(text):
    t = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "workstream"


def md_inline(s):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(s))


def default_year(plan, ref):
    m = re.search(r"/(\d{4})\b", str(plan.get("updated", "")))
    return int(m.group(1)) if m else ref.year


def day_key(date_text, year):
    """Khoá ngày dạng YYYY-MM-DD, hoặc UNKNOWN_DAY khi không đọc được."""
    m = DAY_RE.match(date_text or "")
    if not m:
        return UNKNOWN_DAY
    d, mo, y = m.groups()
    try:
        return date(int(y) if y else year, int(mo), int(d)).isoformat()
    except ValueError:
        return UNKNOWN_DAY


def day_label(key):
    if key == UNKNOWN_DAY:
        return "Không rõ ngày"
    y, mo, d = key.split("-")
    return "%s/%s/%s" % (d, mo, y)


def request_days(plan, ref):
    year = default_year(plan, ref)
    days = {}
    for r in plan["requests"]:
        days.setdefault(day_key(r["date"], year), []).append(r)
    ordered = sorted(k for k in days if k != UNKNOWN_DAY)
    if UNKNOWN_DAY in days:
        ordered.append(UNKNOWN_DAY)
    return ordered, days


def sorted_items(items):
    return sorted(items, key=lambda i: ORDER.index(i["status"]))


# ---------------------------------------------------------------- HTML

CSS = """
:root{--bg:#f6f7fb;--card:#fff;--ink:#16181d;--muted:#5d6472;--line:#e3e6ee;--accent:#0a6fd6;
--doing:#0a6fd6;--todo:#5d6472;--need:#b45309;--wait:#7c6f00;--other:#7c3aed;--done:#15803d;--code:#eef0f6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1115;--card:#171a21;--ink:#e8eaf0;--muted:#9aa2b1;--line:#2a2f3a;--accent:#5aa9ff;
--doing:#5aa9ff;--todo:#9aa2b1;--need:#f0a14a;--wait:#d8c64a;--other:#b794ff;--done:#4ade80;--code:#232834}}
:root[data-theme="dark"]{--bg:#0f1115;--card:#171a21;--ink:#e8eaf0;--muted:#9aa2b1;--line:#2a2f3a;--accent:#5aa9ff;--doing:#5aa9ff;--todo:#9aa2b1;--need:#f0a14a;--wait:#d8c64a;--other:#b794ff;--done:#4ade80;--code:#232834}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px 64px}
.top{background:var(--accent);color:#fff;padding:26px 0 22px}.top h1{font-size:26px;line-height:1.2;margin:0 0 6px}.top p{margin:0;opacity:.92}
h2{font-size:19px;margin:34px 0 12px}h3{font-size:16px;margin:0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-top:-18px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:left;cursor:pointer;color:var(--ink);font:inherit}
.stat .n{display:block;font-size:24px;font-weight:700;line-height:1;margin-bottom:4px}.stat.on{outline:2px solid var(--accent)}
.f-doing .n{color:var(--doing)}.f-todo .n{color:var(--todo)}.f-need .n{color:var(--need)}.f-wait .n{color:var(--wait)}.f-other .n{color:var(--other)}.f-done .n{color:var(--done)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:760px){.grid2{grid-template-columns:1fr}}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}.box h2{margin-top:0;font-size:16px}
.box ul{margin:0;padding-left:18px}.box a{color:var(--ink);text-decoration:none}.box a:hover{text-decoration:underline}
.need{border-left:4px solid var(--need)}.next{border-left:4px solid var(--doing)}
.tools{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0 6px}.tools input{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);font:inherit}
.tools button{padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);cursor:pointer;font:inherit}
.phase{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:14px 0}
.phase header{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline}
.phid{display:inline-block;background:var(--accent);color:#fff;border-radius:6px;padding:1px 7px;font-size:13px;margin-right:4px}
.when,.muted{color:var(--muted);font-size:13px}.why{color:var(--muted);margin:6px 0 10px}
.item{border:1px solid var(--line);border-radius:10px;margin:8px 0;background:var(--bg)}
.item summary{list-style:none;cursor:pointer;display:flex;gap:10px;align-items:flex-start;padding:10px 12px}.item summary::-webkit-details-marker{display:none}
.iid{font-weight:700;font-size:13px;color:var(--muted);min-width:34px}.ititle{flex:1;font-weight:600}
.pill{font-size:12px;padding:2px 9px;border-radius:999px;white-space:nowrap;border:1px solid currentColor}
.p-doing{color:var(--doing)}.p-todo{color:var(--todo)}.p-need{color:var(--need)}.p-wait{color:var(--wait)}.p-other{color:var(--other)}.p-done{color:var(--done)}
.s-need{border-left:4px solid var(--need)}.s-doing{border-left:4px solid var(--doing)}.s-other{opacity:.85}
.ibody{padding:0 12px 12px 56px}@media(max-width:600px){.ibody{padding-left:12px}}.ibody ul{margin:4px 0 8px;padding-left:18px}
.src,.ev{margin:4px 0;font-size:13px;color:var(--muted)}
.deps{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.dep{font-size:12px;padding:1px 8px;border-radius:6px;background:var(--code);color:var(--ink);text-decoration:none}
code{background:var(--code);padding:1px 5px;border-radius:5px;font-size:12.5px;word-break:break-all}
.chains{columns:2;column-gap:24px;padding-left:18px}@media(max-width:760px){.chains{columns:1}}.chains li{break-inside:avoid;margin:3px 0}
.tblwrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}
td:first-child{white-space:nowrap;color:var(--muted)}
.day{margin:14px 0}.day h3 .muted{margin-left:6px}
.hide{display:none}footer{margin-top:30px;color:var(--muted);font-size:13px}
"""

JS = """
const items=[...document.querySelectorAll('.item')];let f=null;
function apply(){const q=document.getElementById('q').value.trim().toLowerCase();
items.forEach(e=>{const ok=(!f||e.dataset.status===f)&&(!q||e.dataset.text.includes(q));e.classList.toggle('hide',!ok);});
document.querySelectorAll('.phase').forEach(s=>s.classList.toggle('hide',![...s.querySelectorAll('.item')].some(e=>!e.classList.contains('hide'))));
document.querySelectorAll('.stat[data-f]').forEach(b=>b.classList.toggle('on',b.dataset.f===f));}
document.querySelectorAll('.stat[data-f]').forEach(b=>b.onclick=()=>{f=(f===b.dataset.f)?null:b.dataset.f;apply();});
document.getElementById('q').oninput=apply;
document.getElementById('clear').onclick=()=>{f=null;document.getElementById('q').value='';apply();};
document.getElementById('openall').onclick=()=>items.forEach(e=>e.open=true);
document.querySelectorAll('a.dep,.box a').forEach(a=>a.addEventListener('click',()=>{const t=document.querySelector(a.getAttribute('href'));if(t&&t.tagName==='DETAILS')t.open=true;}));
"""


def render_html(plan, ref):
    items = plan["items"]
    by_id = {i["id"]: i for i in items}
    counts = {k: sum(1 for i in items if i["status"] == k) for k in ORDER}

    def chip(i, prefix):
        it = by_id.get(i)
        t = html.escape(it["title"]) if it else ""
        return '<a class="dep" href="#%s" title="%s">%s %s</a>' % (html.escape(i), t, prefix, html.escape(i))

    def item_html(it):
        lab, cls = P.STATUS_LABEL[it["status"]], it["status"]
        deps = "".join(chip(d, "chờ") for d in it.get("deps", []))
        blocks = "".join(chip(b, "mở") for b in it.get("blocks", []))
        det = "".join("<li>%s</li>" % md_inline(x) for x in it.get("detail", []))
        ev = '<p class="ev"><b>Bằng chứng:</b> %s</p>' % md_inline(it["evidence"]) if it.get("evidence") else ""
        prog = '<p class="src"><b>Chương trình:</b> %s</p>' % md_inline(it["program"]) if it.get("program") else ""
        chk = '<p class="src"><b>Đã kiểm chưa duyệt:</b> %s</p>' % md_inline(it["need_checked"]) if it.get("need_checked") else ""
        text = (it["id"] + " " + it["title"] + " " + " ".join(it.get("detail", []))).lower()
        return ('<details class="item s-%s" id="%s" data-status="%s" data-text="%s">'
                '<summary><span class="iid">%s</span><span class="ititle">%s</span><span class="pill p-%s">%s</span></summary>'
                '<div class="ibody"><ul>%s</ul><p class="src"><b>Nguồn:</b> %s</p>%s%s%s<div class="deps">%s%s</div></div></details>') % (
            cls, html.escape(it["id"]), it["status"], html.escape(text), html.escape(it["id"]), md_inline(it["title"]),
            cls, lab, det, md_inline(it.get("source", "")), prog, ev, chk, deps, blocks)

    need = [i for i in items if i["status"] == "need"]
    nxt = [i for i in items if i["status"] in ("doing", "todo")][:8]
    edges = [(d, i["id"]) for i in items for d in i.get("deps", [])]
    chains = "".join('<li>%s → %s <span class="muted">%s</span></li>' % (
        chip(a, ""), chip(b, ""), html.escape(by_id[b]["title"])) for a, b in edges)

    phase_html = ""
    for ph in plan["phases"]:
        its = sorted_items([i for i in items if i["phase"] == ph["id"]])
        n_open = sum(1 for i in its if i["status"] != "done")
        phase_html += ('<section class="phase"><header><h3><span class="phid">%s</span> %s</h3>'
                       '<span class="when">%s · %d việc mở</span></header><p class="why">%s</p>%s</section>') % (
            html.escape(ph["id"]), html.escape(ph["name"]), html.escape(ph["when"]), n_open, md_inline(ph["why"]),
            "".join(item_html(i) for i in its))

    done_html = "".join('<li class="donegroup"><b>%s</b> %s <span class="muted">%s</span></li>' % (
        html.escape(d["when"]), md_inline(d["what"]), md_inline(d["evidence"])) for d in plan["done"])

    ordered, days = request_days(plan, ref)
    day_html = ""
    for k in ordered:
        rows = "".join('<tr class="reqrow"><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            html.escape(r["date"]), md_inline(r["ask"]), md_inline(r["items"])) for r in days[k])
        day_html += ('<section class="day" data-day="%s"><h3>%s <span class="muted">%d yêu cầu</span></h3>'
                     '<div class="box tblwrap"><table><thead><tr><th>Thời điểm</th><th>Lead yêu cầu</th><th>Việc trong plan</th></tr></thead>'
                     '<tbody>%s</tbody></table></div></section>') % (k, day_label(k), len(days[k]), rows)

    need_html = "".join('<li><a href="#%s"><b>%s</b> %s</a></li>' % (
        html.escape(i["id"]), html.escape(i["id"]), md_inline(i["title"])) for i in need)
    next_html = "".join('<li><a href="#%s"><b>%s</b> %s</a></li>' % (
        html.escape(i["id"]), html.escape(i["id"]), md_inline(i["title"])) for i in nxt)
    stat_html = "".join('<button class="stat f-%s" data-f="%s"><span class="n">%d</span><span>%s</span></button>' % (
        k, k, counts[k], P.STATUS_LABEL[k]) for k in ORDER if counts[k])
    rules_html = "".join("<li>%s</li>" % md_inline(r) for r in plan["rules"])
    span = ("%s đến %s" % (day_label(ordered[0]), day_label([k for k in ordered if k != UNKNOWN_DAY][-1]))
            if [k for k in ordered if k != UNKNOWN_DAY] else "chưa có ngày")
    return '''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title><style>%(css)s</style></head><body>
<div class="top"><div class="wrap"><h1>%(title)s</h1><p>Dựng %(stamp)s · %(progress)s · Yêu cầu %(span)s</p></div></div>
<div class="wrap">
<div class="stats">%(stats)s</div>
<div class="grid2" style="margin-top:16px">
<div class="box need"><h2>Cần Lead quyết (%(nneed)d)</h2><ul>%(need)s</ul></div>
<div class="box next"><h2>Làm tiếp</h2><ul>%(next)s</ul></div>
</div>
<div class="tools"><input id="q" placeholder="Tìm việc theo id hoặc chữ"><button id="openall">Mở hết</button><button id="clear">Bỏ lọc</button></div>
<h2>Các đợt và việc</h2>
%(phases)s
<h2>Chuỗi phụ thuộc</h2>
<div class="box"><p class="muted" style="margin-top:0">Việc bên trái phải xong trước việc bên phải.</p><ul class="chains">%(chains)s</ul></div>
<h2>Luật chạy</h2><div class="box"><ul>%(rules)s</ul></div>
<h2 id="done">Nhóm việc đã xong (%(ndone)d)</h2><div class="box"><ul>%(done)s</ul></div>
<h2>Nhật ký yêu cầu theo ngày (%(nreq)d)</h2>
%(days)s
<footer>Dựng từ <code>plan.json</code> bằng <code>build.py</code>. Sửa plan.json, không sửa file này.</footer>
</div><script>%(js)s</script></body></html>''' % {
        "title": html.escape(plan["title"]), "css": CSS, "js": JS, "stamp": P.fmt_stamp(ref),
        "progress": html.escape(P.progress_line(plan)), "span": html.escape(span), "stats": stat_html,
        "nneed": len(need), "need": need_html, "next": next_html, "phases": phase_html, "chains": chains,
        "rules": rules_html, "ndone": len(plan["done"]), "done": done_html, "nreq": len(plan["requests"]), "days": day_html}


# ---------------------------------------------------------------- MD

def render_md(plan, ref):
    items = plan["items"]
    md = ["# %s" % plan["title"], "",
          "Dựng %s từ `plan.json` bằng `build.py`. Sửa plan.json, không sửa file này." % P.fmt_stamp(ref), "",
          "**%s**" % P.progress_line(plan), "", "## Luật chạy", ""]
    md += ["- %s" % r for r in plan["rules"]]
    for ph in plan["phases"]:
        md += ["", "## %s. %s (%s)" % (ph["id"], ph["name"], ph["when"]), "", ph["why"], ""]
        for it in sorted_items([i for i in items if i["phase"] == ph["id"]]):
            mark = "x" if it["status"] == "done" else " "
            dep = " Chờ: %s." % ", ".join(it["deps"]) if it.get("deps") else ""
            prog = " [%s]" % it["program"] if it.get("program") else ""
            md.append("- [%s] **%s** %s · %s.%s%s" % (mark, it["id"], it["title"], P.STATUS_LABEL[it["status"]], dep, prog))
            md += ["  - %s" % x for x in it.get("detail", [])]
    md += ["", "## Nhóm việc đã xong", ""] + ["- %s: %s (%s)" % (d["when"], d["what"], d["evidence"]) for d in plan["done"]]
    ordered, days = request_days(plan, ref)
    md += ["", "## Nhật ký yêu cầu theo ngày"]
    for k in ordered:
        md += ["", "### Ngày %s (%d yêu cầu)" % (day_label(k), len(days[k])), ""]
        md += ["- %s: %s -> %s" % (r["date"], r["ask"], r["items"]) for r in days[k]]
    return "\n".join(md) + "\n"


# ---------------------------------------------------------------- báo cáo phiên

def render_session_report(plan, ref, since):
    items = plan["items"]
    stamped = [(i, P.parse_stamp(i.get("status_at"), ref)) for i in items]
    done_now = [i for i, t in stamped if i["status"] == "done" and t is not None and t >= since]
    new_reqs = [r for r in plan["requests"] if (P.parse_stamp(r["date"], ref) or datetime.min) >= since]
    groups = {s: [i for i in items if i["status"] == s] for s in ORDER}
    _, _, by_prog, counts = P.progress(plan)
    lines = ["# Báo cáo phiên: %s" % plan["title"], "",
             "Dựng %s. Tính từ %s." % (P.fmt_stamp(ref), P.fmt_stamp(since)), "",
             "**%s**" % P.progress_line(plan)]
    for name in sorted(k for k in by_prog if k):
        d, t = by_prog[name]
        lines.append("- %s: %d/%d" % (name, d, t))
    lines += ["", "Trạng thái: " + " · ".join("%s %d" % (P.STATUS_LABEL[s], counts[s]) for s in ORDER if counts[s]), ""]
    lines += ["## Yêu cầu mới trong phiên (%d)" % len(new_reqs), ""]
    lines += ["- %s: %s -> %s" % (r["date"], r["ask"], r["items"]) for r in new_reqs] or ["- Không có."]
    lines += ["", "## Xong trong phiên (%d)" % len(done_now), ""]
    lines += ["- **%s** %s. Bằng chứng: %s" % (i["id"], i["title"], i.get("evidence", "")) for i in done_now] or ["- Không có."]
    for s in ("doing", "need", "wait", "other"):
        lines += ["", "## %s (%d)" % (P.STATUS_LABEL[s], len(groups[s])), ""]
        rows = []
        for i in groups[s]:
            extra = " Đã kiểm chưa duyệt: %s" % i["need_checked"] if s == "need" and i.get("need_checked") else ""
            dep = " Chờ: %s." % ", ".join(i["deps"]) if i.get("deps") else ""
            rows.append("- **%s** %s.%s%s" % (i["id"], i["title"], dep, extra))
        lines += rows or ["- Không có."]
    return "\n".join(lines) + "\n", {"new_reqs": len(new_reqs), "done_now": len(done_now), "counts": counts}


# ---------------------------------------------------------------- assert

def check_render(plan, html_text, md_text, ref):
    """Ném AssertFail nếu bản render không đủ số việc, số ngày, số yêu cầu."""
    fails = []
    n_items = len(plan["items"])
    h_items = len(re.findall(r'<details class="item ', html_text))
    m_items = len(re.findall(r"^- \[[ x]\] \*\*", md_text, re.M))
    if h_items != n_items:
        fails.append("HTML có %d việc, data có %d" % (h_items, n_items))
    if m_items != n_items:
        fails.append("MD có %d việc, data có %d" % (m_items, n_items))
    ordered, days = request_days(plan, ref)
    h_days = re.findall(r'<section class="day" data-day="([^"]+)"', html_text)
    m_days = re.findall(r"^### Ngày (.+?) \(\d+ yêu cầu\)$", md_text, re.M)
    if sorted(h_days) != sorted(ordered):
        fails.append("HTML thiếu ngày: data %s, render %s" % (ordered, h_days))
    if m_days != [day_label(k) for k in ordered]:
        fails.append("MD thiếu ngày: data %s, render %s" % ([day_label(k) for k in ordered], m_days))
    h_rows = len(re.findall(r'<tr class="reqrow">', html_text))
    if h_rows != len(plan["requests"]):
        fails.append("HTML có %d dòng yêu cầu, data có %d" % (h_rows, len(plan["requests"])))
    h_done = len(re.findall(r'<li class="donegroup">', html_text))
    if h_done != len(plan["done"]):
        fails.append("HTML có %d nhóm việc xong, data có %d" % (h_done, len(plan["done"])))
    total = sum(1 for i in plan["items"] if i["status"] in ORDER)
    if total != n_items:
        fails.append("tổng đếm trạng thái %d khác số việc %d" % (total, n_items))
    if fails:
        raise AssertFail("; ".join(fails))


def check_session_report(plan, text, meta):
    n = len(plan["items"])
    if sum(meta["counts"].values()) != n:
        raise AssertFail("báo cáo phiên: tổng đếm trạng thái %d khác số việc %d" % (sum(meta["counts"].values()), n))
    got = len(re.findall(r"^- \*\*[^*]+\*\* ", text, re.M))
    expect = meta["done_now"] + sum(1 for i in plan["items"] if i["status"] in ("doing", "need", "wait", "other"))
    if got != expect:
        raise AssertFail("báo cáo phiên có %d dòng việc, data cần %d" % (got, expect))


# ---------------------------------------------------------------- chính

def next_version_path(out_dir, stem):
    n = 1
    while (out_dir / ("%s_v%d.md" % (stem, n))).exists():
        n += 1
    return out_dir / ("%s_v%d.md" % (stem, n))


def build_parser():
    ap = argparse.ArgumentParser(prog="build.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--plan", default="plan.json", help="đường dẫn plan.json (mặc định ./plan.json)")
    ap.add_argument("--out-dir", help="thư mục ghi (mặc định thư mục của plan.json)")
    ap.add_argument("--slug", help="tiền tố tên file (mặc định lấy từ title)")
    ap.add_argument("--apply", action="store_true", help="ghi thật; không có cờ này chỉ dry-run")
    ap.add_argument("--session-report", action="store_true", help="dựng thêm báo cáo phiên")
    ap.add_argument("--since", help="mốc đầu phiên 'DD/MM/YYYY HH:MM' (mặc định 00:00 hôm nay)")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    ref = P.now()
    try:
        plan, _ = P.load_plan(args.plan)
    except P.PlanError as e:
        print("LỖI: " + e.msg, file=sys.stderr)
        return e.code
    errs, warns = P.validate(plan, ref)
    if errs:
        print("LỖI: plan.json còn %d lỗi, build dừng. Chạy plan.py lint:" % len(errs), file=sys.stderr)
        for e in errs[:10]:
            print("  - " + e, file=sys.stderr)
        return 2
    for w in warns:
        print("CẢNH BÁO: " + w, file=sys.stderr)

    since = None
    if args.session_report:
        if args.since:
            since = P.parse_stamp(args.since, ref)
            if since is None:
                print("LỖI: --since sai dạng, dùng 'DD/MM/YYYY HH:MM'", file=sys.stderr)
                return 2
        else:
            since = ref.replace(hour=0, minute=0, second=0, microsecond=0)

    out_dir = Path(args.out_dir) if args.out_dir else Path(args.plan).resolve().parent
    slug = args.slug or slugify(plan["title"])
    html_text, md_text = render_html(plan, ref), render_md(plan, ref)
    outputs = [(out_dir / ("%s_master-plan.html" % slug), html_text), (out_dir / ("%s_master-plan.md" % slug), md_text)]
    try:
        check_render(plan, html_text, md_text, ref)
        if args.session_report:
            rep, meta = render_session_report(plan, ref, since)
            check_session_report(plan, rep, meta)
            outputs.append((next_version_path(out_dir, "%s_bao-cao-phien" % slug), rep))
    except AssertFail as e:
        print("LỖI assert: %s. Không ghi file." % e, file=sys.stderr)
        return 5

    counts = {k: sum(1 for i in plan["items"] if i["status"] == k) for k in ORDER}
    print("ok", counts)
    print(P.progress_line(plan))
    if args.apply:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            for path, text in outputs:
                path.write_text(text, encoding="utf-8")
                print("Đã ghi %s" % path)
        except OSError as e:
            print("LỖI: không ghi được: %s" % e, file=sys.stderr)
            return 3
    else:
        for path, text in outputs:
            print("DRY-RUN (chưa ghi): %s, %d byte" % (path, len(text.encode("utf-8"))))
        print("Thêm --apply để ghi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
