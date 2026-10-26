#!/usr/bin/env python3
"""Gán nhãn hàng loạt bằng Jev 1.14 qua OpenRouter Decisions API.

Dùng: /usr/bin/python3 -I jev.py --task tasks/<tên>.json --in items.jsonl --out ket-qua.jsonl [--budget 0.5]
Kiểm trước, không gọi API, không ghi file: thêm --dry-run (kiểm input, ảnh, che secret, đếm ảnh cần đệm).
Kiểm key và thử một mẫu rồi dừng: thêm --preflight-only.
Mã thoát: 0 xong; 1 mọi dòng lỗi; 2 input hỏng (trường phải rỗng, ảnh thiếu hoặc hỏng), chưa gọi API;
3 dừng sớm (thiếu key, mẫu thử lỗi API, key bị từ chối, lỗi API liên tiếp).
Mỗi dòng input: {"id": "...", "state": {...}, "criteria": {"<câu hỏi>": {...}}}; "criteria" là tuỳ chọn,
dùng khi lựa chọn khác nhau theo từng dòng (ví dụ trang đích redirect).
Ảnh (Jev 1.14): đặt {"image_path": "<file .png/.jpg>"} trong state; đường dẫn tương đối tính từ thư mục file input.
Output không chép lại state, chỉ ghi nhãn, xác suất, model, độ trễ và chi phí.
"""
import argparse
import base64
import concurrent.futures as cf
import json
import math
import io
import os
import re
import struct
import sys
import threading
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"
KEY_NAME = "OPENROUTER_JEV_API_KEY"
MAX_BODY_BYTES = 60_000
MAX_IMAGE_BODY_BYTES = 24_000_000  # TypeSafe nhận tới 32 MiB mỗi request có ảnh
IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}  # Jev chỉ nhận PNG, JPEG
MIN_IMAGE_SIDE = 320  # Jev 1.14 trả http_400 khi cạnh ngắn dưới khoảng 280 px (19/10/2026, 15/80 ảnh gold)
MAX_CONSECUTIVE_ERRORS = 5
AUTH_FATAL = {"http_401", "http_402", "http_403"}  # key hết hạn, hết credit, bị từ chối: dừng ngay
# Lỗi của riêng một dòng input. Không tính vào chuỗi lỗi API liên tiếp.
ITEM_ERRORS = {"request_too_large", "image_not_found", "unsupported_image", "image_unreadable",
               "image_pad_needs_pillow", "image_pad_unsupported", "budget_reached", "aborted_consecutive_errors"}
PNG_SIG = b"\x89PNG\r\n\x1a\n"
JPEG_SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}

# Jev nằm ngoài máy: che secret và email, rút gọn chuỗi mã hoá dài trước khi gửi.
SECRET_PATTERNS = [
    (re.compile(r"(define\(\s*['\"][A-Z_]*(?:KEY|SALT|PASSWORD|PASS|SECRET|TOKEN|USER|NAME|HOST)[A-Z_]*['\"]\s*,\s*)(['\"]).*?\2", re.I),
     r"\1'<redacted>'"),
    (re.compile(r"((?:api[_-]?key|secret|token|passw(?:or)?d|pwd|auth[_-]?key)['\"]?\s*(?:=>|=|:)\s*)(['\"])[^'\"]{6,}\2", re.I),
     r"\1'<redacted>'"),
    (re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}"), "<redacted-key>"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "<redacted-jwt>"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<email>"),
]
BLOB = re.compile(r"[A-Za-z0-9+/=]{160,}|(?:\\x[0-9a-fA-F]{2}){50,}|[0-9a-fA-F]{160,}")


def redact(value):
    if isinstance(value, str):
        for pattern, repl in SECRET_PATTERNS:
            value = pattern.sub(repl, value)
        return BLOB.sub(lambda m: m.group(0)[:60] + f"...<encoded blob, {len(m.group(0))} chars>", value)
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    return value


def sniff_image(data):
    """Trả (mime, rộng, cao) theo nội dung file; None nếu không phải PNG hoặc JPEG đọc được."""
    if data[:8] == PNG_SIG and data[12:16] == b"IHDR" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return "image/png", w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0xFF:
                i += 1
            elif marker == 0x01 or 0xD0 <= marker <= 0xD9:
                i += 2
            elif marker in JPEG_SOF:
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return "image/jpeg", w, h
            else:
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def _get_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None


