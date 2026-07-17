# Bộ Email Templates — Báo cáo & Nghiệm thu dự án SEO (Team Account)

> **Nguồn chuẩn hóa:** mẫu email hiện hành tại `GTV Ops/wiki/account/` (3. MẪU BÁO CÁO CÔNG VIỆC HÀNG THÁNG + 3.1 THÁNG CUỐI) + điều khoản nghiệm thu/thanh toán trong hợp đồng mẫu (CareerViet, PVI, Minh Tuấn Mobile).
> **Phiên bản:** v1 — 07/2026.

## Quy ước dùng template

- `{...}` = dữ liệu **tự động** lấy từ hệ thống (dashboard/sheet) — Account chỉ kiểm tra lại.
- `[...]` = Account **điền tay** theo hợp đồng và tình hình dự án.
- ⚖️ = câu chữ có giá trị pháp lý — **không tự ý sửa**, chỉ thay biến số cho khớp hợp đồng.
- 📖 **Tên hạng mục trong mọi bảng chép NGUYÊN VĂN từ PL01** — theo sheet `1B. SOW MAPPING` của file quản lý dự án (xem `account-report_SOW-KPI-Naming-Standard_v1.md`). Tên nội bộ/tên tool (Apply Thanks, cloudstack…) không xuất hiện trong email gửi khách; nếu cần chú thích kỹ thuật thì đặt trong ngoặc sau tên hợp đồng.
- Mỗi dự án có nhịp nghiệm thu khác nhau (PVI: đợt 2 tháng · CareerViet: đợt 3 tháng · Minh Tuấn Mobile: hàng tháng). Chọn đúng template theo loại kỳ báo cáo.

### ⚠️ Điểm pháp lý phải khớp hợp đồng (lỗi phát hiện ở mẫu cũ)

Mẫu email cũ ghi cứng "**04 ngày**" cho thời hạn khách xác nhận, trong khi hợp đồng (vd CareerViet Điều 5.2 PL01) quy định "**07 ngày làm việc**". Từ v1 này, thời hạn xác nhận là **biến `[X ngày làm việc]` chép đúng từ hợp đồng từng dự án**. Tương tự với thời hạn thanh toán (05/10/15 ngày tùy hợp đồng) và số ngày tạm ngưng tối đa.

---

## TEMPLATE 1 — Email báo cáo tiến độ & KPI hàng tháng (kỳ KHÔNG gắn thanh toán)

**Dùng khi:** tháng nằm giữa đợt nghiệm thu (chưa đến mốc thanh toán), hoặc dự án nghiệm thu theo đợt nhiều tháng. Mục đích: chốt kết quả tháng bằng email làm căn cứ cộng dồn cho BBNT đợt.

**Tiêu đề:** `[GTV SEO] – BÁO CÁO TIẾN ĐỘ & KPI DỰ ÁN {Tên dự án} – THÁNG THỨ {n} ({MM/YYYY})`

