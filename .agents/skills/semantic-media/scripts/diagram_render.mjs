// Render sơ đồ HTML → PNG 2x → PNG/WebP đúng kích thước spec, kèm kiểm lỗi bố cục và chữ.
// ROOT=<thư mục gốc phục vụ HTTP> [SRC_SUB=src] [SPECS=<ROOT>/specs.json] [OUT=<ROOT>/out] [FONTS="800 40px Montserrat;600 20px Inter"] node diagram_render.mjs [ID ...]
// specs.json: {"items":[{"id","size_px":"1200x675","export":{"file_name","max_kb"},"json_prompt":{headline,subheadline,elements,typography}}]}
// Trang HTML đặt class .canvas cho khung, .logo cho logo, và gán window.__ready = true khi font, icon, ảnh đã tải.
// Kết quả: OUT/<ID>.png, <file_name>.webp, <ID>.check.json. Mã thoát 1 nếu có lỗi.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {openTab, sleep} from '../../wp-pagespeed/scripts/_chrome.mjs';
import {judgeMinFont} from './diagram_checks.mjs';

if (process.argv.slice(2).some(a => a === '--help' || a === '-h')) {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').filter(l => l.startsWith('//')).slice(0, 5).map(l => l.slice(3)).join('\n'));
  console.log('Cỡ chữ nhỏ nhất không đo được (không có hộp chữ) là lỗi, không phải đạt. Mã thoát: 0 đạt hết, 1 có lỗi.');
  process.exit(0);
}

const ROOT = path.resolve(process.env.ROOT || '.');
const SUB = process.env.SRC_SUB || 'src', SRC = path.join(ROOT, SUB), OUT = path.resolve(process.env.OUT || path.join(ROOT, 'out'));
const SPECS = JSON.parse(fs.readFileSync(process.env.SPECS || path.join(ROOT, 'specs.json'), 'utf8')).items;
const FONTS = (process.env.FONTS || '').split(';').map(s => s.trim()).filter(Boolean);
const TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.json': 'application/json'};
fs.mkdirSync(OUT, {recursive: true});

const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream'}); fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

// Chuỗi bắt buộc phải xuất hiện nguyên văn (NFC) trên ảnh: tiêu đề, phụ đề, nhãn, câu hỏi, chip.
function expected(spec) {
  const jp = spec.json_prompt || {}, out = [];
  const t = v => typeof v === 'string' ? v : v && v.text;
  if (t(jp.headline)) out.push(t(jp.headline));
  if (t(jp.subheadline)) out.push(t(jp.subheadline));
  for (const e of jp.elements || []) {
    for (const k of ['label', 'text', 'question', 'header']) if (typeof e[k] === 'string') out.push(...e[k].split(' · '));
    for (const k of ['items', 'chips', 'terms', 'steps']) if (Array.isArray(e[k])) out.push(...e[k].filter(x => typeof x === 'string'));
  }
  return [...new Set(out.map(s => s.normalize('NFC').trim()).filter(Boolean))];
}

const CHECK = `(() => {
  const W = innerWidth, H = innerHeight, bad = [];
  const logo = document.querySelector('.logo'), L = logo && logo.getBoundingClientRect();
  const texts = [...document.querySelectorAll('.canvas *')].filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
  const boxes = [];
  for (const e of texts) {
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e), name = e.textContent.trim().slice(0, 40);
    if (r.width === 0 || cs.visibility === 'hidden') continue;
    if (r.left < -1 || r.top < -1 || r.right > W + 1 || r.bottom > H + 1) bad.push('ra ngoài canvas: ' + name);
    if (e.scrollWidth > e.clientWidth + 2 && cs.overflow !== 'visible') bad.push('tràn ngang: ' + name);
    if (e.scrollHeight > e.clientHeight + 2 && cs.overflow !== 'visible') bad.push('tràn dọc: ' + name);
    if (L && r.left < L.right && r.right > L.left && r.top < L.bottom && r.bottom > L.top) bad.push('đè logo: ' + name);
    // Span inline (từ ghép .nw) nằm trong khối cha: hộp nội dung cao hơn line-height nên không so chồng chữ.
    if (cs.display !== 'inline') boxes.push({r, name, e, fs: parseFloat(cs.fontSize)});
  }
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
    const ix = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left), iy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (ix > 2 && iy > 2) bad.push('chữ chồng nhau: ' + a.name + ' | ' + b.name);
  }
  const fonts = Object.fromEntries(${JSON.stringify(FONTS)}.map(f => [f, document.fonts.check(f, 'Việt')]));
  if (Object.values(fonts).some(v => !v)) bad.push('font chưa tải: ' + JSON.stringify(fonts));
  // Đo mọi phần tử chữ nhìn thấy, kể cả span inline. Không có phần tử nào thì trả null, không trả Infinity.
  const sizes = texts.filter(e => e.getBoundingClientRect().width > 0 && getComputedStyle(e).visibility !== 'hidden').map(e => parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite);
  const minFont = sizes.length ? Math.min(...sizes) : null;
  return {bad, minFont, text: document.querySelector('.canvas').innerText};
})()`;

