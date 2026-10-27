// test_combined_href.mjs (wp-ucss): combinedHref trên Chrome headless thật, không gọi mạng (mọi request trả tại chỗ).
// Ca hỏng thật: site mẫu 27/10/2026, trang đã đổi sang CSS gọn chỉ giữ URL gốc trong onerror; verify.mjs bỏ qua 124 cặp.
import { rq, combinedHref } from '../lib-ucss.mjs';

const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const C = '/wp-content/litespeed/css/';
const ORIG = `${C}0123456789abcdef0123456789abcdef.css`;
const PAGES = {
  '/doi/': `<link rel="stylesheet" href="/gon/a.css" data-ucss="1" onerror="this.onerror=null;this.href='${ORIG}?ver=1'"><body>x</body>`,
  '/goc/': `<link rel="stylesheet" href="${ORIG}?ver=1"><body>x</body>`,
  '/khong/': '<body>x</body>',
};
const CSS = { [ORIG]: 'body{color:rgb(1,2,3)}', '/gon/a.css': 'body{color:rgb(9,9,9)}' };

const b = await rq('puppeteer-core').launch({ executablePath: CHROME, headless: 'new', pipe: true, args: ['--no-first-run', '--host-resolver-rules=MAP * ~NOTFOUND'] });
let bad = 0;
const ok = (name, cond) => { if (!cond) bad++; console.log(cond ? 'OK ' : 'SAI', name); };
try {
  const p = await b.newPage();
  await p.setRequestInterception(true);
  p.on('request', r => {
    const u = new URL(r.url());
    if (PAGES[u.pathname]) return r.respond({ status: 200, contentType: 'text/html', body: PAGES[u.pathname] });
    if (CSS[u.pathname]) return r.respond({ status: 200, contentType: 'text/css', body: CSS[u.pathname] });
    return r.respond({ status: 404, body: '' });
  });
  const color = () => p.evaluate(() => getComputedStyle(document.body).color);
  await p.goto('http://site.test/doi/', { waitUntil: 'load' });
  ok('trang đã đổi: trước khi gọi, đang dùng CSS gọn', await color() === 'rgb(9, 9, 9)');
  const h = await combinedHref(p, C);
  ok('trang đã đổi: trả URL gốc lấy từ onerror', h === `http://site.test${ORIG}?ver=1`);
  ok('trang đã đổi: link đã nạp lại file gộp gốc', await color() === 'rgb(1, 2, 3)');
  await p.goto('http://site.test/goc/', { waitUntil: 'load' });
  ok('trang gốc: trả href có sẵn', await combinedHref(p, C) === `http://site.test${ORIG}?ver=1`);
  await p.goto('http://site.test/khong/', { waitUntil: 'load' });
  ok('trang không có CSS gộp: trả null', await combinedHref(p, C) === null);
} finally {
  await b.close();
}
process.exit(bad ? 1 : 0);
