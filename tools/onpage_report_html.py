#!/usr/bin/env python3
"""Onpage batch report (.md) → bảng nhiệt HTML để đọc nhanh.

Đọc batch report theo `_TEMPLATES/onpage-batch.md`: bảng mục 3 (score per URL), mục 5 (AX),
mục 7 (MX). File .md vẫn là bản gốc; HTML là bản xem, sinh lại được bất cứ lúc nào.
Chỉ đọc file nguồn, chỉ dùng thư viện chuẩn.

Usage:
    python3 tools/onpage_report_html.py <batch-report.md> [--out <file.html>]

Output mặc định: `<batch-report>.view.html` cạnh file .md (đã gitignore `*.view.html`).
"""

import html
import json
import re
import secrets
import sys
from pathlib import Path

ITEM_RE = re.compile(r"\b(T[23]-P\d{1,2}|P\d{1,2}|AX\d|MX\d)\b")
SCORE_RE = re.compile(r"(\d+)\s*/\s*(\d+)")
OK_MARKS = ("☑", "✅", "✔", "pass", "đạt", "x")
BAD_MARKS = ("❌", "✘", "fail", "rớt")
NA_MARKS = ("n/a", "na", "—", "-", "")


def tables_by_section(text):
    """Trả về {tiêu đề H2: [bảng, ...]}, mỗi bảng là list dòng, mỗi dòng là list ô."""
    out, title, buf = {}, "", []

    def flush():
        if buf:
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in buf]
            rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c or "--") for c in r)]
            if len(rows) > 1:
                out.setdefault(title, []).append(rows)
        buf.clear()

    for line in text.split("\n"):
        if line.startswith("## "):
            flush()
            title = line[3:].strip()
        elif line.strip().startswith("|"):
            buf.append(line)
        else:
            flush()
    flush()
    return out


def find_table(tables, key, need):
    for title, group in tables.items():
        if key in title.lower():
            for t in group:
                if any(need in c.lower() for c in t[0]):
                    return t
    return None


def col(header, *needles):
    for i, h in enumerate(header):
        if all(n in h.lower() for n in needles):
            return i
    return None


def mark(cell):
    c = cell.strip().lower()
    if c in NA_MARKS or c.startswith("n/a"):
        return "na"
    if "cannot" in c:
        return "todo"
    if any(m in c for m in BAD_MARKS):
        return "fail"
    if any(c == m or c.startswith(m) for m in OK_MARKS):
        return "pass"
    if c in ("☐", "{{x}}"):
        return "todo"
    return "todo" if "{{" in c else "pass" if c else "na"


def parse(text):
    tables = tables_by_section(text)
    fm = dict(re.findall(r"^([a-z_]+):\s*\"?(.*?)\"?\s*$", text.split("---")[1], re.M)) \
        if text.startswith("---") and text.count("---") >= 2 else {}
    data = {"meta": fm, "urls": [], "ax": [], "mx": [], "max": 23}
    t = find_table(tables, "bảng batch", "url")
    if t:
        h = t[0]
        i_url, i_type, i_p0 = col(h, "url"), col(h, "loại"), col(h, "p0")
        i_fail, i_fix, i_re, i_st = col(h, "item fail"), col(h, "ngày fix"), col(h, "re-score"), col(h, "status")
        score_cols = [i for i, x in enumerate(h) if x.lower().startswith("score")]
        for r in t[1:]:
            r = r + [""] * (len(h) - len(r))
            best = None
            for i in score_cols:
                m = SCORE_RE.search(r[i])
                if m and (best is None or int(m.group(2)) > best[1]):
                    best = (int(m.group(1)), int(m.group(2)))
            rescore = SCORE_RE.search(r[i_re]) if i_re is not None else None
            fails = sorted(set(ITEM_RE.findall(r[i_fail])) if i_fail is not None else [])
            data["urls"].append({
                "url": r[i_url] if i_url is not None else "",
                "type": r[i_type] if i_type is not None else "",
                "p0": mark(r[i_p0]) if i_p0 is not None else "todo",
                "score": best[0] if best else None, "of": best[1] if best else None,
                "rescore": int(rescore.group(1)) if rescore else None,
                "fails": fails,
                "fix": r[i_fix] if i_fix is not None else "",
                "status": r[i_st] if i_st is not None else "",
            })
            if best:
                data["max"] = max(data["max"], best[1])
    for key, bucket, prefix in (("ax extension", "ax", "ax"), ("mx", "mx", "mx")):
        t = find_table(tables, key, "url")
        if not t:
            continue
        h = t[0]
        i_url = col(h, "url")
        items = [(i, re.match(r"(AX\d|MX\d)", x, re.I).group(1).upper())
                 for i, x in enumerate(h) if re.match(r"(AX\d|MX\d)", x, re.I)]
        extra = [(i, x) for i, x in enumerate(h) if i != i_url and i not in [k for k, _ in items]]
        for r in t[1:]:
            r = r + [""] * (len(h) - len(r))
            data[bucket].append({"url": r[i_url] if i_url is not None else "",
                                 "items": {name: mark(r[i]) for i, name in items},
                                 "extra": {x: r[i] for i, x in extra}})
    return data


