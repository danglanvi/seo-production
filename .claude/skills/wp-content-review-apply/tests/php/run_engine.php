<?php
/**
 * Chạy một script engine (apply.php, locate.php) với WordPress giả, trong phạm vi hàm như `wp eval-file`.
 * php tests/php/run_engine.php <script.php> <store.json> <store-out.json>
 * store.json: {"posts":{ID:{...}}, "meta":{ID:{key:value}}, "usermeta":{UID:{key:value}}, "options":{name:value}, "tables":{...}}
 * Sau khi script chạy xong, ghi trạng thái cuối của store ra store-out.json (kèm danh sách lệnh ghi).
 */
define( 'ABSPATH', '/stub/' );
define( 'ARRAY_A', 'ARRAY_A' );
[ , $script, $store_in, $store_out ] = $argv;
$GLOBALS['WPS_STORE'] = json_decode( file_get_contents( $store_in ), true );
$GLOBALS['WPS_STORE']['calls'] = array();

function wps_unslash_deep( $v ) {
	return is_string( $v ) ? stripslashes( $v ) : $v;
}
function wp_slash( $v ) {
	return is_string( $v ) ? addslashes( $v ) : $v;
}
function kses_remove_filters() {}
function wp_cache_flush() {
	$GLOBALS['WPS_STORE']['calls'][] = 'wp_cache_flush';
}
function clean_post_cache( $id ) {
	$GLOBALS['WPS_STORE']['calls'][] = "clean_post_cache:$id";
}
function current_time( $t ) {
	return '2026-10-25 00:00:00';
}
function delete_option( $n ) {}
function wp_json_encode( $v, $flags = 0 ) {
	return json_encode( $v, $flags );
}
function get_post( $id ) {
	$p = $GLOBALS['WPS_STORE']['posts'][ $id ] ?? null;
	return $p ? (object) $p : null;
}
function get_post_meta( $id, $k, $single = true ) {
	return $GLOBALS['WPS_STORE']['meta'][ $id ][ $k ] ?? '';
}
function update_post_meta( $id, $k, $v ) {
	$GLOBALS['WPS_STORE']['meta'][ $id ][ $k ] = wps_unslash_deep( $v );
	$GLOBALS['WPS_STORE']['calls'][]           = "update_post_meta:$id:$k";
}
function get_user_meta( $uid, $k, $single = true ) {
	return $GLOBALS['WPS_STORE']['usermeta'][ $uid ][ $k ] ?? '';
}
function update_user_meta( $uid, $k, $v ) {
	$GLOBALS['WPS_STORE']['usermeta'][ $uid ][ $k ] = wps_unslash_deep( $v );
}
function get_option( $n ) {
	return $GLOBALS['WPS_STORE']['options'][ $n ] ?? false;
}
function update_option( $n, $v ) {
	$GLOBALS['WPS_STORE']['options'][ $n ] = $v;
}
class WPS_Stub_DB {
	public $posts  = 'wp_posts';
	public $postmeta = 'wp_postmeta';
	public $options = 'wp_options';
	public $prefix = 'wp_';
	public $insert_id = 1;
	public function update( $table, $data, $where ) {
		foreach ( $data as $k => $v ) {
			$GLOBALS['WPS_STORE']['posts'][ $where['ID'] ][ $k ] = $v;
		}
		$GLOBALS['WPS_STORE']['calls'][] = 'wpdb_update:' . $where['ID'];
	}
	public function prepare( $q, ...$a ) {
		return $q . '|' . json_encode( $a );
	}
	public function esc_like( $s ) {
		return addcslashes( $s, '_%\\' );
	}
	public function get_var( $q ) {
		return null;
	}
	public function insert( $t, $d ) {}
	// set_post_modified.php: đọc và ghi 2 cột ngày của posts. Tham số lấy từ chuỗi prepare() giả.
	private function wps_args( $q ) {
		return json_decode( substr( $q, strrpos( $q, '|' ) + 1 ), true );
	}
	public function get_row( $q, $mode = null ) {
		$a = $this->wps_args( $q );
		$p = $GLOBALS['WPS_STORE']['posts'][ $a[0] ] ?? null;
		return $p ? array( 'm' => $p['post_modified'], 'g' => $p['post_modified_gmt'] ) : null;
	}
	public function query( $q ) {
		[ $m, $g, $id, $om, $og ] = $this->wps_args( $q );
		$p = $GLOBALS['WPS_STORE']['posts'][ $id ] ?? null;
		$GLOBALS['WPS_STORE']['calls'][] = "wpdb_query:$id";
		if ( ! $p || $p['post_modified'] !== $om || $p['post_modified_gmt'] !== $og ) {
			return 0;
		}
		$GLOBALS['WPS_STORE']['posts'][ $id ]['post_modified']     = $m;
		$GLOBALS['WPS_STORE']['posts'][ $id ]['post_modified_gmt'] = $g;
		return 1;
	}
	// locate.php: chọn bộ kết quả theo bảng có trong câu SQL.
	public function get_results( $q, $mode = null ) {
		$T = $GLOBALS['WPS_STORE']['tables'] ?? array();
		foreach ( array( 'postmeta', 'options', 'posts' ) as $name ) {
			if ( false !== strpos( $q, 'wp_' . $name ) || false !== strpos( $q, '{' . $name . '}' ) ) {
				$GLOBALS['WPS_STORE']['calls'][] = 'get_results:' . $name;
				return $T[ $name ] ?? array();
			}
		}
		return array();
	}
}
$wpdb = new WPS_Stub_DB();
$GLOBALS['wpdb'] = $wpdb;
register_shutdown_function(
	function () use ( $store_out ) {
		file_put_contents( $store_out, json_encode( $GLOBALS['WPS_STORE'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT ) );
	}
);
// Chạy trong hàm để biến cấp file không thành biến toàn cục, giống wp eval-file.
function wps_run_like_eval_file( $file ) {
	global $wpdb;
	include $file;
}
wps_run_like_eval_file( $script );
