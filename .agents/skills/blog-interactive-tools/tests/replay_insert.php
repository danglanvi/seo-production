<?php
/* Phát lại insert_shortcode.php ngoài WordPress (stub tối thiểu), DRY=1 + SRC.
 * php tests/replay_insert.php <plan.json> <src.json>  → in JSON vị trí chèn. */
define( 'ABSPATH', '/tmp/' );
$wpdb = null;
function has_blocks( $c ) { return false !== strpos( (string) $c, '<!-- wp:' ); }
function wp_strip_all_tags( $s ) { return trim( strip_tags( preg_replace( '@<(script|style)[^>]*?>.*?</\1>@si', '', $s ) ) ); }
function get_post_meta( $id, $k, $s ) { return ''; }
function wp_json_encode( $d, $f = 0 ) { return json_encode( $d, $f ); }
putenv( 'PLAN=' . $argv[1] );
putenv( 'SRC=' . $argv[2] );
putenv( 'DRY=1' );
putenv( 'SC=gtv_tool' );
require dirname( __DIR__ ) . '/scripts/insert_shortcode.php';
