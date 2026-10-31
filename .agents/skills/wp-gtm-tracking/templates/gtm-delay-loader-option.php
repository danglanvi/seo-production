<?php
/**
 * Plugin Name: GTV - GTM hoãn (mẫu)
 * Description: Hoãn GTM và gtag Google Ads tới lần tương tác đầu hoặc N giây sau load. Bỏ gtag G-xxx gắn thẳng khi container GTM đã có Google tag gửi page_view. Giỏ, checkout, cảm ơn nạp ngay.
 *
 * Mẫu gốc: skills/wp-pagespeed/templates/gtm-delay-loader.php. Quy trình: skills/wp-gtm-tracking/SKILL.md.
 *
 * File này KHÔNG ghi DB. Nó đổi đầu ra tại lúc in trang:
 *  1. Lọc option `ihaf_insert_header` (Insert Headers and Footers) khi wp_head chạy ở frontend: bỏ snippet GTM, và bỏ gtag G-xxx
 *     gắn thẳng nếu container có Google tag cho ID đó. Option trong DB giữ nguyên. Trong wp-admin bộ lọc không chạy,
 *     nên lưu form WPCode không làm mất snippet.
 *  2. In loader hoãn thay cho snippet GTM. ID container lấy từ hằng số GTVD_GTM_ID, nếu trống thì lấy từ chính option
 *     (nên đổi snippet sang GTM-BBBB222 ở option thì loader tự theo, không sửa file này).
 *  3. Chỉ khi gtag G-xxx bị bỏ: bọc đầu ra của Google Listings & Ads ở wp_head (ưu tiên 999999). Thẻ `gtag/js?id=AW-…` đổi thành
 *     thẻ meta `gtvd-defer-src`. Lệnh gtag() inline của plugin giữ nguyên và chờ trong dataLayer.
 *     Loader nạp thẻ AW đó và GTM cùng một mốc (hẹn giờ hoặc tương tác), cả hai `async=false`: tải song song, thực thi theo thứ tự
 *     chèn, AW trước gtm.js. Google tag trong GTM thấy AW đã đăng ký nên không nạp lại `AW…&cx=c`: AW nạp 1 lần.
 *     Không nạp AW sớm hơn GTM: script bắt đầu trước LCP quan sát bị Lantern tính vào LCP (site bán lẻ mẫu 31/10/2026: 2,2 → 3,7 s).
 *     Dự phòng: 4 s sau khi gtm.js nạp xong mà window.google_tag_manager chưa có ID AW, hoặc gtm.js lỗi, loader nạp lại thẻ meta.
 *     URL quảng cáo (gọi g() khi trang đang parse): GTM nạp ngay, Google tag tự nạp AW, dự phòng như trên.
 *     Khi còn giữ gtag G-xxx thì không hoãn AW: gtag.js của G tự nạp gtag/js?id=AW ngay khi thấy lệnh config AW (đã đo: AW tải lúc 348 ms trong bản giữ gtag G).
 *  4. Giỏ, checkout, trang cảm ơn: in snippet GTM chuẩn (nạp ngay), không đụng thẻ AW của plugin.
 *
 * Cờ tắt nhanh: đổi tên file thành gtvd-gtm-delay.php.off rồi purge theo URL. Mọi thứ về đúng như cũ vì DB không đổi.
 * Tự an toàn: nếu regex không bóc được snippet khỏi option (hoặc bóc mất thẻ meta), file này không làm gì và ghi một dòng vào error_log.
 *
 * Hằng số (khai trước khi file này nạp, ví dụ trong wp-config.php; không khai thì dùng mặc định):
 *   GTVD_GTM_WAIT_MS   2000   Số ms sau sự kiện load thì nạp nếu chưa có tương tác. 0 = không hẹn giờ, chỉ chờ tương tác.
 *   GTVD_GTM_ID        ''     Ép ID container. Trống = đọc từ option ihaf_insert_header.
 *   GTVD_GTM_DROP_GTAG 'auto' 'auto' = chỉ bỏ gtag G-xxx khi container có Google tag chạy mọi trang (kiểm bằng gtm.js công khai,
 *                                 chạy ở WP-Cron, không chạy trong request của khách). true = luôn bỏ. false = luôn giữ.
 * Kiểm tay verdict: wp eval 'gtvd_gtm_verify("GTM-XXXXXXX","G-XXXXXXXXXX");' rồi wp transient get gtvd_gtm_v_GTM-XXXXXXX_G-XXXXXXXXXX
 */
