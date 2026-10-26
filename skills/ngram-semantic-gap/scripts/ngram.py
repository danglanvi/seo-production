#!/usr/bin/env python3
"""N-gram tiếng Việt ở 2 cấp: cụm lặp toàn site và khoảng trống cụm của một trang so với top SERP.

Chạy bằng Python ≥ 3.9. Lệnh `comp` và `site` cần beautifulsoup4 (chạy `python3 -E`). Các lệnh khác chỉ cần stdlib.
  comp      --html-dir DIR --out DIR                     HTML trang (đối thủ hoặc trang mình) → JSON {title, meta, headings, text}
  page      --comp F... (--page-json F | --page-blocks F) --name M1 --out DIR [--tier1 a,b] [--attrs attrs.tsv] [--n 2-4]
  gsc       --gsc F --page URL (--page-json F | --page-blocks F) --name M1 --out DIR [--gap DIR] [--n 1-3]
  measure   --before F --after F --gap DIR --name M1 --out F.json [--gsc-ngrams F]
  sections  --page-blocks KEY=F ... --out rows.jsonl     section theo H2 → dòng input của svi.py build
  doorway   --pairs F --ref KEY [--sections rows.jsonl] [--pct 90] --out DIR
  site      --html-dir DIR --out DIR [--rep-min 5] [--groups groups.tsv]

Tách tiếng: chữ thường, NFC, chỉ chữ cái tiếng Việt và số. N-gram không vượt ranh giới dòng (khối chữ).
Cụm bắt đầu hoặc kết thúc bằng hư từ (STOP) bị bỏ, cụm toàn số bị bỏ.
Ngưỡng đồng thuận: cụm có ở ít nhất max(3, ⌈n/2⌉) trang đối thủ có chữ thân.
Dữ liệu GSC chỉ xử lý local bằng script này. Không gửi GSC vào Jev hay API bên ngoài.
Embedding section không làm ở đây: dùng svi.py của skill site-vector-index (lệnh `sections` dựng input cho nó).
"""
import argparse
import collections
import glob
import gzip
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

STOP = set("""và của là các những cho với được có trong để này một không khi thì từ đến tại theo như bạn chúng tôi sẽ đã
cũng về nhiều hơn ra vào lên mà nên nếu hay hoặc đó rất bị vì do người việc cần giúp gì nào bao mỗi đều vẫn còn đang thể
ta mình họ nó đây kể sau trước trên dưới qua lại thêm chỉ ấy rồi thế sự cách nhất""".split())
TOK = re.compile(r"[0-9a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+")
MDLINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


# ---------- tách tiếng và đếm ----------

def nfc(s):
    return unicodedata.normalize("NFC", s or "").lower()


def toks(s):
    return TOK.findall(nfc(s))


def parse_n(spec):
    if "-" in spec:
        a, b = spec.split("-", 1)
        return tuple(range(int(a), int(b) + 1))
    return tuple(int(x) for x in spec.split(","))


def grams(text, ns=(2, 3, 4)):
    """Đếm n-gram theo từng dòng. Thứ tự vòng lặp (dòng → n → vị trí) giữ thứ tự khoá ổn định cho phép sắp xếp."""
    c = collections.Counter()
    for line in text.split("\n"):
        t = toks(line)
        for n in ns:
            for i in range(len(t) - n + 1):
                g = t[i:i + n]
                if g[0] in STOP or g[-1] in STOP or all(x.isdigit() for x in g):
                    continue
                c[" ".join(g)] += 1
    return c


def strip_accents(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


# ---------- đọc input ----------

def read_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write_tsv(path, header, rows):
    with open(path, "w", encoding="utf-8") as fo:
        fo.write("\t".join(header) + "\n")
        for r in rows:
            fo.write("\t".join(map(str, r)) + "\n")


def read_tsv(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:] if l.strip()]


def doc_text(d):
    """Chữ của một trang đã trích: title, meta, heading, thân. Heading nhận dạng [tag, chữ] hoặc chữ."""
    heads = [h[1] if isinstance(h, (list, tuple)) else h for h in d.get("headings") or []]
    return (d.get("title") or "") + "\n" + (d.get("meta") or "") + "\n" + "\n".join(heads) + "\n" + (d.get("text") or "")


