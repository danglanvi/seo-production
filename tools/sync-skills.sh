#!/bin/bash
# sync-skills.sh — Đồng bộ skill canonical → 2 runtime mirror (bản STANDALONE, bash thuần)
#
# Dùng khi folder này chạy TÁCH KHỎI workspace Vincent (team clone/tải từ Drive):
#   bash tools/sync-skills.sh
#
# Luật: skills/ là nguồn duy nhất. KHÔNG sửa tay .claude/skills/ hoặc .agents/skills/ —
# sửa skills/<tên>/... xong chạy script này để 2 mirror nhận bản mới.
# (Trong workspace Vincent, Lead vẫn dùng tools/sync-agent-skills.rb ở root như cũ —
#  script đó đọc skills/manifest.yaml; script này là bản rút gọn cho standalone.)
#
# 2 skill CLAUDE-ONLY (không copy sang .agents/ cho Codex/Antigravity):
#   gtv-client-report · gtv-weekly-report

set -euo pipefail
cd "$(dirname "$0")/.."

CLAUDE_ONLY=("gtv-client-report" "gtv-weekly-report")

if [ ! -d "skills" ]; then
  echo "LỖI: không thấy folder skills/ — chạy script từ trong folder SEO Production." >&2
  exit 1
fi

echo "== Đồng bộ skills/ → .claude/skills/ (đủ 100%) =="
rsync -a --delete --exclude ".DS_Store" skills/ .claude/skills/

echo "== Đồng bộ skills/ → .agents/skills/ (trừ skill claude-only) =="
RSYNC_ARGS=(-a --delete --exclude ".DS_Store")
for s in "${CLAUDE_ONLY[@]}"; do RSYNC_ARGS+=(--exclude "/$s/"); done
rsync "${RSYNC_ARGS[@]}" skills/ .agents/skills/

echo ""
echo "== Kiểm tra parity =="
N_SRC=$(find skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
N_CLAUDE=$(find .claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
N_AGENTS=$(find .agents/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
DIFF_CLAUDE=$(diff -rq skills .claude/skills 2>/dev/null | wc -l | tr -d ' ')
echo "skills/: $N_SRC · .claude/skills/: $N_CLAUDE (lệch nội dung: $DIFF_CLAUDE — phải là 0)"
echo ".agents/skills/: $N_AGENTS (= $N_SRC − ${#CLAUDE_ONLY[@]} skill claude-only)"

if [ "$DIFF_CLAUDE" != "0" ] || [ "$N_CLAUDE" != "$N_SRC" ]; then
  echo "CẢNH BÁO: mirror .claude/skills chưa khớp canonical — xem diff ở trên." >&2
  exit 2
fi
echo "OK — mirror đồng bộ. Nhớ commit cả 3 nơi (skills/ + 2 mirror) cùng lúc."
