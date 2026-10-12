#!/usr/bin/env python3
"""Dựng bản nháp JSON qp-project/1 từ bảng hạng (output `qp_ranks.py table -o hang.json`).

  python3 qp_scaffold.py <hang.json> --slug acme --name "Acme Shop" --domain acme.vn --lead "Tên Lead"
                         [--tabs id1,id2,id3] [--period "12–23/10"] -o <CLIENT>_qp-chan-doan_v1.json

Script điền sẵn mọi trường có số: measure, status_row, beat_stats, idea (số keyword, số template, URL hub),
templates (đếm nhóm hạng, trạng thái gợi ý, ghi chú số), grid (chip keyword và hạng), canonical (URL hub),
matrix (tên cụm, số liệu), measure_slide (regex nháp từ rules.json), flags (lần chạy bị loại, keyword lệch bộ).
Câu chuyên môn tiêu chuẩn (cơ chế, luật canonical, quy trình lật URL, luật đọc số) cũng điền sẵn.
Trường cần người phân tích viết được để "TODO: <gợi ý>". `qp_render.py check` báo lỗi khi còn TODO.

Hạng trên chip = median của bảng hạng (median_high nên luôn là số nguyên có thật). Không ghi đè file đã có (tăng version).
Bảng hạng chạy --no-compare (không có mốc so sánh): không gắn trạng thái "Đang lan", compare_date để trống, cột so sánh bỏ.
Quá 16 template thì dừng: gộp template nhỏ trong rules.json rồi chạy lại qp_ranks.py table (không cắt bớt âm thầm).
"""
import argparse, json, math, re, sys
from collections import Counter
from pathlib import Path

STATUS = {"ok": "Đã mở", "up": "Đang lan", "mid": "Kẹt", "no": "Chưa có hạng"}
TD = "TODO: "


def ceil_rank(v):
    return None if v is None else int(math.ceil(v))


def d_vn(s):
    """'09.10.2026 11:10' → '09/10/2026'."""
    return s[:10].replace(".", "/") if s else ""


def span(runs):
    if not runs:
        return ""
    ds = sorted({d_vn(r) for r in runs}, key=lambda x: x[6:] + x[3:5] + x[:2])
    return ds[0] if len(ds) == 1 else f"{ds[0][:5]}–{ds[-1]}"


def status(t):
    """Trạng thái gợi ý của một template. "up" chỉ khi có mốc so sánh và số keyword Top 10 tăng đủ ngưỡng."""
    n, now, ago = t["n"], t["now"], t.get("ago")
    t10n = now["t3"] + now["t10"]
    if ago and t10n - (ago["t3"] + ago["t10"]) >= max(2, math.ceil(0.15 * n)):
        return "up"
    if now["t3"]:
        return "ok"
    if now["t10"] + now["t20"] + now["t50"]:
        return "mid"
    return "no"


def score(t):
    return (t["id"] not in ("khac", "other"), t["now"]["t10"] + t["now"]["t20"], t["now"]["t3"], t["n"])


def base_slot(label):
    m = re.match(r"(.*?)\s*(\[.*\].*)$", label)
    return (m.group(1).strip(), m.group(2).strip()) if m else (label, "")


def chip_label(kw, common):
    words = [w for w in kw.split() if w.lower() not in common]
    lab = " ".join(words) or kw
    while len(lab) > 30 and " " in lab:
        lab = lab.rsplit(" ", 1)[0]
    return lab[:30]


RE2_BAD = re.compile(r"\(\?<?[=!]|\\[1-9]|\\b(?=[^\x00-\x7f])|(?<=[^\x00-\x7f])\\b")


def re2_ok(rx):
    """GSC dùng RE2: không lookaround, không backreference; \\b chỉ hiểu chữ ASCII nên không đặt sát chữ có dấu."""
    return not RE2_BAD.search(rx)


