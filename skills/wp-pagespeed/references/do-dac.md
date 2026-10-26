# Đo đạc: PSI, mô phỏng Chrome, ảnh chụp, bản đồ font

Đọc file này ở Bước 2. Mọi script nằm ở `$WPS/scripts/` (cách đặt `WPS`: SKILL.md, mục đường dẫn). Đặt `"$WPS"` trong nháy, vì đường dẫn có thể có dấu cách.

## 1. Chọn công cụ

| Tình huống | Công cụ | Lý do |
|---|---|---|
| Production, baseline và nghiệm thu | `psi_run.py` + `psi_table.py` | Số giống PSI mà chủ site và khách thấy |
| Đo nhanh một template sau một đợt sửa | `perf_probe.mjs` 3 lượt | 1 phút mỗi template, không tốn quota PSI |
| Staging có Basic Auth | `perf_probe.mjs` với `CDP_AUTH` | PSI không vào được staging |
| So staging với production | `perf_probe.mjs` trên cả 2, so bằng `probe_table.py` | Cùng máy, cùng mạng mô phỏng |
| Kiểm chức năng và bố cục | `shot.mjs` + `shot_cmp.py` | Bắt lỗi do sửa, không đo tốc độ |
| Kiểm font thật sự vẽ | `fontmap.mjs` | CSS khai báo khác font Chrome dùng |
| Lấy danh sách template | `templates.php` qua `wp eval-file` | Một lệnh thay cho nhiều truy vấn |
| Hiện tượng chỉ PSI thấy, Chrome trên máy không tái hiện | A/B trên PSI (mục 3 dưới) | Chrome của PSI xử lý font và ưu tiên tải khác Chrome trên máy |
| Tự host font Google Fonts | `gfonts_selfhost.py` | Giữ đúng subset, `unicode-range`, thứ tự rule |
| Kiểm font tự host hiển thị giống bản cũ | `font_same.mjs --a <trước> --b <sau>` | So bề rộng chữ, khung phần tử, chiều cao trang |
| Đề xuất đổi cách nạp tracking | `gtm_inventory.py --url <trang>` | Biết hoãn GTM sẽ mất sự kiện nào |
| Tìm phần tử gây CLS và nó dịch bao nhiêu px, từng nhánh dữ liệu | `cls_trace.mjs --url <trang> [--session '<json>'] [--net fast]` | In toạ độ trước > sau của từng shift, nạp sẵn storage |
| Dựng và đo biến thể HTML cho A/B trên PSI | `psi_ab.py build/upload/urls/table/quarantine` | Regex phải khớp đúng số lần, danh sách URL xen kẽ |
| Kiểm loader GTM hoãn sau khi cài | `gtm_delay_check.mjs --url <trang>` | 4 trường hợp, chặn hit thật, không cuộn |
| Kiểm robots, canonical và nhãn cache sau PSI, purge hoặc làm nóng | `cache_variants.py <url sạch> ...` | 5 biến thể cache: desktop và mobile có hoặc không có WebP, Googlebot smartphone |
| Quyết định A/B khi PSI nhiễu | `psi_decide.py` | Một nhãn theo ngưỡng đặt trước, gỡ lệch máy PSI |
| CLS chỉ PSI thấy | `psi_cls_dump.py`, `lh_local.mjs --block-vary` | Xem PSI thấy gì, dựng lại môi trường PSI (`cls-chi-psi-thay.md`) |
| Làm nóng, đo tỉ lệ hit theo bản cache | `lam_nong.sh` | 4 bản cache, Accept có WebP, TSV mã, nhãn cache, TTFB |
| Bảng "Phần còn trừ điểm", chi phí theo nguyên nhân | `psi_con_tru.py [--mt]` | Audit có trọng số dưới 0,9 ở 5 hạng mục, `styleLayout`, font, TBT |
| Bề rộng hiển thị của ảnh ở 360–1920 px | `img_display_width.mjs`, `img_width_report.py` | Ảnh thừa hoặc mờ, trước khi đổi `srcset`, `sizes` |
| Loại trừ JS của LiteSpeed cho loader, pixel | `ls_exclusions_check.py` | Guest Mode dùng danh sách riêng (`fcp-guest-mode.md`) |

## 2. PSI

