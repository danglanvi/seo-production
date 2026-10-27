#!/bin/bash
# regen.sh (wp-ucss, chạy trên máy local, launchd mỗi ngày theo mẫu templates/ucss-regen.plist): tái tạo CSS gọn khi file gộp của URL đã chọn đổi.
# Dùng: regen.sh --site <site.json> (hoặc biến UCSS_SITE). Thư mục làm việc = thư mục chứa site.json: chon/chon.tsv (chon_url.py), out-chon/, runs/.
# Chuỗi: quét URL đã chọn (m, d, p, q) → so md5 file gộp và path với lần trước → sinh cho cặp (path, biến thể) mới hoặc đổi file gộp
# → dựng → kiểm cặp đã sinh lại → make_map → nếu map đổi: deploy (DRY rồi thật) → purge LiteSpeed path đổi (12 path/lệnh) → làm nóng → purge CDN (trường cdn) đúng các URL đó.
# Lỗi ở bước nào thì dừng, map trên site giữ nguyên (trang không có trong map dùng file gốc). Log: runs/<ngày>/regen.log.
# Biến: DRY=1 (mặc định 0): chạy tới make_map, in việc sẽ làm, không ghi server. FORCE=1: sinh lại mọi cặp. MIN_URLS (mặc định 20): chon.tsv ít URL hơn thì dừng.
# Server cần sẵn trong remote_dir: deploy_ucss.sh (và mu-plugin cho lần cài đầu MU=1).
set -u
[ "${1:-}" = --site ] && UCSS_SITE=$2
SITE="$(cd "$(dirname "${UCSS_SITE:?thiếu --site <site.json> hoặc UCSS_SITE}")" && pwd)/$(basename "$UCSS_SITE")"; export UCSS_SITE="$SITE"
D="$(cd "$(dirname "$0")" && pwd)"
# cfg <khoá> [mặc định]: đọc một giá trị của site.json.
cfg() { python3 -I -c 'import json,sys
v = json.load(open(sys.argv[1])).get(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
sys.exit("site.json thiếu khoá " + sys.argv[2]) if v is None else print(v)' "$SITE" "$@"; }
cd "$(dirname "$SITE")"
W="$PWD"; R="$W/runs/$(date +%Y%m%d-%H%M)"; mkdir -p "$R"; exec > >(tee -a "$R/regen.log") 2>&1
DRY=${DRY:-0}; PL="$D/plock.sh"
WPS="$D/../../wp-pagespeed/scripts"
say() { echo "[$(date '+%F %T')] $*"; }
stop() { say "DỪNG: $*"; exit 1; }
HOST=$(cfg host) && SSH=$(cfg ssh) && DR=$(cfg docroot) && UD=$(cfg ucss_dir wp-content/ucss) && RD=$(cfg remote_dir) && PHPB=$(cfg php_bin) \
  && WU=$(cfg wp_user) && MUN=$(cfg mu_plugin ucss-swap.php) && CDN=$(cfg cdn none) && LK=$(cfg lock_file '~/.cm/locks/prod-http.lock') \
  && ML=$(cfg maint_lockdir '~/.cm/locks/_server-maint.lockdir') || stop "site.json thiếu khoá"
export PLOCK_FILE="${LK/#\~/$HOME}"; ML="${ML/#\~/$HOME}"
# Không chạy chồng việc bảo trì server (restart, nâng cấp) hay lane khác đang giữ khoá.
[ -d "$ML" ] && stop "$ML đang bị giữ"
say "bắt đầu, DRY=$DRY"

# 1. Danh sách URL: bộ đã chọn (chon/chon.tsv), 4 biến thể khách: m, d (Accept có WebP) và q, p (Accept */*, cũng là bản Googlebot).
# CDN giữ bản Accept của lượt đầu sau purge, nên cả 2 bản cần CSS gọn (site WordPress OLS + LiteSpeed Cache, 27/10/2026). URL đã bỏ khỏi site thì inventory ghi mã khác 200 và bị loại.
# Chờ khoá tối đa 900 giây ở mọi bước, như bản gốc: lane khác giữ khoá vài phút thì job vẫn chạy.
O=out-chon
tail -n +2 chon/chon.tsv | cut -f1 > "$R/all.txt"
[ "$(grep -c '^/' "$R/all.txt")" -ge "${MIN_URLS:-20}" ] || stop "chon.tsv quá ngắn"
bash "$PL" 900 3600 python3 -I "$D/inventory.py" "$R/all.txt" "$R/inv.jsonl" m,d,p,q || stop "quét URL lỗi"
python3 -I "$D/inv_summary.py" "$R/inv.jsonl" "$R/jobs.txt" || stop "tóm tắt lỗi"

# 2. Cặp cần sinh lại: chưa có kết quả, hoặc md5 file gộp khác lần trước.
python3 -I - "$R" <<'EOF' || exit 1
import json, os, sys, glob
R = sys.argv[1]
import re
slug = lambda p: (re.sub(r'[^\w-]+', '_', p.strip('/')) or 'home')[:120]
cur = {}
for l in open(f'{R}/inv.jsonl'):
    r = json.loads(l)
    if r.get('code') == 200 and len(set(r['css'])) == 1 and r.get('final', r['path']) == r['path']:
        cur[(r['path'], r['v'])] = r['css'][0]
redo = []
for (p, v), h in sorted(cur.items()):
    f = f'out-chon/pages/{v}_{slug(p)}.json'
    old = json.load(open(f)).get('hash') if os.path.exists(f) else None
    if old != h or os.environ.get('FORCE') == '1':
        redo.append(f'{p} {v}')
        for d in ('pages', 'verify'):
            g = f'out-chon/{d}/{v}_{slug(p)}.json'
            if os.path.exists(g): os.replace(g, g + '.cu')
open(f'{R}/jobs_redo.txt', 'w').write('\n'.join(redo) + ('\n' if redo else ''))
print('cặp cần sinh lại:', len(redo))
EOF
N=$(grep -c . "$R/jobs_redo.txt" || true)
if [ "$N" -gt 0 ]; then
  bash "$PL" 900 7200 node "$D/gen.mjs" "$R/jobs_redo.txt" $O 4 > "$R/gen.log" 2>&1 || stop "gen lỗi"
  node "$D/build.mjs" $O > "$R/build.log" 2>&1 || stop "build lỗi"
  # Kiểm lại mọi cặp dùng file gộp vừa dựng lại (file gọn đổi thì trang cũ cùng file cũng phải kiểm lại).
  python3 -I - "$R" <<'EOF' || exit 1
import json, glob, os, sys
R = sys.argv[1]
redo = set(tuple(l.split()) for l in open(f'{R}/jobs_redo.txt') if l.strip())
hs = set()
for f in glob.glob('out-chon/pages/*.json'):
    r = json.load(open(f))
    if (r['path'], r['dev']) in redo and r.get('hash'): hs.add(r['hash'])
jobs = []
for f in glob.glob('out-chon/pages/*.json'):
    r = json.load(open(f))
    if r.get('hash') in hs:
        jobs.append(f"{r['path']} {r['dev']}")
        v = f.replace('/pages/', '/verify/')
        if os.path.exists(v): os.replace(v, v + '.cu')
open(f'{R}/jobs_verify.txt', 'w').write('\n'.join(sorted(jobs)) + '\n')
print('cặp cần kiểm lại:', len(jobs), 'file gộp:', len(hs))
EOF
  bash "$PL" 900 7200 node "$D/verify.mjs" "$R/jobs_verify.txt" $O 4 > "$R/verify.log" 2>&1 || stop "verify lỗi"
fi

# 3. Map mới, so với map trên site.
UCSS_VER="$(date +%Y%m%d-%H%M)" python3 -I "$D/make_map.py" $O "$R/stage" | tee "$R/map.txt" || stop "make_map lỗi"
php -l "$R/stage/map.php" >/dev/null || stop "map.php lỗi cú pháp"
ssh -n -o BatchMode=yes "$SSH" "cat $DR/$UD/map.php 2>/dev/null" > "$R/map_site.php" 2>/dev/null
# Cổng mất path (MAX_LOST, mặc định 3) và danh sách purge: map_diff.py.
python3 -I "$D/map_diff.py" "$R/map_site.php" "$R/stage/map.php" "$R" || exit 1
NP=$(grep -c . "$R/purge_paths.txt" || true)
[ "$NP" -eq 0 ] && { say "map không đổi, xong"; exit 0; }
[ "$DRY" = 1 ] && { say "DRY: dừng trước khi ghi server ($NP path sẽ purge, CDN: $CDN)"; exit 0; }

# 4. Giao: chép stage lên server, deploy (DRY rồi thật), purge LiteSpeed, làm nóng. Giữ khoá production khi purge và làm nóng.
ST="$RD/stage-$(basename "$R")"
DENV="STAGE=$ST DOCROOT=$DR UCSS_DIR=$UD REMOTE_DIR=$RD PHP_BIN=$PHPB WP_USER=$WU MU_NAME=$MUN"
ssh -n -o BatchMode=yes "$SSH" "mkdir -p $ST" 2>/dev/null && scp -q "$R/stage/"*.css "$R/stage/map.php" "$SSH:$ST/" 2>/dev/null || stop "scp lỗi"
ssh -n -o BatchMode=yes "$SSH" "DRY=1 $DENV bash $RD/deploy_ucss.sh" 2>/dev/null | tee "$R/deploy_dry.txt" | grep -q "DRY: chưa ghi" || stop "deploy DRY không đạt"
ssh -n -o BatchMode=yes "$SSH" "DRY=0 $DENV bash $RD/deploy_ucss.sh" 2>/dev/null | tee "$R/deploy.txt" | grep -q "ghi map.php" || stop "deploy lỗi"
DRY=0 F="$R/purge-groups.txt" bash "$PL" 900 1800 bash "$D/purge_ucss.sh" > "$R/purge.txt" 2>&1
grep -q "đã chạy" "$R/purge.txt" || say "CẢNH BÁO: purge không in kết quả"
# Chỉ làm nóng 2 bản khách guest-d, guest-m: bản ret-* phải POST guest.vary.php lấy cookie, gấp đôi lượt gọi production.
bash "$PL" 900 3600 bash "$WPS/lam_nong.sh" --host "https://$HOST" -f "$R/purge_paths.txt" -V guest-d,guest-m -W both -s 1 -o "$R/warm.tsv" -q > "$R/warm.txt" 2>&1 \
  || say "CẢNH BÁO: làm nóng lỗi, xem $R/warm.txt"

# 5. Purge CDN (bước tuỳ chọn theo trường cdn của site.json), sau khi origin đã làm nóng.
# bunny: purge từng URL qua API (bunny_purge.py); site.json có cdn_host thì làm nóng ngay bằng bản WebP (Bunny giữ bản Accept của lượt đầu).
# none: không có CDN giữ HTML. Loại khác: chưa có nhánh, báo để purge tay.
case "$CDN" in
  bunny) WARM=$([ -n "$(cfg cdn_host '')" ] && echo --warm)
    python3 -I "$D/bunny_purge.py" "$R/purge_paths.txt" --apply $WARM > "$R/cdn.txt" 2>&1 || say "CẢNH BÁO: purge Bunny chưa đủ, xem $R/cdn.txt" ;;
  none) echo "không có CDN" > "$R/cdn.txt" ;;
  *) echo "chưa có nhánh purge cho CDN \"$CDN\"" > "$R/cdn.txt"; say "CẢNH BÁO: CDN \"$CDN\" chưa có nhánh purge, purge tay các path trong $R/purge_paths.txt" ;;
esac
say "xong: $NP path, $(tail -1 "$R/purge.txt"); CDN: $(tail -1 "$R/cdn.txt")"
