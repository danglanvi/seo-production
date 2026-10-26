<?php
/**
 * Plugin Name: GTM hoãn có hẹn giờ
 * Description: Nạp gtm.js ở thao tác đầu tiên hoặc TG_GTM_DELAY ms sau sự kiện load. Trang chuyển đổi và URL quảng cáo nạp ngay.
 *
 * Mẫu của skill wp-pagespeed (checklist-theo-lop.md lớp 7). Đã chạy trên production site mẫu 2 từ 18/10/2026.
 * Đổi thời điểm nạp tracking là đổi dữ liệu đo lường: chỉ cài khi người duyệt đồng ý.
 *
 * Cài:
 * 1. Gỡ snippet GTM đang có (theme, plugin, Customizer, nội dung trang). Grep mã container để chắc không còn bản thứ hai.
 * 2. Sửa 3 hằng số dưới đây. Chọn TG_GTM_DELAY theo cách ở lớp 7 (max(observedTraceEnd − observedLoad) + 1,5–2 s).
 * 3. Chép vào wp-content/mu-plugins/, kiểm php -l trên server, purge cache.
 * 4. LiteSpeed Cache bật Delay JS: thêm "gtm-delay-loader" vào JS Delayed Excludes (optm-js_defer_exc).
 * 5. Kiểm: scripts/gtm_delay_check.mjs.
 * Rollback: chuyển file này ra khỏi mu-plugins/, trả snippet cũ.
 */
defined( 'ABSPATH' ) || exit;

const TG_GTM_ID      = 'GTM-XXXXXXX';
const TG_GTM_DELAY   = 5000;
const TG_GTM_NOW_URL = '#/(cam-on|thank-you|thanh-toan)[^/]*/?$#'; // trang bắn chuyển đổi khi tải trang: nạp ngay

function tg_gtm_now() {
	$path = (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH );
	return (bool) preg_match( TG_GTM_NOW_URL, $path );
}

add_action( 'wp_head', function () {
	if ( tg_gtm_now() ) {
		?>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','<?php echo TG_GTM_ID; ?>');</script>
<!-- End Google Tag Manager -->
		<?php
		return;
	}
	?>
<!-- Google Tag Manager: gtm-delay-loader -->
<script data-no-optimize="1">(function(w,d,i,t){w.dataLayer=w.dataLayer||[];w.dataLayer.push({'gtm.start':new Date().getTime(),event:'gtm.js'});
var e=['pointerdown','touchstart','keydown','wheel','scroll','mousemove'],o={passive:true},x=0;
function g(){if(x)return;x=1;e.forEach(function(n){w.removeEventListener(n,g,o)});var j=d.createElement('script');j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;d.head.appendChild(j)}
if(/[?&](gclid|gbraid|wbraid|fbclid|ttclid|utm_[a-z]+)=/.test(location.search))return g();
e.forEach(function(n){w.addEventListener(n,g,o)});var s=function(){setTimeout(g,t)};d.readyState==='complete'?s():w.addEventListener('load',s);
})(window,document,'<?php echo TG_GTM_ID; ?>',<?php echo (int) TG_GTM_DELAY; ?>);</script>
<!-- End Google Tag Manager -->
	<?php
}, 1 );

add_action( 'wp_body_open', function () {
	?>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=<?php echo TG_GTM_ID; ?>" height="0" width="0" style="display:none;visibility:hidden" data-no-lazy="1"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
	<?php
} );
