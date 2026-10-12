#!/usr/bin/env python3
"""Đọc hạng bộ keyword cam kết từ SpySERP, lọc lần chạy lỗi, tính median, gom theo query template.

  python3 qp_ranks.py bo    <file.csv|.tsv|.txt> [--col "Keyword"] [--where "Nhóm=Thúc đẩy"] -o bo-cam-ket.txt
                            # trích bộ keyword cam kết từ một cột của file (CSV tải từ sheet KPI cũng được)
  python3 qp_ranks.py runs  <nguồn> [<nguồn> ...] --domain <domain> [--engine GM1] [--project <id|tên>]
  python3 qp_ranks.py terms <nguồn> ... --domain <domain> [--engine GM1] [--keywords bo-cam-ket.txt] [--rules rules.json]
                            # gợi ý ô biến để viết rules.json: cụm từ lặp nhiều nhất + số keyword Top 10 của mỗi cụm
  python3 qp_ranks.py table <nguồn> ... --domain <domain> [--engine GM1] [--project <id|tên>]
                            [--keywords bo-cam-ket.txt] [--rules rules.json] [--targets url-target.csv] [--k 3]
                            [--now-runs "09.10.2026 11:10,08.10.2026 08:41"] [--compare 11.09.2026 | --no-compare]
                            [--keep-recent] [--drop "05.10.2026 09:04,..."] [--max-missing 0.025] -o hang.json [--tsv hang.tsv]

<nguồn>: file CSV export của SpySERP (dấu ';', ',' hoặc tab: file tải lại từ Google Sheets cũng đọc được; có ~15 dòng meta
         trước header "Keywords") hoặc file JSON chuẩn hoá
         (schema 1: {"projects":[{id,name,dates,keywords[{keyword,tracks[{domain,engine,url,series}]}]}]}).
         Truyền nhiều file khi SpySERP chia lần chạy theo trang ("Schedules Page") hoặc chia keyword theo trang
         ("Keywords Page"): script gộp theo ngày và theo keyword. Ngày trùng thì lấy file có lần chạy mới hơn.
--keywords: bộ cam kết, mỗi dòng một keyword (tạo bằng lệnh bo). Lọc export theo bộ này, báo keyword có trong bộ mà thiếu.
--rules:   JSON [{"id","label","rx"}...] theo thứ tự ưu tiên khớp (regex Python, không phân biệt hoa thường).
           Keyword thuộc rule đầu tiên khớp. Nên có rule cuối "khac" với rx "." để mọi keyword có template.
--targets: URL target theo kế hoạch, mỗi dòng "keyword<tab hoặc , hoặc ;>URL". Lệnh đếm keyword Google trả URL khác kế hoạch.

Quy ước (đợt chẩn đoán 10 dự án, 10/2026):
- Hạng >=101, '>100', ô trống = ngoài độ sâu quét (null). Không phải hạng 101.
- Độ sâu quét của lần chạy = 50 nếu hạng lớn nhất thấy được <=50, ngược lại 100. Từ khoảng 25/09/2026 SpySERP chỉ quét 50.
- Project có nhiều domain (so sánh đối thủ): ô thiếu = keyword mà mọi domain cùng engine đều null ở lần chạy đó.
  Lần chạy hợp lệ khi tỷ lệ ô thiếu < --max-missing (mặc định 2,5% bộ keyword). Ô thiếu trong lần chạy hợp lệ bị bỏ riêng.
- Project một domain: không phân biệt được ô thiếu với ngoài độ sâu. Lần chạy có số keyword có hạng < 70% median các lần
  bị đánh dấu nghi thiếu và loại. Nếu lần bị loại nằm trong K lần mới nhất, lệnh table dừng (mã 3): site có thể rơi thật.
  Lead kiểm trên SpySERP rồi chọn --keep-recent (rơi thật, giữ lại) hoặc --drop (thiếu dữ liệu thật).
- "now" = median K lần chạy hợp lệ mới nhất (mặc định K=3); "ago" = median tối đa K lần chạy hợp lệ trong ±7 ngày quanh ngày
  so sánh (mặc định: lần mới nhất trừ 28 ngày). Không có lần nào trong khoảng đó thì table dừng (mã 2) và in cách xử lý;
  --no-compare chạy tiếp không có mốc so sánh (deck bỏ cột so sánh, không gắn trạng thái "Đang lan").
- Median lấy giá trị cao khi số giá trị chẵn (median_high), nên hạng luôn là số nguyên có thật. Hạng ngoài độ sâu tính là
  độ sâu+1 khi lấy median; median > độ sâu thì ghi null.
- Nhóm hạng cho slide Template: t3 (1–3), t10 (4–10), t20 (11–20), t50 (21–độ sâu), out (ngoài độ sâu).
- Cột Volume của SpySERP được đọc vào "vol". SpySERP ghi 0 khi chưa lấy volume: 0 không có nghĩa là không ai tìm.
Chỉ đọc file nguồn. Không gọi mạng.
"""
import argparse, csv, io, json, re, statistics, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}")
KW_COLS = {"keyword", "keywords", "từ khóa", "từ khoá", "keyword cam kết", "từ khóa cam kết", "từ khoá cam kết"}


