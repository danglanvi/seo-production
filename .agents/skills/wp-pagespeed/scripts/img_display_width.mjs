// Đo bề rộng hiển thị và cỡ gốc của từng <img> trên một trang ở nhiều bề rộng viewport (mặc định 360, 412, 768, 1024, 1366, 1920).
// Chrome headless qua CDP, chạy máy cục bộ. Chỉ đọc trang, không ghi gì lên site. Đổi Chrome bằng biến CHROME_BIN.
// node "$WPS/scripts/img_display_width.mjs" --url URL [--widths 360,412,768,1024,1366,1920] [--dpr 1] [--settle 2500]
//   [--resolve host=ip] [--cookie tên=giá trị] [--expect '<chuỗi trong title>'] [--no-guard] [--allow-redirect-host]
//   [--out file.json --apply]
// Gộp kết quả và tìm ảnh thừa: python3 "$WPS/scripts/img_width_report.py" file.json
// Mỗi bề rộng: mở lại trang với Emulation.setDeviceMetricsOverride {width, deviceScaleFactor: dpr, mobile: false}. KHÔNG bật cờ mobile của CDP
// (luật M28: cờ này đổi viewport bố cục và làm scrollWidth, bề rộng hiển thị lệch). Kết quả ghi cả innerWidth thật để kiểm viewport có đúng không.
// Ảnh lazy được ép loading=eager rồi chờ tải (không cuộn trang). currentSrc phụ thuộc dpr: chạy lại với --dpr 2 để xem máy màn hình nét.
// Mỗi ảnh: src (thuộc tính), currentSrc, fileWidth/fileHeight (px thật của file, đo bằng Image() riêng), naturalWidth/Height (số trình duyệt báo,
// đã chia theo mật độ: ảnh có srcset w kèm sizes báo bề rộng nguồn theo sizes, không phải px của file), displayWidth/Height (px CSS), visible,
// bytes (encodedBodySize từ Resource Timing), srcsetWidths, loading (trước khi ép eager). Ảnh nền CSS không nằm trong kết quả.
// Guard như perf_probe.mjs: thoát mã 4 khi HTTP >= 400, host bị redirect, title không chứa --expect, hoặc cổng tunnel của --resolve không mở.
// --out cần --apply (mặc định in JSON ra stdout, không ghi file). Không ghi đè file có sẵn.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass" từ .agent-secrets/.env, không gõ vào lệnh.
// Mã thoát: 0 xong, 1 lỗi đo hoặc ghi file, 2 thiếu hoặc sai tham số, 4 guard báo lỗi.
import {existsSync, writeFileSync} from 'fs';
import {args, openTab, sleep, DUA} from './_chrome.mjs';
import {verdict, checkTunnel, die as guardDie} from './_guard.mjs';

const o = args(process.argv.slice(2), ['no-guard', 'allow-redirect-host', 'help', 'h', 'apply']);
if (o.help || o.h || !o.url) {
  console.log('Dùng: node img_display_width.mjs --url URL [--widths 360,412,768,1024,1366,1920] [--dpr 1] [--settle 2500] [--resolve host=ip] [--cookie tên=giá trị] [--expect <title>] [--no-guard] [--allow-redirect-host] [--out file.json --apply]\nMô tả đầy đủ ở đầu file script.');
  process.exit(o.help || o.h ? 0 : 2);
}
const widths = String(o.widths || '360,412,768,1024,1366,1920').split(',').map(s => +s.trim());
const dpr = +(o.dpr || 1), settle = +(o.settle || 2500);
if (!widths.length || widths.some(w => !Number.isInteger(w) || w < 200 || w > 4000)) { console.error('--widths phải là danh sách số nguyên từ 200 đến 4000'); process.exit(2); }
if (!(dpr >= 1 && dpr <= 4)) { console.error('--dpr phải từ 1 đến 4'); process.exit(2); }
if (!(settle >= 0 && settle <= 30000)) { console.error('--settle phải từ 0 đến 30000 ms'); process.exit(2); }
let u;
try { u = new URL(o.url); } catch { console.error('--url không hợp lệ'); process.exit(2); }
if (o.out && !o.apply) console.error('Dry-run: --out bị bỏ qua vì chưa có --apply. JSON in ra stdout.');
if (o.apply && !o.out) { console.error('--apply cần --out'); process.exit(2); }
if (o.apply && existsSync(o.out)) { console.error(`${o.out} đã có (script không ghi đè)`); process.exit(1); }

try { await checkTunnel(o.resolve, o.url); } catch (e) { guardDie(e.message); }

