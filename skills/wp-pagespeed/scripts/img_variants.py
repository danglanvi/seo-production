#!/usr/bin/env python3
"""Sinh bản ảnh nhẹ cho đúng các ảnh mà HTML của trang đang dùng, rồi viết lại thẻ <img> trỏ tới bản mới.

Ba việc, đều theo luật lớp 3 của checklist-theo-lop.md:
  1. Logo dải chạy ngang (src nằm dưới thư mục logo): bản <tên>-<cao>h.webp cao --logo-height px (mặc định 88). PNG cũng đổi sang WebP.
     Chỉ giữ bản mới khi nhỏ hơn bản gốc. Logo WebP đã cao bằng hoặc thấp hơn --logo-height giữ nguyên. SVG giữ nguyên.
  2. Ảnh có srcset: thêm các cỡ --widths (mặc định 400,560,720) từ ảnh gốc <tên>.webp, chất lượng --photo-quality (mặc định 75).
     Chỉ thêm cỡ hẹp hơn ảnh gốc và nhỏ hơn byte so với bản lớn nhất đang có trong srcset. Không đổi sizes (đo bề rộng hiển thị trước, img_display_width.mjs).
  3. Avatar (thẻ <img> khớp --avatar-match): bản <tên>-<rộng>w.webp rộng --avatar-width px (mặc định 96), chỉ khi nhỏ hơn bản gốc. Thẻ có srcset bị bỏ qua.
Chỉ ghi file cho ảnh trang dùng. Ảnh nằm trong thư mục nhưng HTML không nhắc tới thì không đụng. Tên file mới, nên cache 1 năm không giữ bản cũ.

Dùng (cần Pillow; chạy python3 không có -I):
  python3 img_variants.py --html trang.html --map /wp-content/uploads/site/=./uploads [--map PREFIX=DIR ...] [--apply --out-html trang-moi.html]
  --html FILE            HTML cần xử lý. Lặp lại được (nhiều trang dùng chung ảnh). Với nhiều file, dùng --out-html-dir.
  --map TIỀN_TỐ=THƯ_MỤC  tiền tố URL của ảnh trong HTML và thư mục local chứa chính các file đó. Lặp lại được.
  --logo-dir TÊN         thư mục logo dưới tiền tố. Mặc định logos/
  --logo-height, --widths, --photo-quality, --logo-quality, --avatar-match, --avatar-width   xem trên.
  --apply                ghi bản ảnh mới. Không có --apply: chỉ in kế hoạch và dung lượng, không ghi file nào.
  --out-html FILE        (một --html) ghi HTML đã viết lại. Không bao giờ ghi đè HTML gốc hay ảnh có sẵn.
  --out-html-dir DIR     (nhiều --html) ghi HTML đã viết lại vào DIR cùng tên file.
Cuối cùng in một dòng "IMG_VARIANTS tao=<n> co_san=<n> giu_goc=<n> tiet_kiem_kb=<kb>".
Mã thoát: 0 xong, 1 lỗi dữ liệu (thiếu HTML, thiếu Pillow, thư mục --map không có, đích --out-html đã có), 2 sai tham số.
"""
import argparse
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    print('Lỗi: cần Pillow (pip install pillow). Chạy python3 không có -I.', file=sys.stderr)
    sys.exit(1)

STATS = {'tao': 0, 'co_san': 0, 'giu_goc': 0, 'bytes': 0}


def die(msg, code=1):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


def load(path):
    im = Image.open(path)
    im.load()
    return im


def encode(im, w, h, q):
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA')
    if (w, h) != im.size:
        im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, alpha_quality=85, method=6)
    return buf.getvalue()


class Planner:
    def __init__(self, apply):
        self.apply, self.decided = apply, {}

    def make(self, out, data, orig_bytes, label):
        """Ghi (hoặc chỉ lên kế hoạch) một bản mới. Trả True nếu bản mới được dùng."""
        if out in self.decided:
            return self.decided[out]  # cùng ảnh xuất hiện lần hai trong HTML
        self.decided[out] = self._make(out, data, orig_bytes, label)
        return self.decided[out]

    def _make(self, out, data, orig_bytes, label):
        if os.path.exists(out):
            STATS['co_san'] += 1
            print('  CÓ SẴN  %s (giữ nguyên, không ghi đè)' % out)
            return True
        if len(data) >= orig_bytes:
            STATS['giu_goc'] += 1
            print('  GIỮ GỐC %s: bản mới %d B không nhỏ hơn bản gốc %d B' % (label, len(data), orig_bytes))
            return False
        STATS['tao'] += 1
        STATS['bytes'] += orig_bytes - len(data)
        print('  %s %s: %d B (gốc %d B)' % ('TẠO    ' if self.apply else 'SẼ TẠO ', out, len(data), orig_bytes))
        if self.apply:
            with open(out, 'wb') as f:
                f.write(data)
        return True


