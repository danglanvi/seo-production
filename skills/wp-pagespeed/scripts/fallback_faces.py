#!/usr/bin/env python3
"""Sinh @font-face font dự phòng đã chỉnh số đo cho một họ font web, để chữ không nhảy dòng khi font thật về (CLS do font).

Với mỗi dải độ đậm, script đo bề rộng một mẫu chữ Việt thật bằng font web và bằng font dự phòng (Arial hoặc Liberation Sans), rồi in:
  @font-face{font-family:'<Họ> Fallback';font-weight:<dải>;src:local(...);size-adjust:..%;ascent-override:..%;descent-override:..%;line-gap-override:0%}
size-adjust = bề rộng font web / bề rộng font dự phòng, tính riêng từng độ đậm. Một face cho cả dải 650-900 làm H1 độ đậm 800 xuống dòng khác
khi font thật về (CLS trên máy Linux của PSI, đo 18/10/2026). Ascent và descent lấy từ hhea của font web ở độ đậm 400, chia cho size-adjust.
Chỉ đo ký tự có trong cả font web lẫn font dự phòng, để hai tổng bề rộng cùng một tập ký tự.

Dùng (cần fontTools và brotli; chạy không có -I vì -I bỏ thư mục site-packages của người dùng):
  python3 fallback_faces.py --family "Tên Họ" --web "latin.woff2,vi.woff2@400" --web "latin-700.woff2,vi-700.woff2@700" [--sample trang.txt]
  python3 fallback_faces.py --family "Tên Họ" --web "bien-thien-latin.woff2,bien-thien-vi.woff2"          (font biến thiên, không có @độ đậm)
  --web FILE[,FILE...][@ĐỘ ĐẬM]  các file subset của cùng một độ đậm (latin, vi...). Font biến thiên: bỏ @ĐỘ ĐẬM, script khoá wght theo từng dải.
  --family TÊN                   họ font web. Face dự phòng tên "<TÊN> Fallback".
  --sample FILE                  văn bản UTF-8 lấy từ trang thật (H1, đoạn đầu, menu). Mặc định dùng mẫu có sẵn, kém sát hơn.
  --fallback-regular/-bold FILE  font dự phòng để đo. Mặc định tìm Arial (macOS) hoặc Liberation Sans (Linux).
  --local-regular/-bold LIST     tên local() ngăn cách bằng dấu phẩy. Mặc định Arial và Liberation Sans.
  --ranges "lo-hi:đậm đo:r|b,..." dải độ đậm, độ đậm dùng để đo, r là font thường, b là font đậm. Mặc định 6 dải 100-900.
  --out-dir DIR --apply          ghi <họ>-fallback.css và localtest.html vào DIR. Không có --apply: in CSS ra stdout, không ghi file.
localtest.html khai từng local() thành một face riêng. Mở trang trên máy cần kiểm, mỗi tên báo ĐÃ KHỚP hoặc KHÔNG KHỚP (biến window.__LT).
Máy PSI chạy Linux: tên local() khớp ở máy này chưa chắc khớp ở đó. Kiểm trên PSI bằng psi_ab.py trước khi giữ (do-dac.md mục 3).
Ghi chú kết quả: A/B 18/10/2026 trên PSI (5 trang x 3 lượt x 2 thiết bị) cho thấy face dự phòng chỉnh số đo không giảm CLS ở một site mẫu
(0,086 sang 0,086; 0,08 sang 0,081), vì Lantern làm tròn bề rộng chữ. Đo CLS trước và sau, giữ khi thật sự giảm.
Mã thoát: 0 xong, 1 lỗi dữ liệu (thiếu thư viện, không đọc được font, không có ký tự chung), 2 sai tham số.
"""
import argparse
import html
import os
import re
import sys

try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
except ImportError:
    print('Lỗi: cần fontTools và brotli (pip install fonttools brotli). Chạy python3 không có -I.', file=sys.stderr)
    sys.exit(1)

