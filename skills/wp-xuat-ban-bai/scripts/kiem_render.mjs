#!/usr/bin/env node
// Kiểm bài hiển thị trên giao diện thật của site, ở 1366 px và 390 px.
//
//   node kiem_render.mjs <bai.html> --profile <web-profile.json> --out <thư mục>   trước khi đăng: ghép bài vào khung bài mẫu
//   node kiem_render.mjs --url <URL bài> --profile <web-profile.json> --out <thư mục>  sau khi đăng
//
// Trước khi đăng: mở render.bai_mau của profile, thay vùng render.khung_noi_dung bằng thân bài bọc .doc-kit, nạp
// doc-kit.css và doc-kit.js của site, đổi ảnh cục bộ thành data URI. Ra: render.json, desktop.png, mobile.png.
// Mã thoát: 0 đạt, 1 có lỗi (tràn ngang, ảnh hỏng, lỗi JS, khối bấm không chạy, chữ sơ đồ quá nhỏ trên mobile), 2 sai input.
import {readFileSync, writeFileSync, mkdirSync, existsSync} from 'fs';
import {dirname, resolve, extname, join} from 'path';
import {args, openTab, setViewport, loadUrl, shot, jsErrors, sleep} from './_cdp.mjs';

const o = args(process.argv.slice(2));
if (!o.profile || !o.out || (!o.url && !o._[0])) { console.error('Cần <bai.html> hoặc --url, cùng --profile và --out'); process.exit(2); }
const prof = JSON.parse(readFileSync(o.profile, 'utf8'));
const r = prof.render || {};
const site = (prof.url || '').replace(/\/$/, '');
mkdirSync(o.out, {recursive: true});
const MIN_SVG_PX = Number(o['min-svg-px'] || 11);

const MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.mp4': 'video/mp4'};
function article(file) {
  const src = readFileSync(file, 'utf8'), base = dirname(resolve(file));
  const h1 = (src.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) || [])[1] || '';
  let body = (src.match(/<main[^>]*>([\s\S]*)<\/main>/) || [null, src])[1];
  body = body.replace(/<header class="hd">[\s\S]*?<\/header>/, '').replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '');
  body = body.replace(/(src|poster)="([^"]+)"/g, (m, a, u) => {
    if (/^(https?:|data:|\/\/|#)/.test(u)) return m;
    const p = resolve(base, decodeURIComponent(u));
    if (!existsSync(p)) return m;
    return `${a}="data:${MIME[extname(p).toLowerCase()] || 'application/octet-stream'};base64,${readFileSync(p).toString('base64')}"`;
  });
  const head = src.split('<body')[0];
  const css = [...head.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map(m => m[1]).filter(s => !s.includes(':root{--bg:#FAF9F5')).join('\n');
  return {h1: h1.replace(/<[^>]+>/g, '').trim(), body, css};
}

const INJECT = (a, sel) => `(async () => {
  const box = document.querySelector(${JSON.stringify(sel)});
  if (!box) return 'không thấy vùng nội dung ' + ${JSON.stringify(sel)};
  box.innerHTML = '<div class="doc-kit" data-doc>' + ${JSON.stringify(a.body)} + '</div>';
  const h1 = document.querySelector('h1'); if (h1) h1.textContent = ${JSON.stringify(a.h1)};
  const load = (tag, attrs) => new Promise(res => { const e = document.createElement(tag); Object.assign(e, attrs); e.onload = e.onerror = res; document.head.appendChild(e); });
  if (!document.querySelector('link[href*="doc-kit.css"]')) await load('link', {rel: 'stylesheet', href: ${JSON.stringify(site + '/wp-content/doc-kit/doc-kit.css')}});
  if (${JSON.stringify(a.css)}.trim()) { const s = document.createElement('style'); s.textContent = '.doc-kit{' + ${JSON.stringify(a.css)} + '}'; document.head.appendChild(s); }
  await load('script', {src: ${JSON.stringify(site + '/wp-content/doc-kit/doc-kit.js')}});
  return 'ok';
})()`;

