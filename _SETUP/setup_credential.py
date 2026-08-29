#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup_credential.py — gắn chìa khóa Google CỦA BẠN vào repo này, rồi in danh sách file cần xin quyền.

Chạy từ root repo:
    python3 _SETUP/setup_credential.py detect              # máy đã có key chưa? có thì dùng luôn
    python3 _SETUP/setup_credential.py register <key.json> # gắn key vào repo (chép, phân quyền, ghi config)
    python3 _SETUP/setup_credential.py share                # in checklist: xin share file nào, quyền gì
    python3 _SETUP/setup_credential.py check                # soát lại: cấu hình đã đủ và sạch placeholder chưa

Mô hình: MỖI NGƯỜI MỘT ROBOT RIÊNG. Bạn tự tạo service account trong Google Cloud của mình
(hướng dẫn: _SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md), rồi chạy `register`. Repo không chứa
robot của ai cả — mọi thứ nhận dạng bạn đều nằm trong file local đã gitignore.

`register` ghi đúng 3 chỗ, tất cả đều KHÔNG commit:
    ~/.config/gcp/<project>-<robot>.json   chìa khóa, chmod 600, nằm NGOÀI repo (không bao giờ lọt git)
    config/local.yaml                       để script chạy từ terminal biết đường dẫn key
    .claude/settings.local.json             để mọi lệnh chạy trong Claude Code có sẵn biến môi trường
Và render .mcp.json từ .mcp.json.example nếu repo có bản mẫu.

Chỉ thư viện chuẩn — chạy được trước khi pip install. Verb `share` cần lib Google mới kiểm được
trạng thái thật; thiếu lib thì vẫn in checklist, chỉ bỏ cột trạng thái.
"""
import argparse
import glob
import json
import os
import re
import shutil
import stat
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)  # google-auth cảnh báo Python cũ — không liên quan người dùng

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GCP_DIR = os.path.expanduser("~/.config/gcp")
LOCAL_YAML = os.path.join(ROOT, "config", "local.yaml")
CLAUDE_SETTINGS = os.path.join(ROOT, ".claude", "settings.local.json")
MCP_EXAMPLE = None  # tìm động ở dưới — repo để .mcp.json.example ở root hoặc config/

SCOPES_RW = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HUONG_DAN = """
Chưa có chìa khóa nào trên máy. Bạn cần TỰ TẠO robot của riêng mình — 6 bước, khoảng 10 phút:

  1. Vào https://console.cloud.google.com → tạo project mới (tên gì cũng được, vd "gtv-<tên bạn>").
  2. APIs & Services → Library → bật 2 API: «Google Sheets API» và «Google Drive API».
  3. IAM & Admin → Service Accounts → Create service account → đặt tên → Done.
  4. Bấm vào service account vừa tạo → tab KEYS → Add key → Create new key → chọn JSON → Create.
     Trình duyệt tải về 1 file .json — ĐÂY LÀ CHÌA KHÓA, giữ kín như mật khẩu.
  5. Quay lại đây chạy:  python3 _SETUP/setup_credential.py register ~/Downloads/<tên-file>.json
  6. Script sẽ in ra địa chỉ robot của bạn + danh sách file cần xin quyền Editor.

Giải thích đầy đủ (robot là gì, chìa khóa là gì, giữ sao cho an toàn):
  _SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md
"""


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def rel(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def read_key(path):
    """Đọc file service account -> dict. Trả None nếu không phải key hợp lệ."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (ValueError, OSError):
        return None
    if data.get("type") != "service_account" or not data.get("client_email"):
        return None
    return data


def find_mcp_example():
    for candidate in (os.path.join(ROOT, ".mcp.json.example"),
                      os.path.join(ROOT, "config", "mcp.json.example")):
        if os.path.isfile(candidate):
            return candidate
    return None


