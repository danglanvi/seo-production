#!/bin/bash
# Áp một khối cấu hình vào file sống trên server (.htaccess hoặc vhost) theo cách idempotent, có backup, có kiểm hồi quy và rollback tự sinh.
#
# Dùng:
#   apply_server_block.sh --alias <ssh alias> --target htaccess|vhost --remote-file <đường dẫn trên server> \
#       --block <file khối> --mark <nhãn> --site-url <https://domain> [tuỳ chọn]
#
# Mặc định là DIỄN TẬP: đọc server, in diff và kế hoạch, không ghi gì. Thêm --apply để ghi thật.
#
# Tuỳ chọn:
#   --probes FILE        Dòng "mã-mong-đợi path" như exposure_default.txt. Sau khi áp, mọi dòng phải đạt.
#   --paths FILE         Mỗi dòng một path hồi quy. Mã HTTP trước và sau phải giống nhau.
#                        Mặc định: /  /wp-login.php  /wp-admin/admin-ajax.php
#                        Không đưa path mà khối này cố ý đổi mã (ví dụ /readme.html) vào đây, hãy đưa vào --probes.
#   --staging 0|1        1: site staging có Basic Auth. Đặt STAGING_AUTH="user:pass" trong môi trường. Mặc định 0.
#   --restart 0|1        1: chạy lệnh restart sau khi ghi. OpenLiteSpeed cần restart để nhận .htaccess và vhost. Mặc định 0.
#   --restart-cmd CMD    Mặc định /usr/local/lsws/bin/lswsctrl restart. Chỉ restart giờ thấp điểm hoặc khi người duyệt cho phép.
#   --check-cmd CMD      Lệnh kiểm cú pháp chạy trên server, {FILE} là file mới. Thất bại thì không ghi.
#   --position top|bottom  Chỗ chèn khi chưa có khối. Mặc định top cho htaccess, bottom cho vhost.
#   --after ERE          Chèn sau dòng đầu tiên khớp biểu thức này. Ưu tiên hơn --position.
#   --backup-root DIR    Backup về máy làm việc. Mặc định $HOME/Backups.
#   --remote-backup-root DIR  Backup trên server. Mặc định /root.
#   --wait SEC           Chờ sau restart rồi mới đo lại. Mặc định 3.
#   --no-auto-rollback   Khi có hồi quy, chỉ báo, không tự rollback.
#   --apply              Ghi thật.
#   -h, --help           In trợ giúp này.
#
# Khối được bọc bằng dòng "# BEGIN <nhãn> (<ngày>)" và "# END <nhãn>". Chạy lại với cùng nhãn:
#   nội dung giống thì không làm gì; nội dung khác thì thay đúng khối đó.
#
# Biến môi trường: SSH_CMD (mặc định "ssh -o BatchMode=yes -o ConnectTimeout=15"), STAGING_AUTH.
#
# Mã thoát: 0 xong hoặc không có gì để làm · 2 sai tham số · 3 preflight server hoặc file đích lỗi ·
#   4 backup không khớp md5 · 5 hồi quy (đã rollback, hoặc chưa nếu --no-auto-rollback) ·
#   6 probe không đạt sau khi áp · 7 ghi file lỗi · 8 rollback không khôi phục được file gốc.
set -uo pipefail

