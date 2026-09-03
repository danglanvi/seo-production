#!/usr/bin/env python3
"""content_sync.py — đấu nối SEO Production ↔ fork Content Production (Python stdlib, chạy trong instance).

  python3 tools/content_sync.py --fork "../Content Production - <client>"            # → 05-content-plan/content-tracking/content-status.md
  python3 tools/content_sync.py --fork "<fork>" --pull-delivered                     # + copy bài humanized/published-gdoc → content-tracking/delivered/<slug>.md

Đọc `index.md` (bảng có cột slug + status), `log.md` (ngày đổi status gần nhất), `08-humanized/**/<slug>.md`, `09-publish-gdoc/**/<slug>.md` của fork. Không ghi gì vào fork.
"""
from __future__ import annotations

import argparse, datetime as dt, re, shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["planned", "researched", "outlined", "drafted", "verified", "briefed", "humanized", "published-gdoc", "archived", "updating", "updated", "republished-gdoc"]


def read_index(fork: Path):
    rows, hdr = [], None
    for line in (fork / "index.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            hdr = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if hdr is None:
            if "slug" in low and "status" in low:
                hdr = low
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            continue
        r = dict(zip(hdr, cells))
        st = r.get("status", "").strip("`")
        r["status_key"] = re.split(r"[\s(]", st, 1)[0].lower() if st else ""
        rows.append(r)
    return rows


def last_touch(fork: Path):
    """slug → ngày cuối xuất hiện trong log.md (heading ## [YYYY-MM-DD] …)."""
    out, cur = {}, None
    p = fork / "log.md"
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s*\[(\d{4}-\d{2}-\d{2})\]", line)
        if m:
            cur = dt.date.fromisoformat(m.group(1))
            continue
        if cur:
            for slug in re.findall(r"\b(\d{6}-[a-z0-9-]+)", line):
                if slug not in out or out[slug] < cur:
                    out[slug] = cur
    return out


def find_file(fork: Path, slug: str, phase: str):
    return next(iter(sorted((fork / phase).glob(f"**/{slug}.md"))), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", required=True)
    ap.add_argument("--pull-delivered", action="store_true")
    ap.add_argument("--stuck-days", type=int, default=14)
    a = ap.parse_args()
    fork = Path(a.fork).expanduser().resolve()
    if not (fork / "index.md").exists():
        raise SystemExit(f"không thấy index.md trong {fork}")
    out_dir = ROOT / "05-content-plan" / "content-tracking"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, touch = read_index(fork), last_touch(fork)
    today = dt.date.today()
    cnt = Counter(r["status_key"] for r in rows)
    by_cluster = defaultdict(Counter)
    for r in rows:
        by_cluster[r.get("cluster", "")][r["status_key"]] += 1
    stuck = [(r, touch.get(r["slug"])) for r in rows if r["status_key"] not in ("planned", "archived", "published-gdoc") and touch.get(r["slug"]) and (today - touch[r["slug"]]).days >= a.stuck_days]
    ready = [r for r in rows if r["status_key"] in ("humanized", "published-gdoc", "republished-gdoc")]

    L = [f"# Content status — fork `{fork.name}` — {today.isoformat()}", "", "> Sinh tự động bởi `tools/content_sync.py`. Không sửa tay. Số này ghi vào % mốc dòng #15/#16/#19 `index.md`.", "",
         f"**Tổng {len(rows)} bài.** " + " · ".join(f"{s}: {cnt[s]}" for s in ORDER if cnt.get(s)) + (f" · khác: {sum(v for k, v in cnt.items() if k not in ORDER)}" if any(k not in ORDER for k in cnt) else ""), "",
         "## Theo cluster", "", "| cluster | tổng | " + " | ".join(ORDER[:9]) + " |", "|---|---|" + "---|" * 9]
    for c, cc in sorted(by_cluster.items()):
        L.append(f"| {c} | {sum(cc.values())} | " + " | ".join(str(cc.get(s, "")) for s in ORDER[:9]) + " |")
    L += ["", f"## Bài kẹt ≥{a.stuck_days} ngày (theo log.md fork)", ""]
    L += [f"- `{r['slug']}` — {r['status_key']} — lần chạm cuối {d.isoformat()} ({(today - d).days} ngày)" for r, d in stuck] or ["- không có (hoặc log.md chưa ghi slug)"]
    L += ["", "## Sẵn sàng cho WS06 (humanized / published-gdoc)", "", "| slug | title | status | file humanized | Google Doc |", "|---|---|---|---|---|"]
    for r in ready:
        hf = find_file(fork, r["slug"], "08-humanized")
        url = r.get("published url", "")
        L.append(f"| {r['slug']} | {r.get('title', '')[:70]} | {r['status_key']} | {hf.relative_to(fork) if hf else '—'} | {url if url.startswith('http') else '—'} |")
    if not ready:
        L.append("| — | | | | |")
    (out_dir / "content-status.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"✓ {out_dir / 'content-status.md'} — {len(rows)} bài · kẹt {len(stuck)} · sẵn sàng {len(ready)}")

    if a.pull_delivered:
        dd = out_dir / "delivered"
        dd.mkdir(exist_ok=True)
        n = 0
        for r in ready:
            src = find_file(fork, r["slug"], "08-humanized") or find_file(fork, r["slug"], "09-publish-gdoc")
            if src:
                shutil.copy2(src, dd / f"{r['slug']}.md")
                n += 1
        print(f"✓ delivered/: {n} file (bản để onpage/đăng — sửa ở fork rồi sync lại)")


if __name__ == "__main__":
    main()
