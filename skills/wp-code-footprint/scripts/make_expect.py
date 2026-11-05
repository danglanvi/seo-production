#!/usr/bin/env python3
"""make_expect.py <thư mục lane> [--srv <thư mục bản chép production>] [--theme <tên theme>] : sinh build/EXPECT.tsv (relpath<TAB>md5 bản production lúc 00:12 trong srv/, hoặc NEW)
và build/MOVES.tsv từ build/MOVES.txt (mỗi dòng một relpath cần chuyển sang quarantine; thư mục ghi DIR)."""
import hashlib, sys
from pathlib import Path
args = sys.argv[1:]
lane = Path(args[0]).resolve(); build = lane / "build"
srv = Path(args[args.index("--srv") + 1]).resolve() if "--srv" in args else lane.parent.parent / "srv"
theme = args[args.index("--theme") + 1] if "--theme" in args else "theme"
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def srv_path(rel):
    if rel.startswith("mu-plugins/"): return srv / rel
    if rel.startswith(f"themes/{theme}/"): return srv / "theme" / rel[len(f"themes/{theme}/"):]
    return None
rows = []
for p in sorted(build.rglob("*")):
    if not p.is_file() or p.name in ("EXPECT.tsv", "MOVES.tsv", "MOVES.txt", ".DS_Store"): continue
    rel = p.relative_to(build).as_posix(); s = srv_path(rel)
    rows.append((rel, md5(s) if s and s.is_file() else "NEW"))
(build / "EXPECT.tsv").write_text("".join(f"{r}\t{m}\n" for r, m in rows))
mv = build / "MOVES.txt"
if mv.exists():
    out = []
    for rel in [l.strip() for l in mv.read_text().splitlines() if l.strip()]:
        s = srv_path(rel)
        out.append((rel, "DIR" if (s and s.is_dir()) else (md5(s) if s and s.is_file() else "ABSENT")))
    (build / "MOVES.tsv").write_text("".join(f"{r}\t{m}\n" for r, m in out))
    print("MOVES:", *(f"{r}={m[:8]}" for r, m in out))
print("EXPECT:", len(rows), "file;", sum(1 for _, m in rows if m == "NEW"), "NEW")
for r, m in rows: print(f"  {m[:8]} {r}")
