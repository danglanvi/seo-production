"""Test offline cho script của wp-security-hardening v1.7. Chạy: python3 -B scripts/tests/test_sec_scripts.py
Không SSH, không gọi site thật. SSH được thay bằng shim chạy lệnh cục bộ. HTTP chạy trên server giả 127.0.0.1.
Ca hỏng thật (nguồn: de-xuat-chi-tiet_76.md, sec-1, sec-4, và bản v1.5 của skill):
- 17/10: áp khối làm 13 trang 404, mất 3,5 phút phát hiện và rollback tay (sec-1).
- 16/10: backup ra file 0 byte vì server không có zstd, rc=127 (sec-4).
- 18/10: backup_pull.sh báo exit 0 dù 'rsync: command not found' (sec-4).
- 17/10: dump một phần có DROP TABLE suýt xoá bảng termmeta (sec-4).
- 19/10: theme trả 410 cho path lạ nên site qua kiểm dù chưa có rule (v1.5, sec-10).
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
TEMPLATES = os.path.join(SKILL, 'templates', 'backup-tu-dong')
APPLY = os.path.join(SCRIPTS, 'apply_server_block.sh')
EXPOSURE = os.path.join(SCRIPTS, 'exposure_check.sh')
PREFLIGHT = os.path.join(SCRIPTS, 'preflight_remote.sh')
VERIFY = os.path.join(SCRIPTS, 'verify_backup.sh')
PULL = os.path.join(TEMPLATES, 'backup_pull.sh')
SITEBK = os.path.join(TEMPLATES, 'site-backup.sh')
CNFPHP = os.path.join(TEMPLATES, 'backup-cnf.php')
PHP = shutil.which('php')

FAKE_SSH = '''#!/bin/bash
# ssh giả: bỏ alias, chạy phần lệnh còn lại cục bộ như shell từ xa.
shift
PATH="${FAKE_REMOTE_PATH:-$PATH}" exec bash -c "$*"
'''


def sh(args, env=None, input_=None, timeout=60):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(args, capture_output=True, text=True, env=e, input=input_, timeout=timeout)


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)
    return path


def md5(path):
    import hashlib
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def toolbox(root, names, extra=None):
    """Thư mục PATH chỉ chứa các công cụ trong names (symlink) cộng shim extra {tên: nội dung script}."""
    d = os.path.join(root, 'tb-' + str(len(os.listdir(root))))
    os.makedirs(d)
    for n in names:
        p = shutil.which(n)
        if p:
            os.symlink(p, os.path.join(d, n))
    for n, body in (extra or {}).items():
        write(os.path.join(d, n), body, 0o755)
    return d


BASE_TOOLS = ['bash', 'sed', 'awk', 'cut', 'tr', 'head', 'tail', 'wc', 'sort', 'cat', 'date', 'mktemp', 'mkdir', 'rm', 'mv', 'cp',
              'grep', 'basename', 'dirname', 'du', 'df', 'ls', 'touch', 'chmod']


class Site:
    """Server HTTP giả. Hành vi phụ thuộc nội dung file htaccess giả, giống một site sau khi áp khối."""

    def __init__(self, htaccess, flag=None, random_code=404):
        self.htaccess, self.flag, self.random_code = htaccess, flag, random_code
        site = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                code = site.code(self.path)
                loc = '/' if code in (301, 302) else None
                self.send_response(code)
                if loc:
                    self.send_header('Location', loc + 'slug-an')
                self.send_header('Content-Length', '2')
                self.end_headers()
                self.wfile.write(b'ok')

        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.url = 'http://127.0.0.1:%d' % self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def code(self, path):
        try:
            ht = open(self.htaccess, encoding='utf-8').read() if self.htaccess else ''
        except OSError:
            ht = ''
        active = (not self.flag) or os.path.exists(self.flag)  # OpenLiteSpeed: rule chỉ có tác dụng sau restart
        if '/wps-' in path:
            return self.random_code
        if path.startswith('/blog/') and 'BREAK-BLOG' in ht and active:
            return 404
        if path == '/wp-content/uploads/test.php':
            return 403 if ('BLOCK-UPLOADS-PHP' in ht and active) else 200
        if path == '/wp-activate.php':
            return 302
        if path == '/wp-config.php':
            return 404
        return 200

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class ApplyBase(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)
        self.ssh = write(os.path.join(self.t, 'fake_ssh.sh'), FAKE_SSH, 0o755)
        self.rfile = os.path.join(self.t, 'srv', 'www', '.htaccess')
        write(self.rfile, '# WordPress\nRewriteEngine On\nRewriteRule . /index.php [L]\n', 0o640)
        self.orig = md5(self.rfile)
        self.bk_local = os.path.join(self.t, 'Backups')
        self.bk_remote = os.path.join(self.t, 'rbk')
        self.flag = os.path.join(self.t, 'restarted')
        self.block = write(os.path.join(self.t, 'block.txt'), 'RewriteRule ^wp-content/uploads/.*\\.php$ - [F,L] # BLOCK-UPLOADS-PHP\n')
        self.probes = write(os.path.join(self.t, 'probes.txt'), '403 /wp-content/uploads/test.php PHP trong uploads phải 403\n')
        self.paths = write(os.path.join(self.t, 'paths.txt'), '/\n/wp-login.php\n/wp-admin/admin-ajax.php\n' + ''.join('/blog/bai-%d/\n' % i for i in range(1, 14)))
        self.site = None

    def start_site(self, **kw):
        self.site = Site(self.rfile, **kw)
        self.addCleanup(self.site.close)

    def apply(self, *extra, block=None, apply_=True, env=None):
        if self.site is None:
            self.start_site()
        args = ['bash', APPLY, '--alias', 'test-alias', '--target', 'htaccess', '--remote-file', self.rfile,
                '--block', block or self.block, '--mark', 'sec-test', '--site-url', self.site.url, '--probes', self.probes,
                '--paths', self.paths, '--backup-root', self.bk_local, '--remote-backup-root', self.bk_remote, '--wait', '0']
        if apply_:
            args.append('--apply')
        e = {'SSH_CMD': self.ssh}
        e.update(env or {})
        return sh(args + list(extra), env=e)

    def backups(self):
        out = []
        for r, _d, f in os.walk(self.bk_local):
            out += [os.path.join(r, x) for x in f if x == 'rollback.sh']
        return out

    def text(self):
        return open(self.rfile, encoding='utf-8').read()


class TestApplyServerBlock(ApplyBase):
    def test_help(self):
        r = sh(['bash', APPLY, '--help'])
        self.assertEqual(r.returncode, 0)
        self.assertIn('--apply', r.stdout)

    def test_bad_args(self):
        r = sh(['bash', APPLY, '--alias', 'a', '--target', 'mycnf', '--remote-file', '/x', '--block', self.block, '--mark', 'm', '--site-url', 'http://x'])
        self.assertEqual(r.returncode, 2)
        r = sh(['bash', APPLY, '--alias', 'a', '--target', 'htaccess', '--remote-file', '/x', '--block', self.block, '--mark', 'bad mark', '--site-url', 'http://x'])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(sh(['bash', APPLY, '--khong-co']).returncode, 2)

    def test_dry_run_writes_nothing(self):
        r = self.apply(apply_=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('DIỄN TẬP', r.stdout)
        self.assertIn('BLOCK-UPLOADS-PHP', r.stdout)  # diff hiện khối sẽ chèn
        self.assertEqual(md5(self.rfile), self.orig)
        self.assertFalse(os.path.exists(self.bk_local))
        self.assertFalse(os.path.exists(self.bk_remote) and os.listdir(self.bk_remote))

    def test_apply_ok_backup_probe_rollback_file(self):
        r = self.apply()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = self.text()
        self.assertEqual(t.count('# BEGIN sec-test ('), 1)
        self.assertEqual(t.count('# END sec-test'), 1)
        self.assertTrue(t.startswith('# BEGIN sec-test'))  # htaccess: chèn ở đầu
        self.assertEqual(stat.S_IMODE(os.stat(self.rfile).st_mode), 0o640)  # giữ mode
        rbs = self.backups()
        self.assertEqual(len(rbs), 1)
        pre = os.path.dirname(rbs[0])
        self.assertEqual(md5(os.path.join(pre, '.htaccess')), self.orig)  # backup ở máy này khớp file gốc
        self.assertIn(self.orig, open(os.path.join(pre, 'MD5SUMS')).read())
        remote_bks = [os.path.join(self.bk_remote, d) for d in os.listdir(self.bk_remote)]
        self.assertEqual(len(remote_bks), 1)
        self.assertEqual(md5(os.path.join(remote_bks[0], '.htaccess')), self.orig)  # backup trên server khớp
        self.assertTrue(os.path.exists(os.path.join(pre, 'http_before.tsv')))
        self.assertFalse([f for f in os.listdir(os.path.dirname(self.rfile)) if 'wps-new' in f])
        # rollback tự sinh chạy được
        rb = sh(['bash', rbs[0]], env={'SSH_CMD': self.ssh})
        self.assertEqual(rb.returncode, 0, rb.stdout + rb.stderr)
        self.assertEqual(md5(self.rfile), self.orig)

    def test_idempotent_same_block(self):
        self.assertEqual(self.apply().returncode, 0)
        after_first = md5(self.rfile)
        n = len(self.backups())
        r = self.apply()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('giống hệt', r.stdout)
        self.assertEqual(md5(self.rfile), after_first)
        self.assertEqual(len(self.backups()), n)  # không tạo backup mới khi không có gì để làm

    def test_changed_block_replaces_in_place(self):
        self.assertEqual(self.apply().returncode, 0)
        b2 = write(os.path.join(self.t, 'block2.txt'), 'RewriteRule ^wp-content/uploads/.*\\.php$ - [F,L] # BLOCK-UPLOADS-PHP v2\nRewriteRule ^xmlrpc\\.php$ - [F]\n')
        r = self.apply(block=b2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = self.text()
        self.assertEqual(t.count('# BEGIN sec-test'), 1)
        self.assertIn('v2', t)
        self.assertEqual(t.count('RewriteRule . /index.php [L]'), 1)  # phần còn lại không đổi

    def test_regression_13_pages_404_auto_rollback(self):
        """Ca hỏng 17/10: khối làm 13 trang bài trả 404. Script phải thấy, rollback, và file về đúng bản gốc."""
        bad = write(os.path.join(self.t, 'bad.txt'), 'RewriteRule ^blog/ - [R=404] # BREAK-BLOG\nRewriteRule ^wp-content/uploads/.*\\.php$ - [F,L] # BLOCK-UPLOADS-PHP\n')
        r = self.apply(block=bad)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn('HỒI QUY', r.stderr)
        self.assertEqual(r.stderr.count('/blog/bai-'), 13)  # liệt kê đủ 13 trang
        self.assertIn('ROLLBACK OK', r.stdout)
        self.assertEqual(md5(self.rfile), self.orig)

    def test_regression_no_auto_rollback_then_manual(self):
        bad = write(os.path.join(self.t, 'bad.txt'), 'RewriteRule ^blog/ - [R=404] # BREAK-BLOG\n')
        r = self.apply('--no-auto-rollback', block=bad)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertNotEqual(md5(self.rfile), self.orig)
        self.assertIn('rollback.sh', r.stderr)
        rb = sh(['bash', self.backups()[0]], env={'SSH_CMD': self.ssh})
        self.assertEqual(rb.returncode, 0, rb.stdout + rb.stderr)
        self.assertEqual(md5(self.rfile), self.orig)

    def test_probe_fail_without_restart_then_ok_with_restart(self):
        self.start_site(flag=self.flag)  # rule chỉ có tác dụng sau restart, như OpenLiteSpeed
        r = self.apply()
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)
        self.assertIn('--restart 1', r.stderr)
        self.assertIn('FAIL', r.stdout)
        # cùng nhãn, cùng khối: lần này thêm restart. Khối đã có nên script báo giống hệt, rollback rồi áp lại.
        sh(['bash', self.backups()[0]], env={'SSH_CMD': self.ssh})
        self.assertEqual(md5(self.rfile), self.orig)
        r = self.apply('--restart', '1', '--restart-cmd', 'touch %s' % self.flag)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(self.flag))

    def test_restart_failure_rolls_back(self):
        # restart lỗi lần đầu, lần sau (sau rollback) chạy được
        cmd = '[ -e %s ] || { touch %s; false; }' % (self.flag, self.flag)
        r = self.apply('--restart', '1', '--restart-cmd', cmd)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertEqual(md5(self.rfile), self.orig)
        self.assertIn('ROLLBACK OK', r.stdout)

    def test_restart_always_failing_exit_8_but_file_restored(self):
        r = self.apply('--restart', '1', '--restart-cmd', 'false')
        self.assertEqual(r.returncode, 8, r.stdout + r.stderr)
        self.assertEqual(md5(self.rfile), self.orig)  # file đã về bản gốc dù restart vẫn lỗi
        self.assertIn('restart sau rollback thất bại', r.stderr)

    def test_missing_remote_file(self):
        os.remove(self.rfile)
        r = self.apply()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(self.bk_local))

    def test_broken_markers_refuse(self):
        with open(self.rfile, 'a') as f:
            f.write('# BEGIN sec-test (2026-10-01)\nRewriteRule x y\n')
        before = md5(self.rfile)
        r = self.apply()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertEqual(md5(self.rfile), before)

    def test_check_cmd_failure_keeps_original(self):
        r = self.apply('--check-cmd', 'grep -q KHONG-BAO-GIO {FILE}')
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertEqual(md5(self.rfile), self.orig)
        self.assertFalse([f for f in os.listdir(os.path.dirname(self.rfile)) if 'wps-new' in f])

    def test_check_cmd_success(self):
        r = self.apply('--check-cmd', 'grep -q BLOCK-UPLOADS-PHP {FILE}')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_preflight_missing_md5_tool(self):
        tb = toolbox(self.t, ['bash', 'cp', 'mv', 'stat', 'chmod', 'chown', 'mkdir', 'cat', 'cut', 'rm', 'sed', 'tr', 'awk', 'python3'])
        r = self.apply(env={'FAKE_REMOTE_PATH': tb})
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn('md5sum', r.stderr)
        self.assertEqual(md5(self.rfile), self.orig)

    def test_bottom_and_after(self):
        r = self.apply('--position', 'bottom')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.text().rstrip().endswith('# END sec-test'))
        sh(['bash', self.backups()[0]], env={'SSH_CMD': self.ssh})
        r = self.apply('--after', '^RewriteEngine On')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = self.text().splitlines()
        self.assertEqual(lines[2], '# BEGIN sec-test (' + lines[2].split('(')[1])
        sh(['bash', self.backups()[-1]], env={'SSH_CMD': self.ssh})
        r = self.apply('--after', '^KHONG-CO-DONG-NAY')
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(md5(self.rfile), self.orig)


class TestExposureCheck(unittest.TestCase):
    """sec-10: URL ngẫu nhiên phải 404. Ca hỏng: theme trả 410 (hoặc 200, 301) cho path lạ nhưng vẫn qua kiểm."""

    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)
        self.list = write(os.path.join(self.t, 'l.txt'), '404 /wps-{RAND}/ ngẫu nhiên\n404 /wps-{RAND}.html ngẫu nhiên\n404|403|410 /wp-config.php\n')

    def run_with(self, code):
        s = Site(None, random_code=code)
        self.addCleanup(s.close)
        return sh(['bash', EXPOSURE, s.url, self.list], env={'WPS_RAND': 'abc123'})

    def test_404_ok(self):
        r = self.run_with(404)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('/wps-abc123/', r.stdout)  # {RAND} đã thay

    def test_410_fails(self):
        r = self.run_with(410)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual(r.stdout.count('FAIL'), 2)

    def test_200_soft_404_fails(self):
        self.assertEqual(self.run_with(200).returncode, 1)

    def test_301_to_home_fails_and_hides_location(self):
        r = self.run_with(301)
        self.assertEqual(r.returncode, 1)
        self.assertNotIn('slug-an', r.stdout)
        self.assertIn('có redirect', r.stdout)

    def test_show_location_flag(self):
        s = Site(None, random_code=301)
        self.addCleanup(s.close)
        r = sh(['bash', EXPOSURE, s.url, self.list, '--show-location'], env={'WPS_RAND': 'abc123'})
        self.assertIn('slug-an', r.stdout)

    def test_rand_changes_between_runs(self):
        s = Site(None)
        self.addCleanup(s.close)
        a = sh(['bash', EXPOSURE, s.url, self.list]).stdout
        b = sh(['bash', EXPOSURE, s.url, self.list]).stdout
        self.assertNotEqual(a.splitlines()[0], b.splitlines()[0])

    def test_empty_200_still_ok_without_rand(self):
        # wp-config.php trả 200 rỗng vẫn được chấp nhận như trước (khác với dòng {RAND})
        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Length', '0')
                self.end_headers()
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), H)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close)
        self.addCleanup(httpd.shutdown)
        one = write(os.path.join(self.t, 'one.txt'), '403 /wp-config.php\n404 /wps-{RAND}/\n')
        r = sh(['bash', EXPOSURE, 'http://127.0.0.1:%d' % httpd.server_address[1], one])
        self.assertIn('(200 rỗng)', r.stdout)
        self.assertEqual(r.stdout.count('FAIL'), 1)  # chỉ dòng {RAND}

    def test_default_list_has_rand_probes_and_help(self):
        d = open(os.path.join(SCRIPTS, 'exposure_default.txt'), encoding='utf-8').read()
        self.assertGreaterEqual(d.count('{RAND}'), 2)
        self.assertEqual(sh(['bash', EXPOSURE, '--help']).returncode, 0)
        self.assertEqual(sh(['bash', EXPOSURE]).returncode, 2)


class TestPreflightRemote(unittest.TestCase):
    """sec-4: server không có zstd (16/10, rc=127, file 0 byte). Preflight phải báo phương án thay hoặc dừng."""

    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)

    def run_pf(self, tools, *args):
        tb = toolbox(self.t, BASE_TOOLS + tools)
        return sh(['/bin/bash', PREFLIGHT, '--path', self.t] + list(args), env={'PATH': tb})

    def test_help(self):
        self.assertEqual(sh(['bash', PREFLIGHT, '--help']).returncode, 0)
        self.assertEqual(sh(['bash', PREFLIGHT, '--la']).returncode, 2)

    def test_all_tools_ok(self):
        r = self.run_pf(['tar', 'gzip', 'zstd', 'rsync'])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('COMPRESS=zstd', r.stdout)
        self.assertIn('PULL=rsync', r.stdout)
        self.assertIn('RESULT=ok', r.stdout)

    def test_no_zstd_falls_back_to_gzip(self):
        r = self.run_pf(['tar', 'gzip', 'rsync'])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('COMPRESS=gzip', r.stdout)
        self.assertIn('RESULT=degraded', r.stdout)
        self.assertIn('file 0 byte', r.stdout)

    def test_no_compressor_fails(self):
        r = self.run_pf(['tar', 'rsync'])
        self.assertEqual(r.returncode, 1)
        self.assertIn('RESULT=fail', r.stdout)

    def test_no_rsync_uses_tar_over_ssh(self):
        r = self.run_pf(['tar', 'gzip', 'zstd'])
        self.assertEqual(r.returncode, 0)
        self.assertIn('PULL=tar-ssh', r.stdout)
        self.assertIn('RESULT=degraded', r.stdout)

    def test_need_db_without_mysqldump_fails(self):
        r = self.run_pf(['tar', 'gzip', 'zstd', 'rsync'], '--need-db')
        self.assertEqual(r.returncode, 1)
        self.assertIn('mysqldump', r.stdout)

    def test_low_disk_fails(self):
        r = self.run_pf(['tar', 'gzip', 'zstd', 'rsync'], '--min-free-gb', '99999999')
        self.assertEqual(r.returncode, 1)
        self.assertIn('RESULT=fail', r.stdout)


def noise(n):
    import random
    rnd = random.Random(7)
    return ''.join('INSERT INTO `wp_posts` VALUES (%d,\'%032x\');\n' % (i, rnd.getrandbits(128)) for i in range(n))


DUMP_FULL = ''.join('DROP TABLE IF EXISTS `wp_t%d`;\nCREATE TABLE `wp_t%d` (id int);\nINSERT INTO `wp_t%d` VALUES (1);\n' % (i, i, i) for i in range(3)) + '-- Dump completed on 2026-10-25\n'


def compress(path, data, kind):
    raw = path + '.raw'
    write(raw, data)
    if kind == 'zst':
        subprocess.run(['zstd', '-q', '-f', raw, '-o', path], check=True)
    elif kind == 'gz':
        with open(path, 'wb') as f:
            subprocess.run(['gzip', '-c', raw], stdout=f, check=True)
    else:
        shutil.copy(raw, path)
    os.remove(raw)
    return path


@unittest.skipUnless(shutil.which('zstd'), 'cần zstd để dựng file mẫu')
class TestVerifyBackup(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)

    def f(self, name, data, kind):
        return compress(os.path.join(self.t, name), data, kind)

    def test_help(self):
        self.assertEqual(sh(['bash', VERIFY, '--help']).returncode, 0)
        self.assertEqual(sh(['bash', VERIFY]).returncode, 2)

    def test_zero_byte_file_fails(self):
        """Ca 16/10: server không có zstd, lệnh ra file 0 byte và script vẫn đi tiếp."""
        p = write(os.path.join(self.t, 'site-db.sql.zst'), '')
        r = sh(['bash', VERIFY, p])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn('0 byte', r.stdout)

    def test_good_full_dumps(self):
        for kind, name in (('zst', 'a.sql.zst'), ('gz', 'b.sql.gz'), ('', 'c.sql')):
            r = sh(['bash', VERIFY, '--min-bytes', '10', '--min-tables', '3', self.f(name, DUMP_FULL, kind)])
            self.assertEqual(r.returncode, 0, name + r.stdout)
            self.assertIn('3 bảng', r.stdout)

    def test_truncated_dump_fails(self):
        p = self.f('a.sql.gz', DUMP_FULL.replace('-- Dump completed on 2026-10-25\n', ''), 'gz')
        r = sh(['bash', VERIFY, '--min-bytes', '10', p])
        self.assertEqual(r.returncode, 1)
        self.assertIn('Dump completed', r.stdout)

    def test_too_few_tables_fails(self):
        p = self.f('a.sql.zst', DUMP_FULL, 'zst')
        self.assertEqual(sh(['bash', VERIFY, '--min-bytes', '10', '--min-tables', '146', p]).returncode, 1)

    def test_corrupt_gzip_fails(self):
        p = self.f('a.sql.gz', DUMP_FULL * 50, 'gz')
        data = open(p, 'rb').read()
        open(p, 'wb').write(data[:len(data) // 2])
        r = sh(['bash', VERIFY, '--min-bytes', '10', p])
        self.assertEqual(r.returncode, 1)

    def test_partial_dump_with_drop_table_fails(self):
        """Ca 17/10: dump --where không có --no-create-info, có DROP TABLE termmeta, nạp lại sẽ xoá cả bảng."""
        data = 'DROP TABLE IF EXISTS `wp_termmeta`;\nCREATE TABLE `wp_termmeta` (id int);\nINSERT INTO `wp_termmeta` VALUES (1);\n-- Dump completed\n'
        p = self.f('part.sql.gz', data, 'gz')
        r = sh(['bash', VERIFY, '--partial', '--min-bytes', '10', p])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn('DROP TABLE', r.stdout)
        self.assertIn('CREATE TABLE', r.stdout)

    def test_partial_dump_replace_only_ok(self):
        p = self.f('part.sql.gz', "REPLACE INTO `wp_termmeta` VALUES (1,2,'a','b');\n", 'gz')
        r = sh(['bash', VERIFY, '--partial', '--min-bytes', '10', p])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('REPLACE INTO=1', r.stdout)

    def test_partial_dump_insert_warns(self):
        p = self.f('part.sql', "INSERT INTO `wp_termmeta` VALUES (1,2,'a','b');\n", '')
        r = sh(['bash', VERIFY, '--partial', '--min-bytes', '10', p])
        self.assertEqual(r.returncode, 0)
        self.assertIn('cảnh báo', r.stdout)

    def test_sums_written_by_basename_only_when_all_ok(self):
        a = self.f('a.sql.zst', DUMP_FULL, 'zst')
        r = sh(['bash', VERIFY, '--min-bytes', '10', '--write-sums', a])
        self.assertEqual(r.returncode, 0, r.stdout)
        with open(os.path.join(self.t, 'SHA256SUMS')) as fh:
            sums = fh.read()
        self.assertIn('  a.sql.zst', sums)
        self.assertNotIn(self.t, sums)
        self.assertEqual(subprocess.run(['shasum', '-a', '256', '-c', 'SHA256SUMS'], cwd=self.t, capture_output=True).returncode, 0)
        # chạy lại không nhân đôi dòng
        sh(['bash', VERIFY, '--min-bytes', '10', '--write-sums', a])
        with open(os.path.join(self.t, 'SHA256SUMS')) as fh:
            self.assertEqual(fh.read().count('a.sql.zst'), 1)

    def test_sums_not_written_when_any_fails(self):
        d = os.path.join(self.t, 'x')
        os.makedirs(d)
        ok = compress(os.path.join(d, 'a.sql.zst'), DUMP_FULL, 'zst')
        bad = write(os.path.join(d, 'b.sql.zst'), '')
        r = sh(['bash', VERIFY, '--min-bytes', '10', '--write-sums', ok, bad])
        self.assertEqual(r.returncode, 1)
        self.assertFalse(os.path.exists(os.path.join(d, 'SHA256SUMS')))

    def test_tar_archives(self):
        src = os.path.join(self.t, 'src')
        write(os.path.join(src, 'a.txt'), noise(200))
        tz = os.path.join(self.t, 'f.tar.zst')
        subprocess.run('tar -C "%s" -cf - . | zstd -q -f -o "%s"' % (src, tz), shell=True, check=True)
        r = sh(['bash', VERIFY, tz])
        self.assertEqual(r.returncode, 0, r.stdout)
        empty = write(os.path.join(self.t, 'e.tar.zst'), '')
        self.assertEqual(sh(['bash', VERIFY, empty]).returncode, 1)
        junk = write(os.path.join(self.t, 'j.tar.zst'), 'khong phai zstd ' * 200)
        self.assertEqual(sh(['bash', VERIFY, junk]).returncode, 1)

    def test_missing_file_and_unknown_ext(self):
        self.assertEqual(sh(['bash', VERIFY, os.path.join(self.t, 'khong-co.sql')]).returncode, 1)
        p = write(os.path.join(self.t, 'x.bin'), 'a' * 3000)
        self.assertEqual(sh(['bash', VERIFY, p]).returncode, 1)


def make_server_tree(root, with_db=True, zero_db=False, last_ok=None):
    """Cây /www/backup/auto giả. last_ok None thì lấy giờ hiện tại."""
    src = os.path.join(root, 'srv-backup', 'auto')
    os.makedirs(os.path.join(src, 'db'))
    os.makedirs(os.path.join(src, 'files'))
    if with_db:
        p = os.path.join(src, 'db', 'site-db-Sun-0.sql.zst')
        if zero_db:
            write(p, '')
        else:
            compress(p, DUMP_FULL.replace('-- Dump completed', noise(200) + '-- Dump completed'), 'zst')
    write(os.path.join(src, 'files', 'site-files-0.tar.zst'), 'x' * 100)
    ts = last_ok or subprocess.run(['date', '+%F %T'], capture_output=True, text=True).stdout.strip()
    write(os.path.join(src, 'LAST_OK_db'), ts + '\n')
    return src


@unittest.skipUnless(shutil.which('zstd'), 'cần zstd để dựng file mẫu')
class TestBackupPull(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)
        self.ssh = write(os.path.join(self.t, 'fake_ssh.sh'), FAKE_SSH, 0o755)
        self.dest = os.path.join(self.t, 'dest')
        self.sub = os.path.join(self.t, 'repo', 'templates', 'backup-tu-dong')

    def run_pull(self, src, extra_path_first=None, remote_path=None, env=None):
        e = {'SSH_CMD': self.ssh, 'ALIAS': 'test-alias', 'DEST': self.dest, 'SRC': src, 'VERIFY': VERIFY}
        if extra_path_first:
            e['PATH'] = extra_path_first + os.pathsep + os.environ['PATH']
        if remote_path:
            e['FAKE_REMOTE_PATH'] = remote_path
        e.update(env or {})
        return sh(['bash', PULL], env=e)

    RSYNC_OK = '#!/bin/bash\nsrc="${@: -2:1}"; dst="${@: -1}"; src="${src#*:}"; cp -R "$src." "$dst"\n'
    RSYNC_MISSING = '#!/bin/bash\necho "bash: rsync: command not found" >&2\nexit 127\n'

    def test_help_and_missing_alias(self):
        self.assertEqual(sh(['bash', PULL, '--help']).returncode, 0)
        r = sh(['bash', PULL], env={'ALIAS': ''})
        self.assertEqual(r.returncode, 2)

    def test_rsync_ok(self):
        src = make_server_tree(self.t)
        shim = toolbox(self.t, [], {'rsync': self.RSYNC_OK})
        r = self.run_pull(src, shim)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dest, 'db', 'site-db-Sun-0.sql.zst')))

    def test_rsync_missing_on_server_uses_tar(self):
        src = make_server_tree(self.t)
        remote = toolbox(self.t, ['bash', 'tar', 'cat'])  # server không có rsync
        r = self.run_pull(src, remote_path=remote)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('THAY THẾ', r.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.dest, 'db', 'site-db-Sun-0.sql.zst')))

    def test_rsync_command_not_found_must_not_exit_zero(self):
        """Ca 18/10: 'rsync: command not found' mà script thoát 0. Ở đây rsync trả 127: phải thoát khác 0."""
        src = make_server_tree(self.t)
        # LAST_OK_db có sẵn ở máy từ lần kéo trước: kiểu dữ liệu cũ khiến script báo thành công giả
        write(os.path.join(self.dest, 'LAST_OK_db'), subprocess.run(['date', '+%F %T'], capture_output=True, text=True).stdout.strip() + '\n')
        shim = toolbox(self.t, [], {'rsync': self.RSYNC_MISSING})
        r = self.run_pull(src, shim)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('127', r.stderr)

    def test_zero_byte_db_after_pull_fails(self):
        src = make_server_tree(self.t, zero_db=True)
        shim = toolbox(self.t, [], {'rsync': self.RSYNC_OK})
        r = self.run_pull(src, shim)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('0 byte', r.stdout)

    def test_stale_backup_fails(self):
        src = make_server_tree(self.t, last_ok='2020-01-01 00:00:00')
        shim = toolbox(self.t, [], {'rsync': self.RSYNC_OK})
        r = self.run_pull(src, shim)
        self.assertEqual(r.returncode, 1)
        self.assertIn('48 giờ', r.stderr)

    def test_linux_date_dash_d_branch(self):
        """Máy Linux dùng date -d. Shim date mô phỏng GNU date, kiểm script ưu tiên nhánh -d."""
        src = make_server_tree(self.t)
        gnu = '#!/bin/bash\nif [ "$1" = "-d" ]; then python3 -I -c \'import sys,time;print(int(time.mktime(time.strptime(sys.argv[1],"%Y-%m-%d %H:%M:%S"))))\' "$2"; exit; fi\nif [ "$1" = "-j" ]; then echo "date: illegal option -- j" >&2; exit 1; fi\nexec /bin/date "$@"\n'
        shim = toolbox(self.t, [], {'rsync': self.RSYNC_OK, 'date': gnu})
        r = self.run_pull(src, shim)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


DUMPER = '''#!/bin/bash
echo "$@" > "$ARGS_FILE"
case "${DUMP_MODE:-ok}" in
  ok) printf 'CREATE TABLE `wp_a` (id int);\\nINSERT INTO `wp_a` VALUES (1);\\n-- Dump completed on 2026-10-25\\n';;
  trunc) printf 'CREATE TABLE `wp_a` (id int);\\nINSERT INTO `wp_a` VALUES (1);\\n';;
  fail) echo "mysqldump: Error: 'Access denied; you need the PROCESS privilege' when trying to dump tablespaces" >&2; exit 2;;
esac
'''


@unittest.skipUnless(PHP, 'cần php để chạy backup-cnf.php')
class TestSiteBackup(unittest.TestCase):
    """Chạy site-backup.sh db trong thư mục giả. mysqldump giả."""

    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)
        self.site = os.path.join(self.t, 'www', 'example.com')
        write(os.path.join(self.site, 'wp-config.php'), "<?php\ndefine( 'DB_NAME', 'wpdb' );\ndefine( 'DB_USER', 'u' );\ndefine( 'DB_PASSWORD', 'p' );\n")
        self.bdir = os.path.join(self.t, 'backup')
        self.args = os.path.join(self.t, 'dump_args.txt')

    def run_db(self, tools, mode='ok'):
        extra = {'mysqldump': DUMPER}
        tb = toolbox(self.t, BASE_TOOLS + tools + ['tar', 'tee'], extra)
        env = {'PATH': tb, 'SITE': self.site, 'BACKUP_DIR': self.bdir, 'PHP_BIN': PHP, 'CNF_PHP': CNFPHP, 'ARGS_FILE': self.args, 'DUMP_MODE': mode}
        return sh(['/bin/bash', SITEBK, 'db'], env=env)

    def files(self):
        out = []
        for r, _d, f in os.walk(os.path.join(self.bdir, 'db')):
            out += f
        return out

    def test_help(self):
        self.assertEqual(sh(['bash', SITEBK, '--help']).returncode, 0)
        self.assertEqual(sh(['bash', SITEBK, 'khac'], env={'BACKUP_DIR': tempfile.mkdtemp(prefix='wps-test-')}).returncode, 2)

    @unittest.skipUnless(shutil.which('zstd'), 'cần zstd')
    def test_ok_zstd_flags(self):
        r = self.run_db(['zstd', 'zstdcat', 'gzip'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('--no-tablespaces', open(self.args).read())
        self.assertIn('--single-transaction', open(self.args).read())
        fs = self.files()
        self.assertEqual(len(fs), 1)
        self.assertTrue(fs[0].endswith('.sql.zst'))
        self.assertTrue(os.path.exists(os.path.join(self.bdir, 'LAST_OK_db')))
        v = sh(['bash', VERIFY, '--min-bytes', '10', os.path.join(self.bdir, 'db', fs[0])])
        self.assertEqual(v.returncode, 0, v.stdout)

    def test_no_zstd_uses_gzip(self):
        """Ca 16/10: server không có zstd. Bản cũ ra file 0 byte. Bản mới dùng gzip và báo."""
        r = self.run_db(['gzip'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('THAY THẾ', r.stdout)
        fs = self.files()
        self.assertEqual([f for f in fs if f.endswith('.sql.gz')], fs)
        self.assertEqual(len(fs), 1)
        v = sh(['bash', VERIFY, '--min-bytes', '10', os.path.join(self.bdir, 'db', fs[0])])
        self.assertEqual(v.returncode, 0, v.stdout)

    def test_no_compressor_fails_without_files(self):
        r = self.run_db([])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.files(), [])

    def test_dump_error_leaves_no_file(self):
        r = self.run_db(['gzip'], mode='fail')
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.files(), [])  # không .part, không file rỗng
        self.assertFalse(os.path.exists(os.path.join(self.bdir, 'LAST_OK_db')))

    def test_truncated_dump_rejected(self):
        r = self.run_db(['gzip'], mode='trunc')
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.files(), [])
        self.assertFalse(os.path.exists(os.path.join(self.bdir, 'LAST_OK_db')))


@unittest.skipUnless(PHP, 'cần php')
class TestBackupCnf(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='wps-test-')
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)

    def cnf(self, host_line, password="p\\'w\"d"):
        cfg = write(os.path.join(self.t, 'wp-config.php'), "<?php\ndefine( 'DB_NAME', 'wpdb' );\ndefine( 'DB_USER', 'usr' );\ndefine( 'DB_PASSWORD', '%s' );\n%s\n" % (password, host_line))
        out = os.path.join(self.t, 'my.cnf')
        r = sh([PHP, CNFPHP, cfg, out])
        return r, (open(out).read() if os.path.exists(out) else '')

    def test_localhost_uses_socket_default(self):
        r, c = self.cnf("define( 'DB_HOST', 'localhost' );")
        self.assertEqual(r.stdout, 'wpdb')
        self.assertNotIn('host=', c)
        self.assertNotIn('port=', c)
        self.assertIn('user="usr"', c)

    def test_no_db_host_line(self):
        r, c = self.cnf('')
        self.assertEqual(r.returncode, 0)
        self.assertNotIn('host=', c)

    def test_host_port(self):
        """DB_HOST dạng host:port: bản cũ bỏ qua nên mysqldump nối nhầm vào socket localhost."""
        r, c = self.cnf("define( 'DB_HOST', 'db.internal:3307' );")
        self.assertIn('host="db.internal"', c)
        self.assertIn('port=3307', c)

    def test_localhost_with_port(self):
        r, c = self.cnf("define( 'DB_HOST', 'localhost:3307' );")
        self.assertNotIn('host=', c)
        self.assertIn('port=3307', c)

    def test_socket_path(self):
        r, c = self.cnf("define( 'DB_HOST', 'localhost:/var/run/mysqld/mysqld.sock' );")
        self.assertIn('socket="/var/run/mysqld/mysqld.sock"', c)
        self.assertNotIn('port=', c)

    def test_plain_host(self):
        r, c = self.cnf("define( 'DB_HOST', '127.0.0.1' );")
        self.assertIn('host="127.0.0.1"', c)

    def test_password_escaped_and_not_printed(self):
        r, c = self.cnf("define( 'DB_HOST', 'localhost' );")
        self.assertIn('password="p\'w\\"d"', c)  # mật khẩu PHP là p'w"d, trong file cnf dấu " được thoát
        self.assertEqual(r.stdout, 'wpdb')  # stdout chỉ có tên DB

    def test_missing_key_fails(self):
        cfg = write(os.path.join(self.t, 'wp-config2.php'), "<?php\ndefine( 'DB_NAME', 'wpdb' );\n")
        r = sh([PHP, CNFPHP, cfg, os.path.join(self.t, 'o.cnf')])
        self.assertEqual(r.returncode, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
