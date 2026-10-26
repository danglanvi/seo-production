"""Hàm dùng chung cho chain_check.py, pick_target.py và build_tax_plan.py: chuẩn hoá đường dẫn, khớp rule redirect, đọc dump bài.
Không chạy trực tiếp. Chỉ cần thư viện chuẩn.
"""
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

NHAP = {"draft", "pending", "private", "future", "auto-draft"}


def norm(u):
    """URL hoặc đường dẫn → '/a/b' (không host, query, dấu / cuối). WordPress lưu slug emoji dạng %f0%9f..., nên giải mã trước khi so."""
    s = unicodedata.normalize("NFC", unquote(urlsplit(str(u or "").strip()).path)).casefold()
    return "/" + "/".join(x for x in s.split("/") if x)


def host_of(u):
    return urlsplit(str(u or "")).netloc.casefold()


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def load_dump(p):
    """Dump của export_urls.php: danh sách hoặc {"posts": [...]}. Thêm khoá `keys` = các đường dẫn đã chuẩn hoá của bài."""
    d = load_json(p)
    rows = d["posts"] if isinstance(d, dict) else d
    for r in rows:
        r["keys"] = {norm(x) for x in (r.get("path"), r.get("pm_uri")) if x}
        r["slug_n"] = norm(r.get("name") or "").strip("/")
        r["old_n"] = {norm(x).strip("/") for x in r.get("old_slugs") or []}
    return rows


class Rule:
    def __init__(self, raw, origin="co", seq=0):
        self.id = str(raw.get("id", f"moi-{seq}"))
        # "pattern" không kèm "sources" là redirect trong plan.json của build_tax_plan.py: regex kiểu Rank Math.
        srcs = raw.get("sources") or [{"pattern": raw.get("from", raw.get("pattern", "")),
                                       "comparison": raw.get("comparison", "regex" if "pattern" in raw else "exact")}]
        self.sources = [(str(s.get("pattern", "")), s.get("comparison", "exact")) for s in srcs]
        self.to = str(raw.get("to", ""))
        self.code = int(raw.get("code", 301))
        self.status = raw.get("status", "active")
        self.to_key = raw.get("to_key")
        self.origin = origin

    def match(self, path):
        """Giống Rank Math: so với đường dẫn không có / ở đầu và cuối. Trả match (regex) hoặc True; không khớp trả None."""
        p = path.strip("/")
        for pat, cmp_ in self.sources:
            q = norm(pat).strip("/") if cmp_ != "regex" else pat
            if cmp_ == "exact" and q == p:
                return True
            if cmp_ == "contains" and q and q in p:
                return True
            if cmp_ == "start" and q and p.startswith(q):
                return True
            if cmp_ == "end" and q and p.endswith(q):
                return True
            if cmp_ == "regex":
                try:
                    m = re.search(pat, p, re.I)
                except re.error:
                    continue
                if m:
                    return m
        return None

    def target(self, m=None, host=""):
        """Đường dẫn đích đã chuẩn hoá. None khi đích ở site khác hoặc còn biến $N chưa thay được."""
        if host and host_of(self.to) and host_of(self.to) != host.casefold():
            return None
        t = self.to
        if "$" in t:
            if not hasattr(m, "group"):
                return None
            t = re.sub(r"\$(\d)", lambda x: (m.group(int(x.group(1))) or "") if int(x.group(1)) <= (m.re.groups or 0) else "", t)
        return norm(t)


def first_match(rules, path, skip=None):
    for r in rules:
        if r is skip:
            continue
        m = r.match(path)
        if m:
            return r, m
    return None, None
