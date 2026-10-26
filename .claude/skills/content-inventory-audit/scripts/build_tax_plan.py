#!/usr/bin/env python3
"""Đổi cây chuyên mục an toàn: chẩn đoán cây hiện tại, rồi dựng plan.json cho taxonomy_rollout.php.
Script chỉ đọc file đã xuất và ghi file local khi có --out. Không gọi site, không ghi DB.

  diagnose --cats cats.json --posts urls.json [--cpt-archives /a/ /b/] [--clicks clicks.json | --gsc gsc_page_180d.json] [--rules rules.json] [--spec spec.json] [--out ra.json]
  build    --spec spec.json --map map.tsv [--posts urls.json] [--out plan.json]

diagnose kiểm 5 dấu hiệu trước khi gán bài:
  1. truc_tron: các trục chia trộn nhau. Script chỉ liệt kê cây theo cha → con. Claude đọc, không tự kết luận.
  2. trung_archive_cpt: chuyên mục có đường dẫn trùng archive của post type.
  3. slug_va_cham: slug chuyên mục trùng slug bài hoặc trang đang publish.
  4. click_chuyen_muc: click GSC 180 ngày cộng theo danh mục chính.
  5. redirect_chiem_url: rule redirect đang bật khớp đường dẫn chuyên mục (hiện tại và theo --spec).
  ket_luan = "cay_sai" khi có dấu hiệu 2, 3 hoặc 5. Cây sai thì đề xuất cây trước, rồi mới gán bài.
Vào của diagnose:
  --cats    [{id, slug, parent (id, 0 = gốc), path, name?}]
  --posts   kết quả export_urls.php; thêm cats (danh sách slug) và primary (slug) cho bài cần tính click
  --cpt-archives  đường dẫn archive của post type, hoặc một file cpt.json (PART=cpt của export_tax_redirects.php)
  --clicks  {id bài: [click, impression]}
  --gsc    thay cho --clicks: output của `tools/gsc/gsc.sh query <property> 180 page` (JSON rows) hoặc TSV cột page, clicks, impressions.
            Script khớp page với path và pm_uri của bài; số page không khớp bài nào ghi ở gsc_khong_khop.
  --rules   danh sách rule như chain_check.py
Vào của build:
  --spec   {terms:[{key, term_id|null, name, slug, parent (key|null)}], pm_remove, noindex_terms, secondary:{id: key}, cpt_moves:{id: post_type},
            skip:[id], redirects:[{old, to_key, trang: "giu"|"ve_trang_1"}], extra_redirects:[{pattern, to, note, to_term?}], deactivate_redirects:[id]}
  --map    TSV cột id, primary (key chuyên mục chính mới)
  --posts  có thì đặt expect_cats theo chuyên mục hiện tại và cảnh báo bài chưa có trong map
build kiểm: cha tồn tại và không vòng, slug không trùng giữa anh em, mọi chuyên mục có uri (Permalink Manager tự tạo URI "category/…" cho
chuyên mục chưa có URI riêng), primary và secondary có trong cây, tối đa 1 secondary khác primary, đích redirect là chuyên mục của cây mới.
Không --out thì chỉ in tóm tắt (dry-run). Mã thoát: 0 xong · 1 plan sai (không ghi file) · 2 input sai.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from urlpath import Rule, first_match, load_dump, load_json, norm  # noqa: E402


def spec_paths(spec):
    by = {t["key"]: t for t in spec["terms"]}

    def uri(t, depth=0):
        if depth > 20:
            raise ValueError(f"vòng cha-con ở {t['key']}")
        return (uri(by[t["parent"]], depth + 1) + "/" if t.get("parent") else "") + t["slug"]

    return {t["key"]: "/" + uri(t) for t in spec["terms"]}


def gsc_clicks(path, posts):
    """GSC theo page → ({id bài: [click, impression]}, số page không khớp bài nào)."""
    by = {k: str(p["id"]) for p in posts for k in p["keys"]}
    p = Path(path)
    if p.suffix == ".json":
        rows = [(r["keys"][0], r.get("clicks", 0), r.get("impressions", 0)) for r in load_json(p).get("rows", [])]
    else:
        with open(p, encoding="utf-8-sig") as f:
            rows = [(r["page"], r.get("clicks") or 0, r.get("impressions") or 0) for r in csv.DictReader(f, delimiter="\t")]
    out, miss = {}, 0
    for page, c, i in rows:
        pid = by.get(norm(page))
        if not pid:
            miss += 1
            continue
        s = out.setdefault(pid, [0, 0])
        s[0] += int(float(c))
        s[1] += int(float(i))
    return out, miss


def diagnose(a):
    cats = load_json(a.cats)
    posts = load_dump(a.posts)
    spec = load_json(a.spec) if a.spec else None
    res = {"truc_tron": {"kieu": "doc_tay", "cay": {}}, "trung_archive_cpt": [], "slug_va_cham": [], "click_chuyen_muc": [],
           "redirect_chiem_url": []}
    slug_of = {str(c["id"]): c["slug"] for c in cats}
    for c in cats:
        if str(c.get("parent") or 0) != "0":
            res["truc_tron"]["cay"].setdefault(slug_of.get(str(c["parent"]), "?"), []).append(c["slug"])
    arch = a.cpt_archives or []
    if len(arch) == 1 and arch[0].endswith(".json") and Path(arch[0]).is_file():  # output PART=cpt của export_tax_redirects.php
        arch = load_json(arch[0])
    cpt = {norm(x) for x in arch}
    live = [p for p in posts if p.get("status") == "publish" and p.get("type") != "attachment"]
    rules = [Rule(r, "co", i) for i, r in enumerate(load_json(a.rules)) if r.get("status", "active") == "active"] if a.rules else []
    paths = {c["slug"]: norm(c.get("path") or "/" + c["slug"]) for c in cats}
    if spec:
        for k, p in spec_paths(spec).items():
            if p not in paths.values():
                paths["moi:" + k] = p
    for slug, p in paths.items():
        if p in cpt:
            res["trung_archive_cpt"].append({"chuyen_muc": slug, "path": p})
        for post in live:
            if post["slug_n"] == slug.removeprefix("moi:") or p in post["keys"]:
                res["slug_va_cham"].append({"chuyen_muc": slug, "bai": post["id"], "type": post.get("type"), "path": p})
                break
        r, _ = first_match(rules, p)
        if r:
            res["redirect_chiem_url"].append({"chuyen_muc": slug, "path": p, "rule": r.id, "den": norm(r.to)})
    if a.clicks or a.gsc:
        ck = load_json(a.clicks) if a.clicks else {}
        if a.gsc:
            ck, res["gsc_khong_khop"] = gsc_clicks(a.gsc, posts)
        agg = {}
        for p in posts:
            if p.get("type") == "post" and str(p["id"]) in ck:
                k = p.get("primary") or (p.get("cats") or ["(không có)"])[0]
                s = agg.setdefault(k, [0, 0, 0])
                s[0] += 1
                s[1] += ck[str(p["id"])][0]
                s[2] += ck[str(p["id"])][1]
        res["click_chuyen_muc"] = [{"chuyen_muc": k, "bai": v[0], "click": v[1], "impression": v[2]} for k, v in sorted(agg.items(), key=lambda x: -x[1][1])]
    res["ket_luan"] = "cay_sai" if res["trung_archive_cpt"] or res["slug_va_cham"] or res["redirect_chiem_url"] else "cay_chua_thay_dau_hieu_hong"
    return res


def build(a):
    spec = load_json(a.spec)
    err, warn = [], []
    terms = spec["terms"]
    keys = [t["key"] for t in terms]
    if len(set(keys)) != len(keys):
        err.append("key chuyên mục trùng nhau")
    by = {t["key"]: t for t in terms}
    for t in terms:
        if t.get("parent") and t["parent"] not in by:
            err.append(f"{t['key']}: cha {t['parent']} không có trong cây")
    sib = {}
    for t in terms:
        k = (t.get("parent"), t["slug"])
        if k in sib:
            err.append(f"slug {t['slug']} trùng giữa anh em ({sib[k]} và {t['key']})")
        sib[k] = t["key"]
    if err:
        return None, err, warn
    try:
        uri = {k: v.strip("/") for k, v in spec_paths(spec).items()}
    except ValueError as e:
        return None, [str(e)], warn
    out_terms = [dict(t, parent=t.get("parent"), term_id=t.get("term_id"), uri=uri[t["key"]]) for t in terms]
    rows = list(csv.DictReader(open(a.map, encoding="utf-8-sig"), delimiter="\t"))
    skip = set(spec.get("skip", []))
    cur = {}
    if a.posts:
        cur = {int(p["id"]): sorted(p.get("cats") or []) for p in load_dump(a.posts) if p.get("type") == "post"}
    sec = {int(k): v for k, v in spec.get("secondary", {}).items()}
    cpt = {int(k): v for k, v in spec.get("cpt_moves", {}).items()}
    posts, mapped = [], set()
    for r in rows:
        pid = int(r["id"])
        mapped.add(pid)
        if pid in skip:
            continue
        e = {"id": pid, "expect_cats": cur.get(pid, [])}
        if pid in cpt:
            e["cpt"] = cpt[pid]
        else:
            prim = r["primary"]
            if prim not in by:
                err.append(f"bài {pid}: primary {prim} không có trong cây")
                continue
            if pid in sec and sec[pid] not in by:
                err.append(f"bài {pid}: secondary {sec[pid]} không có trong cây")
                continue
            if pid in sec and sec[pid] == prim:
                warn.append(f"bài {pid}: secondary trùng primary, bỏ secondary")
                sec.pop(pid)
            e.update(cats=[prim] + ([sec[pid]] if pid in sec else []), primary=prim)
        posts.append(e)
    for pid in sorted(set(sec) | set(cpt)):
        if pid not in mapped:
            warn.append(f"bài {pid} có secondary hoặc cpt_moves nhưng không có trong map")
    for pid in sorted(set(cur) - mapped - skip):
        warn.append(f"bài {pid} chưa có trong map: giữ nguyên chuyên mục")
    reds = []
    for r in spec.get("redirects", []):
        if r["to_key"] not in uri:
            err.append(f"redirect {r['old']}: đích {r['to_key']} không có trong cây")
            continue
        sfx = "(/page/[0-9]+)?" if r.get("trang", "ve_trang_1") == "giu" else "(?:/page/[0-9]+)?"
        reds.append({"pattern": f"^(?:category/)?{r['old']}{sfx}$", "to": "/" + uri[r["to_key"]] + "/", "note": r["old"], "to_term": r["to_key"]})
    for r in spec.get("extra_redirects", []):
        if r.get("to_term") and r["to_term"] not in uri:
            err.append(f"redirect {r.get('note')}: to_term {r['to_term']} không có trong cây")
            continue
        reds.append(r)
    if err:
        return None, err, warn
    plan = {"terms": out_terms, "pm_remove": spec.get("pm_remove", []), "noindex_terms": spec.get("noindex_terms", []), "posts": posts,
            "redirects": reds, "deactivate_redirects": spec.get("deactivate_redirects", [])}
    return plan, err, warn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("diagnose")
    d.add_argument("--cats", required=True)
    d.add_argument("--posts", required=True)
    d.add_argument("--cpt-archives", nargs="*", default=[])
    for k in ("clicks", "gsc", "rules", "spec", "out"):
        d.add_argument("--" + k)
    b = sub.add_parser("build")
    b.add_argument("--spec", required=True)
    b.add_argument("--map", required=True)
    b.add_argument("--posts")
    b.add_argument("--out")
    a = ap.parse_args()
    for k in ("cats", "posts", "clicks", "gsc", "rules", "spec", "map"):
        p = getattr(a, k, None)
        if p and not Path(p).is_file():
            print(f"lỗi: không có file --{k} {p}", file=sys.stderr)
            return 2
    try:
        if a.cmd == "diagnose":
            res = diagnose(a)
            text = json.dumps(res, ensure_ascii=False, indent=1)
            if a.out:
                Path(a.out).write_text(text, encoding="utf-8")
            print(text)
            return 0
        plan, err, warn = build(a)
    except (ValueError, KeyError, TypeError) as e:
        print(f"lỗi input: {e!r}", file=sys.stderr)
        return 2
    for w in warn:
        print("cảnh báo:", w, file=sys.stderr)
    if err:
        for e in err:
            print("lỗi plan:", e, file=sys.stderr)
        return 1
    print(json.dumps({"chuyen_muc": len(plan["terms"]), "bai": len(plan["posts"]), "chuyen_post_type": sum("cpt" in p for p in plan["posts"]),
                      "redirect": len(plan["redirects"]), "canh_bao": len(warn), "ghi_file": bool(a.out)}, ensure_ascii=False))
    if a.out:
        Path(a.out).write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
