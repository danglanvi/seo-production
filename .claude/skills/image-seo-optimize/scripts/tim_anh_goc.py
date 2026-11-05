#!/usr/bin/env python3
"""Tìm bản gốc lớn hơn cho ảnh nhỏ đang phục vụ: so từng ảnh đích với từng ảnh ứng viên bằng SIFT + RANSAC. Chỉ đọc file.

Ảnh đích: ảnh mờ do nguồn nhỏ (thumbnail 300 px, ảnh hero 570–640 px). Ứng viên: ảnh lớn cùng tên gốc hoặc cùng chủ đề
lấy từ uploads, thư mục quarantine, backup trước tối ưu. Kết quả "ti_le" là số pixel nguồn trên 1 pixel đích:
>= 1,3 thì đáng dựng lại; 1,0 là cùng cỡ, không lợi. "doi_xung" gần 0 và "xoay" gần 0 nghĩa là ảnh đích là bản thu thẳng
của ứng viên: thu nhỏ trực tiếp từ ứng viên, không cần dung_lai_anh.py.

Ca thật 05/11/2026, site agency mẫu: 16 ảnh đích, 30 ứng viên: 2 thumbnail khách hàng có bản gốc 1080–1200 px (ti_le 3,6–4,0),
1 avatar có bản lớn hơn 1,48 lần, các ảnh còn lại không có nguồn lớn hơn.

Dùng (cần opencv-python, numpy):
  python3 tim_anh_goc.py --dich <thư mục hoặc file>... --ung-vien <thư mục hoặc file>... [--min-inliers 25]
In mỗi ảnh đích một dòng JSON: dich, ung_vien (null nếu không khớp), inliers, ti_le, xoay, doi_xung.
Mã thoát: 0 xong · 2 thiếu thư viện hoặc không có ảnh.
"""
import argparse
import json
import os
import sys

DUOI = ('.jpg', '.jpeg', '.png', '.webp')


def liet_ke(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(DUOI)]
        elif p.lower().endswith(DUOI):
            out.append(p)
    return out


def doc_xam(cv2, np, p, max_side=2200):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None:
        return None, 1.0
    if im.ndim == 3 and im.shape[2] == 4:
        a = im[:, :, 3:] / 255.0
        im = (im[:, :, :3] * a + 255 * (1 - a)).astype(np.uint8)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) if im.ndim == 3 else im
    s = 1.0
    if max(g.shape) > max_side:
        s = max_side / max(g.shape)
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return cv2.createCLAHE(2.0, (8, 8)).apply(g), s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dich', nargs='+', required=True)
    ap.add_argument('--ung-vien', nargs='+', required=True)
    ap.add_argument('--min-inliers', type=int, default=25)
    a = ap.parse_args(argv)
    try:
        import cv2
        import numpy as np
    except ImportError:
        print(json.dumps({'loi': 'thiếu opencv-python hoặc numpy'}, ensure_ascii=False))
        return 2
    dich, uv = liet_ke(a.dich), liet_ke(a.ung_vien)
    if not dich or not uv:
        print(json.dumps({'loi': 'không có ảnh đích hoặc ứng viên'}, ensure_ascii=False))
        return 2
    sift = cv2.SIFT_create(6000)
    bf = cv2.BFMatcher()
    U = []
    for p in uv:
        g, s = doc_xam(cv2, np, p)
        if g is None:
            continue
        k, d = sift.detectAndCompute(g, None)
        if d is not None and len(d) >= 10:
            U.append((p, k, d, s))
    for t in dich:
        g, _ = doc_xam(cv2, np, t, max_side=4000)
        best = {'dich': t, 'ung_vien': None, 'inliers': 0}
        if g is not None:
            k1, d1 = sift.detectAndCompute(g, None)
            for p, k2, d2, s in ([] if d1 is None else U):
                if p == t:
                    continue
                good = [m for m, n in (x for x in bf.knnMatch(d1, d2, k=2) if len(x) == 2) if m.distance < 0.75 * n.distance]
                if len(good) < 12:
                    continue
                p1 = np.float32([k1[x.queryIdx].pt for x in good])
                p2 = np.float32([k2[x.trainIdx].pt for x in good])
                M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0)
                n = int(inl.sum()) if inl is not None else 0
                if M is None or n <= best['inliers']:
                    continue
                best = {'dich': t, 'ung_vien': p, 'inliers': n, 'ti_le': round(float(np.hypot(M[0, 0], M[1, 0])) / s, 3),
                        'xoay': round(float(np.degrees(np.arctan2(M[1, 0], M[0, 0]))), 3),
                        'doi_xung': [round(float(M[0, 2]) / s, 1), round(float(M[1, 2]) / s, 1)]}
        if best['inliers'] < a.min_inliers:
            best = {'dich': t, 'ung_vien': None, 'inliers': best['inliers']}
        print(json.dumps(best, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
