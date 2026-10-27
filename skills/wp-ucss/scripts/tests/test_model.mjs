// test_model.mjs (wp-ucss): ca kiểm cho model.mjs. node test_model.mjs → in OK/SAI từng ca, mã 1 nếu có ca sai.
import { buildModel, buildReduced, relaxed, jsTokens, fixCss } from '../model.mjs';
import { rq } from '../lib-ucss.mjs';
const postcss = rq('postcss');
let bad = 0;
const eq = (name, a, b) => { const ok = JSON.stringify(a) === JSON.stringify(b); if (!ok) bad++; console.log(ok ? 'OK ' : 'SAI', name, ok ? '' : `\n   có: ${JSON.stringify(a)}\n   cần: ${JSON.stringify(b)}`); };
const parseErr = css => { try { postcss.parse(css); return null; } catch (e) { return e.reason; } };

// 1. Bỏ pseudo: trạng thái, pseudo-element, hàm lồng; escape giữ nguyên; compound rỗng thành *.
{
  const m = buildModel('.a:hover>.b::before{x:1}a:not(:hover) img{x:1}.lg\\:w-full:focus{x:1}.x>:first-child{x:1}::selection{x:1}.c:is(.d,.e) ~ p{x:1}input::-moz-placeholder{x:1}');
  eq('bỏ pseudo', m.list, ['.a > .b', 'a img', '.lg\\:w-full', '.x > *', '*', '.c ~ p', 'input']);
}
// 2. Danh sách selector: cùng chuỗi đã bỏ pseudo dùng chung chỉ số.
{
  const m = buildModel('.a,.a:hover,.b{x:1}');
  eq('chỉ số dùng chung', m.rules[0], [0, 0, 1]);
}
// 3. Rule trong @keyframes không vào mô hình; @keyframes trong @media vẫn đọc tên.
{
  const m = buildModel('@media (min-width:1px){@keyframes k{from{a:1}to{a:2}}.q{animation:k 1s}}');
  eq('keyframes', [m.list, m.kf], [['.q'], ['k']]);
}
// 4. Dựng: giữ thứ tự, giữ cả danh sách selector, bỏ @media rỗng, giữ @layer rỗng dạng câu lệnh.
{
  const css = '.a{x:1}@media (max-width:9px){.z{y:1}}.b,.z{y:2}@layer l{.z{q:1}}.c{x:3}';
  const m = buildModel(css);
  const used = new Set(['.a', '.b', '.c'].map(s => m.list.indexOf(s)));
  eq('dựng', buildReduced(css, m, used, [], []).css, '.a{x:1}.b,.z{y:2}@layer l;.c{x:3}');
  eq('dựng lọc selector', buildReduced(css, m, used, [], [], new Set(), new Set(), { filterSel: true }).css, '.a{x:1}.b{y:2}@layer l;.c{x:3}');
}
// 5. Selector gốc Chrome không đọc được: giữ nguyên danh sách khi lọc.
{
  const css = '.a::-moz-selection,.a::selection{color:red}';
  const m = buildModel(css);
  const r = buildReduced(css, m, new Set([0]), [], [], new Set(['0:0']), new Set(), { filterSel: true });
  eq('selector Chrome lỗi', r.css, css);
}
// 6. Font và keyframes: mặc định giữ hết; pruneFonts bỏ cái không dùng, giữ cái dùng qua biến CSS.
{
  const css = '@font-face{font-family:A;src:url(a)}@font-face{font-family:"B C";src:url(b)}@font-face{font-family:D;src:url(d)}:root{--f:"B C",x}.a{font-family:A}@keyframes k1{}@keyframes k2{}@keyframes k3{}.a{animation:k1 1s;--an:k2}';
  const m = buildModel(css);
  const used = new Set([m.list.indexOf('*'), m.list.indexOf('.a')]);
  eq('giữ hết font', buildReduced(css, m, used, [], []).stats.ffOut, 3);
  const r = buildReduced(css, m, used, [], [], new Set(), new Set(), { pruneFonts: true });
  eq('bỏ font, keyframes thừa', [r.stats.ffOut, r.stats.kfOut, r.css.includes('family:D'), r.css.includes('k3')], [2, 2, false, false]);
}
// 7. Bản nới: class động, attribute, thẻ nội dung.
{
  const m = buildModel('.menu .is-open>a[aria-expanded=true]{x:1}.post pre code{x:1}');
  const dyn = c => c === 'is-open';
  eq('nới', [relaxed(m, 0, dyn), relaxed(m, 1, dyn, new Set(['pre']))], ['.menu * > a', '.post * code']);
}
// 8. Token JS: chuỗi nháy đơn, kép, backtick; tiền tố kết thúc bằng -.
{
  const J = new Set(), P = new Set();
  jsTokens(`a.addClass("is-open active");b.classList.add('mega-toggle-on');c=\`slick-\${i}\``, J, P);
  eq('token JS', [J.has('is-open'), J.has('active'), J.has('mega-toggle-on'), P.has('slick-')], [true, true, true, true]);
}
// 9. Rule lồng (CSS nesting) giữ nguyên.
{
  const css = '.p{a:1;.q{b:2}}.r{c:3}';
  const m = buildModel(css);
  eq('nesting', [m.rules[0], buildReduced(css, m, new Set(), [], []).css.includes('.p{a:1;.q{b:2}}')], [[-1], true]);
}
// 10. Dấu } thừa ở cấp ngoài: postcss báo lỗi; fixCss đổi thành !, rule b thành selector lỗi như Chrome (Chrome bỏ b, giữ c).
{
  const css = 'a{color:red}}b{color:blue}c{x:1}';
  const m = buildModel(css);
  eq('dấu } thừa', [parseErr(css), fixCss(css), m.list, m.rules, buildReduced(css, m, new Set([0]), [], []).css],
    ['Unexpected }', 'a{color:red}!b{color:blue}c{x:1}', ['a', 'c'], [[0], [-1], [1]], 'a{color:red}!b{color:blue}']);
}
// 11. U+00A0 rồi dấu cách đầu khai báo: postcss báo lỗi; fixCss đổi dấu cách thành U+00A0, khai báo vẫn là tên lạ như Chrome đọc.
{
  const css = '.a{x:1;\u00a0 color:red}.b{y:2}';
  const m = buildModel(css);
  eq('U+00A0', [parseErr(css), fixCss(css), m.list, buildReduced(css, m, new Set([0, 1]), [], []).css],
    ['Unknown word color', '.a{x:1;\u00a0\u00a0color:red}.b{y:2}', ['.a', '.b'], '.a{x:1;\u00a0\u00a0color:red}.b{y:2}']);
}
process.exit(bad ? 1 : 0);
