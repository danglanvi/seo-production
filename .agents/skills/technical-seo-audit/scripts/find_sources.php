<?php
// Dò nơi chứa từng chuỗi trong DB WordPress: post_content, postmeta (gồm _elementor_data, menu), options, term, usermeta.
// Chỉ đọc. Chạy: PAT='a|b|c' wp eval-file find_sources.php > sources.json
// Gốc: script audit link 18/10/2026. Bản này tự thêm chuỗi có dấu / thoát (\/), vì _elementor_data lưu JSON
// với dấu / dạng \/ nên LIKE theo chuỗi thường không thấy.
global $wpdb;
$pats = array();
foreach ( array_filter( explode( '|', (string) getenv( 'PAT' ) ) ) as $p ) {
	$pats[] = $p;
	if ( false !== strpos( $p, '/' ) ) {
		$pats[] = str_replace( '/', '\\/', $p );
	}
}
$out = array();
foreach ( array_unique( $pats ) as $p ) {
	$like = '%' . $wpdb->esc_like( $p ) . '%';
	$r    = array();
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT ID, post_type, post_status, post_name FROM {$wpdb->posts} WHERE post_content LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$c           = get_post_field( 'post_content', $x->ID, 'raw' );
		$r['post'][] = array( $x->ID, $x->post_type, $x->post_status, $x->post_name, substr_count( $c, $p ) );
	}
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT m.post_id, m.meta_key, p.post_type, p.post_status, p.post_name, m.meta_value FROM {$wpdb->postmeta} m LEFT JOIN {$wpdb->posts} p ON p.ID=m.post_id WHERE m.meta_value LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$r['meta'][] = array( (int) $x->post_id, $x->meta_key, $x->post_type, $x->post_status, $x->post_name, substr_count( $x->meta_value, $p ), substr_count( $x->meta_value, str_replace( '/', '\\/', $p ) ) );
	}
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT option_name, option_value FROM {$wpdb->options} WHERE option_value LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$r['opt'][] = array( $x->option_name, substr_count( $x->option_value, $p ) );
	}
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT term_id, taxonomy FROM {$wpdb->term_taxonomy} WHERE description LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$r['term'][] = array( (int) $x->term_id, $x->taxonomy );
	}
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT term_id, meta_key FROM {$wpdb->termmeta} WHERE meta_value LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$r['termmeta'][] = array( (int) $x->term_id, $x->meta_key );
	}
	$rows = $wpdb->get_results( $wpdb->prepare( "SELECT user_id, meta_key FROM {$wpdb->usermeta} WHERE meta_value LIKE %s", $like ) );
	foreach ( $rows as $x ) {
		$r['usermeta'][] = array( (int) $x->user_id, $x->meta_key );
	}
	$out[ $p ] = (object) $r;
}
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT );
