#!/bin/bash
# stg_deploy.sh <lane>  (stdin: tar của build/). Lint PHP, chuyển file trong MOVES.txt sang quarantine staging, chép file vào staging.
set -euo pipefail
LANE="$1"; U="${WORK_DIR:-/root/code-footprint}/$LANE/stg-up"; rm -rf "$U"; mkdir -p "$U"; tar -C "$U" -xf -
cd "$U"
while IFS= read -r f; do ${PHP_BIN:-php} -l "$f" >/dev/null || { echo "LOI PHP $f"; exit 1; }; done < <(find . -name '*.php')
S=$(ls -d ${STG_GLOB:?STG_GLOB} | head -1); W="$S/wp-content"
if [ -f MOVES.tsv ]; then while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; if [ -e "$W/$r" ]; then mkdir -p "${WORK_DIR:-/root/code-footprint}/$LANE/stg-quarantine/$(dirname "$r")"; rm -rf "${WORK_DIR:-/root/code-footprint}/$LANE/stg-quarantine/$r"; mv "$W/$r" "${WORK_DIR:-/root/code-footprint}/$LANE/stg-quarantine/$r"; echo "MOVED-STG $r"; else echo "ABSENT-STG $r"; fi; done < MOVES.tsv; fi
while IFS= read -r f; do case "$f" in EXPECT.tsv|MOVES.tsv|MOVES.txt|.DS_Store) continue;; esac; mkdir -p "$(dirname "$W/$f")"; cp "$f" "$W/$f"; chown ${WP_USER:-www}:${WP_USER:-www} "$W/$f"; echo "$(md5sum "$W/$f" | cut -c1-8) $f"; done < <(find . -type f | sed 's#^\./##')
echo "STG-DEPLOY-OK $LANE $(date +%H:%M:%S)"
