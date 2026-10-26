#!/usr/bin/env python3
"""visual-serp-lab: ảnh trong bài so với alt và mục chứa ảnh; màn đầu của trang so với trang được AI trích.

Nhánh media (images, fetch: Python có beautifulsoup4 + Pillow; embed: venv embedding):
  images  --html-dir DIR --out images.jsonl [--min-width 80]
          Ảnh trong main content (luật chọn vùng của site-vector-index): src, alt, caption, H2, H3, mục chứa ảnh.
          Code gắn cờ: missing_alt, fileish_alt (alt dạng tên file), alt_reused (một alt cho nhiều ảnh khác nhau).
          Ghi thêm sections.jsonl (chữ của từng mục) cạnh images.jsonl.
  fetch   --images images.jsonl --cache DIR --out sample.jsonl [--per-page 2 | --all] [--seed 19] [--delay 0.15]
          Tải ảnh công khai, lưu PNG cạnh dài tối đa 768. Mặc định lấy mẫu ảnh nội dung có alt.
  embed   --sample sample.jsonl --sections sections.jsonl --out W/media.jsonl
          EmbeddingGemma: ảnh (không prompt), alt (SearchQuery), mục (Document). Ra alt_cos, sec_cos, sec_margin.
  jev-in  --media W/media.jsonl --out W/jev_media_in.jsonl
          Input Jev rubric image-fit. Ảnh có cạnh dưới 320 px được đệm nền trắng: Jev trả http_400 với ảnh nhỏ.
  pairs   --media W/media.jsonl --jev-out W/jev_media_out.jsonl --gold gold_alt.jsonl --out W/calibration/alt_score_pairs.jsonl
          Điểm alt-score của ảnh có gold (label yes = alt tả đúng ảnh), cho calibrate.py cosine --grid.
  media  --images images.jsonl --media W/media.jsonl --jev-out W/jev_media_out.jsonl --registry R --site D --out-dir W
          Cổng: alt-score (điểm = p alt_matches + 2 × alt_cos, ngưỡng loại) và image-fit fits_section (Jev).
Nhánh layout:
  shoot   --urls urls.txt --out-dir DIR [--width 1366 --height 900]
          Chụp màn đầu bằng Chrome headless. Mobile dưới 500 px: dùng iframe wrapper (Chrome ép tối thiểu 500 px).
  jev-in  --shots DIR/shots.jsonl --pools pools.jsonl --out W/jev_layout_in.jsonl
          Input Jev rubric first-screen, mỗi cặp pool × URL một dòng (câu answer_visible phụ thuộc truy vấn).
  layout  --jev-out W/jev_layout_out.jsonl --pools pools.jsonl --registry R --site D --own-domain D --out-dir W
          Tỷ lệ trang có từng đặc điểm ở màn đầu: được trích so với không được trích, trang của mình. Ra auc_rows.jsonl.
Cosine ảnh–chữ dồn trong dải hẹp và khác thang cosine chữ–chữ: hiệu chuẩn theo site trước khi đặt ngưỡng.
"""
import argparse
import hashlib
import io
import json
import random
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (compatible; GTV-SVI/1.0; +visual-serp-lab)"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VI = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)
ALT_W = 2  # trọng số alt_cos trong điểm alt, chọn trên gold dev
FEATURES = ("answer_visible", "price", "form", "trust", "byline", "media", "toc", "covered")


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def write(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def key(s):
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def task_version(name):
    return json.loads((Path(__file__).resolve().parents[1] / "tasks" / f"{name}.json").read_text(encoding="utf-8"))["version"]


def fileish(alt):
    """Alt dạng tên file: 'ui ux 10', 'pic3', 'Group35', 'shopify la gi 08'. Đúng 20/20 ca trên gold pilot."""
    a = unicodedata.normalize("NFC", (alt or "").strip())
    if not a:
        return False
    if re.fullmatch(r"(img|image|pic|picture|photo|anh|ảnh|group|frame|screenshot|untitled)[\s_-]*\d*", a, re.I):
        return True
    return bool(re.search(r"\d+$", a)) and not VI.search(a) and len(a.split()) <= 7 and not re.search(r"\b(19|20)\d\d$", a)


def best_src(img, base):
    for k in ("data-lazy-src", "data-src", "data-original", "src"):
        v = img.get(k)
        if v and not v.startswith("data:"):
            return urljoin(base, v.strip().strip("”\""))
    ss = img.get("data-lazy-srcset") or img.get("srcset") or ""
    cands = [x.strip().split(" ")[0] for x in ss.split(",") if x.strip()]
    return urljoin(base, cands[-1]) if cands else ""


def cmd_images(a):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site-vector-index" / "scripts"))
    import extract as X  # noqa: E402  (cùng bộ skill: pick_main, strip_noise, nfc)
    from bs4 import BeautifulSoup
    out, sections = [], []
    for f in sorted(Path(a.html_dir).glob("*.html")):
        uf = f.with_suffix(".url")
        if not uf.exists():
            continue
        url = uf.read_text(encoding="utf-8").strip()
        main, _ = X.pick_main(BeautifulSoup(f.read_text(encoding="utf-8", errors="ignore"), "html.parser"))
        X.strip_noise(main)
        sec, h2, h3, prev, blocks, heads, imgs = 0, "", "", "", defaultdict(list), {0: ""}, []
        for el in main.find_all(["h2", "h3", "p", "li", "img", "figcaption"]):
            if el.name == "h2":
                sec, h2, h3 = sec + 1, X.nfc(el.get_text(" ")), ""
                heads[sec] = h2
                continue
            if el.name == "h3":
                h3 = X.nfc(el.get_text(" "))
                continue
            if el.name == "img":
                src = best_src(el, url)
                if not src or src.lower().split("?")[0].endswith(".svg"):
                    continue
                try:
                    if el.get("width") and int(str(el["width"]).replace("px", "")) < a.min_width:
                        continue
                except ValueError:
                    pass
                fig = el.find_parent("figure")
                cap = fig.find("figcaption") if fig else None
                imgs.append({"page": url, "src": src, "alt": X.nfc(el.get("alt", "")),
                             "caption": X.nfc(cap.get_text(" ")) if cap else "", "sec": sec, "h2": h2, "h3": h3,
                             "prev": prev[:400]})
                continue
            t = X.nfc(el.get_text(" "))
            if t:
                blocks[sec].append(t)
                prev = t
        secs = {k: (heads.get(k, "") + ": " if heads.get(k) else "") + " ".join(v)[:3000] for k, v in blocks.items()
                if len(" ".join(v).split()) >= 20}
        for i, im in enumerate(imgs):
            im["id"] = f"{url}#img{i}"
            im["section_text"] = secs.get(im["sec"], "")
            out.append(im)
        sections += [{"page": url, "sec": k, "text": v} for k, v in secs.items()]
    n_src, alt_src = Counter(x["src"] for x in out), defaultdict(set)
    for x in out:
        if x["alt"]:
            alt_src[x["alt"].casefold()].add(x["src"])
    for x in out:
        x["src_count"] = n_src[x["src"]]
        x["alt_reused"] = len(alt_src[x["alt"].casefold()]) if x["alt"] else 0
        x["flags"] = [f for f, on in (("missing_alt", not x["alt"]), ("fileish_alt", fileish(x["alt"])),
                                      ("alt_reused", x["alt_reused"] > 1)) if on]
    write(a.out, out)
    write(Path(a.out).with_name("sections.jsonl"), sections)
    c = Counter(f for x in out for f in x["flags"])
    print(f"{len(out)} ảnh, {len({x['page'] for x in out})} trang, {len(n_src)} src, cờ {dict(c)}")


def cmd_fetch(a):
    from PIL import Image
    rows = jl(a.images)
    if a.all:
        pick = rows
    else:
        r, by = random.Random(a.seed), defaultdict(list)
        for x in rows:
            if x["src_count"] == 1 and x["alt"]:
                by[x["page"]].append(x)
        pick = [y for xs in by.values() for y in r.sample(xs, min(a.per_page, len(xs)))]
    cache, ok = Path(a.cache), []
    cache.mkdir(parents=True, exist_ok=True)
    for x in pick:
        dst = cache / f"{key(x['src'])}.png"
        if not dst.exists():
            try:
                req = urllib.request.Request(x["src"], headers={"User-Agent": UA})
                im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=20).read(8_000_000))).convert("RGB")
            except Exception:
                continue
            if min(im.size) < 64:
                continue
            im.thumbnail((768, 768))
            im.save(dst)
            time.sleep(a.delay)
        ok.append({**x, "img": str(dst.resolve())})
    write(a.out, ok)
    print(f"{len(ok)}/{len(pick)} ảnh -> {a.out}")


