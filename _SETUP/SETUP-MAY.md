# SETUP MÁY — runbook cài repo này

> **AI đọc file này rồi làm theo, đừng đưa cả file cho người dùng đọc.** Người dùng chỉ cần trả lời
> vài câu hỏi và bấm vài nút trên trình duyệt. Mọi lệnh terminal do AI chạy.
>
> Người dùng điển hình: lần đầu cài Claude Code, không quen terminal, không biết service account là gì.
> Nói bằng tiếng Việt thường, không dùng từ kỹ thuật khi không cần.

## Luật chạy runbook

1. **Đừng đoán máy thiếu gì — hỏi doctor.** Mọi quyết định bước kế tiếp dựa trên output
   `python3 _SETUP/setup_doctor.py --json`, không dựa vào phỏng đoán.
2. **Sửa từ tầng thấp lên.** Tầng B không thể xong khi tầng A còn thiếu. Đừng nhảy cóc.
3. **Không tự tạo credential hộ người dùng, không xin file key qua chat.** Chìa khóa là bí mật của
   họ; việc của AI là hướng dẫn và gắn file họ đã tự tải về.
4. **Chỉ báo xong khi doctor trả `ok: true`.** Chưa đạt thì nói rõ đang kẹt tầng nào, chờ ai.
5. Cài đặt xong mới bắt đầu việc nội dung. Đang setup thì đừng mở việc khác.

---

## Bước 0 — định vị

Xác nhận đang ở root repo (thư mục có `_SETUP/` và `CLAUDE.md`). Nếu người dùng mới chỉ đưa link
GitHub mà chưa clone: clone về chỗ họ chọn (mặc định `~/Documents/`), `cd` vào rồi mới chạy tiếp.

Repo private của tổ chức `GTV-SEO-Agency` → người dùng phải được mời vào tổ chức và đăng nhập
GitHub trước. Clone báo lỗi `Repository not found` gần như luôn là chưa được mời, không phải sai link
— báo họ xin Lead mời vào tổ chức, đừng loay hoay thử lại.

## Bước 1 — khám máy

```bash
python3 _SETUP/setup_doctor.py --json
```

Đọc JSON, tóm tắt cho người dùng bằng 2-3 câu: máy đủ gì, thiếu gì, mất bao lâu để xong. Đừng đổ cả
JSON ra màn hình.

## Bước 2 — tầng A: phần mềm nền

Thiếu `git` / `node` / `npx` / `uv` → cài bằng lệnh doctor đã in. Trên macOS cần Homebrew trước:

