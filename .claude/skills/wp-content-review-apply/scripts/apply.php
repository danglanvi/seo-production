<?php
/**
 * Ghi plan.json (do plan.py sinh hoặc agent dựng) lên WordPress. Mặc định chạy thử; DRY=0 mới ghi.
 * Chạy: PLAN=/tmp/plan.json DRY=1 [PURGE=0] [OUT=/tmp/log-dry.json] [SRC=/tmp/src.json] [FAIL_ON_SKIP=1] wp eval-file apply.php
 * OUT: ghi log JSON vào file (không ghi đè file có sẵn). Không có OUT thì in JSON ra stdout.
 * FAIL_ON_SKIP=1: thoát mã 2 khi còn dòng skip. Lỗi đầu vào (thiếu PLAN, JSON sai, OUT đã có) thoát mã 1.
 * Log: before (giá trị trước khi ghi, dùng để rollback), md5_after (md5 giá trị vừa ghi), ok, skip (kèm lý do), notes, redirect_ids.
 *
 * Thao tác (mỗi thao tác có item, post):
 *   meta:<key>, post_title, post_name (+ redirect 301), acf:<field>, elementor:<widget>:<đường.dẫn>, content (md5_before), redirect:
 *     dạng cũ, so giá trị hiện tại với `before`, ghi `value`.
 *   text: thay một câu trong một trường. {field, old, new, ctx_trai?, ctx_phai?, nth?, multi?, count?}
 *   fix:  sửa đích danh cả trường. {field, old, new}. old = null nghĩa là khoá chưa có.
 *   field: post_content | post_title | post_excerpt | meta:<k> | elementor:<widget>:<đường.dẫn> | usermeta:<uid>:<k> | option:<tên>[:<đường.dẫn>]
 *   el_rm: gỡ phần tử Elementor theo id. {post, id, widget_type?}
 *   el_restore: chèn lại phần tử. {post, id, parent, index?, widget | src_key} (src_key tra trong file SRC)
 * text khớp sau khi chuẩn hoá NFC, đổi NBSP thành dấu cách và gộp khoảng trắng. Phải khớp đúng 1 vị trí.
 * Khớp nhiều vị trí thì dùng ctx_trai, ctx_phai, nth (từ 1) hoặc multi. Thao tác đã áp rồi thì báo "đã đúng", không áp lần hai.
 * Đường dẫn Elementor và option phải có đủ khoá cha. Đường dẫn sai thì skip, không tạo khoá rác, không đánh dấu ghi.
 * Chạy được bằng `wp eval-file` (mọi hàm tự chứa, không dùng biến toàn cục của file).
 */
if ( ! defined( 'ABSPATH' ) && isset( $argv ) && in_array( '--help', $argv, true ) ) {
	echo "apply.php: xem chú thích đầu file. Chạy qua wp eval-file với biến môi trường PLAN, DRY, OUT, SRC, PURGE, FAIL_ON_SKIP.\n";
	exit( 0 );
}

global $wpdb;

// ---- Hàm tự chứa ----
function wps_nfc( $s ) {
	return ( is_string( $s ) && class_exists( 'Normalizer' ) && ! Normalizer::isNormalized( $s, Normalizer::FORM_C ) ) ? Normalizer::normalize( $s, Normalizer::FORM_C ) : $s;
}

// Chuẩn hoá để so cả chuỗi: NFC, NBSP thành dấu cách, gộp khoảng trắng, bỏ đầu cuối.
function wps_cmp( $s ) {
	$s = wps_nfc( (string) $s );
	return trim( preg_replace( '/[\s\x{00A0}\x{202F}]+/u', ' ', $s ) );
}

const WPS_WS = '[\s\x{00A0}\x{202F}]';

