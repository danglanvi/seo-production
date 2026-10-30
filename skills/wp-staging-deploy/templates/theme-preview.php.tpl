<?php
/**
 * Plugin Name: Xem trước theme (tạm)
 * Description: Xem trước theme __PREVIEW_THEME__ khi URL có ?thp=<mã> hoặc cookie thp đúng mã. Không có mã thì không làm gì. Gỡ: đổi đuôi .off.
 * Version: 1.3.0
 *
 * Mẫu của skill wp-staging-deploy, references/khong-co-staging.md. Điền 3 chỗ __…__ trên máy người vận hành.
 * Mã 32 ký tự chỉ nằm trong bản trên server và trong file 0600 của người vận hành. Không đưa mã vào repo, báo cáo hay ảnh.
 */
defined('ABSPATH') || exit;

(function () {
	$code    = '__PREVIEW_CODE__';
	$base    = '__BASE_THEME__';
	$preview = '__PREVIEW_THEME__';

	$given    = '';
	$from_get = false;
	if (isset($_GET['thp']) && is_string($_GET['thp'])) {
		$given    = $_GET['thp'];
		$from_get = true;
	} elseif (isset($_COOKIE['thp']) && is_string($_COOKIE['thp'])) {
		$given = $_COOKIE['thp'];
	}
	if ($given === '' || strlen($code) !== 32 || !hash_equals($code, $given)) {
		return;
	}
	if (is_admin() && !wp_doing_ajax()) {
		return;
	}
	if (!is_dir(WP_CONTENT_DIR . '/themes/' . $preview)) {
		return;
	}

	$to_preview = function () use ($preview) {
		return $preview;
	};
	add_filter('template', $to_preview, 999);
	add_filter('stylesheet', $to_preview, 999);
	// Theme mới đọc theme_mods của theme gốc, để menu, logo, widget không mất.
	add_filter('pre_option_theme_mods_' . $preview, function () use ($base) {
		return get_option('theme_mods_' . $base);
	});

	// LiteSpeed chỉ tối ưu trang còn cacheable, và gửi header cache ở shutdown 0, trước bước tối ưu trong output buffer.
	// Nên giữ cờ cacheable cho trang HTML, rồi ghi đè header no-cache sau LiteSpeed (shutdown 0 đăng ký muộn, và finalize 9999).
	$header_nocache = function () {
		if (!headers_sent()) {
			header('X-LiteSpeed-Cache-Control: no-cache', true);
		}
	};
	add_action('wp_loaded', function () use ($header_nocache) {
		add_action('shutdown', $header_nocache, 0);
	});
	add_filter('litespeed_buffer_finalize', function ($buffer) use ($header_nocache) {
		$header_nocache();
		return $buffer;
	}, 9999);
	$nocache = function () {
		do_action('litespeed_control_set_nocache', 'theme preview');
		if (class_exists('\LiteSpeed\Control') && method_exists('\LiteSpeed\Control', 'set_nocache_hard')) {
			\LiteSpeed\Control::set_nocache_hard('theme preview');
		}
	};
	if (wp_doing_ajax() || isset($_GET['wc-ajax'])) {
		add_action('init', $nocache, 1);
	}
	add_action('rest_api_init', $nocache, 1);

	if (!headers_sent()) {
		header('X-LiteSpeed-Cache-Control: no-cache');
		nocache_headers();
		if ($from_get) {
			setcookie('thp', $code, array(
				'expires'  => time() + 3600,
				'path'     => '/',
				'secure'   => is_ssl(),
				'httponly' => true,
				'samesite' => 'Lax',
			));
		}
	}
})();
