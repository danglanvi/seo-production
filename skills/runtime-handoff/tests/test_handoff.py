#!/usr/bin/env python3
"""Test offline cho check, stamp, prompt, switch, limit, night. Chạy: python3 -B tests/test_handoff.py"""
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import handoff as h  # noqa: E402

GOOD = """# HANDOFF: thử

## Trạng thái

19/10/2026: đang làm bước 2.

## Đã xong

- Bước 1: `out/a.md`.

## Bước tiếp

1. Làm bước 2.

## Chờ Lead quyết

- Publish bài lên site.

## Bẫy đã gặp

- zsh coi "?" là glob.
"""


def fill_night(t):
    t = t.replace("- (việc làm được khi mọi tool hỏi quyền bị chặn: đọc file, chạy script local, ghi vào thư mục workstream)", "- Soát lỗi chính tả trong `out/a.md`.")
    t = t.replace("- (dd/mm/yyyy HH:MM: giờ agent kiểm lại tiến độ)", "- 26/10/2026 01:30")
    t = t.replace("- (CronCreate chết cùng phiên. Liệt kê lịch kèm giờ, hoặc ghi: không có)", "- Không có")
    return t.replace("- (đường dẫn file heartbeat, agent ghi giờ vào đó sau mỗi việc)", "- `night/heartbeat.txt`")


def status_doc(status):
    return GOOD.replace("19/10/2026: đang làm bước 2.", status)


def test_stamp_and_time_checks(d):
    os.environ["HANDOFF_NOW"] = "2026-10-17 13:09"
    # Ca hỏng thật (phiên d61dfcca, 17/10): HANDOFF ghi mốc 13:20 lúc máy chỉ 13:09.
    f = d / "future.md"
    f.write_text(status_doc("17/10/2026 13:20: subagent trang chạy."), encoding="utf-8")
    r = h.check(f)
    assert any("tương lai" in e for e in r["errors"]), r
    # Trong ngưỡng 2 phút thì chấp nhận.
    f.write_text(status_doc("17/10/2026 13:10: subagent trang chạy."), encoding="utf-8")
    assert h.check(f)["errors"] == []
    # Ca hỏng thật (HANDOFF GTV-Website 24/10): mốc '24/10 12:35' thiếu năm.
    f.write_text(status_doc("17/10/2026: xong. Cập nhật 24/10 12:35 sau khi sửa."), encoding="utf-8")
    assert any("thiếu năm" in e for e in h.check(f)["errors"])
    # Mốc giờ tương lai trong 'Đã xong' chỉ cảnh báo.
    f.write_text(GOOD.replace("- Bước 1: `out/a.md`.", "- Bước 1 xong lúc 18/10/2026 09:00."), encoding="utf-8")
    r = h.check(f)
    assert r["errors"] == [] and any("tương lai" in w for w in r["warnings"]), r

    # stamp: mặc định dry-run, --write sửa đè một đoạn, không thêm dòng.
    g = d / "HANDOFF.md"
    before = g.read_text(encoding="utf-8")
    r = h.stamp(g, "Đang làm  bước 3.\nXong bước 2.")
    assert r["status_line"] == "17/10/2026 13:09: Đang làm bước 3. Xong bước 2." and not r["written"]
    assert g.read_text(encoding="utf-8") == before, "dry-run không được ghi"
    r = h.stamp(g, "Đang làm bước 3.", write=True)
    after = g.read_text(encoding="utf-8")
    assert r["written"] and r["check"]["errors"] == [] and "17/10/2026 13:09: Đang làm bước 3." in after
    assert "19/10/2026" not in after and len(after.splitlines()) == len(before.splitlines()), after
    assert after.count("## Trạng thái") == 1 and "## Đã xong" in after
    for bad in ["", "   "]:
        try:
            h.stamp(g, bad)
            raise AssertionError("note rỗng phải lỗi")
        except ValueError:
            pass

    # Ca hỏng thật (phiên 06e8cc9a, 26/10): stamp xoá dòng `Lane:` của lane đang chạy ít nhất 4 lần.
    lane = "Lane: cs-css-stable giữ CSS gộp · phiên 06e8cc9a · run wf_3acc68af-b46"
    g.write_text(status_doc(f"19/10/2026: đang làm bước 2.\n\n{lane}\n- Lane: cs-rum-gtm giữ GTM"), encoding="utf-8")
    r = h.stamp(g, "Lane CSS đang chạy.", write=True)
    after = g.read_text(encoding="utf-8")
    assert r["lanes_kept"] == 2 and lane in after and "- Lane: cs-rum-gtm giữ GTM" in after, after
    assert after.index("17/10/2026 13:09: Lane CSS đang chạy.") < after.index(lane) < after.index("## Đã xong")
    r = h.stamp(g, "Đóng đợt.", write=True, drop_lanes=True)
    after = g.read_text(encoding="utf-8")
    assert r["lanes_kept"] == 0 and "Lane:" not in after and r["check"]["errors"] == [], after


