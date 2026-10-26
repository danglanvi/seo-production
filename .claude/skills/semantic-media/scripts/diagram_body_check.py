#!/usr/bin/env python3
"""Kiểm chữ của sơ đồ với thân bài trước khi chèn. Offline, không gọi model.

  python3 diagram_body_check.py --specs specs.json --body bai.html [--id AI19 ...] [--out report.json --write] [--claims claims.jsonl]
  python3 diagram_body_check.py --specs specs.json --body-map map.json
      specs.json: cùng file với diagram_render.mjs ({"items":[{"id","json_prompt":{...}}]}).
      --body: một file thân bài (.html, .md, .txt) dùng cho mọi sơ đồ chọn. --body-map: {"<id sơ đồ>": "<file thân bài>"}.

Mỗi chuỗi chữ trên sơ đồ được xếp vào một mức:
  khop        chuỗi nằm nguyên văn trong thân bài và không có câu liên quan nói ngược chiều
  mot_phan    từ khoá của chuỗi có trong thân bài nhưng không nguyên văn (nhãn rút gọn): Claude đọc
  khong_thay  từ khoá không có trong thân bài: lỗi
  nguoc       chuỗi khẳng định, nhưng mọi câu thân bài nói về cùng từ khoá đều phủ định (hoặc ngược lại): lỗi
  can_doc     các câu thân bài về từ khoá có cả khẳng định lẫn phủ định: Claude hoặc Jev claim-faithful đọc
Số trên sơ đồ không có trong thân bài cũng là lỗi (so_khong_thay).
Mã thoát: 0 không có lỗi, 1 có lỗi (--strict tính cả can_doc và mot_phan), 2 sai tham số hoặc thiếu file.
Mặc định chỉ in kết quả. Chỉ ghi --out và --claims khi có --write (không có thì in "dry-run").
--claims ghi mỗi chuỗi cần đọc một dòng {"id","claim","evidence":[tối đa 3 câu thân bài]} làm input cho Jev claim-faithful.
"""
import argparse
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

STOP = {"có", "là", "của", "và", "các", "những", "một", "cho", "được", "với", "trong", "để", "khi", "thì", "mà", "này", "đó", "the", "a", "an", "of", "and", "to", "in", "is", "are", "bị", "cũng", "đã", "sẽ", "đang", "rất", "như", "hay", "hoặc", "từ", "ở", "về", "theo"}
# Cụm chứa "không" nhưng không phải phủ định.
NOT_NEG = ["không chỉ", "không gian", "không ngừng", "không thể thiếu", "không những"]
NEG_RE = re.compile(r"\b(không|chưa|chẳng|not|no|without|never)\b", re.I)
BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br", "section", "article", "blockquote", "figcaption", "td", "th"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def squash(s):
    return re.sub(r"\s+", " ", nfc(s)).strip()


def body_text(path):
    raw = Path(path).read_text(encoding="utf-8")
    if Path(path).suffix.lower() in (".html", ".htm"):
        p = _Text()
        p.feed(raw)
        raw = "".join(p.parts)
    return raw


def sentences(text):
    out = []
    for block in nfc(text).split("\n"):
        for s in re.split(r"(?<=[.!?;])\s+|\s[•·]\s", block):
            s = squash(s)
            if len(s) >= 3:
                out.append(s)
    return out


def tokens(s):
    return [t for t in re.findall(r"[\w][\w\-]*", nfc(s).lower()) if t not in STOP and not NEG_RE.fullmatch(t)]


def numbers(s):
    return set(re.findall(r"\d+(?:[.,]\d+)*", nfc(s)))


def is_negated(s):
    low = nfc(s).lower()
    for p in NOT_NEG:
        low = low.replace(p, " ")
    return bool(NEG_RE.search(low))


def expected(spec):
    """Cùng luật với expected() của diagram_render.mjs."""
    jp = spec.get("json_prompt") or {}
    t = lambda v: v if isinstance(v, str) else (v or {}).get("text") if isinstance(v, dict) else None
    out = []
    for k in ("headline", "subheadline"):
        if t(jp.get(k)):
            out.append(t(jp[k]))
    for e in jp.get("elements") or []:
        for k in ("label", "text", "question", "header"):
            if isinstance(e.get(k), str):
                out.extend(e[k].split(" · "))
        for k in ("items", "chips", "terms", "steps"):
            if isinstance(e.get(k), list):
                out.extend(x for x in e[k] if isinstance(x, str))
    seen, res = set(), []
    for s in out:
        s = squash(s)
        if s and s not in seen:
            seen.add(s)
            res.append(s)
    return res


