#!/usr/bin/env python3
"""Hạng mục 13 đến 15 và phần phụ trợ của web-qa-gate v1.3 (Python stdlib, không cần mạng, không cần trình duyệt).

qa_gate.py nhập module này. Mỗi hàm check_* nhận số đo đã thu (jsonl của interact_probe.mjs, landmarks.mjs, HTML server) và trả
cùng cấu trúc với qa_gate.cat(): {status, summary, findings, notes}.
  13 check_interact   Tương tác và trạng thái: menu mobile, slider, trạng thái :hover/:focus/:active/:visited, màu nút theo kit
  14 check_layout     Toàn vẹn bố cục: lưới, số trong heading, CTA trùng link, cặp VI/EN, landmark
  15 check_og         Open Graph và Twitter Card
  ui-visual: check_tile_coverage, apply_sample
Chạy riêng: python3 -E qa_extra.py --help
"""
import argparse
import json
import math
import random
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

RANK = {"FAIL": 3, "WARN": 2, "PASS": 1, "SKIP": 0}


def cat(status, summary, findings=None, notes=None):
    return {"status": status, "summary": summary, "findings": findings or [], "notes": notes or []}


def worst(findings):
    return max((f["level"] for f in findings), key=RANK.get, default="PASS")


# ---------- Màu và tương phản ----------

def parse_color(c):
    """'rgb(1, 2, 3)', 'rgba(1,2,3,0.5)', '#abc', '#aabbcc', 'transparent' -> (r, g, b, a) hoặc None."""
    if not c:
        return None
    c = c.strip().lower()
    if c == "transparent":
        return (0, 0, 0, 0.0)
    m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", c)
    if m:
        a = m.group(4)
        a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    m = re.match(r"#([0-9a-f]{3,8})$", c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) in (6, 8):
            a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
    return None


def is_transparent(c):
    p = parse_color(c)
    return p is None or p[3] <= 0.02


