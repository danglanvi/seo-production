<?php
/**
 * Chèn shortcode công cụ vào thân bài, ngay trước heading neo (cuối mục liên quan).
 * Biến:
 *   PLAN=<file JSON> {"<post_id>": ["<tên công cụ>", "<đầu chữ của heading neo>"]}
 *   SC=site_tool     tên shortcode; chèn [SC name="<tên công cụ>"]
 *   DRY=1            mặc định chỉ in vị trí chèn. DRY=0 cần BK=<thư mục ghi được> để lưu before.json, after.json cho rollback_shortcode.php
 *   SRC=<file JSON>  {"<post_id>": {"content": "..."}}: đọc nội dung từ file thay vì DB (phát lại trên bản backup). Chỉ dùng với DRY=1
 * Đọc post_content mới nhất và ghi ngay trong cùng lần chạy. Câu UPDATE có điều kiện MD5 nội dung cũ: agent khác vừa sửa bài thì không ghi đè.
 * Không đổi post_modified, không tạo revision. Bài Elementor (builder) thì bỏ qua.
 * Chạy: sudo -u www HOME=/tmp/wpcli-home PLAN=... BK=... DRY=0 <php> /usr/local/bin/wp --path=<root> eval-file insert_shortcode.php
 */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
global $wpdb;
$dry  = '0' !== getenv( 'DRY' );
$bk   = rtrim( (string) getenv( 'BK' ), '/' );
$sc   = preg_replace( '/[^a-z0-9_]/', '', (string) ( getenv( 'SC' ) ?: 'site_tool' ) );
$plan = json_decode( (string) @file_get_contents( (string) getenv( 'PLAN' ) ), true ) ?: array();
$src  = getenv( 'SRC' ) ? ( json_decode( (string) @file_get_contents( getenv( 'SRC' ) ), true ) ?: array() ) : null;
if ( ! $plan ) {
	echo json_encode( array( 'error' => 'PLAN rỗng hoặc không đọc được' ) ), "\n";
	return;
}
if ( ! $dry && ( null !== $src || ! $bk || ! is_dir( $bk ) || ! is_writable( $bk ) ) ) {
	echo json_encode( array( 'error' => 'DRY=0 cần BK ghi được và không dùng SRC' ) ), "\n";
	return;
}
$norm   = function ( $h ) {
	return trim( (string) preg_replace( '/\s+/u', ' ', html_entity_decode( wp_strip_all_tags( $h ), ENT_QUOTES, 'UTF-8' ) ) );
};
$out    = array();
$before = array();
$after  = array();
foreach ( $plan as $id => $p ) {
	list( $name, $anchor ) = $p;
	$row = null !== $src ? ( isset( $src[ $id ] ) ? (object) array( 'post_content' => $src[ $id ]['content'], 'post_modified' => '' ) : null )
		: $wpdb->get_row( $wpdb->prepare( "SELECT post_content, post_status, post_modified FROM {$wpdb->posts} WHERE ID=%d", $id ) );
	if ( ! $row ) {
		$out[ $id ] = 'missing';
		continue;
	}
	$c   = $row->post_content;
	$tag = '[' . $sc . ' name="' . $name . '"]';
	if ( false !== strpos( $c, $tag ) ) {
		$out[ $id ] = 'already';
		continue;
	}
	if ( null === $src && 'builder' === get_post_meta( $id, '_elementor_edit_mode', true ) ) {
		$out[ $id ] = 'elementor-skip';
		continue;
	}
	preg_match_all( '#<h([1-6])\b[^>]*>(.*?)</h\1>#si', $c, $m, PREG_SET_ORDER | PREG_OFFSET_CAPTURE );
	$hits = array();
	foreach ( $m as $x ) {
		if ( 0 === strpos( $norm( $x[2][0] ), $anchor ) ) {
			$hits[] = $x[0][1];
		}
	}
	if ( 1 !== count( $hits ) ) {
		$out[ $id ] = 'anchor-count-' . count( $hits );
		continue;
	}
	$at     = $hits[0];
	$blocks = has_blocks( $c );
	if ( $blocks ) {
		// Comment mở block gần nhất trước heading (wp:heading hoặc wp:html). Giữa comment và thẻ heading chỉ được có khoảng trắng
		// hoặc </p> (bài cũ chuyển từ classic có comment block bọc trong <p>).
		$cm = strrpos( substr( $c, 0, $at ), '<!-- wp:' );
		if ( false === $cm || ! preg_match( '#^<!-- wp:(heading|html)\b#', substr( $c, $cm, 20 ) ) || '' !== trim( str_replace( '</p>', '', preg_replace( '#^<!-- wp:[^>]*?-->#s', '', substr( $c, $cm, $at - $cm ) ) ) ) ) {
			$out[ $id ] = 'block-comment-not-found';
			continue;
		}
		$at      = $cm;
		$snippet = "<!-- wp:shortcode -->\n" . $tag . "\n<!-- /wp:shortcode -->\n\n";
	} else {
		// Dòng trống trước và sau để wpautop tách shortcode thành đoạn riêng (shortcode_unautop gỡ <p> bọc ngoài).
		$snippet = "\n" . $tag . "\n\n";
	}
	$new = substr( $c, 0, $at ) . $snippet . substr( $c, $at );
	$ctx = $norm( substr( $c, max( 0, $at - 160 ), 160 ) ) . ' ▶[' . $name . ']◀ ' . $norm( substr( $c, $at, 120 ) );
	if ( $dry ) {
		$out[ $id ] = array( 'dry' => 'ok', 'blocks' => $blocks, 'at' => $at, 'ctx' => $ctx );
		continue;
	}
	$before[ $id ] = array( 'post_content' => $c, 'md5' => md5( $c ), 'post_modified' => $row->post_modified );
	file_put_contents( $bk . '/before.json', wp_json_encode( $before, JSON_UNESCAPED_UNICODE ) );
	$n             = $wpdb->query( $wpdb->prepare( "UPDATE {$wpdb->posts} SET post_content=%s WHERE ID=%d AND MD5(post_content)=%s", $new, $id, md5( $c ) ) );
	if ( 1 !== (int) $n ) {
		unset( $before[ $id ] );
		file_put_contents( $bk . '/before.json', wp_json_encode( $before, JSON_UNESCAPED_UNICODE ) );
		$out[ $id ] = 'changed-or-failed';
		continue;
	}
	clean_post_cache( $id );
	$after[ $id ] = array( 'md5' => md5( $new ), 'snippet' => $snippet, 'name' => $name );
	file_put_contents( $bk . '/after.json', wp_json_encode( $after, JSON_UNESCAPED_UNICODE ) );
	$out[ $id ]   = array( 'written' => 'ok', 'blocks' => $blocks, 'ctx' => $ctx );
}
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT ), "\n";
