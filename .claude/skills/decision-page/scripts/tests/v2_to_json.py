#!/usr/bin/env python3
"""Công cụ test: đọc trang v2 của đợt rà skill web và sinh cau-hoi.json tương ứng.

Chỉ dùng để tạo fixture web-skill-review.json. Trang v2 không ghi risk_if_skipped
và touches_live, nên bảng RISK bên dưới bổ sung hai trường này theo nội dung từng thẻ.
Chạy: python3 v2_to_json.py <v2.html> <thư mục fixtures>
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

RISK = {
    "s1": ("Anh tiếp tục nhận trang chờ quyết dựng tay, mỗi bản mất 10 đến 30 phút và có thể mất ghi chú.", False),
    "s2": ("Mỗi lần đổi tài khoản tốn 25 đến 46 phút, và memory vẫn giữ dòng sai về quyền ArtifactData.", False),
    "s3": ("Lead từ form có thể tiếp tục mất mà không ai biết.", False),
    "s4": ("Mỗi lần sửa giao diện sống tiếp tục tốn hàng trăm phút và nhiều vòng kiểm.", False),
    "s5": ("Việc anh đã giao tiếp tục bị quên và mốc giờ tiếp tục sai.", False),
    "l1": ("Phiên chính và cron tiếp tục đứng hàng trăm phút khi anh vắng.", True),
    "l2": ("Sau compact, báo cáo tiếp tục ra tiếng Anh và giờ ghi file tiếp tục lệch.", True),
    "l4": ("Lỗi glob zsh tiếp tục lặp lại ở mọi agent.", True),
    "u1": ("22 bản nâng cấp không được dựng, các lỗi đã đo vẫn còn.", False),
    "b1": ("Phiên dựng không có cách làm thống nhất, dễ chạy quá trần agent.", False),
}


def inl(s):
    s = re.sub(r"<code>(.*?)</code>", lambda m: "`" + m.group(1) + "`", s, flags=re.S)
    s = re.sub(r"<b>(.*?)</b>", lambda m: "**" + m.group(1) + "**", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def table(inner):
    rows = re.findall(r"<tr>(.*?)</tr>", inner, re.S)
    head = [inl(x) for x in re.findall(r"<th>(.*?)</th>", rows[0], re.S)]
    body, num = [], set()
    for r in rows[1:]:
        cells = re.findall(r'<td( class="n")?>(.*?)</td>', r, re.S)
        for i, (c, _) in enumerate(cells):
            if c:
                num.add(i)
        body.append([inl(t) for _, t in cells])
    return {"type": "table", "head": head, "rows": body, "num_cols": sorted(num)}


TOK = re.compile(
    r'(?P<ctx><ul class="ctx">(?P<ctxi>.*?)</ul>)'
    r'|(?P<muted><p class="muted">(?P<mutedi>.*?)</p>)'
    r'|(?P<stats><div class="stats">(?P<statsi>.*?)</div>\s*(?=<div class="tbl">|<h3>|<p|</section>))'
    r'|(?P<tbl><div class="tbl"><table>(?P<tbli>.*?)</table></div>)'
    r'|(?P<h3><h3>(?P<h3i>.*?)</h3>)', re.S)


def main(src, out):
    s = Path(src).read_text(encoding="utf-8")
    spec = {"project": "web-skill-review", "version": 2}
    spec["eyebrow"] = inl(re.search(r'<div class="eyebrow">(.*?)</div>', s, re.S).group(1))
    spec["title"] = inl(re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))
    spec["page_title"] = inl(re.search(r"<title>(.*?)</title>", s).group(1))
    spec["intro"] = inl(re.search(r'<p class="lede">(.*?)</p>', s, re.S).group(1))
    spec["key_note"] = inl(re.search(r'<div class="note key">(.*?)</div>', s, re.S).group(1))
    spec["answer_title"] = "Trả lời trang Duyệt skill web site-mau (artifact, bản 2):"
    spec["db"] = {"collection": "answers", "doc": "lead"}
    spec["report_html_file"] = "web-skill-review_bao-cao.fragment.html"
    spec["report_label"] = "Báo cáo đầy đủ"
    cards = []
    for m in re.finditer(r'<section class="card( info| done)?" id="(\w+)"( data-id="[^"]*" data-t="[^"]*")?>(.*?)</section>', s, re.S):
        kind = (m.group(1) or "").strip() or "question"
        cid = m.group(2)
        inner = m.group(4)
        h2 = re.search(r'<h2><span class="id">(.*?)</span> (.*?)</h2>', inner, re.S)
        c = {"id": cid, "label": inl(h2.group(1)), "title": inl(h2.group(2)), "kind": kind}
        dt = re.search(r'data-t="([^"]*)"', m.group(0))
        if dt:
            c["toc"] = html.unescape(dt.group(1))
        blocks = []
        for t in TOK.finditer(inner):
            if t.group("ctx"):
                items = [inl(x) for x in re.findall(r"<li>(.*?)</li>", t.group("ctxi"), re.S)]
                if kind == "question":
                    c["context"] = items
                else:
                    blocks.append({"type": "list", "items": items})
            elif t.group("muted"):
                blocks.append({"type": "p", "text": inl(t.group("mutedi"))})
            elif t.group("stats"):
                blocks.append({"type": "stats", "items": [
                    {"n": inl(a), "label": inl(b)} for a, b in re.findall(r"<b>(.*?)</b><span>(.*?)</span>", t.group("statsi"), re.S)]})
            elif t.group("tbl"):
                blocks.append(table(t.group("tbli")))
            elif t.group("h3"):
                blocks.append({"type": "h3", "text": inl(t.group("h3i"))})
        if blocks:
            c["blocks"] = blocks
        qs = []
        for q in re.finditer(r'<div class="q" data-q="(.*?)"><b>(.*?)</b><div class="opts">(.*?)</div></div>', inner, re.S):
            opts = []
            for o in re.finditer(r'<label( class="rec")?><input type="radio" name="\w+" value="(.*?)">(.*?)</label>', q.group(3), re.S):
                opts.append({"label": inl(o.group(3)), "value": html.unescape(o.group(2)), "recommended": bool(o.group(1))})
            qs.append({"short": html.unescape(q.group(1)), "text": inl(q.group(2)), "options": opts})
        if qs:
            c["questions"] = qs
            risk, live = RISK[cid]
            c["risk_if_skipped"] = risk
            c["touches_live"] = live
            ph = re.search(r'<textarea data-note="\w+" aria-label="[^"]*" placeholder="([^"]*)"', inner)
            c["note"] = {"placeholder": html.unescape(ph.group(1))} if ph else True
        cards.append(c)
    spec["cards"] = cards
    outd = Path(out)
    outd.mkdir(parents=True, exist_ok=True)
    (outd / "web-skill-review.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rep = re.search(r'<article class="report">\n?(.*?)\n?</article>', s, re.S).group(1)
    (outd / "web-skill-review_bao-cao.fragment.html").write_text(rep + "\n", encoding="utf-8")
    print("cards:", len(cards), "questions:", sum(len(c.get("questions", [])) for c in cards), "report bytes:", len(rep))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
