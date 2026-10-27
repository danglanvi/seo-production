#!/usr/bin/env node
// Đo sơ đồ SVG bằng Chrome với font thật: chữ tràn khung chứa (data-o), chữ đè chữ, cỡ chữ nhỏ nhất; chụp PNG 2x để soát.
//
//   node svg_kiem.mjs <media_plan.json> --profile <web-profile.json> [--only IMG-01] [--webp]
//
// Bản desktop đặt trong khung 760 px, bản điện thoại trong khung 320 px. Ảnh soát: <thư mục svg>/_kiem/<tên>.png, <tên>-m.png.
// --webp: xuất thêm <tên>.webp 1520 px (2x) cho Google Images hoặc ảnh chia sẻ; cần python3 + Pillow.
// Mã thoát: 0 đạt, 1 có lỗi.
import {readFileSync, writeFileSync, mkdirSync, existsSync} from 'fs';
import {dirname, resolve, join, basename} from 'path';
import {execFileSync} from 'child_process';
import {args, openTab} from './_cdp.mjs';

const o = args(process.argv.slice(2), ['webp']);
const planPath = resolve(o._[0] || ''), plan = JSON.parse(readFileSync(planPath, 'utf8'));
const prof = o.profile ? JSON.parse(readFileSync(o.profile, 'utf8')) : {};
const fontCss = (prof.media || {}).font_css || 'https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Be+Vietnam+Pro:wght@400;700&display=block';
const only = o.only ? new Set(String(o.only).split(',')) : null;
const base = dirname(planPath);
const MIN_FS = 12;

const MEASURE = `(async () => {
  await document.fonts.ready;
  const out = [];
  for (const svg of document.querySelectorAll('svg')) {
    const r = {loi: [], min_fs: 99, cao: Math.round(svg.getBoundingClientRect().height)};
    const texts = [...svg.querySelectorAll('text')];
    for (const t of texts) {
      const fs = parseFloat(t.getAttribute('font-size') || '16');
      r.min_fs = Math.min(r.min_fs, fs);
      const own = t.dataset.o && svg.querySelector('#' + CSS.escape(t.dataset.o));
      if (own) {
        const a = t.getBBox(), b = own.getBBox();
        if (a.x < b.x - 1 || a.y < b.y - 1 || a.x + a.width > b.x + b.width + 1 || a.y + a.height > b.y + b.height + 1)
          r.loi.push('tràn khung: "' + t.textContent.slice(0, 40) + '"');
      }
    }
    for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
      const a = texts[i].getBBox(), b = texts[j].getBBox();
      const ox = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x), oy = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
      if (ox > 2 && oy > 3) r.loi.push('chữ đè chữ: "' + texts[i].textContent.slice(0, 25) + '" / "' + texts[j].textContent.slice(0, 25) + '"');
    }
    if (r.min_fs < ${MIN_FS}) r.loi.push('chữ nhỏ nhất ' + r.min_fs + ' < ${MIN_FS}');
    out.push(r);
  }
  return out;
})()`;

const tab = await openTab({block: []});
let loi = 0;
const report = {};
try {
  for (const it of plan.items) {
    if (!it.svg || (only && !only.has(it.id))) continue;
    const dir = join(base, dirname(it.svg), '_kiem');
    mkdirSync(dir, {recursive: true});
    const res = {};
    for (const [k, W, f] of [['d', 760, it.svg], ['m', 320, it.svg_m]]) {
      if (!f) continue;
      const svg = readFileSync(join(base, f), 'utf8');
      const page = `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="${fontCss}">
        <style>body{margin:0;background:#fff}#k{width:${W}px;padding:16px}svg{display:block;width:100%;height:auto}</style></head>
        <body><div id="k">${svg}</div></body></html>`;
      await tab.send('Emulation.setDeviceMetricsOverride', {width: W + 32, height: 900, deviceScaleFactor: 2, mobile: false});
      await tab.send('Page.navigate', {url: 'about:blank'});
      const fr = await tab.send('Page.getFrameTree');
      await tab.send('Page.setDocumentContent', {frameId: fr.result.frameTree.frame.id, html: page});
      await new Promise(r => setTimeout(r, 900));
      const [m] = await tab.evalv(MEASURE, true);
      const box = await tab.evalv(`(() => { const r = document.querySelector('#k').getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()`);
      const shot = await tab.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true, clip: {...box, scale: 1}});
      const png = join(dir, basename(f).replace(/\.svg$/, '.png'));
      writeFileSync(png, Buffer.from(shot.result.data, 'base64'));
      res[k] = {...m, anh: png};
      loi += m.loi.length;
      console.log(`${it.id} ${k === 'd' ? 'desktop' : 'mobile '}: ${m.loi.length ? 'LOI ' + m.loi.join(' · ') : 'ok'} · cao ${m.cao}px · chữ nhỏ nhất ${m.min_fs}`);
    }
    if (o.webp && res.d) {
      const wp = join(base, it.svg.replace(/\.svg$/, '.webp'));
      execFileSync('python3', ['-c', `from PIL import Image;Image.open(${JSON.stringify(res.d.anh)}).convert('RGB').save(${JSON.stringify(wp)},'WEBP',quality=86,method=6)`]);
      console.log(`  webp: ${wp}`);
    }
    report[it.id] = res;
  }
} finally {
  await tab.close();
}
writeFileSync(join(base, 'svg_kiem.json'), JSON.stringify(report, null, 1));
process.exit(loi ? 1 : 0);
