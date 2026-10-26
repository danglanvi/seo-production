#!/usr/bin/env python3
"""Test offline cho inventory.py: bài, chuyên mục, output Jev, crawl, GSC và registry đều là dữ liệu giả, không cần mạng hay model.
Chạy: python3 -I tests/test_inventory.py
"""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = HERE.parent / "scripts" / "inventory.py"
H = "https://mau.vn"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-I", str(INV), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def wtsv(p, head, rows):
    Path(p).write_text("\t".join(head) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows), encoding="utf-8")


def rtsv(p):
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


def jw(p, o):
    Path(p).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")


def jl(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


CATS = [{"id": 1, "slug": "seo", "name": "SEO", "parent": 0}, {"id": 2, "slug": "seo-onpage", "name": "Onpage", "parent": 1},
        {"id": 3, "slug": "seo-technical", "name": "Technical", "parent": 1}, {"id": 4, "slug": "tin-tuc", "name": "Tin", "parent": 0},
        {"id": 5, "slug": "chua-phan-loai", "name": "Khác", "parent": 0}]


def post(i, cats, primary, title="Bài &#8211; mẫu"):
    return {"id": i, "title": title, "url": f"{H}/bai-{i}/", "lang": "vi", "cats": cats, "primary": primary,
            "desc": "", "excerpt": "mô tả " * 100, "h2": ["H2 một", "H2 hai"]}


def jev(i, choice, conf, ver="2026-10-18.1"):
    return {"id": str(i), "answers": {"primary": {"choice": choice, "confidence": conf}}, "task_version": ver}


def test_jev_in(d):
    jw(d / "posts.json", {"cats": CATS, "posts": [post(1, ["seo"], 0)]})
    wtsv(d / "scope.tsv", ["slug", "pham_vi"], [["seo", "cha"], ["seo-onpage", "onpage"], ["seo-technical", "kỹ thuật"], ["tin-tuc", "tin"]])
    out = json.loads(run("jev-in", "--posts", d / "posts.json", "--scope", d / "scope.tsv", "--site", "mau.vn", "--out", d / "in.jsonl").stdout)
    assert out["chuyen_muc_khong_co_pham_vi"] == ["chua-phan-loai"], out
    r = json.loads((d / "in.jsonl").read_text().splitlines()[0])
    assert r["state"]["title"] == "Bài – mẫu" and r["state"]["url_path"] == "/bai-1/", r
    assert len(r["state"]["description"]) == 400 and r["state"]["headings"] == "H2 một | H2 hai"
    assert set(r["criteria"]["primary"]) == {"seo", "seo-onpage", "seo-technical", "tin-tuc"}


def test_category(d):
    posts = [post(1, ["seo-onpage"], 2),          # đã đúng: bỏ qua
             post(2, ["seo-onpage"], 0),          # chưa có chính, Jev 0.95: tự ghi
             post(3, ["seo-onpage", "seo"], 1),   # đang ở cha, Jev 0.92: tự ghi
             post(4, ["seo-technical"], 3),       # chính hẹp còn gắn, Jev 0.97 muốn đổi: Claude đọc
             post(5, ["seo-onpage"], 3),          # chính không còn gắn: Jev 0.8 → Claude đọc
             post(6, ["seo"], 0),                 # Jev 0.65 → Claude chọn
             post(7, ["seo"], 0),                 # Jev 0.4 → người quyết
             post(8, ["seo"], 0)]                 # không có output Jev
    jw(d / "posts.json", {"cats": CATS, "posts": posts})
    jl(d / "jev.jsonl", [jev(1, "seo-onpage", .99), jev(2, "seo-onpage", .95), jev(3, "seo-technical", .92), jev(4, "seo-onpage", .97),
                        jev(5, "seo-onpage", .8), jev(6, "seo-technical", .65), jev(7, "tin-tuc", .4)])
    jw(d / "reg.json", {"entries": [{"rubric": "category-pick", "version": "v2026-10-18.1", "site": "mau.vn", "threshold": 0.9, "reject_below": 0.75},
                                    {"rubric": "category-pick", "version": "v2026-10-18.1", "site": "*", "industry": "seo-agency", "threshold": 0.95, "reject_below": None}]})
    base = ["category", "--posts", d / "posts.json", "--jev-out", d / "jev.jsonl"]
    s = json.loads(run(*base, "--registry", d / "reg.json", "--site", "mau.vn", "--out", d / "c1").stdout)
    assert s["da_dung"] == 1 and s["khong_co_jev"] == ["8"] and s["nguong"]["auto"] == 0.9 and s["nguong"]["reject"] == 0.75, s
    g = {r["id"]: (r["cong"], r["trang_thai"]) for r in rtsv(d / "c1" / "gate.tsv")}
    assert g["2"] == ("tự ghi", "ready") and g["3"] == ("tự ghi", "ready"), g
    assert g["4"] == ("Claude đọc", "cho_claude") and g["5"] == ("Claude đọc", "cho_claude"), g
    assert g["6"] == ("Claude chọn", "cho_claude") and g["7"] == ("người quyết", "cho_nguoi_duyet"), g
    ap = {x["id"]: x for x in json.loads((d / "c1" / "apply.json").read_text())}
    assert set(ap) == {2, 3}, ap
    assert ap[2] == {"id": 2, "primary": 2, "primary_slug": "seo-onpage", "add": [], "remove": [], "expect_cats": [2], "expect_primary": 0}
    assert ap[3]["add"] == [3] and ap[3]["expect_primary"] == 1
    dec = {r["id"]: r for r in rtsv(d / "c1" / "decisions.tsv")}
    assert dec["3"]["lý do đổi"] == "đang ở danh mục cha" and dec["5"]["lý do đổi"] == "danh mục chính không còn gắn"
    assert dec["2"]["tiêu đề"] == "Bài – mẫu"
    # site khác: entry "*" khớp khi cùng ngành; không có reject → khoảng dưới auto là Claude chọn
    s = json.loads(run(*base, "--registry", d / "reg.json", "--site", "khac.vn", "--industry", "seo-agency", "--out", d / "c2").stdout)
    assert s["nguong"]["auto"] == 0.95 and s["nguong"]["reject"] == 0.95, s
    p = run(*base, "--registry", d / "reg.json", "--site", "khac.vn", "--industry", "noi-that", "--out", d / "c2b")
    assert "chưa có registry" in p.stderr and json.loads(p.stdout)["nguong"]["auto"] == 0.9
    # version Jev khác registry: cảnh báo, dùng mặc định
    jl(d / "jev2.jsonl", [jev(2, "seo-onpage", .95, "2026-11-01.1")])
    p = run("category", "--posts", d / "posts.json", "--jev-out", d / "jev2.jsonl", "--registry", d / "reg.json", "--site", "mau.vn", "--out", d / "c3")
    assert "chưa có registry" in p.stderr and json.loads(p.stdout)["nguong"]["auto"] == 0.9
    # quyết định của Claude và người duyệt
    wtsv(d / "quyet.tsv", ["id", "quyet", "chuyen_muc", "go", "ly_do"],
         [["4", "giu", "", "", "chính hẹp đúng chủ đề"], ["5", "theo_jev", "", "", ""], ["6", "chon", "seo-onpage", "seo", "bài onpage"],
          ["7", "chon", "seo-technical", "", "người duyệt chọn"]])
    (d / "ok.txt").write_text("7\n")
    s = json.loads(run(*base, "--registry", d / "reg.json", "--site", "mau.vn", "--claude", d / "quyet.tsv", "--approved", d / "ok.txt",
                       "--out", d / "c4").stdout)
    ap = {x["id"]: x for x in json.loads((d / "c4" / "apply.json").read_text())}
    assert set(ap) == {2, 3, 5, 6, 7}, ap  # 4 giữ chính cũ, không đổi gì
    assert ap[6]["primary_slug"] == "seo-onpage" and ap[6]["add"] == [2] and ap[6]["remove"] == [1]
    assert ap[7]["primary_slug"] == "seo-technical"
    g = {r["id"]: r["trang_thai"] for r in rtsv(d / "c4" / "gate.tsv")}
    assert g["4"] == "không đổi", g
    # chuyên mục không có trong taxonomy: dừng
    wtsv(d / "sai.tsv", ["id", "quyet", "chuyen_muc", "go", "ly_do"], [["6", "chon", "khong-co", "", ""]])
    run(*base, "--claude", d / "sai.tsv", "--out", d / "c5", ok=False)


def test_scan(d):
    jl(d / "pages.jsonl", [{"url": f"{H}/a/", "title": "Hướng dẫn SEO 2023", "h1": ["SEO"]}, {"url": f"{H}/b/", "title": "B"}])
    jl(d / "blocks.jsonl", [
        {"url": f"{H}/a/", "region": "entry", "tag": "h2", "text": "Cập nhật 2024"},
        {"url": f"{H}/a/", "region": "entry", "tag": "p", "text": "Mở Universal Analytics và Data Studio. Dùng Universal Analytics."},
        {"url": f"{H}/a/", "region": "footer", "tag": "p", "text": "Google+ ở footer không tính"},
        {"url": f"{H}/b/", "region": "main", "tag": "h3", "text": "Năm 2026 và FIDO"}])
    s = json.loads(run("scan", "--pages", d / "pages.jsonl", "--blocks", d / "blocks.jsonl", "--year-max", "2025", "--out", d / "s").stdout)
    assert s == {"trang": 2, "nam_title_h1": 1, "nam_heading": 1, "luot_loi_thoi": 2, "trang_loi_thoi": 1, "year_max": 2025}, s
    hits = rtsv(d / "s" / "scan_hits.tsv")
    assert [h["so_lan"] for h in hits] == ["2", "1"] and hits[0]["ly_do"].startswith("Universal Analytics"), hits
    pages = {r["url"]: r for r in rtsv(d / "s" / "scan_pages.tsv")}
    assert pages[f"{H}/a/"]["nam_title_h1"] == "2023" and pages[f"{H}/a/"]["loi_thoi"] == "Universal Analytics; Data Studio"
    assert pages[f"{H}/b/"]["nam_heading"] == "" and pages[f"{H}/b/"]["loi_thoi"] == ""  # 2026 > year-max, FIDO không phải FID
    (d / "urls.txt").write_text(f"{H}/b/\n")
    s = json.loads(run("scan", "--pages", d / "pages.jsonl", "--blocks", d / "blocks.jsonl", "--urls", d / "urls.txt", "--out", d / "s2").stdout)
    assert s["trang"] == 1


def test_dup(d):
    jl(d / "pairs.jsonl", [{"url_a": f"{H}/meta-title-la-gi/", "url_b": f"{H}/seo-title-la-gi/", "cos": 0.97},
                           {"url_a": f"{H}/lap-ke-hoach-seo/", "url_b": f"{H}/chien-luoc-seo/", "cos": 0.96},
                           {"url_a": f"{H}/x/", "url_b": f"{H}/y/", "cos": 0.5}])
    wtsv(d / "gsc.tsv", ["page", "query", "clicks", "impressions"], [
        ["/meta-title-la-gi/", "meta title", 3, 500], ["/meta-title-la-gi/", "Meta Title là gì", 1, 90],
        ["/meta-title-la-gi/#ftoc-1", "meta title", 0, 9999],
        ["/seo-title-la-gi/", "seo title là gì", 2, 80],
        ["/lap-ke-hoach-seo/", "hướng dẫn làm seo web", 0, 900], ["/lap-ke-hoach-seo/", "kế hoạch seo", 1, 50],
        ["/chien-luoc-seo/", "spam.com", 0, 800], ["/chien-luoc-seo/", "chiến lược seo", 4, 300], ["/chien-luoc-seo/", "kế hoạch seo", 0, 10]])
    s = json.loads(run("dup", "--pairs", d / "pairs.jsonl", "--gsc", d / "gsc.tsv", "--min", "0.9", "--out", d / "u").stdout)
    assert s == {"cap": 2, "cap_can_kiem_serp": 2, "cap_cung_query_dau": 0}, s
    rows = rtsv(d / "u" / "dup_pairs.tsv")
    assert (rows[0]["query_a"], rows[0]["query_b"]) == ("meta title là gì", "seo title là gì"), rows[0]  # khớp slug, gộp hoa thường
    assert rows[0]["impr_a"] == "590", rows[0]  # bỏ dòng #ftoc
    assert (rows[1]["query_a"], rows[1]["query_b"], rows[1]["query_chung"]) == ("kế hoạch seo", "chiến lược seo", "1"), rows[1]
    serp = rtsv(d / "u" / "serp_pairs.tsv")
    assert serp[0]["a"] == "meta title là gì" and serp[0]["note"] == "/meta-title-la-gi/ ~ /seo-title-la-gi/"


def test_decide(d):
    head = ["url", "loai", "clicks", "ban_sao_cua", "dup_of", "serp_chung", "kenh_ngung", "dich_goi_y", "outdated", "effort"]
    rows = [["/tien/", "trang-tien", 0, "/x/", "", "", "1", "", "1", "no"],
            ["/copy/", "huong-dan", 9, "/goc/", "", "", "", "", "", ""],
            ["/copy-site-khac/", "huong-dan", 0, "https://khac.vn/a/", "", "", "", "", "", ""],
            ["/gop/", "huong-dan", 5, "", "/giu/", "7", "", "", "", ""],
            ["/xam/", "huong-dan", 5, "", "/giu/", "5", "", "", "", ""],
            ["/tach/", "huong-dan", 5, "", "/giu/", "2", "", "", "", ""],
            ["/chua-serp/", "huong-dan", 5, "", "/giu/", "", "", "", "", ""],
            ["/nl-tin/", "tin", 3, "", "", "", "1", "", "", ""],
            ["/nl-hd/", "huong-dan", 0, "", "", "", "1", "/chuyen-muc/", "", ""],
            ["/nl-qc/", "quang-cao", 0, "", "", "", "1", "", "", ""],
            ["/tin-cu/", "tin", 0, "", "", "", "", "", "", ""],
            ["/tin-con-click/", "tin", 2, "", "", "", "", "", "", ""],
            ["/cu/", "huong-dan", 0, "", "", "", "", "", "1", ""],
            ["/mong-click/", "huong-dan", 4, "", "", "", "", "", "", "no"],
            ["/mong/", "huong-dan", 0, "", "", "", "", "", "", "no"],
            ["/tot/", "huong-dan", 4, "", "", "", "", "", "", "yes"]]
    wtsv(d / "inv.tsv", head, rows)
    run("decide", "--inv", d / "inv.tsv", "--out", d / "dd")
    out = {r["url"]: r for r in rtsv(d / "dd" / "proposals.tsv")}
    want = {"/tien/": "giữ", "/copy/": "410", "/copy-site-khac/": "410", "/gop/": "gộp → 301", "/xam/": "xem lại", "/tach/": "giữ",
            "/chua-serp/": "xem lại", "/nl-tin/": "410", "/nl-hd/": "301", "/nl-qc/": "301", "/tin-cu/": "410",
            "/tin-con-click/": "giữ", "/cu/": "làm mới", "/mong-click/": "làm mới", "/mong/": "xem lại", "/tot/": "giữ"}
    assert {u: r["de_xuat"] for u, r in out.items()} == want, {u: r["de_xuat"] for u, r in out.items()}
    assert all(out[u]["trang_thai"] == "chờ người duyệt" for u in out if want[u] in ("410", "301", "gộp → 301", "xem lại"))
    assert out["/gop/"]["dich_301"] == "/giu/" and out["/gop/"]["buoc_ghi"].startswith("chép phần riêng")
    assert "đổi đích sang /goc/" in out["/copy/"]["buoc_ghi"] and "đổi thành 410" in out["/copy-site-khac/"]["buoc_ghi"]
    assert all(out[u]["buoc_ghi"].startswith("chuyển nháp") for u in ("/copy/", "/nl-tin/", "/nl-hd/", "/tin-cu/"))
    assert "thiếu đích 301" in out["/nl-qc/"]["ly_do"] and out["/nl-hd/"]["dich_301"] == "/chuyen-muc/"


def main():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        test_jev_in(d)
        test_category(d)
        test_scan(d)
        test_dup(d)
        test_decide(d)
    print("OK test_inventory")


if __name__ == "__main__":
    main()
