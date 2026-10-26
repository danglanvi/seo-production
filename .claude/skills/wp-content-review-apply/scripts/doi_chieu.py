#!/usr/bin/env python3
"""Đối chiếu thẻ đã duyệt trên trang duyệt với trang live (chỉ đọc, không ghi lên site).

python3 -I doi_chieu.py <thư mục bản sao db> --out <thư mục kết quả> --site https://<host> [--cache pages.json] [--khoa khoa.txt]

Bản sao db: thư mục có report/*.json (mỗi file một tài liệu phần) và reviews/*.json (mỗi file một thẻ đã duyệt).
Giá trị cuối của một trường: values (chữ người duyệt sửa) > phương án đã chọn (A, B hoặc options) > proposed.
Mỗi trường có chữ thật nhận một nhãn:
  da-len    chữ mới có trên trang (khớp ít nhất 85% cụm 6 chữ) và chữ cũ không còn.
  chua-len  chữ cũ còn và chữ mới chưa có.
  mot-phan  các trường hợp còn lại.
  doc-tay   trường là hướng dẫn hoặc luật, không so chữ được.
Thẻ bị bỏ (rejected) và thẻ đang có khoá lane (--khoa) nhận nhãn bo-qua và không tải trang.
Ra ket-qua.json và ket-qua.md trong --out. Có hàng "ghi ngay": thẻ approved hoặc edited mà chưa lên site.
Tải trang bằng URL sạch (bỏ query và fragment), 2 luồng, 1 request mỗi giây cho cả hai luồng, chỉ tới host của --site.
--cache: file JSON lưu trang đã tải. File có sẵn thì chỉ đọc file, không tải lại. Chưa có thì tải rồi ghi file.
Thoát mã 2 khi sai đầu vào hoặc file đầu ra đã có (thêm --force để ghi đè kết quả cũ).
"""
import argparse
import collections
import concurrent.futures as cf
import datetime
import html
import json
import pathlib
import re
import sys
import threading
import time
import unicodedata
import urllib.parse
import urllib.request

DEFAULT_TARGET_KEYS = {"seo_title", "meta", "meta_desc", "description", "h1"}
INSTR_KEYS = {"action", "luat", "plan", "members", "quyet_dinh", "hien_trang", "can_cu", "kiem_ke", "vi_tri", "order", "form", "robots",
              "label_hide", "required", "menu", "pages", "schema", "tkw", "ent", "url", "lo", "pham_vi", "cach_lam", "ghi_chu"}


def base_key(k):
    return str(k or "").split("#")[0]


def norm(s, year):
    s = html.unescape(str(s or ""))
    s = unicodedata.normalize("NFC", s).lower()
    s = s.replace("%currentyear%", str(year)).replace(" ", " ")
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[“”\"'‘’«»–—\-•*#|:;,.!?()\[\]/]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def shingles(s, n=6):
    w = s.split()
    return {" ".join(w[i:i + n]) for i in range(max(1, len(w) - n + 1))} if w else set()


def is_instr(key, val, year):
    v = str(val or "").strip()
    return base_key(key) in INSTR_KEYS or v.startswith("(") or v.startswith("Mỗi ") or len(norm(v, year).split()) < 3


def clean_url(u):
    p = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", "", ""))


def fid_keys(fields):
    """Khoá lưu của từng trường: trường đầu giữ key, trường trùng thành key#n (khớp fid của trang duyệt)."""
    seen, out = {}, []
    for f in fields:
        k = f.get("key")
        seen[k] = seen.get(k, 0) + 1
        out.append(k if seen[k] == 1 else "%s#%d" % (k, seen[k]))
    return out


def load_export(src):
    src = pathlib.Path(src)
    reviews = {}
    for f in sorted((src / "reviews").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)
        reviews[d.get("item_id") or f.stem] = d
    cards = []
    for f in sorted((src / "report").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)
        for it in d.get("items") or []:
            cards.append((f.stem, it, d))
    return cards, reviews


def final_fields(it, sec_doc, rv):
    """Danh sách {key, before, final} theo thứ tự ưu tiên values > phương án > proposed."""
    opt = rv.get("option") or it.get("default_option")
    optvals = {}
    for o in (it.get("options") or sec_doc.get("options") or []):
        if o.get("id") == opt or o.get("key") == opt:
            optvals = o.get("values") or {}
    vals = rv.get("values") or {}
    out = []
    fields = it.get("fields") or []
    for fl, k in zip(fields, fid_keys(fields)):
        if k in vals:
            v = vals[k]
        elif opt and opt in fl and "proposed" not in fl:
            v = fl[opt]
        elif k in optvals:
            v = optvals[k]
        elif "proposed" in fl:
            v = fl["proposed"]
        else:
            v = fl.get("A")
        out.append({"key": k, "before": fl.get("before"), "final": v})
    for k, v in optvals.items():
        if k not in {x["key"] for x in out}:
            out.append({"key": k, "before": None, "final": v})
    return out


class Limiter(object):
    """Giãn cách tối thiểu giữa hai request, dùng chung cho mọi luồng."""

    def __init__(self, rps):
        self.gap = 1.0 / rps if rps > 0 else 0
        self.lock = threading.Lock()
        self.next = 0.0

    def wait(self):
        with self.lock:
            now = time.monotonic()
            t = max(now, self.next)
            self.next = t + self.gap
        if t > now:
            time.sleep(t - now)


def parse_page(h, code, year):
    t = re.search(r"<title[^>]*>(.*?)</title>", h, re.S)
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', h)
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    ld = " ".join(re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S))
    body = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", h, flags=re.S)
    return {"code": code, "title": norm(t.group(1) if t else "", year), "meta": norm(m.group(1) if m else "", year), "h1": norm(" ".join(h1), year),
            "text": norm(body, year) + " " + norm(ld, year), "hrefs": " ".join(re.findall(r'href="([^"]+)"', h))}