def cmd_embed(a):
    rows = jl(a.sample)
    # Đường dẫn ảnh không tồn tại thì SentenceTransformer encode chuỗi đường dẫn như chữ, không báo lỗi.
    miss = [x["img"] for x in rows if not Path(x["img"]).is_file()]
    if miss:
        sys.exit(f"{len(miss)} ảnh không tìm thấy (vd {miss[0]}): chạy từ thư mục đúng hoặc dùng đường dẫn tuyệt đối")
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    pages = {x["page"] for x in rows}
    secs = [s for s in jl(a.sections) if s["page"] in pages]
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    # Có nhánh ảnh: không tắt vision_config. bfloat16: float16 cho NaN với model này.
    m = SentenceTransformer("google/embeddinggemma-2", device=dev, model_kwargs={"torch_dtype": torch.bfloat16})

    def enc(xs, prompt=None):
        kw = {"prompt_name": prompt} if prompt else {}
        return np.asarray(m.encode(xs, batch_size=8, normalize_embeddings=True, convert_to_numpy=True,
                                   show_progress_bar=False, **kw), dtype=np.float64)

    I = enc([x["img"] for x in rows])
    A = enc([x["alt"] or "ảnh" for x in rows], "SearchQuery")
    S = enc([s["text"] for s in secs], "Document") if secs else np.zeros((0, I.shape[1]))
    by = defaultdict(list)
    for j, s in enumerate(secs):
        by[s["page"]].append((s["sec"], j))
    out = []
    for i, x in enumerate(rows):
        y = {**x, "alt_cos": round(float(I[i] @ A[i]), 4)}
        c = {k: float(I[i] @ S[j]) for k, j in by[x["page"]]}
        if x["sec"] in c:
            oth = [v for k, v in c.items() if k != x["sec"]]
            y["sec_cos"] = round(c[x["sec"]], 4)
            y["sec_margin"] = round(c[x["sec"]] - max(oth), 4) if oth else None
        out.append(y)
    write(a.out, out)
    print(f"{len(out)} ảnh -> {a.out}")


