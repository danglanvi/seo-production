// Điều khiển Chrome headless qua DevTools Protocol (Node ≥22 có WebSocket sẵn).
//   node cdp.mjs audit <deck.html>                 → in JSON: phần tử tràn vùng nội dung của từng slide
//   node cdp.mjs shots <deck.html> <outdir> [n..]  → chụp PNG 1920×1080 từng slide (mặc định: mọi slide)
// Mỗi lần chạy: user-data-dir riêng, timeout 120 giây, xong thì đóng và kill đúng nhóm tiến trình Chrome đã mở.
import { spawn } from 'node:child_process';
import fs from 'node:fs'; import path from 'node:path'; import os from 'node:os';

const [, , mode, file, outdir, ...nums] = process.argv;
// Đường dẫn Chrome: biến CHROME_PATH, rồi vị trí mặc định của macOS, Linux, Windows.
const CH = process.env.CHROME_PATH || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome',
  '/usr/bin/chromium', '/usr/bin/chromium-browser', 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'].find(p => fs.existsSync(p));
if (!CH) { console.error('cdp: không thấy Chrome; đặt CHROME_PATH'); process.exit(2); }
const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'qpcdp_'));
const ch = spawn(CH, ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--user-data-dir=${ud}`, '--remote-debugging-port=0',
  '--window-size=1920,1080', 'about:blank'], { detached: true, stdio: 'ignore' });
const cleanup = () => { try { process.kill(-ch.pid, 'SIGKILL'); } catch { } try { fs.rmSync(ud, { recursive: true, force: true }); } catch { } };
const timer = setTimeout(() => { console.error('cdp: timeout'); cleanup(); process.exit(2); }, 120000);
const sleep = ms => new Promise(r => setTimeout(r, ms));

const AUDIT = `(async () => {
  await document.fonts.ready;
  const out = [], slides = [...document.querySelectorAll('.slide')];
  const desc = el => (el.className && typeof el.className === 'string' ? el.tagName.toLowerCase() + '.' + el.className.trim().split(/\\s+/).join('.') : el.tagName.toLowerCase());
  for (const [i, s] of slides.entries()) {
    slides.forEach(x => x.classList.remove('active', 'visible'));
    s.classList.add('active', 'visible');
    const hasWrap = !!s.querySelector('.wrap');
    const box = hasWrap ? {l: 118, r: 1802, b: 1002} : {l: 60, r: 1860, b: 1012};
    const root = s.querySelector('.wrap') || s;
    const bad = [];
    root.querySelectorAll('*').forEach(el => {
      if (el.closest('.foot,.chrome,.bg-grid,.glow,.beat-rings,svg')) return;
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) return;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden') return;
      const over = [];
      if (r.bottom > box.b) over.push('dưới ' + Math.round(r.bottom - box.b) + 'px');
      if (r.right > box.r) over.push('phải ' + Math.round(r.right - box.r) + 'px');
      if (r.left < box.l) over.push('trái ' + Math.round(box.l - r.left) + 'px');
      if (cs.overflow !== 'visible' && !el.classList.contains('tl') && !el.classList.contains('typed') && !el.classList.contains('sb')) {
        if (el.scrollHeight > el.clientHeight + 3) over.push('cắt dọc ' + (el.scrollHeight - el.clientHeight) + 'px');
        if (el.scrollWidth > el.clientWidth + 3) over.push('cắt ngang ' + (el.scrollWidth - el.clientWidth) + 'px');
      }
      if (over.length) bad.push({el, d: desc(el), over: over.join(', '), txt: (el.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 70)});
    });
    const top = bad.filter(b => !bad.some(o => o.el !== b.el && o.el.contains(b.el) && o.over.split(',')[0].split(' ')[0] === b.over.split(',')[0].split(' ')[0]));
    const clip = [...s.querySelectorAll('.tl')].filter(el => el.scrollWidth > el.clientWidth + 2).map(el => el.innerText.trim().slice(0, 50));
    out.push({n: i + 1, title: s.dataset.title, bad: top.slice(0, 6).map(b => ({d: b.d, over: b.over, txt: b.txt})), clip});
  }
  return out;
})()`;

try {
  let port;
  for (let i = 0; i < 150 && !port; i++) { try { port = fs.readFileSync(path.join(ud, 'DevToolsActivePort'), 'utf8').split('\n')[0]; } catch { await sleep(100); } }
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = no; });
  let id = 0; const pend = new Map();
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file://' + path.resolve(file) + '?qa' });
  await sleep(1500);
  await send('Runtime.evaluate', { expression: 'document.fonts.ready.then(() => 1)', awaitPromise: true });
  if (mode === 'audit') {
    const r = await send('Runtime.evaluate', { expression: AUDIT, awaitPromise: true, returnByValue: true });
    console.log(JSON.stringify(r.result.result.value ?? r.result));
  } else if (mode === 'shots') {
    fs.mkdirSync(outdir, { recursive: true });
    const cnt = (await send('Runtime.evaluate', { expression: "document.querySelectorAll('.slide').length", returnByValue: true })).result.result.value;
    const list = nums.length ? nums.map(Number) : Array.from({ length: cnt }, (_, i) => i + 1);
    for (const n of list) {
      await send('Runtime.evaluate', { expression: `(() => { const s=[...document.querySelectorAll('.slide')]; s.forEach((x,k)=>{x.classList.toggle('active',k===${n - 1});x.classList.toggle('visible',k===${n - 1});}); s[${n - 1}].dispatchEvent(new CustomEvent('enter')); document.getElementById('counter').textContent='${n} / '+s.length; })()` });
      await sleep(350);
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(path.join(outdir, `s${String(n).padStart(3, '0')}.png`), Buffer.from(shot.result.data, 'base64'));
    }
    console.log(`cdp: ${list.length} ảnh → ${outdir}`);
  } else if (mode === 'hover') {
    // node cdp.mjs hover <deck.html> <out.png> <slide> <selector>: rê chuột lên phần tử đầu tiên khớp selector rồi chụp
    const [n, sel] = nums;
    const pos = (await send('Runtime.evaluate', { returnByValue: true, expression: `(() => { const s=[...document.querySelectorAll('.slide')]; s.forEach((x,k)=>{x.classList.toggle('active',k===${n - 1});x.classList.toggle('visible',k===${n - 1});}); s[${n - 1}].dispatchEvent(new CustomEvent('enter')); const el=s[${n - 1}].querySelector(${JSON.stringify(sel)}); if(!el) return null; const r=el.getBoundingClientRect(); return {x:r.left+Math.min(r.width/2,40), y:r.top+r.height/2}; })()` })).result.result.value;
    if (!pos) { console.log('cdp: không thấy phần tử'); } else {
      await sleep(400);
      await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: pos.x, y: pos.y });
      await sleep(300);
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(outdir, Buffer.from(shot.result.data, 'base64'));
      const tip = (await send('Runtime.evaluate', { returnByValue: true, expression: "(() => { const t=document.getElementById('qtip'); return t && t.classList.contains('on') ? t.innerText.slice(0, 160) : 'KHÔNG HIỆN'; })()" })).result.result.value;
      console.log('cdp: tooltip →', tip);
    }
  }
  await send('Browser.close').catch(() => { });
} catch (err) {
  console.error('cdp:', err.message);
  clearTimeout(timer); cleanup(); process.exit(2);
}
clearTimeout(timer); cleanup(); process.exit(0);