def judge(label, sents, flat):
    """Trả (mức, ghi chú, danh sách câu bằng chứng).
    Chuỗi nằm nguyên văn trong thân bài vẫn qua bước so chiều khẳng định/phủ định: ca AI19 (site gtvseo, 19/10),
    'có schema' nằm nguyên văn trong câu kể tin đồn, còn câu kết luận phủ định."""
    low = squash(label).lower()
    verbatim = low in flat
    toks = tokens(label)
    if not toks:
        return ("khop", "", []) if verbatim else ("mot_phan", "chuỗi chỉ có từ phổ thông, cần đọc", [])
    body_toks = set(tokens(flat))
    miss = [t for t in toks if t not in body_toks]
    if not verbatim and (len(miss) == len(toks) or len(miss) / len(toks) > 0.4):
        return "khong_thay", "từ khoá không có trong thân bài: " + ", ".join(miss), []
    # Câu thân bài chứa mọi từ khoá còn thấy được.
    need = [t for t in toks if t in body_toks]
    rel = [s for s in sents if all(t in set(tokens(s)) for t in need)]
    if not rel:
        if verbatim:
            return "khop", "", []
        rel = sorted(sents, key=lambda s: -sum(t in set(tokens(s)) for t in need))[:3]
        return "mot_phan", "từ khoá nằm rải ở nhiều câu", rel[:3]
    neg_label = is_negated(label)
    flags = [is_negated(s) != neg_label for s in rel]
    # Bằng chứng: câu ngược chiều trước, rồi câu chứa nguyên văn chuỗi.
    ev = [rel[i] for i in sorted(range(len(rel)), key=lambda i: (not flags[i], low not in rel[i].lower()))][:3]
    if all(flags) and not miss:  # nhãn thiếu từ khoá thì không đủ chắc để kết luận ngược
        return "nguoc", "chuỗi " + ("phủ định" if neg_label else "khẳng định") + " nhưng mọi câu liên quan nói ngược lại", ev
    if any(flags):
        return "can_doc", "thân bài có cả câu cùng và câu ngược hướng", ev
    return ("khop", "", []) if verbatim else ("mot_phan", "nhãn rút gọn, cùng hướng với thân bài", ev)


def check(spec, path):
    sents = sentences(body_text(path))
    flat = squash(" ".join(sents)).lower()
    body_nums = numbers(flat)
    rows, claims, errors = [], [], []
    for label in expected(spec):
        level, note, ev = judge(label, sents, flat)
        rows.append({"text": label, "level": level, "note": note})
        if level in ("nguoc", "can_doc", "mot_phan") and ev:
            claims.append({"id": spec["id"], "claim": label, "evidence": ev[:3]})
        bad_nums = sorted(n for n in numbers(label) if n not in body_nums)
        if bad_nums:
            rows[-1]["so_khong_thay"] = bad_nums
            errors.append(f"{spec['id']}: số {', '.join(bad_nums)} không có trong thân bài ('{label}')")
        if level in ("khong_thay", "nguoc"):
            errors.append(f"{spec['id']}: {level} '{label}': {note}")
    return {"id": spec["id"], "body": str(path), "rows": rows, "errors": errors}, claims


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kiểm chữ sơ đồ với thân bài (offline).", epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specs", required=True)
    ap.add_argument("--body")
    ap.add_argument("--body-map")
    ap.add_argument("--id", nargs="*", help="chỉ kiểm các sơ đồ này")
    ap.add_argument("--out", help="ghi báo cáo JSON, cần --write")
    ap.add_argument("--claims", help="ghi input cho Jev claim-faithful, cần --write")
    ap.add_argument("--write", action="store_true", help="cho phép ghi --out và --claims")
    ap.add_argument("--strict", action="store_true", help="tính can_doc và mot_phan là lỗi")
    a = ap.parse_args(argv)
    if bool(a.body) == bool(a.body_map):
        print("Chọn đúng một trong --body hoặc --body-map", file=sys.stderr)
        return 2
    try:
        items = json.loads(Path(a.specs).read_text(encoding="utf-8"))["items"]
        bmap = json.loads(Path(a.body_map).read_text(encoding="utf-8")) if a.body_map else {}
    except (OSError, ValueError, KeyError) as e:
        print(f"Không đọc được specs hoặc body-map: {e}", file=sys.stderr)
        return 2
    reports, claims, errors = [], [], []
    for spec in items:
        if a.id and spec["id"] not in a.id:
            continue
        path = a.body or bmap.get(spec["id"])
        if not path or not Path(path).is_file():
            print(f"{spec['id']}: không có file thân bài ({path})", file=sys.stderr)
            return 2
        r, c = check(spec, path)
        reports.append(r)
        claims += c
        errors += r["errors"]
        if a.strict:
            errors += [f"{spec['id']}: {x['level']} '{x['text']}'" for x in r["rows"] if x["level"] in ("can_doc", "mot_phan")]
        n = {}
        for x in r["rows"]:
            n[x["level"]] = n.get(x["level"], 0) + 1
        print(f"{spec['id']} {json.dumps(n, ensure_ascii=False)}")
        for x in r["rows"]:
            if x["level"] != "khop":
                print(f"   - {x['level']}: {x['text']} {('(' + x['note'] + ')') if x['note'] else ''}")
    if not reports:
        print("Không có sơ đồ nào để kiểm", file=sys.stderr)
        return 2
    for label, target, payload in (("--out", a.out, json.dumps({"reports": reports}, ensure_ascii=False, indent=1)),
                                   ("--claims", a.claims, "\n".join(json.dumps(c, ensure_ascii=False) for c in claims))):
        if target:
            if a.write:
                Path(target).write_text(payload + "\n", encoding="utf-8")
                print(f"đã ghi {target}")
            else:
                print(f"dry-run: sẽ ghi {target} khi có --write")
    for e in errors:
        print("LỖI", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
