<?php
/**
 * Mẫu mu-plugin media: video YouTube dạng facade và VideoObject. Đổi tiền tố site_ và site- theo site.
 * 1. Video YouTube dạng facade: ảnh poster + nút phát; iframe youtube-nocookie chỉ tạo khi người xem bấm.
 *    - Shortcode [site_video id="" start="" title="" caption=""].
 *    - Tự đổi iframe YouTube trong nội dung bài và widget Video của Elementor. Video riêng tư hoặc không có trong
 *      site-media/videos.json thì giữ nguyên, chờ người duyệt quyết.
 * 2. JSON-LD VideoObject cho video sở hữu có trong bài (wp_head).
 */

defined( 'ABSPATH' ) || exit;

function site_media_videos() {
	static $v = null;
	if ( null === $v ) {
		$f = __DIR__ . '/site-media/videos.json';
		$v = is_readable( $f ) ? (array) json_decode( (string) file_get_contents( $f ), true ) : array();
	}
	return $v;
}

// Video phát được: có trong danh sách, không riêng tư.
function site_media_playable( $id ) {
	$v = site_media_videos();
	return isset( $v[ $id ] ) && in_array( $v[ $id ]['a'] ?? '', array( 'public', 'unlisted', 'available (oEmbed)' ), true );
}

function site_media_start( $query ) {
	if ( preg_match( '/(?:^|[?&;])(?:start|t)=(\d+)/', html_entity_decode( (string) $query ), $m ) ) {
		return (int) $m[1];
	}
	return 0;
}

function site_media_facade( $id, $start = 0, $title = '', $caption = '' ) {
	$v     = site_media_videos();
	$title = trim( wp_strip_all_tags( (string) $title ) );
	if ( '' === $title || 'YouTube video player' === $title ) {
		$title = $v[ $id ]['t'] ?? 'Video YouTube';
	}
	$poster = 'https://i.ytimg.com/vi_webp/' . $id . '/hqdefault.webp';
	$html   = '<figure class="site-video">'
		. '<button type="button" class="site-yt" data-id="' . esc_attr( $id ) . '" data-start="' . (int) $start . '" aria-label="' . esc_attr( 'Phát video: ' . $title ) . '">'
		. '<img src="' . esc_url( $poster ) . '" width="480" height="360" alt="' . esc_attr( $title ) . '" loading="lazy" decoding="async" data-no-lazy="1">'
		. '<span class="site-yt__play" aria-hidden="true"></span>'
		. '</button>'
		. '<noscript><a href="' . esc_url( 'https://www.youtube.com/watch?v=' . $id . ( $start ? '&t=' . (int) $start . 's' : '' ) ) . '">' . esc_html( $title ) . '</a></noscript>';
	if ( '' !== trim( (string) $caption ) ) {
		$html .= '<figcaption>' . wp_kses_post( $caption ) . '</figcaption>';
	}
	return $html . '</figure>';
}

add_shortcode(
	'site_video',
	function ( $atts ) {
		$a = shortcode_atts( array( 'id' => '', 'start' => 0, 'title' => '', 'caption' => '' ), $atts, 'site_video' );
		if ( ! preg_match( '/^[A-Za-z0-9_-]{11}$/', $a['id'] ) ) {
			return '';
		}
		return site_media_facade( $a['id'], (int) $a['start'], $a['title'], $a['caption'] );
	}
);

// Đổi iframe YouTube trong HTML sang facade. Iframe đứng một mình trong <p> thì thay cả thẻ <p> để không lồng <figure> trong <p>.
function site_media_convert( $html ) {
	if ( is_admin() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || false === stripos( (string) $html, 'youtube' ) ) {
		return $html;
	}
	$re = '#(<p\b[^>]*>\s*)?<iframe\b([^>]*?)\bsrc="(?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})([^"]*)"([^>]*)>\s*</iframe>(\s*</p>)?#i';
	return preg_replace_callback(
		$re,
		function ( $m ) {
			$id = $m[3];
			if ( ! site_media_playable( $id ) ) {
				return $m[0];
			}
			$title = preg_match( '/\btitle="([^"]*)"/i', $m[2] . ' ' . $m[5], $t ) ? html_entity_decode( $t[1] ) : '';
			$fig   = site_media_facade( $id, site_media_start( $m[4] ), $title );
			if ( '' !== $m[1] && ! empty( $m[6] ) ) {
				return $fig;
			}
			return $m[1] . $fig . ( $m[6] ?? '' );
		},
		$html
	);
}
add_filter( 'the_content', 'site_media_convert', 99 );
add_filter( 'elementor/frontend/the_content', 'site_media_convert', 99 );
add_filter(
	'elementor/widget/render_content',
	function ( $content, $widget ) {
		$name = $widget->get_name();
		if ( 'video' === $name ) {
			$s = $widget->get_settings_for_display();
			if ( 'youtube' === ( $s['video_type'] ?? '' ) && preg_match( '#(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})#', (string) ( $s['youtube_url'] ?? '' ), $m ) && site_media_playable( $m[1] ) ) {
				return site_media_facade( $m[1], (int) ( $s['start'] ?? 0 ) );
			}
			return $content;
		}
		return in_array( $name, array( 'text-editor', 'html', 'shortcode' ), true ) ? site_media_convert( $content ) : $content;
	},
	10,
	2
);

