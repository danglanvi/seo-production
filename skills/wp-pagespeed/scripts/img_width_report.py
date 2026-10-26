# Gộp kết quả của img_display_width.mjs và tìm ảnh thừa hoặc thiếu nét. Chỉ đọc file JSON, không gọi mạng, không ghi file.
#   python3 -I "$WPS/scripts/img_width_report.py" ket-qua.json [ket-qua-dpr2.json ...] [--tolerance 1.25] [--min-display 24] [--blur 0.9] [--json] [--strict]
# Với mỗi ảnh (gom theo thuộc tính src) và mỗi viewport có ảnh hiển thị:
#   cần = displayWidth x dpr (px của file cần có), có = fileWidth của currentSrc (px thật của file; thiếu thì dùng naturalWidth), tỉ lệ = có / cần.
#   thừa = tỉ lệ > --tolerance (mặc định 1,25) ở MỌI viewport hiển thị: file nào cũng quá lớn, cần bản nhỏ hơn.
#   thừa một phần = chỉ một số viewport quá lớn (srcset chọn sai hoặc thiếu cỡ ở các viewport đó).
#   mờ = tỉ lệ < --blur (mặc định 0,9) ở ít nhất một viewport: ảnh bị kéo giãn, đừng giảm cỡ.
# KB thừa ước tính = bytes x (1 - (cần / có)^2) ở viewport tệ nhất, giả định dung lượng tỉ lệ với số điểm ảnh. Chỉ là ước lượng để xếp thứ tự.
# Bỏ qua: SVG, ảnh nhỏ hơn --min-display px hiển thị (icon, pixel đếm), ảnh ẩn.
# Mã thoát: 0 xong, 1 có ảnh thừa hoặc mờ khi dùng --strict, 2 file đầu vào thiếu hoặc hỏng.
import argparse
import json
import sys


def die(msg, code=2):
    print('Lỗi: ' + msg, file=sys.stderr)
    sys.exit(code)


ap = argparse.ArgumentParser(description='Gộp kết quả img_display_width.mjs, tìm ảnh thừa hoặc mờ.')
ap.add_argument('files', nargs='+', help='JSON từ img_display_width.mjs (nhiều file, ví dụ dpr 1 và dpr 2)')
ap.add_argument('--tolerance', type=float, default=1.25)
ap.add_argument('--blur', type=float, default=0.9)
ap.add_argument('--min-display', type=float, default=24.0)
ap.add_argument('--json', action='store_true')
ap.add_argument('--strict', action='store_true')
a = ap.parse_args()
if a.tolerance <= 1 or not 0 < a.blur <= 1:
    die('--tolerance phải lớn hơn 1 và --blur trong (0, 1]')

imgs = {}  # (url, src) -> {'obs': [...]}
for path in a.files:
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        vps, dpr = data['viewports'], float(data['dpr'])
    except (OSError, ValueError, KeyError, TypeError) as e:
        die('không đọc được %s: %s' % (path, e))
    for vp in vps:
        for im in vp['images']:
            src = im.get('src') or im.get('currentSrc')
            if not src or str(im.get('currentSrc', src)).split('?')[0].lower().endswith('.svg'):
                continue
            rec = imgs.setdefault((data.get('url', path), src), {'obs': [], 'srcset': im.get('srcsetWidths') or [], 'loading': im.get('loading', '')})
            rec['obs'].append({'vw': vp['vw'], 'inner': vp.get('innerWidth'), 'dpr': dpr, 'disp': im['displayWidth'], 'nat': im.get('fileWidth') or im['naturalWidth'], 'bytes': im.get('bytes', 0),
                               'visible': bool(im.get('visible')), 'cur': im.get('currentSrc', '')})

rows = []
for (url, src), rec in imgs.items():
    seen = [o for o in rec['obs'] if o['visible'] and o['disp'] >= a.min_display and o['nat'] > 0]
    if not seen:
        continue
    for o in seen:
        o['need'] = o['disp'] * o['dpr']
        o['ratio'] = o['nat'] / o['need']
    over = [o for o in seen if o['ratio'] > a.tolerance]
    blur = [o for o in seen if o['ratio'] < a.blur]
    if blur:
        verdict = 'mờ'
    elif len(over) == len(seen):
        verdict = 'thừa'
    elif over:
        verdict = 'thừa một phần'
    else:
        verdict = 'đạt'
    worst = max(seen, key=lambda o: o['ratio'])
    waste = max(0.0, worst['bytes'] * (1 - (worst['need'] / worst['nat']) ** 2)) / 1024.0 if worst['ratio'] > a.tolerance else 0.0
    rows.append({
        'url': url, 'src': src, 'verdict': verdict, 'cần_px_tối_đa': round(max(o['need'] for o in seen)), 'có_px': sorted({o['nat'] for o in seen}),
        'viewport_tệ_nhất': worst['vw'], 'tỉ_lệ_tệ_nhất': round(worst['ratio'], 2), 'kb_thừa_ước_tính': round(waste, 1),
        'viewport_thừa': [o['vw'] for o in over], 'viewport_mờ': [o['vw'] for o in blur], 'srcset_widths': rec['srcset'], 'loading': rec['loading'],
    })
order = {'mờ': 0, 'thừa': 1, 'thừa một phần': 2, 'đạt': 3}
rows.sort(key=lambda r: (order[r['verdict']], -r['kb_thừa_ước_tính']))

if a.json:
    print(json.dumps(rows, ensure_ascii=False, indent=1))
else:
    print('%-13s %-8s %-12s %-9s %s' % ('Kết luận', 'KB thừa', 'Cần px', 'Có px', 'Ảnh (viewport tệ nhất, tỉ lệ)'))
    for r in rows:
        print('%-13s %-8.1f %-12d %-9s %s (vw %s, x%.2f)%s' % (
            r['verdict'], r['kb_thừa_ước_tính'], r['cần_px_tối_đa'], '/'.join(str(x) for x in r['có_px']), r['src'], r['viewport_tệ_nhất'], r['tỉ_lệ_tệ_nhất'],
            ' [lazy]' if r['loading'] == 'lazy' else ''))
bad = [r for r in rows if r['verdict'] != 'đạt']
total = sum(r['kb_thừa_ước_tính'] for r in rows)
print('IMG_WIDTH_REPORT anh=%d thua=%d mo=%d kb_thua=%.1f' % (len(rows), len([r for r in rows if r['verdict'].startswith('thừa')]), len([r for r in rows if r['verdict'] == 'mờ']), total),
      file=sys.stderr if a.json else sys.stdout)
sys.exit(1 if (bad and a.strict) else 0)
