<?php
/**
 * Chỉ đọc: giá trị thô hiện tại để soạn trang duyệt. Chạy: [IDS=1,2,3] wp eval-file collect.php > current.json
 * Không có IDS thì lấy mọi bài, trang public đang publish (bỏ attachment).
 */
$ids = getenv( 'IDS' ) ? array_map( 'intval', explode( ',', getenv( 'IDS' ) ) ) : null;
if ( ! $ids ) {
	$types = get_post_types( array( 'public' => true ) );
	unset( $types['attachment'] );
	$ids = get_posts( array( 'post_type' => array_values( $types ), 'post_status' => 'publish', 'numberposts' => -1, 'fields' => 'ids', 'suppress_filters' => true ) );
}
$out = array();
foreach ( $ids as $id ) {
	$p = get_post( $id );
	if ( ! $p ) {
		continue;
	}
	$lang = apply_filters( 'wpml_post_language_details', null, $id );
	preg_match_all( '/<h1[^>]*>(.*?)<\/h1>/is', $p->post_content, $h1 );
	$out[] = array(
		'id'         => $id,
		'type'       => $p->post_type,
		'status'     => $p->post_status,
		'url'        => get_permalink( $id ),
		'lang'       => is_array( $lang ) ? $lang['language_code'] : '',
		'wpml_dup'   => get_post_meta( $id, '_icl_lang_duplicate_of', true ),
		'template'   => get_page_template_slug( $id ),
		'post_title' => $p->post_title,
		'post_name'  => $p->post_name,
		'rm_title'   => get_post_meta( $id, 'rank_math_title', true ),
		'rm_desc'    => get_post_meta( $id, 'rank_math_description', true ),
		'rm_focus'   => get_post_meta( $id, 'rank_math_focus_keyword', true ),
		'rm_robots'  => get_post_meta( $id, 'rank_math_robots', true ),
		'h1_in_body' => array_map( 'wp_strip_all_tags', $h1[1] ),
		'elementor'  => (bool) get_post_meta( $id, '_elementor_data', true ),
		'md5'        => md5( $p->post_content ),
		'modified'   => $p->post_modified,
	);
}
$t   = get_option( 'rank-math-options-titles' );
$tpl = array();
foreach ( (array) $t as $k => $v ) {
	if ( is_string( $v ) && preg_match( '/_(title|description)$/', $k ) ) {
		$tpl[ $k ] = $v;
	}
}
echo wp_json_encode( array( 'rank_math_templates' => $tpl, 'items' => $out ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
