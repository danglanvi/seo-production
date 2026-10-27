// Mẫu script Workflow nhiều lane sửa site sống (v1.1).
// Nguồn: 7 script phiên f00d80af (22–24/10/2026) và đợt rà transcript 16–24/10 (phiên bf61eacd, mục hs-1 đến hs-12).
// Cách dùng: chép file, thay phần <…>, giữ đúng một mẫu ở cuối file (A, B, C hoặc D), xoá các mẫu còn lại.
// Trước khi chạy: python3 tools/wf-status.py lint-script <file> --args <args.json> --base <thư mục workstream>. Còn ERROR thì sửa, không chạy.
// Chạy với args: { base: '<thư mục workstream>', now: '<giờ từ lệnh date>' }.

export const meta = {
  name: '<site>-<đợt>',
  description: '<một dòng: việc gì, mấy lane, mẫu nào>',
  phases: [
    { title: 'Làm', detail: '<tên các lane>' },
    { title: 'Kiểm', detail: 'kiểm độc lập: Sonnet cho lane thường, Opus cho lane lõi' },
    { title: 'Sửa', detail: '1 vòng sửa cho lane có lỗi production' },
  ],
}

const B = args.base
// Trần mỗi workflow: 6 agent, tính cả agent kiểm và sửa, chạy khoảng 90 phút. Việc nhiều hơn thì tách workflow theo đồ thị phụ thuộc.
// Script không đo được giờ (không có Date.now). Trần 90 phút thực thi bằng budget_min: tổng budget_min trên chuỗi dài nhất, cộng lượt kiểm, không quá 90.
const MAX_AGENTS = 6
// Số agent chạy cùng lúc: min(CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS (repo này đặt 2, tính theo từng phiên), slot còn trống của phiên này theo "wf-status.py slots <thư mục session>").
const SLOTS = 2

const COMMON = `Workspace: "${B}" (<tên workstream, entity>). Bắt đầu khoảng ${args.now} (+07).

NGUỒN PHÊ DUYỆT: <trích nguyên văn tin Lead kèm giờ, hoặc đường dẫn file quyết định + mục>. Đây là task của lane, không phải câu hỏi chờ trả lời. Được phép ghi file báo cáo .md trong thư mục lane. Làm tới khi xong hoặc gặp blocker thật, không hỏi lại.

Đọc trước khi làm: BRIEF.md và CHECKPOINT.md trong thư mục lane. Chỉ đọc HANDOFF, luật tổng hợp hoặc Archive khi gặp tình huống BRIEF không có.

<khối luật: references/luat-lane.md §1 + mục nền tảng §3 + bảng sở hữu §4. Lane không có BRIEF.md thì chép thêm khối "Bẫy shell" của §1.>`

const RESULT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'partial', 'held', 'blocked', 'rolled_back'] },
    held_until: { type: 'string', description: 'status held: điều kiện mở, ví dụ "staging.lockdir nhả" hoặc "lane l8-css đạt kiểm"' },
    changes: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, what: { type: 'string' }, where: { type: 'string' }, production: { type: 'boolean' }, evidence: { type: 'string' },
    }, required: ['what', 'where', 'production', 'evidence'] } },
    numbers: { type: 'string', description: 'số trước/sau' },
    not_done: { type: 'array', items: { type: 'object', properties: { what: { type: 'string' }, why: { type: 'string' } }, required: ['what', 'why'] } },
    for_lead: { type: 'array', items: { type: 'string' } },
    mark_applied: { type: 'array', items: { type: 'string' } },
    folder: { type: 'string' },
    rollback: { type: 'string' },
  },
  required: ['status', 'changes', 'not_done', 'for_lead', 'folder', 'rollback'],
}
// loi_production chặn: mở vòng sửa và kiểm lại. loi_bao_cao không chặn: vòng sửa (nếu có) sửa kèm, hoặc phiên chính sửa bằng Edit.
const CHECK = {
  type: 'object',
  properties: {
    pass: { type: 'boolean', description: 'true khi loi_production rỗng và mọi tiêu chí đạt' },
    loi_production: { type: 'array', items: { type: 'object', properties: {
      desc: { type: 'string' }, evidence: { type: 'string' }, url: { type: 'string' },
    }, required: ['desc', 'evidence'] } },
    loi_bao_cao: { type: 'array', items: { type: 'object', properties: {
      desc: { type: 'string' }, file: { type: 'string' },
    }, required: ['desc'] } },
    verified: { type: 'array', items: { type: 'string' } },
    sampled: { type: 'array', items: { type: 'string' }, description: 'URL hoặc mục kiểm theo mẫu' },
    rolled_back: { type: 'boolean' },
  },
  required: ['pass', 'loi_production', 'loi_bao_cao', 'verified'],
}