def _lin(v):
    v /= 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def contrast(fg, bg):
    """Tỉ lệ tương phản WCAG. fg có alpha thì trộn lên bg; bg có alpha thì trộn lên trắng. Không đọc được màu thì trả None."""
    f, b = parse_color(fg), parse_color(bg)
    if not f or not b:
        return None
    b = tuple(b[i] * b[3] + 255 * (1 - b[3]) for i in range(3))
    f = tuple(f[i] * f[3] + b[i] * (1 - f[3]) for i in range(3))
    l1, l2 = sorted((luminance(f), luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def same_color(a, b, tol=4):
    pa, pb = parse_color(a), parse_color(b)
    return bool(pa and pb and all(abs(pa[i] - pb[i]) <= tol for i in range(3)))


def large_text(fs, fw):
    """WCAG: chữ lớn là từ 24 px, hoặc từ 18,66 px và đậm."""
    return (fs or 0) >= 24 or ((fs or 0) >= 18.66 and (fw or 400) >= 700)


# ---------- 13. Tương tác và trạng thái ----------

def _label(name, w, extra=""):
    return f"{name} {w}px{extra}"


def check_interact(rows, icfg=None):
    icfg = icfg or {}
    findings, notes, n = [], [], 0
    has_data = False

    def add(level, item, page, issue, **kw):
        findings.append({"item": item, "level": level, "page": page, "issue": issue, **kw})

    for r in rows:
        if r.get("kind", "page") != "page":
            continue
        name, vw = r.get("name"), r.get("vw")
        if r.get("err"):
            notes.append(f"đo lỗi: {name} {vw}px: {r['err']}")
            continue
        # 13a menu mobile
        m = r.get("menu")
        if m is not None:
            has_data = True
            n += 1
            if m.get("err"):
                add("WARN", "13a", name, f"{vw}px: {m['err']}")
            elif not m.get("found"):
                if m.get("declared"):
                    add("FAIL", "13a", name, f"{vw}px: nút menu khai báo không hiện" + (f" (có trong DOM: {m['hiddenSel']}, kích thước 0 hoặc ẩn)" if m.get("existsHidden") else " (không có trong DOM)"))
                else:
                    add("WARN", "13a", name, f"{vw}px: không thấy nút mở menu. Site không có menu mobile thì bỏ qua, nếu có thì khai interact.menu_toggle.selector")
            else:
                ink = m.get("ink") or []
                bg = m.get("bg") or "rgb(255, 255, 255)"
                if not ink:
                    add("FAIL", "13a", name, f"{vw}px: nút menu {m.get('sel')} ({m.get('w')}x{m.get('h')} px) có kích thước nhưng vạch và chữ trong suốt hoặc rỗng", button=m.get("sel"))
                else:
                    ratios = [contrast(i.get("color"), bg) for i in ink]
                    ratios = [x for x in ratios if x is not None]
                    if ratios and max(ratios) < 1.5:
                        add("FAIL", "13a", name, f"{vw}px: vạch hoặc chữ của nút menu {m.get('sel')} cùng màu nền (tương phản cao nhất {max(ratios):.2f}:1)", button=m.get("sel"))
                before, after = m.get("links"), m.get("linksAfter")
                if before is None or after is None:
                    add("WARN", "13a", name, f"{vw}px: không đọc được số link sau khi bấm")
                elif after - before <= 0:
                    add("FAIL", "13a", name, f"{vw}px: bấm nút menu {m.get('sel')} không tăng số link nhìn thấy (trước {before}, sau {after})", button=m.get("sel"))
        # 13b slider
        for s in r.get("sliders") or []:
            has_data = True
            n += 1
            sel = s.get("selector")
            if s.get("err"):
                add("WARN", "13b", name, f"{vw}px {sel}: {s['err']}")
            elif not s.get("found"):
                add("WARN", "13b", name, f"{vw}px: không thấy slider {sel}")
            elif not s.get("btn"):
                add("WARN" if s.get("items", 0) > 1 else "PASS", "13b", name, f"{vw}px {sel}: không thấy mũi tên next. Khai sliders[].next nếu theme dùng selector khác")
            elif not s.get("items"):
                add("WARN", "13b", name, f"{vw}px {sel}: không thấy thẻ nào. Khai sliders[].items")
            else:
                if s.get("covered"):
                    add("FAIL", "13b", name, f"{vw}px {sel}: mũi tên {s.get('btnSel')} bị che, bấm không tới: " + "; ".join(s["covered"][:3]), button=s.get("btnSel"))
                before, after = s.get("before"), s.get("after")
                if not s.get("disabled") and before is not None and after is not None and not s.get("covered"):
                    if sorted(before) == sorted(after) and s.get("items", 0) > len(before):
                        add("FAIL", "13b", name, f"{vw}px {sel}: bấm mũi tên không đổi tập thẻ nhìn thấy (vẫn thẻ {before}, tổng {s['items']} thẻ)", button=s.get("btnSel"))
                elif s.get("covered") and before is not None:
                    pass
        # 13c trạng thái
        for it in r.get("states") or []:
            has_data = True
            n += 1
            sel = it.get("selector")
            if not it.get("matched"):
                add("WARN", "13c", name, f"{vw}px: selector {sel} không khớp phần tử nào")
                continue
            bystate = defaultdict(list)
            low = defaultdict(list)
            for nd in it.get("nodes") or []:
                b = nd.get("base") or {}
                for st, v in (nd.get("states") or {}).items():
                    if not v.get("changed"):
                        bystate[st].append(nd.get("sel"))
                    thr = it.get("min_contrast") or (3.0 if large_text(v.get("fs"), v.get("fw")) else 4.5)
                    c = contrast(v.get("color"), v.get("bg"))
                    if c is not None and c < thr:
                        low[st].append(f"{nd.get('sel')} {c:.2f}:1")
            for st, ex in sorted(bystate.items()):
                level = "FAIL" if st == "focus" else "WARN"
                add(level, "13c", name, f"{vw}px {sel}: trạng thái :{st} không đổi kiểu hiển thị", examples=ex[:4])
            for st, ex in sorted(low.items()):
                add("FAIL", "13c", name, f"{vw}px {sel}: tương phản ở :{st} dưới ngưỡng", examples=ex[:4])
        # 13d màu nút theo kit
        kit = icfg.get("kit_button_colors") or {}
        colors = kit.get("colors") or []
        if r.get("buttons") is not None and colors:
            has_data = True
            n += 1
            tol = kit.get("tolerance", 4)
            bad = []
            for b in r["buttons"]:
                fill = b.get("bg")
                if is_transparent(fill):
                    if b.get("bgImage"):
                        continue
                    fill = b.get("border") if b.get("borderW") and not is_transparent(b.get("border")) else b.get("color")
                if not any(same_color(fill, k, tol) for k in colors):
                    bad.append(f"{b.get('sel')} \"{b.get('text')}\" {fill}")
            if bad:
                add("FAIL", "13d", name, f"{vw}px: {len(bad)} nút không dùng màu kit ({', '.join(colors)})", examples=bad[:4])
            # Chiều ngược: phần tử không phải CTA (accordion, tab, mũi tên slider) mang nền màu kit, thường do rule nút của kit tô mọi <button>.
            painted = [f"{b.get('sel')} \"{b.get('text')}\" {b.get('bg')}" for b in r.get("non_cta") or []
                       if not is_transparent(b.get("bg")) and any(same_color(b.get("bg"), k, tol) for k in colors)]
            if painted:
                add("WARN", "13d", name, f"{vw}px: {len(painted)} phần tử không phải CTA mang nền màu kit (rule nút của kit tô cả button khác)", examples=painted[:4])
    if any(r.get("buttons") for r in rows) and not (icfg.get("kit_button_colors") or {}).get("colors"):
        notes.append("13d bỏ qua: chưa khai interact.kit_button_colors.colors (màu kit Elementor của site).")
    if not has_data:
        return cat("SKIP", "chưa có số đo tương tác (khai khối interact trong qa.json)", notes=notes)
    findings = [f for f in findings if f["level"] != "PASS"]
    status = worst(findings)
    by = defaultdict(int)
    for f in findings:
        by[f["item"]] += 1
    summ = f"{n} phép đo, " + (", ".join(f"{k}: {v}" for k, v in sorted(by.items())) if by else "không có lỗi")
    return cat(status, summ, sorted(findings, key=lambda f: (-RANK[f["level"]], f["item"], f["page"])), notes)


# ---------- 14. Toàn vẹn bố cục ----------

def _rel_diff(a, b):
    return abs(a - b) / max(a, b, 1)


def _landmark_findings(r, add):
    name, vw, lm = r.get("name"), r.get("vw"), r.get("landmarks") or {}
    st = r.get("status")
    if st not in (200, None):
        add("FAIL", "14e", name, f"{vw}px: trang trả {st}, không đo landmark")
        return
    if lm.get("main", 0) != 1:
        add("FAIL", "14e", name, f"{vw}px: có {lm.get('main', 0)} phần tử main (cần đúng 1)", examples=lm.get("mainSel"))
    h1 = lm.get("h1") or []
    if len(h1) != 1:
        add("FAIL", "14e", name, f"{vw}px: có {len(h1)} thẻ h1 nhìn thấy (cần đúng 1)")
    elif lm.get("main") and "main" not in (h1[0].get("in") or ""):
        add("WARN", "14e", name, f"{vw}px: h1 nằm ngoài main (trong: {h1[0].get('in') or 'body'})")
    if lm.get("banner", 0) < 1:
        add("WARN", "14e", name, f"{vw}px: không có header cấp trang (banner)")
    if lm.get("contentinfo", 0) < 1:
        add("WARN", "14e", name, f"{vw}px: không có footer cấp trang (contentinfo)")
    mn = lm.get("menu")
    if mn and mn.get("links", 0) >= 3 and not (mn.get("tag") == "nav" or mn.get("role") == "navigation" or mn.get("inNav")):
        trap = " (menu nằm trong widget_text, plugin dựng bằng div)" if mn.get("widgetText") else ""
        add("FAIL", "14e", name, f"{vw}px: menu chính {mn.get('sel')} không nằm trong nav hay role=navigation{trap}", examples=[mn.get("sel")])
    elif not mn and not (lm.get("navs") or []):
        add("WARN", "14e", name, f"{vw}px: không tìm thấy menu chính. Khai landmarks.menu_selector")
    navs = [x for x in lm.get("navs") or [] if x.get("links", 0) >= 1]
    if len(navs) > 1:
        names = [x.get("label") for x in navs]
        if any(not x for x in names) or len(set(names)) < len(names):
            add("WARN", "14e", name, f"{vw}px: {len(navs)} vùng nav, tên truy cập thiếu hoặc trùng nhau", examples=[x.get("sel") for x in navs[:4]])
    if lm.get("banner", 0) > 1 or lm.get("contentinfo", 0) > 1:
        add("WARN", "14e", name, f"{vw}px: {lm.get('banner')} banner, {lm.get('contentinfo')} contentinfo (cần 1 mỗi loại)")
    if not lm.get("skip"):
        add("WARN", "14e", name, f"{vw}px: không thấy skip link")


def check_layout(rows, landmark_rows=(), icfg=None):
    findings, notes, n = [], [], 0

    def add(level, item, page, issue, **kw):
        findings.append({"item": item, "level": level, "page": page, "issue": issue, **kw})

    for r in rows:
        if r.get("kind", "page") == "pair":
            if r.get("err"):
                notes.append(f"đo lỗi cặp {r.get('name')}: {r['err']}")
                continue
            n += 1
            vi, en = r.get("vi") or {}, r.get("en") or {}
            nm = r.get("name")
            if vi.get("status") not in (200, None) or en.get("status") not in (200, None):
                add("FAIL", "14d", nm, f"cặp VI/EN: trang trả {vi.get('status')} và {en.get('status')}")
                continue
            a, b = vi.get("sig"), en.get("sig")
            if not a or not b:
                add("WARN", "14d", nm, "cặp VI/EN: thiếu số đo cấu trúc")
                continue
            hard = [k for k in ("h1", "h2", "h3", "forms") if a.get(k) != b.get(k)]
            if hard:
                add("WARN", "14d", nm, "cặp VI/EN lệch cấu trúc: " + ", ".join(f"{k} {a.get(k)} và {b.get(k)}" for k in hard))
            if a.get("grids") != b.get("grids"):
                add("WARN", "14d", nm, f"cặp VI/EN lệch số thẻ trong lưới: VI {a.get('grids')}, EN {b.get('grids')}")
            soft = [k for k in ("sections", "buttons", "images", "paragraphs") if abs(a.get(k, 0) - b.get(k, 0)) > 1 and _rel_diff(a.get(k, 0), b.get(k, 0)) > 0.1]
            if soft:
                add("WARN", "14d", nm, "cặp VI/EN lệch số lượng: " + ", ".join(f"{k} {a.get(k)} và {b.get(k)}" for k in soft))
            continue
        lay, name, vw = r.get("layout"), r.get("name"), r.get("vw")
        if r.get("err"):
            notes.append(f"đo lỗi: {name} {vw}px: {r['err']}")
            continue
        if lay is None:
            continue
        n += 1
        for g in lay.get("grids") or []:
            rows_ = g.get("rows") or []
            cols = g.get("cols", 0)
            if g.get("empty"):
                add("WARN", "14a", name, f"{vw}px: lưới {g.get('sel')} có {g['empty']} ô trống (không chữ, không ảnh, không nút)", examples=[g.get("sel")])
            if len(rows_) > 1 and any(c < cols for c in rows_[:-1]):
                add("WARN", "14a", name, f"{vw}px: lưới {g.get('sel')} thiếu ô giữa các hàng (số ô mỗi hàng {rows_})", examples=[g.get("sel")])
            elif cols > 1 and rows_ and rows_[-1] < cols and len(rows_) > 1:
                add("WARN", "14a", name, f"{vw}px: lưới {g.get('sel')} hàng cuối chỉ có {rows_[-1]}/{cols} ô ({g.get('n')} thẻ)", examples=[g.get("sel")])
        for c in lay.get("claims") or []:
            if c.get("missing"):
                add("WARN", "14b", name, f"{vw}px: không thấy {c['missing']} {c.get('heading')}")
            elif c.get("claimed") is None:
                add("WARN", "14b", name, f"{vw}px: heading {c.get('heading')} không có số: \"{c.get('text')}\"")
            elif c["claimed"] != c.get("cards"):
                add("FAIL", "14b", name, f"{vw}px: heading nói {c['claimed']}, thấy {c.get('cards')} thẻ (\"{c.get('text')}\")", examples=[c.get("heading")])
        for c in lay.get("ctas") or []:
            same = len(set(c.get("labels") or [])) == 1
            add("WARN", "14c", name,
                f"{vw}px: {len(c['labels'])} CTA trong {c.get('section')} cùng trỏ {c.get('href')}" + (" và cùng nhãn (có thể là bản lặp)" if same else ""),
                examples=c.get("labels"))
    for r in landmark_rows:
        if r.get("err"):
            notes.append(f"đo landmark lỗi: {r.get('name')} {r.get('vw')}px: {r['err']}")
            continue
        n += 1
        _landmark_findings(r, add)
    if not n and not notes:
        return cat("SKIP", "chưa có số đo bố cục (khai khối interact trong qa.json)")
    if not n:
        return cat("WARN", "mọi phép đo bố cục đều lỗi", notes=notes)
    status = worst(findings)
    by = defaultdict(int)
    for f in findings:
        by[f["item"]] += 1
    summ = f"{n} phép đo, " + (", ".join(f"{k}: {v}" for k, v in sorted(by.items())) if by else "không có lỗi")
    return cat(status, summ, sorted(findings, key=lambda f: (-RANK[f["level"]], f["item"], f["page"])), notes)


# ---------- 15. Open Graph ----------

def image_dims(data):
    """Đọc cỡ ảnh từ header (PNG, JPEG, GIF, WebP). Không đọc được thì trả None."""
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            k = data[12:16]
            if k == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
            if k == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return (w & 0x3FFF, h & 0x3FFF)
            if k == b"VP8L":
                b = int.from_bytes(data[21:25], "little")
                return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
        if data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                mk = data[i + 1]
                if mk in (0xD8, 0x01) or 0xD0 <= mk <= 0xD7:
                    i += 2
                    continue
                ln = struct.unpack(">H", data[i + 2:i + 4])[0]
                if mk in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return (w, h)
                i += 2 + ln
    except (struct.error, IndexError):
        return None
    return None


def meta_first(meta, key):
    v = (meta or {}).get(key) or []
    return v[0].strip() if v else ""


def _norm(u):
    s = urlsplit(u)
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), (s.path or "/").rstrip("/") or "/", s.query, ""))


