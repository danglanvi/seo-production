#!/usr/bin/env python3
"""So số đo của type_probe.mjs với thang chữ và báo lỗi. Chỉ đọc file JSON, không gọi mạng.

Chạy: python3 type_check.py <type_probe.json> [--rules FILE] [--list] [--json] [--out FILE] [--print-defaults]

Báo: % chữ đọc dưới ngưỡng, H1 lệch giữa các template, H2 và H3 lệch thang, dòng quá dài, hero sát menu.
Thang mặc định nằm trong DEFAULTS, mỗi số có nguồn. Số riêng của site đặt trong file --rules:
  .json: chính là bộ luật.  .md: lấy khối ```json đầu tiên có khoá "type_rules".
Chỉ khối chữ vùng main, không fixed, không nằm trong exclude được tính. Component đặc biệt khai ở "components" (cỡ riêng hoặc loại hẳn).
Mã thoát: 0 không có lỗi mức fail · 1 có lỗi mức fail · 2 file hoặc luật sai.
"""
import argparse
import collections
import copy
import json
import re
import sys

DEFAULTS = {
    "body_min_px": {"desktop": 16, "mobile": 15},
    "body_min_chars": 25,
    "read_tags": ["p", "li", "td", "dd", "blockquote", "figcaption", "dt", "th"],
    "small_pct_max": 5,
    "max_cpl": 80,
    "h1_spread_px": 4,
    "heading_step_px": 2,
    "h_scale": {"tolerance_px": 1},
    "h_max_distinct": 2,
    "hero_gap_min_px": {"desktop": 32, "mobile": 24},
    "exclude": {"regions": ["header", "footer", "nav"], "sel_regex": [r"icon", r"(^|[ .>])fa[sbrl]?([ .\-]|$)", r"dashicons", r"eicon"], "text_regex": []},
    "components": [],
    "severity": {"body_small": "fail", "h1_spread": "fail", "h_order": "fail", "hero_tight": "fail", "h_scale": "warn", "long_line": "warn"},
}

SOURCES = {
    "body_min_px": "Ngưỡng đọc trên màn hình thường (desktop 16, mobile 15), đợt ux-type-audit gtvseo 19–20/10/2026. Không phải luật của Google.",
    "body_min_chars": "Khối dưới 25 ký tự là nhãn hoặc nút, không tính chữ thân (cùng đợt ux-type-audit).",
    "small_pct_max": "Pilot gtvseo 19–20/10/2026: sau khi sửa, 2 trang còn 1,6–5,6% khối dưới ngưỡng, phần còn lại là nhãn đã chốt. Chưa hiệu chuẩn thêm.",
    "max_cpl": "WCAG 2.2 tiêu chí 1.4.8 (mức AAA): dòng không quá 80 ký tự. Lane thang chữ gtvseo 20/10/2026 dùng ngưỡng này.",
    "h1_spread_px": "Ước lượng, chưa có nguồn. Pilot gtvseo: H1 56 px trang chủ so với 32 px trang dịch vụ là lỗi; sau sửa 40 so với 36 được chấp nhận.",
    "heading_step_px": "H2 và H3 phải lớn hơn chữ thân ít nhất 2 px, H2 lớn hơn H3 (ux-type-audit 19–20/10/2026).",
    "h_max_distinct": "Ước lượng, chưa có nguồn: mỗi cấp H2 hoặc H3 nên có tối đa 2 cỡ trên một trang.",
    "hero_gap_min_px": "Ước lượng, chưa có nguồn. Pilot gtvseo: khoảng menu → H1 64 px desktop và 56 px mobile đạt; bản cũ hero sát menu bị Vincent báo.",
    "exclude": "Vùng header, footer, nav và icon font không thuộc thang chữ thân bài.",
}


def is_mobile(page):
    return page.get("width", 1366) < 800


def vpk(page):
    return "mobile" if is_mobile(page) else "desktop"


def merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out


def load_rules(path):
    if not path:
        return copy.deepcopy(DEFAULTS)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        raise ValueError("không đọc được --rules: %s" % e)
    if path.endswith(".json"):
        data = json.loads(text)
        data = data.get("type_rules", data)
    else:
        data = None
        for m in re.finditer(r"```json\s*\n(.*?)\n```", text, flags=re.S):
            try:
                obj = json.loads(m.group(1))
            except ValueError:
                continue
            if isinstance(obj, dict) and "type_rules" in obj:
                data = obj["type_rules"]
                break
        if data is None:
            raise ValueError("không thấy khối ```json có khoá \"type_rules\" trong %s" % path)
    if not isinstance(data, dict):
        raise ValueError("type_rules phải là object")
    unknown = set(data) - set(DEFAULTS)
    if unknown:
        raise ValueError("khoá lạ trong luật: %s" % ", ".join(sorted(unknown)))
    return merge(DEFAULTS, data)


