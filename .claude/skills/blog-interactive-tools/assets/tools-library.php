<?php
/**
 * Mẫu mu-plugin: 8 công cụ tương tác trong thân bài blog. Đổi tiền tố site_ và site- theo site, khớp SC của insert_shortcode.php.
 * Shortcode [site_tool name="serp|kw-group|seo-checklist|swot|fb-cover|faq-schema|fb-ads|alt-text"].
 * - Server in sẵn khung HTML đầy đủ (nhãn, ô nhập, vùng kết quả cố định chiều cao) để không gây CLS và crawler đọc được.
 * - CSS in ở <head>, JS ở cuối trang, chỉ trên bài có shortcode. Vanilla JS, không thư viện, không gọi mạng.
 * - Ngưỡng và công thức lấy theo bài chứa công cụ. Số pixel tiêu đề, mô tả là ước lượng.
 * Script có data-no-optimize, data-no-defer để LiteSpeed không hoãn tới lần chạm đầu. Style có data-no-optimize để LiteSpeed
 * không gộp vào file CSS tổng tải bất đồng bộ: công cụ có style ngay lần vẽ đầu.
 */

defined( 'ABSPATH' ) || exit;

function site_tools_names() {
	return array( 'serp', 'kw-group', 'seo-checklist', 'swot', 'fb-cover', 'faq-schema', 'fb-ads', 'alt-text' );
}

// Tên công cụ có trong nội dung bài đang xem.
function site_tools_on_page() {
	static $names = null;
	if ( null === $names ) {
		$names = array();
		$post  = is_singular() ? get_post() : null;
		if ( $post && false !== strpos( (string) $post->post_content, '[site_tool' ) && preg_match_all( '/\[site_tool\s+name=["\']?([a-z-]+)/', $post->post_content, $m ) ) {
			$names = array_values( array_intersect( site_tools_names(), array_unique( $m[1] ) ) );
		}
	}
	return $names;
}

function site_tools_open( $id, $name, $title, $lead ) {
	return '<section class="site-tool site-tool--' . $name . '" data-tool="' . $name . '" id="' . $id . '" aria-labelledby="' . $id . '-t">'
		. '<p class="site-tool__eye">Công cụ miễn phí của ' . esc_html( get_bloginfo( 'name' ) ) . '</p>'
		. '<p class="site-tool__title" id="' . $id . '-t">' . $title . '</p>'
		. '<p class="site-tool__lead">' . $lead . '</p>';
}

function site_tools_close( $note ) {
	return '<p class="site-tool__foot">' . $note . ' Công cụ chỉ xử lý dữ liệu trên trình duyệt của bạn và không gửi đi đâu.</p></section>';
}

function site_tools_field( $id, $key, $label, $type = 'text', $attrs = '', $hint = '' ) {
	$in = 'textarea' === $type
		? '<textarea id="' . $id . '-' . $key . '" data-k="' . $key . '" ' . $attrs . '></textarea>'
		: '<input type="' . $type . '" id="' . $id . '-' . $key . '" data-k="' . $key . '" autocomplete="off" ' . $attrs . '>';
	return '<div class="site-f"><label for="' . $id . '-' . $key . '">' . $label . '</label>' . $in . ( $hint ? '<p class="site-hint">' . $hint . '</p>' : '' ) . '</div>';
}

function site_tools_out( $h, $empty, $extra = '' ) {
	return '<div class="site-out" style="height:' . $h . 'px" tabindex="0" role="group" aria-label="Kết quả"' . $extra . '><p class="site-sum" data-k="sum" aria-live="polite">' . $empty . '</p><div data-k="res"></div></div>';
}

/* ---------- 1. Xem trước kết quả Google (bài meta-description) ---------- */
function site_tool_html_serp( $id ) {
	$sp = function ( $m ) {
		$s = 'm' === $m ? 'm' : 'd';
		return '<div class="site-sp' . ( 'm' === $m ? ' site-sp--m' : '' ) . '"><div class="site-sp__site"><span class="site-sp__fav" aria-hidden="true"></span><span class="site-sp__id"><span class="site-sp__n" data-k="n' . $s . '">' . esc_html( wp_parse_url( home_url(), PHP_URL_HOST ) ) . '</span><span class="site-sp__u" data-k="u' . $s . '">' . esc_html( home_url() ) . '</span></span></div>'
			. '<p class="site-sp__t" data-k="t' . $s . '">Tiêu đề trang của bạn</p><p class="site-sp__s" data-k="s' . $s . '">Meta description của bạn sẽ hiện ở đây.</p></div>';
	};
	return site_tools_open( $id, 'serp', 'Xem trước kết quả Google', 'Gõ tiêu đề và meta description để xem chúng hiện trên Google ra sao. Lúc mở trang, ô nhập đã có sẵn tiêu đề và mô tả của chính bài này.' )
		. '<div class="site-g2">' . site_tools_field( $id, 'kw', 'Từ khóa chính', 'text', 'placeholder="ví dụ: meta description"', 'Google thường tô đậm phần khớp với truy vấn.' )
		. site_tools_field( $id, 'url', 'Đường dẫn trang', 'text', 'placeholder="https://vi-du.vn/trang-cua-ban/" inputmode="url"' ) . '</div>'
		. '<div class="site-f"><label for="' . $id . '-ti">Tiêu đề (SEO title)</label><input type="text" id="' . $id . '-ti" data-k="ti" autocomplete="off"><div class="site-meter" aria-hidden="true"><span data-k="tb"></span></div><p class="site-hint" data-k="tn">0 ký tự · 0 / 580 px</p></div>'
		. '<div class="site-f"><label for="' . $id . '-de">Meta description</label><textarea id="' . $id . '-de" data-k="de" rows="3"></textarea><div class="site-meter" aria-hidden="true"><span data-k="db"></span></div><p class="site-hint" data-k="dn">0 ký tự · 0 / 920 px</p></div>'
		. '<label class="site-cb"><input type="checkbox" data-k="dt"> Thêm ngày đăng trước mô tả (bài khuyên trừ hao phần này)</label>'
		. '<div class="site-sp__wrap"><p class="site-sp__h">Trên máy tính</p><div class="site-sp__x" tabindex="0" role="group" aria-label="Bản xem trước trên máy tính">' . $sp( 'd' ) . '</div>'
		. '<p class="site-sp__h">Trên điện thoại</p>' . $sp( 'm' ) . '</div>'
		. site_tools_out( 250, 'Nhập tiêu đề và mô tả để kiểm.' )
		. site_tools_close( 'Mốc 150–160 ký tự và 120 ký tự đầu lấy theo bài viết. Mốc 580 px cho tiêu đề và 920 px cho mô tả trên máy tính là mức ước lượng phổ biến, Google không công bố con số chính thức.' );
}

/* ---------- 2. Gom nhóm từ khóa theo SERP (bài nghien-cuu-tu-khoa) ---------- */
function site_tool_html_kw_group( $id ) {
	$ph = "mèo cảnh\nhttps://site-a.vn/meo-canh\nhttps://site-b.vn/giong-meo\n…\n\ngiống mèo tây\nhttps://site-b.vn/giong-meo\n…";
	return site_tools_open( $id, 'kw-group', 'Gom nhóm từ khóa theo SERP trùng nhau', 'Cách làm giống phần thủ công trong bài: tìm từng từ khóa ở tab ẩn danh, chép 10 URL đầu tiên rồi dán vào đây. Hai từ khóa có từ 5 URL trùng nhau sẽ về chung một nhóm.' )
		. site_tools_field( $id, 'in', 'Dữ liệu SERP', 'textarea', 'rows="9" spellcheck="false" placeholder="' . esc_attr( $ph ) . '"', 'Mỗi khối gồm một dòng từ khóa và các dòng URL bên dưới, các khối cách nhau một dòng trống. Công cụ cũng nhận bảng hai cột từ khóa và URL dán từ Excel.' )
		. '<div class="site-row"><div class="site-f site-f--n">' . '<label for="' . $id . '-min">Số URL trùng tối thiểu</label><input type="number" id="' . $id . '-min" data-k="min" value="5" min="1" max="10" inputmode="numeric"></div>'
		. '<button type="button" class="site-btn" data-k="go">Gom nhóm</button><button type="button" class="site-btn site-btn--g" data-k="demo">Điền ví dụ</button></div>'
		. site_tools_out( 340, 'Kết quả gom nhóm sẽ hiện ở đây.' )
		. '<div class="site-row site-row--end"><button type="button" class="site-btn site-btn--g site-cp" data-k="cp">Sao chép</button><button type="button" class="site-btn site-btn--g" data-k="csv">Tải CSV</button></div>'
		. site_tools_close( 'Từ khóa đứng trước được chọn làm từ khóa đầu nhóm (parent keyword), nên hãy đặt từ khóa chủ đề lên đầu. Ví dụ điền sẵn dùng URL giả lập, không phải SERP thật.' );
}