const MEASURE = sel => `(async () => {
  const W = innerWidth, box = document.querySelector(${JSON.stringify(sel)}) || document.body;
  for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); }
  scrollTo(0, 0); await new Promise(r => setTimeout(r, 400));
  const name = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).slice(0, 2).join('.') : '');
  const tran = [];
  for (const e of box.querySelectorAll('*')) {
    const rc = e.getBoundingClientRect();
    if (rc.width && rc.right > W + 1 && !e.closest('.tbl, pre, .bcmd.multi')) tran.push(name(e) + ' phải=' + Math.round(rc.right));
    if (tran.length > 12) break;
  }
  const anh_hong = [...box.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth === 0).map(i => (i.getAttribute('src') || '').slice(0, 90));
  const svg_nho = [];
  for (const s of box.querySelectorAll('svg')) {
    const vb = s.viewBox && s.viewBox.baseVal, cw = s.getBoundingClientRect().width;
    if (!vb || !vb.width || !cw || s.closest('[hidden]') || getComputedStyle(s).display === 'none' || s.closest('button')) continue;
    for (const t of s.querySelectorAll('text')) {
      const fs = parseFloat(getComputedStyle(t).fontSize) * cw / vb.width;
      if (fs < ${MIN_SVG_PX}) { svg_nho.push((s.closest('figure')?.dataset.img || 'svg') + ': "' + t.textContent.trim().slice(0, 40) + '" ' + fs.toFixed(1) + 'px'); break; }
    }
  }
  const bam = {tab: 0, tab_loi: 0, quiz: 0, quiz_loi: 0, chk: 0, chk_loi: 0, calc: 0, calc_loi: 0};
  for (const g of box.querySelectorAll('.btabs, .tabs')) {
    const bs = g.querySelectorAll('.btab-bar button, [role=tab]');
    if (bs.length < 2) continue;
    bam.tab++; bs[1].click(); await new Promise(r => setTimeout(r, 60));
    const panes = [...g.querySelectorAll('.btab-pane, [role=tabpanel]')];
    if (panes.length > 1 && (panes[1].hidden || getComputedStyle(panes[1]).display === 'none')) bam.tab_loi++;
    bs[0].click();
  }
  for (const q of box.querySelectorAll('.bquiz .qz, [data-quiz]')) {
    const b = q.querySelector('button[data-ok]') || q.querySelector('button');
    if (!b) continue;
    bam.quiz++; b.click(); await new Promise(r => setTimeout(r, 60));
    const fb = q.querySelector('.fb, .res, [data-ans]');
    if (fb && (fb.hidden || getComputedStyle(fb).display === 'none')) bam.quiz_loi++;
  }
  for (const c of box.querySelectorAll('.bchk, .chk')) {
    const i = c.querySelector('input[type=checkbox]');
    if (!i) continue;
    bam.chk++; const before = (c.querySelector('.bchk-n') || {}).textContent; i.click(); await new Promise(r => setTimeout(r, 60));
    const after = (c.querySelector('.bchk-n') || {}).textContent;
    if (c.querySelector('.bchk-n') && before === after) bam.chk_loi++;
    i.click();
  }
  for (const c of box.querySelectorAll('.calc')) {
    const i = c.querySelector('input[type=range]'), out = c.querySelector('[data-f]');
    if (!i || !out) continue;
    bam.calc++; const before = out.textContent; i.value = i.max; i.dispatchEvent(new Event('input', {bubbles: true}));
    await new Promise(r => setTimeout(r, 60));
    if (out.textContent === before) bam.calc_loi++;
  }
  return {rong: W, scroll_w: document.documentElement.scrollWidth, tran, anh_hong, svg_nho, bam,
    doc_kit: !!document.querySelector('.doc-kit'), css_doc_kit: !!document.querySelector('link[href*="doc-kit.css"]'),
    js_doc_kit: !!document.querySelector('script[src*="doc-kit.js"]'), h1: document.querySelectorAll('h1').length};
})()`;

const tab = await openTab();
const report = {nguon: o.url || o._[0], che_do: o.url ? 'sau-dang' : 'truoc-dang', khung: r.khung_noi_dung, ket_qua: {}};
let loi = 0;
try {
  const a = o.url ? null : article(o._[0]);
  for (const [ten, W] of [['desktop', 1366], ['mobile', 390]]) {
    await setViewport(tab, W);
    await loadUrl(tab, o.url || r.bai_mau);
    if (a) {
      const ok = await tab.evalv(INJECT(a, r.khung_noi_dung), true);
      if (ok !== 'ok') { console.error(ok); process.exit(2); }
      await sleep(900);
    }
    const m = await tab.evalv(MEASURE(r.khung_noi_dung || 'body'), true);
    // Lỗi từ doc-kit.js là lỗi của bài. Lỗi script khác của site (plugin mục lục bám heading cũ khi ghép bài) chỉ ghi cảnh báo.
    const errs = jsErrors(tab).filter(e => !/gtag|fbq|clarity|zalo/i.test(e.msg));
    m.loi_js = [...new Set(errs.filter(e => /doc-kit/.test(e.url) || !e.url).map(e => e.msg))];
    m.canh_bao_js = [...new Set(errs.filter(e => e.url && !/doc-kit/.test(e.url)).map(e => e.msg + ' @ ' + e.url.split('/').pop()))];
    m.tran_ngang = m.scroll_w > m.rong + 1;
    await shot(tab, join(o.out, `${ten}.png`));
    const fails = [];
    if (m.tran_ngang || m.tran.length) fails.push('tràn ngang');
    if (m.anh_hong.length) fails.push('ảnh hỏng');
    if (m.loi_js.length) fails.push('lỗi JS');
    if (m.bam.tab_loi || m.bam.quiz_loi || m.bam.chk_loi || m.bam.calc_loi) fails.push('khối bấm không chạy');
    if (ten === 'mobile' && m.svg_nho.length) fails.push('chữ sơ đồ nhỏ');
    if (o.url && !(m.doc_kit && m.css_doc_kit && m.js_doc_kit)) fails.push('thiếu doc-kit');
    m.loi = fails; loi += fails.length;
    report.ket_qua[ten] = m;
    console.log(`${ten} ${W}px: ${fails.length ? 'LOI ' + fails.join(', ') : 'ok'} · khối bấm ${JSON.stringify(m.bam)}${m.svg_nho.length ? ' · svg nhỏ: ' + m.svg_nho.join(' | ') : ''}`);
    if (m.tran.length) console.log('  tràn: ' + m.tran.join(' · '));
    if (m.loi_js.length) console.log('  JS: ' + m.loi_js.slice(0, 3).join(' · '));
    if (m.canh_bao_js.length) console.log('  cảnh báo JS của site: ' + m.canh_bao_js.slice(0, 2).join(' · '));
  }
} finally {
  await tab.close();
}
writeFileSync(join(o.out, 'render.json'), JSON.stringify(report, null, 1));
console.log(`ảnh: ${join(o.out, 'desktop.png')} · ${join(o.out, 'mobile.png')}`);
process.exit(loi ? 1 : 0);
