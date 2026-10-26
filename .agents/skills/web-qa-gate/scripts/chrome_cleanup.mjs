// Dọn Chrome mồ côi do các script web-qa-gate để lại (profile tạm wqg-* mà tiến trình node mở nó đã chết).
// node chrome_cleanup.mjs            chỉ liệt kê (dry-run, mặc định)
// node chrome_cleanup.mjs --apply    giết Chrome mồ côi và xoá thư mục profile của nó
// Chrome của lượt chạy khác đang sống không bị đụng: script chỉ đụng profile có owner.pid đã chết.
// Mã thoát: 0 xong, 1 lỗi khi dọn, 2 sai tham số.
import {args, sweepOrphans} from './_cdp.mjs';
import {tmpdir} from 'node:os';

const o = args(process.argv.slice(2), ['help', 'apply']);
if (o.help) {
  console.log('chrome_cleanup.mjs [--apply] [--tmp <thư mục>]\n  mặc định chỉ liệt kê (dry-run). --apply giết Chrome mồ côi và xoá profile.\n  --tmp  thư mục chứa profile wqg-* (mặc định: thư mục tạm của hệ thống).');
  process.exit(0);
}
const bad = Object.keys(o).filter(k => k !== '_' && !['apply', 'tmp'].includes(k));
if (bad.length || o._.length) { console.error('tham số lạ: ' + [...bad, ...o._].join(', ')); process.exit(2); }
try {
  const list = sweepOrphans({apply: !!o.apply, tmp: typeof o.tmp === 'string' ? o.tmp : tmpdir()});
  for (const x of list) console.log(`${o.apply ? 'đã dọn' : 'mồ côi'}: ${x.dir} (chủ ${x.owner ?? 'không rõ'}, Chrome ${x.pids.length ? x.pids.join(',') : 'không còn chạy'})`);
  console.log(`${list.length} thư mục mồ côi${o.apply ? ' đã dọn' : '. Thêm --apply để dọn.'}`);
} catch (e) { console.error('lỗi: ' + e.message); process.exit(1); }
