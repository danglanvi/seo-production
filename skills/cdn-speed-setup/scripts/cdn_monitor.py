# Giám sát CDN chia vùng (nhánh B) mỗi 5 phút bằng launchd. Chỉ báo, không tự trả DNS.
# Mỗi vòng: DNS qua 3 resolver, NS Cloudflare của zone (làm phẳng CNAME), NS của CDN, HTTP thẳng origin,
# HTTP qua trạm CDN vùng xa (trang chủ có cache, và URL có query đi xuyên tới origin).
# Mỗi giờ: Globalping từ Mỹ và VN; tài khoản CDN. Mỗi ngày: chứng chỉ trên CDN, tin "vẫn chạy".
# Mọi kiểm bọc lỗi riêng: một kiểm hỏng không làm mất cảnh báo của kiểm khác. Không ghi IP, token, chat ID.
#   python3 cdn_monitor.py run --config site.json [--dry]      một vòng (launchd gọi); --dry không ghi trạng thái, in tin thay vì gửi
#   python3 cdn_monitor.py test-alert --config site.json       gửi một tin thử
#   python3 cdn_monitor.py status --config site.json           trạng thái và 5 vòng gần nhất
#   python3 cdn_monitor.py install|uninstall --config site.json [--apply]
import argparse
import copy
import datetime as dt
import fcntl
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdn import _call, bn, classify, globalping, mask, secret  # noqa: E402

DEFAULTS = {"path": "/", "probe_query": "cdn-monitor=1", "resolvers": ["sys", "1.1.1.1", "8.8.8.8"],
            "resolver_labels": {"sys": "hệ thống", "1.1.1.1": "cloudflare", "8.8.8.8": "google"},
            "cf_ns": [], "ecs_far": "8.8.8.0/24", "interval_s": 300, "fail_after": 2, "window_fail": 3, "recover_after": 2,
            "repeat_min": 120, "gap_min": 15, "globalping_every_min": 60, "globalping_min_quota": 30,
            "globalping_far": [{"magic": "Ashburn"}, {"magic": "Dallas"}, {"magic": "Los Angeles"}, {"magic": "Chicago"}, {"magic": "New York"}],
            "globalping_vn": {"country": "VN", "limit": 6},
            "confirm_far": [{"magic": "Chicago"}, {"magic": "Ashburn"}, {"magic": "Dallas"}], "acct_every_min": 60, "trial_warn_days": 3, "min_balance_usd": 3,
            "cert_warn_days": 30, "heartbeat_hour": 8, "cdn_server_re": "bunny", "bunny_billing": False}
CRIT = {"dns_mat", "flatten_loi", "ns_cdn", "origin_http", "cdn_http", "cdn_origin", "cdn_taikhoan"}
UNSWITCH = {"dns_mat", "flatten_loi", "ns_cdn", "cdn_http", "cdn_origin", "cdn_taikhoan"}
REPEAT_MIN = {"cdn_tien": 24 * 60, "cert_cdn": 24 * 60, "cdn_api": 6 * 60, "giam_sat_loi": 60}
SUPPRESS = {"ns_cdn_mot": "ns_cdn", "dns_mot": "dns_mat"}
TEN = {"dns_mat": "domain mất phân giải ở VN", "dns_mot": "một resolver không phân giải được domain",
       "vn_lech": "khách VN nhận IP CDN (đi vòng)", "flatten_loi": "NS Cloudflare không trả IP cho apex (lỗi làm phẳng CNAME)",
       "ns_cdn": "NS của CDN không trả lời", "ns_cdn_mot": "một NS của CDN không trả lời",
       "origin_http": "origin không trả 200", "cdn_http": "trang chủ qua CDN vùng xa lỗi",
       "cdn_origin": "CDN không lấy được trang từ origin", "xa_nhan_origin": "vùng xa nhận IP origin (Googlebot không qua CDN)",
       "vn_lech_gp": "probe VN (Globalping) nhận IP CDN", "cdn_taikhoan": "tài khoản CDN bị khoá",
       "cdn_api": "không đọc được tài khoản CDN qua API", "cdn_tien": "tiền CDN sắp cạn",
       "cert_cdn": "chứng chỉ trên CDN sắp hết hạn hoặc lỗi", "giam_sat_loi": "giám sát gặp lỗi nội bộ"}
UA = "cdn-monitor/1.0 (+giam sat CDN, 3 request/5 phut)"
_last_prod = [0.0]


def load_cfg(path):
    cfg = copy.deepcopy(DEFAULTS)
    cfg.update(json.load(open(path, encoding="utf-8")))
    cfg["config_path"] = os.path.abspath(path)
    for k in ("origin_file", "state_dir"):
        cfg[k] = os.path.expanduser(cfg[k])
    cfg["alert_cmd"] = [os.path.expanduser(x) for x in cfg["alert_cmd"]]
    return cfg


def dig(*args):
    try:
        out = subprocess.run(["dig", "+short", "+time=3", "+tries=2", *args], capture_output=True, text=True, timeout=20).stdout
    except (subprocess.TimeoutExpired, OSError):
        return []
    return [x for x in out.split() if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", x)]


def pace():
    # Production: tối đa 1 request/giây. Các request trong vòng chạy tuần tự nên tối đa 1 đồng thời.
    w = 1.1 - (time.time() - _last_prod[0])
    if w > 0:
        time.sleep(w)
    _last_prod[0] = time.time()


def curl(url, domain, ip, prod=True):
    if prod:
        pace()
    args = ["curl", "-s", "-o", "/dev/null", "-D", "-", "-A", UA, "--max-time", "20",
            "-w", "\nCODE=%{http_code} T=%{time_starttransfer}", url]
    if ip:
        args[1:1] = ["--resolve", "%s:443:%s" % (domain, ip)]
    try:
        r = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=30).stdout
    except (subprocess.TimeoutExpired, OSError):
        return {"code": 0, "t": None, "server": ""}
    c = re.search(r"CODE=(\d+) T=(\S+)", r)
    s = re.search(r"(?im)^server:\s*(.+)$", r)
    return {"code": int(c.group(1)) if c else 0, "t": round(float(c.group(2)) * 1000) if c else None,
            "server": s.group(1).strip() if s else ""}


def net_ok():
    # Mạng máy giám sát: đạt khi một trong hai đích HTTP trả lời. Mạng lỗi thì bỏ vòng, không báo.
    if curl("https://www.google.com/generate_204", "", None, prod=False)["code"] == 204:
        return True
    return curl("https://www.cloudflare.com/cdn-cgi/trace", "", None, prod=False)["code"] == 200


def ns_ip(name, cache):
    # Tra IP của NS qua 1.1.1.1 rồi 8.8.8.8, không qua resolver của router nhà.
    if name not in cache:
        ips = dig("@1.1.1.1", name, "A") or dig("@8.8.8.8", name, "A")
        cache[name] = ips[0] if ips else None
    return cache[name]


def cert_days(ip, domain):
    pace()
    ctx = ssl.create_default_context()
    with socket.create_connection((ip, 443), timeout=15) as s:
        with ctx.wrap_socket(s, server_hostname=domain) as t:
            na = t.getpeercert()["notAfter"]
    exp = dt.datetime.strptime(na, "%b %d %H:%M:%S %Y %Z")
    return (exp - dt.datetime.utcnow()).days


def check_round(cfg, origin, errors):
    # Trả ({khoá: (đạt, chi tiết)}, IP trạm CDN). Kiểm nào lỗi nội bộ thì bỏ khoá đó và ghi vào errors.
    res, cache, lab = {}, {}, cfg["resolver_labels"]

    def safe(name, fn):
        try:
            fn()
        except BaseException as e:  # noqa: B902 — gồm cả SystemExit của _cdn.secret
            errors.append("%s: %s" % (name, type(e).__name__))

    def dns():
        cls = {}
        for r in cfg["resolvers"]:
            cls[lab.get(r, r)] = classify(dig(*([] if r == "sys" else ["@" + r]), cfg["domain"], "A"), origin)
        det = ", ".join("%s %s" % kv for kv in cls.items())
        res["dns_mat"] = (any(v != "EMPTY" for v in cls.values()), det)
        res["dns_mot"] = (all(v != "EMPTY" for v in cls.values()), det)
        res["vn_lech"] = (all(v != "CDN" for v in cls.values()), det)

    def flatten():
        if not cfg["cf_ns"]:
            return
        ans = {}
        for n in cfg["cf_ns"]:
            ip = ns_ip(n, cache)
            if ip:
                ans[n] = classify(dig("@" + ip, cfg["domain"], "A"), origin)
        if ans:
            res["flatten_loi"] = (any(v != "EMPTY" for v in ans.values()), ", ".join("%s %s" % kv for kv in ans.items()))

    def ns_cdn():
        ans = {}
        for n in cfg["geo_ns"]:
            ip = ns_ip(n, cache)
            if ip:
                ans[n] = bool(dig("@" + ip, cfg["geo_name"], "A"))
        if ans:
            det = ", ".join("%s %s" % (n, "trả lời" if v else "KHÔNG trả lời") for n, v in ans.items())
            res["ns_cdn"] = (any(ans.values()), det)
            res["ns_cdn_mot"] = (all(ans.values()), det)

    url = "https://%s%s" % (cfg["domain"], cfg["path"])

    def origin_http():
        o = curl(url, cfg["domain"], origin)
        res["origin_http"] = (o["code"] == 200, "mã %s, %s ms" % (o["code"], o["t"]))

    eip = [None]

    def cdn():
        eip[0] = (dig("@8.8.8.8", cfg["cdn_host"], "A", "+subnet=" + cfg["ecs_far"]) or [None])[0]
        if not eip[0]:
            res["cdn_http"] = (False, "không tra được IP trạm CDN của %s" % cfg["cdn_host"])
            return
        for key, u in (("cdn_http", url), ("cdn_origin", url + ("&" if "?" in url else "?") + cfg["probe_query"])):
            e = curl(u, cfg["domain"], eip[0])
            ok = e["code"] == 200 and re.search(cfg["cdn_server_re"], e["server"], re.I) is not None
            res[key] = (ok, "mã %s, %s ms, server %s" % (e["code"], e["t"], e["server"] or "-"))

    for name, fn in (("dns", dns), ("flatten", flatten), ("ns_cdn", ns_cdn), ("origin_http", origin_http), ("cdn", cdn)):
        safe(name, fn)
    return res, eip[0]