def rx(patterns):
    return [re.compile(p, re.I) for p in patterns]


def classify(b, rules, ex_sel, ex_text, comps, vk):
    """Trả (nhóm, ngưỡng px hoặc None). nhóm: 'tinh' (tính), 'loai' (loại). min_px của component là số hoặc {desktop, mobile}; 0 hoặc thiếu là loại hẳn."""
    if b.get("fixed") or b.get("region") in rules["exclude"]["regions"]:
        return "loai", None
    hay = (b.get("sel", "") + " " + b.get("cls", ""))
    if any(r.search(hay) for r in ex_sel) or any(r.search(b.get("t", "")) for r in ex_text):
        return "loai", None
    for name, rg, raw in comps:
        if rg.search(hay):
            mn = raw.get(vk) if isinstance(raw, dict) else raw
            if raw is None or mn == 0:
                return "loai", None
            return "tinh", mn
    return "tinh", None


def check(data, rules):
    ex_sel, ex_text = rx(rules["exclude"]["sel_regex"]), rx(rules["exclude"]["text_regex"])
    comps = []
    for c in rules["components"]:
        comps.append((c.get("name", c.get("sel_regex", "?")), re.compile(c["sel_regex"], re.I), c.get("min_px")))
    sev = rules["severity"]
    findings, pages_out, h1s = [], [], collections.defaultdict(list)
    for pg in data.get("pages", []):
        label = "%s %s" % (pg.get("name") or pg.get("path"), pg.get("vp") or vpk(pg))
        if pg.get("error"):
            findings.append({"code": "probe_error", "severity": "fail", "page": label, "msg": "lượt đo lỗi: %s" % pg["error"]})
            continue
        vk = vpk(pg)
        floor = rules["body_min_px"][vk]
        main = [b for b in pg.get("blocks", []) if b["tag"] in rules["read_tags"] and b.get("n", 0) >= rules["body_min_chars"]]
        counted, excluded, small = [], 0, []
        for b in main:
            grp, mn = classify(b, rules, ex_sel, ex_text, comps, vk)
            if grp == "loai":
                excluded += 1
                continue
            counted.append(b)
            if b["fs"] < (mn if mn is not None else floor):
                small.append(dict(b, limit=mn if mn is not None else floor))
        chars = sum(b["n"] for b in counted) or 1
        dist = collections.Counter()
        for b in counted:
            dist[int(b["fs"])] += b["n"]
        body = max(dist.items(), key=lambda x: x[1])[0] if dist else 0
        small_pct = round(sum(b["n"] for b in small) / chars * 100, 1)
        heads = [h for h in pg.get("heads", []) if h.get("region") == "main" and not h.get("fixed")]
        sizes = {lv: sorted({round(h["fs"]) for h in heads if h["tag"] == lv}) for lv in ("h1", "h2", "h3", "h4")}
        page = {"page": label, "vp": vk, "body_px": body, "blocks": len(counted), "excluded": excluded, "small_pct": small_pct, "small": len(small), "heads": sizes, "h1_gap": pg.get("h1_gap")}
        pages_out.append(page)

        def add(code, msg, detail=None):
            findings.append({"code": code, "severity": sev.get(code, "warn"), "page": label, "msg": msg, **({"detail": detail} if detail else {})})

        if small_pct > rules["small_pct_max"]:
            add("body_small", "%s%% chữ đọc dưới ngưỡng %s px (tối đa %s%%), chữ thân %s px" % (small_pct, floor, rules["small_pct_max"], body),
                _dedupe(small))
        elif small:
            page["note"] = "%d khối dưới ngưỡng nhưng %s%% <= %s%%" % (len(small), small_pct, rules["small_pct_max"])
            page["small_detail"] = _dedupe(small)
        step = rules["heading_step_px"]
        for lv in ("h2", "h3"):
            low = [s for s in sizes[lv] if body and s < body + step]
            if low:
                add("h_order", "%s cỡ %s px chưa lớn hơn chữ thân %s px ít nhất %s px" % (lv.upper(), low, body, step))
        if sizes["h2"] and sizes["h3"] and min(sizes["h2"]) <= max(sizes["h3"]):
            add("h_order", "H2 nhỏ nhất %s px <= H3 lớn nhất %s px" % (min(sizes["h2"]), max(sizes["h3"])))
        tol = rules["h_scale"].get("tolerance_px", 1)
        for lv in ("h2", "h3"):
            allowed = (rules["h_scale"].get(lv) or {}).get(vk)
            if allowed:
                off = [s for s in sizes[lv] if all(abs(s - a) > tol for a in allowed)]
                if off:
                    add("h_scale", "%s cỡ %s px lệch thang %s px (dung sai %s)" % (lv.upper(), off, allowed, tol))
            elif len(sizes[lv]) > rules["h_max_distinct"]:
                add("h_scale", "%s có %d cỡ khác nhau %s (tối đa %d)" % (lv.upper(), len(sizes[lv]), sizes[lv], rules["h_max_distinct"]))
        longs = sorted([b for b in counted if b.get("lines", 1) > 1 and b.get("cpl", 0) > rules["max_cpl"]], key=lambda b: -b["cpl"])
        if longs:
            add("long_line", "%d khối có hơn %d ký tự mỗi dòng, dài nhất %d" % (len(longs), rules["max_cpl"], longs[0]["cpl"]),
                [{"sel": b["sel"], "cpl": b["cpl"], "w": b["w"], "y": b["y"]} for b in longs[:8]])
        gap = pg.get("h1_gap")
        if gap is not None and gap < rules["hero_gap_min_px"][vk]:
            add("hero_tight", "H1 cách đáy header %s px, tối thiểu %s px" % (gap, rules["hero_gap_min_px"][vk]))
        h1 = sizes["h1"]
        if h1:
            h1s[vk].append((page["page"], h1[0]))
    for vk, lst in h1s.items():
        vals = [v for _, v in lst]
        if len(lst) > 1 and max(vals) - min(vals) > rules["h1_spread_px"]:
            findings.append({"code": "h1_spread", "severity": sev.get("h1_spread", "fail"), "page": "(mọi trang, %s)" % vk,
                             "msg": "H1 lệch %s px giữa các template (tối đa %s px)" % (max(vals) - min(vals), rules["h1_spread_px"]),
                             "detail": [{"page": p, "h1_px": v} for p, v in lst]})
    return {"pages": pages_out, "findings": findings}