// Model theo references/chon-model.md. Lane chỉ đọc: Sonnet high. core: true cho lane chạm theme, template, mu-plugin hoặc config sống.
const LANES = [
  { key: '<lane-1>', model: '<sonnet|opus>', effort: '<high|xhigh>', folder: `${B}/<đợt>/<lane-1>`, readOnly: false, core: false, budget_min: 45,
    task: `<1. việc cụ thể, lệnh hoặc giá trị, file nguồn>
<2. …>`,
    accept: `<tiêu chí đo được: cổng tất định đã chạy (verify.py, sweep, Jev), giá trị trên site, backup theo phiên bản, lệnh trả lại thử DRY đạt, 0 5xx mới, robots/canonical không đổi>` },
  { key: '<lane-doc>', model: 'sonnet', effort: 'high', folder: `${B}/<đợt>/<lane-doc>`, readOnly: true, core: false, budget_min: 30,
    task: `<việc chỉ đọc hoặc chỉ đo>`,
    accept: `<số đo cần có, file kết quả>` },
]

// goi(): mọi agent đi qua hàm này. Agent trả null (hạn mức, lỗi API, bị bỏ qua) thì dừng khởi agent mới.
let STOP = ''
let launched = 0
async function goi(prompt, opts) {
  if (STOP) { log(`Bỏ ${opts.label}: ${STOP}`); return null }
  if (launched >= MAX_AGENTS) { log(`Bỏ ${opts.label}: workflow đã đủ ${MAX_AGENTS} agent, chuyển sang workflow sau`); return null }
  launched++
  const r = await agent(prompt, opts)
  if (r === null) STOP = `agent ${opts.label} trả null (hạn mức hoặc lỗi API), không khởi agent mới`
  return r
}

// pool(): chạy fn trên từng item, tối đa n cùng lúc. Dùng thay parallel() trên cả danh sách.
async function pool(items, n, fn) {
  const out = new Array(items.length)
  let next = 0
  const worker = async () => {
    while (next < items.length) { const i = next++; out[i] = await Promise.resolve().then(() => fn(items[i], i)).catch(() => null) }
  }
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, worker))
  return out
}

const checkOpts = L => (L.core ? { model: 'opus', effort: 'high' } : { model: 'sonnet', effort: 'high' })