/* ---------- 3. Chấm bài theo checklist (bài cach-viet-bai-chuan-seo) ---------- */
function site_tool_html_seo_checklist( $id ) {
	$manual = array( '1 Nội dung độc đáo, không sao chép', '2 Không lỗi chính tả, ngữ pháp', '3 Định dạng hợp nội dung (danh sách, đoạn văn, bảng)', '4 Có hình ảnh hoặc video liên quan', '9 Độ dài đủ trả lời ý định tìm kiếm', '11 In đậm, in nghiêng đúng chỗ', '12 Blockquote có nguồn', '13 Internal link tới bài liên quan', '14 External link tới nguồn uy tín', '15 Ảnh thumbnail rõ, đúng chủ đề', '18 Có LSI keywords', '19 Có semantic keywords', '20 Câu rõ, cấu trúc H1–H3 mạch lạc', '21 Câu trả lời ngắn ngay dưới heading câu hỏi', '22 Tiêu đề và mô tả gợi tò mò', '23 Nội dung khớp ý định, trang tải nhanh', '24 Có video, infographic hoặc công cụ', '25 CTA rõ, đặt chỗ dễ thấy' );
	$li     = '';
	foreach ( $manual as $i => $m ) {
		list( $n, $t ) = explode( ' ', $m, 2 );
		$li .= '<label class="site-cb"><input type="checkbox" data-m="' . $i . '"> <span>#' . $n . ' ' . $t . '</span></label>';
	}
	return site_tools_open( $id, 'seo-checklist', 'Chấm nhanh bài viết theo checklist', 'Dán tiêu đề, meta description và nội dung bài vào đây. Công cụ tự chấm các mục đo được trong checklist bên dưới, phần còn lại bạn tự đánh dấu.' )
		. '<div class="site-g2">' . site_tools_field( $id, 'kw', 'Từ khóa chính', 'text', 'placeholder="ví dụ: chiến lược seo"' )
		. site_tools_field( $id, 'k2', 'Từ khóa phụ', 'text', 'placeholder="cách nhau bằng dấu phẩy"' ) . '</div>'
		. site_tools_field( $id, 'ti', 'Tiêu đề SEO' )
		. site_tools_field( $id, 'de', 'Meta description', 'textarea', 'rows="2"' )
		. site_tools_field( $id, 'bd', 'Nội dung bài', 'textarea', 'rows="7" spellcheck="false"', 'Dán HTML hoặc văn bản. Nếu dán văn bản, viết heading dạng ## hoặc ###.' )
		. site_tools_out( 400, 'Nhập từ khóa chính và dán bài để chấm.' )
		. '<details class="site-man"><summary data-k="mp">Các mục tự đánh dấu: 0/' . count( $manual ) . '</summary><div class="site-man__l">' . $li . '</div></details>'
		. site_tools_close( 'Số thứ tự (#5, #7…) khớp với mục trong checklist của bài. Mật độ từ khóa chỉ để tham khảo, vì bài khuyên không nhắm một mật độ cố định. Số câu mỗi đoạn là ước tính.' );
}

/* ---------- 4. SWOT và chiến lược S-O, W-O, S-T, W-T (bài swot-la-gi) ---------- */
function site_tool_html_swot( $id ) {
	$q = array(
		's' => array( 'Điểm mạnh (S)', 'Doanh nghiệp có lợi thế nào so với đối thủ?|Nguồn lực hoặc tài sản giá trị nào mà doanh nghiệp sở hữu?|Khách hàng đánh giá cao nhất điều gì?|Đội ngũ có kỹ năng, chuyên môn đặc biệt nào?|Công nghệ, quy trình nào giúp vượt đối thủ?' ),
		'w' => array( 'Điểm yếu (W)', 'Hoạt động nào cần cải thiện?|Doanh nghiệp thiếu nguồn lực, kỹ năng quan trọng nào?|Khách hàng phàn nàn nhiều nhất về điều gì?|Đối thủ có lợi thế nào hơn doanh nghiệp?|Yếu tố nào đang cản trở tăng trưởng?' ),
		'o' => array( 'Cơ hội (O)', 'Có xu hướng thị trường mới nào để tận dụng?|Thay đổi công nghệ nào mở ra cơ hội mới?|Phân khúc khách hàng nào chưa khai thác?|Có thể mở rộng địa lý, thâm nhập thị trường mới không?|Thay đổi pháp luật nào tạo cơ hội?' ),
		't' => array( 'Thách thức (T)', 'Đối thủ đang có động thái gì?|Hành vi khách hàng thay đổi ra sao, có gây bất lợi không?|Rủi ro kinh tế, chính trị, xã hội nào ảnh hưởng?|Thay đổi công nghệ nào đe dọa vị thế hiện tại?|Có thách thức nào về nguồn cung, chi phí nguyên liệu?' ),
	);
	$f = '';
	foreach ( $q as $k => $v ) {
		$f .= '<div class="site-f site-sw__in site-sw__in--' . $k . '"><label for="' . $id . '-' . $k . '">' . $v[0] . '</label><textarea id="' . $id . '-' . $k . '" data-k="' . $k . '" rows="4" placeholder="Mỗi yếu tố một dòng"></textarea>'
			. '<details><summary>Câu hỏi gợi ý</summary><p class="site-hint">' . str_replace( '|', '<br>', $v[1] ) . '</p></details></div>';
	}
	return site_tools_open( $id, 'swot', 'Lập ma trận SWOT và chiến lược S-O, W-O, S-T, W-T', 'Ghi mỗi yếu tố một dòng, đặt dòng quan trọng nhất lên đầu như cách xếp hạng ở Bước 3. Công cụ dựng ma trận và ghép hai yếu tố ưu tiên của mỗi ô thành gợi ý chiến lược.' )
		. site_tools_field( $id, 'goal', 'Mục tiêu phân tích', 'text', 'placeholder="ví dụ: mở thêm kênh bán online trong năm tới"' )
		. '<div class="site-g2">' . $f . '</div>'
		. site_tools_out( 460, 'Ma trận SWOT và gợi ý chiến lược sẽ hiện ở đây.' )
		. '<div class="site-row site-row--end"><button type="button" class="site-btn site-btn--g site-cp" data-k="cp">Sao chép</button><button type="button" class="site-btn site-btn--g" data-k="txt">Tải file .txt</button><button type="button" class="site-btn site-btn--g" data-k="clr">Xoá hết</button></div>'
		. site_tools_close( 'Gợi ý chiến lược là câu ghép từ các yếu tố bạn nhập, bạn cần tự cân nhắc trước khi dùng. Trình duyệt lưu bản nháp để bạn không mất bài khi tải lại trang.' );
}

/* ---------- 5. Xem trước ảnh bìa Facebook (bài kich-thuoc-anh-bia-facebook) ---------- */
function site_tool_html_fb_cover( $id ) {
	$ph = '<span class="site-fc__ph" data-k="ph">Chưa chọn ảnh</span>';
	return site_tools_open( $id, 'fb-cover', 'Xem trước ảnh bìa Facebook trên máy tính và điện thoại', 'Chọn ảnh từ máy để xem phần nào bị cắt trên máy tính và điện thoại. Công cụ cũng kiểm kích thước, tỷ lệ và dung lượng theo mốc trong bài.' )
		. '<label class="site-drop" data-k="drop" for="' . $id . '-file"><span class="site-drop__t">Chọn ảnh bìa (JPG hoặc PNG)</span><span class="site-drop__s">hoặc kéo thả ảnh vào khung này</span>'
		. '<input type="file" id="' . $id . '-file" data-k="file" accept="image/png,image/jpeg,image/webp" class="site-drop__in"></label>'
		. '<div class="site-fc">'
		. '<div class="site-fc__b site-fc__b--d"><p class="site-sp__h">Máy tính · khung 851 × 315</p><div class="site-fc__fr site-fc__fr--d"><div class="site-fc__img" data-k="di"></div>' . $ph . '</div></div>'
		. '<div class="site-fc__b"><p class="site-sp__h">Điện thoại · khung 640 × 360</p><div class="site-fc__fr site-fc__fr--m"><div class="site-fc__img" data-k="mi"></div>' . $ph . '<span class="site-fc__av" aria-hidden="true"></span></div><p class="site-hint">Vòng tròn chỉ minh hoạ chỗ ảnh đại diện che lên ảnh bìa.</p></div>'
		. '<div class="site-fc__b"><p class="site-sp__h">Ảnh gốc · phần hiện trên từng thiết bị</p><div class="site-fc__fr site-fc__fr--s"><div class="site-fc__src" data-k="si"><span class="site-fc__r site-fc__r--d" data-k="rd"></span><span class="site-fc__r site-fc__r--m" data-k="rm"></span><span class="site-fc__r site-fc__r--x" data-k="rx"></span></div>' . $ph . '</div>'
		. '<p class="site-fc__lg"><span class="site-fc__k site-fc__k--d"></span>Máy tính <span class="site-fc__k site-fc__k--m"></span>Điện thoại <span class="site-fc__k site-fc__k--x"></span>Hiện trên cả hai</p></div>'
		. '</div>'
		. site_tools_out( 230, 'Chọn ảnh để kiểm kích thước, tỷ lệ và dung lượng.' )
		. site_tools_close( 'Khung hiển thị, kích thước, tỷ lệ và dung lượng lấy theo số đo trong bài.' );
}

/* ---------- 6. Tạo FAQ Schema JSON-LD (bài faq-la-gi) ---------- */
function site_tool_faq_row( $id, $i ) {
	return '<div class="site-qa"><div class="site-qa__top"><label for="' . $id . '-q' . $i . '">Câu hỏi <span data-no>' . $i . '</span></label><button type="button" class="site-x" data-del aria-label="Xoá câu hỏi ' . $i . '">Xoá</button></div>'
		. '<input type="text" id="' . $id . '-q' . $i . '" data-q autocomplete="off" placeholder="ví dụ: FAQ là gì?">'
		. '<label class="site-lb2" for="' . $id . '-a' . $i . '">Câu trả lời</label><textarea id="' . $id . '-a' . $i . '" data-a rows="3" placeholder="Trả lời ngắn, 2–4 câu"></textarea></div>';
}
function site_tool_html_faq_schema( $id ) {
	return site_tools_open( $id, 'faq-schema', 'Tạo mã FAQ Schema (JSON-LD)', 'Nhập câu hỏi và câu trả lời. Công cụ kiểm độ dài câu trả lời theo mốc 2–4 câu ở phần Lưu ý bên dưới, rồi xuất mã JSON-LD và khung HTML dùng thẻ H3 cho câu hỏi như Bước 4.' )
		. site_tools_field( $id, 'kw', 'Từ khóa chính (không bắt buộc)', 'text', 'placeholder="ví dụ: faq là gì"' )
		. '<div class="site-qas" data-k="rows">' . site_tool_faq_row( $id, 1 ) . site_tool_faq_row( $id, 2 ) . '</div>'
		. '<div class="site-row"><button type="button" class="site-btn site-btn--g" data-k="add">+ Thêm câu hỏi</button></div>'
		. site_tools_out( 170, 'Nhập ít nhất một cặp hỏi đáp.' )
		. '<div class="site-tabs" role="group" aria-label="Chọn loại mã"><button type="button" class="site-tab" data-tab="js" aria-pressed="true">JSON-LD</button><button type="button" class="site-tab" data-tab="html" aria-pressed="false">HTML</button></div>'
		. '<label class="site-sr" for="' . $id . '-js">Mã JSON-LD</label><textarea class="site-code" id="' . $id . '-js" data-k="js" readonly spellcheck="false"></textarea>'
		. '<label class="site-sr" for="' . $id . '-html">Mã HTML</label><textarea class="site-code" id="' . $id . '-html" data-k="html" readonly spellcheck="false" hidden></textarea>'
		. '<div class="site-row site-row--end"><button type="button" class="site-btn site-cp" data-k="cp">Sao chép mã</button></div>'
		. site_tools_close( 'Từ tháng 8/2023, Google chỉ hiện kết quả nhiều định dạng (rich result) dạng FAQ cho một số trang chính phủ và y tế có uy tín (theo Google Search Central). Mã này là dữ liệu có cấu trúc hợp lệ cho phần hỏi đáp.' );
}

