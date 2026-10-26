#!/usr/bin/env python3
"""Hai kiểm từ access log của site WordPress. Chỉ stdlib, chạy trên máy, output không chứa IP.

uploads    Hit của mọi UA vào /wp-content/uploads/ trả 404 hoặc 410: số hit, số file, tổng byte, % byte trên mọi
           response, trung vị byte, file và referer ngoài site nhiều hit nhất. Trung vị trên --max-bytes (mặc định
           2048) nghĩa là WordPress dựng cả trang lỗi cho file thiếu. Ca thật gtvseo.com 06–19/10/2026: 284.240 hit,
           45,2/120,0 GB băng thông, khoảng 95 KB mỗi response. Sau rule 404 tĩnh ngày 21/10: 1.249 byte.
redirects  Hit HTML của Googlebot từ IP đã xác minh (verified_ips.txt của verify_googlebot.py). Bỏ file tĩnh, feed,
           /wp-*, .php và URL có query. Liệt kê URL trả 3xx, đếm 404 và 410. --remove-list: URL trong danh sách bỏ
           đã duyệt; hit 410 vào URL ngoài danh sách bị gắn cờ. --hub-urls: trang danh mục hoặc hub.
           --probe: GET từng URL 3xx, tự theo tối đa 5 bước, lấy status hiện tại, số bước, đích cuối, status đích,
           rồi chia nhóm. Probe gọi site thật: chỉ chạy khi được phép, giữ --workers thấp.

Ví dụ:
  python3 -B log_checks.py uploads --log a.access_log [--log b.access_log.gz] [--site https://example.com] \\
      [--from 2026-10-06 --to 2026-10-19] [--max-bytes 2048] [--json]
  python3 -B log_checks.py redirects --log a.access_log --site https://example.com --verified-ips verified_ips.txt \\
      [--remove-list bo.txt] [--hub-urls hub.txt] [--probe --workers 4 --timeout 10 --deadline 300] \\
      [--out-dir DIR [--force]] [--json]

Nhóm redirect (một URL có thể thuộc nhiều nhóm):
  da_doi           status hiện tại không còn là 3xx (đã đổi sang 200, 404 hoặc 410)
  chuoi            từ 2 bước trở lên: rút về 1 bước
  dich_khong_200   đích cuối không trả 200, gồm vòng lặp và quá 5 bước: sửa đích
  ve_trang_chu     đích cuối là trang chủ: nguy cơ soft 404
  tam_thoi         bước đầu là 302, 303 hoặc 307
  ve_hub           đích cuối nằm trong --hub-urls: rà từng URL
  thieu_gach_cuoi  1 bước, đích chỉ thêm "/" cuối
  mot_buoc_200     1 bước, đích 200, không thuộc nhóm trên
  chua_do          bật --probe nhưng chưa đo xong (lỗi mạng hoặc quá --deadline)
Không có --probe: chỉ có nhóm tam_thoi theo mã trong log.

Mã thoát: 0 = không có cờ, 1 = có cờ (trung vị upload thiếu trên ngưỡng; nhóm chuoi, dich_khong_200, ve_trang_chu,
tam_thoi, ve_hub; 410 ngoài danh sách bỏ), 2 = lỗi đầu vào (file không đọc được dòng nào, thiếu file IP, không có hit
Googlebot đã xác minh), 3 = còn URL chưa probe xong (ưu tiên hơn mã 1).
"""
import argparse
import gzip
import http.client
import ipaddress
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_clusters import ASSET, LINE, bot_of, day_of, norm  # noqa: E402

REDIR = (301, 302, 303, 307, 308)
TEMP = (302, 303, 307)
FLAG_GROUPS = ("chuoi", "dich_khong_200", "ve_trang_chu", "tam_thoi", "ve_hub")
FEED = re.compile(r"/feed/?$")
UA = "Mozilla/5.0 (compatible; seo-logfile-analysis log_checks.py)"


class Fail(Exception):
    pass


def norm_ip(s):
    try:
        return str(ipaddress.ip_address(s.strip()))
    except ValueError:
        return s