def padded(path, cache):
    from PIL import Image
    im = Image.open(path)
    if min(im.size) >= 320:
        return str(path)
    q = Path(cache) / (Path(path).stem + "_pad.png")
    if not q.exists():
        im = im.convert("RGB")
        w, h = max(im.width, 320), max(im.height, 320)
        c = Image.new("RGB", (w, h), "white")
        c.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
        c.save(q)
    return str(q.resolve())


def cmd_jev_in(a):
    out = []
    if a.media:
        for x in jl(a.media):
            out.append({"id": x["id"], "state": {
                "image": {"image_path": padded(x["img"], Path(x["img"]).parent)}, "alt": x["alt"],
                "section": {"heading": " > ".join(t for t in (x["h2"], x["h3"]) if t),
                            "text": (x["section_text"] or x["prev"])[:800]},
                "caption": x.get("caption", "")}})
    else:
        shots = {s["url"]: s["shot"] for s in jl(a.shots) if s.get("shot")}
        for p in jl(a.pools):
            for u in p["urls"]:
                if u["url"] in shots:
                    out.append({"id": f"{p['id']}|{u['url']}", "state": {
                        "query": p["text"], "screenshot": {"image_path": padded(shots[u["url"]], Path(shots[u["url"]]).parent)}}})
    write(a.out, out)
    print(f"{len(out)} dòng -> {a.out}")


