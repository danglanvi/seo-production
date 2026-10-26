# Test offline cho psi_con_tru.py. Ca hỏng thật: site mẫu 2, 18/10/2026. Agent nghiệm thu ở 85 điểm mobile, chỉ đo hạng mục performance,
# không liệt kê phần còn trừ điểm. Người duyệt tự đo, thấy còn việc ở tầng theme và các hạng mục khác, phải phản hồi 3 lượt.
# Script phải báo template chưa đo đủ 5 hạng mục và liệt kê đúng audit có trọng số dưới ngưỡng.
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fixtures import run  # noqa: E402

PERF_REFS = [('first-contentful-paint', 10), ('largest-contentful-paint', 25), ('total-blocking-time', 30),
             ('cumulative-layout-shift', 25), ('speed-index', 10), ('render-blocking-insight', 0)]


def lr(cats, audits, dev='mobile', extra_audits=None):
    """cats: {id: (score, [(audit, weight, group)])}. audits: {id: (score, displayValue, scoreDisplayMode)}."""
    au = {k: {'id': k, 'title': 'Tiêu đề ' + k, 'score': v[0], 'displayValue': v[1], 'scoreDisplayMode': v[2] if len(v) > 2 else 'numeric'}
          for k, v in audits.items()}
    au.update(extra_audits or {})
    categories = {c: {'id': c, 'score': s, 'auditRefs': [{'id': i, 'weight': w, 'group': g} for i, w, g in refs]} for c, (s, refs) in cats.items()}
    return {'lighthouseResult': {'configSettings': {'formFactor': dev}, 'categories': categories, 'audits': au}}


def perf_cat(score):
    return {'performance': (score, [(i, w, 'metrics' if w else 'insights') for i, w in PERF_REFS])}


def perf_audits(tbt, lcp=0.95, rb=1.0):
    return {'first-contentful-paint': (0.98, '0,9 s'), 'largest-contentful-paint': (lcp, '2,1 s'), 'total-blocking-time': (tbt, '%d ms' % int((1 - tbt) * 1000)),
            'cumulative-layout-shift': (1.0, '0'), 'speed-index': (0.97, '1,2 s'), 'render-blocking-insight': (rb, '', 'metricSavings')}


def five_cats(contrast=0.0):
    c = perf_cat(0.85)
    c['accessibility'] = (0.93, [('color-contrast', 7, 'a11y-color-contrast'), ('aria-allowed-attr', 10, 'a11y-aria'), ('bypass', 0, 'hidden')])
    c['best-practices'] = (1.0, [('errors-in-console', 1, 'best-practices-general')])
    c['seo'] = (1.0, [('document-title', 1, 'seo-content')])
    c['agentic-browsing'] = (1.0, [('llms-txt', 0, 'agent-discoverability')])
    a = perf_audits(0.6)
    a.update({'color-contrast': (contrast, ''), 'aria-allowed-attr': (1.0, ''), 'bypass': (0.0, ''), 'errors-in-console': (1.0, ''),
              'document-title': (1.0, ''), 'llms-txt': (0.0, '')})
    return c, a


def write(d, name, obj):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f)