// Dựng mẫu regex từ chuỗi: khoảng trắng bất kỳ khớp mọi chuỗi khoảng trắng (kể cả NBSP).
function wps_pattern( $s ) {
	$s = wps_nfc( (string) $s );
	if ( '' === $s ) {
		return '';
	}
	$parts = preg_split( '/[\s\x{00A0}\x{202F}]+/u', $s );
	$parts = array_map(
		function ( $p ) {
			return preg_quote( $p, '~' );
		},
		$parts
	);
	// Đầu hoặc cuối chuỗi là khoảng trắng thì $parts có phần tử rỗng ở đó: implode vẫn giữ dấu cách đúng chỗ.
	return implode( WPS_WS . '+', $parts );
}

// Trả danh sách [byte_start, byte_len] của phần `old` trong $c, có tính ctx_trai, ctx_phai.
function wps_find( $c, $old, $ctx_l, $ctx_r ) {
	$po = wps_pattern( $old );
	if ( '' === $po ) {
		return array();
	}
	$pl  = wps_pattern( $ctx_l );
	$pr  = wps_pattern( $ctx_r );
	$re  = '~(?<l>' . $pl . ')' . ( '' !== $pl ? WPS_WS . '*' : '' ) . '(?<o>' . $po . ')' . ( '' !== $pr ? WPS_WS . '*' : '' ) . '(?<r>' . $pr . ')~u';
	$n   = @preg_match_all( $re, $c, $m, PREG_OFFSET_CAPTURE );
	$out = array();
	if ( $n ) {
		foreach ( $m['o'] as $hit ) {
			$out[] = array( $hit[1], strlen( $hit[0] ) );
		}
	}
	return $out;
}

// Chữ `new` đã nằm đúng vị trí $start của $c chưa (chống áp lần hai khi new chứa old).
function wps_starts_with_new( $c, $start, $new ) {
	$pn = wps_pattern( $new );
	return '' !== $pn && 1 === @preg_match( '~\G' . $pn . '~u', $c, $m, 0, $start );
}

// Đổi một giá trị. Trả array( st => ok|dung|skip, new, why, nfc ).
function wps_change( $t, $cur, $x ) {
	if ( 'fix' === $t ) {
		$old = array_key_exists( 'old', $x ) ? $x['old'] : false;
		if ( false === $old && ! array_key_exists( 'old', $x ) ) {
			return array( 'st' => 'skip', 'why' => 'thiếu old' );
		}
		$same = function ( $a, $b ) {
			return ( is_string( $a ) && is_string( $b ) ) ? wps_cmp( $a ) === wps_cmp( $b ) : wp_json_encode( $a ) === wp_json_encode( $b );
		};
		if ( $same( $cur, $x['new'] ) ) {
			return array( 'st' => 'dung' );
		}
		if ( null === $old ) {
			if ( null !== $cur && '' !== $cur ) {
				return array( 'st' => 'skip', 'why' => 'khoá đã có giá trị, bản lúc soạn ghi chưa có: ' . mb_substr( is_string( $cur ) ? $cur : wp_json_encode( $cur ), 0, 120 ) );
			}
		} elseif ( ! $same( $cur, $old ) ) {
			return array( 'st' => 'skip', 'why' => 'giá trị hiện tại khác bản lúc soạn: ' . mb_substr( is_string( $cur ) ? $cur : wp_json_encode( $cur ), 0, 120 ) );
		}
		return array( 'st' => 'ok', 'new' => $x['new'] );
	}
	// text
	if ( ! is_string( $cur ) ) {
		return array( 'st' => 'skip', 'why' => 'giá trị hiện tại không phải chuỗi' );
	}
	if ( ! isset( $x['old'], $x['new'] ) || '' === (string) $x['old'] ) {
		return array( 'st' => 'skip', 'why' => 'thiếu old hoặc new' );
	}
	$c     = wps_nfc( $cur );
	$new   = wps_nfc( (string) $x['new'] );
	$ctx_l = (string) ( $x['ctx_trai'] ?? '' );
	$ctx_r = (string) ( $x['ctx_phai'] ?? '' );
	$all   = wps_find( $c, $x['old'], $ctx_l, $ctx_r );
	$live  = array();
	foreach ( $all as $h ) {
		if ( ! wps_starts_with_new( $c, $h[0], $new ) ) {
			$live[] = $h;
		}
	}
	if ( ! $live ) {
		if ( $all || wps_find( $c, $new, $ctx_l, $ctx_r ) ) {
			return array( 'st' => 'dung' );
		}
		return array( 'st' => 'skip', 'why' => 'không thấy chữ cũ: ' . mb_substr( (string) $x['old'], 0, 80 ) );
	}
	$n = count( $live );
	if ( ! empty( $x['multi'] ) ) {
		if ( isset( $x['count'] ) && (int) $x['count'] !== $n ) {
			return array( 'st' => 'skip', 'why' => "khớp $n vị trí, cần {$x['count']}" );
		}
		$pick = $live;
	} elseif ( isset( $x['nth'] ) ) {
		$k = (int) $x['nth'];
		if ( $k < 1 || $k > count( $all ) ) {
			return array( 'st' => 'skip', 'why' => "nth=$k nhưng chỉ có " . count( $all ) . ' vị trí' );
		}
		if ( wps_starts_with_new( $c, $all[ $k - 1 ][0], $new ) ) {
			return array( 'st' => 'dung' );
		}
		$pick = array( $all[ $k - 1 ] );
	} elseif ( 1 !== $n ) {
		return array( 'st' => 'skip', 'why' => "khớp $n vị trí, cần 1: thêm ctx_trai, ctx_phai, nth hoặc multi" );
	} else {
		$pick = $live;
	}
	for ( $i = count( $pick ) - 1; $i >= 0; $i-- ) {
		$c = substr( $c, 0, $pick[ $i ][0] ) . $new . substr( $c, $pick[ $i ][0] + $pick[ $i ][1] );
	}
	return array( 'st' => 'ok', 'new' => $c, 'nfc' => $c !== $cur && wps_nfc( $cur ) !== $cur );
}

