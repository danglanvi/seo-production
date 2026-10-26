<?php
/**
 * Đổi cây chuyên mục theo plan.json của build_tax_plan.py. Mặc định DRY: chỉ ghi log, không ghi DB.
 * Chạy: PLAN=plan.json DRY=1 wp eval-file taxonomy_rollout.php > log.json
 * Biến môi trường:
 *   PLAN           đường dẫn plan.json (bắt buộc)
 *   DRY            1 (mặc định) chỉ log; 0 ghi DB. Backup quan hệ chuyên mục và meta trước khi chạy DRY=0.
 *   ALLOW_CHANGED  1: vẫn gán lại bài có chuyên mục khác bản export (dùng cho staging)
 *   TEXTS          JSON {key: {name, desc}}: tên và mô tả đã duyệt
 *   LANG_CODE      mã ngôn ngữ WPML gán cho chuyên mục mới (bỏ trống thì không đụng WPML)
 *   OUT            ghi log JSON ra file này thay cho stdout (stdout có thể lẫn dòng "Success:" của LiteSpeed và warning PHP)
 * Thứ tự: 1 chuyên mục → 2 URI Permalink Manager → 3 noindex → 4 gán bài → 5 redirect → 6 đếm lại, kiểm.
 * Mã thoát: 0 xong · 1 có lỗi trong log.errors (plan không áp dụng được, hoặc kiểm sau ghi lệch).
 */
global $wpdb;
$plan_path = getenv( 'PLAN' );
if ( ! $plan_path || ! is_readable( $plan_path ) ) {
	fwrite( STDERR, "Thiếu PLAN hoặc không đọc được file\n" );
	exit( 2 );
}
$plan  = json_decode( file_get_contents( $plan_path ), true );
$dry   = getenv( 'DRY' ) !== '0';
$allow = getenv( 'ALLOW_CHANGED' ) === '1';
$lang  = getenv( 'LANG_CODE' );
$texts = getenv( 'TEXTS' ) ? json_decode( file_get_contents( getenv( 'TEXTS' ) ), true ) : array();
$log   = array( 'dry' => $dry, 'terms' => array(), 'pm' => array(), 'robots' => array(), 'posts' => array(), 'redirects' => array(), 'deactivated' => array(), 'errors' => array() );

// 1. Chuyên mục: đổi tên, slug, cha, mô tả; tạo chuyên mục mới.
$ids = array();
foreach ( $plan['terms'] as $t ) {
	if ( isset( $texts[ $t['key'] ]['name'] ) ) {
		$t['name'] = $texts[ $t['key'] ]['name'];
	}
	$desc   = $texts[ $t['key'] ]['desc'] ?? null;
	$parent = $t['parent'] ? ( $ids[ $t['parent'] ] ?? 0 ) : 0;
	if ( $t['term_id'] ) {
		$cur = get_term( (int) $t['term_id'], 'category' );
		if ( ! $cur || is_wp_error( $cur ) ) {
			$log['errors'][] = "thiếu chuyên mục {$t['term_id']}";
			continue;
		}
		$ids[ $t['key'] ] = (int) $cur->term_id;
		$chg              = array();
		if ( html_entity_decode( $cur->name, ENT_QUOTES, 'UTF-8' ) !== $t['name'] ) { // WordPress lưu "&" thành "&amp;"
			$chg['name'] = $t['name'];
		}
		if ( $cur->slug !== $t['slug'] ) {
			$chg['slug'] = $t['slug'];
		}
		if ( (int) $cur->parent !== (int) $parent ) {
			$chg['parent'] = (int) $parent;
		}
		if ( null !== $desc && trim( $cur->description ) !== $desc ) {
			$chg['description'] = $desc;
		}
		$log['terms'][] = array( 'id' => (int) $cur->term_id, 'before' => array( $cur->name, $cur->slug, (int) $cur->parent ), 'change' => $chg );
		if ( $chg && ! $dry ) {
			$r = wp_update_term( $cur->term_id, 'category', $chg );
			if ( is_wp_error( $r ) ) {
				$log['errors'][] = "term {$cur->term_id}: " . $r->get_error_message();
			}
		}
		continue;
	}
	$ex = get_term_by( 'slug', $t['slug'], 'category' );
	if ( $ex ) {
		$ids[ $t['key'] ]  = (int) $ex->term_id;
		$log['terms'][]    = array( 'id' => (int) $ex->term_id, 'exists' => $t['slug'] );
		continue;
	}
	$log['terms'][] = array( 'new' => $t['slug'], 'name' => $t['name'], 'parent' => (int) $parent );
	if ( $dry ) {
		$ids[ $t['key'] ] = 'new:' . $t['slug'];
		continue;
	}
	$r = wp_insert_term( $t['name'], 'category', array( 'slug' => $t['slug'], 'parent' => (int) $parent, 'description' => $desc ?? '' ) );
	if ( is_wp_error( $r ) ) {
		$log['errors'][] = "tạo {$t['slug']}: " . $r->get_error_message();
		continue;
	}
	$ids[ $t['key'] ] = (int) $r['term_id'];
	if ( $lang && has_action( 'wpml_set_element_language_details' ) ) {
		do_action( 'wpml_set_element_language_details', array( 'element_id' => $r['term_taxonomy_id'], 'element_type' => 'tax_category', 'trid' => false, 'language_code' => $lang, 'source_language_code' => null ) );
	}
}

