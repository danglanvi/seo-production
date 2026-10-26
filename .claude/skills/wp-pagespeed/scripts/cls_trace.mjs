// Tìm nguồn CLS: in từng layout shift kèm mốc giờ, điểm, phần tử và toạ độ trước > sau (y/cao, px CSS).
// node cls_trace.mjs --url URL [--desktop] [--runs 3] [--net slow|fast|<trễ ms>,<kbps>] [--cpu 4]
//   [--session '{"khoa":"giá trị"}'] [--local '{"khoa":"giá trị"}'] [--eval '<biểu thức JS in kèm kết quả>']
//   [--host h --resolve h=ip --cookie ten=gia-tri]   (staging: CDP_AUTH="user:pass" từ file env)
// --session, --local nạp sẵn sessionStorage, localStorage trước khi mở URL: dùng để đo từng nhánh của trang đổi bố cục theo dữ liệu
// (trang thanh toán có đơn và không có đơn, khách đã đăng nhập). Chặn GTM, GA, Facebook, Apps Script: bài đo không gửi hit thật.
// Mặc định mobile 412×823 DPR 1,75, mạng chậm 150 ms + 1,6 Mbps, CPU x4. --net fast: font về trước lần vẽ đầu, gần lượt tải thật của PSI.
import {args, openTab, sleep, MUA, DUA} from './_chrome.mjs';

const o = args(process.argv.slice(2), ['desktop']);
if (!o.url) { console.error('Thiếu --url'); process.exit(2); }
const BLOCK = ['*googletagmanager.com/*', '*google-analytics.com/*', '*doubleclick.net/*', '*connect.facebook.net/*', '*facebook.com/tr*', '*script.google.com/*'];
const net = o.net || 'slow', runs = +(o.runs || 1);
const [lat, kbps] = net === 'slow' ? [150, 1600] : net === 'fast' ? [0, 0] : net.split(',').map(Number);

const tab = await openTab({host: o.host || new URL(o.url).host, resolve: o.resolve, cookie: o.cookie});
await tab.send('Network.enable');
await tab.send('Network.setBlockedURLs', {urls: BLOCK});
await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
await tab.send('Emulation.setDeviceMetricsOverride', o.desktop ? {width: 1350, height: 940, deviceScaleFactor: 1, mobile: false} : {width: 412, height: 823, deviceScaleFactor: 1.75, mobile: true});
await tab.send('Emulation.setUserAgentOverride', {userAgent: o.desktop ? DUA : MUA});
await tab.send('Page.enable');
await tab.send('Page.addScriptToEvaluateOnNewDocument', {source: `window.__cls=0;window.__sh=[];new PerformanceObserver(function(l){l.getEntries().forEach(function(e){if(e.hadRecentInput)return;window.__cls+=e.value;
window.__sh.push([Math.round(e.startTime),+e.value.toFixed(4),(e.sources||[]).map(function(s){var n=s.node,r=function(x){return Math.round(x.y)+'/'+Math.round(x.height)};
return (n&&n.nodeType===1?(n.id?'#'+n.id:n.tagName.toLowerCase()+(typeof n.className==='string'&&n.className?'.'+n.className.split(' ')[0]:'')):'?')+'@'+r(s.previousRect)+'>'+r(s.currentRect)}).join(' | ')])})}).observe({type:'layout-shift',buffered:true});`});

async function go(url) {
  await tab.send('Page.navigate', {url});
  for (let i = 0; i < 300; i++) { await sleep(100); if (await tab.evalv(`document.readyState==='complete'`)) break; }
}
if (o.session || o.local) {
  await go(new URL(o.url).origin + '/robots.txt');
  for (const [k, store] of [['session', 'sessionStorage'], ['local', 'localStorage']]) {
    if (o[k]) for (const [key, v] of Object.entries(JSON.parse(o[k]))) await tab.evalv(`${store}.setItem(${JSON.stringify(key)}, ${JSON.stringify(typeof v === 'string' ? v : JSON.stringify(v))}); true`);
  }
}
for (let r = 1; r <= runs; r++) {
  if (lat || kbps) await tab.send('Network.emulateNetworkConditions', {offline: false, latency: lat, downloadThroughput: kbps * 125, uploadThroughput: 750 * 125});
  else await tab.send('Network.emulateNetworkConditions', {offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1});
  await tab.send('Emulation.setCPUThrottlingRate', {rate: +(o.cpu || (o.desktop ? 1 : 4))});
  await go(o.url + (o.url.includes('?') ? '&' : '?') + 'clst=' + Date.now());
  await sleep(2500);
  await tab.send('Emulation.setCPUThrottlingRate', {rate: 1});
  const res = await tab.evalv(`({cls:+window.__cls.toFixed(4),shifts:window.__sh})`);
  if (o.eval) res.eval = await tab.evalv(o.eval);
  console.log(JSON.stringify({run: r, net, ...res}));
}
await tab.close();
