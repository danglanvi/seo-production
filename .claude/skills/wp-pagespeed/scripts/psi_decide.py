# Quyết định A/B trên PSI trong nhiễu: so nhánh A (gốc) với nhánh B (thử), trả đúng một nhãn.
# Chỉ đọc file JSON do psi_run.py ghi. Không gọi mạng, không ghi file.
#   python3 -I "$WPS/scripts/psi_decide.py" <psi-dir> --a v0 --b v4 [--dev mobile] [--page <tên>] [--max-runs 5] [--json]
#   python3 -I "$WPS/scripts/psi_decide.py" --a-dir <psi-A> --b-dir <psi-B>      (hai thư mục psi_run, ghép theo <tên>_<thiết bị>)
# Tên file kiểu psi_ab: <trang>-<biến thể>-r<k>_<thiết bị>_run1.json (k là vòng xen kẽ).
# Nhãn: tốt hơn | không đổi | xấu hơn | chưa đủ lượt. Dòng cuối luôn là "PSI_DECIDE label=<...>".
# Ngưỡng mặc định (site agency mẫu 10/2026, hiệu chuẩn lại ở site khác): --min-gain 3 điểm, --lcp-ms 200, --cls 0.02.
# Đặt ngưỡng TRƯỚC khi đo, không sửa sau khi thấy số. Lệch máy PSI (benchmarkIndex) lớn hơn 20% thì chỉ so trong nhóm máy chung.
# Mã thoát: 0 = có nhãn tốt hơn, không đổi hoặc xấu hơn; 3 = chưa đủ lượt, đo thêm; 1 = dữ liệu hỏng hoặc thiếu; 2 = sai tham số.
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_lib as L  # noqa: E402

ap = argparse.ArgumentParser(description='Quyết định A/B trên PSI: tốt hơn, không đổi, xấu hơn hoặc chưa đủ lượt.')
ap.add_argument('psi_dir', nargs='?', help='thư mục JSON của psi_run (tên kiểu psi_ab)')
ap.add_argument('--a', help='biến thể gốc, ví dụ v0')
ap.add_argument('--b', help='biến thể thử, ví dụ v4')
ap.add_argument('--a-dir', help='thư mục nhánh A (thay cho psi_dir)')
ap.add_argument('--b-dir', help='thư mục nhánh B (thay cho psi_dir)')
ap.add_argument('--dev', default='mobile', choices=['mobile', 'desktop'])
ap.add_argument('--page', help='chỉ xét một trang')
ap.add_argument('--max-runs', type=int, default=L.DEFAULT_THR['max_runs'])
ap.add_argument('--min-runs', type=int, default=L.DEFAULT_THR['min_runs'])
ap.add_argument('--min-gain', type=float, default=L.DEFAULT_THR['min_gain'])
ap.add_argument('--lcp-ms', type=float, default=L.DEFAULT_THR['lcp_ms'])
ap.add_argument('--cls', type=float, default=L.DEFAULT_THR['cls'])
ap.add_argument('--bench-gap', type=float, default=L.DEFAULT_THR['bench_gap'])
ap.add_argument('--json', action='store_true', help='in kết quả dạng JSON')
a = ap.parse_args()

thr = {'min_gain': a.min_gain, 'lcp_ms': a.lcp_ms, 'cls': a.cls, 'max_runs': a.max_runs, 'min_runs': a.min_runs, 'bench_gap': a.bench_gap}


def die(msg, code=1):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


groups = {}  # page -> {'A': [runs], 'B': [runs]}
try:
    if a.a_dir or a.b_dir:
        if not (a.a_dir and a.b_dir):
            die('cần cả --a-dir và --b-dir', 2)
        for side, d in (('A', a.a_dir), ('B', a.b_dir)):
            for f in sorted(glob.glob(os.path.join(d, '*_%s_run*.json' % a.dev))):
                base = os.path.basename(f)
                page = base.split('_%s_run' % a.dev)[0]
                r = L.load_run(f)
                r['k'] = int(base.rsplit('_run', 1)[1].split('.')[0])
                groups.setdefault(page, {'A': [], 'B': []})[side].append(r)
    else:
        if not (a.psi_dir and a.a and a.b):
            die('cần <psi-dir> --a <biến thể> --b <biến thể>, hoặc --a-dir và --b-dir', 2)
        if a.a == a.b:
            die('--a và --b phải khác nhau', 2)
        if not os.path.isdir(a.psi_dir):
            die('không thấy thư mục ' + a.psi_dir)
        for f in sorted(glob.glob(os.path.join(a.psi_dir, '*.json'))):
            p = L.parse_ab_name(os.path.basename(f))
            if not p or p['dev'] != a.dev or p['var'] not in (a.a, a.b):
                continue
            r = L.load_run(f)
            r['k'] = int(p['k'])
            groups.setdefault(p['page'], {'A': [], 'B': []})['A' if p['var'] == a.a else 'B'].append(r)
except ValueError as e:
    die(str(e))

if a.page:
    groups = {k: v for k, v in groups.items() if k == a.page}
if not groups:
    die('không có file PSI khớp (thiết bị %s, A=%s, B=%s). Kiểm tên file và --dev' % (a.dev, a.a or a.a_dir, a.b or a.b_dir))

results = {}
for page in sorted(groups):
    results[page] = L.decide(groups[page]['A'], groups[page]['B'], thr)

labels = [r['label'] for r in results.values()]
if 'worse' in labels:
    overall = 'worse'
elif 'more' in labels:
    overall = 'more'
elif 'better' in labels:
    overall = 'better'
else:
    overall = 'same'

if a.json:
    print(json.dumps({'overall': overall, 'pages': results}, ensure_ascii=False, indent=1, default=str))
else:
    print('thiết bị %s | ngưỡng: điểm %.1f, LCP %.0f ms, CLS %.3f, %d-%d lượt mỗi nhánh' % (a.dev, thr['min_gain'], thr['lcp_ms'], thr['cls'], thr['min_runs'], thr['max_runs']))
    print('trang | nA/nB | điểm A→B | benchmarkIndex A/B | LCP Δ ms | CLS Δ | nhãn | lý do')
    for page, r in results.items():
        f = lambda k, fmt: (fmt % r[k]) if r.get(k) is not None else '–'
        print('%s | %d/%d | %s→%s | %s/%s | %s | %s | %s | %s%s' % (
            page, r['nA'], r['nB'], f('scoreA', '%.1f'), f('scoreB', '%.1f'), f('benchA', '%.0f'), f('benchB', '%.0f'),
            f('dLcp', '%+.0f'), f('dCls', '%+.3f'), L.LABELS[r['label']], r['reason'], ('; ' + r['note']) if r['note'] else ''))
    print('PSI_DECIDE label=%s (%s)' % (overall, L.LABELS[overall]))

sys.exit(3 if overall == 'more' else 0)
