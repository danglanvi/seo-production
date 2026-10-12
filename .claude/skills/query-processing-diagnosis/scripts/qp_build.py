#!/usr/bin/env python3
"""Một lệnh cho toàn bộ khâu kiểm và dựng: check → verify (đối chiếu số với bảng hạng) → dựng deck → quét bản web → audit → chụp.

  python3 qp_build.py <du-an.json> [--ranks hang.json] [--topics topics.json] [--out deck.html]
                      [--web-out deck_web.html] [--handoff <CLIENT>_qp-handoff-content_v<N>.md] [--numbers con-so-nguon.md]
                      [--shots <thư mục> [--slides 13,14,15]] [--no-audit]

- check: schema, giới hạn độ dài, regex RE2, chữ cấm, còn TODO (qp_render.check).
- verify (khi có --ranks): số trên deck khớp hang.json của qp_ranks.py:
    lỗi   — idea.n_kw, idea.n_tpl, tổng n của các template = số keyword, measure.engine/depth/date/compare_date,
            templates n/now/ago, ghi chú "Top 10: a → b" của template, trạng thái "Đang lan" không khớp số,
            keyword trên chip/aug/pairs/retrieve không có trong bộ hoặc hạng khác median (median_high),
            topic: n_kw khác danh sách, keyword thuộc hai topic, keyword ngoài bộ (khi có --topics).
    cảnh báo — hạng chỉ khớp một lần chạy (không khớp median), trạng thái khác gợi ý, Top 3/5/10 ghi trong chữ khác median,
            hạng ghi trong chữ ("keyword" #n) khác bảng hạng, vol khác cột Volume của SpySERP, hub_url ngoài 10 URL hub.
  topics.json: {"T1": ["keyword", ...], "T2": [...]}
- dựng: bản nội bộ (mặc định cùng tên file JSON, đuôi .html); bản --web nếu có --web-out, kèm quét chữ có thể lộ điều khoản
  hợp đồng (chỉ tiêu, nghiệm thu, phụ lục, gia hạn...) trong phần bản web hiện ra. Mỗi chỗ trúng phải đọc lại.
- --handoff: file bàn giao cho team content (template, URL Google chọn, topic + keyword, trạm hỏng, SERP, regex). Cần --ranks.
- --numbers: bảng "con số → nguồn → cách tính" cho hồ sơ mục 2. Cần --ranks.
- audit: cần Node ≥22 và Chrome; thiếu thì bỏ qua và in lý do. --shots không kèm --slides thì chụp slide Template, Ưu tiên, Kế hoạch.
Dừng ở khâu đầu tiên có lỗi. Thoát mã 0 khi mọi khâu đạt.
"""
import argparse, copy, json, math, re, shutil, subprocess, sys
from datetime import date
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
import qp_render as Q  # noqa: E402
from qp_scaffold import status as tpl_status, d_vn  # noqa: E402

# Cụm có thể lộ điều khoản hợp đồng trên bản web (rút từ lệnh quét của site đào tạo, đợt 10/2026). Trúng = đọc lại, không tự chặn.
RISKY = ["chỉ tiêu", "nghiệm thu", "khoảng cách tới", "còn thiếu", r"thiếu \d", "quá hạn", "hết hạn", "phụ lục", "thanh lý",
         "gia hạn", r"\bKPI\b", "chưa ký", "bản ký", "đàm phán", "hợp đồng", r"\bPBN\b"]
SHOT_TITLES = ("Template", "Ưu tiên", "Kế hoạch", "2 tuần")
CONTENT_STAGES = {"B2", "B3", "B6", "B8"}


def median_ok(r, key):
    m = r.get(key)
    return {None if m is None else int(math.ceil(m))}


def raw_runs(r):
    return {v for v in (r.get("series") or {}).values() if v not in ("x", None)}