def test_status_length_and_resume(d):
    os.environ["HANDOFF_NOW"] = "2026-10-21 17:00"
    f = d / "resume.md"
    # Ca hỏng thật (e297d7d3, 21/10): HANDOFF ghi resume wf_ và Trạng thái dài.
    long = "21/10/2026 16:12: Một. Hai. Ba. Bốn câu."
    f.write_text(status_doc(long).replace("1. Làm bước 2.", "1. Chạy resume wf_d6b56376-f91 cho lô 2."), encoding="utf-8")
    r = h.check(f)
    assert any("3 câu" in w for w in r["warnings"]) and any("resume" in w for w in r["warnings"]), r
    f.write_text(status_doc("21/10/2026 16:12: resumeFromRunId đã dùng.").replace("1. Làm bước 2.", "1. Chạy lại."), encoding="utf-8")
    assert any("resume" in w for w in h.check(f)["warnings"])


def test_prompt_supersedes(d):
    os.environ["HANDOFF_NOW"] = "2026-10-19 21:00"
    g = d / "HANDOFF.md"
    g.write_text(GOOD.replace("## Bước tiếp", "## Quyết định đã chốt\n\n- Bám Koray, không đổi concept ảnh.\n\n## Bước tiếp"), encoding="utf-8")
    (d / "decisions.md").write_text("x", encoding="utf-8")
    p = h.prompt(g, "claude", "", "19/10/2026 19:30")
    assert p.startswith("Prompt này thay prompt gửi lúc 19/10/2026 19:30."), p
    assert "Giờ máy lúc tạo prompt: 19/10/2026 21:00" in p and "Bám Koray" in p and "decisions.md" in p and "tiếng Việt có dấu" in p
    assert "Thay prompt" not in h.prompt(g, "claude", "")
    for bad in ["hôm qua", "19/10 19:30", "20/10/2026 09:00"]:
        try:
            h.prompt(g, "claude", "", bad)
            raise AssertionError("supersedes sai phải lỗi: " + bad)
        except ValueError:
            pass


def test_switch(d):
    os.environ["HANDOFF_NOW"] = "2026-10-20 12:00"
    root = d / "repo"
    (root / "ws/_tools").mkdir(parents=True)
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    (root / "ws/wf.js").write_text("// script", encoding="utf-8")
    g = root / "ws/HANDOFF.md"
    g.write_text(status_doc("20/10/2026 11:55: đổi tài khoản."), encoding="utf-8")
    outside = d / "wf_tmp.js"
    outside.write_text("// script", encoding="utf-8")
    url = "https://claude.ai/artifact/AbC123xyz"
    text, errs = h.switch(g, "dich@example.com", [url + "@v3"], [str(root / "ws/wf.js")])
    assert errs == [] and "dich@example.com" in text and url in text and "version v3" in text and "artifact-account-migration" in text, errs
    assert "tools/wf-status.py slots " in text, "wf-status cần lệnh con slots"
    # Ca hỏng thật (20/10): script workflow còn ở thư mục tạm, mất khi đổi tài khoản.
    _, errs = h.switch(g, "dich@example.com", [url], [str(outside)])
    assert any("ngoài repo" in e for e in errs), errs
    _, errs = h.switch(g, "dich@example.com", ["http://evil.example/x"], [])
    assert any("URL artifact" in e for e in errs)
    g.write_text(status_doc("hôm nay: sai."), encoding="utf-8")
    _, errs = h.switch(g, "dich@example.com", [], [])
    assert any(e.startswith("HANDOFF:") for e in errs)


