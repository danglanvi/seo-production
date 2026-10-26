<?php
/**
 * Rollback của insert_shortcode.php: trả post_content về bản trước khi chèn shortcode.
 * Chạy: DRY=1|0 BK=<thư mục có before.json, after.json> wp eval-file rollback_shortcode.php
 * - Bài chưa ai sửa sau lần chèn (md5 khớp after.json): ghi lại nguyên văn nội dung cũ.
 * - Bài đã bị sửa sau đó: chỉ gỡ đúng đoạn shortcode đã chèn, giữ phần sửa của người khác.
 * - Không đổi post_modified. Gỡ file mu-plugin và purge cache làm bằng lệnh shell (SKILL.md mục Rollback).
 */
global $wpdb;
$dry    = '0' !== getenv( 'DRY' );
$bk     = rtrim( (string) getenv( 'BK' ), '/' );
$before = json_decode( (string) @file_get_contents( $bk . '/before.json' ), true );
$after  = json_decode( (string) @file_get_contents( $bk . '/after.json' ), true );
if ( ! is_array( $before ) ) {
	echo json_encode( array( 'error' => 'Không đọc được ' . $bk . '/before.json' ) );
	return;
}
$out = array();
foreach ( $before as $id => $b ) {
	$id  = (int) $id;
	$cur = $wpdb->get_var( $wpdb->prepare( "SELECT post_content FROM {$wpdb->posts} WHERE ID=%d", $id ) );
	if ( null === $cur ) {
		$out[ $id ] = 'missing';
		continue;
	}
	$a = $after[ $id ] ?? null;
	if ( md5( $cur ) === $b['md5'] ) {
		$out[ $id ] = 'already-original';
		continue;
	}
	if ( $a && md5( $cur ) === $a['md5'] ) {
		$new  = $b['post_content'];
		$mode = 'restore-exact';
	} elseif ( $a && false !== strpos( $cur, $a['snippet'] ) ) {
		$new  = str_replace( $a['snippet'], '', $cur );
		$mode = 'strip-snippet (bài đã được sửa sau lần chèn)';
	} else {
		$out[ $id ] = 'manual: không thấy snippet, cần xem tay';
		continue;
	}
	if ( $dry ) {
		$out[ $id ] = 'dry: ' . $mode;
		continue;
	}
	$n = $wpdb->query( $wpdb->prepare( "UPDATE {$wpdb->posts} SET post_content=%s WHERE ID=%d AND MD5(post_content)=%s", $new, $id, md5( $cur ) ) );
	clean_post_cache( $id );
	$out[ $id ] = ( 1 === (int) $n ? 'ok: ' : 'failed: ' ) . $mode;
}
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT );
