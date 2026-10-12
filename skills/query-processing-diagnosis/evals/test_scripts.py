#!/usr/bin/env python3
"""Test offline cho script của skill (không mạng, không cần Chrome). Thoát mã 1 nếu có ca hỏng.

  python3 evals/test_scripts.py
"""
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

D = Path(__file__).resolve().parents[1]
S = D / "scripts"
FAIL = []


def run(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)


def ok(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def load_mod(name):
    sys.path.insert(0, str(S))
    spec = importlib.util.spec_from_file_location(name, S / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def spyserp_csv(path, dates, rows, sep=";", project="Demo", vols=None):
    """CSV giả lập export SpySERP. rows: [(keyword, {domain: [hạng theo dates]})]."""
    hdr = ["Keywords", "Category", "Domains", "Search engines", "SERP Url", "Clustering #1", "Best Position", "Volume"] + dates
    q = lambda xs: sep.join(f'"{x}"' for x in xs)
    lines = [q(["", f"Project: {project}"]), q(["", "Search Engine", "GM1", "Google Mobile", "(demo)"]), q(["", "Schedules Page", "1"]), q(hdr)]
    for kw, by in rows:
        for dom, s in by.items():
            url = f"https://{dom}/den-hoc/?srsltid=x"
            lines.append(q([kw, "Main", dom, "GM1", url, "", "", str((vols or {}).get(kw, ""))] + s))
    Path(path).write_text("﻿" + "\n".join(lines), encoding="utf-8")


tmp = Path(tempfile.mkdtemp(prefix="qptest_"))
fx = D / "examples" / "mau-du-an.json"

# 1. renderer: check + project + --web bỏ kpi
r = run(S / "qp_render.py", "check", fx)
ok("check fixture OK", r.returncode == 0 and "OK" in r.stdout, r.stdout + r.stderr)
run(S / "qp_render.py", "project", fx, tmp / "a.html")
run(S / "qp_render.py", "project", fx, tmp / "w.html", "--web")
a, w = (tmp / "a.html").read_text(), (tmp / "w.html").read_text()
ok("deck nội bộ có khối kpi", "Mốc mẫu" in a)
ok("deck --web bỏ kpi và thẻ internal", "Mốc mẫu" not in w)
ok("nhãn mốc so sánh lấy từ compare_date", "Top 10: 11/09 → nay" in a)
bad = json.loads(fx.read_text())
bad["measure_slide"]["regex"][0]["rx"] = "(?<!x)đèn"
(tmp / "bad.json").write_text(json.dumps(bad, ensure_ascii=False))
r = run(S / "qp_render.py", "check", tmp / "bad.json")
ok("check chặn regex lookbehind (RE2)", r.returncode == 1 and "RE2" in r.stdout, r.stdout)
bad["measure_slide"]["regex"][0]["rx"] = "(?i)\\bnữ\\b"
(tmp / "bad2.json").write_text(json.dumps(bad, ensure_ascii=False))
r = run(S / "qp_render.py", "check", tmp / "bad2.json")
ok("check chặn \\b sát chữ có dấu (RE2)", r.returncode == 1 and "không dấu" in r.stdout, r.stdout)
Q = load_mod("qp_render")
ok("tô đỏ câu 'chưa xác nhận'", "<r>" in Q.mark_check("URL này chưa xác nhận bằng GSC."))
nc = json.loads(fx.read_text())
nc["measure"]["compare_date"] = ""
for x in nc["templates"]["items"]:
    x["ago"] = None
ok("check: không có mốc so sánh mà gắn 'Đang lan' là lỗi", any("status = up" in x for x in Q.check(json.loads(json.dumps(nc)))))
for x in nc["templates"]["items"]:
    x["status"] = "mid" if x["status"] == "up" else x["status"]
ok("check: template ago = null hợp lệ khi không có mốc so sánh", Q.check(json.loads(json.dumps(nc))) == [], str(Q.check(json.loads(json.dumps(nc)))[:3]))
ok("deck không mốc so sánh: chỉ ghi Top 10 hiện tại", "Top 10 hiện tại (chưa có mốc so sánh)" in Q.build_project(Q._mark(nc), False))
nc["measure"]["compare_date"] = "11/09/2026"
ok("check: có compare_date mà template ago trống là lỗi", any("ago trống" in x for x in Q.check(json.loads(json.dumps(nc)))))

# 2. qp_ranks: CSV giả lập 2 domain, 4 lần chạy, lần 2 thiếu dữ liệu
dates = ["09.10.2026 09:00", "08.10.2026 09:00", "07.10.2026 09:00", "10.09.2026 09:00"]
rows = [
    ("đèn học cho bé", {"denhoc.example": ["2", "", "3", "8"], "doithu.example": ["5", "", "6", "9"]}),
    ("đèn học chống cận", {"denhoc.example": ["9", "", "12", ">100"], "doithu.example": ["1", "", "2", "3"]}),
    ("đèn học led", {"denhoc.example": ["", "", "", ""], "doithu.example": ["4", "", "4", "4"]}),
    ("giá đèn học", {"denhoc.example": ["15", "", "11", "30"], "doithu.example": ["7", "", "7", "7"]}),
]
vols = {"đèn học cho bé": "1,300", "giá đèn học": "0"}
spyserp_csv(tmp / "demo.csv", dates, rows, vols=vols)
(tmp / "rules.json").write_text(json.dumps([{"id": "gia", "label": "giá [sp]", "rx": "^giá"}, {"id": "khac", "label": "khác", "rx": "."}], ensure_ascii=False))
(tmp / "kw.txt").write_text("đèn học cho bé\nđèn học chống cận\nđèn học led\ngiá đèn học\nđèn học kẹp bàn\n", encoding="utf-8")
base = ["--domain", "denhoc.example", "--engine", "GM1", "--rules", tmp / "rules.json", "--keywords", tmp / "kw.txt", "--k", "2"]
r = run(S / "qp_ranks.py", "table", tmp / "demo.csv", *base, "-o", tmp / "h.json")
ok("qp_ranks chạy", r.returncode == 0, r.stderr)
h = json.loads((tmp / "h.json").read_text())
ok("loại lần chạy thiếu dữ liệu", [x["valid"] for x in h["runs"]] == [True, False, True, True], str(h["runs"]))
ok("now = median 2 lần hợp lệ mới nhất", h["now_runs"] == ["09.10.2026 09:00", "07.10.2026 09:00"])
kw = {x["kw"]: x for x in h["keywords"]}
ok("median_high (2,3 → 3): hạng luôn là số nguyên có thật", kw["đèn học cho bé"]["now"] == 3, str(kw["đèn học cho bé"]))
ok("ngoài độ sâu = null, không phải 101", kw["đèn học led"]["now"] is None and kw["đèn học chống cận"]["ago"] is None)
ok("URL bỏ query string", kw["giá đèn học"]["url"] == "/den-hoc/")
ok("báo keyword thiếu trong export", h["not_in_export"] == ["đèn học kẹp bàn"])
ok("template: tổng nhóm = n", all(sum(t["now"].values()) == t["n"] for t in h["templates"]) and sum(t["n"] for t in h["templates"]) == 4)
ok("Top 10 now = 1 (median 12 nằm ngoài Top 10)", h["tops"]["now"]["10"] == 1, str(h["tops"]))
ok("đọc cột Volume (1,300 → 1300; 0 giữ là 0)", kw["đèn học cho bé"]["vol"] == 1300 and kw["giá đèn học"]["vol"] == 0, str(kw["đèn học cho bé"]))
ok("có mốc so sánh trong ±7 ngày", h["compare"] is True and h["ago_runs"] == ["10.09.2026 09:00"])

# 2b. file tải từ Google Sheets (dấu phẩy) cho cùng kết quả
spyserp_csv(tmp / "demo_comma.csv", dates, rows, sep=",", vols=vols)
r = run(S / "qp_ranks.py", "table", tmp / "demo_comma.csv", *base, "-o", tmp / "hc.json")
hc = json.loads((tmp / "hc.json").read_text()) if r.returncode == 0 else {}
ok("đọc CSV dấu phẩy (tải lại từ Google Sheets)", r.returncode == 0 and hc.get("tops") == h["tops"], r.stderr[-300:])

# 2c. export chia hai trang lịch: gộp hai file cho cùng kết quả
spyserp_csv(tmp / "p1.csv", dates[:2], [(k, {d: s[:2] for d, s in by.items()}) for k, by in rows], vols=vols)
spyserp_csv(tmp / "p2.csv", dates[2:], [(k, {d: s[2:] for d, s in by.items()}) for k, by in rows])
r = run(S / "qp_ranks.py", "table", tmp / "p2.csv", tmp / "p1.csv", *base, "-o", tmp / "hm.json")
hm = json.loads((tmp / "hm.json").read_text()) if r.returncode == 0 else {}
ok("gộp nhiều file export theo ngày", r.returncode == 0 and hm.get("tops") == h["tops"] and hm.get("now_runs") == h["now_runs"]
   and hm.get("ago_runs") == h["ago_runs"], r.stderr[-300:])

# 2d. không có lần chạy quanh mốc so sánh → dừng mã 2; --no-compare chạy tiếp, không có số mốc
spyserp_csv(tmp / "short.csv", dates[:3], [(k, {d: s[:3] for d, s in by.items()}) for k, by in rows])
r = run(S / "qp_ranks.py", "table", tmp / "short.csv", *base, "-o", tmp / "hs.json")
ok("thiếu mốc so sánh: dừng mã 2, in cách xử lý", r.returncode == 2 and "--no-compare" in r.stderr, r.stdout + r.stderr)
r = run(S / "qp_ranks.py", "table", tmp / "short.csv", *base, "--no-compare", "-o", tmp / "hs.json")
hs = json.loads((tmp / "hs.json").read_text()) if r.returncode == 0 else {}
ok("--no-compare: compare=false, ago null", r.returncode == 0 and hs.get("compare") is False and hs["tops"]["ago"] is None
   and all(t["ago"] is None for t in hs["templates"]), r.stderr[-300:])

# 2e. project một domain: lần chạy mới nhất nghi thiếu → dừng mã 3 (gate hỏi Lead)
d5 = ["12.10.2026 09:00", "11.10.2026 09:00", "10.10.2026 09:00", "09.10.2026 09:00", "12.09.2026 09:00"]
one = [(f"kw {i}", {"mot.example": (["", "4", "4", "5", "6"] if i < 8 else ["3", "4", "4", "5", "6"])}) for i in range(10)]
spyserp_csv(tmp / "one.csv", d5, one)
ob = ["--domain", "mot.example", "--engine", "GM1", "-o", tmp / "ho.json"]
r = run(S / "qp_ranks.py", "table", tmp / "one.csv", *ob)
ok("một domain: lần mới nhất nghi thiếu → dừng mã 3", r.returncode == 3 and "--keep-recent" in r.stderr, r.stdout + r.stderr)
r = run(S / "qp_ranks.py", "table", tmp / "one.csv", *ob, "--keep-recent")
ho = json.loads((tmp / "ho.json").read_text()) if r.returncode == 0 else {}
ok("--keep-recent: giữ lần mới nhất (site rơi thật)", r.returncode == 0 and ho.get("now_runs", [""])[0] == d5[0], r.stderr[-300:])
r = run(S / "qp_ranks.py", "table", tmp / "one.csv", *ob, "--drop", d5[0])
ho = json.loads((tmp / "ho.json").read_text()) if r.returncode == 0 else {}
ok("--drop: bỏ lần mới nhất (thiếu dữ liệu thật)", r.returncode == 0 and ho.get("now_runs", [""])[0] == d5[1], r.stderr[-300:])

# 2f. URL target theo kế hoạch: đếm keyword Google trả URL khác
(tmp / "targets.csv").write_text("keyword,url\ngiá đèn học,https://denhoc.example/gia-den-hoc/\nđèn học cho bé,/den-hoc/\n", encoding="utf-8")
r = run(S / "qp_ranks.py", "table", tmp / "demo.csv", *base, "--targets", tmp / "targets.csv", "-o", tmp / "ht.json")
ht = json.loads((tmp / "ht.json").read_text()) if r.returncode == 0 else {"targets": []}
tg = {t["url"]: t for t in ht["targets"]}
ok("--targets: bắt keyword lệch URL kế hoạch", tg.get("/gia-den-hoc", {}).get("other_url") == 1 and tg.get("/den-hoc", {}).get("match") == 1, str(ht["targets"]))

# 2g. lệnh bo: trích bộ cam kết từ cột của file sheet, lọc theo nhóm, bỏ trùng
(tmp / "kpi.csv").write_text("STT,Từ khóa,Nhóm\n1,Đèn học cho bé,Thúc đẩy\n2,giá đèn học,Duy trì\n3,đèn học cho bé,Thúc đẩy\n4,đèn học led,Thúc đẩy\n", encoding="utf-8")
r = run(S / "qp_ranks.py", "bo", tmp / "kpi.csv", "--where", "Nhóm=Thúc đẩy", "-o", tmp / "bo.txt")
ok("bo: trích cột Từ khóa, lọc nhóm, bỏ trùng", r.returncode == 0 and (tmp / "bo.txt").read_text().split("\n")[:2] == ["Đèn học cho bé", "đèn học led"], r.stdout + r.stderr)

# 3. terms: gợi ý cụm, bỏ phần đầu chung
r = run(S / "qp_ranks.py", "terms", tmp / "demo.csv", "--domain", "denhoc.example", "--engine", "GM1")
ok("terms chạy và tách phần đầu chung", r.returncode == 0 and "phần đầu chung" in r.stdout and "đèn học" in r.stdout, r.stdout + r.stderr)

# 4. scaffold: điền số, còn TODO; check chặn TODO
sc = tmp / "scaf.json"
r = run(S / "qp_scaffold.py", tmp / "h.json", "--slug", "demo", "--name", "Demo", "--domain", "denhoc.example", "--lead", "Lead", "--tabs", "gia,khac", "-o", sc)
ok("scaffold chạy", r.returncode == 0, r.stderr)
P = json.loads(sc.read_text())
ok("scaffold điền số từ bảng hạng", P["idea"]["n_kw"] == 4 and P["templates"]["items"][0]["n"] in (1, 3) and P["measure"]["depth"] == 50, str(P["idea"]) + str(P["measure"]))
ok("chip lấy median của bảng hạng", any(c["now"] == 3 for t in P["grid"]["tabs"] for c in t["chips"] if c["kw"] == "đèn học cho bé"))
ok("scaffold không viết tắt kw, S/M/L", " kw" not in json.dumps(P, ensure_ascii=False) and "S/M/L" not in json.dumps(P, ensure_ascii=False))
r = run(S / "qp_render.py", "check", sc)
ok("check chặn TODO", r.returncode == 1 and "còn TODO" in r.stdout)
r = run(S / "qp_scaffold.py", tmp / "h.json", "--slug", "demo", "--name", "Demo", "--domain", "x", "-o", sc)
ok("scaffold không ghi đè file đã có", r.returncode != 0)
r = run(S / "qp_scaffold.py", tmp / "h.json", "--slug", "demo", "--name", "Demo", "--domain", "x", "--tabs", "gia,sai", "-o", tmp / "t.json")
ok("scaffold báo rõ --tabs gõ sai", r.returncode != 0 and "sai" in (r.stderr + r.stdout) and "Traceback" not in r.stderr, r.stderr[-300:])
r = run(S / "qp_scaffold.py", tmp / "hs.json", "--slug", "demo", "--name", "Demo", "--domain", "x", "-o", tmp / "s2.json")
P2 = json.loads((tmp / "s2.json").read_text()) if r.returncode == 0 else {"templates": {"items": [{"status": "?"}]}, "measure": {"compare_date": "?"}}
ok("scaffold không mốc so sánh: không 'Đang lan', compare_date trống", r.returncode == 0 and P2["measure"]["compare_date"] == ""
   and all(x["status"] != "up" and x["ago"] is None and "→" not in x["note"] for x in P2["templates"]["items"]), r.stderr[-300:])
h17 = json.loads((tmp / "h.json").read_text())
h17["templates"] = [dict(h17["templates"][0], id=f"t{i}") for i in range(17)]
(tmp / "h17.json").write_text(json.dumps(h17, ensure_ascii=False))
r = run(S / "qp_scaffold.py", tmp / "h17.json", "--slug", "demo", "--name", "Demo", "--domain", "x", "-o", tmp / "s17.json")
ok("scaffold dừng khi quá 16 template (không cắt âm thầm)", r.returncode != 0 and "16" in (r.stderr + r.stdout))

# 5. verify: bắt hạng sai, keyword ngoài bộ, topic trùng, trạng thái và ghi chú lệch số
F = json.loads(fx.read_text())
Hd = json.loads((tmp / "h.json").read_text())
qb = load_mod("qp_build")
F["grid"]["tabs"][0]["chips"][0].update({"kw": "đèn học cho bé", "now": 7, "ago": None})
e, w = qb.verify(F, Hd, {"T1": ["giá đèn học", "đèn học led"], "T2": ["đèn học led"]})
ok("verify bắt hạng không khớp", any("đèn học cho bé" in x and "now = 7" in x for x in e), str(e[:5]))
ok("verify bắt keyword ngoài bộ", any("không có trong bộ" in x for x in e))
ok("verify bắt keyword thuộc hai topic", any("thuộc cả T1 và T2" in x for x in e))
ok("verify bắt n_kw lệch topics.json", any("priority.T1.n_kw" in x for x in e))
ok("verify bắt tổng n template khác số keyword", any("tổng n" in x for x in e))
F["grid"]["tabs"][0]["chips"][0].update({"now": 2})
e, w = qb.verify(F, Hd, None)
ok("verify: hạng một lần chạy chỉ là cảnh báo", not any("now = 2" in x for x in e) and any("now = 2" in x for x in w), str(w[:5]))
PS = json.loads(sc.read_text())
PS["templates"]["items"][0]["status"] = "up"
PS["templates"]["items"][0]["note"] = "Top 10: 0 → 5; hạng 11–20: 0"
PS["cover"]["rep_sub"] = "Từ khóa “đèn học cho bé” #9 theo đo mới nhất."
e, w = qb.verify(PS, Hd, None)
ok("verify bắt 'Đang lan' không khớp số", any("status = up" in x for x in e), str(e[:5]))
ok("verify bắt ghi chú Top 10 sai số", any(".note ghi Top 10 0 → 5" in x for x in e), str(e[:5]))
ok("verify cảnh báo hạng ghi trong chữ khác bảng hạng", any("ghi hạng 9" in x for x in w), str(w[:8]))
PS["measure"]["date"] = "01/01/2026"
e, w = qb.verify(PS, Hd, None)
ok("verify bắt measure.date lệch lần chạy", any("measure.date" in x for x in e))

# 6. bản web: quét chữ dễ lộ điều khoản; bàn giao content và bảng con số → nguồn
Fw = json.loads(fx.read_text())
Fw["plan"]["rows"][0]["task"] = "Chụp baseline trước kỳ nghiệm thu."
hits = qb.risky_scan(Fw)
ok("quét bản web bắt chữ 'nghiệm thu' ngoài khối kpi", any("nghiệm thu" in x for x in hits) and not any("Mốc mẫu" in x for x in hits), str(hits[:3]))
Fh = json.loads(fx.read_text())
md = qb.handoff(Fh, Hd, {"T1": ["giá đèn học"]}, "demo.json")
ok("bàn giao content có đủ mục và bảng tra keyword", all(s in md for s in ("## 2. Topic ưu tiên", "## 4. Trạm hỏng", "## 8. Tra keyword", "| giá đèn học | gia |"))
   and "Mốc mẫu" not in md, md[:300])
nb = qb.numbers(Fh, Hd, {"T1": ["giá đèn học"]}, "demo.json")
ok("bảng con số → nguồn có Top 3/5/10 và lần chạy bị loại", "Top 3/5/10 = 1/1/1" in nb and "lần chạy bị loại" in nb, nb[:400])

print(f"\n{len(FAIL)} ca hỏng" if FAIL else "\nTất cả ca PASS")
sys.exit(1 if FAIL else 0)
