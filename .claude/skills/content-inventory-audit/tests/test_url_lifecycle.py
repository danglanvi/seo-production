#!/usr/bin/env python3
"""Test offline cho chain_check.py, pick_target.py, build_tax_plan.py, wayback_cdx.py (chỉ --offline)
và 3 script PHP (taxonomy_rollout.php, export_urls.php, export_tax_redirects.php).
Mọi dữ liệu là fixture giả (site mau.vn), không cần mạng, SSH hay WordPress thật. PHP chạy bằng stub WordPress nếu máy có `php`.
Chạy: python3 -I tests/test_url_lifecycle.py
Ca hỏng thật đã gặp (nhãn site ghi ở từng test):
  - [gtvseo 17/10] rule 301 cũ trỏ tới trang đang ở nháp, qua một rule trung gian (chuỗi 2 bước).
  - [theaigrowth 17/10] script chuyên mục tạo 301 sai vì Permalink Manager còn giữ URI cũ của chuyên mục.
  - [gtvseo 18/10] cây chuyên mục trùng archive của post type, rule Rank Math chiếm URL chuyên mục mới.
  - Slug emoji: WordPress lưu %f0%9f..., rule và crawl dùng ký tự thật.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE.parent / "scripts"


def run(script, *args, ok=0):
    p = subprocess.run([sys.executable, "-I", str(S / script), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == ok, (script, args, p.returncode, p.stdout[-800:], p.stderr[-800:])
    return p


def jw(p, o):
    Path(p).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")


def post(i, typ, st, name, path=None, pm=None, old=None, **kw):
    return dict(id=i, type=typ, status=st, name=name, parent=0, path=path, pm_uri=pm, old_slugs=old or [], **kw)


DUMP = [
    post(1, "post", "publish", "bai-song", "/bai-song/"),
    post(2, "post", "draft", "seo-fundamental-trial", None, "/seo-fundamental-trial/"),
    post(3, "post", "publish", "bai-moi", "/bai-moi/", None, ["bai-cu"]),
    post(4, "attachment", "inherit", "anh-trung"),
    post(5, "page", "trash", "trang-xoa"),
    post(6, "post", "publish", "%f0%9f%94%a5-khuyen-mai", "/%f0%9f%94%a5-khuyen-mai/"),
]


def rule(i, src, to, cmp_="exact", status="active", **kw):
    return dict(id=i, sources=[{"pattern": src, "comparison": cmp_}], to=to, code=301, status=status, **kw)


def findings(p):
    return {(f["rule"], f["ma"]) for f in json.loads(p.stdout)["chi_tiet"]}


def test_chain_check(d):
    jw(d / "dump.json", DUMP)
    # [gtvseo 17/10] chuỗi tới trang nháp: 14 → 59 → bài đang ở nháp. Phải bắt cả chuỗi lẫn đích nháp.
    jw(d / "r1.json", [rule(14, "/seo-fundamental-old/", "/seo-fundamental-trial-1/"), rule(59, "/seo-fundamental-trial-1/", "/seo-fundamental-trial/")])
    p = run("chain_check.py", "--rules", d / "r1.json", "--dump", d / "dump.json", ok=1)
    assert findings(p) == {("14", "chuoi"), ("59", "dich_nhap")}, p.stdout
    # slug emoji: rule nguồn viết ký tự thật, đích viết %F0%9F...: chỉ khớp sau khi giải mã
    jw(d / "r2.json", [rule(20, "/🔥-khuyen-mai/", "/bai-moi/"), rule(21, "/x/", "/%F0%9F%94%A5-khuyen-mai/")])
    f = findings(run("chain_check.py", "--rules", d / "r2.json", "--dump", d / "dump.json", ok=1))
    assert ("21", "chuoi") in f and ("20", "nguon_dang_song") in f, f
    # [theaigrowth 17/10] Permalink Manager còn URI cũ: 301 trỏ /seo/tu-khoa/ nhưng chuyên mục đang ở category/seo/tu-khoa
    jw(d / "r3.json", [rule(30, "/seo/keyword-research/", "/seo/tu-khoa/", to_key="tax-45"), rule(31, "/seo/offpage-cu/", "/seo/offpage/", to_key="tax-38")])
    jw(d / "uris.json", {"tax-45": "category/seo/tu-khoa", "tax-38": "seo/offpage"})
    f = findings(run("chain_check.py", "--rules", d / "r3.json", "--uris", d / "uris.json", ok=1))
    assert f == {("30", "dich_lech_uri")}, f
    # vòng, trùng nguồn khác đích, đích trang chủ, đích chuyên mục
    jw(d / "r4.json", [rule(40, "/a/", "/b/"), rule(41, "/b/", "/a/"), rule(50, "/dup/", "/x/"), rule(51, "/dup/", "/y/"), rule(52, "/c/", "/"),
                       rule(53, "/d/", "/danh-muc/")])
    jw(d / "terms.json", ["/danh-muc/", "/seo/"])
    p = run("chain_check.py", "--rules", d / "r4.json", "--terms", d / "terms.json", "--out", d / "f.tsv", ok=1)
    f = findings(p)
    assert {("40", "vong"), ("41", "vong"), ("51", "trung_nguon"), ("52", "dich_trang_chu"), ("53", "dich_danh_muc")} <= f, f
    assert (d / "f.tsv").read_text().startswith("rule\tma\tmuc\tchi_tiet\n")
    # rule mới trùng nguồn rule trong thùng rác chỉ là cảnh báo → mã thoát 0
    jw(d / "r5.json", [rule(60, "/trash-src/", "/bai-moi/", status="trashed"), rule(61, "/ok/", "/bai-moi/")])
    jw(d / "new5.json", [rule("moi-a", "/trash-src/", "/bai-song/")])
    p = run("chain_check.py", "--rules", d / "r5.json", "--new", d / "new5.json", "--dump", d / "dump.json")
    assert findings(p) == {("moi-a", "nguon_co_rule_thung_rac")}, p.stdout
    # đích ở domain khác không tính chuỗi; rule sạch thoát 0
    jw(d / "r6.json", [rule(70, "/a/", "https://khac.example/b/"), rule(71, "/b/", "/bai-song/")])
    p = run("chain_check.py", "--rules", d / "r6.json", "--host", "mau.vn", "--dump", d / "dump.json")
    assert json.loads(p.stdout)["phat_hien"] == 0, p.stdout
    # đích 410 theo crawl và bài trong thùng rác, attachment
    (d / "st.tsv").write_text("path\tcode\n/gone/\t410\n")
    jw(d / "r7.json", [rule(80, "/q/", "/gone/"), rule(81, "/r/", "/trang-xoa/"), rule(82, "/s/", "/anh-trung/")])
    f = findings(run("chain_check.py", "--rules", d / "r7.json", "--status", d / "st.tsv", "--dump", d / "dump.json", ok=1))
    assert f == {("80", "dich_loi_http"), ("81", "dich_thung_rac"), ("82", "dich_attachment")}, f
    p = run("chain_check.py", "--rules", d / "khong-co.json", ok=2)
    assert "không có file" in p.stderr
    (d / "hong.json").write_text("{không phải json")
    run("chain_check.py", "--rules", d / "hong.json", ok=2)
    # Rank Math lưu rule 410 với url_to rỗng: không được báo đích trang chủ. Rule 301 dẫn vào nguồn rule 410 là lỗi dich_410.
    r8 = [dict(rule(90, "/tin-cu/", ""), code=410), dict(rule(91, "/tin-cu-2/", "/tin-cu/")), dict(rule(92, "/tin-cu-3/", ""), code=451)]
    jw(d / "r8.json", r8)
    f = findings(run("chain_check.py", "--rules", d / "r8.json", ok=1))
    assert f == {("91", "dich_410")}, f


def test_pick_target(d):
    jw(d / "dump.json", DUMP)
    jw(d / "terms.json", ["/danh-muc/"])
    jw(d / "wb.json", {"/khong-co/": [["timestamp", "statuscode"], ["20210423174117", "200"], ["20220125171857", "301"]],
                       "/chi-301/": [["timestamp", "statuscode"], ["20210423174117", "301"]]})
    head = "url\tclicks\tdich_goi_y\ttam_dong\n"
    rows = [
        ["/seo-fundamental-trial/", 17, "", ""],            # [gtvseo 17/10] bài còn ở nháp: khôi phục trước khi 301
        ["/bai-cu/", 0, "", ""],                            # slug cũ
        ["/anh-trung/", 0, "", ""],                         # chỉ có attachment trùng slug
        ["/trang-xoa/", 0, "", ""],                         # thùng rác
        ["/%F0%9F%94%A5-khuyen-mai/", 0, "", ""],           # emoji: đang sống
        ["/khong-co/", 0, "", ""],                          # Wayback 200
        ["/chi-301/", 0, "", ""],                           # Wayback chỉ có 301: không đủ căn cứ nội dung
        ["/khong-co-2/", 5, "", ""],                        # có click
        ["/moi-xoa/", 0, "/danh-muc/", ""],                 # đích là chuyên mục: lỗi (chốt 26/10)
        ["/bad-home/", 0, "/", ""],                         # đích trang chủ
        ["/bad-draft/", 0, "/seo-fundamental-trial/", ""],  # đích là bài nháp
        ["/bad-none/", 0, "/khong-ton-tai/", ""],           # đích không có trong DB
        ["/tam/", 0, "/bai-moi/", "1"],                     # đóng tạm
    ]
    (d / "urls.tsv").write_text(head + "".join("\t".join(map(str, r)) + "\n" for r in rows), encoding="utf-8")
    base = ["--urls", d / "urls.tsv", "--dump", d / "dump.json", "--wayback", d / "wb.json", "--terms", d / "terms.json"]
    p = run("pick_target.py", *base, "--out", d / "ra.tsv")
    got = {r.split("\t")[0]: r.split("\t") for r in (d / "ra.tsv").read_text().splitlines()[1:]}
    ma = {u.lower(): c[1] for u, c in got.items()}
    want = {"/seo-fundamental-trial/": "khoi_phuc", "/bai-cu/": "301", "/anh-trung/": "410_de_xuat", "/trang-xoa/": "khoi_phuc",
            "/%f0%9f%94%a5-khuyen-mai/": "giu", "/khong-co/": "doc_wayback", "/chi-301/": "410_de_xuat", "/khong-co-2/": "hoi",
            "/moi-xoa/": "loi", "/bad-home/": "loi", "/bad-draft/": "loi", "/bad-none/": "loi", "/tam/": "302"}
    assert ma == want, ma
    assert got["/bai-cu/"][2] == "/bai-moi/" and got["/bai-cu/"][3] == "old_slug"
    assert "attachment_trung_slug" in got["/anh-trung/"][4] and "chuyên mục" in "\t".join(got["/moi-xoa/"])
    run("pick_target.py", *base, "--strict", ok=1)
    # không --out: in ra stdout, không tạo file
    p = run("pick_target.py", *base)
    assert p.stdout.startswith("url\tma\tdich") and not (d / "stdout.tsv").exists()
    run("pick_target.py", "--urls", d / "khong-co.tsv", "--dump", d / "dump.json", ok=2)
    # bo=1: chỉ URL trong danh sách bỏ đã duyệt thành 410, URL khác giữ 404 (410_de_xuat). --rules-out ra rule cho chain_check --new.
    (d / "u2.tsv").write_text("url\tclicks\tdich_goi_y\ttam_dong\tbo\n/khong-co-3/\t0\t\t\t1\n/khong-co-4/\t0\t\t\t\n/bai-cu/\t0\t\t\t\n"
                              "/tam/\t0\t/bai-moi/\t1\t\n", encoding="utf-8")
    p = run("pick_target.py", "--urls", d / "u2.tsv", "--dump", d / "dump.json", "--rules-out", d / "moi.json")
    ma = {ln.split("\t")[0]: ln.split("\t")[1] for ln in p.stdout.splitlines()[1:]}
    assert ma == {"/khong-co-3/": "410", "/khong-co-4/": "410_de_xuat", "/bai-cu/": "301", "/tam/": "302"}, ma
    moi = json.loads((d / "moi.json").read_text())
    assert [(r["from"], r["to"], r["code"]) for r in moi] == [("/khong-co-3/", "", 410), ("/bai-cu/", "/bai-moi/", 301), ("/tam/", "/bai-moi/", 302)], moi
    jw(d / "rules0.json", [])
    assert findings(run("chain_check.py", "--rules", d / "rules0.json", "--new", d / "moi.json", "--dump", d / "dump.json")) == set()


def test_build_tax_plan(d):
    spec = {
        "terms": [{"key": "seo", "term_id": 4, "name": "SEO", "slug": "seo", "parent": None},
                  {"key": "tu-khoa", "term_id": 45, "name": "Nghiên cứu từ khóa", "slug": "tu-khoa", "parent": "seo"},
                  {"key": "thuat-toan", "term_id": None, "name": "Thuật toán", "slug": "thuat-toan", "parent": "seo"},
                  {"key": "website", "term_id": 13, "name": "Website", "slug": "website", "parent": None}],
        "pm_remove": ["tax-130"], "noindex_terms": [39], "secondary": {"100": "seo"}, "cpt_moves": {"104": "inbound-marketing"}, "skip": [103],
        "redirects": [{"old": "seo/keyword-research", "to_key": "tu-khoa"}, {"old": "seo/cu", "to_key": "seo", "trang": "giu"}],
        "deactivate_redirects": [370]}
    jw(d / "spec.json", spec)
    (d / "map.tsv").write_text("id\tprimary\n100\ttu-khoa\n101\twebsite\n102\tthuat-toan\n103\tseo\n104\tseo\n", encoding="utf-8")
    jw(d / "urls.json", [dict(post(i, "post", "publish", f"b{i}", f"/b{i}/"), cats=["cu"]) for i in (100, 101, 102, 103, 104, 105)])
    base = ["build", "--spec", d / "spec.json", "--map", d / "map.tsv", "--posts", d / "urls.json"]
    p = run("build_tax_plan.py", *base)  # dry-run: không ghi file
    assert json.loads(p.stdout)["ghi_file"] is False and "bài 105 chưa có trong map" in p.stderr, (p.stdout, p.stderr)
    run("build_tax_plan.py", *base, "--out", d / "plan.json")
    plan = json.loads((d / "plan.json").read_text())
    # [theaigrowth 17/10] mọi chuyên mục phải có uri riêng, kể cả chuyên mục mới
    assert {t["key"]: t["uri"] for t in plan["terms"]} == {"seo": "seo", "tu-khoa": "seo/tu-khoa", "thuat-toan": "seo/thuat-toan", "website": "website"}
    ids = {p["id"]: p for p in plan["posts"]}
    assert 103 not in ids and ids[104] == {"id": 104, "expect_cats": ["cu"], "cpt": "inbound-marketing"}
    assert ids[100]["cats"] == ["tu-khoa", "seo"] and ids[100]["primary"] == "tu-khoa" and ids[101]["cats"] == ["website"]
    r = {x["note"]: x for x in plan["redirects"]}
    assert r["seo/keyword-research"]["to"] == "/seo/tu-khoa/" and r["seo/keyword-research"]["to_term"] == "tu-khoa"
    assert r["seo/keyword-research"]["pattern"].endswith("(?:/page/[0-9]+)?$") and r["seo/cu"]["pattern"].endswith("(/page/[0-9]+)?$")
    assert plan["deactivate_redirects"] == [370] and plan["pm_remove"] == ["tax-130"]
    # [gtvseo 18/10] kiểm redirect của plan trước khi ghi: rule cũ đang chiếm URL chuyên mục mới tạo chuỗi
    jw(d / "r_ex.json", [rule(99, "/seo/tu-khoa/", "/seo/")])
    f = findings(run("chain_check.py", "--rules", d / "r_ex.json", "--new", d / "plan.json", ok=1))
    assert ("moi-0", "chuoi") in f, f
    # plan sai: không ghi file, mã thoát 1
    def bad(mut, msg):
        s = json.loads(json.dumps(spec))
        mut(s)
        jw(d / "bad.json", s)
        (d / "bad_plan.json").unlink(missing_ok=True)
        p = run("build_tax_plan.py", "build", "--spec", d / "bad.json", "--map", d / "map.tsv", "--out", d / "bad_plan.json", ok=1)
        assert msg in p.stderr and not (d / "bad_plan.json").exists(), p.stderr
    bad(lambda s: s["terms"][1].update(parent="khong-co"), "cha khong-co")
    bad(lambda s: s["terms"].append({"key": "x", "term_id": None, "name": "X", "slug": "tu-khoa", "parent": "seo"}), "trùng giữa anh em")
    bad(lambda s: s["redirects"][0].update(to_key="khong-co"), "đích khong-co")
    bad(lambda s: s["terms"][0].update(parent="tu-khoa"), "vòng cha-con")
    (d / "map_bad.tsv").write_text("id\tprimary\n100\tkhong-co\n")
    run("build_tax_plan.py", "build", "--spec", d / "spec.json", "--map", d / "map_bad.tsv", ok=1)
    run("build_tax_plan.py", "build", "--spec", d / "khong-co.json", "--map", d / "map.tsv", ok=2)


def test_diagnose(d):
    # [gtvseo 18/10] chuyên mục inbound-marketing trùng archive CPT; trang /ai/ trùng slug chuyên mục ai; rule chiếm URL chuyên mục mới
    jw(d / "cats.json", [{"id": 4, "slug": "seo", "parent": 0, "path": "/seo/"}, {"id": 9, "slug": "inbound-marketing", "parent": 0, "path": "/inbound-marketing/"},
                         {"id": 10, "slug": "ai", "parent": 0, "path": "/ai/"}, {"id": 45, "slug": "tu-khoa", "parent": 4, "path": "/seo/tu-khoa/"}])
    posts = [dict(post(1, "post", "publish", "a", "/seo/a/"), primary="tu-khoa", cats=["tu-khoa"]),
             dict(post(2, "post", "publish", "b", "/seo/b/"), primary="tu-khoa", cats=["tu-khoa"]),
             dict(post(3, "post", "publish", "c", "/c/"), primary="seo", cats=["seo"]),
             post(4, "page", "publish", "ai", "/ai/")]
    jw(d / "posts.json", posts)
    jw(d / "clicks.json", {"1": [100, 900], "2": [50, 400], "3": [7, 70]})
    jw(d / "rules.json", [rule(99, "/seo/thuat-toan/", "/x/")])
    jw(d / "spec.json", {"terms": [{"key": "seo", "term_id": 4, "name": "SEO", "slug": "seo", "parent": None},
                                   {"key": "thuat-toan", "term_id": None, "name": "T", "slug": "thuat-toan", "parent": "seo"}]})
    p = run("build_tax_plan.py", "diagnose", "--cats", d / "cats.json", "--posts", d / "posts.json", "--cpt-archives", "/inbound-marketing/",
            "--clicks", d / "clicks.json", "--rules", d / "rules.json", "--spec", d / "spec.json")
    r = json.loads(p.stdout)
    assert [x["chuyen_muc"] for x in r["trung_archive_cpt"]] == ["inbound-marketing"], r
    assert [x["chuyen_muc"] for x in r["slug_va_cham"]] == ["ai"], r
    assert [x["chuyen_muc"] for x in r["redirect_chiem_url"]] == ["moi:thuat-toan"], r
    assert r["click_chuyen_muc"][0] == {"chuyen_muc": "tu-khoa", "bai": 2, "click": 150, "impression": 1300}
    assert r["truc_tron"]["kieu"] == "doc_tay" and r["truc_tron"]["cay"] == {"seo": ["tu-khoa"]}
    assert r["ket_luan"] == "cay_sai"
    jw(d / "cpt.json", ["/inbound-marketing/"])  # output PART=cpt của export_tax_redirects.php
    r2 = json.loads(run("build_tax_plan.py", "diagnose", "--cats", d / "cats.json", "--posts", d / "posts.json", "--cpt-archives", d / "cpt.json").stdout)
    assert [x["chuyen_muc"] for x in r2["trung_archive_cpt"]] == ["inbound-marketing"], r2
    # --gsc: output gsc.sh query (JSON rows) hoặc TSV page/clicks/impressions, khớp theo path của bài
    jw(d / "gsc.json", {"rows": [{"keys": ["https://mau.vn/seo/a/"], "clicks": 100, "impressions": 900},
                                 {"keys": ["https://mau.vn/seo/b/?utm=x"], "clicks": 50, "impressions": 400},
                                 {"keys": ["https://mau.vn/seo/"], "clicks": 9, "impressions": 90}]})
    r = json.loads(run("build_tax_plan.py", "diagnose", "--cats", d / "cats.json", "--posts", d / "posts.json", "--gsc", d / "gsc.json").stdout)
    assert r["click_chuyen_muc"][0] == {"chuyen_muc": "tu-khoa", "bai": 2, "click": 150, "impression": 1300} and r["gsc_khong_khop"] == 1, r
    (d / "gsc.tsv").write_text("page\tclicks\timpressions\nhttps://mau.vn/c/\t7\t70\n", encoding="utf-8")
    r = json.loads(run("build_tax_plan.py", "diagnose", "--cats", d / "cats.json", "--posts", d / "posts.json", "--gsc", d / "gsc.tsv").stdout)
    assert r["click_chuyen_muc"] == [{"chuyen_muc": "seo", "bai": 1, "click": 7, "impression": 70}], r
    # cây sạch
    jw(d / "cats2.json", [{"id": 4, "slug": "seo", "parent": 0, "path": "/seo/"}])
    jw(d / "posts2.json", [post(3, "post", "publish", "c", "/c/")])
    r = json.loads(run("build_tax_plan.py", "diagnose", "--cats", d / "cats2.json", "--posts", d / "posts2.json").stdout)
    assert r["ket_luan"] == "cay_chua_thay_dau_hieu_hong", r


def test_wayback(d):
    # Chỉ chạy --offline với cache giả: không gọi mạng.
    (d / "ra.tsv").write_text("url\tma\tdich\tnguon\tcanh_bao\tly_do\n/khong-co/\t410_de_xuat\t\t\t\t\n/co-click/\thoi\t\t\t\t\n"
                              "/bai-song/\tgiu\t\t\t\t\n/chua-cache/\t410_de_xuat\t\t\t\t\n", encoding="utf-8")
    c = d / "cache"
    c.mkdir()
    (c / "%2Fkhong-co.json").write_text(json.dumps([["timestamp", "statuscode"], ["20210423174117", "200"]]))
    (c / "%2Fco-click.json").write_text("[]")
    p = run("wayback_cdx.py", "--in", d / "ra.tsv", "--host", "mau.vn", "--out", d / "wb.json", "--cache", c, "--offline")
    wb = json.loads((d / "wb.json").read_text())
    assert set(wb) == {"/khong-co/", "/co-click/"} and "chua-cache" in p.stderr, (wb, p.stderr)
    assert json.loads(p.stdout) == {"url": 3, "co_du_lieu": 2, "co_ban_200": 1, "loi_mang": 0}, p.stdout
    # wb.json đi thẳng vào pick_target.py: /khong-co/ thành doc_wayback
    jw(d / "dump.json", DUMP)
    (d / "urls.tsv").write_text("url\tclicks\tdich_goi_y\ttam_dong\n/khong-co/\t0\t\t\n", encoding="utf-8")
    out = run("pick_target.py", "--urls", d / "urls.tsv", "--dump", d / "dump.json", "--wayback", d / "wb.json").stdout
    assert out.splitlines()[1].split("\t")[1] == "doc_wayback", out
    run("wayback_cdx.py", "--in", d / "khong-co.tsv", "--host", "mau.vn", "--out", d / "x.json", ok=2)
    run("wayback_cdx.py", "--in", d / "ra.tsv", "--host", "mau.vn", "--out", d / "x.json", "--offline", ok=2)


STUB = r"""<?php
// Stub WordPress tối thiểu. Mọi lệnh ghi in "WRITE" rồi thoát 99.
const ARRAY_A = 'ARRAY_A';
function w($n) { echo "WRITE $n\n"; exit(99); }
class WP_Error {}
function is_wp_error($x) { return $x instanceof WP_Error; }
function get_term($id, $t) { $m = [4 => ['seo', 'kinh-nghiem-seo', 0, ''], 45 => ['Từ khoá', 'keyword-research', 4, '']];
  if (!isset($m[$id])) return null; return (object)['term_id' => $id, 'name' => $m[$id][0], 'slug' => $m[$id][1], 'parent' => $m[$id][2], 'description' => $m[$id][3]]; }
