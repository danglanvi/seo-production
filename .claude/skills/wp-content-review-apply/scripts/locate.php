<?php
/**
 * Chỉ đọc: tìm nơi lưu của một chữ cũ trước khi viết op text, fix.
 * Chạy: NEEDLES=/tmp/needles.json [OUT=/tmp/locate.json] [SKIP_META=1] [SKIP_OPTIONS=1] wp eval-file locate.php
 * NEEDLES: [{"id": "...", "needle": "chữ cần tìm"}].
 * Mỗi hit: post, type, status, where (post_content, post_title, meta:<key>, option:<tên>), count (số lần khớp đúng chữ).
 * Khớp sau khi chuẩn hoá NFC, NBSP thành dấu cách, gộp khoảng trắng. Chữ trong _elementor_data tìm được dù JSON escape \uXXXX.
 * LIKE của MySQL không phân biệt dấu, nên script đếm lại bằng regex đúng chữ và bỏ hit có count 0.
 * Quét postmeta bằng LIKE rất nặng trên DB lớn. Luật lane: không chạy trên production. Dùng staging, hoặc đặt SKIP_META=1.
 * Thoát mã 1 khi thiếu NEEDLES hoặc OUT đã có.
 */
if ( ! defined( 'ABSPATH' ) && isset( $argv ) && in_array( '--help', $argv, true ) ) {
	echo "locate.php: xem chú thích đầu file. Chạy qua wp eval-file với biến môi trường NEEDLES, OUT, SKIP_META, SKIP_OPTIONS.\n";
	exit( 0 );
}
global $wpdb;

function wpl_nfc( $s ) {
	return ( is_string( $s ) && class_exists( 'Normalizer' ) ) ? Normalizer::normalize( $s, Normalizer::FORM_C ) : $s;
}

function wpl_regex( $needle ) {
	$parts = preg_split( '/[\s\x{00A0}\x{202F}]+/u', trim( wpl_nfc( $needle ) ) );
	return '~' . implode(
		'[\s\x{00A0}\x{202F}]+',
		array_map(
			function ( $p ) {
				return preg_quote( $p, '~' );
			},
			$parts
		)
	) . '~u';
}

// Chuỗi dài nhất không có khoảng trắng: dùng cho LIKE để không trượt vì NBSP.
function wpl_token( $needle ) {
	$best = '';
	foreach ( preg_split( '/[\s\x{00A0}\x{202F}]+/u', wpl_nfc( $needle ) ) as $w ) {
		if ( mb_strlen( $w ) > mb_strlen( $best ) ) {
			$best = $w;
		}
	}
	return $best;
}

// Gom mọi chuỗi trong giá trị JSON đã giải mã, nối bằng xuống dòng.
function wpl_strings( $v ) {
	if ( is_string( $v ) ) {
		return $v . "\n";
	}
	$o = '';
	if ( is_array( $v ) ) {
		foreach ( $v as $x ) {
			$o .= wpl_strings( $x );
		}
	}
	return $o;
}

function wpl_count( $value, $re ) {
	if ( ! is_string( $value ) ) {
		return 0;
	}
	$n = (int) preg_match_all( $re, wpl_nfc( $value ) );
	if ( ! $n && in_array( substr( ltrim( $value ), 0, 1 ), array( '[', '{' ), true ) ) {
		$d = json_decode( $value, true );
		if ( is_array( $d ) ) {
			$n = (int) preg_match_all( $re, wpl_nfc( wpl_strings( $d ) ) );
		}
	}
	return $n;
}

$nf = getenv( 'NEEDLES' );
if ( ! $nf || ! is_readable( $nf ) ) {
	fwrite( STDERR, "Thiếu NEEDLES hoặc không đọc được file\n" );
	exit( 1 );
}
$in = json_decode( (string) file_get_contents( $nf ), true );
if ( ! is_array( $in ) ) {
	fwrite( STDERR, "NEEDLES không phải JSON mảng\n" );
	exit( 1 );
}
$out_file = getenv( 'OUT' );
if ( $out_file && file_exists( $out_file ) ) {
	fwrite( STDERR, "OUT đã có, không ghi đè: $out_file\n" );
	exit( 1 );
}
$out = array();
foreach ( $in as $n ) {
	$needle = wpl_nfc( (string) ( $n['needle'] ?? '' ) );
	if ( '' === trim( $needle ) ) {
		continue;
	}
	$re    = wpl_regex( $needle );
	$tok   = wpl_token( $needle );
	$like  = '%' . $wpdb->esc_like( $tok ) . '%';
	$likej = '%' . $wpdb->esc_like( trim( (string) wp_json_encode( $tok ), '"' ) ) . '%';
	$hits  = array();
	foreach ( (array) $wpdb->get_results( $wpdb->prepare( "SELECT ID, post_status, post_type, post_content, post_title FROM {$wpdb->posts} WHERE post_status IN ('publish','draft','private','future') AND post_type NOT IN ('revision') AND (post_content LIKE %s OR post_title LIKE %s)", $like, $like ), ARRAY_A ) as $r ) {
		foreach ( array( 'post_title', 'post_content' ) as $col ) {
			$c = wpl_count( $r[ $col ], $re );
			if ( $c ) {
				$hits[] = array( 'post' => (int) $r['ID'], 'type' => $r['post_type'], 'status' => $r['post_status'], 'where' => $col, 'count' => $c );
			}
		}
	}
	if ( getenv( 'SKIP_META' ) !== '1' ) {
		foreach ( (array) $wpdb->get_results( $wpdb->prepare( "SELECT m.post_id, m.meta_key, m.meta_value, p.post_status, p.post_type FROM {$wpdb->postmeta} m JOIN {$wpdb->posts} p ON p.ID = m.post_id WHERE p.post_type <> 'revision' AND (m.meta_value LIKE %s OR m.meta_value LIKE %s)", $like, $likej ), ARRAY_A ) as $r ) {
			$c = wpl_count( $r['meta_value'], $re );
			if ( $c ) {
				$hits[] = array( 'post' => (int) $r['post_id'], 'type' => $r['post_type'], 'status' => $r['post_status'], 'where' => 'meta:' . $r['meta_key'], 'count' => $c );
			}
		}
	}
	if ( getenv( 'SKIP_OPTIONS' ) !== '1' ) {
		foreach ( (array) $wpdb->get_results( $wpdb->prepare( "SELECT option_name, option_value FROM {$wpdb->options} WHERE option_value LIKE %s OR option_value LIKE %s", $like, $likej ), ARRAY_A ) as $r ) {
			$c = wpl_count( (string) $r['option_value'], $re );
			if ( $c ) {
				$hits[] = array( 'where' => 'option:' . $r['option_name'], 'count' => $c );
			}
		}
	}
	$out[] = array( 'id' => $n['id'] ?? '', 'needle' => $needle, 'hits' => $hits );
}
$json = wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE );
if ( $out_file ) {
	if ( false === file_put_contents( $out_file, $json . "\n", LOCK_EX ) ) {
		fwrite( STDERR, "Không ghi được OUT: $out_file\n" );
		exit( 1 );
	}
	echo 'OUT ' . $out_file . ' needles=' . count( $out ) . "\n";
} else {
	echo $json, "\n";
}