usage() { sed -n '2,/^set -uo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
die() { echo "LỖI: $*" >&2; exit "${2:-2}"; }

ALIAS=""; TARGET=""; RFILE=""; BLOCK=""; MARK=""; SITE=""; PROBES=""; PATHS=""
STAGING=0; RESTART=0; RESTART_CMD="/usr/local/lsws/bin/lswsctrl restart"; CHECK_CMD=""
POSITION=""; AFTER=""; BACKUP_ROOT="$HOME/Backups"; RBACKUP_ROOT="/root"; WAIT=3; AUTO_RB=1; APPLY=0
SSH_CMD="${SSH_CMD:-ssh -o BatchMode=yes -o ConnectTimeout=15}"

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0;;
    --alias) ALIAS="${2-}"; shift 2;;
    --target) TARGET="${2-}"; shift 2;;
    --remote-file) RFILE="${2-}"; shift 2;;
    --block) BLOCK="${2-}"; shift 2;;
    --mark) MARK="${2-}"; shift 2;;
    --site-url) SITE="${2-}"; shift 2;;
    --probes) PROBES="${2-}"; shift 2;;
    --paths) PATHS="${2-}"; shift 2;;
    --staging) STAGING="${2-}"; shift 2;;
    --restart) RESTART="${2-}"; shift 2;;
    --restart-cmd) RESTART_CMD="${2-}"; shift 2;;
    --check-cmd) CHECK_CMD="${2-}"; shift 2;;
    --position) POSITION="${2-}"; shift 2;;
    --after) AFTER="${2-}"; shift 2;;
    --backup-root) BACKUP_ROOT="${2-}"; shift 2;;
    --remote-backup-root) RBACKUP_ROOT="${2-}"; shift 2;;
    --wait) WAIT="${2-}"; shift 2;;
    --no-auto-rollback) AUTO_RB=0; shift;;
    --apply) APPLY=1; shift;;
    *) die "Tham số lạ: $1 (xem --help)";;
  esac
done

[ -n "$ALIAS" ] || die "Thiếu --alias"
case "$TARGET" in htaccess|vhost) ;; *) die "--target chỉ nhận htaccess hoặc vhost. my.cnf và sshd làm tay, mỗi lần khác nhau, sshd có thể tự khoá server.";; esac
[ -n "$RFILE" ] || die "Thiếu --remote-file"
[ -f "$BLOCK" ] || die "Không thấy file khối: ${BLOCK:-<trống>}"
[ -n "$SITE" ] || die "Thiếu --site-url"
case "$MARK" in ''|*[!A-Za-z0-9._-]*) die "--mark chỉ gồm chữ, số, dấu chấm, gạch ngang, gạch dưới (ví dụ sec-r1-r6)";; esac
case "$STAGING" in 0|1) ;; *) die "--staging chỉ nhận 0 hoặc 1";; esac
case "$RESTART" in 0|1) ;; *) die "--restart chỉ nhận 0 hoặc 1";; esac
case "$WAIT" in ''|*[!0-9]*) die "--wait phải là số giây";; esac
[ -z "$POSITION" ] && { [ "$TARGET" = vhost ] && POSITION=bottom || POSITION=top; }
case "$POSITION" in top|bottom) ;; *) die "--position chỉ nhận top hoặc bottom";; esac
[ -z "$PROBES" ] || [ -f "$PROBES" ] || die "Không thấy file probes: $PROBES"
[ -z "$PATHS" ] || [ -f "$PATHS" ] || die "Không thấy file paths: $PATHS"
if [ "$STAGING" = 1 ] && [ -z "${STAGING_AUTH:-}" ]; then
  echo "CẢNH BÁO: --staging 1 nhưng chưa đặt STAGING_AUTH. Nếu staging có Basic Auth, mã 401 sẽ lẫn vào snapshot." >&2
fi
if grep -qE "^# (BEGIN|END) ${MARK}( |\$)" "$BLOCK"; then die "File khối đã chứa dòng BEGIN/END của nhãn $MARK"; fi
SITE="${SITE%/}"
HERE="$(cd "$(dirname "$0")" && pwd)"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/applyblock.XXXXXX")" || die "Không tạo được thư mục tạm" 3
trap 'rm -rf "$TMP"' EXIT
chmod 700 "$TMP"

q() { printf '%q' "$1"; }
rsh() { $SSH_CMD "$ALIAS" "$@"; }
log() { echo "$*"; }

lmd5() {
  if command -v md5sum >/dev/null 2>&1; then md5sum < "$1" | cut -d' ' -f1
  elif command -v md5 >/dev/null 2>&1; then md5 -q "$1"
  else python3 -I -c 'import hashlib,sys;print(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; fi
}
# Hàm md5 và stat chạy trên server. Chạy được cả Linux (GNU) lẫn macOS (BSD).
RLIB='md5f(){ if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | cut -d" " -f1; else md5 -q "$1"; fi; }; statf(){ stat -c "%u:%g %a" "$1" 2>/dev/null || stat -f "%u:%g %Lp" "$1"; };'

