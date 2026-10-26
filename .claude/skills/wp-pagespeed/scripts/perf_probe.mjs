// Bản của skill wp-pagespeed. Đổi Chrome bằng biến CHROME_BIN.
// Đo tốc độ tải bằng Chrome mô phỏng:
// Chrome headless, mobile 412×823 DPR 1,75, mạng 4G chậm 1,6 Mbps, trễ 150 ms, CPU x4; desktop 1350×940 không giới hạn.
// Mỗi lượt mở một Chrome mới và tắt cache, nên DNS, kết nối và tài nguyên đều tải lại từ đầu như lượt đo của PSI.
// node "$WPS/scripts/perf_probe.mjs" --url URL [--dev mobile|desktop] [--runs 3] [--label tên] [--resolve host=ip] [--cookie tên=giá trị]
//   [--expect '<chuỗi trong title>'] [--min-lcp 100] [--no-guard] [--allow-redirect-host] [--done <file>] [--detail]
// Guard chống đo nhầm đích: sau lượt đầu in dòng "GUARD host=<host thật> status=<HTTP> title=<title>". Thoát mã 4, bỏ số đo, khi:
//   status >= 400 hoặc không có status, host thật khác host của URL (redirect), title không chứa --expect, LCP dưới --min-lcp ms (mặc định 100).
//   Có --resolve thì kiểm cổng của ip trước khi mở Chrome (tunnel staging đã tắt thì thoát mã 4 ngay). --no-guard tắt guard khi cố ý.
//   Desktop chạy máy cục bộ nhanh có thể có LCP dưới 100 ms hợp lệ: đặt --min-lcp 0 hoặc dùng mobile.
// --done <file>: khi xong ghi một dòng "PROBE_DONE exit=<mã>" vào file (cho lệnh chạy nền). Chỉ ghi file này.
// Mã thoát: 0 xong, 2 thiếu tham số, 4 guard báo lỗi.
// Staging có Basic Auth: đặt CDP_AUTH="user:pass" từ .agent-secrets/.env, không gõ vào lệnh. Header chỉ gắn cho request tới đúng host của URL.
// In một dòng JSON mỗi lượt và một dòng "median". Chỉ số: ttfb, fcp, lcp, tbt (tổng phần vượt 50 ms của long task sau FCP), cls, kb, reqs.
import {spawn} from 'child_process';
import {mkdtempSync, rmSync} from 'fs';
import {tmpdir} from 'os';
import {join} from 'path';
import {writeFileSync} from 'fs';
import {verdict, line as guardLine, checkTunnel, GUARD_EXIT, MIN_LCP_MS} from './_guard.mjs';

