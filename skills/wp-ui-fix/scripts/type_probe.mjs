// Đo chữ theo từng khối của trang đang chạy: cỡ chữ, line-height, bề rộng, số dòng, ký tự mỗi dòng, vị trí; mọi heading H1–H4; khoảng cách header → H1.
// node type_probe.mjs [name=]<url>... --out <thư mục> [--widths 390,1366] [--header SEL] [--extra SEL] [--max-screens N] [--no-shots]
//                     [--resolve host=ip] [--cookie n=v] [--wait ms] [--block mẫu,mẫu]
// Ghi <out>/type_probe.json (cho type_check.py) và ảnh <slug>_<w>_hero.jpg (header còn hiện) + <slug>_<w>_sNN.jpg (từng màn, đã ẩn phần tử fixed).
// Ẩn phần tử fixed bằng opacity:0 khi chụp từng màn, GIỮ sticky (header dính ngoài hero và ảnh sticky trong nội dung phải còn).
// Chỉ đọc: không bấm, không gửi form. Chặn tracking. Staging có Basic Auth: WEB_QA_AUTH="user:pass". Không gán cứng host nào.
// Mã thoát: 0 xong · 1 có URL lỗi · 2 sai cú pháp.
// Port từ type_probe.mjs, measure.mjs và hero_probe.mjs của đợt 19–20/10/2026, bỏ host gán cứng và đường dẫn puppeteer.
import fs from 'node:fs';
import path from 'node:path';

const HELP = `type_probe.mjs — đo chữ theo khối trên trang đang chạy

Dùng:  node type_probe.mjs [tên=]<url>... --out <thư mục> [tuỳ chọn]

  --out DIR          thư mục ghi type_probe.json và ảnh (bắt buộc)
  --widths 390,1366  các bề rộng (mặc định 390,1366). Dưới 800 dùng UA điện thoại
  --header SEL       selector của header (mặc định header,[role=banner],#masthead,.site-header,#header)
  --extra SEL        thêm selector khối chữ ngoài p, li, td, th, dd, dt, blockquote, figcaption, h1–h4, label, summary
  --max-screens N    tối đa N ảnh mỗi trang và bề rộng (mặc định 16)
  --no-shots         không chụp ảnh
  --resolve h=ip     ánh xạ host tới IP (staging qua tunnel);  --cookie n=v
  --wait MS          chờ sau khi tải (mặc định 2500)
  --block a,b        mẫu URL chặn thêm (có dấu *)
  --help             in trợ giúp

Tên trước dấu = dùng để gom H1 giữa các template, ví dụ home=https://x/ dv=https://x/dich-vu/.
Mã thoát: 0 xong · 1 có URL lỗi · 2 sai cú pháp.`;

const argv = process.argv.slice(2);
if (argv.includes('--help') || argv.includes('-h')) { console.log(HELP); process.exit(0); }

let cdp;
try { cdp = await import('../../web-qa-gate/scripts/_cdp.mjs'); }
catch (e) { console.error('Không nạp được web-qa-gate/scripts/_cdp.mjs: cần skill web-qa-gate cạnh wp-ui-fix.\n' + e.message); process.exit(1); }
const {args, openTab, sleep, MUA, DUA} = cdp;

