// Đo tương tác và bố cục cho web-qa-gate (hạng mục 13 "Tương tác và trạng thái", hạng mục 14 "Toàn vẹn bố cục").
// node interact_probe.mjs --job job.json --out interact.jsonl [--only menu,slider,states,buttons,layout,pairs] [--page-timeout 120000]
// node interact_probe.mjs --help
// job.json do qa_gate.py dựng: pages [{name,url}], interact {menu_toggle, sliders, changed_selectors, kit_button_colors, grids,
//   count_claims, cta_selectors, pairs, widths}, block, host, resolve, cookie, wait, shots_dir, page_timeout.
// Script chỉ đọc và bấm nút giao diện (menu, mũi tên slider). Không điền form, không gửi gì. Tracking bị chặn từ đầu phiên.
// Mọi lượt đo dùng viewport thật (không bật cờ mobile của CDP), UA Chrome thường, và tải lại trang ở từng bề rộng.
// Mỗi dòng ra là một URL x một bề rộng. Phép đo nào lỗi ghi vào trường err của dòng, không làm dừng cả lượt quét.
// Mã thoát: 0 đã ghi dữ liệu, 1 không mở được Chrome hoặc không ghi được dòng nào, 2 sai tham số.
import fs from 'node:fs'; import path from 'node:path';
import {args, openTab, sleep, setViewport, loadUrl, docResponse, tap, withTimeout, sweepOrphans} from './_cdp.mjs';

const USAGE = `interact_probe.mjs --job job.json --out interact.jsonl [--only menu,slider,states,buttons,layout,pairs] [--page-timeout ms]
  --job            file job.json (qa_gate.py tự dựng khi chạy run; khối "interact" lấy từ qa.json)
  --out            file jsonl ghi thêm vào cuối. Mỗi dòng: một URL x một bề rộng.
  --only           chỉ chạy một số nhóm đo. Mặc định: mọi nhóm có khai báo trong job.
  --page-timeout   trần thời gian cho mỗi URL x bề rộng, mili giây (mặc định 120000). Hết giờ thì ghi err và mở lại Chrome.
  --help           in trợ giúp này.
Nhóm đo: menu (13a), slider (13b), states (13c), buttons (13d), layout (14a-c: lưới, số trong heading, CTA trùng link), pairs (14d: cặp VI/EN).
Mặc định bề rộng: menu 390; slider 360 và 390; states 1366; buttons 390 và 1366; layout 390 và 1366; pairs 1366.`;

const o = args(process.argv.slice(2), ['help']);
if (o.help) { console.log(USAGE); process.exit(0); }
if (!o.job || !o.out) { console.error(USAGE); process.exit(2); }
let job;
try { job = JSON.parse(fs.readFileSync(o.job, 'utf8')); } catch (e) { console.error('không đọc được job: ' + e.message); process.exit(2); }
const I = job.interact || {};
const only = o.only ? new Set(String(o.only).split(',')) : null;
const on = k => !only || only.has(k);
const PAGE_TIMEOUT = +(o['page-timeout'] || job.page_timeout || 120000);
const wait = +(job.wait || 2500);

// ---- Cấu hình theo nhóm đo ----
const menuCfg = I.menu_toggle === undefined || I.menu_toggle === false ? null : (I.menu_toggle === true ? {} : I.menu_toggle);
const sliders = I.sliders || [];
const states = I.changed_selectors || [];
const kit = I.kit_button_colors || null;
const layoutOn = !!(I.grids || I.count_claims || I.cta_selectors || I.layout);
const pairs = I.pairs || [];
const W_MENU = (menuCfg && menuCfg.widths) || [390];
const W_STATES = I.states_widths || [1366];
const W_BUTTONS = (kit && kit.widths) || [390, 1366];
const W_LAYOUT = (I.layout_widths) || (I.grids && I.grids.widths) || [390, 1366];
const W_PAIRS = I.pairs_widths || [1366];
const sliderWidths = s => s.widths || [360, 390];

