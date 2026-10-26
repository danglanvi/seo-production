// Kiểm trang duyệt offline: chạy script của templates/trang-duyet.html trên DOM giả với bản sao db, rồi so số đếm trên trang với số đếm tính từ bản sao.
// node kiem_trang_duyet.mjs <trang-duyet.html> <thư mục bản sao db> [--json]
// Bản sao db: thư mục có report/*.json (mỗi file một tài liệu phần) và reviews/*.json (mỗi file một thẻ đã duyệt, có item_id).
// Dùng sau khi thêm status mới, đổi truy vấn reviews hoặc đổi danh sách phần. Không gọi mạng, không cần Chrome.
// Thoát mã 0 khi số đếm khớp, 1 khi lệch, 2 khi sai đầu vào.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const STATUSES = ['pending', 'approved', 'edited', 'applied', 'rejected'];

export function readExport(dir) {
  const rd = (sub) => {
    const d = path.join(dir, sub);
    if (!fs.existsSync(d)) return [];
    return fs.readdirSync(d).filter((f) => f.endsWith('.json')).sort().map((f) => {
      let j = JSON.parse(fs.readFileSync(path.join(d, f), 'utf8'));
      if (j && j.data && typeof j.data === 'object' && !Array.isArray(j.data)) j = j.data;
      return { id: f.replace(/\.json$/, ''), data: j };
    });
  };
  return { report: rd('report'), reviews: rd('reviews') };
}

function scriptOf(html) {
  const all = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
  if (!all.length) throw new Error('Không thấy <script> trong template');
  return all[all.length - 1][1];
}

// Kho giả: hỗ trợ collection(), doc().set/delete, where (>=, <, ==), limit, onSnapshot, get.
function fakeDb(seed) {
  const cols = { report: new Map(), reviews: new Map() };
  seed.report.forEach((d) => cols.report.set(d.id, d.data));
  seed.reviews.forEach((d) => cols.reviews.set(d.data.item_id || d.id, d.data));
  const subs = [];
  const run = (name, filters, lim) => {
    let rows = [...cols[name].entries()].sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
    for (const [f, op, v] of filters) {
      rows = rows.filter(([, data]) => {
        const x = data[f];
        if (x === undefined) return false;
        return op === '>=' ? x >= v : op === '<' ? x < v : op === '==' ? x === v : true;
      });
    }
    if (lim) rows = rows.slice(0, lim);
    return { docs: rows.map(([id, data]) => ({ id, data: () => data })) };
  };
  const notify = (name) => subs.filter((s) => s.name === name).forEach((s) => queueMicrotask(() => s.cb(run(name, s.filters, s.lim))));
  const query = (name, filters = [], lim = 0) => ({
    where: (f, op, v) => query(name, filters.concat([[f, op, v]]), lim),
    limit: (n) => query(name, filters, n),
    get: () => Promise.resolve(run(name, filters, lim)),
    onSnapshot: (cb) => { subs.push({ name, filters, lim, cb }); setTimeout(() => cb(run(name, filters, lim)), 0); return () => {}; },
    doc: (id) => ({
      set: (data) => { cols[name].set(id, data); notify(name); return Promise.resolve(); },
      delete: () => { cols[name].delete(id); notify(name); return Promise.resolve(); },
    }),
  });
  return {
    collection: (name) => query(name),
    doc: (p) => query(p.split('/')[0]).doc(p.split('/')[1]),
    cols,
    stats: { queries: () => subs.map((s) => ({ name: s.name, filters: s.filters.length, lim: s.lim })) },
  };
}

function fakeDom() {
  const els = {};
  const el = (id) => (els[id] = els[id] || { id, innerHTML: '', textContent: '', hidden: false, dataset: {}, classList: { toggle() {} }, focus() {} });
  const handlers = {};
  const document = {
    activeElement: null,
    getElementById: el,
    querySelector: () => null,
    addEventListener: (t, fn) => { (handlers[t] = handlers[t] || []).push(fn); },
  };
  return { document, els, handlers };
}

