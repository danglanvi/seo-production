// Lighthouse local (mô phỏng như PSI) cho ca "CLS hoặc FCP chỉ PSI thấy, perf_probe không tái hiện". Dựng lại môi trường PSI trên máy mình.
//   node "$WPS/scripts/lh_local.mjs" --url <URL> [--dev mobile|desktop] [--runs 1] [--out <thư mục>] [--block-vary] [--block '<glob>,<glob>']
//     [--obs-cpu 1.2] [--delay 200] [--sim-cpu 4] [--expect '<chuỗi trong title>'] [--expect-path /path/] [--resolve host=ip] [--lh-modules <thư mục node_modules>] [--dry-run]
// --block-vary: chặn *guest.vary.php*. LiteSpeed Guest Mode reload trang một lần cho khách thường, PSI không reload. Chặn để trang giữ bản Guest Mode như PSI.
// --obs-cpu: CPU throttle của Chrome thật (mặc định 1). --sim-cpu: cpuSlowdownMultiplier của mô phỏng Lantern (mặc định 4, như PSI mobile).
// --delay: trễ thêm (ms) cho mỗi request tới host của URL (mặc định 0), để giả lập máy PSI chậm hơn máy bạn.
// Module Lighthouse lấy từ --lh-modules, biến LH_MODULES, hoặc cache npx (~/.npm/_npx/*/node_modules có lighthouse, chrome-launcher, puppeteer-core). Không tự tải.
// Không có --out thì chỉ in kết quả. Có --out thì ghi thêm results.jsonl và lh_<thiết bị>_run<N>.json (dạng {lighthouseResult: ...}, đọc được bằng psi_cls_dump.py).
// --dry-run: in cấu hình sẽ dùng rồi thoát, không mở Chrome, không gọi mạng.
// In ra: host của URL, không in đường dẫn cá nhân. Guard chống đo nhầm: status >= 400, title không chứa --expect, host thật lệch,
//   path thật khác path của --url (redirect) hoặc khác --expect-path → thoát mã 4. Kết quả ghi trường path (path thật của lượt đo).
// Mã thoát: 0 xong, 1 lỗi chạy, 2 thiếu tham số, 3 không thấy module Lighthouse, 4 guard báo lỗi.
import {existsSync, mkdirSync, readdirSync, appendFileSync, writeFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {join} from 'node:path';
import {args} from './_chrome.mjs';
import {verdict, line as guardLine, checkTunnel, GUARD_EXIT} from './_guard.mjs';

const o = args(process.argv.slice(2), ['block-vary', 'dry-run', 'help', 'no-guard']);
const USAGE = 'Dùng: node lh_local.mjs --url URL [--dev mobile|desktop] [--runs 1] [--out dir] [--block-vary] [--block glob,glob] [--obs-cpu 1] [--delay 0] [--sim-cpu 4] [--expect title] [--expect-path /path/] [--resolve host=ip] [--lh-modules dir] [--dry-run] [--no-guard]\nMô tả đầy đủ ở đầu file script.';
if (o.help) { console.log(USAGE); process.exit(0); }
if (!o.url || o.url === true) { console.error(USAGE); process.exit(2); }

const url = o.url, dev = o.dev || 'mobile', runs = +(o.runs || 1);
if (!['mobile', 'desktop'].includes(dev) || !(runs >= 1)) { console.error('--dev phải là mobile hoặc desktop, --runs >= 1'); process.exit(2); }
const host = new URL(url).host;
const obsCpu = +(o['obs-cpu'] || 1), delay = +(o.delay || 0), simCpu = +(o['sim-cpu'] || 4);
const blocked = [...(o['block-vary'] ? ['*guest.vary.php*'] : []), ...String(o.block === true || !o.block ? '' : o.block).split(',').filter(Boolean)];
const UA = dev === 'mobile'
  ? 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
  : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36';
const slow4g = {rttMs: 150, throughputKbps: 1638.4, requestLatencyMs: 562.5, downloadThroughputKbps: 1474.56, uploadThroughputKbps: 675};
const flags = {output: 'json', onlyCategories: ['performance'], logLevel: 'error', formFactor: dev, emulatedUserAgent: UA,
  blockedUrlPatterns: blocked, throttlingMethod: 'simulate',
  throttling: dev === 'mobile' ? {...slow4g, cpuSlowdownMultiplier: simCpu} : {rttMs: 40, throughputKbps: 10240, cpuSlowdownMultiplier: 1, requestLatencyMs: 0, downloadThroughputKbps: 0, uploadThroughputKbps: 0},
  ...(dev === 'desktop' ? {screenEmulation: {mobile: false, width: 1350, height: 940, deviceScaleFactor: 1, disabled: false}} : {})};

if (o['dry-run']) {
  console.log(JSON.stringify({host, dev, runs, obsCpu, delay, simCpu, out: o.out || null, flags}, null, 1));
  console.log('DRY-RUN: chưa mở Chrome, chưa gọi mạng.');
  process.exit(0);
}

function findModules() {
  const need = ['lighthouse', 'chrome-launcher', 'puppeteer-core'];
  const cands = [o['lh-modules'], process.env.LH_MODULES];
  const npx = join(homedir(), '.npm', '_npx');
  if (existsSync(npx)) for (const d of readdirSync(npx)) cands.push(join(npx, d, 'node_modules'));
  return cands.filter(c => c && c !== true).find(c => need.every(n => existsSync(join(c, n)))) || null;
}
const NM = findModules();
if (!NM) {
  console.error('Không thấy lighthouse, chrome-launcher, puppeteer-core. Chạy một lần: npx --yes -p lighthouse -p chrome-launcher -p puppeteer-core true, hoặc đặt --lh-modules <thư mục node_modules>.');
  process.exit(3);
}
if (!o['no-guard']) {
  try { await checkTunnel(o.resolve, url); } catch (e) { console.error('GUARD LỖI: ' + e.message); process.exit(GUARD_EXIT); }
}
const lighthouse = (await import(join(NM, 'lighthouse/core/index.js'))).default;
const chromeLauncher = await import(join(NM, 'chrome-launcher/dist/index.js'));
// puppeteer-core ≤24 để file ở lib/esm/, bản 25 chuyển sang lib/puppeteer/ (cache npx 28/10/2026).
const puppeteer = (await import(join(NM, ['lib/esm/puppeteer', 'lib/puppeteer'].map(d => `puppeteer-core/${d}/puppeteer-core.js`).find(f => existsSync(join(NM, f))) || 'puppeteer-core/lib/esm/puppeteer/puppeteer-core.js'))).default;

if (o.out && o.out !== true) mkdirSync(o.out, {recursive: true});
const chrome = await chromeLauncher.launch({chromeFlags: ['--headless=new', '--ignore-certificate-errors', ...(o.resolve && o.resolve !== true ? [`--host-resolver-rules=MAP ${String(o.resolve).split('=')[0]} ${String(o.resolve).split('=')[1]}`] : [])]});
let code = 0;
try {
  for (let i = 1; i <= runs; i++) {
    const browser = await puppeteer.connect({browserURL: `http://127.0.0.1:${chrome.port}`, defaultViewport: null});
    const page = (await browser.pages())[0] || (await browser.newPage());
    if (delay > 0) {
      const cdp = await page.createCDPSession();
      await cdp.send('Fetch.enable', {patterns: [{urlPattern: `*://${host}/*`, requestStage: 'Request'}]});
      cdp.on('Fetch.requestPaused', async e => {
        await new Promise(r => setTimeout(r, delay));
        await cdp.send('Fetch.continueRequest', {requestId: e.requestId}).catch(() => {});
      });
    }
    if (obsCpu !== 1) { const c2 = await page.createCDPSession(); await c2.send('Emulation.setCPUThrottlingRate', {rate: obsCpu}); }
    const lr = (await lighthouse(url, flags, undefined, page)).lhr;
    const title = await page.title().catch(() => '');
    const realHost = await page.evaluate('location.host').catch(() => host);
    const finalPath = (() => { try { return new URL(lr.finalDisplayedUrl || lr.finalUrl).pathname; } catch { return null; } })();
    const a = lr.audits;
    const nr = a['network-requests']?.details?.items || [];
    const doc = nr.find(x => x.resourceType === 'Document') || {};
    const num = k => (a[k]?.numericValue == null ? null : Math.round(a[k].numericValue));
    const rec = {run: i, host: realHost, path: finalPath, dev, time: new Date().toISOString(), err: lr.runtimeError?.code || null,
      score: Math.round((lr.categories.performance.score || 0) * 100), FCP: num('first-contentful-paint'), LCP: num('largest-contentful-paint'),
      TBT: num('total-blocking-time'), CLS: +(a['cumulative-layout-shift']?.numericValue ?? -1).toFixed(3),
      status: doc.statusCode ?? null, blocked, obsCpu, delay, simCpu, lh: lr.lighthouseVersion};
    if (!o['no-guard']) {
      console.log(guardLine({host: realHost, status: rec.status, title}));
      const errs = verdict({requestedHost: host, finalHost: realHost, status: rec.status, title, expect: o.expect === true ? undefined : o.expect,
        requestedPath: new URL(url).pathname, finalPath, expectPath: o['expect-path'] === true ? undefined : o['expect-path']});
      if (errs.length) { console.error('GUARD LỖI: ' + errs.join('; ')); code = GUARD_EXIT; await browser.disconnect(); break; }
    }
    console.log(JSON.stringify(rec));
    if (o.out && o.out !== true) {
      appendFileSync(join(o.out, 'results.jsonl'), JSON.stringify(rec) + '\n');
      writeFileSync(join(o.out, `lh_${dev}_run${i}.json`), JSON.stringify({lighthouseResult: lr}));
    }
    await browser.disconnect();
  }
} catch (e) {
  console.error('Lỗi chạy Lighthouse: ' + String(e.message || e).split('\n')[0]);
  code = 1;
} finally {
  await chrome.kill();
}
process.exit(code);