def nfc(s):
    return unicodedata.normalize("NFC", str(s or "")).strip()


def pos(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v) if 1 <= v <= 100 else None
    v = str(v).strip()
    if not v or v in ("-", "—") or v.startswith(">"):
        return None
    try:
        n = int(v.replace(",", "").replace(".", ""))
    except ValueError:
        return None
    return n if 1 <= n <= 100 else None


def num(v):
    v = str(v or "").strip().replace(",", "").replace(".", "")
    return int(v) if v.isdigit() else None


def sniff(text, want):
    """Thử dấu ';', ',' và tab; chọn cách tách cho dòng header có ô thoả want(cell) dài nhất. Trả (rows, hi) hoặc (None, None)."""
    best = (None, None, -1)
    for d in (";", ",", "\t"):
        rows = list(csv.reader(io.StringIO(text), delimiter=d))
        hi = next((i for i, r in enumerate(rows) if any(want(nfc(c)) for c in r)), None)
        if hi is not None and len(rows[hi]) > best[2]:
            best = (rows, hi, len(rows[hi]))
    return best[0], best[1]


def dtt(s):
    """Ngày giờ của một lần chạy, dùng để xếp mới → cũ."""
    for f, n in (("%d.%m.%Y %H:%M", 16), ("%d.%m.%Y", 10)):
        try:
            return datetime.strptime(s.strip()[:n], f)
        except ValueError:
            pass
    return datetime.min


def read_csv(path):
    rows, hi = sniff(Path(path).read_text(encoding="utf-8-sig", errors="replace"), lambda c: c == "Keywords")
    if rows is None or rows[hi][0].strip() != "Keywords":
        sys.exit(f"{path}: không thấy dòng header 'Keywords' (đã thử dấu ; , và tab). File không phải export SpySERP?")
    meta = {}
    for r in rows[:hi]:
        c = [x.strip() for x in r if x.strip()]
        if c and c[0].startswith("Project:"):
            meta["name"] = c[0].split(":", 1)[1].strip()
        elif len(c) >= 2:
            meta[c[0]] = " | ".join(c[1:])
    hdr = [x.strip() for x in rows[hi]]
    col = {n: i for i, n in enumerate(hdr) if n}
    di = [i for i, h in enumerate(hdr) if DATE_RE.match(h)]
    kws, order = {}, []
    for r in rows[hi + 1:]:
        if not r or not r[0].strip():
            continue
        g = lambda n: r[col[n]].strip() if n in col and col[n] < len(r) else ""
        k = nfc(r[0])
        if k not in kws:
            kws[k] = {"keyword": k, "vol": None, "tracks": []}
            order.append(k)
        if kws[k]["vol"] is None and g("Volume"):
            kws[k]["vol"] = num(g("Volume"))
        kws[k]["tracks"].append({"domain": g("Domains"), "engine": g("Search engines"), "url": g("SERP Url"),
                                 "series": [r[i] if i < len(r) else "" for i in di]})
    pages = {k: v for k, v in meta.items() if k in ("Schedules Page", "Keywords Page")}
    return {"id": None, "name": meta.get("name", Path(path).name), "dates": [hdr[i] for i in di],
            "keywords": [kws[k] for k in order], "engine_config": meta.get("Search Engine", ""), "pages": pages, "file": str(path)}


