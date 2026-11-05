#!/usr/bin/env python3
"""Quét tất định HTML sống của một site WordPress: footprint comment, inline script/style, semantic HTML5.
Chạy: python3 -I scan_html.py <html_dir> <out_dir>
Ra: scan_html.json, scan_html.md, jev_comments.jsonl, jev_scripts.jsonl, jev_sections.jsonl, emb_scripts.jsonl
"""
import json
import os
import hashlib
import re
import subprocess
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

VI = re.compile(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵĂÂĐÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ]")
# Thuộc tính data-* riêng của site cần liệt kê đủ (theme, plugin tự viết), ví dụ FOOTPRINT_DATA_ATTRS="data-vidu-|data-scroll-to"
SITE_ATTRS = [s for s in os.environ.get("FOOTPRINT_DATA_ATTRS", "").split("|") if s]
LANDMARKS = ["header", "nav", "main", "article", "section", "aside", "footer", "form", "figure", "time", "h1", "h2", "h3", "h4", "h5", "h6", "b", "i", "strong", "em"]


JS_TYPES = {"", "module", "text/javascript", "application/javascript", "text/ecmascript",
            "application/ecmascript", "application/x-ecmascript", "application/x-javascript",
            "text/litespeed", "text/jscript", "text/livescript", "text/x-ecmascript", "text/x-javascript"}
JS_TYPES.update(f"text/javascript1.{n}" for n in range(6))


def script_type(s):
    return (s["attrs"].get("type") or "").split(";", 1)[0].strip().lower()


def parse_scripts(scripts):
    if not scripts:
        return {"parser": None, "results": []}
    payload = [{"text": s["text"], "type": script_type(s)} for s in scripts]
    try:
        run = subprocess.run(["node", str(Path(__file__).with_name("js_comments.mjs"))],
                             input=json.dumps(payload), text=True, capture_output=True, timeout=60)
        result = json.loads(run.stdout)
        if run.returncode or len(result.get("results", [])) != len(scripts):
            raise ValueError(result.get("error", "Số kết quả parser không khớp"))
        return result
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"parser": None, "results": [{"comments": [], "error": str(exc)} for _ in scripts]}


