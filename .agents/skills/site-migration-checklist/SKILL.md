---
name: site-migration-checklist
description: "Checklist + workflow audit site migration (đổi domain, đổi cấu trúc URL, redesign, gộp site, đổi CMS) qua 3 giai đoạn PRE / DURING / POST — layer sự kiện migration, neo lý thuyết Ranking Signal Consolidation và Historical Data (bảo toàn signal, không reset). Use when: (1) 'chuẩn bị migration cho [domain]', 'lập redirect map cho [site]', 'audit staging trước launch'; (2) 'site vừa migrate xong, traffic drop — triage giúp'; (3) 'định nghĩa rollback criteria trước khi đổi CMS'. Benchmark ưu tiên Ahrefs MCP, fallback user export/paste. KHÔNG dùng cho: audit technical định kỳ (→ technical-seo-audit — chỉ gọi làm bước con), content refresh (→ content-refresh), traffic drop không gắn migration event."
metadata:
  version: "1.0"
---

# Site Migration Checklist

Checklist + workflow audit cho **sự kiện site migration**: đổi domain, đổi cấu trúc URL, redesign, gộp site, đổi CMS — chia 3 giai đoạn PRE → DURING → POST. Nguyên lý gốc: migration đúng là migration **BẢO TOÀN** Ranking Signal + Historical Data, không phải cơ hội "làm mới" — Historical Data không reset được, chỉ overwrite ([[Historical Data]]).

Upstream: benchmark data từ Ahrefs/GSC (Path detection bên dưới). Downstream: có thể gọi `technical-seo-audit` làm bước con (staging audit, post-launch crawl health); dùng output `backlink-research` để priority redirect map.

## Phân vai (boundary với skill anh em)

| Việc | Skill |
|---|---|
| Audit quanh **sự kiện migration** (PRE/DURING/POST, redirect map, triage drop) | **site-migration-checklist** (skill này) |
| Audit technical **định kỳ** (crawl health, CWV, index hygiene thường xuyên) | → `technical-seo-audit` (skill này có thể gọi làm bước con ở 1.5 và 3.1) |
| Rewrite / update content theo chu kỳ | → `content-refresh` (guardrail: KHÔNG rewrite content trong đợt migration) |
| Phân tích + kế hoạch backlink | → `backlink-research` / `backlink-plan` (skill này chỉ DÙNG backlink data để priority map) |
| Audit onpage per-page OP1-OP55 | → `seo-onpage` |

## Input

**Required:**
- `$MIGRATION_TYPE` — một trong: `domain` / `https` / `url-structure` / `redesign` / `merge` / `cms` (`https` = HTTP→HTTPS). 🔴 Chỉ chọn MỘT — xem Bước 0 mục 2, Rule "one change at a time".
- `$SITE_OLD` — domain/URL structure hiện tại.
- `$SITE_NEW` — domain/URL structure đích (hoặc staging URL nếu đang ở PRE).
- `$PHASE` — `pre` / `during` / `post` (skill render đúng phần checklist theo giai đoạn).

**Optional:**
- `$LAUNCH_DATE` — ngày launch (bắt buộc nếu `$PHASE = post`, để tính khung thời gian triage).
- `$CRAWL_EXPORT_OLD` / `$CRAWL_EXPORT_NEW` — export crawl Screaming Frog (Internal tab CSV).
- `$GSC_EXPORT` — export GSC Performance (pages).

**Path detection — benchmark data (traffic/backlinks theo page):**
- **Path A (ưu tiên):** Ahrefs MCP — `site-explorer-top-pages`, `site-explorer-pages-by-backlinks`, `site-explorer-organic-keywords` cho `$SITE_OLD`.
- **Path B:** user export CSV — GSC Performance (pages, 3-12 tháng) + Ahrefs Best by links.
- **Path C (đường lùi cuối — luôn chạy được không cần MCP):** user paste danh sách top 50-100 URL kèm traffic/backlink ước lượng. ⚠️ Note trong output: benchmark độ tin thấp hơn, triage POST sẽ thiếu baseline chi tiết.

## Workflow

### Bước 0 — Scope, gate & rollback criteria