def test_limit(d):
    os.environ["HANDOFF_NOW"] = "2026-10-20 11:30"
    g = d / "lim" / "HANDOFF.md"
    (d / "lim/lane-a").mkdir(parents=True)
    g.write_text(status_doc("20/10/2026 11:25: sắp hết usage."), encoding="utf-8")
    sess = d / "lim/sess"
    live, dead = sess / "subagents/workflows/wf_live", sess / "subagents/workflows/wf_dead"
    for run in (live, dead):
        run.mkdir(parents=True)
        (run / "journal.jsonl").write_text("{}\n", encoding="utf-8")
        (run / "agent-a1.jsonl").write_text("{}\n", encoding="utf-8")
    old = time.time() - 3 * 3600
    for f in dead.iterdir():
        os.utime(f, (old, old))
    r = h.limit(g, str(sess), [str(d / "lim/lane-a")])
    runs = {x["run"]: x for x in r["runs"]}
    assert runs["wf_live"]["live"] and not runs["wf_dead"]["live"] and runs["wf_live"]["agents"] == 1, r
    assert not (d / "lim/lane-a/inbox.md").exists(), "dry-run không được ghi inbox"
    r = h.limit(g, str(sess), [str(d / "lim/lane-a")], write=True)
    inbox = (d / "lim/lane-a/inbox.md").read_text(encoding="utf-8")
    assert "20/10/2026 11:30 Lệnh checkpoint (sắp hết hạn mức)" in inbox and "Không ghi production" in inbox
    r = h.limit(g, str(sess), [str(d / "lim/lane-a")], write=True)
    assert "chưa trả lời" in r["inbox"][0]["action"] and inbox == (d / "lim/lane-a/inbox.md").read_text(encoding="utf-8")
    ib = d / "lim/lane-a/inbox.md"
    ib.write_text(ib.read_text(encoding="utf-8") + "- Đã checkpoint lúc 11:40\n", encoding="utf-8")
    assert h.limit(g, str(sess), [str(d / "lim/lane-a")], write=True)["inbox"][0]["action"] == "ghi"
    assert ib.read_text(encoding="utf-8").count(h.LIMIT_MARK) == 2
    try:
        h.limit(g, None, [str(d / "khong-co")])
        raise AssertionError("lane không tồn tại phải lỗi")
    except ValueError:
        pass


def test_night_lint(d):
    os.environ["HANDOFF_NOW"] = "2026-10-18 22:00"
    n = d / "nightlint"
    h.night_init(n, "Chạy đêm 18/10")
    plan = n / "PLAN.md"
    base = fill_night(plan.read_text(encoding="utf-8"))
    base = base.replace("- (đọc, sửa file trong thư mục nào, chạy lệnh nào, ghi staging nào)", "- Sửa file trong `out/`.")
    base = base.replace("- [ ] (việc 1: tiêu chí xong)", "- [ ] Việc A: test pass")
    base = base.replace("26/10/2026 01:30", "18/10/2026 23:30")
    plan.write_text(base, encoding="utf-8")
    assert h.night_check(plan)["errors"] == [], h.night_check(plan)
    # Ca hỏng thật (đêm 18 sang 19/10): Hàng việc gọi ArtifactData và Monitor có $( rồi treo 500 phút.
    risky = base.replace("- [ ] Việc A: test pass", "- [ ] Nạp thẻ bằng ArtifactData batch\n- [ ] Chờ bằng Monitor until $(test -f done)\n- [ ] Publish artifact báo cáo\n- [ ] Launch Workflow lô 3")
    plan.write_text(risky, encoding="utf-8")
    errs = h.night_check(plan)["errors"]
    names = " ".join(errs)
    assert all(k in names for k in ["ArtifactData", "Monitor có $(", "Artifact publish", "launch Workflow"]), errs
    # Có dòng 'Đã thử lúc ... khi Lead còn thức' thì bỏ qua lint này.
    plan.write_text(risky + "\n- Đã thử lúc 21:40 khi Lead còn thức: ArtifactData batch chạy được.\n", encoding="utf-8")
    assert h.night_check(plan)["errors"] == [], h.night_check(plan)
    # Câu cấm không bị tính nhầm.
    plan.write_text(base.replace("- [ ] Việc A: test pass", "- [ ] Việc A: test pass. Không gọi ArtifactData."), encoding="utf-8")
    assert h.night_check(plan)["errors"] == []
    # Việc local-only không được gọi tool hỏi quyền, kể cả khi có dòng 'Đã thử lúc'.
    bad_local = base.replace("- Soát lỗi chính tả trong `out/a.md`.", "- Ghi ArtifactData vào db.") + "\n- Đã thử lúc 21:40 khi Lead còn thức.\n"
    plan.write_text(bad_local, encoding="utf-8")
    assert any("local-only" in e for e in h.night_check(plan)["errors"])
    # Thiếu mục mới, mốc giờ thiếu năm, lịch không có giờ, heartbeat còn chữ mẫu.
    plan.write_text(base.replace("## Heartbeat\n- `night/heartbeat.txt`\n", ""), encoding="utf-8")
    assert "thiếu mục 'Heartbeat'" in h.night_check(plan)["errors"]
    plan.write_text(base.replace("- 18/10/2026 23:30", "- 18/10 23:30").replace("- Không có", "- Cron V1-8 chạy sau"), encoding="utf-8")
    errs = " ".join(h.night_check(plan)["errors"])
    assert "Giờ kiểm kế tiếp" in errs and "Lịch đang sống" in errs, errs
    plan.write_text(base.replace("- 18/10/2026 23:30", "- 18/10/2026 21:00"), encoding="utf-8")
    r = h.night_check(plan)
    assert r["errors"] == [] and any("đã qua" in w for w in r["warnings"]), r


