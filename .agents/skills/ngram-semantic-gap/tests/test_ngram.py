#!/usr/bin/env python3
"""Test offline cho ngram.py: trang đối thủ, blocks, GSC, bản đề xuất và HTML đều là dữ liệu giả, không cần mạng hay model.
Chạy: python3 -E tests/test_ngram.py (phần comp và site cần beautifulsoup4; thiếu thì bỏ qua 2 phần đó và báo SKIP).
"""
import json
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
NG = HERE.parent / "scripts" / "ngram.py"
sys.path.insert(0, str(HERE.parent / "scripts"))
import ngram  # noqa: E402


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-E", str(NG), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def jw(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def jl(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def tsv(p):
    lines = Path(p).read_text(encoding="utf-8").splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:]]


def test_tokens():
    # NFC: chữ tổ hợp (NFD) và chữ dựng sẵn cho cùng tiếng; không vượt ranh giới dòng; bỏ cụm mở/đóng bằng hư từ và cụm toàn số
    nfd = unicodedata.normalize("NFD", "Dịch vụ SEO")
    assert ngram.toks(nfd) == ["dịch", "vụ", "seo"]
    g = ngram.grams("bảng giá seo\nwebsite của bạn 2024 2025", (2, 3))
    assert g["bảng giá"] == 1 and g["giá seo"] == 1 and "seo website" not in g
    assert "của bạn" not in g and "2024 2025" not in g and "website của" not in g
    assert ngram.parse_n("2-4") == (2, 3, 4) and ngram.parse_n("1,3") == (1, 3)


def test_page(d):
    common = "Bảng giá dịch vụ SEO website\nQuy trình SEO website rõ ràng"
    comps = {"c1": common + "\nGoogle Maps cho doanh nghiệp", "c2": common + "\nGoogle Maps địa phương",
             "c3": common + "\nGoogle Maps", "c4": "Bảng giá dịch vụ SEO website\nchỉ có ở c4 thôi"}
    files = []
    for k, t in comps.items():
        jw(d / f"{k}.json", {"title": "", "meta": "", "headings": [["h2", "Giới thiệu"]], "text": t})
        files.append(d / f"{k}.json")
    # trang chỉ có heading (đối thủ chặn 403): vào ma trận thuộc tính, không vào n-gram
    jw(d / "c5.json", {"title": "Google Maps", "meta": "", "headings": ["Google Maps là gì"], "text": "", "headings_only": True})
    files.append(d / "c5.json")
    jl(d / "blocks.jsonl", [
        {"region": "header", "text": "Google Maps menu"},
        {"region": "main", "text": "Bảng giá dịch vụ SEO website của GTV"},
        {"region": "main", "text": "Thống trị ngách hàng đầu"},
        {"region": "main", "text": "Thống trị ngách hàng đầu"},
        {"region": "entry", "text": "Xem [thống trị ngách](https://x.vn/a) hàng đầu"},
    ])
    (d / "attrs.tsv").write_text("thuoc_tinh\tregex\nbản đồ\tgoogle maps\nbảng giá\tbảng giá\n", encoding="utf-8")
    run("page", "--comp", *files, "--page-blocks", d / "blocks.jsonl", "--tier1", "c1,c5", "--attrs", d / "attrs.tsv",
        "--name", "P", "--out", d / "out")
    s = json.loads((d / "out" / "summary_P.json").read_text(encoding="utf-8"))
    assert s["docs"] == 5 and s["docs_full_text"] == 4 and s["need_df"] == 3 and s["headings_only"] == ["c5"]
    miss = {r["ngram"]: r for r in tsv(d / "out" / "ngram_missing_P.tsv")}
    # "google maps" có ở 3/4 trang có chữ thân; vùng header của trang mình không được tính
    assert miss["google maps"]["df_doi_thu"] == "3" and miss["quy trình"]["df_doi_thu"] == "3"
    assert "seo website" not in miss and "bảng giá" not in miss
    uniq = {r["ngram"]: r["tan_so_trang"] for r in tsv(d / "out" / "ngram_unique_P.tsv")}
    # khối trùng nguyên văn bị bỏ, link markdown bị gỡ: "thống trị ngách" = 2 (1 khối main + 1 khối entry)
    assert uniq.get("thống trị ngách") == "2" and "hàng đầu" in uniq
    shared = {r["ngram"]: r for r in tsv(d / "out" / "ngram_shared_P.tsv")}
    assert shared["seo website"]["df_doi_thu"] == "4"
    cons = {r["thuoc_tinh"]: r for r in tsv(d / "out" / "consensus_P.tsv")}
    # c1, c5 tier 1 → tổng trọng số 7; google maps có ở c1 (2) + c2 + c3 + c5 (2) = 6 → 86% MANDATORY, trang không có
    assert cons["bản đồ"]["pct_trong_so"] == "86" and cons["bản đồ"]["muc"] == "MANDATORY" and cons["bản đồ"]["trang"] == "KHÔNG"
    assert cons["bảng giá"]["trang"] == "có"
    # thứ tự ổn định: hai lần chạy cho file giống hệt từng byte
    run("page", "--comp", *files, "--page-blocks", d / "blocks.jsonl", "--name", "P", "--out", d / "out2")
    assert (d / "out" / "ngram_missing_P.tsv").read_bytes() == (d / "out2" / "ngram_missing_P.tsv").read_bytes()
    # --keep-dup giữ khối trùng
    run("page", "--comp", *files, "--page-blocks", d / "blocks.jsonl", "--keep-dup", "--name", "K", "--out", d / "out")
    uk = {r["ngram"]: r["tan_so_trang"] for r in tsv(d / "out" / "ngram_unique_K.tsv")}
    assert uk["thống trị ngách"] == "3"
    # tên tier1 sai thì dừng
    run("page", "--comp", *files, "--page-blocks", d / "blocks.jsonl", "--tier1", "khong-co", "--name", "X", "--out", d / "out",
        ok=False)


