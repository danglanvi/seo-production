// test_verify_init.mjs (wp-ucss): initPair, unswap, combinedHash trên Chrome headless thật, không gọi mạng (HTML và CSS trả tại chỗ).
// Ca hỏng thật: site agency mẫu 27/10/2026, Owl Carousel thêm owl-loading rồi đo phần tử. CSS gọn thiếu .owl-carousel.owl-loading
// nên carousel còn display:none lúc đo, xếp lưới nhiều hàng. Fixture giả lập đúng hành vi đó bằng một script nhỏ.
import fs from 'fs';
import os from 'os';
import { join } from 'path';
import { rq } from '../lib-ucss.mjs';

const tmp = fs.mkdtempSync(join(os.tmpdir(), 'wp-ucss-init-'));
const H = 'ab'.repeat(16);
fs.writeFileSync(join(tmp, 'site.json'), JSON.stringify({
  host: 'site.test', asset_hosts: [], block_dns: [], accept_language: 'vi',
  ua: { m: 'UA-m', d: 'UA-d' }, accept: { m: '*/*', d: '*/*' },
  viewport: { m: { width: 390, height: 844, isMobile: true, hasTouch: true }, d: { width: 1366, height: 900 } },
  combined_css_path: '/wp-content/litespeed/css/', test_prefix: '/wp-content/litespeed/ucss-test/', ucss_dir: 'wp-content/ucss',
  js_ready_event: 'DOMContentLiteSpeedLoaded', js_deferred_selector: 'script[type="litespeed/javascript"]',
  stub_vary: 'guest\\.vary\\.php', stub_ajax: 'admin-ajax\\.php', states: {}, cache_dir: join(tmp, 'cache'),
}));
process.env.UCSS_SITE = join(tmp, 'site.json');
process.env.INIT_WAIT = '300';
const { initPair, unswap, combinedHash } = await import('../verify_init.mjs');

// Owl giả: khi có tương tác, thêm owl-loading, đo bề rộng; thấy phần tử thì dựng stage một hàng, không thấy thì để item xếp lưới.
const OWL = `document.addEventListener('mousemove', function init() {
  document.removeEventListener('mousemove', init);
  const c = document.querySelector('.owl-carousel'); c.classList.add('owl-loading');
  const w = c.offsetWidth;
  if (w > 0) { const s = document.createElement('div'); s.className = 'owl-stage'; s.style.width = (w * 8) + 'px';
    [...c.children].forEach(it => { it.style.width = w + 'px'; s.appendChild(it); }); c.appendChild(s); }
  c.classList.remove('owl-loading'); c.classList.add('owl-loaded');
});`;
const HTML = `<!doctype html><html><head><link rel="stylesheet" href="/wp-content/ucss/${H}.0123abcd.css" data-ucss="1" onerror="this.onerror=null;this.href='/wp-content/litespeed/css/${H}.css?ver=1'"></head>
<body><div class="owl-carousel">${'<div class="item">x</div>'.repeat(8)}</div><div style="height:300px">sau</div><script>${OWL}</script></body></html>`;
const BASE = '.owl-carousel{display:none;overflow:hidden}.owl-carousel.owl-loaded{display:block}.owl-carousel .item{float:left;width:40%;height:100px}.owl-stage{display:flex}';
const GOP = BASE + '.owl-carousel.owl-loading{opacity:0;display:block}';
const GON_THIEU = BASE;
const GON_SUA = GOP;

let bad = 0;
const ok = (name, cond, more = '') => { if (!cond) bad++; console.log(cond ? 'OK ' : 'SAI', name, cond ? '' : more); };
ok('combinedHash đọc md5 trong onerror', combinedHash(HTML) === H);
const html = unswap(HTML, H);
ok('unswap trả link CSS gọn về URL file gộp', html.includes(`href="/wp-content/litespeed/css/${H}.css"`) && !html.includes('/wp-content/ucss/'));
ok('combinedHash: 2 file gộp thì null', combinedHash(HTML + `<link href="/wp-content/litespeed/css/${'cd'.repeat(16)}.css">`) === null);

const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const b = await rq('puppeteer-core').launch({ executablePath: CHROME, headless: 'new', pipe: true, args: ['--no-first-run', '--host-resolver-rules=MAP * ~NOTFOUND'] });
try {
  for (const dev of ['d', 'm']) {
    const r1 = await initPair(b, '/owl/', dev, html, H, GOP, GON_THIEU);
    ok(`${dev}: CSS gọn thiếu rule owl-loading thì báo lệch`, r1.lech && r1.gon.w[0] > r1.gop.w[0] && r1.gop.w[0] === 100, JSON.stringify(r1));
    const r2 = await initPair(b, '/owl/', dev, html, H, GOP, GON_SUA);
    ok(`${dev}: CSS gọn đã sửa thì không lệch`, !r2.lech && r2.gop.w[0] === 100, JSON.stringify(r2));
  }
} finally {
  await b.close();
  fs.rmSync(tmp, { recursive: true, force: true });
}
process.exit(bad ? 1 : 0);
