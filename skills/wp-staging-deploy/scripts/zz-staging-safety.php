<?php
/* mu-plugin chỉ dùng cho staging: không gửi email, noindex, chặn robots, tắt cache LiteSpeed.
 * Cần WP_ENVIRONMENT_TYPE = 'staging' trong wp-config của staging. Gọi /?stg_purge=1 để xoá cache LiteSpeed còn sót.
 * Không chép file này lên production (đặt trong --skip của merge3.py). */
if ( ! defined( 'WP_ENVIRONMENT_TYPE' ) || WP_ENVIRONMENT_TYPE !== 'staging' ) { return; }
add_filter( 'pre_wp_mail', '__return_true' );
add_filter( 'pre_option_blog_public', function () { return '0'; } );
add_filter( 'robots_txt', function () { return "User-agent: *\nDisallow: /\n"; }, 999 );
add_action( 'send_headers', function () {
	header( 'X-Robots-Tag: noindex, nofollow', true );
	header( 'X-LiteSpeed-Cache-Control: no-cache', true );
	if ( isset( $_GET['stg_purge'] ) ) { header( 'X-LiteSpeed-Purge: *', true ); }
} );
