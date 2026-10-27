// dbg_el.mjs (wp-ucss): tìm vì sao một phần tử lệch giữa CSS gốc và CSS gọn.
// node dbg_el.mjs --site <site.json> <outDir> <path> <dev> <css selector> <thuộc tính,...> [state: tai|js]
// In: hộp, display của phần tử và tổ tiên, các rule khớp (CDP CSS.getMatchedStylesForNode) có khai báo thuộc tính cần xem, ở cả hai bản.
import fs from 'fs';
import { site, args, slug, launch, openPage, runStates } from './lib-ucss.mjs';

const S = site();
const [outDir, path, dev, sel, propsArg, stateArg] = args();
const props = propsArg.split(',');
const CPATH = S.combined_css_path;
const gen = JSON.parse(fs.readFileSync(`${outDir}/pages/${dev}_${slug(path)}.json`, 'utf8'));
const FAKE = `https://${S.host}${S.test_prefix}` + gen.hash + '.css';
const override = new Map([[FAKE, { type: 'text/css', body: fs.readFileSync(`${outDir}/reduced/${gen.hash}.css`) }]]);
const browser = await launch();
const { p } = await openPage(browser, path, dev, { override, log: [] });
if ((stateArg || 'js') === 'js') await runStates(p, dev, async name => { if (name === 'js') throw new Error('dừng'); }, []).catch(() => {});
await p.evaluate(async (u, c) => {
  const o = document.querySelector(`link[rel="stylesheet"][href*="${c}"]`);
  const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = u;
  await new Promise(r => { l.onload = r; l.onerror = r; o.after(l); });
  window.__O = o; window.__R = l; l.sheet.disabled = true;
}, FAKE, CPATH);
const flip = red => p.evaluate(red => { __O.sheet.disabled = red; __R.sheet.disabled = !red; document.body.offsetHeight; }, red);
const cdp = await p.target().createCDPSession();
await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
const n = await p.evaluate((sel, props) => {
  const els = [...document.querySelectorAll(sel)];
  const snap = () => els.map(e => props.map(x => getComputedStyle(e).getPropertyValue(x)).join('|'));
  const a = snap(); __O.sheet.disabled = true; __R.sheet.disabled = false; document.body.offsetHeight; const b = snap();
  __O.sheet.disabled = false; __R.sheet.disabled = true;
  const idx = els.map((e, i) => a[i] !== b[i] ? i : -1).filter(i => i >= 0);
  idx.slice(0, 3).forEach((i, k) => els[i].setAttribute('data-dbg', k));
  return idx.length;
}, sel, props);
console.log(`${sel}: ${n} phần tử lệch`);
for (let k = 0; k < Math.min(n, 3); k++) {
  for (const red of [false, true]) {
    await flip(red);
    const info = await p.evaluate((k, props) => {
      const e = document.querySelector(`[data-dbg="${k}"]`); const r = e.getBoundingClientRect(); const anc = [];
      for (let x = e; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); anc.push(x.tagName.toLowerCase() + (x.id ? '#' + x.id : '') + '.' + [...x.classList].slice(0, 4).join('.') + ':' + cs.display + (cs.visibility !== 'visible' ? '/' + cs.visibility : '')); }
      return { rect: [r.x, r.y, r.width, r.height].map(Math.round), v: props.map(x => x + '=' + getComputedStyle(e).getPropertyValue(x)), anc: anc.slice(0, 8) };
    }, k, props);
    const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
    const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-dbg="${k}"]` });
    const m = await cdp.send('CSS.getMatchedStylesForNode', { nodeId });
    const rules = (m.matchedCSSRules || []).filter(x => x.rule.style.cssProperties.some(c => props.some(pp => c.name === pp || c.name.startsWith(pp.split('-')[0]))))
      .map(x => (x.rule.media && x.rule.media.length ? '@' + x.rule.media.map(q => q.text).join(' ') + ' ' : '') + x.rule.selectorList.text.slice(0, 120) + ' {' + x.rule.style.cssProperties.filter(c => props.some(pp => c.name.startsWith(pp.split('-')[0]))).map(c => c.name + ':' + c.value).join(';').slice(0, 160) + '}');
    console.log(`#${k} ${red ? 'GỌN' : 'GỐC'} rect=${info.rect} ${info.v.join(' ')}\n  tổ tiên: ${info.anc.join(' < ')}\n  rule: \n   ${rules.join('\n   ')}`);
  }
}
await browser.close();
