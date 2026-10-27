"""Test offline: media_plan.py (tu-md, kiem, chu-so-do), svg_dung.py (7 kiểu), chen_media.py. Không cần Chrome.
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
    test_kiem_luat()
    test_chen_media()
    print("OK 4 test")
