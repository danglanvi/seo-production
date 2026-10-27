// build.mjs (wp-ucss): gộp kết quả gen theo file CSS gộp, dựng bản CSS gọn và bảng số.
// node build.mjs --site <site.json> <outDir> [safelist.txt]. Ghi <outDir>/reduced/<hash>.css và <outDir>/build.json.
// safelist.txt: mỗi dòng một regex; selector đã bỏ pseudo khớp regex thì luôn giữ. font_src_rewrite lấy từ safelist JSON của site.
import fs from 'fs';
import zlib from 'zlib';
import { site, args, asset } from './lib-ucss.mjs';
import { buildModel, buildReduced } from './model.mjs';

const [outDir, safeFile] = args();
const SAFELIST = JSON.parse(fs.readFileSync(site().safelist, 'utf8'));
const SAFE = safeFile && fs.existsSync(safeFile) ? fs.readFileSync(safeFile, 'utf8').split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#')).map(l => new RegExp(l)) : [];
fs.mkdirSync(outDir + '/reduced', { recursive: true });
const groups = new Map();
for (const f of fs.readdirSync(outDir + '/pages')) {
  const r = JSON.parse(fs.readFileSync(`${outDir}/pages/${f}`, 'utf8'));
  if (!r.hash || r.err) continue;
  if (!groups.has(r.hash)) groups.set(r.hash, { href: r.href, pages: [] });
  groups.get(r.hash).pages.push(r);
}
const br = b => zlib.brotliCompressSync(b, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } }).length;
const out = [];
for (const [hash, g] of groups) {
  const css = (await asset(g.href)).body.toString('utf8');
  const m = buildModel(css);
  // Quét trước: cú pháp cần nhánh riêng và url() tương đối (file gọn đặt thư mục khác thì url tương đối sẽ sai).
  const scan = {
    layer: (css.match(/@layer\b/g) || []).length, container: (css.match(/@container\b/g) || []).length, scope: (css.match(/@scope\b/g) || []).length,
    nestRules: m.rules.filter(x => x.length && x.every(u => u === -1)).length, parseFail: m.rules.reduce((a, x) => a + x.filter(u => u === -1).length, 0),
    relUrl: (css.match(/url\(\s*(?!["']?(?:\/|https?:|data:|#))[^)]*\)/g) || []).slice(0, 5),
  };
  const keep = new Set(), fams = new Set(), anims = new Set(), kfJs = new Set();
  let nUsed = 0, nRelax = 0;
  for (const r of g.pages) {
    r.used.forEach(u => keep.add(u)); r.invalid.forEach(u => keep.add(u));
    const before = keep.size; r.relaxed.forEach(u => keep.add(u)); nRelax += keep.size - before;
    r.fams.forEach(x => fams.add(x)); r.anims.forEach(x => anims.add(x)); (r.kfJs || []).forEach(x => kfJs.add(x));
  }
  nUsed = keep.size - nRelax;
  let nSafe = 0;
  if (SAFE.length) m.list.forEach((s, u) => { if (!keep.has(u) && SAFE.some(re => re.test(s))) { keep.add(u); nSafe++; } });
  const fi = `${outDir}/model/${hash}.invalid.json`;
  const origInvalid = new Set(fs.existsSync(fi) ? JSON.parse(fs.readFileSync(fi, 'utf8')) : []);
  const r = buildReduced(css, m, keep, fams, anims, origInvalid, kfJs, { fontSrcRewrite: SAFELIST.font_src_rewrite || [] });
  fs.writeFileSync(`${outDir}/reduced/${hash}.css`, r.css);
  const row = {
    hash, pages: g.pages.length, paths: [...new Set(g.pages.map(p => p.path))].length, devs: [...new Set(g.pages.map(p => p.dev))].join(''),
    selUniq: m.list.length, keep: keep.size, keepDom: nUsed, keepRelax: nRelax, keepSafe: nSafe, origInvalid: origInvalid.size,
    scan, rawIn: Buffer.byteLength(css), rawOut: Buffer.byteLength(r.css), brIn: br(Buffer.from(css)), brOut: br(Buffer.from(r.css)), ...r.stats,
  };
  out.push(row);
  console.log(hash.slice(0, 8), `trang=${row.pages}`, `giữ ${row.keep}/${row.selUniq} (DOM ${nUsed}, nới ${nRelax}, safelist ${nSafe})`,
    `raw ${Math.round(row.rawIn / 1024)}→${Math.round(row.rawOut / 1024)} KB`, `br ${Math.round(row.brIn / 1024)}→${Math.round(row.brOut / 1024)} KB`,
    `font-face ${r.stats.ffOut}/${r.stats.ffIn}`, `keyframes ${r.stats.kfOut}/${r.stats.kfIn}`, JSON.stringify(scan));
}
fs.writeFileSync(`${outDir}/build.json`, JSON.stringify(out, null, 1));
