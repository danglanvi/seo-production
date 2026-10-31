<?php
/**
 * Khung thử gtvd-gtm-delay.php ngoài WordPress (stub tối thiểu). Không đụng server.
 * php harness.php <kịch-bản> [thư-mục-ra]   (mỗi kịch bản một tiến trình vì file nạp hằng số một lần)
 * Kịch bản: ok | unknown | now | cleaned | t7 | badsnip | admin | cli | container | wait0
 * Đầu ra: <thư-mục-ra>/<kịch-bản>.html (đầu trang giả lập) và dòng KIEM: ĐẠT/LỖI.
 */
error_reporting( E_ALL );
define( 'ABSPATH', __DIR__ . '/' );
$scenario = isset( $argv[1] ) ? $argv[1] : 'ok';
$outdir   = isset( $argv[2] ) ? $argv[2] : sys_get_temp_dir();
$fx       = __DIR__ . '/fixture/';
$logfile  = tempnam( sys_get_temp_dir(), 'gtmlog' );
ini_set( 'error_log', $logfile );
ini_set( 'log_errors', '1' );

const MINUTE_IN_SECONDS = 60;
const HOUR_IN_SECONDS   = 3600;
$GLOBALS['hooks']      = array();
$GLOBALS['options']    = array();
$GLOBALS['transients'] = array();
$GLOBALS['scheduled']  = array();
$GLOBALS['action']     = '';
$GLOBALS['flags']      = array( 'admin' => false, 'cart' => false );

function add_action( $h, $f, $p = 10, $n = 1 ) { $GLOBALS['hooks'][ $h ][ $p ][] = $f; }
function add_filter( $h, $f, $p = 10, $n = 1 ) { $GLOBALS['hooks'][ $h ][ $p ][] = $f; }
function remove_filter( $h, $f, $p = 10 ) {
	if ( isset( $GLOBALS['hooks'][ $h ][ $p ] ) ) {
		$GLOBALS['hooks'][ $h ][ $p ] = array_values( array_filter( $GLOBALS['hooks'][ $h ][ $p ], function ( $x ) use ( $f ) { return $x !== $f; } ) );
	}
}
function apply_filters( $h, $v ) {
	if ( empty( $GLOBALS['hooks'][ $h ] ) ) { return $v; }
	ksort( $GLOBALS['hooks'][ $h ] );
	foreach ( $GLOBALS['hooks'][ $h ] as $fs ) { foreach ( $fs as $f ) { $v = call_user_func( $f, $v ); } }
	return $v;
}
function get_option( $n ) { return apply_filters( 'option_' . $n, isset( $GLOBALS['options'][ $n ] ) ? $GLOBALS['options'][ $n ] : false ); }
function doing_action( $a ) { return $GLOBALS['action'] === $a; }
function is_admin() { return $GLOBALS['flags']['admin']; }
function is_cart() { return $GLOBALS['flags']['cart']; }
function is_checkout() { return false; }
function is_order_received_page() { return false; }
function wp_unslash( $s ) { return stripslashes( $s ); }
function esc_js( $s ) { return addslashes( $s ); }
function wp_json_encode( $v ) { return json_encode( $v, JSON_UNESCAPED_UNICODE ); }
function get_transient( $k ) { return isset( $GLOBALS['transients'][ $k ] ) ? $GLOBALS['transients'][ $k ] : false; }
function set_transient( $k, $v, $t ) { $GLOBALS['transients'][ $k ] = $v; return true; }
function wp_next_scheduled( $h, $a = array() ) { return false; }
function wp_schedule_single_event( $t, $h, $a = array() ) { $GLOBALS['scheduled'][] = array( $h, $a ); return true; }
function is_wp_error( $x ) { return false; }
function wp_remote_get( $u, $a = array() ) { return array( 'url' => $u, 'code' => 200, 'body' => file_get_contents( $GLOBALS['fixture_for'][ $u ] ) ); }
function wp_remote_retrieve_response_code( $r ) { return $r['code']; }
function wp_remote_retrieve_body( $r ) { return $r['body']; }

