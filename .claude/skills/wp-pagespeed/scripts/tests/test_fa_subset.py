# Test offline cho fa_subset/collect_icons.py và fa_subset/build_fa.py. Font Awesome giả: icon ở vùng PUA U+F000, mỗi style một file.
# Ca hỏng thật 21/10/2026 (site agency mẫu): critical CSS thiếu khai báo Font Awesome cho .fas và .fab, @font-face nằm trong file CSS đầy đủ 138 KB,
# FCP mô phỏng tăng từ 1,95 lên 2,7 s. fa-faces.css phải có đủ cặp face (bản cắt + bản đầy đủ) cho mọi kiểu đã khai.
# Ca kiểm kèm theo: icon fab bị xếp vào solid thì thành ô vuông, nên collect_icons.py phải tách kiểu đúng; icon thêm sau (không có trong bản cắt)
# phải rơi vào face đầy đủ. Kết quả đã đo ở site mẫu 17/10/2026: 167 KB còn khoảng 7 KB.
import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixtures_assets import make_font, py  # noqa: E402

COLLECT = os.path.join('fa_subset', 'collect_icons.py')
BUILD = os.path.join('fa_subset', 'build_fa.py')

FA_CSS = '''
.fa-heart:before{content:"\\f004"}
.fa-star:before{content:"\\f005"}
.fa-search:before,.fa-magnifying-glass:before{content:"\\f002"}
.fa-check-circle:before{content:"\\f058"}
.fa-phone:before{content:"\\f095"}
.fa-whatsapp:before{content:"\\f232"}
.fa-facebook-f:before{content:"\\f39e"}
.fa-1:before{content:"\\31"}
.fa-bolt::before{content:"\\f0e7"}
.fa-fw{width:1.25em}
.fa-spin{animation:fa-spin 2s infinite linear}
'''

FA7_CSS = '.fa-rocket{--fa:"\\f135"}\n.fa-user{--fa: "\\f007"}\n'

HTML = '''<!doctype html><html><body>
<i class="fas fa-heart"></i>
<i class="far fa-heart fa-2x"></i>
<a href="https://zalo.me/x"><i aria-hidden="true" class="fab fa-whatsapp"></i></a>
<i class="fa fa-star"></i>
<i class="fa-solid fa-search fa-fw"></i>
<i class="fa-solid fa-magnifying-glass"></i>
<i class='fas fa-1'></i>
<i class="fas fa-notreal"></i>
<i class="fal fa-bolt"></i>
<p>fa fa-spin trong văn bản thường không phải icon</p>
</body></html>
'''

ELEMENTOR = '{"settings":{"selected_icon":{"value":"fab fa-facebook-f","library":"fa-brands"},"icon2":{"value":"fas fa-phone","library":"fa-solid"}}}'
ELEMENTOR_ESCAPED = ELEMENTOR.replace('"', '\\"')
CUSTOM_CSS = '.tick:before{font-family:"Font Awesome 5 Free";font-weight:900;content:"\\f058"}\n.x{color:red}\n'


def parse_ranges(rng):
    out = set()
    for part in rng.split(','):
        part = part.strip()[2:]
        if '-' in part:
            a, b = part.split('-')
            out.add((int(a, 16), int(b, 16)))
        else:
            out.add((int(part, 16), int(part, 16)))
    return sorted(out)


def in_ranges(cp, rs):
    return any(a <= cp <= b for a, b in rs)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = tempfile.TemporaryDirectory()
        cls.d = cls.t.name
        cls.css = os.path.join(cls.d, 'all.css')
        with open(cls.css, 'w') as f:
            f.write(FA_CSS)
        cls.src = os.path.join(cls.d, 'site')
        os.makedirs(cls.src)
        for n, t in (('page.html', HTML), ('elementor.json', ELEMENTOR_ESCAPED), ('custom.css', CUSTOM_CSS)):
            with open(os.path.join(cls.src, n), 'w', encoding='utf-8') as f:
                f.write(t)

    @classmethod
    def tearDownClass(cls):
        cls.t.cleanup()

    def collect(self, *extra, paths=None):
        return py(COLLECT, '--css', self.css, *extra, *(paths or [self.src]))


