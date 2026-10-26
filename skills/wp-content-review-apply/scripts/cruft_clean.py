#!/usr/bin/env python3
"""Làm sạch HTML thừa trong bài, meta ACF và widget: dán từ Google Docs, Google Translate, TinyMCE, Elementor.
Luật tất định. Ca mơ hồ (&nbsp; cạnh chữ số hoặc giữa hai chữ, style còn lại sau khi lọc) lấy quyết định từ file Jev.
Chỉ đọc file export và ghi file kết quả local. Không chạm DB.

python3 -I cruft_clean.py <export.json> <thư mục ra> [--emit-jev] [--jev-nbsp nbsp_out.jsonl] [--jev-style style_out.jsonl] [--force]

export.json do export_cruft.php sinh: {"posts": [{id, type, slug, content, el, md5c, md5e}],
  "meta": [{meta_id, post_id, key, value, md5}], "options": [{key, value, md5}]}. Dạng cũ (list bài) vẫn đọc được.
--emit-jev ghi các ca mơ hồ ra jev_nbsp_in.jsonl, jev_style_in.jsonl và style_index.json trong thư mục ra, để chạy Jev trước.
Chạy lại với --jev-nbsp và --jev-style (file kết quả Jev) để áp quyết định.
Bất biến. Mỗi mục phải đạt cả ba. Mục không đạt vào rejected.json và không vào changes.json:
  1. chữ hiển thị không đổi (bỏ thẻ inline, entity, BOM, NBSP, khoảng trắng);
  2. bộ khung thẻ khối không đổi (bỏ span, p, strong, b, em, i, br);
  3. cấu trúc sau wpautop không đổi, tính bằng bản port wpautop trong file này.
Bất biến 3 chỉ là kiểm sơ bộ. Cổng thật là compare_autop.php chạy trên site bằng wpautop của WordPress: phải 0 khác biệt.
Ra: changes.json (kèm md5 bản gốc để apply_cruft.php kiểm), rejected.json, thống kê trên stdout.
Mã thoát: 0 mọi mục đạt bất biến, 1 có mục bị loại (xem rejected.json), 2 sai đầu vào hoặc file ra đã có (thêm --force).
"""
import argparse
import collections
import html
import json
import os
import re
import sys

# ---------- wpautop (port) và chữ ký cấu trúc ----------

AB = (r'(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|form|map|area|blockquote|address|math|style|p|'
      r'h[1-6]|hr|fieldset|legend|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary)')
LB, RB = '⟨', '⟩'


def _sub(p, r, s, f=0):
    return re.sub(p, r, s, flags=f | re.A)


