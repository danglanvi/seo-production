#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_deck.py — Ráp deck báo cáo tuần SEO từ content.yaml + skeleton + data tuần.

Mục tiêu 80/20: AI chỉ viết NHẬN XÉT/ACTION trong content.yaml nhỏ,
script này ráp toàn bộ HTML deck (bảng số từ data-ref, class pos/neg/mut,
breadcrumb + pill + brandbar + data-meta + page-no tự động).

Cách chạy:
  python3 build_deck.py --content content-w11.yaml \
      --skeleton deck-skeleton.html --datadir <weekdir> --out deck.html \
      [--logo-client logo.png] [--logo-gtv logo.png]

Schema content.yaml: xem references/content-schema.md của skill gtv-weekly-report.
Chỉ dùng stdlib + PyYAML. Exit non-zero khi FAIL validate.
"""
import argparse
import base64
import io
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("FAIL: thiếu PyYAML (pip install pyyaml)\n")
    sys.exit(2)

MINUS = "−"  # − dùng cho bảng movers (theo deck chuẩn v4)

# Loại slide KHÔNG bắt buộc data_meta
NO_DATA_META = {"cover", "agenda", "qna", "thanks", "support", "manual"}

CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]

MOVER_PRESETS = {
    "jl": {
        "headers": ["URL", "Intent", "PV", "Δ PV", "%", "Clicks", "Δ Clicks", "Pos", "Δ Pos*"],
        "fields": ["url", "intent", "pv", "d_pv", "pct", "clicks", "d_clicks", "pos", "d_pos"],
    },
    "blog": {
        "headers": ["Bài viết (slug rút gọn)", "Nhóm chủ đề", "PV", "Δ PV", "%", "Pos"],
        "fields": ["slug", "chu_de", "pv", "d_pv", "pct", "pos"],
    },
}


def die(msg):
    sys.stderr.write("FAIL: %s\n" % msg)
    sys.exit(1)


def fmt_int(n):
    try:
        return "{:,}".format(int(round(float(n))))
    except (TypeError, ValueError):
        return "—"


def fmt_signed(n, minus=MINUS):
    try:
        v = float(n)
    except (TypeError, ValueError):
        return "—"
    s = "{:,}".format(int(round(abs(v))))
    if v > 0:
        return "+" + s
    if v < 0:
        return minus + s
    return "0"


def fmt_signed_f1(n, minus=MINUS):
    try:
        v = float(n)
    except (TypeError, ValueError):
        return "—"
    if abs(v) < 0.05:
        return "0.0"
    return ("+" if v > 0 else minus) + ("%.1f" % abs(v))


def fmt_pct_signed(n, minus=MINUS, decimals=1):
    try:
        v = float(n)
    except (TypeError, ValueError):
        return "—"
    s = ("{:,.%df}" % decimals).format(abs(v))
    if v > 0:
        return "+" + s + "%"
    if v < 0:
        return minus + s + "%"
    return "0" + ("." + "0" * decimals if decimals else "") + "%"


def num_of(s):
    """Parse số từ chuỗi có dấu phẩy/%/dấu −."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).strip().replace(",", "").replace("%", "").replace(MINUS, "-").replace("–", "-")
    if t in ("", "-", "—"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def delta_cls(val):
    v = num_of(val)
    if v is None or v == 0:
        return "mut"
    return "pos" if v > 0 else "neg"


def pct_cls(val, threshold=100.0):
    v = num_of(val)
    if v is None:
        return "mut"
    return "pos" if v >= threshold else "neg"


def markup(text):
    """Mini-markup: **đậm** → <b>, {pos}/{neg}/{flat} → span màu, {i} → <i>."""
    if text is None:
        return ""
    t = str(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = (t.replace("{pos}", '<span class="up">').replace("{/pos}", "</span>")
          .replace("{neg}", '<span class="down">').replace("{/neg}", "</span>")
          .replace("{flat}", '<span class="flat">').replace("{/flat}", "</span>")
          .replace("{mut}", '<span class="flat">').replace("{/mut}", "</span>")
          .replace("{i}", "<i>").replace("{/i}", "</i>"))
    return t


def style_attr(s):
    return ' style="%s"' % s if s else ""


def shorten_url(u, limit=52):
    if len(u) <= limit:
        return u
    return u[:40] + "…" + u[-10:]


def blog_slug(u, limit=50):
    s = re.sub(r"^https?://[^/]+", "", str(u))
    s = re.sub(r"^/vi/talentcommunity/", "", s)
    s = re.sub(r"\.[0-9A-Za-z]{8}\.html$", "", s)
    s = re.sub(r"\.html$", "", s)
    if len(s) > limit:
        return s[:limit] + "…"
    return s


# ---------------------------------------------------------------- data store
class DataStore(object):
    def __init__(self, datadir):
        self.datadir = datadir
        self._cache = {}

    def _load(self, fname, required_by):
        if fname in self._cache:
            return self._cache[fname]
        path = os.path.join(self.datadir, fname)
        if not os.path.exists(path):
            die("data-ref «%s» cần file %s nhưng không thấy trong --datadir" % (required_by, fname))
        with io.open(path, encoding="utf-8") as f:
            self._cache[fname] = json.load(f)
        return self._cache[fname]

    def digest(self):
        return self._load("digest.json", "digest:*")

    def resolve(self, ref):
        """digest:<section> | movers:<key>:<losers|gainers>[:slice] | apply_groups | blog_groups | digest:sow:<week key>"""
        if not isinstance(ref, str):
            return ref
        parts = ref.split(":")
        if parts[0] == "digest":
            d = self.digest()
            if len(parts) >= 3 and parts[1] == "sow":
                key = ":".join(parts[2:])
                weeks = d["sections"]["sow_status"]["weeks"]
                if key not in weeks:
                    die("digest:sow — không có tuần «%s». Có: %s" % (key, list(weeks.keys())))
                return weeks[key]
            sec = d["sections"].get(parts[1])
            if sec is None:
                die("digest:%s — section không tồn tại trong digest.json" % parts[1])
            return sec
        if parts[0] == "movers":
            if len(parts) < 3:
                die("data-ref movers cần dạng movers:<key>:<losers|gainers>[:slice] — nhận «%s»" % ref)
            data = self._load("movers_pv_%s.json" % parts[1], ref)
            side = parts[2]
            if side not in ("losers", "gainers"):
                die("movers side phải là losers/gainers — nhận «%s»" % side)
            rows = data[side]
            if len(parts) >= 4 and parts[3] not in ("*", ""):
                m = re.match(r"^(\d+)(?:-(\d+))?$", parts[3])
                if not m:
                    die("slice movers không hợp lệ: «%s» (dùng 1-10 | 5 | *)" % parts[3])
                a = int(m.group(1))
                b = int(m.group(2) or m.group(1))
                rows = rows[a - 1: b]
            return {"rows": rows, "meta": data}
        if parts[0] == "apply_groups":
            return self._load("apply_groups.json", ref)
        if parts[0] == "blog_groups":
            return self._load("blog_groups.json", ref)
        die("data-ref không hiểu: «%s»" % ref)


# ---------------------------------------------------------------- khối chung
def brandbar(meta):
    return ('  <div class="brandbar">\n'
            '    <img class="logo-client" alt="%s">\n'
            '    <img class="logo-gtv" alt="GTV SEO">\n'
            "  </div>\n" % meta.get("client", "Client"))


def bullets_html(items, ul_style=""):
    out = ["      <ul%s>" % style_attr(ul_style)]
    for it in items or []:
        if isinstance(it, dict):
            out.append("        <li%s>%s</li>" % (style_attr(it.get("style", "")), markup(it.get("text", ""))))
        else:
            out.append("        <li>%s</li>" % markup(it))
    out.append("      </ul>")
    return "\n".join(out)


def has_prefix(text):
    t = str(text).lstrip()
    return bool(re.match(r"^([①-⑳]|\(\d+\)|\d+[\.\)])", t))


def action_list(items, auto_circle=True):
    out = ['        <ul style="list-style:none;margin:8px 0 0;padding-left:6px;">']
    n = len(items or [])
    for i, it in enumerate(items or []):
        text = it.get("text") if isinstance(it, dict) else it
        pre = ""
        if auto_circle and not has_prefix(text):
            pre = (CIRCLED[i] if i < len(CIRCLED) else "(%d)" % (i + 1)) + " "
        mb = ' style="margin-bottom:8px;"' if i < n - 1 else ""
        out.append("          <li%s>%s%s</li>" % (mb, pre, markup(text)))
    out.append("        </ul>")
    return "\n".join(out)


def action_box(action):
    """action: {label, intro?, items, style?} — luôn render ul mỗi ý 1 li (luật #13)."""
    if not action:
        return ""
    label = action.get("label", "Việc cần làm:")
    intro = (" " + markup(action["intro"])) if action.get("intro") else ""
    parts = ['      <div class="action"%s><b>%s</b>%s' % (style_attr(action.get("style", "")), markup(label), intro)]
    parts.append(action_list(action.get("items") or []))
    # khối kép «Đọc pattern / Việc cần làm» trong CÙNG box
    if action.get("label2"):
        parts.append("        <b>%s</b>%s" % (markup(action["label2"]),
                                              (" " + markup(action["intro2"])) if action.get("intro2") else ""))
        parts.append(action_list(action.get("items2") or []))
    parts.append("      </div>")
    return "\n".join(parts)


def pattern_action_box(slide):
    """movers: pattern {label,intro,items} + action {label,items} chung 1 box (luật #13)."""
    pat = slide.get("pattern")
    act = slide.get("action")
    if not pat and not act:
        return ""
    style = (pat or act or {}).get("box_style", "font-size:22px;padding:10px 20px;")
    parts = ['      <div class="action"%s>' % style_attr(style)]
    if pat:
        intro = (" " + markup(pat["intro"])) if pat.get("intro") else ""
        parts.append("        <b>%s</b>%s" % (markup(pat.get("label", "Đọc pattern:")), intro))
        parts.append('        <ul style="list-style:none;margin:4px 0 8px;padding-left:6px;">')
        items = pat.get("items") or []
        for i, it in enumerate(items):
            mb = ' style="margin-bottom:8px;"' if i < len(items) - 1 else ""
            parts.append("          <li%s>%s</li>" % (mb, markup(it)))
        parts.append("        </ul>")
    if act:
        parts.append("        <b>%s</b>" % markup(act.get("label", "Việc cần làm:")))
        parts.append('        <ul style="list-style:none;margin:6px 0 0;padding-left:6px;">')
        items = act.get("items") or []
        for i, it in enumerate(items):
            text = it
            pre = "" if has_prefix(text) else (CIRCLED[i] if i < len(CIRCLED) else "(%d)" % (i + 1)) + " "
            mb = ' style="margin-bottom:8px;"' if i < len(items) - 1 else ""
            parts.append("          <li%s>%s%s</li>" % (mb, pre, markup(text)))
        parts.append("        </ul>")
    parts.append("      </div>")
    return "\n".join(parts)


def nx_block(col, default_ul_style=""):
    """col: {title?, title_style?, bullets, ul_style?}"""
    out = []
    if col.get("title"):
        out.append('          <h3%s>%s</h3>' % (style_attr(col.get("title_style", "")), markup(col["title"])))
    out.append(bullets_html(col.get("bullets"), col.get("ul_style", default_ul_style)))
    return "\n".join(out)


def scope_note(slide):
    sn = slide.get("scope_note")
    if not sn:
        return ""
    return '      <div class="scope-note"%s>%s</div>\n' % (
        style_attr(slide.get("scope_note_style", "font-size:18px;")), markup(sn))


# ---------------------------------------------------------------- bảng literal
def cell_html(value, kind):
    cls = None
    if isinstance(value, dict):
        cls = value.get("c")
        value = value.get("v", "")
    v = "" if value is None else str(value)
    # override class bằng hậu tố "…|cls"
    m = re.match(r"^(.*)\|(pos|neg|mut|num|ctr|name)$", v)
    if m:
        v, cls = m.group(1), m.group(2)
    if cls is None:
        if kind == "name":
            cls = "name"
        elif kind == "ctr":
            cls = "ctr"
        elif kind == "num":
            cls = "num"
        elif kind == "delta":
            cls = delta_cls(v)
        elif kind == "pct100":
            cls = pct_cls(v)
        else:
            cls = ""
    extra = ""
    attr = (' class="%s"' % cls) if cls else ""
    return "<td%s%s>%s</td>" % (attr, extra, markup(v) if kind == "name" else v)


def table_html(tbl, resolver=None):
    """tbl: {class?, style?, wrap_style?, headers, col_kinds, rows | data(+options)}"""
    tclass = tbl.get("class", "data")
    rows_spec = tbl.get("rows")
    if rows_spec is None and tbl.get("data"):
        die("table cần rows literal hoặc renderer data riêng — «data» chỉ hợp lệ ở type chuyên dụng")
    headers = tbl.get("headers") or []
    kinds = tbl.get("col_kinds") or []
    out = ['      <div class="tbl-wrap"%s>' % style_attr(tbl.get("wrap_style", ""))]
    out.append('        <table class="%s"%s>' % (tclass, style_attr(tbl.get("style", ""))))
    if headers:
        ths = []
        for h in headers:
            if isinstance(h, dict):
                ths.append("<th%s>%s</th>" % (style_attr(h.get("style", "")), markup(h.get("label", ""))))
            else:
                ths.append("<th>%s</th>" % markup(h))
        out.append("          <thead><tr>%s</tr></thead>" % "".join(ths))
    out.append("          <tbody>")
    for row in rows_spec or []:
        rcls = ""
        cells = row
        if isinstance(row, dict):
            rcls = row.get("class", "")
            if row.get("divider"):
                ncols = len(headers) or len(kinds) or 1
                out.append('            <tr class="%s"><td colspan="%d">%s</td></tr>'
                           % (row.get("class", "divider"), ncols, markup(row.get("divider"))))
                continue
            cells = row.get("cells", [])
        tds = []
        for j, val in enumerate(cells):
            kind = kinds[j] if j < len(kinds) else ""
            tds.append(cell_html(val, kind))
        attr = (' class="%s"' % rcls) if rcls else ""
        out.append("            <tr%s>%s</tr>" % (attr, "".join(tds)))
    out.append("          </tbody>")
    out.append("        </table>")
    out.append("      </div>")
    return "\n".join(out)


# ---------------------------------------------------------------- renderer per type
def render_cover(slide, meta, ctx):
    return (
        '<section class="slide cover%s">\n' % (" active" if ctx["index"] == 0 else "")
        + brandbar(meta)
        + '  <div class="cover-box">\n'
        + '    <h1 class="cover-title">%s</h1>\n' % markup(slide.get("title", ""))
        + '    <p class="cover-outline">%s</p>\n' % markup(slide.get("outline", "SEO Report (Weekly)"))
        + '    <div class="cover-week">%s</div>\n' % markup(slide.get("week_line", ""))
        + '    <div class="cover-domain">%s</div>\n' % markup(slide.get("domain", ""))
        + "  </div>\n"
        + '  <div class="cover-foot"><span></span><span>%s</span></div>\n' % markup(slide.get("footer", "PRESENTED BY GTV SEO"))
        + "%PAGENO%\n</section>"
    )


def render_agenda(slide, meta, ctx):
    items = "\n".join('    <div class="agenda-item">%s</div>' % markup(x) for x in slide.get("items") or [])
    return (
        '<section class="slide">\n'
        + '  <div class="agenda-left"><div class="agenda-word">%s</div></div>\n' % markup(slide.get("word", "AGENDA"))
        + '  <div class="agenda-right">\n' + items + "\n  </div>\n"
        + "%PAGENO%\n" + brandbar(meta) + "</section>"
    )


def render_runrate(slide, meta, ctx):
    data = ctx["store"].resolve(slide.get("data", "digest:runrate_tuan"))
    summary = data.get("summary") or []
    weeks = data.get("weeks") or []
    month = slide.get("month_label") or ""
    dmeta = ctx["store"].digest().get("meta", {})
    week_label = slide.get("hl_week") or ctx["meta"].get("week_label") or dmeta.get("week_label", "")
    if not month:
        for w in weeks:
            if w and w[0] == week_label and len(w) > 2:
                month = str(w[2]).split("/")[0]
                break
    cards = []
    for row in summary:
        if len(row) < 9 or not row[0]:
            continue
        r = list(row)
        good1 = "rr-pct-good" if (num_of(r[3]) or 0) >= (num_of(r[4]) or 0) else "rr-pct-bad"
        good2 = "rr-pct-good" if (num_of(r[7]) or 0) >= (num_of(r[8]) or 0) else "rr-pct-bad"
        cards.append(
            '        <div class="rr-card">\n'
            "          <h4>%s</h4>\n" % r[0]
            + '          <div class="rr-vals">\n'
            + '            <span><span class="rr-num">%s</span><span class="rr-lbl">Lũy kế năm / KH %s</span></span>\n' % (r[2], r[1])
            + '            <span><span class="%s">%s</span><span class="rr-lbl">Run-rate LK (time %s)</span></span>\n' % (good1, r[3], r[4])
            + '            <span><span class="rr-num">%s</span><span class="rr-lbl">Lũy kế %s / KPI %s</span></span>\n' % (r[6], month, r[5])
            + '            <span><span class="%s">%s</span><span class="rr-lbl">Run-rate %s (time %s)</span></span>\n' % (good2, r[7], month, r[8])
            + "          </div>\n        </div>"
        )
    headers = ["Tuần", "Kỳ (ngày)", "Tháng", "PV Prior Year", "PV KPI tuần", "PV Thực tế", "%HT",
               "Run-rate LK", "Apply Prior Year", "Apply KPI tuần", "Apply Thực tế", "%HT", "Run-rate LK", "CR"]
    limit = int(slide.get("weeks_limit", 8))
    body_rows = [w for w in weeks if len(w) >= 14 and str(w[5]).strip()]
    body_rows = body_rows[-limit:]
    trs = []
    for w in body_rows:
        hl = (w[0] == week_label)
        def td(i, kind):
            v = w[i] if i < len(w) else ""
            if hl and i in (0, 5, 10):
                v = "<b>%s</b>" % v
            if kind == "pct":
                return '<td class="%s">%s</td>' % (pct_cls(w[i]), v)
            if kind == "num":
                return '<td class="num">%s</td>' % v
            return '<td class="ctr">%s</td>' % v
        cells = [td(0, "ctr"), td(1, "ctr"), td(2, "ctr"), td(3, "num"), td(4, "num"), td(5, "num"),
                 td(6, "pct"), td(7, "pct"), td(8, "num"), td(9, "num"), td(10, "num"),
                 td(11, "pct"), td(12, "pct"), td(13, "ctr")]
        trs.append("            <tr%s>%s</tr>" % (' class="hl"' if hl else "", "".join(cells)))
    body = (
        '    <div class="content">\n'
        + '      <div class="rr-cards">\n' + "\n".join(cards) + "\n      </div>\n"
        + '      <div class="tbl-wrap">\n'
        + '        <table class="data compact">\n'
        + "          <thead>\n            <tr>%s</tr>\n          </thead>\n" % "".join("<th>%s</th>" % h for h in headers)
        + "          <tbody>\n" + "\n".join(trs) + "\n          </tbody>\n"
        + "        </table>\n      </div>\n"
    )
    if slide.get("bullets"):
        body += '      <div class="nx">\n' + bullets_html(slide["bullets"], slide.get("bullets_style", "")) + "\n      </div>\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def resolve_special_rows(slide, ctx):
    """Bảng data-ref cho table_side/table_full: apply_groups | digest:sow:… (khác thì rows literal)."""
    ref = slide.get("data")
    if not ref:
        return None
    if isinstance(ref, str) and ref.startswith("apply_groups"):
        data = ctx["store"].resolve("apply_groups")
        name_map = slide.get("name_map") or {}
        kpi = set(slide.get("kpi_rows") or [])
        rows = []
        for g in data.get("groups", []):
            name = name_map.get(g["group"], g["group"])
            rows.append({
                "class": "kpi-row" if g["group"] in kpi else "",
                "cells": [name, fmt_int(g["apply"]), fmt_int(g["apply_prev"]),
                          {"v": fmt_signed(g["d"], minus="-"), "c": delta_cls(g["d"])},
                          {"v": fmt_pct_signed(g["pct"], minus="-", decimals=2), "c": delta_cls(g["pct"])}],
            })
        gt = data.get("grand_total")
        if gt:
            rows.append({"class": "total",
                         "cells": [slide.get("total_label", "Grand Total"), fmt_int(gt["apply"]), fmt_int(gt["apply_prev"]),
                                   {"v": fmt_signed(gt["d"], minus="-"), "c": delta_cls(gt["d"])},
                                   {"v": fmt_pct_signed(gt["pct"], minus="-", decimals=2), "c": delta_cls(gt["pct"])}]})
        return {"headers": slide.get("table", {}).get("headers") or
                           ["Page Group", "Apply tuần này", "Apply tuần trước", "Δ", "%"],
                "col_kinds": ["name", "num", "num", "delta", "delta"],
                "rows": rows,
                "class": slide.get("table", {}).get("class", "data"),
                "style": slide.get("table", {}).get("style", ""),
                "wrap_style": slide.get("table", {}).get("wrap_style", "")}
    die("data-ref «%s» chưa được hỗ trợ cho type %s" % (ref, slide.get("type")))


def render_table_side(slide, meta, ctx):
    tbl = resolve_special_rows(slide, ctx) or slide.get("table") or die("table_side thiếu «table» hoặc «data»")
    left = ['        <div class="col-l">', table_html(tbl), ]
    if slide.get("left_note"):
        left.append('          <div class="action" style="margin-top:14px;">%s</div>' % markup(slide["left_note"]))
    left.append("        </div>")
    right = slide.get("right") or {}
    rparts = ['        <div class="col-r">', '          <div class="nx">', nx_block(right, right.get("ul_style", "")), "          </div>"]
    if right.get("action"):
        rparts.append(action_box(right["action"]).replace('      <div class="action"', '          <div class="action"'))
    rparts.append("        </div>")
    body = ('    <div class="content"%s>\n' % style_attr(slide.get("content_style", ""))
            + '      <div class="split">\n' + "\n".join(left) + "\n" + "\n".join(rparts) + "\n      </div>\n")
    if slide.get("action"):
        body += action_box(slide["action"]) + "\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def render_table_full(slide, meta, ctx):
    tbl = resolve_special_rows(slide, ctx) or slide.get("table") or die("table_full thiếu «table» hoặc «data»")
    body = '    <div class="content"%s>\n' % style_attr(slide.get("content_style", ""))
    body += scope_note(slide)
    body += table_html(tbl) + "\n"
    below = slide.get("below") or {}
    if below.get("split"):
        sp = below["split"]
        body += ('      <div class="split"%s>\n' % style_attr(below.get("split_style", ""))
                 + '        <div class="col-l nx">\n' + nx_block(sp.get("left", {})) + "\n        </div>\n"
                 + '        <div class="col-r nx">\n' + nx_block(sp.get("right", {})) + "\n        </div>\n"
                 + "      </div>\n")
    elif below.get("bullets"):
        body += '      <div class="nx">\n' + bullets_html(below["bullets"], below.get("ul_style", "")) + "\n      </div>\n"
    if slide.get("action"):
        body += action_box(slide["action"]) + "\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def mover_cell(row, field, url_marks, name_font="19px", intent_font="18px"):
    if field == "url":
        u = str(row.get("url", ""))
        disp = shorten_url(u)
        mark = (url_marks or {}).get(u, "")
        return '<td class="name" style="font-size:%s;">%s%s</td>' % (name_font, disp, mark)
    if field == "slug":
        u = str(row.get("url", ""))
        mark = (url_marks or {}).get(u, "")
        return '<td class="name" style="font-size:%s;">%s%s</td>' % (name_font, blog_slug(u), mark)
    if field in ("intent", "chu_de"):
        val = row.get("intent") if field == "intent" else row.get("chu_de")
        return '<td class="ctr" style="font-size:%s;">%s</td>' % (intent_font, val or "—")
    if field == "pv":
        return '<td class="num">%s</td>' % fmt_int(row.get("pv"))
    if field == "d_pv":
        return '<td class="%s">%s</td>' % (delta_cls(row.get("d_pv")), fmt_signed(row.get("d_pv")))
    if field == "pct":
        return '<td class="%s">%s</td>' % (delta_cls(row.get("pct")), fmt_pct_signed(row.get("pct")))
    if field == "clicks":
        if row.get("clicks") is None:
            return '<td class="num">—</td>'
        return '<td class="num">%s</td>' % fmt_int(row.get("clicks"))
    if field == "d_clicks":
        if row.get("clicks") is None or row.get("clicks_prev") is None:
            return '<td class="ctr">—</td>'
        d = float(row["clicks"]) - float(row["clicks_prev"])
        return '<td class="%s">%s</td>' % (delta_cls(d), fmt_signed(d))
    if field == "pos":
        p = row.get("pos")
        if not p:
            return '<td class="num">—</td>'
        return '<td class="num">%.1f</td>' % float(p)
    if field == "d_pos":
        p, pp = row.get("pos"), row.get("pos_prev")
        if not p or not pp:
            return '<td class="ctr">—</td>'
        d = round(float(pp) - float(p), 1)  # dương = lên hạng (quy ước sheet)
        return '<td class="%s">%s</td>' % (delta_cls(d), fmt_signed_f1(d))
    return "<td>%s</td>" % (row.get(field) or "")


def render_movers(slide, meta, ctx):
    ref = slide.get("data") or die("movers thiếu «data» (vd movers:jl:losers:1-10)")
    res = ctx["store"].resolve(ref)
    rows = res["rows"]
    preset_key = slide.get("columns", "jl")
    preset = MOVER_PRESETS.get(preset_key) or die("movers columns preset không hợp lệ: %s" % preset_key)
    fields = slide.get("fields") or preset["fields"]
    headers = slide.get("headers") or preset["headers"][: len(fields)]
    url_marks = slide.get("url_marks") or {}
    ths = []
    for i, h in enumerate(headers):
        st = ' style="text-align:left;"' if fields[i] in ("url", "slug") else ""
        ths.append("<th%s>%s</th>" % (st, h))
    trs = []
    for row in rows:
        tds = [mover_cell(row, f, url_marks) for f in fields]
        trs.append("<tr>%s</tr>" % "".join(tds))
    body = '    <div class="content"%s>\n' % style_attr(slide.get("content_style", "gap:8px;justify-content:flex-start;padding-top:0;"))
    body += scope_note(slide)
    body += ('      <div class="tbl-wrap">\n'
             + '        <table class="%s"%s>\n' % (slide.get("table_class", "data compact dense"),
                                                   style_attr(slide.get("table_style", "font-size:21px;")))
             + "          <thead><tr>%s</tr></thead>\n" % "".join(ths)
             + "          <tbody>\n" + "\n".join(trs) + "\n          </tbody>\n"
             + "        </table>\n      </div>\n")
    if slide.get("split"):
        sp = slide["split"]
        body += ('      <div class="split"%s>\n' % style_attr(slide.get("split_style", ""))
                 + '        <div class="col-l nx">\n' + nx_block(sp.get("left", {})) + "\n        </div>\n"
                 + '        <div class="col-r nx">\n' + nx_block(sp.get("right", {})) + "\n        </div>\n"
                 + "      </div>\n")
    box = pattern_action_box(slide)
    if box:
        body += box + "\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def render_blog_groups(slide, meta, ctx):
    data = ctx["store"].resolve("blog_groups")
    include = slide.get("include") or []
    rows_by_key = {}
    for r in data.get("rows", []):
        rows_by_key["%s|%s" % (r.get("seo_flag", ""), r.get("group", ""))] = r
    sel = []
    for key in include:
        if isinstance(key, dict):
            key = "%s|%s" % (key.get("flag", ""), key.get("group", ""))
        if key not in rows_by_key:
            die("blog_groups include không khớp: «%s». Key có: %s" % (key, sorted(rows_by_key.keys())))
        sel.append((rows_by_key[key], ""))
    gt = data.get("grand_total")
    if gt:
        sel.append((gt, "total"))
    headers = slide.get("headers") or ["Nhóm chủ đề", "URL", "PV tuần này", "PV tuần trước",
                                       "Δ PV", "Clicks", "Δ Clicks", "Pos", "Δ Pos*", "Δ Imp"]
    trs = []
    for r, rcls in sel:
        name = slide.get("total_label", "Grand Total") if rcls == "total" else \
            (slide.get("name_map", {}) or {}).get(r.get("group"), r.get("group"))
        d_pv, d_clicks, d_imp = r.get("d_pv", ""), r.get("d_clicks", ""), r.get("d_imp", "")
        d_pos = r.get("d_pos")
        pos = r.get("pos")
        tds = [
            '<td class="name">%s</td>' % markup(name),
            '<td class="num">%s</td>' % "{:,}".format(int(str(r.get("url_count", "")).replace(",", ""))),
            '<td class="num">%s</td>' % r.get("pv", ""),
            '<td class="num">%s</td>' % r.get("pv_prev", ""),
            '<td class="%s">%s</td>' % (delta_cls(d_pv), d_pv),
            '<td class="num">%s</td>' % r.get("clicks", ""),
            '<td class="%s">%s</td>' % (delta_cls(d_clicks), fmt_signed(d_clicks, minus="-") if num_of(d_clicks) is not None else d_clicks),
            '<td class="num">%s</td>' % ("%.1f" % float(pos) if pos not in (None, "") else "—"),
            '<td class="%s">%s</td>' % (delta_cls(d_pos), ("%.1f" % float(d_pos) if float(d_pos) < 0 else ("+%.1f" % float(d_pos) if float(d_pos) > 0 else "0.0")) if d_pos not in (None, "") else "—"),
            '<td class="%s">%s</td>' % (delta_cls(d_imp), (("+" + str(d_imp)) if (num_of(d_imp) or 0) > 0 else str(d_imp))),
        ]
        trs.append("            <tr%s>%s</tr>" % ((' class="%s"' % rcls) if rcls else "", "".join(tds)))
    body = '    <div class="content"%s>\n' % style_attr(slide.get("content_style", ""))
    body += scope_note(slide)
    body += ('      <div class="tbl-wrap">\n'
             + '        <table class="%s"%s>\n' % (slide.get("table_class", "data compact"),
                                                   style_attr(slide.get("table_style", "font-size:21px;")))
             + "          <thead><tr>%s</tr></thead>\n" % "".join("<th>%s</th>" % h for h in headers)
             + "          <tbody>\n" + "\n".join(trs) + "\n          </tbody>\n"
             + "        </table>\n      </div>\n")
    if slide.get("bullets"):
        body += '      <div class="nx">\n' + bullets_html(slide["bullets"], slide.get("bullets_style", "")) + "\n      </div>\n"
    if slide.get("action"):
        body += action_box(slide["action"]) + "\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


SOW_STATUS_MAP = [
    ("Done", "done", "Done"),
    ("Đang làm", "doing", "Đang làm"),
    ("Trễ hạn", "late", "Trễ hạn"),
    ("Tạm ngưng", "paused", "Tạm ngưng"),
]


def render_sow(slide, meta, ctx):
    rows = slide.get("rows")
    if rows is None and slide.get("data"):
        data = ctx["store"].resolve(slide["data"])
        rows = [{"task": t.get("task", ""), "status": t.get("status", "")} for t in data.get("tasks", [])]
    if rows is None:
        die("sow thiếu «rows» hoặc «data»")
    # Chuẩn Vincent 23/07/2026: bảng công việc 5 cột — Hạng mục (nhóm, rowspan) | Task cụ thể | PIC | Deadline | Tiến độ.
    # Row có hangmuc/pic/deadline → render 5 cột; row chỉ task/status → fallback 2 cột (deck cũ).
    ext = any(isinstance(r, dict) and (r.get("hangmuc") or r.get("pic") or r.get("deadline")) for r in rows)
    norm = []
    for r in rows:
        if isinstance(r, dict):
            norm.append({"hangmuc": (r.get("hangmuc") or "").strip(), "task": r.get("task", ""),
                         "pic": (r.get("pic") or "").strip(), "deadline": (str(r.get("deadline") or "")).strip(),
                         "status": (r.get("status") or "").strip()})
        else:
            norm.append({"hangmuc": "", "task": r[0], "pic": "", "deadline": "",
                         "status": (r[1] if len(r) > 1 else "").strip()})
    counts = {}
    for r in norm:
        st = r["status"] or "—"
        counts[st] = counts.get(st, 0) + 1
    chips = slide.get("chips")
    if chips is None:
        chips = []
        for label, cls, disp in SOW_STATUS_MAP:
            if counts.get(label):
                chips.append({"n": counts[label], "cls": cls, "label": disp})
        blank = counts.get("—", 0)
        if blank:
            chips.append({"n": blank, "cls": "notyet", "label": "Chưa cập nhật status"})
    chip_html = "\n".join('        <div class="chip %s"><span class="n">%s</span><span class="t">%s</span></div>'
                          % (c.get("cls", ""), c.get("n", ""), c.get("label", "")) for c in chips)
    if ext:
        tr_list = []
        i = 0
        while i < len(norm):
            span = 1
            while i + span < len(norm) and norm[i + span]["hangmuc"] == norm[i]["hangmuc"]:
                span += 1
            for j in range(i, i + span):
                r = norm[j]
                cells = []
                if j == i:
                    cells.append('<td class="name" rowspan="%d" style="font-weight:700;vertical-align:middle;">%s</td>'
                                 % (span, markup(r["hangmuc"] or "—")))
                cells.append('<td class="name">%s</td>' % markup(r["task"]))
                cells.append('<td class="ctr">%s</td>' % markup(r["pic"] or "—"))
                cells.append('<td class="ctr">%s</td>' % (r["deadline"] or "—"))
                cells.append('<td class="ctr">%s</td>' % (r["status"] or "—"))
                tr_list.append("            <tr>" + "".join(cells) + "</tr>")
            i += span
        trs = "\n".join(tr_list)
        thead = '          <thead><tr><th style="width:13%">Hạng mục</th><th style="width:40%">Task cụ thể</th><th style="width:15%">PIC</th><th style="width:13%">Deadline</th><th>Tiến độ</th></tr></thead>\n'
    else:
        trs = "\n".join('            <tr><td class="name">%s</td><td class="ctr">%s</td></tr>'
                        % (markup(r["task"]), r["status"] or "—") for r in norm)
        thead = '          <thead><tr><th style="width:72%">Task</th><th>Status</th></tr></thead>\n'
    body = ('    <div class="content">\n'
            + '      <div class="chips">\n' + chip_html + "\n      </div>\n"
            + '      <div class="tbl-wrap">\n'
            + '        <table class="data compact">\n'
            + thead
            + "          <tbody>\n" + trs + "\n          </tbody>\n"
            + "        </table>\n      </div>\n    </div>\n")
    return content_slide(slide, meta, ctx, body)


def render_next_week(slide, meta, ctx):
    if slide.get("rows"):
        return render_sow(slide, meta, ctx)
    body = ('    <div class="content">\n'
            + '      <div class="manual-slot">%s</div>\n' % markup(slide.get("text", ""))
            + "    </div>\n")
    return content_slide(slide, meta, ctx, body)


def render_support(slide, meta, ctx):
    trs = []
    for r in slide.get("rows") or []:
        label = r.get("scope") if isinstance(r, dict) else r
        desc = (r.get("description") if isinstance(r, dict) else "") or "&nbsp;"
        trs.append('            <tr><td class="name">%s</td><td class="desc">%s</td></tr>' % (markup(label), desc))
    body = ('    <div class="content">\n'
            + '      <div class="tbl-wrap">\n'
            + '        <table class="data support-tbl">\n'
            + '          <thead><tr><th style="width:30%">SCOPE</th><th style="width:70%">Description</th></tr></thead>\n'
            + "          <tbody>\n" + "\n".join(trs) + "\n          </tbody>\n"
            + "        </table>\n      </div>\n")
    if slide.get("note"):
        body += '      <div class="support-note">%s</div>\n' % markup(slide["note"])
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def render_nhanxet_2col(slide, meta, ctx):
    body = '    <div class="content"%s>\n' % style_attr(slide.get("content_style", ""))
    if slide.get("single"):
        col = slide.get("left") or slide.get("column") or {}
        body += '      <div class="nx">\n' + nx_block(col) + "\n      </div>\n"
    else:
        left, right = slide.get("left") or {}, slide.get("right") or {}
        body += ('      <div class="split">\n'
                 + '        <div class="col-l nx" style="flex:1;">\n' + nx_block(left) + "\n        </div>\n"
                 + '        <div class="col-r nx" style="flex:1;">\n' + nx_block(right) + "\n        </div>\n"
                 + "      </div>\n")
    if slide.get("action"):
        body += action_box(slide["action"]) + "\n"
    body += "    </div>\n"
    return content_slide(slide, meta, ctx, body)


def render_qna(slide, meta, ctx):
    return ('<section class="slide qna">\n'
            + '  <div class="qna-big">%s</div>\n' % markup(slide.get("big", "Q&amp;A"))
            + '  <div class="qna-title">%s</div>\n' % markup(slide.get("title", "HỎI ĐÁP &amp; THẢO LUẬN"))
            + brandbar(meta) + "%PAGENO%\n</section>")


def render_thanks(slide, meta, ctx):
    return ('<section class="slide thanks">\n'
            + '  <div class="thanks-logos">\n'
            + '    <img class="logo-client" alt="%s">\n' % meta.get("client", "Client")
            + '    <span class="thanks-x">×</span>\n'
            + '    <img class="logo-gtv" alt="GTV SEO">\n'
            + "  </div>\n"
            + '  <div class="thanks-word">%s</div>\n' % markup(slide.get("word", "Thank You"))
            + '  <div class="thanks-foot">%s</div>\n' % markup(slide.get("foot", "PRESENTED BY GTV SEO"))
            + "%PAGENO%\n</section>")


def render_manual(slide, meta, ctx):
    html = slide.get("html") or die("slide manual thiếu «html»")
    if "%PAGENO%" not in html:
        html = html.replace("</section>", "%PAGENO%\n</section>")
    return html


def content_slide(slide, meta, ctx, body):
    """Khung chuẩn slide nội dung: crumb + pill + sub + body + brandbar + data-meta + page-no."""
    parts = ['<section class="slide">', '  <div class="s-pad">']
    if slide.get("crumb"):
        parts.append('    <div class="crumb">%s</div>' % markup(slide["crumb"]))
    if slide.get("pill"):
        parts.append('    <div class="pill-wrap"><div class="pill">%s</div><div class="pill-underline"></div></div>' % markup(slide["pill"]))
    if slide.get("sub"):
        idx = ('<span class="idx">%s</span> ' % slide["idx"]) if slide.get("idx") else ""
        parts.append('    <div class="slide-sub">%s%s</div>' % (idx, markup(slide["sub"])))
    parts.append(body.rstrip("\n"))
    parts.append("  </div>")
    parts.append(brandbar(meta).rstrip("\n"))
    if slide.get("data_meta"):
        parts.append('  <div class="data-meta">%s</div>' % markup(slide["data_meta"]))
    parts.append("%PAGENO%")
    parts.append("</section>")
    return "\n".join(parts)


RENDERERS = {
    "cover": render_cover,
    "agenda": render_agenda,
    "runrate": render_runrate,
    "table_side": render_table_side,
    "table_full": render_table_full,
    "nhanxet_2col": render_nhanxet_2col,
    "diagnose": render_nhanxet_2col,
    "movers": render_movers,
    "blog_groups": render_blog_groups,
    "sow": render_sow,
    "next_week": render_next_week,
    "support": render_support,
    "qna": render_qna,
    "thanks": render_thanks,
    "manual": render_manual,
}


def main():
    ap = argparse.ArgumentParser(description="Ráp deck báo cáo tuần từ content.yaml + skeleton + data")
    ap.add_argument("--content", required=True)
    ap.add_argument("--skeleton", required=True)
    ap.add_argument("--datadir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo-client", help="PNG logo client (khi skeleton còn placeholder)")
    ap.add_argument("--logo-gtv", help="PNG logo GTV (khi skeleton còn placeholder)")
    args = ap.parse_args()

    with io.open(args.content, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    meta = doc.get("meta") or {}
    slides = doc.get("slides") or []
    if not slides:
        die("content.yaml không có slides")

    with io.open(args.skeleton, encoding="utf-8") as f:
        skeleton = f.read()
    if "<!-- SLIDES -->" not in skeleton:
        die("skeleton thiếu marker <!-- SLIDES -->")

    store = DataStore(args.datadir)
    ctx = {"store": store, "meta": meta}

    errors = []
    rendered = []
    for i, slide in enumerate(slides):
        stype = slide.get("type")
        if stype not in RENDERERS:
            errors.append("slide %d: type «%s» không hợp lệ" % (i + 1, stype))
            continue
        if stype not in NO_DATA_META and not slide.get("data_meta"):
            errors.append("slide %d (%s): thiếu data_meta — bắt buộc cho slide data (luật render bảng #4)" % (i + 1, stype))
            continue
        ctx["index"] = i
        rendered.append(RENDERERS[stype](slide, meta, ctx))
    if errors:
        for e in errors:
            sys.stderr.write("FAIL: %s\n" % e)
        sys.exit(1)

    n = len(rendered)
    final_slides = []
    for i, html in enumerate(rendered):
        html = html.replace("%PAGENO%", '  <div class="page-no">%d/%d</div>' % (i + 1, n))
        final_slides.append(html)
    slides_html = "\n\n".join(final_slides)

    out_html = skeleton.replace("<!-- SLIDES -->", slides_html)
    out_html = out_html.replace("{{TITLE}}", meta.get("title", "SEO Report Weekly"))
    out_html = out_html.replace("{{EDIT_KEY}}", meta.get("edit_key", "deck-edit"))

    for ph, arg_path, name in (("{{LOGO_CLIENT_B64}}", args.logo_client, "client"),
                               ("{{LOGO_GTV_B64}}", args.logo_gtv, "gtv")):
        if ph in out_html:
            path = arg_path
            if not path:
                # fallback: weekly-template/assets cạnh skeleton
                guess_dir = os.path.join(os.path.dirname(os.path.abspath(args.skeleton)), "assets")
                for fn in (["logo-client.png", "logo-careerviet.png"] if name == "client" else ["logo-gtv.png"]):
                    p = os.path.join(guess_dir, fn)
                    if os.path.exists(p):
                        path = p
                        break
            if not path or not os.path.exists(path):
                die("skeleton còn placeholder %s — truyền --logo-%s <png> hoặc đặt logo trong assets/ cạnh skeleton" % (ph, name))
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            out_html = out_html.replace(ph, "data:image/png;base64," + b64)

    # -------- validate cuối
    fails = []
    n_sections = out_html.count('<section class="slide')
    if n_sections != len(slides):
        fails.append("số <section class=slide> (%d) != số slide yaml (%d)" % (n_sections, len(slides)))
    if "{{" in out_html:
        pos = out_html.find("{{")
        fails.append("còn placeholder '{{' chưa thay (vị trí %d: …%s…)" % (pos, out_html[pos:pos + 40]))
    if 'class="slide cover active"' not in out_html and 'class="slide active' not in out_html:
        fails.append("slide 1 chưa có class active")
    for i, slide in enumerate(slides):
        if slide.get("type") not in NO_DATA_META and 'class="data-meta"' not in final_slides[i]:
            fails.append("slide %d thiếu .data-meta trong HTML render" % (i + 1))
    if fails:
        for e in fails:
            sys.stderr.write("FAIL validate: %s\n" % e)
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8") as f:
        f.write(out_html)

    types = {}
    for s in slides:
        types[s["type"]] = types.get(s["type"], 0) + 1
    print("BUILD OK: %s" % args.out)
    print("  slides: %d/%d · page-no 1/%d…%d/%d · edit_key=%s" % (n, len(slides), n, n, n, meta.get("edit_key", "deck-edit")))
    print("  types: " + ", ".join("%s×%d" % (k, v) for k, v in sorted(types.items())))
    print("  size: %.1f KB" % (len(out_html.encode('utf-8')) / 1024.0))
    print("  validate: PASS (đủ slide, không còn {{, data-meta đủ, slide 1 active)")


if __name__ == "__main__":
    main()
