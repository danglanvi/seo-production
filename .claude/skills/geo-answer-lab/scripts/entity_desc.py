#!/usr/bin/env python3
"""Nhất quán mô tả entity: gom đoạn mô tả brand từ nguồn công khai, so với mô tả chính thức và facts.json.

Lệnh:
  collect --sources sources.tsv --brands brands.json --out passages.jsonl [--raw raw.jsonl] [--paste-dir DIR]
          [--save-dir DIR] [--max-per-source 12]
      sources.tsv: cột url, kind (about, home, gbp, linkedin, press, directory, toplist, social, other). Chỉ GET trang công khai.
      Trang cần đăng nhập (LinkedIn, GBP): dán chữ vào <paste-dir>/<kind>__<tên>.txt, dòng đầu là URL.
      --raw: raw.jsonl của collect.py; lấy đoạn câu trả lời AI có nhắc brand chính (kind ai:<engine>).
  prepare --passages passages.jsonl --brands brands.json --canon canon.txt --out-dir DIR
      Ra services_in.jsonl (rubric entity-desc: mô tả brand khớp mô tả chính thức không) và claims_in.jsonl
      (rubric company-fact-claim: số đứng cạnh nhãn, đánh dấu ⟦...⟧).
  gold-sheet --passages passages.jsonl --n 60 --seed 19 --out sheet.jsonl [--skip ids.txt] [--enrich REGEX]
      Lấy mẫu đoạn để gán gold mù cho rubric entity-desc: nửa từ câu trả lời AI, nửa từ trang web. Gán "services"
      (consistent, different, not_described) trước khi xem nhãn Jev hay cosine. --enrich: một nửa mẫu lấy từ đoạn
      khớp regex chữ, để holdout có đủ đoạn lệch (lớp hiếm).
  embed --passages passages.jsonl --canon canon.txt --out cos.jsonl   (venv EmbeddingGemma)
      Cosine giữa từng đoạn và mô tả chính thức, prompt SentenceSimilarity. Chỉ để xếp và tóm tắt theo nguồn:
      cosine không tách được đoạn lệch (đoạn lệch vẫn nói về SEO nên cosine cao).
  report --passages passages.jsonl --facts facts.json --dir DIR [--registry model-calibration.json --site <domain>]
      Đọc services_out.jsonl, claims_out.jsonl, cos.jsonl trong DIR. So số với facts.json bằng luật tất định,
      tìm cụm "cách viết cấm" của facts.json. Ra issues.tsv, summary.json, entity_report.md.
      Cổng entity-desc đọc từ registry, rồi calibration-defaults.json, theo version trong tasks/entity-desc.json:
      threshold = P(different) từ ngưỡng này thì tự chốt "mô tả dịch vụ lệch"; reject_below = dưới ngưỡng này và
      Jev không chọn different thì bỏ qua. Không có entry: Claude đọc mọi đoạn có mô tả.
Jev chỉ nhận chữ công khai: đoạn mô tả, mô tả chính thức, tên brand. Không gửi GSC, hợp đồng, email.
"""
import argparse
import csv
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

TASKS = Path(__file__).resolve().parents[1] / "tasks"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "blockquote", "dd"}
SKIP = {"script", "style", "template", "svg", "nav", "footer", "form", "head"}
NUM = r"(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)"
# Nhãn đi sau số mà facts.json có thể so. Lọc trước để Jev chỉ nhận số có khả năng là fact của brand.
UNIT = (r"năm|dự án|doanh nghiệp|khách hàng|thương hiệu|đối tác|nhân sự|nhân viên|chuyên gia|thành viên|học viên|"
        r"khoá|khóa|website|traffic|lượt|người|sự kiện|event|%|years?|projects?|clients?|businesses|employees|"
        r"experts?|students?|members?|subscribers?")
CLAIM = re.compile(NUM + r"\s*(\+|k\b|triệu|tr\b|million)?\s*(" + UNIT + r")", re.I)
YEAR = re.compile(r"(?:từ|năm|thành lập|ra đời|since|founded(?: in)?|established(?: in)?)\s*(?:năm\s*)?((?:19|20)\d{2})\b", re.I)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()] if Path(p).exists() else []


