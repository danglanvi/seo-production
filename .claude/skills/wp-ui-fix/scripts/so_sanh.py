#!/usr/bin/env python3
"""Dựng trang HTML so ảnh trước/sau từ hai lượt chụp của shot_el.mjs: cặp ảnh, khung đỏ quanh vùng đổi, bảng số liệu,
lựa chọn có đánh dấu đề xuất, ô ghi chú và nút "Chép câu trả lời". Chỉ đọc ảnh trên máy, không gọi mạng.

Chạy: python3 so_sanh.py --dir DIR [--truoc truoc] [--sau sau] [--out FILE.html] [--title "..."]
                         [--cau-hoi cau-hoi.json] [--so-lieu so-lieu.json] [--thr 40] [--gap 24] [--embed] [--json]

  --dir       thư mục chứa shots_<nhãn>.json và ảnh của hai lượt chụp
  --truoc     nhãn lượt trước (mặc định truoc);  --sau  nhãn lượt sau (mặc định sau)
  --out       file HTML ra (mặc định <dir>/so-sanh_v<N>.html, N tự tăng khi file đã có)
  --cau-hoi   {"cau_hoi": [{"id", "hoi", "boi_canh"?, "lua_chon": [{"id", "nhan", "de_xuat"?}]}]}. Mặc định một câu duyệt bản sau
  --so-lieu   [{"muc", "truoc", "sau", "ghi_chu"?}], ví dụ điểm PSI trước/sau lấy từ wp-pagespeed
  --thr       ngưỡng lệch độ sáng 0–255 để tính một điểm ảnh là đổi (mặc định 40)
  --gap       hai vùng đổi cách nhau dưới N px theo chiều dọc thì gộp một khung (mặc định 24)
  --embed     nhúng ảnh vào HTML (base64) để gửi một file
  --json      in kết quả dạng JSON

Ghép cặp theo (name, width) của hai file shots_*.json. Cặp "không đổi" chỉ là cảnh báo: bản sửa chưa lên, cache cũ, hoặc trang đối chứng.
Mã thoát: 0 xong · 1 thiếu cặp ảnh hoặc ảnh lỗi (HTML vẫn dựng cho các cặp còn lại) · 2 sai cú pháp hoặc file JSON sai.
"""
import argparse
import base64
import html
import json
import os
import re
import sys

Image = ImageChops = None

DEFAULT_Q = [{"id": "q1", "hoi": "Duyệt bản sau để áp tiếp?", "lua_chon": [
    {"id": "duyet", "nhan": "Duyệt bản sau", "de_xuat": True},
    {"id": "sua", "nhan": "Sửa tiếp theo ghi chú"},
    {"id": "giu", "nhan": "Giữ bản trước, trả về"}]}]
MAX_BOXES = 20