def split_name(name):
    if len(name) <= 18:
        return [name]
    words, a = name.split(), ""
    for i, w in enumerate(words):
        if len((a + " " + w).strip()) > 18:
            b = " ".join(words[i:])
            return [a, b] if a and len(b) <= 18 else [TD + "tên ≤18 ký tự mỗi dòng"]
        a = (a + " " + w).strip()
    return [a]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ranks")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--lead", default="")
    ap.add_argument("--tabs", default="")
    ap.add_argument("--period", default="")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    H = json.loads(Path(a.ranks).read_text(encoding="utf-8"))
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} đã có. Đặt version mới (_v<N+1>) thay vì ghi đè.")

    tops, tpls, kws = H["tops"]["now"], H["templates"], H["keywords"]
    cmp = bool(H.get("ago_runs")) and H.get("compare", True)
    t3, t5, t10 = (tops[str(n)] if str(n) in tops else tops[n] for n in (3, 5, 10))
    k = len(H["now_runs"])
    now_lbl = f"median {k} lần {span(H['now_runs'])}" if k > 1 else d_vn(H["now_runs"][0])
    src = f"SpySERP · {H.get('project') or ''} · {H['engine']} · {now_lbl} · " + (f"so với {span(H['ago_runs'])}" if cmp else "chưa có mốc so sánh")
    if not tpls:
        raise SystemExit("hang.json chưa có template: chạy qp_ranks.py table với --rules trước.")
    if len(tpls) > 16:
        raise SystemExit(f"hang.json có {len(tpls)} template, deck nhận tối đa 16. Gộp template nhỏ trong rules.json rồi chạy lại "
                         "qp_ranks.py table (không cắt bớt: keyword của template bị cắt sẽ mất khỏi deck).")
    if len(tpls) < 5:
        print(f"Cảnh báo: chỉ có {len(tpls)} template, deck cần 5–16. Tách template lớn trong rules.json nếu được.")
    tpls = sorted(tpls, key=score, reverse=True)
    by_tpl = {}
    for r in kws:
        by_tpl.setdefault(r["tpl"], []).append(r)
    rules = {x["id"]: x for x in H.get("rules", [])}
    gdf = Counter(w.lower() for r in kws for w in set(r["kw"].split()))
    head = {w for w, c in gdf.items() if c >= 0.5 * max(1, len(kws))}
    hubs = H.get("hub_urls") or [["/", 0, 0]]

    items = []
    for t in tpls:
        st = status(t)
        t10n = t["now"]["t3"] + t["now"]["t10"]
        note = f"Top 10: {t['ago']['t3'] + t['ago']['t10']} → {t10n}" if cmp and t.get("ago") else f"Top 10 hiện tại: {t10n}"
        items.append({"id": t["id"], "label": t["label"][:40], "n": t["n"], "now": t["now"], "ago": t.get("ago") if cmp else None,
                      "status": st, "status_label": STATUS[st], "note": f"{note}; hạng 11–20: {t['now']['t20']}"[:62]})

    ids = [t["id"] for t in tpls]
    tab_ids = [x for x in a.tabs.split(",") if x] or [i for i in ids if i not in ("khac", "other")][:3]
    if set(tab_ids) - set(ids):
        sys.exit(f"--tabs có id không có trong bảng hạng: {sorted(set(tab_ids) - set(ids))}. Id đang có: {ids}")
    tabs = []
    for tid in tab_ids:
        t = next(x for x in tpls if x["id"] == tid)
        rs = sorted(by_tpl.get(tid, []), key=lambda r: (r["now"] is None, r["now"] or 0))[:12]
        common = head  # chỉ bỏ phần đầu chung của cả bộ, giữ chữ phân biệt biến thể
        b, s = base_slot(t["label"])
        tabs.append({"id": tid, "base": b[:30], "slot": s[:18] or "[biến]",
                     "chips": [{"label": chip_label(r["kw"], common), "kw": r["kw"], "now": ceil_rank(r["now"]), "ago": ceil_rank(r["ago"])} for r in rs]
                              + [{"label": "TODO", "kw": "TODO: thêm keyword", "now": None, "ago": None}] * max(0, 4 - len(rs)),
                     "read": TD + "lưới cho thấy biến thể nào đã thắng, biến thể nào kẹt (≤260 ký tự)",
                     "act": TD + "việc làm trên URL đại diện của template này", "topic": TD + "T? · P? · công sức nhỏ/vừa/lớn"})

    regex = []
    for t in tpls[:6]:
        rx = rules.get(t["id"], {}).get("rx", "")
        if t["id"] in ("khac", "other") or rx in ("", "."):
            continue
        rx = rx if rx.startswith("(?i)") else "(?i)" + rx
        regex.append({"name": t["label"][:40], "rx": rx if re2_ok(rx) and len(rx) <= 110 else TD + "regex RE2 cho template " + t["id"]})
    while len(regex) < 3:
        regex.append({"name": TD + "template", "rx": TD + "regex RE2"})

    flags = [{"slide": "Đo", "text": f"Lần chạy bị loại: {r['date']} ({r['why']})."} for r in H["runs"] if not r["valid"]][:6]
    if H.get("not_in_export"):
        flags.append({"slide": "Template", "text": f"{len(H['not_in_export'])} keyword trong bộ cam kết không có trong export SpySERP."})
    if H.get("unmatched"):
        flags.append({"slide": "Template", "text": f"{len(H['unmatched'])} keyword chưa có template."})
    if not cmp:
        flags.append({"slide": "Template", "text": "Chưa có mốc so sánh: export không có lần chạy hợp lệ quanh mốc 4 tuần trước. "
                                                   "Deck bỏ cột so sánh và không gắn trạng thái Đang lan."})
    for t in H.get("targets") or []:
        if t["other_url"]:
            flags.append({"slide": "Canonical", "text": f"{t['other_url']}/{t['n']} keyword của URL target {t['url']} đang được Google trả về URL khác."})

    P = {
        "schema": "qp-project/1", "slug": a.slug, "name": a.name, "name_lines": split_name(a.name),
        "domain": a.domain, "lead": a.lead,
        "measure": {"has_rank": True, "tool": "SpySERP", "project": str(H.get("project") or ""), "engine": H["engine"],
                    "engine_label": TD + "thiết bị, vị trí đo (đọc engine_config: " + (H.get("engine_config") or "")[:80] + ")",
                    "date": d_vn(H["now_runs"][0]), "compare_date": d_vn(H["ago_runs"][0]) if cmp else "", "depth": H["depth"]},
        "status_row": {"set": f"{H['n_keywords']} keyword ({H['engine']})", "now": f"Top 3/5/10 = {t3}/{t5}/{t10}"},
        "kpi": {"target": TD + "mốc nghiệm thu gần nhất (nội bộ)", "gap": TD + "khoảng cách tới mốc", "risk": TD + "Cao | Vừa", "beat_stats": []},
        "headline": {"template": items[0]["label"][:44], "fact": TD + "một câu bằng chứng (≤70 ký tự)"},
        "cover": {"query": TD + "keyword khách gõ thật", "tokens": [{"t": TD + "mảnh", "r": "vai trò", "k": "known"}, {"t": TD + "mảnh", "r": "vai trò", "k": "op"}],
                  "rep": TD + "query đại diện", "rep_sub": TD + "bao nhiêu keyword cam kết đi theo query này"},
        "idea": {"n_kw": H["n_keywords"], "n_tpl": len(items), "hub_url": hubs[0][0], "hub_n": hubs[0][1], "hub_top10": hubs[0][2],
                 "mechanism": "Patent US8645407B2 mô tả việc gom các query gần nghĩa thành cụm và lấy tâm cụm làm gợi ý tìm kiếm. Giả thuyết: Google dùng tâm cụm làm query đại diện, trang khớp query đó nhận relevance cho cả họ.",
                 "effect": "Đẩy đúng một query đại diện có thể kéo nhiều keyword cam kết cùng lúc. Một lỗi ở một trạm cũng có thể làm rơi cả họ keyword.", "src": src},
        "beat_stats": [[str(H["n_keywords"]), "keyword cam kết"], [f"{t3}/{t5}/{t10}", f"Top 3/5/10 ({'median ' + str(k) + ' lần' if k > 1 else d_vn(H['now_runs'][0])})"]],
        "templates": {"title": f"{len(items)} template: <g>{items[0]['label'][:30]}</g> đáng đẩy nhất", "src": src + " · gom bằng rules.json", "items": items},
        "grid": {"title": "Lưới hạng: biến thể nào <g>đã thắng</g>", "src": src, "tabs": tabs},
        "canonical": {"rows": [{"query": TD + "query đại diện", "google": f"{u} · giữ {n} keyword, {t} Top 10", "problem": TD + "vì sao chưa ổn",
                                "decision": TD + "URL đại diện + việc kèm theo", "tag": TD + "T?"} for u, n, t in (hubs + [["TODO", 0, 0]] * 3)[:3]],
                      "rules": ["Giữ URL Google đang chọn nếu URL đó đã vào Top 10.", "Chỉ gom hai URL khi có bằng chứng hai URL tranh nhau."],
                      "flip": {"label": "Khi Google lật URL", "steps": ["Ghi hai URL và ngày lật.", "Kiểm canonical, internal link và anchor trỏ về mỗi URL.",
                                                                       "Chọn URL đại diện theo loại trang của SERP.", "Dồn anchor về URL đó, chờ 14 ngày rồi đọc median."]},
                      "src": src},
        "serp": {"src": TD + "nguồn SERP và ngày", "cards": [{"query": TD + f"query đại diện intent {i + 1}", "meta": TD + "nguồn · thị trường · ngày",
                                                             "rows": [{"p": j + 1, "type": "TODO", "cls": "other", "domain": "TODO"} for j in range(6)],
                                                             "verdict": TD + "intent + loại trang Google muốn", "so": TD + "Vì vậy: …"} for i in range(3)]},
        "matrix": {"src": src + " · trang thật GET " + TD + "ngày", "rows": [{"name": t["label"][:36], "topic": "T?", "stages": {},
                                                                              "stat": f"{t['n']} keyword · Top 10 = {t['now']['t3'] + t['now']['t10']}"[:90],
                                                                              "diag": TD + "chẩn đoán từ trang thật", "fix": TD + "việc sửa"}
                                                                             for t in tpls if t["id"] not in ("khac", "other")][:max(5, min(8, len(tpls)))]},
        "levers": {"title": "Ngoài chữ: <g>4 nhóm việc</g> đi kèm", "src": TD + "site_check ngày …",
                   "cols": [{"label": c, "items": [{"k": "Kỹ thuật", "text": TD + "dữ kiện trang thật + việc"}, {"k": "Ranking", "text": TD + "dữ kiện trang thật + việc"}]}
                            for c in ("Internal link", "Hình ảnh", "Chức năng", "Schema")],
                   "dont": ["Không hứa hạng cho slideshow hay FAQPage.", "Không thêm link sitewide chỉ để đẩy hạng."]},
        "priority": {"src": src, "rows": [{"id": f"T{i + 1}", "template": TD + "template", "evidence": TD + "bằng chứng", "why": TD + "vì sao xếp ở đây",
                                           "n_kw": 0, "stages": TD + "B?", "pri": "P1", "when": TD + "thời điểm"} for i in range(4)]},
        "measure_slide": {"intro": "Dán regex vào bộ lọc query của GSC để đọc cả họ keyword. SpySERP nhóm theo cùng template.",
                          "why": "Google xử lý cả họ query, nên hạng lên xuống theo họ. Đọc từng keyword dễ nhầm dao động thành kết quả.",
                          "regex": regex,
                          "timeline": [{"d": "Tuần 0", "t": "Chụp baseline hạng và GSC, mở nhật ký thay đổi theo URL."},
                                       {"d": "+14 ngày", "t": "Đọc median các lần chạy hợp lệ của từng template."},
                                       {"d": TD + "ngày đo", "t": TD + "kỳ đo tiếp theo: trang Top 3/5 chỉ thêm, không rút."}],
                          "rule": {"label": "Luật đọc số", "text": "Bỏ lần chạy thiếu dữ liệu. Đọc median các lần chạy hợp lệ, không đọc số của một ngày."},
                          "src": src},
        "plan": {"who": a.lead or TD + "Lead", "period": a.period or TD + "dd–dd/mm", "title": "Kế hoạch hành động",
                 "rows": [{"when": TD + "ngày", "task": TD + "việc cụ thể", "who": TD + "ai", "done": TD + "xong khi"} for _ in range(5)],
                 "cards": [{"label": "Nhắc", "text": "Trước kỳ đo, trang đang giữ Top 3 hoặc Top 5 chỉ thêm nội dung, không rút."}], "src": src},
        "flags": flags, "guides": {},
        "gloss": {str(H.get("project") or "SpySERP"): f"Project SpySERP đo bộ keyword cam kết, engine {H['engine']}."} if H.get("project") else {},
    }
    out.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
    todo = json.dumps(P, ensure_ascii=False).count("TODO")
    print(f"{out}: {len(items)} template, {len(tabs)} tab lưới, {len(regex)} regex nháp, {len(flags)} flag · còn {todo} chỗ TODO")
    print("Tiếp: viết các ô TODO (xoá khối tuỳ chọn không dùng: levers/aug/pairs/retrieve/qa), rồi chạy qp_build.py.")


if __name__ == "__main__":
    main()
