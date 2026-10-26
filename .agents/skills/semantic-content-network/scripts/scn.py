#!/usr/bin/env python3
"""Phần tất định của plan mạng nội dung (SCN): đồ thị link, kiểm SERP trước khi gộp, template Query Processing, trạng thái thẻ, lô duyệt.

Chạy bằng Python ≥ 3.9, chỉ cần thư viện chuẩn.
  graph         --sf DIR --out DIR [--home URL] [--money money.tsv] [--add add.tsv]
                Screaming Frog (internal_all.csv, all_inlinks.csv) → click depth, PageRank nội bộ, link ngữ cảnh, what-if
  serp-overlap  --serp F... --out DIR [--pairs pairs.tsv] [--top 10]
                SERP top 10 (TSV seed/pos/url hoặc thư mục JSON Firecrawl) → số URL chung, verdict theo ngưỡng 6/10
  qp            --gsc F --templates templates.tsv --out DIR
                GSC query × page 90 ngày + regex template → mốc theo template, URL Google chọn, cờ tách/lật URL
  status        --reviews DIR --cards F... --out status.json [--until ISO]
  guard         --reviews DIR --cards F --out guard.json [--until ISO]     chặn sửa chữ đã duyệt, chặn dùng lại id đã duyệt
  batch         --lots lots.json --cards F... --status status.json --out DIR [--report <đường dẫn plan>]

Ngưỡng SERP: từ 6/10 URL chung là cùng nhóm, 4–5/10 là vùng xám, dưới 4/10 là tách (luật Query Processing).
Dữ liệu GSC chỉ xử lý local bằng script này. Không gửi GSC vào Jev hay API bên ngoài.
"""
import argparse
import collections
import csv
import glob
import itertools
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

csv.field_size_limit(sys.maxsize)


