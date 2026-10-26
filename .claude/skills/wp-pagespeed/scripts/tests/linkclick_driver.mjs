// Trình điều khiển Chrome cho test_gtm_linkclick.py. Không phải script của skill. Mở một trang trên server giả 127.0.0.1, bấm một phần tử bằng
// chuỗi sự kiện chuột thật của CDP, rồi in JSON gồm các event gtm.linkClick trong dataLayer.
// node linkclick_driver.mjs --url URL --mode early|late|none|div [--target z]
//   early: nhấn và nhả ngay, click đến trước khi gtm.js (server giả trễ 600 ms) chạy.  late: nhấn, chờ gtm.js chạy xong, rồi nhả.
//   none: không thao tác.  div: như early nhưng bấm vào phần tử không phải link (id d).
import {args, openTab, sleep} from '../_chrome.mjs';

const o = args(process.argv.slice(2));
const tab = await openTab({host: '127.0.0.1'});
try {
  await tab.send('Network.enable');
  await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
  await tab.send('Page.navigate', {url: o.url});
  for (let i = 0; i < 100; i++) { await sleep(100); if (await tab.evalv(`document.readyState==='complete'`)) break; }
  const id = o.mode === 'div' ? 'd' : 'z';
  const r = JSON.parse(await tab.evalv(`JSON.stringify(document.getElementById('${id}').getBoundingClientRect())`));
  const x = r.x + r.width / 2, y = r.y + r.height / 2;
  const mouse = (type, extra = {}) => tab.send('Input.dispatchMouseEvent', {type, x, y, button: 'left', clickCount: 1, ...extra});
  if (o.mode !== 'none') {
    await mouse('mousePressed', {buttons: 1});
    if (o.mode === 'late') await sleep(1600);
    await mouse('mouseReleased', {buttons: 0});
  }
  await sleep(o.mode === 'none' ? 1200 : 1600);
  console.log(await tab.evalv(`JSON.stringify({
    gtmExec: !!window.__gtmExec,
    first: (window.dataLayer || [])[0] ? window.dataLayer[0].event : null,
    clicks: (window.dataLayer || []).filter(e => e.event === 'gtm.linkClick').map(e => ({native: !!e.native, url: e['gtm.elementUrl'], id: e['gtm.elementId'],
      cls: e['gtm.elementClasses'], target: e['gtm.elementTarget'], isEl: !!(e['gtm.element'] && e['gtm.element'].nodeType === 1)})),
  })`));
} finally {
  await tab.close();
}
