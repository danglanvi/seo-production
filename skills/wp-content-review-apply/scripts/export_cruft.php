<?php
/**
 * Xuất bài, meta ACF và widget có rác HTML để làm sạch. Chỉ đọc DB.
 * OUT=<file json> wp eval-file export_cruft.php
 *   OUT    bắt buộc. File ra, không ghi đè file có sẵn.
 *   LIMIT  tuỳ chọn. Tối đa số bài xuất (thử nhỏ trước).
 * Ra {"posts": [{id, type, slug, content, el, md5c, md5e}], "meta": [{meta_id, post_id, key, value, md5}],
 *     "options": [{key, value, md5}]}. md5 tính trên giá trị thô trong DB: apply_cruft.php so md5 trước khi ghi.
 * Đưa file ra cho cruft_clean.py. Chạy bằng đúng bản PHP của web (references/ghi-an-toan.md mục 2).
 */
global $wpdb;
$out_path = getenv( 'OUT' );
if ( ! $out_path || file_exists( $out_path ) ) {
	fwrite( STDERR, "Cần OUT=<file chưa có>\n" );
	exit( 2 );
}
$limit = (int) getenv( 'LIMIT' );
$pat   = "font-weight: ?400|aria-level=|data-sheets-|<p>&nbsp;</p>|&nbsp;|data-mce-type|docs-internal-guid|dir=.ltr|mso-";
$posts = array();
$last  = 0;
while ( true ) {
	$rows = $wpdb->get_results(
		$wpdb->prepare(
			"SELECT p.ID, p.post_type, p.post_name, p.post_content, m.meta_value AS el FROM {$wpdb->posts} p
			 LEFT JOIN {$wpdb->postmeta} m ON m.post_id = p.ID AND m.meta_key = '_elementor_data'
			 WHERE p.ID > %d AND p.post_status = 'publish' AND p.post_type NOT IN ('revision','nav_menu_item','attachment')
			 AND (p.post_content REGEXP %s OR m.meta_value REGEXP %s) ORDER BY p.ID LIMIT 200",
			$last,
			$pat,
			$pat
		),
		ARRAY_A
	);
	if ( ! $rows ) {
		break;
	}
	foreach ( $rows as $r ) {
		$last    = (int) $r['ID'];
		$el      = is_string( $r['el'] ) ? $r['el'] : '';
		$posts[] = array(
			'id'      => (string) $r['ID'],
			'type'    => $r['post_type'],
			'slug'    => $r['post_name'],
			'content' => $r['post_content'],
			'el'      => '' === $el ? null : $el,
			'md5c'    => md5( $r['post_content'] ),
			'md5e'    => md5( $el ),
		);
		if ( $limit && count( $posts ) >= $limit ) {
			break 2;
		}
	}
}
$meta = array();
$rows = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT m.meta_id, m.post_id, m.meta_key, m.meta_value FROM {$wpdb->postmeta} m JOIN {$wpdb->posts} p ON p.ID = m.post_id
		 WHERE p.post_status = 'publish' AND m.meta_key NOT LIKE %s AND m.meta_value REGEXP %s",
		'\\_%',
		$pat
	),
	ARRAY_A
);
foreach ( $rows as $r ) {
	if ( is_serialized( $r['meta_value'] ) ) {
		continue;
	}
	$meta[] = array(
		'meta_id' => (int) $r['meta_id'],
		'post_id' => (int) $r['post_id'],
		'key'     => $r['meta_key'],
		'value'   => $r['meta_value'],
		'md5'     => md5( $r['meta_value'] ),
	);
}
$options = array();
foreach ( array( 'widget_text', 'widget_custom_html' ) as $o ) {
	$v = get_option( $o );
	if ( is_array( $v ) ) {
		$options[] = array(
			'key'   => $o,
			'value' => $v,
			'md5'   => md5( wp_json_encode( $v ) ),
		);
	}
}
file_put_contents( $out_path, wp_json_encode( array( 'posts' => $posts, 'meta' => $meta, 'options' => $options ) ) );
echo count( $posts ) . ' bài, ' . count( $meta ) . ' meta, ' . count( $options ) . " option\n";
