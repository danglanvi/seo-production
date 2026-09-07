## §13. Anti-patterns (đừng tái phạm)

| Anti-pattern | Vì sao cấm | Làm đúng |
|---|---|---|
| Tạo folder theo tháng / theo pha | Timeline theo dõi bằng `index.md`; folder theo tháng gây phân mảnh deliverable | Cấu trúc theo WORKSTREAM, tiến độ ở bảng B |
| Sửa `02-raw/knowledge/` trong instance | Drift với master — bản vá không lan được sang dự án khác | Đề xuất vá ở master (vòng 2), nhận qua `MIGRATION.md` |
| Set `done` khi chưa QC PASS (công đoạn có checklist) | Phá gate chất lượng — lỗi lọt tới client | QC PASS hoặc `done*` có waiver của Lead (§6, §7) |
| Copy lý thuyết wiki vào project | Knowledge pack đã chưng cất đủ để vận hành; tri thức sâu là tài sản bảo mật ở kho gốc | Gặp wikilink đứt → hỏi Lead (§10.5) |
| Hard-code dữ liệu client vào master | Master là template dùng lại cho mọi client | Client data chỉ ở `00-client-context/` + `index.md` instance; master dùng `{{PLACEHOLDER}}` |
| Sửa mirror `.claude/skills/` / `.agents/skills/` | Mirror được sinh tự động — sửa tay sẽ bị đè | Sửa `skills/` nguồn rồi chạy sync theo quy trình master |
| Viết bài content trong folder này | Content có pipeline + checklist riêng ở repo content | Plan/tracking ở `05-content-plan/`, bài viết ở repo `Content Production - <client>/` (§5.4) |
| Tự hạ ngưỡng checklist để cho qua QC | Ngưỡng là cam kết chất lượng, không phải gợi ý | Báo đúng item rớt + lý do; muốn nới → Lead quyết `CONDITIONAL-PASS` (§7.3) |
| Bung sub-agent/orchestrator cho việc 1 trạm | Mỗi sub-agent nạp lại luật + skill, người vận hành không thấy tiến trình | Trạm-first (§0.5): làm trong phiên, lặp tuần tự; `ORCHESTRATOR.md` chỉ khi gọi rõ |
