// Chụp ảnh theo selector (hoặc màn đầu) ở nhiều bề rộng, làm một vế của cặp ảnh trước/sau cho so_sanh.py.
// node shot_el.mjs [tên=]<url>... --out <thư mục> --label <truoc|sau|...> [--sel SELECTOR] [--nth N] [--widths 390,1366] [--pad 16]
//                  [--css file] [--keep-fixed] [--dpr 1] [--max-h 4000] [--resolve host=ip] [--cookie n=v] [--wait ms] [--block mẫu,mẫu]
// Có --sel: cuộn tới phần tử, ẩn phần tử fixed bằng opacity:0 (giữ sticky), chụp khung phần tử cộng lề --pad.
// Không --sel: chụp màn đầu như người dùng thấy, giữ cả header và nút fixed.
// --css: chèn CSS thử sau khi tải trang (chỉ trong Chrome của lượt chụp) để có ảnh "sau" trước khi deploy.
// Ghi <out>/<slug>_<W>_<label>.png và <out>/shots_<label>.json. JSON chỉ ghi đường dẫn, không ghi host (staging qua tunnel không lộ host).
// Chỉ đọc: không bấm, không gửi form. Chặn tracking. Staging có Basic Auth: WEB_QA_AUTH="user:pass".
// Mã thoát: 0 xong · 1 có URL lỗi hoặc selector không khớp · 2 sai cú pháp.
// Phụ thuộc: ../../web-qa-gate/scripts/_cdp.mjs (skill web-qa-gate nằm cạnh wp-ui-fix).
import fs from 'node:fs';
import path from 'node:path';

const HELP = `shot_el.mjs — chụp ảnh theo selector hoặc màn đầu, làm cặp ảnh trước/sau

Dùng:  node shot_el.mjs [tên=]<url>... --out <thư mục> --label <nhãn> [tuỳ chọn]

  --out DIR          thư mục ghi ảnh và shots_<nhãn>.json (bắt buộc)
  --label L          nhãn lượt chụp, ví dụ truoc (production) hoặc sau (staging) (bắt buộc)
  --sel SELECTOR     phần tử cần chụp. Bỏ trống: chụp màn đầu, giữ header và nút fixed
  --nth N            phần tử thứ N trong các phần tử khớp (mặc định 0)
  --widths 390,1366  các bề rộng (mặc định 390,1366). Dưới 800 dùng UA điện thoại
  --pad N            lề quanh phần tử, px (mặc định 16)
  --css FILE         chèn CSS thử sau khi tải trang, không ghi gì lên site
  --keep-fixed       không ẩn phần tử fixed khi chụp theo selector
  --dpr N            tỉ lệ điểm ảnh (mặc định 1). Hai vế của một cặp phải dùng cùng số
  --max-h N          chiều cao tối đa của ảnh phần tử, px (mặc định 4000)
  --resolve h=ip     ánh xạ host tới IP (staging qua tunnel);  --cookie n=v
  --wait MS          chờ sau khi tải (mặc định 2500)
  --block a,b        mẫu URL chặn thêm (có dấu *)
  --help             in trợ giúp

Tên trước dấu = dùng làm khoá ghép cặp, ví dụ home=https://x/ dv=https://x/dich-vu/. Hai lượt trước và sau phải dùng cùng tên.
Mã thoát: 0 xong · 1 có URL lỗi hoặc selector không khớp · 2 sai cú pháp.`;

const argv = process.argv.slice(2);
if (argv.includes('--help') || argv.includes('-h')) { console.log(HELP); process.exit(0); }

let cdp;
try { cdp = await import('../../web-qa-gate/scripts/_cdp.mjs'); }
catch (e) { console.error('Không nạp được web-qa-gate/scripts/_cdp.mjs: cần skill web-qa-gate cạnh wp-ui-fix.\n' + e.message); process.exit(1); }
const {args, openTab, sleep, MUA, DUA} = cdp;

