#!/usr/bin/env bash
# Tìm một chuỗi CSS (selector, thuộc tính, giá trị) trong 7 nguồn CSS của site WordPress, để sửa MỌI bản sao.
#   1 theme (css, scss, php, html)        2 critical CSS theo template (tên có ccss/critical, litespeed/ccss)
#   3 Customizer custom_css (DB)          4 mu-plugins
#   5 Elementor (uploads/elementor/css)   6 plugin (css)
#   7 file gộp do cache sinh (litespeed/css, litespeed/ucss, wp-content/cache)
# Chỉ đọc. Không SSH, không gọi mạng. Chạy trên bản copy local hoặc trên server (đường dẫn --wp là web root).
set -u

usage() {
  cat <<'H'
css_sources.sh — tìm chuỗi CSS trong 7 nguồn CSS của site WordPress

Dùng:  css_sources.sh --wp <web root> [tuỳ chọn] <mẫu> [<mẫu> ...]

  --wp DIR              web root có thư mục wp-content (bắt buộc)
  --theme SLUG          chỉ quét theme này (mặc định: mọi theme)
  --regex               mẫu là regex mở rộng (mặc định: chuỗi cố định)
  --custom-css-file F   file chứa custom_css đã xuất, ví dụ:
                        wp post list --post_type=custom_css --post_status=publish --field=post_content > F
  --wp-cmd 'CMD'        lệnh wp-cli đầy đủ (ví dụ 'wp --path=/x'); script chạy lệnh xuất custom_css ở trên. Bỏ qua nếu đã có --custom-css-file
  --max N               tối đa N dòng khớp mỗi file (mặc định 5)
  --tsv                 in nguồn<TAB>file<TAB>dòng<TAB>nội dung, không in tiêu đề
  --files               chỉ in đường dẫn file khớp, mỗi file một dòng
  -h, --help            in trợ giúp

Mã thoát: 0 có khớp · 1 không khớp ở nguồn nào · 2 sai cú pháp hoặc --wp không hợp lệ.
Nguồn 3 nằm trong DB: không có --custom-css-file hoặc --wp-cmd thì script ghi "chưa kiểm" và vẫn chạy 6 nguồn còn lại.
Nguồn 7 chỉ là bản sinh ra. Muốn sửa thì tìm bản nguồn ở nguồn 1–6, sửa rồi purge cache.
H
}

WP=""; THEME=""; REGEX=0; CCF=""; WPCMD=""; MAX=5; TSV=0; FILES=0; PATS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --wp) WP="${2:-}"; shift 2 ;;
    --theme) THEME="${2:-}"; shift 2 ;;
    --regex) REGEX=1; shift ;;
    --custom-css-file) CCF="${2:-}"; shift 2 ;;
    --wp-cmd) WPCMD="${2:-}"; shift 2 ;;
    --max) MAX="${2:-5}"; shift 2 ;;
    --tsv) TSV=1; shift ;;
    --files) FILES=1; shift ;;
    --) shift; while [ $# -gt 0 ]; do PATS+=("$1"); shift; done ;;
    -*) echo "Tuỳ chọn lạ: $1. Chạy --help." >&2; exit 2 ;;
    *) PATS+=("$1"); shift ;;
  esac
done
[ -n "$WP" ] || { echo "Thiếu --wp. Chạy --help." >&2; exit 2; }
[ -d "$WP/wp-content" ] || { echo "Không thấy $WP/wp-content." >&2; exit 2; }
[ "${#PATS[@]}" -gt 0 ] || { echo "Thiếu <mẫu> cần tìm." >&2; exit 2; }
case "$MAX" in ''|*[!0-9]*) echo "--max phải là số." >&2; exit 2 ;; esac
[ -z "$CCF" ] || [ -f "$CCF" ] || { echo "Không thấy file --custom-css-file: $CCF" >&2; exit 2; }

GFLAG="-F"; [ "$REGEX" = 1 ] && GFLAG="-E"
EA=(); for p in "${PATS[@]}"; do EA+=(-e "$p"); done
WC="$WP/wp-content"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/css_sources.XXXXXX")" || exit 2
trap 'rm -rf "$TMP"' EXIT
HITS="$TMP/hits.tsv"; : > "$HITS"