def load_json(path, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise ValueError("không đọc được %s %s: %s" % (what, path, e))


def load_questions(path):
    if not path:
        return DEFAULT_Q
    data = load_json(path, "--cau-hoi")
    qs = data.get("cau_hoi") if isinstance(data, dict) else data
    if not isinstance(qs, list) or not qs:
        raise ValueError("--cau-hoi phải có danh sách cau_hoi không rỗng")
    seen = set()
    for q in qs:
        if not isinstance(q, dict) or not q.get("id") or not q.get("hoi"):
            raise ValueError("mỗi câu hỏi cần id và hoi: %s" % q)
        if q["id"] in seen:
            raise ValueError("id câu hỏi trùng: %s" % q["id"])
        seen.add(q["id"])
        opts = q.get("lua_chon")
        if not isinstance(opts, list) or len(opts) < 2:
            raise ValueError("câu %s cần ít nhất 2 lựa chọn" % q["id"])
        if len({o.get("id") for o in opts}) != len(opts) or any(not o.get("id") or not o.get("nhan") for o in opts):
            raise ValueError("câu %s: mỗi lựa chọn cần id riêng và nhan" % q["id"])
        if sum(1 for o in opts if o.get("de_xuat")) > 1:
            raise ValueError("câu %s có hơn một lựa chọn đề xuất" % q["id"])
    return qs


def load_metrics(path):
    if not path:
        return []
    data = load_json(path, "--so-lieu")
    rows = data.get("rows") if isinstance(data, dict) else data
    if not isinstance(rows, list) or any(not isinstance(r, dict) or "muc" not in r for r in rows):
        raise ValueError("--so-lieu phải là danh sách {muc, truoc, sau, ghi_chu?}")
    return rows


def change_boxes(pa, pb, thr, gap):
    """So hai ảnh trên vùng chung (góc trên trái). Trả (khung [x0,y0,x1,y1], % điểm ảnh đổi, cỡ A, cỡ B)."""
    A, B = Image.open(pa), Image.open(pb)
    sa, sb = A.size, B.size
    A, B = A.convert("L"), B.convert("L")
    w, h = min(sa[0], sb[0]), min(sa[1], sb[1])
    d = ImageChops.difference(A.crop((0, 0, w, h)), B.crop((0, 0, w, h))).point(lambda v: 255 if v > thr else 0)
    changed = d.histogram()[255]
    pct = round(100.0 * changed / (w * h), 2) if w * h else 0.0
    if not changed:
        return [], 0.0, sa, sb
    rows = list(d.convert("F").resize((1, h), Image.BOX).getdata())
    bands, start, last = [], None, None
    for y, v in enumerate(rows):
        if v > 0:
            if start is None:
                start = y
            elif y - last > gap:
                bands.append((start, last))
                start = y
            last = y
    if start is not None:
        bands.append((start, last))
    boxes = []
    for y0, y1 in bands:
        crop = d.crop((0, y0, w, y1 + 1))
        if crop.histogram()[255] < 6:
            continue
        bb = crop.getbbox()
        if bb:
            boxes.append([bb[0], y0 + bb[1], bb[2] - 1, y0 + bb[3] - 1])
    if len(boxes) > MAX_BOXES:
        boxes.sort(key=lambda b: -(b[2] - b[0] + 1) * (b[3] - b[1] + 1))
        boxes = sorted(boxes[:MAX_BOXES], key=lambda b: b[1])
    return boxes, pct, sa, sb


def next_out(d):
    n = 1
    while os.path.exists(os.path.join(d, "so-sanh_v%d.html" % n)):
        n += 1
    return os.path.join(d, "so-sanh_v%d.html" % n)


def img_src(path, out_dir, embed):
    if embed:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    return os.path.relpath(path, out_dir).replace(os.sep, "/")


def overlay(boxes, size):
    W, H = size
    out = []
    for x0, y0, x1, y1 in boxes:
        out.append('<span class="box" style="left:%.3f%%;top:%.3f%%;width:%.3f%%;height:%.3f%%"></span>' % (
            100.0 * x0 / W, 100.0 * y0 / H, 100.0 * (x1 - x0 + 1) / W, 100.0 * (y1 - y0 + 1) / H))
    return "".join(out)


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1a1a1a;--muted:#5f6368;--line:#dadce0;--red:#d93025;--gold:#c99a06;--gold-bg:#fff8e1;--ok:#188038}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:1440px;margin:0 auto;padding:24px 16px 80px}h1{font-size:26px;line-height:1.25;margin:0 0 4px}h2{font-size:20px;margin:32px 0 12px}
.meta{color:var(--muted);font-size:14px;margin:0 0 16px}.legend{font-size:14px;color:var(--muted)}.legend b{color:var(--red)}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:15px}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:#f1f3f4}
.pair{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:0 0 20px}
.pair h3{font-size:16px;margin:0 0 8px}.pair .st{font-size:14px;color:var(--muted);margin:0 0 10px}.st.warn{color:var(--red)}
.cols{display:grid;grid-template-columns:1fr;gap:12px}@media (min-width:900px){.cols{grid-template-columns:1fr 1fr}}
figure{margin:0}figcaption{font-size:13px;font-weight:600;color:var(--muted);margin:0 0 4px;text-transform:uppercase;letter-spacing:.04em}
.shot{position:relative;display:inline-block;max-width:100%;border:1px solid var(--line);line-height:0}.shot img{max-width:100%;height:auto;display:block}
.box{position:absolute;border:2px solid var(--red);box-shadow:0 0 0 1px #fff;pointer-events:none}
.q{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:0 0 14px}.q p{margin:0 0 8px}
.opt{display:block;border:1px solid var(--line);border-radius:6px;padding:8px 10px;margin:6px 0;cursor:pointer}.opt.dx{border:2px solid var(--gold);background:var(--gold-bg)}
.tag{display:inline-block;font-size:12px;font-weight:700;color:#7a5c00;background:#ffe9a8;border-radius:4px;padding:0 6px;margin-left:6px}
textarea{width:100%;min-height:56px;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px}
button{font:inherit;font-weight:600;padding:10px 18px;border:0;border-radius:6px;background:#1a73e8;color:#fff;cursor:pointer}#done{margin-left:10px;color:var(--ok);font-size:14px}
.miss{color:var(--red)}
"""

JS = """
(function(){
  var KEY='so-sanh:'+document.title;
  function save(){try{var s={};document.querySelectorAll('input[type=radio]:checked').forEach(function(r){s[r.name]=r.value});
    document.querySelectorAll('textarea').forEach(function(t){s['note:'+t.id]=t.value});localStorage.setItem(KEY,JSON.stringify(s))}catch(e){}}
  function load(){try{var s=JSON.parse(localStorage.getItem(KEY)||'{}');Object.keys(s).forEach(function(k){
    if(k.indexOf('note:')===0){var t=document.getElementById(k.slice(5));if(t)t.value=s[k]}
    else{var r=document.querySelector('input[name="'+k+'"][value="'+s[k]+'"]');if(r)r.checked=true}})}catch(e){}}
  function answer(){var L=[document.title+' - trả lời'];
    document.querySelectorAll('.q').forEach(function(q){var id=q.dataset.id,pick=q.querySelector('input:checked'),dx=q.querySelector('input[data-dx="1"]');
      var line=id+' ('+q.dataset.hoi+'): ';
      if(pick){line+=pick.value+' - '+pick.dataset.nhan}else if(dx){line+=dx.value+' - '+dx.dataset.nhan+' (trống, theo đề xuất)'}else{line+='(chưa chọn)'}
      L.push(line);var n=document.getElementById('note-'+id);if(n&&n.value.trim())L.push('  ghi chú: '+n.value.trim())});
    var g=document.getElementById('note-chung');if(g&&g.value.trim())L.push('Ghi chú chung: '+g.value.trim());return L.join('\\n')}
  function copy(){var t=answer(),ok=function(){var d=document.getElementById('done');d.textContent='Đã chép';setTimeout(function(){d.textContent=''},2500)};
    if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,function(){fb(t);ok()})}else{fb(t);ok()}}
  function fb(t){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy')}catch(e){}document.body.removeChild(a)}
  document.addEventListener('change',save);document.addEventListener('input',save);load();
  document.getElementById('chep').addEventListener('click',copy);window.__answer=answer;
})();
"""


def build_html(title, pairs, missing, questions, metrics, out_dir, embed, args):
    e = html.escape
    P = ['<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         "<title>%s</title><style>%s</style></head><body><main>" % (e(title), CSS),
         "<h1>%s</h1>" % e(title),
         '<p class="meta">Lượt trước: <b>%s</b> · lượt sau: <b>%s</b> · %d cặp ảnh · ngưỡng lệch %d</p>' % (e(args.truoc), e(args.sau), len(pairs), args.thr),
         '<p class="legend">Khung <b>đỏ</b> đánh dấu vùng ảnh khác nhau giữa hai lượt. Khung không cho biết bản nào đẹp hơn.</p>']
    if metrics:
        P.append("<h2>Số liệu trước và sau</h2><table><tr><th>Mục</th><th>Trước</th><th>Sau</th><th>Ghi chú</th></tr>")
        for r in metrics:
            P.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(e(str(r.get(k, ""))) for k in ("muc", "truoc", "sau", "ghi_chu")))
        P.append("</table>")
    P.append("<h2>Ảnh trước và sau</h2>")
    for p in pairs:
        warn = p["status"] == "không đổi" or p.get("note")
        P.append('<section class="pair"><h3>%s · %d px</h3><p class="st%s">%s · %s%% điểm ảnh đổi · %d khung%s</p><div class="cols">' % (
            e(p["name"]), p["width"], " warn" if warn else "", e(p["status"]), p["pct"], len(p["boxes"]), (" · " + e(p["note"])) if p.get("note") else ""))
        for side, key, size in (("Trước", "img_truoc", p["size_truoc"]), ("Sau", "img_sau", p["size_sau"])):
            P.append('<figure><figcaption>%s</figcaption><div class="shot"><img src="%s" alt="%s %s %d px" loading="lazy">%s</div></figure>' % (
                side, e(img_src(p[key], out_dir, embed)), side, e(p["name"]), p["width"], overlay(p["boxes"], size)))
        P.append("</div></section>")
    if missing:
        P.append('<h2>Thiếu cặp</h2><ul class="miss">%s</ul>' % "".join("<li>%s</li>" % e(m) for m in missing))
    P.append("<h2>Câu cần duyệt</h2>")
    for q in questions:
        P.append('<div class="q" data-id="%s" data-hoi="%s"><p><b>%s</b></p>%s' % (
            e(q["id"]), e(q["hoi"]), e(q["hoi"]), ("<p>%s</p>" % e(q["boi_canh"])) if q.get("boi_canh") else ""))
        for o in q["lua_chon"]:
            dx = bool(o.get("de_xuat"))
            P.append('<label class="opt%s"><input type="radio" name="%s" value="%s" data-nhan="%s"%s> %s%s</label>' % (
                " dx" if dx else "", e(q["id"]), e(o["id"]), e(o["nhan"]), ' data-dx="1"' if dx else "", e(o["nhan"]), '<span class="tag">Đề xuất</span>' if dx else ""))
        P.append('<textarea id="note-%s" placeholder="Ghi chú cho câu này"></textarea></div>' % e(q["id"]))
    P.append('<div class="q"><p><b>Ghi chú chung</b></p><textarea id="note-chung" placeholder="Ghi chú chung"></textarea></div>')
    P.append('<p><button id="chep" type="button">Chép câu trả lời</button><span id="done" role="status"></span></p>')
    P.append("<script>%s</script></main></body></html>" % JS)
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--truoc", default="truoc")
    ap.add_argument("--sau", default="sau")
    ap.add_argument("--out")
    ap.add_argument("--title")
    ap.add_argument("--cau-hoi", dest="cau_hoi")
    ap.add_argument("--so-lieu", dest="so_lieu")
    ap.add_argument("--thr", type=int, default=40)
    ap.add_argument("--gap", type=int, default=24)
    ap.add_argument("--embed", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    global Image, ImageChops
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("Lỗi: thiếu Pillow (python3 -m pip install Pillow)", file=sys.stderr)
        return 2
    if not (0 <= a.thr <= 254) or a.gap < 0:
        print("Lỗi: --thr phải trong 0–254, --gap >= 0", file=sys.stderr)
        return 2
    if not re.match(r"^[A-Za-z0-9_-]+$", a.truoc) or not re.match(r"^[A-Za-z0-9_-]+$", a.sau):
        print("Lỗi: nhãn chỉ gồm chữ không dấu, số, - và _", file=sys.stderr)
        return 2
    try:
        A = load_json(os.path.join(a.dir, "shots_%s.json" % a.truoc), "lượt trước")
        B = load_json(os.path.join(a.dir, "shots_%s.json" % a.sau), "lượt sau")
        if not isinstance(A, dict) or not isinstance(B, dict) or not isinstance(A.get("shots"), list) or not isinstance(B.get("shots"), list):
            raise ValueError("file shots_*.json không có danh sách shots")
        questions = load_questions(a.cau_hoi)
        metrics = load_metrics(a.so_lieu)
    except ValueError as ex:
        print("Lỗi: %s" % ex, file=sys.stderr)
        return 2
    out = a.out or next_out(a.dir)
    out_dir = os.path.dirname(os.path.abspath(out))
    ia = {(s.get("name"), s.get("width")): s for s in A["shots"]}
    ib = {(s.get("name"), s.get("width")): s for s in B["shots"]}
    pairs, missing = [], []
    for key in list(ia) + [k for k in ib if k not in ia]:
        sa, sb = ia.get(key), ib.get(key)
        label = "%s %s px" % key
        if not sa or not sb:
            missing.append("%s: chỉ có ở lượt %s" % (label, a.truoc if sa else a.sau))
            continue
        if sa.get("error") or sb.get("error") or not sa.get("file") or not sb.get("file"):
            missing.append("%s: lượt chụp lỗi (%s)" % (label, sa.get("error") or sb.get("error") or "không có file"))
            continue
        pa, pb = os.path.join(a.dir, sa["file"]), os.path.join(a.dir, sb["file"])
        try:
            boxes, pct, size_a, size_b = change_boxes(pa, pb, a.thr, a.gap)
        except (OSError, ValueError) as ex:
            missing.append("%s: không đọc được ảnh (%s)" % (label, ex))
            continue
        note = None
        if size_a != size_b:
            note = "cỡ ảnh lệch %dx%d → %dx%d, chỉ so vùng chung" % (size_a + size_b)
        if sa.get("sel") != sb.get("sel"):
            note = (note + "; " if note else "") + "hai lượt chụp khác selector"
        pairs.append({"name": key[0], "width": key[1], "status": "đổi" if boxes else "không đổi", "pct": pct, "boxes": boxes,
                      "size_truoc": list(size_a), "size_sau": list(size_b), "img_truoc": pa, "img_sau": pb, **({"note": note} if note else {})})
    title = a.title or "So sánh trước và sau"
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(title, pairs, missing, questions, metrics, out_dir, a.embed, a))
    res = {"out": out, "pairs": [{k: v for k, v in p.items() if not k.startswith("img_")} for p in pairs], "missing": missing}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for p in pairs:
            flag = "CẢNH BÁO " if p["status"] == "không đổi" else ""
            print("%s%s %dpx: %s, %s%% điểm ảnh, %d khung%s" % (flag, p["name"], p["width"], p["status"], p["pct"], len(p["boxes"]), (" · " + p["note"]) if p.get("note") else ""))
        for m in missing:
            print("THIẾU " + m)
        print("Ghi %s" % out)
        print("Mở: file://%s" % os.path.abspath(out).replace(" ", "%20"))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
