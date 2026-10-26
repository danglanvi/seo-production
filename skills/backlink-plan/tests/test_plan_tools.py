#!/usr/bin/env python3
"""Test offline cho plan_tools.py: dữ liệu Ahrefs mẫu và CSV plan mẫu, không gọi mạng.
Chạy: python3 -I tests/test_plan_tools.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = Path(__file__).resolve().parent.parent / "scripts" / "plan_tools.py"


def run(*args, ok=True):
    p = subprocess.run([sys.executable, "-B", "-I", str(S), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (p.returncode, p.stderr)
    return p


def rd(dom, month, live=True, spam=False, traffic=10):
    return {"domain": dom, "first_seen": f"{month}-05T00:00:00Z", "last_seen": None if live else "2026-03-01T00:00:00Z",
            "is_spam": spam, "traffic_domain": traffic}


CSV_HEAD = "Domain/nguồn,Dạng,Giá,Target URL,Anchor type,Anchor,Tháng,Trạng thái,DR\n"


def plan(rows):
    return CSV_HEAD + "".join(f"s{i}.vn,guest,1,{t},{k},{a},{m},dự kiến,{dr}\n" for i, (t, k, a, m, dr) in enumerate(rows))


def main():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        ms = ["2026-01", "2026-02", "2026-03", "2026-04"]
        a = [rd(f"a{i}.vn", m) for i, m in enumerate(ms * 2)]  # 2 RD/tháng
        a += [rd(f"ab{i}.vn", "2026-03") for i in range(30)]  # tháng bùng
        a += [rd("rac.vn", "2026-01", spam=True), rd("khong.vn", "2026-01", traffic=0), rd("cu.vn", "2025-12")]
        b = [rd(f"b{i}.vn", m, live=(i % 2 == 0)) for i, m in enumerate(ms * 4)]  # 4 RD/tháng, 2 còn sống
        (d / "a.json").write_text(json.dumps({"target": "a.vn", "refdomains": a}))
        (d / "b.json").write_text(json.dumps([{"type": "text", "text": json.dumps({"target": "b.vn", "refdomains": b})}]))
        (d / "m.json").write_text(json.dumps({"target": "mau.vn", "refdomains": [rd("x.vn", "2026-02")]}))
        run("velocity", "--file", d / "m.json", d / "a.json", d / "b.json", "--mine", "mau.vn", "--since", "2026-01", "--until", "2026-04", "--out", d / "v.md")
        v = json.loads((d / "v.json").read_text())
        A = v["domains"]["a.vn"]
        assert A["new"] == [2, 2, 32, 2], "bỏ spam, traffic 0, ngoài kỳ"
        assert A["median"] == 2 and A["burst"] == ["2026-03"]
        assert v["domains"]["b.vn"]["median_live"] == 2
        assert v["pace"] == 2, "nhịp = trung vị còn sống của đối thủ"
        run("velocity", "--file", d / "a.json", d / "b.json", "--mine", "mau.vn", "--since", "2026-01", "--until", "2026-04", "--new-site", "--out", d / "v2.md")
        assert json.loads((d / "v2.json").read_text())["pace"] == 1

        kws = [{"keyword": "seo là gì", "volume": 1000, "best_position": 8, "best_position_url": "https://www.mau.vn/seo-la-gi/", "sum_traffic": 5},
               {"keyword": "seo", "volume": 500, "best_position": 12, "best_position_url": "https://mau.vn/seo-la-gi?x=1", "sum_traffic": 1},
               {"keyword": "lạ", "volume": 100, "best_position": 5, "best_position_url": "https://mau.vn/SEO/SEO%20Onpage", "sum_traffic": 0}]
        (d / "k.json").write_text(json.dumps({"keywords": kws}))
        run("quickwins", "--file", d / "k.json", "--out", d / "q.md")
        q = json.loads((d / "q.json").read_text())["rows"]
        assert q[0]["url"] == "mau.vn/seo-la-gi" and q[0]["n"] == 2 and q[0]["volume"] == 1500 and not q[0]["odd"]
        assert q[1]["odd"]
        md = (d / "q.md").read_text(encoding="utf-8")
        assert "| mau.vn/SEO/SEO%20Onpage |" not in md and "đã loại khỏi bảng (1)" in md, "URL breadcrumb không vào bảng target"

        good = [("/a", "brand", f"Mẫu {i}", "2026-01", 30) for i in range(5)] + [("/a", "naked", "mau.vn", "2026-01", 30) for _ in range(2)] \
            + [("/a", "partial", "dịch vụ seo uy tín", "2026-01", 50), ("/a", "brand_kw", "mẫu dịch vụ seo", "2026-02", 45),
               ("/a", "Khớp một phần", "seo tổng thể", "2026-02", 55)]
        (d / "ok.csv").write_text(plan(good), encoding="utf-8")
        run("check", "--csv", d / "ok.csv", "--stage", "1", "--out", d / "ok.md")
        assert json.loads((d / "ok.json").read_text())["safe_pct"] == 70.0

        bad = good + [("/a", "exact", "dịch vụ seo", "2026-03", 70), ("/a", "exact", "dịch vụ seo", "2026-03", 50),
                      ("/a", "partial", "seo tổng thể", "2026-04", 20), ("/a", "lạ", "x", "2026-04", 50)]
        (d / "bad.csv").write_text(plan(bad), encoding="utf-8")
        run("check", "--csv", d / "bad.csv", "--stage", "1", "--out", d / "bad.md", ok=False)
        f = " | ".join(json.loads((d / "bad.json").read_text())["fails"])
        for want in ("Anchor type lạ", "ngoài khung giai đoạn 1", "vượt trần 10%", "lặp 2 lần trong tháng 2026-03", "DR 20 < 40", "exact ở nguồn DR 50 < 60"):
            assert want in f, (want, f)
    print("test_plan_tools: OK")


if __name__ == "__main__":
    main()