def write(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def brand_rx(cfg):
    own = cfg["own"]
    b = cfg["brands"][own]
    parts = [b["regex"]] + [re.escape(a.lower()) for a in b.get("aliases", []) if len(a) > 3]
    return re.compile("|".join(parts), re.I)


class Blocks(HTMLParser):
    """Khối chữ theo thứ tự trên trang: (thẻ, chữ). Bỏ script, style, nav, footer, form. Đếm theo từng thẻ."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.cur, self.buf = [], Counter(), None, []
        self.meta, self.ld = {}, []
        self._ld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and (a.get("name") or a.get("property") or "").lower() in ("description", "og:description"):
            self.meta[(a.get("name") or a.get("property")).lower()] = a.get("content") or ""
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._ld, self.buf_ld = True, []
            return
        if tag in SKIP:
            self.skip[tag] += 1
        elif tag in BLOCK and not sum(self.skip.values()):
            self.flush()
            self.cur, self.buf = tag, []

    def handle_endtag(self, tag):
        if tag == "script" and self._ld:
            self._ld = False
            self.ld.append("".join(self.buf_ld))
            return
        if tag in SKIP and self.skip[tag]:
            self.skip[tag] -= 1
        elif tag == self.cur:
            self.flush()

    def handle_data(self, d):
        if self._ld:
            self.buf_ld.append(d)
        elif self.cur and not sum(self.skip.values()):
            self.buf.append(d)

    def flush(self):
        if self.cur:
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if t:
                self.out.append((self.cur, t))
        self.cur, self.buf = None, []


def ld_descriptions(ld_texts, rx):
    out = []

    def walk(o):
        if isinstance(o, dict):
            if rx.search(str(o.get("name") or "")) and isinstance(o.get("description"), str):
                out.append(html.unescape(o["description"]))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for t in ld_texts:
        try:
            walk(json.loads(t))
        except ValueError:
            continue
    return out


def split_long(t, limit=700):
    if len(t) <= limit:
        return [t]
    sents = re.split(r"(?<=[.!?])\s+", t)
    out, cur = [], ""
    for s in sents:
        if cur and len(cur) + len(s) > limit:
            out.append(cur)
            cur = ""
        cur = (cur + " " + s).strip()
    return out + ([cur] if cur else [])


def passages_from_html(page, rx, max_n):
    p = Blocks()
    try:
        p.feed(page)
    except Exception:  # HTML hỏng: giữ phần đã đọc
        pass
    p.flush()
    found, seen = [], set()

    def add(text, section=""):
        for t in split_long(text):
            if len(t) >= 30 and t not in seen:
                seen.add(t)
                found.append({"text": t, "section": section})

    for k in ("description", "og:description"):
        if rx.search(p.meta.get(k, "")):
            add(p.meta[k], "meta " + k)
    for d in ld_descriptions(p.ld, rx):
        add(d, "JSON-LD")
    blocks, i = p.out, 0
    while i < len(blocks):
        tag, t = blocks[i]
        if tag[0] == "h" and rx.search(t):  # mục về brand: lấy các khối tới heading cùng cấp hoặc cao hơn
            lvl, j = int(tag[1]), i + 1
            while j < len(blocks) and j - i <= 15 and not (blocks[j][0][0] == "h" and int(blocks[j][0][1]) <= lvl):
                if blocks[j][0][0] != "h":
                    add(blocks[j][1], t[:120])
                j += 1
            i = j
            continue
        if tag[0] != "h" and rx.search(t):
            add(t)
        i += 1
    return found[:max_n]


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    for attempt in range(2):  # lỗi mạng thoáng qua: thử lại một lần
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read(3_000_000).decode("utf-8", "ignore")
        except urllib.error.HTTPError:
            raise
        except Exception:
            if attempt:
                raise
            time.sleep(3)


def cmd_collect(a):
    cfg = json.loads(Path(a.brands).read_text(encoding="utf-8"))
    rx = brand_rx(cfg)
    rows, log = [], []
    with open(a.sources, encoding="utf-8") as fh:
        srcs = [r for r in csv.DictReader(fh, delimiter="\t") if (r.get("url") or "").strip()]
    for s in srcs:
        url, kind = s["url"].strip(), (s.get("kind") or "other").strip()
        try:
            st, page = get(url)
            time.sleep(0.5)
        except Exception as x:
            log.append({"url": url, "kind": kind, "status": getattr(x, "code", None) or type(x).__name__, "passages": 0})
            continue
        if a.save_dir:
            Path(a.save_dir).mkdir(parents=True, exist_ok=True)
            (Path(a.save_dir) / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")).write_text(page, encoding="utf-8")
        ps = passages_from_html(page, rx, a.max_per_source)
        log.append({"url": url, "kind": kind, "status": st, "passages": len(ps)})
        for k, p in enumerate(ps):
            rows.append({"id": f"{url}#{k}", "url": url, "kind": kind, **p})
    if a.paste_dir:
        for f in sorted(Path(a.paste_dir).glob("*.txt")):
            lines = f.read_text(encoding="utf-8").splitlines()
            url, kind = (lines[0].strip() if lines else f.name), f.stem.split("__")[0]
            ps = [t for t in split_long(" ".join(l.strip() for l in lines[1:] if l.strip())) if rx.search(t)]
            log.append({"url": url, "kind": kind, "status": "dán tay", "passages": len(ps)})
            rows += [{"id": f"{url}#p{k}", "url": url, "kind": kind, "text": t, "section": "dán tay"} for k, t in enumerate(ps)]
    if a.raw:
        best = {}
        for r in jl(a.raw):
            if r.get("ok") and r.get("answer"):
                best[(r["prompt_id"], r["engine"], r["run"])] = r
        for (pid, eng, run), r in sorted(best.items()):
            for k, para in enumerate(re.split(r"\n\s*\n", r["answer"])):
                para = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", para)  # bỏ link Markdown, giữ chữ
                para = re.sub(r"\s+", " ", para.replace("**", "")).strip()
                if rx.search(para) and len(para) >= 30:
                    for m, t in enumerate(split_long(para)):
                        if rx.search(t):
                            rows.append({"id": f"ai|{pid}|{eng}|{run}|{k}.{m}", "url": f"ai:{eng}", "kind": f"ai:{eng}",
                                         "text": t, "section": pid})
    write(a.out, rows)
    write(Path(a.out).with_name("sources_log.jsonl"), log)
    print(f"collect: {len(rows)} đoạn từ {len(log)} nguồn (+AI nếu có) -> {a.out}", file=sys.stderr)


def cmd_prepare(a):
    cfg = json.loads(Path(a.brands).read_text(encoding="utf-8"))
    own = cfg["own"]
    canon = Path(a.canon).read_text(encoding="utf-8").strip()
    aliases = cfg["brands"][own].get("aliases", [])
    svc, claims = [], []
    for p in jl(a.passages):
        svc.append({"id": p["id"], "state": {"brand": own, "aliases": aliases, "canon": canon, "passage": p["text"]}})
        for k, m in enumerate(list(CLAIM.finditer(p["text"])) + list(YEAR.finditer(p["text"]))):
            s, e = m.span()
            claims.append({"id": f"{p['id']}~{k}", "state": {
                "site_profile": canon, "page": p["url"], "snippet": p["text"][:s] + "⟦" + p["text"][s:e] + "⟧" + p["text"][e:]},
                "match": p["text"][s:e], "passage_id": p["id"]})
    od = Path(a.out_dir)
    write(od / "services_in.jsonl", svc)
    write(od / "claims_in.jsonl", [{"id": c["id"], "state": c["state"]} for c in claims])
    write(od / "claims_index.jsonl", [{"id": c["id"], "passage_id": c["passage_id"], "match": c["match"]} for c in claims])
    print(f"prepare: {len(svc)} đoạn cho entity-desc, {len(claims)} số cho company-fact-claim -> {od}", file=sys.stderr)


def cmd_gold_sheet(a):
    import random
    skip = set(Path(a.skip).read_text(encoding="utf-8").split()) if a.skip else set()
    pool = [p for p in jl(a.passages) if p["id"] not in skip]
    ai = sorted((p for p in pool if p["kind"].startswith("ai:")), key=lambda p: p["id"])
    web = sorted((p for p in pool if not p["kind"].startswith("ai:")), key=lambda p: p["id"])
    rnd = random.Random(a.seed)
    pick = []
    if a.enrich:  # lớp hiếm (mô tả lệch): lấy một nửa mẫu từ đoạn khớp regex chữ, không dùng nhãn hay điểm model
        rx = re.compile(a.enrich, re.I)
        hit = sorted((p for p in pool if rx.search(p["text"])), key=lambda p: p["id"])
        pick = rnd.sample(hit, min(len(hit), a.n // 2))
        chosen = {p["id"] for p in pick}
        ai = [p for p in ai if p["id"] not in chosen]
        web = [p for p in web if p["id"] not in chosen]
    rest = a.n - len(pick)
    pick += rnd.sample(ai, min(len(ai), rest // 2)) + rnd.sample(web, min(len(web), rest - rest // 2))
    write(a.out, [{"id": p["id"], "kind": p["kind"], "url": p["url"], "text": p["text"], "services": None} for p in pick])
    print(f"gold-sheet: {len(pick)} đoạn -> {a.out}. Gán services trước khi xem nhãn Jev.", file=sys.stderr)


def cmd_embed(a):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
    import numpy as np
    import svi
    ps = jl(a.passages)
    canon = Path(a.canon).read_text(encoding="utf-8").strip()
    enc = svi.encoder(512)
    V = enc.encode([p["text"] for p in ps], a.prompt)
    c = enc.encode([canon], a.prompt)[0]
    cos = V @ c
    write(a.out, [{"id": p["id"], "cos": round(float(x), 4)} for p, x in zip(ps, cos)])
    print(f"embed: {len(ps)} đoạn, cosine trung vị {float(np.median(cos)):.3f} -> {a.out}", file=sys.stderr)


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def entry(registry, site, rubric, version, question):
    """Entry hiệu chuẩn: registry của site trước, rồi calibration-defaults.json."""
    for path, want in ((registry, site), (find_defaults(), None)):
        if not path or not Path(path).exists():
            continue
        for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
            if (e.get("rubric") == rubric and e.get("version") == version and e.get("question") in (question, None)
                    and (want is None or e.get("site") == want)):
                return e, ("site" if want else "defaults")
    return None, None


def gate(registry, site, rubric, version, question):
    e, src = entry(registry, site, rubric, version, question)
    g = e and (e.get("conf_gate") or e.get("threshold"))
    return (float(g), src) if g is not None else (None, None)


def task_version(name):
    return json.loads((TASKS / f"{name}.json").read_text(encoding="utf-8"))["version"]


def value(match):
    m = re.search(NUM, match)
    if not m:
        return None
    s = m.group(1)
    v = float(re.sub(r"[.,]", "", s)) if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", s) else float(s.replace(",", "."))
    if re.search(r"triệu|million|\btr\b", match, re.I):
        v *= 1_000_000
    elif re.search(r"\d\s*k\b", match, re.I):
        v *= 1000
    return v


def answer(row, q):
    x = (row.get("answers") or {}).get(q) or {}
    return x.get("choice"), float(x.get("confidence") or 0)


def p_of(row, q, label):
    return float((((row.get("answers") or {}).get(q) or {}).get("probabilities") or {}).get(label) or 0)


def src(p):
    """Câu trả lời AI ghi id (prompt, engine, lượt) để tìm lại trong raw.jsonl; trang web ghi URL."""
    return p["id"] if p["kind"].startswith("ai:") else p["url"]


def cmd_report(a):
    ps = {p["id"]: p for p in jl(a.passages)}
    facts = json.loads(Path(a.facts).read_text(encoding="utf-8"))
    d = Path(a.dir)
    svc = {r["id"]: r for r in jl(d / "services_out.jsonl")}
    cl = {r["id"]: r for r in jl(d / "claims_out.jsonl")}
    idx = jl(d / "claims_index.jsonl")
    cos = {r["id"]: r["cos"] for r in jl(d / "cos.jsonl")} if (d / "cos.jsonl").exists() else {}  # Gemma tuỳ chọn
    e_svc, src_svc = entry(a.registry, a.site, "entity-desc", task_version("entity-desc"), "services")
    e_svc = e_svc or {}
    acc, rb = e_svc.get("conf_gate") or e_svc.get("threshold"), e_svc.get("reject_below")
    g_sub, _ = gate(a.registry, a.site, "company-fact-claim", task_version("company-fact-claim"), "subject")
    g_met, _ = gate(a.registry, a.site, "company-fact-claim", task_version("company-fact-claim"), "metric")
    g_sub, g_met = g_sub or 0.5, g_met or 0.83  # ngưỡng đã hiệu chuẩn 17/10 (README tools/web-ai-assist §5)
    ent = a.entity.lower()
    fx = {(f["entity"].lower(), f["metric"]): f for f in facts}

    def fact_for(subject, metric):
        """Số của công ty so với fact của brand; số của người sáng lập so với fact của người sáng lập (thiếu thì lấy bên kia)."""
        fo = (a.founder or "").lower()
        first, second = (ent, fo) if subject == "company" else (fo, ent)
        return fx.get((first, metric)) or fx.get((second, metric))
    issues, svc_seen = [], Counter()
    for i in idx:
        r = cl.get(i["id"])
        if not r:
            continue
        sub, cs = answer(r, "subject")
        met, cm = answer(r, "metric")
        p = ps[i["passage_id"]]
        if sub not in ("company", "founder"):
            continue
        if cs < g_sub or cm < g_met:
            issues.append({"type": "số cần đọc", "passage": p, "found": i["match"], "fact_id": "", "canon": "",
                           "note": f"Jev dưới cổng: subject {sub} {cs:.2f}, metric {met} {cm:.2f}"})
            continue
        f = fact_for(sub, met)
        if not f or f.get("value") is None:
            continue
        v = value(i["match"]) if met != "founding_year" else float(re.search(r"(?:19|20)\d{2}", i["match"]).group(0))
        if v is None or v == f["value"]:
            continue
        kind = "nói quá" if v > f["value"] else "lệch hoặc cũ"
        if met in ("founding_year", "years_experience"):
            kind = "lệch năm"
        issues.append({"type": kind, "passage": p, "found": i["match"], "fact_id": f["id"], "canon": f["canon"], "note": ""})
    for p in ps.values():
        low, hit = p["text"].lower(), set()
        for f in facts:
            for b in f.get("banned") or []:
                if b and b.lower() in low and b.lower() not in hit:  # một cụm cấm ghi một lần mỗi đoạn
                    hit.add(b.lower())
                    issues.append({"type": "cách viết cấm", "passage": p, "found": b, "fact_id": f["id"], "canon": f["canon"],
                                   "note": ""})
        r = svc.get(p["id"])
        if r:
            ch, _ = answer(r, "services")
            pd = p_of(r, "services", "different")
            svc_seen[ch] += 1
            if acc is not None and pd >= float(acc):  # cổng tự chốt: precision đạt trên holdout
                issues.append({"type": "mô tả dịch vụ lệch", "passage": p, "found": "", "fact_id": "", "canon": "",
                               "note": f"Jev P(lệch) {pd:.2f}", "pd": pd})
            elif rb is not None:  # cổng lọc: dưới ngưỡng và Jev không chọn different thì bỏ qua
                if ch == "different" or pd >= float(rb):
                    issues.append({"type": "mô tả cần đọc", "passage": p, "found": "", "fact_id": "", "canon": "",
                                   "note": f"Jev nghi lệch: {ch}, P(lệch) {pd:.2f}", "pd": pd})
            elif ch in ("different", "consistent"):  # chưa có cổng: Claude đọc mọi đoạn có mô tả
                issues.append({"type": "mô tả cần đọc", "passage": p, "found": "", "fact_id": "", "canon": "",
                               "note": f"Jev {ch}, P(lệch) {pd:.2f}, chưa có cổng", "pd": pd})
    # Gemma: độ gần mô tả chính thức theo nguồn (chỉ mô tả, không quyết định)
    per_src = defaultdict(list)
    for pid, p in ps.items():
        per_src[(p["kind"], p["url"])].append(cos.get(pid))
    flagged = Counter(i["passage"]["url"] for i in issues if i["type"] not in ("số cần đọc", "mô tả cần đọc"))
    rows = sorted(({"kind": k, "url": u, "passages": len(v), "issues": flagged.get(u, 0),
                    "cos_mean": round(sum(v) / len(v), 4) if None not in v else None} for (k, u), v in per_src.items()),
                  key=lambda x: (x["cos_mean"] is None, x["cos_mean"] or 0))
    with open(d / "issues.tsv", "w", encoding="utf-8") as fh:
        fh.write("type\tkind\turl\tfound\tfact_id\tcanon\tnote\tpassage\n")
        for i in issues:
            p = i["passage"]
            fh.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in
                               (i["type"], p["kind"], src(p), i["found"], i["fact_id"], i["canon"], i["note"], p["text"])) + "\n")
    summary = {"passages": len(ps), "sources": len({p["url"] for p in ps.values()}), "issues": dict(Counter(i["type"] for i in issues)),
               "jev_services": dict(svc_seen), "gate_services": {"accept": acc, "reject_below": rb, "source": src_svc},
               "by_source": rows}
    (d / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Nhất quán mô tả entity", "",
         f"{summary['passages']} đoạn từ {summary['sources']} nguồn. Lỗi theo loại: {summary['issues']}.",
         f"Jev `entity-desc` theo nhãn: {dict(svc_seen)}.",
         f"Cổng `entity-desc`: tự chốt {acc}, lọc dưới {rb} ({src_svc or 'chưa có: Claude đọc mọi đoạn có mô tả'}).", "",
         "## Nguồn theo độ gần mô tả chính thức (Gemma, thấp trước)", "",
         "| Loại | Nguồn | Đoạn | Cosine TB | Lỗi đã chốt |", "|---|---|---|---|---|"]
    L += [f"| {r['kind']} | {r['url']} | {r['passages']} | {r['cos_mean']} | {r['issues']} |" for r in rows]
    L += ["", "## Lỗi", "", "| Loại lỗi | Nguồn | Chữ tìm thấy | Fact chuẩn | Ghi chú | Đoạn |", "|---|---|---|---|---|---|"]
    order = ["lệch năm", "lệch hoặc cũ", "nói quá", "cách viết cấm", "mô tả dịch vụ lệch", "số cần đọc", "mô tả cần đọc"]
    for i in sorted(issues, key=lambda x: (order.index(x["type"]), -x.get("pd", 0))):
        p = i["passage"]
        L.append(f"| {i['type']} | {src(p)} | {i['found']} | {i['fact_id']} {i['canon']} | {i['note']} | {p['text'][:160]} |")
    L += ["", "## Việc tiếp theo", "",
          "- Lỗi trên site của brand: chuyển skill `site-fact-consistency` (sửa theo facts.json, ghi qua `wp-content-review-apply`).",
          "- Lỗi ở nguồn ngoài (báo, directory, top list, hồ sơ): ghi vào danh sách xin sửa của `geo-offsite-audit`.",
          "- Lỗi trong câu trả lời AI: tìm nguồn AI trích trong `citations.jsonl` cùng câu trả lời, sửa nguồn đó trước.",
          "- Tên khách, tên cộng đồng, giải thưởng chưa có trong facts.json: Claude đối chiếu wiki Company, không tự kết luận."]
    (d / "entity_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"report: {len(issues)} mục -> {d / 'entity_report.md'}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--sources", required=True)
    c.add_argument("--brands", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--raw")
    c.add_argument("--paste-dir")
    c.add_argument("--save-dir")
    c.add_argument("--max-per-source", type=int, default=12)
    p = sub.add_parser("prepare")
    for f in ("passages", "brands", "canon", "out-dir"):
        p.add_argument("--" + f, required=True)
    g = sub.add_parser("gold-sheet")
    g.add_argument("--passages", required=True)
    g.add_argument("--n", type=int, default=60)
    g.add_argument("--seed", type=int, default=19)
    g.add_argument("--skip")
    g.add_argument("--enrich", help="regex chữ để lấy thêm mẫu lớp hiếm, ví dụ 'inbound|digital marketing'")
    g.add_argument("--out", required=True)
    e = sub.add_parser("embed")
    for f in ("passages", "canon", "out"):
        e.add_argument("--" + f, required=True)
    e.add_argument("--prompt", default="SentenceSimilarity")
    r = sub.add_parser("report")
    for f in ("passages", "facts", "dir"):
        r.add_argument("--" + f, required=True)
    r.add_argument("--registry")
    r.add_argument("--site")
    r.add_argument("--entity", required=True, help="chủ thể công ty trong facts.json, ví dụ Alpha")
    r.add_argument("--founder", default="", help="chủ thể người sáng lập trong facts.json (nếu có)")
    a = ap.parse_args()
    {"collect": cmd_collect, "prepare": cmd_prepare, "gold-sheet": cmd_gold_sheet, "embed": cmd_embed,
     "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
