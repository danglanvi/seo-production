# Mô phỏng luật chia vùng của templates/geo-dns-script.js để test offline. Hai danh sách phải trùng với template (test kiểm).
# ASIA: mã quốc gia GeoIP của máy hỏi. ASIA_SZ: mã trạm Bunny DNS nhận câu hỏi (serverZone = RegionCode của API /region).
# Không gộp hai danh sách: trạm Bunny ở Los Angeles có mã "LA", trùng mã quốc gia Lào.
ASIA = ["VN", "SG", "HK", "TH", "MY", "ID", "PH", "KH", "LA", "MM", "BN", "TW", "JP", "KR", "CN", "IN"]
ASIA_SZ = ["SG", "HK", "JP", "TW", "KR", "VN", "TH", "MY", "ID", "PH", "PP", "IN", "CEN", "CCU", "ND", "MU", "BD"]
# Mã trạm Bunny ở Mỹ (26/10/2026). Dùng trong test để bắt va chạm mã.
US_SZ = ["ASB", "BO", "CLT", "DEN", "GA", "HI", "HOU", "IL", "KC", "LA", "MI", "MSP", "NY", "OG", "PB", "PHX", "SIL", "TX", "WA"]


def route(country, server_zone, query_type="A"):
    cc = (country or "").upper()
    sz = (server_zone or "").upper()
    if cc in ASIA or sz in ASIA_SZ or not cc:
        return "ORIGIN" if query_type == "A" else "EMPTY"
    return "CDN"
