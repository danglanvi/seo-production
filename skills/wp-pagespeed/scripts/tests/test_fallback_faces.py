# Test offline cho fallback_faces.py. Font giả dựng bằng fontTools, mỗi ký tự một bề rộng biết trước.
# Ca hỏng thật (18/10/2026, site mẫu 2): một face dự phòng cho cả dải 650-900 làm H1 độ đậm 800 xuống dòng khác khi font thật về,
# CLS mobile của một trang dịch vụ 0 sang 0,27. Số đo phải tính riêng từng độ đậm. Ca thứ hai: font web tách subset latin và vi,
# bỏ subset vi thì bề rộng chữ Việt lệch. Ca thứ ba: ký tự chỉ có ở một trong hai font không được lọt vào tổng bề rộng.
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixtures_assets import LATIN, VIET, make_font, py  # noqa: E402

SAMPLE = ('Tối ưu tốc độ website: ' + 'Đăng ký tư vấn miễn phí, được hỗ trợ ngay. ' * 6)


def face_values(css):
    out = []
    for m in re.finditer(r"font-weight:(\d+) (\d+);src:([^;]+);size-adjust:([\d.]+)%;ascent-override:([\d.]+)%;descent-override:([\d.]+)%;line-gap-override:0%", css):
        out.append({'lo': int(m.group(1)), 'hi': int(m.group(2)), 'src': m.group(3), 'sa': float(m.group(4)), 'asc': float(m.group(5)), 'desc': float(m.group(6))})
    return out


class FallbackFaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = tempfile.TemporaryDirectory()
        d = cls.t.name
        cls.d = d
        # Font web: latin 600 (thường) và 700 (đậm 700); vi 650 và 760. Font dự phòng: mọi ký tự 500, đậm 560.
        cls.l400 = make_font(os.path.join(d, 'w400-latin.ttf'), {c: 600 for c in LATIN}, asc=950, desc=-250)
        cls.v400 = make_font(os.path.join(d, 'w400-vi.ttf'), {c: 650 for c in VIET}, asc=950, desc=-250)
        cls.l700 = make_font(os.path.join(d, 'w700-latin.ttf'), {c: 700 for c in LATIN}, asc=950, desc=-250)
        cls.v700 = make_font(os.path.join(d, 'w700-vi.ttf'), {c: 760 for c in VIET}, asc=950, desc=-250)
        cls.fbr = make_font(os.path.join(d, 'fb-r.ttf'), {c: 500 for c in LATIN + VIET})
        cls.fbb = make_font(os.path.join(d, 'fb-b.ttf'), {c: 560 for c in LATIN + VIET})
        cls.sample = os.path.join(d, 'mau.txt')
        with open(cls.sample, 'w', encoding='utf-8') as f:
            f.write(SAMPLE)

    @classmethod
    def tearDownClass(cls):
        cls.t.cleanup()

    def args(self, *extra, web400=True, web700=True):
        a = ['--family', 'Be Test', '--sample', self.sample, '--fallback-regular', self.fbr, '--fallback-bold', self.fbb]
        if web400:
            a += ['--web', '%s,%s@400' % (self.l400, self.v400)]
        if web700:
            a += ['--web', '%s,%s@700' % (self.l700, self.v700)]
        return a + list(extra)

    def expected(self, wl, wv, fb):
        chars = [c for c in dict.fromkeys(SAMPLE) if c.isprintable()]
        web = sum((wv if c in VIET else wl) for c in chars if c in LATIN or c in VIET)
        return web / (fb * len([c for c in chars if c in LATIN or c in VIET]))

    def test_size_adjust_matches_width_ratio(self):
        r = py('fallback_faces.py', *self.args(web700=False))
        self.assertEqual(r.returncode, 0, r.stderr)
        faces = face_values(r.stdout)
        self.assertTrue(faces)
        want = self.expected(600, 650, 500) * 100
        # Dải 100-449 và 450-549 đo ở 400 và 500: cả hai dùng font độ đậm 400 (gần nhất), cùng số đo, nên được gộp.
        self.assertAlmostEqual(faces[0]['sa'], want, delta=0.02)
        self.assertEqual(faces[0]['lo'], 100)
        self.assertIn("local('Arial')", faces[0]['src'])
        self.assertIn("font-family:'Be Test Fallback'", r.stdout)
        self.assertEqual(r.stdout.count('line-gap-override:0%'), len(faces))

    def test_ev_bold_gets_own_size_adjust(self):
        r = py('fallback_faces.py', *self.args())
        self.assertEqual(r.returncode, 0, r.stderr)
        faces = face_values(r.stdout)
        reg = [f for f in faces if f['lo'] < 550]
        bold = [f for f in faces if f['lo'] >= 550]
        self.assertTrue(reg and bold)
        self.assertAlmostEqual(reg[0]['sa'], self.expected(600, 650, 500) * 100, delta=0.02)
        self.assertAlmostEqual(bold[0]['sa'], self.expected(700, 760, 560) * 100, delta=0.02)
        self.assertGreater(abs(reg[0]['sa'] - bold[0]['sa']), 3.0)  # một face chung cho mọi độ đậm sẽ sai ít nhất ngần này
        self.assertIn("local('Arial Bold')", bold[0]['src'])
        # Dải 550-900 chỉ có font đậm 700 nên dùng chung số đo, không lẫn với dải thường.
        self.assertEqual((reg[0]['lo'], reg[0]['hi'], bold[0]['lo'], bold[0]['hi']), (100, 549, 550, 900))
        self.assertTrue(all(f['hi'] >= f['lo'] for f in faces))

    def test_ev_missing_vi_subset_changes_result(self):
        with_vi = face_values(py('fallback_faces.py', *self.args(web700=False)).stdout)[0]['sa']
        no_vi = py('fallback_faces.py', '--family', 'Be Test', '--sample', self.sample, '--fallback-regular', self.fbr, '--fallback-bold', self.fbb,
                   '--web', self.l400 + '@400')
        self.assertEqual(no_vi.returncode, 0, no_vi.stderr)
        sa_no_vi = face_values(no_vi.stdout)[0]['sa']
        # Không có subset vi: chữ Việt rơi khỏi phép đo, tỉ lệ về đúng 600/500 và lệch so với bản đủ subset.
        self.assertAlmostEqual(sa_no_vi, 120.0, delta=0.02)
        self.assertGreater(abs(with_vi - sa_no_vi), 1.0)

    def test_chars_missing_in_one_font_are_skipped(self):
        d = self.d
        web = make_font(os.path.join(d, 'solo-web.ttf'), {c: 600 for c in LATIN + 'ế'})
        fb = make_font(os.path.join(d, 'solo-fb.ttf'), {c: 500 for c in LATIN + 'ộ'})
        sample = os.path.join(d, 'solo.txt')
        with open(sample, 'w', encoding='utf-8') as f:
            f.write('aaaa bbbb ế ế ế ế ế ế ộ ộ ộ ộ ộ ộ ' * 8)
        r = py('fallback_faces.py', '--family', 'Solo', '--sample', sample, '--web', web + '@400', '--fallback-regular', fb, '--fallback-bold', fb)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAlmostEqual(face_values(r.stdout)[0]['sa'], 120.0, delta=0.02)  # ế và ộ không tính vào phép đo

    def test_ascent_descent_divided_by_size_adjust(self):
        faces = face_values(py('fallback_faces.py', *self.args(web700=False)).stdout)
        f = faces[0]
        self.assertAlmostEqual(f['asc'], 95.0 / (f['sa'] / 100.0), delta=0.05)
        self.assertAlmostEqual(f['desc'], 25.0 / (f['sa'] / 100.0), delta=0.05)

    def test_custom_local_names_and_ranges(self):
        r = py('fallback_faces.py', *self.args('--local-regular', 'Roboto,Roboto-Regular', '--local-bold', 'Roboto Bold', '--ranges', '100-599:400:r,600-900:700:b'))
        self.assertEqual(r.returncode, 0, r.stderr)
        faces = face_values(r.stdout)
        self.assertEqual([(f['lo'], f['hi']) for f in faces], [(100, 599), (600, 900)])
        self.assertIn("local('Roboto'),local('Roboto-Regular')", faces[0]['src'])
        self.assertIn("local('Roboto Bold')", faces[1]['src'])

    def test_dry_run_default_writes_nothing_apply_writes_both(self):
        out = os.path.join(self.d, 'ra')
        r = py('fallback_faces.py', *self.args('--out-dir', out, web700=False))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(out))
        self.assertIn('Dry-run', r.stderr)
        r2 = py('fallback_faces.py', *self.args('--out-dir', out, '--apply', web700=False))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(sorted(os.listdir(out)), ['be-test-fallback.css', 'localtest.html'])
        # Không ghi đè lần hai.
        r3 = py('fallback_faces.py', *self.args('--out-dir', out, '--apply', web700=False))
        self.assertEqual(r3.returncode, 1)
        self.assertIn('không ghi đè', r3.stderr)

    def test_localtest_declares_each_local_once(self):
        out = os.path.join(self.d, 'lt')
        r = py('fallback_faces.py', *self.args('--out-dir', out, '--apply', '--local-regular', 'Arial,Liberation Sans', '--local-bold', 'Arial Bold'))
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(out, 'localtest.html'), encoding='utf-8') as fh:
            h = fh.read()
        for i, n in enumerate(['Arial', 'Liberation Sans', 'Arial Bold']):
            self.assertEqual(h.count("@font-face{font-family:'lt%d';src:local('%s')}" % (i, n)), 1, n)
        self.assertNotIn("lt3'", h)
        self.assertIn('window.__LT', h)

    def test_bad_inputs(self):
        # font tĩnh không có @độ đậm
        r = py('fallback_faces.py', '--family', 'X', '--web', self.l400, '--fallback-regular', self.fbr, '--fallback-bold', self.fbb)
        self.assertEqual(r.returncode, 2)
        self.assertIn('@ĐỘ ĐẬM', r.stderr)
        # thiếu --web
        self.assertEqual(py('fallback_faces.py', '--family', 'X').returncode, 2)
        # file font hỏng
        bad = os.path.join(self.d, 'hong.ttf')
        with open(bad, 'wb') as f:
            f.write(b'khong phai font')
        r = py('fallback_faces.py', '--family', 'X', '--web', bad + '@400', '--fallback-regular', self.fbr, '--fallback-bold', self.fbb)
        self.assertEqual(r.returncode, 1)
        # tên local() có dấu nháy
        r = py('fallback_faces.py', *self.args('--local-regular', "Arial'); x{"))
        self.assertEqual(r.returncode, 2)
        # dải sai
        self.assertEqual(py('fallback_faces.py', *self.args('--ranges', '900-100:400:r')).returncode, 2)
        # --apply thiếu --out-dir
        self.assertEqual(py('fallback_faces.py', *self.args('--apply')).returncode, 2)

    def test_no_common_chars_is_error(self):
        web = make_font(os.path.join(self.d, 'w-only-x.ttf'), {'x': 600})
        fb = make_font(os.path.join(self.d, 'f-only-y.ttf'), {'y': 500})
        s = os.path.join(self.d, 'xy.txt')
        with open(s, 'w') as f:
            f.write('xy' * 200)
        r = py('fallback_faces.py', '--family', 'X', '--sample', s, '--web', web + '@400', '--fallback-regular', fb, '--fallback-bold', fb)
        self.assertEqual(r.returncode, 1)
        self.assertIn('không có ký tự nào chung', r.stderr)

    def test_woff2_input(self):
        w = make_font(os.path.join(self.d, 'w.woff2'), {c: 600 for c in LATIN + VIET}, flavor='woff2')
        r = py('fallback_faces.py', '--family', 'Be Test', '--sample', self.sample, '--web', w + '@400', '--fallback-regular', self.fbr, '--fallback-bold', self.fbb)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAlmostEqual(face_values(r.stdout)[0]['sa'], 120.0, delta=0.02)

    def test_help(self):
        r = py('fallback_faces.py', '--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('--family', r.stdout)


class VariableFont(unittest.TestCase):
    """Font biến thiên có trục wght: bề rộng đổi theo độ đậm, script phải khoá wght từng dải."""

    @classmethod
    def setUpClass(cls):
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from fontTools.ttLib.tables.TupleVariation import TupleVariation
        cls.t = tempfile.TemporaryDirectory()
        chars = LATIN
        order = ['.notdef'] + ['g%X' % ord(c) for c in chars]
        fb = FontBuilder(1000, isTTF=True)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap({ord(c): 'g%X' % ord(c) for c in chars})
        empty = TTGlyphPen(None).glyph()
        fb.setupGlyf({g: empty for g in order})
        fb.setupHorizontalMetrics({'.notdef': (500, 0), **{'g%X' % ord(c): (600, 0) for c in chars}})
        fb.setupHorizontalHeader(ascent=900, descent=-200)
        fb.setupNameTable({'familyName': 'Var', 'styleName': 'Regular'})
        fb.setupOS2()
        fb.setupPost()
        fb.setupFvar([('wght', 400, 400, 900, 'Weight')], [])
        # Ở wght 900 mỗi glyph rộng thêm 200: delta phantom point 2 (advance) = +200. Glyph rỗng không có điểm thật, nên 4 điểm phantom.
        var = {g: [TupleVariation({'wght': (0.0, 1.0, 1.0)}, [(0, 0), (200, 0), (0, 0), (0, 0)])] for g in order}
        fb.setupGvar(var)
        cls.path = os.path.join(cls.t.name, 'var.ttf')
        fb.save(cls.path)
        cls.fb = make_font(os.path.join(cls.t.name, 'fb.ttf'), {c: 500 for c in chars})
        cls.sample = os.path.join(cls.t.name, 's.txt')
        with open(cls.sample, 'w') as f:
            f.write('Hello World this is a sample of text for measuring ' * 6)

    @classmethod
    def tearDownClass(cls):
        cls.t.cleanup()

    def test_variable_font_per_weight(self):
        r = py('fallback_faces.py', '--family', 'Var', '--sample', self.sample, '--web', self.path, '--fallback-regular', self.fb, '--fallback-bold', self.fb,
               '--ranges', '100-449:400:r,450-900:900:r')
        self.assertEqual(r.returncode, 0, r.stderr)
        faces = face_values(r.stdout)
        self.assertEqual(len(faces), 2, r.stdout)
        self.assertAlmostEqual(faces[0]['sa'], 120.0, delta=0.05)   # 600/500
        self.assertAlmostEqual(faces[1]['sa'], 160.0, delta=0.05)   # 800/500


if __name__ == '__main__':
    unittest.main()
