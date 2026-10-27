# Ước average response time trong GSC Crawl Stats theo tỉ lệ trúng cache CDN.
# RT ≈ 40 + 20h + (M + S)(1 − h). h: tỉ lệ trúng cache toàn host (theo cơ cấu request Googlebot).
# M: thời gian trạm CDN gọi về origin (ms). S: thời gian origin xử lý (ms). 40 và 20: phần nền và phần trạm khi trúng.
# Kết quả là số (ước). Chỉ ghi (đo) khi GSC Crawl Stats đã có số của các ngày sau khi đổi.
#   python3 rt_model.py --mix work/mix.json [--M 200 --S 80]
# mix.json: {"nhom": {"share": 0.13, "hit": 0.6}, ...}. share lấy từ log Googlebot, hit lấy từ log CDN (không từ vài request thử).
import argparse
import json


def rt(h, M=200, S=80):
    return 40 + 20 * h + (M + S) * (1 - h)


def host_hit(mix):
    total = sum(v["share"] for v in mix.values())
    return sum(v["share"] * v["hit"] for v in mix.values()) / total


def h_for(target, M=200, S=80):
    # Tỉ lệ trúng tối thiểu để RT < target.
    return (40 + M + S - target) / (M + S - 20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", required=True)
    ap.add_argument("--M", type=float, default=200)
    ap.add_argument("--S", type=float, default=80)
    a = ap.parse_args()
    mix = json.load(open(a.mix))
    total = sum(v["share"] for v in mix.values())
    if abs(total - 1) > 0.02:
        print("cảnh báo: tổng share = %.3f, không phải 1" % total)
    h = host_hit(mix)
    print("h = %.3f  RT (ước) = %.0f ms" % (h, rt(h, a.M, a.S)))
    for t in (250, 200):
        print("RT < %d ms cần h > %.3f" % (t, h_for(t, a.M, a.S)))
    worst = sorted(mix.items(), key=lambda kv: -kv[1]["share"] * (1 - kv[1]["hit"]))[:3]
    print("nhóm kéo RT nhiều nhất:", [(k, v["share"], v["hit"]) for k, v in worst])


if __name__ == "__main__":
    main()