def current_config():
    """Đường dẫn key repo đang dùng, theo đúng thứ tự ưu tiên của mọi script trong hệ."""
    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env:
        return os.path.expanduser(env), "biến môi trường"
    if os.path.isfile(LOCAL_YAML):
        with open(LOCAL_YAML, "r", encoding="utf-8") as handle:
            m = re.search(r"^\s*credentials_path:\s*[\"']?(.+?)[\"']?\s*$", handle.read(), re.M)
        if m:
            return os.path.expanduser(m.group(1)), rel(LOCAL_YAML)
    if os.path.isfile(CLAUDE_SETTINGS):
        try:
            with open(CLAUDE_SETTINGS, "r", encoding="utf-8") as handle:
                value = (json.load(handle).get("env") or {}).get("GOOGLE_APPLICATION_CREDENTIALS")
            if value:
                return os.path.expanduser(value), rel(CLAUDE_SETTINGS)
        except (ValueError, OSError):
            pass
    return None, None


# ---------------------------------------------------------------- detect

def cmd_detect(args):
    path, source = current_config()
    if path and read_key(path):
        data = read_key(path)
        print("Repo ĐÃ được cấu hình rồi.")
        print("  robot  : %s" % data["client_email"])
        print("  key    : %s" % path)
        print("  khai ở : %s" % source)
        print("\nKiểm tra quyền truy cập: python3 _SETUP/setup_credential.py share")
        return 0
    if path:
        print("CẢNH BÁO: %s trỏ tới %s nhưng file đó không đọc được.\n" % (source, path))

    # Quét những chỗ key hay nằm. Ưu tiên ~/.config/gcp (chỗ chuẩn), rồi ~/Downloads (vừa tải về).
    seen, found = set(), []
    for pattern in (os.path.join(GCP_DIR, "*.json"),
                    os.path.expanduser("~/Downloads/*.json")):
        for candidate in sorted(glob.glob(pattern)):
            real = os.path.realpath(candidate)
            if real in seen:
                continue
            seen.add(real)
            data = read_key(candidate)
            if data:
                found.append((candidate, data))

    if not found:
        print(HUONG_DAN)
        return 1

    print("Tìm thấy %d chìa khóa trên máy:\n" % len(found))
    for index, (candidate, data) in enumerate(found, 1):
        print("  [%d] %s" % (index, candidate))
        print("      robot: %s" % data["client_email"])
        print("      project: %s" % data.get("project_id", "?"))
    print("\nGắn cái bạn muốn dùng vào repo này:")
    print("  python3 _SETUP/setup_credential.py register \"%s\"" % found[0][0])
    return 1


# ---------------------------------------------------------------- register

def write_local_yaml(key_path, data):
    os.makedirs(os.path.dirname(LOCAL_YAML), exist_ok=True)
    with open(LOCAL_YAML, "w", encoding="utf-8") as handle:
        handle.write(
            "# Cấu hình LOCAL của máy bạn — sinh bởi _SETUP/setup_credential.py.\n"
            "# KHÔNG commit (đã nằm trong .gitignore). Mỗi người một robot riêng.\n"
            "google:\n"
            "  credentials_path: %s\n"
            "  service_account_email: %s\n"
            "  project_id: %s\n" % (key_path, data["client_email"], data.get("project_id", ""))
        )
    return LOCAL_YAML


