<?php
/**
 * Trả lại giá trị gốc từ backup của apply_cruft.php. Mặc định chạy thử (DRY): chỉ báo mục nào trả được. Chỉ ghi khi DRY=0.
 * BK=<backup.json> LOG=<log của apply_cruft.php> [DRY=0] wp eval-file rollback_cruft.php
 * Chỉ trả mục mà giá trị hiện tại còn bằng md5 sau khi ghi (md5_after trong LOG). Giá trị đã đổi sau đó
 * là của phiên khác: không chép đè, in "đã đổi sau khi ghi" để sửa tay từ giá trị gốc (references/ghi-an-toan.md mục 5).
 * Mã thoát 0 xong, 1 có mục không trả, 2 thiếu đầu vào.
 */
global $wpdb;
$bk_path  = getenv( 'BK' );
$log_path = getenv( 'LOG' );
$dry      = '0' !== getenv( 'DRY' );
if ( ! $bk_path || ! is_file( $bk_path ) || ! $log_path || ! is_file( $log_path ) ) {
	fwrite( STDERR, "Cần BK=<backup.json> và LOG=<log apply_cruft>\n" );
	exit( 2 );
}
$bk    = json_decode( file_get_contents( $bk_path ), true );
$log   = json_decode( file_get_contents( $log_path ), true );
$after = array();
foreach ( $log['applied'] ?? array() as $a ) {
	$after[ $a['kind'] . ':' . $a['id'] ] = $a;
}
$restored = 0;
$kept     = array();
foreach ( $bk as $b ) {
	$k = $b['kind'] . ':' . $b['id'];
	if ( ! isset( $after[ $k ] ) ) {
		continue; // mục này không được ghi trong lượt đó
	}
	$a = $after[ $k ];
	if ( 'post' === $b['kind'] ) {
		$p   = get_post( $b['id'] );
		$el  = get_post_meta( $b['id'], '_elementor_data', true );
		$now_c = $p ? md5( $p->post_content ) : '';
		$now_e = md5( is_string( $el ) ? $el : '' );
		if ( $now_c !== $a['md5_after'] || $now_e !== $a['md5_el_after'] ) {
			$kept[] = $k;
			continue;
		}
		if ( ! $dry ) {
			$wpdb->update( $wpdb->posts, array( 'post_content' => $b['content'] ), array( 'ID' => (int) $b['id'] ) );
			if ( '' !== $b['el'] ) {
				update_post_meta( (int) $b['id'], '_elementor_data', wp_slash( $b['el'] ) );
				delete_post_meta( (int) $b['id'], '_elementor_element_cache' );
			}
			clean_post_cache( (int) $b['id'] );
		}
	} elseif ( 'meta' === $b['kind'] ) {
		$cur = $wpdb->get_var( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->postmeta} WHERE meta_id = %d", $b['id'] ) );
		if ( null === $cur || md5( $cur ) !== $a['md5_after'] ) {
			$kept[] = $k;
			continue;
		}
		if ( ! $dry ) {
			$wpdb->update( $wpdb->postmeta, array( 'meta_value' => $b['value'] ), array( 'meta_id' => (int) $b['id'] ) );
			wp_cache_delete( $b['post_id'], 'post_meta' );
			clean_post_cache( $b['post_id'] );
		}
	} else {
		if ( md5( wp_json_encode( get_option( $b['id'] ) ) ) !== $a['md5_after'] ) {
			$kept[] = $k;
			continue;
		}
		if ( ! $dry ) {
			update_option( $b['id'], $b['value'] );
		}
	}
	$restored++;
}
if ( ! $dry ) {
	wp_cache_flush();
}
echo ( $dry ? 'chạy thử' : 'đã trả' ) . ": $restored mục trả được, " . count( $kept ) . " mục đã đổi sau khi ghi\n";
foreach ( $kept as $k ) {
	echo "đã đổi sau khi ghi, không chép đè: $k\n";
}
exit( $kept ? 1 : 0 );
