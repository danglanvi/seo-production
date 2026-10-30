#!/usr/bin/env python3
"""Gom URL ứng viên cho nhánh C (301 hoặc 410) từ access log của origin và log của CDN. Chỉ đọc file, không gọi site.

Giữ đường dẫn trả 301, 302, 307, 308, 404 hoặc 410 mà có ít nhất một lượt Googlebot đã xác minh hoặc một lượt người dùng có referer.
Bỏ đường dẫn không phải trang: wp-*, feed, file tĩnh, .md, llms.txt, đường dẫn rác, đường dò quét, đuôi phụ của bài.
Giữ path ghép %20 và đuôi ":XXX": đó là link hỏng nội bộ, cần người đọc, không tự bỏ.
Output không chứa IP và không chứa UA. Ra TSV tương thích --urls của pick_target.py (cột url, clicks, dich_goi_y, tam_dong, bo)
cộng cột số liệu log. clicks để trống: điền từ GSC theo references/bo-bai.md mục 4.2.
Ca thật 27/10/2026, site agency mẫu: log origin 7 ngày và log CDN 2 ngày cho 8.826 và 2.143 đường dẫn, còn 516 sau bộ lọc;
sau khi kiểm mã hiện tại và loại URL đã có rule tĩnh, 225 URL cần quyết (54 301 qua PHP, 158 404, 13 410).

Dùng (chỉ stdlib):
  python3 log_urls_chet.py --site-host example.com --log access.log [--log access.log.1.gz ...]
                           [--cdn-log cdn-ngay1.log --cdn-format bunny] [--verified-ips verified_ips.txt]
                           [--since 2026-10-20] [--until 2026-10-27T09:00] [--drop-regex RE ...] --out urls_ung_vien.tsv
  --log          access log của origin (định dạng combined; OpenLiteSpeed có thể thêm host phía trước IP). .gz đọc thẳng.
  --cdn-log      log CDN. --cdn-format bunny: dòng ngăn bằng "|", cột 0 cache, 1 mã, 2 giờ (ms epoch UTC), 5 IP, 6 referer, 7 URL đầy đủ, 9 UA.
  --verified-ips verified_ips.txt của seo-logfile-analysis/scripts/verify_googlebot.py. Thiếu file: nhận IP đầu 66.249. và 2001:4860:4801:
                 có UA Google, in cảnh báo "chưa xác minh". UA Google từ IP khác không tính là Googlebot.
  --drop-regex   bỏ thêm đường dẫn khớp RE (lặp lại được), ví dụ đường dẫn riêng của site.
Cột out: url, clicks, dich_goi_y, tam_dong, bo, ma_log, luot, googlebot, nguoi_ref, noi_bo, ma_khac, lan_cuoi, nguon, ref_top.
  nguoi_ref = lượt người dùng có referer (loại UA bot, curl, python...). noi_bo = trong đó referer là chính site.
  ma_khac = mã khác của cùng đường dẫn (ví dụ 200:12): đường dẫn có mã 200 có thể đã sống lại.
Mã thoát: 0 xong · 2 input sai hoặc một file log không đọc được dòng nào (không ghi "0 URL" cho file đó).
"""
import argparse
import csv
import gzip
import ipaddress
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

KEEP = {"301", "302", "307", "308", "404", "410"}
LINE = re.compile(r"^'?(?:\S+ )?(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] \"(?P<method>[A-Z]+) (?P<path>\S+)(?: [^\"]*)?\" "
                  r"(?P<status>\d{3}) \S+(?: \"(?P<ref>[^\"]*)\" \"(?P<ua>[^\"]*)\")?")
BOT = re.compile(r"bot|crawl|spider|slurp|curl|python|wget|headless|lighthouse|monitor|scan|http-client|go-http|java|okhttp|axios|node-fetch|"
                 r"libwww|externalhit|preview|fetch|check|uptime|semrush|ahrefs|mj12|dataforseo|bytespider|gpt|claude|perplexity|bing|yandex|"
                 r"petal|baidu|duckduck|facebook|meta-|amazon|google", re.I)
