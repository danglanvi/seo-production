<?php
/**
 * Plugin Name: Security hardening (wp-security-hardening)
 * Description: Bảo mật mức ứng dụng. Lớp này không thay Wordfence. Lớp vẫn chạy khi đổi theme hoặc tắt plugin.
 *
 * Mẫu của skill wp-security-hardening, gốc đã chạy trên production 17/10/2026.
 * - Chặn đăng ký, chặn sửa file trong admin, kể cả khi option hoặc wp-config bị đổi.
 * - Tắt XML-RPC, pingback, trackback.
 * - Khách chưa đăng nhập không liệt kê được user: REST /wp/v2/users, ?author=, ?author_name=, trang tác giả chưa có bài, oEmbed, sitemap user.
 * - Ẩn version WordPress và plugin: thẻ generator, tham số ver= của CSS, JS.
 * - Khách vào wp-admin, wp-signup.php, wp-activate.php nhận 404. Các đường dẫn này redirect ra URL trang đăng nhập ẩn.
 * - Contact Form 7: ô bẫy và giới hạn số lần gửi cho mỗi IP. Bình luận: ô bẫy.
 *
 * Site có chức năng thành viên (WooCommerce tài khoản, khoá học): đặt WSH_ALLOW_REGISTRATION = true trong wp-config.php.
 * Giới hạn theo IP dùng REMOTE_ADDR. Nếu site đứng sau proxy (Cloudflare), cấu hình IP thật ở web server trước.
 * Cài: chép vào wp-content/mu-plugins/, chạy php -l trên server, rồi kiểm site. Rollback: chuyển file ra khỏi mu-plugins/.
 */
defined( 'ABSPATH' ) || exit;

const WSH_HP       = '_wsh_hp';
const WSH_CF7_MAX  = 5;
const WSH_CF7_SPAN = 600;

defined( 'DISALLOW_FILE_EDIT' ) || define( 'DISALLOW_FILE_EDIT', true );

function wsh_allow_registration() {
	return defined( 'WSH_ALLOW_REGISTRATION' ) && WSH_ALLOW_REGISTRATION;
}

// Kẻ tấn công hay bật đăng ký và đặt vai trò mặc định là admin để bám trụ.
add_filter( 'pre_option_default_role', fn() => 'subscriber' );
if ( ! wsh_allow_registration() ) {
	add_filter( 'pre_option_users_can_register', fn() => '0' );
}

/* ---------- XML-RPC, pingback, trackback ---------- */

add_filter( 'xmlrpc_enabled', '__return_false' );
add_filter( 'xmlrpc_methods', '__return_empty_array' );
add_filter( 'pings_open', '__return_false', 99 );
add_action( 'pre_ping', function ( &$links ) {
	$links = [];
} );
add_filter( 'wp_headers', function ( $h ) {
	unset( $h['X-Pingback'] );
	return $h;
} );

/* ---------- liệt kê user ---------- */

function wsh_guest() {
	return ! is_user_logged_in();
}

// Priority 99: ACF Pro (ACF_Rest_Api::initialize, priority 10) trả null và xoá kết quả của filter chạy trước nó.
add_filter( 'rest_pre_dispatch', function ( $result, $server, $request ) {
	if ( null === $result && wsh_guest() && preg_match( '#^/wp/v2/users(?:/|$)#', $request->get_route() ) ) {
		return new WP_Error( 'rest_user_cannot_view', 'Không có quyền xem người dùng.', [ 'status' => 401 ] );
	}
	return $result;
}, 99, 3 );

// ?author=1 và ?author_name=x trả 404 cho khách. Bỏ qua request REST (?rest_route=).
add_filter( 'request', function ( $qv ) {
	if ( ! is_admin() && empty( $qv['rest_route'] ) && ( isset( $_GET['author'] ) || isset( $_GET['author_name'] ) ) && wsh_guest() ) {
		return [ 'error' => '404' ];
	}
	return $qv;
} );

// /author/<slug>/ của user chưa có bài công khai: 404. Không cho khách dò tên đăng nhập qua slug tác giả.
add_action( 'template_redirect', function () {
	if ( ! is_author() || ! wsh_guest() ) {
		return;
	}
	$u = get_queried_object();
	if ( ! $u instanceof WP_User || ! count_user_posts( $u->ID, 'post', true ) ) {
		$GLOBALS['wp_query']->set_404();
		status_header( 404 );
		nocache_headers();
	}
}, 1 );

add_filter( 'oembed_response_data', function ( $data ) {
	unset( $data['author_name'], $data['author_url'] );
	return $data;
} );

add_filter( 'wp_sitemaps_add_provider', fn( $provider, $name ) => 'users' === $name ? false : $provider, 10, 2 );

/* ---------- ẩn version ---------- */

remove_action( 'wp_head', 'wp_generator' );
add_filter( 'the_generator', '__return_empty_string' );