/* ---------- 7. Chỉ số quảng cáo Facebook (bài do-luong-hieu-qua-quang-cao-facebook) ---------- */
function site_tool_html_fb_ads( $id ) {
	$f = array(
		'sp' => array( 'Chi tiêu', '7.000.000' ),
		'rs' => array( 'Số kết quả', '10' ),
		'rv' => array( 'Doanh thu', '' ),
		'vl' => array( 'Giá trị mỗi kết quả (không bắt buộc)', '350.000' ),
		'im' => array( 'Lượt hiển thị', '' ),
		'rc' => array( 'Người xem (tiếp cận)', '' ),
		'ck' => array( 'Lượt nhấp vào liên kết', '' ),
	);
	$h = '';
	foreach ( $f as $k => $v ) {
		$h .= '<div class="site-f"><label for="' . $id . '-' . $k . '">' . $v[0] . '</label><input type="text" inputmode="decimal" id="' . $id . '-' . $k . '" data-k="' . $k . '" value="' . $v[1] . '" autocomplete="off"></div>';
	}
	$h .= '<div class="site-f"><label for="' . $id . '-cur">Đơn vị tiền</label><select id="' . $id . '-cur" data-k="cur"><option value="đ">VND (đ)</option><option value="USD">USD</option></select></div>';
	$m = array(
		'cpr'  => array( 'CPR', 'Chi tiêu ÷ Số kết quả', '700.000 đ' ),
		'roas' => array( 'ROAS', 'Doanh thu ÷ Chi tiêu', '–' ),
		'cpm'  => array( 'CPM', 'Chi tiêu ÷ Lượt hiển thị × 1.000', '–' ),
		'fq'   => array( 'Tần suất', 'Lượt hiển thị ÷ Người xem', '–' ),
		'ctr'  => array( 'CTR (liên kết)', 'Lượt nhấp ÷ Lượt hiển thị × 100%', '–' ),
		'cpc'  => array( 'CPC (liên kết)', 'Chi tiêu ÷ Lượt nhấp', '–' ),
	);
	$c = '';
	foreach ( $m as $k => $v ) {
		$c .= '<div class="site-mt"><span class="site-mt__n">' . $v[0] . '</span><span class="site-mt__v" data-k="' . $k . '">' . $v[2] . '</span><span class="site-mt__f">' . $v[1] . '</span></div>';
	}
	return site_tools_open( $id, 'fb-ads', 'Tính nhanh chỉ số quảng cáo Facebook', 'Nhập số liệu lấy từ Trình quản lý quảng cáo. Công cụ tính CPR, ROAS, CPM, tần suất, CTR và CPC theo định nghĩa trong bài. Số điền sẵn là ví dụ CPA 700.000 đ so với giá trị khách hàng 350.000 đ ở mục 2.' )
		. '<div class="site-g2">' . $h . '</div>'
		. '<div class="site-mts">' . $c . '</div>'
		. site_tools_out( 200, 'Nhận xét theo số liệu bạn nhập.' )
		. site_tools_close( 'Mốc tần suất 10 lần và CTR trung bình 0,9% là số liệu bài dẫn, chỉ để tham khảo.' );
}

/* ---------- 8. Kiểm alt text (bài alt-text-la-gi) ---------- */
function site_tool_html_alt_text( $id ) {
	return site_tools_open( $id, 'alt-text', 'Kiểm tra alt text', 'Dán một alt text để kiểm nhanh, hoặc dán HTML của cả trang để rà mọi ảnh cùng lúc.' )
		. site_tools_field( $id, 'in', 'Alt text hoặc HTML', 'textarea', 'rows="4" spellcheck="false" placeholder="ví dụ: Bảng so sánh kích thước ảnh bìa Facebook trên máy tính và điện thoại"' )
		. site_tools_field( $id, 'kw', 'Từ khóa (không bắt buộc)', 'text', 'placeholder="ví dụ: ảnh bìa facebook"' )
		. '<div class="site-meter" aria-hidden="true"><span data-k="bar"></span></div><p class="site-hint" data-k="n">0 / 125 ký tự</p>'
		. site_tools_out( 300, 'Kết quả kiểm tra sẽ hiện ở đây.' )
		. site_tools_close( 'Mốc 125 ký tự và các lỗi được kiểm lấy theo bài viết. Công cụ không tải ảnh trong HTML bạn dán.' );
}

add_shortcode(
	'site_tool',
	function ( $atts ) {
		static $n = 0;
		$a = shortcode_atts( array( 'name' => '' ), $atts, 'site_tool' );
		$f = 'site_tool_html_' . str_replace( '-', '_', (string) $a['name'] );
		if ( is_feed() || ! in_array( $a['name'], site_tools_names(), true ) || ! function_exists( $f ) ) {
			return '';
		}
		++$n;
		return $f( 'sitet' . $n );
	}
);

