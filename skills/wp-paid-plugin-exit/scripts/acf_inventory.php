<?php
/* Kiểm kê ACF Pro trước khi chuyển sang Secure Custom Fields (SCF): nhóm trường, loại trường Pro, trang Options, block ACF,
 * số bài có dữ liệu cho từng nhóm. Chỉ đọc. In JSON. Chạy khi ACF Pro còn bật. */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
if ( ! function_exists( 'acf_get_field_groups' ) ) { echo wp_json_encode( array( 'error' => 'ACF không chạy' ) ), "\n"; return; }
global $wpdb;
$pro   = array( 'repeater', 'flexible_content', 'gallery', 'clone' );
$out   = array( 'acf_version' => defined( 'ACF_VERSION' ) ? ACF_VERSION : null, 'pro' => defined( 'ACF_PRO' ), 'groups' => array(), 'pro_types' => array(), 'options_pages' => array(), 'blocks' => array() );
$count = function ( $fields ) use ( &$count, $pro, &$out ) {
	foreach ( (array) $fields as $f ) {
		if ( in_array( $f['type'], $pro, true ) ) { $out['pro_types'][ $f['type'] ] = ( $out['pro_types'][ $f['type'] ] ?? 0 ) + 1; }
		$count( $f['sub_fields'] ?? array() );
		foreach ( (array) ( $f['layouts'] ?? array() ) as $l ) { $count( $l['sub_fields'] ?? array() ); }
	}
};
foreach ( acf_get_field_groups() as $g ) {
	$fields = acf_get_fields( $g );
	$count( $fields );
	$names = wp_list_pluck( (array) $fields, 'name' );
	$used  = $names ? (int) $wpdb->get_var( "SELECT COUNT(DISTINCT post_id) FROM {$wpdb->postmeta} WHERE meta_key IN ('" . implode( "','", array_map( 'esc_sql', $names ) ) . "')" ) : 0;
	$out['groups'][] = array( 'key' => $g['key'], 'title' => $g['title'], 'active' => (bool) $g['active'], 'fields' => count( (array) $fields ), 'posts_with_data' => $used, 'local' => $g['local'] ?? '' );
}
if ( function_exists( 'acf_get_options_pages' ) ) { $out['options_pages'] = array_keys( (array) acf_get_options_pages() ); }
if ( function_exists( 'acf_get_block_types' ) ) { $out['blocks'] = array_keys( (array) acf_get_block_types() ); }
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
