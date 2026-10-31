"""Test offline: media_plan.py (tu-md, kiem, chu-so-do), svg_dung.py (10 kiểu, định tuyến mũi tên), chen_media.py. Không cần Chrome.
Chạy từ skills/anh-trong-bai/: python3 -B tests/test_media_bai.py"""
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
FIX = HERE / "fixtures"
PROFILE = FIX / "web-profile.json"


def run(*args):
    r = subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def png(path, w, h):
    raw = b"".join(b"\x00" + b"\xff\xff\xff" * w for _ in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


SO_DO = {
    "luong": {"kieu": "luong", "to": [1], "nhom": [{"tu": 0, "den": 1, "nhan": "Chuẩn bị"}],
              "buoc": [{"tieu_de": f"Bước {i}", "mo_ta": "Việc ngắn"} for i in range(1, 6)]},
    "quyet-dinh": {"kieu": "quyet-dinh", "dau": "Đất trong chậu", "hoi": "Đất còn ẩm không?",
                   "co": {"nhan": "Có", "ket_qua": "Chờ", "tiep": "Kiểm lại ngày mai"},
                   "khong": {"nhan": "Không", "ket_qua": "Tưới", "tiep": "Tưới đến khi nước chảy ra đáy"}},
    "khoi": {"kieu": "khoi", "khoi": [{"tieu_de": "Cây"}, {"tieu_de": "Đất"}, {"tieu_de": "Nước", "to": True}],
             "noi": [{"tu": 0, "den": 1, "nhan": "mọc trong"}, {"tu": 0, "den": 2, "nhan": "cần", "net": "dut"}]},
    "so-sanh": {"kieu": "so-sanh", "cot": [{"tieu_de": "Tưới tay", "dong": ["Rẻ", "Tốn công"]},
                                          {"tieu_de": "Tưới nhỏ giọt", "dong": ["Đều", "Tốn tiền lắp"], "to": True}]},
    "moc": {"kieu": "moc", "moc": [{"thoi_gian": "Tháng 1", "tieu_de": "Gieo"}, {"thoi_gian": "Tháng 3", "tieu_de": "Thu"}]},
    "cot": {"kieu": "cot", "don_vi": " lít", "nguon": "Trạm mẫu 2026",
            "du_lieu": [{"nhan": "Rau", "gia_tri": 2}, {"nhan": "Cây ăn quả", "gia_tri": 8, "to": True}]},
    "danh-sach": {"kieu": "danh-sach", "muc": [{"tieu_de": "Liệt kê cây"}, {"tieu_de": "Đo ẩm"}, {"tieu_de": "Chia lịch"}]},
}


def plan_7(d):
    items = [{"id": f"IMG-0{i}", "loai": "so-do", "alt": f"Sơ đồ mẫu kiểu {k}", "caption": f"Điều rút ra từ kiểu {k}",
              "ten_file": f"so-do-{k}", "so_do": sp} for i, (k, sp) in enumerate(SO_DO.items(), 1)]
    p = Path(d, "media_plan.json")
    p.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
    return p


def test_tu_md():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "media_plan.json")
        rc, log = run(SCRIPTS / "media_plan.py", "tu-md", FIX / "bai-mau.md", "--out", out)
        assert rc == 0, log
        items = json.loads(out.read_text(encoding="utf-8"))["items"]
        assert [(i["id"], i["loai"], i["ten_file"]) for i in items] == [
            ("IMG-01", "so-do", "lich-tuoi-4-buoc"), ("IMG-02", "anh-chup", "huong-dan-do-am")]
        assert items[0]["alt"] == "Bốn bước lập lịch tưới cây cho vườn nhỏ"
        rc, log = run(SCRIPTS / "media_plan.py", "tu-md", FIX / "bai-mau.md", "--out", out)
        assert rc != 0 and "Không ghi đè" in log


