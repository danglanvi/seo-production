<?php
// test_mu.php (wp-ucss): 8 ca cho mu-plugin templates/ucss-swap.php, giả lập hàm WordPress. php test_mu.php → in OK/SAI, mã 1 nếu có ca sai.
$tmp = sys_get_temp_dir() . '/wp-ucss-mu-' . getmypid();
define( 'ABSPATH', $tmp . '/' );
define( 'WP_CONTENT_DIR', $tmp . '/wp-content' );
$F = array();
function add_filter( $n, $cb, $p ) { global $F; $F[ $n ] = $cb; }
function is_user_logged_in() { return ! empty( $GLOBALS['LOGGED'] ); }
function is_admin() { return false; }
function is_feed() { return false; }
function esc_attr( $s ) { return htmlspecialchars( $s, ENT_QUOTES ); }

$H   = str_repeat( 'd4', 16 );
$dir = WP_CONTENT_DIR . '/ucss';
mkdir( $dir, 0755, true );
file_put_contents( "$dir/$H.0123abcd.css", 'body{}' );
file_put_contents( "$dir/map.php", "<?php\nreturn array( 'v' => 'test', 'files' => array( '$H' => array( 'f' => '$H.0123abcd.css', 'p' => array( '/dich-vu/' => 1 ) ) ) );\n" );
require __DIR__ . '/../../templates/ucss-swap.php';
$run = function ( $uri, $html ) use ( &$F ) { $_SERVER['REQUEST_URI'] = $uri; return $F['litespeed_buffer_after']( $html ); };

$sync  = '<html><head><link data-optimized="2" rel="stylesheet" href="https://example.com/wp-content/litespeed/css/' . $H . '.css?ver=0b2e5" /></head><body></body></html>';
$async = "<html><head><link rel='preload' data-asynced='1' data-optimized='2' as='style' onload=\"this.onload=null;this.rel='stylesheet'\" href='https://example.com/wp-content/litespeed/css/" . $H . ".css?ver=0b2e5' ><noscript><link data-optimized=2 rel=stylesheet href=\"/wp-content/litespeed/css/" . $H . ".css?ver=0b2e5\"></noscript></head></html>";
$other = str_replace( $H, str_repeat( 'a', 32 ), $sync );
$bad   = 0;
$ok    = function ( $name, $cond ) use ( &$bad ) { $bad += $cond ? 0 : 1; echo ( $cond ? 'OK  ' : 'SAI ' ) . $name . "\n"; };
$sw    = function ( $o ) { return substr_count( $o, '/wp-content/ucss/' ); };

$o = $run( '/dich-vu/', $sync );
$ok( 'link sync đổi, có onerror về file gốc', 1 === $sw( $o ) && false !== strpos( $o, 'data-ucss="1" onerror="this.onerror=null;this.href=\'https://example.com/wp-content/litespeed/css/' . $H . '.css?ver=0b2e5\'"' ) );
$ok( 'path có ?nc=1 vẫn đổi', 1 === $sw( $run( '/dich-vu/?nc=1', $sync ) ) );
$ok( 'path khác không đổi', 0 === $sw( $run( '/khac/', $sync ) ) );
$o = $run( '/dich-vu/', $async );
$ok( 'link async + noscript đổi cả hai', 2 === $sw( $o ) && false !== strpos( $o, "onload=\"this.onload=null;this.rel='stylesheet'\"" ) );
$ok( 'md5 file gộp khác không đổi', 0 === $sw( $run( '/dich-vu/', $other ) ) );
$GLOBALS['LOGGED'] = 1;
$ok( 'người đăng nhập không đổi', $sync === $run( '/dich-vu/', $sync ) );
$GLOBALS['LOGGED'] = 0;
touch( "$dir/OFF" );
$ok( 'file OFF tắt', $sync === $run( '/dich-vu/', $sync ) );
unlink( "$dir/OFF" );
rename( "$dir/$H.0123abcd.css", "$tmp/x.css" );
$ok( 'thiếu file gọn không đổi', $sync === $run( '/dich-vu/', $sync ) );

unlink( "$tmp/x.css" ); unlink( "$dir/map.php" ); rmdir( $dir ); rmdir( WP_CONTENT_DIR ); rmdir( $tmp );
exit( $bad ? 1 : 0 );