DEFAULT_RANGES = '100-449:400:r,450-549:500:r,550-649:600:b,650-749:700:b,750-849:800:b,850-900:900:b'
LOCAL_R = 'Arial,ArialMT,Liberation Sans,LiberationSans'
LOCAL_B = 'Arial Bold,Arial-BoldMT,Liberation Sans Bold,LiberationSans-Bold'
FB_CANDIDATES = {
    'r': ['/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
          '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'],
    'b': ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
          '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf'],
}
SAMPLE = ('Chúng tôi xây dựng website nhanh hơn, dễ tìm thấy hơn trên Google. Cách đo tốc độ tải trang bằng dữ liệu thật của người dùng. '
          'Tối ưu hình ảnh, phông chữ và mã nguồn để trang hiển thị ổn định, không bị nhảy dòng. Đăng ký tư vấn miễn phí, '
          'khách hàng nhận báo cáo chi tiết mỗi tháng. Quyền riêng tư, điều khoản sử dụng, liên hệ, đường dẫn, thư viện, thương hiệu. '
          'Ấn tượng, nguyễn, trường học, được, ớ, ữ, ỷ, ẵ, ặ, Ế, Ộ, Ừ, Ỵ, Đ, ơ, ư. 0123456789 %&@#')
SAFE_NAME = re.compile(r'^[\w .\-]+$')


def fail(msg, code=1):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


def parse_ranges(s):
    out = []
    for part in s.split(','):
        m = re.fullmatch(r'\s*(\d+)-(\d+):(\d+):([rb])\s*', part)
        if not m:
            fail('--ranges sai ở "%s" (dạng lo-hi:đậm đo:r|b)' % part, 2)
        lo, hi, w, k = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        if lo > hi or not 1 <= w <= 1000:
            fail('--ranges sai ở "%s"' % part, 2)
        out.append((lo, hi, w, k))
    return out


def parse_names(s, flag):
    names = [x.strip() for x in s.split(',') if x.strip()]
    for n in names:
        if not SAFE_NAME.match(n):
            fail('%s có tên không hợp lệ: %r (chỉ chữ, số, dấu cách, dấu chấm, gạch)' % (flag, n), 2)
    return names


def load(path):
    try:
        return TTFont(path)
    except Exception as e:  # noqa: BLE001 - fontTools ném nhiều loại lỗi
        fail('không đọc được font %s: %s' % (path, e))


class Web:
    """Font web gồm nhiều file subset ở mỗi độ đậm. pins: {độ đậm: [file]}; var: [file] của font biến thiên."""

    def __init__(self, specs):
        self.pins, self.var = {}, []
        for spec in specs:
            files, _, w = spec.partition('@')
            files = [f.strip() for f in files.split(',') if f.strip()]
            if not files:
                fail('--web rỗng', 2)
            for f in files:
                if not os.path.exists(f):
                    fail('không có file font: %s' % f)
            if w:
                if not w.strip().isdigit():
                    fail('@độ đậm phải là số: %s' % spec, 2)
                self.pins[int(w)] = files
            else:
                probe = load(files[0])
                if 'fvar' not in probe or 'wght' not in [a.axisTag for a in probe['fvar'].axes]:
                    fail('%s là font tĩnh, thêm @ĐỘ ĐẬM (ví dụ @400)' % files[0], 2)
                self.var = files

    def at(self, w):
        if w in self.pins:
            return [load(f) for f in self.pins[w]]
        if self.var:
            out = []
            for f in self.var:
                font = load(f)
                ax = [a for a in font['fvar'].axes if a.axisTag == 'wght'][0]
                out.append(instancer.instantiateVariableFont(font, {'wght': min(max(w, ax.minValue), ax.maxValue)}))
            return out
        near = min(self.pins, key=lambda p: abs(p - w))
        print('Cảnh báo: không có font độ đậm %d, dùng độ đậm %d cho dải này' % (w, near), file=sys.stderr)
        return [load(f) for f in self.pins[near]]


