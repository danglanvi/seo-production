<?php
/**
 * Mẫu mu-plugin: chạy site bằng Elementor free khi Elementor Pro tắt. Đổi tiền tố site_ và site- theo site, khớp PREFIX của el_free_convert.php.
 * Khi Pro bật, file này chỉ giữ thanh tiến độ đọc và menu footer; phần còn lại không chạy.
 * - Header, footer: in mẫu Elementor đang gắn điều kiện toàn site (option elementor_pro_theme_builder_conditions), giống Pro.
 * - Shortcode [elementor-template id="…"].
 * - Ô Custom CSS ở tab Nâng cao của widget, container và trang.
 */

// Shortcode thay widget Pro (posts, progress-tracker, nav-menu) và CSS, JS của carousel cuộn ngang. Chạy cả khi Pro bật.
add_shortcode(
	'site_progress',
	function () {
		return '<div class="site-progress" aria-hidden="true"><span></span></div>';
	}
);
add_shortcode(
	'site_menu',
	function ( $atts ) {
		$a = shortcode_atts( array( 'menu' => '', 'label' => 'Menu' ), $atts );
		$m = wp_nav_menu(
			array(
				'menu'        => $a['menu'],
				'container'   => false,
				'menu_class'  => 'site-fmenu__list',
				'echo'        => false,
				'fallback_cb' => '__return_empty_string',
			)
		);
		return $m ? '<details class="site-fmenu"><summary>' . esc_html( $a['label'] ) . '</summary>' . $m . '</details>' : '';
	}
);
// [site_posts count="3" cols="1" thumb="1" date="0" excerpt="20"]: bài mới nhất, markup giống skin classic của widget posts.
add_shortcode(
	'site_posts',
	function ( $atts ) {
		$a = shortcode_atts( array( 'count' => 3, 'cols' => 1, 'thumb' => 1, 'date' => 0, 'excerpt' => 20 ), $atts );
		$q = new WP_Query( array( 'post_type' => 'post', 'posts_per_page' => (int) $a['count'], 'ignore_sticky_posts' => true, 'no_found_rows' => true ) );
		$o = '<div class="elementor-posts-container elementor-posts elementor-posts--skin-classic elementor-grid site-posts" style="--site-cols:' . (int) $a['cols'] . '">';
		while ( $q->have_posts() ) {
			$q->the_post();
			$u  = esc_url( get_permalink() );
			$o .= '<article class="elementor-post elementor-grid-item">';
			if ( (int) $a['thumb'] && has_post_thumbnail() ) {
				$o .= '<a class="elementor-post__thumbnail__link" href="' . $u . '" tabindex="-1"><div class="elementor-post__thumbnail">' . get_the_post_thumbnail( null, 'medium_large', array( 'loading' => 'lazy' ) ) . '</div></a>';
			}
			$o .= '<div class="elementor-post__text"><h3 class="elementor-post__title"><a href="' . $u . '">' . esc_html( get_the_title() ) . '</a></h3>';
			if ( (int) $a['date'] ) {
				$o .= '<div class="elementor-post__meta-data"><span class="elementor-post-date">' . esc_html( get_the_date() ) . '</span></div>';
			}
			if ( (int) $a['excerpt'] ) {
				$o .= '<div class="elementor-post__excerpt"><p>' . esc_html( wp_trim_words( get_the_excerpt(), (int) $a['excerpt'], '…' ) ) . '</p></div>';
			}
			$o .= '</div></article>';
		}
		wp_reset_postdata();
		return $o . '</div>';
	}
);

