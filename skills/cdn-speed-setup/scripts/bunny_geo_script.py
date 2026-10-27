# Dựng script DNS chia vùng từ templates/geo-dns-script.js, gửi lên Bunny Compute và publish (nhánh B, O7b).
# Chạy thử theo mặc định: in bản đã che IP và so với code đang chạy. Thêm --apply để gửi và publish.
# Trước --apply: backup code đang chạy bằng --backup <thư mục>. Script không ghi IP vào file.
#   python3 bunny_geo_script.py --script-id 12345 --pull-zone <tên pull zone> --origin-file ~/.cm/x.origin --backup backup/v3-truoc [--apply --note "lý do"]
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdn import bn, mask, origin_ip  # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "geo-dns-script.js")


def render(tpl, ip, pz):
    out = tpl.replace("{{ORIGIN_IP}}", ip).replace("{{PULL_ZONE_NAME}}", pz)
    if "{{" in out:
        sys.exit("Template còn placeholder chưa thay")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-id", required=True, type=int)
    ap.add_argument("--pull-zone", required=True, help="tên pull zone Bunny (không phải id)")
    ap.add_argument("--origin-file", required=True)
    ap.add_argument("--backup")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--note", default="cdn-speed-setup")
    a = ap.parse_args()
    code = render(open(TEMPLATE, encoding="utf-8").read(), origin_ip(a.origin_file), a.pull_zone)
    c, live = bn("GET", "/compute/script/%d/code" % a.script_id)
    if c != 200:
        sys.exit("Không đọc được code script %d (HTTP %s)" % (a.script_id, c))
    live_code = (live or {}).get("Code", "")
    if a.backup:
        os.makedirs(a.backup, exist_ok=True)
        open(os.path.join(a.backup, "dns-script.js"), "w", encoding="utf-8").write(mask(live_code))
        print("backup", os.path.join(a.backup, "dns-script.js"))
    print("giống code đang chạy:", live_code.strip() == code.strip())
    if not a.apply:
        print("CHẠY THỬ. Bản sẽ gửi (che IP):\n" + mask(code))
        return
    c1, _ = bn("POST", "/compute/script/%d/code" % a.script_id, {"Code": code})
    c2, _ = bn("POST", "/compute/script/%d/publish" % a.script_id, {"Note": a.note})
    print("code HTTP", c1, "publish HTTP", c2)
    sys.exit(0 if c1 < 300 and c2 < 300 else 1)


if __name__ == "__main__":
    main()
