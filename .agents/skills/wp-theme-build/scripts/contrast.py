#!/usr/bin/env python3
"""Đo tương phản WCAG của bảng token màu "token brand → token theme → nơi dùng → tương phản".

  python3 contrast.py check <bảng.md|bảng.csv> [--brand <file guideline|#hex,#hex>] [--write]
      đọc bảng, tính tỉ lệ tương phản từng dòng, in kết quả. Mặc định chạy thử, không ghi file.
      --write ghi cột "tương phản" vào bảng (chỉ khi người duyệt đồng ý ghi).
  python3 contrast.py pair <chữ> <nền> [--size text|large|ui]
      đo một cặp màu. Chữ và nền có thể là dải: "#FF5A1F,#FF9E1B" (lấy điểm tệ nhất).

Cột của bảng (không phân biệt hoa thường và dấu):
  token brand | token theme | nơi dùng | chữ (fg) | nền (bg) | cỡ (text, large, ui) | ngoại lệ
  - "chữ" và "nền" nhận nhiều màu (chữ gradient, nền gradient): lấy tỉ lệ thấp nhất của mọi cặp.
  - "cỡ" mặc định text (ngưỡng 4.5). large và ui có ngưỡng 3.0.
  - "ngoại lệ" có lý do: dòng trượt vẫn được báo, nhưng không làm exit 1.
  - "token brand" có mã hex ngoài danh sách --brand: báo NGOÀI GUIDELINE, exit 1.
  - Dòng không có cả chữ lẫn nền: bỏ qua.

Exit 0: đạt hết. Exit 1: có dòng trượt hoặc ngoài guideline. Exit 2: lỗi đầu vào.
Không hỗ trợ màu có alpha. Trộn màu lên nền trước khi đưa vào bảng.
"""
import argparse
import csv
import io
import math
import re
import sys
import unicodedata
from pathlib import Path

HEX = re.compile(r"#[0-9a-fA-F]+\b")
THRESH = {"text": 4.5, "large": 3.0, "ui": 3.0}
ALIASES = {
    "brand": {"token brand", "brand", "mau brand"},
    "theme": {"token theme", "theme", "token"},
    "use": {"noi dung", "noi dung", "use", "vi tri"},
    "fg": {"chu", "fg", "mau chu", "foreground"},
    "bg": {"nen", "bg", "mau nen", "background"},
    "size": {"co", "size", "co chu"},
    "waive": {"ngoai le", "waive", "exception"},
    "ratio": {"tuong phan", "contrast", "ratio"},
}


class InputError(Exception):
    pass


