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
  lan         nhiều vai theo làn: lan[tên], buoc[{tieu_de, mo_ta, lan, cot?, hoi?, to?}],
              noi[{tu, den, nhan, loai: "tien"|"sua"|"hoc"}] (thiếu thì nối bước liền nhau), vong[{tu, den, nhan, loai}]
  vong-lap    chuỗi một hàng có vòng phản hồi: buoc[{tieu_de, mo_ta, to}], vong[{tu, den, nhan, loai: "sua"|"hoc"}]
  so-lieu     ô số liệu: so[{gia_tri, nhan, truoc?, don_vi?, to?}], cot?, nguon (bắt buộc)
Mũi tên của lan và vong-lap đi theo trục, tránh hộp; vòng "sua" màu canh_bao, "hoc" màu chinh, nét đứt. Nhãn mũi tên có viền nền.
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


def _bo_goc(pts, r=8):
    """Đường gấp khúc → path có góc bo bán kính r (nhỏ hơn nửa đoạn ngắn), điểm cuối giữ nguyên cho đầu mũi tên."""
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for (x0, y0), (x1, y1), (x2, y2) in zip(pts, pts[1:], pts[2:]):
        l1, l2 = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        rr = min(r, l1 / 2, l2 / 2)
        if rr < 1:
            d += f' L{x1:.1f} {y1:.1f}'
            continue
        ax, ay = x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr
        bx, by = x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr
        d += f' L{ax:.1f} {ay:.1f} Q{x1:.1f} {y1:.1f} {bx:.1f} {by:.1f}'
    return d + f' L{pts[-1][0]:.1f} {pts[-1][1]:.1f}'


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
        da = ' stroke-dasharray="6 4"' if dash else ''
        self.parts.append(f'<path d="{d}" stroke="{c}" stroke-width="2" fill="none" marker-end="url(#a)"{da}/>')
        if label:
            lx, ly = (x1 + x2) / 2, ((y1 + y2) / 2 - curve / 2 - 8) if curve else (min(y1, y2) - 8)
            self.label(lx, ly, label)

    def label(self, x, y, s, color=None, fs=13, bold=False, anchor='middle'):
        """Nhãn mũi tên có viền màu nền, để đọc được khi nằm đè lên nét."""
        fw = ' font-weight="700"' if bold else ''
        # viền chữ cùng màu nền tại chỗ: trong dải làn là nen_nhat, ngoài là nen
        halo = self.p['nen_nhat'] if any(y1 <= y - fs / 2 <= y2 for y1, y2 in getattr(self, 'dai_nen', [])) else self.p['nen']
        self.parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{fs}" fill="{color or self.p["chu_phu"]}"{fw} text-anchor="{anchor}" '
                          f'paint-order="stroke" stroke="{halo}" stroke-width="5" stroke-linejoin="round">{E(s)}</text>')

    def path(self, pts, color='phu', dash=False):
        mk = {'phu': 'a', 'canh_bao': 'ar', 'chinh': 'ac'}[color]
        da = ' stroke-dasharray="6 4"' if dash else ''
        self.parts.append(f'<path d="{_bo_goc(pts)}" stroke="{self.p[color]}" stroke-width="2" fill="none" stroke-linejoin="round" marker-end="url(#{mk})"{da}/>')

    def diamond(self, x, y, w, h, title):
        cx, cy = x + w / 2, y + h / 2
        bid = self.uid()
        self.parts.append(f'<polygon id="{bid}" points="{cx:.0f},{y:.0f} {x + w:.0f},{cy:.0f} {cx:.0f},{y + h:.0f} {x:.0f},{cy:.0f}" '
                          f'fill="{self.p["nen"]}" stroke="{self.p["canh_bao"]}" stroke-width="1.8"/>')
        tw = w * 0.56
        th = self.measure(tw, [(title, 14, True, '')])
        self.text_block(cx - tw / 2, cy - th / 2 - 2, tw, [(title, 14, True, self.p['chu'])], owner=bid)

    def render(self):
        p = self.p
        g, a = self.pid + '-g', self.pid + '-a'
        # đầu mũi tên cỡ cố định (userSpaceOnUse), không phóng theo độ dày nét; khía sau để đầu nhọn, gọn
        mk = ''.join(f'<marker id="{self.pid}-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" '
                     f'orient="auto-start-reverse"><path d="M0.5 1L9.5 5L0.5 9L2.8 5z" fill="{p[c]}" stroke="{p[c]}" stroke-width="0.8" stroke-linejoin="round"/></marker>'
                     for k, c in (('a', 'phu'), ('ar', 'canh_bao'), ('ac', 'chinh')))
        defs = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p.get("grad1", p["chinh"])}"/>'
                f'<stop offset="1" stop-color="{p.get("grad2", p["phu"])}"/></linearGradient>{mk}</defs>')
        H = int(self.H + 8)
        tid, did = self.uid('t'), self.uid('d')
        body = ''.join(self.parts).replace('url(#g)', f'url(#{g})')
        for k in ('a', 'ar', 'ac'):
            body = body.replace(f'url(#{k})', f'url(#{self.pid}-{k})')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {H}" role="img" aria-labelledby="{tid} {did}" '
                f'font-family="{E(self.font)}" style="max-width:100%;height:auto">'
                f'<title id="{tid}">{E(self.title)}</title><desc id="{did}">{E(self.desc)}</desc>{defs}' + body + '</svg>')


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
            s.label(x + half / 2 + 8, (y + ys) / 2 + 5, b['nhan'], bold=True, anchor='start')
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
        s.label((xm + xr) / 2, yt - 8, b['nhan'], bold=True)
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
                s.label(W / 2 - 25, (pos[a][0] + pos[a][1] + pos[b][0]) / 2 + 5, r.get('nhan', ''))
            else:
                s.label(W / 2 - 25, pos[b][0] - 12, r.get('nhan', ''))
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
            s.label(xs[lo] + w + gap / 2, top + h + 18, r.get('nhan', ''))
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