class ConTru(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.perf = os.path.join(self.t.name, 'psi-final')
        self.cat5 = os.path.join(self.t.name, 'psi-final-5hm')

    def tearDown(self):
        self.t.cleanup()

    def js(self, *argv):
        r = run('psi_con_tru.py', *argv, '--json')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.strip().splitlines()
        self.assertTrue(lines[-1].startswith('CON_TRU '), r.stdout)
        return json.loads(lines[0]), lines[-1]

    def test_ca_that_chi_do_performance(self):
        # Ca 18/10: chỉ có 3 lượt performance. Script phải báo thiếu 4 hạng mục.
        for k, tbt in enumerate([0.5, 0.6, 0.95], 1):
            write(self.perf, 'home_mobile_run%d.json' % k, lr(perf_cat(0.85), perf_audits(tbt)))
        r = run('psi_con_tru.py', self.perf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('CHƯA ĐO ĐỦ 5 HẠNG MỤC', r.stdout)
        self.assertIn('home mobile: thiếu accessibility, best-practices, seo, agentic-browsing', r.stdout)
        self.assertTrue(r.stdout.strip().endswith('CON_TRU dong=1 thieu_hang_muc=1'), r.stdout)
        # TBT trung vị 0,6 dưới ngưỡng ở 2/3 lượt, LCP 0,95 không vào bảng.
        self.assertIn('`total-blocking-time`', r.stdout)
        self.assertIn('| 0,60 | 2/3 |', r.stdout)
        self.assertNotIn('`largest-contentful-paint`', r.stdout)

    def test_gop_hai_thu_muc_du_5_hang_muc(self):
        for k, tbt in enumerate([0.5, 0.6, 0.95], 1):
            write(self.perf, 'home_mobile_run%d.json' % k, lr(perf_cat(0.85), perf_audits(tbt)))
        c, a = five_cats()
        write(self.cat5, 'home_mobile_run1.json', lr(c, a))
        out, last = self.js(self.perf, self.cat5)
        self.assertEqual(last, 'CON_TRU dong=2 thieu_hang_muc=0')
        self.assertEqual(out['thieu'], [])
        self.assertEqual([(x['hang_muc'], x['audit']) for x in out['con_tru']], [('performance', 'total-blocking-time'), ('accessibility', 'color-contrast')])
        # Audit trọng số 0 (llms-txt) và nhóm hidden (bypass) không phải phần trừ điểm.
        ids = {x['audit'] for x in out['con_tru']}
        self.assertNotIn('llms-txt', ids)
        self.assertNotIn('bypass', ids)
        self.assertEqual(out['hang_muc'][0]['luot'], 4)
        self.assertAlmostEqual(out['hang_muc'][0]['diem']['accessibility'], 0.93)

    def test_gop_vong_xen_ke_va_file_khong_hau_to(self):
        write(self.perf, 'lien-he-r1_mobile_run1.json', lr(perf_cat(0.9), perf_audits(0.95)))
        write(self.perf, 'lien-he-r2_mobile_run1.json', lr(perf_cat(0.92), perf_audits(0.97)))
        c, a = five_cats(contrast=1.0)
        write(self.cat5, 'lien-he.json', lr(c, a, dev='desktop'))
        out, _ = self.js(self.perf, self.cat5)
        got = {(x['template'], x['dev']): x['luot'] for x in out['hang_muc']}
        self.assertEqual(got, {('lien-he', 'mobile'): 2, ('lien-he', 'desktop'): 1})

    def test_diag_them_audit_chan_doan(self):
        write(self.perf, 'home_mobile_run1.json', lr(perf_cat(0.95), perf_audits(0.95, rb=0.5)))
        out, _ = self.js(self.perf)
        self.assertEqual(out['con_tru'], [])
        out, _ = self.js(self.perf, '--diag')
        self.assertEqual([x['audit'] for x in out['con_tru']], ['render-blocking-insight'])

    def test_mt_trung_vi(self):
        for k, (sl, kb) in enumerate([(600, 100), (400, 120), (500, 110)], 1):
            extra = {'mainthread-work-breakdown': {'details': {'items': [{'group': 'styleLayout', 'duration': sl}, {'group': 'scriptEvaluation', 'duration': 200}]}},
                     'network-requests': {'details': {'items': [{'resourceType': 'Font', 'transferSize': kb * 1024}, {'resourceType': 'Script', 'transferSize': 9000}]}},
                     'render-blocking-insight': {'score': 1, 'details': {'items': [{'url': 'a.css'}]}},
                     'total-blocking-time': {'score': 0.9, 'numericValue': 150 + k}}
            write(self.perf, 'home_mobile_run%d.json' % k, lr(perf_cat(0.9), perf_audits(0.9), extra_audits=extra))
        out, _ = self.js(self.perf, '--mt')
        m = out['mt'][0]
        self.assertEqual((m['style_layout_ms'], m['script_ms'], m['font_kb'], m['font_file'], m['chan_hien_thi'], m['tbt_ms']), (500, 200, 110, 1, 1, 152))

    def test_thu_tu_theo_urls(self):
        for n in ('blog', 'home'):
            write(self.perf, '%s_mobile_run1.json' % n, lr(perf_cat(0.9), perf_audits(0.95)))
        u = os.path.join(self.t.name, 'urls.tsv')
        with open(u, 'w') as f:
            f.write('home\thttps://site-a.example/\nblog\thttps://site-a.example/blog/\n')
        out, _ = self.js(self.perf, '--urls', u)
        self.assertEqual([x['template'] for x in out['hang_muc']], ['home', 'blog'])

    def test_dau_vao_hong(self):
        os.makedirs(self.perf)
        with open(os.path.join(self.perf, 'home_mobile_run1.json'), 'w') as f:
            f.write('{cắt dở')
        write(self.perf, 'spec.json', {'pages': {}})
        r = run('psi_con_tru.py', self.perf)
        self.assertEqual(r.returncode, 1)
        self.assertIn('bỏ qua 2 file', r.stderr)
        self.assertEqual(run('psi_con_tru.py', os.path.join(self.t.name, 'khong-co')).returncode, 2)
        self.assertEqual(run('psi_con_tru.py', self.perf, '--thr', '0').returncode, 2)
        # File hỏng nằm cạnh file tốt: vẫn chạy, báo số file bỏ qua.
        write(self.perf, 'blog_mobile_run1.json', lr(perf_cat(0.9), perf_audits(0.95)))
        r = run('psi_con_tru.py', self.perf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Bỏ qua 2 file', r.stdout)


if __name__ == '__main__':
    unittest.main()
