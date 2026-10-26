// Bản đồ font theo vùng: font khai báo, font Chrome thật sự vẽ, file CSS + selector khai báo; chụp ảnh tô viền theo font.
// node fontmap.mjs --out <thư mục> [--src] [--mobile] [--resolve host=ip] [--cookie n=v] <url>...
// Mặc định đo trang như khách nhận (sau tối ưu của LiteSpeed). --src thêm LSCWP_CTRL=before_optm để thấy file CSS gốc; chỉ dùng để tìm file cần sửa.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass". Ghi fontmap.json, <slug>__overview.jpg, <slug>__g<N>.jpg.
import fs from 'node:fs';
import {args, openTab, sleep} from './_chrome.mjs';
const o = args(process.argv.slice(2), ['src', 'mobile']), urls = o._, outDir = o.out;
fs.mkdirSync(outDir, { recursive: true });
const sheets = new Map();
const tab = await openTab({host: new URL(urls[0]).host, resolve: o.resolve, cookie: o.cookie});
const send = tab.send;
tab.on(m => { if (m.method === 'CSS.styleSheetAdded') sheets.set(m.params.header.styleSheetId, m.params.header); });
const ev = expression => tab.evalv(expression, true);
await send('Page.enable'); await send('DOM.enable'); await send('CSS.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', o.mobile ? { width: 390, height: 844, deviceScaleFactor: 2, mobile: true } : { width: 1366, height: 900, deviceScaleFactor: 1, mobile: false });

// Mỗi web font một màu theo thứ tự gặp. Đỏ: font hệ thống (web font chưa nạp hoặc thiếu ký tự). Xám: không vẽ lúc đo.
// Montserrat biến thiên của Google Fonts hiện tên "Montserrat Thin".
const PAL = ['#16a34a', '#2563eb', '#0891b2', '#9333ea', '#ca8a04', '#db2777', '#0d9488', '#4f46e5'], pal = new Map();
const color = (fam, custom) => fam === '?' ? '#6b7280' : !custom ? '#dc2626' : (pal.has(fam) || pal.set(fam, PAL[pal.size % PAL.length]), pal.get(fam));
const srcName = h => !h ? '?' : h.isInline ? 'inline <style> trong HTML' : (h.sourceURL || '?').replace(/^https?:\/\/[^/]+/, '').split('?')[0];

// Thứ tự cascade: các rule theo thứ tự CDP trả về, inline style sau cùng; khai báo !important thắng khai báo thường.
function winner(rules, inline, tag) {
  const c = [];
  for (const m of rules || []) {
    const r = m.rule; if (r.origin !== 'regular') continue;
    for (const x of r.style.cssProperties || []) if ((x.name === 'font-family' || x.name === 'font') && !x.disabled && x.value && x.text !== undefined)
      c.push({ value: x.value.replace(/\s*!important/, ''), imp: !!x.important || /!important/.test(x.value), selector: r.selectorList.text + tag, sheet: srcName(sheets.get(r.styleSheetId)) });
  }
  for (const x of (inline && inline.cssProperties) || []) if ((x.name === 'font-family' || x.name === 'font') && !x.disabled && x.value && x.text !== undefined)
    c.push({ value: x.value.replace(/\s*!important/, ''), imp: !!x.important, selector: 'style=""' + tag, sheet: 'inline style="" trên thẻ' });
  if (!c.length) return null;
  const imp = c.filter(x => x.imp);
  const w = imp.length ? imp[imp.length - 1] : c[c.length - 1];
  return { ...w, value: w.value + (w.imp ? ' !important' : '') };
}
function findDecl(ms) {
  const own = winner(ms.matchedCSSRules, ms.inlineStyle, '');
  if (own) return own;
  for (const inh of ms.inherited || []) { const w = winner(inh.matchedCSSRules, inh.inlineStyle, ' (thừa kế)'); if (w) return w; }
  return { value: '(mặc định trình duyệt)', selector: '-', sheet: '-' };
}

