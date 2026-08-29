# -*- coding: utf-8 -*-
"""_cred.py — tìm chìa khóa service account cho mọi script báo cáo trong skill này.

Thứ tự: biến môi trường GOOGLE_APPLICATION_CREDENTIALS  ->  config/local.yaml của repo
        (do _SETUP/setup_credential.py sinh)  ->  `credentials:` trong report-config.yaml.

Mỗi người dùng service account của riêng mình; repo không giữ credential của ai — vì vậy
report-config.yaml để trống trường `credentials`, và giá trị thật sống ở file local.
"""
import os
import re
import sys


def _from_local_yaml(start):
    """Đi ngược lên tìm config/local.yaml của repo. Dùng regex để không phụ thuộc pyyaml."""
    cur = os.path.dirname(os.path.abspath(start))
    while True:
        candidate = os.path.join(cur, "config", "local.yaml")
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as handle:
                m = re.search(r"^\s*credentials_path:\s*[\"']?(.+?)[\"']?\s*$", handle.read(), re.M)
            return m.group(1) if m else None
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def path(cfg=None, start=None):
    """Trả đường dẫn file key. Không tìm thấy -> thoát kèm hướng dẫn, không trả None."""
    cand = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cand:
        cand = _from_local_yaml(start or (cfg or {}).get("_config_dir") or __file__)
    if not cand and cfg:
        cand = cfg.get("credentials")
    if not cand:
        sys.exit("LỖI: máy chưa cấu hình credential Google.\n"
                 "  Chạy: python3 _SETUP/setup_credential.py detect")
    cand = os.path.expanduser(str(cand))
    if not os.path.isfile(cand):
        sys.exit("LỖI: không thấy file credentials: %s\n"
                 "  Chạy lại: python3 _SETUP/setup_credential.py detect" % cand)
    return cand
