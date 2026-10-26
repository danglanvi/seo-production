<?php
/**
 * Ghi bản làm sạch HTML thừa. Mặc định chạy thử (DRY): chỉ so md5 và in kế hoạch. Chỉ ghi khi DRY=0.
 * CHANGES=<changes.json> CMP=<ket-qua compare_autop.json> BK=<backup.json> OUT=<log.json> [DRY=0] wp eval-file apply_cruft.php
 *   CHANGES  bắt buộc. File do cruft_clean.py sinh.
 *   CMP      bắt buộc khi DRY=0. Kết quả compare_autop.php: phải có bad = 0 và changes_md5 khớp CHANGES. Thiếu thì dừng.
 *   BK       bắt buộc khi DRY=0. File backup giá trị gốc. Không ghi đè file có sẵn.
 *   OUT      tuỳ chọn. Log {applied: [{kind, id, md5_after}], skipped: [...]}. rollback_cruft.php đọc log này.
 * Mục chỉ được ghi khi md5 giá trị hiện tại bằng md5 lúc xuất. Khác thì skip: site đã đổi sau lúc xuất.
 * Ghi bằng $wpdb->update cho post_content và postmeta (không đổi ngày cập nhật, không lọc HTML),
 * _elementor_data lưu bằng wp_slash(wp_json_encode()). Xoá object cache cuối lượt. Purge trang do người chạy làm theo ghi-an-toan.md mục 1.
 * Mã thoát 0 xong, 1 có skip, 2 thiếu đầu vào hoặc bị chặn.
 */
global $wpdb;
$changes_path = getenv( 'CHANGES' );
$dry          = '0' !== getenv( 'DRY' );
if ( ! $changes_path || ! is_file( $changes_path ) ) {
	fwrite( STDERR, "Cần CHANGES=<changes.json>\n" );
	exit( 2 );
}
$bk_path  = getenv( 'BK' );
$cmp_path = getenv( 'CMP' );
if ( ! $dry ) {
	$cmp = $cmp_path && is_file( $cmp_path ) ? json_decode( file_get_contents( $cmp_path ), true ) : null;
	if ( ! $cmp || 0 !== (int) $cmp['bad'] || ( $cmp['changes_md5'] ?? '' ) !== md5_file( $changes_path ) ) {
		fwrite( STDERR, "Dừng: cần CMP từ compare_autop.php với bad = 0 và đúng file CHANGES này.\n" );
		exit( 2 );
	}
	if ( ! $bk_path || file_exists( $bk_path ) ) {
		fwrite( STDERR, "Dừng: cần BK=<file backup chưa có>.\n" );
		exit( 2 );
	}
}
$ch = json_decode( file_get_contents( $changes_path ), true );
$bk = array();
$ok = array();
$skipped = array();
foreach ( $ch as $c ) {
	if ( 'post' === $c['kind'] ) {
		$p  = get_post( $c['id'] );
		$el = get_post_meta( $c['id'], '_elementor_data', true );
		$el = is_string( $el ) ? $el : '';
		if ( ! $p || md5( $p->post_content ) !== $c['md5c'] || md5( $el ) !== $c['md5e'] ) {
			$skipped[] = array( 'kind' => 'post', 'id' => $c['id'], 'why' => 'md5 khác lúc xuất' );
			continue;
		}
		$bk[] = array( 'kind' => 'post', 'id' => $c['id'], 'content' => $p->post_content, 'el' => $el );
	} elseif ( 'meta' === $c['kind'] ) {
		$cur = $wpdb->get_var( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->postmeta} WHERE meta_id = %d", $c['meta_id'] ) );
		if ( null === $cur || md5( $cur ) !== $c['md5'] ) {
			$skipped[] = array( 'kind' => 'meta', 'id' => $c['meta_id'], 'why' => 'md5 khác lúc xuất' );
			continue;
		}
		$bk[] = array( 'kind' => 'meta', 'id' => $c['meta_id'], 'post_id' => $c['post_id'], 'value' => $cur );
	} else {
		$cur = get_option( $c['key'] );
		if ( md5( wp_json_encode( $cur ) ) !== $c['md5'] ) {
			$skipped[] = array( 'kind' => 'option', 'id' => $c['key'], 'why' => 'md5 khác lúc xuất' );
			continue;
		}
		$bk[] = array( 'kind' => 'option', 'id' => $c['key'], 'value' => $cur );
	}
	$ok[] = $c;
}
echo ( $dry ? 'chạy thử' : 'ghi' ) . ': khớp ' . count( $ok ) . ', skip ' . count( $skipped ) . "\n";
foreach ( $skipped as $s ) {
	echo "skip {$s['kind']} {$s['id']}: {$s['why']}\n";
}
$applied = array();
if ( ! $dry ) {
	file_put_contents( $bk_path, wp_json_encode( $bk ) );
	foreach ( $ok as $c ) {
		if ( 'post' === $c['kind'] ) {
			$id = (int) $c['id'];
			if ( null !== $c['content'] ) {
				$wpdb->update( $wpdb->posts, array( 'post_content' => $c['content'] ), array( 'ID' => $id ) );
			}
			if ( ! empty( $c['el'] ) ) {
				$d = json_decode( $c['el'], true );
				if ( is_array( $d ) ) {
					update_post_meta( $id, '_elementor_data', wp_slash( wp_json_encode( $d ) ) );
					delete_post_meta( $id, '_elementor_element_cache' );
				}
			}
			clean_post_cache( $id );
			$after = get_post( $id );
			$el2   = get_post_meta( $id, '_elementor_data', true );
			$applied[] = array( 'kind' => 'post', 'id' => $c['id'], 'md5_after' => md5( $after->post_content ), 'md5_el_after' => md5( is_string( $el2 ) ? $el2 : '' ) );
		} elseif ( 'meta' === $c['kind'] ) {
			$wpdb->update( $wpdb->postmeta, array( 'meta_value' => $c['new'] ), array( 'meta_id' => $c['meta_id'] ) );
			wp_cache_delete( $c['post_id'], 'post_meta' );
			clean_post_cache( $c['post_id'] );
			$applied[] = array( 'kind' => 'meta', 'id' => $c['meta_id'], 'post_id' => $c['post_id'], 'md5_after' => md5( $c['new'] ) );
		} else {
			update_option( $c['key'], $c['new'] );
			$applied[] = array( 'kind' => 'option', 'id' => $c['key'], 'md5_after' => md5( wp_json_encode( get_option( $c['key'] ) ) ) );
		}
	}
	wp_cache_flush();
	echo 'đã ghi ' . count( $applied ) . " mục. Purge cache trang theo URL, rồi chạy compare và verify.\n";
}
if ( getenv( 'OUT' ) ) {
	file_put_contents( getenv( 'OUT' ), wp_json_encode( array( 'dry' => $dry, 'applied' => $applied, 'would_apply' => $dry ? count( $ok ) : null, 'skipped' => $skipped ) ) );
}
exit( $skipped ? 1 : 0 );
