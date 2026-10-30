# Bẫy shell trên máy Mac của Lead

Trang này ghi các lệnh hay hỏng khi agent (Claude Code, Codex) chạy shell trên 3 máy Mac. Mỗi dòng là một cách viết sai và cách viết đúng. Nguồn: đợt rà hội thoại 16–24/10/2026, 33 mục lỗi ở 6 phiên, khoảng 150 lượt tool hỏng hoặc chạy lại. Thêm 3 dòng ngày 27/10/2026 (`IFS`, `declare -A`, `${n:+…}`), đã tái hiện bằng `/bin/bash` 3.2 và `zsh -c`.

Bản rút 11 dòng cho brief của lane nằm ở `skills/web-lane-orchestration/references/luat-lane.md`, khối "### Bẫy shell". Khi sửa một bẫy, sửa cả hai nơi.

## Option zsh trong `~/.zshenv`

Mỗi máy cần 2 dòng sau trong `~/.zshenv`. Syncthing không đồng bộ dotfile, nên cài riêng từng máy.

```zsh
# Claude Code / Codex agent: tắt 2 option zsh hay làm lệnh agent hỏng (tools/shell-traps-macos.md trong workspace)
[[ -n "$CLAUDECODE" ]] && { setopt NO_NOMATCH; unsetopt EQUALS; }
```

- `NO_NOMATCH`: glob không khớp file thì giữ nguyên chữ, không báo "no matches found". Ví dụ `--include=*.md`.
- Bỏ `EQUALS`: zsh không hiểu `=` đầu từ là tên lệnh. Ví dụ `echo ====` không còn báo "==== not found".
- Hai option chỉ bật khi biến `CLAUDECODE` có giá trị. Shell của Lead giữ nguyên hành vi cũ.
- Không bật `SH_WORD_SPLIT` toàn cục. Option này đổi hành vi của script khác.

Trạng thái cài:

| Máy | Ngày cài | Cách kiểm |
|---|---|---|
| Mac mini cơ quan | 25/10/2026 | `echo ====` trong Bash tool in ra `====` |
| Mac mini nhà | chưa | |
| MacBook Air | chưa | |

Cài trên máy còn lại: thêm 2 dòng trên vào cuối `~/.zshenv` khi file chưa có chúng, và giữ nội dung cũ. Cài xong, ghi ngày vào bảng trên.

Codex không đặt biến `CLAUDECODE`. Trên Codex, các bẫy dưới vẫn áp dụng đầy đủ.

## Đừng viết → viết

| Đừng viết | Viết | Lý do |
|---|---|---|
| `grep -r --include=*.md` | `rg -g '*.md'` hoặc `--include='*.md'` | Glob không quote làm zsh báo "no matches found" khi chưa cài `NO_NOMATCH` |
| `echo =====` | `echo '---'` hoặc `printf '%s\n' '====='` | zsh hiểu `=` đầu từ là tên lệnh |
| `timeout 300 cmd` | `perl -e 'alarm 300; exec @ARGV' cmd` | macOS không có `timeout` và `gtimeout` |
| `sleep 60; kiểm` ở đầu lệnh | Chạy nền, kiểm ở lượt sau | Claude Code chặn lệnh mở đầu bằng `sleep` |
| Đường dẫn workspace không nháy | `"/Users/<user>/<thư mục có dấu cách>/..."` | Tên thư mục có 2 dấu cách liền nhau và dấu `&` |
| `cd thư-mục && lệnh` qua nhiều lượt | Đường dẫn tuyệt đối, hoặc đặt biến `W` cho thư mục workstream | Bash tool reset cwd sau mỗi lệnh |
| `for u in $urls` | `while read -r u; do …; done < urls.txt` | zsh không tách biến theo dòng. Một vòng đo ra kết quả giả "000" |
| `IFS=' '` đặt cho cả script, rồi `for n in $(ls dir)` | `while IFS= read -r n; do …; done < danh-sach.txt`, hoặc `unset IFS` sau vòng cần tách | `IFS` chỉ có dấu cách thì không tách theo dòng. Ngày 27/10/2026 vòng chép gộp 8 tên file thành 1, không chép file nào; 4 trang dùng CSS gộp khoảng 2 phút |
| `declare -A` trong script `#!/bin/bash` | Python, hoặc file TSV đọc bằng `while read` | `/bin/bash` của macOS là 3.2, không có mảng kết hợp. Ngày 27/10/2026 mảng URL hỏng, 75 lượt Lighthouse đo cùng một trang |
| `lenh ${n:+--flag "$n"}` trong zsh | `args=(); [[ -n $n ]] && args=(--flag "$n"); lenh "${args[@]}"` | zsh không tách kết quả `${n:+…}` thành 2 đối số. Lệnh nhận một đối số `--flag X` và báo lỗi |
| `set -- $x` để tách "slug MÃ" | `${=x}`, hoặc ghép `slug:MÃ` rồi `${c%%:*}`, `${c##*:}` | zsh không tách biến không nháy |
| `.hooks.$e[]` trong chuỗi jq | `.hooks.${e}[]` | zsh hiểu `$e[` là chỉ số mảng và báo "invalid subscript" |
| `grep -oE` với regex dài có `{0,N}` lớn | Python `re`, hoặc `rg` | `grep` trong Bash tool là ugrep, báo "exceeds complexity limit" |
| `find -newermt '-30 minutes'` | Mốc tuyệt đối: `-newermt '2026-10-25 09:00'` | `find` của Bash tool là bfs, không hiểu mốc tương đối |
| `cat -A file` | `cat -et file` | `cat` của macOS không có `-A` |
| `sed -n 'a,+Np'` | `sed -n 'a,bp'` | `sed` của macOS không hiểu `+N` |
| `python3 -I script.py` khi script cần Pillow | `python3 script.py` hoặc `~/.venvs/embeddinggemma/bin/python` | `-I` bỏ site-packages của user, nên mất Pillow |
| `pkill -f <tên chung>` | `kill $(cat work/x.pid)` | Tên chung giết cả tiến trình của phiên khác |
| `rm -rf` lô cũ | `mv` vào `_cu/<giờ>/` | `_REFERENCE/luat-duyet-dieu-phoi.md` cấm xoá file khi Lead chưa yêu cầu |

## Lệnh chạy lâu

Lệnh dự kiến quá 2 phút: chạy nền rồi kiểm bằng lệnh ngắn.

```zsh
nohup <lệnh> > work/x.log 2>&1 < /dev/null & echo $! > work/x.pid
perl -e 'alarm 60; exec @ARGV' tail -5 work/x.log
```

Không chờ bằng Monitor trong agent phụ. Không chờ một lệnh quá 10 phút.