```bash
python3 -I "$WPS/scripts/psi_run.py" --urls urls.tsv --out psi-base --runs 3 --dry-run
python3 -I "$WPS/scripts/psi_run.py" --urls urls.tsv --out psi-base --runs 3 --detach
cat psi-base/PSI_STATE.txt
python3 -I "$WPS/scripts/psi_table.py" psi-base [psi-sau ...] [--detail]
```

- `--dry-run` in số lượt cần đo và thời gian ước tính, không gọi API.
- Script từ chối chạy tiền cảnh khi ước tính trên 8 phút (mã thoát 5). Lệnh tiền cảnh dài bị cắt hoặc làm phiên treo. Chọn một trong hai cách:
  - Runtime có chế độ chạy nền và báo khi lệnh xong: chạy lệnh ở chế độ đó, thêm `--fg-ok`.
  - Runtime không có chế độ đó: thêm `--detach`. Sau thời gian ước tính, đọc `<out>/PSI_STATE.txt` bằng một lệnh ngắn. File ghi `RUNNING` khi đang chạy, `DONE lỗi=<n> exit=<mã>` khi xong.
  - Không viết vòng `sleep` để chờ. Không đọc log liên tục.
- `--jobs 2` là mặc định: 2 lượt chạy đồng thời. Script xếp lượt xen kẽ theo vòng, URL, thiết bị, nên mọi URL rải đều theo giờ.
  - Tổng request đồng thời lên một site không quá 2, tính cả lane khác đang đo cùng site.
  - `--jobs 3` hoặc `4` chỉ khi `cache_variants.py` báo hit đủ 5 biến thể và workstream cho phép. Thêm `--jobs-ok` để xác nhận.
- Mỗi mốc đo dùng một thư mục chung `<ev>/psi-<mốc>`. Lane khác cần số cùng mốc thì đọc thư mục đó. Không chép `psi_run.py` vào thư mục lane, gọi thẳng `"$WPS/scripts/psi_run.py"`.
- `psi_run.py` tìm `PAGESPEED_API_KEY` trong `.agent-secrets/.env` từ thư mục hiện tại trở lên. Script không ghi key vào file hay log.
- Script làm nóng cache bằng UA có chữ `Chrome-Lighthouse` trước lượt đầu. LiteSpeed tách cache theo UA, nên làm nóng bằng UA thường không đủ. Lượt làm nóng gửi `Accept` có `image/webp` như Chrome của PSI, vì rewrite WebP theo `Accept` tách thêm một biến thể cache (`checklist-theo-lop.md` lớp 1).
- Script bỏ qua file đã có. Lượt lỗi chạy lại thì chỉ đo phần thiếu.
- Chỉ đo URL sạch, hoặc URL có một tham số nằm trong danh sách không cache của plugin (LiteSpeed: option `cache-exc_qs`). `psi_run.py` từ chối URL có `utm_*`, `fbclid`, `gclid`, `_ga`. Lý do:
  - LiteSpeed bỏ các tham số này khỏi khoá cache (option `cache-drop_qs`).
  - Nhiều theme và plugin SEO trả `noindex` và bỏ canonical cho URL có query.
  - Lượt PSI đầu khi cache trống ghi bản `noindex` đó vào cache của URL sạch. Site agency mẫu 21/10: 4 lượt PSI `?utm_source=` lúc 21:57–21:58 làm Googlebot smartphone nhận `noindex` ở trang chủ và /blog/ khoảng 50 phút.
