#!/usr/bin/env python3
"""Nén lại một ảnh WebP từ nguồn gốc JPG hoặc PNG, giữ SSIM luma trên ngưỡng theo loại ảnh. Không ghi đè file nào.

Vòng lặp: cwebp -m 6 -pass 10 từ nguồn gốc, q giảm từ --q-start theo --step tới khi file nhỏ hơn --target-kb hoặc SSIM dưới ngưỡng.
SSIM so với file đang phục vụ (--ref). Không có --ref thì so với nguồn gốc. Chỉ ghi --out khi nhỏ hơn --ref ít nhất --min-saving.
Ca thật 27/10/2026, 35 banner case study của một site WordPress: 32 file đổi, 1.514 KB còn 1.205 KB (-20,4%).
Điểm PSI và LCP đổi trong nhiễu. Chỉ số byte đổi thật.

Dùng (cần cwebp, Pillow, numpy):
  python3 webp_recompress.py --src goc.jpg --kind chu|that --out moi.webp [--ref dang-phuc-vu.webp] [--target-kb 30]
                             [--q-start 80] [--q-min 40] [--step 2] [--min-saving 0.08] [--bg '#ffffff']
In một dòng JSON: action, q, bytes, ref_bytes, ssim_luma. action:
  skip-nho        --ref đã nhỏ hơn --target-kb
  keep-ssim       ngay q đầu SSIM đã dưới ngưỡng: giữ --ref
  keep-saving     bản mới nhỏ hơn --ref chưa tới --min-saving: giữ --ref
  new-file        chưa có --ref WebP, bản mới đạt: đã ghi --out
  recompress      có --ref, bản mới đạt: đã ghi --out
Mã thoát: 0 xong (kể cả khi giữ nguyên) · 2 input sai hoặc thiếu cwebp.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ssim_luma import NGUONG, parse_bg, ssim_luma  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--kind", required=True, choices=sorted(NGUONG))
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref")
    ap.add_argument("--target-kb", type=float, default=30)
    ap.add_argument("--q-start", type=int, default=80)
    ap.add_argument("--q-min", type=int, default=40)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--min-saving", type=float, default=0.08)
    ap.add_argument("--bg", default="#ffffff")
    a = ap.parse_args(argv)
    if not shutil.which("cwebp"):
        print("Thiếu cwebp (brew install webp).", file=sys.stderr)
        return 2
    src = Path(a.src)
    ref = Path(a.ref) if a.ref else None
    if not src.is_file() or (ref and not ref.is_file()):
        print("Không thấy file --src hoặc --ref.", file=sys.stderr)
        return 2
    if Path(a.out).exists():
        print("--out đã có. Script không ghi đè.", file=sys.stderr)
        return 2
    chuan = ref or src
    ref_b = chuan.stat().st_size
    target = a.target_kb * 1024
    nguong = NGUONG[a.kind]
    bg = parse_bg(a.bg)
    kq = {"action": "", "q": None, "bytes": None, "ref_bytes": ref_b, "ssim_luma": None, "nguong": nguong}
    if ref and ref_b <= target:
        kq["action"] = "skip-nho"
        print(json.dumps(kq))
        return 0
    with tempfile.TemporaryDirectory() as td:
        tot = None
        for q in range(a.q_start, a.q_min - 1, -a.step):
            t = os.path.join(td, f"q{q}.webp")
            r = subprocess.run(["cwebp", "-quiet", "-m", "6", "-pass", "10", "-q", str(q), "-metadata", "icc", str(src), "-o", t],
                               capture_output=True)
            if r.returncode:
                print(f"cwebp lỗi ở q={q}: {r.stderr.decode(errors='replace')[:200]}", file=sys.stderr)
                return 2
            sz = os.path.getsize(t)
            ss = ssim_luma(str(chuan), t, bg)[0]
            if ss < nguong:
                break
            tot = (q, sz, ss, t)
            if sz <= target:
                break
        if tot is None:
            kq["action"] = "keep-ssim"
        else:
            q, sz, ss, t = tot
            kq.update(q=q, bytes=sz, ssim_luma=round(ss, 4))
            if sz > ref_b * (1 - a.min_saving):
                kq["action"] = "keep-saving"
            else:
                Path(a.out).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(t, a.out)
                kq["action"] = "recompress" if ref else "new-file"
    print(json.dumps(kq))
    return 0


if __name__ == "__main__":
    sys.exit(main())
