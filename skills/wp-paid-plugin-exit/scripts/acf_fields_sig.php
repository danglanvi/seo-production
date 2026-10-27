<?php
/**
 * acf_fields_sig.php (wp-paid-plugin-exit): chữ ký giá trị ACF qua API, chỉ đọc. Chạy trước và sau khi đổi ACF Pro sang SCF hay bản miễn phí.
 * Đọc get_fields() đã định dạng và thô cho mọi bài publish có dữ liệu ACF, term và user có meta ACF, trang options.
 * Dùng: OUT=/tmp/wpcli-home/fields_<nhãn>.json wp eval-file acf_fields_sig.php
 * In: phiên bản ACF, số đối tượng, md5 tổng. So 2 file bằng md5 theo từng đối tượng (khoá "sig").
 * Site mẫu 24/10/2026: 376 đối tượng, lệch 0 sau khi đổi trên production.
 */
if ( ! defined( 'ABSPATH' ) || ! function_exists( 'get_fields' ) ) {
	fwrite( STDERR, "Cần WordPress và ACF đang bật\n" );
	exit( 1 );
}
global $wpdb;
$out  = getenv( 'OUT' ) ?: '/tmp/wpcli-home/fields.json';
$ids  = $wpdb->get_col( "SELECT DISTINCT p.ID FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id=p.ID WHERE p.post_status='publish' AND m.meta_key LIKE '\\_%' AND m.meta_value LIKE 'field\\_%' ORDER BY p.ID" );
$tids = $wpdb->get_col( "SELECT DISTINCT term_id FROM {$wpdb->termmeta} WHERE meta_value LIKE 'field\\_%' ORDER BY term_id" );
$uids = $wpdb->get_col( "SELECT DISTINCT user_id FROM {$wpdb->usermeta} WHERE meta_value LIKE 'field\\_%' ORDER BY user_id" );
$all  = array();
foreach ( $ids as $id ) {
	$all[ "p$id" ] = array( get_fields( (int) $id ), get_fields( (int) $id, false ) );
}
foreach ( $tids as $t ) {
	$all[ "term_$t" ] = array( get_fields( "term_$t" ), get_fields( "term_$t", false ) );
}
foreach ( $uids as $u ) {
	$all[ "user_$u" ] = array( get_fields( "user_$u" ), get_fields( "user_$u", false ) );
}
$all['option'] = array( get_fields( 'option' ), get_fields( 'option', false ) );
$meta          = array( 'acf' => defined( 'ACF_VERSION' ) ? ACF_VERSION : '?', 'path' => defined( 'ACF_PATH' ) ? basename( ACF_PATH ) : '?', 'n' => count( $all ) );
$meta['sig']   = array_map( function ( $v ) { return md5( serialize( $v ) ); }, $all );
$meta['md5']   = md5( serialize( $meta['sig'] ) );
file_put_contents( $out, wp_json_encode( array( 'meta' => $meta, 'data' => $all ) ) );
echo 'acf=', $meta['acf'], ' path=', $meta['path'], ' n=', $meta['n'], ' posts=', count( $ids ), ' terms=', count( $tids ), ' users=', count( $uids ), ' md5=', $meta['md5'], "\n";
