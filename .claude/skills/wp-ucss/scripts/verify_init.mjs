// verify_init.mjs (wp-ucss): khởi tạo trang dưới file gộp và dưới file gọn từ đầu, cùng HTML, rồi so chiều cao trang và chiều cao widget JS.
// node verify_init.mjs --site <site.json> <jobs.txt> <thư mục CSS gọn> <thư mục ra>
//   jobs.txt: "path biến_thể" mỗi dòng. Thư mục CSS gọn chứa <md5 file gộp>.css (out/reduced hoặc thư mục bản sửa).
//   Ghi <thư mục ra>/<v>_<slug>.json và tom_tat.tsv. Mã 1 khi có cặp lệch hoặc lỗi.
// verify.mjs khởi tạo JS dưới CSS gộp rồi mới đổi sheet, nên không bắt lỗi khi JS đo phần tử lúc khởi tạo
// (site agency mẫu 27/10/2026: Owl Carousel thiếu .owl-carousel.owl-loading, carousel xếp lưới cao 1.400–2.703 px thay vì 350–503 px).
// Mỗi cặp tải HTML một lần (qua gate). Hai lượt nạp trang dùng đúng HTML đó; link CSS gọn mà mu-plugin đã đổi được trả về URL file gộp,
// rồi URL file gộp được trả bằng CSS gộp (lượt gop) hoặc CSS gọn (lượt gon). Không ghi gì lên server.
// Widget đo: khoá init_widgets của site.json (mặc định carousel Owl, slick, Swiper, Elementor). Ngưỡng lệch: INIT_TOL px (mặc định 2).
import fs from 'fs';
import https from 'https';
import { resolve } from 'path';
import { pathToFileURL } from 'url';
import { site, args, slug, launch, openPage, asset, gate, isDesk, sleep } from './lib-ucss.mjs';

const WIDGETS = '.owl-carousel, .slick-slider, .swiper, .elementor-image-carousel-wrapper';
const TOL = Number(process.env.INIT_TOL || 2);
const WAIT = Number(process.env.INIT_WAIT || 2500);

// Trả link CSS gọn do mu-plugin đổi về URL file gộp gốc, để cả hai lượt nạp CSS qua cùng một URL.
export function unswap(html, hash) {
  const S = site(), sub = (S.ucss_dir || 'wp-content/ucss').replace(/^\/+|\/+$/g, '');
  const re = new RegExp(`/${sub.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/${hash}\\.[0-9a-f]{8}\\.css`, 'g');
  return html.replace(re, `${S.combined_css_path}${hash}.css`);
}

// md5 file gộp trong HTML (kể cả URL gốc nằm trong onerror). Trả null khi trang không có hoặc có hơn một file gộp.
export function combinedHash(html) {
  const S = site(), c = S.combined_css_path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const hs = new Set([...html.matchAll(new RegExp(`${c}([0-9a-f]{32})\\.css`, 'g'))].map(m => m[1]));
  return hs.size === 1 ? [...hs][0] : null;
}

async function interact(p, dev) {
  const S = site();
  await sleep(1200);
  await p.mouse.move(200, 300); await p.mouse.move(220, 320);
  if (!isDesk(dev)) await p.touchscreen.tap(5, 5).catch(() => {});
  await p.keyboard.press('Shift');
  for (let i = 0; i < 40; i++) { if (await p.evaluate(s => window.__lsd || !document.querySelector(s), S.js_deferred_selector)) break; await sleep(200); }
  await sleep(WAIT);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 600) { await p.evaluate(v => window.scrollTo(0, v), y); await sleep(100); }
  await sleep(Math.min(WAIT, 1500));
  await p.evaluate(() => window.scrollTo(0, 0)); await sleep(300);
}

async function measure(browser, path, dev, html, hash, css, widgets, log) {
  const S = site();
  const override = new Map([[`https://${S.host}${S.combined_css_path}${hash}.css`, { type: 'text/css', body: css }]]);
  const { ctx, p, errs } = await openPage(browser, path, dev, { override, log, doc: html });
  try {
    await interact(p, dev);
    const r = await p.evaluate(sel => ({
      h: document.documentElement.scrollHeight,
      w: [...document.querySelectorAll(sel)].map(e => Math.round(e.getBoundingClientRect().height)),
    }), widgets);
    return { ...r, errs };
  } finally {
    await p.goto('about:blank').catch(() => {}); await ctx.close().catch(() => {});
  }
}