def wpautop(text, br=True):
    """Bản port wpautop của WordPress, bỏ phần xử lý pre. Dùng để kiểm sơ bộ, không thay compare_autop.php."""
    if not text.strip():
        return ''
    text += '\n'
    text = _sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n', text)
    text = _sub(r'(<' + AB + r'[\s/>])', r'\n\n\1', text)
    text = _sub(r'(</' + AB + r'>)', r'\1\n\n', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = _sub(r'\n\n+', '\n\n', text)
    parts = [t for t in re.split(r'\n\s*\n', text, flags=re.A) if t != '']
    text = ''.join('<p>' + t.strip('\n') + '</p>\n' for t in parts)
    text = _sub(r'<p>\s*</p>', '', text)
    text = _sub(r'<p>([^<]+)</(div|address|form)>', r'<p>\1</p></\2>', text)
    text = _sub(r'<p>\s*(</?' + AB + r'[^>]*>)\s*</p>', r'\1', text)
    text = _sub(r'<p>(<li.+?)</p>', r'\1', text)
    text = _sub(r'<p><blockquote([^>]*)>', r'<blockquote\1><p>', text, re.I)
    text = text.replace('</blockquote></p>', '</p></blockquote>')
    text = _sub(r'<p>\s*(</?' + AB + r'[^>]*>)', r'\1', text)
    text = _sub(r'(</?' + AB + r'[^>]*>)\s*</p>', r'\1', text)
    if br:
        text = re.sub(r'<(script|style|svg|math).*?</\1>', lambda m: m.group(0).replace('\n', '<WPPreserveNewline />'), text, flags=re.S)
        text = text.replace('<br>', '<br />').replace('<br/>', '<br />')
        text = _sub(r'(?<!<br />)\s*\n', '<br />\n', text)
        text = text.replace('<WPPreserveNewline />', '\n')
    text = _sub(r'(</?' + AB + r'[^>]*>)\s*<br />', r'\1', text)
    text = _sub(r'<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)', r'\1', text)
    text = _sub(r'\n</p>$', '</p>', text)
    return text


def struct_sig(h, autop):
    """Chữ ký cấu trúc hiển thị: đoạn, xuống dòng, khối. Cùng thuật toán với wps_cruft_struct trong compare_autop.php."""
    if autop:
        h = wpautop(h)
    h = h.replace('&nbsp;', ' ').replace('\xa0', ' ').replace('﻿', ' ')
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    h = re.sub(r'</?(span|strong|b|em|i|a|u|sup|sub|small|mark|code|font)\b[^>]*>', '', h, flags=re.I)
    h = re.sub(r'<(/?)(p|br|li|ul|ol|h[1-6]|td|th|tr|table|div|figure|blockquote|iframe|img)\b[^>]*>', LB + r'\1\2' + RB, h, flags=re.I)
    h = re.sub(r'<[^>]+>', '', h)
    h = re.sub(r'\s+', ' ', h)
    h = re.sub(r'\s*(' + LB + r'[^' + RB + r']*' + RB + r')\s*', r'\1', h)
    while True:
        h0 = h
        for t in (LB + 'p' + RB + LB + '/p' + RB, LB + 'div' + RB + LB + '/div' + RB, LB + 'p' + RB + LB + 'br' + RB + LB + '/p' + RB):
            h = h.replace(t, '')
        h = re.sub(LB + 'br' + RB + '(' + LB + r'/(?:p|li|td|th|h[1-6])' + RB + ')', r'\1', h)
        if h == h0:
            break
    return h.strip()


# ---------- luật làm sạch ----------

# Khai báo style là rác dán: bỏ hẳn.
RESIDUE = [
    r'font-weight:\s*(?:400|normal)(?:\s*!msorm)?', r'vertical-align:\s*(?:inherit|baseline)',
    r'background-color:\s*transparent', r'font-variant[a-z-]*:\s*normal', r'font-style:\s*normal',
    r'white-space:\s*pre-wrap', r'box-sizing:\s*inherit', r'font-family:[^;]*', r'[a-z-]+:\s*var\(\s*--e-global-[^)]*\)[^;]*',
    r'text-align:\s*var\(--text-align\)', r'text-decoration:\s*none', r'color:\s*(?:#000000|#000|rgb\(0,\s*0,\s*0\)|black)',
    r'font-size:\s*(?:11|12)pt', r'list-style-type:\s*(?:disc|decimal)', r'letter-spacing:\s*normal',
]
RES = re.compile(r'^(?:' + '|'.join(RESIDUE) + r')$', re.I)
STYLED = ('span', 'li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'strong', 'em', 'i', 'ol', 'ul')
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)\b([^<>]*?)(/?)>', re.S)


def norm_decl(s):
    return [re.sub(r'\s+', ' ', d.strip()) for d in s.split(';') if d.strip()]


def strip_style(decls, style_jev):
    keep = [d for d in decls if not RES.match(d)]
    if keep and style_jev is not None:
        if style_jev.get('; '.join(keep).lower()) == 'paste_residue':
            keep = []
    return keep


def clean_html(h, style_jev=None, nbsp_jev=None, pid='', amb=None, stats=None, autop=False):
    if not h or '<' not in h and '&nbsp;' not in h and '\xa0' not in h:
        return h
    st = stats if stats is not None else collections.Counter()
    # 1. Bookmark TinyMCE lưu nhầm (span rộng 0 chứa BOM) và ký tự BOM lạc
    h, n = re.subn(r'<span data-mce-type="bookmark"[^>]*>﻿*</span>', '', h); st['mce_bookmark'] += n
    h, n = re.subn('﻿', '', h); st['bom'] += n
    # Span chỉ chứa xuống dòng: wpautop đổi mỗi xuống dòng thành một <br>. Gỡ span làm hai xuống dòng dính nhau,
    # wpautop đổi thành ngắt đoạn và bố cục trang lệch (ca 19/10: seo-global-la-gi đổi bố cục từ y≈4876).
    # Giữ span (bỏ style) để mỗi xuống dòng vẫn tách nhau như bản gốc.
    if autop:
        h, n = re.subn(r'<span\b[^>]*>([ \t]*(?:\r?\n[ \t]*)+)</span>', lambda m: '\x01' + m.group(1) + '\x02', h); st['nl_span_kept'] += n
    h, n = re.subn(r'\s+aria-level="\d+"', '', h); st['aria_level'] += n
    h, n = re.subn(r'\s+data-sheets-[a-z-]+=(?:"[^"]*"|\'[^\']*\')', '', h); st['data_sheets'] += n
    h, n = re.subn(r'\s+dir="ltr"', '', h); st['dir_ltr'] += n
    # 2. style: lọc khai báo rác; span không còn thuộc tính thì gỡ (giữ chữ bên trong)
    out, stack, pos = [], [], 0
    for m in TAG.finditer(h):
        out.append(h[pos:m.start()]); pos = m.end()
        close, name, attrs, selfc = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        tag = m.group(0)
        if name == 'span' and not close and not selfc:
            sm = re.search(r'\sstyle="([^"]*)"', attrs)
            unwrap = False
            if sm:
                keep = strip_style(norm_decl(sm.group(1)), style_jev)
                if len(keep) != len(norm_decl(sm.group(1))):
                    st['style_decl_removed'] += len(norm_decl(sm.group(1))) - len(keep)
                if keep and amb is not None:
                    amb['style'].add('; '.join(keep).lower())
                rest = attrs.replace(sm.group(0), (' style="' + '; '.join(keep) + ';"') if keep else '')
                if not keep and not rest.strip():
                    unwrap = True
                else:
                    tag = '<span' + rest + '>'
            elif not attrs.strip():
                unwrap = True
            stack.append(unwrap)
            if unwrap:
                st['span_unwrapped'] += 1
                continue
        elif name == 'span' and close:
            if stack and stack.pop():
                continue
        elif name in STYLED and not close:
            sm = re.search(r'\sstyle="([^"]*)"', attrs)
            if sm:
                keep = strip_style(norm_decl(sm.group(1)), style_jev)
                if keep and amb is not None:
                    amb['style'].add('; '.join(keep).lower())
                if len(keep) != len(norm_decl(sm.group(1))):
                    st['style_decl_removed'] += len(norm_decl(sm.group(1))) - len(keep)
                    tag = '<' + m.group(2) + attrs.replace(sm.group(0), (' style="' + '; '.join(keep) + ';"') if keep else '') + selfc + '>'
        out.append(tag)
    out.append(h[pos:]); h = ''.join(out)
    # 3. Thẻ inline rỗng không thuộc tính, đoạn văn rỗng
    for _ in range(3):
        h, n = re.subn(r'<(strong|b|em|i|span)>(\s*)</\1>', lambda m: ' ' if m.group(2) else '', h); st['empty_inline'] += n
    h, n = re.subn(r'<p>(?:\s|&nbsp;|\xa0|<br\s*/?>)*</p>\s*', '', h); st['p_empty'] += n

    # 4. &nbsp;
    h2 = h

    def nb(m):
        a = h2[m.start() - 1] if m.start() else ''
        b = h2[m.end()] if m.end() < len(h2) else ''
        if a == '>' and b == '<':
            st['nbsp_kept_sole'] += 1  # &nbsp; là toàn bộ nội dung một phần tử (ô bảng rỗng): giữ
            return m.group(0)
        if autop:
            pre = list(re.finditer(r'\n|<br\b[^>]*>|<p\b[^>]*>|</(?:p|ol|ul|li|h[1-6]|div|table|figure|blockquote)>', h2[max(0, m.start() - 400):m.start()]))
            ls = (max(0, m.start() - 400) + pre[-1].end()) if pre else 0
            nx = re.search(r'\n|<br\b|</p>|<(?:p|ol|ul|h[1-6]|div|table|figure|img|blockquote)\b', h2[m.end():m.end() + 400])
            le = m.end() + nx.start() if nx else len(h2)
            line = re.sub(r'<[^>]*>', '', h2[ls:m.start()] + h2[m.end():le]).replace('&nbsp;', '').replace('\xa0', '')
            if not line.strip():
                st['nbsp_kept_line'] += 1  # dòng chỉ có &nbsp;: khoảng trống đệm, giữ
                return m.group(0)
        if not a or not b or a in ' \t\r\n>;' or b in ' \t\r\n<&\xa0':
            st['nbsp_to_space'] += 1  # cạnh khoảng trắng, thẻ hoặc &nbsp; khác: dấu cách thường
            return ' '
        key = '%s:%d' % (pid, m.start())
        if nbsp_jev is not None and key in nbsp_jev:
            if nbsp_jev[key] == 'plain_space':
                st['nbsp_to_space_jev'] += 1
                return ' '
            st['nbsp_kept_jev'] += 1
            return m.group(0)
        if amb is not None:
            ctx = h2[max(0, m.start() - 80):m.start()] + '⟦NBSP⟧' + h2[m.end():m.end() + 80]
            amb['nbsp'].append({'id': key, 'snippet': html.unescape(re.sub(r'<[^>]+>', '', ctx)).replace('\xa0', ' ')})
        st['nbsp_kept_unknown'] += 1
        return m.group(0)
    h = re.sub(r'&nbsp;|\xa0', nb, h2)
    h = re.sub(r'(?<=[^\s>]) {2,}(?=[^\s<])', ' ', h)  # gộp khoảng trắng đôi sinh ra trong chữ, không đụng xuống dòng
    return h.replace('\x01', '<span>').replace('\x02', '</span>')


INLINE = r'</?(?:span|strong|b|em|i|a|u|sup|sub|small|mark|code|font)\b[^>]*>'


def visible(h):
    t = re.sub(INLINE, '', h or '', flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t).replace('\xa0', ' ').replace('﻿', '')
    return re.sub(r'\s+', ' ', t).strip()


def skeleton(h):
    return collections.Counter(m.group(1).lower() for m in re.finditer(r'<([a-zA-Z][a-zA-Z0-9]*)', h or '')
                               if m.group(1).lower() not in ('span', 'p', 'strong', 'b', 'em', 'i', 'br'))


def walk_el(x, f, key=''):
    if isinstance(x, dict):
        return {k: walk_el(v, f, k) for k, v in x.items()}
    if isinstance(x, list):
        return [walk_el(v, f, key) for v in x]
    if isinstance(x, str) and ('<' in x or '&nbsp;' in x or '\xa0' in x):
        return f(x, key)
    return x


def check_pair(old, new, autop):
    """Trả danh sách bất biến bị phá: 'chu', 'khung', 'cau_truc'."""
    bad = []
    if visible(new) != visible(old):
        bad.append('chu')
    if skeleton(new) != skeleton(old):
        bad.append('khung')
    if struct_sig(new, autop) != struct_sig(old, autop):
        bad.append('cau_truc')
    return bad


def check_value(old, new, key=''):
    """So từng chuỗi HTML đã đổi trong giá trị lồng nhau (Elementor, option). Trả tập bất biến bị phá."""
    bad = set()
    if isinstance(old, dict) and isinstance(new, dict):
        for k in old:
            if k in new:
                bad |= check_value(old[k], new[k], k)
    elif isinstance(old, list) and isinstance(new, list):
        for a, b in zip(old, new):
            bad |= check_value(a, b, key)
    elif isinstance(old, str) and isinstance(new, str) and old != new:
        bad |= set(check_pair(old, new, True))
    return bad


def load_jev(p, kq):
    if not p:
        return None
    r = {}
    for l in open(p, encoding='utf-8'):
        if not l.strip():
            continue
        o = json.loads(l)
        r[o['id']] = ((o.get('answers') or {}).get(kq) or {}).get('choice') or o.get(kq)
    return r


def clean_post(r, style_jev, nbsp_jev, amb):
    st = collections.Counter()
    pid = str(r['id'])
    content = r.get('content') or ''
    classic = '<!-- wp:' not in content
    nc = clean_html(content, style_jev, nbsp_jev, pid + 'c', amb, st, autop=classic)
    ne, bad = None, set()
    if nc != content:
        bad |= set(check_pair(content, nc, classic))
    if r.get('el'):
        el = json.loads(r['el'])
        cnt = [0]

        def f(s, key):
            cnt[0] += 1
            return clean_html(s, style_jev, nbsp_jev, '%se%d' % (pid, cnt[0]), amb, st, autop=(key == 'editor'))
        new_el = walk_el(el, f)
        if new_el != el:
            ne = json.dumps(new_el, ensure_ascii=False, separators=(',', ':'))
            bad |= check_value(el, new_el)
    if nc == content and ne is None:
        return None, st, bad
    ch = {'kind': 'post', 'id': r['id'], 'type': r.get('type'), 'slug': r.get('slug'), 'content': nc if nc != content else None, 'el': ne,
          'md5c': r.get('md5c'), 'md5e': r.get('md5e'),
          'bytes_before': len(content.encode()) + len((r.get('el') or '').encode()),
          'bytes_after': len(nc.encode()) + len((ne or r.get('el') or '').encode()), 'stats': dict(st)}
    return ch, st, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description='Làm sạch HTML thừa. Xem docstring đầu file.')
    ap.add_argument('export')
    ap.add_argument('out')
    ap.add_argument('--emit-jev', action='store_true')
    ap.add_argument('--jev-nbsp')
    ap.add_argument('--jev-style')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args(argv)
    if not os.path.isfile(a.export):
        print('Không có file export: ' + a.export, file=sys.stderr)
        return 2
    for fn in ('changes.json', 'rejected.json'):
        if os.path.exists(os.path.join(a.out, fn)) and not a.force:
            print('File ra đã có: %s (thêm --force để ghi đè)' % os.path.join(a.out, fn), file=sys.stderr)
            return 2
    try:
        with open(a.export, encoding='utf-8') as fh:
            data = json.load(fh)
        nbsp_jev = load_jev(a.jev_nbsp, 'intent')
        style_raw = load_jev(a.jev_style, 'kind')
        style_jev = None
        if style_raw is not None:
            with open(os.path.join(a.out, 'style_index.json'), encoding='utf-8') as fh:
                idx = json.load(fh)
            style_jev = {idx[k]: v for k, v in style_raw.items() if k in idx}
    except (OSError, ValueError, KeyError) as e:
        print('Không đọc được đầu vào: %s' % e, file=sys.stderr)
        return 2
    if isinstance(data, list):
        data = {'posts': data}
    os.makedirs(a.out, exist_ok=True)
    amb = {'nbsp': [], 'style': set()} if a.emit_jev else None
    total, changes, rejected = collections.Counter(), [], []

    def take(ch, bad, label):
        if ch is None:
            return
        if bad:
            rejected.append({'kind': ch['kind'], 'id': ch.get('id', ch.get('meta_id', ch.get('key'))), 'slug': ch.get('slug'), 'vi_pham': sorted(bad), 'mo_ta': label})
        else:
            changes.append(ch)

    for r in data.get('posts') or []:
        ch, st, bad = clean_post(r, style_jev, nbsp_jev, amb)
        total += st
        take(ch, bad, 'bài %s' % r.get('slug'))
    for r in data.get('meta') or []:
        st = collections.Counter()
        new = clean_html(r['value'], style_jev, nbsp_jev, 'm%s' % r['meta_id'], amb, st, autop=True)
        total += st
        if new != r['value']:
            take({'kind': 'meta', 'meta_id': r['meta_id'], 'post_id': r.get('post_id'), 'key': r.get('key'), 'new': new, 'md5': r.get('md5'),
                  'bytes_before': len(r['value'].encode()), 'bytes_after': len(new.encode()), 'stats': dict(st)},
                 set(check_pair(r['value'], new, True)), 'meta %s' % r.get('key'))
    for r in data.get('options') or []:
        cnt = [0]
        st = collections.Counter()

        def f(s, key):
            cnt[0] += 1
            return clean_html(s, style_jev, nbsp_jev, 'o%s%d' % (r['key'], cnt[0]), amb, st, autop=True)
        new = walk_el(r['value'], f)
        total += st
        if new != r['value']:
            take({'kind': 'option', 'key': r['key'], 'new': new, 'md5': r.get('md5'), 'stats': dict(st),
                  'bytes_before': len(json.dumps(r['value'], ensure_ascii=False)), 'bytes_after': len(json.dumps(new, ensure_ascii=False))},
                 check_value(r['value'], new), 'option %s' % r['key'])
    if a.emit_jev:
        with open(os.path.join(a.out, 'jev_nbsp_in.jsonl'), 'w', encoding='utf-8') as fo:
            for x in amb['nbsp']:
                fo.write(json.dumps({'id': x['id'], 'state': {'snippet': x['snippet']}}, ensure_ascii=False) + '\n')
        idx = {}
        with open(os.path.join(a.out, 'jev_style_in.jsonl'), 'w', encoding='utf-8') as fo:
            for i, s in enumerate(sorted(amb['style'])):
                k = 's%d' % i
                idx[k] = s
                fo.write(json.dumps({'id': k, 'state': {'inline_style': s}}, ensure_ascii=False) + '\n')
        with open(os.path.join(a.out, 'style_index.json'), 'w', encoding='utf-8') as fo:
            json.dump(idx, fo, ensure_ascii=False, indent=0)
        print('mơ hồ: nbsp %d, style %d' % (len(amb['nbsp']), len(amb['style'])))
    with open(os.path.join(a.out, 'changes.json'), 'w', encoding='utf-8') as fo:
        json.dump(changes, fo, ensure_ascii=False)
    with open(os.path.join(a.out, 'rejected.json'), 'w', encoding='utf-8') as fo:
        json.dump(rejected, fo, ensure_ascii=False, indent=1)
    print('đổi %d mục, loại %d mục (phá bất biến)' % (len(changes), len(rejected)))
    print(json.dumps(dict(total), ensure_ascii=False))
    print('byte %d -> %d' % (sum(c['bytes_before'] for c in changes), sum(c['bytes_after'] for c in changes)))
    for x in rejected[:20]:
        print('LOẠI %s %s: %s' % (x['kind'], x['id'], ','.join(x['vi_pham'])), file=sys.stderr)
    return 1 if rejected else 0


if __name__ == '__main__':
    sys.exit(main())