# ---- 1. Preflight từ xa
log "== 1. Preflight server"
RF=$(q "$RFILE")
RDIR=$(q "$(dirname "$RFILE")")
pre=$(rsh "for t in cp mv stat chmod chown mkdir cat cut rm; do command -v \$t >/dev/null 2>&1 || echo MISSING:\$t; done; { command -v md5sum || command -v md5; } >/dev/null 2>&1 || echo MISSING:md5sum; [ -f $RF ] && [ -r $RF ] || echo MISSING_FILE:$RFILE; [ -d $RDIR ] && [ -w $RDIR ] || echo NOT_WRITABLE_DIR:$RDIR; mkdir -p $(q "$RBACKUP_ROOT") 2>/dev/null; [ -w $(q "$RBACKUP_ROOT") ] || echo NOT_WRITABLE_BACKUP:$RBACKUP_ROOT" 2>&1) || die "Không chạy được lệnh trên server (alias $ALIAS)" 3
if [ "$RESTART" = 1 ]; then
  rbin=${RESTART_CMD%% *}
  chk=$(rsh "[ -x $(q "$rbin") ] || command -v $(q "$rbin") >/dev/null 2>&1 || echo MISSING_RESTART:$rbin" 2>&1) || die "Không chạy được lệnh trên server" 3
  pre="$pre"$'\n'"$chk"
fi
pre=$(printf '%s\n' "$pre" | sed '/^$/d')
if [ -n "$pre" ]; then
  echo "$pre" | sed 's/^/  thiếu: /' >&2
  die "Preflight server không đạt, dừng trước khi làm gì." 3
fi
log "  đạt"

# ---- 2. Đọc file hiện tại và tính file mới
log "== 2. Đọc file đích và dựng bản mới"
rsh "cat $RF" > "$TMP/current" || die "Không đọc được $RFILE" 3
M_SRV=$(rsh "$RLIB md5f $RF" | tr -d '[:space:]')
M_CUR=$(lmd5 "$TMP/current")
[ "$M_SRV" = "$M_CUR" ] || die "md5 file đọc về ($M_CUR) khác md5 trên server ($M_SRV)" 4
STAT=$(rsh "$RLIB statf $RF") || die "Không đọc được owner và mode của $RFILE" 3
OWN=${STAT%% *}; MODE=${STAT#* }
case "$OWN" in *[!0-9:]*|'') die "Owner đọc được không hợp lệ: $OWN" 3;; esac
case "$MODE" in *[!0-7]*|'') die "Mode đọc được không hợp lệ: $MODE" 3;; esac

TODAY=$(date +%F)
{ printf '# BEGIN %s (%s)\n' "$MARK" "$TODAY"; cat "$BLOCK"; [ -z "$(tail -c1 "$BLOCK")" ] || echo; printf '# END %s\n' "$MARK"; } > "$TMP/newblock"
{ cat "$BLOCK"; [ -z "$(tail -c1 "$BLOCK")" ] || echo; } > "$TMP/blockbody"

nb=$(awk -v p="# BEGIN $MARK" 'index($0,p)==1 { r=substr($0,length(p)+1,1); if (r==""||r==" ") n++ } END{print n+0}' "$TMP/current")
ne=$(awk -v p="# END $MARK" 'index($0,p)==1 { r=substr($0,length(p)+1,1); if (r==""||r==" ") n++ } END{print n+0}' "$TMP/current")
if [ "$nb" != "$ne" ] || [ "$nb" -gt 1 ]; then
  die "Khối $MARK trong file đích hỏng (BEGIN=$nb, END=$ne). Sửa tay rồi chạy lại." 3
fi