function workPrompt(L, extra) {
  return `${COMMON}\n\nLane: ${L.key}. Thư mục lane: ${L.folder}/ (tạo nếu chưa có). BRIEF: ${L.folder}/BRIEF.md.\n\nViệc:\n${L.task}\n${extra || ''}\n\nNgân sách: ${L.budget_min} phút. Hết ngân sách thì ghi CHECKPOINT.md, trả status partial. Cần chờ khoá hay điều kiện ngoài lane thì trả status held kèm held_until, không ngủ chờ.\nTiêu chí đạt (agent kiểm độc lập sẽ dùng): ${L.accept}\n\nGhi kết quả theo schema vào ${L.folder}/ket-qua.json, rồi trả đúng kết quả đó.`
}
function checkPrompt(L, n) {
  const lan2 = n > 1 ? `\nLượt ${n}: chỉ kiểm lại mục loi_production của lượt trước và phần lượt trước chưa kiểm xong. Dùng lại dữ liệu quét trong ${L.folder}/kiem/, không quét lại phần đã đạt.` : ''
  return `${COMMON}\n\nVai: kiểm độc lập lane ${L.key}, lượt ${n}. Không tin báo cáo của lane: tự đo trên site (chỉ đọc), đọc file trong ${L.folder}/. Kết quả lane tự báo: ${L.folder}/ket-qua.json.\nViệc của lane:\n${L.task}\n\nTiêu chí đạt: ${L.accept}\nCổng tất định chạy trước: verify.py, kết quả sweep, Jev approved-applied (cái nào lane có). Sau đó soát mọi mục cổng gắn cờ, cộng mẫu 10–15% URL hoặc mục còn lại. Kiểm thêm: backup tồn tại và md5 khớp, lệnh trả lại trong rollback.md chạy đúng ở chế độ DRY (không chạy thật trên production), không có 5xx mới, robots và canonical bản Googlebot smartphone không đổi ở URL bị chạm, file trong thư mục lane không chứa host staging, mật khẩu, slug đăng nhập hay key.${lan2}\n\nPhân loại lỗi: loi_production là lỗi trên site hoặc thiếu backup/lệnh trả lại; loi_bao_cao là lỗi trong file báo cáo, số ghi sai, thiếu mục tài liệu. Ghi kiem-doc-lap.md (mục "Lượt ${n}"). Cuối mục ghi đúng một dòng "Kết luận: đạt" hoặc "Kết luận: không đạt"; mark_batch.py của wp-content-review-apply đọc dòng này. Chỉ đọc. Ngoại lệ: thay đổi của lane đang làm hỏng site (5xx, noindex, đăng nhập hỏng, bố cục vỡ nặng) thì trả lại theo rollback.md, ghi rõ, đặt rolled_back=true.`
}
function fixPrompt(L) {
  return `${COMMON}\n\nLane: ${L.key}. Thư mục lane: ${L.folder}/. Đây là vòng sửa duy nhất sau kiểm độc lập không đạt.\nViệc gốc:\n${L.task}\n\nTiêu chí đạt: ${L.accept}\n\nĐọc kết quả lượt trước ở ${L.folder}/ket-qua.json và lỗi ở ${L.folder}/kiem-doc-lap.md mục "Lượt 1". Sửa mọi loi_production, rồi loi_bao_cao. Backup bản hiện tại thành phiên bản mới trước khi sửa. Cập nhật bao-cao.md, CHECKPOINT.md, rollback.md, mark_applied.json, ket-qua.json. Trả kết quả đầy đủ theo schema.`
}

async function runLane(L, extra) {
  const work = await goi(workPrompt(L, extra), { label: `lam:${L.key}`, phase: 'Làm', model: L.model, effort: L.effort, schema: RESULT })
  if (!work || work.status === 'held') return { lane: L.key, work }
  const check = await goi(checkPrompt(L, 1), { label: `kiem:${L.key}`, phase: 'Kiểm', ...checkOpts(L), schema: CHECK })
  // Lane chỉ đọc: một lượt kiểm, không vòng sửa. Mục thiếu chuyển cho lane sau đo bổ sung.
  // loi_bao_cao không mở vòng sửa: phiên chính sửa bằng Edit khi đóng đợt.
  if (L.readOnly || !check || check.loi_production.length === 0) return { lane: L.key, work, check }
  log(`${L.key}: ${check.loi_production.length} lỗi production, chạy 1 vòng sửa`)
  const fix = await goi(fixPrompt(L), { label: `sua:${L.key}`, phase: 'Sửa', model: L.model, effort: L.effort, schema: RESULT })
  const check2 = fix ? await goi(checkPrompt(L, 2), { label: `kiem2:${L.key}`, phase: 'Kiểm', ...checkOpts(L), schema: CHECK }) : null
  return { lane: L.key, work, check, fix, check2 }
}
const lastCheck = r => r && (r.check2 || r.check)
const passed = r => !!lastCheck(r) && lastCheck(r).loi_production.length === 0
const final = r => r && (r.fix || r.work)
const rolledBack = r => !!r && (!!(lastCheck(r) || {}).rolled_back || (final(r) || {}).status === 'rolled_back')
// Trả bản tóm tắt ngắn kèm đường dẫn. Báo cáo đợt do phiên chính hoặc một workflow riêng làm, không nối vào workflow ghi.
const summary = r => r && ({
  lane: r.lane, status: (final(r) || {}).status, held_until: (final(r) || {}).held_until, pass: passed(r),
  loi_production: (lastCheck(r) || {}).loi_production, loi_bao_cao: ((lastCheck(r) || {}).loi_bao_cao || []).length,
  ket_qua: (final(r) || {}).folder ? `${final(r).folder}/ket-qua.json` : undefined, stop: STOP || undefined,
})