def strings(o, path=""):
    """Mọi chuỗi chữ tự do trong JSON (bỏ trường định danh, keyword, regex)."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in ("kw", "rx", "url", "slug", "domain", "id", "schema", "lead", "engine", "tool", "hub_url"):
                yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


def verify(P, H, topics):
    err, warn = [], []
    K = {r["kw"].lower(): r for r in H["keywords"]}
    cmp = bool(H.get("ago_runs")) and H.get("compare", True)
    nk = int(re.sub(r"\D", "", str(P["idea"].get("n_kw", ""))) or -1)
    if nk != H["n_keywords"]:
        err.append(f"idea.n_kw = {nk}, bảng hạng có {H['n_keywords']} keyword")
    items = P["templates"]["items"]
    if int(P["idea"].get("n_tpl", -1)) != len(items):
        err.append(f"idea.n_tpl = {P['idea'].get('n_tpl')}, slide Template có {len(items)} template")
    if sum(int(x["n"]) for x in items) != H["n_keywords"]:
        err.append(f"templates: tổng n = {sum(int(x['n']) for x in items)}, bảng hạng có {H['n_keywords']} keyword "
                   "(template bị cắt hoặc thiếu; gộp rule trong rules.json thay vì bỏ template)")
    m = P["measure"]
    if m.get("engine") != H["engine"]:
        err.append(f"measure.engine = {m.get('engine')}, bảng hạng đo {H['engine']}")
    if int(m.get("depth") or 0) != H["depth"]:
        err.append(f"measure.depth = {m.get('depth')}, bảng hạng có độ sâu {H['depth']}")
    if m.get("date") and m["date"] != d_vn(H["now_runs"][0]):
        err.append(f"measure.date = {m['date']}, lần chạy mới nhất dùng cho số hiện tại là {d_vn(H['now_runs'][0])}")
    if cmp and m.get("compare_date") not in {d_vn(x) for x in H["ago_runs"]}:
        err.append(f"measure.compare_date = {m.get('compare_date')!r}, mốc so sánh của bảng hạng: {sorted({d_vn(x) for x in H['ago_runs']})}")
    if not cmp and m.get("compare_date"):
        err.append(f"measure.compare_date = {m['compare_date']}, bảng hạng chạy --no-compare (không có mốc so sánh)")
    T = {t["id"]: t for t in H["templates"]}
    for x in items:
        t = T.get(x["id"])
        if not t:
            warn.append(f"templates.{x['id']}: không có trong bảng hạng (rules.json đổi id?)")
            continue
        for k in ("n", "now", "ago"):
            if x.get(k) != t.get(k):
                err.append(f"templates.{x['id']}.{k} = {x.get(k)}, bảng hạng: {t.get(k)}")
        want = tpl_status(t)
        if x["status"] == "up" and want != "up":
            err.append(f"templates.{x['id']}.status = up (Đang lan) nhưng số không đủ: "
                       + (f"Top 10 {t['ago']['t3'] + t['ago']['t10']} → {t['now']['t3'] + t['now']['t10']}" if t.get("ago") else "không có mốc so sánh"))
        elif x["status"] != want:
            warn.append(f"templates.{x['id']}.status = {x['status']}, số gợi ý {want}: ghi lý do vào tip nếu cố ý")
        t10n = t["now"]["t3"] + t["now"]["t10"]
        mm = re.search(r"Top 10[^\d]*(\d+)\s*→\s*(\d+)", Q.plain(x.get("note", "")))
        if mm and (not t.get("ago") or (int(mm.group(1)), int(mm.group(2))) != (t["ago"]["t3"] + t["ago"]["t10"], t10n)):
            err.append(f"templates.{x['id']}.note ghi Top 10 {mm.group(1)} → {mm.group(2)}, bảng hạng: "
                       + (f"{t['ago']['t3'] + t['ago']['t10']} → {t10n}" if t.get("ago") else f"{t10n} (không có mốc so sánh)"))

    def kw_check(path, k, has_ago=True):
        r = K.get(str(k.get("kw", "")).lower())
        if not r:
            err.append(f"{path}: “{k.get('kw')}” không có trong bộ keyword của bảng hạng")
            return
        for key in ("now", "ago") if has_ago else ("now",):
            if key not in k:
                continue
            v = k.get(key)
            if v in median_ok(r, key):
                continue
            if key == "now" and v in raw_runs(r):
                warn.append(f"{path}: “{r['kw']}” now = {v} là hạng một lần chạy, median = {r['now']}. Dùng median, hoặc ghi rõ ngày trong tip")
            else:
                err.append(f"{path}: “{r['kw']}” {key} = {v}, bảng hạng cho {r.get(key) or 'ngoài độ sâu'}")
        if k.get("vol") not in (None, "", r.get("vol")) and r.get("vol"):
            warn.append(f"{path}: “{r['kw']}” vol = {k.get('vol')}, Volume SpySERP = {r['vol']} (ghi nguồn volume nếu cố ý)")

    for i, tab in enumerate(P["grid"]["tabs"]):
        for j, c in enumerate(tab["chips"]):
            kw_check(f"grid.tabs[{i}].chips[{j}]", c)
    for i, c in enumerate((P.get("aug") or {}).get("components", [])):
        for j, k in enumerate(c["kws"]):
            kw_check(f"aug.components[{i}].kws[{j}]", k, False)
    for i, c in enumerate((P.get("pairs") or {}).get("items", [])):
        for j, k in enumerate(c["kws"]):
            kw_check(f"pairs.items[{i}].kws[{j}]", k, False)
    for i, c in enumerate((P.get("retrieve") or {}).get("rows", [])):
        for j, k in enumerate(c["kws"]):
            kw_check(f"retrieve.rows[{i}].kws[{j}]", k, False)

    tp = H["tops"]["now"]
    want = "/".join(str(tp.get(str(n), tp.get(n))) for n in (3, 5, 10))
    texts = list(strings({k: v for k, v in P.items() if k not in ("kpi", "flags")}))
    texts += [(f"beat_stats[{i}]", " ".join(map(str, b))) for i, b in enumerate(P["beat_stats"])]
    for path, s in texts:
        s = Q.plain(s)
        mm = re.search(r"Top 3/5/10[^0-9]*(\d+/\d+/\d+)|(\d+/\d+/\d+)[^0-9]*Top 3/5/10", s)
        got = mm and (mm.group(1) or mm.group(2))
        if got and got != want:
            warn.append(f"{path}: Top 3/5/10 = {got}, median bảng hạng = {want} (ghi rõ nếu cố ý dùng số một ngày)")
        low = s.lower()
        for kw, r in K.items():
            if kw not in low:
                continue
            for mm in re.finditer(re.escape(kw) + r"[”\"'’)]?\s*[:(,–-]?\s*(?:#|hạng\s+)(\d{1,3})\b", low):
                v = int(mm.group(1))
                if v not in median_ok(r, "now") | raw_runs(r) | median_ok(r, "ago"):
                    warn.append(f"{path}: “{r['kw']}” ghi hạng {v} trong chữ, bảng hạng: nay {r['now'] or 'ngoài độ sâu'}"
                                + (f", mốc so sánh {r['ago'] or 'ngoài độ sâu'}" if cmp else ""))
    if P["idea"].get("hub_url") and P["idea"]["hub_url"] not in [u for u, _, _ in H.get("hub_urls", [])]:
        warn.append(f"idea.hub_url {P['idea']['hub_url']} không nằm trong 10 URL hub của bảng hạng")

    if topics:
        owner = {}
        for tid, ks in topics.items():
            for k in ks:
                if k.lower() not in K:
                    err.append(f"topics.{tid}: “{k}” không có trong bộ keyword")
                if k.lower() in owner and owner[k.lower()] != tid:
                    err.append(f"“{k}” thuộc cả {owner[k.lower()]} và {tid}")
                owner[k.lower()] = tid
        for x in P["priority"]["rows"]:
            if x["id"] in topics:
                if int(x["n_kw"]) != len(topics[x["id"]]):
                    err.append(f"priority.{x['id']}.n_kw = {x['n_kw']}, topics.json có {len(topics[x['id']])} keyword")
            elif x["id"] != "mới":
                warn.append(f"priority.{x['id']}: không có trong topics.json")
    elif P["priority"]["rows"]:
        warn.append("chưa có --topics: không kiểm được n_kw và keyword trùng giữa topic (checklist QP-06)")
    return err, warn


def web_view(P):
    """Phần JSON mà bản --web hiện ra: bỏ kpi, flags và thẻ kế hoạch internal."""
    W = copy.deepcopy({k: v for k, v in P.items() if k not in ("kpi", "flags")})
    W["plan"]["cards"] = [c for c in W["plan"].get("cards", []) if not c.get("internal")]
    return W


def risky_scan(P):
    txt = " ".join(Q.plain(s) for _, s in strings(web_view(P)))
    hits = []
    for w in RISKY:
        for mm in re.finditer(w, txt, re.I):
            hits.append(f"[{w}] …{txt[max(0, mm.start() - 60):mm.end() + 60]}…")
    return hits


def tpl_url(H):
    """URL Google đang trả nhiều nhất cho keyword của mỗi template."""
    out = {}
    for r in H["keywords"]:
        if r.get("tpl") and r.get("url"):
            out.setdefault(r["tpl"], {}).setdefault(r["url"], 0)
            out[r["tpl"]][r["url"]] += 1
    return {t: max(c.items(), key=lambda x: x[1]) for t, c in out.items()}


def md(s):
    return Q.plain(s).replace("|", "/").replace("\n", " ").strip()


def handoff(P, H, topics, src_json):
    cmp = bool(H.get("ago_runs")) and H.get("compare", True)
    tu = tpl_url(H)
    owner = {k.lower(): tid for tid, ks in (topics or {}).items() for k in ks}
    m = P["measure"]
    L = ["---", "type: qp-handoff-content", f"client: {P['name']}", f"domain: {P['domain']}", f"deck_json: {Path(src_json).name}",
         f"engine: {H['engine']}", f"do_luc: {m.get('date')}", f"moc_so_sanh: {m.get('compare_date') or 'không có'}",
         f"do_sau: {H['depth']}", f"sinh_ngay: {date.today().isoformat()}", "---", "",
         f"# {P['name']}: bàn giao chẩn đoán Query Processing cho team content", "",
         f"> Sinh tự động bằng `qp_build.py --handoff` từ `{Path(src_json).name}`, `hang.json`, `topics.json`. Không sửa tay: "
         "sửa JSON ở repo SEO rồi dựng lại. Repo content đọc file này trong snapshot SEO (`project_sync.py pull`); "
         "cách dùng ở `_REFERENCE/query-processing.md` của repo content. Chữ \"cần GSC\", \"giả thuyết\" là điểm chưa kiểm chéo.", "",
         "## 1. Template và URL Google đang chọn", "",
         "| Template | Số keyword | Top 10 " + ("(mốc → nay)" if cmp else "(hiện tại)") + " | Trạng thái | URL Google trả nhiều nhất |",
         "|---|---|---|---|---|"]
    for x in P["templates"]["items"]:
        t10 = x["now"]["t3"] + x["now"]["t10"]
        tt = f"{x['ago']['t3'] + x['ago']['t10']} → {t10}" if x.get("ago") else str(t10)
        u = tu.get(x["id"])
        L.append(f"| {md(x['label'])} | {x['n']} | {tt} | {md(x['status_label'])} | {f'{u[0]} ({u[1]} keyword)' if u else '—'} |")
    L += ["", "## 2. Topic ưu tiên và keyword cam kết mỗi topic đẩy", "",
          "| Topic | Ưu tiên | Template | Trạm | Khi nào | Vì sao | Keyword cam kết |", "|---|---|---|---|---|---|---|"]
    for x in P["priority"]["rows"]:
        ks = (topics or {}).get(x["id"], [])
        L.append(f"| {x['id']} | {x['pri']} | {md(x['template'])} | {md(x['stages'])} | {md(x['when'])} | {md(x.get('why', ''))} | "
                 f"{len(ks)}: {', '.join(ks) if ks else '—'} |")
    L += ["", "## 3. Canonical: một query đại diện, một URL", "",
          "| Query đại diện | URL Google đang chọn | Vấn đề | Quyết định | Topic |", "|---|---|---|---|---|"]
    for x in P["canonical"]["rows"]:
        L.append(f"| {md(x['query'])} | {md(x['google'])} | {md(x['problem'])} | {md(x['decision'])} | {md(x['tag'])} |")
    L += ["", "## 4. Trạm hỏng theo cụm", "",
          "Trạm B2 (segment), B3 (biến thể), B6 (câu hỏi), B8 (passage) là việc team content làm được. "
          "B4 (canonical), B5 (context), B7 (retrieve) là việc của team SEO và dev: sửa trạm đó trước, chưa viết thêm nội dung.", "",
          "| Cụm | Trạm chính | Trạm phụ | Việc sửa | Team content làm? |", "|---|---|---|---|---|"]
    for x in P["matrix"]["rows"]:
        main = [k for k, v in x["stages"].items() if int(v) == 2]
        sub = [k for k, v in x["stages"].items() if int(v) == 1]
        mine = "Có" if set(main) & CONTENT_STAGES and not set(main) & {"B4", "B7"} else "Chờ team SEO sửa trước" if set(main) & {"B4", "B7"} else "Không"
        L.append(f"| {md(x['name'])} | {', '.join(main) or '—'} | {', '.join(sub) or '—'} | {md(x.get('fix', ''))} | {mine} |")
    L += ["", "## 5. SERP: loại trang Google muốn", "", "| Query | Kết luận | Vì vậy |", "|---|---|---|"]
    for x in P["serp"]["cards"]:
        L.append(f"| {md(x['query'])} | {md(x['verdict'])} | {md(x.get('so', ''))} |")
    L += ["", "## 6. Regex đo trong GSC", "", "| Template | Regex |", "|---|---|"]
    for x in P["measure_slide"]["regex"]:
        L.append(f"| {md(x['name'])} | `{x['rx']}` |")
    fl = [f for f in P.get("flags", [])]
    if fl:
        L += ["", "## 7. Điểm cần kiểm tay", ""] + [f"- {md(f['slide'])}: {md(f['text'])}" for f in fl]
    L += ["", "## 8. Tra keyword: template, URL Google trả, hạng, topic", "",
          "Tra bằng tìm chữ (Ctrl+F hoặc grep), không đọc hết bảng. Hạng là median các lần chạy hợp lệ; trống = ngoài độ sâu đo.", "",
          "| Keyword | Template | URL Google trả | Hạng nay | Topic |", "|---|---|---|---|---|"]
    for r in sorted(H["keywords"], key=lambda r: (r.get("tpl") or "~", r["now"] if r["now"] is not None else 999)):
        L.append(f"| {r['kw']} | {r.get('tpl') or '—'} | {r.get('url') or '—'} | {r['now'] if r['now'] is not None else ''} | {owner.get(r['kw'].lower(), '')} |")
    return "\n".join(L) + "\n"


def numbers(P, H, topics, src_json):
    src = H["source"] if isinstance(H["source"], str) else ", ".join(H["source"])
    base = f"{src} · {H['engine']} · {H['mode']}"
    cmp = bool(H.get("ago_runs")) and H.get("compare", True)
    tp, ta = H["tops"]["now"], H["tops"].get("ago")
    g = lambda d, n: d.get(str(n), d.get(n))
    now_s = ", ".join(H["now_runs"])
    L = ["| Con số trên deck | Slide | Nguồn (file, engine, ngày) | Cách tính |", "|---|---|---|---|",
         f"| {H['n_keywords']} keyword | Ý tưởng, Template | {base} · bộ cam kết `bo-cam-ket.txt` | `qp_ranks.py table --keywords` |",
         f"| Top 3/5/10 = {g(tp, 3)}/{g(tp, 5)}/{g(tp, 10)} | mở dự án, bảng tổng quan | {base} · {now_s} | median {len(H['now_runs'])} lần hợp lệ (median_high) |"]
    if cmp and ta:
        L.append(f"| Top 3/5/10 mốc so sánh = {g(ta, 3)}/{g(ta, 5)}/{g(ta, 10)} | Template | {base} · {', '.join(H['ago_runs'])} | median quanh {H.get('compare_target')} (±7 ngày) |")
    L.append(f"| Độ sâu {H['depth']} | mọi slide | {base} | lệnh `runs`: hạng lớn nhất thấy được |")
    bad = [r for r in H["runs"] if not r["valid"]]
    if bad:
        L.append(f"| {len(bad)} lần chạy bị loại | Đo | {base} | lệnh `runs`: " + "; ".join(f"{r['date']} ({r['why']})" for r in bad[:8]) + " |")
    for x in P["templates"]["items"]:
        L.append(f"| {md(x['label'])}: n={x['n']}, Top 10 nay {x['now']['t3'] + x['now']['t10']} | Template | {base} | rule `{x['id']}` trong `rules.json` |")
    if P["idea"].get("hub_url"):
        L.append(f"| URL hub {P['idea']['hub_url']}: {P['idea'].get('hub_n')} keyword, {P['idea'].get('hub_top10')} Top 10 | Ý tưởng | {base} · cột SERP Url lần chạy mới nhất | `hub_urls` của bảng hạng |")
    for tid, ks in (topics or {}).items():
        L.append(f"| {tid}: {len(ks)} keyword | Ưu tiên | `topics.json` | `qp_build.py --topics` (không keyword nào thuộc hai topic) |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json")
    ap.add_argument("--ranks")
    ap.add_argument("--topics")
    ap.add_argument("--out")
    ap.add_argument("--web-out")
    ap.add_argument("--handoff")
    ap.add_argument("--numbers")
    ap.add_argument("--shots")
    ap.add_argument("--slides", default="")
    ap.add_argument("--no-audit", action="store_true")
    a = ap.parse_args()
    P = json.loads(Path(a.json).read_text(encoding="utf-8"))

    errs = Q.check(P)
    print(f"1. check: {'OK' if not errs else str(len(errs)) + ' lỗi'}")
    for x in errs[:60]:
        print("   -", x)
    if errs:
        sys.exit(1)

    H = json.loads(Path(a.ranks).read_text(encoding="utf-8")) if a.ranks else None
    topics = json.loads(Path(a.topics).read_text(encoding="utf-8")) if a.topics else None
    if H:
        e, w = verify(P, H, topics)
        print(f"2. verify: {len(e)} lỗi, {len(w)} cảnh báo")
        for x in e[:60]:
            print("   - LỖI", x)
        for x in w[:30]:
            print("   - cảnh báo", x)
        if e:
            sys.exit(1)
    else:
        print("2. verify: bỏ qua (chưa có --ranks)")
        if a.handoff or a.numbers:
            sys.exit("--handoff và --numbers cần --ranks hang.json")

    PM = Q._mark(P)
    out = Path(a.out or Path(a.json).with_suffix(".html"))
    out.write_text(Q.build_project(PM, False), encoding="utf-8")
    html_text = out.read_text(encoding="utf-8")
    titles = re.findall(r'<section class="slide[^"]*" data-title="([^"]*)"', html_text)
    msg = f"3. dựng: {out} ({len(titles)} slide)"
    if a.web_out:
        Path(a.web_out).write_text(Q.build_project(PM, True), encoding="utf-8")
        msg += f" · bản --web: {a.web_out}"
    print(msg)
    if a.web_out:
        hits = risky_scan(P)
        print(f"   bản web: {len(hits)} chỗ có chữ dễ lộ điều khoản hợp đồng" + (" (đọc lại từng chỗ, sửa nếu lộ chỉ tiêu, mốc, hạn)" if hits else ""))
        for x in hits[:30]:
            print("    ", x)
    if a.handoff:
        Path(a.handoff).write_text(handoff(P, H, topics, a.json), encoding="utf-8")
        print(f"   bàn giao content: {a.handoff}")
    if a.numbers:
        Path(a.numbers).write_text(numbers(P, H, topics, a.json), encoding="utf-8")
        print(f"   con số → nguồn: {a.numbers}")

    if a.no_audit:
        print("4. audit: bỏ qua (--no-audit)")
    elif not shutil.which("node"):
        print("4. audit: bỏ qua (không có Node). Ghi lý do vào hồ sơ mục 4.")
    else:
        r = subprocess.run([sys.executable, str(D / "audit.py"), str(out)], capture_output=True, text=True, timeout=200)
        lines = [x for x in r.stdout.splitlines() if x.strip()]
        print("4. " + (lines[-1] if lines else "audit: không có kết quả " + r.stderr[-200:]))
        for x in lines[:-1][:20]:
            print("   ", x)
        if r.returncode == 1:
            sys.exit(1)
    if a.shots and shutil.which("node"):
        nums = [x for x in a.slides.split(",") if x] or [str(i + 1) for i, t in enumerate(titles) if t in SHOT_TITLES]
        r = subprocess.run(["node", str(D / "cdp.mjs"), "shots", str(out), a.shots, *nums], capture_output=True, text=True, timeout=200)
        print(f"5. chụp slide {','.join(nums)}: " + (r.stdout.strip() or r.stderr.strip()[-200:]))


if __name__ == "__main__":
    main()
