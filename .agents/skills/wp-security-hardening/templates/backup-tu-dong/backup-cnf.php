<?php
// Đọc DB_* trong wp-config.php, ghi file [client] cho mysqldump vào $argv[2], in tên DB. Không in mật khẩu.
// DB_HOST dạng "host:port" ghi thêm host và port. Dạng "localhost:/đường/dẫn/socket" ghi socket. "localhost" hoặc thiếu: dùng socket mặc định.
$c = file_get_contents( $argv[1] );
$v = [];
foreach ( [ 'DB_NAME', 'DB_USER', 'DB_PASSWORD' ] as $k ) {
	if ( ! preg_match( "/define\(\s*['\"]{$k}['\"]\s*,\s*'((?:[^'\\\\]|\\\\.)*)'/", $c, $m ) ) {
		fwrite( STDERR, "Thiếu $k trong wp-config.php\n" );
		exit( 1 );
	}
	$v[ $k ] = strtr( $m[1], [ "\\'" => "'", '\\\\' => '\\' ] );
}
$q = fn( $s ) => '"' . addcslashes( $s, "\"\\" ) . '"';
$extra = '';
if ( preg_match( "/define\(\s*['\"]DB_HOST['\"]\s*,\s*'((?:[^'\\\\]|\\\\.)*)'/", $c, $m ) ) {
	$h = strtr( $m[1], [ "\\'" => "'", '\\\\' => '\\' ] );
	if ( preg_match( '#^(.*?):(/.*)$#', $h, $p ) ) {
		$extra = 'socket=' . $q( $p[2] ) . "\n";
	} elseif ( preg_match( '/^(.*):(\d+)$/', $h, $p ) ) {
		$extra = ( '' !== $p[1] && 'localhost' !== $p[1] ? 'host=' . $q( $p[1] ) . "\n" : '' ) . 'port=' . $p[2] . "\n";
	} elseif ( '' !== $h && 'localhost' !== $h ) {
		$extra = 'host=' . $q( $h ) . "\n";
	}
}
file_put_contents( $argv[2], "[client]\nuser=" . $q( $v['DB_USER'] ) . "\npassword=" . $q( $v['DB_PASSWORD'] ) . "\n" . $extra );
echo $v['DB_NAME'];
