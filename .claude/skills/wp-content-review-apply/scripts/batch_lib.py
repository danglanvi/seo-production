"""Hàm dùng chung của mark_batch.py và seed_batches.py: đọc kết quả query ArtifactData, chia lô, ghi file lô.
Không chạy trực tiếp. Hai script gọi bằng sys.path của thư mục scripts/ (python3 -I không tự thêm thư mục này).
"""
import json
import os
import re

META_KEYS = {'doc_id', 'id', '_id', 'version', '_version', 'if_version', 'collection', 'createdAt', 'created_at'}
LIST_KEYS = ('documents', 'docs', 'results', 'items', 'data', 'rows')


def parse_docs(obj):
    """Đưa kết quả query hoặc list của ArtifactData về {doc_id: {'version': int|None, 'data': dict}}.
    Nhận: list tài liệu; object có khoá documents/docs/results/items/data/rows là list; object {doc_id: tài liệu}.
    Tài liệu: id ở doc_id, id hoặc _id; version ở version, _version hoặc if_version; dữ liệu ở data hoặc ngay trong tài liệu."""
    if isinstance(obj, dict):
        for k in LIST_KEYS:
            if isinstance(obj.get(k), list):
                obj = obj[k]
                break
        else:
            if obj and all(isinstance(v, dict) for v in obj.values()):
                obj = [dict(v, doc_id=k) if not any(x in v for x in ('doc_id', 'id', '_id')) else v for k, v in obj.items()]
            else:
                raise ValueError('không nhận ra dạng kết quả query')
    if not isinstance(obj, list):
        raise ValueError('không nhận ra dạng kết quả query')
    out = {}
    for d in obj:
        if not isinstance(d, dict):
            continue
        did = d.get('doc_id') or d.get('id') or d.get('_id')
        if not did:
            continue
        ver = d.get('version', d.get('_version', d.get('if_version')))
        data = d['data'] if isinstance(d.get('data'), dict) else {k: v for k, v in d.items() if k not in META_KEYS}
        out[str(did)] = {'version': ver if isinstance(ver, int) else None, 'data': data}
    return out


def safe_name(doc_id):
    return re.sub(r'[^A-Za-z0-9._-]', '_', str(doc_id))


def chunks(items, size, max_bytes=None, sizeof=None):
    """Chia items thành lô tối đa size phần tử và (nếu có) tối đa max_bytes tổng sizeof(item)."""
    batch, total = [], 0
    for it in items:
        b = sizeof(it) if (max_bytes and sizeof) else 0
        if batch and (len(batch) >= size or (max_bytes and total + b > max_bytes)):
            yield batch
            batch, total = [], 0
        batch.append(it)
        total += b
    if batch:
        yield batch


def prepare_out(out_dir, force):
    """Trả None nếu dùng được thư mục ra, hoặc chuỗi lý do nếu có file sẵn mà thiếu --force."""
    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        return 'đường dẫn ra không phải thư mục: ' + out_dir
    if os.path.isdir(out_dir) and os.listdir(out_dir) and not force:
        return 'thư mục ra đã có file: %s (thêm --force để ghi vào)' % out_dir
    return None
