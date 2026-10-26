#!/usr/bin/env python3
"""Chấm luật viết theo đoạn: code đếm luật đếm được, Jev chấm 5 câu hỏi theo đoạn, Claude đọc vùng xám và luật cần cả trang.

  paragraphs --html-dir DIR [--urls urls.txt] [--selector .entry-content] --out paras.jsonl
             Cần beautifulsoup4 (python3 -E nếu venv thiếu). Thư mục có cặp file <tên>.html + <tên>.url.
             Mỗi đoạn: <p>, hoặc <p> kết thúc bằng ":" gộp với danh sách ngay sau nó. Ghi heading gần nhất (H2/H3).
  code       --paras paras.jsonl --out code.jsonl       Luật code: 21, 24, 26, 32 (references/writing-rules-routing.md).
  prepare    --paras paras.jsonl --out jev_in.jsonl [--max N --seed S]
  report     --paras paras.jsonl --jev-out jev_out.jsonl --code code.jsonl --out-dir DIR [--registry R --site D]
Cổng đọc từ entry rubric "writing-rules" theo từng câu hỏi: ngưỡng yes → "vi phạm", ngưỡng no → "đạt".
Entry chỉ có `reject_below` là mốc lọc: p ≥ mốc → "Claude đọc", p dưới mốc → "Jev xếp thấp" (không phải "đạt").
Câu hỏi không có entry → "chưa hiệu chuẩn", không đọc cột đó. Câu `answer_first` chỉ tính cho đoạn đầu sau heading.
"""
import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUBRIC = "writing-rules"
TASK = Path(__file__).resolve().parents[1] / "tasks" / "writing-rules.json"
QUESTIONS = ["answer_first", "hedging", "fluff", "vague_quantity", "plural_no_example"]
RULES = {"answer_first": "11, 17, 20", "hedging": "1", "fluff": "2", "vague_quantity": "3, 6, 8",
         "plural_no_example": "9, 25"}
LONG_WORDS = 120
QUOTE = re.compile(r'^\s*["“”‘’«]')
CITE_FIRST = re.compile(r"^\s*(theo|dựa theo|căn cứ theo|according to)\s+[^,]{2,60},", re.I)