def split_path(raw):
    """Trả (host, path, query). Log thường chỉ có path; một số dòng ghi URL đầy đủ."""
    if raw.startswith("http"):
        p = urlsplit(raw)
        return p.netloc.lower().removeprefix("www."), p.path or "/", p.query
    path, _, query = raw.partition("?")
    return "", path or "/", query


def rows(paths, date_from, date_to, stats):
    for p in paths:
        st = stats.setdefault(str(p), {"lines": 0, "parsed": 0})
        op = gzip.open if str(p).endswith(".gz") else open
        try:
            with op(p, "rt", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    st["lines"] += 1
                    m = LINE.match(line)
                    if not m:
                        continue
                    st["parsed"] += 1
                    day = day_of(m["time"])
                    if (date_from and day and day < date_from) or (date_to and day and day > date_to):
                        continue
                    yield m
        except (OSError, EOFError) as e:
            raise Fail(f"Không đọc được log {p}: {e}")


def check_files(stats):
    bad = [f for f, s in stats.items() if s["parsed"] == 0]
    if bad:
        raise Fail("Không đọc được dòng nào trong: " + ", ".join(bad) + ". Không ghi '0 lỗi' cho file này.")


def read_list(path, what):
    try:
        return [t for t in Path(path).read_text(encoding="utf-8").split() if t.strip()]
    except OSError as e:
        raise Fail(f"Không đọc được {what} {path}: {e}")


def gb(n):
    return f"{n / 1e9:.1f} GB" if n >= 1e8 else f"{n / 1e6:.1f} MB"


def cmd_uploads(a):
    host = urlparse(a.site).netloc.lower().removeprefix("www.") if a.site else None
    stats, total_bytes, total_hits = {}, 0, 0
    sizes, per_file, refs, status = [], defaultdict(lambda: [0, 0]), Counter(), Counter()
    for m in rows(a.log, a.date_from, a.date_to, stats):
        b = int(m["bytes"]) if m["bytes"].isdigit() else 0
        total_bytes += b
        total_hits += 1
        path = split_path(m["path"])[1]
        if not path.startswith("/wp-content/uploads/") or m["status"] not in ("404", "410"):
            continue
        sizes.append(b)
        per_file[path][0] += 1
        per_file[path][1] += b
        status[m["status"]] += 1
        r = urlparse(m["ref"] or "").netloc.lower().removeprefix("www.")
        if r and r != host:
            refs[r] += 1
    check_files(stats)
    miss = sum(sizes)
    med = statistics.median(sizes) if sizes else 0
    s = {"lines": sum(v["lines"] for v in stats.values()), "parsed": sum(v["parsed"] for v in stats.values()),
         "hits_all": total_hits, "bytes_all": total_bytes, "missing_hits": len(sizes), "missing_files": len(per_file),
         "status": dict(status), "missing_bytes": miss,
         "missing_bytes_pct": round(100 * miss / total_bytes, 1) if total_bytes else 0.0,
         "median_bytes": med, "over_max": sum(1 for x in sizes if x > a.max_bytes), "max_bytes": a.max_bytes,
         "top_files": [{"path": p, "hits": v[0], "avg_bytes": round(v[1] / v[0])}
                       for p, v in sorted(per_file.items(), key=lambda kv: -kv[1][0])[:15]],
         "top_referer_hosts": refs.most_common(10)}
    flag = bool(sizes) and med > a.max_bytes
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return 1 if flag else 0
    print("# File upload thiếu trả 404/410 (mọi UA)\n")
    print(f"- Dòng log: {s['lines']}, đọc được: {s['parsed']}. Response trong khung: {total_hits}, {gb(total_bytes)}.")
    print(f"- Hit vào file thiếu trong /wp-content/uploads/: {s['missing_hits']} hit, {s['missing_files']} file, "
          f"mã {s['status']}.")
    print(f"- Dung lượng: {gb(miss)} = {s['missing_bytes_pct']}% dung lượng mọi response. Trung vị {med:.0f} byte "
          f"mỗi response; {s['over_max']} response trên {a.max_bytes} byte.")
    if flag:
        print(f"- Cờ: trung vị trên {a.max_bytes} byte. WordPress đang dựng cả trang lỗi cho file thiếu.")
    print("\n| File | Hit | Byte TB |\n|---|---|---|")
    for r in s["top_files"]:
        print(f"| {r['path']} | {r['hits']} | {r['avg_bytes']} |")
    print("\n| Referer ngoài site | Hit |\n|---|---|")
    for h, n in s["top_referer_hosts"]:
        print(f"| {h} | {n} |")
    return 1 if flag else 0


def default_fetch(url, timeout):
    p = urlsplit(url)
    cls = http.client.HTTPSConnection if p.scheme == "https" else http.client.HTTPConnection
    conn = cls(p.netloc, timeout=timeout)
    try:
        conn.request("GET", (p.path or "/") + ("?" + p.query if p.query else ""), headers={"User-Agent": UA})
        r = conn.getresponse()
        return r.status, r.getheader("Location")
    finally:
        conn.close()


def trace(url, fetch, max_hops=5):
    chain, first = [url], None
    while True:
        st, loc = fetch(chain[-1])
        first = st if first is None else first
        if st in REDIR and loc:
            nxt = urljoin(chain[-1], loc)
            if nxt in chain or len(chain) > max_hops:
                return {"status_hien_tai": first, "so_buoc": len(chain), "dich_cuoi": nxt,
                        "status_dich": "vong_lap" if nxt in chain else "qua_5_buoc"}
            chain.append(nxt)
            continue
        return {"status_hien_tai": first, "so_buoc": len(chain) - 1, "dich_cuoi": chain[-1], "status_dich": st}


def probe_all(urls, fetch, workers, deadline):
    res = {}
    ex = ThreadPoolExecutor(max_workers=max(1, workers))
    futs = {ex.submit(trace, u, fetch): u for u in urls}
    done, _ = wait(futs, timeout=deadline)
    for f in done:
        try:
            res[futs[f]] = f.result()
        except (OSError, http.client.HTTPException, ValueError):
            pass
    ex.shutdown(wait=False, cancel_futures=True)
    return res


def groups(path, codes, pr, probing, hubs):
    if not probing:
        return ["tam_thoi"] if any(int(k) in TEMP for k in codes) else []
    if pr is None:
        return ["chua_do"]
    first, hops, final, fst = pr["status_hien_tai"], pr["so_buoc"], pr["dich_cuoi"], pr["status_dich"]
    if first not in REDIR:
        return ["da_doi"]
    g = []
    if hops >= 2:
        g.append("chuoi")
    if fst != 200:
        g.append("dich_khong_200")
    if urlsplit(final).path in ("", "/") and path != "/":
        g.append("ve_trang_chu")
    if first in TEMP:
        g.append("tam_thoi")
    if norm(final) in hubs:
        g.append("ve_hub")
    if not g:
        g.append("thieu_gach_cuoi" if urlsplit(final).path == path + "/" else "mot_buoc_200")
    return g


def write_tsv(out_dir, files, force):
    out = Path(out_dir)
    for name in files:
        if (out / name).exists() and not force:
            raise Fail(f"{out / name} đã có. Thêm --force để ghi đè.")
    out.mkdir(parents=True, exist_ok=True)
    for name, (head, body) in files.items():
        (out / name).write_text("\t".join(head) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in body),
                                encoding="utf-8")
        print(f"Đã ghi {out / name} ({len(body)} dòng)", file=sys.stderr)


