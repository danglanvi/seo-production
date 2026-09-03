#!/usr/bin/env python3
"""migrate_v2026_09_3.py — đưa instance lên master v2026.09.3 (idempotent, stdlib).

  python3 "SEO Production/tools/migrate_v2026_09_3.py" "PROJECTS/<client>"   [--dry]

Làm: (1) copy folder/template/skill/README/cheat-sheet MỚI (không đè deliverable, đè infra nhóm A: root luật, _REFERENCE, _TEMPLATES, knowledge, skills, README/CLAUDE/AGENTS trạm, tools);
(2) index.md instance: append 3 dòng #34–36 + 2 dòng bảng C, đổi tiêu đề bảng B (chỉ khi chưa có); (3) MIGRATION.md frontmatter master_version; (4) append log.md op `migrate`.
"""
from __future__ import annotations

import datetime as dt, re, shutil, sys
from pathlib import Path

MASTER = Path(__file__).resolve().parents[1]
GROUP_A = ["CLAUDE.md", "AGENTS.md", "AGENT.md", "README.md", "MIGRATION.md", "ORCHESTRATOR.md", "COMMANDS.md", "SETUP.md", "SYNC.md",
           "_REFERENCE", "_TEMPLATES", "02-raw/knowledge", "skills", ".claude/skills", ".agents/skills", "tools",
           "13-cro/README.md", "13-cro/CLAUDE.md", "13-cro/AGENTS.md", "14-entity/README.md", "14-entity/CLAUDE.md", "14-entity/AGENTS.md"]
WS_INFRA = ["README.md", "CLAUDE.md", "AGENTS.md"]
NEW_DIRS = ["13-cro", "03-audits/technical", "03-audits/content", "03-audits/entity", "03-audits/offsite", "03-audits/full",
            "05-content-plan/keyword-research", "05-content-plan/content-tracking/delivered", "14-entity", "02-raw/seo-data/keywords"]
ROWS_B = [l for l in (MASTER / "index.md").read_text(encoding="utf-8").splitlines() if re.match(r"^\| 3[456] \|", l)]
ROWS_C = [l for l in (MASTER / "index.md").read_text(encoding="utf-8").splitlines() if l.startswith("| CRO (WS13") or l.startswith("| Content tracking (WS05")]


def copy(src: Path, dst: Path, dry):
    if src.is_dir():
        if not dry:
            shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    inst = Path(sys.argv[1]).resolve()
    dry = "--dry" in sys.argv
    if not (inst / "index.md").exists():
        raise SystemExit(f"{inst} không phải instance (thiếu index.md)")
    done = []
    for rel in GROUP_A:
        src = MASTER / rel
        if src.exists():
            copy(src, inst / rel, dry)
            done.append(f"đè {rel}")
    for ws in sorted(p for p in MASTER.iterdir() if re.match(r"^\d\d-", p.name)):
        for f in WS_INFRA:
            if (ws / f).exists():
                copy(ws / f, inst / ws.name / f, dry)
        for sub in ws.rglob("README.md"):
            rel = sub.relative_to(MASTER)
            copy(sub, inst / rel, dry)
    for d in NEW_DIRS:
        if not dry:
            (inst / d).mkdir(parents=True, exist_ok=True)
    done.append(f"thêm {len(NEW_DIRS)} folder mới + README trạm/subfolder")
    # dọn folder entity cũ trong WS06 (bản sáng 03/09 chỉ có README, không có deliverable)
    old_entity = inst / "06-onpage-internal-link" / "entity"
    if old_entity.is_dir():
        leftovers = [f for f in old_entity.iterdir() if f.name != "README.md"]
        if leftovers:
            done.append(f"⚠ giữ {old_entity.name}/ vì còn {len(leftovers)} file — Lead dời tay sang 14-entity/")
        elif not dry:
            for f in old_entity.iterdir():
                f.unlink()
            old_entity.rmdir()
            done.append("xoá 06-onpage-internal-link/entity/ rỗng → 14-entity/")
    # index.md
    idx = inst / "index.md"
    txt = idx.read_text(encoding="utf-8")
    if "| 34 |" not in txt:
        lines = txt.splitlines()
        last33 = max(i for i, l in enumerate(lines) if re.match(r"^\| 33 \|", l))
        lines[last33 + 1:last33 + 1] = ROWS_B
        txt = "\n".join(lines) + "\n"
        done.append("index.md: +#34–36")
    if "| CRO (WS13" not in txt and "| Content refresh (WS03" in txt:
        txt = re.sub(r"(\| Content refresh \(WS03[^\n]*\n)", lambda m: m.group(1) + "\n".join(ROWS_C) + "\n", txt, count=1)
        done.append("index.md: bảng C +2 dòng")
    txt = txt.replace("## B. Bảng 33 công đoạn", "## B. Bảng 36 công đoạn (33 gốc + #34–36 CRO từ v2026.09.3)")
    txt2 = re.sub(r"^(\| 13 \|[^|]*\|[^|]*\|) 06 \|", r"\1 14 |", txt, flags=re.M)
    if txt2 != txt:
        txt = txt2
        done.append("index.md: #13 WS 06 → 14")
    if not dry:
        idx.write_text(txt, encoding="utf-8")
    mg = inst / "MIGRATION.md"
    if mg.exists() and not dry:
        mg.write_text(re.sub(r"master_version:\s*\S+", "master_version: v2026.09.3", mg.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    log = inst / "log.md"
    if log.exists() and not dry:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(f"\n## [{dt.date.today().isoformat()}] migrate | master v2026.09.3 — WS 13 CRO (#34–36) + WS 14 Entity (#13 chuyển từ WS 06), keyword-research, content-tracking, audit lẻ — @claude\n\n- " + "\n- ".join(done) + "\n- Lead dời tay file audit/keyword research cũ vào folder mới (op `move`).\n")
    print(("DRY " if dry else "") + f"✓ {inst.name}: " + " · ".join(done))


if __name__ == "__main__":
    main()
