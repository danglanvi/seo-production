#!/usr/bin/env python3
"""test_qa_sau_giao.py (wp-ucss): phân loại link và so robots/canonical của qa_sau_giao.py, không gọi mạng."""
import json, os, sys
T = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(T)
sys.path.insert(0, S)
import qa_sau_giao as qa  # noqa: E402

SITE = json.load(open(os.path.join(S, '..', 'templates', 'site.example.json')))
MAP = os.path.join(T, 'fixtures', 'map-su-co', 'site.php')
q = qa.Qa(SITE, MAP)
p = sorted(q.path_md5)[0]; h = q.path_md5[p]
C = SITE['combined_css_path']
doi = f'<link rel="stylesheet" href="/wp-content/ucss/{h}.abcd1234.css" data-ucss="1" onerror="this.onerror=null;this.href=\'{C}{h}.css?ver=1\'">'
goc = f'<link data-optimized="2" rel="stylesheet" href="{C}{h}.css?ver=1">'
moi = f'<link rel="stylesheet" href="{C}{"f" * 32}.css">'
bad = 0
def ok(name, cond):
    global bad
    bad += 0 if cond else 1
    print('OK ' if cond else 'SAI', name)

ok('link đã đổi: ĐẠT', q.judge(p, 200, p, doi)[0] == 'ĐẠT')
ok('link file gộp có trong map chưa đổi: SAI', q.judge(p, 200, p, goc)[0] == 'SAI')
ok('file gộp mới ngoài map: CẢNH BÁO', q.judge(p, 200, p, moi)[0] == 'CẢNH BÁO')
ok('mã 301 hoặc đổi URL: SAI', q.judge(p, 301, p + 'x/', doi)[0] == 'SAI')
ok('onerror chứa md5 không bị tính là link chưa đổi', q.links(doi) == ([h], []))
rows = [{'path': p, 'v': 'g', 'robots': 'index, follow', 'canonical': 'https://example.com' + p}]
ok('robots/canonical giữ nguyên: không báo', qa.compare(rows, rows) == [])
ok('robots đổi: báo', len(qa.compare(rows, [dict(rows[0], robots='noindex')])) == 1)
sys.exit(1 if bad else 0)
