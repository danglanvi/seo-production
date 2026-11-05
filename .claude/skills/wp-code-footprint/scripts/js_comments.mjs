import { createRequire } from 'node:module';
import { readFileSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const require = createRequire(import.meta.url);
const CACHE = join(homedir(), '.cache', 'wp-code-footprint', 'node_modules', 'acorn');
try {
  const acorn = require(process.env.ACORN_PATH || (existsSync(CACHE) ? CACHE : 'acorn'));
  const blocks = JSON.parse(readFileSync(0, 'utf8'));
  const results = blocks.map(({ text, type }) => {
    const comments = [];
    try {
      acorn.parse(text, {
        ecmaVersion: 'latest', sourceType: type === 'module' ? 'module' : 'script',
        locations: true,
        onComment(block, value, start, end, loc) {
          comments.push([block ? 'block' : 'line', text.slice(start, end), loc.line]);
        },
      });
      return { comments };
    } catch (e) {
      return { comments, error: e.message };
    }
  });
  process.stdout.write(JSON.stringify({ parser: `acorn@${acorn.version}`, results }));
} catch (e) {
  process.stdout.write(JSON.stringify({ error: `Acorn chưa sẵn sàng: ${e.code || e.message}. Đặt ACORN_PATH tới module đã cài.` }));
  process.exitCode = 2;
}