def check_globalping(cfg, origin):
    # Trả ({khoá: kết quả}, ghi chú) hoặc (None, ghi chú) khi bỏ qua.
    c, lim = _call("https://api.globalping.io/v1", {}, "GET", "/limits", timeout=20)
    try:
        left = lim["rateLimit"]["measurements"]["create"]["remaining"]
    except Exception:
        left = 0
    need = len(cfg["globalping_far"]) + cfg["globalping_vn"].get("limit", 0)
    if left < max(cfg["globalping_min_quota"], need):
        return None, "bỏ qua: Globalping còn %s probe" % left
    out, notes = {}, []
    for key, locs, bad in (("xa_nhan_origin", cfg["globalping_far"], "ORIGIN"), ("vn_lech_gp", [cfg["globalping_vn"]], "CDN")):
        r = globalping({"type": "dns", "target": cfg["domain"], "locations": locs,
                        "measurementOptions": {"query": {"type": "A"}, "protocol": "UDP", "port": 53}}, wait_s=40)
        rows = []
        for x in r.get("results", []):
            ans = [v.get("value") for v in (x["result"].get("answers") or []) if v.get("type") == "A"]
            rows.append(("%s AS%s" % (x["probe"].get("city"), x["probe"].get("asn")), classify(ans, origin)))
        det = ", ".join("%s %s" % kv for kv in rows)
        if any(cl != "EMPTY" for _, cl in rows):
            # Probe trả rỗng là lỗi của probe, không tính.
            out[key] = (all(cl != bad for _, cl in rows), det)
        else:
            notes.append("%s: không có câu trả lời" % key)
    return (out or None), "; ".join(notes) or "đo xong"


def confirm_far(cfg, keys):
    # Máy giám sát ở VN tới trạm CDN ở Mỹ bằng đường quốc tế. Đường này rớt giờ cao điểm: mã 0, request không tới trạm
    # (log Bunny 01/11/2026 22:30–02/11 01:00, cùng lúc trạm vẫn trả 200 cho Googlebot). Đo lại bằng HTTP từ probe Mỹ.
    # Trả {khoá: chi tiết} cho khoá được đa số probe xác nhận đạt. Thiếu quota hoặc probe lỗi thì giữ kết quả lỗi.
    c, lim = _call("https://api.globalping.io/v1", {}, "GET", "/limits", timeout=20)
    try:
        left = lim["rateLimit"]["measurements"]["create"]["remaining"]
    except Exception:
        left = 0
    if left < len(keys) * len(cfg["confirm_far"]):
        return {}, "bỏ qua: Globalping còn %s probe" % left
    out = {}
    for key in keys:
        req = {"method": "GET", "path": cfg["path"]}
        if key == "cdn_origin":
            req["query"] = cfg["probe_query"]
        r = globalping({"type": "http", "target": cfg["domain"], "locations": cfg["confirm_far"],
                        "measurementOptions": {"request": req, "protocol": "HTTPS", "port": 443}}, wait_s=40)
        oks = []
        for x in r.get("results", []):
            h = {k.lower(): v for k, v in (x["result"].get("headers") or {}).items()}
            oks.append(x["result"].get("statusCode") == 200 and re.search(cfg["cdn_server_re"], str(h.get("server") or ""), re.I) is not None)
        if oks and sum(oks) * 2 > len(oks):
            out[key] = "%d/%d probe Mỹ nhận 200 từ CDN" % (sum(oks), len(oks))
    return out, "đo xong"