def read_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def read_tsv(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def wjson(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def expand(paths):
    out = []
    for p in paths:
        hits = sorted(glob.glob(p))
        out.extend(hits if hits else [p])
    return out


# ---------- graph: depth, PageRank, link ngữ cảnh ----------

def load_sf(d, rep_min):
    """Link ngữ cảnh = link vị trí Content mà cặp anchor–đích xuất hiện trên dưới rep_min trang nguồn (loại khối template)."""
    d = Path(d)
    pages, sf_depth = set(), {}
    with open(d / "internal_all.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if (r.get("Content Type", "").startswith("text/html") and r.get("Status Code") == "200"
                    and r.get("Indexability") == "Indexable"):
                pages.add(r["Address"])
                sf_depth[r["Address"]] = r.get("Crawl Depth", "")
    out = collections.defaultdict(set)
    pos_rows = collections.defaultdict(collections.Counter)  # số dòng link theo vị trí (một trang có thể link nhiều lần)
    ct_anchor = collections.defaultdict(set)
    pair_src = collections.defaultdict(set)
    with open(d / "all_inlinks.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            s, t = r["Source"], r["Destination"].split("#")[0]
            if r.get("Type") != "Hyperlink" or r.get("Follow") != "true" or s not in pages or t not in pages or s == t:
                continue
            out[s].add(t)
            pos_rows[t][r.get("Link Position", "")] += 1
            if r.get("Link Position") == "Content":
                anc = re.sub(r"\s+", " ", (r.get("Anchor") or r.get("Alt Text") or "")).strip().lower()
                ct_anchor[(s, t)].add(anc)
                pair_src[(t, anc)].add(s)
    ctx = {e for e, ancs in ct_anchor.items() if any(len(pair_src[(e[1], x)]) < rep_min for x in ancs)}
    return pages, sf_depth, out, ctx, pos_rows


def pagerank(pages, out, d=0.85, it=40):
    n = len(pages)
    pr = {p: 1 / n for p in pages}
    for _ in range(it):
        nxt = {p: (1 - d) / n for p in pages}
        dangling = sum(pr[p] for p in pages if not out[p])
        for s in pages:
            for t in out[s]:
                nxt[t] += d * pr[s] / len(out[s])
        for p in pages:
            nxt[p] += d * dangling / n
        pr = nxt
    return pr


def bfs(home, adj):
    dist, q = {home: 0}, collections.deque([home])
    while q:
        u = q.popleft()
        for v in sorted(adj.get(u, ())):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def graph_tables(pages, out, ctx, home):
    content = collections.defaultdict(set)
    src = collections.defaultdict(set)
    src_ct = collections.defaultdict(set)
    for s, ts in out.items():
        for t in ts:
            src[t].add(s)
    for s, t in ctx:
        content[s].add(t)
        src_ct[t].add(s)
    return {"pr": pagerank(sorted(pages), out), "d_all": bfs(home, out), "d_ct": bfs(home, content),
            "src": src, "src_ct": src_ct}


def cmd_graph(a):
    pages, sf_depth, out, ctx, pos = load_sf(a.sf, a.rep_min)
    if not pages:
        sys.exit("không có trang HTML 200 index được trong internal_all.csv")
    ctx_src = f"Screaming Frog: vị trí Content, cặp anchor–đích lặp dưới {a.rep_min} trang"
    if a.ctx_rows:  # anchor vùng main content của site-vector-index (extract.py đã bỏ nav, footer, khối liên quan)
        ctx = {(r["url"], r["meta"]["target"]) for r in read_jsonl(a.ctx_rows)
               if r.get("level") == "anchor" and r["url"] in pages and (r.get("meta") or {}).get("target") in pages
               and r["url"] != r["meta"]["target"]}
        ctx_src = f"site-vector-index anchor: {a.ctx_rows}"
    home = a.home or min(pages, key=lambda u: (len(urlparse(u).path), u))
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    g = graph_tables(pages, out, ctx, home)
    pr = g["pr"]
    rows = sorted(pages, key=lambda p: (-round(pr[p], 12), p))
    # cùng định dạng file pagerank_internal.tsv của workstream 18/10
    with open(od / "pagerank_internal.tsv", "w") as f:
        f.write("hang\turl\tpr_x1000\tso_trang_nguon\tcontent\tnavigation\theader\tfooter\n")
        for i, p in enumerate(rows, 1):
            c = pos[p]
            f.write(f"{i}\t{p}\t{pr[p] * 1000:.3f}\t{len(g['src'][p])}\t{c['Content']}\t{c['Navigation']}\t{c['Header']}\t{c['Footer']}\n")
    money = {}
    if a.money:
        money = {r["url"]: r.get("ma", r["url"]) for r in read_tsv(a.money)}
    after = None
    if a.add:
        out2 = collections.defaultdict(set, {k: set(v) for k, v in out.items()})
        ctx2 = set(ctx)
        added, skipped = 0, []
        for r in read_tsv(a.add):
            s, t = r["source"], r["target"]
            if s not in pages or t not in pages:
                skipped.append([s, t])
                continue
            out2[s].add(t)
            if (r.get("position") or "Content") == "Content":
                ctx2.add((s, t))
            added += 1
        after = graph_tables(pages, out2, ctx2, home)
    with open(od / "pages.tsv", "w") as f:
        head = ["url", "ma", "depth_all", "depth_ngu_canh", "sf_crawl_depth", "trang_nguon", "trang_nguon_ngu_canh", "pr_x1000"]
        if after:
            head += ["depth_all_sau", "depth_ngu_canh_sau", "trang_nguon_ngu_canh_sau", "pr_x1000_sau"]
        f.write("\t".join(head) + "\n")
        for p in rows:
            v = [p, money.get(p, ""), g["d_all"].get(p, ""), g["d_ct"].get(p, ""), sf_depth.get(p, ""), len(g["src"][p]),
                 len(g["src_ct"][p]), f"{pr[p] * 1000:.3f}"]
            if after:
                v += [after["d_all"].get(p, ""), after["d_ct"].get(p, ""), len(after["src_ct"][p]), f"{after['pr'][p] * 1000:.3f}"]
            f.write("\t".join(map(str, v)) + "\n")

    def dist(d):
        c = collections.Counter(d.get(p, "không tới") for p in pages)
        return {str(k): c[k] for k in sorted(c, key=lambda x: (isinstance(x, str), x))}

    s = {"pages": len(pages), "home": home, "edges": sum(len(v) for v in out.values()), "nguon_link_ngu_canh": ctx_src,
         "canh_ngu_canh": len(ctx),
         "depth_all": dist(g["d_all"]), "depth_ngu_canh": dist(g["d_ct"]),
         "khong_link_ngu_canh_vao": sum(1 for p in pages if p != home and not g["src_ct"][p]),
         "sf_depth_khop": sum(1 for p in pages if str(g["d_all"].get(p, "")) == str(sf_depth.get(p, ""))),
         "money": {money[p]: {"url": p, "depth_all": g["d_all"].get(p), "depth_ngu_canh": g["d_ct"].get(p),
                              "trang_nguon_ngu_canh": len(g["src_ct"][p]), "hang_pr": rows.index(p) + 1}
                   for p in money if p in pages}}
    if after:
        s["what_if"] = {"them": added, "bo_qua": skipped, "depth_ngu_canh_sau": dist(after["d_ct"]),
                        "money_sau": {money[p]: {"depth_ngu_canh": after["d_ct"].get(p),
                                                 "trang_nguon_ngu_canh": len(after["src_ct"][p])} for p in money if p in pages}}
    wjson(od / "graph_summary.json", s)
    print(json.dumps({k: s[k] for k in ("pages", "edges", "depth_all", "depth_ngu_canh", "khong_link_ngu_canh_vao", "sf_depth_khop")},
                     ensure_ascii=False))


# ---------- serp-overlap ----------

def norm_url(u):
    p = urlparse(u)
    return (p.netloc.replace("www.", "") + p.path).rstrip("/")


def load_serp(paths, top):
    """TSV có cột seed, pos, url; hoặc file JSON Firecrawl search (tên file = truy vấn, '_' thay khoảng trắng)."""
    urls = {}
    for p in expand(paths):
        pth = Path(p)
        files = sorted(pth.glob("*.json")) if pth.is_dir() else [pth]
        for f in files:
            if f.suffix == ".json":
                d = json.loads(f.read_text(encoding="utf-8"))
                web = (d.get("data") or {}).get("web") if isinstance(d.get("data"), dict) else d.get("data")
                if web is None:
                    continue
                q = unicodedata.normalize("NFC", f.stem.replace("_", " "))
                urls.setdefault(q, [norm_url(x["url"]) for x in web[:top]])
            else:
                rows = sorted(read_tsv(f), key=lambda r: int(r["pos"]))
                order = []
                for r in read_tsv(f):
                    if r["seed"] not in order:
                        order.append(r["seed"])
                for q in order:
                    if q not in urls:
                        urls[q] = [norm_url(r["url"]) for r in rows if r["seed"] == q][:top]
    return urls


def verdict(n):
    return "cùng nhóm" if n >= 6 else "vùng xám" if n >= 4 else "tách"


def cmd_serp(a):
    urls = load_serp(a.serp, a.top)
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    allp = {f"{x} | {y}": len(set(urls[x]) & set(urls[y])) for x, y in itertools.combinations(urls, 2)}
    wjson(od / "overlap_all.json", allp)
    res = []
    if a.pairs:
        for r in read_tsv(a.pairs):
            x, y = unicodedata.normalize("NFC", r["a"]), unicodedata.normalize("NFC", r["b"])
            if x not in urls or y not in urls:
                res.append({"a": x, "b": y, "chung": None, "verdict": "thiếu SERP", "note": r.get("note", "")})
                continue
            n = len(set(urls[x]) & set(urls[y]))
            short = min(len(urls[x]), len(urls[y])) < a.top
            res.append({"a": x, "b": y, "chung": n, "verdict": verdict(n) + (" · SERP dưới 10 URL" if short else ""),
                        "url_chung": sorted(set(urls[x]) & set(urls[y])), "note": r.get("note", "")})
        with open(od / "overlap_pairs.tsv", "w", encoding="utf-8") as f:
            f.write("a\tb\tchung\tverdict\tnote\n")
            for r in res:
                f.write(f"{r['a']}\t{r['b']}\t{'' if r['chung'] is None else r['chung']}/{a.top}\t{r['verdict']}\t{r['note']}\n")
        wjson(od / "overlap_pairs.json", res)
    print(json.dumps({"seeds": len(urls), "pairs": len(res), "verdict": collections.Counter(r["verdict"].split(" ·")[0] for r in res)},
                     ensure_ascii=False))


# ---------- qp: template Query Processing từ GSC ----------

def read_gsc(path, dims):
    p = Path(path)
    if p.suffix == ".json":
        order = dims.split(",")
        for r in json.loads(p.read_text(encoding="utf-8"))["rows"]:
            k = dict(zip(order, r["keys"]))
            yield k["query"], k["page"], r["impressions"], r["clicks"], r["position"]
    else:
        for r in read_tsv(p):
            yield r["query"], r["page"], float(r["impressions"]), float(r["clicks"]), float(r["position"])


def path_of(u):
    return re.sub(r"^https?://[^/]+", "", u) or "/"


def qp_flag(target, urls, tot):
    if not tot:
        return "chưa đo được"
    u1, s1, p1 = urls[0]
    if not target.startswith("/"):
        return "chưa chọn URL đích"
    tail = " · chưa vào Top 10" if p1 > 10 else ""
    if u1 == target:
        return ("ổn" if s1 >= 60 else "tách URL") + tail
    return ("lật URL" if s1 >= 50 else "tách URL") + tail


def cmd_qp(a):
    rows = [r for r in read_gsc(a.gsc, a.dims) if "#" not in r[1]]  # bỏ dòng jump link: lặp hiển thị của URL gốc
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    out = []
    for t in read_tsv(a.templates):
        rx = t["regex"]
        c, clk, pw, nq = collections.Counter(), collections.Counter(), collections.defaultdict(float), set()
        for q, p, imp, ck, pos in rows:
            if re.search(rx, q):
                p = path_of(p)
                c[p] += imp
                clk[p] += ck
                pw[p] += pos * imp
                nq.add(q)
        tot = sum(c.values())
        top = [(u, round(v / tot * 100), round(pw[u] / v, 1)) for u, v in c.most_common(3)] if tot else []
        out.append({"id": t["id"], "template": t["template"], "target": t["target"], "regex": rx, "n_query": len(nq),
                    "impr": tot, "clicks": sum(clk.values()), "urls": top, "flag": qp_flag(t["target"], top, tot)})
    wjson(od / "baseline.json", out)
    with open(od / "baseline.tsv", "w") as fh:
        fh.write("id\ttemplate\ttrang đích\tsố truy vấn\tlượt hiển thị\tclick\tURL 1\tURL 2\tregex\n")
        for d in out:
            u = [f"{x} {y}% vt {z}" for x, y, z in d["urls"]] + ["", ""]
            fh.write(f"{d['id']}\t{d['template']}\t{d['target']}\t{d['n_query']}\t{d['impr']}\t{d['clicks']}\t{u[0]}\t{u[1]}\t{d['regex']}\n")
    with open(od / "qp_flags.tsv", "w") as fh:
        fh.write("id\ttemplate\ttrang đích\tURL Google chọn\ttỷ lệ\tvị trí\tcờ\n")
        for d in out:
            u1 = d["urls"][0] if d["urls"] else ("", "", "")
            fh.write(f"{d['id']}\t{d['template']}\t{d['target']}\t{u1[0]}\t{u1[1]}\t{u1[2]}\t{d['flag']}\n")
    print(json.dumps({"templates": len(out), "flags": collections.Counter(d["flag"].split(" ·")[0] for d in out)}, ensure_ascii=False))


# ---------- thẻ duyệt: status, guard, batch ----------

def load_cards(paths):
    items, section = {}, {}
    for p in expand(paths):
        for it in json.loads(Path(p).read_text(encoding="utf-8"))["items"]:
            items[it["id"]] = it
            section[it["id"]] = Path(p).stem
    return items, section


def load_reviews(d, until=None):
    rev = {}
    for f in sorted(Path(d).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if "item_id" not in r:
            continue
        if until and (r.get("updatedAt") or "") > until:
            continue
        rev[r["item_id"]] = r
    return rev


def cmd_status(a):
    items, section = load_cards(a.cards)
    rev = load_reviews(a.reviews, a.until)
    st = {cid: [section[cid], it.get("kind", ""), rev[cid]["status"] if cid in rev else "pending", it.get("label", "")]
          for cid, it in items.items()}
    wjson(a.out, st)
    by = collections.Counter(v[2] for v in st.values())
    pre = collections.Counter(f"{v[0]}:{v[2]}" for v in st.values())
    print(json.dumps({"cards": len(st), "status": by, "by_section": dict(sorted(pre.items()))}, ensure_ascii=False))


def clean(t):
    t = re.sub(r"\[IMG alt=\"[^\"]*\"\]", " ", t or "")
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("**", "").replace("&amp;", "&").replace(" ", " ")
    t = re.sub(r"^\s*[-*]\s+", " ", t, flags=re.M)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", t).strip())


def variants(fld):
    return {k: clean(fld[k]) for k in ("proposed", "A", "B") if isinstance(fld.get(k), str)}


def cmd_guard(a):
    items, _ = load_cards([a.cards])
    rev = load_reviews(a.reviews, a.until)
    done = {k: r for k, r in rev.items() if r.get("status") in ("approved", "edited", "applied")}
    approved = []
    for r in done.values():
        for k, v in (r.get("values") or {}).items():
            if k in ("slug", "flag") or not isinstance(v, str):
                continue
            n = clean(v)
            if len(n) >= 25:
                approved.append({"id": r["item_id"], "key": k, "head": n[:60], "tail": n[-60:], "text": n})
    reuse, overlap = [], []
    for cid, c in items.items():
        if cid in done:
            vals = done[cid].get("values") or {}
            changed = [f["key"] for f in c["fields"] if f["key"] in vals and isinstance(vals[f["key"]], str)
                       and clean(vals[f["key"]]) not in variants(f).values()]
            reuse.append({"card": cid, "status": done[cid]["status"], "field_changed": changed})
        for i, f in enumerate(c["fields"]):
            before = clean(f.get("before", ""))
            if not before or before.startswith("(chưa có)") or before.startswith("(trống)"):
                continue
            for ap in approved:
                parts = [p for p in (ap["head"], ap["tail"]) if p in before]
                if not parts:
                    continue
                ch = [k for k, v in variants(f).items() if not all(p in v for p in parts)]
                overlap.append({"card": cid, "field": i, "key": f["key"], "approved_id": ap["id"], "approved_key": ap["key"],
                                "changed_variants": ch, "approved_text": ap["text"][:300]})
    conflict = [o for o in overlap if o["changed_variants"]]
    wjson(a.out, {"reviews_used": len(done), "values_used": len(approved), "id_da_duyet": reuse, "trung_chu_da_duyet": overlap,
                  "sua_chu_da_duyet": conflict})
    print(json.dumps({"reviews_used": len(done), "values_used": len(approved), "id_da_duyet": len(reuse),
                      "id_da_duyet_doi_chu": sum(1 for r in reuse if r["field_changed"]), "trung_chu_da_duyet": len(overlap),
                      "sua_chu_da_duyet": len(conflict)}, ensure_ascii=False))


MUST_SOLO = {"seo_title", "meta", "h1", "title"}


def cmd_batch(a):
    items, _ = load_cards(a.cards)
    st = json.loads(Path(a.status).read_text(encoding="utf-8"))
    lots = json.loads(Path(a.lots).read_text(encoding="utf-8"))
    pending = {k for k, v in st.items() if v[2] == "pending"}
    seen, cards, report = {}, [], {"lots": {}, "dropped_not_pending": [], "missing": [], "duplicates": [], "solo_warn": []}
    for lot in lots:
        mem = []
        for m in lot["members"]:
            if m not in items:
                report["missing"].append(m)
            elif m not in pending:
                report["dropped_not_pending"].append(m)
            elif m in seen:
                report["duplicates"].append([m, seen[m], lot["id"]])
            else:
                seen[m] = lot["id"]
                mem.append(m)
                if any(f["key"] in MUST_SOLO for f in items[m]["fields"]):
                    report["solo_warn"].append(m)
        if len(mem) < 2:
            report["lots"][lot["id"]] = {"members": len(mem), "note": "dưới 2 thẻ: duyệt riêng, không dựng lô"}
            continue
        lines = "\n".join(f"- {m}: {items[m]['label']}" for m in mem)
        note = (f"{lot['rule']} Duyệt lô = duyệt {len(mem)} thẻ trong danh sách, theo phương án chọn sẵn của từng thẻ. "
                "Thẻ đã bấm riêng giữ quyết định riêng. Muốn loại thẻ nào khỏi lô: bấm E và xoá dòng của thẻ đó. "
                + (lot.get("note", "") + " " if lot.get("note") else "") + (f"Báo cáo: {a.report}." if a.report else "")).strip()

        def sample(cid, n):
            f = items[cid]["fields"][0]
            return {"key": f"mau{n}", "name": f"Mẫu {n}: {cid} · {f['name']}", "before": f.get("before", ""),
                    "proposed": f.get("proposed", ""), "max": 0, "editable": False}

        cards.append({"id": f"{a.prefix}{lot['id']}", "label": f"Lô {lot['id'].upper()} · {lot['title']}", "url": a.url,
                      "kind": "Duyệt theo lô", "lang": "vi", "note": note,
                      "fields": [{"key": "members", "name": f"Thẻ trong lô ({len(mem)})", "before": lines, "proposed": lines,
                                  "max": 0, "editable": True}, sample(mem[0], 1), sample(mem[len(mem) // 2], 2)]})
        report["lots"][lot["id"]] = {"members": len(mem), "ids": mem}
    solo = sorted(pending - set(seen))
    report.update({"pending": len(pending), "in_lots": len(seen), "solo": len(solo), "solo_ids": solo})
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    wjson(od / "lot_cards.json", {"items": cards})
    wjson(od / "batch_summary.json", report)
    print(json.dumps({"pending": len(pending), "in_lots": len(seen), "solo": len(solo),
                      "lots": {k: v["members"] for k, v in report["lots"].items()}, "solo_warn": report["solo_warn"],
                      "dropped": len(report["dropped_not_pending"]), "duplicates": len(report["duplicates"])}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("graph")
    g.add_argument("--sf", required=True, help="thư mục export Screaming Frog có internal_all.csv, all_inlinks.csv")
    g.add_argument("--home")
    g.add_argument("--money", help="TSV url<TAB>ma (trang tiền)")
    g.add_argument("--add", help="TSV source<TAB>target[<TAB>position]: link đề xuất để mô phỏng")
    g.add_argument("--rep-min", type=int, default=5, help="cặp anchor–đích lặp từ chừng này trang = link template")
    g.add_argument("--ctx-rows", help="rows.jsonl của site-vector-index: link ngữ cảnh lấy từ dòng level anchor")
    g.add_argument("--out", required=True)
    s = sub.add_parser("serp-overlap")
    s.add_argument("--serp", nargs="+", required=True)
    s.add_argument("--pairs", help="TSV a<TAB>b[<TAB>note]")
    s.add_argument("--top", type=int, default=10)
    s.add_argument("--out", required=True)
    q = sub.add_parser("qp")
    q.add_argument("--gsc", required=True)
    q.add_argument("--dims", default="query,page")
    q.add_argument("--templates", required=True, help="TSV id<TAB>template<TAB>target<TAB>regex")
    q.add_argument("--out", required=True)
    st = sub.add_parser("status")
    st.add_argument("--reviews", required=True)
    st.add_argument("--cards", nargs="+", required=True)
    st.add_argument("--until", help="mốc ISO UTC, ví dụ 2026-10-18T08:30")
    st.add_argument("--out", required=True)
    gu = sub.add_parser("guard")
    gu.add_argument("--reviews", required=True)
    gu.add_argument("--cards", required=True)
    gu.add_argument("--until")
    gu.add_argument("--out", required=True)
    b = sub.add_parser("batch")
    b.add_argument("--lots", required=True, help='JSON [{"id", "title", "rule", "members", "note"}]')
    b.add_argument("--cards", nargs="+", required=True)
    b.add_argument("--status", required=True)
    b.add_argument("--prefix", default="lo-")
    b.add_argument("--url", default="")
    b.add_argument("--report", default="")
    b.add_argument("--out", required=True)
    a = ap.parse_args()
    {"graph": cmd_graph, "serp-overlap": cmd_serp, "qp": cmd_qp, "status": cmd_status, "guard": cmd_guard,
     "batch": cmd_batch}[a.cmd](a)


if __name__ == "__main__":
    main()
