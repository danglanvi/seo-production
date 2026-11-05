#!/usr/bin/env python3
"""footprint_count.py <file.html>... : đếm footprint trong HTML: khối inline script/style, comment tiếng Việt trong code,
comment có từ khoá quy trình, HTML comment VI, data-no-optimize. In một dòng mỗi file. Dùng để so trước/sau."""
import os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_html import scan_file
VI = re.compile(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", re.I)
# Từ quy trình chung + token riêng của site (tên người duyệt, mã lane, mã bản) qua biến FOOTPRINT_EXTRA="Tên|lane-x|v8-ky-thuat"
_EXTRA = "|".join(t for t in os.environ.get("FOOTPRINT_EXTRA", "").split("|") if t)
PROC = re.compile(r"(\blane\b|phiên|đợt|\blô \d|/\d{2}/20\d{2}|\baxe\b|(?<!trình )duyệt" + ("|" + _EXTRA if _EXTRA else "") + ")", re.I)
incomplete = False
for f in sys.argv[1:]:
    h = open(f, encoding="utf-8", errors="replace").read()
    r = scan_file(Path(f))
    incomplete |= not r["scan_complete"]
    cm = r["_comment_texts"]
    hc = r["_html_comment_texts"]
    vi = [c for c in cm if VI.search(c)]; proc = [c for c in cm if PROC.search(c)]
    print(f"{f}: inline_script={r['inline_scripts']} inline_style={r['inline_styles']} js_bytes={r['inline_js_bytes']//1024}KiB css_bytes={r['inline_css_bytes']//1024}KiB important_raw_html={h.count('!important')} comment_code={len(cm)} comment_vi={len(vi)} comment_quytrinh={len(proc)} htmlcomment_vi={sum(1 for c in hc if VI.search(c))} htmlcomment_quytrinh={sum(1 for c in hc if PROC.search(c))} data_no_optimize={h.count('data-no-optimize')} scan_complete={int(r['scan_complete'])}")
    for c in proc[:5]: print("   QT:", " ".join(c.split())[:110])
    for err in r["scan_errors"]:
        print(f"   INCOMPLETE: {err['where']}#{err['block_id']}: {err['error']}", file=sys.stderr)
if incomplete or len(sys.argv) < 2:
    raise SystemExit(2)
