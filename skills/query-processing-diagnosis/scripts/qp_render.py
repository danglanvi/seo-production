#!/usr/bin/env python3
"""Dựng deck "Query Processing đẩy keyword cam kết" từ file JSON của dự án (schema qp-project/1, xem references/schema-qp-project.md).

  python3 qp_render.py check <du-an.json> [...]                       # kiểm schema, giới hạn độ dài chữ, regex, chữ cấm; phải in OK
  python3 qp_render.py project <du-an.json> <out.html> [--web] [--back <tong-quan.html>]
                                                                      # deck một dự án (15–17 slide)
  python3 qp_render.py overview <out.html> <a.json> <b.json> ... [--web] [--link "{slug}.html"]
                                                                      # deck tổng quan nhiều dự án, bấm tên dự án mở deck riêng
  python3 qp_render.py all <out.html> <a.json> <b.json> ... [--web]   # deck gộp: tổng quan + mọi dự án

--web: bỏ phần nội bộ (khối kpi: mốc, khoảng cách, rủi ro; thẻ plan.cards có internal=true). Dùng khi deck đi ra ngoài nhóm dự án.
Thứ tự dự án trong overview/all: trường `order`, rồi thứ tự file trên dòng lệnh.
CSS + engine slide: assets/base.css, assets/base.js (lấy từ deck training Query Processing của GTV).
"""
import html, json, re, sys
from pathlib import Path

D = Path(__file__).parent
BASE_CSS = (D / "assets" / "base.css").read_text()
BASE_JS = (D / "assets" / "base.js").read_text()
e = html.escape
STAGES = [("B2", "Segment"), ("B3", "Augment"), ("B4", "Canonical"), ("B5", "Context"), ("B6", "Câu hỏi"), ("B7", "Retrieve"), ("B8", "Passage")]
FOOT = '<footer class="foot"><span>Query Processing · đẩy keyword cam kết</span><span>Tài liệu nội bộ GTV · không gửi khách</span></footer>'
LINK = "{slug}.html"  # mẫu link từ overview sang deck dự án; đổi bằng --link


def fname(slug):
    return LINK.format(slug=slug)


def month_of(P):
    """Tháng/năm của lần đo (measure.date dạng dd/mm/yyyy, yyyy-mm-dd hoặc chuỗi tự do)."""
    d = str((P.get("measure") or {}).get("date") or "")
    m = re.search(r"(\d{4})-(\d{2})-\d{2}", d) or re.search(r"\d{1,2}/(\d{1,2})/(\d{4})", d)
    if not m:
        return ""
    return f"{m.group(2)}/{m.group(1)}" if "-" in m.group(0) else f"{int(m.group(1)):02d}/{m.group(2)}"


# ---------- chữ ----------
ALLOWED = re.compile(r"</?(b|g|i|r)>|<br>")


def t(s):
    """Chữ tự do: cho phép <b>, <i>, <br>, <g> (chữ gradient), <r> (chữ đỏ: cần kiểm tay). Ký tự & < > khác được escape."""
    if s is None:
        return ""
    s = str(s)
    out, pos = [], 0
    for m in ALLOWED.finditer(s):
        out.append(e(s[pos:m.start()], quote=False))
        tag = m.group(0)
        out.append({"<g>": '<span class="grad-text">', "</g>": "</span>", "<r>": '<span class="kt">', "</r>": "</span>"}.get(tag, tag))
        pos = m.end()
    out.append(e(s[pos:], quote=False))
    return "".join(out)


def plain(s):
    return re.sub(r"<[^>]+>", "", str(s or ""))


def tipa(s):
    """Thuộc tính data-tip: chữ đầy đủ hiện khi rê chuột (cùng markup với chữ tự do)."""
    return f' data-tip="{e(t(s))}"' if s else ""


def ti(s):
    return '<i class="ti">i</i>' if s else ""


# ---------- chú thích khi rê chuột ----------
GUIDE = {
    "idea": "<b>Slide trả lời:</b> vì sao đẩy keyword theo họ, không đẩy từng keyword.<br><b>Đọc:</b> từ trái sang phải là số keyword cam kết, số template (họ keyword), rồi URL đang giữ nhiều keyword nhất. Hai thẻ dưới nói cơ chế và hệ quả: đẩy đúng một trang có thể kéo cả họ lên, và một lỗi trên trang đó cũng làm cả họ rơi.",
    "steps": "Quy trình chung cho mọi dự án. Mỗi bước có một đầu ra. Các slide sau của dự án đi theo đúng thứ tự 6 bước này.",
    "templates": "<b>Slide trả lời:</b> bộ keyword cam kết chia thành những họ nào, và họ nào đã có hạng tốt.<br><b>Đọc:</b> mỗi dòng là một template. Độ dài thanh là số keyword. Màu là nhóm hạng hiện tại: xanh đậm Top 3, xanh Top 4–10, tím 11–20, xám 21 tới độ sâu đo, hồng là ngoài độ sâu đo. Cột giữa là số keyword Top 10 ở mốc so sánh (ngày ghi ở dòng nguồn) và hiện tại; deck không có mốc so sánh thì chỉ ghi số hiện tại. Rê chuột lên nhãn trạng thái để xem nghĩa, lên dòng để xem giải thích đầy đủ.",
    "grid": "<b>Slide trả lời:</b> trong một template, biến thể nào đã thắng, biến thể nào còn kẹt.<br><b>Đọc:</b> chọn tab template. Mỗi ô là một keyword: số ở góc là hạng hiện tại, dòng nhỏ là hạng ở mốc so sánh. Ô viền hồng: site có trang nhưng keyword chưa vào độ sâu đo. Thẻ trắng bên phải là nhận định, thẻ màu là việc cần làm. Nút “Mô phỏng lan trust” chỉ minh họa cách Koray mô tả, không phải dữ liệu.",
    "canonical": "<b>Slide trả lời:</b> mỗi họ query nên do URL nào nhận.<br><b>Đọc:</b> cột “Google đang chọn” là URL và hạng thật trong công cụ đo hạng. Cột “Vấn đề” nói vì sao chưa ổn. Cột “Quyết định” là URL giữ vai đại diện và việc kèm theo. Rê chuột lên dòng để xem lý do đầy đủ. Luật bên phải áp cho mọi dòng.",
    "serp": "<b>Slide trả lời:</b> với query đại diện của từng intent, Google đang muốn loại trang nào, và site có dùng đúng loại trang không.<br><b>Đọc:</b> mỗi thẻ là top kết quả của một query. Nhãn màu là loại trang. Dòng xanh là site. Cuối thẻ là intent, kết luận về loại trang và việc rút ra.<br><b>Vì sao cần:</b> nếu Top 10 gần như toàn trang danh mục mà site đẩy trang sản phẩm, sửa chữ trên trang sản phẩm khó thắng. Loại trang quyết định URL nào được đẩy ở slide Canonical.",
    "matrix": "<b>Slide trả lời:</b> mỗi cụm keyword đang hỏng ở trạm nào trong chuỗi Google xử lý query, để sửa đúng chỗ.<br><b>Đọc:</b> mỗi dòng là một cụm. Chấm đặc là trạm hỏng chính, vòng rỗng là trạm phụ. Rê chuột lên tên trạm để xem trạm đó làm gì; rê lên chấm để xem vì sao cụm hỏng ở đó. Bấm vào dòng để xem số liệu, chẩn đoán và việc làm.<br><b>Vì sao cần:</b> cùng là “chưa lên Top”, nhưng lỗi Retrieve phải sửa kỹ thuật, lỗi Canonical phải chọn lại URL, chỉ lỗi Augment mới cần thêm nội dung. Trạm B1 (tách token) không có đòn bẩy SEO nên không có cột.",
    "aug": "<b>Slide trả lời:</b> trên trang đang rank, thêm khối nào để phủ các biến thể chưa được phủ.<br><b>Đọc:</b> khung trái là bố cục trang, đánh số theo khối. Bảng phải cho biết mỗi khối nhắm keyword nào và hạng hiện tại. Rê chuột lên khối hoặc dòng để thấy cặp tương ứng và giải thích đầy đủ.",
    "levers": "<b>Slide trả lời:</b> ngoài chữ và heading, cần làm gì với internal link, hình ảnh, chức năng và schema.<br><b>Đọc:</b> mỗi cột là một nhóm việc. Nhãn đầu dòng là loại tác động: <b>Ranking</b> ảnh hưởng hạng; <b>Kỹ thuật</b> giúp Google đọc đúng trang; <b>UX</b> giúp người mua, không đẩy hạng trực tiếp. Dòng dưới cùng là việc không nên làm.",
    "pairs": "<b>Slide trả lời:</b> query dạng “X và Y” cần trang đặt hai entity song song.",
    "retrieve": "<b>Slide trả lời:</b> trang nào có trên site mà keyword vẫn không có hạng, và đã kiểm những gì.<br><b>Đọc:</b> mỗi dòng là một trang cùng keyword cam kết của nó. Thẻ phải là điều đã kiểm bằng HTTP và giả thuyết cần GSC xác nhận. Lỗi Retrieve phải sửa trước mọi việc nội dung.",
    "qa": "Các câu team hay hỏi khi triển khai, trả lời bằng dữ liệu của dự án. Mỗi thẻ: câu trả lời ngắn, bằng chứng, việc làm.",
    "priority": "<b>Slide trả lời:</b> làm topic nào trước, vì sao.<br><b>Đọc:</b> mỗi dòng là một topic (gói việc T1, T2…). Topic ghi “mới” là đề xuất chưa kiểm chéo. Cột “Keyword” là số keyword cam kết topic đẩy, không trùng giữa các topic. P0 làm ngay, P1 làm trong đợt này, P2 làm sau khi xong P1.<br><b>Nguyên tắc xếp:</b> lỗi chặn hoặc làm rơi nhiều keyword cùng lúc làm trước; việc nhỏ cho keyword đã ở #6–10 làm tiếp; việc nội dung lớn trên trang đang giữ Top 3 làm sau khi chụp baseline.",
    "measure": "<b>Slide trả lời:</b> đo thế nào để biết một topic có tác dụng.<br><b>Vì sao đo theo template:</b> Google xử lý cả họ query, nên hạng lên xuống theo họ. Đọc từng keyword dễ nhầm dao động thành kết quả.<br><b>Đọc:</b> bảng trái là regex dán vào GSC để lọc cả họ. Các ngày bên phải cho biết khi nào đọc số. Luật đọc số giải thích cách bỏ lần chạy lỗi.",
    "plan": "<b>Slide trả lời:</b> ai làm gì, khi nào, thế nào là xong.<br><b>Đọc:</b> mỗi dòng là một việc. Cột “Xong khi” là tiêu chí kiểm. Rê chuột lên dòng để xem vì sao làm việc đó. Bấm vào dòng để đánh dấu đã xong (chỉ giữ trong lần xem này).",
    "overview": "Bảng hiện trạng các dự án. Bấm tên dự án để mở deck riêng.",
    "patterns": "Các pattern lặp lại ở nhiều dự án. Mỗi pattern gắn với một trạm trong chuỗi xử lý query.",
}
STATUS_TIP = {
    "ok": "<b>Đã mở:</b> template đã có keyword Top 3. Google đã chấp nhận site cho họ này. Việc tiếp theo là phủ các biến thể chưa có hạng tốt trên cùng URL.",
    "up": "<b>Đang lan:</b> số keyword Top 10 của họ tăng rõ so với mốc so sánh (khoảng 4 tuần trước). Giữ nguyên trang, chỉ chỉnh nhỏ.",
    "mid": "<b>Kẹt:</b> có keyword trong Top 50 nhưng chưa vào Top 10. Xem slide Pipeline để biết trạm hỏng.",
    "no": "<b>Chưa có hạng:</b> phần lớn keyword ngoài độ sâu đo. Thường do Google chưa lấy trang (Retrieve) hoặc site chưa có trang đúng loại.",
}
TYPE_TIP = {
    "cat": "Trang danh mục: liệt kê nhiều sản phẩm hoặc dịch vụ.", "home": "Trang chủ.", "list": "Bài top list hoặc bài tổng hợp.",
    "guide": "Bài hướng dẫn.", "aio": "AI Overview.", "vid": "Video.", "prod": "Trang sản phẩm hoặc khối Shopping.",
    "local": "Kết quả local (Maps, Google Business Profile).", "forum": "Diễn đàn.", "news": "Tin tức.", "other": "Loại khác.",
}
STAGE_TIP = {
    "B2": "<b>B2 Segment:</b> Google cắt query thành các mảnh có nghĩa theo log tìm kiếm (US9690847B2). Cụm hỏng ở đây khi title, heading không dùng đúng mảnh người dùng gõ, ví dụ thiếu tên sản phẩm hoặc thêm chữ chen giữa. Đòn bẩy: đặt đúng mảnh vào title, H1, heading.",
    "B3": "<b>B3 Augment:</b> Google giữ mảnh chính và thay mảnh phụ bằng biến thể gần nghĩa để mở rộng query (US8577913B1). Cụm hỏng ở đây khi trang chỉ phủ vài biến thể. Đòn bẩy: phủ các biến thể anh em trên cùng URL bằng bảng, H3, card.",
    "B4": "<b>B4 Canonical:</b> Google gom các cách gõ thành cụm, tâm cụm là query đại diện, rồi chọn một URL cho cụm (US8645407B2). Cụm hỏng ở đây khi một họ query chia cho nhiều URL, hoặc Google chọn URL khác URL site muốn. Đòn bẩy: chốt một URL, một anchor.",
    "B5": "<b>B5 Context:</b> Google gắn ngữ cảnh địa điểm, thời gian, người dùng vào query (US10146829B2). Cụm hỏng ở đây khi query địa phương mà trang thiếu tín hiệu địa điểm.",
    "B6": "<b>B6 Câu hỏi:</b> Google đổi keyword thành câu hỏi ngầm, gọi là K2Q (US9898554B2). Cụm hỏng ở đây khi heading không phải câu người dùng hỏi, hoặc câu trả lời nằm xa heading.",
    "B7": "<b>B7 Retrieve:</b> Google lấy trang vào danh sách ứng viên rồi lọc dần trước khi chấm hạng. Cụm hỏng ở đây khi trang noindex, canonical sai, chưa được crawl lại hoặc quá giống trang khác: keyword không có hạng dù trang tồn tại. Sửa trạm này trước mọi việc nội dung.",
    "B8": "<b>B8 Passage:</b> Google chọn đoạn trả lời dựa trên heading và đoạn ngay dưới heading (US9959315B1). Cụm hỏng ở đây khi đoạn trả lời dài, lan man hoặc nằm cuối bài.",
}
KIND_CLS = {"Ranking": "rank", "Kỹ thuật": "tech", "UX": "ux", "Shopping": "tech"}
GLOSS = [  # thuật ngữ: bọc lần xuất hiện đầu tiên trên mỗi slide (chạy phía trình duyệt)
    ("query đại diện", "Query Google chọn làm tâm của một cụm cách gõ gần nghĩa (US8645407B2). Google xử lý cả cụm theo query này, nên trang khớp query đại diện có thể nhận hạng cho cả họ."),
    ("URL đại diện", "URL site chọn để Google trả cho cả một họ query. Mỗi họ chỉ nên có một URL đại diện. Hai URL cùng nhắm một họ thì Google phải chọn, và hay lật qua lại."),
    ("query template|template", "Họ keyword cùng cấu trúc, chỉ khác một ô biến. Ví dụ “[sản phẩm] [size]”. Theo Koray, khi site thắng vài biến thể, Google thử site cho cả họ; Google chưa công bố cơ chế này."),
    ("biến thể", "Một cách điền vào ô biến của template. Ví dụ “10 inch” là một biến thể của “rattan pendant light [size]”."),
    ("retrieve", "Bước Google lấy trang vào danh sách ứng viên trước khi chấm hạng (trạm B7). Trang không được retrieve thì không có hạng, dù nội dung tốt."),
    ("noindex", "Thẻ meta robots báo Google không đưa trang vào chỉ mục. Trang noindex không có hạng; lâu dài Google cũng ít đi theo link trên trang đó."),
    ("tự canonical", "Trang khai thẻ canonical trỏ về chính nó: báo Google đây là bản chính."),
    ("median", "Số ở giữa khi xếp các lần đo theo thứ tự. Ví dụ hạng 5, 9, 30 có median 9. Median bỏ qua một lần đo lệch, nên ổn định hơn đọc một lần chạy."),
    ("lần chạy đủ|lần chạy thiếu", "Lần chạy đủ: SpySERP quét được gần hết bộ keyword. Lần chạy thiếu: quét được rất ít keyword, nên bị bỏ khi tính số."),
    ("PDP", "Product Detail Page: trang chi tiết của một sản phẩm."),
    ("anchor", "Chữ hiển thị của link. Google dùng anchor để hiểu trang đích nói về gì. Một anchor nên trỏ về một URL."),
    ("SERP", "Trang kết quả tìm kiếm của Google."),
    ("DR\\d+", "Domain Rating của Ahrefs (0–100): đo sức mạnh backlink của cả domain."),
    ("ngoài \\d+", "Keyword không xuất hiện trong số kết quả SpySERP quét. Không có nghĩa là hạng ngay sau độ sâu đó."),
    ("augmentation map|augment", "Google mở rộng query thành các biến thể gần nghĩa (trạm B3). Trang phủ được các biến thể này trên cùng URL thì được chấm cho cả họ."),
    ("component", "Một khối trên trang (bảng, H3, nhóm card sản phẩm, đoạn trả lời) phục vụ một nhóm query."),
    ("K2Q", "Keyword-to-Question: Google đổi keyword thành câu hỏi ngầm để tìm đoạn trả lời (trạm B6)."),
    ("passage", "Đoạn văn Google trích để trả lời (trạm B8). Đoạn trả lời nên nằm ngay dưới heading và tự đủ nghĩa."),
    ("lan trust", "Cách Koray mô tả: Google thử site ở một biến thể; nếu người dùng hài lòng, Google thử tiếp các biến thể cùng cấu trúc. Google chưa công bố cơ chế này."),
    ("JSON-LD", "Cách viết structured data (schema.org) trong thẻ script. Google đọc khối này để hiểu loại trang và sản phẩm. Một lỗi cú pháp làm Google bỏ cả khối."),
    ("Rich Results Test", "Công cụ của Google kiểm structured data của một URL: search.google.com/test/rich-results."),
    ("URL Inspection", "Công cụ trong Google Search Console: cho biết URL đã index chưa, Google chọn canonical nào, lần crawl gần nhất."),
    ("GSC", "Google Search Console."),
    ("regex", "Biểu thức chính quy: mẫu chữ dùng để lọc nhiều query cùng lúc trong GSC."),
    ("click depth", "Số lần bấm từ trang chủ tới trang. Trang càng sâu thì Googlebot càng ít ghé."),
    ("baseline", "Số đo trước khi sửa, dùng để so sánh sau khi sửa."),
]


