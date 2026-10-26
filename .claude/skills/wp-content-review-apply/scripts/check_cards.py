#!/usr/bin/env python3
"""Lint thẻ duyệt trước khi nạp lên trang duyệt (ArtifactData set). Chỉ đọc file local.

python3 -I check_cards.py <thư mục report> [--reviews <thư mục reviews>] [--json]

<thư mục report>: mỗi file *.json là một tài liệu phần ({"intro", "items": [...]}) hoặc summary.json ({"sections": [...]}).
Lỗi (thoát mã 1), nạp thẻ sẽ làm trang duyệt hỏng:
  - thẻ thiếu id, hoặc hai thẻ cùng id (trong một phần hoặc giữa hai phần);
  - hai trường cùng key trong một thẻ (values lưu đè nhau: mọi ô hiện cùng một chữ). Builder phải đặt key#n;
  - trường thiếu key hoặc thiếu before;
  - trường có phương án A hoặc B mà thẻ và phần đều không có options (trang chỉ hiện A);
  - trường dùng phương án không có trong options;
  - tài liệu quá 256 KiB (giới hạn của db).
  - với --reviews: file thiếu item_id, hoặc status lạ (bộ đếm trên trang bỏ qua status lạ).
Cảnh báo (không đổi mã thoát):
  - thẻ không có fields; trường có target mặc định mà thẻ thiếu post_id (plan.py sẽ bỏ);
  - phần trong summary không có tài liệu, tài liệu có thẻ mà summary không liệt kê, count lệch số thẻ;
  - tài liệu quá 200 KiB;
  - với --reviews: kết quả duyệt của thẻ không có trong report; values có khoá không thuộc trường nào của thẻ.
Thoát mã 2 khi sai đầu vào.
"""
import argparse
import glob
import json
import os
import sys

STATUSES = {'pending', 'approved', 'edited', 'rejected', 'applied'}
DEFAULT_KEYS = {'seo_title', 'meta', 'h1', 'slug'}
MAX_DOC = 256 * 1024
WARN_DOC = 200 * 1024


def fid_keys(fields):
    seen, out = {}, []
    for f in fields:
        k = f.get('key')
        seen[k] = seen.get(k, 0) + 1
        out.append(k if seen[k] == 1 else '%s#%d' % (k, seen[k]))
    return out