def jl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def clean(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def cmd_paragraphs(a):
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        sys.exit("thiếu beautifulsoup4: chạy bằng python3 -E của hệ thống hoặc cài bs4")
    want = {l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()} if a.urls else None
    rows = []
    for uf in sorted(Path(a.html_dir).glob("*.url")):
        url = uf.read_text(encoding="utf-8").strip()
        if want is not None and url not in want:
            continue
        soup = BeautifulSoup((uf.with_suffix(".html")).read_text(encoding="utf-8", errors="replace"), "html.parser")
        root = soup.select_one(a.selector) or soup.find("article") or soup.find("main")
        if not root:
            continue
        heading, first, n, cur = "", True, 0, None
        for el in root.find_all(["h2", "h3", "p", "ul", "ol"]):
            if el.find_parent(["ul", "ol"]) and el.name in ("ul", "ol", "p"):
                continue
            if el.name in ("h2", "h3"):
                heading, first, cur = clean(el.get_text(" ")), True, None
                continue
            text = clean(el.get_text(" "))
            if el.name in ("ul", "ol"):
                if cur is not None:
                    items = [clean(li.get_text(" ")) for li in el.find_all("li", recursive=False)]
                    cur["text"] += " " + " ; ".join(i for i in items if i)
                    cur["words"] = len(cur["text"].split())
                    cur["has_list"] = True
                    cur = None
                continue
            if len(text.split()) < 8:
                continue
            row = {"id": f"{url}#p{n}", "url": url, "heading": heading, "first_after_heading": first and bool(heading),
                   "text": text, "words": len(text.split()), "has_list": False}
            rows.append(row)
            n += 1
            first = False
            cur = row if text.endswith(":") else None
    write(a.out, rows)
    print(f"{len(rows)} đoạn từ {len({r['url'] for r in rows})} trang -> {a.out}", file=sys.stderr)
    return 0


def code_flags(p):
    f = []
    if QUOTE.match(p["text"]):
        f.append("R24 mở đoạn bằng trích dẫn")
    if CITE_FIRST.match(p["text"]):
        f.append("R21 dẫn nguồn trước claim")
    if "/" in p.get("heading", "") and not re.search(r"https?://|\d/\d", p["heading"]):
        f.append("R26 heading dùng dấu /")
    if p["words"] > LONG_WORDS and not p.get("has_list"):
        f.append(f"R32 đoạn dài {p['words']} chữ")
    return f


def cmd_code(a):
    rows = [{"id": p["id"], "url": p["url"], "flags": code_flags(p)} for p in jl(a.paras)]
    write(a.out, rows)
    print(f"{sum(1 for r in rows if r['flags'])}/{len(rows)} đoạn có cờ code -> {a.out}", file=sys.stderr)
    return 0


def cmd_prepare(a):
    paras = jl(a.paras)
    if a.max and len(paras) > a.max:
        random.Random(a.seed).shuffle(paras)
        paras = paras[:a.max]
    rows = [{"id": p["id"], "state": {"heading": p["heading"], "text": p["text"][:3000]}} for p in paras]
    write(a.out, rows)
    print(f"{len(rows)} đoạn gửi Jev -> {a.out}", file=sys.stderr)
    return 0


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def load_gates(registry, site, version):
    for path, want_site, src in ((registry, site, "site"), (find_defaults(), None, "defaults")):
        if not path or not Path(path).exists():
            continue
        g = defaultdict(dict)
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == RUBRIC and e.get("version") == version and e.get("mode") == "jev" \
                    and (not want_site or e.get("site") == want_site):
                if e.get("threshold") is not None:
                    g[e["question"]][e.get("positive")] = e["threshold"]
                elif e.get("reject_below") is not None:
                    g[e["question"]]["triage"] = e["reject_below"]
        if g:
            return dict(g), src
    return {}, None


def decide(p_yes, gate):
    if not gate:
        return "chưa hiệu chuẩn"
    if p_yes is None:
        return "Claude đọc"
    if "yes" in gate and p_yes >= gate["yes"]:
        return "vi phạm"
    if "no" in gate and 1 - p_yes >= gate["no"]:
        return "đạt"
    if "triage" in gate and p_yes < gate["triage"]:
        return "Jev xếp thấp"
    return "Claude đọc"


def cmd_report(a):
    version = json.loads(TASK.read_text(encoding="utf-8"))["version"]
    gates, src = load_gates(a.registry, a.site, version)
    jev = {r["id"]: r for r in jl(a.jev_out)} if a.jev_out else {}
    code = {r["id"]: r["flags"] for r in jl(a.code)} if a.code else {}
    rows, per_page = [], defaultdict(Counter)
    for p in jl(a.paras):
        ans = (jev.get(p["id"]) or {}).get("answers") or {}
        if not ans and not code.get(p["id"]):
            continue
        r = {"id": p["id"], "url": p["url"], "heading": p["heading"], "code": code.get(p["id"], [])}
        for q in QUESTIONS:
            if q == "answer_first" and not p["first_after_heading"]:
                continue
            if not ans:
                continue
            r[q] = decide((ans.get(q) or {}).get("p_yes"), gates.get(q, {}))
            per_page[p["url"]][f"{q}:{r[q]}"] += 1
        for f in r["code"]:
            per_page[p["url"]][f.split()[0]] += 1
        rows.append(r)
    out = Path(a.out_dir)
    write(out / "paragraphs.jsonl", rows)
    L = [f"# Luật viết theo đoạn — rubric {RUBRIC} {version}", "",
         f"- Đoạn đã chấm: {len(rows)}. Cổng: {gates or 'chưa có'} ({src or 'Claude đọc mọi nhãn Jev'}).",
         "- Câu hỏi Jev ↔ luật: " + "; ".join(f"`{q}` = luật {RULES[q]}" for q in QUESTIONS) + ".",
         "- `answer_first` là câu hỏi ngược chiều: \"vi phạm\" nghĩa là câu đầu KHÔNG trả lời heading.",
         "- Luật cần cả trang (35, 41–60) và information gain không có trong bảng này: xem SKILL.md.", "",
         "| URL | " + " | ".join(QUESTIONS) + " | Cờ code |", "|---" * (len(QUESTIONS) + 2) + "|"]
    for u, c in sorted(per_page.items()):
        cells = [f"{c[q + ':vi phạm']} vi phạm / {c[q + ':Claude đọc']} đọc" if gates.get(q) else "—" for q in QUESTIONS]
        codes = ", ".join(f"{k}×{v}" for k, v in c.items() if k.startswith("R"))
        L.append(f"| {u} | " + " | ".join(cells) + f" | {codes} |")
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(rows)} đoạn -> {out}", file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("paragraphs")
    p.add_argument("--html-dir", required=True)
    p.add_argument("--urls")
    p.add_argument("--selector", default=".entry-content")
    p.add_argument("--out", required=True)
    c = sub.add_parser("code")
    c.add_argument("--paras", required=True)
    c.add_argument("--out", required=True)
    r = sub.add_parser("prepare")
    r.add_argument("--paras", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--max", type=int, default=0)
    r.add_argument("--seed", type=int, default=20261019)
    t = sub.add_parser("report")
    t.add_argument("--paras", required=True)
    t.add_argument("--jev-out")
    t.add_argument("--code")
    t.add_argument("--out-dir", required=True)
    t.add_argument("--registry")
    t.add_argument("--site")
    a = ap.parse_args(argv)
    return {"paragraphs": cmd_paragraphs, "code": cmd_code, "prepare": cmd_prepare, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
