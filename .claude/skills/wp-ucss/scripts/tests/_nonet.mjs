// _nonet.mjs (wp-ucss): nạp trước test Node (NODE_OPTIONS=--import) để chặn mọi lượt gọi mạng. Test phải chạy offline.
import http from 'http'; import https from 'https'; import net from 'net';
const no = () => { throw new Error('test offline không được gọi mạng'); };
for (const m of [http, https]) { m.get = no; m.request = no; }
net.connect = no; net.createConnection = no; globalThis.fetch = no;
