#!/usr/bin/env python3
"""File HTML để người duyệt sửa chữ trực tiếp trên bản sao của trang (nút E), rồi xuất bản sửa cho chế độ khối nguồn.

Dựng:  python3 sua_truc_tiep.py build --html <trang.html> --page <mã trang> --title "<tên trang>" --out <file sửa.html>
         [--base https://site/] [--meta-title "..."] [--meta-desc "..."]
  <trang.html>: HTML đã render của trang (curl) hoặc mảnh nội dung. Script gắn data-b cho từng khối chữ lá (p, h1–h6, li, td, th,
  figcaption, blockquote, dt, dd, summary, caption), bỏ script của trang, chèn lớp sửa (assets/edit-layer.*).
  Mở file bằng Chrome, bấm E để sửa, "Tải HTML" hoặc "Sao chép cho Claude" (dòng cuối ED-JSON).
Xuất:  python3 sua_truc_tiep.py apply <file HTML đã tải hoặc file chữ có ED-JSON> --out <thư mục edits>
  Ghi mỗi khối sửa một file JSON dạng collection `edits` của chế độ khối nguồn: {page, block, before, text, status, dup}.
  `dup` = "k#n" khi chữ gốc của khối xuất hiện nhiều lần trên trang: khối là lần thứ n (đếm từ 1) của chữ đó.
  Chữ đã chuẩn hoá Unicode NFC và gộp khoảng trắng. meta (title, desc) ghi thành khối <page>-meta-title, <page>-meta-desc.
"""
import argparse
import html
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
BLOCK = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "figcaption", "blockquote", "dt", "dd", "summary", "caption"}
SKIP = {"script", "style", "svg", "template", "noscript"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def norm(s):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s).strip())


class Blocks(HTMLParser):
    """Tìm khối chữ lá: thẻ BLOCK có chữ và không chứa thẻ BLOCK khác. Ghi vị trí '>' của thẻ mở và đầu thẻ đóng."""

    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.src, self.stack, self.out, self.skip = src, [], [], 0
        lines = src.split("\n")
        self.off = [0]
        for ln in lines:
            self.off.append(self.off[-1] + len(ln) + 1)

    def pos(self):
        line, col = self.getpos()
        return self.off[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if tag == "br" and not self.skip:
                for b in self.stack:
                    b["text"].append(" ")
            return
        if tag in SKIP:
            self.skip += 1
        p = self.pos()
        gt = p + len(self.get_starttag_text()) - 1
        if tag in BLOCK:
            for b in self.stack:
                if b["tag"] in BLOCK:
                    b["leaf"] = False
        self.stack.append({"tag": tag, "gt": gt, "text": [], "leaf": True})

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                break
        else:
            return
        node = self.stack[i]
        del self.stack[i:]
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        t = norm("".join(node["text"]))
        if tag in BLOCK and node["leaf"] and t:
            self.out.append({"gt": node["gt"], "end": self.pos(), "text": t})

    def handle_data(self, data):
        if self.skip:
            return
        for b in self.stack:
            b["text"].append(data)


def annotate(src, page):
    p = Blocks(src)
    p.feed(src)
    p.close()
    blocks = sorted(p.out, key=lambda b: b["gt"])
    for i, b in enumerate(blocks, 1):
        b["id"] = f"{page}-{i:03d}"
    for b in sorted(blocks, key=lambda b: -b["gt"]):
        inner = src[b["gt"] + 1:b["end"]]
        attrs = f' data-b="{b["id"]}" data-t="{html.escape(b["text"])}" data-o="{html.escape(inner)}"'
        src = src[:b["gt"]] + attrs + src[b["gt"]:]
    return src, blocks


def build(a):
    raw = Path(a.html).read_text(encoding="utf-8")
    raw = re.sub(r"<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
    body = re.search(r"<body\b[^>]*>(.*)</body>", raw, re.S | re.I)
    head = re.search(r"<head\b[^>]*>(.*)</head>", raw, re.S | re.I)
    frag, blocks = annotate(body.group(1) if body else raw, a.page)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    meta = {"title": a.meta_title or "", "desc": a.meta_desc or ""}
    src = json.dumps({"page": a.page, "title": a.title, "builtAt": now, "meta": meta}, ensure_ascii=False).replace("<", "\\u003c")
    e = html.escape
    keep_head = re.sub(r"<title>.*?</title>|<meta[^>]+robots[^>]*>|<base\b[^>]*>", "", head.group(1), flags=re.S | re.I) if head else ""
    doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
{f'<base href="{e(a.base)}">' if a.base else ''}
<title>Sửa nội dung: {e(a.title)}</title>
{keep_head}
<style>{(ASSETS / 'edit-layer.css').read_text(encoding='utf-8')}</style>
<script type="application/json" id="ed-src">{src}</script>
<script type="application/json" id="ed-edits">{{}}</script>
</head>
<body class="ed-root">
{frag}
<button type="button" class="ed-btn" id="ed-btn" aria-pressed="false" title="Sửa nội dung (phím E)">E<span class="ed-badge" id="ed-badge"></span></button>
<span class="ed-hint" id="ed-hint">Bấm E để sửa chữ</span>
<div class="ed-panel" id="ed-panel" hidden>
<h6>Sửa nội dung: {e(a.title)}</h6>
<p>Bấm vào chữ để sửa, Enter để xong. Chỗ đã sửa có viền vàng. Đã sửa <span class="ed-n" id="ed-n">0</span> chỗ. Nháp tự lưu trong trình duyệt này.</p>
<div class="ed-row"><button type="button" class="pri" data-a="html">Tải HTML về Downloads (Cmd+S)</button></div>
<div class="ed-row"><button type="button" data-a="copy">Sao chép cho Claude</button><button type="button" data-a="off">Thoát (E)</button></div>
<details><summary>SEO title, meta description</summary>
<label for="ed-m-title">SEO title <span class="ed-cnt" id="ed-c-title"></span></label><input type="text" id="ed-m-title" value="{e(meta['title'])}">
<label for="ed-m-desc">Meta description <span class="ed-cnt" id="ed-c-desc"></span></label><textarea id="ed-m-desc" rows="3">{e(meta['desc'])}</textarea></details>
<details><summary>Ghi chú cho Claude</summary><label for="ed-note">Việc không sửa thẳng trên chữ được: đổi ảnh, thêm hoặc bỏ khối, in đậm, đổi link.</label><textarea id="ed-note"></textarea></details>
<details><summary>Danh sách chỗ đã sửa</summary><ul class="ed-list" id="ed-list"></ul></details>
<label class="ed-chk"><input type="checkbox" data-a="show"> Hiện khối ẩn</label>
<div class="ed-row" style="margin-top:8px"><button type="button" class="warn" data-a="reset">Bỏ hết bản sửa</button></div>
<div class="ed-msg" id="ed-msg" role="status"></div>
</div>
<script>{(ASSETS / 'edit-layer.js').read_text(encoding='utf-8')}</script>
</body>
</html>
"""
    Path(a.out).write_text(doc, encoding="utf-8")
    dups = {}
    for b in blocks:
        dups[b["text"]] = dups.get(b["text"], 0) + 1
    print(f"{a.out}: {len(blocks)} khối, {sum(1 for v in dups.values() if v > 1)} chữ lặp nhiều khối")
    return 0


def load_saved(path):
    s = Path(path).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="ed-edits">(.*?)</script>', s, re.S) or re.search(r"^ED-JSON: (.+)$", s, re.M)
    data = json.loads(m.group(1) or "{}") if m else {}
    blocks = re.findall(r'data-b="([^"]+)" data-t="([^"]*)"', s)  # data-t do JS ghi lại lúc mở đầu
    return data, [(b, html.unescape(t)) for b, t in blocks]


def apply(a):
    data, blocks = load_saved(a.saved)
    if not data.get("page"):
        sys.exit("File chưa có bản sửa: mở file, bấm E, sửa rồi bấm Tải HTML.")
    page = data["page"]
    occ, seen = {}, {}
    for b, t in blocks:
        t = norm(t)
        seen[t] = seen.get(t, 0) + 1
        occ[b] = (seen[t], t)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for e in data.get("edits", []):
        before, text = norm(e["before"]), norm(e["text"])
        rec = {"page": page, "block": e["b"], "before": before, "text": text, "status": "edited"}
        if e["b"] in occ and seen[occ[e["b"]][1]] > 1:
            rec["dup"] = f"k#{occ[e['b']][0]}"
        (out / f"{e['b']}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        print(f"{e['b']}{' ' + rec['dup'] if 'dup' in rec else ''}\n  cũ: {before}\n  mới: {text}")
        n += 1
    for k, v in (data.get("meta") or {}).items():
        bid = f"{page}-meta-{k}"
        (out / f"{bid}.json").write_text(json.dumps({"page": page, "block": bid, "before": norm(v["before"]), "text": norm(v["text"]), "status": "edited"}, ensure_ascii=False), encoding="utf-8")
        n += 1
    if data.get("note"):
        print(f"Ghi chú của người duyệt (xử lý tay): {data['note']}")
    print(f"{n} bản sửa -> {out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--html", required=True)
    b.add_argument("--page", required=True)
    b.add_argument("--title", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--base")
    b.add_argument("--meta-title")
    b.add_argument("--meta-desc")
    p = sub.add_parser("apply")
    p.add_argument("saved")
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return build(a) if a.cmd == "build" else apply(a)


if __name__ == "__main__":
    sys.exit(main())