- PSI trả kết quả cache cho cùng một URL trong vài phút. Cần nhiều lượt liên tiếp trên trang thật thì xen kẽ nhiều URL, hoặc dùng tham số nằm trong `cache-exc_qs` (ví dụ `?nc=<số>`). Đọc option trước. Thêm tham số vào option là đổi config, cần duyệt riêng.
- Sau mỗi đợt PSI, chạy `cache_variants.py` trên URL sạch đã đo. Lệnh trả exit 1 khi robots hoặc canonical lệch giữa các biến thể.
- Mặc định chỉ đo hạng mục performance. `--categories performance,accessibility,best-practices,seo,agentic-browsing` đo cả 5 hạng mục trong một lượt (khoảng 12–15 giây mỗi URL). Bước 5 bắt buộc một lượt 5 hạng mục cho mọi URL, cả 2 thiết bị.
- Lập bảng "Phần còn trừ điểm" cho báo cáo nghiệm thu:

  ```bash
  python3 -I "$WPS/scripts/psi_con_tru.py" <ev>/psi-final <ev>/psi-final-5hm --urls <ev>/urls.tsv --mt
  ```

  - Bảng 1: điểm trung vị 5 hạng mục mỗi template và thiết bị. Ô `-` là chưa đo. Trước khi giao, output không còn mục `CHƯA ĐO ĐỦ 5 HẠNG MỤC` và dòng cuối ghi `thieu_hang_muc=0`.
  - Bảng 2: audit có trọng số và điểm dưới 0,9. Hạng mục performance chỉ có 5 chỉ số mang trọng số. Thêm `--diag` để xem audit chẩn đoán. Người làm điền cột "Lý do chưa sửa" cho từng dòng.
  - `--mt`: `styleLayout`, script, font KB và số file, tài nguyên chặn hiển thị, TBT. Dùng cho lớp 5b của `checklist-theo-lop.md`.
- Mỗi URL, mỗi thiết bị đo 3 lượt. So trung vị. Ô điểm của `psi_table.py` ghi mọi lượt để thấy độ dao động.
- Một lượt PSI mất 20–40 giây. 15 URL × 2 thiết bị × 3 lượt mất khoảng 25 phút với `--jobs 2`, gấp đôi nếu chạy tuần tự. `--dry-run` in ước tính cho danh sách thật.

Đọc số:

- Điểm lab dùng số mô phỏng (Lantern). Xem thêm cột `obs` (observed) của `psi_table.py`. Nếu số mô phỏng xấu mà observed tốt, nguyên nhân thường là tài nguyên chặn hiển thị có ưu tiên cao.
- FCP mô phỏng có 2 chế độ. Cùng một trang, FCP mobile có thể nhảy giữa khoảng 1,5 s và khoảng 3 s giữa các lượt. Đây là lý do phải lấy trung vị 3 lượt.
- Site bật LiteSpeed Guest Mode có thể cho cột observed giống nhau ở nhiều template (lượt thử 10/2026: FCP = LCP = 2,3 s ở 5/6 template mobile). Khi đó chỉ dùng observed để so giữa các lượt cùng trang. Script nạp font chặn hiển thị cũng cho dấu hiệu này (`checklist-theo-lop.md` lớp 4). Kiểm cả 2 nguyên nhân.
- Staging thường không bật LiteSpeed Cache, nên không có Guest Mode. Không dùng staging để đo thay đổi FCP liên quan Guest Mode. A/B trên production bằng `psi_ab.py`, hoặc đo bằng PSI sau khi lên production và giữ lệnh rollback sẵn.
- LCP observed muộn thì Lantern đưa request GTM, gtag, Pixel vào chuỗi mô phỏng của LCP. Site mẫu 2: LCP mô phỏng 5–8,6 s trong khi LCP observed dưới 0,6 s. Đọc observed và `lcp-breakdown-insight` trước khi sửa ảnh LCP.
- Lượt chậm ngẫu nhiên: site mẫu 2 có khoảng 1/3 lượt mobile với FCP observed 1,35–1,42 s. Trong các lượt này, HTML tải xong trước 0,25 s, font tải xong trước 0,5 s và không có tài nguyên chặn hiển thị. Trang đối chứng không đổi gì cũng gặp. Không truy nguyên từng lượt. Luôn đo kèm một URL đối chứng.
- Lượt chậm có thể dồn cả 3 lượt vào một URL. Site mẫu 2 (18/10): trang Doanh nghiệp đạt 61–63 điểm với 3/3 lượt FCP observed 1,48–1,56 s. Đo lại được 84, 90, 82. Nếu một URL có từ 2/3 lượt chậm, đo lại 3 lượt xen kẽ với 2 URL khác trước khi kết luận trang bị lùi.
- So trước và sau trong cùng một buổi đo. Mốc của buổi khác có thể lệch nhiều dù code không đổi. Site mẫu 2: trung vị mobile 11 template đạt 88 lúc rạng sáng và 75 lúc 15:30 cùng ngày.
- Tách lượt theo tốc độ máy PSI: đọc `lighthouseResult.environment.benchmarkIndex` trong JSON từng lượt. Hai nhóm lượt đo nối tiếp nhau có thể rơi vào máy nhanh và máy chậm. Site agency mẫu 24/10 (preload font `/website/`): bản A trung vị 94,5, bản C 88,5. Ba lượt A đầu chạy máy có `benchmarkIndex` 890–1088. Chỉ so lượt dưới 800 thì A và C cùng quanh 87–88. Đo xen kẽ hai bản cùng URL đối chứng trong cùng khung giờ, rồi so theo từng nhóm máy. Quyết định khi đó dựa vào chỉ số lệch nhất quán ở cả hai nhóm máy (ở đây FCP lab chậm hơn ở 11/12 lượt). `psi_decide.py` và `psi_ab.py table --split-bench` tách nhóm máy tự động (mục 3).
- CrUX (field) cập nhật theo cửa sổ 28 ngày. Không dùng CrUX để nghiệm thu một đợt sửa vừa xong.
- Đọc field trước khi đuổi chỉ số lab: `loadingExperience` (URL) và `originLoadingExperience` (origin) trong JSON PSI. `psi_table.py --detail` và `psi_cls_dump.py` in phần này. Luật dùng field: SKILL.md Bước 3 mục 0.
- Nguyên nhân CLS trong `layout-shifts` và `cls-culprits-insight` ("Phông chữ web") là phỏng đoán theo thời điểm font tải. Site mẫu 2: CLS 0,92 do JS ẩn khối sau lần vẽ đầu, PSI vẫn ghi nguyên nhân là font. Xem `screenshot-thumbnails`, `boundingRect` của phần tử, rồi đo bằng `cls_trace.mjs` (cả `--net fast`) trước khi sửa font.
- `cls_trace.mjs` trên Mac cho CLS nhỏ trong khi PSI cho CLS lớn: nghi font dự phòng. Máy Linux của PSI vẽ chữ chờ font bằng font khác Mac (`checklist-theo-lop.md` lớp 4).
- TBT là chỉ số lab. TBT không thay INP.

