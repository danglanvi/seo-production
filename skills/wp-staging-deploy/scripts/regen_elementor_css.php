<?php
/* Sinh lại file CSS Elementor từng tài liệu, ghi đè tại chỗ. Không xoá cache CSS toàn site.
 * Biến: IDS="12,34" (tuỳ chọn; trống = mọi tài liệu Elementor publish/private, cả elementor_library, và kit đang dùng), DRY=1 mặc định.
 * Sửa output widget thì xoá _elementor_element_cache của tài liệu đó trước khi chạy.
 * Chạy: sudo -u www HOME=/tmp/wpcli-home IDS=... DRY=0 <php> /usr/local/bin/wp --path=<root> eval-file regen_elementor_css.php */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
global $wpdb;
$dry = getenv( 'DRY' ) !== '0';
if ( getenv( 'IDS' ) ) {
	$ids = array_map( 'intval', explode( ',', getenv( 'IDS' ) ) );
} else {
	$ids = $wpdb->get_col(
		"SELECT p.ID FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id = p.ID AND m.meta_key = '_elementor_edit_mode' AND m.meta_value = 'builder'
		 WHERE p.post_status IN ('publish','private') AND p.post_type <> 'revision' ORDER BY p.ID"
	);
	array_unshift( $ids, (int) get_option( 'elementor_active_kit' ) );
}
$ids = array_values( array_filter( array_unique( array_map( 'intval', $ids ) ) ) );
$log = [ 'dry' => $dry, 'n' => count( $ids ), 'fail' => [] ];
if ( ! $dry ) {
	foreach ( $ids as $id ) {
		try {
			( new \Elementor\Core\Files\CSS\Post( $id ) )->update();
		} catch ( \Throwable $e ) {
			$log['fail'][ $id ] = $e->getMessage();
		}
	}
}
echo wp_json_encode( $log, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
