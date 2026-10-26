<?php
/**
 * Xuất dữ liệu tra cứu cho build_tax_plan.py, chain_check.py và pick_target.py (chỉ đọc, không ghi gì).
 * Dùng: PART=<phần> OUT=<phần>.json wp eval-file export_tax_redirects.php
 *       Không đặt OUT thì in JSON ra stdout (chạy với -d display_errors=0 để warning PHP không lẫn vào).
 * PART:
 *   cats   chuyên mục: id, slug, name, parent, count, path        → build_tax_plan.py diagnose --cats
 *   rules  bảng redirect Rank Math: id, sources, to, code, status → chain_check.py --rules, diagnose --rules
 *   uris   option permalink-manager-uris ("tax-<id>", "<id bài>" → uri) → chain_check.py --uris
 *   terms  đường dẫn mọi trang term công khai và archive post type → pick_target.py --terms, chain_check.py --terms
 *   cpt    đường dẫn archive của post type                        → diagnose --cpt-archives
 * Site không có bảng Rank Math: rules trả [] và báo ở STDERR. Plugin redirect khác: xuất tay theo cùng dạng.
 * Rule 410 và 451 của Rank Math có url_to rỗng: giữ nguyên, chain_check.py không coi là đích trang chủ.
 * Mã thoát: 0 xong · 2 PART sai.
 */
global $wpdb;
$part = getenv( 'PART' );
$path = function ( $u ) {
	return ( ! $u || is_wp_error( $u ) ) ? null : wp_parse_url( $u, PHP_URL_PATH );
};
$out  = array();
switch ( $part ) {
	case 'cats':
		$cats = get_terms( array( 'taxonomy' => 'category', 'hide_empty' => false ) );
		foreach ( is_array( $cats ) ? $cats : array() as $c ) {
			$out[] = array(
				'id'     => (int) $c->term_id,
				'slug'   => $c->slug,
				'name'   => html_entity_decode( $c->name, ENT_QUOTES, 'UTF-8' ),
				'parent' => (int) $c->parent,
				'count'  => (int) $c->count,
				'path'   => $path( get_term_link( $c ) ),
			);
		}
		break;
	case 'rules':
		$t = $wpdb->prefix . 'rank_math_redirections';
		if ( $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $t ) ) !== $t ) {
			fwrite( STDERR, "Không có bảng $t: site không dùng Rank Math Redirections\n" );
			break;
		}
		foreach ( $wpdb->get_results( "SELECT id, sources, url_to, header_code, status FROM $t", ARRAY_A ) as $r ) {
			$src   = maybe_unserialize( $r['sources'] );
			$out[] = array(
				'id'      => (int) $r['id'],
				'sources' => array_map(
					function ( $s ) {
						return array( 'pattern' => $s['pattern'] ?? '', 'comparison' => $s['comparison'] ?? 'exact' );
					},
					is_array( $src ) ? array_values( $src ) : array()
				),
				'to'      => (string) $r['url_to'],
				'code'    => (int) $r['header_code'],
				'status'  => $r['status'],
			);
		}
		break;
	case 'uris':
		$out = (object) get_option( 'permalink-manager-uris', array() );
		break;
	case 'terms':
	case 'cpt':
		foreach ( get_post_types( array( 'public' => true, 'has_archive' => true ) ) as $pt ) {
			$out[] = $path( get_post_type_archive_link( $pt ) );
		}
		if ( 'terms' === $part ) {
			foreach ( get_taxonomies( array( 'public' => true ) ) as $tax ) {
				$terms = get_terms( array( 'taxonomy' => $tax, 'hide_empty' => false ) );
				foreach ( is_array( $terms ) ? $terms : array() as $term ) {
					$out[] = $path( get_term_link( $term ) );
				}
			}
		}
		$out = array_values( array_unique( array_filter( $out ) ) );
		break;
	default:
		fwrite( STDERR, "PART phải là cats, rules, uris, terms hoặc cpt\n" );
		exit( 2 );
}
$json = wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE );
if ( getenv( 'OUT' ) ) {
	file_put_contents( getenv( 'OUT' ), $json );
	echo 'OK ', $part, ' → ', getenv( 'OUT' ), "\n";
} else {
	echo $json, "\n";
}
