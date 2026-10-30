#!/bin/bash
# tests/run.sh — test offline cho loader hoãn GTM. Mã 0 khi mọi ca đạt.
# Kiểm bản sẽ cài: LOADER=<đường dẫn bản cài> bash tests/run.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
L="${LOADER:-$HERE/../templates/gtm-delay-loader-option.php}"
FAIL=0
php -l "$L" >/dev/null || FAIL=1
python3 -m py_compile "$HERE/../scripts/gtm_api.py" || FAIL=1
cd "$HERE"
for s in ok unknown now cleaned t7 nog badsnip admin cli container wait0; do
  if OUT="$(LOADER="$L" php harness.php "$s" 2>&1)"; then
    echo "$s: $(printf '%s\n' "$OUT" | grep -c '^ĐẠT') ca đạt"
  else
    echo "== $s"; printf '%s\n' "$OUT" | grep -v '^ĐẠT'; FAIL=1
  fi
done
exit $FAIL
