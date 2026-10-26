#!/usr/bin/env python3
"""the_link.py - sửa link trong thẻ (markdown và raw HTML) rồi đếm lại luật link.

Lệnh:
  unlink    gỡ link tới một đích, giữ chữ anchor
  reanchor  đổi chữ anchor của link tới một đích
  to-sc     gỡ link ở main content, đặt lại ở một mục supplementary content (SC)
  check     chỉ đếm luật, không sửa

Luật đếm lại sau mỗi lần sửa (references/link-placement.md §1, anchor-rules.md §2):
  R1  mỗi đích tối đa 1 link trong một tài liệu (link mảnh #... tính cùng đích)
  R2  mỗi mục H2 thuộc main content (MC) nhận tối đa 1 link mới
  R3  một chữ anchor tối đa 3 lần (trong các file đưa vào)
  Cảnh báo: link nằm ở mở bài trước H2 đầu.

Xử lý: &amp;, NBSP (U+00A0 và &nbsp;), NFC/NFD tiếng Việt, <span> lồng trong <a>, href tuyệt đối hay tương đối,
dấu nháy đơn hay kép, anchor markdown có dấu ngoặc vuông lồng. Bỏ qua link trong comment HTML, <script>, <style>,
khối code markdown.

Mặc định là dry-run: in diff, không ghi file. Ghi bằng --write (tạo bản .bak-<giờ>) hoặc --out FILE_MỚI.
Chỉ ghi khi sửa không sinh vi phạm mới. Dùng --allow-violations để ghi dù có vi phạm mới.

Mã thoát: 0 đạt · 1 lỗi thao tác (không tìm thấy, mơ hồ, lỗi file) · 2 sai tham số · 3 có vi phạm luật.

Dùng như thư viện: from the_link import unlink_text, reanchor_text, to_sc_text, analyze.
Ví dụ:
  the_link.py unlink the.md --target /dich-vu-seo/ --host vidu.vn
  the_link.py reanchor the.md --target /dich-vu-seo/ --old "dịch vụ SEO" --new "dịch vụ SEO & GEO" --write
  the_link.py to-sc the.md --target /bang-gia/ --anchor "bảng giá" --to-h2 "câu hỏi"
  the_link.py check a.md b.html --base a_truoc.md
"""
import argparse
import datetime
import difflib
import html
import json
import os
import re
import sys
import unicodedata
from bisect import bisect_right

SC_DEFAULT = (r"faq|câu hỏi|hỏi đáp|kết luận|lời kết|tổng kết|tóm lại|giới thiệu (?:về )?(?:công ty|doanh nghiệp|chúng tôi)"
              r"|về chúng tôi|dịch vụ của (?:công ty|chúng tôi)|đọc thêm|bài viết liên quan|liên hệ")

OPEN_A = re.compile(r"<a(?=[\s>/])(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", re.I)
CLOSE_A = re.compile(r"</a\s*>", re.I)
MD_LINK = re.compile(r"\[((?:[^\[\]\n]|\[[^\[\]\n]*\])+)\]\(\s*(<[^>\n]*>|(?:[^()\s]|\([^()\n]*\))+)(\s+\"[^\"\n]*\")?\s*\)")
MD_HEAD = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)
HTML_HEAD = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>", re.I | re.S)
TAG = re.compile(r"<[^>]*>")
NBSP_INNER = r"\s|&nbsp;|&#0*160;|&#x0*a0;"


