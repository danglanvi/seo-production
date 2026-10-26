// Đo trên Chrome headless cho web-qa-gate, gom từ ux_probe.mjs, axe_run.mjs, focus.mjs và tiles.mjs của đợt 15–18/10/2026.
// node browser_probe.mjs --job job.json --out browser.jsonl [--tabs N] [--resume] [--sample N|P%] [--seed S] [--cache cached|nc|both] [--page-timeout ms]
// node browser_probe.mjs --help
// job.json do qa_gate.py dựng: pages [{name,url,form}], widths, axe_js, axe_widths, focus_widths, focus_max, block, tracking,
//   shots_dir, tiles, host, resolve, cookie, wait. Mỗi dòng ra = một URL x một bề rộng.
// Cờ quét nhiều URL (hs-8): --tabs N chạy N Chrome song song (tối đa 6); --resume bỏ qua dòng đã đo tốt trong --out và đo lại dòng lỗi;
//   --sample N|P% lấy mẫu N URL hoặc P% số URL (cố định theo --seed, URL có "always": true luôn nằm trong mẫu).
// Cờ bản cache: --cache cached đo bản có cache (URL sạch, tải 2 lần nếu lần đầu chưa hit), nc đo bản bỏ cache (?nc=ngẫu nhiên), both đo cả hai.
//   Không có cờ: tải đúng URL đã cho (variant "default"). Mỗi dòng ghi variant và header cache. Axe, focus và ảnh chụp chỉ chạy ở variant đầu.
// Vệ sinh: mỗi URL x bề rộng có trần thời gian (--page-timeout, mặc định 120000 ms), hết giờ thì ghi err và mở lại Chrome. Chrome mồ côi của
//   lượt cũ bị dọn khi bắt đầu. Job có thể khai hide_selectors (danh sách selector) hoặc hide_fixed: true để ẩn nút nổi khi chụp ảnh.
//   tiles: số màn chụp mỗi URL, hoặc "all" (mặc định) = đủ ceil(page_h/vh) màn, tối đa tiles_max (mặc định 12).
// Mã thoát: 0 có ít nhất một dòng đo tốt, 1 không dòng nào đo tốt hoặc không mở được Chrome, 2 sai tham số.
// Không gửi form, không bấm nút. Mọi request tới tracking bị chặn từ đầu phiên (Network.setBlockedURLs).
// Bề rộng < 800 px dùng UA điện thoại, cảm ứng và DPR gần 2, nhưng không bật cờ mobile của CDP: cờ này nới innerWidth theo phần tràn
// (đặt 390 thì JS đọc 421 lúc load), nên slider dựng theo sai mốc. Script vẫn so với bề rộng đặt (vw), không so với innerWidth.
// Mỗi bề rộng tải lại trang (slider dựng theo cỡ lúc tải) và UA là Chrome thường (UA HeadlessChrome làm slick không khởi tạo).
import fs from 'node:fs'; import path from 'node:path';
import {args, openTab, sleep, MUA, DUA, withTimeout, sweepOrphans} from './_cdp.mjs';

const USAGE = `browser_probe.mjs --job job.json --out browser.jsonl [--tabs N] [--resume] [--sample N|P%] [--seed S] [--cache cached|nc|both] [--page-timeout ms]
  --job            file job.json do qa_gate.py dựng.
  --out            file jsonl. Mỗi dòng: một URL x một bề rộng x một variant.
  --tabs N         chạy N Chrome song song (1 đến 6, mặc định 1).
  --resume         bỏ qua dòng đã đo tốt trong --out, đo lại dòng lỗi. Không có cờ này thì ghi thêm vào cuối file.
  --sample N|P%    đo N URL, hoặc P% số URL (ví dụ 12 hoặc 15%). Chọn cố định theo --seed (mặc định 1). URL có "always": true luôn được chọn.
  --cache MODE     cached (bản có cache), nc (bản bỏ cache), both. Mặc định: tải đúng URL đã cho.
  --page-timeout   trần thời gian cho mỗi URL x bề rộng, mili giây (mặc định 120000).
  --list           chỉ in kế hoạch đo (URL, bề rộng, variant còn phải đo) rồi thoát. Không mở Chrome. Kết hợp được với --resume và --sample.
  --help           in trợ giúp này.`;