const ids = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(SRC).filter(f => f.endsWith('.html')).map(f => f.replace('.html', ''));
const tab = await openTab();
await tab.send('Page.enable');
let fail = 0;
for (const id of ids) {
  const spec = SPECS.find(s => s.id === id.replace(/-v\d+$/, ''));
  if (!spec) { console.log(id, 'không có spec'); fail++; continue; }
  const [W, H] = spec.size_px.split('x').map(Number);
  await tab.send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: 2, mobile: false});
  await tab.send('Page.navigate', {url: `http://127.0.0.1:${port}/${SUB}/${id}.html?t=${Date.now()}`});
  let ok = false;
  for (let i = 0; i < 100 && !ok; i++) { await sleep(150); ok = await tab.evalv('window.__ready === true'); }
  if (!ok) { console.log(id, 'trang không báo __ready'); fail++; continue; }
  await sleep(200);
  const res = await tab.evalv(CHECK);
  const text = (res.text || '').normalize('NFC').replace(/\s+/g, ' ');
  const missing = expected(spec).filter(s => !text.includes(s.replace(/\s+/g, ' ')));
  const minText = parseInt(String(spec.json_prompt?.typography?.min_text_height || '0'), 10);
  const fontVerdict = judgeMinFont(res.minFont, minText);
  if (fontVerdict.issue) res.bad.push(fontVerdict.issue);
  const shot = await tab.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: false});
  const big = path.join(OUT, `${id}@2x.png`);
  fs.writeFileSync(big, Buffer.from(shot.result.data, 'base64'));
  const webpName = id.endsWith(spec.id) ? spec.export.file_name : spec.export.file_name.replace('.webp', id.slice(spec.id.length) + '.webp');
  const kb = execFileSync('/usr/bin/python3', ['-c', `
import sys
from PIL import Image
big, png, webp, w, h, maxkb = sys.argv[1:7]
im = Image.open(big).convert('RGB').resize((int(w), int(h)), Image.LANCZOS)
im.save(png, optimize=True)
q = 90
while True:
    im.save(webp, 'WEBP', quality=q, method=6)
    import os; kb = os.path.getsize(webp) / 1024
    if kb <= float(maxkb) or q <= 60: break
    q -= 5
print(f'{kb:.0f}KB q{q}')`, big, path.join(OUT, `${id}.png`), path.join(OUT, webpName), String(W), String(H), String(spec.export.max_kb)]).toString().trim();
  const report = {id, size: spec.size_px, webp: webpName, webp_kb: kb, min_font: fontVerdict.measured ? res.minFont : null, min_font_measured: fontVerdict.measured, issues: res.bad, missing_strings: missing};
  fs.writeFileSync(path.join(OUT, `${id}.check.json`), JSON.stringify(report, null, 1));
  const n = res.bad.length + missing.length;
  if (n) fail++;
  console.log(`${id} ${spec.size_px} ${kb} ${fontVerdict.label} ${n ? 'LỖI ' + n : 'đạt'}`);
  for (const b of res.bad) console.log('   -', b);
  for (const m of missing) console.log('   - thiếu chuỗi:', m);
}
await tab.close(); server.close();
process.exit(fail ? 1 : 0);
