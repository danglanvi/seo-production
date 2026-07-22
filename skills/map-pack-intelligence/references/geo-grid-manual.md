# Geo-Grid Manual Protocol — đo tay chuẩn (Tier 2/3)

> Dùng bởi `map-pack-intelligence` khi không có API. Mục tiêu: kết quả lặp lại được — sai lệch phương pháp giữa 2 kỳ đo làm SoLV không so sánh được.

## 1. Dựng lưới tọa độ

1. Lấy tọa độ trung tâm = địa chỉ chi nhánh (SAB: trọng tâm service area). Cách lấy: right-click trên Google Maps → copy lat,lng.
2. Sinh điểm lưới cách đều. Quy đổi nhanh: **0,01° lat ≈ 1,11 km**; 0,01° lng ≈ 1,04 km tại vĩ độ VN (~10-21°). Vd lưới 5x5 bán kính 2km → bước ≈ 1km → offset ±0,009° lat, ±0,0096° lng quanh tâm.
3. Ghi bảng điểm: ID (A1…E5) · lat,lng · mô tả khu vực (phường/landmark) — bảng này tái sử dụng mọi kỳ đo, KHÔNG dựng lưới mới mỗi kỳ.

## 2. Giả lập vị trí trên desktop (phương pháp chính Tier 2)

Per điểm × per query:

1. Chrome **Incognito** (không đăng nhập Google — bắt buộc).
2. DevTools (F12) → Command Menu (Ctrl/Cmd+Shift+P) → "Show Sensors" → Location → **Other…** → dán lat,lng điểm lưới.
3. Mở `google.com/maps` (hoặc google.com rồi query có local intent) → search query → cho phép/không cho phép location prompt một cách NHẤT QUÁN giữa mọi điểm (khuyến nghị: dùng Maps, Maps đọc sensor override trực tiếp).
4. Ghi kết quả (mục 4). Đóng incognito, mở phiên mới cho điểm kế (tránh location cache).

**Biến thể UULE:** encode tọa độ/canonical name vào tham số `uule=` của URL search Google — dùng khi cần script hóa hàng loạt. Lưu ý: UULE encode theo canonical location name (thô hơn tọa độ tự do); nếu cần độ phân giải dưới cấp phường → dùng sensor override. Chọn MỘT phương pháp cho cả kỳ đo, ghi vào mục Phương pháp của output.

## 3. Thực địa spot-check (kiểm chứng) & Tier 3 screenshot

- **Thực địa:** chọn 3-5 điểm đại diện (tâm + 4 góc), đến nơi, điện thoại 4G (không Wi-Fi cố định), chế độ ẩn danh/không đăng nhập, search query, chụp màn hình. Dùng để kiểm chứng phương pháp giả lập — lệch nhiều giữa giả lập và thực địa → ghi caveat, ưu tiên số thực địa.
- **Tier 3 (khách tự chụp):** gửi khách bảng điểm (mục 1, kèm link Maps từng tọa độ) + hướng dẫn: đứng gần vị trí đó hoặc set vị trí, ẩn danh, search đúng query, chụp cả màn hình có top 3. Nhận ảnh → nhập bảng, ô không có ảnh = ⬜.

## 4. Template ghi số

| Điểm | Lat,Lng | Query | Vị trí mình | Top 1 | Top 2 | Top 3 | Giờ đo |
|---|---|---|---|---|---|---|---|
| A1 | 10.78,106.69 | nha khoa quận 3 | 2 | Đối thủ A | **Mình** | Đối thủ B | 14:20 |

Quy ước "Vị trí mình": 1-3 (trong pack — mở "More places" xác nhận thứ tự nếu cần) · 4-20 (thứ hạng trong local finder) · ∅ (không thấy trong 20).

## 5. Kỷ luật đo (bắt buộc để so kỳ)

- Cùng **khung giờ** (±2h) và cùng **ngày trong tuần** giữa các kỳ.
- Cùng phương pháp (sensor override HOẶC UULE HOẶC thực địa — không trộn trong 1 kỳ, trừ spot-check kiểm chứng ghi riêng).
- Cùng ngôn ngữ/quốc gia trình duyệt (vi-VN).
- Đo hết 1 query trên toàn lưới rồi mới sang query kế (giảm drift thời gian trong 1 query).
- Lưu raw (bảng mục 4 + screenshots) vào folder project — SoLV tính lại được khi cần verify.
