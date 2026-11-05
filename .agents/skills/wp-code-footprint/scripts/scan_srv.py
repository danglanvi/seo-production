#!/usr/bin/env python3
"""Quét tất định mu-plugins + theme đã chép về: comment tiếng Việt, hook, ob_start, inline printer, trùng mục đích.
Chạy: python3 -I scan_srv.py <srv_dir> <out_dir>
Ra: scan_srv.json, scan_srv.md, emb_plugins.jsonl, jev_plugin_comments.jsonl
"""
import json
import os, re
import sys
from collections import Counter
from pathlib import Path
EXTRA_RE = "".join("|" + t for t in os.environ.get("FOOTPRINT_EXTRA", "").split("|") if t)  # token riêng của site, ví dụ "Tên|lane-x"

VI = re.compile(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵĂÂĐÊÔƠƯ]")
HOOK = re.compile(r"add_(action|filter)\(\s*['\"]([^'\"]+)['\"]")
FUNC = re.compile(r"function\s+([a-zA-Z0-9_]+)\s*\(")
PRIO = re.compile(r"add_(?:action|filter)\(\s*['\"]([^'\"]+)['\"]\s*,\s*[^,]+,\s*(-?\d+)")
RISK = {
    "ob_start": "ghi đè HTML lúc chạy (output buffer)",
    "MutationObserver": "vá DOM sau khi tải bằng JS",
    "setTimeout": "chờ bằng timer",
    "preg_replace": "sửa HTML bằng regex",
    "str_replace": "sửa HTML bằng thay chuỗi",
    "DOMDocument": "parse HTML server",
    "wp_footer": "in vào footer",
    "wp_head": "in vào head",
    "template_redirect": "chặn template",
    "the_content": "lọc nội dung bài",
    "elementor": "chạm Elementor",
    "litespeed": "chạm LiteSpeed",
    "remove_action": "gỡ hook theme/plugin",
    "!important": "CSS !important",
    "error_log": "ghi log",
    "file_put_contents": "ghi file",
    "shell_exec": "gọi shell",
    "exec(": "gọi shell",
    "curl_": "gọi HTTP",
    "wp_remote": "gọi HTTP",
}


def head_comment(src: str) -> str:
    m = re.match(r"\s*<\?php\s*/\*\*?([\s\S]*?)\*/", src)
    return " ".join(m.group(1).split())[:600] if m else ""


def comments(src: str):
    res = []
    for m in re.finditer(r"/\*[\s\S]*?\*/", src):
        res.append(("block", m.group(0), src[: m.start()].count("\n") + 1))
    for m in re.finditer(r"(?m)^[ \t]*(//|#)[^\n]*", src):
        res.append(("line", m.group(0), src[: m.start()].count("\n") + 1))
    return res


def scan(p: Path, root: Path):
    src = p.read_text(encoding="utf-8", errors="replace")
    rel = str(p.relative_to(root))
    cm = comments(src)
    vi_cm = [(k, " ".join(t.split())[:300], ln) for k, t, ln in cm if VI.search(t)]
    hooks = Counter(h for _, h in HOOK.findall(src))
    funcs = FUNC.findall(src)
    risks = {k: src.count(k) for k in RISK if k in src}
    inline_js = len(re.findall(r"<script\b", src))
    inline_css = len(re.findall(r"<style\b", src))
    prios = PRIO.findall(src)
    return {
        "file": rel,
        "bytes": len(src.encode()),
        "lines": src.count("\n") + 1,
        "head": head_comment(src),
        "hooks": dict(hooks),
        "hook_prios": prios[:30],
        "funcs": funcs[:60],
        "func_prefixes": Counter(f.split("_")[0] + "_" + f.split("_")[1] if f.count("_") >= 1 else f for f in funcs).most_common(5),
        "risks": risks,
        "script_tags": inline_js,
        "style_tags": inline_css,
        "comment_total": len(cm),
        "comment_vi": len(vi_cm),
        "comment_vi_lines": vi_cm,
        "mentions_session": bool(re.search(r"(phiên|lane|HANDOFF|đợt|lô \d|staging" + EXTRA_RE + ")", src)),
        "session_words": sorted(set(re.findall(r"(phiên \w+|lane \w+|HANDOFF|đợt \d|lô \d+|staging" + EXTRA_RE + ")", src)))[:15],
    }


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for d in ("mu-plugins", "theme"):
        for p in sorted((root / d).rglob("*")):
            if p.is_file() and p.suffix in (".php", ".js", ".css"):
                rows.append(scan(p, root))
    (out / "scan_srv.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    mu = [r for r in rows if r["file"].startswith("mu-plugins/") and r["file"].endswith(".php") and r["file"].count("/") == 1]
    with (out / "emb_plugins.jsonl").open("w", encoding="utf-8") as fh:
        for r in mu:
            txt = f"{Path(r['file']).stem}. {r['head']} Hooks: {', '.join(r['hooks'])}. Functions: {', '.join(r['funcs'][:25])}."
            fh.write(json.dumps({"id": r["file"], "text": txt}, ensure_ascii=False) + "\n")
    with (out / "jev_plugin_comments.jsonl").open("w", encoding="utf-8") as fh:
        for r in mu:
            for k, t, ln in r["comment_vi_lines"]:
                fh.write(json.dumps({"id": f"{r['file']}:{ln}", "state": {"file": r["file"], "line": ln, "comment": t}}, ensure_ascii=False) + "\n")
    lines = ["# Quét tất định mu-plugins (05/11/2026)", "", f"Tổng: {len(mu)} mu-plugin .php, {sum(r['bytes'] for r in mu)//1024} KB, {sum(r['lines'] for r in mu)} dòng, {sum(r['comment_vi'] for r in mu)} dòng comment tiếng Việt.", "", "| File | KB | dòng | comment VI | hook chính | rủi ro | script/style in ra | nhắc phiên/lane |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(mu, key=lambda x: -x["bytes"]):
        hooks = ", ".join(f"{k}×{v}" for k, v in sorted(r["hooks"].items(), key=lambda kv: -kv[1])[:4])
        risks = ", ".join(f"{k}×{v}" for k, v in r["risks"].items() if k in ("ob_start", "MutationObserver", "preg_replace", "DOMDocument", "remove_action", "!important"))
        lines.append(f"| {r['file'].split('/')[-1]} | {r['bytes']//1024} | {r['lines']} | {r['comment_vi']} | {hooks} | {risks} | {r['script_tags']}/{r['style_tags']} | {', '.join(r['session_words'][:4])} |")
    lines.append("")
    lines.append("## Theme: file có comment tiếng Việt hoặc nhắc phiên/lane")
    for r in rows:
        if r["file"].startswith("theme/") and (r["comment_vi"] or r["mentions_session"]):
            lines.append(f"- {r['file']}: {r['comment_vi']} comment VI; {', '.join(r['session_words'][:5])}")
    (out / "scan_srv.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"files={len(rows)} mu={len(mu)}")


if __name__ == "__main__":
    main()