def test_svg_7_kieu_va_chu_so_do():
    with tempfile.TemporaryDirectory() as d:
        p = plan_7(d)
        rc, log = run(SCRIPTS / "svg_dung.py", p, "--profile", PROFILE, "--out", Path(d, "media"))
        assert rc == 0, log
        items = json.loads(p.read_text(encoding="utf-8"))["items"]
        for it in items:
            for k in ("svg", "svg_m"):
                s = Path(d, it[k]).read_text(encoding="utf-8")
                assert s.startswith("<svg") and 'role="img"' in s and "<title" in s, it["id"]
        both = Path(d, items[0]["svg"]).read_text(encoding="utf-8") + Path(d, items[0]["svg_m"]).read_text(encoding="utf-8")
        ids = re.findall(r'\bid="([^"]+)"', both)
        assert len(ids) == len(set(ids)), "trùng id giữa bản desktop và bản điện thoại"
        assert "Nguồn: Trạm mẫu 2026" in Path(d, items[5]["svg"]).read_text(encoding="utf-8")
        rc, _ = run(SCRIPTS / "media_plan.py", "chu-so-do", p, "--out", Path(d, "chu.json"))
        chu = json.loads(Path(d, "chu.json").read_text(encoding="utf-8"))["items"]
        assert len(chu) == 7 and "Đất còn ẩm không?" in chu[1]["json_prompt"]["elements"][0]["items"]
        assert "Cây ăn quả 8" in chu[5]["json_prompt"]["elements"][0]["items"]
        bad = json.loads(p.read_text(encoding="utf-8"))
        del bad["items"][5]["so_do"]["nguon"]
        p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        rc, _ = run(SCRIPTS / "svg_dung.py", p, "--profile", PROFILE, "--out", Path(d, "media"), "--only", "IMG-06")
        assert rc != 0, "biểu đồ cột thiếu nguồn phải dừng"


LAN = {"kieu": "lan", "lan": ["Bạn (SEO)", "AI · Claude Code", "Google Sheet"],
       "buoc": [{"tieu_de": "Giao việc", "lan": 0}, {"tieu_de": "Lập outline", "lan": 1}, {"tieu_de": "Ghi lên Sheet", "lan": 2},
                {"tieu_de": "Review", "lan": 0}, {"tieu_de": "Còn Chặn?", "lan": 0, "hoi": True},
                {"tieu_de": "AI chỉnh", "lan": 1, "cot": 4}, {"tieu_de": "Sheet cập nhật", "lan": 2, "cot": 4},
                {"tieu_de": "Chốt", "lan": 0, "cot": 5}],
       "noi": [{"tu": 0, "den": 1}, {"tu": 1, "den": 2}, {"tu": 2, "den": 3}, {"tu": 3, "den": 4},
               {"tu": 4, "den": 5, "nhan": "Có"}, {"tu": 5, "den": 6}, {"tu": 4, "den": 7, "nhan": "Không"}],
       "vong": [{"tu": 6, "den": 3, "nhan": "Vòng sửa", "loai": "sua"}]}
VONG = {"kieu": "vong-lap", "buoc": [{"tieu_de": "Nộp bài"}, {"tieu_de": "Máy kiểm"}, {"tieu_de": "AI gắn cờ"}, {"tieu_de": "Người quyết"}],
        "vong": [{"tu": 1, "den": 0, "nhan": "Còn lỗi", "loai": "sua"}, {"tu": 3, "den": 0, "nhan": "Có Chặn", "loai": "sua"},
                 {"tu": 3, "den": 2, "nhan": "Bài học tuần", "loai": "hoc"}]}
SO = {"kieu": "so-lieu", "nguon": "Trạm mẫu 2026", "so": [{"truoc": "40", "gia_tri": "15", "nhan": "Mục người chấm", "to": True},
                                                        {"gia_tri": "47", "don_vi": "%", "nhan": "Giảm ký tự"}]}