def fetch_all(urls, year, rps, workers):
    lim = Limiter(rps)

    def one(u):
        lim.wait()
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 wp-doi-chieu"}), timeout=40)
            return u, parse_page(r.read().decode("utf-8", "ignore"), r.status, year)
        except Exception as e:  # noqa: BLE001
            return u, {"code": getattr(e, "code", 0), "title": "", "meta": "", "h1": "", "text": "", "hrefs": ""}

    with cf.ThreadPoolExecutor(workers) as ex:
        return dict(ex.map(one, urls))


def contains(hay, s):
    w = s.split()
    if len(w) < 6:
        return 1.0 if s and s in hay else 0.0
    sv = shingles(s)
    return sum(1 for x in sv if x in hay) / len(sv)


def label_field(key, before, final, page, year):
    b = base_key(key)
    if page is None or is_instr(key, final, year):
        return {"ket_qua": "doc-tay" if page else "khong-co-url"}
    hay = page["title"] if b == "seo_title" else page["meta"] if b in ("meta", "meta_desc", "description") else page["h1"] if b == "h1" else page["text"]
    nv, nb = norm(final, year), norm(before, year)
    if b == "text" and str(final).startswith("[") and "](" in str(final):
        href = re.findall(r"\]\(([^)]+)\)", str(final))
        return {"ket_qua": "da-len" if href and all(h in page["hrefs"] for h in href) else "chua-len"}
    hit = contains(hay, nv)
    uo = shingles(nb) - shingles(nv) if len(nb.split()) >= 6 else set()
    old = (sum(1 for s in uo if s in hay) / len(uo) > 0.6) if uo else (bool(nb) and len(nb.split()) >= 3 and nb not in nv and nb in hay)
    res = {"khop": round(hit, 2), "cu_con": old}
    if b in DEFAULT_TARGET_KEYS:
        res["live"] = hay[:220]
    res["ket_qua"] = "da-len" if hit >= 0.85 and not old else "chua-len" if old and hit < 0.5 else "mot-phan"
    return res


def load_locks(path):
    """File khoá: mỗi dòng một mã thẻ, hoặc tiền tố kết thúc bằng dấu *. Dòng trống và dòng bắt đầu # bị bỏ."""
    exact, prefix = set(), []
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        (prefix.append(ln[:-1]) if ln.endswith("*") else exact.add(ln))
    return lambda i: i in exact or any(i.startswith(p) for p in prefix)


def build(cards, reviews, locked, pages, year):
    out = []
    for section, it, sec_doc in cards:
        rv = reviews.get(it["id"], {})
        st = rv.get("status", "chua-duyet")
        c = {"section": section, "id": it["id"], "label": it.get("label"), "url": it.get("url"), "status": st,
             "option": rv.get("option") or it.get("default_option"), "note": rv.get("note"), "fields": final_fields(it, sec_doc, rv)}
        skip = "rejected" if st == "rejected" else "khoa-lane" if locked(it["id"]) else None
        page = pages.get(clean_url(c["url"])) if c["url"] and str(c["url"]).startswith("http") else None
        for fl in c["fields"]:
            if skip:
                fl["ket_qua"] = "bo-qua"
            else:
                fl.update(label_field(fl["key"], fl["before"], fl["final"], page, year))
        rs = [fl["ket_qua"] for fl in c["fields"]] or ["doc-tay"]
        c["ket_qua"] = ("bo-qua" if skip else "da-len" if all(r == "da-len" for r in rs) else
                        "khong-co-url" if all(r == "khong-co-url" for r in rs) else
                        "chua-len" if all(r in ("chua-len", "khong-co-url") for r in rs) else "doc-tay" if all(r == "doc-tay" for r in rs) else "mot-phan")
        if skip:
            c["bo_qua_vi"] = skip
        c["http"] = page["code"] if page else None
        out.append(c)
    return out