const report = [];
for (const url of urls) {
  const slug = url.replace(/^https?:\/\/[^/]+/, '').replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home';
  await send('Page.navigate', { url: o.src ? url + (url.includes('?') ? '&' : '?') + 'LSCWP_CTRL=before_optm' : url });
  await sleep(6000);
  await ev('window.dispatchEvent(new Event("touchstart"));document.dispatchEvent(new MouseEvent("mousemove"))');
  for (let k = 1; k <= 6; k++) { await ev(`window.scrollTo(0, document.body.scrollHeight*${k}/6)`); await sleep(700); }
  await ev('window.scrollTo(0,0)'); await sleep(1200);
  const els = await ev(`(() => {
    const SKIP = /font ?awesome|fa-|eicons|slick|icomoon|dashicons/i, out = [];
    let i = 0;
    for (const e of document.querySelectorAll('body *')) {
      if (i >= 3000) break;
      if (/^(SCRIPT|STYLE|NOSCRIPT|svg|path|IFRAME|TEXTAREA|SELECT|OPTION)$/i.test(e.tagName)) continue;
      const txt = [...e.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim().length > 1).map(n => n.textContent.trim()).join(' ');
      if (!txt) continue;
      const cs = getComputedStyle(e); if (SKIP.test(cs.fontFamily)) continue;
      if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
      const r = e.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue;
      e.setAttribute('data-fm', i);
      const cls = (typeof e.className === 'string' ? e.className : '').trim().split(/\\s+/).filter(c => !/^elementor-(element|widget)-[a-z0-9]{6,}|^e-con|^ue-/.test(c)).slice(0, 2).join('.');
      out.push({ i, tag: e.tagName.toLowerCase(), cls, text: txt.replace(/\\s+/g, ' ').slice(0, 70), fam: cs.fontFamily, w: cs.fontWeight, size: cs.fontSize, y: Math.round(r.top + scrollY), h: Math.round(r.height) });
      i++;
    }
    return out;
  })()`);
  // Mẫu: tối đa 2 phần tử cho mỗi chữ ký (font khai báo + thẻ + class), tổng tối đa 180.
  const bySig = new Map();
  for (const e of els) { const sig = e.fam + '|' + e.tag + '|' + e.cls; if (!bySig.has(sig)) bySig.set(sig, []); if (bySig.get(sig).length < 2) bySig.get(sig).push(e); }
  const sample = [...bySig.values()].flat().slice(0, 180);
  const root = (await send('DOM.getDocument', { depth: 0 })).result.root.nodeId;
  const sigInfo = new Map();
  for (const e of sample) {
    const q = await send('DOM.querySelector', { nodeId: root, selector: `[data-fm="${e.i}"]` });
    const nodeId = q.result?.nodeId; if (!nodeId) continue;
    const pf = await send('CSS.getPlatformFontsForNode', { nodeId });
    const fonts = (pf.result?.fonts || []).sort((a, b) => b.glyphCount - a.glyphCount);
    const ms = (await send('CSS.getMatchedStylesForNode', { nodeId })).result || {};
    const d = findDecl(ms);
    const rendered = fonts[0] ? fonts[0].familyName.replace(/ Font$/, '') : '?';
    const sig = e.fam + '|' + e.tag + '|' + e.cls;
    if (!sigInfo.has(sig)) sigInfo.set(sig, { rendered, custom: fonts[0]?.isCustomFont, decl: d });
  }
  // Nhóm theo font thật sự vẽ + giá trị khai báo + file nguồn.
  const groups = new Map();
  for (const e of els) {
    const s = sigInfo.get(e.fam + '|' + e.tag + '|' + e.cls); if (!s) continue;
    const key = s.rendered + '||' + s.decl.value + '||' + s.decl.sheet;
    if (!groups.has(key)) groups.set(key, { rendered: s.rendered, custom: s.custom, declared: s.decl.value, sheet: s.decl.sheet, selectors: new Set(), styles: new Set(), count: 0, examples: [] });
    const g = groups.get(key); g.count++; g.selectors.add(s.decl.selector); g.styles.add(`${e.w} ${e.size}`);
    if (g.examples.length < 12 && e.h < 400 && !g.examples.some(x => x.tag === e.tag && x.cls === e.cls)) g.examples.push(e);
    e.rendered = s.rendered; e.custom = s.custom;
  }
  // Tô viền theo font thật sự vẽ.
  const paint = els.filter(e => e.rendered).map(e => [e.i, color(e.rendered, e.custom)]);
  await ev(`(() => { for (const [i, c] of ${JSON.stringify(paint)}) { const e = document.querySelector('[data-fm="'+i+'"]'); if (e) { e.style.outline = '2px solid ' + c; e.style.outlineOffset = '1px'; } } })()`);
  await ev('window.scrollTo(0,0)'); await sleep(400);
  const ov = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70 });
  fs.writeFileSync(`${outDir}/${slug}__overview.jpg`, Buffer.from(ov.result.data, 'base64'));
  const gl = [...groups.values()].sort((a, b) => b.count - a.count);
  let gi = 0;
  for (const g of gl) {
    gi++;
    const ex = g.examples.slice().sort((a, b) => parseFloat(b.size) - parseFloat(a.size) || a.y - b.y)[0];
    const clip = await ev(`(() => { const e = document.querySelector('[data-fm="${ex.i}"]'); if (!e) return null;
      e.scrollIntoView({ block: 'center' });
      document.querySelectorAll('.fm-badge').forEach(b => b.remove());
      const r = e.getBoundingClientRect(); const b = document.createElement('div'); b.className = 'fm-badge';
      b.textContent = ${JSON.stringify(g.rendered)} + ' · ' + getComputedStyle(e).fontWeight + ' · ' + getComputedStyle(e).fontSize;
      b.style.cssText = 'position:absolute;z-index:2147483647;background:${color(g.rendered, g.custom)};color:#fff;font:600 12px/1.4 monospace;padding:2px 6px;border-radius:3px;left:' + (r.left + scrollX) + 'px;top:' + Math.max(0, r.top + scrollY - 22) + 'px';
      document.body.appendChild(b);
      const x = Math.max(0, r.left - 24), y = Math.max(0, r.top - 34);
      return { x: x + scrollX, y: y + scrollY, width: Math.min(innerWidth - x, Math.max(r.width + 48, 480)), height: Math.min(innerHeight - y, Math.max(Math.min(r.height, 360) + 60, 120)) };
    })()`);
    if (!clip) continue;
    await sleep(500);
    const shot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 75, clip: { ...clip, scale: 1 } });
    g.img = `${slug}__g${gi}.jpg`;
    fs.writeFileSync(`${outDir}/${g.img}`, Buffer.from(shot.result.data, 'base64'));
  }
  report.push({ url, slug, overview: `${slug}__overview.jpg`, elements: els.length, groups: gl.map(g => ({ ...g, selectors: [...g.selectors].slice(0, 6), styles: [...g.styles].slice(0, 8) })) });
  console.log(url, 'phần tử', els.length, '| nhóm', gl.map(g => `${g.rendered}(${g.count}) ← ${g.sheet}`).join('; '));
}
fs.writeFileSync(`${outDir}/fontmap.json`, JSON.stringify(report, null, 1));
await tab.close();
process.exit(0);