defined( 'ABSPATH' ) || exit;

if ( ! defined( 'GTVD_GTM_WAIT_MS' ) ) {
	define( 'GTVD_GTM_WAIT_MS', 2000 );
}
if ( ! defined( 'GTVD_GTM_ID' ) ) {
	define( 'GTVD_GTM_ID', '' );
}
if ( ! defined( 'GTVD_GTM_DROP_GTAG' ) ) {
	define( 'GTVD_GTM_DROP_GTAG', 'auto' );
}

// Snippet GTM trong option: thẻ script chứa googletagmanager.com/gtm.js, kèm hai dòng chú thích của Google nếu có.
const GTVD_GTM_RE_GTM = '~(?:<!--\s*Google Tag Manager\s*-->\s*)?<script[^>]*>(?:(?!</script>).)*?googletagmanager\.com/gtm\.js(?:(?!</script>).)*?</script>\s*(?:<!--\s*End Google Tag Manager\s*-->\s*)?~is';
// gtag gắn thẳng: thẻ gtag/js?id=G-… rồi khối script có lệnh gtag(. Nhóm 1 = ID đo lường.
const GTVD_GTM_RE_GTAG = '~(?:<!--\s*Google tag \(gtag\.js\)\s*-->\s*)?<script[^>]*googletagmanager\.com/gtag/js\?id=(G-[A-Z0-9]+)[^>]*></script>\s*<script[^>]*>(?:(?!</script>).)*?gtag\((?:(?!</script>).)*?</script>\s*~is';
// Thẻ gtag Google Ads do Google Listings & Ads in ra.
const GTVD_GTM_RE_AW = '~<script\b[^>]*\bsrc=["\'](https://www\.googletagmanager\.com/gtag/js\?id=AW-[0-9]+)["\'][^>]*></script>~i';

/** Giá trị gốc của option, không qua bộ lọc của file này. */
function gtvd_gtm_raw_header() {
	remove_filter( 'option_ihaf_insert_header', 'gtvd_gtm_filter_header', 20 );
	$raw = (string) get_option( 'ihaf_insert_header' );
	add_filter( 'option_ihaf_insert_header', 'gtvd_gtm_filter_header', 20 );
	return $raw;
}

/** Đọc object "resource" trong gtm.js công khai (đếm ngoặc, bỏ qua chuỗi) rồi giải mã JSON. */
function gtvd_gtm_resource( $js ) {
	$p = strpos( $js, '"resource"' );
	$p = false === $p ? false : strpos( $js, '{', $p );
	if ( false === $p ) {
		return null;
	}
	$depth = 0;
	$str   = false;
	$len   = strlen( $js );
	for ( $i = $p; $i < $len; $i++ ) {
		$c = $js[ $i ];
		if ( $str ) {
			if ( '\\' === $c ) {
				$i++;
			} elseif ( '"' === $c ) {
				$str = false;
			}
		} elseif ( '"' === $c ) {
			$str = true;
		} elseif ( '{' === $c ) {
			$depth++;
		} elseif ( '}' === $c && 0 === --$depth ) {
			$res = json_decode( substr( $js, $p, $i - $p + 1 ), true );
			return is_array( $res ) ? $res : null;
		}
	}
	return null;
}

/**
 * Container có Google tag cho $ga_id chạy ở mọi trang và gửi page_view không?
 * Điều kiện ok: tag __googtag đúng ID, không tắt send_page_view, nằm trong một rule chỉ có một điều kiện
 * là sự kiện tải trang (gtm.init, gtm.js, gtm.dom, gtm.load), không có rule chặn.
 * Trả array( 'ok' => bool, 'why' => lý do ).
 */
