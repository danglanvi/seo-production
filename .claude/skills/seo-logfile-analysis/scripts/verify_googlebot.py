#!/usr/bin/env python3
"""Xác minh IP Googlebot (hoặc Bingbot) trong access log: lọc theo dải IP chính chủ trước, chỉ rDNS phần còn lại. Chỉ stdlib.

Vì sao: ngày 19/10/2026 rDNS tuần tự 429 IP chạy quá 600 giây. Dải IP chính chủ loại phần lớn IP trong vài mili giây,
nên rDNS chỉ chạy cho IP nằm ngoài dải. Script không tự tải dải IP. Tải file trước bằng curl, rồi truyền bằng --ranges:
  https://developers.google.com/static/search/apis/ipranges/googlebot.json            (Googlebot)
  https://developers.google.com/static/search/apis/ipranges/special-crawlers.json     (crawler đặc biệt)
  https://developers.google.com/static/search/apis/ipranges/user-triggered-fetchers.json
  https://www.bing.com/toolbox/bingbot.json                                           (Bingbot)
File dải IP là JSON {"prefixes":[{"ipv4Prefix":"..."},{"ipv6Prefix":"..."}]} hoặc text, mỗi dòng một CIDR.

Ví dụ:
  python3 -B verify_googlebot.py --log a.access_log --log b.access_log.gz --ranges googlebot.json \\
      [--ranges special-crawlers.json] [--bot googlebot|bingbot] [--max-rdns 500] [--workers 16] [--deadline 120] \\
      [--out-dir DIR --write] [--json]
  python3 -B verify_googlebot.py --ips ips.txt --ranges googlebot.json --no-rdns

Mỗi IP có một trạng thái:
  range      nằm trong dải chính chủ. Tính là thật, không cần rDNS.
  rdns       ngoài dải, nhưng rDNS về đúng đuôi tên miền của hãng và forward-confirm ra đúng IP. Tính là thật.
             Số IP nhóm này nhiều nghĩa là file dải IP cũ. Tải lại file.
             Googlebot chỉ nhận đuôi .googlebot.com và .google.com. PTR googleusercontent.com là máy thuê Google Cloud:
             log site agency mẫu 19/10/2026 có 126 IP như vậy, đều giả UA. Fetcher do người dùng kích hoạt: dùng dải
             user-triggered-fetchers.json.
  fake       ngoài dải và rDNS sai hoặc forward-confirm lệch. Tách riêng, không đưa vào phân tích.
  unchecked  ngoài dải, nhưng chưa rDNS (vượt --max-rdns, quá --deadline, hoặc --no-rdns). Không tính là thật.
--crosscheck N: rDNS thử N IP trong dải để đo độ lệch giữa dải IP và rDNS. Chỉ để báo cáo, không đổi trạng thái.

Đầu ra mặc định là bảng tóm tắt, không chứa IP. Mặc định dry-run: không ghi file. Thêm --write với --out-dir để ghi
verified_ips.txt (đưa vào log_clusters.py --verified-ips), fake_ips.txt, unchecked_ips.txt. Các file này chứa IP, giữ trên máy.
Không ghi đè file có sẵn khi thiếu --force.

Mã thoát: 0 = mọi IP thật, 1 = có IP fake, 2 = lỗi (thiếu dải IP, file hỏng, log không có IP bot nào),
3 = còn IP unchecked (ưu tiên hơn mã 1). Không ghi "100% thật" khi mã thoát là 2 hoặc 3.
"""
import argparse
import bisect
import gzip
import ipaddress
import json
import re
import socket
import sys
import threading
import time
from collections import Counter
from pathlib import Path

LINE = re.compile(r"^'?(?:\S+ )?(?P<ip>\S+) \S+ \S+ \[[^\]]+\] \"[^\"]*\" \d{3} \S+(?: \"[^\"]*\" \"(?P<ua>[^\"]*)\")?")
BOTS = {
    "googlebot": (re.compile(r"googlebot|google-inspectiontool|storebot-google|googleother|google-extended", re.I),
                  (".googlebot.com", ".google.com")),
    "bingbot": (re.compile(r"bingbot|msnbot|bingpreview", re.I), (".search.msn.com",)),
}


