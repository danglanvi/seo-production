#!/usr/bin/env python3
"""Dựng trang chờ Lead quyết (HTML) từ cau-hoi.json.

Chế độ local: file HTML đầy đủ, nút "Chép câu trả lời", lưu localStorage.
Chế độ --artifact: mảnh HTML cho Artifact tool (token màu ở :root, dark mode,
db collection/doc lưu câu trả lời, nút "Lưu, tôi trả lời xong", nút Chép dự phòng).

Mặc định dry-run: kiểm schema, chọn tên file, in kế hoạch, không ghi gì.
Thêm --write để ghi. Script không gọi Artifact tool, không gọi mạng.
Python stdlib, chạy được trên Python 3.9.
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

DEFAULT_RULE = (
    "Câu nào anh để trống, phiên làm theo đề xuất. Ngoại lệ: mục có nhãn "
    "\"Phải chọn\" (xoá, gửi ra ngoài, tiền, pháp lý, config sống) chỉ chạy khi anh chọn rõ."
)
BLANK_DEFAULT = "(để trống, theo đề xuất)"
BLANK_HOLD = "(để trống, chưa làm)"
RESERVED_IDS = {
    "toc", "out", "copy", "done", "clear", "cnt", "sync", "view-quyet",
    "view-baocao", "tab-quyet", "tab-baocao", "dp-root",
}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SENSITIVE = [
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "địa chỉ IP"),
    (re.compile(r"(?i)\b(?:api[_-]?key|secret|password|passwd|access[_-]?token|auth[_-]?token)\s*[:=]\s*[^\s<]{6,}"), "secret hoặc mật khẩu"),
    (re.compile(r"(?i)mật khẩu\s*[:=]\s*[^\s<]{4,}"), "mật khẩu"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "khoá dạng sk-"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._-]{12,}"), "Bearer token"),
    (re.compile(r"\bAKIA[0-9A-Z]{12,}"), "khoá AWS"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"), "private key"),
    (re.compile(r"\.agent-secrets"), "đường dẫn secret"),
    (re.compile(r"(?i)\bssh\s+[\w.-]+@[\w.-]+"), "lệnh ssh tới host"),
]


class SpecError(Exception):
    def __init__(self, problems):
        super().__init__("; ".join(problems))
        self.problems = list(problems)


# ---------------------------------------------------------------- văn bản

def esc(s):
    return htmllib.escape(str(s), quote=True)


_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline(text):
    """Escape rồi đổi `code`, **đậm**, [chữ](link) thành thẻ. Không cho HTML thô."""
    t = esc(text)
    t = _CODE.sub(lambda m: "<code>" + m.group(1) + "</code>", t)
    t = _BOLD.sub(lambda m: "<b>" + m.group(1) + "</b>", t)

    def link(m):
        href = m.group(2)
        if re.match(r"(?i)^\s*(javascript|data|vbscript):", htmllib.unescape(href)):
            return m.group(1)
        return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (href, m.group(1))

    return _LINK.sub(link, t)


def norm_ws(s):
    return " ".join(str(s).split())


# ---------------------------------------------------------------- schema

def _is_url(src):
    return bool(re.match(r"(?i)^(https?:)?//", src)) or src.startswith("data:")


def load_spec(path, check_files=True, artifact=False):
    """Đọc cau-hoi.json, kiểm và chuẩn hoá. Lỗi → SpecError (danh sách lỗi)."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SpecError(["không thấy file: %s" % path])
    except json.JSONDecodeError as e:
        raise SpecError(["JSON hỏng: %s" % e])
    if not isinstance(raw, dict):
        raise SpecError(["gốc JSON phải là object"])
    pr = []
    base = path.resolve().parent
    spec = dict(raw)
    spec["_base"] = str(base)
    for k in ("project", "title"):
        if not str(raw.get(k, "")).strip():
            pr.append("thiếu trường bắt buộc: %s" % k)
    if raw.get("project") and not re.match(r"^[a-z0-9][a-z0-9-]*$", str(raw["project"])):
        pr.append("project chỉ gồm a-z, 0-9, dấu gạch: %r" % raw["project"])
    cards = raw.get("cards")
    if not isinstance(cards, list) or not cards:
        pr.append("cards phải là danh sách không rỗng")
        raise SpecError(pr)
    seen_ids, seen_labels = set(), set()
    out_cards = []
    for i, c in enumerate(cards):
        where = "cards[%d]" % i
        if not isinstance(c, dict):
            pr.append("%s phải là object" % where)
            continue
        c = dict(c)
        cid = str(c.get("id", ""))
        where = "thẻ %r" % (cid or i)
        if not ID_RE.match(cid):
            pr.append("%s: id phải khớp [a-z0-9_-]" % where)
        elif cid in RESERVED_IDS:
            pr.append("%s: id trùng id hệ thống" % where)
        elif cid in seen_ids:
            pr.append("%s: id bị trùng" % where)
        seen_ids.add(cid)
        label = str(c.get("label") or c.get("title") or "").strip()
        if not label:
            pr.append("%s: thiếu label hoặc title" % where)
        if label in seen_labels:
            pr.append("%s: label %r bị trùng, câu trả lời sẽ khó đọc" % (where, label))
        seen_labels.add(label)
        c["label"] = label
        if not str(c.get("title", "")).strip():
            pr.append("%s: thiếu title" % where)
        c["toc"] = str(c.get("toc") or c.get("title") or "")
        qs = c.get("questions") or []
        kind = c.get("kind") or ("question" if qs else "info")
        if kind not in ("question", "info", "done"):
            pr.append("%s: kind chỉ nhận question, info, done" % where)
        c["kind"] = kind
        if kind == "question":
            ctx = c.get("context")
            if not isinstance(ctx, list) or not [x for x in ctx if str(x).strip()]:
                pr.append("%s: thiếu context (danh sách bối cảnh)" % where)
            if not str(c.get("risk_if_skipped", "")).strip():
                pr.append("%s: thiếu risk_if_skipped" % where)
            if not isinstance(c.get("touches_live"), bool):
                pr.append("%s: thiếu touches_live (true hoặc false)" % where)
            if not qs:
                pr.append("%s: thẻ question cần ít nhất 1 câu hỏi" % where)
        elif qs:
            pr.append("%s: thẻ %s không có câu hỏi, đổi kind thành question" % (where, kind))
        nq = []
        for j, q in enumerate(qs):
            qw = "%s câu %d" % (where, j + 1)
            if not isinstance(q, dict):
                pr.append("%s phải là object" % qw)
                continue
            q = dict(q)
            if not str(q.get("text", "")).strip():
                pr.append("%s: thiếu text" % qw)
            if len(qs) > 1 and not str(q.get("key", "")).strip():
                pr.append("%s: thẻ nhiều câu hỏi, mỗi câu cần key" % qw)
            key = str(q.get("key", "")).strip()
            q["name"] = cid if not key else "%s.%s" % (cid, key)
            q["short"] = str(q.get("short") or q.get("text") or "").strip()
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 2:
                pr.append("%s: cần ít nhất 2 phương án" % qw)
                nq.append(q)
                continue
            no, vals, nrec = [], set(), 0
            for k, o in enumerate(opts):
                if not isinstance(o, dict) or not str(o.get("label", "")).strip():
                    pr.append("%s phương án %d: thiếu label" % (qw, k + 1))
                    continue
                o = dict(o)
                o["value"] = str(o.get("value") or o["label"]).strip()
                o["recommended"] = bool(o.get("recommended"))
                o["destructive"] = bool(o.get("destructive") or o.get("xoa"))
                if o["value"] in vals:
                    pr.append("%s: value trùng %r" % (qw, o["value"]))
                vals.add(o["value"])
                nrec += o["recommended"]
                no.append(o)
            if nrec != 1:
                pr.append("%s: cần đúng 1 phương án recommended, đang có %d" % (qw, nrec))
            q["options"] = no
            nq.append(q)
        c["questions"] = nq
        images = c.get("images") or []
        nimg = []
        for k, im in enumerate(images):
            if not isinstance(im, dict) or not str(im.get("src", "")).strip():
                pr.append("%s ảnh %d: thiếu src" % (where, k + 1))
                continue
            src = str(im["src"])
            if _is_url(src):
                if artifact and not src.startswith(("http", "//", "data:")):
                    pr.append("%s ảnh %d: src không dùng được trong artifact" % (where, k + 1))
            else:
                if artifact:
                    pr.append("%s ảnh %d: ảnh cục bộ không chạy trên artifact, dùng URL https hoặc data:" % (where, k + 1))
                if check_files and not (base / src).is_file():
                    pr.append("%s ảnh %d: không thấy file %s" % (where, k + 1, src))
            nimg.append(dict(im))
        c["images"] = nimg
        for b in c.get("blocks") or []:
            if not isinstance(b, dict) or b.get("type") not in BLOCK_TYPES:
                pr.append("%s: block lạ %r (nhận %s)" % (where, (b or {}).get("type") if isinstance(b, dict) else b, ", ".join(sorted(BLOCK_TYPES))))
        out_cards.append(c)
    spec["cards"] = out_cards
    rf = raw.get("report_html_file")
    if rf:
        rp = base / rf
        if check_files and not rp.is_file():
            pr.append("không thấy report_html_file: %s" % rf)
        elif check_files and re.search(r"(?i)<script", rp.read_text(encoding="utf-8")):
            pr.append("report_html_file chứa <script>, bị từ chối")
    db = raw.get("db") or {}
    spec["db"] = {"collection": str(db.get("collection") or "answers"), "doc": str(db.get("doc") or "lead")}
    if pr:
        raise SpecError(pr)
    return spec