STATIC = re.compile(r"\.(jpe?g|png|gif|webp|avif|svg|css|js|mjs|json|woff2?|ttf|otf|eot|ico|xml|txt|map|pdf|mp[34]|zip|gz|rar|tar|sql|bak|"
                    r"php\d?|asp|aspx|jsp|cgi|env|ini|ya?ml|log|md|html?|xsl|swf|exe|dll|sh|py|rb|git)$", re.I)
SCAN = re.compile(r"/(\.well-known|\.git|\.env|phpmyadmin|cpanel|administrator|backup|sql|aws|cgi-bin)(/.*)?$|^/(admin|db)(/.*)?$", re.I)
TAIL = re.compile(r"/(comment-page-\d+|amp|trackback|embed)/?$", re.I)
JUNK = re.compile(r"about:blank|\*|%22|%27|%3C|%3E|%E2%80%9|\\\\|//|\s", re.I)
GOOGLE_PREFIX = ("66.249.", "2001:4860:4801:")


class Fail(Exception):
    pass


def ly_do_bo(path, drop):
    if path in ("/", ""):
        return "trang chủ"
    if re.search(r"(^|/)wp-|/xmlrpc|/feed/?$", path, re.I):
        return "wp-*, feed"
    if re.search(r"llms(-full)?\.txt", path, re.I):
        return ".md, llms.txt"
    if STATIC.search(path.rstrip("/")):
        return "file tĩnh, .md"
    if JUNK.search(path):
        return "đường dẫn rác"
    if SCAN.search(path):
        return "đường dẫn dò quét"
    if TAIL.search(path):
        return "đuôi phụ của bài"
    for rx in drop:
        if rx.search(path):
            return "--drop-regex"
    return None


def parse_time(s):
    return datetime.strptime(s.split()[0], "%d/%b/%Y:%H:%M:%S")


