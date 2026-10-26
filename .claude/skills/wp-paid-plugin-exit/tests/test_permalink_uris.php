<?php
/* Test permalink-uris.php bằng stub WordPress tối thiểu. Chạy: php tests/test_permalink_uris.php */
define( 'ABSPATH', '/tmp/' );
$GLOBALS['F'] = array();
function add_filter( $h, $cb, $p = 10, $n = 1 ) { $GLOBALS['F'][ $h ] = $cb; }
function add_action( $h, $cb, $p = 10, $n = 1 ) { $GLOBALS['F'][ $h ] = $cb; }
function get_option( $k ) { return 'https://vi-du.vn'; }
function user_trailingslashit( $u ) { return rtrim( $u, '/' ) . '/'; }
function get_post_type( $id ) { return array( 5 => 'page', 7 => 'post', 9 => 'khoa_hoc' )[ $id ] ?? false; }
function get_post_status( $id ) { return 7 === $id ? 'draft' : 'publish'; }
function get_term( $id ) { return (object) array( 'term_id' => $id, 'taxonomy' => 3 === $id ? 'category' : 'chu_de', 'slug' => 'cd' ); }
function is_wp_error( $x ) { return false; }

$dir = sys_get_temp_dir() . '/pu_' . getmypid();
@mkdir( $dir );
copy( dirname( __DIR__ ) . '/scripts/permalink-uris.php', "$dir/permalink-uris.php" );
file_put_contents( "$dir/permalink-uris.json", json_encode( array( '5' => 'dich-vu/seo', '7' => 'bai-nhap', '9' => 'en/khoa-hoc-a', 'tax-3' => 'tin-tuc', 'tax-4' => 'chu-de/x' ) ) );
require "$dir/permalink-uris.php";

$ok = 0;
$eq = function ( $a, $b, $msg ) use ( &$ok ) {
	if ( $a !== $b ) { fwrite( STDERR, "FAIL $msg: " . var_export( $a, true ) . "\n" ); exit( 1 ); }
	$ok++;
};
$req = function ( $path ) { $GLOBALS['wp'] = (object) array( 'request' => $path ); return $GLOBALS['F']['request']( array( 'x' => 1 ) ); };
$eq( $req( 'dich-vu/seo' ), array( 'page_id' => 5 ), 'trang' );
$eq( $req( 'Dich-Vu/SEO/' ), array( 'page_id' => 5 ), 'không phân biệt hoa thường' );
$eq( $req( 'en/khoa-hoc-a' ), array( 'p' => 9, 'post_type' => 'khoa_hoc' ), 'CPT có tiền tố ngôn ngữ' );
$eq( $req( 'tin-tuc/page/2' ), array( 'cat' => 3, 'paged' => 2 ), 'chuyên mục phân trang' );
$eq( $req( 'chu-de/x' ), array( 'chu_de' => 'cd' ), 'taxonomy riêng' );
$eq( $req( 'khong-co' ), array( 'x' => 1 ), 'path ngoài bản đồ giữ nguyên' );
$link = $GLOBALS['F']['post_type_link'];
$eq( $link( 'https://vi-du.vn/?p=9', (object) array( 'ID' => 9 ) ), 'https://vi-du.vn/en/khoa-hoc-a/', 'link CPT không lặp tiền tố' );
$eq( $link( 'https://vi-du.vn/?p=7', 7 ), 'https://vi-du.vn/?p=7', 'bài nháp giữ link gốc' );
$eq( $GLOBALS['F']['term_link']( 'x', (object) array( 'term_id' => 3 ) ), 'https://vi-du.vn/tin-tuc/', 'link term' );
array_map( 'unlink', glob( "$dir/*" ) );
rmdir( $dir );
echo "OK $ok kiểm\n";