MODE_DESC=""
if [ "$nb" = 1 ]; then
  awk -v p="# BEGIN $MARK" -v e="# END $MARK" '
    index($0,p)==1 { r=substr($0,length(p)+1,1); if (r==""||r==" ") { inb=1; next } }
    inb && index($0,e)==1 { inb=0; next }
    inb { print }' "$TMP/current" > "$TMP/oldbody"
  if cmp -s "$TMP/oldbody" "$TMP/blockbody"; then
    log "  khối $MARK đã có và giống hệt. Không làm gì."
    exit 0
  fi
  MODE_DESC="THAY khối $MARK đang có"
  NEWBLOCK="$TMP/newblock" BEGIN_P="# BEGIN $MARK" END_P="# END $MARK" awk '
    BEGIN { p=ENVIRON["BEGIN_P"]; e=ENVIRON["END_P"]; nbf=ENVIRON["NEWBLOCK"] }
    !inb && index($0,p)==1 { r=substr($0,length(p)+1,1); if (r==""||r==" ") { inb=1; while ((getline l < nbf) > 0) print l; close(nbf); next } }
    inb { if (index($0,e)==1) inb=0; next }
    { print }' "$TMP/current" > "$TMP/new"
elif [ -n "$AFTER" ]; then
  MODE_DESC="CHÈN khối $MARK sau dòng khớp /$AFTER/"
  NEWBLOCK="$TMP/newblock" AFTER_RE="$AFTER" awk '
    BEGIN { re=ENVIRON["AFTER_RE"]; nbf=ENVIRON["NEWBLOCK"] }
    { print }
    !done && $0 ~ re { while ((getline l < nbf) > 0) print l; close(nbf); done=1 }
    END { if (!done) exit 9 }' "$TMP/current" > "$TMP/new" || die "Không có dòng nào khớp --after /$AFTER/. Không chèn." 2
elif [ "$POSITION" = top ]; then
  MODE_DESC="CHÈN khối $MARK ở đầu file"
  { cat "$TMP/newblock"; cat "$TMP/current"; } > "$TMP/new"
else
  MODE_DESC="CHÈN khối $MARK ở cuối file"
  { cat "$TMP/current"; [ ! -s "$TMP/current" ] || [ -z "$(tail -c1 "$TMP/current")" ] || echo; cat "$TMP/newblock"; } > "$TMP/new"
fi
M_NEW=$(lmd5 "$TMP/new")
log "  $MODE_DESC ($TARGET)"
log "  md5 trước $M_CUR, md5 sau $M_NEW, owner $OWN, mode $MODE"
echo "--- diff (hiện tại → mới)"
diff -u "$TMP/current" "$TMP/new" | sed '1,2d' | head -60
echo "---"

# ---- 3. Snapshot mã HTTP trước
CURL_K=""
if [ "$STAGING" = 1 ] && [ -n "${STAGING_AUTH:-}" ]; then
  CURL_K="$TMP/curl.cfg"
  ( umask 077; printf 'user = "%s"\n' "$STAGING_AUTH" > "$CURL_K" )
fi
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
http_code() {
  if [ -n "$CURL_K" ]; then curl -s -K "$CURL_K" -A "$UA" -o /dev/null -m 20 -w '%{http_code}' "$SITE$1" 2>/dev/null
  else curl -s -A "$UA" -o /dev/null -m 20 -w '%{http_code}' "$SITE$1" 2>/dev/null; fi
}
paths_list() {
  if [ -n "$PATHS" ]; then grep -vE '^[[:space:]]*(#|$)' "$PATHS" | tr -d '\r' | awk '{print $1}'
  else printf '%s\n' / /wp-login.php /wp-admin/admin-ajax.php; fi
}
snapshot() {
  : > "$1"
  paths_list | while IFS= read -r p; do
    c=$(http_code "$p"); [ -n "$c" ] || c=000
    printf '%s\t%s\n' "$p" "$c" >> "$1"
  done
}
run_probes() { # $1 = file lưu kết quả; trả mã thoát của exposure_check.sh
  [ -n "$PROBES" ] || { : > "$1"; return 0; }
  EXPOSURE_CURL_CONFIG="$CURL_K" bash "$HERE/exposure_check.sh" "$SITE" "$PROBES" > "$1" 2>&1
}

