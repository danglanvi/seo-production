# stg_env.sh — helper truy cập staging. Dùng bằng: export STG_ALIAS=<alias>; source stg_env.sh; stg_load   (bash hoặc zsh)
# Không viết STG_ALIAS=<alias> source stg_env.sh: biến gán trước lệnh source không còn khi gọi stg_load.
#
# Biến vào:
#   STG_ALIAS      alias ssh của server (lấy từ 00-client-context/wp-server.md). Bắt buộc cho stg_load.
#   STG_HOME_FILE  file trên server chứa URL staging (mặc định /root/.stg_home)
#   STG_HOST       nếu đã có thì stg_load bỏ qua ssh
# Hàm:
#   SSH <alias> <lệnh...>   ssh -n, BatchMode, lọc cảnh báo post-quantum trên stderr, giữ mã thoát của ssh
#   stg_load                đọc STG_HOME_FILE qua ssh một lần, chuẩn hoá thành host, export STG_HOST. Không in host
#   stg_mask                filter stdin→stdout: thay đúng chuỗi STG_HOST bằng <stg-host>. Host trống thì lỗi, không in gì
#   stg_auth_parse          stdin: file Basic Auth → stdout "user:pass". Nhận user=/password=, STG_BASIC_USER=/STG_BASIC_PASS=
#                           hoặc dòng đầu user:pass. File có dòng KHOÁ= mà thiếu khoá user hoặc pass thì lỗi, không đoán
# Quy tắc: mọi output staging đi qua stg_mask trước khi vào log, file hoặc chat.
# File này không đặt set -e hay set -u, để không làm hỏng shell đang gọi.

STG_UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
STG_SSH_NOISE='post-quantum|store now, decrypt later|openssh\.com/pq|The server may need to be upgraded'

SSH() {
  local -a _rc
  local _u=0 _r=""
  case $- in *u*) _u=1; set +u ;; esac  # ${pipestatus[@]} không tồn tại trong bash, ${PIPESTATUS[@]} không có trong zsh
  [ -n "${ZSH_VERSION:-}" ] && setopt local_options no_multios  # MULTIOS của zsh nhân đôi stdout khi dùng 1>&3
  { ssh -n -o BatchMode=yes -o ServerAliveInterval=15 "$@" 2>&1 1>&3 3>&- | grep -v -E "$STG_SSH_NOISE" >&2
    _rc=("${PIPESTATUS[@]}" "${pipestatus[@]}"); } 3>&1
  # Phần tử không rỗng đầu tiên là mã thoát của ssh (zsh chèn một phần tử rỗng cho PIPESTATUS).
  for _r in "${_rc[@]}"; do [ -n "$_r" ] && break; done
  [ "$_u" = 1 ] && set -u
  return "${_r:-1}"
}

stg_norm_host() { # chuỗi → host: bỏ scheme, đường dẫn, khoảng trắng
  local h="$1"
  h="${h%%$'\n'*}"
  h="${h//[[:space:]]/}"
  h="${h#*://}"
  h="${h%%/*}"
  printf '%s' "$h"
}

stg_load() {
  if [ -n "${STG_HOST:-}" ]; then return 0; fi
  if [ -z "${STG_ALIAS:-}" ]; then echo "stg_load: thiếu STG_ALIAS (alias ssh trong wp-server.md)" >&2; return 2; fi
  local raw rc h
  raw="$(SSH "$STG_ALIAS" "cat '${STG_HOME_FILE:-/root/.stg_home}'")"; rc=$?
  if [ "$rc" -ne 0 ]; then echo "stg_load: ssh lỗi, mã $rc" >&2; return "$rc"; fi
  h="$(stg_norm_host "$raw")"
  case "$h" in
    ''|*[!A-Za-z0-9.:-]*) echo "stg_load: nội dung ${STG_HOME_FILE:-/root/.stg_home} không phải host hợp lệ (độ dài ${#h})" >&2; return 3 ;;
  esac
  STG_HOST="$h"; export STG_HOST
}

stg_mask() {
  STG_MASK_HOST="${STG_HOST:-}" perl -pe 'BEGIN { $h = $ENV{STG_MASK_HOST}; die "stg_mask: STG_HOST trống, từ chối in\n" if $h eq ""; } s/\Q$h\E/<stg-host>/g'
}

stg_auth_parse() {
  local line k v u="" p="" kv=0 first="" seen=0
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"
    [ "$seen" = 0 ] && { first="$line"; seen=1; }
    line="${line#export }"
    case "$line" in *=*) ;; *) continue ;; esac
    k="${line%%=*}"; v="${line#*=}"
    case "$k" in ''|[0-9]*|*[!A-Za-z0-9_]*) continue ;; esac
    kv=1
    case "$v" in \"*\") v="${v#\"}"; v="${v%\"}" ;; \'*\') v="${v#\'}"; v="${v%\'}" ;; esac
    case "$k" in user|STG_BASIC_USER) u="$v" ;; password|STG_BASIC_PASS) p="$v" ;; esac
  done
  if [ "$kv" = 1 ]; then
    if [ -z "$u" ] || [ -z "$p" ]; then
      echo "stg_auth_parse: file có dòng KHOÁ= nhưng thiếu user/password hoặc STG_BASIC_USER/STG_BASIC_PASS" >&2; return 2
    fi
    printf '%s:%s\n' "$u" "$p"; return 0
  fi
  case "$first" in ?*:?*) printf '%s\n' "$first"; return 0 ;; esac
  echo "stg_auth_parse: Basic Auth cần dạng user:pass, user=/password= hoặc STG_BASIC_USER=/STG_BASIC_PASS=" >&2
  return 2
}
