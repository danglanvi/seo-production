#!/usr/bin/env python3
"""Kiểm kê container GTM công khai trước khi đề xuất đổi cách nạp tracking (Lớp 7).

Dùng:
  python3 -I gtm_inventory.py GTM-XXXXXXX
  python3 -I gtm_inventory.py --url https://example.com/      (tìm mã GTM trong HTML)

Chỉ đọc file gtm.js công khai, không cần quyền vào GTM. In: dung lượng, số tag theo loại, sự kiện GA4, sự kiện Pixel,
trình nghe click link, click, gửi form, và hệ quả nếu hoãn GTM đến khi người xem tương tác.
"""
import argparse
import collections
import json
import re
import sys
import urllib.request

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
LOAI = {
    '__googtag': 'Google tag (GA4 config)', '__gaawe': 'GA4 event', '__awct': 'Google Ads conversion', '__sp': 'Google Ads remarketing',
    '__gclidw': 'Conversion linker', '__html': 'Custom HTML', '__img': 'Custom image', '__paused': 'Tag đang tạm dừng',
    '__lcl': 'Trình nghe click link', '__cl': 'Trình nghe click', '__fsl': 'Trình nghe gửi form', '__sdl': 'Trình nghe cuộn',
    '__ytl': 'Trình nghe YouTube', '__evl': 'Trình nghe hiển thị phần tử', '__tl': 'Bộ hẹn giờ', '__jel': 'Trình nghe lỗi JS',
}
BEN_THU_BA = {'connect.facebook.net': 'Facebook Pixel', 'analytics.tiktok.com': 'TikTok Pixel', 'clarity.ms': 'Microsoft Clarity',
              'static.hotjar.com': 'Hotjar', 'snap.licdn.com': 'LinkedIn Insight'}  # Google Ads: xem tag __awct, __sp (chuỗi googleadservices có sẵn trong mã gtm.js)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('gtm', nargs='?')
    ap.add_argument('--url')
    a = ap.parse_args()
    gid = a.gtm
    if a.url:
        ids = sorted(set(re.findall(r'GTM-[A-Z0-9]{4,10}', get(a.url))))
        if not ids:
            sys.exit('Không thấy mã GTM trong HTML của ' + a.url)
        print('Mã GTM trong trang:', ', '.join(ids))
        gid = gid or ids[0]
    if not gid:
        sys.exit('Cần mã GTM hoặc --url')
    s = get('https://www.googletagmanager.com/gtm.js?id=' + gid)
    i = s.find('"tags":[')
    if i < 0:
        sys.exit('Không đọc được danh sách tag trong gtm.js')
    tags, _ = json.JSONDecoder().raw_decode(s, i + len('"tags":'))
    print(f'{gid}: gtm.js {len(s) // 1024} KB chưa nén, {len(tags)} tag')
    dem = collections.Counter(t.get('function', '') for t in tags)
    for f, n in dem.most_common():
        ten = LOAI.get(f) or ('Template cộng đồng' + (' (Facebook Pixel)' if any(t.get('function') == f and 'vtp_pixelId' in t for t in tags) else ''))
        print(f'  {n:>3}  {f:<16} {ten}')
    ga4 = [t['vtp_eventName'] for t in tags if t.get('function') == '__gaawe' and t.get('vtp_eventName')]
    px = [t.get('vtp_customEventName') or t.get('vtp_standardEventName') for t in tags if 'vtp_pixelId' in t]
    if ga4:
        print('Sự kiện GA4:', '; '.join(ga4))
    if px:
        print('Sự kiện Pixel:', '; '.join(x for x in px if x))
    co = [ten for host, ten in BEN_THU_BA.items() if host in s]
    if co:
        print('Container tải thêm:', ', '.join(co))
    print('Nếu hoãn GTM đến khi người xem tương tác:')
    print('  - Mất pageview và PageView Pixel của lượt thoát ngay, không chạm. Meta ghi thiếu "lượt xem trang đích" (LPV).')
    if dem['__lcl'] or dem['__cl']:
        print(f'  - Có {dem["__lcl"] + dem["__cl"]} trình nghe click: cú click đầu tiên (Zalo, Messenger, Hotline, link ra ngoài) mở link trước khi GTM kịp ghi.')
    if dem['__fsl']:
        print(f'  - Có {dem["__fsl"]} trình nghe gửi form: thường vẫn ghi được, vì người xem đã gõ phím trước khi gửi.')
    print('  - Người chuyển trang trước khi GTM chạy làm mất gclid, fbclid của trang đích.')
    print('  - Giữ GTM tải ngay ở trang thanh toán, cảm ơn. Đơn ghi phía server (form, cổng thanh toán) không bị ảnh hưởng.')


if __name__ == '__main__':
    main()
