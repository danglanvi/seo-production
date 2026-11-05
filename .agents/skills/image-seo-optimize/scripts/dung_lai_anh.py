#!/usr/bin/env python3
"""Dựng lại ảnh thiết kế nhỏ (đang phục vụ) ở độ phân giải cao từ ảnh nguồn lớn hơn cùng nội dung. Không ghi đè file nào.

Cách làm: căn ảnh nhỏ với ảnh nguồn bằng SIFT + RANSAC (phép đồng dạng). Học phép chuyển màu cục bộ
nho = a(x)*nguon + b(x) theo từng kênh (guided filter), phóng a, b lên cỡ đích rồi áp vào nguồn đã căn.
Cách này giữ lớp phủ màu, vùng mờ dần và chỉnh màu của bản thiết kế. Vùng nguồn không phủ lấy ảnh nhỏ phóng to.
Kênh alpha (bo góc, tách nền) lấy từ ảnh nhỏ phóng to.

Ca thật 05/11/2026, site agency mẫu: ảnh đội ngũ hero mobile 570 px dựng lại 786 px, hero mobile 360 px dựng lại 1080 px.
Ca hỏng: banner có vùng mờ dần sang trắng: bản dựng nhạt hơn bản gốc sau đầu người. Luôn xem file --diff-png và ảnh ở 100%.

Dùng (cần opencv-python, numpy):
  python3 dung_lai_anh.py --nho dang-phuc-vu.png --nguon anh-goc-lon.jpg --out moi.png [--scale 1.29] [--diff-png diff.png]
--scale: cỡ đích = cỡ ảnh nhỏ × scale. Mặc định bằng tỉ lệ nguồn/nhỏ đo được (không phóng quá nguồn).
In một dòng JSON: size, inliers, ti_le_nguon, phu (tỉ lệ diện tích nguồn phủ), sai_khac_tb (mức lệch màu khi thu về cỡ cũ, /255).
Mã thoát: 0 xong · 2 input sai, thiếu thư viện · 3 căn không đạt (dưới 25 điểm khớp).
"""
import argparse
import json
import sys


def _load_gray(cv2, np, im):
    if im.ndim == 3 and im.shape[2] == 4:
        a = im[:, :, 3:] / 255.0
        im = (im[:, :, :3] * a + 255 * (1 - a)).astype(np.uint8)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) if im.ndim == 3 else im
    return cv2.createCLAHE(2.0, (8, 8)).apply(g)