def full_text(d):
    """Trang có chữ thân. Trang chỉ lấy được heading (bị chặn 403) chỉ vào ma trận thuộc tính, không vào n-gram."""
    return bool((d.get("text") or "").strip()) and not d.get("headings_only")


def expand(paths):
    out = []
    for p in paths:
        hits = sorted(glob.glob(p))
        out.extend(hits if hits else [p])
    return out


def blocks_text(path, regions, keep_dup):
    """Chữ trang mình từ blocks jsonl. Lọc vùng khi dòng có trường region; bỏ khối trùng nguyên văn trừ khi --keep-dup."""
    seen, out = set(), []
    for d in read_jsonl(path):
        if regions and "region" in d and d["region"] not in regions:
            continue
        t = MDLINK.sub(r"\1", (d.get("text") or "")).strip()
        if not t:
            continue
        if not keep_dup:
            if t in seen:
                continue
            seen.add(t)
        out.append(t)
    return "\n".join(out)


def own_text(a):
    if a.page_json:
        return doc_text(json.loads(Path(a.page_json).read_text(encoding="utf-8")))
    regions = set(x for x in a.regions.split(",") if x) if a.regions else set()
    return blocks_text(a.page_blocks, regions, a.keep_dup)


def plain_text(path):
    """File bản trước hoặc bản đề xuất: .jsonl = blocks (vùng main, entry), .json = trang đã trích, còn lại = chữ thường."""
    p = Path(path)
    if p.suffix == ".jsonl":
        return blocks_text(p, {"main", "entry"}, False)
    if p.suffix == ".json":
        return doc_text(json.loads(p.read_text(encoding="utf-8")))
    return MDLINK.sub(r"\1", p.read_text(encoding="utf-8"))


# ---------- comp: HTML → JSON ----------

