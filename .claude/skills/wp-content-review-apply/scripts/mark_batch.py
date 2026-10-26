#!/usr/bin/env python3
"""Dựng các lô ArtifactData update để gắn "đã áp" (status applied) cho thẻ duyệt. Chỉ đọc và ghi file local.
Script không gọi ArtifactData. Agent chính chạy từng lô sau khi Vincent vừa nhắn.

python3 -I mark_batch.py --lane <thư mục lane> [--lane ...] --versions <query.json>
                         [--so-id ~/.cm/ma/applied-ids.txt] [--out ~/.cm/ma/b<hhmm>] [--batch-size 50]
                         [--now 2026-10-25T09:30:00Z] [--ghi] [--force] [--json]

Đầu vào:
  --lane: thư mục lane có mark_applied.json ([{"id", "status": "applied", "note"}]) và kiem-doc-lap*.md.
          Chỉ lấy lane mà kết luận trong kiem-doc-lap (file mới nhất theo giờ sửa, mục "Kết luận" cuối cùng) là đạt.
          Kết luận không đạt, chưa đạt, đạt có điều kiện, hoặc không đọc ra kết luận: bỏ cả lane.
          Một id lệch trong lane không đạt thì sửa mark_applied.json (bỏ id đó) và kiểm độc lập lại.
  --versions: kết quả MỘT lần query collection reviews với status in [approved, edited], limit 1000, lưu ra file JSON.
          Không get từng thẻ, không query "__name__ in". Thẻ không có trong file này (pending, rejected, đã applied) bị bỏ.
  --so-id: sổ id đã gắn. Mặc định ~/.cm/ma/applied-ids.txt. Id có trong sổ bị bỏ.
Mỗi thẻ ra một lệnh update {status: applied, appliedAt, note}. note = note cũ của Vincent + dòng mới của agent, không đè note cũ.
note mới nên bắt đầu bằng "[Claude hh:mm]" và nêu chỗ ghi, cách verify, rollback. Thiếu "[Claude" thì script thêm dấu giờ.
Đầu ra (khi có --ghi), trong --out (mặc định ~/.cm/ma/b<hhmm>/, đường dẫn ngắn để lệnh không dài):
  <id>.json          dữ liệu update của một thẻ.
  _writes_NN.json    một lô, tối đa --batch-size lệnh {op: update, collection: reviews, doc_id, if_version, file_path}.
  ids.txt            id của các thẻ trong lô. --ghi cũng nối các id này vào --so-id.
                     Nếu Vincent từ chối một lô, xoá các id của lô đó khỏi sổ trước khi chạy lại.
Không có --ghi: chạy thử, chỉ in kế hoạch và không ghi file nào.
Luôn in trước số lô, tức số hộp duyệt mà Vincent phải bấm.
Mã thoát: 0 chạy được (kể cả khi không còn thẻ nào), 1 có lỗi dữ liệu (JSON hỏng, thiếu id hoặc note, id trùng giữa lane,
thẻ không có version), 2 sai đầu vào hoặc thư mục ra đã có file.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_lib  # noqa: E402

POS = re.compile(r'(?<!\w)đạt(?!\w)', re.I)
VERDICT = re.compile(r'(?:không|chưa)\s+đạt|pass\s*=\s*false|đạt\s+có\s+điều\s+kiện|(?<!\w)đạt(?!\w)', re.I)


MARK = re.compile(r'kết luận[^\n]{0,15}?(?::|\n)', re.I)


def lane_verdict(text):
    """Trả (đạt: bool, lý do). Mốc là chữ "Kết luận" đứng đầu dòng hoặc đầu câu, kèm dấu hai chấm hoặc xuống dòng.
    Lấy mốc cuối cùng. Từ khoá đầu tiên trong 400 ký tự sau mốc quyết định."""
    t = unicodedata.normalize('NFC', text).replace('*', '').replace('`', '')
    pos = None
    for m in MARK.finditer(t):
        before = re.sub(r'[#>\s-]+$', '', t[max(0, m.start() - 40):m.start()].split('\n')[-1])
        if before == '' or before[-1] in '.!?':
            pos = m.end()
    if pos is None:
        return False, 'không có mục "Kết luận" đứng đầu dòng hoặc đầu câu'
    seg = t[pos:pos + 400]
    m = VERDICT.search(seg)
    if not m:
        return False, 'không đọc ra "đạt" hay "không đạt" sau mục "Kết luận"'
    word = m.group(0).lower()
    if POS.fullmatch(word):
        return True, 'đạt'
    return False, word


def read_lane(lane):
    """Trả (entries, bỏ_lý_do, lỗi)."""
    ma = os.path.join(lane, 'mark_applied.json')
    if not os.path.isfile(ma):
        return None, 'thiếu mark_applied.json', None
    kd = sorted(glob.glob(os.path.join(lane, 'kiem-doc-lap*.md')), key=os.path.getmtime)
    if not kd:
        return None, 'thiếu kiem-doc-lap.md: lane chưa có người kiểm độc lập', None
    ok, why = lane_verdict(open(kd[-1], encoding='utf-8').read())
    if not ok:
        return None, 'kiem-doc-lap (%s) không đạt: %s' % (os.path.basename(kd[-1]), why), None
    try:
        data = json.load(open(ma, encoding='utf-8'))
    except ValueError as e:
        return None, None, 'mark_applied.json không phải JSON: %s' % e
    if not isinstance(data, list):
        return None, None, 'mark_applied.json phải là list'
    return data, None, None


def merge_note(old, new):
    old = (old or '').rstrip()
    if new.strip() and new.strip() in old:
        return old
    return (old + '\n\n' if old else '') + new.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description='Dựng lô gắn "đã áp" cho thẻ duyệt. Xem docstring đầu file.')
    ap.add_argument('--lane', action='append', required=True)
    ap.add_argument('--versions', required=True)
    ap.add_argument('--so-id', default='~/.cm/ma/applied-ids.txt')
    ap.add_argument('--out')
    ap.add_argument('--batch-size', type=int, default=50)
    ap.add_argument('--now', help='ISO UTC, mặc định giờ hiện tại')
    ap.add_argument('--ghi', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if a.batch_size < 1:
        print('--batch-size phải từ 1', file=sys.stderr)
        return 2
    for l in a.lane:
        if not os.path.isdir(l):
            print('Không có thư mục lane: ' + l, file=sys.stderr)
            return 2
    try:
        remote_raw = json.load(open(a.versions, encoding='utf-8'))
        remote = batch_lib.parse_docs(remote_raw)
    except (OSError, ValueError) as e:
        print('Không đọc được --versions: %s' % e, file=sys.stderr)
        return 2
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    if a.now:
        now = datetime.datetime.strptime(a.now.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
    now_iso = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    so_path = os.path.expanduser(a.so_id)
    known = set()
    if os.path.isfile(so_path):
        known = {l.strip() for l in open(so_path, encoding='utf-8') if l.strip()}
    out_dir = os.path.abspath(os.path.expanduser(a.out or '~/.cm/ma/b' + now.strftime('%H%M')))
    if a.ghi:
        why = batch_lib.prepare_out(out_dir, a.force)
        if why:
            print(why, file=sys.stderr)
            return 2

    errors, skipped_lanes, skipped, warns = [], [], [], []
    plan, seen = [], {}
    for lane in a.lane:
        entries, why_skip, err = read_lane(lane)
        if err:
            errors.append('%s: %s' % (lane, err))
            continue
        if why_skip:
            skipped_lanes.append({'lane': lane, 'ly_do': why_skip})
            continue
        for i, e in enumerate(entries):
            where = '%s#%d' % (os.path.basename(lane.rstrip('/')), i)
            if not isinstance(e, dict) or not e.get('id'):
                errors.append('%s: thiếu id' % where)
                continue
            iid = str(e['id'])
            note = str(e.get('note') or '').strip()
            if e.get('status', 'applied') != 'applied':
                errors.append('%s (%s): status phải là applied, đang là %r' % (where, iid, e.get('status')))
                continue
            if not note:
                errors.append('%s (%s): thiếu note' % (where, iid))
                continue
            if iid in seen:
                errors.append('%s (%s): id trùng với lane %s' % (where, iid, seen[iid]))
                continue
            seen[iid] = os.path.basename(lane.rstrip('/'))
            if not note.startswith('[Claude'):
                note = '[Claude %s] %s' % (now.strftime('%H:%M'), note)
            if not re.search(r'rollback|trả lại|hoàn tác', note, re.I) or not re.search(r'verify|kiểm|đối chiếu', note, re.I):
                warns.append('%s: note nên nêu cả verify và rollback' % iid)
            if iid in known:
                skipped.append({'id': iid, 'ly_do': 'đã có trong sổ id'})
                continue
            doc = remote.get(iid)
            if doc is None:
                skipped.append({'id': iid, 'ly_do': 'không có trong --versions: thẻ chưa duyệt, đã bỏ, hoặc đã applied'})
                continue
            if doc['data'].get('status') not in (None, 'approved', 'edited'):
                skipped.append({'id': iid, 'ly_do': 'status trên trang là %s' % doc['data'].get('status')})
                continue
            if doc['version'] is None:
                errors.append('%s: thẻ không có version trong --versions, không đặt được if_version' % iid)
                continue
            old = doc['data'].get('note') or ''
            if note.strip() in old:
                skipped.append({'id': iid, 'ly_do': 'note này đã có trên thẻ'})
                continue
            plan.append({'id': iid, 'version': doc['version'], 'lane': seen[iid],
                         'data': {'status': 'applied', 'appliedAt': now_iso, 'note': merge_note(old, note)}})
    if len(remote) >= 1000:
        warns.append('--versions có %d tài liệu: query có thể bị cắt ở limit 1000, thẻ ngoài mốc này sẽ bị bỏ' % len(remote))

    batches = list(batch_lib.chunks(plan, a.batch_size))
    res = {'lanes_bo': skipped_lanes, 'the_bo': skipped, 'the_gan': len(plan), 'so_lo': len(batches),
           'so_hop_duyet': len(batches), 'loi': errors, 'canh_bao': warns, 'da_ghi': False, 'out': out_dir if a.ghi else None}
    if a.ghi and plan and not errors:
        os.makedirs(out_dir, exist_ok=True)
        for p in plan:
            with open(os.path.join(out_dir, batch_lib.safe_name(p['id']) + '.json'), 'w', encoding='utf-8') as f:
                json.dump(p['data'], f, ensure_ascii=False, indent=1)
        for n, b in enumerate(batches, 1):
            writes = [{'op': 'update', 'collection': 'reviews', 'doc_id': p['id'], 'if_version': p['version'],
                       'file_path': os.path.join(out_dir, batch_lib.safe_name(p['id']) + '.json')} for p in b]
            with open(os.path.join(out_dir, '_writes_%02d.json' % n), 'w', encoding='utf-8') as f:
                json.dump(writes, f, ensure_ascii=False, indent=1)
        with open(os.path.join(out_dir, 'ids.txt'), 'w', encoding='utf-8') as f:
            f.write(''.join(p['id'] + '\n' for p in plan))
        os.makedirs(os.path.dirname(so_path) or '.', exist_ok=True)
        with open(so_path, 'a', encoding='utf-8') as f:
            f.write(''.join(p['id'] + '\n' for p in plan))
        res['da_ghi'] = True
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print('Vincent phải bấm %d hộp duyệt (%d lô, %d thẻ).' % (len(batches), len(batches), len(plan)))
        for l in skipped_lanes:
            print('BỎ LANE %s: %s' % (l['lane'], l['ly_do']))
        for s in skipped:
            print('BỎ THẺ %s: %s' % (s['id'], s['ly_do']))
        for w in warns:
            print('CẢNH BÁO %s' % w)
        for e in errors:
            print('LỖI %s' % e)
        for n, b in enumerate(batches, 1):
            print('lô %02d: %d thẻ, từ %s tới %s' % (n, len(b), b[0]['id'], b[-1]['id']))
        if res['da_ghi']:
            print('Đã ghi vào %s và nối %d id vào %s' % (out_dir, len(plan), so_path))
        else:
            print('Chạy thử, chưa ghi file. Thêm --ghi để ghi.' if not errors else 'Có lỗi, chưa ghi file.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