// ---- Hàm chạy trong trang. Viết thật bằng JS, nạp qua toString() để không phải escape chuỗi. ----
const LIB = () => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const sel = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; const c = [...e.classList].filter(x => !/^elementor-(element|widget)-[0-9a-f]+$/.test(x)).slice(0, 2); if (c.length) s += '.' + c.join('.'); return s; };
  const transp = c => !c || c === 'transparent' || /^rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0(\.0+)?\s*\)$/.test(c);
  const bgEff = e => { for (let x = e; x; x = x.parentElement) { const c = getComputedStyle(x).backgroundColor; if (!transp(c)) return c; } return 'rgb(255, 255, 255)'; };
  const visibleLinks = () => [...document.querySelectorAll('a[href]')].filter(a => { if (!vis(a)) return false; const r = a.getBoundingClientRect(); return r.right > 0 && r.left < innerWidth && r.bottom > 0; }).length;
  window.__wqg = {vis, sel, transp, bgEff, visibleLinks};
  return true;
};

const MENU_FIND = cfg => {
  const W = window.__wqg;
  const sels = cfg.selector ? [cfg.selector] : ['button[aria-controls]', '[aria-expanded]', '.mega-menu-toggle', '.menu-toggle', '.navbar-toggler', 'button[class*="burger" i]', 'button[class*="hamburger" i]'];
  const region = 'header,nav,[role=banner],[role=navigation],#masthead,.site-header,.mega-menu-wrap,.elementor-location-header';
  let found = null, hidden = null;
  for (const s of sels) {
    let list = []; try { list = [...document.querySelectorAll(s)]; } catch { continue; }
    for (const e of list) {
      if (!cfg.selector && !e.closest(region)) continue;
      if (W.vis(e) && e.getBoundingClientRect().top < 400) { found = e; break; }
      if (!hidden) hidden = e;
    }
    if (found) break;
  }
  if (!found) return {found: false, declared: !!cfg.selector, existsHidden: !!hidden, hiddenSel: hidden ? W.sel(hidden) : null};
  const ink = [], bg = W.bgEff(found);
  const hex = c => c;
  const consider = (el, pseudo, own) => {
    const s = getComputedStyle(el, pseudo || null);
    if (pseudo) {
      const c = s.content;
      if (c === 'none' || c === 'normal') return;
      if (c !== '""' && c !== "''" && !W.transp(s.color)) ink.push({kind: 'glyph', on: W.sel(el) + pseudo, color: hex(s.color)});
    }
    const r = el.getBoundingClientRect();
    const sized = pseudo ? (parseFloat(s.width) > 0 && parseFloat(s.height) > 0) || s.display === 'block' || s.position === 'absolute' : r.width > 0 && r.height > 0;
    if (!own && sized && !W.transp(s.backgroundColor)) ink.push({kind: 'bg', on: W.sel(el) + (pseudo || ''), color: s.backgroundColor});
    if (pseudo && own && !W.transp(s.backgroundColor)) ink.push({kind: 'bg', on: W.sel(el) + pseudo, color: s.backgroundColor});
    if (!own) for (const side of ['Top', 'Bottom']) {
      if (parseFloat(s['border' + side + 'Width']) > 0 && s['border' + side + 'Style'] !== 'none' && !W.transp(s['border' + side + 'Color']) && sized) ink.push({kind: 'border', on: W.sel(el) + (pseudo || ''), color: s['border' + side + 'Color']});
    }
    if (!pseudo && el instanceof SVGElement) {
      if (s.fill && s.fill !== 'none' && !W.transp(s.fill)) ink.push({kind: 'svg-fill', on: W.sel(el), color: s.fill});
      if (s.stroke && s.stroke !== 'none' && parseFloat(s.strokeWidth) > 0 && !W.transp(s.stroke)) ink.push({kind: 'svg-stroke', on: W.sel(el), color: s.stroke});
    }
  };
  consider(found, '::before', true); consider(found, '::after', true);
  const text = (found.innerText || '').trim();
  const fs0 = getComputedStyle(found);
  if (text && !W.transp(fs0.color)) ink.push({kind: 'text', on: W.sel(found), color: fs0.color});
  for (const d of [...found.querySelectorAll('*')].slice(0, 60)) {
    if (!(d instanceof SVGElement) && !W.vis(d)) continue;
    consider(d, null, false); consider(d, '::before', false); consider(d, '::after', false);
  }
  window.__wqgMenu = found;
  const r = found.getBoundingClientRect();
  return {found: true, sel: W.sel(found), x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), w: Math.round(r.width), h: Math.round(r.height),
    bg, ink: ink.slice(0, 12), text: text.slice(0, 30), links: W.visibleLinks(), expanded: found.getAttribute('aria-expanded')};
};
const MENU_AFTER = () => ({links: window.__wqg.visibleLinks(), expanded: window.__wqgMenu ? window.__wqgMenu.getAttribute('aria-expanded') : null});

