#!/usr/bin/env python3
"""Test offline cho prepare.py và report.py (không gọi API). Chạy: python3 -I tests/test_geo_answer.py"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "scripts"


def run(script, *args, ok=True):
    r = subprocess.run([sys.executable, "-I", str(S / script), *map(str, args)], capture_output=True, text=True)
    assert (r.returncode == 0) == ok, (script, r.stdout, r.stderr)
    return r


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "prompts.tsv").write_text("id\tfunnel\tbranded\ttopic\tprompt\n"
                                   "P1\tBOFU\tno\tx\tCông ty SEO nào uy tín?\n"
                                   "P2\tBOFU\tyes\tx\tAlpha có uy tín không?\n", encoding="utf-8")
    (t / "brands.json").write_text(json.dumps({"own": "Alpha", "own_domains": ["alpha.vn"], "brands": {
        "Alpha": {"regex": r"\balpha\b", "aliases": ["alpha.vn"]},
        "Beta": {"regex": r"\bbeta\b", "aliases": []}}}), encoding="utf-8")
    write(t / "raw.jsonl", [
        {"prompt_id": "P1", "engine": "e1", "run": 1, "ok": True, "answer": "Nên xem Beta trước, sau đó Alpha.",
         "citations": [{"url": "https://www.alpha.vn/dich-vu?utm_source=x", "title": ""},
                       {"url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc", "title": "beta.vn"}]},
        {"prompt_id": "P1", "engine": "e1", "run": 2, "ok": True, "answer": "Chỉ có Beta.", "citations": []},
        {"prompt_id": "P1", "engine": "e1", "run": 3, "ok": False, "error": "http_500"},
        {"prompt_id": "P2", "engine": "e1", "run": 1, "ok": True, "answer": "Alpha có case study, nhưng review do Alpha tự đăng.",
         "citations": []}])
    w = t / "w"
    run("prepare.py", "--raw", t / "raw.jsonl", "--prompts", t / "prompts.tsv", "--brands", t / "brands.json", "--out-dir", w)
    det = {r["id"]: r for r in jl(w / "det.jsonl")}
    assert len(det) == 6, len(det)  # 3 câu trả lời hợp lệ × 2 brand
    assert det["P1|e1|1|Beta"]["mention_order"] == 1 and det["P1|e1|1|Alpha"]["mention_order"] == 2
    assert det["P1|e1|2|Alpha"]["regex_mention"] is False
    assert det["P2|e1|1|Alpha"]["named_in_question"] and not det["P2|e1|1|Beta"]["named_in_question"]
    jin = jl(w / "jev_in.jsonl")
    assert {r["id"] for r in jin} == {"P1|e1|1|Alpha", "P1|e1|1|Beta", "P1|e1|2|Beta", "P2|e1|1|Alpha"}
    cites = {c["answer_id"]: c for c in jl(w / "citations.jsonl")}
    assert cites["P1|e1|1"]["own_cited"] and [d["domain"] for d in cites["P1|e1|1"]["domains"]] == ["alpha.vn", "beta.vn"]

    def ans(role, rc, proof, pc, obj):
        return {"role": {"choice": role, "confidence": rc}, "proof": {"choice": proof, "confidence": pc},
                "objection": {"p_yes": obj}}
    write(w / "jev_out.jsonl", [
        {"id": "P1|e1|1|Alpha", "answers": ans("recommended", 0.9, "self_description", 0.9, 0.1), "task_version": "v-test"},
        {"id": "P1|e1|1|Beta", "answers": ans("recommended", 0.95, "third_party", 0.4, 0.5), "task_version": "v-test"},
        {"id": "P1|e1|2|Beta", "answers": ans("recommended", 0.9, "third_party", 0.9, 0.9), "task_version": "v-test"},
        {"id": "P2|e1|1|Alpha", "answers": ans("subject", 0.9, "named_results", 0.9, 0.95), "task_version": "v-test"}])
    run("prepare.py", "--raw", t / "raw.jsonl", "--prompts", t / "prompts.tsv", "--brands", t / "brands.json",
        "--out-dir", w, "--jev-out", w / "jev_out.jsonl")
    assert {r["id"] for r in jl(w / "glm_in.jsonl")} == {"P1|e1|1|Beta", "P1|e1|2|Beta", "P2|e1|1|Alpha"}
    write(w / "glm_out.jsonl", [{"id": "P2|e1|1|Alpha", "quotes": [{"text": "review do Alpha tự đăng", "tag": "proof_doubt"}]}])

    # chưa có cổng cho version này: dừng
    run("report.py", "--dir", w, "--brands", t / "brands.json", ok=False)
    reg = {"entries": [{"rubric": "ai-answer-brand", "version": "v-test", "site": "alpha.vn", "question": q, "conf_gate": g}
                       for q, g in (("role", 0.5), ("proof", 0.5), ("objection", 0.7))]}
    (t / "reg.json").write_text(json.dumps(reg), encoding="utf-8")
    run("report.py", "--dir", w, "--brands", t / "brands.json", "--registry", t / "reg.json", "--site", "alpha.vn")
    rep = json.loads((w / "report.json").read_text(encoding="utf-8"))
    a, b = rep["brands"]["Alpha|all"], rep["brands"]["Beta|all"]
    assert a["pairs"] == 2 and a["mention_rate"] == 0.5 and a["recommended_rate"] == 0.5  # P2 nêu tên Alpha: không tính
    assert b["pairs"] == 3 and b["mention_rate"] == round(2 / 3, 3) and b["first_of_mentioned"] == 1.0
    assert b["third_party_of_mentioned"] == 0.5 and b["review_items"] == 2  # proof 0,4 và objection 0,5 dưới cổng
    assert rep["own"]["answers_citing_own_domain"] == 1 and rep["own"]["objections_by_tag"] == {"proof_doubt": 1}
    assert "review do Alpha tự đăng" in (w / "report.md").read_text(encoding="utf-8")
print("test_geo_answer: đạt")
