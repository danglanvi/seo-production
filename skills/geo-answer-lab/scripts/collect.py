#!/usr/bin/env python3
"""Thu câu trả lời AI có web search qua OpenRouter: mỗi prompt × engine × lần chạy một dòng trong raw.jsonl.

Dùng: /usr/bin/python3 -I collect.py --prompts prompts.tsv --out raw.jsonl [--runs 3] [--engines chatgpt,perplexity,gemini]
prompts.tsv: cột id, funnel, branded, topic, prompt (tab). Chạy lại thì bỏ qua lượt đã có ok=true.
Model engine đổi theo thời gian: sửa ENGINES hoặc truyền --engine-models '{"chatgpt": "<model>"}'. Ghi ngày và model vào từng dòng.
Chi phí: khoảng 0,01–0,03 USD mỗi lượt; --budget chặn tổng.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KEY_NAME = "OPENROUTER_API_KEY"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
# engine: (model, web search, tham số thêm). "builtin" = model tự tìm web, không cần plugin.
ENGINES = {"chatgpt": ("openai/gpt-6.1-sol", "native", {"reasoning": {"effort": "low"}}),
           "perplexity": ("perplexity/sonar", "builtin", {}),
           "gemini": ("google/gemini-3.8-flash", "native", {})}


def load_key():
    """Biến môi trường trước, rồi .agent-secrets/.env tìm ngược từ thư mục chạy và thư mục script."""
    if os.environ.get(KEY_NAME):
        return os.environ[KEY_NAME]
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            env = d / ".agent-secrets" / ".env"
            if env.is_file():
                for line in env.read_text(encoding="utf-8").splitlines():
                    m = re.match(rf"^\s*(?:export\s+)?{KEY_NAME}\s*=\s*['\"]?([^'\"\s]+)", line)
                    if m:
                        return m.group(1)
    sys.exit(f"thiếu {KEY_NAME}: đặt biến môi trường hoặc thêm vào .agent-secrets/.env")


def call(key, model, search, prompt, extra, timeout=180):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "usage": {"include": True}, **extra}
    if search != "builtin":
        body["plugins"] = [{"id": "web", "engine": search}]
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "X-Title": "geo-answer-lab"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--engines", default=",".join(ENGINES))
    ap.add_argument("--engine-models", default="{}", help="JSON đổi model theo engine")
    ap.add_argument("--budget", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    engines = {e: ENGINES[e] for e in a.engines.split(",")}
    for e, m in json.loads(a.engine_models).items():
        engines[e] = (m, *engines[e][1:])
    prompts = list(csv.DictReader(a.prompts.open(encoding="utf-8"), delimiter="\t"))
    done = set()
    if a.out.exists():
        for l in a.out.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            if r.get("ok"):
                done.add((r["prompt_id"], r["engine"], r["run"]))
    jobs = [(p, e, k) for p in prompts for e in engines for k in range(1, a.runs + 1) if (p["id"], e, k) not in done]
    print(f"collect: {len(jobs)} lượt cần chạy", file=sys.stderr)
    key = load_key()
    spent = [0.0]

    def work(job):
        p, e, k = job
        model, search, extra = engines[e]
        rec = {"prompt_id": p["id"], "engine": e, "run": k, "model": model, "date": time.strftime("%Y-%m-%d %H:%M"),
               "env": f"OpenRouter API, web search {search}"}
        if spent[0] >= a.budget:
            return {**rec, "ok": False, "error": "budget_reached"}
        for attempt in range(3):
            try:
                d = call(key, model, search, p["prompt"], extra)
                msg = d["choices"][0]["message"]
                cost = (d.get("usage") or {}).get("cost") or 0
                spent[0] += cost
                return {**rec, "ok": True, "response_id": d.get("id"), "model_served": d.get("model"), "cost": cost,
                        "answer": msg.get("content") or "",
                        "citations": [{"url": (c.get("url_citation") or {}).get("url"),
                                       "title": (c.get("url_citation") or {}).get("title")}
                                      for c in (msg.get("annotations") or []) if c.get("type") == "url_citation"]}
            except Exception as x:  # lỗi mạng/HTTP: thử lại, rồi ghi lỗi để lượt sau chạy tiếp
                err = f"http_{x.code}" if isinstance(x, urllib.error.HTTPError) else type(x).__name__
                rec.update(ok=False, error=err)
                time.sleep(5 * (attempt + 1))
        return rec

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as ex, a.out.open("a", encoding="utf-8") as f:
        for rec in ex.map(work, jobs):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
    print(f"collect: xong, chi phí {spent[0]:.3f} USD -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
