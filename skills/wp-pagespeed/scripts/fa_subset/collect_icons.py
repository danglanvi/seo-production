#!/usr/bin/env python3
"""Thu danh sách icon Font Awesome mà site thật sự dùng, theo từng kiểu (solid, regular, brands), ra codepoint.

Đọc: file hoặc thư mục HTML, PHP, JS, JSON (dữ liệu Elementor xuất từ DB), CSS tuỳ chỉnh, và CSS của Font Awesome để tra tên icon sang codepoint.
Không gọi mạng, không ghi file mặc định. Dùng cùng build_fa.py (cùng thư mục).

Dùng (chạy python3 không có -I):
  python3 collect_icons.py --css fa-all.min.css PATH [PATH ...] [--out icons.json --apply] [--strict]
  --css FILE     CSS Font Awesome 5, 6 hoặc 7 (all.min.css). Lặp lại được. Dùng để đổi tên icon sang codepoint.
  PATH           file hoặc thư mục cần quét: HTML đã render, theme, dữ liệu Elementor, custom CSS.
  --out FILE --apply   ghi JSON. Không có --apply: in JSON ra stdout, không ghi file.
  --strict       thoát mã 1 nếu có tên icon không tra được trong CSS.
Kiểu icon lấy từ class đi cùng: fas, fa-solid, fa là solid. far, fa-regular là regular. fab, fa-brands là brands. fal, fat, fad (Pro) bị bỏ và báo.
Class như fa-2x, fa-fw, fa-spin không phải icon. File CSS Font Awesome (từ 50 khai báo icon trở lên) bị bỏ qua khi quét, để không gom cả thư viện.
Quy tắc CSS riêng dạng .x:before{font-family:"Font Awesome 5 Free";font-weight:900;content:"\\f058"} cũng được tính: độ đậm 900 là solid, 400 là regular,
họ Brands là brands.
Mã thoát: 0 xong, 1 lỗi dữ liệu hoặc --strict có icon lạ, 2 sai tham số.
"""
import argparse
import json
import os
import re
import sys

STYLE_TOKENS = {'fas': 'solid', 'fa-solid': 'solid', 'fa': 'solid', 'far': 'regular', 'fa-regular': 'regular', 'fab': 'brands', 'fa-brands': 'brands'}
PRO_TOKENS = {'fal', 'fat', 'fad', 'fass', 'fa-light', 'fa-thin', 'fa-duotone', 'fa-sharp'}
NOT_ICON = {'fa-solid', 'fa-regular', 'fa-brands', 'fa-light', 'fa-thin', 'fa-duotone', 'fa-sharp', 'fa-fw', 'fa-lg', 'fa-xs', 'fa-sm', 'fa-spin', 'fa-pulse',
            'fa-border', 'fa-inverse', 'fa-stack', 'fa-stack-1x', 'fa-stack-2x', 'fa-li', 'fa-ul', 'fa-rotate-90', 'fa-rotate-180', 'fa-rotate-270',
            'fa-flip-horizontal', 'fa-flip-vertical', 'fa-flip-both', 'fa-pull-left', 'fa-pull-right', 'fa-beat', 'fa-fade', 'fa-beat-fade', 'fa-bounce',
            'fa-shake', 'fa-spin-pulse', 'fa-spin-reverse', 'fa-swap-opacity', 'fa-rotate-by', 'fa-width-auto', 'fa-fw', 'fa-layers', 'fa-classic', 'fa-chisel'}
SIZE_RE = re.compile(r'^fa-\d+x$')
TEXT_EXT = {'.html', '.htm', '.php', '.js', '.mjs', '.json', '.css', '.txt', '.twig', '.tpl', '.svg', '.xml', '.md'}
SKIP_DIRS = {'.git', 'node_modules', '__pycache__'}
RULE_RE = re.compile(r'([^{}]+)\{([^{}]*)\}')
SEL_RE = re.compile(r'^\s*\.fa-([a-z0-9-]+)(?::{1,2}before)?\s*$')
CP_RE = re.compile(r'(?:content|--fa)\s*:\s*["\']\\([0-9a-fA-F]{1,6})\s*["\']')
RUN_RE = re.compile(r'(?<![\w-])(?:(?:fas|far|fab|fal|fat|fad|fass|fa)|fa-[a-z0-9-]+)(?:\s+(?:(?:fas|far|fab|fal|fat|fad|fass|fa)(?![\w-])|fa-[a-z0-9-]+(?![\w-])))*(?![\w-])')


def die(msg, code=1):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


