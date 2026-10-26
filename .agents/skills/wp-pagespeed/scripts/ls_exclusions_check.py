# Kiểm danh sách loại trừ JS của LiteSpeed Cache cho các script phải chạy nguyên trạng (loader GTM hoãn, pixel, chat).
# Chỉ đọc file cấu hình đã xuất. Không gọi mạng, không SSH, không ghi file.
#   python3 -I "$WPS/scripts/ls_exclusions_check.py" --conf <file> --script gtm-delay-loader [--script googletagmanager.com/gtm.js ...]
# Lấy cấu hình trên server (chỉ đọc), mỗi dòng "key<TAB>giá trị JSON":
#   for k in guest optm-js_defer optm-js_defer_exc optm-gm_js_exc; do printf '%s\t' "$k"; <lệnh wp> option get "litespeed.conf.$k" --format=json; done > ls-conf.tsv
# File --conf nhận: JSON object, JSON list {name|key, value}, hoặc dòng "key<TAB>giá trị" / "key=giá trị". Danh sách có thể là mảng hoặc chuỗi nhiều dòng.
# Luật: LiteSpeed Guest Mode (khách mới, lượt xem đầu) dùng danh sách riêng optm-gm_js_exc (filter litespeed_optm_gm_js_exc).
# Danh sách Delay JS thường, optm-js_defer_exc, không áp cho Guest Mode. Script nằm ở danh sách sai thì vẫn bị trễ ở lượt xem đầu.
# Một mục loại trừ khớp khi nó là chuỗi con của chuỗi nhận dạng script (đường dẫn src hoặc đoạn mã inline), giống cách LiteSpeed so khớp.
# Mã thoát: 0 = đạt, 1 = có script chưa được loại trừ ở danh sách đang có hiệu lực, 2 = sai tham số hoặc file cấu hình thiếu key/hỏng.
# Dòng cuối luôn là "LS_EXCL ok" hoặc "LS_EXCL fail".
import argparse
import json
import sys

KEY_GUEST, KEY_DEFER, KEY_DEFER_EXC, KEY_GM_EXC = 'guest', 'optm-js_defer', 'optm-js_defer_exc', 'optm-gm_js_exc'
PREFIX = 'litespeed.conf.'


def die(msg, code=2):
    print('Lỗi: ' + msg, file=sys.stderr)
    print('LS_EXCL fail')
    sys.exit(code)


def parse_value(raw):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def load_conf(path):
    try:
        text = open(path, encoding='utf-8').read()
    except OSError as e:
        die('không đọc được %s: %s' % (path, e))
    conf = {}
    stripped = text.strip()
    if stripped[:1] in '{[':
        try:
            data = json.loads(stripped)
        except ValueError as e:
            die('JSON hỏng trong %s: %s' % (path, e))
        if isinstance(data, dict):
            conf = dict(data)
        else:
            for it in data:
                if isinstance(it, dict) and ('name' in it or 'key' in it):
                    conf[it.get('name', it.get('key'))] = it.get('value')
    else:
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            sep = '\t' if '\t' in ln else '='
            if sep not in ln:
                continue
            k, v = ln.split(sep, 1)
            conf[k.strip()] = parse_value(v)
    return {(k[len(PREFIX):] if str(k).startswith(PREFIX) else str(k)): v for k, v in conf.items()}


def as_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        return [x.strip() for x in v.replace('\\n', '\n').splitlines() if x.strip()]
    return [str(x).strip() for x in v if str(x).strip()]


def truthy(v):
    return str(v).strip().lower() in ('1', 'true', 'on', 'yes', '2')


def matches(entries, script):
    return [e for e in entries if e in script]


ap = argparse.ArgumentParser(description='Kiểm script có nằm trong danh sách loại trừ JS đúng của LiteSpeed (Guest Mode dùng optm-gm_js_exc).')
ap.add_argument('--conf', required=True, help='file cấu hình LiteSpeed đã xuất (JSON hoặc key<TAB>giá trị)')
ap.add_argument('--script', action='append', default=[], help='chuỗi nhận dạng script phải được loại trừ, lặp lại cho nhiều script (mặc định gtm-delay-loader)')
a = ap.parse_args()
scripts = a.script or ['gtm-delay-loader']

conf = load_conf(a.conf)
missing = [k for k in (KEY_GUEST, KEY_DEFER) if k not in conf]
if missing:
    die('file cấu hình thiếu key %s (xuất lại theo hướng dẫn đầu script)' % ', '.join(missing))
guest, defer_mode = truthy(conf[KEY_GUEST]), str(conf[KEY_DEFER]).strip().lower() not in ('0', 'false', 'off', '', 'none')
defer_exc, gm_exc = as_list(conf.get(KEY_DEFER_EXC)), as_list(conf.get(KEY_GM_EXC))

print('guest=%s optm-js_defer=%s | %s: %d mục | %s: %d mục' % (
    'bật' if guest else 'tắt', conf[KEY_DEFER], KEY_DEFER_EXC, len(defer_exc), KEY_GM_EXC, len(gm_exc)))
if not guest and not defer_mode:
    print('Guest Mode và Delay JS đều tắt: không cần loại trừ.')

fail = 0
for s in scripts:
    in_gm, in_defer = matches(gm_exc, s), matches(defer_exc, s)
    if guest:
        if in_gm:
            print('ĐẠT  %s: %s khớp "%s"' % (s, KEY_GM_EXC, in_gm[0]))
        else:
            fail += 1
            hint = ''
            if in_defer:
                hint = ' Script đang nằm ở %s ("%s"), danh sách này không áp cho Guest Mode.' % (KEY_DEFER_EXC, in_defer[0])
            print('LỖI  %s: Guest Mode bật nhưng %s không có mục khớp.%s Thêm "%s" vào %s (filter litespeed_optm_gm_js_exc).' % (s, KEY_GM_EXC, hint, s, KEY_GM_EXC))
    if defer_mode:
        if in_defer:
            print('ĐẠT  %s: %s khớp "%s"' % (s, KEY_DEFER_EXC, in_defer[0]))
        else:
            fail += 1
            print('LỖI  %s: Delay JS bật nhưng %s không có mục khớp. Thêm "%s" vào %s.' % (s, KEY_DEFER_EXC, s, KEY_DEFER_EXC))

print('LS_EXCL fail' if fail else 'LS_EXCL ok')
sys.exit(1 if fail else 0)
