// Test đơn vị cho _cascade.mjs, không cần Chrome. Chạy: node tests/cascade_unit.mjs  (mã thoát 1 khi có ca sai)
import assert from 'node:assert/strict';
import {specificity, resolveProps, cmpDecl, declsFromStyle} from '../_cascade.mjs';

const cases = [
  ['p', [0, 0, 1]],
  ['.a p', [0, 1, 1]],
  ['.a .b .c p', [0, 3, 1]],
  ['.accordion-list .accordion-item .accordion-body .expanded-content-1 p', [0, 4, 1]],
  ['#x .y', [1, 1, 0]],
  ['a[href^="http"]:hover', [0, 2, 1]],
  [':where(.a, .b) p', [0, 0, 1]],
  [':is(.a, #b) p', [1, 0, 1]],
  [':not(.a) p', [0, 1, 1]],
  ['li:nth-child(2n+1)', [0, 1, 1]],
  ['p::before', [0, 0, 2]],
  ['*', [0, 0, 0]],
  ['ul > li + li', [0, 0, 3]],
  ['[data-x="a.b#c"]', [0, 1, 0]],
  ['.a\\:b', [0, 1, 0]],
];
for (const [sel, want] of cases) assert.deepEqual(specificity(sel), want, sel);

const D = (o) => ({prop: 'font-size', value: '16px', important: false, spec: [0, 0, 1], order: 0, origin: 'author', inline: false, layer: null, ...o});
// Ca hỏng thật 19–20/10/2026: accordion 12px do theme ép bằng selector 4 lớp. Luật 1 lớp ép 16px thua.
let r = resolveProps([
  D({value: '12px', spec: specificity('.accordion-list .accordion-item .accordion-body .expanded-content-1 p'), order: 1}),
  D({value: '16px', spec: specificity('.accordion-body p'), order: 5}),
]);
assert.equal(r[0].winner.value, '12px');
assert.match(r[0].overridden[0].why, /specificity thấp hơn/);
assert.match(r[0].need, /> \(0,4,1\)/);
// !important đè specificity cao
r = resolveProps([D({value: '20px', important: true, spec: [0, 1, 1]}), D({value: '12px', spec: [1, 0, 0]})]);
assert.equal(r[0].winner.value, '20px');
// inline thắng rule thường, nhưng rule !important thắng inline thường
r = resolveProps([D({value: '10px', inline: true, spec: [1, 0, 0]}), D({value: '30px', spec: [0, 9, 9]})]);
assert.equal(r[0].winner.value, '10px');
r = resolveProps([D({value: '10px', inline: true, spec: [1, 0, 0]}), D({value: '30px', important: true, spec: [0, 0, 1]})]);
assert.equal(r[0].winner.value, '30px');
// Cùng specificity: rule nạp sau thắng
r = resolveProps([D({value: 'a', order: 1}), D({value: 'b', order: 2})]);
assert.equal(r[0].winner.value, 'b'); assert.match(r[0].overridden[0].why, /nạp trước/);
// CSS mặc định của trình duyệt thua
assert.ok(cmpDecl(D({origin: 'author'}), D({origin: 'ua', spec: [0, 9, 9], order: 9})) > 0);
// @layer: rule không layer thắng rule có layer (thường); đảo ngược với !important
assert.equal(resolveProps([D({value: 'L', layer: 'base', spec: [1, 0, 0]}), D({value: 'U'})])[0].winner.value, 'U');
assert.equal(resolveProps([D({value: 'L', layer: 'base', important: true}), D({value: 'U', important: true})])[0].winner.value, 'L');
// Chuẩn hoá cssProperties của CDP: bỏ bản trùng, giữ longhand sinh từ shorthand, tách !important
const ds = declsFromStyle({cssProperties: [
  {name: 'font-size', value: '20px!important', important: true, text: 'font-size:20px!important'},
  {name: 'font-size', value: '20px !important', important: true},
  {name: 'margin', value: '0 0 10px', text: 'margin:0 0 10px'},
  {name: 'margin-top', value: '0px'},
]}, {selector: 'p'});
assert.deepEqual(ds.map(d => [d.prop, d.value, d.important, d.implicit]), [['font-size', '20px', true, false], ['margin', '0 0 10px', false, false], ['margin-top', '0px', false, true]]);
console.log('cascade_unit: OK');