// Khởi động trang. Trả về { totals(), navHtml(), mainHtml(), click(act, id, v), db, settle() }.
export async function boot(templatePath, seed) {
  const script = scriptOf(fs.readFileSync(templatePath, 'utf8'));
  const dom = fakeDom();
  const db = fakeDb(seed);
  const win = {
    scrollTo() {},
    claude: { use: (n) => Promise.resolve(n === 'db' ? db : null) },
  };
  const mem = {};
  const ls = { getItem: (k) => (k in mem ? mem[k] : null), setItem: (k, v) => { mem[k] = String(v); } };
  new Function('document', 'window', 'localStorage', 'location', 'CSS', script)(dom.document, win, ls, { hash: '' }, { escape: (s) => s });
  const settle = () => new Promise((r) => setTimeout(r, 40));
  await settle();
  return {
    db,
    settle,
    totalsHtml: () => dom.els.totals.innerHTML,
    navHtml: () => dom.els.nav.innerHTML,
    mainHtml: () => dom.els.main.innerHTML,
    typeInto: (id, field, value) => {
      const t = { id: '', dataset: { edit: id, field }, value };
      (dom.handlers.input || []).forEach((fn) => fn({ target: t }));
    },
    review: (id) => db.cols.reviews.get(id),
    click: async (act, id, v) => {
      const btn = { dataset: { act, id, v }, disabled: false };
      const ev = { target: { closest: (s) => (s === '[data-act]' ? btn : null) } };
      (dom.handlers.click || []).forEach((fn) => fn(ev));
      await settle();
    },
  };
}

const num = (s) => Number(String(s).replace(/\./g, ''));

// Đọc số đếm từ HTML của header: Tổng, Chờ, Duyệt, Sửa, Đã áp, Bỏ.
export function parseTotals(html) {
  const get = (label) => { const m = html.match(new RegExp(label + ' <b>([\\d.]+)</b>')); return m ? num(m[1]) : null; };
  return { total: get('Tổng'), pending: get('Chờ'), approved: get('Duyệt'), edited: get('Sửa'), applied: get('Đã áp'), rejected: get('Bỏ') };
}

// Số đếm tính từ bản sao: mọi thẻ trong mọi tài liệu report (trừ summary), trạng thái theo reviews, mặc định pending.
export function expectedTotals(seed) {
  const rv = {};
  seed.reviews.forEach((d) => { rv[d.data.item_id || d.id] = d.data.status || 'pending'; });
  const c = { total: 0, pending: 0, approved: 0, edited: 0, applied: 0, rejected: 0 };
  seed.report.forEach((d) => {
    if (d.id === 'summary') return;
    ((d.data && d.data.items) || []).forEach((it) => {
      const s = rv[it.id] || 'pending';
      c.total++;
      c[s] = (c[s] || 0) + 1;
    });
  });
  return c;
}

export async function check(templatePath, dir) {
  const seed = readExport(dir);
  const page = await boot(templatePath, seed);
  const got = parseTotals(page.totalsHtml());
  const want = expectedTotals(seed);
  const diffs = Object.keys(want).filter((k) => got[k] !== want[k]).map((k) => ({ field: k, page: got[k], db: want[k] }));
  return { page: got, db: want, diffs, queries: page.db.stats.queries(), reviews_in_copy: seed.reviews.length };
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;
if (isMain) {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log('node kiem_trang_duyet.mjs <trang-duyet.html> <thư mục bản sao db> [--json]\nSo số đếm trên trang (Tổng, Chờ, Duyệt, Sửa, Đã áp, Bỏ) với số đếm từ bản sao db. Thoát 0 khi khớp, 1 khi lệch, 2 khi sai đầu vào.');
    process.exit(0);
  }
  const [tpl, dir] = args.filter((a) => !a.startsWith('--'));
  if (!tpl || !dir || !fs.existsSync(tpl) || !fs.existsSync(dir)) {
    console.error('Thiếu hoặc sai đường dẫn. Xem --help.');
    process.exit(2);
  }
  const r = await check(tpl, dir);
  if (args.includes('--json')) console.log(JSON.stringify(r, null, 1));
  else {
    console.log('Trạng thái | trên trang | trong bản sao db');
    for (const k of ['total', ...STATUSES]) console.log(`${k} | ${r.page[k]} | ${r.db[k]}${r.page[k] === r.db[k] ? '' : '   LỆCH'}`);
  }
  process.exit(r.diffs.length ? 1 : 0);
}
