#!/usr/bin/env python3
"""Kiểm cặp trang 2 ngôn ngữ có tương đương không, bằng vector EmbeddingGemma 2 đã có trong store (chạy local).

Chạy bằng Python có numpy (venv EmbeddingGemma):
  pairs  --store DIR [--page-store DIR] --b-prefix /en/ [--declared declared.jsonl] [--k 5] --out pairs.jsonl
         Store của site-vector-index: vec.npy + items.jsonl, có mục level "page" và "section".
         Trang có path bắt đầu bằng --b-prefix là ngôn ngữ B, còn lại là ngôn ngữ A.
         Ứng viên của mỗi trang B: top k trang A theo cosine cấp trang, cộng cặp đã khai hreflang.
         declared.jsonl: mỗi dòng {"a_url", "b_url"}.
  declared --html-dir DIR --out declared.jsonl [--a-lang vi --b-lang en]
         Đọc thẻ <link rel="alternate" hreflang> trong file HTML đã tải (cặp file .html + .url).
  report --pairs pairs.jsonl --out-dir DIR [--registry model-calibration.json --site <domain>] [--metric sec_cov]
Điểm của cặp:
  page_cos  cosine cấp trang; sec_cov  min của 2 chiều (mỗi section của trang này gặp section gần nhất của trang kia, lấy trung bình).
Ngưỡng nhận và ngưỡng loại đọc từ entry cosine rubric "hreflang-pair", version = tên metric. Không có ngưỡng thì Claude đọc mọi cặp.
Ngưỡng loại còn là nháp (chưa holdout): cặp dưới ngưỡng không bị loại, chỉ xếp cuối danh sách Claude đọc.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

RUBRIC = "hreflang-pair"


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_store(d):
    import numpy as np
    d = Path(d)
    items = jl(d / "items.jsonl")
    vec = np.load(d / "vec.npy").astype("float32")
    if len(items) != len(vec):
        sys.exit(f"store lỗi: {len(items)} mục, {len(vec)} vector")
    return items, vec


def is_b(url, prefix):
    return urlparse(url).path.startswith(prefix)


def coverage(x, y):
    """Trung bình cosine lớn nhất của mỗi section x với các section y."""
    if not len(x) or not len(y):
        return None
    return float((x @ y.T).max(axis=1).mean())


def cmd_pairs(a):
    import numpy as np
    items, vec = load_store(a.store)
    p_items, p_vec = load_store(a.page_store) if a.page_store else (items, vec)
    page = {it["url"]: p_vec[i] for i, it in enumerate(p_items) if it["level"] == "page"}
    secs = {}
    for i, it in enumerate(items):
        if it["level"] == "section":
            secs.setdefault(it["url"], []).append(i)
    secv = {u: vec[ix] for u, ix in secs.items()}
    a_urls = [u for u in page if not is_b(u, a.b_prefix)]
    b_urls = [u for u in page if is_b(u, a.b_prefix)]
    if not a_urls or not b_urls:
        sys.exit(f"thiếu trang: {len(a_urls)} trang A, {len(b_urls)} trang B (--b-prefix {a.b_prefix})")
    declared = {}
    for d in (jl(a.declared) if a.declared else []):
        declared.setdefault(d["b_url"], set()).add(d["a_url"])
    A = np.stack([page[u] for u in a_urls])
    rows = []
    for b in b_urls:
        cos = A @ page[b]
        order = np.argsort(-cos)
        top = [a_urls[j] for j in order[:a.k]]
        margin = float(cos[order[0]] - cos[order[1]]) if len(order) > 1 else None
        rank = {a_urls[j]: r + 1 for r, j in enumerate(order)}
        for u in dict.fromkeys(top + sorted(declared.get(b, ()))):
            if u not in page:
                rows.append({"id": f"{b}|{u}", "b_url": b, "a_url": u, "declared": True, "error": "không có trong store"})
                continue
            j = a_urls.index(u)
            c1 = coverage(secv.get(b, []), secv.get(u, []))
            c2 = coverage(secv.get(u, []), secv.get(b, []))
            rows.append({"id": f"{b}|{u}", "b_url": b, "a_url": u, "declared": u in declared.get(b, ()),
                         "rank": rank[u], "page_cos": round(float(cos[j]), 4), "top_margin": round(margin, 4),
                         "sec_b2a": None if c1 is None else round(c1, 4), "sec_a2b": None if c2 is None else round(c2, 4),
                         "sec_cov": None if c1 is None or c2 is None else round(min(c1, c2), 4)})
    write(a.out, rows)
    print(f"{len(b_urls)} trang B, {len(rows)} cặp ứng viên -> {a.out}", file=sys.stderr)
    return 0


LINK = re.compile(r"<link\b[^>]*>", re.I)


def attr(tag, name):
    m = re.search(rf'{name}\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return m.group(1) if m else None


def cmd_declared(a):
    rows = []
    for f in sorted(Path(a.html_dir).glob("*.html")):
        alt = {}
        for tag in LINK.findall(f.read_text(encoding="utf-8", errors="replace")):
            if (attr(tag, "rel") or "").lower() == "alternate" and attr(tag, "hreflang"):
                alt[attr(tag, "hreflang").lower()] = attr(tag, "href")
        a_url = next((v for k, v in alt.items() if k.split("-")[0] == a.a_lang), None)
        b_url = next((v for k, v in alt.items() if k.split("-")[0] == a.b_lang), None)
        if a_url and b_url:
            rows.append({"a_url": a_url, "b_url": b_url, "source": f.name})
    uniq = list({(r["a_url"], r["b_url"]): r for r in rows}.values())
    write(a.out, uniq)
    print(f"{len(uniq)} cặp đã khai -> {a.out}", file=sys.stderr)
    return 0


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def load_gate(registry, site, metric):
    for path, want_site, src in ((registry, site, "site"), (find_defaults(), None, "defaults")):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == RUBRIC and e.get("version") == metric and e.get("mode") == "cosine" \
                    and (not want_site or e.get("site") == want_site):
                return {"accept": e.get("threshold"), "reject": e.get("reject_below")}, src
    return {}, None


LOW = "Claude đọc cuối"


def decide(score, gate):
    if score is None:
        return "Claude đọc", "thiếu section"
    if gate.get("accept") is not None and score >= gate["accept"]:
        return "tương đương", f"{score:.3f} ≥ {gate['accept']}"
    if gate.get("reject") is not None and score < gate["reject"]:
        return LOW, f"{score:.3f} < {gate['reject']}: nháp, chưa holdout"
    return "Claude đọc", f"{score:.3f} trong vùng xám" if gate else "chưa có ngưỡng"


def cmd_report(a):
    rows = jl(a.pairs)
    gate, src = load_gate(a.registry, a.site, a.metric)
    for r in rows:
        r["decision"], r["why"] = decide(r.get(a.metric), gate) if "error" not in r else ("Claude đọc", r["error"])
    by_b = {}
    for r in rows:
        by_b.setdefault(r["b_url"], []).append(r)
    pages = []
    for b, rs in sorted(by_b.items()):
        dec = [r for r in rs if r["declared"]]
        keep = sorted((r for r in rs if "rank" in r), key=lambda r: (r["decision"] == LOW, r["rank"]))
        best = keep[0] if keep else None
        if dec and any(r["decision"] == LOW for r in dec):
            flag = "cặp đã khai dưới ngưỡng nháp: Claude đọc"
        elif dec and all(r["decision"] == "tương đương" for r in dec):
            flag = "cặp đã khai tương đương"
        elif not keep:
            flag = "không có ứng viên: Claude đọc"
        elif best["decision"] == LOW:
            flag = "mọi ứng viên dưới ngưỡng nháp: Claude đọc"
        elif dec:
            flag = "cặp đã khai: Claude đọc"
        else:
            flag = "chưa khai hreflang: Claude đọc ứng viên"
        pages.append({"b_url": b, "declared": [r["a_url"] for r in dec], "best": best and best["a_url"],
                      "best_score": best and best.get(a.metric), "shortlist": [r["a_url"] for r in keep],
                      "low": [r["a_url"] for r in keep if r["decision"] == LOW], "flag": flag,
                      "_last": not best or best["decision"] == LOW})
    pages.sort(key=lambda p: p.pop("_last"))
    out = Path(a.out_dir)
    write(out / "pairs_decided.jsonl", rows)
    write(out / "pages.jsonl", pages)
    L = [f"# Kiểm cặp tương đương — metric {a.metric}", "",
         f"- Ngưỡng: {gate or 'chưa có'} ({src or 'Claude đọc mọi cặp'}).",
         "- Chỉ số mô phỏng bằng embedding. Claude đọc 2 trang trước khi đề xuất thêm hay gỡ hreflang.", "",
         "- Ứng viên đầu = cosine cấp trang cao nhất, ưu tiên cặp trên ngưỡng loại.",
         "- Cặp dưới ngưỡng loại không bị loại: xếp cuối, đánh dấu (nháp, chưa holdout).", "",
         "| Trang B | Đã khai | Ứng viên đầu | Điểm | Ứng viên còn lại | Kết luận |", "|---|---|---|---|---|---|"]
    for p in pages:
        rest = ", ".join(u + (" (nháp)" if u in p["low"] else "") for u in p["shortlist"] if u != p["best"]) or "—"
        L.append(f"| {p['b_url']} | {', '.join(p['declared']) or '—'} | {p['best'] or '—'} | {p['best_score']} | {rest} | {p['flag']} |")
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(pages)} trang B -> {out}", file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs")
    p.add_argument("--store", required=True)
    p.add_argument("--page-store")
    p.add_argument("--b-prefix", required=True)
    p.add_argument("--declared")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--out", required=True)
    d = sub.add_parser("declared")
    d.add_argument("--html-dir", required=True)
    d.add_argument("--a-lang", default="vi")
    d.add_argument("--b-lang", default="en")
    d.add_argument("--out", required=True)
    r = sub.add_parser("report")
    r.add_argument("--pairs", required=True)
    r.add_argument("--out-dir", required=True)
    r.add_argument("--registry")
    r.add_argument("--site")
    r.add_argument("--metric", default="sec_cov", choices=["sec_cov", "page_cos"])
    a = ap.parse_args(argv)
    return {"pairs": cmd_pairs, "declared": cmd_declared, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
