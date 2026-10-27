// lib-ucss.mjs (wp-ucss): cấu hình site, module Node và Chrome cho gen, verify, build.
// Cài module một lần: mkdir -p ~/.cache/wp-ucss && cd ~/.cache/wp-ucss && npm i puppeteer-core postcss css-tree@3.2.1
// Ghim css-tree 3.2.1: test hồi quy byte chạy trên bản này; bản 1.x tách selector lệch chỉ số (model.mjs dừng).
// Thư mục module khác: UCSS_NODE_MODULES=<node_modules>. Chrome khác: CHROME_BIN.
// Chỉ HTML đi tới site (mỗi lượt cách nhau ≥ rate_ms). CSS, JS, font tải một lần bằng Node rồi trả từ bộ nhớ và đĩa (cache_dir).
// Ảnh trả GIF 1×1 tại chỗ. Host đo lường bị chặn DNS. Không gửi form, không theo link.
import fs from 'fs';
import os from 'os';
import { join, resolve, dirname } from 'path';
import crypto from 'crypto';
import https from 'https';
import { createRequire } from 'module';

const NM = process.env.UCSS_NODE_MODULES || join(os.homedir(), '.cache/wp-ucss/node_modules');
export const rq = createRequire(NM.replace(/\/*$/, '/'));
const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
export const sleep = ms => new Promise(r => setTimeout(r, ms));
export const slug = p => (p.replace(/^\/|\/$/g, '').replace(/[^\w-]+/g, '_') || 'home').slice(0, 120);
// Biến thể: m, d (khách mobile, desktop, Accept có WebP), g (Googlebot), q, p (khách mobile, desktop gửi Accept */*).
// CDN giữ bản Accept của lượt đầu sau purge, nên bản p, q cũng cần CSS gọn (site WordPress OLS + LiteSpeed Cache, 27/10/2026).
export const isDesk = dev => dev === 'd' || dev === 'p';

// Cấu hình site: --site <site.json> hoặc biến UCSS_SITE (mẫu: templates/site.example.json).
// cache_dir và safelist tương đối thì tính từ thư mục chứa site.json.
const NEED = ['host', 'asset_hosts', 'block_dns', 'ua', 'accept', 'accept_language', 'viewport', 'combined_css_path', 'test_prefix',
  'js_ready_event', 'js_deferred_selector', 'stub_vary', 'stub_ajax', 'states'];
let S = null;
export function site() {
  if (S) return S;
  const a = process.argv, i = a.indexOf('--site'), f = i >= 0 ? a[i + 1] : process.env.UCSS_SITE;
  if (!f) throw new Error('thiếu --site <site.json> hoặc biến UCSS_SITE');
  const j = JSON.parse(fs.readFileSync(f, 'utf8'));
  for (const k of NEED) if (j[k] === undefined) throw new Error(`site.json thiếu khoá "${k}"`);
  const abs = p => resolve(dirname(resolve(f)), p.replace(/^~(?=\/)/, os.homedir()));
  S = { rate_ms: 1000, cache_dir: `~/.cache/wp-ucss/cache/${j.host}`, safelist: 'safelist.json', ...j };
  S.cache_dir = abs(S.cache_dir) + '/';
  S.safelist = abs(S.safelist);
  return S;
}
// Tham số vị trí, đã bỏ cặp --site <file>.
export function args() { const a = process.argv.slice(2), i = a.indexOf('--site'); if (i >= 0) a.splice(i, 2); return a; }

const GIF = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64');
const mem = new Map();
const key = u => crypto.createHash('md5').update(u).digest('hex');
let lastHit = 0, chain = Promise.resolve();
// Hàng đợi chung: mọi lượt tới host của site cách nhau ≥ rate_ms.
export function gate() { const p = chain.then(async () => { const w = lastHit + site().rate_ms - Date.now(); if (w > 0) await sleep(w); lastHit = Date.now(); }); chain = p; return p; }

function fetchBuf(u) {
  return new Promise((res, rej) => {
    https.get(u, { headers: { 'User-Agent': site().ua.d, 'Accept': '*/*' }, timeout: 60000 }, r => {
      if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location) { r.resume(); return fetchBuf(new URL(r.headers.location, u).href).then(res, rej); }
      const b = []; r.on('data', c => b.push(c)); r.on('end', () => res({ status: r.statusCode, type: r.headers['content-type'] || 'application/octet-stream', body: Buffer.concat(b) }));
    }).on('error', rej).on('timeout', function () { this.destroy(new Error('timeout')); });
  });
}
// Tài nguyên tĩnh: bộ nhớ → đĩa → mạng (host của site qua gate).
export async function asset(u) {
  if (mem.has(u)) return mem.get(u);
  const S = site(), f = S.cache_dir + key(u);
  if (fs.existsSync(f)) { const meta = JSON.parse(fs.readFileSync(f + '.json', 'utf8')); const v = { ...meta, body: fs.readFileSync(f) }; mem.set(u, v); return v; }
  if (new URL(u).hostname === S.host) await gate();
  const v = await fetchBuf(u);
  if (v.status === 200) { fs.mkdirSync(S.cache_dir, { recursive: true }); fs.writeFileSync(f, v.body); fs.writeFileSync(f + '.json', JSON.stringify({ status: v.status, type: v.type, url: u })); }
  mem.set(u, v);
  return v;
}

