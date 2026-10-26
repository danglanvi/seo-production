"""Test contrast.py bằng bảng giả. Chạy: python3 -B tests/test_contrast.py

Ca hỏng thật lấy từ đợt dựng theme site TAG 17/10/2026:
- chữ trắng trên nút CTA gradient cam #FF5A1F → #FF9E1B không đạt AA;
- màu chàm #2F3E9E nằm ngoài guideline (tím #850DBA → cyan #00CCFF).
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import contrast  # noqa: E402

BRAND = "#850DBA,#00CCFF"

TABLE = """Ghi chú đầu file.

| Token brand | Token theme | Nơi dùng | Chữ | Nền | Cỡ | Ngoại lệ |
|---|---|---|---|---|---|---|
| #850DBA | --tg-link | link trong bài | #4F46C8 | #FFFFFF | text | |
| #850DBA | --tg-chip | chip nhãn | #FFFFFF | #4F46C8 | text | |
| - | --tg-cta | nút mua | #FFFFFF | #FF5A1F → #FF9E1B | large | |
| #2F3E9E | --tg-primary | tiêu đề | #2F3E9E | #FFFFFF | large | |
| #00CCFF | --tg-deco | đường viền | | | | |

Đoạn cuối giữ nguyên.
"""


def run(argv):
    out = []
    orig = contrast.print if hasattr(contrast, "print") else None
    contrast.print = lambda *a, **k: out.append(" ".join(str(x) for x in a))
    try:
        rc = contrast.main(argv)
    finally:
        if orig is None:
            del contrast.print
        else:
            contrast.print = orig
    return rc, "\n".join(out)


def test_math():
    assert contrast.fmt_ratio(contrast.ratio((0, 0, 0), (255, 255, 255))) == "21.00"
    # #767676 trên trắng đạt 4.5, #777777 thì không
    assert contrast.ratio(contrast.parse_hex("#767676"), (255, 255, 255)) >= 4.5
    assert contrast.ratio(contrast.parse_hex("#777"), (255, 255, 255)) < 4.5
    assert contrast.parse_hex("#fff") == (255, 255, 255)


def test_gradient_takes_worst_stop():
    # chữ trắng trên 2 đầu gradient: đầu cam sáng quyết định
    r = contrast.worst_ratio("#FFFFFF", "#FF5A1F → #FF9E1B")
    assert r < 2.1
    assert r < contrast.worst_ratio("#FFFFFF", "#FF5A1F")


def test_check_real_failures():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d, "bang.md")
        f.write_text(TABLE, encoding="utf-8")
        rc, out = run(["check", str(f)])
        assert rc == 1
        assert "--tg-link\t" in out and "đạt" in out
        cta = [x for x in out.splitlines() if x.startswith("--tg-cta")][0]
        assert "trượt" in cta  # 2.06 < 3.0 dù cỡ large
        assert "BỎ QUA" in [x for x in out.splitlines() if x.startswith("--tg-deco")][0]
        # không có --brand thì #2F3E9E không bị báo
        assert "NGOÀI GUIDELINE" not in out
        rc, out = run(["check", str(f), "--brand", BRAND])
        assert rc == 1
        prim = [x for x in out.splitlines() if x.startswith("--tg-primary")][0]
        assert "ngoài guideline: #2F3E9E" in prim
        # chạy thử: file không đổi
        assert f.read_text(encoding="utf-8") == TABLE


def test_waiver_and_write():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d, "bang.md")
        waived = (TABLE.replace("| large | |\n", "| large | CTA cam đã treo, chờ Vincent |\n")
                  .replace("| #2F3E9E | --tg-primary", "| #00CCFF | --tg-primary"))
        f.write_text(waived, encoding="utf-8")
        rc, out = run(["check", str(f), "--brand", BRAND])
        assert rc == 0, out
        assert "ngoại lệ (CTA cam đã treo, chờ Vincent)" in out
        rc, _ = run(["check", str(f), "--brand", BRAND, "--write"])
        assert rc == 0
        txt = f.read_text(encoding="utf-8")
        assert txt.startswith("Ghi chú đầu file.\n") and txt.rstrip().endswith("Đoạn cuối giữ nguyên.")
        assert "| Tương phản |" in txt and "6.90:1 đạt" in txt
        # chạy lại không thêm cột thứ hai
        run(["check", str(f), "--write"])
        assert f.read_text(encoding="utf-8").count("Tương phản") == 1


def test_csv_and_errors():
    with tempfile.TemporaryDirectory() as d:
        c = Path(d, "bang.csv")
        c.write_text("token theme,chữ,nền\n--a,#000000,#FFFFFF\n--b,#777777,#FFFFFF\n", encoding="utf-8")
        rc, out = run(["check", str(c)])
        assert rc == 1 and "--b\t4.47:1 trượt" in out
        # alpha, thiếu cột, thiếu file: exit 2
        c.write_text("token theme,chữ,nền\n--a,#00000080,#FFFFFF\n", encoding="utf-8")
        assert run(["check", str(c)])[0] == 2
        c.write_text("token theme,màu\n--a,#000000\n", encoding="utf-8")
        assert run(["check", str(c)])[0] == 2
        assert run(["check", f"{d}/khong-co.md"])[0] == 2
        c.write_text("token theme,chữ,nền,cỡ\n--a,#000000,#FFFFFF,huge\n", encoding="utf-8")
        assert run(["check", str(c)])[0] == 2


REAL_TAG = """| Token brand | Token theme | Nơi dùng | Chữ | Nền | Cỡ | Ngoại lệ |
|---|---|---|---|---|---|---|
| #850DBA #00CCFF (pha) | --tg-pu3 | link | #4F46C8 | #FFFFFF | text | |
| #850DBA | --tg-gt | chữ gradient H1, H2 | #850DBA, #4F46C8, #1D72C9 | #FFFFFF | large | |
| #7A7FD1 | --tg-pu | chấm đầu dòng | #7A7FD1 | #FFFFFF | ui | |
| #1A1A2E | --gt2 | chữ gradient trên nền tối | #D3B8FA #A9B2F5 #33D6FF | #1A1A2E | large | |
| - | --tg-cta | nút mua | #FFFFFF | #F0123A → #FF3D1F → #FF7A00 | text | điểm treo cũ, chờ duyệt |
| #2F3E9E | --tg-pu3-cu | link bản cũ | #2F3E9E | #FFFFFF | text | |
"""


def test_real_tag_palette_gradient_text():
    # Ca thật site TAG 17/10/2026 (bảng màu brand v1, contrast_brand.py): chữ gradient trong H1 cần nhiều mã ở ô chữ.
    r = lambda fg, bg: contrast.worst_ratio(fg, bg)
    assert abs(r("#4F46C8", "#FFFFFF") - 6.90) < 0.01
    assert abs(r("#850DBA, #4F46C8, #1D72C9", "#FFFFFF") - 4.88) < 0.01
    assert abs(r("#FFFFFF", "#F0123A → #FF3D1F → #FF7A00") - 2.61) < 0.01
    assert abs(r("#D3B8FA #A9B2F5 #33D6FF", "#1A1A2E") - 8.43) < 0.01
    with tempfile.TemporaryDirectory() as d:
        f = Path(d, "bang.md")
        f.write_text(REAL_TAG, encoding="utf-8")
        rc, out = run(["check", str(f), "--brand", "#850DBA,#00CCFF,#7A7FD1,#A758BA,#1A1A2E,#FFFFFF"])
        lines = {x.split("\t")[0]: x for x in out.splitlines() if "\t" in x}
        assert "4.88:1 đạt" in lines["--tg-gt"]
        assert "ngoại lệ (điểm treo cũ, chờ duyệt)" in lines["--tg-cta"]
        assert "ngoài guideline: #2F3E9E" in lines["--tg-pu3-cu"]
        assert "NGOÀI GUIDELINE" not in lines["--tg-pu3"]  # màu pha ghi gốc guideline ở cột Token brand
        assert rc == 1 and "1 dòng cần sửa" in out
        c = Path(d, "bang.csv")
        c.write_text("token theme,chữ,nền\n--a,,#FFFFFF\n", encoding="utf-8")
        assert run(["check", str(c)])[0] == 2  # ô chữ trống nhưng có nền


def test_pair_cli():
    assert run(["pair", "#FFFFFF", "#FF5A1F,#FF9E1B"])[0] == 1
    assert run(["pair", "#FFFFFF", "#FF5A1F"])[0] == 1  # 3.11 < 4.5 với chữ thường
    assert run(["pair", "#FFFFFF", "#FF5A1F", "--size", "large"])[0] == 0  # 3.11 >= 3.0 với chữ lớn
    assert run(["pair", "#4F46C8", "#FFFFFF"])[0] == 0


if __name__ == "__main__":
    test_math()
    test_gradient_takes_worst_stop()
    test_check_real_failures()
    test_waiver_and_write()
    test_csv_and_errors()
    test_real_tag_palette_gradient_text()
    test_pair_cli()
    print("OK 7 test")
