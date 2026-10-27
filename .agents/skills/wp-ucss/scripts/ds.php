<?php
// ds.php (wp-ucss): danh sách bài/trang đã đăng cho chon_url.py (path, post_type, danh mục, danh mục chính Yoast, template, độ dài nội dung).
// Chạy: sudo -u <wp_user> <php_bin> <wp_bin> --path=<docroot> eval-file ds.php > ds.json. Post type: biến UCSS_POST_TYPES="post,page,..." (mặc định mọi type public trừ attachment).
$types = getenv( 'UCSS_POST_TYPES' ) ? explode( ',', getenv( 'UCSS_POST_TYPES' ) ) : array_values( array_diff( get_post_types( [ 'public' => true ], 'names' ), [ 'attachment' ] ) );
$out = [];
$q = new WP_Query( [ 'post_type' => $types, 'post_status' => 'publish', 'posts_per_page' => -1, 'fields' => 'ids', 'no_found_rows' => true ] );
foreach ( $q->posts as $id ) {
	$p    = get_post( $id );
	$path = wp_parse_url( get_permalink( $id ), PHP_URL_PATH );
	$cats = $p->post_type === 'post' ? wp_get_post_categories( $id, [ 'fields' => 'slugs' ] ) : [];
	$pc   = get_post_meta( $id, '_yoast_wpseo_primary_category', true );
	$out[] = [ $path, $p->post_type, implode( '|', $cats ), $pc ? get_term( $pc )->slug ?? '' : '', get_page_template_slug( $id ), strlen( $p->post_content ) ];
}
$counts = [];
foreach ( get_post_types( [ 'public' => true ], 'names' ) as $t ) {
	$counts[ $t ] = wp_count_posts( $t )->publish ?? 0;
}
echo json_encode( [ 'types' => $counts, 'cats' => array_map( fn( $t ) => [ $t->slug, $t->name, $t->count, $t->parent ], get_terms( [ 'taxonomy' => 'category', 'hide_empty' => false ] ) ), 'rows' => $out ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES );
