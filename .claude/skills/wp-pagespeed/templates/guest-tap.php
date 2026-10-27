<?php
/**
 * Plugin Name: Guest tap replay (wp-pagespeed)
 * Description: Trang LiteSpeed Guest Mode hoãn JS tới lần tương tác đầu, nên lần chạm đầu vào nút menu bị mất. Script nhớ cú chạm đó và bấm lại sau khi LiteSpeed nạp xong JS hoãn. Gỡ: chuyển file ra khỏi mu-plugins rồi purge các URL đã chạm.
 */
defined( 'ABSPATH' ) || exit;

// Selector nút mở menu của theme. Site mẫu 26/10/2026 (Max Mega Menu): 'button.mega-toggle-animated,.mega-indicator'.
const WPS_GUEST_TAP_SEL = 'button.mega-toggle-animated,.mega-indicator';

add_action( 'wp_footer', function () {
	if ( ! defined( 'LITESPEED_GUEST' ) || ! LITESPEED_GUEST ) {
		return;
	}
	?>
<script id="wps-guest-tap" data-no-optimize="1" data-no-defer="1">
(function(){var q=null,s=<?php echo wp_json_encode( WPS_GUEST_TAP_SEL ); ?>;
document.addEventListener('click',function(e){if(!document.querySelector('script[type="litespeed/javascript"]'))return;var b=e.target.closest&&e.target.closest(s);if(b)q=b;},true);
document.addEventListener('DOMContentLiteSpeedLoaded',function(){if(!q)return;var b=q;q=null;setTimeout(function(){b.click();},150);});
})();
</script>
	<?php
}, 99 );