def write_claude_settings(key_path):
    """Đặt biến môi trường cho mọi lệnh chạy trong Claude Code — nhờ vậy script cũ không cần sửa.

    Merge theo key, giữ nguyên phần cấu hình sẵn có của người dùng (permissions, hooks...).
    """
    os.makedirs(os.path.dirname(CLAUDE_SETTINGS), exist_ok=True)
    settings = {}
    if os.path.isfile(CLAUDE_SETTINGS):
        try:
            with open(CLAUDE_SETTINGS, "r", encoding="utf-8") as handle:
                settings = json.load(handle)
        except ValueError:
            backup = CLAUDE_SETTINGS + ".bak"
            shutil.copy2(CLAUDE_SETTINGS, backup)
            print("   (settings.local.json hỏng JSON — đã backup sang %s rồi ghi mới)" % rel(backup))
    settings.setdefault("env", {})["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    with open(CLAUDE_SETTINGS, "w", encoding="utf-8") as handle:
        json.dump(settings, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return CLAUDE_SETTINGS


def render_mcp(key_path, data):
    """Sinh .mcp.json từ bản mẫu, thay placeholder liên quan credential.

    Placeholder không đoán được (API key, GA4 property, Drive folder) để nguyên — `check` sẽ
    liệt kê đích danh cho người dùng điền tay. Không bao giờ đè .mcp.json đã có.
    """
    example = find_mcp_example()
    if not example:
        return None, []
    target = os.path.join(ROOT, ".mcp.json")
    if os.path.isfile(target):
        return None, ["đã có .mcp.json — giữ nguyên, không đè"]

    with open(example, "r", encoding="utf-8") as handle:
        raw = handle.read()
    raw = raw.replace("{{DUONG_DAN_TUYET_DOI_SERVICE_ACCOUNT_JSON}}", key_path)
    raw = raw.replace("{{SERVICE_ACCOUNT_EMAIL}}", data["client_email"])

    try:
        parsed = json.loads(raw)
    except ValueError as err:
        return None, ["bản mẫu %s không phải JSON hợp lệ: %s" % (rel(example), err)]
    parsed.pop("_huong_dan", None)  # bỏ trước khi quét placeholder: hướng dẫn có nhắc {{TEN_BIEN}} làm ví dụ

    # File sinh ra phải luôn chạy được: Claude Code gặp {{...}} là server đó lỗi khi khởi động.
    # Thiếu API key -> server vô dụng, bỏ cả server. Thiếu ID tùy chọn (Drive folder, GA4 property)
    # -> chỉ bỏ biến đó, server vẫn chạy với hành vi mặc định.
    dropped = []
    servers = parsed.get("mcpServers") or {}
    secret = re.compile(r"KEY|TOKEN|SECRET|PASSWORD")
    for name in sorted(servers):
        env = servers[name].get("env") or {}
        unfilled = [k for k, v in env.items()
                    if isinstance(v, str) and re.search(r"\{\{[A-Z0-9_]+\}\}", v)]
        if any(secret.search(k) for k in unfilled):
            del servers[name]
            dropped.append(name)
            continue
        for key in unfilled:
            del env[key]

    with open(target, "w", encoding="utf-8") as handle:
        json.dump(parsed, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return target, dropped


def cmd_register(args):
    src = os.path.expanduser(args.key)
    if not os.path.isfile(src):
        die("LỖI: không thấy file %s" % src)
    data = read_key(src)
    if not data:
        die("LỖI: %s không phải file key service account.\n"
            "Key đúng là file JSON có \"type\": \"service_account\" — tải từ Google Cloud Console\n"
            "→ IAM & Admin → Service Accounts → tab Keys → Add key → JSON." % src)

    os.makedirs(GCP_DIR, exist_ok=True)
    os.chmod(GCP_DIR, stat.S_IRWXU)

    # Key đã nằm đúng chỗ rồi thì dùng tại chỗ — không nhân bản file bí mật thêm lần nữa.
    if os.path.dirname(os.path.realpath(src)) == os.path.realpath(GCP_DIR):
        dest = os.path.realpath(src)
    else:
        project = data.get("project_id", "gcp")
        robot = data["client_email"].split("@", 1)[0]
        dest = os.path.join(GCP_DIR, "%s-%s.json" % (project, robot))
        shutil.copy2(src, dest)
    os.chmod(dest, stat.S_IRUSR | stat.S_IWUSR)

    print("Đã gắn robot vào repo %s\n" % os.path.basename(ROOT))
    print("  robot : %s" % data["client_email"])
    print("  key   : %s  (chmod 600, nằm ngoài repo nên không bao giờ lọt git)" % dest)
    print("\nĐã ghi:")
    print("  · %s" % rel(write_local_yaml(dest, data)))
    print("  · %s" % rel(write_claude_settings(dest)))
    mcp, notes = render_mcp(dest, data)
    if mcp:
        print("  · %s (sinh từ bản mẫu)" % rel(mcp))
    if mcp and notes:
        print("\n  Đã bỏ %d MCP server khỏi .mcp.json vì cần key bạn chưa có: %s"
              % (len(notes), ", ".join(notes)))
        print("  Có key rồi thì thêm lại từ .mcp.json.example — không bắt buộc để repo chạy.")
    elif notes:
        for note in notes:
            print("  · %s" % note)

    if os.path.realpath(src).startswith(os.path.expanduser("~/Downloads")):
        print("\n⚠  Bản gốc vẫn nằm trong ~/Downloads. Xóa đi cho sạch:\n   rm \"%s\"" % src)

    print("\n" + "-" * 72)
    return cmd_share(args)


# ---------------------------------------------------------------- share

def collect_targets():
    """Gom thứ cần xin quyền, ưu tiên FOLDER CHA — share 1 folder là mọi file bên trong có luôn.

    Trả [(loại, id, nhãn)]. Cần PyYAML; thiếu thì trả rỗng và caller tự báo.
    """
    import yaml

    targets, seen = [], set()

    def add(kind, sid, label):
        sid = str(sid).strip()
        if re.fullmatch(r"[A-Za-z0-9_-]{20,}", sid) and sid not in seen:
            seen.add(sid)
            targets.append((kind, sid, label))

    # drive-links.yaml: chỉ lấy FOLDER GỐC (parent rỗng) của từng client. Share folder gốc là
    # mọi file con bên trong có quyền theo, kể cả file tạo mới sau này — không liệt kê file lẻ.
    links = os.path.join(ROOT, "tools", "drive-links.yaml")
    if os.path.isfile(links):
        with open(links, "r", encoding="utf-8") as handle:
            reg = yaml.safe_load(handle) or {}
        for slug, meta in (reg.get("clients") or {}).items():
            if not isinstance(meta, dict):
                continue
            for item in meta.get("files") or []:
                if not isinstance(item, dict):
                    continue
                if item.get("kind") == "folder" and not str(item.get("parent") or "").strip():
                    add("folder", item.get("id", ""),
                        "folder gốc «%s» — client %s" % (item.get("name", "?"), slug))

    registry = os.path.join(ROOT, "tools", "review-sheets.yaml")
    if os.path.isfile(registry):
        with open(registry, "r", encoding="utf-8") as handle:
            reg = yaml.safe_load(handle) or {}
        for slug, meta in (reg.get("clients") or {}).items():
            if isinstance(meta, dict) and meta.get("id"):
                add("sheet", meta["id"], "workbook «Theo dõi dự án» — client %s" % slug)
        for name, meta in (reg.get("members") or {}).items():
            if isinstance(meta, dict) and meta.get("id"):
                add("sheet", meta["id"], "sheet report tuần — %s" % name)

    for name in ("report-config.yaml", os.path.join("09-reporting", "report-config.yaml")):
        cfg_path = os.path.join(ROOT, name)
        if not os.path.isfile(cfg_path):
            continue
        with open(cfg_path, "r", encoding="utf-8") as handle:
            cfg = yaml.safe_load(handle) or {}
        # folder báo cáo tuần: share 1 lần, mọi workbook tạo bên trong tự kế thừa quyền
        for node in (cfg, cfg.get("report_tuan") or {}):
            if isinstance(node, dict) and node.get("drive_folder_id"):
                add("folder", node["drive_folder_id"], "folder báo cáo dự án (%s)" % name)
        for key, meta in (cfg.get("spreadsheets") or {}).items():
            if isinstance(meta, dict) and meta.get("id"):
                add("sheet", meta["id"], "workbook «%s» (%s)" % (key, name))
    return targets


def link_for(kind, sid):
    if kind == "folder":
        return "https://drive.google.com/drive/folders/%s" % sid
    return "https://docs.google.com/spreadsheets/d/%s/edit" % sid


def check_access(targets, key_path):
    """Hỏi Drive xem robot đã có quyền gì. Trả {id: 'editor'|'viewer'|'chưa có'|'?'}."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError:
        return {}
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=SCOPES_RW)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    status = {}
    for _, sid, _ in targets:
        try:
            meta = drive.files().get(fileId=sid, fields="capabilities/canEdit",
                                     supportsAllDrives=True).execute()
            status[sid] = "editor" if (meta.get("capabilities") or {}).get("canEdit") else "viewer"
        except HttpError:
            status[sid] = "chưa có"
        except Exception:
            status[sid] = "?"
    return status


LABEL = {"editor": "✅ Editor",
         "viewer": "⚠️  chỉ Viewer — script đọc được, AI ghi qua MCP sẽ lỗi; nên xin nâng Editor",
         "chưa có": "❌ chưa share", "?": "— không kiểm được"}


def cmd_share(args):
    path, source = current_config()
    if not path or not read_key(path):
        die("Chưa gắn chìa khóa. Chạy trước: python3 _SETUP/setup_credential.py detect")
    data = read_key(path)
    email = data["client_email"]

    print("\nĐỊA CHỈ ROBOT CỦA BẠN — copy dòng này để gửi cho người giữ file:\n")
    print("    %s\n" % email)

    try:
        targets = collect_targets()
    except ImportError:
        print("(chưa cài PyYAML nên không đọc được registry — chạy tầng B của doctor trước)")
        return 1

    if not targets:
        print("Repo này chưa khai file Google nào cần đọc — chưa phải xin quyền gì.")
        print("Khi Lead đưa link Drive/Sheet của client, khai vào registry rồi chạy lại lệnh này.")
        return 0

    status = check_access(targets, path)
    print("Xin quyền **Editor** cho robot trên %d mục sau (chia sẻ như chia sẻ cho người thường):\n"
          % len(targets))
    folders = [t for t in targets if t[0] == "folder"]
    if folders:
        print("  Ưu tiên share FOLDER trước — share 1 folder thì mọi file bên trong có quyền luôn,")
        print("  kể cả file tạo mới sau này. Chỉ share từng sheet khi sheet nằm ngoài các folder này.\n")

    for index, (kind, sid, label) in enumerate(targets, 1):
        state = LABEL.get(status.get(sid, "?"), "—")
        print("  %2d. [%s] %s" % (index, "FOLDER" if kind == "folder" else "sheet ", label))
        print("      %s" % link_for(kind, sid))
        print("      %s\n" % state)

    if not status:
        print("(chưa cài đủ lib Google nên không kiểm được trạng thái — cột trên chỉ là danh sách cần share)")
        return 1

    missing = [t for t in targets if status.get(t[1]) == "chưa có"]
    viewer = [t for t in targets if status.get(t[1]) == "viewer"]

    if missing:
        print("Còn %d mục robot CHƯA thấy. Cách xin (bạn KHÔNG tự cấp được — phải người sở hữu file làm):\n"
              % len(missing))
        print("  Nhắn cho Lead / người sở hữu file:")
        print("  ┌" + "─" * 70)
        print("  │ Anh/chị share giúp em quyền **Editor** cho địa chỉ robot này với ạ:")
        print("  │     %s" % email)
        print("  │ Cần Editor (không phải Viewer) vì script ghi thẳng vào sheet.")
        print("  │ Các mục cần share:")
        for kind, sid, label in missing[:10]:
            print("  │   · %s — %s" % (label, link_for(kind, sid)))
        if len(missing) > 10:
            print("  │   · ... và %d mục nữa" % (len(missing) - 10))
        print("  └" + "─" * 70)
        print("\nShare xong chạy lại lệnh này để xác nhận: python3 _SETUP/setup_credential.py share")
        return 1

    if viewer:
        print("Robot thấy đủ %d mục — script trong repo chạy được ngay." % len(targets))
        print("%d mục mới ở mức Viewer. Script không sao (đều đọc-only), nhưng AI thao tác sheet qua"
              % len(viewer))
        print("MCP google-sheets sẽ lỗi ghi. Xin nâng lên Editor khi cần, trừ mục cố ý để Viewer:")
        for kind, sid, label in viewer:
            print("   · %s" % label)
        print("\nGiải thích: _SETUP/CHIA-QUYEN-DRIVE.md")
        return 0

    print("Đủ quyền Editor trên toàn bộ danh sách. Giải thích: _SETUP/CHIA-QUYEN-DRIVE.md")
    return 0


# ---------------------------------------------------------------- check

def repo_needs_google():
    """Dùng chung tiêu chí với setup_doctor để hai lệnh không đòi hỏi khác nhau."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import setup_doctor
        return setup_doctor.needs_google()
    except Exception:
        return True  # không xác định được thì cứ đòi — thà thừa còn hơn bỏ sót


def cmd_check(args):
    problems, notes = [], []
    path, source = current_config()
    if not path and not repo_needs_google():
        notes.append("repo không dùng API Google — không cần credential")
    elif not path:
        problems.append("chưa khai credentials ở đâu cả — chạy `detect`")
    elif not os.path.isfile(path):
        problems.append("%s trỏ tới %s nhưng không có file" % (source, path))
    elif not read_key(path):
        problems.append("%s không phải key service account hợp lệ" % path)
    else:
        mode = os.stat(path).st_mode & 0o777
        if mode != 0o600:
            problems.append("key %s đang chmod %s — nên là 600 (chmod 600 \"%s\")"
                            % (path, oct(mode), path))

    mcp = os.path.join(ROOT, ".mcp.json")
    if os.path.isfile(mcp):
        with open(mcp, "r", encoding="utf-8") as handle:
            raw = handle.read()
        left = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", raw)))
        if left:
            problems.append(".mcp.json còn placeholder chưa điền: %s" % ", ".join(left))
        try:
            json.loads(raw)
        except ValueError as err:
            problems.append(".mcp.json không phải JSON hợp lệ: %s" % err)
    elif find_mcp_example():
        # MCP là tùy chọn: repo chạy được không cần, skill thiếu server sẽ tự chạy đường lùi.
        notes.append("chưa có .mcp.json (bản mẫu: %s). Không bắt buộc — chỉ cần khi muốn dùng MCP."
                     % rel(find_mcp_example()))

    if problems:
        print("CHƯA ĐẠT — %d việc phải xử lý:" % len(problems))
        for problem in problems:
            print("  · %s" % problem)
        for note in notes:
            print("  (ghi chú) %s" % note)
        return 1
    print("ĐẠT — cấu hình credential của repo %s sạch và đầy đủ." % os.path.basename(ROOT))
    for note in notes:
        print("  (ghi chú) %s" % note)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Gắn chìa khóa Google của bạn vào repo + in checklist xin quyền")
    sub = parser.add_subparsers(dest="verb", required=True)
    sub.add_parser("detect", help="máy đã có key chưa; có thì chỉ cách dùng luôn")
    reg = sub.add_parser("register", help="gắn 1 file key vào repo này")
    reg.add_argument("key", help="đường dẫn file .json tải từ Google Cloud")
    sub.add_parser("share", help="in checklist file cần xin quyền Editor")
    sub.add_parser("check", help="soát lại cấu hình đã đủ và sạch placeholder chưa")
    args = parser.parse_args()

    if not os.path.isdir(os.path.join(ROOT, "_SETUP")):
        die("LỖI: phải chạy từ root repo (thư mục chứa _SETUP/).", 2)

    return {"detect": cmd_detect, "register": cmd_register,
            "share": cmd_share, "check": cmd_check}[args.verb](args)


if __name__ == "__main__":
    sys.exit(main())
