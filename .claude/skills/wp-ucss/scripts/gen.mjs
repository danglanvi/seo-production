// gen.mjs (wp-ucss): render từng trang guest, ghi selector của file CSS gộp khớp DOM ở mọi trạng thái.
// node gen.mjs --site <site.json> <jobs.txt: "path dev" mỗi dòng> <outDir> [số tab, mặc định 2]. Trang đã có file kết quả thì bỏ qua (chạy lại được).
import fs from 'fs';
import { site, args, slug, launch, openPage, runStates, asset, combinedHref, T } from './lib-ucss.mjs';
import { buildModel, relaxed, jsTokens, loadSafelist } from './model.mjs';
const S = site();
const SAFE = loadSafelist(S.safelist);
const CPATH = S.combined_css_path;
const HASH = new RegExp(CPATH.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([0-9a-f]{32})\\.css');

const [jobsFile, outDir, tabsArg] = args();
const TABS = Number(tabsArg || 2);
const jobs = fs.readFileSync(jobsFile, 'utf8').split('\n').map(l => l.trim().split(/\s+/)).filter(x => x[0] && x[0].startsWith('/'));
fs.mkdirSync(outDir + '/pages', { recursive: true }); fs.mkdirSync(outDir + '/model', { recursive: true });
const models = new Map(), jsTok = new Map();

async function model(hash, url) {
  if (models.has(hash)) return models.get(hash);
  const css = (await asset(url)).body.toString('utf8');
  const m = buildModel(css);
  fs.writeFileSync(`${outDir}/model/${hash}.json`, JSON.stringify({ list: m.list, rules: m.rules, pseudoSel: m.pseudoSel }));
  models.set(hash, m);
  return m;
}
async function tokensOf(src) {
  if (jsTok.has(src)) return jsTok.get(src);
  const J = new Set(), P = new Set();
  try { jsTokens((await asset(src)).body.toString('utf8'), J, P); } catch (e) {}
  const v = { J, P }; jsTok.set(src, v); return v;
}

async function one(browser, path, dev) {
  const f = `${outDir}/pages/${dev}_${slug(path)}.json`;
  if (fs.existsSync(f)) return;
  const log = [], t0 = Date.now();
  const { ctx, p, errs } = await openPage(browser, path, dev, { log });
  const rec = { path, dev, log, errs };
  try {
    const href = await combinedHref(p, CPATH);
    const nLinks = await p.evaluate(c => document.querySelectorAll(`link[href*="${c}"]`).length, CPATH);
    rec.final = await p.evaluate(() => location.pathname);
    if (!href) { rec.hash = null; return; }
    rec.hash = href.match(HASH)[1]; rec.href = href; rec.nLinks = nLinks;
    const m = await model(rec.hash, href.split('?')[0] + (href.includes('?') ? '?' + href.split('?')[1] : ''));
    await p.evaluate(list => {
      window.__U = list; window.__M = new Uint8Array(list.length); window.__F = new Set(); window.__A = new Set();
      window.__test = () => {
        let n = 0;
        for (let i = 0; i < __U.length; i++) if (!__M[i]) { try { if (document.querySelector(__U[i])) { __M[i] = 1; n++; } } catch (e) { __M[i] = 3; } }
        const add = cs => { if (!cs) return; cs.fontFamily.split(',').forEach(f => __F.add(f.trim().replace(/^["']|["']$/g, '').toLowerCase())); cs.animationName.split(',').forEach(a => __A.add(a.trim().toLowerCase())); };
        for (const el of document.querySelectorAll('*')) { add(getComputedStyle(el)); for (const ps of ['::before', '::after']) { const c = getComputedStyle(el, ps); if (c.content !== 'none' && c.content !== 'normal') add(c); } }
        return n;
      };
    }, m.list);
    // Selector gốc có pseudo mà Chrome không đọc được: ghi một lần cho mỗi file gộp.
    const fi = `${outDir}/model/${rec.hash}.invalid.json`;
    if (!fs.existsSync(fi)) {
      const ok = await p.evaluate(ss => ss.map(s => { try { return CSS.supports('selector(' + s + ')') ? 1 : 0; } catch (e) { return 0; } }), m.pseudoSel.map(x => x[2]));
      fs.writeFileSync(fi, JSON.stringify(m.pseudoSel.filter((x, k) => !ok[k]).map(x => x[0] + ':' + x[1])));
    }
    rec.states = [];
    await runStates(p, dev, async name => { const n = await T(p.evaluate(() => __test()), 20000, log, 'test-' + name); rec.states.push([name, n]); }, log);
    // Trình duyệt tắt JS: nội dung <noscript> thành phần tử thật. Dựng lại trong DOM rồi thử selector lần cuối.
    const nNs = await T(p.evaluate(() => {
      const ns = [...document.querySelectorAll('noscript')];
      ns.forEach(n => { const t = document.createElement('template'); t.innerHTML = n.textContent; n.textContent = ''; n.appendChild(t.content); });
      return ns.length;
    }), 5000, log, 'noscript');
    if (nNs) { const n = await T(p.evaluate(() => __test()), 20000, log, 'test-noscript'); rec.states.push(['noscript', n]); }
    const M = await p.evaluate(() => Array.from(__M));
    rec.used = []; rec.invalid = [];
    M.forEach((v, i) => { if (v === 1) rec.used.push(i); else if (v === 3) rec.invalid.push(i); });
    // Tập J: token chuỗi trong mọi JS trang chạy (file ngoài + inline). File ngoài chỉ đọc khi URL chứa host của site.
    const { srcs, inline } = await p.evaluate(() => ({ srcs: [...document.scripts].map(s => s.src).filter(Boolean), inline: [...document.scripts].filter(s => !s.src).map(s => s.textContent).join('\n') }));
    const J = new Set(), P = new Set();
    jsTokens(inline, J, P);
    for (const s of srcs) { if (!s.includes(S.host)) continue; const t = await tokensOf(s); t.J.forEach(x => J.add(x)); t.P.forEach(x => P.add(x)); }
    const Pa = [...P];
    const dyn = c => J.has(c) || Pa.some(x => c.startsWith(x)) || SAFE.safeClass(c);
    const cand = []; M.forEach((v, i) => { if (v === 0) cand.push(i); });
    const rs = cand.map(i => relaxed(m, i, dyn, SAFE.optType));
    const hit = await p.evaluate(rs => rs.map(s => { try { return document.querySelector(s) ? 1 : 0; } catch (e) { return 1; } }), rs);
    rec.relaxed = cand.filter((i, k) => hit[k]);
    rec.kfJs = m.kf.filter(n => J.has(n));
    rec.fams = await p.evaluate(() => [...__F]); rec.anims = await p.evaluate(() => [...__A]).then(a => a.filter(x => x !== 'none'));
    rec.nJ = J.size; rec.nScripts = srcs.length;
  } catch (e) { rec.err = String(e).slice(0, 200); }
  finally {
    rec.ms = Date.now() - t0;
    if (rec.err && rec.hash) { /* lỗi giữa chừng: không ghi file kết quả để lần chạy sau làm lại */ console.log('LỖI', dev, path, rec.err); }
    else fs.writeFileSync(f, JSON.stringify(rec));
    console.log(dev, path, rec.hash ? rec.hash.slice(0, 8) : '-', 'used', (rec.used || []).length, 'relax', (rec.relaxed || []).length, Math.round(rec.ms / 1000) + 's', errs.length ? 'pageerr=' + errs.length : '');
    await p.goto('about:blank').catch(() => {}); await ctx.close().catch(() => {});
  }
}

const browser = await launch();
let k = 0;
await Promise.all(Array.from({ length: TABS }, async () => { while (k < jobs.length) { const [path, dev] = jobs[k++]; await one(browser, path, dev); } }));
await browser.close();
