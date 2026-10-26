<?php
/* mu-plugin TẠM, chỉ dùng trên staging để đo robots và canonical của chuyên mục, phân trang như site public.
 * Staging ép noindex toàn site qua pre_option_blog_public = '0' (zz-staging-safety.php của wp-staging-deploy).
 * File này trả '1' ở priority 99, nên Rank Math và theme xuất thẻ robots theo cấu hình thật.
 * Header X-Robots-Tag noindex và robots.txt chặn của staging vẫn giữ nguyên.
 * Gỡ file ngay sau lượt đo. Không chép lên production (guard WP_ENVIRONMENT_TYPE bên dưới). */
if ( ! defined( 'WP_ENVIRONMENT_TYPE' ) || WP_ENVIRONMENT_TYPE !== 'staging' ) { return; }
add_filter( 'pre_option_blog_public', function () { return '1'; }, 99 );