def guide(key, P=None):
    g = GUIDE.get(key, "")
    extra = ((P or {}).get("guides") or {}).get(key)
    return g + (f"<br><br><b>Ở {P['name']}:</b> {extra}" if extra else "")


# ---------- hạng ----------
class R:
    def __init__(self, P):
        m = P["measure"]
        self.has = m.get("has_rank", True)
        self.depth = m.get("depth") or 100
        self.eng = m.get("engine", "")
        cd = m.get("compare_date") or ""
        self.cmp = bool(cd)
        self.cl = cd[:5] if cd else ""  # nhãn mốc so sánh, ví dụ "14/09"

    def cls(self, p):
        return "rout" if not p else "r3" if p <= 3 else "r10" if p <= 10 else "r20" if p <= 20 else "r50"

    def txt(self, p):
        if not self.has:
            return "chưa đo"
        return f"#{p}" if p else f"ngoài {self.depth}"

    def chip(self, k):
        p = k.get("now")
        return f'<span class="rk {self.cls(p) if self.has else "rout"}">{self.txt(p)}</span>'


def slide(title, sec, body, cls="", src="", attrs="", guide="", qp=""):
    src = f'<p class="src">{t(src)}</p>' if src else ""
    how = f'<span class="howto"{tipa(guide)}>Cách đọc slide</span>' if guide else ""
    if qp and "data-qp" not in attrs:
        attrs += f' data-qp="{qp}"'
    return f'''<section class="slide {cls}" data-title="{e(plain(title))}"{attrs}>
  <div class="bg-grid"></div>
  <header class="chrome"><span class="sec">{sec}</span><span class="chr-r">{how}<span class="pgn"></span></span></header>
  <div class="wrap">{body}{src}</div>
  {FOOT}
</section>'''


# ---------- slide dùng chung ----------
def s_cover(P, n_proj, overview=False, back=None, dates=""):
    c = P["cover"]
    toks = "".join(f'<span class="tk {e(x.get("k", "known"))}">{e(x["t"])}<small>{e(x["r"])}</small></span>' for x in c["tokens"])
    qlen = len(c["query"])
    mon = month_of(P)
    mon = f" · {mon}" if mon else ""
    if overview:
        sub = f"Áp phương pháp Query Processing lên bộ keyword cam kết của {n_proj} dự án GTV. Mỗi dự án có deck riêng."
        pills = f'<span class="pill blue">{n_proj} dự án</span><span class="pill">Ví dụ: {e(P["name"])}</span>' + (f'<span class="pill">{e(dates)}</span>' if dates else "")
        title = 'Query Processing<br><span class="grad-text">đẩy keyword cam kết</span>'
        eyebrow = f"Tài liệu nội bộ{mon} · không gửi khách"
    else:
        sub = f"Áp phương pháp Query Processing lên bộ keyword cam kết của {e(P['name'])}."
        m = P["measure"]
        meas = f'{e(m.get("tool", ""))} {e(m.get("date", ""))}' if m.get("has_rank", True) else "Chưa có số đo hạng"
        pills = f'<span class="pill blue">{e(P["name"])}</span><span class="pill">Lead {e(P.get("lead") or "chưa gán")}</span><span class="pill">{meas}</span>'
        if back:
            pills += f'<a class="pill back" href="{e(back)}">← Tổng quan {n_proj} dự án</a>'
        title = f'{e(P["name"])}<br><span class="grad-text">đẩy keyword cam kết</span>'
        eyebrow = f"Query Processing ứng dụng{mon} · không gửi khách"
    return f'''<section class="slide s-cover" data-title="Cover">
  <div class="bg-grid"></div><div class="glow g1"></div><div class="glow g2"></div>
  <header class="chrome"><span class="sec">GTV SEO · <b>Query Processing ứng dụng</b></span><span class="pgn"></span></header>
  <div class="cover-l">
    <div class="eyebrow reveal d1">{eyebrow}</div>
    <h1 class="sm reveal d2">{title}</h1>
    <p class="cover-sub reveal d3">{sub}</p>
    <div class="cover-meta reveal d4">{pills}</div>
    <p class="kt-legend reveal d4"><span class="kt">Chữ đỏ</span> là chỗ cần kiểm tay (GSC, SERP hoặc trang thật) trước khi làm.</p>
  </div>
  <div class="cover-r">
    <div class="qbox reveal d2">
      <svg viewBox="0 0 24 24" fill="none" stroke="#0693E3" stroke-width="2.4" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>
      <span class="typed tq" style="--n:{qlen};--w:{qlen + .5}ch">{e(c["query"])}</span>
    </div>
    <div class="tokens">{toks}</div>
    <div class="arrow-down"></div>
    <div class="rep-card">
      <div class="mono">Google hiểu thành</div>
      <div class="rep">{e(c["rep"])}</div>
      <div class="rep-sub">{t(c["rep_sub"])}</div>
    </div>
  </div>
  {FOOT}
</section>'''


def s_idea(P):
    d = P["idea"]
    return slide("Ý tưởng", "01 · <b>Cách nghĩ</b>", f'''
    <h2 class="h2 reveal d1">Hợp đồng đếm keyword. Google xử lý <span class="grad-text">query đại diện</span>.</h2>
    <div class="row grow">
      <div class="flow3 reveal d2">
        <div class="stat"><div class="v">{e(str(d["n_kw"]))}</div><div class="t">{t(d.get("n_kw_text") or f"keyword cam kết của {P['name']}. Hợp đồng đếm từng keyword vào Top 3/5/10.")}</div></div>
        <div class="farrow">→</div>
        <div class="stat"><div class="v">{e(str(d["n_tpl"]))}</div><div class="t">query template. Mỗi template là một họ biến thể có cùng cấu trúc.</div></div>
        <div class="farrow">→</div>
        <div class="stat hl"><div class="v">1 URL</div><div class="t">{t(d.get("hub_text") or f"{d['hub_url']} đang giữ {d['hub_n']} keyword cam kết, {d['hub_top10']} keyword trong Top 10.")}</div></div>
      </div>
    </div>
    <div class="row reveal d3" style="gap:28px;margin-bottom:6px">
      <div class="card f1"><span class="lbl">Cơ chế</span><p>{t(d["mechanism"])}</p></div>
      <div class="card f1"><span class="lbl">Hệ quả cho KPI</span><p>{t(d["effect"])}</p></div>
    </div>''', src=d.get("src", ""), guide=guide("idea", P), qp=P["slug"])


STEPS = [
    ("Gom theo template", "Chia bộ keyword cam kết thành họ query cùng cấu trúc, ví dụ “đèn học [thuộc tính]”.", "Đầu ra: bảng template × biến, có hạng"),
    ("Đọc lưới hạng", "Xem template nào đã mở trust (có biến thể Top 3), template nào chưa có tài liệu được retrieve.", "Đầu ra: nhóm đẩy tiếp · sửa trước · chưa làm"),
    ("Kiểm SERP", "Đọc loại trang top 10 và AI Overview. Kiểm SERP overlap. Chốt 1 URL cho mỗi query đại diện.", "Đầu ra: bảng query đại diện → URL"),
    ("Dò pipeline", "Tìm trạm đang hỏng ở từng cụm: segment, augment, canonical, context, câu hỏi, retrieve, passage.", "Đầu ra: ma trận cụm × trạm"),
    ("Sửa đúng trạm", "Sửa trên trang đang rank: augmentation map, K2Q, segment, gom URL. Trước kỳ đo chỉ thêm, không rút.", "Đầu ra: topic gắn keyword cam kết"),
    ("Đo theo template", "Regex GSC và nhóm SpySERP theo template. Đọc median các lần chạy đầy đủ, chờ 14 ngày.", "Đầu ra: mở rộng · dừng · hoàn lại"),
]


def s_steps():
    return slide("6 bước", "01 · <b>Cách nghĩ</b>", '''
    <h2 class="h2 reveal d1">Quy trình <span class="grad-text">6 bước</span> cho bộ keyword cam kết</h2>
    <div class="row grow"><div class="steps6" style="width:100%">''' + "".join(
        f'<div class="step reveal d{i + 1}"><div class="hd"><span class="num">{i + 1}</span><h4>{a}</h4></div><p>{b}</p><div class="out">{c}</div></div>' for i, (a, b, c) in enumerate(STEPS)) +
        '</div></div>', src="Site mới bắt đầu từ entity; dự án đang chạy bắt đầu từ bộ keyword cam kết đã có hạng. Bước 3 kiểm SERP overlap trước khi gộp hay tách URL. Bước 4 theo chuỗi 8 trạm xử lý query (B1–B8).", guide=guide("steps"))


