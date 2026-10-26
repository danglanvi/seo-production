"""Test parity.py bằng ảnh và file giả. Chạy: python3 -B tests/test_parity.py (cần Pillow)"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import parity  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


def shot(path, h, box=None, color=(0, 0, 0)):
    im = Image.new("RGB", (100, h), "white")
    if box:
        ImageDraw.Draw(im).rectangle(box, fill=color)
    im.save(path)


def test_shots():
    with tempfile.TemporaryDirectory() as d:
        shot(f"{d}/same-a-d.png", 200)
        shot(f"{d}/same-b-d.png", 200, (0, 150, 9, 151), (240, 240, 240))  # lệch màu nhỏ hơn tol 32: không tính
        shot(f"{d}/low-a-d.png", 200)
        shot(f"{d}/low-b-d.png", 200, (0, 150, 99, 151))  # 200 điểm = 1% cả trang, 0% màn đầu
        shot(f"{d}/top-a-d.png", 200)
        shot(f"{d}/top-b-d.png", 200, (0, 0, 99, 1))  # 1% cả trang, 2% màn đầu 100 px
        shot(f"{d}/tall-a-d.png", 200)
        shot(f"{d}/tall-b-d.png", 220)
        out = []
        orig = print
        try:
            parity.print = lambda s: out.append(s)
            rc = parity.main(["shots", "--dir", d, "--a", "a", "--b", "b", "--fold", "d=100"])
        finally:
            parity.print = orig
        rows = {r.split("\t")[0]: r for r in out[0].splitlines()}
        assert rows["same-d.png"].endswith("đạt") and "lệch cả trang=0.00%" in rows["same-d.png"]
        assert rows["low-d.png"].endswith("đạt") and "lệch cả trang=1.00%" in rows["low-d.png"]
        assert rows["top-d.png"].endswith("LỆCH") and "màn đầu=2.00%" in rows["top-d.png"]
        assert rows["tall-d.png"].endswith("LỆCH")
        assert rc == 1


def test_status_and_text():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "a.tsv").write_text("/\t200 \n/x\t301 https://s/x/?q=1\n", encoding="utf-8")
        Path(d, "b.tsv").write_text("/\t200 \n/x\t301 https://s/x/\n", encoding="utf-8")
        assert parity.main(["status", "--a", f"{d}/a.tsv", "--b", f"{d}/b.tsv"]) == 1
        assert parity.main(["status", "--a", f"{d}/a.tsv", "--b", f"{d}/b.tsv", "--ignore-query-in-redirect"]) == 0
        for side, txt in (("ta", "Xin  chào\nbạn"), ("tb", "Xin chào bạn")):
            Path(d, side).mkdir()
            Path(d, side, "home.txt").write_text(txt, encoding="utf-8")
        assert parity.main(["text", "--a", f"{d}/ta", "--b", f"{d}/tb"]) == 0
        Path(d, "tb", "home.txt").write_text("Xin chào các bạn", encoding="utf-8")
        assert parity.main(["text", "--a", f"{d}/ta", "--b", f"{d}/tb"]) == 1


if __name__ == "__main__":
    test_shots()
    test_status_and_text()
    print("OK 2 test")