MAU = {'tien': ('phu', False), 'sua': ('canh_bao', True), 'hoc': ('chinh', True)}


def _cat(seg, r, m=3):
    """Đoạn theo trục seg có cắt hình chữ nhật r = (x, y, w, h) nới m px (m âm: chỉ phần lõi) không."""
    (x1, y1), (x2, y2) = seg
    rx, ry, rw, rh = r
    return min(x1, x2) < rx + rw + m and max(x1, x2) > rx - m and min(y1, y2) < ry + rh + m and max(y1, y2) > ry - m


def _ranh(pts, rects, a, b):
    """Đường gấp khúc không cắt hộp nào khác, và không đi xuyên lõi hộp đầu, hộp cuối."""
    for seg in zip(pts, pts[1:]):
        for k, r in enumerate(rects):
            if _cat(seg, r, -3 if k in (a, b) else 3):
                return False
    return True


def _duong(rects, a, b, loai, gap, tren, duoi, oa=0, ob=0):
    """Các phương án đường theo trục từ hộp a tới hộp b, xếp theo ưu tiên: [(tên, điểm)]. oa, ob: lệch điểm ra, điểm vào."""
    ax, ay, aw, ah = rects[a]
    bx, by, bw, bh = rects[b]
    acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
    phai, xuong = bcx > acx + 1, bcy > acy + 1
    a_ra, b_vao = (ax + aw, bx) if phai else (ax, bx + bw)
    a_dung, b_dung = (ay + ah, by) if xuong else (ay, by + bh)
    kenh = [('tren', [(acx + oa, ay), (acx + oa, tren), (bcx + ob, tren), (bcx + ob, by)]),
            ('duoi', [(acx + oa, ay + ah), (acx + oa, duoi), (bcx + ob, duoi), (bcx + ob, by + bh)])]
    if loai == 'tien':
        kenh.reverse()
    if abs(acy - bcy) < 1:
        thang = [('thang', [(a_ra, acy + oa), (b_vao, bcy + oa)])] if loai == 'tien' else []
        return thang + kenh
    if abs(acx - bcx) < 1:
        # cùng cột: thẳng, hoặc ra cạnh bên, đi dọc trong khe cạnh cột (khi có hộp khác ở giữa), rồi vào cạnh bên
        # ra và vào ở nửa hộp hướng về nhau: đường dọc ngắn hơn, không cắt mũi tên khác vào giữa cạnh hộp
        hg = 1 if bcy > acy else -1
        ya, yb = acy + hg * abs(oa), bcy - hg * abs(ob)
        ben = [(t, [(x0, ya), (gx, ya), (gx, yb), (x0, yb)])
               for t, x0, gx in (('trai', ax, ax - gap / 2), ('phai', ax + aw, ax + aw + gap / 2)) if gx > 0]
        return [('thang', [(acx + oa, a_dung), (bcx + oa, b_dung)])] + ben + kenh
    c = []
    if (acx + oa < bx) if phai else (acx + oa > bx + bw):
        c.append(('l1', [(acx + oa, a_dung), (acx + oa, bcy + ob), (b_vao, bcy + ob)]))
    if (acy + oa < by) if xuong else (acy + oa > by + bh):
        c.append(('l2', [(a_ra, acy + oa), (bcx + ob, acy + oa), (bcx + ob, b_dung)]))
    if loai != 'tien':
        c.reverse()
    for gx in ((ax + aw + gap / 2) if phai else (ax - gap / 2), (bx - gap / 2) if phai else (bx + bw + gap / 2)):
        if (ax + aw <= gx <= bx) if phai else (bx + bw <= gx <= ax):
            c.append(('z', [(a_ra, acy + oa), (gx, acy + oa), (gx, bcy + ob), (b_vao, bcy + ob)]))
    return c + kenh


