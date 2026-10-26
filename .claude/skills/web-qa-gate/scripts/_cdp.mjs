// Mở Chrome headless riêng (profile tạm, cổng ngẫu nhiên) và trả về một tab CDP. Chép từ wp-pagespeed/scripts/_chrome.mjs, thêm chặn tracking.
// Chrome: biến CHROME_BIN, rồi Chrome cài sẵn của macOS/Linux, rồi Chromium của Playwright (~/Library/Caches/ms-playwright, ~/.cache/ms-playwright).
// Basic Auth (biến WEB_QA_AUTH hoặc CDP_AUTH = "user:pass") chỉ gắn cho request tới đúng host truyền vào. resolve: "host=ip".
// block: danh sách mẫu URL (có *) bị chặn bằng Network.setBlockedURLs, tương đương route abort của Playwright.
import {spawn, execFileSync} from 'child_process';
import {existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync} from 'fs';
import {homedir, tmpdir} from 'os';
import {join} from 'path';

export const MUA = 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36';
export const DUA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
export const sleep = ms => new Promise(r => setTimeout(r, ms));

// Chrome do script này mở. Thoát tiến trình (kể cả Ctrl+C, kill) thì giết Chrome, để không để lại Chrome mồ côi.
const liveChrome = new Set();
const killLive = () => { for (const c of liveChrome) { try { c.kill('SIGKILL'); } catch {} } liveChrome.clear(); };
process.on('exit', killLive);
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(sig, () => { killLive(); process.exit(130); });
const alive = pid => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } };

// Tìm (apply=true thì giết) Chrome mồ côi: thư mục profile wqg-* mà tiến trình node đã mở nó (ghi trong owner.pid) không còn sống.
// Chrome của lượt chạy khác đang sống không bị đụng. Thư mục cũ không có owner.pid chỉ bị coi là mồ côi khi quá 2 giờ.
export function sweepOrphans({apply = false, tmp = tmpdir(), prefix = 'wqg-'} = {}) {
  let ps = '';
  try { ps = execFileSync('ps', ['-axo', 'pid=,command='], {encoding: 'utf8', maxBuffer: 32 << 20}); } catch {}
  const procs = ps.split('\n').map(l => l.trim().match(/^(\d+)\s+(.*)$/)).filter(Boolean).map(m => ({pid: +m[1], cmd: m[2]}));
  const out = [];
  for (const name of readdirSync(tmp).filter(n => n.startsWith(prefix))) {
    const dir = join(tmp, name);
    let owner = null, orphan;
    try {
      if (!statSync(dir).isDirectory()) continue;
      try { owner = parseInt(readFileSync(join(dir, 'owner.pid'), 'utf8'), 10); } catch {}
      orphan = owner ? !alive(owner) : Date.now() - statSync(dir).mtimeMs > 2 * 3600e3;
    } catch { continue; }
    if (!orphan) continue;
    const pids = procs.filter(p => p.pid !== process.pid && p.cmd.includes(`--user-data-dir=${dir}`)).map(p => p.pid);
    if (apply) {
      for (const pid of pids) { try { process.kill(pid, 'SIGKILL'); } catch {} }
      try { rmSync(dir, {recursive: true, force: true}); } catch {}
    }
    out.push({dir, owner, pids, removed: apply});
  }
  return out;
}

export function chromeBin() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  const fixed = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
  for (const p of fixed) if (existsSync(p)) return p;
  for (const base of [join(homedir(), 'Library/Caches/ms-playwright'), join(homedir(), '.cache/ms-playwright')]) {
    if (!existsSync(base)) continue;
    for (const d of readdirSync(base).filter(x => /^chromium-\d+$/.test(x)).sort().reverse()) {
      const cands = [
        join(base, d, 'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        join(base, d, 'chrome-mac/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        join(base, d, 'chrome-mac/Chromium.app/Contents/MacOS/Chromium'),
        join(base, d, 'chrome-linux/chrome'),
      ];
      for (const c of cands) if (existsSync(c)) return c;
    }
  }
  throw new Error('không tìm thấy Chrome: đặt CHROME_BIN hoặc cài Chromium của Playwright');
}

export function args(argv, bools = []) {
  const opt = {_: []};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) { opt._.push(argv[i]); continue; }
    const k = argv[i].slice(2);
    opt[k] = (!bools.includes(k) && argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
  }
  return opt;
}

