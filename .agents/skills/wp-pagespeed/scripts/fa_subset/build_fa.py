#!/usr/bin/env python3
"""Cắt font Font Awesome chỉ còn icon site dùng, kèm CSS tách theo unicode-range.

Mỗi kiểu (solid, regular, brands) sinh 2 khai báo @font-face:
  1. bản cắt (vài KB) với unicode-range là các icon đang dùng
  2. bản đầy đủ với unicode-range là mọi codepoint còn lại
Trang chỉ tải bản cắt. Icon mới thêm sau vẫn hiện đúng vì trình duyệt tự tải bản đầy đủ khi gặp codepoint ngoài bản cắt.
Kết quả đã đo ở site mẫu (10/2026): FA 5.15 từ 167 KB còn khoảng 7 KB. Đo lại bằng báo cáo của script này trước khi giữ.

Dùng (cần fontTools và brotli; chạy python3 không có -I). icons.json lấy từ collect_icons.py:
  python3 build_fa.py --icons icons.json --font solid=fa-solid-900.woff2 --font regular=fa-regular-400.woff2 --font brands=fa-brands-400.woff2 \\
      --url-prefix /wp-content/uploads/fonts/ --stamp 20261017 --out-dir ./fa-ra [--apply]
  --font KIỂU=FILE      font đầy đủ (woff2 hoặc ttf). KIỂU là solid, regular hoặc brands. Lặp lại được.
  --full-url KIỂU=URL   URL của font đầy đủ trên site. Mặc định <url-prefix><tên file font>.
  --family-free TÊN     họ cho solid và regular. Mặc định "Font Awesome 5 Free". Dùng "Font Awesome 6 Free" hoặc 7 cho bản đó.
  --family-brands TÊN   họ cho brands. Mặc định "Font Awesome 5 Brands".
  --display GIÁ TRỊ     font-display. Mặc định block, giống CSS gốc của Font Awesome.
  --stamp NHÃN          nhãn trong tên file cắt (fa-solid-<nhãn>-sub.woff2). Đổi tên khi nội dung đổi, vì file font cache 1 năm.
  --out-dir DIR --apply ghi <KIỂU>-<nhãn>-sub.woff2, fa-faces.css, fa-report.json. Không có --apply: chỉ in báo cáo kích thước, không ghi file.
  --strict              thoát mã 1 nếu icon dùng mà font không có glyph (thiếu glyph là lỗi sẵn có của site, mặc định chỉ cảnh báo).
Script không ghi đè file đã có. Upload file cắt lên --url-prefix, giữ nguyên font đầy đủ đang chạy. Gỡ CSS này là về như cũ.
Giữ thông tin giấy phép: bản cắt giữ nguyên bảng name của font gốc (OFL). Ghi giấy phép của Font Awesome vào README của theme.
Mã thoát: 0 xong, 1 lỗi dữ liệu (--strict có glyph thiếu, font hỏng, icons.json hỏng), 2 sai tham số.
"""
import argparse
import io
import json
import os
import sys

try:
    from fontTools import subset
    from fontTools.ttLib import TTFont
except ImportError:
    print('Lỗi: cần fontTools và brotli (pip install fonttools brotli). Chạy python3 không có -I.', file=sys.stderr)
    sys.exit(1)

STYLES = {'solid': 900, 'regular': 400, 'brands': 400}
MAX_CP = 0x10FFFF


def die(msg, code=1):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


def ranges_css(cps):
    """Danh sách codepoint đã sắp xếp -> 'U+F004,U+F006-F008'."""
    out, i = [], 0
    cps = sorted(set(cps))
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        out.append('U+%X' % cps[i] if i == j else 'U+%X-%X' % (cps[i], cps[j]))
        i = j + 1
    return ','.join(out)


def complement_css(cps):
    """Mọi codepoint từ 0 đến 10FFFF trừ cps."""
    out, start = [], 0
    for cp in sorted(set(cps)):
        if cp > start:
            out.append((start, cp - 1))
        start = cp + 1
    if start <= MAX_CP:
        out.append((start, MAX_CP))
    return ','.join('U+%X' % a if a == b else 'U+%X-%X' % (a, b) for a, b in out)


def cut(path, cps):
    """Cắt font về các codepoint trong cps. Trả (bytes woff2, codepoint có trong font)."""
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = []
    opts.hinting = False
    opts.name_IDs = ['*']
    opts.notdef_outline = True
    try:
        font = subset.load_font(path, opts)
    except Exception as e:  # noqa: BLE001
        die('không đọc được font %s: %s' % (path, e))
    have = set(font.getBestCmap())
    keep = sorted(cp for cp in cps if cp in have)
    s = subset.Subsetter(opts)
    s.populate(unicodes=keep)
    s.subset(font)
    buf = io.BytesIO()
    font.flavor = 'woff2'
    font.save(buf)
    return buf.getvalue(), keep