// Tách chuỗi `field` của thao tác text, fix. Trả null khi sai dạng.
function wps_parse_field( $f ) {
	$f = (string) $f;
	if ( in_array( $f, array( 'post_content', 'post_title', 'post_excerpt' ), true ) ) {
		return array( 'kind' => 'post', 'col' => $f );
	}
	$p = explode( ':', $f, 3 );
	if ( 'meta' === $p[0] && ! empty( $p[1] ) ) {
		return array( 'kind' => 'meta', 'key' => isset( $p[2] ) ? $p[1] . ':' . $p[2] : $p[1] );
	}
	if ( 'elementor' === $p[0] && ! empty( $p[1] ) && ! empty( $p[2] ) ) {
		return array( 'kind' => 'elementor', 'wid' => $p[1], 'path' => $p[2] );
	}
	if ( 'usermeta' === $p[0] && ! empty( $p[1] ) && ! empty( $p[2] ) ) {
		return array( 'kind' => 'usermeta', 'uid' => (int) $p[1], 'key' => $p[2] );
	}
	if ( 'option' === $p[0] && ! empty( $p[1] ) ) {
		return array( 'kind' => 'option', 'name' => $p[1], 'path' => $p[2] ?? '' );
	}
	return null;
}

// Mọi khoá cha phải có sẵn. Khoá cuối được thiếu khi $leaf_may_miss.
function wps_has( $arr, $keys, $leaf_may_miss ) {
	$last = array_pop( $keys );
	foreach ( $keys as $k ) {
		if ( ! is_array( $arr ) || ! array_key_exists( $k, $arr ) ) {
			return false;
		}
		$arr = $arr[ $k ];
	}
	return is_array( $arr ) && ( $leaf_may_miss || array_key_exists( $last, $arr ) );
}

function &wps_find_widget( array &$els, $id ) {
	$none = null;
	foreach ( $els as &$e ) {
		if ( ( $e['id'] ?? '' ) === $id ) {
			return $e;
		}
		if ( ! empty( $e['elements'] ) ) {
			$r = &wps_find_widget( $e['elements'], $id );
			if ( null !== $r ) {
				return $r;
			}
		}
	}
	return $none;
}

