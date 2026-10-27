// model.mjs (wp-ucss): mô hình selector của một file CSS gộp, và dựng bản CSS gọn từ tập selector đã dùng.
// Gen và build cùng gọi walkSelRules để thứ tự rule giống nhau. Không chạy được với CSS lồng (nesting): rule có rule con được giữ nguyên.
import fs from 'fs';
import { rq } from './lib-ucss.mjs';
const postcss = rq('postcss');
export const csstree = rq('css-tree');
// css-tree cũ (1.0.0-alpha.28 trong cache wp-pagespeed) tách selector khác 3.x: chỉ số selector lệch với kết quả gen, CSS gọn bỏ nhầm rule. Dừng sớm.
if (!/^[3-9]\./.test(csstree.version || '')) throw new Error(`model.mjs cần css-tree 3.x, đang có ${csstree.version || 'bản cũ không ghi version'} (UCSS_NODE_MODULES)`);

const KF = /^(-\w+-)?keyframes$/i;
const unesc = s => s.replace(/\\([0-9a-fA-F]{1,6}\s?|.)/g, (m, c) => /^[0-9a-fA-F]/.test(c) && c.length > 1 ? String.fromCodePoint(parseInt(c, 16)) : c);

// Khoảng trắng U+00A0 đứng đầu khai báo (sau { hoặc ;) làm postcss báo "Unknown word". Chrome coi U+00A0 là ký tự tên, nên khai báo đó
// vốn không hợp lệ và bị bỏ. Đổi dấu cách thường trong chuỗi đầu đó thành U+00A0: tên thuộc tính thành một từ lạ, Chrome vẫn bỏ, postcss đọc được.
// Dấu } thừa ở cấp ngoài cùng làm postcss báo "Unexpected }". Chrome đưa dấu đó vào selector của rule kế tiếp nên bỏ rule đó.
// Đổi } thừa thành ! : selector vẫn không hợp lệ, Chrome bỏ đúng rule đó, postcss đọc được (đã thử CSSOM, site WordPress OLS + LiteSpeed Cache, 26/10/2026).
const strayBrace = css => {
  let d = 0, out = null;
  for (let i = 0; i < css.length; i++) {
    const c = css[i];
    if (c === '/' && css[i + 1] === '*') { const j = css.indexOf('*/', i + 2); i = j < 0 ? css.length : j + 1; continue; }
    if (c === '"' || c === "'") { for (i++; i < css.length && css[i] !== c; i++) if (css[i] === '\\') i++; continue; }
    if ((c === 'u' || c === 'U') && /^url\(\s*[^"'\s]/i.test(css.slice(i, i + 6))) { const j = css.indexOf(')', i); i = j < 0 ? css.length : j; continue; }
    if (c === '{') d++;
    else if (c === '}') { if (d > 0) d--; else (out ||= css.split(''))[i] = '!'; }
  }
  return out ? out.join('') : css;
};
export const fixCss = css => strayBrace(css.replace(/([{;])([\u00a0 \t]*\u00a0[\u00a0 \t]*)(?=[^\s:;{}])/g, (m, a, b) => a + b.replace(/[ \t]/g, '\u00a0')));

// Gọi cb(rule, idx) cho mọi rule có selector, bỏ rule trong @keyframes. idx tăng theo thứ tự duyệt.
export function walkSelRules(root, cb) {
  let i = 0;
  root.walkRules(rule => {
    // Bỏ rule trong @keyframes và rule lồng trong rule khác (CSS nesting: rule cha giữ nguyên cả khối).
    for (let p = rule.parent; p && p.type !== 'root'; p = p.parent) if ((p.type === 'atrule' && KF.test(p.name)) || p.type === 'rule') return;
    cb(rule, i++);
  });
}

// Tách selector thành các compound. Trả null khi css-tree không đọc được hoặc có & (CSS lồng).
function compounds(sel) {
  let ast;
  try { ast = csstree.parse(sel, { context: 'selector' }); } catch (e) { return null; }
  if (ast.type !== 'Selector') return null;
  const out = [{ comb: null, parts: [] }];
  let bad = false;
  ast.children.forEach(n => {
    if (n.type === 'Combinator') out.push({ comb: n.name, parts: [] });
    else {
      if (n.type === 'NestingSelector' || n.type === 'Raw') bad = true;
      out[out.length - 1].parts.push({ t: n.type, s: csstree.generate(n), n: n.type === 'ClassSelector' ? unesc(n.name) : (n.type === 'AttributeSelector' ? unesc(csstree.generate(n.name)) : null) });
    }
  });
  return bad ? null : out;
}

function emit(cs, keep) {
  return cs.map((c, i) => {
    const t = c.parts.filter(keep).map(p => p.s).join('') || '*';
    return i === 0 ? t : (c.comb === ' ' ? ' ' : ` ${c.comb} `) + t;
  }).join('');
}
const PSEUDO = p => p.t !== 'PseudoClassSelector' && p.t !== 'PseudoElementSelector';

// Mô hình: danh sách selector đã bỏ pseudo (duy nhất) để thử querySelector, và với mỗi rule danh sách chỉ số u của từng selector.
// u = -1: selector không đọc được, luôn giữ.
export function buildModel(cssText) {
  const root = postcss.parse(fixCss(cssText));
  const idx = new Map(), list = [], comp = [], rules = [], pseudoSel = [];
  walkSelRules(root, (rule, i) => {
    if (rule.nodes && rule.nodes.some(n => n.type === 'rule' || n.type === 'atrule')) { rules[i] = rule.selectors.map(() => -1); return; }
    rule.selectors.forEach((s, k) => { if (s.includes(':')) pseudoSel.push([i, k, s.trim()]); });
    rules[i] = rule.selectors.map(s => {
      const cs = compounds(s.trim());
      if (!cs) return -1;
      const st = emit(cs, PSEUDO);
      if (!idx.has(st)) { idx.set(st, list.length); list.push(st); comp.push(cs); }
      return idx.get(st);
    });
  });
  const kf = new Set(); root.walkAtRules(a => { if (KF.test(a.name)) kf.add(a.params.trim().replace(/^["']|["']$/g, '').toLowerCase()); });
  return { list, comp, rules, pseudoSel, kf: [...kf], nRules: rules.length };
}

// Bản nới của selector u: bỏ pseudo, bỏ mọi attribute selector, bỏ class "động" (dyn(tên) = true: JS thêm, safelist keep_class),
// bỏ type selector trong optType (thẻ nội dung có thể thêm khi sửa bài: pre, table…). Compound rỗng thành *.
export function relaxed(model, u, dyn, optType = new Set()) {
  const keep = p => {
    if (p.t === 'AttributeSelector') return false;
    if (p.t === 'ClassSelector') return !dyn(p.n);
    if (p.t === 'TypeSelector') return !optType.has(p.s.toLowerCase());
    return PSEUDO(p);
  };
  return emit(model.comp[u], keep);
}

// Safelist: keep_class (regex) và keep_selector dạng ".class" thành hàm dyn; keep_selector dạng thẻ thành optType.
export function loadSafelist(file) {
  const j = JSON.parse(fs.readFileSync(file, 'utf8'));
  const res = (j.keep_class || []).map(x => new RegExp(x.p));
  const cls = new Set(), optType = new Set();
  for (const x of j.keep_selector || []) {
    if (/^\.[\w-]+$/.test(x.p)) cls.add(x.p.slice(1));
    else if (/^[a-z][a-z0-9]*$/i.test(x.p)) optType.add(x.p.toLowerCase());
  }
  return { safeClass: c => cls.has(c) || res.some(r => r.test(c)), optType };
}

// Token chuỗi trong JS: mọi cụm [\w-] trong chuỗi nháy đơn/kép. Token kết thúc bằng - hoặc _ là tiền tố.
export function jsTokens(text, J, P) {
  const re = /"((?:[^"\\\n]|\\.){1,400})"|'((?:[^'\\\n]|\\.){1,400})'|`((?:[^`\\]|\\.){1,400})`/g;
  let m;
  while ((m = re.exec(text))) {
    for (const t of (m[1] || m[2] || m[3]).split(/[^\w-]+/)) {
      if (t.length < 2 || /^\d/.test(t)) continue;
      J.add(t);
      if (/[-_]$/.test(t) && t.length >= 4) P.add(t);
    }
  }
}

const famList = v => v.split(',').map(f => f.trim().replace(/^["']|["']$/g, '').toLowerCase()).filter(Boolean);
const animNames = v => v.split(',').flatMap(a => a.trim().split(/\s+/)).filter(t => /^-?[a-zA-Z_][\w-]*$/.test(t)).map(t => t.toLowerCase());
const fontShorthandFamilies = v => { const m = v.match(/(?:^|\s)(?:[\d.]+(?:px|em|rem|%|pt|vw|vh)?(?:\/[\w.%]+)?)\s+(.+)$/); return m ? famList(m[1]) : []; };

// Dựng CSS gọn. used: Set chỉ số u cần giữ. fams, anims: tên font và animation thấy trong DOM (computed style).
// origInvalid: Set "i:k" của selector gốc Chrome không đọc được (CSS.supports). Rule chứa selector đó giữ nguyên danh sách selector,
// vì lọc bớt sẽ làm rule vốn bị Chrome bỏ qua nay có hiệu lực.
// opt.filterSel: bỏ selector không dùng trong danh sách của rule giữ lại (mặc định tắt: giữ nguyên danh sách, theo Debloat và bản tổng hợp bài học repo).
// opt.pruneFonts: bỏ @font-face, @keyframes không dùng (mặc định tắt ở bản đầu).
export function buildReduced(cssText, model, used, fams0, anims0, origInvalid = new Set(), kfJs = new Set(), opt = {}) {
  const root = postcss.parse(fixCss(cssText));
  const st = { rulesIn: 0, rulesOut: 0, selIn: 0, selOut: 0, ffIn: 0, ffOut: 0, kfIn: 0, kfOut: 0 };
  walkSelRules(root, (rule, i) => {
    const us = model.rules[i];
    st.rulesIn++; st.selIn += us.length;
    const keepIdx = us.map((u, k) => u < 0 || used.has(u) ? k : -1).filter(k => k >= 0);
    if (!keepIdx.length) { rule.remove(); return; }
    st.rulesOut++;
    const anyInvalid = us.some((u, k) => origInvalid.has(i + ':' + k));
    const filt = opt.filterSel && !anyInvalid && keepIdx.length < us.length;
    if (filt) rule.selectors = keepIdx.map(k => rule.selectors[k]);
    st.selOut += filt ? keepIdx.length : us.length;
  });
  // Font và animation dùng: computed style trong DOM, khai báo của rule còn giữ, và chuỗi xuất hiện trong mọi giá trị còn giữ
  // (biến CSS kiểu --e-global-typography-*-font-family, animation đặt qua biến). Tên keyframes có trong JS (kfJs) cũng giữ.
  const fams = new Set(fams0), anims = new Set(anims0);
  let vals = '';
  root.walkDecls(d => {
    for (let p = d.parent; p && p.type !== 'root'; p = p.parent) if (p.type === 'atrule' && (KF.test(p.name) || p.name === 'font-face')) return;
    const prop = d.prop.toLowerCase();
    vals += ' ' + d.value.toLowerCase();
    if (prop === 'font-family') famList(d.value).forEach(f => fams.add(f));
    else if (prop === 'font') fontShorthandFamilies(d.value).forEach(f => fams.add(f));
    else if (prop === 'animation' || prop === 'animation-name' || /^-\w+-animation(-name)?$/.test(prop)) animNames(d.value).forEach(a => anims.add(a));
  });
  const tokRe = n => new RegExp('(^|[^\\w-])' + n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^\\w-])');
  root.walkAtRules(a => {
    if (a.name === 'font-face') {
      st.ffIn++;
      let fam = null; a.walkDecls('font-family', d => { fam = famList(d.value)[0]; });
      if (opt.pruneFonts && fam && !fams.has(fam) && !vals.includes(fam)) a.remove(); else st.ffOut++;
    } else if (KF.test(a.name)) {
      st.kfIn++;
      const n = a.params.trim().replace(/^["']|["']$/g, '').toLowerCase();
      if (opt.pruneFonts && !anims.has(n) && !kfJs.has(n) && !tokRe(n).test(vals)) a.remove(); else st.kfOut++;
    }
  });
  // Bỏ at-rule khối rỗng (@media, @supports, @container, @layer có khối), lặp tới khi không còn.
  let changed = true;
  while (changed) {
    changed = false;
    root.walkAtRules(a => {
      if (!a.nodes || a.nodes.length !== 0 || ['font-face', 'page'].includes(a.name)) return;
      // @layer x {} rỗng thành @layer x; để giữ thứ tự layer.
      if (a.name === 'layer' && a.params.trim()) a.replaceWith(postcss.atRule({ name: 'layer', params: a.params }));
      else a.remove();
      changed = true;
    });
  }
  // Font nhúng data: (base64) trong @font-face: thay bằng URL file font có sẵn trên site (opt.fontSrcRewrite), để bỏ byte nặng khỏi CSS chặn hiển thị.
  for (const fr of opt.fontSrcRewrite || []) {
    root.walkAtRules('font-face', a => {
      let fam = null; a.walkDecls('font-family', d => { fam = famList(d.value)[0]; });
      if (fam !== fr.family.toLowerCase()) return;
      a.walkDecls('src', d => {
        const nv = d.value.replace(/url\(\s*["']?data:[^)]*\)\s*format\(\s*["']?woff2?["']?\s*\)/gi, fr.data_to);
        if (nv !== d.value) { d.value = nv; st.fontRewrite = (st.fontRewrite || 0) + 1; }
      });
    });
  }
  root.walkComments(c => c.remove());
  const out = root.toResult({ map: false }).css.replace(/\n\s*\n/g, '\n');
  return { css: out, stats: st, fams: [...fams], anims: [...anims] };
}