def _rut(pts):
    """Lùi điểm cuối 4 px cho đầu mũi tên, đẩy điểm đầu 2 px ra khỏi viền hộp."""
    def dich(p, q, d):
        dx, dy = q[0] - p[0], q[1] - p[1]
        n = (dx * dx + dy * dy) ** 0.5 or 1
        return (p[0] + dx / n * d, p[1] + dy / n * d)
    pts = list(pts)
    pts[0] = dich(pts[0], pts[1], 2)
    pts[-1] = dich(pts[-1], pts[-2], 4)
    return pts


def _nhan_duong(s, pts, text, color, tren_hop):
    """Đặt nhãn trên đoạn ngang dài nhất đủ chỗ, rồi cạnh đoạn dọc dài nhất; mũi tên ngắn thì đặt ở dải trên mép hộp nguồn."""
    segs = list(zip(pts, pts[1:]))
    ngang = [g for g in segs if abs(g[0][1] - g[1][1]) < 1 and abs(g[0][0] - g[1][0]) >= text_w(text, 13, True) + 12]
    if ngang:
        (x1, y1), (x2, _) = max(ngang, key=lambda g: abs(g[0][0] - g[1][0]))
        s.label((x1 + x2) / 2, y1 - 7, text, color, bold=True)
        return
    (x1, y1), (x2, y2) = max(segs, key=lambda g: abs(g[0][1] - g[1][1]))
    if abs(y1 - y2) >= 24:
        ym, tw = (y1 + y2) / 2 + 5, text_w(text, 13, True)
        hop = getattr(s, 'hop_ve', [])
        trung = lambda bx: any(bx < x + w and bx + tw > x and ym - 13 < y + h and ym + 3 > y for x, y, w, h in hop)
        if trung(x1 + 7) and not trung(x1 - 7 - tw):
            s.label(x1 - 7, ym, text, color, bold=True, anchor='end')
        else:
            s.label(x1 + 7, ym, text, color, bold=True, anchor='start')
    else:
        (x1, _), (x2, _) = segs[0]
        s.label((x1 + x2) / 2, tren_hop - 7, text, color, bold=True)


