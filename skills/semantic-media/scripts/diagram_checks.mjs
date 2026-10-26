// Hàm thuần của diagram_render.mjs: đo chữ nhỏ nhất và chấm đạt/lỗi. Không cần Chrome, test offline được.
// node diagram_checks.mjs --help

// Cỡ chữ nhỏ nhất của danh sách cỡ chữ. Trả null khi danh sách rỗng hoặc không có số hữu hạn.
export function minFontOf(sizes) {
  const ok = (sizes || []).filter(n => typeof n === 'number' && Number.isFinite(n) && n > 0);
  return ok.length ? Math.min(...ok) : null;
}

// minFont có đo được không. JSON.stringify(Infinity) ra null, nên null, NaN, Infinity và chuỗi đều tính là không đo được.
export function isMeasured(minFont) {
  return typeof minFont === 'number' && Number.isFinite(minFont) && minFont > 0;
}

// Chấm cỡ chữ nhỏ nhất theo spec. minText là min_text_height của spec (0 nếu spec không khai).
// Trả {measured, issue, label}: issue là chuỗi lỗi hoặc null; label là đoạn chữ in ra console.
export function judgeMinFont(minFont, minText) {
  if (!isMeasured(minFont)) {
    return {measured: false, issue: 'không đo được chữ nhỏ nhất (không có hộp chữ nào để đo)', label: 'chữ nhỏ nhất không đo được'};
  }
  const label = `chữ nhỏ nhất ${minFont}px`;
  if (minText && minFont < minText * 0.66) return {measured: true, issue: `chữ nhỏ nhất ${minFont}px, spec ${minText}px`, label};
  return {measured: true, issue: null, label};
}

const HELP = `diagram_checks.mjs: hàm đo chữ nhỏ nhất cho diagram_render.mjs.
Dùng làm module: import {minFontOf, isMeasured, judgeMinFont} from './diagram_checks.mjs'.
Dùng dòng lệnh để thử nhanh: node diagram_checks.mjs <minFont|null> [minText]
  Ví dụ: node diagram_checks.mjs null 24   -> "không đo được", mã thoát 1
         node diagram_checks.mjs 20 24     -> "đạt", mã thoát 0
Mã thoát 0 khi đo được và đạt, 1 khi lỗi, 2 khi sai tham số.`;

import {fileURLToPath} from 'node:url';
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const a = process.argv.slice(2);
  if (a.includes('--help') || a.includes('-h')) { console.log(HELP); process.exit(0); }
  if (!a.length) { console.error(HELP); process.exit(2); }
  const v = a[0] === 'null' ? null : Number(a[0]);
  const minText = a[1] === undefined ? 0 : Number(a[1]);
  if ((a[0] !== 'null' && Number.isNaN(v)) || Number.isNaN(minText)) { console.error('tham số phải là số hoặc null'); process.exit(2); }
  const r = judgeMinFont(v, minText);
  console.log(r.issue ? `LỖI: ${r.issue}` : `đạt: ${r.label}`);
  process.exit(r.issue ? 1 : 0);
}
