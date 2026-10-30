#!/usr/bin/env python3
"""GTM API v2 cho một container. Token OAuth đọc từ file JSON 0600 (khoá access_token) ở biến GTM_TOKEN_FILE; không in token.

  gtm_api.py inventory   --container GTM-XXXX --backup-dir <thư mục>   chỉ đọc: lưu live version ra JSON, in tag/trigger/biến
  gtm_api.py preview-url --container GTM-XXXX --workspace <id>         quick_preview, ghi URL gtm.js preview (có gtm_auth) vào file 0600 cạnh token
  gtm_api.py version     --container GTM-XXXX --workspace <id> --name <tên> [--notes <ghi chú>]   tạo version, in versionId
  gtm_api.py publish     --container GTM-XXXX --version <id>           publish. Chỉ chạy khi người duyệt đã cho áp
"""
import argparse, datetime, json, os, sys, time, urllib.error, urllib.request

BASE = "https://tagmanager.googleapis.com/tagmanager/v2/"


def call(path, method="GET", body=None, soft=False):
    token = json.load(open(os.environ["GTM_TOKEN_FILE"]))["access_token"]
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    for attempt in range(6):
        time.sleep(4.5)  # quota GTM API mặc định khoảng 15 lượt mỗi phút mỗi user
        try:
            return json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                time.sleep(20 * (attempt + 1))
                continue
            err = e
            break
    msg = "HTTP %s %s: %s" % (err.code, path.split("?")[0], err.read().decode()[:600])
    if soft:
        print(msg)
        return {}
    sys.exit(msg)


def find_container(public_id):
    c = call("accounts/containers:lookup?tagId=" + public_id, soft=True)
    if c.get("path"):
        return c
    for acc in call("accounts").get("account", []):
        for c in call(acc["path"] + "/containers").get("container", []):
            if c.get("publicId") == public_id:
                return c
    sys.exit("không thấy container " + public_id)


def summarize(v):
    out = []
    for t in v.get("tag", []):
        params = {p["key"]: p.get("value", p.get("list", p.get("map"))) for p in t.get("parameter", [])}
        out.append("TAG  %-38s type=%-10s firing=%s blocking=%s paused=%s %s" % (t["name"], t["type"], t.get("firingTriggerId"), t.get("blockingTriggerId"), t.get("paused", False), json.dumps({k: params[k] for k in list(params)[:6]}, ensure_ascii=False)[:300]))
    for tr in v.get("trigger", []):
        out.append("TRIG %-38s id=%s type=%s filter=%s %s" % (tr["name"], tr["triggerId"], tr["type"], json.dumps(tr.get("filter", []), ensure_ascii=False)[:200], json.dumps(tr.get("customEventFilter", []), ensure_ascii=False)[:160]))
    for va in v.get("variable", []):
        out.append("VAR  %-38s type=%s %s" % (va["name"], va["type"], json.dumps(va.get("parameter", []), ensure_ascii=False)[:200]))
    out.append("BUILTIN " + ", ".join(b["name"] for b in v.get("builtInVariable", [])))
    return out


def inventory(a):
    c = find_container(a.container)
    live = call(c["path"] + "/versions:live")
    os.makedirs(a.backup_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    path = os.path.join(a.backup_dir, "gtm_%s_live_v%s_%s.json" % (a.container, live.get("containerVersionId"), stamp))
    json.dump(live, open(path, "w"), ensure_ascii=False, indent=1)
    print("container:", c.get("name"), c["path"], "| live version:", live.get("containerVersionId"), live.get("name", ""), "| backup:", path.replace(os.path.expanduser("~"), "~"))
    print("workspaces:", [(w["workspaceId"], w["name"]) for w in call(c["path"] + "/workspaces").get("workspace", [])])
    print("\n".join(summarize(live)))


def preview_url(a):
    c = find_container(a.container)
    ws = c["path"] + "/workspaces/" + a.workspace
    qp = call(ws + ":quick_preview", "POST", soft=True)
    print("quick_preview compilerError:", qp.get("compilerError", False))
    for e in call(c["path"] + "/environments").get("environment", []):
        if e.get("type") == "workspace" and e.get("workspaceId") == a.workspace:
            out = os.path.join(os.path.dirname(os.environ["GTM_TOKEN_FILE"]), ".preview-url")  # gtm_auth là khoá xem preview: để ngoài repo
            fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            os.write(fd, ("https://www.googletagmanager.com/gtm.js?id=%s&gtm_auth=%s&gtm_preview=env-%s&gtm_cookies_win=x" % (a.container, e["authorizationCode"], e["environmentId"])).encode())
            os.close(fd)
            print("môi trường preview env-%s, URL ghi vào %s (0600)" % (e["environmentId"], out.replace(os.path.expanduser("~"), "~")))
            return
    sys.exit("không thấy môi trường preview của workspace " + a.workspace)


def version(a):
    c = find_container(a.container)
    r = call(c["path"] + "/workspaces/" + a.workspace + ":create_version", "POST", {"name": a.name, "notes": a.notes or ""})
    v = r.get("containerVersion", {})
    print("compilerError:", r.get("compilerError", False), "| versionId:", v.get("containerVersionId"), "| tag:", len(v.get("tag", [])), "| trigger:", len(v.get("trigger", [])), "| biến:", len(v.get("variable", [])))


def publish(a):
    c = find_container(a.container)
    r = call(c["path"] + "/versions/" + a.version + ":publish", "POST")
    print("compilerError:", r.get("compilerError", False), "| live version:", r.get("containerVersion", {}).get("containerVersionId"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["inventory", "preview-url", "version", "publish"])
    ap.add_argument("--container", required=True)
    ap.add_argument("--backup-dir")
    ap.add_argument("--workspace")
    ap.add_argument("--name")
    ap.add_argument("--notes")
    ap.add_argument("--version")
    a = ap.parse_args()
    need = {"inventory": ["backup_dir"], "preview-url": ["workspace"], "version": ["workspace", "name"], "publish": ["version"]}[a.cmd]
    miss = [k for k in need if not getattr(a, k)]
    if miss:
        ap.error("thiếu --" + ", --".join(k.replace("_", "-") for k in miss))
    if not os.environ.get("GTM_TOKEN_FILE"):
        sys.exit("thiếu biến GTM_TOKEN_FILE")
    {"inventory": inventory, "preview-url": preview_url, "version": version, "publish": publish}[a.cmd](a)
