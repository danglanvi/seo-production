// Trace long task theo hàm JS trước khi sửa JS (lớp 6, checklist-theo-lop.md). Chrome headless qua CDP, chỉ đọc trang.
//   node "$WPS/scripts/trace_fn.mjs" --url <URL sạch> [--dev mobile|desktop] [--cpu 4] [--runs 3] [--settle 5000] [--min-task 50]
//     [--block '<glob>,<glob>'] [--expect '<chuỗi trong title>'] [--expect-path /path/] [--resolve host=ip] [--cookie tên=giá trị]
//     [--out file.json] [--no-guard]
// Mỗi long task (> --min-task ms) in: mốc bắt đầu, độ dài, thời gian Layout + UpdateLayoutTree bên trong, và các lệnh gọi JS từ 8 ms
// (FunctionCall, TimerFire, EvaluateScript, EventDispatch, FireAnimationFrame, v8.compile) kèm tên hàm, file, dòng. Script inline in
// thêm đoạn đầu của dòng nguồn lấy từ HTML gốc (lineNumber của trace tính từ 1). Trường "nguon" của task: "js" khi có lệnh gọi JS từ 8 ms, "layout" khi không có.
// Không thêm tham số vào URL: URL có tham số có thể nhận HTML khác bản cache (noindex, khác lazy-load). Tắt cache trình duyệt mỗi lượt.
// Mặc định chặn GTM, GA4, Ads, doubleclick, Facebook, Apps Script để bài đo không gửi hit thật. --block thêm mẫu chặn.
// Mobile 412×823, DPR 1,75; desktop 1350×940. CPU throttle --cpu (mặc định 4). Không giả lập mạng chậm.
// tbt_obs = tổng (độ dài − 50 ms) của long task sau FCP, số quan sát trên máy này, không phải TBT của PSI.
// Guard như lh_local.mjs (_guard.mjs): HTTP >= 400, host hoặc path bị redirect, title không chứa --expect, path khác --expect-path → mã 4.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass" từ .agent-secrets/.env, không gõ vào lệnh.
// Mã thoát: 0 xong, 1 lỗi đo, 2 thiếu hoặc sai tham số, 4 guard báo lỗi.
import {writeFileSync} from 'fs';
import {args, openTab, sleep, MUA, DUA} from './_chrome.mjs';
import {verdict, line as guardLine, checkTunnel, die as guardDie, GUARD_EXIT} from './_guard.mjs';

const o = args(process.argv.slice(2), ['no-guard', 'help']);
const USAGE = 'Dùng: node trace_fn.mjs --url URL [--dev mobile|desktop] [--cpu 4] [--runs 3] [--settle 5000] [--min-task 50] [--block glob,glob] [--expect title] [--expect-path /path/] [--resolve host=ip] [--cookie n=v] [--out file.json] [--no-guard]\nMô tả đầy đủ ở đầu file script.';
if (o.help) { console.log(USAGE); process.exit(0); }
if (!o.url || o.url === true) { console.error(USAGE); process.exit(2); }
const dev = o.dev || 'mobile', cpu = +(o.cpu || 4), runs = +(o.runs || 3), settle = +(o.settle || 5000), minTask = +(o['min-task'] || 50);
if (!['mobile', 'desktop'].includes(dev) || !(runs >= 1) || !(cpu >= 1)) { console.error('--dev phải là mobile hoặc desktop, --runs >= 1, --cpu >= 1'); process.exit(2); }
const u = new URL(o.url);
const BLOCK = ['*googletagmanager.com/*', '*google-analytics.com/*', '*doubleclick.net/*', '*googleadservices.com/*', '*connect.facebook.net/*',
  '*facebook.com/tr*', '*script.google.com/*', ...String(o.block === true || !o.block ? '' : o.block).split(',').filter(Boolean)];
