<?php
/**
 * Plugin Name: 301 ảnh đổi tên
 * Description: URL ảnh tên cũ trả 404 thì 301 sang tên mới theo bảng anh-301.json cùng thư mục. Chỉ đọc bảng khi request là 404.
 *
 * Đặt file này và anh-301.json vào wp-content/mu-plugins/. Bảng: {"/wp-content/uploads/a/cu.webp": "/wp-content/uploads/a/moi.webp"}.
 * Server phải chuyển request file không tồn tại vào WordPress (references/doi-ten-anh-da-dang.md bước 6).
 * Tắt: chuyển file ra khỏi mu-plugins/ rồi purge cache.
 */
defined( 'ABSPATH' ) || exit;

add_action( 'template_redirect', function () {
	if ( ! is_404() ) {
		return;
	}
	$path = rawurldecode( (string) wp_parse_url( (string) ( $_SERVER['REQUEST_URI'] ?? '' ), PHP_URL_PATH ) );
	$file = __DIR__ . '/anh-301.json';
	$map  = is_file( $file ) ? json_decode( (string) file_get_contents( $file ), true ) : null;
	if ( is_array( $map ) && isset( $map[ $path ] ) ) {
		wp_safe_redirect( home_url( $map[ $path ] ), 301, 'anh-301' );
		exit;
	}
}, 1 );