const o = args(argv, ['no-shots']);
const targets = o._.map(a => { const m = /^([A-Za-z0-9_-]+)=(https?:\/\/.+)$/.exec(a); return m ? {name: m[1], url: m[2]} : {name: null, url: a}; });
if (!targets.length || !o.out || targets.some(t => !/^https?:\/\//.test(t.url))) { console.error('Thiếu <url> (http hoặc https) hoặc --out. Chạy --help.'); process.exit(2); }
const widths = String(o.widths || '390,1366').split(',').map(Number);
if (widths.some(w => !(w >= 200 && w <= 4000))) { console.error('--widths phải nằm trong 200–4000.'); process.exit(2); }
const wait = +(o.wait || 2500), maxScreens = +(o['max-screens'] || 16), shots = !o['no-shots'];
const headerSel = typeof o.header === 'string' ? o.header : 'header,[role=banner],#masthead,.site-header,#header';
const extraSel = typeof o.extra === 'string' ? o.extra : '';
const BLOCK = ['*googletagmanager.com*', '*google-analytics.com*', '*connect.facebook.net*', '*facebook.com/tr*', '*hotjar.com*', '*clarity.ms*', '*doubleclick.net*', '*guest.vary.php*',
  ...(typeof o.block === 'string' ? o.block.split(',').filter(Boolean) : [])];
const slugOf = (t, i) => (t.name || (new URL(t.url).pathname.replace(/^\/|\/$/g, '').replace(/[^A-Za-z0-9]+/g, '-') || 'home')) + (targets.filter((x, j) => j < i && (x.name || '') === (t.name || '')).length ? '-' + i : '');

// Chạy trong trang. Trả khối chữ, heading, header và khoảng cách header → H1.
const PROBE = `((headerSel, extraSel, vw) => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const path = e => { const a = []; let n = e; for (let i = 0; n && n.nodeType === 1 && i < 4; i++, n = n.parentElement) { let s = n.tagName.toLowerCase(); if (n.id) s += '#' + n.id; else if (n.classList.length) s += '.' + [...n.classList].slice(0, 2).join('.'); a.unshift(s); } return a.join(' > '); };
  const region = e => e.closest('nav,[role=navigation],#mega-menu-wrap-primary,[id^=mega-menu-wrap]') ? 'nav'
    : e.closest('footer,.site-footer,#footer,[role=contentinfo]') ? 'footer'
    : e.closest(headerSel) && (e.closest(headerSel).getBoundingClientRect().top + scrollY) < 200 ? 'header' : 'main';
  const posOf = e => { let fixed = false, sticky = false; for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const p = getComputedStyle(n).position; if (p === 'fixed') fixed = true; if (p === 'sticky') sticky = true; } return {fixed, sticky}; };
  const lineCount = e => {
    const rg = document.createRange(); rg.selectNodeContents(e);
    const tops = new Set(); for (const r of rg.getClientRects()) if (r.width > 1 && r.height > 1) tops.add(Math.round(r.top / 3));
    return Math.max(1, tops.size);
  };
  const SEL = 'p,li,td,th,dd,dt,blockquote,figcaption,h1,h2,h3,h4,label,summary' + (extraSel ? ',' + extraSel : '');
  const blocks = [];
  document.querySelectorAll(SEL).forEach(e => {
    if (!vis(e)) return;
    if (e.querySelector('p,li,h1,h2,h3,h4,blockquote') && !/^H/.test(e.tagName)) return;
    const t = (e.innerText || '').replace(/\\s+/g, ' ').trim(); if (t.length < 3) return;
    const s = getComputedStyle(e), r = e.getBoundingClientRect(), fs = parseFloat(s.fontSize);
    const lhpx = parseFloat(s.lineHeight) || fs * 1.4;
    const lines = lineCount(e), p = posOf(e);
    blocks.push({ tag: e.tagName.toLowerCase(), sel: path(e), cls: String(e.className).slice(0, 60), fs, fw: s.fontWeight, lh: +(lhpx / fs).toFixed(2),
      w: Math.round(r.width - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight)), lines, n: t.length, cpl: lines > 1 ? Math.round(t.length / lines) : t.length,
      y: Math.round(r.top + scrollY), region: region(e), fixed: p.fixed, sticky: p.sticky, t: t.slice(0, 70) });
  });
  const heads = [...document.querySelectorAll('h1,h2,h3,h4')].filter(vis).map(h => { const s = getComputedStyle(h), p = posOf(h);
    return { tag: h.tagName.toLowerCase(), fs: parseFloat(s.fontSize), fw: s.fontWeight, ff: s.fontFamily.split(',')[0].replace(/"/g, ''), y: Math.round(h.getBoundingClientRect().top + scrollY), region: region(h), fixed: p.fixed, sel: path(h), t: (h.innerText || '').replace(/\\s+/g, ' ').slice(0, 70) }; });
  const hdr = [...document.querySelectorAll(headerSel)].find(h => vis(h) && h.getBoundingClientRect().top + scrollY < 200);
  const header = hdr ? { sel: path(hdr), top: Math.round(hdr.getBoundingClientRect().top + scrollY), bottom: Math.round(hdr.getBoundingClientRect().bottom + scrollY), position: getComputedStyle(hdr).position } : null;
  const h1 = heads.find(h => h.tag === 'h1' && h.region !== 'nav' && h.region !== 'footer');
  return { blocks, heads, header, h1_gap: header && h1 ? h1.y - header.bottom : null, docH: document.documentElement.scrollHeight, innerW: innerWidth, docW: document.documentElement.scrollWidth, title: document.title.slice(0, 80) };
})`;

const tab = await openTab({host: new URL(targets[0].url).host, resolve: o.resolve, cookie: o.cookie, block: BLOCK});
const {send, evalv, events, close} = tab;
fs.mkdirSync(o.out, {recursive: true});
const pages = [];
let bad = 0;
try {
  await send('Page.enable'); await send('Runtime.enable');
  for (const [ti, t] of targets.entries()) for (const W of widths) {
    const mob = W < 800, H = mob ? 800 : 900, slug = slugOf(t, ti);
    const row = {name: t.name || slug, slug, url: t.url, path: new URL(t.url).pathname, width: W, vp: (mob ? 'm' : 'd') + W, mobile: mob};
    try {
      await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: mob ? 2 : 1, mobile: false});
      await send('Emulation.setTouchEmulationEnabled', {enabled: mob});
      await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
      events.length = 0;
      await send('Page.navigate', {url: t.url});
      for (let i = 0; i < 60 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
      const docs = events.filter(e => e.method === 'Network.responseReceived' && e.params.type === 'Document');
      row.status = docs.length ? docs[docs.length - 1].params.response.status : null;
      if (row.status >= 400) throw new Error('HTTP ' + row.status + ': không đo trang lỗi');
      const failedDoc = events.find(e => e.method === 'Network.loadingFailed' && e.params.type === 'Document' && !e.params.canceled);
      if (failedDoc) throw new Error('không tải được trang: ' + (failedDoc.params.errorText || 'lỗi mạng'));
      if (row.status === null) throw new Error('không có mã HTTP: không đo trang lỗi');
      await sleep(wait);
      // Cuộn hết trang để ảnh lazy và slider dựng xong, rồi về đầu trang.
      await evalv(`(async()=>{for(let y=0;y<Math.min(document.documentElement.scrollHeight,30000);y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,100));}scrollTo(0,0);await new Promise(r=>setTimeout(r,600));})()`, true);
      const m = await evalv(`${PROBE}(${JSON.stringify(headerSel)}, ${JSON.stringify(extraSel)}, ${W})`);
      if (!m) throw new Error('probe không trả kết quả');
      Object.assign(row, m);
      row.shots = [];
      if (shots) {
        const save = async name => { const s = await send('Page.captureScreenshot', {format: 'jpeg', quality: 72}); fs.writeFileSync(path.join(o.out, name), Buffer.from(s.result.data, 'base64')); row.shots.push(name); };
        await save(`${slug}_${W}_hero.jpg`);
        // Ẩn fixed (nút nổi, thanh dưới đáy, header fixed) bằng opacity:0. Sticky giữ nguyên. Phần tử fixed phủ gần cả màn hình (nền) không ẩn.
        const hid = await evalv(`(()=>{let f=0,s=0;document.querySelectorAll('body *').forEach(e=>{const p=getComputedStyle(e).position;
          if(p==='fixed'&&e.getBoundingClientRect().height<innerHeight*0.9){e.style.setProperty('opacity','0','important');f++}
          else if(p==='sticky')s++});return {fixed:f,sticky:s}})()`);
        row.hid_fixed = hid ? hid.fixed : 0; row.kept_sticky = hid ? hid.sticky : 0;
        const total = Math.min(row.docH, 16000);
        for (let y = 0, i = 0; y < total && i < maxScreens; y += H, i++) { await evalv(`scrollTo(0,${y})`); await sleep(300); await save(`${slug}_${W}_s${String(i).padStart(2, '0')}.jpg`); }
        await evalv('scrollTo(0,0)');
      }
      console.log(`${row.name} ${row.vp} khối=${row.blocks.length} heading=${row.heads.length} h1_gap=${row.h1_gap} ảnh=${row.shots.length}`);
    } catch (e) {
      row.error = String(e && e.message || e).slice(0, 200); bad++;
      console.error(`LỖI ${t.url} ${W}px: ${row.error}`);
    }
    pages.push(row);
  }
} finally {
  await close();
}
fs.writeFileSync(path.join(o.out, 'type_probe.json'), JSON.stringify({version: 1, generated: new Date().toISOString(), pages}, null, 1));
console.log(`Ghi ${path.join(o.out, 'type_probe.json')} (${pages.length} lượt đo, ${bad} lỗi)`);
process.exit(bad ? 1 : 0);
