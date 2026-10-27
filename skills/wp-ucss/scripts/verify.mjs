// verify.mjs (wp-ucss): so giao diện CSS gốc và CSS gọn trên cùng trang, cùng trạng thái.
// node verify.mjs --site <site.json> <jobs.txt> <outDir> [số tab]. CSS gọn lấy từ <outDir>/reduced/<hash>.css, nạp vào trang qua URL giả test_prefix (không đụng server).
// Mỗi trạng thái chụp 3 lần: A (gốc), B (gọn), A2 (gốc lại). Chỉ tính lệch khi A = A2 và B ≠ A, để loại nhiễu do slider, animation, timer.
import fs from 'fs';
import { site, args, slug, launch, openPage, runStates, combinedHref, T } from './lib-ucss.mjs';

const S = site();
const [jobsFile, outDir, tabsArg] = args();
const TABS = Number(tabsArg || 2);
const STATES = new Set((process.env.STATES || 'js,cuon,menu,hover1,accordion,form').split(','));
const jobs = fs.readFileSync(jobsFile, 'utf8').split('\n').map(l => l.trim().split(/\s+/)).filter(x => x[0] && x[0].startsWith('/'));
fs.mkdirSync(outDir + '/verify', { recursive: true });
const FAKE = `https://${S.host}${S.test_prefix}`;
const CPATH = S.combined_css_path;

const INPAGE = () => {
  // Khoảng 80 thuộc tính ảnh hưởng hiển thị. Hộp phần tử (@rect) bắt mọi lệch bố cục còn lại.
  const PROPS = ['display', 'position', 'top', 'right', 'bottom', 'left', 'float', 'clear', 'width', 'height', 'min-width', 'min-height', 'max-width', 'max-height',
    'margin-top', 'margin-right', 'margin-bottom', 'margin-left', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width', 'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
    'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color', 'border-top-left-radius', 'border-top-right-radius', 'border-bottom-left-radius', 'border-bottom-right-radius',
    'box-sizing', 'overflow-x', 'overflow-y', 'z-index', 'opacity', 'visibility', 'color', 'background-color', 'background-image', 'background-size', 'background-position', 'background-repeat',
    'font-family', 'font-size', 'font-weight', 'font-style', 'line-height', 'letter-spacing', 'text-align', 'text-decoration-line', 'text-transform', 'white-space', 'word-break', 'overflow-wrap',
    'transform', 'animation-name', 'flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'align-self', 'flex-grow', 'flex-shrink', 'flex-basis', 'order', 'row-gap', 'column-gap',
    'grid-template-columns', 'grid-template-rows', 'grid-column-start', 'grid-column-end', 'grid-row-start', 'grid-row-end', 'box-shadow', 'filter', 'object-fit', 'list-style-type',
    'cursor', 'pointer-events', 'clip-path', 'vertical-align', 'text-overflow', 'aspect-ratio', 'content'];
  const st = document.createElement('style'); st.id = 'ucss-freeze';
  st.textContent = '*,*::before,*::after{transition-duration:0s!important;transition-delay:0s!important;animation-play-state:paused!important;caret-color:transparent!important}';
  document.head.appendChild(st);
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.') : '');
  const read = cs => { const o = {}; for (const p of PROPS) o[p] = cs.getPropertyValue(p); return o; };
  window.__snap = () => {
    const rows = [];
    for (const el of document.querySelectorAll('body, body *')) {
      const v = read(getComputedStyle(el));
      const r = el.getBoundingClientRect();
      v['@rect'] = [r.x, r.y, r.width, r.height].map(x => Math.round(x * 2) / 2).join(',');
      const ps = {};
      for (const pe of ['::before', '::after'].concat(/^(INPUT|TEXTAREA)$/.test(el.tagName) ? ['::placeholder'] : []).concat(el.tagName === 'LI' ? ['::marker'] : [])) {
        const c = getComputedStyle(el, pe);
        if ((pe === '::before' || pe === '::after') && (c.content === 'none' || c.content === 'normal')) { ps[pe] = 'none'; continue; }
        ps[pe] = read(c);
      }
      // Dấu JS: class và style inline. JS đổi giữa các lần chụp thì phần tử đó không dùng để so.
      rows.push({ el, v, ps, js: (el.getAttribute('class') || '') + '|' + (el.getAttribute('style') || '') });
    }
    const fonts = new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '').toLowerCase() + '|' + f.weight + '|' + f.style));
    // Animation CSS đang có: thiếu @keyframes thì Chrome không tạo CSSAnimation dù animation-name giữ nguyên.
    const anims = document.getAnimations().map(a => a.animationName || '').filter(Boolean).sort().join(',');
    return { rows, fonts, anims, h: document.documentElement.scrollHeight };
  };
  window.__diff = (A, B, A2) => {
    const out = [], keys = []; let n = 0, unstable = 0;
    const m2 = new Map(A2.rows.map(r => [r.el, r])), mb = new Map(B.rows.map(r => [r.el, r]));
    // Phần tử lệch đầu tiên (tối đa 3) để chụp ảnh gốc | gọn cho Jev.
    const dEls = window.__dEls = [];
    const mark = el => { if (dEls.length < 3 && !dEls.includes(el)) dEls.push(el); };
    // keys: "<số thứ tự phần tử>|<pseudo>|<thuộc tính>" để so lượt xác nhận (DOM giữ nguyên giữa hai lượt).
    const hit = (i, el, where, p, a, b) => { n++; mark(el); keys.push(i + '|' + where + '|' + p); if (out.length < 200) out.push([name(el), where, p, a, b, i]); };
    const cmp = (a, b, a2, where, el, i) => {
      if (a === 'none' || b === 'none') { if (a !== b && a === a2) hit(i, el, where, 'content', a === 'none' ? 'none' : 'có', b === 'none' ? 'none' : 'có'); return; }
      for (const p in a) if (a[p] !== b[p] && a2 && a[p] === a2[p]) hit(i, el, where, p, String(a[p]).slice(0, 80), String(b[p]).slice(0, 80));
    };
    A.rows.forEach((ra, i) => {
      const rb = mb.get(ra.el), r2 = m2.get(ra.el); if (!rb || !r2) return;
      if (ra.js !== rb.js || ra.js !== r2.js) { unstable++; return; }
      cmp(ra.v, rb.v, r2.v, '', ra.el, i);
      for (const pe in ra.ps) cmp(ra.ps[pe], rb.ps[pe], r2.ps[pe], pe, ra.el, i);
    });
    const lostFonts = [...A.fonts].filter(f => A2.fonts.has(f) && !B.fonts.has(f));
    const animDiff = A.anims !== B.anims ? [A.anims.slice(0, 300), B.anims.slice(0, 300), A2.anims === A.anims] : null;
    const hDiff = A.h !== B.h && A.h === A2.h ? [A.h, B.h] : null;
    return { n, out, keys, lostFonts, animDiff, hDiff, unstable, els: A.rows.length };
  };
};