def _png_chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def _pad_png_stdlib(data, nw, nh):
    """Đệm nền trắng cho PNG không cần Pillow. Nhận PNG 8 hoặc 16 bit, không interlace, không bảng màu."""
    pos, idat, ihdr = 8, [], None
    while pos + 8 <= len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            ihdr = body
        elif kind == b"IDAT":
            idat.append(body)
        pos += 12 + n
    if ihdr is None or not idat:
        raise ValueError("image_unreadable")
    w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", ihdr)
    if interlace or ctype not in (0, 2, 4, 6) or depth not in (8, 16):
        raise ValueError("image_pad_unsupported")
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype] * depth // 8
    stride = w * bpp
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error:
        raise ValueError("image_unreadable") from None
    if len(raw) != h * (stride + 1):
        raise ValueError("image_unreadable")
    rows, prev = [], bytearray(stride)
    for y in range(h):
        ftype = raw[y * (stride + 1)]
        cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = cur[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ftype == 1:
                cur[x] = (cur[x] + a) & 255
            elif ftype == 2:
                cur[x] = (cur[x] + b) & 255
            elif ftype == 3:
                cur[x] = (cur[x] + ((a + b) >> 1)) & 255
            elif ftype == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                cur[x] = (cur[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            elif ftype != 0:
                raise ValueError("image_unreadable")
        rows.append(bytes(cur))
        prev = cur
    white = b"\xff" * bpp
    x0, y0 = (nw - w) // 2, (nh - h) // 2
    blank = b"\x00" + white * nw
    out = [blank] * y0
    out += [b"\x00" + white * x0 + r + white * (nw - w - x0) for r in rows]
    out += [blank] * (nh - h - y0)
    head = struct.pack(">IIBBBBB", nw, nh, depth, ctype, 0, 0, 0)
    return (PNG_SIG + _png_chunk(b"IHDR", head)
            + _png_chunk(b"IDAT", zlib.compress(b"".join(out), 6)) + _png_chunk(b"IEND", b""))


def _pad_pillow(Image, data, nw, nh):
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info else "RGB")
    except Exception:
        raise ValueError("image_unreadable") from None
    canvas = Image.new(im.mode, (nw, nh), (255,) * len(im.mode))
    canvas.paste(im, ((nw - im.width) // 2, (nh - im.height) // 2))
    buf = io.BytesIO()
    canvas.save(buf, "PNG")
    return buf.getvalue()


def pad_image(data, min_side=MIN_IMAGE_SIDE):
    """Trả (mime, bytes). Cạnh ngắn dưới min_side thì đệm nền trắng ở giữa để cả hai cạnh đạt tối thiểu min_side."""
    info = sniff_image(data)
    if info is None:
        raise ValueError("image_unreadable")
    mime, w, h = info
    if w < 1 or h < 1:
        raise ValueError("image_unreadable")
    if min(w, h) >= min_side:
        return mime, data
    nw, nh = max(w, min_side), max(h, min_side)
    Image = _get_pil()
    if Image is not None:
        return "image/png", _pad_pillow(Image, data, nw, nh)
    if mime == "image/png":
        return "image/png", _pad_png_stdlib(data, nw, nh)
    raise ValueError("image_pad_needs_pillow")  # JPEG nhỏ cần Pillow; chạy bằng python có Pillow hoặc đổi sang PNG


def collect_image_paths(value, out):
    if isinstance(value, list):
        for v in value:
            collect_image_paths(v, out)
    elif isinstance(value, dict):
        if set(value) == {"image_path"}:
            out.append(value["image_path"])
        else:
            for v in value.values():
                collect_image_paths(v, out)
    return out


def check_images(items, base, min_side=MIN_IMAGE_SIDE):
    """Kiểm mọi ảnh trước khi gọi API. Trả (lỗi {id: [(đường dẫn, mã)]}, số ảnh, số ảnh cần đệm)."""
    problems, total, to_pad = {}, 0, 0
    for item in items:
        for rel in collect_image_paths(item.get("state"), []):
            total += 1
            path = base / rel
            code = None
            if not path.is_file():
                code = "image_not_found"
            elif path.suffix.lower() not in IMAGE_MIME:
                code = "unsupported_image"
            else:
                try:
                    info = sniff_image(path.read_bytes())
                except OSError:
                    info = None
                if info is None:
                    code = "image_unreadable"
                elif min(info[1], info[2]) < min_side:
                    to_pad += 1
            if code:
                problems.setdefault(item.get("id"), []).append((str(rel), code))
    return problems, total, to_pad


def load_images(value, base, min_side=MIN_IMAGE_SIDE):
    """Đổi {"image_path": ...} thành phần ảnh base64 của Decisions API. Chạy sau redact để không cắt dữ liệu ảnh."""
    if isinstance(value, list):
        return [load_images(v, base, min_side) for v in value]
    if isinstance(value, dict):
        if set(value) == {"image_path"}:
            path = base / value["image_path"]
            if path.suffix.lower() not in IMAGE_MIME:
                raise ValueError("unsupported_image")
            try:
                raw = path.read_bytes()
            except FileNotFoundError:
                raise ValueError("image_not_found") from None
            except OSError:
                raise ValueError("image_unreadable") from None
            mime, raw = pad_image(raw, min_side)
            return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64.b64encode(raw).decode()}"}}
        return {k: load_images(v, base, min_side) for k, v in value.items()}
    return value


def load_key():
    """Biến môi trường trước, rồi .agent-secrets/.env tìm ngược từ thư mục chạy và thư mục script."""
    if os.environ.get(KEY_NAME):
        return os.environ[KEY_NAME]
    seen = set()
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            env = d / ".agent-secrets" / ".env"
            if env in seen or not env.is_file():
                continue
            seen.add(env)
            for line in env.read_text(encoding="utf-8").splitlines():
                m = re.match(rf"^\s*(?:export\s+)?{KEY_NAME}\s*=\s*['\"]?([^'\"\s]+)", line)
                if m:
                    return m.group(1)
    sys.exit(f"thiếu {KEY_NAME}: đặt biến môi trường hoặc thêm vào .agent-secrets/.env của repo")


def finite01(x):
    return type(x) in (int, float) and math.isfinite(x) and 0 <= x <= 1


def check_answers(payload, questions):
    if not str(payload.get("model", "")).startswith(MODEL):
        raise ValueError("unexpected_model")
    answers = payload.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise ValueError("invalid_answers")
    out = {}
    for name, q in questions.items():
        a = answers[name]
        if a.get("type") != q["type"]:
            raise ValueError("invalid_answer_type")
        if q["type"] == "noul":
            if not finite01(a.get("noul")):
                raise ValueError("invalid_noul")
            out[name] = {"p_yes": a["noul"]}
        elif q["type"] == "choice":
            if a.get("choice") not in q["criteria"] or not finite01(a.get("confidence")):
                raise ValueError("invalid_choice")
            out[name] = {"choice": a["choice"], "confidence": a["confidence"],
                         "probabilities": a.get("probabilities", {})}
        elif q["type"] == "score":
            levels = len(q["criteria"]) - 1
            s = a.get("score")
            if type(s) not in (int, float) or not 0 <= s <= levels:
                raise ValueError("invalid_score")
            # Quy về thang 0-1 để mọi rubric so được với nhau.
            out[name] = {"score": round(s / levels, 3), "confidence": a.get("confidence")}
        elif q["type"] == "box":
            # Cạnh hộp là tỉ lệ theo chiều rộng, chiều cao ảnh. Box luôn trả hộp, kể cả khi không có mục tiêu.
            b = a.get("box") or {}
            if not all(finite01(b.get(k)) for k in ("top", "bottom", "left", "right")):
                raise ValueError("invalid_box")
            out[name] = {"box": {k: b[k] for k in ("top", "bottom", "left", "right")}, "confidence": a.get("confidence")}
        else:
            raise ValueError("unsupported_type")
    return out


def call(key, state, questions, timeout=30):
    body = json.dumps({"model": MODEL, "state": state, "questions": questions},
                      ensure_ascii=False, allow_nan=False).encode("utf-8")
    has_image = b'"image_url"' in body
    if len(body) > (MAX_IMAGE_BODY_BYTES if has_image else MAX_BODY_BYTES):
        raise ValueError("request_too_large")
    if has_image:
        timeout = max(timeout, 90)  # request có ảnh chạy chế độ ngữ cảnh dài, chậm hơn
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read(512_000))
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()
            if code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 + attempt * 3)
                continue
            raise ValueError(f"http_{code}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < 2:
                time.sleep(2 + attempt * 3)
                continue
            raise ValueError("network_error") from None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True, type=Path)
    ap.add_argument("--in", dest="inp", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="file JSONL kết quả (bắt buộc trừ khi dùng --dry-run hoặc --preflight-only)")
    ap.add_argument("--budget", type=float, default=0.5, help="trần chi phí USD cho một lượt chạy")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-consecutive-errors", type=int, default=MAX_CONSECUTIVE_ERRORS,
                    help="dừng khi số lỗi API liên tiếp đạt ngưỡng này; 0 là tắt. Lỗi 401, 402, 403 dừng ngay")
    ap.add_argument("--min-image-side", type=int, default=MIN_IMAGE_SIDE,
                    help="cạnh ngắn tối thiểu của ảnh gửi đi, px; ảnh nhỏ hơn được đệm nền trắng")
    ap.add_argument("--dry-run", action="store_true", help="kiểm input và ảnh, không gọi API, không ghi file")
    ap.add_argument("--preflight-only", action="store_true", help="kiểm key, thử 1 mẫu thật rồi dừng, không ghi file")
    ap.add_argument("--no-preflight", action="store_true", help="bỏ bước thử 1 mẫu trước lượt chạy (không khuyến nghị)")
    args = ap.parse_args(argv)
    if not (args.dry_run or args.preflight_only or args.out):
        ap.error("thiếu --out")

    task = json.loads(args.task.read_text(encoding="utf-8"))
    items = [json.loads(l) for l in args.inp.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not items:
        print("Dừng: file input không có dòng nào.", file=sys.stderr)
        return 2
    blocked = {k for i in items for k in task.get("must_be_empty", []) if i["state"].get(k)}
    if blocked:
        print(f"Dừng: trường {sorted(blocked)} phải rỗng. Dữ liệu GSC chỉ xử lý local, không gửi Jev.", file=sys.stderr)
        return 2
    problems, n_images, n_pad = check_images(items, args.inp.parent, args.min_image_side)
    if problems:
        print(f"Dừng: {len(problems)} dòng có ảnh thiếu hoặc hỏng, chưa gọi API. Sửa input rồi chạy lại.", file=sys.stderr)
        for item_id, errs in list(problems.items())[:10]:
            for rel, code in errs:
                print(f"  {item_id}: {code}: {rel}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"dry-run: {len(items)} dòng, {n_images} ảnh, {n_pad} ảnh sẽ đệm lên cạnh ngắn {args.min_image_side} px. "
              "Không gọi API, không ghi file.", file=sys.stderr)
        return 0
    try:
        key = load_key()
    except SystemExit as e:
        print(f"Dừng: {e.code}", file=sys.stderr)
        return 3

    spent = [0.0]
    consecutive = [0]
    abort = [None]
    lock = threading.Lock()

    def run(item):
        with lock:
            if abort[0]:
                return {"id": item["id"], "error": "aborted_consecutive_errors", "route": "review"}
            if spent[0] >= args.budget:
                return {"id": item["id"], "error": "budget_reached", "route": "review"}
        questions = json.loads(json.dumps(task["questions"]))
        for name, crit in (item.get("criteria") or {}).items():
            questions[name]["criteria"] = crit
        started = time.monotonic()
        try:
            payload = call(key, load_images(redact(item["state"]), args.inp.parent, args.min_image_side), questions)
            answers = check_answers(payload, questions)
        except ValueError as e:
            code = str(e)
            if code not in ITEM_ERRORS:
                with lock:
                    consecutive[0] += 1
                    limit = args.max_consecutive_errors
                    if abort[0] is None and (code in AUTH_FATAL or (limit and consecutive[0] >= limit)):
                        abort[0] = code
            return {"id": item["id"], "error": code, "route": "review"}
        cost = (payload.get("usage") or {}).get("cost") or 0
        with lock:
            spent[0] += cost if finite01(cost) else 0
            consecutive[0] = 0
        return {"id": item["id"], "answers": answers, "model": payload["model"],
                "task": task["name"], "task_version": task["version"],
                "latency_ms": round((time.monotonic() - started) * 1000), "cost": cost}

    # Thử mẫu trước: key hết hạn hoặc request sai chặn lượt chạy ngay, không đốt cả lô.
    first_results = []
    if not args.no_preflight or args.preflight_only:
        for item in items[:3]:
            r = run(item)
            first_results.append(r)
            if "error" not in r:
                break
            if r["error"] in ITEM_ERRORS:
                continue  # lỗi riêng của dòng này, thử dòng kế
            print(f"Dừng: mẫu thử {r['id']} lỗi {r['error']}. Chưa chạy phần còn lại.", file=sys.stderr)
            return 3
        else:
            print("Dừng: 3 mẫu thử đầu đều lỗi riêng của dòng, kiểm input.", file=sys.stderr)
            return 3
        print(f"preflight đạt: mẫu {first_results[-1]['id']}, chi phí {spent[0]:.5f} USD.", file=sys.stderr)
        if args.preflight_only:
            return 0

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = first_results + list(ex.map(run, items[len(first_results):]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    errors = sum(1 for r in results if "error" in r)
    print(f"{len(results)} dòng, lỗi {errors}, chi phí {spent[0]:.5f} USD -> {args.out}", file=sys.stderr)
    if abort[0]:
        skipped = sum(1 for r in results if r.get("error") == "aborted_consecutive_errors")
        print(f"Dừng sớm: lỗi {abort[0]} (ngưỡng {args.max_consecutive_errors} lỗi API liên tiếp, 401/402/403 dừng ngay). "
              f"{skipped} dòng chưa gọi, đánh dấu aborted_consecutive_errors. Sửa nguyên nhân rồi chạy lại các dòng lỗi.",
              file=sys.stderr)
        return 3
    return 1 if errors == len(results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
