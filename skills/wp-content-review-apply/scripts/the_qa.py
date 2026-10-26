#!/usr/bin/env python3
"""Cổng QA máy cho thẻ duyệt có chữ mới. Chạy trước ArtifactData set. Chỉ đọc file local, không gọi mạng hay model.

python3 -I the_qa.py <file thẻ .json | thư mục report> --entity gtv|tag|academy|client --facts facts.json
                     [--site https://<host>] [--copy-guard <copy_guard.py>] [--khong-copy-guard]
                     [--khong-px] [--nam 2026] [--max-title 65] [--max-meta 160]
                     [--ghi <thư mục ra>] [--force] [--json]

Đầu vào: tài liệu phần ({"items": [...]}) hoặc thư mục có nhiều file như vậy (bỏ summary.json).
Mỗi trường có chữ mới (proposed, A, B khác before) phải đạt 6 kiểm tra. Lỗi thì thoát mã 1 và không được nạp thẻ:
  1. qa.humanizer: trường (hoặc thẻ) có khối "qa" với "humanizer" không rỗng, ví dụ "1.4 | đã rà" hoặc "1.4 | không đổi".
  2. nfc: chữ ở dạng Unicode NFC.
  3. do_dai: seo_title tối đa --max-title ký tự, meta tối đa --max-meta ký tự, đếm sau khi thay %currentyear%.
     Có serp_pixel.py của skill seo-onpage thì đo thêm px (title 688, meta 920). Thiếu thì chỉ cảnh báo.
  4. links: mọi link trong before (hoặc raw) còn trong chữ mới. Link mất là lỗi. Link thêm chỉ ghi vào qa.links.them.
  5. so: mỗi số trong chữ mới có trong before, raw hoặc facts.json. Số lạ là lỗi.
  6. copy_guard: chạy copy_guard.py check - --entity <entity>. Có dòng mức "chặn" là lỗi.
     Không tìm thấy copy_guard.py thì lỗi, trừ khi có --khong-copy-guard (ghi cảnh báo).
Bỏ qua kiểm chữ với trường slug, url, post_name. Trường giữ nguyên (chữ bằng before) không kiểm.
facts.json: JSON bất kỳ. Script lấy mọi số trong mọi chuỗi và số của file. Ví dụ {"khach": "hơn 100 khách", "nam_lam": 10}.
Không có --ghi: chỉ báo cáo, không ghi gì (chạy thử). Có --ghi: ghi bản thẻ đã điền qa.copy_guard, qa.do_dai, qa.links,
qa.nfc vào thư mục ra (chỉ khi không có lỗi), giữ nguyên qa.humanizer và qa.jev_text_qa do agent điền. Không ghi đè file có sẵn khi thiếu --force.
Với trường nhiều phương án, qa.do_dai là {"A": {...}, "B": {...}}. Trường một phương án (proposed) dùng {ky_tu, px}.
Mã thoát: 0 đạt, 1 có lỗi QA, 2 sai đầu vào hoặc file ra đã có.
"""
import argparse
import datetime
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))  # thư mục chứa các skill
COPY_GUARD_PATHS = [
    os.path.join(SKILLS, 'website-conversion-copywriting', 'scripts', 'copy_guard.py'),
    os.path.join(os.path.dirname(SKILLS), 'skills', 'website-conversion-copywriting', 'scripts', 'copy_guard.py'),
    os.path.join(os.path.dirname(os.path.dirname(SKILLS)), 'skills', 'website-conversion-copywriting', 'scripts', 'copy_guard.py'),
]
PIXEL_PATH = os.path.join(SKILLS, 'seo-onpage', 'scripts', 'serp_pixel.py')
VARIANTS = ('proposed', 'A', 'B')
NO_PROSE = {'slug', 'url', 'post_name'}
TITLE_KEYS = {'seo_title', 'title'}
META_KEYS = {'meta', 'meta_desc', 'description'}
YEAR_VARS = ('%%currentyear%%', '%currentyear%')
HREF = re.compile(r'''href\s*=\s*["']([^"']+)["']''', re.I)
MDLINK = re.compile(r'\]\(([^)\s]+)\)')
NUM = re.compile(r'\d[\d.,]*\d|\d')
BAD_HUMANIZER = {'', 'chua', 'chưa', 'no', 'none', 'n/a', 'na', 'khong', 'không'}