def check_account(cfg, now_local):
    c, u = bn("GET", "/user")
    if c != 200 or not isinstance(u, dict) or "Suspended" not in u:
        return {"cdn_api": (False, "HTTP %s%s" % (c, "" if isinstance(u, dict) and "Suspended" in u else ", thiếu trường Suspended"))}
    res = {"cdn_api": (True, "đọc được")}
    days = None
    if u.get("BillingFreeUntilDate"):
        end = dt.datetime.strptime(u["BillingFreeUntilDate"][:19], "%Y-%m-%dT%H:%M:%S")  # UTC
        days = (end - dt.datetime.utcnow()).total_seconds() / 86400
    bal, trial = float(u.get("Balance") or 0), float(u.get("TrialBalance") or 0)
    det = "khoá: %s, số dư %.2f USD, dùng thử còn %s ngày, tín dụng dùng thử %.2f USD" % (
        u["Suspended"], bal, "-" if days is None else "%.1f" % days, trial)
    res["cdn_taikhoan"] = (not u["Suspended"], det)
    if cfg["heartbeat_hour"] <= now_local.hour < 21:  # tin về tiền chỉ gửi ban ngày
        in_trial = days is not None and days > 0 and trial > 0
        low = (in_trial and days <= cfg["trial_warn_days"] and bal < cfg["min_balance_usd"]) or \
              (not in_trial and bal < cfg["min_balance_usd"])
        res["cdn_tien"] = (not low, det)
    return res


def evaluate(state, results, now, cfg, scheduled):
    # Máy trạng thái. Kiểm mỗi vòng: báo khi lỗi fail_after vòng liền hoặc window_fail trong 6 vòng gần nhất; hồi phục khi đạt
    # recover_after vòng liền. Kiểm theo lịch (scheduled): báo ngay lần lỗi đầu, hồi phục ở lần đạt đầu. Hàm thuần để test.
    alerts, recovered = [], []
    checks = state.setdefault("checks", {})
    for key, (ok, det) in results.items():
        st = dict(checks.get(key) or {})
        st.setdefault("fail", 0)
        sched = key in scheduled
        hist = (list(st.get("hist", [])) + [bool(ok)])[-6:]
        if ok:
            st["fail"] = 0
            st["okrun"] = st.get("okrun", 0) + 1
            if st.get("alerted") is not None:
                if sched or st["okrun"] >= cfg["recover_after"]:
                    recovered.append((key, det))
                    st = {"fail": 0, "okrun": st["okrun"]}
                    hist = []
            elif all(hist):
                st.pop("since", None)
        else:
            st["okrun"] = 0
            st["fail"] += 1
            st.setdefault("since", now)
            hit = st["fail"] >= (1 if sched else cfg["fail_after"]) or \
                (not sched and sum(1 for h in hist if not h) >= cfg["window_fail"])
            if hit and (st.get("alerted") is None or now - st["alerted"] >= REPEAT_MIN.get(key, cfg["repeat_min"]) * 60):
                alerts.append((key, det, st["since"]))
                st["alerted"] = now
        st["hist"] = hist
        checks[key] = st
    return alerts, recovered


def revert_unsent(state, prev_checks, alerts, recovered):
    # Gửi tin lỗi: trả các khoá vừa báo hoặc vừa hồi phục về trạng thái cũ để vòng sau gửi lại.
    checks = state["checks"]
    for k, _, _ in alerts:
        old = prev_checks.get(k, {})
        if "alerted" in old:
            checks[k]["alerted"] = old["alerted"]
        else:
            checks[k].pop("alerted", None)
    for k, _ in recovered:
        if k in prev_checks:
            checks[k] = dict(prev_checks[k], hist=checks[k].get("hist", []))


def hhmm(ts):
    return dt.datetime.fromtimestamp(ts).strftime("%d/%m %H:%M")


