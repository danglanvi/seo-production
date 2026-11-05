#!/usr/bin/env python3
"""Khử trùng input Jev/Gemma và dựng docs JS theme cho so khớp. Chạy từ thư mục audit."""
import hashlib
import json
import sys
from pathlib import Path

A = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
OUT = A / "work" / "out"
JEV = A / "jev"
EMB = A / "emb"
JEV.mkdir(exist_ok=True)
EMB.mkdir(exist_ok=True)


def rows(p):
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def write(p, items):
    with open(p, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    return len(items)


# 1. comment trong HTML: gộp theo (where, block, text)
seen, out, pages = {}, [], {}
for r in rows(OUT / "jev_comments.jsonl"):
    s = r["state"]
    key = (s["where"], s["block"].split("@")[0], s["comment"][:200])
    pages.setdefault(key, set()).add(s["page"])
    if key in seen:
        continue
    seen[key] = r["id"]
    out.append({"id": r["id"], "state": {"page": s["page"], "block": s["block"], "where": s["where"], "comment": s["comment"]}})
for it in out:
    s = it["state"]
    s["pages_seen"] = len(pages[(s["where"], s["block"].split("@")[0], s["comment"][:200])])
n1 = write(JEV / "in_html_comments.jsonl", out)

# 2. comment trong mu-plugins: giữ nguyên
n2 = write(JEV / "in_plugin_comments.jsonl", list(rows(OUT / "jev_plugin_comments.jsonl")))

# 3. inline script: gộp theo hash code_head
seen, out = {}, []
for r in rows(OUT / "jev_scripts.jsonl"):
    s = r["state"]
    h = hashlib.md5(s["code_head"][:1200].encode()).hexdigest()
    if h in seen:
        seen[h]["state"]["pages_seen"] += 1
        continue
    r["state"]["pages_seen"] = 1
    seen[h] = r
    out.append(r)
n3 = write(JEV / "in_scripts.jsonl", out)

# 4. section/article/aside: gộp theo (tag, heading, class, text[:160])
seen, out = {}, []
for r in rows(OUT / "jev_sections.jsonl"):
    s = r["state"]
    key = (s["tag"], s["heading"], s["class"], s["text"][:160])
    if key in seen:
        seen[key]["state"]["pages_seen"] += 1
        continue
    r["state"]["pages_seen"] = 1
    seen[key] = r
    out.append(r)
n4 = write(JEV / "in_sections.jsonl", out)

# 5. Gemma: inline script (unique) và docs JS theme
emb_q = []
seen = set()
for r in rows(OUT / "emb_scripts.jsonl"):
    h = hashlib.md5(r["text"][:1200].encode()).hexdigest()
    if h in seen or len(r["text"].strip()) < 200:
        continue
    seen.add(h)
    emb_q.append({"id": r["id"], "text": r["text"][:5000]})
n5 = write(EMB / "q_inline_scripts.jsonl", emb_q)
docs = []
for p in sorted((A / "srv" / "theme").rglob("*.js")):
    if "vendor" in p.parts or ".min." in p.name:
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    for i in range(0, min(len(txt), 30000), 5000):
        docs.append({"id": f"{p.relative_to(A / 'srv')}#{i//5000}", "text": txt[i:i + 5000]})
# mu-plugin JS inline cũng là docs để thấy script nào chồng script nào
for p in sorted((A / "srv" / "mu-plugins").glob("*.php")):
    txt = p.read_text(encoding="utf-8", errors="replace")
    if "<script" in txt or "wp_add_inline_script" in txt:
        for i in range(0, min(len(txt), 40000), 5000):
            docs.append({"id": f"{p.relative_to(A / 'srv')}#{i//5000}", "text": txt[i:i + 5000]})
n6 = write(EMB / "d_theme_js.jsonl", docs)
print(f"html_comments={n1} plugin_comments={n2} scripts={n3} sections={n4} emb_q={n5} emb_docs={n6}")
