#!/usr/bin/env python3
"""Test offline cho scn.py: export Screaming Frog, SERP, GSC, review và thẻ đều là dữ liệu giả, không cần mạng hay model.
Chạy: python3 -I tests/test_scn.py
"""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCN = HERE.parent / "scripts" / "scn.py"
sys.path.insert(0, str(HERE.parent / "scripts"))
import scn  # noqa: E402

H = "https://mau.vn"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-I", str(SCN), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def wcsv(p, head, rows):
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)


def wtsv(p, head, rows):
    Path(p).write_text("\t".join(head) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows), encoding="utf-8")


def jw(p, o):
    Path(p).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")


def tsv(p):
    return scn.read_tsv(p)


def test_graph(d):
    sf = d / "sf"
    sf.mkdir()
    pages = ["/", "/dich-vu/", "/bai-a/", "/bai-b/", "/bai-c/", "/bai-d/", "/bai-e/", "/bai-f/"]
    rows = [[H + p, "text/html; charset=UTF-8", "200", "Indexable", "0" if p == "/" else ""] for p in pages]
    rows += [[H + "/noindex/", "text/html", "200", "Non-Indexable", "1"], [H + "/404/", "text/html", "404", "Non-Indexable", "1"]]
    wcsv(sf / "internal_all.csv", ["Address", "Content Type", "Status Code", "Indexability", "Crawl Depth"], rows)
    L = []

    def link(s, t, pos="Content", anchor="x", follow="true", typ="Hyperlink"):
        L.append([typ, H + s, H + t, anchor, follow, pos])

    for p in pages[1:]:
        link("/", p, "Navigation", "menu")           # menu: depth 1 theo mọi link, không phải link ngữ cảnh
    for p in ["/bai-a/", "/bai-b/", "/bai-c/", "/bai-d/", "/bai-e/"]:
        link(p, "/dich-vu/", "Content", "Tư vấn ngay")  # khối CTA lặp 5 trang: link template
    link("/", "/bai-a/", "Content", "bài A")
    link("/bai-a/", "/bai-b/", "Content", "bài B")
    link("/bai-a/", "/bai-b/", "Content", "bài B lần 2")  # 2 dòng cùng cặp: số dòng vị trí = 2
    link("/bai-b/", "/bai-c/", "Content", "bài C")
    link("/bai-c/", "/dich-vu/", "Content", "dịch vụ SEO")
    link("/bai-c/", "/bai-d/", "Content", "bài D", follow="false")  # nofollow: bỏ
    link("/bai-c/", "/noindex/", "Content", "noindex")              # đích không index: bỏ
    link("/bai-c/", "/bai-c/#muc-1", "Content", "mục lục")          # tự trỏ qua jump link: bỏ
    link("/bai-e/", "/bai-f/", "Content", "ảnh", typ="Image")       # không phải Hyperlink: bỏ
    wcsv(sf / "all_inlinks.csv", ["Type", "Source", "Destination", "Anchor", "Follow", "Link Position"], L)
    wtsv(d / "money.tsv", ["url", "ma"], [[H + "/dich-vu/", "M1"]])
    run("graph", "--sf", sf, "--money", d / "money.tsv", "--out", d / "g")
    s = json.loads((d / "g" / "graph_summary.json").read_text(encoding="utf-8"))
    assert s["pages"] == 8 and s["home"] == H + "/" and s["sf_depth_khop"] == 1
    assert s["depth_all"] == {"0": 1, "1": 7}
    # link ngữ cảnh: / → bài A → bài B → bài C → dịch vụ; CTA lặp 5 trang không tính; bài D, E, F không có link ngữ cảnh tới
    assert s["depth_ngu_canh"] == {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "không tới": 3}
    assert s["money"]["M1"] == {"url": H + "/dich-vu/", "depth_all": 1, "depth_ngu_canh": 4, "trang_nguon_ngu_canh": 1,
                                "hang_pr": s["money"]["M1"]["hang_pr"]}
    pr = {r["url"]: r for r in tsv(d / "g" / "pagerank_internal.tsv")}
    assert abs(sum(float(r["pr_x1000"]) for r in pr.values()) - 1000) < 0.05
    assert pr[H + "/bai-b/"]["content"] == "2" and pr[H + "/bai-b/"]["navigation"] == "1"
    assert pr[H + "/dich-vu/"]["hang"] == "1"  # trang tiền nhận link từ 7 trang
    # what-if: thêm link ngữ cảnh từ trang chủ tới dịch vụ → depth ngữ cảnh 1
    wtsv(d / "add.tsv", ["source", "target"], [[H + "/", H + "/dich-vu/"], [H + "/", H + "/khong-co/"]])
    run("graph", "--sf", sf, "--money", d / "money.tsv", "--add", d / "add.tsv", "--out", d / "g2")
    s2 = json.loads((d / "g2" / "graph_summary.json").read_text(encoding="utf-8"))
    assert s2["what_if"]["them"] == 1 and s2["what_if"]["bo_qua"] == [[H + "/", H + "/khong-co/"]]
    assert s2["what_if"]["money_sau"]["M1"]["depth_ngu_canh"] == 1
    # nguồn link ngữ cảnh từ site-vector-index
    rows = [{"id": "a1", "level": "anchor", "url": H + "/", "text": "x", "meta": {"target": H + "/bai-d/", "anchor": "d"}},
            {"id": "p1", "level": "passage", "url": H + "/", "text": "y", "meta": {}}]
    Path(d / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    run("graph", "--sf", sf, "--ctx-rows", d / "rows.jsonl", "--out", d / "g3")
    s3 = json.loads((d / "g3" / "graph_summary.json").read_text(encoding="utf-8"))
    assert s3["canh_ngu_canh"] == 1 and s3["depth_ngu_canh"]["1"] == 1


def test_serp(d):
    rows = []
    base = [f"https://site{i}.vn/a" for i in range(10)]
    for i, u in enumerate(base, 1):
        rows.append(["dịch vụ x", i, u])
    for i, u in enumerate(["http://www.site0.vn/a/", *base[1:6], "https://khac1.vn", "https://khac2.vn", "https://khac3.vn",
                           "https://khac4.vn"], 1):
        rows.append(["công ty x", i, u])  # 6 URL chung (www, http, dấu / cuối vẫn khớp)
    for i, u in enumerate([base[0], "https://z.vn"], 1):
        rows.append(["x là gì", i, u])  # 1 chung với mỗi truy vấn kia, SERP chỉ 2 URL
    for i, u in enumerate(base[:4] + ["https://z1.vn", "https://z2.vn"], 1):
        rows.append(["x giá", i, u])  # 4 chung với "dịch vụ x", SERP chỉ 6 URL
    wtsv(d / "serp.tsv", ["seed", "pos", "url"], rows)
    wtsv(d / "pairs.tsv", ["a", "b", "note"], [["dịch vụ x", "công ty x", "gộp?"], ["dịch vụ x", "x giá", ""],
                                              ["công ty x", "x là gì", ""], ["dịch vụ x", "không có", ""]])
    run("serp-overlap", "--serp", d / "serp.tsv", "--pairs", d / "pairs.tsv", "--out", d / "s")
    r = json.loads((d / "s" / "overlap_pairs.json").read_text(encoding="utf-8"))
    assert [x["chung"] for x in r] == [6, 4, 1, None]
    assert r[0]["verdict"] == "cùng nhóm" and r[1]["verdict"] == "vùng xám · SERP dưới 10 URL"
    assert r[2]["verdict"].startswith("tách") and r[3]["verdict"] == "thiếu SERP"
    allp = json.loads((d / "s" / "overlap_all.json").read_text(encoding="utf-8"))
    assert list(allp)[:3] == ["dịch vụ x | công ty x", "dịch vụ x | x là gì", "dịch vụ x | x giá"] and len(allp) == 6
    # thư mục JSON Firecrawl: tên file = truy vấn
    (d / "fc").mkdir()
    jw(d / "fc" / "dịch_vụ_x.json", {"data": {"web": [{"url": u} for u in base]}})
    jw(d / "fc" / "công_ty_x.json", {"data": [{"url": u} for u in base[:7]]})
    run("serp-overlap", "--serp", d / "fc", "--out", d / "s2")
    assert json.loads((d / "s2" / "overlap_all.json").read_text(encoding="utf-8")) == {"công ty x | dịch vụ x": 7}
    assert scn.verdict(6) == "cùng nhóm" and scn.verdict(5) == "vùng xám" and scn.verdict(3) == "tách"


def test_qp(d):
    rows = [["page", "query", "clicks", "impressions", "position"],
            [H + "/dich-vu/", "dịch vụ seo", 10, 700, 4], [H + "/bai-a/", "dịch vụ seo", 1, 300, 20],
            [H + "/dich-vu/#ftoc-gia", "dịch vụ seo", 50, 5000, 1],                       # jump link: bỏ
            [H + "/bai-a/", "giá seo", 1, 600, 8], [H + "/bang-gia/", "giá seo", 1, 400, 9],
            [H + "/bang-gia/", "báo giá seo", 0, 100, 12]]
    Path(d / "gsc.tsv").write_text("\n".join("\t".join(map(str, r)) for r in rows) + "\n", encoding="utf-8")
    wtsv(d / "tpl.tsv", ["id", "template", "target", "regex"],
         [["T1", "dịch vụ seo", "/dich-vu/", "^dịch vụ seo$"], ["T2", "giá seo", "/bang-gia/", "giá seo"],
          ["T3", "agency", "/agency/", "agency"], ["T4", "báo giá", "(trang mới)", "^báo giá"]])
    run("qp", "--gsc", d / "gsc.tsv", "--templates", d / "tpl.tsv", "--out", d / "q")
    b = {r["id"]: r for r in json.loads((d / "q" / "baseline.json").read_text(encoding="utf-8"))}
    assert b["T1"]["impr"] == 1000 and b["T1"]["urls"][0] == ["/dich-vu/", 70, 4.0] and b["T1"]["flag"] == "ổn"
    assert b["T2"]["impr"] == 1100 and b["T2"]["urls"][0][0] == "/bai-a/" and b["T2"]["flag"] == "lật URL"
    assert b["T3"]["flag"] == "chưa đo được" and b["T4"]["flag"] == "chưa chọn URL đích"
    assert scn.qp_flag("/a/", [("/a/", 55, 3.0)], 10) == "tách URL"
    assert scn.qp_flag("/a/", [("/b/", 45, 12.0)], 10) == "tách URL · chưa vào Top 10"
    head = (d / "q" / "baseline.tsv").read_text(encoding="utf-8").splitlines()[0]
    assert head.startswith("id\ttemplate\ttrang đích\tsố truy vấn")


def test_cards(d):
    rev = d / "rev"
    rev.mkdir()
    jw(rev / "c1.json", {"item_id": "c1", "status": "approved", "updatedAt": "2026-10-18T05:00:00Z",
                         "values": {"para": "Đoạn đã duyệt nói về quy trình SEO sáu bước của công ty mẫu rất rõ ràng."}})
    jw(rev / "c2.json", {"item_id": "c2", "status": "edited", "updatedAt": "2026-10-18T09:00:00Z", "values": {}})
    jw(rev / "khac.json", {"note": "không phải review"})
    cards = {"items": [
        {"id": "c1", "label": "Trang A", "kind": "Trang", "fields": [{"key": "para", "name": "Đoạn", "before": "cũ",
                                                                      "proposed": "Đoạn đã duyệt nói về quy trình SEO sáu bước của công ty mẫu rất rõ ràng."}]},
        {"id": "c2", "label": "Trang B", "kind": "Trang", "fields": [{"key": "seo_title", "name": "Title", "before": "a", "proposed": "b"}]},
        {"id": "c3", "label": "Bài C", "kind": "Bài", "fields": [{"key": "para1", "name": "Đoạn 1", "before": "x", "proposed": "y"}]},
        {"id": "c4", "label": "Bài D", "kind": "Bài", "fields": [{"key": "para1", "name": "Đoạn 1", "before": "x", "proposed": "z"}]},
        {"id": "c5", "label": "Bài E", "kind": "Bài", "fields": [{"key": "para1", "name": "Đoạn 1", "before": "x", "proposed": "w"}]},
        {"id": "c6", "label": "Trang F", "kind": "Trang", "fields": [{"key": "seo_title", "name": "Title", "before": "a", "proposed": "c"}]}]}
    jw(d / "scn-a.json", cards)
    run("status", "--reviews", rev, "--cards", d / "scn-a.json", "--until", "2026-10-18T08:30", "--out", d / "st.json")
    st = json.loads((d / "st.json").read_text(encoding="utf-8"))
    assert st["c1"][2] == "approved" and st["c2"][2] == "pending" and st["c1"][0] == "scn-a"
    run("status", "--reviews", rev, "--cards", d / "scn-a.json", "--out", d / "st_now.json")
    assert json.loads((d / "st_now.json").read_text(encoding="utf-8"))["c2"][2] == "edited"
    # guard: thẻ mới dùng lại id c1 và đổi chữ; thẻ khác sửa đoạn chứa chữ đã duyệt
    new = {"items": [
        {"id": "c1", "label": "Trang A", "fields": [{"key": "para", "name": "Đoạn", "before": "x", "proposed": "Chữ khác hẳn."}]},
        {"id": "v2-x", "label": "Trang A", "fields": [{"key": "block", "name": "Khối", "proposed": "Viết lại toàn bộ khối.",
                                                       "before": "Mở đầu. Đoạn đã duyệt nói về quy trình SEO sáu bước của công ty mẫu rất rõ ràng. Hết."}]},
        {"id": "v2-y", "label": "Trang A", "fields": [{"key": "block", "name": "Khối", "before": "Đoạn đã duyệt nói về quy trình SEO sáu bước của công ty mẫu rất rõ ràng.",
                                                       "proposed": "Đoạn đã duyệt nói về quy trình SEO sáu bước của công ty mẫu rất rõ ràng. Thêm câu."}]}]}
    jw(d / "new.json", new)
    run("guard", "--reviews", rev, "--cards", d / "new.json", "--out", d / "guard.json")
    g = json.loads((d / "guard.json").read_text(encoding="utf-8"))
    assert g["id_da_duyet"] == [{"card": "c1", "status": "approved", "field_changed": ["para"]}]
    assert [x["card"] for x in g["sua_chu_da_duyet"]] == ["v2-x"] and len(g["trung_chu_da_duyet"]) == 2
    # batch: c1 đã duyệt bị loại; c6 có title nên cảnh báo; lô 1 thẻ không dựng; thẻ trùng giữa 2 lô bị chặn
    lots = [{"id": "l1", "title": "Sửa đoạn", "rule": "Luật: chỉ sửa đoạn.", "members": ["c1", "c3", "c4", "c6"], "note": ""},
            {"id": "l2", "title": "Lô nhỏ", "rule": "Luật.", "members": ["c3", "c5"], "note": ""},
            {"id": "l3", "title": "Thiếu", "rule": "Luật.", "members": ["khong-co"], "note": ""}]
    jw(d / "lots.json", lots)
    run("batch", "--lots", d / "lots.json", "--cards", d / "scn-a.json", "--status", d / "st.json", "--out", d / "b")
    s = json.loads((d / "b" / "batch_summary.json").read_text(encoding="utf-8"))
    assert s["lots"]["l1"]["ids"] == ["c3", "c4", "c6"] and s["dropped_not_pending"] == ["c1"]
    assert s["duplicates"] == [["c3", "l1", "l2"]] and s["lots"]["l2"]["members"] == 1 and s["missing"] == ["khong-co"]
    assert s["solo_warn"] == ["c6"] and s["pending"] == 5 and s["in_lots"] == 4 and s["solo_ids"] == ["c2"]
    lc = json.loads((d / "b" / "lot_cards.json").read_text(encoding="utf-8"))["items"]
    assert [c["id"] for c in lc] == ["lo-l1"] and lc[0]["fields"][0]["name"] == "Thẻ trong lô (3)"


def main():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        test_graph(d)
        test_serp(d)
        test_qp(d)
        test_cards(d)
    print("OK test_scn")


if __name__ == "__main__":
    main()
