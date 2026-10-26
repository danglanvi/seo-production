#!/bin/bash
# Kiểm dấu bám trụ trên server Ubuntu/Debian, chỉ đọc. Chạy bằng root: ssh <alias> "bash -s" < persistence.sh > persistence.txt
# Stack khác aaPanel: ssh <alias> "WWW_USER=www-data WEBROOT=/var/www bash -s" < persistence.sh
# Đọc kết quả theo references/ung-cuu-su-co.md mục 4.
WWW_USER="${WWW_USER:-www}"; WEBROOT="${WEBROOT:-/www/wwwroot}"
echo "### systemd units not owned by any package (enabled/running)"
for u in $(systemctl list-unit-files --type=service --state=enabled --no-legend | awk '{print $1}'); do
  f=$(systemctl show -p FragmentPath --value "$u"); [ -z "$f" ] && continue
  dpkg -S "$f" >/dev/null 2>&1 || echo "  $u -> $f ($(stat -c %y "$f" | cut -c1-10)) ExecStart=$(systemctl show -p ExecStart --value "$u" | grep -oE 'path=[^ ;]+' | head -1)"
done
echo "### timers"; systemctl list-timers --all --no-legend | awk '{print $(NF-1), $NF}' | head -20
echo "### /etc/systemd/system recent files (90d)"; find /etc/systemd/system /lib/systemd/system -type f -mtime -90 -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | head
echo "### rc.local"; ls -la /etc/rc.local 2>&1; [ -f /etc/rc.local ] && grep -v '^#' /etc/rc.local | grep -v '^$'
echo "### /etc/profile.d (non-package)"; for f in /etc/profile.d/*; do dpkg -S "$f" >/dev/null 2>&1 || echo "  $f ($(stat -c %y "$f" | cut -c1-10))"; done
echo "### root shell rc files"; ls -la --time-style=long-iso /root/.bashrc /root/.profile /root/.bash_profile /root/.bash_login /root/.bash_logout 2>&1 | grep -v 'No such'
grep -nE 'curl|wget|nc |bash -i|/dev/tcp|base64|python|perl|eval|LD_PRELOAD|alias (ssh|sudo|ls)' /root/.bashrc /root/.profile /root/.bash_profile 2>/dev/null | head
echo "### /etc/ld.so.preload"; ls -la /etc/ld.so.preload 2>&1; cat /etc/ld.so.preload 2>/dev/null
echo "### dpkg --verify (critical packages)"; dpkg --verify libpam-modules libpam-runtime openssh-server openssh-client coreutils procps util-linux passwd login sudo cron 2>&1 | grep -vE ' c /etc/' | head -20; echo "(config-file changes, 'c', excluded above):"; dpkg --verify libpam-modules libpam-runtime openssh-server coreutils procps util-linux passwd login sudo cron 2>&1 | grep -E ' c /etc/' | head
echo "### PAM unusual modules"; grep -rhE '^[^#].*pam_[a-z_]+\.so' /etc/pam.d/ | grep -oE 'pam_[a-z_0-9]+\.so' | sort | uniq -c | sort -rn | head -30
find /lib/x86_64-linux-gnu/security /lib/security -name '*.so' -newer /etc/hostname -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | head
echo "### SUID/SGID not from packages"
find / -xdev \( -perm -4000 -o -perm -2000 \) -type f 2>/dev/null | while read f; do dpkg -S "$f" >/dev/null 2>&1 || echo "  $f $(stat -c '%U %a %y' "$f" | cut -c1-30)"; done | head -20
echo "### executables / scripts in tmp dirs"
find /tmp /var/tmp /dev/shm -xdev -type f \( -perm -u+x -o -name '*.sh' -o -name '*.php' -o -name '*.py' -o -name '*.pl' -o -name '*.so' -o -name '.*' \) -printf '%TY-%Tm-%Td %u %s %p\n' 2>/dev/null | grep -vE '/tmp/(lshttpd|wpcli-home|wpcli-root)/' | head -20
echo "### processes with deleted exe or running from tmp"
for p in /proc/[0-9]*; do e=$(readlink $p/exe 2>/dev/null); case "$e" in *"(deleted)"*|/tmp/*|/var/tmp/*|/dev/shm/*) echo "  pid ${p#/proc/} $(cat $p/comm 2>/dev/null) $e";; esac; done | grep -v 'lsphp\|litespeed\|openlitespeed' | head
echo "### processes running as $WWW_USER (non-php/web server)"; ps -eo user,pid,ppid,etime,args --no-headers | awk -v u="$WWW_USER" '$1==u' | grep -vE 'lsphp|litespeed|openlitespeed|lshttpd|php-fpm|apache2|httpd|nginx' | head
echo "### outbound connections (established, non-local)"; ss -tnp state established 2>/dev/null | awk 'NR>1 {print $4, $5, $6}' | grep -vE '127\.0\.0\.1|::1' | awk '{split($2,a,":"); print a[1], $3}' | sed -E 's/users:\(\("([^"]+)".*/\1/' | sort | uniq -c | sort -rn | head -15
echo "### crontabs (all users)"; for u in $(cut -d: -f1 /etc/passwd); do c=$(crontab -l -u $u 2>/dev/null | grep -vE '^\s*#|^\s*$'); [ -n "$c" ] && { echo "  [$u]"; echo "$c" | sed 's/^/    /'; }; done
ls -la /etc/cron.d/ /var/spool/cron/crontabs/ 2>/dev/null | grep -v '^total'
for f in /etc/cron.d/*; do dpkg -S "$f" >/dev/null 2>&1 || { echo "  non-pkg: $f"; grep -vE '^\s*#|^\s*$' "$f" | head -5; }; done
echo "### at jobs"; atq 2>&1 | head; ls /var/spool/cron/atjobs 2>/dev/null | head
echo "### kernel modules not in modules.dep"; for m in $(lsmod | awk 'NR>1{print $1}'); do modinfo -n $m >/dev/null 2>&1 || echo "  $m (no modinfo)"; done; lsmod | wc -l
echo "### users with shell / uid 0"; awk -F: '$3==0 || $7 !~ /(nologin|false|sync|halt|shutdown)$/ {print "  "$1, $3, $7}' /etc/passwd
echo "### authorized_keys anywhere"; find / -xdev -name 'authorized_keys*' -type f 2>/dev/null | while read f; do echo "  $f: $(cut -d' ' -f3- "$f" | tr '\n' ' ')"; done
echo "### $WWW_USER-owned files outside webroots (recent 120d)"; find / -xdev -user "$WWW_USER" -type f -mtime -120 -not -path "$WEBROOT/*" -not -path '/www/wwwlogs/*' -not -path '/tmp/lshttpd/*' -not -path '/tmp/wpcli-home/*' -not -path '/usr/local/lsws/*' -not -path '/proc/*' -not -path '/www/server/panel/*' 2>/dev/null | head -20
echo "### sudoers"; grep -rvhE '^\s*#|^\s*$' /etc/sudoers /etc/sudoers.d/ 2>/dev/null