# ---------- slide tổng quan ----------
def s_overview_idea(PS):
    n_kw = sum(int(re.sub(r"\D", "", str(P["idea"]["n_kw"])) or 0) for P in PS)
    n_tpl = sum(int(P["idea"]["n_tpl"]) for P in PS)
    ex = PS[0]
    return slide("Ý tưởng", "01 · <b>Cách nghĩ</b>", f'''
    <h2 class="h2 reveal d1">Hợp đồng đếm keyword. Google xử lý <span class="grad-text">query đại diện</span>.</h2>
    <div class="row grow">
      <div class="flow3 reveal d2">
        <div class="stat"><div class="v">{n_kw:,}</div><div class="t">keyword cam kết hoặc keyword ưu tiên của {len(PS)} dự án. Hợp đồng đếm từng keyword vào Top 3/5/10.</div></div>
        <div class="farrow">→</div>
        <div class="stat"><div class="v">{n_tpl}</div><div class="t">query template. Mỗi template là một họ biến thể có cùng cấu trúc.</div></div>
        <div class="farrow">→</div>
        <div class="stat hl"><div class="v">1 URL</div><div class="t">cho mỗi query đại diện. Ví dụ {e(ex["name"])}: {e(ex["idea"]["hub_url"])} giữ {ex["idea"]["hub_n"]} keyword cam kết.</div></div>
      </div>
    </div>
    <div class="row reveal d3" style="gap:28px;margin-bottom:6px">
      <div class="card f1"><span class="lbl">Cơ chế</span><p>Google gom các cách gõ thành cụm. Tâm cụm là query đại diện (US8645407B2). Giả thuyết: trang khớp query đại diện nhận relevance cho cả họ.</p></div>
      <div class="card f1"><span class="lbl">Hệ quả cho KPI</span><p>Đẩy đúng một query đại diện có thể kéo nhiều keyword cam kết cùng lúc. Một lỗi ở một trạm cũng có thể làm rơi cả họ keyword.</p></div>
    </div>''', src="Tổng số keyword cộng theo bộ đang dùng trong deck của từng dự án (xem slide bộ keyword của từng dự án).", guide=guide("idea"))


def meas_range(PS):
    """Chuỗi nguồn đo cho overview: công cụ + các ngày đo khác nhau của các dự án."""
    tools = sorted({(P.get("measure") or {}).get("tool") or "" for P in PS if (P.get("measure") or {}).get("has_rank", True)} - {""})
    dates = []
    for P in PS:
        d = (P.get("measure") or {}).get("date")
        if d and (P.get("measure") or {}).get("has_rank", True) and d not in dates:
            dates.append(d)
    if not dates:
        return ""
    return f"{', '.join(tools) or 'Đo hạng'} {dates[0]}" + (f"–{dates[-1]}" if len(dates) > 1 else "")


def s_overview_table(PS, web, link=True):
    rows = ""
    for P in PS:
        s, k = P["status_row"], P.get("kpi") or {}
        name = f'<a href="{fname(P["slug"])}">{e(P["name"])}</a>' if link else e(P["name"])
        hl = P.get("headline", {})
        cells = f'<td><b>{name}</b><small>{e(P.get("lead") or "chưa gán Lead")}</small></td><td>{t(s["set"])}</td><td class="m">{t(s["now"])}</td>'
        if not web:
            risk = k.get("risk", "")
            cells += f'<td class="m">{t(k.get("target", ""))}</td><td class="m">{t(k.get("gap", ""))}</td><td><span class="pri {"stop" if risk == "Cao" else "mid"}">{e(risk)}</span></td>'
        cells += f'<td>{t(hl.get("template", ""))}<small>{t(hl.get("fact", ""))}</small></td>'
        rows += f"<tr>{cells}</tr>"
    if web:
        head = '<th style="width:16%">Dự án</th><th style="width:20%">Bộ keyword</th><th style="width:20%">Hiện tại</th><th>Template đáng đẩy nhất</th>'
        title = f'{len(PS)} dự án: hiện trạng và <span class="grad-text">template đáng đẩy</span>'
    else:
        head = '<th style="width:12%">Dự án</th><th style="width:14%">Bộ cam kết</th><th style="width:14%">Hiện tại</th><th style="width:15%">Mốc gần nhất</th><th style="width:12%">Khoảng cách</th><th style="width:6%">Rủi ro</th><th>Template đáng đẩy nhất</th>'
        title = f'{len(PS)} dự án: bộ cam kết so với <span class="grad-text">mốc nghiệm thu</span>'
    return slide(f"{len(PS)} dự án", "01 · <b>Bức tranh</b>", f'''
    <h2 class="h2 reveal d1">{title}</h2>
    <div class="row grow"><table class="tbl tp10{' dense' if len(PS) > 10 else ''} reveal d2"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>''',
                 src="Số Top 3/5/10 khi không ghi khác. Hiện tại: " + (meas_range(PS) or "xem deck từng dự án") + ". Bấm tên dự án để mở deck riêng.", guide=guide("overview"))


# 7 pattern rút từ đợt chẩn đoán 10 dự án GTV (10/2026, đã kiểm chéo). Cột 3 = khi nào dùng.
PATTERNS = [
    ("B4", "Chốt một URL cho mỗi canonical query", "Hai hoặc ba URL cùng nhận một họ query; Google lật URL giữa các lần đo", "Giữ URL Google đang chọn nếu đã Top 10. Khác nhóm người dùng thì không ép gộp."),
    ("B3", "Phủ biến thể template trên trang đã thắng một biến thể", "Trang đã Top 3–5 cho một biến thể, biến thể anh em đứng 6–20", "Đọc trang live trước. Sắp lại khối có sẵn trước khi thêm khối mới."),
    ("B2 · B7", "Đưa đúng segment của query vào title, H1, heading", "Title, H1 thiếu mảnh người dùng gõ (tên tỉnh, tên dịch vụ, có dấu)", "Giả thuyết: chạy pilot có nhóm đối chứng trước khi áp cả template."),
    ("B6 · B8", "K2Q và đoạn trả lời ngay dưới heading", "Keyword dạng câu hỏi, giá, so sánh đang ở hạng 4–10", "Không dùng heading câu hỏi cho query thương mại thuần."),
    ("B5", "Context địa điểm", "Biến thể địa danh của cùng một query", "Kiểm SERP overlap trước khi gom biến thể địa danh. Chỉ ghi dịch vụ có thật."),
    ("B3", "Anchor nhất quán: một anchor trỏ một URL", "Anchor lặp sitewide đang trỏ nhiều URL hoặc sai URL", "Anchor thành synthetic query chỉ khi lặp trên rất nhiều trang (US9916366B1)."),
    ("B7", "Sửa điều kiện retrieve trước mọi topic", "Trang có trên site mà keyword không có hạng: noindex, canonical sai, trang chờ, chưa live", "Một lỗi retrieve có thể gỡ nhiều keyword cùng lúc."),
]


def s_overview_rules():
    rows = "".join(f'<tr><td><span class="tid">{a}</span></td><td class="m">{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td></tr>' for a, b, c, d in PATTERNS)
    return slide("Pattern", "01 · <b>Pattern dùng lại</b>", f'''
    <h2 class="h2 reveal d1">7 pattern Query Processing <span class="grad-text">dùng lại được</span></h2>
    <div class="row grow" style="gap:36px">
      <table class="tbl patt f1 reveal d2"><thead><tr><th style="width:9%">Trạm</th><th style="width:28%">Pattern</th><th style="width:28%">Khi nào dùng</th><th>Lưu ý</th></tr></thead><tbody>{rows}</tbody></table>
      <div class="col reveal d3" style="width:430px;flex:none">
        <div class="card gradb"><span class="lbl">Luật chung</span><p>Trước ngày đo, trang đang giữ Top 3 hoặc Top 5 chỉ thêm, không rút.</p><p>Trang vừa sửa: chờ 14 ngày rồi mới đọc. Giữ nhật ký thay đổi theo URL.</p><p>Đọc hạng bằng median các ngày đo hợp lệ.</p></div>
        <div class="card"><span class="lbl">Không làm</span><p>Blog chỉ kéo traffic. Scale trang /x-vs-y hoặc trang địa điểm bằng AI. So sánh chê đối thủ. Nhân một khung H2 sang nhiều category.</p></div>
      </div>
    </div>''', src="Pattern rút từ đợt chẩn đoán Query Processing 10 dự án GTV (10/2026, đã kiểm chéo). Áp cho dự án này khi khớp điều kiện ở cột “Khi nào dùng”.", guide=guide("patterns"))


# ---------- slide dự án ----------
def s_beat(P, idx, n, web):
    stats = list(P["beat_stats"]) + ([] if web else list((P.get("kpi") or {}).get("beat_stats", [])))
    st = "".join(f"<div><b>{e(a)}</b><span>{t(b)}</span></div>" for a, b in stats)
    lines = "<br>".join(e(x) for x in P.get("name_lines") or [P["name"]])
    pos = f"Dự án {idx}/{n}" if n > 1 else "Dự án"
    return f'''<section class="slide s-beat" data-title="{e(P["name"])}">
  <div class="beat-rings"></div>
  <header class="chrome"><span class="sec">{pos}</span><span class="pgn"></span></header>
  <div class="beat">
    <div class="eyebrow reveal d1">{pos} · Lead {e(P.get("lead") or "chưa gán")} · {e(P["domain"])}</div>
    <h2 class="reveal d2">{lines}</h2>
    <div class="beat-stats reveal d3">{st}</div>
  </div>
  {FOOT}
</section>'''


def sec(P, label, num="02"):
    return f'{num} · <b>{e(P["name"])} · {label}</b>'


def s_templates(P, r):
    T = P["templates"]
    items = T["items"]
    maxn = max(x["n"] for x in items)
    bars = ""
    for x in items:
        n, now, ago = x["n"], x["now"], x["ago"]
        if r.has:
            segs = "".join(f'<i class="{b}" style="width:{100 * now.get(b, 0) / n:.2f}%"></i>' for b in ("t3", "t10", "t20", "t50", "out") if now.get(b))
            t10n = now.get("t3", 0) + now.get("t10", 0)
            tt = f'<span class="ta">{ago.get("t3", 0) + ago.get("t10", 0)}</span>→<b>{t10n}</b>' if ago else f'<b>{t10n}</b>'
        else:
            segs = '<i class="nod" style="width:100%"></i>'
            tt = "—"
        st = f'<span class="st {e(x["status"])}"{tipa(STATUS_TIP.get(x["status"]))}>{e(x["status_label"])}</span>'
        bars += f'''<div class="tb"{tipa(x.get("tip"))}><div class="tl">{e(x["label"])}</div><div class="tbar"><div class="sb" style="width:{100 * n / maxn:.1f}%">{segs}</div><span class="tn">{n}</span>{ti(x.get("tip"))}</div>
      <div class="tt">{tt}</div><div class="ts">{st}<small>{t(x["note"])}</small></div></div>'''
    if r.has:
        legend = f'<span><i class="t3"></i>Top 3</span><span><i class="t10"></i>4–10</span><span><i class="t20"></i>11–20</span><span><i class="t50"></i>21–{r.depth}</span><span><i class="out"></i>ngoài {r.depth}</span><span class="lg-r">{f"Top 10: {r.cl} → nay" if r.cmp else "Top 10 hiện tại (chưa có mốc so sánh)"}</span>'
    else:
        legend = '<span><i class="nod"></i>chưa có số đo hạng</span><span class="lg-r">Độ dài thanh = số keyword</span>'
    dense = " dense" if len(items) > 14 else ""
    return slide("Template", sec(P, "Gom template"), f'''
    <h2 class="h2 reveal d1">{t(T["title"])}</h2>
    <div class="legend reveal d2">{legend}</div>
    <div class="tbars{dense} reveal d3">{bars}</div>''', src=T.get("src", ""), guide=guide("templates", P), qp=P["slug"])


def s_grid(P, r):
    G = P["grid"]
    btn = "".join(f'<button class="btn{" on" if i == 0 else ""}" data-t="{e(x["id"])}">{e(x.get("label") or (x["base"] + " " + x["slot"]))}</button>' for i, x in enumerate(G["tabs"]))
    run_tip = "Minh họa cách Koray mô tả: Google thử site ở biến thể đang có hạng tốt nhất, rồi thử các biến thể cùng cấu trúc. Đây là hình minh họa, không phải dữ liệu đo."
    return slide("Lưới template", sec(P, "Lưới hạng"), f'''
    <h2 class="h2 reveal d1">{t(G["title"])}</h2>
    <div class="btnrow tabs tgTabs reveal d2">{btn}</div>
    <div class="row grow" style="gap:44px">
      <div class="col f14 reveal d2">
        <div class="tpl-line tgLine"></div>
        <div class="tchips tgChips"></div>
        <div class="row" style="gap:16px;align-items:center;margin-top:4px"><button class="btn primary tgRun"{tipa(run_tip)}>▶ Mô phỏng lan trust</button><button class="btn tgReset">Làm lại</button><span class="tpl-msg tgMsg"></span></div>
      </div>
      <div class="col f1 reveal d3">
        <div class="card"><span class="lbl">Đọc lưới</span><p class="tgRead"></p></div>
        <div class="card gradb"><span class="lbl tgTopic"></span><p class="tgAct"></p></div>
      </div>
    </div>''', cls="s-tg", src=G.get("src", ""), attrs=f' data-qp="{P["slug"]}"', guide=guide("grid", P))


def _txt(x):
    return x["text"] if isinstance(x, dict) else x


def _tip(x):
    return x.get("tip") if isinstance(x, dict) else None


