# Chạy trên server: python3 htaccess_webp.py add|remove --root <web root> --backup-dir <thư mục ngoài web root> [--dirs 'uploads|themes/<theme>']
# Chèn (hoặc gỡ) block WebP vào <web root>/.htaccess, đặt trước "# BEGIN LSCACHE" (hoặc đầu file nếu không có).
# Đọc bản hiện tại ngay lúc chạy, backup kèm thời gian, ghi nguyên tử, giữ owner và quyền. OpenLiteSpeed cần restart sau khi đổi.
import argparse, os, shutil, sys, time

ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=['add', 'remove'])
ap.add_argument('--root', required=True)
ap.add_argument('--backup-dir', required=True)
ap.add_argument('--dirs', default='uploads')
a = ap.parse_args()

P = os.path.join(a.root, '.htaccess')
BEGIN, END = '# BEGIN WPS WebP', '# END WPS WebP'
BLOCK = BEGIN + '''
# Trả bản .webp cùng URL khi trình duyệt chấp nhận WebP và file <ảnh>.<đuôi>.webp tồn tại. Gỡ: xoá block này.
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTP_ACCEPT} image/webp
RewriteCond %{REQUEST_FILENAME}.webp -f
RewriteRule ^(wp-content/(?:''' + a.dirs + ''')/.+\\.(?:jpe?g|png))$ $1.webp [NC,L]
</IfModule>
''' + END + '\n'

st = os.stat(P)
cur = open(P, encoding='utf-8').read()
os.makedirs(a.backup_dir, exist_ok=True)
bk = os.path.join(a.backup_dir, 'htaccess.' + time.strftime('%Y%m%d-%H%M%S') + '.' + a.mode)
shutil.copy2(P, bk)
if a.mode == 'add':
    if BEGIN in cur:
        print('block đã có, không đổi'); sys.exit(0)
    i = cur.find('# BEGIN LSCACHE')
    new = (cur[:i] + BLOCK + '\n' + cur[i:]) if i >= 0 else (BLOCK + '\n' + cur)
else:
    i, j = cur.find(BEGIN), cur.find(END)
    if i < 0 or j < 0:
        print('không có block'); sys.exit(0)
    new = cur[:i] + cur[j + len(END):].lstrip('\n')
tmp = P + '.wpstmp'
open(tmp, 'w', encoding='utf-8').write(new)
os.chown(tmp, st.st_uid, st.st_gid)
os.chmod(tmp, st.st_mode & 0o777)
os.replace(tmp, P)
print('ok', a.mode, 'backup', bk, 'dòng', cur.count('\n'), '->', new.count('\n'))