function wps_count_el( array $els, $id ) {
	$n = 0;
	foreach ( $els as $e ) {
		if ( ( $e['id'] ?? '' ) === $id ) {
			$n++;
		}
		if ( ! empty( $e['elements'] ) ) {
			$n += wps_count_el( $e['elements'], $id );
		}
	}
	return $n;
}

// Gỡ phần tử theo id, chỉ gọi sau khi wps_count_el báo đúng 1.
function wps_rm_el( array &$els, $id ) {
	foreach ( $els as $i => &$e ) {
		if ( ( $e['id'] ?? '' ) === $id ) {
			unset( $els[ $i ] );
			$els = array_values( $els );
			return true;
		}
		if ( ! empty( $e['elements'] ) && wps_rm_el( $e['elements'], $id ) ) {
			return true;
		}
	}
	return false;
}

function wps_has_rm_redirects() {
	global $wpdb;
	$tbl = $wpdb->prefix . 'rank_math_redirections';
	return $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $tbl ) ) === $tbl;
}

function wps_add_redirect( $src, $to, $code, $dry, &$log ) {
	global $wpdb;
	$tbl = $wpdb->prefix . 'rank_math_redirections';
	if ( ! wps_has_rm_redirects() ) {
		return 'site không có bảng redirect của Rank Math, ghi redirect bằng plugin redirect của site';
	}
	$src = trim( $src, '/' );
	$has = $wpdb->get_var( $wpdb->prepare( "SELECT id FROM $tbl WHERE status='active' AND sources LIKE %s", '%"pattern";s:' . strlen( $src . '/' ) . ':"' . $wpdb->esc_like( $src . '/' ) . '"%' ) );
	if ( $has ) {
		return "đã có redirect #$has";
	}
	if ( ! $dry ) {
		$now = current_time( 'mysql' );
		$wpdb->insert(
			$tbl,
			array(
				'sources'     => serialize(
					array(
						array( 'ignore' => '', 'pattern' => $src . '/', 'comparison' => 'exact' ),
						array( 'ignore' => '', 'pattern' => $src, 'comparison' => 'exact' ),
					)
				),
				'url_to'      => $to,
				'header_code' => (string) $code,
				'hits'        => 0,
				'status'      => 'active',
				'created'     => $now,
				'updated'     => $now,
			)
		);
		$log['redirect_ids'][ $src ] = $wpdb->insert_id;
		delete_option( 'rank_math_redirections_cache' );
	}
	return true;
}

