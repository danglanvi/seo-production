#!/bin/bash
# sync-skills.sh — dựng lại 2 runtime mirror từ skills/ (bản STANDALONE, bash thuần).
#
# Dùng khi repo này chạy TÁCH KHỎI workspace Vincent (team clone từ GitHub):
#     bash _SETUP/sync-skills.sh
#
# Trong workspace Vincent thì vẫn dùng `ruby tools/sync-agent-skills.rb` ở root như cũ —
# script đó đọc skills/manifest.yaml và quản cả 11 repo cùng lúc. Script này là bản rút gọn
# cho clone standalone, nơi không có tools/ của workspace.
#
# Luật không đổi: skills/ là nguồn duy nhất. KHÔNG sửa tay .claude/skills/ hay .agents/skills/.
#
# Danh sách skill claude-only (không copy sang .agents/) được SUY RA từ hiện trạng: skill nào
# đang có trong skills/ mà không có trong .agents/skills/ thì giữ nguyên tình trạng đó. Nhờ vậy
# script chạy đúng cho mọi repo mà không cần cấu hình riêng.

set -euo pipefail
cd "$(dirname "$0")/.."

[ -d skills ] || { echo "LỖI: không thấy folder skills/ — chạy từ root repo." >&2; exit 1; }

EXCLUDES=()
if [ -d .agents/skills ]; then
  while IFS= read -r name; do
    [ -d ".agents/skills/$name" ] || EXCLUDES+=("$name")
  done < <(find skills -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
fi

echo "== skills/ → .claude/skills/ (đủ 100%) =="
mkdir -p .claude/skills
rsync -a --delete --exclude ".DS_Store" skills/ .claude/skills/

echo "== skills/ → .agents/skills/ =="
if [ ${#EXCLUDES[@]} -gt 0 ]; then
  echo "   giữ nguyên ${#EXCLUDES[@]} skill claude-only: ${EXCLUDES[*]}"
fi
mkdir -p .agents/skills
ARGS=(-a --delete --exclude ".DS_Store")
for name in ${EXCLUDES[@]+"${EXCLUDES[@]}"}; do ARGS+=(--exclude "/$name/"); done
rsync "${ARGS[@]}" skills/ .agents/skills/

N_SRC=$(find skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
N_CLAUDE=$(find .claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
N_AGENTS=$(find .agents/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
DIFF=$(diff -rq skills .claude/skills 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "skills/: $N_SRC · .claude/skills/: $N_CLAUDE (lệch nội dung: $DIFF — phải là 0)"
echo ".agents/skills/: $N_AGENTS (= $N_SRC − ${#EXCLUDES[@]} skill claude-only)"

if [ "$DIFF" != "0" ] || [ "$N_CLAUDE" != "$N_SRC" ]; then
  echo "CẢNH BÁO: .claude/skills chưa khớp canonical — xem diff ở trên." >&2
  exit 2
fi
echo "OK — mirror đồng bộ. Commit cả 3 nơi (skills/ + 2 mirror) cùng lúc."
