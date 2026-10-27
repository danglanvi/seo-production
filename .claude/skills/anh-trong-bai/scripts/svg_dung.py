#!/usr/bin/env python3
"""Dựng sơ đồ SVG trong bài từ spec trong media_plan.json, theo màu và font của web-profile.

  python3 svg_dung.py <media_plan.json> --profile <web-profile.json> --out <thư mục media> [--only IMG-01,IMG-04]

Mỗi mục loai "so-do" có khối "so_do" với "kieu":
  luong       các bước nối tiếp: buoc[{tieu_de, mo_ta}], to[chỉ số tô đậm], nhom[{tu, den, nhan}]
  quyet-dinh  một câu hỏi rẽ hai nhánh: dau, hoi, co{nhan, ket_qua, tiep?}, khong{nhan, ket_qua, tiep?}
  khoi        các thực thể và quan hệ: khoi[{tieu_de, mo_ta}], noi[{tu, den, nhan, net: "dut"|"lien"}]
  so-sanh     các cột so sánh: cot[{tieu_de, dong[]}]
  moc         mốc thời gian: moc[{thoi_gian, tieu_de, mo_ta}]
  cot         biểu đồ thanh ngang: du_lieu[{nhan, gia_tri}], don_vi, nguon (bắt buộc)
  danh-sach   N mục đánh số: muc[{tieu_de, mo_ta}]
Mỗi sơ đồ ra 2 file: <ten_file>.svg (khung 760, desktop) và <ten_file>-m.svg (khung 320, điện thoại).
Ghi lại media_plan.json: svg, svg_m. Chữ dài tự xuống dòng theo bề rộng ước lượng; svg_kiem.mjs đo lại bằng Chrome.
Chỉ dùng Python stdlib.
"""
import argparse
import html
import json
import os
import re
import sys

E = html.escape
DW, MW = 760, 320  # bề rộng khung desktop và mobile; mobile 320 để chữ 13 px hiện khoảng 12 px trên máy 390 px
NARROW = set('iljtfr.,;:!|\'"()[] ')
WIDE = set('mwMW@%')


def text_w(s, fs, bold=False):
    w = 0.0
    for ch in s:
        if ch in NARROW:
            w += 0.32
        elif ch in WIDE:
            w += 0.86
        elif ch.isupper():
            w += 0.68
        elif ch.isdigit():
            w += 0.58
        else:
            w += 0.54
    return w * fs * (1.06 if bold else 1.0)


def wrap(s, max_w, fs, bold=False):
    words, lines, cur = str(s).split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if text_w(t, fs, bold) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines or ['']