const a = process.argv.slice(2), opt = {};
for (let i = 0; i < a.length; i++) {
  const k = a[i].replace(/^--/, '');
  opt[k] = (a[i + 1] && !a[i + 1].startsWith('--')) ? a[++i] : true;
}
if (opt.help || opt.h || !opt.url) {
  console.log('Dùng: node perf_probe.mjs --url URL [--dev mobile|desktop] [--runs 3] [--label tên] [--resolve host=ip] [--cookie tên=giá trị] [--expect <title>] [--min-lcp 100] [--no-guard] [--allow-redirect-host] [--done <file>] [--detail]\nMô tả đầy đủ ở đầu file script.');
  process.exit(opt.help || opt.h ? 0 : 2);
}
const doneFile = typeof opt.done === 'string' ? opt.done : null;
const finish = code => { if (doneFile) writeFileSync(doneFile, `PROBE_DONE exit=${code}\n`); process.exit(code); };
const url = opt.url, mob = (opt.dev || 'mobile') === 'mobile', runs = +(opt.runs || 3), host = new URL(url).host, label = opt.label || new URL(url).pathname;
const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MUA = 'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36';
const DUA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const auth = process.env.CDP_AUTH ? 'Basic ' + Buffer.from(process.env.CDP_AUTH).toString('base64') : null;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const median = xs => { const s = [...xs].sort((p, q) => p - q), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

const OBS = `window.__p={lcp:0,el:'',cls:0,lt:[]};
new PerformanceObserver(l=>{for(const e of l.getEntries()){__p.lcp=e.startTime;const n=e.element;__p.el=n?(n.tagName.toLowerCase()+(n.id?'#'+n.id:'')+(e.url?' '+e.url.split('/').pop().slice(0,48):'')):''}}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){__p.cls+=e.value;if(e.value>=0.005)(__p.sh=__p.sh||[]).push([Math.round(e.startTime),+e.value.toFixed(3),(e.sources||[]).map(s=>s.node?(s.node.nodeName||'').toLowerCase()+(s.node.className&&typeof s.node.className==='string'?'.'+s.node.className.split(' ')[0]:''):'').join('|')])}}).observe({type:'layout-shift',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())__p.lt.push([e.startTime,e.duration])}).observe({type:'longtask',buffered:true});`;
const COLLECT = `(()=>{const n=performance.getEntriesByType('navigation')[0]||{},f=(performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime||0;
return {host:location.host,title:document.title.slice(0,120),ttfb:Math.round(n.responseStart||0),fcp:Math.round(f),lcp:Math.round(__p.lcp),tbt:Math.round(__p.lt.filter(x=>x[0]>=f).reduce((t,x)=>t+Math.max(0,x[1]-50),0)),
cls:+__p.cls.toFixed(3),shifts:(__p.sh||[]).slice(0,4),dom:document.getElementsByTagName('*').length,el:__p.el,theme:[...new Set(performance.getEntriesByType('resource').map(r=>r.name).concat([...document.querySelectorAll('[href*="/themes/"],[src*="/themes/"]')].map(e=>e.href||e.src)).filter(h=>/\\/themes\\//.test(h)).map(h=>h.replace(/.*\\/themes\\/([^/?#]+).*/,'$1')))].join('+')||'-'}})()`;

async function once() {
  const port = 9300 + Math.floor(Math.random() * 400), prof = mkdtempSync(join(tmpdir(), 'perf-'));
  const flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
    '--no-first-run', '--no-default-browser-check', '--ignore-certificate-errors'];
  if (opt.resolve) { const [h, ip] = String(opt.resolve).split('='); flags.push(`--host-resolver-rules=MAP ${h} ${ip}`); }
  const chrome = spawn(CHROME, [...flags, 'about:blank'], {stdio: 'ignore'});
  try {
    let list;
    for (let i = 0; i < 60 && !list; i++) { await sleep(150); try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch {} }
    const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
    let id = 0, loaded = false;
    const pend = {}, net = {bytes: 0, reqs: 0, status: null}, req = {};
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; return; }
      if (m.method === 'Fetch.requestPaused') {
        const headers = Object.entries(m.params.request.headers).map(([name, value]) => ({name, value}));
        if (auth) headers.push({name: 'Authorization', value: auth});
        ws.send(JSON.stringify({id: ++id, method: 'Fetch.continueRequest', params: {requestId: m.params.requestId, headers}}));
      } else if (m.method === 'Network.responseReceived') {
        if (m.params.type === 'Document' && net.status === null) net.status = m.params.response.status;
      } else if (m.method === 'Network.requestWillBeSent') {
        net.reqs++;
        req[m.params.requestId] = {url: m.params.request.url, type: m.params.type, pri: m.params.request.initialPriority, t0: m.params.timestamp};
      } else if (m.method === 'Network.loadingFinished') {
        net.bytes += m.params.encodedDataLength;
        if (req[m.params.requestId]) Object.assign(req[m.params.requestId], {kb: m.params.encodedDataLength / 1024, t1: m.params.timestamp});
      }
      else if (m.method === 'Page.loadEventFired') loaded = true;
    };
    await new Promise(r => ws.onopen = r);
    const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
    await send('Page.enable'); await send('Network.enable'); await send('Network.setCacheDisabled', {cacheDisabled: true});
    // Chặn đúng host của URL ở cả staging lẫn production để độ trễ do chặn request như nhau; chỉ staging được gắn Basic Auth.
    await send('Fetch.enable', {patterns: [{urlPattern: `https://${host}/*`, requestStage: 'Request'}]});
    for (const c of String(opt.cookie || '').split(';').filter(Boolean)) { const [n, v] = c.split('='); await send('Network.setCookie', {name: n, value: v, domain: host, path: '/', secure: true}); }
    await send('Emulation.setDeviceMetricsOverride', mob ? {width: 412, height: 823, deviceScaleFactor: 1.75, mobile: true} : {width: 1350, height: 940, deviceScaleFactor: 1, mobile: false});
    await send('Network.setUserAgentOverride', {userAgent: mob ? MUA : DUA});
    if (mob) {
      await send('Network.emulateNetworkConditions', {offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8});
      await send('Emulation.setCPUThrottlingRate', {rate: 4});
    }
    await send('Page.addScriptToEvaluateOnNewDocument', {source: OBS});
    await send('Page.navigate', {url});
    for (let i = 0; i < 160 && !loaded; i++) await sleep(250);
    await sleep(5000);
    const r = await send('Runtime.evaluate', {expression: COLLECT, returnByValue: true});
    if (opt.detail) {
      // --detail: 15 request nặng nhất, kèm loại, độ ưu tiên và mốc bắt đầu, kết thúc (ms tính từ request đầu tiên).
      const rs = Object.values(req), t0 = Math.min(...rs.map(x => x.t0));
      rs.filter(x => x.kb).sort((p, q) => q.kb - p.kb).slice(0, 15).forEach(x => console.log(
        `  ${x.kb.toFixed(1).padStart(7)} KB ${String(x.type).padEnd(10)} ${String(x.pri).padEnd(8)} ${String(Math.round((x.t0 - t0) * 1000)).padStart(6)}→${String(Math.round((x.t1 - t0) * 1000)).padEnd(6)} ${x.url.replace(/^https?:\/\//, '').slice(0, 90)}`));
    }
    return {...r.result.result.value, status: net.status, kb: Math.round(net.bytes / 1024), reqs: net.reqs};
  } finally {
    chrome.kill('SIGKILL');
    await sleep(300);
    try { rmSync(prof, {recursive: true, force: true}); } catch {}
  }
}