def test_lan_vong_lap_so_lieu():
    sys.path.insert(0, str(SCRIPTS))
    import svg_dung as m
    pal, font = m.palette(json.loads(PROFILE.read_text(encoding="utf-8")))
    # mọi mũi tên đi theo trục, không cắt hộp hay tên làn (ca lỗi: mũi tên chéo, mũi tên đè tên làn 31/10/2026)
    for sp in (LAN, VONG):
        s = m.Svg(760, pal, font, "t", "d", "x")
        m.KIND[sp["kieu"]](s, sp, False)
        assert all(ok for _, _, ok in s.tuyen), [(e, ok) for e, _, ok in s.tuyen]
        if sp.get("lan"):
            assert len(s.rects) == len(sp["buoc"]) + len(sp["lan"]), "tên làn phải là vật cản khi định tuyến"
        for _, pts, _ in s.tuyen:
            assert all(a[0] == b[0] or a[1] == b[1] for a, b in zip(pts, pts[1:])), pts
    with tempfile.TemporaryDirectory() as d:
        items = [{"id": f"IMG-0{i}", "loai": "so-do", "alt": f"Sơ đồ {k}", "caption": "c", "ten_file": k, "so_do": sp}
                 for i, (k, sp) in enumerate((("lan", LAN), ("vong-lap", VONG), ("so-lieu", SO)), 1)]
        p = Path(d, "media_plan.json")
        p.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
        rc, log = run(SCRIPTS / "svg_dung.py", p, "--profile", PROFILE, "--out", Path(d, "media"))
        assert rc == 0, log
        for k in ("lan", "vong-lap", "so-lieu"):
            for suf in ("", "-m"):
                assert Path(d, "media", f"{k}{suf}.svg").read_text(encoding="utf-8").startswith("<svg"), k + suf
        v = Path(d, "media", "vong-lap.svg").read_text(encoding="utf-8")
        assert 'stroke="#DC2626"' in v and 'stroke-dasharray' in v and 'paint-order="stroke"' in v
        assert "Nguồn: Trạm mẫu 2026" in Path(d, "media", "so-lieu.svg").read_text(encoding="utf-8")
        run(SCRIPTS / "media_plan.py", "chu-so-do", p, "--out", Path(d, "chu.json"))
        chu = json.loads(Path(d, "chu.json").read_text(encoding="utf-8"))["items"]
        assert "sua" not in chu[1]["json_prompt"]["elements"][0]["items"] and "Mục người chấm 15" in chu[2]["json_prompt"]["elements"][0]["items"]
        for bad in ({**SO, "nguon": ""}, {**LAN, "buoc": [{"tieu_de": "X", "lan": 5}]}, {**VONG, "vong": [{"tu": 1, "den": 9}]}):
            items[0]["so_do"] = bad
            p.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
            rc, _ = run(SCRIPTS / "svg_dung.py", p, "--profile", PROFILE, "--out", Path(d, "media"), "--only", "IMG-01")
            assert rc != 0, bad


CH3 = {"kieu": "lan", "lan": ["Chấm bài", "Theo dõi và học"],
       "buoc": [{"tieu_de": "Nộp bài", "cot": 0}, {"tieu_de": "Máy kiểm", "cot": 1}, {"tieu_de": "AI gắn cờ", "cot": 2},
                {"tieu_de": "Người quyết", "cot": 3}, {"tieu_de": "Đạt", "cot": 4},
                {"tieu_de": "Script", "lan": 1, "cot": 3}, {"tieu_de": "Bài học", "lan": 1, "cot": 2}],
       "noi": [{"tu": 0, "den": 1}, {"tu": 1, "den": 2}, {"tu": 2, "den": 3}, {"tu": 3, "den": 4},
               {"tu": 3, "den": 5, "nhan": "Comment"}, {"tu": 5, "den": 6}],
       "vong": [{"tu": 1, "den": 0, "nhan": "Còn lỗi", "loai": "sua"}, {"tu": 3, "den": 0, "nhan": "Có Chặn", "loai": "sua"},
                {"tu": 6, "den": 2, "nhan": "Tuần sau", "loai": "hoc"}]}
OAI = {"kieu": "lan", "lan": ["Bạn", "AI", "Sheet"],
       "buoc": [{"tieu_de": "Giao việc", "lan": 0}, {"tieu_de": "Lập outline", "lan": 1}, {"tieu_de": "Ghi lên Sheet", "lan": 2},
                {"tieu_de": "Review", "lan": 0}, {"tieu_de": "AI chỉnh", "lan": 1, "cot": 3},
                {"tieu_de": "Sheet cập nhật", "lan": 2, "cot": 3}, {"tieu_de": "Chốt", "lan": 0, "cot": 4}],
       "noi": [{"tu": 0, "den": 1}, {"tu": 1, "den": 2}, {"tu": 2, "den": 3}, {"tu": 3, "den": 4, "nhan": "Còn Chặn"},
               {"tu": 4, "den": 5}, {"tu": 3, "den": 6, "nhan": "Hết Chặn"}],
       "vong": [{"tu": 5, "den": 3, "nhan": "Vòng sửa", "loai": "sua"}]}