def read_json(path, project):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ps = data.get("projects", data) if isinstance(data, dict) else data
    if project:
        ps = [p for p in ps if str(p.get("id")) == str(project) or project.lower() in str(p.get("name", "")).lower()]
    if len(ps) > 1 and len({str(p.get("id")) for p in ps}) == 1:
        # cùng project có bản một domain và bản so sánh đối thủ: lấy bản nhiều domain để phát hiện được ô thiếu
        ps = [max(ps, key=lambda p: len({t["domain"] for k in p.get("keywords", []) for t in k["tracks"]}))]
    if len(ps) != 1:
        names = [f'{p.get("id")} {p.get("name")} ({p.get("mode", "")}, {len(p.get("keywords", []))} keyword)' for p in ps]
        sys.exit("Cần chọn đúng một project bằng --project. Đang có:\n  " + "\n  ".join(names))
    p = dict(ps[0])
    p["keywords"] = [dict(k, keyword=nfc(k["keyword"]), vol=k.get("vol", k.get("volume"))) for k in p.get("keywords", [])]
    p.setdefault("pages", {})
    p["file"] = str(path)
    return p


def read_sources(paths, project):
    """Đọc một hay nhiều nguồn rồi gộp: ngày xếp mới → cũ, keyword và track hợp lại, ngày trùng lấy file mới hơn."""
    srcs = [read_csv(p) if str(p).lower().endswith((".csv", ".tsv")) else read_json(p, project) for p in paths]
    srcs.sort(key=lambda s: max(map(dtt, s["dates"]), default=datetime.min), reverse=True)
    dates = sorted({d for s in srcs for d in s["dates"]}, key=dtt, reverse=True)
    at = {d: i for i, d in enumerate(dates)}
    kws = {}
    for s in srcs:
        for k in s["keywords"]:
            K = kws.setdefault(k["keyword"], {"keyword": k["keyword"], "vol": None, "tracks": {}})
            if K["vol"] is None and k.get("vol") is not None:
                K["vol"] = k["vol"]
            for t in k["tracks"]:
                T = K["tracks"].setdefault((norm_dom(t["domain"]), t["engine"]),
                                           {"domain": t["domain"], "engine": t["engine"], "url": t.get("url") or "", "series": [""] * len(dates)})
                T["url"] = T["url"] or t.get("url") or ""
                for d, v in zip(s["dates"], t["series"]):
                    if T["series"][at[d]] in ("", None):
                        T["series"][at[d]] = v
    first = srcs[0]
    return {"id": first.get("id"), "name": first.get("name"), "dates": dates, "engine_config": first.get("engine_config", ""),
            "keywords": [dict(k, tracks=list(k["tracks"].values())) for k in kws.values()],
            "pages": [(Path(s["file"]).name, s["pages"]) for s in srcs if s.get("pages")], "files": [s["file"] for s in srcs]}


def dt(s):
    return datetime.strptime(s[:10], "%d.%m.%Y")


def stop(msg, code):
    """Dừng có mã riêng: 2 = thiếu mốc so sánh, 3 = gate nghiệp vụ hỏi Lead."""
    print(msg, file=sys.stderr)
    sys.exit(code)


def norm_dom(d):
    return d.lower().replace("www.", "").strip()


def norm_path(u):
    u = (u or "").strip()
    if not u:
        return ""
    p = urlsplit(u).path if "://" in u else u.split("?")[0]
    p = p.lower()
    return p.rstrip("/") or "/"