function run_head() {
	$GLOBALS['action'] = 'wp_head';
	$h = $GLOBALS['hooks']['wp_head'];
	ksort( $h );
	ob_start();
	echo '<script data-no-optimize="1" data-no-defer="1">window.dataLayer=window.dataLayer||[];dataLayer.push({"page_type":"home"});</script>' . "\n"; // site-ga4-datalayer.php, ưu tiên 1
	foreach ( $h as $p => $fs ) {
		foreach ( $fs as $f ) {
			if ( 10 === $p && 'wpcode' === $f ) { echo wp_unslash( get_option( 'ihaf_insert_header' ) ); continue; } // WPCode: global-output.php
			if ( 999999 === $p && 'gla' === $f ) { echo gla_output(); continue; }                                   // Google Listings & Ads: GlobalSiteTag.php
			call_user_func( $f );
		}
	}
	$GLOBALS['action'] = '';
	return ob_get_clean();
}
function gla_output() {
	return "\n\t\t<!-- Global site tag (gtag.js) - Google Ads: AW-1000000001 - Google for WooCommerce -->\n\t\t<script async src=\"https://www.googletagmanager.com/gtag/js?id=AW-1000000001\"></script>\n\t\t<script>\n\t\t\twindow.dataLayer = window.dataLayer || [];\n\t\t\tfunction gtag() { dataLayer.push(arguments); }\n\t\t\tgtag( 'consent', 'default', { ad_user_data: 'denied' } );\n\t\t\tgtag('js', new Date());\n\t\t\tgtag('set', 'developer_id.dOGY3NW', true);\n\t\t\tgtag(\"config\", \"AW-1000000001\", { \"groups\": \"GLA\", \"send_page_view\": false });\n\t\t</script>\n\n";
}

$hdr = file_get_contents( $fx . 'ihaf_insert_header.raw' );
$GLOBALS['options']['ihaf_insert_header'] = rtrim( $hdr, "\n" );
$GLOBALS['fixture_for'] = array(
	'https://www.googletagmanager.com/gtm.js?id=GTM-AAAA111' => $fx . 'gtm-AAAA111-resource.js',
	'https://www.googletagmanager.com/gtm.js?id=GTM-BBBB222' => $fx . 'gtm-BBBB222-resource.js',
);
$verdict_ok = array( 'ok' => true, 'why' => 'Google tag G-TEST000001 chạy ở mọi trang', 'at' => 1 );

switch ( $scenario ) {
	case 'ok':      // container có Google tag: bỏ gtag trực tiếp
		$GLOBALS['transients']['gtvd_gtm_v_GTM-AAAA111_G-TEST000001'] = $verdict_ok;
		break;
	case 'wait0':   // không hẹn giờ
		define( 'GTVD_GTM_WAIT_MS', 0 );
		$GLOBALS['transients']['gtvd_gtm_v_GTM-AAAA111_G-TEST000001'] = $verdict_ok;
		break;
	case 'unknown': // chưa có verdict: giữ gtag, hẹn kiểm
		break;
	case 'now':     // giỏ hàng
		$GLOBALS['flags']['cart'] = true;
		$GLOBALS['transients']['gtvd_gtm_v_GTM-AAAA111_G-TEST000001'] = $verdict_ok;
		break;
	case 'cleaned': // option đã bị người khác dọn sạch snippet, ID ép bằng hằng số
		define( 'GTVD_GTM_ID', 'GTM-BBBB222' );
		$GLOBALS['options']['ihaf_insert_header'] = "<meta name=\\'dmca-site-verification\\' content=\\'x\\' />";
		break;
	case 't7':      // snippet đã đổi sang container mới, verdict của T7 còn trống
		$GLOBALS['options']['ihaf_insert_header'] = str_replace( 'GTM-AAAA111', 'GTM-BBBB222', $GLOBALS['options']['ihaf_insert_header'] );
		$GLOBALS['transients']['gtvd_gtm_v_GTM-BBBB222_G-TEST000001'] = array( 'ok' => false, 'why' => 'container rỗng, chưa có tag nào' );
		break;
	case 'badsnip': // snippet GTM dạng thẻ src (regex không bóc): file phải tự tắt
		$GLOBALS['options']['ihaf_insert_header'] = "<meta name=\\'a\\' content=\\'b\\' />\n<script async src=\\\"https://www.googletagmanager.com/gtm.js?id=GTM-AAAA111\\\"></script>";
		break;
	case 'admin':
		$GLOBALS['flags']['admin'] = true;
		break;
	case 'nog':     // gtm-3010: snippet T7, option không còn gtag G
		$GLOBALS['options']['ihaf_insert_header'] = preg_replace( '~<script[^>]*googletagmanager\.com/gtag/js\?id=G-[^>]*></script>\s*<script[^>]*>(?:(?!</script>).)*?gtag\((?:(?!</script>).)*?</script>\s*~is', '', str_replace( 'GTM-AAAA111', 'GTM-BBBB222', $GLOBALS['options']['ihaf_insert_header'] ) );
		break;
}

require getenv( 'LOADER' ) ?: __DIR__ . '/../templates/gtm-delay-loader-option.php';
// Đăng ký giả lập đầu ra của WPCode và GLA vào đúng ưu tiên của chúng.
$GLOBALS['hooks']['wp_head'][10][]     = 'wpcode';
$GLOBALS['hooks']['wp_head'][999999][] = 'gla';

