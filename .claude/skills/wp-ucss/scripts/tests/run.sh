#!/bin/bash
# run.sh (wp-ucss): chạy toàn bộ test offline. bash scripts/tests/run.sh → mã 0 khi mọi phần đạt.
# Module Node: UCSS_NODE_MODULES (mặc định ~/.cache/wp-ucss/node_modules, cần postcss + css-tree 3.x + puppeteer-core). Không gọi mạng.
# Chỉ test_combined_href.mjs mở Chrome headless (CHROME_BIN), mọi request trả tại chỗ. Máy không có Chrome thì phần đó BỎ.
set -u
T="$(cd "$(dirname "$0")" && pwd)"; S="$T/.."; K="$S/.."
export UCSS_NODE_MODULES="${UCSS_NODE_MODULES:-$HOME/.cache/wp-ucss/node_modules}"
# NODE_OPTIONS tách theo dấu cách: đường dẫn phải ở dạng file URL đã mã hoá.
export NODE_OPTIONS="--import=$(node -p 'require("url").pathToFileURL(process.argv[1]).href' "$T/_nonet.mjs")"
fail=0
part() { echo "== $1"; shift; "$@" || { fail=$((fail + 1)); echo "   -> phần này SAI"; }; }

syntax() {
  local bad=0 f
  for f in "$S"/*.mjs "$T"/*.mjs; do node --check "$f" || bad=1; done
  for f in "$S"/*.py "$T"/*.py; do python3 -I -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$f" || bad=1; done
  for f in "$S"/*.sh "$T"/*.sh; do bash -n "$f" || bad=1; done
  if command -v php >/dev/null; then for f in "$S"/*.php "$K"/templates/*.php "$T"/*.php; do php -l "$f" >/dev/null || bad=1; done; else echo "BỎ php -l: máy không có php"; fi
  for f in "$K"/templates/*.json; do python3 -I -m json.tool "$f" >/dev/null || bad=1; done
  [ $bad = 0 ] && echo "OK  cú pháp mjs, py, sh, php, json"
  return $bad
}
part "cú pháp" syntax
part "model.mjs (13 ca)" node "$T/test_model.mjs"
part "build.mjs hồi quy byte trên fixture" node "$T/test_build.mjs"
# Snapshot thật (tuỳ chọn): UCSS_SNAP=<pages, model, reduced> UCSS_SNAP_SITE=<site.json có cache_dir đủ file gộp>. Xem test_snapshot.mjs.
if [ -n "${UCSS_SNAP:-}" ]; then part "build.mjs hồi quy byte trên snapshot" node "$T/test_snapshot.mjs"; else echo "== snapshot: BỎ, chưa đặt UCSS_SNAP"; fi
part "biến thể m, d, g, p, q" node "$T/test_variants.mjs"
# regen.sh giữ các tham số của bản gốc: quét 4 biến thể khách, chờ khoá 900 giây, làm nóng chỉ 2 bản guest.
regen() {
  local f="$S/regen.sh" bad=0
  grep -q 'inv.jsonl" m,d,p,q' "$f" || { echo "SAI inventory không quét m,d,p,q"; bad=1; }
  grep -q 'lam_nong.sh" .* -V guest-d,guest-m ' "$f" || { echo "SAI lam_nong.sh thiếu -V guest-d,guest-m"; bad=1; }
  [ "$(grep -c 'bash "$PL" 900 ' "$f")" = 5 ] && ! grep -q 'bash "$PL" [0-8][0-9]* ' "$f" || { echo "SAI plock không chờ 900 giây ở đủ 5 chỗ"; bad=1; }
  [ $bad = 0 ] && echo "OK  regen.sh: m,d,p,q, -V guest-d,guest-m, chờ khoá 900 giây"
  return $bad
}
part "regen.sh" regen
# gen.mjs và verify.mjs đọc URL gốc trong onerror ở trang đã đổi sang CSS gọn (27/10/2026: thiếu nhánh này, hash null ở gen và 124 cặp bị bỏ qua ở verify).
# regen.sh dừng khi map mới mất quá MAX_LOST path (27/10/2026: map 130 → 70 path vẫn được giao).
genfb() {
  local bad=0 f
  grep -q "link\[rel=\"stylesheet\"\]\[onerror\]" "$S/lib-ucss.mjs" && grep -q "match(/href='(\[^'\]+)'/)" "$S/lib-ucss.mjs" || { echo "SAI lib-ucss.mjs thiếu combinedHref đọc onerror"; bad=1; }
  for f in gen.mjs verify.mjs; do grep -q "await combinedHref(p, CPATH)" "$S/$f" || { echo "SAI $f không dùng combinedHref"; bad=1; }; done
  grep -q 'map_diff.py" "$R/map_site.php" "$R/stage/map.php" "$R" || exit 1' "$S/regen.sh" || { echo "SAI regen.sh không gọi map_diff.py (cổng MAX_LOST)"; bad=1; }
  [ $bad = 0 ] && echo "OK  gen.mjs, verify.mjs đọc URL gốc trong onerror; regen.sh có cổng mất path"
  return $bad
}
part "gen.mjs, verify.mjs, cổng map" genfb
CH="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ -x "$CH" ]; then part "combinedHref trên Chrome (3 ca)" node "$T/test_combined_href.mjs"; else echo "== combinedHref: BỎ, máy không có Chrome"; fi
if command -v php >/dev/null; then part "mu-plugin (8 ca)" php "$T/test_mu.php"; else echo "== mu-plugin: BỎ, máy không có php"; fi
part "make_map.py" python3 -I "$T/test_make_map.py"
part "map_diff.py: cổng mất path (ca 27/10)" python3 -I "$T/test_map_diff.py"
part "qa_sau_giao.py" python3 -I "$T/test_qa_sau_giao.py"
part "chon_url.py" python3 -I "$T/test_chon_url.py"
# Không còn tên site, tên người, id CDN của site gốc trong skill (mẫu ghép chuỗi để file này không tự khớp).
names() { local hit; hit=$(grep -rIniE "g""tv|vin""cent|686""5439" "$K"); [ -z "$hit" ] && echo "OK  không còn tên site gốc" || { echo "$hit"; return 1; }; }
part "tên site gốc" names
echo "== kết quả: $([ $fail = 0 ] && echo 'mọi phần đạt' || echo "$fail phần SAI")"
exit $fail
