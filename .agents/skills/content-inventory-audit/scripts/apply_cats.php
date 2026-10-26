<?php
/**
 * Ghi danh mục chính và thêm/gỡ chuyên mục theo apply.json của `inventory.py category`. Chỉ chạy sau khi người duyệt chốt.
 * Dùng: FIX=<apply.json> DRY=1|0 [META=rank_math_primary_category|_yoast_wpseo_primary_category] wp eval-file apply_cats.php
 * Mặc định chạy thử (DRY=1). Bỏ qua bài có chuyên mục hoặc danh mục chính khác lúc audit. Kiểm URL trước và sau.
 * Backup trước khi ghi thật: bảng term_relationships của các bài và meta danh mục chính.
 */
global $wpdb;
$fix  = json_decode( file_get_contents( getenv( 'FIX' ) ), true );
$dry  = getenv( 'DRY' ) !== '0';
$meta = getenv( 'META' ) ?: 'rank_math_primary_category';
$ids  = array_map( function ( $f ) { return (int) $f['id']; }, $fix );

$trans = array();
if ( $ids && $wpdb->get_var( "SHOW TABLES LIKE '{$wpdb->prefix}icl_translations'" ) ) {
	$in    = implode( ',', $ids );
	$trans = $wpdb->get_col( "SELECT DISTINCT a.element_id FROM {$wpdb->prefix}icl_translations a
        JOIN {$wpdb->prefix}icl_translations b ON a.trid = b.trid AND b.element_id <> a.element_id
        WHERE a.element_type = 'post_post' AND a.element_id IN ($in)" );
}

$log = array();
$n   = array( 'ghi' => 0, 'bỏ qua' => 0, 'lỗi' => 0 );
foreach ( $fix as $f ) {
	$id  = (int) $f['id'];
	$cur = array_map( 'intval', wp_get_object_terms( $id, 'category', array( 'fields' => 'ids' ) ) );
	sort( $cur );
	$prim = (int) get_post_meta( $id, $meta, true );
	$url  = get_permalink( $id );
	$row  = array( 'id' => $id, 'url' => $url, 'before_cats' => $cur, 'before_primary' => $prim );
	$exp  = array_map( 'intval', $f['expect_cats'] );
	if ( $cur !== $exp || $prim !== (int) $f['expect_primary'] ) {
		$row['skip'] = 'khác lúc audit';
		$n['bỏ qua']++;
		$log[] = $row;
		continue;
	}
	$new = array_values( array_diff( array_unique( array_merge( $cur, array_map( 'intval', $f['add'] ) ) ), array_map( 'intval', $f['remove'] ) ) );
	sort( $new );
	$row['after_cats']    = $new;
	$row['after_primary'] = (int) $f['primary'];
	if ( ! in_array( (int) $f['primary'], $new, true ) ) {
		$row['skip'] = 'danh mục chính không nằm trong chuyên mục gắn';
		$n['bỏ qua']++;
		$log[] = $row;
		continue;
	}
	if ( ! $dry ) {
		if ( $new !== $cur ) {
			$r = wp_set_object_terms( $id, $new, 'category', false );
			if ( is_wp_error( $r ) ) {
				$row['error'] = $r->get_error_message();
				$n['lỗi']++;
				$log[] = $row;
				continue;
			}
		}
		update_post_meta( $id, $meta, (int) $f['primary'] );
		clean_post_cache( $id );
		$chk = array_map( 'intval', wp_get_object_terms( $id, 'category', array( 'fields' => 'ids' ) ) );
		sort( $chk );
		$row['ok']        = $chk === $new && (int) get_post_meta( $id, $meta, true ) === (int) $f['primary'];
		$row['url_after'] = get_permalink( $id );
		if ( ! $row['ok'] || $row['url_after'] !== $url ) {
			$n['lỗi']++;
		}
	}
	$n['ghi']++;
	$log[] = $row;
}
if ( ! $dry ) {
	do_action( 'litespeed_purge_all' );
}
echo wp_json_encode( array( 'dry' => $dry, 'meta' => $meta, 'prefix' => $wpdb->prefix, 'dem' => $n, 'co_ban_dich' => $trans, 'log' => $log ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