log "== 3. Snapshot mã HTTP trước"
snapshot "$TMP/before.tsv"
sed 's/^/  /' "$TMP/before.tsv"
if grep -qE '	(000|5[0-9][0-9])$' "$TMP/before.tsv"; then
  echo "CẢNH BÁO: site đang trả 000 hoặc 5xx ở ít nhất một path trước khi áp. Kiểm site rồi chạy lại nếu cần." >&2
fi
run_probes "$TMP/probes_before.txt"; PB_RC=$?
if [ -n "$PROBES" ]; then
  log "  probe trước khi áp (chỉ để so): $(grep -c '^OK' "$TMP/probes_before.txt") OK, $(grep -c '^FAIL' "$TMP/probes_before.txt") FAIL"
fi

if [ "$APPLY" != 1 ]; then
  TS_PLAN=$(date +%Y%m%d-%H%M%S)
  echo
  log "== DIỄN TẬP: chưa ghi gì lên server, chưa tạo file nào ở máy này."
  log "Nếu thêm --apply, script sẽ:"
  log "  - backup $RFILE vào $RBACKUP_ROOT/backup-$MARK-$TS_PLAN/ (cp -p, md5) và kéo về $BACKUP_ROOT/$ALIAS/$TODAY/$MARK-pre/"
  log "  - sinh rollback.sh cạnh bản backup ở máy này"
  log "  - $MODE_DESC, giữ owner $OWN và mode $MODE"
  [ "$RESTART" = 1 ] && log "  - restart bằng: $RESTART_CMD" || log "  - không restart (thêm --restart 1 nếu stack cần, ví dụ OpenLiteSpeed)"
  log "  - đo lại mã HTTP, so với snapshot; khác thì rollback$([ $AUTO_RB = 1 ] || echo ' (đã tắt, chỉ báo)')"
  exit 0
fi

# ---- 4. Backup
TS=$(date +%Y%m%d-%H%M%S)
BK="$RBACKUP_ROOT/backup-$MARK-$TS"
BASE=$(basename "$RFILE")
log "== 4. Backup"
rsh "mkdir -p $(q "$BK") && chmod 700 $(q "$BK") && cp -p $RF $(q "$BK/$BASE") && $RLIB md5f $(q "$BK/$BASE") > $(q "$BK/MD5SUMS") && printf '%s\n' $(q "$STAT") > $(q "$BK/stat.txt")" \
  || die "Backup trên server lỗi" 4
M_BK=$(rsh "cat $(q "$BK/MD5SUMS")" | tr -d '[:space:]')
[ "$M_BK" = "$M_CUR" ] || die "md5 bản backup trên server ($M_BK) khác file gốc ($M_CUR). Dừng, chưa sửa gì." 4
LB="$BACKUP_ROOT/$ALIAS/$TODAY/$MARK-pre"
[ -e "$LB" ] && LB="$LB-$(date +%H%M%S)"
mkdir -p "$LB" && chmod 700 "$LB" || die "Không tạo được $LB" 4
rsh "cat $(q "$BK/$BASE")" > "$LB/$BASE" || die "Không kéo backup về máy" 4
[ "$(lmd5 "$LB/$BASE")" = "$M_CUR" ] || die "md5 bản backup ở máy khác file gốc. Dừng, chưa sửa gì." 4
printf '%s\n' "$M_CUR  $BASE" > "$LB/MD5SUMS"
printf '%s\n' "$STAT" > "$LB/stat.txt"
cp "$TMP/before.tsv" "$LB/http_before.tsv"
log "  server: $BK"
log "  máy này: $LB"