def check_og(pages, images=None, canonical_host=None, min_width=1200):
    """pages: [{name, url, status, parsed:{meta, canonical}}]. images: {tên trang: {url, code, content_type, bytes, w, h}} từ lượt tải ảnh.
    FAIL: thiếu og:image, og:image tương đối hoặc svg, ảnh không tải được hoặc không phải ảnh. WARN: thiếu thẻ khác, webp/avif, ảnh nhỏ hoặc nặng."""
    images = images or {}
    findings, n, shared = [], 0, defaultdict(list)

    def add(level, page, issue, **kw):
        findings.append({"page": page, "level": level, "issue": issue, **kw})

    for p in pages:
        if p.get("status") not in (200, None):
            continue
        info = p.get("parsed") or {}
        meta = info.get("meta") or {}
        n += 1
        nm = p["name"]
        img = meta_first(meta, "og:image")
        if not img:
            add("FAIL", nm, "thiếu og:image")
        else:
            s = urlsplit(img)
            ext = Path(s.path).suffix.lower()
            if not s.scheme or not s.netloc:
                add("FAIL", nm, f"og:image là đường dẫn tương đối: {img}")
            else:
                shared[img].append(nm)
                if ext == ".svg":
                    add("FAIL", nm, f"og:image là SVG, Facebook và X không hiển thị: {img}")
                elif ext in (".webp", ".avif"):
                    add("WARN", nm, f"og:image là {ext[1:].upper()}, nền tảng chia sẻ an toàn nhất với JPEG hoặc PNG: {img}")
                if canonical_host and s.netloc.lower() != canonical_host.lower():
                    add("WARN", nm, f"og:image trỏ host khác canonical: {s.netloc}")
                if s.scheme == "http" and (p.get("url") or "").startswith("https"):
                    add("WARN", nm, "og:image dùng http trên trang https")
                im = images.get(nm)
                if im:
                    if str(im.get("code")) != "200":
                        add("FAIL", nm, f"og:image trả mã {im.get('code')}: {img}")
                    elif not str(im.get("content_type") or "").lower().startswith("image/"):
                        add("FAIL", nm, f"og:image không phải ảnh (content-type {im.get('content_type') or 'rỗng'}): {img}")
                    else:
                        w, h = im.get("w"), im.get("h")
                        if w and h:
                            if w < min_width:
                                add("WARN", nm, f"og:image rộng {w}px, dưới {min_width}px khuyến nghị cho ảnh chia sẻ lớn")
                            if not 1.6 <= w / h <= 2.0:
                                add("WARN", nm, f"og:image {w}x{h} tỉ lệ {w / h:.2f}, ngoài 1,6 đến 2,0: nền tảng sẽ cắt")
                            for k, v in (("og:image:width", w), ("og:image:height", h)):
                                t = meta_first(meta, k)
                                if t.isdigit() and int(t) != v:
                                    add("WARN", nm, f"{k} khai {t}, ảnh thật {v}")
                        if (im.get("bytes") or 0) > 5 * 1024 * 1024:
                            add("WARN", nm, f"og:image nặng {im['bytes'] // 1024} KB, X giới hạn 5 MB")
        miss = [k for k in ("og:title", "og:description", "og:url", "og:type") if not meta_first(meta, k)]
        if miss:
            add("WARN", nm, "thiếu " + ", ".join(miss))
        ogu, cans = meta_first(meta, "og:url"), (info.get("canonical") or [])
        if ogu and cans:
            c = urljoin(p.get("url") or "", cans[0])
            if _norm(ogu) != _norm(c):
                add("WARN", nm, f"og:url khác canonical: {ogu} và {c}")
        if not meta_first(meta, "twitter:card"):
            add("WARN", nm, "thiếu twitter:card")
        elif not meta_first(meta, "twitter:image") and img:
            add("WARN", nm, "thiếu twitter:image (X dùng og:image khi có twitter:card)")
        if not img and not meta_first(meta, "twitter:image"):
            add("FAIL", nm, "thiếu cả og:image lẫn twitter:image")
    if not n:
        return cat("SKIP", "không có HTML trang 200")
    notes = []
    dup = {u: v for u, v in shared.items() if len(v) >= 3}
    if dup:
        u, v = max(dup.items(), key=lambda kv: len(kv[1]))
        notes.append(f"{len(v)} trang dùng chung một og:image ({u}). Hợp lệ với ảnh mặc định, nhưng bài viết nên có ảnh riêng.")
    if not images:
        notes.append("Chưa tải ảnh og:image nên chưa kiểm mã HTTP, cỡ và dung lượng. Chạy run (không --skip og) để kiểm.")
    findings.sort(key=lambda f: (-RANK[f["level"]], f["page"]))
    status = worst(findings)
    return cat(status, f"{n} trang 200, {len({f['page'] for f in findings if f['level'] == 'FAIL'})} trang lỗi OG", findings, notes)


