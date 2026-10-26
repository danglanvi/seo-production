<?php
/**
 * Xuất bản đồ URL tuỳ chỉnh của Permalink Manager (option permalink-manager-uris) cho mu-plugin permalink-uris.php. Chỉ đọc DB.
 * Chạy khi Permalink Manager còn bật: so link mà mu-plugin sẽ in với link Permalink Manager đang in.
 * Site dùng WPML dạng thư mục: URI của bài khác ngôn ngữ mặc định được thêm tiền tố "<mã>/", link tính trong ngôn ngữ của bài.
 * Output (stdout, JSON): map {"<id>" | "tax-<term_id>": "<uri>"} chỉ gồm bài publish và term còn tồn tại, kèm thống kê và danh sách lệch.
 * Chạy: <php> /usr/local/bin/wp --path=<root> eval-file pm_export.php > pm.json ; rồi lấy khoá "map" ghi vào permalink-uris.json
 */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
$uris = (array) get_option( 'permalink-manager-uris', array() );
$map  = array();
$out  = array( 'total' => count( $uris ), 'kept' => 0, 'skip' => array( 'not_publish' => 0, 'missing' => 0 ), 'dupes' => array(), 'mismatch' => array(), 'checked' => 0 );
$seen = array();
$def  = apply_filters( 'wpml_default_language', null );
$cur  = apply_filters( 'wpml_current_language', null );
foreach ( $uris as $key => $uri ) {
	$uri = trim( (string) $uri, '/' );
	if ( 0 === strpos( (string) $key, 'tax-' ) ) {
		$t = get_term( (int) substr( $key, 4 ) );
		if ( ! $t || is_wp_error( $t ) ) { $out['skip']['missing']++; continue; }
		$link = get_term_link( $t );
	} else {
		$st = get_post_status( (int) $key );
		if ( ! $st ) { $out['skip']['missing']++; continue; }
		if ( 'publish' !== $st ) { $out['skip']['not_publish']++; continue; }
		$l  = apply_filters( 'wpml_post_language_details', null, (int) $key );
		$lc = is_array( $l ) && ! empty( $l['language_code'] ) ? $l['language_code'] : null;
		if ( $lc ) { do_action( 'wpml_switch_language', $lc ); }
		$link = get_permalink( (int) $key );
		if ( $lc ) { do_action( 'wpml_switch_language', $cur ); }
		if ( $lc && $def && $lc !== $def && 0 !== strpos( $uri . '/', $lc . '/' ) ) { $uri = $lc . '/' . $uri; }
	}
	if ( isset( $seen[ $uri ] ) ) { $out['dupes'][] = array( $seen[ $uri ], $key, $uri ); continue; }
	$seen[ $uri ]        = $key;
	$map[ (string) $key ] = $uri;
	$out['kept']++;
	$want = user_trailingslashit( home_url( '/' . $uri ) );
	$out['checked']++;
	if ( ! is_wp_error( $link ) && untrailingslashit( $link ) !== untrailingslashit( $want ) ) {
		$out['mismatch'][] = array( 'key' => $key, 'pm' => wp_make_link_relative( $link ), 'map' => '/' . $uri );
	}
}
$out['map'] = $map;
echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n";