// ver=6.2.2 thành ver=<8 ký tự hash>. Hash đổi khi version đổi, nên trình duyệt và cache vẫn tải bản mới.
function wsh_hide_ver( $src ) {
	if ( is_admin() || ! is_string( $src ) || ! str_contains( $src, 'ver=' ) ) {
		return $src;
	}
	$host = wp_parse_url( $src, PHP_URL_HOST );
	if ( $host && wp_parse_url( home_url(), PHP_URL_HOST ) !== $host ) {
		return $src;
	}
	return preg_replace_callback( '/([?&])ver=([^&#]+)/', fn( $m ) => $m[1] . 'ver=' . substr( wp_hash( $m[2] ), 0, 8 ), $src );
}
add_filter( 'style_loader_src', 'wsh_hide_ver', 9999 );
add_filter( 'script_loader_src', 'wsh_hide_ver', 9999 );

/* ---------- đường dẫn làm lộ trang đăng nhập ẩn ---------- */

// - wp-signup.php, wp-activate.php chỉ dùng cho multisite. Trên site đơn, 2 file này redirect ra URL đăng nhập.
// - Khách vào wp-admin bị auth_redirect() chuyển tới URL đăng nhập. Trả 404, trừ admin-ajax.php và admin-post.php.
add_action( 'init', function () {
	$page = $GLOBALS['pagenow'] ?? '';
	$hide = ( ! is_multisite() && ! wsh_allow_registration() && in_array( $page, [ 'wp-signup.php', 'wp-activate.php' ], true ) )
		|| ( is_admin() && wsh_guest() && ! wp_doing_ajax() && ! wp_doing_cron() && 'admin-post.php' !== $page );
	if ( $hide ) {
		status_header( 404 );
		nocache_headers();
		exit;
	}
}, 0 );

/* ---------- form: ô bẫy và giới hạn số lần gửi ---------- */

// Ô bẫy ẩn bằng clip-path, không đẩy ra ngoài màn hình (left:-9999px làm công cụ kiểm giao diện báo tràn ngang).
// Tên bắt đầu bằng "_", nên CF7 không đưa ô này vào dữ liệu form hay email.
function wsh_hp_field() {
	return '<span class="wsh-hp" aria-hidden="true" style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap"><label>Để trống ô này <input type="text" name="' . WSH_HP . '" value="" tabindex="-1" autocomplete="off" style="width:1px;height:1px;padding:0;border:0"></label></span>';
}

function wsh_hp_filled() {
	return ! empty( $_POST[ WSH_HP ] ); // phpcs:ignore WordPress.Security.NonceVerification -- chỉ kiểm ô bẫy có giá trị hay không
}

// Đếm theo IP trong cửa sổ $span giây. Hết lượt thì trả false.
function wsh_rate_ok( $bucket, $max, $span ) {
	$key = 'wsh_rl_' . $bucket . '_' . md5( (string) ( $_SERVER['REMOTE_ADDR'] ?? '' ) );
	$n   = (int) get_transient( $key );
	if ( $n >= $max ) {
		return false;
	}
	set_transient( $key, $n + 1, $span );
	return true;
}

add_filter( 'wpcf7_form_elements', fn( $html ) => $html . wsh_hp_field() );

// CF7 gọi filter này sau bước kiểm dữ liệu, trước khi gửi email. Trả true thì CF7 đánh dấu spam và không gửi.
// Form gửi qua REST bằng JS riêng không có ô bẫy. Ô bẫy chỉ chặn khi có giá trị, nên form đó vẫn qua.
add_filter( 'wpcf7_spam', function ( $spam, $submission = null ) {
	if ( $spam ) {
		return $spam;
	}
	$reason = '';
	if ( wsh_hp_filled() ) {
		$reason = 'Ô bẫy có giá trị.';
	} elseif ( ! wsh_rate_ok( 'cf7', WSH_CF7_MAX, WSH_CF7_SPAN ) ) {
		$reason = 'Quá ' . WSH_CF7_MAX . ' lần gửi trong ' . ( WSH_CF7_SPAN / 60 ) . ' phút từ một IP.';
	}
	if ( '' === $reason ) {
		return false;
	}
	if ( $submission && method_exists( $submission, 'add_spam_log' ) ) {
		$submission->add_spam_log( [ 'agent' => 'wp-security-hardening', 'reason' => $reason ] );
	}
	return true;
}, 20, 2 );

add_action( 'comment_form_after_fields', function () {
	echo wsh_hp_field(); // phpcs:ignore WordPress.Security.EscapeOutput -- HTML tĩnh
} );

add_filter( 'preprocess_comment', function ( $comment ) {
	if ( wsh_guest() && wsh_hp_filled() ) {
		wp_die( 'Bình luận bị chặn.', '', [ 'response' => 403 ] );
	}
	return $comment;
} );

/* ---------- header ---------- */

add_action( 'send_headers', function () {
	header( 'Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()' );
} );
