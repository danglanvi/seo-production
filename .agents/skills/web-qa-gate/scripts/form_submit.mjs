// Gửi form THẬT một lần để kiểm form gửi mail và lưu được. Lệnh này tạo lead thật và gửi mail tới hộp thư thật.
// Chỉ gọi qua: qa_gate.py run --submit-live (qa_gate.py kiểm duyệt production trước). Không gọi trực tiếp.
// node form_submit.mjs --submit-live --url URL --data data.json --token QA-... --out kq.json [--form "form.sel"] [--success "sel hoặc chữ"]
// Chặn 2 lớp: cần cờ --submit-live VÀ biến môi trường WEB_QA_SUBMIT_LIVE bằng đúng host của URL.
// data.json: {"tên trường": "giá trị"}; chuỗi {token} được thay bằng --token để người vận hành tìm mail.
import fs from 'node:fs';
import {args, openTab, sleep, DUA} from './_cdp.mjs';

const o = args(process.argv.slice(2), ['submit-live']);
const host = new URL(o.url).host;
if (!o['submit-live'] || process.env.WEB_QA_SUBMIT_LIVE !== host) {
  console.error(`từ chối: cần --submit-live và WEB_QA_SUBMIT_LIVE=${host}`);
  process.exit(2);
}
const data = JSON.parse(fs.readFileSync(o.data, 'utf8'));
for (const k in data) data[k] = String(data[k]).replaceAll('{token}', o.token);
// Chặn analytics để lượt thử không thành chuyển đổi trong báo cáo. Không chặn endpoint của form.
const block = ['*googletagmanager.com*', '*google-analytics.com*', '*analytics.google.com*', '*facebook.net*', '*facebook.com/tr*', '*doubleclick.net*', '*clarity.ms*'];
const tab = await openTab({host, block});
const {send, evalv, events} = tab;
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', {width: 1366, height: 900, deviceScaleFactor: 1, mobile: false});
await send('Network.setUserAgentOverride', {userAgent: DUA});
await send('Page.navigate', {url: o.url});
for (let i = 0; i < 60 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(500);
await sleep(2500);
const fill = await evalv(`(()=>{const data=${JSON.stringify(data)};
  const f=${o.form ? `document.querySelector(${JSON.stringify(o.form)})` : `[...document.forms].find(f=>!f.querySelector('input[name="s"],input[type="search"]'))`};
  if(!f)return {err:'không thấy form'};
  const miss=[];for(const k in data){const el=f.querySelector('[name="'+k+'"]');if(!el){miss.push(k);continue}
    el.focus();el.value=data[k];el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}
  if(miss.length)return {err:'thiếu trường',miss};
  const b=f.querySelector('[type=submit],button:not([type=button])');if(!b)return {err:'không thấy nút gửi'};
  b.click();return {ok:true}})()`);
let ok = false, posts = [];
if (fill && fill.ok) {
  for (let i = 0; i < 40 && !ok; i++) {
    await sleep(500);
    posts = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.method === 'POST').map(e => e.params.requestId);
    if (o.success) ok = !!(await evalv(`(()=>{const s=${JSON.stringify(o.success)};try{const e=document.querySelector(s);if(e&&e.offsetParent!==null)return true}catch{}return document.body.innerText.includes(s)})()`));
  }
}
const status = events.filter(e => e.method === 'Network.responseReceived' && posts.includes(e.params.requestId))
  .map(e => ({url: e.params.response.url.slice(0, 120), status: e.params.response.status}));
const res = {url: o.url, token: o.token, time: new Date().toISOString(), fill, success_seen: ok, posts: status};
fs.writeFileSync(o.out, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res));
await tab.close();
process.exit(fill && fill.ok ? 0 : 1);
