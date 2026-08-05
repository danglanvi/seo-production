#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pptx.py — chuyển content YAML của deck (nguồn của build_deck.py) sang PowerPoint GỐC.

Khác với xuất ảnh: mọi thứ trên slide là đối tượng PowerPoint thật —
text box, bảng, biểu đồ native — nên mở trong PowerPoint/Keynote/Google Slides là sửa được.

Dùng:
  python3 skills/gtv-weekly-report/scripts/build_pptx.py \
      --content 09-reporting/quarterly/2026-Q1/content-t7-quy1-v3.yaml \
      --out     09-reporting/quarterly/2026-Q1/<CLIENT>_bao-cao-T7-Quy1_v3.pptx

Ghi chú thiết kế:
  · Khổ 13,333 × 7,5 inch (16:9) khớp stage 1920×1080 của deck HTML → 1 px = 0,5 pt.
  · Bảng màu, cỡ chữ, bố cục bám theo `09-reporting/weekly-template/deck-skeleton.html`.
  · Font dùng Arial (có sẵn mọi máy + đủ dấu tiếng Việt). Font gốc của deck
    (Be Vietnam Pro / Bricolage Grotesque) là webfont, máy khách thường không có.
  · Gradient nền cover/agenda/Q&A dựng bằng shape có gradient fill.
  · Chữ viền (cover outline) và chữ gradient (Thank You) PowerPoint không có
    tương đương trực tiếp → xấp xỉ bằng màu đặc/độ trong.
