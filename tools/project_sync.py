#!/usr/bin/env python3
"""project_sync.py — kéo dữ liệu của repo content cùng khách về repo SEO (bản chỉ đọc). Luật: _REFERENCE/project-sync.md.

  python3 tools/project_sync.py pull                    # đọc project-sync.yaml (content_repo, branch) ở root instance
  python3 tools/project_sync.py pull --repo <URL|PATH>  # chỉ định repo content (GitHub URL hoặc thư mục local)

Repo content là nguồn chủ của Kho tri thức khách (00-context/kb/) và bài viết. Lệnh này clone/fetch repo content vào
.peer/content/ (gitignore) rồi chạy tools/content_sync.py: content-status + bài humanized (delivered/) + kb-snapshot/<ngày>/.
Snapshot KB kèm _source.md (repo + commit). Không ghi gì vào repo content.
"""

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_config(path):
    """project-sync.yaml dạng `key: value` một cấp (không cần PyYAML)."""
    cfg = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" in line:
                key, value = line.split(":", 1)
                cfg[key.strip()] = value.strip().strip("\"'")
    return cfg


def git(*args):
    return subprocess.run(["git", *map(str, args)], check=True, capture_output=True, text=True).stdout.strip()


def fetch(repo, branch, dest):
    if (dest / ".git").is_dir():
        git("-C", dest, "fetch", "--depth", "1", "origin", branch)
        git("-C", dest, "reset", "-q", "--hard", "FETCH_HEAD")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "-q", "--depth", "1", "--branch", branch, repo, dest)
    return git("-C", dest, "rev-parse", "HEAD")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["pull"])
    ap.add_argument("--repo", help="URL GitHub hoặc thư mục repo content; mặc định content_repo trong project-sync.yaml")
    ap.add_argument("--branch", help="mặc định branch trong project-sync.yaml, không có thì main")
    a = ap.parse_args()
    cfg = read_config(ROOT / "project-sync.yaml")
    repo = a.repo or cfg.get("content_repo")
    if not repo or "{{" in repo:
        print("Thiếu repo content: điền content_repo trong project-sync.yaml (mẫu _TEMPLATES/project-sync.yaml) hoặc dùng --repo")
        return 2
    branch = a.branch or cfg.get("branch") or "main"
    peer = ROOT / ".peer" / "content"
    try:
        commit = fetch(repo, branch, peer)
    except subprocess.CalledProcessError as exc:
        print(f"Không kéo được repo content {repo} ({branch}): {exc.stderr.strip() or exc}")
        return 1
    print(f"✓ repo content {repo} @ {commit[:8]}", flush=True)
    res = subprocess.run([sys.executable, str(ROOT / "tools" / "content_sync.py"), "--fork", str(peer),
                          "--pull-delivered", "--pull-kb"])
    snap = ROOT / "00-client-context" / "kb-snapshot" / dt.date.today().isoformat()
    if res.returncode == 0 and snap.is_dir() and not (snap / "_source.md").exists():
        (snap / "_source.md").write_text(
            f"# Nguồn snapshot KB\n\n- Repo: {repo}\n- Nhánh: {branch}\n- Commit: {commit}\n"
            f"- Kéo lúc: {dt.datetime.now().isoformat(timespec='minutes')}\n\n"
            "Chỉ đọc. Sửa fact ở repo content (Kho tri thức khách) rồi kéo bản mới.\n", encoding="utf-8")
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())
