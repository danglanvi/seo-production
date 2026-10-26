#!/usr/bin/env python3
"""Test offline cho lệnh rewrite của quality.py (không gọi Jev, không gọi mạng). Chạy: python3 -B -I tests/test_rewrite.py
Phần --embed chạy với encoder giả (SVI_FAKE=1) khi có venv EmbeddingGemma (SVI_PYTHON hoặc ~/.venvs/embeddinggemma).
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


def jev(id_, facts, p_loss, p_add):
    rest = round(1 - p_loss, 4)
    return {"id": id_, "answers": {"facts": {"choice": facts, "confidence": max(p_loss, rest),
                                             "probabilities": {"kept": rest, "dropped": p_loss, "changed": 0, "unknown": 0}},
                                   "added": {"p_yes": p_add}}}


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "skill").mkdir()
    shutil.copytree(SKILL / "scripts", t / "skill/scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(SKILL / "tasks", t / "skill/tasks")
    Q = t / "skill/scripts/quality.py"
    VER = json.loads((SKILL / "tasks/rewrite-keep.json").read_text(encoding="utf-8"))["version"]

    def run(*args, ok=True, py=sys.executable, env=None):
        r = subprocess.run([py, "-B", "-I", str(Q), *map(str, args)], capture_output=True, text=True, cwd=t, env=env)
        assert (r.returncode == 0) == ok, (args, r.stderr)
        return r

    pairs = [
        {"id": "p1", "url": "https://mau.vn/a/", "old": "Alpha là agency SEO hàng đầu Việt Nam, 6 năm kinh nghiệm.",
         "new": "Alpha là agency SEO & GEO với 10 năm kinh nghiệm."},
        {"id": "p2", "url": "https://mau.vn/a/", "old": "Alpha làm SEO tổng thể cho doanh nghiệp.",
         "new": "Alpha làm SEO tổng thể, hoàn tiền nếu không đạt KPI."},
        {"id": "p3", "url": "https://mau.vn/b/", "old": "Đội ngũ hơn 80 nhân sự của Alpha mặc đồng phục.",
         "new": "Đội ngũ Alpha mặc đồng phục."},
        {"id": "p4", "url": "https://mau.vn/b/", "old": "Bob, CEO của Alpha, chia sẻ về SEO.",
         "new": "Bob, CEO của Alpha và Co-founder Beta, chia sẻ về SEO."},
        {"id": "p5", "url": "https://mau.vn/b/", "old": "Alpha là đơn vị dẫn đầu kỷ nguyên GEO.",
         "new": "Alpha là đơn vị tiên phong kỷ nguyên GEO."},
        {"id": "p6", "url": "https://mau.vn/b/", "old": "Blog #1 về SEO tại Việt Nam.", "new": "Blog về SEO tại Việt Nam."},
        {"id": "p7", "url": "https://mau.vn/b/", "old": "Giống nhau", "new": "Giống nhau"},
    ]
    write(t / "pairs.jsonl", pairs)
    facts = [{"id": "alpha.years", "entity": "Alpha", "metric": "years_experience", "value": 10, "canon": "10 năm",
              "allowed": ["10 năm"], "banned": ["gần 10 năm"]},
             {"id": "bob.title", "entity": "Bob", "metric": "title", "value": None, "canon": "Co-founder Beta",
              "banned": ["Founder Beta"]}]
    json.dump(facts, open(t / "facts.json", "w"), ensure_ascii=False)

    # 1. Không model: luật tất định và input Jev (chỉ chữ cũ, chữ mới, trang)
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r0", "--facts", t / "facts.json", "--entity", "Alpha=Alpha",
        "--entity", "Bob=Bob")
    rows = {r["id"]: r for r in jl(t / "r0/rewrite.jsonl")}
    assert set(rows) == {"p1", "p2", "p3", "p4", "p5", "p6"}  # p7 không đổi chữ: bỏ
    assert rows["p2"]["decision"] == "chặn" and "hoàn tiền" in rows["p2"]["why"][0]
    assert rows["p1"]["checks"]["lost_num"] == [6.0] and rows["p1"]["checks"]["new_num_unknown"] == []  # "10 năm" có trong bảng fact
    assert rows["p3"]["checks"]["lost_num"] == [80.0]
    assert rows["p4"]["checks"]["new_banned"] == [] and rows["p4"]["decision"] != "chặn"  # "Co-founder Beta" không chạm "Founder Beta"
    assert rows["p6"]["checks"]["lost_num"] == []  # "#1" là cụm xếp hạng, không phải số
    # Không có --own-site (bản nháp site khách): không gửi Jev, Claude đọc mọi cặp
    assert jl(t / "r0/rw_jev_in.jsonl") == []
    assert all(r["decision"] != "an toàn" and "bản nháp site khách: Jev không đọc, Claude đọc" in r["why"] for r in rows.values())
    assert "không gửi Jev" in (t / "r0/report.md").read_text(encoding="utf-8")
    # Có --own-site (site của chính đơn vị vận hành): input Jev chỉ có chữ cũ, chữ mới, trang
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r0s", "--own-site", "--facts", t / "facts.json",
        "--entity", "Alpha=Alpha", "--entity", "Bob=Bob")
    assert all("chưa có nhãn Jev" in r["why"] for r in jl(t / "r0s/rewrite.jsonl"))
    ji = jl(t / "r0s/rw_jev_in.jsonl")
    assert len(ji) == 6 and set(ji[0]["state"]) == {"page", "old", "new"}

    # 2. Có nhãn Jev, chưa có cổng: cặp Jev không ghi kept thì Claude đọc
    write(t / "jev.jsonl", [jev("p1", "changed", 0.9, 0.99), jev("p2", "kept", 0.1, 0.99), jev("p3", "dropped", 0.95, 0.02),
                            jev("p4", "kept", 0.2, 0.95), jev("p5", "kept", 0.3, 0.02), jev("p6", "kept", 0.75, 0.02)])
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r1x", "--jev-out", t / "jev.jsonl", ok=False)  # site khách
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r1", "--own-site", "--facts", t / "facts.json",
        "--entity", "Alpha=Alpha", "--entity", "Bob=Bob", "--jev-out", t / "jev.jsonl")
    rows = {r["id"]: r for r in jl(t / "r1/rewrite.jsonl")}
    assert rows["p5"]["decision"] == "an toàn" and rows["p6"]["decision"] == "an toàn", rows["p6"]
    assert any("chưa có cổng" in w for w in rows["p1"]["why"])

    # 3. Có cổng registry: lọc dưới reject_below, Jev chọn dropped/changed vẫn đọc; added theo cổng confidence
    reg = {"entries": [{"rubric": "rewrite-keep", "version": VER, "question": "facts", "site": "mau.vn", "mode": "jev",
                        "threshold": None, "reject_below": 0.72},
                       {"rubric": "rewrite-keep", "version": VER, "question": "added", "site": "mau.vn", "mode": "jev",
                        "conf_gate": 0.85}]}
    json.dump(reg, open(t / "reg.json", "w"))
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r2", "--own-site", "--facts", t / "facts.json", "--entity", "Alpha=Alpha",
        "--entity", "Bob=Bob", "--jev-out", t / "jev.jsonl", "--registry", t / "reg.json", "--site", "mau.vn")
    rows = {r["id"]: r for r in jl(t / "r2/rewrite.jsonl")}
    assert rows["p6"]["decision"] == "cần đọc"  # P 0,75 ≥ 0,72
    assert rows["p5"]["decision"] == "an toàn"
    assert not any(w.startswith("Jev: thêm") for w in rows["p1"]["why"])  # số mới 10 khớp "10 năm" của bảng fact
    assert any(w.startswith("Jev: thêm") for w in rows["p4"]["why"])  # thêm tên, không có số giải thích
    rep = (t / "r2/report.md").read_text(encoding="utf-8")
    assert "lọc dưới 0.72 (site)" in rep and "chưa chạy" in rep

    # 4. --gsc cần --embed và --pages
    run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r3", "--gsc", t / "x.tsv", ok=False)

    # 5. --embed với encoder giả: query mang click, passage khớp nhất bị sửa thì ghi touched
    py = os.environ.get("SVI_PYTHON") or (str(VENV) if VENV.exists() else None)
    if py:
        shutil.copytree(SKILL.parent / "site-vector-index/scripts", t / "site-vector-index/scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        write(t / "pages.jsonl", [{"url": "https://mau.vn/a/", "text": "Alpha là agency SEO hàng đầu Việt Nam, 6 năm kinh nghiệm.\n"
                                                                      "Alpha làm SEO tổng thể cho doanh nghiệp."},
                                  {"url": "https://mau.vn/b/", "text": "Trang này không có cặp nào trùng chữ cũ."}])
        (t / "gsc.tsv").write_text("page\tquery\tclicks\timpressions\n/a/\tagency seo\t5\t50\n/a/\tseo tổng thể\t0\t9\n"
                                   "/b/\tđồng phục alpha\t3\t10\n", encoding="utf-8")
        env = dict(os.environ, SVI_FAKE="1")
        run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r4", "--embed", "--pages", t / "pages.jsonl",
            "--gsc", t / "gsc.tsv", py=py, env=env)
        qs = jl(t / "r4/queries.jsonl")
        assert [(q["url"], q["query"]) for q in qs if q["url"].endswith("/a/")] == [("https://mau.vn/a/", "agency seo")]  # bỏ query 0 click
        qa = next(q for q in qs if q["query"] == "agency seo")
        assert qa["touched"] and qa["status"] == ("query cần đọc" if qa["delta"] < 0 else "giữ")
        qb = next(q for q in qs if q["query"] == "đồng phục alpha")
        assert not qb["touched"] and qb["delta"] == 0 and qb["status"] == "giữ"
        assert all(r["drift"] is not None for r in jl(t / "r4/rewrite.jsonl"))
        reg["entries"].append({"rubric": "rewrite-query-drop", "site": "mau.vn", "mode": "cosine", "threshold": 0.5})
        json.dump(reg, open(t / "reg.json", "w"))
        run("rewrite", "--pairs", t / "pairs.jsonl", "--out-dir", t / "r5", "--embed", "--pages", t / "pages.jsonl",
            "--gsc", t / "gsc.tsv", "--registry", t / "reg.json", "--site", "mau.vn", py=py, env=env)
        assert all(q["status"] != "query cần đọc" for q in jl(t / "r5/queries.jsonl"))  # cosine giả lệch < 0,5
    else:
        print("bỏ qua --embed: không có venv EmbeddingGemma")
print("test_rewrite: đạt")
