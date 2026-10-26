<?php
/**
 * Đổi widget Elementor Pro sang widget free (image, shortcode, html). Chạy được khi Pro còn bật.
 * Giữ id phần tử, ô Nâng cao (khoá bắt đầu bằng "_") và custom_css.
 * Biến:
 *   IDS="12,34"   tài liệu cần đổi (lấy từ pro_inventory.php). Bắt buộc, trừ khi có SRC_DIR.
 *   SRC_DIR=<dir> đọc _elementor_data từ file el_<id>.json thay vì DB (chạy lại trên bản backup). Chỉ dùng với DRY=1.
 *   PREFIX=site   tiền tố shortcode và class của theme: [<PREFIX>_posts], [<PREFIX>_menu], [<PREFIX>_progress], .<PREFIX>-carousel
 *   DRY=1         mặc định chỉ in log. DRY=0 cần BK=<thư mục> để lưu bản gốc el_<id>.json trước khi ghi.
 * Theme hoặc mu-plugin phải có shortcode và CSS tương ứng (xem SKILL.md mục "Phần thay cho Elementor Pro").
 * Chạy: sudo -u www HOME=/tmp/wpcli-home IDS=... PREFIX=... <php> /usr/local/bin/wp --path=<root> eval-file el_free_convert.php
 */
