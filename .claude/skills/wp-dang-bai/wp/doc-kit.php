<?php
/**
 * Plugin Name: doc-kit — bài theo format tài liệu pages.dev (27/10/2026)
 * Description: Bài có meta _doc_kit = 1: bọc nội dung trong <div class="doc-kit">, nạp doc-kit.css và doc-kit.js chỉ ở bài đó, in CSS riêng của bài (_doc_kit_css), bỏ wpautop.
 *   REST: meta _doc_kit, _doc_kit_css; trường doc_seo (title, description, focus_keyword của Rank Math).
 *   kses: tài khoản không có unfiltered_html (Người đăng bài) được dùng svg, button, input, label, details, video của format. Không mở <script>, <style>, on*.
 * Nguồn: SEO Production/skills/wp-dang-bai/wp/. Cài: doc-kit.php vào mu-plugins/, thư mục doc-kit/ vào wp-content/. Rollback: chuyển 2 thứ đó ra chỗ khác, purge cache.
 */
defined( 'ABSPATH' ) || exit;

add_action( 'init', function () {
	$auth = function ( $allowed, $key, $post_id ) {
		return current_user_can( 'edit_post', $post_id );
	};
	register_post_meta( 'post', '_doc_kit', [ 'type' => 'boolean', 'single' => true, 'show_in_rest' => true, 'auth_callback' => $auth ] );
	register_post_meta( 'post', '_doc_kit_css', [
		'type'              => 'string',
		'single'            => true,
		'show_in_rest'      => true,
		'auth_callback'     => $auth,
		'sanitize_callback' => function ( $css ) {
			return preg_replace( '#</?\s*(style|script)|javascript:|expression\s*\(|@import#i', '', (string) $css );
		},
	] );
} );

add_action( 'rest_api_init', function () {
	$keys = [ 'title', 'description', 'focus_keyword' ];
	register_rest_field( 'post', 'doc_seo', [
		'get_callback'    => function ( $p ) use ( $keys ) {
			$o = [];
			foreach ( $keys as $k ) {
				$o[ $k ] = (string) get_post_meta( $p['id'], 'rank_math_' . $k, true );
			}
			return $o;
		},
		'update_callback' => function ( $v, $post ) use ( $keys ) {
			foreach ( $keys as $k ) {
				if ( isset( $v[ $k ] ) ) {
					update_post_meta( $post->ID, 'rank_math_' . $k, sanitize_text_field( $v[ $k ] ) );
				}
			}
			return true;
		},
		'schema'          => [ 'type' => 'object', 'context' => [ 'edit' ], 'properties' => array_fill_keys( $keys, [ 'type' => 'string' ] ) ],
	] );
} );

add_action( 'wp', function () {
	if ( ! is_singular( 'post' ) || ! get_post_meta( get_queried_object_id(), '_doc_kit', true ) ) {
		return;
	}
	remove_filter( 'the_content', 'wpautop' );
	add_filter( 'the_content', function ( $c ) {
		if ( get_the_ID() !== get_queried_object_id() || false !== strpos( $c, 'class="doc-kit"' ) ) {
			return $c;
		}
		return '<div class="doc-kit" data-doc="' . esc_attr( get_post_field( 'post_name', get_queried_object_id() ) ) . '">' . $c . '</div>';
	}, 20 );
	add_action( 'wp_enqueue_scripts', function () {
		$dir = WP_CONTENT_DIR . '/doc-kit/'; // web không đọc được mu-plugins/ (hardening), nên asset nằm ở wp-content/doc-kit/
		$url = content_url( 'doc-kit/' );
		wp_enqueue_style( 'tg-tool-doc-kit', $url . 'doc-kit.css', [], filemtime( $dir . 'doc-kit.css' ) );
		$css = (string) get_post_meta( get_queried_object_id(), '_doc_kit_css', true );
		if ( '' !== $css ) {
			wp_add_inline_style( 'tg-tool-doc-kit', $css );
		}
		wp_enqueue_script( 'tg-tool-doc-kit', $url . 'doc-kit.js', [], filemtime( $dir . 'doc-kit.js' ), [ 'in_footer' => true, 'strategy' => 'defer' ] );
	} );
} );

add_filter( 'wp_kses_allowed_html', function ( $tags, $context ) {
	if ( 'post' !== $context ) {
		return $tags;
	}
	$svg = array_fill_keys( [
		'class', 'id', 'style', 'transform', 'fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin',
		'opacity', 'font-size', 'font-weight', 'font-family', 'font-style', 'text-anchor', 'dominant-baseline', 'letter-spacing', 'marker-start', 'marker-end', 'clip-path',
		'x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'dx', 'dy', 'width', 'height', 'd', 'points', 'offset', 'stop-color', 'stop-opacity',
		'viewbox', 'xmlns', 'preserveaspectratio', 'gradientunits', 'gradienttransform', 'markerwidth', 'markerheight', 'refx', 'refy', 'orient', 'markerunits',
		'patternunits', 'textlength', 'lengthadjust', 'role', 'aria-label', 'aria-hidden', 'focusable',
	], true );
	foreach ( [ 'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'tspan', 'defs', 'lineargradient', 'radialgradient', 'stop', 'marker', 'clippath', 'pattern', 'title', 'desc', 'symbol' ] as $t ) {
		$tags[ $t ] = $svg;
	}
	$add = [
		'button'  => [ 'type', 'class', 'disabled', 'aria-selected', 'aria-controls', 'aria-label', 'role' ],
		'input'   => [ 'type', 'class', 'id', 'name', 'value', 'checked', 'min', 'max', 'step', 'aria-label' ],
		'label'   => [ 'for', 'class', 'hidden' ],
		'details' => [ 'open', 'class', 'id' ],
		'summary' => [ 'class' ],
		'video'   => [ 'src', 'poster', 'controls', 'preload', 'playsinline', 'muted', 'loop', 'width', 'height', 'class' ],
		'source'  => [ 'src', 'type' ],
		'section' => [ 'class', 'id' ],
	];
	foreach ( $add as $t => $attrs ) {
		$tags[ $t ] = ( $tags[ $t ] ?? [] ) + array_fill_keys( $attrs, true );
	}
	foreach ( [ 'div', 'p', 'span', 'section', 'figure', 'ol', 'ul', 'li' ] as $t ) {
		$tags[ $t ]['hidden'] = true;
	}
	return function_exists( '_wp_add_global_attributes' ) ? array_map( '_wp_add_global_attributes', $tags ) : $tags;
}, 10, 2 );
