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
 *    Bật Guest Mode: danh sách riêng là optm-gm_js_exc (filter litespeed_optm_gm_js_exc). optm-js_defer_exc không áp cho Guest Mode.
 *    Chuỗi "gtm-delay-loader" nằm trong thân script (chú thích đầu script), để mục loại trừ khớp nội dung inline.
 *    Kiểm cấu hình đã xuất: scripts/ls_exclusions_check.py.
 * 5. Kiểm: scripts/gtm_delay_check.mjs.
 * Tái phát link click: khách bấm link (Zalo, tel:, mailto:) ở thao tác đầu tiên, trước khi gtm.js nạp xong. Bộ nghe Link Click của GTM chưa
 * cài nên click đó mất. Loader ghi lại link bị bấm trong lúc chờ, rồi đẩy event gtm.linkClick vào dataLayer khi gtm.js nạp xong (tối đa 5 link).
 * Chỉ replay link còn trong trang. Link mở cùng tab làm trang rời đi trước khi gtm.js nạp, nên không replay được: đo click đó bằng cách khác.
 * Trigger loại "All Elements" dùng gtm.click, loader không replay event này.
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
<script data-no-optimize="1">/*gtm-delay-loader*/(function(w,d,i,t){w.dataLayer=w.dataLayer||[];w.dataLayer.push({'gtm.start':new Date().getTime(),event:'gtm.js'});
var e=['pointerdown','touchstart','keydown','wheel','scroll','mousemove'],o={passive:true},x=0,q=[],r=0;
function k(v){if(r)return;var a=v.target&&v.target.closest&&v.target.closest('a[href],area[href]');if(a&&q.length<5)q.push(a)}
function f(){r=1;d.removeEventListener('click',k,true);var l=q;q=[];l.forEach(function(a){if(!d.contains(a))return;w.dataLayer.push({event:'gtm.linkClick','gtm.element':a,'gtm.elementClasses':typeof a.className==='string'?a.className:'','gtm.elementId':a.id||'','gtm.elementTarget':a.target||'','gtm.elementUrl':a.href||''})})}
function z(){r=1;q=[];d.removeEventListener('click',k,true)}
function g(){if(x)return;x=1;e.forEach(function(n){w.removeEventListener(n,g,o)});var j=d.createElement('script');j.async=true;j.onload=f;j.onerror=z;j.src='https://www.googletagmanager.com/gtm.js?id='+i;d.head.appendChild(j)}
d.addEventListener('click',k,true);
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
