// Đo trang tham chiếu trước khi vẽ mockup (wp-theme-build Bước 1b). Chỉ đọc: không bấm, không gửi form, chặn tracking.
// node measure_ref.mjs measure <url> [--widths 1440,390] [--scroll 6] [--out ref.json] [--wait ms] [--block mẫu,mẫu]
// node measure_ref.mjs vi-subset "<Font A>,<Font B>" [--css file.css]
// node measure_ref.mjs fonts --ref ref.json --fonts "A,B,C" --out so-font.html [--shot so-font.png] [--width 1440] [--no-google]
// measure: cột chữ, font, cỡ chữ, line-height, H1, H2, markup mục lục, nút mở mục lục; cuộn bằng wheel (trang cuộn mượt bỏ qua scrollTo),
//          rồi liệt kê phần tử dính (header, CTA, mục lục). vi-subset: hỏi fonts.googleapis.com/css2 với UA Chrome, báo font thiếu subset vietnamese.
// fonts: dựng trang so tối đa 6 bộ font trên cùng một đoạn văn, theo cột chữ và cỡ chữ đo được. --shot chụp trang đó.
// Mã thoát: 0 xong · 1 không đo được cột chữ hoặc có font thiếu subset vietnamese · 2 sai tham số.
// Dùng skills/web-qa-gate/scripts/_cdp.mjs, nên skill web-qa-gate phải nằm cạnh.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {args, openTab, sleep, setViewport, loadUrl, DUA} from '../../web-qa-gate/scripts/_cdp.mjs';

const TRACK = ['*googletagmanager.com*', '*google-analytics.com*', '*doubleclick.net*', '*facebook.net*', '*connect.facebook*',
  '*script.google.com*', '*clarity.ms*', '*hotjar*', '*tiktok*'];
const SAMPLE = 'Đoạn văn mẫu để so font tiếng Việt. Chữ có dấu chồng như ặ, ẫ, ỡ, ữ, ự, ỳ, Ổ, Ữ phải rõ và không chạm dòng trên. '
  + 'Số 0123456789, dấu “ngoặc kép” và (ngoặc đơn) cũng cần dễ đọc ở cỡ chữ thân bài.';
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const die = (msg, code = 2) => { console.error(msg); process.exit(code); };

