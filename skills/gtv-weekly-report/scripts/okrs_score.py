#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okrs_score.py — Chấm điểm OKRs quý vừa khép, sinh danh sách carry-over, và soi chất
lượng bản nháp OKRs quý kế.

Ba đầu ra:
  1. Điểm từng KR + điểm từng Objective (trung bình KR) theo thang 0.0–1.0 của
     _TEMPLATES/okrs.md §6.
  2. Carry-over: KR chưa Done → tự động sang kỳ sau, status «Chuyển tiếp»
     (rule Vincent chốt 23/07/2026, áp cho cả plan tháng lẫn OKRs quý).
  3. Soi bản nháp quý kế theo luật lập OKRs: mỗi KR phải có baseline + target đo được
     + owner + deadline. KR thiếu con số là KR không chấm điểm được vào cuối quý.

KR không có status KHÔNG bị chấm 0 — bị đánh CANNOT-VERIFY và loại khỏi phép trung
bình, có liệt kê riêng. Chấm 0 cho ô người ta quên điền là bịa số theo hướng xấu.

Chạy offline: đọc digest.json đã fetch.

Cách chạy:
  python3 okrs_score.py --config <report-config.yaml> --period 2026-Q1
  python3 okrs_score.py --config ... --period 2026-Q1 --md 09-reporting/okrs-q1-score.md
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import yaml  # noqa: E402

# Bảng quy đổi status → điểm. Khai tường minh để người đọc báo cáo cãi được, thay vì
# giấu trong đầu AI. «Đang làm» = 0.5 là quy ước bảo thủ: có tiến triển nhưng chưa xong.
STATUS_SCORE = {
    "done": 1.0,
    "hoàn thành": 1.0,
    "đang làm": 0.5,
    "in progress": 0.5,
    "trễ hạn": 0.3,
    "tạm ngưng": 0.2,
    "chưa bắt đầu": 0.0,
}
SCORE_BAND = [(0.9, "xuất sắc (soát lại: target có đặt thấp quá không)"),
              (0.7, "đạt tốt"), (0.4, "đạt một phần"), (0.0, "không đạt")]

STOPWORDS = set("và của các cho từ với theo trên trong tại về là các một những "
                "triển khai hoàn thiện hoàn tất thúc đẩy tăng chuẩn hoá chuẩn hóa "
                "thực hiện tiến hành đề xuất lên plan file".split())


def log(m):
    print(m, flush=True)


def norm(s):
    s = unicodedata.normalize("NFC", str(s or "")).lower()
    return re.sub(r"\s+", " ", s).strip()


def tokens(s):
    t = re.findall(r"[a-zà-ỹ0-9]+", norm(s))
    return {w for w in t if len(w) > 2 and w not in STOPWORDS}


def band(score):
    for lo, label in SCORE_BAND:
        if score >= lo:
            return label
    return "không đạt"


def parse_okrs(rows, cols):
    """Dòng có cột Objective → mở Objective mới; dòng chỉ có cột KR → KR của Objective đang mở."""
    hdr = next((i for i, r in enumerate(rows)
                if norm(r[0] if r else "").startswith("objective")), None)
    if hdr is None:
        return []
    objs, cur = [], None

    def g(r, key):
        j = cols.get(key)
        return " ".join(str(r[j]).split()) if j is not None and j < len(r) else ""

    for r in rows[hdr + 1:]:
        if not r or not any(str(c).strip() for c in r):
            continue
        o_txt = " ".join(str(r[0]).split()) if r else ""
        kr_txt = g(r, "kr")
        if o_txt:
            cur = {"objective": o_txt, "krs": []}
            objs.append(cur)
        if not kr_txt or cur is None:
            continue
        cur["krs"].append({
            "kr": kr_txt,
            "pic": g(r, "pic"),
            "deadline": g(r, "deadline"),
            "status": g(r, "status"),
            "note": g(r, "note"),
            "baseline": g(r, "baseline"),
            "file": g(r, "file"),
        })
    return objs


def score_objectives(objs):
    for o in objs:
        scored, unknown = [], []
        for kr in o["krs"]:
            s = STATUS_SCORE.get(norm(kr["status"]))
            kr["score"] = s
            if s is None:
                kr["verdict"] = "CANNOT-VERIFY — ô Status để trống, không chấm"
                unknown.append(kr)
            else:
                kr["verdict"] = band(s)
                scored.append(s)
        o["score"] = round(sum(scored) / len(scored), 2) if scored else None
        o["band"] = band(o["score"]) if o["score"] is not None else "không chấm được"
        o["kr_scored"] = len(scored)
        o["kr_unknown"] = len(unknown)
    return objs


def carry_over(objs):
    out = []
    for o in objs:
        for kr in o["krs"]:
            if norm(kr["status"]) in ("done", "hoàn thành"):
                continue
            out.append({
                "objective": o["objective"],
                "kr": kr["kr"],
                "pic": kr["pic"],
                "status_cu": kr["status"] or "(trống)",
                "status_moi": "Chuyển tiếp",
                "note": kr["note"],
            })
    return out


