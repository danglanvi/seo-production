#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup_doctor.py — khám máy: repo này còn thiếu gì để chạy được agentic workflow.

Chạy từ root repo (Account Production / BD Production / SEO Production / Content Production / instance PROJECTS):
    python3 _SETUP/setup_doctor.py              # in bảng khám cho người đọc
    python3 _SETUP/setup_doctor.py --json       # bản máy đọc, để AI tự quyết bước kế tiếp
    python3 _SETUP/setup_doctor.py --fix        # tự cài phần cài được (pip, playwright) rồi khám lại
    python3 _SETUP/setup_doctor.py --tier C     # chỉ chạy 1 tầng (A|B|C|D)

Bốn tầng, chạy theo thứ tự — tầng sau chỉ có nghĩa khi tầng trước đạt:
    A. NỀN       python3 / git / node / npx / uv / gws — cài bằng brew, gws bằng npm
    B. THƯ VIỆN  import từng lib khai trong requirements.txt của repo
    C. ĐĂNG NHẬP gws đăng nhập email công ty, đủ quyền drive/sheets/docs — BẮT BUỘC mọi repo.
                 Robot (service account) chỉ khi repo có script cần: có file, đúng định dạng, đọc được
    D. QUYỀN     (chỉ repo dùng robot) gọi Drive/Sheets API thật trên từng ID repo cần → có quyền EDIT chưa

Script chỉ ĐỌC và chẩn đoán (trừ --fix). Không sửa file nào của repo, không ghi credential.
Chỉ thư viện chuẩn ở tầng A-C — chạy được trên máy chưa cài gì. Tầng D dùng lib Google đã kiểm ở tầng B.

Exit code: 0 = đủ điều kiện chạy · 1 = còn thiếu · 2 = không xác định được repo.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)  # google-auth cảnh báo Python cũ — không liên quan người dùng

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IS_MAC = platform.system() == "Darwin"

# Tên trên PyPI -> tên module lúc import. Chỉ khai lib thật sự có trong requirements.txt của 6 repo.
IMPORT_NAME = {
    "google-api-python-client": "googleapiclient",
    "google-auth": "google.auth",
    "pyyaml": "yaml",
    "pillow": "PIL",
    "python-docx": "docx",
    "python-pptx": "pptx",
    "markdown": "markdown",
    "requests": "requests",
}

# Lệnh cài cho từng thứ ở tầng A. macOS dùng brew; hệ khác chỉ in link vì cách cài khác nhau.
BASE_TOOLS = [
    ("git", "git", "brew install git", "https://git-scm.com/downloads"),
    ("node", "node", "brew install node", "https://nodejs.org"),
    ("npx", "npx", "brew install node", "https://nodejs.org"),
    ("uv", "uv", "brew install uv", "https://docs.astral.sh/uv/getting-started/installation/"),
    ("gws", "gws", "npm install -g @googleworkspace/cli", "npm install -g @googleworkspace/cli"),
]

# gws (Google Workspace CLI) là đường chính vào Google của mọi repo: đăng nhập bằng email công ty,
# file Drive share cho cả domain nên không phải xin quyền từng file.
WORKSPACE_DOMAIN = "gtvseo.com"
GWS_SCOPES = {
    "drive": "https://www.googleapis.com/auth/drive",
    "sheets": "https://www.googleapis.com/auth/spreadsheets",
    "docs": "https://www.googleapis.com/auth/documents",
}
GWS_LOGIN = "gws auth login -s drive,sheets,docs"


# ---------------------------------------------------------------- tiện ích

def rel(path):
    return os.path.relpath(path, ROOT)


class Result:
    """Gom kết quả để in bảng cho người VÀ xuất JSON cho AI từ cùng một nguồn."""

    def __init__(self):
        self.tiers = {}

    def add(self, tier, name, ok, detail="", fix="", skipped=False):
        self.tiers.setdefault(tier, []).append(
            {"name": name, "ok": ok, "skipped": skipped, "detail": detail, "fix": fix}
        )

    def tier_ok(self, tier):
        return all(item["ok"] or item["skipped"] for item in self.tiers.get(tier, []))

    def all_ok(self):
        return all(self.tier_ok(t) for t in self.tiers)


def run(cmd):
    """Chạy lệnh, trả (rc, output gộp). Không raise — doctor không được chết vì lệnh lỗi."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        return 127, "không có lệnh %s" % cmd[0]
    except subprocess.TimeoutExpired:
        return 124, "quá 10 phút, đã hủy"


# ---------------------------------------------------------------- tầng A

def tier_a(res):
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 9)
    res.add("A", "python3 >= 3.9", ok, "đang dùng %d.%d" % (major, minor),
            "brew install python3" if IS_MAC else "https://www.python.org/downloads/")

    for label, binary, brew, link in BASE_TOOLS:
        path = shutil.which(binary)
        detail = path or "chưa cài"
        if path and binary == "node":
            rc, out = run(["node", "--version"])
            if rc == 0:
                detail = "%s (%s)" % (path, out)
                m = re.match(r"v(\d+)", out)
                if m and int(m.group(1)) < 18:
                    res.add("A", label, False, detail + " — quá cũ, cần >= 18",
                            brew if IS_MAC else link)
                    continue
        res.add("A", label, bool(path), detail, brew if IS_MAC else link)


# ---------------------------------------------------------------- tầng B

def read_requirements():
    """Đọc requirements.txt của repo -> [(tên pypi, dòng gốc)]. Không có file = repo không cần lib nào."""
    path = os.path.join(ROOT, "requirements.txt")
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            name = re.split(r"[<>=!~\[]", line, 1)[0].strip()
            out.append((name, line))
    return out


def tier_b(res):
    reqs = read_requirements()
    if not reqs:
        res.add("B", "requirements.txt", True, "repo không khai thư viện nào", skipped=True)
        return
    fix = "python3 -m pip install -r requirements.txt"
    for name, line in reqs:
        module = IMPORT_NAME.get(name.lower(), name.lower().replace("-", "_"))
        code = "import %s" % module
        rc, out = run([sys.executable, "-c", code])
        res.add("B", "%s (import %s)" % (name, module), rc == 0,
                line if rc == 0 else out.splitlines()[-1] if out else "không import được", fix)


# ---------------------------------------------------------------- tầng C

def gws_status():
    """Đọc `gws auth status` -> dict, hoặc None. Lệnh in thêm dòng chữ ngoài JSON nên chỉ lấy khối JSON."""
    _, out = run(["gws", "auth", "status"])
    start = out.find("{")
    if start < 0:
        return None
    try:
        return json.JSONDecoder().raw_decode(out[start:])[0]
    except ValueError:
        return None


def tier_c_gws(res):
    guide = "_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md phần 1"
    if not shutil.which("gws"):
        res.add("C", "gws đăng nhập", False, "chưa cài gws (tầng A)", "npm install -g @googleworkspace/cli")
        return
    st = gws_status()
    if st is None:
        res.add("C", "gws đăng nhập", False, "không đọc được `gws auth status`", GWS_LOGIN)
        return
    user = st.get("user") or ""
    if st.get("client_config_exists") is False:
        res.add("C", "gws đăng nhập", False, "thiếu OAuth client (~/.config/gws/client_secret.json)", guide)
        return
    if not user or not (st.get("token_valid") or st.get("has_refresh_token")):
        res.add("C", "gws đăng nhập", False, "chưa đăng nhập", GWS_LOGIN)
        return
    if not user.lower().endswith("@" + WORKSPACE_DOMAIN):
        res.add("C", "gws đăng nhập", False, "%s — cần email @%s" % (user, WORKSPACE_DOMAIN),
                "gws auth logout && " + GWS_LOGIN)
        return
    res.add("C", "gws đăng nhập", True, user)
    scopes = st.get("scopes") or []
    missing = [name for name, url in GWS_SCOPES.items() if url not in scopes]
    res.add("C", "gws quyền drive, sheets, docs", not missing,
            "thiếu: %s" % ", ".join(missing) if missing else "đủ", GWS_LOGIN)


def find_credential():
    """Tìm chìa khóa theo đúng thứ tự ưu tiên mà mọi script trong hệ đang dùng.

    Trả (path, nguồn) hoặc (None, None). KHÔNG quét ~/Downloads ở đây — doctor chỉ báo
    cái đang được dùng thật; việc đi tìm file mới là của setup_credential.py detect.
    """
    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env:
        return os.path.expanduser(env), "biến môi trường GOOGLE_APPLICATION_CREDENTIALS"

    local = os.path.join(ROOT, "config", "local.yaml")
    if os.path.isfile(local):
        with open(local, "r", encoding="utf-8") as handle:
            m = re.search(r"^\s*credentials_path:\s*[\"']?(.+?)[\"']?\s*$", handle.read(), re.M)
        if m:
            return os.path.expanduser(m.group(1)), "config/local.yaml"

    settings = os.path.join(ROOT, ".claude", "settings.local.json")
    if os.path.isfile(settings):
        try:
            with open(settings, "r", encoding="utf-8") as handle:
                value = (json.load(handle).get("env") or {}).get("GOOGLE_APPLICATION_CREDENTIALS")
            if value:
                return os.path.expanduser(value), ".claude/settings.local.json"
        except (ValueError, OSError):
            pass
    return None, None


def read_credential(path):
    """Đọc file key -> (dict, lỗi). Không bao giờ in private_key ra ngoài."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except ValueError:
        return None, "file không phải JSON hợp lệ"
    except OSError as err:
        return None, "không đọc được: %s" % err
    if data.get("type") != "service_account":
        return None, "không phải key service account (type=%s)" % data.get("type")
    if not data.get("client_email") or not data.get("private_key"):
        return None, "thiếu client_email hoặc private_key"
    return data, None


def needs_google():
    """Repo có thật sự cần credential Google không — suy từ chính repo, không cấu hình riêng.

    Có nếu: requirements.txt khai thư viện google, HOẶC bản mẫu MCP khai service account.
    Repo đi Google bằng gws (vd Content Production) không cần robot; gws kiểm riêng ở tier_c_gws.
    """
    for name, line in read_requirements():
        if name.lower().startswith("google-"):
            return True
    for candidate in (os.path.join(ROOT, ".mcp.json.example"),
                      os.path.join(ROOT, "config", "mcp.json.example")):
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as handle:
                raw = handle.read()
            if "SERVICE_ACCOUNT" in raw or "GOOGLE_APPLICATION_CREDENTIALS" in raw:
                return True
    return False


def tier_c(res):
    tier_c_gws(res)
    fix = "python3 _SETUP/setup_credential.py detect"
    if not needs_google():
        res.add("C", "robot (service account)", True, "repo không có script cần robot — gws là đủ", skipped=True)
        return None
    path, source = find_credential()
    if not path:
        res.add("C", "robot (service account)", False,
                "chưa khai ở env, config/local.yaml hay .claude/settings.local.json", fix)
        return None
    if not os.path.isfile(path):
        res.add("C", "robot (service account)", False, "%s (khai ở %s) — không thấy file" % (path, source), fix)
        return None

    data, err = read_credential(path)
    if err:
        res.add("C", "robot (service account)", False, "%s — %s" % (path, err), fix)
        return None

    res.add("C", "robot (service account)", True, "%s (khai ở %s)" % (path, source))
    res.add("C", "robot email", True, data["client_email"])
    mode = oct(os.stat(path).st_mode & 0o777)
    res.add("C", "quyền file key", mode == "0o600", "chmod %s" % mode,
            "chmod 600 %s" % path)
    return data


# ---------------------------------------------------------------- tầng D

def tier_d(res, cred_data):
    """Dùng chung danh sách mục tiêu với setup_credential để hai lệnh không bao giờ nói khác nhau."""
    fix = "python3 _SETUP/setup_credential.py share"
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import setup_credential
        targets = setup_credential.collect_targets()
    except Exception as err:  # registry hỏng không được làm chết doctor
        res.add("D", "đọc registry", False, "lỗi: %s" % err, fix)
        return

    if not targets:
        res.add("D", "quyền Google", True, "repo chưa khai file Google nào cần đọc", skipped=True)
        return

    path, _ = find_credential()
    status = setup_credential.check_access(targets, path)
    for kind, sid, label in targets:
        state = status.get(sid, "?")
        # Viewer KHÔNG phải lỗi chặn: mọi script trong repo đều dùng scope readonly nên chạy được.
        # Chỉ MCP google-sheets mới cần Editor — nên báo cảnh báo, không đánh rớt cả tầng.
        res.add("D", label, state in ("editor", "viewer"),
                setup_credential.LABEL.get(state, "—"), fix)


# ---------------------------------------------------------------- --fix

