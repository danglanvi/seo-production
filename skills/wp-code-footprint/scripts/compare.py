#!/usr/bin/env python3
"""compare.py: bảng trước/sau từ html/ (00:13) và html-after/ bằng footprint_count logic. In Markdown."""
import re, sys, subprocess, json
from pathlib import Path
before, after = Path(sys.argv[1]), Path(sys.argv[2])
tool = Path(__file__).resolve().parent / "footprint_count.py"
def run(d):
    proc = subprocess.run([sys.executable, "-I", str(tool), *sorted(str(p) for p in d.glob("*.html"))], capture_output=True, text=True)
    if proc.returncode:
        print(f"INCOMPLETE: {d}; kiểm parser và danh sách HTML.\n{proc.stderr}", file=sys.stderr)
        raise SystemExit(2)
    out = proc.stdout
    res = {}
    for line in out.splitlines():
        m = re.match(r"(.+?\.html): (.*)", line)
        if m: res[Path(m.group(1)).name] = dict(kv.split("=") for kv in m.group(2).split())
    return res
b, a = run(before), run(after)
if not b or set(b) != set(a):
    print(f"INCOMPLETE: tập URL trước/sau khác nhau; thiếu={sorted(set(b)-set(a))}, thêm={sorted(set(a)-set(b))}", file=sys.stderr)
    raise SystemExit(2)
keys = ["inline_script", "inline_style", "js_bytes", "css_bytes", "comment_code", "comment_vi", "comment_quytrinh", "htmlcomment_quytrinh", "data_no_optimize"]
print("| Trang | " + " | ".join(f"{k} trước→sau" for k in keys) + " |"); print("|---|" + "---|" * len(keys))
tot = {k: [0, 0] for k in keys}
for f in sorted(b):
    if f not in a: continue
    row = []
    for k in keys:
        x, y = b[f][k], a[f][k]
        row.append(f"{x}→{y}")
        for i, v in enumerate((x, y)):
            try: tot[k][i] += int(re.sub(r"\D", "", v) or 0)
            except: pass
    print(f"| {f} | " + " | ".join(row) + " |")
print("| TỔNG | " + " | ".join(f"{tot[k][0]}→{tot[k][1]}" for k in keys) + " |")