function get_term_by($f, $v, $t) { return false; }
function get_option($k, $d = false) { return ['tax-45' => 'category/seo/keyword-research']; }
function get_term_meta($id, $k, $s) { return ''; }
function get_post($id) { return (object)['ID' => $id, 'post_type' => 'post']; }
function wp_get_object_terms($id, $t, $a) { return ['kinh-nghiem-seo']; }
function maybe_serialize($x) { return serialize($x); }
function wp_parse_url($u, $c = -1) { return parse_url($u, $c); }
function wp_json_encode($x, $f = 0) { return json_encode($x, $f); }
function get_permalink($id) { return 'https://mau.vn/p' . $id . '/'; }
function update_option() { w('update_option'); } function update_term_meta() { w('update_term_meta'); } function update_post_meta() { w('update_post_meta'); }
function wp_update_term() { w('wp_update_term'); } function wp_insert_term() { w('wp_insert_term'); } function wp_set_object_terms() { w('wp_set_object_terms'); }
function delete_post_meta() { w('delete_post_meta'); } function clean_post_cache() { w('clean_post_cache'); }
class DBStub { public $prefix = 'wp_'; public $posts = 'wp_posts'; public $postmeta = 'wp_postmeta';
  function prepare($q, ...$a) { return $q; } function get_var($q) { return null; } function get_row($q, $o = null) { return null; }
  function update() { w('wpdb->update'); } function query() { w('wpdb->query'); }
  function get_results($q, $o = null) { return strpos($q, 'postmeta') !== false ? ($GLOBALS['META'] ?? []) : ($GLOBALS['ROWS'] ?? []); } }
