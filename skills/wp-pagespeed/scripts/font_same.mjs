// So font hiển thị giữa 2 URL, ví dụ production trước khi tự host font và staging sau khi tự host.
// Đo: bề rộng chuỗi mẫu tiếng Việt bằng canvas ở từng độ đậm, khung 6 phần tử đầu dùng họ font, số phần tử, chiều cao trang,
// request font, lỗi JS. Chặn GTM, GA, Pixel, Clarity, Hotjar, Apps Script. Tắt cache.
// node font_same.mjs --family Roboto --weights 700,800,900 --a <url trước> --b <url sau> [--dev desktop] [--text "..."]
// Staging: CDP_AUTH="user:pass" trong biến môi trường, --resolve host=ip, --cookie tên=giá trị. Hai tuỳ chọn này chỉ áp cho URL có đúng host.
import {openTab, sleep, args, MUA, DUA} from './_chrome.mjs';

const o = args(process.argv.slice(2));
if (!o.family || !o.a || !o.b) { console.error('Cần --family, --a, --b'); process.exit(1); }
const W = String(o.weights || '400,700').split(',').map(Number);
const T = o.text && o.text !== true ? o.text : 'Khoá học thực chiến 2026: Ăn Ơ Ư Đ ữ ỹ ệ ỗ, 1.990.000đ';
const BLOCK = ['*googletagmanager.com*', '*google-analytics.com*', '*analytics.google.com*', '*facebook.net*', '*facebook.com/tr*',
  '*doubleclick.net*', '*clarity.ms*', '*hotjar*', '*script.google.com*'];
const fam = JSON.stringify(o.family);
const M = `(async()=>{await document.fonts.ready;const c=document.createElement('canvas').getContext('2d');const r={w:{}};
 for(const w of ${JSON.stringify(W)}){await document.fonts.load(w+' 32px '+${JSON.stringify(JSON.stringify(o.family))},${JSON.stringify(T)});c.font=w+' 32px '+${JSON.stringify(JSON.stringify(o.family))};r.w[w]=c.measureText(${JSON.stringify(T)}).width.toFixed(1)}
 const els=[...document.querySelectorAll('body *')].filter(e=>e.offsetParent&&e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&getComputedStyle(e).fontFamily.replace(/["']/g,'').split(',')[0].trim()===${fam});
 r.n=els.length;r.box=els.slice(0,6).map(e=>{const b=e.getBoundingClientRect();return getComputedStyle(e).fontWeight+':'+Math.round(b.width)+'x'+Math.round(b.height)}).join(' ');
 r.h=document.documentElement.scrollHeight;return r})()`;

async function run(url) {
  const host = new URL(url).hostname;
  const own = o.resolve && String(o.resolve).startsWith(host + '=');
  const tab = await openTab(own ? {host, resolve: o.resolve, cookie: o.cookie} : {host});
  const {send} = tab;
  const errs = [], fonts = [];
  tab.on(m => {
    if (m.method === 'Runtime.exceptionThrown') errs.push((m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text || '').slice(0, 120));
    if (m.method === 'Network.responseReceived' && m.params.type === 'Font') fonts.push(m.params.response.url.split('?')[0].split('/').slice(-1)[0] + (/fonts\.gstatic/.test(m.params.response.url) ? ' (gstatic)' : ''));
  });
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setBlockedURLs', {urls: BLOCK});
  await send('Network.setCacheDisabled', {cacheDisabled: true});
  const mob = o.dev !== 'desktop';
  await send('Emulation.setDeviceMetricsOverride', mob ? {width: 412, height: 823, deviceScaleFactor: 1.75, mobile: true} : {width: 1366, height: 900, deviceScaleFactor: 1, mobile: false});
  await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
  await send('Page.navigate', {url}); await sleep(4000);
  const r = (await send('Runtime.evaluate', {expression: M, awaitPromise: true, returnByValue: true})).result?.result?.value || {};
  await tab.close();
  return {...r, fonts, errs};
}

const A = await run(o.a), B = await run(o.b);
for (const [k, v] of [['a', A], ['b', B]]) console.log(k, JSON.stringify(v));
const lech = W.filter(w => Math.abs(Number(A.w?.[w]) - Number(B.w?.[w])) > 0.15);
const giong = !lech.length && A.box === B.box && A.n === B.n && Math.abs(A.h - B.h) <= 2 && !B.errs.length;
console.log(giong ? 'GIỐNG: bề rộng chữ, khung phần tử, chiều cao trang không đổi' :
  'KHÁC:' + (lech.length ? ' bề rộng ở ' + lech.join(',') : '') + (A.box !== B.box ? ' khung phần tử' : '') + (A.n !== B.n ? ' số phần tử' : '') +
  (Math.abs(A.h - B.h) > 2 ? ` chiều cao ${A.h}→${B.h}` : '') + (B.errs.length ? ' có lỗi JS' : ''));
