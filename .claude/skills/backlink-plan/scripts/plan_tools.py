#!/usr/bin/env python3
"""Số liệu và kiểm cho backlink-plan. Chỉ dùng thư viện chuẩn.

  velocity  --file <rdnew_<domain>.json>... --mine <domain> --since 2025-10 --until 2026-10 [--new-site] --out <velocity.md>
            RD mới không spam theo tháng từ Ahrefs referring-domains (is_spam=false, traffic_domain>0, có first_seen, last_seen).
            Nhịp chuẩn = trung vị các tháng, vì tháng bùng (≥ 3 lần trung vị) làm lệch trung bình. Site mới: ½ nhịp.
  quickwins --file <organic-keywords.json> [--top 20] --out <quickwins.md>
            Gom từ khoá vị trí 4–20 theo URL đích (Bước 1 mục 4). Gắn cờ URL lạ (chữ hoa, %20, thiếu slug).
  check     --csv <plan.csv> --stage 1|2|3 --out <check.md>
            Kiểm file CSV per-link theo references/anchor-ratio-framework.md. Trả mã 1 khi có FAIL.
            Cột bắt buộc: Target URL, Anchor type, Anchor, Tháng. Cột tuỳ chọn: DR.
"""
import argparse
import csv
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SAFE = {"brand", "naked", "generic", "image"}
KEYWORD = {"exact", "partial", "synonym", "brand_kw", "niche", "longtail", "title"}
ALIAS = {"brand thuần": "brand", "thương hiệu": "brand", "link trần": "naked", "url": "naked", "naked/url": "naked",
         "chung chung": "generic", "ảnh": "image", "image (alt)": "image", "chính xác": "exact", "khớp một phần": "partial",
         "đồng nghĩa": "synonym", "semantic": "synonym", "brand + keyword": "brand_kw", "brand+kw": "brand_kw",
         "compound": "brand_kw", "lĩnh vực": "niche", "long-tail": "longtail", "long tail": "longtail", "title anchor": "title"}
STAGE = {1: (65, 75), 2: (40, 50), 3: (35, 45)}  # % nhóm AN TOÀN; bảng giai đoạn ghi ~70 cho GĐ1, cho lệch ±5


def load(path, key):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, list) and d and isinstance(d[0], dict) and "text" in d[0]:
        t = d[0]["text"]
        d, _ = json.JSONDecoder().raw_decode(t[t.index("{"):])
    return d.get("target"), d[key]


def write_out(out, lines, data):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(out).with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {out}")


def months(since, until):
    y, m = map(int, since.split("-"))
    y2, m2 = map(int, until.split("-"))
    out = []
    while (y, m) <= (y2, m2):
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def cmd_velocity(a):
    ms = months(a.since, a.until)
    res = {}
    for f in a.file:
        tgt, rds = load(f, "refdomains")
        new, live = Counter(), Counter()
        for x in rds:
            k = (x.get("first_seen") or "")[:7]
            if k in ms and not x.get("is_spam") and (x.get("traffic_domain") or 0) > 0:
                new[k] += 1
                if not x.get("last_seen"):
                    live[k] += 1
        med = statistics.median([new[k] for k in ms])
        med_live = statistics.median([live[k] for k in ms])
        burst = [k for k in ms if new[k] >= max(3 * med, 20)]
        res[tgt] = {"new": [new[k] for k in ms], "live": [live[k] for k in ms], "median": med, "median_live": med_live,
                    "mean": round(sum(new.values()) / len(ms), 1), "burst": burst, "capped": len(rds) % 250 == 0}
    comps = [t for t in res if t != a.mine]
    pace = statistics.median([res[t]["median_live"] for t in comps]) if comps else None
    if pace is not None and a.new_site:
        pace = pace / 2
    lines = [f"# RD mới không spam theo tháng ({ms[0]} → {ms[-1]})", "",
             "Lọc: Ahrefs is_spam = false, traffic_domain > 0. \"Còn sống\" = chưa mất link (last_seen trống).", "",
             "| Domain | Trung vị/tháng | Trung vị còn sống | Trung bình | Tháng bùng |", "|---|---|---|---|---|"]
    for t, r in res.items():
        lines.append(f"| {t}{' (chạm trần 250 dòng)' if r['capped'] else ''} | {r['median']} | {r['median_live']} | {r['mean']} | {', '.join(r['burst']) or '—'} |")
    lines += ["", "| Tháng | " + " | ".join(res) + " |", "|---|" + "---|" * len(res)]
    for i, k in enumerate(ms):
        lines.append(f"| {k} | " + " | ".join(f"{res[t]['new'][i]} ({res[t]['live'][i]})" for t in res) + " |")
    lines += ["", f"Nhịp chuẩn đề xuất = trung vị \"còn sống\" của đối thủ{' × ½ (site mới)' if a.new_site else ''}: **{pace} RD/tháng**.",
              "Số trong ngoặc là RD còn sống. Tháng bùng là tháng có RD mới ≥ 3 lần trung vị và ≥ 20."]
    write_out(a.out, lines, {"months": ms, "domains": res, "pace": pace, "new_site": a.new_site})


def norm_url(u):
    u = re.sub(r"^https?://(www\.)?", "", (u or "").strip()).split("?")[0].split("#")[0]
    return u.rstrip("/")


def odd_url(u):
    path = u.split("/", 1)[1] if "/" in u else ""
    return bool(re.search(r"[A-Z]|%20", path)) or (path != "" and "-" not in path and "/" in path)