def _canh(sp, n):
    noi = sp.get('noi') or [{'tu': i, 'den': i + 1} for i in range(n - 1)]
    edges = [dict(e, loai=e.get('loai', 'tien')) for e in noi] + [dict(v, loai=v.get('loai', 'sua')) for v in sp.get('vong', [])]
    for e in edges:
        if e['loai'] not in MAU or not (0 <= e['tu'] < n and 0 <= e['den'] < n) or e['tu'] == e['den']:
            sys.exit(f'Cạnh {e} sai: loai là tien|sua|hoc, tu và den là chỉ số bước khác nhau trong 0..{n - 1}')
    return edges


def k_lan(s, sp, mobile):
    st, lanes = sp['buoc'], sp.get('lan') or ['']
    if any(not 0 <= b.get('lan', 0) < len(lanes) for b in st):
        sys.exit(f'"{s.title}": mỗi bước cần "lan" trong 0..{len(lanes) - 1}')
    edges, named = _canh(sp, len(st)), any(lanes)
    if mobile:
        return _lan_doc(s, st, lanes, edges, named)
    nc = max(b.get('cot', i) for i, b in enumerate(st)) + 1
    cot = lambda i: st[i].get('cot', i)
    gap = 30
    # khe giữa 2 cột liền nhau giãn đủ chỗ cho nhãn của mũi tên ngang cùng làn ("Có", "Không")
    khe = [gap] * max(nc - 1, 0)
    for e in edges:
        a, b = e['tu'], e['den']
        if e.get('nhan') and e['loai'] == 'tien' and st[a].get('lan', 0) == st[b].get('lan', 0) and abs(cot(a) - cot(b)) == 1:
            k = min(cot(a), cot(b))
            khe[k] = max(khe[k], text_w(e['nhan'], 13, True) + 20)
    w = (s.W - 16 - sum(khe)) / nc
    xc = [8 + c * w + sum(khe[:c]) for c in range(nc)]
    f1, f2, pad = (15, 13, 10) if w >= 150 else (13.5, 12, 8)

    def cao(b):
        if b.get('hoi'):
            return max(66, s.measure(w * 0.56, [(b['tieu_de'], 14, True, '')]) + 36)
        return s.measure(w - 2 * pad, [(b['tieu_de'], f1, True, ''), (b.get('mo_ta', ''), f2, False, '')]) + 2 * pad + 4
    lh = {}
    for b in st:
        lh[b.get('lan', 0)] = max(lh.get(b.get('lan', 0), 0), cao(b))
    head = 26 if named else (22 if any(e.get('nhan') and e['loai'] == 'tien' for e in edges) else 0)
    ly, y = {}, 0
    for L in range(len(lanes)):
        ly[L] = y
        y += head + lh.get(L, 40) + (12 if named else 0) + 6
    bottom = y - 6
    rects = [(xc[cot(i)], ly[b.get('lan', 0)] + head, w, lh[b.get('lan', 0)]) for i, b in enumerate(st)]
    # tên làn cũng là vật cản: mũi tên không đi qua chữ
    can = rects + ([(8, ly[L] + 4, text_w(n.upper(), 12, True) + 8, 18) for L, n in enumerate(lanes)] if named else [])
    s.tuyen, s.rects = [], can
    nt = nd = 0
    dem = {}
    # cạnh tiến trước; vòng ngắn trước vòng dài để vòng ngắn nằm kênh gần hộp
    for e in sorted(edges, key=lambda e: (e['loai'] != 'tien', abs(cot(e['tu']) - cot(e['den'])))):
        a, b = e['tu'], e['den']
        oa = ob = 0
        if e['loai'] != 'tien':
            # vòng đi sang trái: ra lệch phải, vào lệch trái; vòng dài lệch xa hơn để không cắt vòng ngắn
            sg = 1 if cot(b) <= cot(a) else -1
            oa = sg * min(18 * (1 + dem.get(a, 0)), w / 2 - 8)
            ob = -sg * min(18 * (1 + dem.get(b, 0)), w / 2 - 8)
            dem[a], dem[b] = dem.get(a, 0) + 1, dem.get(b, 0) + 1
        cands = _duong(rects, a, b, e['loai'], gap, -16 - 24 * nt, bottom + 16 + 24 * nd, oa, ob)
        ten, pts = next((c for c in cands if _ranh(c[1], can, a, b)), next(c for c in cands if c[0] == 'tren'))
        nt += ten == 'tren'
        nd += ten == 'duoi'
        sach = _ranh(pts, can, a, b)
        if not _ranh(pts, rects, a, b):  # chỉ cắt tên làn thì không cảnh báo: tên làn tự dời chỗ khi vẽ
            print(f'CANH BAO "{s.title[:40]}": cạnh {a}→{b} không tìm được đường không cắt hộp; đổi "cot" hoặc tách sơ đồ', file=sys.stderr)
        s.tuyen.append((e, pts, sach))
    dy = 40 + 24 * (nt - 1) if nt else 8
    for L, name in enumerate(lanes):
        if named:
            s.parts.append(f'<rect x="0" y="{ly[L] + dy:.0f}" width="{s.W}" height="{head + lh.get(L, 40) + 12:.0f}" rx="12" fill="{s.p["nen_nhat"]}"/>')
            # đường vào hộp đầu làn buộc phải qua dải tên làn: dời tên sang khoảng trống đầu tiên không có nét nào
            tw, tx = text_w(name.upper(), 12, True), 12
            chan = sorted((min(p[0], q[0]) - 14, max(p[0], q[0]) + 14) for _, pts, _ in s.tuyen for p, q in zip(pts, pts[1:])
                          if min(p[1], q[1]) <= ly[L] + 24 and max(p[1], q[1]) >= ly[L] + 2)
            for x1, x2 in chan:
                if x1 < tx + tw and x2 > tx:
                    tx = x2
            tx = tx if tx + tw <= s.W - 8 else 12
            s.ten_lan = getattr(s, 'ten_lan', []) + [(tx, ly[L] + 4, tw, 18)]
            s.parts.append(f'<text x="{tx:.0f}" y="{ly[L] + dy + 18:.0f}" font-size="12" font-weight="700" fill="{s.p["chinh"]}">{E(name.upper())}</text>')
    for (x, yy, ww, hh), b in zip(rects, st):
        if b.get('hoi'):
            s.diamond(x, yy + dy, ww, hh, b['tieu_de'])
        else:
            s.card(x, yy + dy, ww, b['tieu_de'], b.get('mo_ta', ''), b.get('to', False), pad=pad, fs1=f1, fs2=f2, min_h=hh)
    s.dai_nen = [(ly[L] + dy, ly[L] + dy + head + lh.get(L, 40) + 12) for L in range(len(lanes))] if named else []
    s.hop_ve = [(x, yy + dy, ww, hh) for x, yy, ww, hh in rects]
    for e, pts, _ in s.tuyen:
        color, dash = MAU[e['loai']]
        pts = _rut([(x, yy + dy) for x, yy in pts])
        s.path(pts, color, dash)
        if e.get('nhan'):
            _nhan_duong(s, pts, e['nhan'], s.p[color] if e['loai'] != 'tien' else None, rects[e['tu']][1] + dy)
    s.H = dy + bottom + (16 + 24 * nd if nd else 4)