def s_canonical(P):
    C = P["canonical"]

    def pri(x):
        tag = x["tag"]
        return "hi" if x.get("new") or "P0" in tag else "keep" if tag in ("giữ", "keep") else "mid"
    crow = "".join(f'<tr{tipa(x.get("tip"))}><td class="m">{t(x["query"])}</td><td>{t(x["google"])}</td><td>{t(x["problem"])}</td><td>{t(x["decision"])}{ti(x.get("tip"))}</td><td><span class="pri {pri(x)}">{e(x["tag"])}</span></td></tr>' for x in C["rows"])
    rules = "".join(f"<p{tipa(_tip(x))}>{t(_txt(x))}{ti(_tip(x))}</p>" for x in C["rules"])
    F = C.get("flip")
    flip = ""
    if F:
        steps = "".join(f"<li>{t(s)}</li>" for s in F["steps"])
        flip = f'<div class="card flip"{tipa(F.get("tip"))}><span class="lbl">{t(F["label"])}{ti(F.get("tip"))}</span><ol>{steps}</ol></div>'
    return slide("Canonical", sec(P, "Canonical"), f'''
    <h2 class="h2 reveal d1">{t(C.get("title") or "Một query đại diện = <g>một URL</g>")}</h2>
    <div class="row grow" style="gap:32px">
      <table class="tbl cant f1 reveal d2"><thead><tr><th style="width:17%">Query</th><th style="width:25%">Google đang chọn</th><th style="width:23%">Vấn đề</th><th>Quyết định</th><th style="width:8%">Topic</th></tr></thead><tbody>{crow}</tbody></table>
      <div class="col reveal d3{" cflip" if F else ""}" style="width:{430 if F else 360}px;flex:none">
        <div class="card gradb"><span class="lbl">Luật</span>{rules}</div>{flip}
      </div>
    </div>''', src=C.get("src", ""), guide=guide("canonical", P), qp=P["slug"])


TYCLS = {"cat", "home", "list", "guide", "aio", "vid", "prod", "local", "forum", "news", "other"}


def s_serp(P):
    S = P["serp"]
    cards = ""
    for i, c in enumerate(S["cards"]):
        rs = ""
        for x in c["rows"]:
            cls = x["cls"] if x["cls"] in TYCLS else "other"
            rtip = x.get("tip") or ("Dòng của site trong cùng lần đo." if x.get("me") else None)
            rs += f'<div class="sr{" me" if x.get("me") else ""}"{tipa(rtip)}><span class="p">{e(str(x["p"]))}</span><span class="ty {cls}"{tipa(TYPE_TIP.get(cls))}>{e(x["type"])}</span><span class="dm">{e(x["domain"])}</span><span class="dr">{e(x.get("dr", ""))}</span></div>'
        so = f'<div class="so"{tipa(c.get("so_tip"))}>{t(c["so"])}{ti(c.get("so_tip"))}</div>' if c.get("so") else ""
        cards += f'<div class="serpc reveal d{i + 2}"><div class="q">{e(c["query"])}</div><div class="d">{e(c["meta"])}</div>{rs}<div class="verdict">{t(c["verdict"])}</div>{so}</div>'
    return slide("SERP", sec(P, "SERP"), f'''
    <h2 class="h2 reveal d1">{t(S.get("title") or "Loại trang Google chọn quyết định <g>URL nào được đẩy</g>")}</h2>
    <div class="row grow"><div class="serp3" style="width:100%">{cards}</div></div>''', cls="s-serp", src=S.get("src", ""), guide=guide("serp", P), qp=P["slug"])


def mx_stage_tip(x, a, b):
    v = int(x["stages"].get(a, 0))
    if not v:
        return None
    why = (x.get("why") or {}).get(a)
    role = "trạm chính" if v == 2 else "trạm phụ"
    return f"<b>{a} {b} · {role}:</b> {why}" if why else STAGE_TIP.get(a)


def s_matrix(P):
    M = P["matrix"]
    head = "".join(f'<th{tipa(STAGE_TIP.get(a))}><b>{a}</b><small>{b}</small></th>' for a, b in STAGES)
    rows = ""
    for i, x in enumerate(M["rows"]):
        cells = "".join(f'<td><span class="dot v{int(x["stages"].get(a, 0))}"{tipa(mx_stage_tip(x, a, b))}></span></td>' for a, b in STAGES)
        rows += f'<tr data-i="{i}"{" class=sel" if i == 0 else ""}><td class="nm">{e(x["name"])}</td>{cells}<td class="tp">{e(x["topic"])}</td></tr>'
    dense = " dense" if len(M["rows"]) > 11 else ""
    sub = M.get("sub") or "Mỗi dòng là một cụm keyword. Chấm đặc là trạm hỏng chính, vòng rỗng là trạm phụ. Rê chuột lên tên trạm hoặc lên chấm để xem giải thích; bấm vào dòng để xem chẩn đoán và việc làm."
    return slide("Pipeline", sec(P, "Pipeline"), f'''
    <h2 class="h2 reveal d1">{t(M.get("title") or "Mỗi cụm hỏng ở <g>một trạm khác nhau</g>")}</h2>
    <p class="mxsub reveal d1">{t(sub)}</p>
    <div class="row grow" style="gap:40px">
      <table class="mx mxT{dense} reveal d2"><thead><tr><th class="nm">Cụm keyword cam kết</th>{head}<th>Topic</th></tr></thead><tbody>{rows}</tbody></table>
      <div class="col reveal d3" style="width:540px;flex:none">
        <div class="card mxc"><span class="lbl mxName"></span><p class="mxs mxStat"></p><p class="mxst mxStg"></p><p class="mxDiag"></p><p class="mxfix mxFix"></p></div>
        <div class="mxlg"><span><i class="dot v2"></i>trạm chính</span><span><i class="dot v1"></i>trạm phụ</span></div>
      </div>
    </div>''', cls="s-mx", src=M.get("src", ""), attrs=f' data-qp="{P["slug"]}"', guide=guide("matrix", P))


CIRC = "①②③④⑤⑥⑦"


def s_aug(P, r):
    A = P["aug"]
    comps = A["components"]

    def q(k):
        vol = f' · {e(str(k["vol"]))}' if k.get("vol") else ""
        return f'{e(k.get("label") or k["kw"])} {r.chip(k)}{vol}'
    wf = "".join(f'<div class="wb{" h1" if i == 0 else ""}" data-k="{i + 1}"{tipa(c.get("tip"))}><span>{e(c["short"])} <small>{CIRC[i]}</small></span>{"<div class=gal><i></i><i></i><i></i><i></i></div>" if i == 0 else ""}</div>' for i, c in enumerate(comps))
    at = "".join(f'<tr data-k="{i + 1}"{tipa(c.get("tip"))}><td><span class="k">{i + 1}</span></td><td>{t(c["desc"])}{ti(c.get("tip"))}</td><td class="m qs">{"<br>".join(q(k) for k in c["kws"])}</td></tr>' for i, c in enumerate(comps))
    return slide("Augmentation", sec(P, "Augmentation map"), f'''
    <h2 class="h2 reveal d1">{t(A["title"])}</h2>
    <div class="row grow">
      <div class="wf reveal d2"><div class="nav">{e(A["url"])}</div>{wf}</div>
      <div class="f1 reveal d3"><table class="tbl augt"><thead><tr><th style="width:52px"></th><th style="width:44%">Component trên trang</th><th>Keyword cam kết · hạng {e(r.eng)}</th></tr></thead><tbody>{at}</tbody></table></div>
    </div>''', cls="s-aug", src=A.get("src", ""), attrs=f' data-n="{len(comps)}"', guide=guide("aug", P), qp=P["slug"])


def s_levers(P):
    L = P["levers"]
    cols = ""
    for i, c in enumerate(L["cols"]):
        its = "".join(f'<li{tipa(x.get("tip"))}><span class="kd {KIND_CLS.get(x["k"], "tech")}">{e(x["k"])}</span><span class="lt">{t(x["text"])}{ti(x.get("tip"))}</span></li>' for x in c["items"])
        cols += f'<div class="lvc reveal d{min(i + 2, 5)}"><h4>{t(c["label"])}</h4><ul>{its}</ul></div>'
    dont = "".join(f"<span{tipa(_tip(x))}>{t(_txt(x))}{ti(_tip(x))}</span>" for x in L.get("dont", []))
    dont = f'<div class="lvno reveal d5"><b>Không làm</b>{dont}</div>' if dont else ""
    return slide("Ngoài chữ", sec(P, "Ngoài nội dung"), f'''
    <h2 class="h2 reveal d1">{t(L.get("title") or "Ngoài chữ: <g>4 nhóm việc</g> đi kèm")}</h2>
    <div class="row grow"><div class="lv4" style="width:100%">{cols}</div></div>{dont}''', cls="s-lv", src=L.get("src", ""), guide=guide("levers", P), qp=P["slug"])


def s_pairs(P, r):
    X = P["pairs"]

    def pq(k):
        return f'<div>{e(k.get("label") or k["kw"])} {r.chip(k)}</div>'
    pc = "".join(f'<div class="pair"><div class="pe"><span>{e(p["a"])}</span><b>{e(p.get("op", "và"))}</b><span>{e(p["b"])}</span></div><div class="pq">{"".join(pq(k) for k in p["kws"])}</div></div>' for p in X["items"])
    note = f'<p class="note">{t(X["note"])}</p>' if X.get("note") else ""
    return slide("So sánh", sec(P, "Query semantics"), f'''
    <h2 class="h2 reveal d1">{t(X.get("title") or "Query “X và Y”: hai entity anh em, <g>đặt song song</g>")}</h2>
    <div class="row grow" style="gap:40px">
      <div class="pairs f14 reveal d2">{pc}</div>
      <div class="col f1 reveal d3">
        <div class="card"><span class="lbl">{t(X["why"]["label"])}</span><p>{t(X["why"]["text"])}</p></div>
        <div class="card gradb"><span class="lbl">{t(X["action"]["label"])}</span><p>{t(X["action"]["text"])}</p></div>
        {note}
      </div>
    </div>''', src=X.get("src", ""), guide=guide("pairs", P), qp=P["slug"])


def s_retrieve(P, r):
    G = P["retrieve"]
    rows = "".join(f'<tr{tipa(x.get("tip"))}><td class="m">{e(x["url"])}</td><td>{"<br>".join(e(k["kw"]) for k in x["kws"])}</td><td class="m">{"<br>".join(r.txt(k.get("now")) for k in x["kws"])}</td><td>{t(x["note"])}{ti(x.get("tip"))}</td></tr>' for x in G["rows"])
    return slide("Retrieve", sec(P, "Trạm Retrieve"), f'''
    <h2 class="h2 reveal d1">{t(G["title"])}</h2>
    <div class="row grow" style="gap:36px">
      <table class="tbl gapt f1 reveal d2"><thead><tr><th style="width:27%">Trang trên site</th><th style="width:30%">Keyword cam kết</th><th style="width:10%">Hạng</th><th>{e(G.get("check_label", "Đã kiểm"))}</th></tr></thead><tbody>{rows}</tbody></table>
      <div class="col reveal d3" style="width:420px;flex:none">
        <div class="card"><span class="lbl">Đã kiểm</span><p>{t(G["checked"])}</p></div>
        <div class="card gradb"><span class="lbl">{e(G.get("hyp_label", "Giả thuyết · cần GSC"))}</span><p>{t(G["hypothesis"])}</p></div>
      </div>
    </div>''', src=G.get("src", ""), guide=guide("retrieve", P), qp=P["slug"])


def s_qa(P):
    Q = P["qa"]
    cards = "".join(f'''<div class="qa-c reveal d{min(i + 2, 5)}"{tipa(x.get("tip"))}><div class="qq">{t(x["q"])}{ti(x.get("tip"))}</div><p class="qa-a">{t(x["a"])}</p><p class="qa-e"><b>Bằng chứng:</b> {t(x["ev"])}</p><p class="qa-x"><b>Làm:</b> {t(x["act"])}</p></div>''' for i, x in enumerate(Q["items"]))
    return slide("Hỏi đáp", sec(P, "Hỏi đáp triển khai"), f'''
    <h2 class="h2 reveal d1">{t(Q.get("title") or "Hỏi đáp <g>triển khai</g>")}</h2>
    <div class="row grow"><div class="qa4" style="width:100%">{cards}</div></div>''', cls="s-qa", src=Q.get("src", ""), guide=guide("qa", P), qp=P["slug"])


def s_priority(P):
    X = P["priority"]
    has_why = any(x.get("why") for x in X["rows"])

    def row(x):
        pc = "hi" if x["pri"] == "P0" else "mid" if x["pri"] == "P1" else "keep"
        if has_why:
            mid = f'<td class="m">{t(x["template"])}</td><td>{t(x["evidence"])}</td><td>{t(x["why"])}{ti(x.get("tip"))}</td><td class="m">{e(str(x["n_kw"]))}</td>'
            head = f'<td><span class="tid">{e(x["id"])}</span><small class="stg">{e(x["stages"])}</small></td>'
        else:
            mid = f'<td class="m">{t(x["template"])}</td><td>{t(x["evidence"])}</td><td class="m">{e(str(x["n_kw"]))}</td><td class="m">{e(x["stages"])}</td>'
            head = f'<td><span class="tid">{e(x["id"])}</span></td>'
        return f'<tr{tipa(x.get("tip"))}>{head}{mid}<td><span class="pri {pc}">{e(x["pri"])}</span></td><td>{t(x["when"])}</td></tr>'
    pr = "".join(row(x) for x in X["rows"])
    if has_why:
        th = '<th style="width:7%">Topic</th><th style="width:18%">Template</th><th style="width:19%">Bằng chứng</th><th style="width:27%">Vì sao xếp ở đây</th><th style="width:7%">Keyword</th><th style="width:7%">Ưu tiên</th><th>Thời điểm</th>'
    else:
        th = '<th style="width:6%">Topic</th><th style="width:26%">Template</th><th style="width:22%">Bằng chứng</th><th style="width:8%">Keyword</th><th style="width:11%">Trạm</th><th style="width:7%">Ưu tiên</th><th>Thời điểm</th>'
    return slide("Ưu tiên", sec(P, "Ưu tiên"), f'''
    <h2 class="h2 reveal d1">{t(X.get("title") or "Bảng ưu tiên template → <g>topic</g>")}</h2>
    <div class="row grow"><table class="tbl prt{" why" if has_why else ""} reveal d2"><thead><tr>{th}</tr></thead><tbody>{pr}</tbody></table></div>''', src=X.get("src", ""), guide=guide("priority", P), qp=P["slug"])