## 3. A/B trên PSI

Dùng khi PSI thấy một hiện tượng mà `perf_probe.mjs` không tái hiện. Site mẫu 2 tìm ra lỗi script nạp font bằng cách này.

1. Lưu HTML của trang thật bằng `curl`. Tạo một file cho bản gốc (`v0`) và một file cho mỗi thay đổi.
2. Đặt các file vào `wp-content/uploads/psi-ab/` của production. OpenLiteSpeed phục vụ file tĩnh này như trang thật, cùng server và cùng CDN.
3. Viết `urls.tsv` xen kẽ các biến thể. Mỗi dòng có một `?r=<số>` khác nhau. Chạy `psi_run.py --runs 1`. Mỗi biến thể cần ít nhất 4 dòng.
4. Thêm một URL đối chứng không đổi vào cùng danh sách.
5. Quyết định bằng `psi_decide.py` theo ngưỡng đã ghi trước khi đo.
6. Xong thì chuyển `psi-ab/` vào quarantine. Không xoá. Kiểm mọi URL bản tĩnh trả 404 hoặc 410.

Mọi bản HTML tĩnh, kể cả `v0`, phải có `<meta name="robots" content="noindex,nofollow">` và canonical trỏ chính nó. Site agency mẫu 22/10: 6 bản tĩnh A/B nằm công khai khoảng 30 phút với robots index và canonical trỏ URL gốc. `psi_ab.py build` tự chèn hai thẻ này. `upload` chạy `verify` trước và từ chối khi thiếu (mã 3).

Không đo một URL nhiều lượt liên tiếp. PSI trả kết quả cache: site mẫu 2 có 4 lượt liên tiếp giống hệt nhau.

Không A/B bằng công tắc tham số trong mu-plugin đang chạy production. Site agency mẫu 23/10 22:14–22:23: một lane thêm nhánh `?gtvdd_ab=` vào mu-plugin production để đổi CSS rồi đo 20 lượt PSI. Lần đó không hại vì tham số không nằm trong `cache-drop_qs`. Nếu tham số nằm trong option này, bản thử sẽ ghi đè cache của URL sạch. Cách đúng là bản HTML tĩnh qua `psi_ab.py`. Cách khác cần chủ site duyệt trước.

