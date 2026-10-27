// ccss_gap.mjs (wp-ucss): tìm phần tử có hộp khác nhau giữa "chỉ critical CSS" và "critical CSS + CSS gọn", trong 1,5 màn hình đầu.
// node ccss_gap.mjs --site <site.json> <file HTML có critical CSS inline + link CSS gọn nạp không chặn> <m|d|p|q> [file CSS vá thêm]
// Mở HTML local (không gọi production cho document). CSS, font, svg lấy từ cache local hoặc qua hàng đợi của lib-ucss.
// Bản "chỉ critical" chặn file trong ucss_dir và combined_css_path. File thứ 3 (tuỳ chọn) chèn vào cuối <style id="<ccss_style_id>">.
// Phần tử trong menu thả xuống đang ẩn (selector ở states.submenu, mặc định Max Mega Menu) bị bỏ, trừ khi đặt IN_MENU=1.
// Site mẫu 26/10/2026: thiếu quy tắc .screen-reader-text làm link "skip to content" hiện rồi ẩn, CLS 0,026–0,028.
import fs from 'fs';
import { site, args, launch, asset } from './lib-ucss.mjs';

const S = site();
const [file, dev, extraFile] = args();
if (!file || !S.ua[dev]) { console.error('dùng: node ccss_gap.mjs --site <site.json> <file.html> <m|d|p|q> [vá.css]'); process.exit(2); }
const styleId = S.ccss_style_id || 'ucss-ccss';
const sub = S.states.submenu || '.mega-sub-menu, .mega-menu-column';
const ucssDir = '/' + (S.ucss_dir || 'wp-content/ucss').replace(/^\/|\/$/g, '') + '/';
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const blockRe = new RegExp(esc(ucssDir) + '|' + esc(S.combined_css_path));
let html = fs.readFileSync(file, 'utf8');
if (extraFile) {
  const re = new RegExp(`(<style id="${esc(styleId)}">[\\s\\S]*?)(<\\/style>)`);
  if (!re.test(html)) { console.error(`không thấy <style id="${styleId}"> trong HTML`); process.exit(2); }
  html = html.replace(re, (m, a, b) => a + fs.readFileSync(extraFile, 'utf8') + b);
}
const AB = `https://${S.host}/__ccss_gap__/`;
const browser = await launch();
async function render(onlyCcss) {
  const ctx = await browser.createBrowserContext(); const p = await ctx.newPage();
  await p.setUserAgent(S.ua[dev]); await p.setViewport(S.viewport[dev]); await p.setRequestInterception(true);
  p.on('request', async q => {
    const u = q.url();
    try {
      if (u === AB) return q.respond({ status: 200, contentType: 'text/html; charset=utf-8', body: html });
      const h = new URL(u).hostname;
      if (/\.(css|woff2?|ttf|otf|svg)(\?|$)/i.test(u) && (h === S.host || S.asset_hosts.includes(h))) {
        if (onlyCcss && h === S.host && blockRe.test(new URL(u).pathname)) return q.abort();
        const v = await asset(u); return q.respond({ status: v.status, contentType: v.type, body: v.body });
      }
      return q.abort();
    } catch (e) { q.abort().catch(() => {}); }
  });
  await p.evaluateOnNewDocument((inMenu, sub) => { window.__inMenu = inMenu; window.__sub = sub; }, !!process.env.IN_MENU, sub);
  await p.goto(AB, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => {
    const out = {}; let i = 0;
    for (const el of document.querySelectorAll('body *')) {
      i++; const b = el.getBoundingClientRect(); if (b.top > innerHeight * 1.5) continue;
      if (!window.__inMenu && el.closest(window.__sub)) continue;
      out[i] = [el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].slice(0, 3).join('.') : ''), Math.round(b.top), Math.round(b.height), Math.round(b.left), Math.round(b.width), getComputedStyle(el).display];
    }
    return out;
  });
  await ctx.close(); return r;
}
const A = await render(true), B = await render(false);
let n = 0;
for (const k of Object.keys(B)) {
  const a = A[k], b = B[k]; if (!a) continue;
  if (a[1] !== b[1] || a[2] !== b[2] || a[5] !== b[5]) {
    if (n++ < 25) console.log(b[0].padEnd(60), `chỉ critical top=${a[1]} h=${a[2]} ${a[5]}`, '|', `đủ CSS top=${b[1]} h=${b[2]} ${b[5]}`);
  }
}
console.log('phần tử khác hộp trong 1,5 màn hình:', n);
await browser.close();
process.exit(n ? 1 : 0);
