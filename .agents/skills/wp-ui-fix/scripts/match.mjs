// Tìm rule CSS thắng cho MỌI thuộc tính của một phần tử, kèm file nguồn, dòng, specificity, !important và mọi bản sao bị đè.
// node match.mjs <url> <selector> [--props font-size,margin] [--all] [--width 390] [--widths 390,1366] [--nth 0]
//                [--state hover|focus|active|visited] [--ua] [--css file] [--json] [--out file] [--resolve host=ip] [--cookie n=v] [--wait ms]
// Chỉ đọc: tải trang, đọc CSSOM qua CDP, không bấm, không gửi form. Chặn request tracking (GA, GTM, Pixel, Hotjar, Clarity).
// --css: chèn file CSS thử vào trang sau khi tải (chỉ trong Chrome của lượt đo), rồi báo rule thử thắng hay thua ở từng thuộc tính.
// Staging có Basic Auth: đặt WEB_QA_AUTH="user:pass" (chỉ gửi tới host của URL). Dùng Chrome cài sẵn hoặc CHROME_BIN.
// Mã thoát: 0 xong · 1 lỗi chạy hoặc selector không khớp phần tử nào · 2 sai cú pháp lệnh · 3 có --css và CSS thử thua ở ít nhất một thuộc tính.
// Phụ thuộc: ../../web-qa-gate/scripts/_cdp.mjs (skill web-qa-gate nằm cạnh wp-ui-fix).
import fs from 'node:fs';
import {specificity, resolveProps, declsFromStyle, fmtSpec} from './_cascade.mjs';

const HELP = `match.mjs — rule CSS thắng cho từng thuộc tính của một phần tử

Dùng:  node match.mjs <url> <selector> [tuỳ chọn]

  --props a,b      chỉ in các thuộc tính này (mặc định: mọi thuộc tính có khai báo rõ)
  --all            in cả longhand do shorthand sinh ra (margin-top từ margin)
  --width N        một bề rộng (mặc định 1366). --widths 390,1366 đo nhiều bề rộng
  --nth N          phần tử thứ N trong các phần tử khớp selector (mặc định 0)
  --state S        ép :hover, :focus, :active hoặc :visited trước khi đọc
  --ua             tính cả CSS mặc định của trình duyệt
  --css FILE       chèn CSS thử sau khi tải trang, báo rule thử thắng hay thua (không ghi gì lên site)
  --json           in JSON thay cho bảng;  --out FILE  ghi JSON ra file
  --resolve h=ip   ánh xạ host tới IP (staging qua tunnel);  --cookie n=v  gắn cookie
  --wait MS        chờ sau khi tải (mặc định 2500)
  --help           in trợ giúp

Mã thoát: 0 xong · 1 lỗi chạy hoặc selector không khớp · 2 sai cú pháp · 3 CSS thử (--css) thua ở ít nhất một thuộc tính.`;

const argv = process.argv.slice(2);
if (argv.includes('--help') || argv.includes('-h')) { console.log(HELP); process.exit(0); }

let cdp;
try { cdp = await import('../../web-qa-gate/scripts/_cdp.mjs'); }
catch (e) { console.error('Không nạp được web-qa-gate/scripts/_cdp.mjs: cần skill web-qa-gate cạnh wp-ui-fix.\n' + e.message); process.exit(1); }
const {args, openTab, sleep, MUA, DUA} = cdp;