class Fail(Exception):
    pass


def norm_ip(s):
    try:
        return str(ipaddress.ip_address(s.strip()))
    except ValueError:
        return None


def load_ranges(paths):
    """Đọc file dải IP (JSON prefixes hoặc text CIDR). Trả (v4, v6): hai list (start, end) đã gộp và sắp xếp."""
    nets = []
    for p in paths:
        try:
            raw = Path(p).read_text(encoding="utf-8")
        except OSError as e:
            raise Fail(f"Không đọc được file dải IP {p}: {e}")
        found = []
        if raw.lstrip().startswith("{"):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                raise Fail(f"File dải IP không phải JSON hợp lệ {p}: {e}")
            for item in data.get("prefixes", []):
                cidr = item.get("ipv4Prefix") or item.get("ipv6Prefix")
                if cidr:
                    found.append(cidr)
        else:
            for line in raw.splitlines():
                line = line.split("#", 1)[0].strip()
                if line:
                    found.append(line)
        if not found:
            raise Fail(f"File dải IP không có prefix nào: {p}")
        for c in found:
            try:
                nets.append(ipaddress.ip_network(c, strict=False))
            except ValueError:
                raise Fail(f"Prefix không hợp lệ trong {p}: {c}")
    out = {4: [], 6: []}
    for ver in (4, 6):
        merged = ipaddress.collapse_addresses([n for n in nets if n.version == ver])
        out[ver] = sorted((int(n.network_address), int(n.broadcast_address)) for n in merged)
    return out[4], out[6]


def in_ranges(ip, ranges):
    a = ipaddress.ip_address(ip)
    lst = ranges[0] if a.version == 4 else ranges[1]
    n = int(a)
    i = bisect.bisect_right(lst, (n, float("inf"))) - 1
    return i >= 0 and lst[i][0] <= n <= lst[i][1]