// Chụp vùng phần tử lệch (hộp gộp của bản gốc và bản gọn, thêm lề 16 px) ở cả hai bản: <base>_<i>_a.png (gốc), _b.png (gọn).
async function shots(p, base, rec) {
  fs.mkdirSync(outDir + '/shots', { recursive: true });
  const k = await p.evaluate(() => (window.__dEls || []).length);
  const flip = red => p.evaluate(async red => {
    __O.sheet.disabled = red; __R.sheet.disabled = !red; await document.fonts.ready;
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, red);
  for (let i = 0; i < k; i++) {
    const rect = () => p.evaluate(i => { const r = __dEls[i].getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }, i);
    await p.evaluate(i => __dEls[i].scrollIntoView({ block: 'center' }), i);
    const ra = await rect(); await flip(true); const rb = await rect(); await flip(false);
    const vw = await p.evaluate(() => [innerWidth, innerHeight]);
    const x = Math.max(0, Math.min(ra[0], rb[0]) - 16), y = Math.max(0, Math.min(ra[1], rb[1]) - 16);
    const w = Math.min(vw[0], Math.max(ra[2], rb[2]) + 16) - x, h = Math.min(vw[1], Math.max(ra[3], rb[3]) + 16) - y;
    if (w < 8 || h < 8) continue;
    const clip = { x, y, width: w, height: h };
    await p.screenshot({ path: `${base}_${i}_a.png`, clip });
    await flip(true); await p.screenshot({ path: `${base}_${i}_b.png`, clip }); await flip(false);
    (rec.shots ||= []).push(`${base.split('/').pop()}_${i}`);
  }
}

async function one(browser, path, dev) {
  const f = `${outDir}/verify/${dev}_${slug(path)}.json`;
  if (fs.existsSync(f)) return;
  const log = [], t0 = Date.now();
  const gen = JSON.parse(fs.readFileSync(`${outDir}/pages/${dev}_${slug(path)}.json`, 'utf8'));
  const red = `${outDir}/reduced/${gen.hash}.css`;
  const rec = { path, dev, hash: gen.hash, log, states: [] };
  if (!gen.hash || !fs.existsSync(red)) { rec.skip = 'không có CSS gọn'; fs.writeFileSync(f, JSON.stringify(rec)); return; }
  const override = new Map([[FAKE + gen.hash + '.css', { type: 'text/css', body: fs.readFileSync(red) }]]);
  const { ctx, p, errs } = await openPage(browser, path, dev, { override, log });
  rec.errs = errs;
  try {
    const href = await combinedHref(p, CPATH);
    if (!href || !href.includes(gen.hash)) { rec.skip = 'file gộp đã đổi: ' + (href || 'không có'); return; }
    // Gắn CSS gọn ngay sau link gốc, tắt sẵn; nạp font một lần.
    await p.evaluate(async (u, c) => {
      const o = document.querySelector(`link[rel="stylesheet"][href*="${c}"]`);
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = u; l.id = 'ucss-red';
      await new Promise(r => { l.onload = r; l.onerror = r; o.after(l); });
      window.__O = o; window.__R = l;
      o.sheet.disabled = true; l.sheet.disabled = false; document.body.offsetHeight; await document.fonts.ready;
      o.sheet.disabled = false; l.sheet.disabled = true; document.body.offsetHeight; await document.fonts.ready;
    }, FAKE + gen.hash + '.css', CPATH);
    await p.evaluate(INPAGE);
    let hov = 0;
    await runStates(p, dev, async name => {
      if (name === 'hover') name = 'hover' + (++hov);
      if (!STATES.has(name)) return;
      const once = () => T(p.evaluate(async () => {
        const fr = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        await fr(); const A = __snap();
        __O.sheet.disabled = true; __R.sheet.disabled = false; await document.fonts.ready; await fr(); const B = __snap();
        __O.sheet.disabled = false; __R.sheet.disabled = true; await document.fonts.ready; await fr(); const A2 = __snap();
        return __diff(A, B, A2);
      }), 45000, log, 'so-' + name);
      const r = await once();
      // Lượt xác nhận: chỉ giữ lệch xuất hiện ở cả hai lượt. Nguồn: site WordPress OLS + LiteSpeed Cache, 26/10/2026: margin auto của flex item
      // đọc ra 0px ngay sau khi đổi sheet (hộp và ảnh trùng từng pixel), lượt đọc sau trả đúng giá trị.
      if (r && (r.n || r.hDiff || r.lostFonts.length)) {
        const r2 = await once();
        if (r2) {
          const k2 = new Set(r2.keys), keep = new Set(r.keys.filter(k => k2.has(k)));
          r.transient = r.n - keep.size; r.n = keep.size;
          r.out = r.out.filter(o => keep.has(o[5] + '|' + o[1] + '|' + o[2]));
          if (!r2.hDiff) r.hDiff = null;
          r.lostFonts = r.lostFonts.filter(f => r2.lostFonts.includes(f));
        }
      }
      if (r) delete r.keys;
      rec.states.push([name, r || null]);
      if (r && r.n) await T(shots(p, `${outDir}/shots/${dev}_${slug(path)}_${name}`, rec), 30000, log, 'anh-' + name);
    }, log);
  } catch (e) { rec.err = String(e).slice(0, 200); }
  finally {
    rec.ms = Date.now() - t0;
    if (!rec.err) fs.writeFileSync(f, JSON.stringify(rec));
    const tot = rec.states.reduce((s, [, r]) => s + (r ? r.n : 0), 0);
    const lost = rec.states.reduce((s, [, r]) => s + (r ? r.lostFonts.length : 0), 0);
    console.log(dev, path, (rec.hash || '-').slice(0, 8), rec.skip || `lệch=${tot}`, lost ? 'mất-font=' + lost : '', Math.round(rec.ms / 1000) + 's', rec.err || '');
    await p.goto('about:blank').catch(() => {}); await ctx.close().catch(() => {});
  }
}

const browser = await launch();
let k = 0;
await Promise.all(Array.from({ length: TABS }, async () => { while (k < jobs.length) { const [path, dev] = jobs[k++]; await one(browser, path, dev); } }));
await browser.close();
