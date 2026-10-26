// Cài một lần: mkdir -p ~/.cache/wp-pagespeed && cd ~/.cache/wp-pagespeed && npm i penthouse@2 puppeteer-core clean-css postcss
// Chạy từ thư mục đó để Node tìm thấy package: cp <skill>/scripts/ccss_gen.mjs ~/.cache/wp-pagespeed/ && node ~/.cache/wp-pagespeed/ccss_gen.mjs ...
// node ccss_gen.mjs --jobs jobs.json --out <thư mục> [--skip-id <id thẻ style critical đang có>] [--resolve host=ip]
// jobs: [{"key":"home","urls":["https://example.com/"]}, ...]. Sinh <key>-m.css (mobile 390x844) và <key>-d.css (desktop 1366x900).
// CSS đầu vào lấy từ CSSOM của Chrome, không lấy text gốc: quy tắc Chrome bỏ vì lỗi cú pháp không lọt vào critical CSS.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass". Chrome chỉ gửi thông tin này khi host trả 401.
import fs from 'node:fs'; import path from 'node:path';
import puppeteer from 'puppeteer-core';
import penthouse from 'penthouse';
import CleanCSS from 'clean-css';
import postcss from 'postcss';

const o = {};
for (let i = 2; i < process.argv.length; i++) { const k = process.argv[i].replace(/^--/, ''); o[k] = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : true; }
fs.mkdirSync(o.out, { recursive: true });
const UA = {
  m: 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
  d: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
};
const VP = { m: { width: 390, height: 844 }, d: { width: 1366, height: 900 } };
const cred = process.env.CDP_AUTH ? { username: process.env.CDP_AUTH.split(':')[0], password: process.env.CDP_AUTH.split(':').slice(1).join(':') } : null;
const flags = ['--headless=new', '--ignore-certificate-errors'];
if (o.resolve) { const [h, ip] = String(o.resolve).split('='); flags.push(`--host-resolver-rules=MAP ${h} ${ip}`); }
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: flags, defaultViewport: null });

// penthouse gọi browser.close() sau mỗi job: chặn để dùng lại Chrome. Mỗi tab mới nhận Basic Auth nếu có.
const newPage = async () => { const p = await browser.newPage(); if (cred) await p.authenticate(cred); return p; };
const safeBrowser = new Proxy(browser, { get(t, p) { if (p === 'close') return async () => {}; if (p === 'newPage') return newPage; const v = t[p]; return typeof v === 'function' ? v.bind(t) : v; } });
const absUrls = (css, base) => css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, u) => {
  if (/^(data:|https?:|\/\/|#|about:)/i.test(u)) return m;
  try { return `url(${q}${new URL(u, base).href}${q})`; } catch { return m; }
});

async function pageCss(url, dev) {
  const page = await newPage();
  await page.setUserAgent(UA[dev]);
  await page.setViewport({ ...VP[dev], deviceScaleFactor: 1, isMobile: dev === 'm', hasTouch: dev === 'm' });
  await page.goto(url, { waitUntil: 'load', timeout: 90000 });
  await new Promise(r => setTimeout(r, 1500));
  const sheets = await page.evaluate(skip => [...document.styleSheets].map(sh => {
    const node = sh.ownerNode;
    if (skip && node && node.id === skip) return null;
    if (sh.media && sh.media.mediaText && /^print$/i.test(sh.media.mediaText)) return null;
    try { return { href: sh.href || location.href, text: [...sh.cssRules].map(r => r.cssText).join('\n') }; }
    catch (e) { return { href: sh.href, text: null }; }
  }).filter(Boolean), o['skip-id'] || '');
  await page.close();
  const parts = [];
  for (const sh of sheets) {
    if (sh.text === null) {
      const r = await fetch(sh.href, { headers: { 'User-Agent': UA[dev] } });
      console.log('  cross-origin, dùng text gốc:', sh.href.slice(-70));
      if (r.ok) parts.push(absUrls(await r.text(), sh.href));
    } else parts.push(absUrls(sh.text, sh.href));
  }
  return parts.join('\n');
}

const ruleKey = r => r.replace(/\s+/g, ' ').trim();
for (const job of JSON.parse(fs.readFileSync(o.jobs, 'utf8'))) for (const dev of ['m', 'd']) {
  const outs = [];
  for (const url of job.urls) {
    const css = await pageCss(url, dev);
    const t0 = Date.now();
    const crit = await penthouse({
      url, cssString: css, width: VP[dev].width, height: VP[dev].height, userAgent: UA[dev],
      puppeteer: { getBrowser: () => safeBrowser }, unstableKeepBrowserAlive: true, blockJSRequests: true, renderWaitTime: 400,
      keepLargerMediaQueries: false, timeout: 90000, pageLoadSkipTimeout: 25000,
    });
    console.log(`${job.key}-${dev} ${url} full=${Math.round(css.length / 1024)}KB crit=${Math.round(crit.length / 1024)}KB ${Date.now() - t0}ms`);
    outs.push(crit);
  }
  // Gộp nhiều URL mẫu: giữ thứ tự bản đầu, thêm khối chưa có của bản sau.
  let merged = outs[0];
  if (outs.length > 1) {
    const parsed = outs.map((x, i) => { try { return postcss.parse(x); } catch (e) { console.log(`  bỏ bản ${i} khi gộp: ${e.reason}`); return null; } }).filter(Boolean);
    const root = parsed[0], seen = new Set(root.nodes.map(n => ruleKey(n.toString())));
    for (const r of parsed.slice(1)) for (const n of r.nodes) { const k = ruleKey(n.toString()); if (!seen.has(k)) { seen.add(k); root.append(n.clone()); } }
    merged = root.toString();
  }
  // Bỏ @import (Google Fonts) và @charset: trong <style> inline, @import chặn hiển thị; file CSS đầy đủ vẫn giữ.
  const min = new CleanCSS({ level: 1 }).minify(merged).styles.replace(/@import\s+url\([^)]*\)[^;]*;/g, '').replace(/@charset\s+"[^"]*";/g, '');
  fs.writeFileSync(path.join(o.out, `${job.key}-${dev}.css`), min);
  console.log(`=> ${job.key}-${dev}.css ${Math.round(min.length / 1024)}KB`);
}
await browser.close();
console.log('CCSS_DONE');
