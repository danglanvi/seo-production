#!/usr/bin/env python3
"""Dựng các lô ArtifactData set để nạp tài liệu report hoặc pages lên trang duyệt. Chỉ đọc và ghi file local.
Script không gọi ArtifactData. Dùng cho đợt nạp lớn: chỉ nạp tài liệu còn thiếu thay vì nạp lại cả collection.

python3 -I seed_batches.py --docs <thư mục tài liệu> --collection report --remote <list.json | thư mục>
                           [--only-missing] [--out <thư mục ra>] [--batch-size 50] [--max-bytes 400000]
                           [--ghi] [--force] [--json]

--docs: thư mục có <doc_id>.json cho mỗi tài liệu cần nạp (ví dụ meta.json, links.json, summary.json).
--collection: report hoặc pages. Collection reviews và edits là dữ liệu của người duyệt: script từ chối.
--remote: kết quả ArtifactData list hoặc query của cùng collection (file JSON), hoặc thư mục file <doc_id>.json do list --out_dir ghi.
          Dạng file JSON có version cho từng tài liệu. Dạng thư mục không có version.
Mặc định:
  tài liệu chưa có trên trang     -> set.
  tài liệu có trên trang, giống   -> bỏ.
  tài liệu có trên trang, khác    -> set kèm if_version. Thiếu version thì báo lỗi, không đoán.
--only-missing: chỉ nạp tài liệu chưa có trên trang. Tài liệu đã có, dù khác, đều bỏ.
Tài liệu trên 256 KiB báo lỗi: chia thành hai phần trước. Lô chia theo --batch-size lệnh và --max-bytes tổng dung lượng file.
Đầu ra (khi có --ghi): _writes_NN.json trong --out (mặc định thư mục cạnh --docs tên _seed). Mỗi lệnh
{op: set, collection, doc_id, file_path[, if_version]}. file_path là đường dẫn tuyệt đối của file trong --docs.
Không có --ghi: chạy thử, chỉ in kế hoạch. Luôn in số lô, tức số hộp duyệt Vincent phải bấm.
Mã thoát: 0 chạy được, 1 có lỗi dữ liệu, 2 sai đầu vào hoặc thư mục ra đã có file.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_lib  # noqa: E402

MAX_DOC = 256 * 1024
FORBIDDEN = {'reviews', 'edits'}


def load_local(docs_dir):
    docs, errors = {}, []
    for fp in sorted(glob.glob(os.path.join(docs_dir, '*.json'))):
        name = os.path.splitext(os.path.basename(fp))[0]
        if name.startswith('_'):
            continue
        raw = open(fp, 'rb').read()
        if len(raw) > MAX_DOC:
            errors.append('%s: %d KiB vượt 256 KiB, chia thành hai phần' % (name, len(raw) // 1024))
            continue
        try:
            d = json.loads(raw.decode('utf-8'))
        except ValueError as e:
            errors.append('%s: không phải JSON: %s' % (name, e))
            continue
        d = d.get('data', d) if isinstance(d, dict) and set(d) <= {'data', 'version', 'doc_id', 'id'} else d
        docs[name] = {'path': os.path.abspath(fp), 'data': d, 'bytes': len(raw)}
    return docs, errors


def load_remote(path):
    if os.path.isdir(path):
        out = {}
        for fp in glob.glob(os.path.join(path, '*.json')):
            d = json.load(open(fp, encoding='utf-8'))
            out[os.path.splitext(os.path.basename(fp))[0]] = {'version': d.get('version') if isinstance(d, dict) and isinstance(d.get('version'), int) else None,
                                                              'data': d.get('data', d) if isinstance(d, dict) else d}
        return out
    return batch_lib.parse_docs(json.load(open(path, encoding='utf-8')))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Dựng lô set cho report hoặc pages. Xem docstring đầu file.')
    ap.add_argument('--docs', required=True)
    ap.add_argument('--collection', required=True)
    ap.add_argument('--remote', required=True)
    ap.add_argument('--only-missing', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--batch-size', type=int, default=50)
    ap.add_argument('--max-bytes', type=int, default=400000)
    ap.add_argument('--ghi', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if a.collection in FORBIDDEN:
        print('Collection %s là dữ liệu của người duyệt, không nạp bằng script này.' % a.collection, file=sys.stderr)
        return 2
    if not os.path.isdir(a.docs) or not os.path.exists(a.remote) or a.batch_size < 1:
        print('Thiếu thư mục --docs, --remote hoặc --batch-size sai', file=sys.stderr)
        return 2
    try:
        remote = load_remote(a.remote)
    except (OSError, ValueError) as e:
        print('Không đọc được --remote: %s' % e, file=sys.stderr)
        return 2
    local, errors = load_local(a.docs)
    out_dir = os.path.abspath(a.out or os.path.join(os.path.dirname(os.path.abspath(a.docs)), '_seed'))
    if a.ghi:
        why = batch_lib.prepare_out(out_dir, a.force)
        if why:
            print(why, file=sys.stderr)
            return 2
    plan, skipped = [], []
    for name, d in local.items():
        r = remote.get(name)
        if r is None:
            plan.append({'id': name, 'path': d['path'], 'bytes': d['bytes'], 'version': None, 'lydo': 'thiếu trên trang'})
        elif a.only_missing:
            skipped.append({'id': name, 'ly_do': 'đã có trên trang (--only-missing)'})
        elif r['data'] == d['data']:
            skipped.append({'id': name, 'ly_do': 'giống bản trên trang'})
        elif r['version'] is None:
            errors.append('%s: khác bản trên trang nhưng không có version, không đặt được if_version' % name)
        else:
            plan.append({'id': name, 'path': d['path'], 'bytes': d['bytes'], 'version': r['version'], 'lydo': 'khác bản trên trang'})
    batches = list(batch_lib.chunks(plan, a.batch_size, a.max_bytes, lambda p: p['bytes']))
    res = {'nap': len(plan), 'bo': skipped, 'so_lo': len(batches), 'so_hop_duyet': len(batches), 'loi': errors, 'da_ghi': False,
           'out': out_dir if a.ghi else None}
    if a.ghi and plan and not errors:
        os.makedirs(out_dir, exist_ok=True)
        for n, b in enumerate(batches, 1):
            writes = []
            for p in b:
                w = {'op': 'set', 'collection': a.collection, 'doc_id': p['id'], 'file_path': p['path']}
                if p['version'] is not None:
                    w['if_version'] = p['version']
                writes.append(w)
            with open(os.path.join(out_dir, '_writes_%02d.json' % n), 'w', encoding='utf-8') as f:
                json.dump(writes, f, ensure_ascii=False, indent=1)
        res['da_ghi'] = True
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print('Vincent phải bấm %d hộp duyệt (%d lô, %d tài liệu).' % (len(batches), len(batches), len(plan)))
        for s in skipped:
            print('BỎ %s: %s' % (s['id'], s['ly_do']))
        for e in errors:
            print('LỖI %s' % e)
        for n, b in enumerate(batches, 1):
            print('lô %02d: %d tài liệu, %d KiB' % (n, len(b), sum(p['bytes'] for p in b) // 1024))
        print('Đã ghi vào %s' % out_dir if res['da_ghi'] else ('Chạy thử, chưa ghi file. Thêm --ghi để ghi.' if not errors else 'Có lỗi, chưa ghi file.'))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
