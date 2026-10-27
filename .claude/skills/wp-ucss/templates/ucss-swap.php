<?php
/**
 * Plugin Name: wp-ucss swap
 * Description: Đổi link CSS gộp của LiteSpeed sang bản gọn đã kiểm trong wp-content/ucss/. Chỉ đổi khi map.php có đúng md5 file gộp và đúng path trang. Không có thì giữ link gốc.
 * Tắt nhanh: tạo file wp-content/ucss/OFF rồi purge các trang. Gỡ hẳn: chuyển file này ra khỏi mu-plugins (vào thư mục quarantine) rồi purge.
 */

defined( 'ABSPATH' ) || exit;

// Chạy sau mọi bước tối ưu của LiteSpeed, trước khi trả trang và lưu cache (core.cls.php, litespeed_buffer_after).
add_filter( 'litespeed_buffer_after', function ( $html ) {
	$sub = 'ucss'; // Thư mục CSS gọn trong wp-content, khớp ucss_dir của site.json. deploy_ucss.sh MU=1 kiểm dòng này.
	if ( ! is_string( $html ) || false === strpos( $html, '/litespeed/css/' ) || false === stripos( $html, '</html>' ) ) {
		return $html;
	}
	if ( is_user_logged_in() || is_admin() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
		return $html;
	}
	$dir = WP_CONTENT_DIR . '/' . $sub;
	if ( file_exists( $dir . '/OFF' ) || ! is_file( $dir . '/map.php' ) ) {
		return $html;
	}
	$map = include $dir . '/map.php';
	if ( empty( $map['files'] ) || ! is_array( $map['files'] ) ) {
		return $html;
	}
	$path = isset( $_SERVER['REQUEST_URI'] ) ? (string) strtok( $_SERVER['REQUEST_URI'], '?#' ) : '';

	return preg_replace_callback(
		'#<link\b[^>]*?\bhref=(["\'])((?:https?:)?//[^"\']*?)?/wp-content/litespeed/css/([0-9a-f]{32})\.css(\?[^"\']*)?\1[^>]*>#',
		function ( $m ) use ( $map, $path, $dir, $sub ) {
			$h = $m[3];
			if ( empty( $map['files'][ $h ]['p'][ $path ] ) ) {
				return $m[0];
			}
			$f = $map['files'][ $h ]['f'];
			if ( ! preg_match( '#^[0-9a-f]{32}\.[0-9a-f]{8}\.css$#', $f ) || ! is_file( $dir . '/' . $f ) ) {
				return $m[0];
			}
			$orig = $m[2] . '/wp-content/litespeed/css/' . $h . '.css' . ( isset( $m[4] ) ? $m[4] : '' );
			$tag  = str_replace( $m[1] . $orig . $m[1], $m[1] . $m[2] . '/wp-content/' . $sub . '/' . $f . $m[1], $m[0] );
			// Bản gọn lỗi tải thì trình duyệt nạp lại file gộp gốc.
			if ( false === stripos( $tag, 'onerror=' ) ) {
				$tag = preg_replace( '#\s*/?>$#', ' data-ucss="1" onerror="this.onerror=null;this.href=\'' . esc_attr( $orig ) . '\'"$0', $tag, 1 );
			}
			return $tag;
		},
		$html
	);
}, 99 );