function gtvd_gtm_check_container( $js, $ga_id ) {
	$res = gtvd_gtm_resource( $js );
	if ( ! $res || ! isset( $res['tags'] ) ) {
		return array( 'ok' => false, 'why' => 'không đọc được cấu trúc container' );
	}
	if ( ! $res['tags'] ) {
		return array( 'ok' => false, 'why' => 'container rỗng, chưa có tag nào' );
	}
	$page = array( 'gtm.init', 'gtm.js', 'gtm.dom', 'gtm.load' );
	foreach ( $res['tags'] as $i => $tag ) {
		if ( ( isset( $tag['function'] ) ? $tag['function'] : '' ) !== '__googtag' || ( isset( $tag['vtp_tagId'] ) ? $tag['vtp_tagId'] : '' ) !== $ga_id ) {
			continue;
		}
		if ( preg_match( '~send_page_view.{0,80}false~i', wp_json_encode( $tag ) ) ) {
			return array( 'ok' => false, 'why' => 'Google tag ' . $ga_id . ' tắt send_page_view' );
		}
		$all_pages = false;
		$blocked   = false;
		foreach ( isset( $res['rules'] ) ? $res['rules'] : array() as $rule ) {
			$if  = array();
			$add = array();
			foreach ( $rule as $part ) {
				if ( 'if' === $part[0] ) {
					$if = array_slice( $part, 1 );
				} elseif ( 'add' === $part[0] ) {
					$add = array_slice( $part, 1 );
				} elseif ( 'block' === $part[0] || 'unless' === $part[0] ) {
					$blocked = $blocked || in_array( $i, array_slice( $part, 1 ), true ) || 'unless' === $part[0];
				}
			}
			if ( in_array( $i, $add, true ) && 1 === count( $if ) && 2 === count( $rule ) ) {
				$pred = isset( $res['predicates'][ $if[0] ] ) ? $res['predicates'][ $if[0] ] : array();
				if ( isset( $pred['function'], $pred['arg1'] ) && '_eq' === $pred['function'] && in_array( $pred['arg1'], $page, true ) ) {
					$all_pages = true;
				}
			}
		}
		if ( $all_pages && ! $blocked ) {
			return array( 'ok' => true, 'why' => 'Google tag ' . $ga_id . ' chạy ở mọi trang' );
		}
		return array( 'ok' => false, 'why' => 'Google tag ' . $ga_id . ' có nhưng trigger không phải mọi trang' );
	}
	return array( 'ok' => false, 'why' => 'container không có Google tag cho ' . $ga_id );
}

/** Chạy trong WP-Cron (hook gtvd_gtm_verify). Ghi transient, và ghi error_log khi phải giữ gtag. */
function gtvd_gtm_verify( $gtm_id, $ga_id ) {
	$r = wp_remote_get( 'https://www.googletagmanager.com/gtm.js?id=' . rawurlencode( $gtm_id ), array( 'timeout' => 10, 'user-agent' => 'Mozilla/5.0 (compatible; site-gtm-check)' ) );
	if ( is_wp_error( $r ) || 200 !== (int) wp_remote_retrieve_response_code( $r ) ) {
		$v   = array( 'ok' => false, 'why' => 'không tải được gtm.js của ' . $gtm_id );
		$ttl = 10 * MINUTE_IN_SECONDS;
	} else {
		$v   = gtvd_gtm_check_container( (string) wp_remote_retrieve_body( $r ), $ga_id );
		$ttl = $v['ok'] ? 12 * HOUR_IN_SECONDS : HOUR_IN_SECONDS;
	}
	set_transient( 'gtvd_gtm_v_' . $gtm_id . '_' . $ga_id, $v, $ttl );
	if ( ! $v['ok'] ) {
		error_log( '[gtvd-gtm-delay] CẢNH BÁO giữ gtag trực tiếp ' . $ga_id . ': ' . $v['why'] );
	}
}
add_action( 'gtvd_gtm_verify', 'gtvd_gtm_verify', 10, 2 );

/** Verdict đã lưu. Thiếu thì hẹn một lần kiểm bằng WP-Cron và coi như "chưa ok" (giữ gtag). */
function gtvd_gtm_verdict( $gtm_id, $ga_id ) {
	$v = get_transient( 'gtvd_gtm_v_' . $gtm_id . '_' . $ga_id );
	if ( ! is_array( $v ) ) {
		if ( ! wp_next_scheduled( 'gtvd_gtm_verify', array( $gtm_id, $ga_id ) ) ) {
			wp_schedule_single_event( time() + 10, 'gtvd_gtm_verify', array( $gtm_id, $ga_id ) );
		}
		return array( 'ok' => false, 'why' => 'chưa kiểm container' );
	}
	return $v;
}

/** Trạng thái của request hiện tại. Tính một lần, chỉ dùng trong wp_head ở frontend. */
function gtvd_gtm_state() {
	static $s = null;
	if ( null !== $s ) {
		return $s;
	}
	$s   = array( 'on' => false );
	$raw = gtvd_gtm_raw_header();

	$gtm = (string) GTVD_GTM_ID;
	if ( '' === $gtm && preg_match( GTVD_GTM_RE_GTM, $raw, $m ) && preg_match( '~GTM-[A-Z0-9]{4,}~', $m[0], $i ) ) {
		$gtm = $i[0];
	}
	if ( '' === $gtm ) {
		error_log( '[gtvd-gtm-delay] Không tìm thấy ID container (hằng số trống, option không có snippet GTM). File này không làm gì.' );
		return $s;
	}

	$drop = false;
	$ga   = '';
	if ( preg_match( GTVD_GTM_RE_GTAG, $raw, $g ) ) {
		$ga   = $g[1];
		$mode = GTVD_GTM_DROP_GTAG;
		$drop = true === $mode || ( 'auto' === $mode && ! empty( gtvd_gtm_verdict( $gtm, $ga )['ok'] ) );
	}

	$strip = preg_replace( GTVD_GTM_RE_GTM, '', $raw );
	if ( $drop ) {
		$strip = preg_replace( GTVD_GTM_RE_GTAG, '', $strip );
	}
	// Kiểm: không còn thẻ GTM, đúng nhóm gtag còn lại, không mất thẻ meta (DMCA).
	$ok = null !== $strip
		&& false === stripos( $strip, 'googletagmanager.com/gtm.js' )
		&& ( ! $drop || false === stripos( $strip, 'googletagmanager.com/gtag/js' ) )
		&& substr_count( $strip, '<meta' ) === substr_count( $raw, '<meta' );
	if ( ! $ok ) {
		error_log( '[gtvd-gtm-delay] Không bóc sạch snippet khỏi ihaf_insert_header. File này không làm gì, trang giữ nguyên.' );
		return $s;
	}

	$now = function_exists( 'is_cart' ) && ( is_cart() || is_checkout() || is_order_received_page() );
	$s   = array(
		'on'    => true,
		'gtm'   => $gtm,
		'drop'  => $drop,
		'ga'    => $ga,
		'strip' => $strip,
		'now'   => (bool) apply_filters( 'gtvd_gtm_now', $now ),
		'wait'  => max( 0, (int) apply_filters( 'gtvd_gtm_wait_ms', GTVD_GTM_WAIT_MS ) ),
	);
	return $s;
}

/** Bộ lọc option: chỉ chạy lúc wp_head ở frontend. wp-admin, REST, WP-CLI nhận giá trị gốc. */
function gtvd_gtm_filter_header( $value ) {
	if ( is_admin() || ! doing_action( 'wp_head' ) ) {
		return $value;
	}
	$s = gtvd_gtm_state();
	return $s['on'] ? $s['strip'] : $value;
}
if ( ! is_admin() ) {
	add_filter( 'option_ihaf_insert_header', 'gtvd_gtm_filter_header', 20 );
}

