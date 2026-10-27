# test_chon_url.py (wp-ucss): luật chọn URL của chon_url.py trên fixture nhỏ (ds, gsc, inv tự viết).
# python3 -I test_chon_url.py → in OK/SAI, mã 1 nếu có ca sai.
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
A, B, C = 'a' * 32, 'b' * 32, 'c' * 32
tmp = tempfile.mkdtemp(prefix='wp-ucss-chon-')
# path: (post_type, danh mục, hash, click, hiển thị, vị trí)
P = {
    '/': ('page', '', A, 100, 5000, 3), '/dich-vu/': ('page', '', A, 50, 3000, 8), '/lien-he/': ('page', '', C, 2, 100, 10),
    '/geo-1/': ('post', 'geo', B, 10, 800, 12), '/geo-2/': ('post', 'geo', B, 0, 50, 30),
    '/seo-1/': ('post', 'seo', B, 40, 2000, 5), '/seo-2/': ('post', 'seo', B, 30, 1500, 9), '/seo-3/': ('post', 'seo', B, 1, 9000, 11),
    '/mkt-1/': ('post', 'marketing', B, 20, 1000, 20), '/mkt-2/': ('post', 'marketing', B, 5, 3000, 14),
    '/bo-qua/': ('post', 'seo', B, 0, 10, 50),
}
json.dump({'rows': [[p, t, c, '', '', 1000] for p, (t, c, *_) in P.items()]}, open(f'{tmp}/ds.json', 'w'))
json.dump({'rows': [{'keys': ['https://example.com' + p], 'clicks': v[3], 'impressions': v[4], 'position': v[5]} for p, v in P.items()]}, open(f'{tmp}/gsc.json', 'w'))
with open(f'{tmp}/inv.jsonl', 'w') as f:
    for p, v in P.items():
        for dev in 'md':
            f.write(json.dumps({'path': p, 'v': dev, 'code': 200, 'final': p, 'css': [v[2]]}) + '\n')
    # Bị loại khỏi tập chọn: redirect, 2 file gộp, mã 404.
    f.write(json.dumps({'path': '/redirect/', 'v': 'm', 'code': 200, 'final': '/khac/', 'css': [A]}) + '\n')
    f.write(json.dumps({'path': '/hai-css/', 'v': 'm', 'code': 200, 'final': '/hai-css/', 'css': [A, C]}) + '\n')
    f.write(json.dumps({'path': '/loi/', 'v': 'm', 'code': 404, 'final': '/loi/', 'css': []}) + '\n')
json.dump({'min_clicks': 5, 'min_impr': 500, 'must': ['/lien-he/', '/bo-qua/', '/loi/', '/redirect/'], 'priority_cats': ['geo'], 'core_cats': ['seo'],
           'top_core': 3, 'top_outer': 1, 'top_impr': 2, 'max_pos': 15, 'extra_per_hash': {B[:8]: 1}, 'skip': ['/bo-qua/']}, open(f'{tmp}/chon.json', 'w'))
r = subprocess.run([sys.executable, '-I', os.path.join(HERE, '..', 'chon_url.py'), f'{tmp}/ds.json', f'{tmp}/gsc.json', f'{tmp}/inv.jsonl', f'{tmp}/out.tsv',
                    '--cfg', f'{tmp}/chon.json'], capture_output=True, text=True)

bad = 0
def ok(name, cond, more=''):
    global bad
    bad += not cond
    print('OK ' if cond else 'SAI', name, '' if cond else more)

ok('chon_url.py chạy', r.returncode == 0, r.stderr[-400:])
rows = [l.split('\t') for l in open(f'{tmp}/out.tsv').read().splitlines()[1:]] if os.path.exists(f'{tmp}/out.tsv') else []
got = [(x[0], x[1]) for x in rows]
want = [('/lien-he/', 'template'), ('/', 'template'), ('/seo-1/', 'template'), ('/seo-2/', 'template'), ('/geo-1/', 'uu-tien'), ('/geo-2/', 'uu-tien'),
        ('/seo-3/', 'core'), ('/mkt-1/', 'outer'), ('/mkt-2/', 'outer')]
ok('đúng 9 URL theo luật, đúng thứ tự và nhóm', got == want, f'\n   có: {got}\n   cần: {want}')
ok('bỏ skip, redirect, 2 file gộp, mã 404', not {'/bo-qua/', '/redirect/', '/hai-css/', '/loi/', '/dich-vu/'} & {p for p, _ in got})
ok('dòng tóm tắt', 'chọn 9 URL' in r.stdout and 'file gộp phủ: 3/3' in r.stdout, r.stdout)
shutil.rmtree(tmp)
sys.exit(1 if bad else 0)