const SLIDER_FIND = async cfg => {
  const W = window.__wqg, nap = ms => new Promise(r => setTimeout(r, ms));
  const box = document.querySelector(cfg.selector);
  if (!box) return {found: false};
  box.scrollIntoView({block: 'center'}); await nap(500);
  const nexts = cfg.next ? [cfg.next] : ['.slick-next', '.swiper-button-next', '.owl-next', '.splide__arrow--next', 'button[aria-label*="next" i]', 'button[aria-label*="tiếp" i]', 'button[aria-label*="sau" i]'];
  let btn = null;
  for (let scope = box, up = 0; scope && up < 4 && !btn; scope = scope.parentElement, up++) {
    for (const s of nexts) { const e = [...scope.querySelectorAll(s)].find(W.vis); if (e) { btn = e; break; } }
  }
  const itemsSel = cfg.items || '.slick-slide, .swiper-slide, .owl-item, .splide__slide, li';
  const items = [...box.querySelectorAll(itemsSel)];
  const vk = () => items.map((e, i) => ({e, i})).filter(({e}) => {
    const r = e.getBoundingClientRect(); if (!(r.width > 0 && r.height > 0)) return false;
    const s = getComputedStyle(e); if (s.visibility === 'hidden' || s.display === 'none') return false;
    const ov = Math.min(r.right, innerWidth) - Math.max(r.left, 0);
    return ov >= r.width * 0.5 && r.bottom > 0 && r.top < innerHeight;
  }).map(x => x.i);
  if (!btn) return {found: true, btn: false, items: items.length, before: vk()};
  btn.scrollIntoView({block: 'center'}); await nap(400);
  const r = btn.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  const pts = {center: [cx, cy], left: [r.left + 2, cy], right: [r.right - 2, cy], top: [cx, r.top + 2], bottom: [cx, r.bottom - 2]};
  const hits = {}, covered = [];
  for (const k in pts) {
    const el = document.elementFromPoint(pts[k][0], pts[k][1]);
    hits[k] = !!el && (el === btn || btn.contains(el));
    if (!hits[k]) covered.push(k + ' bị ' + (el ? W.sel(el) : 'ngoài màn hình') + ' che');
  }
  window.__wqgS = {vk, btn};
  const disabled = btn.disabled || btn.getAttribute('aria-disabled') === 'true' || /disabled/.test(btn.className);
  return {found: true, btn: true, btnSel: W.sel(btn), x: Math.round(cx), y: Math.round(cy), w: Math.round(r.width), h: Math.round(r.height), items: items.length, before: vk(), disabled, hits, covered};
};
const SLIDER_AFTER = () => ({after: window.__wqgS.vk()});