def match_next_quarter(carry, next_objs, strong=0.34, weak=0.18):
    """Ướm từng việc tồn sang bản nháp quý kế. Chỉ là GỢI Ý cho người rà — trùng từ khoá
    không có nghĩa là cùng một việc.

    Dùng ĐỘ CHỨA |A∩B|/min(|A|,|B|) chứ không phải Jaccard: KR quý này viết dài dòng
    (kèm mô tả, link, ghi chú) trong khi KR quý sau viết cô đọng, Jaccard sẽ phạt nặng
    phần chênh độ dài và báo "không thấy" cho những việc thực ra có mặt.
    Luôn trả về ứng viên gần nhất kèm điểm, kể cả khi dưới ngưỡng — để người rà tự quyết,
    thay vì nuốt mất thông tin."""
    nxt = [{"objective": o["objective"], "kr": kr["kr"],
            "tok": tokens(o["objective"] + " " + kr["kr"])}
           for o in next_objs for kr in o["krs"]]
    for c in carry:
        ct = tokens(c["objective"] + " " + c["kr"])
        best, best_s = None, 0.0
        for n in nxt:
            if not ct or not n["tok"]:
                continue
            ov = len(ct & n["tok"]) / min(len(ct), len(n["tok"]))
            if ov > best_s:
                best, best_s = n, ov
        c["match_score"] = round(best_s, 3)
        c["kr_q2_gan_nhat"] = best["kr"][:110] if best else None
        # Ghép từ khoá tiếng Việt KHÔNG đủ tin để kết luận "việc này đã/chưa có trong Q2"
        # (đã thấy nó ướm «Plan content Strategy» sang «plan Backlink»). Chỉ phát tín hiệu
        # thô kèm điểm; việc ánh xạ đúng nghĩa phải do người đọc chốt.
        c["kr_q2"] = best["kr"][:110] if (best and best_s >= strong) else None
        c["goi_y_may"] = ("ứng viên mạnh" if best and best_s >= strong
                          else "ứng viên yếu" if best and best_s >= weak
                          else "không có ứng viên gần")
        c["can_nguoi_chot"] = True
    return carry