def set_attr(tag, name, value):
    return re.sub(r'(\s%s=")\d+(")' % name, r'\g<1>%d\g<2>' % value, tag, count=1)


def logos(html, prefix, updir, a, plan):
    pat = re.compile(r'<img[^>]*\ssrc="' + re.escape(prefix + a.logo_dir) + r'([^"]+\.(?:webp|png|jpe?g))"[^>]*>', re.I)

    def rep(m):
        rel = a.logo_dir + m.group(1)
        f = os.path.join(updir, rel)
        if not os.path.isfile(f):
            return m.group(0)
        im = load(f)
        ext = os.path.splitext(f)[1].lower()
        if ext == '.webp' and im.height <= a.logo_height:
            return m.group(0)
        h = min(a.logo_height, im.height)
        w = round(im.width * h / im.height)
        stem = os.path.splitext(os.path.basename(rel))[0]
        out = os.path.join(os.path.dirname(f), '%s-%dh.webp' % (stem, a.logo_height))
        if not plan.make(out, encode(im, w, h, a.logo_quality), os.path.getsize(f), rel):
            return m.group(0)
        tag = m.group(0).replace(prefix + rel, prefix + os.path.join(os.path.dirname(rel), os.path.basename(out)).replace(os.sep, '/'))
        return set_attr(set_attr(tag, 'width', w), 'height', h)
    return pat.sub(rep, html)


def srcsets(html, prefix, updir, a, plan):
    def rep(m):
        items = [x.strip().rsplit(None, 1) for x in m.group(1).split(',') if x.strip()]
        urls = {}
        for it in items:
            if len(it) == 2 and it[1].endswith('w') and it[1][:-1].isdigit():
                urls[int(it[1][:-1])] = it[0]
        if not urls:
            return m.group(0)
        top = max(urls)
        u = urls[top]
        mm = re.fullmatch(re.escape(prefix) + r'(.+)-%dw\.webp' % top, u)
        if not mm:
            return m.group(0)
        stem = mm.group(1)
        full, topfile = os.path.join(updir, stem + '.webp'), os.path.join(updir, u[len(prefix):])
        if not os.path.isfile(full) or not os.path.isfile(topfile):
            return m.group(0)
        im = load(full)
        top_bytes = os.path.getsize(topfile)
        changed = False
        for w in a.widths:
            if w >= min(im.width, top) or w in urls:
                continue
            out = os.path.join(updir, '%s-%dw.webp' % (stem, w))
            if plan.make(out, encode(im, w, round(im.height * w / im.width), a.photo_quality), top_bytes, '%s-%dw' % (stem, w)):
                urls[w] = '%s%s-%dw.webp' % (prefix, stem, w)
                changed = True
        if not changed:
            return m.group(0)
        return 'srcset="' + ', '.join('%s %dw' % (urls[w], w) for w in sorted(urls)) + '"'
    return re.sub(r'srcset="([^"]+)"', rep, html)


def avatars(html, prefix, updir, a, plan):
    pat = re.compile(r'<img[^>]*>', re.I)

    def rep(m):
        tag = m.group(0)
        if not re.search(a.avatar_match, tag, re.I) or 'srcset=' in tag:
            return tag
        s = re.search(r'\ssrc="' + re.escape(prefix) + r'([^"]+\.(?:webp|png|jpe?g))"', tag, re.I)
        if not s or re.search(r'-(?:\d+h|\d+w)\.webp$', s.group(1)):
            return tag
        f = os.path.join(updir, s.group(1))
        if not os.path.isfile(f):
            return tag
        im = load(f)
        if im.width <= a.avatar_width:
            return tag
        h = round(im.height * a.avatar_width / im.width)
        out = os.path.join(os.path.dirname(f), '%s-%dw.webp' % (os.path.splitext(os.path.basename(f))[0], a.avatar_width))
        if not plan.make(out, encode(im, a.avatar_width, h, a.logo_quality), os.path.getsize(f), s.group(1)):
            return tag
        new = prefix + os.path.join(os.path.dirname(s.group(1)), os.path.basename(out)).replace(os.sep, '/')
        tag = tag.replace(prefix + s.group(1), new)
        return set_attr(set_attr(tag, 'width', a.avatar_width), 'height', h)
    return pat.sub(rep, html)