def _lan_doc(s, st, lanes, edges, named):
    """Bản điện thoại: các bước xếp dọc theo thứ tự, thẻ ghi tên làn; cạnh nhảy cóc đi rãnh phải, vòng lùi đi rãnh trái."""
    gl, gr = 30, 22
    x, w = 8 + gl, s.W - 16 - gl - gr
    # nhãn của cạnh đi rãnh đặt dưới thẻ nguồn, trong nửa thẻ phía rãnh: khoảng cách sau thẻ giãn theo số dòng nhãn
    nw = w / 2 - 16
    nl = [sum(len(wrap(e['nhan'], nw, 13, True)) for e in edges if e['tu'] == i and e['den'] != i + 1 and e.get('nhan'))
          for i in range(len(st))]
    y, rects = 8, []
    for i, b in enumerate(st):
        if b.get('hoi'):
            h = max(70, s.measure(w * 0.45, [(b['tieu_de'], 14, True, '')]) + 40)
            s.diamond(x + w * 0.1, y, w * 0.8, h, b['tieu_de'])
            rects.append((x + w * 0.1, y, w * 0.8, h))
            y += h + 32 + 16 * max(0, nl[i] - 1)
            continue
        else:
            hi = b.get('to', False)
            ink, sub, chip = ('#FFFFFF',) * 3 if hi else (s.p['chu'], s.p['chu_phu'], s.p['chinh'])
            spec = ([(lanes[b.get('lan', 0)].upper(), 12, True, chip)] if named else []) + [(b['tieu_de'], 15, True, ink)]
            spec += [(b['mo_ta'], 13, False, sub)] if b.get('mo_ta') else []
            h = s.measure(w - 24, spec) + 28
            bid = s.box(x, y, w, h, hi)
            s.text_block(x + 12, y + 10, w - 24, spec, owner=bid)
        rects.append((x, y, w, h))
        y += h + 32 + 16 * max(0, nl[i] - 1)
    # rãnh: cạnh tiến mặc định bên phải, vòng lùi bên trái; cạnh cắt chéo một cạnh cùng rãnh (hai khoảng chồng một phần)
    # thì sang rãnh kia, để các vòng lồng nhau thay vì cắt nhau
    cheo = lambda p, q: p[0] < q[0] < p[1] < q[1] or q[0] < p[0] < q[1] < p[1]
    phai, dat = {}, {True: [], False: []}
    for i in sorted((i for i, e in enumerate(edges) if e['den'] != e['tu'] + 1), key=lambda i: abs(edges[i]['den'] - edges[i]['tu'])):
        e = edges[i]
        k, side = (min(e['tu'], e['den']), max(e['tu'], e['den'])), e['den'] > e['tu']
        if any(cheo(k, q) for q in dat[side]) and not any(cheo(k, q) for q in dat[not side]):
            side = not side
        phai[i] = side
        dat[side].append(k)
    s.ranh_doc = dat
    kl = kr = 0
    xep, ra_, vao_ = {}, {}, {}
    # cạnh liền nhau trước; cạnh đi rãnh xếp từ ngắn tới dài: cạnh ngắn ở rãnh trong, cạnh dài ở rãnh ngoài
    for i in sorted(range(len(edges)), key=lambda i: (edges[i]['den'] != edges[i]['tu'] + 1, abs(edges[i]['den'] - edges[i]['tu']))):
        e = edges[i]
        a, b = e['tu'], e['den']
        (xa, ya, wa, ha), (xb, yb, wb, hb) = rects[a], rects[b]
        color, dash = MAU[e['loai']]
        lc = s.p[color] if e['loai'] != 'tien' else None
        if b == a + 1:
            cx = x + w / 2
            s.path(_rut([(cx, ya + ha), (cx, yb)]), color, dash)
            if e.get('nhan'):
                # cùng nguồn đã có nhãn rãnh phải (dưới thẻ, nửa phải): nhãn mũi tên giữa đặt sang trái
                trai = any(phai.get(j) and f['tu'] == a and f.get('nhan') for j, f in enumerate(edges))
                s.label(cx - 8 if trai else cx + 8, (ya + ha + yb) / 2 + 5, e['nhan'], lc, bold=True, anchor='end' if trai else 'start')
            continue
        side = phai[i]
        if side:
            gx, x1, x2, kr = x + w + 8 + 7 * kr, xa + wa, xb + wb, kr + 1
        else:
            gx, x1, x2, kl = x - 8 - 7 * kl, xa, xb, kl + 1
        # cạnh ngoài ra thấp hơn, vào cao hơn (vòng lùi) để không cắt cạnh trong; 14 px để hai đầu mũi tên không chạm nhau
        sg = 1 if b < a else -1
        y1 = ya + ha / 2 + sg * 14 * ra_.get((a, side), 0)
        y2 = yb + hb / 2 - sg * 14 * vao_.get((b, side), 0)
        ra_[(a, side)], vao_[(b, side)] = ra_.get((a, side), 0) + 1, vao_.get((b, side), 0) + 1
        s.path(_rut([(x1, y1), (gx, y1), (gx, y2), (x2, y2)]), color, dash)
        for ln in (wrap(e['nhan'], nw, 13, True) if e.get('nhan') else []):
            ny = ya + ha + 19 + 16 * xep.get(a, 0)
            xep[a] = xep.get(a, 0) + 1
            if side:
                s.label(x + w - 4, ny, ln, lc, bold=True, anchor='end')
            else:
                s.label(x + 4, ny, ln, lc, bold=True, anchor='start')
    s.H = y - 32 - 16 * max(0, nl[-1] - 1) + 8 + 16 * nl[-1]