1. **Classify migration type** — mỗi type bật/tắt items khác nhau (bảng đầy đủ ở [references/migration-checklist-full.md](references/migration-checklist-full.md#0-scoping)). Điểm quyết định nhanh:

| Type | Change of Address (GSC) | Redirect map 1-1 | Rủi ro chính |
|---|---|---|---|
| Domain move | 🔴 Bắt buộc (mọi variant www/non-www, subdomain) | Có | Cao nhất — HD + backlink signal |
| HTTP→HTTPS | Không cần (Google xác nhận) | Có (rule đơn giản) | Thấp |
| URL structure | Không | Có (map từng URL) | Trung-cao |
| Redesign giữ URL | Không | Không (URL giữ nguyên) | Content/speed parity |
| Merge sites | Per-domain | Có (per-site) | Cao — nhiều HD nguồn |
| CMS change | Không (trừ khi kèm domain) | Thường có (URL hay đổi theo CMS) | Trung-cao |

2. 🔴 **Rule "one change at a time"** (Google site-move doc): KHÔNG gộp đổi domain + CMS + redesign trong 1 đợt. Nếu user muốn gộp → khai báo rõ đây là **rủi ro cộng dồn**, mỗi thay đổi thêm ngoài scope tối thiểu phải được liệt kê riêng trong report, đề xuất tách đợt. Site lớn: đề xuất move theo section, chọn section ít biến động làm test trước.

3. 🔴 **Rollback criteria định nghĩa TRƯỚC launch, không phải sau khi cháy.** Đây là khung quyết định (decision tree ở references, mục 3.5) — ⚠️ convention GTV tự định, không có ngưỡng chuẩn ngành. Ghi rõ trong report: rollback cũng có cost (Google thấy double migration).

4. **Gate MCP:** nếu đi Path A → báo user số call Ahrefs dự kiến (~4-8 call cho benchmark), chờ xác nhận rồi mới gọi.

5. **Khai báo timeline kỳ vọng** với stakeholder ngay từ đầu — 🔴 mọi con số recovery là **ước lượng có nguồn dạng range**, không hứa cứng (xem Behavior Gate #2). Điều duy nhất nói chắc được: Google xác nhận "temporary fluctuation là bình thường; site trung bình mất vài tuần để phần lớn pages chuyển index, site lớn lâu hơn" (Google site-move doc).

### Bước 1 — PRE (benchmark + mapping + staging audit)

Checklist đầy đủ có [owner] + [blocker]: [references/migration-checklist-full.md](references/migration-checklist-full.md#1-pre). Tóm tắt trình tự:

1. **Benchmark** (Path A/B/C): rankings, traffic theo page, backlinks theo page, indexed count (GSC + sitemap), CWV baseline. Snapshot có ngày — đây là baseline cho crawl parity ở POST.
2. **Full crawl site cũ** — Screaming Frog: bật integration XML sitemap + GA + GSC để bắt **orphan pages**; lưu database storage mode để Compare sau launch (SF migration tutorial).
3. **Dọn index pollution TRƯỚC khi map** — pages zero-CTR / zero organic keywords nhiều tháng → 410 hoặc noindex, KHÔNG map 1-1, không redirect rác sang site mới ([[Index Pollution]], [[Ranking Signal Consolidation]] 4 methods).
4. **Redirect mapping 1-1** — method chọn theo scale (<500 manual / 500-10k Near Duplicates / >10k vector embeddings): [references/redirect-mapping-method.md](references/redirect-mapping-method.md). Priority: pages có organic traffic > backlinks > conversions trước (Aleyda checklist).
5. **Staging audit** — bypass robots.txt/auth/IP restriction; check noindex/nofollow staging thường mang; URL Mapping trong SF Compare mode (regex) map staging vs live → segment Added/New/Removed/Missing; verify tracking + speed parity. Có thể gọi `technical-seo-audit` cho phần crawl health.
6. **Server capacity check** — ⚠️ Google crawl NẶNG HƠN tạm thời trong lúc move (Google site-move doc).

### Bước 2 — DURING (launch day)

1. Deploy **301/308 server-side** — ❌ không 302/307; nếu phát hiện 302 → convert ([[Status Codes]], Koray case >1.500 redirects convert).
2. **Gỡ mọi staging block**: noindex, robots.txt disallow, HTTP auth — lỗi phổ biến nhất Google liệt kê.
3. Verify **self-referencing canonical** trên mọi URL mới; update hreflang annotations sang URL mới.
4. **Sitemap:** submit sitemap MỚI sau khi redirects active; **GIỮ sitemap cũ trong GSC** để theo dõi indexed count giảm dần về 0 (Google site-move doc). Ưu tiên `sitemap_index.xml` phân theo category ([[Robots.txt]]).
5. **Change of Address tool** trong GSC — chỉ khi domain move, submit cho mọi variant.
6. Verify tracking fires (custom search "does not contain" tag trên crawl).
7. Spot-check **top-100 URL cũ** bằng SF list mode → 301 đúng target, 1 hop.

### Bước 3 — POST (parity, coverage, triage)

⚠️ **Cửa sổ cứu redirect sót là VÀI TUẦN** trước khi signals mất (Gary Illyes, gsqi.com) → audit redirect toàn bộ phải chạy trong **tuần 1**, không để sau.

| Khung thời gian | Việc chính |
|---|---|
| **Tuần 1** | SF list mode toàn bộ URL cũ + "Always Follow Redirects" → All Redirects report (chain → flatten 1 hop, loop, final status 200 + indexable); crawl parity vs baseline (Compare mode); 404 log (target <50 hits/tháng, zero cho 410 — [[Status Codes]]); GSC crawl errors |
| **Tuần 2-6** | GSC Coverage; sitemap cũ indexed count → 0 rồi mới gỡ; impressions transfer old → new; "Indexed, though blocked by robots.txt" phải = 0 |
| **Tháng 2-6** | HD lens: hiệu ứng đầy đủ của migration chỉ đo được sau ~6 tháng (6-month lag rule — [[Historical Data]]); giữ redirects ≥ 1 năm (Google) |

**Triage traffic drop** — 🔴 trước mọi kết luận, check ngày Google core update (Ahrefs traffic-drop SOP) — phân biệt drop-do-migration vs drop-do-algorithm:

| Tín hiệu | Kết luận | Action |
|---|---|---|
| Dip 10-20%, ổn định, hồi trong 2-6 tuần, GSC sạch lỗi | Normal fluctuation (SEJ) | Monitor, không can thiệp |
| Drop >30%, crawl errors/404 mới trong GSC, indexed giảm | Migration hangover (SEJ) | Điều tra ngay 6 nguyên nhân (references mục 3.4), **fix highest-traffic pages first** |
| Drop >50% overnight | Sự cố hệ thống | Escalate + chạy rollback decision tree |
| >4 tuần không có dấu hiệu ổn định | Hangover kéo dài | Full re-audit + xét rollback criteria đã định ở Bước 0 |

### Bước 4 — Report

Render output theo skeleton dưới, lưu đúng naming convention, liệt kê action items ưu tiên theo impact (blocker trước).

## Output

File: `<project>_Migration-Audit_v1.md` (tăng `_v2`, `_v3`… nếu trùng) — trả về folder dự án theo TASK ROUTING.

```markdown
# Migration Audit — <SITE_OLD> → <SITE_NEW>

## Scope
- Migration type: <type> | Phase: <pre/during/post> | Launch date: <date hoặc TBD>
- Thay đổi ngoài scope tối thiểu (rủi ro cộng dồn): <liệt kê hoặc "không">
- Rollback criteria (định trước launch): <ngưỡng + điều kiện>

## Benchmark snapshot (<ngày>, nguồn: <Ahrefs MCP / GSC export / user paste>)
| Metric | Giá trị | Nguồn |
|---|---|---|
| Organic traffic /tháng | … | … |
| Top pages (traffic) | … | … |
| Pages có backlinks | … | … |
| Indexed count | … | … |

## Checklist status — <PHASE>
- [ ] <item> [owner] [blocker]
…

## Findings & risks
| # | Finding | Mức độ | Evidence (nguồn + ngày) | Action |
|---|---|---|---|---|

## Timeline kỳ vọng (ước lượng có nguồn — KHÔNG cam kết)
<range theo loại migration + citation + câu: "phụ thuộc loại migration,
chất lượng redirect map, và Historical Data hiện có">

## Next steps (ưu tiên theo impact)
1. …
```

## Behavior Gates

1. **🔴 Think Before** — Bước 0 luôn chạy trước: classify type, gate "one change at a time", rollback criteria định trước launch. Không nhảy thẳng vào checklist khi chưa rõ `$MIGRATION_TYPE` + `$PHASE`. Type mơ hồ (vd "đổi CMS có đổi domain không?") → hỏi, không giả định.
2. **🔴 Evidence** — mọi con số trong report truy được về nguồn + ngày. Timeline recovery LUÔN render dạng range + citation + câu điều kiện "phụ thuộc loại migration, chất lượng redirect map, và Historical Data hiện có". Số secondhand (vd "523 days average recovery, 17% never recover") nếu dùng phải label rõ **"chưa verify primary source"** — không bao giờ dùng làm cam kết.
3. **🔴 Surgical** — chỉ audit quanh sự kiện migration. Phát hiện vấn đề technical không liên quan migration → note 1 dòng, route sang `technical-seo-audit`, không tự mở rộng scope. Không đề xuất rewrite content trong đợt migration.
4. **🔴 Goal-driven** — mục tiêu duy nhất: BẢO TOÀN Ranking Signal + Historical Data qua migration ([[Ranking Signal Consolidation]], [[Historical Data]]). Mọi quyết định (map hay 410, redirect hay giữ URL) đánh giá qua lens này. Koray: nếu rebuild toàn site, ưu tiên "change content + name nhưng GIỮ URL" khi có thể.

## Anti-patterns

- ❌ **Bulk redirect URL cũ về homepage** hoặc trang không liên quan — Google coi như soft-404 (Google site-move doc).
- ❌ **Block URL cũ bằng robots.txt** — chặn luôn việc truyền signal, SE không thấy được redirect ([[Ranking Signal Consolidation]]).
- ❌ **Dựa vào canonical thay 301** — canonical chỉ là hint, dùng sai Googlebot bỏ qua + tốn crawl budget ([[Index Pollution]]).
- ❌ **Bán narrative "migration để reset/refresh historical data"** — HD không reset được, chỉ overwrite bằng signal mạnh hơn ([[Historical Data]] In Practice mục 2).
- ❌ **Hứa timeline hồi phục cứng** — chỉ được nói range có citation + điều kiện.
- ❌ **302/307 cho redirect permanent** — phải 301/308 server-side ([[Status Codes]]).
- ❌ **Rewrite content / đổi structure "tiện thể" trong đợt migration** — rủi ro cộng dồn, vi phạm "one change at a time"; nếu cần refresh → `content-refresh` sau khi migration ổn định.
- ❌ **Map 1-1 pages rác** (zero-CTR nhiều tháng) sang site mới — 410, không redirect ([[Index Pollution]]).
- ❌ **Gỡ redirects/sitemap cũ sớm** — redirects giữ ≥1 năm; sitemap cũ chỉ gỡ khi indexed count về 0.

## References & wiki

**References nội bộ skill:**
- [references/migration-checklist-full.md](references/migration-checklist-full.md) — checklist 3 giai đoạn chi tiết (owner/blocker), triage matrix, rollback decision tree, bảng recovery timeline có label.
- [references/redirect-mapping-method.md](references/redirect-mapping-method.md) — nguyên tắc map 1-1, priority tiers, method theo scale, QA, template sheet.

**Wiki Semantic SEO (neo lý thuyết):**
- [[Ranking Signal Consolidation]] — cơ chế 301/canonical transfer signal; 4 methods xử lý URL thừa.
- [[Historical Data]] — 6-month lag rule; HD không reset, chỉ overwrite; timing benchmark SOP v1.
- [[Status Codes]] — 301 vs 302/307; 410 cho gone; flatten chain 1 hop; log target.
- [[Robots.txt]] — sitemap_index theo category; "Indexed, though blocked" = 0.
- [[Index Pollution]] — canonical là hint; dọn pages zero-value trước migration.

**Nguồn ngoài (đã dùng trong facts):** Google Search Central site-move doc · Google Search Central redirects doc (developers.google.com/search/docs/crawling-indexing/301-redirects) · Aleyda Solis 3-phase methodology · Screaming Frog migration + vector embeddings tutorials · SEJ migration-hangover (searchenginejournal.com/what-is-a-migration-hangover-traffic-drop-how-do-you-avoid-it/575102/) · gsqi.com Gary Illyes (gsqi.com/marketing-blog/image-migrations-lost-signals/) · Ahrefs traffic-drop SOP (ahrefs.com/blog/analyze-sudden-traffic-drop/).

## Changelog

- **v1.0 (2026-07-07):** khởi tạo — nền: wiki Koray (Historical Data, Ranking Signal Consolidation, Status Codes, Robots.txt, Index Pollution) + Google site-move doc + Aleyda 3-phase + Screaming Frog migration/embeddings tutorials + SEJ migration-hangover + Gary Illyes signal-loss window.