class CollectIcons(Base):
    def data(self, r):
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_styles_split_and_modifiers_skipped(self):
        d = self.data(self.collect())
        s = d['styles']
        self.assertEqual(d['icons']['brands']['whatsapp'], 'f232')
        # Ca hỏng thật: icon fab không được lọt sang solid.
        self.assertNotIn('f232', s['solid'])
        self.assertNotIn('f232', s['regular'])
        self.assertIn('f004', s['solid'])      # fas fa-heart
        self.assertIn('f004', s['regular'])    # far fa-heart: cùng codepoint, nằm ở kiểu regular
        self.assertIn('f005', s['solid'])      # "fa fa-star" là solid
        self.assertIn('f002', s['solid'])      # fa-search và alias fa-magnifying-glass
        self.assertIn('31', s['solid'])        # fa-1 là icon chữ số, không phải cỡ chữ
        self.assertEqual(d['icons']['solid']['search'], d['icons']['solid']['magnifying-glass'])
        self.assertFalse(any(k.startswith('fw') or k == 'spin' for k in d['icons']['solid']))

    def test_elementor_json_escaped_and_custom_css(self):
        d = self.data(self.collect())
        self.assertIn('f39e', d['styles']['brands'])   # fab fa-facebook-f trong JSON bị escape \"
        self.assertIn('f095', d['styles']['solid'])    # fas fa-phone
        self.assertIn('f058', d['styles']['solid'])    # .tick:before font-weight 900 content "\f058"
        self.assertNotIn('f058', d['styles']['regular'])

    def test_unknown_and_pro_reported(self):
        d = self.data(self.collect())
        self.assertIn('fa-notreal', d['unknown'])
        self.assertIn('fa-bolt', d['pro_skipped'])     # fal là Pro: bỏ
        self.assertNotIn('f0e7', d['styles']['solid'])
        self.assertEqual(self.collect('--strict').returncode, 1)

    def test_dry_run_default_and_apply(self):
        out = os.path.join(self.d, 'icons.json')
        r = self.collect('--out', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(out))
        self.assertIn('Dry-run', r.stderr)
        r2 = self.collect('--out', out, '--apply')
        self.assertEqual(r2.returncode, 0, r2.stderr)
        with open(out) as fh:
            self.assertIn('f232', json.load(fh)['styles']['brands'])
        self.assertEqual(self.collect('--out', out, '--apply').returncode, 1)  # không ghi đè

    def test_library_css_in_scanned_dir_is_skipped(self):
        d = os.path.join(self.d, 'with-lib')
        os.makedirs(d)
        with open(os.path.join(d, 'page.html'), 'w') as f:
            f.write('<i class="fas fa-heart"></i>')
        with open(os.path.join(d, 'all.min.css'), 'w') as f:
            f.write(''.join('.fa-icon%d:before{content:"\\f%03x"}\n' % (i, i) for i in range(80)))
        r = self.collect(paths=[d])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['styles']['solid'], ['f004'])
        self.assertIn('CSS thư viện', r.stderr)

    def test_fa7_css_syntax_and_css_not_scanned(self):
        c7 = os.path.join(self.d, 'fa7.css')
        with open(c7, 'w') as f:
            f.write(FA7_CSS)
        d = os.path.join(self.d, 'fa7-site')
        os.makedirs(d)
        with open(os.path.join(d, 'a.html'), 'w') as f:
            f.write('<i class="fa-solid fa-rocket"></i><i class="fa-regular fa-user"></i>')
        r = py(COLLECT, '--css', c7, d)
        self.assertEqual(r.returncode, 0, r.stderr)
        j = json.loads(r.stdout)
        self.assertEqual(j['styles']['solid'], ['f135'])
        self.assertEqual(j['styles']['regular'], ['f007'])

    def test_bad_inputs(self):
        self.assertEqual(py(COLLECT, '--css', self.css, os.path.join(self.d, 'khong-co')).returncode, 1)
        self.assertEqual(py(COLLECT, '--css', os.path.join(self.d, 'khong-co.css'), self.src).returncode, 1)
        empty = os.path.join(self.d, 'rong.css')
        open(empty, 'w').close()
        self.assertEqual(py(COLLECT, '--css', empty, self.src).returncode, 1)
        self.assertEqual(py(COLLECT, '--css', self.css, self.src, '--apply').returncode, 2)

    def test_help(self):
        r = py(COLLECT, '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--css', r.stdout)


