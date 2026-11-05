import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).resolve().parents[1] / 'inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    base = '/wp-content/litespeed/css/'
    a = '45d6c438acad4c2cf9a612a07dbd8e2a'
    b = 'dce389fffbe7e8a95644e7bbd613db26'

    def hashes(self, html):
        return inventory.css_hashes(html, self.base)

    def test_combined_link(self):
        self.assertEqual(self.hashes(f'<link rel="preload" as="style" href="https://cdn.example{self.base}{self.a}.css?ver=1&amp;x=2">'), [self.a])

    def test_inline_site_prefixed_marker_and_attribute_order(self):
        self.assertEqual(self.hashes(f"<style data-vidu-h='{self.a}' data-no-optimize='1' id='vidu-ucss-inline'>body{{color:red}}</style>"), [self.a])

    def test_inline_template_marker(self):
        self.assertEqual(self.hashes(f'<style id="ucss-inline" data-ucss-h="{self.a}"></style>'), [self.a])

    def test_same_hash_deduplicated(self):
        html = f'<link href="{self.base}{self.a}.css"><style id="vidu-ucss-inline" data-vidu-h="{self.a}"></style>'
        self.assertEqual(self.hashes(html), [self.a])

    def test_ambiguous_hashes_preserved(self):
        html = f'<link href="{self.base}{self.a}.css"><style id="vidu-ucss-inline" data-vidu-h="{self.b}"></style>'
        self.assertEqual(self.hashes(html), [self.a, self.b])

    def test_swapped_link_template_marker(self):
        # Đúng chuỗi templates/ucss-swap.php sinh ra.
        html = f"<link rel='stylesheet' href='/wp-content/ucss/{self.a}.12345678.css' data-ucss=\"1\" onerror=\"this.onerror=null;this.href='/wp-content/litespeed/css/{self.a}.css?ver=1'\">"
        self.assertEqual(self.hashes(html), [self.a])

    def test_swapped_link_site_prefixed_marker(self):
        html = f"<link rel='stylesheet' href='/wp-content/vidu-ucss/{self.a}.12345678.css' data-vidu-ucss='1' onerror=\"this.onerror=null;this.href='/wp-content/litespeed/css/{self.a}.css?ver=1&amp;x=2'\">"
        self.assertEqual(self.hashes(html), [self.a])

    def test_no_unmarked_fallback_or_unrelated_js(self):
        html = f"<link onerror=\"this.href='{self.base}{self.a}.css'\"><link data-ucss='1' onerror=\"console.log('{self.base}{self.a}.css')\">"
        self.assertEqual(self.hashes(html), [])

    def test_not_evidence_in_text_comment_or_other_style(self):
        html = f'<!-- <link href="{self.base}{self.a}.css"> --><script>var url="{self.base}{self.a}.css";</script><style data-vidu-h="{self.a}" id="other"></style>'
        self.assertEqual(self.hashes(html), [])


if __name__ == '__main__':
    unittest.main()
