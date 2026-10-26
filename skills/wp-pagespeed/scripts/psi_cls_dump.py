# Đổ chi tiết CLS từ một file JSON của PSI (hoặc JSON do lh_local.mjs ghi): layout-shifts, cls-culprits-insight, filmstrip, final-screenshot, benchmarkIndex.
# Dùng ở ca "CLS chỉ PSI thấy, perf_probe và cls_trace không tái hiện": xem PSI thật sự thấy gì TRƯỚC khi deploy bản sửa.
#   python3 -I "$WPS/scripts/psi_cls_dump.py" <file PSI .json> [--out <thư mục>] [--top 8]
# Không có --out: chỉ in, không ghi file (dry-run). Có --out: ghi final-screenshot.png, filmstrip-<n>-<ms>ms.png và filmstrip-all.png vào thư mục đó,
# rồi xem ảnh bằng công cụ Read. Cần Pillow để đổi JPEG thành PNG và ghép khung; thiếu Pillow thì ghi .jpg và báo.
# In theo thứ tự: URL và thiết bị, benchmarkIndex (máy PSI nhanh hay chậm), CLS lab, CLS field (CrUX), từng dịch chuyển (selector, điểm, boundingRect,
# nguyên nhân PSI gán). Nguyên nhân "Phông chữ web" chỉ là phỏng đoán theo thời điểm font tải (do-dac.md mục 2): kiểm bằng ảnh và boundingRect.
# Mã thoát: 0 xong (kể cả khi không có dịch chuyển), 1 file hỏng hoặc không có lighthouseResult, 2 sai tham số.
import argparse
import base64
import io
import json
import os
import sys

ap = argparse.ArgumentParser(description='Đổ chi tiết CLS, filmstrip và benchmarkIndex từ một file JSON của PSI.')
ap.add_argument('json_file')
ap.add_argument('--out', help='thư mục ghi PNG (không có thì chỉ in)')
ap.add_argument('--top', type=int, default=8, help='số dịch chuyển in tối đa')
a = ap.parse_args()

try:
    with open(a.json_file, encoding='utf-8') as f:
        j = json.load(f)
except (OSError, ValueError) as e:
    print('Lỗi: không đọc được JSON: %s' % e, file=sys.stderr)
    sys.exit(1)
lr = j.get('lighthouseResult') if isinstance(j, dict) else None
if not lr:
    print('Lỗi: file không có lighthouseResult (PSI lỗi hoặc file cắt dở)', file=sys.stderr)
    sys.exit(1)
au = lr.get('audits', {})


def rect(n):
    r = (n or {}).get('boundingRect') or {}
    if not r:
        return '?'
    return 'top=%s left=%s w=%s h=%s' % (r.get('top'), r.get('left'), r.get('width'), r.get('height'))


def sel(n):
    n = n or {}
    return n.get('selector') or n.get('nodeLabel') or n.get('snippet') or '?'


env = lr.get('environment') or {}
cs = lr.get('configSettings') or {}
print('URL: %s | thiết bị: %s | Lighthouse %s' % (lr.get('finalDisplayedUrl') or lr.get('finalUrl'), cs.get('formFactor'), lr.get('lighthouseVersion')))
bi = env.get('benchmarkIndex')
print('benchmarkIndex: %s%s' % (bi, '' if bi is None else (' (máy chậm, dưới 800)' if bi < 800 else ' (máy nhanh)')))
cls = (au.get('cumulative-layout-shift') or {}).get('numericValue')
print('CLS lab: %s' % ('%.3f' % cls if cls is not None else '?'))
le = j.get('loadingExperience') or {}
m = (le.get('metrics') or {}).get('CUMULATIVE_LAYOUT_SHIFT_SCORE')
if m:
    print('CLS field (CrUX p75, loadingExperience): %.2f, nhóm %s' % (m.get('percentile', 0) / 100.0, m.get('category')))
else:
    print('CLS field (CrUX): không có dữ liệu')