if (!opt['no-guard']) {
  try { await checkTunnel(opt.resolve, url); } catch (e) { console.error('GUARD LỖI: ' + e.message); finish(GUARD_EXIT); }
}
const all = [];
for (let i = 1; i <= runs; i++) {
  const m = await once();
  all.push(m);
  const {host: realHost, title, status, ...rest} = m;
  if (!opt['no-guard']) {
    const errs = verdict({requestedHost: host, finalHost: realHost, status, title, expect: opt.expect === true ? undefined : opt.expect,
      lcp: m.lcp, minLcp: opt['min-lcp'] !== undefined ? +opt['min-lcp'] : MIN_LCP_MS, allowRedirectHost: !!opt['allow-redirect-host']});
    if (i === 1 || errs.length) console.log(guardLine({host: realHost, status, title}));
    if (errs.length) { console.error('GUARD LỖI: ' + errs.join('; ') + '. Số đo bỏ, kiểm URL, --expect, tunnel rồi chạy lại (hoặc --no-guard nếu cố ý).'); finish(GUARD_EXIT); }
  }
  console.log(JSON.stringify({label, dev: mob ? 'mobile' : 'desktop', run: i, status, ...rest}));
}
const keys = ['ttfb', 'fcp', 'lcp', 'tbt', 'cls', 'kb', 'reqs', 'dom'];
console.log(JSON.stringify({label, dev: mob ? 'mobile' : 'desktop', run: 'median', ...Object.fromEntries(keys.map(k => [k, median(all.map(x => x[k]))])), el: all[0].el, theme: all[0].theme}));
finish(0);