class Svg:
    def __init__(self, W, pal, font, title, desc, pid='s'):
        self.W, self.p, self.font, self.title, self.desc, self.pid = W, pal, font, title, desc, pid
        self.parts, self.n, self.H = [], 0, 0

    def uid(self, k='b'):
        self.n += 1
        return f'{self.pid}-{k}{self.n}'

    def text_block(self, x, y, w, lines_spec, anchor='middle', owner=None):
        """lines_spec: [(chữ, cỡ, đậm, màu)]. Trả y cuối. Mỗi dòng xuống theo cỡ chữ x 1.32."""
        out = []
        for s, fs, bold, color in lines_spec:
            for ln in wrap(s, w, fs, bold):
                y += fs * 1.32
                tx = x + (w / 2 if anchor == 'middle' else 0)
                fw = ' font-weight="700"' if bold else ''
                ow = f' data-o="{owner}"' if owner else ''
                ta = 'middle' if anchor == 'middle' else 'start'
                out.append(f'<text x="{tx:.0f}" y="{y - fs * 0.32:.0f}" font-size="{fs}" fill="{color}"{fw} text-anchor="{ta}"{ow}>{E(ln)}</text>')
        self.parts += out
        return y

    def measure(self, w, lines_spec):
        return sum(len(wrap(s, w, fs, b)) * fs * 1.32 for s, fs, b, _ in lines_spec)

    def box(self, x, y, w, h, hi=False, dash=False):
        bid = self.uid()
        fill = 'url(#g)' if hi else self.p['nen']
        stroke = 'none' if hi else self.p['vien']
        da = ' stroke-dasharray="6 5"' if dash else ''
        self.parts.append(f'<rect id="{bid}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{da}/>')
        return bid

    def card(self, x, y, w, title, desc='', hi=False, pad=14, fs1=17, fs2=14, min_h=0):
        ink = '#FFFFFF' if hi else self.p['chu']
        sub = '#FFFFFF' if hi else self.p['chu_phu']
        spec = [(title, fs1, True, ink)] + ([(desc, fs2, False, sub)] if desc else [])
        h = max(min_h, self.measure(w - 2 * pad, spec) + 2 * pad + 4)
        bid = self.box(x, y, w, h, hi)
        self.text_block(x + pad, y + pad - 2, w - 2 * pad, spec, owner=bid)
        return h

    def arrow(self, x1, y1, x2, y2, dash=False, color=None, label=None, curve=0):
        c = color or self.p['phu']
        if curve:
            mx, my = (x1 + x2) / 2, min(y1, y2) - curve
            d = f'M{x1:.0f} {y1:.0f} Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}'
        else:
            d = f'M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}'
        da = ' stroke-dasharray="7 6"' if dash else ''
        self.parts.append(f'<path d="{d}" stroke="{c}" stroke-width="2.2" fill="none" marker-end="url(#a)"{da}/>')
        if label:
            lx, ly = (x1 + x2) / 2, ((y1 + y2) / 2 - curve / 2 - 8) if curve else (min(y1, y2) - 8)
            self.parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="13" fill="{self.p["chu_phu"]}" text-anchor="middle">{E(label)}</text>')

    def render(self):
        p = self.p
        g, a = self.pid + '-g', self.pid + '-a'
        defs = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p.get("grad1", p["chinh"])}"/>'
                f'<stop offset="1" stop-color="{p.get("grad2", p["phu"])}"/></linearGradient>'
                f'<marker id="{a}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0 0L10 5L0 10z" fill="{p["phu"]}"/></marker></defs>')
        H = int(self.H + 8)
        tid, did = self.uid('t'), self.uid('d')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {H}" role="img" aria-labelledby="{tid} {did}" '
                f'font-family="{E(self.font)}" style="max-width:100%;height:auto">'
                f'<title id="{tid}">{E(self.title)}</title><desc id="{did}">{E(self.desc)}</desc>{defs}'
                + ''.join(self.parts).replace('url(#g)', f'url(#{g})').replace('url(#a)', f'url(#{a})') + '</svg>')


def grid_rows(n, per):
    return [list(range(i, min(i + per, n))) for i in range(0, n, per)]