export async function launch() {
  const HRR = site().block_dns.map(h => `MAP ${h} ~NOTFOUND`).join(', ');
  return rq('puppeteer-core').launch({ executablePath: CHROME, headless: 'new', protocolTimeout: 60000, args: ['--no-first-run', '--hide-scrollbars', `--host-resolver-rules=${HRR}`] });
}

// override: Map url → {type, body} để thay tài nguyên (verify dùng để nạp CSS gọn từ máy).
export async function openPage(browser, path, dev, { override = new Map(), log = [] } = {}) {
  const S = site();
  const vary = new RegExp(S.stub_vary), ajax = new RegExp(S.stub_ajax);
  const ctx = await browser.createBrowserContext();
  const p = await ctx.newPage();
  await p.setUserAgent(S.ua[dev]); await p.setViewport(S.viewport[dev]);
  await p.setExtraHTTPHeaders({ 'Accept-Language': S.accept_language });
  await p.setRequestInterception(true);
  let docDone = false;
  p.on('request', async q => {
    const u = q.url(); const rt = q.resourceType();
    try {
      if (/^data:|^blob:/.test(u)) return q.continue();
      let h = ''; try { h = new URL(u).hostname; } catch (e) {}
      if (rt === 'document' && q.frame() === p.mainFrame()) {
        if (docDone || h !== S.host) return q.abort();
        docDone = true; await gate(); return q.continue({ headers: { ...q.headers(), Accept: S.accept[dev] } });
      }
      if (override.has(u.split('?')[0])) { const o = override.get(u.split('?')[0]); return q.respond({ status: 200, contentType: o.type, body: o.body }); }
      if (rt === 'image' || rt === 'media') return q.respond({ status: 200, contentType: 'image/gif', body: GIF });
      if (vary.test(u)) return q.respond({ status: 200, contentType: 'application/json', body: '[]' });
      if (q.method() !== 'GET' || ajax.test(u)) return q.respond({ status: 200, contentType: 'application/json', body: '{}' });
      if ((h === S.host && /\.(css|js|woff2?|ttf|otf|eot|svg)(\?|$)/i.test(u)) || S.asset_hosts.includes(h)) {
        const v = await asset(u);
        return q.respond({ status: v.status, contentType: v.type, body: v.body, headers: { 'Access-Control-Allow-Origin': '*' } });
      }
      log.push('chặn ' + rt + ' ' + u.slice(0, 90));
      return q.abort();
    } catch (e) { log.push('lỗi req ' + String(e).slice(0, 80)); try { q.abort(); } catch (e2) {} }
  });
  await p.evaluateOnNewDocument(ev => {
    window.__lsd = 0;
    document.addEventListener(ev, () => { window.__lsd = 1; });
    // Không theo link khi bấm: chặn mặc định của thẻ a có href thật, handler JS vẫn chạy.
    document.addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[href]'); if (a && !/^(#|javascript:)/.test(a.getAttribute('href') || '#')) e.preventDefault(); }, true);
    document.addEventListener('submit', e => e.preventDefault(), true);
    window.open = () => null;
  }, S.js_ready_event);
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.goto(`https://${S.host}${path}`, { waitUntil: 'load', timeout: 60000 }).catch(e => log.push('goto ' + String(e).slice(0, 60)));
  return { ctx, p, errs };
}