// Một cặp: lượt gop (CSS gộp) và lượt gon (CSS gọn), cùng HTML. lech = true khi chiều cao trang hoặc một widget khác quá TOL px.
export async function initPair(browser, path, dev, html, hash, cssGop, cssGon, { widgets = site().init_widgets || WIDGETS, log = [] } = {}) {
  const gop = await measure(browser, path, dev, html, hash, cssGop, widgets, log);
  const gon = await measure(browser, path, dev, html, hash, cssGon, widgets, log);
  const why = [];
  if (Math.abs(gop.h - gon.h) > TOL) why.push(`chiều cao trang ${gop.h} → ${gon.h}`);
  if (gop.w.length !== gon.w.length) why.push(`số widget ${gop.w.length} → ${gon.w.length}`);
  else gop.w.forEach((h, i) => { if (Math.abs(h - gon.w[i]) > TOL) why.push(`widget ${i} cao ${h} → ${gon.w[i]}`); });
  return { path, dev, hash, gop, gon, lech: why.length > 0, why };
}

function getHtml(path, dev) {
  const S = site();
  return gate().then(() => new Promise((res, rej) => {
    https.get(`https://${S.host}${path}`, { headers: { 'User-Agent': S.ua[dev], Accept: S.accept[dev], 'Accept-Language': S.accept_language }, timeout: 60000 }, r => {
      const b = []; r.on('data', c => b.push(c)); r.on('end', () => res({ status: r.statusCode, body: Buffer.concat(b).toString('utf8') }));
    }).on('error', rej).on('timeout', function () { this.destroy(new Error('timeout')); });
  }));
}

async function main() {
  const S = site();
  const [jobsFile, redDir, outDir] = args();
  if (!outDir) { console.log('Dùng: node verify_init.mjs --site <site.json> <jobs.txt> <thư mục CSS gọn> <thư mục ra>'); process.exit(2); }
  const jobs = fs.readFileSync(jobsFile, 'utf8').split('\n').map(l => l.trim().split(/\s+/)).filter(x => x[0] && x[0].startsWith('/'));
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await launch();
  const rows = ['path\tv\tmd5\tket_qua\tchieu_cao_gop\tchieu_cao_gon\twidget_gop\twidget_gon\tly_do'];
  let bad = 0;
  for (const [path, dev] of jobs) {
    const log = [], f = `${outDir}/${dev}_${slug(path)}.json`;
    let rec;
    try {
      const h = await getHtml(path, dev);
      const hash = h.status === 200 ? combinedHash(h.body) : null;
      const red = hash && `${redDir}/${hash}.css`;
      if (h.status !== 200) rec = { path, dev, err: `mã ${h.status}` };
      else if (!hash) rec = { path, dev, err: 'không có đúng một file gộp' };
      else if (!fs.existsSync(red)) rec = { path, dev, hash, err: 'thư mục CSS gọn không có file cho md5 này' };
      else {
        const gopCss = (await asset(`https://${S.host}${S.combined_css_path}${hash}.css`)).body;
        rec = await initPair(browser, path, dev, unswap(h.body, hash), hash, gopCss, fs.readFileSync(red), { log });
      }
    } catch (e) { rec = { path, dev, err: String(e).slice(0, 200) }; }
    rec.log = log;
    fs.writeFileSync(f, JSON.stringify(rec, null, 1));
    const kq = rec.err ? 'LỖI' : rec.lech ? 'LỆCH' : 'ĐẠT';
    if (kq !== 'ĐẠT') bad++;
    rows.push([path, dev, (rec.hash || '-').slice(0, 8), kq, rec.gop?.h ?? '', rec.gon?.h ?? '', (rec.gop?.w || []).join(','), (rec.gon?.w || []).join(','), rec.err || (rec.why || []).join('; ')].join('\t'));
    console.log(dev, path, kq, rec.err || (rec.why || []).join('; '));
  }
  await browser.close();
  fs.writeFileSync(`${outDir}/tom_tat.tsv`, rows.join('\n') + '\n');
  console.log(`cặp: ${jobs.length} | không đạt: ${bad}`);
  process.exit(bad ? 1 : 0);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) await main();
