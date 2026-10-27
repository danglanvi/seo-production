#!/usr/bin/env node
// Chụp một vùng trang web thật làm ảnh minh hoạ: tìm khối chứa đoạn chữ, tô câu cần nhấn, chụp 2x.
//
//   node chup_trang.mjs --url <URL> --chua "<đoạn chữ có trong khối>" --out <file.png>
//        [--to "<câu cần tô vàng>"] [--rong 1000] [--khoi p|section|div|table|li] [--them 1] [--le 24] [--an "<selector, ...>"]
//
// --khoi: thẻ của khối cần chụp (mặc định khối nhỏ nhất chứa đoạn chữ). --them N: lấy thêm N khối liền sau.
// --an: ẩn phần tử che nội dung (banner cookie, thanh dính). In ra kích thước, URL, ngày chụp để ghi caption.
// Mã thoát: 0 đạt, 1 không thấy đoạn chữ, 2 sai tham số.
import {writeFileSync} from 'fs';
import {execFileSync} from 'child_process';
import {args, openTab, setViewport, loadUrl} from './_cdp.mjs';

const o = args(process.argv.slice(2));
if (!o.url || !o.chua || !o.out) { console.error('Cần --url, --chua, --out'); process.exit(2); }
const W = Number(o.rong || 1000), pad = Number(o.le || 24), more = Number(o.them || 0);
const TO_RE = o.to ? String(o.to).normalize('NFC').trim().split(/\s+/).map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s+') : '';

const FIND = `(() => {
  const want = ${JSON.stringify(String(o.chua))}.replace(/\\s+/g, ' ').trim().toLowerCase().normalize('NFC');
  for (const s of ${JSON.stringify(String(o.an || ''))}.split(',').map(x => x.trim()).filter(Boolean))
    document.querySelectorAll(s).forEach(e => e.style.setProperty('display', 'none', 'important'));
  document.querySelectorAll('header, nav, [class*=cookie], [id*=cookie], [class*=consent]').forEach(e => {
    const p = getComputedStyle(e).position; if (p === 'fixed' || p === 'sticky') e.style.setProperty('display', 'none', 'important'); });
  const tag = ${JSON.stringify(o.khoi || '')};
  let best = null;
  for (const e of document.querySelectorAll(tag || 'p, li, td, dd, dt, h1, h2, h3, h4, blockquote, pre, section, article, div, table')) {
    const t = (e.textContent || '').replace(/\\s+/g, ' ').toLowerCase().normalize('NFC');
    if (!t.includes(want)) continue;
    if (!best || (e.textContent || '').length < (best.textContent || '').length) best = e;
  }
  if (!best) return null;
  // mở khối thu gọn chứa đoạn chữ (details, khối expandable của devsite)
  for (let a = best; a; a = a.parentElement) {
    if (a.tagName === 'DETAILS') a.open = true;
    if (a.hidden) a.hidden = false;
    if (/expandable|collapsed/.test(a.className || '')) { a.classList.add('expanded'); a.classList.remove('collapsed'); }
  }
  const to = ${JSON.stringify(TO_RE)};
  if (to) {
    // so theo từ, bỏ qua xuống dòng và khoảng trắng thừa trong mã nguồn của trang
    const re = new RegExp(to);
    const w = document.createTreeWalker(best, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const v = n.nodeValue.normalize('NFC'), mm = v.match(re);
      if (!mm) continue;
      if (v !== n.nodeValue) n.nodeValue = v;
      const r = document.createRange(); r.setStart(n, mm.index); r.setEnd(n, mm.index + mm[0].length);
      const m = document.createElement('mark'); m.style.cssText = 'background:#FFE58A;color:inherit;padding:0 2px;border-radius:3px';
      r.surroundContents(m); break;
    }
  }
  // trang có khung cuộn riêng (sidebar cố định): mở khung để cả trang cuộn theo window, toạ độ chụp mới đúng
  for (let a = best.parentElement; a && a !== document.body; a = a.parentElement) {
    const cs = getComputedStyle(a);
    if (/(auto|scroll)/.test(cs.overflowY) && a.scrollHeight > a.clientHeight + 4)
      ['overflow', 'height', 'max-height'].forEach((k, i) => a.style.setProperty(k, ['visible', 'auto', 'none'][i], 'important'));
  }
  const els = [best]; let x = best;
  for (let k = 0; k < ${more}; k++) { x = x.nextElementSibling; if (!x) break; els.push(x); }
  els[0].scrollIntoView({block: 'center'});
  window.__chup = els;
  return true;
})()`;

const tab = await openTab();
try {
  await setViewport(tab, W);
  await tab.send('Emulation.setDeviceMetricsOverride', {width: W, height: 900, deviceScaleFactor: 2, mobile: false});
  await tab.send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-color-scheme', value: 'light'}]});
  await loadUrl(tab, o.url, 1500);
  if (!(await tab.evalv(FIND))) { console.error(`Không thấy đoạn "${o.chua}" trên ${o.url}`); process.exit(1); }
  await new Promise(r => setTimeout(r, 600));
  // Đo lại ngay trước khi chụp, theo toạ độ màn hình. Chụp cả màn hình rồi cắt bằng Pillow: clip của CDP lệch trên trang
  // có bố cục absolute hoặc khung cuộn riêng (ca thật 27/10/2026: hexdocs chụp ra cột field khác).
  const rect = await tab.evalv(`(() => { const rs = window.__chup.map(e => e.getBoundingClientRect());
    const l = Math.min(...rs.map(r => r.left)), t = Math.min(...rs.map(r => r.top)), rr = Math.max(...rs.map(r => r.right)), b = Math.max(...rs.map(r => r.bottom));
    return {x: Math.max(0, l - ${pad}), y: Math.max(0, t - 2), w: Math.min(innerWidth, rr + ${pad}) - Math.max(0, l - ${pad}), h: b - t + 3, vh: innerHeight}; })()`);
  let clip;
  if (rect.y + rect.h <= rect.vh) {
    const shot = await tab.send('Page.captureScreenshot', {format: 'png'});
    writeFileSync(o.out, Buffer.from(shot.result.data, 'base64'));
    execFileSync('python3', ['-c', `from PIL import Image;im=Image.open(${JSON.stringify(o.out)});im.crop((${2 * rect.x},${2 * rect.y},${2 * (rect.x + rect.w)},${2 * (rect.y + rect.h)})).save(${JSON.stringify(o.out)})`]);
    clip = {width: rect.w, height: rect.h};
  } else {
    const sy = await tab.evalv('scrollY');
    clip = {x: rect.x, y: rect.y + sy, width: rect.w, height: rect.h, scale: 1};
    const shot = await tab.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true, clip});
    writeFileSync(o.out, Buffer.from(shot.result.data, 'base64'));
  }
  const d = new Date();
  console.log(JSON.stringify({file: o.out, rong: Math.round(clip.width * 2), cao: Math.round(clip.height * 2), url: o.url,
    ngay_chup: `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`}));
} finally {
  await tab.close();
}
