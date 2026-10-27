// Script bản ghi DNS chia vùng trên Bunny DNS (nhánh B, phương án O7b).
// Máy hỏi ở châu Á nhận A của origin. Vùng khác nhận pull zone Bunny.
// Thay {{ORIGIN_IP}} và {{PULL_ZONE_NAME}} lúc gửi lên Bunny bằng script, không lưu IP trong repo.
// Hai danh sách phải trùng scripts/geo_rule.py (test kiểm). Không gộp: trạm Bunny Los Angeles có mã "LA", trùng mã Lào.
const ASIA = ["VN", "SG", "HK", "TH", "MY", "ID", "PH", "KH", "LA", "MM", "BN", "TW", "JP", "KR", "CN", "IN"];
const ASIA_SZ = ["SG", "HK", "JP", "TW", "KR", "VN", "TH", "MY", "ID", "PH", "PP", "IN", "CEN", "CCU", "ND", "MU", "BD"];
const ORIGIN = "{{ORIGIN_IP}}";
const PZ = "{{PULL_ZONE_NAME}}";
const TTL = 30;

export default function handleQuery(query) {
  const r = query.request;
  const host = String(r.hostname || "").toLowerCase();
  const g = r.geoLocation || {};
  const cc = String(g.country || "");
  const sz = String(r.serverZone || "").toUpperCase();
  const toOrigin = ASIA.indexOf(cc) >= 0 || ASIA_SZ.indexOf(sz) >= 0 || !cc;
  // Bản ghi phụ "whoami" (TXT) để chẩn đoán: script thấy quốc gia, ASN, trạm DNS nào.
  if (host.indexOf("whoami") === 0) {
    return new TxtRecord("cc=" + cc + " asn=" + g.asn + " edns=" + (r.ednsIP ? "co" : "-") +
      " srv=" + sz + " qt=" + r.queryType + " route=" + (toOrigin ? "ORIGIN" : "CDN"), TTL);
  }
  if (toOrigin) {
    if (r.queryType === "A") return new ARecord(ORIGIN, TTL);
    return [];
  }
  return new PullZoneRecord(PZ);
}