def cmd_comp(a):
    from bs4 import BeautifulSoup
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for fn in sorted(Path(a.html_dir).iterdir()):
        if not (fn.name.endswith(".html") or fn.name.endswith(".html.gz")):
            continue
        raw = gzip.decompress(fn.read_bytes()) if fn.name.endswith(".gz") else fn.read_bytes()
        soup = BeautifulSoup(raw.decode("utf-8", "ignore"), "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        md = soup.find("meta", attrs={"name": "description"})
        meta = md.get("content", "") if md else ""
        for t in soup(["script", "style", "noscript", "svg", "iframe", "form", "nav", "header", "footer", "aside"]):
            t.decompose()
        for sel in ['[class*="sidebar"]', '[class*="related-post"]', '[id*="comments"]', '[class*="breadcrumb"]',
                    '[id="ez-toc-container"]', '[class*="footer-widgets"]', '[id="footer"]']:
            for t in soup.select(sel):
                if t.name not in ("body", "html", "main", "article"):
                    t.decompose()
        cand = [c for c in (soup.find("main"), soup.find("article"), soup.body, soup) if c is not None]
        root = max(cand[:-1] or cand, key=lambda c: len(c.get_text(" ", strip=True))) if len(cand) > 1 else cand[0]
        heads = [[h.name, re.sub(r"\s+", " ", h.get_text(" ", strip=True))[:200]] for h in root.find_all(["h1", "h2", "h3"])
                 if h.get_text(strip=True)]
        blocks, seen = [], set()
        for el in root.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "blockquote"]):
            if el.find(["p", "li", "td"]) and el.name in ("li", "td"):
                continue
            tx = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
            if len(tx) > 2 and tx not in seen:
                seen.add(tx)
                blocks.append(tx)
        text = "\n".join(blocks)
        stem = fn.name.replace(".html.gz", "").replace(".html", "")
        rec = {"file": fn.name, "title": title, "meta": meta, "headings": heads, "text": text,
               "words": len(re.findall(r"\w+", text))}
        (out / f"{stem}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        print(stem, rec["words"], len(heads), file=sys.stderr)


# ---------- page: khoảng trống cụm của một trang ----------

def read_attrs(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, rx = line.split("\t", 1)
        if name == "thuoc_tinh":
            continue
        rows.append((name, rx))
    return rows


def level(wpct):
    return "MANDATORY" if wpct >= 80 else "RECOMMENDED" if wpct >= 50 else "OPTIONAL" if wpct >= 20 else "DIFFERENTIATOR"


def gap(docs, own, ns, top):
    """docs: {tên: chữ} của trang đối thủ có chữ thân, theo thứ tự SERP. Trả missing, unique, shared và ngưỡng đồng thuận."""
    per = {f: grams(t, ns) for f, t in docs.items()}
    dfc = collections.Counter(k for f in docs for k in per[f])
    gc = grams(own, ns)
    need = max(3, -(-len(docs) // 2))
    missing = sorted(((k, dfc[k], sum(per[f][k] for f in docs)) for k in dfc if dfc[k] >= need and gc[k] == 0),
                     key=lambda x: (-x[1], -x[2]))
    uniq = sorted(((k, gc[k]) for k in gc if dfc[k] == 0 and gc[k] >= 2), key=lambda x: -x[1])
    shared = sorted(((k, dfc[k], gc[k]) for k in gc if dfc[k] >= need), key=lambda x: (-x[1], -x[2]))
    return missing[:top], uniq[:top], shared[:top], need, (len(missing), len(uniq), len(shared))


def cmd_page(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = expand(a.comp)
    if not files:
        sys.exit("thiếu --comp")
    raw = {Path(f).stem: json.loads(Path(f).read_text(encoding="utf-8")) for f in files}
    docs = {k: doc_text(d) for k, d in raw.items()}
    full = {k: docs[k] for k in docs if full_text(raw[k])}
    own = own_text(a)
    tier1 = set(x for x in (a.tier1 or "").split(",") if x)
    unknown = tier1 - set(docs)
    if unknown:
        sys.exit(f"--tier1 có tên không nằm trong --comp: {sorted(unknown)}")
    ns = parse_n(a.n)
    missing, uniq, shared, need, counts = gap(full, own, ns, a.top)
    write_tsv(out / f"ngram_missing_{a.name}.tsv", ["ngram", "df_doi_thu", "tong_tan_so"], missing)
    write_tsv(out / f"ngram_unique_{a.name}.tsv", ["ngram", "tan_so_trang"], uniq)
    write_tsv(out / f"ngram_shared_{a.name}.tsv", ["ngram", "df_doi_thu", "tan_so_trang"], shared)
    summary = {"name": a.name, "n": list(ns), "docs": len(docs), "docs_full_text": len(full), "need_df": need,
               "headings_only": sorted(set(docs) - set(full)), "tier1": sorted(tier1),
               "missing": counts[0], "unique": counts[1], "shared": counts[2], "page_words": len(toks(own)),
               "comp_words": {k: len(toks(v)) for k, v in docs.items()}}
    if a.attrs:
        wtot = sum(2 if f in tier1 else 1 for f in docs)
        rows = []
        for name, rx in read_attrs(a.attrs):
            hit = [f for f in docs if re.search(rx, nfc(docs[f]))]
            w = sum(2 if f in tier1 else 1 for f in hit)
            wpct = round(100 * w / wtot)
            rows.append((name, len(hit), len(docs), round(100 * len(hit) / len(docs)), wpct, level(wpct),
                         "có" if re.search(rx, nfc(own)) else "KHÔNG", ",".join(hit)))
        write_tsv(out / f"consensus_{a.name}.tsv",
                  ["thuoc_tinh", "so_doi_thu", "tong", "pct", "pct_trong_so", "muc", "trang", "doi_thu_co"], rows)
        summary["attrs_missing_ge50"] = [r[0] for r in rows if r[4] >= 50 and r[6] == "KHÔNG"]
    (out / f"summary_{a.name}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("name", "docs", "docs_full_text", "need_df", "missing", "unique", "shared",
                                              "page_words")}, ensure_ascii=False))


# ---------- gsc: cụm query theo hiển thị ----------

def norm_path(u):
    u = re.sub(r"^https?://[^/]+", "", (u or "").strip())
    u = u.split("?")[0]
    return (u.rstrip("/") or "/") if u != "/" else "/"


def read_gsc(path, dims):
    """Nhận TSV/CSV có cột page, query, impressions, clicks, position; JSON API {"rows": [{"keys": [...]}]}; hoặc jsonl."""
    p = Path(path)
    txt = p.read_text(encoding="utf-8")
    rows = []
    if p.suffix == ".json":
        order = dims.split(",")
        for r in json.loads(txt)["rows"]:
            k = dict(zip(order, r["keys"]))
            rows.append({"query": k.get("query", ""), "page": k.get("page", ""), "impressions": r.get("impressions", 0),
                         "clicks": r.get("clicks", 0), "position": r.get("position", 0)})
    elif p.suffix == ".jsonl":
        rows = read_jsonl(p)
    else:
        sep = "\t" if p.suffix in (".tsv", ".txt") else ","
        lines = txt.splitlines()
        head = [h.strip().lower() for h in lines[0].split(sep)]
        for l in lines[1:]:
            if l.strip():
                rows.append(dict(zip(head, l.split(sep))))
    for r in rows:
        for f in ("impressions", "clicks", "position"):
            r[f] = float(r.get(f) or 0)
    return rows


def cmd_gsc(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    target = norm_path(a.page)
    agg, jump = {}, 0
    for r in read_gsc(a.gsc, a.dims):
        page = r.get("page", "")
        if "#" in page:  # dòng jump link (#ftoc-…) lặp hiển thị của URL gốc
            jump += 1
            continue
        if norm_path(page) != target:
            continue
        q = unicodedata.normalize("NFC", r["query"]).casefold().strip()
        x = agg.setdefault(q, {"impressions": 0.0, "clicks": 0.0, "pos_w": 0.0})
        x["impressions"] += r["impressions"]
        x["clicks"] += r["clicks"]
        x["pos_w"] += r["position"] * r["impressions"]
    own = grams(own_text(a), parse_n(a.n))
    gap_label = {}
    if a.gap:
        for kind in ("missing", "shared"):
            f = Path(a.gap) / f"ngram_{kind}_{a.name}.tsv"
            if f.exists():
                for r in read_tsv(f):
                    gap_label.setdefault(r["ngram"], kind)
    ng = {}
    for q, x in agg.items():
        for g in set(grams(q, parse_n(a.n))):
            y = ng.setdefault(g, {"impressions": 0.0, "clicks": 0.0, "pos_w": 0.0, "queries": 0})
            y["impressions"] += x["impressions"]
            y["clicks"] += x["clicks"]
            y["pos_w"] += x["pos_w"]
            y["queries"] += 1
    # Biến thể dấu: cùng dạng bỏ dấu với một cụm khác có nhiều hiển thị hơn ("dich vu seo", "dich vụ seo" của "dịch vụ seo").
    lead = {}
    for g, y in ng.items():
        k = strip_accents(g)
        if y["impressions"] > lead.get(k, (None, -1))[1]:
            lead[k] = (g, y["impressions"])
    rows = []
    for g, y in sorted(ng.items(), key=lambda kv: (-kv[1]["impressions"], kv[0])):
        variant = int(lead[strip_accents(g)][0] != g)
        pos = y["pos_w"] / y["impressions"] if y["impressions"] else 0
        rows.append((g, len(g.split()), int(y["impressions"]), int(y["clicks"]), y["queries"], f"{pos:.1f}",
                     own[g], gap_label.get(g, "-"), variant))
    write_tsv(out / f"gsc_ngram_{a.name}.tsv",
              ["ngram", "n", "impressions", "clicks", "queries", "vi_tri_tb", "tan_so_trang", "doi_thu", "bien_the_dau"],
              rows[:a.top])
    tot = sum(x["impressions"] for x in agg.values())
    s = {"name": a.name, "page": target, "queries": len(agg), "impressions": int(tot), "jump_rows_skipped": jump,
         "ngrams": len(rows), "missing_on_page_top20": [r[0] for r in rows if r[6] == 0 and not r[8]][:20]}
    (out / f"gsc_summary_{a.name}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False))


# ---------- measure: đo bản đề xuất trước khi ghi ----------

def cmd_measure(a):
    before, after = plain_text(a.before), plain_text(a.after)
    ns = parse_n(a.n)
    gb, ga = grams(before, ns), grams(after, ns)
    gdir = Path(a.gap)
    miss = read_tsv(gdir / f"ngram_missing_{a.name}.tsv")[:a.top_missing]
    covered, stuffed = [], []
    for r in miss:
        k, df, tf = r["ngram"], int(r["df_doi_thu"]), int(r["tong_tan_so"])
        cap = max(3, 2 * math.ceil(tf / df))  # gấp đôi tần số trung bình trên một trang đối thủ có cụm
        if ga[k]:
            covered.append({"ngram": k, "after": ga[k], "df_doi_thu": df})
            if ga[k] > cap:
                stuffed.append({"ngram": k, "after": ga[k], "cap": cap})
    uf = gdir / f"ngram_unique_{a.name}.tsv"
    lost = [r["ngram"] for r in read_tsv(uf) if gb[r["ngram"]] and not ga[r["ngram"]]] if uf.exists() else []
    res = {"name": a.name, "words_before": len(toks(before)), "words_after": len(toks(after)),
           "missing_checked": len(miss), "missing_covered_before": sum(1 for r in miss if gb[r["ngram"]]),
           "missing_covered_after": len(covered), "covered": covered, "stuffing": stuffed,
           "unique_lost": lost}
    if a.gsc_ngrams:
        g = [r for r in read_tsv(a.gsc_ngrams) if int(r["n"]) >= 2 and r["bien_the_dau"] == "0"][:a.top_gsc]
        tot = sum(int(r["impressions"]) for r in g) or 1
        res["gsc_top"] = len(g)
        res["gsc_impr_covered_before"] = round(sum(int(r["impressions"]) for r in g if gb[r["ngram"]]) / tot, 3)
        res["gsc_impr_covered_after"] = round(sum(int(r["impressions"]) for r in g if ga[r["ngram"]]) / tot, 3)
        res["gsc_still_missing"] = [r["ngram"] for r in g if not ga[r["ngram"]]][:20]
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("covered",)}, ensure_ascii=False))


# ---------- sections + doorway: so section giữa các trang cùng template ----------

def cmd_sections(a):
    regions = set(a.regions.split(","))
    out = open(a.out, "w", encoding="utf-8")
    n = 0
    for spec in a.page_blocks:
        key, path = spec.split("=", 1)
        secs, order, seen, url = {}, [], set(), ""
        for d in read_jsonl(path):
            url = url or d.get("url", "")
            if "region" in d and d["region"] not in regions:
                continue
            t = (d.get("text") or "").strip()
            if not t or t in seen:
                continue
            if re.search(r"https?://|\.(jpg|png|webp|svg|gif|mp4)\b", t):
                continue
            if len(t) < 25 and d.get("tag") not in ("h2", "h3"):
                continue
            seen.add(t)
            h = d.get("h2") or "(hero)"
            if d.get("tag") == "h2":
                h = t
            if h not in secs:
                secs[h] = []
                order.append(h)
            secs[h].append(t)
        for i, h in enumerate(order):
            text = " ".join(secs[h])
            if len(text) < a.min_chars:
                continue
            out.write(json.dumps({"id": f"{key}-{i:02d}", "level": "section", "url": url or key, "text": text[:6000],
                                  "meta": {"page": key, "h2": h[:120]}}, ensure_ascii=False) + "\n")
            n += 1
    out.close()
    print(n, "section", file=sys.stderr)


def shingles(t, k=5):
    w = re.findall(r"\w+", t.lower())
    return set(" ".join(w[i:i + k]) for i in range(len(w) - k + 1))


def percentile(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f = math.floor(k)
    return xs[f] if f + 1 >= len(xs) else xs[f] + (xs[f + 1] - xs[f]) * (k - f)


def page_of(sid):
    return sid.rsplit("-", 1)[0]


def cmd_doorway(a):
    p = Path(a.pairs)
    if p.suffix == ".jsonl":
        pairs = [(r["a"], r["b"], float(r["cos"])) for r in read_jsonl(p)]
    else:
        pairs = [(r["a"], r["b"], float(r["cos"])) for r in read_tsv(p)]
    sec = {r["id"]: r for r in read_jsonl(a.sections)} if a.sections else {}
    pairs = [x for x in pairs if page_of(x[0]) != page_of(x[1])]
    cut = percentile([c for _, _, c in pairs], a.pct)
    best = {}
    for x, y, c in pairs:
        for s, t in ((x, y), (y, x)):
            if page_of(t) == a.ref and page_of(s) != a.ref and c > best.get(s, (None, -9))[1]:
                best[s] = (t, c)
    pages = collections.defaultdict(list)
    ids = set(sec) or {i for x in pairs for i in x[:2]}
    for s in sorted(ids):
        if page_of(s) != a.ref:
            pages[page_of(s)].append(s)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, summ = [], {"ref": a.ref, "pct": a.pct, "cut": round(cut, 4), "pairs": len(pairs), "pages": {}}
    for pg, ss in sorted(pages.items()):
        hit = 0
        for s in ss:
            t, c = best.get(s, ("", float("nan")))
            jac = ""
            if s in sec and t in sec:
                A, B = shingles(sec[s]["text"]), shingles(sec[t]["text"])
                jac = f"{len(A & B) / max(1, len(A | B)):.3f}"
            near = c >= cut
            hit += near
            rows.append((s, t, f"{c:.3f}", jac, int(near), (sec.get(s, {}).get("meta", {}).get("h2", ""))[:80]))
        summ["pages"][pg] = {"sections": len(ss), "ge_cut": hit}
    write_tsv(out / "doorway_sections.tsv", ["section", "gan_nhat_ref", "cos", "jaccard5", "tu_cut", "h2"], rows)
    (out / "doorway_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False))


# ---------- site: cụm lặp toàn site ----------

BLOCK = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "figcaption", "dt", "dd", "div", "section",
         "article", "button", "label", "summary", "caption", "header", "footer", "main", "aside", "nav", "ul", "ol", "table", "form"}
SEL = {"header": ".elementor-location-header, #masthead, .site-header, body > header",
       "footer": ".elementor-location-footer, #colophon, .site-footer, body > footer",
       "floating": "", "entry": ".entry-content", "nav": "nav, .mega-menu-wrap"}


def segments(html, sel):
    from bs4 import BeautifulSoup, Comment, NavigableString
    s = BeautifulSoup(html, "html.parser")
    for c in s.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    body = s.body or s
    for el in body.find_all(["script", "style", "noscript", "svg", "template", "iframe"]):
        el.decompose()
    marks = {}

    def region_of(el):
        for p in [el] + list(el.parents):
            k = marks.get(id(p))
            if k:
                return k
        return "main"

    for name in ("header", "footer", "floating", "entry"):
        if sel[name]:
            for el in body.select(sel[name]):
                marks[id(el)] = name
    if sel["nav"]:
        for el in body.select(sel["nav"]):
            if region_of(el) == "main":
                marks[id(el)] = "nav"
    out, cur = [], None
    for node in body.descendants:
        if not isinstance(node, NavigableString):
            continue
        t = str(node).strip()
        if not t:
            continue
        par = node.parent
        while par is not None and par.name not in BLOCK:
            par = par.parent
        k = id(par)
        if cur and cur[0] == k:
            cur[2] += " " + t
            continue
        if cur:
            out.append(cur)
        cur = [k, region_of(par) if par is not None else "main", t]
    if cur:
        out.append(cur)
    return [(r, unicodedata.normalize("NFC", re.sub(r"\s+", " ", t)).strip()) for _, r, t in out]


def html_pages(d):
    """Thư mục HTML: <x>.html hoặc <x>.html.gz, URL ở file <x>.url cạnh bên (cache của site-vector-index); thiếu thì dùng tên file."""
    for f in sorted(Path(d).iterdir()):
        if f.name.endswith(".html") or f.name.endswith(".html.gz"):
            stem = f.name.replace(".html.gz", "").replace(".html", "")
            uf = f.with_name(stem + ".url")
            url = uf.read_text(encoding="utf-8").strip() if uf.exists() else stem
            raw = gzip.decompress(f.read_bytes()) if f.name.endswith(".gz") else f.read_bytes()
            yield url, raw.decode("utf-8", "ignore")


def cmd_site(a):
    import statistics
    sel = dict(SEL)
    for k in SEL:
        v = getattr(a, f"sel_{k}")
        if v is not None:
            sel[k] = v
    ns = parse_n(a.n)
    segs = {u: segments(h, sel) for u, h in html_pages(a.html_dir)}
    N = len(segs)
    if not N:
        sys.exit("không có file HTML")
    seg_pages = collections.defaultdict(set)
    for u, ss in segs.items():
        for r, t in ss:
            if r in ("main", "entry") and toks(t):
                seg_pages[(r, t.lower())].add(u)

    def cls(r, t):
        if r in ("header", "footer", "floating", "nav"):
            return "boiler_site"
        if len(seg_pages[(r, t.lower())]) >= a.rep_min:
            return "boiler_tpl" if r == "main" else "boiler_entry"
        return "content"

    df = {c: collections.Counter() for c in ("content", "boiler")}
    tf = {c: collections.Counter() for c in ("content", "boiler")}
    df_all, words = collections.Counter(), {}
    for u, ss in segs.items():
        w = collections.Counter()
        seen = {"content": set(), "boiler": set()}
        for r, t in ss:
            c = cls(r, t)
            k = "content" if c == "content" else "boiler"
            w[c] += len(toks(t))
            for g, cnt in grams(t, ns).items():
                tf[k][g] += cnt
                seen[k].add(g)
        for k in seen:
            df[k].update(seen[k])
        df_all.update(seen["content"] | seen["boiler"])
        words[u] = w
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "ngram_site_top.tsv", ["ngram", "n", "df_pages_any", "df_content", "df_boiler", "tf_content", "tf_boiler"],
              [(g, len(g.split()), d, df["content"][g], df["boiler"][g], tf["content"][g], tf["boiler"][g])
               for g, d in df_all.most_common(a.top)])
    write_tsv(out / "ngram_content_top.tsv", ["ngram", "n", "df_content", "tf_content"],
              [(g, len(g.split()), d, tf["content"][g]) for g, d in df["content"].most_common(a.top // 2)])
    boil = sorted(((g, d) for g, d in df["boiler"].items() if d >= a.boiler_pct / 100 * N),
                  key=lambda x: (-x[1], -tf["boiler"][x[0]]))
    write_tsv(out / "ngram_boiler_sitewide.tsv", ["ngram", "n", "df_boiler", "pct_pages", "tf_boiler"],
              [(g, len(g.split()), d, f"{d / N:.1%}", tf["boiler"][g]) for g, d in boil])
    rep = sorted(((k, v) for k, v in seg_pages.items() if len(v) >= a.rep_min), key=lambda x: -len(x[1]) * len(toks(x[0][1])))
    write_tsv(out / "repeated_segments.tsv", ["region", "pages", "words", "text"],
              [(r, len(v), len(toks(t)), t[:300]) for (r, t), v in rep])
    groups = {}
    if a.groups:
        groups = {r["url"]: r["group"] for r in read_tsv(a.groups)}
    rows = []
    for u, w in words.items():
        tot = sum(w.values()) or 1
        b = w["boiler_site"] + w["boiler_tpl"] + w["boiler_entry"]
        g = groups.get(u) or ("/" + norm_path(u).strip("/").split("/")[0] if norm_path(u) != "/" else "/")
        rows.append((u, g, tot, w["content"], w["boiler_site"], w["boiler_tpl"], w["boiler_entry"], f"{b / tot:.3f}"))
    write_tsv(out / "page_regions.tsv", ["url", "group", "words_total", "content", "boiler_site", "boiler_tpl", "boiler_entry",
                                         "boiler_share"], rows)
    by = collections.defaultdict(list)
    for r in rows:
        by[r[1]].append(r)
    tpl = {g: {"pages": len(rs), "median_words_total": statistics.median(r[2] for r in rs),
               "median_content": statistics.median(r[3] for r in rs),
               "median_boiler_share": round(statistics.median(float(r[7]) for r in rs), 3)}
           for g, rs in sorted(by.items(), key=lambda x: -len(x[1]))}
    s = {"pages": N, "rep_min": a.rep_min, "boiler_pct": a.boiler_pct, "boiler_ngrams": len(boil),
         "repeated_segments": len(rep), "template_ratio": tpl}
    (out / "site_summary.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: s[k] for k in ("pages", "boiler_ngrams", "repeated_segments")}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("comp")
    c.add_argument("--html-dir", required=True)
    c.add_argument("--out", required=True)

    def own(p, n_default):
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--page-json", help="trang mình đã trích bằng lệnh comp (khuyên dùng: cùng cách trích với đối thủ)")
        g.add_argument("--page-blocks", help="blocks jsonl {text, region?} của trang mình")
        p.add_argument("--regions", default="main,entry", help="vùng giữ lại khi blocks có trường region")
        p.add_argument("--keep-dup", action="store_true", help="giữ khối chữ trùng nguyên văn")
        p.add_argument("--name", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--n", default=n_default, help="số tiếng của cụm, ví dụ 2-4 hoặc 1,2,3")
        p.add_argument("--top", type=int, default=300)

    p = sub.add_parser("page")
    p.add_argument("--comp", nargs="+", required=True, help="JSON trang đối thủ theo thứ tự SERP; nhận glob")
    p.add_argument("--tier1", default="", help="tên trang đối thủ ở vị trí 1–3, trọng số gấp đôi trong ma trận thuộc tính")
    p.add_argument("--attrs", help="TSV thuoc_tinh<TAB>regex")
    own(p, "2-4")
    g = sub.add_parser("gsc")
    g.add_argument("--gsc", required=True)
    g.add_argument("--dims", default="query,page", help="thứ tự keys trong JSON của API")
    g.add_argument("--page", required=True)
    g.add_argument("--gap", help="thư mục output của lệnh page, để gắn nhãn missing/shared")
    own(g, "1-3")
    m = sub.add_parser("measure")
    m.add_argument("--before", required=True)
    m.add_argument("--after", required=True)
    m.add_argument("--gap", required=True)
    m.add_argument("--name", required=True)
    m.add_argument("--gsc-ngrams")
    m.add_argument("--n", default="2-4")
    m.add_argument("--top-missing", type=int, default=50)
    m.add_argument("--top-gsc", type=int, default=30)
    m.add_argument("--out", required=True)
    s = sub.add_parser("sections")
    s.add_argument("--page-blocks", nargs="+", required=True, help="KEY=blocks.jsonl, ví dụ M1=blocks_M1.jsonl")
    s.add_argument("--regions", default="main,entry")
    s.add_argument("--min-chars", type=int, default=120)
    s.add_argument("--out", required=True)
    d = sub.add_parser("doorway")
    d.add_argument("--pairs", required=True, help="output svi.py pairs (jsonl) hoặc TSV có cột a, b, cos")
    d.add_argument("--ref", required=True, help="KEY của trang gốc, ví dụ M1")
    d.add_argument("--sections")
    d.add_argument("--pct", type=float, default=90)
    d.add_argument("--out", required=True)
    t = sub.add_parser("site")
    t.add_argument("--html-dir", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--rep-min", type=int, default=5, help="khối chữ lặp nguyên văn trên từ chừng này trang = khối template")
    t.add_argument("--boiler-pct", type=float, default=80)
    t.add_argument("--groups", help="TSV url<TAB>group (template); thiếu thì gom theo thư mục đầu")
    t.add_argument("--n", default="1-3")
    t.add_argument("--top", type=int, default=3000)
    for k in SEL:
        t.add_argument(f"--sel-{k}", dest=f"sel_{k}", default=None, help=f"CSS selector vùng {k}")
    a = ap.parse_args()
    {"comp": cmd_comp, "page": cmd_page, "gsc": cmd_gsc, "measure": cmd_measure, "sections": cmd_sections,
     "doorway": cmd_doorway, "site": cmd_site}[a.cmd](a)


if __name__ == "__main__":
    main()
