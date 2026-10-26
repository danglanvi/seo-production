#!/usr/bin/env python3
"""Test offline cho lệnh claims của quality.py: regex lớp 1, tách câu, facts.json, kết quả Jev và Gemma giả, cổng registry.
Không gọi mạng, không cần model. Chạy: python3 -I tests/test_claims.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.dont_write_bytecode = True  # không sinh __pycache__ trong thư mục skill (mirror sync sẽ chép theo)
sys.path.insert(0, str(SCRIPTS))
import quality as q  # noqa: E402

Q = SCRIPTS / "quality.py"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-I", str(Q), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, p.stderr
    return p


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def labels(text):
    return {h["label"] for h in q.l1_hits(text) if not h["neg"]}


# 1. Regex lớp 1: cụm rõ, phủ định, số có dấu chấm.
assert labels("Chúng tôi hoàn phí nếu không đạt KPI.") == {"hoàn tiền"}
assert labels("Cam kết Top 10 các từ khoá.") == {"cam kết kết quả"}
assert labels("Bảo hành 3 tháng sau nghiệm thu.") == {"cam kết kết quả"}
assert labels("Website của bạn là nguồn trích dẫn số 1.") == {"#1"}  # dấu chấm cuối câu vẫn tính
assert labels("Agency #1 Việt Nam") == {"#1"} and labels("Top 1 Google") == {"#1"}
assert not labels("Văn phòng: Số 128, Đường số 7.") and not labels("Đạt 1.000 traffic, số 1.5 lần.")
assert not labels("Từ khoá lên top 1-5 sau 3 tháng")
assert labels("đơn vị hàng đầu") == {"hàng đầu"} and labels("dịch vụ tốt nhất") == {"tốt nhất"}
neg = q.l1_hits("Chúng tôi không cam kết top 3 cho từ khoá khó.")
assert neg and all(h["neg"] for h in neg), neg

# 2. Tách câu, ô đếm, số.
assert q.split_sentences("500+ ¶ Dự án đã làm. Câu hai rất ngắn.") == ["500+ Dự án đã làm.", "Câu hai rất ngắn."]
assert q.nums("1.000 traffic, 4,5 triệu, 3.000+ học viên") == {1000.0, 4500000.0, 3000.0}
long = " ".join(["chữ"] * 30) + " cam kết top 10 " + " ".join(["chữ"] * 30)
w = q.windows(long)
assert len(w) == 1 and "cam kết top 10" in w[0] and w[0].startswith("… "), w

# 3. Hàm decide: thứ tự luật.
D = q.decide
assert D({"l1": [], "jev": {"guarantee": "yes"}})[0] == "người đọc"
assert D({"l1": [], "jev": {"guarantee": "review"}}) == ("người đọc", ["Jev dưới cổng: guarantee"])
assert D({"l1": [{"label": "hoàn tiền", "neg": False}], "jev": {"guarantee": "no", "subject": "other_company"}})[0] == "giữ"
assert D({"l1": [], "fact": {"status": "lệch", "band": "nhận", "why": "x", "entity_note": ""}})[0] == "sửa theo fact"
assert D({"l1": [], "fact": {"status": "lệch", "band": "nhận", "why": "x", "entity_note": "lệch entity"}})[0] == "người đọc"
assert D({"l1": [], "jev": {"self_superlative": "yes", "subject": "owner"}})[0] == "xoá"
assert D({"l1": [], "jev": {"self_superlative": "yes", "subject": "client"}})[0] == "giữ"
assert D({"l1": [{"label": "tốt nhất", "neg": False}]})[0] == "người đọc"  # chưa chạy Jev
assert D({"l1": [], "jev": {"unsourced_stat": "yes"}})[0] == "thêm nguồn"

# 4. Lệnh claims đầu cuối với facts.json, Jev và Gemma giả.
S = {
    "s1": "Alpha SEO cam kết Top 10 các từ khoá.",
    "s2": "Chúng tôi hoàn phí nếu không đạt KPI.",
    "s3": "Alpha SEO có 80+ nhân sự.",
    "s4": "Alpha SEO là agency số 1.",
    "s5": "Không cam kết top 3 cho từ khoá khó.",
    "s6": "Văn phòng: Số 128, Đường số 7.",
    "s7": "Theo khảo sát, 75% người dùng không xem trang 2.",
    "s8": "Alpha SEO đã đào tạo 3.000 học viên.",
    "s9": "Beta Academy có 9.000 học viên.",
    "s10": "Beta Academy có 3000+ học viên.",
    "s11": "Alpha SEO có 3000+ học viên.",
    "s12": "Alpha SEO có 60 dự án.",
    "s13": "Alpha SEO có 7.000 học viên.",
    "s14": "Alpha SEO bảo đảm website lên trang nhất.",
    "s15": "Khách Gamma là thương hiệu hàng đầu.",
}
ID = {k: q.sid(v) for k, v in S.items()}
F = [
    {"id": "alp.staff", "entity": "ALP", "metric": "staff", "value": 40, "canon": "40+ nhân sự", "allowed": ["40+ nhân sự"],
     "banned": ["80+ nhân sự"], "decided": "2026-10-17", "decided_by": "chủ site", "quote": "", "source": "test"},
    {"id": "alp.students", "entity": "ALP", "metric": "students", "value": 5000, "canon": "5.000+ học viên",
     "allowed": ["5.000+ học viên"], "banned": [], "decided": "2026-10-17", "decided_by": "chủ site", "quote": "", "source": "test"},
    {"id": "bta.students", "entity": "BTA", "metric": "students", "value": 500, "canon": "500+ học viên", "allowed": [],
     "banned": ["3000+ học viên"], "decided": "2026-10-17", "decided_by": "chủ site", "quote": "", "source": "test"},
]


def cg(g=0.05, s=0.05, u=0.05, subj="owner", c=0.95):
    return {"guarantee": {"p_yes": g}, "self_superlative": {"p_yes": s}, "unsourced_stat": {"p_yes": u},
            "subject": {"choice": subj, "confidence": c}}


JEV = {"s1": cg(g=0.95), "s4": cg(s=0.95), "s5": cg(g=0.1, subj="general", c=0.9), "s7": cg(u=0.95, subj="general", c=0.9),
       "s14": cg(g=0.5), "s15": cg(s=0.9, subj="client", c=0.9)}
NN = {"s8": [("alp.students", 0.9)], "s9": [("alp.students", 0.88), ("bta.students", 0.87)], "s12": [("alp.students", 0.86)],
      "s13": [("alp.students", 0.9)], "s6": [("alp.staff", 0.7)]}


def fm(choice, conf, none):
    return {"fact": {"choice": choice, "confidence": conf, "probabilities": {"none": none, choice: conf}}}


FJ = {"s8": fm("alp.students", 0.9, 0.02), "s9": fm("alp.students", 0.9, 0.05), "s12": fm("none", 0.9, 0.9),
      "s13": fm("alp.students", 0.6, 0.1)}
REG = {"entries": [
    *({"rubric": "claim-guard", "version": "t1", "mode": "jev", "site": "mau.vn", "question": k, "conf_gate": v}
      for k, v in (("guarantee", 0.75), ("self_superlative", 0.85), ("unsourced_stat", 0.8), ("subject", 0.85))),
    {"rubric": "fact-check", "version": "1", "mode": "cosine", "site": "mau.vn", "reject_below": 0.82},
    {"rubric": "fact-match", "version": "f1", "mode": "jev", "site": "mau.vn", "question": "fact", "positive": "none",
     "conf_gate": 0.8, "threshold": 0.35}]}

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "page.txt").write_text(" ".join(S.values()), encoding="utf-8")
    write(t / "page.jsonl", [{"url": "https://mau.vn/a/", "text": " ".join(S.values())}])
    (t / "facts.json").write_text(json.dumps(F, ensure_ascii=False), encoding="utf-8")
    (t / "reg.json").write_text(json.dumps(REG), encoding="utf-8")
    (t / "reg0.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
    common = ["--owner", "Alpha SEO", "--facts", t / "facts.json",
              "--entity", "ALP=Alpha SEO|ALP", "--entity", "BTA=Beta Academy|BTA", "--site-entity", "ALP", "--site", "mau.vn"]
    base = ["claims", "--rows", t / "page.jsonl", *common]
    # 4a. Chưa có model: regex + cụm cấm của bảng fact.
    run(*base, "--out-dir", t / "o0")
    sent = {r["id"] for r in jl(t / "o0/jev_in.jsonl")}
    assert {ID[k] for k in ("s1", "s2", "s4", "s14", "s15")} <= sent and ID["s6"] not in sent
    assert ID["s8"] in {r["id"] for r in jl(t / "o0/fact_q.jsonl")} and len(jl(t / "o0/fact_d.jsonl")) == 3
    r0 = {s["sid"]: s for s in jl(t / "o0/claims.jsonl")}
    assert r0[ID["s3"]]["de_xuat"] == "sửa theo fact" and r0[ID["s3"]]["fact"]["band"] == "cụm cấm"
    assert r0[ID["s10"]]["de_xuat"] == "sửa theo fact"  # cụm cấm của BTA, câu nêu BTA
    assert not r0[ID["s11"]].get("fact")  # cụm cấm của BTA không áp cho câu nêu ALP
    assert r0[ID["s4"]]["de_xuat"] == "người đọc" and r0[ID["s2"]]["de_xuat"] == "người đọc"
    # 4b. Ghép Jev: thiếu cổng thì dừng; đủ cổng thì áp nhãn.
    write(t / "jev.jsonl", [{"id": ID[k], "task_version": "t1", "answers": v} for k, v in JEV.items()])
    write(t / "nn.jsonl", [{"id": ID[k], "top": [{"id": i, "cos": c} for i, c in v]} for k, v in NN.items()])
    write(t / "fj.jsonl", [{"id": ID[k], "task_version": "f1", "answers": v} for k, v in FJ.items()])
    run(*base, "--out-dir", t / "o1", "--jev-out", t / "jev.jsonl", "--registry", t / "reg0.json", ok=False)
    run(*base, "--out-dir", t / "o2", "--jev-out", t / "jev.jsonl", "--fact-nn", t / "nn.jsonl", "--fact-jev-out", t / "fj.jsonl",
        "--registry", t / "reg.json")
    r = {s["sid"]: s for s in jl(t / "o2/claims.jsonl")}
    d = {k: r[ID[k]]["de_xuat"] for k in S}
    assert d["s1"] == "người đọc" and "cam kết" in r[ID["s1"]]["notes"][0]
    assert d["s4"] == "xoá" and d["s5"] == "giữ" and d["s7"] == "thêm nguồn" and d["s15"] == "giữ", d
    assert d["s14"] == "người đọc" and r[ID["s14"]]["notes"] == ["Jev dưới cổng: guarantee"]
    assert d["s8"] == "sửa theo fact" and r[ID["s8"]]["fact"]["band"] == "nhận", r[ID["s8"]]
    assert d["s9"] == "người đọc" and "lệch entity" in r[ID["s9"]]["fact"]["entity_note"]
    assert d["s12"] == "giữ" and not r[ID["s12"]].get("fact")  # Jev: không fact nào cùng chỉ số
    assert d["s13"] == "người đọc" and r[ID["s13"]]["fact"]["band"] == "xám"
    assert not r[ID["s6"]].get("fact")  # dưới sàn cosine
    fin = {x["id"]: x for x in jl(t / "o2/fact_jev_in.jsonl")}
    assert set(fin) == {ID[k] for k in ("s8", "s9", "s12", "s13")} and "none" in fin[ID["s8"]]["criteria"]["fact"]
    tsv = (t / "o2/claims.tsv").read_text(encoding="utf-8").splitlines()
    assert tsv[0].split("\t") == ["cau", "url", "so_trang", "lop", "nhan", "p", "fact", "de_xuat", "ghi_chu"]
    order = [line.split("\t")[7] for line in tsv[1:]]
    assert order == sorted(order, key=q.ORDER.index), order
    rep = (t / "o2/report.md").read_text(encoding="utf-8")
    assert "cổng guarantee 0.75 (site)" in rep and "sàn cosine 0.82 (site)" in rep
    # 4c. Bản nháp site khách (--text, không --own-site): không gửi Jev, câu chạm dấu hiệu chuyển Claude đọc.
    draft = ["claims", "--text", t / "page.txt", "--url", "https://mau.vn/a/", *common]
    run(*draft, "--out-dir", t / "o3", "--jev-out", t / "jev.jsonl", "--registry", t / "reg.json", ok=False)
    run(*draft, "--out-dir", t / "o3", "--fact-jev-out", t / "fj.jsonl", "--registry", t / "reg.json", ok=False)
    run(*draft, "--out-dir", t / "o3", "--fact-nn", t / "nn.jsonl", "--registry", t / "reg.json")
    assert jl(t / "o3/jev_in.jsonl") == [] and jl(t / "o3/fact_jev_in.jsonl") == []
    r3 = {s["sid"]: s for s in jl(t / "o3/claims.jsonl")}
    assert r3[ID["s3"]]["de_xuat"] == "sửa theo fact" and r3[ID["s15"]]["de_xuat"] == "người đọc"
    assert "không gửi Jev" in (t / "o3/report.md").read_text(encoding="utf-8")
    # 4d. Bản nháp site của chính đơn vị vận hành (--own-site): gửi Jev như trang đã đăng.
    own = [*draft, "--own-site"]
    run(*own, "--out-dir", t / "o4", "--fact-nn", t / "nn.jsonl", "--registry", t / "reg.json")
    assert {r["id"] for r in jl(t / "o4/jev_in.jsonl")} == sent
    assert {x["id"] for x in jl(t / "o4/fact_jev_in.jsonl")} == set(fin)
    assert "--own-site" in (t / "o4/report.md").read_text(encoding="utf-8")
    run(*own, "--out-dir", t / "o5", "--jev-out", t / "jev.jsonl", "--fact-nn", t / "nn.jsonl", "--fact-jev-out", t / "fj.jsonl",
        "--registry", t / "reg.json")
    r5 = {s["sid"]: s for s in jl(t / "o5/claims.jsonl")}
    assert {k: r5[ID[k]]["de_xuat"] for k in S} == d
print("test_claims: đạt")