"""

import argparse
import os
import re
import sys

import yaml
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Emu, Pt

# ─────────────────────────────────────────────── hệ toạ độ & bảng màu

EMU_PER_PX = 6350            # 1920 px = 13,333 in = 12.192.000 EMU
SLIDE_W, SLIDE_H = 1920, 1080


def px(v):
    return Emu(int(round(v * EMU_PER_PX)))


def pt(v):
    """px của deck → pt của PowerPoint (960 pt / 1920 px)."""
    return Pt(v * 0.5)


C = {
    "ink":      RGBColor(0x0B, 0x12, 0x26),
    "ink_soft": RGBColor(0x3B, 0x47, 0x5F),
    "mut":      RGBColor(0x64, 0x74, 0x8B),
    "mut_bg":   RGBColor(0xEE, 0xF2, 0xF7),
    "blue":     RGBColor(0x06, 0x93, 0xE3),
    "purple":   RGBColor(0x99, 0x00, 0xEF),
    "pos":      RGBColor(0x0E, 0x8A, 0x4D),
    "pos_bg":   RGBColor(0xEA, 0xF6, 0xEF),
    "neg":      RGBColor(0xD6, 0x1F, 0x3D),
    "neg_bg":   RGBColor(0xFD, 0xEE, 0xF1),
    "thead":    RGBColor(0x0F, 0x17, 0x2A),
    "row_alt":  RGBColor(0xF4, 0xF7, 0xFB),
    "kpi_hl":   RGBColor(0xFF, 0xF6, 0xDC),
    "border":   RGBColor(0xE2, 0xE8, 0xF0),
    "slide_bg": RGBColor(0xF7, 0xF9, 0xFC),
    "card":     RGBColor(0xFF, 0xFF, 0xFF),
    "white":    RGBColor(0xFF, 0xFF, 0xFF),
    "crumb":    RGBColor(0x94, 0xA3, 0xB8),
    "meta":     RGBColor(0x85, 0x93, 0xA8),
    "div_bg":   RGBColor(0xE7, 0xF3, 0xEC),
    "div_neg_bg": RGBColor(0xFB, 0xE9, 0xEC),
    "scope_bg": RGBColor(0xFF, 0xF8, 0xE1),
    "link":     RGBColor(0x06, 0x93, 0xE3),
    "scope_fg": RGBColor(0x8A, 0x6D, 0x00),
}

FONT = "Arial"

# khung chung mỗi slide nội dung (px)
PAD_L, PAD_R = 72, 72
CONTENT_TOP = 236
CONTENT_BOTTOM = 1010
CONTENT_W = SLIDE_W - PAD_L - PAD_R


def die(msg):
    sys.stderr.write("LỖI: %s\n" % msg)
    sys.exit(1)


# ─────────────────────────────────────────────── mini-markup → runs

_TOKEN = re.compile(r"\*\*(.+?)\*\*|\{(pos|neg|flat|mut|i)\}(.*?)\{/\2\}", re.S)
_ENT = [("&amp;", "&"), ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]
_MD_LINK = re.compile(r"\[([^\[\]]+?)\]\((https?://[^\s)]+)\)")
_SRC_TOKEN = re.compile(r"\[\[([^\[\]]+?)\]\]")
SOURCES = {}   # key -> {label, url} — nạp từ --sources, giống build_deck.py


def resolve_src(m):
    """[[key]] / [[key|nhãn]] → markdown [nhãn](url); không tra được thì trả nhãn trần."""
    key, _, label = m.group(1).partition("|")
    e = SOURCES.get(key.strip())
    text = label.strip() or (e or {}).get("label") or key.strip()
    return "[%s](%s)" % (text, e["url"]) if e else text


def clean(text):
    t = str(text if text is not None else "")
    t = _SRC_TOKEN.sub(resolve_src, t)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</?(b|i|em|strong|span)[^>]*>", "", t, flags=re.I)
    for a, b in _ENT:
        t = t.replace(a, b)
    return t


def parse_runs(text, bold=False, italic=False, color=None, link=None):
    """Trả về [(text, bold, italic, color, link)] — hiểu **đậm**, {pos}/{neg}/{mut}/{i},
    [nhãn](url) và [[key]] đã được resolve sẵn thành markdown link trước khi vào đây."""
    t = clean(text)
    out, i = [], 0
    for m in _MD_LINK.finditer(t):
        if m.start() > i:
            out.extend(parse_runs(t[i:m.start()], bold, italic, color, link))
        out.extend(parse_runs(m.group(1), bold, italic, C["link"], m.group(2)))
        i = m.end()
    if out or i:
        if i < len(t):
            out.extend(parse_runs(t[i:], bold, italic, color, link))
        return out or [("", bold, italic, color, link)]
    out, i = [], 0
    for m in _TOKEN.finditer(t):
        if m.start() > i:
            out.append((t[i:m.start()], bold, italic, color, link))
        if m.group(1) is not None:
            out.extend(parse_runs(m.group(1), True, italic, color, link))
        else:
            tok, inner = m.group(2), m.group(3)
            if tok == "i":
                out.extend(parse_runs(inner, bold, True, color, link))
            elif tok == "pos":
                out.extend(parse_runs(inner, True, italic, C["pos"], link))
            elif tok == "neg":
                out.extend(parse_runs(inner, True, italic, C["neg"], link))
            else:
                out.extend(parse_runs(inner, True, italic, C["mut"], link))
        i = m.end()
    if i < len(t):
        out.append((t[i:], bold, italic, color, link))
    return out or [("", bold, italic, color, link)]


def fill_para(para, text, size, color, bold=False, italic=False, font=FONT, bold_color=None):
    """Đổ mini-markup vào một paragraph, mỗi đoạn định dạng là một run."""
    for chunk, b, it, col, href in parse_runs(text, bold=bold, italic=italic, color=color):
        if chunk == "":
            continue
        r = para.add_run()
        r.text = chunk
        r.font.size = size
        r.font.name = font
        r.font.bold = bool(b)
        r.font.italic = bool(it)
        r.font.color.rgb = col if col is not None else (bold_color if (b and bold_color) else color)
        if href:
            # PowerPoint tự bôi màu theo theme khi có hyperlink → ép lại màu + gạch chân
            r.hyperlink.address = href
            r.font.color.rgb = C["link"]
            r.font.underline = True


def textbox(slide, x, y, w, h, text, size, color, bold=False, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, line=1.35, italic=False, font=FONT, wrap=True):
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = clean(text).split("\n")
    for k, ln in enumerate(lines):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        fill_para(p, ln, size, color, bold=bold, italic=italic, font=font)
    return box


def rect(slide, x, y, w, h, fill=None, shape=MSO_SHAPE.RECTANGLE, line=None, line_w=1):
    sh = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = px(line_w)
    sh.text_frame.word_wrap = True
    return sh


def gradient_rect(slide, x, y, w, h, c1, c2, angle=160, shape=MSO_SHAPE.RECTANGLE):
    sh = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
    sh.shadow.inherit = False
    sh.line.fill.background()
    sh.fill.gradient()
    stops = sh.fill.gradient_stops
    stops[0].color.rgb = c1
    stops[0].position = 0.0
    stops[1].color.rgb = c2
    stops[1].position = 1.0
    try:
        sh.fill.gradient_angle = angle
    except Exception:
        pass
    return sh


# ─────────────────────────────────────────────── chrome chung

def blank_slide(prs, bg=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])   # layout trắng
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg or C["slide_bg"]
    return s


def add_chrome(slide, sp, page_no):
    """crumb + pill + gạch gradient + tiêu đề + scope note + nguồn dữ liệu + số trang."""
    y = 56
    if sp.get("crumb"):
        textbox(slide, PAD_L, y, CONTENT_W, 22, clean(sp["crumb"]).upper(),
                pt(15), C["crumb"], align=PP_ALIGN.CENTER, line=1.0)
    y += 26
    if sp.get("pill"):
        textbox(slide, PAD_L, y, CONTENT_W, 24, clean(sp["pill"]).upper(),
                pt(19), C["blue"], bold=True, align=PP_ALIGN.CENTER, line=1.0)
        y += 30
        gradient_rect(slide, (SLIDE_W - 96) / 2, y, 96, 4, C["blue"], C["purple"], angle=0)
        y += 18
    if sp.get("sub"):
        head = clean(sp["sub"])
        if sp.get("idx"):
            head = "%s · %s" % (sp["idx"], head)
        textbox(slide, PAD_L, y, CONTENT_W, 108, head, pt(46), C["ink"],
                bold=True, align=PP_ALIGN.CENTER, line=1.16)
    if sp.get("scope_note"):
        box = rect(slide, PAD_L + 120, 196, CONTENT_W - 240, 34, C["scope_bg"], line=C["border"])
        tf = box.text_frame
        tf.margin_left = tf.margin_right = px(14)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        fill_para(p, sp["scope_note"], pt(18), C["scope_fg"])
    if sp.get("data_meta"):
        textbox(slide, PAD_L, 1016, 1500, 44, sp["data_meta"], pt(15), C["meta"], line=1.4)
    textbox(slide, SLIDE_W - 200, 1022, 170, 24, str(page_no), pt(16), C["meta"],
            align=PP_ALIGN.RIGHT, line=1.0)


def content_top(sp):
    return 250 if sp.get("scope_note") else CONTENT_TOP


# ─────────────────────────────────────────────── bảng

SOW_UU_COLOR = {"P0": RGBColor(0xD2, 0x1F, 0x3C), "P1": RGBColor(0xC7, 0x74, 0x00),
                "P2": RGBColor(0x5B, 0x6B, 0x8C), "P3": RGBColor(0x5B, 0x6B, 0x8C)}


def cell_spec(value):
    """Chuẩn hoá 1 ô: trả (text, class) — hiểu chuỗi JSON, dict {v,c}/{t,class}, hậu tố |cls."""
    cls = None
    if isinstance(value, str) and value.lstrip().startswith('{"'):
        import json
        try:
            value = json.loads(value)
        except ValueError:
            pass
    if isinstance(value, dict):
        cls = value.get("c", value.get("class"))
        value = value.get("v", value.get("t", ""))
    v = "" if value is None else str(value)
    m = re.match(r"^(.*)\|(pos|neg|mut|num|ctr|name|p0|p1|p2|p3)$", v)
    if m:
        v, cls = m.group(1), m.group(2)
    return v, (cls or "")


def col_widths(headers, rows, total_w):
    """Chia cột theo độ dài chữ trung bình, kẹp min/max để cột đầu không nuốt hết."""
    n = len(headers)
    # header có thể là dict {label, style} (build_deck dùng style để đặt width)
    heads = [(h.get("label", "") if isinstance(h, dict) else h) for h in headers]
    pct = [None] * n
    for j, h in enumerate(headers):
        if isinstance(h, dict):
            m = re.search(r"width\s*:\s*([\d.]+)%", h.get("style", "") or "")
            if m:
                pct[j] = float(m.group(1))
    if any(p is not None for p in pct):   # tôn trọng width khai tay, phần còn lại chia đều
        rest = 100.0 - sum(p for p in pct if p is not None)
        blank = [j for j in range(n) if pct[j] is None]
        for j in blank:
            pct[j] = max(4.0, rest / len(blank))
        widths = [int(total_w * p / sum(pct)) for p in pct]
        widths[-1] = total_w - sum(widths[:-1])
        return widths
    weights = []
    for j in range(n):
        samples = [len(clean(str(heads[j])))]
        for r in rows:
            cells = r.get("cells") if isinstance(r, dict) else r
            if not cells or (isinstance(r, dict) and r.get("class", "").startswith("divider")):
                continue
            if j < len(cells):
                txt, _ = cell_spec(cells[j])
                samples.append(len(clean(txt)))
        avg = sum(samples) / float(len(samples))
        weights.append(max(6.0, min(avg, 46.0)))
    tot = sum(weights)
    widths = [int(total_w * w / tot) for w in weights]
    widths[-1] = total_w - sum(widths[:-1])
    return widths


def style_cell(cell, text, cls, size, is_first_col, row_kind=""):
    cell.margin_left = cell.margin_right = px(9)
    cell.margin_top = cell.margin_bottom = px(4)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]

    fg, bg, align, bold = C["ink"], None, PP_ALIGN.LEFT, False
    if cls == "pos":
        fg, bg, align, bold = C["pos"], C["pos_bg"], PP_ALIGN.RIGHT, True
    elif cls == "neg":
        fg, bg, align, bold = C["neg"], C["neg_bg"], PP_ALIGN.RIGHT, True
    elif cls == "mut":
        fg, bg, align = C["mut"], C["mut_bg"], PP_ALIGN.RIGHT
    elif cls == "num":
        align = PP_ALIGN.RIGHT
    elif cls == "ctr":
        align = PP_ALIGN.CENTER
    elif cls == "name":
        bold = True
    elif cls in ("p0", "p1", "p2", "p3"):
        fg, align, bold = SOW_UU_COLOR[cls.upper()], PP_ALIGN.CENTER, True
    if row_kind == "kpi-row" and is_first_col:
        bg = C["kpi_hl"]
    if row_kind == "total":
        bold = True
        bg = RGBColor(0xED, 0xF1, 0xF8)

    p.alignment = align
    p.line_spacing = 1.18
    fill_para(p, text, size, fg, bold=bold)
    if bg is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
    else:
        cell.fill.background()


def add_table(slide, tbl, x, y, w, h):
    headers = tbl.get("headers") or []
    rows = tbl.get("rows") or []
    compact = "compact" in (tbl.get("class") or "")
    size = pt(19 if compact else 22)
    head_size = pt(18 if compact else 21)

    # dòng divider chỉ có key `divider` (không có `cells`) → không tính vào số cột
    ncol = max(len(headers), max((len(r.get("cells") or []) if isinstance(r, dict) else len(r)
                                  for r in rows), default=1))
    nrow = len(rows) + (1 if headers else 0)

    shape = slide.shapes.add_table(nrow, ncol, px(x), px(y), px(w), px(h))
    table = shape.table
    table.first_row = bool(headers)
    table.horz_banding = False

    widths = col_widths(headers or [""] * ncol, rows, w)
    for j, cw in enumerate(widths):
        table.columns[j].width = px(cw)

    head_h = 46 if compact else 52
    body_h = max(24, int((h - (head_h if headers else 0)) / max(1, len(rows))))
    r0 = 0
    if headers:
        table.rows[0].height = px(head_h)
        for j in range(ncol):
            cell = table.cell(0, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C["thead"]
            cell.margin_left = cell.margin_right = px(9)
            cell.margin_top = cell.margin_bottom = px(3)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.line_spacing = 1.15
            hv = headers[j] if j < len(headers) else ""
            if isinstance(hv, dict):
                hv = hv.get("label", "")
            fill_para(p, hv, head_size, C["white"], bold=True)
        r0 = 1

    for i, r in enumerate(rows):
        ri = r0 + i
        table.rows[ri].height = px(body_h)
        kind = r.get("class", "") if isinstance(r, dict) else ""
        cells = (r.get("cells") if isinstance(r, dict) else r) or []

        if kind.startswith("divider"):
            neg = kind == "divider-neg"
            first = table.cell(ri, 0)
            if ncol > 1:
                first.merge(table.cell(ri, ncol - 1))
            txt, _ = cell_spec(r.get("divider") if isinstance(r, dict) and r.get("divider")
                               else (cells[0] if cells else ""))
            first.margin_left = px(12)
            first.margin_top = first.margin_bottom = px(2)
            first.vertical_anchor = MSO_ANCHOR.MIDDLE
            first.fill.solid()
            first.fill.fore_color.rgb = C["div_neg_bg"] if neg else C["div_bg"]
            p = first.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            fill_para(p, txt, pt(18), C["neg"] if neg else C["pos"], bold=True)
            continue

        for j in range(ncol):
            txt, cls = cell_spec(cells[j]) if j < len(cells) else ("", "")
            style_cell(table.cell(ri, j), txt, cls, size, j == 0, kind)
            if not cls and kind != "kpi-row" and kind != "total" and (i % 2 == 1):
                cell = table.cell(ri, j)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C["row_alt"]
    return shape


# ─────────────────────────────────────────────── khối phụ

def add_bullets(slide, items, x, y, w, h, size_px=26, color=None, gap=8, min_px=17):
    """Danh sách gạch đầu dòng — tự thu nhỏ cỡ chữ cho vừa chiều cao được cấp."""
    items = items or []
    s = size_px
    while s > min_px:
        need = sum(est_height(it.get("text", "") if isinstance(it, dict) else it,
                              w - 26, s, line=1.42, pad=gap) for it in items)
        if need <= h:
            break
        s -= 1
    size = pt(s)
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for k, it in enumerate(items):
        text = it.get("text", "") if isinstance(it, dict) else it
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.line_spacing = 1.42
        p.space_after = Pt(gap * 0.5)
        set_bullet(p, s)
        fill_para(p, text, size, color or C["ink_soft"], bold_color=C["ink"])
    return box


def set_bullet(para, size_px):
    """Bật bullet tròn xanh + thụt treo ở cấp XML — dòng gãy canh thẳng lề chữ."""
    pPr = para._p.get_or_add_pPr()
    mar = int(size_px * 0.62 * EMU_PER_PX)
    pPr.set("marL", str(mar))
    pPr.set("indent", str(-mar))
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    clr = OxmlElement("a:buClr")
    srgb = OxmlElement("a:srgbClr")
    srgb.set("val", "0693E3")
    clr.append(srgb)
    fnt = OxmlElement("a:buFont")
    fnt.set("typeface", "Arial")
    ch = OxmlElement("a:buChar")
    ch.set("char", "\u2022")
    for el in (clr, fnt, ch):
        pPr.append(el)


def est_height(text, width_px, size_px, line=1.3, pad=20):
    """Ước lượng chiều cao cần cho một đoạn chữ Arial — dùng để chừa chỗ, tránh tràn đáy."""
    body = clean(text)
    per = max(6, int((width_px - 24) / (0.515 * size_px)))
    lines = 0
    for ln in body.split("\n"):
        lines += max(1, -(-len(ln) // per))
    return int(lines * size_px * line + pad)


def add_action(slide, action, x, y, w, h):
    card = rect(slide, x, y, w, h, C["card"], line=C["border"])
    rect(slide, x, y, 6, h, C["blue"])
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = px(24)
    tf.margin_right = px(20)
    tf.margin_top = tf.margin_bottom = px(10)
    p = tf.paragraphs[0]
    p.line_spacing = 1.3
    fill_para(p, action.get("label", ""), pt(24), C["ink"], bold=True)
    CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, it in enumerate(action.get("items") or []):
        text = it.get("text", "") if isinstance(it, dict) else it
        pre = "" if re.match(r"^\s*([①-⑳]|\(\d+\)|\d+[\.\)])", str(text)) else (
            (CIRCLED[i] if i < len(CIRCLED) else "(%d)" % (i + 1)) + " ")
        pa = tf.add_paragraph()
        pa.line_spacing = 1.3
        fill_para(pa, pre + str(text), pt(23), C["ink"])
    return card


# ─────────────────────────────────────────────── renderer từng loại slide

def r_cover(prs, sp, meta, page):
    s = blank_slide(prs)
    gradient_rect(s, 0, 0, SLIDE_W, SLIDE_H, C["blue"], C["purple"], angle=160)
    textbox(s, 110, 250, SLIDE_W - 220, 260, sp.get("title", ""), pt(104), C["white"],
            bold=True, line=1.06)
    if sp.get("outline"):
        tb = textbox(s, 110, 500, SLIDE_W - 220, 130, sp["outline"], pt(96), C["white"],
                     bold=True, line=1.08)
        for p in tb.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xCF, 0xE4, 0xF7)
    if sp.get("week_line"):
        textbox(s, 110, 660, SLIDE_W - 220, 46, sp["week_line"], pt(30), C["white"], line=1.2)
    if sp.get("domain"):
        textbox(s, 110, 712, SLIDE_W - 220, 36, sp["domain"], pt(22),
                RGBColor(0xDC, 0xE6, 0xF5), line=1.2)
    rect(s, 110, 962, SLIDE_W - 220, 2, RGBColor(0x9F, 0xBF, 0xE0))
    textbox(s, 110, 984, 900, 32, sp.get("footer", "PRESENTED BY GTV SEO"), pt(20),
            RGBColor(0xC9, 0xD4, 0xE6), bold=True, line=1.0)
    textbox(s, SLIDE_W - 400, 984, 290, 32, meta.get("client", ""), pt(20),
            RGBColor(0xC9, 0xD4, 0xE6), bold=True, align=PP_ALIGN.RIGHT, line=1.0)
    return s


def r_agenda(prs, sp, meta, page):
    s = blank_slide(prs, C["card"])
    gradient_rect(s, 640, 0, SLIDE_W - 640, SLIDE_H, C["blue"], C["purple"], angle=160)
    textbox(s, 90, 470, 470, 120, "AGENDA", pt(88), C["ink"], bold=True, line=1.0)
    gradient_rect(s, 92, 596, 140, 5, C["blue"], C["purple"], angle=0)
    items = sp.get("items") or []
    top, gap = 150, min(96, int((SLIDE_H - 300) / max(1, len(items))))
    for i, it in enumerate(items):
        textbox(s, 736, top + i * gap, SLIDE_W - 736 - 96, gap - 8,
                "%d.  %s" % (i + 1, clean(it)), pt(38), C["white"], bold=True, line=1.15)
    return s


def r_table_full(prs, sp, meta, page):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    below = (sp.get("below") or {}).get("bullets")
    avail = CONTENT_BOTTOM - top
    if below:
        bh = sum(est_height(b.get("text", "") if isinstance(b, dict) else b,
                            CONTENT_W - 26, 23, line=1.42, pad=8) for b in below)
        bh = max(70, min(int(avail * 0.46), bh + 8))
        th = avail - bh - 18
    else:
        th, bh = avail, 0
    add_table(s, sp["table"], PAD_L, top, CONTENT_W, th)
    if below:
        add_bullets(s, below, PAD_L, top + th + 18, CONTENT_W, bh, size_px=23)
    return s


def r_nhanxet(prs, sp, meta, page):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    avail = CONTENT_BOTTOM - top
    if sp.get("action"):
        ah = 150
        avail -= ah + 18
    cols = [sp.get("left") or {}] if sp.get("single") else [sp.get("left") or {}, sp.get("right") or {}]
    gap = 36
    cw = (CONTENT_W - gap * (len(cols) - 1)) / float(len(cols))
    for i, col in enumerate(cols):
        x = PAD_L + i * (cw + gap)
        if col.get("title"):
            m = re.search(r"color:\s*(#[0-9A-Fa-f]{6})", col.get("title_style", "") or "")
            tcol = RGBColor.from_string(m.group(1)[1:].upper()) if m else C["ink"]
            gradient_rect(s, x, top + 4, 6, 34, C["blue"], C["purple"], angle=0)
            textbox(s, x + 18, top, cw - 18, 46, col["title"], pt(34), tcol, bold=True, line=1.1)
        add_bullets(s, col.get("bullets"), x, top + 56, cw, avail - 56, size_px=25)
    if sp.get("action"):
        add_action(s, sp["action"], PAD_L, top + avail + 18, CONTENT_W, 150)
    return s


def r_image(prs, sp, meta, page, base):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    imgs = sp.get("images")
    if not imgs and sp.get("image"):
        imgs = [{"src": sp["image"], "label": sp.get("label", "")}]
    imgs = imgs or []
    maxh = sp.get("img_maxh") or 440
    bullets = sp.get("bullets")

    gap = 26
    n = max(1, len(imgs))
    slot_w = (CONTENT_W - gap * (n - 1)) / float(n)
    cap_h = 44 if any(i.get("label") for i in imgs) else 0

    # đo trước để canh giữa theo chiều dọc như .content của deck HTML
    boxes = []
    for im in imgs:
        path = os.path.join(base, im["src"]) if not os.path.isabs(im["src"]) else im["src"]
        if not os.path.exists(path):
            die("không thấy ảnh: %s" % path)
        with Image.open(path) as pic:
            iw, ih = pic.size
        sc = min(slot_w / iw, maxh / float(ih))
        boxes.append((path, iw * sc, ih * sc))
    row_h = max([b[2] for b in boxes] or [0])

    bh = 0
    if bullets:
        bh = sum(est_height(b.get("text", "") if isinstance(b, dict) else b,
                            CONTENT_W - 26, 23, line=1.42, pad=10) for b in bullets)
        bh = min(bh + 8, CONTENT_BOTTOM - top - row_h - cap_h - 30)
    total = row_h + cap_h + (22 + bh if bullets else 0)
    y = top + max(0, (CONTENT_BOTTOM - top - total) / 2.0)

    for k, (path, w, h) in enumerate(boxes):
        x = PAD_L + k * (slot_w + gap) + (slot_w - w) / 2.0
        iy = y + (row_h - h) / 2.0
        rect(s, x - 8, iy - 8, w + 16, h + 16, C["card"], line=C["border"])
        s.shapes.add_picture(path, px(x), px(iy), px(w), px(h))
        lbl = imgs[k].get("label")
        if lbl:
            textbox(s, PAD_L + k * (slot_w + gap), y + row_h + 10, slot_w, cap_h,
                    lbl, pt(20), C["mut"], align=PP_ALIGN.CENTER, line=1.25)

    if bullets:
        add_bullets(s, bullets, PAD_L, y + row_h + cap_h + 22, CONTENT_W, max(60, bh), size_px=23)
    return s


def r_chart(prs, sp, meta, page):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    ch = sp["chart"]
    note = sp.get("note")
    nh = min(230, max(80, est_height(note, CONTENT_W - 44, 23, line=1.3, pad=26))) if note else 0
    h = CONTENT_BOTTOM - top - nh - (18 if note else 0)

    data = CategoryChartData()
    data.categories = [clean(c) for c in ch.get("categories") or []]
    for ser in ch.get("series") or []:
        data.add_series(clean(ser.get("name", "")), tuple(ser.get("values") or ()))

    kind = (ch.get("kind") or "bar").lower()
    ctype = XL_CHART_TYPE.COLUMN_CLUSTERED if kind == "bar" else XL_CHART_TYPE.LINE_MARKERS
    frame = s.shapes.add_chart(ctype, px(PAD_L), px(top), px(CONTENT_W), px(h), data)
    chart = frame.chart
    chart.has_title = False
    chart.font.size = pt(20)
    chart.font.name = FONT
    chart.font.color.rgb = C["ink_soft"]

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False

    fmt = (ch.get("fmt") or "int").lower()
    try:
        va = chart.value_axis
        va.has_major_gridlines = True
        va.tick_labels.number_format_is_linked = False
        va.tick_labels.number_format = {"int": "#,##0", "pct": '0.0"%"'}.get(fmt, "#,##0.0")
        va.format.line.color.rgb = C["border"]
    except Exception:
        pass

    for i, ser in enumerate(ch.get("series") or []):
        col = ser.get("color")
        if not col:
            continue
        rgb = RGBColor.from_string(col.lstrip("#").upper())
        plot_ser = chart.series[i]
        if kind == "bar":
            plot_ser.format.fill.solid()
            plot_ser.format.fill.fore_color.rgb = rgb
        else:
            plot_ser.format.line.color.rgb = rgb
            plot_ser.format.line.width = px(4)

    if note:
        card = rect(s, PAD_L, CONTENT_BOTTOM - nh, CONTENT_W, nh, C["card"], line=C["border"])
        rect(s, PAD_L, CONTENT_BOTTOM - nh, 6, nh, C["blue"])
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = px(24)
        tf.margin_right = px(20)
        tf.margin_top = tf.margin_bottom = px(8)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.line_spacing = 1.3
        fill_para(p, note, pt(23), C["ink"])
    return s


def r_sow(prs, sp, meta, page):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    rows = sp.get("rows") or []
    norm = [{"hangmuc": (r.get("hangmuc") or "").strip(), "task": r.get("task", ""),
             "uu": str(r.get("uu_tien") or r.get("uu") or "").strip(),
             "pic": (r.get("pic") or "").strip(),
             "deadline": str(r.get("deadline") or "").strip(),
             "status": (r.get("status") or "").strip()} for r in rows]

    counts = {}
    for r in norm:
        counts[r["status"] or "—"] = counts.get(r["status"] or "—", 0) + 1
    chip_w = (CONTENT_W - 22 * (len(counts) - 1)) / float(max(1, len(counts)))
    for i, (label, n) in enumerate(counts.items()):
        x = PAD_L + i * (chip_w + 22)
        rect(s, x, top, chip_w, 92, C["card"], line=C["border"])
        col = {"Mới": C["blue"], "Chuyển tiếp": C["mut"], "Đang chờ Dev": C["neg"],
               "Done": C["pos"]}.get(label, C["mut"])
        textbox(s, x, top + 10, chip_w, 50, str(n), pt(48), col, bold=True,
                align=PP_ALIGN.CENTER, line=1.0)
        textbox(s, x, top + 62, chip_w, 24, label, pt(17), C["mut"],
                align=PP_ALIGN.CENTER, line=1.0)

    ty = top + 108
    has_uu = any(r["uu"] for r in norm)
    headers = ["Hạng mục", "Công việc", "Ưu tiên", "PIC", "Deadline", "Tiến độ"] if has_uu \
        else ["Hạng mục", "Công việc", "PIC", "Deadline", "Tiến độ"]
    trows = []
    prev = None
    for r in norm:
        hm = "" if r["hangmuc"] == prev else r["hangmuc"]
        prev = r["hangmuc"]
        cells = [("**%s**" % hm) if hm else "", r["task"]]
        if has_uu:
            cells.append('{"t":"%s","class":"%s"}' % (r["uu"], r["uu"].lower() or "ctr"))
        cells += ['{"t":"%s","class":"ctr"}' % r["pic"],
                  '{"t":"%s","class":"ctr"}' % r["deadline"],
                  '{"t":"%s","class":"ctr"}' % r["status"]]
        trows.append(cells)
    add_table(s, {"class": "data compact", "headers": headers, "rows": trows},
              PAD_L, ty, CONTENT_W, CONTENT_BOTTOM - ty)
    return s


def r_support(prs, sp, meta, page):
    s = blank_slide(prs)
    add_chrome(s, sp, page)
    top = content_top(sp)
    rows = sp.get("rows") or []
    note = sp.get("note")
    nh = 70 if note else 0
    headers = ["Blocker", "Ngày chờ", "Chặn KPI nào", "Chi phí trì hoãn", "Người quyết (khách)", "Hạn phản hồi"]
    trows = []
    for r in rows:
        trows.append(["**%s**" % clean(r.get("blocker", "")),
                      '{"t":"%s","class":"ctr"}' % clean(r.get("cho") or "—"),
                      clean(r.get("chan_kpi") or "—"),
                      clean(r.get("chi_phi") or "—"),
                      '{"t":"%s","class":"ctr"}' % clean(r.get("nguoi_quyet") or "—"),
                      '{"t":"**%s**","class":"ctr"}' % clean(r.get("han") or "—")])
    add_table(s, {"class": "data compact", "headers": headers, "rows": trows},
              PAD_L, top, CONTENT_W, CONTENT_BOTTOM - top - nh)
    if note:
        textbox(s, PAD_L, CONTENT_BOTTOM - nh + 8, CONTENT_W, nh, note, pt(22), C["mut"],
                align=PP_ALIGN.CENTER, line=1.3)
    return s


def r_qna(prs, sp, meta, page):
    s = blank_slide(prs)
    gradient_rect(s, 0, 0, SLIDE_W, SLIDE_H, C["blue"], C["purple"], angle=160)
    tb = textbox(s, 0, 330, SLIDE_W, 420, clean(sp.get("big", "Q&A")), pt(300), C["white"],
                 bold=True, align=PP_ALIGN.CENTER, line=1.0)
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = RGBColor(0x7F, 0xBF, 0xEE)
    textbox(s, 110, 120, SLIDE_W - 220, 110, clean(sp.get("title", "HỎI ĐÁP & THẢO LUẬN")),
            pt(76), C["white"], bold=True, line=1.1)
    rect(s, 110, 236, 760, 4, RGBColor(0xE8, 0xF1, 0xFB))
    return s


def r_thanks(prs, sp, meta, page):
    s = blank_slide(prs)
    textbox(s, 0, 400, SLIDE_W, 260, sp.get("word", "Thank You"), pt(180),
            RGBColor(0x4A, 0x4A, 0xD8), bold=True, italic=True,
            align=PP_ALIGN.CENTER, line=1.0, font="Georgia")
    textbox(s, 0, 900, SLIDE_W, 40, sp.get("foot", "PRESENTED BY GTV SEO"), pt(22),
            C["ink_soft"], bold=True, align=PP_ALIGN.CENTER, line=1.0)
    return s


RENDER = {
    "cover": r_cover, "agenda": r_agenda, "table_full": r_table_full,
    "nhanxet_2col": r_nhanxet, "chart": r_chart, "sow": r_sow,
    "support": r_support, "qna": r_qna, "thanks": r_thanks,
}


# ─────────────────────────────────────────────── main

def main():
    ap = argparse.ArgumentParser(description="content YAML → PowerPoint gốc (sửa được)")
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default=".", help="thư mục gốc để giải đường dẫn ảnh")
    ap.add_argument("--sources", help="YAML registry nguồn dữ liệu (token [[key]] → hyperlink)")
    args = ap.parse_args()

    if args.sources:
        with open(args.sources, encoding="utf-8") as f:
            sdoc = yaml.safe_load(f) or {}
        for k, v in (sdoc.get("sources") or {}).items():
            if v.get("url"):
                SOURCES[k] = v
        print("  sources: nạp %d nguồn từ %s" % (len(SOURCES), args.sources))

    with open(args.content, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    meta = doc.get("meta") or {}
    slides = doc.get("slides") or []

    prs = Presentation()
    prs.slide_width = px(SLIDE_W)
    prs.slide_height = px(SLIDE_H)
    prs.core_properties.title = meta.get("title", "Báo cáo")
    prs.core_properties.author = "GTV SEO"

    made = 0
    for i, sp in enumerate(slides, 1):
        t = sp.get("type")
        if t == "image":
            r_image(prs, sp, meta, i, args.base)
        elif t in RENDER:
            RENDER[t](prs, sp, meta, i)
        else:
            die("chưa hỗ trợ slide type «%s» (slide %d)" % (t, i))
        made += 1

    prs.save(args.out)
    size = os.path.getsize(args.out) / 1024.0
    print("PPTX: %s" % args.out)
    print("Slide: %d · %.1f KB · khổ %.3f × %.3f inch"
          % (made, size, prs.slide_width / 914400.0, prs.slide_height / 914400.0))


if __name__ == "__main__":
    main()