export async function openTab({host, resolve, cookie, block = []} = {}) {
  const port = 9300 + Math.floor(Math.random() * 400), prof = mkdtempSync(join(tmpdir(), 'wqg-'));
  const flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
    '--no-first-run', '--no-default-browser-check', '--ignore-certificate-errors'];
  if (resolve) { const [h, ip] = String(resolve).split('='); flags.push(`--host-resolver-rules=MAP ${h} ${ip}`); }
  try { writeFileSync(join(prof, 'owner.pid'), String(process.pid)); } catch {}
  const chrome = spawn(chromeBin(), [...flags, 'about:blank'], {stdio: 'ignore'});
  liveChrome.add(chrome);
  let list;
  for (let i = 0; i < 80 && !list; i++) { await sleep(150); try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch {} }
  if (!list) { chrome.kill('SIGKILL'); liveChrome.delete(chrome); throw new Error('Chrome không mở được cổng CDP'); }
  const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once: true}));
  const cred = process.env.WEB_QA_AUTH || process.env.CDP_AUTH;
  const auth = cred ? 'Basic ' + Buffer.from(cred).toString('base64') : null;
  let id = 0; const pending = new Map(), events = [], listeners = [];
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({id: i, method, params})); });
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
    if (m.method === 'Fetch.requestPaused') {
      const headers = Object.entries(m.params.request.headers).map(([name, value]) => ({name, value}));
      if (auth) headers.push({name: 'Authorization', value: auth});
      ws.send(JSON.stringify({id: ++id, method: 'Fetch.continueRequest', params: {requestId: m.params.requestId, headers}}));
      return;
    }
    if (m.method) { events.push(m); listeners.forEach(f => f(m)); }
  });
  await send('Network.enable');
  if (block.length) await send('Network.setBlockedURLs', {urls: block});
  if (auth && host) await send('Fetch.enable', {patterns: [{urlPattern: `https://${host}/*`, requestStage: 'Request'}, {urlPattern: `http://${host}/*`, requestStage: 'Request'}]});
  for (const c of String(cookie || '').split(';').filter(Boolean)) {
    const [n, v] = c.split('=');
    await send('Network.setCookie', {name: n.trim(), value: v, domain: host, path: '/'});
  }
  const evalv = async (expression, awaitPromise = false) => (await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise})).result?.result?.value;
  const close = async () => { try { ws.close(); } catch {} chrome.kill('SIGKILL'); liveChrome.delete(chrome); await sleep(300); try { rmSync(prof, {recursive: true, force: true}); } catch {} };
  return {send, evalv, events, on: f => listeners.push(f), close};
}

// ---- Hàm dùng chung cho các script đo mới (interact_probe, landmarks). browser_probe.mjs giữ bản riêng của nó. ----

// Đặt viewport thật (không bật cờ mobile của CDP, xem browser_probe.mjs). Dưới 800 px: UA điện thoại và cảm ứng.
export async function setViewport(tab, W, H = null) {
  const mob = W < 800, h = H || (mob ? 800 : 900);
  await tab.send('Emulation.setDeviceMetricsOverride', {width: W, height: h, deviceScaleFactor: 1, mobile: false});
  await tab.send('Emulation.setTouchEmulationEnabled', {enabled: mob});
  await tab.send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
  return {mob, H: h};
}

// Tải URL, chờ load, giả một lần rê chuột và phím Shift (LiteSpeed hoãn JS tới lần chạm đầu), rồi chờ thêm.
export async function loadUrl(tab, url, wait = 2500) {
  tab.events.length = 0;
  await tab.send('Page.navigate', {url});
  for (let i = 0; i < 60 && !tab.events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
  await sleep(wait);
  await tab.send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: 120, y: 200});
  await tab.send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Shift'});
  await tab.send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift'});
  await sleep(800);
}

// Mã HTTP và header cache của tài liệu chính ở lượt tải gần nhất.
export function docResponse(tab) {
  const docs = tab.events.filter(e => e.method === 'Network.responseReceived' && e.params.type === 'Document');
  if (!docs.length) return {status: null, cache: ''};
  const r = docs[docs.length - 1].params.response, h = {};
  for (const k in r.headers || {}) h[k.toLowerCase()] = r.headers[k];
  return {status: r.status, cache: h['x-litespeed-cache'] || h['x-cache'] || h['cf-cache-status'] || ''};
}

// Chạm thật (touch) tại toạ độ viewport. Cần Emulation.setTouchEmulationEnabled (setViewport lo việc này ở bề rộng nhỏ).
export async function tap(tab, x, y) {
  await tab.send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x, y}]});
  await sleep(60);
  await tab.send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
}

// Cho một phép đo chạy tối đa ms mili giây. Hết giờ thì ném lỗi 'timeout'. Phép đo bị treo không giữ lượt quét.
export function withTimeout(promise, ms, label = 'timeout') {
  let t;
  return Promise.race([promise, new Promise((_, rej) => { t = setTimeout(() => rej(new Error(label)), ms); })]).finally(() => clearTimeout(t));
}