def do_fix(res):
    """Chỉ cài những thứ cài được bằng lệnh an toàn. Không đụng credential, không sudo."""
    done = []
    if not res.tier_ok("B") and os.path.isfile(os.path.join(ROOT, "requirements.txt")):
        print("\n→ cài thư viện Python...")
        rc, out = run([sys.executable, "-m", "pip", "install", "-r",
                       os.path.join(ROOT, "requirements.txt")])
        print(out[-2000:] if out else "")
        done.append("pip install -r requirements.txt: %s" % ("OK" if rc == 0 else "LỖI"))

    # Repo có script Node (chụp sheet, QC deck) thì mới cần Playwright.
    tools_dir = os.path.join(ROOT, "tools")
    needs_playwright = os.path.isdir(tools_dir) and any(
        name.endswith(".js") for name in os.listdir(tools_dir))
    if needs_playwright and shutil.which("npx"):
        rc, _ = run(["npx", "--yes", "playwright", "--version"])
        if rc != 0:
            print("\n→ cài Playwright (dùng để tự soi lỗi slide)...")
            run(["npm", "install", "playwright"])
            rc, out = run(["npx", "playwright", "install", "chromium"])
            done.append("playwright chromium: %s" % ("OK" if rc == 0 else "LỖI"))
    return done


# ---------------------------------------------------------------- in ấn

MARK = {True: "OK  ", False: "THIẾU"}
TIER_TITLE = {
    "A": "A. NỀN — phần mềm cơ bản của máy",
    "B": "B. THƯ VIỆN — gói Python repo cần",
    "C": "C. ĐĂNG NHẬP — gws (bắt buộc) và robot (khi repo cần)",
    "D": "D. QUYỀN — robot đã được share file chưa (chỉ repo dùng robot)",
}


def print_report(res, order):
    print("Khám máy cho repo: %s\n" % os.path.basename(ROOT))
    for tier in order:
        items = res.tiers.get(tier)
        if not items:
            continue
        print(TIER_TITLE[tier])
        for item in items:
            mark = "bỏ qua" if item["skipped"] else MARK[item["ok"]]
            print("  %-6s %-42s %s" % (mark, item["name"], item["detail"]))
        if not res.tier_ok(tier):
            fixes = sorted({i["fix"] for i in items if not i["ok"] and not i["skipped"] and i["fix"]})
            for fix in fixes:
                print("         → sửa bằng: %s" % fix)
        print()

    if res.all_ok():
        print("KẾT LUẬN: máy đủ điều kiện chạy repo này.")
    else:
        stuck = [t for t in order if t in res.tiers and not res.tier_ok(t)]
        print("KẾT LUẬN: chưa chạy được — còn kẹt ở tầng %s." % ", ".join(stuck))
        print("Làm theo dòng «sửa bằng» của tầng thấp nhất trước, rồi chạy lại doctor.")


def main():
    parser = argparse.ArgumentParser(
        description="Khám máy: repo này còn thiếu gì để chạy agentic workflow")
    parser.add_argument("--json", action="store_true", help="xuất JSON cho AI đọc")
    parser.add_argument("--fix", action="store_true", help="tự cài phần cài được rồi khám lại")
    parser.add_argument("--tier", choices=list("ABCD"), help="chỉ chạy 1 tầng")
    args = parser.parse_args()

    if not os.path.isdir(os.path.join(ROOT, "_SETUP")):
        print("LỖI: phải chạy từ root repo (thư mục chứa _SETUP/).", file=sys.stderr)
        return 2

    order = [args.tier] if args.tier else list("ABCD")

    def examine():
        res = Result()
        if "A" in order:
            tier_a(res)
        if "B" in order:
            tier_b(res)
        cred = None
        if "C" in order:
            cred = tier_c(res)
        if "D" in order:
            if not res.tier_ok("B"):
                res.add("D", "quyền Google", True, "chờ tầng B xong mới kiểm được", skipped=True)
            elif "C" in order and not needs_google():
                res.add("D", "quyền Google", True, "repo không dùng robot — file share cho domain, gws là đủ", skipped=True)
            elif "C" in order and not cred:
                res.add("D", "quyền Google", True, "chờ tầng C xong mới kiểm được", skipped=True)
            else:
                tier_d(res, cred)
        return res

    res = examine()
    if args.fix:
        actions = do_fix(res)
        for line in actions:
            print("   %s" % line)
        res = examine()

    if args.json:
        print(json.dumps({
            "repo": os.path.basename(ROOT),
            "root": ROOT,
            "ok": res.all_ok(),
            "tiers": {t: {"ok": res.tier_ok(t), "checks": res.tiers[t]} for t in res.tiers},
        }, ensure_ascii=False, indent=2))
    else:
        print_report(res, order)
    return 0 if res.all_ok() else 1


if __name__ == "__main__":
    sys.exit(main())