// Phần tử trong ngữ cảnh DOM: chọn selector, nền thực (đi lên tổ tiên khi nền trong suốt), cỡ chữ. Màu theo trạng thái đọc bằng CDP.
const STATE_EXTRA = function () {
  const W = window.__wqg, s = getComputedStyle(this);
  return {bg: W.bgEff(this), fs: parseFloat(s.fontSize), fw: parseInt(s.fontWeight, 10) || 400, sel: W.sel(this), text: (this.innerText || '').trim().slice(0, 30)};
};
const STATE_PROPS = ['color', 'background-color', 'background-image', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color', 'outline-style', 'outline-width', 'outline-color', 'box-shadow', 'text-decoration-line', 'transform', 'opacity', 'filter'];
const isTransp = c => !c || c === 'transparent' || /^rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0(\.0+)?\s*\)$/.test(c);

const BUTTONS = cfg => {
  const W = window.__wqg;
  const sels = (cfg.selectors && cfg.selectors.length) ? cfg.selectors : ['a.elementor-button', '.elementor-button', 'button.button', 'a.btn', '.btn', 'a.button'];
  const seen = new Set(), out = [];
  for (const s of sels) {
    let list = []; try { list = [...document.querySelectorAll(s)]; } catch { continue; }
    for (const e of list) {
      if (seen.has(e) || !W.vis(e) || out.length >= 80) continue;
      seen.add(e);
      const c = getComputedStyle(e);
      out.push({sel: W.sel(e), text: (e.innerText || '').trim().slice(0, 30), bg: c.backgroundColor, color: c.color, border: c.borderTopColor, borderW: parseFloat(c.borderTopWidth) || 0, bgImage: c.backgroundImage !== 'none'});
    }
  }
  return out;
};

// Phần tử bấm được nhưng không phải CTA (accordion, tab, mũi tên slider, nút đóng). Rule nút của kit Elementor có thể tô cả các phần tử này.
const NON_CTA = cfg => {
  const W = window.__wqg;
  const cta = (cfg.selectors && cfg.selectors.length) ? cfg.selectors : ['a.elementor-button', '.elementor-button', 'button.button', 'a.btn', '.btn', 'a.button'];
  const sels = (cfg.non_cta && cfg.non_cta.length) ? cfg.non_cta : ['button', '[role="button"]', '.slick-arrow', '.swiper-button-next', '.swiper-button-prev', '.elementor-tab-title', '.elementor-accordion-title', 'summary'];
  const isCta = e => cta.some(s => { try { return e.matches(s) || !!e.closest(s); } catch { return false; } });
  const seen = new Set(), out = [];
  for (const s of sels) {
    let list = []; try { list = [...document.querySelectorAll(s)]; } catch { continue; }
    for (const e of list) {
      if (seen.has(e) || !W.vis(e) || isCta(e) || out.length >= 80) continue;
      seen.add(e);
      const c = getComputedStyle(e);
      out.push({sel: W.sel(e), text: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 30), bg: c.backgroundColor, bgImage: c.backgroundImage !== 'none'});
    }
  }
  return out;
};

