#!/usr/bin/env python3
"""Ghép slot media với video sở hữu bằng EmbeddingGemma 2, rồi kiểm luật của media plan.

  ~/.venvs/embeddinggemma/bin/python media_match.py nn --slots slots_q.jsonl --videos videos_d.jsonl --out slot_video_nn.jsonl [--k 8]
      slots_q.jsonl, videos_d.jsonl: mỗi dòng {"id", "text"}. Slot dùng prompt SearchQuery, video dùng Document (dùng lại encoder của site-vector-index).
  python3 media_match.py check --plan media_plan.json [--nn slot_video_nn.jsonl] [--max-pages 2] [--used images.jsonl]
      plan: {"site_entity", "slots": [{"slot_id","page","decision","purpose","media":{"video_id","src"},"alt","caption","gap_media_type",
             "speaker_entity","speaker_evidence","allow_reuse"}]}. Báo vi phạm luật, exit 1 khi có.
      Lời chứng thực (purpose "testimonial"): cần speaker_entity và speaker_evidence; speaker_entity phải trùng page_entity hoặc site_entity.
      --used: ảnh đang hiển thị ở các trang, file .jsonl của visual-serp-lab `visual.py images` ({"page","src"}) hoặc .txt mỗi dòng một src.
      Ảnh trong plan trùng ảnh của trang khác, hoặc lặp ở nhiều trang của plan, là lỗi. So theo đường dẫn, bỏ host, query, hậu tố -WxH và -scaled.
      Ảnh gần giống (crop, nén lại) script không bắt. Ngoại lệ ghi allow_reuse: true.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
SVI = HERE.parents[1] / "site-vector-index" / "scripts"
FAKE_KINDS = {"people", "office", "team", "customer", "testimonial_avatar", "event"}  # không dùng ảnh AI cho lớp này
IMAGE_KINDS = {"real_photo", "photo", "screenshot", "image", "diagram", "ai_image"}


def read_jsonl(p):
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def img_key(src):
    p = urlparse(str(src).strip()).path or str(src).strip()
    return re.sub(r"-(\d+x\d+|scaled)(?=\.[A-Za-z0-9]+$)", "", p).lower()


def page_key(p):
    return ((urlparse(str(p)).path or str(p)).rstrip("/") or "/") if p else None


def read_used(path):
    used = defaultdict(set)
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        r = json.loads(line) if line.startswith("{") else {"src": line}
        if r.get("src"):
            used[img_key(r["src"])].add(page_key(r.get("page")))
    return used


def cmd_nn(a):
    sys.path.insert(0, str(SVI))
    sys.dont_write_bytecode = True  # không sinh __pycache__ trong skill khác
    import numpy as np
    import svi
    enc = svi.encoder(a.max_tokens)
    s, v = read_jsonl(a.slots), read_jsonl(a.videos)
    qs = enc.encode([x["text"] for x in s], a.qprompt)
    ds = enc.encode([x["text"] for x in v], a.dprompt)
    sims = qs @ ds.T
    with open(a.out, "w", encoding="utf-8") as fh:
        for i, row in enumerate(sims):
            top = np.argsort(-row)[: a.k]
            fh.write(json.dumps({"id": s[i]["id"], "max_cos": round(float(row[top[0]]), 4),
                                 "top": [{"id": v[j]["id"], "cos": round(float(row[j]), 4)} for j in top]}) + "\n")
    print(f"nn: {len(s)} slot × {len(v)} video -> {a.out}", file=sys.stderr)
    return 0


def cmd_check(a):
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    slots = plan["slots"] if isinstance(plan, dict) else plan
    nn = {r["id"]: [t["id"] for t in r["top"]] for r in read_jsonl(a.nn)} if a.nn else {}
    site_entity = plan.get("site_entity") if isinstance(plan, dict) else None
    used = read_used(a.used) if a.used else {}
    pages, img_pages = defaultdict(set), defaultdict(set)
    errs, rank = [], defaultdict(int)
    for s in slots:
        m = s.get("media") if isinstance(s.get("media"), dict) else {}
        sid, kind = s.get("slot_id"), s.get("decision") or m.get("kind")
        vid = m.get("video_id") or m.get("id")
        if kind in ("youtube", "youtube_video") and vid and not str(vid).startswith("chờ"):
            pages[vid].add(s.get("page"))
            if sid in nn:
                r = nn[sid].index(vid) + 1 if vid in nn[sid] else 0
                rank["top3" if 1 <= r <= 3 else ("top8" if r else "ngoài top8")] += 1
        if kind not in (None, "skip", "drop") and s.get("status") not in ("needs_source", "dropped"):
            for f in ("alt", "caption"):
                if not (s.get(f) or "").strip():
                    errs.append(f"{sid}: thiếu {f}")
        if kind == "ai_image" and (s.get("photo_class") in FAKE_KINDS or s.get("gap_media_type") == "real_photo"):
            errs.append(f"{sid}: ảnh AI thay ảnh thật sẽ thành ảnh giả")
        live = kind not in (None, "skip", "drop") and s.get("status") not in ("needs_source", "dropped")
        if live and s.get("purpose") == "testimonial":
            want = s.get("page_entity") or site_entity
            ent = s.get("speaker_entity")
            if not want:
                errs.append(f"{sid}: lời chứng thực cần page_entity hoặc site_entity để so entity người nói")
            elif not ent or not (s.get("speaker_evidence") or "").strip():
                errs.append(f"{sid}: lời chứng thực chưa kiểm entity người nói (thiếu speaker_entity hoặc speaker_evidence)")
            elif ent.strip().casefold() != want.strip().casefold():
                errs.append(f"{sid}: người nói thuộc {ent}, trang thuộc {want}")
        src = m.get("src") or m.get("file")
        if live and kind in IMAGE_KINDS and src and not s.get("allow_reuse"):
            k, pg = img_key(src), page_key(s.get("page"))
            img_pages[k].add(pg)
            if k in used:
                other = sorted(p for p in used[k] if p and p != pg)
                if other or None in used[k]:
                    errs.append(f"{sid}: ảnh {src} đã dùng ở trang khác: {other or 'theo --used'}")
    for vid, ps in pages.items():
        if len(ps) > a.max_pages:
            errs.append(f"video {vid} ở {len(ps)} trang (tối đa {a.max_pages}): {sorted(ps)}")
    for k, ps in img_pages.items():
        if len(ps) > 1:
            errs.append(f"ảnh {k} lặp ở {len(ps)} trang của plan: {sorted(ps)}")
    print(json.dumps({"slots": len(slots), "video_rank": dict(rank), "errors": errs}, ensure_ascii=False, indent=1))
    return 1 if errs else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nn")
    n.add_argument("--slots", required=True)
    n.add_argument("--videos", required=True)
    n.add_argument("--out", required=True)
    n.add_argument("--k", type=int, default=8)
    n.add_argument("--qprompt", default="SearchQuery")
    n.add_argument("--dprompt", default="Document")
    n.add_argument("--max-tokens", type=int, default=512)
    c = sub.add_parser("check")
    c.add_argument("--plan", required=True)
    c.add_argument("--nn")
    c.add_argument("--max-pages", type=int, default=2)
    c.add_argument("--used", help="ảnh đang dùng ở các trang: images.jsonl của visual.py images, hoặc .txt mỗi dòng một src")
    a = ap.parse_args(argv)
    return cmd_nn(a) if a.cmd == "nn" else cmd_check(a)


if __name__ == "__main__":
    sys.exit(main())
