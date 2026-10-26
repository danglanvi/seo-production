"""Test offline: đo chữ nhỏ nhất của diagram_render.mjs và kiểm chữ sơ đồ với thân bài. Chạy: python3 -B tests/test_diagram.py
Ca hỏng thật: 19/10 'AI27 ... chữ nhỏ nhất nullpx đạt' (minFont null bị coi là đạt) và sơ đồ AI19 'Có schema' trái thân bài."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import diagram_body_check as dbc  # noqa: E402

NODE = shutil.which("node")
CHROME = os.environ.get("CHROME_BIN") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def node_eval(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], capture_output=True, text=True, timeout=30, cwd=SCRIPTS)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_min_font_logic():
    r = node_eval("""import {minFontOf, isMeasured, judgeMinFont} from './diagram_checks.mjs';
console.log(JSON.stringify({
  empty: minFontOf([]), inf: minFontOf([Infinity]), nan: minFontOf([NaN, 0]), ok: minFontOf([30, 18, 22]),
  m_null: isMeasured(null), m_inf: isMeasured(Infinity), m_str: isMeasured('20'), m_ok: isMeasured(18),
  j_null: judgeMinFont(null, 24), j_undef: judgeMinFont(undefined, 0), j_low: judgeMinFont(10, 24), j_ok: judgeMinFont(20, 24), j_nospec: judgeMinFont(8, 0)}))""")
    assert r["empty"] is None and r["inf"] is None and r["nan"] is None and r["ok"] == 18
    assert not r["m_null"] and not r["m_inf"] and not r["m_str"] and r["m_ok"]
    for k in ("j_null", "j_undef"):  # lỗi cũ: null được coi là đạt dù spec có hay không
        assert r[k]["measured"] is False and r[k]["issue"] and "không đo được" in r[k]["label"]
    assert r["j_low"]["issue"] == "chữ nhỏ nhất 10px, spec 24px"
    assert r["j_ok"]["issue"] is None and r["j_nospec"]["issue"] is None


def run_render(html, spec_extra):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "src").mkdir()
        (root / "src" / "AI27.html").write_text(
            f'<!doctype html><meta charset="utf-8"><body style="margin:0"><script>window.__ready=true</script>{html}', encoding="utf-8")
        spec = {"id": "AI27", "size_px": "400x200", "export": {"file_name": "ai27.webp", "max_kb": 200}, **spec_extra}
        (root / "specs.json").write_text(json.dumps({"items": [spec]}), encoding="utf-8")
        env = {**os.environ, "ROOT": str(root)}
        r = subprocess.run([NODE, str(SCRIPTS / "diagram_render.mjs"), "AI27"], capture_output=True, text=True, timeout=120, env=env)
        rep = json.loads((root / "out" / "AI27.check.json").read_text(encoding="utf-8")) if (root / "out" / "AI27.check.json").exists() else None
        return r, rep


def test_render_null_min_font_is_error():
    if not (NODE and Path(CHROME).exists()):
        print("bỏ qua test_render_null_min_font_is_error: thiếu node hoặc Chrome")
        return
    # Canvas không có chữ nào đo được: bản cũ in 'chữ nhỏ nhất nullpx đạt'.
    r, rep = run_render('<div class="canvas" style="width:400px;height:200px;background:#eee"></div>',
                        {"json_prompt": {"typography": {"min_text_height": "24px"}}})
    assert r.returncode == 1, r.stdout + r.stderr
    assert "nullpx" not in r.stdout and "không đo được" in r.stdout and "đạt" not in r.stdout.split("\n")[0].replace("không đo được", "")
    assert rep["min_font"] is None and rep["min_font_measured"] is False and any("không đo được" in i for i in rep["issues"])


def test_render_inline_only_text_is_measured():
    if not (NODE and Path(CHROME).exists()):
        print("bỏ qua test_render_inline_only_text_is_measured: thiếu node hoặc Chrome")
        return
    # Chữ chỉ nằm trong span inline: bản cũ không có hộp nào để đo nên ra null.
    r, rep = run_render('<div class="canvas" style="width:400px;height:200px"><span style="font-size:20px">Có schema</span></div>',
                        {"json_prompt": {"headline": "Có schema", "typography": {"min_text_height": "24px"}}})
    assert r.returncode == 0, r.stdout + r.stderr
    assert rep["min_font"] == 20 and rep["min_font_measured"] is True and not rep["issues"]


BODY = """<html><body><script>var x='schema không phải'</script>
<h2>Schema có giúp xếp hạng không</h2>
<p>Nghiên cứu năm 2024 trên 1.000 trang không thấy quan hệ giữa schema và thứ hạng. Schema giúp công cụ hiểu trang rõ hơn.</p>
<p>Tốc độ tải trang ảnh hưởng đến trải nghiệm người dùng.</p></body></html>"""


def spec(*labels):
    return {"id": "AI19", "json_prompt": {"headline": "Yếu tố xếp hạng", "elements": [{"label": " · ".join(labels)}]}}


def test_body_check_levels():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "bai.html")
        p.write_text(BODY, encoding="utf-8")
        rep, claims = dbc.check({"id": "AI19", "json_prompt": {"elements": [{"items": [
            "Tốc độ tải trang", "Có tốc độ", "Có quan hệ giữa schema và thứ hạng", "Kết luận 2025", "Cloudflare", "Mẫu 1.000 trang", "Mẫu 5.000 trang"]}]}}, p)
        lv = {r["text"]: r["level"] for r in rep["rows"]}
        assert lv["Tốc độ tải trang"] == "khop"
        assert lv["Cloudflare"] == "khong_thay"
        assert lv["Có quan hệ giữa schema và thứ hạng"] in ("nguoc", "can_doc")
        assert any("5.000" in e for e in rep["errors"])  # số không có trong thân bài
        assert not any("1.000" in e for e in rep["errors"])
        assert "var x" not in " ".join(dbc.sentences(dbc.body_text(p)))  # bỏ nội dung script
        assert is_neg("Không thấy quan hệ") and not is_neg("Không chỉ nhanh mà còn rẻ")


def is_neg(s):
    return dbc.is_negated(s)


def test_body_check_ai19_polarity_cli():
    """Ca thật AI19: sơ đồ ghi 'Có schema' là yếu tố thứ hạng, bài nói nghiên cứu không thấy quan hệ."""
    body = "<p>Nghiên cứu không thấy quan hệ giữa schema và thứ hạng.</p><p>Schema chỉ giúp công cụ hiểu trang.</p>"
    body_neg_only = "<p>Nghiên cứu không thấy quan hệ giữa schema và thứ hạng.</p>"
    with tempfile.TemporaryDirectory() as d:
        sp = Path(d, "specs.json")
        sp.write_text(json.dumps({"items": [{"id": "AI19", "json_prompt": {"elements": [{"items": ["Có schema"]}]}}]}), encoding="utf-8")
        b1, b2 = Path(d, "mixed.html"), Path(d, "neg.html")
        b1.write_text(body, encoding="utf-8")
        b2.write_text(body_neg_only, encoding="utf-8")
        cl = Path(d, "claims.jsonl")
        # Mọi câu về schema đều phủ định: lỗi, thoát 1. Có --claims nhưng không --write: không ghi file.
        rc = dbc.main(["--specs", str(sp), "--body", str(b2), "--claims", str(cl)])
        assert rc == 1 and not cl.exists()
        # Thân bài có cả câu khẳng định: cần đọc, không lỗi trừ khi --strict.
        assert dbc.main(["--specs", str(sp), "--body", str(b1)]) == 0
        assert dbc.main(["--specs", str(sp), "--body", str(b1), "--strict"]) == 1
        # --write ghi input cho Jev.
        dbc.main(["--specs", str(sp), "--body", str(b1), "--claims", str(cl), "--write"])
        row = json.loads(cl.read_text(encoding="utf-8").splitlines()[0])
        assert row["claim"] == "Có schema" and row["evidence"] and row["id"] == "AI19"
        # Lỗi tham số và file thiếu.
        assert dbc.main(["--specs", str(sp)]) == 2
        assert dbc.main(["--specs", str(sp), "--body", str(Path(d, "khong-co.html"))]) == 2


def test_body_check_verbatim_but_opposite():
    """Ca thật AI19 chạy lại trên thân bài thật (site gtvseo, 25/10): 'có schema' nằm nguyên văn trong câu kể tin đồn,
    nên bản đầu của script xếp 'khop' và thoát 0. Nay phải ra can_doc, câu phủ định đứng đầu bằng chứng."""
    body = ("<p>Sử dụng Schema Markup cho trang.</p>"
            "<p>Không có sự kết nối nào giữa việc có schema và ranking cao trong Google.</p>"
            "<p>Người ta đồn rằng khi bạn có schema thì bạn sẽ rank cao hơn.</p>"
            "<p>Tốc độ tải trang ảnh hưởng đến trải nghiệm.</p>")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "bai.html")
        p.write_text(body, encoding="utf-8")
        rep, claims = dbc.check({"id": "AI19", "json_prompt": {"elements": [{"label": "Có schema"}, {"label": "Tốc độ tải trang"}]}}, p)
        lv = {r["text"]: r["level"] for r in rep["rows"]}
        assert lv["Có schema"] == "can_doc", lv
        assert lv["Tốc độ tải trang"] == "khop"  # nguyên văn, không có câu ngược chiều
        ev = [c for c in claims if c["claim"] == "Có schema"][0]["evidence"]
        assert ev[0].startswith("Không có sự kết nối")


def test_help_flags():
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "diagram_body_check.py"), "--help"], capture_output=True, text=True)
    assert r.returncode == 0 and "--specs" in r.stdout
    if NODE:
        for f in ("diagram_render.mjs", "diagram_checks.mjs"):
            r = subprocess.run([NODE, str(SCRIPTS / f), "--help"], capture_output=True, text=True, timeout=30)
            assert r.returncode == 0 and "diagram" in r.stdout


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    if not NODE:
        print("thiếu node: bỏ qua test_min_font_logic, test_help_flags phần node")
        tests = [t for t in tests if t is not test_min_font_logic]
    for t in tests:
        t()
    print(f"OK {len(tests)} test")
