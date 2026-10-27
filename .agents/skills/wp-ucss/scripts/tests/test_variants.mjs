// test_variants.mjs (wp-ucss): biến thể m, d, g, p, q trong site.example.json và isDesk khớp bản gốc.
// p = d nhưng Accept */*, q = m nhưng Accept */*. isDesk: chỉ d, p là desktop (không tap, có hover).
import fs from 'fs';
import { isDesk } from '../lib-ucss.mjs';

const S = JSON.parse(fs.readFileSync(new URL('../../templates/site.example.json', import.meta.url), 'utf8'));
let bad = 0;
const ok = (name, cond) => { if (!cond) bad++; console.log(cond ? 'OK ' : 'SAI', name); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
for (const k of ['ua', 'accept', 'viewport']) ok(`${k} có đủ m, d, g, p, q`, ['m', 'd', 'g', 'p', 'q'].every(v => S[k][v]));
ok('p = d (UA, viewport)', same(S.ua.p, S.ua.d) && same(S.viewport.p, S.viewport.d));
ok('q = m (UA, viewport)', same(S.ua.q, S.ua.m) && same(S.viewport.q, S.viewport.m));
ok('Accept của g, p, q là */*', ['g', 'p', 'q'].every(v => S.accept[v] === '*/*'));
ok('isDesk: d, p desktop; m, g, q mobile', isDesk('d') && isDesk('p') && !isDesk('m') && !isDesk('g') && !isDesk('q'));
process.exit(bad ? 1 : 0);