add_action(
	'wp_footer',
	function () {
		?>
<style id="site-el-free">.site-posts{display:grid;grid-template-columns:repeat(var(--site-cols,1),minmax(0,1fr));gap:30px}.site-posts .elementor-post__thumbnail img{display:block;width:100%;height:auto}.site-posts .elementor-post__title{margin:0 0 8px;font-size:18px;line-height:1.4}.site-posts .elementor-post__title a{color:inherit}.site-posts .elementor-post__meta-data,.site-posts .elementor-post__excerpt p{font-size:14px;margin:0 0 8px}@media(max-width:767px){.site-posts{grid-template-columns:1fr}}.site-carousel{position:relative;padding-bottom:60px}.site-carousel__track{display:flex;gap:var(--gap,20px);overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}.site-carousel__track::-webkit-scrollbar{display:none}.site-carousel__track>*{flex:0 0 calc((100% - (var(--per,1) - 1)*var(--gap,20px))/var(--per,1));scroll-snap-align:start;margin:0}html body .site-carousel .site-carousel__nav{position:absolute;top:auto;bottom:0;transform:none;width:44px;height:44px;padding:0;border-radius:50%;border:1px solid #CBD5E1;background:#fff;color:#0693E3;font-size:24px;line-height:42px;box-shadow:0 2px 8px rgba(3,8,21,.08);cursor:pointer;z-index:2}html body .site-carousel .site-carousel__nav:is(:hover,:focus-visible){background:#0693E3;color:#fff;border-color:#0693E3}.site-carousel__nav--prev{left:calc(50% - 52px)}.site-carousel__nav--next{right:calc(50% - 52px)}.site-media img{width:100%;height:var(--h,400px);object-fit:contain;display:block}.site-testi__item{background:#fff;border-radius:12px;padding:24px;box-shadow:0 4px 18px rgba(20,20,43,.08)}.site-testi__content{margin:0 0 16px;font-style:normal}.site-testi__footer{display:flex;align-items:center;gap:12px}.site-testi__footer img{width:56px;height:56px;border-radius:50%;object-fit:cover}.site-testi__name{display:block;font-weight:700}.site-testi__title{display:block;font-size:14px;opacity:.8}.site-slide{height:var(--h,350px);background-size:contain;background-repeat:no-repeat;background-position:center;display:flex;align-items:flex-end;justify-content:center}.site-slide h3{background:rgba(0,0,0,.5);color:#fff;padding:6px 14px;border-radius:6px;font-size:18px}@media(max-width:767px){.site-carousel__track>*{flex-basis:100%}}.site-progress{height:5px;background:transparent}.site-progress span{display:block;height:100%;width:0;background:#276AE6;transition:width .1s linear}.site-fmenu summary{cursor:pointer;list-style:none;color:#fff;font-weight:600;padding:10px 0;display:flex;align-items:center;gap:8px}.site-fmenu summary::-webkit-details-marker{display:none}.site-fmenu summary:before{content:"\2630";font-size:18px}.site-fmenu__list{list-style:none;margin:0;padding:0}.site-fmenu__list li a{display:block;padding:8px 0;color:#fff;border-bottom:1px solid rgba(255,255,255,.12)}.site-fmenu__list .sub-menu{list-style:none;padding-left:16px}</style>
<script>document.querySelectorAll('.site-carousel').forEach(function(c){var t=c.querySelector('.site-carousel__track');c.querySelectorAll('.site-carousel__nav').forEach(function(b){b.addEventListener('click',function(){t.scrollBy({left:(b.classList.contains('site-carousel__nav--prev')?-1:1)*t.clientWidth,behavior:'smooth'})})})});</script>
<script>(function(){var b=document.querySelectorAll('.site-progress span');if(!b.length)return;var t=0;function u(){t=0;var h=document.documentElement,m=h.scrollHeight-h.clientHeight,p=m>0?Math.min(100,h.scrollTop/m*100):0;for(var i=0;i<b.length;i++)b[i].style.width=p+'%'}addEventListener('scroll',function(){if(!t){t=1;requestAnimationFrame(u)}},{passive:true});u()})();</script>
		<?php
	},
	50
);

if ( defined( 'ELEMENTOR_PRO_VERSION' ) || ! did_action( 'elementor/loaded' ) ) {
	return;
}

/** ID mẫu header/footer cho ngôn ngữ hiện tại, theo điều kiện Pro đã lưu. */
function site_el_location_id( $location ) {
	$c   = get_option( 'elementor_pro_theme_builder_conditions' );
	$ids = array_keys( (array) ( $c[ $location ] ?? array() ) );
	if ( ! $ids || 'publish' !== get_post_status( (int) $ids[0] ) ) {
		return 0;
	}
	return (int) apply_filters( 'wpml_object_id', (int) $ids[0], 'elementor_library', true );
}

function site_el_print_location( $location ) {
	$id = site_el_location_id( $location );
	if ( ! $id ) {
		return;
	}
	$tag = 'footer' === $location ? 'footer' : 'header';
	echo '<' . $tag . ' class="site-el-' . esc_attr( $location ) . ' elementor-location-' . esc_attr( $location ) . '">';
	echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display( $id ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	echo '</' . $tag . '>';
}

// Display Conditions của Pro: bản này chỉ xét điều kiện from_url. Site dùng điều kiện khác thì viết thêm.
// Xét như Pro: nhóm ngoài là OR, nhóm trong là AND, so chuỗi không phân biệt hoa thường. Điều kiện loại khác coi là đạt.
$site_dc_hidden = array();
add_action(
	'elementor/frontend/before_render',
	function ( $el ) use ( &$site_dc_hidden ) {
		$raw = $el->get_settings( 'e_display_conditions' );
		$grp = ! empty( $raw[0] ) ? json_decode( $raw[0], true ) : array();
		if ( ! $grp || \Elementor\Plugin::instance()->editor->is_edit_mode() ) {
			return;
		}
		$ref = strtolower( (string) wp_get_raw_referer() );
		$ok  = false;
		foreach ( (array) $grp as $and ) {
			$all = true;
			foreach ( (array) $and as $c ) {
				if ( 'from_url' !== ( $c['condition'] ?? '' ) ) {
					continue;
				}
				$v   = strtolower( (string) ( $c['from_url'] ?? '' ) );
				$cmp = $c['comparator'] ?? '';
				$all = $all && ( 'is' === $cmp ? $v === $ref : ( 'is_not' === $cmp ? $v !== $ref : ( 'contains' === $cmp ? str_contains( $ref, $v ) : ( 'not_contain' === $cmp && ! str_contains( $ref, $v ) ) ) ) );
			}
			$ok = $ok || $all;
		}
		if ( ! $ok ) {
			add_filter( 'elementor/element/get_child_type', '__return_false' );
			add_filter( 'elementor/frontend/' . $el->get_type() . '/should_render', '__return_false' );
			$site_dc_hidden[] = $el->get_id();
		}
	}
);
add_action(
	'elementor/frontend/after_render',
	function ( $el ) use ( &$site_dc_hidden ) {
		if ( in_array( $el->get_id(), $site_dc_hidden, true ) ) {
			remove_filter( 'elementor/element/get_child_type', '__return_false' );
			remove_filter( 'elementor/frontend/' . $el->get_type() . '/should_render', '__return_false' );
		}
	}
);

// Logo header giờ là widget Image (thay widget logo của Pro): giữ như production là không lazy-load, và chọn bản ảnh nhỏ.
add_filter(
	'wp_get_attachment_image_attributes',
	function ( $attr, $att ) {
		if ( (int) $att->ID === (int) get_theme_mod( 'custom_logo' ) ) {
			$attr['data-no-lazy'] = '1';
			$attr['sizes']        = '(max-width: 767px) 120px, 180px';
		}
		return $attr;
	},
	10,
	2
);

// CSS của header, footer và CSS chung của Elementor nạp trong <head>, kể cả trang không dựng bằng Elementor.
add_action(
	'wp_enqueue_scripts',
	function () {
		$ids = array_filter( array( site_el_location_id( 'header' ), site_el_location_id( 'footer' ) ) );
		if ( ! $ids ) {
			return;
		}
		$fe = \Elementor\Plugin::instance()->frontend;
		$fe->enqueue_styles();
		foreach ( $ids as $id ) {
			( new \Elementor\Core\Files\CSS\Post( $id ) )->enqueue();
		}
	},
	20
);

// Header, footer: thay header.php, footer.php của theme như Pro (theme vẫn chạy file của nó trong bộ đệm rồi bỏ).
add_action(
	'get_header',
	function ( $name ) {
		if ( ! site_el_location_id( 'header' ) ) {
			return;
		}
		?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
		<?php
		wp_body_open();
		site_el_print_location( 'header' );
		$templates = array();
		if ( '' !== (string) $name ) {
			$templates[] = "header-{$name}.php";
		}
		$templates[] = 'header.php';
		remove_all_actions( 'wp_head' );
		ob_start();
		locate_template( $templates, true );
		ob_get_clean();
	}
);
add_action(
	'get_footer',
	function ( $name ) {
		if ( ! site_el_location_id( 'footer' ) ) {
			return;
		}
		site_el_print_location( 'footer' );
		wp_footer();
		echo "\n</body>\n</html>\n";
		$templates = array();
		if ( '' !== (string) $name ) {
			$templates[] = "footer-{$name}.php";
		}
		$templates[] = 'footer.php';
		ob_start();
		locate_template( $templates, true );
		ob_get_clean();
	}
);
add_filter(
	'body_class',
	function ( $c ) {
		$c[] = 'site-el-free';
		return $c;
	}
);
add_action(
	'wp_head',
	function () {
		echo '<style id="site-el-sticky">.site-el-header{position:sticky;top:0;z-index:999}.site-el-header #header.sticky{position:static}</style>' . "\n";
	},
	3
);

// Shortcode [elementor-template id="…"] của Pro.
add_shortcode(
	'elementor-template',
	function ( $atts ) {
		$id = (int) ( $atts['id'] ?? 0 );
		if ( ! $id || 'publish' !== get_post_status( $id ) ) {
			return '';
		}
		$id = (int) apply_filters( 'wpml_object_id', $id, get_post_type( $id ), true );
		$css = is_array( $atts ) && isset( $atts['css'] ) && 'false' !== $atts['css'] && (bool) $atts['css'];
		return \Elementor\Plugin::instance()->frontend->get_builder_content_for_display( $id, $css );
	}
);

// Custom CSS: thay khối quảng cáo "Custom CSS (Pro)" bằng ô nhập thật, in CSS như Pro.
add_action(
	'elementor/element/after_section_end',
	function ( $stack, $section_id ) {
		if ( 'section_custom_css_pro' !== $section_id ) {
			return;
		}
		$cm  = \Elementor\Plugin::instance()->controls_manager;
		$old = $cm->get_control_from_stack( $stack->get_unique_name(), 'section_custom_css_pro' );
		$cm->remove_control_from_stack( $stack->get_unique_name(), array( 'section_custom_css_pro', 'custom_css_pro' ) );
		$stack->start_controls_section( 'section_custom_css', array( 'label' => 'Custom CSS', 'tab' => $old['tab'] ?? \Elementor\Controls_Manager::TAB_ADVANCED ) );
		$stack->add_control(
			'custom_css',
			array(
				'label'       => 'CSS riêng',
				'type'        => \Elementor\Controls_Manager::CODE,
				'description' => 'Dùng "selector" để trỏ tới chính phần tử này.',
				'language'    => 'css',
				'render_type' => 'ui',
			)
		);
		$stack->end_controls_section();
	},
	10,
	2
);
add_action(
	'elementor/element/parse_css',
	function ( $post_css, $element ) {
		if ( $post_css instanceof \Elementor\Core\DynamicTags\Dynamic_CSS ) {
			return;
		}
		$css = trim( (string) ( $element->get_settings()['custom_css'] ?? '' ) );
		if ( '' === $css ) {
			return;
		}
		$post_css->get_stylesheet()->add_raw_css( str_replace( 'selector', $post_css->get_element_unique_selector( $element ), $css ) );
	},
	10,
	2
);
add_action(
	'elementor/css-file/post/parse',
	function ( $post_css ) {
		$doc = \Elementor\Plugin::instance()->documents->get( $post_css->get_post_id() );
		$css = $doc ? trim( (string) ( $doc->get_settings( 'custom_css' ) ?? '' ) ) : '';
		if ( '' !== $css ) {
			$post_css->get_stylesheet()->add_raw_css( str_replace( 'selector', $doc->get_css_wrapper_selector(), $css ) );
		}
	}
);