const COLLECT = `(async () => {
  const imgs = [...document.images];
  const loading = imgs.map(i => i.getAttribute('loading') || '');
  imgs.forEach(i => { if (i.loading === 'lazy') i.loading = 'eager'; });
  const t0 = performance.now();
  while (performance.now() - t0 < ${settle} && imgs.some(i => !i.complete)) await new Promise(r => setTimeout(r, 100));
  const res = performance.getEntriesByType('resource');
  const widthsOf = s => (s || '').split(',').map(x => x.trim().split(/\\s+/)).filter(p => /^\\d+w$/.test(p[1] || '')).map(p => parseInt(p[1]));
  window.__wpsUrls = imgs.map(i => i.currentSrc);
  return {
    innerWidth: window.innerWidth, scrollWidth: document.documentElement.scrollWidth, host: location.host, title: document.title.slice(0, 120),
    images: imgs.map((i, n) => {
      const r = i.getBoundingClientRect(), cs = getComputedStyle(i), e = res.find(x => x.name === i.currentSrc);
      return {
        src: i.getAttribute('src') || '', currentSrc: i.currentSrc, naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight,
        displayWidth: +r.width.toFixed(1), displayHeight: +r.height.toFixed(1),
        visible: r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden',
        bytes: e ? (e.encodedBodySize || e.transferSize || 0) : 0, srcsetWidths: widthsOf(i.getAttribute('srcset')), loading: loading[n], complete: i.complete,
      };
    }),
  };
})()`;

const PROBE = `(async () => {
  const r = {};
  for (const u of [...new Set(window.__wpsUrls || [])]) {
    if (!u) continue;
    try { const p = new Image(); p.src = u; await p.decode(); r[u] = [p.naturalWidth, p.naturalHeight]; } catch (e) {}
  }
  return r;
})()`;

const tab = await openTab({host: o.host || u.host, resolve: o.resolve, cookie: o.cookie});
let status = null;
tab.on(ev => { if (ev.method === 'Network.responseReceived' && ev.params.type === 'Document' && status === null) status = ev.params.response.status; });
const out = {url: o.url, dpr, widths, status: null, title: '', viewports: []};
try {
  await tab.send('Network.enable');
  await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
  await tab.send('Emulation.setUserAgentOverride', {userAgent: DUA});
  for (const [idx, vw] of widths.entries()) {
    await tab.send('Emulation.setDeviceMetricsOverride', {width: vw, height: 900, deviceScaleFactor: dpr, mobile: false});
    await tab.send('Page.navigate', {url: o.url});
    let ready = false;
    for (let i = 0; i < 200 && !ready; i++) { await sleep(100); ready = (await tab.evalv(`document.readyState === 'complete' && performance.getEntriesByType('navigation')[0]?.loadEventEnd > 0`)) === true; }
    if (!ready) throw new Error(`trang không tải xong ở viewport ${vw}`);
    const r = await tab.evalv(COLLECT, true);
    if (!r) throw new Error(`không đọc được ảnh ở viewport ${vw}`);
    await tab.send('Network.setCacheDisabled', {cacheDisabled: false});
    const dims = (await tab.evalv(PROBE, true)) || {};
    await tab.send('Network.setCacheDisabled', {cacheDisabled: true});
    for (const im of r.images) { const d = dims[im.currentSrc]; im.fileWidth = d ? d[0] : im.naturalWidth; im.fileHeight = d ? d[1] : im.naturalHeight; }
    if (idx === 0) {
      out.status = status; out.title = r.title;
      if (!o['no-guard']) {
        const errs = verdict({requestedHost: u.host, finalHost: r.host, status, title: r.title, expect: o.expect, allowRedirectHost: !!o['allow-redirect-host']});
        console.error(`GUARD host=${r.host} status=${status} title=${JSON.stringify(r.title)}`);
        if (errs.length) { await tab.close(); guardDie(errs); }
      }
    }
    out.viewports.push({vw, innerWidth: r.innerWidth, scrollWidth: r.scrollWidth, images: r.images});
  }
} catch (e) {
  console.error('Lỗi đo: ' + e.message);
  await tab.close();
  process.exit(1);
}
await tab.close();
const json = JSON.stringify(out, null, 1) + '\n';
if (o.apply) { writeFileSync(o.out, json); console.error(`Đã ghi ${o.out}`); } else process.stdout.write(json);
console.error(`IMG_WIDTH url=${o.url} vw=${widths.join(',')} dpr=${dpr} anh=${out.viewports[0].images.length}`);