def cmd_pairs(a):
    med = {x["id"]: x for x in jl(a.media)}
    ja = answers(a.jev_out)
    out = [{"id": g["id"], "cos": round(ja[g["id"]]["alt_matches"]["p_yes"] + ALT_W * med[g["id"]]["alt_cos"], 4),
            "label": int(g["label"] == "yes")}
           for g in jl(a.gold) if g.get("label") in ("yes", "no") and g["id"] in med and g["id"] in ja]
    write(a.out, out)
    print(f"{len(out)} cặp -> {a.out}")


def find_defaults():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            for rel in ("tools/ai-assist", "SEO Production/tools/ai-assist"):
                f = d / rel / "calibration-defaults.json"
                if f.is_file():
                    return f
    return None


def entries(registry, site):
    """Entry của site trước, rồi tới defaults."""
    for path, want in ((registry, site), (find_defaults(), None)):
        if path and Path(path).exists():
            for e in json.loads(Path(path).read_text(encoding="utf-8")).get("entries", []):
                if want is None or e.get("site") == want:
                    yield e, ("site" if want else "defaults")


def jev_gate(registry, site, rubric, version, question, field="conf_gate"):
    """field="conf_gate": nhận cả yes lẫn no khi max(p, 1-p) ≥ cổng. field="threshold": chỉ nhận yes khi p ≥ ngưỡng."""
    for e, src in entries(registry, site):
        if e.get("rubric") == rubric and e.get("version") == version and e.get("mode") == "jev" \
                and e.get("question") == question and e.get("positive") in (None, "yes"):
            g = e.get(field) or e.get("conf_gate") or e.get("threshold")
            if g:
                return g, src
    return None, None


def answers(path):
    return {r["id"]: r["answers"] for r in jl(path) if "answers" in r}


def cmd_media(a):
    allimg = jl(a.images)
    med = {x["id"]: x for x in jl(a.media)}
    ja = answers(a.jev_out)
    ver = task_version("image-fit")
    alt_rej, alt_src = None, None
    for e, src in entries(a.registry, a.site):
        if e.get("rubric") == "alt-score" and e.get("version") == f"{ver}+w{ALT_W}" and e.get("reject_below") is not None:
            alt_rej, alt_src = e["reject_below"], src
            break
    fit_g, fit_src = jev_gate(a.registry, a.site, "image-fit", ver, "fits_section", "threshold")
    if alt_rej is None or fit_g is None:
        sys.exit(f"thiếu cổng alt-score hoặc image-fit {ver}: hiệu chuẩn bằng model-calibration trước")
    dec = []
    for x in allimg:
        d = {k: x[k] for k in ("id", "page", "src", "alt", "h2", "h3", "flags")}
        f, y, an = set(x["flags"]), med.get(x["id"]), ja.get(x["id"])
        if "missing_alt" in f:
            d["alt_status"] = "thiếu alt"
        elif "fileish_alt" in f:
            d["alt_status"] = "alt dạng tên file"
        elif y and an:
            d["alt_score"] = round(an["alt_matches"]["p_yes"] + ALT_W * y["alt_cos"], 3)
            d["alt_status"] = "alt lệch ảnh" if d["alt_score"] < alt_rej else "chưa kết luận"
        else:
            d["alt_status"] = "chưa đo"
        if y and an:
            d["fit_p"] = an["fits_section"]["p_yes"]
            d["fit_status"] = "khớp mục" if d["fit_p"] >= fit_g else "review"
        else:
            d["fit_status"] = "chưa đo"
        dec.append(d)
    out = Path(a.out_dir)
    write(out / "media_decisions.jsonl", dec)
    ca, cf = Counter(d["alt_status"] for d in dec), Counter(d["fit_status"] for d in dec if d["fit_status"] != "chưa đo")
    n_med = sum(1 for d in dec if d["fit_status"] != "chưa đo")
    P = lambda u: urlparse(u).path or "/"
    L = ["# Ảnh trong bài: alt và độ khớp mục", "",
         f"{len(dec)} ảnh trong main content của {len({d['page'] for d in dec})} trang. Model đo {n_med} ảnh đã tải.",
         f"Cổng: alt lệch khi p alt_matches + {ALT_W} × cos ảnh–alt < {alt_rej} ({alt_src}); khớp mục khi Jev ≥ {fit_g} ({fit_src}).", ""]
    if "defaults" in (alt_src, fit_src):
        L += ["Có cổng lấy từ defaults (đo trên site khác): kết quả là bản nháp tới khi hiệu chuẩn trên 40+ ảnh của site này.", ""]
    L += ["| Alt | Ảnh |", "|---|---|"] + [f"| {k} | {v} |" for k, v in ca.most_common()] + [""]
    L += ["| Ảnh so với mục chứa nó (ảnh đã đo) | Ảnh |", "|---|---|"] + [f"| {k} | {v} |" for k, v in cf.most_common()] + [""]
    reuse = defaultdict(set)
    for x in allimg:
        if "alt_reused" in x["flags"]:
            reuse[x["alt"]].add(x["src"])
    if reuse:
        L += ["## Một alt cho nhiều ảnh khác nhau", "", "| Alt | Số ảnh khác nhau |", "|---|---|"]
        L += [f"| {k[:60]} | {len(v)} |" for k, v in sorted(reuse.items(), key=lambda kv: -len(kv[1]))[:15]] + [""]
    bad = sorted([d for d in dec if d["alt_status"] == "alt lệch ảnh"], key=lambda d: d["alt_score"])
    if bad:
        L += ["## Alt lệch ảnh (điểm thấp trước)", "", "| Trang | Alt | Mục | Điểm |", "|---|---|---|---|"]
        L += [f"| {P(d['page'])} | {d['alt'][:60]} | {(d['h3'] or d['h2'])[:50]} | {d['alt_score']} |" for d in bad[:a.top]] + [""]
    rv = sorted([d for d in dec if d["fit_status"] == "review"], key=lambda d: d["fit_p"])
    if rv:
        L += ["## Ảnh có thể không khớp mục (Claude xem ảnh trước khi đề xuất)", "", "| Trang | Alt | Mục | Jev |", "|---|---|---|---|"]
        L += [f"| {P(d['page'])} | {d['alt'][:50]} | {(d['h3'] or d['h2'])[:50]} | {round(d['fit_p'], 2)} |" for d in rv[:a.top]] + [""]
    files = Counter(P(d["page"]) for d in dec if d["alt_status"] in ("thiếu alt", "alt dạng tên file"))
    if files:
        L += ["## Trang nhiều ảnh thiếu alt hoặc alt dạng tên file", "", "| Trang | Ảnh |", "|---|---|"]
        L += [f"| {k} | {v} |" for k, v in files.most_common(20)] + [""]
    (out / "media_report.md").write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"alt": dict(ca), "fit": dict(cf)}, ensure_ascii=False))


