<?php
/**
 * Chạy script dọn HTML thừa (export_cruft, compare_autop, apply_cruft, rollback_cruft) với WordPress giả, như `wp eval-file`.
 * php tests/php/run_cruft.php <script.php> <store.json> <store-out.json>
 * store.json: {"posts":{ID:{ID, post_content, post_type, post_name}}, "meta":{ID:{key:value}},
 *   "postmeta_rows":{meta_id:{post_id, meta_key, meta_value}}, "options":{name:value},
 *   "export_posts_pages":[[rows...]], "export_meta_rows":[rows...]}
 * wpautop ở đây là bản port để test, gần với lõi WordPress. Cổng thật chạy trên site với wpautop của WordPress.
 * Sau khi chạy, ghi store cuối ra store-out.json (kèm danh sách lệnh ghi trong "calls").
 */
define( 'ABSPATH', '/stub/' );
define( 'ARRAY_A', 'ARRAY_A' );
[ , $script, $store_in, $store_out ] = $argv;
$GLOBALS['WPS_STORE']          = json_decode( file_get_contents( $store_in ), true );
$GLOBALS['WPS_STORE']['calls'] = array();

function wp_slash( $v ) {
	return is_string( $v ) ? addslashes( $v ) : $v;
}
function wp_json_encode( $v, $flags = 0 ) {
	return json_encode( $v, $flags );
}
function clean_post_cache( $id ) {
	$GLOBALS['WPS_STORE']['calls'][] = "clean_post_cache:$id";
}
function wp_cache_flush() {
	$GLOBALS['WPS_STORE']['calls'][] = 'wp_cache_flush';
}
function wp_cache_delete( $k, $g = '' ) {
	$GLOBALS['WPS_STORE']['calls'][] = "wp_cache_delete:$k";
}
function is_serialized( $v ) {
	return is_string( $v ) && preg_match( '/^[aOsi]:\d+[:;]/', $v );
}
function has_blocks( $c ) {
	return false !== strpos( (string) $c, '<!-- wp:' );
}
function get_post( $id ) {
	$p = $GLOBALS['WPS_STORE']['posts'][ $id ] ?? null;
	return $p ? (object) $p : null;
}
function get_post_meta( $id, $k, $single = true ) {
	return $GLOBALS['WPS_STORE']['meta'][ $id ][ $k ] ?? '';
}
function update_post_meta( $id, $k, $v ) {
	$GLOBALS['WPS_STORE']['meta'][ $id ][ $k ] = is_string( $v ) ? stripslashes( $v ) : $v;
	$GLOBALS['WPS_STORE']['calls'][]           = "update_post_meta:$id:$k";
}
function delete_post_meta( $id, $k ) {
	unset( $GLOBALS['WPS_STORE']['meta'][ $id ][ $k ] );
}
function get_option( $n ) {
	return $GLOBALS['WPS_STORE']['options'][ $n ] ?? false;
}
function update_option( $n, $v ) {
	$GLOBALS['WPS_STORE']['options'][ $n ] = $v;
	$GLOBALS['WPS_STORE']['calls'][]       = "update_option:$n";
}
function wpautop( $text, $br = true ) {
	$ab = '(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|form|map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|legend|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary)';
	if ( '' === trim( $text ) ) {
		return '';
	}
	$text  = $text . "\n";
	$text  = preg_replace( '|<br\s*/?>\s*<br\s*/?>|', "\n\n", $text );
	$text  = preg_replace( '!(<' . $ab . '[\s/>])!', "\n\n$1", $text );
	$text  = preg_replace( '!(</' . $ab . '>)!', "$1\n\n", $text );
	$text  = str_replace( array( "\r\n", "\r" ), "\n", $text );
	$text  = preg_replace( "/\n\n+/", "\n\n", $text );
	$parts = preg_split( '/\n\s*\n/', $text, -1, PREG_SPLIT_NO_EMPTY );
	$text  = '';
	foreach ( $parts as $t ) {
		$text .= '<p>' . trim( $t, "\n" ) . "</p>\n";
	}
	$text = preg_replace( '|<p>\s*</p>|', '', $text );
	$text = preg_replace( '!<p>([^<]+)</(div|address|form)>!', '<p>$1</p></$2>', $text );
	$text = preg_replace( '!<p>\s*(</?' . $ab . '[^>]*>)\s*</p>!', '$1', $text );
	$text = preg_replace( '|<p>(<li.+?)</p>|', '$1', $text );
	$text = preg_replace( '|<p><blockquote([^>]*)>|i', '<blockquote$1><p>', $text );
	$text = str_replace( '</blockquote></p>', '</p></blockquote>', $text );
	$text = preg_replace( '!<p>\s*(</?' . $ab . '[^>]*>)!', '$1', $text );
	$text = preg_replace( '!(</?' . $ab . '[^>]*>)\s*</p>!', '$1', $text );
	if ( $br ) {
		$text = preg_replace_callback( '/<(script|style|svg|math).*?<\/\\1>/s', function ( $m ) {
			return str_replace( "\n", '<WPPreserveNewline />', $m[0] );
		}, $text );
		$text = str_replace( array( '<br>', '<br/>' ), '<br />', $text );
		$text = preg_replace( '|(?<!<br />)\s*\n|', "<br />\n", $text );
		$text = str_replace( '<WPPreserveNewline />', "\n", $text );
	}
	$text = preg_replace( '!(</?' . $ab . '[^>]*>)\s*<br />!', '$1', $text );
	$text = preg_replace( '!<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)!', '$1', $text );
	$text = preg_replace( "|\n</p>$|", '</p>', $text );
	return $text;
}
class WPS_Cruft_DB {
	public $posts    = 'wp_posts';
	public $postmeta = 'wp_postmeta';
	public $options  = 'wp_options';
	public function prepare( $q, ...$a ) {
		return json_encode( array( 'q' => $q, 'a' => $a ) );
	}
	public function update( $table, $data, $where ) {
		if ( 'wp_posts' === $table ) {
			foreach ( $data as $k => $v ) {
				$GLOBALS['WPS_STORE']['posts'][ $where['ID'] ][ $k ] = $v;
			}
			$GLOBALS['WPS_STORE']['calls'][] = 'wpdb_update_post:' . $where['ID'];
		} else {
			foreach ( $data as $k => $v ) {
				$GLOBALS['WPS_STORE']['postmeta_rows'][ $where['meta_id'] ][ $k ] = $v;
			}
			$GLOBALS['WPS_STORE']['calls'][] = 'wpdb_update_meta:' . $where['meta_id'];
		}
		return 1;
	}
	public function get_var( $p ) {
		$d = json_decode( $p, true );
		if ( false !== strpos( $d['q'], 'meta_id = %d' ) ) {
			return $GLOBALS['WPS_STORE']['postmeta_rows'][ $d['a'][0] ]['meta_value'] ?? null;
		}
		return null;
	}
	public function get_results( $p, $mode = null ) {
		$d = json_decode( $p, true );
		if ( false !== strpos( $d['q'], 'p.ID >' ) ) {
			return array_shift( $GLOBALS['WPS_STORE']['export_posts_pages'] ) ?: array();
		}
		return $GLOBALS['WPS_STORE']['export_meta_rows'] ?? array();
	}
}
$wpdb = new WPS_Cruft_DB();
$GLOBALS['wpdb'] = $wpdb;
register_shutdown_function(
	function () use ( $store_out ) {
		file_put_contents( $store_out, json_encode( $GLOBALS['WPS_STORE'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT ) );
	}
);
function wps_run_like_eval_file( $file ) {
	global $wpdb;
	include $file;
}
wps_run_like_eval_file( $script );