// ---- Đầu vào ----
$plan_file = getenv( 'PLAN' );
if ( ! $plan_file || ! is_readable( $plan_file ) ) {
	fwrite( STDERR, "Thiếu PLAN hoặc không đọc được file plan\n" );
	exit( 1 );
}
$plan = json_decode( (string) file_get_contents( $plan_file ), true );
if ( ! is_array( $plan ) || ! isset( $plan['ops'] ) || ! is_array( $plan['ops'] ) ) {
	fwrite( STDERR, "PLAN không phải JSON có khoá ops\n" );
	exit( 1 );
}
$out_file = getenv( 'OUT' );
if ( $out_file && file_exists( $out_file ) ) {
	fwrite( STDERR, "OUT đã có, không ghi đè: $out_file\n" );
	exit( 1 );
}
$src_file = getenv( 'SRC' );
$src      = $src_file && is_readable( $src_file ) ? json_decode( (string) file_get_contents( $src_file ), true ) : array();
$dry      = getenv( 'DRY' ) !== '0';
kses_remove_filters();
$log  = array( 'dry' => $dry, 'before' => array(), 'md5_after' => array(), 'ok' => array(), 'skip' => array(), 'notes' => array(), 'redirect_ids' => array() );
$norm = function ( $s ) {
	$s = html_entity_decode( preg_replace( '/<[^>]+>/', ' ', (string) $s ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
	if ( class_exists( 'Normalizer' ) ) {
		$s = Normalizer::normalize( str_replace( "\xc2\xa0", ' ', $s ), Normalizer::FORM_C );
	}
	return trim( preg_replace( '/\s+/u', ' ', $s ) );
};
$skip = function ( $what, $why ) use ( &$log ) {
	$log['skip'][] = array( $what, $why );
};
$ok   = function ( $what ) use ( &$log ) {
	$log['ok'][] = $what;
};

$el_cache = array();
$el_dirty = array();
$buf      = array(); // Bộ đệm giá trị cho text, fix: nhiều thao tác cùng trường nối tiếp nhau, ghi một lần ở cuối.
$el_load  = function ( $post ) use ( &$el_cache, &$log ) {
	if ( ! isset( $el_cache[ $post ] ) ) {
		$raw = get_post_meta( $post, '_elementor_data', true );
		$log['before']['elementor'][ $post ] = $raw;
		$el_cache[ $post ] = is_string( $raw ) ? json_decode( $raw, true ) : null;
	}
	return is_array( $el_cache[ $post ] );
};

foreach ( $plan['ops'] as $x ) {
	$t     = (string) ( $x['target'] ?? '' );
	$post  = (int) ( $x['post'] ?? 0 );
	$item  = (string) ( $x['item'] ?? '' );
	$what  = trim( "$item $post $t" ) . ( isset( $x['field'] ) ? ':' . $x['field'] : '' );
	$loc   = null;
	$needs = 'redirect' !== $t;
	if ( 'text' === $t || 'fix' === $t ) {
		$loc = wps_parse_field( $x['field'] ?? '' );
		if ( ! $loc ) {
			$skip( $what, 'field sai dạng' );
			continue;
		}
		$needs = ! in_array( $loc['kind'], array( 'usermeta', 'option' ), true );
	}
	$p = $needs ? get_post( $post ) : null;
	if ( $needs && ! $p ) {
		$skip( $what, 'không có post' );
		continue;
	}

	// ---- text, fix ----
	if ( $loc ) {
		$keys = array();
		if ( 'elementor' === $loc['kind'] ) {
			if ( ! $el_load( $post ) ) {
				$skip( $what, 'không có _elementor_data hợp lệ' );
				continue;
			}
			$w = &wps_find_widget( $el_cache[ $post ], $loc['wid'] );
			if ( null === $w ) {
				$skip( $what, 'không thấy widget' );
				unset( $w );
				continue;
			}
			$keys = explode( '.', $loc['path'] );
			$miss = 'fix' === $t && array_key_exists( 'old', $x ) && null === $x['old'];
			if ( ! wps_has( $w['settings'] ?? array(), $keys, $miss ) ) {
				$skip( $what, 'không thấy đường dẫn' );
				unset( $w );
				continue;
			}
			$slot = &$w['settings'];
		} else {
			$sk = $loc['kind'] . '|' . ( $loc['col'] ?? $loc['key'] ?? $loc['name'] ) . '|' . ( 'usermeta' === $loc['kind'] ? $loc['uid'] : $post );
			if ( ! isset( $buf[ $sk ] ) ) {
				if ( 'post' === $loc['kind'] ) {
					$v = $p->{$loc['col']};
				} elseif ( 'meta' === $loc['kind'] ) {
					$v = get_post_meta( $post, $loc['key'], true );
				} elseif ( 'usermeta' === $loc['kind'] ) {
					$v = get_user_meta( $loc['uid'], $loc['key'], true );
				} else {
					$v = get_option( $loc['name'] );
				}
				$buf[ $sk ] = array( 'loc' => $loc, 'post' => $post, 'orig' => $v, 'cur' => $v );
			}
			if ( 'option' === $loc['kind'] && '' !== $loc['path'] ) {
				$keys = explode( '.', $loc['path'] );
				$miss = 'fix' === $t && array_key_exists( 'old', $x ) && null === $x['old'];
				if ( ! wps_has( $buf[ $sk ]['cur'], $keys, $miss ) ) {
					$skip( $what, 'không thấy đường dẫn' );
					continue;
				}
			}
			$slot = &$buf[ $sk ]['cur'];
		}
		foreach ( $keys as $k ) {
			$slot = &$slot[ $k ];
		}
		$res = wps_change( $t, $slot, $x );
		if ( 'ok' === $res['st'] ) {
			$slot = $res['new'];
			if ( 'elementor' === $loc['kind'] ) {
				$el_dirty[ $post ] = true;
			}
			if ( ! empty( $res['nfc'] ) ) {
				$log['notes'][] = "$what: chuẩn hoá NFC cả trường khi ghi";
			}
			$ok( $what );
		} elseif ( 'dung' === $res['st'] ) {
			$ok( "$what (đã đúng)" );
		} else {
			$skip( $what, $res['why'] );
		}
		unset( $slot, $w );
		continue;
	}

	// ---- el_rm, el_restore ----
	if ( 'el_rm' === $t || 'el_restore' === $t ) {
		if ( ! $el_load( $post ) ) {
			$skip( $what, 'không có _elementor_data hợp lệ' );
			continue;
		}
		$id = (string) ( $x['id'] ?? '' );
		if ( '' === $id ) {
			$skip( $what, 'thiếu id' );
			continue;
		}
		$n = wps_count_el( $el_cache[ $post ], $id );
		if ( 'el_rm' === $t ) {
			if ( 1 !== $n ) {
				$skip( $what, "gỡ $n phần tử, cần 1: $id" );
				continue;
			}
			if ( ! empty( $x['widget_type'] ) ) {
				$e = &wps_find_widget( $el_cache[ $post ], $id );
				$wt = $e['widgetType'] ?? ( $e['elType'] ?? '' );
				unset( $e );
				if ( $wt !== $x['widget_type'] ) {
					$skip( $what, "phần tử $id là $wt, cần {$x['widget_type']}" );
					continue;
				}
			}
			wps_rm_el( $el_cache[ $post ], $id );
		} else {
			if ( $n > 0 ) {
				$ok( "$what (đã đúng)" );
				continue;
			}
			$wd = $x['widget'] ?? ( isset( $x['src_key'] ) ? ( $src[ $x['src_key'] ]['widget'] ?? null ) : null );
			if ( ! is_array( $wd ) || ( $wd['id'] ?? '' ) !== $id ) {
				$skip( $what, 'thiếu widget gốc hoặc id widget khác id thao tác' );
				continue;
			}
			$parent = (string) ( $x['parent'] ?? '' );
			if ( '' === $parent ) {
				$list = &$el_cache[ $post ];
			} else {
				$pe = &wps_find_widget( $el_cache[ $post ], $parent );
				if ( null === $pe ) {
					$skip( $what, "không thấy container $parent" );
					unset( $pe );
					continue;
				}
				if ( ! isset( $pe['elements'] ) ) {
					$pe['elements'] = array();
				}
				$list = &$pe['elements'];
			}
			$idx = isset( $x['index'] ) ? (int) $x['index'] : count( $list );
			if ( $idx < 0 || $idx > count( $list ) ) {
				$skip( $what, "index $idx ngoài khoảng 0 đến " . count( $list ) );
				unset( $list, $pe );
				continue;
			}
			array_splice( $list, $idx, 0, array( $wd ) );
			unset( $list, $pe );
		}
		$el_dirty[ $post ] = true;
		$ok( $what );
		continue;
	}

	// ---- Dạng cũ: so `before`, ghi `value` ----
	if ( 'content' === $t ) {
		$log['before']['content_md5'][ $post ] = md5( $p->post_content );
		if ( md5( $p->post_content ) !== $x['md5_before'] ) {
			$skip( $what, 'bài đã đổi sau lúc tính' );
			continue;
		}
		if ( ! $dry ) {
			$wpdb->update( $wpdb->posts, array( 'post_content' => $x['value'] ), array( 'ID' => $post ) );
			clean_post_cache( $post );
			$log['md5_after']['post_content'][ $post ] = md5( $x['value'] );
		}
		$ok( $what );
		continue;
	}
	if ( 'redirect' === $t ) {
		$r = wps_add_redirect( $x['src'], $x['to'], $x['code'], $dry, $log );
		true === $r ? $ok( $what ) : $skip( $what, $r );
		continue;
	}
	// Đọc giá trị hiện tại theo loại.
	$kind = explode( ':', $t, 3 );
	if ( 'meta' === $kind[0] ) {
		$cur = get_post_meta( $post, $kind[1], true );
	} elseif ( 'post_title' === $t || 'post_name' === $t ) {
		$cur = $p->$t;
	} elseif ( 'acf' === $kind[0] && function_exists( 'get_field' ) ) {
		$cur = get_field( $kind[1], $post, false );
	} elseif ( 'elementor' === $kind[0] ) {
		if ( empty( $kind[2] ) ) {
			$skip( $what, 'thiếu đường dẫn' );
			continue;
		}
		if ( ! $el_load( $post ) ) {
			$skip( $what, 'không có _elementor_data hợp lệ' );
			continue;
		}
		$w = &wps_find_widget( $el_cache[ $post ], $kind[1] );
		if ( null === $w ) {
			$skip( $what, 'không thấy widget' );
			unset( $w );
			continue;
		}
		// Kiểm mọi khoá cha trước khi lấy tham chiếu: lấy tham chiếu tới khoá thiếu sẽ tạo khoá null trong dữ liệu ghi.
		$keys = explode( '.', $kind[2] );
		if ( ! wps_has( $w['settings'] ?? array(), $keys, '' === $norm( $x['before'] ?? '' ) ) ) {
			$skip( $what, 'không thấy đường dẫn' );
			unset( $w );
			continue;
		}
		$slot = &$w['settings'];
		foreach ( $keys as $k ) {
			$slot = &$slot[ $k ];
		}
		$cur = $slot ?? '';
	} else {
		$skip( $what, 'loại thao tác chưa hỗ trợ' );
		continue;
	}
	$log['before']['values'][ $post ][ $t ] = $cur;
	if ( $norm( $cur ) === $norm( $x['value'] ) ) {
		$ok( "$what (đã đúng)" );
		unset( $w, $slot );
		continue;
	}
	if ( $norm( $cur ) !== $norm( $x['before'] ) ) {
		$skip( $what, 'giá trị hiện tại khác bản lúc soạn: ' . mb_substr( $norm( $cur ), 0, 120 ) );
		unset( $w, $slot );
		continue;
	}
	if ( 'post_name' === $t && ! empty( $x['redirect'] ) && ! wps_has_rm_redirects() ) {
		$skip( $what, 'đổi slug cần 301 nhưng site không có bảng redirect của Rank Math: tạo redirect bằng plugin của site trước' );
		continue;
	}
	if ( 'elementor' === $kind[0] ) {
		$slot = $x['value'];
		unset( $w, $slot );
		$el_dirty[ $post ] = true;
	} elseif ( ! $dry ) {
		if ( 'meta' === $kind[0] ) {
			update_post_meta( $post, $kind[1], wp_slash( $x['value'] ) );
		} elseif ( 'acf' === $kind[0] ) {
			update_field( $kind[1], $x['value'], $post );
		} else {
			$wpdb->update( $wpdb->posts, array( $t => $x['value'] ), array( 'ID' => $post ) );
			clean_post_cache( $post );
		}
	}
	if ( 'post_name' === $t && ! empty( $x['redirect'] ) ) {
		$r = wps_add_redirect( $x['redirect']['src'], $x['redirect']['to'], $x['redirect']['code'], $dry, $log );
		if ( true !== $r ) {
			$skip( "$what redirect", $r );
		}
	}
	$ok( $what );
}

// ---- Ghi bộ đệm text, fix ----
foreach ( $buf as $sk => $B ) {
	if ( $B['cur'] === $B['orig'] ) {
		continue;
	}
	$loc = $B['loc'];
	$md5 = md5( is_string( $B['cur'] ) ? $B['cur'] : (string) wp_json_encode( $B['cur'] ) );
	if ( 'post' === $loc['kind'] ) {
		$log['before']['values'][ $B['post'] ][ $loc['col'] ] = $B['orig'];
	} elseif ( 'meta' === $loc['kind'] ) {
		$log['before']['values'][ $B['post'] ][ 'meta:' . $loc['key'] ] = $B['orig'];
	} elseif ( 'usermeta' === $loc['kind'] ) {
		$log['before']['usermeta'][ $loc['uid'] ][ $loc['key'] ] = $B['orig'];
	} else {
		$log['before']['option'][ $loc['name'] ] = $B['orig'];
	}
	$log['md5_after'][ $sk ] = $md5;
	if ( $dry ) {
		continue;
	}
	if ( 'post' === $loc['kind'] ) {
		$wpdb->update( $wpdb->posts, array( $loc['col'] => $B['cur'] ), array( 'ID' => $B['post'] ) );
		clean_post_cache( $B['post'] );
	} elseif ( 'meta' === $loc['kind'] ) {
		update_post_meta( $B['post'], $loc['key'], wp_slash( $B['cur'] ) );
	} elseif ( 'usermeta' === $loc['kind'] ) {
		update_user_meta( $loc['uid'], $loc['key'], wp_slash( $B['cur'] ) );
	} else {
		update_option( $loc['name'], $B['cur'] );
	}
}

if ( ! $dry ) {
	foreach ( array_keys( $el_dirty ) as $post ) {
		$json = wp_json_encode( $el_cache[ $post ] );
		update_post_meta( $post, '_elementor_data', wp_slash( $json ) );
		$log['md5_after'][ "elementor|$post" ] = md5( (string) $json );
		clean_post_cache( $post );
		// Chỉ sinh lại CSS của tài liệu vừa ghi. files_manager->clear_cache() xoá CSS Elementor toàn site.
		if ( class_exists( '\Elementor\Core\Files\CSS\Post' ) ) {
			( new \Elementor\Core\Files\CSS\Post( $post ) )->update();
		}
	}
	if ( class_exists( '\RankMath\Sitemap\Cache' ) ) {
		\RankMath\Sitemap\Cache::invalidate_storage();
	}
	// Xoá object cache (Redis, Memcached) trước khi purge trang: purge trước thì lượt tải kế có thể dựng lại HTML từ object cũ.
	wp_cache_flush();
	// PURGE=0: không purge toàn site, người chạy tự purge theo URL (site có hồ sơ server cấm purge toàn site).
	$purge = getenv( 'PURGE' ) !== '0';
	if ( ! $purge ) {
		// bỏ qua cache trang
	} elseif ( class_exists( '\LiteSpeed\Purge' ) ) {
		\LiteSpeed\Purge::purge_all();
	} elseif ( function_exists( 'rocket_clean_domain' ) ) {
		rocket_clean_domain();
	} elseif ( function_exists( 'w3tc_flush_all' ) ) {
		w3tc_flush_all();
	} elseif ( function_exists( 'wp_cache_clear_cache' ) ) {
		wp_cache_clear_cache();
	}
	$log['purged'] = $purge;
}
foreach ( array( 'md5_after', 'notes', 'redirect_ids' ) as $k ) {
	if ( ! $log[ $k ] ) {
		unset( $log[ $k ] );
	}
}
$json = wp_json_encode( $log, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE );
if ( $out_file ) {
	if ( false === file_put_contents( $out_file, $json . "\n", LOCK_EX ) ) {
		fwrite( STDERR, "Không ghi được OUT: $out_file\n" );
		exit( 1 );
	}
	echo 'OUT ' . $out_file . ' dry=' . ( $dry ? 1 : 0 ) . ' ok=' . count( $log['ok'] ) . ' skip=' . count( $log['skip'] ) . "\n";
} else {
	echo $json, "\n";
}
if ( getenv( 'FAIL_ON_SKIP' ) === '1' && $log['skip'] ) {
	exit( 2 );
}