def norm(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def parse_hex(token):
    h = token.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise InputError(f"mã màu không hợp lệ hoặc có alpha: {token}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def fmt_ratio(r):
    return f"{math.floor(r * 100) / 100:.2f}"


def hexes(cell):
    return HEX.findall(cell or "")


def worst_ratio(fg_cell, bg_cell):
    fgs, bgs = hexes(fg_cell), hexes(bg_cell)
    if not fgs:
        raise InputError(f"ô chữ không có mã màu: '{fg_cell}'")
    if not bgs:
        raise InputError(f"ô nền không có mã màu: '{bg_cell}'")
    return min(ratio(parse_hex(f), parse_hex(b)) for f in fgs for b in bgs)


def split_md_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def read_md(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            header = split_md_row(lines[i])
            keys = map_header(header)
            if "fg" in keys.values() and "bg" in keys.values() and j - i >= 3:
                rows = [split_md_row(x) for x in lines[i + 2:j]]
                return {"kind": "md", "lines": lines, "span": (i, j), "header": header, "rows": rows}
            i = j
        else:
            i += 1
    raise InputError("không thấy bảng có cột chữ và nền")


def read_csv(text):
    delim = "\t" if "\t" in text.splitlines()[0] else ","
    data = list(csv.reader(io.StringIO(text), delimiter=delim))
    if len(data) < 2:
        raise InputError("bảng CSV không có dòng dữ liệu")
    return {"kind": "csv", "header": data[0], "rows": data[1:], "delim": delim}


def map_header(header):
    out = {}
    for idx, h in enumerate(header):
        n = norm(h)
        for key, names in ALIASES.items():
            if n in names and idx not in out:
                out[idx] = key
    return out


def load_brand(arg):
    if not arg:
        return None
    p = Path(arg)
    src = p.read_text(encoding="utf-8") if p.is_file() else arg
    found = {parse_hex(h) for h in hexes(src)}
    if not found:
        raise InputError("--brand không có mã màu nào")
    return found


def evaluate(table, brand):
    keys = map_header(table["header"])
    col = {v: k for k, v in keys.items()}
    for need in ("fg", "bg"):
        if need not in col:
            raise InputError(f"thiếu cột {need}")
    results = []
    for n, row in enumerate(table["rows"], 1):
        row = row + [""] * (len(table["header"]) - len(row))
        get = lambda k: row[col[k]].strip() if k in col else ""
        fg_cell, bg_cell = get("fg"), get("bg")
        label = get("theme") or get("use") or f"dòng {n}"
        if not fg_cell and not bg_cell:
            results.append({"label": label, "status": "BỎ QUA", "ratio": None, "text": "-", "fail": False})
            continue
        size = norm(get("size")) or "text"
        if size not in THRESH:
            raise InputError(f"{label}: cỡ '{size}' không hợp lệ (text, large, ui)")
        r = worst_ratio(fg_cell, bg_cell)
        need = THRESH[size]
        waive = get("waive").strip(" -")
        fail = r < need
        status = "ĐẠT"
        if fail:
            status = "NGOẠI LỆ" if waive else "TRƯỢT"
        text = f"{fmt_ratio(r)}:1 {status.lower()}" + (f" ({waive})" if fail and waive else "")
        brand_bad = False
        if brand and "brand" in col:
            bad = [h for h in hexes(get("brand")) if parse_hex(h) not in brand]
            if bad:
                brand_bad = True
                status += " + NGOÀI GUIDELINE"
                text += f"; ngoài guideline: {' '.join(bad)}"
        results.append({"label": label, "status": status, "ratio": r, "need": need, "text": text,
                        "fail": (fail and not waive) or brand_bad})
    return results, col


def render_written(table, col, results):
    header = list(table["header"])
    ridx = col.get("ratio")
    if ridx is None:
        header.append("Tương phản")
        ridx = len(header) - 1
    rows = []
    for row, res in zip(table["rows"], results):
        row = row + [""] * (len(table["header"]) - len(row))
        row = row[:len(table["header"])] + [""] * (len(header) - len(table["header"]))
        row[ridx] = res["text"]
        rows.append(row)
    if table["kind"] == "csv":
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=table["delim"], lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
        return buf.getvalue()
    i, j = table["span"]
    sep = "|" + "|".join("---" for _ in header) + "|"
    block = ["| " + " | ".join(header) + " |", sep] + ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(table["lines"][:i] + block + table["lines"][j:]) + "\n"


def cmd_check(a):
    path = Path(a.file)
    if not path.is_file():
        raise InputError(f"không thấy file {a.file}")
    text = path.read_text(encoding="utf-8")
    table = read_csv(text) if path.suffix.lower() in (".csv", ".tsv") else read_md(text)
    results, col = evaluate(table, load_brand(a.brand))
    for r in results:
        print(f"{r['label']}\t{r['text'] if r['ratio'] is not None else r['status']}")
    failed = [r for r in results if r["fail"]]
    print(f"Tổng {len(results)} dòng, {len(failed)} dòng cần sửa.")
    out = render_written(table, col, results)
    if a.write:
        path.write_text(out, encoding="utf-8")
        print(f"Đã ghi cột tương phản vào {path}")
    else:
        print("Chạy thử: chưa ghi file. Thêm --write để ghi cột tương phản.")
    return 1 if failed else 0


def cmd_pair(a):
    r = worst_ratio(a.fg, a.bg)
    need = THRESH[a.size]
    ok = r >= need
    print(f"{fmt_ratio(r)}:1 (cần {need}) {'đạt' if ok else 'trượt'}")
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Đo tương phản WCAG cho bảng token màu.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="đo cả bảng token")
    c.add_argument("file")
    c.add_argument("--brand", help="file guideline hoặc danh sách mã hex, cách nhau bằng dấu phẩy")
    c.add_argument("--write", action="store_true", help="ghi cột tương phản vào file (mặc định chạy thử)")
    c.set_defaults(fn=cmd_check)
    q = sub.add_parser("pair", help="đo một cặp màu")
    q.add_argument("fg")
    q.add_argument("bg")
    q.add_argument("--size", choices=sorted(THRESH), default="text")
    q.set_defaults(fn=cmd_pair)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except InputError as e:
        print(f"Lỗi đầu vào: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
