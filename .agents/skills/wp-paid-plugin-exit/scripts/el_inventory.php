<?php
/* Kiểm kê phần Elementor Pro đang dùng: widget Pro, Custom CSS, sticky, motion, thuộc tính, link popup, điều kiện Theme Builder. Chỉ đọc. In JSON. */
if ( ! defined( "ABSPATH" ) ) { exit( 1 ); }
global $wpdb;
$pro_widgets = array( 'posts', 'portfolio', 'gallery', 'form', 'login', 'slides', 'nav-menu', 'animated-headline', 'hotspot', 'price-list', 'price-table', 'flip-box', 'call-to-action', 'media-carousel', 'testimonial-carousel', 'reviews', 'table-of-contents', 'countdown', 'share-buttons', 'blockquote', 'facebook-button', 'facebook-comments', 'facebook-embed', 'facebook-page', 'template', 'theme-site-logo', 'theme-site-title', 'theme-page-title', 'theme-post-title', 'theme-post-excerpt', 'theme-post-featured-image', 'theme-archive-title', 'archive-posts', 'post-info', 'post-navigation', 'post-comments', 'author-box', 'sitemap', 'breadcrumbs', 'lottie', 'paypal-button', 'stripe-button', 'progress-tracker', 'video-playlist', 'code-highlight', 'search-form', 'loop-grid', 'loop-carousel', 'mega-menu', 'nested-carousel', 'off-canvas', 'link-in-bio' );
$rows = $wpdb->get_results( "SELECT p.ID, p.post_type, p.post_status, p.post_title, m.meta_value FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id = p.ID AND m.meta_key = '_elementor_data' WHERE p.post_status IN ('publish','private','draft') AND p.post_type NOT IN ('revision')" );
$out = array();
foreach ( $rows as $r ) {
	$d = json_decode( $r->meta_value, true );
	if ( ! is_array( $d ) ) {
		continue;
	}
	$info = array( 'pro' => array(), 'css' => 0, 'sticky' => 0, 'motion' => 0, 'attrs' => 0, 'popup_links' => 0 );
	$walk = function ( $els ) use ( &$walk, &$info, $pro_widgets ) {
		foreach ( (array) $els as $e ) {
			$s = $e['settings'] ?? array();
			if ( ( $e['elType'] ?? '' ) === 'widget' && in_array( $e['widgetType'] ?? '', $pro_widgets, true ) ) {
				$info['pro'][ $e['widgetType'] ] = ( $info['pro'][ $e['widgetType'] ] ?? 0 ) + 1;
			}
			if ( ! empty( $s['custom_css'] ) ) {
				$info['css']++;
			}
			if ( ! empty( $s['sticky'] ) ) {
				$info['sticky']++;
			}
			foreach ( $s as $k => $v ) {
				if ( strpos( $k, 'motion_fx' ) === 0 && $v && 'yes' === $v ) {
					$info['motion']++;
					break;
				}
			}
			if ( ! empty( $s['_attributes'] ) ) {
				$info['attrs']++;
			}
			$j = wp_json_encode( $s );
			$info['popup_links'] += substr_count( $j, 'popup%3Aopen' ) + substr_count( $j, 'popup:open' );
			
			$walk( $e['elements'] ?? array() );
		}
	};
	$walk( $d );
	$ps = get_post_meta( $r->ID, '_elementor_page_settings', true );
	if ( is_array( $ps ) && ! empty( $ps['custom_css'] ) ) {
		$info['css']++;
		$info['page_css'] = 1;
	}
	if ( $info['pro'] || $info['css'] || $info['sticky'] || $info['motion'] || $info['attrs'] || $info['popup_links'] ) {
		$out[] = array( 'id' => (int) $r->ID, 'type' => $r->post_type, 'status' => $r->post_status, 'title' => $r->post_title, 'tpl_type' => get_post_meta( $r->ID, '_elementor_template_type', true ), 'url' => 'publish' === $r->post_status && 'elementor_library' !== $r->post_type ? wp_make_link_relative( get_permalink( $r->ID ) ) : '' ) + $info;
	}
}
echo wp_json_encode( array( 'docs' => $out, 'conditions' => get_option( 'elementor_pro_theme_builder_conditions' ), 'pro_version' => defined( 'ELEMENTOR_PRO_VERSION' ) ? ELEMENTOR_PRO_VERSION : null ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES );
