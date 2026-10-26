<?php
/**
 * Purge LiteSpeed theo danh sách URL. Không purge toàn site.
 * Không gọi litespeed_purge_post: site đặt purge-post_all=1 thì purge theo post sẽ purge "*".
 * Tag URL của LiteSpeed bỏ query string, nên một lệnh purge xoá mọi biến thể của URL đó (mobile, guest, webp).
 * Trong WP-CLI, LiteSpeed xếp lệnh vào hàng đợi và gửi ở request PHP kế tiếp: gọi 1 request không cache sau khi chạy.
 * Biến: URLS="/a/,/b/" (bắt buộc, path tương đối), DRY=1 mặc định (chỉ liệt kê), MAX=20.
 * Chạy: sudo -u www HOME=/tmp/wpcli-home URLS="/,/dich-vu/" DRY=0 <php> /usr/local/bin/wp --path=<root> eval-file purge_urls.php 2>/dev/null | grep '^{'
 * Output chỉ in path, không in host.
 */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
$dry  = getenv( 'DRY' ) !== '0';
$max  = (int) ( getenv( 'MAX' ) ?: 20 );
$urls = array_values( array_unique( array_filter( array_map( 'trim', explode( ',', (string) getenv( 'URLS' ) ) ), function ( $u ) {
	return '' !== $u && '/' === $u[0] && ! preg_match( '#[*<?\s]#', $u );
} ) ) );
$out = [
	'mode'           => $dry ? 'DRY' : 'PURGE',
	'urls'           => $urls,
	'purge_url_hook' => has_action( 'litespeed_purge_url' ) ? 'yes' : 'NO',
	'purge-post_all' => get_option( 'litespeed.conf.purge-post_all' ),
];
$emit = function () use ( &$out ) { echo wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ), "\n"; };
if ( ! $urls || count( $urls ) > $max ) {
	$out['status'] = 'skip'; $out['reason'] = "URLS rỗng hoặc dài hơn MAX=$max"; $emit(); return;
}
if ( $dry ) { $out['status'] = 'would_purge'; $emit(); return; }
if ( 'yes' !== $out['purge_url_hook'] ) { $out['status'] = 'skip'; $out['reason'] = 'không có hook purge của LiteSpeed'; $emit(); return; }
if ( ! defined( 'LITESPEED_PURGE_SILENT' ) ) { define( 'LITESPEED_PURGE_SILENT', true ); }
foreach ( $urls as $u ) { do_action( 'litespeed_purge_url', $u ); }
$q = (string) get_option( 'litespeed.purge.queue' );
$out['status'] = false !== strpos( $q, '*' ) ? 'WARN: hàng đợi có "*" do nguồn khác thêm' : 'queued';
$emit();
