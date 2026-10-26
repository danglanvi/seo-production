<?php
/**
 * Plugin Name: WPS LCP priority
 * Description: Bỏ lazy-load và gắn fetchpriority="high" cho ảnh LCP của từng template. Mẫu của skill wp-pagespeed, gốc đã chạy trên production 16/10/2026. Tắt: chuyển file ra khỏi mu-plugins rồi purge cache LiteSpeed.
 *
 * Cách dùng: sửa $wps_lcp_rules theo phần tử LCP mà PSI báo cho từng template, kiểm `php -l`, chép vào wp-content/mu-plugins/, purge, đo lại template đó.
 * Chạy trên filter litespeed_buffer_before (trước bước lazy-load của LiteSpeed). Site không dùng LiteSpeed: đổi sang output buffer của plugin cache tương ứng.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
 * Mỗi luật: src = chuỗi có trong src của ảnh; cls = chuỗi có trong thẻ img ('' nếu không cần); dev = 'mobile' | 'desktop' | 'all'.
 * after = chuỗi HTML đánh dấu vùng bắt đầu tìm, ví dụ class của card nổi bật đầu tiên ở trang blog ('' nếu tìm từ đầu trang). Với after, src có thể để ''.
 */
$GLOBALS['wps_lcp_rules'] = array(
	// array( 'src' => '/uploads/2026/01/hero-mobile.png', 'cls' => '', 'dev' => 'mobile', 'after' => '' ),
	// array( 'src' => '', 'cls' => '', 'dev' => 'all', 'after' => 'class="feat-card-large"' ),
);
// Post type có ảnh đại diện là LCP, ví dụ array( 'customer-stories' ). Để trống nếu LCP của bài là chữ.
$GLOBALS['wps_lcp_thumb_types'] = array();

function wps_lcp_mark_img( $tag ) {
	if ( false === stripos( $tag, 'data-no-lazy' ) ) {
		$tag = preg_replace( '#^<img\b#i', '<img data-no-lazy="1"', $tag );
	}
	$tag = preg_replace( '#\sloading=(["\'])lazy\1#i', ' loading="eager"', $tag );
	if ( false === stripos( $tag, 'fetchpriority' ) ) {
		$tag = preg_replace( '#^<img\b#i', '<img fetchpriority="high"', $tag );
	}
	return $tag;
}

// Đánh dấu ảnh đầu tiên khớp $match (callback nhận thẻ img, trả true/false), bắt đầu tìm từ vị trí $from.
function wps_lcp_mark_first( $html, $match, $from = 0 ) {
	if ( ! preg_match_all( '#<img\b[^>]*>#i', $html, $m, PREG_OFFSET_CAPTURE, $from ) ) {
		return $html;
	}
	foreach ( $m[0] as $hit ) {
		if ( $match( $hit[0] ) ) {
			return substr_replace( $html, wps_lcp_mark_img( $hit[0] ), $hit[1], strlen( $hit[0] ) );
		}
	}
	return $html;
}

add_filter(
	'litespeed_buffer_before',
	function ( $html ) {
		if ( ! is_string( $html ) || is_admin() || false === stripos( $html, '<img' ) || false === stripos( $html, '</html>' ) ) {
			return $html;
		}
		$dev = wp_is_mobile() ? 'mobile' : 'desktop';

		// 1. Ảnh WordPress đã chọn làm ứng viên LCP (fetchpriority="high") thì không lazy-load.
		$html = preg_replace_callback(
			'#<img\b[^>]*\bfetchpriority=(["\'])high\1[^>]*>#i',
			function ( $m ) {
				return wps_lcp_mark_img( $m[0] );
			},
			$html
		);

		// 2. Luật theo template.
		foreach ( $GLOBALS['wps_lcp_rules'] as $r ) {
			if ( 'all' !== $r['dev'] && $dev !== $r['dev'] ) {
				continue;
			}
			if ( '' !== $r['src'] && false === strpos( $html, $r['src'] ) ) {
				continue;
			}
			$from = 0;
			if ( '' !== $r['after'] ) {
				$from = strpos( $html, $r['after'] );
				if ( false === $from ) {
					continue;
				}
			}
			$html = wps_lcp_mark_first(
				$html,
				function ( $tag ) use ( $r ) {
					return ( '' === $r['src'] || false !== strpos( $tag, $r['src'] ) ) && ( '' === $r['cls'] || false !== strpos( $tag, $r['cls'] ) );
				},
				$from
			);
		}

		// 3. Ảnh đại diện của bài, chỉ ở post type mà PSI báo ảnh đại diện là LCP.
		if ( $GLOBALS['wps_lcp_thumb_types'] && is_singular( $GLOBALS['wps_lcp_thumb_types'] ) && has_post_thumbnail() ) {
			$thumb = get_the_post_thumbnail_url( get_queried_object_id(), 'full' );
			if ( $thumb ) {
				$base = preg_replace( '#\.(jpe?g|png|webp)$#i', '', wp_basename( $thumb ) );
				$html = wps_lcp_mark_first(
					$html,
					function ( $tag ) use ( $base ) {
						return false !== strpos( $tag, $base );
					}
				);
			}
		}

		return $html;
	},
	5
);