# ---------- ui-visual: phủ ảnh chụp ----------

def check_tile_coverage(browser_rows, tiles_mode="all"):
    """Mỗi URL x bề rộng cần ít nhất ceil(page_h / vh) màn chụp. Thiếu màn là FAIL khi tiles_mode là "all" (mặc định).
    Khi site chọn số màn cố định (mẫu), thiếu màn chỉ là WARN. Chạm trần tiles_max cũng là WARN."""
    out = []
    for r in browser_rows:
        if r.get("err") or "shots" not in r:
            continue
        shots = r["shots"]
        if not shots:
            out.append({"shot": f"{r.get('name')}|{r.get('vw')}", "level": "FAIL" if tiles_mode == "all" else "WARN", "issue": "không có ảnh chụp nào"})
            continue
        ph = max((s.get("page_h") or 0) for s in shots)
        vh = r.get("vh") or 900
        need = r.get("tiles_needed") or max(1, math.ceil(ph / vh))
        got = len(shots)
        if got >= need:
            continue
        capped = r.get("tiles_cap") is not None and got >= r["tiles_cap"] and tiles_mode == "all"
        level = "WARN" if (tiles_mode != "all" or capped) else "FAIL"
        why = "chạm trần tiles_max, tăng ui_visual.tiles_max" if capped else ("số màn chọn cố định" if tiles_mode != "all" else "chụp thiếu màn")
        out.append({"shot": f"{r.get('name')}|{r.get('vw')}", "level": level, "issue": f"chụp {got}/{need} màn (trang cao {ph}px, màn cao {vh}px): {why}"})
    return out


