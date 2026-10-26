#!/bin/bash
# Kiểm công cụ backup và dump trên server trước khi chạy dump, nén hoặc kéo backup. Chỉ đọc.
# Chạy trên server:  ssh <alias> 'bash -s -- [tuỳ chọn]' < preflight_remote.sh
# Chạy tại máy này để thử: bash preflight_remote.sh [tuỳ chọn]
#
# Tuỳ chọn:
#   --path DIR     Thư mục sẽ ghi backup, để kiểm dung lượng trống. Mặc định /root.
#   --need-db      Bắt buộc có mysqldump. Thiếu thì thoát 1.
#   --min-free-gb N  Dung lượng trống tối thiểu (GB). Mặc định 2. Thiếu thì thoát 1.
#   -h, --help     In trợ giúp này.
#
# Đầu ra: mỗi công cụ một dòng "tool: có|không (đường dẫn)", rồi các dòng khoá=giá trị:
#   COMPRESS=zstd|gzip   nén dump và tar. Thiếu zstd thì gzip. Thiếu cả hai thì thoát 1.
#   PULL=rsync|tar-ssh   cách kéo về máy làm việc. Thiếu rsync trên server thì tar-ssh (tar qua kết nối SSH).
#   FREE_GB=<số>         dung lượng trống ở --path
#   RESULT=ok|degraded|fail
# Dùng các giá trị này để chọn lệnh. Không chạy tiếp lệnh dump khi RESULT=fail.
# Mã thoát: 0 ok hoặc degraded (đã có phương án thay) · 1 thiếu công cụ bắt buộc hoặc thiếu dung lượng · 2 sai tham số.
CHECK_PATH=/root; NEED_DB=0; MIN_GB=2
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,/^# Mã thoát/p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    --path) CHECK_PATH="${2-}"; shift 2;;
    --need-db) NEED_DB=1; shift;;
    --min-free-gb) MIN_GB="${2-}"; shift 2;;
    *) echo "Tham số lạ: $1 (xem --help)" >&2; exit 2;;
  esac
done
case "$MIN_GB" in ''|*[!0-9]*) echo "--min-free-gb phải là số" >&2; exit 2;; esac
fail=0; degraded=0
has() { command -v "$1" 2>/dev/null; }
show() { p=$(has "$1"); if [ -n "$p" ]; then echo "$1: có ($p)"; return 0; else echo "$1: không"; return 1; fi; }
for t in tar gzip zstd rsync mysqldump mysql df; do show $t; done
COMPRESS=""
if has zstd >/dev/null; then COMPRESS=zstd
elif has gzip >/dev/null; then COMPRESS=gzip; degraded=1; echo "THAY THẾ: không có zstd, dùng gzip. Đừng chạy lệnh có 'zstd' trong pipe, nó cho ra file 0 byte."
else echo "THIẾU: không có zstd lẫn gzip."; fail=1; fi
has tar >/dev/null || { echo "THIẾU: tar (bắt buộc cho backup file)."; fail=1; }
if has rsync >/dev/null; then PULL=rsync
else PULL=tar-ssh; degraded=1; echo "THAY THẾ: server không có rsync, kéo bằng tar qua SSH. Báo cáo rõ, đừng để backup_pull.sh báo thành công."; fi
if ! has mysqldump >/dev/null; then
  if [ $NEED_DB = 1 ]; then echo "THIẾU: mysqldump (bắt buộc cho dump DB)."; fail=1; else echo "GHI CHÚ: không có mysqldump, chưa dump được DB."; fi
fi
FREE=""
if has df >/dev/null; then
  FREE=$(df -Pk "$CHECK_PATH" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1048576}')
fi
if [ -z "$FREE" ]; then echo "THIẾU: không đọc được dung lượng trống ở $CHECK_PATH."; fail=1
elif [ "$FREE" -lt "$MIN_GB" ]; then echo "THIẾU: chỉ còn ${FREE} GB ở $CHECK_PATH, cần ít nhất $MIN_GB GB."; fail=1; fi
echo "COMPRESS=$COMPRESS"
echo "PULL=$PULL"
echo "FREE_GB=$FREE"
if [ $fail = 1 ]; then echo "RESULT=fail"; exit 1
elif [ $degraded = 1 ]; then echo "RESULT=degraded"; exit 0
else echo "RESULT=ok"; exit 0; fi