const LAYOUT = cfg => {
  const W = window.__wqg, res = {grids: [], claims: [], ctas: []};
  const kids = c => [...c.children].filter(e => { if (!W.vis(e)) return false; const p = getComputedStyle(e).position; return p !== 'absolute' && p !== 'fixed'; });
  let conts;
  if (cfg.grids && cfg.grids.selectors && cfg.grids.selectors.length) conts = cfg.grids.selectors.flatMap(s => { try { return [...document.querySelectorAll(s)]; } catch { return []; } });
  else conts = [...document.body.querySelectorAll('*')].filter(c => {
    if (c.closest('header,footer,nav') || !W.vis(c)) return false;
    const s = getComputedStyle(c);
    if (!(s.display === 'grid' || s.display === 'inline-grid' || ((s.display === 'flex') && s.flexWrap === 'wrap'))) return false;
    const k = kids(c); if (k.length < 3) return false;
    return k.every(e => { const r = e.getBoundingClientRect(); return r.width >= 80 && r.height >= 80; });
  });
  for (const c of conts.slice(0, 40)) {
    const k = kids(c); if (k.length < 2) continue;
    const rows = []; for (const e of k) { const t = Math.round(e.getBoundingClientRect().top / 4); let r = rows.find(x => Math.abs(x.t - t) <= 1); if (!r) rows.push(r = {t, n: 0}); r.n++; }
    rows.sort((a, b) => a.t - b.t);
    const counts = rows.map(r => r.n), cols = Math.max(...counts);
    const empty = k.filter(e => !(e.innerText || '').trim() && !e.querySelector('img,svg,video,iframe,picture,canvas,input,button,a[href]') && getComputedStyle(e).backgroundImage === 'none').length;
    res.grids.push({sel: W.sel(c), n: k.length, cols, rows: counts.slice(0, 12), empty});
  }
  for (const cl of cfg.count_claims || []) {
    const h = document.querySelector(cl.heading); if (!h) { res.claims.push({heading: cl.heading, missing: 'heading'}); continue; }
    const text = (h.innerText || '').trim(), m = text.match(new RegExp(cl.pattern || '\\d+'));
    const n = [...document.querySelectorAll(cl.cards)].filter(W.vis).length;
    res.claims.push({heading: cl.heading, text: text.slice(0, 80), claimed: m ? parseInt(m[1] || m[0], 10) : null, cards: n});
  }
  const csel = (cfg.cta_selectors && cfg.cta_selectors.length) ? cfg.cta_selectors : ['a.elementor-button', 'a.btn', 'a.button', 'a[class*="cta" i]', 'a[role="button"]'];
  const ctas = [...new Set(csel.flatMap(s => { try { return [...document.querySelectorAll(s)]; } catch { return []; } }))].filter(W.vis);
  const groups = new Map();
  for (const a of ctas) {
    const sec = a.closest('section,.elementor-section,.e-con,[class*="section" i]') || a.parentElement && a.parentElement.parentElement || document.body;
    if (!groups.has(sec)) groups.set(sec, []);
    groups.get(sec).push(a);
  }
  for (const [sec, list] of groups) {
    if (list.length < 2) continue;
    const by = new Map();
    for (const a of list) { let h = a.getAttribute('href') || ''; try { h = new URL(h, location.href).href; } catch {} if (!by.has(h)) by.set(h, []); by.get(h).push((a.innerText || '').trim().slice(0, 30)); }
    for (const [href, labels] of by) if (labels.length > 1 && href) res.ctas.push({section: W.sel(sec), href: href.slice(0, 120), labels});
  }
  return res;
};

const SIG = () => {
  const W = window.__wqg, vc = s => [...document.querySelectorAll(s)].filter(W.vis).length;
  const main = document.querySelector('main') || document.body;
  const grids = [...main.querySelectorAll('*')].filter(c => { if (!W.vis(c)) return false; const s = getComputedStyle(c); return s.display === 'grid' || (s.display === 'flex' && s.flexWrap === 'wrap'); })
    .map(c => [...c.children].filter(W.vis).length).filter(n => n >= 3);
  return {h1: vc('h1'), h2: vc('h2'), h3: vc('h3'), sections: [...main.children].filter(W.vis).length, forms: vc('form'), buttons: vc('button, a.elementor-button, a.btn, a.button'),
    images: vc('img'), paragraphs: vc('p'), links: vc('a[href]'), grids};
};

