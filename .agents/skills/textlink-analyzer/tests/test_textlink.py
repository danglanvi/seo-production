#!/usr/bin/env python3
"""Test offline cho textlink.py: URL báo mẫu, terms mẫu, số Ahrefs mẫu. Không gọi mạng.
Chạy: python3 -I tests/test_textlink.py
"""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = Path(__file__).resolve().parent.parent / "scripts" / "textlink.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(S.parent))
import textlink as tl  # noqa: E402


def run(*args):
    p = subprocess.run([sys.executable, "-B", "-I", str(S), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


TERMS = {"targets": [{"url": "https://mau.vn/den-pha-led/", "quota": 2, "A": ["đèn pha led"], "B": ["chiếu sáng"]},
                     {"url": "https://mau.vn/den-panel/", "quota": 1, "A": ["đèn panel", "đèn led panel"], "B": ["chiếu sáng"]},
                     {"url": "https://mau.vn/", "quota": 2, "home": True}],
         "C": ["điện", "xây dựng"], "neg": ["tai nạn", "đối thủ x"]}

URLS = ["https://bao-a.vn/den-pha-led-tiet-kiem-dien-12345.html",
        "https://www.bao-a.vn/den-pha-led-tiet-kiem-dien-12345.html?utm=1",  # trùng sau chuẩn hoá
        "https://bao-b.vn/kinh-nghiem-chon-den-led-panel-chieu-sang-van-phong.html",
        "https://bao-a.vn/giai-phap-chieu-sang-nha-xuong.html",
        "https://bao-b.vn/tai-nan-dien-giat-o-cong-truong.html",  # negative
        "https://bao-c.vn/doi-thu-x-ra-mat-den-pha-led.html",  # negative: đối thủ
        "https://bao-c.vn/gia-vang-hom-nay.html",  # không khớp
        "https://bao-c.vn/nganh-xay-dung-phuc-hoi.html",
        "https://bao-a.vn/thi-truong-dien-mat-troi.html"]


def main():
    assert tl.plain("Đèn Pha LED") == "den pha led"
    assert tl.slug_forms("đèn pha led") == {"den-pha-led"}
    assert tl.tokens("https://www.bao.vn/Den-Pha-Led-2024-998877.html") == ("bao.vn", "-den-pha-led-")
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "terms.json").write_text(json.dumps(TERMS, ensure_ascii=False), encoding="utf-8")
        (d / "urls.txt").write_text("\n".join(URLS), encoding="utf-8")
        p = run("filter", "--urls", d / "urls.txt", "--terms", d / "terms.json", "--out", d / "c.csv")
        assert "Cảnh báo" in p.stderr and "chiếu sáng" in p.stderr, "term ngắn phải bị cảnh báo"
        info = json.loads(p.stdout)
        assert info["bỏ"] == {"trùng": 1, "negative": 2, "không khớp": 1}, info
        C = {r["url"].split("/")[-1]: r for r in rows(d / "c.csv")}
        assert C["den-pha-led-tiet-kiem-dien-12345.html"]["tier"] == "A" and C["den-pha-led-tiet-kiem-dien-12345.html"]["targets"] == "0"
        panel = C["kinh-nghiem-chon-den-led-panel-chieu-sang-van-phong.html"]
        assert panel["tier"] == "A" and panel["targets"] == "1", "đèn led panel thuộc target 1"
        assert C["giai-phap-chieu-sang-nha-xuong.html"]["tier"] == "B" and C["giai-phap-chieu-sang-nha-xuong.html"]["targets"] in ("0|1", "1|0")
        assert C["nganh-xay-dung-phuc-hoi.html"]["tier"] == "C"

        (d / "ah.json").write_text(json.dumps([{"type": "text", "text": json.dumps({"pages": [
            {"url": "https://bao-a.vn/thi-truong-dien-mat-troi.html", "sum_traffic": 500, "referring_domains": 3}]})}]))
        info = json.loads(run("enrich", "--candidates", d / "c.csv", "--ahrefs", d / "ah.json", "--out", d / "e.csv").stdout)
        assert info["có số Ahrefs"] == 1
        E = {r["url"]: r for r in rows(d / "e.csv")}
        assert E["https://bao-a.vn/thi-truong-dien-mat-troi.html"]["refdomains"] == "3", "top-pages dùng trường referring_domains"
        info = json.loads(run("allocate", "--candidates", d / "e.csv", "--terms", d / "terms.json", "--cap-domain", "0.4", "--out", d / "p.csv").stdout)
        P = rows(d / "p.csv")
        dest = {r["URL đi link"].split("/")[-1]: r["URL đích"] for r in P}
        assert dest["kinh-nghiem-chon-den-led-panel-chieu-sang-van-phong.html"] == "https://mau.vn/den-panel/"
        assert info["cap mỗi domain"] == 2 and max(info["domain"].values()) <= 2, "cap theo domain"
        assert "https://bao-a.vn/thi-truong-dien-mat-troi.html" not in [r["URL đi link"] for r in P] or dest.get("thi-truong-dien-mat-troi.html") == "https://mau.vn/"
        assert len({r["URL đi link"] for r in P}) == len(P), "mỗi URL báo gánh 1 trang đích"
    print("test_textlink: OK")


if __name__ == "__main__":
    main()
