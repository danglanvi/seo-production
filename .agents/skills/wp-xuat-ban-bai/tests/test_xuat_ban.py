"""Test offline: md_to_html.py, kiem_bai.py (không --online), phần đọc profile và thẻ meta của wp_publish.py.
Chạy từ skills/wp-xuat-ban-bai/: python3 -B tests/test_xuat_ban.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
FIX = HERE / "fixtures"
PROFILE = FIX / "00-context" / "web-profile.json"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE.parents[1] / "wp-dang-bai" / "scripts"))
import md_to_html  # noqa: E402


def build():
    prof = json.loads(PROFILE.read_text(encoding="utf-8"))
    return md_to_html.build(str(FIX / "bai-mau.md"), prof)


def kiem(html_text):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "bai.html")
        p.write_text(html_text, encoding="utf-8")
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "kiem_bai.py"), str(p), "--profile", str(PROFILE)],
                           capture_output=True, text=True)
    return r.returncode, r.stdout


def test_md_to_html():
    slug, page, info = build()
    assert slug == "lap-lich-tuoi-cay"
    assert '<header class="hd">' in page and page.count("<h1>") == 1
    assert '<meta name="slug" content="lap-lich-tuoi-cay">' in page
    assert '<meta name="keyword" content="lập lịch tưới cây">' in page
    assert "<title>Lập lịch tưới cây là gì? Cách lập lịch cho vườn nhỏ</title>" in page
    # link ra ngoài thành số chú thích, link nội bộ giữ nguyên
    assert 'href="https://khuyennong.example.org' not in page.split('<section class="notes')[0]
    assert '<sup class="fn"><a href="#nguon-1"' in page and 'id="nguon-1"' in page
    assert 'href="/chon-dat-trong/"' in page
    assert info["cho_media"] == ["IMG-01"] and 'class="wide cho-media" data-img="IMG-01"' in page
    assert '<p class="chu-ky">' in page and '<p class="lead">' in page
    assert '<div class="tbl wide"><table>' in page
    # đoạn lặp meta description và phần báo cáo không vào thân bài
    assert "Image placeholders" not in page and page.count("Bài hướng dẫn cách lập lịch cho vườn nhỏ trong 4 bước") == 1


def test_kiem_bai_chan_khung_cho():
    _, page, _ = build()
    rc, out = kiem(page)
    assert rc == 1 and "giữ chỗ" in out
    page = page.replace('<figure class="wide cho-media" data-img="IMG-01"><figcaption>[Chờ media IMG-01]</figcaption></figure>',
                        '<figure class="wide"><img src="a.webp" alt="Bốn bước lập lịch" width="10" height="10"></figure>')
    rc, out = kiem(page)
    assert rc == 0, out


def test_kiem_bai_luat():
    _, page, _ = build()
    page = page.replace('<figure class="wide cho-media" data-img="IMG-01"><figcaption>[Chờ media IMG-01]</figcaption></figure>', '')
    bad = page.replace("</main>",
                       '<p>Vườn Khác cũng làm vậy. <a href="https://ngoai.example.net/x">nguồn</a> Hoàn 100% tiền.</p>'
                       '<div class="calc"><input type="range" data-i="a"><b data-f="alert(a)">0</b></div>'
                       '<div class="bchk"><label><input type="checkbox"></label></div>'
                       '<button type="button" data-embed="tpl-x" data-src="https://evil.example.net/x">Xem</button>'
                       '<script>alert(1)</script></main>')
    rc, out = kiem(bad)
    assert rc == 1
    for s in ("brand bên kia", "link ra ngoài https://ngoai.example.net/x", "cam kết hoàn tiền", "công thức .calc",
              "thiếu data-key", "<script>", 'không có phần tử id="tpl-x"', "không phải link Google"):
        assert s in out, s
    no_sig = page.replace("Vườn Mẫu - Vườn nhỏ cho nhà phố", "")
    rc, out = kiem(no_sig)
    assert rc == 1 and "thiếu chữ ký" in out


def test_wp_publish_profile_va_meta():
    import wp_publish
    _, page, _ = build()
    title, desc, body, css, hm = wp_publish.extract(page)
    assert title.startswith("Lập lịch tưới cây là gì?") and "<h1" not in body
    assert hm["slug"] == "lap-lich-tuoi-cay" and hm["keyword"] == "lập lịch tưới cây"
    cwd = os.getcwd()
    try:
        os.chdir(FIX)
        assert wp_publish.load_profile("mau")["url"] == "https://vuon-mau.example.com"
        assert wp_publish.load_profile("khac") == {}
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    test_md_to_html()
    test_kiem_bai_chan_khung_cho()
    test_kiem_bai_luat()
    test_wp_publish_profile_va_meta()
    print("OK 4 test")
