#!/usr/bin/env python3
"""Test offline cho bl_research.py: dữ liệu Ahrefs mẫu, không gọi mạng.
Chạy: python3 -I tests/test_bl_research.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE.parent / "scripts" / "bl_research.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(S.parent))
import bl_research as br  # noqa: E402


def run(*args):
    p = subprocess.run([sys.executable, "-B", "-I", str(S), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p


def rd(dom, **kw):
    x = {"domain": dom, "domain_rating": 50, "is_spam": False, "traffic_domain": 100, "positions_source_domain": 50, "dofollow_links": 1}
    x.update(kw)
    return x


def save(p, obj, mcp=False):
    txt = json.dumps(obj, ensure_ascii=False)
    Path(p).write_text(json.dumps([{"type": "text", "text": txt + "Display these results"}]) if mcp else txt, encoding="utf-8")


def test_classify():
    L, K = ["mau"], ["dịch vụ seo", "đào tạo seo"]
    cases = {"": "rong", "Mẫu": "chu_de", "MAU": "brand", "Mau Agency": "brand", "mau dịch vụ seo": "brand_kw",
             "dịch vụ SEO": "exact", "dịch vụ SEO tổng thể": "partial", "https://mau.vn/": "naked", "mau.vn": "naked",
             "tại đây": "generic", "Internal Link": "chu_de", "TELEGRAM @SEO_LINKS - SEO BACKLINKS": "spam", "x" * 95: "spam"}
    for a, want in cases.items():
        assert br.classify(a, L, K) == want, (a, br.classify(a, L, K), want)


def main():
    test_classify()
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        save(d / "mine.json", {"target": "mau.vn", "refdomains": [rd("da-co.vn")]})
        save(d / "a.json", {"target": "a.vn", "refdomains": [rd("bao.vn", domain_rating=80), rd("da-co.vn"), rd("rac.xyz", is_spam=True, traffic_domain=0, positions_source_domain=0),
                                                         rd("mot.vn"), rd("nghi.info", is_spam=True), rd("behance.net", dofollow_links=0)]}, mcp=True)
        save(d / "b.json", {"target": "b.vn", "refdomains": [rd("bao.vn", domain_rating=79), rd("da-co.vn"), rd("rac.xyz", is_spam=True, traffic_domain=0, positions_source_domain=0),
                                                         rd("nghi.info"), rd("behance.net", dofollow_links=0)]})
        run("gap", "--mine", d / "mine.json", "--comp", d / "a.json", d / "b.json", "--out", d / "gap.md")
        g = json.loads((d / "gap.json").read_text(encoding="utf-8"))
        R = {r["domain"]: r for r in g["rows"]}
        assert set(R) == {"bao.vn", "rac.xyz", "nghi.info", "behance.net"}, "bỏ tên miền đã trỏ mình và tên miền chỉ trỏ 1 đối thủ"
        assert R["bao.vn"]["verdict"] == "KEEP" and R["bao.vn"]["dr"] == 80
        assert R["rac.xyz"]["verdict"] == "REJECT" and R["rac.xyz"]["machine"] == ["M1", "M2"]
        assert R["nghi.info"]["verdict"] == "REVIEW", "một tín hiệu là REVIEW"
        assert R["behance.net"]["platform"] and not R["behance.net"]["dofollow"]
        assert g["rows"][0]["verdict"] == "KEEP" and g["rows"][-1]["verdict"] == "REJECT"

        rows = lambda pairs: [{"anchor": a, "refdomains": n} for a, n in pairs]  # noqa: E731
        save(d / "an_mau.json", {"target": "mau.vn", "anchors": rows([("mau.vn", 50), ("Internal link", 50), ("TELEGRAM @X - SEO BACKLINKS", 100)])})
        save(d / "an_a.json", {"target": "a.vn", "anchors": rows([("A", 50), ("dịch vụ seo", 50)])})
        save(d / "an_b.json", {"target": "b.vn", "anchors": rows([("b.vn", 100)])})
        run("anchors", "--file", d / "an_mau.json", d / "an_a.json", d / "an_b.json", "--mine", "mau.vn", "--keywords", "dịch vụ seo", "--out", d / "an.md")
        an = json.loads((d / "an.json").read_text(encoding="utf-8"))
        m = an["share"]["mau.vn"]
        assert m["spam_share"] == 0.5 and m["naked"] == 0.5 and m["chu_de"] == 0.5, "tỷ lệ tính trên phần không spam"
        assert an["share"]["a.vn"]["brand"] == 0.5 and an["share"]["a.vn"]["exact"] == 0.5
        assert an["consensus"]["naked"] == 0.5 and an["consensus"]["brand"] == 0.25
        assert "Lệch của mình" in (d / "an.md").read_text(encoding="utf-8")

        (d / "h.json").write_text(json.dumps({"history": {"mau.vn": [{"date": f"2026-0{i}-01", "refdomains": v} for i, v in enumerate([100, 130, 90, 160], 1)]}}))
        run("velocity", "--file", d / "h.json", "--out", d / "v.md")
        v = json.loads((d / "v.json").read_text(encoding="utf-8"))["mau.vn"]
        assert v["net_per_month"] == 20.0 and v["max_up"] == ["2026-04", 70] and v["max_down"] == ["2026-03", -40]
    print("test_bl_research: OK")


if __name__ == "__main__":
    main()