def k_vong_lap(s, sp, mobile):
    st = [dict(b, lan=0, cot=i) for i, b in enumerate(sp['buoc'])]
    k_lan(s, {'buoc': st, 'lan': [''], 'vong': [dict(v, loai=v.get('loai', 'sua')) for v in sp.get('vong', [])]}, mobile)


def k_so_lieu(s, sp, mobile):
    if not sp.get('nguon'):
        sys.exit(f'Ô số liệu "{s.title}" thiếu "nguon". Số liệu phải có nguồn.')
    items, W, gap = sp['so'], s.W, 12
    vals = [(f'{d["truoc"]} → ' if d.get('truoc') not in (None, '') else '') + f'{d["gia_tri"]}{d.get("don_vi", "")}' for d in items]
    if mobile:
        per = 2 if all(text_w(v, 22, True) <= (W - 16 - gap) / 2 - 24 for v in vals) else 1
    else:
        per = sp.get('cot') or (len(items) if len(items) <= 4 else 3)
    y = 8
    for row in grid_rows(len(items), per):
        w = (W - 16 - gap * (per - 1)) / per
        fs = {}
        for i in row:
            f = 22 if mobile else 30
            while f > 16 and text_w(vals[i], f, True) > w - 24:
                f -= 1
            fs[i] = f
        h = max(s.measure(w - 24, [(vals[i], fs[i], True, ''), (items[i]['nhan'], 13.5, False, '')]) + 28 for i in row)
        for j, i in enumerate(row):
            x = 8 + j * (w + gap)
            hi = items[i].get('to', False)
            bid = s.box(x, y, w, h, hi)
            s.text_block(x + 12, y + 10, w - 24, [(vals[i], fs[i], True, '#FFFFFF' if hi else s.p['chinh']),
                                                  (items[i]['nhan'], 13.5, False, '#FFFFFF' if hi else s.p['chu_phu'])], anchor='start', owner=bid)
        y += h + gap
    s.H = s.text_block(8, y - 6, W - 16, [('Nguồn: ' + sp['nguon'], 12, False, s.p['chu_phu'])], anchor='start') + 4


KIND = {'luong': k_luong, 'quyet-dinh': k_quyet_dinh, 'khoi': k_khoi, 'so-sanh': k_so_sanh, 'moc': k_moc, 'cot': k_cot, 'danh-sach': k_danh_sach,
        'lan': k_lan, 'vong-lap': k_vong_lap, 'so-lieu': k_so_lieu}


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
