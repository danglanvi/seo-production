// Trình điều khiển Chrome cho test_guest_tap.py. Không phải script của skill. Mở trang trên server giả 127.0.0.1, bấm phần tử bằng
// chuỗi sự kiện chuột thật của CDP, gọi window.__load() (giả lượt LiteSpeed nạp JS hoãn), rồi in số lần menu mở.
// node guesttap_driver.mjs --url URL --mode early|late|none|other
//   early: bấm nút trước khi JS nạp.  late: nạp JS rồi mới bấm.  none: không bấm.  other: bấm phần tử khác trước khi JS nạp.
import {args, openTab, sleep} from '../_chrome.mjs';

const o = args(process.argv.slice(2));
const tab = await openTab({host: '127.0.0.1'});
try {
  await tab.send('Page.navigate', {url: o.url});
  for (let i = 0; i < 100; i++) { await sleep(100); if (await tab.evalv(`document.readyState==='complete'`)) break; }
  const click = async id => {
    const r = JSON.parse(await tab.evalv(`JSON.stringify(document.getElementById('${id}').getBoundingClientRect())`));
    const x = r.x + r.width / 2, y = r.y + r.height / 2;
    await tab.send('Input.dispatchMouseEvent', {type: 'mousePressed', x, y, button: 'left', clickCount: 1, buttons: 1});
    await tab.send('Input.dispatchMouseEvent', {type: 'mouseReleased', x, y, button: 'left', clickCount: 1, buttons: 0});
  };
  if (o.mode === 'early') await click('z');
  if (o.mode === 'other') await click('d');
  await tab.evalv('window.__load()');
  if (o.mode === 'late') await click('z');
  await sleep(500);
  console.log(await tab.evalv('JSON.stringify({opened: window.__opened || 0})'));
} finally {
  await tab.close();
}