# ---------- Lấy mẫu URL (--sample) ----------

def apply_sample(items, spec, seed=1):
    """Chọn N phần tử hoặc P% số phần tử, cố định theo seed. Phần tử có always=True luôn nằm trong mẫu. Giữ thứ tự gốc."""
    if spec in (None, "", False):
        return list(items)
    m = re.match(r"^(\d+(?:\.\d+)?)(%?)$", str(spec).strip())
    if not m:
        raise ValueError("--sample nhận N hoặc P% (ví dụ 12 hoặc 15%)")
    want = math.ceil(len(items) * float(m.group(1)) / 100) if m.group(2) else int(float(m.group(1)))
    if want >= len(items):
        return list(items)
    keep = {i for i, x in enumerate(items) if x.get("always")}
    rest = [i for i in range(len(items)) if i not in keep]
    random.Random(seed).shuffle(rest)
    for i in rest:
        if len(keep) >= want:
            break
        keep.add(i)
    return [x for i, x in enumerate(items) if i in keep]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dims", help="in cỡ ảnh đọc từ header (png, jpeg, gif, webp)")
    d.add_argument("file")
    c = sub.add_parser("contrast", help="tỉ lệ tương phản WCAG giữa hai màu")
    c.add_argument("fg")
    c.add_argument("bg")
    a = ap.parse_args(argv)
    if a.cmd == "dims":
        dims = image_dims(Path(a.file).read_bytes())
        if not dims:
            print("không đọc được cỡ ảnh", file=sys.stderr)
            return 1
        print(f"{dims[0]}x{dims[1]}")
        return 0
    r = contrast(a.fg, a.bg)
    if r is None:
        print("không đọc được màu", file=sys.stderr)
        return 1
    print(f"{r:.2f}:1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