const o = args(argv, ['all', 'ua', 'json']);
const [url, selector] = o._;
if (!url || !selector || !/^https?:\/\//.test(url)) { console.error('Thiếu <url> (http hoặc https) hoặc <selector>. Chạy --help.'); process.exit(2); }
const widths = String(o.widths || o.width || '1366').split(',').map(Number);
if (widths.some(w => !(w >= 200 && w <= 4000))) { console.error('--width phải nằm trong 200–4000.'); process.exit(2); }
if (o.state && !['hover', 'focus', 'active', 'visited'].includes(o.state)) { console.error('--state chỉ nhận hover, focus, active, visited.'); process.exit(2); }
const nth = +(o.nth || 0), wait = +(o.wait || 2500);
const propsFilter = o.props ? new Set(String(o.props).split(',').map(s => s.trim()).filter(Boolean)) : null;
let trialCss = null;
if (o.css) {
  try { trialCss = fs.readFileSync(String(o.css), 'utf8'); } catch (e) { console.error('Không đọc được --css: ' + e.message); process.exit(2); }
}
const TRIAL = 'CSS thử (--css ' + String(o.css || '').split('/').pop() + ')';
const BLOCK = ['*googletagmanager.com*', '*google-analytics.com*', '*connect.facebook.net*', '*facebook.com/tr*', '*hotjar.com*', '*clarity.ms*', '*doubleclick.net*', '*guest.vary.php*'];

const strip = u => (u || '').replace(/^https?:\/\/[^/]+/, '').replace(/^file:\/\//, '').split('?')[0];
const hintSource = p => /\/litespeed\/(css|ucss)\/|\/wp-content\/cache\//.test(p) ? 'file CSS gộp do cache sinh ra. Tìm file nguồn bằng css_sources.sh rồi sửa nguồn.'
  : /ccss|critical/i.test(p) ? 'critical CSS. Sửa mọi bản theo template, dựng lại critical CSS nếu đổi nguồn.'
  : /elementor\/css\/post-/.test(p) ? 'CSS do Elementor sinh. Sửa trong Elementor hoặc kit, không sửa file sinh.' : null;

const tab = await openTab({host: new URL(url).host, resolve: o.resolve, cookie: o.cookie, block: BLOCK});
const {send, evalv, events, close} = tab;
const results = [];
let failed = false, trialLost = false;
try {
  await send('Page.enable'); await send('DOM.enable'); await send('CSS.enable');
  for (const W of widths) {
    const mob = W < 800, H = mob ? 800 : 900;
    await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: 1, mobile: false});
    await send('Emulation.setTouchEmulationEnabled', {enabled: mob});
    await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
    events.length = 0;
    await send('Page.navigate', {url});
    for (let i = 0; i < 60 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
    await sleep(wait);
    const trialIds = new Set();
    if (trialCss !== null) {
      const before = new Set(events.filter(e => e.method === 'CSS.styleSheetAdded').map(e => e.params.header.styleSheetId));
      await evalv(`(()=>{const s=document.createElement('style');s.id='wp-ui-fix-thu';s.textContent=${JSON.stringify(trialCss)};document.head.appendChild(s);return 1})()`);
      await sleep(300);
      for (const e of events) if (e.method === 'CSS.styleSheetAdded' && !before.has(e.params.header.styleSheetId)) trialIds.add(e.params.header.styleSheetId);
    }
    const sheets = new Map();
    for (const e of events) if (e.method === 'CSS.styleSheetAdded') sheets.set(e.params.header.styleSheetId, e.params.header);
    const info = await evalv(`(()=>{const l=[...document.querySelectorAll(${JSON.stringify(selector)})];const e=l[${nth}];if(!e)return {count:l.length};
      const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {count:l.length,tag:e.tagName.toLowerCase(),cls:String(e.className).slice(0,80),id:e.id,w:Math.round(r.width),h:Math.round(r.height),
      text:(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,60),computed:{'font-size':s.fontSize,'line-height':s.lineHeight,'font-weight':s.fontWeight,color:s.color,'font-family':s.fontFamily.slice(0,60)}}})()`);
    if (!info || !info.tag) { results.push({width: W, error: `selector khớp ${info ? info.count : 0} phần tử, không có phần tử thứ ${nth}`}); failed = true; continue; }
    const doc = await send('DOM.getDocument', {depth: 0});
    const q = await send('DOM.querySelectorAll', {nodeId: doc.result.root.nodeId, selector});
    const nodeId = q.result && q.result.nodeIds && q.result.nodeIds[nth];
    if (!nodeId) { results.push({width: W, error: 'DOM.querySelectorAll không trả node'}); failed = true; continue; }
    if (o.state) await send('CSS.forcePseudoState', {nodeId, forcedPseudoClasses: [o.state]});
    const ms = (await send('CSS.getMatchedStylesForNode', {nodeId})).result || {};
    const comp = Object.fromEntries((((await send('CSS.getComputedStyleForNode', {nodeId})).result || {}).computedStyle || []).map(p => [p.name, p.value]));
    const decls = [];
    let order = 0;
    for (const m of ms.matchedCSSRules || []) {
      const r = m.rule;
      const origin = r.origin === 'regular' ? 'author' : r.origin === 'user-agent' ? 'ua' : null;
      if (!origin || (origin === 'ua' && !o.ua)) { order++; continue; }
      const sels = r.selectorList.selectors.map(s => s.text);
      const idx = (m.matchingSelectors && m.matchingSelectors.length) ? m.matchingSelectors : sels.map((_, i) => i);
      const matched = idx.map(i => sels[i]).filter(Boolean);
      const spec = matched.map(specificity).reduce((p, c) => (c[0] - p[0] || c[1] - p[1] || c[2] - p[2]) > 0 ? c : p, [0, 0, 0]);
      const sh = r.styleSheetId ? sheets.get(r.styleSheetId) : null;
      const source = origin === 'ua' ? 'trình duyệt' : trialIds.has(r.styleSheetId) ? TRIAL : !sh ? '?' : sh.isInline ? 'inline <style> trong HTML' : strip(sh.sourceURL) || '?';
      const lineBase = sh && sh.isInline ? sh.startLine : 0;
      const media = (r.media || []).map(x => x.text).join(' and ') || null;
      const layer = (r.layers && r.layers.length) ? r.layers.map(l => l.text).join('.') : null;
      decls.push(...declsFromStyle(r.style, {selector: matched.join(', ') || r.selectorList.text, spec, order: order++, origin, inline: false, layer, media, source, lineBase}));
    }
    decls.push(...declsFromStyle(ms.inlineStyle, {selector: 'style=""', spec: [1, 0, 0], order: order++, origin: 'author', inline: true, layer: null, media: null, source: 'thuộc tính style="" trên thẻ', lineBase: 0}));
    const fix = d => {
      const line = d.range && !d.inline ? d.range.startLine + d.lineBase + 1 : null, col = d.range && !d.inline ? d.range.startColumn + 1 : null;
      const {range, lineBase, order: _o, ...rest} = d;
      return {...rest, line, col};
    };
    const props = resolveProps(decls).filter(p => propsFilter ? propsFilter.has(p.prop) : (o.all || !p.winner.implicit));
    const out = props.map(p => ({
      prop: p.prop, computed: comp[p.prop] ?? null, winner: fix(p.winner), overridden: p.overridden.map(fix), need: p.need,
      layerUncertain: p.layerUncertain, hint: hintSource(p.winner.source || ''),
    }));
    const trial = trialCss === null ? null : {
      file: String(o.css),
      wins: out.filter(p => p.winner.source === TRIAL).map(p => p.prop),
      loses: out.filter(p => p.winner.source !== TRIAL && p.overridden.some(d => d.source === TRIAL)).map(p => p.prop),
    };
    if (trial && trial.loses.length) trialLost = true;
    results.push({width: W, url, selector, element: info, state: o.state || null, properties: out, trial, hiddenLonghands: o.all || propsFilter ? 0 : resolveProps(decls).filter(p => p.winner.implicit).length});
  }
} catch (e) {
  console.error('Lỗi: ' + (e && e.message || e));
  failed = true;
} finally {
  await close();
}

const loc = d => d.line ? `${d.source}:${d.line}${d.col ? ':' + d.col : ''}` : d.source;
const val = d => d.value + (d.important ? ' !important' : '') + (d.media ? `  @media ${d.media}` : '');
if (o.out) fs.writeFileSync(o.out, JSON.stringify({generated: new Date().toISOString(), results}, null, 1));
if (o.json) console.log(JSON.stringify({results}, null, 1));
else for (const r of results) {
  console.log(`\n=== ${r.width}px — ${selector}`);
  if (r.error) { console.log('LỖI: ' + r.error); continue; }
  const e = r.element;
  console.log(`Phần tử: <${e.tag}${e.id ? '#' + e.id : ''}${e.cls ? ' class="' + e.cls + '"' : ''}> ${e.w}×${e.h}px, khớp ${e.count} phần tử, "${e.text}"`);
  console.log(`Tính ra: ${Object.entries(e.computed).map(([k, v]) => `${k}=${v}`).join(' · ')}`);
  for (const p of r.properties) {
    const w = p.winner;
    console.log(`\n${p.prop}: ${val(w)}   [tính ra ${p.computed}]${w.implicit ? '  (từ shorthand)' : ''}`);
    console.log(`  thắng: ${w.selector} ${fmtSpec(w.spec)}${w.inline ? ' inline' : ''}  ← ${loc(w)}`);
    if (p.hint) console.log(`  lưu ý: ${p.hint}`);
    if (p.layerUncertain) console.log('  lưu ý: nhiều @layer có tên, thứ tự giữa các layer chưa được kiểm.');
    for (const d of p.overridden) console.log(`  bản sao bị đè: ${val(d)}  ${d.selector} ${fmtSpec(d.spec)}  ← ${loc(d)}  (${d.why})`);
    console.log(`  muốn đè: ${p.need}`);
  }
  if (r.hiddenLonghands) console.log(`\n(${r.hiddenLonghands} longhand do shorthand sinh ra bị ẩn; dùng --all để xem)`);
  if (!r.properties.length) console.log('Không có khai báo nào khớp bộ lọc.');
  if (r.trial) console.log(`\nCSS thử: thắng ${r.trial.wins.join(', ') || '(không thuộc tính nào)'} · thua ${r.trial.loses.join(', ') || '(không thuộc tính nào)'}`);
}
process.exit(failed ? 1 : trialLost ? 3 : 0);