def report_md(cards):
    tab = collections.defaultdict(collections.Counter)
    for c in cards:
        tab[c["section"]][c["ket_qua"]] += 1
    L = ["| Mục | đã lên | một phần | chưa lên | đọc tay | bỏ qua | không có trang |", "|---|---|---|---|---|---|---|"]
    for s, v in sorted(tab.items()):
        L.append("| %s | %d | %d | %d | %d | %d | %d |" % (s, v["da-len"], v["mot-phan"], v["chua-len"], v["doc-tay"], v["bo-qua"], v["khong-co-url"]))
    todo = [c for c in cards if c["status"] in ("approved", "edited") and c["ket_qua"] in ("chua-len", "mot-phan")]
    L += ["", "## Hàng ghi ngay (đã duyệt hoặc đã sửa, chưa lên site đủ)", ""]
    if not todo:
        L.append("Không có thẻ nào.")
    for c in todo:
        L.append("- `%s` (%s, %s): %s" % (c["id"], c["section"], c["status"], c["ket_qua"]))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Đối chiếu thẻ đã duyệt với trang live (chỉ đọc). Xem docstring đầu file.")
    ap.add_argument("export", help="thư mục bản sao db (có report/ và reviews/)")
    ap.add_argument("--out", required=True, help="thư mục ghi ket-qua.json và ket-qua.md")
    ap.add_argument("--site", help="https://host: chỉ tải URL của host này")
    ap.add_argument("--cache", help="file JSON lưu trang đã tải; có sẵn thì không tải lại")
    ap.add_argument("--khoa", help="file mã thẻ đang có khoá lane (mỗi dòng một mã hoặc tiền tố*)")
    ap.add_argument("--year", type=int, default=datetime.date.today().year, help="năm thay cho %%currentyear%%")
    ap.add_argument("--rps", type=float, default=1.0, help="số request mỗi giây (mặc định 1)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--force", action="store_true", help="ghi đè ket-qua.* đã có")
    a = ap.parse_args(argv)

    src = pathlib.Path(a.export)
    if not (src / "report").is_dir():
        print("Thiếu report/ trong " + a.export, file=sys.stderr)
        return 2  # reviews/ có thể chưa có khi chưa ai duyệt: coi là rỗng
    out = pathlib.Path(a.out)
    if not a.force and ((out / "ket-qua.json").exists() or (out / "ket-qua.md").exists()):
        print("ket-qua.* đã có trong %s, thêm --force để ghi đè" % a.out, file=sys.stderr)
        return 2
    cards, reviews = load_export(src)
    locked = load_locks(a.khoa) if a.khoa else (lambda i: False)

    cache = pathlib.Path(a.cache) if a.cache else None
    if cache and cache.exists():
        pages = json.loads(cache.read_text(encoding="utf-8"))
    else:
        if not a.site:
            print("Cần --site hoặc --cache có sẵn", file=sys.stderr)
            return 2
        host = urllib.parse.urlsplit(a.site)
        if host.scheme not in ("http", "https") or not host.netloc:
            print("--site phải là http(s)://host", file=sys.stderr)
            return 2
        want = set()
        for section, it, sec_doc in cards:
            rv = reviews.get(it["id"], {})
            u = it.get("url")
            if rv.get("status") == "rejected" or locked(it["id"]) or not u or not str(u).startswith("http"):
                continue
            cu = clean_url(u)
            if urllib.parse.urlsplit(cu).netloc == host.netloc:
                want.add(cu)
        pages = fetch_all(sorted(want), a.year, a.rps, a.workers)
        if cache:
            cache.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")

    result = build(cards, reviews, locked, pages, a.year)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ket-qua.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    md = report_md(result)
    (out / "ket-qua.md").write_text(md, encoding="utf-8")
    print(md)
    print("URL %d, lỗi %d" % (len(pages), sum(1 for p in pages.values() if p.get("code") != 200)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