def adv_map(fonts, chars):
    """codepoint -> bề rộng (đơn vị em). Font đầu tiên có ký tự thì thắng."""
    out = {}
    for ch in chars:
        for f in fonts:
            g = f.getBestCmap().get(ord(ch))
            if g:
                out[ch] = f['hmtx'][g][0] / f['head'].unitsPerEm
                break
    return out


def find_fallback(kind, given):
    if given:
        if not os.path.exists(given):
            fail('không có font dự phòng: %s' % given)
        return given
    for c in FB_CANDIDATES[kind]:
        if os.path.exists(c):
            return c
    fail('không tìm thấy Arial hay Liberation Sans, truyền --fallback-%s FILE' % ('regular' if kind == 'r' else 'bold'))


def measure(web_fonts, fb_font, chars):
    wa, fa = adv_map(web_fonts, chars), adv_map([fb_font], chars)
    common = [c for c in chars if c in wa and c in fa]
    if not common:
        fail('mẫu chữ không có ký tự nào chung giữa font web và font dự phòng')
    return sum(wa[c] for c in common) / sum(fa[c] for c in common), len(common)


def face(fam, lo, hi, src, sa, asc, desc):
    return ("@font-face{font-family:'%s';font-weight:%d %d;src:%s;size-adjust:%.2f%%;ascent-override:%.2f%%;descent-override:%.2f%%;line-gap-override:0%%}"
            % (fam, lo, hi, src, sa * 100, asc / sa * 100, desc / sa * 100))


def localtest(names, family):
    faces = ''.join("@font-face{font-family:'lt%d';src:local('%s')}" % (i, n) for i, n in enumerate(names))
    js_names = ','.join("'%s'" % n for n in names)
    return ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8"><title>localtest %s</title>\n<style>%sbody{font:16px system-ui;margin:24px}'
            '.ok{color:#087f23}.no{color:#b00020}td{padding:4px 12px}</style></head><body>\n<h1>Tên local() khớp trên máy này</h1><table id="t"></table>\n'
            '<script>\nconst names=[%s];window.__LT={};\n'
            'Promise.allSettled(Array.from(document.fonts).map(f=>f.load())).then(()=>{\n'
            ' const rows=[];Array.from(document.fonts).forEach(f=>{const i=+f.family.replace(/\\D/g,"");window.__LT[names[i]]=f.status==="loaded";});\n'
            ' names.forEach((n,i)=>{const ok=window.__LT[n];rows.push("<tr><td>"+n+"</td><td class=\\""+(ok?"ok":"no")+"\\">"+(ok?"ĐÃ KHỚP":"KHÔNG KHỚP")+'
            '"</td><td style=\\"font-family:lt"+i+",monospace\\">Tiếng Việt Ế Ộ Ừ Đ</td></tr>")});\n'
            ' document.getElementById("t").innerHTML=rows.join("");document.title="LT done";});\n</script></body></html>\n'
            % (html.escape(family), faces, js_names))