$wpdb = new DBStub();
"""


def test_php(d):
    php = shutil.which("php")
    if not php:
        print("bỏ qua PHP: máy không có php")
        return
    for f in ("taxonomy_rollout.php", "export_urls.php", "export_tax_redirects.php"):
        p = subprocess.run([php, "-l", str(S / f)], capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
    # rollout: DRY mặc định không ghi gì, plan khớp stub → thoát 0
    jw(d / "plan.json", {"terms": [{"key": "seo", "term_id": 4, "name": "seo", "slug": "kinh-nghiem-seo", "parent": None, "uri": "kinh-nghiem-seo"},
                                   {"key": "tu-khoa", "term_id": 45, "name": "Từ khoá", "slug": "tu-khoa", "parent": "seo", "uri": "kinh-nghiem-seo/tu-khoa"}],
                         "pm_remove": [], "noindex_terms": [], "posts": [{"id": 100, "expect_cats": ["kinh-nghiem-seo"], "cats": ["tu-khoa"], "primary": "tu-khoa"}],
                         "redirects": [{"pattern": "^seo/cu$", "to": "/kinh-nghiem-seo/tu-khoa/", "note": "cu", "to_term": "tu-khoa"}],
                         "deactivate_redirects": []})
    stub = STUB + """
if (!class_exists('RankMath')) { eval('namespace RankMath\\\\Redirections; class DB { static function add() { echo "WRITE rm_add\\n"; exit(99); } static function change_status() { echo "WRITE rm_status\\n"; exit(99); } }'); }
"""
    (d / "h_rollout.php").write_text(stub + "include getenv('TARGET');\n")

    def prun(target, env, ok):
        e = {"TARGET": str(S / target), "PATH": "/usr/bin:/bin:/opt/homebrew/bin", **env}
        p = subprocess.run([php, str(d / "h_rollout.php")], capture_output=True, text=True, env=e)
        assert p.returncode == ok, (target, env, p.returncode, p.stdout[-600:], p.stderr[-300:])
        return p
    p = prun("taxonomy_rollout.php", {"PLAN": str(d / "plan.json")}, 0)
    log = json.loads(p.stdout)
    assert log["dry"] is True and "WRITE" not in p.stdout and log["errors"] == []
    assert log["terms"][0]["change"] == [] and log["terms"][1]["change"] == {"slug": "tu-khoa"}, log["terms"]
    assert log["pm"][1] == ["tax-45", "category/seo/keyword-research", "kinh-nghiem-seo/tu-khoa"], log["pm"]
    assert log["posts"][0]["after"] == ["tu-khoa"]
    # DRY không đặt thì vẫn là DRY; không PLAN thì thoát 2
    prun("taxonomy_rollout.php", {"PLAN": str(d / "plan.json"), "DRY": "1"}, 0)
    # [theaigrowth 17/10] đích 301 khác URI Permalink Manager của chuyên mục đích: log báo lỗi, thoát 1
    plan = json.loads((d / "plan.json").read_text())
    plan["redirects"][0]["to"] = "/seo/tu-khoa/"
    jw(d / "plan_lech.json", plan)
    log = json.loads(prun("taxonomy_rollout.php", {"PLAN": str(d / "plan_lech.json")}, 1).stdout)
    assert "khác URI Permalink Manager" in log["errors"][0] and log["redirects"][0]["dich_lech_uri"] == "kinh-nghiem-seo/tu-khoa", log
    prun("taxonomy_rollout.php", {}, 2)
    # DRY=0 phải ghi (stub chặn bằng exit 99): chứng minh cổng DRY có tác dụng
    p = prun("taxonomy_rollout.php", {"PLAN": str(d / "plan.json"), "DRY": "0"}, 99)
    assert "WRITE" in p.stdout
    # export_urls.php: chỉ đọc, ra JSON đúng trường
    (d / "h_export.php").write_text(stub.replace("$wpdb = new DBStub();", "$wpdb = new DBStub(); $META = [['post_id' => 3, 'meta_value' => 'bai-cu']]; $ROWS = [['ID' => 3, 'post_type' => 'post', 'post_status' => 'publish', 'post_name' => 'bai-moi', 'post_parent' => 0], ['ID' => 4, 'post_type' => 'attachment', 'post_status' => 'inherit', 'post_name' => 'anh', 'post_parent' => 3], ['ID' => 5, 'post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'gioi-thieu', 'post_parent' => 0]];")
                                    + "function get_post_meta($id, $k, $s = false) { return $k === 'rank_math_primary_category' ? 45 : ''; }\n"
                                    + "include getenv('TARGET');\n")
    e = {"TARGET": str(S / "export_urls.php"), "PATH": "/usr/bin:/bin:/opt/homebrew/bin"}
    p = subprocess.run([php, str(d / "h_export.php")], capture_output=True, text=True, env=e)
    assert p.returncode == 0 and "WRITE" not in p.stdout, p.stdout + p.stderr
    out = json.loads(p.stdout[p.stdout.index("["):])
    byid = {o["id"]: o for o in out}
    assert byid[3]["old_slugs"] == ["bai-cu"] and byid[3]["path"] == "/p3/" and byid[4]["path"] is None, out
    # bài publish có cats và primary (slug) cho diagnose; attachment không có
    assert byid[3]["cats"] == ["kinh-nghiem-seo"] and byid[3]["primary"] == "keyword-research" and "cats" not in byid[4] and "cats" not in byid[5], out
    # export_tax_redirects.php: chỉ đọc, 5 phần, xuất rule Rank Math đúng dạng chain_check.py
    rm = STUB + r"""