def parse_css(text):
    """name -> codepoint (hex thường). Trả thêm số khai báo để nhận ra file thư viện."""
    out = {}
    for sel, body in RULE_RE.findall(text):
        m = CP_RE.search(body)
        if not m:
            continue
        cp = '%x' % int(m.group(1), 16)
        for one in sel.split(','):
            s = SEL_RE.match(one)
            if s:
                out[s.group(1)] = cp
    return out


def style_from_rule(body):
    if 'font awesome' not in body.lower() and 'fontawesome' not in body.lower():
        return None
    if re.search(r'brands', body, re.I):
        return 'brands'
    w = re.search(r'font-weight\s*:\s*(\d+|bold|normal)', body, re.I)
    if w and w.group(1).lower() in ('900', 'bold', '800', '700', '600'):
        return 'solid'
    if w:
        return 'regular'
    return 'solid'


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in TEXT_EXT:
                        yield os.path.join(root, f)
        else:
            die('không có đường dẫn: %s' % p)


def main():
    ap = argparse.ArgumentParser(description='Thu icon Font Awesome đang dùng theo kiểu solid, regular, brands.', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('paths', nargs='+', help='file hoặc thư mục cần quét')
    ap.add_argument('--css', action='append', required=True, help='CSS Font Awesome để tra tên icon sang codepoint')
    ap.add_argument('--out', help='ghi JSON vào file này (cần --apply)')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    if a.apply and not a.out:
        die('--apply cần --out', 2)

    names = {}
    css_files = set()
    for c in a.css:
        try:
            with open(c, encoding='utf-8', errors='ignore') as f:
                names.update(parse_css(f.read()))
        except OSError as e:
            die('không đọc được CSS %s: %s' % (c, e))
        css_files.add(os.path.abspath(c))
    if not names:
        die('không tìm thấy khai báo icon nào trong --css (cần dạng .fa-xxx:before{content:"\\fxxx"})')

    styles = {'solid': {}, 'regular': {}, 'brands': {}}
    unknown, pro, skipped_files, scanned = set(), set(), [], 0
    for path in walk(a.paths):
        if os.path.abspath(path) in css_files:
            continue
        try:
            if os.path.getsize(path) > 8 * 1024 * 1024:
                continue
            with open(path, encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except OSError:
            continue
        if path.lower().endswith('.css') and len(parse_css(text)) >= 50:
            skipped_files.append(path)
            continue
        scanned += 1
        for m in RUN_RE.finditer(text):
            toks = m.group(0).split()
            icons = [t for t in toks if t.startswith('fa-') and t not in NOT_ICON and t not in PRO_TOKENS and not SIZE_RE.match(t)]
            if not icons:
                continue
            if any(t in PRO_TOKENS for t in toks):
                pro.update(icons)
                continue
            kinds = {STYLE_TOKENS[t] for t in toks if t in STYLE_TOKENS} or {'solid'}
            if len(kinds) > 1:
                kinds = {STYLE_TOKENS[t] for t in toks if t in ('fas', 'far', 'fab', 'fa-solid', 'fa-regular', 'fa-brands')} or kinds
            for t in icons:
                n = t[3:]
                if n in names:
                    for k in kinds:
                        styles[k][n] = names[n]
                else:
                    unknown.add(t)
        for sel, body in RULE_RE.findall(text):
            kind = style_from_rule(body)
            if not kind:
                continue
            for cp in CP_RE.findall(body):
                styles[kind].setdefault('css:%x' % int(cp, 16), '%x' % int(cp, 16))

    result = {
        'styles': {k: sorted(set(v.values())) for k, v in styles.items()},
        'icons': {k: dict(sorted(v.items())) for k, v in styles.items()},
        'unknown': sorted(unknown),
        'pro_skipped': sorted(pro),
        'scanned_files': scanned,
        'skipped_library_css': skipped_files,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    print('Quét %d file. solid %d, regular %d, brands %d codepoint. Lạ %d, Pro bỏ %d.' % (
        scanned, len(result['styles']['solid']), len(result['styles']['regular']), len(result['styles']['brands']), len(unknown), len(pro)), file=sys.stderr)
    for s in skipped_files:
        print('Bỏ qua CSS thư viện: %s' % s, file=sys.stderr)
    if unknown:
        print('Tên icon không tra được: %s' % ', '.join(sorted(unknown)), file=sys.stderr)
    if a.apply:
        if os.path.exists(a.out):
            die('%s đã có (script không ghi đè). Đổi tên file ra.' % a.out)
        with open(a.out, 'w', encoding='utf-8') as f:
            f.write(text)
        print('Đã ghi %s' % a.out, file=sys.stderr)
    else:
        sys.stdout.write(text)
        print('Dry-run: chưa ghi file. Thêm --out FILE --apply để ghi.', file=sys.stderr)
    if unknown and a.strict:
        sys.exit(1)


if __name__ == '__main__':
    main()