const o = args(process.argv.slice(2), ['help', 'resume', 'list']);
if (o.help) { console.log(USAGE); process.exit(0); }
if (!o.job || !o.out) { console.error(USAGE); process.exit(2); }
let job;
try { job = JSON.parse(fs.readFileSync(o.job, 'utf8')); } catch (e) { console.error('không đọc được job: ' + e.message); process.exit(2); }
const cacheMode = o.cache === undefined ? null : String(o.cache);
if (cacheMode !== null && !['cached', 'nc', 'both'].includes(cacheMode)) { console.error('--cache chỉ nhận cached, nc hoặc both'); process.exit(2); }
const tabsN = o.tabs === undefined ? 1 : parseInt(o.tabs, 10);
if (!(tabsN >= 1)) { console.error('--tabs phải là số nguyên từ 1'); process.exit(2); }
const variants = cacheMode === null ? ['default'] : (cacheMode === 'both' ? ['cached', 'nc'] : [cacheMode]);
const PAGE_TIMEOUT = +(o['page-timeout'] || job.page_timeout || 120000);

// Lấy mẫu cố định: cùng seed cho cùng danh sách thì ra cùng mẫu. Giữ thứ tự gốc của danh sách.
function samplePages(pages, spec, seed = 1) {
  if (spec === undefined || spec === null || spec === true) return pages;
  const m = String(spec).match(/^(\d+(?:\.\d+)?)(%?)$/);
  if (!m) throw new Error('--sample nhận N hoặc P%');
  const want = m[2] ? Math.ceil(pages.length * parseFloat(m[1]) / 100) : parseInt(m[1], 10);
  if (want >= pages.length) return pages;
  let a = (seed >>> 0) || 1;
  const rnd = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const idx = pages.map((_, i) => i), keep = new Set(idx.filter(i => pages[i].always));
  const rest = idx.filter(i => !keep.has(i));
  for (let i = rest.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [rest[i], rest[j]] = [rest[j], rest[i]]; }
  for (const i of rest) { if (keep.size >= want) break; keep.add(i); }
  return idx.filter(i => keep.has(i)).map(i => pages[i]);
}
const widths = job.widths || [360, 768, 1366];
const axeW = new Set(job.axe_widths || [widths[0], widths[widths.length - 1]]);
const focusW = new Set(job.focus_widths || [widths[0], widths[widths.length - 1]]);
const AXE = job.axe_js ? fs.readFileSync(job.axe_js, 'utf8') : null;
const tilesCfg = job.tiles ?? 'all', tilesMax = job.tiles_max || 12;
const tiles = tilesCfg === 'all' ? tilesMax : +tilesCfg;
if (job.shots_dir && tiles > 0) fs.mkdirSync(job.shots_dir, {recursive: true});
const glob = p => new RegExp('^' + p.split('*').map(s => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$', 'i');
const trackRe = (job.tracking || job.block || []).map(glob);
const isTracking = u => trackRe.some(r => r.test(u));

const PROBE = `(async(vw)=>{
const H=innerHeight;
const vis=e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&+s.opacity>0.05};
const sel=e=>{let s=e.tagName.toLowerCase();if(e.id)s+='#'+e.id;const c=[...e.classList].filter(x=>!/^elementor-(element|widget)-[0-9a-f]+$/.test(x)).slice(0,2);if(c.length)s+='.'+c.join('.');return s};
for(let y=0;y<Math.min(document.documentElement.scrollHeight,30000);y+=H*0.8){scrollTo(0,y);await new Promise(r=>setTimeout(r,120));}
scrollTo(0,0);await new Promise(r=>setTimeout(r,500));
const clipped=e=>{for(let p=e.parentElement;p&&p!==document.body;p=p.parentElement){const s=getComputedStyle(p);if(/(hidden|clip|auto|scroll)/.test(s.overflowX))return true;}return false};
const all=[...document.body.querySelectorAll('*')].filter(e=>!['SCRIPT','STYLE','NOSCRIPT','svg','path','BR'].includes(e.tagName));
const over=[];for(const e of all){const r=e.getBoundingClientRect();if(r.width>0&&r.right>vw+2&&vis(e)&&!clipped(e))over.push({s:sel(e),r:Math.round(r.right)});}
const uniq=a=>{const m=new Map();for(const x of a){if(!m.has(x.s))m.set(x.s,{...x,n:0});m.get(x.s).n++;}return [...m.values()].sort((a,b)=>b.r-a.r)};
const isSearch=f=>f.getAttribute('role')==='search'||!!f.querySelector('input[name="s"],input[type="search"]');
const forms=[...document.forms].filter(f=>!isSearch(f)).map(f=>{const ins=[...f.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]),textarea,select')];
  return {sel:sel(f),visible:vis(f),fields:ins.length,visibleFields:ins.filter(vis).length,submit:!!f.querySelector('[type=submit],button:not([type=button])'),
    hidden:[...f.querySelectorAll('input[type=hidden]')].map(x=>x.name).filter(Boolean).slice(0,20)}});
const imgs=[...document.images];
return {innerW:innerWidth,docW:document.documentElement.scrollWidth,docH:document.documentElement.scrollHeight,
 overflow:uniq(over).slice(0,8),overflowN:over.length,forms,
 brokenImgs:imgs.filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('src')&&!i.getAttribute('src').startsWith('data:')).length,
 title:document.title.slice(0,80)}
})`;

// changed: style của phần tử trước (outline, box-shadow, viền, nền, màu chữ, gạch chân) có đổi khi mất focus không.
// Đọc lúc Tab sang phần tử kế, nên không cần blur bằng script.
const FOCUS = `(()=>{const st=x=>{const s=getComputedStyle(x);return [s.outlineStyle,s.outlineWidth,s.outlineColor,s.boxShadow,s.borderTopColor,s.borderBottomColor,s.borderLeftColor,s.borderRightColor,s.borderBottomWidth,s.backgroundColor,s.color,s.textDecorationLine].join('|')};
 const p=window.__wqgPrev,e=document.activeElement;let prevChanged=null;if(p&&p.el!==e)prevChanged=st(p.el)!==p.s;
 if(!e||e===document.body){window.__wqgPrev=null;return {end:true,prevChanged}}
 window.__wqgPrev={el:e,s:st(e)};const s=getComputedStyle(e),r=e.getBoundingClientRect();
 const sig=(()=>{const p=[];for(let x=e,i=0;x&&x!==document.body&&i<3;x=x.parentElement,i++){let t=x.tagName.toLowerCase();if(x.id){p.unshift(t+'#'+x.id);break}const c=[...x.classList].slice(0,2);if(c.length)t+='.'+c.join('.');p.unshift(t)}return p.join(' > ')})();
 return {sig,txt:(e.innerText||e.value||e.getAttribute('aria-label')||'').trim().replace(/\\s+/g,' ').slice(0,40),href:(e.getAttribute('href')||'').slice(0,80),fv:e.matches(':focus-visible'),
  outline:s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0?s.outlineWidth+' '+s.outlineStyle+' '+s.outlineColor:'',shadow:s.boxShadow!=='none'?s.boxShadow.slice(0,60):'',
  inview:r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth,w:Math.round(r.width),h:Math.round(r.height),hidden:!e.checkVisibility(),prevChanged}})()`;

const AXE_RUN = `axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']},resultTypes:['violations']}).then(r=>JSON.stringify({version:axe.version,v:r.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,
  ex:v.nodes.slice(0,4).map(x=>{const d=(x.any[0]||{}).data||{};return {t:x.target.join(' ').slice(0,90),fg:d.fgColor,bg:d.bgColor,cr:d.contrastRatio,fs:d.fontSize}})}))}))`;

const pages = samplePages(job.pages || [], o.sample, o.seed === undefined ? 1 : parseInt(o.seed, 10));
const wait = +(job.wait || 2500);
const keyOf = r => `${r.name}|${r.vw}|${r.variant || 'default'}`;

// --resume: giữ dòng đo tốt, bỏ dòng lỗi (đo lại), ghi file mới thay file cũ.
const done = new Set();
if (o.resume && fs.existsSync(o.out)) {
  const keep = [];
  for (const l of fs.readFileSync(o.out, 'utf8').split('\n')) {
    if (!l.trim()) continue;
    try { const r = JSON.parse(l); if (!r.err) { keep.push(l); done.add(keyOf(r)); } } catch {}
  }
  fs.writeFileSync(o.out + '.tmp', keep.map(l => l + '\n').join(''));
  fs.renameSync(o.out + '.tmp', o.out);
}
fs.mkdirSync(path.dirname(path.resolve(o.out)), {recursive: true});
const out = fs.createWriteStream(o.out, {flags: 'a'});

const withNc = u => u + (u.includes('?') ? '&' : '?') + 'nc=' + Math.random().toString(36).slice(2, 10);
const stripNc = u => u.replace(/([?&])nc=[^&#]*&?/, '$1').replace(/[?&]$/, '');

async function load(tab, url) {
  tab.events.length = 0;
  await tab.send('Page.navigate', {url});
  for (let i = 0; i < 60 && !tab.events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
  await sleep(wait);
}
const respOf = tab => {
  const docs = tab.events.filter(e => e.method === 'Network.responseReceived' && e.params.type === 'Document');
  if (!docs.length) return {status: null, cache: ''};
  const r = docs[docs.length - 1].params.response, h = {};
  for (const k in r.headers || {}) h[k.toLowerCase()] = r.headers[k];
  return {status: r.status, cache: h['x-litespeed-cache'] || h['x-cache'] || h['cf-cache-status'] || ''};
};
const HIDE = `(()=>{const sels=%SELS%;document.querySelectorAll('[data-wqg-hidden]').forEach(e=>{e.style.visibility=e.dataset.wqgHidden;e.removeAttribute('data-wqg-hidden')});
 const hid=e=>{if(!e.hasAttribute('data-wqg-hidden')){e.setAttribute('data-wqg-hidden',e.style.visibility||'');e.style.visibility='hidden'}};
 for(const s of sels){try{document.querySelectorAll(s).forEach(hid)}catch{}}
 if(%FIXED%)for(const e of document.body.querySelectorAll('*')){const c=getComputedStyle(e);if(c.position==='fixed'&&e.getBoundingClientRect().top>100)hid(e)}})()`;

async function measure(tab, pg, W, variant, full) {
  const {send, evalv} = tab;
  const mob = W < 800, H = mob ? 800 : 900;
  const dpr = mob ? Math.min(2, Math.floor(1568 / Math.max(W, H) * 100) / 100) : 1;  // ảnh cho Jev tối đa 1.568 px mỗi cạnh
  const row = {name: pg.name, url: pg.url, vw: W, vh: H, mobile: mob, form: !!pg.form, variant};
  try {
    await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: dpr, mobile: false});
    await send('Emulation.setTouchEmulationEnabled', {enabled: mob});
    await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
    const url = variant === 'nc' ? withNc(stripNc(pg.url)) : (variant === 'cached' ? stripNc(pg.url) : pg.url);
    await load(tab, url);
    if (variant === 'cached') {
      // Bản có cache: lần tải đầu có thể là miss (làm nóng). Tải lại một lần để đo bản đã cache.
      const first = respOf(tab);
      if (first.cache && !/hit/i.test(first.cache)) { row.warmed = first.cache; await load(tab, url); }
    }
    const all = [...tab.events];
    // Tương tác giả để JS bị hoãn tới lần chạm đầu (LiteSpeed, delay JS) chạy như với người dùng thật. Tracking đã bị chặn.
    await send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: 120, y: 200});
    await send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Shift'}); await send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift'});
    await sleep(800);
    Object.assign(row, await evalv(`${PROBE}(${W})`, true) || {err: 'probe không trả kết quả'});
    Object.assign(row, respOf(tab));
    row.jsErrors = tab.events.filter(e => e.method === 'Runtime.exceptionThrown').length;
    if (full && job.shots_dir && tiles > 0) {
      row.shots = [];
      const docH = row.docH || H, need = Math.max(1, Math.ceil(docH / H)), n = Math.max(1, Math.min(tiles, need));
      row.tiles_needed = need; row.tiles_cap = tiles;
      const hideSels = job.hide_selectors || [], hideFixed = !!job.hide_fixed;
      if (hideSels.length || hideFixed) await evalv(HIDE.replace('%SELS%', JSON.stringify(hideSels)).replace('%FIXED%', hideFixed));
      for (let i = 0; i < n; i++) {
        const y = n === 1 ? 0 : Math.round(i * (docH - H) / (n - 1));
        await evalv(`scrollTo(0,${y})`); await sleep(500);
        const s = await send('Page.captureScreenshot', {format: 'jpeg', quality: 72});
        const file = `${pg.name}_${W}_${i}.jpg`;
        fs.writeFileSync(path.join(job.shots_dir, file), Buffer.from(s.result.data, 'base64'));
        row.shots.push({file, i, y, page_h: docH});
      }
      await evalv('scrollTo(0,0)');
      if (hideSels.length || hideFixed) await evalv(HIDE.replace('%SELS%', '[]').replace('%FIXED%', 'false'));
    }
    if (full && AXE && axeW.has(W)) {
      await send('Runtime.evaluate', {expression: AXE});
      const r = await evalv(AXE_RUN, true);
      const a = r ? JSON.parse(r) : null;
      row.axe = a ? {version: a.version, violations: a.v} : {err: 'axe không chạy'};
    }
    all.push(...tab.events);
    if (full && focusW.has(W)) {
      await load(tab, url);
      all.push(...tab.events);
      await send('Emulation.setFocusEmulationEnabled', {enabled: true});
      await evalv("document.documentElement.style.scrollBehavior='auto'");  // cuộn mượt làm phần tử vừa nhận focus còn ngoài màn hình lúc đo
      const items = [];
      for (let i = 0; i < (job.focus_max || 80); i++) {
        await send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9});
        await send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9});
        await sleep(120);
        const r = await evalv(FOCUS);
        if (!r) break;
        if (items.length && r.prevChanged !== null) items[items.length - 1].changed = r.prevChanged;
        delete r.prevChanged;
        if (r.end) break;
        if (items.length > 1 && r.sig === items[0].sig && r.txt === items[0].txt) break;  // vòng lại phần tử đầu
        items.push(r);
      }
      row.focus = {n: items.length, items};
      all.push(...tab.events);
    }
    // Đếm request tới tracking: bị chặn là đúng; lọt (có response) là FAIL.
    const reqs = new Map(), blocked = new Set(), answered = new Set();
    for (const e of all) {
      if (e.method === 'Network.requestWillBeSent') reqs.set(e.params.requestId, e.params.request.url);
      if (e.method === 'Network.loadingFailed' && e.params.blockedReason) blocked.add(e.params.requestId);
      if (e.method === 'Network.responseReceived') answered.add(e.params.requestId);
    }
    const tr = [...reqs].filter(([, u]) => isTracking(u));
    row.tracking = {seen: tr.length, blocked: tr.filter(([id]) => blocked.has(id)).length,
      leaked: [...new Set(tr.filter(([id]) => !blocked.has(id) && answered.has(id)).map(([, u]) => u.slice(0, 120)))]};
  } catch (e) { row.err = String(e).slice(0, 160); }
  return row;
}

