#!/usr/bin/env python3
"""Đo SSIM độ sáng (luma) giữa hai ảnh cùng kích thước và so với ngưỡng theo loại ảnh.

Luma = trung bình 3 kênh RGB, cửa sổ đều 7x7. Ngưỡng 0,97 và 0,98 hiệu chuẩn trên cách đo này: đổi cách đo thì đo lại ngưỡng.
Ngưỡng theo loại ảnh (--kind):
  chu   ảnh có chữ hoặc logo: 0,98
  that  ảnh chụp thật: 0,97
Ảnh có kênh alpha phải đo trên nền thật của trang (--bg). Cùng một cặp ảnh cho 0,9737 trên nền thật và 0,9616 trên nền đen hoặc trắng.
Không có --bg mà ảnh có alpha thì script thoát 2. Truyền --bg nhiều lần để in thêm số của nền khác. Cổng đạt dùng nền đầu tiên.

Dùng (cần Pillow và numpy; chạy python3 không có -I):
  python3 ssim_luma.py A B --kind chu|that [--min 0.975] [--bg '#1e1b4b' --bg '#000000'] [--json]
Mã thoát: 0 đạt ngưỡng · 1 dưới ngưỡng · 2 input sai (thiếu thư viện, khác kích thước, ảnh có alpha mà thiếu --bg).
"""
import argparse
import json
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError as e:  # pragma: no cover
    sys.exit(f"Thiếu thư viện ({e.name}). Cài: python3 -m pip install pillow numpy")

NGUONG = {"chu": 0.98, "that": 0.97}


def _box(a, k):
    c = np.cumsum(np.cumsum(np.pad(a, ((1, 0), (1, 0))), 0), 1)
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def ssim_kenh(a, b, k=7):
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ma, mb = _box(a, k), _box(b, k)
    saa, sbb, sab = _box(a * a, k) - ma * ma, _box(b * b, k) - mb * mb, _box(a * b, k) - ma * mb
    cov = k * k / (k * k - 1)
    s = ((2 * ma * mb + c1) * (2 * cov * sab + c2)) / ((ma * ma + mb * mb + c1) * (cov * (saa + sbb) + c2))
    return float(s.mean())


def co_alpha(path):
    im = Image.open(path)
    return im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)


def parse_bg(s):
    s = s.strip().lstrip("#")
    if "," in s:
        v = tuple(int(x) for x in s.split(","))
    else:
        v = tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    if len(v) != 3 or any(not 0 <= x <= 255 for x in v):
        raise ValueError(f"nền không hợp lệ: {s}")
    return v


def tai(path, bg):
    im = Image.open(path).convert("RGBA")
    nen = Image.new("RGBA", im.size, tuple(bg) + (255,))
    return np.asarray(Image.alpha_composite(nen, im).convert("RGB"))


def ssim_luma(pa, pb, bg=(255, 255, 255)):
    """Trả (ssim_luma, ssim_kenh_thap_nhat) của hai file ảnh, ghép lên nền bg trước khi đo."""
    a, b = tai(pa, bg), tai(pb, bg)
    if a.shape != b.shape:
        raise ValueError(f"khác kích thước: {a.shape[1]}x{a.shape[0]} và {b.shape[1]}x{b.shape[0]}")
    return ssim_kenh(a.mean(2), b.mean(2)), min(ssim_kenh(a[..., i], b[..., i]) for i in range(3))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--kind", choices=sorted(NGUONG), help="loại ảnh, chọn ngưỡng 0,98 (chu) hoặc 0,97 (that)")
    ap.add_argument("--min", type=float, help="ngưỡng riêng, thắng --kind")
    ap.add_argument("--bg", action="append", help="nền thật của trang: #RRGGBB hoặc R,G,B. Lặp lại để đo thêm nền khác")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    nguong = a.min if a.min is not None else NGUONG.get(a.kind)
    if nguong is None:
        ap.error("cần --kind hoặc --min")
    try:
        alpha = co_alpha(a.a) or co_alpha(a.b)
        if alpha and not a.bg:
            print("Ảnh có kênh alpha: truyền --bg bằng nền thật của trang (không dùng nền đen hoặc trắng).", file=sys.stderr)
            return 2
        nen = [parse_bg(x) for x in (a.bg or ["#ffffff"])]
        kq = []
        for n in nen:
            luma, kenh = ssim_luma(a.a, a.b, n)
            kq.append({"bg": "#%02x%02x%02x" % n, "ssim_luma": round(luma, 4), "ssim_kenh_thap_nhat": round(kenh, 4)})
    except (OSError, ValueError) as e:
        print(f"Lỗi input: {e}", file=sys.stderr)
        return 2
    dat = kq[0]["ssim_luma"] >= nguong
    if a.json:
        print(json.dumps({"nguong": nguong, "dat": dat, "do": kq}, ensure_ascii=False))
    else:
        for r in kq:
            print(f"SSIM_LUMA {r['ssim_luma']:.4f} nen={r['bg']} kenh_thap_nhat={r['ssim_kenh_thap_nhat']:.4f}")
        print(f"NGUONG {nguong} {'DAT' if dat else 'KHONG_DAT'} (nền đầu tiên: {kq[0]['bg']})")
    return 0 if dat else 1


if __name__ == "__main__":
    sys.exit(main())