def doc_combined(p):
    op = gzip.open if str(p).endswith(".gz") else open
    n = ok = 0
    with op(p, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            n += 1
            m = LINE.match(line)
            if not m:
                continue
            ok += 1
            try:
                t = parse_time(m["time"])
            except ValueError:
                continue
            yield dict(ip=m["ip"], t=t, method=m["method"], path=m["path"].split("?")[0], q="?" in m["path"], code=m["status"],
                       ref=m["ref"] or "-", ua=m["ua"] or "-")
    if ok == 0:
        raise Fail(f"Không đọc được dòng nào trong {p}. Không ghi '0 URL' cho file này.")


def doc_bunny(p):
    op = gzip.open if str(p).endswith(".gz") else open
    ok = 0
    with op(p, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            c = line.rstrip("\n").split("|")
            if len(c) < 12:
                continue
            u = urlsplit(c[7])
            if not u.path:
                continue
            try:
                t = datetime.fromtimestamp(int(c[2]) / 1000, timezone.utc).replace(tzinfo=None)
            except ValueError:
                continue
            ok += 1
            yield dict(ip=c[5], t=t, method="GET", path=u.path, q=bool(u.query), code=c[1], ref=c[6] or "-", ua=c[9] or "-")
    if ok == 0:
        raise Fail(f"Không đọc được dòng nào trong {p} (--cdn-format bunny). Không ghi '0 URL' cho file này.")


def doc_ips(p):
    out = set()
    for tok in Path(p).read_text(encoding="utf-8").split():
        try:
            out.add(str(ipaddress.ip_address(tok.strip())))
        except ValueError:
            pass
    if not out:
        raise Fail(f"{p} không có IP nào.")
    return out


def norm_ip(s):
    try:
        return str(ipaddress.ip_address(s))
    except ValueError:
        return s


def gom(nguon, a, ips):
    host = a.site_host.lower().removeprefix("www.")
    drop = [re.compile(x) for x in a.drop_regex]
    since = datetime.fromisoformat(a.since) if a.since else None
    until = datetime.fromisoformat(a.until) if a.until else None
    st = defaultdict(lambda: dict(ma=Counter(), gb=0, ur=0, ir=0, ref=Counter(), last=None, nguon=set()))
    khac = defaultdict(Counter)
    bo = Counter()
    tong = 0
    for ten, it in nguon:
        for r in it:
            if r["method"] not in ("GET", "HEAD") or (since and r["t"] < since) or (until and r["t"] > until):
                continue
            tong += 1
            p = r["path"]
            khac[p][r["code"]] += 1
            if r["code"] not in KEEP:
                continue
            why = ly_do_bo(p, drop)
            if why:
                bo[why] += 1
                continue
            s = st[p]
            s["ma"][r["code"]] += 1
            s["nguon"].add(ten)
            s["last"] = max(s["last"] or r["t"], r["t"])
            google = "Google" in r["ua"] and (norm_ip(r["ip"]) in ips if ips is not None else r["ip"].startswith(GOOGLE_PREFIX))
            if google:
                s["gb"] += 1
            elif r["ref"] not in ("-", "") and not BOT.search(r["ua"]):
                s["ur"] += 1
                rh = (urlsplit(r["ref"]).netloc or "").lower().removeprefix("www.")
                if rh == host or rh.endswith("." + host):
                    s["ir"] += 1
                if rh:
                    s["ref"][rh] += 1
    rows = []
    for p, s in st.items():
        if not (s["gb"] or s["ur"]):
            continue
        ma_khac = {k: v for k, v in khac[p].items() if k not in KEEP}
        rows.append([p, "", "", "", "", ",".join(f"{k}:{v}" for k, v in s["ma"].most_common()), sum(s["ma"].values()), s["gb"], s["ur"], s["ir"],
                     ",".join(f"{k}:{v}" for k, v in ma_khac.items()), s["last"].strftime("%Y-%m-%d %H:%M"), "+".join(sorted(s["nguon"])),
                     ",".join(f"{k}:{v}" for k, v in s["ref"].most_common(3))])
    rows.sort(key=lambda r: (-(r[7] + r[8]), r[0]))
    return rows, bo, tong, len(st)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site-host", required=True)
    ap.add_argument("--log", action="append", default=[])
    ap.add_argument("--cdn-log", action="append", default=[])
    ap.add_argument("--cdn-format", choices=["bunny"])
    ap.add_argument("--verified-ips")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--drop-regex", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if not (a.log or a.cdn_log):
        ap.error("cần --log hoặc --cdn-log")
    if a.cdn_log and not a.cdn_format:
        ap.error("--cdn-log cần --cdn-format")
    try:
        ips = doc_ips(a.verified_ips) if a.verified_ips else None
        if ips is None:
            print("CẢNH BÁO: chưa xác minh IP Googlebot (thiếu --verified-ips). Cột googlebot chỉ dựa trên UA và dải IP đầu.", file=sys.stderr)
        for p in a.log + a.cdn_log:
            if not Path(p).is_file():
                raise Fail(f"Không thấy file {p}")
        nguon = [("origin", doc_combined(p)) for p in a.log] + [("cdn", doc_bunny(p)) for p in a.cdn_log]
        rows, bo, tong, so_path = gom(nguon, a, ips)
    except (Fail, ValueError, OSError) as e:
        print(f"Lỗi input: {e}", file=sys.stderr)
        return 2
    if Path(a.out).exists():
        print(f"{a.out} đã có. Script không ghi đè.", file=sys.stderr)
        return 2
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["url", "clicks", "dich_goi_y", "tam_dong", "bo", "ma_log", "luot", "googlebot", "nguoi_ref", "noi_bo", "ma_khac",
                    "lan_cuoi", "nguon", "ref_top"])
        w.writerows(rows)
    print(f"LOG_URLS_CHET dong={tong} duong_dan_trang_loi={so_path} ung_vien={len(rows)} loai={dict(bo)}", file=sys.stderr)
    print(f"Ghi {len(rows)} URL vào {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
