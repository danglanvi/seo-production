// test_build.mjs (wp-ucss): hồi quy byte cho build.mjs trên fixture nhỏ (CSS tự viết + 2 trang kết quả gen).
// expected/ sinh bằng build.mjs bản gốc trên cùng fixture. Chạy offline: CSS gộp nạp từ cache tạm, không gọi mạng.
// node test_build.mjs → in OK/SAI, mã 1 nếu khác.
import fs from 'fs';
import os from 'os';
import crypto from 'crypto';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const here = p => fileURLToPath(new URL(p, import.meta.url));
const FX = here('./fixtures/build/'), H = 'edc1344da9f5f7bd77e238b8e05c2a47';
const href = `https://example.com/wp-content/litespeed/css/${H}.css?ver=1a2b3`;
const tmp = fs.mkdtempSync(os.tmpdir() + '/wp-ucss-test-');
const site = JSON.parse(fs.readFileSync(here('../../templates/site.example.json'), 'utf8'));
Object.assign(site, { cache_dir: tmp + '/cache', safelist: FX + 'safelist.json' });
fs.writeFileSync(tmp + '/site.json', JSON.stringify(site));
fs.mkdirSync(tmp + '/cache');
const key = crypto.createHash('md5').update(href).digest('hex');
fs.copyFileSync(FX + 'combined.css', `${tmp}/cache/${key}`);
fs.writeFileSync(`${tmp}/cache/${key}.json`, JSON.stringify({ status: 200, type: 'text/css', url: href }));
fs.cpSync(FX + 'pages', tmp + '/out/pages', { recursive: true });
fs.cpSync(FX + 'model', tmp + '/out/model', { recursive: true });

const r = spawnSync(process.execPath, [here('../build.mjs'), '--site', tmp + '/site.json', tmp + '/out', FX + 'keep.txt'], { encoding: 'utf8' });
let bad = 0;
const ok = (name, cond, more = '') => { if (!cond) bad++; console.log(cond ? 'OK ' : 'SAI', name, cond ? '' : more); };
ok('build.mjs chạy', r.status === 0, r.stderr.slice(-400));
const same = f => fs.existsSync(f[0]) && Buffer.compare(fs.readFileSync(f[0]), fs.readFileSync(f[1])) === 0;
ok(`reduced/${H.slice(0, 8)}.css giống bản gốc từng byte`, same([`${tmp}/out/reduced/${H}.css`, FX + `expected/${H}.css`]));
ok('build.json giống bản gốc', same([`${tmp}/out/build.json`, FX + 'expected/build.json']));
fs.rmSync(tmp, { recursive: true, force: true });
process.exit(bad ? 1 : 0);