shifts = ((au.get('layout-shifts') or {}).get('details') or {}).get('items') or []
print('\nDịch chuyển (layout-shifts): %d' % len(shifts))
for i, it in enumerate(shifts[:a.top], 1):
    n = it.get('node')
    print('%d. điểm %.3f | %s | %s' % (i, it.get('score', 0), sel(n), rect(n)))
    causes = []
    for sub in ((it.get('subItems') or {}).get('items') or []):
        ex = sub.get('extra') or {}
        causes.append('%s%s' % (sub.get('cause', '?'), (' [%s]' % sel(ex)) if ex.get('selector') or ex.get('nodeLabel') else (' [%s]' % ex.get('value')) if ex.get('value') else ''))
    for c in causes:
        print('     nguyên nhân PSI: %s' % c)
    if any('font' in c.lower() or 'phông' in c.lower() for c in causes):
        print('     lưu ý: "phông chữ" là phỏng đoán theo thời điểm font tải. Xem ảnh filmstrip và boundingRect.')
if len(shifts) > a.top:
    print('... còn %d dịch chuyển nhỏ hơn' % (len(shifts) - a.top))
if not shifts:
    print('PSI không ghi dịch chuyển nào trong lượt này.')

# cls-culprits-insight: gom nguyên nhân theo phần tử
ins = ((au.get('cls-culprits-insight') or {}).get('details') or {})
culprits = []
for tbl in ins.get('items') or []:
    for row in tbl.get('items') or []:
        if row.get('subItems') and row.get('node'):
            culprits.append(row)
if culprits:
    print('\nThủ phạm (cls-culprits-insight): %d' % len(culprits))
    for row in culprits[:a.top]:
        subs = [(s.get('cause'), sel(s.get('extra'))) for s in (row['subItems'].get('items') or [])]
        print('- %s (%.3f): %s' % (sel(row['node']), row.get('score', 0), '; '.join('%s → %s' % (c, s) for c, s in subs)))


def to_bytes(data_uri):
    return base64.b64decode(data_uri.split(',', 1)[1])


fs = (au.get('final-screenshot') or {}).get('details') or {}
thumbs = ((au.get('screenshot-thumbnails') or {}).get('details') or {}).get('items') or []
print('\nẢnh: final-screenshot %s, filmstrip %d khung' % ('có' if fs.get('data') else 'không', len(thumbs)))
if not a.out:
    print('Chưa ghi PNG. Thêm --out <thư mục> để lưu ảnh rồi xem bằng Read.')
    sys.exit(0)

os.makedirs(a.out, exist_ok=True)
try:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        # python3 -I tắt user site-packages, nơi pip install --user đặt Pillow. Thêm lại đường dẫn đó rồi thử một lần nữa.
        import site
        sys.path.append(site.getusersitepackages())
        from PIL import Image, ImageDraw
except ImportError:
    Image = None
    print('Thiếu Pillow: ghi JPEG gốc, không ghép khung (pip install pillow).', file=sys.stderr)


def save(data_uri, stem):
    raw = to_bytes(data_uri)
    if Image is None:
        p = os.path.join(a.out, stem + '.jpg')
        open(p, 'wb').write(raw)
        return p, None
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    p = os.path.join(a.out, stem + '.png')
    im.save(p)
    return p, im


written, frames = [], []
if fs.get('data'):
    written.append(save(fs['data'], 'final-screenshot')[0])
for n, t in enumerate(thumbs, 1):
    if not t.get('data'):
        continue
    p, im = save(t['data'], 'filmstrip-%d-%dms' % (n, round(t.get('timing', 0))))
    written.append(p)
    if im is not None:
        frames.append((im, t.get('timing', 0)))
if frames:
    h = max(im.height for im, _ in frames)
    sheet = Image.new('RGB', (sum(im.width for im, _ in frames) + 4 * (len(frames) - 1), h + 14), 'white')
    x = 0
    d = ImageDraw.Draw(sheet)
    for im, ms in frames:
        sheet.paste(im, (x, 14))
        d.text((x + 2, 1), '%d ms' % round(ms), fill='black')
        x += im.width + 4
    p = os.path.join(a.out, 'filmstrip-all.png')
    sheet.save(p)
    written.append(p)
print('Đã ghi %d ảnh vào %s' % (len(written), a.out))
for p in written:
    print('  ' + p)
