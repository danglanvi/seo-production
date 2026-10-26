// Logic cascade CSS thuần (không cần Chrome): specificity, chọn rule thắng cho từng thuộc tính, giải thích vì sao rule khác thua.
// match.mjs dùng file này; tests/cascade_unit.mjs kiểm riêng.
// Thứ tự thắng (CSS Cascade 4): mức origin + !important, rồi @layer, rồi inline style, rồi specificity (a,b,c), rồi thứ tự nạp.
// Giới hạn: không phân biệt thứ tự giữa hai @layer có tên; gặp trường hợp này thì đặt cờ layerUncertain.

function skipBalanced(s, i, open, close) {
  let depth = 0, q = null;
  for (; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === '\\') i++; else if (c === q) q = null; continue; }
    if (c === '"' || c === "'") { q = c; continue; }
    if (c === open) depth++;
    else if (c === close && --depth === 0) return i;
  }
  return s.length - 1;
}

function splitTop(s) {
  const out = []; let depth = 0, q = null, cur = '';
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) { cur += c; if (c === '\\') cur += s[++i] || ''; else if (c === q) q = null; continue; }
    if (c === '"' || c === "'") { q = c; cur += c; continue; }
    if (c === '(' || c === '[') depth++;
    if (c === ')' || c === ']') depth--;
    if (c === ',' && depth === 0) { out.push(cur); cur = ''; continue; }
    cur += c;
  }
  out.push(cur);
  return out.map(x => x.trim()).filter(Boolean);
}

const IDENT = /[A-Za-z0-9_¡-￿-]/;
const LEGACY_PE = new Set(['before', 'after', 'first-line', 'first-letter']);

export function cmpSpec(x, y) { return x[0] - y[0] || x[1] - y[1] || x[2] - y[2]; }
export const fmtSpec = s => `(${s[0]},${s[1]},${s[2]})`;

export function specificity(sel) {
  let a = 0, b = 0, c = 0, i = 0;
  const s = String(sel);
  const ident = () => { let j = i; while (j < s.length && (IDENT.test(s[j]) || s[j] === '\\')) { if (s[j] === '\\') j++; j++; } const t = s.slice(i, j); i = j; return t; };
  while (i < s.length) {
    const ch = s[i];
    if (ch === '#') { i++; ident(); a++; }
    else if (ch === '.') { i++; ident(); b++; }
    else if (ch === '[') { i = skipBalanced(s, i, '[', ']') + 1; b++; }
    else if (ch === ':') {
      if (s[i + 1] === ':') { i += 2; ident(); if (s[i] === '(') i = skipBalanced(s, i, '(', ')') + 1; c++; continue; }
      i++;
      const name = ident().toLowerCase();
      if (s[i] === '(') {
        const end = skipBalanced(s, i, '(', ')'), inner = s.slice(i + 1, end);
        i = end + 1;
        if (name === 'where') continue;
        if (['is', 'not', 'has', 'matches', '-webkit-any', '-moz-any'].includes(name)) {
          const m = splitTop(inner).map(specificity).reduce((p, q) => cmpSpec(p, q) >= 0 ? p : q, [0, 0, 0]);
          a += m[0]; b += m[1]; c += m[2];
        } else if (/^nth-(last-)?(child|of-type)$/.test(name)) {
          b++;
          const of = inner.split(/\s+of\s+/i)[1];
          if (of) { const m = splitTop(of).map(specificity).reduce((p, q) => cmpSpec(p, q) >= 0 ? p : q, [0, 0, 0]); a += m[0]; b += m[1]; c += m[2]; }
        } else b++;
      } else if (LEGACY_PE.has(name)) c++;
      else b++;
    }
    else if (ch === '*' || ch === '&' || ch === '>' || ch === '+' || ch === '~' || ch === ' ' || ch === '\t' || ch === '\n' || ch === ',' || ch === '|') i++;
    else if (IDENT.test(ch) || ch === '\\') { ident(); c++; }
    else i++;
  }
  return [a, b, c];
}

