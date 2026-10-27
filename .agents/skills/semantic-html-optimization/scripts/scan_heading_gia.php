<?php
// scan_heading_gia.php (semantic-html-optimization). Chỉ đọc. Chạy: OUT=<file.jsonl> IDS=<id,id,...> wp eval-file scan_heading_gia.php
// Quét bằng wpautop(post_content), không quét chuỗi thô: dòng <strong>X</strong> đứng ngay sau </ul> hoặc [/caption] chỉ cách một lần xuống dòng
// vẫn được wpautop bọc thành <p><strong> (site agency mẫu 27/10/2026: lần quét thô sót 142 đoạn ở 48 bài).
// Tìm đoạn <p> chỉ chứa <strong>/<b> (3-80 ký tự), không trong li/td/th/blockquote/figcaption/a/button, không dính <br />.
// Đánh dấu mọi thẻ strong/b thô bằng data-shk=k để biết vị trí thô của đoạn. OUT=<file JSONL> (chưa tồn tại). IDS=danh sách ID bài, bắt buộc.
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
$out = getenv( 'OUT' ); $ids = array_filter( array_map( 'intval', explode( ',', (string) getenv( 'IDS' ) ) ) );
if ( ! $out || file_exists( $out ) || ! $ids ) { echo "thiếu OUT/IDS hoặc OUT đã có\n"; exit( 1 ); }
$fh = fopen( $out, 'w' ); $n = 0;
foreach ( $ids as $id ) {
	$p = get_post( $id ); if ( ! $p ) { continue; }
	$raw = $p->post_content;
	if ( ! preg_match_all( '~<(strong|b)(\s[^>]*)?>~i', $raw, $m, PREG_OFFSET_CAPTURE ) ) { continue; }
	$marked = $raw;
	for ( $i = count( $m[0] ) - 1; $i >= 0; $i-- ) {
		$tag = $m[1][ $i ][0]; $pos = $m[1][ $i ][1] + strlen( $tag );
		$marked = substr( $marked, 0, $pos ) . ' data-shk="' . $i . '"' . substr( $marked, $pos );
	}
	$h = wpautop( $marked );
	preg_match_all( '~<p(?:\s[^>]*)?>\s*<(strong|b)\s+data-shk="(\d+)"[^>]*>((?:(?!</\1>).){1,400}?)</\1>\s*</p>~is', $h, $c, PREG_OFFSET_CAPTURE );
	$cands = array();
	foreach ( $c[0] as $j => $hit ) {
		$k = (int) $c[2][ $j ][0]; $inner = $c[3][ $j ][0];
		if ( preg_match( '~<(?!/?(?:span|em|i|u|font)\b)[a-z]~i', $inner ) ) { continue; }
		$txt = trim( preg_replace( '~[\s\x{00A0}]+~u', ' ', html_entity_decode( strip_tags( $inner ), ENT_QUOTES, 'UTF-8' ) ) );
		$len = mb_strlen( $txt );
		if ( $len < 3 || $len > 80 ) { continue; }
		$before = substr( $h, 0, $hit[1] );
		$depth = array();
		if ( preg_match_all( '~<(/?)(td|th|li|blockquote|figcaption|button|a|summary|details|dd|dt|table)\b[^>]*>~i', $before, $o, PREG_SET_ORDER ) ) {
			foreach ( $o as $t ) { $nm = strtolower( $t[2] ); $depth[ $nm ] = ( $depth[ $nm ] ?? 0 ) + ( '/' === $t[1] ? -1 : 1 ); }
		}
		$cont = array(); foreach ( $depth as $nm => $d ) { if ( $d > 0 ) { $cont[] = $nm; } }
		$ro = $m[0][ $k ][1]; // vị trí thô của thẻ mở
		$close = stripos( $raw, '</' . $m[1][ $k ][0] . '>', $ro );
		$cands[] = array( 'k' => $k, 'raw_start' => $ro, 'raw_end' => $close === false ? null : $close + strlen( $m[1][ $k ][0] ) + 3, 'tag' => strtolower( $m[1][ $k ][0] ), 'text' => $txt, 'container' => $cont, 'h_start' => $hit[1], 'h_end' => $hit[1] + strlen( $hit[0] ) );
	}
	if ( ! $cands ) { continue; }
	$hh = preg_replace( '~ data-shk="\d+"~', '', $h );
	fwrite( $fh, json_encode( array( 'post' => $id, 'cands' => $cands, 'h' => $h ), JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE ) . "\n" ); $n++;
}
fclose( $fh ); echo "ok bài có ứng viên: $n\n";
