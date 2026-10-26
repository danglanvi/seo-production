// Kịch bản tương tác cho test_template.py: thẻ ảnh, bấm Duyệt ở phần ngoài ORDER, sửa hai trường trùng key, kiểm status applied.
// node tests/template_driver.mjs <trang-duyet.html>   (thoát 0 khi đạt, 1 khi sai, in lý do)
import { boot, parseTotals } from '../scripts/kiem_trang_duyet.mjs';
const tpl = process.argv[2];
const fields = [
  { key: 'text', name: 'Đoạn 1', editable: true, before: 'chữ cũ 1', proposed: 'chữ đề xuất 1' },
  { key: 'text', name: 'Đoạn 2', editable: true, before: 'chữ cũ 2', proposed: 'chữ đề xuất 2' },
];
const seed = {
  report: [
    { id: 'summary', data: { sections: [{ key: 'meta', title: 'Meta', state: 'ready' }] } },
    { id: 'meta', data: { items: [{ id: 'm1', url: 'https://example.vn/a/', label: 'A', img: 'anh/m1-truoc-sau.webp', img_alt: 'Trước và sau', img_w: 760, img_h: 400, img_cap: 'Ảnh <b>chụp</b>', fields: [{ key: 'seo_title', name: 'T', max: 65, before: 'a', A: 'b', B: 'a' }] }] } },
    { id: 'r3', data: { items: [{ id: 'r3-x', url: 'https://example.vn/b/', label: 'B', fields }, { id: 'r3-y', url: 'https://example.vn/c/', label: 'C', fields: [{ key: 'text', name: 'D', editable: true, before: 'x', proposed: 'y' }] }] } },
  ],
  reviews: [{ id: 'r3-y', data: { item_id: 'r3-y', status: 'applied', values: { text: 'y' } } }],
};
const fail = (m) => { console.error('SAI: ' + m); process.exit(1); };
const page = await boot(tpl, seed);
let t = parseTotals(page.totalsHtml());
if (t.total !== 3 || t.applied !== 1 || t.pending !== 2) fail('đếm ban đầu ' + JSON.stringify(t));
// 0) Thẻ ảnh: ảnh publish kèm trang hiện trong thẻ, chú thích được escape.
const m1 = page.mainHtml();
if (!m1.includes('<figure class="shot"><a href="anh/m1-truoc-sau.webp"') || !m1.includes('width="760" height="400"')) fail('thẻ ảnh không hiện');
if (m1.includes('<b>chụp</b>') || !m1.includes('&lt;b&gt;chụp&lt;/b&gt;')) fail('chú thích ảnh không escape');
// 1) r3 không có trong summary lẫn ORDER nhưng phải có trong thanh phần và bấm Duyệt chạy được.
if (!page.navHtml().includes('r3')) fail('thanh phần thiếu r3');
await page.click('nav', '', 'r3');
await page.click('approve', 'r3-x');
const rv = page.review('r3-x');
if (!rv || rv.status !== 'approved') fail('Duyệt ở phần r3 không lưu');
t = parseTotals(page.totalsHtml());
if (t.approved !== 1 || t.pending !== 1) fail('đếm sau Duyệt ' + JSON.stringify(t));
// 2) Thẻ đã áp không có nút E và nút Đặt lại.
const html = page.mainHtml();
const blockY = html.slice(html.indexOf('id="c-r3-y"'));
if (/data-act="edit"|data-act="reset"/.test(blockY.slice(0, blockY.indexOf('</article>')))) fail('thẻ applied còn nút E hoặc Đặt lại');
// 3) Hai trường cùng key: sửa riêng từng ô, values phải có text và text#2 khác nhau.
await page.click('reset', 'r3-x');
await page.click('edit', 'r3-x');
page.typeInto('r3-x', 'text', 'một');
page.typeInto('r3-x', 'text#2', 'hai');
await page.click('save', 'r3-x');
const v = page.review('r3-x');
if (!v || v.status !== 'edited' || v.values.text !== 'một' || v.values['text#2'] !== 'hai') fail('values trùng key ' + JSON.stringify(v));
console.log('OK', JSON.stringify(parseTotals(page.totalsHtml())));