classify() {  # đường dẫn tương đối từ web root -> số nguồn
  case "$1" in
    wp-content/litespeed/ccss/*) echo 2 ;;
    wp-content/litespeed/*|wp-content/cache/*) echo 7 ;;
    */ccss*|*/critical*|*ccss*|*critical*) echo 2 ;;
    wp-content/uploads/elementor/*) echo 5 ;;
    wp-content/mu-plugins/*) echo 4 ;;
    wp-content/plugins/*) echo 6 ;;
    wp-content/themes/*) echo 1 ;;
    *) echo 6 ;;
  esac
}

scan() {  # scan <thư mục> <include...>
  local dir="$1"; shift
  [ -d "$dir" ] || return 0
  local inc=(); for e in "$@"; do inc+=(--include="$e"); done
  grep -rnI $GFLAG "${inc[@]}" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=languages --exclude='*.map' "${EA[@]}" -- "$dir" 2>/dev/null |
  while IFS= read -r line; do
    f="${line%%:*}"; rest="${line#*:}"; ln="${rest%%:*}"; txt="${rest#*:}"
    rel="${f#$WP/}"
    printf '%s\t%s\t%s\t%s\n' "$(classify "$rel")" "$rel" "$ln" "$(printf '%s' "$txt" | tr '\t' ' ' | cut -c1-160)" >> "$HITS"
  done
}

if [ -n "$THEME" ]; then scan "$WC/themes/$THEME" '*.css' '*.scss' '*.php' '*.html'
else scan "$WC/themes" '*.css' '*.scss' '*.php' '*.html'; fi
scan "$WC/mu-plugins" '*.css' '*.scss' '*.php'
scan "$WC/plugins" '*.css' '*.scss'
scan "$WC/uploads/elementor" '*.css'
scan "$WC/litespeed" '*.css'
scan "$WC/cache" '*.css'

# Nguồn 3: custom_css trong DB.
C3="chưa kiểm"
if [ -z "$CCF" ] && [ -n "$WPCMD" ]; then
  CCF="$TMP/custom_css.txt"
  # shellcheck disable=SC2086
  if $WPCMD post list --post_type=custom_css --post_status=publish --field=post_content > "$CCF" 2>"$TMP/wp.err"; then :; else
    echo "Cảnh báo: lệnh wp-cli xuất custom_css lỗi: $(head -c 200 "$TMP/wp.err")" >&2; CCF=""
  fi
fi
if [ -n "$CCF" ]; then
  C3="đã kiểm"
  grep -nI $GFLAG "${EA[@]}" -- "$CCF" 2>/dev/null | while IFS= read -r line; do
    ln="${line%%:*}"; txt="${line#*:}"
    printf '3\t%s\t%s\t%s\n' "custom_css (Customizer, DB)" "$ln" "$(printf '%s' "$txt" | tr '\t' ' ' | cut -c1-160)" >> "$HITS"
  done
fi

TOTAL=$(wc -l < "$HITS" | tr -d ' ')
NFILES=$(cut -f2 "$HITS" | sort -u | wc -l | tr -d ' ')

if [ "$FILES" = 1 ]; then cut -f2 "$HITS" | sort -u
elif [ "$TSV" = 1 ]; then sort -t$'\t' -k1,1n -k2,2 -k3,3n "$HITS"
else
  NAME=("" "theme" "critical CSS theo template" "Customizer custom_css (DB)" "mu-plugins" "Elementor (CSS sinh)" "plugin" "file gộp do cache sinh")
  echo "Mẫu: ${PATS[*]}"
  for n in 1 2 3 4 5 6 7; do
    cnt=$(awk -F'\t' -v n="$n" '$1==n' "$HITS" | wc -l | tr -d ' ')
    fc=$(awk -F'\t' -v n="$n" '$1==n{print $2}' "$HITS" | sort -u | wc -l | tr -d ' ')
    if [ "$n" = 3 ] && [ "$C3" = "chưa kiểm" ]; then echo "[3] ${NAME[3]}: CHƯA KIỂM (thiếu --custom-css-file hoặc --wp-cmd)"; continue; fi
    echo "[$n] ${NAME[$n]}: $cnt khớp, $fc file"
    awk -F'\t' -v n="$n" '$1==n{print $2}' "$HITS" | sort -u | while IFS= read -r f; do
      awk -F'\t' -v n="$n" -v f="$f" -v m="$MAX" '$1==n && $2==f { c++; if (c<=m) printf "    %s:%s: %s\n", $2, $3, $4 } END { if (c>m) printf "    ... còn %d dòng khớp trong file này\n", c-m }' "$HITS"
    done
  done
  echo
  echo "Tổng: $TOTAL dòng khớp, $NFILES file."
  SRCS=$(cut -f1 "$HITS" | sort -un | tr '\n' ' ')
  echo "Nguồn có khớp: ${SRCS:-không có}"
  if [ "$TOTAL" -gt 0 ]; then
    echo "Sửa MỌI bản sao ở nguồn 1–6. Nguồn 7 là bản sinh: sửa nguồn rồi purge cache và dựng lại critical CSS."
  fi
fi

[ "$TOTAL" -gt 0 ] && exit 0
exit 1