def k_luong(s, sp, mobile):
    steps, to = sp['buoc'], set(sp.get('to', []))
    W, gap = s.W, 34
    y = 8
    if sp.get('nhom') and not mobile:
        y += 30
    if mobile:
        w = W - 16
        pos = []
        starts = {g['tu']: g['nhan'] for g in sp.get('nhom', [])}
        for i, st in enumerate(steps):
            if i in starts:
                if i:
                    y -= gap - 22
                s.parts.append(f'<text x="8" y="{y + 15:.0f}" font-size="14" font-weight="700" fill="{s.p["chinh"]}">{E(starts[i])}</text>')
                y += 24
            h = s.card(8, y, w, st['tieu_de'], st.get('mo_ta', ''), i in to)
            pos.append((y, h))
            if i < len(steps) - 1:
                s.arrow(W / 2, y + h + 2, W / 2, y + h + gap - 4)
            y += h + gap
        for g in sp.get('nhom', []):
            y0, y1 = pos[g['tu']][0], pos[g['den']][0] + pos[g['den']][1]
            s.parts.append(f'<path d="M{W - 3} {y0:.0f}V{y1:.0f}" stroke="{s.p["chinh"]}" stroke-width="3"/>')
        s.H = y - gap + 8
        return
    one = sp.get('mot_hang') or len(steps) <= 4
    per = len(steps) if one else (4 if len(steps) == 8 else min(4, (len(steps) + 1) // 2))
    f1, f2, pad = (17, 14, 14) if len(steps) <= 5 or not one else (14, 12.5, 9)
    if one and len(steps) > 5:
        gap = 18
    for r, row in enumerate(grid_rows(len(steps), per)):
        w = (W - 16 - gap * (per - 1)) / per
        hs = [s.measure(w - 2 * pad, [(steps[i]['tieu_de'], f1, True, ''), (steps[i].get('mo_ta', ''), f2, False, '')]) + 2 * pad + 4 for i in row]
        h = max(hs)
        for j, i in enumerate(row):
            x = 8 + j * (w + gap)
            s.card(x, y, w, steps[i]['tieu_de'], steps[i].get('mo_ta', ''), i in to, pad=pad, fs1=f1, fs2=f2, min_h=h)
            if j < len(row) - 1:
                s.arrow(x + w + 3, y + h / 2, x + w + gap - 4, y + h / 2)
            if r == 0 and sp.get('nhom'):
                for g in sp['nhom']:
                    if g['tu'] == i:
                        x2 = 8 + (min(g['den'], row[-1]) - row[0]) * (w + gap) + w
                        s.parts.append(f'<path d="M{x:.0f} {y - 12:.0f}H{x2:.0f}" stroke="{s.p["chinh"]}" stroke-width="3"/>')
                        s.parts.append(f'<text x="{(x + x2) / 2:.0f}" y="{y - 20:.0f}" font-size="14" font-weight="700" fill="{s.p["chinh"]}" text-anchor="middle">{E(g["nhan"])}</text>')
        if r < len(grid_rows(len(steps), per)) - 1:
            # mũi tên gấp khúc: xuống nửa khoảng cách, sang trái tới cột đầu, rồi xuống hàng sau
            xa, xb, ym = 8 + (len(row) - 1) * (w + gap) + w / 2, 8 + w / 2, y + h + gap / 2
            s.parts.append(f'<path d="M{xa:.0f} {y + h + 2:.0f}V{ym:.0f}H{xb:.0f}V{y + h + gap - 4:.0f}" stroke="{s.p["phu"]}" '
                           f'stroke-width="2.2" fill="none" marker-end="url(#a)"/>')
        y += h + gap
    s.H = y - gap + 8


def k_quyet_dinh(s, sp, mobile):
    W, y, gap = s.W, 8, 34
    if mobile:
        w = W - 16
        h = s.card(8, y, w, sp['dau'])
        s.arrow(W / 2, y + h + 2, W / 2, y + h + gap - 4)
        y += h + gap
        h = s.card(8, y, w, sp['hoi'], hi=True)
        y += h
        half = (w - 14) / 2
        ys = y + gap + 14
        hmax = 0
        for k, (key, x) in enumerate((('co', 8), ('khong', 8 + half + 14))):
            b = sp[key]
            s.arrow(x + half / 2, y + 2, x + half / 2, ys - 4)
            s.parts.append(f'<text x="{x + half / 2 + 8:.0f}" y="{(y + ys) / 2 + 5:.0f}" font-size="13" font-weight="700" fill="{s.p["chu_phu"]}">{E(b["nhan"])}</text>')
            hh = s.card(x, ys, half, b['ket_qua'], b.get('tiep', ''), fs1=15, fs2=13)
            hmax = max(hmax, hh)
        s.H = ys + hmax + 8
        return
    w1, wq, g1, g2 = 200, 230, 46, 78
    xq, xr = 8 + w1 + g1, 8 + w1 + g1 + wq + g2
    wr = W - 8 - xr
    hc = s.card(xr, y, wr, sp['co']['ket_qua'], sp['co'].get('tiep', ''), fs1=16, fs2=13)
    yk = y + hc + 26
    hk = s.card(xr, yk, wr, sp['khong']['ket_qua'], sp['khong'].get('tiep', ''), fs1=16, fs2=13)
    cy = y + (hc + 26 + hk) / 2
    spec_d = [(sp['dau'], 17, True, '')]
    h1 = s.measure(w1 - 28, spec_d) + 32
    s.card(8, cy - h1 / 2, w1, sp['dau'])
    hq = s.measure(wq - 28, [(sp['hoi'], 17, True, '')]) + 32
    s.card(xq, cy - hq / 2, wq, sp['hoi'], hi=True)
    s.arrow(8 + w1 + 3, cy, xq - 4, cy)
    xm = xq + wq + 18
    for b, yt in ((sp['co'], y + hc / 2), (sp['khong'], yk + hk / 2)):
        s.parts.append(f'<path d="M{xq + wq + 2:.0f} {cy:.0f}H{xm:.0f}V{yt:.0f}H{xr - 4:.0f}" stroke="{s.p["phu"]}" stroke-width="2.2" fill="none" marker-end="url(#a)"/>')
        s.parts.append(f'<text x="{(xm + xr) / 2:.0f}" y="{yt - 8:.0f}" font-size="13" font-weight="700" fill="{s.p["chu_phu"]}" text-anchor="middle">{E(b["nhan"])}</text>')
    s.H = max(yk + hk, cy + h1 / 2, cy + hq / 2) + 8


def k_khoi(s, sp, mobile):
    bl, W, gap = sp['khoi'], s.W, 40
    if mobile:
        y, w, pos = 8, W - 70, []
        for i, b in enumerate(bl):
            h = s.card(8, y, w, b['tieu_de'], b.get('mo_ta', ''), b.get('to', False))
            pos.append((y, h))
            y += h + gap
        for k, r in enumerate(sp.get('noi', [])):
            a, b = sorted((r['tu'], r['den']))
            xa = 8 + w + 10 + k * 14
            ya, yb = pos[a][0] + pos[a][1] / 2, pos[b][0] + pos[b][1] / 2
            dash = ' stroke-dasharray="6 5"' if r.get('net') == 'dut' else ''
            s.parts.append(f'<path d="M{8 + w + 2} {ya:.0f}H{xa:.0f}V{yb:.0f}H{8 + w + 4}" stroke="{s.p["phu"]}" stroke-width="2" fill="none"{dash} marker-end="url(#a)"/>')
            if b - a == 1:
                s.parts.append(f'<text x="{W / 2 - 25:.0f}" y="{(pos[a][0] + pos[a][1] + pos[b][0]) / 2 + 5:.0f}" font-size="13" fill="{s.p["chu_phu"]}" text-anchor="middle">{E(r.get("nhan", ""))}</text>')
            else:
                s.parts.append(f'<text x="{W / 2 - 25:.0f}" y="{pos[b][0] - 12:.0f}" font-size="13" fill="{s.p["chu_phu"]}" text-anchor="middle">{E(r.get("nhan", ""))}</text>')
        s.H = y - gap + 8
        return
    n = len(bl)
    top = 70 if any(abs(r['tu'] - r['den']) > 1 for r in sp.get('noi', [])) else 12
    w = (W - 16 - gap * (n - 1)) / n
    h = max(s.measure(w - 28, [(b['tieu_de'], 17, True, ''), (b.get('mo_ta', ''), 14, False, '')]) + 32 for b in bl)
    xs = []
    for i, b in enumerate(bl):
        x = 8 + i * (w + gap)
        xs.append(x)
        s.card(x, top, w, b['tieu_de'], b.get('mo_ta', ''), b.get('to', False), min_h=h)
    for r in sp.get('noi', []):
        a, b = r['tu'], r['den']
        dash = r.get('net') == 'dut'
        if abs(a - b) == 1:
            lo, hi_ = sorted((a, b))
            s.arrow(xs[lo] + w + 3, top + h / 2, xs[hi_] - 4, top + h / 2, dash=dash)
            s.parts.append(f'<text x="{xs[lo] + w + gap / 2:.0f}" y="{top + h + 18:.0f}" font-size="13" fill="{s.p["chu_phu"]}" text-anchor="middle">{E(r.get("nhan", ""))}</text>')
        else:
            s.arrow(xs[a] + w / 2, top - 4, xs[b] + w / 2, top - 4, dash=dash, curve=58, label=r.get('nhan'))
    s.H = top + h + 26


def k_so_sanh(s, sp, mobile):
    cols, W, gap = sp['cot'], s.W, 14
    y = 8
    if mobile:
        for c in cols:
            h = s.card(8, y, W - 16, c['tieu_de'], ' · '.join(c['dong']), c.get('to', False))
            y += h + 12
        s.H = y
        return
    n = len(cols)
    w = (W - 16 - gap * (n - 1)) / n
    head = max(s.measure(w - 24, [(c['tieu_de'], 17, True, '')]) for c in cols) + 24
    rows = max(len(c['dong']) for c in cols)
    rh = [max(s.measure(w - 24, [(c['dong'][r] if r < len(c['dong']) else '', 14, False, '')]) for c in cols) + 18 for r in range(rows)]
    for i, c in enumerate(cols):
        x = 8 + i * (w + gap)
        bid = s.box(x, y, w, head + sum(rh) + 8, False)
        hb = s.box(x, y, w, head, True)
        s.text_block(x + 12, y + 10, w - 24, [(c['tieu_de'], 17, True, '#FFFFFF')], owner=hb)
        yy = y + head + 4
        for r in range(rows):
            if r < len(c['dong']):
                s.text_block(x + 12, yy + 4, w - 24, [(c['dong'][r], 14, False, s.p['chu'])], owner=bid)
            if r < rows - 1:
                s.parts.append(f'<path d="M{x + 12:.0f} {yy + rh[r]:.0f}H{x + w - 12:.0f}" stroke="{s.p["vien"]}" stroke-width="1"/>')
            yy += rh[r]
    s.H = y + head + sum(rh) + 16


def k_moc(s, sp, mobile):
    ms, W = sp['moc'], s.W
    if mobile:
        y, x0 = 8, 26
        line = len(s.parts)
        s.parts.append('')
        for m in ms:
            s.parts.append(f'<circle cx="{x0}" cy="{y + 14:.0f}" r="8" fill="url(#g)"/>')
            h = s.card(x0 + 22, y, W - x0 - 30, m['thoi_gian'] + ' · ' + m['tieu_de'], m.get('mo_ta', ''), fs1=15, fs2=13)
            y += h + 14
        s.parts[line] = f'<path d="M{x0} 14V{y - 20:.0f}" stroke="{s.p["vien"]}" stroke-width="3"/>'
        s.H = y
        return
    n = len(ms)
    w = (W - 16 - 14 * (n - 1)) / n
    ly = 34
    s.parts.append(f'<path d="M8 {ly}H{W - 8}" stroke="{s.p["vien"]}" stroke-width="3"/>')
    hmax = 0
    for i, m in enumerate(ms):
        x = 8 + i * (w + 14)
        s.parts.append(f'<circle cx="{x + w / 2:.0f}" cy="{ly}" r="9" fill="url(#g)"/>')
        s.parts.append(f'<text x="{x + w / 2:.0f}" y="{ly - 16}" font-size="14" font-weight="700" fill="{s.p["chinh"]}" text-anchor="middle">{E(m["thoi_gian"])}</text>')
        hmax = max(hmax, s.card(x, ly + 24, w, m['tieu_de'], m.get('mo_ta', ''), fs1=15, fs2=13))
    s.H = ly + 24 + hmax + 8


def k_cot(s, sp, mobile):
    data, W = sp['du_lieu'], s.W
    if not sp.get('nguon'):
        sys.exit(f'Biểu đồ "{s.title}" thiếu "nguon". Số liệu trên biểu đồ phải có nguồn.')
    lw = 120 if mobile else 230
    bw = W - 16 - lw - 70
    mx = max(float(d['gia_tri']) for d in data) or 1
    y = 8
    unit = sp.get('don_vi', '')
    for d in data:
        lines = wrap(d['nhan'], lw - 8, 14)
        h = max(30, len(lines) * 18 + 8)
        s.text_block(8, y + (h - len(lines) * 18) / 2 - 4, lw - 8, [(d['nhan'], 14, False, s.p['chu'])], anchor='start', owner=None)
        L = bw * float(d['gia_tri']) / mx
        fill = 'url(#g)' if d.get('to') else s.p['chinh']
        s.parts.append(f'<rect x="{8 + lw:.0f}" y="{y + h / 2 - 11:.0f}" width="{max(L, 2):.0f}" height="22" rx="6" fill="{fill}"/>')
        v = f'{d["gia_tri"]}{unit}'
        s.parts.append(f'<text x="{8 + lw + L + 8:.0f}" y="{y + h / 2 + 5:.0f}" font-size="14" font-weight="700" fill="{s.p["chu"]}">{E(v)}</text>')
        y += h + 6
    s.parts.append(f'<text x="8" y="{y + 16:.0f}" font-size="12" fill="{s.p["chu_phu"]}">Nguồn: {E(sp["nguon"])}</text>')
    s.H = y + 24


def k_danh_sach(s, sp, mobile):
    items, W = sp['muc'], s.W
    per = 1 if mobile else (sp.get('cot') or (2 if len(items) <= 4 else 3))
    gap, y = 14, 8
    for row in grid_rows(len(items), per):
        w = (W - 16 - gap * (per - 1)) / per
        specs = {i: [(items[i]['tieu_de'], 16, True, s.p['chu'])] + ([(items[i]['mo_ta'], 13.5, False, s.p['chu_phu'])] if items[i].get('mo_ta') else [])
                 for i in row}
        th = {i: s.measure(w - 70, specs[i]) for i in row}
        h = max(56, max(th.values()) + 28)
        for j, i in enumerate(row):
            x = 8 + j * (w + gap)
            bid = s.box(x, y, w, h, False)
            s.parts.append(f'<circle cx="{x + 28:.0f}" cy="{y + 28:.0f}" r="17" fill="url(#g)"/>'
                           f'<text x="{x + 28:.0f}" y="{y + 34:.0f}" font-size="16" font-weight="700" fill="#FFFFFF" text-anchor="middle">{i + 1}</text>')
            # thẻ chỉ có tiêu đề: căn giữa dọc theo vòng số; thẻ có mô tả: bắt đầu từ trên
            ty = y + 28 - th[i] / 2 - 2 if len(specs[i]) == 1 and th[i] < 40 else y + 10
            s.text_block(x + 56, ty, w - 70, specs[i], anchor='start', owner=bid)
        y += h + gap
    s.H = y - gap + 8


KIND = {'luong': k_luong, 'quyet-dinh': k_quyet_dinh, 'khoi': k_khoi, 'so-sanh': k_so_sanh, 'moc': k_moc, 'cot': k_cot, 'danh-sach': k_danh_sach}


def palette(profile):
    m = (profile.get('media') or {})
    p = {'chinh': '#2563EB', 'phu': '#7C3AED', 'chu': '#0F172A', 'chu_phu': '#475569', 'vien': '#CBD5E1', 'nen': '#FFFFFF', 'nen_nhat': '#F1F5F9', 'canh_bao': '#DC2626'}
    p.update(m.get('mau') or {})
    return p, m.get('font') or 'Arial, sans-serif'


def build(item, profile):
    sp = item['so_do']
    if sp.get('kieu') not in KIND:
        sys.exit(f'{item["id"]}: kieu "{sp.get("kieu")}" không hỗ trợ. Chọn một trong: {", ".join(KIND)}')
    pal, font = palette(profile)
    out = {}
    for mobile, W in ((False, DW), (True, MW)):
        pid = re.sub(r'[^a-z0-9]', '', item['id'].lower()) + ('m' if mobile else 'd')
        s = Svg(W, pal, font, item.get('alt', ''), item.get('caption', ''), pid)
        KIND[sp['kieu']](s, sp, mobile)
        out['m' if mobile else 'd'] = s.render()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plan')
    ap.add_argument('--profile', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only')
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding='utf-8'))
    profile = json.load(open(a.profile, encoding='utf-8'))
    only = set(a.only.split(',')) if a.only else None
    os.makedirs(a.out, exist_ok=True)
    base = os.path.dirname(os.path.abspath(a.plan))
    n = 0
    for it in plan['items']:
        if it.get('loai') != 'so-do' or not it.get('so_do') or (only and it['id'] not in only):
            continue
        name = it.get('ten_file') or it['id'].lower()
        res = build(it, profile)
        for k, suf in (('d', ''), ('m', '-m')):
            p = os.path.join(a.out, f'{name}{suf}.svg')
            open(p, 'w', encoding='utf-8').write(res[k])
        it['svg'] = os.path.relpath(os.path.join(a.out, name + '.svg'), base)
        it['svg_m'] = os.path.relpath(os.path.join(a.out, name + '-m.svg'), base)
        n += 1
        print(f'{it["id"]}\t{it["so_do"]["kieu"]}\t{it["svg"]}')
    json.dump(plan, open(a.plan, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{n} sơ đồ')


if __name__ == '__main__':
    main()