def audit_next_quarter(objs):
    """Soi bản nháp quý kế: KR thiếu con số/deadline/PIC là KR cuối quý không chấm được."""
    findings = []
    for o in objs:
        for kr in o["krs"]:
            miss = []
            if not kr["pic"]:
                miss.append("PIC")
            if not kr["deadline"]:
                miss.append("deadline")
            blob = f"{kr['kr']} {kr['note']} {kr['baseline']}"
            if not re.search(r"\d", blob):
                miss.append("con số target/baseline")
            elif not kr["baseline"]:
                miss.append("baseline (có target nhưng chưa có mốc xuất phát)")
            if miss:
                findings.append({"objective": o["objective"][:60], "kr": kr["kr"][:100],
                                 "thieu": miss})
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--period", required=True)
    ap.add_argument("--md", default=None, help="Ghi bản markdown cho người đọc")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg_dir = os.path.dirname(os.path.abspath(args.config))
    p = (cfg.get("periods") or {}).get(args.period)
    if not p:
        sys.exit(f"LỖI: kỳ {args.period!r} không có trong config")
    bucket = "monthly" if p.get("mode") == "month" else "quarterly"
    d = os.path.join(os.path.dirname(cfg_dir), "02-raw", "seo-data", bucket, args.period)
    digest_p = os.path.join(d, "digest.json")
    if not os.path.isfile(digest_p):
        sys.exit(f"LỖI: thiếu {digest_p} — chạy fetch_period_data.py trước")
    digest = json.load(open(digest_p, encoding="utf-8"))

    cur = parse_okrs(digest["sections"].get("okrs_quy_1") or [],
                     {"kr": 1, "file": 5, "pic": 6, "status": 8, "note": 9, "deadline": 3})
    nxt = parse_okrs(digest["sections"].get("okrs_quy_2") or [],
                     {"kr": 1, "pic": 2, "deadline": 3, "note": 4, "baseline": 5})
    if not cur:
        sys.exit("LỖI: không đọc được bảng OKRs quý này (section okrs_quy_1)")

    score_objectives(cur)
    carry = match_next_quarter(carry_over(cur), nxt)
    draft_gaps = audit_next_quarter(nxt)

    n_kr = sum(len(o["krs"]) for o in cur)
    done = sum(1 for o in cur for k in o["krs"] if norm(k["status"]) == "done")
    doing = sum(1 for o in cur for k in o["krs"] if norm(k["status"]) == "đang làm")
    blank = sum(1 for o in cur for k in o["krs"] if not k["status"])
    scored = [o["score"] for o in cur if o["score"] is not None]
    overall = round(sum(scored) / len(scored), 2) if scored else None

    log(f"\n{'='*100}\nCHẤM ĐIỂM OKRs — {args.period} ({p.get('label')})")
    log(f"  {len(cur)} Objective · {n_kr} KR  →  Done {done} · Đang làm {doing} · chưa điền status {blank}")
    log(f"  Điểm trung bình toàn kỳ: {overall}  ({band(overall) if overall is not None else '—'})\n")
    for i, o in enumerate(cur, 1):
        sc = f"{o['score']:.2f}" if o["score"] is not None else "—"
        log(f"  O{i}. {o['objective'][:78]}")
        log(f"      điểm {sc} ({o['band']}) · chấm {o['kr_scored']}/{len(o['krs'])} KR"
            + (f" · {o['kr_unknown']} KR chưa có status" if o["kr_unknown"] else ""))
        for kr in o["krs"]:
            mark = f"{kr['score']:.1f}" if kr["score"] is not None else " ? "
            log(f"        [{mark}] {kr['kr'][:66]:<66} {kr['status'] or '(trống)'}")

    log(f"\n  ── CARRY-OVER sang quý kế: {len(carry)} việc ──")
    log("     (Việc ướm sang Q2 chỉ là gợi ý máy theo từ khoá — người đọc phải chốt.)")
    for c in carry:
        log(f"       · {c['kr'][:70]}")
        log(f"           PIC {c['pic'] or '—'} · status cũ {c['status_cu']} → «Chuyển tiếp» "
            f"· {c['goi_y_may']} ({c['match_score']})")

    if nxt:
        log(f"\n  ── SOI BẢN NHÁP OKRs QUÝ KẾ: {len(nxt)} Objective · "
            f"{sum(len(o['krs']) for o in nxt)} KR ──")
        if draft_gaps:
            log(f"     {len(draft_gaps)} KR còn thiếu thành phần bắt buộc:")
            for g in draft_gaps:
                log(f"       · {g['kr'][:68]:<68} thiếu: {', '.join(g['thieu'])}")
        else:
            log("     ✓ mọi KR đều đủ PIC + deadline + con số")

    res = {"period": args.period, "label": p.get("label"),
           "overall_score": overall, "objectives": cur,
           "counts": {"objectives": len(cur), "krs": n_kr, "done": done,
                      "doing": doing, "no_status": blank},
           "status_score_map": STATUS_SCORE,
           "carry_over": carry, "next_quarter_objectives": nxt,
           "next_quarter_gaps": draft_gaps}
    out_p = os.path.join(d, f"okrs_score_{args.period}.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    log(f"\n  → {out_p}")

    if args.md:
        L = [f"# Chấm điểm OKRs {p.get('label')} — {cfg.get('client_name') or cfg.get('client') or ''}".rstrip(" —"), "",
             f"Nguồn: sheet OKRs vận hành (tab theo range khai trong config). Thang điểm theo `_TEMPLATES/okrs.md` §6. "
             f"Quy đổi status → điểm: " + " · ".join(f"{k} = {v}" for k, v in STATUS_SCORE.items()) + ".",
             f"KR chưa điền status được đánh CANNOT-VERIFY và **loại khỏi phép trung bình** "
             f"(không chấm 0).", "",
             f"**Điểm toàn kỳ: {overall} — {band(overall) if overall is not None else '—'}** "
             f"({len(cur)} Objective · {n_kr} KR · Done {done} · Đang làm {doing} · "
             f"chưa có status {blank})", "",
             "## Điểm theo Objective", "",
             "| # | Objective | Điểm | Xếp loại | KR chấm được |", "|---|---|---|---|---|"]
        for i, o in enumerate(cur, 1):
            sc = f"{o['score']:.2f}" if o["score"] is not None else "—"
            L.append(f"| O{i} | {o['objective'][:78]} | **{sc}** | {o['band']} | "
                     f"{o['kr_scored']}/{len(o['krs'])} |")
        L += ["", "## Việc chuyển tiếp sang quý sau", "",
              "Rule Vincent 23/07/2026: KR chưa Done tự động sang kỳ kế, status «Chuyển tiếp».", "",
              "> Cột cuối là **gợi ý máy theo trùng từ khoá** — không phải kết luận. "
              "Việc quyết KR nào thực sự đã có chỗ trong Q2 phải do người đọc chốt.", "",
              "| KR | PIC | Status cũ | Gợi ý máy | KR Q2 gần nhất |",
              "|---|---|---|---|---|"]
        for c in carry:
            L.append(f"| {c['kr'][:80]} | {c['pic'] or '—'} | {c['status_cu']} | "
                     f"{c['goi_y_may']} ({c['match_score']}) | {(c.get('kr_q2_gan_nhat') or '—')[:70]} |")
        if draft_gaps:
            L += ["", "## Bản nháp OKRs quý kế — KR còn thiếu thành phần", "",
                  "KR thiếu baseline hoặc con số target thì cuối quý không chấm điểm được.", "",
                  "| Objective | KR | Thiếu |", "|---|---|---|"]
            for g in draft_gaps:
                L.append(f"| {g['objective']} | {g['kr']} | {', '.join(g['thieu'])} |")
        os.makedirs(os.path.dirname(os.path.abspath(args.md)), exist_ok=True)
        with open(args.md, "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        log(f"  → {args.md}")


if __name__ == "__main__":
    main()