// Chạy trong trang. Cột chữ = nhóm <p> dài (từ 80 ký tự) chung một phần tử cha, nhóm nhiều chữ nhất.
// Mục lục = nhóm từ 3 link tới id có thật, gom theo khung gần nhất (nav, aside, details, [class*=toc]).
const PROBE = `(() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const sel = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; const c = [...e.classList].slice(0, 2); if (c.length) s += '.' + c.join('.'); return s; };
  const pos = e => { for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const p = getComputedStyle(n).position; if (p === 'fixed' || p === 'sticky') return p; } return 'static'; };
  const font = e => { const s = getComputedStyle(e), fs = parseFloat(s.fontSize), lh = s.lineHeight === 'normal' ? null : parseFloat(s.lineHeight);
    return {family: s.fontFamily, size: fs, line_height: lh, lh_ratio: lh ? +(lh / fs).toFixed(2) : null, weight: s.fontWeight}; };
  const groups = new Map();
  for (const p of document.querySelectorAll('p')) {
    if (!vis(p) || pos(p) !== 'static' || (p.innerText || '').trim().length < 80) continue;
    groups.set(p.parentElement, (groups.get(p.parentElement) || []).concat(p));
  }
  let best = null, bestLen = 0;
  for (const arr of groups.values()) { const n = arr.reduce((a, p) => a + p.innerText.length, 0); if (n > bestLen) { best = arr; bestLen = n; } }
  let col = null;
  if (best) {
    const ws = best.map(p => p.getBoundingClientRect().width).sort((a, b) => a - b);
    const cpl = best.map(p => { const lh = parseFloat(getComputedStyle(p).lineHeight), n = lh ? Math.round(p.getBoundingClientRect().height / lh) : 0; return n > 1 ? p.innerText.length / n : 0; }).filter(Boolean);
    col = {container: sel(best[0].parentElement), width: Math.round(ws[Math.floor(ws.length / 2)]), left: Math.round(best[0].getBoundingClientRect().left),
      paragraphs: best.length, chars_per_line: cpl.length ? Math.round(cpl.reduce((a, b) => a + b) / cpl.length) : null, font: font(best[0])};
  }
  const links = [...document.querySelectorAll('a[href*="#"]')].filter(a => { const h = a.getAttribute('href'), id = decodeURIComponent(h.split('#')[1] || '');
    return id && document.getElementById(id) && (h.startsWith('#') || a.pathname === location.pathname); });
  const tg = new Map();
  for (const a of links) { const box = a.closest('[class*=toc],[id*=toc],nav,aside,details') || a.closest('ol,ul'); if (box) tg.set(box, (tg.get(box) || []).concat(a)); }
  const cand = [...tg.entries()].filter(([, a]) => a.length >= 3).sort((x, y) => (vis(y[0]) - vis(x[0])) || (y[1].length - x[1].length));
  let toc = null;
  if (cand.length) {
    const [box, ls] = cand[0], chain = [];
    for (let n = ls[0]; n && n !== box.parentElement; n = n.parentElement) chain.unshift(n.tagName.toLowerCase() + (n.classList[0] ? '.' + n.classList[0] : ''));
    const depth = Math.max(...ls.map(a => { let d = 0; for (let n = a; n && n !== box; n = n.parentElement) if (/^(OL|UL)$/.test(n.tagName)) d++; return d; }));
    const btn = [...document.querySelectorAll('button,summary,[aria-expanded],[aria-controls]')].filter(vis).find(b => {
      const t = document.getElementById(b.getAttribute('aria-controls') || '');
      return (t && (t.contains(box) || box.contains(t))) || /mục lục|nội dung bài|table of contents|contents|on this page/i.test((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')); });
    const r = box.getBoundingClientRect();
    toc = {box: sel(box), markup: chain.join(' > '), links: ls.length, depth, details: !!(box.closest('details') || box.querySelector('details')), visible: vis(box),
      position: pos(box), top: Math.round(r.top), left: Math.round(r.left), width: Math.round(r.width),
      toggle: btn ? sel(btn) + ' "' + ((btn.innerText || btn.getAttribute('aria-label') || '').trim().slice(0, 30)) + '"' : null};
  }
  const h = t => { const e = [...document.querySelectorAll(t)].find(vis); return e ? Object.assign({text: e.innerText.trim().slice(0, 60)}, font(e)) : null; };
  return {title: document.title, col, h1: h('h1'), h2: h('h2'), toc, scrollY: Math.round(scrollY)};
})()`;

// Phần tử fixed hoặc sticky đang hiện trong khung nhìn (header, CTA dính, nút mục lục). Bỏ phần tử con của phần tử đã liệt kê và lớp phủ gần cả màn.
const STUCK = `(() => {
  const out = [], seen = [];
  for (const e of document.querySelectorAll('body *')) {
    const s = getComputedStyle(e); if (s.position !== 'fixed' && s.position !== 'sticky') continue;
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1 || s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) continue;
    if (r.bottom <= 0 || r.top >= innerHeight || r.height > innerHeight * 0.9 || seen.some(p => p.contains(e))) continue;
    seen.push(e);
    let id = e.tagName.toLowerCase(); if (e.id) id += '#' + e.id; if (e.classList[0]) id += '.' + e.classList[0];
    out.push({sel: id, position: s.position, top: Math.round(r.top), bottom: Math.round(innerHeight - r.bottom), height: Math.round(r.height),
      text: (e.innerText || e.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim().slice(0, 40)});
  }
  return out.slice(0, 12);
})()`;

