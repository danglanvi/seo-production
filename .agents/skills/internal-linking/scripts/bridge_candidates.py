#!/usr/bin/env python3
"""bridge_candidates.py - lọc đoạn ứng viên cho contextual bridge rồi xuất input Jev link-bridge (offline, stdlib).

Wrapper mỏng quanh skill site-vector-index (svi.py) và rubric Jev link-bridge. Script không nạp model, không gọi mạng.
EmbeddingGemma chạy một lần trong `svi.py query` (một tiến trình, store đã cache vector).

Lệnh:
  queries  trang đích -> q.jsonl cho `svi.py query --level passage --per-url`
  build    hits của svi + rows.jsonl (+ pages.jsonl) -> jev_in.jsonl, candidates.jsonl, candidates.tsv, summary.json
  merge    candidates.jsonl + kết quả jev.py -> bảng ứng viên xếp theo xác suất natural_bridge để Claude chọn

Trang đích (--targets): file .jsonl, mỗi dòng {"url", "title"?, "summary"?, "headings"?: [...], "keywords"?: [...]},
hoặc file văn bản mỗi dòng một URL. Trường thiếu lấy từ pages.jsonl của svi extract (H1 hoặc title, meta description, H2).
"keywords" là cụm từ khoá mạnh: đoạn chứa cụm đó vào danh sách dù không nằm trong top-K của embedding.

Lọc ở build (references/link-placement.md §1, anchor-rules.md §2):
  cung_trang     đoạn nằm trên chính trang đích
  mo_bai         đoạn trước H2 đầu (luật 7: không đặt link ở mở bài)
  h2_cam         H2 khớp --skip-h2
  lap_template   cùng chữ đoạn có trên từ --boilerplate-min trang (khối lặp theo template)
  trang_da_link  trang nguồn đã có link main content tới đích (luật 5: 1 link/đích/trang); --keep-linked giữ kèm cờ
  mc             đoạn ở main content khi chạy --sc-only (link cần chuyển xuống SC)
  duoi_cos       cosine dưới --min-cos (không có mặc định: hiệu chuẩn theo site)
Header, footer, nav, sidebar, TOC đã bị svi extract bỏ trước khi cắt passage.
jev_in.jsonl dùng khoá state của lượt hiệu chuẩn link-bridge: source {title, heading, paragraph}, target {url, title,
summary, headings}. Thiếu pages.jsonl thì cột vung có thể là "?" (không biết H2 nào là H2 cuối).

Mã thoát: 0 xong · 1 lỗi đầu vào (file thiếu, JSON hỏng, file output đã có) · 2 sai tham số.
Ví dụ:
  bridge_candidates.py queries --targets dich.txt --pages pages.jsonl --out q.jsonl
  <venv>/bin/python -I svi.py query --store store/ --in q.jsonl --level passage --per-url --k 40 --out hits.jsonl
  bridge_candidates.py build --targets dich.txt --hits hits.jsonl --rows rows.jsonl --pages pages.jsonl --out cau-noi/
  jev.py --task tasks/link-bridge.json --in cau-noi/jev_in.jsonl --out cau-noi/jev_out.jsonl --budget 0.1
  bridge_candidates.py merge --candidates cau-noi/candidates.jsonl --jev cau-noi/jev_out.jsonl --out cau-noi/bang.tsv
"""
import argparse
import collections
import json
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from the_link import SC_DEFAULT, dest_of, norm  # noqa: E402

NB = "natural_bridge"
NB_MIN = 0.85  # references/link-placement.md §5 bước 4


