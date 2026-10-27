# Làm nóng cache CDN ở trạm Mỹ (và trạm trung chuyển Origin Shield) cho danh sách URL, kèm ảnh trong HTML nếu bật --images.
# Gửi request tới IP trạm Mỹ của tên CDN (tra qua 8.8.8.8 với ECS dải Mỹ), không tra domain thật: sau khi chia vùng, máy ở VN nhận origin.
# Nhịp tối đa 1 request/giây, 1 luồng.
# HTML gửi Accept có image/webp (--accept): Bunny không tách HTML theo Accept và giữ bản của lượt đầu sau purge (site VN 27/10/2026).
#   python3 warm.py --domain example.com --cdn-host example.b-cdn.net --urls work/urls.txt --images --out work/warm-1.json
import argparse
import os
import re
import subprocess
import sys
import time
from collections import Counter
from urllib.parse import urljoin, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdn import save_json  # noqa: E402

UAS = {
    "mobile": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) cdn-warm",
    "desktop": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) cdn-warm",
}
WEBP_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
IMG = re.compile(r"""(?:src|data-src)=["']([^"']+\.(?:png|jpe?g|webp|gif|svg|avif))(?:\?[^"']*)?["']|srcset=["']([^"']+)["']""", re.I)


def edge_ip(cdn_host, ecs):
    out = subprocess.run(["dig", "+short", "@8.8.8.8", cdn_host, "A", "+subnet=" + ecs], capture_output=True, text=True).stdout.split()
    ips = [x for x in out if re.match(r"^\d+\.\d+\.\d+\.\d+$", x)]
    if not ips:
        sys.exit("Không tra được IP trạm CDN cho %s" % cdn_host)
    return ips[0]


def images(html, base, domain):
    found = set()
    for m in IMG.finditer(html):
        if m.group(1):
            found.add(m.group(1))
        else:
            for part in m.group(2).split(","):
                u = part.strip().split(" ")[0]
                if u:
                    found.add(u)
    out = set()
    for u in found:
        full = urljoin(base, u)
        if urlparse(full).hostname == domain:
            out.add(full.split("#")[0])
    return sorted(out)


def fetch(url, domain, ip, ua, body=False, accept=None):
    args = ["curl", "-s", "-A", ua, "--resolve", "%s:443:%s" % (domain, ip), "-D", "-", "--max-time", "60",
            "-w", "\nCODE=%{http_code} T=%{time_starttransfer}", url]
    if accept:
        args[4:4] = ["-H", "Accept: " + accept]
    if not body:
        args[2:2] = ["-o", "/dev/null"]
    r = subprocess.run(args, capture_output=True, text=True, errors="replace").stdout
    c = re.search(r"CODE=(\d+) T=(\S+)", r)
    cache = re.search(r"(?im)^(?:cdn-cache|cf-cache-status):\s*(\S+)", r)
    return {"code": c.group(1) if c else "ERR", "cache": cache.group(1) if cache else None,
            "t": float(c.group(2)) if c else None}, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--cdn-host", required=True, help="tên CDN có IP theo vùng, ví dụ <zone>.b-cdn.net")
    ap.add_argument("--ecs", default="8.8.8.0/24", help="dải ECS để chọn trạm; mặc định dải Mỹ")
    ap.add_argument("--urls", required=True)
    ap.add_argument("--images", action="store_true")
    ap.add_argument("--accept", default=WEBP_ACCEPT, help="Accept cho HTML; mặc định như Chrome, có image/webp")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ip = edge_ip(a.cdn_host, a.ecs)
    urls = [u.strip() for u in open(a.urls) if u.strip().startswith("https://%s/" % a.domain)]
    rows, seen_img = [], set()

    def one(u, kind, ua, body=False, accept=None):
        t0 = time.time()
        res, raw = fetch(u, a.domain, ip, ua, body, accept)
        rows.append({"u": u, "v": kind, **res})
        time.sleep(max(0, 1.0 - (time.time() - t0)))
        return raw

    for u in urls:
        for k, ua in UAS.items():
            raw = one(u, k, ua, body=a.images and k == "desktop", accept=a.accept)
            if a.images and k == "desktop":
                for img in images(raw, u, a.domain):
                    if img not in seen_img:
                        seen_img.add(img)
                        one(img, "img", UAS["desktop"])
    save_json(a.out, rows)
    print("xong", len(rows), "ảnh", len(seen_img), Counter(r["code"] for r in rows), Counter(r["cache"] for r in rows))


if __name__ == "__main__":
    main()
