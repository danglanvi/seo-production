"""Test offline scripts/so_duyet.py và plan.py --so, plan.py với key#n.
Chạy: python3 -B tests/test_so_duyet_plan.py
Ca hỏng thật:
- 19/10 09:09: lượt đêm ghi đè 37 thẻ title/meta Vincent đã duyệt ngày 17/10 (ca ghi_de_khong_qua_duyet).
- 24/10: thẻ cũ v2-qp-titles suýt ghi đè title và H1 của thẻ m24 duyệt sau (ca the_cu_khong_de_the_moi).
- 18/10: key trùng trong thẻ đổi thành key#n, plan.py không tìm được target mặc định và đẩy sang ghi tay.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def py(script, args):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / script)] + args, capture_output=True, text=True, timeout=60)


def w(d, rel, obj):
    p = Path(d, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def title_card(i, post, before, a):
    return {"id": i, "post_id": post, "url": "https://example.vn/p%s/" % post,
            "fields": [{"key": "seo_title", "name": "t", "before": before, "raw": before, "A": a, "B": before}]}


def rv(i, status, t, value=None, option="A"):
    d = {"item_id": i, "status": status, "option": option, "updatedAt": t, "values": {}}
    if value:
        d["values"] = {"seo_title": value}
    return d


class Ledger(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)
        w(self.d, "report/meta.json", {"items": [
            title_card("duyet-17", 7, "Cũ 7", "Title do Vincent duyệt 17/10"),
            title_card("duyet-19", 7, "Cũ 7", "Title duyệt sau 19/10"),
            title_card("khac", 8, "Cũ 8", "Title post 8"),
        ]})
        w(self.d, "reviews/duyet-17.json", rv("duyet-17", "edited", "2026-10-17T07:00:00.000Z", "Title Vincent tự gõ 17/10"))
        w(self.d, "reviews/duyet-19.json", rv("duyet-19", "approved", "2026-10-19T08:00:00.000Z"))
        w(self.d, "reviews/khac.json", rv("khac", "approved", "2026-10-17T07:00:00.000Z"))
        r = py("so_duyet.py", ["build", "--report", str(self.d / "report"), "--reviews", str(self.d / "reviews"), "--out", str(self.d / "so.json")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.so = json.loads((self.d / "so.json").read_text(encoding="utf-8"))

    def tearDown(self):
        self.t.cleanup()

    def check(self, ops):
        w(self.d, "plan.json", {"ops": ops})
        r = py("so_duyet.py", ["check", "--so", str(self.d / "so.json"), "--plan", str(self.d / "plan.json"), "--out", str(self.d / ("kq%d.json" % len(list(self.d.glob("kq*.json")))))])
        return r, json.loads(sorted(self.d.glob("kq*.json"))[-1].read_text(encoding="utf-8"))

    def test_so_co_gia_tri_cuoi_cua_the_da_sua(self):
        e = {x["item"]: x for x in self.so["entries"]["7|meta:rank_math_title"]}
        self.assertEqual(e["duyet-17"]["value"], "Title Vincent tự gõ 17/10")  # values thắng phương án
        self.assertEqual(e["duyet-19"]["value"], "Title duyệt sau 19/10")
        self.assertEqual(self.so["items"], 3)

    def test_ghi_de_khong_qua_duyet(self):
        """Op của lượt đêm (thẻ không có trong sổ) ghi đè title đã duyệt: bị chặn."""
        r, kq = self.check([{"item": "dem-19-title", "post": 7, "target": "meta:rank_math_title", "before": "Cũ 7", "value": "Title lượt đêm"}])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual(len(kq["blocked"]), 1)
        self.assertIn("không có trong sổ", kq["blocked"][0]["why"])

    def test_the_cu_khong_de_the_moi(self):
        r, kq = self.check([{"item": "duyet-17", "post": 7, "target": "meta:rank_math_title", "before": "Cũ 7", "value": "Title Vincent tự gõ 17/10"}])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual(kq["blocked"][0]["against"][0]["item"], "duyet-19")

    def test_the_moi_de_the_cu_thi_qua_nhung_duoc_liet_ke(self):
        r, kq = self.check([{"item": "duyet-19", "post": 7, "target": "meta:rank_math_title", "before": "Cũ 7", "value": "Title duyệt sau 19/10"}])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(kq["blocked"], [])
        self.assertEqual(kq["ghi_de_cu"][0]["against"][0]["item"], "duyet-17")

    def test_op_cung_gia_tri_va_target_khac_va_text_khong_bi_chan(self):
        r, kq = self.check([
            {"item": "bat-ky", "post": 7, "target": "meta:rank_math_title", "value": "Title duyệt sau 19/10"},  # cùng giá trị đã duyệt
            {"item": "bat-ky", "post": 7, "target": "post_title", "value": "H1 khác"},  # target khác
            {"item": "bat-ky", "post": 7, "target": "text", "field": "post_content", "old": "a", "new": "b"},
            {"item": "fix-1", "post": 8, "target": "fix", "field": "meta:rank_math_title", "old": "Cũ 8", "new": "Title post 8"},
        ])
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_thieu_gio_thi_chan(self):
        w(self.d, "reviews/duyet-19.json", dict(rv("duyet-19", "approved", ""), updatedAt=""))
        r = py("so_duyet.py", ["build", "--report", str(self.d / "report"), "--reviews", str(self.d / "reviews"), "--out", str(self.d / "so2.json")])
        self.so = json.loads((self.d / "so2.json").read_text(encoding="utf-8"))
        (self.d / "so.json").write_text(json.dumps(self.so), encoding="utf-8")
        r, kq = self.check([{"item": "duyet-19", "post": 7, "target": "meta:rank_math_title", "value": "Title duyệt sau 19/10"}])
        self.assertEqual(r.returncode, 1)

    def test_build_khong_ghi_de_va_gop_so_cu(self):
        out = ["build", "--report", str(self.d / "report"), "--reviews", str(self.d / "reviews"), "--out", str(self.d / "so.json")]
        r = py("so_duyet.py", out)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--force", r.stderr)
        # Sổ mới chỉ có 1 thẻ, gộp sổ cũ thì giữ các thẻ kia.
        w(self.d, "r2/report/meta.json", {"items": [title_card("duyet-19", 7, "Cũ 7", "Title duyệt sau 19/10")]})
        w(self.d, "r2/reviews/duyet-19.json", rv("duyet-19", "approved", "2026-10-19T08:00:00.000Z"))
        r = py("so_duyet.py", ["build", "--report", str(self.d / "r2/report"), "--reviews", str(self.d / "r2/reviews"), "--out", str(self.d / "so3.json"), "--cu", str(self.d / "so.json")])
        self.assertEqual(r.returncode, 0, r.stderr)
        so3 = json.loads((self.d / "so3.json").read_text(encoding="utf-8"))
        self.assertEqual({e["item"] for e in so3["entries"]["7|meta:rank_math_title"]}, {"duyet-17", "duyet-19"})
        self.assertEqual(py("so_duyet.py", ["--help"]).returncode, 0)
        self.assertEqual(py("so_duyet.py", ["check", "--so", "/khong/co", "--plan", "/khong/co"]).returncode, 2)

    def test_the_moi_doi_chu_da_duyet(self):
        """18/10: thẻ A1/A2/A4 viết lại chữ Vincent đã duyệt. Thẻ mới có before bằng chữ đã duyệt mà đề xuất khác: lỗi."""
        w(self.d, "r9/report/meta.json", {"items": [{"id": "khoi-1", "post_id": 9, "url": "https://example.vn/p9/",
                                                      "fields": [{"key": "text", "name": "Đoạn", "before": "Đoạn cũ 9", "proposed": "Đoạn Vincent duyệt"}]}]})
        w(self.d, "r9/reviews/khoi-1.json", {"item_id": "khoi-1", "status": "approved", "updatedAt": "2026-10-18T07:00:00.000Z", "values": {}})
        r = py("so_duyet.py", ["build", "--report", str(self.d / "r9/report"), "--reviews", str(self.d / "r9/reviews"),
                               "--out", str(self.d / "so9.json"), "--cu", str(self.d / "so.json")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("9|~text", json.loads((self.d / "so9.json").read_text(encoding="utf-8"))["entries"])
        w(self.d, "moi/report/summary.json", {"sections": []})
        w(self.d, "moi/report/a1.json", {"items": [
            title_card("a1-title", 7, "Title duyệt sau 19/10", "Title viết lại"),  # đổi title đã duyệt
            {"id": "a1-khoi", "post_id": 9, "url": "https://example.vn/p9/",
             "fields": [{"key": "text", "name": "Đoạn", "before": "Đoạn  Vincent duyệt", "A": "Đoạn viết lại", "B": "Đoạn  Vincent duyệt"}]},
            title_card("a1-ok", 8, "Cũ 8 khác", "Title mới post 8"),  # before không phải chữ đã duyệt
            title_card("duyet-19", 7, "Cũ 7", "Title duyệt sau 19/10"),  # thẻ đã có trong sổ: bỏ qua
        ]})
        r = py("so_duyet.py", ["the", "--so", str(self.d / "so9.json"), "--report", str(self.d / "moi/report"), "--json"])
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        kq = json.loads(r.stdout)
        self.assertEqual(sorted(x["item"] for x in kq["loi"]), ["a1-khoi", "a1-title"])
        self.assertEqual(kq["loi"][0]["duyet_boi"], ["duyet-19"])
        # Có lý do (vượt pixel) thì chỉ liệt kê, không lỗi.
        w(self.d, "moi/report/a1.json", {"items": [dict(title_card("a1-title", 7, "Title duyệt sau 19/10", "Title ngắn hơn"),
                                                        fields=[{"key": "seo_title", "name": "t", "before": "Title duyệt sau 19/10", "A": "Title ngắn hơn",
                                                                 "doi_chu_duyet": "vượt 688 px"}])]})
        r = py("so_duyet.py", ["the", "--so", str(self.d / "so9.json"), "--report", str(self.d / "moi/report"), "--json"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["cho_phep"][0]["ly_do"], "vượt 688 px")
        self.assertEqual(py("so_duyet.py", ["the", "--so", "/khong/co", "--report", "/khong/co"]).returncode, 2)


class PlanSo(unittest.TestCase):
    def test_plan_chan_op_de_gia_tri_duyet_moi_hon(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            # Sổ dựng từ toàn bộ hai thẻ. plan.py chỉ chạy trên thẻ cũ (một lô riêng).
            w(d, "full/report/meta.json", {"items": [title_card("cu", 7, "Cũ 7", "Title cũ duyệt"), title_card("moi", 7, "Cũ 7", "Title mới duyệt")]})
            w(d, "full/reviews/cu.json", rv("cu", "approved", "2026-10-17T07:00:00.000Z"))
            w(d, "full/reviews/moi.json", rv("moi", "approved", "2026-10-19T08:00:00.000Z"))
            self.assertEqual(py("so_duyet.py", ["build", "--report", str(d / "full/report"), "--reviews", str(d / "full/reviews"), "--out", str(d / "so.json")]).returncode, 0)
            w(d, "lo/report/meta.json", {"items": [title_card("cu", 7, "Cũ 7", "Title cũ duyệt"), title_card("khac", 9, "Cũ 9", "Title post 9")]})
            w(d, "lo/reviews/cu.json", rv("cu", "approved", "2026-10-17T07:00:00.000Z"))
            w(d, "lo/reviews/khac.json", rv("khac", "approved", "2026-10-17T07:00:00.000Z"))
            args = ["--reviews", str(d / "lo/reviews"), "--report", str(d / "lo/report"), "--out", str(d / "plan.json")]
            r = py("plan.py", args)  # không có sổ: cả hai op vào plan (lỗi cũ)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(len(json.loads((d / "plan.json").read_text(encoding="utf-8"))["ops"]), 2)
            (d / "plan.json").unlink()
            r = py("plan.py", args + ["--so", str(d / "so.json")])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            plan = json.loads((d / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual([o["item"] for o in plan["ops"]], ["khac"])
            self.assertEqual(plan["holds"][0]["item"], "cu")
            self.assertIn("moi", plan["holds"][0]["why"])
            self.assertIn("chặn theo sổ: 1", r.stdout)

    def test_key_n_tim_duoc_target_mac_dinh(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            it = {"id": "dup", "post_id": 5, "url": "https://example.vn/p5/", "fields": [
                {"key": "meta", "name": "m", "before": "Meta cũ một", "raw": "Meta cũ một", "proposed": "Meta mới một"},
                {"key": "meta#2", "name": "m2", "before": "Meta cũ hai", "raw": "Meta cũ hai", "proposed": "Meta mới hai"}]}
            w(d, "report/meta.json", {"items": [it]})
            w(d, "reviews/dup.json", {"item_id": "dup", "status": "approved", "values": {}})
            r = py("plan.py", ["--reviews", str(d / "reviews"), "--report", str(d / "report"), "--out", str(d / "plan.json")])
            self.assertEqual(r.returncode, 1)  # hai giá trị khác nhau cho cùng post|target: plan dừng, không đoán
            self.assertIn("XUNG ĐỘT", r.stdout)  # bản cũ: meta#2 không có target mặc định, trường rơi vào ghi tay và không báo xung đột

if __name__ == "__main__":
    unittest.main(verbosity=1)