// CSS in ở <head>, JS ở cuối trang, khi bài có video nhúng. Không dựa vào cờ lúc render vì Elementor cache output widget.
// Script có data-no-optimize để LiteSpeed không hoãn tới lần chạm đầu (lần bấm phát chính là lần chạm đầu).
function site_media_page_has_video() {
	static $has = null;
	if ( null === $has ) {
		$post = is_singular() ? get_post() : null;
		$has  = $post && array_filter( site_media_ids_for_post( $post ), 'site_media_playable' );
	}
	return (bool) $has;
}
add_action(
	'wp_head',
	function () {
		if ( site_media_page_has_video() ) {
			?>
<style id="site-media-css">
.site-video{margin:24px 0;max-width:100%}
html body .site-video .site-yt,html body .site-video iframe{position:relative;display:block;width:100%;height:auto;min-height:0;aspect-ratio:16/9;border:0;margin:0;padding:0;border-radius:12px;overflow:hidden;background:#030815;box-shadow:none;cursor:pointer}
html body .site-video .site-yt:is(:hover,:focus){background:#030815}
.site-video .site-yt img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;margin:0;transition:transform .3s ease}
.site-video .site-yt:hover img{transform:scale(1.03)}
.site-yt__play{position:absolute;left:50%;top:50%;width:76px;height:54px;transform:translate(-50%,-50%);border-radius:14px;background:linear-gradient(135deg,#0693E3,#9900EF);box-shadow:0 8px 24px rgba(3,8,21,.35);transition:transform .2s ease}
.site-yt__play::before{content:"";position:absolute;left:31px;top:16px;border-style:solid;border-width:11px 0 11px 19px;border-color:transparent transparent transparent #fff}
.site-video .site-yt:hover .site-yt__play{transform:translate(-50%,-50%) scale(1.08)}
html body .site-video .site-yt:focus-visible{outline:3px solid #0693E3;outline-offset:3px}
.site-video figcaption{margin-top:8px;font-size:14px;line-height:1.5;color:#475569}
.wp-block-embed__wrapper:has(.site-video)::before{display:none}
</style>
			<?php
		}
	},
	30
);
add_action(
	'wp_footer',
	function () {
		if ( site_media_page_has_video() ) {
			?>
<script id="site-media-js" data-no-optimize="1" data-no-defer="1">
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.site-yt');if(!b)return;e.preventDefault();var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0'+(+b.dataset.start?'&start='+b.dataset.start:'');f.title=b.getAttribute('aria-label').replace(/^Phát video: /,'');f.allow='accelerometer; autoplay; encrypted-media; picture-in-picture';f.allowFullscreen=true;b.replaceWith(f);f.focus()});
</script>
			<?php
		}
	},
	5
);

// VideoObject: lấy ID video từ nội dung bài, dữ liệu Elementor và shortcode; lưu cache theo ngày sửa bài.
function site_media_ids_for_post( $post ) {
	$key = 'site_media_ids_' . $post->ID . '_' . strtotime( $post->post_modified_gmt );
	$ids = get_transient( $key );
	if ( false === $ids ) {
		$content = (string) $post->post_content;
		$el      = str_replace( '\\/', '/', (string) get_post_meta( $post->ID, '_elementor_data', true ) );
		$re      = array(
			'#youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})#',                                   // iframe
			'#\[site_video[^\]]*\bid=["\']?([A-Za-z0-9_-]{11})#',                                       // shortcode
			'#^\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})\S*\s*$#m', // dòng URL trơn (oEmbed)
			'#wp:embed \{"url":"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})#', // khối embed
			'#"youtube_url":"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})#',    // widget Video Elementor
		);
		$found = array();
		foreach ( $re as $r ) {
			preg_match_all( $r, $content . "\n" . $el, $m );
			$found = array_merge( $found, $m[1] );
		}
		$ids = array_values( array_unique( $found ) );
		set_transient( $key, $ids, WEEK_IN_SECONDS );
	}
	return $ids;
}

// VideoObject cho video sở hữu có trong bài. In JSON-LD riêng; site có plugin schema dạng @graph thì chuyển mảng này vào graph đó.
// videos.json: {"<id>": {"t": tiêu đề, "d": mô tả, "u": ngày đăng ISO, "s": số giây, "a": public|unlisted, "author": "<@id Person hoặc Organization>", "third": true nếu video của kênh khác}}
add_action(
	'wp_head',
	function () {
		$post = is_singular() ? get_post() : null;
		if ( ! $post ) {
			return;
		}
		$v     = site_media_videos();
		$url   = get_permalink( $post );
		$graph = array();
		foreach ( site_media_ids_for_post( $post ) as $id ) {
			$x = $v[ $id ] ?? null;
			if ( ! $x || ! empty( $x['third'] ) || ! in_array( $x['a'] ?? '', array( 'public', 'unlisted' ), true ) || empty( $x['u'] ) || empty( $x['s'] ) ) {
				continue;
			}
			$s    = (int) $x['s'];
			$node = array(
				'@type'        => 'VideoObject',
				'@id'          => $url . '#video-' . $id,
				'name'         => $x['t'],
				'description'  => $x['d'] ?: $x['t'],
				'thumbnailUrl' => array( 'https://i.ytimg.com/vi/' . $id . '/maxresdefault.jpg', 'https://i.ytimg.com/vi/' . $id . '/hqdefault.jpg' ),
				'uploadDate'   => $x['u'],
				'duration'     => 'PT' . ( $s >= 3600 ? intdiv( $s, 3600 ) . 'H' : '' ) . ( $s % 3600 >= 60 ? intdiv( $s % 3600, 60 ) . 'M' : '' ) . ( $s % 60 ) . 'S',
				'embedUrl'     => 'https://www.youtube-nocookie.com/embed/' . $id,
				'url'          => 'https://www.youtube.com/watch?v=' . $id,
			);
			if ( ! empty( $x['author'] ) ) {
				$node['author'] = array( '@id' => $x['author'] );
			}
			$graph[] = $node;
		}
		if ( $graph ) {
			echo '<script type="application/ld+json">' . wp_json_encode( array( '@context' => 'https://schema.org', '@graph' => $graph ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . "</script>\n";
		}
	},
	30
);