def face(family, weight, display, url, rng):
    return ("@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:%s;src:url(%s) format('woff2');%s}"
            % (family, weight, display, url, ('unicode-range:' + rng) if rng else '')).replace(';}', '}')


def parse_pairs(items, flag):
    out = {}
    for it in items:
        k, sep, v = it.partition('=')
        if not sep or k not in STYLES or not v:
            die('%s phải có dạng KIỂU=giá trị với KIỂU là solid, regular hoặc brands: %r' % (flag, it), 2)
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description='Cắt Font Awesome theo icon đang dùng và sinh CSS unicode-range.', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('--icons', required=True, help='JSON từ collect_icons.py')
    ap.add_argument('--font', action='append', default=[], help='KIỂU=FILE font đầy đủ')
    ap.add_argument('--full-url', action='append', default=[], help='KIỂU=URL font đầy đủ trên site')
    ap.add_argument('--url-prefix', default='/')
    ap.add_argument('--family-free', default='Font Awesome 5 Free')
    ap.add_argument('--family-brands', default='Font Awesome 5 Brands')
    ap.add_argument('--display', default='block')
    ap.add_argument('--stamp', required=True)
    ap.add_argument('--out-dir')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    if not a.font:
        die('thiếu --font', 2)
    if a.apply and not a.out_dir:
        die('--apply cần --out-dir', 2)
    if not a.stamp.replace('-', '').replace('_', '').isalnum():
        die('--stamp chỉ gồm chữ, số, gạch', 2)
    fonts, full_urls = parse_pairs(a.font, '--font'), parse_pairs(a.full_url, '--full-url')
    try:
        with open(a.icons, encoding='utf-8') as f:
            used = json.load(f)['styles']
    except (OSError, ValueError, KeyError) as e:
        die('không đọc được --icons (%s): %s' % (a.icons, e))
    prefix = a.url_prefix if a.url_prefix.endswith('/') else a.url_prefix + '/'

    css, files, report, missing_any = [], {}, {}, False
    for style in ('solid', 'regular', 'brands'):
        if style not in fonts:
            continue
        path = fonts[style]
        if not os.path.exists(path):
            die('không có font %s: %s' % (style, path))
        family = a.family_brands if style == 'brands' else a.family_free
        weight = STYLES[style]
        want = sorted({int(x, 16) for x in used.get(style, [])})
        full_url = full_urls.get(style) or prefix + os.path.basename(path)
        full_size = os.path.getsize(path)
        if not want:
            css.append(face(family, weight, a.display, full_url, ''))
            report[style] = {'icons': 0, 'full_bytes': full_size, 'sub_bytes': None, 'note': 'không có icon dùng, giữ bản đầy đủ'}
            continue
        data, keep = cut(path, want)
        miss = [cp for cp in want if cp not in keep]
        missing_any = missing_any or bool(miss)
        name = 'fa-%s-%s-sub.woff2' % (style, a.stamp)
        files[name] = data
        css.append(face(family, weight, a.display, prefix + name, ranges_css(keep)))
        css.append(face(family, weight, a.display, full_url, complement_css(keep)))
        report[style] = {'icons': len(keep), 'full_bytes': full_size, 'sub_bytes': len(data), 'file': name,
                         'saved_percent': round(100.0 * (1 - len(data) / full_size), 1), 'missing_glyph': ['%x' % cp for cp in miss]}
        print('%-8s %3d icon: %d B còn %d B (giảm %.1f%%)%s' % (style, len(keep), full_size, len(data), report[style]['saved_percent'],
                                                              ('. Font không có glyph: ' + ', '.join('U+%X' % cp for cp in miss)) if miss else ''), file=sys.stderr)
    if not report:
        die('không có kiểu nào để xử lý', 2)
    text = '\n'.join(css) + '\n'
    if a.apply:
        os.makedirs(a.out_dir, exist_ok=True)
        targets = [os.path.join(a.out_dir, n) for n in list(files) + ['fa-faces.css', 'fa-report.json']]
        for t in targets:
            if os.path.exists(t):
                die('%s đã có (script không ghi đè). Đổi --stamp hoặc --out-dir.' % t)
        for n, data in files.items():
            with open(os.path.join(a.out_dir, n), 'wb') as f:
                f.write(data)
        with open(os.path.join(a.out_dir, 'fa-faces.css'), 'w', encoding='utf-8') as f:
            f.write(text)
        with open(os.path.join(a.out_dir, 'fa-report.json'), 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print('Đã ghi %d file vào %s' % (len(targets), a.out_dir), file=sys.stderr)
    else:
        sys.stdout.write(text)
        print('Dry-run: chưa ghi file. Thêm --out-dir DIR --apply để ghi bản cắt, fa-faces.css, fa-report.json.', file=sys.stderr)
    if missing_any and a.strict:
        sys.exit(1)


if __name__ == '__main__':
    main()