def NFC(s):
    return unicodedata.normalize('NFC', str(s if s is not None else ''))


def base_key(k):
    return str(k or '').split('#')[0]


def canon_num(n):
    n = n.strip('.,')
    if re.fullmatch(r'\d{1,3}([.,]\d{3})+', n):
        return re.sub(r'[.,]', '', n)
    return n.replace(',', '.')


def numbers(text):
    t = re.sub(r'https?://\S+', ' ', str(text or ''))
    t = HREF.sub(' ', t)
    t = MDLINK.sub(' ', t)
    for v in YEAR_VARS:
        t = t.replace(v, ' ')
    return {canon_num(m) for m in NUM.findall(t)}


def facts_numbers(obj):
    out = set()
    if isinstance(obj, dict):
        for v in obj.values():
            out |= facts_numbers(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= facts_numbers(v)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out.add(canon_num(('%g' % obj) if isinstance(obj, float) else str(obj)))
    elif isinstance(obj, str):
        out |= numbers(obj)
    return out


def links(text, host):
    found = set()
    for u in HREF.findall(text or '') + MDLINK.findall(text or ''):
        u = u.strip()
        if u.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        p = urlsplit(u)
        if p.netloc and host and p.netloc.lower() == host:
            u = p.path + ('?' + p.query if p.query else '')
        elif p.netloc:
            u = '%s://%s%s' % (p.scheme or 'https', p.netloc.lower(), p.path + ('?' + p.query if p.query else ''))
        else:
            u = p.path + ('?' + p.query if p.query else '')
        if len(u) > 1 and u.endswith('/'):
            u = u.rstrip('/')
        found.add(u or '/')
    return found


def load_pixel():
    if not os.path.isfile(PIXEL_PATH):
        return None
    spec = importlib.util.spec_from_file_location('serp_pixel_qa', PIXEL_PATH)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        prof = mod.PROFILES['desktop']
        return {'title': mod.Meter(prof['title_size']), 'desc': mod.Meter(prof['desc_size']),
                'title_limit': prof['title_limit'], 'desc_limit': prof['desc_limit']}
    except Exception:
        return None


def find_copy_guard(explicit):
    for p in ([explicit] if explicit else COPY_GUARD_PATHS):
        if p and os.path.isfile(p):
            return p
    return None


def run_copy_guard(path, entity, text):
    p = subprocess.run([sys.executable, '-I', path, 'check', '-', '--entity', entity, '--json'],
                       input=text, capture_output=True, text=True, timeout=60)
    if p.returncode not in (0, 1):
        raise RuntimeError('copy_guard lỗi mã %d: %s' % (p.returncode, p.stderr.strip()[-200:]))
    try:
        d = json.loads(p.stdout)
        n = int((d.get('tong') or {}).get('chặn', 0))
    except ValueError:
        n = 1 if p.returncode == 1 else 0
    return max(n, 1 if p.returncode == 1 else 0)


def before_text(f):
    if 'raw' in f:
        return NFC(f.get('raw'))
    b = NFC(f.get('before'))
    return '' if re.fullmatch(r'\(.*\)', b.strip()) else b


def check_doc(name, doc, ctx):
    errors, warns, filled = [], [], []
    E = lambda where, msg: errors.append({'where': where, 'msg': msg})
    W = lambda where, msg: warns.append({'where': where, 'msg': msg})
    n_checked = 0
    for it in doc.get('items') or []:
        iid = it.get('id') or '?'
        for f in it.get('fields') or []:
            key = base_key(f.get('key'))
            if key in NO_PROSE:
                continue
            old = before_text(f)
            old_n = re.sub(r'\s+', ' ', NFC(f.get('before'))).strip()
            texts = {}
            for v in VARIANTS:
                if isinstance(f.get(v), str) and f[v].strip():
                    t = NFC(f[v])
                    if re.sub(r'\s+', ' ', t).strip() not in (old_n, re.sub(r'\s+', ' ', old).strip()):
                        texts[v] = f[v]
            if not texts:
                continue
            where = '%s/%s/%s' % (name, iid, f.get('key'))
            qa = f.get('qa') if isinstance(f.get('qa'), dict) else (it.get('qa') if isinstance(it.get('qa'), dict) else None)
            new_qa = dict(qa or {})
            hum = str((qa or {}).get('humanizer') or '').strip()
            if not qa or hum.lower() in BAD_HUMANIZER:
                E(where, 'thiếu qa.humanizer: chữ mới chưa qua humanizer')
            if qa and not str(qa.get('jev_text_qa') or '').strip():
                W(where, 'thiếu qa.jev_text_qa')
            lost_all, added_all, dolai = set(), set(), {}
            cg_total = 0
            before_links = links(old, ctx['host'])
            ok_nums = numbers(old) | numbers(f.get('before')) | ctx['facts']
            for v, t in texts.items():
                n_checked += 1
                if unicodedata.normalize('NFC', t) != t:
                    E(where, 'phương án %s không ở dạng NFC' % v)
                shown = t
                for yv in YEAR_VARS:
                    shown = shown.replace(yv, ctx['nam'])
                chars = len(shown.strip())
                px = None
                lim = ctx['max_title'] if key in TITLE_KEYS else ctx['max_meta'] if key in META_KEYS else None
                if lim is not None and chars > lim:
                    E(where, 'phương án %s dài %d ký tự, tối đa %d' % (v, chars, lim))
                if (key in TITLE_KEYS or key in META_KEYS) and ctx['pixel']:
                    meter = ctx['pixel']['title' if key in TITLE_KEYS else 'desc']
                    plim = ctx['pixel']['title_limit' if key in TITLE_KEYS else 'desc_limit']
                    px = round(meter.width(shown.strip()), 1)
                    if px > plim:
                        E(where, 'phương án %s rộng %s px, tối đa %s px' % (v, px, plim))
                elif (key in TITLE_KEYS or key in META_KEYS) and not ctx['px_warned']:
                    ctx['px_warned'] = True
                    W('toàn bộ', 'không đo được px (thiếu seo-onpage/scripts/serp_pixel.py hoặc dùng --khong-px): chỉ kiểm ký tự')
                dolai[v] = {'ky_tu': chars, 'px': px}
                now_links = links(t, ctx['host'])
                lost, added = before_links - now_links, now_links - before_links
                if lost:
                    E(where, 'phương án %s mất link: %s' % (v, ', '.join(sorted(lost))))
                lost_all |= lost
                added_all |= added
                bad = sorted(n for n in numbers(t) if n not in ok_nums)
                if bad:
                    E(where, 'phương án %s có số không có trong before, raw hay facts: %s' % (v, ', '.join(bad)))
                if ctx['cg']:
                    try:
                        n = run_copy_guard(ctx['cg'], ctx['entity'], t)
                    except Exception as e:
                        E(where, str(e))
                        n = 0
                    if n:
                        E(where, 'phương án %s bị copy_guard chặn (%d dòng)' % (v, n))
                    cg_total += n
            new_qa['copy_guard'] = ('ok' if not cg_total else '%d chặn' % cg_total) if ctx['cg'] else 'chưa chạy'
            new_qa['do_dai'] = next(iter(dolai.values())) if list(dolai) == ['proposed'] else dolai
            new_qa['links'] = {'mat': sorted(lost_all), 'them': sorted(added_all)}
            new_qa['nfc'] = all(unicodedata.normalize('NFC', t) == t for t in texts.values())
            filled.append((it, f, new_qa))
    return errors, warns, filled, n_checked


def load_docs(path):
    files = [path] if os.path.isfile(path) else sorted(glob.glob(os.path.join(path, '*.json')))
    docs = {}
    for fp in files:
        name = os.path.splitext(os.path.basename(fp))[0]
        if name == 'summary':
            continue
        d = json.load(open(fp, encoding='utf-8'))
        d = d.get('data', d) if isinstance(d, dict) else d
        if isinstance(d, dict) and isinstance(d.get('items'), list):
            docs[name] = d
    return docs


def main(argv=None):
    ap = argparse.ArgumentParser(description='Cổng QA máy cho thẻ duyệt có chữ mới. Xem docstring đầu file.')
    ap.add_argument('path', help='file thẻ .json hoặc thư mục report')
    ap.add_argument('--entity', required=True, choices=['gtv', 'tag', 'academy', 'client'])
    ap.add_argument('--facts', required=True, help='facts.json: số liệu được phép dùng')
    ap.add_argument('--site', default='', help='https://<host> để coi link cùng host là link nội bộ')
    ap.add_argument('--copy-guard', dest='cg')
    ap.add_argument('--khong-copy-guard', action='store_true', help='bỏ copy_guard khi thiếu script (ghi cảnh báo)')
    ap.add_argument('--khong-px', action='store_true')
    ap.add_argument('--nam', default=str(datetime.date.today().year))
    ap.add_argument('--max-title', type=int, default=65)
    ap.add_argument('--max-meta', type=int, default=160)
    ap.add_argument('--ghi', help='thư mục ra: ghi bản thẻ đã điền qa')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if not os.path.exists(a.path) or not os.path.isfile(a.facts):
        print('Thiếu đường dẫn thẻ hoặc facts.json', file=sys.stderr)
        return 2
    try:
        docs = load_docs(a.path)
        facts = json.load(open(a.facts, encoding='utf-8'))
    except ValueError as e:
        print('Không đọc được JSON: %s' % e, file=sys.stderr)
        return 2
    if not docs:
        print('Không có tài liệu có "items" trong ' + a.path, file=sys.stderr)
        return 2
    cg = None
    warns0 = []
    if not a.khong_copy_guard:
        cg = find_copy_guard(a.cg)
        if not cg:
            print('Không tìm thấy copy_guard.py. Đặt --copy-guard <đường dẫn> hoặc chạy với --khong-copy-guard.', file=sys.stderr)
            return 2
    else:
        warns0.append({'where': 'toàn bộ', 'msg': 'đã bỏ copy_guard theo --khong-copy-guard'})
    out_dir = a.ghi
    if out_dir:
        if os.path.exists(out_dir) and not os.path.isdir(out_dir):
            print('--ghi phải là thư mục', file=sys.stderr)
            return 2
        for name in docs:
            if os.path.exists(os.path.join(out_dir, name + '.json')) and not a.force:
                print('File ra đã có: %s (thêm --force để ghi đè)' % os.path.join(out_dir, name + '.json'), file=sys.stderr)
                return 2
    host = urlsplit(a.site).netloc.lower() if a.site else ''
    ctx = {'host': host, 'facts': facts_numbers(facts), 'nam': a.nam, 'max_title': a.max_title, 'max_meta': a.max_meta,
           'pixel': None if a.khong_px else load_pixel(), 'px_warned': False, 'cg': cg, 'entity': a.entity}
    errors, warns, checked = [], list(warns0), 0
    for name, d in docs.items():
        e, w, filled, n = check_doc(name, d, ctx)
        errors += e
        warns += w
        checked += n
        for it, f, qa in filled:
            f['qa'] = qa
    wrote = False
    if out_dir and not errors:
        os.makedirs(out_dir, exist_ok=True)
        for name, d in docs.items():
            with open(os.path.join(out_dir, name + '.json'), 'w', encoding='utf-8') as fo:
                json.dump(d, fo, ensure_ascii=False, indent=1)
        wrote = True
    res = {'errors': errors, 'warnings': warns, 'tai_lieu': len(docs), 'chu_da_kiem': checked, 'da_ghi': wrote}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for e in errors:
            print('LỖI  %s: %s' % (e['where'], e['msg']))
        for w in warns:
            print('CẢNH BÁO %s: %s' % (w['where'], w['msg']))
        print('%d tài liệu, %d chữ mới đã kiểm, %d lỗi, %d cảnh báo%s' % (
            len(docs), checked, len(errors), len(warns), ' (đã ghi vào %s)' % out_dir if wrote else ' (chưa ghi file)'))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