def test_gsc_measure(d):
    rows = [
        ("page", "query", "clicks", "impressions", "position"),
        ("https://mau.vn/dich-vu-seo/", "Dịch vụ SEO website", 5, 1000, 10),
        ("https://mau.vn/dich-vu-seo/", unicodedata.normalize("NFD", "dịch vụ seo website"), 1, 200, 20),
        ("https://mau.vn/dich-vu-seo/#ftoc-gia", "dịch vụ seo website", 9, 900, 3),  # jump link: bỏ
        ("https://mau.vn/dich-vu-seo/", "dich vu seo website", 0, 300, 12),
        ("https://mau.vn/dich-vu-seo/", "bảng giá seo", 2, 400, 8),
        ("https://mau.vn/khac/", "dịch vụ seo website", 9, 5000, 1),
    ]
    (d / "gsc.tsv").write_text("\n".join("\t".join(map(str, r)) for r in rows) + "\n", encoding="utf-8")
    jl(d / "own.jsonl", [{"region": "main", "text": "Bảng giá SEO trọn gói"}])
    run("page", "--comp", d / "c1.json", d / "c2.json", d / "c3.json", d / "c4.json", "--page-blocks", d / "own.jsonl",
        "--name", "G", "--out", d / "gap")
    run("gsc", "--gsc", d / "gsc.tsv", "--page", "/dich-vu-seo", "--page-blocks", d / "own.jsonl", "--gap", d / "gap",
        "--name", "G", "--out", d / "gsc", "--n", "2-4")
    s = json.loads((d / "gsc" / "gsc_summary_G.json").read_text(encoding="utf-8"))
    assert s["jump_rows_skipped"] == 1 and s["queries"] == 3 and s["impressions"] == 1900
    g = {r["ngram"]: r for r in tsv(d / "gsc" / "gsc_ngram_G.tsv")}
    # NFD + chữ hoa gộp vào cùng query; "dich vu seo website" là biến thể thiếu dấu
    assert g["seo website"]["impressions"] == "1500" and g["dịch vụ seo website"]["impressions"] == "1200"
    assert g["dịch vụ seo website"]["bien_the_dau"] == "0" and g["dich vu seo website"]["bien_the_dau"] == "1"
    assert g["seo website"]["bien_the_dau"] == "0" and g["seo website"]["tan_so_trang"] == "0"
    assert g["seo website"]["doi_thu"] == "missing" and g["bảng giá"]["tan_so_trang"] == "1"
    assert abs(float(g["dịch vụ seo website"]["vi_tri_tb"]) - 11.7) < 0.05
    # measure: bản đề xuất phủ cụm thiếu, bắt nhồi cụm, bắt mất cụm riêng
    (d / "before.txt").write_text("Thống trị ngách hàng đầu. Thống trị ngách tốt.\nBảng giá SEO trọn gói", encoding="utf-8")
    (d / "after.txt").write_text("Bảng giá SEO trọn gói\n" + "Google Maps giúp quy trình SEO. " * 5, encoding="utf-8")
    (d / "gap" / "ngram_unique_G.tsv").write_text("ngram\ttan_so_trang\nthống trị ngách\t2\n", encoding="utf-8")
    run("measure", "--before", d / "before.txt", "--after", d / "after.txt", "--gap", d / "gap", "--name", "G",
        "--gsc-ngrams", d / "gsc" / "gsc_ngram_G.tsv", "--out", d / "m.json")
    m = json.loads((d / "m.json").read_text(encoding="utf-8"))
    cov = {x["ngram"]: x["after"] for x in m["covered"]}
    assert cov["google maps"] == 5 and m["missing_covered_before"] == 0
    assert any(x["ngram"] == "google maps" and x["cap"] == 3 for x in m["stuffing"])
    assert m["unique_lost"] == ["thống trị ngách"]
    assert m["gsc_impr_covered_after"] < 0.5 and "seo website" in m["gsc_still_missing"]