// 2. URI chuyên mục trong Permalink Manager. Đọc sau bước 1, vì plugin tự ghi URI "category/…" khi chuyên mục đổi.
$uris = get_option( 'permalink-manager-uris', array() );
foreach ( $plan['terms'] as $t ) {
	if ( empty( $t['uri'] ) || ! is_int( $ids[ $t['key'] ] ?? null ) ) {
		continue;
	}
	$k              = 'tax-' . $ids[ $t['key'] ];
	$log['pm'][]    = array( $k, $uris[ $k ] ?? null, $t['uri'] );
	$uris[ $k ]     = $t['uri'];
}
foreach ( $plan['pm_remove'] as $k ) {
	$log['pm'][] = array( $k, $uris[ $k ] ?? null, null );
	unset( $uris[ $k ] );
}
if ( ! $dry ) {
	update_option( 'permalink-manager-uris', $uris );
}

// 3. Noindex chuyên mục rỗng và chuyên mục trùng post type, để gỡ khỏi sitemap chuyên mục.
foreach ( $plan['noindex_terms'] as $tid ) {
	$cur            = get_term_meta( $tid, 'rank_math_robots', true );
	$has            = is_array( $cur ) && in_array( 'noindex', $cur, true );
	$log['robots'][] = array( $tid, $cur, $has ? 'giữ' : 'noindex' );
	if ( ! $has && ! $dry ) {
		update_term_meta( $tid, 'rank_math_robots', array( 'noindex' ) );
	}
}

// 4. Gán lại bài; chuyển bài sang post type có sẵn.
foreach ( $plan['posts'] as $p ) {
	$post = get_post( $p['id'] );
	if ( ! $post ) {
		$log['posts'][] = array( 'id' => $p['id'], 'st' => 'thiếu bài' );
		continue;
	}
	$cur = wp_get_object_terms( $p['id'], 'category', array( 'fields' => 'slugs' ) );
	sort( $cur );
	$e = array( 'id' => $p['id'], 'before' => $cur );
	if ( $cur !== $p['expect_cats'] ) {
		$e['khac_export'] = $p['expect_cats'];
		if ( ! $allow ) {
			$e['st']        = 'bỏ qua: chuyên mục đã đổi sau bản export';
			$log['posts'][] = $e;
			continue;
		}
	}
	if ( isset( $p['cpt'] ) ) {
		$e['cpt']        = array( $post->post_type, $p['cpt'] );
		$e['url_before'] = get_permalink( $p['id'] );
		if ( ! $dry && $post->post_type !== $p['cpt'] ) {
			$wpdb->update( $wpdb->posts, array( 'post_type' => $p['cpt'] ), array( 'ID' => $p['id'] ) );
			delete_post_meta( $p['id'], 'rank_math_primary_category' );
			clean_post_cache( $p['id'] );
			$e['url_after'] = get_permalink( $p['id'] );
		}
		$log['posts'][] = $e;
		continue;
	}
	$tids       = array_map( function ( $k ) use ( $ids ) { return $ids[ $k ] ?? null; }, $p['cats'] );
	$e['after']   = $p['cats'];
	$e['primary'] = $p['primary'];
	if ( in_array( null, $tids, true ) ) {
		$e['st']        = 'lỗi: thiếu chuyên mục đích';
		$log['posts'][] = $e;
		continue;
	}
	if ( ! $dry ) {
		wp_set_object_terms( $p['id'], array_map( 'intval', $tids ), 'category', false );
		update_post_meta( $p['id'], 'rank_math_primary_category', (int) $ids[ $p['primary'] ] );
		clean_post_cache( $p['id'] );
	}
	$log['posts'][] = $e;
}