def item_columns(max_score):
    cols = ["P%d" % i for i in range(1, 24)]
    if max_score >= 31:
        cols += ["T2-P%d" % i for i in range(1, 9)]
    if max_score >= 39:
        cols += ["T3-P%d" % i for i in range(1, 9)]
    return cols


CSS = """
:root{--bg:#fff;--fg:#1a1f2b;--mut:#667085;--line:#e4e7ec;--card:#f8f9fb;--ok:#d9f2df;--bad:#f04438;--na:#eef0f3;--todo:#fff4d6;--acc:#3b5bdb}
:root[data-theme=dark]{--bg:#12151c;--fg:#e6e8ee;--mut:#98a2b3;--line:#2a2f3a;--card:#1a1e27;--ok:#1f4a2c;--na:#232833;--todo:#4a3a10}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif}
header,main{padding:16px 20px;max-width:1400px;margin:0 auto}h1{font-size:19px;margin:0 0 4px}h2{font-size:15px;margin:26px 0 8px}
.sub{color:var(--mut);font-size:13px}.cards{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px;min-width:120px}
.card b{display:block;font-size:20px}.card span{font-size:12px;color:var(--mut)}
button{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:4px 12px;cursor:pointer}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:12px}th,td{border-bottom:1px solid var(--line);padding:5px 6px;text-align:center;white-space:nowrap}
th{position:sticky;top:0;background:var(--card);cursor:pointer;user-select:none}th.on{background:var(--acc);color:#fff}
td.url,th.url{text-align:left;position:sticky;left:0;background:var(--bg);max-width:340px;overflow:hidden;text-overflow:ellipsis}
td.c{width:22px;min-width:22px;padding:0;height:24px}td.pass{background:var(--ok)}td.fail{background:var(--bad)}td.na{background:var(--na)}td.todo{background:var(--todo)}
td.txt{text-align:left;white-space:normal;min-width:180px}
.bars div{display:flex;align-items:center;gap:8px;margin:3px 0;font-size:12px}.bars i{display:block;height:12px;background:var(--bad);border-radius:3px}
.legend span{display:inline-block;width:12px;height:12px;border-radius:2px;margin:0 4px 0 12px;vertical-align:-1px}
.hide{display:none}
"""

JS = """
const D=JSON.parse(document.getElementById('data').textContent);
const root=document.documentElement;
document.getElementById('theme').onclick=()=>{root.dataset.theme=root.dataset.theme==='dark'?'':'dark'};
let sortKey='score',asc=true,filter=null;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function draw(){
  const rows=[...D.urls].filter(u=>!filter||u.fails.includes(filter));
  rows.sort((a,b)=>{const x=a[sortKey]??-1,y=b[sortKey]??-1;return (x>y?1:x<y?-1:0)*(asc?1:-1)});
  const head='<tr><th class="url" data-s="url">URL</th><th data-s="p0">P0</th><th data-s="score">Điểm</th><th data-s="rescore">Sau sửa</th>'
    +D.cols.map(c=>`<th data-i="${c}" class="${filter===c?'on':''}" title="Bấm để lọc URL rớt ${c}">${c.replace('T2-','²').replace('T3-','³')}</th>`).join('')+'</tr>';
  const body=rows.map(u=>`<tr><td class="url" title="${esc(u.url)}">${esc(u.url)}</td><td class="c ${u.p0}"></td>`
    +`<td>${u.score==null?'—':u.score+'/'+u.of}</td><td>${u.rescore==null?'—':u.rescore}</td>`
    +D.cols.map(c=>`<td class="c ${u.p0==='fail'?'na':u.score==null?'todo':u.fails.includes(c)?'fail':'pass'}" title="${c}"></td>`).join('')+'</tr>').join('');
  document.getElementById('heat').innerHTML=head+body;
  document.getElementById('count').textContent=rows.length+' / '+D.urls.length+' URL'+(filter?' rớt '+filter:'');
  document.querySelectorAll('#heat th[data-s]').forEach(th=>th.onclick=()=>{const k=th.dataset.s;asc=sortKey===k?!asc:true;sortKey=k;draw()});
  document.querySelectorAll('#heat th[data-i]').forEach(th=>th.onclick=()=>{filter=filter===th.dataset.i?null:th.dataset.i;draw()});
}
draw();
"""