def compose(cfg, alerts, recovered, now, notes=()):
    lines = []
    keys = {k for k, _, _ in alerts}
    shown = [(k, d, s) for k, d, s in alerts if SUPPRESS.get(k) not in keys]
    if shown:
        crit = any(k in CRIT for k, _, _ in shown)
        lines.append("[CDN %s] %s lúc %s" % (cfg["domain"], "LỖI NGHIÊM TRỌNG" if crit else "Cảnh báo", hhmm(now)))
        for k, det, since in shown:
            lines.append("- %s (từ %s): %s" % (TEN.get(k, k), hhmm(since), det))
        unsw = keys & UNSWITCH
        if "origin_http" in keys:
            unsw -= {"cdn_origin"}  # origin chết thì CDN cũng không lấy được trang: trả DNS không giúp gì
        if unsw:
            lines.append("Trả DNS về origin (khoảng 60 giây): %s" % cfg["unswitch_hint"])
        if "origin_http" in keys and not unsw:
            lines.append("VPS lỗi: kiểm VPS trước. Chưa nên trả DNS, vì CDN còn bản lưu cho khách ngoài châu Á.")
        lines.append("Giám sát chỉ báo, không tự trả DNS.")
    if recovered:
        lines.append("[CDN %s] Đã hồi phục lúc %s: %s" % (cfg["domain"], hhmm(now), "; ".join(TEN.get(k, k) for k, _ in recovered)))
    lines.extend(notes)
    return mask("\n".join(lines)) if lines else ""


def send(cfg, msg, dry):
    if dry:
        print("--- TIN (dry) ---\n" + msg)
        return True
    try:
        r = subprocess.run(cfg["alert_cmd"] + [msg], capture_output=True, text=True, timeout=60)
    except (subprocess.TimeoutExpired, OSError) as e:
        print("gửi tin lỗi: %s" % type(e).__name__, file=sys.stderr)
        return False
    if r.returncode != 0:
        print("gửi tin lỗi, mã %s" % r.returncode, file=sys.stderr)  # không in stderr: có thể chứa token, chat ID
    return r.returncode == 0


def load_state(sp, errors, dry=False):
    if not os.path.exists(sp):
        return {}
    try:
        st = json.load(open(sp))
        if not isinstance(st, dict):
            raise ValueError("không phải object")
        return st
    except (ValueError, OSError) as e:
        if not dry:
            os.replace(sp, sp + ".hong-%s" % time.strftime("%Y%m%d-%H%M%S"))
        errors.append("state.json hỏng (%s), tạo lại" % type(e).__name__)
        return {}


def save_state(sp, state):
    tmp = sp + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, sp)


def heartbeat_msg(cfg, state, today):
    y = (dt.date.fromisoformat(today) - dt.timedelta(days=1)).isoformat()
    c = state.get("counts", {}).get(y)
    exp = 86400 // cfg["interval_s"]
    if c is None:
        return "[CDN %s] Giám sát vẫn chạy. Hôm qua không có số liệu (giám sát mới cài hoặc máy tắt cả ngày)." % cfg["domain"]
    theo_muc = "; ".join("%s %d vòng" % (TEN.get(k, k), n) for k, n in c.get("keys", {}).items())
    dang = [TEN.get(k, k) for k, v in state.get("checks", {}).items() if v.get("fail")]
    ngay_cai = state.get("first_day") == y
    thieu = c["rounds"] < 0.8 * exp and not ngay_cai
    return "[CDN %s] %sHôm qua %d/%d vòng%s (mất mạng %d vòng, gián đoạn %d phút), %d vòng có mục lỗi%s. Đang lỗi: %s." % (
        cfg["domain"], "Cảnh báo: giám sát chạy thiếu vòng. " if thieu else "Giám sát vẫn chạy. ",
        c["rounds"], exp, ", là ngày cài" if ngay_cai else "", c.get("net_down", 0), c.get("gap_min", 0), c["fail_rounds"],
        " (%s)" % theo_muc if theo_muc else "", "; ".join(dang) or "không")