def main():
    ap = argparse.ArgumentParser(description='Sinh @font-face font dự phòng có size-adjust theo từng độ đậm.', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('--family', required=True)
    ap.add_argument('--web', action='append', default=[], help='FILE[,FILE...][@ĐỘ ĐẬM]')
    ap.add_argument('--sample', help='file văn bản UTF-8 lấy từ trang thật')
    ap.add_argument('--fallback-regular')
    ap.add_argument('--fallback-bold')
    ap.add_argument('--local-regular', default=LOCAL_R)
    ap.add_argument('--local-bold', default=LOCAL_B)
    ap.add_argument('--ranges', default=DEFAULT_RANGES)
    ap.add_argument('--out-dir')
    ap.add_argument('--apply', action='store_true', help='ghi file vào --out-dir (mặc định chỉ in CSS)')
    a = ap.parse_args()

    if not a.web:
        fail('thiếu --web', 2)
    if a.apply and not a.out_dir:
        fail('--apply cần --out-dir', 2)
    ranges = parse_ranges(a.ranges)
    local = {'r': parse_names(a.local_regular, '--local-regular'), 'b': parse_names(a.local_bold, '--local-bold')}
    if not SAFE_NAME.match(a.family):
        fail('--family có ký tự không hợp lệ: %r' % a.family, 2)
    if a.sample:
        try:
            text = open(a.sample, encoding='utf-8').read()
        except OSError as e:
            fail('không đọc được --sample: %s' % e)
    else:
        text = SAMPLE
        print('Cảnh báo: dùng mẫu chữ có sẵn. Truyền --sample với chữ thật của trang để số đo sát hơn.', file=sys.stderr)
    chars = [c for c in dict.fromkeys(text) if c.isprintable()]
    if len(text.strip()) < 200:
        print('Cảnh báo: mẫu chữ chỉ có %d ký tự, số đo có thể lệch. Dùng từ 200 ký tự có dấu tiếng Việt.' % len(text.strip()), file=sys.stderr)

    web = Web(a.web)
    fb = {k: load(find_fallback(k, getattr(a, 'fallback_regular' if k == 'r' else 'fallback_bold'))) for k in 'rb'}
    base = web.at(min(web.pins, key=lambda p: abs(p - 400)) if web.pins and not web.var else 400)[0]
    upm = base['head'].unitsPerEm
    asc, desc = base['hhea'].ascent / upm, -base['hhea'].descent / upm

    rows = []
    for lo, hi, w, k in ranges:
        sa, n = measure(web.at(w), fb[k], chars)
        rows.append({'lo': lo, 'hi': hi, 'w': w, 'k': k, 'sa': sa, 'n': n})
    merged = []
    for r in rows:
        if merged and merged[-1]['k'] == r['k'] and abs(merged[-1]['sa'] - r['sa']) < 0.00005:
            merged[-1]['hi'] = r['hi']
        else:
            merged.append(dict(r))
    fam = a.family + ' Fallback'
    css = '\n'.join(face(fam, r['lo'], r['hi'], ','.join("local('%s')" % n for n in local[r['k']]), r['sa'], asc, desc) for r in merged) + '\n'

    print('Họ %s: %d ký tự đo, ascent %.1f%%, descent %.1f%% (hhea, chưa chia size-adjust)' % (a.family, len(chars), asc * 100, desc * 100), file=sys.stderr)
    for r in rows:
        print('  dải %3d-%3d đo ở %d (%s): size-adjust %.2f%% (%d ký tự chung)' % (r['lo'], r['hi'], r['w'], 'thường' if r['k'] == 'r' else 'đậm', r['sa'] * 100, r['n']),
              file=sys.stderr)
    if a.apply:
        os.makedirs(a.out_dir, exist_ok=True)
        slug = re.sub(r'[^a-z0-9]+', '-', a.family.lower()).strip('-') or 'font'
        paths = [os.path.join(a.out_dir, slug + '-fallback.css'), os.path.join(a.out_dir, 'localtest.html')]
        for p in paths:
            if os.path.exists(p):
                fail('%s đã có, chuyển sang thư mục mới hoặc đổi tên (script không ghi đè)' % p)
        with open(paths[0], 'w', encoding='utf-8') as f:
            f.write(css)
        with open(paths[1], 'w', encoding='utf-8') as f:
            f.write(localtest(list(dict.fromkeys(local['r'] + local['b'])), a.family))
        print('Đã ghi: ' + ', '.join(paths), file=sys.stderr)
    else:
        sys.stdout.write(css)
        print('Dry-run: chưa ghi file. Thêm --out-dir DIR --apply để ghi CSS và localtest.html.', file=sys.stderr)


if __name__ == '__main__':
    main()
