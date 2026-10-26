#!/bin/bash
# Cách ly file ảnh tên cũ sau khi đã đổi tên và có 301 (references/doi-ten-anh-da-dang.md bước 8). Không xoá file.
# cach-ly: chuyển <web root><URL cũ> sang <thư mục backup>/<ngày giờ>/, chỉ khi file của URL mới đã có.
# tra-lai: đưa file của lần cách ly gần nhất về chỗ cũ, không ghi đè file đang có.
# Dùng: anh_cach_ly.sh <ssh alias> <web root> <bảng 301 JSON> cach-ly|tra-lai [thư mục backup ngoài web root]
# Bảng JSON: {"/wp-content/uploads/a/cu.webp": "/wp-content/uploads/a/moi.webp", ...}. User SSH cần quyền ghi web root.
set -e
A="$1"; ROOT="${2%/}"; MAP="$3"; ACT="$4"; Q="${5:-/www/backup/anh-ten-cu/$(basename "$ROOT")}"
case "$ACT" in cach-ly|tra-lai) ;; *) sed -n '2,6p' "$0"; exit 1 ;; esac
REMOTE='set -e
ROOT=$1; Q=$2; ACT=$3
if [ "$ACT" = cach-ly ]; then
  D=$Q/$(date +%Y%m%d-%H%M%S); n=0
  while IFS=$'"'"'\t'"'"' read -r o m; do
    [ -f "$ROOT$o" ] || continue
    if [ ! -f "$ROOT$m" ]; then echo "giữ $o: chưa có $m"; continue; fi
    mkdir -p "$D$(dirname "$o")"; mv "$ROOT$o" "$D$o"; n=$((n+1))
  done
  echo "đã cách ly $n file sang $D"
else
  L=$(ls -d "$Q"/2* 2>/dev/null | sort | tail -1); [ -n "$L" ] || { echo "Không có bản cách ly trong $Q"; exit 1; }
  n=0
  while IFS= read -r -d "" f; do
    r=${f#$L}
    if [ -e "$ROOT$r" ]; then echo "bỏ qua $r: đã có"; continue; fi
    mkdir -p "$ROOT$(dirname "$r")"; mv "$f" "$ROOT$r"; n=$((n+1))
  done < <(find "$L" -type f -print0)
  echo "đã trả $n file từ $L"
fi'
printf '%s\n' "$REMOTE" | ssh "$A" 'cat > /tmp/anh_cach_ly_remote.sh'
python3 -I -c "import json,sys; [print(k + '\t' + v) for k, v in json.load(open(sys.argv[1])).items()]" "$MAP" |
  ssh "$A" "bash /tmp/anh_cach_ly_remote.sh '$ROOT' '$Q' $ACT"
echo "Nhớ purge cache của site."