def test_sections_doorway(d):
    blk = []
    for pg, extra in (("A", ""), ("B", " Hà Nội")):
        blk = [{"url": f"https://mau.vn/{pg}/", "region": "main", "tag": "p", "h2": "", "text": "Đoạn mở đầu dài đủ chữ cho section hero" * 4 + extra},
               {"url": f"https://mau.vn/{pg}/", "region": "main", "tag": "h2", "h2": "", "text": "Bảng giá dịch vụ"},
               {"url": f"https://mau.vn/{pg}/", "region": "main", "tag": "p", "h2": "Bảng giá dịch vụ", "text": "Giá từ 10 triệu mỗi tháng cho gói cơ bản" * 4},
               {"url": f"https://mau.vn/{pg}/", "region": "main", "tag": "p", "h2": "Bảng giá dịch vụ", "text": "https://mau.vn/anh.jpg"},
               {"url": f"https://mau.vn/{pg}/", "region": "footer", "tag": "p", "h2": "", "text": "Chân trang" * 30}]
        jl(d / f"b_{pg}.jsonl", blk)
    run("sections", "--page-blocks", f"A={d / 'b_A.jsonl'}", f"B={d / 'b_B.jsonl'}", "--out", d / "sec.jsonl")
    sec = [json.loads(l) for l in (d / "sec.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [s["id"] for s in sec] == ["A-00", "A-01", "B-00", "B-01"] and sec[1]["meta"]["h2"] == "Bảng giá dịch vụ"
    assert all("Chân trang" not in s["text"] and "anh.jpg" not in s["text"] for s in sec)
    # cặp giả: ngưỡng là p90 của cặp khác trang, không phải ngưỡng tuyệt đối; id có dấu "-" trong KEY vẫn tách đúng
    pairs = [("A-00", "B-00", 0.99), ("A-01", "B-01", 0.80), ("A-00", "B-01", 0.70), ("A-01", "B-00", 0.75), ("A-00", "A-01", 0.999)]
    (d / "pairs.tsv").write_text("a\tb\tcos\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in pairs), encoding="utf-8")
    run("doorway", "--pairs", d / "pairs.tsv", "--ref", "A", "--sections", d / "sec.jsonl", "--out", d / "door")
    s = json.loads((d / "door" / "doorway_summary.json").read_text(encoding="utf-8"))
    assert s["pairs"] == 4 and abs(s["cut"] - ngram.percentile([0.99, 0.80, 0.70, 0.75], 90)) < 1e-9
    assert s["pages"]["B"] == {"sections": 2, "ge_cut": 1}
    assert abs(ngram.percentile([1, 2, 3, 4, 5], 90) - 4.6) < 1e-9 and ngram.page_of("loc-hn-03") == "loc-hn"


def test_html(d):
    try:
        import bs4  # noqa: F401
    except ImportError:
        print("SKIP comp, site: thiếu beautifulsoup4")
        return
    (d / "comp").mkdir()
    (d / "comp" / "x.html").write_text("""<html><head><title>Dịch vụ SEO</title><meta name="description" content="Mô tả">
<script>var a=1</script></head><body><nav>Menu chính</nav><main><h1>Dịch vụ SEO</h1><p>Bảng giá dịch vụ SEO website.</p>
<div class="sidebar"><p>Bài liên quan</p></div><ul><li>Google Maps</li></ul></main><footer>Chân trang</footer></body></html>""",
                                      encoding="utf-8")
    run("comp", "--html-dir", d / "comp", "--out", d / "compj")
    x = json.loads((d / "compj" / "x.json").read_text(encoding="utf-8"))
    assert x["title"] == "Dịch vụ SEO" and x["meta"] == "Mô tả" and x["headings"] == [["h1", "Dịch vụ SEO"]]
    assert "Bảng giá dịch vụ SEO website." in x["text"] and "Menu" not in x["text"] and "Bài liên quan" not in x["text"]
    site = d / "site"
    site.mkdir()
    for i in range(6):
        body = (f'<div class="elementor-location-header"><a>Trang chủ</a><a>Liên hệ hotline</a></div>'
                f'<main><h1>Bài số {i}</h1><p>Nội dung riêng chủ đề {["seo", "geo", "ads", "web", "maps", "ai"][i]} dài</p>'
                + ('<p>Nhận tư vấn SEO miễn phí ngay hôm nay</p>' if i < 5 else '') +
                '</main><div class="elementor-location-footer"><p>Công ty mẫu địa chỉ Hà Nội</p></div>')
        (site / f"p{i}.html").write_text(f"<html><body>{body}</body></html>", encoding="utf-8")
        (site / f"p{i}.url").write_text(f"https://mau.vn/blog/p{i}/", encoding="utf-8")
    run("site", "--html-dir", site, "--out", d / "siteout", "--rep-min", "5")
    s = json.loads((d / "siteout" / "site_summary.json").read_text(encoding="utf-8"))
    assert s["pages"] == 6 and s["repeated_segments"] == 1
    boil = {r["ngram"]: r for r in tsv(d / "siteout" / "ngram_boiler_sitewide.tsv")}
    # header, footer có trên 6/6 trang; khối CTA lặp trên 5/6 trang (83%) cũng là boilerplate
    assert "liên hệ hotline" in boil and "công ty mẫu" in boil and "tư vấn seo" in boil
    assert "chủ đề seo" not in boil
    reg = {r["url"]: r for r in tsv(d / "siteout" / "page_regions.tsv")}
    r0 = reg["https://mau.vn/blog/p0/"]
    assert r0["group"] == "/blog" and int(r0["boiler_tpl"]) == 9 and int(r0["boiler_site"]) > 0
    assert float(reg["https://mau.vn/blog/p5/"]["boiler_share"]) < float(r0["boiler_share"])


def main():
    test_tokens()
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        test_page(d)
        test_gsc_measure(d)
        test_sections_doorway(d)
        test_html(d)
    print("OK test_ngram")


if __name__ == "__main__":
    main()