def cmd_redirects(a, fetch):
    site = urlparse(a.site)
    host = site.netloc.lower().removeprefix("www.")
    base = f"{site.scheme or 'https'}://{site.netloc}"
    verified = {norm_ip(t) for t in read_list(a.verified_ips, "file IP đã xác minh")}
    if not verified:
        raise Fail("File IP đã xác minh rỗng. Chạy verify_googlebot.py --write trước.")
    remove = {norm(u) for u in read_list(a.remove_list, "danh sách bỏ")} if a.remove_list else None
    hubs = {norm(u) for u in read_list(a.hub_urls, "danh sách hub")} if a.hub_urls else set()
    stats, c = {}, Counter()
    hits, codes = Counter(), defaultdict(Counter)
    gone = {"404": Counter(), "410": Counter()}
    for m in rows(a.log, a.date_from, a.date_to, stats):
        if bot_of(m["ua"]) != "googlebot":
            continue
        if norm_ip(m["ip"]) not in verified:
            c["tu_khai"] += 1
            continue
        if m["method"] not in ("GET", "HEAD"):
            continue
        h, path, query = split_path(m["path"])
        if h and h != host:
            continue
        if query:
            c["co_query"] += 1
            continue
        if ASSET.search(path) or path.startswith("/wp-") or path.endswith(".php") or FEED.search(path):
            c["khong_html"] += 1
            continue
        c["html"] += 1
        st = int(m["status"])
        if st in REDIR:
            hits[path] += 1
            codes[path][st] += 1
        elif m["status"] in gone:
            gone[m["status"]][norm(base + path)] += 1
    check_files(stats)
    if not c["html"]:
        raise Fail(f"Không có hit HTML nào của Googlebot từ IP đã xác minh ({c['tu_khai']} hit tự khai bị bỏ). "
                   "Không ghi '0 redirect'.")
    paths = sorted(hits, key=lambda p: (-hits[p], p))
    probed = probe_all([base + p for p in paths], fetch, a.workers, a.deadline) if a.probe else {}
    table = []
    for p in paths:
        pr = probed.get(base + p)
        g = groups(p, codes[p], pr, a.probe, hubs)
        table.append({"hit_googlebot": hits[p], "url": base + p, "ma_trong_log": dict(codes[p]),
                      **(pr or {"status_hien_tai": "", "so_buoc": "", "dich_cuoi": "", "status_dich": ""}), "nhom": g})
    by_group = defaultdict(lambda: [0, 0])
    for r in table:
        for g in r["nhom"]:
            by_group[g][0] += 1
            by_group[g][1] += r["hit_googlebot"]
    gone_rows = [(u, st, n, ("khong_ro" if remove is None else "co" if u in remove else "khong"))
                 for st in ("410", "404") for u, n in gone[st].most_common()]
    outside = [r for r in gone_rows if r[1] == "410" and r[3] == "khong"]
    log_codes = Counter()
    for p in paths:
        log_codes.update(codes[p])
    s = {"lines": sum(v["lines"] for v in stats.values()), "parsed": sum(v["parsed"] for v in stats.values()),
         "html_hits": c["html"], "skipped": {"tu_khai": c["tu_khai"], "co_query": c["co_query"],
                                              "khong_html": c["khong_html"]},
         "redirect_urls": len(paths), "redirect_hits": sum(hits.values()), "log_codes": dict(log_codes),
         "hits_404": sum(gone["404"].values()), "urls_404": len(gone["404"]),
         "hits_410": sum(gone["410"].values()), "urls_410": len(gone["410"]),
         "urls_410_ngoai_danh_sach": None if remove is None else len(outside),
         "hits_410_ngoai_danh_sach": None if remove is None else sum(r[2] for r in outside),
         "probed": bool(a.probe), "groups": {g: {"urls": v[0], "hits": v[1]} for g, v in by_group.items()},
         "rows": table}
    if a.out_dir:
        write_tsv(a.out_dir, {
            "redirects.tsv": (["hit_googlebot", "url", "ma_trong_log", "status_hien_tai", "so_buoc", "dich_cuoi",
                               "status_dich", "nhom"],
                              [[r["hit_googlebot"], r["url"], json.dumps(r["ma_trong_log"]), r["status_hien_tai"],
                                r["so_buoc"], r["dich_cuoi"], r["status_dich"], ",".join(r["nhom"])] for r in table]),
            "status_404_410.tsv": (["url", "status", "hit_googlebot", "trong_danh_sach_bo"], gone_rows)}, a.force)
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
    else:
        print("# Redirect và 404/410 — Googlebot đã xác minh\n")
        print(f"- Dòng log: {s['lines']}, đọc được: {s['parsed']}. Hit HTML của Googlebot đã xác minh: {c['html']}. "
              f"Bỏ: {c['tu_khai']} hit tự khai từ IP chưa xác minh, {c['co_query']} hit URL có query, "
              f"{c['khong_html']} hit không phải HTML.")
        print(f"- 3xx: {s['redirect_urls']} URL, {s['redirect_hits']} hit. Mã trong log: {s['log_codes']}.")
        print(f"- 404: {s['hits_404']} hit, {s['urls_404']} URL. 410: {s['hits_410']} hit, {s['urls_410']} URL.")
        if remove is None:
            print("- Thiếu --remove-list: chưa phân được 410 đúng hay sai danh sách bỏ.")
        else:
            print(f"- Cờ 410 ngoài danh sách bỏ: {len(outside)} URL, {s['hits_410_ngoai_danh_sach']} hit.")
        if s["hits_410"] > s["hits_404"]:
            print("- 410 nhiều hơn 404: theme có thể đổi mọi 404 thành 410. Kiểm URL ngẫu nhiên phải trả 404.")
        if not a.probe:
            print("- Chưa probe: nhóm chỉ dựa vào mã trong log. Thêm --probe để đo đích cuối.")
        print("\n| Nhóm | URL | Hit |\n|---|---|---|")
        for g, v in sorted(by_group.items(), key=lambda kv: -kv[1][1]):
            print(f"| {g} | {v[0]} | {v[1]} |")
        print("\n| Hit | URL | Mã log | Status hiện tại | Số bước | Đích cuối | Status đích | Nhóm |")
        print("|---|---|---|---|---|---|---|---|")
        for r in table[:25]:
            print(f"| {r['hit_googlebot']} | {r['url']} | {r['ma_trong_log']} | {r['status_hien_tai']} | "
                  f"{r['so_buoc']} | {r['dich_cuoi']} | {r['status_dich']} | {', '.join(r['nhom'])} |")
    if any("chua_do" in r["nhom"] for r in table):
        print(f"Cảnh báo: {by_group['chua_do'][0]} URL chưa probe xong.", file=sys.stderr)
        return 3
    flagged = any(g in FLAG_GROUPS for r in table for g in r["nhom"]) or bool(outside)
    return 1 if flagged else 0