// ---- Chạy ----
let tab = null;
async function openSession() {
  if (tab) { try { await tab.close(); } catch {} }
  tab = await openTab({host: job.host, resolve: job.resolve, cookie: job.cookie, block: job.block || []});
  await tab.send('Page.enable'); await tab.send('Runtime.enable');
  await tab.send('DOM.enable'); await tab.send('CSS.enable');
}
const ev = (fn, arg, awaitPromise = false) => tab.evalv(`(${fn})(${arg === undefined ? '' : JSON.stringify(arg)})`, awaitPromise);
const shot = async (name) => {
  if (!job.shots_dir) return null;
  fs.mkdirSync(job.shots_dir, {recursive: true});
  const s = await tab.send('Page.captureScreenshot', {format: 'jpeg', quality: 72});
  fs.writeFileSync(path.join(job.shots_dir, name), Buffer.from(s.result.data, 'base64'));
  return name;
};

async function doMenu(row, pg, W) {
  const f = await ev(MENU_FIND, menuCfg);
  if (!f) { row.menu = {err: 'phép đo không trả kết quả'}; return; }
  row.menu = {...f};
  if (!f.found) return;
  const closed = await shot(`${pg.name}_${W}_menu-dong.jpg`);
  await tap(tab, f.x, f.y);
  await sleep(+(menuCfg.settle || 700));
  const after = await ev(MENU_AFTER) || {};
  row.menu.linksAfter = after.links; row.menu.expandedAfter = after.expanded;
  row.menu.shots = [closed, await shot(`${pg.name}_${W}_menu-mo.jpg`)].filter(Boolean);
}

async function doSlider(row, pg, W) {
  row.sliders = [];
  for (const s of sliders) {
    if (s.page && s.page !== pg.name) continue;
    if (!sliderWidths(s).includes(W)) continue;
    const f = await ev(SLIDER_FIND, s, true);
    const item = {selector: s.selector, ...(f || {err: 'phép đo không trả kết quả'})};
    if (f && f.found && f.btn) {
      await tap(tab, f.x, f.y);
      await sleep(+(s.settle || 900));
      Object.assign(item, await ev(SLIDER_AFTER) || {});
    }
    row.sliders.push(item);
  }
}

async function doStates(row, pg) {
  row.states = [];
  const doc = await tab.send('DOM.getDocument', {depth: 0});
  const root = doc.result.root.nodeId;
  for (const cfg of states) {
    if (cfg.page && cfg.page !== pg.name) continue;
    const want = cfg.states || ['hover', 'focus', 'active', 'visited'];
    const q = await tab.send('DOM.querySelectorAll', {nodeId: root, selector: cfg.selector});
    const ids = (q.result && q.result.nodeIds || []).slice(0, cfg.limit || 3);
    const item = {selector: cfg.selector, min_contrast: cfg.min_contrast, matched: (q.result && q.result.nodeIds || []).length, nodes: []};
    for (const nodeId of ids) {
      const rn = await tab.send('DOM.resolveNode', {nodeId});
      const objectId = rn.result && rn.result.object && rn.result.object.objectId;
      if (!objectId) continue;
      // CSS.getComputedStyleForNode trả cả màu :visited thật. getComputedStyle trong trang luôn trả màu chưa thăm (luật riêng tư của trình duyệt).
      const read = async () => {
        const cs = await tab.send('CSS.getComputedStyleForNode', {nodeId});
        const v = {}; for (const x of (cs.result && cs.result.computedStyle) || []) if (STATE_PROPS.includes(x.name)) v[x.name] = x.value;
        const ex = (await tab.send('Runtime.callFunctionOn', {objectId, functionDeclaration: `${STATE_EXTRA}`, returnByValue: true})).result?.result?.value;
        if (!ex || !Object.keys(v).length) return null;
        return {v, bg: isTransp(v['background-color']) ? ex.bg : v['background-color'], fs: ex.fs, fw: ex.fw, sel: ex.sel, text: ex.text};
      };
      await tab.send('CSS.forcePseudoState', {nodeId, forcedPseudoClasses: []});
      const base = await read();
      if (!base) continue;
      const node = {sel: base.sel, text: base.text, base: {color: base.v.color, bg: base.bg, fs: base.fs, fw: base.fw}, states: {}};
      for (const st of want) {
        await tab.send('CSS.forcePseudoState', {nodeId, forcedPseudoClasses: [st]});
        await sleep(+(cfg.settle || 400));
        const r = await read();
        await tab.send('CSS.forcePseudoState', {nodeId, forcedPseudoClasses: []});
        if (!r) continue;
        node.states[st] = {changed: Object.keys(base.v).filter(k => base.v[k] !== r.v[k]), color: r.v.color, bg: r.bg, fs: r.fs, fw: r.fw};
      }
      item.nodes.push(node);
    }
    row.states.push(item);
  }
}

