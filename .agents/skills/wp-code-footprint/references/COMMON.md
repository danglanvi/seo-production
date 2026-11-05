# COMMON — luật cứng cho lane dọn footprint (chép vào prompt của mỗi lane, thay phần trong <…>)

Mục đích: mỗi lane chỉ chạm tập file của mình, ghi production qua cổng md5, có backup và rollback, và chứng minh "chỉ comment đổi" bằng so token. Nguồn: đợt dọn site agency mẫu 05/11/2026 (4 lane, 0 lỗi production).

```text
BỐI CẢNH: <site> (WordPress, <cache/CDN>). Người duyệt cho phép dọn lúc <giờ, lời duyệt nguyên văn>. Audit gốc: <đường dẫn báo cáo audit>.
Bạn là một lane. Phiên chính điều phối, kiểm độc lập bằng Jev + quét tất định, và purge cache toàn site SAU khi mọi lane xong. Bạn không purge toàn site. Người duyệt vắng: không hỏi, tự quyết trong BRIEF, ngoài BRIEF ghi bao-cao.md.

LUẬT CỨNG
- Chỉ chạm file trong bảng sở hữu của BRIEF. Cần sửa file lane khác: ghi bao-cao.md, không tự sửa.
- Nguồn code gốc = bản production chép lúc <giờ>: <đợt>/srv/mu-plugins/ và <đợt>/srv/theme/. Chép file cần sửa vào FOLDER/build/<relpath trong wp-content>/ rồi sửa ở đó. Không sửa srv/. Chỉ đặt vào build/ file thật sự thay đổi. File cần chuyển sang quarantine (thay cho xoá): ghi relpath vào build/MOVES.txt.
- Công cụ đã test (không tự viết lệnh ssh ghi khác): TOOLS/stg_deploy.sh FOLDER · TOOLS/make_expect.py FOLDER [--theme <theme>] · TOOLS/prod_deploy.sh FOLDER (dừng mã 3 nếu md5 production khác bản srv/) · TOOLS/stg_get.sh <path> [m] · TOOLS/prod_get.sh <path> [m|d] [nc|cache] [webp] · TOOLS/md5.sh <relpath>... · TOOLS/health.sh <HH:MM> · TOOLS/footprint_count.py <html>...
- Thứ tự bắt buộc: sửa build → php -l → stg_deploy → kiểm staging (200, không fatal, dấu hiệu sửa có mặt) → make_expect → lấy khoá → prod_deploy → CHECKPOINT.md ngay (giờ, file, md5, lệnh ROLLBACK, "kiểm sau áp: chưa") → nhả khoá → kiểm production bằng prod_get ... nc + health.sh → CHECKPOINT "kiểm sau áp: đạt|không đạt".
- Khoá ghi production dùng chung: mkdir ~/.cm/locks/<site>-prod-write.lockdir thành công mới chạy prod_deploy; rmdir ngay sau PROD-DEPLOY-OK. Giữ tối đa 5 phút. Bị giữ: kiểm lại tối đa 1 lần/phút bằng lệnh ngắn, quá 10 phút trả held.
- Khoá lane: date > ~/.cm/locks/<lane>.lock lúc bắt đầu; đổi tên .lock.done-HHMM khi xong, .lock.stopped-HHMM khi dừng dở.
- Production: tối đa 1 request mỗi giây từ lane. Không WP-CLI ghi.
- Bản ?nc= có thể trả noindex và không canonical (site noindex mọi URL có query). Không so robots/canonical trên bản nc. So trên bản cache sau purge.
- Không in host staging, mật khẩu, key, slug đăng nhập. Không cat file secret.
- Không dùng Monitor, Workflow, Agent, SendMessage, Artifact, ArtifactData, tool trình duyệt. Không rm -rf. Không sleep đầu lệnh, không vòng chờ. Mọi lệnh ≤ 10 phút.
- Điều kiện dừng: 5xx mới, PHP Fatal mới, trang trắng, robots/canonical bản cache đổi, đăng nhập hỏng → chạy ngay lệnh ROLLBACK, kiểm lại, ghi lý do, trả failed.
- Chứng minh "chỉ comment đổi": so token PHP (token_get_all bỏ T_COMMENT/T_DOC_COMMENT/T_WHITESPACE), JS (acorn tokenizer), CSS (bỏ comment, gộp khoảng trắng) giữa srv/ và build/. Lệch chỉ được là khối BRIEF cho bỏ.
- Đầu ra bắt buộc trong FOLDER: CHECKPOINT.md; bao-cao.md (kết luận trước, bảng số trước/sau, file đã đổi, việc không làm và lý do); rollback.md; ket-qua.json {"lane","status":"done|partial|held|failed","prod_deployed":bool,"files":[],"moves":[],"before":{},"after":{},"loi_production":[],"loi_bao_cao":[],"notes":[]}.
```

Bẫy đã gặp:

- `MOVES.txt` để trong `build/` làm cổng EXPECT dừng mã 2 ở bản đầu. Bản script hiện tại bỏ qua `MOVES.txt`, `MOVES.tsv`, `EXPECT.tsv`, `.DS_Store`.
- Một file chỉ ghi production một lượt. Lượt 2 cần EXPECT có md5 mới (lấy bằng `md5sum` trên server), vì `make_expect.py` so với bản `srv/` lúc đầu.
- Trang đăng nhập có thể trả 302, không phải 200. So với mốc đo trước, không so với số mong đợi trong đầu.