def main():
    d = Path(tempfile.mkdtemp())
    (d / "out").mkdir()
    (d / "out/a.md").write_text("x")
    f = d / "HANDOFF.md"
    f.write_text(GOOD, encoding="utf-8")
    r = h.check(f)
    assert r["errors"] == [] and r["warnings"] == [], r

    bad = d / "bad.md"
    bad.write_text(GOOD.replace("19/10/2026", "hôm nay").replace("## Đã xong", "## Xong") + "\n" * 60 + "`out/khong-co.md`\n", encoding="utf-8")
    r = h.check(bad)
    assert any("quá 60" in e for e in r["errors"]) and any("Đã xong" in e for e in r["errors"]) and any("ngày" in e for e in r["errors"]), r
    assert r["warnings"] == ["không thấy file: out/khong-co.md"], r

    p = h.prompt(f, "codex", "Không dùng sub-agent.")
    assert "Publish bài lên site." in p and "Làm bước 2." in p and "AGENTS.md" in p and "CLAUDE.md" not in p, p

    n = d / "night"
    h.night_init(n, "Thử đêm")
    plan = n / "PLAN.md"
    assert h.night_check(plan)["errors"], "mẫu chưa điền phải lỗi"
    t = plan.read_text(encoding="utf-8")
    t = t.replace("- (đọc, sửa file trong thư mục nào, chạy lệnh nào, ghi staging nào)", "- Sửa file trong `skills/`.")
    t = t.replace("- [ ] (việc 1: tiêu chí xong)", "- [x] Việc A: test pass\n- [x] Việc B: lint 0\n- [ ] Việc C: sync")
    t = fill_night(t)
    t = t.replace("## Chờ Lead\n", "## Chờ Lead\n- Xoá file cũ?\n")
    t += "- 01:10 Việc A: test pass, `tests/a.txt`\n"
    plan.write_text(t, encoding="utf-8")
    assert h.night_check(plan)["errors"] == [], h.night_check(plan)
    text, missing = h.night_report(plan)
    assert "Xong 2/3" in text and missing == 1 and "Việc B: lint 0 (THIẾU dòng nhật ký" in text and "Xoá file cũ?" in text, text
    try:
        h.night_init(n, "lần 2")
        raise AssertionError("phải từ chối ghi đè PLAN.md")
    except ValueError:
        pass
    for fn in [test_stamp_and_time_checks, test_status_length_and_resume, test_prompt_supersedes, test_switch, test_limit, test_night_lint]:
        sub = d / fn.__name__
        sub.mkdir()
        (sub / "out").mkdir()
        (sub / "out/a.md").write_text("x")
        (sub / "HANDOFF.md").write_text(GOOD, encoding="utf-8")
        try:
            fn(sub)
        finally:
            os.environ.pop("HANDOFF_NOW", None)
    print("OK 10 nhóm kiểm")


if __name__ == "__main__":
    main()