const CALL = /^(FunctionCall|TimerFire|EvaluateScript|FireAnimationFrame|EventDispatch|v8\.compile|XHRReadyStateChange)$/;
const noQuery = s => String(s || '').split(/[?#]/)[0];

if (!o['no-guard']) { try { await checkTunnel(o.resolve, o.url); } catch (e) { guardDie(e.message); } }
const tab = await openTab({host: u.host, resolve: o.resolve, cookie: o.cookie});
let code = 0;
const out = [];
try {
  await tab.send('Network.enable');
  await tab.send('Network.setBlockedURLs', {urls: BLOCK});
  await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
  await tab.send('Emulation.setDeviceMetricsOverride', dev === 'mobile' ? {width: 412, height: 823, deviceScaleFactor: 1.75, mobile: true} : {width: 1350, height: 940, deviceScaleFactor: 1, mobile: false});
  await tab.send('Emulation.setUserAgentOverride', {userAgent: dev === 'mobile' ? MUA : DUA});
  await tab.send('Page.enable');
  let doc = null, chunks = [], complete = null;
  tab.on(m => {
    if (m.method === 'Network.responseReceived' && m.params.type === 'Document' && !doc) doc = {id: m.params.requestId, status: m.params.response.status};
    else if (m.method === 'Tracing.dataCollected') chunks.push(...m.params.value);
    else if (m.method === 'Tracing.tracingComplete' && complete) complete();
  });
  for (let r = 1; r <= runs; r++) {
    await tab.send('Page.navigate', {url: 'about:blank'});
    await sleep(200);
    doc = null; chunks = []; tab.events.length = 0;
    await tab.send('Emulation.setCPUThrottlingRate', {rate: cpu});
    await tab.send('Tracing.start', {transferMode: 'ReportEvents', traceConfig: {includedCategories: ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'v8.execute', 'blink.user_timing', 'loading']}});
    await tab.send('Page.navigate', {url: o.url});
    for (let i = 0; i < 600; i++) { await sleep(100); if (await tab.evalv(`document.readyState==='complete'`)) break; }
    await sleep(settle);
    const ended = new Promise(res => { complete = res; setTimeout(res, 30000); });
    await tab.send('Tracing.end');
    await ended;
    await tab.send('Emulation.setCPUThrottlingRate', {rate: 1});
    const pg = await tab.evalv('({host: location.host, path: location.pathname, title: document.title})') || {};
    if (!o['no-guard']) {
      const errs = verdict({requestedHost: u.host, finalHost: pg.host, status: doc ? doc.status : null, title: pg.title, expect: o.expect === true ? undefined : o.expect,
        requestedPath: u.pathname, finalPath: pg.path, expectPath: o['expect-path'] === true ? undefined : o['expect-path']});
      if (r === 1 || errs.length) console.log(guardLine({host: pg.host, status: doc ? doc.status : null, title: pg.title}));
      if (errs.length) { console.error('GUARD LỖI: ' + errs.join('; ') + '. Số đo bỏ, kiểm URL, --expect, --expect-path rồi chạy lại.'); code = GUARD_EXIT; break; }
    }
    let html = '';
    if (doc) {
      const b = (await tab.send('Network.getResponseBody', {requestId: doc.id})).result;
      if (b) html = b.base64Encoded ? Buffer.from(b.body, 'base64').toString('utf8') : b.body;
    }
    const lines = html.split('\n');
    const cnt = {};
    for (const e of chunks) if (e.name === 'ParseHTML') cnt[e.pid + ':' + e.tid] = (cnt[e.pid + ':' + e.tid] || 0) + 1;
    const main = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0]?.[0];
    if (!main) { console.error(`Lượt ${r}: trace không có ParseHTML, không xác định được luồng chính.`); code = 1; continue; }
    const on = e => e.pid + ':' + e.tid === main;
    const X = chunks.filter(e => e.ph === 'X' && e.dur && on(e)).sort((a, b) => a.ts - b.ts || b.dur - a.dur);
    const nav = chunks.find(e => e.name === 'navigationStart' && on(e)) || X[0];
    const fcp = chunks.find(e => e.name === 'firstContentfulPaint' && on(e));
    const tasks = X.filter(e => e.name === 'RunTask' && e.dur > minTask * 1000);
    let tbt = 0; const lt = [], fn = {};
    for (const t of tasks) {
      const dur = t.dur / 1000;
      if (!fcp || t.ts >= fcp.ts) tbt += dur - 50;
      const kids = X.filter(e => e !== t && e.ts >= t.ts && e.ts + e.dur <= t.ts + t.dur);
      const isLayout = e => e.name === 'Layout' || e.name === 'UpdateLayoutTree';
      const calls = [];
      for (const c of kids.filter(e => CALL.test(e.name))) {
        if (c.dur / 1000 < 8) continue;
        const d = c.args?.data || {};
        const file = noQuery(d.url).split('/').pop() || '(inline)';
        const inline = d.url && noQuery(d.url) === noQuery(o.url);
        const src = inline && d.lineNumber != null ? (lines[d.lineNumber - 1] || '').trim().slice(0, 70) : '';
        const lay = kids.filter(e => isLayout(e) && e.ts >= c.ts && e.ts + e.dur <= c.ts + c.dur).reduce((s, e) => s + e.dur, 0) / 1000;
        const k = `${c.name}:${d.functionName || d.type || ''}@${inline ? '(inline)' : file}:${d.lineNumber ?? ''}${src ? ' ' + src : ''}`;
        calls.push(`${k}=${Math.round(c.dur / 1000)}(layout ${Math.round(lay)})`);
        fn[k] = (fn[k] || 0) + c.dur / 1000;
      }
      const layT = kids.filter(isLayout).reduce((s, e) => s + e.dur, 0) / 1000;
      lt.push({start: Math.round((t.ts - nav.ts) / 1000), dur: Math.round(dur), layout: Math.round(layT), nguon: calls.length ? 'js' : 'layout', calls: calls.slice(0, 6)});
    }
    const res = {run: r, dev, cpu, path: pg.path, fcp: fcp ? Math.round((fcp.ts - nav.ts) / 1000) : null, tbt_obs: Math.round(tbt),
      long_tasks: lt, top_fn: Object.fromEntries(Object.entries(fn).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([k, v]) => [k, Math.round(v)]))};
    out.push(res);
    console.log(JSON.stringify(res));
  }
} catch (e) {
  console.error('Lỗi đo: ' + String(e.message || e).split('\n')[0]);
  code = 1;
} finally {
  await tab.close();
}
if (o.out && o.out !== true && out.length) writeFileSync(o.out, JSON.stringify(out, null, 1));
console.log(`TRACE_FN_DONE runs=${out.length} long_tasks=${out.reduce((s, x) => s + x.long_tasks.length, 0)} js=${out.reduce((s, x) => s + x.long_tasks.filter(t => t.nguon === 'js').length, 0)}`);
process.exit(code);