```
Kính gửi: Anh/Chị [tên người nhận chính]
          [TÊN CÔNG TY ĐẦY ĐỦ THEO HỢP ĐỒNG]

GTV SEO kính gửi anh/chị báo cáo tiến độ và KPI của dự án SEO tháng thứ {n}
(kỳ dữ liệu {từ ngày} – {đến ngày}), cụ thể như sau:

1. KẾT QUẢ KPI ĐẠT ĐƯỢC

| LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | TỶ LỆ HOÀN THÀNH THỰC TẾ | TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU | LINK BÁO CÁO |
|---|---|---|---|---|---|---|
| {Organic Traffic/Pageview} | {mô tả chỉ số + nguồn đo theo Tài liệu kỹ thuật HĐ} | {cam kết} | {kết quả} | {%} | {% (tối đa 100%)} | {link} |
| TOP | {Bộ từ khóa ...} — TOP {3/5/10} | {%} | {%} | {%} | {% (tối đa 100%)} | {link} |
| {Nguyên liệu/Công việc} | {hạng mục} | {số lượng} | {số lượng} | {%} | {%} | {link} |
| **KẾT QUẢ KPI THÁNG** | | | | | **{%}** | |

→ GTV đã hoàn thành {…}% KPI theo lộ trình cam kết của tháng thứ {n}.
   [1 câu nhận định: vượt/đạt/chưa đạt hạng mục nào, vì sao — viết ngắn, trung thực.]

Lưu ý về dữ liệu:
- Thứ hạng từ khóa lấy từ SpySERP – kiểm tra tại [google.com / google.com.vn —
  đúng thị trường quy định trong hợp đồng], khu vực Việt Nam, ngày tracking {dd/mm}.
  [Nếu HĐ có quy tắc TOP lồng nhau (TOP 5 ⊂ TOP 10) thì ghi rõ cách đếm tại đây.]
  Khuyến khích anh/chị kiểm tra trong 2–3 ngày kể từ ngày nhận báo cáo để sai số
  so với thời điểm chụp dữ liệu không quá lớn.
- Traffic/Pageview tải từ Google Analytics 4 theo đúng cách đo thống nhất tại
  [Tài liệu kỹ thuật đính kèm hợp đồng].

2. BÁO CÁO TIẾN ĐỘ CÔNG VIỆC THÁNG {n}

| STT | Tên công việc | Thời hạn | Trạng thái | Kết quả/Link |
|---|---|---|---|---|
| {tự động từ sheet Kế hoạch} | | | | |

3. VẤN ĐỀ PHÁT SINH / TỒN ĐỌNG & HÀNH ĐỘNG PHỐI HỢP
[Chỉ ghi khi có — theo 3 nhóm: (a) tiến độ chỉnh sửa web — bên nào giữ, ảnh hưởng
KPI ra sao, action 2 bên; (b) thay đổi từ phía khách ảnh hưởng KPI; (c) content
chậm/delay duyệt — hạng mục nào, cần khách làm gì, deadline nào.]

4. VIỆC CẦN ANH/CHỊ PHỐI HỢP TRONG THÁNG TỚI  ← (mục mới — luôn có, tối đa 3 gạch đầu dòng)
- [việc 1 — deadline]
- [việc 2 — deadline]

5. KẾ HOẠCH THÁNG TIẾP THEO
Kế hoạch tháng thứ {n+1} đã cập nhật tại: {link Báo cáo công việc}.
Toàn bộ file dự án tại: {link Folder báo cáo} · Dashboard theo dõi real-time: {link}.

⚖️ Nhờ anh/chị kiểm tra và phản hồi xác nhận kết quả KPI nêu tại mục 1 & 2 qua email
này trong vòng [X ngày làm việc — chép đúng hợp đồng] kể từ ngày nhận báo cáo, để hai
bên thống nhất số liệu làm căn cứ nghiệm thu đợt theo Hợp đồng số [số HĐ].
⚖️ Nếu sau [Y ngày làm việc — theo hợp đồng] GTV chưa nhận được phản hồi chính thức
qua email, [chọn đúng theo hợp đồng dự án: "kết quả báo cáo được xem là đã được chấp
thuận" HOẶC "GTV sẽ tạm dừng triển khai các hạng mục tiếp theo cho đến khi hai bên
thống nhất kết quả; thời gian tạm ngưng được cộng dồn vào tiến độ dự án, tối đa
[Z] ngày"].

Trân trọng cảm ơn anh/chị!
[Chữ ký Account: Họ tên – Account Manager, GTV SEO – SĐT – email]
```

---

## TEMPLATE 2 — Email báo cáo NGHIỆM THU ĐỢT/GIAI ĐOẠN (kỳ gắn thanh toán)

**Dùng khi:** kết thúc đợt theo hợp đồng (2–3 tháng/đợt, hoặc tháng với hợp đồng nghiệm thu hàng tháng). Email này mở thủ tục: xác nhận KPI → ký BBNT → đề nghị thanh toán → xuất hóa đơn.

**Tiêu đề:** `[GTV SEO] – BÁO CÁO NGHIỆM THU ĐỢT {k} DỰ ÁN {Tên dự án} (THÁNG THỨ {m}–{n}) – ĐỀ NGHỊ XÁC NHẬN KPI`

