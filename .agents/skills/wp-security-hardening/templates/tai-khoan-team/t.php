<?php
// Kiểm tài khoản team + 2FA. Chạy: wp eval-file t.php, JSON trên stdin: {"act":..., "pw":..., "tag":...}.
// In dòng "PASS|FAIL <tên>" và JSON kết quả; không in mật khẩu.
$in  = json_decode( stream_get_contents( STDIN ), true ) ?: [];
$act = $in['act'] ?? '';
$tag = preg_replace( '/[^a-z0-9]/', '', $in['tag'] ?? 'x' );
$W   = 'zz_tw_' . $tag;
$L   = 'zz_sl_' . $tag;
function ok( $name, $cond ) { echo ( $cond ? 'PASS ' : 'FAIL ' ), $name, "\n"; }
function as_user( $u ) { wp_set_current_user( $u ? $u->ID : 0 ); }

if ( 'setup' === $act ) {
	foreach ( [ $W => 'team_writer', $L => 'seo_leader' ] as $login => $role ) {
		$id = wp_insert_user( [ 'user_login' => $login, 'user_pass' => $in['pw'], 'user_email' => $login . '@example.invalid', 'role' => $role, 'display_name' => $login ] );
		ok( "tạo $role", ! is_wp_error( $id ) );
	}
	exit;
}

$w = get_user_by( 'login', $W );
$l = get_user_by( 'login', $L );

if ( 'unit' === $act ) {
	$by = TEAM_BYLINE_ID;
	ok( 'role team_writer có publish_posts, không có unfiltered_html, edit_others_posts, edit_pages', $w && user_can( $w, 'publish_posts' ) && ! user_can( $w, 'unfiltered_html' ) && ! user_can( $w, 'edit_others_posts' ) && ! user_can( $w, 'edit_pages' ) );
	ok( 'role seo_leader có edit_others_posts, edit_pages, rank_math_redirections, create_users; không có manage_options, install_plugins, rank_math_role_manager', $l && user_can( $l, 'edit_others_posts' ) && user_can( $l, 'edit_pages' ) && user_can( $l, 'rank_math_redirections' ) && user_can( $l, 'create_users' ) && ! user_can( $l, 'manage_options' ) && ! user_can( $l, 'install_plugins' ) && ! user_can( $l, 'rank_math_role_manager' ) );

	as_user( $w );
	$p = wp_insert_post( [ 'post_title' => 'zz test ' . $tag, 'post_content' => '<p>ok</p><script>alert(1)</script><p onclick="x()">c</p>', 'post_status' => 'draft', 'post_type' => 'post' ] );
	$post = get_post( $p );
	ok( 'bài mới của Người đăng bài đứng tên team', $post && (int) $post->post_author === $by );
	ok( 'ghi _team_writer = người thật', (int) get_post_meta( $p, '_team_writer', true ) === $w->ID );
	ok( 'Người đăng bài: kses bỏ <script> và onclick', $post && false === strpos( $post->post_content, '<script' ) && false === strpos( $post->post_content, 'onclick' ) );
	ok( 'Người đăng bài sửa được bài đứng tên team', current_user_can( 'edit_post', $p ) );
	if ( empty( $in['prod'] ) ) { // Production: không publish bài thử (purge CDN, sitemap, ping).
		wp_update_post( [ 'ID' => $p, 'post_status' => 'publish' ] );
		ok( 'Người đăng bài đăng thẳng được (publish)', 'publish' === get_post_status( $p ) && current_user_can( 'edit_post', $p ) && current_user_can( 'delete_post', $p ) );
	} else {
		ok( 'Người đăng bài có quyền publish bài đứng tên team', current_user_can( 'publish_posts' ) && current_user_can( 'delete_post', $p ) );
	}
	$admins = get_users( [ 'role' => 'administrator', 'fields' => 'ID' ] );
	$other  = get_posts( [ 'post_type' => 'post', 'author__not_in' => [ $by, $w->ID ], 'numberposts' => 1, 'post_status' => 'any' ] );
	ok( 'Người đăng bài không sửa được bài đứng tên người khác', ! $other || ! current_user_can( 'edit_post', $other[0]->ID ) );
	$pages = get_posts( [ 'post_type' => 'page', 'numberposts' => 1 ] );
	ok( 'Người đăng bài không sửa được trang (page)', ! $pages || ! current_user_can( 'edit_post', $pages[0]->ID ) );
	ok( 'Người đăng bài không quản lý user', ! current_user_can( 'list_users' ) && ! current_user_can( 'edit_user', $l->ID ) );

	as_user( $l );
	ok( 'SEO Leader sửa user Người đăng bài', current_user_can( 'edit_user', $w->ID ) && current_user_can( 'delete_user', $w->ID ) && current_user_can( 'promote_user', $w->ID ) );
	ok( 'SEO Leader không sửa được administrator', ! current_user_can( 'edit_user', (int) $admins[0] ) && ! current_user_can( 'delete_user', (int) $admins[0] ) );
	require_once ABSPATH . 'wp-admin/includes/user.php';
	ok( 'SEO Leader chỉ gán được role Người đăng bài', array_keys( get_editable_roles() ) === [ 'team_writer' ] );
	$nu = wp_insert_user( [ 'user_login' => 'zz_nu_' . $tag, 'user_pass' => wp_generate_password( 24 ), 'user_email' => 'zz_nu_' . $tag . '@example.invalid', 'role' => 'administrator' ] );
	ok( 'User do SEO Leader tạo luôn là Người đăng bài (kể cả khi xin administrator)', ! is_wp_error( $nu ) && [ 'team_writer' ] === array_values( get_userdata( $nu )->roles ) );
	if ( ! is_wp_error( $nu ) ) { as_user( null ); wp_delete_user( $nu ); }
	as_user( $l );
	$admin_post = get_posts( [ 'post_type' => 'post', 'author' => (int) $admins[0], 'numberposts' => 1, 'post_status' => 'any' ] );
	if ( $admin_post ) {
		$before = (int) $admin_post[0]->post_author;
		add_filter( 'wp_insert_post_data', $probe = function ( $d ) use ( &$seen ) { $seen = (int) $d['post_author']; return $d; }, 100 );
		$seen = null;
		apply_filters( 'wp_insert_post_data', [ 'post_type' => 'post', 'post_author' => $before ], [ 'ID' => $admin_post[0]->ID ], [], false );
		remove_filter( 'wp_insert_post_data', $probe, 100 );
		ok( 'SEO Leader sửa bài của người khác: tác giả giữ nguyên', $seen === $before );
	}

	if ( class_exists( 'Two_Factor_Core' ) ) {
		foreach ( [ 'Người đăng bài' => $w, 'SEO Leader' => $l ] as $n => $u ) {
			ok( "2FA tự bật cho $n (Email)", Two_Factor_Core::is_user_using_two_factor( $u->ID ) && 'Two_Factor_Email' === get_class( Two_Factor_Core::get_primary_provider_for_user( $u->ID ) ) );
		}
		$every = true;
		foreach ( get_users( [ 'fields' => 'ID' ] ) as $id ) { $every = $every && Two_Factor_Core::is_user_using_two_factor( (int) $id ); }
		ok( 'Mọi tài khoản trên site đều có 2FA', $every );
	} else {
		ok( 'Plugin Two Factor đang chạy', false );
	}
	as_user( null );
	wp_delete_post( $p, true );
	exit;
}

