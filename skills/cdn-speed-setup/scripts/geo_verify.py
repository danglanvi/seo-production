# Kiểm DNS và TTFB theo vùng bằng Globalping: nhóm VN (theo ASN nhà mạng) và nhóm Mỹ (theo thành phố), 3 loại resolver.
# Không ghi IP. TTFB không tính DNS = tcp + tls + firstByte. Globalping không cho đặt User-Agent.
#   python3 geo_verify.py --domain example.com --path /trang-mau/ --origin-file ~/.cm/example.origin --out work/verify-1.json
# Mỗi nhóm tốn 4 phép đo × số probe của nhóm (VN,US: 40 probe). Quota Globalping: 250 probe/giờ/IP, dùng chung cho mọi lane trên máy.
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdn import classify, globalping, globalping_need, origin_ip, save_json  # noqa: E402

GROUPS = {
    "VN": [{"magic": "AS7552"}, {"magic": "AS45899"}, {"magic": "AS18403"}, {"magic": "AS45903"}, {"magic": "AS24086"}],
    "US": [{"magic": "Ashburn"}, {"magic": "Dallas"}, {"magic": "Los Angeles"}, {"magic": "Chicago"}, {"magic": "San Jose"}],
    "EU": [{"magic": "Frankfurt"}, {"magic": "London"}, {"magic": "Amsterdam"}],
}


def ttfb_nodns(t):
    return (t.get("tcp") or 0) + (t.get("tls") or 0) + (t.get("firstByte") or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--path", default="/")
    ap.add_argument("--origin-file", required=True)
    ap.add_argument("--groups", default="VN,US")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    origin = origin_ip(a.origin_file)
    globalping_need(sum(4 * len(GROUPS[g]) for g in a.groups.split(",")))
    out = {"dns": [], "http": []}
    for grp in a.groups.split(","):
        locs = GROUPS[grp]
        for res in (None, "1.1.1.1", "8.8.8.8"):
            mo = {"query": {"type": "A"}, "protocol": "UDP", "port": 53}
            if res:
                mo["resolver"] = res
            r = globalping({"type": "dns", "target": a.domain, "locations": locs, "measurementOptions": mo})
            for x in r.get("results", []):
                ans = [v.get("value") for v in (x["result"].get("answers") or []) if v.get("type") == "A"]
                row = {"grp": grp, "resolver": res or "probe", "asn": x["probe"].get("asn"), "city": x["probe"].get("city"),
                       "cls": classify(ans, origin)}
                out["dns"].append(row)
                print(row)
        path, _, query = a.path.partition("?")
        req = {"method": "GET", "path": path}
        if query:
            req["query"] = query
        r = globalping({"type": "http", "target": a.domain, "locations": locs,
                        "measurementOptions": {"request": req, "protocol": "HTTPS", "port": 443}})
        for x in r.get("results", []):
            h = {k.lower(): v for k, v in (x["result"].get("headers") or {}).items()}
            row = {"grp": grp, "asn": x["probe"].get("asn"), "city": x["probe"].get("city"), "code": x["result"].get("statusCode"),
                   "server": h.get("server"), "cache": h.get("cdn-cache") or h.get("cf-cache-status"),
                   "ttfb_nodns": ttfb_nodns(x["result"].get("timings") or {})}
            out["http"].append(row)
            print(row)
    save_json(a.out, out)


if __name__ == "__main__":
    main()
