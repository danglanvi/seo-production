// Kiểm đầu cuối lớp sửa: mở file sửa trong Chrome headless, xác nhận 0 khối "đã sửa" lúc đầu, sửa 1 đoạn, lưu bản HTML đã sửa.
// node tests/e2e_sua_truc_tiep.mjs <file sửa.html> <file lưu.html>
import fs from 'node:fs';
import path from 'node:path';
import {openTab, sleep} from '../../wp-pagespeed/scripts/_chrome.mjs';
const [file, saved] = process.argv.slice(2);
const tab = await openTab();
await tab.send('Page.enable');
await tab.send('Page.navigate', {url: 'file://' + path.resolve(file)});
await sleep(2500);
const r = await tab.evalv(`(() => {
  const c0 = window.__ed.collect().edits.length;
  const el = [...document.querySelectorAll('p[data-b]')].find(x => window.__ed.textOf(x).length > 60);
  const before = el.getAttribute('data-t');
  el.textContent = window.__ed.textOf(el) + ' (sửa thử)';
  el.dispatchEvent(new Event('input', {bubbles: true}));
  const c = window.__ed.collect();
  return {c0, block: el.getAttribute('data-b'), before, edits: c.edits, html: window.__ed.serialize()};
})()`);
fs.writeFileSync(saved, r.html);
console.log(JSON.stringify({c0: r.c0, block: r.block, n: r.edits.length, before: r.before.slice(0, 60), text: r.edits[0] && r.edits[0].text.slice(-40)}));
await tab.close();
process.exit(r.c0 === 0 && r.edits.length === 1 ? 0 : 1);