def run(cfg, dry):
    os.umask(0o077)
    os.makedirs(cfg["state_dir"], exist_ok=True)
    os.chdir(os.path.dirname(cfg["config_path"]))  # để _cdn.secret() tìm .agent-secrets/.env khi launchd chạy ở /
    lockf = open(os.path.join(cfg["state_dir"], "lock"), "w")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("vòng trước chưa xong, bỏ vòng này")
        return 0
    sp = os.path.join(cfg["state_dir"], "state.json")
    errors = []
    state = load_state(sp, errors, dry)

    def persist():
        if not dry:
            save_state(sp, state)

    now, nowl = time.time(), dt.datetime.now()
    today = dt.date.today().isoformat()
    state.setdefault("first_day", today)
    day = state.setdefault("counts", {}).setdefault(today, {"rounds": 0, "fail_rounds": 0, "net_down": 0, "gap_min": 0})
    pending = state.setdefault("pending_notes", [])
    log = {"t": nowl.isoformat(timespec="seconds")}
    gap = now - state["last_run"] if state.get("last_run") else 0
    if gap > cfg["gap_min"] * 60:
        # Tin gián đoạn vào hàng chờ, gửi ở vòng đầu có mạng, chỉ xoá khi gửi được.
        pending.append("[CDN %s] Giám sát bị gián đoạn khoảng %d phút (%s đến %s): máy ngủ, tắt hoặc launchd dừng. Không có số liệu trong lúc đó." % (
            cfg["domain"], gap / 60, hhmm(state["last_run"]), hhmm(now)))
        day["gap_min"] = day.get("gap_min", 0) + int(gap / 60)
        for st in state.get("checks", {}).values():
            if st.get("alerted") is None:
                st.update({"fail": 0, "hist": []})
                st.pop("since", None)
    state["last_run"] = now
    if not net_ok():
        log["net"] = False
        state["net_down"] = state.get("net_down", 0) + 1
        day["net_down"] = day.get("net_down", 0) + 1
    else:
        log["net"] = True
        if state.get("net_down", 0) >= 3:
            pending.append("[CDN %s] Mạng của máy giám sát mất khoảng %d phút, đã có lại. Không có số liệu trong lúc đó." % (
                cfg["domain"], state["net_down"] * cfg["interval_s"] / 60))
        state["net_down"] = 0
        del pending[:-5]
        results, scheduled, ip = {}, set(), None
        try:
            origin = open(cfg["origin_file"]).read().strip()
            if not re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", origin):
                raise ValueError("file IP origin không chứa IPv4")
        except (OSError, ValueError) as e:
            origin = None
            errors.append("origin_file: %s" % type(e).__name__)
        if origin:
            r, ip = check_round(cfg, origin, errors)
            results.update(r)
            # Chỉ đo lại lỗi "mã 0" (không có phản hồi). Trạm trả mã lỗi thật thì báo như cũ.
            lost = [k for k in ("cdn_http", "cdn_origin") if k in results and not results[k][0] and results[k][1].startswith("mã 0,")]
            if lost:
                try:
                    conf, note = confirm_far(cfg, lost)
                except BaseException as e:  # noqa: B902
                    conf, note = {}, "lỗi %s" % type(e).__name__
                log["xac_nhan_xa"] = "%s: %s" % (",".join(lost), note)
                for k, d in conf.items():
                    results[k] = (True, "máy giám sát không tới được trạm CDN (%s); %s" % (results[k][1], d))
            if now - state.get("last_gp", 0) >= cfg["globalping_every_min"] * 60:
                try:
                    gr, note = check_globalping(cfg, origin)
                except BaseException as e:  # noqa: B902
                    gr, note = None, "lỗi %s" % type(e).__name__
                log["globalping"] = note
                if gr:
                    results.update(gr)
                    # Vùng xa nhận origin (lỗi mã trạm) báo ngay; probe VN lệch cần 2 lần đo để tránh báo giả.
                    scheduled |= set(gr) & {"xa_nhan_origin"}
                    state["last_gp"] = now
                else:  # bỏ qua hoặc lỗi: thử lại sau 15 phút
                    state["last_gp"] = now - (cfg["globalping_every_min"] - 15) * 60
        retry_acct = now - (cfg["acct_every_min"] - 15) * 60
        if cfg.get("bunny_billing") and now - state.get("last_acct", 0) >= cfg["acct_every_min"] * 60:
            try:
                ar = check_account(cfg, nowl)
            except BaseException as e:  # noqa: B902 — lỗi mạng hay thiếu key đi đường cdn_api, không câm
                ar = {"cdn_api": (False, "lỗi %s" % type(e).__name__)}
            results.update(ar)
            scheduled |= set(ar) - {"cdn_api"}
            state["last_acct"] = now if ar["cdn_api"][0] else retry_acct
        if ip and state.get("last_cert") != today and nowl.hour >= cfg["heartbeat_hour"]:
            try:
                d = cert_days(ip, cfg["domain"])
                results["cert_cdn"] = (d > cfg["cert_warn_days"], "chứng chỉ trên CDN còn %d ngày" % d)
                state["last_cert"] = today
                state.pop("cert_err", None)
            except BaseException as e:  # noqa: B902 — lỗi lần đầu trong ngày thì thử lại vòng sau, lỗi lần hai mới báo
                if state.get("cert_err") == today:
                    results["cert_cdn"] = (False, "lỗi chứng chỉ trên CDN: %s" % type(e).__name__)
                    state["last_cert"] = today
                else:
                    state["cert_err"] = today
            if "cert_cdn" in results:
                scheduled.add("cert_cdn")
        results["giam_sat_loi"] = (not errors, "; ".join(errors) or "không")
        prev = copy.deepcopy(state.get("checks", {}))
        alerts, recovered = evaluate(state, results, now, cfg, scheduled)
        msg = compose(cfg, alerts, recovered, now, list(pending))
        if msg:
            persist()  # ghi trước khi gửi: đĩa lỗi thì vòng chết trước khi gửi, không lặp tin mỗi vòng
            log["sent"] = send(cfg, msg, dry)
            if log["sent"]:
                state["pending_notes"] = []
            else:
                revert_unsent(state, prev, alerts, recovered)
                touched = {k for k, _, _ in alerts} | {k for k, _ in recovered}
                if touched & {"cdn_taikhoan", "cdn_tien", "cdn_api"}:
                    state["last_acct"] = retry_acct
                if "cert_cdn" in touched:
                    state.pop("last_cert", None)
        log["checks"] = {k: [ok, det] for k, (ok, det) in results.items()}
        day["rounds"] += 1
        failed = [k for k, (ok, _) in results.items() if not ok]
        day["fail_rounds"] += int(bool(failed))
        for k in failed:
            day.setdefault("keys", {})[k] = day.get("keys", {}).get(k, 0) + 1
        hb = cfg.get("heartbeat_hour")
        if hb is not None and nowl.hour >= hb and state.get("last_heartbeat") != today:
            old_hb = state.get("last_heartbeat")
            state["last_heartbeat"] = today
            persist()
            if not send(cfg, mask(heartbeat_msg(cfg, state, today)), dry):
                state["last_heartbeat"] = old_hb
    cutoff = (dt.date.today() - dt.timedelta(days=15)).isoformat()
    state["counts"] = {k: v for k, v in state.get("counts", {}).items() if k >= cutoff}
    line = mask(json.dumps(log, ensure_ascii=False))
    if dry:
        print(line)
        return 0
    persist()
    with open(os.path.join(cfg["state_dir"], "log-%s.jsonl" % today[:7]), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    old = (dt.date.today() - dt.timedelta(days=95)).isoformat()[:7]
    for fn in os.listdir(cfg["state_dir"]):
        if re.fullmatch(r"log-\d{4}-\d{2}\.jsonl", fn) and fn[4:11] < old:
            os.remove(os.path.join(cfg["state_dir"], fn))
    print(line)
    return 0


def run_safe(cfg, dry):
    # Lỗi ngoài dự tính: in traceback đã che IP ra stderr, gửi tối đa 1 tin mỗi giờ.
    # Mốc gửi lưu ở state_dir, nếu không ghi được thì ở thư mục tạm, để đĩa lỗi không làm tin lặp mỗi vòng.
    try:
        return run(cfg, dry)
    except BaseException as e:  # noqa: B902
        print(mask(traceback.format_exc())[-3000:], file=sys.stderr)
        paths = [os.path.join(cfg["state_dir"], "loi-noi-bo.json"),
                 os.path.join("/tmp", "cdn-monitor-%s-loi.json" % re.sub(r"[^\w.-]", "_", cfg["label"]))]
        last = 0
        for ep in paths:
            try:
                last = max(last, json.load(open(ep)).get("sent", 0))
            except (ValueError, OSError, AttributeError):
                pass
        if time.time() - last >= 3600 and send(cfg, "[CDN %s] Giám sát lỗi nội bộ (%s). Xem %s/launchd.log." % (
                cfg["domain"], type(e).__name__, cfg["state_dir"]), dry) and not dry:
            for ep in paths:
                try:
                    json.dump({"sent": time.time()}, open(ep, "w"))
                    break
                except OSError:
                    continue
        return 1


def plist(cfg):
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    logp = os.path.join(cfg["state_dir"], "launchd.log")
    args = ["/usr/bin/python3", "-B", os.path.join(HERE, "cdn_monitor.py"), "run", "--config", cfg["config_path"]]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            '<plist version="1.0">\n<dict>\n'
            '\t<key>Label</key><string>%s</string>\n'
            '\t<key>ProgramArguments</key>\n\t<array>%s</array>\n'
            '\t<key>EnvironmentVariables</key>\n\t<dict><key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin:%s</string></dict>\n'
            '\t<key>StartInterval</key><integer>%d</integer>\n'
            '\t<key>RunAtLoad</key><true/>\n'
            '\t<key>StandardOutPath</key><string>/dev/null</string>\n'
            '\t<key>StandardErrorPath</key><string>%s</string>\n'
            '</dict>\n</plist>\n') % (esc(cfg["label"]), "".join("<string>%s</string>" % esc(a) for a in args),
                                     esc(os.path.expanduser("~/.local/bin")), cfg["interval_s"], esc(logp))