def test_mui_ten_lan_31_10_toi():
    """Ca lỗi tối 31/10/2026: vòng cùng cột xuyên hộp giữa, tên làn bị mũi tên đè, nhãn mũi tên ngắn trôi xa,
    vòng cắt nhau ở bản điện thoại, đầu mũi tên phóng theo độ dày nét."""
    sys.path.insert(0, str(SCRIPTS))
    import svg_dung as m
    pal, font = m.palette(json.loads(PROFILE.read_text(encoding="utf-8")))
    for sp in (CH3, OAI, LAN):
        s = m.Svg(760, pal, font, "t", "d", "x")
        m.KIND["lan"](s, sp, False)
        n = len(sp["buoc"])
        assert all(m._ranh(pts, s.rects[:n], e["tu"], e["den"]) for e, pts, _ in s.tuyen), "đường cắt hộp"
        # tên làn không nằm trên nét nào
        for tx, ty, tw, th in s.ten_lan:
            for _, pts, _ in s.tuyen:
                assert not any(m._cat(g, (tx, ty, tw, th), 2) for g in zip(pts, pts[1:])), (tx, pts)
        # mũi tên ngang có nhãn giữa 2 cột liền nhau: đoạn ngang đủ dài để nhãn nằm trên nét
        for e, pts, _ in s.tuyen:
            ngang = [abs(a[0] - b[0]) for a, b in zip(pts, pts[1:]) if abs(a[1] - b[1]) < 1]
            if e.get("nhan") and e["loai"] == "tien" and len(pts) == 2 and ngang:
                assert ngang[0] >= m.text_w(e["nhan"], 13, True) + 12, (e, ngang)
        mb = m.Svg(320, pal, font, "t", "d", "y")
        m.KIND["lan"](mb, sp, True)
        for side, ks in mb.ranh_doc.items():
            for i, p in enumerate(ks):
                for q in ks[i + 1:]:
                    assert not (p[0] < q[0] < p[1] < q[1] or q[0] < p[0] < q[1] < p[1]), (side, p, q)
    out = s.render()
    assert 'markerUnits="userSpaceOnUse"' in out and " Q" in out, "đầu mũi tên cỡ cố định, góc bo"


def test_kiem_luat():
    items = [
        {"id": "IMG-01", "loai": "so-do", "alt": "Ảnh sơ đồ tưới", "caption": "x", "ten_file": "a"},
        {"id": "IMG-02", "loai": "so-do", "alt": "Clip mô phỏng đường quét", "caption": "y", "ten_file": "b"},
        {"id": "IMG-03", "loai": "anh-ai", "alt": "Vườn rau", "caption": "z", "ten_file": "c", "mo_ta": "đội ngũ đang tưới"},
        {"id": "IMG-04", "loai": "anh-chup", "alt": "Đoạn hướng dẫn", "caption": "Đoạn hướng dẫn", "ten_file": "Ten_File"},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "plan.json")
        p.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
        rc, log = run(SCRIPTS / "media_plan.py", "kiem", p, "--profile", PROFILE)
        assert rc == 1
        for s in ('IMG-01: alt mở bằng', 'IMG-02: alt nói "Clip"', "IMG-03: ảnh AI tả người", "IMG-04: caption trùng alt",
                  'IMG-04: ten_file "Ten_File"'):
            assert s in log, s


def test_chen_media():
    with tempfile.TemporaryDirectory() as d:
        p = plan_7(d)
        run(SCRIPTS / "svg_dung.py", p, "--profile", PROFILE, "--out", Path(d, "media"), "--only", "IMG-01")
        plan = json.loads(p.read_text(encoding="utf-8"))
        png(Path(d, "media", "chup.png"), 40, 30)
        plan["items"] = [plan["items"][0], {"id": "IMG-09", "loai": "anh-chup", "alt": "Đoạn hướng dẫn độ ẩm",
                                             "caption": "Trạm mẫu, chụp ngày 27/10/2026", "ten_file": "chup", "src": "media/chup.png"}]
        p.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        hole = '<figure class="wide cho-media" data-img="{}"><figcaption>[Chờ media {}]</figcaption></figure>'
        h = Path(d, "bai.html")
        h.write_text("<html><head></head><body><main>" + hole.format("IMG-01", "IMG-01") + hole.format("IMG-09", "IMG-09")
                     + "</main></body></html>", encoding="utf-8")
        for _ in range(2):  # chèn lại lần hai không nhân đôi khối hay CSS
            rc, log = run(SCRIPTS / "chen_media.py", h, p)
            assert rc == 0 and "chèn 2" in log, log
        s = h.read_text(encoding="utf-8")
        assert s.count('class="sv-d"') == 1 and s.count('class="sv-m"') == 1 and s.count(".sv-m{display:none}") == 1
        assert 'width="40" height="30" loading="lazy" decoding="async"' in s and "cho-media" not in s
        rc, log = run(SCRIPTS / "media_plan.py", "kiem", p, "--profile", PROFILE, "--html", h)
        assert rc == 0, log


if __name__ == "__main__":
    test_tu_md()
    test_svg_7_kieu_va_chu_so_do()
    test_lan_vong_lap_so_lieu()
    test_mui_ten_lan_31_10_toi()
    test_kiem_luat()
    test_chen_media()
    print("OK 6 test")