def can_anh(cv2, np, nho, nguon):
    """Trả (M nhỏ→nguồn 2x3, số inlier). M None nếu không căn được."""
    sift = cv2.SIFT_create(8000)
    k1, d1 = sift.detectAndCompute(_load_gray(cv2, np, nho), None)
    k2, d2 = sift.detectAndCompute(_load_gray(cv2, np, nguon), None)
    if d1 is None or d2 is None:
        return None, 0
    good = [m for m, n in (x for x in cv2.BFMatcher().knnMatch(d1, d2, k=2) if len(x) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 12:
        return None, len(good)
    p1 = np.float32([k1[g.queryIdx].pt for g in good])
    p2 = np.float32([k2[g.trainIdx].pt for g in good])
    M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=2.0, maxIters=20000)
    return M, (int(inl.sum()) if inl is not None else 0)


def dung_lai(cv2, np, nho, nguon, scale=None, sigma=6.0, eps=40.0):
    alpha = nho[:, :, 3] if nho.ndim == 3 and nho.shape[2] == 4 else None
    S = nho[:, :, :3].astype(np.float32)
    src = nguon[:, :, :3].astype(np.float32) if nguon.ndim == 3 else cv2.cvtColor(nguon, cv2.COLOR_GRAY2BGR).astype(np.float32)
    M, inl = can_anh(cv2, np, nho, nguon)
    if M is None or inl < 25:
        return None, {'inliers': inl}
    h, w = S.shape[:2]
    sc = float(np.hypot(M[0, 0], M[1, 0]))
    f = min(scale or sc, sc)
    blur = lambda x: cv2.GaussianBlur(x, (0, 0), sigma)
    # nguồn căn về cỡ nhỏ (thu trước để khỏi răng cưa) để học a, b
    src_s = cv2.resize(src, None, fx=1 / sc, fy=1 / sc, interpolation=cv2.INTER_AREA)
    Ms = M / sc
    inv_s = cv2.invertAffineTransform(Ms)
    srcS = cv2.warpAffine(src_s, inv_s, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    valid = (cv2.warpAffine(np.ones(src_s.shape[:2], np.float32), inv_s, (w, h), borderValue=0) > 0.999).astype(np.float32)
    wv = blur(valid) + 1e-6
    A = np.zeros_like(S); B = np.zeros_like(S)
    for c in range(3):
        I = srcS[:, :, c] * valid; P = S[:, :, c] * valid
        mI = blur(I) / wv; mP = blur(P) / wv
        a = (blur(I * P) / wv - mI * mP) / (blur(I * I) / wv - mI * mI + eps)
        A[:, :, c] = blur(a); B[:, :, c] = blur(mP - a * mI)
    W, H = int(round(w * f)), int(round(h * f))
    ratio = sc / f
    src_t = cv2.resize(src, None, fx=1 / ratio, fy=1 / ratio, interpolation=cv2.INTER_AREA) if ratio > 1.05 else src
    Mt = (M / f) / (ratio if ratio > 1.05 else 1.0)
    Mt[:, :2] = M[:, :2] / f / (ratio if ratio > 1.05 else 1.0)
    Mt[:, 2] = M[:, 2] / (ratio if ratio > 1.05 else 1.0)
    inv_t = cv2.invertAffineTransform(Mt)
    srcT = cv2.warpAffine(src_t, inv_t, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    covT = cv2.warpAffine(np.ones(src_t.shape[:2], np.float32), inv_t, (W, H), borderValue=0)
    hi = cv2.resize(A, (W, H), interpolation=cv2.INTER_CUBIC) * srcT + cv2.resize(B, (W, H), interpolation=cv2.INTER_CUBIC)
    base = cv2.resize(S, (W, H), interpolation=cv2.INTER_LANCZOS4)
    m = cv2.GaussianBlur(cv2.erode((covT > 0.999).astype(np.float32), np.ones((5, 5), np.uint8)), (0, 0), 4 * f)
    m = np.clip((m - 0.5) * 2, 0, 1)[:, :, None]
    out = np.clip(hi * m + base * (1 - m), 0, 255).astype(np.uint8)
    if alpha is not None:
        out = np.dstack([out, cv2.resize(alpha, (W, H), interpolation=cv2.INTER_CUBIC)])
    back = cv2.resize(out[:, :, :3], (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    err = np.abs(cv2.GaussianBlur(back, (0, 0), 5) - cv2.GaussianBlur(S, (0, 0), 5)).mean(2)
    if alpha is not None:
        err = err * (alpha > 250)
    info = {'size': [W, H], 'inliers': inl, 'ti_le_nguon': round(sc, 3), 'phu': round(float((covT > 0.999).mean()), 4),
            'sai_khac_tb': round(float(np.abs(back - S).mean()), 2)}
    return (out, err), info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--nho', required=True)
    ap.add_argument('--nguon', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--scale', type=float)
    ap.add_argument('--diff-png')
    a = ap.parse_args(argv)
    try:
        import cv2
        import numpy as np
    except ImportError:
        print(json.dumps({'loi': 'thiếu opencv-python hoặc numpy'}))
        return 2
    nho = cv2.imread(a.nho, cv2.IMREAD_UNCHANGED)
    nguon = cv2.imread(a.nguon, cv2.IMREAD_UNCHANGED)
    if nho is None or nguon is None:
        print(json.dumps({'loi': 'không đọc được ảnh'}))
        return 2
    res, info = dung_lai(cv2, np, nho, nguon, a.scale)
    if res is None:
        print(json.dumps({'loi': 'căn không đạt', **info}, ensure_ascii=False))
        return 3
    out, err = res
    cv2.imwrite(a.out, out)
    if a.diff_png:
        cv2.imwrite(a.diff_png, cv2.applyColorMap(np.clip(err * 10, 0, 255).astype(np.uint8), cv2.COLORMAP_JET))
    print(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