def s_measure(P):
    M = P["measure_slide"]
    rx = "".join(f'<tr{tipa(x.get("tip"))}><td>{e(x["name"])}{ti(x.get("tip"))}</td><td><code class="rx">{e(x["rx"])}</code></td></tr>' for x in M["regex"])
    tl = "".join(f'<div class="tl-i"{tipa(x.get("tip"))}><div class="d">{e(x["d"])}</div><p>{t(x["t"])}{ti(x.get("tip"))}</p></div>' for x in M["timeline"])
    why = f'<p class="note why"><b>Vì sao đo theo template:</b> {t(M["why"])}</p>' if M.get("why") else ""
    return slide("Đo", sec(P, "Đo lường"), f'''
    <h2 class="h2 reveal d1">Đo theo <span class="grad-text">template</span>, không đo từng keyword</h2>
    <div class="row grow">
      <div class="col f14 reveal d2">{why}<p class="note">{t(M["intro"])}</p>
        <table class="tbl rxt"><thead><tr><th style="width:30%">Template</th><th>Regex</th></tr></thead><tbody>{rx}</tbody></table></div>
      <div class="col" style="width:600px;flex:none">
        <div class="card reveal d3"><div class="tline">{tl}</div></div>
        <div class="card gradb reveal d4"{tipa(M["rule"].get("tip"))}><span class="lbl">{t(M["rule"]["label"])}{ti(M["rule"].get("tip"))}</span><p>{t(M["rule"]["text"])}</p></div>
      </div>
    </div>''', cls="s-ms", src=M.get("src", ""), guide=guide("measure", P), qp=P["slug"])


def s_plan(P, web):
    X = P["plan"]
    cards = [c for c in X["cards"] if not (web and c.get("internal"))]
    if X.get("rows"):
        tr = "".join(f'<tr{tipa(x.get("tip"))}><td class="m">{t(x["when"])}</td><td><span class="ck"></span>{t(x["task"])}{ti(x.get("tip"))}</td><td>{t(x["who"])}</td><td>{t(x["done"])}</td></tr>' for x in X["rows"])
        cc = "".join(f'<div class="pcard{" g" if i == 0 else ""}"><b>{t(c["label"])}:</b> {t(c["text"])}</div>' for i, c in enumerate(cards))
        return slide("Kế hoạch", sec(P, "Kế hoạch hành động"), f'''
    <h2 class="h2 reveal d1">{t(X.get("title") or "Kế hoạch hành động")}: <span class="grad-text">{e(X["who"])}</span> ({e(X["period"])})</h2>
    <div class="row grow"><table class="tbl plt reveal d2"><thead><tr><th style="width:11%">Khi nào</th><th style="width:47%">Việc</th><th style="width:9%">Ai làm</th><th>Xong khi</th></tr></thead><tbody>{tr}</tbody></table></div>
    <div class="pcards reveal d3">{cc}</div>''', cls="s-plan", src=X.get("src", ""), guide=guide("plan", P), qp=P["slug"])
    cc = "".join(f'<div class="card{" gradb" if i == 0 else ""}"><span class="lbl">{t(c["label"])}</span><p>{t(c["text"])}</p></div>' for i, c in enumerate(cards))
    return slide("2 tuần", sec(P, "Việc 2 tuần"), f'''
    <h2 class="h2 reveal d1">2 tuần tới: <span class="grad-text">{e(X["who"])}</span> ({e(X["period"])})</h2>
    <div class="row grow">
      <ul class="chk f14 reveal d2">{"".join(f"<li><i></i><span>{t(c)}</span></li>" for c in X["items"])}</ul>
      <div class="col f1 reveal d3">{cc}</div>
    </div>''', src=X.get("src", ""), guide=guide("plan", P), qp=P["slug"])


def project_slides(P, idx, n, web):
    r = R(P)
    out = [s_beat(P, idx, n, web), s_templates(P, r), s_grid(P, r), s_canonical(P), s_serp(P), s_matrix(P)]
    if P.get("aug"):
        out.append(s_aug(P, r))
    if P.get("pairs"):
        out.append(s_pairs(P, r))
    if P.get("levers"):
        out.append(s_levers(P))
    if P.get("retrieve"):
        out.append(s_retrieve(P, r))
    if P.get("qa"):
        out.append(s_qa(P))
    out += [s_priority(P), s_measure(P), s_plan(P, web)]
    return out


def jsre(k):
    return re.sub(r"[.*+?^${}()|[\]\\/]", lambda m: "\\" + m.group(0), k)


def js_data(P):
    r = R(P)
    tg = {x["id"]: {"base": x["base"], "slot": x["slot"], "read": t(x["read"]), "act": t(x["act"]), "topic": plain(x["topic"]),
                    "chips": [[c["label"], c.get("now") if r.has else None, c.get("ago") if r.has else None, 1 if c.get("gap") else 0, c["kw"]] for c in x["chips"]]}
          for x in P["grid"]["tabs"]}
    mx = []
    for x in P["matrix"]["rows"]:
        stg = " · ".join(f'{"Trạm chính" if int(x["stages"].get(a, 0)) == 2 else "Trạm phụ"}: {a} {b}' for a, b in STAGES if int(x["stages"].get(a, 0)))
        fix = f'<b>Việc làm:</b> {t(x["fix"])}' if x.get("fix") else ""
        mx.append([e(x["name"]), t(x["stat"]), e(stg), t(x["diag"]), fix])
    m = P["measure"]
    gloss = [[jsre(k), v] for k, v in (P.get("gloss") or {}).items()]
    if m.get("engine") and m.get("engine_label"):
        gloss.append([jsre(m["engine"]), f'Engine đo hạng trong {m.get("tool", "SpySERP")}: {m["engine_label"]}. Team báo cáo theo engine này.'])
    for x in P["priority"]["rows"]:
        if re.fullmatch(r"T\d+", x["id"]):
            gloss.append([x["id"], f'<b>Topic {x["id"]}</b> ({x["pri"]}, {plain(x["when"])}): {plain(x["template"])}. Bằng chứng: {plain(x["evidence"])}.'])
    return {"tg": tg, "mx": mx, "has": r.has, "depth": r.depth, "cmp": r.cmp, "cl": r.cl, "first": P["grid"]["tabs"][0]["id"], "gloss": gloss}