# ---- 5. Rollback tự sinh
RB="$LB/rollback.sh"
{
  echo '#!/bin/bash'
  echo "# Rollback tự sinh bởi apply_server_block.sh ngày $TODAY, nhãn $MARK. Khôi phục file về bản trước khi áp."
  echo '# Dùng: bash rollback.sh [--dry-run]'
  echo 'set -u'
  printf 'ALIAS=%q\n' "$ALIAS"
  printf 'RFILE=%q\n' "$RFILE"
  printf 'BKFILE=%q\n' "$BK/$BASE"
  printf 'LOCAL=%q\n' "$LB/$BASE"
  printf 'EXPECT=%q\n' "$M_CUR"
  printf 'OWN=%q\n' "$OWN"
  printf 'MODE=%q\n' "$MODE"
  printf 'RESTART=%q\n' "$RESTART"
  printf 'RESTART_CMD=%q\n' "$RESTART_CMD"
  printf 'SSH_CMD=${SSH_CMD:-%q}\n' "$SSH_CMD"
  cat <<'RBEOF'
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
q() { printf '%q' "$1"; }
rsh() { $SSH_CMD "$ALIAS" "$@"; }
RLIB='md5f(){ if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | cut -d" " -f1; else md5 -q "$1"; fi; };'
echo "Khôi phục $RFILE về md5 $EXPECT"
if [ $DRY = 1 ]; then echo "(diễn tập) cp -p $BKFILE → $RFILE, rồi kiểm md5$([ "$RESTART" = 1 ] && echo ", restart: $RESTART_CMD")"; exit 0; fi
NEW="$RFILE.wps-rb.$$"
if rsh "cp -p $(q "$BKFILE") $(q "$NEW") && [ \"\$($RLIB md5f $(q "$NEW"))\" = $(q "$EXPECT") ]" 2>/dev/null; then
  echo "  dùng bản backup trên server"
else
  echo "  bản backup trên server thiếu hoặc lệch, đẩy bản ở máy này lên"
  rsh "cat > $(q "$NEW")" < "$LOCAL" || { echo "LỖI: không đẩy được bản backup" >&2; exit 1; }
  [ "$(rsh "$RLIB md5f $(q "$NEW")" | tr -d '[:space:]')" = "$EXPECT" ] || { rsh "rm -f $(q "$NEW")"; echo "LỖI: md5 bản đẩy lên không khớp" >&2; exit 1; }
fi
rsh "chown $OWN $(q "$NEW") && chmod $MODE $(q "$NEW") && mv -f $(q "$NEW") $(q "$RFILE")" || { rsh "rm -f $(q "$NEW")"; echo "LỖI: không đặt được bản gốc" >&2; exit 1; }
[ "$(rsh "$RLIB md5f $(q "$RFILE")" | tr -d '[:space:]')" = "$EXPECT" ] || { echo "LỖI: md5 sau rollback khác bản gốc" >&2; exit 1; }
if [ "$RESTART" = 1 ]; then rsh "$RESTART_CMD" || { echo "LỖI: restart sau rollback thất bại" >&2; exit 1; }; fi
echo "ROLLBACK OK"
RBEOF
} > "$RB"
chmod 700 "$RB"
log "  rollback: bash $(q "$RB")"

