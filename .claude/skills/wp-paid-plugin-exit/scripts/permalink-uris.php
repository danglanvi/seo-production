<?php
/**
 * Plugin Name: Permalink URIs
 * Description: Thay Permalink Manager Pro bằng bản đồ URL tĩnh. Bản đồ ở permalink-uris.json cùng thư mục, sinh bằng pm_export.php.
 * Chỉ chạy khi Permalink Manager tắt. Map: {"<id>": "<uri>", "tax-<term_id>": "<uri>"}; URI không có / đầu và cuối, đã gồm tiền tố ngôn ngữ.
 */
defined( 'ABSPATH' ) || exit;

function pu_map() {
	static $m = null;
	if ( null === $m ) {
		$f = __DIR__ . '/permalink-uris.json';
		$m = is_readable( $f ) ? (array) json_decode( (string) file_get_contents( $f ), true ) : array();
	}
	return $m;
}

function pu_url( $uri ) {
	// Dùng option home thô: home_url() có filter ngôn ngữ của WPML sẽ thêm tiền tố lần nữa.
	return user_trailingslashit( rtrim( (string) get_option( 'home' ), '/' ) . '/' . $uri );
}

// Tra path của request trong bản đồ. Trả [khoá, số trang] hoặc null.
function pu_lookup( $path ) {
	static $rev = null;
	if ( null === $rev ) {
		$rev = array_flip( array_map( 'strtolower', pu_map() ) );
	}
	$path = strtolower( trim( rawurldecode( (string) $path ), '/' ) );
	$page = 0;
	if ( preg_match( '#^(.+)/page/(\d+)$#', $path, $mm ) ) {
		$path = $mm[1];
		$page = (int) $mm[2];
	}
	return isset( $rev[ $path ] ) ? array( (string) $rev[ $path ], $page ) : null;
}

if ( defined( 'PERMALINK_MANAGER_VERSION' ) || class_exists( 'Permalink_Manager_Class' ) ) {
	return;
}

add_filter( 'request', function ( $qv ) {
	$hit = pu_lookup( $GLOBALS['wp']->request ?? '' );
	if ( ! $hit ) {
		return $qv;
	}
	list( $key, $page ) = $hit;
	if ( 0 === strpos( $key, 'tax-' ) ) {
		$t = get_term( (int) substr( $key, 4 ) );
		if ( ! $t || is_wp_error( $t ) ) {
			return $qv;
		}
		$new = 'category' === $t->taxonomy ? array( 'cat' => $t->term_id ) : ( 'post_tag' === $t->taxonomy ? array( 'tag_id' => $t->term_id ) : array( $t->taxonomy => $t->slug ) );
		return $new + ( $page ? array( 'paged' => $page ) : array() );
	}
	$id   = (int) $key;
	$type = get_post_type( $id );
	if ( ! $type ) {
		return $qv;
	}
	return 'page' === $type ? array( 'page_id' => $id ) : array( 'p' => $id, 'post_type' => $type );
}, 1 );

$pu_post_link = function ( $link, $post ) {
	$id = is_object( $post ) ? $post->ID : (int) $post;
	$m  = pu_map();
	return isset( $m[ (string) $id ] ) && 'publish' === get_post_status( $id ) ? pu_url( $m[ (string) $id ] ) : $link;
};
add_filter( 'post_link', $pu_post_link, 99, 2 );
add_filter( 'page_link', $pu_post_link, 99, 2 );
add_filter( 'post_type_link', $pu_post_link, 99, 2 );
add_filter( 'term_link', function ( $link, $term ) {
	$m = pu_map();
	return isset( $m[ 'tax-' . $term->term_id ] ) ? pu_url( $m[ 'tax-' . $term->term_id ] ) : $link;
}, 99, 2 );

// URL gốc của WordPress (slug mặc định) 301 về URI trong bản đồ.
add_action( 'template_redirect', function () {
	if ( ! is_singular() && ! is_category() && ! is_tag() && ! is_tax() ) {
		return;
	}
	$m   = pu_map();
	$key = is_singular() ? (string) get_queried_object_id() : 'tax-' . get_queried_object_id();
	if ( ! isset( $m[ $key ] ) || is_paged() ) {
		return;
	}
	$path = trim( (string) wp_parse_url( (string) ( $_SERVER['REQUEST_URI'] ?? '' ), PHP_URL_PATH ), '/' );
	if ( strtolower( rawurldecode( $path ) ) !== strtolower( $m[ $key ] ) ) {
		$q = (string) wp_parse_url( (string) ( $_SERVER['REQUEST_URI'] ?? '' ), PHP_URL_QUERY );
		wp_safe_redirect( pu_url( $m[ $key ] ) . ( '' !== $q ? '?' . $q : '' ), 301 );
		exit;
	}
}, 1 );