function get_terms($a) { $c = fn($i, $s, $n, $p, $t) => (object)['term_id' => $i, 'slug' => $s, 'name' => $n, 'parent' => $p, 'count' => 1, 'taxonomy' => $t];
  if ($a['taxonomy'] === 'category') return [$c(4, 'seo', 'SEO &amp; GEO', 0, 'category'), $c(45, 'tu-khoa', 'Từ khoá', 4, 'category')];
  return $a['taxonomy'] === 'post_tag' ? [$c(7, 'ai', 'AI', 0, 'post_tag')] : []; }
function get_term_link($t) { return $t->taxonomy === 'category' ? ($t->term_id === 45 ? 'https://mau.vn/seo/tu-khoa/' : 'https://mau.vn/seo/') : 'https://mau.vn/tag/' . $t->slug . '/'; }
function get_post_types($a) { return ['khoa-hoc' => 'khoa-hoc']; }
function get_post_type_archive_link($pt) { return 'https://mau.vn/' . $pt . '/'; }
function get_taxonomies($a) { return ['category' => 'category', 'post_tag' => 'post_tag']; }
function maybe_unserialize($x) { return is_string($x) ? unserialize($x) : $x; }
class DBRM extends DBStub { function get_var($q) { return getenv('HAS_RM') === '1' ? 'wp_rank_math_redirections' : null; }
  function get_results($q, $o = null) { return [
    ['id' => '14', 'sources' => serialize([['ignore' => '', 'pattern' => 'seo-cu', 'comparison' => 'exact']]), 'url_to' => 'https://mau.vn/seo/', 'header_code' => '301', 'status' => 'active'],
    ['id' => '15', 'sources' => serialize([['ignore' => '', 'pattern' => 'tin-cu', 'comparison' => 'exact']]), 'url_to' => '', 'header_code' => '410', 'status' => 'active']]; } }
