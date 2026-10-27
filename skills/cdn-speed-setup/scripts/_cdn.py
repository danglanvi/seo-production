# Helper chung cho script cdn-speed-setup: đọc secret, gọi API Cloudflare/Bunny/Globalping, che IP.
# Secret: biến môi trường, hoặc dòng cùng tên trong .agent-secrets/.env tìm từ thư mục hiện tại trở lên. Không in secret.
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

IPRE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:[0-9a-f]{1,4}:){3,7}[0-9a-f]{1,4}\b"
                  r"|\b[0-9a-f]{1,4}::[0-9a-f:]{1,35}|\b(?:[0-9a-f]{1,4}:){1,6}:(?:[0-9a-f]{1,4})?\b", re.I)


def mask(s):
    # Lượt hai che phần đuôi IPv6 nén còn sót sau lượt một (ví dụ "<ip>:84e5").
    return re.sub(r"<ip>(?::[0-9a-f]{1,4})+", "<ip>", IPRE.sub("<ip>", s), flags=re.I)


def save_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(mask(json.dumps(obj, ensure_ascii=False, indent=1)))


def secret(name, required=True):
    if os.environ.get(name):
        return os.environ[name]
    d = os.getcwd()
    while True:
        p = os.path.join(d, ".agent-secrets", ".env")
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                m = re.match(r"\s*(?:export\s+)?%s\s*=\s*(.*)$" % re.escape(name), line)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    if required:
        sys.exit("Không thấy %s (biến môi trường hoặc .agent-secrets/.env)" % name)
    return None


def origin_ip(path):
    # IP origin nằm trong file chmod 600 ngoài thư mục dự án (ví dụ ~/.cm/<site>.origin), không nằm trong repo.
    ip = open(os.path.expanduser(path)).read().strip()
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
        sys.exit("File IP origin không chứa IPv4: %s" % path)
    return ip


def _call(base, hdr, method, path, body=None, timeout=60):
    req = urllib.request.Request(base + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={**hdr, "Content-Type": "application/json", "Accept": "application/json",
                                          "User-Agent": "cdn-speed-setup/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read()
            return r.status, (json.loads(b) if b.strip() else None)
    except urllib.error.HTTPError as e:
        b = e.read()
        try:
            return e.code, json.loads(b)
        except Exception:
            return e.code, b.decode(errors="replace")[:500]


def cf(method, path, body=None):
    return _call("https://api.cloudflare.com/client/v4", {"Authorization": "Bearer " + secret("CLOUDFLARE_DNS_TOKEN")},
                 method, path, body)


def bn(method, path, body=None):
    return _call("https://api.bunny.net", {"AccessKey": secret("BUNNY_API_KEY")}, method, path, body)


def cf_zone_id(name):
    c, j = cf("GET", "/zones?name=%s" % name)
    if c != 200 or not j.get("result"):
        sys.exit("Không đọc được zone %s (HTTP %s)" % (name, c))
    return j["result"][0]["id"]


def cf_records(zid, name):
    c, j = cf("GET", "/zones/%s/dns_records?name=%s" % (zid, name))
    if c != 200:
        sys.exit("Không đọc được bản ghi %s (HTTP %s)" % (name, c))
    return j["result"]


def globalping_need(n_probe):
    # Quota Globalping không đăng nhập: 250 probe mỗi giờ cho mỗi IP. Mỗi probe trong một phép đo tính 1 (8 probe = 8).
    # Quota dùng chung cho mọi lane trên máy. Thiếu quota thì dừng trước khi đo, tránh file kết quả rỗng.
    c, j = _call("https://api.globalping.io/v1", {}, "GET", "/limits", timeout=20)
    try:
        lim = j["rateLimit"]["measurements"]["create"]
    except Exception:
        print("không đọc được quota Globalping (HTTP %s), vẫn chạy" % c)
        return
    if lim["remaining"] < n_probe:
        sys.exit("Globalping còn %d probe, cần %d. Mở lại sau %d phút." % (lim["remaining"], n_probe, lim["reset"] // 60 + 1))
    print("Globalping còn %d probe, lượt này dùng khoảng %d" % (lim["remaining"], n_probe))


def globalping(payload, wait_s=60):
    # Query string đặt ở trường query, không ở path.
    c, j = _call("https://api.globalping.io/v1", {}, "POST", "/measurements", payload, timeout=40)
    if c not in (200, 202):
        return {"error": c, "detail": j}
    for _ in range(wait_s):
        time.sleep(1.0)
        c2, r = _call("https://api.globalping.io/v1", {}, "GET", "/measurements/%s" % j["id"], timeout=40)
        if isinstance(r, dict) and r.get("status") == "finished":
            return r
    return {"error": "timeout"}


def classify(answers, origin):
    # Phân loại câu trả lời DNS: ORIGIN (có IP origin), CDN (có IP khác), EMPTY (không có A).
    ips = [a for a in answers if a and IPRE.fullmatch(a)]
    if origin in ips:
        return "ORIGIN"
    return "CDN" if ips else "EMPTY"
