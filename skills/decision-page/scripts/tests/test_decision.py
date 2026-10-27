#!/usr/bin/env python3
"""Test offline cho gen_decision.py và parse_answer.py.

Chạy từ thư mục skill: python3 -B scripts/tests/test_decision.py
Không gọi mạng, không gọi Artifact tool. Test Chrome dùng Chrome headless local
và tự bỏ qua (SKIP) khi máy không có Chrome.

Ca hỏng thật lấy từ đợt rà skill web 10/2026 (đề xuất coord-3, ops2-1):
- ghi chú mất khi bấm Chép hoặc khi nạp lại trang (v5 mất khoảng 6 phút);
- thẻ thiếu bối cảnh, thiếu rủi ro, thiếu cờ config sống (Lead "không hiểu ý");
- để trống ở thẻ chạm config sống hoặc việc xoá phải thành "chờ chọn rõ", không "làm".
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import gen_decision as g  # noqa: E402
import parse_answer as pa  # noqa: E402
import htmlcmp  # noqa: E402

FX = HERE / "fixtures"
MAU = FX / "cau-hoi_mau.json"
REAL = FX / "web-skill-review.json"
V2 = Path(__file__).resolve().parents[4] / "Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-skill-review_cho-anh-quyet_v2.html"
TMP = []


def tmpdir():
    d = tempfile.mkdtemp(prefix="dp-test-")
    TMP.append(d)
    return Path(d)


def run(mod, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue(), err.getvalue()


def mutated_spec(fn):
    raw = json.loads(MAU.read_text(encoding="utf-8"))
    fn(raw)
    d = tmpdir()
    p = d / "cau-hoi.json"
    p.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return p


def expect_spec_error(fn, needle):
    p = mutated_spec(fn)
    try:
        g.load_spec(p)
    except g.SpecError as e:
        assert any(needle in x for x in e.problems), "thiếu thông báo %r, có %r" % (needle, e.problems)
        rc, _, err = run(g, [str(p)])
        assert rc == 2, "mã thoát phải là 2, nhận %s" % rc
        return
    raise AssertionError("spec hỏng mà không bị từ chối: %s" % needle)


# ------------------------------------------------------------ schema

def t_mau_hop_le():
    spec = g.load_spec(MAU)
    assert len(spec["cards"]) == 4
    assert spec["cards"][3]["questions"][0]["name"] == "l1.rule"
    assert spec["cards"][0]["questions"][0]["name"] == "a1"


def t_the_thieu_context():
    expect_spec_error(lambda r: r["cards"][0].pop("context"), "thiếu context")


def t_the_thieu_risk():
    expect_spec_error(lambda r: r["cards"][0].pop("risk_if_skipped"), "thiếu risk_if_skipped")


def t_the_thieu_touches_live():
    expect_spec_error(lambda r: r["cards"][0].pop("touches_live"), "thiếu touches_live")


def t_khong_co_de_xuat():
    def f(r):
        for o in r["cards"][0]["questions"][0]["options"]:
            o["recommended"] = False
    expect_spec_error(f, "đúng 1 phương án recommended, đang có 0")


def t_hai_de_xuat():
    def f(r):
        for o in r["cards"][0]["questions"][0]["options"][:2]:
            o["recommended"] = True
    expect_spec_error(f, "đang có 2")


def t_id_trung_va_label_trung():
    expect_spec_error(lambda r: r["cards"][1].update(id="a1"), "id bị trùng")
    expect_spec_error(lambda r: r["cards"][1].update(label="A1"), "label 'A1' bị trùng")


def t_nhieu_cau_thieu_key():
    expect_spec_error(lambda r: r["cards"][3]["questions"][1].pop("key"), "mỗi câu cần key")


def t_anh_thieu_file():
    expect_spec_error(lambda r: r["cards"][0].update(images=[{"src": "img/khong-co.webp", "caption": "x"}]), "không thấy file img/khong-co.webp")


def t_json_hong():
    d = tmpdir()
    p = d / "hong.json"
    p.write_text('{"project": "x", ', encoding="utf-8")
    rc, _, err = run(g, [str(p)])
    assert rc == 2 and "JSON hỏng" in err


def t_anh_cuc_bo_khong_vao_artifact():
    d = tmpdir()
    (d / "a.webp").write_bytes(b"x")
    raw = json.loads(MAU.read_text(encoding="utf-8"))
    raw["cards"][0]["images"] = [{"src": "a.webp"}]
    (d / "s.json").write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    assert run(g, [str(d / "s.json")])[0] == 0
    rc, _, err = run(g, [str(d / "s.json"), "--artifact"])
    assert rc == 2 and "artifact" in err


# ------------------------------------------------------------ tên file, dry-run

def t_so_ban_tu_tang():
    d = tmpdir()
    for n in ("mau-thu_cho-anh-quyet_v1.html", "mau-thu_cho-anh-quyet_v3.html", "mau-thu_cho-anh-quyet_v7.html",
              "mau-thu_cho-anh-quyet_v8_artifact.html", "khac_cho-anh-quyet_v20.html", "mau-thu_cho-anh-quyet_v9.md"):
        (d / n).write_text("x")
    assert g.next_version(d, "mau-thu") == 9
    assert g.next_version(tmpdir(), "mau-thu") == 1


def t_dry_run_khong_ghi():
    d = tmpdir()
    rc, out, _ = run(g, [str(MAU), "--out", str(d)])
    assert rc == 0 and "DRY-RUN" in out
    assert list(d.iterdir()) == [], "dry-run đã ghi file"


def t_write_khong_ghi_de():
    d = tmpdir()
    assert run(g, [str(MAU), "--out", str(d), "--write"])[0] == 0
    assert (d / "mau-thu_cho-anh-quyet_v1.html").is_file()
    assert (d / "mau-thu_cho-anh-quyet_v1.cau-hoi.json").is_file()
    assert run(g, [str(MAU), "--out", str(d), "--write"])[0] == 0
    assert (d / "mau-thu_cho-anh-quyet_v2.html").is_file(), "lần hai phải ra v2"
    rc, _, err = run(g, [str(MAU), "--out", str(d), "--write", "--version", "1"])
    assert rc == 2 and "không ghi đè" in err
    side = json.loads((d / "mau-thu_cho-anh-quyet_v2.cau-hoi.json").read_text(encoding="utf-8"))
    assert side["version"] == 2


def t_both_cung_so_ban_va_readme():
    d = tmpdir()
    (d / "mau-thu_cho-anh-quyet_v4.html").write_text("x")
    assert run(g, [str(MAU), "--out", str(d), "--both", "--write"])[0] == 0
    for n in ("v5.html", "v5_artifact.html", "v5_khoi-phuc.md", "v5.cau-hoi.json"):
        assert (d / ("mau-thu_cho-anh-quyet_" + n)).is_file(), n
    assert "answers" in (d / "mau-thu_cho-anh-quyet_v5_khoi-phuc.md").read_text(encoding="utf-8")


def t_open_can_write():
    rc, _, err = run(g, [str(MAU), "--open"])
    assert rc == 2 and "--write" in err


PS_THUONG = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Helpers/Google Chrome Helper.app/Contents/MacOS/Google Chrome Helper --type=renderer\n"
PS_HEADLESS = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --headless=new --user-data-dir=/tmp/x --dump-dom file:///a.html\n/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Helpers/Google Chrome Helper.app/Contents/MacOS/Google Chrome Helper --type=gpu-process\n"


def t_kiem_cua_so_chrome_khong_headless():
    # coord-3: mở xong phải kiểm có Chrome thường, vì Chrome headless không hiện cửa sổ cho Lead
    assert g.chrome_window_state(PS_THUONG) == "co"
    assert g.chrome_window_state(PS_HEADLESS) == "chi-headless"
    assert g.chrome_window_state("/usr/sbin/cfprefsd agent\n") == "khong"
    assert g.chrome_window_state(None) is None


def t_open_chi_headless_thi_exit_5_va_in_file_url():
    class R:
        returncode = 0
    calls = []
    old_run, old_ps, old_sleep = g.subprocess.run, g._ps_text, g.time.sleep
    g.subprocess.run = lambda cmd, **kw: (calls.append(cmd), R())[1]
    g.time.sleep = lambda s: None
    try:
        g._ps_text = lambda: PS_HEADLESS
        d = tmpdir()
        rc, out, err = run(g, [str(MAU), "--out", str(d), "--write", "--open"])
        assert rc == 5 and "headless" in err and "file:///" in out, (rc, err)
        assert calls and calls[0][:3] == ["open", "-a", "Google Chrome"], calls
        g._ps_text = lambda: PS_THUONG
        rc, out, err = run(g, [str(MAU), "--out", str(d), "--write", "--open"])
        assert rc == 0 and "Mở Chrome:" in out, (rc, err)
    finally:
        g.subprocess.run, g._ps_text, g.time.sleep = old_run, old_ps, old_sleep


def t_help_hai_script():
    for mod in (g, pa):
        try:
            run(mod, ["--help"])
        except SystemExit as e:
            assert e.code == 0
        else:
            raise AssertionError("--help phải thoát")


# ------------------------------------------------------------ nội dung trang

def t_escape_va_link_doc():
    def f(r):
        r["title"] = "<script>alert(1)</script> tiêu đề"
        r["cards"][0]["context"] = ["[bấm](javascript:alert(1)) và [ok](https://example.com/x)", "<img src=x onerror=alert(1)>"]
    p = mutated_spec(f)
    spec = g.load_spec(p)
    h = g.build_html(spec, 1, tmpdir())
    assert "<script>alert(1)" not in h and "&lt;script&gt;alert(1)" in h
    assert "<img src=x" not in h and "&lt;img" in h
    assert "javascript:alert" not in h.split("<script>")[0]
    assert 'href="https://example.com/x"' in h


def t_quet_du_lieu_nhay_cam():
    for text in ("Server 203.0.113.45 đang chạy", "password: Abc12345xyz", "key sk-abcdefghijklmnopqrstuv"):
        p = mutated_spec(lambda r, t=text: r["cards"][0].update(context=[t]))
        rc, _, err = run(g, [str(p)])
        assert rc == 4, (text, rc)
        assert run(g, [str(p), "--allow-sensitive"])[0] == 0
    d = tmpdir()
    (d / "deny.txt").write_text("# mẫu riêng\nmay-chu-thu-nghiem\n", encoding="utf-8")
    p = mutated_spec(lambda r: r["cards"][0].update(context=["Thử trên may-chu-thu-nghiem tối qua"]))
    assert run(g, [str(p), "--deny-file", str(d / "deny.txt")])[0] == 4
    assert run(g, [str(p)])[0] == 0


def t_cau_truc_trang():
    spec = g.load_spec(MAU)
    loc = g.build_html(spec, 1, tmpdir())
    art = g.build_html(spec, 1, tmpdir(), artifact=True)
    assert loc.startswith("<!doctype html>") and "</body>" in loc
    assert art.startswith("<title>") and not re.search(r"<(html|body|head)[\s>]", art)
    for h in (loc, art):
        assert ":root{" in h and "prefers-color-scheme:dark" in h and 'data-theme="dark"' in h
        assert "padding-left:max(16px" in h and "overflow-x:auto" in h
    assert "claude.use('db')" in art and '"collection": "answers"' in art and "Lưu, tôi trả lời xong" in art
    assert "Lưu, tôi trả lời xong" not in loc and '"db": null' in loc
    ex = htmlcmp.extract(loc)
    assert [c["id"] for c in ex["cards"]] == ["a1", "i1", "d1", "l1"]
    for c in ex["cards"]:
        recs = [o for o in c["opts"] if o[1]]
        nq = len(c["q"])
        assert len(recs) == nq, "mỗi câu đúng một ô đề xuất: %s" % c["id"]
    assert loc.count('data-hold="1"') == 3, "xoá và config sống phải đánh dấu hold"
    assert loc.count("Phải chọn") == 2, "thẻ d1 và l1 có nhãn Phải chọn"
    toc = loc.split('id="toc"')[1].split("</nav>")[0]
    assert "Số liệu" not in toc and "Dựng skill" in toc


def t_ghi_chu_the_thong_tin_co_o():
    spec = g.load_spec(MAU)
    loc = g.build_html(spec, 1, tmpdir())
    assert 'data-note="i1"' in loc, "thẻ info có note: true phải có ô ghi chú"
    spec["cards"][1]["note"] = False
    assert 'data-note="i1"' not in g.build_html(spec, 1, tmpdir())


# ------------------------------------------------------------ Chrome headless

def chrome_or_skip(fn):
    def wrapper():
        if not g.find_chrome():
            print("      SKIP: không có Chrome")
            return
        fn()
    wrapper.__name__ = fn.__name__
    return wrapper


@chrome_or_skip
def t_chrome_trang_tot_dat():
    spec = g.load_spec(MAU)
    d = tmpdir()
    loc = g.build_html(spec, 1, d)
    art = g.build_html(spec, 1, d, artifact=True)
    errs, missing = g.chrome_test(spec, 1, loc, art)
    assert not missing and errs == [], errs


@chrome_or_skip
def t_chrome_bat_mat_ghi_chu_khi_chep():
    spec = g.load_spec(MAU)
    d = tmpdir()
    loc = g.build_html(spec, 1, d)
    needle = "if(n&&n.value.trim())parts.push('Ghi chú: '+n.value.trim());"
    assert needle in loc
    errs, _ = g.chrome_test(spec, 1, loc.replace(needle, ""))
    assert any("nội dung clip khác dữ liệu" in e for e in errs), errs


@chrome_or_skip
def t_chrome_bat_mat_ghi_chu_khi_nap_lai():
    spec = g.load_spec(MAU)
    loc = g.build_html(spec, 1, tmpdir())
    needle = "document.querySelectorAll('textarea[data-note]').forEach(t=>{t.value=st.notes[t.dataset.note]||''});"
    assert needle in loc
    errs, _ = g.chrome_test(spec, 1, loc.replace(needle, ""))
    assert any("khôi phục" in e for e in errs), errs


@chrome_or_skip
def t_chrome_bat_khong_luu_local_storage():
    spec = g.load_spec(MAU)
    loc = g.build_html(spec, 1, tmpdir())
    needle = "try{localStorage.setItem(CFG.key,JSON.stringify(st))}catch(e){}"
    assert needle in loc
    errs, _ = g.chrome_test(spec, 1, loc.replace(needle, ""))
    assert any("localStorage" in e for e in errs), errs


@chrome_or_skip
def t_chrome_bat_db_mat_ghi_chu():
    spec = g.load_spec(MAU)
    d = tmpdir()
    loc = g.build_html(spec, 1, d)
    art = g.build_html(spec, 1, d, artifact=True)
    needle = "choices:st.choices,notes:st.notes,"
    assert needle in art
    errs, _ = g.chrome_test(spec, 1, loc, art.replace(needle, "choices:st.choices,"))
    assert any("artifact/lưu" in e for e in errs), errs


@chrome_or_skip
def t_chrome_cli_exit_3_khi_hong():
    # --chrome-test qua CLI phải thoát 0 với trang tốt
    d = tmpdir()
    rc, out, err = run(g, [str(MAU), "--out", str(d), "--both", "--chrome-test"])
    assert rc == 0 and "Chrome test: đạt" in out, (rc, out, err)


# ------------------------------------------------------------ parse_answer

def spec_real():
    return g.load_spec(REAL, check_files=False)


def t_parse_text_v2_roundtrip():
    spec = spec_real()
    ans = pa.from_text(str(FX / "tra-loi-v2_mau.txt"), spec)
    db = json.loads((FX / "tra-loi-db_mau.json").read_text(encoding="utf-8"))["data"]
    assert ans["choices"] == db["choices"], (ans["choices"], db["choices"])
    assert ans["notes"] == db["notes"], (ans["notes"], db["notes"])
    assert ans["notes"]["s2"] == "Làm xong s1 trước, s2 sau.\nKhông đụng memory khác."


def t_dinh_dang_chep_khong_troi():
    spec = spec_real()
    db = json.loads((FX / "tra-loi-db_mau.json").read_text(encoding="utf-8"))["data"]
    want = g.expected_copy_text(spec, 2, db["choices"], db["notes"])
    assert want == (FX / "tra-loi-v2_mau.txt").read_text(encoding="utf-8").rstrip("\n")
    assert want == db["text"]


def t_parse_db_cac_lop_boc():
    spec = spec_real()
    data = json.loads((FX / "tra-loi-db_mau.json").read_text(encoding="utf-8"))["data"]
    d = tmpdir()
    for i, shape in enumerate((data, {"data": data}, {"doc": {"doc_id": "lead", "data": data}}, [{"data": data}])):
        p = d / ("db%d.json" % i)
        p.write_text(json.dumps(shape, ensure_ascii=False), encoding="utf-8")
        a = pa.from_db(str(p))
        assert a["choices"] == data["choices"] and a["done"] is True, i


def t_trong_theo_de_xuat_tru_config_song():
    spec = spec_real()
    ans = pa.from_text(str(FX / "tra-loi-v2_mau.txt"), spec)
    items, problems = pa.resolve(spec, ans)
    by = {i["card"]: i for i in items}
    assert problems == []
    assert by["s4"]["source"] == "default" and by["s4"]["value"].startswith("Dựng skill riêng wp-ui-fix")
    assert by["s1"]["source"] == "chosen"
    assert by["l1"]["source"] == "hold" and by["l1"]["reason"] == "config sống", "để trống ở config sống phải chờ chọn rõ"
    assert by["l4"]["source"] == "hold"
    assert by["l2"]["source"] == "chosen", "chọn rõ config sống thì làm"
    assert by["b1"]["source"] == "default"


def t_cau_tra_loi_cu_dong_nghia_trong():
    spec = spec_real()
    d = tmpdir()
    t = ("Trả lời trang Duyệt skill web site-mau (artifact, bản 2):\n"
         "Luật 1 — Hook chặn hộp duyệt: (để trống, theo đề xuất)\n")
    p = d / "t.txt"
    p.write_text(t, encoding="utf-8")
    items, _ = pa.resolve(spec, pa.from_text(str(p), spec))
    assert items[0]["source"] == "hold" or [i for i in items if i["card"] == "l1"][0]["source"] == "hold"


def t_chu_dan_bi_cat_thi_the_vang_dong_khong_lam():
    # Nút Chép luôn in mọi thẻ có câu hỏi. Chữ dán thiếu dòng của một thẻ là chữ bị cắt, không phải để trống.
    spec = spec_real()
    d = tmpdir()
    p = d / "cat.txt"
    p.write_text("Trả lời:\nSkill 2 — Skill artifact-account-migration: (để trống, theo đề xuất)\n", encoding="utf-8")
    items, problems = pa.resolve(spec, pa.from_text(str(p), spec))
    by = {i["card"]: i for i in items}
    assert by["s2"]["source"] == "default"
    assert by["s4"]["source"] == "hold" and by["s4"]["reason"] == "thiếu dòng trong chữ dán", by["s4"]
    assert not [i for i in items if i["source"] == "default" and i["card"] != "s2"], "thẻ vắng dòng không được tính theo đề xuất"
    assert any("Skill 4" in x for x in problems)
    rc, out, _ = run(pa, ["--spec", str(REAL), "--text", str(p)])
    assert rc == 3 and "thiếu dòng trong chữ dán" not in out.split("## Làm")[1].split("##")[0], out


def t_de_xuat_la_xoa_thi_hold():
    spec = g.load_spec(MAU)
    d = tmpdir()
    p = d / "t.txt"
    p.write_text("Trả lời:\nD1 — Xoá file nháp?: (để trống, chưa làm)\n", encoding="utf-8")
    items, _ = pa.resolve(spec, pa.from_text(str(p), spec))
    d1 = [i for i in items if i["card"] == "d1"][0]
    assert d1["source"] == "hold" and "xoá" in d1["reason"]
    p.write_text("Trả lời:\nD1 — Xoá file nháp?: Xoá 12 file\n", encoding="utf-8")
    items, _ = pa.resolve(spec, pa.from_text(str(p), spec))
    assert [i for i in items if i["card"] == "d1"][0]["source"] == "chosen", "chọn rõ việc xoá thì làm"


def t_gia_tri_la_va_ten_la():
    spec = spec_real()
    d = tmpdir()
    p = d / "x.json"
    p.write_text(json.dumps({"choices": {"s1": "Dựng cho vui", "khong-co": "x"}, "notes": {"zzz": "y"}, "done": True}), encoding="utf-8")
    sp = REAL
    rc, out, err = run(pa, ["--spec", str(sp), "--db", str(p)])
    assert rc == 3, rc
    assert "không khớp phương án" in out and "khong-co" in out and "zzz" in out


def t_text_khong_nhan_ra_dong_nao():
    d = tmpdir()
    p = d / "r.txt"
    p.write_text("xin chào, tôi chọn ok hết\n", encoding="utf-8")
    rc, _, err = run(pa, ["--spec", str(REAL), "--text", str(p)])
    assert rc == 2 and "không nhận ra" in err


def t_text_thieu_cau_trong_the():
    d = tmpdir()
    p = d / "r.txt"
    p.write_text("Trả lời:\nSkill 1 — câu khác hẳn: abc\n", encoding="utf-8")
    rc, _, err = run(pa, ["--spec", str(REAL), "--text", str(p)])
    assert rc == 2 and "không thấy câu" in err


def t_gia_tri_chua_dau_cham_phay_va_hai_cham():
    spec = g.load_spec(MAU)
    spec["cards"][0]["questions"][0]["options"][1]["value"] = "Làm A; rồi B: xong"
    ch = {"a1": "Làm A; rồi B: xong"}
    no = {"a1": "ghi chú; thêm Ghi chú: giả"}
    d = tmpdir()
    p = d / "t.txt"
    p.write_text(g.expected_copy_text(spec, 1, ch, no) + "\n", encoding="utf-8")
    a = pa.from_text(str(p), spec)
    assert a["choices"] == ch and a["notes"] == no, (a["choices"], a["notes"])


def t_done_va_require_done():
    d = tmpdir()
    p = d / "x.json"
    p.write_text(json.dumps({"choices": {}, "notes": {}, "done": False}), encoding="utf-8")
    rc, out, _ = run(pa, ["--spec", str(REAL), "--db", str(p)])
    assert rc == 0 and "chưa bấm" in out
    rc, _, err = run(pa, ["--spec", str(REAL), "--db", str(p), "--require-done"])
    assert rc == 4


def t_json_dau_ra():
    rc, out, _ = run(pa, ["--spec", str(REAL), "--text", str(FX / "tra-loi-v2_mau.txt"), "--json"])
    data = json.loads(out)
    assert rc == 0 and data["items"][0]["source"] == "chosen"
    assert sum(1 for i in data["items"] if i["source"] == "hold") == 2


def t_into_dry_run_va_idempotent():
    d = tmpdir()
    f = d / "HANDOFF.md"
    f.write_text("# HANDOFF\n\n## Bước tiếp\n\n1. Làm việc.\n", encoding="utf-8")
    base = ["--spec", str(REAL), "--text", str(FX / "tra-loi-v2_mau.txt"), "--version", "2", "--into", str(f)]
    before = f.read_text(encoding="utf-8")
    rc, _, err = run(pa, base)
    assert rc == 0 and "DRY-RUN" in err and f.read_text(encoding="utf-8") == before
    assert run(pa, base + ["--write"])[0] == 0
    once = f.read_text(encoding="utf-8")
    assert once.count("## Quyết định:") == 1 and "decision-page:web-skill-review:v2" in once and "## Bước tiếp" in once
    assert run(pa, base + ["--write"])[0] == 0
    twice = f.read_text(encoding="utf-8")
    assert twice.count("## Quyết định:") == 1, "ghi lần hai phải thay, không nhân đôi"
    f.write_text(twice + "\n## Bẫy đã gặp\n\n- zsh.\n", encoding="utf-8")
    assert run(pa, base + ["--write"])[0] == 0
    third = f.read_text(encoding="utf-8")
    assert third.count("## Quyết định:") == 1 and "## Bẫy đã gặp" in third


def t_write_can_into():
    rc, _, err = run(pa, ["--spec", str(REAL), "--text", str(FX / "tra-loi-v2_mau.txt"), "--write"])
    assert rc == 2 and "--into" in err


def t_sidecar_dung_lam_spec():
    d = tmpdir()
    assert run(g, [str(MAU), "--out", str(d), "--write"])[0] == 0
    side = d / "mau-thu_cho-anh-quyet_v1.cau-hoi.json"
    ch, no = g.sample_selection(g.load_spec(MAU))
    t = d / "t.txt"
    t.write_text(g.expected_copy_text(g.load_spec(MAU), 1, ch, no) + "\n", encoding="utf-8")
    rc, out, _ = run(pa, ["--spec", str(side), "--text", str(t)])
    assert rc == 0 and "(bản 1)" in out


# ------------------------------------------------------------ ca thật: đợt rà skill web

def t_ca_that_dung_lai_trang_tu_json():
    d = tmpdir()
    rc, out, err = run(g, [str(REAL), "--out", str(d), "--both", "--write", "--version", "2"])
    assert rc == 0, err
    assert (d / "web-skill-review_cho-anh-quyet_v2.html").is_file()
    spec = g.load_spec(REAL)
    assert len(spec["cards"]) == 12 and sum(len(c["questions"]) for c in spec["cards"]) == 10
    if not V2.is_file():
        print("      SKIP so với v2: không có %s" % V2.name)
        return
    mine = htmlcmp.extract((d / "web-skill-review_cho-anh-quyet_v2.html").read_text(encoding="utf-8"))
    want = htmlcmp.extract(V2.read_text(encoding="utf-8"))
    diff = htmlcmp.diff(want, mine)
    assert diff == [], "\n".join(diff)
    art = htmlcmp.extract((d / "web-skill-review_cho-anh-quyet_v2_artifact.html").read_text(encoding="utf-8"))
    assert htmlcmp.diff(want, art) == []
    art_text = (d / "web-skill-review_cho-anh-quyet_v2_artifact.html").read_text(encoding="utf-8")
    assert '"collection": "answers"' in art_text and '"doc": "lead"' in art_text


@chrome_or_skip
def t_ca_that_chrome():
    spec = g.load_spec(REAL)
    d = tmpdir()
    loc = g.build_html(spec, 2, d)
    art = g.build_html(spec, 2, d, artifact=True)
    errs, missing = g.chrome_test(spec, 2, loc, art)
    assert not missing and errs == [], errs


def t_ca_that_khong_lo_du_lieu_nhay_cam():
    spec = g.load_spec(REAL)
    h = g.build_html(spec, 2, tmpdir(), artifact=True)
    assert g.scan_sensitive(h) == []


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]


def main():
    fails = 0
    for fn in TESTS:
        try:
            fn()
            print("PASS  %s" % fn.__name__)
        except Exception:
            fails += 1
            print("FAIL  %s" % fn.__name__)
            traceback.print_exc()
    for d in TMP:
        shutil.rmtree(d, ignore_errors=True)
    print("\n%d test, %d lỗi" % (len(TESTS), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