class BuildFa(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        full = {'solid': [0xF002, 0xF004, 0xF005, 0xF058, 0xF095, 0xF0E7, 0xF135, 0x31] + list(range(0xF100, 0xF120)) + list(range(0xF200, 0xF240)),
                'regular': [0xF004, 0xF005, 0xF058] + list(range(0xF100, 0xF140)),
                'brands': [0xF232, 0xF39E] + list(range(0xF300, 0xF3F0))}
        cls.fonts = {}
        for style, cps in full.items():
            cls.fonts[style] = make_font(os.path.join(cls.d, 'fa-%s-full.woff2' % style), {chr(cp): 600 for cp in cps}, flavor='woff2', family='FA ' + style,
                                         license_text='SIL OFL 1.1 test')
        cls.icons = os.path.join(cls.d, 'icons.json')
        with open(cls.icons, 'w') as f:
            json.dump({'styles': {'solid': ['f004', 'f005', 'f002'], 'regular': ['f004'], 'brands': ['f232']}}, f)

    def build(self, *extra, icons=None, styles=('solid', 'regular', 'brands')):
        a = ['--icons', icons or self.icons, '--url-prefix', '/wp-content/uploads/fonts', '--stamp', '20261017']
        for s in styles:
            a += ['--font', '%s=%s' % (s, self.fonts[s])]
        return py(BUILD, *a, *extra)

    def faces(self, css):
        out = []
        for m in re.finditer(r"@font-face\{font-family:'([^']+)';font-style:normal;font-weight:(\d+);font-display:(\w+);src:url\(([^)]+)\) format\('woff2'\)(?:;unicode-range:([^}]+))?\}", css):
            out.append({'family': m.group(1), 'weight': int(m.group(2)), 'display': m.group(3), 'url': m.group(4), 'rng': parse_ranges(m.group(5)) if m.group(5) else None})
        return out

    def test_dry_run_prints_css_writes_nothing(self):
        out = os.path.join(self.d, 'ra-dry')
        r = self.build('--out-dir', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(out))
        self.assertIn('Dry-run', r.stderr)
        self.assertEqual(len(self.faces(r.stdout)), 6)  # 3 kiểu x (bản cắt + bản đầy đủ)

    def test_six_faces_split_by_unicode_range_without_overlap(self):
        faces = self.faces(self.build().stdout)
        self.assertEqual(len(faces), 6)
        by = {}
        for f in faces:
            by.setdefault((f['family'], f['weight']), []).append(f)
        self.assertEqual(set(by), {('Font Awesome 5 Free', 900), ('Font Awesome 5 Free', 400), ('Font Awesome 5 Brands', 400)})
        for (fam, w), pair in by.items():
            sub, full = pair
            self.assertIn('-sub.woff2', sub['url'])
            self.assertNotIn('-sub', full['url'])
            for cp in (0xF002, 0xF004, 0xF005, 0xF232, 0x41, 0xF006, 0xF0FF, 0x10FFFF, 0x0):
                self.assertNotEqual(in_ranges(cp, sub['rng']), in_ranges(cp, full['rng']), 'U+%X phải nằm đúng một face (%s %d)' % (cp, fam, w))
        solid = by[('Font Awesome 5 Free', 900)]
        self.assertTrue(all(in_ranges(cp, solid[0]['rng']) for cp in (0xF002, 0xF004, 0xF005)))
        self.assertTrue(in_ranges(0xF058, solid[1]['rng']))  # icon thêm sau (f058 có trong font, không có trong bản cắt) rơi vào face đầy đủ
        self.assertTrue(in_ranges(0xF232, by[('Font Awesome 5 Brands', 400)][0]['rng']))
        self.assertTrue(all(f['display'] == 'block' for f in faces))

    def test_urls_use_prefix_and_full_font_name(self):
        faces = self.faces(self.build().stdout)
        urls = {f['url'] for f in faces}
        self.assertIn('/wp-content/uploads/fonts/fa-solid-20261017-sub.woff2', urls)
        self.assertIn('/wp-content/uploads/fonts/fa-solid-full.woff2', urls)
        r = self.build('--full-url', 'solid=/cu/fa-solid-900.woff2', '--family-free', 'Font Awesome 6 Free', '--display', 'swap')
        self.assertIn('/cu/fa-solid-900.woff2', r.stdout)
        self.assertIn("'Font Awesome 6 Free'", r.stdout)
        self.assertIn('font-display:swap', r.stdout)

    def test_apply_writes_cut_font_with_only_used_glyphs(self):
        from fontTools.ttLib import TTFont
        out = os.path.join(self.d, 'ra-apply')
        r = self.build('--out-dir', out, '--apply')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(os.listdir(out)), ['fa-brands-20261017-sub.woff2', 'fa-faces.css', 'fa-regular-20261017-sub.woff2', 'fa-report.json', 'fa-solid-20261017-sub.woff2'])
        sub = TTFont(os.path.join(out, 'fa-solid-20261017-sub.woff2'))
        self.assertEqual(sorted(sub.getBestCmap()), [0xF002, 0xF004, 0xF005])
        full_size = os.path.getsize(self.fonts['solid'])
        self.assertLess(os.path.getsize(os.path.join(out, 'fa-solid-20261017-sub.woff2')), full_size)
        with open(os.path.join(out, 'fa-report.json')) as fh:
            rep = json.load(fh)
        self.assertEqual(rep['solid']['icons'], 3)
        self.assertGreater(rep['solid']['saved_percent'], 20)
        # Giữ giấy phép OFL trong bảng name (nameID 13).
        self.assertIn('SIL OFL', sub['name'].getDebugName(13) or '')
        # Không ghi đè lần hai.
        r2 = self.build('--out-dir', out, '--apply')
        self.assertEqual(r2.returncode, 1)
        self.assertIn('không ghi đè', r2.stderr)

    def test_style_without_icons_keeps_single_full_face(self):
        ic = os.path.join(self.d, 'icons-solid-only.json')
        with open(ic, 'w') as f:
            json.dump({'styles': {'solid': ['f004'], 'regular': [], 'brands': []}}, f)
        faces = self.faces(self.build(icons=ic).stdout)
        reg = [f for f in faces if f['family'] == 'Font Awesome 5 Free' and f['weight'] == 400]
        brands = [f for f in faces if 'Brands' in f['family']]
        self.assertEqual(len(reg), 1)
        self.assertIsNone(reg[0]['rng'])
        self.assertNotIn('-sub', reg[0]['url'])
        self.assertEqual(len(brands), 1)

    def test_ev_icon_missing_in_font_warns_and_strict_fails(self):
        # Icon dùng sai kiểu: fa-facebook-f (f39e, chỉ có ở brands) đưa vào solid, font solid không có glyph này.
        ic = os.path.join(self.d, 'icons-wrong-style.json')
        with open(ic, 'w') as f:
            json.dump({'styles': {'solid': ['f004', 'f39e'], 'regular': [], 'brands': []}}, f)
        r = self.build(icons=ic, styles=('solid',))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('U+F39E', r.stderr)
        self.assertEqual(self.build('--strict', icons=ic, styles=('solid',)).returncode, 1)

    def test_pipeline_collect_then_build(self):
        r = self.collect()
        self.assertEqual(r.returncode, 0, r.stderr)
        ic = os.path.join(self.d, 'pipeline.json')
        with open(ic, 'w') as f:
            f.write(r.stdout)
        b = self.build(icons=ic)
        self.assertEqual(b.returncode, 0, b.stderr)
        self.assertEqual(len(self.faces(b.stdout)), 6)

    def test_bad_inputs(self):
        self.assertEqual(py(BUILD, '--icons', self.icons, '--stamp', 'x').returncode, 2)   # thiếu --font
        self.assertEqual(py(BUILD, '--icons', self.icons, '--stamp', 'x', '--font', 'bold=' + self.fonts['solid']).returncode, 2)
        self.assertEqual(py(BUILD, '--icons', os.path.join(self.d, 'khong-co.json'), '--stamp', 'x', '--font', 'solid=' + self.fonts['solid']).returncode, 1)
        self.assertEqual(py(BUILD, '--icons', self.icons, '--stamp', 'x', '--font', 'solid=' + os.path.join(self.d, 'khong-co.woff2')).returncode, 1)
        self.assertEqual(self.build('--apply').returncode, 2)  # --apply thiếu --out-dir
        self.assertEqual(py(BUILD, '--icons', self.icons, '--stamp', '../x', '--font', 'solid=' + self.fonts['solid']).returncode, 2)

    def test_help(self):
        r = py(BUILD, '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--icons', r.stdout)


if __name__ == '__main__':
    unittest.main()
