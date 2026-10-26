"""Test offline sua_truc_tiep.py: khối lá, chuẩn hoá NFC, <br>, khối chữ trùng k#n. Chạy: python3 -B tests/test_sua_truc_tiep.py"""
import json
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sua_truc_tiep as st  # noqa: E402

NFD = unicodedata.normalize("NFD", "Dịch vụ SEO")
HTML = f"""<html><head><title>x</title></head><body>
<ul><li><p>Mục lồng</p></li></ul>
<p>{NFD}</p><p>Xem thêm</p><div><p>Dòng 1<br>Dòng 2</p></div><p>Xem thêm</p><script>var x='<p>KHONG-LAY</p>'</script>
</body></html>"""


def test_build_and_apply():
    with tempfile.TemporaryDirectory() as d:
        src = Path(d, "page.html")
        src.write_text(HTML, encoding="utf-8")
        out = Path(d, "edit.html")
        st.main(["build", "--html", str(src), "--page", "pg", "--title", "T", "--out", str(out)])
        s = out.read_text(encoding="utf-8")
        _, blocks = st.load_saved(out)
        texts = [t for _, t in blocks]
        assert texts == ["Mục lồng", "Dịch vụ SEO", "Xem thêm", "Dòng 1 Dòng 2", "Xem thêm"], texts  # li chứa p: chỉ p là khối lá
        assert unicodedata.is_normalized("NFC", texts[1]) and "KHONG-LAY" not in s
        ids = [b for b, _ in blocks]
        edits = {"page": "pg", "edits": [{"b": ids[4], "before": "Xem thêm", "text": "Xem chi tiết"}], "meta": {}, "note": ""}
        saved = Path(d, "saved.html")
        saved.write_text(s.replace('<script type="application/json" id="ed-edits">{}</script>',
                                   '<script type="application/json" id="ed-edits">' + json.dumps(edits, ensure_ascii=False) + "</script>"), encoding="utf-8")
        st.main(["apply", str(saved), "--out", str(Path(d, "edits"))])
        rec = json.loads(Path(d, "edits", ids[4] + ".json").read_text(encoding="utf-8"))
        assert rec["dup"] == "k#2" and rec["text"] == "Xem chi tiết" and rec["status"] == "edited"


if __name__ == "__main__":
    test_build_and_apply()
    print("OK 1 test")
