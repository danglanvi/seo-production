#!/usr/bin/env python3
"""Gắn tiền tố .doc-kit cho CSS của format bài blog (pages.dev) để chỉ áp vào thân bài trên WordPress.

Dùng: python3 css_scope.py <file.css> [--drop-chrome] > out.css
- :root, html, body, main -> .doc-kit ; * -> .doc-kit * ; selector khác -> .doc-kit.doc-kit <selector> (đủ mạnh hơn CSS bài viết của theme).
- --drop-chrome: bỏ luật của phần khung trang pages.dev không đưa lên WordPress (.nav, footer.ft, .hd, .eyebrow, .date, h1)
  và bỏ background, font-size gốc của body để thân bài theo nền và cỡ chữ của theme.
Thư viện: chỉ Python stdlib."""
import re
import sys

ROOTS = {':root', 'html', 'body', 'main'}
CHROME = re.compile(r'(^|[\s>+~,])(\.nav|footer\.ft|\.ft|\.hd|\.eyebrow|\.date|h1)(?![\w-])')


def split_rules(css):
    """Trả danh sách (prelude, body) ở cấp ngoài cùng; body của @media giữ nguyên chuỗi để xử lý đệ quy."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        prelude = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
            k += 1
        out.append((prelude, css[j + 1:k - 1]))
        i = k
    return out


def scope_selector(sel, drop_chrome):
    parts = []
    for s in sel.split(','):
        s = s.strip()
        if not s:
            continue
        if drop_chrome and CHROME.search(' ' + s):
            continue
        if s in ROOTS:
            parts.append('.doc-kit')
        elif s == '*':
            parts.append('.doc-kit *')
        else:
            parts.append('.doc-kit.doc-kit ' + re.sub(r'^(html|body|main)\s+', '', s))
    return ','.join(dict.fromkeys(parts))


def scope(css, drop_chrome=False):
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    out = []
    for prelude, body in split_rules(css):
        if prelude.startswith('@media') or prelude.startswith('@supports'):
            inner = scope(body, drop_chrome)
            if inner.strip():
                out.append(f'{prelude}{{{inner}}}')
        elif prelude.startswith('@'):
            out.append(f'{prelude}{{{body}}}')
        else:
            sel = scope_selector(prelude, drop_chrome)
            if not sel:
                continue
            if drop_chrome and prelude.strip() in ('body', 'main'):
                body = re.sub(r'(^|;)\s*(background|font-size|margin|padding)\s*:[^;]*', r'\1', body)
            out.append(f'{sel}{{{body.strip()}}}')
    return '\n'.join(out)


if __name__ == '__main__':
    sys.stdout.write(scope(open(sys.argv[1], encoding='utf-8').read(), '--drop-chrome' in sys.argv) + '\n')
