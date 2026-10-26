#!/usr/bin/env python3
"""content-quality-lab: đo dấu hiệu effort của trang (dữ liệu gốc, trải nghiệm trực tiếp, nguồn có tên) bằng Jev,
so trang của mình với trang được AI trích trong cùng pool kết quả tìm kiếm.

Chạy bằng Python 3 (không cần thư viện ngoài):
  prepare  --rows rows.jsonl --pages pages.jsonl --out jev_in.jsonl [--urls urls.txt] [--max-chars 12000]
           Ghép chữ các section (output extract.py của site-vector-index) dưới tiêu đề trang. Bỏ trang dưới 150 chữ.
  validate --jev-out jev_out.jsonl --pools pools.jsonl --out auc_rows.jsonl
           Dòng {"pool","url","cited", <điểm từng câu hỏi>} cho calibrate.py auc của skill model-calibration.
  report   --jev-out jev_out.jsonl --registry model-calibration.json --site <domain> --out-dir DIR
           [--pools pools.jsonl --own-domain <domain>]
           Nhãn yes/no/review theo cổng confidence. Có pools: so trang của mình với trang được trích cùng pool.
  template --store DIR --registry model-calibration.json --site <domain> --out-dir DIR [--urls urls.txt]
           Passage của trang này gần trùng passage của trang khác cùng site (EmbeddingGemma, chạy bằng venv embedding).
           Ngưỡng nhận và dải xám lấy từ entry cosine "passage-dup" của registry. Ra dup_pairs.jsonl, pages.jsonl, report.md.
  claims   --rows rows.jsonl [--pages pages.jsonl] [--text file.txt --url URL [--own-site]] --out-dir DIR [--urls urls.txt]
           [--owner "Tên chủ site"] [--facts facts.json --entity "ACM=Acme SEO|ACM" --site-entity ACM]
           [--jev-out jev_out.jsonl] [--fact-nn fact_nn.jsonl] [--fact-jev-out fact_jev_out.jsonl]
           [--registry model-calibration.json --site <domain>]
           Chặn claim. Lớp 1 regex: hoàn tiền, cam kết kết quả, #1/số 1/top 1, hàng đầu, tốt nhất.
           Lớp 2 Jev rubric claim-guard: bảo đảm ngầm, tự xếp hạng, số không nguồn (input jev_in.jsonl).
           Lớp 3 so với bảng fact: câu chạm "cách viết cấm" của fact cùng entity là lệch (không cần model).
           Câu có số còn lại: EmbeddingGemma lấy 5 fact ứng viên (emb.py nn trên fact_q.jsonl, fact_d.jsonl),
           Jev rubric fact-match chọn fact cùng chỉ số (fact_jev_in.jsonl), code so số và entity.
           Chạy lại sau mỗi bước model, kèm --jev-out, --fact-nn, --fact-jev-out. Ra claims.tsv, claims.jsonl, report.md.
           --text không có --own-site (bản nháp site khách): không gửi Jev, chỉ regex, cụm cấm và Gemma trên máy.
  rewrite  --pairs pairs.jsonl --out-dir DIR [--own-site] [--facts facts.json --entity ...] [--jev-out rw_jev_out.jsonl]
           [--registry model-calibration.json --site <domain>] [--embed --pages pages.jsonl --gsc page_query.tsv]
           Kiểm an toàn khi viết lại. Code: số mất, số mới chưa có trong bảng fact, tên mất, cam kết hay xếp hạng mới,
           cách viết cấm mới. Jev rubric rewrite-keep (input rw_jev_in.jsonl, chỉ chữ trang và URL): fact còn đủ không,
           có thêm fact hay lời hứa không. Chỉ có --own-site mới gửi Jev, vì bản mới là chữ nháp chưa đăng.
           --embed (venv): cosine cũ ↔ mới; với --pages và --gsc, query GSC mang click được so với
           passage của trang cũ và trang mới, trên máy. Ra rewrite.tsv, rewrite.jsonl, queries.tsv, report.md.
pools.jsonl: {"id", "text", "urls": [{"url", "label"}]} hoặc dạng query của retrieval-lab ("candidates" + "labels").
Jev chỉ nhận chữ công khai của trang web, và bản nháp chưa đăng của site do chính đơn vị vận hành sở hữu (--own-site).
Bản nháp của site khách không gửi Jev. Không gửi GSC, hợp đồng, email.
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

RUBRIC = "content-effort"
NOUL = ("original_data", "first_hand", "named_sources")
CLAIM_RUBRIC = "claim-guard"
CLAIM_Q = ("guarantee", "self_superlative", "unsourced_stat")
SUBJ = "subject"
FACT_RUBRIC = "fact-check"
FACT_MATCH_RUBRIC = "fact-match"
K_FACT = 5
NONE_FACT = "No listed fact describes the same subject and the same kind of quantity as a number in the sentence."


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def domain(u):
    return urlparse(u).netloc.lower().removeprefix("www.")


def find_defaults():
    """tools/ai-assist/calibration-defaults.json của repo SEO Production, tìm ngược từ thư mục chạy và thư mục script."""
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def gates(registry, site, version, rubric=RUBRIC):
    out, src = {}, {}
    for path, want_site, name in ((registry, site, "site"), (find_defaults(), None, "defaults")):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == rubric and e.get("version") == version and e.get("mode") == "jev" \
                    and (want_site is None or e.get("site") == want_site):
                g = e.get("conf_gate") or e.get("threshold")
                if g and e["question"] not in out:
                    out[e["question"]], src[e["question"]] = g, name
    return out, src


def load_pools(path):
    pools = []
    for p in jl(path):
        if "urls" in p:
            urls = [{"url": u["url"], "cited": int(u.get("label", 0) > 0)} for u in p["urls"]]
        else:
            lab = p.get("labels") or {}
            urls = [{"url": u, "cited": int(lab.get(u, 0) > 0)} for u in p.get("candidates", [])]
        pools.append({"id": p["id"], "text": p.get("text", ""), "urls": urls})
    return pools


def cmd_prepare(a):
    pages = {p["url"]: p for p in jl(a.pages)}
    want = {l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()} if a.urls else None
    secs = defaultdict(list)
    for r in jl(a.rows):
        if r["level"] != "section" or (want and r["url"] not in want):
            continue
        m = re.search(r"#s(\d+)$", r["id"])
        secs[r["url"]].append((int(m.group(1)) if m else 0, r["text"]))
    out, skipped = [], 0
    for u, parts in sorted(secs.items()):
        p = pages.get(u, {})
        body = "\n\n".join(t for _, t in sorted(parts))
        if len(body.split()) < 150:
            skipped += 1
            continue
        lang = "en" if (p.get("lang") or "").lower().startswith("en") else "vi"
        out.append({"id": u, "state": {"lang": lang, "text": ((p.get("title") or "") + "\n\n" + body)[:a.max_chars]}})
    write(a.out, out)
    print(f"prepare: {len(out)} trang, bỏ {skipped} trang dưới 150 chữ -> {a.out}", file=sys.stderr)


def scores(r):
    a = r.get("answers") or {}
    out = {"effort": (a.get("effort") or {}).get("score")}
    for q in NOUL:
        out[q] = (a.get(q) or {}).get("p_yes")
    return out


def cmd_validate(a):
    jev = {r["id"]: r for r in jl(a.jev_out) if "answers" in r}
    rows = []
    for p in load_pools(a.pools):
        for u in p["urls"]:
            if u["url"] in jev:
                rows.append({"pool": p["id"], "url": u["url"], "cited": u["cited"], **scores(jev[u["url"]])})
    write(a.out, rows)
    print(f"validate: {len(rows)} dòng, {len({r['pool'] for r in rows})} pool -> {a.out}", file=sys.stderr)


def cmd_report(a):
    jev = {r["id"]: r for r in jl(a.jev_out) if "answers" in r}
    if not jev:
        sys.exit("jev_out rỗng")
    version = next(iter(jev.values()))["task_version"]
    g, gsrc = gates(a.registry, a.site, version)
    missing = {"original_data", "first_hand"} - set(g)
    if missing:
        sys.exit(f"chưa có cổng cho {sorted(missing)} ở rubric {version}: hiệu chuẩn bằng skill model-calibration trước")

    def label(r, q):
        p = ((r.get("answers") or {}).get(q) or {}).get("p_yes")
        if q not in g:
            return "chưa hiệu chuẩn"
        if p is None:
            return "review"
        return "yes" if p >= g[q] else ("no" if p <= 1 - g[q] else "review")

    pages = []
    for u, r in sorted(jev.items()):
        s = scores(r)
        pages.append({"url": u, "domain": domain(u), "effort": s["effort"], **{q: label(r, q) for q in NOUL},
                      **{f"p_{q}": s[q] for q in NOUL}})
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write(out / "pages.jsonl", pages)
    L = ["# Dấu hiệu effort của trang", "",
         f"Rubric `{RUBRIC}` {version}. Cổng: " + ", ".join(f"{q} {g[q]} ({gsrc[q]})" for q in sorted(g)) + ".",
         "Nhãn dưới cổng ghi review: Claude đọc trang rồi gán tay.", ""]
    if any(s == "defaults" for s in gsrc.values()):
        L += ["Một số cổng lấy từ defaults (đo trên site khác): số liệu là bản nháp tới khi hiệu chuẩn trên 40 mẫu của site này.", ""]
    L += ["| Câu hỏi | yes | no | review | chưa hiệu chuẩn |", "|---|---|---|---|---|"]
    for q in NOUL:
        c = defaultdict(int)
        for p in pages:
            c[p[q]] += 1
        L.append(f"| {q} | {c['yes']} | {c['no']} | {c['review']} | {c['chưa hiệu chuẩn']} |")
    if a.pools:
        by = {p["url"]: p for p in pages}
        own = (a.own_domain or a.site or "").lower().removeprefix("www.")

        def mean_p(rows, q):
            v = [r[f"p_{q}"] for r in rows if r[f"p_{q}"] is not None]
            return f"{sum(v) / len(v):.2f}" if v else "—"

        L += ["", f"## So với trang được AI trích (domain mình: {own})", "",
              "Cột p là xác suất Jev trung bình (0–1). So p của trang mình với p của trang được trích cùng pool.", "",
              "| Pool | Truy vấn | Được trích: dữ liệu gốc yes/n · p | Trang của mình | Dữ liệu gốc · p | Trải nghiệm · p | Việc gợi ý |",
              "|---|---|---|---|---|---|---|"]
        for p in load_pools(a.pools):
            cited = [by[u["url"]] for u in p["urls"] if u["cited"] and u["url"] in by]
            mine = [by[u["url"]] for u in p["urls"] if u["url"] in by and by[u["url"]]["domain"] == own]
            share = f"{sum(c['original_data'] == 'yes' for c in cited)}/{len(cited)} · {mean_p(cited, 'original_data')}"
            if not mine:
                L.append(f"| {p['id']} | {p['text'][:60]} | {share} | (không có) | | | trang mình ngoài pool: kiểm truy xuất bằng `retrieval-lab` |")
                continue
            for m in mine:
                todo = []
                if m["original_data"] == "no" and any(c["original_data"] == "yes" for c in cited):
                    todo.append("thêm số đo từ dự án thật (`expert-case-study`)")
                if m["first_hand"] == "no" and any(c["first_hand"] == "yes" for c in cited):
                    todo.append("kể việc đã làm, không chỉ nêu kết quả")
                if "review" in (m["original_data"], m["first_hand"]):
                    todo.append("Claude đọc trang trước")
                L.append(f"| {p['id']} | {p['text'][:60]} | {share} | {m['url']} | {m['original_data']} · {m['p_original_data']:.2f} | "
                         f"{m['first_hand']} · {m['p_first_hand']:.2f} | {'; '.join(todo) or '—'} |")
    L += ["", "Chỉ số mô phỏng ý tưởng contentEffort trong tài liệu rò rỉ của Google, trọng số thật chưa công bố.",
          "Nhãn đo dấu hiệu trong chữ của trang, không đo chất lượng sự thật của số liệu."]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"report: {len(pages)} trang -> {out / 'report.md'}", file=sys.stderr)


def dup_gate(registry, site):
    for path, want_site in ((registry, site), (find_defaults(), None)):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if e.get("rubric") == "passage-dup" and e.get("mode") == "cosine" and e.get("threshold") \
                    and (want_site is None or e.get("site") == want_site):
                return e["threshold"], ("site" if want_site else "defaults")
    return None, None


def cmd_template(a):
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
    import svi  # noqa: E402  (cùng bộ skill)
    thr, src = dup_gate(a.registry, a.site)
    if thr is None:
        sys.exit("chưa có ngưỡng passage-dup: gán 40+ cặp và chạy calibrate.py cosine (rubric passage-dup) trước")
    gray = round(thr - a.gray, 2)
    st = svi.Store(a.store)
    want = {l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()} if a.urls else None
    idx = [i for i, it in enumerate(st.items) if it["level"] == "passage" and (want is None or it["url"] in want)]
    if not idx:
        sys.exit("không có passage trong scope")
    X = st.vec[idx].astype(np.float32)
    U = np.asarray([st.items[i]["url"] for i in idx])
    best, arg = np.zeros(len(idx), dtype=np.float32), np.zeros(len(idx), dtype=int)
    for s in range(0, len(idx), 2048):
        S = X[s:s + 2048] @ X.T
        S[U[s:s + 2048][:, None] == U[None, :]] = -1  # chỉ so với trang khác
        arg[s:s + 2048] = S.argmax(1)
        best[s:s + 2048] = S[np.arange(S.shape[0]), arg[s:s + 2048]]
    pairs, seen = [], set()
    for k in np.flatnonzero(best >= gray):
        j = int(arg[k])
        key = tuple(sorted((int(k), j)))
        if key in seen:
            continue
        seen.add(key)
        A, B = st.items[idx[k]], st.items[idx[j]]
        pairs.append({"a": A["id"], "b": B["id"], "url_a": A["url"], "url_b": B["url"], "cos": round(float(best[k]), 4),
                      "status": "dup" if best[k] >= thr else "review",
                      "text_a": (A.get("text") or "")[:300], "text_b": (B.get("text") or "")[:300]})
    pairs.sort(key=lambda p: -p["cos"])
    per = defaultdict(lambda: [0, 0])
    for u, b in zip(U, best):
        per[u][0] += 1
        per[u][1] += int(b >= thr)
    pages = sorted(({"url": u, "passages": n, "dup": d, "dup_share": round(d / n, 3)} for u, (n, d) in per.items()),
                   key=lambda p: -p["dup_share"])
    out = Path(a.out_dir)
    write(out / "dup_pairs.jsonl", pairs)
    write(out / "pages.jsonl", pages)
    L = ["# Khối chữ lặp giữa các trang", "",
         f"Ngưỡng trùng {thr} ({src}); dải {gray}–{thr} ghi review. {len(idx)} passage, {len(per)} trang.", "",
         "## Trang có tỷ lệ passage trùng cao nhất", "", "| URL | Passage | Trùng | Tỷ lệ |", "|---|---|---|---|"]
    for p in pages[:30]:
        if p["dup"]:
            L.append(f"| {p['url']} | {p['passages']} | {p['dup']} | {p['dup_share']:.0%} |")
    L += ["", "## Cặp trùng (30 cặp đầu)", "", "| Cos | Trang A | Trang B | Đầu đoạn A |", "|---|---|---|---|"]
    for p in pairs[:30]:
        L.append(f"| {p['cos']} {p['status']} | {p['url_a']} | {p['url_b']} | {p['text_a'][:90].replace('|', ' ')} |")
    L += ["", "## Đọc kết quả", "",
          "- Khối mẫu (CTA, bảng giá, form) lặp ở nhiều trang là bình thường. Chỉ sửa khi khối đó nằm sai mục, ví dụ dưới heading kết quả.",
          "- Lời chứng thực, số liệu, mô tả dịch vụ lặp: so người nói, số và ngày giữa các bản. Lệch thì chuyển `site-fact-consistency`.",
          "- Trang địa phương gần trùng nhau: thêm nội dung riêng của địa phương, hoặc gộp trang.",
          "- Tỷ lệ trùng chưa được chứng minh là dự báo hiển thị (pilot site mẫu: rho −0,03 trên trang nội dung). Không đưa vào báo cáo khách như yếu tố xếp hạng."]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"template: {len(pairs)} cặp (≥{gray}), {sum(p['dup'] > 0 for p in pages)} trang có passage trùng -> {out}",
          file=sys.stderr)


# ---------- claims: chặn cam kết, tự xếp hạng, số không nguồn, số lệch bảng fact ----------

# Lớp 1: cụm cấm rõ. Cụm có "không/chưa/never..." đứng trước trong 4 từ thì ghi phủ định, không tính là trúng.
L1 = [
    ("hoàn tiền", re.compile(
        r"\bhoàn\s+(?:lại\s+)?(?:100\s*%\s+)?(?:học\s+)?(?:phí|tiền)\b|\bhoàn\s+trả\s+(?:lại\s+)?(?:\S+\s+){0,2}?(?:phí|tiền)\b"
        r"|\btrả\s+lại\s+(?:100\s*%\s+)?(?:tiền|phí)\b|\bmoney[\s-]?back\b|\brefund", re.I)),
    ("cam kết kết quả", re.compile(
        r"\b(?:cam\s+kết|bảo\s+đảm|đảm\s+bảo|bảo\s+hành|guarantee[ds]?|guaranteeing)\s+(?:\d+\s*%\s+)?(?:các\s+)?"
        r"(?:kết\s+quả|KPIs?\b|thứ\s+hạng|top\b|lên\s+top|vị\s+trí|traffic|doanh\s+(?:số|thu)|results?\b|rankings?\b)"
        r"|\bKPIs?\s+(?:đã\s+)?cam\s+kết|\bbảo\s+hành\s+(?:tối\s+đa\s+)?\d+\s*(?:tháng|ngày)", re.I)),
    # Dấu chấm, phẩy sau "1" chỉ loại khi kèm số (1.000, 1,5); "số 1." cuối câu vẫn tính.
    ("#1", re.compile(r"(?<![\w&])#\s?1(?!\d|[.,]\d)|\bsố\s+(?:1|một)\b(?!\d|[.,/:]\d)|\btop\s*1\b(?!\d|[.,]\d|[\-–])"
                      r"|\bno\.\s?1\b|\bnumber\s+one\b", re.I)),
    ("hàng đầu", re.compile(r"\bhàng\s+đầu\b|\bleading\b", re.I)),
    ("tốt nhất", re.compile(r"\btốt\s+nhất\b|\bbest\b", re.I)),
]
NEG = re.compile(r"(?:^|\s)(?:không|chưa|chẳng|never|no|not|don't|without)(?:\s+\S+){0,3}\s*$", re.I)
# Câu nào chạm một trong các dấu hiệu này mới gửi Jev. Câu không chạm thì Jev không đọc (giới hạn recall ghi ở SKILL.md).
TRIGGER = re.compile(r"\d\s*%|\d\s*\+|\d\s*(?:lần|triệu|nghìn|ngàn|tỷ|million|billion|k)\b|\bx\s?\d|\d{1,3}(?:\.\d{3})+|nhất\b|hàng\s+đầu|dẫn\s+đầu|đầu\s+tiên|tiên\s+phong|thống\s+trị|vượt\s+trội|số\s+một|\btop\b|#"
                     r"|cam\s+kết|bảo\s+đảm|đảm\s+bảo|bảo\s+hành|chắc\s+chắn|hoàn\s+(?:phí|tiền|trả)|gấp\s+\S+\s+lần|\bx\d"
                     r"|leading|best|guarantee|promise|refund|money", re.I)
NUM = re.compile(r"(?<![\w.,])(\d{1,3}(?:\.\d{3})+(?!\d)|\d+\.\d{1,2}(?![\d.])|\d+)(?:,(\d+))?"
                 r"(?:\s*\+?\s*(triệu|tỷ|nghìn|ngàn|million|billion|k)\b)?", re.I)
MULT = {"triệu": 1e6, "million": 1e6, "tỷ": 1e9, "billion": 1e9, "nghìn": 1e3, "ngàn": 1e3, "k": 1e3}
ORDER = ["người đọc", "sửa theo fact", "xoá", "thêm nguồn", "giữ"]
MAX_WORDS, WIN = 40, 12


def norm(s):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s or "")).strip()


def sid(text):
    return hashlib.sha1(norm(text).lower().encode("utf-8")).hexdigest()[:12]


def nums(text):
    out = set()
    for m in NUM.finditer(text or ""):
        a, dec, unit = m.group(1), m.group(2), (m.group(3) or "").lower()
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", a):
            v = float(a.replace(".", ""))
        else:
            v = float(a)
        if dec:
            v = v * 1000 + float(dec) if len(dec) == 3 and "." not in a and not unit else float(f"{int(v)}.{dec}")
        out.add(round(v * MULT.get(unit, 1), 4))
    return out


def split_sentences(text):
    """Tách câu: dấu kết câu + khoảng trắng + chữ hoa, số hoặc ngoặc. Ký tự ¶ và xuống dòng là ranh giới khối."""
    out, parts = [], []
    for p in re.split(r"\s*(?:¶|\n)\s*", text or ""):
        if parts and re.fullmatch(r"[\d.,+%kK ]+", parts[-1]):  # ô đếm: số ở khối trước, nhãn ở khối sau
            parts[-1] += " " + p
        else:
            parts.append(p)
    for part in parts:
        start = 0
        for m in re.finditer(r"[.!?…]+[\"”’)]?\s+", part):
            c = part[m.end():m.end() + 1]
            if c and (c.isupper() or c.isdigit() or c in "\"“‘(["):
                out.append(part[start:m.end()].strip())
                start = m.end()
        out.append(part[start:].strip())
    return [s for s in out if s]


def windows(sent):
    """Câu dài (bảng giá, ô liền nhau) thành cửa sổ ±12 từ quanh mỗi chỗ chạm dấu hiệu."""
    toks = list(re.finditer(r"\S+", sent))
    if len(toks) <= MAX_WORDS:
        return [sent]
    # Cụm lớp 1 luôn có cửa sổ riêng, đặt cụm ở giữa. Dấu hiệu khác cách cửa sổ trước tối thiểu 12 từ mới mở cửa sổ mới.
    l1 = sorted({m.start() for _, r in L1 for m in r.finditer(sent)})
    other = sorted({m.start() for m in TRIGGER.finditer(sent)} - set(l1))
    tok_i = lambda h: next((k for k, t in enumerate(toks) if t.end() > h), len(toks) - 1)  # noqa: E731
    centers = []
    for i in map(tok_i, l1):
        if all(abs(i - c) > 4 for c in centers):
            centers.append(i)
    for i in map(tok_i, other):
        if all(abs(i - c) > WIN for c in centers):
            centers.append(i)
    spans = sorted({(max(0, i - WIN), min(len(toks), i + WIN + 1)) for i in centers})
    return [("… " if lo else "") + sent[toks[lo].start():toks[hi - 1].end()] + (" …" if hi < len(toks) else "")
            for lo, hi in spans]


def l1_hits(text):
    out = []
    for name, rx in L1:
        for m in rx.finditer(text):
            out.append({"label": name, "match": m.group(0), "neg": bool(NEG.search(text[max(0, m.start() - 40):m.start()]))})
    return out


def read_segments(a):
    """(url, đoạn chữ) từ rows/pages/blocks JSONL hoặc file chữ."""
    want = {l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()} if a.urls else None
    segs = []
    for f in a.rows or []:
        pend = None  # ô đếm tách 2 dòng (blocks): dòng chỉ có số ghép với dòng kế tiếp cùng URL
        for r in jl(f):
            if not r.get("url") or not r.get("text") or ("level" in r and r["level"] != a.level):
                continue
            t, head = r["text"], ((r.get("meta") or {}).get("heading") or "")
            if pend:
                segs.append((pend[0], pend[1] + (" " + t if pend[0] == r["url"] else "")))
                pend = None
            if re.fullmatch(r"[\d.,+%kK ]+", t.strip()):
                pend = (r["url"], t.strip())
                continue
            if head and t.startswith(head + ":"):
                segs.append((r["url"], head))
                t = t[len(head) + 1:]
            segs.append((r["url"], t))
        if pend:
            segs.append(pend)
    for f in a.text or []:
        segs.append((a.url or str(f), Path(f).read_text(encoding="utf-8")))
    have = {u for u, _ in segs}  # pages.jsonl thường là cả site: chỉ lấy title, meta, h1 của trang có trong rows hoặc file chữ
    for f in [a.pages] if a.pages else []:
        for p in jl(f):
            if p.get("url") not in have:
                continue
            for k in ("title", "meta", "h1"):
                if p.get(k) and isinstance(p[k], str):
                    segs.append((p["url"], p[k]))
    return [(u, t) for u, t in segs if want is None or u in want]


def load_facts(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    facts = d.get("facts", []) if isinstance(d, dict) else d
    for f in facts:
        miss = {"id", "entity", "metric", "value"} - set(f)
        if miss:
            sys.exit(f"facts.json: fact {f.get('id')} thiếu {sorted(miss)}")
    return facts


def fact_doc(f):
    """Chữ đại diện một fact cho Gemma và Jev, ví dụ "ACM: seo projects: 550+ doanh nghiệp"."""
    return f"{f['entity']}: {f['metric'].replace('_', ' ')}: {f.get('canon') or f['value']}"


def phrase_rx(p):
    p = norm(p)
    return re.compile(("(?<![\\d.,])" if p[:1].isdigit() else "(?<!\\w)") + re.escape(p)
                      + ("(?![\\d])" if p[-1:].isdigit() or p[-1:] == "+" else "(?!\\w)"), re.I)


def entity_rx(spec_list, facts):
    al = defaultdict(list)
    for s in spec_list or []:
        name, _, rest = s.partition("=")
        al[name.strip()] += [x.strip() for x in rest.split("|") if x.strip()]
    for f in facts:
        al[f["entity"]] = al.get(f["entity"]) or [f["entity"]]
    out = {}
    for name, xs in al.items():
        parts = [(re.escape(x), x.isupper() and len(x) <= 4) for x in xs]
        cs = "|".join(p for p, c in parts if c)
        ci = "|".join(p for p, c in parts if not c)
        out[name] = (re.compile(rf"(?<!\w)(?:{cs})(?!\w)") if cs else None,
                     re.compile(rf"(?<!\w)(?:{ci})(?!\w)", re.I) if ci else None)
    return out


def entities_in(text, erx):
    return {n for n, (a, b) in erx.items() if (a and a.search(text)) or (b and b.search(text))}


def compare_fact(text, f):
    """So số của câu với một fact: khớp, lệch số hoặc chạm cách viết bị cấm. Luật tất định, không model."""
    t = norm(text)
    if any(phrase_rx(p).search(t) for p in f.get("banned") or []):
        return "lệch", "chạm cách viết bị cấm"
    if any(phrase_rx(p).search(t) for p in f.get("allowed") or []) or (f.get("canon") and phrase_rx(f["canon"]).search(t)):
        return "khớp", "cách viết được phép"
    fv = set().union(*(nums(str(x)) for x in [f["value"], f.get("canon") or "", *(f.get("allowed") or [])]))
    if not fv:
        return "chưa rõ", "fact không có số: Claude so cách viết"
    if nums(t) & fv:
        return "khớp", "số khớp"
    return "lệch", f"số câu {sorted(nums(t))} ≠ fact {f.get('canon') or f['value']}"


def reg_entries(registry, site):
    """Entry của registry site trước, rồi entry của calibration-defaults.json."""
    for path, want_site in ((registry, site), (find_defaults(), None)):
        if path and Path(path).exists():
            for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
                if want_site is None or e.get("site") == want_site:
                    yield e, ("site" if want_site else "defaults")


def cos_floor(registry, site, rubric):
    """Sàn cosine để lấy ứng viên fact: reject_below của entry cosine (dưới sàn gần như chắc không cùng chỉ số)."""
    for e, src in reg_entries(registry, site):
        if e.get("rubric") == rubric and e.get("mode") == "cosine" and (e.get("reject_below") or e.get("threshold")):
            return e.get("reject_below") or e["threshold"], src
    return None, None


def none_thr(registry, site, version):
    """Ngưỡng xác suất nhãn none của fact-match: từ ngưỡng này trở lên coi như câu không nói về fact nào."""
    for e, _ in reg_entries(registry, site):
        if e.get("rubric") == FACT_MATCH_RUBRIC and e.get("version") == version and e.get("positive") == "none" \
                and e.get("threshold"):
            return e["threshold"]
    return None


def build_sentences(a):
    by, flat = {}, defaultdict(list)
    for url, seg in read_segments(a):
        flat[url] += split_sentences(seg)  # câu kề nhau trong trang, kể cả qua ranh giới khối, làm ngữ cảnh cho Jev
    for url, sents in flat.items():
        for i, s in enumerate(sents):
            for w in windows(s):
                k = sid(w)
                if k in by:
                    if url not in by[k]["urls"]:
                        by[k]["urls"].append(url)
                    continue
                hits = l1_hits(w)  # câu chạm cụm lớp 1 luôn gửi Jev, kể cả khi không chạm TRIGGER (ví dụ "số 1")
                by[k] = {"sid": k, "text": norm(w), "urls": [url], "before": norm(sents[i - 1])[-200:] if i else "",
                         "after": norm(sents[i + 1])[:200] if i + 1 < len(sents) else "",
                         "l1": hits, "cand": bool(TRIGGER.search(w) or hits), "nums": sorted(nums(w))}
    return list(by.values())


def jev_label(p, g):
    if p is None:
        return "review"
    return "yes" if p >= g else ("no" if p <= 1 - g else "review")


def decide(s):
    """Đề xuất cho một câu. Mọi dòng claims.tsv chỉ là đề xuất: không lệnh nào tự sửa trang."""
    lab = {h["label"] for h in s["l1"] if not h["neg"]}
    J, F = s.get("jev") or {}, s.get("fact") or {}
    subj = J.get(SUBJ)  # owner, other_company, client, general; "review" khi dưới cổng; None khi chưa chạy Jev
    other = subj in ("other_company", "client")
    # 1. Cam kết, hoàn tiền: chủ site quyết. Chỉ hạ khi Jev chắc câu nói về bên khác và không phải cam kết của chủ site.
    if lab & {"hoàn tiền", "cam kết kết quả"} or J.get("guarantee") in ("yes", "review"):
        if other and J.get("guarantee") == "no":
            return "giữ", [f"cam kết của bên khác (chủ thể {subj})"]
        if lab & {"hoàn tiền", "cam kết kết quả"} or J.get("guarantee") == "yes":
            return "người đọc", ["cam kết hoặc bảo đảm: chủ site quyết, agent không tự viết câu cam kết mới"]
        return "người đọc", ["Jev dưới cổng: guarantee"]
    # 2. Số lệch bảng fact (chạm cách viết cấm, hoặc Jev fact-match qua cổng, cùng entity): sửa theo fact.
    if F.get("status") == "lệch" and F.get("band") in ("cụm cấm", "nhận") and not F.get("entity_note"):
        return "sửa theo fact", [F["why"]]
    # 3. Tự xếp hạng: chỉ đề xuất xoá khi Jev chắc chủ thể là chủ site.
    sup = lab & {"#1", "hàng đầu", "tốt nhất"}
    if J.get("self_superlative") == "yes" and subj == "owner":
        return "xoá", ["tự xếp hạng không nguồn: bỏ cụm so sánh nhất hoặc dẫn nguồn bên thứ ba"]
    if J.get("self_superlative") == "yes" and not other:
        return "người đọc", [f"Jev: so sánh nhất, chủ thể {subj}"]
    if sup and (not J or J.get("self_superlative") == "review"):
        return "người đọc", ["regex trúng cụm so sánh nhất, Jev chưa chạy hoặc dưới cổng"]
    # 4. Số liệu không nguồn.
    if J.get("unsourced_stat") == "yes":
        return "thêm nguồn", ["Jev: số liệu không nguồn; ghi nguồn hoặc bỏ số"]
    notes = []
    if J.get("unsourced_stat") == "review":
        notes.append("Jev dưới cổng: unsourced_stat")
    if F.get("entity_note"):
        notes.append(F["entity_note"])
    if F.get("status") == "lệch" and F.get("band") == "xám":
        notes.append("fact dải xám: " + F["why"])
    if notes:
        return "người đọc", notes
    if sup or J.get("self_superlative") == "yes":
        return "giữ", [f"regex hoặc Jev trúng so sánh nhất nhưng không phải chủ site tự xếp hạng (chủ thể {subj})"]
    return "giữ", []


def cmd_claims(a):
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sents = build_sentences(a)
    if not sents:
        sys.exit("không có câu nào trong input")
    nojev = bool(a.text) and not a.own_site  # bản nháp site khách: không gửi Jev
    lang ={p["url"]: ("en" if (p.get("lang") or "").lower().startswith("en") else "vi") for p in jl(a.pages)} if a.pages else {}
    jin = [{"id": s["sid"], "state": {"lang": lang.get(s["urls"][0], a.lang), "owner": a.owner or domain(s["urls"][0]),
                                      "page": s["urls"][0], "before": s["before"], "sentence": s["text"], "after": s["after"]}}
           for s in sents if s["cand"] and not nojev]
    write(out / "jev_in.jsonl", jin)
    facts = load_facts(a.facts) if a.facts else []
    erx = entity_rx(a.entity, facts) if facts else {}
    brands = {s.partition("=")[0].strip() for s in a.entity or []}
    info = [f"{len(sents)} câu, {len(jin)} câu gửi Jev"]
    if nojev:
        info.append("Bản nháp site khách (--text, không có --own-site): cả lượt không gửi Jev, chỉ chạy regex, cụm cấm "
                    "và Gemma trên máy. Câu chạm dấu hiệu: Claude đọc")
    elif a.text:
        info.append("Bản nháp chưa đăng của site do chính đơn vị vận hành sở hữu (--own-site): chữ nháp được gửi Jev")
    if facts:
        write(out / "fact_q.jsonl", [{"id": s["sid"], "text": s["text"]} for s in sents if s["nums"]])
        write(out / "fact_d.jsonl", [{"id": f["id"], "text": fact_doc(f)} for f in facts])
        # Lớp 3a, không cần model: câu chạm "cách viết cấm" của fact cùng entity (entity khai bằng --entity) là lệch.
        banned = [(f, p, strict_rx(p)) for f in facts for p in f.get("banned") or []]
        for s in sents:
            ents = (entities_in(s["text"], erx) & brands) or ({a.site_entity} if a.site_entity else set())
            hit = next(((f, p) for f, p, rx in banned if not (f["entity"] in brands and f["entity"] not in ents)
                        and rx.search(s["text"])), None)
            if hit:
                f, p = hit
                s["fact"] = {"id": f["id"], "entity": f["entity"], "cos": None, "band": "cụm cấm", "status": "lệch",
                             "why": f"chạm cách viết cấm \"{p}\" (fact {f['id']}: {f.get('canon') or f['value']})",
                             "entity_note": ""}
        info.append(f"{sum(1 for s in sents if s.get('fact'))} câu chạm cách viết cấm của bảng fact")
    if a.jev_out:
        jev = {r["id"]: r for r in jl(a.jev_out) if "answers" in r}
        version = next(iter(jev.values()))["task_version"] if jev else None
        g, gsrc = gates(a.registry, a.site, version, CLAIM_RUBRIC)
        missing = set(CLAIM_Q) - set(g)
        if missing:
            sys.exit(f"chưa có cổng claim-guard {version} cho {sorted(missing)}: hiệu chuẩn bằng skill model-calibration trước")
        for s in sents:
            r = jev.get(s["sid"])
            if r:
                ans = r["answers"]
                s["p"] = {q: (ans.get(q) or {}).get("p_yes") for q in CLAIM_Q}
                s["jev"] = {q: jev_label(s["p"][q], g[q]) for q in CLAIM_Q}
                sj = ans.get("subject")
                if sj:  # câu hỏi choice: nhận khi confidence từ cổng trở lên, không có cổng thì coi như dưới cổng
                    ok = SUBJ in g and (sj.get("confidence") or 0) >= g[SUBJ]
                    s["jev"][SUBJ] = sj["choice"] if ok else "review"
        info.append(f"Jev claim-guard {version}, cổng " + ", ".join(f"{q} {g[q]} ({gsrc[q]})" for q in (*CLAIM_Q, SUBJ) if q in g))
    if a.fact_nn:
        if not facts:
            sys.exit("--fact-nn cần --facts")
        floor, src = cos_floor(a.registry, a.site, FACT_RUBRIC)
        if floor is None:
            sys.exit("chưa có sàn fact-check: gán 40+ câu có số với fact đúng và chạy calibrate.py cosine (rubric fact-check) trước")
        fmap = {f["id"]: f for f in facts}
        nn = {r["id"]: r for r in jl(a.fact_nn)}
        fj, fg, fgsrc, fnone = {}, None, None, None
        if a.fact_jev_out:
            fj = {r["id"]: r for r in jl(a.fact_jev_out) if "answers" in r}
            fv = next(iter(fj.values()))["task_version"] if fj else None
            gg, gs = gates(a.registry, a.site, fv, FACT_MATCH_RUBRIC)
            fg, fgsrc, fnone = gg.get("fact"), gs.get("fact"), none_thr(a.registry, a.site, fv)
            if fj and fg is None:
                sys.exit(f"chưa có cổng fact-match {fv}: hiệu chuẩn bằng skill model-calibration trước")
        fjin = []
        for s in sents:
            r = nn.get(s["sid"])
            if nojev or s.get("fact") or not r or not r["top"] or r["top"][0]["cos"] < floor:
                continue
            cands = [(fmap[t["id"]], t["cos"]) for t in r["top"][:K_FACT] if t["id"] in fmap and t["cos"] >= floor]
            fjin.append({"id": s["sid"], "state": {"lang": lang.get(s["urls"][0], a.lang),
                                                   "owner": a.owner or domain(s["urls"][0]), "page": s["urls"][0],
                                                   "before": s["before"], "sentence": s["text"], "after": s["after"]},
                         "criteria": {"fact": {"none": NONE_FACT, **{c[0]["id"]: fact_doc(c[0]) for c in cands}}}})
            # Chỉ entity khai bằng --entity (thương hiệu tách bạch, ví dụ hai công ty) mới xét lệch entity.
            named = entities_in(s["text"], erx) & brands
            ents = named or ({a.site_entity} if a.site_entity else set())
            same = [c for c in cands if c[0]["entity"] in ents]
            f, cos = max(same or cands, key=lambda c: c[1])
            band = "xám"  # chưa có Jev fact-match hoặc dưới cổng: Claude đọc khi số lệch
            ans = ((fj.get(s["sid"]) or {}).get("answers") or {}).get("fact")
            if ans:
                conf = ans.get("confidence") or 0
                if (fnone is not None and (ans.get("probabilities") or {}).get("none", 0) >= fnone) \
                        or (ans["choice"] == "none" and conf >= fg):
                    continue  # Jev: không fact nào cùng chỉ số với câu
                if ans["choice"] in fmap:  # dưới cổng vẫn hiện fact Jev chọn, vì Jev chọn đúng hơn cosine
                    f, cos = fmap[ans["choice"]], dict((c[0]["id"], c[1]) for c in cands).get(ans["choice"], cos)
                    band = "nhận" if conf >= fg else "xám"
            status, why = compare_fact(s["text"], f)
            note = ""
            if named and f["entity"] in brands and f["entity"] not in named:
                note = f"lệch entity: câu nêu {', '.join(sorted(named))}, fact gần nhất của {f['entity']}"
            elif status == "lệch":  # chỉ tính cách viết được phép của entity khác, không tính số trùng ngẫu nhiên
                other = [c for c in cands if c[0]["entity"] != f["entity"] and c[0]["entity"] in brands
                         and compare_fact(s["text"], c[0])[1] == "cách viết được phép"]
                if other:
                    note = f"lệch entity: số khớp fact {other[0][0]['id']} của {other[0][0]['entity']}"
            s["fact"] = {"id": f["id"], "entity": f["entity"], "cos": cos, "band": band,
                         "status": status, "why": f"{why} (fact {f['id']}: {f.get('canon') or f['value']})",
                         "entity_note": note}
        write(out / "fact_jev_in.jsonl", fjin)
        info.append(f"Gemma lấy tối đa {K_FACT} fact ứng viên, sàn cosine {floor} ({src}); {len(fjin)} câu cho Jev fact-match"
                    + (f", cổng fact {fg} ({fgsrc}), ngưỡng none {fnone}" if fj else ": chưa ghép Jev, mọi fact ở dải xám"))
    for s in sents:
        s["de_xuat"], s["notes"] = decide(s)
        if nojev and s["cand"] and s["de_xuat"] == "giữ":
            s["de_xuat"], s["notes"] = "người đọc", ["bản nháp site khách: Jev không đọc, Claude đọc câu chạm dấu hiệu"]
    write(out / "claims.jsonl", sents)
    # Trong cùng đề xuất: câu có regex, nhãn Jev yes hoặc fact chắc chắn lên trước câu dưới cổng.
    sure = lambda s: any(not h["neg"] for h in s["l1"]) or "yes" in (s.get("jev") or {}).values() \
        or (s.get("fact") or {}).get("band") in ("cụm cấm", "nhận")  # noqa: E731
    flagged = sorted((s for s in sents if s["de_xuat"] != "giữ" or any(not h["neg"] for h in s["l1"])),
                     key=lambda s: (ORDER.index(s["de_xuat"]), not sure(s), -len(s["urls"])))
    cols = ["cau", "url", "so_trang", "lop", "nhan", "p", "fact", "de_xuat", "ghi_chu"]
    lines = ["\t".join(cols)]
    for s in flagged:
        lop, nhan = [], []
        if s["l1"]:
            lop.append("regex")
            nhan += [h["label"] + (" (phủ định)" if h["neg"] else "") for h in s["l1"]]
        J = s.get("jev") or {}
        if any(J.get(q, "no") != "no" for q in CLAIM_Q):
            lop.append("jev")
            nhan += [f"jev {q}={J[q]}" for q in CLAIM_Q if J.get(q, "no") != "no"] + [f"chủ thể={J.get(SUBJ, '?')}"]
        if s.get("fact"):
            lop.append("fact" if s["fact"]["band"] == "cụm cấm" else "gemma")
            nhan.append(f"fact {s['fact']['status']} ({s['fact']['band']})")
        p = " ".join(f"{q[0]}={v:.2f}" for q, v in (s.get("p") or {}).items() if v is not None)
        if (s.get("fact") or {}).get("cos") is not None:
            p += f" cos={s['fact']['cos']:.3f}"
        row = [s["text"], s["urls"][0], str(len(s["urls"])), "+".join(dict.fromkeys(lop)), "; ".join(dict.fromkeys(nhan)),
               p.strip(), (s.get("fact") or {}).get("id", ""), s["de_xuat"], "; ".join(s["notes"])]
        lines.append("\t".join(c.replace("\t", " ").replace("\n", " ") for c in row))
    (out / "claims.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    cnt = defaultdict(int)
    for s in flagged:
        cnt[s["de_xuat"]] += 1
    L = ["# Chặn claim", "", *[f"- {x}" for x in info], "",
         "| Đề xuất | Số câu |", "|---|---|", *[f"| {k} | {cnt[k]} |" for k in ORDER if cnt[k]], "",
         "- Cam kết hoàn tiền, bảo đảm KPI hay thứ hạng: chủ site quyết. Agent không tự viết câu cam kết mới.",
         "- Nhãn Jev dưới cổng và fact ở dải xám: Claude đọc rồi gán tay.",
         "- Lớp regex chỉ bắt cụm rõ. Câu không chạm dấu hiệu nào thì Jev không đọc."]
    if not a.jev_out and not nojev:
        L.append(f"- Chưa ghép Jev: chạy jev.py với tasks/claim-guard.json trên {out / 'jev_in.jsonl'}.")
    if facts and not a.fact_nn:
        L.append(f"- Chưa ghép Gemma: chạy emb.py nn --qprompt SentenceSimilarity --dprompt SentenceSimilarity --k 5 trên {out / 'fact_q.jsonl'}.")
    if a.fact_nn and not a.fact_jev_out and not nojev:
        L.append(f"- Chưa ghép Jev fact-match: chạy jev.py với tasks/fact-match.json trên {out / 'fact_jev_in.jsonl'}.")
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"claims: {len(sents)} câu, {len(flagged)} dòng claims.tsv, {len(jin)} câu cho Jev -> {out}", file=sys.stderr)


# ---------- rewrite: kiểm an toàn khi viết lại ----------

RW_RUBRIC = "rewrite-keep"
RW_QUERY = "rewrite-query-drop"
LOSS = ("dropped", "changed")
STOP = ("chặn", "cần đọc", "an toàn")


def task_version(name):
    return json.loads((Path(__file__).resolve().parents[1] / "tasks" / f"{name}.json").read_text(encoding="utf-8"))["version"]


def rw_entry(registry, site, rubric, version=None, question=None):
    for e, src in reg_entries(registry, site):
        if e.get("rubric") == rubric and (version is None or e.get("version") == version) \
                and (question is None or e.get("question") == question):
            return e, src
    return {}, None


def passages_of(lines, max_words=80):
    """Dòng chữ của trang thành passage: ghép câu trong một dòng tới tối đa max_words từ. Dòng dưới 3 từ bỏ qua."""
    out = []
    for line in lines:
        cur = ""
        for s in split_sentences(line):
            if cur and len((cur + " " + s).split()) > max_words:
                out.append(cur)
                cur = ""
            cur = (cur + " " + s).strip()
        if cur:
            out.append(cur)
    return [p for p in out if len(p.split()) >= 3]


def apply_pairs(lines, pairs):
    """Thay chữ cũ bằng chữ mới trong từng dòng của trang. Cặp không thấy chữ cũ thì trả về trong miss."""
    new, miss = list(lines), []
    for p in pairs:
        o, n = norm(p["old"]), norm(p["new"])
        hit = [i for i, l in enumerate(new) if o and o in l]
        if not hit:
            miss.append(p["id"])
        for i in hit:
            new[i] = new[i].replace(o, n)
    return new, miss


def pair_checks(p, erx, facts):
    """Luật tất định cho một cặp cũ/mới: số mất, số mới, entity mất, cụm cam kết hay xếp hạng mới, cụm cấm mới."""
    o, n = norm(p["old"]), norm(p["new"])
    rank = dict(L1)["#1"]
    no, nn = nums(rank.sub(" ", o)), nums(rank.sub(" ", n))  # "#1", "top 1" là cụm xếp hạng, không phải số liệu
    # Số mới chỉ coi là đã có trong bảng fact khi câu mới chứa đúng cách viết canon hoặc allowed của một fact có số đó.
    known = {v for f in facts for ph in [f.get("canon") or "", *(f.get("allowed") or [])] if ph and strict_rx(ph).search(n)
             for v in nums(ph)}
    l1o = {h["label"] for h in l1_hits(o) if not h["neg"]}
    l1n = {h["label"] for h in l1_hits(n) if not h["neg"]}
    return {"lost_num": sorted(no - nn), "new_num": sorted(nn - no), "new_num_unknown": sorted((nn - no) - known) if facts else sorted(nn - no),
            "lost_ent": sorted(entities_in(o, erx) - entities_in(n, erx)) if erx else [],
            "new_l1": sorted(l1n - l1o),
            "new_banned": sorted({b for f in facts for b in f.get("banned") or [] if strict_rx(b).search(n) and not strict_rx(b).search(o)})}


def strict_rx(p):
    """Như phrase_rx, thêm: cụm đứng sau dấu gạch nối không tính ("Co-founder X" không chạm cụm cấm "Founder X")."""
    return re.compile(phrase_rx(p).pattern.replace("(?<!\\w)", "(?<![\\w-])", 1), re.I)


def rw_decide(c, j, rb, acc, g_add, miss="chưa có nhãn Jev"):
    """Kết luận một cặp: chặn, cần đọc hoặc an toàn, kèm lý do. Không lệnh nào tự sửa trang."""
    why, stop = [], False
    promise = set(c["new_l1"]) & {"hoàn tiền", "cam kết kết quả"}
    if promise:
        why.append("thêm cam kết hoặc hoàn tiền: " + ", ".join(sorted(promise)))
        stop = True
    if c["new_banned"]:
        why.append("thêm cách viết cấm của bảng fact: " + ", ".join(c["new_banned"]))
        stop = True
    if c["lost_num"]:
        why.append(f"mất số {c['lost_num']}")
    if c["lost_ent"]:
        why.append(f"mất tên {c['lost_ent']}")
    if c["new_num_unknown"]:
        why.append(f"số mới chưa có trong bảng fact {c['new_num_unknown']}")
    rank = sorted(set(c["new_l1"]) - promise)
    if rank:
        why.append("thêm cụm xếp hạng: " + ", ".join(rank))
    if j is None:
        return ("chặn" if stop else "cần đọc"), why + [miss]
    if acc is not None and j["p_loss"] >= acc:
        why.append(f"Jev: {j['facts']}, P mất hoặc đổi fact {j['p_loss']:.2f} (qua cổng)")
    elif rb is not None and (j["facts"] in LOSS or j["p_loss"] >= rb):
        why.append(f"Jev nghi mất hoặc đổi fact: {j['facts']}, P {j['p_loss']:.2f}")
    elif rb is None and j["facts"] != "kept":
        why.append(f"Jev: {j['facts']}, P mất hoặc đổi fact {j['p_loss']:.2f} (chưa có cổng)")
    if j["added"] is not None:
        lab = jev_label(j["added"], g_add) if g_add else ("yes" if j["added"] >= 0.5 else "no")
        explained = c["new_num"] and not c["new_num_unknown"]  # số mới đều có trong bảng fact
        if lab == "yes" and not explained:  # dải giữa không ghi: pilot, nhãn yes qua cổng bắt đủ cặp thêm fact
            why.append(f"Jev: thêm fact hoặc lời hứa (p {j['added']:.2f})")
    return ("chặn" if stop else "cần đọc" if why else "an toàn"), why


def cmd_rewrite(a):
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pairs = [p for p in jl(a.pairs) if norm(p.get("old")) and norm(p.get("new")) and norm(p["old"]) != norm(p["new"])]
    if not pairs:
        sys.exit("pairs.jsonl không có cặp cũ/mới khác nhau")
    # Bản mới là chữ nháp chưa đăng: chỉ site của chính đơn vị vận hành (--own-site) mới gửi Jev.
    write(out / "rw_jev_in.jsonl", [{"id": p["id"], "state": {"page": p.get("url") or "", "old": norm(p["old"]), "new": norm(p["new"])}}
                                    for p in pairs if a.own_site])
    miss = "chưa có nhãn Jev" if a.own_site else "bản nháp site khách: Jev không đọc, Claude đọc"
    facts = load_facts(a.facts) if a.facts else []
    erx = entity_rx(a.entity, facts) if (facts or a.entity) else {}
    version = task_version(RW_RUBRIC)
    e_f, src = rw_entry(a.registry, a.site, RW_RUBRIC, version, "facts")
    e_a, _ = rw_entry(a.registry, a.site, RW_RUBRIC, version, "added")
    acc, rb = e_f.get("threshold"), e_f.get("reject_below")
    g_add = e_a.get("conf_gate") or e_a.get("threshold")
    jev = {}
    if a.jev_out:
        for r in jl(a.jev_out):
            if "answers" not in r:
                continue
            f = r["answers"].get("facts") or {}
            pr = f.get("probabilities") or {}
            ad = r["answers"].get("added") or {}
            jev[r["id"]] = {"facts": f.get("choice"), "p_loss": round(sum(float(pr.get(k) or 0) for k in LOSS), 4),
                            "added": ad.get("p_yes") if "p_yes" in ad else (ad.get("probabilities") or {}).get("yes")}
    drift = {}
    enc = None
    if a.embed:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
        import svi  # noqa: E402  (cùng bộ skill; chạy bằng venv embedding)
        enc = svi.encoder(512)
        vo = enc.encode([norm(p["old"]) for p in pairs], "SentenceSimilarity")
        vn = enc.encode([norm(p["new"]) for p in pairs], "SentenceSimilarity")
        drift = {p["id"]: round(float(x @ y), 4) for p, x, y in zip(pairs, vo, vn)}
    rows = []
    for p in pairs:
        c = pair_checks(p, erx, facts)
        j = jev.get(p["id"])
        dec, why = rw_decide(c, j, rb, acc, g_add, miss)
        rows.append({"id": p["id"], "url": p.get("url") or "", "decision": dec, "why": why, "checks": c,
                     "jev": j, "drift": drift.get(p["id"]), "old": norm(p["old"]), "new": norm(p["new"])})
    rows.sort(key=lambda r: (STOP.index(r["decision"]), -((r["jev"] or {}).get("p_loss") or 0)))
    write(out / "rewrite.jsonl", rows)
    with open(out / "rewrite.tsv", "w", encoding="utf-8") as fh:
        fh.write("decision\turl\tid\twhy\tp_loss\tdrift\told\tnew\n")
        for r in rows:
            fh.write("\t".join(str(x).replace("\t", " ") for x in (
                r["decision"], r["url"], r["id"], "; ".join(r["why"]), (r["jev"] or {}).get("p_loss", ""),
                "" if r["drift"] is None else r["drift"], r["old"], r["new"])) + "\n")
    qrows, qinfo = [], "chưa chạy: cần --embed, --pages và --gsc"
    if a.gsc and a.pages and enc is not None:
        qrows, qinfo = rw_queries(a, pairs, enc)
        with open(out / "queries.tsv", "w", encoding="utf-8") as fh:
            fh.write("status\turl\tquery\tclicks\timpressions\tcos_old\tcos_new\tdelta\ttouched\ttop_old\ttop_new\n")
            for q in qrows:
                fh.write("\t".join(str(q[k]).replace("\t", " ") for k in (
                    "status", "url", "query", "clicks", "impressions", "cos_old", "cos_new", "delta", "touched", "top_old", "top_new")) + "\n")
        write(out / "queries.jsonl", qrows)
    cnt = Counter(r["decision"] for r in rows)
    L = ["# Kiểm an toàn khi viết lại", "",
         f"{len(pairs)} cặp cũ/mới. Kết luận: {dict(cnt)}. Nhãn Jev: {len(jev)} cặp.",
         ("Site của chính đơn vị vận hành (--own-site): bản nháp được gửi Jev." if a.own_site else
          "Bản nháp site khách (không có --own-site): không gửi Jev, chỉ chạy code, cụm cấm và Gemma trên máy. "
          "Claude đọc mọi cặp."),
         f"Cổng `{RW_RUBRIC}` {version}: tự chốt {acc}, lọc dưới {rb} ({src or 'chưa có: Claude đọc mọi cặp Jev chưa ghi kept'}). "
         f"Cổng `added`: {g_add}.",
         f"Query mang click: {qinfo}.", "",
         "## Cặp cần xem", "", "| Kết luận | Trang | Lý do | Cũ | Mới |", "|---|---|---|---|---|"]
    for r in rows:
        if r["decision"] != "an toàn":
            L.append(f"| {r['decision']} | {r['url']} | {'; '.join(r['why'])} | {r['old'][:140].replace('|', ' ')} | {r['new'][:140].replace('|', ' ')} |")
    if qrows:
        risk = [q for q in qrows if q["status"] == "query cần đọc"]
        L += ["", "## Query mang click có passage khớp nhất bị sửa", "",
              f"{len(risk)} query cần đọc, tổng {sum(q['clicks'] for q in risk)} click trong kỳ GSC. Dữ liệu GSC chỉ xử lý trên máy, không gửi Jev.", "",
              "| Trang | Query | Click | Cos cũ → mới | Passage cũ |", "|---|---|---|---|---|"]
        for q in risk[:60]:
            L.append(f"| {q['url']} | {q['query']} | {q['clicks']} | {q['cos_old']} → {q['cos_new']} | {q['top_old'][:120].replace('|', ' ')} |")
    L += ["", "## Đọc kết quả", "",
          "- \"chặn\": bản mới thêm cam kết, hoàn tiền hoặc cách viết cấm. Không đăng; chủ site quyết câu cam kết.",
          "- \"cần đọc\": Claude so bản cũ, bản mới và bảng fact. Số mới chạy thêm lệnh `claims` trên bản mới.",
          "- Query cần đọc: bản mới làm passage khớp nhất của query yếu đi. Giữ ý trả lời query đó trong bản mới, hoặc ghi lý do bỏ.",
          "- Cosine cũ ↔ mới chỉ mô tả mức đổi chữ, không quyết định an toàn."]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"rewrite: {len(pairs)} cặp {dict(cnt)}, {len(qrows)} query -> {out}", file=sys.stderr)


def rw_queries(a, pairs, enc):
    """Query GSC mang click của từng trang: cosine tốt nhất tới passage của bản cũ và bản mới (Gemma local)."""
    import numpy as np
    pages = {p["url"]: p for p in jl(a.pages)}
    by_url = defaultdict(list)
    for p in pairs:
        by_url[p.get("url") or ""].append(p)
    gsc = defaultdict(list)
    with open(a.gsc, encoding="utf-8") as fh:
        for r in csv_rows(fh):
            if float(r.get("clicks") or 0) >= a.min_clicks:
                gsc[urlparse(r["page"]).path or "/"].append(r)
    e_q, _ = rw_entry(a.registry, a.site, RW_QUERY)
    delta_thr = e_q.get("threshold")
    cache = {}

    def vec(texts, prompt):
        need = [t for t in dict.fromkeys(texts) if (prompt, t) not in cache]
        if need:
            for t, v in zip(need, enc.encode(need, prompt)):
                cache[(prompt, t)] = v
        return np.asarray([cache[(prompt, t)] for t in texts]) if texts else np.zeros((0, 1))

    rows, miss_all, n_pages = [], [], 0
    for url, ps in by_url.items():
        page = pages.get(url)
        qs = gsc.get(urlparse(url).path or "/", [])
        if not page or not qs:
            continue
        n_pages += 1
        old_lines = [norm(l) for l in re.split(r"\s*(?:¶|\n)\s*", page.get("text") or "") if norm(l)]
        new_lines, miss = apply_pairs(old_lines, ps)
        miss_all += miss
        po, pn = passages_of(old_lines), passages_of(new_lines)
        Vo, Vn = vec(po, "Document"), vec(pn, "Document")
        Q = vec([r["query"] for r in qs], "SearchQuery")
        So, Sn = Q @ Vo.T, Q @ Vn.T
        newset = set(pn)
        for k, r in enumerate(qs):
            io, inn = int(So[k].argmax()), int(Sn[k].argmax())
            d = round(float(Sn[k, inn] - So[k, io]), 4)
            touched = po[io] not in newset
            st = ("query cần đọc" if (d <= -delta_thr if delta_thr is not None else (touched and d < 0))
                  else "giảm nhẹ" if d < 0 else "giữ")
            rows.append({"url": url, "query": r["query"], "clicks": int(float(r["clicks"])),
                         "impressions": int(float(r.get("impressions") or 0)), "cos_old": round(float(So[k, io]), 4),
                         "cos_new": round(float(Sn[k, inn]), 4), "delta": d, "touched": touched,
                         "top_old": po[io], "top_new": pn[inn], "status": st})
    rows.sort(key=lambda q: (q["status"] != "query cần đọc", q["delta"]))
    info = (f"{len(rows)} query ở {n_pages} trang; ngưỡng {RW_QUERY} {delta_thr if delta_thr is not None else 'chưa có (mọi query có passage khớp nhất bị sửa và cosine giảm)'}"
            + (f"; {len(miss_all)} cặp không thấy chữ cũ trên trang" if miss_all else ""))
    return rows, info


def csv_rows(fh):
    import csv
    csv.field_size_limit(10 ** 9)
    return csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--rows", required=True)
    p.add_argument("--pages", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--urls", default=None)
    p.add_argument("--max-chars", type=int, default=12000, help="Jev nhận tối đa khoảng 8K token")
    v = sub.add_parser("validate")
    v.add_argument("--jev-out", required=True)
    v.add_argument("--pools", required=True)
    v.add_argument("--out", required=True)
    r = sub.add_parser("report")
    r.add_argument("--jev-out", required=True)
    r.add_argument("--registry", default=None)
    r.add_argument("--site", default=None)
    r.add_argument("--out-dir", required=True)
    r.add_argument("--pools", default=None)
    r.add_argument("--own-domain", default=None)
    t = sub.add_parser("template")
    t.add_argument("--store", required=True)
    t.add_argument("--registry", default=None)
    t.add_argument("--site", default=None)
    t.add_argument("--out-dir", required=True)
    t.add_argument("--urls", default=None)
    t.add_argument("--gray", type=float, default=0.02, help="độ rộng dải review dưới ngưỡng trùng")
    c = sub.add_parser("claims")
    c.add_argument("--rows", action="append", help="JSONL có url + text (rows/blocks); lặp được")
    c.add_argument("--level", default="section", help="dòng có trường level thì chỉ lấy level này")
    c.add_argument("--pages", default=None, help="pages.jsonl: thêm title, meta, h1 và ngôn ngữ trang")
    c.add_argument("--text", action="append", help="file chữ; lặp được")
    c.add_argument("--url", default=None, help="URL gán cho file chữ")
    c.add_argument("--urls", default=None)
    c.add_argument("--out-dir", required=True)
    c.add_argument("--owner", default=None, help="tên chủ site cho Jev; mặc định là domain")
    c.add_argument("--lang", default="vi")
    c.add_argument("--facts", default=None, help="facts.json của site-fact-consistency")
    c.add_argument("--entity", action="append", help='bí danh entity, ví dụ "ACM=Acme SEO|ACM"; lặp được')
    c.add_argument("--site-entity", default=None, help="entity mặc định khi câu không nêu tên")
    c.add_argument("--jev-out", default=None)
    c.add_argument("--fact-nn", default=None, help="output emb.py nn trên fact_q.jsonl và fact_d.jsonl")
    c.add_argument("--fact-jev-out", default=None, help="output jev.py tasks/fact-match.json trên fact_jev_in.jsonl")
    c.add_argument("--registry", default=None)
    c.add_argument("--site", default=None)
    c.add_argument("--own-site", action="store_true", help="--text là bản nháp của site do chính đơn vị vận hành sở hữu: gửi Jev")
    w = sub.add_parser("rewrite")
    w.add_argument("--own-site", action="store_true", help="bản viết lại thuộc site của chính đơn vị vận hành: gửi Jev")
    w.add_argument("--pairs", required=True, help="JSONL {id, url, old, new}: đoạn đang có trên trang và đoạn viết lại")
    w.add_argument("--out-dir", required=True)
    w.add_argument("--pages", default=None, help="JSONL {url, text}: chữ trang hiện tại, mỗi khối một dòng")
    w.add_argument("--gsc", default=None, help="TSV page, query, clicks, impressions của GSC (chỉ xử lý trên máy)")
    w.add_argument("--min-clicks", type=float, default=1, help="chỉ xét query có từ ngần này click")
    w.add_argument("--embed", action="store_true", help="dùng EmbeddingGemma (chạy bằng venv): cosine cũ ↔ mới và query")
    w.add_argument("--facts", default=None, help="facts.json của site-fact-consistency")
    w.add_argument("--entity", action="append", help='bí danh entity, ví dụ "ACM=Acme SEO|ACM"; lặp được')
    w.add_argument("--jev-out", default=None, help="output jev.py tasks/rewrite-keep.json trên rw_jev_in.jsonl")
    w.add_argument("--registry", default=None)
    w.add_argument("--site", default=None)
    a = ap.parse_args()
    if a.cmd == "rewrite" and a.gsc and not (a.embed and a.pages):
        ap.error("rewrite --gsc cần --embed và --pages")
    if a.cmd == "claims" and not (a.rows or a.text):
        ap.error("claims cần --rows hoặc --text")
    if a.cmd == "claims" and a.text and not a.own_site and (a.jev_out or a.fact_jev_out):
        ap.error("bản nháp site khách (--text, không có --own-site) không ghép Jev")
    if a.cmd == "rewrite" and a.jev_out and not a.own_site:
        ap.error("bản nháp site khách (rewrite không có --own-site) không ghép Jev")
    {"prepare": cmd_prepare, "validate": cmd_validate, "report": cmd_report, "template": cmd_template,
     "claims": cmd_claims, "rewrite": cmd_rewrite}[a.cmd](a)


if __name__ == "__main__":
    main()