# ---------- CSS / JS ----------
EXTRA_CSS = r'''
.s-cover h1.sm{font-size:86px;line-height:1.02;margin:26px 0 30px}
.typed.tq{font-size:27px}
.slide.visible .typed.tq{animation:typingq 2.2s steps(var(--n)) .5s forwards,blink .8s step-end 2.7s 4}
@keyframes typingq{to{width:var(--w)}}
.qa .typed.tq{width:var(--w);animation:none}
.pill.back{text-decoration:none;color:var(--blue-deep);border-color:var(--blue)}
.tk.new{border:2px solid var(--pink);color:var(--pink)}
.rep-sub{font:500 18px/1.4 var(--mono);margin-top:12px;opacity:.85}
.flow3{display:flex;align-items:stretch;gap:24px;width:100%}
.flow3 .stat{flex:1;padding:30px 32px}
.flow3 .stat .v{font-size:84px}
.flow3 .stat .t{font-size:23px}
.farrow{display:flex;align-items:center;font:800 54px/1 var(--disp);color:var(--purple)}
.tbl.tp10 td{font-size:18px;padding:9px 11px;line-height:1.3}
.tbl.tp10.dense td{padding:7px 11px;font-size:17px}
.tbl.tp10 td.m{font-size:16px}
.tbl.tp10 td small{display:block;font:400 14px/1.3 var(--body);color:var(--muted);margin-top:3px}
.tbl.tp10 a{color:var(--blue-deep);text-decoration:none;border-bottom:1.5px solid rgba(6,147,227,.35)}
.tbl.patt td{font-size:17px;padding:10px 11px;line-height:1.35}.tbl.patt td.m{font-weight:600}
.k-muted{color:var(--faint)}
.beat-stats{display:flex;gap:56px;margin-top:10px;flex-wrap:wrap}
.beat-stats div{display:flex;flex-direction:column;gap:10px}
.beat-stats b{font:800 64px/1 var(--disp);color:#fff;letter-spacing:-.02em}
.beat-stats span{font:500 19px/1.3 var(--mono);color:rgba(255,255,255,.82)}
.legend{display:flex;gap:26px;align-items:center;font:500 17px/1 var(--mono);color:var(--muted);margin:6px 0 16px}
.legend i{display:inline-block;width:18px;height:18px;border-radius:5px;margin-right:8px;vertical-align:-3px}
.legend .lg-r{margin-left:auto}
.t3{background:#0B5E94}.t10{background:#0693E3}.t20{background:rgba(153,0,239,.5)}.t50{background:#CBD5E1}.out{background:rgba(239,0,75,.28)}.nod{background:repeating-linear-gradient(45deg,#CBD5E1 0 8px,#E2E8F0 8px 16px)}
.tbars{display:flex;flex-direction:column;gap:4px}
.tb{display:grid;grid-template-columns:470px 1fr 110px 470px;gap:18px;align-items:center;height:44px}
.tbars.dense{gap:2px}.tbars.dense .tb{height:38px}.tbars.dense .tl{font-size:17px}
.tl{font:500 19px/1.15 var(--mono);color:var(--ink);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tbar{display:flex;align-items:center;gap:12px;height:30px}
.sb{display:flex;height:30px;border-radius:7px;overflow:hidden;transform-origin:left center;transform:scaleX(0);transition:transform 1s var(--ease) .3s}
.slide.visible .sb{transform:scaleX(1)}.qa .sb{transform:scaleX(1);transition:none}
.sb i{display:block;height:100%}
.tn{font:600 19px var(--mono);color:var(--muted)}
.tt{font:500 21px var(--mono);color:var(--faint);text-align:center}.tt b{color:var(--blue-deep);font-size:24px;margin-left:6px}.tt .ta{margin-right:6px}
.ts{display:flex;align-items:center;gap:12px;min-width:0}
.ts small{font:400 16px/1.2 var(--body);color:var(--muted)}
.st{font:600 15px/1 var(--mono);padding:7px 10px;border-radius:7px;white-space:nowrap}
.st.ok{background:rgba(6,147,227,.14);color:var(--blue-deep)}.st.up{background:var(--grad);color:#fff}.st.mid{background:var(--bg-3);color:var(--ink)}.st.no{background:rgba(239,0,75,.1);color:var(--pink)}
.tabs{margin:2px 0 8px;flex-wrap:wrap}.tabs .btn{font-size:17px;padding:11px 15px}
.tpl-line{font:700 34px/1.2 var(--disp);margin-bottom:6px}
.s-tg .tchips{gap:11px}
.s-tg .tchip{padding:12px 13px 11px}
.s-tg .tchip .v{font-size:19px;padding-right:62px}
.s-tg .tchip .m{font-size:14px}
.s-tg .tchip .rk{font-size:16px}
.tchip .rk.r3{background:#0B5E94;color:#fff}.tchip .rk.r10{background:rgba(6,147,227,.16);color:var(--blue-deep)}.tchip .rk.r20{background:rgba(153,0,239,.12);color:var(--purple)}.tchip .rk.r50,.tchip .rk.rout{background:var(--bg-3);color:var(--muted)}
.tchip.gap{border:2px dashed var(--pink)}
.tchip.seed .rk{background:rgba(255,255,255,.25)!important;color:#fff!important}
.s-tg .tpl-msg{margin:0;font-size:19px}
.rk{display:inline-block;font:700 15px/1 var(--mono);padding:4px 7px;border-radius:6px;margin-left:4px;vertical-align:1px}
.rk.r3{background:#0B5E94;color:#fff}.rk.r10{background:rgba(6,147,227,.16);color:var(--blue-deep)}.rk.r20{background:rgba(153,0,239,.12);color:var(--purple)}.rk.r50,.rk.rout{background:var(--bg-3);color:var(--muted)}
.tbl.cant td{font-size:18px;padding:12px 12px}.tbl.cant td.m{font-size:17px;font-weight:600}
.ty.cat{background:rgba(6,147,227,.12);color:var(--blue-deep)}.ty.home{background:var(--bg-3);color:var(--ink)}
.ty.prod{background:rgba(6,147,227,.2);color:var(--blue-deep)}.ty.local{background:rgba(153,0,239,.1);color:var(--purple)}.ty.forum,.ty.news,.ty.other{background:var(--bg-3);color:var(--muted)}
.sr{grid-template-columns:40px 120px 1fr 54px}
.mx{border-collapse:separate;border-spacing:0;flex:1}
.mx th{font:500 15px/1.15 var(--mono);color:var(--faint);text-transform:uppercase;letter-spacing:.06em;padding:0 6px 12px;text-align:center;border-bottom:2px solid var(--line)}
.mx th b{display:block;font:700 19px var(--disp);color:var(--ink);letter-spacing:0}
.mx th small{display:block;font-size:13px;margin-top:4px}
.mx th.nm,.mx td.nm{text-align:left}
.mx td{padding:10px 6px;border-bottom:1px solid var(--line);text-align:center;cursor:pointer;transition:background .2s}
.mx.dense td{padding:7px 6px}
.mx td.nm{font:500 19px/1.2 var(--body);padding-left:12px;width:340px}
.mx td.tp{font:600 16px var(--mono);color:var(--blue-deep)}
.mx tr:hover td{background:var(--bg-2)}
.mx tr.sel td{background:rgba(6,147,227,.08)}
.dot{display:inline-block;width:22px;height:22px;border-radius:50%;vertical-align:middle}
.dot.v0{background:transparent}.dot.v1{border:3px solid var(--purple)}.dot.v2{background:var(--grad)}
.mxs{font:600 19px/1.35 var(--mono)!important;color:var(--blue-deep)!important;margin-bottom:8px}
.mxlg{display:flex;gap:26px;font:500 17px var(--mono);color:var(--muted)}.mxlg i{margin-right:8px}
.augt td.qs{font-size:16px;line-height:1.7}
.wb{font-size:17px}
.pairs{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.pair{border:1.5px solid var(--line);border-radius:18px;padding:16px 18px;background:#fff}
.pe{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.pe span{font:700 21px/1 var(--disp);padding:9px 13px;border-radius:10px;background:var(--bg-3)}
.pe b{font:600 16px var(--mono);color:var(--purple)}
.pq div{font:400 17px/1.55 var(--body);color:var(--muted)}
.tbl.gapt td{font-size:17px;padding:11px 12px;line-height:1.45}.tbl.gapt td.m{font-size:16px}
.tbl.prt td{font-size:18px}
.rxt td{font-size:20px;padding:11px 12px}.rxt code.rx{white-space:normal;word-break:break-word;display:inline-block;font-size:17px}
.tid{display:inline-block;font:700 16px var(--mono);padding:6px 9px;border-radius:7px;background:var(--ink);color:#fff}
.chr-r{display:flex;align-items:center;gap:22px}
.howto{font:600 15px/1 var(--mono);letter-spacing:.06em;color:var(--blue-deep);border:1.5px solid rgba(6,147,227,.45);background:#fff;border-radius:999px;padding:8px 14px;cursor:help;text-transform:none}
.howto::before{content:"?";display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:var(--blue);color:#fff;font:700 12px/1 var(--mono);margin-right:8px;vertical-align:1px}
[data-tip]{cursor:help}
.ti{display:inline-flex;align-items:center;justify-content:center;width:19px;height:19px;border-radius:50%;background:rgba(6,147,227,.15);color:var(--blue-deep);font:700 12px/1 var(--mono);font-style:normal;margin-left:6px;vertical-align:2px}
.gradb .ti,.gradb .gl+.ti{background:rgba(255,255,255,.28);color:#fff}
.gl{border-bottom:2px dotted rgba(6,147,227,.6)}
.tbar .ti{margin-left:0}
.gradb .gl,.tchip.seed .gl{border-bottom-color:rgba(255,255,255,.7)}
.s-serp .sr{height:38px}
.serpc .verdict{margin-top:10px;padding:11px 14px;font-size:18px}
.serpc .so{margin-top:8px;padding:10px 14px;border-radius:12px;background:rgba(6,147,227,.1);font:600 17px/1.4 var(--body);color:var(--blue-deep)}
.cant td{line-height:1.38}
.cflip .card.gradb p{font-size:20px;line-height:1.4}
.flip{padding:20px 24px}.flip ol{margin:0;padding-left:22px}.flip li{font:400 18px/1.4 var(--body);margin-bottom:5px}
.mxsub{font:400 19px/1.4 var(--body);color:var(--muted);margin:-4px 0 6px;max-width:1500px}
.mxc p{font-size:19px;line-height:1.45}.mxc .mxst{font:500 16px/1.35 var(--mono);color:var(--purple);margin:2px 0 8px}.mxc .mxfix{margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(6,147,227,.08);color:var(--blue-deep)}
.lv4{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;align-items:start}
.lvc{background:#fff;border:1.5px solid var(--line);border-radius:20px;padding:20px 20px 12px;box-shadow:0 12px 34px rgba(3,8,21,.05)}
.lvc h4{font:700 25px/1.15 var(--disp);margin-bottom:10px}
.lvc ul{list-style:none;margin:0;padding:0}
.lvc li{display:flex;flex-direction:column;gap:6px;padding:9px 0;border-top:1px solid var(--line);font:400 17px/1.4 var(--body)}
.kd{align-self:flex-start;font:600 12.5px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:5px 8px;border-radius:6px}
.kd.rank{background:var(--grad);color:#fff}.kd.tech{background:rgba(6,147,227,.14);color:var(--blue-deep)}.kd.ux{background:var(--bg-3);color:var(--muted)}
.lvno{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin:10px 0 4px;font:400 17px/1.3 var(--body)}
.lvno b{font:600 15px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--pink)}
.lvno span{padding:7px 12px;border-radius:999px;background:rgba(239,0,75,.07);color:var(--ink)}
.qa4{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.qa-c{background:#fff;border:1.5px solid var(--line);border-radius:20px;padding:20px 24px;box-shadow:0 12px 34px rgba(3,8,21,.05)}
.qq{font:700 24px/1.25 var(--disp);margin-bottom:8px}
.qa-c p{font:400 18px/1.42 var(--body);margin-top:6px}.qa-a{font-weight:600!important;color:var(--blue-deep)}
.qa-e b,.qa-x b{font:600 14px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--purple);margin-right:4px}
.tbl.prt.why td{font-size:16.5px;padding:10px 10px;line-height:1.35}.tbl.prt.why td.m{font-size:15.5px}
.stg{display:block;font:500 12.5px/1.2 var(--mono);color:var(--faint);margin-top:6px}
.s-ms .note.why{color:var(--ink);font-size:20px}
.s-ms .tl-i p{font-size:20px}
.s-plan .row.grow{align-items:flex-start;margin-top:4px}.tbl.plt th{padding-bottom:8px}
.tbl.plt td{font-size:15.5px;padding:7px 9px;line-height:1.32;cursor:pointer}.tbl.plt td.m{font-size:14px;font-weight:600}
.plt .ck{display:inline-block;width:18px;height:18px;border-radius:5px;border:2px solid var(--line-2);margin-right:9px;vertical-align:-3px}
.plt tr.done .ck{background:var(--grad);border-color:transparent}.plt tr.done td{color:var(--muted)}
.pcards{display:flex;gap:14px;margin:6px 0 0}.pcard{flex:1;font:400 15.5px/1.38 var(--body);padding:9px 14px;border-radius:12px;border:1.5px solid var(--line);background:#fff}.pcard.g{background:var(--grad-v);color:#fff;border:none}
#qtip{position:fixed;z-index:9999;max-width:460px;padding:13px 16px;border-radius:12px;background:#0B1220;color:#F1F5F9;font:400 14.5px/1.55 "Be Vietnam Pro",system-ui,sans-serif;box-shadow:0 18px 44px rgba(0,0,0,.28);pointer-events:none;opacity:0;transition:opacity .12s;left:0;top:0}
#qtip.on{opacity:1}#qtip b{color:#7DD3FC;font-weight:600}
'''

APP_JS = r'''
(function () {
  const cls = p => !p ? 'rout' : p <= 3 ? 'r3' : p <= 10 ? 'r10' : p <= 20 ? 'r20' : 'r50';
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  document.querySelectorAll('.s-tg').forEach(root => {
    const D = QP[root.dataset.qp], q = c => root.querySelector(c);
    let key = D.first, timers = [], chips = [];
    function render() {
      const d = D.tg[key];
      q('.tgLine').innerHTML = `${d.base} <span class="slot">${d.slot}</span>`;
      q('.tgChips').innerHTML = d.chips.map((c, i) => {
        const was = !D.has ? 'chưa có số đo' : !D.cmp ? 'chưa có mốc so sánh' : c[2] ? `${D.cl}: #${c[2]}` : `${D.cl}: ngoài ${D.depth}`;
        const now = !D.has ? '—' : c[1] ? '#' + c[1] : '—';
        const tip = esc(`<b>${c[4]}</b><br>Hạng nay: ${now === '—' ? 'ngoài ' + D.depth : now} · ${was}${c[3] ? '<br>Viền hồng: site có trang cho biến thể này nhưng keyword chưa vào độ sâu đo.' : ''}`);
        return `<div class="tchip${c[3] ? ' gap' : ''}" data-i="${i}" data-tip="${tip}"><div class="v">${c[0]}</div><div class="m">${was}</div><span class="rk ${D.has ? cls(c[1]) : 'rout'}">${now}</span></div>`;
      }).join('');
      chips = [...q('.tgChips').children];
      chips.forEach((c, i) => c.addEventListener('click', () => ripple(i)));
      q('.tgRead').innerHTML = d.read; q('.tgAct').innerHTML = d.act; q('.tgTopic').textContent = d.topic;
      reset();
      if (QA) { const s = seedIdx(); chips[s].classList.add('seed'); chips.forEach((c, i) => { if (i !== s && d.chips[i][1]) c.classList.add('lit'); }); }
    }
    function seedIdx() { const d = D.tg[key]; let b = 0; d.chips.forEach((c, i) => { if (c[1] && (!d.chips[b][1] || c[1] < d.chips[b][1])) b = i; }); return b; }
    function reset() { timers.forEach(clearTimeout); timers = []; chips.forEach(c => c.classList.remove('lit', 'seed')); q('.tgMsg').textContent = ''; }
    function ripple(i0) {
      reset(); const d = D.tg[key];
      chips[i0].classList.add('seed');
      q('.tgMsg').textContent = `Google thử site ở biến thể “${d.chips[i0][0]}”, rồi thử các biến thể cùng cấu trúc.`;
      const r0 = Math.floor(i0 / 4), c0 = i0 % 4;
      chips.forEach((c, i) => { if (i === i0) return; const dd = Math.abs(Math.floor(i / 4) - r0) + Math.abs(i % 4 - c0); timers.push(setTimeout(() => c.classList.add('lit'), 500 + dd * 280)); });
    }
    root.querySelectorAll('.tgTabs .btn').forEach(b => b.onclick = () => { root.querySelectorAll('.tgTabs .btn').forEach(x => x.classList.remove('on')); b.classList.add('on'); key = b.dataset.t; render(); });
    q('.tgRun').onclick = () => ripple(seedIdx());
    q('.tgReset').onclick = reset;
    render();
  });
  document.querySelectorAll('.s-mx').forEach(root => {
    const MX = QP[root.dataset.qp].mx, rows = root.querySelectorAll('.mxT tbody tr');
    function sel(i) { rows.forEach(r => r.classList.toggle('sel', +r.dataset.i === i)); ['.mxName', '.mxStat', '.mxStg', '.mxDiag', '.mxFix'].forEach((c, k) => { const el = root.querySelector(c); el.innerHTML = MX[i][k] || ''; el.style.display = MX[i][k] ? '' : 'none'; }); }
    rows.forEach(r => r.addEventListener('click', () => sel(+r.dataset.i)));
    sel(0);
  });
  document.querySelectorAll('.s-aug').forEach(root => {
    const rows = root.querySelectorAll('.augt tbody tr'), blocks = root.querySelectorAll('.wf .wb'), n = +root.dataset.n;
    let auto = null, k = 1, hovering = false;
    function hl(m) { rows.forEach(r => r.classList.toggle('hl', r.dataset.k == m)); blocks.forEach(b => b.classList.toggle('hl', b.dataset.k == m)); }
    [...rows, ...blocks].forEach(el => { el.addEventListener('mouseenter', () => { hovering = true; hl(el.dataset.k); }); el.addEventListener('mouseleave', () => { hovering = false; }); });
    root.addEventListener('enter', () => { clearInterval(auto); k = 1; hl(1); auto = setInterval(() => { if (!hovering) { k = k % n + 1; hl(k); } }, 2400); });
    hl(QA ? Math.min(4, n) : 1);
  });
  document.querySelectorAll('.chk li').forEach(li => li.addEventListener('click', () => li.classList.toggle('done')));
  document.querySelectorAll('.plt tbody tr').forEach(tr => tr.addEventListener('click', () => tr.classList.toggle('done')));
  // chú thích khi rê chuột: một khung nổi ngoài stage (stage bị scale)
  const tip = document.createElement('div'); tip.id = 'qtip'; document.body.appendChild(tip);
  let cur = null;
  function place(x, y) { const w = tip.offsetWidth, h = tip.offsetHeight; let L = x + 16, T = y + 18; if (L + w > innerWidth - 8) L = Math.max(8, x - w - 16); if (T + h > innerHeight - 8) T = Math.max(8, y - h - 14); tip.style.left = L + 'px'; tip.style.top = T + 'px'; }
  function show(el, x, y) { tip.innerHTML = el.dataset.tip; tip.classList.add('on'); cur = el; place(x, y); }
  function hide() { tip.classList.remove('on'); cur = null; }
  const touch = matchMedia('(hover: none)').matches;
  document.addEventListener('mouseover', ev => { if (touch) return; const el = ev.target.closest && ev.target.closest('[data-tip]'); if (el) { if (el !== cur) show(el, ev.clientX, ev.clientY); } else if (cur) hide(); });
  document.addEventListener('mousemove', ev => { if (cur && !touch) place(ev.clientX, ev.clientY); });
  document.addEventListener('click', ev => { if (!touch) return; const el = ev.target.closest && ev.target.closest('[data-tip]'); if (el && el !== cur) show(el, ev.clientX, ev.clientY); else hide(); });
  document.addEventListener('keydown', hide);
  // thuật ngữ: bọc lần xuất hiện đầu tiên trên mỗi slide
  const SKIP = '[data-tip],code,button,.rk,.tid,h1,h2,th,.btnrow,.tchips,.tpl-line,.src,.sr,.mxlg,.legend,.st,.kd,.pill,.eyebrow,.foot,.chrome,.lvno span,.wf .nav';
  document.querySelectorAll('.slide').forEach(sl => {
    const list = QG.concat((QP[sl.dataset.qp] || {}).gloss || []);
    const res = list.map(([p, d]) => [new RegExp('(?<![\\p{L}\\p{N}])(?:' + p + ')(?![\\p{L}\\p{N}])', 'iu'), d]);
    const seen = new Set(), root = sl.querySelector('.wrap'); if (!root) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: n => n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach(n0 => {
      let node = n0;
      while (node) {
        let best = null;
        res.forEach(([re, d], k) => { if (seen.has(k)) return; const m = re.exec(node.data); if (m && (!best || m.index < best.m.index)) best = { m, d, k }; });
        if (!best) break;
        seen.add(best.k);
        const mid = node.splitText(best.m.index), rest = mid.splitText(best.m[0].length);
        const sp = document.createElement('span'); sp.className = 'gl'; sp.dataset.tip = best.d; sp.textContent = mid.data; mid.replaceWith(sp);
        node = rest;
      }
    });
  });
})();
'''


