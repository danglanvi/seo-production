#!/bin/bash
# prod_deploy.sh <lane>  (stdin: tar của build/ có EXPECT.tsv: relpath<TAB>md5-hiện-tại|NEW; MOVES.tsv tuỳ chọn: relpath<TAB>md5|DIR).
# Dừng mã 3 nếu production đã đổi. Backup trước. Chuyển MOVES sang /root/quarantine-20261105/<lane>/ rồi chép file. In lệnh rollback.
set -euo pipefail
LANE="$1"; B="${WORK_DIR:-/root/code-footprint}/$LANE"; U="$B/prod-up"; rm -rf "$U"; mkdir -p "$U" "$B/backup"; tar -C "$U" -xf -
cd "$U"; [ -f EXPECT.tsv ] || { echo "DUNG: thieu EXPECT.tsv"; exit 2; }
P=${DOCROOT:?DOCROOT}/wp-content
while IFS= read -r f; do ${PHP_BIN:-php} -l "$f" >/dev/null || { echo "LOI PHP $f"; exit 1; }; done < <(find . -name '*.php')
while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; [ -f "$r" ] || { echo "DUNG: build thieu $r"; exit 2; }
  if [ "$m" = "NEW" ]; then [ -e "$P/$r" ] && { echo "DUNG: production da co $r"; exit 3; }
  else [ -e "$P/$r" ] || { echo "DUNG: production khong co $r"; exit 3; }; cur=$(md5sum "$P/$r" | cut -c1-32); [ "$cur" = "$m" ] || { echo "DUNG: $r tren production da doi ($cur)"; exit 3; }; fi
done < EXPECT.tsv
while IFS= read -r f; do case "$f" in EXPECT.tsv|MOVES.tsv|MOVES.txt|.DS_Store) continue;; esac; grep -q "^$f"$'\t' EXPECT.tsv || { echo "DUNG: $f khong co trong EXPECT.tsv"; exit 2; }; done < <(find . -type f | sed 's#^\./##')
if [ -f MOVES.tsv ]; then while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; [ -e "$P/$r" ] || { echo "DUNG: khong co de chuyen $r"; exit 3; }; if [ -f "$P/$r" ] && [ "$m" != "DIR" ]; then cur=$(md5sum "$P/$r" | cut -c1-32); [ "$cur" = "$m" ] || { echo "DUNG: $r da doi ($cur)"; exit 3; }; fi; done < MOVES.tsv; fi
T=$(date +%H%M%S); BK="$B/backup/prod-before-$T.tgz"; LIST="$B/backup/list-$T.txt"; NEWF="$B/backup/new-files-$T.txt"; : > "$LIST"; : > "$NEWF"
while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; if [ "$m" = "NEW" ]; then echo "$r" >> "$NEWF"; else echo "$r" >> "$LIST"; fi; done < EXPECT.tsv
[ -f MOVES.tsv ] && cut -f1 MOVES.tsv >> "$LIST"
if [ -s "$LIST" ]; then tar -czf "$BK" -C "$P" -T "$LIST"; echo "BACKUP $BK $(md5sum "$BK" | cut -c1-8) $(wc -l < "$LIST") muc"; fi
Q="${QUAR_DIR:-/root/quarantine}/$LANE"
if [ -f MOVES.tsv ]; then while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; mkdir -p "$Q/$(dirname "$r")"; rm -rf "$Q/$r"; mv "$P/$r" "$Q/$r"; echo "MOVED $r -> quarantine"; done < MOVES.tsv; fi
while IFS=$'\t' read -r r m; do [ -z "$r" ] && continue; mkdir -p "$(dirname "$P/$r")"; cp "$r" "$P/$r"; chown ${WP_USER:-www}:${WP_USER:-www} "$P/$r"; echo "$(md5sum "$P/$r" | cut -c1-8) $r"; done < EXPECT.tsv
# Rollback: kiểm archive đọc được, chụp bản đang chạy, giải nén, rồi mới xoá file mới; chown đúng file trong danh sách. Dừng ở lỗi đầu tiên.
echo "ROLLBACK: set -e; tar -tzf $BK >/dev/null; cat $LIST $NEWF | tar -czf $B/backup/before-rollback-\$(date +%H%M%S).tgz -C $P --ignore-failed-read -T - ; [ -s $LIST ] && tar -xzf $BK -C $P && xargs -a $LIST -r -I{} chown ${WP_USER:-www}:${WP_USER:-www} $P/{} ; xargs -a $NEWF -r -I{} rm -f $P/{}"
echo "PROD-DEPLOY-OK $LANE $(date +%H:%M:%S)"