def build(src, domain, engine):
    engines = sorted({t["engine"] for k in src["keywords"] for t in k["tracks"] if t["engine"]})
    if not engine:
        if len(engines) > 1:
            sys.exit(f"Project có nhiều engine {engines}: chọn --engine theo hợp đồng.")
        engine = engines[0] if engines else ""
    own, others = {}, {}
    for k in src["keywords"]:
        tr = [t for t in k["tracks"] if not engine or t["engine"] == engine]
        mine = [t for t in tr if norm_dom(t["domain"]) == norm_dom(domain)]
        if not mine:
            continue
        own[k["keyword"]] = {"url": mine[0].get("url") or "", "s": [pos(v) for v in mine[0]["series"]], "vol": k.get("vol")}
        others[k["keyword"]] = [[pos(v) for v in t["series"]] for t in tr]
    if not own:
        doms = sorted({t["domain"] for k in src["keywords"] for t in k["tracks"]})
        sys.exit(f"Không thấy domain {domain} với engine {engine}. Domain có trong nguồn: {doms}")
    multi = max(len(v) for v in others.values()) > 1
    return src["dates"], engine, own, others, multi


def analyse_runs(dates, own, others, multi, max_missing, drop):
    n = len(own)
    ranked = [sum(1 for k in own if own[k]["s"][i]) for i in range(len(dates))]
    med_ranked = statistics.median([x for x in ranked if x] or [0])
    runs = []
    for i, d in enumerate(dates):
        allv = [v for k in others for s in others[k] for v in [s[i]] if v]
        depth = 50 if allv and max(allv) <= 50 else 100
        missing = sum(1 for k in others if all(s[i] is None for s in others[k])) if multi else None
        heur = False
        if d in drop:
            valid, why = False, "loại theo --drop"
        elif multi:
            valid = missing < max(1, max_missing * n)
            why = "" if valid else f"thiếu {missing}/{n} keyword"
        else:
            valid = ranked[i] >= 0.7 * med_ranked and ranked[i] > 0
            why = "" if valid else f"nghi thiếu: {ranked[i]} keyword có hạng, median các lần {med_ranked:g}"
            heur = not valid
        runs.append({"i": i, "date": d, "ranked": ranked[i], "missing": missing, "depth": depth, "valid": valid, "why": why, "heur": heur})
    return runs


def missing_cell(others, k, i, multi):
    return multi and all(s[i] is None for s in others[k])


def median_rank(own, others, k, idxs, depth, multi):
    vals = [own[k]["s"][i] or depth + 1 for i in idxs if not missing_cell(others, k, i, multi)]
    if not vals:
        return None
    m = statistics.median_high(vals)
    return None if m > depth else m


def bucket(p, depth):
    return "out" if p is None else "t3" if p <= 3 else "t10" if p <= 10 else "t20" if p <= 20 else "t50"


def span_note(src, dates):
    """Một dòng mô tả khoảng ngày của nguồn + cảnh báo khi SpySERP chia trang hoặc dưới 35 ngày."""
    if not dates:
        return ["  Nguồn không có cột ngày."]
    old, new = dtt(dates[-1]), dtt(dates[0])
    days = (new - old).days
    out = [f"  Nguồn: {len(src['files'])} file, {len(dates)} lần chạy từ {old:%d.%m.%Y} tới {new:%d.%m.%Y} ({days} ngày)"]
    if days < 35:
        out.append(f"  CẢNH BÁO: nguồn chỉ có {days} ngày (cần ≥35 ngày để có mốc so sánh 4 tuần).")
        for name, pg in src.get("pages") or []:
            if pg.get("Schedules Page"):
                out.append(f"  {name} ghi 'Schedules Page {pg['Schedules Page']}': SpySERP chia lần chạy theo trang. "
                           "Export thêm trang lịch cũ hơn (hoặc chọn khoảng ngày ≥35 ngày) rồi truyền mọi file vào cùng lệnh.")
    return out