def collect_ips(logs, ips_file, ua_rx):
    """Trả (Counter hit theo IP, số dòng, số dòng không đọc được, số dòng IP không hợp lệ)."""
    hits = Counter()
    lines = unparsed = badip = 0
    if ips_file:
        try:
            text = Path(ips_file).read_text(encoding="utf-8")
        except OSError as e:
            raise Fail(f"Không đọc được file IP {ips_file}: {e}")
        for tok in text.split():
            ip = norm_ip(tok)
            if ip:
                hits[ip] += 1
            else:
                badip += 1
        return hits, 0, 0, badip
    for p in logs:
        op = gzip.open if str(p).endswith(".gz") else open
        try:
            with op(p, "rt", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    lines += 1
                    m = LINE.match(line)
                    if not m:
                        unparsed += 1
                        continue
                    if not ua_rx.search(m["ua"] or ""):
                        continue
                    ip = norm_ip(m["ip"])
                    if ip:
                        hits[ip] += 1
                    else:
                        badip += 1
        except (OSError, EOFError) as e:
            raise Fail(f"Không đọc được log {p}: {e}")
    return hits, lines, unparsed, badip


def host_ok(host, suffixes):
    h = (host or "").lower().rstrip(".")
    return any(h.endswith("." + s.lstrip(".").lower()) for s in suffixes)


def default_reverse(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (OSError, UnicodeError):
        return None


def default_forward(host):
    try:
        return {norm_ip(x[4][0]) for x in socket.getaddrinfo(host, None)}
    except (OSError, UnicodeError):
        return set()


def rdns_verdict(ip, suffixes, reverse, forward):
    host = reverse(ip)
    if not host or not host_ok(host, suffixes):
        return False
    return norm_ip(ip) in {norm_ip(x) for x in forward(host) if x}


def run_rdns(todo, suffixes, reverse, forward, workers, deadline):
    """rDNS song song bằng thread daemon. IP chưa xong khi hết deadline không có trong kết quả."""
    results, queue, lock = {}, list(todo), threading.Lock()

    def work():
        while True:
            with lock:
                if not queue:
                    return
                ip = queue.pop(0)
            ok = rdns_verdict(ip, suffixes, reverse, forward)
            with lock:
                results[ip] = ok

    threads = [threading.Thread(target=work, daemon=True) for _ in range(max(1, min(workers, len(todo) or 1)))]
    for t in threads:
        t.start()
    end = time.monotonic() + deadline
    for t in threads:
        t.join(max(0.0, end - time.monotonic()))
    with lock:
        queue.clear()
        return dict(results)


def classify(hits, ranges, suffixes, reverse, forward, max_rdns, workers, deadline, no_rdns, crosscheck):
    status = {}
    outside = []
    for ip in hits:
        if in_ranges(ip, ranges):
            status[ip] = "range"
        else:
            outside.append(ip)
    outside.sort(key=lambda i: (-hits[i], i))
    todo = [] if no_rdns else outside[:max_rdns]
    res = run_rdns(todo, suffixes, reverse, forward, workers, deadline) if todo else {}
    for ip in outside:
        if ip in res:
            status[ip] = "rdns" if res[ip] else "fake"
        else:
            status[ip] = "unchecked"
    cross = None
    if crosscheck:
        sample = sorted((i for i, s in status.items() if s == "range"), key=lambda i: (-hits[i], i))[:crosscheck]
        r2 = run_rdns(sample, suffixes, reverse, forward, workers, deadline)
        cross = {"sampled": len(r2), "mismatch": sum(1 for v in r2.values() if not v)}
    return status, cross


def summarize(hits, status, stats, cross, rdns_lookups):
    ips = Counter(status.values())
    hit_by = Counter()
    for ip, n in hits.items():
        hit_by[status[ip]] += n
    total_ip, total_hit = len(hits), sum(hits.values())
    real_ip = ips["range"] + ips["rdns"]
    real_hit = hit_by["range"] + hit_by["rdns"]
    return {
        "lines": stats["lines"], "unparsed_lines": stats["unparsed"], "invalid_ip_lines": stats["badip"],
        "ips": total_ip, "hits": total_hit,
        "ips_by_status": {k: ips[k] for k in ("range", "rdns", "fake", "unchecked")},
        "hits_by_status": {k: hit_by[k] for k in ("range", "rdns", "fake", "unchecked")},
        "real_ip_pct": round(100 * real_ip / total_ip, 1) if total_ip else 0.0,
        "real_hit_pct": round(100 * real_hit / total_hit, 1) if total_hit else 0.0,
        "rdns_lookups": rdns_lookups, "crosscheck": cross,
    }


def print_table(s):
    print(f"Dòng log: {s['lines']} · không đọc được: {s['unparsed_lines']} · dòng IP không hợp lệ: {s['invalid_ip_lines']}")
    print(f"IP bot tự khai: {s['ips']} · hit: {s['hits']} · số lần rDNS: {s['rdns_lookups']}")
    print("| trạng thái | IP | hit |")
    print("|---|---|---|")
    for k in ("range", "rdns", "fake", "unchecked"):
        print(f"| {k} | {s['ips_by_status'][k]} | {s['hits_by_status'][k]} |")
    print(f"Thật: {s['real_ip_pct']}% IP, {s['real_hit_pct']}% hit")
    if s["ips_by_status"]["rdns"]:
        print(f"Lưu ý: {s['ips_by_status']['rdns']} IP chỉ qua rDNS, ngoài dải. Tải lại file dải IP rồi chạy lại.")
    if s["ips_by_status"]["unchecked"]:
        print(f"Cảnh báo: {s['ips_by_status']['unchecked']} IP chưa kiểm. Không tính vào phần trăm thật.", file=sys.stderr)
    if s["crosscheck"]:
        c = s["crosscheck"]
        print(f"Kiểm chéo: rDNS lệch ở {c['mismatch']}/{c['sampled']} IP trong dải.")


def write_outputs(out_dir, status, hits, write, force):
    names = {"verified_ips.txt": ("range", "rdns"), "fake_ips.txt": ("fake",), "unchecked_ips.txt": ("unchecked",)}
    plan = {n: sorted(i for i, s in status.items() if s in keep) for n, keep in names.items()}
    for n, ips in plan.items():
        path = Path(out_dir) / n
        if not write:
            print(f"[dry-run] sẽ ghi {path} ({len(ips)} IP)")
            continue
        if path.exists() and not force:
            raise Fail(f"{path} đã có. Thêm --force để ghi đè.")
    if not write:
        return
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for n, ips in plan.items():
        (Path(out_dir) / n).write_text("".join(i + "\n" for i in ips), encoding="utf-8")
        print(f"Đã ghi {Path(out_dir) / n} ({len(ips)} IP)")


def main(argv=None, reverse=None, forward=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", action="append", default=[], help="access log, .gz đọc thẳng; lặp cho nhiều file")
    ap.add_argument("--ips", help="file IP, mỗi dòng một IP (thay cho --log)")
    ap.add_argument("--ranges", action="append", default=[], help="file dải IP chính chủ; lặp cho nhiều file")
    ap.add_argument("--bot", choices=sorted(BOTS), default="googlebot")
    ap.add_argument("--suffix", action="append", help="đuôi tên miền rDNS hợp lệ, ghi đè mặc định của --bot; lặp được")
    ap.add_argument("--rdns-only", action="store_true", help="cho phép chạy không có --ranges (chậm, rDNS mọi IP)")
    ap.add_argument("--no-rdns", action="store_true", help="không rDNS; IP ngoài dải thành unchecked")
    ap.add_argument("--max-rdns", type=int, default=500, help="số IP ngoài dải tối đa được rDNS, ưu tiên IP nhiều hit (mặc định 500)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--deadline", type=float, default=120.0, help="tổng giây tối đa cho rDNS (mặc định 120)")
    ap.add_argument("--crosscheck", type=int, default=0, help="rDNS thử N IP trong dải để đo độ lệch")
    ap.add_argument("--out-dir")
    ap.add_argument("--write", action="store_true", help="ghi file vào --out-dir (mặc định dry-run)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    ua_rx, default_suffixes = BOTS[a.bot]
    suffixes = tuple(a.suffix) if a.suffix else default_suffixes
    reverse = reverse or default_reverse
    forward = forward or default_forward
    try:
        if not a.log and not a.ips:
            raise Fail("Cần --log hoặc --ips.")
        if not a.ranges and not a.rdns_only:
            raise Fail("Thiếu --ranges. Tải file dải IP chính chủ (xem --help). Muốn rDNS mọi IP thì thêm --rdns-only.")
        if a.write and not a.out_dir:
            raise Fail("--write cần --out-dir.")
        ranges = load_ranges(a.ranges) if a.ranges else ([], [])
        hits, lines, unparsed, badip = collect_ips(a.log, a.ips, ua_rx)
        if not hits:
            raise Fail(f"Không có IP {a.bot} nào trong đầu vào (đọc {lines} dòng, {unparsed} dòng không đọc được). Không ghi 100% thật.")
        status, cross = classify(hits, ranges, suffixes, reverse, forward, a.max_rdns, a.workers, a.deadline, a.no_rdns, a.crosscheck)
        summ = summarize(hits, status, {"lines": lines, "unparsed": unparsed, "badip": badip}, cross,
                         sum(1 for s in status.values() if s in ("rdns", "fake")))
        if a.json:
            print(json.dumps(summ, ensure_ascii=False, indent=1))
        else:
            print_table(summ)
        if a.out_dir:
            write_outputs(a.out_dir, status, hits, a.write, a.force)
        elif a.write:
            raise Fail("--write cần --out-dir.")
    except Fail as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    if summ["ips_by_status"]["unchecked"]:
        return 3
    return 1 if summ["ips_by_status"]["fake"] else 0


if __name__ == "__main__":
    sys.exit(main())