`scripts/psi_ab.py` làm các bước trên (lệnh mẫu ở đầu script):

```bash
python3 -I "$WPS/scripts/psi_ab.py" build --spec ab.json --dir <ev>/psi-ab-<tag> --site https://example.com --tag <tag> --a v0 --b v4 --min-gain 3 --lcp-ms 200 --cls 0.02
python3 -I "$WPS/scripts/psi_ab.py" verify --dir <ev>/psi-ab-<tag>
python3 -I "$WPS/scripts/psi_ab.py" upload --dir <ev>/psi-ab-<tag> --ssh <alias> --root <web root> --tag <tag> --apply
python3 -I "$WPS/scripts/psi_ab.py" urls --dir <ev>/psi-ab-<tag> --site https://example.com --tag <tag> > <ev>/urls-ab.tsv
python3 -I "$WPS/scripts/psi_run.py" --urls <ev>/urls-ab.tsv --out <ev>/psi-ab --runs 1 --devices mobile --detach
python3 -I "$WPS/scripts/psi_decide.py" <ev>/psi-ab --a v0 --b v4 --dev mobile
python3 -I "$WPS/scripts/psi_ab.py" table --psi <ev>/psi-ab --split-bench
python3 -I "$WPS/scripts/psi_ab.py" quarantine --ssh <alias> --root <web root> --tag <tag> --site https://example.com --dir <ev>/psi-ab-<tag> --apply
```

- `upload` và `quarantine` ghi lên server. Không có `--apply`, hai lệnh chỉ in lệnh sẽ chạy.
- `build` ghi ngưỡng vào `spec.json` (mục `decision`) và khoá ngưỡng sau lần build đầu. Build lại với ngưỡng khác bị từ chối (mã 2). Không đổi ngưỡng sau khi thấy số.
- `ab.json` khai trang gốc và biến thể. Mỗi biến thể là danh sách phép thay `re`/`sub` (khớp đúng `count` lần, sai thì script dừng) hoặc `html_class` (thêm class lên `<html>`).
- Bảng kết quả có điểm từng lượt, trung vị, TBT, LCP, `observedTraceEnd − observedLoad` lớn nhất (để chọn mốc hoãn GTM) và số lượt có long task của tracking.
- Trang cần regex khớp số lần khác nhau (ví dụ stack font có 2 chỗ ở landing, 0 chỗ ở bài viết): tách mỗi nhóm trang một spec, chạy `build` từng spec vào cùng `--dir`. `spec.json` gộp danh sách trang, nên `urls` và `table` thấy đủ.
- Bảng `table` không có CLS. Đọc CLS, điểm agentic và phần tử dịch chuyển từ JSON (`layout-shifts`), so cả LCP: một biến thể có thể đổi CLS lấy LCP (site mẫu 2, preload font: CLS 0,08 → 0 nhưng LCP mô phỏng 1,5 → 2,3 s).
- Kiểm tính năng của Chrome trên máy PSI (font `local()` nào có, API nào chạy): dựng trang thử in kết quả bằng `console.error(...)`, chạy PSI hạng mục `best-practices`, đọc chuỗi trong audit `errors-in-console`.

Quyết định trong nhiễu bằng `psi_decide.py`:

- Nhãn: tốt hơn, không đổi, xấu hơn, chưa đủ lượt. Dòng cuối là `PSI_DECIDE label=<...>`.
- Ngưỡng mặc định lấy từ site agency mẫu 10/2026: điểm 3, LCP 200 ms, CLS 0,02. Site khác hiệu chuẩn lại (skill `model-calibration`).
- Mỗi nhánh đo 3–5 lượt xen kẽ. Mã 0 là đã có nhãn: dừng đo. Mã 3 là chưa đủ lượt: đo thêm một vòng xen kẽ, tối đa `--max-runs 5`. Sau 5 lượt mà chênh vẫn dưới ngưỡng, nhãn là "không đổi".
- Hai nhánh lệch `benchmarkIndex` trên 20% thì script chỉ so trong nhóm máy có đủ lượt của cả hai nhánh.
- Site agency mẫu 23/10: một lane đo 7 đợt, khoảng 80 lượt mobile cho một URL, rồi vẫn kết luận không áp. Dừng ở nhãn đầu tiên tiết kiệm phần lớn số lượt đó.

