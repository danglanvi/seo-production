#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okrs_sheet_diff.py — Kéo tab «OKRs Quý N» của team về snapshot CSV và đối chiếu với
bản OKRs canonical trong instance.

Vì sao cần: OKRs sống ở hai nơi — sheet team chạy hằng ngày, và file .md trong instance
(đóng công đoạn #8, có baseline + backup plan). Hai bản trôi khỏi nhau là chuyện chắc
chắn xảy ra. Script này trả lời đúng một câu hỏi: **file của mình còn khớp sheet của
team tới đâu?**

Ba việc:
  1. Kéo tab OKRs → ghi snapshot CSV vào 02-raw/ (immutable, ngày trong tên folder).
  2. Tách sheet thành cây Objective → Key Result (sheet gộp ô Objective, KR đánh số «1.» «2.»).
  3. Nếu có --compare <file .md>: in ra KR **chỉ có trên sheet**, KR **chỉ có trong file**,
     và KR khớp nhưng **lệch PIC / Deadline**.

Đối chiếu bằng chữ, không bằng ID — sheet không có ID ổn định. Ghép theo độ tương đồng
tiêu đề KR (SequenceMatcher ≥ ngưỡng), nên kết quả là **danh sách để người soi**, không
phải phán quyết tự động. Mọi dòng nghi ngờ đều in ra thay vì im lặng bỏ qua.

Chạy:
  python3 okrs_sheet_diff.py --config 09-reporting/report-config.yaml \\
      --range-key <key trong spreadsheets.<wb>.ranges> --workbook <key workbook> \\
      --snapshot 02-raw/seo-data/okrs/<YYYY-MM-DD>/okrs-quy<N>-sheet.csv \\
      [--compare 01-strategy-okrs/<CLIENT>_okrs-q<N>_v<N>.md] [--threshold 0.55]

  --no-fetch : bỏ qua gọi API, đọc thẳng file --snapshot đã có (chạy offline).

Chỉ ĐỌC Google Sheets. Không bao giờ ghi ngược lên sheet.
"""
import argparse
import csv
import difflib
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("LỖI: thiếu PyYAML (pip3 install pyyaml)\n")
    sys.exit(2)


def die(msg):
    sys.stderr.write("LỖI: %s\n" % msg)
    sys.exit(1)


def norm(s):
    """Chuan hoa chuoi de so khop: bo markdown, dau cau, so thu tu, khoang trang thua.

    Ban .md viet lai tieu de KR co **dam**, «nhay», emoji — sheet thi khong.
    Khong got sach may thu nay thi KR nao cung truot khop."""
    s = re.sub(r"<[^>]+>", " ", str(s or ""))
    s = s.replace("\u00a0", " ").lower()
    s = re.sub(r"^\s*(kr)?\s*\d+\s*[.)]?\s*", "", s)   # bo «1.» «2)» «KR3» dau dong
    s = s.replace("**", " ").replace("`", " ").replace("~~", " ")
    s = re.sub(r"[^\w\s%/\u00d7+-]", " ", s, flags=re.U)
    return re.sub(r"\s+", " ", s).strip()


def norm_date(s):
    """«15/8» «15/09» «≤31/08» → «15/08» — khac cach go ngay khong phai cho lech that.

    KHONG goi norm() o day: norm() cat so thu tu dau dong nen se an mat «15» cua «15/9».
    """
    t = re.sub(r"<[^>]+>", " ", str(s or "")).lower()
    t = t.replace("**", " ").replace("~~", " ").replace("`", " ")
    t = re.sub(r"[^\w\s/]", " ", t, flags=re.U)
    t = re.sub(r"\b(\d{1,2})/(\d{1,2})\b",
               lambda m: "%02d/%02d" % (int(m.group(1)), int(m.group(2))), t)
    return re.sub(r"\s+", " ", t).strip()


# Tu noi tieng Viet + dong tu chung cua moi KR — giu lai thi KR nao cung giong KR nao.
STOP = {"va", "cac", "cho", "cua", "theo", "voi", "tu", "trong", "ve", "da", "duoc", "mot",
        "la", "co", "de", "khi", "nay", "do", "nhom", "tien", "hanh", "trien", "khai",
        "thuc", "day", "hoan", "tat", "thien", "tang", "truong", "moi", "site", "page",
        "v\u00e0", "c\u00e1c", "c\u1ee7a", "v\u1edbi", "t\u1eeb", "v\u1ec1", "\u0111\u00e3",
        "\u0111\u01b0\u1ee3c", "m\u1ed9t", "l\u00e0", "c\u00f3", "\u0111\u1ec3",
        "n\u00e0y", "\u0111\u00f3", "nh\u00f3m", "ti\u1ebfn", "h\u00e0nh",
        "tri\u1ec3n", "khai", "th\u00fac", "\u0111\u1ea9y", "ho\u00e0n", "t\u1ea5t",
        "thi\u1ec7n", "t\u0103ng", "tr\u01b0\u1edfng", "m\u1edbi"}


def similarity(a, b):
    """Ba thuoc do, lay max — de nguoi soi quyet, script khong phan.

    · SequenceMatcher: bat cac cap gan nhu chep nguyen van.
    · Jaccard tu khoa : bat cap viet lai nhung cung bo tu khoa.
    · Containment     : bat cap tieu de sheet NGAN nam gon trong dong .md DAI
                        (ban .md hay nhet ca dien giai vao o Key Result).
    """
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    seq = difflib.SequenceMatcher(None, na, nb).ratio()
    wa = {w for w in na.split() if len(w) > 2 and w not in STOP}
    wb = {w for w in nb.split() if len(w) > 2 and w not in STOP}
    if not (wa | wb):
        return seq
    jac = len(wa & wb) / float(len(wa | wb))
    cont = len(wa & wb) / float(min(len(wa), len(wb))) if (wa and wb) else 0.0
    return max(seq, jac, cont * 0.9)   # ha nhe containment: bao gom khong manh bang trung khop


def fetch_sheet(cfg, range_key, workbook_key="ke_hoach_tong"):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    cred = os.path.expanduser(cfg["credentials"])
    if not os.path.exists(cred):
        die("không thấy credentials: %s" % cred)
    wb = (cfg.get("spreadsheets") or {}).get(workbook_key)
    if not wb:
        die("workbook «%s» không có trong config.spreadsheets" % workbook_key)
    rng = (wb.get("ranges") or {}).get(range_key)
    if not rng:
        die("range «%s» không có trong spreadsheets.%s.ranges" % (range_key, workbook_key))

    creds = service_account.Credentials.from_service_account_file(
        cred, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    res = svc.spreadsheets().values().get(
        spreadsheetId=wb["id"], range=rng,
        valueRenderOption="FORMATTED_VALUE").execute()
    rows = res.get("values", [])
    print("  kéo: %s → %d dòng" % (rng, len(rows)))
    return rows


def write_snapshot(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    width = max((len(r) for r in rows), default=0)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(list(r) + [""] * (width - len(r)))
    print("  snapshot: %s" % path)


def read_snapshot(path):
    if not os.path.isfile(path):
        die("không thấy snapshot %s — bỏ --no-fetch để kéo mới" % path)
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.reader(f)]


# ─────────────────────────────────────────────── tách cây O → KR

HEAD_HINTS = ("objectives", "key results", "pic", "deadline", "baseline")


def parse_sheet(rows):
    """[{oid, otitle, krs:[{title, pic, deadline, note, baseline}]}] — sheet gộp ô Objective."""
    objs, cur = [], None
    for r in rows:
        cells = [(c or "").strip() for c in r] + [""] * 6
        o, kr, pic, dl, note, base = cells[:6]
        low = " ".join(cells[:4]).lower()
        if any(h in low for h in HEAD_HINTS) and not kr.strip().startswith(tuple("0123456789")):
            continue                                     # dòng header
        if o:
            m = re.match(r"\s*(O\d+)\s*[:.\-]?\s*(.*)", o, re.S)
            oid = m.group(1) if m else "O?"
            otitle = (m.group(2) if m else o).strip()
            cur = {"oid": oid, "otitle": otitle, "krs": []}
            objs.append(cur)
        if kr and cur is not None:
            title = kr.split("\n")[0].strip()
            cur["krs"].append({"title": title, "full": kr, "pic": pic,
                               "deadline": dl, "note": note, "baseline": base})
    return [o for o in objs if o["krs"]]


def parse_md(path):
    """Đọc bản .md canonical: bảng KR có cột | # | Key Result | Baseline | Target | Owner | Deadline |"""
    if not os.path.isfile(path):
        die("không thấy file so sánh: %s" % path)
    txt = open(path, encoding="utf-8").read()
    objs, cur = [], None
    for line in txt.split("\n"):
        m = re.match(r"^###\s+(O\d+)\s*[—:\-]\s*(.*)", line.strip())
        if m:
            cur = {"oid": m.group(1), "otitle": m.group(2).strip(), "krs": []}
            objs.append(cur)
            continue
        if cur is None or not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 6 or not re.match(r"^KR\d+$", cols[0]):
            continue
        cur["krs"].append({"title": cols[1], "full": cols[1], "baseline": cols[2],
                           "target": cols[3], "pic": cols[4], "deadline": cols[5],
                           "note": cols[6] if len(cols) > 6 else ""})
    return [o for o in objs if o["krs"]]


# ─────────────────────────────────────────────── đối chiếu

def match(a_krs, b_krs, threshold):
    """Ghép KR theo độ tương đồng tiêu đề. Trả (cặp khớp, chỉ-có-A, chỉ-có-B)."""
    used, pairs = set(), []
    for i, a in enumerate(a_krs):
        best, bi = 0.0, None
        for j, b in enumerate(b_krs):
            if j in used:
                continue
            r = similarity(a["title"], b["title"])
            if r > best:
                best, bi = r, j
        if bi is not None and best >= threshold:
            used.add(bi)
            pairs.append((a, b_krs[bi], best))
        else:
            pairs.append((a, None, best))
    only_b = [b for j, b in enumerate(b_krs) if j not in used]
    return pairs, only_b


def main():
    ap = argparse.ArgumentParser(description="Đối chiếu OKRs sheet team vs bản canonical trong instance")
    ap.add_argument("--config", required=True)
    # Tab OKRs doi cho giua cac ky va giua cac client — KHONG dat mac dinh, bat
    # nguoi chay khai tuong minh sau khi xac nhan tab team dang duy tri.
    ap.add_argument("--range-key", required=True, help="key trong spreadsheets.<wb>.ranges")
    ap.add_argument("--workbook", required=True, help="key workbook trong spreadsheets:")
    ap.add_argument("--snapshot", required=True, help="đường dẫn CSV snapshot (ghi ra, hoặc đọc vào khi --no-fetch)")
    ap.add_argument("--compare", help="file .md canonical để đối chiếu")
    ap.add_argument("--threshold", type=float, default=0.55, help="ngưỡng tương đồng tiêu đề KR (0-1)")
    ap.add_argument("--no-fetch", action="store_true", help="không gọi API, đọc snapshot có sẵn")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.no_fetch:
        rows = read_snapshot(args.snapshot)
        print("  đọc snapshot có sẵn: %s (%d dòng)" % (args.snapshot, len(rows)))
    else:
        rows = fetch_sheet(cfg, args.range_key, args.workbook)
        if not rows:
            die("sheet trả về 0 dòng — kiểm lại range")
        write_snapshot(rows, args.snapshot)

    sheet = parse_sheet(rows)
    n_kr = sum(len(o["krs"]) for o in sheet)
    print("\nSHEET: %d Objective · %d KR" % (len(sheet), n_kr))
    for o in sheet:
        flag = "" if len(o["krs"]) <= 5 else "   ⚠ VƯỢT TRẦN 5 KR"
        print("  %-4s %d KR%s  %s" % (o["oid"], len(o["krs"]), flag, o["otitle"][:78]))

    if not args.compare:
        print("\n(không có --compare → chỉ snapshot. Thêm --compare <file .md> để đối chiếu)")
        return

    md = parse_md(args.compare)
    print("\nFILE : %s — %d Objective · %d KR"
          % (args.compare, len(md), sum(len(o["krs"]) for o in md)))

    md_by_oid = {o["oid"]: o for o in md}
    total_gap = 0
    print("\n" + "=" * 92)
    print("ĐỐI CHIẾU (ngưỡng tương đồng %.2f — mọi dòng nghi ngờ đều in ra để người soi)" % args.threshold)
    print("=" * 92)

    for so in sheet:
        mo = md_by_oid.get(so["oid"])
        print("\n### %s — %s" % (so["oid"], so["otitle"][:74]))
        if not mo:
            print("   ✗ Objective này KHÔNG có trong file .md")
            total_gap += 1
            continue
        pairs, only_md = match(so["krs"], mo["krs"], args.threshold)
        for a, b, score in pairs:
            if b is None:
                print("   ✗ CHỈ CÓ TRÊN SHEET (%.2f) : %s" % (score, a["title"][:76]))
                total_gap += 1
                continue
            diffs = []
            for k, lbl in (("pic", "PIC"), ("deadline", "Deadline")):
                f = norm_date if k == "deadline" else norm
                va, vb = f(a.get(k)), f(b.get(k))
                if va and vb and va != vb:
                    diffs.append("%s sheet «%s» ≠ file «%s»" % (lbl, a.get(k), b.get(k)))
            if diffs:
                print("   ⚠ LỆCH (%.2f) : %s" % (score, a["title"][:66]))
                for d in diffs:
                    print("        · %s" % d)
                total_gap += len(diffs)
            else:
                print("   ✓ khớp (%.2f) : %s" % (score, a["title"][:70]))
        for b in only_md:
            print("   ✗ CHỈ CÓ TRONG FILE .md    : %s" % b["title"][:76])
            total_gap += 1

    for mo in md:
        if mo["oid"] not in {o["oid"] for o in sheet}:
            print("\n### %s — ✗ Objective chỉ có trong file .md: %s" % (mo["oid"], mo["otitle"][:60]))
            total_gap += 1

    print("\n" + "=" * 92)
    if total_gap == 0:
        print("KẾT LUẬN: file .md KHỚP sheet team — cập nhật `fact_check:` trong frontmatter.")
    else:
        print("KẾT LUẬN: %d chỗ lệch cần xử. Sheet là bản team đang chạy — lệch chỗ nào thì HỎI," % total_gap)
        print("          đừng mặc định file .md đúng. Xử xong mới cập nhật `fact_check:`.")
    print("=" * 92)
    sys.exit(0)


if __name__ == "__main__":
    main()
