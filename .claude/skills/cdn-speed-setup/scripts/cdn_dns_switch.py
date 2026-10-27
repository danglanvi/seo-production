# Đổi apex (hoặc tên bất kỳ) giữa bản ghi A về origin và CNAME về đích CDN, bằng batch API của Cloudflare (nguyên khối, không có khoảng NODATA).
# Chạy thử theo mặc định; thêm --apply để ghi. Backup ghi qua mask(), không chứa IP.
#   python3 cdn_dns_switch.py backup   --zone example.com --name example.com --origin-file ~/.cm/example.origin --out backup/v1
#   python3 cdn_dns_switch.py switch   --zone example.com --name example.com --target geo.cdn-zone.example.net [--apply]
#   python3 cdn_dns_switch.py unswitch --zone example.com --name example.com --origin-file ~/.cm/example.origin [--apply]
#   python3 cdn_dns_switch.py pin-a    --zone example.com --name www.example.com --origin-file ~/.cm/example.origin [--apply]
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdn import cf, cf_records, cf_zone_id, mask, origin_ip, save_json  # noqa: E402


def body_to_cname(rec, name, target, ttl=60):
    return {"deletes": [{"id": rec["id"]}], "posts": [{"type": "CNAME", "name": name, "content": target, "proxied": False, "ttl": ttl}]}


def body_to_a(rec, name, ip, ttl=1):
    return {"deletes": [{"id": rec["id"]}], "posts": [{"type": "A", "name": name, "content": ip, "proxied": False, "ttl": ttl}]}


def plan(cmd, recs, name, target=None, ip=None):
    # Trả (body hoặc None, lý do). Hàm thuần để test offline.
    live = [r for r in recs if r["type"] in ("A", "CNAME")]
    if len(live) != 1:
        return None, "cần đúng 1 bản ghi A hoặc CNAME cho %s, đang có %d" % (name, len(live))
    r = live[0]
    if r.get("proxied"):
        return None, "bản ghi đang proxied; skill này chỉ đổi bản ghi DNS-only"
    if cmd == "switch":
        if r["type"] == "CNAME" and r["content"] == target:
            return None, "đã trỏ tới đích, không làm gì"
        return body_to_cname(r, name, target), "%s → CNAME %s" % (r["type"], target)
    if cmd in ("unswitch", "pin-a"):
        if r["type"] == "A" and r["content"] == ip:
            return None, "đã là A về origin, không làm gì"
        return body_to_a(r, name, ip), "%s → A origin" % r["type"]
    return None, "lệnh lạ"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["backup", "switch", "unswitch", "pin-a"])
    ap.add_argument("--zone", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--target")
    ap.add_argument("--origin-file")
    ap.add_argument("--out")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    zid = cf_zone_id(a.zone)
    recs = cf_records(zid, a.name)
    print("live", [(r["type"], mask(r["content"]), r.get("proxied"), r.get("ttl")) for r in recs])
    if a.cmd == "backup":
        if not a.out:
            ap.error("backup cần --out")
        save_json(os.path.join(a.out, "dns-%s.json" % a.name), recs)
        if a.origin_file and not os.path.exists(os.path.expanduser(a.origin_file)):
            ip = [r["content"] for r in recs if r["type"] == "A"]
            if ip:
                p = os.path.expanduser(a.origin_file)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(ip[0])
                os.chmod(p, 0o600)
                print("đã lưu IP origin vào", a.origin_file)
        print("backup xong")
        return
    if a.cmd == "switch" and not a.target:
        ap.error("switch cần --target")
    ip = origin_ip(a.origin_file) if a.cmd in ("unswitch", "pin-a") else None
    body, why = plan(a.cmd, recs, a.name, a.target, ip)
    print("kế hoạch:", why)
    if body is None or not a.apply:
        if body is not None:
            print("CHẠY THỬ, chưa ghi. Thêm --apply để ghi.")
        return
    c, j = cf("POST", "/zones/%s/dns_records/batch" % zid, body)
    print("batch HTTP", c, "" if c < 300 else mask(str(j))[:400])
    sys.exit(0 if c < 300 else 1)


if __name__ == "__main__":
    main()