def page(title, slides, data):
    ctrl = BASE_JS.split("/* ===========================================\n   S03")[0]
    edit = BASE_JS[BASE_JS.index("/* ===========================================\n   SỬA CHỮ"):].replace("new SlidePresentation();", "")
    js = ctrl + "\nconst QP = " + json.dumps(data, ensure_ascii=False) + ";\nconst QG = " + json.dumps([[p, d] for p, d in GLOSS], ensure_ascii=False) + ";\n" + APP_JS + edit + "\nnew SlidePresentation();\n"
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<!-- Deck nội bộ GTV, không gửi khách. Nguồn dựng: skill query-processing-diagnosis, scripts/qp_render.py. Sửa nội dung ở file JSON rồi dựng lại, không sửa HTML. Điều hướng: ← → / Space / vuốt. #n mở slide n. ?qa hiện trạng thái cuối. -->
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@1,9..144,500&display=swap" rel="stylesheet">
<style>{BASE_CSS}{EXTRA_CSS}</style>
</head>
<body>
<div class="progress" id="progress"></div>
<button id="edit" title="E">Sửa chữ</button>
<div class="deck-viewport">
<main class="deck-stage" id="deckStage">
{chr(10).join(slides)}
</main>
</div>
<nav class="deck-controls" aria-label="Điều hướng slide">
  <button id="prevBtn" aria-label="Slide trước">‹</button><span id="counter">1 / {len(slides)}</span><button id="nextBtn" aria-label="Slide sau">›</button>