def lint(report_dir, reviews_dir=None):
    errors, warns = [], []
    E = lambda where, msg: errors.append({'where': where, 'msg': msg})
    W = lambda where, msg: warns.append({'where': where, 'msg': msg})
    docs = {}
    for f in sorted(glob.glob(os.path.join(report_dir, '*.json'))):
        name = os.path.splitext(os.path.basename(f))[0]
        raw = open(f, 'rb').read()
        try:
            d = json.loads(raw.decode('utf-8'))
        except ValueError as e:
            E(name, 'không phải JSON hợp lệ: %s' % e)
            continue
        d = d.get('data', d) if isinstance(d, dict) else d
        if not isinstance(d, dict):
            E(name, 'tài liệu phải là object')
            continue
        docs[name] = d
        if len(raw) > MAX_DOC:
            E(name, 'tài liệu %d KiB vượt 256 KiB, chia thành hai phần' % (len(raw) // 1024))
        elif len(raw) > WARN_DOC:
            W(name, 'tài liệu %d KiB, gần giới hạn 256 KiB' % (len(raw) // 1024))
    ids, item_fields = {}, {}
    for name, d in docs.items():
        if name == 'summary':
            continue
        sec_opts = d.get('options') or []
        for n, it in enumerate(d.get('items') or []):
            iid = it.get('id')
            where = '%s#%d' % (name, n) if not iid else '%s/%s' % (name, iid)
            if not iid:
                E(where, 'thẻ thiếu id')
                continue
            if iid in ids:
                E(where, 'id trùng với thẻ ở %s' % ids[iid])
            ids.setdefault(iid, name)
            fields = it.get('fields')
            if not fields:
                W(where, 'thẻ không có fields')
                fields = []
            item_fields[iid] = fid_keys(fields)
            keys = [f.get('key') for f in fields]
            for k in sorted({k for k in keys if k is not None and keys.count(k) > 1}):
                E(where, 'có %d trường cùng key "%s": đặt key#n cho từng trường' % (keys.count(k), k))
            opts = it.get('options') or sec_opts
            opt_keys = {o.get('key') for o in opts}
            for f in fields:
                if f.get('key') is None:
                    E(where, 'trường thiếu key')
                    continue
                if 'before' not in f:
                    E(where, 'trường "%s" thiếu before' % f['key'])
                used = [k for k in ('A', 'B') if k in f]
                if used and not opts:
                    E(where, 'trường "%s" có phương án %s nhưng thẻ và phần không có options: trang chỉ hiện A' % (f['key'], '/'.join(used)))
                for k in used:
                    if opts and k not in opt_keys:
                        E(where, 'trường "%s" dùng phương án %s không có trong options' % (f['key'], k))
                if f['key'].split('#')[0] in DEFAULT_KEYS and not f.get('target') and not it.get('post_id'):
                    W(where, 'trường "%s" ghi theo target mặc định nhưng thẻ thiếu post_id' % f['key'])
    summ = docs.get('summary')
    if summ is not None:
        listed = {}
        for s in summ.get('sections') or []:
            listed[s.get('key')] = s
        for k, s in listed.items():
            if k not in docs:
                W('summary', 'phần "%s" không có tài liệu report/%s' % (k, k))
            elif s.get('count') is not None and s['count'] != len(docs[k].get('items') or []):
                W('summary', 'phần "%s" ghi count=%s nhưng có %d thẻ' % (k, s['count'], len(docs[k].get('items') or [])))
        for k, d in docs.items():
            if k != 'summary' and (d.get('items') or []) and k not in listed:
                W('summary', 'tài liệu "%s" có %d thẻ mà summary không liệt kê' % (k, len(d['items'])))
    if reviews_dir:
        for f in sorted(glob.glob(os.path.join(reviews_dir, '*.json'))):
            stem = os.path.splitext(os.path.basename(f))[0]
            try:
                d = json.load(open(f, encoding='utf-8'))
            except ValueError as e:
                E('reviews/' + stem, 'không phải JSON hợp lệ: %s' % e)
                continue
            d = d.get('data', d) if isinstance(d, dict) else {}
            iid = d.get('item_id')
            if not iid:
                E('reviews/' + stem, 'thiếu item_id')
                continue
            if d.get('status') not in STATUSES:
                E('reviews/' + iid, 'status lạ "%s": bộ đếm trên trang bỏ qua' % d.get('status'))
            if iid not in ids:
                W('reviews/' + iid, 'thẻ không có trong report')
                continue
            known = set(item_fields[iid])
            extra = [k for k in (d.get('values') or {}) if k not in known]
            if extra:
                W('reviews/' + iid, 'values có khoá không thuộc trường nào của thẻ: %s' % ', '.join(extra))
    return errors, warns, {'docs': len(docs), 'items': len(ids)}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Lint thẻ duyệt. Xem docstring đầu file.')
    ap.add_argument('report')
    ap.add_argument('--reviews')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    for d in (a.report, a.reviews):
        if d and not os.path.isdir(d):
            print('Không có thư mục ' + d, file=sys.stderr)
            return 2
    errors, warns, stat = lint(a.report, a.reviews)
    if a.json:
        print(json.dumps({'errors': errors, 'warnings': warns, **stat}, ensure_ascii=False, indent=1))
    else:
        for e in errors:
            print('LỖI  %s: %s' % (e['where'], e['msg']))
        for w in warns:
            print('CẢNH BÁO %s: %s' % (w['where'], w['msg']))
        print('%d tài liệu, %d thẻ, %d lỗi, %d cảnh báo' % (stat['docs'], stat['items'], len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
