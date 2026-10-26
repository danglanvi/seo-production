<?php
/**
 * Cổng bất biến wpautop. Chỉ đọc DB, không ghi. So cấu trúc hiển thị (đoạn, xuống dòng, khối) giữa giá trị hiện có trong DB
 * và bản làm sạch trong changes.json, qua đúng wpautop của WordPress. Phải 0 khác biệt trước khi ghi.
 * CHANGES=<changes.json> OUT=<ket-qua.json> wp eval-file compare_autop.php
 *   CHANGES  bắt buộc. File do cruft_clean.py sinh.
 *   OUT      bắt buộc. Kết quả {changes_md5, total, bad, diffs[]}. apply_cruft.php (DRY=0) đòi file này có bad = 0.
 * Mã thoát 0 khi bad = 0, 1 khi còn khác biệt, 2 khi thiếu đầu vào.
 */
global $wpdb;
$changes_path = getenv( 'CHANGES' );
$out_path     = getenv( 'OUT' );
if ( ! $changes_path || ! is_file( $changes_path ) || ! $out_path ) {
	fwrite( STDERR, "Cần CHANGES=<changes.json> và OUT=<ket-qua.json>\n" );
	exit( 2 );
}
if ( ! function_exists( 'wps_cruft_struct' ) ) {
	function wps_cruft_struct( $h, $autop ) {
		if ( $autop ) {
			$h = wpautop( $h );
		}
		$h = str_replace( array( '&nbsp;', "\xc2\xa0", "\xef\xbb\xbf" ), ' ', $h );
		$h = preg_replace( '#<!--.*?-->#s', '', $h );
		$h = preg_replace( '#</?(span|strong|b|em|i|a|u|sup|sub|small|mark|code|font)\b[^>]*>#i', '', $h );
		$h = preg_replace( '#<(/?)(p|br|li|ul|ol|h[1-6]|td|th|tr|table|div|figure|blockquote|iframe|img)\b[^>]*>#i', '⟨$1$2⟩', $h );
		$h = preg_replace( '#<[^>]+>#', '', $h );
		$h = preg_replace( '#\s+#u', ' ', $h );
		$h = preg_replace( '#\s*(⟨[^⟩]*⟩)\s*#u', '$1', $h );
		do {
			$h0 = $h;
			$h  = str_replace( array( '⟨p⟩⟨/p⟩', '⟨div⟩⟨/div⟩', '⟨p⟩⟨br⟩⟨/p⟩' ), '', $h );
			$h  = preg_replace( '#⟨br⟩(⟨/(?:p|li|td|th|h[1-6])⟩)#u', '$1', $h );
		} while ( $h !== $h0 );
		return trim( $h );
	}
	function wps_cruft_pairs( $a, $b, &$out ) {
		if ( is_array( $a ) && is_array( $b ) ) {
			foreach ( $a as $k => $v ) {
				if ( isset( $b[ $k ] ) ) {
					wps_cruft_pairs( $v, $b[ $k ], $out );
				}
			}
			return;
		}
		if ( is_string( $a ) && is_string( $b ) && $a !== $b ) {
			$out[] = array( $a, $b );
		}
	}
}
$ch  = json_decode( file_get_contents( $changes_path ), true );
$bad = 0;
$diffs = array();
foreach ( $ch as $c ) {
	$pairs = array();
	$label = '';
	if ( 'post' === $c['kind'] ) {
		$p     = get_post( $c['id'] );
		$label = (string) $c['slug'];
		if ( ! $p ) {
			continue;
		}
		if ( null !== $c['content'] ) {
			$pairs[] = array( $p->post_content, $c['content'], ! has_blocks( $p->post_content ) );
		}
		if ( ! empty( $c['el'] ) ) {
			$old = json_decode( (string) get_post_meta( $c['id'], '_elementor_data', true ), true );
			$new = json_decode( $c['el'], true );
			$tmp = array();
			wps_cruft_pairs( $old, $new, $tmp );
			foreach ( $tmp as $t ) {
				$pairs[] = array( $t[0], $t[1], true );
			}
		}
	} elseif ( 'meta' === $c['kind'] ) {
		$label   = 'meta ' . $c['meta_id'];
		$pairs[] = array( (string) $wpdb->get_var( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->postmeta} WHERE meta_id = %d", $c['meta_id'] ) ), $c['new'], true );
	} else {
		$label = 'option ' . $c['key'];
		$tmp   = array();
		wps_cruft_pairs( get_option( $c['key'] ), $c['new'], $tmp );
		foreach ( $tmp as $t ) {
			$pairs[] = array( $t[0], $t[1], true );
		}
	}
	foreach ( $pairs as $pr ) {
		$x = wps_cruft_struct( $pr[0], $pr[2] );
		$y = wps_cruft_struct( $pr[1], $pr[2] );
		if ( $x === $y ) {
			continue;
		}
		$bad++;
		if ( count( $diffs ) < 50 ) {
			$diffs[] = array( 'id' => $c['id'] ?? ( $c['meta_id'] ?? $c['key'] ), 'label' => $label, 'truoc' => mb_substr( $x, 0, 300 ), 'sau' => mb_substr( $y, 0, 300 ) );
		}
		break;
	}
}
$res = array( 'changes_md5' => md5_file( $changes_path ), 'total' => count( $ch ), 'bad' => $bad, 'diffs' => $diffs );
file_put_contents( $out_path, wp_json_encode( $res ) );
echo "mục khác cấu trúc wpautop: $bad / " . count( $ch ) . "\n";
exit( $bad ? 1 : 0 );