// 5. Redirect 301 cho URL chuyên mục cũ; tắt rule cũ (giữ bản ghi, không xoá).
// Đích phải khớp URI Permalink Manager của chuyên mục đích: lệch thì 301 rơi vào URL không tồn tại.
$tbl = $wpdb->prefix . 'rank_math_redirections';
foreach ( $plan['redirects'] as $r ) {
	$sources = array( array( 'ignore' => '', 'pattern' => $r['pattern'], 'comparison' => 'regex' ) );
	$have    = $wpdb->get_var( $wpdb->prepare( "SELECT id FROM $tbl WHERE sources=%s AND status='active'", maybe_serialize( $sources ) ) );
	$e       = array( 'note' => $r['note'], 'to' => $r['to'], 'id' => $have ? (int) $have : null );
	if ( ! empty( $r['to_term'] ) && is_int( $ids[ $r['to_term'] ] ?? null ) ) {
		$want = $uris[ 'tax-' . $ids[ $r['to_term'] ] ] ?? null;
		if ( null === $want || trim( $want, '/' ) !== trim( $r['to'], '/' ) ) {
			$e['dich_lech_uri'] = $want;
			$log['errors'][]    = "redirect {$r['note']}: đích {$r['to']} khác URI Permalink Manager " . ( $want ?? '(chưa có)' );
		}
	}
	if ( ! $have && ! $dry && empty( $log['errors'] ) ) {
		$e['id'] = \RankMath\Redirections\DB::add( array( 'sources' => $sources, 'url_to' => home_url( $r['to'] ), 'header_code' => 301, 'status' => 'active' ) );
	}
	$log['redirects'][] = $e;
}
foreach ( $plan['deactivate_redirects'] as $rid ) {
	$row                = $wpdb->get_row( $wpdb->prepare( "SELECT id, status, sources, url_to FROM $tbl WHERE id=%d", $rid ), ARRAY_A );
	$log['deactivated'][] = $row ? array( $rid, $row['status'], wp_parse_url( $row['url_to'], PHP_URL_PATH ) ) : array( $rid, 'không có' );
	if ( $row && 'active' === $row['status'] && ! $dry && empty( $log['errors'] ) ) {
		\RankMath\Redirections\DB::change_status( array( $rid ), 'inactive' );
	}
}

// 6. Đếm lại, flush rewrite, xoá cache sitemap, purge, kiểm đường dẫn từng chuyên mục.
if ( ! $dry ) {
	$tt = $wpdb->get_col( "SELECT term_taxonomy_id FROM {$wpdb->term_taxonomy} WHERE taxonomy='category'" );
	wp_update_term_count_now( array_map( 'intval', $tt ), 'category' );
	flush_rewrite_rules( false );
	if ( class_exists( '\RankMath\Sitemap\Cache' ) ) {
		\RankMath\Sitemap\Cache::invalidate_storage();
	}
	do_action( 'litespeed_purge_all' );
	$log['after'] = array();
	foreach ( $plan['terms'] as $t ) {
		if ( ! is_int( $ids[ $t['key'] ] ?? null ) ) {
			continue;
		}
		$term   = get_term( $ids[ $t['key'] ], 'category' );
		$path   = trim( (string) wp_parse_url( get_term_link( $term ), PHP_URL_PATH ), '/' );
		$log['after'][] = array( $t['key'], (int) $term->term_id, $term->slug, (int) $term->parent, (int) $term->count, $path );
		if ( ! empty( $t['uri'] ) && $path !== trim( $t['uri'], '/' ) ) {
			$log['errors'][] = "chuyên mục {$t['key']}: đường dẫn thật /$path khác plan /{$t['uri']}";
		}
	}
	$bad = 0;
	foreach ( $plan['posts'] as $p ) {
		if ( ! get_post( $p['id'] ) || isset( $p['cpt'] ) ) {
			continue;
		}
		$now  = wp_get_object_terms( $p['id'], 'category', array( 'fields' => 'ids' ) );
		$want = array_map( function ( $k ) use ( $ids ) { return (int) $ids[ $k ]; }, $p['cats'] );
		sort( $now );
		sort( $want );
		if ( $now != $want || (int) get_post_meta( $p['id'], 'rank_math_primary_category', true ) !== (int) $ids[ $p['primary'] ] ) {
			$bad++;
		}
	}
	$log['verify_posts_bad'] = $bad;
	if ( $bad ) {
		$log['errors'][] = "$bad bài lệch sau khi ghi";
	}
}
$json = wp_json_encode( $log, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE );
if ( getenv( 'OUT' ) ) {
	file_put_contents( getenv( 'OUT' ), $json );
	echo 'OK log → ', getenv( 'OUT' ), ', lỗi: ', count( $log['errors'] ), "\n";
} else {
	echo $json;
}
exit( $log['errors'] ? 1 : 0 );
