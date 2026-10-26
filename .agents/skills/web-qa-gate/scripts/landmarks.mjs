// Đếm landmark trên DOM đã render, cho hạng mục 14 "Toàn vẹn bố cục" của web-qa-gate (14e).
// node landmarks.mjs --job job.json --out landmarks.jsonl [--page-timeout 120000]
// node landmarks.mjs --url https://stg.example.vn/ --out landmarks.jsonl [--widths 390,1366] [--menu "#menu-chinh"]
// node landmarks.mjs --help
// job.json: pages [{name,url}], widths, landmarks {menu_selector}, block, host, resolve, cookie, wait. Chỉ đọc. Chặn tracking từ đầu phiên.
// Mỗi dòng ra là một URL x một bề rộng. Lý do đo trên DOM đã render: plugin menu (ví dụ Max Mega Menu, widget_text) dựng menu bằng
// <div>, nên HTML server và DOM render có thể khác nhau về <nav>, <main>, <header>.
// Mã thoát: 0 đã ghi dữ liệu, 1 không mở được Chrome hoặc không ghi được dòng nào, 2 sai tham số.
import fs from 'node:fs'; import path from 'node:path';
import {args, openTab, sleep, setViewport, loadUrl, docResponse, withTimeout, sweepOrphans} from './_cdp.mjs';

const USAGE = `landmarks.mjs --job job.json --out landmarks.jsonl [--page-timeout ms]
landmarks.mjs --url <url> [--url <url> ...] --out landmarks.jsonl [--widths 390,1366] [--menu <selector>]
  --job            file job.json do qa_gate.py dựng (trang, bề rộng, menu_selector).
  --url            đo thẳng một URL (không cần job). Dùng cho lần thử nhanh.
  --widths         bề rộng, ngăn cách bằng dấu phẩy (mặc định 390,1366).
  --menu           selector của menu chính. Mặc định tìm trong header: nav, [role=navigation], .mega-menu-wrap, #site-navigation.
  --out            file jsonl ghi thêm vào cuối.
  --page-timeout   trần thời gian cho mỗi URL x bề rộng, mili giây (mặc định 120000).
  --help           in trợ giúp này.`;

const o = args(process.argv.slice(2), ['help']);
if (o.help) { console.log(USAGE); process.exit(0); }
if (!o.out || (!o.job && !o.url)) { console.error(USAGE); process.exit(2); }
let job = {};
if (o.job) { try { job = JSON.parse(fs.readFileSync(o.job, 'utf8')); } catch (e) { console.error('không đọc được job: ' + e.message); process.exit(2); } }
if (o.url) job.pages = [{name: 'url', url: o.url}];
const widths = (o.widths ? String(o.widths).split(',').map(Number) : null) || job.landmark_widths || [390, 1366];
const menuSel = o.menu || (job.landmarks && job.landmarks.menu_selector) || null;
const PAGE_TIMEOUT = +(o['page-timeout'] || job.page_timeout || 120000);

const LM = menuSelector => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const sel = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; const c = [...e.classList].slice(0, 2); if (c.length) s += '.' + c.join('.'); return s; };
  // Chuỗi tổ tiên là landmark hoặc vùng (main, header, footer, nav, aside, article, section) để biết phần tử nằm ở đâu.
  const within = e => { const a = []; for (let n = e.parentElement; n && n !== document.body; n = n.parentElement) if (/^(MAIN|HEADER|FOOTER|NAV|ASIDE|ARTICLE|SECTION|FORM)$/.test(n.tagName) || n.getAttribute('role')) a.unshift(n.tagName.toLowerCase() + (n.getAttribute('role') ? '[' + n.getAttribute('role') + ']' : '')); return a.join('>'); };
  const role = e => e.getAttribute('role') || '';
  const name = e => e.getAttribute('aria-label') || (e.getAttribute('aria-labelledby') ? (document.getElementById(e.getAttribute('aria-labelledby')) || {}).innerText || '' : '') || '';
  const mains = [...document.querySelectorAll('main,[role=main]')];
  const topLevel = (tag, r) => [...document.querySelectorAll(`${tag},[role=${r}]`)].filter(e => !e.closest('article,aside,main,nav,section,[role=main]') || (e.getAttribute('role') === r));
  const banners = topLevel('header', 'banner'), infos = topLevel('footer', 'contentinfo');
  const navs = [...document.querySelectorAll('nav,[role=navigation]')].filter(vis).map(e => ({sel: sel(e), tag: e.tagName.toLowerCase(), role: role(e), label: name(e), links: e.querySelectorAll('a[href]').length, in: within(e)}));
  const h1s = [...document.querySelectorAll('h1')].filter(vis).map(h => ({in: within(h), text: (h.innerText || '').trim().slice(0, 60)}));
  let menu = null;
  const cands = menuSelector ? [menuSelector] : ['header nav', 'header [role=navigation]', '.mega-menu-wrap', '#site-navigation', '.main-navigation', '#masthead nav', '.elementor-location-header nav'];
  for (const s of cands) {
    let e = null; try { e = document.querySelector(s); } catch {}
    if (e) { menu = {sel: sel(e), tag: e.tagName.toLowerCase(), role: role(e), inNav: !!e.closest('nav,[role=navigation]'), in: within(e), links: e.querySelectorAll('a[href]').length, declared: !!menuSelector, widgetText: !!e.closest('.widget_text,.textwidget')}; break; }
  }
  const skip = [...document.querySelectorAll('a[href^="#"]')].slice(0, 6).some(a => /skip|bỏ qua|nội dung chính|main/i.test((a.innerText || '') + a.className + a.getAttribute('href')));
  return {main: mains.length, mainSel: mains.map(sel).slice(0, 3), banner: banners.length, contentinfo: infos.length, navs: navs.slice(0, 10), h1: h1s, menu, skip,
    footerLists: document.querySelectorAll('footer ul').length};
};

fs.mkdirSync(path.dirname(path.resolve(o.out)), {recursive: true});
const out = fs.createWriteStream(o.out, {flags: 'a'});
let tab = null, written = 0;
async function openSession() {
  if (tab) { try { await tab.close(); } catch {} }
  tab = await openTab({host: job.host, resolve: job.resolve, cookie: job.cookie, block: job.block || []});
  await tab.send('Page.enable'); await tab.send('Runtime.enable');
}
try { sweepOrphans({apply: true}); await openSession(); } catch (e) { console.error('không mở được Chrome: ' + e.message); process.exit(1); }
for (const pg of job.pages || []) for (const W of widths) {
  const row = {name: pg.name, url: pg.url, vw: W};
  try {
    await withTimeout((async () => {
      await setViewport(tab, W);
      await loadUrl(tab, pg.url, +(job.wait || 2500));
      Object.assign(row, docResponse(tab));
      row.landmarks = await tab.evalv(`(${LM})(${JSON.stringify(menuSel)})`);
      if (!row.landmarks) row.err = 'phép đo không trả kết quả';
    })(), PAGE_TIMEOUT);
  } catch (e) { row.err = String(e.message || e).slice(0, 160); if (e.message === 'timeout') { try { await openSession(); } catch {} } }
  out.write(JSON.stringify(row) + '\n'); written++;
  process.stderr.write(`${pg.name} ${W} ${row.err ? 'ERR ' + row.err : 'main=' + row.landmarks.main + ' nav=' + row.landmarks.navs.length + ' h1=' + row.landmarks.h1.length}\n`);
}
out.end(); await tab.close();
if (!written) { console.error('không có URL để đo'); process.exit(1); }
process.exit(0);
