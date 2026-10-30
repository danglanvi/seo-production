#!/usr/bin/env python3
"""Test offline cho transcript_recall.py và các lệnh CLI của handoff.py. Chạy: python3 -B tests/test_transcript_recall.py
Fixture là transcript giả dựng trong thư mục tạm; không đọc ~/.claude."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
RECALL = SCRIPTS / "transcript_recall.py"
HANDOFF = SCRIPTS / "handoff.py"
os.environ["TZ"] = "Asia/Ho_Chi_Minh"
time.tzset()

# Khoá giả ghép từ mảnh, để file test không chứa chuỗi giống secret thật.
FAKE_KEY = "sk-" + "ant-" + "A1b2C3d4" * 4
FAKE_JWT = "ey" + "J" + "a" * 12 + "." + "b" * 12 + "." + "c" * 12
FAKE_HOST = "stg-" + "demo-host.example.net"
FAKE_IP = "203." + "0.113.7"
FAKE_HEX = "9f" * 20
# Hai dạng key dán vào chat ngày 26–27/10/2026, ghép giả từ mảnh: QUIC.cloud <chữ>.<32 ký tự>, Bunny hai UUID nối liền.
FAKE_QUIC = "AbCdEfG" + "." + "Xy7Kq2Lm" * 4
FAKE_UUID = "1a2b3c4d-" + "5e6f-7a8b-9c0d-" + "1e2f3a4b5c6d"
FAKE_BUNNY = FAKE_UUID + FAKE_UUID.replace("1", "7")
LONG_TEXT = "Lead dặn rất dài " + "chi tiết " * 120 + "CUỐI-TIN"


def rec(kind, content, ts, side=False):
    return {"type": kind, "isSidechain": side, "timestamp": ts, "message": {"role": kind, "content": content}}


def build(d):
    big = "dòng log dài " * 2000
    lines = [
        {"type": "ai-title", "aiTitle": "Workstream site-mau", "sessionId": "x"},
        rec("user", "<system-reminder>luật</system-reminder>", "2026-10-19T11:00:00.000Z"),
        rec("user", [{"type": "text", "text": "Đổi link GnLt sang bản mới nhé. Cấu hình API_KEY=" + FAKE_KEY}], "2026-10-19T11:07:00.000Z"),
        rec("assistant", [{"type": "thinking", "thinking": "bỏ qua"}, {"type": "text", "text": f"Đã đổi. Gọi {FAKE_HOST} từ {FAKE_IP} với {FAKE_JWT} và hash {FAKE_HEX}."}], "2026-10-19T11:08:00.000Z"),
        rec("assistant", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "curl -u admin:matkhau https://" + FAKE_HOST + "/x"}}], "2026-10-19T11:09:00.000Z"),
        rec("user", [{"type": "tool_result", "tool_use_id": "t1", "content": "ok 200"}], "2026-10-19T11:09:05.000Z"),
        rec("assistant", [{"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": "/a/b.md"}}], "2026-10-19T11:10:00.000Z"),
        rec("user", [{"type": "tool_result", "tool_use_id": "t2", "content": [{"type": "text", "text": big}]}], "2026-10-19T11:10:05.000Z"),
        rec("assistant", [{"type": "tool_use", "id": "t3", "name": "Read", "input": {"file_path": "BRAIN/journal/2026-10-01.md"}}], "2026-10-19T11:11:00.000Z"),
        rec("user", [{"type": "tool_result", "tool_use_id": "t3", "content": "nội dung riêng tư"}], "2026-10-19T11:11:05.000Z"),
        rec("user", "Xem lại BRAIN/journal hôm qua giúp tôi", "2026-10-19T11:12:00.000Z"),
        rec("user", "tin của agent phụ", "2026-10-19T11:13:00.000Z", side=True),
        rec("user", "Tiếp tục lô 2, không hỏi lại.", "2026-10-19T12:00:00.000Z"),
        rec("user", f"đây là API key của tôi: {FAKE_QUIC} và API bunny: {FAKE_BUNNY}; run {FAKE_UUID}", "2026-10-19T12:05:00.000Z"),
        {"type": "attachment", "isSidechain": False, "timestamp": "2026-10-19T12:06:00.000Z",
         "attachment": {"type": "queued_command", "commandMode": "prompt", "prompt": "nhớ đọc, review từng câu chữ chat cụ thể nhé"}},
        {"type": "attachment", "isSidechain": False, "timestamp": "2026-10-19T12:06:00.000Z",
         "attachment": {"type": "queued_command", "commandMode": "task-notification", "prompt": "<task-notification>xong</task-notification>"}},
        rec("user", LONG_TEXT, "2026-10-19T12:07:00.000Z"),
    ]
    f = d / "84cabbc3-aaaa.jsonl"
    f.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\nhỏng không phải json\n", encoding="utf-8")
    (d / "84cabbc3-bbbb.jsonl").write_text("{}\n", encoding="utf-8")
    (d / "7ecaa7b8-cccc.jsonl").write_text(json.dumps(rec("user", "phiên khác", "2026-10-18T10:00:00.000Z")) + "\n", encoding="utf-8")
    return f


def run(script, *args, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run([sys.executable, "-B", str(script), *args], capture_output=True, text=True, env=e)


def main():
    d = Path(tempfile.mkdtemp())
    build(d)
    base = ["--projects-dir", str(d)]

    for script in (RECALL, HANDOFF):
        r = run(script, "--help")
        assert r.returncode == 0 and "usage" in r.stdout.lower(), script
    assert run(RECALL, "user", "7ecaa7b8", *base).stdout.count("phiên khác") == 1

    # Tin của Lead: giờ VN, key bị che, reminder và tin agent phụ bị bỏ, BRAIN/journal bị ẩn.
    r = run(RECALL, "user", "7ecaa7b8-c", *base)
    assert "[18/10 17:00] Lead: phiên khác" in r.stdout, r.stdout
    r = run(RECALL, "user", "84cabbc3-aaaa", *base)
    assert r.returncode == 0, r.stderr
    assert "[19/10 18:07] Lead: Đổi link GnLt" in r.stdout and FAKE_KEY not in r.stdout and "API_KEY=[ẨN]" in r.stdout, r.stdout
    assert "luật" not in r.stdout and "agent phụ" not in r.stdout, r.stdout
    assert "nhắc tới BRAIN/journal" in r.stdout and "hôm qua giúp" not in r.stdout, r.stdout
    assert "Tiếp tục lô 2" in r.stdout
    # Lọc grep, since, last.
    r = run(RECALL, "user", "84cabbc3-aaaa", "--grep", "lô 2", *base)
    assert r.stdout.count("Lead:") == 1 and "Tiếp tục lô 2" in r.stdout
    r = run(RECALL, "user", "84cabbc3-aaaa", "--since", "2026-10-19 19:00", "--until", "2026-10-19 19:00", *base)
    assert r.stdout.count("Lead:") == 1 and "[19/10 19:00]" in r.stdout, r.stdout
    r = run(RECALL, "user", "84cabbc3-aaaa", "--last", "1", *base)
    assert r.stdout.count("Lead:") == 1

    # Key QUIC.cloud và Bunny bị che; UUID đơn (run id) giữ nguyên.
    r = run(RECALL, "user", "84cabbc3-aaaa", "--grep", "API key", *base)
    assert FAKE_QUIC not in r.stdout and FAKE_BUNNY not in r.stdout and FAKE_QUIC.split(".")[1] not in r.stdout, r.stdout
    assert r.stdout.count("[KEY]") == 2 and FAKE_UUID in r.stdout, r.stdout
    # Tin gõ giữa lượt (queued_command) có trong lệnh user; task-notification bị bỏ.
    r = run(RECALL, "user", "84cabbc3-aaaa", "--since", "2026-10-19 19:06", "--until", "2026-10-19 19:06", *base)
    assert "[19/10 19:06] Lead (giữa lượt): nhớ đọc, review từng câu chữ" in r.stdout and "xong" not in r.stdout, r.stdout
    # Mặc định lệnh user không cắt tin; --width cắt và cảnh báo trên stderr.
    r = run(RECALL, "user", "84cabbc3-aaaa", "--grep", "CUỐI-TIN", *base)
    assert "CUỐI-TIN" in r.stdout and "cảnh báo" not in r.stderr, (r.stdout[-200:], r.stderr)
    r = run(RECALL, "user", "84cabbc3-aaaa", "--grep", "CUỐI-TIN", "--width", "600", *base)
    assert "CUỐI-TIN" not in r.stdout and "đã cắt 1 tin ở 600 ký tự" in r.stderr, r.stderr

    # Claude: che host, IP, JWT, hex; không in phần thinking.
    r = run(RECALL, "assistant", "84cabbc3-aaaa", *base, env={"STG_HOST": FAKE_HOST})
    out = r.stdout
    assert r.returncode == 0, r.stderr
    for leaked in (FAKE_HOST, FAKE_IP, FAKE_JWT, FAKE_HEX, "bỏ qua"):
        assert leaked not in out, (leaked, out)
    assert "[IP]" in out and "[JWT]" in out and "[HEX]" in out and "[ẨN]" in out, out

    # Tool: kết quả lớn chỉ in kích thước, BRAIN/journal bị ẩn, mật khẩu -u bị che.
    r = run(RECALL, "tools", "84cabbc3-aaaa", *base, env={"STG_HOST": FAKE_HOST})
    out = r.stdout
    assert "ok 200" in out and "curl -u [ẨN]" in out and "admin:matkhau" not in out and FAKE_HOST not in out, out
    assert "lớn hơn 4000, không in" in out and "dòng log dài" not in out, out[:600]
    assert "nội dung riêng tư" not in out and out.count("[bỏ: nhắc tới BRAIN/journal]") >= 1, out
    r = run(RECALL, "tools", "84cabbc3-aaaa", "--name", "^Bash$", "--results", "0", *base)
    assert r.stdout.count("->") == 1 and "ok 200" not in r.stdout

    # Phiên: liệt kê, che nội dung, tên phiên.
    r = run(RECALL, "sessions", "--limit", "5", *base)
    assert r.returncode == 0 and "84cabbc3" in r.stdout and "Workstream site-mau" in r.stdout and "7ecaa7b8" in r.stdout, r.stdout
    assert FAKE_KEY not in r.stdout

    # Lỗi dùng trả mã 2: tiền tố khớp nhiều phiên, phiên không có, thời gian sai, thư mục trống.
    r = run(RECALL, "user", "84cabbc3", *base)
    assert r.returncode == 2 and "khớp 2 phiên" in r.stderr, (r.returncode, r.stderr)
    assert run(RECALL, "user", "khongco", *base).returncode == 2
    assert run(RECALL, "user", "84cabbc3-aaaa", "--since", "hôm qua", *base).returncode == 2
    empty = d / "empty"
    empty.mkdir()
    assert run(RECALL, "sessions", "--projects-dir", str(empty)).returncode == 2

    # CLI handoff.py: stamp mặc định dry-run, --write sửa đè; lỗi trả mã khác 0.
    h = d / "HANDOFF.md"
    h.write_text("# H\n\n## Trạng thái\n\n01/01/2026: cũ.\n\n## Đã xong\n\n- a\n\n## Bước tiếp\n\n1. b\n\n## Chờ Lead quyết\n\n- c\n\n## Bẫy đã gặp\n\n- d\n", encoding="utf-8")
    env = {"HANDOFF_NOW": "2026-10-24 12:35"}
    before = h.read_text(encoding="utf-8")
    r = run(HANDOFF, "stamp", str(h), "--note", "Đang làm.", env=env)
    assert r.returncode == 0 and "24/10/2026 12:35: Đang làm." in r.stdout and h.read_text(encoding="utf-8") == before
    r = run(HANDOFF, "stamp", str(h), "--note", "Đang làm.", "--write", env=env)
    assert r.returncode == 0 and "24/10/2026 12:35: Đang làm." in h.read_text(encoding="utf-8")
    assert run(HANDOFF, "stamp", str(h), "--note", " ", env=env).returncode == 2
    h.write_text(before.replace("01/01/2026: cũ.", "24/10/2026: xong. Cập nhật 24/10 12:35."), encoding="utf-8")
    assert run(HANDOFF, "check", str(h), env=env).returncode == 1
    r = run(HANDOFF, "prompt", str(h), "--supersedes", "25/10/2026 09:00", env=env)
    assert r.returncode == 2 and "tương lai" in r.stderr
    assert run(HANDOFF, "limit", str(h), env=env).returncode == 1
    assert run(HANDOFF, "switch", str(h), "--account", "dich@example.com", env=env).returncode == 1
    print("OK transcript_recall và CLI")


if __name__ == "__main__":
    main()
