// Mở Chrome headless riêng (profile tạm, cổng ngẫu nhiên) và trả về một tab CDP. Dùng chung cho shot.mjs và fontmap.mjs.
// Basic Auth (biến CDP_AUTH="user:pass") chỉ gắn cho request tới đúng host truyền vào. resolve: "host=ip".
import {spawn} from 'child_process';
import {mkdtempSync, rmSync} from 'fs';
import {tmpdir} from 'os';
import {join} from 'path';

export const MUA = 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36';
export const DUA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export function args(argv, bools = []) {
  const opt = {_: []};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) { opt._.push(argv[i]); continue; }
    const k = argv[i].slice(2);
    opt[k] = (!bools.includes(k) && argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
  }
  return opt;
}

export async function openTab({host, resolve, cookie} = {}) {
  const port = 9300 + Math.floor(Math.random() * 400), prof = mkdtempSync(join(tmpdir(), 'wps-'));
  const flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
    '--no-first-run', '--no-default-browser-check', '--ignore-certificate-errors'];
  if (resolve) { const [h, ip] = String(resolve).split('='); flags.push(`--host-resolver-rules=MAP ${h} ${ip}`); }
  const chrome = spawn(process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [...flags, 'about:blank'], {stdio: 'ignore'});
  let list;
  for (let i = 0; i < 80 && !list; i++) { await sleep(150); try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch {} }
  if (!list) { chrome.kill('SIGKILL'); throw new Error('Chrome không mở được cổng CDP'); }
  const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once: true}));
  const auth = process.env.CDP_AUTH ? 'Basic ' + Buffer.from(process.env.CDP_AUTH).toString('base64') : null;
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
  if (auth && host) await send('Fetch.enable', {patterns: [{urlPattern: `https://${host}/*`, requestStage: 'Request'}]});
  for (const c of String(cookie || '').split(';').filter(Boolean)) {
    const [n, v] = c.split('=');
    await send('Network.setCookie', {name: n, value: v, domain: host, path: '/', secure: true});
  }
  const evalv = async (expression, awaitPromise = false) => (await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise})).result?.result?.value;
  const close = async () => { try { ws.close(); } catch {} chrome.kill('SIGKILL'); await sleep(300); try { rmSync(prof, {recursive: true, force: true}); } catch {} };
  return {send, evalv, events, on: f => listeners.push(f), close};
}
