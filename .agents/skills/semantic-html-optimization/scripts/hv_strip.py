import json
import sys

raw = sys.stdin.read()
for f in json.loads(raw) if raw.strip() else []:
    fid = f["filePath"].rsplit("/", 1)[-1].removesuffix(".html")
    for m in f["messages"]:
        print(json.dumps({"id": fid, "rule": m.get("ruleId"), "sev": m.get("severity"), "sel": m.get("selector"),
                          "msg": m.get("message", "")[:200]}, ensure_ascii=False))