def main(argv=None, fetch=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("uploads", "redirects"):
        p = sub.add_parser(name)
        p.add_argument("--log", action="append", required=True, help="access log, .gz đọc thẳng; lặp cho nhiều file")
        p.add_argument("--from", dest="date_from")
        p.add_argument("--to", dest="date_to")
        p.add_argument("--json", action="store_true")
        if name == "uploads":
            p.add_argument("--site", help="gốc site, để bỏ referer cùng site")
            p.add_argument("--max-bytes", type=int, default=2048)
        else:
            p.add_argument("--site", required=True, help="gốc site, ví dụ https://example.com")
            p.add_argument("--verified-ips", required=True, help="verified_ips.txt của verify_googlebot.py")
            p.add_argument("--remove-list", help="URL trong danh sách bỏ đã duyệt, mỗi dòng một URL")
            p.add_argument("--hub-urls", help="URL trang danh mục hoặc hub, mỗi dòng một URL")
            p.add_argument("--probe", action="store_true", help="GET từng URL 3xx trên site thật")
            p.add_argument("--workers", type=int, default=4)
            p.add_argument("--timeout", type=float, default=10.0)
            p.add_argument("--deadline", type=float, default=300.0, help="tổng giây tối đa cho probe")
            p.add_argument("--out-dir")
            p.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "uploads":
            return cmd_uploads(a)
        return cmd_redirects(a, fetch or (lambda u: default_fetch(u, a.timeout)))
    except Fail as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
