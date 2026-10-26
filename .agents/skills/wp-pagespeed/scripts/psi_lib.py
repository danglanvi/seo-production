# Hàm dùng chung cho psi_decide.py, psi_ab.py, psi_cls_dump.py. Không chạy trực tiếp.
# Chỉ dùng thư viện chuẩn. Tương thích Python 3.9.
# Script gọi bằng "python3 -I" phải thêm thư mục của chính nó vào sys.path trước khi import psi_lib.
import json
import re
import statistics as st

# Ngưỡng mặc định lấy từ site agency mẫu 10/2026. Hiệu chuẩn lại ở site khác (skill model-calibration).
DEFAULT_THR = {'min_gain': 3.0, 'lcp_ms': 200.0, 'cls': 0.02, 'min_runs': 3, 'max_runs': 5, 'bench_gap': 0.2, 'bench_cut': 800.0, 'pair_share': 0.6}

LABELS = {'better': 'tốt hơn', 'same': 'không đổi', 'worse': 'xấu hơn', 'more': 'chưa đủ lượt'}

AB_NAME = re.compile(r'^(?P<page>.+)-(?P<var>[^-]+)-r(?P<k>\d+)_(?P<dev>mobile|desktop)_run(?P<m>\d+)\.json$')


def median(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def load_run(path):
    """Đọc một file JSON của PSI v5. Ném ValueError khi file hỏng hoặc không có lighthouseResult."""
    try:
        with open(path, encoding='utf-8') as f:
            j = json.load(f)
    except (OSError, ValueError) as e:
        raise ValueError('%s: không đọc được JSON (%s)' % (path, e))
    lr = j.get('lighthouseResult') if isinstance(j, dict) else None
    if not lr:
        raise ValueError('%s: không có lighthouseResult (PSI lỗi hoặc file cắt dở)' % path)
    au = lr.get('audits', {})
    score = (lr.get('categories', {}).get('performance') or {}).get('score')
    num = lambda k: (au.get(k) or {}).get('numericValue')
    return {
        'file': path,
        'score': None if score is None else score * 100.0,
        'lcp': num('largest-contentful-paint'),
        'fcp': num('first-contentful-paint'),
        'tbt': num('total-blocking-time'),
        'cls': num('cumulative-layout-shift'),
        'bench': (lr.get('environment') or {}).get('benchmarkIndex'),
        'dev': (lr.get('configSettings') or {}).get('formFactor'),
    }


def parse_ab_name(fname):
    """File do psi_ab + psi_run ghi: <trang>-<biến thể>-r<k>_<thiết bị>_run<m>.json. Trả None nếu tên khác."""
    m = AB_NAME.match(fname)
    return m.groupdict() if m else None


def _med(runs, k):
    return median([r[k] for r in runs])


def decide(a_runs, b_runs, thr=None):
    """So nhánh A (gốc) với nhánh B (thử) trong nhiễu. Trả dict: label (better|same|worse|more), reason, số liệu.

    Nhãn tính theo ngưỡng đặt trước (thr), không đổi sau khi thấy số:
    - better: trung vị điểm B hơn A từ min_gain, CLS không tăng quá thr.cls, LCP không chậm quá thr.lcp_ms,
      và B hơn A ở ít nhất pair_share số cặp lượt xen kẽ (khi có tên psi_ab).
    - worse: điểm B kém A từ min_gain, hoặc CLS/LCP xấu đi quá ngưỡng (kể cả khi điểm tăng).
    - same: chênh dưới ngưỡng và đã đủ max_runs lượt mỗi nhánh.
    - more: chưa đủ min_runs, lệch máy PSI chưa gỡ được, hoặc chênh dưới ngưỡng mà chưa đủ max_runs.
    """
    t = dict(DEFAULT_THR)
    t.update(thr or {})
    out = {'label': 'more', 'reason': '', 'nA': len(a_runs), 'nB': len(b_runs), 'thr': t, 'note': ''}
    a_runs = [r for r in a_runs if r.get('score') is not None]
    b_runs = [r for r in b_runs if r.get('score') is not None]
    out['nA'], out['nB'] = len(a_runs), len(b_runs)
    if min(len(a_runs), len(b_runs)) < t['min_runs']:
        out['reason'] = 'cần ít nhất %d lượt mỗi nhánh (A=%d, B=%d)' % (t['min_runs'], len(a_runs), len(b_runs))
        return out
    a_runs = sorted(a_runs, key=lambda r: r.get('k', 0))[:int(t['max_runs'])]
    b_runs = sorted(b_runs, key=lambda r: r.get('k', 0))[:int(t['max_runs'])]
    out['nA'], out['nB'] = len(a_runs), len(b_runs)
    ba, bb = _med(a_runs, 'bench'), _med(b_runs, 'bench')
    out['benchA'], out['benchB'] = ba, bb
    if ba and bb and abs(ba - bb) / max(ba, bb) > t['bench_gap']:
        # Hai nhánh rơi vào máy PSI nhanh chậm khác nhau: chỉ so trong nhóm máy có đủ lượt của cả hai nhánh.
        cut = t['bench_cut']
        best = None
        for name, pick in (('máy chậm (< %d)' % cut, lambda r: (r.get('bench') or 0) < cut), ('máy nhanh (>= %d)' % cut, lambda r: (r.get('bench') or 0) >= cut)):
            ga, gb = [r for r in a_runs if pick(r)], [r for r in b_runs if pick(r)]
            if len(ga) >= 2 and len(gb) >= 2 and (best is None or len(ga) + len(gb) > len(best[1]) + len(best[2])):
                best = (name, ga, gb)
        if best is None:
            out['reason'] = 'lệch máy PSI: benchmarkIndex trung vị A=%.0f, B=%.0f, không nhóm máy nào có đủ 2 lượt mỗi nhánh. Đo thêm xen kẽ' % (ba, bb)
            return out
        out['note'] = 'lệch máy PSI (A=%.0f, B=%.0f): chỉ so nhóm %s' % (ba, bb, best[0])
        a_runs, b_runs = best[1], best[2]
        out['nA'], out['nB'] = len(a_runs), len(b_runs)
    ma, mb = _med(a_runs, 'score'), _med(b_runs, 'score')
    d = mb - ma
    dl = (_med(b_runs, 'lcp') or 0) - (_med(a_runs, 'lcp') or 0)
    dc = (_med(b_runs, 'cls') or 0) - (_med(a_runs, 'cls') or 0)
    out.update({'scoreA': ma, 'scoreB': mb, 'dScore': d, 'dLcp': dl, 'dCls': dc})
    ka, kb = {r.get('k'): r['score'] for r in a_runs if r.get('k') is not None}, {r.get('k'): r['score'] for r in b_runs if r.get('k') is not None}
    pairs = [(ka[k], kb[k]) for k in sorted(set(ka) & set(kb))]
    share = (sum(1 for x, y in pairs if y > x) / len(pairs)) if len(pairs) >= 3 else None
    out['pairShare'] = share
    if dc > t['cls']:
        out['label'], out['reason'] = 'worse', 'CLS trung vị tăng %.3f (ngưỡng %.3f)' % (dc, t['cls'])
    elif dl > t['lcp_ms']:
        out['label'], out['reason'] = 'worse', 'LCP trung vị chậm thêm %.0f ms (ngưỡng %.0f)' % (dl, t['lcp_ms'])
    elif d <= -t['min_gain']:
        out['label'], out['reason'] = 'worse', 'điểm trung vị giảm %.1f (ngưỡng %.1f)' % (-d, t['min_gain'])
    elif d >= t['min_gain']:
        if share is not None and share < t['pair_share']:
            out['reason'] = 'điểm trung vị tăng %.1f nhưng chỉ %.0f%% cặp lượt B hơn A (cần %.0f%%). Đo thêm' % (d, share * 100, t['pair_share'] * 100)
        else:
            out['label'], out['reason'] = 'better', 'điểm trung vị tăng %.1f (ngưỡng %.1f)' % (d, t['min_gain'])
    if out['label'] == 'more' and not out['reason']:
        out['reason'] = 'chênh điểm %.1f dưới ngưỡng %.1f, mới %d lượt' % (d, t['min_gain'], min(out['nA'], out['nB']))
    if out['label'] == 'more' and min(out['nA'], out['nB']) >= t['max_runs']:
        out['label'], out['reason'] = 'same', 'chênh điểm %.1f dưới ngưỡng %.1f sau %d lượt mỗi nhánh' % (d, t['min_gain'], t['max_runs'])
    return out


# ---------- bản HTML tĩnh A/B: noindex và canonical tự trỏ ----------

_ROBOTS = re.compile(r'<meta\b[^>]*\bname\s*=\s*["\'](?:robots|googlebot|bingbot)["\'][^>]*>\s*', re.I)
_CANON = re.compile(r'<link\b[^>]*\brel\s*=\s*["\']canonical["\'][^>]*>\s*', re.I)
_HEAD = re.compile(r'<head\b[^>]*>', re.I)


def inject_noindex(html, canonical):
    """Bỏ mọi meta robots và canonical cũ, chèn noindex,nofollow và canonical trỏ chính bản tĩnh ngay sau <head>."""
    if not _HEAD.search(html):
        raise ValueError('HTML không có thẻ <head>')
    html = _ROBOTS.sub('', html)
    html = _CANON.sub('', html)
    ins = '<meta name="robots" content="noindex,nofollow"><link rel="canonical" href="%s">' % canonical.replace('"', '&quot;')
    m = _HEAD.search(html)
    return html[:m.end()] + ins + html[m.end():]


def check_noindex(html, canonical=None):
    """Trả danh sách lỗi. Rỗng nghĩa là bản tĩnh an toàn: đúng một meta robots noindex,nofollow, đúng một canonical tự trỏ."""
    errs = []
    robots = _ROBOTS.findall(html)
    if len(robots) != 1:
        errs.append('có %d thẻ meta robots (cần đúng 1)' % len(robots))
    for r in robots:
        c = re.search(r'content\s*=\s*["\']([^"\']*)["\']', r, re.I)
        v = (c.group(1) if c else '').lower().replace(' ', '')
        if 'noindex' not in v or 'nofollow' not in v:
            errs.append('meta robots không phải noindex,nofollow: %s' % (v or '(trống)'))
    canons = _CANON.findall(html)
    if len(canons) != 1:
        errs.append('có %d thẻ canonical (cần đúng 1)' % len(canons))
    for c in canons:
        h = re.search(r'href\s*=\s*["\']([^"\']*)["\']', c, re.I)
        href = h.group(1) if h else ''
        if canonical is not None and href != canonical:
            errs.append('canonical trỏ %s, cần %s' % (href, canonical))
    return errs
