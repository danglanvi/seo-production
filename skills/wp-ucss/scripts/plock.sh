#!/bin/bash
# plock.sh <giây chờ khoá> <giây chạy tối đa> <lệnh...>: chạy lệnh trong khoá production (flock(2) bằng Perl, vì macOS không có lệnh flock).
# File khoá: biến PLOCK_FILE (regen.sh lấy từ lock_file của site.json), mặc định ~/.cm/locks/prod-http.lock. Cùng kiểu khoá với flock(1).
# Hết giờ chờ: mã 75. Hết giờ chạy: TERM tiến trình con, mã 124.
PLOCK_FILE=${PLOCK_FILE:-$HOME/.cm/locks/prod-http.lock} exec perl -MFcntl=:flock -e '
  ($w,$r)=(shift,shift); open(F,">>",$ENV{PLOCK_FILE}) or die "open";
  $SIG{ALRM}=sub{print STDERR "plock: hết giờ chờ khoá\n"; exit 75}; alarm $w; flock(F,LOCK_EX) or die "lock"; alarm 0;
  print STDERR "plock: giữ khoá ".localtime()."\n";
  $p=fork; if(!$p){exec @ARGV or die "exec"}
  $SIG{ALRM}=sub{kill "TERM",$p; print STDERR "plock: hết giờ chạy\n"; waitpid($p,0); exit 124}; alarm $r;
  waitpid($p,0); exit($?>>8)' "$@"