class Err(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


# ---------- chuẩn hoá chuỗi ----------
def norm_keep(s):
    """Giữ hoa thường: bỏ thẻ, giải mã entity, NBSP thành cách, NFC, gộp khoảng trắng."""
    s = html.unescape(TAG.sub("", s or ""))
    s = unicodedata.normalize("NFC", s.replace(" ", " "))
    return re.sub(r"\s+", " ", s).strip()


def norm(s):
    return norm_keep(s).casefold()


def char_pat(c):
    if c == "&":
        return r"(?:&amp;|&#0*38;|&#x0*26;|&)"
    forms = sorted({c, unicodedata.normalize("NFC", c), unicodedata.normalize("NFD", c)}, key=len, reverse=True)
    if len(forms) == 1:
        return re.escape(c)
    return "(?:" + "|".join(re.escape(f) for f in forms) + ")"


def flex_re(old, allow_tags, ignore_case=False):
    toks = norm_keep(old).split(" ")
    if not toks or toks == [""]:
        raise Err("chữ cần tìm đang rỗng", 2)
    sep = "(?:" + NBSP_INNER + (r"|<[^>]*>" if allow_tags else "") + ")+"
    return re.compile(sep.join("".join(char_pat(c) for c in t) for t in toks), re.I if ignore_case else 0)


def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- mask: bỏ phần không phải nội dung ----------
def _blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def mask(text):
    t = re.sub(r"<!--.*?-->", _blank, text, flags=re.S)
    t = re.sub(r"<(script|style)\b.*?</\1\s*>", _blank, t, flags=re.S | re.I)
    t = re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$", _blank, t)
    t = re.sub(r"(?<!`)(`+)(?!`)[^\n]*?(?<!`)\1(?!`)", _blank, t)
    return t


# ---------- đích ----------
def dest_of(href, hosts):
    """Trả (dest, frag). dest None nếu không phải link tới trang (tel, mailto, javascript, #frag)."""
    h = html.unescape((href or "").strip().strip("<>"))
    if not h or h.startswith("#") or re.match(r"^(tel|mailto|sms|javascript|data):", h, re.I):
        return None, None
    h, _, frag = h.partition("#")
    if h.startswith("//"):
        h = "https:" + h
    m = re.match(r"^https?://([^/?#]+)(.*)$", h, re.I)
    if m:
        host = m.group(1).lower()
        host = host[4:] if host.startswith("www.") else host
        rest = m.group(2) or "/"
        if host in hosts:
            h = rest if rest.startswith("/") else "/" + rest
        else:
            h = "https://" + host + (rest.rstrip("/") if rest != "/" else "")
            return h, frag or None
    if h.startswith("/"):
        h = h.rstrip("/") or "/"
    return h or "/", frag or None


def target_spec(target, hosts):
    d, f = dest_of(target, hosts)
    if d is None:
        raise Err("--target không phải URL trang: %r" % target, 2)
    return d, f


def get_attr(tag_text, name):
    m = re.search(r"\b" + name + r"\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", tag_text, re.I)
    return next((g for g in m.groups() if g is not None), None) if m else None


# ---------- tìm link ----------
class Link(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def find_links(text, hosts):
    m = mask(text)
    links = []
    opens = list(OPEN_A.finditer(m))
    for i, o in enumerate(opens):
        c = CLOSE_A.search(m, o.end())
        if not c or (i + 1 < len(opens) and opens[i + 1].start() < c.start()):
            continue
        tag = text[o.start():o.end()]
        href = get_attr(tag, "href")
        dest, frag = dest_of(href, hosts) if href is not None else (None, None)
        inner = text[o.end():c.start()]
        links.append(Link(kind="html", start=o.start(), end=c.end(), in_s=o.end(), in_e=c.start(), href=href, dest=dest,
                          frag=frag, open_tag=tag, anchor=norm_keep(inner), inner=inner, md_dest=None))
    spans = [(l.start, l.end) for l in links]
    for mm in MD_LINK.finditer(m):
        if mm.start() > 0 and m[mm.start() - 1] == "!":
            continue
        if any(s <= mm.start() < e for s, e in spans):
            continue
        href = mm.group(2)
        dest, frag = dest_of(href, hosts)
        links.append(Link(kind="md", start=mm.start(), end=mm.end(), in_s=mm.start(1), in_e=mm.end(1), href=href, dest=dest,
                          frag=frag, open_tag=None, anchor=norm_keep(text[mm.start(1):mm.end(1)]),
                          inner=text[mm.start(1):mm.end(1)], md_dest=text[mm.start(2):mm.end(3) if mm.group(3) else mm.end(2)]))
    links.sort(key=lambda l: l.start)
    return links


# ---------- mục H2 ----------
def sections(text, sc_re, sc_last):
    """Danh sách mục: {title, start, end, zone}. Mục 0 là mở bài (trước H2 đầu) khi tài liệu có H2."""
    m = mask(text)
    heads = []
    for h in MD_HEAD.finditer(m):
        if len(h.group(1)) == 2:
            heads.append((h.start(), h.end(), norm(h.group(2))))
    for h in HTML_HEAD.finditer(m):
        if h.group(1) == "2":
            heads.append((h.start(), h.end(), norm(h.group(2))))
    heads.sort()
    if not heads:
        return [{"title": None, "start": 0, "end": len(text), "zone": "?", "head_end": 0}], False
    secs = [{"title": None, "start": 0, "end": heads[0][0], "zone": "MC", "head_end": 0}]
    for i, (s, he, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        zone = "SC" if (sc_re.search(title) or i >= len(heads) - sc_last) else "MC"
        secs.append({"title": title, "start": s, "end": end, "zone": zone, "head_end": he})
    return secs, True


def sec_index(secs, pos):
    return max(0, bisect_right([s["start"] for s in secs], pos) - 1)


# ---------- phân tích luật ----------
def describe(text, l, secs):
    i = sec_index(secs, l.start)
    return {"kind": l.kind, "dest": l.dest, "frag": l.frag, "href": l.href, "anchor": l.anchor,
            "dong": text.count("\n", 0, l.start) + 1, "muc": secs[i]["title"], "vung": secs[i]["zone"]}


def analyze(texts, hosts=(), base_texts=None, sc_last=2, sc_pattern=SC_DEFAULT, max_anchor=3, site_anchors=None, allow_multi=()):
    """texts: {tên: text}. base_texts: {tên: text} bản trước khi sửa, để biết link nào mới. Trả dict kết quả."""
    hosts = _hosts(hosts)
    sc_re = re.compile(sc_pattern, re.I)
    viol, warn, anchor_count = [], [], dict(site_anchors or {})
    allow = set(dest_of(a, hosts)[0] for a in allow_multi)
    n_links = 0
    for name, text in texts.items():
        links = find_links(text, hosts)
        secs, has_h2 = sections(text, sc_re, sc_last)
        base_pairs = None
        if base_texts is not None and name in base_texts:
            base_pairs = set((l.dest, norm(l.anchor)) for l in find_links(base_texts[name], hosts))
        by_dest = {}
        mc_new = {}
        for l in links:
            if l.dest is None:
                continue
            n_links += 1
            by_dest.setdefault(l.dest, []).append(l)
            a = norm(l.anchor)
            if a:
                anchor_count[a] = anchor_count.get(a, 0) + 1
            is_new = base_pairs is None or (l.dest, a) not in base_pairs
            i = sec_index(secs, l.start)
            if has_h2 and secs[i]["zone"] == "MC":
                if i == 0:
                    if is_new:
                        warn.append({"luat": "mo_bai", "file": name, "dest": l.dest,
                                     "msg": "link nằm ở mở bài trước H2 đầu (dòng %d)" % (text.count("\n", 0, l.start) + 1)})
                elif is_new:
                    mc_new.setdefault(i, []).append(l)
        for d, ls in by_dest.items():
            if len(ls) > 1 and d not in allow:
                viol.append({"luat": "R1", "key": "R1|%s|%s" % (name, d), "file": name, "dest": d, "so_link": len(ls),
                             "msg": "%s: %d link tới %s (dòng %s). Giữ 1, gỡ phần còn lại hoặc ghi lý do riêng." % (
                                 name, len(ls), d, ", ".join(str(text.count("\n", 0, l.start) + 1) for l in ls))})
        for i, ls in mc_new.items():
            if len(ls) > 1:
                viol.append({"luat": "R2", "key": "R2|%s|%s" % (name, secs[i]["title"]), "file": name, "muc": secs[i]["title"],
                             "so_link": len(ls),
                             "msg": "%s: mục H2 %r thuộc MC có %d link mới (tối đa 1)." % (name, secs[i]["title"], len(ls))})
        if not has_h2 and links:
            warn.append({"luat": "khong_co_h2", "file": name, "msg": "%s: không có H2, bỏ qua R2 và vùng MC/SC." % name})
    for a, n in sorted(anchor_count.items()):
        if n > max_anchor:
            viol.append({"luat": "R3", "key": "R3|%s" % a, "anchor": a, "so_lan": n,
                         "msg": "anchor %r xuất hiện %d lần (tối đa %d)." % (a, n, max_anchor)})
    return {"so_link": n_links, "vi_pham": viol, "canh_bao": warn}


# ---------- thao tác sửa ----------
def _match(links, spec, anchor=None, contains=False):
    d, f = spec
    out = [l for l in links if l.dest == d and (f is None or l.frag == f)]
    if anchor is not None:
        a = norm(anchor)
        out = [l for l in out if (a in norm(l.anchor) if contains else norm(l.anchor) == a)]
    return out


def _pick(text, cands, secs, nth, all_, what):
    if not cands:
        raise Err("không tìm thấy link để %s" % what)
    if nth is not None:
        if not 1 <= nth <= len(cands):
            raise Err("--nth %d ngoài khoảng 1..%d" % (nth, len(cands)))
        return [cands[nth - 1]]
    if len(cands) > 1 and not all_:
        lst = "; ".join("#%d dòng %d [%s] %r" % (i + 1, describe(text, l, secs)["dong"], l.kind, l.anchor)
                         for i, l in enumerate(cands))
        raise Err("có %d link khớp, chưa rõ gỡ link nào: %s. Dùng --nth N hoặc --all." % (len(cands), lst))
    return cands


def _apply(text, edits):
    for s, e, r in sorted(edits, key=lambda x: -x[0]):
        text = text[:s] + r + text[e:]
    return text


def unlink_text(text, target, hosts=(), anchor=None, contains=False, nth=None, all_=False, sc_last=2, sc_pattern=SC_DEFAULT):
    hosts = _hosts(hosts)
    links = find_links(text, hosts)
    secs, _ = sections(text, re.compile(sc_pattern, re.I), sc_last)
    picked = _pick(text, _match(links, target_spec(target, hosts), anchor, contains), secs, nth, all_, "gỡ")
    edits = [(l.start, l.end, l.inner) for l in picked]
    return _apply(text, edits), [dict(describe(text, l, secs), viec="gỡ link") for l in picked]


def _hosts(hosts):
    return set((h.lower()[4:] if h.lower().startswith("www.") else h.lower()) for h in hosts)


def _reanchor_inner(l, rx, new):
    """Trả inner mới, hoặc None nếu không khớp. Không bao giờ xoá thẻ trong inner."""
    inner = l.inner
    m = rx.search(inner)
    if not m:
        return None
    if l.kind == "md":
        if re.search(r"[\[\]]", new):
            raise Err("anchor mới chứa [ hoặc ] trong link markdown")
        return inner[:m.start()] + new + inner[m.end():]
    seg = re.split(r"(<[^>]*>)", inner[m.start():m.end()])
    newh = html_escape(new)
    out, put = [], False
    for part in seg:
        if part.startswith("<") and part.endswith(">"):
            out.append(part)
        elif not put and part:
            out.append(newh)
            put = True
    return inner[:m.start()] + "".join(out) + inner[m.end():]


def reanchor_text(text, target, old, new, hosts=(), nth=None, all_=False, ignore_case=False, sc_last=2, sc_pattern=SC_DEFAULT):
    hosts = _hosts(hosts)
    links = find_links(text, hosts)
    secs, _ = sections(text, re.compile(sc_pattern, re.I), sc_last)
    rx = {k: flex_re(old, k == "html", ignore_case) for k in ("md", "html")}
    cands = [l for l in _match(links, target_spec(target, hosts)) if rx[l.kind].search(l.inner)]
    picked = _pick(text, cands, secs, nth, all_, "đổi anchor %r" % old)
    edits = []
    for l in picked:
        edits.append((l.in_s, l.in_e, _reanchor_inner(l, rx[l.kind], new)))
    info = [dict(describe(text, l, secs), viec="đổi anchor", anchor_moi=new) for l in picked]
    return _apply(text, edits), info


def _plain_mask(text):
    """Chỉ chữ thường: bỏ thẻ, link, tiêu đề, code. Cùng độ dài với text."""
    m = mask(text)
    m = TAG.sub(_blank, m)
    for l in find_links(text, set()):
        m = m[:l.start] + re.sub(r"[^\n]", " ", m[l.start:l.end]) + m[l.end:]
    m = MD_HEAD.sub(_blank, m)
    return m


def to_sc_text(text, target, anchor, hosts=(), to_h2=None, nth=None, all_=False, occurrence=1, as_=None, ignore_case=False,
               sc_last=2, sc_pattern=SC_DEFAULT):
    hosts = _hosts(hosts)
    sc_re = re.compile(sc_pattern, re.I)
    links = find_links(text, hosts)
    secs0, _ = sections(text, sc_re, sc_last)
    picked = _pick(text, _match(links, target_spec(target, hosts)), secs0, nth, all_, "chuyển xuống SC")
    if len(picked) != 1:
        raise Err("to-sc chỉ chuyển 1 link mỗi lần; dùng --nth để chọn")
    src = picked[0]
    t2 = _apply(text, [(src.start, src.end, src.inner)])
    secs, has_h2 = sections(t2, sc_re, sc_last)
    if not has_h2:
        raise Err("tài liệu không có H2, không xác định được mục SC")
    if to_h2:
        rh = re.compile(to_h2, re.I)
        dests = [s for s in secs[1:] if rh.search(s["title"])]
        if len(dests) != 1:
            raise Err("--to-h2 %r khớp %d mục (cần đúng 1): %s" % (to_h2, len(dests), [s["title"] for s in dests]))
    else:
        dests = [s for s in reversed(secs[1:]) if s["zone"] == "SC"]
        if not dests:
            raise Err("không có mục SC nào")
    pm = _plain_mask(t2)
    rx = flex_re(anchor, False, ignore_case)
    m = dest = None
    for d in dests:
        hits = [h for h in rx.finditer(pm, d["head_end"], d["end"]) if "<" not in t2[h.start():h.end()]]
        if len(hits) >= occurrence:
            m, dest = hits[occurrence - 1], d
            break
    if m is None:
        raise Err("không thấy chữ %r trong mục SC %s (chưa nằm trong link khác). Sửa câu trước, hoặc chọn --to-h2 khác." % (
            anchor, [d["title"] for d in dests]))
    kind = as_ or src.kind
    got = t2[m.start():m.end()]
    if kind == "md":
        if re.search(r"[\[\]]", got):
            raise Err("chữ khớp chứa [ hoặc ]")
        md_dest = src.md_dest or ("%s" % src.href)
        rep = "[%s](%s)" % (got, md_dest)
    else:
        tag = src.open_tag or '<a href="%s">' % html_escape(src.href or "")
        rep = tag + got + "</a>"
    t3 = t2[:m.start()] + rep + t2[m.end():]
    desc = describe(text, src, secs0)
    return t3, [dict(desc, viec="gỡ link ở %s" % desc["vung"]),
                {"viec": "đặt link ở mục SC %r" % dest["title"], "anchor": got, "dest": src.dest}]


# ---------- CLI ----------
def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def violation_keys(rep):
    return set(v["key"] for v in rep["vi_pham"])


def cmd_check(a):
    texts = {p: read(p) for p in a.files}
    base = None
    if a.base:
        if len(a.files) != 1:
            raise Err("--base chỉ dùng với 1 file", 2)
        base = {a.files[0]: read(a.base)}
    sa = json.load(open(a.site_anchors, encoding="utf-8")) if a.site_anchors else None
    rep = analyze(texts, a.host, base, a.sc_last, a.sc_h2, a.max_anchor, sa, a.allow_multi)
    emit(a, rep, [], None)
    return 3 if rep["vi_pham"] else 0


def emit(a, rep, info, diff, extra=None):
    if a.json:
        out = dict(rep)
        out["thay_doi"] = info
        out.update(extra or {})
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    for i in info:
        print("- %s: dòng %s · %s · %r%s" % (i["viec"], i.get("dong", "-"), i.get("dest"), i.get("anchor"),
                                           " → %r" % i["anchor_moi"] if "anchor_moi" in i else ""))
    if diff:
        sys.stdout.write("".join(diff))
        if not diff[-1].endswith("\n"):
            print()
    print("Số link tính luật: %d" % rep["so_link"])
    for v in rep["vi_pham"]:
        print("VI PHẠM %s: %s" % (v["luat"], v["msg"]))
    for w in rep["canh_bao"]:
        print("Cảnh báo %s: %s" % (w["luat"], w["msg"]))
    if not rep["vi_pham"]:
        print("Luật R1-R3: đạt.")
    for line in (extra or {}).get("ghi_chu", []):
        print(line)


def cmd_edit(a):
    if a.write and a.out:
        raise Err("chọn --write hoặc --out, không dùng cả hai", 2)
    if a.file == "-" and a.write:
        raise Err("không dùng --write với stdin; dùng --out", 2)
    text = read(a.file)
    common = dict(hosts=a.host, sc_last=a.sc_last, sc_pattern=a.sc_h2)
    try:
        if a.cmd == "unlink":
            new, info = unlink_text(text, a.target, anchor=a.anchor, contains=a.contains, nth=a.nth, all_=a.all, **common)
        elif a.cmd == "reanchor":
            new, info = reanchor_text(text, a.target, a.old, a.new, nth=a.nth, all_=a.all, ignore_case=a.ignore_case, **common)
        else:
            new, info = to_sc_text(text, a.target, a.anchor, to_h2=a.to_h2, nth=a.nth, all_=a.all, occurrence=a.occurrence,
                                   as_=a.as_, ignore_case=a.ignore_case, **common)
    except Err as e:
        if a.missing_ok and "không tìm thấy link" in str(e):
            print("Không có gì để đổi (--missing-ok): %s" % e)
            return 0
        raise
    sa = json.load(open(a.site_anchors, encoding="utf-8")) if a.site_anchors else None
    kw = dict(hosts=a.host, sc_last=a.sc_last, sc_pattern=a.sc_h2, max_anchor=a.max_anchor, site_anchors=sa,
              allow_multi=a.allow_multi)
    before = analyze({a.file: text}, **kw)
    after = analyze({a.file: new}, base_texts={a.file: text}, **kw)
    fresh = [v for v in after["vi_pham"] if v["key"] not in violation_keys(before)]
    diff = list(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "trước", "sau", n=1))
    notes, rc = [], 0
    if fresh and not a.allow_violations:
        rc = 3
        notes.append("Vi phạm mới do lần sửa này: %d. Không ghi file. Dùng --allow-violations nếu chấp nhận." % len(fresh))
    elif a.write:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if not a.no_backup:
            bak = "%s.bak-%s" % (a.file, stamp)
            with open(bak, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            notes.append("Đã tạo bản lưu %s" % bak)
        with open(a.file, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        notes.append("Đã ghi %s" % a.file)
    elif a.out:
        if a.out == "-":
            sys.stdout.write(new)
            return rc
        if os.path.exists(a.out):
            raise Err("--out %s đã tồn tại, không ghi đè" % a.out)
        with open(a.out, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        notes.append("Đã ghi %s" % a.out)
    else:
        notes.append("Dry-run: chưa ghi gì. Thêm --write hoặc --out để ghi.")
    after["vi_pham_moi"] = [v["key"] for v in fresh]
    emit(a, after, info, diff, {"ghi_chu": notes, "rc": rc})
    return rc


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, edit=True):
        sp.add_argument("--host", action="append", default=[], help="host của site (lặp được), vd vidu.vn; link tuyệt đối "
                        "tới host này được coi là link nội bộ")
        sp.add_argument("--sc-last", type=int, default=2, help="số H2 cuối tính là SC (mặc định 2)")
        sp.add_argument("--sc-h2", default=SC_DEFAULT, help="regex tên H2 thuộc SC (thêm vào luật 'H2 cuối')")
        sp.add_argument("--max-anchor", type=int, default=3, help="số lần tối đa của một anchor (mặc định 3)")
        sp.add_argument("--site-anchors", help="JSON {anchor: số lần} đã có ở file khác, cộng vào R3")
        sp.add_argument("--allow-multi", action="append", default=[], help="đích được phép có hơn 1 link (đã ghi lý do trong plan)")
        sp.add_argument("--json", action="store_true", help="in kết quả dạng JSON")

    def edit(sp):
        common(sp)
        sp.add_argument("file", help="file markdown hoặc HTML, '-' là stdin (chỉ dry-run hoặc --out)")
        sp.add_argument("--target", required=True, help="đích của link, vd /dich-vu-seo/ hoặc URL đầy đủ")
        sp.add_argument("--nth", type=int, help="chọn link thứ N khi có nhiều link khớp")
        sp.add_argument("--all", action="store_true", help="áp cho mọi link khớp")
        sp.add_argument("--write", action="store_true", help="ghi vào file, tạo bản .bak-<giờ>")
        sp.add_argument("--no-backup", action="store_true", help="với --write: không tạo bản .bak")
        sp.add_argument("--out", help="ghi ra file mới (không ghi đè); '-' in ra stdout")
        sp.add_argument("--allow-violations", action="store_true", help="ghi dù lần sửa sinh vi phạm luật mới")
        sp.add_argument("--missing-ok", action="store_true", help="không tìm thấy link thì thoát 0 (chạy lại an toàn)")
        sp.add_argument("--ignore-case", action="store_true")

    u = sub.add_parser("unlink", help="gỡ link, giữ chữ", description="Gỡ link tới --target, giữ chữ anchor và thẻ bên trong.")
    edit(u)
    u.add_argument("--anchor", help="chỉ gỡ link có anchor đúng chữ này")
    u.add_argument("--contains", action="store_true", help="--anchor khớp một phần")
    r = sub.add_parser("reanchor", help="đổi chữ anchor", description="Đổi chữ anchor của link tới --target. Giữ thẻ lồng như <span>.")
    edit(r)
    r.add_argument("--old", required=True, help="chữ cũ (một phần hoặc cả anchor)")
    r.add_argument("--new", required=True, help="chữ mới")
    s = sub.add_parser("to-sc", help="chuyển link xuống mục SC",
                       description="Gỡ link ở vị trí hiện tại, rồi bọc --anchor trong mục SC bằng cùng href. "
                       "Không thấy chữ trong mục SC thì dừng, không ghi.")
    edit(s)
    s.add_argument("--anchor", required=True, help="chữ có sẵn trong mục SC để bọc link")
    s.add_argument("--to-h2", help="regex tên H2 đích (mặc định: mục SC cuối)")
    s.add_argument("--occurrence", type=int, default=1, help="lần xuất hiện thứ N của chữ trong mục (mặc định 1)")
    s.add_argument("--as", dest="as_", choices=["md", "html"], help="dạng link mới (mặc định theo link cũ)")
    c = sub.add_parser("check", help="đếm luật, không sửa", description="Đếm R1-R3 trên một hoặc nhiều file. Nhiều file để R3 đếm chung.")
    common(c)
    c.add_argument("files", nargs="+")
    c.add_argument("--base", help="bản trước khi sửa (1 file): R2 chỉ tính link mới so với bản này")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return cmd_check(a) if a.cmd == "check" else cmd_edit(a)
    except Err as e:
        print("LỖI: %s" % e, file=sys.stderr)
        return e.code
    except (OSError, UnicodeDecodeError) as e:
        print("LỖI file: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