```bash
command -v brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Cài Homebrew mất vài phút và **có hỏi mật khẩu máy** — báo trước để người dùng khỏi hoảng.
`uv` chỉ cần khi repo có MCP Google (ga4 / gsc / google-sheets); thiếu nó không chặn phần còn lại.

## Bước 3 — tầng B: thư viện Python

```bash
python3 _SETUP/setup_doctor.py --fix
```

Lệnh này chạy `pip install -r requirements.txt` và cài Playwright nếu repo cần. Gặp lỗi
`externally-managed-environment` (Python cài bằng brew) thì thêm `--user`:

```bash
python3 -m pip install --user -r requirements.txt
```

## Bước 4 — tầng C: chìa khóa Google

```bash
python3 _SETUP/setup_credential.py detect
```

Ba nhánh:

| Kết quả detect | Làm gì |
|---|---|
| Repo đã cấu hình | Xong tầng C, sang bước 5 |
| Thấy key sẵn trên máy (`~/.config/gcp/` hoặc `~/Downloads/`) | Xác nhận với người dùng đúng robot đó rồi chạy `register <đường dẫn>` script đã in sẵn |
| Không thấy key nào | Người dùng phải tự tạo — đọc `_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md`, dẫn họ qua 6 bước trên trình duyệt, đợi họ tải file `.json` về rồi `register` |

Dẫn 6 bước tạo service account thì **đọc cho họ từng bước một, chờ họ làm xong bước này mới nói bước
sau**. Đổ cả 6 bước một lượt là họ lạc ngay.

`register` tự làm hết phần còn lại: chép key vào `~/.config/gcp/` với `chmod 600`, ghi
`config/local.yaml` và `.claude/settings.local.json`, sinh `.mcp.json` từ bản mẫu nếu repo có.

## Bước 5 — tầng D: xin quyền trên Drive

```bash
python3 _SETUP/setup_credential.py share
```

Lệnh in địa chỉ robot + danh sách file/folder cần share + sẵn một đoạn tin nhắn xin quyền.

**Người dùng KHÔNG tự cấp quyền cho mình được** — phải người sở hữu file (Lead / Account) share.
Việc của AI ở đây là: đưa họ địa chỉ robot, đưa đoạn tin nhắn để copy, nói rõ gửi cho ai.

Xin **Editor** làm mặc định. Người dùng hỏi "Viewer có được không" thì trả lời chính xác: script
trong repo đều đọc-only nên Viewer chạy được; nhưng khi AI thao tác sheet qua MCP `google-sheets`
thì cần ghi, Viewer sẽ lỗi `403` ở giữa chừng công việc chứ không lỗi ngay — khó tìm hơn nhiều.
Ngoại lệ cố ý để Viewer nằm trong `_SETUP/CHIA-QUYEN-DRIVE.md`.

Repo chưa khai file Google nào → bỏ qua bước này, không phải lỗi.

## Bước 6 — chốt

```bash
python3 _SETUP/setup_doctor.py
python3 _SETUP/setup_credential.py check
```

Cả hai `ĐẠT` → báo người dùng đã xong, và nói **một** việc họ có thể làm ngay bằng repo này (tra
`COMMANDS.md`). Đừng liệt kê hết mọi tính năng.

Còn kẹt → nói rõ kẹt cái gì, cần ai làm gì, và phần nào của repo vẫn dùng được trong lúc chờ.

---

## Cần MCP không?

MCP là các nguồn dữ liệu ngoài (Ahrefs, Firecrawl, GA4, Search Console, Google Sheets). Repo chạy
được mà không có MCP — skill nào cần sẽ tự chạy đường lùi và ghi rõ giới hạn dữ liệu.

Chỉ cài MCP khi người dùng chủ động cần, hoặc `.mcp.json` còn placeholder và họ đã có sẵn API key.
Khoá API lấy từ Lead. **Không bao giờ viết API key vào file được commit** — chỉ vào `.mcp.json`
(đã gitignore).

## Bẫy hay gặp

| Triệu chứng | Nguyên nhân thật |
|---|---|
| `Repository not found` khi clone | Chưa được mời vào tổ chức GitHub, không phải sai link |
| `pip: externally-managed-environment` | Python của Homebrew — thêm `--user` |
| Script chạy tay ở Terminal thì lỗi credential, trong Claude Code thì được | Terminal không đọc `.claude/settings.local.json`; script đọc `config/local.yaml` nên vẫn chạy được — nếu vẫn lỗi thì `config/local.yaml` chưa ghi, chạy lại `register` |
| `HttpError 403/404` khi kéo sheet | Chưa share cho robot, hoặc share nhầm địa chỉ email cá nhân thay vì địa chỉ robot |
| Kéo sheet được nhưng AI ghi qua MCP thì lỗi 403 | Đang là Viewer, cần nâng Editor |
| Đã share rồi vẫn báo chưa có quyền | Share nhầm sang robot của người khác — đối chiếu địa chỉ robot bằng `setup_credential.py detect` |

## Tuyệt đối không

- Không commit file key `.json`, `.mcp.json`, `config/local.yaml`, `.claude/settings.local.json`.
- Không gửi file key qua email, chat hay Drive dùng chung. Máy nào cần thì tạo key riêng cho máy đó.
- Không dùng chung một robot giữa nhiều người bằng cách chuyền file key cho nhau.
- Không sửa `_SETUP/` — thư mục này là bản sao đồng bộ từ kho chung, sửa sẽ bị đè ở lần sync sau.
  Thấy sai thì báo Lead vá bản gốc wiki nội bộ «setup-kit» (ngoài repo, hỏi Lead/Vincent).