/* ---------- CSS ---------- */
function site_tools_css( $name ) {
	$css = array(
		'base'          => <<<'CSS'
html body .site-tool{--gi:#030815;--gm:#475569;--gl:#E2E8F0;--gb:#F8FAFC;position:relative;display:block;margin:36px 0;padding:24px 24px 20px;border:1px solid var(--gl);border-radius:16px;background:#fff;color:var(--gi);font:400 15px/1.6 Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;text-align:left;box-shadow:0 1px 2px rgba(3,8,21,.04),0 12px 32px -18px rgba(3,8,21,.2);overflow:hidden}
html body .site-tool::before{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:linear-gradient(90deg,#0693E3,#9900EF)}
html body .site-tool *,html body .site-tool *::before,html body .site-tool *::after{box-sizing:border-box}
html body .site-tool p{margin:0;padding:0;font-size:inherit;line-height:inherit;color:inherit}
html body .site-tool .site-tool__eye{display:flex;align-items:center;gap:8px;margin:0 0 6px;font:600 12px/1.4 Inter,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--gm)}
html body .site-tool .site-tool__eye::before{content:"";flex:none;width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0693E3,#9900EF)}
html body .site-tool .site-tool__title{margin:0 0 6px;font:700 21px/1.3 Montserrat,Inter,system-ui,sans-serif;letter-spacing:-.01em;color:var(--gi)}
html body .site-tool .site-tool__lead{margin:0 0 18px;color:var(--gm)}
html body .site-tool .site-f{margin:0 0 14px;min-width:0}
html body .site-tool label,html body .site-tool .site-lb2{display:block;margin:0 0 6px;padding:0;font:600 14px/1.4 Inter,system-ui,sans-serif;color:var(--gi);text-transform:none;letter-spacing:0}
html body .site-tool :is(input[type=text],input[type=number],textarea,select){display:block;width:100%;max-width:100%;height:auto;min-height:44px;margin:0;padding:10px 12px;border:1px solid #7A869A;border-radius:10px;background:#fff;color:var(--gi);font:400 15px/1.5 Inter,system-ui,sans-serif;box-shadow:none;outline:0;-webkit-appearance:none;appearance:none}
html body .site-tool textarea{min-height:88px;resize:vertical}
html body .site-tool select{padding-right:36px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%23475569' stroke-width='2'/%3E%3C/svg%3E") no-repeat right 14px center}
html body .site-tool :is(input,textarea,select):focus{border-color:#0567A8;box-shadow:0 0 0 3px rgba(6,147,227,.3)}
html body .site-tool ::placeholder{color:#64748B;opacity:1}
html body .site-tool .site-btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;width:auto;min-height:44px;margin:0;padding:10px 18px;border:1px solid transparent;border-radius:10px;background:linear-gradient(135deg,#0567A8,#8200CC);color:#fff;font:600 14px/1.2 Inter,system-ui,sans-serif;text-transform:none;letter-spacing:0;text-decoration:none;white-space:nowrap;cursor:pointer;box-shadow:none;transition:filter .15s}
html body .site-tool .site-btn:is(:hover,:focus,:active){background:linear-gradient(135deg,#0567A8,#8200CC);color:#fff;filter:brightness(1.12)}
html body .site-tool .site-btn--g,html body .site-tool .site-btn--g:is(:hover,:focus,:active){background:#fff;color:var(--gi);border-color:#7A869A;filter:none}
html body .site-tool .site-btn--g:hover{background:#F1F5F9}
html body .site-tool .site-cp{min-width:132px}
html body .site-tool :is(.site-btn,.site-x,.site-tab,input,textarea,select,summary,.site-out,.site-sp__x):focus-visible{outline:3px solid #0567A8;outline-offset:2px}
html body .site-tool .site-row{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin:0 0 4px}
html body .site-tool .site-row--end{margin:12px 0 0}
html body .site-tool .site-g2{display:grid;grid-template-columns:minmax(0,1fr);gap:0 16px}
@media (min-width:640px){html body .site-tool .site-g2{grid-template-columns:repeat(2,minmax(0,1fr))}}
html body .site-tool .site-out{position:relative;margin:16px 0 0;padding:14px 16px;border:1px solid var(--gl);border-radius:12px;background:var(--gb);overflow:auto;overscroll-behavior:contain}
html body .site-tool .site-sum{min-height:24px;margin:0 0 6px;font-weight:600;color:var(--gi)}
html body .site-tool .site-chk{display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-top:1px solid var(--gl);font-size:14px;line-height:1.5}
html body .site-tool .site-chk:first-child{border-top:0}
html body .site-tool .site-chk b{display:block;font-weight:600;color:var(--gi)}
html body .site-tool .site-chk i{display:block;font-style:normal;color:var(--gm);overflow-wrap:anywhere}
html body .site-tool .site-st{flex:none;display:inline-block;min-width:74px;margin-top:1px;padding:1px 8px;border-radius:999px;font:600 12px/1.6 Inter,system-ui,sans-serif;text-align:center}
html body .site-tool .site-st--ok{background:#DCFCE7;color:#065F46}
html body .site-tool .site-st--wa{background:#FEF3C7;color:#92400E}
html body .site-tool .site-st--er{background:#FEE2E2;color:#991B1B}
html body .site-tool .site-st--in{background:#E0F2FE;color:#075985}
html body .site-tool .site-hint{margin:6px 0 0;font-size:13px;line-height:1.5;color:var(--gm)}
html body .site-tool .site-cb{display:flex;gap:8px;align-items:flex-start;margin:0 0 8px;font-weight:400;font-size:14px;cursor:pointer}
html body .site-tool .site-cb input{flex:none;width:18px;height:18px;min-height:0;margin:2px 0 0;accent-color:#0567A8}
html body .site-tool .site-meter{position:relative;height:6px;margin:8px 0 0;border-radius:99px;background:var(--gl);overflow:hidden}
html body .site-tool .site-meter span{position:absolute;left:0;top:0;bottom:0;width:0;border-radius:99px;background:linear-gradient(90deg,#0693E3,#9900EF);transition:width .2s}
html body .site-tool .site-meter span.is-over{background:#DC2626}
html body .site-tool details{margin:6px 0 0}
html body .site-tool summary{cursor:pointer;font-size:13px;font-weight:600;color:#0567A8}
html body .site-tool .site-tool__foot{margin:16px 0 0;padding:12px 0 0;border-top:1px dashed var(--gl);font-size:13px;line-height:1.55;color:var(--gm)}
html body .site-tool .site-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
html body .site-tool .site-sp__h{margin:0 0 8px;font:600 12px/1.4 Inter,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--gm)}
@media (max-width:480px){html body .site-tool{margin:28px 0;padding:20px 16px 16px;border-radius:14px}html body .site-tool .site-tool__title{font-size:19px}html body .site-tool .site-btn{flex:1 1 auto}html body .site-tool :is(input[type=text],input[type=number],textarea,select){font-size:16px}}
@media (prefers-reduced-motion:reduce){html body .site-tool *{transition:none!important}}
CSS
		,
		'serp'          => <<<'CSS'
html body .site-tool .site-sp__wrap{margin:18px 0 0}
html body .site-tool .site-sp__x{overflow-x:auto;margin:0 0 14px;padding:0 0 4px}
html body .site-tool .site-sp{width:600px;padding:14px 16px;border:1px solid var(--gl);border-radius:12px;background:#fff;font-family:Arial,sans-serif}
html body .site-tool .site-sp--m{width:auto;max-width:380px;border-radius:16px}
html body .site-tool .site-sp__site{display:flex;align-items:center;gap:10px;height:32px;margin:0 0 6px}
html body .site-tool .site-sp__fav{flex:none;width:28px;height:28px;border:1px solid #DADCE0;border-radius:50%;background:radial-gradient(circle,#9900EF 0 5px,transparent 6px),#F1F3F4}
html body .site-tool .site-sp__id{min-width:0}
html body .site-tool .site-sp__n{display:block;font:400 14px/18px Arial,sans-serif;color:#202124;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .site-tool .site-sp__u{display:block;font:400 12px/16px Arial,sans-serif;color:#4D5156;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .site-tool .site-sp__t{height:26px;margin:0 0 4px;font:400 20px/26px Arial,sans-serif;color:#1A0DAB;white-space:nowrap;overflow:hidden}
html body .site-tool .site-sp__s{height:44px;font:400 14px/22px Arial,sans-serif;color:#4D5156;overflow:hidden;overflow-wrap:anywhere}
html body .site-tool .site-sp__s b{font-weight:700;color:#202124}
html body .site-tool .site-sp__s em{font-style:normal;color:#70757A}
html body .site-tool .site-sp--m .site-sp__t{height:48px;font-size:18px;line-height:24px;white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
html body .site-tool .site-sp--m .site-sp__s{height:66px}
CSS
		,
		'kw-group'      => <<<'CSS'
html body .site-tool .site-f--n{width:190px;margin:0}
html body .site-tool .site-kg{margin:10px 0 0;padding:12px 14px;border:1px solid var(--gl);border-radius:10px;background:#fff}
html body .site-tool .site-kg__h{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline;font-weight:700;color:var(--gi)}
html body .site-tool .site-kg__h small{font-weight:400;font-size:13px;color:var(--gm)}
html body .site-tool .site-kg__c{display:flex;justify-content:space-between;gap:10px;padding:6px 0 0;font-size:14px}
html body .site-tool .site-kg__c span:last-child{flex:none;color:#065F46;font-weight:600}
CSS
		,
		'seo-checklist' => <<<'CSS'
html body .site-tool .site-man{margin:14px 0 0;padding:12px 14px;border:1px solid var(--gl);border-radius:12px}
html body .site-tool .site-man summary{font-size:14px}
html body .site-tool .site-man__l{display:grid;grid-template-columns:minmax(0,1fr);gap:2px 16px;margin:12px 0 0}
@media (min-width:640px){html body .site-tool .site-man__l{grid-template-columns:repeat(2,minmax(0,1fr))}}
CSS
		,
		'swot'          => <<<'CSS'
html body .site-tool .site-sw__in label{display:flex;align-items:center;gap:8px}
html body .site-tool .site-sw__in label::before{content:"";flex:none;width:10px;height:10px;border-radius:3px;background:var(--c)}
html body .site-tool .site-sw__in--s,html body .site-tool .site-sw--s{--c:#047857}
html body .site-tool .site-sw__in--w,html body .site-tool .site-sw--w{--c:#B45309}
html body .site-tool .site-sw__in--o,html body .site-tool .site-sw--o{--c:#0567A8}
html body .site-tool .site-sw__in--t,html body .site-tool .site-sw--t{--c:#B91C1C}
html body .site-tool .site-swm{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;margin:10px 0 0}
@media (min-width:560px){html body .site-tool .site-swm{grid-template-columns:repeat(2,minmax(0,1fr))}}
html body .site-tool .site-swm>div{padding:12px 14px;border:1px solid var(--gl);border-top:3px solid var(--c,#0567A8);border-radius:10px;background:#fff;font-size:14px;line-height:1.5}
html body .site-tool .site-swm b{display:block;margin:0 0 4px}
html body .site-tool .site-swm small{display:block;margin:0 0 6px;font-size:12px;color:var(--gm)}
html body .site-tool .site-swm p{margin:0 0 4px;overflow-wrap:anywhere}
html body .site-tool .site-swm .site-sw--x{--c:#8200CC}
CSS
		,
		'fb-cover'      => <<<'CSS'
html body .site-tool .site-drop{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:96px;margin:0 0 16px;padding:16px;border:2px dashed #7A869A;border-radius:12px;background:var(--gb);text-align:center;cursor:pointer}
html body .site-tool .site-drop:is(:hover,.is-over){border-color:#0567A8;background:#EFF6FF}
html body .site-tool .site-drop:focus-within{outline:3px solid #0567A8;outline-offset:2px}
html body .site-tool .site-drop__t{font-weight:700;color:var(--gi)}
html body .site-tool .site-drop__s{font-weight:400;font-size:13px;color:var(--gm)}
html body .site-tool .site-drop__in{position:absolute;inset:0;width:100%;height:100%;min-height:0;opacity:0;cursor:pointer}
html body .site-tool .site-fc{display:grid;grid-template-columns:minmax(0,1fr);gap:16px}
@media (min-width:640px){html body .site-tool .site-fc{grid-template-columns:repeat(2,minmax(0,1fr))}html body .site-tool .site-fc__b--d{grid-column:1/-1}}
html body .site-tool .site-fc__fr{position:relative;overflow:hidden;border-radius:10px;background:repeating-linear-gradient(45deg,#EEF2F7 0 12px,#E2E8F0 12px 24px)}
html body .site-tool .site-fc__fr--d{aspect-ratio:851/315}
html body .site-tool .site-fc__fr--m{aspect-ratio:640/360}
html body .site-tool .site-fc__fr--s{aspect-ratio:2/1;background:#0F172A}
html body .site-tool .site-fc__img{position:absolute;inset:0;background:center/cover no-repeat}
html body .site-tool .site-fc__ph{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:var(--gm)}
html body .site-tool .site-fc__fr--s .site-fc__ph{color:#CBD5E1}
html body .site-tool .site-fc__av{position:absolute;left:5%;bottom:-14%;width:30%;aspect-ratio:1;border:3px solid #fff;border-radius:50%;background:rgba(15,23,42,.55)}
html body .site-tool .site-fc__src{position:absolute;visibility:hidden;background:center/100% 100% no-repeat}
html body .site-tool .site-fc__r{position:absolute;border:2px solid var(--c)}
html body .site-tool .site-fc__r--d,html body .site-tool .site-fc__k--d{--c:#38BDF8}
html body .site-tool .site-fc__r--m,html body .site-tool .site-fc__k--m{--c:#E879F9}
html body .site-tool .site-fc__r--x,html body .site-tool .site-fc__k--x{--c:#4ADE80}
html body .site-tool .site-fc__r--x{border-style:dashed;border-width:3px;background:rgba(74,222,128,.12)}
html body .site-tool .site-fc__lg{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;margin:8px 0 0;font-size:13px;color:var(--gm)}
html body .site-tool .site-fc__k{display:inline-block;width:14px;height:10px;border:2px solid var(--c);border-radius:2px;background:#0F172A}
CSS
		,
		'faq-schema'    => <<<'CSS'
html body .site-tool .site-qa{margin:0 0 12px;padding:12px 14px;border:1px solid var(--gl);border-radius:12px;background:var(--gb)}
html body .site-tool .site-qa__top{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:0 0 6px}
html body .site-tool .site-qa__top label{margin:0}
html body .site-tool .site-qa .site-lb2{margin:10px 0 6px}
html body .site-tool .site-x{display:inline-flex;align-items:center;min-height:32px;margin:0;padding:4px 10px;border:1px solid transparent;border-radius:8px;background:transparent;color:#991B1B;font:600 13px/1.2 Inter,system-ui,sans-serif;text-transform:none;box-shadow:none;cursor:pointer}
html body .site-tool .site-x:is(:hover,:focus,:active){background:#FEE2E2;color:#991B1B}
html body .site-tool .site-tabs{display:flex;gap:6px;margin:16px 0 8px}
html body .site-tool .site-tab{min-height:38px;margin:0;padding:6px 14px;border:1px solid #7A869A;border-radius:999px;background:#fff;color:var(--gi);font:600 13px/1.2 Inter,system-ui,sans-serif;text-transform:none;box-shadow:none;cursor:pointer}
html body .site-tool .site-tab:is(:hover,:focus,:active){background:#F1F5F9;color:var(--gi)}
html body .site-tool .site-tab[aria-pressed=true],html body .site-tool .site-tab[aria-pressed=true]:is(:hover,:focus){background:#030815;border-color:#030815;color:#fff}
html body .site-tool textarea.site-code{height:220px;min-height:220px;resize:none;background:#0F172A;border-color:#0F172A;color:#E2E8F0;font:400 13px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre;overflow:auto}
html body .site-tool textarea.site-code[hidden]{display:none}
CSS
		,
		'fb-ads'        => <<<'CSS'
html body .site-tool .site-mts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:4px 0 0}
@media (min-width:640px){html body .site-tool .site-mts{grid-template-columns:repeat(3,minmax(0,1fr))}}
html body .site-tool .site-mt{display:flex;flex-direction:column;justify-content:space-between;height:112px;padding:12px 14px;border:1px solid var(--gl);border-radius:12px;background:#fff}
html body .site-tool .site-mt__n{font-size:13px;font-weight:600;color:var(--gm)}
html body .site-tool .site-mt__v{font:700 20px/1.25 Montserrat,Inter,system-ui,sans-serif;color:var(--gi);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .site-tool .site-mt__f{font-size:12px;line-height:1.35;color:var(--gm)}
CSS
		,
		'alt-text'      => <<<'CSS'
html body .site-tool .site-im{font-size:13px;color:var(--gm);overflow-wrap:anywhere}
CSS
		,
	);
	return $css[ $name ] ?? '';
}

/* ---------- JS ---------- */
function site_tools_js( $name ) {
	$js = array(
		'base'          => <<<'JS'
var D=document,T={},ST={ok:'Đạt',wa:'Xem lại',er:'Chưa đạt',in:'Thông tin'};
function $(r,k){return r.querySelector('[data-k="'+k+'"]')}
function E(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return'&#'+c.charCodeAt(0)+';'})}
function N(s){return String(s||'').normalize('NFC').toLowerCase().replace(/\s+/g,' ').trim()}
function rx(n){return new RegExp('(^|[^\\p{L}\\p{N}])('+n.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')(?=$|[^\\p{L}\\p{N}])','giu')}
function cnt(h,n){n=N(n);if(!n)return 0;var m=N(h).match(rx(n));return m?m.length:0}
function pos(h,n){n=N(n);if(!n)return -1;var m=rx(n).exec(N(h));return m?m.index+m[1].length:-1}
function db(f,ms){var t;return function(){clearTimeout(t);t=setTimeout(f,ms||180)}}
function R(r,C,head){var ok=0,n=0,h=C.map(function(c){if(c[0]!='in')n++;if(c[0]=='ok')ok++;return'<div class="site-chk"><span class="site-st site-st--'+c[0]+'">'+ST[c[0]]+'</span><div><b>'+c[1]+'</b>'+(c[2]?'<i>'+c[2]+'</i>':'')+'</div></div>'}).join('');$(r,'res').innerHTML=h;$(r,'sum').textContent=head!=null?head:(n?'Đạt '+ok+'/'+n+' mục.':'')}
function cp(t,b){var o=b.textContent;function ok(){b.textContent='Đã sao chép';setTimeout(function(){b.textContent=o},1600)}function fb(){var a=D.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;opacity:0';D.body.appendChild(a);a.select();try{D.execCommand('copy');ok()}catch(e){}a.remove()}if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(ok,fb);else fb()}
function dl(n,t,m){var u=URL.createObjectURL(new Blob(['﻿'+t],{type:(m||'text/plain')+';charset=utf-8'})),a=D.createElement('a');a.href=u;a.download=n;D.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},4000)}
function num(s){s=String(s||'').replace(/[\s₫đ$%]/gi,'');if(!s)return NaN;if(/,\d{1,2}$/.test(s))s=s.replace(/\./g,'').replace(',','.');else{s=s.replace(/,/g,'');if(/^\d{1,3}(\.\d{3})+$/.test(s))s=s.replace(/\./g,'')}return parseFloat(s)}
function F(n,d){return isFinite(n)?n.toLocaleString('vi-VN',{maximumFractionDigits:d==null?2:d}):'–'}
function sc(s){return(String(s).match(/[^.!?…]+(?:[.!?…]+|$)/g)||[]).filter(function(x){return x.trim().length>1}).length}
JS
		,
		'serp'          => <<<'JS'
T.serp=function(r){var g=function(k){return $(r,k)},kw=g('kw'),ti=g('ti'),de=g('de'),ur=g('url'),dt=g('dt'),cx=D.createElement('canvas').getContext('2d'),FT='20px Arial',FS='14px Arial',d=new Date(),DS=d.getDate()+' thg '+(d.getMonth()+1)+', '+d.getFullYear()+' — ';
function px(s,f){cx.font=f;return cx.measureText(s).width}
function cut(s,l,f){if(px(s,f)<=l)return s;var a=0,b=s.length;while(a<b){var m=(a+b+1)>>1;if(px(s.slice(0,m)+' ...',f)<=l)a=m;else b=m-1}var t=s.slice(0,a),p=t.lastIndexOf(' ');if(p>a*.6)t=t.slice(0,p);return t.replace(/[\s,.;:–-]+$/,'')+' ...'}
function hl(s,k){s=E(s);return k?s.replace(rx(E(k)),'$1<b>$2</b>'):s}
function up(){var k=N(kw.value),t=ti.value.trim(),s=de.value.trim().replace(/\s+/g,' '),dp=dt.checked?DS:'',u=ur.value.trim()||location.origin+location.pathname,h=u,p=[];
try{var U=new URL(/^https?:/i.test(u)?u:'https://'+u);h=U.hostname.replace(/^www\./,'');p=U.pathname.split('/').filter(Boolean)}catch(e){}
var cr='https://'+h+(p.length?' › '+p.join(' › '):'');g('nd').textContent=g('nm').textContent=h;g('ud').textContent=g('um').textContent=cr;
var tw=px(t,FT),sw=px(dp+s,FS),ds=cut(dp+s,920,FS).slice(dp.length),ms=s.length>120?s.slice(0,120).replace(/\s+\S*$/,'')+' ...':s;
g('td').textContent=cut(t||'Tiêu đề trang của bạn',580,FT);g('tm').textContent=t||'Tiêu đề trang của bạn';
var pre=dp?'<em>'+E(dp)+'</em>':'';g('sd').innerHTML=pre+hl(ds,k);g('sm').innerHTML=pre+hl(ms,k);
var b1=g('tb'),b2=g('db');b1.style.width=Math.min(100,tw/5.8)+'%';b1.classList.toggle('is-over',tw>580);b2.style.width=Math.min(100,sw/9.2)+'%';b2.classList.toggle('is-over',sw>920);
g('tn').textContent=t.length+' ký tự · '+Math.round(tw)+' / 580 px';g('dn').textContent=s.length+' ký tự · '+Math.round(sw)+' / 920 px';
if(!t&&!s){R(r,[],'Nhập tiêu đề và mô tả để kiểm.');return}
var C=[],L=s.length;C.push(L>=150&&L<=160?['ok','Mô tả dài '+L+' ký tự','Nằm trong mốc 150–160 ký tự bài khuyên.']:['wa','Mô tả dài '+L+' ký tự',L<150?'Ngắn hơn mốc 150–160 ký tự, còn chỗ để thêm thông tin hữu ích.':'Dài hơn 160 ký tự, phần cuối dễ bị cắt.']);
C.push(tw<=580?['ok','Tiêu đề hiện đủ trên máy tính',Math.round(tw)+' / 580 px.']:['wa','Tiêu đề có thể bị cắt','Vượt mốc 580 px khoảng '+Math.round(tw-580)+' px.']);
C.push(sw<=920?['ok','Mô tả hiện đủ trên máy tính',Math.round(sw)+' / 920 px'+(dp?', đã tính cả ngày đăng.':'.')]:['wa','Mô tả có thể bị cắt','Vượt mốc 920 px khoảng '+Math.round(sw-920)+' px'+(dp?', đã tính cả ngày đăng.':'.')]);
C.push(/["“”]/.test(s)?['wa','Mô tả có dấu ngoặc kép','Bài khuyên không dùng dấu ngoặc kép trong meta description.']:['ok','Không có dấu ngoặc kép','']);
if(k){var i=pos(s,k);C.push(cnt(t,k)?['ok','Tiêu đề có từ khóa chính','']:['wa','Tiêu đề chưa có từ khóa chính','']);
C.push(i<0?['wa','Mô tả chưa có từ khóa chính','Thêm từ khóa để Google có phần tô đậm.']:i+k.length<=120?['ok','Từ khóa nằm trong 120 ký tự đầu','Ý chính hiện đủ trên điện thoại.']:['wa','Từ khóa nằm sau 120 ký tự đầu','Đưa ý chính lên trước để không bị cắt trên điện thoại.'])}
else C.push(['in','Chưa nhập từ khóa chính','Nhập từ khóa để kiểm vị trí và phần tô đậm.']);R(r,C)}
if(!ti.value)ti.value=D.title;var m=D.querySelector('meta[name="description"]');if(m&&!de.value)de.value=m.content;ur.placeholder=location.origin+location.pathname;
[kw,ti,de,ur].forEach(function(e){e.addEventListener('input',db(up,120))});dt.addEventListener('change',up);up()};
JS
		,
		'kw-group'      => <<<'JS'
T['kw-group']=function(r){var ta=$(r,'in'),mn=$(r,'min'),G=[];
function nu(u){return u.trim().replace(/^https?:\/\//i,'').replace(/^www\./i,'').replace(/[#?].*$/,'').replace(/\/+$/,'').toLowerCase()}
function isU(s){return/^(https?:\/\/|www\.)\S+$|^[a-z0-9-]+(\.[a-z0-9-]+)+\/\S*$/i.test(s.trim())}
function parse(t){var ks=[],mp={},cur=null;function add(k,u){var x=N(k);if(!x)return;if(!mp[x]){mp[x]={k:k.trim(),u:[]};ks.push(mp[x])}if(u){u=nu(u);if(mp[x].u.indexOf(u)<0&&mp[x].u.length<10)mp[x].u.push(u)}}
t.split(/\r?\n/).forEach(function(l){l=l.trim();if(!l){cur=null;return}var c=l.split(l.indexOf('\t')>-1?'\t':/[;,]/);
if(c.length>1&&!isU(c[0])){var u=c.filter(isU)[0];if(u){add(c[0],u);cur=null;return}}if(isU(l)){if(cur)add(cur,l)}else{cur=l;add(l)}});return ks}
function run(){var n=Math.max(1,Math.min(10,parseInt(mn.value,10)||5)),ks=parse(ta.value);G=[];
ks.forEach(function(k){var b=null,bo=0;G.forEach(function(g){var o=k.u.filter(function(u){return g.h.u.indexOf(u)>-1}).length;if(o>bo){bo=o;b=g}});if(b&&bo>=n)b.c.push([k,bo]);else G.push({h:k,c:[]})});
if(!ks.length){R(r,[],'Chưa có từ khóa nào. Dán dữ liệu SERP rồi bấm Gom nhóm.');return}
var few=ks.filter(function(k){return k.u.length<n}).map(function(k){return E(k.k)+' ('+k.u.length+' URL)'});
$(r,'res').innerHTML=G.map(function(g,i){return'<div class="site-kg"><div class="site-kg__h">Nhóm '+(i+1)+': '+E(g.h.k)+'<small>từ khóa đầu nhóm · '+g.h.u.length+' URL</small></div>'+g.c.map(function(c){return'<div class="site-kg__c"><span>'+E(c[0].k)+'</span><span>trùng '+c[1]+'/'+Math.min(g.h.u.length,c[0].u.length)+' URL</span></div>'}).join('')+'</div>'}).join('')+(few.length?'<div class="site-chk"><span class="site-st site-st--wa">Xem lại</span><div><b>Từ khóa có ít hơn '+n+' URL</b><i>'+few.join(', ')+'</i></div></div>':'');
$(r,'sum').textContent=ks.length+' từ khóa, gom thành '+G.length+' nhóm (mốc '+n+' URL trùng).'}
function rows(){var o=[['Nhóm','Từ khóa','Vai trò','URL trùng với từ khóa đầu nhóm']];G.forEach(function(g,i){o.push([i+1,g.h.k,'Đầu nhóm','']);g.c.forEach(function(c){o.push([i+1,c[0].k,'Thành viên',c[1]])})});return o}
$(r,'go').addEventListener('click',run);mn.addEventListener('change',function(){if(G.length)run()});
$(r,'demo').addEventListener('click',function(){var a='https://site-',L=function(k,s){return k+'\n'+s.split(' ').map(function(x){return a+x+'.vn/'+(x<'f'?'giong-meo-canh':'nuoi-meo')}).join('\n')};
ta.value=[L('mèo cảnh','a b c d e f g h'),L('giống mèo tây','a b c d e k l m'),L('giống mèo cảnh đẹp','b c d e a n p q'),L('cách nuôi mèo con','f g h r s t u v')].join('\n\n');run()});
$(r,'cp').addEventListener('click',function(){if(!G.length)run();cp(rows().map(function(x){return x.join('\t')}).join('\n'),this)});
$(r,'csv').addEventListener('click',function(){if(!G.length)run();if(G.length)dl('gom-nhom-tu-khoa.csv',rows().map(function(x){return x.map(function(v){return'"'+String(v).replace(/"/g,'""')+'"'}).join(',')}).join('\r\n'),'text/csv')})};
JS
		,
		'seo-checklist' => <<<'JS'
T['seo-checklist']=function(r){var g=function(k){return $(r,k)},kw=g('kw'),k2=g('k2'),ti=g('ti'),de=g('de'),bd=g('bd'),mb=r.querySelectorAll('[data-m]'),mp=g('mp');
function parse(t){if(!t.trim())return null;var o={h:[],p:[],img:[],a:-1,x:''};
if(/<[a-z][\s\S]*>/i.test(t)){var d=new DOMParser().parseFromString(t,'text/html');d.querySelectorAll('script,style,noscript').forEach(function(e){e.remove()});
d.querySelectorAll('h1,h2,h3,h4').forEach(function(e){o.h.push([+e.tagName[1],e.textContent.trim()])});d.querySelectorAll('p').forEach(function(e){var s=e.textContent.trim();if(s)o.p.push(s)});
d.querySelectorAll('img').forEach(function(e){o.img.push(e.hasAttribute('alt')?e.getAttribute('alt').trim():null)});o.a=d.querySelectorAll('a[href]').length;o.x=d.body.textContent}
else{o.x=t;t.split(/\n\s*\n/).forEach(function(b){var f=[];b.split('\n').forEach(function(l){var m=l.match(/^(#{1,4})\s+(.+)/);if(m){if(f.length)o.p.push(f.join(' '));f=[];o.h.push([m[1].length,m[2].trim()])}else if(l.trim())f.push(l.trim())});if(f.length)o.p.push(f.join(' '))})}return o}
function up(){var k=N(kw.value),K=k2.value.split(/[,;\n]/).map(N).filter(Boolean),t=ti.value.trim(),m=de.value.trim(),o=parse(bd.value),C=[];
if(!k){R(r,[],'Nhập từ khóa chính để bắt đầu chấm.');return}
var tl=t.length;if(t){C.push(tl>=55&&tl<=65?['ok','#5 Tiêu đề dài '+tl+' ký tự','Trong mốc 55–65 ký tự.']:['wa','#5 Tiêu đề dài '+tl+' ký tự','Bài khuyên 55–65 ký tự.']);
var i=pos(t,k),w=i<0?0:N(t).slice(0,i).split(' ').filter(Boolean).length,c=cnt(t,k);
C.push(i<0?['er','#5 Tiêu đề chưa có từ khóa chính','']:w<=2?['ok','#5 Từ khóa chính đứng đầu tiêu đề','Có '+w+' từ đứng trước, trong mốc không quá 2 từ.']:['wa','#5 Từ khóa chính đứng hơi xa','Có '+w+' từ đứng trước. Bài khuyên cách không quá 2 từ tính từ bên trái.']);
if(c>2)C.push(['wa','#5 Từ khóa lặp '+c+' lần trong tiêu đề','Bài khuyên không lặp quá 2 lần.'])}else C.push(['in','#5 Chưa nhập tiêu đề','']);
if(m){var ml=m.length,f1=m.split(/[.!?](\s|$)/)[0],mc=cnt(m,k);C.push(ml>=150&&ml<=160?['ok','#7 Meta description dài '+ml+' ký tự','Trong mốc 150–160 ký tự.']:['wa','#7 Meta description dài '+ml+' ký tự','Bài khuyên 150–160 ký tự.']);
C.push(!mc?['er','#7 Meta chưa có từ khóa chính','']:cnt(f1,k)&&mc<=3?['ok','#7 Từ khóa chính ở câu đầu của meta','Xuất hiện '+mc+' lần, không quá 3 lần.']:['wa','#7 Xem lại từ khóa chính trong meta',mc>3?'Lặp '+mc+' lần, bài khuyên không quá 3 lần.':'Nên đưa từ khóa vào câu đầu.']);
if(K.length)C.push(K.some(function(x){return cnt(m,x)})?['ok','#7 Meta có từ khóa phụ','']:['wa','#7 Meta chưa có từ khóa phụ',''])}else C.push(['in','#7 Chưa nhập meta description','']);
if(o){var hs=o.h.filter(function(h){return h[0]>1});if(!K.length)C.push(['in','#6 Nhập từ khóa phụ để kiểm heading','']);else if(!hs.length)C.push(['wa','#6 Chưa thấy heading H2–H4','Dán HTML có thẻ heading hoặc viết ## trước heading.']);
else{var hk=hs.filter(function(h){return K.some(function(x){return cnt(h[1],x)})}).length;C.push(hk?['ok','#6 Heading có từ khóa phụ',hk+'/'+hs.length+' heading H2–H4 chứa từ khóa phụ.']:['wa','#6 Chưa heading nào chứa từ khóa phụ',hs.length+' heading H2–H4.'])}
var P=o.p;if(P.length){C.push(cnt(P[0],k)?['ok','#8 Đoạn mở đầu có từ khóa chính','']:['wa','#8 Đoạn mở đầu chưa có từ khóa chính','']);C.push(cnt(P[P.length-1],k)?['ok','#8 Đoạn kết có từ khóa chính','']:['wa','#8 Đoạn kết chưa có từ khóa chính',''])}
var lp=P.filter(function(p){return sc(p)>4}).length;C.push(lp?['wa','#10 '+lp+' đoạn dài hơn 4 câu','Bài khuyên đoạn văn ngắn 3–4 câu.']:['ok','#10 Đoạn văn ngắn','Không đoạn nào dài hơn 4 câu.']);
if(o.img.length){var na=o.img.filter(function(a){return!a}).length,la=o.img.filter(function(a){return a&&a.length>125}).length;C.push(na||la?['wa','#16 Alt ảnh cần sửa',(na?na+' ảnh thiếu alt. ':'')+(la?la+' alt dài hơn 125 ký tự.':'')]:['ok','#16 Alt ảnh đạt',o.img.length+' ảnh có alt, không quá 125 ký tự.'])}
var wc=(o.x.trim().match(/\S+/g)||[]).length;C.push(['in','#17 Từ khóa chính xuất hiện '+cnt(o.x,k)+' lần trong khoảng '+F(wc,0)+' từ','Chỉ để tham khảo. Hãy viết tự nhiên.']);
if(o.a>-1)C.push(['in','#13, #14 Bài có '+o.a+' liên kết','Kiểm tra lại link nội bộ và nguồn ngoài uy tín.'])}else C.push(['in','#6, #8, #10, #16 Dán nội dung bài để kiểm thêm','']);R(r,C)}
function mu(){var n=0;mb.forEach(function(b){if(b.checked)n++});mp.textContent='Các mục tự đánh dấu: '+n+'/'+mb.length}
[kw,k2,ti,de,bd].forEach(function(e){e.addEventListener('input',db(up,250))});mb.forEach(function(b){b.addEventListener('change',mu)})};
JS
		,
		'swot'          => <<<'JS'
T.swot=function(r){var K='site-swot-v1',ks=['s','w','o','t'],F=ks.map(function(k){return $(r,k)}),gl=$(r,'goal'),H=['Điểm mạnh (S)','Điểm yếu (W)','Cơ hội (O)','Thách thức (T)'],txt='';
try{var v=JSON.parse(localStorage.getItem(K)||'null');if(v){gl.value=v.g||'';F.forEach(function(f,i){f.value=v.v[i]||''})}}catch(e){}
function L(f){return f.value.split('\n').map(function(x){return x.replace(/^\s*(?:[-–•*+]|\d+[.)])\s*/,'').trim()}).filter(Boolean)}
function pr(a,b,f){var o=[];a.slice(0,2).forEach(function(x){b.slice(0,2).forEach(function(y){o.push(f(x,y))})});return o}
function q(s){return'“'+s+'”'}
function up(){var A=F.map(L),S=A[0],W=A[1],O=A[2],Tt=A[3];try{localStorage.setItem(K,JSON.stringify({g:gl.value,v:F.map(function(f){return f.value})}))}catch(e){}
if(!A.some(function(a){return a.length})){$(r,'res').innerHTML='';$(r,'sum').textContent='Ma trận SWOT và gợi ý chiến lược sẽ hiện ở đây.';txt='';return}
var X=[['S-O','Dùng điểm mạnh để nắm cơ hội',pr(S,O,function(x,y){return'Dùng '+q(x)+' để nắm '+q(y)+'.'})],['W-O','Khắc phục điểm yếu để nắm cơ hội',pr(W,O,function(x,y){return'Khắc phục '+q(x)+' để nắm '+q(y)+'.'})],['S-T','Dùng điểm mạnh để giảm thách thức',pr(S,Tt,function(x,y){return'Dùng '+q(x)+' để giảm tác động của '+q(y)+'.'})],['W-T','Phòng thủ: giảm điểm yếu, tránh thách thức',pr(W,Tt,function(x,y){return'Hạn chế '+q(x)+' để tránh '+q(y)+'.'})]];
function cell(c,t,s,it){return'<div class="site-sw--'+c+'"><b>'+t+'</b>'+(s?'<small>'+s+'</small>':'')+(it.length?it.map(function(x,i){return'<p>'+(c=='x'?'':(i+1)+'. ')+E(x)+'</p>'}).join(''):'<p>Chưa có.</p>')+'</div>'}
$(r,'res').innerHTML='<div class="site-swm">'+A.map(function(a,i){return cell(ks[i],H[i],'',a)}).join('')+'</div><p class="site-sum" style="margin-top:14px">Gợi ý chiến lược</p><div class="site-swm">'+X.map(function(x){return cell('x',x[0],x[1],x[2])}).join('')+'</div>';
$(r,'sum').textContent='Ma trận có '+(S.length+W.length+O.length+Tt.length)+' yếu tố'+(gl.value.trim()?' cho mục tiêu: '+gl.value.trim():'')+'.';
txt='PHÂN TÍCH SWOT\n'+(gl.value.trim()?'Mục tiêu: '+gl.value.trim()+'\n':'')+A.map(function(a,i){return'\n'+H[i].toUpperCase()+'\n'+(a.length?a.map(function(x,j){return(j+1)+'. '+x}).join('\n'):'(chưa có)')}).join('\n')+'\n\nGỢI Ý CHIẾN LƯỢC\n'+X.map(function(x){return'\n'+x[0]+' ('+x[1].toLowerCase()+')\n'+(x[2].length?x[2].map(function(y){return'- '+y}).join('\n'):'(chưa có)')}).join('\n')}
F.concat(gl).forEach(function(f){f.addEventListener('input',db(up,200))});
$(r,'cp').addEventListener('click',function(){up();if(txt)cp(txt,this)});$(r,'txt').addEventListener('click',function(){up();if(txt)dl('phan-tich-swot.txt',txt)});
$(r,'clr').addEventListener('click',function(){if(!confirm('Xoá toàn bộ nội dung SWOT đã nhập?'))return;gl.value='';F.forEach(function(f){f.value=''});up()});up()};
JS
		,
		'fb-cover'      => <<<'JS'
T['fb-cover']=function(r){var g=function(k){return $(r,k)},inp=g('file'),dz=g('drop'),si=g('si'),u;
function vis(w,h,a){return w/h>a?{x:(w-h*a)/2,y:0,w:h*a,h:h}:{x:0,y:(h-w/a)/2,w:w,h:w/a}}
function box(e,b,w,h){e.style.cssText='left:'+b.x/w*100+'%;top:'+b.y/h*100+'%;width:'+b.w/w*100+'%;height:'+b.h/h*100+'%'}
function err(m){R(r,[['er','Không đọc được ảnh',m]],'')}
function load(f){if(!f)return;if(!/^image\//.test(f.type)){err('Hãy chọn tệp ảnh JPG hoặc PNG.');return}if(u)URL.revokeObjectURL(u);u=URL.createObjectURL(f);var im=new Image();im.onload=function(){show(f,im.naturalWidth,im.naturalHeight)};im.onerror=function(){err('Trình duyệt không mở được tệp này.')};im.src=u}
function show(f,w,h){['di','mi'].forEach(function(k){g(k).style.backgroundImage='url("'+u+'")'});si.style.backgroundImage='url("'+u+'")';
r.querySelectorAll('[data-k="ph"]').forEach(function(e){e.style.visibility='hidden'});
var ri=w/h,a=2;si.style.cssText+=';visibility:visible;'+(ri>=a?'left:0;width:100%;height:'+a/ri*100+'%;top:'+(100-a/ri*100)/2+'%':'top:0;height:100%;width:'+ri/a*100+'%;left:'+(100-ri/a*100)/2+'%');
var D1=vis(w,h,851/315),M=vis(w,h,640/360),x0=Math.max(D1.x,M.x),y0=Math.max(D1.y,M.y),X={x:x0,y:y0,w:Math.min(D1.x+D1.w,M.x+M.w)-x0,h:Math.min(D1.y+D1.h,M.y+M.h)-y0};
box(g('rd'),D1,w,h);box(g('rm'),M,w,h);box(g('rx'),X,w,h);
var kb=f.size/1024,rt=ri.toFixed(2).replace('.',','),C=[];
C.push(/jpe?g|png/.test(f.type)?['ok','Định dạng '+f.type.split('/')[1].toUpperCase(),'Bài đề xuất JPG hoặc PNG.']:['wa','Định dạng '+f.type.split('/')[1].toUpperCase(),'Bài đề xuất JPG hoặc PNG.']);
C.push(w<400||h<150?['er','Ảnh '+w+' × '+h+' px nhỏ quá','Nhỏ nhất 400 × 150 px.']:w>1958||h>745?['wa','Ảnh '+w+' × '+h+' px lớn hơn mức tối đa','Lớn nhất 1958 × 745 px.']:(w==851&&h==315)||(w==1702&&h==630)?['ok','Ảnh '+w+' × '+h+' px','Đúng kích thước đề xuất.']:['in','Ảnh '+w+' × '+h+' px','Bài đề xuất 851 × 315 px, hoặc 1702 × 630 px để ảnh nét hơn.']);
C.push(Math.abs(ri-2.7)<.05?['ok','Tỷ lệ '+rt+':1','Khớp tỷ lệ 2,7:1.']:['wa','Tỷ lệ '+rt+':1','Bài khuyên tỷ lệ 2,7:1, nên một phần ảnh sẽ bị cắt.']);
C.push(kb<=100?['ok','Dung lượng '+F(kb,1)+' KB','Không quá 100 KB.']:['wa','Dung lượng '+F(kb,1)+' KB','Bài khuyên tối đa 100 KB. Hãy nén ảnh.']);
C.push(['in','Phần ảnh hiện trên cả hai thiết bị: '+Math.round(X.w)+' × '+Math.round(X.h)+' px','Đặt logo, chữ và lời kêu gọi hành động trong khung viền đứt.']);R(r,C)}
inp.addEventListener('change',function(){load(inp.files[0])});
['dragenter','dragover'].forEach(function(e){dz.addEventListener(e,function(v){v.preventDefault();dz.classList.add('is-over')})});
['dragleave','drop'].forEach(function(e){dz.addEventListener(e,function(v){v.preventDefault();dz.classList.remove('is-over')})});
dz.addEventListener('drop',function(v){load(v.dataTransfer.files[0])})};
JS
		,
		'faq-schema'    => <<<'JS'
T['faq-schema']=function(r){var g=function(k){return $(r,k)},bx=g('rows'),js=g('js'),ht=g('html'),kw=g('kw'),n=2,cur='js';
function tpl(i){var d=D.createElement('div'),id=r.id;d.className='site-qa';d.innerHTML='<div class="site-qa__top"><label for="'+id+'-q'+i+'">Câu hỏi <span data-no></span></label><button type="button" class="site-x" data-del>Xoá</button></div><input type="text" id="'+id+'-q'+i+'" data-q autocomplete="off"><label class="site-lb2" for="'+id+'-a'+i+'">Câu trả lời</label><textarea id="'+id+'-a'+i+'" data-a rows="3" placeholder="Trả lời ngắn, 2–4 câu"></textarea>';return d}
function num(){bx.querySelectorAll('.site-qa').forEach(function(q,i){q.querySelector('[data-no]').textContent=i+1;q.querySelector('[data-del]').setAttribute('aria-label','Xoá câu hỏi '+(i+1))})}
function up(){var P=[],C=[],k=N(kw.value),seen={};bx.querySelectorAll('.site-qa').forEach(function(q,i){var Q=q.querySelector('[data-q]').value.trim(),A=q.querySelector('[data-a]').value.trim().replace(/\s*\n\s*/g,' ');if(!Q&&!A)return;
var no='Câu '+(i+1)+': ';if(!Q||!A){C.push(['er',no+'thiếu '+(Q?'câu trả lời':'câu hỏi'),'']);return}P.push([Q,A]);
var s=sc(A);C.push(s>=2&&s<=4?['ok',no+'trả lời '+s+' câu','Trong mốc 2–4 câu.']:['wa',no+'trả lời '+s+' câu',s<2?'Có thể thêm một câu giải thích.':'Bài khuyên chỉ nên dài 2–4 câu.']);
if(seen[N(Q)])C.push(['wa',no+'trùng câu hỏi '+seen[N(Q)],'']);else seen[N(Q)]=i+1;if(k&&!cnt(Q+' '+A,k))C.push(['in',no+'chưa có từ khóa chính','Chỉ thêm khi đọc vẫn tự nhiên.'])});
if(!P.length){js.value=ht.value='';R(r,C,C.length?'Hoàn thiện các cặp hỏi đáp bên dưới.':'Nhập ít nhất một cặp hỏi đáp.');return}
var o={'@context':'https://schema.org','@type':'FAQPage',mainEntity:P.map(function(p){return{'@type':'Question',name:p[0],acceptedAnswer:{'@type':'Answer',text:p[1]}}})};
js.value='<script type="application/ld+json">\n'+JSON.stringify(o,null,2).replace(/<\//g,'<\\/')+'\n</'+'script>';
var H=function(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')};ht.value='<section class="faq">\n  <h2>Câu hỏi thường gặp</h2>\n'+P.map(function(p){return'  <h3>'+H(p[0])+'</h3>\n  <p>'+H(p[1])+'</p>'}).join('\n')+'\n</section>';
var ok=C.filter(function(c){return c[0]=='ok'}).length;R(r,C,P.length+' cặp hỏi đáp, '+ok+' câu trả lời đúng mốc 2–4 câu.')}
bx.addEventListener('input',db(up,200));kw.addEventListener('input',db(up,200));
bx.addEventListener('click',function(e){var b=e.target.closest('[data-del]');if(!b)return;var q=b.closest('.site-qa');if(bx.children.length>1)q.remove();else{q.querySelector('[data-q]').value=q.querySelector('[data-a]').value=''}num();up()});
g('add').addEventListener('click',function(){if(bx.children.length>=20)return;var d=tpl(++n);bx.appendChild(d);num();d.querySelector('input').focus()});
r.querySelectorAll('[data-tab]').forEach(function(b){b.addEventListener('click',function(){cur=b.dataset.tab;r.querySelectorAll('[data-tab]').forEach(function(x){x.setAttribute('aria-pressed',x===b)});js.hidden=cur!='js';ht.hidden=cur!='html'})});
g('cp').addEventListener('click',function(){var v=(cur=='js'?js:ht).value;if(v)cp(v,this)});num();up()};
JS
		,
		'fb-ads'        => <<<'JS'
T['fb-ads']=function(r){var g=function(k){return $(r,k)},I=['sp','rs','rv','vl','im','rc','ck'];
function up(){var v={};I.forEach(function(k){v[k]=num(g(k).value)});var c=g('cur').value,u=c=='USD'?' USD':' đ',m=function(x){return isFinite(x)?F(x,c=='USD'?2:0)+u:'–'},q=function(a,b){return a>=0&&b>0?a/b:NaN};
var cpr=q(v.sp,v.rs),roas=q(v.rv,v.sp),cpm=q(v.sp,v.im)*1000,fq=q(v.im,v.rc),ctr=q(v.ck,v.im)*100,cpc=q(v.sp,v.ck);
g('cpr').textContent=m(cpr);g('roas').textContent=isFinite(roas)?F(roas,2)+' lần':'–';g('cpm').textContent=m(cpm);g('fq').textContent=isFinite(fq)?F(fq,2)+' lần':'–';g('ctr').textContent=isFinite(ctr)?F(ctr,2)+'%':'–';g('cpc').textContent=m(cpc);
var C=[];if(v.rc>v.im)C.push(['er','Người xem lớn hơn lượt hiển thị','Mỗi người xem được tính ít nhất một lượt hiển thị. Kiểm tra lại số liệu.']);
if(v.ck>v.im)C.push(['er','Lượt nhấp lớn hơn lượt hiển thị','Kiểm tra lại số liệu.']);
if(isFinite(cpr)&&v.vl>0)C.push(cpr>v.vl?['er','Mỗi kết quả tốn '+m(cpr)+' nhưng chỉ mang về '+m(v.vl),'Chiến dịch đang lỗ trên mỗi kết quả, cần tối ưu lại mức chi.']:['ok','Mỗi kết quả tốn '+m(cpr)+', thấp hơn giá trị '+m(v.vl),'Mỗi kết quả mang về nhiều hơn số tiền bỏ ra.']);
if(isFinite(roas))C.push(roas<1?['wa','ROAS '+F(roas,2)+': doanh thu thấp hơn chi tiêu','Mỗi 1'+u+' chi tiêu mang về '+F(roas,2)+u+' doanh thu.']:['ok','ROAS '+F(roas,2),'Mỗi 1'+u+' chi tiêu mang về '+F(roas,2)+u+' doanh thu.']);
if(isFinite(fq))C.push(fq>10?['wa','Tần suất '+F(fq,2)+' lần','Hơn 10 lần: bài gợi ý có thể đang quá tải đối tượng. Nếu tỷ lệ chuyển đổi còn cao thì đối tượng chưa quá tải.']:['ok','Tần suất '+F(fq,2)+' lần','Chưa vượt mốc 10 lần bài nêu.']);
if(isFinite(ctr))C.push(['in','CTR liên kết '+F(ctr,2)+'%','Bài dẫn CTR trung bình mọi ngành là 0,9%. CTR cao thì CPC thường thấp hơn.']);
R(r,C,C.length?C.length+' nhận xét theo số liệu bạn nhập.':'Nhập thêm số liệu để xem nhận xét.')}
I.concat('cur').forEach(function(k){g(k).addEventListener('input',db(up,150));g(k).addEventListener('change',up)});up()};
JS
		,
		'alt-text'      => <<<'JS'
T['alt-text']=function(r){var g=function(k){return $(r,k)},ta=g('in'),kw=g('kw'),bar=g('bar'),nn=g('n'),BAD=/^(hình ảnh|bức ảnh|bức hình|ảnh|hình|image|picture|photo)( của| of)\b/i;
function chk(a,k){var C=[],l=a.length;C.push(l<=125?['ok',l+' / 125 ký tự','Ngắn gọn, trong mốc 125 ký tự.']:['wa',l+' / 125 ký tự','Dài hơn 125 ký tự, nên rút gọn.']);
if(BAD.test(N(a)))C.push(['wa','Mở đầu bằng “'+E(N(a).match(BAD)[0])+'”','Bài khuyên bỏ cụm này vì ảnh đã là ảnh.']);
if(k){var c=cnt(a,k);C.push(!c?['in','Chưa có từ khóa','Chỉ thêm khi từ khóa mô tả đúng ảnh.']:c>1?['wa','Từ khóa lặp '+c+' lần','Xem lại để tránh nhồi nhét từ khóa.']:['ok','Có từ khóa, không lặp',''])}return C}
function up(){var v=ta.value,k=N(kw.value);if(/<img\b/i.test(v)){bar.style.width='0';nn.textContent='Chế độ rà HTML';
var im=[].slice.call(new DOMParser().parseFromString(v,'text/html').images),bad=0,h=im.map(function(e,i){var s=(e.getAttribute('src')||e.getAttribute('data-src')||'').split(/[?#]/)[0].split('/').pop()||'(không có src)',a=e.getAttribute('alt'),C;
if(a==null)C=[['er','Thiếu thuộc tính alt','']];else if(!a.trim())C=[['wa','Alt rỗng','chưa có mô tả cho ảnh.']];else C=chk(a.trim(),k).filter(function(c){return c[0]!='ok'&&c[0]!='in'});
if(C.length)bad++;return'<div class="site-chk"><span class="site-st site-st--'+(C.length?C[0][0]:'ok')+'">'+ST[C.length?C[0][0]:'ok']+'</span><div><b>Ảnh '+(i+1)+': '+E(s)+'</b><i>'+(a?'alt: '+E(a.trim()):'')+'</i>'+C.map(function(c){return'<i>'+c[1]+(c[2]?': '+c[2]:'')+'</i>'}).join('')+'</div></div>'});
$(r,'res').innerHTML=h.join('');$(r,'sum').textContent=im.length+' ảnh, '+bad+' ảnh cần sửa alt.';return}
var a=v.trim().replace(/\s+/g,' ');bar.style.width=Math.min(100,a.length/1.25)+'%';bar.classList.toggle('is-over',a.length>125);nn.textContent=a.length+' / 125 ký tự';
if(!a){R(r,[],'Kết quả kiểm tra sẽ hiện ở đây.');return}R(r,chk(a,k))}
ta.addEventListener('input',db(up,150));kw.addEventListener('input',db(up,150));up()};
JS
		,
	);
	return $js[ $name ] ?? '';
}

add_action(
	'wp_head',
	function () {
		$names = site_tools_on_page();
		if ( ! $names ) {
			return;
		}
		$css = site_tools_css( 'base' );
		foreach ( $names as $n ) {
			$css .= site_tools_css( $n );
		}
		echo "<style id=\"site-tools-css\" data-no-optimize=\"1\">\n" . $css . "</style>\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	},
	31
);

add_action(
	'wp_footer',
	function () {
		$names = site_tools_on_page();
		if ( ! $names ) {
			return;
		}
		$js = site_tools_js( 'base' );
		foreach ( $names as $n ) {
			$js .= site_tools_js( $n );
		}
		$js .= "D.querySelectorAll('.site-tool[data-tool]').forEach(function(el){try{T[el.dataset.tool]&&T[el.dataset.tool](el)}catch(e){window.console&&console.error('site-tool',el.dataset.tool,e)}});\n";
		echo '<script id="site-tools-js" data-no-optimize="1" data-no-defer="1">' . "\n(function(){\n" . $js . "})();\n</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	},
	6
);