def terms(a, own, others, multi, runs):
    """In cụm 1–2 âm tiết lặp nhiều nhất (bỏ phần đầu chung) để viết rules.json mà không phải đọc cả bộ keyword."""
    kws = list(own)
    if a.keywords:
        want = {nfc(x).lower() for x in Path(a.keywords).read_text(encoding="utf-8").splitlines() if x.strip()}
        kws = [k for k in kws if k.lower() in want]
    if a.rules:
        comp = [re.compile(x["rx"], re.I) for x in json.loads(Path(a.rules).read_text(encoding="utf-8")) if x["rx"] != "."]
        kws = [k for k in kws if not any(rx.search(k) for rx in comp)]
        print(f"Chỉ xét {len(kws)} keyword chưa khớp rule nào (bỏ rule '.')")
    valid = [r["i"] for r in runs if r["valid"]][:3]
    top10 = {k for k in kws if (median_rank(own, others, k, valid, 100, multi) or 999) <= 10}
    toks = {k: re.findall(r"[\w.+-]+", k.lower()) for k in kws}
    df = {}
    for k, ts in toks.items():
        for w in set(ts):
            df[w] = df.get(w, 0) + 1
    head = {w for w, c in df.items() if c >= 0.5 * max(1, len(kws))}
    grams = {}
    for k, ts in toks.items():
        seen = set()
        for n in (1, 2):
            for i in range(len(ts) - n + 1):
                g = tuple(ts[i:i + n])
                if all(w in head for w in g) or g in seen:
                    continue
                seen.add(g)
                grams.setdefault(g, []).append(k)
    order = [w for k in kws for w in toks[k]]
    head_txt = " ".join(sorted(head, key=order.index))
    print(f"{len(kws)} keyword · phần đầu chung (≥50% keyword): {head_txt or '—'}")
    print("cụm | số keyword | Top 10 | ví dụ")
    for g, ks in sorted(grams.items(), key=lambda x: (-len(x[1]), x[0]))[:60]:
        if len(ks) < 2:
            break
        print(f"  {' '.join(g):<24} {len(ks):>4} {sum(1 for k in ks if k in top10):>4}   {ks[0]}")


def cmd_bo(a):
    """Trích bộ keyword cam kết thành file mỗi dòng một keyword (bỏ trùng, giữ thứ tự)."""
    p = Path(a.source[0])
    text = p.read_text(encoding="utf-8-sig", errors="replace")
    if p.suffix.lower() == ".txt" and not a.col:
        kws = [nfc(x) for x in text.splitlines() if x.strip()]
    else:
        want = (lambda c: c.lower() == a.col.lower()) if a.col else (lambda c: c.lower() in KW_COLS)
        rows, hi = sniff(text, want)
        if rows is None:
            sys.exit(f"{p}: không thấy cột {a.col or 'Keyword/Từ khóa'}. Dùng --col \"<tên cột>\".")
        hdr = [nfc(c) for c in rows[hi]]
        ci = next(i for i, c in enumerate(hdr) if want(c))
        cond = None
        if a.where:
            wc, wv = (x.strip() for x in a.where.split("=", 1))
            if wc not in hdr:
                sys.exit(f"--where: không có cột {wc!r}. Cột đang có: {[c for c in hdr if c]}")
            cond = (hdr.index(wc), nfc(wv).lower())
        kws = [nfc(r[ci]) for r in rows[hi + 1:] if len(r) > ci and r[ci].strip()
               and (cond is None or (len(r) > cond[0] and nfc(r[cond[0]]).lower() == cond[1]))]
    seen, out = set(), []
    for k in kws:
        if k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    if not a.out:
        sys.exit("bo: cần -o <bo-cam-ket.txt>")
    Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{a.out}: {len(out)} keyword (bỏ {len(kws) - len(out)} dòng trùng). 3 keyword đầu: {' | '.join(out[:3])}")