async function wheel(tab, steps) {
  for (let i = 0; i < steps; i++) {
    await tab.send('Input.dispatchMouseEvent', {type: 'mouseWheel', x: 200, y: 300, deltaX: 0, deltaY: 600});
    await sleep(350);
  }
  await sleep(700);
}

function line(row) {
  const c = row.col, f = c && c.font, t = row.toc;
  const fam = f ? f.family.split(',')[0].replace(/["']/g, '') : '-';
  const parts = [`${row.width}px`, c ? `cột ${c.width}px (${c.paragraphs} đoạn, ~${c.chars_per_line ?? '?'} ký tự/dòng)` : 'không thấy cột chữ',
    f ? `chữ "${fam}" ${f.size}/${f.line_height ?? 'normal'} (${f.lh_ratio ?? '-'})` : '',
    row.h1 ? `H1 ${row.h1.size}` : '', row.h2 ? `H2 ${row.h2.size}` : '',
    t ? `mục lục ${t.box}: ${t.markup}, ${t.links} link, ${t.depth} cấp, ${t.visible ? t.position : 'ẩn'}${t.toggle ? ', nút ' + t.toggle : ''}` : 'không thấy mục lục'];
  const a = row.sau_cuon;
  const dinh = a.dinh.map(d => `${d.sel}${d.text ? ' "' + d.text + '"' : ''} (${d.position}, ${d.bottom <= 2 ? 'đáy' : 'đỉnh ' + d.top})`).join('; ');
  return parts.filter(Boolean).join(' · ') + `\n    sau ${a.steps} lượt wheel: scrollY ${a.scrollY}${a.toc_top != null ? ', mục lục top ' + a.toc_top : ''} · dính: ${dinh || 'không có'}`;
}

async function measure(o) {
  const url = o._[1]; if (!url) die('thiếu <url>');
  const widths = String(o.widths || '1440,390').split(',').map(Number).filter(Boolean);
  const steps = +(o.scroll ?? 6), wait = +(o.wait || 2500);
  const block = TRACK.concat(o.block ? String(o.block).split(',') : []);
  let host = null; try { host = new URL(url).host || null; } catch { die('url không hợp lệ: ' + url); }
  const tab = await openTab({host, block});
  const rows = [];
  try {
    await tab.send('Page.enable'); await tab.send('Runtime.enable');
    for (const W of widths) {
      await setViewport(tab, W);
      await loadUrl(tab, url, wait);
      const before = await tab.evalv(PROBE);
      await wheel(tab, steps);
      const after = await tab.evalv(PROBE), dinh = await tab.evalv(STUCK);
      rows.push({width: W, ...before, sau_cuon: {steps, scrollY: after.scrollY, toc_top: after.toc && after.toc.visible ? after.toc.top : null, toc_visible: after.toc ? after.toc.visible : null, dinh}});
    }
  } finally { await tab.close(); }
  const res = {url, do_luc: new Date().toISOString(), widths: rows};
  if (o.out) fs.writeFileSync(o.out, JSON.stringify(res, null, 2));
  for (const r of rows) console.log(line(r));
  return rows.every(r => r.col) ? 0 : 1;
}

async function viSubset(o) {
  const fonts = String(o._[1] || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!fonts.length) die('thiếu danh sách font');
  let css = '';
  if (o.css) { try { css = fs.readFileSync(o.css, 'utf8'); } catch { die('không đọc được ' + o.css); } }
  else for (const f of fonts) {
    const u = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(f).replace(/%20/g, '+')}&display=swap`;
    try { const r = await fetch(u, {headers: {'user-agent': DUA}}); css += r.ok ? await r.text() : ''; } catch {}
  }
  const have = new Map();
  for (const m of css.matchAll(/\/\*\s*([\w-]+)\s*\*\/\s*@font-face\s*\{([^}]*)\}/g)) {
    const fam = (m[2].match(/font-family:\s*['"]?([^;'"]+)/) || [])[1]; if (!fam) continue;
    const k = fam.trim().toLowerCase(); if (!have.has(k)) have.set(k, new Set()); have.get(k).add(m[1].toLowerCase());
  }
  let bad = 0;
  for (const f of fonts) {
    const s = have.get(f.toLowerCase());
    const ok = !!(s && s.has('vietnamese')); if (!ok) bad++;
    console.log(`${f}\t${ok ? 'có vietnamese' : s ? 'THIẾU vietnamese' : 'KHÔNG THẤY font'}\t${s ? [...s].join(',') : '-'}`);
  }
  return bad ? 1 : 0;
}

async function fonts(o) {
  if (!o.ref || !o.fonts || !o.out) die('cần --ref, --fonts, --out');
  const list = String(o.fonts).split(',').map(s => s.trim()).filter(Boolean);
  if (!list.length || list.length > 6) die(`cần 1–6 font, đang có ${list.length}`);
  let ref; try { ref = JSON.parse(fs.readFileSync(o.ref, 'utf8')); } catch { die('không đọc được ' + o.ref); }
  const row = (ref.widths || []).find(r => !o.width || r.width === +o.width);
  if (!row || !row.col) die('ref không có số đo cột chữ ở bề rộng này');
  const c = row.col, size = c.font.size, lh = c.font.lh_ratio || 1.6, h2 = row.h2 ? row.h2.size : Math.round(size * 1.5);
  const link = o['no-google'] ? '' : `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${list.map(f => 'family=' + encodeURIComponent(f).replace(/%20/g, '+') + ':wght@400;700').join('&')}&display=swap">`;
  const text = esc(o.text || SAMPLE);
  const html = `<!doctype html><html lang="vi"><meta charset="utf-8"><title>So font</title>${link}
<style>body{margin:24px;background:#fff;color:#1f2933;font-family:system-ui,sans-serif}.g{display:flex;flex-wrap:wrap;gap:32px}
.b{width:${c.width}px}.n{font:600 13px/1.4 system-ui,sans-serif;color:#5b6472;margin:0 0 8px}.b h2{margin:0 0 12px;font-size:${h2}px;line-height:1.3}
.b p.t{margin:0;font-size:${size}px;line-height:${lh}}</style>
<p class="n">Số đo tham chiếu: ${esc(ref.url)} ở ${row.width}px. Cột ${c.width}px, chữ ${size}px, line-height ${lh}.</p><div class="g">
${list.map(f => `<section class="b" style="font-family:'${esc(f)}',system-ui,sans-serif"><p class="n">${esc(f)}</p><h2>Tiêu đề mục: quy trình kiểm tra 5 bước</h2><p class="t">${text}</p></section>`).join('\n')}
</div></html>\n`;
  fs.writeFileSync(o.out, html);
  console.log(`Đã ghi ${o.out} (${list.length} font).`);
  if (!o.shot) return 0;
  const tab = await openTab({});
  try {
    await tab.send('Page.enable');
    await setViewport(tab, Math.max(row.width, c.width + 48));
    await loadUrl(tab, pathToFileURL(fs.realpathSync(o.out)).href, 1500);
    await tab.evalv('document.fonts.ready.then(() => 1)', true);
    const shot = await tab.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true});
    fs.writeFileSync(o.shot, Buffer.from(shot.result.data, 'base64'));
    console.log(`Đã chụp ${o.shot}.`);
  } finally { await tab.close(); }
  return 0;
}

const o = args(process.argv.slice(2), ['no-google', 'help']);
const cmd = {measure, 'vi-subset': viSubset, fonts}[o._[0]];
if (o.help || !cmd) { console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('\n').filter(l => l.startsWith('//')).slice(0, 8).map(l => l.slice(3)).join('\n')); process.exit(o.help ? 0 : 2); }
process.exit(await cmd(o));