BLOCK_TYPES = {"p", "h3", "list", "table", "stats", "note", "bars"}


# ---------------------------------------------------------------- dựng HTML

def render_blocks(blocks):
    out = []
    for b in blocks or []:
        t = b["type"]
        if t == "p":
            out.append('<p class="%s">%s</p>' % ("muted" if b.get("muted", True) else "", inline(b.get("text", ""))))
        elif t == "h3":
            out.append("<h3>%s</h3>" % inline(b.get("text", "")))
        elif t == "list":
            out.append("<ul class=\"ctx\">%s</ul>" % "".join("<li>%s</li>" % inline(x) for x in b.get("items", [])))
        elif t == "note":
            out.append('<div class="note %s">%s</div>' % (esc(b.get("tone", "")), inline(b.get("text", ""))))
        elif t == "stats":
            out.append('<div class="stats">%s</div>' % "".join(
                '<div class="stat"><b>%s</b><span>%s</span></div>' % (esc(s.get("n", "")), inline(s.get("label", "")))
                for s in b.get("items", [])))
        elif t == "table":
            num = set(b.get("num_cols") or [])
            head = "".join("<th>%s</th>" % inline(h) for h in b.get("head", []))
            rows = []
            for r in b.get("rows", []):
                rows.append("<tr>%s</tr>" % "".join(
                    '<td%s>%s</td>' % (' class="n"' if ci in num else "", inline(v)) for ci, v in enumerate(r)))
            out.append('<div class="tbl"><table><tr>%s</tr>%s</table></div>' % (head, "".join(rows)))
        elif t == "bars":
            mx = float(b.get("max") or max([float(r.get("value", 0)) for r in b.get("rows", [])] + [1]))
            rows = []
            for r in b.get("rows", []):
                v = float(r.get("value", 0))
                pct = max(0.0, min(100.0, v / mx * 100.0))
                rows.append(
                    '<div class="row"><span class="lb">%s</span><span class="track"><span class="fill %s" style="width:%.1f%%"></span></span><span class="val">%s</span></div>'
                    % (inline(r.get("label", "")), esc(r.get("tone", "")), pct, esc(r.get("display", r.get("value", "")))))
            cap = '<figcaption>%s</figcaption>' % inline(b["caption"]) if b.get("caption") else ""
            out.append('<figure class="chartbox"><div class="ctitle">%s</div><div class="chart">%s</div>%s</figure>'
                       % (inline(b.get("title", "")), "".join(rows), cap))
    return "\n".join(out)


def render_images(images, base, out_dir):
    if not images:
        return ""
    figs = []
    for im in images:
        src = str(im["src"])
        if not _is_url(src):
            src = os.path.relpath(str((Path(base) / src).resolve()), str(Path(out_dir).resolve()))
            src = quote(src)
        cap = '<figcaption>%s</figcaption>' % inline(im["caption"]) if im.get("caption") else ""
        figs.append('<figure class="full"><a href="%s" target="_blank"><img loading="lazy" src="%s" alt="%s"></a>%s</figure>'
                    % (esc(src), esc(src), esc(im.get("alt") or im.get("caption") or ""), cap))
    return '<div class="shots">%s</div>' % "".join(figs)


def is_hold_q(card, q):
    rec_destructive = any(o["recommended"] and o["destructive"] for o in q["options"])
    return bool(card.get("touches_live")) or rec_destructive