// URL file CSS gộp của trang (c = combined_css_path). Trang đã dùng CSS gọn (mu-plugin đổi href, URL gốc nằm trong onerror):
// trả link về file gộp gốc, chờ nạp xong rồi trả URL. Thiếu bước này, gen.mjs ghi hash null và verify.mjs bỏ qua cặp đã đổi link
// (site mẫu 27/10/2026: 124 cặp bị bỏ qua, map mới mất 30 path).
export async function combinedHref(p, c) {
  return p.evaluate(async c => {
    const l = document.querySelector(`link[rel="stylesheet"][href*="${c}"]`);
    if (l) return l.href;
    const s = [...document.querySelectorAll('link[rel="stylesheet"][onerror]')].find(x => x.getAttribute('onerror').includes(c));
    const m = s && s.getAttribute('onerror').match(/href='([^']+)'/);
    if (!m) return null;
    await new Promise(r => { s.onload = s.onerror = r; s.href = m[1]; setTimeout(r, 15000); });
    return s.href;
  }, c);
}

export const T = (pr, ms, log, name) => Promise.race([pr, sleep(ms).then(() => { log.push('hết giờ ' + name); })]).catch(e => log.push(name + ': ' + String(e).slice(0, 80)));

// Các trạng thái giao diện. cb(tên) chạy sau mỗi trạng thái (gen: thử selector; verify: so style). Selector lấy từ states của site.json.
export async function runStates(p, dev, cb, log) {
  const S = site(), st = S.states;
  await sleep(1200);
  await cb('tai');
  // JS hoãn của trang guest chạy khi có tương tác.
  await T((async () => {
    await p.mouse.move(200, 300); await p.mouse.move(220, 320);
    if (!isDesk(dev)) await p.touchscreen.tap(5, 5).catch(() => {});
    await p.keyboard.press('Shift');
    for (let i = 0; i < 40; i++) { if (await p.evaluate(s => window.__lsd || !document.querySelector(s), S.js_deferred_selector)) break; await sleep(200); }
    await sleep(1200);
  })(), 15000, log, 'js');
  await cb('js');
  await T((async () => {
    const H = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < H; y += 700) { await p.evaluate(v => window.scrollTo(0, v), y); await sleep(120); }
    await sleep(800);
  })(), 30000, log, 'cuon');
  await cb('cuon');
  await T(p.evaluate(() => window.scrollTo(0, 0)).then(() => sleep(500)), 8000, log, 'len');
  await cb('dau');
  if (!isDesk(dev)) {
    await T((async () => {
      await p.evaluate(s => { const t = document.querySelector(s); if (t) t.click(); }, st.menu_toggle); await sleep(900);
      await p.evaluate(s => { [...document.querySelectorAll(s)].slice(0, 3).forEach(x => x.click()); }, st.menu_indicator); await sleep(900);
    })(), 8000, log, 'menu');
    await cb('menu');
    await T(p.evaluate(s => { const t = document.querySelector(s); if (t) t.click(); }, st.menu_toggle).then(() => sleep(600)), 8000, log, 'dongmenu');
  } else {
    const items = await p.$$(st.hover).catch(() => []);
    for (const it of items.slice(0, 8)) {
      await T(it.hover().then(() => sleep(450)), 3000, log, 'hover');
      await cb('hover');
    }
    await T(p.mouse.move(5, 600).then(() => sleep(400)), 2000, log, 'roi');
  }
  // Accordion, tab, details, toggle: bấm tối đa 12 phần tử, không bấm nút gửi form.
  await T(p.evaluate(sel => {
    const els = [...document.querySelectorAll(sel)].filter(e => !e.closest('form') && e.type !== 'submit').slice(0, 12);
    els.forEach(e => { try { e.click(); } catch (x) {} });
    return els.length;
  }, st.accordion).then(() => sleep(900)), 6000, log, 'accordion');
  await cb('accordion');
  await T((async () => {
    const n = await p.evaluate(s => { const b = [...document.querySelectorAll(s)].slice(0, 6); b.forEach(x => x.click()); return b.length; }, st.slider_next);
    if (n) await sleep(900);
  })(), 5000, log, 'slider');
  await cb('slider');
  // Form: focus rồi blur ô bắt buộc (hiện lỗi kiểm), gõ thử vào ô đầu. Không gửi.
  await T((async () => {
    const ins = await p.$$(st.form_inputs);
    for (const el of ins.slice(0, 4)) { await el.focus().catch(() => {}); await sleep(120); await p.evaluate(e => e.blur(), el).catch(() => {}); }
    if (ins[0]) { await ins[0].focus(); await p.keyboard.type('a', { delay: 30 }); }
    await sleep(700);
  })(), 8000, log, 'form');
  await cb('form');
}
