<?php
/**
 * Plugin Name: GTV - Ảnh trong menu tải chậm (mẫu)
 * Description: Ảnh đính kèm in trong menu (mega menu) nhận loading="lazy", bỏ fetchpriority, sizes theo bề rộng hiển thị, src bản nhỏ. Menu desktop ẩn trên mobile nên điện thoại không tải các ảnh này.
 *
 * Mẫu của skill wp-pagespeed (references/plugin-chong-cheo.md mục 4). Nguồn: nhật ký tối ưu site TMĐT mẫu 30/10/2026,
 * 16 ảnh gốc 2000–2560 px trong mega menu tải ngay lúc mở trang, ảnh đầu bị WordPress gắn fetchpriority="high".
 * Đặt vào mu-plugins/ hoặc functions.php của theme con. Đổi 2 hằng số theo bề rộng ảnh menu đo trên trang.
 * Chỉ áp cho ảnh in qua wp_get_attachment_image() trong lúc dựng menu. Ảnh dán thẳng thẻ <img> trong nội dung menu không đổi.
 */
defined( 'ABSPATH' ) || exit;

if ( ! defined( 'GTVD_MENU_IMG_SIZES' ) ) {
	define( 'GTVD_MENU_IMG_SIZES', '300px' ); // bề rộng hiển thị của ảnh trong menu
}
if ( ! defined( 'GTVD_MENU_IMG_SRC_W' ) ) {
	define( 'GTVD_MENU_IMG_SRC_W', 600 ); // bản src dự phòng, khoảng 2 lần bề rộng hiển thị
}

add_filter( 'wp_nav_menu_objects', function ( $items ) {
	$GLOBALS['gtvd_in_nav_menu'] = true;
	return $items;
} );
add_filter( 'wp_nav_menu_items', function ( $items ) {
	$GLOBALS['gtvd_in_nav_menu'] = false;
	return $items;
} );
add_filter( 'wp_get_attachment_image_attributes', function ( $attr, $attachment ) {
	if ( empty( $GLOBALS['gtvd_in_nav_menu'] ) ) {
		return $attr;
	}
	$attr['loading'] = 'lazy';
	unset( $attr['fetchpriority'] );
	$attr['sizes'] = GTVD_MENU_IMG_SIZES;
	$small         = wp_get_attachment_image_src( $attachment->ID, array( GTVD_MENU_IMG_SRC_W, GTVD_MENU_IMG_SRC_W ) );
	if ( $small ) {
		$attr['src'] = $small[0];
	}
	return $attr;
}, 20, 2 );