def render_card(c, base, out_dir):
    kind = c["kind"]
    cls = "card" + ("" if kind == "question" else " " + kind)
    live = ""
    hold_any = any(is_hold_q(c, q) for q in c["questions"])
    if hold_any:
        live = '<em class="chip chip-x">Phải chọn</em>'
    parts = ['<section class="%s" id="%s" data-id="%s" data-t="%s">' % (cls, esc(c["id"]), esc(c["label"]), esc(c["toc"])),
             '  <h2><span class="id">%s</span> %s %s</h2>' % (esc(c["label"]), inline(c["title"]), live)]
    ctx = [x for x in (c.get("context") or []) if str(x).strip()]
    if ctx:
        parts.append('  <ul class="ctx">%s</ul>' % "".join("<li>%s</li>" % inline(x) for x in ctx))
    if str(c.get("risk_if_skipped", "")).strip():
        parts.append('  <p class="muted"><b>Nếu bỏ qua:</b> %s</p>' % inline(c["risk_if_skipped"]))
    if c.get("touches_live"):
        parts.append('  <div class="note warn">Mục này chạm site hoặc config đang chạy. Để trống nghĩa là chưa làm.</div>')
    elif hold_any:
        parts.append('  <div class="note warn">Phương án đề xuất là việc xoá hoặc gửi ra ngoài. Để trống nghĩa là chưa làm.</div>')
    blk = render_blocks(c.get("blocks"))
    if blk:
        parts.append(blk)
    img = render_images(c.get("images"), base, out_dir)
    if img:
        parts.append(img)
    for q in c["questions"]:
        opts = []
        for o in q["options"]:
            chips = ""
            if o["recommended"]:
                chips += '<em class="chip chip-rec">Đề xuất</em>'
            if o["destructive"]:
                chips += '<em class="chip chip-x">Xoá hoặc ra ngoài</em>'
            cons = '<small class="cons">%s</small>' % inline(o["consequence"]) if o.get("consequence") else ""
            opts.append('<label class="%s"><input type="radio" name="%s" value="%s"><span class="ot">%s%s</span>%s</label>'
                        % ("rec" if o["recommended"] else "", esc(q["name"]), esc(o["value"]), inline(o["label"]), cons, chips))
        parts.append('  <div class="q" data-q="%s"%s><b>%s</b><div class="opts">\n    %s</div></div>'
                     % (esc(q["short"]), ' data-hold="1"' if is_hold_q(c, q) else "", inline(q["text"]), "\n    ".join(opts)))
    want_note = c.get("note", kind == "question")
    if want_note:
        ph = c["note"].get("placeholder", "Ghi chú") if isinstance(c.get("note"), dict) else "Ghi chú"
        parts.append('  <textarea data-note="%s" aria-label="Ghi chú %s" placeholder="%s"></textarea>' % (esc(c["id"]), esc(c["label"]), esc(ph)))
    parts.append("</section>")
    return "\n".join(parts)


