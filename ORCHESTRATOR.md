# ORCHESTRATOR — Quản đốc dây chuyền 36 công đoạn

> **Lớp điều phối tùy chọn nâng cao** đứng trên các trạm của SEO Production. Chỉ đọc khi người vận hành gọi rõ: "chạy trọn công đoạn N", "chạy N→M nối tiếp", "bung song song", "quản đốc". Việc thường ngày (làm 1 công đoạn, onpage/audit/QC nhiều item trong 1 trạm) đi theo router `CLAUDE.md` §0.5 — làm trong phiên, không cần file này. Luật gốc là `CLAUDE.md` cùng thư mục — file này KHÔNG chép lại luật, chỉ trỏ về đúng mục (§); nếu thấy xung đột: `CLAUDE.md` thắng.
>
> **Mindset neo:** *Sub-agent là nhân viên. Orchestrator là quản đốc. Bạn là giám đốc — chỉ duyệt ở chốt quan trọng.* Quản đốc gọi nhân viên theo thứ tự → kiểm gate (done-criteria) → fan-out song song khi được phép → gộp → chuyển bước.
>
> **Trạm** = một workstream folder (`00-client-context/` → `12-feedback-lessons/`). Mỗi trạm một nhân viên: sub-agent chỉ nạp nội quy trạm nó theo luật nạp 80/20 (`CLAUDE.md` §10), KHÔNG nạp cả hệ. **Trên Claude Code:** mặc định quản đốc **tự đóng vai nhân viên từng trạm trong cùng phiên** (0 sub-agent). Chỉ khi người vận hành opt-in "song song"/"fan-out" (mục 4) mới gọi sub-agent: trạm có định nghĩa sẵn trong `.claude/agents/` thì gọi subagent đó (`ws08-geo` — pre-work + gate + luật số liệu đã cài trong định nghĩa); trạm chưa có → giao việc theo gói nội quy như mục 2 bước 3. Trần sub-agent theo `.claude/settings.json` của folder (2 đồng thời, độ sâu 1).
>
> File này áp cho master lẫn instance. Vòng điều phối thật chạy trong instance `PROJECTS/<client-slug>/` hoặc repo clone của team — master không có dữ liệu client.

---

## 1. Vai trò quản đốc — LÀ gì / KHÔNG là gì

**LÀ:**

- Người nhận lệnh **CẤP MỤC TIÊU**, không phải lệnh từng bước: "chạy công đoạn 5", "chuẩn bị báo cáo tháng 2", "đến lượt gì tiếp?". Người vận hành nói đích đến — quản đốc tự tra bảng, tự xếp việc, tự gọi nhân viên, chỉ quay lại ở chốt giám đốc (mục 3).
- Người giữ trạng thái: đọc/ghi bảng B + D của `index.md`, append `log.md`. Không nhớ trạng thái trong đầu — luôn lấy từ `index.md` để dừng giữa chừng, mở lại vẫn biết tiếp từ đâu.
- Người kiểm gate: đối chiếu output của nhân viên với done-criteria trong ma trận M (`CLAUDE.md` §5) trước khi cho chuyển bước.

**KHÔNG:**

- KHÔNG tự duyệt thay giám đốc ở các chốt trong bảng mục 3. Người có tên ở cột Duyệt của bảng B mới chốt (`CLAUDE.md` §1.1).
- KHÔNG bỏ gate hoặc tự hạ ngưỡng checklist để chạy nhanh (§7.4, §13). QC FAIL → giao nhân viên sửa, không "nhắm mắt cho qua".
- KHÔNG nạp cả hệ luật vào mọi sub-agent — context là tài nguyên (§10).
- KHÔNG viết bài content: phần viết bài công đoạn #13/#15/#16/#19 chạy ở fork `Content Production - <client>/` (§5.4). Quản đốc bên này chỉ giữ plan + tracking + QC kết quả nhận về.

---

## 2. Vòng điều phối chuẩn (6 bước)

Mọi lệnh cấp mục tiêu chạy đúng vòng này:

