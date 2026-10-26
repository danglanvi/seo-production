<?php
/**
 * Xuất mọi bài ở mọi post_type và mọi post_status, kèm slug cũ (_wp_old_slug) và URI Permalink Manager (chỉ đọc, không ghi gì).
 * Dùng cho pick_target.py, chain_check.py và build_tax_plan.py.
 * Dùng: OUT=urls.json wp eval-file export_urls.php (không đặt OUT thì in JSON ra stdout)
 * Trường: id, type, status, name, parent, path (chỉ bài publish), pm_uri (nếu site có Permalink Manager), old_slugs.
 * Bài viết (post) publish có thêm cats (slug) và primary (slug danh mục chính Rank Math, rồi Yoast, rồi chuyên mục đầu)
 * để build_tax_plan.py diagnose cộng click theo chuyên mục.
 * Bài nháp giữ URI Permalink Manager cũ: đọc pm_uri để biết URL cũ còn gắn với bài nào.
 */
global $wpdb;
$uris = get_option( 'permalink-manager-uris', array() );
$old  = array();
foreach ( $wpdb->get_results( "SELECT post_id, meta_value FROM {$wpdb->postmeta} WHERE meta_key = '_wp_old_slug'", ARRAY_A ) as $r ) {
	$old[ (int) $r['post_id'] ][] = $r['meta_value'];
}
$skip = "'revision','nav_menu_item','customize_changeset','oembed_cache','user_request','wp_global_styles'";
$rows = $wpdb->get_results( "SELECT ID, post_type, post_status, post_name, post_parent FROM {$wpdb->posts} WHERE post_type NOT IN ($skip)", ARRAY_A );
$out  = array();
foreach ( $rows as $r ) {
	$id   = (int) $r['ID'];
	$path = null;
	if ( 'publish' === $r['post_status'] && 'attachment' !== $r['post_type'] ) {
		$path = wp_parse_url( get_permalink( $id ), PHP_URL_PATH );
	}
	$row = array(
		'id'        => $id,
		'type'      => $r['post_type'],
		'status'    => $r['post_status'],
		'name'      => $r['post_name'],
		'parent'    => (int) $r['post_parent'],
		'path'      => $path,
		'pm_uri'    => isset( $uris[ $id ] ) ? '/' . trim( $uris[ $id ], '/' ) . '/' : null,
		'old_slugs' => $old[ $id ] ?? array(),
	);
	if ( 'post' === $r['post_type'] && null !== $path ) {
		$cats        = wp_get_object_terms( $id, 'category', array( 'fields' => 'slugs' ) );
		$row['cats'] = is_array( $cats ) ? array_values( $cats ) : array();
		$pid         = (int) get_post_meta( $id, 'rank_math_primary_category', true );
		if ( ! $pid ) {
			$pid = (int) get_post_meta( $id, '_yoast_wpseo_primary_category', true );
		}
		$pt             = $pid ? get_term( $pid, 'category' ) : null;
		$row['primary'] = ( $pt && ! is_wp_error( $pt ) ) ? $pt->slug : ( $row['cats'][0] ?? null );
	}
	$out[] = $row;
}
$json = wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE );
if ( getenv( 'OUT' ) ) {
	file_put_contents( getenv( 'OUT' ), $json );
	echo 'OK ', count( $out ), ' dòng → ', getenv( 'OUT' ), "\n";
} else {
	echo $json;
}
