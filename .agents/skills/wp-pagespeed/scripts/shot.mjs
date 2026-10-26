// Chụp và kiểm chức năng từng URL trên desktop 1366 px và mobile 390 px. So 2 lượt bằng shot_cmp.py.
// node "$WPS/scripts/shot.mjs" --urls urls.tsv --out <thư mục> --label <tên> [--vis '{"menu":"#nav","cta":".float-btn"}'] [--blockcss] [--resolve host=ip] [--cookie n=v]
//   [--expect '<chuỗi trong title>'] [--no-guard] [--allow-redirect-host]
// Guard chống đo nhầm đích: mỗi URL x thiết bị in dòng "GUARD host=<host thật> status=<HTTP> title=<title>". Lỗi khi status >= 400 hoặc không có,
//   host thật khác host của URL (redirect), title không chứa --expect. Lỗi ở URL đầu tiên: thoát mã 4 ngay, chưa ghi kết quả.
//   Lỗi ở URL sau: chụp tiếp, ghi kết quả, đánh dấu guard trong results_<label>.json, thoát mã 4 cuối cùng.
//   Có --resolve thì kiểm cổng của ip trước khi mở Chrome. --no-guard tắt guard khi cố ý chụp trang lỗi.
// Mã thoát: 0 xong, 2 thiếu tham số, 4 guard báo lỗi.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass". --blockcss chặn file CSS không chặn hiển thị, chỉ chụp màn hình đầu (xem critical CSS).
// Không gửi form. Ghi results_<label>.json và ảnh <tên>_<thiết bị>[_atf].jpg.
import fs from 'node:fs'; import path from 'node:path';
import {args, openTab, sleep, MUA, DUA} from './_chrome.mjs';
import {verdict, line as guardLine, checkTunnel, GUARD_EXIT} from './_guard.mjs';

const o = args(process.argv.slice(2), ['blockcss', 'no-guard', 'allow-redirect-host', 'help']);
if (o.help || !o.urls || !o.out || !o.label) {
  console.log('Dùng: node shot.mjs --urls urls.tsv --out <thư mục> --label <tên> [--vis <json>] [--blockcss] [--resolve host=ip] [--cookie n=v] [--expect <title>] [--no-guard] [--allow-redirect-host]\nMô tả đầy đủ ở đầu file script.');
  process.exit(o.help ? 0 : 2);
}
const lines = fs.readFileSync(o.urls, 'utf8').trim().split('\n').filter(l => l.trim() && !l.startsWith('#')).map(l => l.split('\t'));
const vis = o.vis ? JSON.parse(o.vis) : {};
const block = !!o.blockcss;
if (!o['no-guard']) {
  try { await checkTunnel(o.resolve, lines[0][1]); } catch (e) { console.error('GUARD LỖI: ' + e.message); process.exit(GUARD_EXIT); }
}
fs.mkdirSync(o.out, {recursive: true});
let guardFails = 0;
const tab = await openTab({host: new URL(lines[0][1]).host, resolve: o.resolve, cookie: o.cookie});
const {send, evalv, events} = tab;
await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', {cacheDisabled: true});
if (block) await send('Network.setBlockedURLs', {urls: ['*/wp-content/litespeed/css/*', '*/wp-content/*.css*', '*fonts.googleapis.com/*', '*cdnjs.cloudflare.com/*.css*', '*cdn.jsdelivr.net/*.css*', '*unpkg.com/*.css*']});

const INFO = `(()=>{const vis=e=>{if(!e)return false;const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&s.opacity!=='0'};
  const forms=[...document.querySelectorAll('form')];const imgs=[...document.images];
  const icons=[...document.querySelectorAll('i[class*="fa-"],span[class*="fa-"],i[class*="eicon-"]')];
  const iconMissing=icons.filter(e=>{const c=getComputedStyle(e,'::before').content;return vis(e)&&(!c||c==='none'||c==='normal'||c==='""')}).length;
  const fonts=[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family.replace(/["']/g,'')+':'+f.weight+(f.style!=='normal'?f.style:''));
  const V=${JSON.stringify(vis)};const v={};for(const k in V)v['vis_'+k]=vis(document.querySelector(V[k]));
  return {innerWidth,scrollWidth:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,
    forms:forms.length,formsVisible:forms.filter(vis).length,
    imgs:imgs.length,brokenImgs:imgs.filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('src')&&!i.getAttribute('src').startsWith('data:')).map(i=>i.getAttribute('src').slice(-80)).slice(0,10),
    slick:document.querySelectorAll('.slick-initialized').length,owl:document.querySelectorAll('.owl-loaded').length,
    swiper:document.querySelectorAll('.swiper-initialized,.swiper-container-initialized').length,flickity:document.querySelectorAll('.flickity-enabled').length,
    jq:typeof window.jQuery==='function'?window.jQuery.fn.jquery:null,icons:icons.length,iconMissing,fonts:[...new Set(fonts)].sort(),
    title:document.title.slice(0,80),...v}})()`;

const results = [];
for (const [name, url] of lines) for (const dev of ['desktop', 'mobile']) {
  const mob = dev === 'mobile', W = mob ? 390 : 1366, H0 = mob ? 844 : 900;
  // Không bật cờ mobile của CDP: cờ này nới innerWidth theo phần tràn, nên scrollWidth luôn bằng innerWidth và slider dựng theo sai mốc.
  await send('Emulation.setDeviceMetricsOverride', {width: W, height: H0, deviceScaleFactor: mob ? 2 : 1, mobile: false});
  await send('Emulation.setTouchEmulationEnabled', {enabled: mob});
  await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
  events.length = 0;
  await send('Page.navigate', {url});
  for (let i = 0; i < 60 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
  await sleep(block ? 1500 : 2500);
  const atf = await send('Page.captureScreenshot', {format: 'jpeg', quality: 70, clip: {x: 0, y: 0, width: W, height: H0, scale: mob ? 1 : 0.6}});
  fs.writeFileSync(path.join(o.out, `${name}_${dev}_atf.jpg`), Buffer.from(atf.result.data, 'base64'));
  const status = events.find(e => e.method === 'Network.responseReceived' && e.params.type === 'Document')?.params.response.status ?? null;
  const realHost = await evalv('location.host'), realTitle = await evalv('document.title');
  let guard = null;
  if (!o['no-guard']) {
    const errs = verdict({requestedHost: new URL(url).host, finalHost: realHost, status, title: realTitle, expect: o.expect === true ? undefined : o.expect, allowRedirectHost: !!o['allow-redirect-host']});
    console.log(guardLine({host: realHost, status, title: realTitle}));
    if (errs.length) {
      guard = errs; guardFails++;
      console.error(`GUARD LỖI ${name} ${dev}: ${errs.join('; ')}`);
      if (results.length === 0) { console.error('URL đầu tiên lỗi guard: dừng, chưa ghi kết quả. Kiểm URL, --expect, tunnel rồi chạy lại (hoặc --no-guard).'); await tab.close(); process.exit(GUARD_EXIT); }
    }
  }
  if (block) { results.push({name, url, dev, status, ...(guard ? {guard} : {})}); console.log(`${o.label} ${name} ${dev} atf`); continue; }
  // Tương tác giả để JS bị trễ (LiteSpeed Guest Mode, delay JS) chạy, rồi cuộn hết trang để ảnh lazy-load tải.
  await send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: 200, y: 300});
  await send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Shift'}); await send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift'});
  await evalv(`(async()=>{const h=document.documentElement.scrollHeight;for(let y=0;y<Math.min(h,15000);y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,120));}window.scrollTo(0,0);})()`, true);
  await sleep(3000);
  const info = await evalv(INFO);
  const errs = new Set();
  for (const e of events) {
    if (e.method === 'Runtime.exceptionThrown') errs.add('EXC ' + (e.params.exceptionDetails.exception?.description || e.params.exceptionDetails.text).split('\n')[0].slice(0, 200));
    if (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error') errs.add('CONSOLE ' + e.params.args.map(a => a.value ?? a.description ?? '').join(' ').slice(0, 200));
    if (e.method === 'Log.entryAdded' && e.params.entry.level === 'error') errs.add('LOG ' + (e.params.entry.text + ' ' + (e.params.entry.url || '')).slice(0, 200));
  }
  const reqs = events.filter(e => e.method === 'Network.responseReceived');
  const bytes = events.filter(e => e.method === 'Network.loadingFinished').reduce((s, e) => s + (e.params.encodedDataLength || 0), 0);
  const imgReq = reqs.filter(e => e.params.type === 'Image');
  const webp = imgReq.filter(e => /webp|avif/.test(e.params.response.mimeType)).length;
  const H = Math.min(info.height, mob ? 9000 : 7000);
  const shot = await send('Page.captureScreenshot', {format: 'jpeg', quality: 55, captureBeyondViewport: true, clip: {x: 0, y: 0, width: W, height: H, scale: mob ? 0.5 : 0.4}});
  fs.writeFileSync(path.join(o.out, `${name}_${dev}.jpg`), Buffer.from(shot.result.data, 'base64'));
  results.push({name, url, dev, vw: W, status, ...(guard ? {guard} : {}), reqs: reqs.length, kb: Math.round(bytes / 1024), imgReq: imgReq.length, webp, ...info, errors: [...errs]});
  const vs = Object.keys(vis).map(k => `${k}=${info['vis_' + k]}`).join(' ');
  console.log(`${o.label} ${name} ${dev} st=${status} sw=${info.scrollWidth}/${info.innerWidth} forms=${info.formsVisible}/${info.forms} broken=${info.brokenImgs.length} icons=${info.icons}-${info.iconMissing} jq=${info.jq} kb=${Math.round(bytes / 1024)} webp=${webp}/${imgReq.length} errs=${errs.size} ${vs}`);
}
fs.writeFileSync(path.join(o.out, `results_${o.label}.json`), JSON.stringify(results, null, 1));
await tab.close();
console.log('SHOT_DONE');
if (guardFails) { console.error(`GUARD LỖI: ${guardFails} lượt chụp lỗi, xem trường guard trong results_${o.label}.json`); process.exit(GUARD_EXIT); }
process.exit(0);