const wantWidths = () => {
  const m = new Map();
  const add = (w, k) => { if (!m.has(w)) m.set(w, new Set()); m.get(w).add(k); };
  if (on('menu') && menuCfg) W_MENU.forEach(w => add(w, 'menu'));
  if (on('slider') && sliders.length) sliders.forEach(s => sliderWidths(s).forEach(w => add(w, 'slider')));
  if (on('states') && states.length) W_STATES.forEach(w => add(w, 'states'));
  if (on('buttons') && kit) W_BUTTONS.forEach(w => add(w, 'buttons'));
  if (on('layout') && layoutOn) W_LAYOUT.forEach(w => add(w, 'layout'));
  return m;
};

fs.mkdirSync(path.dirname(path.resolve(o.out)), {recursive: true});
const out = fs.createWriteStream(o.out, {flags: 'a'});
let written = 0;
try { sweepOrphans({apply: true}); await openSession(); } catch (e) { console.error('không mở được Chrome: ' + e.message); process.exit(1); }
const plan = wantWidths();

async function measure(url, W, feats, row, pg) {
  const {mob} = await setViewport(tab, W);
  row.mobile = mob;
  await loadUrl(tab, url, wait);
  Object.assign(row, docResponse(tab));
  await ev(LIB);
  if (feats.has('menu')) await doMenu(row, pg, W);
  if (feats.has('slider')) await doSlider(row, pg, W);
  if (feats.has('states')) await doStates(row, pg);
  if (feats.has('buttons')) { row.buttons = await ev(BUTTONS, kit) || []; row.non_cta = await ev(NON_CTA, kit) || []; }
  if (feats.has('layout')) row.layout = await ev(LAYOUT, I);
  if (feats.has('sig')) row.sig = await ev(SIG);
}
async function emit(row, feats, label) {
  out.write(JSON.stringify(row) + '\n'); written++;
  process.stderr.write(`${label} ${row.vw} ${row.err ? 'ERR ' + row.err : [...feats].join('+')}\n`);
}
async function guarded(fn, row) {
  try { await withTimeout(fn(), PAGE_TIMEOUT); }
  catch (e) { row.err = String(e.message || e).slice(0, 160); if (e.message === 'timeout') { try { await openSession(); } catch {} } }
}

for (const pg of job.pages || []) {
  for (const [W, feats] of [...plan].sort((a, b) => a[0] - b[0])) {
    const row = {kind: 'page', name: pg.name, url: pg.url, vw: W};
    await guarded(() => measure(pg.url, W, feats, row, pg), row);
    await emit(row, feats, pg.name);
  }
}
if (on('pairs')) for (const pr of pairs) for (const W of W_PAIRS) {
  const row = {kind: 'pair', name: pr.name || `${pr.vi} | ${pr.en}`, vw: W, vi: {url: pr.vi}, en: {url: pr.en}};
  await guarded(async () => {
    for (const side of ['vi', 'en']) {
      const r = {};
      await measure(pr[side], W, new Set(['sig']), r, {name: side});
      row[side] = {url: pr[side], status: r.status, sig: r.sig};
    }
  }, row);
  await emit(row, new Set(['pair']), row.name);
}
out.end(); await tab.close();
if (!written) { console.error('không ghi được dòng nào: kiểm khối interact trong qa.json'); process.exit(1); }
process.exit(0);
