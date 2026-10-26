#!/usr/bin/env python3
"""Kiểm kê bài viết: danh mục chính (Jev category-pick qua cổng), quét lỗi thời tất định, ứng viên trùng, đề xuất giữ/gộp/301/410/nháp.

Chạy bằng Python ≥ 3.9, chỉ cần thư viện chuẩn. Jev chạy riêng bằng tools/ai-assist/jev.py.
  jev-in    --posts posts.json --scope scope.tsv --site <domain> --out jev_in.jsonl
  category  --posts posts.json --jev-out jev_out.jsonl --out DIR [--registry instance.json --registry defaults.json --site <domain> --industry <ngành>]
            [--claude quyet.tsv] [--approved ids.txt] [--auto X --reject Y --human 0.6]
  scan      --pages pages.jsonl (--blocks blocks.jsonl | --rows rows.jsonl) --out DIR [--urls urls.txt] [--terms loi-thoi.tsv] [--year-max 2025]
  dup       --pairs pairs.jsonl --gsc gsc.(tsv|json) --out DIR [--min 0.9]
  decide    --inv inventory.tsv --out DIR

Cổng danh mục chính (ngưỡng lấy từ registry category-pick, thiếu thì 0.9/0.6):
  từ auto: tự ghi, trừ bài đang có danh mục chính hẹp còn gắn (Claude đọc) · reject–auto: Claude đọc tiêu đề + H2
  human–reject: Claude chọn thay Jev · dưới human: người duyệt quyết.
Mọi đề xuất bỏ bài (gộp, 301, 410) chờ người duyệt. Bài bỏ chuyển về nháp, không xoá.
Dữ liệu GSC chỉ xử lý local bằng script này. Không gửi GSC vào Jev.
"""
import argparse
import collections
import csv
import datetime
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
TERMS = HERE.parent / "references" / "loi-thoi.tsv"


def read_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def read_tsv(p):
    with open(p, encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f, delimiter="\t") if any((v or "").strip() for v in r.values())]


def wtsv(p, head, rows):
    Path(p).write_text("\n".join("\t".join(map(str, x)) for x in [head] + rows) + "\n", encoding="utf-8")