CSS = """
/* Layout: một cột đọc 1080px, thẻ xếp dọc, thanh trả lời cố định ở đáy. Token màu ở :root, dark mode theo hệ thống. */
:root{
  --bg:#f4f6fa;--paper:#ffffff;--ink:#122033;--muted:#566579;--line:#dfe5ee;--soft:#edf2f8;
  --accent:#0a6fb0;--accent-ink:#ffffff;--need:#b8235a;--good:#16794a;--rec:#fff6dc;--recb:#d9a800;--recink:#7a5c00;
  --warn:#fdecf2;--warnb:#f0b6ca;
  --f-display:"Bricolage Grotesque","Be Vietnam Pro",system-ui,sans-serif;
  --f-body:"Be Vietnam Pro",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0f141b;--paper:#171e27;--ink:#e6ebf2;--muted:#9aa7b8;--line:#2a3441;--soft:#1f2834;
  --accent:#5fb0ea;--accent-ink:#0b1622;--need:#f06a9a;--good:#53c08a;--rec:#2d2612;--recb:#a8841f;--recink:#e9c65a;
  --warn:#2c1720;--warnb:#7a3350;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0f141b;--paper:#171e27;--ink:#e6ebf2;--muted:#9aa7b8;--line:#2a3441;--soft:#1f2834;
  --accent:#5fb0ea;--accent-ink:#0b1622;--need:#f06a9a;--good:#53c08a;--rec:#2d2612;--recb:#a8841f;--recink:#e9c65a;
  --warn:#2c1720;--warnb:#7a3350;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.6 var(--f-body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:1080px;margin:0 auto;padding-block:24px 160px;display:flex;flex-direction:column;gap:20px}
h1{font:700 clamp(26px,4vw,34px)/1.15 var(--f-display);margin:4px 0 8px;text-wrap:balance;letter-spacing:-.01em}
.eyebrow{font-size:13px;color:var(--muted);letter-spacing:.02em}
.lede{color:var(--muted);margin:0;max-width:72ch}
.tabs{display:flex;gap:8px;flex-wrap:wrap}
.tabs button{font:600 15px var(--f-body);border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:7px 16px;cursor:pointer}
.tabs button[aria-selected="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.toc{display:flex;flex-wrap:wrap;gap:8px}
.toc a{font-size:14px;text-decoration:none;color:var(--ink);background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:5px 12px}
.toc a b{color:var(--need)}
.card{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:14px;scroll-margin-top:12px;min-width:0}
.card h2{margin:0;font:700 20px/1.3 var(--f-display);display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;text-wrap:balance}
.id{font:500 12px var(--f-mono);color:#fff;background:var(--need);border-radius:6px;padding:3px 8px;letter-spacing:.02em}
.card.info .id{background:var(--accent);color:var(--accent-ink)}
.card.done .id{background:var(--good);color:#fff}
.card h3{margin:6px 0 0;font:600 16px/1.35 var(--f-body)}
.ctx{margin:0;padding-left:20px}
.ctx li{margin-bottom:4px}
.muted{color:var(--muted);font-size:14px;margin:0}
.q{border-top:1px dashed var(--line);padding-top:12px;display:flex;flex-direction:column;gap:8px}
.q>b{font-size:16px}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opts label{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--line);border-radius:10px;padding:9px 12px;cursor:pointer;background:var(--paper);max-width:100%;flex:1 1 260px;min-width:0}
.opts label.rec{background:var(--rec);border-color:var(--recb)}
.opts .ot{flex:1;min-width:0}
.opts .cons{display:block;color:var(--muted);font-size:13px;margin-top:2px}
.chip{font-style:normal;font-size:11px;font-weight:700;white-space:nowrap;margin-left:auto;border-radius:6px;padding:1px 6px}
.chip-rec{color:var(--recink)}
.chip-x{color:#fff;background:var(--need)}
h2 .chip-x{margin-left:0}
.opts input{margin-top:5px;accent-color:var(--accent)}
.opts label:has(input:checked){outline:2px solid var(--accent);border-color:var(--accent)}
.opts label:focus-within{outline:2px solid var(--accent)}
textarea{width:100%;min-height:44px;border:1px solid var(--line);border-radius:10px;padding:8px 10px;font:inherit;font-size:14px;resize:vertical;background:var(--paper);color:var(--ink)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tbl{overflow-x:auto;min-width:0}
code{font:500 13px var(--f-mono);background:var(--soft);padding:1px 5px;border-radius:5px;word-break:break-word}
.note{background:var(--soft);border-radius:10px;padding:10px 12px;font-size:14px}
.note.key{background:var(--rec);border:1px solid var(--recb);font-size:15px}
.note.warn{background:var(--warn);border:1px solid var(--warnb);font-size:15px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.stat{background:var(--soft);border-radius:12px;padding:12px 14px}
.stat b{display:block;font:700 26px/1.2 var(--f-display);font-variant-numeric:tabular-nums}
.stat span{font-size:13px;color:var(--muted)}
.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
figure{margin:0;background:var(--soft);border:1px solid var(--line);border-radius:10px;overflow:hidden;min-width:0}
figure img{display:block;width:100%;height:auto;max-height:420px;object-fit:cover;object-position:top}
figure.full img{max-height:none;object-fit:contain}
figcaption{font-size:13px;padding:6px 10px;color:var(--muted)}
.chartbox{padding:12px 14px;background:var(--paper)}
.ctitle{font-weight:600;font-size:15px;margin-bottom:10px}
.chart{display:flex;flex-direction:column;gap:9px}
.row{display:grid;grid-template-columns:minmax(140px,230px) 1fr 64px;gap:10px;align-items:center;font-size:14px}
.track{display:block;background:var(--soft);border-radius:6px;height:18px;overflow:hidden}
.fill{display:block;height:100%;background:var(--accent);border-radius:6px;min-width:3px}
.fill.bad{background:var(--need)}.fill.ok{background:var(--good)}
.val{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--paper);border-top:1px solid var(--line);box-shadow:0 -6px 20px rgba(0,0,0,.08);padding-bottom:env(safe-area-inset-bottom,0px);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.bar .in{max-width:1080px;margin:0 auto;padding-block:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.bar button{font:600 15px var(--f-body);border:0;border-radius:10px;padding:10px 16px;background:var(--accent);color:var(--accent-ink);cursor:pointer}
.bar button.ghost{background:var(--soft);color:var(--ink)}
.bar button:focus-visible,.tabs button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.bar .cnt{font-size:14px;color:var(--muted)}
.bar .sync{font-size:13px;color:var(--muted);flex:1 1 220px;min-width:0}
#out{width:100%;min-height:120px;font:13px var(--f-mono);background:var(--paper);color:var(--ink);border:1px solid var(--line);border-radius:8px}
a{color:var(--accent)}
.report{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:24px;min-width:0}
.report h2{font:700 24px/1.25 var(--f-display);margin:0 0 8px;text-wrap:balance}
.report h3{font:700 19px/1.3 var(--f-display);margin:28px 0 8px;text-wrap:balance}
.report h4{font:600 16px/1.35 var(--f-body);margin:18px 0 6px}
.report p,.report li{max-width:78ch}
.report table{display:block;overflow-x:auto}
@media (max-width:600px){.card,.report{padding:16px}.row{grid-template-columns:1fr 60px}.row .lb{grid-column:1/-1}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

JS = r"""
(function(){
const CFG=__CFG__;
const cards=[...document.querySelectorAll('section.card[data-id]')];
const syncEl=document.getElementById('sync');
function status(t){if(syncEl)syncEl.textContent=t}

/* Tab */
const tabs={quyet:document.getElementById('tab-quyet'),baocao:document.getElementById('tab-baocao')};
const views={quyet:document.getElementById('view-quyet'),baocao:document.getElementById('view-baocao')};
function show(k){for(const n in tabs){if(!tabs[n])continue;const on=n===k;tabs[n].setAttribute('aria-selected',on);views[n].hidden=!on;views[n].style.display=on?(n==='quyet'?'flex':'block'):''}}
if(tabs.quyet&&tabs.baocao){tabs.quyet.onclick=()=>show('quyet');tabs.baocao.onclick=()=>show('baocao');if(location.hash==='#baocao')show('baocao')}

/* Trạng thái: lựa chọn theo tên radio, ghi chú theo id thẻ */
const st={choices:{},notes:{}};
try{const l=JSON.parse(localStorage.getItem(CFG.key)||'null');if(l&&l.choices){Object.assign(st.choices,l.choices);Object.assign(st.notes,l.notes||{})}}catch(e){}
function apply(){
  document.querySelectorAll('input[type=radio]').forEach(r=>{r.checked=st.choices[r.name]===r.value});
  document.querySelectorAll('textarea[data-note]').forEach(t=>{t.value=st.notes[t.dataset.note]||''});
}
function count(){const qs=document.querySelectorAll('.q');let n=0;qs.forEach(q=>{if(q.querySelector('input:checked'))n++});const c=document.getElementById('cnt');if(c)c.textContent='Đã chọn '+n+'/'+qs.length+' câu'}
function saveLocal(){try{localStorage.setItem(CFG.key,JSON.stringify(st))}catch(e){}}
function compose(){
  const out=[CFG.answerTitle];
  cards.forEach(c=>{
    const parts=[];
    c.querySelectorAll('.q').forEach(q=>{const v=q.querySelector('input:checked');parts.push(q.dataset.q+': '+(v?v.value:(q.dataset.hold?CFG.blankHold:CFG.blankDefault)))});
    const n=c.querySelector('textarea[data-note]');
    if(n&&n.value.trim())parts.push('Ghi chú: '+n.value.trim());
    if(parts.length)out.push(c.dataset.id+' — '+parts.join('; '));
  });
  return out.join('\n');
}
apply();count();

/* Nút Chép: gom mọi lựa chọn và mọi ô ghi chú, kể cả thẻ không có câu hỏi */
const copyBtn=document.getElementById('copy');
if(copyBtn)copyBtn.onclick=async()=>{
  const t=compose();const o=document.getElementById('out');o.value=t;
  try{await navigator.clipboard.writeText(t);status('Đã chép. Dán vào chat Claude.')}
  catch(e){o.hidden=false;o.select();status('Trình duyệt chặn chép tự động. Chữ đã chọn sẵn ở ô dưới, anh chép tay.')}
};
const clearBtn=document.getElementById('clear');
if(clearBtn)clearBtn.onclick=()=>{st.choices={};st.notes={};apply();saveLocal();count();status('Đã xoá lựa chọn.')};

/* Lưu db (chỉ bản artifact) */
let ref=null,saving=false,dirty=false,timer=null,doneFlag=false;
function hhmm(iso){try{const d=new Date(iso);return d.toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit'})+' '+d.toLocaleDateString('vi-VN',{day:'2-digit',month:'2-digit'})}catch(e){return ''}}
async function flush(){
  if(!ref)return;
  if(saving){dirty=true;return}
  saving=true;dirty=false;status('Đang lưu…');
  const now=new Date().toISOString();
  try{
    await ref.set({choices:st.choices,notes:st.notes,text:compose(),done:doneFlag,updated:now});
    status(doneFlag?'Đã lưu lúc '+hhmm(now)+'. Nhắn Claude "đã trả lời" để phiên đọc.':'Đã lưu lúc '+hhmm(now)+'. Claude đọc được câu trả lời.');
  }catch(e){
    const c=e&&e.code;
    if(c==='invalid_argument'||c==='not_granted'||c==='revoked'){ref=null;status('Tài khoản này không lưu được. Bấm "Chép câu trả lời" rồi dán vào chat.')}
    else status('Chưa lưu được ('+(c||'lỗi')+'). Lựa chọn vẫn giữ trên máy này; thử lại sau vài giây.');
  }
  saving=false;
  if(dirty&&ref)flush();
}
function queue(){saveLocal();count();if(!ref)return;clearTimeout(timer);timer=setTimeout(flush,700)}
document.querySelectorAll('input[type=radio]').forEach(r=>r.addEventListener('change',()=>{st.choices[r.name]=r.value;queue()}));
document.querySelectorAll('textarea[data-note]').forEach(t=>t.addEventListener('input',()=>{st.notes[t.dataset.note]=t.value;queue()}));
const doneBtn=document.getElementById('done');
if(doneBtn)doneBtn.onclick=()=>{doneFlag=true;saveLocal();if(ref){clearTimeout(timer);flush()}else{status('Chưa nối được kho lưu. Bấm "Chép câu trả lời" rồi dán vào chat.')}};

if(CFG.db){(async()=>{
  let db=null;
  try{db=window.claude&&window.claude.use?await window.claude.use('db'):null}catch(e){db=null}
  if(!db){status('Không nối được kho lưu. Bấm "Chép câu trả lời" rồi dán vào chat.');return}
  ref=db.doc(CFG.db.collection+'/'+CFG.db.doc);
  try{
    const s=await ref.get();
    if(s.exists){const d=s.data()||{};if(d.choices){st.choices=Object.assign({},d.choices);st.notes=Object.assign({},d.notes||{});doneFlag=!!d.done;apply();count();saveLocal()}status('Đã nạp câu trả lời lưu lúc '+hhmm(d.updated)+'.')}
    else status('Lựa chọn tự lưu cho Claude đọc.');
  }catch(e){status('Chưa đọc được kho lưu ('+(e&&e.code||'lỗi')+'). Lựa chọn vẫn lưu khi anh chọn.')}
})()}else{status('Lựa chọn tự lưu trên máy này. Chọn xong, bấm "Chép câu trả lời" rồi dán vào chat.')}
})();
"""


def page_key(spec, version):
    return "dp:%s:v%s" % (spec["project"], version)


def build_html(spec, version, out_dir, artifact=False):
    base = spec["_base"]
    key = page_key(spec, version)
    answer_title = spec.get("answer_title") or "Trả lời trang %s (bản %s):" % (spec["title"], version)
    cfg = {
        "key": key,
        "answerTitle": answer_title,
        "blankDefault": BLANK_DEFAULT,
        "blankHold": BLANK_HOLD,
        "db": spec["db"] if artifact else None,
    }
    cfg_js = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    js = JS.replace("__CFG__", cfg_js)
    cards_html = "\n\n".join(render_card(c, base, out_dir) for c in spec["cards"])
    toc = "".join('<a href="#%s"><b>%s</b> %s</a>' % (esc(c["id"]), esc(c["label"]), esc(c["toc"]))
                  for c in spec["cards"] if c["kind"] == "question" or c.get("in_toc"))
    nq = sum(len(c["questions"]) for c in spec["cards"])
    notes = []
    key_note = spec.get("key_note", DEFAULT_RULE)
    if key_note:
        notes.append('<div class="note key">%s</div>' % inline(key_note))
    for n in spec.get("notes") or []:
        notes.append('<div class="note %s">%s</div>' % (esc(n.get("kind", "")), inline(n.get("text", ""))))
    prev = spec.get("mo_tu_ban_cu") or []
    if prev:
        links = "".join('<li><a href="%s" target="_blank">%s</a>%s</li>' % (
            esc(p.get("href", "")), esc(p.get("label", p.get("href", ""))),
            (" " + inline(p["note"])) if p.get("note") else "") for p in prev)
        notes.append('<div class="note warn"><b>Bản cũ vẫn chờ anh trả lời.</b> Trả lời mỗi bản một lần dán.<ul>%s</ul></div>' % links)
    eyebrow = spec.get("eyebrow") or ("%s · bản %s" % (spec["project"], version))
    report = ""
    tabs = ""
    if spec.get("report_html_file"):
        rp = Path(base) / spec["report_html_file"]
        inner = rp.read_text(encoding="utf-8") if rp.is_file() else ""
        report = '<div id="view-baocao" role="tabpanel" aria-labelledby="tab-baocao" hidden>\n<article class="report">\n%s\n</article>\n</div>' % inner
        tabs = ('<div class="tabs" role="tablist">\n'
                '  <button type="button" role="tab" id="tab-quyet" aria-selected="true" aria-controls="view-quyet">Chờ quyết (%d câu)</button>\n'
                '  <button type="button" role="tab" id="tab-baocao" aria-selected="false" aria-controls="view-baocao">%s</button>\n</div>'
                % (nq, esc(spec.get("report_label") or "Báo cáo đầy đủ")))
    btn_done = '<button id="done" type="button">Lưu, tôi trả lời xong</button>\n  ' if artifact else ""
    btn_clear = "" if artifact else '<button id="clear" class="ghost" type="button">Xoá lựa chọn</button>\n  '
    body = """<div class="wrap" id="dp-root" data-storage-key="%(key)s">
<header>
  <div class="eyebrow">%(eyebrow)s</div>
  <h1>%(title)s</h1>
  <p class="lede">%(intro)s</p>
</header>
%(tabs)s
<div id="view-quyet" role="tabpanel" aria-labelledby="tab-quyet" style="display:flex;flex-direction:column;gap:20px">
%(notes)s
<nav class="toc" id="toc" aria-label="Danh sách câu hỏi">%(toc)s</nav>

%(cards)s
</div>
%(report)s
</div>

<div class="bar"><div class="in">
  %(btn_done)s<button id="copy" class="%(copycls)s" type="button">Chép câu trả lời</button>
  %(btn_clear)s<span class="cnt" id="cnt"></span>
  <span class="sync" id="sync" role="status" aria-live="polite"></span>
  <textarea id="out" readonly aria-label="Câu trả lời" hidden></textarea>
</div></div>
<script>%(js)s</script>
""" % {
        "key": esc(key), "eyebrow": inline(eyebrow), "title": inline(spec["title"]), "intro": inline(spec.get("intro", "")),
        "tabs": tabs, "notes": "\n".join(notes), "toc": toc, "cards": cards_html, "report": report,
        "btn_done": btn_done, "btn_clear": btn_clear, "copycls": "ghost" if artifact else "", "js": js,
    }
    page_title = esc(spec.get("page_title") or spec["title"])
    if artifact:
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Be+Vietnam+Pro:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap">\n')
        return ("<title>%s</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n%s<style>%s</style>\n\n%s"
                % (page_title, fonts, CSS, body))
    return ('<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s</body>\n</html>\n'
            % (page_title, CSS, body))


# ---------------------------------------------------------------- tên file, kiểm

def next_version(out_dir, project):
    rx = re.compile(r"^%s_cho-anh-quyet_v(\d+)(?:_artifact)?\.html$" % re.escape(project))
    best = 0
    d = Path(out_dir)
    if d.is_dir():
        for f in d.iterdir():
            m = rx.match(f.name)
            if m:
                best = max(best, int(m.group(1)))
    return best + 1


def scan_sensitive(text, extra=None):
    hits = []
    pats = list(SENSITIVE)
    for p in extra or []:
        pats.append((re.compile(p), "mẫu cấm riêng"))
    for rx, why in pats:
        for m in rx.finditer(text):
            s = m.group(0)
            hits.append("%s: %s" % (why, s if len(s) < 40 else s[:37] + "..."))
            break
    return hits


def expected_copy_text(spec, version, choices, notes):
    """Bản Python của compose() trong trang. Dùng để so với kết quả Chrome và parse_answer."""
    answer_title = spec.get("answer_title") or "Trả lời trang %s (bản %s):" % (spec["title"], version)
    out = [answer_title]
    for c in spec["cards"]:
        parts = []
        for q in c["questions"]:
            v = choices.get(q["name"])
            parts.append("%s: %s" % (q["short"], v if v else (BLANK_HOLD if is_hold_q(c, q) else BLANK_DEFAULT)))
        if c.get("note", c["kind"] == "question") and str(notes.get(c["id"], "")).strip():
            parts.append("Ghi chú: " + str(notes[c["id"]]).strip())
        if parts:
            out.append("%s — %s" % (c["label"], "; ".join(parts)))
    return "\n".join(out)


# ---------------------------------------------------------------- Chrome headless

def find_chrome():
    env = os.environ.get("CHROME_BIN")
    if env and os.path.exists(env):
        return env
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if os.path.exists(p):
            return p
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        w = shutil.which(n)
        if w:
            return w
    return None


_CHROME_MAIN = re.compile(r"/(?:Google Chrome|Chromium)\.app/Contents/MacOS/(?:Google Chrome|Chromium)(?:\s|$)")


def _ps_text():
    try:
        return subprocess.run(["ps", "-axo", "command="], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def chrome_window_state(ps_text):
    """co: có Chrome thường (không headless); chi-headless: chỉ có bản headless; khong: không có; None: không đọc được ps."""
    if ps_text is None:
        return None
    headless = False
    for line in ps_text.splitlines():
        if not _CHROME_MAIN.search(line) or "--type=" in line:
            continue
        if "--headless" in line:
            headless = True
            continue
        return "co"
    return "chi-headless" if headless else "khong"


def open_local(path, wait=2.0):
    """Mở file bằng Chrome thường rồi kiểm có tiến trình Chrome không headless. Trả (đạt, lời nhắn)."""
    r = subprocess.run(["open", "-a", "Google Chrome", str(path)])
    if r.returncode != 0:
        return False, "open -a trả mã %d" % r.returncode
    time.sleep(wait)
    st = chrome_window_state(_ps_text())
    if st == "co":
        return True, "Chrome thường đang chạy, trang đã mở."
    if st is None:
        return True, "Không đọc được danh sách tiến trình, chưa kiểm được cửa sổ."
    if st == "chi-headless":
        return False, "Chỉ thấy Chrome headless, cửa sổ có thể không hiện."
    return False, "Không thấy tiến trình Chrome sau khi mở."


def run_chrome_dump(chrome, page_path, timeout=90):
    prof = tempfile.mkdtemp(prefix="dp-chrome-")
    try:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               "--disable-extensions", "--user-data-dir=" + prof, "--virtual-time-budget=6000",
               "--dump-dom", Path(page_path).resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def _pre(dump, ident):
    m = re.search(r'<pre id="%s">(.*?)</pre>' % ident, dump, re.S)
    return htmllib.unescape(m.group(1)) if m else None


def chrome_press_copy(chrome, html_text, spec, version, choices, notes, artifact=False,
                      clipboard="ok", preload_storage=False, fake_db=False, click="copy"):
    """Mở trang trong Chrome headless, đặt lựa chọn, bấm nút. Trả dict kết quả.

    clipboard: ok (writeText thành công), deny (writeText bị từ chối, trang hiện ô chữ).
    preload_storage: đặt localStorage trước khi trang chạy (thử khôi phục), không bấm chọn.
    fake_db: giả window.claude.use('db') và ghi lại lệnh set.
    click: copy hoặc done.
    """
    key = page_key(spec, version)
    sel = {"choices": choices, "notes": notes}
    pre = ""
    if preload_storage:
        pre += "try{localStorage.setItem(%s,%s)}catch(e){}" % (json.dumps(key), json.dumps(json.dumps(sel)))
    if fake_db:
        pre += ("window.__sets=[];window.claude={use:async n=>n==='db'?{doc:p=>({get:async()=>({exists:false,data:()=>null}),"
                "set:async d=>{window.__sets.push({path:p,data:d})}})}:null};")
    if clipboard == "ok":
        pre += "Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>{window.__clip=t;return Promise.resolve()}}});"
    else:
        pre += "Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>Promise.reject(new Error('deny'))}});"
    drive = ""
    if not preload_storage:
        drive = ("const S=%s;document.querySelectorAll('input[type=radio]').forEach(r=>{if(S.choices[r.name]===r.value)r.click()});"
                 "document.querySelectorAll('textarea[data-note]').forEach(t=>{const v=S.notes[t.dataset.note];if(v!==undefined){t.value=v;t.dispatchEvent(new Event('input',{bubbles:true}))}});" % json.dumps(sel))
    post = ("<script>window.addEventListener('load',()=>{setTimeout(async()=>{try{%s"
            "document.getElementById('%s').click();await new Promise(r=>setTimeout(r,1500));"
            "const o=document.getElementById('out');const p=document.createElement('pre');p.id='__out';p.textContent=o?o.value:'';document.body.appendChild(p);"
            "const c=document.createElement('pre');c.id='__clip';c.textContent=window.__clip||'';document.body.appendChild(c);"
            "const s=document.createElement('pre');s.id='__sets';s.textContent=JSON.stringify(window.__sets||[]);document.body.appendChild(s);"
            "const l=document.createElement('pre');l.id='__ls';let lv='';try{lv=localStorage.getItem(%s)||''}catch(e){}l.textContent=lv;document.body.appendChild(l);"
            "const h=document.createElement('pre');h.id='__hidden';h.textContent=o?String(o.hidden):'';document.body.appendChild(h);"
            "}catch(e){const x=document.createElement('pre');x.id='__err';x.textContent=String(e);document.body.appendChild(x)}},300)});</script>"
            % (drive, click, json.dumps(key)))
    pre_tag = "<script>%s</script>" % pre
    if artifact:
        doc = ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               '</head><body>%s%s%s</body></html>' % (pre_tag, html_text, post))
    else:
        doc = html_text.replace("<body>", "<body>" + pre_tag, 1).replace("</body>", post + "</body>", 1)
    tmp = tempfile.mkdtemp(prefix="dp-page-")
    try:
        p = Path(tmp) / "page.html"
        p.write_text(doc, encoding="utf-8")
        rc, dump = run_chrome_dump(chrome, p)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    err = _pre(dump, "__err")
    sets = _pre(dump, "__sets")
    return {
        "rc": rc, "error": err, "out": _pre(dump, "__out"), "clip": _pre(dump, "__clip"),
        "sets": json.loads(sets) if sets else None, "storage": _pre(dump, "__ls"),
        "out_hidden": _pre(dump, "__hidden"), "dump_ok": "__out" in dump,
    }


def sample_selection(spec):
    """Chọn xác định: thẻ 0 chọn phương án đầu, thẻ 1 chọn phương án cuối, thẻ 2 để trống, lặp lại.
    Mọi thẻ có ô ghi chú, thẻ chẵn có ghi chú chứa ký tự đặc biệt và xuống dòng."""
    choices, notes = {}, {}
    n = 0
    for c in spec["cards"]:
        for q in c["questions"]:
            m = n % 3
            if m == 0:
                choices[q["name"]] = q["options"][0]["value"]
            elif m == 1:
                choices[q["name"]] = q["options"][-1]["value"]
            n += 1
        if c.get("note", c["kind"] == "question"):
            if len(notes) % 2 == 0:
                notes[c["id"]] = 'Ghi chú <b>"thử"</b> & dòng 1\ndòng 2 của %s' % c["id"]
            else:
                notes[c["id"]] = "Ghi chú ngắn " + c["id"]
    return choices, notes


def chrome_test(spec, version, html_local, html_artifact=None):
    """Bấm Chép trong Chrome và so với dữ liệu. Trả danh sách lỗi (rỗng là đạt)."""
    chrome = find_chrome()
    if not chrome:
        return ["không tìm thấy Chrome (đặt CHROME_BIN)"], True
    choices, notes = sample_selection(spec)
    want = expected_copy_text(spec, version, choices, notes)
    errs = []

    def check(name, res, field="clip"):
        if res["error"]:
            errs.append("%s: lỗi JS trong trang: %s" % (name, res["error"]))
            return
        if not res["dump_ok"]:
            errs.append("%s: Chrome không trả DOM (rc=%s)" % (name, res["rc"]))
            return
        got = res[field]
        if got != want:
            errs.append("%s: nội dung %s khác dữ liệu.\n--- mong đợi\n%s\n--- nhận được\n%s" % (name, field, want, got))

    r1 = chrome_press_copy(chrome, html_local, spec, version, choices, notes, clipboard="ok")
    check("local/chép", r1)
    if r1.get("storage"):
        try:
            st = json.loads(r1["storage"])
            if st.get("notes") != notes or st.get("choices") != choices:
                errs.append("local/localStorage: trạng thái lưu khác dữ liệu (mất ghi chú hoặc lựa chọn)")
        except ValueError:
            errs.append("local/localStorage: JSON hỏng")
    else:
        errs.append("local/localStorage: không lưu gì")
    r2 = chrome_press_copy(chrome, html_local, spec, version, choices, notes, clipboard="deny")
    check("local/chép bị chặn", r2, "out")
    if r2["out_hidden"] != "false":
        errs.append("local/chép bị chặn: ô chữ dự phòng không hiện")
    r3 = chrome_press_copy(chrome, html_local, spec, version, choices, notes, clipboard="ok", preload_storage=True)
    check("local/khôi phục từ localStorage", r3)
    if html_artifact:
        r4 = chrome_press_copy(chrome, html_artifact, spec, version, choices, notes, artifact=True, clipboard="ok", fake_db=True, click="done")
        if r4["error"] or not r4["dump_ok"]:
            errs.append("artifact/lưu: lỗi %s" % (r4["error"] or "không có DOM"))
        else:
            sets = r4["sets"] or []
            path = "%s/%s" % (spec["db"]["collection"], spec["db"]["doc"])
            last = sets[-1] if sets else None
            if not last or last["path"] != path:
                errs.append("artifact/lưu: không ghi vào %s" % path)
            else:
                d = last["data"]
                if d.get("choices") != choices or d.get("notes") != notes or d.get("text") != want or d.get("done") is not True:
                    errs.append("artifact/lưu: dữ liệu ghi vào db khác dữ liệu nhập (choices, notes, text hoặc done)")
        r5 = chrome_press_copy(chrome, html_artifact, spec, version, choices, notes, artifact=True, clipboard="ok", fake_db=False)
        check("artifact/chép dự phòng khi không có db", r5)
    return errs, False


# ---------------------------------------------------------------- ghi file

RESTORE_README = """# Khôi phục trang chờ quyết: {project} bản {n}

- Trang: `{html_name}` (bản artifact, mở local vẫn dùng được nút Chép).
- Dữ liệu dựng: `{spec_name}` (JSON, nguồn của trang).
- Câu trả lời lưu ở db của artifact: collection `{collection}`, doc `{doc}` (trường `choices`, `notes`, `text`, `done`).

Khôi phục khi đổi tài khoản Claude:
1. Publish lại `{html_name}` bằng Artifact tool với `capabilities: {{"db": {{}}}}`.
2. Nếu có bản JSON câu trả lời đã lưu, nạp lại bằng ArtifactData `set` vào `{collection}/{doc}`.
3. Đọc câu trả lời: ArtifactData `get` rồi chạy `parse_answer.py --spec {spec_name} --db <file.json>`.
"""


def write_outputs(spec, spec_path, out_dir, version, html_local, html_artifact, do_local, do_art):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = "%s_cho-anh-quyet_v%d" % (spec["project"], version)
    written = []

    def put(name, text):
        p = out_dir / name
        with open(str(p), "x", encoding="utf-8") as f:  # x: không ghi đè
            f.write(text)
        written.append(p)
        return p

    if do_local:
        put(stem + ".html", html_local)
    if do_art:
        put(stem + "_artifact.html", html_artifact)
        put(stem + "_khoi-phuc.md", RESTORE_README.format(
            project=spec["project"], n=version, html_name=stem + "_artifact.html", spec_name=stem + ".cau-hoi.json",
            collection=spec["db"]["collection"], doc=spec["db"]["doc"]))
    raw = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    raw["version"] = version
    raw["built"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    put(stem + ".cau-hoi.json", json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
    return written


def three_paths(p):
    p = Path(p).resolve()
    return {"tuyệt đối": str(p), "file URL": p.as_uri(), "tương đối từ thư mục hiện tại": os.path.relpath(str(p))}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Dựng trang chờ quyết từ cau-hoi.json. Mặc định dry-run: chỉ kiểm và in kế hoạch.",
        epilog="Mã thoát: 0 đạt; 2 spec hoặc tham số sai; 3 Chrome test lỗi; 4 chạm dữ liệu nhạy cảm; 5 không mở được Chrome; 6 thiếu Chrome.")
    ap.add_argument("spec", help="đường dẫn cau-hoi.json")
    ap.add_argument("--out", help="thư mục ghi (mặc định: thư mục của spec)")
    ap.add_argument("--artifact", action="store_true", help="dựng bản artifact thay cho bản local")
    ap.add_argument("--both", action="store_true", help="dựng cả bản local và bản artifact với cùng số bản")
    ap.add_argument("--write", action="store_true", help="ghi file (không có cờ này là dry-run)")
    ap.add_argument("--open", action="store_true", help='sau khi ghi, mở bản local bằng open -a "Google Chrome"')
    ap.add_argument("--chrome-test", action="store_true", help="bấm Chép trong Chrome headless và so với dữ liệu")
    ap.add_argument("--deny-file", help="file mẫu regex cấm riêng, mỗi dòng một mẫu (giữ ngoài repo)")
    ap.add_argument("--allow-sensitive", action="store_true", help="bỏ qua cổng quét secret, IP (không khuyến nghị)")
    ap.add_argument("--version", type=int, help="ép số bản (mặc định: số lớn nhất trong thư mục + 1)")
    args = ap.parse_args(argv)

    if args.open and not args.write:
        print("LỖI: --open cần --write", file=sys.stderr)
        return 2
    do_art = args.artifact or args.both
    do_local = (not args.artifact) or args.both
    out_dir = Path(args.out) if args.out else Path(args.spec).resolve().parent
    try:
        spec = load_spec(args.spec, artifact=do_art)
    except SpecError as e:
        print("LỖI schema (%d):" % len(e.problems), file=sys.stderr)
        for p in e.problems:
            print("  - " + p, file=sys.stderr)
        return 2
    version = args.version or next_version(out_dir, spec["project"])
    stem = "%s_cho-anh-quyet_v%d" % (spec["project"], version)
    if args.version and (out_dir / (stem + ".html")).exists():
        print("LỖI: %s đã tồn tại, không ghi đè" % (stem + ".html"), file=sys.stderr)
        return 2
    html_local = build_html(spec, version, out_dir, artifact=False) if do_local or args.chrome_test else None
    html_art = build_html(spec, version, out_dir, artifact=True) if do_art else None
    extra = []
    if args.deny_file:
        try:
            extra = [l.strip() for l in Path(args.deny_file).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        except OSError as e:
            print("LỖI: không đọc được --deny-file: %s" % e, file=sys.stderr)
            return 2
    hits = []
    for name, text in (("local", html_local if do_local else None), ("artifact", html_art)):
        if text:
            hits += ["%s: %s" % (name, h) for h in scan_sensitive(text, extra)]
    if hits and not args.allow_sensitive:
        print("LỖI: trang chứa dữ liệu nhạy cảm, không dựng:", file=sys.stderr)
        for h in hits:
            print("  - " + h, file=sys.stderr)
        return 4
    nq = sum(len(c["questions"]) for c in spec["cards"])
    nhold = sum(1 for c in spec["cards"] for q in c["questions"] if is_hold_q(c, q))
    print("%s: %d thẻ, %d câu hỏi, %d câu bắt buộc chọn tay." % ("GHI" if args.write else "DRY-RUN", len(spec["cards"]), nq, nhold))
    print("Số bản: v%d" % version)
    if args.chrome_test:
        errs, missing = chrome_test(spec, version, html_local, html_art)
        if missing:
            print("LỖI: " + errs[0], file=sys.stderr)
            return 6
        if errs:
            print("Chrome test: LỖI", file=sys.stderr)
            for e in errs:
                print("  - " + e, file=sys.stderr)
            return 3
        print("Chrome test: đạt (chép, chép bị chặn, khôi phục localStorage%s)" % (", lưu db, chép dự phòng" if html_art else ""))
    if not args.write:
        names = ([stem + ".html"] if do_local else []) + ([stem + "_artifact.html", stem + "_khoi-phuc.md"] if do_art else []) + [stem + ".cau-hoi.json"]
        print("Sẽ ghi vào %s:" % out_dir)
        for n in names:
            print("  - " + n)
        print("DRY-RUN: chưa ghi file. Thêm --write để ghi.")
        return 0
    try:
        written = write_outputs(spec, args.spec, out_dir, version, html_local, html_art, do_local, do_art)
    except FileExistsError as e:
        print("LỖI: file đã tồn tại, không ghi đè: %s" % e, file=sys.stderr)
        return 2
    for p in written:
        print("Đã ghi: " + str(p))
    main_file = written[0]
    for k, v in three_paths(main_file).items():
        print("  %s: %s" % (k, v))
    if args.open:
        if do_local:
            ok, msg = open_local(main_file)
            if not ok:
                print("LỖI: %s Đưa link file URL ở trên cho Lead." % msg, file=sys.stderr)
                return 5
            print("Mở Chrome: " + msg)
        else:
            print("Bản artifact không mở bằng --open. Publish bằng Artifact tool.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
