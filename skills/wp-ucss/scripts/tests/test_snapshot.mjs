// test_snapshot.mjs (wp-ucss): hồi quy byte build.mjs trên snapshot thật. Tuỳ chọn: run.sh chỉ chạy khi có UCSS_SNAP.
// UCSS_SNAP=<thư mục có pages/, model/, reduced/; reduced/ do bản build đã duyệt dựng trên chính pages/ đó>
// UCSS_SNAP_SITE=<site.json: cache_dir chứa sẵn mọi file gộp, safelist của site>. Offline: file gộp thiếu trong cache thì build.mjs dừng.
import fs from 'fs';
import os from 'os';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const SNAP = process.env.UCSS_SNAP, SITE = process.env.UCSS_SNAP_SITE;
if (!SNAP || !SITE) { console.log('SAI thiếu UCSS_SNAP hoặc UCSS_SNAP_SITE'); process.exit(1); }
const tmp = fs.mkdtempSync(os.tmpdir() + '/wp-ucss-snap-');
for (const d of ['pages', 'model']) fs.cpSync(`${SNAP}/${d}`, `${tmp}/${d}`, { recursive: true });
const r = spawnSync(process.execPath, [fileURLToPath(new URL('../build.mjs', import.meta.url)), '--site', SITE, tmp], { encoding: 'utf8' });
const want = fs.readdirSync(`${SNAP}/reduced`).filter(f => f.endsWith('.css'));
const bad = r.status === 0 ? want.filter(f => { const a = `${tmp}/reduced/${f}`; return !fs.existsSync(a) || !fs.readFileSync(a).equals(fs.readFileSync(`${SNAP}/reduced/${f}`)); }) : want;
if (r.status !== 0) console.log('SAI build.mjs dừng:', r.stderr.slice(-300));
else console.log(bad.length || !want.length ? 'SAI' : 'OK ', `reduced giống từng byte ${want.length - bad.length}/${want.length}`, bad.length ? 'khác: ' + bad.slice(0, 5).join(' ') : '');
fs.rmSync(tmp, { recursive: true, force: true });
process.exit(r.status === 0 && want.length && !bad.length ? 0 : 1);
