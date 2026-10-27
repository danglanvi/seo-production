#!/usr/bin/env python3
"""Dựng wp/doc-kit/doc-kit.css từ blog.css của format bài blog pages.dev.
Dùng: python3 build_kit.py <đường dẫn blog.css>
Font: bỏ Be Vietnam Pro và Source Serif của pages.dev, để thân bài nhận font của theme (GTV: Inter + Montserrat, TAG: Be Vietnam Pro)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from css_scope import scope  # noqa: E402

src = open(sys.argv[1], encoding='utf-8').read()
css = scope(src, drop_chrome=True)
css = re.sub(r'font-family:"Be Vietnam Pro"[^;}]*', 'font-family:inherit', css)
css = re.sub(r'font-family:"Source Serif 4"[^;}]*;?', '', css)
css = re.sub(r'\{;+', '{', css).replace(';;', ';')
css = re.sub(r'(^|\n)[^{}\n]+\{\s*\}', '', css)
head = ('/* doc-kit.css: sinh bằng scripts/build_kit.py từ _format/blog.css của site tài liệu GTV. Không sửa tay.\n'
        '   Áp trong <div class="doc-kit"> của bài có meta _doc_kit. */\n')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wp', 'doc-kit', 'doc-kit.css')
open(out, 'w', encoding='utf-8').write(head + css + '\n.doc-kit.doc-kit img{max-width:100%;height:auto}\n.doc-kit [hidden]{display:none}\n')
print(out, os.path.getsize(out), 'byte')