Thử config cấp site trên mẫu trước. Trước khi áp một thay đổi cho mọi template (option LiteSpeed, font, mu-plugin dùng chung), A/B trên 4 URL thuộc 4 template khác nhau. Chỉ áp toàn site khi nhãn chung của `psi_decide.py` là "tốt hơn". Nhãn chung là "xấu hơn" khi một URL mẫu xấu hơn, và là "chưa đủ lượt" khi một URL mẫu chưa đủ lượt.

## 4. perf_probe.mjs (mô phỏng Chrome)

```bash
node "$WPS/scripts/perf_probe.mjs" --url https://example.com/ --dev mobile --runs 3 --expect '<chuỗi trong title>' [--detail]
# Staging có Basic Auth: đặt CDP_AUTH="user:pass" từ file env, không gõ vào lệnh.
CDP_AUTH="$STG_AUTH" node "$WPS/scripts/perf_probe.mjs" --url https://stg.example.com/ --resolve stg.example.com=<ip> --cookie <cookie chọn theme>=<theme> --expect '<chuỗi trong title>'
```

- Guard chống đo nhầm đích. Sau lượt đầu, script in dòng `GUARD host=<host thật> status=<HTTP> title=<title>`. Script thoát mã 4 và bỏ số đo khi:
  - HTTP từ 400, hoặc không nhận được status.
  - Host thật khác host của URL (bị redirect, ví dụ staging chuyển sang production).
  - Title không chứa chuỗi `--expect`.
  - LCP dưới 100 ms: dấu hiệu đo nhầm trang lỗi. Desktop trên máy nhanh có thể hợp lệ dưới 100 ms, khi đó đặt `--min-lcp 0`.
  - Có `--resolve` mà cổng của IP không mở: tunnel staging đã tắt.
- Luôn truyền `--expect`. Đợt 10/2026 có 2 lần đo nhầm đích, cho số đo vô nghĩa. `--no-guard` chỉ dùng khi cố ý đo trang lỗi.
- Chạy nền: `--done <file>` ghi `PROBE_DONE exit=<mã>` khi xong. Đọc file đó bằng một lệnh ngắn, không đọc log liên tục.
- Mobile: 412×823, DPR 1,75, 1,6 Mbps, trễ 150 ms, CPU x4. Desktop: 1350×940, không giới hạn mạng.
- Mỗi lượt mở Chrome mới với profile mới và tắt cache. DNS, TLS và tài nguyên tải lại từ đầu.
- Header Basic Auth chỉ gắn cho request tới đúng host của URL. Bên thứ ba không nhận header này.
- Kết quả là số mô phỏng chia đều băng thông. Số này không phải điểm PSI. Chỉ so các số đo cùng script.
- `--detail` in 15 request nặng nhất kèm loại, độ ưu tiên và mốc thời gian. Dùng khi cần biết tài nguyên nào chiếm đường găng.
- Theme của staging: `--cookie <tên cookie>=<theme>` nếu site dùng cookie chọn theme (ghi tên cookie trong `wp-server.md`). Cột `theme` ở kết quả xác nhận theme thật sự phục vụ (theme cha và con nối bằng `+`).
- Đặt nhãn `--label <mốc>-<template>`, ví dụ `prod-home`, `stg-home`. Ghi mỗi mốc vào một file JSONL rồi so:

  ```bash
  python3 -I "$WPS/scripts/probe_table.py" probe_production.jsonl probe_staging.jsonl --urls urls.tsv --detail
  ```

- `--detail` của `probe_table.py` in phần tử LCP và nguồn layout shift (trường `el`, `shifts`) cho template có CLS từ 0,1 hoặc LCP chậm hơn mốc đầu từ 0,3 s. Lượt thử 10/2026: lệnh này tìm ra CLS 0,23 do một ảnh `figure` ở trang giới thiệu trên staging mà không cần mở trình duyệt.
- Staging thường chưa bật page cache: TTFB 150–220 ms so với 25–60 ms ở production. Chênh LCP desktop dưới 0,3 s giữa 2 bản thường do TTFB, không do theme.

## 5. shot.mjs và shot_cmp.py

```bash
node "$WPS/scripts/shot.mjs" --urls urls.tsv --out shot-base --label base --expect '<chuỗi trong title>' \
  [--vis '{"menu":"#site-navigation","cta":".float-contact"}'] [--blockcss]
python3 "$WPS/scripts/shot_cmp.py" shot-base base shot-b1 b1
```

- `shot.mjs` có cùng guard với `perf_probe.mjs`: mỗi URL và thiết bị in một dòng `GUARD`. URL đầu lỗi thì thoát mã 4 ngay, chưa ghi kết quả. URL sau lỗi thì chụp tiếp, ghi trường `guard` vào `results_<label>.json`, rồi thoát mã 4.
- Đặt tên mốc chụp theo cặp trước và sau của cùng một đợt: `shot-base`, `shot-<đợt>`, nhãn `--label` trùng tên thư mục.

- `shot.mjs` chụp desktop 1366 px và mobile 390 px: ảnh màn hình đầu, ảnh cả trang. Script giả lập tương tác và cuộn hết trang để JS bị trễ chạy.
- Script ghi: mã HTTP, tràn ngang, form hiển thị, ảnh hỏng, icon font thiếu, slider đã khởi tạo, phiên bản jQuery, font đã nạp, lỗi JS, byte và số ảnh WebP.
- `--vis` thêm kiểm hiển thị theo selector riêng của site, ví dụ mega menu hoặc nút liên hệ nổi.
- `--blockcss` chặn file CSS không chặn hiển thị. Chế độ này chỉ chụp màn hình đầu để xem critical CSS có đủ không.
- `shot_cmp.py` đánh dấu `!!` khi chức năng đổi hoặc có lỗi JS mới. Cột `full` và `atf` ghi phần trăm điểm ảnh lệch. Claude xem ảnh khi `atf` lệch trên 1%.
- Không gửi form nào khi kiểm.

## 6. fontmap.mjs

```bash
node "$WPS/scripts/fontmap.mjs" --out fontmap https://example.com/ https://example.com/bai-viet/
node "$WPS/scripts/fontmap.mjs" --out fontmap-src --src https://example.com/
```

- Mặc định đo trang như khách nhận, sau khi LiteSpeed tối ưu. Đây là số dùng để kết luận.
- `--src` thêm `LSCWP_CTRL=before_optm` để thấy file CSS gốc khai báo font. Ở chế độ này, `@import` trong CSS gốc có thể không chạy, nên font vẽ có thể khác chế độ thường. Chỉ dùng `--src` để tìm file cần sửa.
- Script lấy font Chrome thật sự vẽ bằng `CSS.getPlatformFontsForNode`. Khai báo `!important` thắng khai báo thường khi script dò file nguồn.
- Viền màu: mỗi web font một màu, font hệ thống màu đỏ. Font hệ thống ở chữ chính nghĩa là web font chưa nạp hoặc thiếu ký tự.
- Montserrat biến thiên của Google Fonts hiện tên "Montserrat Thin". Đó vẫn là Montserrat.

## 7. Đặt tên và lưu evidence

- Một thư mục evidence cho mỗi đợt: `evidence-pagespeed-<YYYY-MM-DD>/`.
- Thư mục con theo mốc: `psi-base`, `psi-<đợt>`, `psi-final`, `psi-final-5hm`, `shot-base`, `shot-<đợt>`, `probe-<đợt>.jsonl`.
- Ghi `BASELINE.md` ở gốc thư mục evidence ngay sau Bước 2. Mỗi mốc một dòng: tên mốc, ngày giờ, công cụ, lệnh, thư mục kết quả, trung vị mobile và desktop. Lane sau đọc file này thay vì tìm lại số đo cũ.
- Ghi lệnh đã chạy và giờ chạy vào báo cáo. Không lưu key, cookie đăng nhập hay mật khẩu Basic Auth.
- Mỗi cột trong bảng báo cáo lấy số từ một công cụ. Số đo bằng Chrome trên máy (`perf_probe.mjs`, đo font) ghi ở dòng ghi chú riêng. Không nối số Chrome trên máy với số PSI bằng mũi tên.
- Trước khi giao báo cáo, grep thư mục evidence tìm key: `grep -rlF "$PAGESPEED_API_KEY" <ev>`. Chuỗi dạng `AIza…` trong JSON PSI thường nằm trong dữ liệu base64 của ảnh chụp, không phải key.