def process(html, maps, a, plan):
    for prefix, updir in maps:
        html = logos(html, prefix, updir, a, plan)
        html = avatars(html, prefix, updir, a, plan)
        html = srcsets(html, prefix, updir, a, plan)
    return html


def main():
    ap = argparse.ArgumentParser(description='Sinh bản ảnh nhẹ (logo, srcset, avatar) cho ảnh trang dùng.', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('--html', action='append', required=True)
    ap.add_argument('--map', action='append', required=True, help='TIỀN_TỐ_URL=THƯ_MỤC_LOCAL')
    ap.add_argument('--logo-dir', default='logos/')
    ap.add_argument('--logo-height', type=int, default=88)
    ap.add_argument('--widths', default='400,560,720')
    ap.add_argument('--photo-quality', type=int, default=75)
    ap.add_argument('--logo-quality', type=int, default=82)
    ap.add_argument('--avatar-match', default='avatar')
    ap.add_argument('--avatar-width', type=int, default=96)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--out-html')
    ap.add_argument('--out-html-dir')
    a = ap.parse_args()

    try:
        a.widths = sorted({int(x) for x in a.widths.split(',') if x.strip()})
    except ValueError:
        die('--widths phải là danh sách số ngăn cách bằng dấu phẩy', 2)
    if not a.widths or a.logo_height < 8 or a.avatar_width < 8 or not (1 <= a.photo_quality <= 100 and 1 <= a.logo_quality <= 100):
        die('tham số số không hợp lệ', 2)
    if not a.logo_dir.endswith('/'):
        a.logo_dir += '/'
    try:
        re.compile(a.avatar_match)
    except re.error as e:
        die('--avatar-match không phải regex: %s' % e, 2)
    if a.out_html and len(a.html) != 1:
        die('--out-html chỉ dùng với một --html (nhiều file thì dùng --out-html-dir)', 2)
    if (a.out_html or a.out_html_dir) and not a.apply:
        print('Dry-run: --out-html bị bỏ qua vì chưa có --apply.', file=sys.stderr)
    maps = []
    for m in a.map:
        prefix, sep, d = m.partition('=')
        if not sep or not prefix.startswith('/') and not prefix.startswith('http'):
            die('--map phải có dạng TIỀN_TỐ_URL=THƯ_MỤC, tiền tố bắt đầu bằng /: %r' % m, 2)
        if not os.path.isdir(d):
            die('không có thư mục --map: %s' % d)
        maps.append((prefix if prefix.endswith('/') else prefix + '/', d))

    plan = Planner(a.apply)
    for path in a.html:
        try:
            with open(path, encoding='utf-8') as f:
                html = f.read()
        except OSError as e:
            die('không đọc được HTML %s: %s' % (path, e))
        print('%s:' % path)
        new = process(html, maps, a, plan)
        if a.apply and new != html and (a.out_html or a.out_html_dir):
            dest = a.out_html or os.path.join(a.out_html_dir, os.path.basename(path))
            if os.path.exists(dest):
                die('%s đã có (script không ghi đè HTML)' % dest)
            if a.out_html_dir:
                os.makedirs(a.out_html_dir, exist_ok=True)
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(new)
            print('  Đã ghi HTML mới: %s' % dest)
    print('IMG_VARIANTS tao=%d co_san=%d giu_goc=%d tiet_kiem_kb=%.1f' % (STATS['tao'], STATS['co_san'], STATS['giu_goc'], STATS['bytes'] / 1024.0))
    if not a.apply:
        print('Dry-run: chưa ghi file. Thêm --apply (và --out-html) để ghi.', file=sys.stderr)


if __name__ == '__main__':
    main()
