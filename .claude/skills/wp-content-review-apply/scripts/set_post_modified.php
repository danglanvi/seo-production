<?php
/**
 * set_post_modified.php — đổi post_modified và post_modified_gmt của bài để đổi lastmod trong sitemap. Chạy bằng `wp eval-file`.
 *
 * Biến: MODE=read|dry|write|rbdry|rollback (bắt buộc), TSV=<đường dẫn TSV trên server>.
 * TSV có dòng tiêu đề, mỗi dòng: id, url, post_modified cũ, post_modified_gmt cũ, post_modified mới, post_modified_gmt mới, căn cứ.
 * Giá trị dạng "YYYY-MM-DD HH:MM:SS". post_modified theo giờ của site, post_modified_gmt theo UTC.
 * write: chỉ ghi khi cả 2 cột live còn bằng giá trị cũ. rollback: chỉ ghi khi cả 2 cột live bằng giá trị mới.
 * Sau mỗi dòng ghi: clean_post_cache(ID). Không flush object cache. Lệnh SQL không chạy save_post: tự xoá cache sitemap và purge sau đó.
 * Mỗi dòng in một JSON: status updated | would_update | skip: <lý do> | WARN rows=<n>.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit( 1 );
}
global $wpdb;
$spm_mode = (string) getenv( 'MODE' );
if ( ! in_array( $spm_mode, array( 'read', 'dry', 'write', 'rbdry', 'rollback' ), true ) ) {
	echo "set_post_modified: MODE phải là read, dry, write, rbdry hoặc rollback. Không chạy.\n";
	exit( 2 );
}
$spm_tsv = (string) getenv( 'TSV' );
if ( '' === $spm_tsv || ! is_readable( $spm_tsv ) ) {
	echo "set_post_modified: không đọc được TSV. Không chạy.\n";
	exit( 2 );
}
$spm_re = '/^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$/';
foreach ( array_slice( file( $spm_tsv ), 1 ) as $spm_line ) {
	$spm_r = explode( "\t", rtrim( $spm_line, "\r\n" ) );
	if ( count( $spm_r ) < 6 ) {
		if ( '' !== trim( $spm_line ) ) {
			echo wp_json_encode( array( 'line' => $spm_line, 'status' => 'skip: thiếu cột' ), JSON_UNESCAPED_UNICODE ), "\n";
		}
		continue;
	}
	list( $spm_id, $spm_url, $spm_om, $spm_og, $spm_nm, $spm_ng ) = $spm_r;
	$spm_cur = $wpdb->get_row( $wpdb->prepare( "SELECT post_modified m, post_modified_gmt g FROM {$wpdb->posts} WHERE ID=%d", $spm_id ), ARRAY_A );
	$spm_o   = array( 'id' => $spm_id, 'url' => $spm_url, 'live' => $spm_cur );
	if ( 'read' === $spm_mode ) {
		echo wp_json_encode( $spm_o, JSON_UNESCAPED_UNICODE ), "\n";
		continue;
	}
	$spm_rb   = in_array( $spm_mode, array( 'rollback', 'rbdry' ), true );
	$spm_from = $spm_rb ? array( $spm_nm, $spm_ng ) : array( $spm_om, $spm_og );
	$spm_to   = $spm_rb ? array( $spm_om, $spm_og ) : array( $spm_nm, $spm_ng );
	$spm_bad  = array_filter( array_merge( $spm_from, $spm_to ), function ( $v ) use ( $spm_re ) {
		return ! preg_match( $spm_re, $v );
	} );
	if ( $spm_bad ) {
		$spm_o['status'] = 'skip: sai định dạng';
	} elseif ( ! $spm_cur || $spm_cur['m'] !== $spm_from[0] || $spm_cur['g'] !== $spm_from[1] ) {
		$spm_o['status'] = 'skip: giá trị live khác giá trị mong đợi';
	} elseif ( in_array( $spm_mode, array( 'dry', 'rbdry' ), true ) ) {
		$spm_o['status'] = 'would_update';
		$spm_o['to']     = $spm_to;
	} else {
		$spm_n = $wpdb->query( $wpdb->prepare( "UPDATE {$wpdb->posts} SET post_modified=%s, post_modified_gmt=%s WHERE ID=%d AND post_modified=%s AND post_modified_gmt=%s", $spm_to[0], $spm_to[1], $spm_id, $spm_from[0], $spm_from[1] ) );
		clean_post_cache( (int) $spm_id );
		$spm_o['rows']   = $spm_n;
		$spm_o['status'] = 1 === $spm_n ? 'updated' : 'WARN rows=' . var_export( $spm_n, true );
		$spm_o['after']  = $wpdb->get_row( $wpdb->prepare( "SELECT post_modified m, post_modified_gmt g FROM {$wpdb->posts} WHERE ID=%d", $spm_id ), ARRAY_A );
	}
	echo wp_json_encode( $spm_o, JSON_UNESCAPED_UNICODE ), "\n";
}