def cmd_quickwins(a):
    _, kws = load(a.file, "keywords")
    by = defaultdict(list)
    for k in kws:
        by[norm_url(k.get("best_position_url"))].append(k)
    rows = []
    for u, ks in by.items():
        top = max(ks, key=lambda k: k.get("volume") or 0)
        rows.append({"url": u, "n": len(ks), "volume": sum(k.get("volume") or 0 for k in ks), "traffic": sum(k.get("sum_traffic") or 0 for k in ks),
                     "top_kw": top["keyword"], "top_pos": top.get("best_position"), "odd": odd_url(u)})
    rows.sort(key=lambda r: -r["volume"])
    ok = [r for r in rows if not r["odd"]]
    lines = [f"# Quick win: {len(kws)} từ khoá vị trí 4–20, gom theo {len(ok)} URL", "",
             "| URL | Số từ khoá | Tổng volume | Traffic hiện tại | Từ khoá lớn nhất (vị trí) |", "|---|---|---|---|---|"]
    for r in ok[:a.top]:
        lines.append(f"| {r['url']} | {r['n']} | {r['volume']} | {r['traffic']} | {r['top_kw']} ({r['top_pos']}) |")
    odd = [f"{r['url']} ({r['n']} từ khoá)" for r in rows if r["odd"]]
    # chữ hoa đầu path hoặc %20: thường là breadcrumb danh mục Ahrefs ghi thành URL, không phải trang thật (site mẫu 19/10/2026)
    lines += ["", f"URL lạ, đã loại khỏi bảng ({len(odd)}): {', '.join(odd) or 'không có'}. Kiểm mã HTTP và canonical; URL thật mới đưa lại làm target."]
    write_out(a.out, lines, {"rows": rows})


def kind(s):
    s = unicodedata.normalize("NFC", (s or "").strip().lower())
    return ALIAS.get(s, s.replace(" ", "_"))


def cmd_check(a):
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    fails, warns = [], []
    unknown = sorted({r["Anchor type"] for r in rows if kind(r["Anchor type"]) not in SAFE | KEYWORD})
    if unknown:
        fails.append(f"Anchor type lạ: {', '.join(unknown)}")
    n = len(rows) or 1
    cnt = Counter(kind(r["Anchor type"]) for r in rows)
    safe = round(100 * sum(cnt[k] for k in SAFE) / n, 1)
    lo, hi = STAGE[a.stage]
    if not lo <= safe <= hi:
        fails.append(f"Nhóm AN TOÀN {safe}% ngoài khung giai đoạn {a.stage} ({lo}–{hi}%)")
    by_t = defaultdict(list)
    for r in rows:
        by_t[r["Target URL"]].append(r)
    for t, rs in [("toàn plan", rows)] + list(by_t.items()):
        ex = round(100 * sum(kind(r["Anchor type"]) == "exact" for r in rs) / len(rs), 1)
        if ex > 10:
            fails.append(f"Exact {ex}% ở {t} vượt trần 10%")
        elif ex > 8:
            warns.append(f"Exact {ex}% ở {t} trên 8%")
    seen = Counter((r["Tháng"], unicodedata.normalize("NFC", r["Anchor"].strip().lower())) for r in rows if kind(r["Anchor type"]) not in {"brand", "naked"})
    for (m, anc), c in seen.items():
        if c > 1:
            fails.append(f"Anchor non-brand \"{anc}\" lặp {c} lần trong tháng {m}")
    if rows and "DR" in rows[0]:
        for i, r in enumerate(rows, 2):
            try:
                dr = float(r["DR"])
            except ValueError:
                continue
            k = kind(r["Anchor type"])
            if dr < 40 and k in KEYWORD:
                fails.append(f"Dòng {i}: nguồn DR {dr:g} < 40 nhưng anchor {k}")
            elif k == "exact" and dr < 60:
                fails.append(f"Dòng {i}: exact ở nguồn DR {dr:g} < 60")
    var = {t: len({r["Anchor"].strip().lower() for r in rs}) for t, rs in by_t.items()}
    verdict = "FAIL" if fails else "PASS"
    lines = [f"# Kiểm anchor plan: {verdict}", "", f"{len(rows)} link · giai đoạn {a.stage} · nhóm AN TOÀN {safe}% (khung {lo}–{hi}%)", "",
             "| Loại | Số link | % |", "|---|---|---|"] + [f"| {k} | {v} | {round(100 * v / n, 1)}% |" for k, v in cnt.most_common()]
    lines += ["", "## FAIL", ""] + ([f"- {x}" for x in fails] or ["- không có"])
    lines += ["", "## Cảnh báo", ""] + ([f"- {x}" for x in warns] or ["- không có"])
    lines += ["", "## Số biến thể anchor theo target", ""] + [f"- {t}: {v} biến thể / {len(by_t[t])} link" for t, v in var.items()]
    lines += ["", "Script không kiểm được anchor 3 phần, co-occurrence và việc từ khoá có trong trang đích. Claude đọc các mục này."]
    write_out(a.out, lines, {"verdict": verdict, "safe_pct": safe, "counts": dict(cnt), "fails": fails, "warns": warns, "variations": var})
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("velocity")
    v.add_argument("--file", nargs="+", required=True)
    v.add_argument("--mine", required=True)
    v.add_argument("--since", required=True)
    v.add_argument("--until", required=True)
    v.add_argument("--new-site", action="store_true")
    v.add_argument("--out", required=True)
    q = sub.add_parser("quickwins")
    q.add_argument("--file", required=True)
    q.add_argument("--top", type=int, default=20)
    q.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("--csv", required=True)
    c.add_argument("--stage", type=int, choices=[1, 2, 3], required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"velocity": cmd_velocity, "quickwins": cmd_quickwins, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