// ---------- Mẫu A: đồ thị phụ thuộc, chuỗi độc lập chạy song song (bản 7, 23/10) ----------
// Mỗi chuỗi là các lane có phụ thuộc thật (cùng URL, post, file, hoặc cần dữ liệu lane trước). Chuỗi độc lập chạy ngay trong pool.
const CHAINS = [[LANES[0]], [LANES[1]]]
const outA = await pool(CHAINS, SLOTS, async chain => {
  const out = []
  for (const L of chain) {
    const r = await runLane(L); out.push(r)
    if (!r || !passed(r) || rolledBack(r)) break
  }
  return out
})
return outA.filter(Boolean).flat().filter(Boolean).map(summary)

// ---------- Mẫu B: chuỗi có cổng (Đợt 1 tối ưu VPS, 24/10) ----------
// Lane sau tự kiểm điều kiện thật trên file trước khi làm, vì agent bị TaskStop vẫn có thể trả kết quả.
// const [L_MOC, L_KHONG_RESTART, L_STG, L_PROD, L_DUOI] = LANES   // L_MOC có readOnly: true
// const out = []
// const moc = await runLane(L_MOC); out.push(moc)
// if (!final(moc) || final(moc).status === 'blocked') { log('Không có mốc: dừng đợt'); return out.map(summary) }
// const a = await runLane(L_KHONG_RESTART, `\nMục mốc còn thiếu (đo bổ sung): xem ${L_MOC.folder}/kiem-doc-lap.md mục "Lượt 1".`); out.push(a)
// if (rolledBack(a)) { log('Lane bị trả lại vì lỗi site: dừng đợt'); return out.map(summary) }
// const stg = await runLane(L_STG); out.push(stg)
// if (rolledBack(stg)) { log('Staging bị trả lại: dừng đợt'); return out.map(summary) }
// const stgOk = passed(stg) && (final(stg) || {}).status === 'done'
// const prod = await runLane(L_PROD, `\nTRẠNG THÁI STAGING theo workflow: ${stgOk ? 'ĐẠT' : 'KHÔNG ĐẠT (chỉ làm việc không phụ thuộc staging)'}. Trước khi ghi production, tự kiểm ${L_STG.folder}/ket-qua.json có status done và ${L_STG.folder}/kiem-doc-lap.md lượt cuối không có lỗi production. Không khớp thì trả status held.`); out.push(prod)
// if (rolledBack(prod)) { log('Production bị trả lại: dừng đợt'); return out.map(summary) }
// out.push(await runLane(L_DUOI))
// return out.map(summary)