if ( ! defined( 'ABSPATH' ) ) { exit( 1 ); }
$dry = getenv( 'DRY' ) !== '0';
$src = getenv( 'SRC_DIR' );
$px  = preg_replace( '/[^a-z0-9]/', '', strtolower( getenv( 'PREFIX' ) ?: 'site' ) );
$bk  = getenv( 'BK' );
$log = array( 'dry' => $dry, 'ok' => array(), 'skip' => array(), 'before' => array() );
if ( ! $dry && ( $src || ! $bk || ! is_dir( $bk ) || ! is_writable( $bk ) ) ) {
	echo wp_json_encode( array( 'error' => 'DRY=0 cần BK là thư mục ghi được và không dùng SRC_DIR' ) ), "\n";
	return;
}
$ids = getenv( 'IDS' ) ? array_map( 'intval', explode( ',', getenv( 'IDS' ) ) ) : array();
if ( ! $ids && $src ) {
	foreach ( glob( rtrim( $src, '/' ) . '/el_*.json' ) as $f ) {
		$ids[] = (int) preg_replace( '/\D/', '', basename( $f ) );
	}
	sort( $ids );
}
$logo = (int) get_theme_mod( 'custom_logo' );
$keep = function ( $s ) {
	return array_filter( $s, function ( $k ) { return 0 === strpos( $k, '_' ) || 'custom_css' === $k; }, ARRAY_FILTER_USE_KEY );
};
$sc   = function ( $x, $code ) use ( $keep ) {
	return array( 'id' => $x['id'], 'elType' => 'widget', 'widgetType' => 'shortcode', 'settings' => $keep( $x['settings'] ) + array( 'shortcode' => $code ), 'elements' => array() );
};
$html = function ( $x, $markup ) use ( $keep ) {
	return array( 'id' => $x['id'], 'elType' => 'widget', 'widgetType' => 'html', 'settings' => $keep( $x['settings'] ) + array( 'html' => $markup ), 'elements' => array() );
};
$nav  = '<button type="button" class="' . $px . '-carousel__nav ' . $px . '-carousel__nav--prev" aria-label="Trước">‹</button><button type="button" class="' . $px . '-carousel__nav ' . $px . '-carousel__nav--next" aria-label="Sau">›</button>';
$img  = function ( $im ) {
	$id = (int) ( $im['id'] ?? 0 );
	if ( $id && wp_get_attachment_image_src( $id, 'large' ) ) {
		return wp_get_attachment_image( $id, 'large', false, array( 'loading' => 'lazy' ) );
	}
	return '<img src="' . esc_url( $im['url'] ?? '' ) . '" alt="" loading="lazy">';
};
$home_of = function ( $doc ) {
	$l = apply_filters( 'wpml_post_language_details', null, $doc );
	$u = home_url( '/' );
	return is_array( $l ) && ! empty( $l['language_code'] ) ? apply_filters( 'wpml_permalink', $u, $l['language_code'] ) : $u;
};
$convert = function ( $x, $doc ) use ( $sc, $html, $nav, $img, $logo, $keep, $px, $home_of ) {
	$s = $x['settings'];
	switch ( $x['widgetType'] ) {
		case 'theme-site-logo':
			$u   = wp_get_attachment_image_src( $logo, 'full' );
			$cls = trim( ( $s['_css_classes'] ?? '' ) . ' elementor-widget-theme-site-logo' );
			return array( 'id' => $x['id'], 'elType' => 'widget', 'widgetType' => 'image', 'elements' => array(),
				'settings' => array( '_css_classes' => $cls ) + $keep( $s ) + array( 'image' => array( 'id' => $logo, 'url' => $u[0] ?? '' ), 'image_size' => 'full', 'align' => $s['align'] ?? 'left', 'width' => $s['width'] ?? array(), 'link_to' => 'custom', 'link' => array( 'url' => $home_of( $doc ) ) ) );
		case 'progress-tracker':
			return $sc( $x, "[{$px}_progress]" );
		case 'nav-menu':
			return $sc( $x, "[{$px}_menu menu=\"" . esc_attr( $s['menu'] ?? '' ) . '" label="Menu"]' );
		case 'template':
			return $sc( $x, '[elementor-template id="' . (int) $s['template_id'] . '"]' );
		case 'posts':
			$p = 'cards' === ( $s['_skin'] ?? 'classic' ) ? 'cards_' : 'classic_';
			$a = array(
				'count'   => (int) ( $s[ $p . 'posts_per_page' ] ?? 6 ),
				'cols'    => (int) ( $s[ $p . 'columns' ] ?? 3 ),
				'thumb'   => 'none' === ( $s[ $p . 'thumbnail' ] ?? 'top' ) ? 0 : 1,
				'date'    => in_array( 'date', (array) ( $s[ $p . 'meta_data' ] ?? array( 'date', 'comments' ) ), true ) ? 1 : 0,
				'excerpt' => '' === ( $s[ $p . 'show_excerpt' ] ?? 'yes' ) ? 0 : (int) ( $s[ $p . 'excerpt_length' ] ?? 25 ),
			);
			$code = "[{$px}_posts";
			foreach ( $a as $k => $v ) {
				$code .= " $k=\"$v\"";
			}
			return $sc( $x, $code . ']' );
		case 'testimonial-carousel':
			$per = (int) ( $s['slides_per_view'] ?? 1 ) ?: 1;
			$o   = "<div class=\"{$px}-carousel {$px}-testi\" style=\"--per:$per\"><div class=\"{$px}-carousel__track\">";
			foreach ( $s['slides'] as $sl ) {
				$o .= "<figure class=\"{$px}-testi__item\"><blockquote class=\"{$px}-testi__content\">" . wp_kses_post( $sl['content'] ?? '' ) . "</blockquote><figcaption class=\"{$px}-testi__footer\">" . ( ! empty( $sl['image']['url'] ) ? $img( $sl['image'] ) : '' ) . "<span><span class=\"{$px}-testi__name\">" . esc_html( $sl['name'] ?? '' ) . "</span><span class=\"{$px}-testi__title\">" . esc_html( $sl['title'] ?? '' ) . '</span></span></figcaption></figure>';
			}
			return $html( $x, $o . '</div>' . ( count( $s['slides'] ) > $per ? $nav : '' ) . '</div>' );
		case 'media-carousel':
			$per = 'slideshow' === ( $s['skin'] ?? '' ) ? 1 : ( (int) ( $s['slides_per_view'] ?? 3 ) ?: 3 );
			$h   = (int) ( $s['height']['size'] ?? 400 ) ?: 400;
			$o   = "<div class=\"{$px}-carousel {$px}-media\" style=\"--per:$per;--h:{$h}px\"><div class=\"{$px}-carousel__track\">";
			foreach ( $s['slides'] as $sl ) {
				$o .= "<div class=\"{$px}-media__item\">" . $img( $sl['image'] ?? array() ) . '</div>';
			}
			return $html( $x, $o . '</div>' . $nav . '</div>' );
		case 'slides':
			$h = (int) ( $s['slides_height']['size'] ?? 350 ) ?: 350;
			$o = "<div class=\"{$px}-carousel {$px}-slides\" style=\"--per:1;--h:{$h}px\"><div class=\"{$px}-carousel__track\">";
			foreach ( $s['slides'] as $sl ) {
				$o .= "<div class=\"{$px}-slide\" style=\"background-image:url(" . esc_url( $sl['background_image']['url'] ?? '' ) . ')"><h3>' . esc_html( $sl['heading'] ?? '' ) . '</h3></div>';
			}
			return $html( $x, $o . '</div>' . $nav . '</div>' );
	}
	return null;
};
$walk = function ( &$els, $doc, $path ) use ( &$walk, $convert, &$log ) {
	$n = 0;
	foreach ( $els as $i => &$x ) {
		if ( 'widget' === ( $x['elType'] ?? '' ) ) {
			$new = $convert( $x, $doc );
			if ( $new ) {
				$log['ok'][] = "$doc $path/$i {$x['widgetType']} → {$new['widgetType']}";
				$x = $new;
				$n++;
			}
		}
		if ( ! empty( $x['elements'] ) ) {
			$n += $walk( $x['elements'], $doc, "$path/$i/elements" );
		}
	}
	return $n;
};
foreach ( $ids as $doc ) {
	$raw = $src ? (string) @file_get_contents( rtrim( $src, '/' ) . "/el_$doc.json" ) : get_post_meta( $doc, '_elementor_data', true );
	$d   = json_decode( $raw, true );
	if ( ! $d ) {
		$log['skip'][] = "$doc: không đọc được _elementor_data";
		continue;
	}
	if ( ! $walk( $d, $doc, '' ) ) {
		$log['skip'][] = "$doc: không có widget Pro cần đổi";
		continue;
	}
	$log['before'][ $doc ] = md5( $raw );
	if ( ! $dry ) {
		file_put_contents( rtrim( $bk, '/' ) . "/el_$doc.json", $raw );
		update_post_meta( $doc, '_elementor_data', wp_slash( wp_json_encode( $d ) ) );
		delete_post_meta( $doc, '_elementor_element_cache' );
		( new \Elementor\Core\Files\CSS\Post( $doc ) )->update();
	}
}
echo wp_json_encode( $log, JSON_UNESCAPED_UNICODE ), "\n";