def _dedupe(blocks):
    seen, out = set(), []
    for b in sorted(blocks, key=lambda b: -b["n"]):
        key = (b["sel"].split(" > ")[-1], b["fs"])
        if key in seen:
            continue
        seen.add(key)
        out.append({"sel": b["sel"], "fs": b["fs"], "limit": b["limit"], "n": b["n"], "y": b["y"], "t": b.get("t", "")[:50]})
    return out


def render(res, show_list):
    L = ["| Trang | Khổ | Chữ thân | % dưới ngưỡng | Khối tính / loại | H1 / H2 / H3 (px) | Header → H1 |", "|---|---|---|---|---|---|---|"]
    for p in res["pages"]:
        h = " / ".join(",".join(str(x) for x in p["heads"][k]) or "–" for k in ("h1", "h2", "h3"))
        L.append("| %s | %s | %s px | %s%% | %d / %d | %s | %s |" % (p["page"], p["vp"], p["body_px"], p["small_pct"], p["blocks"], p["excluded"], h, "–" if p["h1_gap"] is None else "%s px" % p["h1_gap"]))
    L.append("")
    fails = [f for f in res["findings"] if f["severity"] == "fail"]
    warns = [f for f in res["findings"] if f["severity"] != "fail"]
    L.append("Kết quả: %s. %d lỗi fail, %d cảnh báo." % ("FAIL" if fails else "PASS", len(fails), len(warns)))
    for f in res["findings"]:
        L.append("- [%s] %s · %s: %s" % (f["severity"].upper(), f["code"], f["page"], f["msg"]))
        if show_list:
            for d in f.get("detail", []):
                L.append("    " + ", ".join("%s=%s" % (k, v) for k, v in d.items()))
    if show_list:
        for p in res["pages"]:
            for d in p.get("small_detail", []):
                L.append("  (dưới ngưỡng nhưng trong mức cho phép) %s: %s px %s" % (p["page"], d["fs"], d["sel"]))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("probe", nargs="?", help="type_probe.json")
    ap.add_argument("--rules")
    ap.add_argument("--list", action="store_true", help="in chi tiết từng khối vi phạm")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--print-defaults", action="store_true", help="in thang mặc định và nguồn của từng số")
    a = ap.parse_args(argv)
    if a.print_defaults:
        print(json.dumps({"defaults": DEFAULTS, "sources": SOURCES}, ensure_ascii=False, indent=1))
        return 0
    if not a.probe:
        ap.print_usage(sys.stderr)
        return 2
    try:
        data = json.load(open(a.probe, encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("pages"), list) or not data["pages"]:
            raise ValueError("file không có danh sách pages")
        rules = load_rules(a.rules)
    except (OSError, ValueError) as e:
        print("Lỗi: %s" % e, file=sys.stderr)
        return 2
    res = check(data, rules)
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1) if a.json else render(res, a.list))
    return 1 if any(f["severity"] == "fail" for f in res["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
