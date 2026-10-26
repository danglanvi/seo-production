// Guard đo nhầm đích, dùng chung cho perf_probe.mjs, shot.mjs và lh_local.mjs. Không chạy trực tiếp.
// Đo nhầm trang 404, nhầm host (redirect sang production) hoặc tunnel staging đã tắt cho ra số vô nghĩa.
// Mã thoát 4 khi guard báo lỗi (hằng GUARD_EXIT).
import net from 'node:net';

export const GUARD_EXIT = 4;
export const MIN_LCP_MS = 100;

// Trả danh sách lỗi (mảng rỗng là đạt).
// status: HTTP status của document chính (null nếu không nhận được). expect: chuỗi phải có trong <title> (không phân biệt hoa thường).
// lcp: ms (bỏ qua nếu undefined). requestedHost, finalHost: host của URL yêu cầu và host của trang sau redirect.
export function verdict({requestedHost, finalHost, status, title, expect, lcp, minLcp = MIN_LCP_MS, allowRedirectHost = false}) {
  const errs = [];
  if (status == null) errs.push('không nhận được HTTP status (tunnel tắt, DNS sai hoặc trang không tải)');
  else if (status >= 400) errs.push(`HTTP ${status}`);
  if (finalHost && requestedHost && finalHost !== requestedHost && !allowRedirectHost) errs.push(`host thật ${finalHost} khác host yêu cầu ${requestedHost} (redirect?)`);
  if (expect && !String(title || '').toLowerCase().includes(String(expect).toLowerCase())) errs.push(`title "${title || ''}" không chứa "${expect}"`);
  if (lcp !== undefined && lcp !== null && lcp < minLcp) errs.push(`LCP ${lcp} ms dưới ${minLcp} ms (dấu hiệu đo nhầm trang lỗi)`);
  return errs;
}

export function line({host, status, title}) {
  return `GUARD host=${host} status=${status} title=${JSON.stringify(title || '')}`;
}

// Khi có --resolve host=ip: kiểm cổng của ip có mở không trước khi mở Chrome. Resolve rỗng thì bỏ qua.
export function checkTunnel(resolve, url, timeoutMs = 2000) {
  return new Promise((ok, fail) => {
    if (!resolve) return ok();
    const ip = String(resolve).split('=')[1];
    const u = new URL(url);
    const port = +(u.port || (u.protocol === 'https:' ? 443 : 80));
    if (!ip) return fail(new Error(`--resolve phải có dạng host=ip, nhận "${resolve}"`));
    const s = net.connect({host: ip, port});
    const t = setTimeout(() => { s.destroy(); fail(new Error(`cổng ${ip}:${port} không trả lời sau ${timeoutMs} ms (tunnel đã tắt?)`)); }, timeoutMs);
    s.on('connect', () => { clearTimeout(t); s.destroy(); ok(); });
    s.on('error', e => { clearTimeout(t); fail(new Error(`cổng ${ip}:${port} không mở: ${e.code || e.message} (tunnel đã tắt?)`)); });
  });
}

export function die(msgs) {
  console.error('GUARD LỖI: ' + [].concat(msgs).join('; ') + '. Số đo bỏ, kiểm URL, --expect, tunnel rồi chạy lại (hoặc --no-guard nếu cố ý).');
  process.exit(GUARD_EXIT);
}