const o = args(argv, ['keep-fixed']);
const targets = o._.map(a => { const m = /^([A-Za-z0-9_-]+)=(https?:\/\/.+)$/.exec(a); return m ? {name: m[1], url: m[2]} : {name: null, url: a}; });
if (!targets.length || typeof o.out !== 'string' || typeof o.label !== 'string' || targets.some(t => !/^https?:\/\//.test(t.url))) {
  console.error('Thiếu <url> (http hoặc https), --out hoặc --label. Chạy --help.'); process.exit(2);
}
if (!/^[A-Za-z0-9_-]+$/.test(o.label)) { console.error('--label chỉ gồm chữ không dấu, số, - và _.'); process.exit(2); }
const widths = String(o.widths || '390,1366').split(',').map(Number);
if (widths.some(w => !(w >= 200 && w <= 4000))) { console.error('--widths phải nằm trong 200–4000.'); process.exit(2); }
const sel = typeof o.sel === 'string' ? o.sel : null;
const nth = +(o.nth || 0), pad = +(o.pad ?? 16), dpr = +(o.dpr || 1), maxH = +(o['max-h'] || 4000), wait = +(o.wait || 2500);
if (![nth, pad, dpr, maxH, wait].every(Number.isFinite) || dpr <= 0 || dpr > 3) { console.error('--nth, --pad, --dpr (0–3), --max-h, --wait phải là số.'); process.exit(2); }
let css = null;
if (o.css) { try { css = fs.readFileSync(String(o.css), 'utf8'); } catch (e) { console.error('Không đọc được --css: ' + e.message); process.exit(2); } }
const BLOCK = ['*googletagmanager.com*', '*google-analytics.com*', '*connect.facebook.net*', '*facebook.com/tr*', '*hotjar.com*', '*clarity.ms*', '*doubleclick.net*', '*guest.vary.php*',
  ...(typeof o.block === 'string' ? o.block.split(',').filter(Boolean) : [])];
const slugOf = (t, i) => (t.name || (new URL(t.url).pathname.replace(/^\/|\/$/g, '').replace(/[^A-Za-z0-9]+/g, '-') || 'home')) + (targets.filter((x, j) => j < i && (x.name || '') === (t.name || '')).length ? '-' + i : '');
const pathOf = u => { const x = new URL(u); return x.pathname + x.search; };

const tab = await openTab({host: new URL(targets[0].url).host, resolve: o.resolve, cookie: o.cookie, block: BLOCK});
const {send, evalv, events, close} = tab;
fs.mkdirSync(o.out, {recursive: true});
const shots = [];
let bad = 0;
try {
  await send('Page.enable'); await send('Runtime.enable');
  for (const [ti, t] of targets.entries()) for (const W of widths) {
    const mob = W < 800, H = mob ? 800 : 900, slug = slugOf(t, ti);
    const row = {name: t.name || slug, slug, path: pathOf(t.url), width: W, label: o.label, sel, nth: sel ? nth : null, css: o.css ? path.basename(String(o.css)) : null, dpr};
    try {
      await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: dpr, mobile: false});
      await send('Emulation.setTouchEmulationEnabled', {enabled: mob});
      await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
      events.length = 0;
      await send('Page.navigate', {url: t.url});
      for (let i = 0; i < 60 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
      const docs = events.filter(e => e.method === 'Network.responseReceived' && e.params.type === 'Document');
      row.status = docs.length ? docs[docs.length - 1].params.response.status : null;
      if (row.status >= 400) throw new Error('HTTP ' + row.status + ': không chụp trang lỗi');
      const failedDoc = events.find(e => e.method === 'Network.loadingFailed' && e.params.type === 'Document' && !e.params.canceled);
      if (failedDoc) throw new Error('không tải được trang: ' + (failedDoc.params.errorText || 'lỗi mạng'));
      if (row.status === null) throw new Error('không có mã HTTP: không chụp trang lỗi');
      await sleep(wait);
      if (css !== null) {
        await evalv(`(()=>{const s=document.createElement('style');s.id='wp-ui-fix-thu';s.textContent=${JSON.stringify(css)};document.head.appendChild(s);return 1})()`);
        await sleep(300);
      }
      row.title = await evalv('document.title.slice(0,80)');
      const file = `${slug}_${W}_${o.label}.png`;
      let shot;
      if (!sel) {
        await evalv('scrollTo(0,0)'); await sleep(300);
        shot = await send('Page.captureScreenshot', {format: 'png'});
        row.rect = {x: 0, y: 0, w: W, h: H};
      } else {
        // Cuộn hết trang cho ảnh lazy và slider dựng xong, rồi cuộn tới phần tử.
        await evalv(`(async()=>{for(let y=0;y<Math.min(document.documentElement.scrollHeight,30000);y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,80));}scrollTo(0,0);await new Promise(r=>setTimeout(r,400));})()`, true);
        const found = await evalv(`(()=>{const l=document.querySelectorAll(${JSON.stringify(sel)});const e=l[${nth}];if(!e)return {count:l.length};e.scrollIntoView({block:'center'});return {count:l.length}})()`);
        if (!found || found.count <= nth) throw new Error(`selector khớp ${found ? found.count : 0} phần tử, không có phần tử thứ ${nth}`);
        await sleep(500);
        if (!o['keep-fixed']) {
          // Ẩn fixed (nút nổi, thanh dưới đáy, header fixed) bằng opacity:0. Sticky giữ nguyên. Phần tử fixed phủ gần cả màn hình (nền) không ẩn.
          const hid = await evalv(`(()=>{let f=0,s=0;document.querySelectorAll('body *').forEach(e=>{const p=getComputedStyle(e).position;
            if(p==='fixed'&&e.getBoundingClientRect().height<innerHeight*0.9){e.style.setProperty('opacity','0','important');f++}
            else if(p==='sticky')s++});return {fixed:f,sticky:s}})()`);
          row.hid_fixed = hid ? hid.fixed : 0; row.kept_sticky = hid ? hid.sticky : 0;
        }
        const r = await evalv(`(()=>{const e=document.querySelectorAll(${JSON.stringify(sel)})[${nth}];const b=e.getBoundingClientRect();
          return {x:b.left+scrollX,y:b.top+scrollY,w:b.width,h:b.height,dw:document.documentElement.scrollWidth,dh:document.documentElement.scrollHeight}})()`);
        if (!r || r.w < 1 || r.h < 1) throw new Error('phần tử không có kích thước (ẩn hoặc display:none)');
        const x = Math.max(0, Math.floor(r.x - pad)), y = Math.max(0, Math.floor(r.y - pad));
        const w = Math.min(Math.ceil(r.w + 2 * pad), Math.max(1, r.dw - x), 4000);
        const h = Math.min(Math.ceil(r.h + 2 * pad), Math.max(1, r.dh - y), maxH);
        row.rect = {x, y, w, h};
        if (r.h + 2 * pad > maxH) row.cut = `cắt ở ${maxH}px, phần tử cao ${Math.round(r.h)}px`;
        shot = await send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true, clip: {x, y, width: w, height: h, scale: 1}});
      }
      if (!shot.result || !shot.result.data) throw new Error('Chrome không trả ảnh');
      fs.writeFileSync(path.join(o.out, file), Buffer.from(shot.result.data, 'base64'));
      row.file = file;
      console.log(`${row.name} ${W}px ${row.path} → ${file} (${row.rect.w}×${row.rect.h})${row.cut ? ' ' + row.cut : ''}`);
    } catch (e) {
      row.error = String(e && e.message || e).slice(0, 200); bad++;
      console.error(`LỖI ${row.name} ${W}px ${row.path}: ${row.error}`);
    }
    shots.push(row);
  }
} finally {
  await close();
}
const outJson = path.join(o.out, `shots_${o.label}.json`);
fs.writeFileSync(outJson, JSON.stringify({version: 1, generated: new Date().toISOString(), label: o.label, shots}, null, 1));
console.log(`Ghi ${outJson} (${shots.length} ảnh, ${bad} lỗi)`);
process.exit(bad ? 1 : 0);
