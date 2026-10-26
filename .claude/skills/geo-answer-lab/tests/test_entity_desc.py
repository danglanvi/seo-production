#!/usr/bin/env python3
"""Test offline cho entity_desc.py (không gọi mạng, không gọi Jev). Chạy: python3 -B -I tests/test_entity_desc.py
Lệnh embed chạy với encoder giả (SVI_FAKE=1) khi có venv EmbeddingGemma (SVI_PYTHON hoặc ~/.venvs/embeddinggemma).
Script được chép vào thư mục tạm, nên test không đọc calibration-defaults.json thật."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
VENV = Path.home() / ".venvs/embeddinggemma/bin/python"


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def svc(id_, choice, pd):
    return {"id": id_, "answers": {"services": {"choice": choice, "confidence": max(pd, 1 - pd),
                                                "probabilities": {"different": pd, choice: max(pd, 1 - pd)}}}}


def claim(id_, subject, metric, cs=0.99, cm=0.99):
    return {"id": id_, "answers": {"subject": {"choice": subject, "confidence": cs}, "metric": {"choice": metric, "confidence": cm}}}


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "skill").mkdir()
    shutil.copytree(SKILL / "scripts", t / "skill/scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(SKILL / "tasks", t / "skill/tasks")
    ED = t / "skill/scripts/entity_desc.py"
    VER = json.loads((SKILL / "tasks/entity-desc.json").read_text(encoding="utf-8"))["version"]

    def run(*args, ok=True, py=sys.executable, env=None):
        r = subprocess.run([py, "-B", "-I", str(ED), *map(str, args)], capture_output=True, text=True, cwd=t, env=env)
        assert (r.returncode == 0) == ok, (args, r.stderr)
        return r

    # 1. Đọc HTML: bỏ nav/footer, lấy meta, JSON-LD, mục dưới heading có tên brand và khối có nhắc brand
    sys.path.insert(0, str(t / "skill/scripts"))
    import entity_desc as ed  # noqa: E402
    cfg = {"own": "Alpha", "brands": {"Alpha": {"regex": r"\balpha\b", "aliases": ["Alpha Agency"]}}}
    rx = ed.brand_rx(cfg)
    page = ('<html><head><meta name="description" content="Alpha là agency SEO và GEO tại Việt Nam từ 2016.">'
            '<script type="application/ld+json">{"@type":"Organization","name":"Alpha","description":"Alpha làm SEO tổng thể cho doanh nghiệp."}</script>'
            '</head><body><nav><p>Alpha trong menu không được lấy vì nằm trong nav</p></nav>'
            '<h2>1. Alpha</h2><p>Đơn vị này cung cấp dịch vụ SEO tổng thể và đào tạo SEO.</p><ul><li>Thiết kế website chuẩn SEO cho doanh nghiệp.</li></ul>'
            '<h2>2. Beta</h2><p>Beta làm quảng cáo và truyền thông, không liên quan brand chính.</p>'
            '<p>Một đoạn khác nói Alpha là Inbound Marketing Agency hàng đầu.</p>'
            '<footer><p>Alpha ở footer không được lấy vì nằm trong footer</p></footer></body></html>')
    ps = ed.passages_from_html(page, rx, 12)
    texts = [p["text"] for p in ps]
    assert texts[0].startswith("Alpha là agency SEO") and ps[0]["section"] == "meta description", ps
    assert "Alpha làm SEO tổng thể cho doanh nghiệp." in texts
    assert "Thiết kế website chuẩn SEO cho doanh nghiệp." in texts  # khối dưới heading có brand, không nêu tên brand
    assert not any("Beta làm quảng cáo" in x or "menu" in x or "footer" in x for x in texts), texts
    assert any("Inbound Marketing Agency" in x for x in texts)
    assert ed.value("4.700 học viên") == 4700 and ed.value("1,5 triệu lượt") == 1_500_000 and ed.value("80k người") == 80000

    # 2. collect không mạng: sources rỗng, đoạn dán tay và câu trả lời AI
    (t / "sources.tsv").write_text("url\tkind\n", encoding="utf-8")
    json.dump(cfg, open(t / "brands.json", "w"))
    (t / "paste").mkdir()
    (t / "paste/linkedin__alpha.txt").write_text("https://linkedin.example/alpha\nAlpha là công ty SEO, thành lập năm 2015, có 80 nhân sự.\n",
                                                 encoding="utf-8")
    write(t / "raw.jsonl", [{"ok": True, "prompt_id": "P1", "engine": "gemini", "run": 1,
                             "answer": "Mở đầu không có tên.\n\n**Alpha** là [agency SEO và Digital Marketing](https://x.vn) với 400 dự án."}])
    run("collect", "--sources", t / "sources.tsv", "--brands", t / "brands.json", "--out", t / "passages.jsonl",
        "--raw", t / "raw.jsonl", "--paste-dir", t / "paste")
    got = jl(t / "passages.jsonl")
    assert [p["kind"] for p in got] == ["linkedin", "ai:gemini"], got
    assert got[1]["text"] == "Alpha là agency SEO và Digital Marketing với 400 dự án." and got[1]["id"] == "ai|P1|gemini|1|1.0"

    # 3. prepare: một dòng entity-desc mỗi đoạn, số và năm được đánh dấu cho company-fact-claim
    (t / "canon.txt").write_text("Alpha là agency SEO và GEO tại Việt Nam, hoạt động từ 2016.", encoding="utf-8")
    run("prepare", "--passages", t / "passages.jsonl", "--brands", t / "brands.json", "--canon", t / "canon.txt", "--out-dir", t)
    si, ci, cx = jl(t / "services_in.jsonl"), jl(t / "claims_in.jsonl"), jl(t / "claims_index.jsonl")
    assert len(si) == 2 and si[0]["state"]["brand"] == "Alpha" and si[0]["state"]["aliases"] == ["Alpha Agency"]
    assert sorted(c["match"] for c in cx) == ["400 dự án", "80 nhân sự", "thành lập năm 2015"], cx
    assert all("⟦" in c["state"]["snippet"] and "site_profile" in c["state"] for c in ci)

    # 4. gold-sheet: --enrich lấy nửa mẫu từ đoạn khớp regex, --skip loại id đã gán, chưa có nhãn
    pool = [{"id": f"w{i}", "url": f"https://x.vn/{i}", "kind": "toplist", "text": f"Alpha đoạn web {i}"} for i in range(20)]
    pool += [{"id": f"a{i}", "url": "ai:chatgpt", "kind": "ai:chatgpt", "text": f"Alpha đoạn AI {i}"} for i in range(20)]
    pool += [{"id": f"r{i}", "url": "https://y.vn", "kind": "toplist", "text": f"Alpha làm Inbound Marketing {i}"} for i in range(6)]
    write(t / "pool.jsonl", pool)
    (t / "skip.txt").write_text("r0\nw0\n", encoding="utf-8")
    run("gold-sheet", "--passages", t / "pool.jsonl", "--n", "10", "--seed", "3", "--skip", t / "skip.txt", "--enrich", "inbound",
        "--out", t / "sheet.jsonl")
    sh = jl(t / "sheet.jsonl")
    assert len(sh) == 10 and sum(r["id"].startswith("r") for r in sh) == 5 and not {"r0", "w0"} & {r["id"] for r in sh}
    assert all(r["services"] is None for r in sh)

    # 5. report: so số với facts.json, cụm cấm, cổng entity-desc theo registry
    d = t / "run"
    d.mkdir()
    P = [{"id": "ai|P1|gemini|1|0.0", "url": "ai:gemini", "kind": "ai:gemini", "text": "Alpha là agency SEO và Digital Marketing, 400 dự án, từ 2015."},
         {"id": "https://y.vn#0", "url": "https://y.vn", "kind": "toplist", "text": "Alpha làm SEO tổng thể, đã làm 600 dự án và 500+ dự án."},
         {"id": "https://y.vn#1", "url": "https://y.vn", "kind": "toplist", "text": "Alpha làm SEO và GEO cho doanh nghiệp lớn."},
         {"id": "https://y.vn#2", "url": "https://y.vn", "kind": "toplist", "text": "Alpha làm SEO kỹ thuật, có 2 văn phòng."},
         {"id": "https://y.vn#3", "url": "https://y.vn", "kind": "toplist", "text": "Liên hệ Alpha: 0900 000 000."}]
    write(t / "p.jsonl", P)
    facts = [{"id": "alpha.seo_projects", "entity": "Alpha", "metric": "seo_projects", "value": 550, "canon": "550+ dự án",
              "banned": ["500+ dự án"]},
             {"id": "alpha.clients", "entity": "Alpha", "metric": "clients", "value": 550, "canon": "550+ doanh nghiệp",
              "banned": ["500+ dự án"]},
             {"id": "alpha.founding_year", "entity": "Alpha", "metric": "founding_year", "value": 2016, "canon": "từ 2016"},
             {"id": "bob.community", "entity": "Bob", "metric": "community", "value": 1000, "canon": "1.000+ thành viên"}]
    json.dump(facts, open(t / "facts.json", "w"), ensure_ascii=False)
    write(d / "services_out.jsonl", [svc(P[0]["id"], "different", 0.95), svc(P[1]["id"], "consistent", 0.1),
                                     svc(P[2]["id"], "consistent", 0.85), svc(P[3]["id"], "different", 0.3),
                                     svc(P[4]["id"], "not_described", 0.01)])
    write(d / "claims_index.jsonl", [{"id": "c1", "passage_id": P[0]["id"], "match": "400 dự án"},
                                     {"id": "c2", "passage_id": P[0]["id"], "match": "từ 2015"},
                                     {"id": "c3", "passage_id": P[1]["id"], "match": "600 dự án"},
                                     {"id": "c4", "passage_id": P[1]["id"], "match": "500+ dự án"},
                                     {"id": "c5", "passage_id": P[3]["id"], "match": "2 văn phòng"}])
    write(d / "claims_out.jsonl", [claim("c1", "company", "seo_projects"), claim("c2", "company", "founding_year"),
                                   claim("c3", "company", "seo_projects"), claim("c4", "other_company", "seo_projects"),
                                   claim("c5", "company", "staff", cs=0.4)])
    write(d / "cos.jsonl", [{"id": p["id"], "cos": 0.8 + k / 100} for k, p in enumerate(P)])

    def report(reg_entry):
        args = ["report", "--passages", t / "p.jsonl", "--facts", t / "facts.json", "--dir", d, "--entity", "Alpha", "--founder", "Bob"]
        if reg_entry is not None:
            json.dump({"entries": [dict(reg_entry, rubric="entity-desc", version=VER, question="services", site="y.vn")]},
                      open(t / "reg.json", "w"))
            args += ["--registry", t / "reg.json", "--site", "y.vn"]
        run(*args)
        rows = (d / "issues.tsv").read_text(encoding="utf-8").splitlines()[1:]
        return [r.split("\t") for r in rows], json.loads((d / "summary.json").read_text(encoding="utf-8"))

    rows, sm = report({"threshold": None, "reject_below": 0.8})
    types = sorted(r[0] for r in rows)
    assert types == ["cách viết cấm", "lệch hoặc cũ", "lệch năm", "mô tả cần đọc", "mô tả cần đọc", "mô tả cần đọc", "nói quá",
                     "số cần đọc"], types
    read = {r[2]: r[6] for r in rows if r[0] == "mô tả cần đọc" and r[2] != "https://y.vn"}
    assert "ai|P1|gemini|1|0.0" in read  # câu trả lời AI ghi id để tìm lại trong raw.jsonl
    flagged = [r[7] for r in rows if r[0] == "mô tả cần đọc"]
    assert P[2]["text"] in flagged and P[3]["text"] in flagged and P[1]["text"] not in flagged  # P 0,1 bị lọc; Jev chọn different thì vẫn đọc
    assert sm["gate_services"] == {"accept": None, "reject_below": 0.8, "source": "site"}
    assert sum(r[0] == "cách viết cấm" for r in rows) == 1  # cùng cụm cấm ở 2 fact: ghi một lần
    md = (d / "entity_report.md").read_text(encoding="utf-8")
    assert md.index("lệch năm") < md.index("mô tả cần đọc |") and "0.95" in md.split("mô tả cần đọc |")[1].split("\n")[0]

    rows, _ = report({"threshold": 0.9, "reject_below": 0.8})  # có cổng tự chốt
    assert [r[7] for r in rows if r[0] == "mô tả dịch vụ lệch"] == [P[0]["text"]]

    rows, sm = report(None)  # chưa có cổng: mọi đoạn có mô tả (consistent, different) Claude đọc
    assert sum(r[0] == "mô tả cần đọc" for r in rows) == 4 and sm["gate_services"]["source"] is None
    assert all("chưa có cổng" in r[6] for r in rows if r[0] == "mô tả cần đọc")
    assert [s["cos_mean"] for s in sm["by_source"]] == [0.8, 0.825]  # nguồn cosine thấp xếp trước

    (d / "cos.jsonl").unlink()  # máy không có Gemma: report vẫn chạy, không có cosine
    rows, sm = report(None)
    assert {s["cos_mean"] for s in sm["by_source"]} == {None} and len(rows) == 9

    # 6. embed với encoder giả: đoạn trùng chữ canon có cosine 1
    py = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else None)
    if py:
        shutil.copytree(SKILL.parent / "site-vector-index/scripts", t / "site-vector-index/scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        write(t / "e.jsonl", [{"id": "x", "url": "u", "kind": "about", "text": (t / "canon.txt").read_text(encoding="utf-8")},
                              {"id": "y", "url": "u", "kind": "about", "text": "Chữ khác hẳn"}])
        run("embed", "--passages", t / "e.jsonl", "--canon", t / "canon.txt", "--out", t / "cos.jsonl", py=py,
            env=dict(os.environ, SVI_FAKE="1"))
        c = {r["id"]: r["cos"] for r in jl(t / "cos.jsonl")}
        assert abs(c["x"] - 1) < 1e-3 and c["y"] < 0.99, c
    else:
        print("bỏ qua embed: không có venv EmbeddingGemma")
print("test_entity_desc: đạt")
