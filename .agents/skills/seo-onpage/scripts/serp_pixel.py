#!/usr/bin/env python3
"""serp_pixel: đo độ rộng title và meta description theo pixel như SERP Google, xuất TSV.

Lệnh:
  measure    --in pages.tsv (cột url, title, description; thiếu cột nào thì bỏ trường đó)
             hoặc --title "..." [--desc "..."]; [--profile desktop] [--limit-title PX] [--limit-desc PX] --out out.tsv
  calibrate  --serp <thư mục JSON Firecrawl search | TSV có cột url, title>... [--full full.tsv] --out report.json
             Học ngưỡng cắt title từ SERP đã lưu: title hiển thị kết thúc bằng "..." là bị cắt.
             Cần title đầy đủ (full.tsv: url, full_title) để gán nhãn dòng bị cắt. Tách dev/holdout theo URL.
  table      --font Arial.ttf --out arial_widths.json   (sinh lại bảng độ rộng ký tự; cần fontTools)

Đo bằng Pillow + file font khi có. Thiếu Pillow hoặc thiếu file font: dùng bảng arial_widths.json cạnh script.
Nguồn số đo và ngưỡng: references/title-pixel.md.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE = HERE / "arial_widths.json"
FONT_PATHS = [
    os.environ.get("SERP_FONT", ""),
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
# Ngưỡng theo đơn vị Arial. title_limit đo trên SERP 18/10/2026 (references/title-pixel.md mục 2).
# desc_limit là ước lượng phổ biến, chưa kiểm chứng trên dữ liệu.
PROFILES = {
    "desktop": {"font": "Arial", "title_size": 20, "desc_size": 14, "title_limit": 688, "desc_limit": 920,
                "title_source": "đo: SERP 18/10/2026, 273 title, dev 133/133, holdout 138/140",
                "desc_source": "ước lượng phổ biến, chưa kiểm chứng"},
}
ELLIPSIS = " ..."
BIG = 2048


def nfc(s):
    return unicodedata.normalize("NFC", (s or "").strip())


class Meter:
    """Đo độ rộng chữ theo px. mode = 'font' (Pillow + file font) hoặc 'table' (bảng ký tự)."""

    def __init__(self, size, force_table=False):
        self.size = size
        self.font = None
        if not force_table:
            try:
                from PIL import ImageFont
                for p in FONT_PATHS:
                    if p and Path(p).is_file():
                        # Nạp ở cỡ lớn rồi quy về cỡ thật: bỏ làm tròn hinting, khớp cách trình duyệt dàn chữ.
                        self.font = ImageFont.truetype(p, BIG)
                        self.path = p
                        break
            except ImportError:
                self.font = None
        if self.font is None:
            t = json.loads(TABLE.read_text(encoding="utf-8"))
            self.upm, self.w, self.default = t["upm"], t["widths"], t["default"]
        self.mode = "font" if self.font is not None else "table"

    def width(self, text):
        text = nfc(text)
        if self.font is not None:
            return float(self.font.getlength(text)) * self.size / BIG
        total = 0
        for ch in text:
            u = self.w.get(ch)
            if u is None:  # ký tự có dấu ngoài bảng: lấy độ rộng chữ gốc
                base = unicodedata.normalize("NFD", ch)[0]
                u = self.w.get(base, self.default)
            total += u
        return total * self.size / self.upm

    def cut(self, text, limit):
        """Phần chữ còn hiện khi cắt theo từ, kèm ' ...'. Trả text gốc nếu vừa."""
        text = nfc(text)
        if self.width(text) <= limit:
            return text
        words, keep = text.split(" "), ""
        for w in words:
            cand = (keep + " " + w).strip()
            if self.width(cand + ELLIPSIS) > limit:
                break
            keep = cand
        return (keep + ELLIPSIS).strip()


def verdict(px, limit):
    return "vừa" if px <= limit else "bị cắt"


def cmd_measure(a):
    prof = dict(PROFILES[a.profile])
    if a.limit_title:
        prof["title_limit"] = a.limit_title
    if a.limit_desc:
        prof["desc_limit"] = a.limit_desc
    mt, md = Meter(prof["title_size"], a.table), Meter(prof["desc_size"], a.table)
    if a.inp:
        rows = list(csv.DictReader(open(a.inp, encoding="utf-8"), delimiter="\t"))
    else:
        rows = [{"url": "", "title": a.title or "", "description": a.desc or ""}]
    out = []
    for r in rows:
        for field, m, lim in (("title", mt, prof["title_limit"]), ("description", md, prof["desc_limit"])):
            text = nfc(r.get(field))
            if not text:
                continue
            px = m.width(text)
            out.append({"url": r.get("url", ""), "field": field, "chars": len(text), "px": round(px, 1),
                        "limit_px": lim, "verdict": verdict(px, lim), "hien_thi": m.cut(text, lim),
                        "do_bang": m.mode, "nguon_nguong": prof[("title" if field == "title" else "desc") + "_source"]})
    cols = ["url", "field", "chars", "px", "limit_px", "verdict", "hien_thi", "do_bang", "nguon_nguong"]
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        w.writerows(out)
    n_cut = sum(o["verdict"] == "bị cắt" for o in out)
    print(json.dumps({"rows": len(out), "bi_cat": n_cut, "do_bang": mt.mode, "profile": a.profile}, ensure_ascii=False))


def load_serp(paths):
    """Trả {url: title hiển thị}. JSON Firecrawl search (data.web[]) hoặc TSV có cột url, title."""
    rows = {}
    for p in paths:
        pth = Path(p)
        files = sorted(pth.rglob("*.json")) if pth.is_dir() else [pth]
        for f in files:
            if f.suffix == ".json":
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                web = (d.get("data") or {}).get("web") if isinstance(d, dict) and isinstance(d.get("data"), dict) else None
                for x in web or []:
                    if x.get("url") and x.get("title"):
                        rows.setdefault(x["url"], nfc(x["title"]))
            else:
                for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"):
                    if r.get("url") and r.get("title"):
                        rows.setdefault(r["url"], nfc(r["title"]))
    return rows


def is_cut(t):
    return t.endswith("...") or t.endswith("…")


def in_holdout(url):
    return int(hashlib.md5(url.encode()).hexdigest(), 16) % 2 == 1


def fit(items, grid):
    """Ngưỡng có độ đúng cao nhất; nhiều ngưỡng bằng nhau thì lấy điểm giữa của dải tốt nhất."""
    scores = [(sum((px > L) == y for px, y in items), L) for L in grid]
    best = max(s for s, _ in scores)
    good = [L for s, L in scores if s == best]
    return good[len(good) // 2], best


def cmd_calibrate(a):
    m = Meter(a.size, a.table)
    shown = load_serp(a.serp)
    full = {}
    if a.full:
        for r in csv.DictReader(open(a.full, encoding="utf-8"), delimiter="\t"):
            full[r["url"]] = nfc(r["full_title"])
    labeled, unlabeled = [], []
    for u, t in shown.items():
        if not is_cut(t):
            labeled.append((u, t, 0))
            continue
        pre = t.rstrip(".…").strip()
        f = full.get(u)
        if f and f.startswith(pre) and len(f) > len(pre):
            labeled.append((u, f, 1))
        else:
            unlabeled.append((u, t))
    dev = [(m.width(t), y) for u, t, y in labeled if not in_holdout(u)]
    hold = [(m.width(t), y) for u, t, y in labeled if in_holdout(u)]
    if sum(y for _, y in dev) < 3 or sum(y for _, y in hold) < 3:
        sys.exit("cần ít nhất 3 title bị cắt có title đầy đủ ở mỗi phần dev và holdout")
    grid = [round(a.lo + i * a.step, 1) for i in range(int((a.hi - a.lo) / a.step) + 1)]
    L, ok_dev = fit(dev, grid)
    err = [{"url": u, "title": t, "label": y, "px": round(m.width(t), 1)}
           for u, t, y in labeled if (m.width(t) > L) != y]
    ok_hold = sum((px > L) == y for px, y in hold)
    shown_ok = sum(m.width(t) <= L for _, t in unlabeled)
    chars = [(len(t), y) for u, t, y in labeled if not in_holdout(u)]
    N, _ = fit(chars, list(range(40, 101)))
    hold_chars = sum((len(t) > N) == y for u, t, y in labeled if in_holdout(u))
    rep = {"size": a.size, "do_bang": m.mode, "n_labeled": len(labeled), "n_cut_labeled": sum(y for *_, y in labeled),
           "n_cut_no_full": len(unlabeled), "limit_px": L,
           "dev": {"n": len(dev), "dung": ok_dev}, "holdout": {"n": len(hold), "dung": ok_hold,
                                                              "accuracy": round(ok_hold / len(hold), 4)},
           "cut_no_full_vua_nguong": f"{shown_ok}/{len(unlabeled)}",
           "so_sanh_ky_tu": {"limit_chars": N, "holdout_dung": hold_chars},
           "loi": err}
    Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("limit_px", "dev", "holdout", "cut_no_full_vua_nguong", "so_sanh_ky_tu")},
                     ensure_ascii=False))


def cmd_table(a):
    from fontTools.ttLib import TTFont
    f = TTFont(a.font)
    cmap, hmtx = f.getBestCmap(), f["hmtx"].metrics
    chars = [chr(c) for c in range(32, 127)]
    chars += [chr(c) for c in range(0xC0, 0x250)] + [chr(c) for c in range(0x1EA0, 0x1EFA)]
    chars += list("–—…‘’“”•·|«»€₫×")
    w = {ch: hmtx[cmap[ord(ch)]][0] for ch in chars if ord(ch) in cmap}
    default = round(sum(w[c] for c in "abcdefghijklmnopqrstuvwxyz") / 26)
    out = {"font": Path(a.font).name, "upm": f["head"].unitsPerEm, "default": default, "widths": w}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print(f"{len(w)} ký tự -> {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--in", dest="inp")
    m.add_argument("--title")
    m.add_argument("--desc")
    m.add_argument("--profile", default="desktop", choices=sorted(PROFILES))
    m.add_argument("--limit-title", type=float)
    m.add_argument("--limit-desc", type=float)
    m.add_argument("--table", action="store_true", help="bỏ qua file font, đo bằng bảng ký tự")
    m.add_argument("--out", required=True)
    c = sub.add_parser("calibrate")
    c.add_argument("--serp", nargs="+", required=True)
    c.add_argument("--full")
    c.add_argument("--size", type=int, default=20)
    c.add_argument("--lo", type=float, default=500)
    c.add_argument("--hi", type=float, default=800)
    c.add_argument("--step", type=float, default=2)
    c.add_argument("--table", action="store_true")
    c.add_argument("--out", required=True)
    t = sub.add_parser("table")
    t.add_argument("--font", required=True)
    t.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "measure" and not (a.inp or a.title or a.desc):
        ap.error("measure cần --in hoặc --title/--desc")
    {"measure": cmd_measure, "calibrate": cmd_calibrate, "table": cmd_table}[a.cmd](a)


if __name__ == "__main__":
    main()