def css_comments(css):
    """Giữ offset gốc; bỏ qua chuỗi, escape và URL token."""
    i = 0
    while i < len(css):
        if css.startswith("/*", i):
            end = css.find("*/", i + 2)
            if end < 0:
                raise ValueError("Comment CSS chưa đóng")
            yield "block", css[i:end + 2], css[:i].count("\n") + 1
            i = end + 2
        elif css[i] in "\"'":
            quote = css[i]
            i += 1
            while i < len(css) and css[i] != quote:
                i += 2 if css[i] == "\\" else 1
            i += 1
        elif css[i] == "\\":
            i += 2
        elif css[i:i + 4].lower() == "url(" and (i == 0 or not re.match(r"[\w-]", css[i - 1])):
            i += 4
            quote = None
            while i < len(css):
                ch = css[i]
                if ch == "\\":
                    i += 2
                    continue
                if quote:
                    if ch == quote:
                        quote = None
                elif ch in "\"'":
                    quote = ch
                elif ch == ")":
                    i += 1
                    break
                i += 1
        else:
            i += 1


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.tags = Counter()
        self.ids = Counter()
        self.roles = []
        self.scripts = []  # dict(attrs, text, line)
        self.styles = []
        self.comments = []
        self.headings = []
        self.sections = []  # section/article/aside with first heading & text
        self.landmark_paths = []
        self.data_attrs = Counter()
        self.cur_script = None
        self.cur_style = None
        self.main_depth = 0
        self.body_text_len = 0
        self.in_body = False
        self.sec_stack = []
        self.empty_sections = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags[tag] += 1
        if "id" in a and a["id"]:
            self.ids[a["id"]] += 1
        for k in a:
            if k.startswith("data-"):
                self.data_attrs[k] += 1
        if "role" in a:
            self.roles.append((tag, a.get("role"), a.get("id") or a.get("class", "")[:60]))
        if tag == "body":
            self.in_body = True
        if tag in ("header", "nav", "main", "article", "section", "aside", "footer", "form"):
            path = "/".join(t for t in self.stack if t in ("header", "nav", "main", "article", "section", "aside", "footer", "body"))
            self.landmark_paths.append((tag, path, a.get("id") or "", (a.get("class") or "")[:80], self.getpos()[0]))
            if tag in ("section", "article", "aside"):
                self.sec_stack.append({"tag": tag, "line": self.getpos()[0], "id": a.get("id") or "", "class": (a.get("class") or "")[:80], "heading": None, "text": [], "depth": len(self.stack)})
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append([tag, self.getpos()[0], "", "/".join(t for t in self.stack if t in ("header", "nav", "main", "article", "section", "aside", "footer"))])
        if tag == "script":
            self.cur_script = {"attrs": a, "text": [], "line": self.getpos()[0]}
        if tag == "style":
            self.cur_style = {"attrs": a, "text": [], "line": self.getpos()[0]}
        if tag not in ("br", "img", "meta", "link", "input", "hr", "source", "path", "circle", "rect", "line", "polyline", "polygon", "use", "stop", "wbr", "area", "base", "col", "embed", "param", "track"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script" and self.cur_script is not None:
            self.cur_script["text"] = "".join(self.cur_script["text"])
            self.scripts.append(self.cur_script)
            self.cur_script = None
        if tag == "style" and self.cur_style is not None:
            self.cur_style["text"] = "".join(self.cur_style["text"])
            self.styles.append(self.cur_style)
            self.cur_style = None
        if tag in ("section", "article", "aside") and self.sec_stack:
            # đóng section gần nhất cùng tag
            for i in range(len(self.sec_stack) - 1, -1, -1):
                if self.sec_stack[i]["tag"] == tag:
                    s = self.sec_stack.pop(i)
                    txt = " ".join(" ".join(s["text"]).split())
                    s["text"] = txt[:400]
                    s["text_len"] = len(txt)
                    if len(txt) == 0:
                        self.empty_sections += 1
                    self.sections.append(s)
                    break
        if self.stack and tag in self.stack:
            # pop tới tag
            while self.stack:
                t = self.stack.pop()
                if t == tag:
                    break

    def handle_data(self, data):
        if self.cur_script is not None:
            self.cur_script["text"].append(data)
            return
        if self.cur_style is not None:
            self.cur_style["text"].append(data)
            return
        if self.headings and any(t in ("h1", "h2", "h3", "h4", "h5", "h6") for t in self.stack):
            self.headings[-1][2] += data
        for s in self.sec_stack:
            if s["heading"] is None and any(t in ("h1", "h2", "h3", "h4", "h5", "h6") for t in self.stack) and data.strip():
                s["heading"] = data.strip()[:120]
            s["text"].append(data)
        if self.in_body:
            self.body_text_len += len(data.strip())

    def handle_comment(self, data):
        self.comments.append((data.strip(), self.getpos()[0]))


def scan_file(path: Path):
    html = path.read_text(encoding="utf-8", errors="replace")
    p = P()
    p.feed(html)
    size = len(html.encode("utf-8"))
    inline_blocks = [s for s in p.scripts if s["text"].strip() and not any(k in s["attrs"] for k in ("src", "data-src"))]
    inline_scripts = [s for s in inline_blocks if script_type(s) in JS_TYPES]
    data_scripts = [s for s in inline_blocks if script_type(s) not in JS_TYPES]
    inline_js_bytes = sum(len(s["text"].encode()) for s in inline_scripts)
    inline_css_bytes = sum(len(s["text"].encode()) for s in p.styles)
    # comment trong JS/CSS inline
    comment_items = []
    comment_texts = []
    scan_errors = []
    for tag, block in (("script", p.cur_script), ("style", p.cur_style)):
        if block is not None:
            scan_errors.append({"where": tag, "block_id": block["attrs"].get("id") or f"noid@{block['line']}", "error": "Thẻ chưa đóng; chưa quét được nội dung"})
    parsed = parse_scripts(inline_scripts)
    for s, result in zip(inline_scripts, parsed["results"]):
        sid = s["attrs"].get("id") or f"noid@{s['line']}"
        if result.get("error"):
            scan_errors.append({"where": "script", "block_id": sid, "error": result["error"]})
        for kind, txt, ln in result["comments"]:
            comment_texts.append(txt)
            comment_items.append({"where": "script", "block_id": sid, "kind": kind, "text": txt.strip()[:400], "line": s["line"] + ln - 1, "vi": bool(VI.search(txt))})
    for s in p.styles:
        sid = s["attrs"].get("id") or f"noid@{s['line']}"
        try:
            for kind, txt, ln in css_comments(s["text"]):
                comment_texts.append(txt)
                comment_items.append({"where": "style", "block_id": sid, "kind": kind, "text": txt.strip()[:400], "line": s["line"] + ln - 1, "vi": bool(VI.search(txt))})
        except ValueError as exc:
            scan_errors.append({"where": "style", "block_id": sid, "error": str(exc)})
    html_comments = [{"where": "html", "text": t[:300], "line": ln, "vi": bool(VI.search(t))} for t, ln in p.comments]
    # heading outline + nhảy cấp
    outline = []
    prev = 0
    skips = 0
    for tag, ln, txt, hpath in p.headings:
        lvl = int(tag[1])
        if prev and lvl > prev + 1:
            skips += 1
        prev = lvl
        outline.append({"tag": tag, "line": ln, "text": " ".join(txt.split())[:100], "path": hpath})
    dup_ids = {k: v for k, v in p.ids.items() if v > 1}
    sections_no_heading = [s for s in p.sections if not s["heading"]]
    nested = defaultdict(int)
    for tag, lpath, _, _, _ in p.landmark_paths:
        if lpath.count(tag) >= 1:
            nested[f"{tag} trong {tag}"] += 1
        if tag == "main" and "main" in lpath:
            nested["main lồng main"] += 1
    return {
        "file": path.name,
        "bytes": size,
        "body_text_chars": p.body_text_len,
        "inline_scripts": len(inline_scripts),
        "inline_js_bytes": inline_js_bytes,
        "inline_data_scripts": len(data_scripts),
        "inline_data_bytes": sum(len(s["text"].encode("utf-8")) for s in data_scripts),
        "scan_complete": not scan_errors,
        "scan_errors": scan_errors,
        "js_parser": parsed["parser"],
        "_comment_texts": comment_texts,
        "_html_comment_texts": [t for t, _ in p.comments],
        "inline_styles": len(p.styles),
        "inline_css_bytes": inline_css_bytes,
        "script_ids": [s["attrs"].get("id") or f"noid@{s['line']}" for s in inline_scripts],
        "script_sizes": {(s["attrs"].get("id") or f"noid@{s['line']}"): len(s["text"].encode()) for s in inline_scripts},
        "style_ids": [s["attrs"].get("id") or f"noid@{s['line']}" for s in p.styles],
        "style_sizes": {(s["attrs"].get("id") or f"noid@{s['line']}"): len(s["text"].encode()) for s in p.styles},
        "comments_in_code": comment_items,
        "comments_in_code_vi": sum(1 for c in comment_items if c["vi"]),
        "html_comments": html_comments,
        "html_comments_vi": sum(1 for c in html_comments if c["vi"]),
        "tags": {t: p.tags.get(t, 0) for t in LANDMARKS},
        "roles": p.roles,
        "data_attrs_site": {k: v for k, v in p.data_attrs.items() if any(s in k for s in SITE_ATTRS)},
        "data_attrs_top": p.data_attrs.most_common(25),
        "dup_ids": dup_ids,
        "headings": outline,
        "heading_skips": skips,
        "sections": p.sections,
        "sections_total": len(p.sections),
        "sections_no_heading": len(sections_no_heading),
        "sections_empty": p.empty_sections,
        "nested_landmarks": dict(nested),
        "landmark_paths": p.landmark_paths,
        "_inline_scripts_raw": [{"id": s["attrs"].get("id") or f"noid@{s['line']}", "line": s["line"], "type": script_type(s), "text": s["text"]} for s in inline_scripts],
    }


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for f in sorted(src.glob("*.html")):
        results.append(scan_file(f))
    slim = []
    jev_comments, jev_scripts, jev_sections, emb_scripts = [], [], [], []
    seen_script = {}
    for r in results:
        page = r["file"]
        for i, c in enumerate(r["comments_in_code"]):
            jev_comments.append({"id": f"{page}#{c['where']}#{c['block_id']}#{i}", "state": {"page": page, "block": c["block_id"], "where": c["where"], "comment": c["text"]}})
        for i, c in enumerate(r["html_comments"]):
            jev_comments.append({"id": f"{page}#html#{i}", "state": {"page": page, "block": "html", "where": "html", "comment": c["text"]}})
        for s in r["_inline_scripts_raw"]:
            key = (s["type"], hashlib.sha256(s["text"].encode("utf-8")).hexdigest())
            if key in seen_script:
                continue
            seen_script[key] = page
            jev_scripts.append({"id": f"{page}#{s['id']}@{s['line']}", "state": {"page": page, "script_id": s["id"], "bytes": len(s["text"].encode("utf-8")), "code_head": s["text"][:1800]}})
            emb_scripts.append({"id": f"{page}#{s['id']}", "text": s["text"][:6000]})
        for i, s in enumerate(r["sections"]):
            if s["text_len"] < 20:
                continue
            jev_sections.append({"id": f"{page}#{s['tag']}@{s['line']}", "state": {"page": page, "tag": s["tag"], "heading": s["heading"] or "", "class": s["class"], "text": s["text"][:400], "text_len": s["text_len"]}})
        r2 = {k: v for k, v in r.items() if not k.startswith("_")}
        slim.append(r2)
    (out / "scan_html.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, rows in (("jev_comments.jsonl", jev_comments), ("jev_scripts.jsonl", jev_scripts), ("jev_sections.jsonl", jev_sections), ("emb_scripts.jsonl", emb_scripts)):
        with (out / name).open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    # bảng tóm tắt
    lines = ["# Quét tất định HTML sống", "", "| Trang | KB | inline JS (khối/KB) | inline CSS (khối/KB) | comment VI trong code | comment HTML VI | main | h1 | section | section không heading | section rỗng | article | aside | nav | nhảy cấp H | id trùng | role= |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in slim:
        t = r["tags"]
        lines.append(f"| {r['file']} | {r['bytes']//1024} | {r['inline_scripts']}/{r['inline_js_bytes']//1024} | {r['inline_styles']}/{r['inline_css_bytes']//1024} | {r['comments_in_code_vi']}/{len(r['comments_in_code'])} | {r['html_comments_vi']}/{len(r['html_comments'])} | {t['main']} | {t['h1']} | {t['section']} | {r['sections_no_heading']} | {r['sections_empty']} | {t['article']} | {t['aside']} | {t['nav']} | {r['heading_skips']} | {len(r['dup_ids'])} | {len(r['roles'])} |")
    lines.append("")
    incomplete = [r for r in slim if not r["scan_complete"]]
    lines.append(f"Quét comment hoàn tất: {len(slim) - len(incomplete)}/{len(slim)} trang. Trang lỗi không được kết luận sạch.")
    for r in incomplete:
        lines.append(f"- INCOMPLETE `{r['file']}`: {json.dumps(r['scan_errors'], ensure_ascii=False)}")
    lines.append("## Comment tiếng Việt lọt ra HTML công khai (gộp theo khối, bỏ trùng)")
    seen = set()
    for r in slim:
        for c in r["comments_in_code"] + r["html_comments"]:
            if not c["vi"]:
                continue
            key = c["text"][:120]
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"- `{r['file']}` {c.get('where')}#{c.get('block_id','html')} dòng {c['line']}: {c['text'][:200]}")
    (out / "scan_html.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"pages={len(slim)} jev_comments={len(jev_comments)} jev_scripts={len(jev_scripts)} jev_sections={len(jev_sections)}")
    if incomplete or not slim:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