# ---- 6. Ghi file mới
log "== 5. Ghi file mới"
NEWR="$RFILE.wps-new.$$"
cleanup_remote() { rsh "rm -f $(q "$NEWR")" >/dev/null 2>&1; }
rsh "cat > $(q "$NEWR")" < "$TMP/new" || { cleanup_remote; die "Không đẩy được file mới lên server" 7; }
[ "$(rsh "$RLIB md5f $(q "$NEWR")" | tr -d '[:space:]')" = "$M_NEW" ] || { cleanup_remote; die "md5 file mới trên server không khớp. Chưa thay file gốc." 7; }
if [ -n "$CHECK_CMD" ]; then
  cmd=${CHECK_CMD//\{FILE\}/$(q "$NEWR")}
  rsh "$cmd" >"$TMP/check.out" 2>&1 || { cleanup_remote; sed 's/^/  /' "$TMP/check.out" >&2; die "Lệnh kiểm cú pháp báo lỗi. Chưa thay file gốc." 7; }
  log "  kiểm cú pháp: đạt"
fi
rsh "chown $OWN $(q "$NEWR") && chmod $MODE $(q "$NEWR") && mv -f $(q "$NEWR") $RF" || { cleanup_remote; die "Không thay được file gốc" 7; }
[ "$(rsh "$RLIB md5f $RF" | tr -d '[:space:]')" = "$M_NEW" ] || die "md5 sau khi ghi khác bản mới. Chạy: bash $(q "$RB")" 7
log "  đã ghi, md5 $M_NEW"

do_rollback() {
  echo "== Rollback"
  if bash "$RB"; then
    snapshot "$TMP/after_rb.tsv"
    if cmp -s "$TMP/before.tsv" "$TMP/after_rb.tsv"; then echo "  mã HTTP sau rollback giống snapshot trước."; return 0; fi
    echo "CẢNH BÁO: sau rollback mã HTTP vẫn khác snapshot trước:" >&2
    diff "$TMP/before.tsv" "$TMP/after_rb.tsv" | sed 's/^/  /' >&2
    return 1
  fi
  return 1
}
fail_restart() {
  echo "LỖI: restart thất bại." >&2
  do_rollback || exit 8
  exit 5
}

# ---- 7. Restart
if [ "$RESTART" = 1 ]; then
  log "== 6. Restart: $RESTART_CMD"
  rsh "$RESTART_CMD" >"$TMP/restart.out" 2>&1 || { sed 's/^/  /' "$TMP/restart.out" >&2; fail_restart; }
  [ "$WAIT" -gt 0 ] && sleep "$WAIT"
  n=0
  while [ "$n" -lt 10 ]; do
    c=$(http_code /); [ -n "$c" ] && [ "$c" != 000 ] && break
    n=$((n+1)); sleep 2
  done
fi

# ---- 8. Snapshot sau, so sánh
log "== 7. Snapshot mã HTTP sau"
snapshot "$TMP/after.tsv"
cp "$TMP/after.tsv" "$LB/http_after.tsv"
if cmp -s "$TMP/before.tsv" "$TMP/after.tsv" && ! grep -qE '	(000|5[0-9][0-9])$' "$TMP/after.tsv"; then
  log "  $(wc -l < "$TMP/after.tsv" | tr -d ' ') path giữ nguyên mã HTTP"
  REG=0
else
  REG=1
  echo "HỒI QUY: mã HTTP khác snapshot trước (path, trước, sau):" >&2
  awk -F'\t' 'NR==FNR { a[$1]=$2; next } a[$1]!=$2 || $2 ~ /^(000|5)/ { print "  " $1 "  " a[$1] " → " $2 }' "$TMP/before.tsv" "$TMP/after.tsv" >&2
fi
if [ "$REG" = 1 ]; then
  if [ "$AUTO_RB" = 1 ]; then
    do_rollback || exit 8
    echo "Đã rollback do hồi quy. Báo cáo: $LB" >&2
    exit 5
  fi
  echo "Chưa rollback (--no-auto-rollback). Chạy: bash $(q "$RB")" >&2
  exit 5
fi

# ---- 9. Probe
RC=0
if [ -n "$PROBES" ]; then
  log "== 8. Probe sau khi áp"
  run_probes "$TMP/probes_after.txt" || RC=6
  cp "$TMP/probes_after.txt" "$LB/probes_after.txt"
  sed 's/^/  /' "$TMP/probes_after.txt"
  if [ "$RC" = 6 ]; then
    echo "PROBE KHÔNG ĐẠT: khối đã ghi nhưng rule chưa có tác dụng." >&2
    [ "$RESTART" = 1 ] || echo "  Nếu stack là OpenLiteSpeed, chạy lại với --restart 1 (giờ thấp điểm hoặc khi được duyệt)." >&2
    echo "  Rollback: bash $(q "$RB")" >&2
  fi
fi
{
  echo "nhãn: $MARK"; echo "ngày: $TODAY"; echo "mục tiêu: $TARGET"; echo "file: $RFILE"
  echo "md5 trước: $M_CUR"; echo "md5 sau: $M_NEW"; echo "owner mode: $OWN $MODE"
  echo "restart: $RESTART"; echo "kết quả: $([ $RC = 0 ] && echo đạt || echo 'probe không đạt')"
} > "$LB/report.txt"
[ "$RC" = 0 ] && log "XONG. Rollback sẵn: bash $(q "$RB")"
exit "$RC"