const openOne = async () => {
  const t = await openTab({host: job.host, resolve: job.resolve, cookie: job.cookie, block: job.block || []});
  await t.send('Page.enable'); await t.send('Runtime.enable');
  return t;
};
const queue = [];
for (const pg of pages) for (const W of widths) for (const variant of variants) {
  if (!done.has(`${pg.name}|${W}|${variant}`)) queue.push({pg, W, variant, full: variant === variants[0]});
}
if (o.list) {
  console.log(JSON.stringify({pages: pages.map(p => p.name), todo: queue.map(t => `${t.pg.name}|${t.W}|${t.variant}`), skipped: done.size}));
  process.exit(0);
}
let ok = 0, bad = 0;
async function worker(id) {
  let tab = await openOne();
  while (queue.length) {
    const t = queue.shift();
    let row;
    try { row = await withTimeout(measure(tab, t.pg, t.W, t.variant, t.full), PAGE_TIMEOUT); }
    catch (e) {
      row = {name: t.pg.name, url: t.pg.url, vw: t.W, variant: t.variant, err: String(e.message || e).slice(0, 160)};
      try { await tab.close(); } catch {}
      tab = await openOne();   // phép đo bị treo: bỏ Chrome cũ, mở Chrome mới cho URL kế
    }
    out.write(JSON.stringify(row) + '\n');
    row.err ? bad++ : ok++;
    process.stderr.write(`${t.pg.name} ${t.W} ${variants.length > 1 || cacheMode ? t.variant + ' ' : ''}${row.err ? 'ERR ' + row.err : `st=${row.status} doc=${row.docW}/${t.W} cache=${row.cache || '-'} axe=${row.axe ? (row.axe.violations || []).length : '-'} focus=${row.focus ? row.focus.n : '-'} track=${row.tracking ? row.tracking.blocked + '/' + row.tracking.seen : '-'}`}\n`);
  }
  await tab.close();
}
try { sweepOrphans({apply: true}); } catch {}
try { await Promise.all(Array.from({length: Math.min(6, tabsN, queue.length)}, (_, i) => worker(i))); }
catch (e) { console.error('không mở được Chrome: ' + e.message); process.exit(1); }
await new Promise(r => out.end(r));
process.exit(ok > 0 || !queue.length && !bad ? 0 : 1);