```
Kính gửi: Anh/Chị [tên]
          [TÊN CÔNG TY ĐẦY ĐỦ]

Căn cứ Hợp đồng dịch vụ SEO số [số HĐ] ký ngày [ngày], GTV SEO kính gửi anh/chị
báo cáo kết quả triển khai ĐỢT {k} (từ tháng thứ {m} đến tháng thứ {n}, kỳ dữ liệu
{từ ngày} – {đến ngày}) và đề nghị nghiệm thu như sau:

1. KẾT QUẢ KPI LŨY KẾ CỦA ĐỢT
[Bảng KPI như Template 1 — số liệu lũy kế đúng theo cách tính của hợp đồng
(trung bình cộng các hạng mục / lũy kế theo timeline PL01). Ghi rõ:]

→ Tỷ lệ hoàn thành bình quân của đợt: {…}% — [đạt/không đạt] ngưỡng nghiệm thu
   tối thiểu [75% — theo hợp đồng] quy định tại [điều khoản].
→ ⚖️ Tỷ lệ hoàn thành để nghiệm thu của mỗi hạng mục tính tối đa 100%; phần vượt
   cam kết của hạng mục này không bù cho phần thiếu của hạng mục khác.

2. HẠNG MỤC CÔNG VIỆC ĐÃ TRIỂN KHAI TRONG ĐỢT
[Bảng công việc như Template 1 — gộp các tháng của đợt, kèm link bằng chứng từng dòng.]

3. HỒ SƠ NGHIỆM THU & THANH TOÁN KÈM THEO
Sau khi anh/chị xác nhận kết quả trên, GTV sẽ gửi bộ hồ sơ thanh toán đợt {k} gồm:
  (1) Báo cáo tiến độ & KPI đạt được của đợt (chính là email này + file đính kèm);
  (2) Biên bản nghiệm thu đợt {k} — số [.../GTV/NT-...] (ký 2 bên);
  (3) Đề nghị thanh toán đợt {k}: {số tiền} VNĐ (đã gồm VAT) — theo [Điều/PL];
  (4) Hóa đơn giá trị gia tăng hợp lệ.

⚖️ TRÌNH TỰ & THỜI HẠN (theo hợp đồng):
- Anh/chị vui lòng phản hồi email xác nhận "Đồng ý nghiệm thu kết quả KPI theo
  báo cáo" trong vòng [X ngày làm việc] kể từ ngày nhận báo cáo này.
- Sau khi nhận xác nhận, GTV gửi BBNT (bản ký) + Đề nghị thanh toán + Hóa đơn GTGT.
- Bên A thanh toán trong vòng [10/15/05 ngày làm việc — theo hợp đồng] kể từ ngày
  nhận đủ hồ sơ thanh toán hợp lệ.
- ⚖️ Nếu sau [Y ngày làm việc] GTV không nhận được phản hồi chính thức, GTV sẽ
  [điều khoản mặc nhiên chấp thuận / tạm ngưng — chép đúng hợp đồng dự án].

4. VẤN ĐỀ TỒN ĐỌNG & KẾ HOẠCH ĐỢT TIẾP THEO
[Ngắn gọn như Template 1 mục 3 + 5.]

Trân trọng cảm ơn anh/chị!
[Chữ ký Account]
```

---

## TEMPLATE 3 — Email báo cáo THÁNG CUỐI + nghiệm thu tổng & thanh lý hợp đồng

**Tiêu đề:** `[GTV SEO] – BÁO CÁO KPI THÁNG CUỐI & ĐỀ NGHỊ NGHIỆM THU TỔNG DỰ ÁN {Tên dự án} – HỢP ĐỒNG SỐ [số HĐ]`

```
Kính gửi: Anh/Chị [tên]
          [TÊN CÔNG TY ĐẦY ĐỦ]

GTV SEO kính gửi anh/chị báo cáo KPI tháng cuối và kết quả tổng của dự án SEO
theo Hợp đồng số [số HĐ]:

1. KẾT QUẢ KPI TOÀN DỰ ÁN
[Bảng KPI tổng — đối chiếu từng hạng mục cam kết tại PL01 với kết quả cuối cùng.
Nếu có hạng mục <100%: ghi rõ tỷ lệ và cách xử lý theo PL02 (gia hạn / hoàn trả
theo công thức / không tính phí hạng mục), trung thực, không làm tròn có lợi.]

→ GTV SEO hoàn thành {…}% KPI cam kết tại Hợp đồng số [số HĐ]. GTV chân thành
cảm ơn Quý công ty đã tin tưởng và phối hợp trong suốt {n} tháng triển khai.

2. BÁO CÁO CÔNG VIỆC THÁNG CUỐI + TỔNG HỢP BÀN GIAO
- Bảng công việc tháng cuối [như Template 1].
- Danh mục bàn giao: {link folder tổng — content, technical, entity, backlink,
  tài khoản, hướng dẫn vận hành}.

3. DỮ LIỆU CHUYỂN ĐỔI & GIÁ TRỊ KINH DOANH (nếu có tracking)
[Time on site, bounce rate + chuyển đổi trực tiếp (Call/Form/Mess) từ Organic —
kèm file PDF tải từ GA4. Đề nghị khách đối chiếu số liệu kinh doanh thực tế.]

4. ĐỀ XUẤT HỌP NGHIỆM THU TỔNG
GTV đề xuất buổi họp nghiệm thu tổng hợp đồng vào [giờ], ngày [dd/mm/yyyy]
([online/offline]). Nhờ anh/chị xác nhận lịch để GTV chuẩn bị.

⚖️ TRÌNH TỰ NGHIỆM THU – THANH LÝ:
- Anh/chị phản hồi "Đồng ý nghiệm thu kết quả KPI theo báo cáo" trong vòng
  [X ngày làm việc] để GTV hoàn thiện: (1) Biên bản nghiệm thu & thanh lý hợp
  đồng; (2) Đề nghị thanh toán đợt cuối; (3) Hóa đơn GTGT đợt cuối.
- ⚖️ Sau [Y ngày làm việc] không có phản hồi, báo cáo nghiệm thu được xem là đã
  được chấp thuận theo [điều khoản], GTV tiến hành thủ tục thanh lý hợp đồng.
- Sau nghiệm thu, dự án chuyển sang giai đoạn BẢO HÀNH KẾT QUẢ trong 30 ngày:
  GTV bảo đảm duy trì tối thiểu [90%] kết quả nghiệm thu (dự phòng [10%] rủi ro
  thuật toán Google) theo [điều khoản bảo hành].
- [Nếu hợp đồng có cơ chế đối soát PL02: "Sau nghiệm thu tổng, hai bên đối soát
  giá trị thực hiện thực tế theo Phụ lục 02; phần chênh lệch (nếu có) hoàn trả
  trong vòng [15] ngày làm việc kể từ ngày ký biên bản nghiệm thu tổng."]

5. ĐỀ XUẤT GIAI ĐOẠN DUY TRÌ  ← (Account luôn chốt mục này — theo SOP T10)
Website dừng xuất bản và tối ưu sẽ mất dần vị trí theo chu kỳ Grow–Maintain–Decline.
GTV đề xuất phương án Duy trì kết quả: [1–2 dòng gói duy trì + lịch trao đổi].

Trân trọng cảm ơn anh/chị!
[Chữ ký Account]
```