</nav>
<script>{js}</script>
</body>
</html>'''


# ---------- dữ liệu ----------
# Chữ đỏ “cần kiểm tay” (Vincent chốt 12/10/2026): câu nói việc còn là giả thuyết, cần GSC, cần URL Inspection
# hoặc chưa kiểm chéo thì tô đỏ, để Lead kiểm tay trước khi làm. Câu đã có <r> thì giữ nguyên.
KT_RE = re.compile(r"[Cc]ần (GSC|URL Inspection|nhật ký|kiểm tay|xác nhận|đối chiếu)|[Kk]iểm URL Inspection|[Kk]hi có GSC"
                   r"|[Gg]iả thuyết|chưa kiểm chéo|chưa kiểm SERP|chưa xác nhận|chưa rõ|chưa biết|chưa so với|đọc GSC trước|cần GSC", re.I)
KT_SKIP = {"src", "gloss", "mechanism", "slug", "name", "name_lines", "domain", "url", "rx", "kw", "label", "id", "lead", "schema", "tool", "engine"}


def mark_check(s):
    if "<r>" in s or not KT_RE.search(s):
        return s
    parts = re.split(r"(?<=[.!?])(\s+|<br>)", s)
    out = []
    for x in parts:
        bal = all(x.count(f"<{k}>") == x.count(f"</{k}>") for k in "bgi")
        out.append(f"<r>{x}</r>" if KT_RE.search(x) and bal and x.strip() else x)
    return "".join(out)


def _mark(o, key=""):
    if isinstance(o, dict):
        return {k: (v if k in KT_SKIP else _mark(v, k)) for k, v in o.items()}
    if isinstance(o, list):
        return [_mark(v, key) for v in o]
    return mark_check(o) if isinstance(o, str) else o


def load(path):
    return _mark(json.loads(Path(path).read_text(encoding="utf-8")))


def loaded(paths):
    PS = [load(p) for p in paths]
    return [P for _, P in sorted(enumerate(PS), key=lambda x: (x[1].get("order") or 10 ** 6, x[0]))]


def build_project(P, web, back=None, idx=1, n=1):
    slides = [s_cover(P, n, back=back), s_idea(P), s_steps()] + project_slides(P, idx, n, web)
    return page(f"{P['name']} · Query Processing đẩy keyword cam kết", slides, {P["slug"]: js_data(P)})


def build_overview(PS, web, with_projects=False):
    slides = [s_cover(PS[0], len(PS), overview=True, dates=meas_range(PS)), s_overview_idea(PS), s_steps(), s_overview_table(PS, web, link=not with_projects), s_overview_rules()]
    data = {}
    if with_projects:
        for i, P in enumerate(PS):
            slides += project_slides(P, i + 1, len(PS), web)
            data[P["slug"]] = js_data(P)
    return page(f"Query Processing đẩy keyword cam kết · {len(PS)} dự án GTV", slides, data)


# ---------- kiểm ----------
LIM = {  # giới hạn theo bố cục 1920×1080 (đã chụp kiểm ở đợt 10/2026)
    "cover.query": 38, "cover.rep": 48, "cover.rep_sub": 80, "cover.tokens": (2, 4), "cover.token.t": 16, "cover.token.r": 14,
    "idea.mechanism": 230, "idea.effect": 230, "idea.hub_text": 120, "idea.n_kw_text": 110, "idea.src": 260,
    "beat_stats": (2, 3), "beat.stat.a": 10, "beat.stat.b": 34, "kpi.beat_stats": (0, 2), "name_lines": (1, 2), "name_line": 18,
    "templates.items": (5, 16), "templates.label": 40, "templates.status_label": 16, "templates.note": 62,
    "grid.tabs": (3, 6), "grid.tab_label": 44, "grid.chips": (4, 16), "grid.chip.label": 30, "grid.read": 260, "grid.act": 260, "grid.topic": 26, "grid.base+slot": 48,
    "canonical.rows": (3, 6), "canonical.cell": 120, "canonical.tag": 14, "canonical.rules": (2, 4), "canonical.rule": 80,
    "serp.cards": (3, 3), "serp.rows": (6, 10), "serp.domain": 26, "serp.type": 12, "serp.verdict": 130, "serp.query": 42, "serp.meta": 40,
    "matrix.rows": (5, 12), "matrix.name": 36, "matrix.stat": 90, "matrix.diag": 380, "matrix.topic": 6,
    "aug.components": (3, 6), "aug.short": 48, "aug.desc": 110, "aug.kws": (1, 5), "aug.url": 60, "aug.kw": 46,
    "pairs.items": (2, 6), "pairs.kws": (1, 5), "pairs.side": 18, "pairs.kw": 48, "pairs.card": 200, "pairs.note": 140,
    "retrieve.rows": (2, 6), "retrieve.kws": (1, 6), "retrieve.url": 46, "retrieve.note": 110, "retrieve.checked": 230, "retrieve.hypothesis": 230,
    "priority.rows": (4, 9), "priority.template": 52, "priority.evidence": 48, "priority.when": 34,
    "measure.regex": (3, 6), "measure.rx": 110, "measure.timeline": (2, 4), "measure.tl": 110, "measure.intro": 230, "measure.rule": 160,
    "plan.items": (5, 8), "plan.item": 125, "plan.cards": (1, 3), "plan.card": 200,
    "src": 400, "headline.template": 44, "headline.fact": 70, "status_row.set": 44, "status_row.now": 44,
    "tip": 700, "guide": 900, "canonical.flip": (2, 5), "canonical.flip_step": 95, "serp.so": 120, "matrix.why": 300, "matrix.fix": 200, "matrix.sub": 200,
    "levers.cols": (3, 4), "levers.items": (2, 5), "levers.text": 150, "levers.dont": (0, 5), "levers.dont_item": 70,
    "qa.items": (2, 4), "qa.q": 70, "qa.a": 170, "qa.ev": 210, "qa.act": 170, "priority.why": 115, "measure.why": 210,
    "plan.rows": (5, 12), "plan.when": 24, "plan.task": 150, "plan.who": 16, "plan.done": 110,
}
REQ = ["schema", "slug", "name", "domain", "lead", "measure", "status_row", "headline", "cover", "idea", "beat_stats", "templates", "grid",
       "canonical", "serp", "matrix", "priority", "measure_slide", "plan"]


def check(P):
    err = []

    def L(path, s, key):
        n = len(plain(s))
        if n > LIM[key]:
            err.append(f"{path}: {n} ký tự > {LIM[key]} ({key})")
        bad = [m for m in re.findall(r"<[^>]*>", str(s or "")) if not ALLOWED.fullmatch(m)]
        if bad:
            err.append(f"{path}: thẻ không cho phép {bad[:3]}")

    def N(path, arr, key):
        lo, hi = LIM[key]
        if not isinstance(arr, list) or not lo <= len(arr) <= hi:
            err.append(f"{path}: cần {lo}–{hi} mục, có {len(arr) if isinstance(arr, list) else type(arr).__name__}")

    def rank(path, v):
        if v is not None and not (isinstance(v, int) and 1 <= v <= 100):
            err.append(f"{path}: hạng phải là int 1–100 hoặc null, có {v!r}")

    for k in REQ:
        if k not in P:
            err.append(f"thiếu khối {k}")
    if err:
        return err
    def todo(o, path=""):
        if isinstance(o, dict):
            for k2, v in o.items():
                todo(v, f"{path}.{k2}" if path else k2)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                todo(v, f"{path}[{i}]")
        elif isinstance(o, str) and "TODO" in o:
            err.append(f"{path}: còn TODO")
    todo(P)
    if P["schema"] != "qp-project/1":
        err.append(f"schema phải là qp-project/1, có {P['schema']!r}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(P["slug"])):
        err.append(f"slug phải là kebab-case không dấu, có {P['slug']!r}")
    P.setdefault("kpi", {})
    m = P["measure"]
    has = m.get("has_rank", True)
    for k in ("engine", "date"):
        if has and not m.get(k):
            err.append(f"measure.{k} trống")
    L("status_row.set", P["status_row"]["set"], "status_row.set"); L("status_row.now", P["status_row"]["now"], "status_row.now")
    L("headline.template", P["headline"].get("template"), "headline.template"); L("headline.fact", P["headline"].get("fact"), "headline.fact")
    N("name_lines", P.get("name_lines") or [P["name"]], "name_lines")
    for x in P.get("name_lines") or []:
        L("name_lines", x, "name_line")
    c = P["cover"]
    L("cover.query", c["query"], "cover.query"); L("cover.rep", c["rep"], "cover.rep"); L("cover.rep_sub", c["rep_sub"], "cover.rep_sub")
    N("cover.tokens", c["tokens"], "cover.tokens")
    for i, x in enumerate(c["tokens"]):
        L(f"cover.tokens[{i}].t", x["t"], "cover.token.t"); L(f"cover.tokens[{i}].r", x["r"], "cover.token.r")
        if x.get("k", "known") not in ("known", "op", "new"):
            err.append(f"cover.tokens[{i}].k phải là known|op|new")
    d = P["idea"]
    for k in ("mechanism", "effect", "src"):
        L(f"idea.{k}", d.get(k), f"idea.{k}")
    for k in ("hub_text", "n_kw_text"):
        if d.get(k):
            L(f"idea.{k}", d[k], f"idea.{k}")
    if not d.get("hub_text"):
        for k in ("hub_url", "hub_n", "hub_top10"):
            if k not in d:
                err.append(f"idea.{k} thiếu (hoặc dùng idea.hub_text)")
    N("beat_stats", P["beat_stats"], "beat_stats")
    for i, (a, b) in enumerate(P["beat_stats"] + P["kpi"].get("beat_stats", [])):
        L(f"beat_stats[{i}][0]", a, "beat.stat.a"); L(f"beat_stats[{i}][1]", b, "beat.stat.b")
    N("kpi.beat_stats", P["kpi"].get("beat_stats", []), "kpi.beat_stats")
    T = P["templates"]
    L("templates.title", T["title"], "cover.rep_sub"); L("templates.src", T.get("src"), "src")
    N("templates.items", T["items"], "templates.items")
    for i, x in enumerate(T["items"]):
        p = f"templates.items[{i}]"
        L(p + ".label", x["label"], "templates.label"); L(p + ".status_label", x["status_label"], "templates.status_label"); L(p + ".note", x["note"], "templates.note"); L(p + ".tip", x.get("tip"), "tip")
        if x["status"] not in ("ok", "up", "mid", "no"):
            err.append(p + ".status phải là ok|up|mid|no")
        if has:
            if x.get("ago") is None and m.get("compare_date"):
                err.append(f"{p}.ago trống nhưng measure.compare_date = {m['compare_date']}: ghi số mốc so sánh hoặc bỏ compare_date")
            if not m.get("compare_date") and x["status"] == "up":
                err.append(f"{p}.status = up nhưng deck không có mốc so sánh: không gắn 'Đang lan'")
            for w in ("now", "ago"):
                if w == "ago" and x.get("ago") is None:
                    continue
                s = sum(int(x[w].get(b, 0)) for b in ("t3", "t10", "t20", "t50", "out"))
                if s != x["n"]:
                    err.append(f"{p}.{w}: tổng các nhóm hạng {s} ≠ n {x['n']}")
    G = P["grid"]
    L("grid.title", G["title"], "cover.rep_sub"); L("grid.src", G.get("src"), "src")
    N("grid.tabs", G["tabs"], "grid.tabs")
    ids = [x["id"] for x in G["tabs"]]
    if len(set(ids)) != len(ids):
        err.append("grid.tabs: id trùng")
    for i, x in enumerate(G["tabs"]):
        p = f"grid.tabs[{i}]"
        L(p + ".label", x.get("label") or (x["base"] + " " + x["slot"]), "grid.tab_label"); L(p + ".base+slot", x["base"] + " " + x["slot"], "grid.base+slot")
        L(p + ".read", x["read"], "grid.read"); L(p + ".act", x["act"], "grid.act"); L(p + ".topic", x["topic"], "grid.topic")
        N(p + ".chips", x["chips"], "grid.chips")
        for j, ch in enumerate(x["chips"]):
            L(f"{p}.chips[{j}].label", ch["label"], "grid.chip.label"); rank(f"{p}.chips[{j}].now", ch.get("now")); rank(f"{p}.chips[{j}].ago", ch.get("ago"))
            if not ch.get("kw"):
                err.append(f"{p}.chips[{j}].kw trống (keyword đầy đủ)")
    C = P["canonical"]
    N("canonical.rows", C["rows"], "canonical.rows"); N("canonical.rules", C["rules"], "canonical.rules"); L("canonical.src", C.get("src"), "src")
    for i, x in enumerate(C["rows"]):
        for k in ("query", "google", "problem", "decision"):
            L(f"canonical.rows[{i}].{k}", x[k], "canonical.cell")
        L(f"canonical.rows[{i}].tag", x["tag"], "canonical.tag"); L(f"canonical.rows[{i}].tip", x.get("tip"), "tip")
    for i, x in enumerate(C["rules"]):
        L(f"canonical.rules[{i}]", _txt(x), "canonical.rule"); L(f"canonical.rules[{i}].tip", _tip(x), "tip")
    if C.get("flip"):
        N("canonical.flip.steps", C["flip"]["steps"], "canonical.flip"); L("canonical.flip.tip", C["flip"].get("tip"), "tip")
        for i, x in enumerate(C["flip"]["steps"]):
            L(f"canonical.flip.steps[{i}]", x, "canonical.flip_step")
    S = P["serp"]
    N("serp.cards", S["cards"], "serp.cards"); L("serp.src", S.get("src"), "src")
    for i, x in enumerate(S["cards"]):
        p = f"serp.cards[{i}]"
        L(p + ".query", x["query"], "serp.query"); L(p + ".meta", x["meta"], "serp.meta"); L(p + ".verdict", x["verdict"], "serp.verdict"); L(p + ".so", x.get("so"), "serp.so"); L(p + ".so_tip", x.get("so_tip"), "tip")
        N(p + ".rows", x["rows"], "serp.rows")
        for j, rr in enumerate(x["rows"]):
            L(f"{p}.rows[{j}].domain", rr["domain"], "serp.domain"); L(f"{p}.rows[{j}].type", rr["type"], "serp.type")
            if rr["cls"] not in TYCLS:
                err.append(f"{p}.rows[{j}].cls phải thuộc {sorted(TYCLS)}")
        if sum(1 for rr in x["rows"] if rr.get("me")) > 1:
            err.append(p + ": tối đa 1 dòng me=true")
    M = P["matrix"]
    N("matrix.rows", M["rows"], "matrix.rows"); L("matrix.src", M.get("src"), "src")
    for i, x in enumerate(M["rows"]):
        p = f"matrix.rows[{i}]"
        L(p + ".name", x["name"], "matrix.name"); L(p + ".stat", x["stat"], "matrix.stat"); L(p + ".diag", x["diag"], "matrix.diag"); L(p + ".topic", x["topic"], "matrix.topic"); L(p + ".fix", x.get("fix"), "matrix.fix")
        for k, v in (x.get("why") or {}).items():
            L(f"{p}.why.{k}", v, "matrix.why")
            if not x["stages"].get(k):
                err.append(f"{p}.why.{k}: trạm này không có chấm")
        for k, v in x["stages"].items():
            if k not in dict(STAGES) or v not in (0, 1, 2):
                err.append(f"{p}.stages: khoá B2–B8, giá trị 0|1|2 (có {k}={v})")
    if P.get("aug"):
        A = P["aug"]
        L("aug.title", A["title"], "cover.rep_sub"); L("aug.url", A["url"], "aug.url"); L("aug.src", A.get("src"), "src")
        N("aug.components", A["components"], "aug.components")
        for i, x in enumerate(A["components"]):
            p = f"aug.components[{i}]"
            L(p + ".short", x["short"], "aug.short"); L(p + ".desc", x["desc"], "aug.desc"); N(p + ".kws", x["kws"], "aug.kws"); L(p + ".tip", x.get("tip"), "tip")
            for j, k in enumerate(x["kws"]):
                L(f"{p}.kws[{j}]", k.get("label") or k["kw"], "aug.kw"); rank(f"{p}.kws[{j}].now", k.get("now"))
    if P.get("pairs"):
        X = P["pairs"]
        L("pairs.title", X.get("title"), "cover.rep_sub"); L("pairs.src", X.get("src"), "src")
        N("pairs.items", X["items"], "pairs.items")
        for i, x in enumerate(X["items"]):
            L(f"pairs.items[{i}].a", x["a"], "pairs.side"); L(f"pairs.items[{i}].b", x["b"], "pairs.side"); N(f"pairs.items[{i}].kws", x["kws"], "pairs.kws")
            for j, k in enumerate(x["kws"]):
                L(f"pairs.items[{i}].kws[{j}]", k.get("label") or k["kw"], "pairs.kw"); rank(f"pairs.items[{i}].kws[{j}].now", k.get("now"))
        for k in ("why", "action"):
            L(f"pairs.{k}.text", X[k]["text"], "pairs.card"); L(f"pairs.{k}.label", X[k]["label"], "grid.topic")
        if X.get("note"):
            L("pairs.note", X["note"], "pairs.note")
    if P.get("retrieve"):
        X = P["retrieve"]
        L("retrieve.title", X["title"], "cover.rep_sub"); L("retrieve.src", X.get("src"), "src")
        L("retrieve.checked", X["checked"], "retrieve.checked"); L("retrieve.hypothesis", X["hypothesis"], "retrieve.hypothesis")
        N("retrieve.rows", X["rows"], "retrieve.rows")
        for i, x in enumerate(X["rows"]):
            L(f"retrieve.rows[{i}].url", x["url"], "retrieve.url"); L(f"retrieve.rows[{i}].note", x["note"], "retrieve.note"); N(f"retrieve.rows[{i}].kws", x["kws"], "retrieve.kws"); L(f"retrieve.rows[{i}].tip", x.get("tip"), "tip")
            for j, k in enumerate(x["kws"]):
                L(f"retrieve.rows[{i}].kws[{j}]", k["kw"], "aug.kw"); rank(f"retrieve.rows[{i}].kws[{j}].now", k.get("now"))
    X = P["priority"]
    N("priority.rows", X["rows"], "priority.rows"); L("priority.src", X.get("src"), "src")
    for i, x in enumerate(X["rows"]):
        L(f"priority.rows[{i}].template", x["template"], "priority.template"); L(f"priority.rows[{i}].evidence", x["evidence"], "priority.evidence"); L(f"priority.rows[{i}].when", x["when"], "priority.when")
        L(f"priority.rows[{i}].why", x.get("why"), "priority.why"); L(f"priority.rows[{i}].tip", x.get("tip"), "tip")
        if x["pri"] not in ("P0", "P1", "P2"):
            err.append(f"priority.rows[{i}].pri phải là P0|P1|P2")
    X = P["measure_slide"]
    L("measure_slide.intro", X["intro"], "measure.intro"); L("measure_slide.rule.text", X["rule"]["text"], "measure.rule"); L("measure_slide.src", X.get("src"), "src")
    N("measure_slide.regex", X["regex"], "measure.regex"); N("measure_slide.timeline", X["timeline"], "measure.timeline")
    L("measure_slide.why", X.get("why"), "measure.why"); L("measure_slide.rule.tip", X["rule"].get("tip"), "tip")
    for i, x in enumerate(X["regex"]):
        L(f"measure_slide.regex[{i}].rx", x["rx"], "measure.rx"); L(f"measure_slide.regex[{i}].tip", x.get("tip"), "tip")
        try:
            re.compile(x["rx"])
        except re.error as ex:
            err.append(f"measure_slide.regex[{i}].rx không hợp lệ: {ex}")
        if re.search(r"\(\?<?[=!]|\\[1-9]", x["rx"]):
            err.append(f"measure_slide.regex[{i}].rx: GSC dùng RE2, không nhận lookahead, lookbehind hay backreference")
        if re.search(r"\\b(?=[^\x00-\x7f])|(?<=[^\x00-\x7f])\\b", x["rx"]):
            err.append(f"measure_slide.regex[{i}].rx: \\b của RE2 chỉ hiểu chữ không dấu; sát chữ có dấu thì dùng (^| )…( |$)")
    for i, x in enumerate(X["timeline"]):
        L(f"measure_slide.timeline[{i}].t", x["t"], "measure.tl"); L(f"measure_slide.timeline[{i}].tip", x.get("tip"), "tip")
    X = P["plan"]
    N("plan.cards", X["cards"], "plan.cards"); L("plan.src", X.get("src"), "src")
    if X.get("rows"):
        N("plan.rows", X["rows"], "plan.rows")
        for i, x in enumerate(X["rows"]):
            for k in ("when", "task", "who", "done"):
                L(f"plan.rows[{i}].{k}", x[k], f"plan.{k}")
            L(f"plan.rows[{i}].tip", x.get("tip"), "tip")
    else:
        N("plan.items", X["items"], "plan.items")
        for i, x in enumerate(X["items"]):
            L(f"plan.items[{i}]", x, "plan.item")
    if P.get("levers"):
        X = P["levers"]
        N("levers.cols", X["cols"], "levers.cols"); N("levers.dont", X.get("dont", []), "levers.dont"); L("levers.src", X.get("src"), "src")
        for i, c in enumerate(X["cols"]):
            N(f"levers.cols[{i}].items", c["items"], "levers.items")
            for j, x in enumerate(c["items"]):
                L(f"levers.cols[{i}].items[{j}]", x["text"], "levers.text"); L(f"levers.cols[{i}].items[{j}].tip", x.get("tip"), "tip")
                if x["k"] not in KIND_CLS:
                    err.append(f"levers.cols[{i}].items[{j}].k phải thuộc {list(KIND_CLS)}")
        for i, x in enumerate(X.get("dont", [])):
            L(f"levers.dont[{i}]", _txt(x), "levers.dont_item"); L(f"levers.dont[{i}].tip", _tip(x), "tip")
    if P.get("qa"):
        X = P["qa"]
        N("qa.items", X["items"], "qa.items"); L("qa.src", X.get("src"), "src")
        for i, x in enumerate(X["items"]):
            for k in ("q", "a", "ev", "act"):
                L(f"qa.items[{i}].{k}", x[k], f"qa.{k}")
            L(f"qa.items[{i}].tip", x.get("tip"), "tip")
    for k, v in (P.get("guides") or {}).items():
        L(f"guides.{k}", v, "guide")
        if k not in GUIDE:
            err.append(f"guides.{k}: không có slide này")
    for k, v in (P.get("gloss") or {}).items():
        L(f"gloss.{k}", v, "tip")
    for i, x in enumerate(P["plan"]["cards"]):
        L(f"plan.cards[{i}].text", x["text"], "plan.card")
    blob = json.dumps({k: v for k, v in P.items() if k != "kpi"}, ensure_ascii=False)
    for w in ("VNĐ", "VND", "đồng/tháng", "triệu đồng", "giá trị hợp đồng", "thanh toán", "hoa hồng", "@gmail", "TAG "):
        if w in blob:
            err.append(f"chữ cấm ngoài khối kpi: “{w}” (không ghi giá, phí, thanh toán, email cá nhân, TAG)")
    return err


def opt(a, name, default=None):
    """Lấy giá trị của cờ --name <v> và bỏ nó khỏi danh sách đối số."""
    if name in a:
        i = a.index(name)
        v = a[i + 1] if i + 1 < len(a) else default
        del a[i:i + 2]
        return v
    return default


def main():
    global LINK
    a = sys.argv[1:]
    web = "--web" in a
    a = [x for x in a if x != "--web"]
    back = opt(a, "--back")
    LINK = opt(a, "--link", LINK)
    if not a:
        print(__doc__); return
    cmd = a[0]
    if cmd == "check":
        if len(a) < 2:
            sys.exit("check cần ít nhất một file JSON")
        bad = 0
        for s in a[1:]:
            P = json.loads(Path(s).read_text(encoding="utf-8"))
            errs = check(P)
            print(f"{P.get('slug', s)}: {'OK' if not errs else str(len(errs)) + ' lỗi'}")
            for x in errs:
                print("  -", x)
            bad += bool(errs)
            if not errs:  # thử dựng cả bản nội bộ và bản --web
                P = _mark(P); build_project(P, False); build_project(P, True)
        sys.exit(1 if bad else 0)
    elif cmd == "project":
        P = load(a[1]); Path(a[2]).write_text(build_project(P, web, back=back), encoding="utf-8"); print(a[2])
    elif cmd == "overview":
        Path(a[1]).write_text(build_overview(loaded(a[2:]), web), encoding="utf-8"); print(a[1])
    elif cmd == "all":
        Path(a[1]).write_text(build_overview(loaded(a[2:]), web, with_projects=True), encoding="utf-8"); print(a[1])
    else:
        sys.exit(f"lệnh không rõ: {cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
