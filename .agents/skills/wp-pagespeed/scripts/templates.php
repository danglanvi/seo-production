<?php
/**
 * Liệt kê template của site để chọn URL đại diện (chỉ đọc). Chạy: wp eval-file templates.php
 * In JSON: page template, post type có bài publish, số trang dùng Elementor, kèm URL mẫu mới nhất của mỗi nhóm.
 */
global $wpdb;
$front = (int) get_option( 'page_on_front' );
$blog  = (int) get_option( 'page_for_posts' );
$out   = array(
	'theme' => get_stylesheet(),
	'front' => $front ? array( 'id' => $front, 'template' => get_page_template_slug( $front ) ?: 'default', 'url' => home_url( '/' ) ) : home_url( '/' ),
	'blog'  => $blog ? get_permalink( $blog ) : null,
);

$rows = $wpdb->get_results(
	"SELECT COALESCE(NULLIF(m.meta_value,''),'default') tpl, COUNT(*) n, MAX(p.ID) sample
	 FROM {$wpdb->posts} p LEFT JOIN {$wpdb->postmeta} m ON m.post_id=p.ID AND m.meta_key='_wp_page_template'
	 WHERE p.post_type='page' AND p.post_status='publish' GROUP BY tpl ORDER BY n DESC"
);
foreach ( $rows as $r ) {
	$out['page_templates'][] = array( 'template' => $r->tpl, 'pages' => (int) $r->n, 'sample' => get_permalink( $r->sample ) );
}

$types = $wpdb->get_results(
	"SELECT post_type, COUNT(*) n, MAX(ID) sample FROM {$wpdb->posts}
	 WHERE post_status='publish' AND post_type NOT IN ('page','attachment','revision','nav_menu_item','wp_block','wp_template','wp_template_part','wp_navigation','wp_global_styles','elementor_library','acf-field','acf-field-group')
	 GROUP BY post_type ORDER BY n DESC"
);
foreach ( $types as $t ) {
	$o = get_post_type_object( $t->post_type );
	if ( ! $o || ! $o->public ) {
		continue;
	}
	$out['post_types'][] = array(
		'type'    => $t->post_type,
		'posts'   => (int) $t->n,
		'sample'  => get_permalink( $t->sample ),
		'archive' => $o->has_archive ? get_post_type_archive_link( $t->post_type ) : null,
	);
}

$out['elementor_pages'] = (int) $wpdb->get_var(
	"SELECT COUNT(DISTINCT p.ID) FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id=p.ID
	 WHERE m.meta_key='_elementor_edit_mode' AND m.meta_value='builder' AND p.post_status='publish'"
);

$cat = get_categories( array( 'orderby' => 'count', 'order' => 'DESC', 'number' => 1 ) );
if ( $cat ) {
	$out['category_sample'] = get_category_link( $cat[0] );
}

echo wp_json_encode( $out, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ), "\n";