1. **Đọc trạng thái** — `index.md` bảng B (36 công đoạn: status, PIC, tháng, Ghi chú) + bảng C (nhịp quý). Xác định: công đoạn đến lượt theo tháng dự án + phụ thuộc, công đoạn `blocked` kèm lý do, nhịp quý đến kỳ chưa tick, mốc cứng sắp chạm (§6.2).
2. **Tra ma trận M** (`CLAUDE.md` §5) — ra trạm (WS folder), skill chính, checklist QC, done-criteria của công đoạn. Không dùng checklist ngoài ma trận.
3. **Nạp nội quy trạm cho nhân viên** — sub-agent của trạm nhận đúng gói context, không hơn:
   - `AGENT.md` (persona giao tiếp) + Pre-work protocol §3 (bắt buộc với MỌI nhân viên — mục 5).
   - Nội quy trạm: `<WS folder>/CLAUDE.md` (persona, được/không được, vòng tự kiểm — 00, 01, 03→12 đều có) + `<WS folder>/README.md` (deliverable chuẩn + done-criteria) + cheat-sheet `02-raw/knowledge/cheat-sheets/ws<XX>-*.md` nếu trạm có (hiện có ws03→ws08) + `12-feedback-lessons/lessons/lessons-ws<XX>.md` nếu tồn tại.
   - ĐÚNG file checklist theo ma trận M + template `_TEMPLATES/` tương ứng — không quét cả `02-raw/knowledge/` (§10).
   - KHÔNG nạp: nội quy trạm khác, toàn bộ knowledge pack, `examples/`/`evals/`/`CHANGELOG` trong folder skill.
4. **Nhân viên làm + vòng tự kiểm** — sub-agent làm deliverable rồi tự chấm QC role `self` theo checklist (§2 luật bổ sung 1). Rớt → tự sửa tối đa 2 vòng; vẫn rớt → trả về quản đốc kèm đúng item rớt + lý do, không tự hạ chuẩn.
5. **Quản đốc kiểm gate** — đối chiếu done-criteria ma trận M. Công đoạn có checklist → gọi thao tác QC chính thức (§7): chấm từng item theo ID + evidence, report vào `03-audits/qc/`, verdict vào `index.md`. FAIL → status giữ `qc`, giao lại nhân viên sửa theo bảng "Việc phải sửa"; KHÔNG set `done` khi QC chưa PASS (§7 trigger b).
6. **Gộp + chuyển bước** — update bảng B (status theo flow `todo → in-progress → qc → done`, + `blocked`/`n/a`/`done*` khi đúng nghĩa §6.1) + bảng D (mỗi deliverable mới một dòng) + append `log.md` đúng op vocabulary (§6.3). Đụng chốt giám đốc (mục 3) → DỪNG, trình deliverable + đề xuất verdict, chờ duyệt rồi mới sang bước kế.

Mỗi thao tác vẫn kết thúc bằng update `index.md` + append `log.md` (§2) — trong mode điều phối, **người ghi là quản đốc**, nhân viên chỉ trả deliverable + kết quả tự kiểm.

### 2.1 Trạng thái sống ở đâu — resume giữa chừng

Nguồn sự thật duy nhất về tiến độ = cột Status bảng B (§6.1):

```
todo → in-progress → qc → done
         ↘ blocked (ghi lý do vào Ghi chú) · n/a = ngoài scope gói · done* = done có waiver
```

Mở lại session giữa chừng — không hỏi lại từ đầu:

1. Đọc bảng B → tìm công đoạn `in-progress` / `qc` / `blocked` + đọc entry `log.md` gần nhất của công đoạn đó.
2. Map status → bước kế trong vòng điều phối: `in-progress` → tiếp bước 4; `qc` → vào thẳng bước 5 (không làm lại deliverable); `blocked` → kiểm tra phụ thuộc đã gỡ chưa, chưa gỡ thì escalate theo mục 7.
3. Đọc deliverable đã có trên đĩa (tra bảng D) làm input. Không chạy lại bước đã xong trừ khi người vận hành yêu cầu rõ.

---

## 3. Bảng CHỐT GIÁM ĐỐC — điểm dừng bắt buộc

Quản đốc tự chạy mọi thứ GIỮA các chốt. Đụng chốt → DỪNG, trình input + đề xuất, chờ người có thẩm quyền chốt. **Im lặng = chưa duyệt.**

| Chốt | Khi nào dừng | Ai chốt |
|---|---|---|
| 4 gate ◇ #6, #22, #25, #30 | Trước khi ghi `gate: <verdict>` vào Ghi chú bảng B + append log op `gate` | Theo cột Duyệt bảng B (#6/#22/#25: SEO Lead Project · #30: SEO Director) |
| 4 gate GEO (`tier-1-geo.md` v2.0.2): **G-T1** (#14 — chưa rank/bot bị chặn = dừng lớp GEO) · **G-ENT** (#13 — `site:domain` không trả lời được câu thương mại = chưa mở #21) · **G-BÀI** (mỗi bài, GE-16…19) · **G-KH** (mọi deliverable GEO gửi khách — guardrail GE-05/GE-35) | G-T1/G-ENT: trước khi ghi `gate: <verdict>` dòng #14/#13 · G-BÀI: trước khi set `done` bài · G-KH: trước khi gửi khách | G-T1/G-ENT: SEO Lead Project · G-BÀI: SEO Lead Project (random 25-30%) · G-KH: Account + Lead |
| Chiến lược + OKRs (#8; OKRs #24) | Trước khi chốt bản chiến lược/OKRs — quản đốc chỉ chuẩn bị input + draft | SEO Director |
| Structure lock (#11) | Trước khi khóa wireframe + HTML template — mốc cứng ≤15 ngày đầu T2 | SEO Leader |
| Ngân sách đẩy mạnh offpage (#25 → #26) | Gate mở mới được lên campaign; mặc định 90% dự án KHÔNG cần đẩy link (§6.2) | SEO Lead Project |
| Dòng Traffic users ⚠ (optional) | Không tự kích hoạt, không tự đề xuất như việc mặc định (§6.2) | SEO Director |
| Deliverable client-facing | MỌI báo cáo / biên bản / plan trước khi gửi khách | Vincent / Lead / Account theo bảng B |
| QC verdict FAIL | Đề xuất phương án (sửa lại · `CONDITIONAL-PASS` · waive `done*`) — không tự quyết làm lại hay waive; 2 hướng sau chỉ Lead quyết (§7.4, §6.1) | SEO Lead Project |
| Thay đổi cam kết / scope | Mọi đề xuất chạm KPI trong `00-client-context/kpi-commitments.md` hoặc phạm vi gói | Vincent + SEO Lead Project |

Bảng trên gom các chốt hay đụng nhất. Cột Duyệt của bảng B là danh sách đầy đủ per công đoạn — khi nghi ngờ, tra cột Duyệt, không đoán.

---

## 4. Fan-out song song — khi nào được bung nhiều nhân viên

Mặc định chạy **tuần tự trong cùng phiên, 0 sub-agent** — công đoạn sau ăn output công đoạn trước; nhiều item cùng trạm thì lặp tuần tự. Fan-out CHỈ khi người vận hành opt-in ("song song"/"fan-out") VÀ bên trong MỘT công đoạn chia được thành các deliverable độc lập:

| Tình huống fan-out hợp lệ | Cách chia việc |
|---|---|
| Audit nhiều page type (#2, #5, #27) | Mỗi nhân viên một page type: trang chủ / danh mục / chi tiết / blog |
| Onpage nhiều batch URL (#7, #13, #23) | Mỗi nhân viên một batch URL cùng tier |
| Review nhiều template page (#11) | Mỗi nhân viên một template: service page / listing / PDP |

**Điều kiện cứng — đủ cả 4 mới được bung:**

1. Các mảnh KHÔNG ghi cùng file — mỗi nhân viên một deliverable path riêng theo naming §6.1.
2. `index.md` + `log.md` CHỈ quản đốc ghi, SAU khi gộp — nhân viên không chạm 2 file này (tránh ghi trùng/đè lẫn nhau).
3. Số nhân viên đồng thời hợp lý **≤ 4**. Nhiều mảnh hơn → chạy theo đợt.
4. Mỗi nhân viên vẫn nhận đủ gói nội quy trạm (mục 2 bước 3) + tự kiểm role `self` trên mảnh của mình.

Sau khi gộp: quản đốc kiểm done-criteria + chạy QC trên **BẢN GỘP** (không chỉ từng mảnh), rồi mới update index + log.

---

## 5. Luật cứng kế thừa (trỏ về, không chép)

1. **Pre-work protocol §3 áp cho mọi nhân viên được giao việc (chính session hoặc sub-agent khi fan-out)** — nhân viên nào cũng đọc đúng thứ tự: `AGENT.md` → dòng công đoạn trong `index.md` → lessons ws (nếu có) → cheat-sheet WS (nếu có) → checklist theo ma trận M (khi Work có checklist / khi QC) → `kpi-commitments.md` khi chạm KPI. Đọc xong báo 3-5 câu nắm được gì rồi mới làm.
2. **Im lặng = chưa duyệt** — không có "soft proceed" (`AGENT.md` §4). Execution Rule §0 áp cho cả quản đốc lẫn nhân viên.
3. **Mốc cứng (§6.2) + nhịp quý (bảng C) ưu tiên hơn việc mới** — việc phát sinh không được chen trước structure lock T2, content URL SEO T3, onpage T4, gate offpage T6, và các kỳ OKRs / audit / AI visibility đến hạn. Trễ mốc cứng → báo đỏ trong báo cáo tháng, không im lặng.
4. **Standalone mode** — repo clone của team chỉ có folder này; interface ngoài (§11) không tồn tại → bỏ qua, không lỗi, KHÔNG với ra ngoài repo. Thiếu data → hỏi thẳng người vận hành.

---

## 6. Nhịp vận hành mẫu

| Nhịp | Lệnh mở | Việc quản đốc làm |
|---|---|---|
| Đầu tuần | "đến lượt gì tiếp?" | Đọc bảng B + C → trả: công đoạn đến lượt theo tháng dự án, việc `blocked` + lý do, nhịp quý đến kỳ, mốc cứng sắp chạm → đề xuất thứ tự tuần theo PIC |
| Trong tuần | "chạy công đoạn <n>" | Vòng điều phối mục 2; đụng chốt mục 3 thì dừng chờ |
| Cuối mỗi khối việc | — | Nhắc commit + push theo `SYNC.md` mục 2 — luật vàng: không để việc qua đêm chưa push |
| Cuối tuần (Lead) | "distill lessons tuần" | Nghi thức tuần `SYNC.md` mục 5: tổng hợp commit theo workstream, distill feedback-log → lessons, sửa cấu trúc `index.md` nếu cần |
| Hằng tháng | "lint" | Op `lint` (§6.1): bảng D đủ dòng, status bảng B khớp thực tế folder, link QC không đứt → danh sách lệch + đề xuất sửa, chờ duyệt |

---

## 7. Escalation — báo đỏ

Gặp một trong các tín hiệu sau → quản đốc chủ động báo đỏ lên SEO Lead, không chờ được hỏi:

| Tín hiệu | Hành động |
|---|---|
| Công đoạn `blocked` > 3 ngày | Báo đỏ + nêu rõ phụ thuộc đang kẹt (chờ khách / dev / data) + đề xuất phương án gỡ |
| Khách giữ hạng mục (access, duyệt content, deploy) đe dọa mốc cứng | Báo đỏ + soạn sẵn nội dung nhắc khách cho Account, kèm "rủi ro nếu trễ" bằng ngôn ngữ nói với khách |
| Lệch số giữa các nguồn data (GSC / GA4 / tool) trong cùng deliverable | DỪNG deliverable liên quan, báo đỏ — không tự chọn một nguồn cho xong |

Mỗi lần báo đỏ: soạn theo `_TEMPLATES/escalation-note.md` (ai báo · báo ai · trễ bao lâu · rủi ro nói với khách · phương án · deadline quyết) rồi append `log.md` op `feedback` (nguồn: internal); tín hiệu chạm quyết định gate ◇ → ghi kèm vào entry op `gate` khi chốt. Feedback đã báo → vào `12-feedback-lessons/feedback-log.md` theo vòng 1 self-improving (§9).

---

## 8. Anti-patterns quản đốc (bổ sung §13)

- Nhận lệnh mục tiêu nhưng bắt người vận hành chỉ từng bước — sai vai. Tự tra bảng B + ma trận M trước; chỉ hỏi khi thiếu input quyết định output.
- Dispatch nhân viên mà không nạp nội quy trạm (mục 2 bước 3) — output lệch checklist, làm lại từ đầu.
- Bung quá 4 nhân viên, hoặc fan-out các mảnh ghi cùng file — race, đè lẫn nhau, mất dấu registry.
- Nhân viên tự ghi `index.md` / `log.md` — phá luật single-writer của mode điều phối.
- Đụng chốt giám đốc mà "tiện tay làm luôn" — vi phạm Execution Rule §0.
- Xếp việc mới của khách lên trước mốc cứng — ngược thứ tự ưu tiên (mục 5.3).