/** Loader. Cùng ưu tiên 10 với đầu ra của WPCode, đúng vị trí snippet GTM cũ. */
function gtvd_gtm_print() {
	$s = gtvd_gtm_state();
	if ( ! $s['on'] ) {
		return;
	}
	$id = esc_js( $s['gtm'] );
	echo '<!-- gtvd-gtm-delay: ' . ( $s['now'] ? 'now' : 'wait=' . (int) $s['wait'] ) . ' gtag=' . ( '' === $s['ga'] ? 'none' : ( $s['drop'] ? 'drop' : 'keep' ) ) . " -->\n";
	if ( $s['now'] ) {
		?>
<script data-no-optimize="1" data-no-defer="1">(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','<?php echo $id; ?>');</script>
		<?php
		return;
	}
	?>
<script data-no-optimize="1" data-no-defer="1">/*gtvd-gtm-delay*/(function(w,d,id,t){w.dataLayer=w.dataLayer||[];w.dataLayer.push({'gtm.start':new Date().getTime(),event:'gtm.js'});
var e=['mouseover','touchstart','scroll','keydown','click'],o={passive:true,capture:true},x=0,r=0,q=[],u='https://www.googletagmanager.com/gtm.js?id='+id,c=[function(){f();setTimeout(a,4000)},function(){z();a()}];
function k(v){if(r)return;var a=v.target&&v.target.closest&&v.target.closest('a[href],area[href]');if(a&&q.length<5)q.push(a)}
function f(){r=1;d.removeEventListener('click',k,true);var l=q;q=[];l.forEach(function(a){if(!d.contains(a))return;w.dataLayer.push({event:'gtm.linkClick','gtm.element':a,'gtm.elementClasses':typeof a.className==='string'?a.className:'','gtm.elementId':a.id||'','gtm.elementTarget':a.target||'','gtm.elementUrl':a.href||''})})}
function z(){r=1;q=[];d.removeEventListener('click',k,true)}
function s(u,c,n){var j=d.createElement('script');j.async=!n;j.src=u;if(c){j.onload=c[0];j.onerror=c[1]}d.head.appendChild(j)}
function a(){var c=w.google_tag_manager;[].forEach.call(d.querySelectorAll('meta[name="gtvd-defer-src"]'),function(m){var i=(m.content.match(/[?&]id=([^&]+)/)||[])[1];if(!(c&&i&&c[i]))s(m.content)})}
function g(){if(x)return;x=1;e.forEach(function(n){w.removeEventListener(n,g,o)});if(d.readyState!=='loading')[].forEach.call(d.querySelectorAll('meta[name="gtvd-defer-src"]'),function(v){s(v.content,0,1)});s(u,c,1)}
d.addEventListener('click',k,true);
if(/[?&](gclid|gbraid|wbraid|fbclid|ttclid|utm_[a-z]+)=/.test(location.search))return g();
e.forEach(function(n){w.addEventListener(n,g,o)});
if(t>0){var h=function(){setTimeout(g,t)};d.readyState==='complete'?h():w.addEventListener('load',h)}
})(window,document,'<?php echo $id; ?>',<?php echo (int) $s['wait']; ?>);</script>
	<?php
}
add_action( 'wp_head', 'gtvd_gtm_print', 10 );

/** Bọc đầu ra của Google Listings & Ads (ưu tiên 999999): thẻ gtag AW thành thẻ meta, để loader nạp. */
function gtvd_gtm_buf( $level = null ) {
	static $lv = 0;
	if ( null !== $level ) {
		$lv = $level;
	}
	return $lv;
}
function gtvd_gtm_hold_aw( $html ) {
	$out = preg_replace( GTVD_GTM_RE_AW, '<meta name="gtvd-defer-src" content="$1">', $html );
	return null === $out ? $html : $out;
}
add_action(
	'wp_head',
	function () {
		$s = gtvd_gtm_state();
		// Hoãn AW khi gtag G đã bỏ, hoặc option không còn gtag G (sau khi đổi T7). Giữ gtag G thì để AW nguyên.
		if ( $s['on'] && ! $s['now'] && ( $s['drop'] || '' === $s['ga'] ) && ob_start( 'gtvd_gtm_hold_aw' ) ) {
			gtvd_gtm_buf( ob_get_level() );
		}
	},
	999998
);
add_action(
	'wp_head',
	function () {
		if ( gtvd_gtm_buf() && ob_get_level() === gtvd_gtm_buf() ) {
			ob_end_flush();
		}
		gtvd_gtm_buf( 0 );
	},
	1000000
);