def side_table(rows, names):
    if not rows:
        return '<div class="sub">Không có dữ liệu trong report.</div>'
    extra = list(rows[0]["extra"].keys())
    head = "<tr><th class='url'>URL</th>" + "".join("<th>%s</th>" % n for n in names) + \
           "".join("<th>%s</th>" % html.escape(x) for x in extra) + "</tr>"
    body = ""
    for r in rows:
        body += "<tr><td class='url'>%s</td>" % html.escape(r["url"])
        body += "".join("<td class='c %s' title='%s'></td>" % (r["items"].get(n, "na"), n) for n in names)
        body += "".join("<td class='txt'>%s</td>" % html.escape(r["extra"].get(x, "")) for x in extra)
        body += "</tr>"
    return "<div class='wrap'><table>%s%s</table></div>" % (head, body)


def render(data, source_name):
    urls = data["urls"]
    scored = [u for u in urls if u["score"] is not None]
    counts = {}
    for u in urls:
        for f in u["fails"]:
            counts[f] = counts.get(f, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:8]
    widest = top[0][1] if top else 1
    bars = "".join('<div><span style="width:52px">%s</span><i style="width:%dpx"></i>%d URL</div>'
                   % (k, max(6, int(220 * v / widest)), v) for k, v in top) or \
        '<div class="sub">Chưa có item FAIL nào được ghi.</div>'
    avg = ("%.1f/%d" % (sum(u["score"] for u in scored) / len(scored), data["max"])) if scored else "—"
    cards = [(len(urls), "URL trong batch"), (avg, "điểm trung bình"),
             (sum(1 for u in urls if u["p0"] == "fail"), "URL rớt P0"),
             (sum(1 for u in urls if u["fails"]), "URL còn item FAIL")]
    ax_names = sorted({k for r in data["ax"] for k in r["items"]})
    mx_names = sorted({k for r in data["mx"] for k in r["items"]})
    payload = {"urls": urls, "cols": item_columns(data["max"])}
    nonce = secrets.token_urlsafe(16)
    meta = data["meta"]
    title = "Onpage batch %s — %s" % (meta.get("batch", ""), meta.get("client", ""))
    return ("""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-%(n)s'">
<title>%(title)s</title><style nonce="%(n)s">%(css)s</style></head><body>
<header><h1>%(title)s</h1><div class="sub">Nguồn: %(src)s · tier /%(max)d · bản xem, file .md là bản gốc</div>
<div class="cards">%(cards)s</div><button id="theme">Sáng / tối</button></header>
<main>
<h2>Bảng nhiệt URL × item <span class="sub" id="count"></span></h2>
<div class="sub legend">Bấm tiêu đề cột URL, P0, Điểm để sắp xếp; bấm một item để lọc URL rớt item đó.
<span style="background:var(--ok)"></span>đạt<span style="background:var(--bad)"></span>rớt<span style="background:var(--todo)"></span>chưa chấm<span style="background:var(--na)"></span>không áp dụng</div>
<div class="wrap"><table id="heat"></table></div>
<h2>Item rớt nhiều nhất</h2><div class="bars">%(bars)s</div>
<h2>MX — nâng cấp định dạng (chấm riêng)</h2>%(mx)s
<h2>AX — AI-search (chấm riêng)</h2>%(ax)s
</main><script type="application/json" id="data">%(data)s</script><script nonce="%(n)s">%(js)s</script></body></html>"""
            % {"n": nonce, "title": html.escape(title), "css": CSS, "src": html.escape(source_name),
               "max": data["max"],
               "cards": "".join('<div class="card"><b>%s</b><span>%s</span></div>' % c for c in cards),
               "bars": bars, "mx": side_table(data["mx"], mx_names), "ax": side_table(data["ax"], ax_names),
               "data": json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"), "js": JS})


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) >= 2 else 2
    src = Path(argv[1]).resolve()
    out = None
    if len(argv) >= 4 and argv[2] == "--out":
        out = Path(argv[3]).resolve()
    elif len(argv) > 2:
        print("Tham số không hợp lệ: %s" % " ".join(argv[2:]), file=sys.stderr)
        return 2
    if not src.is_file():
        print("Không thấy file: %s" % src, file=sys.stderr)
        return 2
    data = parse(src.read_text(encoding="utf-8"))
    if not data["urls"]:
        print("Không tìm thấy bảng 'Bảng batch — score per URL' có cột URL trong %s" % src.name, file=sys.stderr)
        return 1
    out = out or src.with_name(src.stem + ".view.html")
    out.write_text(render(data, src.name), encoding="utf-8")
    print("✓ %s — %d URL, %d dòng MX, %d dòng AX" % (out, len(data["urls"]), len(data["mx"]), len(data["ax"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
