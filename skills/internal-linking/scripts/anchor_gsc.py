#!/usr/bin/env python3
"""anchor_gsc.py - liệt kê anchor ứng viên cho một trang đích từ query GSC đã xuất ra file, kèm kiểm luật anchor (offline).

Script không gọi API. File GSC lấy từ một trong các nguồn:
  - JSON của `gsc.sh query <property> <số ngày> page,query` ({"rows": [{"keys": [...], "clicks", "impressions", ...}]}).
    Thứ tự dimension mặc định là page,query. Dùng --dims query,page nếu file xuất theo thứ tự ngược.
  - CSV hoặc TSV có cột trang và cột query (tên cột tiếng Anh hoặc tiếng Việt). Cột clicks, impressions, position tuỳ chọn.
  - CSV xuất từ giao diện GSC sau khi lọc một trang (cột "Top queries" hoặc "Truy vấn hàng đầu"), không có cột trang.
    Khi đó mọi dòng tính cho --page, và script không kiểm được cờ trang_khac.

Kiểm mỗi query (references/anchor-rules.md §1, §2):
  trang_khac            trang khác nhận nhiều click hơn cho query này (cùng click thì so lượt hiển thị):
                        query chưa phải seed query của trang đích
  khong_co_trong_dich   luật 6: chữ query không có trong nội dung trang đích (cần --target-file)
  mo_bai_dich           luật 1: chữ query nằm trong đoạn đầu của trang đích (cần --target-file). Cờ này chỉ cảnh báo,
                        không làm dòng mất "dat": seed query thường có trong đoạn đầu, Claude quyết và ghi lý do
  khong_co_trong_nguon  luật 6: chữ query không có trong mục nguồn (cần --source-file, thêm --section để chọn mục H2)
  chi_o_dau_doan        luật 2: chữ query chỉ xuất hiện ở đầu đoạn trong mục nguồn
  du_3_lan              anchor đã dùng từ --max-anchor lần trên site (cần --site-anchors, cùng dạng với the_link.py)
Script không chọn anchor. Claude chọn theo anchor-rules.md §6 (intent đích) và luật 5 (dùng từ đồng nghĩa).

Mã thoát: 0 xong · 1 lỗi đầu vào (file thiếu, không có query cho trang đích, mục nguồn không thấy) · 2 sai tham số.
Ví dụ:
  anchor_gsc.py gsc_page_query.json --page /dich-vu-seo/ --target-file dich.html --source-file the.md --section "câu hỏi"
  anchor_gsc.py queries.csv --page https://example.vn/bang-gia/ --site-anchors anchors.json --out anchor.tsv
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from the_link import SC_DEFAULT, dest_of, mask, norm, sections  # noqa: E402

COLS = {
    "query": ("top queries", "queries", "query", "truy van hang dau", "truy van", "keyword", "tu khoa"),
    "page": ("top pages", "landing page", "page", "url", "address", "cac trang hang dau", "trang dich", "trang"),
    "clicks": ("clicks", "so luot nhap", "luot nhap", "nhap"),
    "impressions": ("impressions", "so lan hien thi", "luot hien thi", "hien thi"),
    "position": ("average position", "position", "vi tri trung binh", "vi tri"),
}
CHECKS = ("trang_khac", "khong_co_trong_dich", "mo_bai_dich", "khong_co_trong_nguon", "chi_o_dau_doan", "du_3_lan")
# mo_bai_dich chỉ cảnh báo: seed query của trang thường có sẵn trong đoạn đầu, nên luật 1 có thể va với
# luật "anchor = seed query". Claude quyết và ghi lý do trong plan.
BLOCKING = tuple(c for c in CHECKS if c != "mo_bai_dich")
BLOCK_TAGS = re.compile(r"</?(?:p|h[1-6]|li|ul|ol|div|section|article|br|td|tr|table|blockquote|figcaption|dd|dt)\b[^>]*>",
                        re.I)


class Err(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


def fold(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lstrip("﻿")).replace("đ", "d").replace("Đ", "D")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn")).casefold()


def to_int(v):
    s = re.sub(r"[.,\s ]", "", str(v or "0"))
    return int(s) if s.isdigit() else 0


def to_float(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def host_of(u):
    h = urlparse(u or "").netloc.lower()
    return h[4:] if h.startswith("www.") else h


# ---------- đọc GSC ----------
def read_gsc(path, dims):
    if not os.path.isfile(path):
        raise Err("không thấy file: %s" % path)
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    if raw.lstrip().startswith(("{", "[")):
        try:
            data = json.loads(raw)
        except ValueError:
            raise Err("%s không phải JSON hợp lệ" % path)
        items = data.get("rows", []) if isinstance(data, dict) else data
        order = [d.strip() for d in dims.split(",")]
        out = []
        for r in items:
            keys = r.get("keys") or []
            kv = dict(zip(order, keys))
            if len(keys) == 1 and "query" not in kv:
                kv = {"query": keys[0]}
            if not kv.get("query"):
                continue
            out.append({"page": kv.get("page"), "query": kv["query"], "clicks": to_int(r.get("clicks")),
                        "impressions": to_int(r.get("impressions")), "position": to_float(r.get("position"))})
        return out
    try:
        dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rd = csv.reader(io.StringIO(raw), dialect)
    head = next(rd, None)
    if not head:
        raise Err("%s rỗng" % path)
    idx = {}
    for i, h in enumerate(head):
        fh = fold(h)
        for col, names in COLS.items():
            if col not in idx and any(fh == n or fh.startswith(n) for n in names):
                idx[col] = i
                break
    if "query" not in idx:
        raise Err("%s không có cột query (đọc được: %s)" % (path, ", ".join(head)))
    out = []
    for row in rd:
        if not row or len(row) <= idx["query"] or not row[idx["query"]].strip():
            continue

        def g(c):
            return row[idx[c]] if c in idx and idx[c] < len(row) else None
        out.append({"page": g("page"), "query": row[idx["query"]].strip(), "clicks": to_int(g("clicks")),
                    "impressions": to_int(g("impressions")), "position": to_float(g("position"))})
    return out


# ---------- đọc văn bản ----------
def read_text(path):
    if not os.path.isfile(path):
        raise Err("không thấy file: %s" % path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def is_html(t):
    return bool(re.search(r"<(?:p|h[1-6]|div|article|body)\b", t, re.I))


def paragraphs(text):
    """Khối văn bản không phải heading, theo thứ tự. HTML tách theo thẻ khối; markdown tách theo dòng trống."""
    t = mask(text)
    out = []
    if is_html(t):
        m = re.search(r"<(article|main)\b[^>]*>(.*?)</\1\s*>", t, re.I | re.S)
        body = m.group(2) if m else t
        body = re.sub(r"<(nav|header|footer|aside|form)\b.*?</\1\s*>", " ", body, flags=re.I | re.S)
        body = re.sub(r"<h([1-6])\b.*?</h\1\s*>", "\n\n", body, flags=re.I | re.S)
        for blk in BLOCK_TAGS.sub("\n\n", body).split("\n\n"):
            n = norm(blk)
            if n:
                out.append(n)
        return out
    t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
    for blk in re.split(r"\n[ \t]*\n", t):
        b = blk.strip()
        if not b or b.startswith(("#", "![", "|", "<!--")) or re.match(r"^<h[1-6]\b", b, re.I):
            continue
        b = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", b)
        b = re.sub(r"\[((?:[^\[\]]|\[[^\[\]]*\])+)\]\([^)]*\)", r"\1", b)
        b = re.sub(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+", "", b, flags=re.M)
        n = norm(b.replace("*", " ").replace("_", " "))
        if n:
            out.append(n)
    return out


def section_text(text, pattern, sc_last):
    if not pattern:
        return text
    rx = re.compile(pattern, re.I)
    secs, has_h2 = sections(text, re.compile(SC_DEFAULT, re.I), sc_last)
    hit = [s for s in secs if s["title"] and rx.search(s["title"])]
    if not has_h2 or not hit:
        raise Err("không thấy mục H2 khớp --section %r trong file nguồn" % pattern)
    return "\n\n".join(text[s["head_end"]:s["end"]] for s in hit)


def phrase_re(q):
    return re.compile(r"(?<!\w)" + re.escape(norm(q)) + r"(?!\w)")


# ---------- chính ----------
def analyze(rows, page, hosts=(), target_text=None, source_text=None, site_anchors=None, max_anchor=3,
            exclude=None, min_impressions=0):
    hs = set(h[4:] if h.startswith("www.") else h for h in (x.lower() for x in hosts))
    hs.update(host_of(r["page"]) for r in rows if r.get("page"))
    hs.add(host_of(page))
    hs.discard("")
    single = not any(r.get("page") for r in rows)
    tkey = dest_of(page, hs)[0]
    if tkey is None:
        raise Err("--page không phải URL trang: %r" % page, 2)
    by_q = {}
    for r in rows:
        k = norm(r["query"])
        pk = tkey if single else dest_of(r["page"], hs)[0]
        cur = by_q.setdefault(k, {}).get(pk)
        if cur is None or (r["clicks"], r["impressions"]) > (cur["clicks"], cur["impressions"]):
            by_q[k][pk] = dict(r, page=pk)
    tparas = paragraphs(target_text) if target_text is not None else None
    tall = "\n".join(tparas) if tparas is not None else None
    sparas = paragraphs(source_text) if source_text is not None else None
    anchors = {norm(a): n for a, n in (site_anchors or {}).items()}
    ex = re.compile(exclude, re.I) if exclude else None
    out = []
    for q, pages in by_q.items():
        me = pages.get(tkey)
        if me is None or me["impressions"] < min_impressions or (ex and ex.search(q)):
            continue
        flags, checks = [], {}
        rival = max((v for k, v in pages.items() if k != tkey), key=lambda v: (v["clicks"], v["impressions"]), default=None)
        if rival and (rival["clicks"], rival["impressions"]) > (me["clicks"], me["impressions"]):
            flags.append("trang_khac")
        rx = phrase_re(q)
        if tparas is not None:
            checks["co_trong_dich"] = bool(rx.search(tall))
            checks["mo_bai_dich"] = bool(tparas and rx.search(tparas[0]))
            if not checks["co_trong_dich"]:
                flags.append("khong_co_trong_dich")
            if checks["mo_bai_dich"]:
                flags.append("mo_bai_dich")
        if sparas is not None:
            pos = [m.start() for p in sparas for m in rx.finditer(p)]
            starts = [m.start() == 0 for p in sparas for m in rx.finditer(p)]
            checks["co_trong_nguon"] = bool(pos)
            if not pos:
                flags.append("khong_co_trong_nguon")
            elif all(starts):
                flags.append("chi_o_dau_doan")
        used = anchors.get(q, 0) if site_anchors is not None else None
        if used is not None and used >= max_anchor:
            flags.append("du_3_lan")
        out.append({"query": me["query"], "clicks": me["clicks"], "impressions": me["impressions"],
                    "position": me["position"], "so_tu": len(q.split()), "da_dung": used,
                    "trang_khac": rival["page"] if "trang_khac" in flags else "", "checks": checks, "flags": flags,
                    "dat": not any(f in BLOCKING for f in flags)})
    out.sort(key=lambda x: (not x["dat"], -x["clicks"], -x["impressions"], x["position"] if x["position"] is not None else 1e9))
    run = ["trang_khac"] if not single else []
    run += ["khong_co_trong_dich", "mo_bai_dich"] if tparas is not None else []
    run += ["khong_co_trong_nguon", "chi_o_dau_doan"] if sparas is not None else []
    run += ["du_3_lan"] if site_anchors is not None else []
    return {"page": page, "page_key": tkey, "mot_trang": single, "so_query": len(out), "da_kiem": run,
            "chua_kiem": [f for f in CHECKS if f not in run], "rows": out}


def fmt_cell(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "có" if v else "không"
    if isinstance(v, float):
        return ("%.1f" % v).replace(".", ",")
    if isinstance(v, list):
        return ", ".join(v) or "-"
    return re.sub(r"[\t\r\n|]+", " ", str(v))


COLS_OUT = ["query", "dat", "clicks", "impressions", "position", "so_tu", "da_dung", "flags", "trang_khac"]


def render_md(rep, top):
    lines = ["Trang đích: %s · %d query · đã kiểm: %s · chưa kiểm: %s" % (
        rep["page"], rep["so_query"], ", ".join(rep["da_kiem"]) or "-", ", ".join(rep["chua_kiem"]) or "-")]
    if rep["mot_trang"]:
        lines.append("File GSC không có cột trang: mọi query tính cho trang đích, không kiểm được trang_khac.")
    lines.append("| " + " | ".join(COLS_OUT) + " |")
    lines.append("|" + "---|" * len(COLS_OUT))
    rows = rep["rows"][:top] if top else rep["rows"]
    for r in rows:
        lines.append("| " + " | ".join(fmt_cell(r[c]) for c in COLS_OUT) + " |")
    return "\n".join(lines) + "\n"


def render_tsv(rep):
    lines = ["\t".join(COLS_OUT)]
    for r in rep["rows"]:
        lines.append("\t".join(fmt_cell(r[c]) for c in COLS_OUT))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gsc", help="file GSC: JSON của gsc.sh query, hoặc CSV/TSV")
    ap.add_argument("--page", required=True, help="trang đích: path hoặc URL đầy đủ")
    ap.add_argument("--dims", default="page,query", help="thứ tự dimension trong JSON (mặc định page,query)")
    ap.add_argument("--host", action="append", default=[], help="host của site (lặp được); host trong file GSC tự thêm")
    ap.add_argument("--target-file", help="nội dung trang đích (.md hoặc .html) để kiểm luật 1 và luật 6")
    ap.add_argument("--source-file", help="bài nguồn (.md hoặc .html) để kiểm luật 2 và luật 6")
    ap.add_argument("--section", help="regex tên H2 của mục nguồn sẽ đặt link (vd 'câu hỏi')")
    ap.add_argument("--sc-last", type=int, default=2)
    ap.add_argument("--site-anchors", help="JSON {anchor: số lần} đã dùng trên site (cùng dạng the_link.py)")
    ap.add_argument("--max-anchor", type=int, default=3, help="số lần tối đa của một anchor (mặc định 3)")
    ap.add_argument("--exclude", help="regex bỏ query (vd tên thương hiệu)")
    ap.add_argument("--min-impressions", type=int, default=0)
    ap.add_argument("--top", type=int, default=20, help="số dòng in ra màn hình (0 = tất cả)")
    ap.add_argument("--json", action="store_true", help="in JSON thay cho bảng")
    ap.add_argument("--out", help="ghi .tsv hoặc .json (không ghi đè nếu thiếu --force)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        rows = read_gsc(a.gsc, a.dims)
        if not rows:
            raise Err("file GSC không có dòng query nào")
        tt = read_text(a.target_file) if a.target_file else None
        st = section_text(read_text(a.source_file), a.section, a.sc_last) if a.source_file else None
        if a.section and not a.source_file:
            raise Err("--section cần --source-file", 2)
        sa = None
        if a.site_anchors:
            try:
                sa = json.loads(read_text(a.site_anchors))
            except ValueError:
                raise Err("--site-anchors không phải JSON")
        rep = analyze(rows, a.page, a.host, tt, st, sa, a.max_anchor, a.exclude, a.min_impressions)
        if not rep["rows"]:
            raise Err("không có query nào cho trang đích %s sau khi lọc" % rep["page_key"])
        if a.out:
            if os.path.exists(a.out) and not a.force:
                raise Err("file đã có, không ghi đè: %s (thêm --force)" % a.out)
            with open(a.out, "w", encoding="utf-8") as f:
                f.write(json.dumps(rep, ensure_ascii=False, indent=1) if a.out.endswith(".json") else render_tsv(rep))
        sys.stdout.write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n" if a.json else render_md(rep, a.top))
        return 0
    except Err as e:
        print("LỖI: %s" % e, file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