$res = array();
$ok  = function ( $name, $cond ) use ( &$res ) { $res[] = array( $name, (bool) $cond ); };

if ( 'container' === $scenario ) {
	$k9 = file_get_contents( $fx . 'gtm-AAAA111-resource.js' );
	$t7 = file_get_contents( $fx . 'gtm-BBBB222-resource.js' );
	$r1 = gtvd_gtm_check_container( $k9, 'G-TEST000001' );
	$ok( 'AAAA111 có Google tag mọi trang => ok', $r1['ok'] );
	$r2 = gtvd_gtm_check_container( $t7, 'G-TEST000001' );
	$ok( 'BBBB222 rỗng => không ok (' . $r2['why'] . ')', ! $r2['ok'] && false !== strpos( $r2['why'], 'rỗng' ) );
	$r3 = gtvd_gtm_check_container( $k9, 'G-KHAC' );
	$ok( 'ID đo lường khác => không ok', ! $r3['ok'] );
	$r4 = gtvd_gtm_check_container( str_replace( '"vtp_tagId":"G-TEST000001","tag_id":3', '"vtp_tagId":"G-TEST000001","vtp_configSettingsTable":["list",["map","parameter","send_page_view","parameterValue","false"]],"tag_id":3', $k9 ), 'G-TEST000001' );
	$ok( 'send_page_view=false => không ok', ! $r4['ok'] );
	$r5 = gtvd_gtm_check_container( str_replace( '"rules":[[["if",0],["add",0]]', '"rules":[[["if",0,1],["add",0]]', $k9 ), 'G-TEST000001' );
	$ok( 'trigger có thêm điều kiện => không ok', ! $r5['ok'] );
	$r6 = gtvd_gtm_check_container( 'rác', 'G-TEST000001' );
	$ok( 'dữ liệu hỏng => không ok, không lỗi', ! $r6['ok'] );
	gtvd_gtm_verify( 'GTM-AAAA111', 'G-TEST000001' );
	$ok( 'verify() ghi transient ok', ! empty( $GLOBALS['transients']['gtvd_gtm_v_GTM-AAAA111_G-TEST000001']['ok'] ) );
	gtvd_gtm_verify( 'GTM-BBBB222', 'G-TEST000001' );
	$ok( 'verify() T7 ghi transient không ok + log cảnh báo', empty( $GLOBALS['transients']['gtvd_gtm_v_GTM-BBBB222_G-TEST000001']['ok'] ) && false !== strpos( file_get_contents( $logfile ), 'CẢNH BÁO' ) );
} elseif ( 'cli' === $scenario ) {
	$GLOBALS['options']['ihaf_insert_header'] = $hdr;
	$ok( 'ngoài wp_head (WP-CLI, REST) nhận giá trị gốc', get_option( 'ihaf_insert_header' ) === $hdr );
} else {
	$head = run_head();
	file_put_contents( $outdir . '/' . $scenario . '.html', $head );
	$log = file_get_contents( $logfile );
	$gtm_inline = substr_count( $head, 'googletagmanager.com/gtm.js' );
	switch ( $scenario ) {
		case 'ok':
		case 'wait0':
			$ok( 'còn đúng 1 thẻ DMCA', 1 === substr_count( $head, 'dmca-site-verification' ) );
			$ok( 'gtag G-xxx trực tiếp đã bỏ', false === strpos( $head, 'gtag/js?id=G-' ) && false === strpos( $head, "gtag('config', 'G-" ) );
			$ok( 'không còn snippet GTM cũ', false === strpos( $head, "dl=l!=" ) );
			$ok( 'loader có ID container lấy từ option', false !== strpos( $head, "'GTM-AAAA111'," ) );
			$ok( 'ghi chú gtag=drop', false !== strpos( $head, 'gtag=drop' ) );
			$ok( 'thẻ AW đã thành meta gtvd-defer-src', false !== strpos( $head, '<meta name="gtvd-defer-src" content="https://www.googletagmanager.com/gtag/js?id=AW-1000000001">' ) && false === strpos( $head, '<script async src="https://www.googletagmanager.com/gtag/js?id=AW' ) );
			$ok( 'lệnh gtag() inline của GLA còn nguyên', false !== strpos( $head, 'gtag("config", "AW-1000000001"' ) && false !== strpos( $head, 'function gtag()' ) );
			$ok( 'AW và GTM cùng mốc, async=false để AW thực thi trước, có dự phòng', false !== strpos( $head, 'j.async=!n' ) && false !== strpos( $head, 's(v.content,0,1)});s(u,c,1)}' ) && false !== strpos( $head, 'setTimeout(g,t)' ) && false !== strpos( $head, 'setTimeout(a,4000)' ) && false === strpos( $head, 't-600' ) );
			$ok( 'thứ tự: page_type trước loader', strpos( $head, 'page_type' ) < strpos( $head, 'gtvd-gtm-delay' ) );
			$ok( 'số ms hẹn giờ đúng (' . GTVD_GTM_WAIT_MS . ')', false !== strpos( $head, "'GTM-AAAA111'," . GTVD_GTM_WAIT_MS . ');' ) );
			$ok( 'không ghi log lỗi', '' === trim( $log ) );
			break;
		case 'unknown':
			$ok( 'gtag trực tiếp được giữ', false !== strpos( $head, 'gtag/js?id=G-TEST000001' ) );
			$ok( 'snippet GTM cũ đã bỏ, loader hoãn thay vào', false !== strpos( $head, 'gtag=keep' ) && false === strpos( $head, "dl=l!='dataLayer'" ) );
			$ok( 'hẹn kiểm container bằng WP-Cron', 1 === count( $GLOBALS['scheduled'] ) && 'gtvd_gtm_verify' === $GLOBALS['scheduled'][0][0] );
			$ok( 'giữ gtag G thì thẻ AW của GLA để nguyên (gtag.js của G tự nạp AW)', false !== strpos( $head, '<script async src="https://www.googletagmanager.com/gtag/js?id=AW-1000000001"></script>' ) && false === strpos( $head, '<meta name="gtvd-defer-src"' ) );
			break;
		case 'now':
			$ok( 'nạp ngay: snippet chuẩn, không hẹn giờ', false !== strpos( $head, 'gtvd-gtm-delay: now' ) && false === strpos( $head, 'addEventListener' ) );
			$ok( 'thẻ AW của GLA giữ nguyên', false !== strpos( $head, '<script async src="https://www.googletagmanager.com/gtag/js?id=AW-1000000001"></script>' ) && false === strpos( $head, 'gtvd-defer-src' ) );
			$ok( 'đúng 1 lần nạp gtm.js', 1 === $gtm_inline );
			break;
		case 'cleaned':
			$ok( 'ID container lấy từ hằng số T7', false !== strpos( $head, "'GTM-BBBB222'," ) );
			$ok( 'thẻ DMCA còn nguyên', false !== strpos( $head, 'dmca-site-verification' ) );
			break;
		case 't7':
			$ok( 'loader theo snippet mới BBBB222', false !== strpos( $head, "'GTM-BBBB222'," ) && false === strpos( $head, 'AAAA111' ) );
			$ok( 'container T7 rỗng nên giữ gtag', false !== strpos( $head, 'gtag=keep' ) && false !== strpos( $head, 'gtag/js?id=G-TEST000001' ) );
			break;
		case 'badsnip':
			$ok( 'bóc không sạch: file tự tắt, giữ nguyên option', false !== strpos( $head, 'gtm.js?id=GTM-AAAA111' ) && false === strpos( $head, 'gtvd-gtm-delay' ) );
			$ok( 'ghi cảnh báo error_log', false !== strpos( $log, 'Không tìm thấy ID container' ) || false !== strpos( $log, 'Không bóc sạch' ) );
			break;
		case 'nog':
			$ok( 'loader T7, ' . GTVD_GTM_WAIT_MS . ' ms', false !== strpos( $head, "'GTM-BBBB222'," . GTVD_GTM_WAIT_MS . ');' ) );
			$ok( 'ghi chú gtag=none', false !== strpos( $head, 'gtag=none' ) );
			$ok( 'không có gtag G', false === strpos( $head, 'gtag/js?id=G-' ) );
			$ok( 'thẻ AW thành meta gtvd-defer-src', false !== strpos( $head, '<meta name="gtvd-defer-src" content="https://www.googletagmanager.com/gtag/js?id=AW-1000000001">' ) && false === strpos( $head, '<script async src="https://www.googletagmanager.com/gtag/js?id=AW' ) );
			$ok( 'còn đúng 1 thẻ DMCA', 1 === substr_count( $head, 'dmca-site-verification' ) );
			$ok( 'không ghi log lỗi', '' === trim( $log ) );
			break;
		case 'admin':
			$ok( 'wp-admin: không đăng ký bộ lọc, option nguyên', false !== strpos( get_option( 'ihaf_insert_header' ), 'GTM-AAAA111' ) );
			break;
	}
}
foreach ( $res as $r ) {
	echo ( $r[1] ? 'ĐẠT ' : 'LỖI ' ) . $scenario . ': ' . $r[0] . "\n";
}
unlink( $logfile );
exit( count( array_filter( $res, function ( $r ) { return ! $r[1]; } ) ) ? 1 : 0 );
