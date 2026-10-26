"""Test offline scripts/mark_batch.py và scripts/seed_batches.py (lô ArtifactData gắn 'đã áp' và nạp tài liệu thiếu).
Chạy: python3 -B tests/test_mark_batch.py
Ca hỏng thật:
- 20/10 09:32 (6cae27d5-18): query `__name__ in` trả 0, get từng thẻ 8 lần, KeyError 'version', khoảng 10 tool call thừa.
- 20/10 (e297d7d3-02): batch 31 thẻ phải giữ note cũ của Vincent, update không được đè.
- 20/10 10:18: 513 dấu 'đã áp' qua 11 batch, mỗi batch một hộp duyệt; phải báo trước số hộp.
- 23/10: thẻ lên production khi lane chưa qua kiểm độc lập hoặc kiểm độc lập báo không đạt.
- 21/10 (ops3): list cả collection report chỉ để xem định dạng, nạp lại cả lô khi chỉ thiếu vài tài liệu.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
MARK = SCRIPTS / "mark_batch.py"
SEED = SCRIPTS / "seed_batches.py"
NOW = "2026-10-25T09:30:00Z"
NOTE = "[Claude 09:20] Đã ghi production, verify bản cache và bỏ cache đạt. Rollback: backup/L1."


def w(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", str(script)] + [str(a) for a in args], capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout, p.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)

    def tearDown(self):
        self.t.cleanup()


class Mark(Base):
    def lane(self, name, ids, verdict="### Kết luận\n\n- Kết quả: đạt. Cả việc chạy đúng.\n", note=NOTE):
        w(self.d / name / "mark_applied.json", [{"id": i, "status": "applied", "note": note} for i in ids])
        if verdict is not None:
            w(self.d / name / "kiem-doc-lap.md", "# Kiểm độc lập\n\n" + verdict)
        return self.d / name

    def versions(self, ids, notes=None, version=1, status="approved"):
        docs = [{"doc_id": i, "version": version, "data": {"item_id": i, "status": status, "note": (notes or {}).get(i, "")}} for i in ids]
        w(self.d / "q.json", {"documents": docs})
        return self.d / "q.json"

    def go(self, lanes, q, *extra, so=None):
        so = so or self.d / "so.txt"
        args = []
        for l in lanes:
            args += ["--lane", l]
        return run(MARK, *args, "--versions", q, "--so-id", so, "--out", self.d / "out", "--now", NOW, "--json", *extra)

    def test_chay_thu_khong_ghi_gi(self):
        l = self.lane("a", ["x1", "x2"])
        rc, out, err = self.go([l], self.versions(["x1", "x2"]))
        r = json.loads(out)
        self.assertEqual(rc, 0, out)
        self.assertEqual((r["the_gan"], r["so_hop_duyet"], r["da_ghi"]), (2, 1, False))
        self.assertFalse((self.d / "out").exists())
        self.assertFalse((self.d / "so.txt").exists())

    def test_ghi_dung_dinh_dang_va_giu_note_cu_cua_vincent(self):
        l = self.lane("a", ["x1", "x2"])
        q = self.versions(["x1", "x2"], notes={"x1": "ok theo đề xuất, nhưng link phải nofollow."}, version=3, status="edited")
        rc, out, err = self.go([l], q, "--ghi")
        self.assertEqual(rc, 0, out + err)
        d1 = json.loads((self.d / "out" / "x1.json").read_text(encoding="utf-8"))
        self.assertTrue(d1["note"].startswith("ok theo đề xuất, nhưng link phải nofollow."))
        self.assertIn("[Claude 09:20]", d1["note"])
        self.assertEqual((d1["status"], d1["appliedAt"]), ("applied", "2026-10-25T09:30:00.000Z"))
        d2 = json.loads((self.d / "out" / "x2.json").read_text(encoding="utf-8"))
        self.assertTrue(d2["note"].startswith("[Claude"))
        writes = json.loads((self.d / "out" / "_writes_01.json").read_text(encoding="utf-8"))
        self.assertEqual(writes[0]["op"], "update")
        self.assertEqual((writes[0]["collection"], writes[0]["doc_id"], writes[0]["if_version"]), ("reviews", "x1", 3))
        self.assertTrue(Path(writes[0]["file_path"]).is_absolute())
        self.assertEqual(Path(writes[0]["file_path"]).read_text(encoding="utf-8"), (self.d / "out" / "x1.json").read_text(encoding="utf-8"))
        self.assertEqual((self.d / "out" / "ids.txt").read_text(encoding="utf-8").split(), ["x1", "x2"])
        self.assertEqual((self.d / "so.txt").read_text(encoding="utf-8").split(), ["x1", "x2"])

    def test_120_the_chia_3_lo_50_50_20(self):
        ids = ["t%03d" % i for i in range(120)]
        l = self.lane("a", ids)
        rc, out, err = self.go([l], self.versions(ids), "--ghi")
        r = json.loads(out)
        self.assertEqual((r["so_lo"], r["so_hop_duyet"]), (3, 3))
        sizes = [len(json.loads(p.read_text(encoding="utf-8"))) for p in sorted((self.d / "out").glob("_writes_*.json"))]
        self.assertEqual(sizes, [50, 50, 20])

    def test_chay_lan_hai_khong_gan_lai(self):
        l = self.lane("a", ["x1"])
        q = self.versions(["x1"])
        self.go([l], q, "--ghi")
        rc, out, err = run(MARK, "--lane", l, "--versions", q, "--so-id", self.d / "so.txt", "--out", self.d / "out2", "--now", NOW, "--json", "--ghi")
        r = json.loads(out)
        self.assertEqual((rc, r["the_gan"]), (0, 0))
        self.assertIn("sổ id", r["the_bo"][0]["ly_do"])

    def test_thieu_version_la_loi_khong_get_tung_the(self):
        # ca 20/10: KeyError 'version'. Thẻ không có version trong file query thì báo lỗi rõ.
        l = self.lane("a", ["x1"])
        w(self.d / "q.json", {"documents": [{"doc_id": "x1", "data": {"status": "approved"}}]})
        rc, out, err = self.go([l], self.d / "q.json", "--ghi")
        self.assertEqual(rc, 1)
        self.assertIn("version", json.loads(out)["loi"][0])
        self.assertFalse((self.d / "out").exists())

    def test_the_khong_co_trong_query_bi_bo(self):
        l = self.lane("a", ["x1", "pending-1"])
        rc, out, err = self.go([l], self.versions(["x1"]))
        r = json.loads(out)
        self.assertEqual(rc, 0)
        self.assertEqual(r["the_gan"], 1)
        self.assertEqual(r["the_bo"][0]["id"], "pending-1")

    def test_the_da_applied_tren_trang_bi_bo(self):
        l = self.lane("a", ["x1"])
        rc, out, err = self.go([l], self.versions(["x1"], status="applied"))
        r = json.loads(out)
        self.assertEqual(r["the_gan"], 0)

    def test_lane_khong_dat_bi_bo(self):
        cases = {
            "khong-dat": "Kết luận: KHÔNG ĐẠT. 9 thẻ có trên production, nhưng 2 thẻ còn lỗi.\n",
            "chua-dat": "### Kết luận\n\n- Kết quả: **chưa đạt (pass = false)**. Một tiêu chí chưa đạt.\n",
            "mot-id-lech": "Kiểm 20:15. Kết luận: không đạt, một id: `sa2-chi-phi-nhan-su`. 4 id còn lại đạt.\n",
            "co-dieu-kien": "Kết luận: đạt có điều kiện. Cần Vincent xác nhận.\n",
            "khong-doc-ra": "### Kết luận\n\nLane đo bằng thuộc tính slick-current. Đây là dương tính giả.\n",
            "khong-co-muc": "# Kiểm\n\nMọi việc ổn.\n",
        }
        for name, v in cases.items():
            l = self.lane(name, ["x-" + name], verdict=v)
            rc, out, err = self.go([l], self.versions(["x-" + name]))
            r = json.loads(out)
            self.assertEqual(r["the_gan"], 0, name)
            self.assertEqual(len(r["lanes_bo"]), 1, name)

    def test_lane_dat_nhieu_dang_viet(self):
        for i, v in enumerate(["Kết luận: **Đạt**. 6 thẻ khớp.\n", "### Kết luận: ĐẠT\n", "Kết luận: ĐẠT. Không có ID nào lệch.\n",
                               "## Kết luận\n\nĐẠT. Mọi việc lane báo có thật.\n", "Kết luận: đạt. Lỗi vòng 1 đã hết.\n"]):
            l = self.lane("ok%d" % i, ["y%d" % i], verdict=v)
            rc, out, err = self.go([l], self.versions(["y%d" % i]))
            self.assertEqual(json.loads(out)["the_gan"], 1, v)

    def test_dung_ket_luan_cuoi_khi_kiem_nhieu_luot(self):
        v = "## Kết luận lượt 1\n\nKhông đạt.\n\n## Lượt 2\n\n### Kết luận\n\nĐạt. Đã sửa xong.\n"
        l = self.lane("a", ["x1"], verdict=v)
        rc, out, err = self.go([l], self.versions(["x1"]))
        self.assertEqual(json.loads(out)["the_gan"], 1)

    def test_thieu_kiem_doc_lap_bi_bo(self):
        l = self.lane("a", ["x1"], verdict=None)
        rc, out, err = self.go([l], self.versions(["x1"]))
        r = json.loads(out)
        self.assertEqual(r["the_gan"], 0)
        self.assertIn("kiem-doc-lap", r["lanes_bo"][0]["ly_do"])

    def test_id_trung_giua_hai_lane_la_loi(self):
        a, b = self.lane("a", ["x1"]), self.lane("b", ["x1"])
        rc, out, err = self.go([a, b], self.versions(["x1"]))
        self.assertEqual(rc, 1)
        self.assertIn("trùng", json.loads(out)["loi"][0])

    def test_note_thieu_dau_gio_duoc_them(self):
        l = self.lane("a", ["x1"], note="Đã ghi, verify đạt, rollback ở backup.")
        self.go([l], self.versions(["x1"]), "--ghi")
        d = json.loads((self.d / "out" / "x1.json").read_text(encoding="utf-8"))
        self.assertTrue(d["note"].startswith("[Claude 09:30]"))

    def test_note_rong_la_loi(self):
        l = self.lane("a", ["x1"], note="  ")
        rc, out, err = self.go([l], self.versions(["x1"]))
        self.assertEqual(rc, 1)

    def test_thu_muc_ra_co_file_thoat_2(self):
        l = self.lane("a", ["x1"])
        w(self.d / "out" / "cu.txt", "x")
        rc, out, err = self.go([l], self.versions(["x1"]), "--ghi")
        self.assertEqual(rc, 2)

    def test_help_va_thieu_doi_so(self):
        rc, out, err = run(MARK, "--help")
        self.assertEqual(rc, 0)
        self.assertIn("--versions", out)
        rc, out, err = run(MARK)
        self.assertEqual(rc, 2)

    def test_doc_dang_list_phang_va_dict(self):
        l = self.lane("a", ["x1"])
        w(self.d / "q.json", [{"id": "x1", "version": 2, "status": "approved", "note": "n"}])
        rc, out, err = self.go([l], self.d / "q.json")
        self.assertEqual(json.loads(out)["the_gan"], 1, out)
        w(self.d / "q2.json", {"x1": {"version": 2, "data": {"status": "edited"}}})
        rc, out, err = self.go([l], self.d / "q2.json")
        self.assertEqual(json.loads(out)["the_gan"], 1, out)


class Seed(Base):
    def docs(self, names):
        for n in names:
            w(self.d / "docs" / (n + ".json"), {"intro": n, "items": []})

    def go(self, remote, *extra):
        return run(SEED, "--docs", self.d / "docs", "--collection", "report", "--remote", remote, "--out", self.d / "out", "--json", *extra)

    def test_chi_nap_tai_lieu_thieu(self):
        self.docs(["meta", "links", "year"])
        w(self.d / "r.json", {"documents": [{"doc_id": "meta", "version": 3, "data": {"intro": "meta", "items": []}}]})
        rc, out, err = self.go(self.d / "r.json", "--only-missing", "--ghi")
        r = json.loads(out)
        self.assertEqual(rc, 0, out)
        self.assertEqual(r["nap"], 2)
        writes = json.loads((self.d / "out" / "_writes_01.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(x["doc_id"] for x in writes), ["links", "year"])
        self.assertTrue(all(x["op"] == "set" and "if_version" not in x for x in writes))

    def test_tai_lieu_khac_kem_if_version_va_giong_thi_bo(self):
        self.docs(["meta", "links"])
        w(self.d / "docs" / "meta.json", {"intro": "mới", "items": []})
        w(self.d / "r.json", {"documents": [{"doc_id": "meta", "version": 3, "data": {"intro": "cũ", "items": []}},
                                             {"doc_id": "links", "version": 1, "data": {"intro": "links", "items": []}}]})
        rc, out, err = self.go(self.d / "r.json", "--ghi")
        r = json.loads(out)
        self.assertEqual(r["nap"], 1)
        writes = json.loads((self.d / "out" / "_writes_01.json").read_text(encoding="utf-8"))
        self.assertEqual((writes[0]["doc_id"], writes[0]["if_version"]), ("meta", 3))
        self.assertEqual(r["bo"][0]["id"], "links")

    def test_khac_ma_thieu_version_la_loi(self):
        self.docs(["meta"])
        w(self.d / "docs" / "meta.json", {"intro": "mới", "items": []})
        w(self.d / "rd" / "meta.json", {"intro": "cũ", "items": []})
        rc, out, err = self.go(self.d / "rd", "--ghi")
        self.assertEqual(rc, 1)
        self.assertFalse((self.d / "out").exists())

    def test_tu_choi_collection_cua_nguoi_duyet(self):
        self.docs(["meta"])
        w(self.d / "r.json", [])
        for col in ("reviews", "edits"):
            rc, out, err = run(SEED, "--docs", self.d / "docs", "--collection", col, "--remote", self.d / "r.json")
            self.assertEqual(rc, 2, col)

    def test_chia_lo_theo_so_lenh_va_dung_luong(self):
        self.docs(["d%02d" % i for i in range(7)])
        w(self.d / "r.json", {"documents": []})
        rc, out, err = self.go(self.d / "r.json", "--batch-size", "3", "--ghi")
        self.assertEqual(json.loads(out)["so_lo"], 3)
        size = (self.d / "docs" / "d00.json").stat().st_size
        rc, out, err = self.go(self.d / "r.json", "--max-bytes", str(size * 2 + 1), "--force", "--ghi")
        self.assertEqual(json.loads(out)["so_lo"], 4)

    def test_tai_lieu_qua_256kib_la_loi(self):
        w(self.d / "docs" / "big.json", {"intro": "x" * (257 * 1024), "items": []})
        w(self.d / "r.json", [])
        rc, out, err = self.go(self.d / "r.json")
        self.assertEqual(rc, 1)

    def test_chay_thu_khong_ghi(self):
        self.docs(["meta"])
        w(self.d / "r.json", [])
        rc, out, err = self.go(self.d / "r.json")
        self.assertEqual(rc, 0)
        self.assertFalse((self.d / "out").exists())


if __name__ == "__main__":
    unittest.main()