// d: {prop, value, important, spec:[a,b,c], order, origin:'author'|'ua', inline, layer:null|string}
function tier(d) { return d.important ? (d.origin === 'ua' ? 3 : 2) : (d.origin === 'ua' ? 0 : 1); }
function layerRank(d) { const r = d.layer ? 0 : 1; return d.important ? 1 - r : r; }

// > 0 khi x thắng y.
export function cmpDecl(x, y) {
  return tier(x) - tier(y)
    || layerRank(x) - layerRank(y)
    || (x.inline ? 1 : 0) - (y.inline ? 1 : 0)
    || cmpSpec(x.spec, y.spec)
    || x.order - y.order;
}

export function whyLost(w, d) {
  if (tier(w) !== tier(d)) {
    if (w.important && !d.important) return '!important của rule thắng đè khai báo thường';
    if (d.origin === 'ua') return 'CSS mặc định của trình duyệt luôn thua CSS của site';
    return 'mức origin/!important thấp hơn';
  }
  if (layerRank(w) !== layerRank(d)) return 'nằm trong @layer thứ tự thấp hơn';
  if (!!w.inline !== !!d.inline) return w.inline ? 'inline style thắng mọi selector cùng mức' : 'rule thắng có !important hoặc inline đè';
  const c = cmpSpec(w.spec, d.spec);
  if (c > 0) return `specificity thấp hơn ${fmtSpec(d.spec)} < ${fmtSpec(w.spec)}`;
  return `cùng specificity ${fmtSpec(d.spec)}, nạp trước rule thắng`;
}

// Cách đè một rule thắng bằng rule mới (gợi ý để chọn selector, không thay cho việc sửa nguồn).
export function needToBeat(w) {
  if (w.inline && w.important) return 'inline có !important: không rule CSS nào đè được. Sửa nguồn (PHP, Elementor).';
  if (w.inline) return 'inline thắng mọi selector thường. Dùng !important trong CSS có scope, hoặc sửa nguồn của style="" (PHP, Elementor).';
  if (w.important) return `rule thắng có !important. Cần !important với specificity > ${fmtSpec(w.spec)} (hoặc bằng và nạp sau), hoặc sửa nguồn.`;
  return `Cần specificity > ${fmtSpec(w.spec)}, hoặc bằng và nạp sau file nguồn, hoặc !important. Ưu tiên sửa nguồn.`;
}

export function resolveProps(decls) {
  const by = new Map();
  for (const d of decls) { if (!by.has(d.prop)) by.set(d.prop, []); by.get(d.prop).push(d); }
  const out = [];
  for (const [prop, list] of by) {
    const sorted = [...list].sort((x, y) => cmpDecl(y, x));
    const winner = sorted[0];
    const layers = new Set(list.filter(d => d.layer).map(d => d.layer));
    out.push({
      prop, winner,
      overridden: sorted.slice(1).map(d => ({...d, why: whyLost(winner, d)})),
      layerUncertain: layers.size > 1,
      need: needToBeat(winner),
    });
  }
  return out.sort((x, y) => x.prop.localeCompare(y.prop));
}

// Chuẩn hoá cssProperties của CDP: bỏ bản trùng không có text, giữ longhand do shorthand sinh ra (implicit).
export function declsFromStyle(style, meta) {
  const props = (style && style.cssProperties) || [];
  const explicit = new Set(props.filter(p => p.text !== undefined && !p.disabled).map(p => p.name));
  const out = [];
  for (const p of props) {
    if (p.disabled || p.value === undefined) continue;
    const isExplicit = p.text !== undefined;
    if (!isExplicit && explicit.has(p.name)) continue;
    const imp = !!p.important || /!\s*important\s*$/i.test(p.value);
    out.push({
      ...meta, prop: p.name, value: p.value.replace(/\s*!\s*important\s*$/i, '').trim(), important: imp, implicit: !isExplicit,
      range: p.range || null,
    });
  }
  return out;
}
