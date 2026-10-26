# Test offline cho img_variants.py. Ảnh giả dựng bằng Pillow trong thư mục tạm.
# Ca hỏng thật: (1) 18/10/2026 trang chủ phải tải hero 800w 122 KB trong khi điện thoại cần khoảng 663 px: phải có bản 720w nhẹ hơn.
# (2) logo đối tác WebP đã nén tốt (5 KB), bản 88h lớn hơn thì phải giữ bản gốc, không thay bằng file nặng hơn.
# (3) Script chỉ được tạo file cho ảnh trang dùng, SVG giữ nguyên, tên file mới (không đè ảnh cũ trong cache 1 năm).
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixtures_assets import flat_image, noise_image, py  # noqa: E402

PREFIX = '/wp-content/uploads/site/'


def listing(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = (os.path.getsize(p), os.path.getmtime(p))
    return out


class ImgVariants(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.Image = Image
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name
        self.up = os.path.join(self.d, 'uploads')
        os.makedirs(os.path.join(self.up, 'logos'))
        # Hero: ảnh gốc 1000 px, bản 800w đang dùng. Ảnh nhiễu nên các cỡ khác nhau rõ rệt.
        noise_image(os.path.join(self.up, 'hero.webp'), (1000, 560), seed=3, fmt='WEBP', quality=82)
        noise_image(os.path.join(self.up, 'hero-800w.webp'), (800, 450), seed=3, fmt='WEBP', quality=82)
        # Logo PNG cao 240 px: bản 88h nhỏ hơn nhiều.
        noise_image(os.path.join(self.up, 'logos', 'acme.png'), (480, 240), seed=5, fmt='PNG')
        # Logo WebP đã nén rất mạnh (q=5, cao 100 px): bản 88h q82 sẽ nặng hơn.
        noise_image(os.path.join(self.up, 'logos', 'tiny.webp'), (200, 100), seed=7, fmt='WEBP', quality=5)
        # Logo WebP đã thấp hơn 88 px: giữ nguyên.
        flat_image(os.path.join(self.up, 'logos', 'small.webp'), (120, 60), fmt='WEBP')
        with open(os.path.join(self.up, 'logos', 'mark.svg'), 'w') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>')
        # Avatar 600 px và một ảnh trong thư mục nhưng HTML không dùng.
        noise_image(os.path.join(self.up, 'avatar-an.jpg'), (600, 600), seed=9, fmt='JPEG', quality=90)
        noise_image(os.path.join(self.up, 'khong-dung.webp'), (1000, 560), seed=11, fmt='WEBP', quality=82)
        noise_image(os.path.join(self.up, 'khong-dung-800w.webp'), (800, 450), seed=11, fmt='WEBP', quality=82)
        self.html = os.path.join(self.d, 'trang.html')
        with open(self.html, 'w', encoding='utf-8') as f:
            f.write(self.page())

    def tearDown(self):
        self.t.cleanup()

    def size(self, *parts):
        with self.Image.open(os.path.join(self.up, *parts)) as im:
            return im.size

    def page(self):
        return (
            '<!doctype html><html><body>\n'
            '<img class="hero" src="%shero-800w.webp" srcset="%shero-800w.webp 800w" sizes="100vw" width="800" height="450" alt="Hero">\n'
            '<img class="logo" src="%slogos/acme.png" width="176" height="88" alt="Acme" loading="lazy">\n'
            '<img class="logo" src="%slogos/tiny.webp" width="176" height="88" alt="Tiny">\n'
            '<img class="logo" src="%slogos/small.webp" width="120" height="60" alt="Nhỏ">\n'
            '<img class="logo" src="%slogos/mark.svg" width="88" height="88" alt="Mark">\n'
            '<img class="team-avatar" src="%savatar-an.jpg" width="600" height="600" alt="An">\n'
            '<img src="https://khac.example/anh.png" alt="Ngoài">\n'
            '</body></html>\n' % ((PREFIX,) * 7))

    def run_it(self, *extra):
        return py('img_variants.py', '--html', self.html, '--map', '%s=%s' % (PREFIX, self.up), *extra)

    def test_dry_run_writes_nothing(self):
        before = listing(self.d)
        r = self.run_it('--out-html', os.path.join(self.d, 'moi.html'))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(listing(self.d), before)
        self.assertIn('SẼ TẠO', r.stdout)
        self.assertIn('Dry-run', r.stderr)
        self.assertRegex(r.stdout, r'IMG_VARIANTS tao=\d+')

    def test_apply_creates_expected_variants_and_rewrites_html(self):
        out = os.path.join(self.d, 'moi.html')
        r = self.run_it('--apply', '--out-html', out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = set(os.listdir(self.up)) | {'logos/' + x for x in os.listdir(os.path.join(self.up, 'logos'))}
        # hero: 720w, 560w, 400w (đều hẹp hơn ảnh gốc 1000 và nhẹ hơn bản 800w)
        for w in (400, 560, 720):
            self.assertIn('hero-%dw.webp' % w, files)
        self.assertIn('logos/acme-88h.webp', files)
        self.assertIn('avatar-an-96w.webp', files)
        # Ca hỏng thật: logo WebP đã nén tốt giữ bản gốc, logo thấp hơn 88 px và SVG không sinh file.
        self.assertNotIn('logos/tiny-88h.webp', files)
        self.assertNotIn('logos/small-88h.webp', files)
        self.assertNotIn('logos/mark-88h.webp', files)
        # Ảnh HTML không dùng: không có bản mới.
        self.assertEqual({f for f in files if f.startswith('khong-dung')}, {'khong-dung.webp', 'khong-dung-800w.webp'})
        with open(out, encoding='utf-8') as fh:
            h = fh.read()
        m = re.search(r'srcset="([^"]+)"', h)
        self.assertEqual(m.group(1), '%shero-400w.webp 400w, %shero-560w.webp 560w, %shero-720w.webp 720w, %shero-800w.webp 800w' % ((PREFIX,) * 4))
        self.assertIn('sizes="100vw"', h)  # không đổi sizes
        self.assertIn('src="%slogos/acme-88h.webp" width="176" height="88"' % PREFIX, h)
        self.assertIn('src="%slogos/tiny.webp"' % PREFIX, h)
        self.assertIn('src="%slogos/mark.svg"' % PREFIX, h)
        self.assertIn('src="%savatar-an-96w.webp" width="96" height="96"' % PREFIX, h)
        self.assertIn('loading="lazy"', h)
        self.assertIn('https://khac.example/anh.png', h)
        # Kích thước thật của bản mới.
        self.assertEqual(self.size('hero-720w.webp'), (720, 403))
        self.assertEqual(self.size('logos', 'acme-88h.webp'), (176, 88))
        self.assertEqual(self.size('avatar-an-96w.webp'), (96, 96))

    def test_ev_hero_720w_lighter_than_800w(self):
        self.assertEqual(self.run_it('--apply').returncode, 0)
        self.assertLess(os.path.getsize(os.path.join(self.up, 'hero-720w.webp')), os.path.getsize(os.path.join(self.up, 'hero-800w.webp')))
        self.assertLess(os.path.getsize(os.path.join(self.up, 'hero-400w.webp')), os.path.getsize(os.path.join(self.up, 'hero-560w.webp')))

    def test_ev_heavier_variant_is_not_used(self):
        r = self.run_it()
        self.assertIn('GIỮ GỐC logos/tiny.webp', r.stdout)
        self.assertRegex(r.stdout, r'giu_goc=[1-9]')

    def test_never_overwrites_existing_files_or_html(self):
        self.assertEqual(self.run_it('--apply').returncode, 0)
        snap = listing(self.up)
        out = os.path.join(self.d, 'moi.html')
        r2 = self.run_it('--apply', '--out-html', out)  # lần hai: mọi bản đã có
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(listing(self.up), snap)
        self.assertIn('CÓ SẴN', r2.stdout)
        with open(out, encoding='utf-8') as fh:
            self.assertIn('hero-720w.webp 720w', fh.read())  # HTML vẫn trỏ tới các bản đã có
        r3 = self.run_it('--apply', '--out-html', out)  # đích HTML đã có
        self.assertEqual(r3.returncode, 1)
        self.assertIn('không ghi đè', r3.stderr)

    def test_custom_logo_height_and_widths(self):
        r = self.run_it('--apply', '--logo-height', '60', '--widths', '320', '--avatar-width', '48')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.up, 'logos', 'acme-60h.webp')))
        self.assertTrue(os.path.exists(os.path.join(self.up, 'hero-320w.webp')))
        self.assertFalse(os.path.exists(os.path.join(self.up, 'hero-720w.webp')))
        self.assertTrue(os.path.exists(os.path.join(self.up, 'avatar-an-48w.webp')))

    def test_missing_source_image_leaves_tag(self):
        with open(self.html, 'w', encoding='utf-8') as f:
            f.write('<img src="%slogos/khong-co.png" width="10" height="10"><img srcset="%smat-800w.webp 800w">' % (PREFIX, PREFIX))
        out = os.path.join(self.d, 'moi.html')
        r = self.run_it('--apply', '--out-html', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(out))  # HTML không đổi thì không ghi file

    def test_multiple_html_share_images_counted_once(self):
        h2 = os.path.join(self.d, 'trang2.html')
        with open(h2, 'w', encoding='utf-8') as f:
            f.write(self.page())
        r = py('img_variants.py', '--html', self.html, '--html', h2, '--map', '%s=%s' % (PREFIX, self.up))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len([ln for ln in r.stdout.splitlines() if 'SẼ TẠO' in ln and 'hero-720w.webp' in ln]), 1)

    def test_bad_inputs(self):
        self.assertEqual(py('img_variants.py', '--html', os.path.join(self.d, 'khong-co.html'), '--map', '%s=%s' % (PREFIX, self.up)).returncode, 1)
        self.assertEqual(py('img_variants.py', '--html', self.html, '--map', '%s=%s' % (PREFIX, os.path.join(self.d, 'khong-co'))).returncode, 1)
        self.assertEqual(py('img_variants.py', '--html', self.html, '--map', 'khong-co-dau-bang').returncode, 2)
        self.assertEqual(py('img_variants.py', '--html', self.html, '--map', '%s=%s' % (PREFIX, self.up), '--widths', 'a,b').returncode, 2)
        self.assertEqual(py('img_variants.py', '--html', self.html, '--map', '%s=%s' % (PREFIX, self.up), '--avatar-match', '(').returncode, 2)
        self.assertEqual(py('img_variants.py', '--html', self.html, '--html', self.html, '--map', '%s=%s' % (PREFIX, self.up), '--out-html', 'x.html').returncode, 2)

    def test_help(self):
        r = py('img_variants.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--logo-height', r.stdout)


if __name__ == '__main__':
    unittest.main()
