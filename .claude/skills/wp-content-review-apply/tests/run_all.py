"""Chạy mọi test offline của skill. python3 -B tests/run_all.py   (cần python3, php CLI có intl, node)
Mỗi file test chạy trong một tiến trình riêng. Thoát mã 1 khi có file lỗi. Không gọi mạng ngoài, không cần Chrome."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
bad = []
for f in sorted(here.glob("test_*.py")):
    p = subprocess.run([sys.executable, "-B", str(f)], capture_output=True, text=True)
    tail = (p.stderr.strip().splitlines() or p.stdout.strip().splitlines() or [""])[-1]
    print("%-28s %s  %s" % (f.name, "OK " if p.returncode == 0 else "LỖI", tail))
    if p.returncode:
        bad.append(f.name)
        print(p.stdout[-1500:], p.stderr[-2500:])
sys.exit(1 if bad else 0)
