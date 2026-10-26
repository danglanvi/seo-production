// Kiểm loader GTM hoãn (templates/gtm-delay-loader.php): không thao tác thì gtm.js chưa nạp trước mốc và đã nạp sau mốc,
// có thao tác thì nạp ngay, URL quảng cáo và trang chuyển đổi nạp ngay.
// node gtm_delay_check.mjs --url https://example.com/ [--delay 5000] [--mobile] [--now-url https://example.com/cam-on/]
//   [--host example.com --resolve example.com=<ip> --cookie ten=gia-tri]   (staging: CDP_AUTH="user:pass" từ file env)
// Chặn googletagmanager, google-analytics, doubleclick, facebook bằng Network.setBlockedURLs: bài kiểm không gửi hit thật.
// Script không cuộn trang (sự kiện scroll làm loader chạy sớm). Thao tác thử là phím Shift, không bấm vào link.
import {args, openTab, sleep, MUA, DUA} from './_chrome.mjs';

const o = args(process.argv.slice(2), ['mobile']);
if (!o.url) { console.error('Thiếu --url'); process.exit(2); }
const delay = +(o.delay || 5000), margin = 700;
const BLOCK = ['*googletagmanager.com/*', '*google-analytics.com/*', '*doubleclick.net/*', '*connect.facebook.net/*', '*facebook.com/tr*'];
const HAS = `!!document.querySelector('script[src*="googletagmanager.com/gtm.js"]')`;
const bust = (u, q) => u + (u.includes('?') ? '&' : '?') + q;

const tab = await openTab({host: o.host || new URL(o.url).host, resolve: o.resolve, cookie: o.cookie});
await tab.send('Network.enable');
await tab.send('Network.setBlockedURLs', {urls: BLOCK});
await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
await tab.send('Emulation.setDeviceMetricsOverride', o.mobile ? {width: 412, height: 823, deviceScaleFactor: 1.75, mobile: true} : {width: 1350, height: 940, deviceScaleFactor: 1, mobile: false});
await tab.send('Emulation.setUserAgentOverride', {userAgent: o.mobile ? MUA : DUA});

async function open(url) {
  await tab.send('Page.navigate', {url});
  for (let i = 0; i < 300; i++) {
    await sleep(100);
    if (await tab.evalv(`document.readyState==='complete' && performance.getEntriesByType('navigation')[0].loadEventEnd > 0`)) break;
  }
  return await tab.evalv(`performance.getEntriesByType('navigation')[0].loadEventEnd`);
}
async function until(ms) { while (await tab.evalv('performance.now()') < ms) await sleep(50); }

const res = [];
const check = (name, ok, info) => { res.push({name, ok, ...info}); console.log(`${ok ? 'ĐẠT ' : 'LỖI '} ${name} ${JSON.stringify(info)}`); };

// 1. Không thao tác: chưa nạp trước load + delay − margin, đã nạp sau load + delay + margin.
let L = await open(bust(o.url, 'gdc=idle' + Date.now()));
await until(L + delay - margin);
const early = await tab.evalv(HAS);
await until(L + delay + margin);
const late = await tab.evalv(HAS);
check('không thao tác', !early && late, {load_ms: Math.round(L), truoc_moc: early, sau_moc: late});

// 2. Có thao tác (phím Shift) ngay sau load: nạp ngay.
L = await open(bust(o.url, 'gdc=key' + Date.now()));
const before = await tab.evalv(HAS);
await tab.send('Input.dispatchKeyEvent', {type: 'rawKeyDown', key: 'Shift', code: 'ShiftLeft', windowsVirtualKeyCode: 16});
await tab.send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift', code: 'ShiftLeft', windowsVirtualKeyCode: 16});
await sleep(300);
const after = await tab.evalv(HAS);
check('có thao tác', !before && after, {truoc_phim: before, sau_phim: after});

// 3. URL có tham số quảng cáo: nạp ngay khi trang tải.
L = await open(bust(o.url, 'utm_source=gdc&gdc=' + Date.now()));
check('URL quảng cáo', await tab.evalv(HAS), {load_ms: Math.round(L)});

// 4. Trang chuyển đổi (nếu có): nạp ngay.
if (o['now-url']) {
  L = await open(bust(o['now-url'], 'gdc=' + Date.now()));
  check('trang chuyển đổi', await tab.evalv(HAS), {load_ms: Math.round(L)});
}

await tab.close();
const fail = res.filter(r => !r.ok).length;
console.log(fail ? `GTM_DELAY_CHECK lỗi=${fail}` : 'GTM_DELAY_CHECK đạt');
process.exit(fail ? 1 : 0);
