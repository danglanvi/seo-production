// Chrome headless qua CDP, chỉ dùng Node 22+ (WebSocket, fetch có sẵn). Rút gọn từ web-qa-gate/scripts/_cdp.mjs.
import {spawn} from 'child_process';
import {existsSync, mkdtempSync, rmSync} from 'fs';
import {tmpdir} from 'os';
import {join} from 'path';

export const sleep = ms => new Promise(r => setTimeout(r, ms));
export const MUA = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36';
export const DUA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
// Chặn analytics để lượt chụp không lọt vào GA4 (ca thật 26/10/2026: headless lọt page_view lên production).
export const BLOCK = ['googletagmanager.com', 'google-analytics.com', 'analytics.google.com', 'doubleclick.net', 'facebook.net',
  'facebook.com', 'clarity.ms', 'hotjar.com', 'tiktok.com', 'zalo.me', 'sp.zalo.me'];

export function chromeBin() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  for (const p of ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'])
    if (existsSync(p)) return p;
  throw new Error('không tìm thấy Chrome: đặt biến CHROME_BIN');
}

export function args(argv, bools = []) {
  const o = {_: []};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) { o._.push(argv[i]); continue; }
    const k = argv[i].slice(2);
    o[k] = (!bools.includes(k) && argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
  }
  return o;
}

export async function openTab({block = BLOCK} = {}) {
  const port = 9700 + Math.floor(Math.random() * 250), prof = mkdtempSync(join(tmpdir(), 'xbb-'));
  const rules = block.flatMap(h => [`MAP ${h} ~NOTFOUND`, `MAP *.${h} ~NOTFOUND`]).join(', ');
  const chrome = spawn(chromeBin(), ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${port}`,
    `--user-data-dir=${prof}`, '--no-first-run', '--no-default-browser-check', `--host-resolver-rules=${rules}`, 'about:blank'], {stdio: 'ignore'});
  let list;
  for (let i = 0; i < 80 && !list; i++) { await sleep(150); try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch {} }
  if (!list) { chrome.kill('SIGKILL'); throw new Error('Chrome không mở được cổng CDP'); }
  const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once: true}));
  let id = 0; const pending = new Map(), events = [];
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({id: i, method, params})); });
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
    if (m.method) events.push(m);
  });
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  const evalv = async (expression, awaitPromise = false) => {
    const r = await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise});
    if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || 'lỗi JS khi đo');
    return r.result?.result?.value;
  };
  const close = async () => { try { ws.close(); } catch {} chrome.kill('SIGKILL'); await sleep(300); try { rmSync(prof, {recursive: true, force: true}); } catch {} };
  return {send, evalv, events, close};
}

export async function setViewport(tab, W, H = null) {
  const mob = W < 800, h = H || (mob ? 844 : 900);
  await tab.send('Emulation.setDeviceMetricsOverride', {width: W, height: h, deviceScaleFactor: 1, mobile: mob});
  await tab.send('Emulation.setTouchEmulationEnabled', {enabled: mob});
  await tab.send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
  return {mob, H: h};
}

// Tải URL, chờ load, rê chuột và bấm Shift một lần (LiteSpeed hoãn JS tới lần chạm đầu), rồi chờ thêm.
export async function loadUrl(tab, url, wait = 2000) {
  tab.events.length = 0;
  await tab.send('Page.navigate', {url});
  for (let i = 0; i < 60 && !tab.events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
  await sleep(wait);
  await tab.send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: 120, y: 200});
  await tab.send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Shift'});
  await tab.send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift'});
  await sleep(800);
}

export async function shot(tab, file, fullPage = true) {
  const {writeFileSync} = await import('fs');
  let clip;
  if (fullPage) {
    const h = await tab.evalv('Math.min(document.documentElement.scrollHeight, 16000)');
    const w = await tab.evalv('document.documentElement.clientWidth');
    clip = {x: 0, y: 0, width: w, height: h, scale: 1};
  }
  const r = await tab.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: !!fullPage, ...(clip ? {clip} : {})});
  writeFileSync(file, Buffer.from(r.result.data, 'base64'));
}

// Lỗi JS kèm URL script gây lỗi (lấy từ stack nếu exceptionDetails không có url).
export function jsErrors(tab) {
  return tab.events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => {
    const d = e.params.exceptionDetails, fr = d.stackTrace?.callFrames || [];
    return {msg: (d.exception?.description || d.text || '').split('\n')[0], url: d.url || fr.find(f => f.url)?.url || ''};
  });
}