class Err(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


def read_jsonl(path):
    if not os.path.isfile(path):
        raise Err("không thấy file: %s" % path)
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                raise Err("%s dòng %d không phải JSON" % (path, i))
    return out


def host_of(u):
    h = urlparse(u or "").netloc.lower()
    return h[4:] if h.startswith("www.") else h


def collect_hosts(given, urls):
    hs = set(h.lower()[4:] if h.lower().startswith("www.") else h.lower() for h in given)
    hs.update(h for h in (host_of(u) for u in urls) if h)
    return hs


def ukey(u, hosts):
    d, _ = dest_of(u, hosts)
    return d


def load_targets(path, pages, hosts):
    if not os.path.isfile(path):
        raise Err("không thấy file: %s" % path)
    if path.endswith(".jsonl"):
        items = read_jsonl(path)
    else:
        with open(path, encoding="utf-8") as f:
            items = [{"url": l.strip()} for l in f if l.strip() and not l.lstrip().startswith("#")]
    by_key = {ukey(u, hosts): p for u, p in pages.items()}
    out = []
    for t in items:
        if not t.get("url"):
            raise Err("trang đích thiếu url: %r" % t)
        p = by_key.get(ukey(t["url"], hosts), {})
        t = dict(t)
        if not t.get("title"):
            t["title"] = p.get("h1") or p.get("title") or ""
        if not t.get("summary"):
            t["summary"] = p.get("meta") or ""
        if not t.get("headings"):
            t["headings"] = p.get("h2") or []
        t.setdefault("keywords", [])
        out.append(t)
    if not out:
        raise Err("không có trang đích")
    return out


def target_text(t):
    parts = [t.get("title", ""), t.get("summary", ""), "; ".join(t.get("headings", [])[:12])]
    return ". ".join(p.strip().rstrip(".") for p in parts if p and p.strip().rstrip("."))


def strip_path(text, meta):
    path = " > ".join(x for x in (meta.get("heading"), meta.get("h3")) if x)
    if path and text.startswith(path + ": "):
        return text[len(path) + 2:]
    return text


def zone_of(meta, page, sc_re, sc_last):
    h = meta.get("heading") or ""
    if not h:
        return "MC"
    if sc_re.search(norm(h)):
        return "SC"
    h2s = [norm(x) for x in (page or {}).get("h2") or []]
    if norm(h) in h2s:
        return "SC" if h2s.index(norm(h)) >= len(h2s) - sc_last else "MC"
    return "?"


def phrase_re(p):
    return re.compile(r"(?<!\w)" + re.escape(norm(p)) + r"(?!\w)")


def write_new(path, text, force):
    if os.path.exists(path) and not force:
        raise Err("file đã có, không ghi đè: %s (thêm --force)" % path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def tsv_cell(v):
    if isinstance(v, list):
        v = ",".join(str(x) for x in v)
    return re.sub(r"[\t\r\n]+", " ", "" if v is None else str(v))


# ---------- queries ----------
def cmd_queries(a):
    pages = {p["url"]: p for p in read_jsonl(a.pages)} if a.pages else {}
    hosts = collect_hosts(a.host, list(pages))
    targets = load_targets(a.targets, pages, hosts)
    lines = []
    for t in targets:
        txt = target_text(t)
        if not txt:
            raise Err("trang đích %s không có title, summary hay H2 để làm truy vấn (thêm --pages hoặc trường title)" % t["url"])
        lines.append(json.dumps({"id": t["url"], "text": txt, "filter": {"level": "passage"}}, ensure_ascii=False))
    out = "\n".join(lines) + "\n"
    if a.out in (None, "-"):
        sys.stdout.write(out)
    else:
        write_new(a.out, out, a.force)
        print("queries: %d trang đích -> %s" % (len(lines), a.out), file=sys.stderr)
    return 0


# ---------- build ----------
def cmd_build(a):
    rows = read_jsonl(a.rows)
    hits = read_jsonl(a.hits)
    pages = {p["url"]: p for p in read_jsonl(a.pages)} if a.pages else {}
    hosts = collect_hosts(a.host, [r.get("url", "") for r in rows] + list(pages))
    targets = load_targets(a.targets, pages, hosts)
    tmap = {ukey(t["url"], hosts): t for t in targets}
    sc_re = re.compile(a.sc_h2, re.I)
    skip_re = re.compile(a.skip_h2, re.I) if a.skip_h2 else None

    passages, titles, linked, has_h2 = {}, {}, collections.defaultdict(set), set()
    pages_by_text = collections.defaultdict(set)
    for r in rows:
        lv, url, meta = r.get("level"), r.get("url", ""), r.get("meta") or {}
        if lv == "passage":
            passages[r["id"]] = r
            pages_by_text[norm(strip_path(r.get("text", ""), meta))].add(url)
            if meta.get("heading"):
                has_h2.add(url)
        elif lv == "page" and meta.get("title"):
            titles[url] = meta["title"]
        elif lv == "anchor" and meta.get("target") and meta.get("zone", "main") == "main":
            linked[ukey(url, hosts)].add(ukey(meta["target"], hosts))
    page_by_key = {ukey(u, hosts): p for u, p in pages.items()}

    cands = collections.OrderedDict()
    missing = 0
    for h in hits:
        tk = ukey(h.get("id", ""), hosts)
        if tk not in tmap:
            continue
        for it in h.get("top") or []:
            if it.get("level", "passage") != "passage":
                continue
            if it["id"] not in passages:
                missing += 1
                continue
            c = cands.setdefault((tk, it["id"]), {"cos": None, "nguon": set(), "kw": []})
            c["cos"] = it.get("cos")
            c["nguon"].add("emb")
    for tk, t in tmap.items():
        kws = [(k, phrase_re(k)) for k in t.get("keywords") or [] if norm(k)]
        if not kws:
            continue
        for pid, r in passages.items():
            txt = norm(strip_path(r.get("text", ""), r.get("meta") or {}))
            got = [k for k, rx in kws if rx.search(txt)]
            if got:
                c = cands.setdefault((tk, pid), {"cos": None, "nguon": set(), "kw": []})
                c["nguon"].add("kw")
                c["kw"] = got

    kept, dropped = [], collections.Counter()
    for (tk, pid), c in cands.items():
        r = passages[pid]
        meta = r.get("meta") or {}
        sk = ukey(r["url"], hosts)
        page = page_by_key.get(sk) or pages.get(r["url"])
        heading = meta.get("heading") or ""
        flags = []
        reason = None
        if sk == tk:
            reason = "cung_trang"
        elif not heading:
            if r["url"] in has_h2 or (page or {}).get("h2"):
                reason = "mo_bai"
            elif pid.endswith("#s0p0"):  # trang không có H2: chỉ đoạn đầu là mở bài
                reason = "mo_bai"
            else:
                flags.append("khong_h2")
        if reason is None and skip_re and skip_re.search(norm(heading)):
            reason = "h2_cam"
        text = strip_path(r.get("text", ""), meta)
        if reason is None and len(pages_by_text[norm(text)]) >= a.boilerplate_min:
            reason = "lap_template"
        if reason is None and tk in linked.get(sk, ()):
            if a.keep_linked:
                flags.append("trang_da_link")
            else:
                reason = "trang_da_link"
        vung = zone_of(meta, page, sc_re, a.sc_last) if heading else "MC"
        if reason is None and a.sc_only and vung != "SC":
            reason = "mc"
        if reason is None and a.min_cos is not None and c["cos"] is not None and c["cos"] < a.min_cos:
            reason = "duoi_cos"
        if page is not None and "noindex" in (page.get("robots") or "").lower():
            flags.append("nguon_noindex")
        if reason:
            dropped[reason] += 1
            continue
        t = tmap[tk]
        kept.append({"id": "%s|%s" % (t["url"], pid), "target": t["url"], "source_url": r["url"], "passage_id": pid,
                     "source_title": (page or {}).get("title") or titles.get(r["url"], ""), "h2": heading,
                     "h3": meta.get("h3") or "", "vung": vung, "cos": c["cos"], "nguon": "+".join(sorted(c["nguon"])),
                     "kw": c["kw"], "flags": flags, "text": text})

    kept.sort(key=lambda x: (x["target"], x["cos"] is None, -(x["cos"] or 0)))
    if a.limit:
        per, lim = collections.Counter(), []
        for x in kept:
            per[x["target"]] += 1
            if per[x["target"]] <= a.limit:
                lim.append(x)
            else:
                dropped["vuot_limit"] += 1
        kept = lim

    os.makedirs(a.out, exist_ok=True)
    jev = []
    for x in kept:
        t = tmap[ukey(x["target"], hosts)]
        jev.append({"id": x["id"], "state": {
            "source": {"title": x["source_title"], "heading": " > ".join(v for v in (x["h2"], x["h3"]) if v),
                       "paragraph": x["text"][:3000]},
            "target": {"url": t["url"], "title": t.get("title", ""), "summary": t.get("summary", ""),
                       "headings": list(t.get("headings") or [])[:15]}}})
    cols = ["id", "target", "source_url", "passage_id", "h2", "h3", "vung", "cos", "nguon", "kw", "flags", "text"]
    tsv = ["\t".join(cols)] + ["\t".join(tsv_cell(x[k] if k != "text" else x[k][:300]) for k in cols) for x in kept]
    summary = {"targets": len(tmap), "hits": len(hits), "candidates": len(cands), "kept": len(kept),
               "dropped": dict(dropped), "missing_rows": missing,
               "per_target": dict(collections.Counter(x["target"] for x in kept))}
    write_new(os.path.join(a.out, "jev_in.jsonl"), "".join(json.dumps(j, ensure_ascii=False) + "\n" for j in jev), a.force)
    write_new(os.path.join(a.out, "candidates.jsonl"),
              "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in kept), a.force)
    write_new(os.path.join(a.out, "candidates.tsv"), "\n".join(tsv) + "\n", a.force)
    write_new(os.path.join(a.out, "summary.json"), json.dumps(summary, ensure_ascii=False, indent=1) + "\n", a.force)
    print("build: %d ứng viên, giữ %d, bỏ %s, thiếu rows %d -> %s" % (
        len(cands), len(kept), dict(dropped) or "{}", missing, a.out), file=sys.stderr)
    if missing:
        print("Cảnh báo: %d hit không có trong rows.jsonl. Kiểm rows và store cùng một lần extract." % missing, file=sys.stderr)
    return 0


# ---------- merge ----------
def cmd_merge(a):
    cands = read_jsonl(a.candidates)
    res = {r["id"]: r for r in read_jsonl(a.jev)}
    out = []
    for x in cands:
        r = res.get(x["id"])
        fit = ((r or {}).get("answers") or {}).get("fit") or {}
        probs = fit.get("probabilities") or {}
        nb = probs.get(NB)
        if nb is None and fit.get("choice") == NB:
            nb = fit.get("confidence")
        flags = list(x.get("flags") or [])
        if r is None:
            flags.append("chua_cham")
        elif "error" in r:
            flags.append("loi_jev:%s" % r["error"])
        dat = nb is not None and nb >= a.nb_min
        out.append(dict(x, nb=None if nb is None else round(nb, 3), choice=fit.get("choice", ""), dat=dat, flags=flags))
    out.sort(key=lambda x: (x["target"], not x["dat"], -(x["nb"] or 0), -(x["cos"] or 0)))
    cols = ["target", "dat", "nb", "choice", "vung", "cos", "source_url", "h2", "text", "flags", "id"]
    lines = ["\t".join(cols)] + ["\t".join(tsv_cell(x[k] if k != "text" else x[k][:300]) for k in cols) for x in out]
    txt = "\n".join(lines) + "\n"
    if a.out in (None, "-"):
        sys.stdout.write(txt)
    else:
        write_new(a.out, txt, a.force)
    n_dat = sum(1 for x in out if x["dat"])
    print("merge: %d dòng, đạt natural_bridge >= %.2f: %d, chưa chấm hoặc lỗi: %d" % (
        len(out), a.nb_min, n_dat, sum(1 for x in out if any(f.startswith(("chua_cham", "loi_jev")) for f in x["flags"]))),
        file=sys.stderr)
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queries", help="tạo q.jsonl cho svi.py query")
    q.add_argument("--targets", required=True, help="trang đích: .jsonl hoặc file mỗi dòng một URL")
    q.add_argument("--pages", help="pages.jsonl của svi extract, để lấy H1, meta, H2 của trang đích")
    q.add_argument("--host", action="append", default=[], help="host của site (lặp được)")
    q.add_argument("--out", help="file q.jsonl; bỏ trống hoặc '-' thì in ra stdout")
    q.add_argument("--force", action="store_true", help="cho ghi đè file output")
    b = sub.add_parser("build", help="lọc ứng viên, xuất jev_in.jsonl")
    b.add_argument("--targets", required=True)
    b.add_argument("--hits", required=True, help="output của svi.py query (id = URL trang đích)")
    b.add_argument("--rows", required=True, help="rows.jsonl của svi extract (passage + anchor)")
    b.add_argument("--pages", help="pages.jsonl của svi extract (H2, robots, title)")
    b.add_argument("--host", action="append", default=[])
    b.add_argument("--out", required=True, help="thư mục output")
    b.add_argument("--sc-last", type=int, default=2, help="số H2 cuối tính là SC (mặc định 2, như the_link.py)")
    b.add_argument("--sc-h2", default=SC_DEFAULT, help="regex tên H2 thuộc SC")
    b.add_argument("--sc-only", action="store_true", help="chỉ giữ đoạn ở SC (link cần chuyển xuống SC)")
    b.add_argument("--skip-h2", help="regex tên H2 không đặt link (vd mục lục|tác giả)")
    b.add_argument("--boilerplate-min", type=int, default=3, help="số trang có cùng chữ đoạn để coi là khối template (mặc định 3)")
    b.add_argument("--keep-linked", action="store_true", help="giữ đoạn trên trang đã link tới đích, gắn cờ trang_da_link")
    b.add_argument("--min-cos", type=float, help="bỏ ứng viên embedding có cosine dưới ngưỡng này (hiệu chuẩn theo site)")
    b.add_argument("--limit", type=int, help="giữ tối đa N ứng viên mỗi trang đích")
    b.add_argument("--force", action="store_true")
    m = sub.add_parser("merge", help="ghép kết quả Jev link-bridge")
    m.add_argument("--candidates", required=True)
    m.add_argument("--jev", required=True, help="output của jev.py --task link-bridge")
    m.add_argument("--nb-min", type=float, default=NB_MIN, help="ngưỡng natural_bridge (mặc định 0,85 theo link-placement.md §5)")
    m.add_argument("--out", help="file TSV; bỏ trống hoặc '-' thì in ra stdout")
    m.add_argument("--force", action="store_true")
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return {"queries": cmd_queries, "build": cmd_build, "merge": cmd_merge}[a.cmd](a)
    except Err as e:
        print("LỖI: %s" % e, file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
