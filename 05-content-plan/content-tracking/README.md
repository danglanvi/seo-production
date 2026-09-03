# 05-content-plan/content-tracking/ — đấu nối với fork Content Production (công đoạn #13, #15, #16, #19)

Trạm 05 giữ **plan + tracking + QC kết quả**, bài viết ở fork `Content Production - <client>/`. Folder này là điểm đấu nối:

- `content-status.md` — sinh tự động bằng `python3 tools/content_sync.py --fork "<đường dẫn fork>"`: số bài theo 9 status (`planned → researched → outlined → drafted → verified → briefed → humanized → published-gdoc → archived`), bài kẹt (không đổi status ≥14 ngày theo `log.md` fork), bài `humanized`/`published-gdoc` sẵn sàng cho WS06 đăng, link Google Doc đã có. Không sửa tay.
- `delivered/<slug>.md` — bản humanized (hoặc metadata + link Doc) của bài đã duyệt, copy về khi chạy `content_sync.py --pull-delivered`; đây là **bản để bạn SEO onpage/đăng** (WS06, SOP 11), không phải nơi sửa bài — sửa thì ở fork rồi sync lại.
- `qc/` không ở đây — verdict QC bài (tier-1 outline/writing) ghi vào `03-audits/qc/` + cột QC `index.md` như mọi deliverable.

Nhịp: chạy sync T2 hằng tuần (hoặc trước review tháng); số trong `content-status.md` là số ghi vào % mốc của dòng #15/#16/#19 `index.md`. Hub PSP (`Deliverables/GTV-Brand/PSP-Performance-Hub/`) dùng cùng logic đọc `index.md` fork.
