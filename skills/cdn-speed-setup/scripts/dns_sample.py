# Lấy mẫu câu trả lời DNS nhiều vòng để đo tỉ lệ khách nhận origin hay CDN (nhánh B).
#   Máy local:  python3 dns_sample.py local --domain example.com --ns ns1.example-dns.com --origin-file ~/.cm/x.origin --rounds 50 --out work/dnsloop-1.json
#   Globalping: python3 dns_sample.py globalping --domain example.com --country VN --origin-file ~/.cm/x.origin --rounds 10 --out work/vnsample-1.json
# Chế độ globalping tốn 3 × limit probe mỗi vòng. Quota 250 probe/giờ/IP dùng chung: 10 vòng × 3 × 8 = 240 probe, gần hết quota.
# Không ghi IP. Ghi giờ từng lượt để tách mẫu trước và sau một lần sửa script.
import argparse
import os
import subprocess
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdn import classify, globalping, globalping_need, origin_ip, save_json  # noqa: E402


def dig(*args):
    out = subprocess.run(["dig", "+short", "+time=3", "+tries=1", *args], capture_output=True, text=True).stdout.split()
    return [x for x in out if x.count(".") == 3 and x.replace(".", "").isdigit()]


def local(a, origin):
    rows = []
    targets = {"sys": [], "1.1.1.1": ["@1.1.1.1"], "8.8.8.8": ["@8.8.8.8"]}
    if a.ns:
        targets["ns"] = ["@" + a.ns]
    for _ in range(a.rounds):
        r = {"t": time.strftime("%H:%M:%S")}
        for k, pre in targets.items():
            r[k] = classify(dig(*pre, a.domain, "A"), origin)
        if a.ns:
            r["ns_id"] = subprocess.run(["dig", "+short", "+time=3", "CH", "TXT", "id.server", "@" + a.ns],
                                        capture_output=True, text=True).stdout.strip()
        rows.append(r)
        time.sleep(a.interval)
    for k in targets:
        print(k, Counter(x[k] for x in rows))
    return rows


def gp(a, origin):
    globalping_need(a.rounds * 3 * a.limit)
    rows = []
    for k in range(a.rounds):
        for res in (None, "1.1.1.1", "8.8.8.8"):
            mo = {"query": {"type": "A"}, "protocol": "UDP", "port": 53}
            if res:
                mo["resolver"] = res
            r = globalping({"type": "dns", "target": a.domain, "locations": [{"country": a.country, "limit": a.limit}],
                            "measurementOptions": mo})
            if r.get("error"):
                print("globalping lỗi", r.get("error"), "(hết quota thì chờ đầu giờ sau)")
            for x in r.get("results", []):
                ans = [v.get("value") for v in (x["result"].get("answers") or []) if v.get("type") == "A"]
                rows.append({"k": k, "t": time.strftime("%H:%M:%S"), "res": res or "probe", "asn": x["probe"].get("asn"),
                             "city": x["probe"].get("city"), "cls": classify(ans, origin)})
        time.sleep(a.interval)
    print(len(rows), Counter(r["cls"] for r in rows), Counter((r["res"], r["cls"]) for r in rows))
    print("lượt không nhận origin:", [(r["t"], r["res"], r["asn"], r["city"]) for r in rows if r["cls"] != "ORIGIN"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["local", "globalping"])
    ap.add_argument("--domain", required=True)
    ap.add_argument("--origin-file", required=True)
    ap.add_argument("--ns", help="một NS của zone, để hỏi thẳng NS (chế độ local)")
    ap.add_argument("--country", default="VN")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--interval", type=float, default=None, help="giây giữa hai vòng; mặc định local 10, globalping 40")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.interval is None:
        a.interval = 10 if a.mode == "local" else 40
    origin = origin_ip(a.origin_file)
    rows = local(a, origin) if a.mode == "local" else gp(a, origin)
    save_json(a.out, rows)


if __name__ == "__main__":
    main()