def preflight(cfg):
    errs = []
    try:
        ip = open(cfg["origin_file"]).read().strip()
        if not re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", ip):
            errs.append("origin_file không chứa IPv4")
    except OSError:
        errs.append("không đọc được origin_file")
    if not (os.path.isfile(cfg["alert_cmd"][0]) and os.access(cfg["alert_cmd"][0], os.X_OK)):
        errs.append("không chạy được %s" % cfg["alert_cmd"][0])
    if cfg.get("bunny_billing"):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(cfg["config_path"]))
        if not secret("BUNNY_API_KEY", required=False):
            errs.append("không thấy BUNNY_API_KEY")
        os.chdir(cwd)
    for n in list(cfg["geo_ns"]) + list(cfg["cf_ns"]):
        if not ns_ip(n, {}):
            errs.append("không tra được IP của %s" % n)
    try:
        os.makedirs(cfg["state_dir"], exist_ok=True)
        t = os.path.join(cfg["state_dir"], ".ghi-thu")
        open(t, "w").close()
        os.remove(t)
    except OSError:
        errs.append("không ghi được state_dir")
    return errs


def install(cfg, apply, remove=False):
    p = os.path.expanduser("~/Library/LaunchAgents/%s.plist" % cfg["label"])
    dom = "gui/%d" % os.getuid()
    if remove:
        print("sẽ gỡ", p)
        if apply:
            subprocess.run(["launchctl", "bootout", "%s/%s" % (dom, cfg["label"])], capture_output=True)
            if os.path.exists(p):
                os.makedirs(cfg["state_dir"], exist_ok=True)
                os.replace(p, os.path.join(cfg["state_dir"], "plist-da-go-%s.plist" % time.strftime("%Y%m%d-%H%M")))
        return 0
    errs = preflight(cfg)
    if errs:
        print("Preflight lỗi:", "; ".join(errs))
        return 2
    body = plist(cfg)
    print(body)
    if not apply:
        print("Preflight đạt. CHẠY THỬ: thêm --apply để ghi %s và nạp vào launchd." % p)
        return 0
    os.umask(0o077)
    subprocess.run(["launchctl", "bootout", "%s/%s" % (dom, cfg["label"])], capture_output=True)
    time.sleep(1)
    with open(p, "w") as f:
        f.write(body)
    os.chmod(p, 0o644)
    for _ in range(2):
        r = subprocess.run(["launchctl", "bootstrap", dom, p], capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(2)
    print("launchctl bootstrap mã", r.returncode, r.stderr.strip(), "" if r.returncode == 0 else "(cần phiên đăng nhập GUI của user này)")
    return r.returncode


def status(cfg):
    sp = os.path.join(cfg["state_dir"], "state.json")
    st = json.load(open(sp)) if os.path.exists(sp) else {}
    print("đang lỗi:", {k: v for k, v in st.get("checks", {}).items() if v.get("fail")} or "không")
    print("đếm theo ngày:", st.get("counts", {}))
    lp = os.path.join(cfg["state_dir"], "log-%s.jsonl" % dt.date.today().isoformat()[:7])
    if os.path.exists(lp):
        for line in open(lp, encoding="utf-8").readlines()[-5:]:
            print(line.rstrip()[:500])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "test-alert", "status", "install", "uninstall"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    if a.cmd == "run":
        return run_safe(cfg, a.dry)
    if a.cmd == "test-alert":
        return 0 if send(cfg, "[CDN %s] Tin thử của giám sát CDN. Từ giờ bot báo khi có lỗi, báo khi hồi phục, và gửi tin \"vẫn chạy\" mỗi sáng." % cfg["domain"], a.dry) else 1
    if a.cmd == "status":
        return status(cfg)
    return install(cfg, a.apply, remove=a.cmd == "uninstall")


if __name__ == "__main__":
    sys.exit(main())