// ---------- Mẫu C: audit chỉ đọc → plan → phản biện → sửa plan (audit host, 23/10) ----------
// Lane audit: model 'sonnet', effort 'high'. Plan và phản biện: Opus.
// const FIND = { type: 'object', properties: { findings: { type: 'array', items: { type: 'string' } }, proposals: { type: 'array', items: { type: 'object', properties: {
//   id: { type: 'string' }, action: { type: 'string' }, gain: { type: 'string' }, risk: { type: 'string' }, needs_approval: { type: 'boolean' }, rollback: { type: 'string' }, measure: { type: 'string' },
// }, required: ['id', 'action', 'gain', 'risk', 'needs_approval'] } }, report_path: { type: 'string' } }, required: ['findings', 'proposals', 'report_path'] }
// const PLAN = { type: 'object', properties: { plan_path: { type: 'string' }, summary: { type: 'array', items: { type: 'string' } }, approval_steps: { type: 'array', items: { type: 'string' } } }, required: ['plan_path', 'summary', 'approval_steps'] }
// const CRIT = { type: 'object', properties: { ok: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } }, missing: { type: 'array', items: { type: 'string' } } }, required: ['ok', 'problems', 'missing'] }
// const audits = await pool(LANES, SLOTS, L => goi(`${COMMON}\nCHỈ ĐỌC. Mỗi đề xuất có việc cụ thể, lợi ích có số, rủi ro, cách đo trước/sau, cách trả lại, cần Lead duyệt hay không. Ghi báo cáo vào ${L.folder}/bao-cao.md.\n${L.task}`, { label: 'audit:' + L.key, phase: 'Làm', model: 'sonnet', effort: 'high', schema: FIND }))
// const reports = audits.map((a, i) => a && `- ${LANES[i].key}: ${a.report_path} (${a.proposals.length} đề xuất)`).filter(Boolean).join('\n')
// const plan = await goi(`${COMMON}\nĐọc các báo cáo audit dưới, gom thành MỘT plan, xếp theo lợi ích/rủi ro, có thứ tự chạy và mục "Cần Lead quyết" (câu hỏi ngắn, có đề xuất mặc định).\n${reports}`, { label: 'plan', phase: 'Kiểm', model: 'opus', effort: 'xhigh', schema: PLAN })
// const crit = plan ? await goi(`${COMMON}\nPhản biện plan ${plan.plan_path}: số lợi ích phóng đại, việc có thể làm hỏng site, thiếu cách trả lại, sai thứ tự với lane đang chạy, thiếu đòn bẩy lớn. Ghi phan-bien.md. ok=false nếu cần sửa plan.`, { label: 'phan-bien', phase: 'Kiểm', model: 'opus', effort: 'high', schema: CRIT }) : null
// const fixed = crit && !crit.ok ? await goi(`${COMMON}\nSửa ${plan.plan_path} theo phan-bien.md cùng thư mục. Thêm mục "Đã sửa theo phản biện".`, { label: 'sua-plan', phase: 'Sửa', model: 'opus', effort: 'xhigh', schema: PLAN }) : null
// return { audits: reports, plan: fixed || plan, critique: crit, stop: STOP || undefined }

// ---------- Mẫu D: nhiều lô cùng tài nguyên, kiểm lô N song song với ghi lô N+1 (lô chữ Đợt 1, 20/10) ----------
// Ghi tuần tự vì chung tài nguyên. Kiểm chỉ đọc nên chạy song song với lô ghi kế tiếp. Lỗi production ở lô N chặn lô N+2 trở đi:
// trước khi ghi lô i, chờ lượt kiểm lô i-2 xong. Cùng lúc tối đa 2 agent: ghi lô i và kiểm lô i-1.
// Với 6 agent mỗi workflow: tối đa 3 lô (3 ghi + 3 kiểm). Vòng sửa để workflow sau.
// let chan = ''
// const checks = []
// for (const [i, L] of LANES.entries()) {
//   if (i >= 2) await checks[i - 2]
//   if (chan) { log(`Dừng trước ${L.key}: ${chan}`); break }
//   const w = await goi(workPrompt(L), { label: `lam:${L.key}`, phase: 'Làm', model: L.model, effort: L.effort, schema: RESULT })
//   if (!w || w.status === 'held') break
//   checks.push(goi(checkPrompt(L, 1), { label: `kiem:${L.key}`, phase: 'Kiểm', ...checkOpts(L), schema: CHECK })
//     .then(c => { if (c && c.loi_production.length) chan = `lỗi production ở ${L.key}`; return { lane: L.key, work: w, check: c } }))
// }
// const lots = await Promise.all(checks)
// return lots.map(summary)