def cmd_layout(a):
    ja = answers(a.jev_out)
    ver = task_version("first-screen")
    gates = {q: jev_gate(a.registry, a.site, "first-screen", ver, q) for q in FEATURES}
    rows, own = [], []
    for p in jl(a.pools):
        for u in p["urls"]:
            an = ja.get(f"{p['id']}|{u['url']}")
            if not an:
                continue
            r = {"pool": p["id"], "query": p["text"], "url": u["url"], "cited": int(u.get("label", 0) > 0)}
            for q in FEATURES:
                r[q] = an[q]["p_yes"]
            for b in ("centerpiece", "primary_cta"):
                r[f"{b}_top"] = round(an[b]["box"]["top"], 3) if an.get(b, {}).get("box") else None
            rows.append(r)
            if a.own_domain and a.own_domain in urlparse(u["url"]).netloc:
                own.append(r)
    out = Path(a.out_dir)
    write(out / "auc_rows.jsonl", rows)

    def lab(r, q):
        g = gates[q][0]
        if g is None:
            return None
        return True if r[q] >= g else (False if r[q] <= 1 - g else None)

    L = ["# Màn đầu của trang: trang được AI trích so với không được trích", "",
         f"{len(rows)} cặp pool × URL, {len({r['pool'] for r in rows})} pool. Rubric `first-screen` {ver}.", "",
         "| Đặc điểm | Cổng | Có, trang được trích | Có, trang không được trích | Có, trang của mình |", "|---|---|---|---|---|"]
    for q in FEATURES:
        g, src = gates[q]
        if g is None:
            L.append(f"| {q} | chưa hiệu chuẩn | | | |")
            continue
        cells = []
        for grp in ([r for r in rows if r["cited"]], [r for r in rows if not r["cited"]], own):
            ls = [lab(r, q) for r in grp]
            known = [v for v in ls if v is not None]
            cells.append(f"{sum(known)}/{len(known)}" if known else "")
        L.append(f"| {q} | {g} ({src}) | " + " | ".join(cells) + " |")
    L += ["", "Đọc theo pool: so trang của mình với trang được trích cùng pool, không so với chuẩn chung.",
          "Chỉ số mô phỏng, trọng số thật của Google chưa công bố. Kiểm AUC trong từng pool bằng `calibrate.py auc` trên auc_rows.jsonl.", ""]
    (out / "layout_report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"{len(rows)} dòng -> {out}/auc_rows.jsonl, layout_report.md")


def cmd_shoot(a):
    urls = [l.strip() for l in Path(a.urls).read_text(encoding="utf-8").splitlines() if l.strip()]
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    prof = out / ".chrome-profile"
    log = []
    for u in urls:
        dst = out / f"{key(u)}.png"
        if not dst.exists():
            try:
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                                f"--window-size={a.width},{a.height}", "--virtual-time-budget=8000",
                                f"--user-data-dir={prof.resolve()}", f"--screenshot={dst.resolve()}", u],
                               capture_output=True, timeout=45)
            except subprocess.TimeoutExpired:
                pass
        log.append({"url": u, "shot": str(dst.resolve()) if dst.exists() else None})
    write(out / "shots.jsonl", log)
    print(f"{sum(1 for x in log if x['shot'])}/{len(log)} ảnh chụp -> {out}/shots.jsonl")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("images")
    i.add_argument("--html-dir", required=True)
    i.add_argument("--out", required=True)
    i.add_argument("--min-width", type=int, default=80)
    f = sub.add_parser("fetch")
    f.add_argument("--images", required=True)
    f.add_argument("--cache", required=True)
    f.add_argument("--out", required=True)
    f.add_argument("--per-page", type=int, default=2)
    f.add_argument("--all", action="store_true")
    f.add_argument("--seed", type=int, default=19)
    f.add_argument("--delay", type=float, default=0.15)
    e = sub.add_parser("embed")
    e.add_argument("--sample", required=True)
    e.add_argument("--sections", required=True)
    e.add_argument("--out", required=True)
    j = sub.add_parser("jev-in")
    j.add_argument("--media", default=None)
    j.add_argument("--shots", default=None)
    j.add_argument("--pools", default=None)
    j.add_argument("--out", required=True)
    pp = sub.add_parser("pairs")
    pp.add_argument("--media", required=True)
    pp.add_argument("--jev-out", required=True)
    pp.add_argument("--gold", required=True)
    pp.add_argument("--out", required=True)
    m = sub.add_parser("media")
    m.add_argument("--images", required=True)
    m.add_argument("--media", required=True)
    m.add_argument("--jev-out", required=True)
    m.add_argument("--registry", default=None)
    m.add_argument("--site", required=True)
    m.add_argument("--out-dir", required=True)
    m.add_argument("--top", type=int, default=40)
    y = sub.add_parser("layout")
    y.add_argument("--jev-out", required=True)
    y.add_argument("--pools", required=True)
    y.add_argument("--registry", default=None)
    y.add_argument("--site", required=True)
    y.add_argument("--own-domain", default=None)
    y.add_argument("--out-dir", required=True)
    s = sub.add_parser("shoot")
    s.add_argument("--urls", required=True)
    s.add_argument("--out-dir", required=True)
    s.add_argument("--width", type=int, default=1366)
    s.add_argument("--height", type=int, default=900)
    a = ap.parse_args()
    if a.cmd == "jev-in" and not (a.media or (a.shots and a.pools)):
        sys.exit("jev-in cần --media, hoặc --shots và --pools")
    {"images": cmd_images, "fetch": cmd_fetch, "embed": cmd_embed, "jev-in": cmd_jev_in, "pairs": cmd_pairs, "media": cmd_media,
     "layout": cmd_layout, "shoot": cmd_shoot}[a.cmd](a)


if __name__ == "__main__":
    main()
