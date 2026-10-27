#!/usr/bin/env python3
"""Test offline cho tools/port_skill.py. Chạy: python3 -B tools/tests/test_port_skill.py"""
import contextlib, io, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import port_skill  # noqa: E402


def skill(root, name, version, files):
    d = Path(root, 'skills', name)
    d.mkdir(parents=True, exist_ok=True)
    head = f'---\nname: {name}\nmetadata:\n  version: "{version}"\n---\n' if version else f'---\nname: {name}\n---\n'
    (d / 'SKILL.md').write_text(head + files.pop('SKILL.md', 'thân'), encoding='utf-8')
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    return d


class PortSkill(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.m, self.d, self.bk = t / 'master', t / 'dich co dau cach', t / 'bk'
        skill(self.m, 'a', '1.2.3', {'SKILL.md': 'mới', 'scripts/x.py': 'x2', 'references/r.md': 'r'})
        (self.m / '_TEMPLATES').mkdir()
        (self.m / '_TEMPLATES' / 'mau.md').write_text('mẫu mới', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def run_port(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = port_skill.main(['--master', str(self.m), '--to', str(self.d), '--backup', str(self.bk), '--skills', 'a', *extra])
        return rc, out.getvalue()

    def test_chay_thu_khong_ghi(self):
        skill(self.d, 'a', '1.2.2', {'SKILL.md': 'cũ', 'scripts/x.py': 'x1'})
        rc, out = self.run_port()
        self.assertEqual(rc, 0)
        self.assertIn('a: chep (2 sửa, 1 mới)', out)
        self.assertFalse((self.d / 'skills/a/references/r.md').exists())

    def test_ghi_va_sao_luu(self):
        skill(self.d, 'a', '1.2.2', {'SKILL.md': 'cũ', 'scripts/x.py': 'x1'})
        rc, _ = self.run_port('--write')
        self.assertEqual(rc, 0)
        self.assertEqual((self.d / 'skills/a/scripts/x.py').read_text(encoding='utf-8'), 'x2')
        self.assertTrue((self.d / 'skills/a/references/r.md').exists())
        self.assertEqual((self.bk / 'dich_co_dau_cach/skills/a/scripts/x.py').read_text(encoding='utf-8'), 'x1')
        self.assertEqual(sorted(p.name for p in (self.d / 'skills').iterdir()), ['a'])  # không tạo thư mục lạ

    def test_chan_dich_co_file_rieng(self):
        skill(self.d, 'a', '1.1', {'references/rieng.md': 'fork'})
        rc, out = self.run_port('--write')
        self.assertEqual(rc, 1)
        self.assertIn('chan:đích có file master không có', out)
        self.assertFalse((self.d / 'skills/a/scripts/x.py').exists())

    def test_chan_khong_version(self):
        # Lỗi thật 27/10/2026: bản semantic-html của repo Content không có version, lineage riêng.
        skill(self.d, 'a', None, {})
        rc, out = self.run_port()
        self.assertEqual(rc, 1)
        self.assertIn('không có version', out)

    def test_chan_cung_version_khac_noi_dung(self):
        skill(self.d, 'a', '1.2.3', {'SKILL.md': 'sửa tại chỗ'})
        rc, out = self.run_port()
        self.assertEqual(rc, 1)
        self.assertIn('≥ master', out)

    def test_ep_cho_chep(self):
        skill(self.d, 'a', None, {})
        rc, _ = self.run_port('--ep', 'a', '--write')
        self.assertEqual(rc, 0)
        self.assertIn('version: "1.2.3"', (self.d / 'skills/a/SKILL.md').read_text(encoding='utf-8'))

    def test_skill_thieu_can_new(self):
        self.d.mkdir()
        rc, out = self.run_port('--write')
        self.assertIn('a: thieu', out)
        self.assertFalse((self.d / 'skills/a').exists())
        rc, out = self.run_port('--write', '--new')
        self.assertTrue((self.d / 'skills/a/SKILL.md').exists())

    def test_extra_bo_qua_dich_khong_phai_instance(self):
        skill(self.d, 'a', '1.2.3', {'SKILL.md': 'mới', 'scripts/x.py': 'x2', 'references/r.md': 'r'})
        (self.d / 'MIGRATION.md').write_text('# MIGRATION của repo khác\n', encoding='utf-8')
        (self.d / '_TEMPLATES').mkdir()
        (self.d / '_TEMPLATES' / 'mau.md').write_text('mẫu của fork', encoding='utf-8')
        rc, out = self.run_port('--extra', '_TEMPLATES/mau.md', '--write')
        self.assertIn('bỏ qua (đích không phải instance của master)', out)
        self.assertEqual((self.d / '_TEMPLATES/mau.md').read_text(encoding='utf-8'), 'mẫu của fork')

    def test_extra(self):
        skill(self.d, 'a', '1.2.3', {'SKILL.md': 'mới', 'scripts/x.py': 'x2', 'references/r.md': 'r'})
        (self.d / 'MIGRATION.md').write_text('---\nmaster_version: v1\n---\n', encoding='utf-8')
        (self.d / '_TEMPLATES').mkdir()
        (self.d / '_TEMPLATES' / 'mau.md').write_text('mẫu cũ', encoding='utf-8')
        rc, out = self.run_port('--extra', '_TEMPLATES/mau.md', '--write')
        self.assertEqual(rc, 0)
        self.assertIn('a: giong', out)
        self.assertEqual((self.d / '_TEMPLATES/mau.md').read_text(encoding='utf-8'), 'mẫu mới')
        self.assertEqual((self.bk / 'dich_co_dau_cach/_TEMPLATES/mau.md').read_text(encoding='utf-8'), 'mẫu cũ')


if __name__ == '__main__':
    unittest.main()
