#!/usr/bin/env python3
"""Trích câu nguyên văn hàng loạt bằng GLM Flash qua OpenRouter, cho việc Jev không làm được.

Dùng: /usr/bin/python3 -I glm.py --task tasks/<tên>.json --in items.jsonl --out ket-qua.jsonl [--budget 0.3]
Task: {"name", "version", "instructions", "source": "<trường trong state chứa văn bản nguồn>"}.
Mỗi dòng input: {"id": "...", "state": {...}}. Model trả {"quotes": [{"text": "<câu nguyên văn>", "tag": "<nhãn ngắn>"}]}.
Script chỉ giữ câu có nguyên văn trong state[source] (so sau khi gộp khoảng trắng); câu không khớp bị bỏ và đếm ở "dropped".
GLM không viết content, không chấm điểm: chỉ trích. Dữ liệu gửi đi theo luật của jev.py (che secret và email).
"""
import argparse
import concurrent.futures as cf
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev  # noqa: E402  (redact, load_key cùng thư mục)

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "z-ai/glm-5.3-flash"
MAX_BODY_BYTES = 120_000


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", s or "")).strip().casefold()


def call(key, task, state, timeout=60):
    system = (task["instructions"] + "\nReturn only JSON: {\"quotes\": [{\"text\": \"...\", \"tag\": \"...\"}]}. "
              "Copy each text exactly from the source, as one sentence or one table cell. Return {\"quotes\": []} if nothing fits.")
    body = json.dumps({"model": MODEL, "temperature": 0, "response_format": {"type": "json_object"},
                       "usage": {"include": True},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": json.dumps(state, ensure_ascii=False)}]},
                      ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_BODY_BYTES:
        raise ValueError("request_too_large")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read(1_000_000))
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


def parse(payload, source):
    if not str(payload.get("model", "")).startswith(MODEL.split("/")[0]):
        raise ValueError("unexpected_model")
    text = ((payload.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    m = re.search(r"\{.*\}", text, re.S)
    try:
        quotes = json.loads(m.group(0)).get("quotes") if m else None
    except json.JSONDecodeError:
        quotes = None
    if not isinstance(quotes, list):
        raise ValueError("invalid_json")
    src = norm(source)
    kept, dropped = [], 0
    for q in quotes:
        t = (q or {}).get("text") if isinstance(q, dict) else None
        if isinstance(t, str) and len(norm(t)) >= 8 and norm(t) in src:
            kept.append({"text": t.strip(), "tag": str(q.get("tag") or "")[:40]})
        else:
            dropped += 1
    return kept, dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True, type=Path)
    ap.add_argument("--in", dest="inp", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--budget", type=float, default=0.3, help="trần chi phí USD cho một lượt chạy")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    task = json.loads(args.task.read_text(encoding="utf-8"))
    items = [json.loads(l) for l in args.inp.read_text(encoding="utf-8").splitlines() if l.strip()]
    jev.KEY_NAME = "OPENROUTER_API_KEY"
    key = jev.load_key()
    spent = [0.0]
    lock = threading.Lock()

    def run(item):
        with lock:
            if spent[0] >= args.budget:
                return {"id": item["id"], "error": "budget_reached", "route": "review"}
        state = jev.redact(item["state"])
        started = time.monotonic()
        try:
            payload = call(key, task, state)
            quotes, dropped = parse(payload, state.get(task["source"], ""))
        except ValueError as e:
            return {"id": item["id"], "error": str(e), "route": "review"}
        cost = (payload.get("usage") or {}).get("cost") or 0
        with lock:
            spent[0] += cost if isinstance(cost, (int, float)) else 0
        return {"id": item["id"], "quotes": quotes, "dropped": dropped, "model": payload.get("model"),
                "task": task["name"], "task_version": task["version"],
                "latency_ms": round((time.monotonic() - started) * 1000), "cost": cost}

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(run, items))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    errors = sum(1 for r in results if "error" in r)
    dropped = sum(r.get("dropped", 0) for r in results)
    print(f"{len(results)} dòng, lỗi {errors}, câu bị bỏ vì không khớp nguồn {dropped}, chi phí {spent[0]:.5f} USD -> {args.out}",
          file=sys.stderr)
    return 1 if errors == len(results) and results else 0


if __name__ == "__main__":
    raise SystemExit(main())