---

## TEMPLATE 4 — Follow-up khi khách chưa phản hồi xác nhận

**4a. Nhắc lần 1** (sau 1/2 thời hạn xác nhận — vd ngày thứ 3–4 của thời hạn 7 ngày):

```
Tiêu đề: RE: [tiêu đề email báo cáo gốc] – NHẮC XÁC NHẬN KẾT QUẢ KPI

Kính gửi anh/chị [tên],
GTV xin phép nhắc về báo cáo [tháng thứ n / đợt k] gửi ngày [dd/mm]. Theo
[điều khoản] Hợp đồng số [số HĐ], thời hạn xác nhận kết quả là [X ngày làm việc]
(đến hết ngày [dd/mm]). Nhờ anh/chị sắp xếp kiểm tra và phản hồi giúp GTV — nếu
anh/chị cần GTV giải thích thêm bất kỳ số liệu nào, em sẵn sàng call nhanh 15 phút.
Trân trọng!
```

**4b. Nhắc lần 2 — thông báo hệ quả theo hợp đồng** (ngày cuối thời hạn; đồng thời Account escalate nội bộ theo SOP):

```
Tiêu đề: RE: [tiêu đề gốc] – THÔNG BÁO HẾT THỜI HẠN XÁC NHẬN KẾT QUẢ KPI

Kính gửi anh/chị [tên],
Hôm nay là ngày làm việc thứ [X] kể từ ngày GTV gửi báo cáo [tháng n / đợt k]
(ngày [dd/mm]). ⚖️ Theo [điều khoản] Hợp đồng số [số HĐ], nếu hết ngày [dd/mm]
GTV chưa nhận được phản hồi chính thức qua email: [chép đúng hệ quả trong hợp
đồng — "kết quả được xem là đã chấp thuận và GTV tiến hành thủ tục tiếp theo"
HOẶC "GTV tạm dừng triển khai các hạng mục tiếp theo; thời gian tạm ngưng cộng
dồn vào tiến độ dự án"].
GTV rất mong nhận được phản hồi của anh/chị để dự án giữ đúng tiến độ.
Trân trọng!
```

---

## Checklist Account trước khi bấm gửi (mọi template)

- [ ] Tên mọi hạng mục khớp NGUYÊN VĂN sheet SOW MAPPING (= PL01); không có dòng nào ngoài SOW lẫn trong bảng nghiệm thu.
- [ ] Số liệu KPI khớp dashboard/sheet nguồn, kỳ dữ liệu ghi rõ từ ngày–đến ngày.
- [ ] "Tỷ lệ hoàn thành để nghiệm thu" đã cap 100% từng hạng mục; cách tính bình quân đúng theo hợp đồng dự án.
- [ ] Các biến ⚖️ (X/Y/Z ngày, số HĐ, số tiền, % ngưỡng, hệ quả không phản hồi) **chép đúng từ hợp đồng của dự án đó** — không copy từ dự án khác.
- [ ] Link báo cáo mở được ở quyền của khách (Comment/View).
- [ ] Mục "Việc cần anh/chị phối hợp" có deadline cụ thể.
- [ ] Tiếng Việt đủ dấu, không lỗi tên khách/công ty; đúng người nhận + CC đúng đầu mối 2 bên.
