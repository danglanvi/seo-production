<?php
/**
 * Plugin Name: Tài khoản team + 2FA bắt buộc
 * Description: Lead duyệt cấu trúc tài khoản ngày {{NGAY_DUYET}}.
 *   1. Role "SEO Leader" (seo_leader): quyền Editor + Rank Math (trừ Role Manager, .htaccess) + quản lý tài khoản role "Người đăng bài".
 *   2. Role "Người đăng bài" (team_writer): viết, đăng, sửa bài đứng tên team, tải ảnh, meta Rank Math cơ bản. Không có unfiltered_html.
 *   3. Bài do 2 role trên tạo mới đứng tên tài khoản team {{BYLINE_NAME}} (ID {{BYLINE_ID}}). Người đăng bài sửa được mọi bài đứng tên team.
 *   4. Mọi tài khoản phải có 2FA (plugin Two Factor): chưa bật phương thức nào ngoài mã dự phòng thì tự bật Email.
 * Rollback: chuyển file ra khỏi mu-plugins. Role vẫn nằm trong DB; đổi user về editor/author rồi `wp role delete seo_leader team_writer`.
 * Nguồn: skills/wp-security-hardening/templates/tai-khoan-team/team-accounts.php.tpl
 */
defined( 'ABSPATH' ) || exit;

const TEAM_BYLINE_ID  = {{BYLINE_ID}};
const TEAM_ROLES_VER  = 1;

function team_user_has_role( $user, array $roles ) {
	return $user instanceof WP_User && array_intersect( $roles, (array) $user->roles );
}

add_action( 'init', function () {
	if ( (int) get_option( 'team_roles_ver' ) === TEAM_ROLES_VER || ! get_role( 'editor' ) ) {
		return;
	}
	$writer = array_fill_keys( [
		'read', 'edit_posts', 'publish_posts', 'delete_posts', 'edit_published_posts', 'delete_published_posts', 'upload_files',
		'rank_math_onpage_analysis', 'rank_math_onpage_general', 'rank_math_onpage_snippet', 'rank_math_onpage_social',
	], true );
	$leader = get_role( 'editor' )->capabilities;
	foreach ( get_role( 'administrator' )->capabilities as $cap => $on ) {
		if ( $on && 0 === strpos( $cap, 'rank_math_' ) && ! in_array( $cap, [ 'rank_math_role_manager', 'rank_math_edit_htaccess' ], true ) ) {
			$leader[ $cap ] = true;
		}
	}
	$leader += array_fill_keys( [ 'list_users', 'create_users', 'edit_users', 'delete_users', 'promote_users' ], true );
	remove_role( 'team_writer' );
	add_role( 'team_writer', 'Người đăng bài', $writer );
	remove_role( 'seo_leader' );
	add_role( 'seo_leader', 'SEO Leader', $leader );
	update_option( 'team_roles_ver', TEAM_ROLES_VER );
} );

// Bài mới của team đứng tên tài khoản team. Bài đang đứng tên người khác giữ nguyên tác giả.
add_filter( 'wp_insert_post_data', function ( $data, $postarr ) {
	$user = wp_get_current_user();
	if ( 'post' !== $data['post_type'] || ! team_user_has_role( $user, [ 'team_writer', 'seo_leader' ] ) || ! get_userdata( TEAM_BYLINE_ID ) ) {
		return $data;
	}
	$current = empty( $postarr['ID'] ) ? 0 : (int) get_post_field( 'post_author', $postarr['ID'] );
	if ( ! $current || $current === $user->ID ) {
		$data['post_author'] = TEAM_BYLINE_ID;
	}
	return $data;
}, 99, 2 );

// Ghi người thật đã tạo bài (tác giả hiển thị là tài khoản team).
add_action( 'wp_after_insert_post', function ( $post_id, $post ) {
	$user = wp_get_current_user();
	if ( 'post' === $post->post_type && (int) $post->post_author === TEAM_BYLINE_ID && team_user_has_role( $user, [ 'team_writer', 'seo_leader' ] ) ) {
		add_post_meta( $post_id, '_team_writer', $user->ID, true );
	}
}, 10, 2 );

add_filter( 'map_meta_cap', function ( $caps, $cap, $user_id, $args ) {
	// Người đăng bài sửa, xoá được bài đứng tên team như bài của mình.
	if ( in_array( $cap, [ 'edit_post', 'delete_post' ], true ) && ! empty( $args[0] ) ) {
		$post = get_post( $args[0] );
		if ( $post && 'post' === $post->post_type && (int) $post->post_author === TEAM_BYLINE_ID && team_user_has_role( get_userdata( $user_id ), [ 'team_writer' ] ) ) {
			return str_replace( [ 'edit_others_posts', 'delete_others_posts' ], [ 'edit_posts', 'delete_posts' ], $caps );
		}
		return $caps;
	}
	// SEO Leader chỉ quản lý tài khoản "Người đăng bài" và hồ sơ của chính mình.
	if ( in_array( $cap, [ 'edit_user', 'delete_user', 'promote_user', 'remove_user' ], true ) && ! empty( $args[0] ) && (int) $args[0] !== (int) $user_id ) {
		$actor = get_userdata( $user_id );
		if ( team_user_has_role( $actor, [ 'seo_leader' ] ) && ! user_can( $actor, 'manage_options' ) ) {
			$target = get_userdata( $args[0] );
			if ( ! $target || [ 'team_writer' ] !== array_values( $target->roles ) ) {
				return [ 'do_not_allow' ];
			}
		}
	}
	return $caps;
}, 10, 4 );

add_filter( 'editable_roles', function ( $roles ) {
	$user = wp_get_current_user();
	if ( team_user_has_role( $user, [ 'seo_leader' ] ) && ! user_can( $user, 'manage_options' ) ) {
		return array_intersect_key( $roles, [ 'team_writer' => true ] );
	}
	return $roles;
} );

// Tài khoản do SEO Leader tạo luôn là "Người đăng bài", kể cả khi form không gửi role.
add_action( 'user_register', function ( $user_id ) {
	$actor = wp_get_current_user();
	if ( team_user_has_role( $actor, [ 'seo_leader' ] ) && ! user_can( $actor, 'manage_options' ) ) {
		( new WP_User( $user_id ) )->set_role( 'team_writer' );
	}
}, 20 );

// 2FA bắt buộc: không có phương thức nào ngoài mã dự phòng thì bật Email.
add_filter( 'two_factor_enabled_providers_for_user', function ( $enabled ) {
	$enabled = (array) $enabled;
	return array_diff( $enabled, [ 'Two_Factor_Backup_Codes' ] ) ? $enabled : array_merge( [ 'Two_Factor_Email' ], $enabled );
} );