def nz(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip()


# ---------- jev-in ----------

def cmd_jev_in(a):
    d = json.loads(Path(a.posts).read_text(encoding="utf-8"))
    scope = {r["slug"]: r["pham_vi"] for r in read_tsv(a.scope)}
    missing = sorted({c["slug"] for c in d["cats"]} - set(scope))
    with open(a.out, "w", encoding="utf-8") as f:
        n = 0
        for p in d["posts"]:
            if a.lang and p.get("lang") not in (a.lang, "", None):
                continue
            state = {"site": a.site, "title": html.unescape(p["title"]), "url_path": urlsplit(p["url"]).path,
                     "description": (p.get("desc") or p.get("excerpt") or "")[:400], "headings": " | ".join(p.get("h2") or [])[:700]}
            f.write(json.dumps({"id": str(p["id"]), "state": state, "criteria": {"primary": scope}}, ensure_ascii=False) + "\n")
            n += 1
    print(json.dumps({"posts": n, "options": len(scope), "chuyen_muc_khong_co_pham_vi": missing}, ensure_ascii=False))


# ---------- category: danh mục chính ----------

def band(c):
    return "≥0.90" if c >= .9 else "0.75–0.89" if c >= .75 else "0.60–0.74" if c >= .6 else "<0.60"


def gate_from_registry(a, versions):
    """Ngưỡng cổng: registry khớp rubric category-pick + version + site, rồi tới tham số dòng lệnh.
    Entry site "*" chỉ khớp khi industry của entry là "*" hoặc bằng --industry, vì rubric viết theo ngành."""
    hit, src = None, "mặc định"
    for f in a.registry:
        for e in json.loads(Path(f).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == "category-pick" and str(e.get("version", "")).lstrip("v") in versions \
                    and (e.get("site") == a.site or (e.get("site") == "*" and e.get("industry", "*") in ("*", a.industry))) \
                    and (hit is None or e.get("site") == a.site):
                hit, src = e, f"{Path(f).name}: {e.get('site')} {e.get('version')}"
        if hit:
            break
    auto = a.auto if a.auto is not None else (hit or {}).get("threshold") or 0.9
    reject = a.reject if a.reject is not None else (hit or {}).get("reject_below") or auto
    human = min(a.human, reject)
    if not hit and a.auto is None:
        print(f"cảnh báo: chưa có registry category-pick cho site {a.site}, ngành {a.industry}, version {sorted(versions)}; "
              "dùng 0.9/0.6 và hiệu chuẩn bằng model-calibration trước khi ghi lô lớn", file=sys.stderr)
    return {"auto": auto, "reject": reject, "human": human, "nguon": src if hit else "mặc định hoặc dòng lệnh"}


def cmd_category(a):
    d = json.loads(Path(a.posts).read_text(encoding="utf-8"))
    slug_id = {c["slug"]: c["id"] for c in d["cats"]}
    id_slug = {c["id"]: c["slug"] for c in d["cats"]}
    jev, versions = {}, set()
    for r in read_jsonl(a.jev_out):
        ans = (r.get("answers") or {}).get("primary")
        if ans:
            jev[str(r["id"])] = (ans["choice"], float(ans.get("confidence") or 0))
            versions.add(str(r.get("task_version") or ""))
    claude = {}
    if a.claude:
        for r in read_tsv(a.claude):
            claude[str(r["id"])] = (r["quyet"], r.get("chuyen_muc") or "", [x for x in (r.get("go") or "").split(",") if x],
                                    r.get("ly_do") or "")
    approved = set(Path(a.approved).read_text().split()) if a.approved else set()
    g = gate_from_registry(a, versions)
    out, apply, gate, skipped, no_jev = [], [], [], 0, []
    for p in d["posts"]:
        if a.lang and p.get("lang") not in (a.lang, "", None):
            continue
        pid = str(p["id"])
        if pid not in jev:
            no_jev.append(pid)
            continue
        cats, cur_id = p["cats"], p.get("primary") or 0
        cur = id_slug.get(cur_id) if cur_id else None
        jv, conf = jev[pid]
        stale = bool(cur) and cur not in cats
        if cur and cur == jv and not stale:
            skipped += 1
            continue
        q, slug, rem, why = claude.get(pid, ("", "", [], ""))
        if q == "giu":
            final, kind = cur, "giữ"
        elif q == "chon":
            final, kind = slug, "chọn khác Jev"
        else:
            final, why, kind = jv, "theo Jev", "theo Jev"
        if final not in slug_id:
            sys.exit(f"bài {pid}: chuyên mục '{final}' không có trong taxonomy")
        reason = ("chưa có danh mục chính" if not cur else "danh mục chính không còn gắn" if stale
                  else "đang ở danh mục cha" if cur in a.parent.split(",") else "lệch chủ đề" if final != cur else "-")
        add = [final] if final not in cats else []
        title = html.unescape(p["title"])[:90]
        out.append([p["id"], title, ",".join(cats), cur or "", jv, f"{conf:.2f}", final, ",".join(add), ",".join(rem), kind, reason, why])
        doi_hep = bool(cur) and not stale and cur not in a.parent.split(",") and jv != cur
        if conf >= g["auto"] and not doi_hep:
            cong, status = "tự ghi", "ready"
        elif conf >= g["reject"]:  # gồm bài Jev ≥ auto muốn đổi chính hẹp: 18/10 người duyệt giữ 4/9 bài này
            cong, status = "Claude đọc", "ready" if q else "cho_claude"
        elif conf >= g["human"]:
            cong, status = "Claude chọn", "ready" if q else "cho_claude"
        else:
            cong, status = "người quyết", "ready" if pid in approved else "cho_nguoi_duyet"
        changes = final != cur or add or rem or stale
        gate.append([p["id"], f"{conf:.2f}", cong, status if changes else "không đổi", kind])
        if changes and status == "ready":
            apply.append({"id": p["id"], "primary": slug_id[final], "primary_slug": final,
                          "add": [slug_id[s] for s in add], "remove": [slug_id[s] for s in rem],
                          "expect_cats": sorted(slug_id[s] for s in cats), "expect_primary": cur_id})
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    hdr = ["id", "tiêu đề", "đang gắn", "chính cũ", "Jev", "tin cậy", "chính mới", "thêm", "gỡ", "cách chọn", "lý do đổi", "ghi chú"]
    wtsv(od / "decisions.tsv", hdr, out)
    wtsv(od / "gate.tsv", ["id", "tin_cay", "cong", "trang_thai", "cach_chon"], gate)
    (od / "apply.json").write_text(json.dumps(apply, ensure_ascii=False, indent=1), encoding="utf-8")
    bands = collections.defaultdict(lambda: [0, 0])
    for x in out:
        b = bands[band(float(x[5]))]
        b[0] += 1
        b[1] += x[6] == x[4]
    s = {"posts_xet": len(out), "da_dung": skipped, "khong_co_jev": no_jev, "ghi": len(apply),
         "them": sum(bool(x["add"]) for x in apply), "go": sum(bool(x["remove"]) for x in apply),
         "doi_chinh": sum(1 for x in apply if x["primary_slug"] != (id_slug.get(x["expect_primary"]) if x["expect_primary"] else None)),
         "ly_do": collections.Counter(x[10] for x in out if x[6] != x[3] or x[7] or x[8]),
         "khop_jev_theo_dai": {k: f"{bands[k][1]}/{bands[k][0]}" for k in ("≥0.90", "0.75–0.89", "0.60–0.74", "<0.60")},
         "cong": collections.Counter(f"{x[2]}: {x[3]}" for x in gate), "nguong": g}
    (od / "summary.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False))


# ---------- scan: dấu hiệu lỗi thời ----------

def cmd_scan(a):
    terms = [(r["regex"], r["ten"], r["ly_do"]) for r in read_tsv(a.terms)]
    ymax = a.year_max or datetime.date.today().year - 1
    year = re.compile(r"\b(" + "|".join(str(y) for y in range(2000, ymax + 1)) + r")\b")
    meta = {r["url"]: r for r in read_jsonl(a.pages)}
    body, heads = collections.defaultdict(list), collections.defaultdict(list)
    if a.blocks:  # blocks {url, region, tag, text}: chỉ vùng main, entry
        for b in read_jsonl(a.blocks):
            if b.get("region") in ("entry", "main") and (b.get("text") or "").strip():
                body[b["url"]].append(nz(b["text"]))
                if b.get("tag") in ("h2", "h3"):
                    heads[b["url"]].append(nz(b["text"]))
    else:  # rows.jsonl của site-vector-index (cần --keep-text): section là main content, heading ở meta
        for r in read_jsonl(a.rows):
            m = r.get("meta") or {}
            if r.get("level") == "section" and (r.get("text") or "").strip():
                body[r["url"]].append(nz(r["text"]))
                if m.get("heading"):
                    heads[r["url"]].append(nz(m["heading"]))
            elif r.get("level") == "passage" and m.get("h3") and nz(m["h3"]) not in heads[r["url"]]:
                heads[r["url"]].append(nz(m["h3"]))
    urls = [u.strip() for u in Path(a.urls).read_text().splitlines() if u.strip()] if a.urls else list(meta)
    rows, hits = [], []
    for u in urls:
        m = meta.get(u, {})
        txt = "\n".join(body[u])
        h1 = m.get("h1") if isinstance(m.get("h1"), str) else " | ".join(m.get("h1") or [])
        ty = sorted(set(year.findall(nz(m.get("title", "")) + " " + nz(h1))))
        hy = sorted({y for h in heads[u] for y in year.findall(h)})
        dep = []
        for rx, ten, why in terms:
            f = list(re.finditer(rx, txt, re.I))
            if f:
                k = f[0].start()
                dep.append(ten)
                hits.append((u, why, len(f), txt[max(0, k - 70): k + 90].replace("\n", " ")))
        rows.append((u, len(txt.split()), ",".join(ty), ",".join(hy), "; ".join(dep)))
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    wtsv(od / "scan_pages.tsv", ["url", "words", "nam_title_h1", "nam_heading", "loi_thoi"], rows)
    with open(od / "scan_hits.tsv", "w", encoding="utf-8") as f:
        f.write("url\tly_do\tso_lan\tdoan\n")
        for h in hits:
            f.write("\t".join(map(str, h)) + "\n")
    s = {"trang": len(rows), "nam_title_h1": sum(1 for r in rows if r[2]), "nam_heading": sum(1 for r in rows if r[3]),
         "luot_loi_thoi": len(hits), "trang_loi_thoi": len({h[0] for h in hits}), "year_max": ymax}
    print(json.dumps(s, ensure_ascii=False))


# ---------- dup: ứng viên trùng → truy vấn để kiểm SERP ----------

def read_gsc(path, dims):
    p = Path(path)
    if p.suffix == ".json":
        order = dims.split(",")
        for r in json.loads(p.read_text(encoding="utf-8"))["rows"]:
            k = dict(zip(order, r["keys"]))
            yield k["query"], k["page"], float(r["impressions"]), float(r["clicks"])
    else:
        for r in read_tsv(p):
            yield r["query"], r["page"], float(r["impressions"]), float(r["clicks"])


def path_of(u):
    return (re.sub(r"^https?://[^/]+", "", u or "") or "/").split("?")[0]


def fold(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def head_query(path, qs):
    """Query đại diện của trang: query khớp ≥60% tiếng của slug, nhiều hiển thị nhất; không có thì query nhiều hiển thị nhất."""
    if not qs:
        return ""
    slug = [t for t in path.rstrip("/").split("/")[-1].split("-") if t]
    best = None
    for q, imp in qs.most_common():
        if DOMAIN.search(q):  # query chứa tên miền khác: spam hoặc điều hướng
            continue
        toks = set(re.findall(r"\w+", fold(q)))
        if slug and sum(t in toks for t in slug) / len(slug) >= 0.6:
            best = q
            break
    return best or next((q for q, _ in qs.most_common() if not DOMAIN.search(q)), "")


DOMAIN = re.compile(r"\w\.(com|net|org|vn|io|info|xyz)\b")


def cmd_dup(a):
    pairs = [r for r in read_jsonl(a.pairs) if float(r["cos"]) >= a.min]
    q = collections.defaultdict(collections.Counter)
    clk = collections.Counter()
    for query, page, imp, ck in read_gsc(a.gsc, a.dims):
        if "#" in page:  # dòng jump link lặp hiển thị của URL gốc
            continue
        p = path_of(page)
        q[p][unicodedata.normalize("NFC", query).casefold().strip()] += imp
        clk[p] += ck
    rows, serp = [], []
    for r in pairs:
        pa, pb = path_of(r["url_a"]), path_of(r["url_b"])
        ta, tb = head_query(pa, q[pa]), head_query(pb, q[pb])
        shared = set(q[pa]) & set(q[pb])
        rows.append([r["url_a"], r["url_b"], f"{float(r['cos']):.4f}", ta, tb, len(shared),
                     int(sum(q[pa].values())), int(sum(q[pb].values())), int(clk[pa]), int(clk[pb])])
        if ta and tb and ta != tb:
            serp.append([ta, tb, f"{pa} ~ {pb}"])
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    wtsv(od / "dup_pairs.tsv", ["url_a", "url_b", "cos", "query_a", "query_b", "query_chung", "impr_a", "impr_b", "click_a", "click_b"], rows)
    wtsv(od / "serp_pairs.tsv", ["a", "b", "note"], serp)
    print(json.dumps({"cap": len(rows), "cap_can_kiem_serp": len(serp),
                      "cap_cung_query_dau": sum(1 for x in rows if x[3] and x[3] == x[4])}, ensure_ascii=False))


# ---------- decide: đề xuất giữ, làm mới, gộp, 301, 410 ----------

KEEP_TYPES = {"trang-tien", "bang-chung"}
REMOVE = {"410", "301", "gộp → 301"}


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def propose(r):
    """Trả (đề xuất, đích 301, lý do). Mọi đề xuất bỏ bài chờ người duyệt; bài bỏ luôn về nháp trước."""
    loai, clicks = r.get("loai", ""), num(r.get("clicks"))
    serp = num(r.get("serp_chung"), -1)
    if loai in KEEP_TYPES:
        return "giữ", "", "trang tiền hoặc trang bằng chứng: không xét bỏ"
    if r.get("ban_sao_cua"):
        return "410", "", "bản sao của " + r["ban_sao_cua"]
    if r.get("dup_of") and serp >= 6:
        return "gộp → 301", r["dup_of"], f"trùng ý định, SERP chung {int(serp)}/10"
    if r.get("dup_of") and serp >= 4:
        return "xem lại", "", f"cặp trùng vùng xám {int(serp)}/10: giữ cả hai, đo lại ngày 60"
    if r.get("dup_of") and serp >= 0:
        return "giữ", "", f"SERP tách ({int(serp)}/10): không gộp"
    if r.get("dup_of"):
        return "xem lại", "", "cặp trùng chưa kiểm SERP"
    if r.get("kenh_ngung") == "1":
        if loai == "tin":
            return "410", "", "tin thời sự của kênh đã ngừng"
        return "301", r.get("dich_goi_y", ""), "bài còn giá trị của kênh đã ngừng"
    if loai == "tin" and clicks == 0:
        return "410", "", "tin thời sự hết hạn, không có click trong kỳ GSC"
    if r.get("outdated") == "1":
        return "làm mới", "", "có thông tin lỗi thời"
    if r.get("effort") == "no":
        return ("làm mới", "", "có click nhưng chỉ có kiến thức chung") if clicks > 0 else \
               ("xem lại", "", "kiến thức chung, không có click: gộp, làm mới hoặc 301")
    return "giữ", "", "-"


def steps(de_xuat, r):
    if de_xuat == "410":
        cu = ("đổi đích sang " + r["ban_sao_cua"]) if r.get("ban_sao_cua", "").startswith("/") else "đổi thành 410"
        return f"chuyển nháp → rule 410 → gỡ thẻ <a> trỏ vào bài, giữ chữ → rule 301 cũ trỏ vào bài: {cu}"
    if de_xuat in ("301", "gộp → 301"):
        head = "chép phần riêng sang bài giữ → " if de_xuat == "gộp → 301" else ""
        return head + "chuyển nháp → rule 301 → link nội bộ đổi sang đích → rule 301 cũ trỏ vào bài: đổi sang đích"
    return ""


def cmd_decide(a):
    out = []
    for r in read_tsv(a.inv):
        de_xuat, dich, why = propose(r)
        if "301" in de_xuat and not dich:
            why += "; thiếu đích 301: Claude chọn bài cùng chủ đề, không có bài phù hợp thì 410"
        duyet = "chờ người duyệt" if de_xuat in REMOVE or de_xuat == "xem lại" else "-"
        out.append([r["url"], r.get("loai", ""), de_xuat, dich, duyet, why, steps(de_xuat, r)])
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    wtsv(od / "proposals.tsv", ["url", "loai", "de_xuat", "dich_301", "trang_thai", "ly_do", "buoc_ghi"], out)
    print(json.dumps({"bai": len(out), "de_xuat": collections.Counter(x[2] for x in out)}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jev-in")
    j.add_argument("--posts", required=True)
    j.add_argument("--scope", required=True, help="TSV slug<TAB>pham_vi (phạm vi từng chuyên mục)")
    j.add_argument("--site", required=True)
    j.add_argument("--lang", default="")
    j.add_argument("--out", required=True)
    c = sub.add_parser("category")
    c.add_argument("--posts", required=True)
    c.add_argument("--jev-out", required=True)
    c.add_argument("--claude", help="TSV id<TAB>quyet(giu|chon|theo_jev)<TAB>chuyen_muc<TAB>go<TAB>ly_do")
    c.add_argument("--registry", action="append", default=[],
                   help="model-calibration.json của instance, rồi calibration-defaults.json; lặp được, file đầu ưu tiên")
    c.add_argument("--site", default="*")
    c.add_argument("--industry", default="*", help="ngành của site, so với entry site \"*\" của registry")
    c.add_argument("--auto", type=float, help="ghi đè ngưỡng tự ghi của registry (mặc định 0.9)")
    c.add_argument("--reject", type=float, help="ghi đè reject_below của registry: dưới mức này Claude chọn thay Jev")
    c.add_argument("--human", type=float, default=0.6, help="dưới mức này người duyệt quyết")
    c.add_argument("--approved", help="file id bài người duyệt đã chốt (dải dưới --human)")
    c.add_argument("--parent", default="seo", help="slug chuyên mục cha rộng, cách nhau dấu phẩy")
    c.add_argument("--lang", default="")
    c.add_argument("--out", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--pages", required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--blocks", help="blocks jsonl {url, region, tag, text}")
    g.add_argument("--rows", help="rows.jsonl của site-vector-index, dựng với --keep-text")
    s.add_argument("--urls")
    s.add_argument("--terms", default=str(TERMS))
    s.add_argument("--year-max", type=int, default=0, help="năm cũ nhất còn tính là lỗi thời; mặc định năm trước năm nay")
    s.add_argument("--out", required=True)
    du = sub.add_parser("dup")
    du.add_argument("--pairs", required=True, help="output svi.py pairs --level page (jsonl)")
    du.add_argument("--gsc", required=True)
    du.add_argument("--dims", default="query,page")
    du.add_argument("--min", type=float, default=0.0, help="cosine tối thiểu; lấy từ registry passage-dup hoặc hiệu chuẩn")
    du.add_argument("--out", required=True)
    de = sub.add_parser("decide")
    de.add_argument("--inv", required=True)
    de.add_argument("--out", required=True)
    a = ap.parse_args()
    {"jev-in": cmd_jev_in, "category": cmd_category, "scan": cmd_scan, "dup": cmd_dup, "decide": cmd_decide}[a.cmd](a)


if __name__ == "__main__":
    main()