$wpdb = new DBRM();
include getenv('TARGET');
"""
    (d / "h_tax.php").write_text(rm)

    def trun(part, ok=0, rm_table="1"):
        e = {"TARGET": str(S / "export_tax_redirects.php"), "PATH": "/usr/bin:/bin:/opt/homebrew/bin", "PART": part, "HAS_RM": rm_table}
        p = subprocess.run([php, str(d / "h_tax.php")], capture_output=True, text=True, env=e)
        assert p.returncode == ok and "WRITE" not in p.stdout, (part, p.returncode, p.stdout, p.stderr)
        return p
    cats = json.loads(trun("cats").stdout)
    assert cats[0] == {"id": 4, "slug": "seo", "name": "SEO & GEO", "parent": 0, "count": 1, "path": "/seo/"} and cats[1]["path"] == "/seo/tu-khoa/", cats
    assert json.loads(trun("cpt").stdout) == ["/khoa-hoc/"]
    terms = json.loads(trun("terms").stdout)
    assert terms == ["/khoa-hoc/", "/seo/", "/seo/tu-khoa/", "/tag/ai/"], terms
    assert json.loads(trun("uris").stdout) == {"tax-45": "category/seo/keyword-research"}
    p = trun("rules", rm_table="0")
    assert json.loads(p.stdout) == [] and "Không có bảng" in p.stderr
    rules = json.loads(trun("rules").stdout)
    assert rules[1] == {"id": 15, "sources": [{"pattern": "tin-cu", "comparison": "exact"}], "to": "", "code": 410, "status": "active"}, rules
    trun("khac", ok=2)
    # OUT: ghi file thay cho stdout (stdout trên server có thể lẫn dòng "Success:" và warning PHP)
    e = {"TARGET": str(S / "export_tax_redirects.php"), "PATH": "/usr/bin:/bin:/opt/homebrew/bin", "PART": "cats", "OUT": str(d / "cats_out.json")}
    p = subprocess.run([php, str(d / "h_tax.php")], capture_output=True, text=True, env=e)
    assert p.returncode == 0 and p.stdout.startswith("OK cats") and json.loads((d / "cats_out.json").read_text()) == cats, p.stdout
    p = prun("taxonomy_rollout.php", {"PLAN": str(d / "plan.json"), "OUT": str(d / "log_out.json")}, 0)
    assert p.stdout.startswith("OK log") and json.loads((d / "log_out.json").read_text())["dry"] is True, p.stdout
    # nối thẳng sang chain_check.py: rule 410 rỗng đích không báo lỗi; 301 về chuyên mục chỉ là cảnh báo
    (d / "rules.json").write_text(json.dumps(rules))
    (d / "terms.json").write_text(json.dumps(terms))
    f = findings(run("chain_check.py", "--rules", d / "rules.json", "--terms", d / "terms.json", "--host", "mau.vn"))
    assert f == {("14", "dich_danh_muc")}, f


def test_help():
    for s in ("chain_check.py", "pick_target.py", "build_tax_plan.py", "wayback_cdx.py"):
        p = run(s, "--help")
        assert "Mã thoát" in p.stdout, s


def main():
    test_help()
    for t in (test_chain_check, test_pick_target, test_build_tax_plan, test_diagnose, test_wayback, test_php):
        with tempfile.TemporaryDirectory() as tmp:
            t(Path(tmp))
    print("OK test_url_lifecycle")


if __name__ == "__main__":
    main()