if ( 'codes' === $act ) { // Bật mã dự phòng cho user kiểm thử, đặt làm phương thức chính, in 2 mã cho harness.
	$codes = Two_Factor_Backup_Codes::get_instance()->generate_codes( $w, [ 'number' => 2 ] );
	update_user_meta( $w->ID, '_two_factor_enabled_providers', [ 'Two_Factor_Email', 'Two_Factor_Backup_Codes' ] );
	update_user_meta( $w->ID, '_two_factor_provider', 'Two_Factor_Backup_Codes' );
	echo json_encode( [ 'codes' => $codes ] ), "\n";
	exit;
}

if ( 'apppw' === $act ) { // Tạo app password cho user kiểm thử, in cho harness.
	$r = WP_Application_Passwords::create_new_application_password( $w->ID, [ 'name' => 'zz test ' . $tag ] );
	echo json_encode( [ 'login' => $W, 'pw' => is_wp_error( $r ) ? '' : $r[0] ] ), "\n";
	exit;
}

if ( 'cleanup' === $act ) {
	require_once ABSPATH . 'wp-admin/includes/user.php';
	foreach ( get_posts( [ 'post_type' => 'post', 's' => 'zz test ' . $tag, 'post_status' => 'any', 'numberposts' => 50 ] ) as $p ) { wp_delete_post( $p->ID, true ); }
	foreach ( [ $W, $L, 'zz_nu_' . $tag ] as $login ) { $u = get_user_by( 'login', $login ); if ( $u ) { wp_delete_user( $u->ID ); } }
	ok( 'dọn user và bài kiểm thử', ! get_user_by( 'login', $W ) && ! get_user_by( 'login', $L ) );
	exit;
}