def read_targets(path):
    rows, _ = sniff(Path(path).read_text(encoding="utf-8-sig", errors="replace"), lambda c: "/" in c)
    out = {}
    for r in rows or []:
        c = [nfc(x) for x in r if x.strip()]
        u = next((x for x in c[1:] if "/" in x), None)
        if c and u:
            out[c[0].lower()] = u
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["bo", "runs", "table", "terms"])
    ap.add_argument("source", nargs="+")
    ap.add_argument("--domain")
    ap.add_argument("--engine")
    ap.add_argument("--project")
    ap.add_argument("--keywords")
    ap.add_argument("--rules")
    ap.add_argument("--targets")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--now-runs")
    ap.add_argument("--compare")
    ap.add_argument("--no-compare", action="store_true")
    ap.add_argument("--keep-recent", action="store_true")
    ap.add_argument("--drop", default="")
    ap.add_argument("--max-missing", type=float, default=0.025)
    ap.add_argument("--col")
    ap.add_argument("--where")
    ap.add_argument("-o", "--out")
    ap.add_argument("--tsv")
    a = ap.parse_args()

    if a.cmd == "bo":
        return cmd_bo(a)
    if not a.domain:
        sys.exit(f"{a.cmd}: cần --domain")
    src = read_sources(a.source, a.project)
    dates, engine, own, others, multi = build(src, a.domain, a.engine)
    drop = {x.strip() for x in a.drop.split(",") if x.strip()}
    runs = analyse_runs(dates, own, others, multi, a.max_missing, drop)

    if a.cmd == "runs":
        print(f"{src.get('name')} · engine {engine} · {a.domain} · {len(own)} keyword · {'nhiều domain' if multi else 'một domain'}")
        print("\n".join(span_note(src, dates)))
        for r in runs:
            miss = f"thiếu {r['missing']:>3}" if r["missing"] is not None else ""
            print(f"  {r['date']}  có hạng {r['ranked']:>4}  {miss:<10} độ sâu {r['depth']}  {'hợp lệ' if r['valid'] else 'LOẠI: ' + r['why']}")
        return

    if a.cmd == "terms":
        return terms(a, own, others, multi, runs)

    kws = list(own)
    not_in = []
    if a.keywords:
        want = [nfc(x) for x in Path(a.keywords).read_text(encoding="utf-8").splitlines() if x.strip()]
        low = {k.lower(): k for k in own}
        not_in = [w for w in want if w.lower() not in low]
        kws = [low[w.lower()] for w in want if w.lower() in low]
    recent = [r for r in runs[:a.k] if r["heur"]]
    if recent and not a.now_runs:
        if a.keep_recent:
            for r in recent:
                r.update(valid=True, why="giữ theo --keep-recent (Lead xác nhận site rơi thật)")
        else:
            stop("DỪNG (gate nghiệp vụ, hỏi Lead): lần chạy mới bị nghi thiếu dữ liệu: "
                     + "; ".join(f"{r['date']} ({r['why']})" for r in recent)
                     + ".\nProject một domain không phân biệt được ô thiếu với rơi hạng thật. Lead mở SpySERP kiểm các lần đó:\n"
                       "  - site rơi thật → chạy lại với --keep-recent (deck đọc đúng cú rơi);\n"
                       f"  - SpySERP thiếu dữ liệu → chạy lại với --drop \"{','.join(r['date'] for r in recent)}\".", 3)
    valid = [r for r in runs if r["valid"]]
    if not valid:
        sys.exit("Không có lần chạy hợp lệ. Xem lệnh runs, chỉnh --max-missing hoặc --now-runs.")
    if a.now_runs:
        names = [x.strip() for x in a.now_runs.split(",") if x.strip()]
        now = [r for r in runs if r["date"] in names]
        if len(now) != len(names):
            sys.exit(f"--now-runs có ngày không khớp. Ngày trong nguồn: {dates[:12]}")
    else:
        now = valid[:a.k]
    depth = max(r["depth"] for r in now) if now else 100
    if a.no_compare:
        cdate, ago = None, []
    else:
        cdate = dt(a.compare) if a.compare else dt(now[0]["date"]) - timedelta(days=28)
        near = [r for r in valid if r not in now and abs((dt(r["date"]) - cdate).days) <= 7]
        ago = sorted(near, key=lambda r: (abs((dt(r["date"]) - cdate).days), r["i"]))[:a.k]
        if not ago:
            stop(f"DỪNG: không có lần chạy hợp lệ nào trong ±7 ngày quanh mốc so sánh {cdate:%d.%m.%Y}.\n"
                     + "\n".join(span_note(src, dates)) +
                     "\nCách xử lý (chọn một):\n"
                     "  1. Export thêm lần chạy cũ (trang lịch sau, hoặc khoảng ngày ≥35 ngày) rồi truyền mọi file vào cùng lệnh.\n"
                     "  2. Chọn mốc khác có dữ liệu: --compare dd.mm.yyyy.\n"
                     "  3. --no-compare: deck không có cột so sánh, không gắn trạng thái 'Đang lan'. Ghi lý do vào flags.", 2)
    rules = json.loads(Path(a.rules).read_text(encoding="utf-8")) if a.rules else []
    comp = [(x["id"], x["label"], re.compile(x["rx"], re.I)) for x in rules]
    tg = read_targets(a.targets) if a.targets else {}

    rows = []
    for k in kws:
        tid = next((i for i, _, rx in comp if rx.search(k)), None) if comp else None
        u = own[k]["url"]
        sp = urlsplit(u)
        row = {"kw": k, "tpl": tid, "url": (sp.path or u) if u else "", "vol": own[k].get("vol"),
               "now": median_rank(own, others, k, [r["i"] for r in now], depth, multi),
               "ago": median_rank(own, others, k, [r["i"] for r in ago], depth, multi) if ago else None,
               "series": {r["date"]: ("x" if missing_cell(others, k, r["i"], multi) else own[k]["s"][r["i"]]) for r in now + ago}}
        if tg:
            t = tg.get(k.lower(), "")
            row["target"] = norm_path(t)
            row["on_target"] = None if not t or not row["url"] else norm_path(row["url"]) == norm_path(t)
        rows.append(row)

    def tops(key):
        return {n: sum(1 for r in rows if r[key] is not None and r[key] <= n) for n in (3, 5, 10, 20)}

    tpls = []
    for tid, label, _ in comp:
        rs = [r for r in rows if r["tpl"] == tid]
        if not rs:
            continue
        cnt = lambda key: {b: sum(1 for r in rs if bucket(r[key], depth) == b) for b in ("t3", "t10", "t20", "t50", "out")}
        tpls.append({"id": tid, "label": label, "n": len(rs), "now": cnt("now"), "ago": cnt("ago") if ago else None})
    urls = {}
    for r in rows:
        if r["url"]:
            d = urls.setdefault(r["url"], {"n": 0, "top10": 0})
            d["n"] += 1
            d["top10"] += int(r["now"] is not None and r["now"] <= 10)
    targets = []
    if tg:
        by = {}
        for r in rows:
            if r.get("target"):
                by.setdefault(r["target"], []).append(r)
        for t, rs in sorted(by.items(), key=lambda x: -len(x[1])):
            other = {}
            for r in rs:
                if r["on_target"] is False:
                    other[norm_path(r["url"])] = other.get(norm_path(r["url"]), 0) + 1
            targets.append({"url": t, "n": len(rs), "match": sum(1 for r in rs if r["on_target"]),
                            "other_url": sum(other.values()), "no_rank": sum(1 for r in rs if r["on_target"] is None),
                            "google_urls": sorted(other.items(), key=lambda x: -x[1])[:5]})
    out = {"source": a.source[0] if len(a.source) == 1 else a.source, "project": src.get("name"), "engine": engine,
           "engine_config": src.get("engine_config", ""), "domain": a.domain, "mode": "nhiều domain" if multi else "một domain",
           "depth": depth, "compare": bool(ago),
           "runs": [{k: v for k, v in r.items() if k not in ("i", "heur")} for r in runs],
           "now_runs": [r["date"] for r in now], "ago_runs": [r["date"] for r in ago],
           "compare_target": cdate.strftime("%d.%m.%Y") if cdate else None,
           "n_keywords": len(rows), "tops": {"now": tops("now"), "ago": tops("ago") if ago else None},
           "templates": tpls, "unmatched": [r["kw"] for r in rows if comp and r["tpl"] is None], "not_in_export": not_in,
           "rules": rules, "targets": targets,
           "hub_urls": sorted(([u, d["n"], d["top10"]] for u, d in urls.items()), key=lambda x: (-x[1], -x[2]))[:10],
           "keywords": rows}
    if a.out:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.tsv:
        cell = lambda v: "" if v is None else str(v)
        with open(a.tsv, "w", encoding="utf-8") as f:
            f.write("keyword\ttemplate\turl\tnow\tago\tvol" + ("\ttarget\ton_target" if tg else "") + "\n")
            for r in rows:
                f.write("\t".join([r["kw"], r["tpl"] or "", r["url"], cell(r["now"]), cell(r["ago"]), cell(r["vol"])]
                                  + ([r["target"], cell(r["on_target"])] if tg else [])) + "\n")
    print(f"{src.get('name')} · {engine} · {a.domain} · {len(rows)} keyword · độ sâu {depth}")
    print("\n".join(span_note(src, dates)))
    print(f"  now = median {len(now)} lần: {', '.join(r['date'] for r in now)}")
    if ago:
        gap = max(abs((dt(r["date"]) - cdate).days) for r in ago)
        print(f"  ago = median {len(ago)} lần quanh {cdate:%d.%m.%Y} (lệch tối đa {gap} ngày): {', '.join(r['date'] for r in ago)}")
        print(f"  Top 3/5/10/20 now {tops('now')} · ago {tops('ago')}")
    else:
        print("  ago = không dùng (--no-compare): deck bỏ cột so sánh, không gắn 'Đang lan'")
        print(f"  Top 3/5/10/20 now {tops('now')}")
    nv = sum(1 for r in rows if r["vol"])
    if not_in and any(pg.get("Keywords Page") for _, pg in src.get("pages") or []):
        print("  Export ghi 'Keywords Page': SpySERP có thể chia keyword theo trang. Export thêm trang keyword và truyền cùng lệnh.")
    print(f"  loại {sum(1 for r in runs if not r['valid'])}/{len(runs)} lần chạy · thiếu trong export {len(not_in)} · "
          f"chưa có template {len(out['unmatched'])} · volume SpySERP > 0: {nv}/{len(rows)} keyword")
    for x in tpls:
        print(f"  {x['id']:<12} n={x['n']:<4} now {x['now']}  ago {x['ago'] if x['ago'] else '—'}")
    if out["unmatched"]:
        print(f"  chưa có template ({len(out['unmatched'])}), 25 keyword đầu: " + " | ".join(out["unmatched"][:25]))
    khac = sum(t["n"] for t in tpls if t["id"] in ("khac", "other"))
    if khac > 0.1 * max(1, len(rows)):
        print(f"  CẢNH BÁO: template 'khác' có {khac}/{len(rows)} keyword (>10%). Thêm rule cho các cụm lặp trong lệnh terms.")
    if len(tpls) > 16:
        print(f"  CẢNH BÁO: {len(tpls)} template, deck nhận tối đa 16. Gộp template nhỏ trong rules.json rồi chạy lại.")
    if tg:
        miss = sum(1 for r in rows if not r.get("target"))
        print(f"  URL target: {sum(t['other_url'] for t in targets)} keyword Google trả URL khác kế hoạch · "
              f"{sum(t['no_rank'] for t in targets)} keyword chưa có URL (ngoài độ sâu) · {miss} keyword không có trong file target")
        for t in targets[:12]:
            if t["other_url"]:
                print(f"    {t['url']}: {t['other_url']}/{t['n']} lệch → " + ", ".join(f"{u} ({n})" for u, n in t["google_urls"][:3]))


if __name__ == "__main__":
    main()
