# OS và MySQL hết hạn hỗ trợ: không tăng phí tháng

Nguồn: lane kiểm chỉ đọc và phản biện trên VPS site agency mẫu 23/10/2026 (Ubuntu 20.04, MySQL 5.7, aaPanel, OLS). Phương án đã qua phản biện nhưng chưa chạy thật lúc ghi file này. Lịch chạy của site mẫu: đêm 29→30/10/2026. Sau khi chạy, cập nhật file này theo kết quả.

## 1. Chọn đường

| Đường | Khi nào chọn | Lý do loại hoặc chọn ở site mẫu |
|---|---|---|
| Gắn Ubuntu Pro bản miễn phí (esm-infra, esm-apps) | Chủ server đủ điều kiện bản miễn phí | Chọn. 0 đồng. 231 bản vá chờ, gồm kernel, OpenSSL 1.1, OpenSSH, glibc. Hạn vá kéo thêm 5 năm |
| `do-release-upgrade` tại chỗ | Không chọn khi panel, MySQL hoặc Redis link `libssl.so.1.1` | Ubuntu 22.04 và 24.04 không có `libssl.so.1.1`. Phải nâng 2 lần. Repo lsphp bản mới không có lsphp74. Ước 2–4 giờ dừng mọi site |
| Nâng MySQL trên máy cũ | Không chọn khi RAM < 4 GB | Panel phải dump, gỡ, cài lại. Script biên dịch MySQL 8 đòi ≥ 4.096 MB RAM trống |
| Đổi máy cùng giá | Đến kỳ gia hạn và nhà cung cấp có gói ≥ cấu hình cũ với giá ≤ phí cũ | Dựng OS mới, chuyển site, đổi DNS trong 14 ngày cuối kỳ cũ, không gia hạn máy cũ |
| Mua Pro trả phí | Không chọn | Tăng phí |

Điều kiện bản miễn phí: Canonical ghi theo 3 cách ở 3 trang (ubuntu.com/pro, Ubuntu Pro FAQ, tài liệu Pro), từ "personal use" tới "small-scale commercial use", tối đa 5 máy. Canonical không nói rõ VPS thuê có tính là máy của mình không. Agent trích nguyên văn 3 câu cho Lead. Agent không kết luận pháp lý.

MySQL cũ giữ sau loopback: kiểm MySQL chỉ nghe `127.0.0.1` và firewall chỉ mở 22, 80, 443, cổng panel. Pro không vá MySQL, Redis, OLS và lsphp nếu các gói này không lấy từ kho Ubuntu.

## 2. Các bước gắn Pro

1. Backup ngoài máy: dump mọi DB, `/etc`, cấu hình web server, cấu hình vhost của panel. Kiểm sha256. Hỏi nhà cung cấp có snapshot không và giá bao nhiêu.
2. Gỡ kernel cũ bằng `apt-get purge` đúng tên gói image, modules, headers. Không dùng `autoremove`, vì lệnh đó có thể gỡ gói như `ssl-cert`.
3. `apt-mark hold` mọi gói lấy từ repo ngoài kho Ubuntu (lsphp, web server). Nâng các gói này là việc riêng.
4. `pro attach --attach-config <file>`: file quyền 600 chứa token và `enable_services: [esm-infra, esm-apps]`. Xoá file sau khi attach. Cách này không đưa token vào dòng lệnh và không bật livepatch.
5. Mô phỏng: `apt-get update`, rồi `apt-get -s dist-upgrade`. Danh sách có gói bị gỡ ngoài kernel cũ thì dừng.
6. Chạy cả chuỗi trong một lệnh: `systemd-run --wait --unit=pro-upgrade sh -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold dist-upgrade'`. `dist-upgrade` cài kernel ESM mới mà `upgrade` giữ lại.
7. Reboot. Dựng lại mount không nằm trong `fstab`, ví dụ bind mount `uploads` của staging. Kiểm MySQL theo `references/danh-muc-viec.md` mục 5.
8. unattended-upgrades tự cài gói ESM sau khi attach. Lead chọn: giữ và dời giờ chạy ra khỏi giờ lane, hoặc tắt nguồn ESM và vá tay mỗi tháng. Giữ `Automatic-Reboot "false"`.

Trả lại: kernel chọn bản cũ ở GRUB. Gói userspace (libssl, systemd, glibc) không hạ được bằng apt. Đường lui là snapshot hoặc dựng lại từ backup bước 1. `pro detach` chỉ gỡ nguồn ESM, không hạ gói.

Kiểm sau: `pro security-status` về 0 gói chờ, `uname -r` là kernel ESM, `apt-mark showhold` còn đủ gói, mọi site 200, TTFB hit và miss không chậm hơn mốc.

## 3. Đổi máy cùng giá

- Chỉ làm khi đủ 2 điều kiện: gói mới có CPU, RAM, ổ không thấp hơn máy cũ với giá ≤ phí cũ, và máy cũ sắp tới kỳ gia hạn.
- Phí thêm một lần ≤ 14 ngày phí gói mới. Ghi rõ kỳ trả trước tối thiểu của từng dòng gói.
- So đời CPU. Dòng gói rẻ có thể dùng CPU đời cũ, nên TTFB trượt cache chậm hơn. Đo TTFB miss trong thời gian được hoàn tiền, ngưỡng ≤ mốc cũ + 10%.
- Đích DB: bản MariaDB LTS mới nhất mà panel hỗ trợ. MySQL 8.0 hết hỗ trợ 30/04/2026.
- Điều kiện trước, làm trên máy cũ: chuyển site còn chạy PHP hết hỗ trợ lên bản PHP mà OS mới có.
