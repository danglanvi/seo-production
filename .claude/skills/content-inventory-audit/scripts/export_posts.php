<?php
/**
 * Xuất bài viết đã publish kèm chuyên mục, danh mục chính, mô tả SEO, H2 (chỉ đọc, không ghi gì).
 * Dùng: wp eval-file export_posts.php > posts.json
 * Danh mục chính: meta Rank Math, không có thì meta Yoast. URI Permalink Manager và ngôn ngữ WPML ghi kèm nếu site có plugin đó.
 */
$pm   = get_option( 'permalink-manager' );
$uris = get_option( 'permalink-manager-uris' );
$out  = array(
	'pm_settings'         => array(
		'auto_update_uris'   => $pm['general']['auto_update_uris'] ?? null,
		'redirect'           => $pm['general']['redirect'] ?? null,
		'canonical_redirect' => $pm['general']['canonical_redirect'] ?? null,
		'old_slug_redirect'  => $pm['general']['old_slug_redirect'] ?? null,
	),
	'permalink_structure' => get_option( 'permalink_structure' ),
	'pm_post_tpl'         => $pm['permastructures']['post_types']['post'] ?? ( get_option( 'permalink-manager-permastructs' )['post_types']['post'] ?? null ),
	'cats'                => array(),
	'posts'               => array(),
);
foreach ( get_terms( array( 'taxonomy' => 'category', 'hide_empty' => false ) ) as $c ) {
	$out['cats'][] = array(
		'id' => $c->term_id, 'slug' => $c->slug, 'name' => $c->name, 'parent' => $c->parent, 'count' => $c->count,
		'desc' => wp_strip_all_tags( $c->description ),
		'lang' => apply_filters( 'wpml_element_language_code', null, array( 'element_id' => $c->term_id, 'element_type' => 'category' ) ),
	);
}
$ids = get_posts( array( 'post_type' => 'post', 'post_status' => 'publish', 'numberposts' => -1, 'fields' => 'ids', 'suppress_filters' => true ) );
foreach ( $ids as $id ) {
	$c = get_post_field( 'post_content', $id, 'raw' );
	preg_match_all( '#<h2[^>]*>(.*?)</h2>#is', $c, $m );
	$h2      = array_slice( array_map( function ( $x ) { return trim( wp_strip_all_tags( $x ) ); }, $m[1] ), 0, 8 );
	$lang    = apply_filters( 'wpml_post_language_details', null, $id );
	$primary = (int) get_post_meta( $id, 'rank_math_primary_category', true );
	if ( ! $primary ) {
		$primary = (int) get_post_meta( $id, '_yoast_wpseo_primary_category', true );
	}
	$desc = (string) get_post_meta( $id, 'rank_math_description', true );
	if ( '' === $desc ) {
		$desc = (string) get_post_meta( $id, '_yoast_wpseo_metadesc', true );
	}
	$out['posts'][] = array(
		'id' => $id, 'title' => get_the_title( $id ), 'url' => get_permalink( $id ), 'pm_uri' => $uris[ $id ] ?? null,
		'lang' => is_array( $lang ) ? ( $lang['language_code'] ?? '' ) : '',
		'date' => get_post_field( 'post_date', $id ), 'modified' => get_post_field( 'post_modified', $id ),
		'cats' => wp_list_pluck( get_the_category( $id ), 'slug' ),
		'primary' => $primary,
		'robots' => get_post_meta( $id, 'rank_math_robots', true ),
		'desc' => $desc,
		'excerpt' => wp_trim_words( wp_strip_all_tags( get_post_field( 'post_excerpt', $id ) ?: $c ), 60, '' ),
		'h2' => $h2,
	);
}
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
