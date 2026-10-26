#!/usr/bin/env python3
"""Kiểm rule redirect trước và sau khi ghi: chuỗi, vòng, đích sai, nguồn trùng, URI cũ của Permalink Manager.
Script chỉ đọc file JSON và TSV đã xuất. Không gọi site, không ghi site.

Chạy: python3 chain_check.py --rules rules.json [--new moi.json] [--dump urls.json] [--status status.tsv]
        [--terms terms.json] [--uris uris.json] [--host <domain>] [--out findings.tsv]

Vào:
  --rules   danh sách rule hiện có: {id, sources:[{pattern, comparison}] hoặc from+comparison, to, code, status, to_key?}
            status: active | inactive | trashed. Rank Math xuất bảng rank_math_redirections ra dạng này.
  --new     rule định thêm (cùng dạng), file --rules-out của pick_target.py, hoặc plan.json của build_tax_plan.py (đọc khoá redirects).
            Kiểm cùng bộ rule đang bật, thêm cờ nếu nguồn trùng rule trong thùng rác.
  --dump    kết quả export_urls.php (mọi post_type, mọi post_status). Có thì kiểm trạng thái bài đích.
  --status  TSV cột path, code: mã HTTP crawl được. Có thì cờ đích trả 4xx hoặc 5xx.
  --terms   JSON danh sách đường dẫn trang chuyên mục, thẻ, archive. Có cả --dump và --terms thì cờ đích không tồn tại.
  --uris    JSON permalink-manager-uris (khoá "tax-45", "123" → uri). Rule có to_key phải khớp URI này.
  --host    domain của site. Đích ở domain khác bị bỏ qua, không tính chuỗi.
Ra: JSON tóm tắt ở stdout; --out ghi TSV từng phát hiện.
Mã thoát: 0 không có lỗi · 1 có phát hiện mức "loi" · 2 input sai.
Mức "loi": vong, chuoi, dich_410, dich_nhap, dich_thung_rac, dich_attachment, dich_loi_http, dich_khong_co, dich_trang_chu, dich_lech_uri, trung_nguon.
Mức "canh_bao": dich_danh_muc, nguon_dang_song, nguon_trung, nguon_co_rule_thung_rac, uri_thieu.
Rule 410 và 451 không có đích (Rank Math để url_to rỗng): không kiểm đích. Rule 301 dẫn vào nguồn của rule 410 là lỗi dich_410.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from urlpath import NHAP, Rule, first_match, load_dump, load_json, norm  # noqa: E402

GONE = {410, 451}
LOI = {"vong", "chuoi", "dich_410", "dich_nhap", "dich_thung_rac", "dich_attachment", "dich_loi_http", "dich_khong_co", "dich_trang_chu",
       "dich_lech_uri", "trung_nguon"}


def check(a):
    rules = [Rule(r, "co", i) for i, r in enumerate(load_json(a.rules))]
    raw_new = load_json(a.new) if a.new else []
    if isinstance(raw_new, dict):  # plan.json của build_tax_plan.py
        raw_new = raw_new.get("redirects", [])
    new = [Rule(r, "moi", i) for i, r in enumerate(raw_new)]
    active = sorted([r for r in rules if r.status == "active"], key=lambda r: (not r.id.isdigit(), int(r.id) if r.id.isdigit() else 0, r.id)) + new
    trashed = [r for r in rules if r.status == "trashed"]
    dump = load_dump(a.dump) if a.dump else None
    by_path = {}
    for p in dump or []:
        for k in p["keys"]:
            by_path.setdefault(k, []).append(p)
    terms = {norm(t) for t in load_json(a.terms)} if a.terms else None
    uris = load_json(a.uris) if a.uris else None
    status = {}
    if a.status:
        for ln in Path(a.status).read_text(encoding="utf-8-sig").splitlines()[1:]:
            c = ln.split("\t")
            if len(c) >= 2 and c[1].strip().isdigit():
                status[norm(c[0])] = int(c[1])
    out = []

    def add(r, ma, ct):
        out.append({"rule": r.id, "ma": ma, "muc": "loi" if ma in LOI else "canh_bao", "chi_tiet": ct})

    for r in active:
        t = r.target(None, a.host) if "$" not in r.to and r.code not in GONE else None
        # chuỗi và vòng
        if t:
            seen, cur, hops = [r.id], t, []
            while cur:
                nx, m = first_match(active, cur)
                if not nx:
                    break
                if nx.code in GONE:
                    add(r, "dich_410", f"{' → '.join(seen + [nx.id])}: đích {cur} đã trả {nx.code}. Đổi rule này thành {nx.code} hoặc trỏ sang bài giữ lại.")
                    hops = None
                    break
                if nx.id in seen:
                    add(r, "vong", " → ".join(seen + [nx.id]))
                    hops = None
                    break
                seen.append(nx.id)
                hops.append(nx.id)
                cur = nx.target(m, a.host)
            if hops:
                add(r, "chuoi", f"{' → '.join(seen)}; đích cuối {cur}. Trỏ thẳng về đích cuối.")
            if t == "/":
                add(r, "dich_trang_chu", "đích là trang chủ: 301 về bài cùng chủ đề, không có bài phù hợp thì 410")
            # bài không có path (nháp, thùng rác, attachment): khớp theo slug cuối của đích
            hit = by_path.get(t) or [p for p in dump or [] if not p["keys"] and p["slug_n"] and p["slug_n"] == t.rsplit("/", 1)[-1].strip("/")]
            if hit:
                live = [p for p in hit if p.get("type") != "attachment" and p.get("status") == "publish"]
                if not live:
                    p = hit[0]
                    if p.get("type") == "attachment":
                        add(r, "dich_attachment", f"{t} là attachment (post {p['id']}), không phải trang")
                    elif p.get("status") == "trash":
                        add(r, "dich_thung_rac", f"{t} là bài {p['id']} trong thùng rác")
                    elif p.get("status") in NHAP:
                        add(r, "dich_nhap", f"{t} là bài {p['id']} trạng thái {p['status']}")
            elif terms is not None and dump is not None and t not in terms:
                add(r, "dich_khong_co", f"{t} không có trong dump bài và không có trong danh sách chuyên mục")
            if terms and t in terms and t != "/":
                add(r, "dich_danh_muc", f"{t} là trang chuyên mục hoặc archive: đổi đích sang bài cùng chủ đề, không có bài phù hợp thì 410")
            if t in status and status[t] >= 400:
                add(r, "dich_loi_http", f"{t} trả {status[t]}")
        # nguồn đang sống
        for pat, cmp_ in r.sources:
            if cmp_ == "exact" and by_path:
                live = [p for p in by_path.get(norm(pat), []) if p.get("type") != "attachment" and p.get("status") == "publish"]
                if live:
                    add(r, "nguon_dang_song", f"{norm(pat)} là bài {live[0]['id']} đang publish")
        # URI Permalink Manager
        if r.to_key and uris is not None:
            want = uris.get(str(r.to_key))
            if want is None:
                add(r, "uri_thieu", f"Permalink Manager chưa có URI cho {r.to_key}")
            elif norm(want) != norm(r.to):
                add(r, "dich_lech_uri", f"đích {norm(r.to)} khác URI hiện tại {norm(want)} của {r.to_key}")
    # trùng nguồn
    seen = {}
    for r in active:
        for pat, cmp_ in r.sources:
            k = (norm(pat) if cmp_ != "regex" else pat, cmp_)
            if k in seen and seen[k] is not r:
                o = seen[k]
                if norm(o.to) != norm(r.to):
                    add(r, "trung_nguon", f"cùng nguồn {k[0]} với rule {o.id} nhưng khác đích ({norm(o.to)} và {norm(r.to)})")
                else:
                    add(r, "nguon_trung", f"cùng nguồn và đích với rule {o.id}")
            seen.setdefault(k, r)
    # rule mới trùng nguồn rule trong thùng rác
    for r in new:
        for pat, cmp_ in r.sources:
            for tr in trashed:
                if any((norm(p) if c != "regex" else p, c) == (norm(pat) if cmp_ != "regex" else pat, cmp_) for p, c in tr.sources):
                    add(r, "nguon_co_rule_thung_rac", f"rule {tr.id} trong thùng rác có cùng nguồn {norm(pat)}: kiểm tay trước khi thêm")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", required=True)
    for k in ("new", "dump", "status", "terms", "uris", "host", "out"):
        ap.add_argument("--" + k)
    a = ap.parse_args()
    for k in ("rules", "new", "dump", "status", "terms", "uris"):
        p = getattr(a, k)
        if p and not Path(p).is_file():
            print(f"lỗi: không có file --{k} {p}", file=sys.stderr)
            return 2
    try:
        out = check(a)
    except (ValueError, KeyError, TypeError) as e:
        print(f"lỗi input: {e!r}", file=sys.stderr)
        return 2
    if a.out:
        Path(a.out).write_text("rule\tma\tmuc\tchi_tiet\n" + "".join(f"{o['rule']}\t{o['ma']}\t{o['muc']}\t{o['chi_tiet']}\n" for o in out), encoding="utf-8")
    n_loi = sum(o["muc"] == "loi" for o in out)
    print(json.dumps({"phat_hien": len(out), "loi": n_loi, "canh_bao": len(out) - n_loi, "chi_tiet": out}, ensure_ascii=False, indent=1))
    return 1 if n_loi else 0


if __name__ == "__main__":
    sys.exit(main())
