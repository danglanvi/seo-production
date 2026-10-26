#!/usr/bin/env python3
"""Test offline cho competitor_titles.py (không gọi mạng). Chạy: python3 -B -I tests/test_competitor_titles.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import competitor_titles as ct  # noqa: E402

page = ('<html lang="vi-VN"><head><meta name="robots" content="index, follow"><title>Link là gì? | Đối Thủ</title>'
        '</head><body><nav><h1>Menu</h1></nav><h1 class="t">Link <span>là gì</span>?\n Các loại link</h1><h1>H1 thứ hai</h1>')
r = ct.parse(page)
assert r == {"title": "Link là gì? | Đối Thủ", "h1": "Menu", "lang": "vi-VN", "robots": "index, follow"}, r
# H1 đầu tiên trong thân trang có thẻ con và xuống dòng
r = ct.parse("<title>T</title><h1>Link <b>là gì</b>?\n Các loại</h1>")
assert r["h1"] == "Link là gì? Các loại", r
# HTML hỏng: giữ phần đã đọc
assert ct.parse("<title>Chỉ có title")["title"] in ("", "Chỉ có title")
xml = "<urlset><url><loc> https://a.vn/x/?a=1&amp;b=2 </loc></url><url><loc>https://a.vn/y/</loc></url></urlset>"
assert ct.locs(xml) == ["https://a.vn/x/?a=1&b=2", "https://a.vn/y/"]
print("test_competitor_titles: đạt")
